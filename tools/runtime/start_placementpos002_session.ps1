<#
.SYNOPSIS
Start the PLACEMENT-POS-001 Phase 2 human-play capture on a GENERATED ROM and
RETURN, leaving mGBA running. The operator drives gameplay; this never waits or
kills.

.DESCRIPTION
Phase 2 loads a GENERATED Buu image (an authored +1 placement clone at a chosen
position, built by build/toolkit029/build_map40.py) so a placement at a KNOWN
mutated coordinate constructs and is visible in-game. The settled observer
(placementpos001_construct_watch.lua, 0x0800FDDA trap) captures actor+0x1A0 and
actor+0x1A4 for that construction; the operator screenshots the visible object.

Same proven launch-and-exit ordering as start_placementpos001_session.ps1, with
two differences: the ROM is a GENERATED image verified by its EXACT caller-named
SHA-256 (equality, no wildcard, no skip; refusing the canonical digest here), and
the savestate is the MAP-40 state (roms/...ss1, 2d5740a8...) that actually loads
map 40. Canonical ROM is NEVER launched or touched by this script.

Construction fires on a fresh MAP LOAD. A savestate restore alone does NOT
re-run construction, so after the state loads the operator must cause map 40 to
LOAD (walk out of the room and back / re-enter) with the observer already armed.

It owns NO wait loop, NO finally-block kill, NO Start-Job, NO setup-counting
deadline (mgba-runtime SKILL section 4). The operator ends the session by
closing the mGBA window; evidence is collected by
finish_placementpos002_session.ps1.

Read-only: no emulated memory is written and no input is driven by any script.
#>
[CmdletBinding()]
param(
    # The GENERATED ROM under build/ and its EXACT digest. No default: Phase 2
    # is always about a specific mutated image, so the caller must name both.
    [Parameter(Mandatory = $true)]
    [string]$RomPath,
    [Parameter(Mandatory = $true)]
    [string]$RomSha256,
    # The map-40 state the private savestate loads into (node 3d1b05df).
    [string]$StatePath = 'roms\Dragon Ball Z - Buu''s Fury (U).ss1',
    [string]$StateSha256 = '2D5740A8C54180D153024A11B0E4D1143306957AF55A3AD0664C71CF7D9A1AAB',
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [string]$LuaPath = 'tools\runtime\placementpos001_construct_watch.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11',
    [ValidateRange(1, 33554432)]
    [UInt32]$ExpectedRomSize = 8388608
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$canonicalSha = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
function Resolve-Required([string]$Path, [string]$What) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $root $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$What is missing: $candidate"
    }
    return (Resolve-Path -LiteralPath $candidate).Path
}

$resolvedRom = Resolve-Required $RomPath 'generated ROM'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

# The generated ROM must live under build/ so the canonical image cannot be
# passed here by mistake.
$buildRoot = [System.IO.Path]::GetFullPath((Join-Path $root 'build')).TrimEnd('\') + '\'
if (-not $resolvedRom.StartsWith($buildRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Generated ROM must live under build/: $resolvedRom"
}

# Emulator identity from the binary, not the path (0.11 dev has emu:setBreakpoint).
$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion) { throw "mGBA executable reports no version: $resolvedMGB" }
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}

# Generated ROM identity: an equality test against the caller's digest. Refuse
# the canonical digest outright -- Phase 2 must never run the canonical image.
$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') {
    throw 'RomSha256 must be a full 64-character SHA-256 hex digest'
}
if ($expected -eq $canonicalSha) {
    throw 'RomSha256 is the canonical digest; Phase 2 runs GENERATED ROMs only'
}
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romInfo.Length -ne $ExpectedRomSize -or $romHashBefore -ne $expected) {
    throw "Generated ROM identity mismatch; run refused. Expected $expected, found $romHashBefore"
}

# Savestate identity: equality test on the map-40 state.
$expectedState = $StateSha256.Trim().ToUpperInvariant()
if ($expectedState -notmatch '^[0-9A-F]{64}$') {
    throw 'StateSha256 must be a full 64-character SHA-256 hex digest'
}
$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
if ($stateHash -ne $expectedState) {
    throw "Savestate identity mismatch; run refused. Expected $expectedState, found $stateHash"
}

# Refuse to race an existing emulator or an orphan on the GDB port.
if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; refusing to race it. Stop it first.'
}
$props = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties()
foreach ($ep in $props.GetActiveTcpListeners()) {
    if ($ep.Port -eq 2345) {
        throw 'TCP port 2345 has an owner (orphaned mGBA?); refusing to launch. Stop it first.'
    }
}

$runDir = Join-Path $root ("build\placementpos002\" + $Label)
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
$csv = Join-Path $runDir 'placementpos002-construct.csv'

# mGBA (the child that runs the Lua) must inherit the output path, so set it
# before launching.
$env:PLACEMENTPOS001_OUT = $csv

# One mechanism for every launcher: mGBA loads the state with -t and runs the
# observer with --script, so no Scripting window is opened, nothing takes the
# operator window, and the identity gates live with the flag that needs them.
. (Join-Path $PSScriptRoot 'mgba_session.ps1')
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $resolvedRom `
    -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
    -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected `
    -StatePath $workingState

$identity = [ordered]@{
    label             = $Label
    ticket            = 'PLACEMENT-POS-001'
    phase             = 2
    rom_path          = $resolvedRom
    rom_sha256        = $romHashBefore
    rom_is_generated  = $true
    rom_size          = $romInfo.Length
    canonical_sha256  = $canonicalSha
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

Write-Output 'PLACEMENT-POS-002 SESSION LIVE (generated ROM)'
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  gen ROM  : $resolvedRom"
Write-Output "  gen sha  : $romHashBefore"
Write-Output "  run dir  : $runDir"
Write-Output "  evidence : $csv"
Write-Output ''
Write-Output 'Observer armed on map 40. To construct the mutated clone, RE-ENTER'
Write-Output 'map 40 (walk out of the room and back / cross the load boundary) so'
Write-Output 'the placements reconstruct. When the clone is visible, capture a screenshot'
Write-Output '(scratchpad/shot.ps1 -TargetPid ' + $process.Id + ').'
Write-Output 'Nothing will close mGBA; end the session by closing its window, then'
Write-Output 'run finish_placementpos002_session.ps1 -Label ' + $Label + '.'
