import json
from datetime import datetime

import pytest

from src.api.users import views


def test_add_user(test_app, monkeypatch):
    def mock_get_user_by_email(user_email):
        return None

    def mock_add_user(username, email):
        return True

    monkeypatch.setattr(views, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(views, "add_user", mock_add_user)

    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"username": "sarah", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 201
    assert data.get("message") == "sarah@email.com was added!"


def test_add_user_invalid_json(test_app):
    client = test_app.test_client()
    response = client.post(
        "/users", data=json.dumps({}), content_type="application/json"
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app, monkeypatch):
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app, monkeypatch):
    def mock_get_user_by_email(user_email):
        return True

    def mock_add_user(username, email):
        return True

    monkeypatch.setattr(views, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(views, "add_user", mock_add_user)
    client = test_app.test_client()
    response = client.post(
        "/users",
        data=json.dumps({"username": "sarah", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 409
    assert "Sorry. That email already exists." in data["message"]


def test_single_user(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return {
            "id": 1,
            "username": "sarah",
            "email": "sarah@email.com",
            "created_date": datetime.now(),
        }

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    response = client.get("/users/1")
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data.get("email") == "sarah@email.com"
    assert data.get("username") == "sarah"


def test_single_user_incorrect_id(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    response = client.get("/users/999")
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app, monkeypatch):
    def mock_get_all_users():
        return [
            {
                "id": 1,
                "username": "sarah",
                "email": "sarah@email.com",
                "created_date": datetime.now(),
            },
            {
                "id": 2,
                "username": "adam",
                "email": "adam@email.com",
                "created_date": datetime.now(),
            },
        ]

    monkeypatch.setattr(views, "get_all_users", mock_get_all_users)
    client = test_app.test_client()
    response = client.get("/users")
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert len(data) == 2
    assert "sarah" in data[0]["username"]
    assert "sarah@email.com" in data[0]["email"]
    assert "adam" in data[1]["username"]
    assert "adam@email.com" in data[1]["email"]


def test_remove_user(test_app, monkeypatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id):
        d = AttrDict()
        d.update({"id": 1, "username": "sarah", "email": "sarah@email.com"})
        return d

    def mock_delete_user(user):
        return True

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(views, "delete_user", mock_delete_user)
    client = test_app.test_client()
    response = client.delete("/users/1")
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data.get("message") == "sarah@email.com was removed!"


def test_remove_user_incorrect_id(test_app, monkeypatch):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    response = client.delete("/users/999")
    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert "User 999 does not exist" in data.get("message")


def test_update_user(test_app, monkeypatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id):
        d = AttrDict()
        d.update({"id": 1, "email": "sarah@email.com", "username": "sarah"})
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return None

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(views, "update_user", mock_update_user)
    monkeypatch.setattr(views, "get_user_by_email", mock_get_user_by_email)
    client = test_app.test_client()
    response_1 = client.put(
        "/users/1",
        data=json.dumps({"username": "not_sarah", "email": "not_sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(response_1.data.decode())
    assert response_1.status_code == 200
    assert data.get("message") == "User 1 was updated!"
    resp_two = client.get("/users/1")
    data = json.loads(resp_two.data.decode())
    assert resp_two.status_code == 200
    assert data.get("username") == "sarah"
    assert data.get("email") == "sarah@email.com"


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
    test_app, monkeypatch, user_id, payload, status_code, message
):
    def mock_get_user_by_id(user_id):
        return None

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    client = test_app.test_client()
    resp = client.put(
        f"/users/{user_id}",
        data=json.dumps(payload),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == status_code
    assert message in data["message"]


def test_update_user_duplicate_email(test_app, monkeypatch):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    def mock_get_user_by_id(user_id):
        d = AttrDict()
        d.update({"id": 1, "username": "sarah", "email": "sarah@email.com"})
        return d

    def mock_update_user(user, username, email):
        return True

    def mock_get_user_by_email(email):
        return True

    monkeypatch.setattr(views, "get_user_by_id", mock_get_user_by_id)
    monkeypatch.setattr(views, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(views, "update_user", mock_update_user)
    client = test_app.test_client()
    resp = client.put(
        "/users/1",
        data=json.dumps({"username": "sarah", "email": "sarah@email.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 409
    assert "Sorry. That email already exists." in data["message"]
