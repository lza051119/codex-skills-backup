[CmdletBinding()]
param(
    [string]$VmHost = '10.10.20.188',
    [string]$VmUser = 'root',
    [string]$VmKeyPath = 'C:\Users\27616\.ssh\agentos-vm188-access-ed25519',
    [string]$SshPath = 'C:\Windows\System32\OpenSSH\ssh.exe',
    [string]$CurlPath = 'C:\Windows\System32\curl.exe',
    [string]$VpnExecutable = 'D:\SSLVPN Client\clientGUI.exe',
    [string]$VpnAdapterName = 'SEC-Windows Adapter',
    [int]$VmReachabilityTimeoutSeconds = 60,
    [int]$TunnelTimeoutSeconds = 30,
    [switch]$SkipVpnAutoConnect,
    [switch]$NoBrowser,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$desktopScript = 'C:\Users\27616\Desktop\vm188\single-server-deploy\scripts\open-vm188.ps1'
if (-not (Test-Path -LiteralPath $desktopScript)) { throw 'The VM188 Desktop implementation is missing; do not fall back to repository deployment scripts.' }
& $desktopScript @PSBoundParameters
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
