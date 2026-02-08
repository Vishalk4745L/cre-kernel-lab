"""
Client-side claim signer (Junior agent)

Purpose:
- Create canonical JSON payload
- Sign using Ed25519 PRIVATE KEY
- Output Base64 signature for API usage
"""

import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519

# =================================================
# 🔐 Junior PRIVATE KEY (KEEP SECRET)
# =================================================
# DO NOT put this in server code
PRIVATE_KEY_B64 = "tyCAXGEj8DmGJllVGw3H5j/FsXybExoRJZ7h/uZM79A="

# =================================================
# Claim payload (MUST match API exactly)
# =================================================
claim = {
    "agent": "Junior",
    "entity": "API_PORT",
    "value": "9000",
    "confidence": 0.6,
}

# =================================================
# Canonical JSON (VERY IMPORTANT)
# =================================================
payload_bytes = json.dumps(
    claim,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")

# =================================================
# Load private key
# =================================================
private_key_bytes = base64.b64decode(PRIVATE_KEY_B64)
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

# =================================================
# Sign payload
# =================================================
signature = private_key.sign(payload_bytes)

# Encode signature to Base64 (for HTTP header)
signature_b64 = base64.b64encode(signature).decode()

print("=== SIGNATURE GENERATED ===")
print(signature_b64)