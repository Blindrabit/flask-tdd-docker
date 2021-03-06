import json


def test_ping(test_app):
    client = test_app.test_client()
    response = client.get("/ping")
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data.get("message") == "pong!"
    assert data.get("status") == "success"
