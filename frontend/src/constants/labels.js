/**
 * 中文顯示名稱集中管理（AD-13 / UX-DR：不得散落各頁硬寫）。
 * 一律沿用 PRD 詞彙表，不另創同義詞。
 */

export const LABELS = {
  product: '品項',
  products: '品項',
  stock: '庫存現量',
  stockIn: '入庫',
  stockOut: '出庫',
  stocktake: '盤點',
  movement: '庫存異動',
  replenishment: '補貨判斷',
  performance: '銷貨員業績',
  report: '報表',
  settings: '設定',

  sku: 'sku',
  name: '名稱',
  category: '分類',
  unit: '單位',
  price: '單價',
  safetyQty: '安全庫存',
  leadTimeDays: '補貨前置天數',
  isActive: '啟用',
}

export const MOVE_TYPE_LABEL = {
  IN: '入庫',
  OUT: '出庫',
  ADJUST: '盤點差異',
}
