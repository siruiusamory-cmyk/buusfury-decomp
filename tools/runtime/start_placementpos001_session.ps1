<#
.SYNOPSIS
Start the PLACEMENT-POS-001 Phase 1 human-play capture and RETURN, leaving mGBA
running. The operator drives gameplay; this script never waits and never kills.

.DESCRIPTION
PLACEMENT-POS-001 Phase 1 needs to witness a placement being CONSTRUCTED, which
happens during a live map load. The staged read-only observer
(placementpos001_construct_watch.lua) breaks at the construction store PCs
0x0800FDD2 / 0x0800FDD8 (capturing r4 = actor base, actor+0x1A0, actor+0x1A4)
and at 0x0800FDC8 (raw halfwords via r5), with a liveness breakpoint at the
shared interpreter 0x08004038.

This is the human-play, free-running-core vehicle on the 0.11 dev build (which
has emu:setBreakpoint), NOT the 0.10.5 GDB launcher. It mirrors
start_toolkit031_session.ps1 exactly, because that ordering is proven:

  verify emulator version from the binary (not the path)
    -> verify canonical Buu ROM by exact SHA-256 (equality, no wildcard)
    -> refuse to race an existing mGBA process
    -> copy the savestate into an ignored run dir, verify the copy
    -> launch mGBA on canonical Buu
    -> inject the observer via inject_mgba_lua.ps1
    -> load the savestate AFTER injection (so construction triggers are not missed)
    -> print the PID and EXIT, holding nothing

It owns NO wait loop, NO finally-block kill, NO Start-Job, and NO setup-counting
deadline (mgba-runtime SKILL section 4: two separate bugs of exactly those
shapes killed live sessions). The operator ends the session by closing the mGBA
window; evidence is collected afterwards by finish_placementpos001_session.ps1.

Read-only: no emulated memory is written and no input is driven by any script
here. The map transition that fires the construction breakpoint is produced by
the human walking the player, never by this tooling.
#>
[CmdletBinding()]
param(
    # Canonical Buu by default; both are still verified by hash below.
    [string]$RomPath = 'roms\Dragon Ball Z - Buu''s Fury (U).gba',
    [string]$RomSha256 = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E',
    # The map-39 doorway state (node 666922c9): sitting here, walking through the
    # doorway triggers a transition, and the destination map's placements are
    # constructed then -- which is when the breakpoint fires.
    [string]$StatePath = 'build\rom012\postload-live-01\input.ss1',
    [string]$StateSha256 = '58228E1DC4CE81C80182242B650E18C0EE3DB71F79473A614E5E373DE207E0F7',
    [string]$Label = ('run-' + (Get-Date -Format 'yyyyMMdd-HHmmss')),
    [string]$LuaPath = 'tools\runtime\placementpos001_construct_watch.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    # The 0.11 dev build is required: it exposes emu:setBreakpoint. The 0.10.5
    # stable build does not, and the stable install was once overwritten in
    # place by a 0.11 build, so identity is verified from the binary, not the path.
    [string]$RequiredMGBVersion = '0.11',
    [ValidateRange(1, 33554432)]
    [UInt32]$ExpectedRomSize = 8388608
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
function Resolve-Required([string]$Path, [string]$What) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $root $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$What is missing: $candidate"
    }
    return (Resolve-Path -LiteralPath $candidate).Path
}

$resolvedRom = Resolve-Required $RomPath 'ROM'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

# Emulator identity from the binary, not the path.
$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion) { throw "mGBA executable reports no version: $resolvedMGB" }
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}

# ROM identity: an equality test against the canonical digest. No wildcard, no skip.
$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') {
    throw 'RomSha256 must be a full 64-character SHA-256 hex digest'
}
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romInfo.Length -ne $ExpectedRomSize -or $romHashBefore -ne $expected) {
    throw "ROM identity mismatch; run refused. Expected $expected, found $romHashBefore"
}

# Savestate identity: also an equality test, so a wrong/edited state cannot be
# passed off as the map-39 doorway state.
$expectedState = $StateSha256.Trim().ToUpperInvariant()
if ($expectedState -notmatch '^[0-9A-F]{64}$') {
    throw 'StateSha256 must be a full 64-character SHA-256 hex digest'
}
$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
if ($stateHash -ne $expectedState) {
    throw "Savestate identity mismatch; run refused. Expected $expectedState, found $stateHash"
}

# Refuse to race an existing emulator. A stale process would also hold the GDB
# TCP slot, but this vehicle is UI-injected, so the process check is the guard.
if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; refusing to race it. Stop it first.'
}
# Belt and braces on the port an orphan could still hold, using the same
# non-connecting query the GDB launcher uses (a connect would steal the slot).
$props = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties()
foreach ($ep in $props.GetActiveTcpListeners()) {
    if ($ep.Port -eq 2345) {
        throw 'TCP port 2345 has an owner (orphaned mGBA?); refusing to launch. Stop it first.'
    }
}

$runDir = Join-Path $root ("build\placementpos001\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir"
}
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$workingState = Join-Path $runDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingState).Hash -ne $stateHash) {
    throw 'Savestate copy hash mismatch'
}

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$csv = Join-Path $runDir 'placementpos001-construct.csv'

# The observer reads its output path from the environment, and mGBA (the child
# that runs the Lua) must inherit it, so set it BEFORE launching mGBA.
$env:PLACEMENTPOS001_OUT = $csv

$process = Start-Process -FilePath $resolvedMGB -ArgumentList @('"' + $resolvedRom + '"') -PassThru
Start-Sleep -Seconds 8

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1') `
    -TargetProcessId $process.Id -LuaPath $resolvedLua `
    -ReadyPath $ready -MarkerPath $marker
if ($LASTEXITCODE -ne 0) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw 'Lua injection failed'
}

# Load the state only AFTER the observer is armed, so the construction
# breakpoint is already installed when the destination map's entities are built.
& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'toolkit031_load_state.ps1') `
    -TargetProcessId $process.Id -StatePath $workingState
if ($LASTEXITCODE -ne 0) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw 'Savestate load failed'
}

$identity = [ordered]@{
    label             = $Label
    ticket            = 'PLACEMENT-POS-001'
    phase             = 1
    rom_path          = $resolvedRom
    rom_sha256        = $romHashBefore
    rom_size          = $romInfo.Length
    expected_rom_size = $ExpectedRomSize
    state_path        = $resolvedState
    state_sha256      = $stateHash
    lua_path          = $resolvedLua
    mgba_path         = $resolvedMGB
    mgba_version      = $mgbVersion
    mgba_pid          = $process.Id
    csv_path          = $csv
}
$identity | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

Write-Output 'PLACEMENT-POS-001 SESSION LIVE'
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  evidence : $csv"
Write-Output ''
Write-Output 'Observer armed. You are on the map-39 doorway state.'
Write-Output 'Walk the player THROUGH THE DOORWAY into the next area to construct'
Write-Output 'its placements, then screenshot the visible type-86 object and note'
Write-Output 'roughly where on screen it sits. Nothing will close mGBA; end the'
Write-Output 'session by closing its window, then run finish_placementpos001_session.ps1.'
