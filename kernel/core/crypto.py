"""
v0.8 – Cryptographic Signature Verification (FOUNDATION)

Purpose:
- Real asymmetric cryptography
- Public / private key signatures
- Kernel verifies, never signs
"""

from fastapi import HTTPException
from typing import Optional
import base64
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def compute_payload_hash(payload: str) -> bytes:
    """
    Canonical hash of request payload
    """
    return hashlib.sha256(payload.encode("utf-8")).digest()


# -------------------------------------------------
# Signature Verification
# -------------------------------------------------

def verify_signature(
    public_key_b64: str,
    payload: str,
    signature_b64: Optional[str],
):
    """
    Verify Ed25519 signature

    public_key_b64: base64 encoded public key
    payload: canonical payload string
    signature_b64: base64 encoded signature
    """

    if not signature_b64:
        raise HTTPException(
            status_code=401,
            detail="Missing cryptographic signature"
        )

    try:
        public_key_bytes = base64.b64decode(public_key_b64)
        signature_bytes = base64.b64decode(signature_b64)

        public_key = ed25519.Ed25519PublicKey.from_public_bytes(
            public_key_bytes
        )

        payload_hash = compute_payload_hash(payload)

        public_key.verify(signature_bytes, payload_hash)

    except (InvalidSignature, ValueError):
        raise HTTPException(
            status_code=403,
            detail="Invalid cryptographic signature"
        )

    return True