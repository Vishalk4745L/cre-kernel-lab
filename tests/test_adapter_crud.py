from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_adapter_register_list_delete(monkeypatch):
    monkeypatch.setenv("KERNEL_API_KEY", "secret")

    create = client.post(
        "/kernel/adapters/register",
        json={"adapter_id": "custom-a", "adapter_type": "agent"},
        headers={"X-API-KEY": "secret"},
    )
    assert create.status_code == 200

    listed = client.get("/kernel/adapters")
    assert listed.status_code == 200
    ids = [item["adapter_id"] for item in listed.json()["data"]]
    assert "custom-a" in ids

    deleted = client.delete("/kernel/adapters/custom-a", headers={"X-API-KEY": "secret"})
    assert deleted.status_code == 200
