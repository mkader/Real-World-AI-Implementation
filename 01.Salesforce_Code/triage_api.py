# triage_api.py
import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from retriever import Retriever
from llm_reasoner import get_recommendation
import storage

app = FastAPI(title="TF Triage Agent (demo)")
storage.init_db()

retriever = Retriever()

# in-memory queue for demo. Replace with Redis/Cloud queue for production.
triage_queue = asyncio.Queue()

class FailurePayload(BaseModel):
    error_log: str
    metadata: dict = {}

@app.post("/submit_failure")
async def submit_failure(payload: FailurePayload):
    # queue and return fast
    await triage_queue.put(payload.error_log)
    return {"status": "queued"}

@app.get("/health")
async def health():
    return {"status": "ok"}

async def triage_worker():
    while True:
        error_log = await triage_queue.get()
        try:
            matches = retriever.find_similar(error_log, top_k=5)
            rec_text = get_recommendation(error_log, matches)
            # store in DB
            storage.store_result(error_log, rec_text)
            print("Triaged. Recommendation:\n", rec_text)
        except Exception as e:
            print("Error in triage worker:", e)
        finally:
            triage_queue.task_done()

@app.on_event("startup")
async def startup_event():
    # spawn background task
    asyncio.create_task(triage_worker())
