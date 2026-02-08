# kernel/core/ledger.py
import time
from kernel.core.governance import check_override

# in-memory ledger
ledger = []

# Explicit agent trust (v0.2)
AGENT_TRUST = {
    "Senior": 0.9,
    "Junior": 0.2
}

# how fast old claims decay
DECAY_RATE = 0.0005   # safe & slow
MARGIN = 0.15         # minimum margin to resolve


def add_claim(agent, entity, value, confidence):
    claim = {
        "id": len(ledger) + 1,
        "agent": agent,
        "entity": entity,
        "value": value,
        "confidence": float(confidence),
        "trust": AGENT_TRUST.get(agent, 0.1),
        "timestamp": time.time()
    }
    ledger.append(claim)
    return claim


def resolve_entity(entity):
    # 🔐 v0.3 — HUMAN OVERRIDE (highest authority)
    override = check_override(entity)
    if override:
        return {
            "entity": entity,
            "value": override["value"],
            "confidence": 1.0,
            "status": "human_override",
            "reason": override["reason"]
        }

    now = time.time()
    scores = {}

    # aggregate weighted scores
    for c in ledger:
        if c["entity"] != entity:
            continue

        age = now - c["timestamp"]
        time_decay = max(0.1, 1 - age * DECAY_RATE)

        weight = c["confidence"] * c["trust"] * time_decay
        scores[c["value"]] = scores.get(c["value"], 0) + weight

    # no claims
    if not scores:
        return {
            "entity": entity,
            "status": "unknown"
        }

    # sort values by score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # only one value → resolve directly
    if len(sorted_scores) == 1:
        value, score = sorted_scores[0]
        return {
            "entity": entity,
            "value": value,
            "confidence": round(score, 2),
            "status": "resolved"
        }

    # check consensus margin
    (winner, top_score), (_, second_score) = sorted_scores[:2]

    if (top_score - second_score) < MARGIN:
        return {
            "entity": entity,
            "status": "locked"
        }

    return {
        "entity": entity,
        "value": winner,
        "confidence": round(top_score, 2),
        "status": "resolved"
    }