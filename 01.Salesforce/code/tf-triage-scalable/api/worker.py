# api/worker.py
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from api.db import engine, init_db
from sqlalchemy import text
from pathlib import Path

INDEX_DIR = Path(os.getenv("INDEX_DIR", "/app/index_data"))
INDEX_PATH = INDEX_DIR / "tf_hnsw.index"
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))

def ensure_index(d=None):
    if not INDEX_DIR.exists():
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_PATH.exists():
        # create empty index with d if provided (otherwise will create on first add)
        if d is None:
            return None
        index = faiss.IndexHNSWFlat(d, int(os.getenv("HNSW_M", "32")))
        index.hnsw.efConstruction = int(os.getenv("HNSW_EFCONSTRUCTION", "200"))
        faiss.write_index(index, str(INDEX_PATH))
        return index
    return faiss.read_index(str(INDEX_PATH))

def process_unindexed(batch_size=BATCH_SIZE):
    # find unindexed failures
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, error_log FROM failures WHERE indexed = false ORDER BY id LIMIT :lim"), {"lim": batch_size}).all()
        if not rows:
            return 0
        texts = [r[1] for r in rows]
        ids = [r[0] for r in rows]

    model = SentenceTransformer(EMBED_MODEL)
    emb = model.encode(texts, convert_to_numpy=True)
    faiss.normalize_L2(emb)
    emb = emb.astype("float32")

    # ensure index exists, if not create with d
    index = ensure_index(d=emb.shape[1])
    if index is None:
        index = faiss.IndexHNSWFlat(emb.shape[1], int(os.getenv("HNSW_M", "32")))
        index.hnsw.efConstruction = int(os.getenv("HNSW_EFCONSTRUCTION", "200"))

    # we must read again to append to existing index then save
    index = faiss.read_index(str(INDEX_PATH)) if INDEX_PATH.exists() else index
    start_id = int(index.ntotal)
    index.add(emb)
    faiss.write_index(index, str(INDEX_PATH))

    # persist mapping and mark indexed
    with engine.begin() as conn:
        for i, failure_id in enumerate(ids):
            conn.execute(text("INSERT INTO faiss_map (faiss_id, failure_id) VALUES (:f, :id)"),
                         {"f": start_id + i, "id": int(failure_id)})
            conn.execute(text("UPDATE failures SET indexed = true WHERE id = :id"), {"id": int(failure_id)})

    print(f"Appended {len(ids)} items to FAISS index (starting faiss_id {start_id})")
    return len(ids)
