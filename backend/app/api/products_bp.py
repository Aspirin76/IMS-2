"""品項 API（FR-1、FR-2、FR-3、AR-9）。

回應形狀（AD-9）：
  列表 → {items, total, page, page_size}
  單筆 → 資源物件
  錯誤 → {error: {code, message, details}}
"""

from flask import Blueprint, jsonify, request

from ..domain.errors import DomainError
from ..domain.product_service import create_product, deactivate_product, update_product
from ..extensions import db
from ..models import Product, StockMovement
from ..security import CAN_READ, CAN_WRITE_STOCK, login_required, require_role

products_bp = Blueprint("products", __name__)

PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 100


def _list_envelope(items, total, page, page_size):
    return jsonify({"items": items, "total": total, "page": page, "page_size": page_size})


@products_bp.get("/api/products")
@login_required
@require_role(*CAN_READ)
def list_products():
    """查詢與篩選品項（FR-2）。"""
    keyword = (request.args.get("keyword") or "").strip()
    category = (request.args.get("category") or "").strip()
    is_active = request.args.get("is_active")

    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", PAGE_SIZE_DEFAULT))
    except ValueError:
        raise DomainError("VALIDATION_ERROR", "page 與 page_size 必須是整數", status=400) from None
    if page < 1:
        raise DomainError("VALIDATION_ERROR", "page 必須 ≥ 1", {"field": "page"}, status=400)
    if page_size < 1 or page_size > PAGE_SIZE_MAX:
        raise DomainError(
            "VALIDATION_ERROR",
            f"page_size 必須介於 1 與 {PAGE_SIZE_MAX} 之間",
            {"field": "page_size"},
            status=400,
        )

    query = db.session.query(Product)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter((Product.sku.ilike(pattern)) | (Product.name.ilike(pattern)))
    if category:
        query = query.filter(Product.category == category)
    if is_active is not None and is_active != "":
        query = query.filter(Product.is_active == (is_active.lower() in ("1", "true", "yes")))

    total = query.count()
    products = (
        query.order_by(Product.id).offset((page - 1) * page_size).limit(page_size).all()
    )
    return _list_envelope([p.to_dict() for p in products], total, page, page_size)


@products_bp.post("/api/products")
@require_role(*CAN_WRITE_STOCK)
def post_product():
    """建立品項（FR-1）。"""
    payload = request.get_json(silent=True) or {}
    product = create_product(payload)
    response = jsonify(product.to_dict())
    response.status_code = 201
    response.headers["Location"] = f"/api/products/{product.id}"
    return response


@products_bp.get("/api/products/<int:product_id>")
@login_required
@require_role(*CAN_READ)
def get_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        raise DomainError("NOT_FOUND", f"找不到品項 #{product_id}", status=404)
    return jsonify(product.to_dict())


@products_bp.patch("/api/products/<int:product_id>")
@require_role(*CAN_WRITE_STOCK)
def patch_product(product_id: int):
    """修改品項（FR-3）。"""
    product = db.session.get(Product, product_id)
    if product is None:
        raise DomainError("NOT_FOUND", f"找不到品項 #{product_id}", status=404)
    payload = request.get_json(silent=True) or {}
    return jsonify(update_product(product, payload).to_dict())


@products_bp.delete("/api/products/<int:product_id>")
@require_role(*CAN_WRITE_STOCK)
def delete_product(product_id: int):
    """刪除品項：僅限未被引用的品項；已被引用者改用停用（FR-3）。"""
    product = db.session.get(Product, product_id)
    if product is None:
        raise DomainError("NOT_FOUND", f"找不到品項 #{product_id}", status=404)

    referenced = db.session.query(StockMovement).filter(
        StockMovement.product_id == product_id
    ).first()
    if referenced is not None:
        raise DomainError(
            "PRODUCT_IN_USE",
            "此品項已有庫存異動紀錄，請改用停用",
            {"field": "is_active"},
            status=409,
        )

    db.session.delete(product)
    db.session.commit()
    return "", 204
