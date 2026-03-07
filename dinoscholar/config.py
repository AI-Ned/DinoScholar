import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class DefaultConfig:
    SECRET_KEY = os.environ.get("DINOSCHOLAR_SECRET_KEY", os.urandom(32).hex())
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'dinoscholar.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, "data")


class TestingConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    DATA_DIR = os.path.join(BASE_DIR, "data")
