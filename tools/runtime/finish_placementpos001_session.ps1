<#
.SYNOPSIS
Close out the PLACEMENT-POS-001 Phase 1 human-play session and summarise its
evidence, including the SKILL section 8 liveness verdict.

.DESCRIPTION
The companion to start_placementpos001_session.ps1. That script deliberately
exits while mGBA keeps running, so the post-run steps -- verifying the ROM was
not modified, and reporting what was actually measured -- live here.

Run this AFTER closing the mGBA window.

It never kills the emulator. If mGBA is still up, it says so and stops, because
summarising a session that is still producing evidence would report a partial
result as a final one.

The observer CSV columns are:
  event,pc,r4_actor_base,r5,position_raw_0,position_raw_1,
  actor_1A0,actor_1A4,actor_1A0_asr8,actor_1A4_asr8,note
with `event` in {store_low, store_high, read_low, liveness}. The construction
channel is the store_* / read_low rows (target 0x0800FDC8/0x0800FDD2/0x0800FDD8);
the liveness channel is the `liveness` rows (interpreter 0x08004038).

SKILL section 8 verdict:
  target fires                    -> construction observed
  target silent + liveness fires  -> real negative (that construction path not taken)
  target silent + liveness silent -> instrument UNPROVEN (NOT negative evidence)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\placementpos001\" + $Label)
if (-not (Test-Path -LiteralPath $runDir)) { throw "No such run: $runDir" }

$inputsPath = Join-Path $runDir 'inputs.json'
if (-not (Test-Path -LiteralPath $inputsPath)) { throw "Run has no inputs.json: $runDir" }
$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    Write-Output 'mGBA is STILL RUNNING; close its window before collecting evidence.'
    Write-Output 'Refusing to summarise a session that is still in progress.'
    exit 2
}

# Post-run identity check: before == after == canonical. Same guard the tracked
# GDB launcher performs.
$romHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
if ($romHashAfter -ne $inputs.rom_sha256) {
    throw "ROM changed during the run: $($inputs.rom_sha256) -> $romHashAfter"
}
# The savestate source is immutable too; a working copy was played, never the source.
$stateHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.state_path).Hash
if ($stateHashAfter -ne $inputs.state_sha256) {
    throw "Source savestate changed during the run: $($inputs.state_sha256) -> $stateHashAfter"
}

$csv = $inputs.csv_path
if (-not (Test-Path -LiteralPath $csv)) {
    Write-Output 'no observer output (CSV absent). Instrument produced nothing to read.'
    exit 1
}

$rows = @(Import-Csv -LiteralPath $csv)
$construct = @($rows | Where-Object { $_.event -in @('store_low', 'store_high', 'read_low') })
$liveness = @($rows | Where-Object { $_.event -eq 'liveness' })
$storeLow = @($rows | Where-Object { $_.event -eq 'store_low' })
$storeHigh = @($rows | Where-Object { $_.event -eq 'store_high' })
$readLow = @($rows | Where-Object { $_.event -eq 'read_low' })

Write-Output "run       : $runDir"
Write-Output "rom sha   : $romHashAfter (unchanged, == canonical)"
Write-Output "state sha : $stateHashAfter (source unchanged)"
Write-Output "rows      : $($rows.Count)"
Write-Output ''
Write-Output "CONSTRUCTION (target 0x0800FDC8/0x0800FDD2/0x0800FDD8) : $($construct.Count)"
Write-Output "  read_low   (raw halfwords via r5)   : $($readLow.Count)"
Write-Output "  store_low  (actor+0x1A0, r4 base)   : $($storeLow.Count)"
Write-Output "  store_high (actor+0x1A4)            : $($storeHigh.Count)"
Write-Output "LIVENESS (interpreter 0x08004038)     : $($liveness.Count)"
Write-Output ''

if ($construct.Count -gt 0) {
    Write-Output 'SKILL section 8 case: TARGET FIRES -> construction OBSERVED.'
    Write-Output ''
    Write-Output 'Captured construction rows (each store_low/store_high names r4 = the'
    Write-Output 'actor base for THIS load; never a hard-coded address):'
    $construct |
        Select-Object event, pc, r4_actor_base, r5, position_raw_0, position_raw_1, `
            actor_1A0, actor_1A4, actor_1A0_asr8, actor_1A4_asr8, note |
        Format-Table -AutoSize | Out-String -Width 4096 | Write-Output
    Write-Output 'NEXT (manual, SC3): correlate actor_1A0_asr8 / actor_1A4_asr8 against'
    Write-Output 'the object pixel in the operator screenshot to assign the axis. Do NOT'
    Write-Output 'assign the axis from these numbers alone -- the on-screen pixel is the proof.'
}
elseif ($liveness.Count -gt 0) {
    # The interpreter ran, so the instrument sees execution; construction of the
    # watched placement was simply not reached in this session (e.g. the doorway
    # was not crossed, or that map does not build via this path). A measurement.
    Write-Output 'SKILL section 8 case: TARGET SILENT + LIVENESS FIRES -> REAL NEGATIVE.'
    Write-Output 'The instrument is live (interpreter reached); the construction store was'
    Write-Output 'not hit this session. Re-run and cross the doorway so a fresh map loads.'
}
else {
    # Neither channel fired, so nothing can be concluded in either direction.
    Write-Output 'SKILL section 8 case: TARGET SILENT + LIVENESS SILENT -> INSTRUMENT UNPROVEN.'
    Write-Output 'This is NOT negative evidence. The observer may not have armed, or no'
    Write-Output 'gameplay ran. Confirm lua-ready.txt / marker.txt exist and re-run.'
}
