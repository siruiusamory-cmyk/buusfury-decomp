<#
.SYNOPSIS
Run one bounded TOOLKIT-031 execution observation on a named ROM.

.DESCRIPTION
TOOLKIT-031 needs a FREE-RUNNING core: its evidence is a Lua scripted
breakpoint at the script trampoline, and the frame callback that bounds the run
only ticks while emulation actually advances. The tracked GDB launcher
(run_mgba_capture.ps1) halts the core and hands the single continue to the
capture client; in that mode this observer recorded zero frame ticks, so it
cannot be the vehicle here. This wrapper therefore drives the same proven
INJECTION path without GDB.

What it keeps from the canonical procedure (docs/runtime-capture.md):

  * exact ROM identity is verified BEFORE launch, against a digest the caller
    names -- there is no "accept anything" path;
  * the savestate is hashed and copied into a unique ignored run directory, and
    the copy is what gets loaded;
  * orphan mGBA processes are refused rather than raced;
  * Lua reaches the core through tools/runtime/inject_mgba_lua.ps1, which is
    allowlisted and PID-scoped;
  * the ROM hash is verified again after the run.

What it deliberately does NOT do: install GDB traps, or write emulated memory
or input. The observer is read-only.
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
    # Backstop only, for an unattended run. An attended run ends when the
    # operator closes mGBA or writes STOP-NOW.txt; see the wait loop below.
    [int]$RunSeconds = 3600
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$expectedRomSize = 8388608

function Resolve-Required([string]$Path, [string]$Label) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $root $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$Label is missing: $candidate"
    }
    return (Resolve-Path -LiteralPath $candidate).Path
}

$resolvedRom = Resolve-Required $RomPath 'ROM'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

# Emulator identity, from the binary rather than its path. The stable 0.10.5
# install was once overwritten in place by a 0.11 build, and this observer needs
# 0.11's scripted-breakpoint API, so the version actually matters here.
$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}

# ROM identity. The caller must name the exact digest; this is an equality test,
# never a pattern or a skip.
$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') {
    throw 'RomSha256 must be a full 64-character SHA-256 hex digest'
}
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romInfo.Length -ne $expectedRomSize -or $romHashBefore -ne $expected) {
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

$identity = [ordered]@{
    label          = $Label
    rom_path       = $resolvedRom
    rom_sha256     = $romHashBefore
    rom_size       = $romInfo.Length
    state_path     = $resolvedState
    state_sha256   = $stateHash
    lua_path       = $resolvedLua
    mgba_path      = $resolvedMGB
    mgba_version   = $mgbVersion
    run_seconds    = $RunSeconds
}
$identity | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$csv = Join-Path $runDir 'toolkit031-execution.csv'
$env:TOOLKIT031_OUT = $csv

$process = $null
try {
    # One mechanism for every launcher: mGBA loads the state with -t and runs the
    # observer with --script, so no Scripting window is opened, nothing takes the
    # operator window, and the identity gates live with the flag that needs them.
    . (Join-Path $PSScriptRoot 'mgba_session.ps1')
    $process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $resolvedRom `
        -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
        -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected `
        -StatePath $workingState

    # Wait for the OPERATOR to finish, not for a clock.
    #
    # An earlier version of this loop killed mGBA the moment -RunSeconds elapsed,
    # and the countdown included the ~20s of launch, injection and state load. It
    # therefore terminated the emulator part-way through a human play session
    # that was still generating the evidence, losing the fight/dialogue triggers
    # the run existed to test. An experiment whose triggers are human-driven must
    # never have its window closed underneath the human.
    #
    # The run now ends on an explicit signal:
    #   * the observer writes its marker (its own frame budget is reached), or
    #   * the operator closes the mGBA window, or
    #   * the operator creates STOP-NOW.txt in the run directory
    #     (the same early-finish convention the tracked GDB launcher uses).
    # -RunSeconds remains only as a backstop for an unattended run.
    $stopFile = Join-Path $runDir 'STOP-NOW.txt'
    Write-Output ''
    Write-Output 'mGBA is live and instrumented. Play now.'
    Write-Output '  finish early by closing the mGBA window, or by creating:'
    Write-Output "    $stopFile"
    Write-Output ''
    $deadline = (Get-Date).AddSeconds($RunSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $marker) { break }
        if (Test-Path -LiteralPath $stopFile) { break }
        if ($process.HasExited) { break }
        Start-Sleep -Seconds 2
    }
} finally {
    # Stop only the PID this script started, and only if it is still up: the
    # operator closing the window is a normal, expected way for a run to end.
    if ($process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
    Remove-Item Env:\TOOLKIT031_OUT -ErrorAction SilentlyContinue
}

$romHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romHashAfter -ne $romHashBefore) {
    throw "ROM changed during the run: $romHashBefore -> $romHashAfter"
}

Write-Output "run directory: $runDir"
if (Test-Path -LiteralPath $csv) {
    $rows = Get-Content -LiteralPath $csv
    Write-Output ("rows: " + $rows.Count)
    Write-Output ("EXEC rows: " + (@($rows | Where-Object { $_ -like 'EXEC,*' }).Count))
} else {
    Write-Output 'no observer output'
}
