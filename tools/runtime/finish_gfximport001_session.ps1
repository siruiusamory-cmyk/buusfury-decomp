<#
.SYNOPSIS
Collect and re-verify one GRAPHICS-IMPORT-BOUNDARY-001 live session.

.DESCRIPTION
Runs AFTER the operator closes the mGBA window. It proves the session is usable
evidence before summarising it:

  * the image under test still hashes to the digest the session launched, so the
    run did not modify what it was reading;
  * the source save's hash is unchanged, so the isolated copy really was what the
    emulator wrote to;
  * the observer reported liveness at all, because a silent channel is not a
    negative (mgba-runtime skill, s8);
  * every settled screen it captured is listed with its frame and map index.

It analyses nothing about the graphics: deciding which settled screen is the
gameplay one, and whether the authored tiles reached VRAM, is done afterwards
against these artifacts. This script only establishes that the artifacts are
worth analysing.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\gfximport001\" + $Label)
if (-not (Test-Path -LiteralPath $runDir -PathType Container)) {
    throw "Run directory not found: $runDir"
}

$inputsPath = Join-Path $runDir 'inputs.json'
if (-not (Test-Path -LiteralPath $inputsPath -PathType Leaf)) {
    throw "inputs.json missing from $runDir - the session never started"
}
$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json

$romPath = $inputs.rom_path
$romHashNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $romPath).Hash
$romUnchanged = ($romHashNow -eq $inputs.rom_sha256)

$saveUnchanged = $null
if ($inputs.source_save_path) {
    $saveHashNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.source_save_path).Hash
    $saveUnchanged = ($saveHashNow -eq $inputs.source_save_sha256)
}

$proofPath = Join-Path $runDir 'proof.txt'
$proof = if (Test-Path -LiteralPath $proofPath) { Get-Content -LiteralPath $proofPath } else { @() }

$livenessPath = Join-Path $runDir 'liveness.csv'
$livenessRows = @()
if (Test-Path -LiteralPath $livenessPath) {
    $livenessRows = @(Get-Content -LiteralPath $livenessPath | Where-Object { $_ -and $_ -ne '' })
}

$settlesPath = Join-Path $runDir 'settles.csv'
$settleRows = @()
if (Test-Path -LiteralPath $settlesPath) {
    $settleRows = @(Get-Content -LiteralPath $settlesPath | Where-Object { $_ -and $_ -ne '' })
}

Write-Output 'GRAPHICS-IMPORT-BOUNDARY-001 session summary'
Write-Output "  label            : $Label"
Write-Output "  run dir          : $runDir"
Write-Output "  rom              : $romPath"
Write-Output "  rom sha (launch) : $($inputs.rom_sha256)"
Write-Output "  rom sha (now)    : $romHashNow"
Write-Output "  rom unchanged    : $romUnchanged"
if ($null -ne $saveUnchanged) {
    Write-Output "  source save kept : $saveUnchanged"
}
Write-Output "  mGBA version     : $($inputs.mgba_version)"
Write-Output ''
Write-Output 'Observer liveness (a silent channel would prove nothing):'
if ($livenessRows.Count -le 1) {
    Write-Output '  NO LIVENESS ROWS - the observer never ran; this session is not evidence.'
} else {
    Write-Output "  rows             : $($livenessRows.Count - 1)"
    Write-Output "  first            : $($livenessRows[1])"
    Write-Output "  last             : $($livenessRows[-1])"
}
Write-Output ''
Write-Output 'proof.txt:'
if ($proof.Count -eq 0) { Write-Output '  (absent)' } else { $proof | ForEach-Object { Write-Output "  $_" } }
Write-Output ''
Write-Output 'Settled screens captured (index,frame,map,obj_signature):'
if ($settleRows.Count -le 1) {
    Write-Output '  none'
} else {
    $settleRows | Select-Object -Skip 1 | ForEach-Object { Write-Output "  $_" }
}
Write-Output ''
Write-Output 'Artifacts:'
Get-ChildItem -LiteralPath $runDir -File |
    Sort-Object Name |
    ForEach-Object { Write-Output ("  {0,-28} {1,10}" -f $_.Name, $_.Length) }

if (-not $romUnchanged) { throw 'the image under test changed during the session' }
if ($saveUnchanged -eq $false) { throw 'the source save changed during the session' }
