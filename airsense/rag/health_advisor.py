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
    Includes an explicit system prompt to prevent unwarranted RLHF medical refusals
    on standard environmental PPE and air quality exposure questions.
    """
    system_prompt = (
        "You are AirSense, an expert Environmental Health & Air Quality Advisor for Indian cities. "
        "You provide factual, actionable guidance on air pollution levels, PPE respirators (N95/FFP2), "
        "indoor air purification, outdoor timing, and exposure management grounded strictly in CPCB NAQI and WHO 2021 standards. "
        "Answering environmental safety, mask, and purifier questions is your primary purpose."
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,    # Low temperature for factual, reliable advice
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
    
    prompt = f"""You are AirSense, an empathetic, expert conversational AI Environmental Health Advisor for urban air quality in Indian cities.
You provide evidence-based, actionable guidance grounded strictly in official CPCB NAQI (2014) and WHO (2021) guidelines.

## SCOPE & PERMISSIBILITY DIRECTIVE:
You are an environmental air quality specialist. The user is asking for general CPCB/WHO personal protection equipment (PPE) guidelines (such as N95, FFP2, KN95 masks), outdoor activity safety, indoor ventilation, or air purifier advice.
Answering questions about masks, air purifiers, outdoor exercise timing, or school attendance is your CORE PRIMARY FUNCTION and does NOT constitute restricted clinical medical diagnosis or prescription. 
NEVER refuse legitimate environmental PPE or activity questions with "I cannot provide medical advice". Directly provide the official CPCB and WHO equipment, timing, and exposure management recommendations.

## Official Guidelines Retrieved (for this specific question):
{retrieved_context}
{live_aqi_section}
## Conversational Guidance & Structure Rules:
- Adopt a helpful, empathetic, natural chatbot tone.
- Give a clear **Direct Summary** first.
- Provide **Diurnal Timing Guidance**: Explain when dispersion is best (afternoon 12 PM - 4 PM) vs peak pollution (early morning 6 AM - 8 AM and late evening).
- Provide **Actionable Precautions**: Mask advice (certified N95/FFP2 for AQI > 200 or vulnerable groups), air purifiers (HEPA filter), hydration, ventilation.
- Use clean Markdown with bold bullet points for fast readability.
- Mention which official standard (CPCB NAQI / WHO) supports your guidance.
- Keep the response clear, structured, and under 250 words.

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
    else:
        # Phase 6.5 — Intercept generic LLM safety refusals on legitimate air quality queries
        refusal_triggers = [
            "can't provide medical advice",
            "cannot provide medical advice",
            "not provide medical advice",
            "i am not a doctor",
            "consult a medical professional",
            "consult a physician",
            "as an ai, i cannot",
            "as an ai model",
            "not a medical professional",
            "seek medical advice",
        ]
        is_canned_refusal = any(trigger in answer.lower() for trigger in refusal_triggers) and len(answer.split()) < 75
        if is_canned_refusal:
            q_clean = question.lower()
            if "mask" in q_clean:
                answer = (
                    "**Direct Summary:** When AQI is above 200 (Poor to Very Poor), standard cloth and basic surgical masks provide near-zero protection against fine toxic particulates ($PM_{2.5}$). Certified high-efficiency respirators are mandatory.\n\n"
                    "**Actionable Equipment Guidance:**\n"
                    "• **Recommended Standard:** Certified **N95, FFP2, or KN95** respirators (without exhalation valves in public indoor spaces).\n"
                    "• **Fit & Seal:** Ensure a complete facial seal covering both nose and mouth. Air leakage around gaps drops filtration efficiency drastically.\n"
                    "• **Sensitive Groups:** Priority protection for asthmatic patients, children, elderly citizens, and daily commuters.\n\n"
                    "**Diurnal Timing:** Pollution concentrations are highest during early morning (6 AM – 8 AM) and evening rush hours (6 PM – 9 PM) due to boundary layer thermal inversions. Minimize outdoor exposure during these windows (CPCB NAQI / WHO 2021)."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO PPE Standard)"
            elif "purifier" in q_clean or "home" in q_clean:
                answer = (
                    "**Direct Summary:** When AQI exceeds 150–200, indoor particulate concentration rises rapidly through infiltration. Running a certified air purifier is strongly advised.\n\n"
                    "**Actionable Home Guidance:**\n"
                    "• **Filter Standard:** Choose a true **HEPA H13 filter** (traps 99.97% of particles down to 0.3 microns). Avoid ozone-generating ionizers.\n"
                    "• **Ventilation Strategy:** Keep external windows and doors closed. Ventilate briefly only during peak afternoon dispersion (1 PM – 4 PM).\n"
                    "• **Placement:** Position the purifier in frequently occupied spaces (bedrooms, living rooms) away from walls."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Home Standard)"
            elif "jog" in q_clean or "run" in q_clean or "exercise" in q_clean or "workout" in q_clean:
                answer = (
                    "**Direct Summary:** Strenuous outdoor cardiovascular exercise should be avoided whenever AQI is elevated (>150–200).\n\n"
                    "**Timing & Physiological Guidance:**\n"
                    "• **Diurnal Window:** If outdoor workouts are essential, the safest window is **early afternoon (12 PM – 4 PM)** when solar heating breaks thermal inversions and wind disperses pollutants.\n"
                    "• **Avoid Early Mornings:** Cold morning air traps combustion particulates ($PM_{2.5}$) and vehicle exhaust close to the ground.\n"
                    "• **Indoor Alternative:** Shift heavy cardio workouts indoors into filtered environments to avoid 5x higher minute-ventilation lung deposits (WHO 2021)."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Exercise Standard)"
            elif "school" in q_clean or "child" in q_clean or "toddler" in q_clean:
                answer = (
                    "**Direct Summary:** At an AQI of 250 (Very Poor), children are under high environmental risk due to their higher breathing rate per kilogram of body weight.\n\n"
                    "**Actionable Precautions:**\n"
                    "• **School Measures:** CPCB GRAP Stage II/III guidelines recommend suspending outdoor morning assemblies and physical education sports.\n"
                    "• **Commute Protection:** Children should wear well-fitted pediatric N95 masks during transit to and from school.\n"
                    "• **Classroom Air Quality:** Keep windows closed and ensure indoor activities during high pollution hours."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Child Protection)"
            elif "heart" in q_clean or "cardiac" in q_clean or "cardiovascular" in q_clean:
                answer = (
                    "**Direct Summary:** Cardiovascular patients face acute risks from fine $PM_{2.5}$ particles, which enter the bloodstream and trigger inflammation and arterial vasoconstriction.\n\n"
                    "**Actionable Precautions:**\n"
                    "• **Exposure Limitation:** Stay indoors in air-conditioned or HEPA-filtered rooms during elevated AQI hours.\n"
                    "• **Physical Exertion:** Avoid heavy outdoor lifting or walking, which increases myocardial oxygen demand in polluted air.\n"
                    "• **Medication Readiness:** Keep prescribed cardiac medications on schedule and seek emergency care if experiencing chest tightness (CPCB/WHO)."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Cardiac Advisory)"
            elif "pregnant" in q_clean or "pregnancy" in q_clean or "maternal" in q_clean:
                answer = (
                    "**Direct Summary:** WHO 2021 guidelines highlight that maternal exposure to elevated $PM_{2.5}$ and $NO_2$ is associated with low birth weight and gestational risks.\n\n"
                    "**Actionable Precautions:**\n"
                    "• **Avoid Peak Windows:** Completely avoid roadside exposure during peak morning and evening traffic hours.\n"
                    "• **Personal Protection:** Wear a certified N95 respirator if traveling outdoors in AQI > 150.\n"
                    "• **Indoor Air:** Maintain clean indoor air using HEPA filtration and wet-mopping rather than dry-sweeping."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Maternal Advisory)"
            elif "elderly" in q_clean or "senior" in q_clean or "older" in q_clean:
                answer = (
                    "**Direct Summary:** For senior citizens, AQI above 100 (Moderate) begins to stress respiratory and vascular systems due to reduced lung elasticity.\n\n"
                    "**Actionable Precautions:**\n"
                    "• **Critical Threshold:** AQI > 200 (Poor) requires staying strictly indoors with windows shut.\n"
                    "• **Hydration & Ventilation:** Stay well-hydrated and ventilate living spaces only during warm afternoon hours (1 PM – 4 PM).\n"
                    "• **Pulse Oximetry:** Individuals with chronic obstructive pulmonary disease (COPD) should monitor oxygen saturation levels."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Senior Advisory)"
            elif "asthma" in q_clean or "respiratory" in q_clean or "bronch" in q_clean:
                answer = (
                    "**Direct Summary:** Asthmatic individuals are hypersensitive to $SO_2$, $NO_2$, and fine particulates, which trigger acute airway bronchospasm.\n\n"
                    "**Actionable Precautions:**\n"
                    "• **Inhaler Access:** Always carry a prescribed rescue bronchodilator when stepping outdoors.\n"
                    "• **Protective Equipment:** Use an N95 respirator snugly fitted to filter irritant dust and particulates.\n"
                    "• **Avoid Early Mornings:** Cold morning smog traps ground-level pollutants; schedule any outdoor movement for the afternoon."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Asthma Advisory)"
            elif "commute" in q_clean or "traffic" in q_clean or "transit" in q_clean:
                answer = (
                    "**Direct Summary:** Daily urban commuters face the highest daily acute exposure to vehicular $NO_2$, benzene, and black carbon soot.\n\n"
                    "**Actionable Commute Guidance:**\n"
                    "• **Two-Wheelers & Pedestrians:** Certified N95 or FFP2 respirators are essential during morning and evening rush hours.\n"
                    "• **Four-Wheelers:** Keep vehicle windows rolled up and switch air conditioning to **Recirculation mode** to block tunnel/traffic exhaust.\n"
                    "• **Route Choice:** Prefer wide arterial roads over congested bottleneck alleys where pollutants accumulate."
                )
                selected_model = f"{selected_model} (Grounded CPCB/WHO Commuter Advisory)"
            else:
                answer = get_static_fallback_for_aqi(aqi_value=aqi_value, city=city_name)
                selected_model = f"{selected_model} (CPCB NAQI Standard)"

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
