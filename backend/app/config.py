"""集中讀取設定。只從環境變數取值，不從檔案讀取任何機密（AD-8）。"""

import os
import secrets
from datetime import timedelta


def _secret_key() -> str:
    """Session 簽章金鑰。

    優先取環境變數 APP_SECRET_KEY；未設定時產生一次性的隨機金鑰
    （此時重開程式會需要重新登入，但不會有任何金鑰落到檔案）。
    """
    key = os.environ.get("APP_SECRET_KEY")
    if key:
        return key
    import warnings

    warnings.warn(
        "未設定 APP_SECRET_KEY，將使用一次性隨機金鑰（重啟後需重新登入）。",
        RuntimeWarning,
        stacklevel=2,
    )
    return secrets.token_hex(32)


class Config:
    """基礎設定。

    `DATABASE_URL` 必須由環境變數注入，例如：
        postgresql+psycopg://postgres:<密碼>@localhost:5432/ailearn
    密碼不得寫入任何檔案、原始碼或版控（AD-8 / NFR-2）。
    """

    SECRET_KEY = _secret_key()

    # Session 設定（AD-14、NFR-10）
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    # 單據送出時，允許的單一單據最大品項數（NFR-3）
    MAX_ITEMS_PER_DOCUMENT = 100


class TestConfig(Config):
    TESTING = True
