import os
import secrets

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_urlsafe(32)),
        SQLALCHEMY_DATABASE_URI="sqlite:///uposd.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        INITIAL_ADMIN_USERNAME=os.getenv("UPOSD_ADMIN_USER", "admin"),
        INITIAL_ADMIN_PASSWORD=os.getenv("UPOSD_ADMIN_PASSWORD", "admin123"),
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth_bp
    from .main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        from .models import User
        from .scan_service import seed_demo_data

        db.create_all()
        seed_demo_data()
        username = app.config["INITIAL_ADMIN_USERNAME"]
        password = app.config["INITIAL_ADMIN_PASSWORD"]
        if not User.query.filter_by(username=username).first():
            User.create_default_admin(username, password)
            app.logger.info(
                "Created initial admin user '%s'. Set UPOSD_ADMIN_PASSWORD to override the default.",
                username,
            )

    return app
