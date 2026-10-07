param(
    [Parameter(Mandatory = $true)]
    [string]$RomPath,
    [Parameter(Mandatory = $true)]
    [string]$LuaPath,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedState,
    [string]$MgbaPath = 'build\tools\mgba-0.10.5\extracted\mGBA-0.10.5-win64\mGBA.exe',
    [string]$RequiredMGBVersion = '0.10.5'
)

$ErrorActionPreference = 'Stop'
$expectedHash = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
# Repository root is derived from this script's own location, matching the
# convention in inject_mgba_lua.ps1. A hardcoded absolute path broke every
# clone that did not live at the original developer's path.
$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if (-not (Test-Path -LiteralPath (Join-Path $workspaceRoot 'tools\runtime') -PathType Container)) {
    throw ("Could not resolve the repository root from $PSScriptRoot. " +
        'Run this script from its tracked location at tools\runtime\ inside the repository.')
}
$allowedRuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot 'build\rom006'))
$resolvedLuaPath = [System.IO.Path]::GetFullPath($LuaPath)
$resolvedExpectedState = [System.IO.Path]::GetFullPath($ExpectedState)

# The ROM-006 expected-state contract. Each of the two bootstraps this launcher
# exists for writes exactly one named state directly beneath build\rom006, and
# only those two states are accepted. That is also what confines the stale-state
# removal below to the ignored bootstrap directory. Which Lua paths may run is
# NOT decided here: inject_mgba_lua.ps1 owns the single allowlist and performs
# the membership check.
$allowedStates = @(
    [System.IO.Path]::GetFullPath((Join-Path $allowedRuntimeRoot 'bootstrap.mss'))
    [System.IO.Path]::GetFullPath((Join-Path $allowedRuntimeRoot 'bootstrap-map4.mss'))
)
if ($resolvedExpectedState -notin $allowedStates) {
    throw 'ExpectedState must be a ROM-006 bootstrap state directly beneath build\rom006'
}
$LuaPath = $resolvedLuaPath
$ExpectedState = $resolvedExpectedState

# Fail closed on emulator identity. 0.10.5 is the build the two ROM-006
# bootstraps are written for: each opens with
# assert(emu:getGameCode() == "AGB-BG3E"), and the 0.11 development build reports
# the bare "BG3E" instead. The shared C:\Program Files install was measured
# holding 0.11.0.0, so the version is read from the binary and compared here,
# never inferred from the path, the filename or mere existence.
$resolvedMgb = if ([System.IO.Path]::IsPathRooted($MgbaPath)) {
    $MgbaPath
} else {
    Join-Path $workspaceRoot $MgbaPath
}
if (-not (Test-Path -LiteralPath $resolvedMgb -PathType Leaf)) {
    throw "mGBA executable is missing: $resolvedMgb"
}
$resolvedMgb = (Resolve-Path -LiteralPath $resolvedMgb).Path
$mgbVersion = (Get-Item -LiteralPath $resolvedMgb).VersionInfo.FileVersion
if (-not $mgbVersion) {
    throw "mGBA executable reports no version: $resolvedMgb"
}
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw ("mGBA version mismatch: required $RequiredMGBVersion, found " +
        "$mgbVersion at $resolvedMgb")
}

$rom = Get-Item -LiteralPath $RomPath
$beforeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $RomPath).Hash
$beforeMtime = $rom.LastWriteTimeUtc.Ticks
if ($rom.Length -ne 8388608 -or $beforeHash -ne $expectedHash) {
    throw 'Verified ROM identity mismatch before mGBA bootstrap'
}

$runtimeRoot = Split-Path -Parent $ExpectedState
$runRoot = Join-Path $runtimeRoot ('run-' + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Force -Path $runtimeRoot
$null = New-Item -ItemType Directory -Force -Path (Join-Path $runRoot 'save')
$null = New-Item -ItemType Directory -Force -Path (Join-Path $runRoot 'states')
$null = New-Item -ItemType Directory -Force -Path (Join-Path $runRoot 'screenshots')
if (Test-Path -LiteralPath $ExpectedState) {
    Remove-Item -LiteralPath $ExpectedState -Force
}

$arguments = @(
    '-C', ('savegamePath=' + (Join-Path $runRoot 'save')),
    '-C', ('savestatePath=' + (Join-Path $runRoot 'states')),
    '-C', ('screenshotPath=' + (Join-Path $runRoot 'screenshots')),
    '-C', 'mute=1',
    '-C', 'audioSync=0',
    '-C', 'videoSync=0',
    ('"' + $RomPath + '"')
)

$process = Start-Process -FilePath $resolvedMgb -ArgumentList $arguments -PassThru
try {
    # Injection is delegated. inject_mgba_lua.ps1 owns the Scripting-window UI
    # driver, the allowlist membership check and the bounded Run helper;
    # this launcher keeps only what is ROM-006-specific: the ROM gate and the
    # expected-state contract above, plus the wait below for the state the
    # bootstrap writes. The ready path is written by the injector only after the
    # bootstrap's dofile returns, so "armed" is an observed fact rather than an
    # assumption, and a bootstrap that throws on its opening getGameCode assert
    # reports here instead of as a 120-second wait for a state that could never
    # appear.
    & (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1') `
        -TargetProcessId $process.Id `
        -LuaPath $LuaPath `
        -ReadyPath (Join-Path $runRoot 'bootstrap-ready.txt')

    for ($attempt = 0; $attempt -lt 1200 -and -not (Test-Path -LiteralPath $ExpectedState); $attempt++) {
        Start-Sleep -Milliseconds 100
    }
    if (-not (Test-Path -LiteralPath $ExpectedState)) {
        throw 'Expected state was not created'
    }
}
finally {
    if (-not $process.HasExited) {
        $process.CloseMainWindow() | Out-Null
        Start-Sleep -Milliseconds 500
        if (-not $process.HasExited) { $process.Kill() }
    }
}

$afterRom = Get-Item -LiteralPath $RomPath
$afterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $RomPath).Hash
if ($afterHash -ne $beforeHash -or $afterRom.Length -ne $rom.Length -or $afterRom.LastWriteTimeUtc.Ticks -ne $beforeMtime) {
    throw 'ROM changed during mGBA bootstrap'
}

Get-Item -LiteralPath $ExpectedState | Select-Object FullName,Length,LastWriteTime
Write-Output "ROM_SHA256=$afterHash"
Write-Output "ROM_MTIME_UTC_TICKS=$($afterRom.LastWriteTimeUtc.Ticks)"
