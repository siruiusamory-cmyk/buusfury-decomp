<#
.SYNOPSIS
Wait for the operator to leave and re-enter, then capture - MAP-CHUNK-AUTHORING-001.

.DESCRIPTION
This is `capture_tilepaint001_afterrebuild.ps1`'s methodology, unchanged and for
the same measured reason: the engine only reads a map from ROM when it BUILDS it,
which happens on entering an area, so a capture taken under a savestate load is
decided by the state and not by the ROM. It therefore watches the observer's own
`snapshots.csv` and captures only after the target map has been observed to be
left and re-entered, the rebuild has settled, and the engine is still in the
target map.

Two things are added, both required by this ticket.

**The capture is raised to the foreground first.** A plain screen copy captures
whatever is on the desktop inside the emulator window's rectangle, so any
overlapping window is captured in its place. That was measured the hard way: a
first attempt produced a matched pair whose two frames were not even crops of the
same region, because the two runs' emulator windows sat at different screen
positions and a browser window covered a different part of each. The successor
cannot silently produce that pair - it raises the window, re-reads its rectangle
after the move, and reports the rectangle it actually copied.

**The observer's own evidence columns are carried into the record.** The
successor observer records the ROM size it is running and the address the
engine's live layer record holds for the watched chunk cell; both are copied
beside the image so the capture states which image was live and what the engine
resolved, rather than leaving either to be assumed.

It launches mGBA, loads the state, and exits. It owns no wait loop on the
emulator's lifetime, and it kills only the process it started.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$RomPath,
  [Parameter(Mandatory = $true)][string]$RomSha256,
  [Parameter(Mandatory = $true)][string]$StatePath,
  [Parameter(Mandatory = $true)][string]$Label,
  [Parameter(Mandatory = $true)][int]$TargetMapIndex,
  [string]$OutDir,
  [string]$MGBPath,
  [string]$LuaPath = 'tools\runtime\chunkauth001_watch_rebuild.lua',
  [string]$MGBVersion = '0.11',
  [int]$UiSettleSeconds = 12,
  [int]$TimeoutSeconds = 3600,
  [int]$PollSeconds = 5,
  # Seconds of no screenblock change required after the observed return, so the
  # capture cannot land on a half-rebuilt map.
  [int]$SettleSeconds = 12
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path

function Resolve-Required([string]$Path, [string]$What) {
  $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $root $Path }
  if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw "$What is missing: $candidate" }
  return (Resolve-Path -LiteralPath $candidate).Path
}

if (-not $MGBPath) {
  $MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
}
if (-not $OutDir) { $OutDir = Join-Path $root 'build\chunkauth001\proof' }

$resolvedMGB = Resolve-Required $MGBPath 'mGBA'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedRom = Resolve-Required $RomPath 'ROM'

$version = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $version.StartsWith($MGBVersion)) {
  throw "mGBA version mismatch: required $MGBVersion, found $version"
}
$romHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romHash -ne $RomSha256.Trim().ToUpperInvariant()) {
  throw "ROM identity mismatch: expected $RomSha256, found $romHash"
}
if (Get-Process mGBA -ErrorAction SilentlyContinue) { throw 'an mGBA process is already running' }

$runDir = Join-Path $OutDir $Label
if (Test-Path -LiteralPath $runDir) { Remove-Item -LiteralPath $runDir -Recurse -Force }
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
$workingState = Join-Path $runDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState

# One mechanism for every launcher: mGBA loads the state with -t and runs the
# observer with --script, so no Scripting window is opened, nothing takes the
# operator window, and the identity gates live with the flag that needs them.
. (Join-Path $PSScriptRoot 'mgba_session.ps1')
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $resolvedRom `
    -LuaPath $resolvedLua -ReadyPath (Join-Path $runDir 'lua-ready.txt') -MarkerPath (Join-Path $runDir 'marker.txt') -RunDir $runDir `
    -RequiredMGBVersion $MGBVersion -ExpectedRomSha256 $RomSha256 `
    -StatePath $workingState

$indexPath = Join-Path $runDir 'snapshots.csv'
@{
  label = $Label; rom = $resolvedRom; rom_hash = $romHash
  state_sha256 = $stateHash; mgba_version = $version; mgba_pid = $process.Id
  run_dir = $runDir; observer = $resolvedLua
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

Write-Output "READY - leave map $TargetMapIndex and re-enter it now"
Write-Output "  run dir : $runDir"
Write-Output "  pid  : $($process.Id)"
Write-Output "  watching: $indexPath"

# Wait for a leave-then-return, judged only on what the engine actually did.
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$rebuiltAt = $null
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds $PollSeconds
  if (-not (Test-Path -LiteralPath $indexPath)) { continue }
  $rows = Import-Csv -LiteralPath $indexPath -ErrorAction SilentlyContinue
  if (-not $rows) { continue }
  $leftRows = $rows | Where-Object {
  $_.map_index -and [int]$_.map_index -ne $TargetMapIndex
  }
  if (-not $leftRows) { continue }
  $lastLeft = ($leftRows | Select-Object -Last 1).snapshot
  $returnRows = $rows | Where-Object {
  $_.map_index -and [int]$_.map_index -eq $TargetMapIndex -and
  [int]$_.snapshot -gt [int]$lastLeft
  }
  if ($returnRows) {
  $rebuiltAt = ($returnRows | Select-Object -Last 1).snapshot
  break
  }
}

if (-not $rebuiltAt) {
  Write-Output 'TIMEOUT: no leave-and-return was observed; capture NOT taken'
  Write-Output "  snapshots: $indexPath"
  exit 2
}

# Settle: the rebuild must have FINISHED, not merely started. The observer only
# writes a new row when the engine's screenblock content changes, so "no new
# snapshot for SettleSeconds after the return" is the engine having stopped
# changing the background.
Write-Output "rebuild observed at snapshot $rebuiltAt; waiting for it to settle"
$settleDeadline = (Get-Date).AddSeconds($SettleSeconds)
$lastCount = -1
while ((Get-Date) -lt $settleDeadline) {
  Start-Sleep -Seconds 3
  $now = (Import-Csv -LiteralPath $indexPath -ErrorAction SilentlyContinue | Measure-Object).Count
  if ($now -ne $lastCount) {
  $lastCount = $now
  $settleDeadline = (Get-Date).AddSeconds($SettleSeconds)
  }
}
Write-Output "settled with $lastCount snapshot rows"

# The engine must still be in the target map at the moment of capture, or the
# frame is not the rebuilt map at all.
$finalRows = Import-Csv -LiteralPath $indexPath
$lastIndex = ($finalRows | Where-Object { $_.map_index } | Select-Object -Last 1).map_index
if ([int]$lastIndex -ne $TargetMapIndex) {
  Write-Output "REFUSED: engine is in map $lastIndex at capture time, not $TargetMapIndex"
  exit 3
}

# Raise the emulator before copying the screen, so an overlapping window cannot
# take its place in the frame.
& powershell -NoProfile -ExecutionPolicy Bypass `
  -File (Join-Path $PSScriptRoot 'capture_mgba_window.ps1') `
  -OutPath (Join-Path $runDir "$Label.png") -TitleMatch 'mGBA -' -BringToFront
if ($LASTEXITCODE -ne 0) { throw 'capture failed' }

Copy-Item -LiteralPath $indexPath -Destination (Join-Path $runDir 'snapshots-at-capture.csv') -Force
Write-Output "CAPTURED after rebuild (return snapshot $rebuiltAt, settled, map $lastIndex)"
Write-Output "  image : $(Join-Path $runDir "$Label.png")"
Get-Content -LiteralPath $indexPath
