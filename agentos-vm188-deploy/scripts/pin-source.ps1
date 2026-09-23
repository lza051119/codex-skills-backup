[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryPath,

    [string]$ExpectedTargetSha,
    [string]$IncrementalBaseSha,
    [string]$TeaPath = 'D:\Tools\tea\tea.exe',
    [string]$OutputDirectory = 'C:\Users\27616\Desktop\vm188\single-server-deploy\records',
    [string]$GitPath = 'C:\Program Files\Git\cmd\git.exe'
)

$ErrorActionPreference = 'Stop'
$desktopScript = 'C:\Users\27616\Desktop\vm188\single-server-deploy\scripts\pin-source.ps1'
if (-not (Test-Path -LiteralPath $desktopScript)) { throw 'The VM188 Desktop implementation is missing; do not fall back to repository deployment scripts.' }
& $desktopScript @PSBoundParameters
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
