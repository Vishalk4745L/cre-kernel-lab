"""
CRE Kernel – Identity & Public Key Registry (v1.0 STABLE)

Purpose:
- Bind identities to cryptographic public keys (Ed25519)
- Enforce identity presence, type, and activation
- Enable REAL signature verification
- Developer-friendly (easy to add / rotate keys)

SECURITY MODEL:
- ONLY public keys are stored (never private keys)
- Private keys always stay with agents / humans
- Identity must exist BEFORE any signed action

NOTE:
- In-memory registry (v1.x)
- SQLite / distributed registry comes in v2.x+
"""

from typing import Dict, Optional
from fastapi import HTTPException
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519

# =================================================
# Identity Types
# =================================================

IDENTITY_AGENT = "AGENT"
IDENTITY_HUMAN_ADMIN = "HUMAN_ADMIN"

# =================================================
# Identity Registry
# =================================================
# RULES:
# - key = identity_id (used in X-Identity-Id header)
# - public_key_b64 = Base64-encoded Ed25519 public key (32 bytes)
# - NEVER store private keys here

IDENTITIES: Dict[str, dict] = {

    # -------------------------------------------------
    # AGENTS
    # -------------------------------------------------

    "Senior": {
        "id": "Senior",
        "type": IDENTITY_AGENT,
        "active": True,

        # ⚠️ DEV / PLACEHOLDER KEY
        # Replace with REAL public key when rotating keys
        "public_key_b64": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    },

    "Junior": {
        "id": "Junior",
        "type": IDENTITY_AGENT,
        "active": True,

        # ✅ REAL PUBLIC KEY (matches agent_junior.py private key)
        "public_key_b64": "xtyXT9YG6S0iQHBXVvvcSyVgb/MDIo1nvvBOP9+lc/g=",
    },

    # -------------------------------------------------
    # HUMAN ADMIN (future use)
    # -------------------------------------------------
    # "admin-1": {
    #     "id": "admin-1",
    #     "type": IDENTITY_HUMAN_ADMIN,
    #     "active": True,
    #     "public_key_b64": "<ADMIN_PUBLIC_KEY_B64>",
    # },
}

# =================================================
# Identity Helpers
# =================================================

def get_identity(identity_id: str) -> Optional[dict]:
    """
    Fetch identity from registry.
    Returns None if identity does not exist.
    """
    return IDENTITIES.get(identity_id)


def require_identity(identity_id: Optional[str], expected_type: str) -> dict:
    """
    Enforce identity correctness.

    Checks:
    - Identity header exists
    - Identity is registered
    - Identity is active
    - Identity type matches endpoint requirement

    Used by:
    - /claim        → AGENT
    - /override/*  → HUMAN_ADMIN
    """
    if not identity_id:
        raise HTTPException(
            status_code=401,
            detail="Missing identity id"
        )

    identity = get_identity(identity_id)

    if not identity:
        raise HTTPException(
            status_code=403,
            detail="Unknown identity"
        )

    if not identity.get("active", False):
        raise HTTPException(
            status_code=403,
            detail="Identity inactive"
        )

    if identity.get("type") != expected_type:
        raise HTTPException(
            status_code=403,
            detail="Identity type mismatch"
        )

    return identity


def get_identity_public_key(identity: dict) -> ed25519.Ed25519PublicKey:
    """
    Load Ed25519 public key from identity.

    SECURITY:
    - Public key MUST decode to exactly 32 bytes
    - Any mismatch = hard failure
    """
    pub_b64 = identity.get("public_key_b64")

    if not pub_b64:
        raise HTTPException(
            status_code=500,
            detail="Identity missing public key"
        )

    try:
        pub_bytes = base64.b64decode(pub_b64)

        # Ed25519 public key is ALWAYS 32 bytes
        if len(pub_bytes) != 32:
            raise ValueError("Invalid Ed25519 public key length")

        return ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Invalid public key format"
        )