from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_trust_websocket_stream_emits_on_route():
    with client.websocket_connect('/ws/trust') as websocket:
        client.post('/kernel/route', json={"adapter_id": "mock-agent", "content": "hello"})
        data = websocket.receive_json()

    assert data["agent"] == "mock-agent"
    assert "trust" in data
    assert "change" in data
