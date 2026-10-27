@echo off
REM ============================================================
REM  WorkBuddy Skills one-click sync (double-click to run)
REM  Logic lives in sync.ps1 (plain git, HTTP/1.1, no credential prompt)
REM  Flow: pull -> add -> commit -> push
REM ============================================================
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1"
echo.
echo [sync] Done. Press any key to close this window.
pause >nul
