<#
.SYNOPSIS
Start one SPRITE-NEW-RUNTIME-001 session and exit.

.DESCRIPTION
Launches mGBA on a caller-named image - the canonical ROM for the retail control
run, the derivative for the new-identity run - injects the read-only observer, and
EXITS. It holds no wait loop and owns no process lifetime: the operator (or the
observer's own tick budget) ends the session, and
finish_spritenew001_session.ps1 collects the evidence afterwards. Two earlier
projects killed a live session part-way through by owning the emulator's lifetime,
so this script deliberately does not.

WHY THERE IS NO SAVESTATE. A savestate restores the EWRAM and VRAM a previous run
assembled, including the actor's cached frame record at +0x30 and its frame
pointer at +0x54. A restored cache that already matches what the engine would
select makes the compositor return early ("nothing changed"), so the screen would
keep the PREVIOUS run's tiles and a correct image would look like a failure. The
image has to build the area itself, so the operator boots the image and loads the
saved game.

ARGUMENT SHAPE. mGBA's usage is `[option ...] file`, and `-C OPTION=VALUE` takes a
SEPARATE value argument, so the ROM must be the TRAILING positional argument and
must be passed BARE. Writing the ROM before the `-C` pair makes mGBA consume the
ROM path as the option's value and start with no game loaded. That fault presents
as the injector failing to see the loaded ROM title.

A BARE path only survives `Start-Process -ArgumentList` when it contains no
spaces: PowerShell joins the array with spaces and does not quote, so the canonical
image's own name ("Dragon Ball Z - Buu's Fury (U).gba") is delivered as several
arguments and mGBA opens nothing at all, and the process exits before the injector
can find it. Quoting the element is not a fix either - it reaches mGBA with the
quote characters included. The fix is to remove the spaces from the problem: the
image is copied into the run directory as `rom.gba`, its digest is re-verified
after the copy, and the emulator is handed that path. The source image is never
opened for writing and is re-verified by the finisher.

The image is verified by EXACT digest AND exact size before launch. The save beside
the source image is a private research input and stays read-only: a copy goes into
the run directory and that copy is what the emulator loads and writes.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RomPath,
    [Parameter(Mandatory = $true)][string]$RomSha256,
    [Parameter(Mandatory = $true)][ValidateRange(1, 33554432)][UInt32]$ExpectedRomSize,
    [Parameter(Mandatory = $true)][string]$Label,
    [string]$SavePath,
    # A savestate to stage beside the staged image. mGBA's command line has no
    # savestate flag, so this is not launched with one: the file is copied to
    # <run dir>\rom.ss1, which is the name and location mGBA itself writes and
    # reads state 1 from when it saves beside the ROM, and the operator loads it
    # with the emulator's own Load State action.
    [string]$SavestatePath,
    [ValidateSet('human', 'boot', 'menu')][string]$Script = 'human',
    [ValidateRange(120, 200000)][int]$Ticks = 3600,
    [string]$StructureAddress = '0x088005B4',
    [ValidateRange(0, 65535)][int]$SpriteId = 307,
    [string]$LuaPath,
    [string]$MGBPath,
    [string]$RequiredMGBVersion = '0.11',
    [ValidateRange(4, 60)][int]$UiSettleSeconds = 12,
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

if (-not $LuaPath) { $LuaPath = 'tools\runtime\spritenew001_observer.lua' }
if (-not $MGBPath) {
    $MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
}

$resolvedRom = Resolve-Required $RomPath 'ROM'
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
    throw "ROM identity mismatch; run refused. Expected $expected ($ExpectedRomSize bytes), found $romHashBefore ($($romInfo.Length) bytes)"
}

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; close it first.'
}

$resolvedSave = $null
$saveHash = ''
if ($SavePath) {
    $resolvedSave = Resolve-Required $SavePath 'Save file'
    $saveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedSave).Hash
}

$runDir = Join-Path $root ("build\spritenew001\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir - pass a different -Label."
}
$outRoot = Join-Path $runDir 'out'

if ($DryRun) {
    Write-Output 'DRY RUN - nothing launched, nothing written'
    Write-Output "  label     : $Label"
    Write-Output "  rom       : $resolvedRom"
    Write-Output "  rom sha   : $romHashBefore (verified, $($romInfo.Length) bytes)"
    Write-Output "  save      : $(if ($resolvedSave) { $resolvedSave } else { '(none supplied)' })"
    Write-Output "  observer  : $resolvedLua"
    Write-Output "  mGBA      : $resolvedMGB ($mgbVersion)"
    Write-Output "  script    : $Script (ticks $Ticks)"
    Write-Output "  structure : $StructureAddress  sprite id $SpriteId"
    Write-Output "  run dir   : $runDir (would be created)"
    Write-Output "  mGBA busy : $(if (Get-Process mGBA -ErrorAction SilentlyContinue) { 'YES - close it first' } else { 'no' })"
    return
}

New-Item -ItemType Directory -Path $runDir -Force | Out-Null
New-Item -ItemType Directory -Path $outRoot -Force | Out-Null
$saveDir = Join-Path $runDir 'savegame'
New-Item -ItemType Directory -Path $saveDir -Force | Out-Null

# The staged image. A space-free path is the only form that survives
# Start-Process -ArgumentList unquoted, and quoting is not an option; see the
# comment block above. The copy is verified so the run is still pinned to the
# exact image the caller named.
$stagedRom = Join-Path $runDir 'rom.gba'
Copy-Item -LiteralPath $resolvedRom -Destination $stagedRom -Force
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $stagedRom).Hash -ne $romHashBefore) {
    throw 'Staged ROM copy hash mismatch'
}
if ((Get-Item -LiteralPath $stagedRom).Length -ne $ExpectedRomSize) {
    throw 'Staged ROM copy size mismatch'
}

if ($resolvedSave) {
    $saveName = [System.IO.Path]::GetFileNameWithoutExtension($stagedRom) + '.sav'
    $workingSave = Join-Path $saveDir $saveName
    Copy-Item -LiteralPath $resolvedSave -Destination $workingSave
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingSave).Hash -ne $saveHash) {
        throw 'Save copy hash mismatch'
    }
}

$stagedState = $null
if ($SavestatePath) {
    $resolvedState = Resolve-Required $SavestatePath 'Savestate'
    $stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
    # State 1 beside the image, which is where mGBA itself reads and writes it.
    $stagedState = Join-Path $runDir 'rom.ss1'
    if (Test-Path -LiteralPath $stagedState) {
        throw "Staged savestate already exists: $stagedState"
    }
    Copy-Item -LiteralPath $resolvedState -Destination $stagedState
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $stagedState).Hash -ne $stateHash) {
        throw 'Staged savestate copy hash mismatch'
    }
}

# The state is loaded from the injected command, after the observer's dofile, by
# the emulator's own `emu:loadStateFile`. Quote characters do not survive
# PowerShell's SetValue into the Scripting prompt, so the path goes in a Lua
# long-bracket string, which is also what the mgba-runtime skill requires.
$postCommand = ''
if ($stagedState) {
    $luaState = $stagedState -replace '\\', '/'
    if ($luaState.Contains(']]')) {
        throw 'Savestate path contains an unsupported Lua long-string terminator'
    }
    $postCommand = 'emu:loadStateFile([[' + $luaState + ']])'
}

$ready = Join-Path $runDir 'lua-ready.txt'
$marker = Join-Path $runDir 'lua-marker.txt'

@{
    label              = $Label
    rom_path           = $resolvedRom
    rom_sha256         = $romHashBefore
    rom_size           = $romInfo.Length
    source_save_path   = $resolvedSave
    source_save_sha256 = $saveHash
    isolated_save_dir  = $saveDir
    lua_path           = $resolvedLua
    mgba_path          = $resolvedMGB
    mgba_version       = $mgbVersion
    script             = $Script
    ticks              = $Ticks
    structure_address  = $StructureAddress
    sprite_id          = $SpriteId
    run_dir            = $runDir
    out_root           = $outRoot
    staged_rom_path    = $stagedRom
    source_state_path  = $resolvedState
    staged_state_path  = $stagedState
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

# The observer reads these from the emulator's own environment.
$env:SPRITENEW001_OUT_ROOT = $outRoot
$env:SPRITENEW001_STRUCTURE = $StructureAddress
$env:SPRITENEW001_SPRITE_ID = "$SpriteId"
$env:SPRITENEW001_SCRIPT = $Script
$env:SPRITENEW001_TICKS = "$Ticks"

# One mechanism for every launcher: mGBA runs the observer with --script, so no
# Scripting window is opened, nothing takes the operator window, and the identity
# gates live with the flag that needs them. The savegame override and the state
# load (through the observer's own emu:loadStateFile) ride along.
. (Join-Path $PSScriptRoot 'mgba_session.ps1')
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $stagedRom `
    -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
    -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected `
    -ArgumentList @('-C', ('savegamePath=' + $saveDir)) `
    -PostCommand $postCommand

Write-Output 'SESSION LIVE'
Write-Output "  label    : $Label"
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  outputs  : $outRoot"
Write-Output "  rom hash : $romHashBefore"
Write-Output "  schedule : $Script (observer finishes after $Ticks frames)"
if ($stagedState) {
    Write-Output "  savestate: $stagedState"
    Write-Output "             loaded automatically after injection via emu:loadStateFile"
}
Write-Output ''
Write-Output 'Collect the evidence with:'
Write-Output "  powershell -NoProfile -ExecutionPolicy Bypass -File tools/runtime/finish_spritenew001_session.ps1 -Label $Label"
