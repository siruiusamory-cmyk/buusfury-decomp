<#
.SYNOPSIS
Collect the evidence from a finished SPRITE-NEW-RUNTIME-001 session.

.DESCRIPTION
Re-verifies the image and the source save after the session, then reports what the
observer actually recorded. It refuses to read a silent observer as evidence: an
observer that never armed, or one that armed and wrote nothing, is reported as
"no observations" rather than as a run that found nothing.

It never starts, stops or waits on mGBA. The session belongs to the operator.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Label,
    [switch]$AllowRunning
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\spritenew001\" + $Label)
if (-not (Test-Path -LiteralPath $runDir)) {
    throw "No run directory: $runDir"
}

if (-not $AllowRunning -and (Get-Process mGBA -ErrorAction SilentlyContinue)) {
    throw 'mGBA is still running. Close the window first, then collect; a live emulator can still be writing.'
}

$inputs = Get-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Raw | ConvertFrom-Json
$outRoot = $inputs.out_root

Write-Output "=== SPRITE-NEW-RUNTIME-001 session '$Label' ==="
Write-Output "  rom           : $($inputs.rom_path)"
Write-Output "  rom sha256    : $($inputs.rom_sha256)"
Write-Output "  rom size      : $($inputs.rom_size)"

$romHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
Write-Output "  rom unchanged : $($romHashAfter -eq $inputs.rom_sha256)"

if ($inputs.source_save_path) {
    $saveHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.source_save_path).Hash
    Write-Output "  source save unchanged : $($saveHashAfter -eq $inputs.source_save_sha256)"
}

$armed = Test-Path -LiteralPath (Join-Path $outRoot 'armed.txt')
$done = Test-Path -LiteralPath (Join-Path $outRoot 'done.txt')
$shots = @(Get-ChildItem -Path $outRoot -Filter '*.png' -ErrorAction SilentlyContinue)
$states = @(Get-ChildItem -Path $outRoot -Filter 'state-*.txt' -ErrorAction SilentlyContinue)

Write-Output ''
Write-Output '  observer armed      : ' + $armed
Write-Output '  observer finished   : ' + $done
Write-Output "  screenshots         : $($shots.Count)"
Write-Output "  state reports       : $($states.Count)"

if (-not $armed) {
    Write-Output ''
    Write-Output 'NO OBSERVATIONS: the observer never armed, so this session proves nothing.'
    Write-Output 'The instrument was not running; this is not a negative result.'
    exit 3
}
if ($states.Count -eq 0) {
    Write-Output ''
    Write-Output 'NO OBSERVATIONS: the observer armed but wrote no state report.'
    exit 3
}

$hitsPath = Join-Path $outRoot 'hits.txt'
if (Test-Path -LiteralPath $hitsPath) {
    Write-Output ''
    Write-Output '--- resolution evidence (hits.txt) ---'
    Get-Content -LiteralPath $hitsPath | ForEach-Object { Write-Output "  $_" }
}

Write-Output ''
Write-Output '--- state timeline ---'
foreach ($state in $states | Sort-Object Name) {
    $fields = @{}
    foreach ($line in Get-Content -LiteralPath $state.FullName) {
        $parts = $line -split '=', 2
        if ($parts.Count -eq 2) { $fields[$parts[0]] = $parts[1] }
    }
    $map = if ($fields.ContainsKey('map_index')) { $fields['map_index'] } else { '?' }
    $hits = if ($fields.ContainsKey('constructor_hits')) { $fields['constructor_hits'] } else { '0' }
    $new = if ($fields.ContainsKey('actors_using_new_identity')) { $fields['actors_using_new_identity'] } else { '0' }
    Write-Output ("  {0}: map={1} constructor_hits={2} new_identity_actors={3}" -f `
        $state.Name, $map, $hits, $new)
}

$final = Join-Path $outRoot 'state-final.txt'
if (Test-Path -LiteralPath $final) {
    Write-Output ''
    Write-Output '--- final state ---'
    Get-Content -LiteralPath $final | ForEach-Object { Write-Output "  $_" }
}

Write-Output ''
Write-Output "Run directory: $runDir"
