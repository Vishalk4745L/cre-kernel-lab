"""
v0.9 – Limits & Quotas

Defines rate limits and quotas per identity type.
No enforcement here — rules only.
"""

import time

# Default limits (per identity type)
LIMITS = {
    "AGENT": {
        "max_claims_per_minute": 5,
    },
    "HUMAN_ADMIN": {
        "max_claims_per_minute": 100,
    },
}

# In-memory counter (v0.9 simple)
_CLAIM_COUNTER = {}

def record_claim(identity_id: str):
    """
    Record a claim timestamp for an identity
    """
    now = time.time()
    _CLAIM_COUNTER.setdefault(identity_id, []).append(now)

def get_recent_claims(identity_id: str, window_seconds: int = 60) -> int:
    """
    Count claims in the last window_seconds
    """
    now = time.time()
    timestamps = _CLAIM_COUNTER.get(identity_id, [])

    recent = [t for t in timestamps if now - t <= window_seconds]
    _CLAIM_COUNTER[identity_id] = recent  # cleanup

    return len(recent)

def limit_allows(identity_type: str, identity_id: str) -> bool:
    """
    Check whether identity is within its rate limit
    """
    rules = LIMITS.get(identity_type)
    if not rules:
        return False

    max_per_min = rules["max_claims_per_minute"]
    used = get_recent_claims(identity_id)

    return used < max_per_min