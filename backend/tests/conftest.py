"""pytest 共用設定。

測試需要資料庫時，請設定 TEST_DATABASE_URL 指向一個測試庫（不要用正式的 ailearn）。
"""

import os

import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture()
def app():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("需要 TEST_DATABASE_URL 才能執行資料庫測試")

    class _TestConfig(TestConfig):
        SQLALCHEMY_DATABASE_URI = url

    application = create_app(_TestConfig)
    with application.app_context():
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
