"""登入 / 登出 / 目前使用者（FR-28）。"""

from flask import Blueprint, jsonify, request, session

from ..domain.auth_service import authenticate
from ..extensions import db
from ..models.user import User
from ..security import SESSION_USER_KEY, current_user, login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/auth/login")
def login():
    """登入。密碼錯誤一律回「帳號或密碼錯誤」（NFR-10）。"""
    payload = request.get_json(silent=True) or {}
    user = authenticate(payload.get("username", ""), payload.get("password", ""))
    session.clear()
    session[SESSION_USER_KEY] = user.id
    session.permanent = True
    return jsonify({"user": user.to_dict()})


@auth_bp.post("/api/auth/logout")
def logout():
    """登出。"""
    session.clear()
    return jsonify({"status": "ok"})


@auth_bp.get("/api/auth/me")
@login_required
def me():
    """取得目前登入者。"""
    return jsonify({"user": current_user().to_dict()})


@auth_bp.get("/api/users")
@login_required
def list_users():
    """帳號清單（登入者皆可查看，管理員用於管理）。"""
    users = db.session.query(User).order_by(User.id).all()
    return jsonify(
        {
            "items": [u.to_dict() for u in users],
            "total": len(users),
            "page": 1,
            "page_size": len(users) or 1,
        }
    )
