from pathlib import Path
import sys


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.embeddings.provider import get_embedding
from app.vectorstore.faiss_store import FAISSStore


def main():
    store = FAISSStore()

    store.add(
        chunks=[
            "Catastrophic forgetting occurs when neural networks overwrite old knowledge",
            "Experience replay stores past samples to prevent forgetting",
            "EWC penalises changes to important weights",
            "Progressive networks add new columns for each task",
            "Gradient episodic memory constrains updates using past gradients",
        ],
        metadata=[
            {"source": "paper1.pdf", "page": 1},
            {"source": "paper2.pdf", "page": 3},
            {"source": "paper1.pdf", "page": 2},
            {"source": "paper3.pdf", "page": 1},
            {"source": "paper2.pdf", "page": 5},
        ],
    )

    results = store.search(
        query_vector=get_embedding("how to prevent forgetting"),
        top_k=2,
    )
    for result in results:
        print(result["text"], "->", result["score"])
        print("Metadata:", result["metadata"])


if __name__ == "__main__":
    main()
