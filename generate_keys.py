"""
Generate Ed25519 key pair for CRE Kernel agents
"""

import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

AGENT_NAME = "Junior"

# Generate key pair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Serialize private key (RAW)
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
)

# Serialize public key (RAW)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)

# Base64 encode
private_b64 = base64.b64encode(private_bytes).decode()
public_b64 = base64.b64encode(public_bytes).decode()

print("====================================")
print(f"Agent        : {AGENT_NAME}")
print("====================================")
print("PRIVATE KEY (KEEP SECRET)")
print(private_b64)
print("------------------------------------")
print("PUBLIC KEY (STORE IN SERVER)")
print(public_b64)
print("====================================")