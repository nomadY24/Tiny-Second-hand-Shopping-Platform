import os

import click
from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from config import Config
from .extensions import csrf, db, login_manager
from .models import User


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "로그인이 필요합니다."

    from .routes import admin, auth, main, messages, products, reports, transfers

    for blueprint in (main.bp, auth.bp, products.bp, messages.bp, reports.bp, transfers.bp, admin.bp):
        app.register_blueprint(blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_user():
        return {"viewer": current_user}

    @app.errorhandler(CSRFError)
    def handle_csrf(error):
        return render_template("errors/error.html", code=400, message="요청이 만료되었거나 유효하지 않습니다."), 400

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_error(error):
        code = getattr(error, "code", 500)
        messages = {400: "잘못된 요청입니다.", 401: "로그인이 필요합니다.", 403: "권한이 없습니다.", 404: "페이지를 찾을 수 없습니다.", 500: "서버 오류가 발생했습니다."}
        return render_template("errors/error.html", code=code, message=messages.get(code, messages[500])), code

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, password):
        username = username.strip()
        if len(username) < 3 or len(password) < 8:
            raise click.ClickException("아이디 3자, 비밀번호 8자 이상이어야 합니다.")
        if User.query.filter_by(username=username).first():
            raise click.ClickException("이미 존재하는 아이디입니다.")
        user = User(username=username, role="admin", balance=0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin '{username}' created.")

    with app.app_context():
        db.create_all()

    return app

