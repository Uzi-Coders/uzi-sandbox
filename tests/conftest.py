import os
import pathlib
import sys
import uuid
from types import SimpleNamespace

os.environ.setdefault("SECRET_KEY", "test-only-secret-key")

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from database.db import db  # noqa: E402
from database.models import User  # noqa: E402

PASSWORD = "secret123"


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("data") / "test.sqlite3"
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///" + str(db_file),
    )
    with flask_app.app_context():
        db.create_all()
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    username = "user_" + uuid.uuid4().hex[:8]
    with app.app_context():
        u = User(username=username)
        u.set_password(PASSWORD)
        db.session.add(u)
        db.session.commit()
        data = SimpleNamespace(
            username=u.username, password=PASSWORD, api_key=u.api_key
        )
    return data


@pytest.fixture()
def api_headers(user):
    return {"X-API-Key": user.api_key}
