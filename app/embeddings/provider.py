"""Embedding provider with an optional sentence-transformers backend."""

from __future__ import annotations

import hashlib
import re

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError:
    SentenceTransformer = None


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FALLBACK_DIMENSION = 384
_model = None
_model_load_attempted = False


def _get_model():
    global _model, _model_load_attempted
    if _model_load_attempted:
        return _model

    _model_load_attempted = True
    if SentenceTransformer is None:
        return None

    try:
        _model = SentenceTransformer(MODEL_NAME)
    except Exception:
        _model = None
    return _model


def _fallback_embedding(text: str, dimension: int = FALLBACK_DIMENSION) -> list[float]:
    # Use deterministic hashed token features when sentence-transformers is unavailable.
    vector = np.zeros(dimension, dtype=np.float32)
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        tokens = [text.strip().lower()]

    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=16).digest()
        index = int.from_bytes(digest[:8], "little") % dimension
        sign = 1.0 if digest[8] % 2 == 0 else -1.0
        vector[index] += sign

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector.tolist()


def get_embedding(text: str) -> list[float]:
    """Return an embedding vector for a given text string."""
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    model = _get_model()
    if model is not None:
        return model.encode(text).tolist()
    return _fallback_embedding(text)
