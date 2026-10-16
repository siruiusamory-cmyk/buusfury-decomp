<#
.SYNOPSIS
Summarise one finished MAP-NEW-AUTHORING-001 session from its observer CSV.

.DESCRIPTION
Run this after the operator has closed the mGBA window. It reads the run
directory the launcher created, re-verifies the ROM the session used, and prints
the facts the ticket's evidence depends on:

  * the base the ENGINE loaded, read from the literal pool word its own key lookup
    names, and the row bound it decoded from its own count helper - so "this is a
    relocated table" is the engine's statement and not the build's;
  * the loaded row: its index, the bytes of its two-byte key, the `+0x2C` selector
    source word, the root that word names and that root's `+0x14` layer slot, each
    read only where the engine's own pointer landed;
  * the ordered map-identity timeline, so entering the authored map is
    attributable to a frame;
  * whether any index at or above the canonical count was ever loaded, which is
    the claim itself, and the heartbeat count, so a silent observer is
    distinguishable from a quiet one and never read as a negative.

It writes summary.txt beside the CSV and changes nothing else.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [int]$CanonicalCount = 452
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\mapnew001\" + $Label)
if (-not (Test-Path -LiteralPath $runDir)) { throw "No such run directory: $runDir" }

$inputsPath = Join-Path $runDir 'inputs.json'
$csvPath = Join-Path $runDir 'live-map-identity.csv'
if (-not (Test-Path -LiteralPath $inputsPath)) { throw "Missing inputs.json in $runDir" }
if (-not (Test-Path -LiteralPath $csvPath)) { throw "Missing live-map-identity.csv in $runDir" }

$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json
$rows = Import-Csv -LiteralPath $csvPath

$lines = New-Object System.Collections.Generic.List[string]
function Say([string]$text) { $lines.Add($text); Write-Output $text }

$romNow = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
Say "MAP-NEW-AUTHORING-001 session summary: $Label"
Say ''
Say 'IMAGE'
Say "  rom             : $($inputs.rom_path)"
Say "  rom sha256      : $($romNow)"
Say "  digest recorded : $($inputs.rom_sha256)"
Say "  unchanged       : $($romNow -eq $inputs.rom_sha256)"
Say "  rom size        : $($inputs.rom_size)"
Say "  savestate sha   : $($inputs.state_sha256)"
Say "  observer        : $($inputs.lua_path)"
Say "  mGBA            : $($inputs.mgba_version)"
Say ''

$live = @($rows | Where-Object { $_.kind -eq 'LIVE' })
$heartbeats = @($rows | Where-Object { $_.kind -eq 'HEARTBEAT' })
$unresolved = @($rows | Where-Object { $_.kind -eq 'UNRESOLVED' })

Say 'ROW BOUND'
Say "  rows in csv     : $($rows.Count)"
Say "  LIVE rows       : $($live.Count)"
Say "  HEARTBEAT rows  : $($heartbeats.Count)"
Say "  UNRESOLVED rows : $($unresolved.Count)"
if ($live.Count -eq 0) {
    Say ''
    Say '  NO LIVE ROW WAS EVER RESOLVED. Under docs/skills/mgba-runtime.md section 8'
    Say '  a silent channel with a silent liveness channel is NOTHING, not a negative:'
    Say '  the instrument is unproven. Re-run before drawing any conclusion.'
}
if ($heartbeats.Count -eq 0) {
    Say ''
    Say '  NO HEARTBEAT: the observer frame callback did not run. Treat the whole'
    Say '  session as unproven.'
}
Say ''

Say 'ENGINE-REPORTED IDENTITY'
if ($live.Count -gt 0) {
    $bases = @($live | ForEach-Object { $_.table_base } | Select-Object -Unique)
    $bounds = @($live | ForEach-Object { $_.row_bound } | Select-Object -Unique)
    Say "  table base(s)   : $($bases -join ', ')"
    Say "  row bound(s)    : $($bounds -join ', ')"
    $relocated = @($bases | Where-Object { $_ -ne '0x0808E2E0' })
    Say "  relocated       : $($relocated.Count -gt 0)"
    $against = @($live | ForEach-Object { $_.versus } | Select-Object -Unique)
    Say "  resolved versus : $($against -join ', ')"
    $above = @($live | Where-Object { $_.index -ne '' -and [int]$_.index -ge $CanonicalCount })
    Say "  rows past $CanonicalCount : $($above.Count)"
    if ($above.Count -gt 0) {
        $authored = $above[-1]
        Say "  AUTHORED ROW LOADED AT FRAME $($authored.frame): index=$($authored.index) " +
            "key=$($authored.key_hi)$($authored.key_lo) source=$($authored.source) " +
            "root=$($authored.root) slot0=$($authored.layer_0)"
    }
    Say ''
    Say '  identity timeline (index, versus, key, source word, root, BG0 slot):'
    foreach ($row in $live) {
        Say ("    f{0,-7} index={1,-4} versus={2,-12} key={3}{4} source={5} root={6} slot0={7}" -f `
            $row.frame, $row.index, $row.versus, $row.key_hi, $row.key_lo, $row.source, `
            $row.root, $row.layer_0)
    }
} else {
    Say '  none'
}
Say ''

Say 'MAP-IDENTITY TIMELINE'
if ($live.Count -gt 0) {
    foreach ($row in $live) {
        Say ("  frame {0,-7} index={1,-4} versus={2,-12} {3}" -f `
            $row.frame, $row.index, $row.versus, $row.note)
    }
} else {
    Say '  no map identity was ever observed'
}
Say ''

$summaryPath = Join-Path $runDir 'summary.txt'
$lines -join "`n" | Set-Content -LiteralPath $summaryPath -Encoding utf8
Write-Output ''
Write-Output "summary written: $summaryPath"
