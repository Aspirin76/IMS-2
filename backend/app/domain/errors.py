"""領域層錯誤。所有業務規則違反都從這裡拋出，由 API 層統一轉成錯誤形狀（AD-7 / AD-9）。"""


class DomainError(Exception):
    """業務規則違反。

    code 對應 API 的錯誤代碼，例如 STOCK_INSUFFICIENT、SKU_DUPLICATED。
    status 為對應的 HTTP 狀態碼（400 驗證、404 不存在、409 狀態衝突、422 領域規則）。
    """

    def __init__(self, code: str, message: str, details: dict | None = None, status: int = 422):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.status = status
