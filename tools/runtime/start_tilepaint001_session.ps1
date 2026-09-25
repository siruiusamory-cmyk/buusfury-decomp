<#
.SYNOPSIS
Launch one MAP-TILE-PAINT-001 runtime run: mGBA + read-only Lua observer + state.

.DESCRIPTION
A thin, per-ticket instance of the proven TOOLKIT-031 session shape
(tools/runtime/start_toolkit031_session.ps1), which docs/runtime-capture.md and
the mgba-runtime skill both point at. It follows that script's hard rules
exactly:

  * emulator identity comes from the binary's FileVersion, never from the path
    (the stable install has been silently overwritten by a dev build before);
  * ROM identity is an EXACT caller-supplied SHA-256 equality test, with an
    optional -GeneratedRomSha256 for an authored derivative - there is no
    "accept anything" switch;
  * it refuses to race an existing mGBA process (a failed run leaves one holding
    TCP 2345, after which the other launcher fails closed forever);
  * it creates a unique run directory under build/ (ignored), hashes the
    savestate, copies it in and verifies the copy, so the operator's state is
    never the file mGBA writes to;
  * it LAUNCHES, INJECTS, LOADS THE STATE, PRINTS THE PID AND EXITS. It owns no
    wait loop and no cleanup, so nothing can tear the emulator down mid-run.
    Ending the session is the caller's business (a human closing the window, or
    an automated collector that has taken its screenshot);
  * injection happens BEFORE the state load, because the entities are built
    during the load and a breakpoint armed afterwards would miss them.

The observer must already be allowlisted in tools/runtime/inject_mgba_lua.ps1.

Read-only with respect to emulated state and input: no emulated memory is
written and no input is driven.
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
    [string]$LuaPath = 'tools\runtime\tilepaint001_live_screenblock.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11',
    [ValidateRange(1, 33554432)]
    [UInt32]$ExpectedRomSize = 8388608,
    # Windows the UI is given to finish building its menu bar before injection.
    # The proven session shape used 8s and this build has twice failed to have a
    # Scripting menu by then, right after a previous mGBA exited; the injector
    # reports that as 'Scripting menu item not found', which reads like a
    # missing feature rather than a race.
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

$resolvedRom = Resolve-Required $RomPath 'ROM'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
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
    throw 'An mGBA process is already running; refusing to race it. Stop it first.'
}

$runDir = Join-Path $root ("build\tilepaint001\" + $Label)
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

$process = Start-Process -FilePath $resolvedMGB -ArgumentList @('"' + $resolvedRom + '"') -PassThru
Start-Sleep -Seconds $UiSettleSeconds

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1') `
    -TargetProcessId $process.Id -LuaPath $resolvedLua `
    -ReadyPath $ready -MarkerPath $marker
if ($LASTEXITCODE -ne 0) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw 'Lua injection failed'
}

# Load the state only AFTER the observer is armed, so the callback is already
# installed when the engine constructs and uploads the map's background.
& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'toolkit031_load_state.ps1') `
    -TargetProcessId $process.Id -StatePath $workingState
if ($LASTEXITCODE -ne 0) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw 'Savestate load failed'
}

$identity = [ordered]@{
    label             = $Label
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
    run_dir           = $runDir
}
$identity | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

Write-Output 'SESSION LIVE'
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  observer : $resolvedLua"
Write-Output "  rom      : $resolvedRom"
Write-Output "  rom hash : $romHashBefore"
