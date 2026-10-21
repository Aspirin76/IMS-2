"""user accounts（v0.5：使用者登入與角色權限）

- 建立 users 表（AD-17：取代 salespersons 表）
- 既有 salespersons 的資料遷移為 role='salesperson' 的使用者（密碼設為不可登入的佔位雜湊，需由管理員重設）
- documents.salesperson_id 的外鍵改指 users.id，並同步轉換既有值
- 移除 salespersons 表

Revision ID: 0002_user_accounts
Revises: 0001_initial
Create Date: 2026-10-21
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_user_accounts"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

# 佔位雜湊：不是任何密碼的有效雜湊，遷移後的帳號無法直接登入，必須由管理員重設密碼
UNUSABLE_HASH = "!unusable!forced-password-reset-required!"


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="clerk"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    bind = op.get_bind()

    # 1) 舊銷貨員 → 新使用者
    bind.execute(
        sa.text(
            """
            INSERT INTO users (username, display_name, password_hash, role, is_active, created_at)
            SELECT COALESCE(code, name), name, :unusable, 'salesperson', is_active, created_at
            FROM salespersons
            """
        ),
        {"unusable": UNUSABLE_HASH},
    )

    # 2) documents.salesperson_id 的值轉換成新的 users.id
    bind.execute(
        sa.text(
            """
            UPDATE documents d
            SET salesperson_id = u.id
            FROM users u, salespersons s
            WHERE d.salesperson_id = s.id
              AND u.username = COALESCE(s.code, s.name)
            """
        )
    )

    # 3) 外鍵換指向
    op.drop_constraint("documents_salesperson_id_fkey", "documents", type_="foreignkey")
    op.create_foreign_key(
        "fk_documents_salesperson_users", "documents", "users", ["salesperson_id"], ["id"]
    )

    # 4) 移除舊表
    op.drop_table("salespersons")


def downgrade():
    op.create_table(
        "salespersons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_salespersons_code", "salespersons", ["code"], unique=True)

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO salespersons (name, code, is_active, created_at)
            SELECT display_name, username, is_active, created_at
            FROM users WHERE role = 'salesperson'
            """
        )
    )
    op.drop_constraint("fk_documents_salesperson_users", "documents", type_="foreignkey")
    op.create_foreign_key(
        "documents_salesperson_id_fkey", "documents", "salespersons", ["salesperson_id"], ["id"]
    )
    op.drop_table("users")
