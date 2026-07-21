from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from ..decorators import admin_required
from ..extensions import db
from ..models import AdminLog, Product, Report, Transfer, User


bp = Blueprint("admin", __name__, url_prefix="/admin")


def log(action, target_type, target_id):
    db.session.add(AdminLog(admin_id=current_user.id, action=action, target_type=target_type, target_id=target_id))


@bp.get("")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        users=User.query.order_by(User.id).all(),
        products=Product.query.order_by(Product.id.desc()).all(),
        reports=Report.query.order_by(Report.created_at.desc()).all(),
        transfers=Transfer.query.order_by(Transfer.created_at.desc()).limit(30).all(),
    )


@bp.post("/users/<int:user_id>/toggle")
@admin_required
def toggle_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.is_admin:
        flash("관리자 계정 상태는 변경할 수 없습니다.", "danger")
    else:
        user.status = "suspended" if user.status == "active" else "active"
        log(f"user_{user.status}", "user", user.id)
        db.session.commit()
        flash("사용자 상태를 변경했습니다.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.post("/products/<int:product_id>/toggle")
@admin_required
def toggle_product(product_id):
    product = db.get_or_404(Product, product_id)
    product.is_hidden = not product.is_hidden
    log("product_hidden" if product.is_hidden else "product_restored", "product", product.id)
    db.session.commit()
    flash("상품 공개 상태를 변경했습니다.", "success")
    return redirect(url_for("admin.dashboard"))


@bp.post("/reports/<int:report_id>/<decision>")
@admin_required
def review_report(report_id, decision):
    if decision not in {"approved", "rejected"}:
        return ("", 400)
    report = db.get_or_404(Report, report_id)
    report.status = decision
    report.reviewed_by = current_user.id
    log(f"report_{decision}", "report", report.id)
    db.session.commit()
    flash("신고를 처리했습니다.", "success")
    return redirect(url_for("admin.dashboard"))
