"""
CRE Kernel – Signature Verification (v0.8 STABLE)

Purpose:
- Verify Ed25519 signatures
- Enforce strict authentication
"""

from fastapi import HTTPException
import base64
import os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# =================================================
# DEV MODE FLAG
# =================================================
# Set to "False" to enforce signature verification
DEV_MODE = False   # 🔴 CHANGED TO False FOR PROD

# =================================================
# Signature Verification
# =================================================

def require_signature(
    signature_b64: str,
    payload: bytes,
    public_key: Ed25519PublicKey,
):
    """
    Verify Ed25519 signature.

    DEV MODE:
    - Skips verification
    - Logs warning
    """

    if DEV_MODE:
        print("⚠️ DEV MODE: Signature verification bypassed")
        return

    if not signature_b64:
        raise HTTPException(
            status_code=401,
            detail="Missing signature"
        )

    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, payload)

    except Exception:
        raise HTTPException(
            status_code=403,
            detail="Invalid signature"
        )
