<#
.SYNOPSIS
  westock 安装脚本（Windows，随技能包提供）。

.DESCRIPTION
  下载并校验 westock CLI，安装到 %USERPROFILE%\.local\bin。零参数执行即可。

  固定约束（无开关可绕过）：
    * SHA256 校验强制执行：清单拿不到、条目缺失 / 重复 / 畸形、哈希不匹配，一律拒绝安装。
    * 二进制只从官方发布源下载（需 WESTOCK_ALLOW_UNOFFICIAL_BASE=1 才放行其它域名，校验照旧强制）。
    * 不修改用户 PATH 或任何环境变量。

  执行策略：若系统禁止运行未签名脚本，可仅对本次调用放行，不改变系统设置：
    powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1

  环境变量（供部署方 / 平台注入，agent 无需设置）：
    WESTOCK_BASE                    发布基址（默认官方发布源，其次脚本所在目录）
    WESTOCK_ALLOW_UNOFFICIAL_BASE   允许 WESTOCK_BASE 指向非官方域名（危险；SHA256 仍强制）
    WESTOCK_VERSION                 指定版本（默认包内固定版本，其次 latest.txt）
    WESTOCK_INSTALL_DIR             安装目录（默认 %USERPROFILE%\.local\bin）
    WESTOCK_HOME                    数据根目录（默认 %USERPROFILE%\.westock）
    WESTOCK_CHANNEL_DIR             覆盖实际文件的落盘目录
    WESTOCK_SWITCH                  设为默认入口
    WESTOCK_NO_SWITCH               绝不改动入口（含首次安装）
    WESTOCK_FORCE                   忽略「已安装」判断，强制重新下载
    WESTOCK_YES                     跳过交互确认

.PARAMETER DryRun
  只打印计划，不下载、不落盘。

.PARAMETER Help
  显示本帮助。
#>
[CmdletBinding()]
param(
  [switch]$DryRun,
  [switch]$Help
)

if ([string]::IsNullOrEmpty($env:WESTOCK_BASE)) { $Base = "" } else { $Base = $env:WESTOCK_BASE }
$Version = if ($env:WESTOCK_VERSION) { $env:WESTOCK_VERSION } else { "" }
$Bindir = if ($env:WESTOCK_INSTALL_DIR) { $env:WESTOCK_INSTALL_DIR } else { "" }
$Yes = ($env:WESTOCK_YES -eq "1")
$AllowUnofficialBase = ($env:WESTOCK_ALLOW_UNOFFICIAL_BASE -eq "1")
$Switch = ($env:WESTOCK_SWITCH -eq "1")
$NoSwitch = ($env:WESTOCK_NO_SWITCH -eq "1")
$Force = ($env:WESTOCK_FORCE -eq "1")

$ErrorActionPreference = "Stop"

$BinName = "westock.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseExplicit = -not [string]::IsNullOrEmpty($Base)

$CliBaseDefault = "https://stockbuddy.gtimg.com/release/wbgeneral/cli"
if (-not $BaseExplicit) {
  if ($CliBaseDefault -match "^https?://") { $Base = $CliBaseDefault } else { $Base = $ScriptDir }
}

# 「SHA256.txt 清单文件」自身的预期哈希，作为独立于发布源的信任根。
$PinnedManifestSha256 = "386ad06e07dcb2646d12ec2232f228634f586f640b21f651b115f1b354464c9b"

# 本包对应的发布版本 tag（与该版本 SHA256.txt 信任根配套）。
$PinnedVersion = "v0.0.7"

$Channel = "wbgeneral"

# 发布签名公钥（ed25519）。Windows PowerShell 无内置 ed25519 验签能力：已启用签名时，
# 必须有包内固定的清单哈希作为信任根才允许安装（与 setup.sh 的降级规则一致）。
$SignPubkey = "MCowBQYDK2VwAyEAuUWTdpzqYIBKNNCrOYP4zZOjTaMxKz5vSrE5Gc+NUU0="


$userProfile = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
if ([string]::IsNullOrEmpty($Bindir)) { $Bindir = Join-Path $userProfile ".local\bin" }
$WestockRoot = if ($env:WESTOCK_HOME) { $env:WESTOCK_HOME } else { Join-Path $userProfile ".westock" }
$ChannelDir = if ($env:WESTOCK_CHANNEL_DIR) { $env:WESTOCK_CHANNEL_DIR } else { Join-Path $WestockRoot "channels\$Channel\bin" }

function Test-Channel {
  $sentinel = "__" + "CHANNEL__"
  return (-not [string]::IsNullOrEmpty($Channel)) -and ($Channel -ne $sentinel)
}

function Compare-Version {
  param([string]$A, [string]$B)
  try {
    $va = [version]($A -replace '^v', '')
    $vb = [version]($B -replace '^v', '')
    return $va.CompareTo($vb)
  } catch { return 1 }
}


# 提示如何调用（不修改 PATH）。
function Show-PathHint {
  if (($env:Path -split ';') -contains $Bindir) {
    Write-Info "PATH 已包含 ${Bindir}，可直接用 westock 调用"
  } else {
    Write-Info "$Bindir 不在 PATH 中（本脚本不修改 PATH）"
    Write-Info "  请用绝对路径调用: $dest <子命令>"
  }
}


function Get-BinVersion {
  param([string]$Bin)
  if (-not (Test-Path $Bin)) { return '' }
  $env:WESTOCK_NO_AUTO_UPGRADE = '1'
  try {
    $out = & $Bin version --json 2>$null | Out-String
  } catch { return '' }
  if ($out -match '"version":"([^"]+)"') { return $Matches[1] }
  return ''
}


function Invoke-InstallSelf {
  param([string]$Bin)
  if (-not (Test-Channel)) { return $false }

  $exe = $Bin
  $tempCopy = $false
  if (-not $exe.EndsWith('.exe', [StringComparison]::OrdinalIgnoreCase)) {
    $exe = $Bin + '.exe'
    try { Copy-Item -Force $Bin $exe } catch { return $false }
    $tempCopy = $true
  }

  $isArgs = @('install-self', '--channel', $Channel, '--bindir', $Bindir)
  if ($Version) { $isArgs += @('--version', $Version) }
  if ($Switch) { $isArgs += '--switch' }
  if ($NoSwitch) { $isArgs += '--no-switch' }
  if ($Force) { $isArgs += '--force' }

  try {
    $out = & $exe @isArgs 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
      Write-Green '✅ 安装由程序自身完成'
      $out -split "`n" | Where-Object { $_.Trim() } | ForEach-Object { Write-Info "   $($_.Trim())" }
      return $true
    }
    if ($out -match 'unknown command|unknown flag') {
      Write-Info '   当前产物不支持自行安装，回退到脚本直接写入'
    } else {
      Write-Info "   CLI 安装未成功（rc=${LASTEXITCODE}），回退到脚本内置安装逻辑"
    }
  } catch {
    Write-Info "   CLI 安装异常（$($_.Exception.Message)），回退到脚本内置安装逻辑"
  } finally {
    if ($tempCopy) { Remove-Item -Force $exe -ErrorAction SilentlyContinue }
  }
  return $false
}


# 是否已配置 pinned 信任根（哨兵用拼接构造，避免比较基准与被检查的值一同被替换）。
function Test-Pinned {
  $sentinel = "__PINNED_" + "MANIFEST_SHA256__"
  return (-not [string]::IsNullOrEmpty($PinnedManifestSha256)) -and ($PinnedManifestSha256 -ne $sentinel)
}

function Test-SignPubkey {
  $sentinel = "__SIGN_" + "PUBKEY_B64__"
  return (-not [string]::IsNullOrEmpty($SignPubkey)) -and ($SignPubkey -ne $sentinel)
}

function Test-PinnedVersion {
  $sentinel = "__PINNED_" + "VERSION__"
  return (-not [string]::IsNullOrEmpty($PinnedVersion)) -and ($PinnedVersion -ne $sentinel)
}

function Write-Info  { Write-Host $args }
function Write-Green { param([string]$Msg) Write-Host "✅ $Msg" -ForegroundColor Green }
function Write-Warn  { param([string]$Msg) Write-Host "⚠️  $Msg" -ForegroundColor Yellow }
function Write-Err   { param([string]$Msg) Write-Host "❌ $Msg" -ForegroundColor Red }

if ($Help) {
  Get-Help $MyInvocation.MyCommand.Path
  exit 0
}

if (($Base -match "^https?://") -and ($CliBaseDefault -match "^https?://")) {
  $officialHost = ([uri]$CliBaseDefault).Host
  $baseHost = ([uri]$Base).Host
  if ($officialHost -and ($baseHost -ne $officialHost)) {
    if (-not $AllowUnofficialBase) {
      Write-Err "拒绝从非官方域名下载: ${baseHost}（官方发布源: ${officialHost}）"
      Write-Err "确需自建源请设置环境变量 WESTOCK_ALLOW_UNOFFICIAL_BASE=1"
      exit 1
    }
    Write-Warn "正在使用非官方基址 ${baseHost}（WESTOCK_ALLOW_UNOFFICIAL_BASE）；SHA256 校验仍会强制执行"
  }
}

# 与包内固定的 SHA256.txt 清单信任根失配。
if ([string]::IsNullOrEmpty($Version)) {
  if (Test-PinnedVersion) {
    $Version = $PinnedVersion
  } else {
    $latestFile = Join-Path $Base "latest.txt"
    if (Test-Path $latestFile) {
      $Version = (Get-Content $latestFile -Raw).Trim()
    } else {
      $tag = Get-ChildItem -Directory -Path $Base -Filter "v*" |
        Where-Object { $_.Name -match '^v\d+\.\d+\.\d+' } |
        Sort-Object { [version]($_.Name -replace '^v', '') } -Descending |
        Select-Object -First 1
      if ($null -eq $tag) {
        Write-Err "未找到 latest.txt，且目录下无可用 v* 版本目录，请设置环境变量 WESTOCK_VERSION 指定版本"
        exit 1
      }
      $Version = $tag.Name
    }
  }
}
if (-not $Version.StartsWith("v")) { $Version = "v$Version" }

$artifact = "westock-windows-amd64.exe"
$relative = "$Version/$artifact"
$dest = Join-Path $Bindir $BinName
$realBin = if (Test-Channel) { Join-Path $ChannelDir $BinName } else { $dest }

Write-Info "将安装: $BinName $Version"
Write-Info "  源:   $Base/$relative"
Write-Info "  目标: $dest"
Write-Info "  用户 PATH: 不修改"
if ($DryRun) {
  Write-Info "(dry-run) 未做任何改动"
  exit 0
}

$interactive = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected
if (-not $Yes -and $interactive) {
  $reply = Read-Host "确认安装? [Y/n]"
  if ($reply -match '^[Nn]$') {
    Write-Warn "已取消"
    exit 0
  }
}

if ((Test-Channel) -and (-not $Force) -and (Test-Path $realBin)) {
  $installedVer = Get-BinVersion -Bin $realBin
  if ($installedVer -and ((Compare-Version -A $Version -B $installedVer) -le 0)) {
    Write-Info "   已安装 ${installedVer}（不低于 ${Version}），跳过下载"
    if (-not (Invoke-InstallSelf -Bin $realBin)) { Write-Green "已安装 → $realBin" }
    Show-PathHint
    exit 0
  }
}

$tmp = Join-Path ([IO.Path]::GetTempPath()) ("westock-install-" + [guid]::NewGuid().ToString())
$manifestPath = $null
try {
  if ($Base -match "^https?://") {
    $url = "$Base/$relative"
    Write-Info "⬇️  $url"
    Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
  } else {
    $src = Join-Path $Base $relative
    if (-not (Test-Path $src)) { Write-Err "找不到二进制: $src"; exit 1 }
    Copy-Item -Force $src $tmp
  }

  # ---- 校验 ----
  # 清单落盘后按原始字节计算哈希：避免把响应解码成文本再重新编码（BOM / 编码差异会导致误判）。
  $manifestPath = "$tmp.SHA256.txt"
  if ($Base -match "^https?://") {
    try {
      Invoke-WebRequest -Uri "$Base/$Version/SHA256.txt" -OutFile $manifestPath -UseBasicParsing
    } catch {
      Write-Err "无法获取校验清单 $Base/$Version/SHA256.txt，拒绝安装"
      exit 1
    }
  } else {
    $checksumPath = Join-Path $Base "$Version/SHA256.txt"
    if (-not (Test-Path $checksumPath)) {
      Write-Err "未找到校验清单 ${checksumPath}，拒绝安装"
      exit 1
    }
    Copy-Item -Force $checksumPath $manifestPath
  }
  $manifestText = [System.IO.File]::ReadAllText($manifestPath)

  if ((Test-SignPubkey) -and -not (Test-Pinned)) {
    Write-Err "已启用发布签名，但 PowerShell 无法校验 ed25519 签名且包内无固定清单哈希，拒绝安装"
    exit 1
  }

  # 信任根校验：用固定哈希确认 SHA256.txt 清单本身未被篡改（独立于发布源）。
  if (Test-Pinned) {
    $manifestActual = (Get-FileHash -Path $manifestPath -Algorithm SHA256).Hash.ToLower()
    if ($manifestActual -ne $PinnedManifestSha256.ToLower()) {
      Write-Err "SHA256.txt 清单校验失败（疑似发布源被篡改），拒绝安装"
      Write-Err "  期望: $PinnedManifestSha256"
      Write-Err "  实际: $manifestActual"
      exit 1
    }
  }

  $lines = $manifestText -split "`n"
  $candidates = @()
  foreach ($line in $lines) {
    if ($line -match "^([0-9a-fA-F]{64})\s+(.*\S)\s*$" -and $Matches[2] -eq $artifact) {
      $candidates += $Matches[1].ToLower()
    }
  }
  if ($candidates.Count -eq 0) {
    Write-Err "SHA256.txt 中未找到 $artifact 的合法校验条目，拒绝安装"
    exit 1
  }
  if ($candidates.Count -gt 1) {
    Write-Err "SHA256.txt 中 $artifact 存在 $($candidates.Count) 条校验条目（清单歧义），拒绝安装"
    exit 1
  }

  $expected = $candidates[0]
  $actual = (Get-FileHash -Path $tmp -Algorithm SHA256).Hash.ToLower()
  if ($actual -ne $expected) {
    Write-Err "SHA256 校验失败: $artifact"
    Write-Err "  期望: $expected"
    Write-Err "  实际: $actual"
    exit 1
  }
  Write-Green "SHA256 校验通过: $artifact"

  if (Invoke-InstallSelf -Bin $tmp) {
    Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    Show-PathHint
    exit 0
  }
  New-Item -ItemType Directory -Force -Path $Bindir | Out-Null
  Move-Item -Force $tmp $dest
} finally {
  if (Test-Path $tmp) { Remove-Item -Force $tmp }
  if ($manifestPath -and (Test-Path $manifestPath)) { Remove-Item -Force $manifestPath }
}

Write-Green "已安装 → ${dest}（直接安装）"

# ---- PATH ----
Show-PathHint
