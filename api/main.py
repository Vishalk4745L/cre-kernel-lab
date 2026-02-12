"""CRE Kernel API v1.1"""

import asyncio
import json
import logging
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from queue import Queue
import os
import time
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kernel.core.kernel import Kernel
from kernel.adapters.mock_adapter import MockAgentAdapter
from kernel.core.message import KernelMessage
from kernel.core.ledger import add_claim, resolve_entity
from kernel.core.trust import (
    decay_all_agents,
    get_all_trust,
    get_trust,
    reward_agent,
    set_trust_event_callback,
)
from kernel.core.error_review import record_error_review
from kernel.core.memory_db import get_connection

kernel_instance = Kernel()

app = FastAPI(title="CRE Kernel API", version="1.1")

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


class KernelRouteRequest(BaseModel):
    adapter_id: str
    content: str


class AdapterRegisterRequest(BaseModel):
    adapter_id: str
    adapter_type: str = "agent"


class GenericDbAdapter(MockAgentAdapter):
    def __init__(self, adapter_id: str, adapter_type: str) -> None:
        self.adapter_id = adapter_id
        self.adapter_type = adapter_type


class TrustSocketManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._clients:
            self._clients.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


trust_socket_manager = TrustSocketManager()


def _ensure_logs_dir() -> Path:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def _configure_request_logger() -> tuple[logging.Logger, QueueListener]:
    logs_dir = _ensure_logs_dir()
    logger = logging.getLogger("kernel.requests")
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.propagate = False

    q: Queue = Queue(-1)
    queue_handler = QueueHandler(q)
    file_handler = logging.FileHandler(logs_dir / "kernel_requests.log")
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    listener = QueueListener(q, file_handler)
    logger.addHandler(queue_handler)
    listener.start()
    return logger, listener


request_logger, request_logger_listener = _configure_request_logger()


def require_write_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    expected_key = os.getenv("KERNEL_API_KEY")
    if not expected_key:
        return
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _insert_api_log(method: str, path: str, status: int, duration: float, timestamp: float) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO api_logs (method, path, status, duration, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (method, path, int(status), float(duration), float(timestamp)),
    )
    conn.commit()
    conn.close()


async def _persist_request_log(method: str, path: str, status: int, duration_ms: float, ts: float) -> None:
    payload = {
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration_ms, 3),
        "timestamp": ts,
    }
    request_logger.info(json.dumps(payload))
    await asyncio.to_thread(_insert_api_log, method, path, status, duration_ms, ts)


def _register_adapter_record(adapter_id: str, adapter_type: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO adapters (adapter_id, adapter_type, created_at)
        VALUES (?, ?, ?)
        """,
        (adapter_id, adapter_type, time.time()),
    )
    conn.commit()
    conn.close()


def _load_persisted_adapters() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT adapter_id, adapter_type FROM adapters")
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        adapter_id = row["adapter_id"]
        adapter_type = row["adapter_type"] or "agent"
        if kernel_instance.registry.get(adapter_id):
            continue
        if adapter_id == "mock-agent":
            kernel_instance.register_adapter(MockAgentAdapter())
        else:
            kernel_instance.register_adapter(GenericDbAdapter(adapter_id=adapter_id, adapter_type=adapter_type))


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        ts = time.time()
        asyncio.create_task(
            _persist_request_log(
                request.method,
                request.url.path,
                status,
                duration_ms,
                ts,
            )
        )


@app.on_event("startup")
async def startup():
    _register_adapter_record("mock-agent", "agent")
    _load_persisted_adapters()

    if not kernel_instance.registry.get("mock-agent"):
        kernel_instance.register_adapter(MockAgentAdapter())

    def _trust_callback(event: dict) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(trust_socket_manager.broadcast(event))

    set_trust_event_callback(_trust_callback)
    asyncio.create_task(trust_decay_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    request_logger_listener.stop()


async def trust_decay_loop():
    while True:
        await asyncio.sleep(300)
        async with trust_decay_lock:
            try:
                decay_all_agents()
            except Exception:
                pass


@app.get("/")
def root_status(x_intent: Optional[str] = Header(None)):
    return {"ok": True, "data": {"status": "CRE kernel alive", "intent": x_intent or INTENT_READ}}


@app.get("/kernel/status")
def kernel_status(x_intent: Optional[str] = Header(None)):
    adapters = kernel_instance.registry.list()

    return {
        "ok": True,
        "data": {
            "status": "CRE kernel alive",
            "version": app.version,
            "adapters_registered": len(adapters),
            "timestamp": time.time(),
            "intent": x_intent or INTENT_READ,
        },
    }


@app.get("/resolve/{entity}")
def resolve_entity_api(entity: str, x_intent: Optional[str] = Header(None)):
    return {"ok": True, "data": resolve_entity(entity), "intent": x_intent or INTENT_READ}


@app.get("/trust")
def read_all_trust(x_intent: Optional[str] = Header(None)):
    return {"ok": True, "data": get_all_trust(), "intent": x_intent or INTENT_READ}


@app.get("/trust/{agent}")
def read_agent_trust(agent: str, x_intent: Optional[str] = Header(None)):
    return {
        "ok": True,
        "data": {
            "agent": agent,
            "trust": get_trust(agent),
        },
        "intent": x_intent or INTENT_READ,
    }


@app.get("/trust/events")
def trust_events(limit: int = 50, offset: int = 0, x_intent: Optional[str] = Header(None)):
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
        "intent": x_intent or INTENT_READ,
    }


@app.get("/trust/timeline")
def trust_timeline(agent: str, x_intent: Optional[str] = Header(None)):
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
        timeline.append({"timestamp": r["timestamp"], "trust": round(current, 4)})

    return {"ok": True, "data": timeline, "intent": x_intent or INTENT_READ}


@app.websocket("/ws/trust")
async def trust_updates(websocket: WebSocket):
    await trust_socket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        trust_socket_manager.disconnect(websocket)


@app.post("/kernel/route")
def kernel_route(request: KernelRouteRequest, _: None = Depends(require_write_api_key), x_intent: Optional[str] = Header(None)):
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

    return {"ok": True, "data": routed, "intent": x_intent or INTENT_WRITE}


@app.get("/kernel/adapters")
def kernel_adapters(x_intent: Optional[str] = Header(None)):
    items = []
    for adapter_id in kernel_instance.registry.list():
        adapter = kernel_instance.registry.get(adapter_id)
        items.append(
            {
                "adapter_id": adapter_id,
                "adapter_type": getattr(adapter, "adapter_type", "unknown"),
                "health": adapter.health(),
                "capabilities": adapter.capabilities(),
            }
        )

    return {"ok": True, "data": items if items else [], "intent": x_intent or INTENT_READ}


@app.post("/kernel/adapters/register")
def register_adapter(request: AdapterRegisterRequest, _: None = Depends(require_write_api_key)):
    if kernel_instance.registry.get(request.adapter_id):
        return {"ok": True, "data": {"adapter_id": request.adapter_id, "registered": True}}

    if request.adapter_id == "mock-agent":
        adapter = MockAgentAdapter()
    else:
        adapter = GenericDbAdapter(adapter_id=request.adapter_id, adapter_type=request.adapter_type)

    kernel_instance.register_adapter(adapter)
    _register_adapter_record(request.adapter_id, request.adapter_type)
    return {"ok": True, "data": {"adapter_id": request.adapter_id, "adapter_type": request.adapter_type}}


@app.delete("/kernel/adapters/{adapter_id}")
def delete_adapter(adapter_id: str, _: None = Depends(require_write_api_key)):
    if adapter_id in kernel_instance.registry._adapters:
        del kernel_instance.registry._adapters[adapter_id]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM adapters WHERE adapter_id = ?", (adapter_id,))
    conn.commit()
    conn.close()

    return {"ok": True, "data": {"adapter_id": adapter_id, "deleted": True}}


@app.get("/audit/error-reviews")
def audit_error_reviews(limit: int = 50, offset: int = 0, x_intent: Optional[str] = Header(None)):
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
        "intent": x_intent or INTENT_READ,
    }
