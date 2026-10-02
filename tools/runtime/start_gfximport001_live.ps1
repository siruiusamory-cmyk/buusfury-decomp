<#
.SYNOPSIS
Start one human-played GRAPHICS-IMPORT-BOUNDARY-001 session and exit.

.DESCRIPTION
Launches mGBA on a caller-named image - the canonical ROM for the retail run,
the authored derivative for the authored run - injects the read-only sprite
observer, and EXITS. It holds no wait loop, starts no job and kills nothing: the
operator ends the session by closing the mGBA window, and
finish_gfximport001_session.ps1 collects the evidence afterwards. Two earlier
bugs killed a live session part-way through by owning the emulator's lifetime,
so this script deliberately does not.

WHY THERE IS NO SAVESTATE. A savestate restores the VRAM the previous run
assembled, so an image loaded into a settled area can never be shown to have
supplied the area's sprite graphics - the state did (MAP-TILE-PAINT-001 measured
two different ROMs giving byte-identical VRAM under one state). The area has to
be built during the session, so the operator boots the image and loads the saved
game. That is also why this launcher has no state parameter to misuse.

The image is verified by EXACT digest AND exact size before launch, so a retail
run is pinned to the canonical image and an authored run to the derivative the
production build emitted. The emulator binary's FileVersion is verified from the
binary rather than trusted from its path: a shared system install was once
silently replaced by a development build.

The save beside the source image is a private research input and stays
read-only. A copy is placed in the run directory and that copy is what the
emulator loads and writes, so the original is never touched.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RomPath,
    [Parameter(Mandatory = $true)]
    [string]$RomSha256,
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 33554432)]
    [UInt32]$ExpectedRomSize,
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [string]$SavePath,
    [string]$LuaPath,
    [string]$MGBPath,
    [string]$RequiredMGBVersion = '0.11',
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

if (-not $LuaPath) { $LuaPath = 'tools\runtime\gfximport001_pixel_proof.lua' }
if (-not $MGBPath) {
    # The emulator lives in this checkout's ignored build tree, named relative to
    # the repository root rather than to one machine; the version is still
    # verified from the binary below.
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
    throw 'An mGBA process is already running; close it first (a failed run can leave one holding the GDB port).'
}

$resolvedSave = $null
$saveHash = ''
if ($SavePath) {
    $resolvedSave = Resolve-Required $SavePath 'Save file'
    $saveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedSave).Hash
}

$runDir = Join-Path $root ("build\gfximport001\" + $Label)
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
    Write-Output "  save      : $(if ($resolvedSave) { $resolvedSave } else { '(none supplied)' })"
    Write-Output "  save sha  : $(if ($saveHash) { $saveHash } else { '(n/a)' })"
    Write-Output "  observer  : $resolvedLua"
    Write-Output "  mGBA      : $resolvedMGB ($mgbVersion)"
    Write-Output "  run dir   : $runDir (would be created)"
    Write-Output "  mGBA busy : $(if (Get-Process mGBA -ErrorAction SilentlyContinue) { 'YES - close it first' } else { 'no' })"
    return
}

New-Item -ItemType Directory -Path $runDir -Force | Out-Null
$saveDir = Join-Path $runDir 'savegame'
New-Item -ItemType Directory -Path $saveDir -Force | Out-Null

if ($resolvedSave) {
    # The emulator loads the battery save by the ROM's own stem, from the
    # overridden save directory, so the copy must carry that name.
    $saveName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedRom) + '.sav'
    $workingSave = Join-Path $saveDir $saveName
    Copy-Item -LiteralPath $resolvedSave -Destination $workingSave
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingSave).Hash -ne $saveHash) {
        throw 'Save copy hash mismatch'
    }
}

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'

@{
    label                = $Label
    rom_path             = $resolvedRom
    rom_sha256           = $romHashBefore
    rom_size             = $romInfo.Length
    source_save_path     = $resolvedSave
    source_save_sha256   = $saveHash
    isolated_save_dir    = $saveDir
    lua_path             = $resolvedLua
    mgba_path            = $resolvedMGB
    mgba_version         = $mgbVersion
    run_dir              = $runDir
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

# The save directory override is what keeps the source image's own save
# untouched; the proven capture launcher uses the same switch for the same
# reason.
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
if ($LASTEXITCODE -ne 0) {
    # The script deliberately does not stop the process it started. Killing an
    # mGBA window is what destroyed a live session twice, and the launcher that
    # follows refuses to race any running emulator, so the operator closes it and
    # the next run is told the truth rather than racing a hidden one.
    throw 'Lua injection failed - close the mGBA window before retrying'
}

Write-Output 'SESSION LIVE - hand the keyboard to the operator now'
Write-Output "  label    : $Label"
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  rom      : $resolvedRom"
Write-Output "  rom hash : $romHashBefore"
Write-Output ''
Write-Output 'Boot to the title screen, press Start, choose the saved game, and stand'
Write-Output 'still in the world for a few seconds. Then close the mGBA window.'
Write-Output "  powershell -NoProfile -ExecutionPolicy Bypass -File tools/runtime/finish_gfximport001_session.ps1 -Label $Label"
