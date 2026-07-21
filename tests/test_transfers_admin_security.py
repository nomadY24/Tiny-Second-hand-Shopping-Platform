from app import create_app
from app.extensions import db
from app.models import Product, Transfer, User
from config import TestConfig
from tests.conftest import login


def transfer_data(key="a" * 32, receiver="bob_user", amount="1500", password="password123"):
    return {"receiver": receiver, "amount": amount, "password": password, "idempotency_key": key}


def test_transfer_is_atomic_and_recorded(client, app, users):
    login(client)
    response = client.post("/transfers/new", data=transfer_data(), follow_redirects=True)
    assert "송금이 완료".encode() in response.data
    with app.app_context():
        alice = db.session.get(User, users["alice"])
        bob = db.session.get(User, users["bob"])
        assert (alice.balance, bob.balance) == (8500, 11500)
        assert Transfer.query.count() == 1


def test_transfer_rejects_negative_excess_self_and_replay(client, app, users):
    login(client)
    assert client.post("/transfers/new", data=transfer_data(amount="-1")).status_code == 200
    assert client.post("/transfers/new", data=transfer_data(amount="999999")).status_code == 200
    assert client.post("/transfers/new", data=transfer_data(receiver="alice")).status_code == 200
    client.post("/transfers/new", data=transfer_data(key="b" * 32, amount="10"))
    response = client.post("/transfers/new", data=transfer_data(key="b" * 32, amount="10"))
    assert "이미 처리된 요청".encode() in response.data
    with app.app_context():
        assert Transfer.query.count() == 1


def test_non_admin_is_forbidden(client, users):
    login(client)
    assert client.get("/admin").status_code == 403


def test_admin_can_suspend_user_and_hide_product(client, app, users):
    with app.app_context():
        product = Product(seller_id=users["bob"], title="상품", description="설명", price=100)
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    login(client, "admin", "adminpass123")
    client.post(f"/admin/users/{users['bob']}/toggle")
    client.post(f"/admin/products/{product_id}/toggle")
    with app.app_context():
        assert db.session.get(User, users["bob"]).status == "suspended"
        assert db.session.get(Product, product_id).is_hidden is True


def test_csrf_rejects_post_without_token():
    class CsrfConfig(TestConfig):
        WTF_CSRF_ENABLED = True
    app = create_app(CsrfConfig)
    client = app.test_client()
    response = client.post("/auth/register", data={"username": "csrfuser", "password": "password123", "confirm": "password123"})
    assert response.status_code == 400
    assert "유효하지 않습니다".encode() in response.data
