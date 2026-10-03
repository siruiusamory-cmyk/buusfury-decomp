# ENEMY-RANDOMIZER-EXE-001 - the combined-mode runtime smoke.
#
#   pwsh scripts/smoke-combined-rom.ps1 -Rom <combined.gba>
#
# ONE internal combined test ROM (map-warp + enemy-placement + enemy-stat) is
# booted in the emulator. This is NOT the public combined application and it is
# NOT a validation project.
#
# WHAT IT ACTUALLY SHOWS, stated narrowly because an independent review measured
# the gap between this check and what an earlier version of this header claimed:
#
#   * mGBA opened the file and identified it as a Buu's Fury cartridge. The game
#     code in the window title comes from the cartridge header, which
#     randomization never touches, so this check would pass for any image with an
#     intact header.
#   * the emulator process stayed up for the hold window. mGBA does not exit when
#     the emulated game hangs, so this is NOT proof that the game did not crash.
#   * with no input the game never leaves the title screen, so NO randomized
#     placement, stat or warp is loaded, reached or exercised.
#
# So this is a load-and-stay-up check, and it is reported as one. Evidence that a
# randomized enemy is reachable at runtime already exists elsewhere and is not
# claimed here: RANDOMIZER-ENEMY-PACK-001's controlled A/B on one savestate read
# the engine's live placement records for a map whose slots were both randomized.
# Composition is proved at the byte level instead, in
# tests/integration/test_randomizer_combined_rom.py.
#
# The ROM is launched with an isolated `savegamePath`, so a boot smoke can never
# write the canonical roms/*.sav, and the canonical image is re-hashed afterwards.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Rom,
    [string] $MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string] $CanonicalRom = 'roms\Dragon Ball Z - Buu''s Fury (U).gba',
    [string] $WorkDir = 'build/combined-smoke/run',
    [int] $HoldSeconds = 40,
    [string] $ExpectedGameCode = 'DBZBUUSFURY'
)

$ErrorActionPreference = 'Stop'

# Everything this script needs is located relative to the checkout it is run from.
# There is deliberately no fallback to another working copy's path: a tracked
# script that names one machine's directory is a script nobody else can run, and
# the operator can always pass -MGBPath or -CanonicalRom explicitly.
function Resolve-RequiredFile([string] $Path, [string] $Label) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $repo $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$Label is not present at $candidate. Pass it explicitly if this checkout keeps it elsewhere."
    }
    return (Resolve-Path -LiteralPath $candidate).Path
}

$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $mgba = Resolve-RequiredFile $MGBPath 'the emulator'
    $rom = Resolve-RequiredFile $Rom 'the combined ROM'
    $canonical = Resolve-RequiredFile $CanonicalRom 'the canonical ROM'

    $before = (Get-FileHash $canonical -Algorithm SHA256).Hash
    $runDir = Join-Path $repo $WorkDir
    if (Test-Path $runDir) { Remove-Item $runDir -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $runDir | Out-Null

    Write-Host "booting      : $rom"
    Write-Host "emulator     : $mgba"
    Write-Host "isolated save: $runDir"

    # The ROM is the TRAILING POSITIONAL argument and is passed BARE: mGBA's usage
    # is `[option ...] file`, `-C OPTION=VALUE` takes a separate value argument,
    # and a quoted path reaches mGBA with the quote characters included.
    $process = Start-Process -FilePath $mgba `
        -ArgumentList @('-C', "savegamePath=$runDir", $rom) `
        -PassThru
    try {
        Start-Sleep -Seconds 8
        $process.Refresh()
        if ($process.HasExited) {
            throw "mGBA exited immediately with code $($process.ExitCode) - the image did not boot"
        }

        $windows = Get-Process -Id $process.Id | Select-Object -ExpandProperty MainWindowTitle
        Write-Host "window title : $windows"
        if ($windows -notmatch [regex]::Escape($ExpectedGameCode)) {
            throw "mGBA did not report the loaded game code ($ExpectedGameCode); title was '$windows'"
        }

        $deadline = (Get-Date).AddSeconds($HoldSeconds)
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Seconds 2
            $process.Refresh()
            if ($process.HasExited) {
                throw "mGBA exited during the hold window with code $($process.ExitCode) - the composed image crashed"
            }
        }
        Write-Host "held open    : $HoldSeconds s, process still alive"
    }
    finally {
        if (-not $process.HasExited) {
            $null = $process.CloseMainWindow()
            if (-not $process.WaitForExit(15000)) { $process.Kill() }
        }
    }

    $after = (Get-FileHash $canonical -Algorithm SHA256).Hash
    if ($after -ne $before) { throw "the canonical ROM changed during the smoke: $after" }
    if ($after -ne '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E') {
        throw "the canonical ROM is not canonical after the smoke: $after"
    }

    Write-Host ''
    Write-Host "COMBINED ROM LOAD SMOKE: PASS"
    Write-Host "  rom                  : $rom"
    Write-Host "  sha256               : $((Get-FileHash $rom -Algorithm SHA256).Hash)"
    Write-Host "  header game code     : $ExpectedGameCode"
    Write-Host "  emulator held open   : $HoldSeconds s without exit"
    Write-Host "  canonical ROM        : unchanged, still 940AD5F0...F059E"
    Write-Host ''
    Write-Host "This shows the emulator loaded the image and stayed up. It does NOT show"
    Write-Host "that the game ran without hanging, and no randomized data was exercised:"
    Write-Host "with no input the game never leaves the title screen."
}
finally {
    Pop-Location
}
