# 專案 AI 協作入口

本專案為「資料庫存管理系統」，後端資料庫為 PostgreSQL 18.6（資料庫名稱 `ailearn`，全小寫）。

<!-- bmad:context -->
<!-- Verified 2026-10-21 (尚未納入 git，無 commit SHA)。Managed by bmad-project-context；此區塊內的內容在 refresh 時會被取代。要保留的內容請寫在標記之外。 -->

## Orientation

資料庫存管理系統：進銷存、盤點、補貨判斷、銷貨員業績的單機版工具。後端 Python 3.14 + Flask + SQLAlchemy + Flask-Migrate（Alembic）＋ PostgreSQL 18.6；前端 React 19 + Vite + Ant Design 6（JavaScript，非 TypeScript）。規劃文件在 `_bmad-output/planning-artifacts/`（PRD v0.4、架構 spine、UX spines、epics.md，22 個 story）。BMAD Method v6.12.4 已安裝（`_bmad/`、`.agents/skills/`）。

## Policy

- 資料庫密碼、連線字串一律不寫入檔案、程式碼、`.env`、對話紀錄、產出文件；只在環境變數裡傳遞。
- 不建立 `pgpass.conf`、不修改 `pg_hba.conf`、不重啟資料庫服務，除非使用者當場同意。
- 執行 SQL 前確認目標是 `ailearn`，不要動 `postgres` 系統庫。
- schema 只能由 Alembic 遷移腳本改動；禁用 `db.create_all()`、禁用手改資料庫。
- 庫存現量只能由 `backend/app/domain/stock_service.py` 改寫，其他地方不得 UPDATE `stock.qty`。
- 庫存異動 append-only：不 UPDATE、不 DELETE，更正以反向紀錄表達。
- 權限判斷集中在 `backend/app/security.py`；端點不得自行讀 session 判斷權限。
- 使用者密碼只存單向雜湊（werkzeug）；登入失敗訊息不透露帳號是否存在。
- 記錄者與銷貨員歸屬取自登入身分，忽略前端傳入的同名字段。
- 每完成一段工作，在 `協作區\工作記錄.md` 補一筆（最新在最上面）。
- 有疑問先問使用者，不要自行假設密碼、帳號、資料表結構。

## Where things are

- 環境、連線方式、資料庫規則完整版：`協作區\AGENTS.md`；進度與交接：`協作區\工作記錄.md`。
- 規劃文件：`_bmad-output\planning-artifacts\`（`prds\`、`architecture\`、`ux-designs\`、`epics.md`）。
- 後端：`backend\app\{models,domain,api}\`、`backend\app\security.py`、`backend\migrations\`、`backend\tests\`。
- 前端：`frontend\src\{pages,api,auth,constants}\`。
- 啟動捷徑：`start-backend.cmd`、`start-frontend.cmd`。

## Running and verifying

- 後端：`start-backend.cmd`（提示輸入資料庫密碼，密碼不落地）→ `http://127.0.0.1:5000`。
- 前端：`start-frontend.cmd` → `http://localhost:5173`（用 `localhost`，不要 `127.0.0.1`）。
- 前端改完必跑：`npm run lint`（含 react-hooks `rules-of-hooks`）與 `npm run build`。
- 煙霧測試（需後端在跑）：`python backend\tests\smoke_stock_in.py`。
- 遷移：`..\.venv\Scripts\python.exe -m flask --app "app:create_app" db upgrade`（在 `backend\` 執行）。
- Python 依賴用 `uv`（`.venv` 已在專案根目錄）；PowerShell 裡 npm/npx 一律加 `.cmd`。
- 版本：Python 3.14.7、Node 24.21.0、PostgreSQL 18.6、Flask 3.1.3、SQLAlchemy 2.1.5、Alembic 1.20.0、psycopg 3.3.6、React 19.3.1、antd 6.6.7、Recharts 3.10.1。

## Conventions that differ from defaults

- 用 PRD 詞彙表命名，資料表與 API 欄位用其對應英文：`products`、`stock`、`stock_movements`、`documents`、`document_items`、`users`；不另創同義詞。
- 數量為整數；單價與金額在資料庫為 `NUMERIC(10,2)`，API 以**字串**回傳，前端不做二次四捨五入。
- API 列表一律回 `{items,total,page,page_size}`；錯誤一律回 `{error:{code,message,details}}`；狀態碼 400/401/403/404/409/422。
- 前端數字欄位右對齊並用 `tabular-nums`（`index.html` 的 `.num` 類別）。
- 介面一律繁體中文；`frontend\src\constants\` 集中管理顯示名稱，不在頁面硬寫。
- `.cmd` 批次檔以 **cp950 + CRLF** 儲存。

## Known pitfalls

- **React Hook 只能在元件函式內呼叫**：`AntApp.useApp()` 寫在模組頂層會讓整棵 React 樹渲染失敗、頁面全白（本專案已犯 3 次）。寫完跑 `npm run lint`。
- **空白頁除錯**：`chrome --headless=new --dump-dom <url>` 確認 React 有沒有渲染出內容；要堆疊就在 `index.html` 暫時加 error 監聽把 stack 寫進 DOM，dump 完記得移除。
- **`.cmd` 必須存 cp950 + CRLF，且檔內不可 `chcp 65001`**：CMD 用主控台 codepage 解析批次檔，UTF-8 內容會讓中文指令被拆成亂碼碎片（`'xxx' 不是內部或外部命令`）。
- **Vite 8 只監聽 IPv6 `::1`**：`http://127.0.0.1:5173` 連不上，一律用 `http://localhost:5173`。
- **PowerShell 執行原則擋 `npm.ps1`/`npx.ps1`**：用 `npm.cmd`、`npx.cmd`。
- **記事本暫存密碼的檔案放的是「資料庫 postgres 密碼」**，不是應用程式帳號密碼；示範帳號密碼固定 `demo1234`。用完立刻刪除該檔。
- **`flask create-admin` 必須在真實主控台執行**（getpass 需要 TTY），agent 沒辦法代跑；把指令交給使用者。
- **刪除品項時 `stock` 要 cascade**（`cascade="all, delete-orphan"`），否則 SQLAlchemy 會嘗試清空主鍵欄位 → 500。
- **測試斷言不要寫死示範數字**（如庫存 24），資料庫現況可能不同；斷言增量（`after - before`）。
- **`APP_SECRET_KEY` 未設定**時每次啟動都換金鑰 → 重啟後需重新登入。
- 密碼含 `@ : # /` 等字元時，`DATABASE_URL` 需做 URL 編碼，否則連線失敗。

<!-- /bmad:context -->

## 動工前必讀

1. `協作區\AGENTS.md` — 環境、資料庫連線方式、重要規則（完整版）
2. `協作區\工作記錄.md` — 目前進度、交接紀錄、下一步

## 最重要規則（摘要）

- 資料庫密碼**一律不寫入**任何檔案、程式碼、`.env` 範本或 commit。
- 不建立 `pgpass.conf`、不修改 `pg_hba.conf`、不重啟資料庫服務，除非使用者當場同意。
- 執行 SQL 前先確認目標是 `ailearn`，避免誤動 `postgres` 系統資料庫。
- 每完成一段工作，在 `協作區\工作記錄.md` 補一筆（最新在最上面）。
- 有疑問先問使用者，不要自行假設密碼、帳號或資料表結構。

## BMAD Method v6.12.4（已安裝）

安裝方式：`npx.cmd bmad-method@latest install`（模組 `bmm`、工具 `opencode`、語言繁體中文）

- `_bmad\` — 核心與 bmm 模組、Python 腳本、設定檔
- `.agents\skills\` — 29 個 `bmad-*` skills
- `.opencode\commands\` — 對應的 slash commands
- `_bmad-output\` — 產出：`planning-artifacts\`（PRD、架構、epics）、`implementation-artifacts\`（story、review、retro）

### 怎麼用

- 不知道下一步 → 呼叫 `bmad-help`
- 交辦一個功能或修改 → 呼叫 `bmad-build`
- 需要正式規劃 → `bmad-prd` / `bmad-architecture` / `bmad-create-epics-and-stories` / `bmad-sprint-planning`
- 開新 session 時，agent 應先讀 `協作區\工作記錄.md`，再繼續 BMAD 流程

> BMAD 產出的規劃文件同樣受上面規則約束：**不可出現資料庫密碼或連線字串**。
