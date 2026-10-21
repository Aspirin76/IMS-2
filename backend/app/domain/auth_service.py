"""帳號領域規則（AD-15、AD-17）。

- 密碼只存單向雜湊（werkzeug）。
- 登入失敗一律回「帳號或密碼錯誤」，不透露帳號是否存在（NFR-10）。
"""

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models.user import MIN_PASSWORD_LENGTH, ROLES, ROLE_LABELS, User
from .errors import DomainError

INVALID_CREDENTIALS = "帳號或密碼錯誤"


def hash_password(raw: str) -> str:
    """產生單向雜湊（AD-15）。"""
    return generate_password_hash(raw)


def verify_password(password_hash: str, raw: str) -> bool:
    return check_password_hash(password_hash, raw)


def validate_password(raw: str) -> str:
    """密碼政策：至少 8 碼（NFR-10）。"""
    if not raw or len(raw) < MIN_PASSWORD_LENGTH:
        raise DomainError(
            "WEAK_PASSWORD",
            f"密碼至少 {MIN_PASSWORD_LENGTH} 碼",
            {"field": "password"},
            status=400,
        )
    return raw


def validate_role(role: str) -> str:
    if role not in ROLES:
        raise DomainError(
            "INVALID_ROLE",
            f"角色必須是：{'、'.join(ROLE_LABELS[r] for r in ROLES)}",
            {"field": "role"},
            status=400,
        )
    return role


def authenticate(username: str, password: str) -> User:
    """驗證帳密；失敗拋 DomainError（401）。"""
    user = db.session.query(User).filter(User.username == (username or "").strip()).one_or_none()
    if user is None or not verify_password(user.password_hash, password or ""):
        raise DomainError("INVALID_CREDENTIALS", INVALID_CREDENTIALS, status=401)
    if not user.is_active:
        raise DomainError("ACCOUNT_DISABLED", "此帳號已停用，請聯絡管理員", status=403)
    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()
    return user


def create_user(
    username: str,
    display_name: str,
    password: str,
    role: str = "clerk",
    is_active: bool = True,
) -> User:
    """建立帳號（FR-29）。"""
    username = (username or "").strip()
    display_name = (display_name or "").strip()
    if not username:
        raise DomainError("VALIDATION_ERROR", "帳號不能空白", {"field": "username"}, status=400)
    if not display_name:
        raise DomainError(
            "VALIDATION_ERROR", "姓名不能空白", {"field": "display_name"}, status=400
        )

    existing = db.session.query(User).filter(User.username == username).one_or_none()
    if existing is not None:
        raise DomainError(
            "USERNAME_DUPLICATED",
            f"帳號 {username} 已存在（{existing.display_name}）",
            {"field": "username"},
            status=409,
        )

    validate_password(password)
    validate_role(role)

    user = User(
        username=username,
        display_name=display_name,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.session.add(user)
    db.session.commit()
    return user


def set_password(user: User, new_password: str) -> User:
    """設定新密碼（FR-29、NFR-10）。"""
    validate_password(new_password)
    user.password_hash = hash_password(new_password)
    db.session.commit()
    return user


def set_role(user: User, role: str) -> User:
    validate_role(role)
    user.role = role
    db.session.commit()
    return user


def set_active(user: User, is_active: bool) -> User:
    user.is_active = is_active
    db.session.commit()
    return user
