"""
Resolver compatibility layer.

Purpose:
- Keep legacy resolve_truth helpers for test scripts
- Normalize legacy claim shapes into consensus inputs
- Delegate entity resolution to the SQLite-backed ledger

This avoids duplicated logic while preserving historical entry points.
"""

from __future__ import annotations

import time
from typing import Dict, Iterable, List, Mapping

from kernel.core.consensus import resolve_consensus
from kernel.core.ledger import resolve_entity as resolve_entity_from_ledger
from kernel.core.trust import DEFAULT_TRUST

# Legacy decay defaults (from v0.2 resolver)
_DEFAULT_DECAY_RATE = 0.0005
_MIN_DECAY_FACTOR = 0.1


def resolve_truth(
    claims: Iterable[Mapping[str, object]],
    trust_map: Mapping[str, float],
    *,
    decay_rate: float = _DEFAULT_DECAY_RATE,
) -> Dict[str, object]:
    """
    Legacy resolver helper.

    Accepts a list of claim-like dicts with keys:
      - agent_id
      - value
      - confidence
      - claimed_at (datetime or timestamp, optional)

    Returns a consensus resolution dict (same shape as resolve_consensus).
    """
    now = time.time()
    normalized: List[Dict[str, object]] = []

    for claim in claims:
        agent_id = str(claim.get("agent_id") or claim.get("agent") or "")
        value = claim.get("value")
        confidence = float(claim.get("confidence", 0.0))
        claimed_at = claim.get("claimed_at")

        if claimed_at is not None:
            try:
                timestamp = float(getattr(claimed_at, "timestamp", lambda: claimed_at)())
                age = max(0.0, now - timestamp)
                decay = max(_MIN_DECAY_FACTOR, 1 - age * decay_rate)
                confidence *= decay
            except (TypeError, ValueError):
                pass

        normalized.append(
            {
                "value": value,
                "confidence": confidence,
                "trust": float(trust_map.get(agent_id, DEFAULT_TRUST)),
            }
        )

    return resolve_consensus(normalized)


def resolve_entity(entity: str) -> Dict[str, object]:
    """
    Resolve an entity using the canonical SQLite-backed ledger.
    """
    return resolve_entity_from_ledger(entity)
