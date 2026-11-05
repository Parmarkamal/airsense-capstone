"""
AirSense — RAG Knowledge Base Builder
File: rag/build_knowledge_base.py
Phase: 4 (Week 7)

Ingests WHO/CPCB health guidelines and AQI advisory documents into a persistent
ChromaDB vector store for semantic retrieval during health Q&A.

Run once to build:
    python rag/build_knowledge_base.py

Subsequent runs will re-use the existing ChromaDB collection (or rebuild if forced).
"""

from __future__ import annotations

import sys
from pathlib import Path

import os
import types

# Windows runtime guard: prevent chromadb unused ONNX import crash
os.environ["ANONYMIZED_TELEMETRY"] = "False"
if "onnxruntime" not in sys.modules:
    try:
        import onnxruntime  # noqa: F401
    except Exception:
        sys.modules["onnxruntime"] = types.ModuleType("onnxruntime")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import chromadb
from chromadb.utils import embedding_functions

# ── Import Knowledge Documents ─────────────────────────────────────────────────
from rag.knowledge_documents import (
    WHO_GUIDELINES,
    CPCB_GUIDELINES,
    AQI_HEALTH_ADVISORY,
)

# ── Constants ─────────────────────────────────────────────────────────────────
CHROMA_DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")
COLLECTION_NAME = "airsense_health_knowledge"
CHUNK_SIZE = 600          # characters per text chunk
CHUNK_OVERLAP = 100       # overlap between consecutive chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split a long document into overlapping text chunks for vector embedding.
    
    Why overlap? If a question's answer spans across two adjacent chunks,
    the overlapping region ensures the relevant context is not cut off.
    """
    chunks = []
    start = 0
    text = text.strip()
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_knowledge_base(force_rebuild: bool = False) -> int:
    """
    Build (or verify) the ChromaDB vector store from knowledge documents.
    
    Parameters
    ----------
    force_rebuild : bool
        If True, wipe existing collection and rebuild from scratch.
    
    Returns
    -------
    int
        Total number of document chunks stored in the vector database.
    """
    print("=" * 60)
    print("AirSense RAG Knowledge Base Builder")
    print(f"ChromaDB path: {CHROMA_DB_PATH}")
    print("=" * 60)

    # ── Create ChromaDB client with persistent storage ─────────────────────────
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # Use sentence-transformers for local, offline embeddings (no API key needed)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Check if collection already exists
    existing_collections = [c.name for c in client.list_collections()]
    
    if COLLECTION_NAME in existing_collections and not force_rebuild:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn
        )
        count = collection.count()
        print(f"[INFO] Existing collection found with {count} chunks. Skipping rebuild.")
        print("[INFO] Pass force_rebuild=True to force a fresh rebuild.")
        return count
    
    # Delete existing collection if rebuilding
    if COLLECTION_NAME in existing_collections:
        client.delete_collection(COLLECTION_NAME)
        print("[INFO] Deleted existing collection for fresh rebuild.")
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )
    print("[INFO] Created new ChromaDB collection.")
    
    # ── Define source documents ────────────────────────────────────────────────
    documents = [
        {
            "text": WHO_GUIDELINES,
            "source": "WHO_Air_Quality_Guidelines_2021",
            "category": "international_standards",
        },
        {
            "text": CPCB_GUIDELINES,
            "source": "CPCB_NAAQS_India_2009",
            "category": "india_regulatory_standards",
        },
        {
            "text": AQI_HEALTH_ADVISORY,
            "source": "AirSense_Health_Advisory_QA",
            "category": "practical_health_advice",
        },
    ]
    
    # ── Chunk and index each document ──────────────────────────────────────────
    all_chunks = []
    all_ids = []
    all_metadatas = []
    
    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['source']}__chunk_{i:03d}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append({
                "source": doc["source"],
                "category": doc["category"],
                "chunk_index": i,
            })
        print(f"[INFO] {doc['source']}: {len(chunks)} chunks created.")
    
    # ── Upsert into ChromaDB in batches ───────────────────────────────────────
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        collection.upsert(
            documents=all_chunks[i:i + batch_size],
            ids=all_ids[i:i + batch_size],
            metadatas=all_metadatas[i:i + batch_size],
        )
    
    total = collection.count()
    print(f"\n[SUCCESS] Knowledge base built with {total} total chunks across {len(documents)} sources.")
    print("[INFO] Vector store is ready for semantic retrieval.")
    return total


if __name__ == "__main__":
    force = "--rebuild" in sys.argv
    total_chunks = build_knowledge_base(force_rebuild=force)
    print(f"\nTotal chunks in ChromaDB: {total_chunks}")
    print("You can now run the dashboard and use the AI Health Advisor tab.")
