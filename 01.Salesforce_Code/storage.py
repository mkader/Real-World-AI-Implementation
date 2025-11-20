# storage.py
import sqlite3
from pathlib import Path

DB_PATH = Path("triage_results.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS triage_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_log TEXT,
            recommendation TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_result(error_log, recommendation):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO triage_results (error_log, recommendation) VALUES (?,?)",
              (error_log, recommendation))
    conn.commit()
    conn.close()
