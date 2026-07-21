from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..decorators import active_required
from ..extensions import db
from ..forms import ProductForm
from ..models import Product


bp = Blueprint("products", __name__, url_prefix="/products")


def visible_or_404(product_id):
    product = db.get_or_404(Product, product_id)
    if product.is_hidden and not (current_user.is_authenticated and (current_user.is_admin or current_user.id == product.seller_id)):
        abort(404)
    return product


def require_owner(product):
    if product.seller_id != current_user.id and not current_user.is_admin:
        abort(403)


@bp.get("")
def list_products():
    query = request.args.get("q", "").strip()[:100]
    products = Product.query.filter_by(is_hidden=False)
    if query:
        escaped = query.replace("%", r"\%").replace("_", r"\_")
        pattern = f"%{escaped}%"
        products = products.filter(or_(Product.title.ilike(pattern, escape="\\"), Product.description.ilike(pattern, escape="\\")))
    products = products.order_by(Product.created_at.desc()).all()
    return render_template("products/list.html", products=products, query=query)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@active_required
def create():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            seller_id=current_user.id,
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            price=form.price.data,
            status=form.status.data,
        )
        db.session.add(product)
        db.session.commit()
        flash("상품을 등록했습니다.", "success")
        return redirect(url_for("products.detail", product_id=product.id))
    return render_template("products/form.html", form=form, heading="상품 등록")


@bp.get("/<int:product_id>")
def detail(product_id):
    return render_template("products/detail.html", product=visible_or_404(product_id))


@bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@active_required
def edit(product_id):
    product = db.get_or_404(Product, product_id)
    require_owner(product)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.title = form.title.data.strip()
        product.description = form.description.data.strip()
        product.price = form.price.data
        product.status = form.status.data
        db.session.commit()
        flash("상품을 수정했습니다.", "success")
        return redirect(url_for("products.detail", product_id=product.id))
    return render_template("products/form.html", form=form, heading="상품 수정")


@bp.post("/<int:product_id>/delete")
@login_required
@active_required
def delete(product_id):
    product = db.get_or_404(Product, product_id)
    require_owner(product)
    db.session.delete(product)
    db.session.commit()
    flash("상품을 삭제했습니다.", "success")
    return redirect(url_for("products.list_products"))

