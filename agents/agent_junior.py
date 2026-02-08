# agents/agent_junior.py
"""
Junior Agent – CRE Kernel Client
Role: Low-trust / noisy agent
Purpose: Create disagreement to test trust learning
"""

import json
import base64
import requests
from cryptography.hazmat.primitives.asymmetric import ed25519

# =================================================
# CONFIG
# =================================================

KERNEL_URL = "http://127.0.0.1:8000"

AGENT_NAME = "Junior"          # MUST match identity registry
ENTITY = "API_PORT"

# ❌ Intentionally wrong value (to trigger disagreement)
VALUE = "7000"
CONFIDENCE = 0.6

# Junior's PRIVATE KEY (matches public key in identity.py)
PRIVATE_KEY_B64 = "GX8PfyZBUyfj4TdOzdvkrFZh6IMlNcckzNfksHCCNW4="

# =================================================
# CANONICAL PAYLOAD (MUST MATCH SERVER)
# =================================================

payload_dict = {
    "agent": AGENT_NAME,
    "entity": ENTITY,
    "value": VALUE,
    "confidence": CONFIDENCE,
}

payload = json.dumps(
    payload_dict,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")

# =================================================
# SIGN PAYLOAD (Ed25519)
# =================================================

private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
    base64.b64decode(PRIVATE_KEY_B64)
)

signature = base64.b64encode(
    private_key.sign(payload)
).decode("utf-8")

# =================================================
# SEND CLAIM TO KERNEL
# =================================================

headers = {
    "X-Intent": "WRITE",
    "X-Identity-Id": "Junior",     # 🔥 EXACT MATCH REQUIRED
    "X-Identity-Type": "AGENT",
    "X-Signature": signature,
}

response = requests.post(
    f"{KERNEL_URL}/claim",
    headers=headers,
    json=payload_dict,
)

print("Status:", response.status_code)

try:
    print(response.json())
except Exception:
    print(response.text)