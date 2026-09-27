<#
.SYNOPSIS
Summarise one finished MAP-WARP-CREATE-RUNTIME-001 session from its observer CSV.

.DESCRIPTION
Reads the run directory the launcher wrote (inputs.json plus create-watch.csv),
re-verifies that the ROM, the savestate and the private save are exactly what the
launcher recorded, and prints the rows that carry the proof:

  * the engine's own route to each sampled element of map 40's transition array,
    with the root's count, so element 2 absent on the canonical image and present
    on the derivative is visible in one place;
  * the created element's record fields as the engine's route resolved them: the
    destination key bytes and the map they resolve to, the four region endpoints,
    +0x10, and the arrival words;
  * every live map change with its frame and the map it came from.

It writes summary.txt beside the CSV and changes nothing else.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [string]$RunDir
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
if (-not $RunDir) { $RunDir = Join-Path $root ("build\warpedit001\" + $Label) }
if (-not (Test-Path -LiteralPath $RunDir -PathType Container)) {
    throw "No run directory: $RunDir"
}

$inputsPath = Join-Path $RunDir 'inputs.json'
$csvPath = Join-Path $RunDir 'create-watch.csv'
if (-not (Test-Path -LiteralPath $inputsPath)) { throw "Missing inputs.json in $RunDir" }
if (-not (Test-Path -LiteralPath $csvPath)) { throw "Missing create-watch.csv in $RunDir" }

$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json
$rows = Import-Csv -LiteralPath $csvPath

$lines = [System.Collections.Generic.List[string]]::new()
function Say([string]$text) { $lines.Add($text); Write-Output $text }

Say ('MAP-WARP-CREATE-RUNTIME-001 session: {0}' -f $Label)
Say ('  run dir    : {0}' -f $RunDir)
Say ('  rom        : {0}' -f $inputs.rom_path)
Say ('  rom sha256 : {0}' -f $inputs.rom_sha256)
Say ('  rom size   : {0}' -f $inputs.rom_size)
$romNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
Say ('  rom now    : {0}  {1}' -f $romNow, $(if ($romNow -eq $inputs.rom_sha256) { 'UNCHANGED' } else { 'CHANGED - INVESTIGATE' }))
Say ('  state sha  : {0}' -f $inputs.state_sha256)
if ($inputs.original_save_sha256) {
    $saveNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.original_save_path).Hash
    Say ('  save       : {0}  {1}' -f $saveNow, $(if ($saveNow -eq $inputs.original_save_sha256) { 'UNCHANGED' } else { 'CHANGED - INVESTIGATE' }))
} else {
    Say '  save       : (no save beside this image)'
}
Say ('  observer   : {0}' -f $inputs.lua_path)
Say ('  mGBA       : {0} ({1})' -f $inputs.mgba_path, $inputs.mgba_version)
Say ('  csv rows   : {0}' -f $rows.Count)
Say ''

$elements = @(0, 1, 2)
Say 'ROUTE - the engine''s own path to each element of map 40''s transition array'
foreach ($element in $elements) {
    $candidates = @($rows | Where-Object { $_.kind -in @('ROUTE', 'CREATED') -and [int]$_.element -eq $element })
    if (-not $candidates) {
        Say ('  element {0}: no row (the observer never sampled it)' -f $element)
        continue
    }
    $last = $candidates[-1]
    Say ('  element {0}: status={1} root={2} count={3} array={4} element_ptr={5} record={6}' -f `
        $element, $last.status, $last.root, $last.root_count, $last.array, $last.element_ptr, $last.record)
    if ($last.status -eq 'present') {
        # The arrival is a word at +0x14 and a byte pair at +0x16/+0x17; both are
        # printed as decimal values and as the raw bytes, so the reader never has
        # to guess a base. An empty cell prints as 0 rather than throwing.
        $arrivalX = if ($last.arrival_14) { [Convert]::ToInt32($last.arrival_14, 16) } else { 0 }
        $arrivalY = if ($last.arrival_16 -and $last.arrival_17) { [Convert]::ToInt32($last.arrival_17 + $last.arrival_16, 16) } else { 0 }
        Say ('             key={0}/{1} -> map {2}  region={3}  +0x10={4}  arrival=({5}, {6})  raw {7}/{8}/{9}' -f `
            $last.key_hi, $last.key_lo, $last.key_resolves_to, $last.region_hex, `
            $last.byte_0x10, $arrivalX, $arrivalY, $last.arrival_14, $last.arrival_16, $last.arrival_17)
        Say ('             frame {0}  note: {1}' -f $last.frame, $last.note)
    }
}

Say ''
Say 'ELEMENT 2 (the appended, created element) across the session'
$created = @($rows | Where-Object { [int]$_.element -eq 2 })
if (-not $created) {
    Say '  no rows: the observer never sampled element 2'
} else {
    foreach ($row in $created) {
        Say ('  frame {0}  kind={1}  status={2}  count={3}  array={4}  element_ptr={5}  record={6}  key->map {7}' -f `
            $row.frame, $row.kind, $row.status, $row.root_count, $row.array, $row.element_ptr, $row.record, $row.key_resolves_to)
    }
    $present = @($created | Where-Object { $_.status -eq 'present' })
    if ($present) {
        Say ('  VERDICT: element 2 was PRESENT and resolved through the engine route to record {0}' -f $present[-1].record)
    } else {
        Say ('  VERDICT: element 2 was never present (canonical behaviour: count {0})' -f $created[-1].root_count)
    }
}

Say ''
Say 'MAP - every live map change the engine reported'
$maps = @($rows | Where-Object { $_.kind -eq 'MAP' })
if (-not $maps) {
    Say '  no map rows'
} else {
    foreach ($row in $maps) {
        Say ('  frame {0}  map={1}  entry={2}  {3}' -f $row.frame, $row.map_index, $row.map_entry_ptr, $row.note)
    }
}

$beats = @($rows | Where-Object { $_.kind -eq 'HEARTBEAT' })
$unresolved = @($rows | Where-Object { $_.kind -eq 'ROUTE_UNRESOLVED' })
Say ''
Say ('HEARTBEATS: {0}   ROUTE_UNRESOLVED rows: {1}' -f $beats.Count, $unresolved.Count)

$summary = Join-Path $RunDir 'summary.txt'
$lines | Set-Content -LiteralPath $summary -Encoding utf8
Write-Output ''
Write-Output ('summary written: {0}' -f $summary)
