# ============================================================
#  WorkBuddy Skills one-click sync (PowerShell) - plain git, no extra deps
#  Flow: pull -> add -> commit -> push
#  - GIT_TERMINAL_PROMPT=0 : never block on a credential prompt
#  - http.version=HTTP/1.1 : avoid proxy HTTP/2 (CONNECT tunnel) failures
#  - lowSpeedLimit/Time    : abort a stalled transfer instead of hanging
# ============================================================
$ErrorActionPreference = 'Continue'
Set-Location -LiteralPath $PSScriptRoot
$env:GIT_TERMINAL_PROMPT = '0'

Write-Host "[sync] Step 1/3: pull --rebase from remote..."
git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 pull --rebase
if ($LASTEXITCODE -eq 0) {
    Write-Host "[sync] pull OK."
} else {
    Write-Host "[sync] pull skipped/failed (network). Continuing."
}

Write-Host "[sync] Step 2/3: add + commit..."
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[sync] committed local changes."
    } else {
        Write-Host "[sync] commit FAILED - see the message above."
    }
} else {
    Write-Host "[sync] no local changes to commit."
}

Write-Host "[sync] Step 3/3: push to remote..."
git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 push
if ($LASTEXITCODE -eq 0) {
    Write-Host "[sync] push OK - synced."
} else {
    Write-Host "[sync] push failed (likely network). Re-run this script when network recovers."
}

Write-Host "[sync] Finished."
