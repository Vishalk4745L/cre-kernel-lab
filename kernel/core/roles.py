"""
v0.9 – Role Matrix

Defines what actions each identity type is allowed to perform.
No enforcement here — rules only.
"""

# Actions
ACTION_CLAIM = "CLAIM"
ACTION_OVERRIDE = "OVERRIDE"
ACTION_READ = "READ"
ACTION_AUDIT = "AUDIT"

# Role → allowed actions
ROLE_MATRIX = {
    "AGENT": {
        ACTION_CLAIM,
        ACTION_READ,
    },
    "HUMAN_ADMIN": {
        ACTION_CLAIM,
        ACTION_OVERRIDE,
        ACTION_READ,
        ACTION_AUDIT,
    },
    "OBSERVER": {
        ACTION_READ,
    },
}

def role_allows(identity_type: str, action: str) -> bool:
    """
    Check whether a role allows a given action
    """
    allowed = ROLE_MATRIX.get(identity_type, set())
    return action in allowed