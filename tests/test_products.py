from app.extensions import db
from app.models import Product
from tests.conftest import login


def create_product(client, title="노트북", price="5000"):
    return client.post("/products/new", data={"title": title, "description": "정상 작동하는 중고 상품입니다.", "price": price, "status": "selling"}, follow_redirects=True)


def test_product_crud_and_search(client, app, users):
    login(client)
    response = create_product(client)
    assert "노트북".encode() in response.data
    with app.app_context():
        product = Product.query.one()
        product_id = product.id
    response = client.post(f"/products/{product_id}/edit", data={"title": "게이밍 노트북", "description": "수정된 설명", "price": "7000", "status": "reserved"}, follow_redirects=True)
    assert "게이밍 노트북".encode() in response.data
    response = client.get("/products?q=게이밍")
    assert "게이밍 노트북".encode() in response.data
    response = client.post(f"/products/{product_id}/delete", follow_redirects=True)
    assert "상품을 삭제했습니다".encode() in response.data


def test_negative_price_is_rejected(client, app, users):
    login(client)
    response = create_product(client, price="-1")
    assert response.status_code == 200
    with app.app_context():
        assert Product.query.count() == 0


def test_idor_owner_check_blocks_edit(client, app, users):
    with app.app_context():
        product = Product(seller_id=users["bob"], title="타인 상품", description="설명", price=100)
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    login(client)
    assert client.get(f"/products/{product_id}/edit").status_code == 403
    assert client.post(f"/products/{product_id}/delete").status_code == 403


def test_xss_payload_is_escaped(client, users):
    login(client)
    response = create_product(client, title="<script>alert(1)</script>")
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data
    assert b"<script>alert(1)</script>" not in response.data

