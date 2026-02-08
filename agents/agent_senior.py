# agents/agent_senior.py
"""
Senior Agent – CRE Kernel Client
Role: Stable, high-trust infrastructure agent
"""

import json
import base64
import requests
from cryptography.hazmat.primitives.asymmetric import ed25519

# =================================================
# CONFIG
# =================================================

KERNEL_URL = "http://127.0.0.1:8000"
AGENT_NAME = "Senior"
ENTITY = "API_PORT"
VALUE = "9000"
CONFIDENCE = 0.9

# ⚠️ SAME private key you already use (Senior)
PRIVATE_KEY_B64 = "GX8PfyZBUyfj4TdOzdvkrFZh6IMlNcckzNfksHCCNW4="

# =================================================
# SIGN PAYLOAD
# =================================================

payload = json.dumps(
    {
        "agent": AGENT_NAME,
        "entity": ENTITY,
        "value": VALUE,
        "confidence": CONFIDENCE,
    },
    sort_keys=True,
    separators=(",", ":"),
).encode()

private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
    base64.b64decode(PRIVATE_KEY_B64)
)

signature = base64.b64encode(private_key.sign(payload)).decode()

# =================================================
# SEND CLAIM
# =================================================

headers = {
    "X-Intent": "WRITE",
    "X-Identity-Id": "agent-1",
    "X-Identity-Type": "AGENT",
    "X-Signature": signature,
}

resp = requests.post(
    f"{KERNEL_URL}/claim",
    headers=headers,
    json={
        "agent": AGENT_NAME,
        "entity": ENTITY,
        "value": VALUE,
        "confidence": CONFIDENCE,
    },
)

print("Status:", resp.status_code)
print(resp.json())