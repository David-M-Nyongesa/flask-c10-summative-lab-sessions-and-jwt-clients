from models import User


def signup(client, username, password="secret"):
    return client.post("/signup", json={
        "username": username,
        "password": password,
        "password_confirmation": password,
    })


def test_signup_logs_user_in(client):
    response = signup(client, "David")
    assert response.status_code == 201
    assert response.get_json()["username"] == "David"

    assert client.get("/check_session").status_code == 200


def test_signup_rejects_duplicate_username(client):
    signup(client, "David")
    response = signup(client, "David")
    assert response.status_code == 422


def test_password_is_hashed(client):
    signup(client, "David", "secret")
    user = User.query.filter_by(username="David").first()
    assert user._password_hash != "secret"
    assert user.authenticate("secret")


def test_login_and_logout(client):
    signup(client, "David", "secret")
    client.delete("/logout")
    assert client.get("/check_session").status_code == 401

    bad = client.post("/login", json={"username": "David", "password": "wrong"})
    assert bad.status_code == 401

    good = client.post("/login", json={"username": "David", "password": "secret"})
    assert good.status_code == 200


def test_notes_require_login(client):
    assert client.get("/notes").status_code == 401
    assert client.post("/notes", json={"title": "Hi", "content": "There"}).status_code == 401


def test_notes_crud(client):
    signup(client, "David")

    created = client.post("/notes", json={"title": "Groceries", "content": "Milk"})
    assert created.status_code == 201
    note_id = created.get_json()["id"]

    updated = client.patch(f"/notes/{note_id}", json={"title": "Shopping"})
    assert updated.status_code == 200
    assert updated.get_json()["title"] == "Shopping"

    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404


def test_notes_are_paginated(client):
    signup(client, "David")
    for i in range(12):
        client.post("/notes", json={"title": f"Note {i}", "content": "Text"})

    data = client.get("/notes?page=2&per_page=5").get_json()
    assert len(data["notes"]) == 5
    assert data["page"] == 2
    assert data["total"] == 12
    assert data["total_pages"] == 3


def test_users_cannot_touch_other_users_notes(client):
    signup(client, "David")
    note_id = client.post("/notes", json={"title": "Private", "content": "Secret"}).get_json()["id"]
    client.delete("/logout")

    signup(client, "guest")
    assert client.get("/notes").get_json()["total"] == 0
    assert client.get(f"/notes/{note_id}").status_code == 403
    assert client.patch(f"/notes/{note_id}", json={"title": "Hacked"}).status_code == 403
    assert client.delete(f"/notes/{note_id}").status_code == 403