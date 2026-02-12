from fastapi.testclient import TestClient

from api.main import app
from kernel.core.memory_db import get_connection


client = TestClient(app)


def _count_rows(table: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) AS total FROM {table}")
    total = int(cur.fetchone()["total"])
    conn.close()
    return total


def test_kernel_route_creates_trust_event_and_error_review_for_low_confidence() -> None:
    before_trust_events = _count_rows("trust_events")
    before_error_reviews = _count_rows("error_reviews")

    response = client.post(
        "/kernel/route",
        json={"adapter_id": "mock-agent", "content": "route me"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["agent"] == "mock-agent"

    after_trust_events = _count_rows("trust_events")
    after_error_reviews = _count_rows("error_reviews")

    assert after_trust_events > before_trust_events
    assert after_error_reviews > before_error_reviews
