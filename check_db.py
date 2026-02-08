# check_db.py
"""
Simple DB check script

Purpose:
- Connect to SQLite memory DB
- List all tables created by memory_db.py
"""

from kernel.core.memory_db import get_connection

def main():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()

    print("Tables in SQLite DB:")
    for row in tables:
        # row is sqlite3.Row
        print("-", row["name"] if isinstance(row, dict) or hasattr(row, "__getitem__") else row)

    conn.close()

if __name__ == "__main__":
    main()