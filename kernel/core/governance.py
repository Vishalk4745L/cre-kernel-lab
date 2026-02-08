# kernel/core/governance.py
# v0.3 — Human governance & override control

from kernel.core.audit import log_event

# simple in-memory human override registry
HUMAN_OVERRIDES = {}


def set_override(entity, value, reason="manual override", identity_id=None, signature_verified=False):
    """
    Highest-authority human override.
    This ALWAYS wins over kernel resolution.
    """

    previous = HUMAN_OVERRIDES.get(entity)

    HUMAN_OVERRIDES[entity] = {
        "value": value,
        "reason": reason
    }

    # audit log
    log_event("SET_OVERRIDE", {
        "actor": "HUMAN_ADMIN",
        "entity": entity,
        "previous_state": previous,
        "new_state": HUMAN_OVERRIDES[entity],
        "reason": reason,
        "identity_id": identity_id,
        "signature_verified": signature_verified
    })

    return HUMAN_OVERRIDES[entity]


def clear_override(entity, reason="manual clear", identity_id=None, signature_verified=False):
    """
    Remove human override (also audited).
    """

    previous = HUMAN_OVERRIDES.get(entity)

    if entity in HUMAN_OVERRIDES:
        del HUMAN_OVERRIDES[entity]

        log_event("CLEAR_OVERRIDE", {
            "actor": "HUMAN_ADMIN",
            "entity": entity,
            "previous_state": previous,
            "new_state": None,
            "reason": reason,
            "identity_id": identity_id,
            "signature_verified": signature_verified
        })

        return True

    return False


def check_override(entity):
    """
    Called by resolver.
    If override exists → resolver MUST obey.
    """
    return HUMAN_OVERRIDES.get(entity)