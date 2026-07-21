import secrets

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from ..decorators import active_required
from ..extensions import db
from ..forms import TransferForm
from ..models import Transfer, User


bp = Blueprint("transfers", __name__, url_prefix="/transfers")


@bp.route("/new", methods=["GET", "POST"])
@login_required
@active_required
def create():
    form = TransferForm()
    if form.validate_on_submit():
        receiver = User.query.filter_by(username=form.receiver.data.strip()).first()
        if not current_user.check_password(form.password.data):
            form.password.errors.append("비밀번호가 올바르지 않습니다.")
        elif not receiver or receiver.status != "active":
            form.receiver.errors.append("송금 가능한 사용자를 찾을 수 없습니다.")
        elif receiver.id == current_user.id:
            form.receiver.errors.append("자기 자신에게 송금할 수 없습니다.")
        elif form.amount.data > current_user.balance:
            form.amount.errors.append("잔액이 부족합니다.")
        elif Transfer.query.filter_by(idempotency_key=form.idempotency_key.data).first():
            form.amount.errors.append("이미 처리된 요청입니다.")
        else:
            current_user.balance -= form.amount.data
            receiver.balance += form.amount.data
            db.session.add(Transfer(sender_id=current_user.id, receiver_id=receiver.id, amount=form.amount.data, idempotency_key=form.idempotency_key.data))
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.amount.errors.append("이미 처리된 요청입니다.")
            else:
                flash("송금이 완료되었습니다.", "success")
                return redirect(url_for("transfers.history"))
    if not form.idempotency_key.data:
        form.idempotency_key.data = secrets.token_hex(16)
    return render_template("transfers/form.html", form=form)


@bp.get("")
@login_required
def history():
    rows = Transfer.query.filter((Transfer.sender_id == current_user.id) | (Transfer.receiver_id == current_user.id)).order_by(Transfer.created_at.desc()).all()
    return render_template("transfers/history.html", transfers=rows)

