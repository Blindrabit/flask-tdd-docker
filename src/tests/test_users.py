import json

import pytest

from src.api.users.models import User


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
    assert resp.status_code == 409
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


def test_remove_user(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    user = add_user(username="sarah", email="sarah@email.com")
    client = test_app.test_client()
    response_1 = client.get("/users")
    data = json.loads(response_1.data.decode())
    assert response_1.status_code == 200
    assert len(data) == 1

    response_2 = client.delete(f"/users/{user.id}")
    data = json.loads(response_2.data.decode())
    assert response_2.status_code == 200
    assert data.get("message") == "sarah@email.com was removed!"

    response_3 = client.get("/users")
    data = json.loads(response_3.data.decode())
    assert response_3.status_code == 200
    assert len(data) == 0


def test_remove_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    response = client.delete("/users/999")
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert "User 999 does not exist!" in data["message"]


def test_update_user(test_app, test_database, add_user):
    user = add_user(username="sarah", email="sarah@email.com")
    client = test_app.test_client()
    response_1 = client.put(
        f"/users/{user.id}",
        data=json.dumps({"username": "not sarah", "email": "not_sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response_1.data.decode())
    assert response_1.status_code == 200
    assert data.get("message") == f"User {user.id} was updated!"

    response_2 = client.get(f"/users/{user.id}")
    data = json.loads(response_2.data.decode())
    assert data.get("username") == "not sarah"
    assert data.get("email") == "not_sarah@email.com"


@pytest.mark.parametrize(
    "user_id, payload, status_code, message",
    [
        [1, {}, 400, "Input payload validation failed"],
        [
            1,
            {"email": "sarah@email.com"},
            400,
            "Input payload validation failed",
        ],
        [
            999,
            {"username": "sarah", "email": "sarah@email.com"},
            404,
            "User 999 does not exist",
        ],
    ],
)
def test_update_user_invalid(
    test_app, test_database, user_id, payload, status_code, message
):
    client = test_app.test_client()
    resp = client.put(
        f"/users/{user_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app, test_database, add_user):
    add_user("sarah", "sarah@email.com")
    user = add_user("not_sarah", "notsarah@email.com")

    client = test_app.test_client()
    resp = client.put(
        f"/users/{user.id}",
        data=json.dumps({"username": "something", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 409
    assert "Sorry. That email already exists." in data["message"]
