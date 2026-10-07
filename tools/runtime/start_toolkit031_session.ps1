<#
.SYNOPSIS
Start an instrumented TOOLKIT-031 play session and RETURN, leaving mGBA running.

.DESCRIPTION
Separating "set the experiment up" from "wait for it to finish" is the whole
point of this script.

The earlier wrapper (run_toolkit031_watch.ps1) did both in one process, so the
emulator's lifetime was tied to the lifetime of the shell that launched it. Two
different failures came out of that, and both destroyed a human play session
already in progress:

  1. a -RunSeconds deadline that counted launch, injection and state load, then
     force-killed mGBA part-way through play; and
  2. the finally-block kill firing when the background job hosting the script
     was torn down, which ended the session after roughly twenty seconds.

Neither had anything to do with the experiment. So this script owns NO waiting
and NO cleanup: it verifies identity, launches mGBA, injects the read-only
observer, loads the savestate, prints the PID, and exits. mGBA keeps running,
because nothing is left holding it.

The operator ends the session by closing the mGBA window. Evidence is collected
afterwards by finish_toolkit031_session.ps1, which verifies the ROM hash again.

Read-only: no emulated memory is written and no input is driven.
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
    [string]$LuaPath = 'tools\runtime\toolkit031_execution_watch.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11',
    # The default continues to bind ordinary sessions to canonical Buu. An
    # expanded experiment must name its exact, hardware-window-bounded size
    # alongside its exact image digest; a hash alone must not turn size into an
    # implicit acceptance criterion.
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

# Emulator identity from the binary, not its path: the stable 0.10.5 install was
# once overwritten in place by a 0.11 build, and this observer needs 0.11's
# scripted-breakpoint API.
$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}

# ROM identity: an equality test against a digest the caller names. There is no
# wildcard and no skip.
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
    throw 'An mGBA process is already running; refusing to race it. Stop it first.'
}

$runDir = Join-Path $root ("build\toolkit031\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir"
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
$csv = Join-Path $runDir 'toolkit031-execution.csv'

# The observer reads its output path from the environment, and it must be the
# CHILD process that inherits it, so set it before launching mGBA.
$env:TOOLKIT031_OUT = $csv

# One mechanism for every launcher: mGBA loads the state with -t and runs the
# observer with --script, so no Scripting window is opened and nothing takes the
# operator window. See tools/runtime/mgba_session.ps1.
. (Join-Path $PSScriptRoot 'mgba_session.ps1')
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $resolvedRom `
    -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
    -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected `
    -StatePath $workingState
Set-Content -LiteralPath (Join-Path $runDir 'state-loaded.txt') -Value 'mGBA -t --script' -Encoding ascii

$identity = [ordered]@{
    label        = $Label
    rom_path     = $resolvedRom
    rom_sha256   = $romHashBefore
    rom_size     = $romInfo.Length
    expected_rom_size = $ExpectedRomSize
    state_path   = $resolvedState
    state_sha256 = $stateHash
    lua_path     = $resolvedLua
    mgba_path    = $resolvedMGB
    mgba_version = $mgbVersion
    mgba_pid     = $process.Id
    csv_path     = $csv
}
$identity | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

Write-Output "SESSION LIVE"
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  evidence : $csv"
Write-Output ''
Write-Output 'Play now. Nothing will close mGBA; end the session by closing its window.'
