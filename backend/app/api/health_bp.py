"""健康檢查端點（Story 1.1 AC）。"""

from flask import Blueprint, jsonify

from ..extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        database = "ok"
    except Exception:  # noqa: BLE001 - 健康檢查不應因連線失敗而 500
        database = "error"
    status = 200 if database == "ok" else 503
    return jsonify({"status": "ok" if database == "ok" else "degraded", "database": database}), status
