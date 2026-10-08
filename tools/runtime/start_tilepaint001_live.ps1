<#
.SYNOPSIS
Relaunch the retail engine on the AUTHORED derivative, positioned in map 40.

.DESCRIPTION
MAP-TILE-PAINT-001 needs the engine to BUILD the map rather than inherit it from
a savestate, because a savestate restores emulated RAM and VRAM including the
already-assembled background, so a ROM-side map edit can never appear under it.
Measured: the retail and derivative runs' VRAM, palette, all four screenblocks
and IO registers were byte-identical under one state.

This script exists for the one experiment that resolves that: a HUMAN drives the
player out of the area and back in, which makes the engine re-read the map from
the ROM. The observer is a live-watch variant that latches the painted cell's
screenblock region every frame, so the before/after of the re-entry is captured
without anyone needing to press anything at the right instant.

It holds the emulator only as long as the caller's process lives, which is the
point: this is a foreground interactive launcher, not the unattended session
launcher. It still owns no deadline and kills nothing.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RomPath,
    [Parameter(Mandatory = $true)]
    [string]$RomSha256,
    [Parameter(Mandatory = $true)]
    [string]$StatePath,
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [string]$LuaPath,
    [string]$MGBPath,
    [string]$RequiredMGBVersion = '0.11',
    [ValidateRange(1, 33554432)]
    [UInt32]$ExpectedRomSize = 8388608,
    [ValidateRange(4, 60)]
    [int]$UiSettleSeconds = 12
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

if (-not $LuaPath) { $LuaPath = 'tools\runtime\tilepaint001_live_screenblock.lua' }
if (-not $MGBPath) {
    $MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
}

$resolvedRom = Resolve-Required $RomPath 'ROM'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion"
}

$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') {
    throw 'RomSha256 must be a full 64-character SHA-256 hex digest'
}
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romInfo.Length -ne $ExpectedRomSize -or $romHashBefore -ne $expected) {
    throw "ROM identity mismatch; run refused. Expected $expected, found $romHashBefore"
}

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; stop it first.'
}

$runDir = Join-Path $root ("build\tilepaint001\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    Remove-Item -LiteralPath $runDir -Recurse -Force
}
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
$workingState = Join-Path $runDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingState).Hash -ne $stateHash) {
    throw 'Savestate copy hash mismatch'
}

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'

@{
    label        = $Label
    rom_path     = $resolvedRom
    rom_sha256   = $romHashBefore
    state_sha256 = $stateHash
    lua_path     = $resolvedLua
    mgba_version = $mgbVersion
    run_dir      = $runDir
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

# One mechanism for every launcher: mGBA loads the state with -t and runs the
# observer with --script, so no Scripting window is opened, nothing takes the
# operator window, and the identity gates live with the flag that needs them.
. (Join-Path $PSScriptRoot 'mgba_session.ps1')
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $resolvedRom `
    -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
    -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected `
    -StatePath $workingState

Write-Output 'SESSION LIVE - leave and re-enter the area now'
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  rom      : $resolvedRom"
Write-Output "  rom hash : $romHashBefore"
Write-Output ''
Write-Output 'Close the mGBA window when done; then re-run the collector.'
