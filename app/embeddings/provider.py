"""Embedding provider with an optional sentence-transformers backend."""

from sentence_transformers import SentenceTransformer
from app.core.config import settings

model = SentenceTransformer(settings.embedding_model)


def get_embedding(text: str) -> list[float]:
    """Return an embedding vector for a given text string."""
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")

    return model.encode(text).tolist()
