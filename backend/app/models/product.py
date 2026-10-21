"""品項主檔的資料模型（PRD FR-1 ～ FR-3、附錄 D）。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Product(db.Model):
    """品項：可被管理的商品主檔（AD-13：統一用 products / 品項）。"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str | None] = mapped_column(String(20), default="個")
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    safety_qty: Mapped[int] = mapped_column(Integer, default=0)
    # 補貨前置天數：品項層級（OQ-11 決議，預設 7 天）
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    stock = relationship(
        "Stock",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    movements = relationship("StockMovement", back_populates="product", passive_deletes=True)
    document_items = relationship(
        "DocumentItem", back_populates="product", passive_deletes=True
    )

    def to_dict(self) -> dict:
        """API 表示。金額以字串回傳，避免浮點誤差（AD-10）。"""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "price": f"{self.price:.2f}" if self.price is not None else "0.00",
            "safety_qty": self.safety_qty,
            "lead_time_days": self.lead_time_days,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
