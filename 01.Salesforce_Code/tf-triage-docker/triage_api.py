# triage_api.py
import os
from fastapi import FastAPI
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import storage

app = FastAPI(title="TF Triage Agent (dockerized)")

# init db
storage.init_db()

# redis / queue
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
queue = Queue("triage", connection=redis_conn)

class FailurePayload(BaseModel):
    error_log: str
    metadata: dict = {}

@app.post("/submit_failure")
async def submit_failure(payload: FailurePayload):
    # push job to RQ. The worker will pick up `process_failure` from worker.py
    job = queue.enqueue("worker.process_failure", payload.error_log, job_timeout=1200)
    return {"status": "queued", "job_id": job.get_id()}

@app.get("/health")
async def health():
    return {"status": "ok"}
