import pytest

from app import create_app
from app.extensions import db
from app.models import User
from config import TestConfig


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def users(app):
    with app.app_context():
        alice = User(username="alice", balance=10000)
        alice.set_password("password123")
        bob = User(username="bob_user", balance=10000)
        bob.set_password("password123")
        admin = User(username="admin", role="admin", balance=0)
        admin.set_password("adminpass123")
        db.session.add_all([alice, bob, admin])
        db.session.commit()
        return {"alice": alice.id, "bob": bob.id, "admin": admin.id}


def login(client, username="alice", password="password123"):
    return client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=True)

