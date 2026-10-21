---
status: draft
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - '_bmad-output/planning-artifacts/prds/prd-庫存管理系統-2026-10-21/prd.md'
  - '_bmad-output/planning-artifacts/architecture/architecture-庫存管理系統-2026-10-21/ARCHITECTURE-SPINE.md'
  - '_bmad-output/planning-artifacts/ux-designs/ux-庫存管理系統-2026-10-21/DESIGN.md'
  - '_bmad-output/planning-artifacts/ux-designs/ux-庫存管理系統-2026-10-21/EXPERIENCE.md'
---

# 庫存管理系統 - Epic Breakdown

## Overview

本文件把 PRD（v0.4）與架構 spine（2026-10-21）的需求拆成可實作的 epic 與 story。

**實作順序依 PRD §6.3 兩階段：M1 庫存主線（可交作業的 MVP）→ M2 決策加值。** 本文件的所有 epic 皆標註所屬階段。

**範圍邊界**：UX 設計已於 2026-10-21 由 `bmad-ux` 補齊（`DESIGN.md` ＋ `EXPERIENCE.md`，Ant Design 6 之上），其可實作項目已萃取為 UX-DR1 ～ UX-DR16，一併納入 story 的驗收條件。

## Requirements Inventory

### Functional Requirements

（來源：PRD v0.4 §4；數量 26 條）

```
FR1:  建立品項（sku、名稱、分類、單位、單價、安全庫存、補貨前置天數）；sku 唯一，sku 與名稱必填，單價可為 0
FR2:  查詢與篩選品項（sku／名稱關鍵字部分相符、分類、啟用狀態、排序），單頁上限 100 筆
FR3:  修改與停用品項；已被庫存異動引用的品項不可刪除，只能停用
FR4:  建立並送出入庫單（單號、收貨日期、供貨來源備註、多品項數量與單價），送出後批次更新庫存現量
FR5:  查詢入庫歷史（時間區間、品項、單號），可反查原單據
FR6:  更正已送出的入庫單：以反向（沖銷）紀錄表達，兩筆互相連結
FR7:  建立並送出具庫單（單號、日期、用途：銷售／領用／報廢、多品項數量）；庫存不足時拒絕送出；用途為銷售時必填銷貨員
FR8:  查詢出庫歷史（時間區間、品項、用途、銷貨員），數字與進銷存報表一致
FR9:  查詢庫存現量（關鍵字／分類篩選），顯示值與 stock.qty 完全一致
FR10: 低於安全庫存的警示清單（品項、現量、安全庫存、差距）；安全庫存為 0 者不列入
FR11: 建立盤點單、輸入實盤數，即時顯示帳面數與暫定差異（正＝盤盈、負＝盤虧）
FR12: 送出盤點單：有差異品項必填原因，未填不可送出；送出後不可修改
FR13: 盤點差異報表（品項、時間、帳面數、實盤數、差異量、原因、單號），可看出反覆差異
FR14: 查詢庫存異動明細（品項、類型、時間區間），每筆異動的累加結果必須等於目前庫存現量
FR15: 庫存異動不可竄改：不得修改或刪除，更正一律以新增反向紀錄表達
FR16: 匯出庫存異動紀錄為 CSV（UTF-8 with BOM，Excel 中文不亂碼）
FR17: 進銷存概況報表（期初、入庫、出庫、盤點差異、期末、金額），期末 = 期初 + 入庫 − 出庫 + 盤點差異
FR18: 庫存總值一覽（現量 × 單價加總、高／低庫存排行）
FR19: 補貨建議清單：選擇計算區間（7／30／90 天），依安全庫存 + 日均消耗 × 該品項補貨前置天數 − 庫存現量算建議量；無消耗資料品項另列清單
FR20: 補貨統計報表（區間內入庫量、出庫量、期初期末、平均庫存、消耗速度、補貨次數）
FR21: 匯出／列印補貨建議清單，檔案內標註計算區間與前置天數
FR22: 銷貨員檔案管理（姓名／代號、啟用）；已被引用者不可刪除只能停用
FR23: 出庫單歸屬銷貨員；用途為銷售時必填，未指定者計入「未歸屬銷售」
FR24: 銷貨員業績統計（期間：本週／本月／上月／自訂；銷售金額、件數、品項數、排名）
FR25: 業績明細下鑽：可看到每筆銷售明細並連結回原出庫單，明細加總 = 彙總數字
FR26: 匯出業績報表（彙總與明細兩種粒度）
```

### NonFunctional Requirements

（來源：PRD v0.4 §4.10；數量 9 條）

```
NFR1:  部署與環境：本機 Windows 單一啟動指令啟動；技術棧 React(Vite, JS) + Python Flask + SQLAlchemy + Flask-Migrate(Alembic) + PostgreSQL 18；開發期前後端分開、正式啟動由 Flask 同時提供 API 與靜態檔；Python 依賴以 uv 管理
NFR2:  資料庫與資料：沿用 PostgreSQL 18.6 實例與 ailearn 資料庫；schema 唯一來源為 Alembic 遷移腳本；連線字串只由環境變數注入，alembic.ini 與設定檔不得含明文密碼；不得建立 pgpass.conf、不得改 pg_hba.conf、不得重啟服務；時間戳與時區一致；補貨與業績數字可由原始異動重算
NFR3:  效能：一般操作 ≤ 2 秒；1,000 品項／10,000 異動資料量下查詢 ≤ 2 秒；補貨判斷與業績統計 ≤ 3 秒；單張單據 100 品項內為單一交易且失敗整批 rollback
NFR4:  可靠性與資料完整性：單據與庫存更新同一交易；庫存現量不得變負；應用層不得繞過異動直接改 stock.qty
NFR5:  易用性與可交接性：介面繁體中文；第一天上線者可獨立完成入庫與盤點；提供 Markdown + HTML 雙格式操作手冊（含補貨公式與業績計算說明）
NFR6:  稽核與可追溯：每筆異動記錄時間、品項、類型、數量、單據號、記錄者；任何數字可反溯到每一筆造成它的異動
NFR7:  資料匯出：所有查詢結果清單皆可匯出 CSV，UTF-8 with BOM
NFR8:  測試與可驗收：核心規則具備自動化測試或可重複執行的驗收腳本；補貨公式與業績彙總須有手算對照測試；驗收條件可測試、可量化
NFR9:  開發流程（AI 輔助）：留下可追溯決策紀錄（PRD、架構、epic/story、驗收結果）；敏感資訊不得進入 AI 對話紀錄、產出文件或版本控制
```

### Additional Requirements

（來源：架構 spine `ARCHITECTURE-SPINE.md`；範式＝分層架構 ＋ Transaction Script）

```
AR-1:  AD-1 庫存現量唯一寫入路徑：stock.qty 只由領域服務層改變；禁止任何直接 UPDATE 或 ORM 直接賦值；讀取亦經同一服務層
AR-2:  AD-2 庫存異動 append-only：只允許 INSERT；更正以反向異動 + correction_of_movement_id 表達；不提供異動修改／刪除端點
AR-3:  AD-3 數量變動只能來自單據：每筆異動必帶 document_id；doc_type 僅 IN／OUT／STOCKTAKE；不提供直接建立異動的 API
AR-4:  AD-4 一張單據 = 一個 DB transaction：documents → document_items → stock_movements → stock.qty 同一交易，失敗整批 rollback
AR-5:  AD-5 補貨建議為即時衍生值：不落地、不快取；每次即時計算並回傳 window、calculated_at、各品項 lead_time_days
AR-6:  AD-6 業績以出庫單為計算單位：以 documents(doc_type=OUT, salesperson_id 非空) 為母體；未歸屬另計；不得直接以 movements 為業績來源
AR-7:  AD-7 業務規則在領域層驗證：sku 唯一、數量正整數、出庫不得為負、盤點差異必填原因、單據送出後不可改
AR-8:  AD-8 密碼與連線字串不落地：只從環境變數讀取；alembic.ini 的 sqlalchemy.url 留空由 env.py 覆寫；只提供 .env.example（僅 key）
AR-9:  AD-9 API 形狀統一：列表回 {items,total,page,page_size}；錯誤回 {error:{code,message,details}}；狀態碼 400/404/409/422/500；時間 ISO-8601 含時區
AR-10: AD-10 數量與金額型別：數量為整數；單價與金額為 NUMERIC(10,2)，API 以字串回傳；四捨五入只發生在顯示層
AR-11: AD-11 schema 唯一來源為遷移腳本：禁用 db.create_all()、禁用手改資料庫、SQL 檔不作為 schema 來源
AR-12: AD-12 前端不持有業務規則：不做權威驗證、不做金額計算、不快取業務資料；業務數字一律以 API 回應為準
AR-13: AD-13 命名與詞彙表一致：資料表／欄位／API 欄位統一使用 products、stock、stock_movements、documents、document_items、salespersons；禁止同義詞別名
AR-14: 技術棧版本（已實測／實查 2026-10-21）：Python 3.14.7、Flask 3.1.3、Flask-SQLAlchemy 3.1.1、Flask-Migrate 4.1.0、Alembic 1.20.0、SQLAlchemy 2.1.5、psycopg 3.3.6、Flask-Cors 6.0.5、pytest 9.1.1、uv 0.13.1、Node 24.21.0、React 19.3.1、Vite 8.3.4、antd 6.6.7、Recharts 3.10.1、react-router-dom 7.18.4、PostgreSQL 18.6
AR-15: 資料模型（seed，附錄 D ＋ spine ERD）：products、stock、stock_movements、documents、document_items、salespersons；索引 (product_id, move_type, created_at)、(document_id)、(doc_type, created_at)、(salesperson_id, created_at)、document_items(product_id)
AR-16: 主要 API 表面：/api/products、/api/stock、/api/stock/low-stock、/api/stock-movements、/api/documents?type=IN、/api/documents/stock-in、/api/documents/stock-out、/api/documents/stocktake、/api/reports/stock-summary、/api/replenishment/suggestions?window=30、/api/replenishment/statistics、/api/salespersons、/api/reports/sales-performance、/api/reports/sales-performance/<id>、/api/exports/<report>.csv
AR-17: 原始碼樹（seed）：backend/{app/{config,extensions,models,domain,api,cli},migrations,tests}、frontend/src/{api,components,pages,constants}、docs/、_bmad/、_bmad-output/
AR-18: 執行方式：開發期兩終端機（Flask :5000 / Vite :5173 proxy /api）；正式啟動 npm run build → Flask :5000 同時提供 API 與靜態檔
AR-19: 設定集中於 backend/app/config.py，環境變數前綴 APP_；資料庫連線使用單一 DATABASE_URL，Flask 與 Alembic 共用
AR-20: 測試佈局：backend/tests/，pytest；領域層與 API 層皆需測試；核心規則至少各一測試
AR-21: 前端狀態：不引入 Redux；伺服器資料以 fetch + 自訂 hook（useApi）取得，不做跨頁快取；元件用 AntD Form；中文顯示名集中於 src/constants/labels.js
AR-22: 日誌：結構化單行輸出 stdout，記錄單據號與異動筆數，不記錄密碼與完整連線字串
AR-23: 備份：以 pg_dump 檔案為準，不做自動上雲備份
AR-24: 認證模組：app/security.py 提供 login_required / require_role 守門裝飾器；未登入 401、角色不符 403；端點不得自行判斷權限（AD-14）
AR-25: 密碼儲存：werkzeug.security.generate_password_hash / check_password_hash；users.password_hash 存單向雜湊；明文密碼不得出現在欄位、log、錯誤訊息或 API 回應（AD-15、NFR-10）
AR-26: Session：以 Flask 簽章 cookie 保存，HttpOnly + SameSite=Lax；未登入 401、角色不符 403；登入失敗訊息不區分帳號不存在與密碼錯誤（NFR-10）
AR-27: 身分與歸屬：單據的 recorded_by 一律取自 session（忽略前端傳入）；出庫歸屬由角色決定（銷貨員＝自己、管理員可指定他人）；業績以 users 為母體（AD-16、AD-17）
AR-28: 資料模型：users 表取代 salespersons 表（username unique、display_name、password_hash、role、is_active、created_at、last_login_at）；documents.salesperson_id FK 改指 users.id；以遷移腳本轉換既有 3 筆銷貨員資料（AD-17、AD-11）
```

### UX Design Requirements

（來源：UX spines `DESIGN.md` ＋ `EXPERIENCE.md`，2026-10-21；UI 系統＝Ant Design 6）

```
UX-DR1:  數字呈現規範：所有數量／金額／差異量欄位右對齊並使用 tabular-nums 等寬數字；金額固定兩位小數不縮寫（DESIGN.md typography.numeric、components.table-numeric-cell）
UX-DR2:  顏色語意：主色墨綠 #1F6F5C；強調橘 #C2410C 僅用於三種需立即行動的情況（庫存不足、盤點差異未填原因、送出將被擋）；其餘狀態色繼承 antd 預設
UX-DR3:  資訊架構：11 個畫面（儀表板、品項、入庫、出庫、庫存查詢、盤點、異動紀錄、報表、補貨判斷、銷貨員業績、設定），固定左側導覽依「日常作業／查詢／分析／設定」分組
UX-DR4:  單據表單行為：上方單據資訊＋下方可增列的明細表；Enter 自動新增下一列並聚焦品項欄；底部即時顯示件數與金額合計；送出後表單清空並留在原頁以支援連續登錄（EXPERIENCE.md Component Patterns 單據表單）
UX-DR5:  盤點摩擦處理：差異即時計算並標示「盤盈／盤虧」；差異原因為必填且以橘色標示；頂部差異彙整列顯示「共 N 個品項、差異 M 個、已填原因 K 個」；M > K 時阻擋送出並捲動到第一個缺原因列，禁止跳出對話框
UX-DR6:  送出被擋的錯誤呈現：不清空表單、錯誤顯示在該列下方並含具體數字（「目前 12、需 20」）、焦點移至第一個問題列、伺服器錯誤時保留已輸入內容並提供重試
UX-DR7:  空狀態與查無資料：文案格式固定為「{事實}。{下一步一句話}。」並附一個主要動作按鈕；查無結果時顯示已套用的篩選條件並提供「清除條件」；區間無資料時顯示區間而非空白
UX-DR8:  狀態呈現：冷啟動用 Skeleton、不使用全屏遮罩；提交中按鈕 loading 停用以防重複送出；送出成功以 message 呈現「品項：原數 → 新數」
UX-DR9:  低庫存呈現：僅在有低庫存品項時出現警示條並列出品項與缺口；表格內以標籤標示，不整頁變色；負庫存以 error 色加「負庫存」標籤
UX-DR10: 補貨建議呈現：表頭固定顯示計算區間、前置天數與計算時間；建議量為 0 者不列出；無出庫紀錄的品項另列「無消耗資料（可能滯銷）」清單；匯出檔案須含區間與前置天數標註
UX-DR11: 業績呈現：排名可依金額或件數切換；頁面頂端顯示「未歸屬銷售」警示與合計；每列標註「自報資料」；下鑽明細可連結回原出庫單；匯出檔案帶同樣說明
UX-DR12: 可及性底線：目標 WCAG 2.2 AA；換頁朗報畫面名稱與筆數；錯誤以 aria-live 宣告；焦點外框可見；表格使用真實 table 語義與 th scope；顏色不作為唯一訊息通道（低庫存必有文字標籤、盤盈盤虧必有文字）
UX-DR13: 響應式與平台：≥1280px 固定導覽＋表格滿寬、表單限寬 960px；768–1023px 導覕收圖示、明細改卡片式列；<768px 唯讀（查詢／庫存／報表／業績／補貨可看，寫入頁不顯示送出按鈕）
UX-DR14: 互動禁令：不做無限捲動、不做 hover-only 必要操作、不做多層 Modal、不允許批次刪除已送出單據、不做 wizard 多步驟表單、不做頁面轉場與數字滾動動畫
UX-DR15: 匯出行為：所有清單與報表頁統一「匯出 CSV」動作，輸出 UTF-8 with BOM，匯出後以 message 告知筆數
UX-DR16: 不可逆操作（沖銷、停用品項）需 Modal 確認並要求輸入原因或確認文字；送出單據用 Popconfirm 簡短確認
```

### FR Coverage Map

```
FR1:  Epic 1 - 建立品項（sku 唯一、必填；含補貨前置天數）
FR2:  Epic 1 - 查詢與篩選品項
FR3:  Epic 1 - 修改與停用品項
FR4:  Epic 2 - 建立並送出入庫單
FR5:  Epic 2 - 查詢入庫歷史
FR6:  Epic 2 - 沖銷更正已送出的單據（Story 2.2）
FR7:  Epic 2 - 建立並送出具庫單（含庫存不足阻擋、銷售必填銷貨員）
FR8:  Epic 2 - 查詢出庫歷史
FR9:  Epic 3 - 查詢庫存現量
FR10: Epic 3 - 低於安全庫存的警示清單
FR11: Epic 2 - 建立盤點單、輸入實盤數
FR12: Epic 2 - 送出盤點單（差異必填原因）
FR13: Epic 2 - 盤點差異報表
FR14: Epic 3 - 查詢庫存異動明細
FR15: Epic 3 - 異動不可竄改（AD-2，並在每個寫入 story 帶為 AC）
FR16: Epic 4 - 匯出庫存異動紀錄為 CSV
FR17: Epic 4 - 進銷存概況報表
FR18: Epic 4 - 庫存總值一覽
FR19: Epic 4 - 補貨建議清單
FR20: Epic 4 - 補貨統計報表
FR21: Epic 4 - 匯出／列印補貨建議清單
FR22: Epic 1 - 銷貨員檔案（= 登入帳號的管理）
FR23: Epic 1 - 出庫單歸屬銷貨員（登入身分自動帶入）
FR24: Epic 4 - 銷貨員業績統計與排名（以登入帳號為母體）
FR25: Epic 4 - 業績明細下鑽
FR26: Epic 4 - 匯出業績報表
FR27: Epic 1 - 建立第一個管理員
FR28: Epic 1 - 登入、登出與取得目前使用者
FR29: Epic 1 - 管理員建立與管理帳號
FR30: Epic 1 - 依角色限制操作
FR31: Epic 1 - 記錄者與歸屬自動帶入登入身分
```

**AR 與 UX-DR 覆蓋**

| 需求 | 落在哪個 epic |
|---|---|
| AR-1 ～ AR-3、AR-7、AR-10、AR-13（領域規則、append-only、單據來源、型別、命名） | Epic 2（寫入主戰場）＋ Epic 3（稽核）＋ 全 epic 通用 |
| AR-4（單據＝交易）、AR-19（設定） | Epic 1（基礎設施）＋ Epic 2 |
| AR-5（補貨即時衍生） | Epic 4 |
| AR-6（業績以出庫單為母體） | Epic 4 |
| AR-8（密碼不落地）、AR-11（schema 唯一來源）、AR-9（API 形狀）、AR-15、AR-16、AR-17、AR-18、AR-19、AR-22 | Epic 1（基礎設施）＋ 全 epic 通用 |
| AR-12（前端不持有業務規則）、AR-21（前端慣例） | 全 epic（尤其 Epic 2、Epic 4） |
| AR-14（技術棧版本）、AR-20（測試佈局）、AR-23（備份） | Epic 1 |
| UX-DR1、UX-DR2、UX-DR9、UX-DR11、UX-DR12、UX-DR13、UX-DR14、UX-DR15 | 全 epic（呈現與可及性規範） |
| UX-DR3、UX-DR16 | Epic 1（畫面骨架、導覽、確認對話框） |
| UX-DR4、UX-DR6、UX-DR7、UX-DR8 | Epic 2、Epic 3（單據與清單的表單行為） |
| UX-DR5 | Epic 2 Story 2.3（盤點） |
| UX-DR10 | Epic 4（補貨建議呈現） |

## Epic List

> 交付方案 A：**4 個 epic，一次交付完整閉環**（2026-10-21 使用者核定）。epic 依使用者工作流分組，不依技術層；稽核紀律以橫切約束（AD-1／AD-2）與 story 內 AC 落實，不另立技術型 epic。

### Epic 1: 系統地基、使用者登入與品項主檔

使用者能以帳號登入這套系統（每筆操作留下真實身分），在這台電腦上把系統跑起來、讓資料庫可以從零重建，並建立與管理所有品項（後續所有進銷存、盤點、補貨、業績都以品項為對象）。

**FRs covered:** FR1, FR2, FR3

**Additional requirements:** AR-4（單據＝交易的事務基礎）、AR-8、AR-11、AR-14、AR-15、AR-17、AR-18、AR-19、AR-20、AR-22、AR-23、UX-DR3、UX-DR16

**Notes:** 本 epic 的 Story 1.1 是架構 spine 指定的 starter（專案初始化與遷移腳本），包在「能建立品項」這個使用者價值之下，不單獨成技術型 epic。

### Epic 2: 收貨、銷貨與盤點

使用者能收貨入庫、銷貨出庫、月底盤點並為差異留下原因——每一筆數量變動都留下可追溯的紀錄。

**FRs covered:** FR4, FR5, FR6, FR7, FR8, FR11, FR12, FR13

**Additional requirements:** AR-1、AR-2、AR-3、AR-4、AR-7、AR-10、AR-13、UX-DR4、UX-DR5、UX-DR6、UX-DR7、UX-DR8

**Notes:** Story 順序為 2.1 入庫 → 2.2 沖銷（機制先立起來）→ 2.3 出庫 → 2.4 盤點；盤點雖排在最後但仍在 M1 內完成驗證。Story 2.4 為沖銷更正（FR6）。

### Epic 3: 庫存查詢、警示與數字追溯

使用者能隨時查到每個品項的庫存現量、看到哪些快見底，並追查任何一個數字是怎麼來的——而且沒有任何紀錄可以被事後修改。

**FRs covered:** FR9, FR10, FR14, FR15

**Additional requirements:** AR-1、AR-2、AR-13、UX-DR1、UX-DR2、UX-DR7、UX-DR9、UX-DR15

**Notes:** 本 epic 是「信任層」——FR15（不可竄改）在此集中驗證，但 AD-2 同時是 Epic 2 每個寫入 story 的 AC，不等到本 epic 才生效。

### Epic 4: 管理層要的答案——補貨建議、銷貨員業績與報表

管理者（店主）不必靠記憶或翻發票，就能知道接下來哪些品項要補貨、該補多少、每位銷貨員賣了多少，以及這個月進多少出多少、庫存佔多少資金。

**FRs covered:** FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26

**Additional requirements:** AR-5、AR-6、AR-9、AR-10、AR-13、AR-21、UX-DR1、UX-DR10、UX-DR11、UX-DR15

**Notes:** 依使用者 2026-10-21 決定，補貨判斷與銷貨員業績**納入 MVP**（不延到第二階段），因為這是使用者最明確點名的兩個管理層需求。業績數字為自報性質，UX-DR11 要求頁面與匯出檔都標註「自報資料，非稽核結果」。

---

## Epic 1: 系統地基、使用者登入與品項主檔

使用者能以帳號登入這套系統（每筆操作留下真實身分），在這台電腦上把系統跑起來、讓資料庫可以從零重建，並建立與管理所有品項（後續所有進銷存、盤點、補貨、業績都以品項為對象）。

**FRs covered:** FR1, FR2, FR3, FR22, FR23, FR27, FR28, FR29, FR30, FR31
**AR／UX-DR relevant:** AR-4, AR-8, AR-11, AR-14, AR-15, AR-17, AR-18, AR-19, AR-20, AR-22, AR-23, AR-24 ～ AR-27, UX-DR3, UX-DR16

### Story 1.1: 一鍵啟動的系統與可重建的資料庫

身為**系統使用者**，
我希望**在這台電腦上用一個指令就能啟動整套系統，且資料庫可以從空庫一鍵重建**，
以便**我不必先手動設定環境或手刻資料表，之後換台電腦也能重建出同樣的資料結構**。

**Acceptance Criteria:**

**Given** 尚未建立任何資料表，`ailearn` 資料庫為空
**When** 執行遷移指令（`flask db upgrade`）
**Then** 依序建立 products、stock、stock_movements、documents、document_items、salespersons 六張表與 PRD 附錄 D 指定的索引
**And** 再次執行同一指令不會報錯、不會重建資料（遷移可重入）

**Given** 尚未設定環境變數
**When** 啟動 Flask 應用程式
**Then** 應用程式讀取 `DATABASE_URL` 等環境變數；若未設定則以明確錯誤訊息停止，並在訊息中說明要設定哪一個變數
**And** 任何設定檔、原始碼、`alembic.ini` 中都不含明文密碼（AR-8）

**Given** 應用程式已啟動
**When** 請求 `GET /api/health`
**Then** 回應 200 與 `{ "status": "ok", "database": "ok" }`；資料庫無法連線時回應 503 並標示 `database: "error"`

**Given** 前端尚未安裝
**When** 執行 `npm install` 後啟動 `npm run dev`
**Then** Vite dev server 在 5173 啟動，前端頁面可開啟，且 `/api` 請求被 proxy 至 5000
**And** 執行 `npm run build` 產生 `dist/`，Flask 能以單一網址同時提供 API 與該靜態檔（AR-18）

**Given** 使用者是第一次在本專案工作
**When** 閱讀 `README.md`
**Then** 文件包含：環境需求、建置指令、啟動指令（開發期雙終端機與正式單一指令）、遷移指令、常見錯誤排除
**And** 文件中不含任何密碼

**Requirements:** AR-8, AR-11, AR-14, AR-15, AR-17, AR-18, AR-19, AR-23, NFR-1, NFR-2

### Story 1.2: 建立第一個管理員

身為**系統管理者**，
我希望**用一個指令建立第一個管理員帳號**，
以便**有人能登入並開始管理其他帳號**。

**Acceptance Criteria:**

**Given** 資料庫中尚無任何管理員
**When** 執行 `flask create-admin`，依提示輸入帳號、姓名、密碼與密碼確認
**Then** 建立成功並輸出「管理員已建立：<username>」，該帳號可立即在網頁端登入

**Given** 密碼少於 8 碼，或兩次輸入不一致
**When** 送出
**Then** 拒絕建立，並分別說明「密碼至少 8 碼」與「兩次密碼不一致」

**Given** 資料庫中已存在管理員
**When** 再次執行 `flask create-admin`
**Then** 拒絕執行，提示「已有管理員，請用網頁端新增帳號」

**Given** 整個過程
**When** 檢查檔案、log 與輸出
**Then** 密碼沒有出現在任何檔案或 log 中（FR-27、NFR-10）

**Requirements:** FR-27, AR-24, AR-25

### Story 1.3: 登入與登出

身為**使用者**，
我希望**用帳號與密碼登入**，
以便**系統知道我 是誰，紀錄才會有憑據**。

**Acceptance Criteria:**

**Given** 有效的帳號與密碼
**When** 在登入頁送出
**Then** 登入成功並導向品項頁；畫面右上顯示目前登入者的姓名與角色

**Given** 密碼錯誤或帳號不存在
**When** 送出
**Then** 回 401 並顯示「帳號或密碼錯誤」（不透露是哪一項錯誤）

**Given** 帳號已停用
**When** 嘗試登入
**Then** 拒絕登入並顯示「此帳號已停用，請聯絡管理員」

**Given** 已登入
**When** 點「登出」
**Then** session 清除，回到登入頁；之後呼叫受保護端點回 401

**Given** 未登入者直接開啟受保護頁面
**When** 前端載入
**Then** 導向登入頁，記住原本要去的網址，登入後回到原處

**Requirements:** FR-28, AR-24, AR-26, NFR-10

### Story 1.4: 依角色限制操作

身為**系統管理者**，
我希望**不同角色只能做該做的事**，
以便**唯讀的人不會誤改資料、店員不會誤開盤點單**。

**Acceptance Criteria:**

**Given** 唯讀帳號
**When** 呼叫任何寫入端點（入庫、出庫、盤點、品項異動、帳號管理）
**Then** 回 403，訊息說明「唯讀帳號不能進行此操作」

**Given** 銷貨員帳號
**When** 呼叫入庫或盤點端點
**Then** 回 403，訊息說明該角色不可執行此操作

**Given** 倉管帳號
**When** 呼叫帳號管理端點
**Then** 回 403

**Given** 未登入者
**When** 呼叫任何受保護端點
**Then** 回 401

**Given** 權限檢查
**When** 檢視後端實作
**Then** 權限判斷集中在同一個守門模組，沒有一個端點自行判斷（AD-14）

**Requirements:** FR-30, AR-26

### Story 1.5: 管理員管理帳號

身為**管理員**，
我希望**建立、停用帳號並調整角色**，
以便**誰能操作這套系統由我決定**。

**Acceptance Criteria:**

**Given** 管理員在「使用者管理」頁
**When** 新增帳號（帳號、姓名、密碼、角色）
**Then** 建立成功並出現在清單中；帳號重複時拒絕並指出重複對象

**Given** 任一帳號
**When** 停用
**Then** 該帳號無法再登入（訊息「此帳號已停用」），但其歷史異動、單據與業績仍可查詢

**Given** 任一帳號
**When** 調整角色
**Then** 下次登入即套用新角色

**Given** 管理員要重設某人的密碼
**When** 設定新密碼
**Then** 該使用者可用新密碼登入；密碼同樣以雜湊儲存

**Given** 管理員想停用或降級自己
**When** 嘗試
**Then** 系統拒絕並說明「不能變更自己的權限，以免把系統鎖死」

**Given** 非管理員
**When** 呼叫帳號管理端點
**Then** 回 403，且回應不透露帳號是否存在

**Requirements:** FR-29, AR-25, AR-26, NFR-10

### Story 1.6: 記錄者與歸屬自動帶入登入身分

身為**店主**，
我希望**每一筆紀錄都自動記下是誰做的**，
以便**稽核與業績都可信，不會被填錯**。

**Acceptance Criteria:**

**Given** 已登入的使用者
**When** 建立入庫單（即使前端夾帶他人的記錄者值）
**Then** 單據的記錄者一律是登入帳號，前端傳入的值被忽略（AD-16）

**Given** 銷貨員角色
**When** 開出出庫單
**Then** 銷貨員歸屬自動是自己，不需挑選

**Given** 管理員角色
**When** 開出出庫單
**Then** 可指定另一位銷貨員歸屬，指定後該筆計入對方業績

**Given** 業績統計
**When** 檢視
**Then** 母體為登入帳號，正常情況下不再出現「未歸屬銷售」

**Requirements:** FR-31, FR-23, AR-27, AD-16

### Story 1.7: 建立品項

身為**倉管人員**，
我希望**建立品項主檔（sku、名稱、分類、單位、單價、安全庫存、補貨前置天數）**，
以便**之後的入庫、出庫、盤點都可以直接選擇品項，不必每次重新輸入**。

**Acceptance Criteria:**

**Given** 尚未建立任何品項
**When** 在「品項」頁按「＋ 新增品項」，填入 sku `A-001`、名稱「可樂 500ml」、分類「飲料」、單位「瓶」、單價 `25`、安全庫存 `20`、補貨前置天數 `7` 後送出
**Then** 建立成功，畫面提示「品項已建立：可樂 500ml」，並回到清單且新項目可見
**And** 該品項的庫存現量為 0（顯示為 0，不是空白）

**Given** 已存在 sku `A-001`
**When** 再次建立 sku 為 `A-001` 的品項
**Then** 拒絕送出，錯誤訊息為「sku A-001 已存在（可樂 500ml），請改用其他 sku」並指出重複對象

**Given** 名稱或 sku 留空
**When** 送出
**Then** 拒絕送出並標示缺漏欄位，訊息說明是哪一个欄位缺漏

**Given** 單價填 0 或留白
**When** 送出
**Then** 允許送出，單價視為 0，且不阻擋流程

**Given** 補貨前置天數留空
**When** 送出
**Then** 預設為 7 天（品項層級，OQ-11 決議）

**Given** 送出時發生伺服器錯誤
**When** 畫面顯示錯誤
**Then** 已輸入的內容保留不變，並提供「重試」（UX-DR6）

**Requirements:** FR1, AR-7, AR-13, UX-DR1, UX-DR6, UX-DR7, UX-DR8

### Story 1.8: 查詢與篩選品項

身為**倉管人員**，
我希望**用關鍵字、分類或啟用狀態快速找到品項**，
以便**在需要時立刻取得正確的品項資訊，而不用在一長串清單裡翻找**。

**Acceptance Criteria:**

**Given** 已有 30 筆品項，其中 3 筆名稱含「可樂」
**When** 在搜尋框輸入「可樂」
**Then** 只顯示名稱或 sku 部分相符的品項，結果依建立順序穩定排序
**And** 搜尋條件反映在網址（如 `/products?keyword=可樂`），可直接分享或重新整理

**Given** 搜尋條件篩選後沒有結果
**When** 畫面更新
**Then** 顯示空狀態「沒有符合『可樂』的品項。」並附「清除條件」動作（UX-DR7）

**Given** 品項數量超過 50 筆
**When** 開啟清單
**Then** 以分頁呈現，每頁 50 筆，上限 100 筆（AR-9）

**Given** 清單中包含數量、單價欄位
**When** 顯示表格
**Then** 數量與單價欄位右對齊並使用等寬數字，金額固定兩位小數（UX-DR1）

**Requirements:** FR2, AR-9, UX-DR1, UX-DR7

### Story 1.9: 修改與停用品項

身為**倉管人員**，
我希望**修改品項資訊，或把不再使用的品項停用**，
以便**清單不會越來越雜亂，同時不會誤刪掉歷史資料**。

**Acceptance Criteria:**

**Given** 一個品項
**When** 修改名稱或安全庫存後儲存
**Then** 變更立即生效，且異動紀錄中的歷史資料仍保留原名稱

**Given** 一個尚未被任何單據引用的品項
**When** 按「刪除」
**Then** 允許刪除，確認後從清單移除

**Given** 一個已被庫存異動引用過的品項
**When** 嘗試刪除
**Then** 拒絕刪除並顯示「此品項已有庫存異動紀錄，請改用停用」

**Given** 停用品項
**When** 送出停用
**Then** 跳出 Modal 確認（不可逆操作，UX-DR16）
**And** 停用後該品項不出現在新建單據的品項選擇清單中，但歷史庫存異動與業績仍可查詢
**And** 清單中可篩選出「已停用」品項

**Requirements:** FR3, UX-DR7, UX-DR16

---

## Epic 2: 收貨、銷貨與盤點

使用者能收貨入庫、銷貨出庫、月底盤點並為差異留下原因——每一筆數量變動都留下可追溯的紀錄。

**FRs covered:** FR4, FR5, FR6, FR7, FR8, FR11, FR12, FR13
**AR／UX-DR relevant:** AR-1, AR-2, AR-3, AR-4, AR-7, AR-10, AR-13, UX-DR4, UX-DR5, UX-DR6, UX-DR7, UX-DR8

### Story 2.1: 收貨入庫

身為**倉管人員**，
我希望**把收到的貨一次登錄成多品項的入庫單並送出**，
以便**收貨當下庫存現量就正確，不用事後再改 Excel**。

**Acceptance Criteria:**

**Given** 品項「可樂 500ml」庫存現量 24
**When** 建立入庫單，單號 `IN-20261021-001`、備註「供應商 A 到貨」，明細輸入 36 瓶 × 25 元並送出
**Then** 庫存現量變為 60，且畫面顯示「入庫成功：可樂 500ml，庫存 24 → 60」
**And** 產生 1 筆 move_type = `IN` 的庫存異動，帶有 document_id、單據號、記錄者與送出後的庫存現量（balance_after = 60）

**Given** 一張入庫單有多個品項
**When** 送出
**Then** 所有品項的庫存現量在同一個資料庫交易內更新；任一明細失敗則整批 rollback，不留下部分成功的資料（AR-4）

**Given** 明細數量填 0 或負數
**When** 送出
**Then** 拒絕送出，錯誤標示在該列並指明是哪一列

**Given** 明細中同一品項出現兩列
**When** 送出
**Then** 系統合併為一筆或要求合併後才可送出（行為由架構文件固定，兩者皆可測試）

**Given** 送出成功
**When** 畫面更新
**Then** 表單清空但停留在原頁，記錄者與日期保留，方便連續登錄下一張（UX-DR4）

**Given** 使用者在明細列輸入數量
**When** 按 Enter
**Then** 自動新增下一列並聚焦在品項欄（連續登錄路徑，UX-DR4）

**Given** 頁面載入中或表單送出中
**When** 使用者重複點擊送出
**Then** 按鈕進入 loading 並停用，不會產生兩張單（UX-DR8）

**Given** 任意時間
**When** 查詢該品項的入庫歷史
**Then** 可依時間、品項、單號查到入庫紀錄，並可由紀錄反查原單據（FR5）

**Requirements:** FR4, FR5, AR-1, AR-2, AR-3, AR-4, AR-7, AR-10, UX-DR4, UX-DR6, UX-DR7, UX-DR8


### Story 2.2: 沖銷更正已送出的單據

身為**店主**，
我希望**用一筆反向紀錄更正送錯的入庫單，而不是直接改掉或刪除原單**，
以便**所有更正都留得下痕跡，數字依然可以追溯**。

**Acceptance Criteria:**

**Given** 一張已送出的入庫單（36 瓶，庫存 24 → 60）
**When** 執行「沖銷此單」並填入原因「供應商多送 2 箱，實際只需 34 瓶」後確認
**Then** 產生一筆方向相反的庫存異動，庫存現量回到 24
**And** 新異動的 correction_of_movement_id 指向被沖銷的異動，兩筆互相可追溯
**And** 原始單據與沖銷紀錄都保留，不刪除任何一邊（AR-2）

**Given** 執行沖銷
**When** 確認前
**Then** 跳出 Modal 確認並要求輸入原因（不可逆的稽核行為，UX-DR16）

**Given** 已被沖銷的單據
**When** 再次檢視
**Then** 顯示「已沖銷」狀態標籤與沖銷原因，原始數字仍完整保留

**Given** 系統中沒有任何沖銷功能
**When** 嘗試修改或刪除已產生的庫存異動
**Then** 沒有任何介面或端點可以做到這件事（AD-2）

**Requirements:** FR6, AR-2, AR-3, AR-13, UX-DR16

> **範圍說明：** 本 story 先建立沖銷機制（v1 以入庫單為實作對象，FR6 範圍）；出庫單與盤點單沿用同一機制，於後續 story 直接適用。

---


### Story 2.3: 銷貨出庫

身為**店員**，
我希望**登錄賣出／領用／報廢的數量，並在庫存不足時被立即擋下**，
以便**不會賣出我自己都不知道有多少的貨**。

**Acceptance Criteria:**

**Given** 品項「可樂 500ml」庫存現量 60
**When** 建立出庫單，用途「銷售」，數量 12，指定銷貨員「小美」並送出
**Then** 庫存現量變為 48，畫面顯示「出庫成功：可樂 500ml，庫存 60 → 48」
**And** 產生 1 筆 move_type = `OUT` 的庫存異動，關聯到該出庫單

**Given** 出庫數量 20、庫存現量 12
**When** 送出
**Then** 拒絕送出，錯誤訊息為「無法送出：可樂 500ml 庫存不足，目前 12、需 20。先入庫或改數量。」且表單內容不清空（UX-DR6）

**Given** 銷貨員角色登入
**When** 送出用途為「銷售」的出庫單
**Then** 銷貨員歸屬自動帶入登入身分，不需挑選（FR-31、AD-16）
**And** 即使前端夾帶他人歸屬值也不影響結果

**Given** 用途為「領用」或「報廢」
**When** 送出
**Then** 允許送出；此筆不計入任何人的業績（FR23）

**Given** 出庫單已送出
**When** 再次檢視該單
**Then** 以唯讀模式顯示，不提供編輯或刪除（更正一律走 Story 2.2 的沖銷機制）

**Given** 任意時間
**When** 查詢出貨歷史（可依時間、品項、用途、銷貨員篩選）
**Then** 結果的數字與進銷存概況報表在同一區間的出庫合計一致（FR8）

**Requirements:** FR7, FR8, AR-1, AR-3, AR-4, AR-7, AR-10, UX-DR4, UX-DR6, UX-DR8


### Story 2.4: 月底盤點與差異原因

身為**店主**，
我希望**在盤點時輸入實盤數，並為每個差異留下原因**，
以便**知道數字為什麼對不上、錯在哪，而不是憑印象直接改掉**。

**Acceptance Criteria:**

**Given** 品項「可樂 500ml」帳面 60
**When** 在盤點單輸入實盤數 57
**Then** 該列即時顯示「盤虧 3」（帳面 60、實盤 57），並出現必填的差異原因欄

**Given** 差異原因提供固定選項
**When** 選擇其中一項
**Then** 選項包含：損壞／報廢、被取用未登記、搬運損失、其他；選「其他」時需補自由文字

**Given** 盤點單有 12 個品項、2 個差異、1 個已填原因
**When** 檢視畫面頂部
**Then** 顯示「共 12 個品項、差異 2 個、已填原因 1 個」（UX-DR5）

**Given** 仍有差異未填原因
**When** 按「送出盤點單」
**Then** 送出被阻擋，顯示警示條「還有 1 個品項沒填差異原因，補完才能送出。」並捲動定位到第一個缺原因的列（UX-DR5）

**Given** 所有差異都已填原因
**When** 送出
**Then** 產生對應的 move_type = `ADJUST` 異動（含盤點單號與原因），各品項庫存現量更新為實盤數
**And** 畫面提示「盤點完成：2 個品項差異已記錄（盤盈 1、盤虧 1）。」

**Given** 盤點單已送出
**When** 再次檢視
**Then** 唯讀不可修改；更正方式為另開新盤點單（沖銷機制見 Story 2.2）

**Given** 任意時間
**When** 開啟「盤點差異報表」並依品項或時間區間查詢
**Then** 顯示品項、盤點時間、帳面數、實盤數、差異量、原因、盤點單號，且同一品項的歷次紀錄可依時間排序，便於看出反覆差異（FR13）

**Requirements:** FR11, FR12, FR13, AR-2, AR-3, AR-4, AR-7, UX-DR5, UX-DR7



## Epic 3: 庫存查詢、警示與數字追溯

使用者能隨時查到每個品項的庫存現量、看到哪些快見底，並追查任何一個數字是怎麼來的——而且沒有任何紀錄可以被事後修改。

**FRs covered:** FR9, FR10, FR14, FR15
**AR／UX-DR relevant:** AR-1, AR-2, AR-13, UX-DR1, UX-DR2, UX-DR7, UX-DR9, UX-DR15

### Story 3.1: 查詢庫存現量

身為**倉管人員**，
我希望**隨時查到每個品項現在有多少**，
以便**有人問「還有多少」的時候可以立刻回答，不用去翻紙本**。

**Acceptance Criteria:**

**Given** 已有品項與其異動
**When** 開啟「庫存查詢」
**Then** 每列顯示品項、庫存現量、安全庫存、更新時間
**And** 顯示值與資料庫 `stock.qty` 完全一致（以 SQL 比對驗收，FR9）

**Given** 某品項從未發生任何異動
**When** 顯示清單
**Then** 庫存現量顯示為 0，不是空白

**Given** 清單有 1,000 筆品項、10,000 筆異動
**When** 查詢
**Then** 回應時間不超過 2 秒（NFR-3）

**Given** 清單含有數量欄位
**When** 顯示
**Then** 右對齊、等寬數字；負數以 error 色並加「負庫存」標籤（UX-DR1, UX-DR9）

**Requirements:** FR9, AR-1, UX-DR1, UX-DR9

### Story 3.2: 低庫存警示清單

身為**倉管人員**，
我希望**一眼看到哪些品項快見底、還差多少**，
以便**安排補貨時不用逐項比對**。

**Acceptance Criteria:**

**Given** 品項 A 現量 5、安全庫存 20；品項 B 現量 30、安全庫存 20；品項 C 安全庫存 0
**When** 開啟低庫存警示清單
**Then** 只列出品項 A，顯示現量 5、安全庫存 20、缺口 15
**And** 品項 C（安全庫存 = 0）不出現在清單中（FR10）
**And** 已停用品項不出現在清單中

**Given** 清單有內容
**When** 顯示
**Then** 頁面頂部出現橘色警示條並列出品項與缺口；表格內以標籤標示，不整頁變色（UX-DR9）

**Given** 品項入庫補足後
**When** 重新查詢
**Then** 該品項不再出現在警示清單中

**Requirements:** FR10, UX-DR2, UX-DR9

### Story 3.3: 庫存異動明細與追溯

身為**店主**，
我希望**查得到某個品項的每一筆數量變化**，
以便**被問到數字時可以說清楚來歷**。

**Acceptance Criteria:**

**Given** 品項「可樂 500ml」有入庫、出庫、盤點差異共 5 筆異動
**When** 查詢該品項的異動明細
**Then** 依時間列出每筆異動：時間、品項、類型、數量、當時庫存現量（balance_after）、單據號、備註、記錄者
**And** 依序套用這些異動的累加結果等於目前的庫存現量（可重算驗收，FR14）

**Given** 異動清單
**When** 篩選
**Then** 可依品項、類型（入庫／出庫／盤點差異）、時間區間篩選

**Given** 異動明細
**When** 顯示數字欄位
**Then** 數量右對齊並使用等寬數字（UX-DR1）

**Given** 異動清單
**When** 按「匯出 CSV」
**Then** 匯出檔案的列數與畫面結果列數一致、欄位順序固定，且以 Excel 開啟中文不亂碼（FR16、UX-DR15）

**Requirements:** FR14, FR16, AR-2, AR-9, UX-DR1, UX-DR15

### Story 3.4: 異動紀錄不可竄改

身為**店主**，
我希望**任何人都不能事後修改或刪除已經產生的庫存異動**，
以便**稽核軌跡完整可信**。

**Acceptance Criteria:**

**Given** 資料庫中已存在庫存異動
**When** 以任何介面或端點嘗試 UPDATE 或 DELETE 該筆異動
**Then** 系統拒絕並保留原紀錄（AD-2）

**Given** 一筆需要更正的異動
**When** 檢視該筆異動
**Then** 畫面提供「沖銷」入口（走 Story 2.2 的流程），而非「編輯」或「刪除」

**Given** 資料庫層級
**When** 檢視 stock_movements 的存取規則
**Then** 應用層不提供任何異動修改或刪除的 API 端點

**Requirements:** FR15, AR-2

---

## Epic 4: 管理層要的答案——補貨建議、銷貨員業績與報表

管理者（店主）不必靠記憶或翻發票，就能知道接下來哪些品項要補貨、該補多少、每位銷貨員賣了多少，以及這個月進多少出多少、庫存佔多少資金。

**FRs covered:** FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26
**AR／UX-DR relevant:** AR-5, AR-6, AR-9, AR-10, AR-13, AR-21, UX-DR1, UX-DR10, UX-DR11, UX-DR15

### Story 4.1: 進銷存概況與庫存總值

身為**店主**，
我希望**看某個時間區間的進銷存概況與目前庫存佔了多少資金**，
以便**調整下個月的進貨量**。

**Acceptance Criteria:**

**Given** 2026-10 區間內某品項期初 24、入庫 36、出庫 12、盤點差異 −3
**When** 產生進銷存概況報表
**Then** 期末顯示 45，且等於「期初 + 入庫 − 出庫 + 盤點差異」（可重算驗收，FR17）

**Given** 報表含金額
**When** 顯示
**Then** 金額以「數量 × 單價」計算並顯示兩位小數；API 以字串回傳金額（AR-10）

**Given** 選擇的區間內沒有任何異動
**When** 開啟報表
**Then** 顯示「2026-10-01 ～ 2026-10-31：此區間無資料」，不是空白頁（UX-DR7）

**Given** 開啟「庫存總值」
**When** 顯示
**Then** 列出各品項現量 × 單價與總計，總計與逐品項加總一致，並可依金額或數量排序（FR18）

**Requirements:** FR17, FR18, AR-9, AR-10, UX-DR1, UX-DR7

### Story 4.2: 銷貨員業績統計與明細

身為**店主**，
我希望**看到每位銷貨員在期間內賣了什麼、多少件、多少金額，並能下鑽到明細**，
以便**了解各人貢獻並安排排班**。

**Acceptance Criteria:**

**Given** 期間內 3 位銷貨員有銷售紀錄
**When** 開啟業績頁（期間預設「本月」）
**Then** 每位顯示銷售金額、件數、品項數，依銷售金額排序，可切換以件數排序（FR24）
**And** 期間內沒有銷售紀錄的銷貨員仍列出，顯示 0，不從清單消失

**Given** 歸屬一律來自登入身分
**When** 顯示頁面
**Then** 正常情況下不出現「未歸屬銷售」警示；僅當管理員手動指定他人歸屬時才有例外（UX-DR11、FR-31）

**Given** 業績頁
**When** 檢視
**Then** 頁面標註「歸屬來自登入帳號」，取代原本的「自報資料」標示（UX-DR11、FR-31）

**Given** 點擊某位銷貨員
**When** 進入明細
**Then** 列出每筆銷售的日期、單號、品項、數量、單價、金額，並可連結回原出庫單
**And** 明細加總必須等於彙總數字（可重算驗收，FR25）

**Given** 銷售金額的計算
**When** 檢視
**Then** 金額 = 銷售用途出庫數量 × 該品項單價；盤點差異、報廢、領用不計入（A-20、AR-6）

**Requirements:** FR24, FR25, AR-6, AR-9, AR-10, UX-DR1, UX-DR11

### Story 4.3: 補貨建議清單

身為**店主**，
我希望**看到依近期銷售速度算出的補貨建議（哪些品項要補、補多少）**，
以便**不再憑印象訂貨，避免缺貨與滯銷**。

**Acceptance Criteria:**

**Given** 品項「優酪乳 500ml」安全庫存 10、補貨前置天數 7、最近 30 天出庫 90 瓶、庫存現量 12
**When** 開啟補貨判斷，計算區間選 30 天
**Then** 建議清單列出該品項：現量 12、安全庫存 10、日均消耗 3.0（90 ÷ 30）、建議進貨量 19（＝ max(0, 10 + 3.0 × 7 − 12)）
**And** 該值可由畫面上的數字手算重現（SM-8、AR-5）

**Given** 庫存現量足以撐過補貨前置天數
**When** 計算建議
**Then** 該品項不出現在建議清單中

**Given** 某品項在計算區間內完全沒有出庫紀錄
**When** 計算建議
**Then** 不列入建議清單，改列於「無消耗資料（可能滯銷）」清單（FR19）

**Given** 切換計算區間（7／30／90 天）
**When** 重新計算
**Then** 建議清單內容隨區間改變而改變

**Given** 開啟補貨頁
**When** 檢視畫面
**Then** 表頭固定顯示「計算區間」「補貨前置天數（依各品項設定）」「計算時間」，使用者不會誤認數字（UX-DR10）

**Given** 需要把清單交給跑商
**When** 按「匯出 CSV」
**Then** 匯出檔案包含品項、庫存現量、日均消耗、建議進貨量，且**檔案內標註計算區間與前置天數**（FR21、UX-DR10）

**Given** 系統持續運作
**When** 多次查詢建議
**Then** 每次都即時由原始異動重算，沒有快取或落地表格（AR-5）

**Requirements:** FR19, FR21, AR-5, AR-9, UX-DR10, UX-DR15

### Story 4.4: 補貨統計報表

身為**店主**，
我希望**看到每個品項在一段期間內的進貨、消耗、補貨次數**，
以便**判斷補貨節奏是否合理**。

**Acceptance Criteria:**

**Given** 某品項在區間內入庫 3 張單共 200 件、出庫 150 件
**When** 開啟補貨統計
**Then** 顯示入庫量 200、出庫量 150、期末 = 期初 + 入庫 − 出庫 + 盤點差異、消耗速度、補貨次數 = 3（依入庫**單據張數**計，不以異動列數計，FR20）

**Given** 補貨統計包含平均庫存
**When** 顯示
**Then** 以「(期初 + 期末) ÷ 2」近似計算，並標示為近似值

**Given** 補貨統計
**When** 顯示
**Then** 可依分類彙總並匯出 CSV

**Requirements:** FR20, AR-5, AR-6, AR-9, AR-10

### Story 4.5: 統一 CSV 匯出

身為**使用者**，
我希望**所有清單與報表都能匯出成 Excel 可以直接開啟的 CSV**，
以便**交給別人、貼到報告或自己再分析**。

**Acceptance Criteria:**

**Given** 任一清單頁或報表頁（品項、庫存、入庫、出庫、異動、報表、補貨建議、補貨統計、業績）
**When** 按「匯出 CSV」
**Then** 匯出內容與畫面篩選條件一致，欄位順序固定，列數與畫面結果一致（FR16、FR21、FR26、NFR-7）

**Given** 匯出檔案
**When** 以 Excel 開啟
**Then** 中文欄位與內容不亂碼（UTF-8 with BOM）

**Given** 匯出完成
**When** 畫面提示
**Then** 以 message 告知匯出的筆數（UX-DR15）

**Given** 當前有篩選條件
**When** 匯出
**Then** 匯出的是篩選後的結果，不是全部資料

**Requirements:** FR16, FR21, FR26, NFR-7, AR-9, UX-DR15
