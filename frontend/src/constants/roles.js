/** 角色名稱集中管理（AD-13 / UX-DR：不得散落各頁硬寫）。 */

export const ROLE = {
  ADMIN: 'admin',
  CLERK: 'clerk',
  SALESPERSON: 'salesperson',
  VIEWER: 'viewer',
}

export const ROLE_LABEL = {
  admin: '管理員',
  clerk: '倉管',
  salesperson: '銷貨員',
  viewer: '唯讀',
}

export const ROLE_COLOR = {
  admin: 'gold',
  clerk: 'green',
  salesperson: 'blue',
  viewer: 'default',
}

/** 可寫入（品項異動）的角色（FR-30） */
export const CAN_WRITE_STOCK = [ROLE.ADMIN, ROLE.CLERK]
