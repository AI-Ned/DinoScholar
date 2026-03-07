import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_secret_key():
    """Return a stable secret key.

    On PythonAnywhere (or any server) set the DINOSCHOLAR_SECRET_KEY
    environment variable.  If it is not set, a key is generated once and
    written to a local file so that it survives process restarts and
    keeps sessions valid.
    """
    key = os.environ.get("DINOSCHOLAR_SECRET_KEY")
    if key:
        return key
    key_file = os.path.join(BASE_DIR, ".secret_key")
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            return f.read().strip()
    key = os.urandom(32).hex()
    with open(key_file, "w") as f:
        f.write(key)
    return key


class DefaultConfig:
    SECRET_KEY = _get_secret_key()
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(BASE_DIR, 'dinoscholar.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, "data")


class TestingConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    DATA_DIR = os.path.join(BASE_DIR, "data")
