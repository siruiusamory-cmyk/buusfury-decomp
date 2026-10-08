<#
.SYNOPSIS
Start a COLD-BOOT acceptance session: battery save, no savestate, observer armed.

.DESCRIPTION
Every earlier Kibito comparison loaded a savestate whose EWRAM held decoded dialogue
captured on an older build. This launcher exists so the acceptance run has no state at
all: mGBA starts on the ROM, the game loads the battery save itself, and the observer
sees the game build its own dialogue cache.

What it refuses, and why each refusal is here:
  * an mGBA that is not the 0.11 dev build, because the observer needs its
    scripted-breakpoint API;
  * any ROM whose digest or size is not the exact pair the caller names, because
    "the final image" has to mean one file;
  * a missing battery save, because a cold boot with no save is a different
    experiment from the one this ticket asks for;
  * an existing run directory, so evidence is never appended to;
  * a running mGBA, so two sessions cannot share one save file.

It owns no waiting and no cleanup: it starts the emulator, prints the pid, and exits.
The operator ends the session by closing the window. Nothing is loaded with -t.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RomPath,
    [Parameter(Mandatory = $true)][string]$RomSha256,
    [Parameter(Mandatory = $true)][string]$SavePath,
    [Parameter(Mandatory = $true)][string]$Label,
    [string]$LuaPath = 'tools\runtime\friendv3_coldboot_probe.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11',
    [ValidateRange(1, 33554432)][UInt32]$ExpectedRomSize
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
$resolvedSave = Resolve-Required $SavePath 'Battery save'
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
$romHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romHash -ne $expected) {
    throw "ROM identity mismatch; run refused. Expected $expected, found $romHash"
}
if ($ExpectedRomSize -and $romInfo.Length -ne $ExpectedRomSize) {
    throw "ROM size mismatch; run refused. Expected $ExpectedRomSize, found $($romInfo.Length)"
}

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; refusing to race it. Stop it first.'
}

$runDir = Join-Path $root ("build\friendv3-coldboot\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir"
}
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

# The ROM and its save travel together under one basename, which is how mGBA finds a
# battery save. The save is copied into both places this environment has been seen to
# read from, and the copy is hash-verified, because a save that silently failed to
# copy would turn a cold boot into a fresh game and the run would look clean for the
# wrong reason.
$romCopy = Join-Path $runDir 'friendv3.gba'
$saveCopy = Join-Path $runDir 'friendv3.sav'
Copy-Item -LiteralPath $resolvedRom -Destination $romCopy
Copy-Item -LiteralPath $resolvedSave -Destination $saveCopy
$saveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedSave).Hash
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $saveCopy).Hash -ne $saveHash) {
    throw 'Battery save copy hash mismatch'
}
$saveDir = Join-Path $runDir 'save'
New-Item -ItemType Directory -Path $saveDir -Force | Out-Null
Copy-Item -LiteralPath $resolvedSave -Destination (Join-Path $saveDir 'friendv3.sav')

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$csv = Join-Path $runDir 'coldboot.csv'
$env:TOOLKIT031_OUT = $csv
$env:DIALOGUE_ROM_SIZE = $romInfo.Length

. (Join-Path $PSScriptRoot 'mgba_session.ps1')
# No -StatePath and no -t: this launch has no savestate at all.
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $romCopy `
    -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
    -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected

$identity = [ordered]@{
    label             = $Label
    mode              = 'cold boot, battery save, no savestate'
    rom_path          = $resolvedRom
    rom_sha256        = $romHash
    rom_size          = $romInfo.Length
    save_path         = $resolvedSave
    save_sha256       = $saveHash
    lua_path          = $resolvedLua
    mgba_path         = $resolvedMGB
    mgba_version      = $mgbVersion
    mgba_pid          = $process.Id
    csv_path          = $csv
    screenshot_dir    = $runDir
}
$identity | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

Write-Output 'SESSION LIVE'
Write-Output "  mGBA pid : $($process.Id)"
Write-Output "  run dir  : $runDir"
Write-Output "  rom      : $romHash ($($romInfo.Length) bytes)"
Write-Output "  save     : $saveHash"
Write-Output ''
Write-Output 'Play now. Nothing will close mGBA; end the session by closing its window.'
