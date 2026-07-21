from app.extensions import db
from app.models import Message, Product, Report
from tests.conftest import login


def test_private_message_visible_to_participants(client, app, users):
    login(client)
    response = client.post(f"/messages/{users['bob']}", data={"content": "안녕하세요"}, follow_redirects=True)
    assert "안녕하세요".encode() in response.data
    with app.app_context():
        assert Message.query.count() == 1


def test_duplicate_report_is_rejected(client, app, users):
    with app.app_context():
        product = Product(seller_id=users["bob"], title="의심 상품", description="설명", price=100)
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    login(client)
    data = {"target_type": "product", "target_id": product_id, "reason": "허위 판매로 의심됩니다."}
    client.post("/reports/new", data=data, follow_redirects=True)
    response = client.post("/reports/new", data=data, follow_redirects=True)
    assert "이미 신고한 대상".encode() in response.data
    with app.app_context():
        assert Report.query.count() == 1

