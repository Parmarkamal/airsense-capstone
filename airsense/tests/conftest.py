"""
AirSense — Pytest Configuration & Test Fixtures
File: tests/conftest.py

Handles Windows DLL runtime initialization guards for cross-framework test runs.
"""

from __future__ import annotations

import sys
import types

# On Windows, lightgbm and onnxruntime C-libraries can encounter an OpenMP/VC runtime
# DLL collision if loaded together in the same process.
# Since AirSense uses sentence-transformers (PyTorch) for semantic embeddings rather than ONNX,
# we provide a lightweight module stub to prevent chromadb's unused DefaultEmbeddingFunction
# from triggering an onnxruntime DLL crash on Windows.
if "onnxruntime" not in sys.modules:
    try:
        import onnxruntime  # noqa: F401
    except Exception:
        sys.modules["onnxruntime"] = types.ModuleType("onnxruntime")
