"""
v0.9 – Multi-Agent Consensus Engine

Purpose:
- Resolve conflicting claims
- Use trust + confidence
- Deterministic (no ML yet)
"""

from typing import List, Dict


def resolve_consensus(claims: List[Dict]) -> Dict:
    """
    Input: list of claims for the same entity
    Each claim must include:
      - value
      - confidence
      - trust

    Output:
      {
        status: resolved | contested | unknown,
        value: optional,
        reason: explanation
      }
    """

    if not claims:
        return {
            "status": "unknown",
            "reason": "No claims available"
        }

    # Single claim → resolved
    if len(claims) == 1:
        c = claims[0]
        return {
            "status": "resolved",
            "value": c["value"],
            "reason": "Single claim"
        }

    # -------------------------------------------------
    # Group claims by value
    # -------------------------------------------------
    groups = {}
    for c in claims:
        groups.setdefault(c["value"], []).append(c)

    # Everyone agrees
    if len(groups) == 1:
        value = list(groups.keys())[0]
        return {
            "status": "resolved",
            "value": value,
            "reason": "All agents agree"
        }

    # -------------------------------------------------
    # Trust-weighted scoring
    # -------------------------------------------------
    scores = []

    for value, group in groups.items():
        score = 0.0
        for c in group:
            score += c.get("confidence", 0.0) * c.get("trust", 1.0)
        scores.append((value, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    top_value, top_score = scores[0]
    second_value, second_score = scores[1]

    # Clear winner?
    if top_score >= second_score * 1.2:
        return {
            "status": "resolved",
            "value": top_value,
            "reason": "Trust-weighted consensus"
        }

    # Too close → contested
    return {
        "status": "contested",
        "reason": "Conflicting claims with no clear winner"
    }