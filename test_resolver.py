from datetime import datetime
from kernel.core.resolver import resolve_truth

# Fake trust scores
trust_map = {
    "senior": 0.9,
    "junior": 0.2,
}

# Fake claims (like agents writing memory)
claims = [
    {
        "agent_id": "senior",
        "value": "5432",
        "confidence": 1.0,
        "claimed_at": datetime.utcnow(),
    },
    {
        "agent_id": "junior",
        "value": "3306",
        "confidence": 1.0,
        "claimed_at": datetime.utcnow(),
    },
]

result = resolve_truth(claims, trust_map)

print("RESULT:", result)
