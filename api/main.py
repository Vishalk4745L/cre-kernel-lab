"""
CRE Kernel API – v1.0 (STABLE)
Frontend Compatible Version
Responsibilities:
Accept signed claims from agents
Resolve entities using ledger + consensus
Expose trust scores & trust event history
Apply background time-based trust decay
Allow -authorized human overrides
Provide graph-ready absolute trust
timelines
"""

# ============================================================
# Imports
# ============================================================

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import json
import asyncio
import time

from cryptography.hazmat.primitives.asymmetric import ed25519

# --- Kernel System ---
from kernel.core.kernel import Kernel
from kernel.adapters.mock_adapter import MockAgentAdapter
from kernel.core.message import KernelMessage

from kernel.core.ledger import add_claim, resolve_entity
from kernel.core.governance import set_override, clear_override
from kernel.core.identity import require_identity, get_identity_public_key
from kernel.core.signature import require_signature
from kernel.core.trust import get_trust, get_all_trust, decay_all_agents
from kernel.core.memory_db import get_connection

# ============================================================
# Kernel Singleton
# ============================================================

kernel_instance = Kernel()
kernel_instance.register_adapter(MockAgentAdapter())

# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(title="CRE Kernel API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Constants
# ============================================================

INTENT_READ = "READ"
INTENT_WRITE = "WRITE"

IDENTITY_AGENT = "AGENT"
IDENTITY_HUMAN_ADMIN = "HUMAN_ADMIN"

trust_decay_lock = asyncio.Lock()

# ============================================================
# Models
# ============================================================

class Claim(BaseModel):
    agent: str
    entity: str
    value: str
    confidence: float

# ============================================================
# Helpers
# ============================================================

def require_intent(expected: str, intent: Optional[str]) -> None:
    if intent != expected:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid intent. Expected '{expected}'"
        )

# ============================================================
# Background Trust Decay
# ============================================================

async def trust_decay_loop():
    while True:
        await asyncio.sleep(300)
        async with trust_decay_lock:
            try:
                decay_all_agents()
                print("Trust decay applied")
            except Exception as e:
                print("Trust decay error:", e)

@app.on_event("startup")
async def startup():
    asyncio.create_task(trust_decay_loop())

# ============================================================
# Health
# ============================================================

@app.get("/")
def root_status(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"status": "CRE kernel alive"}

@app.get("/kernel/status")
def kernel_status(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)

    adapters = kernel_instance.registry.list()

    return {
        "status": "CRE kernel alive",
        "version": app.version,
        "adapters_registered": len(adapters),
        "adapters": adapters,
        "timestamp": time.time(),
    }

# ============================================================
# Claims
# ============================================================

@app.post("/claim")
def create_claim(
    claim: Claim,
    x_intent: Optional[str] = Header(None),
    x_identity_id: Optional[str] = Header(None),
    x_signature: Optional[str] = Header(None),
):
    require_intent(INTENT_WRITE, x_intent)

    identity = require_identity(x_identity_id, IDENTITY_AGENT)

    payload = json.dumps(
        claim.dict(),
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
        identity_id=identity["id"],
        signature_verified=True,
    )

    return {"claim_id": c["id"]}

# ============================================================
# Resolution
# ============================================================

@app.get("/resolve/{entity}")
def resolve_entity_api(entity: str, x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return resolve_entity(entity)

# ============================================================
# Trust
# ============================================================

@app.get("/trust")
def read_all_trust(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return get_all_trust()

@app.get("/trust/{agent}")
def read_agent_trust(agent: str, x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"agent": agent, "trust": get_trust(agent)}

# ============================================================
# Trust Events
# ============================================================

@app.get("/trust/events")
def trust_events(limit: int = 50, offset: int = 0,
                 x_intent: Optional[str] = Header(None)):

    require_intent(INTENT_READ, x_intent)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM trust_events")
    total = cur.fetchone()["total"]

    cur.execute(
        """
        SELECT agent, change, reason, timestamp
        FROM trust_events
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )

    rows = cur.fetchall()
    conn.close()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }

# ============================================================
# Trust Timeline
# ============================================================

@app.get("/trust/timeline")
def trust_timeline(agent: str, x_intent: Optional[str] = Header(None)):

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

    current = get_trust(agent)

    for r in reversed(rows):
        current -= r["change"]

    timeline = []
    for r in rows:
        current += r["change"]
        timeline.append({
            "timestamp": r["timestamp"],
            "trust": round(current, 4),
        })

    return {"agent": agent, "timeline": timeline}

# ============================================================
# Kernel Adapter
# ============================================================

@app.post("/kernel/route")
def kernel_route(payload: dict):

    adapter_id = payload.get("adapter_id")
    content = payload.get("content")

    if not adapter_id or not content:
        raise HTTPException(status_code=400, detail="adapter_id and content required")

    msg = KernelMessage(
        source="api",
        type="thought",
        content=content,
        confidence=0.9,
    )

    return kernel_instance.route(adapter_id, msg.to_dict())

@app.get("/kernel/adapters")
def kernel_adapters(x_intent: Optional[str] = Header(None)):

    require_intent(INTENT_READ, x_intent)

    items = []

    for adapter_id in kernel_instance.registry.list():
        adapter = kernel_instance.registry.get(adapter_id)
        if not adapter:
            continue

        items.append({
            "adapter_id": adapter_id,
            "adapter_type": getattr(adapter, "adapter_type", "unknown"),
            "capabilities": adapter.capabilities(),
            "health": adapter.health(),
        })

    return items

# ============================================================
# Audit Error Reviews
# ============================================================

@app.get("/audit/error-reviews")
def audit_error_reviews(limit: int = 50, offset: int = 0,
                        x_intent: Optional[str] = Header(None)):

    require_intent(INTENT_READ, x_intent)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM error_reviews")
    total = cur.fetchone()["total"]

    cur.execute(
        """
        SELECT *
        FROM error_reviews
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )

    rows = cur.fetchall()
    conn.close()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }