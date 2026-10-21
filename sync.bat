@echo off
REM ============================================================
REM  WorkBuddy Skills 一键同步脚本 (double-click to run)
REM  流程: pull -> add -> commit -> push
REM  首次使用需先配置远程仓库:
REM    git remote add origin https://<your-repo-url>.git
REM ============================================================
cd /d "%~dp0"

git pull --rebase

git add -A
git diff --cached --quiet
if %errorlevel%==0 (
  echo [sync] No local changes to commit.
) else (
  git commit -m "sync: %date% %time%"
)

git push
if %errorlevel%==0 (
  echo [sync] Done.
) else (
  echo [sync] Push failed. Make sure remote is set and you are logged in.
)
pause
