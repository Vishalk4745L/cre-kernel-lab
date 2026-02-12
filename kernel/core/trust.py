"""SQLite-backed trust system with trust event logging."""

import time
from typing import Dict, Optional

from kernel.core.memory_db import db_get_all_trust, db_get_trust, db_set_trust, get_connection

# =================================================
# Trust Configuration
# =================================================

DEFAULT_TRUST = 0.1
TRUST_FLOOR = 0.05
TRUST_CEILING = 1.0

BASE_REWARD = 0.05
BASE_PENALTY = 0.05

# =================================================
# Internal helpers
# =================================================

def _log_trust_event(agent: str, change: float, reason: str, confidence: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO trust_events (agent, change, reason, confidence, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (agent, float(change), reason, float(confidence), time.time()),
    )
    conn.commit()
    conn.close()


# =================================================
# Public API (READ)
# =================================================

def get_trust(agent: str) -> float:
    trust = db_get_trust(agent)
    return float(trust if trust is not None else DEFAULT_TRUST)


def get_all_trust() -> Dict[str, float]:
    return db_get_all_trust()


# =================================================
# Learning Rules (WRITE)
# =================================================

def reward_agent(agent: str, confidence: Optional[float] = None, reason: str = "reward") -> None:
    old = get_trust(agent)
    conf = confidence if confidence is not None else 1.0
    conf = max(0.0, min(conf, 1.0))

    delta = BASE_REWARD * conf
    new = min(old + delta, TRUST_CEILING)
    rounded_new = round(new, 4)
    db_set_trust(agent, rounded_new)
    _log_trust_event(agent=agent, change=round(rounded_new - old, 4), reason=reason, confidence=conf)


def penalize_agent(agent: str, confidence: Optional[float] = None, reason: str = "penalty") -> None:
    old = get_trust(agent)
    conf = confidence if confidence is not None else 1.0
    conf = max(0.0, min(conf, 1.0))

    delta = BASE_PENALTY * conf
    new = max(old - delta, TRUST_FLOOR)
    rounded_new = round(new, 4)
    db_set_trust(agent, rounded_new)
    _log_trust_event(agent=agent, change=round(rounded_new - old, 4), reason=reason, confidence=conf)


# =================================================
# Compatibility Layer (DO NOT REMOVE)
# =================================================

def update_trust(
    agent: str,
    correct: bool,
    confidence: Optional[float] = None,
) -> None:
    """
    Backward-compatible API for ledger (v0.9 / v0.10).
    """
    if correct:
        reward_agent(agent, confidence, reason="consensus_correct")
    else:
        penalize_agent(agent, confidence, reason="consensus_incorrect")


# =================================================
# Future hook (safe stub)
# =================================================

def decay_all_agents() -> None:
    """
    v0.11 stub.
    Time-based decay will be implemented in v0.12+.
    """
    return
