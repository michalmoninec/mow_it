import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = os.getenv("APP_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Config(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///map.sqlite3"


class TestConfig(BaseConfig):
    """Testing configuration."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SESSION_PERMANENT = True
