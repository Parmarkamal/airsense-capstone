"""
AirSense — RAG Health Advisor Engine
File: rag/health_advisor.py
Phase: 4 (Week 7)

Implements a Retrieval-Augmented Generation (RAG) pipeline:
  1. RETRIEVE: Semantic search in ChromaDB for relevant WHO/CPCB guidelines
  2. AUGMENT:  Build a context-rich prompt combining retrieved docs + live AQI data
  3. GENERATE: Ollama LLM generates a grounded, evidence-based health answer

Architecture:
  User Question → ChromaDB Semantic Search → Top-K Relevant Chunks
  + Live AQI Context → Ollama LLM (llama3.2:3b) → Health Advisory Answer
"""

from __future__ import annotations

import os
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

# ── Constants ─────────────────────────────────────────────────────────────────
CHROMA_DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")
COLLECTION_NAME = "airsense_health_knowledge"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:3b"   # Preferred: fast, 2GB, accurate enough
FALLBACK_MODEL = "qwen2.5-coder:3b"   # Already downloaded on your machine
TOP_K_RESULTS = 4               # Number of relevant document chunks to retrieve


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
) -> dict:
    """
    Main entry point for the RAG health advisor.
    
    Parameters
    ----------
    question : str
        The health-related question from the user.
    live_aqi_context : str
        Current AQI readings as a formatted string (injected from dashboard).
    model : str | None
        Ollama model to use. Auto-selected if None.
    
    Returns
    -------
    dict with keys:
        - answer: str — The LLM-generated health advisory
        - sources: list[str] — Documents used as context
        - model_used: str — Which Ollama model was used
        - chunks_retrieved: int — Number of context chunks retrieved
    """
    if not question or not question.strip():
        return {
            "answer": "Please type a question about air quality or health.",
            "sources": [],
            "model_used": "N/A",
            "chunks_retrieved": 0,
        }
    
    # Step 1: RETRIEVE — Semantic search in ChromaDB
    retrieved_chunks = retrieve_relevant_context(question, top_k=TOP_K_RESULTS)
    
    # Step 2: AUGMENT — Build the grounded prompt
    prompt = build_rag_prompt(question, retrieved_chunks, live_aqi_context)
    
    # Step 3: GENERATE — Query Ollama LLM
    selected_model = model or _select_model()
    answer = _query_ollama(prompt, selected_model)
    
    # Extract source names
    sources = list({chunk["source"] for chunk in retrieved_chunks})
    
    # Handle Offline or Timeout Gracefully
    if answer == "__OLLAMA_OFFLINE__":
        if retrieved_chunks:
            guideline_bullets = "\n\n".join([
                f"📌 **Excerpt from {c['source']}:**\n> {c['text'].strip()}"
                for c in retrieved_chunks[:2]
            ])
            answer = (
                f"ℹ️ *Note: Ollama LLM server is currently offline. Direct official guidelines retrieved from ChromaDB:*\n\n"
                f"{guideline_bullets}\n\n"
                f"⚠️ **Medical Disclaimer:** Always consult a healthcare specialist for medical conditions. "
                f"To enable natural AI synthesis, run `ollama serve`."
            )
            selected_model = "ChromaDB Direct Semantic Match"
        else:
            answer = "**Ollama is not running.** Please start it with `ollama serve` and refresh."
    elif answer == "__OLLAMA_TIMEOUT__":
        if retrieved_chunks:
            guideline_bullets = "\n\n".join([
                f"📌 **Excerpt from {c['source']}:**\n> {c['text'].strip()}"
                for c in retrieved_chunks[:2]
            ])
            answer = (
                f"⏳ *Note: LLM request timed out during model loading. Direct official guidelines retrieved from ChromaDB:*\n\n"
                f"{guideline_bullets}\n\n"
                f"⚠️ **Medical Disclaimer:** Always consult a healthcare specialist for medical conditions."
            )
            selected_model = "ChromaDB Direct Semantic Match (Fallback)"
        else:
            answer = "**Request timed out.** Please try again in 30 seconds."
            
    return {
        "answer": answer,
        "sources": sources,
        "model_used": selected_model,
        "chunks_retrieved": len(retrieved_chunks),
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
