# Run one unattended dialogue-probe session against a derivative image.
#
# Two phases, deliberately separate, because the launcher must not own the
# emulator's lifetime (docs/skills/mgba-runtime.md section 4):
#
#   -Phase start   stages a run directory, copies and verifies the savestate,
#                  launches through Start-MgbaSession, writes the PID, and exits.
#   -Phase finish  waits for the observer's own completion marker (it stops itself
#                  at 3000 frames), stops that PID, re-verifies the image digest,
#                  and prints the summary row the comparison needs.
#
# Identity is checked three times: the launcher's own -RequiredMGBVersion and
# -ExpectedRomSha256 gates, and the digest again in this script before and after.
# Nothing here writes to a source image or a savestate.

param(
    [Parameter(Mandatory)][ValidateSet('start', 'finish')][string]$Phase,
    [Parameter(Mandatory)][string]$RomPath,
    [Parameter(Mandatory)][string]$ExpectedRomSha256,
    [Parameter(Mandatory)][string]$RunDir,
    [Parameter(Mandatory)][string]$StatePath,
    [string]$MGBPath = '',
    [int]$TimeoutSeconds = 600
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
# The 0.11 dev build is the only one with Lua breakpoints. It, and the
# savestates, live in the working checkout rather than in this ticket's
# worktree, because `build/` and `roms/` are not shared with a worktree. Both are
# therefore passed in and neither has a default: naming a commercial image's save
# state in a tracked file is both a machine-specific path and a proprietary
# filename, and the gates refuse both.
if (-not $MGBPath) {
    $MGBPath = Join-Path $root 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
}
$mgb = $MGBPath
$observer = Join-Path $root 'tools\runtime\dialogue_strip_probe.lua'
$driver = Join-Path $root 'tools\runtime\npc_talk_driver.lua'
$pidFile = Join-Path $RunDir 'mgba.pid'
$marker = Join-Path $RunDir 'lua-marker.txt'
$ready = Join-Path $RunDir 'lua-ready.txt'
$csv = Join-Path $RunDir 'strip-probe.csv'
$workingState = Join-Path $RunDir 'working-state.ss1'

function Get-Digest([string]$Path) {
    (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

if ($Phase -eq 'start') {
    if (-not (Test-Path -LiteralPath $mgb)) { throw "emulator not found: $mgb" }
    $version = (Get-Item -LiteralPath $mgb).VersionInfo.FileVersion
    if (-not $version.StartsWith('0.11')) { throw "mGBA 0.11 required, found $version" }
    if ((Get-Digest $RomPath) -ne $ExpectedRomSha256.ToLowerInvariant()) {
        throw 'image digest does not match the declared one'
    }
    $running = Get-Process -Name 'mGBA' -ErrorAction SilentlyContinue
    if ($running) {
        throw "refusing to race an existing mGBA process: $($running.Id -join ', ')"
    }
    if (Test-Path -LiteralPath $RunDir) { throw "run directory already exists: $RunDir" }
    New-Item -ItemType Directory -Path $RunDir | Out-Null

    # The savestate is immutable input: copy it in, then verify the copy.
    Copy-Item -LiteralPath $StatePath -Destination $workingState
    if ((Get-Digest $workingState) -ne (Get-Digest $StatePath)) {
        throw 'the savestate copy does not match its source'
    }
    $env:TOOLKIT031_OUT = $csv
    Remove-Item Env:\DIALOGUE_EXPAND_ADDR -ErrorAction SilentlyContinue

    . (Join-Path $root 'tools\runtime\mgba_session.ps1')
    $process = Start-MgbaSession -MGBPath $mgb -RomPath $RomPath -LuaPath $observer `
        -ReadyPath $ready -MarkerPath $marker -RunDir $RunDir -RequiredMGBVersion '0.11' `
        -ExpectedRomSha256 $ExpectedRomSha256 -StatePath $workingState `
        -PostCommand ("dofile([[{0}]])" -f $driver)
    Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ascii
    Write-Output "started   : pid $($process.Id)"
    Write-Output "run dir   : $RunDir"
    Write-Output "csv       : $csv"
    exit 0
}

# --- finish -------------------------------------------------------------------
$imagePid = (Get-Content -LiteralPath $pidFile -Raw).Trim()
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    if (Test-Path -LiteralPath $marker) { break }
    Start-Sleep -Seconds 2
}
if (-not (Test-Path -LiteralPath $marker)) {
    Stop-Process -Id $imagePid -Force -ErrorAction SilentlyContinue
    throw "the observer never wrote its completion marker within $TimeoutSeconds s"
}
Start-Sleep -Seconds 2
Stop-Process -Id $imagePid -Force -ErrorAction SilentlyContinue
if ((Get-Digest $RomPath) -ne $ExpectedRomSha256.ToLowerInvariant()) {
    throw 'the image changed during the run'
}
Write-Output "marker    : $(Get-Content -LiteralPath $marker -Raw)"
Write-Output "frames    : $((Get-Content -LiteralPath $csv | Measure-Object -Line).Lines - 1) rows"
Get-Content -LiteralPath $csv | Select-String -Pattern 'SUMMARY|ROMCHECK' | ForEach-Object {
    Write-Output $_.Line
}
