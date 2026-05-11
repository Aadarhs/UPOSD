import os
import secrets
from pathlib import Path

from flask import Flask

from .blueprints.api.routes import api_bp
from .blueprints.auth.routes import auth_bp
from .blueprints.main.routes import main_bp
from .config import Config
from .extensions import db, login_manager
from .sample_data import ensure_seed_data


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    os.makedirs(app.instance_path, exist_ok=True)
    secret_key = app.config.get("SECRET_KEY")
    if not secret_key:
        if app.config.get("FLASK_ENV") == "production":
            raise RuntimeError("SECRET_KEY must be set when FLASK_ENV=production.")
        secret_file = Path(app.instance_path) / ".secret_key"
        if secret_file.exists():
            secret_key = secret_file.read_text(encoding="utf-8").strip()
        else:
            secret_key = secrets.token_hex(32)
            secret_file.write_text(secret_key, encoding="utf-8")
        app.config["SECRET_KEY"] = secret_key

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        ensure_seed_data()

    return app
