# api/build_index.py
import os
import math
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from api.db import engine, init_db
from sqlalchemy import text
from pathlib import Path

INDEX_DIR = Path(os.getenv("INDEX_DIR", "/app/index_data"))
INDEX_PATH = INDEX_DIR / "tf_hnsw.index"
META_PATH = INDEX_DIR / "faiss_map.json"
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))
HNSW_M = int(os.getenv("HNSW_M", "32"))
HNSW_EFCONSTRUCTION = int(os.getenv("HNSW_EFCONSTRUCTION", "200"))

def fetch_total_count():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM failures"))
        return res.scalar_one()

def fetch_batch(offset, limit):
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, error_log FROM failures ORDER BY id OFFSET :off LIMIT :lim"),
                            {"off": offset, "lim": limit}).all()
        return rows

def build():
    init_db()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(EMBED_MODEL)
    total = fetch_total_count()
    if total == 0:
        print("No failures to index.")
        return

    # Temporary collect vectors dims to know d
    # We'll first embed the first small batch to get dim
    first_batch = fetch_batch(0, min(BATCH_SIZE, total))
    texts = [r[1] for r in first_batch]
    emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    d = emb.shape[1]

    # Create HNSW index
    index = faiss.IndexHNSWFlat(d, HNSW_M)
    index.hnsw.efConstruction = HNSW_EFCONSTRUCTION

    # we normalize later for cosine-like behavior using inner product
    faiss.normalize_L2(emb)
    index.add(emb.astype("float32"))

    # map faiss_id -> failure_id
    faiss_id = index.ntotal - 1
    mappings = []
    for r in first_batch:
        mappings.append((index.ntotal - len(first_batch) + mappings.__len__() + 1, r[0]))  # corrected below

    # The above mapping logic is simpler to do by tracking appended ids:
    current_faiss_id = 0
    mappings = []
    # Add first batch properly and map
    index = faiss.IndexHNSWFlat(d, HNSW_M)
    index.hnsw.efConstruction = HNSW_EFCONSTRUCTION
    # add in batches
    offset = 0
    while offset < total:
        batch = fetch_batch(offset, min(BATCH_SIZE, total - offset))
        texts = [r[1] for r in batch]
        emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        faiss.normalize_L2(emb)
        index.add(emb.astype("float32"))
        # map ids
        for i, r in enumerate(batch):
            mappings.append((current_faiss_id, r[0]))
            current_faiss_id += 1
        offset += len(batch)
        print(f"Indexed up to {offset}/{total}")

    # Save index
    faiss.write_index(index, str(INDEX_PATH))
    # Persist mapping in Postgres (replace)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE faiss_map"))
        for faiss_id, failure_id in mappings:
            conn.execute(text("INSERT INTO faiss_map (faiss_id, failure_id) VALUES (:f, :id)"),
                         {"f": int(faiss_id), "id": int(failure_id)})

    print("Index and mapping saved to", INDEX_PATH)

if __name__ == "__main__":
    build()
