"""
v0.11 – Trust System (JSON-backed, STABLE)

Responsibilities:
- Maintain agent trust scores in JSON
- Reward / penalize agents based on outcomes
- Persist trust across restarts
- Expose trust for ledger and API usage
"""

import json
import os
from typing import Dict, Optional

# =================================================
# File paths
# =================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRUST_FILE = os.path.join(DATA_DIR, "trust.json")

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

def _ensure_store() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(TRUST_FILE):
        with open(TRUST_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _load_trust() -> Dict[str, float]:
    _ensure_store()
    try:
        with open(TRUST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {k: float(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def _save_trust(data: Dict[str, float]) -> None:
    with open(TRUST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# =================================================
# Public API (READ)
# =================================================

def get_trust(agent: str) -> float:
    trust = _load_trust()
    return float(trust.get(agent, DEFAULT_TRUST))


def get_all_trust() -> Dict[str, float]:
    return _load_trust()


# =================================================
# Learning Rules (WRITE)
# =================================================

def reward_agent(agent: str, confidence: Optional[float] = None) -> None:
    trust = _load_trust()

    old = trust.get(agent, DEFAULT_TRUST)
    conf = confidence if confidence is not None else 1.0
    conf = max(0.0, min(conf, 1.0))

    delta = BASE_REWARD * conf
    new = min(old + delta, TRUST_CEILING)

    trust[agent] = round(new, 4)
    _save_trust(trust)


def penalize_agent(agent: str, confidence: Optional[float] = None) -> None:
    trust = _load_trust()

    old = trust.get(agent, DEFAULT_TRUST)
    conf = confidence if confidence is not None else 1.0
    conf = max(0.0, min(conf, 1.0))

    delta = BASE_PENALTY * conf
    new = max(old - delta, TRUST_FLOOR)

    trust[agent] = round(new, 4)
    _save_trust(trust)


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
        reward_agent(agent, confidence)
    else:
        penalize_agent(agent, confidence)


# =================================================
# Future hook (safe stub)
# =================================================

def decay_all_agents() -> None:
    """
    v0.11 stub.
    Time-based decay will be implemented in v0.12+.
    """
    return