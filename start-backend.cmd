@echo off
rem 這個檔案以系統 ANSI 編碼（繁中 Windows = cp950/Big5）儲存，CMD 才能正確解析中文。
rem 因此不要再用 chcp 65001 切換編碼，否則中文會變成亂碼。
setlocal
cd /d "%~dp0backend"

set /p DB_PASSWORD=請輸入 PostgreSQL postgres 密碼:
if "%DB_PASSWORD%"=="" (
  echo 密碼不能空白，未啟動。
  pause
  exit /b 1
)

set "DATABASE_URL=postgresql+psycopg://postgres:%DB_PASSWORD%@localhost:5432/ailearn"
if "%APP_SECRET_KEY%"=="" echo [提示] 未設定 APP_SECRET_KEY：重新啟動後需要重新登入。

echo.
echo 後端啟動中：http://127.0.0.1:5000
echo 關閉這個視窗即停止伺服器。
echo.
..\.venv\Scripts\python.exe -m flask --app "app:create_app" run --port 5000
