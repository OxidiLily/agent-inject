param(
  [ValidateSet('all','claude','codex','hermes','opencode','openclaw')]
  [string]$Target = 'all'
)
$ErrorActionPreference = 'Stop'
$scriptDir = $PSScriptRoot
$defaultRoot = Join-Path $HOME 'DATA/Documents/obsidian-vault/setup'
if ($env:LAST_RITE_SETUP_ROOT) { $root = $env:LAST_RITE_SETUP_ROOT }
elseif (Test-Path (Join-Path $scriptDir 'SOUL.md')) { $root = $scriptDir }
else { $root = $defaultRoot }
$soul = Join-Path $root 'SOUL.md'
$kb = Join-Path $root 'knowledge-base.md'
$credDir = Join-Path $root 'kredensial'
$credFile = Join-Path $credDir 'kredensial.env'
if (-not (Test-Path $soul -PathType Leaf)) { throw "[gagal] SOUL tidak ditemukan: $soul. Set LAST_RITE_SETUP_ROOT atau letakkan SOUL.md di folder setup." }
New-Item -ItemType Directory -Force -Path (Join-Path $root 'Sessions'),(Join-Path $root 'Skills'),$credDir | Out-Null
if (-not (Test-Path $credFile)) { New-Item -ItemType File -Path $credFile | Out-Null }
if (-not (Test-Path $kb)) { New-Item -ItemType File -Path $kb | Out-Null }
function Backup-File([string]$Path) {
  if (Test-Path $Path -PathType Leaf) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $dest = "$Path.bak.$stamp"
    Copy-Item -LiteralPath $Path -Destination $dest
    Write-Output "[backup] $dest"
  }
}
function Shared-Block([string]$Agent) {
@"
Agent-ID: $Agent

Canonical operational policy:
$soul

Shared state:
- Sessions: $(Join-Path $root 'Sessions')\
- Skills: $(Join-Path $root 'Skills')\
- Credential manifests: $credDir\<Service>.md
- Secret store: $credFile
- Knowledge Base: $kb

Before substantive work in every new session, read the canonical SOUL.

Credential resolver:
SERVICE_NAME -> <Service>.md -> CREDENTIAL_KEY -> kredensial.env.
Read the service manifest first. Read only the targeted secret key from the secret store.
Do not dump the secret store and do not automatically hunt credentials in agent-specific
.env files, ~/.git-credentials, ~/.netrc, credential helpers, SSH keys, or other agent configs
unless Endministrator explicitly instructs that source.

Shared writes must re-read current state first and record provenance as Agent: $Agent.
"@
}
function Install-Agent([string]$Id,[string]$Command,[string]$Path,[string]$Header) {
  if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) { Write-Output "[skip] $Command tidak terdeteksi"; return }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  Backup-File $Path
  $text = "$Header`r`n`r`n$(Shared-Block $Id)"
  Set-Content -LiteralPath $Path -Value $text -Encoding utf8
  Write-Output "[ok] $Command`: $Path"
}
function Install-Claude { Install-Agent 'claude' 'claude' (Join-Path $HOME '.claude/CLAUDE.md') '# Last Rite Bootstrap — Claude Code' }
function Install-Codex {
  $dir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
  Install-Agent 'codex' 'codex' (Join-Path $dir 'AGENTS.md') '# Last Rite Bootstrap — Codex'
}
function Install-Hermes {
  if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) { Write-Output '[skip] hermes tidak terdeteksi'; return }
  $dir = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME '.hermes' }
  $path = Join-Path $dir 'SOUL.md'; New-Item -ItemType Directory -Force -Path $dir | Out-Null; Backup-File $path
  @"
# Last Rite — Hermes Identity Bootstrap

Kamu adalah Last Rite, asisten pribadi Endministrator.
Bahasa respons utama Indonesia; istilah teknis boleh tetap asli.
Ringkas, presisi, kritis terhadap asumsi, aman, dan verifikasi sebelum mengklaim berhasil.

Sebelum pekerjaan substantif pada setiap sesi, baca operational policy:
$soul

Shared state:
- Sessions: $(Join-Path $root 'Sessions')\
- Skills: $(Join-Path $root 'Skills')\
- Credential manifests: $credDir\<Service>.md
- Secret store: $credFile
- Knowledge Base: $kb

Untuk autentikasi selalu manifest-first:
SERVICE_NAME -> <Service>.md -> CREDENTIAL_KEY -> kredensial.env.

Jangan otomatis mencari service credential di ~/.hermes/.env, ~/.git-credentials,
~/.netrc, credential helper, SSH key, atau config agent lain kecuali Endministrator
secara eksplisit meminta sumber tersebut atau itu memang credential internal Hermes.

Saat menulis shared Session/Skill/KB/manifest, re-read dahulu dan atribusikan Agent: hermes.
"@ | Set-Content -LiteralPath $path -Encoding utf8
  Write-Output "[ok] Hermes: $path"
  Write-Output '[info] SOUL Hermes adalah identity bootstrap. Project context tetap memakai mekanisme native Hermes.'
}
function Install-OpenCode { Install-Agent 'opencode' 'opencode' (Join-Path $HOME '.config/opencode/AGENTS.md') '# Last Rite Bootstrap — OpenCode' }
function Install-OpenClaw {
  if (-not (Get-Command openclaw -ErrorAction SilentlyContinue)) { Write-Output '[skip] openclaw tidak terdeteksi'; return }
  $ws = if ($env:OPENCLAW_WORKSPACE) { $env:OPENCLAW_WORKSPACE } else { Join-Path $HOME '.openclaw/workspace' }
  New-Item -ItemType Directory -Force -Path $ws | Out-Null
  $soulPath = Join-Path $ws 'SOUL.md'; $agentsPath = Join-Path $ws 'AGENTS.md'
  Backup-File $soulPath; Backup-File $agentsPath
  @'
# Last Rite — OpenClaw Soul

Kamu adalah Last Rite, asisten pribadi Endministrator.
Bahasa utama Indonesia; istilah teknis boleh tetap asli.
Ringkas, presisi, kritis, aman, dan verifikasi sebelum mengklaim berhasil.
'@ | Set-Content -LiteralPath $soulPath -Encoding utf8
  $openClawText = @"
# Last Rite Bootstrap — OpenClaw

$(Shared-Block 'openclaw')
"@
  Set-Content -LiteralPath $agentsPath -Value $openClawText -Encoding utf8
  Write-Output "[ok] OpenClaw: $soulPath + $agentsPath"
}
switch ($Target) {
  all { Install-Claude; Install-Codex; Install-Hermes; Install-OpenCode; Install-OpenClaw }
  claude { Install-Claude }
  codex { Install-Codex }
  hermes { Install-Hermes }
  opencode { Install-OpenCode }
  openclaw { Install-OpenClaw }
}
Write-Output "`n[verifikasi] Shared root: $root"
if (Test-Path $soul -PathType Leaf) { '[ok] SOUL readable' }
if (Test-Path (Join-Path $root 'Sessions') -PathType Container) { '[ok] Sessions tersedia' }
if (Test-Path (Join-Path $root 'Skills') -PathType Container) { '[ok] Skills tersedia' }
if (Test-Path $credDir -PathType Container) { '[ok] Credential directory tersedia' }
if (Test-Path $credFile -PathType Leaf) { '[ok] Secret store tersedia' }
$manifest = Get-ChildItem -LiteralPath $credDir -File -ErrorAction SilentlyContinue | Where-Object Name -IEQ 'github.md' | Select-Object -First 1
if ($manifest) {
  Write-Output "[ok] GitHub manifest: $($manifest.FullName)"
  if (Select-String -LiteralPath $manifest.FullName -Pattern 'GITHUB_TOKEN|CREDENTIAL_KEY\s*:\s*GITHUB_TOKEN' -Quiet) { '[ok] GitHub manifest memetakan GITHUB_TOKEN' } else { '[peringatan] GitHub manifest belum memetakan GITHUB_TOKEN secara jelas' }
  if (Select-String -LiteralPath $credFile -Pattern '^GITHUB_TOKEN=.' -Quiet) { '[ok] GITHUB_TOKEN tersedia di secret store (nilai tidak ditampilkan)' } else { '[peringatan] GITHUB_TOKEN tidak ditemukan/empty di secret store' }
}
