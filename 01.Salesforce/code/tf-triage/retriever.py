# retriever.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path

INDEX_PATH = Path("tf_index.faiss")
META_PATH = Path("tf_meta.json")

class Retriever:
    def __init__(self, faiss_path=INDEX_PATH, meta_path=META_PATH, embed_model="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embed_model)
        self.index = None
        self.meta = []
        self.load(faiss_path, meta_path)

    def load(self, faiss_path, meta_path):
        self.index = faiss.read_index(str(faiss_path))
        with open(meta_path, "r") as f:
            self.meta = json.load(f)
        print("Retriever loaded: index entries =", len(self.meta))

    def find_similar(self, error_log, top_k=5):
        vec = self.model.encode([error_log], convert_to_numpy=True)
        faiss.normalize_L2(vec)
        distances, indices = self.index.search(vec.astype(np.float32), top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.meta):
                continue
            results.append({
                "score": float(dist),
                "entry": self.meta[idx]
            })
        return results
