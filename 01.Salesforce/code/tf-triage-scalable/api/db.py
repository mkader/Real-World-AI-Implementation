# api/db.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://triage:triagepass@postgres:5432/triagedb")
engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db():
    with engine.begin() as conn:
        # tables: failures, faiss_map, triage_results, feedback
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS failures (
            id SERIAL PRIMARY KEY,
            error_log TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            indexed BOOLEAN DEFAULT FALSE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS faiss_map (
            faiss_id BIGINT PRIMARY KEY,
            failure_id INTEGER NOT NULL
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS triage_results (
            id SERIAL PRIMARY KEY,
            failure_id INTEGER,
            recommendation TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            failure_id INTEGER,
            helpful BOOLEAN,
            note TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """))
