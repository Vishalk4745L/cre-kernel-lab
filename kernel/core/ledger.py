"""
v0.11 – Ledger (SQLite-backed, STABLE)

Responsibilities:
- Store claims in SQLite
- Resolve entities using consensus
- Persist resolutions in SQLite
- Update agent trust based on outcomes (JSON trust)
- Apply global trust decay (safe stub)
- Respect human overrides
"""

import time
from typing import List, Dict

from kernel.core.audit import log_event
from kernel.core.governance import check_override
from kernel.core.consensus import resolve_consensus
from kernel.core.trust import (
    get_trust,
    update_trust,
    decay_all_agents,
)
from kernel.core.memory_db import get_connection


# =================================================
# Claim ingestion (WRITE → SQLite)
# =================================================

def add_claim(
    agent: str,
    entity: str,
    value: str,
    confidence: float,
) -> Dict:
    """
    Store a new claim into SQLite with live trust snapshot.
    """
    trust = get_trust(agent)
    ts = time.time()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO claims (agent, entity, value, confidence, trust, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (agent, entity, value, float(confidence), trust, ts),
    )

    claim_id = cur.lastrowid
    conn.commit()
    conn.close()

    claim = {
        "id": claim_id,
        "agent": agent,
        "entity": entity,
        "value": value,
        "confidence": float(confidence),
        "trust": trust,
        "timestamp": ts,
    }

    log_event("CLAIM_ADDED", claim)
    return claim


# =================================================
# Entity resolution (READ → SQLite)
# =================================================

def resolve_entity(entity: str) -> Dict:
    """
    Resolve an entity using:
    1. Human override
    2. Consensus over SQLite claims
    3. Global trust decay (safe stub)
    4. Trust learning (confidence-weighted)
    5. Resolution persistence
    """

    now = time.time()

    # -------------------------------------------------
    # 1. Human override (highest authority)
    # -------------------------------------------------
    override = check_override(entity)
    if override:
        record = {
            "entity": entity,
            "value": override["value"],
            "status": "human_override",
            "reason": override["reason"],
            "timestamp": now,
        }
        _store_resolution(record)
        log_event("HUMAN_OVERRIDE_USED", record)
        return record

    # -------------------------------------------------
    # 2. Load claims from SQLite
    # -------------------------------------------------
    conn = get_connection()
    conn.row_factory = None
    cur = conn.cursor()

    cur.execute(
        """
        SELECT agent, value, confidence, trust
        FROM claims
        WHERE entity = ?
        """,
        (entity,),
    )

    rows = cur.fetchall()
    conn.close()

    if not rows:
        record = {
            "entity": entity,
            "value": None,
            "status": "unknown",
            "reason": "No claims available",
            "timestamp": now,
        }
        _store_resolution(record)
        return record

    claims: List[Dict] = [
        {
            "agent": row[0],
            "value": row[1],
            "confidence": float(row[2]),
            "trust": float(row[3]),
        }
        for row in rows
    ]

    # -------------------------------------------------
    # 3. Consensus
    # -------------------------------------------------
    result = resolve_consensus(claims)

    log_event(
        "CONSENSUS_RESULT",
        {
            "entity": entity,
            "result": result,
        },
    )

    # -------------------------------------------------
    # 4. Global trust decay (SAFE – stub in v0.11)
    # -------------------------------------------------
    decay_all_agents()

    # -------------------------------------------------
    # 5. Trust learning
    # -------------------------------------------------
    if result["status"] == "resolved":
        resolved_value = result["value"]

        for c in claims:
            update_trust(
                agent=c["agent"],
                correct=(c["value"] == resolved_value),
                confidence=c["confidence"],
            )

        record = {
            "entity": entity,
            "value": resolved_value,
            "status": "resolved",
            "reason": result["reason"],
            "timestamp": now,
        }
    else:
        record = {
            "entity": entity,
            "value": None,
            "status": result["status"],
            "reason": result.get("reason"),
            "timestamp": now,
        }

    # -------------------------------------------------
    # 6. Persist resolution
    # -------------------------------------------------
    _store_resolution(record)
    return record


# =================================================
# Internal helper – persist resolution
# =================================================

def _store_resolution(record: Dict) -> None:
    """
    Store a resolution record into SQLite.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO resolutions (entity, value, status, reason, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            record.get("entity"),
            record.get("value"),
            record.get("status"),
            record.get("reason"),
            record.get("timestamp"),
        ),
    )

    conn.commit()
    conn.close()