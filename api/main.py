"""
CRE Kernel API – v0.15 (STABLE)

Responsibilities:
- Accept signed claims from agents
- Resolve entities using ledger + consensus
- Expose trust scores & trust event history
- Apply background time-based trust decay (SAFE)
- Allow cryptographically-authorized human overrides
- Provide graph-ready absolute trust timelines
"""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
# --- Kernel Adapter System ---
from kernel.core.kernel import Kernel
from kernel.adapters.mock_adapter import MockAgentAdapter
from kernel.core.message import KernelMessage
import json
import asyncio

from cryptography.hazmat.primitives.asymmetric import ed25519

# =================================================
# Kernel Singleton (Adapter-ready)
# =================================================

kernel_instance = Kernel()

# Register mock adapter (safe test agent)
kernel_instance.register_adapter(MockAgentAdapter())

# ====================================================
# Core Kernel Imports
# ====================================================

from kernel.core.ledger import add_claim, resolve_entity
from kernel.core.governance import set_override, clear_override
from kernel.core.identity import require_identity, get_identity_public_key
from kernel.core.signature import require_signature
from kernel.core.trust import (
    get_trust,
    get_all_trust,
    decay_all_agents,
)
from kernel.core.memory_db import get_connection

# ====================================================
# FastAPI App
# ====================================================

app = FastAPI(
    title="CRE Kernel API",
    version="0.15",
)

# ====================================================
# Constants
# ====================================================

INTENT_READ = "READ"
INTENT_WRITE = "WRITE"

IDENTITY_AGENT = "AGENT"
IDENTITY_HUMAN_ADMIN = "HUMAN_ADMIN"

# ====================================================
# Async Lock (prevents SQLite lock overlap)
# ====================================================

trust_decay_lock = asyncio.Lock()

# ====================================================
# Data Models
# ====================================================

class Claim(BaseModel):
    agent: str
    entity: str
    value: str
    confidence: float

# ====================================================
# Helpers
# ====================================================

def require_intent(expected: str, intent: Optional[str]) -> None:
    if intent != expected:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid intent. Expected '{expected}'",
        )

# ====================================================
# Background Trust Decay (SAFE)
# ====================================================

async def trust_decay_loop() -> None:
    while True:
        await asyncio.sleep(300)  # 5 minutes
        async with trust_decay_lock:
            try:
                decay_all_agents()
                print("🕒 Trust decay applied")
            except Exception as e:
                print("⚠️ Trust decay error:", e)

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(trust_decay_loop())

# ====================================================
# Health Check
# ====================================================

@app.get("/")
def root_status(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"status": "CRE kernel alive"}

# ====================================================
# Claim API
# ====================================================

@app.post("/claim")
def create_claim(
    claim: Claim,
    x_intent: Optional[str] = Header(None),
    x_identity_id: Optional[str] = Header(None),
    x_identity_type: Optional[str] = Header(None),
    x_signature: Optional[str] = Header(None),
):
    require_intent(INTENT_WRITE, x_intent)

    identity = require_identity(x_identity_id, IDENTITY_AGENT)

    payload = json.dumps(
        {
            "agent": claim.agent,
            "entity": claim.entity,
            "value": claim.value,
            "confidence": claim.confidence,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    public_key: ed25519.Ed25519PublicKey = get_identity_public_key(identity)
    require_signature(x_signature, payload, public_key)

    c = add_claim(
        agent=claim.agent,
        entity=claim.entity,
        value=claim.value,
        confidence=claim.confidence,
    )

    return {"ok": True, "claim_id": c["id"], "status": "stored"}

# ====================================================
# Resolution API
# ====================================================

@app.get("/resolve/{entity}")
def resolve_entity_api(entity: str, x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return resolve_entity(entity)

# ====================================================
# Governance APIs (HUMAN_ADMIN)
# ====================================================

@app.post("/override/set/{entity}")
def human_override_set(
    entity: str,
    value: str,
    reason: str = "human override",
    x_intent: Optional[str] = Header(None),
    x_identity_id: Optional[str] = Header(None),
    x_identity_type: Optional[str] = Header(None),
    x_signature: Optional[str] = Header(None),
):
    require_intent(INTENT_WRITE, x_intent)
    identity = require_identity(x_identity_id, IDENTITY_HUMAN_ADMIN)

    payload = json.dumps(
        {"entity": entity, "value": value, "reason": reason},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    public_key = get_identity_public_key(identity)
    require_signature(x_signature, payload, public_key)

    set_override(entity, value, reason)
    return {"ok": True, "entity": entity, "value": value}

@app.post("/override/clear/{entity}")
def human_override_clear(
    entity: str,
    x_intent: Optional[str] = Header(None),
    x_identity_id: Optional[str] = Header(None),
    x_identity_type: Optional[str] = Header(None),
    x_signature: Optional[str] = Header(None),
):
    require_intent(INTENT_WRITE, x_intent)
    identity = require_identity(x_identity_id, IDENTITY_HUMAN_ADMIN)

    payload = json.dumps(
        {"entity": entity},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    public_key = get_identity_public_key(identity)
    require_signature(x_signature, payload, public_key)

    clear_override(entity)
    return {"ok": True, "entity": entity}

# ====================================================
# Trust APIs
# ====================================================

@app.get("/trust")
def read_all_trust(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return get_all_trust()

@app.get("/trust/{agent}")
def read_agent_trust(agent: str, x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"agent": agent, "trust": get_trust(agent)}

# ====================================================
# Trust Events (Explainability)
# ====================================================

@app.get("/trust/events")
def read_trust_events(
    limit: int = 50,
    x_intent: Optional[str] = Header(None),
):
    require_intent(INTENT_READ, x_intent)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT agent, change, reason, timestamp
        FROM trust_events
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "agent": r["agent"],
            "change": r["change"],
            "reason": r["reason"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]

# ====================================================
# Trust Timeline (ABSOLUTE GRAPH)
# ====================================================

@app.get("/trust/timeline")
def trust_timeline(
    agent: str,
    x_intent: Optional[str] = Header(None),
):
    require_intent(INTENT_READ, x_intent)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT change, timestamp
        FROM trust_events
        WHERE agent = ?
        ORDER BY timestamp ASC
        """,
        (agent,),
    )
    rows = cur.fetchall()
    conn.close()

    # reconstruct absolute trust
    current = get_trust(agent)
    for r in reversed(rows):
        current -= r["change"]

    timeline: List[Dict] = []
    for r in rows:
        current += r["change"]
        timeline.append(
            {
                "timestamp": r["timestamp"],
                "trust": round(current, 4),
            }
        )

    return {"agent": agent, "timeline": timeline}


# =================================================
# Kernel Adapter Test Endpoint
# =================================================

@app.post("/kernel/route")
def kernel_route_test(payload: dict):
    """
    Test Kernel → Adapter routing.
    This simulates:
    - Gemini
    - MCP
    - A2A
    - SDK agents (future)

    Payload example:
    {
        "adapter_id": "mock-agent",
        "content": "Hello from API"
    }
    """

    adapter_id = payload.get("adapter_id")
    content = payload.get("content")

    msg = KernelMessage(
        source="api",
        type="thought",
        content=content,
        confidence=0.9,
    )

    result = kernel_instance.route(adapter_id, msg.to_dict())
    return result