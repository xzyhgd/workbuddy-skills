# ============================================================
#  WorkBuddy Skills 一键同步脚本 (PowerShell)
#  流程: pull -> add -> commit -> push
#  首次使用需先配置远程仓库:
#    git remote add origin https://<your-repo-url>.git
# ============================================================
Set-Location $PSScriptRoot

try { git pull --rebase 2>$null } catch { }

git add -A
$hasChanges = ((git diff --cached --quiet); $LASTEXITCODE) -ne 0
if ($hasChanges) {
    git commit -m "sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Write-Host "[sync] 已提交本地改动。"
} else {
    Write-Host "[sync] 没有需要提交的本地改动。"
}

git push
if ($LASTEXITCODE -eq 0) {
    Write-Host "[sync] 同步完成。"
} else {
    Write-Host "[sync] 推送失败：请先配置远程仓库（git remote add origin <url>）并确保已登录。"
}
