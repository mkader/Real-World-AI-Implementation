# api/retriever.py
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from api.db import engine
from sqlalchemy import text

INDEX_DIR = Path(os.getenv("INDEX_DIR", "/app/index_data"))
INDEX_PATH = INDEX_DIR / "tf_hnsw.index"
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
HNSW_EFSEARCH = int(os.getenv("HNSW_EFSEARCH", "64"))

class Retriever:
    def __init__(self):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")
        self.index = faiss.read_index(str(INDEX_PATH))
        # set efSearch
        if hasattr(self.index, "hnsw"):
            self.index.hnsw.efSearch = HNSW_EFSEARCH
        self.model = SentenceTransformer(EMBED_MODEL)

    def search(self, text, top_k=5):
        q = self.model.encode([text], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(q)
        k = min(top_k, int(self.index.ntotal))
        if k == 0:
            return []
        D, I = self.index.search(q, k)
        results = []
        # Fetch metadata for each faiss id
        with engine.connect() as conn:
            for dist, idx in zip(D[0], I[0]):
                if idx < 0:
                    continue
                # map faiss_id -> failure_id
                row = conn.execute(text("SELECT failure_id FROM faiss_map WHERE faiss_id = :f"), {"f": int(idx)}).first()
                if not row:
                    continue
                failure_id = row[0]
                meta = conn.execute(text("SELECT id, error_log FROM failures WHERE id = :id"), {"id": int(failure_id)}).first()
                results.append({
                    "score": float(dist),
                    "faiss_id": int(idx),
                    "failure_id": int(failure_id),
                    "error_log": meta[1]
                })
        return results
