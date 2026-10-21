"""initial schema

建立六張表：products、stock、salespersons、documents、document_items、stock_movements。
對應 PRD v0.4 附錄 D 與架構 spine 的 ERD；schema 的唯一來源是本遷移腳本（AD-11）。

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-21
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- 品項主檔（FR-1 ～ FR-3）---
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("safety_qty", sa.Integer(), nullable=True),
        # 補貨前置天數：品項層級（OQ-11 決議，預設 7 天）
        sa.Column("lead_time_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("idx_products_category", "products", ["category"], unique=False)

    # --- 庫存現量（FR-9；AD-1：只由領域服務層改寫）---
    op.create_table(
        "stock",
        sa.Column("product_id", sa.Integer(), primary_key=True),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
    )

    # --- 銷貨員（FR-22；v1 無密碼）---
    op.create_table(
        "salespersons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_salespersons_code", "salespersons", ["code"], unique=True)

    # --- 單據主檔（AD-3：數量變動只能來自單據）---
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("doc_type", sa.String(20), nullable=False),
        sa.Column("doc_no", sa.String(50), nullable=False),
        sa.Column("doc_date", sa.Date(), nullable=False),
        # 銷貨員歸屬：可為空 = 未歸屬（FR-23）
        sa.Column("salesperson_id", sa.Integer(), nullable=True),
        sa.Column("recorded_by", sa.String(50), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["salesperson_id"], ["salespersons.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_documents_doc_no", "documents", ["doc_no"], unique=True)
    op.create_index("idx_documents_doc_type_created", "documents", ["doc_type", "created_at"], unique=False)
    op.create_index("idx_documents_salesperson_created", "documents", ["salesperson_id", "created_at"], unique=False)

    # --- 單據明細 ---
    op.create_table(
        "document_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
    )
    op.create_index("idx_document_items_document", "document_items", ["document_id"], unique=False)
    op.create_index("idx_document_items_product", "document_items", ["product_id"], unique=False)

    # --- 庫存異動（AD-2：append-only）---
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("move_type", sa.String(10), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        # 套用本筆後的庫存現量，讓明細可重算（FR-14）
        sa.Column("balance_after", sa.Integer(), nullable=True),
        # 指向被更正的原始異動（FR-6）
        sa.Column("correction_of_movement_id", sa.Integer(), nullable=True),
        sa.Column("recorded_by", sa.String(50), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["correction_of_movement_id"], ["stock_movements.id"]),
    )
    op.create_index("idx_movements_product_type_date", "stock_movements", ["product_id", "move_type", "created_at"], unique=False)
    op.create_index("idx_movements_document", "stock_movements", ["document_id"], unique=False)
    op.create_index("idx_movements_created", "stock_movements", ["created_at"], unique=False)


def downgrade():
    op.drop_table("stock_movements")
    op.drop_table("document_items")
    op.drop_table("documents")
    op.drop_table("salespersons")
    op.drop_table("stock")
    op.drop_table("products")
