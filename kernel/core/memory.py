# kernel/core/memory.py
"""
v0.11 – Persistent Memory Engine (JSON)

Stores:
- trust
- claims
- resolutions

Loads on startup
Saves on update
"""

import json
import os
from typing import Any

DATA_DIR = "data"

TRUST_FILE = os.path.join(DATA_DIR, "trust.json")
CLAIMS_FILE = os.path.join(DATA_DIR, "claims.json")
RESOLUTIONS_FILE = os.path.join(DATA_DIR, "resolutions.json")


def _load(path: str, default: Any):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except Exception:
        return default


def _save(path: str, data: Any):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# -------------------------
# TRUST
# -------------------------

def load_trust():
    return _load(TRUST_FILE, {})


def save_trust(trust: dict):
    _save(TRUST_FILE, trust)


# -------------------------
# CLAIMS
# -------------------------

def load_claims():
    return _load(CLAIMS_FILE, [])


def save_claims(claims: list):
    _save(CLAIMS_FILE, claims)


# -------------------------
# RESOLUTIONS
# -------------------------

def load_resolutions():
    return _load(RESOLUTIONS_FILE, [])


def save_resolutions(resolutions: list):
    _save(RESOLUTIONS_FILE, resolutions)