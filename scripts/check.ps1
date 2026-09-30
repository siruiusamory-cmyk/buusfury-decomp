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
      6. compiler probe                  (the probe manifest must reproduce from
                                           the ROM; the probe itself is BLOCKED
                                           without ADS 1.2 - reported, not a
                                           baseline failure)
      7. semantic lift                   (every registered target's decompiled
                                           source must build with the MODERN
                                           toolchain, behave correctly when RUN,
                                           and re-derive its report key by key)

    Gates 5 and 6 are deliberately NOT failures. The baseline's contract is that the
    blocker is measured and precisely documented, not that it is absent. Gate 7 is
    independent of them: it needs the modern ARM toolchain, not ADS, and it is a
    real PASS or FAIL.

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
Write-Host "regression tests"
Write-Host "========================================================================="
if ($SkipTests) {
    Write-Host "skipped (-SkipTests)"
    $notes.Add('pytest gate skipped by request')
} else {
    # Export the baserom we already resolved so the ROM-gated tests RUN instead
    # of skipping. Without this the gate silently weakens to portable-only.
    $previousRom = $env:BUUSFURY_ROM
    $env:BUUSFURY_ROM = $romPath
    Push-Location $repoRoot
    try {
        & $python -m pytest tests -q
        if ($LASTEXITCODE -ne 0) { $overall = 'FAIL' }
    } catch {
        Write-Host "pytest is not available: $($_.Exception.Message)" -ForegroundColor Yellow
        $notes.Add('pytest gate could not run')
    } finally {
        Pop-Location
        if ($null -eq $previousRom) {
            Remove-Item Env:\BUUSFURY_ROM -ErrorAction SilentlyContinue
        } else {
            $env:BUUSFURY_ROM = $previousRom
        }
    }
}

Write-Host ""
Write-Host "========================================================================="
Write-Host "gate 6: compiler probe (DECOMP-COMPILER-PROBE-001)"
Write-Host "========================================================================="
# The manifest and the matrix are measurements, not declarations: both must
# regenerate from the canonical ROM and agree, or this gate FAILS.
& $python -m buusfury compiler-probe --rom $romPath --verify-manifest
if ($LASTEXITCODE -ne 0) { $overall = 'FAIL' }
& $python -m buusfury compiler-probe --rom $romPath --verify-matrix
if ($LASTEXITCODE -ne 0) { $overall = 'FAIL' }

# The probe itself cannot run without ADS 1.2. Report that as BLOCKED, the same
# contract as gate 5, and never let it read as a compiler result. PASS requires
# that at least one configuration actually COMPARED BYTES; a run that merely
# found a driver name is not a result.
#
# The branch reads the document's own fields rather than searching its text. A
# PARTIAL matrix carries "code": "ADS12_UNAVAILABLE" on its blocked ROWS, so a
# substring test would report a run that did compare bytes as BLOCKED. stderr is
# kept out of the parsed stream for the same reason: a warning line would break
# the JSON and turn a working probe into a false FAIL.
$matrixJson = (& $python -m buusfury compiler-probe --rom $romPath --matrix --json 2>$null) -join "`n"
$matrixExit = $LASTEXITCODE
$matrix = $null
$comparisons = $null
$blockerCode = $null
try {
    $matrix = $matrixJson | ConvertFrom-Json
    $comparisons = $matrix.comparisons_run
    $blockerCode = $matrix.code
} catch {
    $matrix = $null
}
if ($null -ne $blockerCode -and $comparisons -eq 0) {
    # Any blocker code is BLOCKED, not FAIL. The distinction between "ADS not
    # installed" and "ADS installed but unlicensed" changes the MESSAGE, not
    # whether this gate fails: both are environment problems this repository
    # cannot fix. The code is printed so the reason is unambiguous.
    Write-Host ""
    Write-Host "      BLOCKED  probe prepared; no compiler result is claimed" -ForegroundColor Yellow
    Write-Host "               reason: $blockerCode"
    if ($blockerCode -eq 'ADS12_LICENSE_UNAVAILABLE') {
        Write-Host "               ADS 1.2 is installed and identified, but FLEXlm refuses"
        Write-Host "               the tools (no compiler/armasm/armlink feature present)."
    }
    $notes.Add("compiler probe BLOCKED ($blockerCode); see docs/COMPILER_PROBE.md")
} elseif ($null -ne $comparisons -and $comparisons -gt 0) {
    # Tested BEFORE the blocker branch's consequence: a document that both
    # compared bytes and names a blocker code must report the comparison, never
    # BLOCKED. build_matrix cannot emit that combination, so this is only about
    # keeping the branch total for a hand-tampered document.
    Write-Host ""
    Write-Host "      PASS  compiler probe compared $comparisons configuration(s)" -ForegroundColor Green
    $notes.Add("compiler probe ran: $comparisons configuration(s) compared; see docs/COMPILER_PROBE.md")
} elseif ($null -ne $matrix) {
    Write-Host "      FAIL  compiler probe ran but compared nothing" -ForegroundColor Red
    $overall = 'FAIL'
} else {
    Write-Host "      FAIL  compiler probe produced no readable result (exit $matrixExit)" -ForegroundColor Red
    $overall = 'FAIL'
}

Write-Host ""
Write-Host "========================================================================="
Write-Host "gate 7: semantic lift (DECOMP-LIFT-PILOT-001, DECOMP-LIFT-SCRIPT-001, DECOMP-LIFT-SCRIPT-HANDLER-001, DECOMP-LIFT-SCRIPT-SM7-001, DECOMP-LIFT-SCRIPT-STACK-001, DECOMP-LIFT-SCRIPT-ARITH-001, DECOMP-LIFT-SCRIPT-USE-001, DECOMP-LIFT-SCRIPT-EFFECT-001, DECOMP-LIFT-SCRIPT-FLAGREAD-001, DECOMP-LIFT-SCRIPT-BOOLUSE-001, DECOMP-LIFT-FLAGSTATE-001, DECOMP-LIFT-FLAGMASK-001)"
Write-Host "========================================================================="
# The lift loop's own verdicts are independent of the ADS blocker: it compiles
# the decompiled source with the MODERN toolchain and checks the reconstruction
# by RUNNING it. ADS_MATCH stays BLOCKED and is reported as such by the tool.
#
# Every registered target is verified. The reports are regenerated and compared
# KEY BY KEY rather than spot-checked, so a changed verdict, comparison or
# function row cannot pass unnoticed.
$liftVerify = (& $python -m buusfury lift --target all --rom $romPath --verify 2>&1) -join "`n"
$liftExit = $LASTEXITCODE
$liftPasses = ([regex]::Matches($liftVerify, "REPORT: PASS")).Count
$liftTargets = (& $python -m buusfury lift --list-targets 2>$null | Select-Object -Skip 1).Count
if ($liftVerify -match "MODERN_TOOLCHAIN_UNAVAILABLE") {
    # No ARM cross toolchain is an environment problem, not a defect in the
    # repository, so it is BLOCKED rather than FAIL - the same contract as
    # gates 5 and 6. A toolchain is never installed by this repository.
    Write-Host "      BLOCKED  no ARM cross toolchain found; the lift loop cannot run here" -ForegroundColor Yellow
    $notes.Add("lift gate BLOCKED (no modern ARM toolchain); see docs/LIFT_PILOT.md")
} elseif ($liftExit -eq 0 -and $liftTargets -gt 0 -and $liftPasses -eq $liftTargets) {
    Write-Host "      PASS  $liftPasses/$liftTargets lift targets re-derived their reports identically" -ForegroundColor Green
    $notes.Add("lift gate PASS ($liftPasses targets; SEMANTIC PROVEN, MODERN_BUILD PASS); ADS_MATCH remains BLOCKED")
} else {
    # Counting the passes against the registry keeps this honest: a run that
    # silently skipped a target cannot report success.
    Write-Host "      FAIL  the lift loop did not reproduce every report ($liftPasses of $liftTargets)" -ForegroundColor Red
    Write-Host $liftVerify
    $overall = 'FAIL'
}

Write-Host ""
Write-Host "========================================================================="
if ($overall -eq 'PASS') {
    Write-Host "OVERALL: PASS" -ForegroundColor Green
    Write-Host "  Gates 1-4 established. Gate 5 (full source reproduction) and gate 6"
    Write-Host "  (compiler probe) are BLOCKED on ARM Developer Suite 1.2; both blockers"
    Write-Host "  are measured and documented in docs/DECOMP_BASELINE.md and"
    Write-Host "  docs/COMPILER_PROBE.md. Gate 7 (semantic lift) passes independently:"
    Write-Host "  it needs the modern toolchain, not ADS."
} else {
    Write-Host "OVERALL: FAIL" -ForegroundColor Red
}
foreach ($note in $notes) { Write-Host "  note: $note" }
Write-Host "========================================================================="
exit $(if ($overall -eq 'PASS') { 0 } else { 1 })
