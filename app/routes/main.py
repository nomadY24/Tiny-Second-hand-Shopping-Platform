from flask import Blueprint, render_template

from ..models import Product


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    products = (
        Product.query.filter_by(is_hidden=False)
        .order_by(Product.created_at.desc())
        .limit(12)
        .all()
    )
    return render_template("index.html", products=products)

