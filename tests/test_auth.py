from app.extensions import db
from app.models import User
from tests.conftest import login


def test_register_hashes_password(client, app):
    response = client.post("/auth/register", data={"username": "new_user", "password": "safePass123", "confirm": "safePass123"}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="new_user").one()
        assert user.password_hash != "safePass123"
        assert user.check_password("safePass123")


def test_duplicate_username_is_rejected(client, users):
    response = client.post("/auth/register", data={"username": "alice", "password": "safePass123", "confirm": "safePass123"})
    assert "이미 사용 중".encode() in response.data


def test_login_uses_generic_error(client, users):
    missing = client.post("/auth/login", data={"username": "nobody", "password": "wrongpass"}, follow_redirects=True)
    wrong = client.post("/auth/login", data={"username": "alice", "password": "wrongpass"}, follow_redirects=True)
    expected = "아이디 또는 비밀번호가 올바르지 않습니다.".encode()
    assert expected in missing.data and expected in wrong.data


def test_suspended_user_cannot_login(client, app, users):
    with app.app_context():
        user = db.session.get(User, users["alice"])
        user.status = "suspended"
        db.session.commit()
    response = login(client)
    assert "현재 이용할 수 없는 계정".encode() in response.data

