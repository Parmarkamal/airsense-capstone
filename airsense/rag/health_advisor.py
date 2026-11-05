"""
AirSense — RAG Health Advisor Engine
File: rag/health_advisor.py
Phase: 4 + 6

Implements a Retrieval-Augmented Generation (RAG) pipeline with Phase 6 safety:
  1. GUARD: Domain classifier — refuse out-of-scope queries without calling Ollama
  2. RETRIEVE: Semantic search in ChromaDB for relevant WHO/CPCB guidelines
  3. THRESHOLD: If retrieval confidence is low, use verified static CPCB fallback
  4. AUGMENT + GENERATE: Grounded prompt → Ollama
  5. DISCLAIMER: Append mandatory medical disclaimer to every advisory answer

Architecture:
  User Question → Domain Guard → ChromaDB → Confidence Gate
  → Ollama / Static Fallback → Disclaimer → Response
"""

from __future__ import annotations

import os
import re
import sys
import types
from pathlib import Path

# Windows runtime guard: prevent chromadb unused ONNX import crash
os.environ["ANONYMIZED_TELEMETRY"] = "False"
if "onnxruntime" not in sys.modules:
    try:
        import onnxruntime  # noqa: F401
    except Exception:
        sys.modules["onnxruntime"] = types.ModuleType("onnxruntime")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import chromadb
import requests
from chromadb.utils import embedding_functions

from rag.knowledge_documents import get_static_fallback_for_aqi

# ── Constants ─────────────────────────────────────────────────────────────────
CHROMA_DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")
COLLECTION_NAME = "airsense_health_knowledge"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:3b"   # Preferred: fast, 2GB, accurate enough
FALLBACK_MODEL = "qwen2.5-coder:3b"   # Already downloaded on your machine
TOP_K_RESULTS = 4               # Number of relevant document chunks to retrieve
RAG_DISTANCE_THRESHOLD = 0.75   # Phase 6: refuse LLM extrapolation when worse than 0.75

DOMAIN_REFUSAL_MESSAGE = (
    "I am the AirSense AI Health Advisor, specialized in urban air quality and "
    "respiratory health impacts. I can only answer questions related to air "
    "pollution, AQI readings, WHO/CPCB standards, and outdoor activity "
    "precautions. Please ask an air quality or health-related question."
)

MEDICAL_DISCLAIMER = (
    "⚠️ **Medical Disclaimer**: AirSense provides general health advisories based "
    "on official WHO (2021) and CPCB NAAQS guidelines and live air quality data. "
    "This is not medical diagnosis or prescription. Consult a physician for acute "
    "respiratory or cardiovascular symptoms."
)

# Strong out-of-domain signals (stocks, code, entertainment, recipes, etc.)
_OUT_OF_DOMAIN_RE = re.compile(
    r"\b("
    r"python|javascript|typescript|quicksort|bubble\s*sort|programming|algorithm|"
    r"leetcode|code\s*review|react|django|sql\s*query|"
    r"stock|stocks|share\s*price|crypto|bitcoin|trading|nasdaq|forex|"
    r"movie|netflix|song|playlist|recipe|cook(?:ing)?|restaurant\s*review|"
    r"homework\s*essay|write\s*a\s*poem"
    r")\b",
    re.IGNORECASE,
)

# Prescription / diagnosis requests outside air-quality advice
_PRESCRIPTION_RE = re.compile(
    r"\b("
    r"prescribe|prescription|dosage|antibiotic|steroid\s*dose|"
    r"diagnose\s+me|what\s+medicine|which\s+tablet|buy\s+inhaler\s+brand"
    r")\b",
    re.IGNORECASE,
)

_AIR_HEALTH_KEYWORDS = (
    "aqi", "air quality", "air pollution", "pollution", "pollutant",
    "pm2.5", "pm2_5", "pm25", "pm10", "no2", "ozone", "so2", "co",
    "who", "cpcb", "naaqs", "grap",
    "asthma", "copd", "respiratory", "lung", "breathe", "breathing",
    "mask", "n95", "ffp2", "purifier", "filter", "ventilation", "windows",
    "outdoor", "outside", "out side", "go out", "go outside", "step out",
    "jog", "jogging", "run", "running", "exercise", "workout", "walk", "walking",
    "play", "playing", "cycling", "commute", "commuter", "travel", "traveling",
    "toddler", "child", "children", "infant", "baby", "kids",
    "elderly", "senior", "old age", "pregnant", "heart", "cardiovascular",
    "smog", "haze", "dust", "smoke", "particulate",
    "delhi", "dilli", "ncr", "new delhi",
    "mumbai", "bombay",
    "ahmedabad", "ahmedabd", "amdavad", "ahmdabad",
    "pune", "poona",
    "bengaluru", "bangalore", "blr",
    "gandhinagar", "gnr",
    "safe to", "is it safe", "is it ok", "is it healthy",
    "best time to", "good time to", "safe time to",
    "cough", "throat", "headache", "allergy", "allergies",
    "fresh air", "clean air", "dirty air",
)


def is_air_quality_or_health_query(query: str) -> bool:
    """
    Phase 6 domain classifier.
    Returns False for stocks/programming/movies/prescriptions outside air-health scope.
    """
    if not query or not str(query).strip():
        return False

    text = str(query).strip()
    lowered = text.lower()
    has_air_health = any(keyword in lowered for keyword in _AIR_HEALTH_KEYWORDS)

    if _OUT_OF_DOMAIN_RE.search(text) and not has_air_health:
        return False

    if _PRESCRIPTION_RE.search(text) and not has_air_health:
        return False

    if has_air_health:
        return True

    # Ambiguous queries without AQ/health signal → refuse (safer for viva defense)
    return False


def append_medical_disclaimer(answer: str) -> str:
    """Ensure every advisory response ends with the mandatory medical disclaimer."""
    if not answer:
        return MEDICAL_DISCLAIMER
    if "Medical Disclaimer" in answer:
        return answer
    return f"{answer.rstrip()}\n\n{MEDICAL_DISCLAIMER}"


def _retrieval_is_confident(chunks: list[dict]) -> bool:
    """True only when chunks exist and best (lowest) distance <= threshold."""
    if not chunks:
        return False
    best = min(float(c.get("distance", 1.0)) for c in chunks)
    return best <= RAG_DISTANCE_THRESHOLD


def _parse_aqi_from_live_context(live_context: str) -> tuple[str, float | None]:
    """Best-effort extract first city name and AQI from dashboard live context string."""
    if not live_context:
        return "", None
    match = re.search(
        r"-\s*([^:]+):\s*AQI\s*=\s*([0-9]+(?:\.[0-9]+)?)",
        live_context,
    )
    if not match:
        return "", None
    return match.group(1).strip(), float(match.group(2))


def _get_chroma_collection():
    """Connect to persistent ChromaDB and return the knowledge collection."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )
        return collection
    except Exception:
        return None


def retrieve_relevant_context(question: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """
    Perform semantic similarity search in ChromaDB.
    
    Returns a list of the top-k most relevant document chunks with:
    - 'text': the actual content chunk
    - 'source': which official document it came from
    - 'distance': cosine similarity distance (lower = more relevant)
    """
    collection = _get_chroma_collection()
    if collection is None or collection.count() == 0:
        return []
    
    try:
        results = collection.query(
            query_texts=[question],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text": doc,
                "source": meta.get("source", "Unknown"),
                "category": meta.get("category", "general"),
                "distance": round(dist, 4),
            })
        return chunks
    except Exception as e:
        print(f"[RAG ERROR] ChromaDB retrieval failed: {e}")
        return []


def _list_available_models() -> list[str]:
    """Query Ollama to get list of downloaded models."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        pass
    return []


def _select_model() -> str:
    """Select the best available Ollama model."""
    available = _list_available_models()
    if not available:
        return DEFAULT_MODEL
    
    # Priority order
    for preferred in [DEFAULT_MODEL, FALLBACK_MODEL, "llama3.2:1b", "llama3:8b"]:
        if preferred in available:
            return preferred
    
    # Return whatever is available
    return available[0]


def _query_ollama(prompt: str, model: str) -> str:
    """
    Send a prompt to the local Ollama LLM and stream the response.
    Uses the Ollama REST API directly (no LangChain overhead).
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,    # Low temperature for factual health advice
            "top_p": 0.85,
            "num_predict": 350,    # Max tokens in response for snappy generation
        },
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"[Error] Ollama returned HTTP {response.status_code}: {response.text[:200]}"
    except requests.exceptions.ConnectionError:
        return "__OLLAMA_OFFLINE__"
    except requests.exceptions.Timeout:
        return "__OLLAMA_TIMEOUT__"


def build_rag_prompt(
    question: str,
    retrieved_chunks: list[dict],
    live_context: str = "",
) -> str:
    """
    Construct the full RAG prompt combining:
    1. Retrieved official health guideline excerpts (WHO/CPCB)
    2. Live AQI context from your sensors
    3. The user's specific question
    """
    # Format retrieved documents
    context_sections = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_sections.append(
            f"[Source {i}: {chunk['source']}]\n{chunk['text']}"
        )
    
    retrieved_context = "\n\n---\n\n".join(context_sections) if context_sections else (
        "No specific guidelines were retrieved for this question. "
        "Please provide a general response based on common air quality health knowledge."
    )
    
    live_aqi_section = ""
    if live_context:
        live_aqi_section = f"""
## Current Live AQI Data (from AirSense Platform):
{live_context}

"""
    
    prompt = f"""You are AirSense, an expert AI Health Advisor for air quality safety in Indian cities. 
You provide evidence-based, practical health advice grounded in official WHO and CPCB guidelines.

## Official Guidelines Retrieved (for this specific question):
{retrieved_context}
{live_aqi_section}
## Instructions:
- Answer the user's question using the official guidelines above as your primary source.
- If live AQI data is provided, incorporate it to give city-specific, real-time advice.
- Be empathetic but medically accurate. Never downplay serious health risks.
- Give practical, actionable recommendations.
- Mention which official source (WHO/CPCB) supports your advice.
- Keep the response concise (under 250 words) but complete.
- Do not hallucinate statistics — only use figures from the provided guidelines.

## User Question:
{question}

## Your Response:"""
    
    return prompt


def ask_health_advisor(
    question: str,
    live_aqi_context: str = "",
    model: str | None = None,
    current_aqi: float | None = None,
    city: str = "",
) -> dict:
    """
    Main entry point for the RAG health advisor (Phase 4 + Phase 6 guardrails).

    Returns dict with keys:
        answer, sources, model_used, chunks_retrieved,
        refused (bool), low_confidence (bool), llm_called (bool)
    """
    empty = {
        "answer": "Please type a question about air quality or health.",
        "sources": [],
        "model_used": "N/A",
        "chunks_retrieved": 0,
        "refused": False,
        "low_confidence": False,
        "llm_called": False,
    }
    if not question or not question.strip():
        return empty

    # Phase 6.1 — Domain guard (never call Ollama on out-of-scope queries)
    if not is_air_quality_or_health_query(question):
        return {
            "answer": DOMAIN_REFUSAL_MESSAGE,
            "sources": [],
            "model_used": "domain_guard",
            "chunks_retrieved": 0,
            "refused": True,
            "low_confidence": False,
            "llm_called": False,
        }

    # Resolve city / AQI for static fallback
    parsed_city, parsed_aqi = _parse_aqi_from_live_context(live_aqi_context)
    city_name = city or parsed_city
    aqi_value = current_aqi if current_aqi is not None else parsed_aqi

    # Step 1: RETRIEVE
    retrieved_chunks = retrieve_relevant_context(question, top_k=TOP_K_RESULTS)
    sources = list({chunk["source"] for chunk in retrieved_chunks})

    # Phase 6.3 — Confidence thresholding (no LLM hallucination on weak retrieval)
    if not _retrieval_is_confident(retrieved_chunks):
        fallback = get_static_fallback_for_aqi(
            aqi_value=aqi_value,
            city=city_name,
        )
        return {
            "answer": append_medical_disclaimer(fallback),
            "sources": sources or ["CPCB_NAAQS_Static_Fallback", "WHO_2021_Static_Fallback"],
            "model_used": "static_cpcb_fallback",
            "chunks_retrieved": len(retrieved_chunks),
            "refused": False,
            "low_confidence": True,
            "llm_called": False,
        }

    # Step 2–3: AUGMENT + GENERATE
    prompt = build_rag_prompt(question, retrieved_chunks, live_aqi_context)
    selected_model = model or _select_model()
    answer = _query_ollama(prompt, selected_model)
    llm_called = answer not in ("__OLLAMA_OFFLINE__", "__OLLAMA_TIMEOUT__")

    if answer == "__OLLAMA_OFFLINE__":
        guideline_bullets = "\n\n".join([
            f"📌 **Excerpt from {c['source']}:**\n> {c['text'].strip()}"
            for c in retrieved_chunks[:2]
        ])
        answer = (
            "ℹ️ *Note: Ollama LLM server is currently offline. Direct official "
            "guidelines retrieved from ChromaDB:*\n\n"
            f"{guideline_bullets}\n\n"
            "To enable natural AI synthesis, run `ollama serve`."
        )
        selected_model = "ChromaDB Direct Semantic Match"
        llm_called = False
    elif answer == "__OLLAMA_TIMEOUT__":
        guideline_bullets = "\n\n".join([
            f"📌 **Excerpt from {c['source']}:**\n> {c['text'].strip()}"
            for c in retrieved_chunks[:2]
        ])
        answer = (
            "⏳ *Note: LLM request timed out during model loading. Direct official "
            "guidelines retrieved from ChromaDB:*\n\n"
            f"{guideline_bullets}"
        )
        selected_model = "ChromaDB Direct Semantic Match (Fallback)"
        llm_called = False

    # Phase 6.2 — Mandatory disclaimer on every advisory answer
    return {
        "answer": append_medical_disclaimer(answer),
        "sources": sources,
        "model_used": selected_model,
        "chunks_retrieved": len(retrieved_chunks),
        "refused": False,
        "low_confidence": False,
        "llm_called": llm_called,
    }


def is_ollama_running() -> bool:
    """Check if Ollama service is accessible."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def is_knowledge_base_ready() -> bool:
    """Check if ChromaDB has been populated."""
    collection = _get_chroma_collection()
    return collection is not None and collection.count() > 0
