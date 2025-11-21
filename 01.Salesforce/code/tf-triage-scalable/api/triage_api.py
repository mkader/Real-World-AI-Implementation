# api/triage_api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from api.db import init_db
from api.retriever import Retriever
from api.worker import process_unindexed
from api.storage import store_result
from redis import Redis
from rq import Queue
from api.db import engine

app = FastAPI(title="TF Triage HNSW")

init_db()
# RQ queue
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("triage", connection=redis_conn)

# instantiate retriever lazily to avoid start-up failure if index missing
retriever = None
def get_retriever():
    global retriever
    if retriever is None:
        retriever = Retriever()
    return retriever

class SubmitPayload(BaseModel):
    error_log: str

@app.post("/submit_failure")
def submit_failure(payload: SubmitPayload):
    # insert into DB (unindexed)
    with engine.begin() as conn:
        res = conn.execute(text("INSERT INTO failures (error_log, indexed) VALUES (:log, false) RETURNING id"),
                           {"log": payload.error_log})
        f_id = res.scalar_one()
    # enqueue indexing worker
    queue.enqueue("api.worker.process_unindexed", job_timeout=600)
    return {"status": "queued", "failure_id": int(f_id)}

@app.get("/search")
def search(q: str, k: int = 5):
    r = get_retriever()
    results = r.search(q, top_k=k)
    return {"results": results}

@app.post("/rebuild_index")
def rebuild_index():
    # run blocking rebuild (not recommended in prod) or enqueue
    queue.enqueue("api.build_index.build", job_timeout=36000)
    return {"status": "rebuild enqueued"}

@app.post("/feedback")
def feedback(payload: dict):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO feedback (failure_id, helpful, note) VALUES (:fid, :helpful, :note)"),
                     {"fid": payload.get("failure_id"), "helpful": bool(payload.get("helpful")), "note": payload.get("note")})
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}

from api.retriever import retrieve_similar_failures
from api.llm_reasoner import explain_failure

@app.post("/query")
def query_failure(error_log: str):
    matches = retrieve_similar_failures(error_log)
    reasoning = explain_failure(error_log, matches)
    return {
        "matches": matches,
        "model_reasoning": reasoning
    }