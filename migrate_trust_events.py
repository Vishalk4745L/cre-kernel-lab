from kernel.core.memory_db import get_connection
import time

conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS trust_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT NOT NULL,
    change REAL NOT NULL,
    reason TEXT NOT NULL,
    confidence REAL,
    timestamp REAL NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ trust_events table ready")