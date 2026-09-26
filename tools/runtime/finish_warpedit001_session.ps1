<#
.SYNOPSIS
Summarise one finished MAP-WARP-RUNTIME-EDIT-001 session from its observer CSV.

.DESCRIPTION
Run this after the operator has closed the mGBA window. It reads the run
directory the launcher created, re-verifies the ROM the session used, and prints
the facts the ticket's evidence depends on:

  * the target record as the engine's OWN route reached it during the run
    (MapEntry[map]+0x2C -> word[0] -> root+0x44 -> element), with the two
    destination key bytes read from the running image and the map that key
    resolves to through the live MapEntry table;
  * the ordered map-identity timeline, so the map entered after the trigger is
    attributable to a frame;
  * whether the engine had already left and re-entered the target map, which is
    what makes the trigger a ROM-side read rather than a restored savestate;
  * the heartbeat count, so a silent observer is distinguishable from a quiet
    one and never read as a negative.

It writes summary.txt beside the CSV and changes nothing else.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [int]$ExpectTargetMap = 40,
    [int]$ExpectedDestination = 0
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\warpedit001\" + $Label)
if (-not (Test-Path -LiteralPath $runDir)) { throw "No such run directory: $runDir" }

$inputsPath = Join-Path $runDir 'inputs.json'
$csvPath = Join-Path $runDir 'session.csv'
if (-not (Test-Path -LiteralPath $inputsPath)) { throw "Missing inputs.json in $runDir" }
if (-not (Test-Path -LiteralPath $csvPath)) { throw "Missing session.csv in $runDir" }

$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json
$rows = Import-Csv -LiteralPath $csvPath

$lines = New-Object System.Collections.Generic.List[string]
function Say([string]$text) { $lines.Add($text); Write-Output $text }

Say "RUN $Label"
Say ("  rom        : {0}" -f $inputs.rom_path)
Say ("  rom sha256 : {0}" -f $inputs.rom_sha256)
$romNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
Say ("  rom now    : {0}  {1}" -f $romNow, $(if ($romNow -eq $inputs.rom_sha256) { 'UNCHANGED' } else { 'CHANGED - INVESTIGATE' }))
Say ("  state sha  : {0}" -f $inputs.state_sha256)
if ($inputs.original_save_sha256) {
    # The save beside the image is a private research input: the session pointed
    # the emulator at an isolated save directory, and this is the check that it
    # stayed that way.
    $saveNow = if (Test-Path -LiteralPath $inputs.original_save_path) {
        (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.original_save_path).Hash
    } else { '' }
    Say ("  save       : {0}  {1}" -f $inputs.original_save_sha256, $(if ($saveNow -eq $inputs.original_save_sha256) { 'UNCHANGED' } else { 'CHANGED - INVESTIGATE' }))
}
Say ("  observer   : {0}" -f $inputs.lua_path)
Say ("  mGBA       : {0} ({1})" -f $inputs.mgba_version, $inputs.mgba_path)

$heartbeats = @($rows | Where-Object { $_.kind -eq 'HEARTBEAT' })
$maps = @($rows | Where-Object { $_.kind -eq 'MAP' })
$target = @($rows | Where-Object { $_.kind -eq 'TARGET' })
$unresolved = @($rows | Where-Object { $_.kind -eq 'TARGET_UNRESOLVED' })

Say ''
Say ("LIVENESS: {0} heartbeat row(s), {1} map row(s)" -f $heartbeats.Count, $maps.Count)
if ($heartbeats.Count -eq 0) {
    Say '  WARNING: no heartbeat rows. The observer may not have armed; a silent'
    Say '  channel is NOT evidence of absence. Do not read this run as a negative.'
}

Say ''
if ($target.Count -eq 0) {
    # An unproven instrument must not be reported as a clear result.
    Say 'TARGET RECORD: NOT RESOLVED during this run'
    if ($unresolved.Count -gt 0) {
        Say ("  observer reported: {0}" -f $unresolved[0].note)
    }
    Say '  The destination key could not be read through the engine route, so this'
    Say '  run does not establish which record the engine would have used.'
} else {
    $t = $target[0]
    Say 'TARGET RECORD (as the engine route reached it):'
    Say ("  frame {0}: map entry {1} -> source {2} -> root {3} -> array {4} -> record {5}" -f `
        $t.frame, $t.map_entry_ptr, $t.source, $t.root, $t.array, $t.record)
    Say ("  destination key bytes: {0} {1}" -f $t.key_hi, $t.key_lo)
    Say ("  key resolves to map  : {0}" -f $t.key_resolves_to)
    Say ("  region bytes         : {0}" -f $t.region_hex)
}

Say ''
Say 'MAP TIMELINE:'
$departures = New-Object System.Collections.Generic.List[object]
# The rebuild marker lands on the ARRIVAL row (entering the target map after
# having been elsewhere); a departure from the target map is labelled `from=N`.
# So the flag has to be carried FORWARD from the arrival to the departures that
# follow it - reading it off the departure row itself finds nothing, which is
# what an earlier revision of this script got wrong.
$sawRebuild = $false
foreach ($row in $maps) {
    if ($row.note -like '*rebuilt-after-leaving*') { $sawRebuild = $true }
    $isDeparture = ($row.note -match '^from=(\d+)$' -and [int]$Matches[1] -eq $ExpectTargetMap)
    $marker = if ($isDeparture -and $sawRebuild) { '   <== after rebuild' } else { '' }
    Say ("  frame {0,8}  map {1}{2}{3}" -f $row.frame, $row.map_index, $(if ($row.note) { "  ($($row.note))" } else { '' }), $marker)
    if ($isDeparture) {
        $departures.Add([pscustomobject]@{ frame = [int]$row.frame; to = [int]$row.map_index; rebuilt = $sawRebuild })
    }
}

Say ''
if ($departures.Count -eq 0) {
    Say ("VERDICT: no departure from map {0} was observed in this run" -f $ExpectTargetMap)
} else {
    $first = $departures[0]
    Say ("VERDICT: first departure from map {0} -> map {1} at frame {2}" -f $ExpectTargetMap, $first.to, $first.frame)
    $afterRebuild = @($departures | Where-Object { $_.rebuilt })
    if ($afterRebuild.Count -gt 0) {
        $r = $afterRebuild[0]
        Say ("  after an observed leave-and-re-enter: map {0} -> map {1} at frame {2}" -f $ExpectTargetMap, $r.to, $r.frame)
    } else {
        Say '  NOTE: no departure was seen after an observed leave-and-re-enter, so'
        Say '  this run does not by itself prove the engine re-read the record from ROM.'
    }
    if ($ExpectedDestination -ne 0) {
        $hit = @($departures | Where-Object { $_.to -eq $ExpectedDestination })
        Say ("  expected destination {0}: {1}" -f $ExpectedDestination, $(if ($hit.Count -gt 0) { 'OBSERVED' } else { 'NOT OBSERVED' }))
    }
}

# --- MAP-WARP-FACING-TRACE-001: the facing correlation ------------------------
#
# The arrival-facing claim is a CORRELATION of four things and this reports all
# four together, because none of them is sufficient alone: the authored byte in
# the record, the selector that can veto the write, the facing byte the engine
# actually wrote on the player, and the operator's own observation. The record
# byte alone proves nothing - that is the whole point of the ticket.
$facingPath = Join-Path $runDir 'facing.csv'
if (Test-Path -LiteralPath $facingPath) {
    $face = Import-Csv -LiteralPath $facingPath
    $changes = @($face | Where-Object { $_.kind -eq 'CHANGE' })
    $recordBytes = @($face | Where-Object { $_.record_facing_raw } |
        Select-Object -ExpandProperty record_facing_raw -Unique)
    $selectors = @($face | Where-Object { $_.selector_raw } |
        Select-Object -ExpandProperty selector_raw -Unique)

    Say ''
    Say 'FACING CORRELATION:'
    Say ("  record +0x10 (live): {0}" -f ($recordBytes -join ', '))
    Say ("  selector 0x03001A34: {0}  ({1})" -f ($selectors -join ', '), `
        $(if ($selectors.Count -eq 1 -and $selectors[0] -eq '0x00000000') {
            'ZERO throughout - the 566 arrival-facing write was ELIGIBLE'
          } else { 'non-zero seen - the traced path SKIPS the arrival write' }))
    Say ("  facing CHANGES: {0}" -f $changes.Count)
    foreach ($row in $changes) {
        Say ("    frame {0,8}  map {1}  facing {2}  [{3}]" -f `
            $row.frame, $row.map_index, $row.player_facing_raw, $row.note)
    }
    # The load-bearing value: the facing byte first written on the player object
    # the WARP created - i.e. the first such row in a map other than the source.
    # Selecting the first match outright picks up the pre-warp object swap in the
    # source map, which says nothing about the arrival.
    $newPlayer = ($changes |
        Where-Object { $_.note -match 'player 0->' -and [int]$_.map_index -ne $ExpectTargetMap } |
        Select-Object -First 1)
    if ($newPlayer) {
        Say ("  the player object the warp created first carries facing byte {0} in map {1} (frame {2})" -f `
            $newPlayer.player_facing_raw, $newPlayer.map_index, $newPlayer.frame)
    } else {
        Say '  no post-warp player object was observed on this channel.'
    }
}

Say ''
Say ("  total rows: {0}" -f $rows.Count)
$lines -join "`r`n" | Set-Content -LiteralPath (Join-Path $runDir 'summary.txt') -Encoding utf8
Write-Output ''
Write-Output ("summary written: {0}" -f (Join-Path $runDir 'summary.txt'))
