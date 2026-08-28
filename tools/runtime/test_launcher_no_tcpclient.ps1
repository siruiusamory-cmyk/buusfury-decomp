<#
.SYNOPSIS
Regression test: ensure run_mgba_capture.ps1 never uses TcpClient/BeginConnect/EndConnect
.DESCRIPTION
These APIs complete a TCP handshake which steals mGBA's single GDB slot.
The launcher must only use non-connecting OS queries (GetActiveTcpListeners).
#>
$ErrorActionPreference = 'Stop'

$launcher = Join-Path $PSScriptRoot 'run_mgba_capture.ps1'
$content = Get-Content -LiteralPath $launcher -Raw

# Check for forbidden patterns in actual code (not comments)
$lines = $content -split "`n"
$inCode = $true
$found = @()

foreach ($line in $lines) {
    $trimmed = $line.TrimStart()
    if ($trimmed.StartsWith('#')) { continue }  # skip comment lines
    if ($trimmed -match 'New-Object System\.Net\.Sockets\.TcpClient') { $found += 'TcpClient constructor' }
    if ($trimmed -match '\.BeginConnect\(') { $found += 'BeginConnect' }
    if ($trimmed -match '\.EndConnect\(') { $found += 'EndConnect' }
    if ($trimmed -match 'GetStream\(\)\.Close\(\)') { $found += 'GetStream().Close()' }
    if ($trimmed -match 'New-Object System\.Net\.Sockets\.TcpListener') { $found += 'TcpListener' }
}

if ($found.Count -gt 0) {
    Write-Error "REGRESSION: Forbidden patterns found in launcher:"
    foreach ($f in $found) { Write-Error "  $f" }
    exit 1
}

# Verify the required pattern exists
if ($content -notmatch 'GetActiveTcpListeners') {
    Write-Error "REGRESSION: Required pattern 'GetActiveTcpListeners' not found"
    exit 1
}

Write-Host "PASS: Launcher uses only non-connecting port checks"
exit 0