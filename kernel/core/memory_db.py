"""
v0.15 – SQLite Memory Layer (STABLE, SINGLE SOURCE OF TRUTH)

Responsibilities:
- Provide SQLite connection
- Initialize all core tables
- Persist trust, claims, resolutions
- Support Error Review Agent system
"""

import sqlite3
from pathlib import Path
from typing import Dict, Optional

# =================================================
# Database Path
# =================================================

DB_PATH = Path("data/cre_memory.db")


# =================================================
# Connection Helper
# =================================================

def get_connection() -> sqlite3.Connection:
    """
    Return SQLite connection with Row access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =================================================
# DB Initialization (CALLED ON IMPORT)
# =================================================

def init_db() -> None:
    """
    Create all required tables if not exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    # ------------------------------
    # Trust table
    # ------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trust (
        agent TEXT PRIMARY KEY,
        trust REAL NOT NULL,
        last_updated REAL
    )
    """)

    # ------------------------------
    # Trust events (explainability)
    # ------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trust_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        change REAL NOT NULL,
        reason TEXT NOT NULL,
        confidence REAL,
        timestamp REAL NOT NULL
    )
    """)

    # ------------------------------
    # Claims
    # ------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT NOT NULL,
        entity TEXT NOT NULL,
        value TEXT NOT NULL,
        confidence REAL NOT NULL,
        trust REAL NOT NULL,
        timestamp REAL NOT NULL
    )
    """)

    # ------------------------------
    # Resolutions
    # ------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resolutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity TEXT NOT NULL,
        value TEXT,
        status TEXT NOT NULL,
        reason TEXT,
        timestamp REAL NOT NULL
    )
    """)

    # ------------------------------
    # Error reviews (Agent → Agent)
    # ------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS error_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        reviewer_agent TEXT NOT NULL,
        target_agent   TEXT NOT NULL,

        entity TEXT NOT NULL,

        observed_value TEXT,
        expected_value TEXT,

        error_type TEXT NOT NULL,
        confidence REAL NOT NULL,

        evidence TEXT,

        timestamp REAL NOT NULL
    )
    """)

    # ------------------------------
    # Error resolutions (consensus)
    # ------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS error_resolutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        entity TEXT NOT NULL,
        target_agent TEXT NOT NULL,

        status TEXT NOT NULL,
        error_type TEXT,

        reason TEXT,

        reviewer_count INTEGER,
        avg_confidence REAL,

        timestamp REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# 🔥 IMPORTANT: initialize DB on import
init_db()


# =================================================
# Trust Helpers (USED BY trust.py)
# =================================================

def db_get_trust(agent: str) -> Optional[float]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT trust FROM trust WHERE agent = ?",
        (agent,),
    )
    row = cur.fetchone()
    conn.close()
    return row["trust"] if row else None


def db_set_trust(agent: str, trust: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO trust (agent, trust, last_updated)
        VALUES (?, ?, strftime('%s','now'))
        ON CONFLICT(agent)
        DO UPDATE SET
            trust = excluded.trust,
            last_updated = excluded.last_updated
        """,
        (agent, trust),
    )
    conn.commit()
    conn.close()


def db_get_all_trust() -> Dict[str, float]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT agent, trust FROM trust")
    rows = cur.fetchall()
    conn.close()
    return {r["agent"]: r["trust"] for r in rows}