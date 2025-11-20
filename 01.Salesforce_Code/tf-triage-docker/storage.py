# storage.py
from sqlalchemy import create_engine, text
import os
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://triage:triagepass@postgres:5432/triagedb")

# echo=False in prod; set True for debugging
engine = create_engine(DATABASE_URL, echo=False, future=True)

def init_db():
    # create table if not exists
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS triage_results (
                id SERIAL PRIMARY KEY,
                error_log TEXT NOT NULL,
                recommendation TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))

def store_result(error_log: str, recommendation: str):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO triage_results (error_log, recommendation) VALUES (:log, :rec)"),
            {"log": error_log, "rec": recommendation}
        )
