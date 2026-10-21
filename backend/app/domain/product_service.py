"""品項主檔的領域規則（AD-7：業務規則在領域層驗證）。"""

from ..extensions import db
from ..models import Product, Stock
from .errors import DomainError

DEFAULT_LEAD_TIME_DAYS = 7


def _require_text(value: str | None, field: str, label: str) -> str:
    text = (value or "").strip()
    if not text:
        raise DomainError("VALIDATION_ERROR", f"{label}不能空白", {"field": field}, status=400)
    return text


def _to_int(value, field: str, label: str, default: int = 0) -> int:
    if value is None or value == "":
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise DomainError("VALIDATION_ERROR", f"{label}必須是整數", {"field": field}, status=400) from None
    if number < 0:
        raise DomainError("VALIDATION_ERROR", f"{label}不能是負數", {"field": field}, status=400)
    return number


def create_product(payload: dict) -> Product:
    """建立品項（FR-1）。sku 唯一；sku 與名稱必填；單價可為 0。"""
    sku = _require_text(payload.get("sku"), "sku", "sku")
    name = _require_text(payload.get("name"), "name", "名稱")

    existing = db.session.query(Product).filter(Product.sku == sku).one_or_none()
    if existing is not None:
        raise DomainError(
            "SKU_DUPLICATED",
            f"sku {sku} 已存在（{existing.name}），請改用其他 sku",
            {"field": "sku", "conflict_id": existing.id},
            status=409,
        )

    product = Product(
        sku=sku,
        name=name,
        category=(payload.get("category") or None),
        unit=payload.get("unit") or "個",
        price=_to_decimal(payload.get("price"), "price", "單價"),
        safety_qty=_to_int(payload.get("safety_qty"), "safety_qty", "安全庫存", 0),
        lead_time_days=_to_int(
            payload.get("lead_time_days"), "lead_time_days", "補貨前置天數", DEFAULT_LEAD_TIME_DAYS
        ),
        is_active=bool(payload.get("is_active", True)),
    )
    db.session.add(product)
    db.session.flush()  # 取用自增 id

    # 每個品項都有一筆庫存現量（初始 0，FR-9）
    db.session.add(Stock(product_id=product.id, qty=0))
    db.session.commit()
    return product


def update_product(product: Product, payload: dict) -> Product:
    """修改品項（FR-3）。sku 唯一性在有變更時才檢查。"""
    if "sku" in payload:
        sku = _require_text(payload.get("sku"), "sku", "sku")
        if sku != product.sku:
            existing = db.session.query(Product).filter(Product.sku == sku).one_or_none()
            if existing is not None:
                raise DomainError(
                    "SKU_DUPLICATED",
                    f"sku {sku} 已存在（{existing.name}），請改用其他 sku",
                    {"field": "sku", "conflict_id": existing.id},
                    status=409,
                )
            product.sku = sku

    if "name" in payload:
        product.name = _require_text(payload.get("name"), "name", "名稱")
    if "category" in payload:
        product.category = payload.get("category") or None
    if "unit" in payload:
        product.unit = payload.get("unit") or "個"
    if "price" in payload:
        product.price = _to_decimal(payload.get("price"), "price", "單價")
    if "safety_qty" in payload:
        product.safety_qty = _to_int(payload.get("safety_qty"), "safety_qty", "安全庫存", 0)
    if "lead_time_days" in payload:
        product.lead_time_days = _to_int(
            payload.get("lead_time_days"), "lead_time_days", "補貨前置天數", DEFAULT_LEAD_TIME_DAYS
        )
    if "is_active" in payload:
        product.is_active = bool(payload.get("is_active"))

    db.session.commit()
    return product


def deactivate_product(product: Product) -> Product:
    """停用品項（FR-3）。已被引用者不可刪除，只能停用。"""
    product.is_active = False
    db.session.commit()
    return product


def _to_decimal(value, field: str, label: str):
    from decimal import Decimal, InvalidOperation

    if value is None or value == "":
        return Decimal("0")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise DomainError("VALIDATION_ERROR", f"{label}格式不正確", {"field": field}, status=400) from None
