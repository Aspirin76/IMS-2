"""帳號管理（FR-29、FR-30；僅管理員）。"""

from flask import Blueprint, jsonify, request

from ..domain.auth_service import create_user, set_active, set_password, set_role
from ..domain.errors import DomainError
from ..extensions import db
from ..models.user import User
from ..security import ADMIN_ONLY, current_user, require_role

users_bp = Blueprint("users", __name__)


@users_bp.post("/api/users")
@require_role(*ADMIN_ONLY)
def post_user():
    """建立帳號。"""
    payload = request.get_json(silent=True) or {}
    user = create_user(
        username=payload.get("username", ""),
        display_name=payload.get("display_name", ""),
        password=payload.get("password", ""),
        role=payload.get("role", "clerk"),
    )
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers["Location"] = f"/api/users/{user.id}"
    return response


@users_bp.patch("/api/users/<int:user_id>")
@require_role(*ADMIN_ONLY)
def patch_user(user_id: int):
    """調整角色、啟用／停用、重設密碼。"""
    user = db.session.get(User, user_id)
    if user is None:
        raise DomainError("NOT_FOUND", f"找不到帳號 #{user_id}", status=404)

    payload = request.get_json(silent=True) or {}
    actor = current_user()

    # 不讓管理員把自己鎖死（FR-29）
    if user.id == actor.id:
        if "role" in payload and payload["role"] != user.role:
            raise DomainError(
                "SELF_LOCKOUT",
                "不能變更自己的角色，以免把系統鎖死",
                {"field": "role"},
                status=409,
            )
        if "is_active" in payload and not payload["is_active"]:
            raise DomainError(
                "SELF_LOCKOUT",
                "不能停用自己的帳號，以免把系統鎖死",
                {"field": "is_active"},
                status=409,
            )

    if "role" in payload:
        set_role(user, payload["role"])
    if "is_active" in payload:
        set_active(user, bool(payload["is_active"]))
    if payload.get("password"):
        set_password(user, payload["password"])

    return jsonify(user.to_dict())


@users_bp.get("/api/users/<int:user_id>")
@require_role(*ADMIN_ONLY)
def get_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        raise DomainError("NOT_FOUND", f"找不到帳號 #{user_id}", status=404)
    return jsonify(user.to_dict())
