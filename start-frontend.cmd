@echo off
rem 以 cp950 儲存，理由同 start-backend.cmd
setlocal
cd /d "%~dp0frontend"
echo.
echo 前端啟動中：http://localhost:5173
echo 關閉這個視窗即停止伺服器。
echo.
call npm run dev
