# 庫存管理系統

小微倉庫／店務用的單機版進銷存與盤點工具。React 前端 ＋ Python Flask 後端 ＋ PostgreSQL 18，schema 由 Alembic（Flask-Migrate）管理。

- 產品需求（PRD v0.4）：`_bmad-output/planning-artifacts/prds/prd-庫存管理系統-2026-10-21/prd.md`
- 架構 spine：`_bmad-output/planning-artifacts/architecture/architecture-庫存管理系統-2026-10-21/ARCHITECTURE-SPINE.md`
- UX spine：`_bmad-output/planning-artifacts/ux-designs/ux-庫存管理系統-2026-10-21/`
- Epics & Stories：`_bmad-output/planning-artifacts/epics.md`

---

## 1. 環境需求

| 工具 | 版本 | 備註 |
|---|---|---|
| Python | 3.14.7 | 已於本機驗證 |
| uv | 0.13.1 | 用於管理 Python 依賴 |
| Node.js | 24.21.0 | 僅供前端建置 |
| PostgreSQL | 18.6 | 本機服務 `postgresql-x64-18`，資料庫 `ailearn` |

## 2. 安裝

```powershell
# 後端
uv venv --python 3.14 .venv
uv pip install --python .venv flask flask-migrate flask-sqlalchemy "psycopg[binary]" flask-cors pytest

# 前端
cd frontend
npm install
```

## 3. 設定資料庫連線（密碼不落地）

密碼**只放在環境變數**，不要寫進任何檔案、`.env`、或版控（見 `協作區\AGENTS.md`）。

```powershell
$env:DATABASE_URL = "postgresql+psycopg://postgres:<你的密碼>@localhost:5432/ailearn"
```

`backend/.env.example` 只列出需要的 key，沒有任何值。

## 4. 建立資料表（schema 唯一來源是遷移腳本）

```powershell
cd backend
..\.venv\Scripts\python.exe -m flask --app "app:create_app" db upgrade
..\.venv\Scripts\python.exe -m flask --app "app:create_app" seed
```

> 禁止 `db.create_all()`、禁止手改資料庫（架構 spine AD-11）。

### 4.1 建立第一位管理員

```powershell
..\.venv\Scripts\python.exe -m flask --app "app:create_app" create-admin --username admin --display-name "店主"
```

指令會互動式詢問密碼（不會顯示、不會寫入檔案）。已存在管理員時會拒絕執行。

### 4.2 示範帳號（`seed` 產生）

| 帳號 | 姓名 | 角色 | 密碼 |
|---|---|---|---|
| `clerk01` | 陳姐 | 倉管 | `demo1234` |
| `XM` | 小美 | 銷貨員 | `demo1234` |
| `AX` | 阿賢 | 銷貨員 | `demo1234` |
| `view01` | 實習生 | 唯讀 | `demo1234` |

## 5. 啟動

> 最方便的兩個捷徑：根目錄的 `start-backend.cmd`（會提示輸入資料庫密碼）與 `start-frontend.cmd`。

### 開發期（兩個終端機）

```powershell
# 終端機 A：後端
cd backend
..\.venv\Scripts\python.exe -m flask --app "app:create_app" run --port 5000

# 終端機 B：前端
cd frontend
npm run dev
```

開啟 <http://127.0.0.1:5173>

### 正式啟動（單一指令、單一網址）

```powershell
cd frontend
npm run build          # 產生 frontend/dist
cd ../backend
..\.venv\Scripts\python.exe -m flask --app "app:create_app" run --port 5000
```

開啟 <http://127.0.0.1:5000>（Flask 同時提供 API 與前端靜態檔）

## 6. 目前進度

| Story | 狀態 |
|---|---|
| 1.1 一鍵啟動的系統與可重建的資料庫 | ✅ |
| 1.2 建立第一個管理員 | ✅（`flask create-admin`） |
| 1.3 登入與登出 | ✅ |
| 1.4 依角色限制操作 | ✅（後端 401/403 ＋ 前端按鈕隱藏） |
| 1.5 管理員管理帳號 | ✅（「使用者管理」頁） |
| 1.6 記錄者與歸屬自動帶入登入身分 | ⏳ 待 Story 2.1（單據功能）完成後驗證 |
| 1.7 建立品項 | ✅ |
| 1.8 查詢與篩選品項 | ✅ |
| 1.9 修改與停用品項 | ✅ |
| 2.1 ～ 4.5 | 未開始 |

## 7. 常見問題

| 症狀 | 原因 | 處理 |
|---|---|---|
| 啟動時說缺少 `DATABASE_URL` | 環境變數沒設 | 依第 3 節設定 |
| `could not translate host name` | 連線字串格式錯 | 確認 `postgresql+psycopg://` 前綴與 `ailearn` 全部小寫 |
| 前端開得起來但 API 都 404 | 後端沒啟或 proxy 沒生效 | 確認終端機 A 在 5000、proxy target 是 `http://127.0.0.1:5000` |
| 中文亂碼 | 終端機編碼 | `chcp 65001`；CSV 匯出一律 UTF-8 with BOM |
| 開啟網頁是登入頁 | 正常 | 尚未登入；用示範帳號或管理員帳號登入 |
| 登入後又被踢回登入頁 | 後端重啟過 | `APP_SECRET_KEY` 未設定時每次重啟都會換金鑰；啟動前設定 `APP_SECRET_KEY` 即可固定 |
| 一直顯示「帳號或密碼錯誤」 | 密碼打錯或帳號已停用 | 密碼至少 8 碼；管理員可在「使用者管理」重設密碼 |
