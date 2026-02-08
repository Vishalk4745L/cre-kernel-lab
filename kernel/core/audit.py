# kernel/core/audit.py
"""
v0.4 – Audit Log Persistence
Append-only, immutable audit trail for CRE Kernel
"""

import json
import time
from pathlib import Path

# Audit log file (JSON Lines format)
AUDIT_LOG_FILE = Path("audit_log.jsonl")


def log_event(event_type: str, data: dict):
    """
    Record an immutable audit event.

    event_type: str
        Examples:
        - CLAIM_ADDED
        - RESOLVE_CALLED
        - OVERRIDE_SET
        - OVERRIDE_CLEARED

    data: dict
        Event-specific metadata
    """

    entry = {
        "timestamp": time.time(),
        "event": event_type,
        "data": data
    }

    # Append-only write (never overwrite history)
    with AUDIT_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")