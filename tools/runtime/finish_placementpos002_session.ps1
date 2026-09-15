<#
.SYNOPSIS
Close out a PLACEMENT-POS-001 Phase 2 human-play session and summarise its
evidence: the settled construction rows, whether actor+0x1A0>>8==raw_0 AND
actor+0x1A4>>8==raw_1 now hold, and the SKILL section 8 liveness verdict.

.DESCRIPTION
Companion to start_placementpos002_session.ps1. Run AFTER closing the mGBA
window. Never kills the emulator; refuses if mGBA is still running.

It verifies the GENERATED ROM's hash is unchanged across the run AND that the
CANONICAL ROM on disk was never touched (still 940ad5f0...). The savestate
source is verified unchanged too.

Observer CSV columns:
  event,pc,r4_actor_base,r5,position_raw_0,position_raw_1,
  actor_1A0,actor_1A4,actor_1A0_asr8,actor_1A4_asr8,note
with `event` in {settled, read_low, liveness}. A `settled` row (trap 0x0800FDDA)
has BOTH stores committed, so its actor_1A0_asr8 / actor_1A4_asr8 are final. Its
raw_0/raw_1 come from the paired `read_low` row for the same r4.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$canonicalRom = Join-Path $root 'roms\Dragon Ball Z - Buu''s Fury (U).gba'
$canonicalSha = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
$runDir = Join-Path $root ("build\placementpos002\" + $Label)
if (-not (Test-Path -LiteralPath $runDir)) { throw "No such run: $runDir" }

$inputsPath = Join-Path $runDir 'inputs.json'
if (-not (Test-Path -LiteralPath $inputsPath)) { throw "Run has no inputs.json: $runDir" }
$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    Write-Output 'mGBA is STILL RUNNING; close its window before collecting evidence.'
    Write-Output 'Refusing to summarise a session that is still in progress.'
    exit 2
}

# The canonical ROM must be untouched by a Phase 2 run.
if (Test-Path -LiteralPath $canonicalRom) {
    $canonNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $canonicalRom).Hash
    if ($canonNow -ne $canonicalSha) {
        throw "CANONICAL ROM CHANGED during the run: $canonicalSha -> $canonNow"
    }
}
# The generated ROM's own hash must be stable across the run.
$genNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
if ($genNow -ne $inputs.rom_sha256) {
    throw "Generated ROM changed during the run: $($inputs.rom_sha256) -> $genNow"
}
# Savestate source unchanged (a working copy was played).
$stateNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.state_path).Hash
if ($stateNow -ne $inputs.state_sha256) {
    throw "Source savestate changed during the run: $($inputs.state_sha256) -> $stateNow"
}

$csv = $inputs.csv_path
if (-not (Test-Path -LiteralPath $csv)) {
    Write-Output 'no observer output (CSV absent). Instrument produced nothing to read.'
    exit 1
}

$rows = @(Import-Csv -LiteralPath $csv)
$settled = @($rows | Where-Object { $_.event -eq 'settled' })
$reads = @($rows | Where-Object { $_.event -eq 'read_low' })
$liveness = @($rows | Where-Object { $_.event -eq 'liveness' })

# Pair each settled row with the most recent read_low for the same r4, so raw_0
# and raw_1 sit beside the settled actor_1A0/1A4 values.
$lastRaw = @{}
$paired = New-Object System.Collections.ArrayList
foreach ($r in $rows) {
    if ($r.event -eq 'read_low') {
        $lastRaw[$r.r4_actor_base] = @{ raw0 = $r.position_raw_0; raw1 = $r.position_raw_1; r5 = $r.r5 }
    }
    elseif ($r.event -eq 'settled') {
        $rawinfo = $lastRaw[$r.r4_actor_base]
        $raw0 = if ($rawinfo) { $rawinfo.raw0 } else { '' }
        $raw1 = if ($rawinfo) { $rawinfo.raw1 } else { '' }
        $r5 = if ($rawinfo) { $rawinfo.r5 } else { '' }
        $x_ok = ($raw0 -ne '' -and [int]$r.actor_1A0_asr8 -eq [int]$raw0)
        $y_ok = ($raw1 -ne '' -and [int]$r.actor_1A4_asr8 -eq [int]$raw1)
        [void]$paired.Add([pscustomobject]@{
            r4 = $r.r4_actor_base; r5 = $r5
            raw_0 = $raw0; raw_1 = $raw1
            a1A0_asr8 = $r.actor_1A0_asr8; a1A4_asr8 = $r.actor_1A4_asr8
            X_match = $x_ok; Y_match = $y_ok
        })
    }
}
$xMatches = @($paired | Where-Object { $_.X_match }).Count
$yMatches = @($paired | Where-Object { $_.Y_match }).Count

Write-Output "run        : $runDir"
Write-Output "gen ROM    : $($inputs.rom_path)"
Write-Output "gen sha    : $genNow (unchanged across run)"
Write-Output "canonical  : $canonicalSha (untouched on disk)"
Write-Output "state sha  : $stateNow (source unchanged)"
Write-Output "rows       : $($rows.Count)  (settled=$($settled.Count) read_low=$($reads.Count) liveness=$($liveness.Count))"
Write-Output ''

if ($settled.Count -gt 0) {
    Write-Output "SKILL section 8 case: TARGET FIRES -> construction OBSERVED (settled trap 0x0800FDDA)."
    Write-Output ''
    Write-Output "SETTLED-ROW AXIS CHECK (both stores committed):"
    Write-Output "  actor+0x1A0>>8 == raw_0 : $xMatches / $($paired.Count)"
    Write-Output "  actor+0x1A4>>8 == raw_1 : $yMatches / $($paired.Count)"
    Write-Output ''
    Write-Output "Paired settled rows (r4 = live actor base, never hard-coded):"
    $paired | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output
    Write-Output 'Phase 2 closes the construction copy only. Do not infer sprite identity'
    Write-Output 'from a lookalike screenshot; Phase 3 static render-consumer evidence'
    Write-Output 'records the coordinate contract in PLACEMENT_POSITION_PROVENANCE.md.'
}
elseif ($liveness.Count -gt 0) {
    Write-Output 'SKILL section 8 case: TARGET SILENT + LIVENESS FIRES -> REAL NEGATIVE.'
    Write-Output 'Instrument live, but no construction seen. Re-enter map 40 so placements reconstruct.'
}
else {
    Write-Output 'SKILL section 8 case: TARGET SILENT + LIVENESS SILENT -> INSTRUMENT UNPROVEN.'
    Write-Output 'Not negative evidence. Confirm lua-ready.txt / marker.txt and re-run.'
}
