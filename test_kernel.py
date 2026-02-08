# test_kernel.py
# Simple test for CRE Kernel (Ledger + Resolver)

from kernel.core.ledger import submit_claim
from kernel.core.resolver import resolve_truth

# Step 1: Agents (mock trust scores)
AGENTS = {
    "senior": 0.9,
    "junior": 0.2
}

# Step 2: Senior writes truth
submit_claim(
    agent_id="senior",
    entity="DB_PORT",
    attribute="value",
    value="5432",
    confidence=1.0
)

# Step 3: Junior hallucinates
submit_claim(
    agent_id="junior",
    entity="DB_PORT",
    attribute="value",
    value="3306",
    confidence=1.0
)

# Step 4: Resolve truth
result = resolve_truth(
    entity="DB_PORT",
    attribute="value"
)

print("RESOLVED RESULT:")
print(result)