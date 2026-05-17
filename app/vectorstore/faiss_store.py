import json
import os
import numpy as np

from ..embeddings.provider import get_embedding

try:
    import faiss
except ModuleNotFoundError:
    faiss = None

class FAISSStore:
    def __init__(self):
        self.index = None
        self.metadata = []
        self.backend = None
        self.embeddings = None

    def add(self, chunks: list[str], metadata: list[dict]):
        if len(chunks) != len(metadata):
            raise ValueError("chunks and metadata must have the same length")
        if not chunks:
            return

        embeddings = np.array([get_embedding(chunk) for chunk in chunks], dtype=np.float32)

        if self.index is None:
            dimension = embeddings.shape[1]
            if faiss is not None:
                self.index = faiss.IndexFlatL2(dimension)
                self.backend = "faiss"
            else:
                self.index = "numpy"
                self.backend = "numpy"
                self.embeddings = np.empty((0, dimension), dtype=np.float32)

        if self.backend == "faiss":
            self.index.add(embeddings)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        for chunk, meta in zip(chunks, metadata):
            self.metadata.append({"text": chunk, **meta})

    def search(self, query_vector: list[float], top_k: int = 5):
        if self.index is None:
            return []

        query = np.array([query_vector], dtype=np.float32)

        if self.backend == "faiss":
            distances, indices = self.index.search(query, top_k)
            ranked_pairs = zip(indices[0], distances[0])
        else:
            distances = np.sum((self.embeddings - query) ** 2, axis=1)
            top_indices = np.argsort(distances)[:top_k]
            ranked_pairs = ((idx, distances[idx]) for idx in top_indices)

        results = []
        for idx, dist in ranked_pairs:
            if idx == -1:
                continue
            meta = self.metadata[idx]
            results.append({"text": meta["text"], "metadata": meta, "score": float(dist)})
        return results

    def save(self, folder: str = "data"):
        os.makedirs(folder, exist_ok=True)
        if self.backend == "faiss":
            faiss.write_index(self.index, f"{folder}/faiss.index")
        elif self.embeddings is not None:
            np.save(f"{folder}/embeddings.npy", self.embeddings)

        with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f)

    def load(self, folder: str = "data"):
        faiss_index_path = f"{folder}/faiss.index"
        numpy_index_path = f"{folder}/embeddings.npy"

        if faiss is not None and os.path.exists(faiss_index_path):
            self.index = faiss.read_index(faiss_index_path)
            self.backend = "faiss"
            self.embeddings = None
        elif os.path.exists(numpy_index_path):
            self.embeddings = np.load(numpy_index_path)
            self.index = "numpy"
            self.backend = "numpy"
        else:
            raise FileNotFoundError(f"No saved vector index found in {folder}")

        with open(f"{folder}/metadata.json", "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
