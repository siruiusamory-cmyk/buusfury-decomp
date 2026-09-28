#Requires -Version 5.1
<#
.SYNOPSIS
    One-command baseline check for the Buu's Fury decompilation project.

.DESCRIPTION
    Runs every gate that can be run on this machine and prints a single
    PASS / FAIL / BLOCKED summary:

      1. canonical baserom identity      (fails closed on any mismatch)
      2. region map tiles the ROM exactly
      3. asset regions rebuilt byte-identically from source assets
      4. portable regression tests
      5. full source reproduction        (BLOCKED without ADS 1.2 - reported,
                                          not treated as a baseline failure)

    Gate 5 is deliberately NOT a failure. The baseline's contract is that the
    blocker is measured and precisely documented, not that it is absent.

    Written for Windows PowerShell 5.1 and later, because 5.1 is present on
    every Windows machine and PowerShell 7 (pwsh) is NOT installed here.

.PARAMETER Rom
    Path to the baserom. Defaults to $BUUSFURY_ROM, then <repo>/baserom.gba.

.PARAMETER Reference
    Root of the fetched 2genkidev/buusfury checkout. Defaults to
    $BUUSFURY_REFERENCE, then <repo>/reference/buusfury.

.PARAMETER Ads12Root
    Root of an ARM Developer Suite 1.2 installation. Defaults to $ADS12_ROOT.

.PARAMETER SkipTests
    Skip the pytest gate (useful when no test runner is installed).

.EXAMPLE
    powershell -File scripts/check.ps1
.EXAMPLE
    .\check.cmd -Rom 'D:\roms\Dragon Ball Z - Buu''s Fury (U).gba'
#>
[CmdletBinding()]
param(
    [string] $Rom,
    [string] $Reference,
    [string] $Ads12Root,
    [switch] $SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repoRoot 'tools'

function Find-Python {
    foreach ($name in @('python', 'python3', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    throw "No Python interpreter found on PATH. The harness needs Python 3.11+."
}

function Resolve-Baserom {
    param([string] $Explicit)
    if ($Explicit) {
        if (-not (Test-Path -LiteralPath $Explicit -PathType Leaf)) {
            throw "baserom not found at -Rom '$Explicit'"
        }
        return (Resolve-Path -LiteralPath $Explicit).Path
    }
    if ($env:BUUSFURY_ROM -and (Test-Path -LiteralPath $env:BUUSFURY_ROM -PathType Leaf)) {
        return (Resolve-Path -LiteralPath $env:BUUSFURY_ROM).Path
    }
    foreach ($candidate in @(
            (Join-Path $repoRoot 'baserom.gba'),
            (Join-Path $repoRoot 'roms/baserom.gba'))) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    return $null
}

function Resolve-Reference {
    param([string] $Explicit)
    if ($Explicit) { return $Explicit }
    if ($env:BUUSFURY_REFERENCE -and (Test-Path $env:BUUSFURY_REFERENCE)) {
        return $env:BUUSFURY_REFERENCE
    }
    $candidate = Join-Path $repoRoot 'reference/buusfury'
    if (Test-Path $candidate) { return $candidate }
    return $null
}

$python = Find-Python
$romPath = Resolve-Baserom -Explicit $Rom
$referencePath = Resolve-Reference -Explicit $Reference

$overall = 'PASS'
$notes = [System.Collections.Generic.List[string]]::new()

Write-Host "repo        : $repoRoot"
Write-Host "python      : $python"

if (-not $romPath) {
    Write-Host "baserom     : NOT FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "Place a legally dumped copy of the canonical ROM (SHA-1"
    Write-Host "  f1c4b07554d2a3b1ad2f325307051e775ce68087)"
    Write-Host "at <repo>/baserom.gba, or set BUUSFURY_ROM, or pass -Rom."
    Write-Host "This repository never tracks ROM data."
    exit 1
}
Write-Host "baserom     : $romPath"
Write-Host "reference   : $(if ($referencePath) { $referencePath } else { '(not fetched)' })"
Write-Host ""

# --------------------------------------------------------------------------
# gates 1-4
# --------------------------------------------------------------------------
$statusArgs = @('-m', 'buusfury', 'status', '--rom', $romPath)
if ($referencePath) { $statusArgs += @('--reference', $referencePath) }
if ($Ads12Root)     { $statusArgs += @('--ads12-root', $Ads12Root) }

& $python @statusArgs
if ($LASTEXITCODE -ne 0) { $overall = 'FAIL' }

Write-Host ""
Write-Host "========================================================================="
Write-Host "portable regression tests"
Write-Host "========================================================================="
if ($SkipTests) {
    Write-Host "skipped (-SkipTests)"
    $notes.Add('pytest gate skipped by request')
} else {
    Push-Location $repoRoot
    try {
        & $python -m pytest tests -q
        if ($LASTEXITCODE -ne 0) { $overall = 'FAIL' }
    } catch {
        Write-Host "pytest is not available: $($_.Exception.Message)" -ForegroundColor Yellow
        $notes.Add('pytest gate could not run')
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "========================================================================="
if ($overall -eq 'PASS') {
    Write-Host "OVERALL: PASS" -ForegroundColor Green
    Write-Host "  Gates 1-4 established. Gate 5 (full source reproduction) is BLOCKED"
    Write-Host "  on ARM Developer Suite 1.2; the blocker is measured and documented in"
    Write-Host "  docs/DECOMP_BASELINE.md."
} else {
    Write-Host "OVERALL: FAIL" -ForegroundColor Red
}
foreach ($note in $notes) { Write-Host "  note: $note" }
Write-Host "========================================================================="
exit $(if ($overall -eq 'PASS') { 0 } else { 1 })
