r"""命令列工具：建立第一位管理員、塞示範資料。

用法：
    $env:DATABASE_URL = "postgresql+psycopg://postgres:<密碼>@localhost:5432/ailearn"
    ..\.venv\Scripts\python.exe -m flask --app "app:create_app" create-admin
    ..\.venv\Scripts\python.exe -m flask --app "app:create_app" seed

安全性：
- 密碼只從環境變數或當場輸入取得，不寫入任何檔案（AD-8、AD-15）。
- seed 只建立「品項」與「示範帳號」；庫存現量由入庫單產生，而入庫功能屬於 Story 2.1，
  在該功能完成前，品項的庫存現量會是 0（這是正確行為，不是 bug）。
"""

import getpass
from datetime import date
from decimal import Decimal

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import Document, DocumentItem, Product, Stock, StockMovement, User
from app.models.user import ROLE_ADMIN, ROLE_SALESPERSON

SAMPLE_PRODUCTS = [
    # sku, 名稱, 分類, 單位, 單價, 安全庫存, 補貨前置天數
    ("A-001", "可樂 500ml", "飲料", "瓶", "25", 20, 7),
    ("A-002", "優酪乳 500ml", "冷藏", "瓶", "45", 12, 3),
    ("A-003", "礦泉水 600ml", "飲料", "瓶", "20", 30, 7),
    ("A-004", "洋芋片 70g", "零食", "包", "32", 15, 10),
    ("A-005", "泡麵 碗裝", "速食", "碗", "45", 24, 14),
    ("A-006", "衛生紙 抽取式", "耗材", "包", "95", 8, 7),
    ("A-007", "洗碗精 500ml", "清潔", "瓶", "68", 5, 10),
    ("A-008", "原子筆 黑色", "文具", "支", "12", 20, 21),
]

# 示範帳號：密碼一律是 demo1234（教學用途，介面有標示）
DEMO_ACCOUNTS = [
    ("clerk01", "陳姐", "clerk"),
    ("view01", "實習生", "viewer"),
]
DEMO_PASSWORD = "demo1234"
# 遷移自舊 salespersons 的帳號，密碼是佔位值；seed 會幫它們設成示範密碼
UNUSABLE_PREFIX = "!"


@click.command("create-admin")
@click.option("--username", default=None, help="帳號（留空則互動詢問）")
@click.option("--display-name", default=None, help="姓名（留空則互動詢問）")
@with_appcontext
def create_admin_command(username: str | None, display_name: str | None) -> None:
    """建立第一位管理員帳號（FR-27）。"""
    from app.domain.auth_service import hash_password

    if db.session.query(User).filter(User.role == ROLE_ADMIN).first() is not None:
        click.echo("已有管理員，請用網頁端新增帳號。")
        return

    click.echo("建立第一位管理員（密碼不會寫入任何檔案）：")
    username = (username or click.prompt("帳號", type=str)).strip()
    display_name = (display_name or click.prompt("姓名", type=str)).strip()
    password = getpass.getpass("密碼（至少 8 碼，不會顯示）")
    confirm = getpass.getpass("再輸入一次密碼")

    if password != confirm:
        click.echo("兩次密碼不一致，未建立。")
        return
    if len(password or "") < 8:
        click.echo("密碼至少 8 碼，未建立。")
        return

    db.session.add(
        User(
            username=username,
            display_name=display_name,
            password_hash=hash_password(password),
            role=ROLE_ADMIN,
        )
    )
    db.session.commit()
    click.echo(f"管理員已建立：{username}")


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """建立示範品項與示範帳號（已存在者略過）。"""
    from app.domain.auth_service import hash_password

    created_products = 0
    for sku, name, category, unit, price, safety_qty, lead_time in SAMPLE_PRODUCTS:
        if db.session.query(Product).filter(Product.sku == sku).one_or_none():
            continue
        product = Product(
            sku=sku,
            name=name,
            category=category,
            unit=unit,
            price=Decimal(price),
            safety_qty=safety_qty,
            lead_time_days=lead_time,
        )
        db.session.add(product)
        db.session.flush()
        db.session.add(Stock(product_id=product.id, qty=0))
        created_products += 1

    created_users = 0
    for username, display_name, role in DEMO_ACCOUNTS:
        if db.session.query(User).filter(User.username == username).one_or_none():
            continue
        db.session.add(
            User(
                username=username,
                display_name=display_name,
                password_hash=hash_password(DEMO_PASSWORD),
                role=role,
            )
        )
        created_users += 1

    # 由舊 salespersons 遷移而來、密碼仍是佔位值的帳號 → 設成示範密碼，讓它們可以登入
    for user in db.session.query(User).all():
        if (user.password_hash or "").startswith(UNUSABLE_PREFIX):
            user.password_hash = hash_password(DEMO_PASSWORD)
            created_users += 1

    db.session.commit()
    click.echo(f"示範資料完成：新增品項 {created_products} 筆、帳號 {created_users} 個。")
    if created_users:
        click.echo(f"示範帳號密碼一律是：{DEMO_PASSWORD}")
    click.echo("（庫存現量目前都是 0 —— 入庫功能屬 Story 2.1，完成後才能有數字。）")


@click.command("reset-demo")
@with_appcontext
def reset_demo_command() -> None:
    """重設示範資料（教學用，會清空所有單據與異動）。

    ⚠️ 這是**示範資料重置**，會直接刪除 documents / document_items / stock_movements，
    並把庫存現量歸零 —— 這違反 AD-2（異動不可竄改）的精神，僅供教學環境重置使用，
    正式環境請勿執行。

    重設後會用領域服務建立一張示範入庫單，讓「可樂 500ml」的庫存現量 = 24，
    正好對上 PRD 的使用者旅程（UJ-1：入庫 36 瓶 → 24 → 60）。
    """
    from app.domain.stock_service import create_stock_in

    db.session.query(StockMovement).delete()
    db.session.query(DocumentItem).delete()
    db.session.query(Document).delete()
    for stock in db.session.query(Stock).all():
        stock.qty = 0
    db.session.commit()

    actor = db.session.query(User).filter(User.username == "clerk01").one_or_none()
    if actor is None:
        click.echo("找不到 clerk01 帳號，請先執行 seed。")
        return

    cola = db.session.query(Product).filter(Product.sku == "A-001").one_or_none()
    if cola is None:
        click.echo("找不到 A-001 品項，請先執行 seed。")
        return

    result = create_stock_in(
        actor,
        {
            "doc_date": date.today().isoformat(),
            "note": "示範資料：開店前的既有庫存",
            "items": [
                {"product_id": cola.id, "qty": 24, "unit_price": 25, "note": "示範初始庫存"}
            ],
        },
    )
    change = result["changes"][0]
    click.echo(f"示範資料已重設：{change['name']} 庫存 {change['before']} → {change['after']}")
    click.echo("（之後在畫面上入庫 36 瓶，就會看到 24 → 60，正是 PRD UJ-1 的情境）")


def register_cli(app) -> None:
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_command)
    app.cli.add_command(reset_demo_command)
