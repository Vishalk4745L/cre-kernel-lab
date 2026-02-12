"""
CRE Kernel API – v1.0 (FRONTEND SAFE BUILD)
Fully aligned with React Control Panel
"""

# ============================================================
# Imports
# ============================================================

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import time

# --- Kernel System ---
from kernel.core.kernel import Kernel
from kernel.adapters.mock_adapter import MockAgentAdapter
from kernel.core.message import KernelMessage
from kernel.core.ledger import add_claim, resolve_entity
from kernel.core.trust import (
    get_trust,
    get_all_trust,
    decay_all_agents,
    reward_agent,
)
from kernel.core.error_review import record_error_review
from kernel.core.memory_db import get_connection

# ============================================================
# Kernel Singleton
# ============================================================

kernel_instance = Kernel()

# Ensure mock-agent always registered (for CI + tests)
try:
    if not kernel_instance.registry.get("mock-agent"):
        kernel_instance.register_adapter(MockAgentAdapter())
except Exception:
    kernel_instance.register_adapter(MockAgentAdapter())

kernel_instance.register_adapter(MockAgentAdapter())

# ============================================================
# FastAPI Setup
# ============================================================

app = FastAPI(title="CRE Kernel API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INTENT_READ = "READ"
INTENT_WRITE = "WRITE"

trust_decay_lock = asyncio.Lock()

# ============================================================
# Models
# ============================================================

class KernelRouteRequest(BaseModel):
    adapter_id: str
    content: str


# ============================================================
# Intent Guard
# ============================================================

def require_intent(expected: str, intent: Optional[str]):
    if intent != expected:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid intent. Expected '{expected}'"
        )

# ============================================================
# Startup (ensure tables exist)
# ============================================================

@app.on_event("startup")
async def startup():

    # Ensure error_reviews table exists
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS error_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewer_agent TEXT,
            target_agent TEXT,
            entity TEXT,
            observed_value TEXT,
            expected_value TEXT,
            error_type TEXT,
            confidence REAL,
            evidence TEXT,
            timestamp REAL
        )
    """)

    conn.commit()
    conn.close()

    asyncio.create_task(trust_decay_loop())


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

# ============================================================
# Health
# ============================================================

@app.get("/")
def root_status(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"ok": True, "data": {"status": "CRE kernel alive"}}


@app.get("/kernel/status")
def kernel_status(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)

    adapters = kernel_instance.registry.list()

    return {
        "ok": True,
        "data": {
            "status": "CRE kernel alive",
            "version": app.version,
            "adapters_registered": len(adapters),
            "timestamp": time.time(),
        },
    }

# ============================================================
# Resolution
# ============================================================

@app.get("/resolve/{entity}")
def resolve_entity_api(entity: str, x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"ok": True, "data": resolve_entity(entity)}

# ============================================================
# Trust
# ============================================================

@app.get("/trust")
def read_all_trust(x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {"ok": True, "data": get_all_trust()}


@app.get("/trust/{agent}")
def read_agent_trust(agent: str, x_intent: Optional[str] = Header(None)):
    require_intent(INTENT_READ, x_intent)
    return {
        "ok": True,
        "data": {
            "agent": agent,
            "trust": get_trust(agent),
        },
    }

# ============================================================
# Trust Events (frontend paged)
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
        "ok": True,
        "data": {
            "items": [dict(r) for r in rows] if rows else [],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
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

    return {"ok": True, "data": timeline}

# ============================================================
# Kernel Route (NO MORE 422)
# ============================================================

@app.post("/kernel/route")
def kernel_route(
    request: KernelRouteRequest,
    x_intent: Optional[str] = Header(None),
):

    require_intent(INTENT_WRITE, x_intent)

    msg = KernelMessage(
        source="api",
        type="thought",
        content=request.content,
        confidence=0.9,
    )

    routed = kernel_instance.route(request.adapter_id, msg.to_dict())

    returned_agent = routed.get("agent") or request.adapter_id
    adapter_content = routed.get("reply") or routed.get("content") or ""
    adapter_confidence = float(routed.get("confidence", 0.0) or 0.0)

    # auto claim
    add_claim(
        agent=returned_agent,
        entity="adapter_response",
        value=str(adapter_content),
        confidence=adapter_confidence,
        identity_id="system",
        signature_verified=True,
    )

    reward_agent(returned_agent, adapter_confidence, reason="adapter_route_claim")

    if adapter_confidence < 0.5:
        record_error_review(
            reviewer_agent="system",
            target_agent=returned_agent,
            entity="adapter_response",
            observed_value=str(adapter_content),
            expected_value="high_confidence_response",
            error_type="LOW_CONFIDENCE",
            confidence=adapter_confidence,
            evidence="auto-generated by kernel route",
            timestamp=time.time(),
        )

    return {"ok": True, "data": routed}

# ============================================================
# Adapters
# ============================================================

@app.get("/kernel/adapters")
def kernel_adapters(x_intent: Optional[str] = Header(None)):

    require_intent(INTENT_READ, x_intent)

    items = []

    for adapter_id in kernel_instance.registry.list():
        adapter = kernel_instance.registry.get(adapter_id)

        items.append({
            "adapter_id": adapter_id,
            "adapter_type": getattr(adapter, "adapter_type", "unknown"),
            "health": adapter.health(),
            "capabilities": adapter.capabilities(),
        })

    return {"ok": True, "data": items if items else []}

# ============================================================
# Audit
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
        "ok": True,
        "data": {
            "items": [dict(r) for r in rows] if rows else [],
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }