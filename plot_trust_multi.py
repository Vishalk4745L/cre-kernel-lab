"""
Multi-agent Trust Timeline Plot
Client-side aggregation (OPTION 1)
"""

import requests
import matplotlib.pyplot as plt

# -----------------------------------------
# CONFIG
# -----------------------------------------

API_BASE = "http://127.0.0.1:8000"
HEADERS = {"X-Intent": "READ"}

AGENTS = ["Senior", "Junior"]   # add more agents here

# -----------------------------------------
# Fetch timeline for one agent
# -----------------------------------------

def fetch_timeline(agent):
    url = f"{API_BASE}/trust/timeline?agent={agent}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["timeline"]

# -----------------------------------------
# Plot multiple agents
# -----------------------------------------

def plot_multi_agent():
    plt.figure(figsize=(10, 5))

    for agent in AGENTS:
        timeline = fetch_timeline(agent)

        if not timeline:
            print(f"⚠️ No data for {agent}")
            continue

        x = [e["timestamp"] for e in timeline]
        y = [e["trust"] for e in timeline]

        plt.plot(x, y, marker="o", label=agent)

    plt.title("Trust Evolution (Multi-Agent)")
    plt.xlabel("Time (unix timestamp)")
    plt.ylabel("Trust Score")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------
# Run
# -----------------------------------------

if __name__ == "__main__":
    plot_multi_agent()