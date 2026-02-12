from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_write_route_requires_api_key_when_configured(monkeypatch):
    monkeypatch.setenv("KERNEL_API_KEY", "secret")

    bad = client.post("/kernel/route", json={"adapter_id": "mock-agent", "content": "x"})
    assert bad.status_code == 401

    good = client.post(
        "/kernel/route",
        json={"adapter_id": "mock-agent", "content": "x"},
        headers={"X-API-KEY": "secret"},
    )
    assert good.status_code == 200
