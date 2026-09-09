import json
import os
import numpy as np
import faiss

from ..embeddings.provider import get_embedding

class FAISSStore:
    def __init__(self):
        self.index = None
        self.metadata = []


    def add(self, chunks: list[str], metadata: list[dict]):
        if len(chunks) != len(metadata):
            raise ValueError("chunks and metadata must have the same length")
        if not chunks:
            return

        embeddings = np.array([get_embedding(chunk) for chunk in chunks], dtype=np.float32)

        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings)

        for chunk, meta in zip(chunks, metadata):
            self.metadata.append({"text": chunk, **meta})


    def search(self, query: str, top_k: int = 5):
        if self.index is None:
            return []

        query_vector = np.array([get_embedding(query)], dtype=np.float32)
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:  # FAISS returns -1 when it can't fill top_k
                continue
            meta = self.metadata[idx]
            results.append({"text": meta["text"], "metadata": meta, "score": float(dist)})
        return results


    def save(self, folder: str = "data"):
        os.makedirs(folder, exist_ok=True)
        faiss.write_index(self.index, f"{folder}/faiss.index")  # save the vectors
        with open(f"{folder}/metadata.json", "w") as f:
            json.dump(self.metadata, f)  # save the text alongside


    def load(self, folder: str = "data"):
        self.index = faiss.read_index(f"{folder}/faiss.index")  # load vectors back
        with open(f"{folder}/metadata.json", "r") as f:
            self.metadata = json.load(f)  # load text back