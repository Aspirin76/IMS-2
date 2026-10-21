"""庫存領域服務：單據 → 異動 → 庫存現量（AD-1、AD-2、AD-3、AD-4、AD-16）。

這是**唯一**可以改寫 `stock.qty` 的地方。任何端點都不得直接 UPDATE 庫存現量。
"""

from datetime import date, datetime, timezone

from sqlalchemy import select

from ..extensions import db
from ..models.document import DOC_TYPE_IN, DOC_TYPE_OUT, DOC_TYPE_STOCKTAKE, Document, DocumentItem
from ..models.movement import MOVE_TYPE_IN, StockMovement
from ..models.product import Product
from ..models.stock import Stock
from ..models.user import User
from .errors import DomainError

MAX_ITEMS_PER_DOCUMENT = 100


def _next_doc_no(doc_type: str, doc_date: date) -> str:
    """產生單號：IN-20261021-001。"""
    prefix = f"{doc_type}-{doc_date.strftime('%Y%m%d')}"
    existing = (
        db.session.query(Document)
        .filter(Document.doc_no.like(f"{prefix}-%"))
        .count()
    )
    return f"{prefix}-{existing + 1:03d}"


def _merge_items(items: list[dict]) -> list[dict]:
    """同一品項多列 → 合併為一列（數量相加、單價取第一列非零值）。"""
    merged: dict[int, dict] = {}
    order: list[int] = []
    for raw in items:
        product_id = raw.get("product_id")
        if product_id is None:
            raise DomainError("VALIDATION_ERROR", "每一列都要選品項", {"field": "items"}, status=400)
        product_id = int(product_id)
        qty = _positive_int(raw.get("qty"), "數量")
        unit_price = _non_negative_decimal(raw.get("unit_price"), "單價")
        note = (raw.get("note") or "").strip() or None

        if product_id not in merged:
            merged[product_id] = {
                "product_id": product_id,
                "qty": qty,
                "unit_price": unit_price,
                "note": note,
            }
            order.append(product_id)
        else:
            merged[product_id]["qty"] += qty
            if merged[product_id]["unit_price"] == 0 and unit_price > 0:
                merged[product_id]["unit_price"] = unit_price
    return [merged[pid] for pid in order]


def _positive_int(value, label: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise DomainError(
            "VALIDATION_ERROR", f"{label}必須是整數", {"field": label}, status=400
        ) from None
    if number <= 0:
        raise DomainError(
            "VALIDATION_ERROR", f"{label}必須大於 0", {"field": label}, status=400
        )
    return number


def _non_negative_decimal(value, label: str):
    from decimal import Decimal, InvalidOperation

    if value is None or value == "":
        return Decimal("0")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise DomainError(
            "VALIDATION_ERROR", f"{label}格式不正確", {"field": label}, status=400
        ) from None
    if number < 0:
        raise DomainError(
            "VALIDATION_ERROR", f"{label}不能是負數", {"field": label}, status=400
        )
    return number


def _parse_date(value) -> date:
    if not value:
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise DomainError(
            "VALIDATION_ERROR", "日期格式不正確（應為 YYYY-MM-DD）", {"field": "doc_date"}, status=400
        ) from None


def _get_or_create_stock(product_id: int) -> Stock:
    """取得品項的庫存現量列；不存在就建立（qty=0）。同時鎖住列避免併發覆寫。"""
    stock = db.session.execute(
        select(Stock).where(Stock.product_id == product_id).with_for_update()
    ).scalar_one_or_none()
    if stock is None:
        stock = Stock(product_id=product_id, qty=0)
        db.session.add(stock)
        db.session.flush()
    return stock


def create_stock_in(actor: User, payload: dict) -> dict:
    """建立並送出入庫單（FR-4）。

    整張單據在同一個交易內完成：documents → document_items → stock_movements → stock.qty（AD-4）。
    記錄者一律取自登入身分（AD-16）。
    """
    doc_date = _parse_date(payload.get("doc_date"))
    doc_no = (payload.get("doc_no") or "").strip() or _next_doc_no("IN", doc_date)
    if db.session.query(Document).filter(Document.doc_no == doc_no).one_or_none():
        raise DomainError(
            "DOC_NO_DUPLICATED",
            f"單號 {doc_no} 已存在，請換一個",
            {"field": "doc_no"},
            status=409,
        )

    raw_items = payload.get("items") or []
    if not raw_items:
        raise DomainError("VALIDATION_ERROR", "至少要有一列明細", {"field": "items"}, status=400)
    if len(raw_items) > MAX_ITEMS_PER_DOCUMENT:
        raise DomainError(
            "VALIDATION_ERROR",
            f"單張單據最多 {MAX_ITEMS_PER_DOCUMENT} 個品項",
            {"field": "items"},
            status=400,
        )

    items = _merge_items(raw_items)

    # 檢查品項存在且未停用
    for item in items:
        product = db.session.get(Product, item["product_id"])
        if product is None:
            raise DomainError(
                "PRODUCT_NOT_FOUND",
                f"找不到品項 #{item['product_id']}",
                {"field": "items", "product_id": item["product_id"]},
                status=400,
            )
        if not product.is_active:
            raise DomainError(
                "PRODUCT_INACTIVE",
                f"品項「{product.name}」已停用，不能登記入庫",
                {"field": "items", "product_id": product.id},
                status=400,
            )

    document = Document(
        doc_type=DOC_TYPE_IN,
        doc_no=doc_no,
        doc_date=doc_date,
        # 記錄者一律取自登入身分，忽略前端傳入（AD-16）
        recorded_by=actor.username,
        note=(payload.get("note") or "").strip() or None,
    )
    db.session.add(document)
    db.session.flush()

    changes = []
    for item in items:
        product = db.session.get(Product, item["product_id"])
        db.session.add(
            DocumentItem(
                document_id=document.id,
                product_id=product.id,
                qty=item["qty"],
                unit_price=item["unit_price"],
                note=item["note"],
            )
        )

        stock = _get_or_create_stock(product.id)
        before = stock.qty
        stock.qty = before + item["qty"]
        stock.updated_at = datetime.now(timezone.utc)

        db.session.add(
            StockMovement(
                product_id=product.id,
                document_id=document.id,
                move_type=MOVE_TYPE_IN,
                qty=item["qty"],
                balance_after=stock.qty,
                recorded_by=actor.username,
                note=item["note"],
            )
        )
        changes.append(
            {
                "sku": product.sku,
                "name": product.name,
                "before": before,
                "after": stock.qty,
                "qty": item["qty"],
            }
        )

    db.session.commit()

    return {
        "document": {
            "id": document.id,
            "doc_no": document.doc_no,
            "doc_type": document.doc_type,
            "doc_date": document.doc_date.isoformat(),
            "recorded_by": document.recorded_by,
            "note": document.note,
            "items": [
                {
                    "product_id": item.product_id,
                    "sku": product.sku,
                    "name": product.name,
                    "qty": item.qty,
                    "unit_price": f"{item.unit_price:.2f}",
                    "amount": f"{item.qty * float(item.unit_price):.2f}",
                }
                for item, product in _items_with_products(document)
            ],
        },
        "changes": changes,
    }


def _items_with_products(document: Document):
    items = (
        db.session.query(DocumentItem)
        .filter(DocumentItem.document_id == document.id)
        .order_by(DocumentItem.id)
        .all()
    )
    for item in items:
        yield item, db.session.get(Product, item.product_id)


def list_documents(doc_type: str | None, product_id: int | None, keyword: str | None,
                   date_from: str | None, date_to: str | None,
                   page: int = 1, page_size: int = 50) -> dict:
    """查詢單據（FR-5、FR-8）。"""
    query = db.session.query(Document)
    if doc_type:
        query = query.filter(Document.doc_type == doc_type)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(Document.doc_no.ilike(pattern))
    if date_from:
        query = query.filter(Document.doc_date >= _parse_date(date_from))
    if date_to:
        query = query.filter(Document.doc_date <= _parse_date(date_to))
    if product_id:
        query = query.join(DocumentItem).filter(DocumentItem.product_id == product_id)

    total = query.count()
    documents = (
        query.order_by(Document.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )

    items = []
    for document in documents:
        doc_items = (
            db.session.query(DocumentItem)
            .filter(DocumentItem.document_id == document.id)
            .order_by(DocumentItem.id)
            .all()
        )
        total_qty = sum(i.qty for i in doc_items)
        total_amount = sum(float(i.unit_price) * i.qty for i in doc_items)
        items.append(
            {
                "id": document.id,
                "doc_no": document.doc_no,
                "doc_type": document.doc_type,
                "doc_date": document.doc_date.isoformat(),
                "recorded_by": document.recorded_by,
                "note": document.note,
                "total_qty": total_qty,
                "total_amount": f"{total_amount:.2f}",
                "items": [
                    {
                        "product_id": i.product_id,
                        "qty": i.qty,
                        "unit_price": f"{i.unit_price:.2f}",
                        "amount": f"{i.qty * float(i.unit_price):.2f}",
                    }
                    for i in doc_items
                ],
            }
        )

    return {"items": items, "total": total, "page": page, "page_size": page_size}
