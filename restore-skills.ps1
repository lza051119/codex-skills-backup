$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$codexSource = Join-Path $repoRoot "codex-skills"
$agentsSource = Join-Path $repoRoot "agents-skills"

$codexDest = Join-Path $env:USERPROFILE ".codex\skills"
$agentsDest = Join-Path $env:USERPROFILE ".agents\skills"

New-Item -ItemType Directory -Force -Path $codexDest | Out-Null
New-Item -ItemType Directory -Force -Path $agentsDest | Out-Null

if (Test-Path -LiteralPath $codexSource) {
  robocopy $codexSource $codexDest /E /XD ".system"
  if ($LASTEXITCODE -gt 7) {
    throw "robocopy failed while restoring Codex skills with exit code $LASTEXITCODE"
  }
}

if (Test-Path -LiteralPath $agentsSource) {
  robocopy $agentsSource $agentsDest /E
  if ($LASTEXITCODE -gt 7) {
    throw "robocopy failed while restoring Agents skills with exit code $LASTEXITCODE"
  }
}

Write-Host "Skills restored. Restart Codex to reload them."
