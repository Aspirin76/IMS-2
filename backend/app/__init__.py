"""應用程式工廠。

架構 spine：分層架構 ＋ Transaction Script。
依賴方向 API → domain → persistence，禁止反向依賴。
"""

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate
from .domain.errors import DomainError


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.config.from_object(config_object)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "缺少 DATABASE_URL 環境變數。請設定，例如：\n"
            '  $env:DATABASE_URL = "postgresql+psycopg://postgres:<密碼>@localhost:5432/ailearn"\n'
            "（密碼只放環境變數，不要寫進任何檔案）"
        )

    db.init_app(app)
    migrate.init_app(app, db)

    # 僅開發期需要：Vite dev server (5173) 與 Flask (5000) 跨埠
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from .api import register_blueprints

    register_blueprints(app)

    from .cli import register_cli

    register_cli(app)

    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError):
        """領域錯誤 → 統一的錯誤形狀（AD-9）。"""
        return (
            jsonify({"error": {"code": error.code, "message": error.message, "details": error.details}}),
            error.status,
        )

    @app.errorhandler(404)
    def handle_404(_error):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "找不到這個資源", "details": {}}}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("未預期的錯誤")
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "伺服器發生未預期的錯誤，請重試",
                        "details": {},
                    }
                }
            ),
            500,
        )

    return app
