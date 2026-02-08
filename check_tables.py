from kernel.core.memory_db import get_connection

c = get_connection()
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in cur.fetchall()])
c.close()