<#
.SYNOPSIS
Start one human-played MAP-WARP-RUNTIME-EDIT-001 session and exit.

.DESCRIPTION
Launches mGBA on a caller-named ROM - the canonical image for the retail run, the
authored derivative for the authored run - injects the read-only transition
observer, loads the savestate AFTER injection (entities are built during the load,
so a trigger armed afterwards would miss them), prints the run directory and the
PID, and EXITS.

It holds no wait loop and kills nothing: the operator ends the session by closing
the mGBA window, and finish_warpedit001_session.ps1 collects the evidence
afterwards. Two earlier bugs killed a live session part-way through by owning the
emulator's lifetime, so this script deliberately does not.

The ROM is verified by EXACT digest before launch, so the retail run is pinned to
the canonical image and the authored run to the derivative the production build
emitted. The emulator binary's FileVersion is verified too: a shared system
install was once silently replaced by a development build.

The savestate is copied into the run directory and the copy is verified, so the
private original is never the file the emulator loads.
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
    [int]$UiSettleSeconds = 12,
    [switch]$DryRun
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

if (-not $LuaPath) { $LuaPath = 'tools\runtime\warpedit001_transition_watch.lua' }
if (-not $MGBPath) {
    # The emulator lives in this checkout's ignored build tree, named relative to
    # the repository root rather than to one machine; the version is still
    # verified from the binary below.
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
    throw 'An mGBA process is already running; close it first (a failed run can leave one holding the GDB port).'
}

$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash

# The save beside the ROM is a private research input and must stay read-only, so
# the emulator is pointed at a save directory inside the run directory instead of
# the one next to the image. Its hash is recorded here and re-checked afterwards.
$saveSibling = [System.IO.Path]::ChangeExtension($resolvedRom, '.sav')
$originalSaveHash = ''
if (Test-Path -LiteralPath $saveSibling -PathType Leaf) {
    $originalSaveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $saveSibling).Hash
}

$runDir = Join-Path $root ("build\warpedit001\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    # Refused rather than overwritten: a prior run directory is evidence, and
    # deleting it is how a session's observations get silently replaced.
    throw "Run directory already exists: $runDir - pass a different -Label."
}

if ($DryRun) {
    # Validate every input and write nothing, so a live human session is never
    # spent discovering a wrong digest or a missing observer.
    Write-Output 'DRY RUN - nothing launched, nothing written'
    Write-Output "  label     : $Label"
    Write-Output "  rom       : $resolvedRom"
    Write-Output "  rom sha   : $romHashBefore (verified, $($romInfo.Length) bytes)"
    Write-Output "  state     : $resolvedState"
    Write-Output "  state sha : $stateHash"
    Write-Output "  save      : $saveSibling"
    Write-Output "  save sha  : $(if ($originalSaveHash) { $originalSaveHash } else { '(no save beside this image)' })"
    Write-Output "  observer  : $resolvedLua"
    Write-Output "  mGBA      : $resolvedMGB ($mgbVersion)"
    Write-Output "  run dir   : $runDir (would be created)"
    Write-Output "  mGBA busy : $(if (Get-Process mGBA -ErrorAction SilentlyContinue) { 'YES - close it first' } else { 'no' })"
    return
}

New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$workingState = Join-Path $runDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingState).Hash -ne $stateHash) {
    throw 'Savestate copy hash mismatch'
}

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$saveDir = Join-Path $runDir 'savegame'
New-Item -ItemType Directory -Path $saveDir -Force | Out-Null

@{
    label                 = $Label
    rom_path              = $resolvedRom
    rom_sha256            = $romHashBefore
    rom_size              = $romInfo.Length
    state_path            = $resolvedState
    state_sha256          = $stateHash
    original_save_path    = $saveSibling
    original_save_sha256  = $originalSaveHash
    isolated_save_dir     = $saveDir
    lua_path              = $resolvedLua
    mgba_path             = $resolvedMGB
    mgba_version          = $mgbVersion
    run_dir               = $runDir
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

# The save directory override is what keeps the image's own save untouched; the
# proven capture launcher uses the same switch for the same reason.
$mgbaArgs = @(
    ('"' + $resolvedRom + '"'),
    '-C', ('savegamePath="' + $saveDir + '"')
)
$process = Start-Process -FilePath $resolvedMGB -ArgumentList $mgbaArgs -PassThru
Start-Sleep -Seconds $UiSettleSeconds

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1') `
    -TargetProcessId $process.Id -LuaPath $resolvedLua `
    -ReadyPath $ready -MarkerPath $marker
if ($LASTEXITCODE -ne 0) { throw 'Lua injection failed' }

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'toolkit031_load_state.ps1') `
    -TargetProcessId $process.Id -StatePath $workingState
if ($LASTEXITCODE -ne 0) { throw 'Savestate load failed' }

Write-Output 'SESSION LIVE - hand the keyboard to the operator now'
Write-Output "  label    : $Label"
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  rom      : $resolvedRom"
Write-Output "  rom hash : $romHashBefore"
Write-Output ''
Write-Output 'Close the mGBA window when done, then run:'
Write-Output "  powershell -NoProfile -ExecutionPolicy Bypass -File tools/runtime/finish_warpedit001_session.ps1 -Label $Label"
