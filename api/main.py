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


# ============================================================
# Kernel Init (CI SAFE)
# ============================================================

kernel_instance = Kernel()

# Always register mock-agent (required for CI + tests)
try:
    kernel_instance.register_adapter(MockAgentAdapter())
except Exception:
    pass

# Ensure mock-agent always exists (for CI + tests)
try:
    if not kernel_instance.registry.get("mock-agent"):
        kernel_instance.register_adapter(MockAgentAdapter())
except Exception:
    kernel_instance.register_adapter(MockAgentAdapter())


# ============================================================
# FastAPI App
# ============================================================

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


# ============================================================
# Models
# ============================================================

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


# ============================================================
# Trust WebSocket Manager
# ============================================================

class TrustSocketManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        dead = []
        for ws in list(self._clients):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


trust_socket_manager = TrustSocketManager()


# ============================================================
# Logging
# ============================================================

def _ensure_logs_dir() -> Path:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def _configure_request_logger():
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


# ============================================================
# API Key
# ============================================================

def require_write_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    expected_key = os.getenv("KERNEL_API_KEY")
    if not expected_key:
        return
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ============================================================
# Background Trust Decay
# ============================================================

async def trust_decay_loop():
    while True:
        await asyncio.sleep(300)
        async with trust_decay_lock:
            try:
                decay_all_agents()
            except Exception:
                pass


@app.on_event("startup")
async def startup():
    def _trust_callback(event: dict) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(trust_socket_manager.broadcast(event))

    set_trust_event_callback(_trust_callback)
    asyncio.create_task(trust_decay_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    request_logger_listener.stop()


# ============================================================
# Health
# ============================================================

@app.get("/")
def root_status(x_intent: Optional[str] = Header(None)):
    return {"ok": True, "data": {"status": "CRE kernel alive", "intent": x_intent or INTENT_READ}}


@app.get("/kernel/status")
def kernel_status(x_intent: Optional[str] = Header(None)):
    adapters = kernel_instance.registry.list()
    return {
        "ok": True,
        "data": {
            "version": app.version,
            "adapters_registered": len(adapters),
            "timestamp": time.time(),
        },
    }


# ============================================================
# Trust
# ============================================================

@app.get("/trust")
def read_all_trust():
    return {"ok": True, "data": get_all_trust()}


@app.get("/trust/{agent}")
def read_agent_trust(agent: str):
    return {"ok": True, "data": {"agent": agent, "trust": get_trust(agent)}}


# ============================================================
# Kernel Route
# ============================================================

@app.post("/kernel/route")
def kernel_route(
    request: KernelRouteRequest,
    _: None = Depends(require_write_api_key),
):
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
            evidence="auto-generated",
            timestamp=time.time(),
        )

    return {"ok": True, "data": routed}


# ============================================================
# WebSocket
# ============================================================

@app.websocket("/ws/trust")
async def trust_updates(websocket: WebSocket):
    await trust_socket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        trust_socket_manager.disconnect(websocket)