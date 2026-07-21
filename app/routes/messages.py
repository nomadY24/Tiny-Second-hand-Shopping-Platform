from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from ..decorators import active_required
from ..extensions import db
from ..forms import MessageForm
from ..models import Message, User


bp = Blueprint("messages", __name__, url_prefix="/messages")


@bp.get("")
@login_required
def inbox():
    rows = Message.query.filter(or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)).order_by(Message.created_at.desc()).all()
    partners = []
    seen = set()
    for message in rows:
        partner = message.receiver if message.sender_id == current_user.id else message.sender
        if partner.id not in seen:
            partners.append((partner, message))
            seen.add(partner.id)
    return render_template("messages/inbox.html", partners=partners)


@bp.route("/<int:user_id>", methods=["GET", "POST"])
@login_required
@active_required
def conversation(user_id):
    other = db.get_or_404(User, user_id)
    if other.id == current_user.id:
        abort(400)
    form = MessageForm()
    if form.validate_on_submit():
        if other.status != "active":
            abort(403)
        db.session.add(Message(sender_id=current_user.id, receiver_id=other.id, content=form.content.data.strip()))
        db.session.commit()
        flash("메시지를 보냈습니다.", "success")
        return redirect(url_for("messages.conversation", user_id=other.id))
    rows = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other.id),
            and_(Message.sender_id == other.id, Message.receiver_id == current_user.id),
        )
    ).order_by(Message.created_at.asc()).all()
    return render_template("messages/conversation.html", other=other, messages=rows, form=form)

