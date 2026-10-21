"""Story 2.1 收貨入庫 的煙霧測試（走 HTTP，針對執行中的後端）。

用法（後端需先啟動，見 start-backend.cmd）：
    python backend/tests/smoke_stock_in.py

會建立一張示範入庫單（可樂 500ml × 36），這是刻意留下的示範資料。
"""

import json
import sys
import urllib.error
import urllib.request
import http.cookiejar

BASE = "http://127.0.0.1:5000"
results = []


def make_client():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    return opener


def call(opener, method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with opener.open(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return e.code, (json.loads(body) if body else None)


def check(name, actual, expected):
    ok = actual == expected
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got {actual!r}, expected {expected!r}")


op = make_client()

# 1) 登入（倉管）
status, body = call(op, "POST", "/api/auth/login", {"username": "clerk01", "password": "demo1234"})
check("倉管登入", status, 200)

# 2) 找出「可樂 500ml」的 id 與目前庫存
status, body = call(op, "GET", "/api/products?keyword=A-001")
check("查詢品項", status, 200)
cola = body["items"][0]
cola_id = cola["id"]
check("找到可樂 500ml", cola["name"], "可樂 500ml")

# 3) 送出前先記下庫存現量（透過異動重算）
status, body = call(op, "GET", f"/api/products/{cola_id}")
check("讀取單一品項", status, 200)

# 4) 送出入庫單
status, body = call(
    op,
    "POST",
    "/api/documents/stock-in",
    {
        "doc_date": "2026-10-21",
        "note": "供應商 A 到貨",
        "items": [{"product_id": cola_id, "qty": 36, "unit_price": 25, "note": "供應商 A 到貨"}],
    },
)
check("送出入庫單", status, 201)
doc_no = body["document"]["doc_no"] if body and "document" in body else None
change = body["changes"][0] if body and body.get("changes") else None
# 庫存增加量＝入庫數量（初始值由資料庫決定，不假設 24）
check("庫存增加 36", (change["after"] - change["before"]) if change else None, 36)
check("記錄者 = 登入帳號", body["document"]["recorded_by"], "clerk01")
check("單號自動產生格式", doc_no.startswith("IN-"), True)

# 5) 異動明細查詢屬 Story 3.3（尚未實作），此處先確認端點存在但回 404
status, body = call(op, "GET", f"/api/stock-movements?product_id={cola_id}")
check("異動查詢尚未實作（預期 404）", status, 404)

# 6) 入庫歷史可查到這張單
status, body = call(op, "GET", "/api/documents?type=IN")
check("查詢入庫歷史", status, 200)
total_docs = body["total"]
found = [d for d in body["items"] if d["doc_no"] == doc_no]
check("入庫歷史含新單", len(found), 1)
check("歷史顯示記錄者", found[0]["recorded_by"] if found else None, "clerk01")
check("歷史件數正確", found[0]["total_qty"] if found else None, 36)

# 7) 同一品項兩列 → 應合併（36 + 4 = 40）
status, body = call(
    op,
    "POST",
    "/api/documents/stock-in",
    {
        "doc_date": "2026-10-21",
        "items": [
            {"product_id": cola_id, "qty": 2, "unit_price": 25},
            {"product_id": cola_id, "qty": 3, "unit_price": 25},
        ],
    },
)
check("同品項多列送出成功", status, 201)
check("同品項多列已合併為一列", len(body["changes"]) if body.get("changes") else 0, 1)
check("合併後數量正確", body["changes"][0]["qty"] if body.get("changes") else None, 5)

# 8) 數量 0 → 拒絕，且不留下半套資料（總筆數不變）
status, body = call(op, "GET", "/api/documents?type=IN")
before_count = body["total"]
status, body = call(
    op,
    "POST",
    "/api/documents/stock-in",
    {"doc_date": "2026-10-21", "items": [{"product_id": cola_id, "qty": 0, "unit_price": 25}]},
)
check("數量 0 被拒", status, 400)
status, body = call(op, "GET", "/api/documents?type=IN")
check("被拒的單沒有留下紀錄", body["total"], before_count)

# 9) 未登入不能入庫
op2 = make_client()
status, body = call(
    op2, "POST", "/api/documents/stock-in", {"items": [{"product_id": cola_id, "qty": 1}]}
)
check("未登入入庫被拒", status, 401)

# 10) 銷貨員不能入庫
op3 = make_client()
call(op3, "POST", "/api/auth/login", {"username": "XM", "password": "demo1234"})
status, body = call(
    op3, "POST", "/api/documents/stock-in", {"items": [{"product_id": cola_id, "qty": 1}]}
)
check("銷貨員入庫被拒", status, 403)

print()
print(f"結果：{sum(results)}/{len(results)} 通過")
sys.exit(0 if all(results) else 1)
