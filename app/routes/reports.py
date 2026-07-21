from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from ..decorators import active_required
from ..extensions import db
from ..forms import ReportForm
from ..models import Product, Report, User


bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.route("/new", methods=["GET", "POST"])
@login_required
@active_required
def create():
    form = ReportForm()
    if form.validate_on_submit():
        target = db.session.get(User if form.target_type.data == "user" else Product, form.target_id.data)
        if not target:
            form.target_id.errors.append("대상을 찾을 수 없습니다.")
        elif form.target_type.data == "user" and target.id == current_user.id:
            form.target_id.errors.append("자기 자신은 신고할 수 없습니다.")
        else:
            report = Report(reporter_id=current_user.id, target_type=form.target_type.data, target_id=form.target_id.data, reason=form.reason.data.strip())
            db.session.add(report)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.target_id.errors.append("이미 신고한 대상입니다.")
            else:
                flash("신고가 접수되었습니다.", "success")
                return redirect(url_for("main.index"))
    return render_template("reports/form.html", form=form)

