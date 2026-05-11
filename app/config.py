import os


class Config:
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///uposd.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
