param(
  [string]$ProjectDir = ".",
  [string]$Main = "main.tex",
  [string]$OutDir = "build",
  [string]$TectonicPath = "D:\tools\tectonic\tectonic.exe",
  [switch]$OnlyCached,
  [int]$Reruns = 2
)

$ErrorActionPreference = "Stop"

$ResolvedProject = (Resolve-Path -LiteralPath $ProjectDir).Path
$MainPath = Join-Path $ResolvedProject $Main
if (-not (Test-Path -LiteralPath $MainPath)) {
  throw "Main TeX file not found: $MainPath"
}

if (-not (Test-Path -LiteralPath $TectonicPath)) {
  throw "Tectonic executable not found: $TectonicPath"
}

$BuildDir = Join-Path $ResolvedProject $OutDir
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

$argsList = @(
  "-X", "compile",
  $MainPath,
  "-o", $BuildDir,
  "--keep-logs",
  "--reruns", "$Reruns"
)

if ($OnlyCached) {
  $argsList += "--only-cached"
}

Write-Host "Compiling $MainPath"
Write-Host "Output directory: $BuildDir"
& $TectonicPath @argsList
if ($LASTEXITCODE -ne 0) {
  throw "Tectonic failed with exit code $LASTEXITCODE"
}

$PdfPath = Join-Path $BuildDir ([System.IO.Path]::GetFileNameWithoutExtension($Main) + ".pdf")
if (-not (Test-Path -LiteralPath $PdfPath)) {
  throw "Compilation finished but PDF was not found: $PdfPath"
}

$PdfItem = Get-Item -LiteralPath $PdfPath
if ($PdfItem.Length -le 0) {
  throw "Compilation produced an empty PDF: $PdfPath"
}

Write-Host "PDF written: $PdfPath"
