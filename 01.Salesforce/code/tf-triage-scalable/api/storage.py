# api/storage.py
from api.db import engine
from sqlalchemy import text

def store_result(failure_id, recommendation):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO triage_results (failure_id, recommendation) VALUES (:fid, :rec)"),
                     {"fid": int(failure_id), "rec": recommendation})
