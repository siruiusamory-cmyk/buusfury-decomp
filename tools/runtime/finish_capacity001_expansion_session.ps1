<#
.SYNOPSIS
Collect the evidence from a finished CAPACITY-001 human expansion session.

.DESCRIPTION
Companion to `start_capacity001_expansion_session.ps1`. The launcher starts mGBA
and exits; the operator ends the session; this script reads what was recorded and
verifies the two ROMs are unchanged. It stops nothing: if mGBA is still running
the operator has not finished, and killing it would be the same bug the runtime
rules warn about.

It reports the facts and does not grade them. In particular a run with no CONSUMER
row is reported together with the LIVENESS row, because a silent consumer plus a
silent liveness channel proves nothing, while a silent consumer plus a firing
liveness channel is a real negative.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\capacity-checkpoint-d\" + $Label)
if (-not (Test-Path -LiteralPath $runDir -PathType Container)) {
    throw "No such run directory: $runDir"
}

$csv = Join-Path $runDir 'capacity001-dialogue.csv'
$marker = Join-Path $runDir 'marker.txt'
$session = Join-Path $runDir 'session.json'

$facts = [ordered]@{ label = $Label; run_dir = $runDir }

if (Test-Path -LiteralPath $session) {
    $document = Get-Content -LiteralPath $session -Raw | ConvertFrom-Json
    $facts.rom_path = $document.rom_path
    $facts.rom_sha256 = $document.rom_sha256
    $facts.rom_size = $document.rom_size
    $facts.expected_pointer = $document.expected_pointer
    $facts.mgba_version = $document.mgba_version

    if (Test-Path -LiteralPath $document.rom_path) {
        $current = (Get-FileHash -Algorithm SHA256 -LiteralPath $document.rom_path).Hash
        $facts.derivative_unchanged = ($current -eq $document.rom_sha256)
        $facts.derivative_sha256_now = $current
    }
    $canonical = Join-Path $root 'roms\Dragon Ball Z - Buu''s Fury (U).gba'
    if (Test-Path -LiteralPath $canonical) {
        $canonicalNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $canonical).Hash
        $facts.canonical_sha256_now = $canonicalNow
        $facts.canonical_unchanged =
            ($canonicalNow -eq '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E')
    }
}

$facts.marker = if (Test-Path -LiteralPath $marker) {
    (Get-Content -LiteralPath $marker -Raw).Trim()
} else { $null }

if (Test-Path -LiteralPath $csv) {
    $rows = @(Get-Content -LiteralPath $csv)
    $facts.row_count = $rows.Count
    $facts.consumer_rows = @($rows | Where-Object { $_ -like 'CONSUMER,*' }).Count
    $facts.liveness_rows = @($rows | Where-Object { $_ -like 'LIVENESS,*' }).Count
    $facts.target_rows = @($rows | Where-Object { $_ -like '*target expanded selector consumed*' }).Count
    $facts.unexpected_target_rows =
        @($rows | Where-Object { $_ -like '*unexpected pointer*' }).Count
    $facts.rows = $rows
} else {
    $facts.row_count = 0
    Write-Output 'no probe output; the probe never armed or never ran'
}

$facts
Write-Output ''
Write-Output '--- evidence ---'
if ($facts.row_count -gt 0) { $rows | ForEach-Object { Write-Output $_ } }
Write-Output ''
Write-Output '--- screenshots ---'
Get-ChildItem -LiteralPath $runDir -Filter '*.png' -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Output ("  " + $_.Name + "  " + $_.Length + " bytes") }

if ($facts.consumer_rows -eq 0 -and $facts.liveness_rows -eq 0) {
    Write-Output ''
    Write-Output 'NULL RESULT, NOT A NEGATIVE: neither the consumer nor the liveness'
    Write-Output 'channel fired, so this run establishes nothing about the resource.'
} elseif ($facts.consumer_rows -eq 0) {
    Write-Output ''
    Write-Output 'REAL NEGATIVE: the liveness channel fired, so the core was executing'
    Write-Output 'the observed code region, but no compressed-dialogue handle was consumed.'
}
