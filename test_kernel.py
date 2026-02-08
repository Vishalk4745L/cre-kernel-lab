# test_kernel.py
# Simple test for CRE Kernel (Ledger + Consensus)

from kernel.core.ledger import add_claim, resolve_entity

# Step 2: Senior writes truth
add_claim(
    agent="senior",
    entity="DB_PORT",
    value="5432",
    confidence=1.0,
)

# Step 3: Junior hallucinates
add_claim(
    agent="junior",
    entity="DB_PORT",
    value="3306",
    confidence=1.0,
)

# Step 4: Resolve truth
result = resolve_entity("DB_PORT")

print("RESOLVED RESULT:")
print(result)
