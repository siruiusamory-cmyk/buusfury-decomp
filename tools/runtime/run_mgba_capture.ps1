<#
.SYNOPSIS
Launch a verified, isolated mGBA runtime and run one bounded read-only capture.

.DESCRIPTION
This preserves the proven ordering: launch GDB-halted, optionally inject Lua
into the new PID, wait for readiness, then let one capture client arm the
breakpoint and issue the first continue. Generated output stays under build/.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$StatePath,
    [UInt32]$Breakpoint = 0,
    [string[]]$AdditionalBreakpoint = @(),
    [string]$RomPath = 'roms\Dragon Ball Z - Buu''s Fury (U).gba',
    # Opt in to launching a GENERATED ROM by naming its exact expected digest.
    # Omitting this keeps the strict canonical-only guard unchanged.
    [string]$GeneratedRomSha256,
    [string]$MGBPath = 'build\tools\mgba-0.10.5\extracted\mGBA-0.10.5-win64\mGBA.exe',
    [string]$RequiredMGBVersion = '0.10.5',
    # Exact digest the resolved mGBA executable must have. Overriding it is a
    # deliberate act and stays an equality test; there is no accept-anything value.
    [string]$MGBSha256 = '5A3C98C2984DD04BD0D7C9378CDFAE937AE0D73A196C880BB2EECF3B254AF247',
    [string]$LuaPath,
    [switch]$LuaStartup,
    [int]$DumpRegister = 1,
    [UInt32]$DumpLength = 0x240,
    [ValidateRange(64, 1024)]
    [UInt32]$StackLength = 64,
    [UInt32]$LrFilter = 0,
    [UInt32]$DumpWord0Filter = 0,
    [UInt32]$PrimaryDumpWord0Filter = 0,
    [int]$DecreaseRegister = -1,
    [UInt32]$CompareDumpOffset = 0,
    [ValidateSet(1, 2, 4)]
    [UInt32]$CompareLength = 4,
    [int]$MaxStops = 20,
    [int]$WindowSeconds = 600,
    [switch]$ScanEwramPointers,
    [switch]$SkipLuaArmedMarker,
    [switch]$LeaveOpen,
    [switch]$DryRun,
    [UInt32]$Watchpoint = 0,
    [UInt32]$WatchpointLength = 2,
    [UInt32]$ReadAddress = 0,
    [UInt32]$ReadLength = 2
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$buildRoot = Join-Path $root 'build\runtime-captures'
$expectedRomSize = 8388608
$expectedRomSha256 = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'

function Resolve-RequiredFile([string]$Path, [string]$Label) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    } else {
        Join-Path $root $Path
    }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$Label is missing: $candidate"
    }
    return (Resolve-Path -LiteralPath $candidate).Path
}

function Test-GdbPortInUse {
    # Non-connecting, non-binding check: query the OS for active TCP listeners
    # on port 2345. This MUST NOT use TcpClient/BeginConnect/EndConnect because
    # completing a TCP handshake with mGBA steals its single GDB slot.
    $props = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties()
    foreach ($ep in $props.GetActiveTcpListeners()) {
        if ($ep.Port -eq 2345) { return $true }
    }
    return $false
}

$resolvedRom = Resolve-RequiredFile $RomPath 'ROM'
$resolvedState = Resolve-RequiredFile $StatePath 'savestate'
$resolvedMGB = Resolve-RequiredFile $MGBPath 'mGBA executable'

# Fail closed on emulator identity. The stable 0.10.5 install at
# C:\Program Files\mGBA was once overwritten in place by a 0.11 development
# build, so every capture silently ran an emulator the research tickets do not
# accept. Identity is the executable's bytes: a wrong binary can report any
# version string, so the version is kept only as the better error message and
# the digest below is the gate.
if ($RequiredMGBVersion) {
    $mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
    if (-not $mgbVersion) {
        throw "mGBA executable reports no version: $resolvedMGB"
    }
    if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
        throw ("mGBA version mismatch: required $RequiredMGBVersion, found " +
            "$mgbVersion at $resolvedMGB. Pass -RequiredMGBVersion to override " +
            'deliberately.')
    }
}
$mgbHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedMGB).Hash
if ($mgbHash -ne $MGBSha256.Trim().ToUpperInvariant()) {
    throw ("mGBA identity mismatch: required executable SHA-256 $MGBSha256, " +
        "found $mgbHash at $resolvedMGB. Pass -MGBSha256 to override deliberately.")
}

$resolvedLua = if ($LuaPath) { Resolve-RequiredFile $LuaPath 'Lua script' } else { $null }
if ($LuaStartup -and -not $resolvedLua) { throw 'LuaStartup requires LuaPath' }
$python = Resolve-RequiredFile (Join-Path $root '.venv\Scripts\python.exe') 'project Python'
if ($StackLength % 4 -ne 0) { throw 'StackLength must be a 4-byte multiple' }
$parsedAdditionalBreakpoints = @()
foreach ($item in $AdditionalBreakpoint) {
    foreach ($token in ($item -split ',')) {
        $normalized = $token.Trim()
        if (-not $normalized) { continue }
        try {
            $value = if ($normalized -match '^0[xX][0-9a-fA-F]+$') {
                [Convert]::ToUInt32($normalized.Substring(2), 16)
            } else {
                [Convert]::ToUInt32($normalized, 10)
            }
        } catch {
            throw "Invalid AdditionalBreakpoint value: $normalized"
        }
        if ($value -eq 0) { throw 'AdditionalBreakpoint entries must be nonzero' }
        $parsedAdditionalBreakpoints += $value
    }
}

# ROM identity gate.
#
# DEFAULT (canonical mode): the ROM must be the canonical image, byte for byte.
# This path is unchanged and is still the only behaviour when the caller says
# nothing, so every existing invocation keeps exactly the guard it had.
#
# GENERATED MODE: opting in requires -GeneratedRomSha256 with the EXACT expected
# digest of the generated image. The check is still an equality test against a
# caller-supplied constant -- there is deliberately no "accept anything" switch,
# no wildcard, and no way to skip verification. TOOLKIT-030 had to start mGBA by
# hand because this launcher could not run a generated ROM at all; that bypass,
# not the guard, is what this parameter removes.
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
$romMode = 'canonical'
if ($GeneratedRomSha256) {
    $expectedGenerated = $GeneratedRomSha256.Trim().ToUpperInvariant()
    if ($expectedGenerated -notmatch '^[0-9A-F]{64}$') {
        throw 'GeneratedRomSha256 must be a full 64-character SHA-256 hex digest'
    }
    if ($expectedGenerated -eq $expectedRomSha256) {
        throw ('GeneratedRomSha256 is the canonical digest; omit the parameter ' +
            'to run in canonical mode')
    }
    if ($romHashBefore -ne $expectedGenerated) {
        throw ("Generated ROM identity mismatch; capture refused before launch. " +
            "Expected $expectedGenerated, found $romHashBefore at $resolvedRom")
    }
    if ($romInfo.Length -ne $expectedRomSize) {
        throw 'Generated ROM size mismatch; capture refused before launch'
    }
    $romMode = 'generated'
} elseif ($romInfo.Length -ne $expectedRomSize -or $romHashBefore -ne $expectedRomSha256) {
    throw 'Canonical ROM identity mismatch; capture refused before launch'
}
$stateInfo = Get-Item -LiteralPath $resolvedState
$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
$identity = [ordered]@{
    rom_path = $resolvedRom
    rom_size = $romInfo.Length
    rom_sha256 = $romHashBefore
    rom_mode = $romMode
    state_path = $resolvedState
    state_size = $stateInfo.Length
    state_sha256 = $stateHash
    breakpoint = ('0x{0:X8}' -f $Breakpoint)
    additional_breakpoints = @($parsedAdditionalBreakpoints | ForEach-Object { '0x{0:X8}' -f $_ })
    lua_path = $resolvedLua
    lua_mode = if ($LuaStartup) { 'startup' } elseif ($resolvedLua) { 'ui-injection' } else { $null }
}

if ($DryRun) {
    $identity | ConvertTo-Json -Depth 3
    exit 0
}
if (Test-GdbPortInUse) {
    throw 'TCP port 2345 is already in use; refusing to interfere with another GDB owner'
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$runId = "$stamp-$([Guid]::NewGuid().ToString('N').Substring(0, 8))"
$runDir = Join-Path $buildRoot $runId
$saveDir = Join-Path $runDir 'save'
$captureDir = Join-Path $runDir 'capture'
$stopFile = Join-Path $runDir 'STOP-NOW.txt'
New-Item -ItemType Directory -Path $saveDir -Force | Out-Null
$workingState = Join-Path $runDir ('working-state' + $stateInfo.Extension)
Copy-Item -LiteralPath $resolvedState -Destination $workingState
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingState).Hash -ne $stateHash) {
    throw 'Working savestate copy identity mismatch'
}
$identity['run_id'] = $runId
$identity['working_state_path'] = $workingState
$identity | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $runDir 'inputs.json')

$process = $null
try {
    $startupLua = $null
    if ($resolvedLua -and $LuaStartup) {
        # Fail closed when this mGBA build has no --script flag. The official
        # 0.10.5 win64 release does NOT expose it: scripting is a build-time
        # option, and passing an unknown flag makes mGBA exit 1 immediately,
        # before it ever opens the GDB port. Without this check the failure
        # surfaces as the misleading downstream error 'mGBA exited before
        # opening the GDB port', which reads as an emulator/port problem and
        # sent one investigation looking at stale processes and savestates.
        # The UI-injection path (omit -LuaStartup) is the supported route on
        # such a build, and is what produced the P-011 capture.
        $helpText = (& $resolvedMGB --help 2>&1 | Out-String)
        if ($helpText -notmatch '--script') {
            throw ("This mGBA build does not support --script, so -LuaStartup " +
                   "cannot work: " + $resolvedMGB + ". Re-run without " +
                   "-LuaStartup to use UI injection instead.")
        }
        $startupLua = Join-Path $runDir 'startup.lua'
        $luaPathForScript = $resolvedLua -replace '\\', '/'
        $markerPathForScript = (Join-Path $runDir 'lua-done.txt') -replace '\\', '/'
        $readyPathForScript = (Join-Path $runDir 'lua-injected.txt') -replace '\\', '/'
        $bootstrap =
            ('rom011_marker_path = [[' + $markerPathForScript + ']]') + "`r`n" +
            ('dofile([[' + $luaPathForScript + ']])') + "`r`n" +
            ('local f=assert(io.open([[' + $readyPathForScript + ']], [[w]])); f:write([[ready]]); f:close()')
        Set-Content -LiteralPath $startupLua -Value $bootstrap -Encoding ascii
    }
    $mgbaArgs = @(
        '--gdb',
        '--savestate', ('"' + $workingState + '"'),
        '-C', ('savegamePath="' + $saveDir + '"'),
        '-C', 'mute=0'
    )
    if ($startupLua) { $mgbaArgs += @('--script', ('"' + $startupLua + '"')) }
    # The owner's dashboard input bridge, outside this repository and named only by an environment
    # variable, so no machine path is tracked here. Honoured only when this build has the flag; the
    # --help probe is skipped when the startup Lua above already proved it.
    $extraScript = $env:LOG1_MGBA_EXTRA_SCRIPT
    if (-not $extraScript) {
        $extraScript = [Environment]::GetEnvironmentVariable('LOG1_MGBA_EXTRA_SCRIPT', 'User')
    }
    if ($extraScript -and -not (Test-Path -LiteralPath $extraScript)) { $extraScript = $null }
    if ($extraScript) {
        if (-not $startupLua) {
            $extraHelp = (& $resolvedMGB --help 2>&1 | Out-String)
            if ($extraHelp -notmatch '--script') {
                throw ("LOG1_MGBA_EXTRA_SCRIPT is set, but this mGBA build does not support " +
                       "--script: " + $resolvedMGB + ". Unset it or use the 0.11 dev build.")
            }
        }
        $mgbaArgs += @('--script', ('"' + $extraScript + '"'))
    }
    $mgbaArgs += ('"' + $resolvedRom + '"')
    $process = Start-Process -FilePath $resolvedMGB -ArgumentList $mgbaArgs -PassThru

    $portDeadline = (Get-Date).AddSeconds(30)
    while (-not (Test-GdbPortInUse)) {
        $process.Refresh()
        if ($process.HasExited) { throw 'mGBA exited before opening the GDB port' }
        if ((Get-Date) -ge $portDeadline) { throw 'mGBA did not open TCP port 2345' }
        Start-Sleep -Milliseconds 200
    }
    Start-Sleep -Seconds 5

    if ($resolvedLua -and -not $LuaStartup) {
        $readyPath = Join-Path $runDir 'lua-injected.txt'
        $markerPath = Join-Path $runDir 'lua-done.txt'
        & powershell.exe -NoProfile -ExecutionPolicy Bypass `
            -File (Join-Path $root 'tools\runtime\inject_mgba_lua.ps1') `
            -TargetProcessId $process.Id `
            -LuaPath $resolvedLua `
            -ReadyPath $readyPath `
            -MarkerPath $markerPath | Out-Null
        if (-not $SkipLuaArmedMarker) {
            $armedPath = Join-Path $runDir 'armed-marker.txt'
            $armedDeadline = (Get-Date).AddSeconds(30)
            while (-not (Test-Path -LiteralPath $armedPath)) {
                $process.Refresh()
                if ($process.HasExited) { throw 'mGBA exited before Lua armed' }
                if ((Get-Date) -ge $armedDeadline) {
                    throw 'Lua did not create armed-marker.txt; use -SkipLuaArmedMarker only when the script has no armed marker'
                }
                Start-Sleep -Milliseconds 200
            }
        }
    }

    $captureArgs = @(
        '-u', '-m', 'tools.runtime.capture_mgba_event',
        '--output-dir', $captureDir,
        '--dump-register', "r$DumpRegister",
        '--dump-length', ('0x{0:X}' -f $DumpLength),
        '--stack-length', ('0x{0:X}' -f $StackLength),
        '--max-stops', [string]$MaxStops,
        '--window-seconds', [string]$WindowSeconds,
        '--stop-file', $stopFile
    )
    if ($Breakpoint -ne 0) {
        $captureArgs += '--breakpoint'
        $captureArgs += ('0x{0:X8}' -f $Breakpoint)
    }
    foreach ($address in $parsedAdditionalBreakpoints) {
        $captureArgs += '--additional-breakpoint'
        $captureArgs += ('0x{0:X8}' -f $address)
    }
    if ($resolvedLua) {
        $captureArgs += '--gameplay-tick-file'
        $captureArgs += (Join-Path $runDir 'frame-tick.txt')
    }
    if ($ScanEwramPointers) { $captureArgs += '--scan-ewram-pointers' }
    if ($LrFilter -ne 0) {
        $captureArgs += '--lr-filter'
        $captureArgs += ('0x{0:X8}' -f $LrFilter)
    }
    if ($DumpWord0Filter -ne 0) {
        $captureArgs += '--dump-word0-filter'
        $captureArgs += ('0x{0:X8}' -f $DumpWord0Filter)
    }
    if ($PrimaryDumpWord0Filter -ne 0) {
        if ($Breakpoint -eq 0) { throw 'PrimaryDumpWord0Filter requires Breakpoint' }
        $captureArgs += '--primary-dump-word0-filter'
        $captureArgs += ('0x{0:X8}' -f $PrimaryDumpWord0Filter)
    }
    if ($DecreaseRegister -ge 0) {
        if ($DecreaseRegister -gt 12) { throw 'DecreaseRegister must be 0 through 12' }
        $captureArgs += '--decrease-register'
        $captureArgs += ('r{0}' -f $DecreaseRegister)
        $captureArgs += '--compare-dump-offset'
        $captureArgs += ('0x{0:X}' -f $CompareDumpOffset)
        $captureArgs += '--compare-length'
        $captureArgs += [string]$CompareLength
    }
    if ($Watchpoint -ne 0) {
        $captureArgs += '--watchpoint'
        $captureArgs += ('0x{0:X8}' -f $Watchpoint)
        $captureArgs += '--watchpoint-length'
        $captureArgs += [string]$WatchpointLength
    }
    if ($ReadAddress -ne 0) {
        $captureArgs += '--read-address'
        $captureArgs += ('0x{0:X8}' -f $ReadAddress)
        $captureArgs += '--read-length'
        $captureArgs += [string]$ReadLength
    }
    Write-Output "Capture run: $runDir"
    Write-Output "When finished early, create: $stopFile"
    & $python @captureArgs
    if ($LASTEXITCODE -ne 0) { throw "capture client exited with code $LASTEXITCODE" }
} finally {
    if ($process -and -not $LeaveOpen) {
        $process.Refresh()
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            $process.WaitForExit(5000) | Out-Null
        }
    }
    $romHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
    if ($romHashAfter -ne $romHashBefore) {
        throw 'Original ROM identity changed during capture'
    }
    $stateHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
    if ($stateHashAfter -ne $stateHash) {
        throw 'Original savestate identity changed during capture'
    }
}
