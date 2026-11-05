"""
AirSense — Unit Tests for Phase 4 RAG Health Advisor
File: tests/test_rag.py
Phase: 4 (Week 7)

Tests verify:
- ChromaDB knowledge base can be built and queried
- Semantic retrieval returns relevant chunks
- RAG prompt construction is correct
- Ollama connectivity check works without crashing

Run:
    pytest tests/test_rag.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_knowledge_documents_content():
    """Verify all three knowledge document strings are non-empty and contain expected keywords."""
    from rag.knowledge_documents import WHO_GUIDELINES, CPCB_GUIDELINES, AQI_HEALTH_ADVISORY

    assert len(WHO_GUIDELINES) > 500, "WHO guidelines document is suspiciously short"
    assert "PM2.5" in WHO_GUIDELINES, "Missing PM2.5 mention in WHO guidelines"
    assert "WHO" in WHO_GUIDELINES, "Missing WHO reference in WHO guidelines"

    assert len(CPCB_GUIDELINES) > 500, "CPCB guidelines document is suspiciously short"
    assert "NAAQS" in CPCB_GUIDELINES, "Missing NAAQS mention in CPCB guidelines"
    assert "AQI" in CPCB_GUIDELINES, "Missing AQI mention in CPCB guidelines"

    assert len(AQI_HEALTH_ADVISORY) > 300, "Health advisory document is suspiciously short"
    assert "asthma" in AQI_HEALTH_ADVISORY.lower(), "Missing asthma mention in health advisory"


def test_chunk_text_produces_overlapping_chunks():
    """Verify that text chunking produces correct overlapping segments."""
    from rag.build_knowledge_base import chunk_text

    test_text = "A" * 1000
    chunks = chunk_text(test_text, chunk_size=200, overlap=50)

    assert len(chunks) > 1, "Should produce multiple chunks for long text"
    assert all(len(c) <= 200 for c in chunks), "No chunk should exceed chunk_size"

    # Verify overlap: end of chunk[0] should appear at start of chunk[1]
    assert chunks[0][-50:] == chunks[1][:50], "Adjacent chunks should have 50-char overlap"


def test_rag_prompt_contains_question():
    """Verify that the built RAG prompt always includes the user's question verbatim."""
    from rag.health_advisor import build_rag_prompt

    question = "Is it safe to jog in Delhi today?"
    mock_chunks = [
        {"text": "PM2.5 annual mean WHO: 5 µg/m³", "source": "WHO_Guidelines_2021", "distance": 0.1},
    ]

    prompt = build_rag_prompt(question, mock_chunks, live_context="Delhi AQI: 180")

    assert question in prompt, "User's exact question must appear in the RAG prompt"
    assert "WHO_Guidelines_2021" in prompt, "Source name must appear in the prompt"
    assert "Delhi AQI: 180" in prompt, "Live context must be injected into the prompt"


def test_rag_prompt_without_live_context():
    """Verify RAG prompt builds correctly even with no live AQI context."""
    from rag.health_advisor import build_rag_prompt

    question = "What AQI is dangerous for children?"
    prompt = build_rag_prompt(question, [], live_context="")

    assert question in prompt, "Question must appear even with empty context"
    assert "No specific guidelines" in prompt, "Should include fallback text when no chunks retrieved"


def test_ollama_status_check_does_not_crash():
    """Verify is_ollama_running() returns a boolean without raising exceptions."""
    from rag.health_advisor import is_ollama_running

    result = is_ollama_running()
    assert isinstance(result, bool), "is_ollama_running() must return True or False"


def test_knowledge_base_status_check_does_not_crash():
    """Verify is_knowledge_base_ready() returns a boolean without raising exceptions."""
    from rag.health_advisor import is_knowledge_base_ready

    result = is_knowledge_base_ready()
    assert isinstance(result, bool), "is_knowledge_base_ready() must return True or False"


@pytest.mark.skipif(
    not Path(PROJECT_ROOT / "data" / "chroma_db").exists(),
    reason="ChromaDB not built yet — run python rag/build_knowledge_base.py first"
)
def test_semantic_retrieval_returns_relevant_chunks():
    """If ChromaDB is built, verify semantic retrieval returns relevant results."""
    from rag.health_advisor import is_knowledge_base_ready, retrieve_relevant_context

    if not is_knowledge_base_ready():
        pytest.skip("Knowledge base not populated yet")

    # Query about asthma — should retrieve chunks about respiratory health
    chunks = retrieve_relevant_context("What should an asthma patient do when AQI is 200?", top_k=3)

    assert len(chunks) > 0, "Should retrieve at least 1 chunk for a valid health question"
    assert all("text" in c and "source" in c for c in chunks), "Each chunk must have 'text' and 'source' keys"
    assert all(isinstance(c["distance"], float) for c in chunks), "Distance must be numeric"
    
    # The combined text of retrieved chunks should mention respiratory terms
    combined = " ".join(c["text"] for c in chunks).lower()
    health_terms = ["asthma", "respiratory", "pm2.5", "aqi", "health", "outdoor"]
    assert any(term in combined for term in health_terms), (
        f"Retrieved chunks should be related to health/AQI, but got: {combined[:200]}"
    )
