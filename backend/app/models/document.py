"""單據主檔（入庫單 / 出庫單 / 盤點單）與明細（PRD 附錄 D）。

AD-3：數量變動只能來自單據流程，異動必須帶 document_id。
AD-17：銷貨員歸屬指向 users 表（登入帳號）。
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db

DOC_TYPE_IN = "IN"
DOC_TYPE_OUT = "OUT"
DOC_TYPE_STOCKTAKE = "STOCKTAKE"
DOC_TYPES = (DOC_TYPE_IN, DOC_TYPE_OUT, DOC_TYPE_STOCKTAKE)


class Document(db.Model):
    """單據：一張具唯一單號的作業憑證。"""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doc_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    doc_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    doc_date: Mapped[date] = mapped_column(Date, nullable=False)
    # 銷貨員歸屬：指向 users.id，可為空 = 未歸屬（FR-23、AD-17）
    salesperson_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    recorded_by: Mapped[str | None] = mapped_column(String(50))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items = relationship("DocumentItem", back_populates="document")
    salesperson = relationship("User", back_populates="documents")
    movements = relationship("StockMovement", back_populates="document")


class DocumentItem(db.Model):
    """單據明細：一列一個品項。"""

    __tablename__ = "document_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    note: Mapped[str | None] = mapped_column(Text)

    document = relationship("Document", back_populates="items")
    product = relationship("Product", back_populates="document_items")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "sku": self.product.sku if self.product else None,
            "qty": self.qty,
            "unit_price": f"{self.unit_price:.2f}",
            "amount": f"{self.qty * float(self.unit_price):.2f}",
            "note": self.note,
        }
