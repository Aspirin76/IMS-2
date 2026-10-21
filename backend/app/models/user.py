"""使用者帳號（PRD FR-22、FR-27 ～ FR-31；AD-15、AD-17）。

銷貨員與登入帳號是同一個實體：`role` 欄位區分 admin／clerk／salesperson／viewer。
密碼只存單向雜湊（AD-15）。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

ROLE_ADMIN = "admin"
ROLE_CLERK = "clerk"
ROLE_SALESPERSON = "salesperson"
ROLE_VIEWER = "viewer"
ROLES = (ROLE_ADMIN, ROLE_CLERK, ROLE_SALESPERSON, ROLE_VIEWER)

ROLE_LABELS = {
    ROLE_ADMIN: "管理員",
    ROLE_CLERK: "倉管",
    ROLE_SALESPERSON: "銷貨員",
    ROLE_VIEWER: "唯讀",
}

MIN_PASSWORD_LENGTH = 8


class User(db.Model):
    """登入帳號。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    # 單向雜湊（含隨機 salt），絕不存明文（AD-15 / NFR-10）
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=ROLE_CLERK)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    documents = relationship("Document", back_populates="salesperson")

    @property
    def role_label(self) -> str:
        return ROLE_LABELS.get(self.role, self.role)

    def to_dict(self) -> dict:
        """API 表示。不含 password_hash（AD-15）。"""
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "role_label": self.role_label,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
