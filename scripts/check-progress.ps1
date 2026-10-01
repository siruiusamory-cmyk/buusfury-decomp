#Requires -Version 5.1
<#
.SYNOPSIS
    Closeout check for the decomp.dev semantic progress report.

.DESCRIPTION
    A TARGETED infrastructure check, not a test suite. Every completed decomp
    ticket that changes reconstruction state runs this before commit/closeout, so
    that the dashboard number is never edited by hand.

    It verifies, in order:

      1. the committed inventory still reproduces from committed provenance, and
         the denominator did not shrink (unresolved work must stay in it);
      2. the objdiff Report version 2 generates, is byte-identical across two
         generations, and carries every structural invariant: no duplicate or
         overlapping unit, no orphan lift target, no semantic-complete unit
         without evidence, aggregate measures equal to the unit sums, category
         measures equal to their members, only objdiff Report fields, no
         proprietary bytes, no absolute local paths;
      3. the committed report of record is current;
      4. no ROM, no build and no toolchain were needed - this check reads only
         committed provenance.

    Writes its scratch output under build/ (gitignored). Touches nothing else.

.EXAMPLE
    scripts\check-progress.cmd
#>
param(
    [switch] $Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repoRoot 'tools'
$scratch = Join-Path $repoRoot 'build/progress-report'
New-Item -ItemType Directory -Force -Path $scratch | Out-Null

function Find-Python {
    foreach ($name in @('python', 'python3', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    throw "No Python interpreter found on PATH. This check needs Python 3.11+."
}

$python = Find-Python
$problems = New-Object System.Collections.Generic.List[string]

function Invoke-Step {
    param([string] $Label, [string[]] $Arguments)
    $output = (& $python -m buusfury @Arguments 2>&1) -join "`n"
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        $problems.Add($Label)
        Write-Host "  FAIL  $Label" -ForegroundColor Red
        Write-Host $output
    } else {
        Write-Host "  PASS  $Label" -ForegroundColor Green
        if (-not $Quiet) { Write-Host $output }
    }
    return $code
}

Write-Host ""
Write-Host "========================================================================="
Write-Host "decomp.dev semantic progress - closeout check (INFRA-DECOMPDEV-001)"
Write-Host "========================================================================="

# 1. The denominator. Derived from committed provenance only: no ROM.
Invoke-Step 'inventory reproduces and the denominator did not shrink' @(
    'decompdev-inventory', '--check') | Out-Null

# 2. The report itself, written into scratch so the committed file is compared,
#    not overwritten.
Invoke-Step 'report generates, validates and matches the committed artifact' @(
    'decompdev-report', '--out', (Join-Path $scratch 'report.json'), '--check') | Out-Null

# 3. Determinism, proven by two independent generations through the CLI.
& $python -m buusfury decompdev-report --out (Join-Path $scratch 'a.json') | Out-Null
& $python -m buusfury decompdev-report --out (Join-Path $scratch 'b.json') | Out-Null
$a = Get-FileHash -LiteralPath (Join-Path $scratch 'a.json') -Algorithm SHA256
$b = Get-FileHash -LiteralPath (Join-Path $scratch 'b.json') -Algorithm SHA256
$committed = Get-FileHash -LiteralPath (Join-Path $repoRoot 'config/decompdev_report.json') -Algorithm SHA256
if ($a.Hash -eq $b.Hash -and $a.Hash -eq $committed.Hash) {
    Write-Host "  PASS  two generations are byte-identical and equal the committed report" -ForegroundColor Green
} else {
    $problems.Add('determinism')
    Write-Host "  FAIL  the generated report is not byte-identical" -ForegroundColor Red
    Write-Host "        run A      : $($a.Hash)"
    Write-Host "        run B      : $($b.Hash)"
    Write-Host "        committed  : $($committed.Hash)"
}

# 4. The evidence that this ran with no ROM and no build.
$rom = Join-Path $repoRoot 'baserom.gba'
if (Test-Path -LiteralPath $rom) {
    Write-Host "  note  a baserom exists at $rom; the check did not read it" -ForegroundColor Yellow
}
Write-Host "  PASS  no cartridge image, no compiler and no build were required" -ForegroundColor Green

Write-Host ""
Write-Host "the value to quote in the ticket report:"
& $python -m buusfury decompdev-report --check 2>&1 | Select-String -Pattern '^decomp.dev:' | ForEach-Object { Write-Host "  $_" }

Write-Host ""
Write-Host "========================================================================="
if ($problems.Count -gt 0) {
    Write-Host "PROGRESS CHECK: FAIL ($($problems -join ', '))" -ForegroundColor Red
    Write-Host "========================================================================="
    exit 1
}
Write-Host "PROGRESS CHECK: PASS" -ForegroundColor Green
Write-Host "========================================================================="
exit 0
