"""
Trust Timeline Plotter – v0.15

Purpose:
- Fetch absolute trust timeline from CRE Kernel
- Plot trust vs time (graph-ready)
- No reconstruction logic needed (API already does it)
"""

import requests
import matplotlib.pyplot as plt
from datetime import datetime

# ==================================================
# Configuration
# ==================================================

API_URL = "http://127.0.0.1:8000/trust/timeline?agent=Senior"
HEADERS = {
    "X-Intent": "READ"
}

# ==================================================
# Fetch trust timeline from API
# ==================================================

response = requests.get(API_URL, headers=HEADERS)
response.raise_for_status()

data = response.json()

# API response structure:
# {
#   "agent": "Senior",
#   "timeline": [
#       { "timestamp": 1234567890.0, "trust": 0.98 },
#       ...
#   ]
# }

timeline = data["timeline"]

if not timeline:
    print("⚠️ No trust history available")
    exit(0)

# ==================================================
# Prepare data for plotting
# ==================================================

timestamps = [
    datetime.fromtimestamp(event["timestamp"])
    for event in timeline
]

trust_values = [
    event["trust"]
    for event in timeline
]

# ==================================================
# Plot
# ==================================================

plt.figure(figsize=(10, 5))
plt.plot(timestamps, trust_values, marker="o")

plt.title(f"Trust Timeline – {data['agent']}")
plt.xlabel("Time")
plt.ylabel("Trust Score")
plt.ylim(0, 1.05)
plt.grid(True)

plt.tight_layout()
plt.show()