# 專案協作說明（給 AI Agent 讀）

> 本檔案是這個資料夾的共用背景資料。任何 agent 在這個資料夾工作前，請先讀完本檔，再讀 `工作記錄.md` 了解目前進度。
>
> ⚠️ 根目錄 `AGENTS.md` 另有一個 managed block（Orientation / Policy / **Known pitfalls** / Running and verifying），記錄了本專案踩過的坑與防範方式，**開工前請一併讀取**。

## 專案概要

- **專案名稱：** 資料庫存管理系統
- **用途：** 庫存／進出貨管理，以 PostgreSQL 為後端資料庫
- **上層資料夾：** `C:\Users\user\Desktop\資料庫存管理系統`
- **使用手冊：** `..\使用手冊.html`（好讀版）、`..\使用手冊.md`（原始檔）
- **作業系統：** Windows（主機名稱 `DESKTOP-O22V3O4`，使用者 `user`）

## 資料庫環境（已實際驗證）

| 項目 | 值 |
|------|-----|
| PostgreSQL 版本 | 18.6（64 位元） |
| 安裝路徑 | `C:\Program Files\PostgreSQL\18` |
| 資料目錄 | `C:\Program Files\PostgreSQL\18\data` |
| Windows 服務 | `postgresql-x64-18`（執行中、開機自動啟動） |
| 主機 / 連接埠 | `localhost` / `5432` |
| 資料庫名稱 | `ailearn`（**全小寫**，勿寫成 AIlearn） |
| 擁有者 / 使用者 | `postgres`（超級使用者，目前是唯一角色） |
| 編碼 / 語系 | UTF8 / `Chinese (Traditional)_Taiwan.950` |
| 認證方式 | `scram-sha-256` |
| 目前資料表 | 尚無（空資料庫，約 8 MB） |

## 連線方式

`bin` **不在 PATH**，必須用完整路徑：

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -U postgres -d ailearn
```

密碼：**由使用者在需要時提供，不要寫進任何檔案。**

## 重要規則（請務必遵守）

1. **絕對不要**把資料庫密碼寫入檔案、程式碼、`.env` 範本或 commit。
2. **不要**建立 `%APPDATA%\postgresql\pgpass.conf`（使用者已明確拒絕明文密碼存檔）。
3. **不要**修改 `pg_hba.conf` 或重啟資料庫服務，除非使用者當場同意（且需要 UAC 提權）。
4. 執行 SQL 前先確認目標是 `ailearn` 資料庫，避免誤操作到 `postgres` 系統資料庫。
5. PostgreSQL 15 之後 `public` schema 預設不開放建立權限，若要建專用帳號需額外 `GRANT`。
6. 中文輸出前先 `chcp 65001`，否則 PowerShell 會亂碼。

## 目前的狀態

- [x] PostgreSQL 18.6 安裝完成、服務正常
- [x] 建立資料庫 `ailearn`
- [x] 修改 `postgres` 密碼（舊密碼已失效）
- [x] 撰寫使用手冊（`使用手冊.md` / `.html`）
- [ ] 建立專用應用程式帳號（尚未決定）
- [ ] 建立資料表（手冊第 6 節有建議 schema，尚未執行）
- [ ] 專案程式碼（尚未開始）

## BMAD Method（AI 開發流程，2026-10-21 安裝）

專案已安裝 **BMAD Method v6.12.4 穩定版**（模組 `bmm`，工具 `opencode`），用來把「需求 → 規格 → 架構 → 實作」的決策留下文件。

| 路徑 | 內容 |
|------|------|
| `_bmad\` | 核心 + bmm 模組、Python 腳本、設定（`core\config.yaml`、`bmm\config.yaml`） |
| `.agents\skills\bmad-*\` | 29 個 skill（給 agent 讀的流程定義） |
| `.opencode\commands\bmad-*.md` | 對應的 29 個 slash command |
| `_bmad-output\` | 產出：`planning-artifacts\`、`implementation-artifacts\` |

- 設定值：`user_name: 使用者`、`communication_language: 繁體中文`、`document_output_language: 繁體中文`、`project_knowledge: docs`。
- 常用入口：`bmad-help`（不知道下一步做什麼就問它）、`bmad-build`（交辦一個功能或修改）、`bmad-prd`、`bmad-architecture`、`bmad-create-epics-and-stories`、`bmad-sprint-planning`。
- skill 內部會跑 `uv run _bmad\scripts\resolve_config.py --project-root .`，環境已具備 `uv 0.13.1`。
- 升級／重裝：`npx.cmd bmad-method@latest install`（PowerShell 會擋 `npm.ps1`/`npx.ps1`，**要加 `.cmd`**）。
- BMAD 的產出物（PRD、架構、故事）仍要遵守本檔的資料庫規則；**密碼絕不可寫進任何產出文件**。

## 資料夾結構

```
資料庫存管理系統\
├── AGENTS.md          ← 給 agent 的入口（導向本檔）
├── 使用手冊.md
├── 使用手冊.html
├── _bmad\             ← BMAD 核心與模組
├── _bmad-output\      ← BMAD 產出（規劃／實作文檔）
├── .agents\skills\    ← BMAD skills（opencode 讀取）
├── .opencode\commands\← BMAD slash commands
└── 協作區\
    ├── AGENTS.md      ← 本檔
    └── 工作記錄.md    ← 進度與交接紀錄
```

## 協作約定

- 每次完成一段工作，在 `工作記錄.md` 補上一筆（日期、做了什麼、留下什麼、下一步）。
- 動工前先看 `工作記錄.md` 最後幾筆，避免重複或覆蓋別人的進度。
- 有疑問先問使用者，不要自行假設密碼、帳號或資料表結構。
