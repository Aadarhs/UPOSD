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

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        ensure_seed_data()

    return app
