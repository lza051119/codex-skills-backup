param(
  [Parameter(Mandatory = $true)]
  [string]$PdfPath,
  [string]$OutputDir = "preview",
  [string]$PdftoppmPath = "D:\tools\poppler\Library\bin\pdftoppm.exe",
  [int]$Dpi = 150,
  [int]$FirstPage = 1,
  [int]$LastPage = 0
)

$ErrorActionPreference = "Stop"

$ResolvedPdf = (Resolve-Path -LiteralPath $PdfPath).Path
if (-not (Test-Path -LiteralPath $PdftoppmPath)) {
  throw "pdftoppm executable not found: $PdftoppmPath"
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$ResolvedOutput = (Resolve-Path -LiteralPath $OutputDir).Path
$Prefix = Join-Path $ResolvedOutput "page"

$argsList = @("-png", "-r", "$Dpi", "-f", "$FirstPage")
if ($LastPage -gt 0) {
  $argsList += @("-l", "$LastPage")
}
$argsList += @($ResolvedPdf, $Prefix)

& $PdftoppmPath @argsList
if ($LASTEXITCODE -ne 0) {
  throw "pdftoppm failed with exit code $LASTEXITCODE"
}

Write-Host "Preview images written to: $ResolvedOutput"
