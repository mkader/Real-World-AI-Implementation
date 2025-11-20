# build_index.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os

INDEX_PATH = Path(os.getenv("INDEX_PATH", "/app/index_data/tf_index.faiss"))
META_PATH = Path(os.getenv("META_PATH", "/app/index_data/tf_meta.json"))
SAMPLE_PATH = Path("sample_data/historical_failures.json")

def build():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    with open(SAMPLE_PATH, "r") as f:
        failures = json.load(f)

    logs = [f["error_log"] for f in failures]
    embeddings = model.encode(logs, convert_to_numpy=True, show_progress_bar=True)

    dim = embeddings.shape[1]
    # Use inner product on normalized vectors for cosine similarity
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dim)
    index.add(np.asarray(embeddings, dtype=np.float32))

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "w") as f:
        json.dump(failures, f, indent=2)

    print(f"Built FAISS index at {INDEX_PATH} (entries: {len(logs)})")

if __name__ == "__main__":
    build()
