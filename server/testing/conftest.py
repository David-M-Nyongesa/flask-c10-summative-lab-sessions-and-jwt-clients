import os

import pytest

# Use a throwaway in-memory database so tests never touch app.db
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

from app import app
from config import db


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def signup(client, username, password="secret"):
    return client.post("/signup", json={
        "username": username,
        "password": password,
        "password_confirmation": password,
    })
