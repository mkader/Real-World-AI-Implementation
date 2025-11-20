# worker.py
import os
import time
from retriever import Retriever
from llm_reasoner import get_recommendation
import storage

# initialize storage (ensure table exists)
storage.init_db()

# load retriever (reads INDEX_PATH / META_PATH env or defaults)
INDEX_PATH = os.getenv("INDEX_PATH", "/app/index_data/tf_index.faiss")
META_PATH = os.getenv("META_PATH", "/app/index_data/tf_meta.json")

# Initialize retriever (it reads paths inside retriever.py by default)
retriever = Retriever()

def process_failure(error_log: str):
    """
    This function will be invoked by RQ worker.
    It's kept synchronous since RQ runs sync workers.
    """
    start = time.time()
    try:
        matches = retriever.find_similar(error_log, top_k=5)
        rec_text = get_recommendation(error_log, matches)
        storage.store_result(error_log, rec_text)
        elapsed = time.time() - start
        print(f"[worker] Processed failure in {elapsed:.2f}s. Recommendation saved.")
        return {"status": "ok", "elapsed_s": elapsed}
    except Exception as e:
        print("[worker] Error processing failure:", e)
        raise
