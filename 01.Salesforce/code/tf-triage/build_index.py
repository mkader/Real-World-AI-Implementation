# build_index.py
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path

INDEX_PATH = Path("tf_index.faiss")
META_PATH = Path("tf_meta.json")
SAMPLE_PATH = Path("sample_data/historical_failures.json")

def build():
    model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast
    with open(SAMPLE_PATH, "r") as f:
        failures = json.load(f)

    logs = [f["error_log"] for f in failures]
    embeddings = model.encode(logs, convert_to_numpy=True, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine-like if we normalize
    # normalize for IP => cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(np.asarray(embeddings, dtype=np.float32))

    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "w") as f:
        json.dump(failures, f, indent=2)

    print(f"Built FAISS index with {len(logs)} entries: {INDEX_PATH}, metadata: {META_PATH}")

if __name__ == "__main__":
    build()
