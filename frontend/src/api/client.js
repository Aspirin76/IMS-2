/**
 * API 客戶端：唯一的資料取得管道（AD-12：前端不持有業務規則、不快取業務資料）。
 * 錯誤一律依 AD-9 的錯誤形狀 {error:{code,message,details}} 轉成例外。
 * 認證以 session cookie 進行，因此所有請求都帶 credentials（AD-14、NFR-10）。
 */

const BASE = '/api'

export class ApiError extends Error {
  constructor(code, message, details = {}, status = 0) {
    super(message)
    this.code = code
    this.details = details
    this.status = status
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (response.status === 204) return null

  let payload
  try {
    payload = await response.json()
  } catch {
    payload = null
  }

  if (!response.ok) {
    const error = payload?.error
    throw new ApiError(
      error?.code ?? 'UNKNOWN',
      error?.message ?? `請求失敗（HTTP ${response.status}）`,
      error?.details ?? {},
      response.status,
    )
  }
  return payload
}

export function buildQuery(params) {
  const search = new URLSearchParams()
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.set(key, value)
  })
  const query = search.toString()
  return query ? `?${query}` : ''
}

export const api = {
  health: () => request('/health'),

  // 認證（FR-28）
  login: (username, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/auth/me'),

  // 帳號管理（FR-29）
  listUsers: () => request('/users'),
  createUser: (payload) => request('/users', { method: 'POST', body: JSON.stringify(payload) }),
  updateUser: (id, payload) =>
    request(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  // 單據（FR-4、FR-5）
  createStockIn: (payload) =>
    request('/documents/stock-in', { method: 'POST', body: JSON.stringify(payload) }),
  listDocuments: (params) => request(`/documents${buildQuery(params)}`),
  getDocument: (id) => request(`/documents/${id}`),

  // 品項
  listProducts: (params) => request(`/products${buildQuery(params)}`),
  createProduct: (payload) =>
    request('/products', { method: 'POST', body: JSON.stringify(payload) }),
  updateProduct: (id, payload) =>
    request(`/products/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deleteProduct: (id) => request(`/products/${id}`, { method: 'DELETE' }),
}
