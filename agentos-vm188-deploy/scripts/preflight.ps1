[CmdletBinding()]
param(
    [string]$RepositoryPath,
    [string]$ExpectedTargetSha,
    [string]$OutputPath,
    [switch]$DisposableRebuild
)
$ErrorActionPreference = 'Stop'
$desktopScript = 'C:\Users\27616\Desktop\vm188\single-server-deploy\scripts\preflight.ps1'
if (-not (Test-Path -LiteralPath $desktopScript)) { throw 'The VM188 Desktop implementation is missing; do not fall back to repository deployment scripts.' }
& $desktopScript @PSBoundParameters
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
