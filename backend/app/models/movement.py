"""庫存異動（PRD FR-14、FR-15、附錄 D）。

AD-2：append-only，只允許 INSERT。更正以反向異動 + correction_of_movement_id 表達。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

MOVE_TYPE_IN = "IN"
MOVE_TYPE_OUT = "OUT"
MOVE_TYPE_ADJUST = "ADJUST"
MOVE_TYPES = (MOVE_TYPE_IN, MOVE_TYPE_OUT, MOVE_TYPE_ADJUST)


class StockMovement(db.Model):
    """一筆不可分割的數量變動紀錄。"""

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True
    )
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"), index=True
    )
    move_type: Mapped[str] = mapped_column(String(10), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    # 套用本筆後的庫存現量，讓明細可重算（FR-14）
    balance_after: Mapped[int | None] = mapped_column(Integer)
    # 指向被更正的原始異動（FR-6 / AD-2）
    correction_of_movement_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_movements.id")
    )
    recorded_by: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    product = relationship("Product", back_populates="movements")
    document = relationship("Document", back_populates="movements")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "document_id": self.document_id,
            "doc_no": self.document.doc_no if self.document else None,
            "move_type": self.move_type,
            "qty": self.qty,
            "balance_after": self.balance_after,
            "correction_of_movement_id": self.correction_of_movement_id,
            "recorded_by": self.recorded_by,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
