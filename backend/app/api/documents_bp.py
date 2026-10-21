"""單據 API：入庫單（FR-4、FR-5）與共用查詢（FR-5、FR-8）。

AD-4：整張單據在同一個交易內完成；失敗整批 rollback。
AD-16：記錄者取自登入身分。
"""

from flask import Blueprint, jsonify, request

from ..domain.errors import DomainError
from ..domain.stock_service import create_stock_in, list_documents
from ..extensions import db
from ..models.document import Document
from ..security import CAN_READ, CAN_WRITE_STOCK, current_user, login_required, require_role

documents_bp = Blueprint("documents", __name__)


@documents_bp.post("/api/documents/stock-in")
@require_role(*CAN_WRITE_STOCK)
def post_stock_in():
    """建立並送出入庫單（FR-4）。"""
    payload = request.get_json(silent=True) or {}
    try:
        result = create_stock_in(current_user(), payload)
    except Exception:
        db.session.rollback()  # 整批 rollback（AD-4）
        raise
    response = jsonify(result)
    response.status_code = 201
    response.headers["Location"] = f"/api/documents/{result['document']['id']}"
    return response


@documents_bp.get("/api/documents")
@login_required
@require_role(*CAN_READ)
def get_documents():
    """查詢單據（FR-5、FR-8）。"""
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 50))
    except ValueError:
        raise DomainError("VALIDATION_ERROR", "page 與 page_size 必須是整數", status=400) from None
    if page < 1 or page_size < 1 or page_size > 100:
        raise DomainError("VALIDATION_ERROR", "分頁參數超出範圍", status=400)

    product_id = request.args.get("product_id")
    result = list_documents(
        doc_type=request.args.get("type") or None,
        product_id=int(product_id) if product_id else None,
        keyword=request.args.get("keyword") or None,
        date_from=request.args.get("from") or None,
        date_to=request.args.get("to") or None,
        page=page,
        page_size=page_size,
    )
    return jsonify(result)


@documents_bp.get("/api/documents/<int:document_id>")
@login_required
@require_role(*CAN_READ)
def get_document(document_id: int):
    """單據明細（可反查原單據）。"""
    document = db.session.get(Document, document_id)
    if document is None:
        raise DomainError("NOT_FOUND", f"找不到單據 #{document_id}", status=404)
    return jsonify(
        {
            "id": document.id,
            "doc_no": document.doc_no,
            "doc_type": document.doc_type,
            "doc_date": document.doc_date.isoformat(),
            "recorded_by": document.recorded_by,
            "note": document.note,
        }
    )
