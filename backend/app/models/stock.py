"""庫存現量（PRD FR-9、附錄 D）。

AD-1：此表的 `qty` 只能由領域服務層改變，任何直接 UPDATE 都視為違規。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Stock(db.Model):
    """某品項目前的庫存現量，與 products 一對一。"""

    __tablename__ = "stock"

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    product = relationship("Product", back_populates="stock")
