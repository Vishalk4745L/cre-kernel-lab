import time
from kernel.core.memory_db import get_connection

conn = get_connection()
cur = conn.cursor()

# Add column if it does not exist
try:
    cur.execute("ALTER TABLE trust ADD COLUMN last_updated REAL")
except Exception:
    pass  # column already exists

# Backfill existing rows
now = time.time()
cur.execute(
    """
    UPDATE trust
    SET last_updated = ?
    WHERE last_updated IS NULL
    """,
    (now,)
)

conn.commit()
conn.close()

print("✅ trust.last_updated column ready")