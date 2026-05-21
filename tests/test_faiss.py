"""
tests/test_faiss.py

Pytest-friendly FAISS store checks with printed search output.

Run with visible output:
    pytest tests/test_faiss.py -s -v
"""

from pathlib import Path
import hashlib
import re
import sys
from tempfile import TemporaryDirectory
import types

import numpy as np
import pytest


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class _TestSentenceTransformer:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def encode(self, text: str):
        vector = np.zeros(384, dtype=np.float32)
        tokens = re.findall(r"\w+", text.lower()) or [text.strip().lower()]

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=16).digest()
            index = int.from_bytes(digest[:8], "little") % len(vector)
            sign = 1.0 if digest[8] % 2 == 0 else -1.0
            vector[index] += sign

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector


sys.modules["sentence_transformers"] = types.SimpleNamespace(
    SentenceTransformer=_TestSentenceTransformer
)

from app.embeddings.provider import get_embedding
from app.vectorstore.faiss_store import FAISSStore
from app.tools.ingestion import store_chunks_and_vectors


SAMPLE_CHUNKS = [
    "Data quality refers to how accurate, complete, consistent, and reliable data is for its intended use.",
    "Common data quality dimensions include accuracy, completeness, consistency, validity, and timeliness.",
    "Poor data quality can lead to incorrect analytics, weak decisions, and operational inefficiencies.",
    "Data profiling and validation rules are common techniques for monitoring data quality issues.",
]

SAMPLE_METADATA = [
    {"source": "notes.txt", "page": 1},
    {"source": "notes.txt", "page": 2},
    {"source": "notes.txt", "page": 3},
    {"source": "notes.txt", "page": 4},
]

QUERY = "What is data quality?"
PDF_PATH = Path("dq.tex.pdf")


def _print_results(results: list[dict]) -> None:
    print("\nTop search results:")
    for index, result in enumerate(results, start=1):
        print(f"\n{index}. score={result['score']:.4f}")
        print(f"   text: {result['text'][:160]}")
        print(f"   metadata: {result['metadata']}")


def _build_store() -> FAISSStore:
    store = FAISSStore()
    store.add(chunks=SAMPLE_CHUNKS, metadata=SAMPLE_METADATA)
    return store


def test_store_search_returns_results():
    store = _build_store()
    results = store.search(
        query_vector=get_embedding(QUERY),
        top_k=2,
    )

    _print_results(results)

    assert len(results) == 2
    assert all(result["text"] for result in results)
    assert all("metadata" in result for result in results)
    assert all("source" in result["metadata"] for result in results)
    assert any("data quality" in result["text"].lower() for result in results)


def test_store_save_and_load_round_trip():
    with TemporaryDirectory() as tmp_dir:
        store = _build_store()
        store.save(folder=tmp_dir)

        reloaded_store = FAISSStore()
        reloaded_store.load(folder=tmp_dir)

        results = reloaded_store.search(
            query_vector=get_embedding(QUERY),
            top_k=2,
        )

        _print_results(results)

        assert len(results) == 2
        assert reloaded_store.metadata
        assert results[0]["metadata"]["source"] == "notes.txt"


def test_pdf_ingestion_save_and_load_round_trip():
    pytest.importorskip("fitz", reason="PyMuPDF is required for PDF ingestion tests")

    with TemporaryDirectory() as tmp_dir:
        store = store_chunks_and_vectors(str(PDF_PATH))
        store.save(folder=tmp_dir)

        reloaded_store = FAISSStore()
        reloaded_store.load(folder=tmp_dir)

        results = reloaded_store.search(
            query_vector=get_embedding(QUERY),
            top_k=2,
        )

        _print_results(results)

        assert len(results) == 2
        assert reloaded_store.metadata
        assert all(result["metadata"]["source"] == PDF_PATH.name for result in results)


if __name__ == "__main__":
    test_store_search_returns_results()
    test_store_save_and_load_round_trip()
    test_pdf_ingestion_save_and_load_round_trip()
