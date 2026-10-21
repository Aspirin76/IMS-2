---
name: 庫存管理系統
status: final
updated: 2026-10-21
description: 單機版的進銷存與盤點工具，供小微倉庫與店務使用。Ant Design 6 / React 上層；本 DESIGN.md 僅定義品牌層增量，其餘繼承 Ant Design 預設值。
colors:
  # 品牌層僅覆寫 primary 與 accent；background / text / border / success / warning / error 等一律繼承 Ant Design 6 預設。
  primary: '#1F6F5C'
  primary-foreground: '#FFFFFF'
  primary-active: '#175646'
  accent: '#C2410C'
  accent-foreground: '#FFFFFF'
typography:
  # 內文、標籤、輔助文字繼承 Ant Design 6 預設字體（系統字體堆疊）。此處只定義「數字」這個專用角色。
  numeric:
    fontFamily: 'inherit'
    fontFeatureSettings: "'tnum' 1, 'lnum' 1"
    fontVariantNumeric: 'tabular-nums'
rounded:
  # 繼承 Ant Design 6 預設（6px / 8px），不做覆寫。
  sm: 6px
  md: 8px
spacing:
  # 繼承 Ant Design 8px 基準網格：8 / 16 / 24 / 32。
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
components:
  table-numeric-cell:
    textAlign: 'right'
    fontVariantNumeric: '{typography.numeric.fontVariantNumeric}'
  low-stock-alert:
    background: '{colors.accent}'
    foreground: '{colors.accent-foreground}'
    radius: '{rounded.md}'
  empty-state:
    textAlign: 'center'
    padding: '{spacing.lg}'
---

## Brand & Style

庫存管理系統是給**小微倉庫與店務現場**用的工具，不是給消費者看的產品。使用者多半一邊顧店一邊登記，螢幕常常被貨品、單據、還有旁邊的人擋住。因此這份品牌語言只有兩條：

1. **數字要能一眼信任** —— 金額與數量用等寬數字（tabular-nums）、右對齊、兩位小數固定，橫向掃過一列就像對帳一樣。
2. **紅色只留給「現在就要處理」** —— 琥珀橘（accent）不是裝飾色，只出現在庫存不足、盤點差異沒填原因、送出會被擋下這三種地方。

整體氣質是「安靜、可靠、算得出來」：白底、清楚的表格欄線、沒有漸層、沒有插畫、沒有鼓勵式文案。介面語言沿用 PRD 詞彙表——品項、庫存現量、入庫、出庫、盤點差異、補貨建議、業績，不另創同義詞。

Ant Design 6 負責 80% 的視覺（Table、Form、Modal、Alert、Tag、Empty、Statistic 等一律照預設），本文件只定義品牌層增量。**改 antd 預設值本身是違反品牌紀律的**——只有下列項目可以被覆寫。

## Colors

- **主色墨綠（`#1F6F5C` 亮 / `#175646` 深）** 是品牌色。用於主要按鈕、作用中的側邊選單項目、連結底線、頁面主標題旁的識別條。取代 antd 預設的 `primary`。取綠是因為「帳面對得上」在這個行業是好話，不是裝飾。
- **強調橘（`#C2410C` 亮 / 深色模式沿用同色）** 是警示色。**只有三種情況可以用**：庫存現量不足安全庫存、盤點差異尚未填寫原因、送出將被系統擋下。不可用於裝飾、hover 效果、一般標籤、成功訊息。
- **其餘所有 token**（`background`、`text`、`border`、`split`、`success`、`warning`、`error`、`info`、`fill`、`table-header` 等）一律繼承 Ant Design 6 預設。不為了好看而改。

避免：漸層、彩色陰影、超過兩個品牌色、把 `accent` 當一般標籤色、把紅色用在非阻擋性提示。

## Typography

內文、標題、標籤、輔助文字**全部繼承 Ant Design 6 預設字體與級距**。本專案只覆寫一個角色：

- **`numeric`** —— 所有數量、金額、日期數字、百分比。啟用 `tabular-nums`（等寬數字）與 `lnum`，讓同一欄的數字**小數點垂直對齊**。這是整份設計裡最重要的一條規則：使用者在對帳時靠的是「數字尾巴排整齊」，不是「字型好看」。
- 金額一律顯示兩位小數（`1250.00`），不省略、不縮寫為 `1.25K`。資料庫與 API 都是 `NUMERIC(10,2)`，顯示層不做二次四捨五入。

不要為了「看起來更有設計感」而把數字換成比例字型或不同字重。

## Layout & Spacing

- 繼承 antd 的 8px 基準網格（8 / 16 / 24 / 32）。頁面區塊間距 24px，區塊內元素間距 16px，表格列間距 8px。
- **固定左側導覽（200px）+ 右側內容區**。內容區最大寬度 `1440px`，表格類頁面允許滿寬（這是需要橫向比較數字的產品），表單類頁面限寬 `960px`，避免表單被拉到全螢幕而難以填寫。
- 表格預設每頁 50 筆、上限 100（與 API `page_size` 一致），分頁固定在表格下方右側。
- 單據表單（入庫／出庫／盤點）採「上方單據資訊、下方明細表」垂直結構，明細表可新增列，不使用多欄並排。
- 手機（< 768px）：導覽收成抽屜，表格改為可橫向捲動，**但表單送出一律不在手機執行**（見 EXPERIENCE.md）。

## Elevation & Depth

繼承 antd 預設：只有浮層（Modal、Dropdown、Popover）有陰影，頁面區塊之間**不用陰影**做層級，改用 1px 分隔線與留白。禁用「卡片浮在卡片上」的疊卡樣式。

## Shapes

繼承 antd 預設圓角（`sm` 6px、`md` 8px）。藥丸形狀（`border-radius: full`）**只**用於狀態標籤（例：低庫存、停用、未歸屬）。卡片與按鈕不使用藥丸形。

## Components

**沿用 antd 預設、不修改的元件**：`Table`、`Form`、`Input`、`InputNumber`、`Select`、`DatePicker`、`Modal`、`Drawer`、`Alert`、`Tag`、`Empty`、`Statistic`、`Tabs`、`Dropdown`、`Tooltip`、`message`、`Popconfirm`、`Descriptions`、`Space`、`Button`（除 primary 色與數字對齊外）。

**品牌層覆寫的元件**：

- **Table（數字欄位）** —— 數量、單價、金額、差異量欄一律 `text-align: right` ＋ `font-variant-numeric: tabular-nums`（`{typography.numeric.fontVariantNumeric}`）。文字欄位維持左對齊。表頭背景沿用 antd 預設，不加深。
- **Statistic（庫存現量）** —— 儀表板與庫存頁的大數字使用 `numeric` 角色；低於安全庫存時數字本身不變色，改由旁邊的 Alert 承載（避免整頁紅字）。
- **低庫存警示條（Alert）** —— 自訂樣式：`{colors.accent}` 背景、`{colors.accent-foreground}` 文字、`{rounded.md}` 圓角。只用在「現在就要處理」的三種情況。
- **Empty state** —— 置中、`{spacing.lg}` 內距；文案固定格式「{事實}。{下一步一句話}。」並附一個主要動作按鈕（例：「還沒有品項。先建立一個品項，才能登記入庫。」）。
- **Tag（庫存狀態）** —— 低於安全庫存用 `accent`；已停用品項用 antd 預設 `default`；銷貨員「未歸屬」用 antd 預設 `warning`。

## Do's and Don'ts

| Do | Don't |
| --- | --- |
| 數字用 `{typography.numeric}`（等寬、右對齊、兩位小數） | 數字左對齊、字型不一致、小數位數省略 |
| `{colors.accent}` 只用在需立即行動的三種情況 | 用 accent 做裝飾、hover、成功訊息、一般標籤 |
| 錯誤訊息說明「為什麼不行」與「該怎麼做」 | 只寫「操作失敗」「錯誤」 |
| 表格用 1px 分隔線與留白分層 | 用陰影堆疊卡片 |
| 沿用 PRD 詞彙表命名所有欄位與按鈕 | 同一個東西出現兩種說法（品項／商品／貨品） |
| 讓「查無資料」成為正常狀態並給出下一步 | 空白表格或紅色錯誤框 |
