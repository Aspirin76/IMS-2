"""帳號與 session 的守門模組（AD-14）。

所有端點的權限判斷都必須走這裡，不得自行讀 session（AD-14 / AR-24）。
"""

from functools import wraps

from flask import jsonify, session

from .extensions import db
from .models.user import ROLE_ADMIN, ROLE_CLERK, ROLE_SALESPERSON, ROLE_VIEWER, User

SESSION_USER_KEY = "user_id"


def current_user() -> User | None:
    """取得目前登入者；未登入回 None。"""
    user_id = session.get(SESSION_USER_KEY)
    if user_id is None:
        return None
    user = db.session.get(User, user_id)
    if user is None or not user.is_active:
        session.pop(SESSION_USER_KEY, None)
        return None
    return user


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message, "details": {}}}), status


def login_required(view):
    """需要登入；未登入回 401（FR-30、NFR-10）。"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return _error("UNAUTHENTICATED", "請先登入", 401)
        return view(*args, **kwargs)

    return wrapped


def require_role(*roles: str):
    """需要指定角色；角色不符回 403（FR-30）。"""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            user = current_user()
            if user.role not in roles:
                return _error(
                    "FORBIDDEN",
                    f"你的角色（{user.role_label}）不能進行此操作",
                    403,
                )
            return view(*args, **kwargs)

        return wrapped

    return decorator


# 常用角色組合
CAN_READ = (ROLE_ADMIN, ROLE_CLERK, ROLE_SALESPERSON, ROLE_VIEWER)
CAN_WRITE_STOCK = (ROLE_ADMIN, ROLE_CLERK)
CAN_WRITE_DOCUMENT = (ROLE_ADMIN, ROLE_CLERK, ROLE_SALESPERSON)
ADMIN_ONLY = (ROLE_ADMIN,)
