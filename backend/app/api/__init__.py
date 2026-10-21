"""API 層：只做解析、驗證、序列化與錯誤轉換（AD-9）。"""

from flask import Flask

from .auth_bp import auth_bp
from .documents_bp import documents_bp
from .health_bp import health_bp
from .products_bp import products_bp
from .users_bp import users_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(documents_bp)
