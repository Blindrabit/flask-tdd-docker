import json

from src.api.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"username": "sarah", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 201
    assert data.get("message") == "sarah@email.com was added!"


def test_add_user_invalid_json(test_app, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users", data=json.dumps({}), content_type="application/json"
    )

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert data.get("message") == "Input payload validation failed"


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert data.get("message") == "Input payload validation failed"


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    client.post(
        "/users",
        data=json.dumps({"username": "sarah", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    resp = client.post(
        "/users",
        data=json.dumps({"username": "sarah", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert data.get("message") == "Sorry. That email already exists."


def test_single_user(test_app, test_database, add_user):
    user = add_user(username="sarah", email="sarah@email.com")
    client = test_app.test_client()
    response = client.get(f"/users/{user.id}")
    data = json.loads(response.data.decode())
    assert data.get("username") == "sarah"
    assert data.get("email") == "sarah@email.com"


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    response = client.get("/users/999")
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert "User 999 does not exist" in data.get("message")


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user(username="sarah", email="sarah@email.com")
    add_user(username="adam", email="adam@email.com")
    client = test_app.test_client()
    response = client.get("/users")
    data = json.loads(response.data.decode())
    assert len(data) == 2
    assert "sarah" in data[0]["username"]
    assert "sarah@email.com" in data[0]["email"]
    assert "adam" in data[1]["username"]
    assert "adam@email.com" in data[1]["email"]
