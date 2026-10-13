# The one place that starts an instrumented mGBA session.
#
# Every launcher used to repeat the same four steps: start mGBA, sleep eight
# seconds, drive the Scripting window through UI Automation to send the observer,
# then load a savestate through the File dialog. That is three windows' worth of
# focus stealing and about seventeen seconds before the operator can play.
#
# mGBA can do all of it itself:
#   * `-t FILE` loads a savestate when starting
#   * `--script FILE` runs a script when starting
# so this helper renders a small bootstrap, hands both to mGBA, and gets out of
# the way. No Scripting window is opened and nothing takes the foreground.
#
# Governance is unchanged: `--script` leaves the injector's path, so the injector
# is still asked to run every one of its checks (allowlist, ready root, marker
# root, long-string terminator, pre-existence) before anything is launched. The
# caller keeps its own emulator-version and ROM-digest gates.

function Initialize-SessionWindow {
    # Windows refuses SetForegroundWindow from a process that does not already own
    # the foreground, so the caller's thread attaches its input to the foreground
    # thread for the duration of the call. That is the supported way to do this.
    if ('DbzSessionWindow' -as [type]) { return $true }
    try {
        Add-Type -Namespace '' -Name 'DbzSessionWindow' -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
[DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
[DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
'@
    } catch {
        return $false
    }
    return $true
}

function Set-SessionWindowFocus {
    param([Parameter(Mandatory)][IntPtr]$Target)
    if (-not (Initialize-SessionWindow)) { return $false }
    if ($Target -eq [IntPtr]::Zero) { return $false }
    $targetPid = 0
    $foreground = [DbzSessionWindow]::GetForegroundWindow()
    $foregroundThread = [DbzSessionWindow]::GetWindowThreadProcessId($foreground, [ref]$targetPid)
    $ownThread = [DbzSessionWindow]::GetCurrentThreadId()
    $attached = $false
    if ($foregroundThread -ne 0 -and $foregroundThread -ne $ownThread) {
        $attached = [DbzSessionWindow]::AttachThreadInput($ownThread, $foregroundThread, $true)
    }
    $ok = [DbzSessionWindow]::SetForegroundWindow($Target)
    if ($attached) {
        [void][DbzSessionWindow]::AttachThreadInput($ownThread, $foregroundThread, $false)
    }
    return $ok
}

function Register-SaveCatalogueRun {
    <#
    Records one staged run in the save catalogue, and never fails the launch.

    The catalogue is a separate tool (`python -m tools.save_catalogue`) that
    indexes every battery save and savestate on this machine; this is its one
    launcher call. It reads the identity block the launcher just wrote
    (`inputs.json`) and records the tool id, the label and the ROM, save and
    state hashes it names. Nothing here changes a gate or a launch decision: a
    missing interpreter or a refused record prints one line and the session
    continues, because an unindexed run is a lost note, not a failed run.

    Call it AFTER the launcher has written its inputs.json.
    #>
    param(
        [Parameter(Mandatory)][string]$RunDir,
        [Parameter(Mandatory)][string]$Tool,
        [Parameter(Mandatory)][string]$Label
    )
    $trailing = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
    $python = Join-Path $trailing '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        Write-Host "save catalogue SKIPPED: no interpreter at $python"
        return
    }
    $arguments = @('-m', 'tools.save_catalogue', 'record-run', '--run-dir', $RunDir,
                   '--tool', $Tool, '--label', $Label)
    Push-Location $trailing
    try {
        & $python @arguments 2>&1 | ForEach-Object { Write-Host "save catalogue: $_" }
    } catch {
        Write-Host "save catalogue SKIPPED: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
}

function Start-MgbaSession {
    <#
    Starts mGBA with the state loaded and the observer running, without opening the
    Scripting window. Returns the started process.

    -ArgumentList carries any extra mGBA options the caller needs, such as a
    savegame override. The ROM is always passed last and bare.
    #>
    param(
        [Parameter(Mandatory)][string]$MGBPath,
        [Parameter(Mandatory)][string]$RomPath,
        [Parameter(Mandatory)][string]$LuaPath,
        [Parameter(Mandatory)][string]$ReadyPath,
        [Parameter(Mandatory)][string]$MarkerPath,
        [Parameter(Mandatory)][string]$RunDir,
        [Parameter(Mandatory)][string]$RequiredMGBVersion,
        [Parameter(Mandatory)][string]$ExpectedRomSha256,
        [string]$StatePath,
        [string]$PostCommand,
        [string[]]$ArgumentList = @(),
        [int]$ReadyTimeoutSeconds = 20
    )

    # The identity gates live here, with the flag that makes them necessary.
    # `--script` leaves the injector's allowlist path, so a caller must not be able
    # to reach the emulator without naming the build and the exact ROM it expects.
    $mgbVersion = (Get-Item -LiteralPath $MGBPath).VersionInfo.FileVersion
    if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
        throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $MGBPath"
    }
    $expectedHash = $ExpectedRomSha256.Trim().ToUpperInvariant()
    if ($expectedHash -notmatch '^[0-9A-F]{64}$') {
        throw 'ExpectedRomSha256 must be a full 64-character SHA-256 hex digest'
    }
    $romHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $RomPath).Hash
    if ($romHash -ne $expectedHash) {
        throw "ROM identity mismatch; run refused. Expected $expectedHash, found $romHash"
    }

    $checkArgs = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1'),
        '-TargetProcessId', $PID,
        '-LuaPath', $LuaPath,
        '-ReadyPath', $ReadyPath,
        '-MarkerPath', $MarkerPath,
        '-CheckOnly'
    )
    & powershell @checkArgs | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Observer rejected by the allowlist or the path rules'
    }

    if (Test-Path -LiteralPath $ReadyPath) { Remove-Item -LiteralPath $ReadyPath -Force }
    if (Test-Path -LiteralPath $MarkerPath) { Remove-Item -LiteralPath $MarkerPath -Force }

    # The savestate is loaded by the bootstrap, NOT by mGBA's `-t`. Measured: with
    # `-t` the state is already in memory when `--script` runs, so an observer
    # would arm too late to see anything the load itself constructs - which is
    # exactly what several observers exist to catch. Loading it here, after the
    # observer is armed, reproduces the ordering the dialog flow had.
    # -PostCommand is Lua that runs after the observer and before the ready marker.
    # It is composed into the bootstrap, so it no longer passes through the
    # injector's prompt validation. Two shapes are admitted - a savestate load and
    # a dofile of another allow-listed file - and anything else is refused rather
    # than run, so a launcher cannot smuggle arbitrary code past the allowlist.
    if ($PostCommand) {
        if ($PostCommand -match '^dofile\(\[\[(?<path>[^\]]+)\]\]\)$') {
            $extra = [System.IO.Path]::GetFullPath($Matches['path'])
            $extraCheckArgs = @(
                '-NoProfile', '-ExecutionPolicy', 'Bypass',
                '-File', (Join-Path $PSScriptRoot 'inject_mgba_lua.ps1'),
                '-TargetProcessId', $PID,
                '-LuaPath', $extra,
                '-CheckOnly'
            )
            & powershell @extraCheckArgs | Out-Null
            if ($LASTEXITCODE -ne 0) { throw 'PostCommand dofile target is not allowlisted' }
        } elseif ($PostCommand -notmatch '^emu:loadStateFile\(\[\[(?<state>[^\]]+)\]\]\)$') {
            throw ('PostCommand must be one of exactly two shapes: ' +
                   'dofile([[<allowlisted lua>]]) or emu:loadStateFile([[<path>]])')
        }
    }
    $bootstrapLines = @(
        ('rom011_marker_path = [[{0}]]' -f ($MarkerPath -replace '\\', '/')),
        ('dofile([[{0}]])' -f ([System.IO.Path]::GetFullPath($LuaPath) -replace '\\', '/'))
    )
    if ($PostCommand) { $bootstrapLines += $PostCommand }
    if ($StatePath) {
        # A failed load RETURNS false; it does not throw. `pcall` therefore only saw a throw, so the
        # old assert let an ordinary failure pass silently and the run continued with no state at
        # all. Both results are captured, the pair is recorded in the run directory, and a load that
        # is not true raises here, before the ready marker is written.
        $stateLuaPath = [System.IO.Path]::GetFullPath($StatePath) -replace '\\', '/'
        $stateLoadRecord = (Join-Path $RunDir 'state-load.txt') -replace '\\', '/'
        $bootstrapLines += @(
            ('local state_ok, state_err = emu.loadStateFile(emu, [[{0}]])' -f $stateLuaPath),
            ('local state_log = assert(io.open([[{0}]], [[w]]))' -f $stateLoadRecord),
            ('state_log:write([[ok ]], state_ok and [[true]] or [[false]], "\n", [[err ]], tostring(state_err), "\n", [[path ]], [[{0}]], "\n")' -f $stateLuaPath),
            'state_log:close()',
            'if not state_ok then error([[savestate load failed: ]] .. tostring(state_err), 0) end'
        )
    }
    $bootstrapLines += @(
        # Mark the moment the state is in memory, so an observer's silence can be attributed to the scene
        # rather than to a dead instrument. Guarded: observers without the hook are unaffected.
        'if dialogue_probe_note then dialogue_probe_note([[STATE loaded]]) end',
        ('local f = assert(io.open([[{0}]], [[w]]))' -f ($ReadyPath -replace '\\', '/')),
        'f:write([[ready]])',
        'f:close()'
    )
    $bootstrap = Join-Path $RunDir 'observer-boot.lua'
    Set-Content -LiteralPath $bootstrap -Value $bootstrapLines -Encoding ascii

    # Paths go in as ONE argument string. As separate array elements PowerShell
    # mangles the embedded quotes and mGBA then reports "Failed to open game file"
    # for a ROM that is perfectly readable.
    # The owner's dashboard sends key presses through a bridge that lives outside this repository and is
    # named only by an environment variable, so no machine path is tracked here. It runs as a second
    # --script. OWNER AUTHORISATION (2026-10-11): it is loaded on every run that can load it, and every
    # run RECORDS its absolute path and SHA-256 in the run directory, which is what makes the exception in
    # docs/skills/mgba-runtime.md section 6 reviewable. A build without --script skips it with a printed
    # note rather than refusing to launch, because the GDB launcher is pinned to such a build.
    # A variable set to "" does NOT survive to the child on Windows PowerShell 5.1 - it arrives as $null -
    # so "set but empty" cannot be the switch that disables the bridge. The switch is a real sentinel the
    # shell cannot drop: the literal value `none`, or LOG1_MGBA_NO_EXTRA_SCRIPT=1.
    $extraScript = $env:LOG1_MGBA_EXTRA_SCRIPT
    $extraScriptDisabled = ($env:LOG1_MGBA_NO_EXTRA_SCRIPT -eq '1') -or ($extraScript -ieq 'none')
    if ($extraScriptDisabled) {
        $extraScript = $null
    }
    elseif ($null -eq $extraScript) {
        # Already-running shells predate the user variable, so fall back to the registry.
        $extraScript = [Environment]::GetEnvironmentVariable('LOG1_MGBA_EXTRA_SCRIPT', 'User')
        if (-not $extraScript) { $extraScript = $null }
    }
    $extraScriptMissing = $false
    if ($extraScript -and -not (Test-Path -LiteralPath $extraScript)) {
        Write-Host "extra script SKIPPED: LOG1_MGBA_EXTRA_SCRIPT names a file that does not exist: $extraScript"
        $extraScriptNote = "LOG1_MGBA_EXTRA_SCRIPT names a file that does not exist: $extraScript"
        $extraScriptMissing = $true
        $extraScript = $null
    }
    $extraScriptSha = $null
    $extraScriptLoaded = $false
    if ($extraScriptDisabled) {
        $extraScriptNote = 'disabled by request: LOG1_MGBA_NO_EXTRA_SCRIPT=1 or the value none'
    }
    elseif (-not $extraScriptMissing) {
        # Only a genuinely unset variable says "not set": a set-but-missing path keeps its own note, which
        # the earlier version overwrote two lines later (the review's finding).
        $extraScriptNote = 'LOG1_MGBA_EXTRA_SCRIPT is not set for this run'
    }
    if ($extraScriptDisabled) {
        Write-Host "extra script SKIPPED: $extraScriptNote"
    }
    elseif ($extraScript) {
        $extraScriptPath = (Resolve-Path -LiteralPath $extraScript).Path
        $supportsScript = ((& $MGBPath --help 2>&1 | Out-String) -match '--script')
        if (-not $supportsScript) {
            $extraScriptNote = "this mGBA build has no --script flag ($mgbVersion), so the bridge was not loaded"
            Write-Host "extra script SKIPPED: $extraScriptNote"
        }
        else {
            $extraScriptSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $extraScriptPath).Hash
            $extraScriptLoaded = $true
            $extraScriptNote = 'loaded as a second --script; it presses only keys the dashboard holds'
            Write-Host "extra script: $extraScriptPath"
            Write-Host "  sha256    : $extraScriptSha"
        }
    }

    # Recorded in the run directory beside inputs.json, so a reviewer sees what was loaded even for the
    # launchers that write their own identity block and know nothing about this flag.
    $record = [ordered]@{
        path    = if ($extraScriptLoaded) { $extraScriptPath } else { $null }
        sha256  = $extraScriptSha
        loaded  = $extraScriptLoaded
        note    = $extraScriptNote
    }
    $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $RunDir 'extra-script.json') -Encoding utf8

    $options = @()
    if ($ArgumentList.Count -gt 0) { $options += $ArgumentList }
    $options += @('--script', $bootstrap)
    if ($extraScriptLoaded) { $options += @('--script', $extraScriptPath) }
    $argumentText = (($options | ForEach-Object { '"{0}"' -f $_ }) -join ' ') +
        (' "{0}"' -f $RomPath)

    $previousForeground = [IntPtr]::Zero
    if (Initialize-SessionWindow) {
        $previousForeground = [DbzSessionWindow]::GetForegroundWindow()
    }

    # An observer cannot hash a file, so the image's identity reaches the child in the
    # environment. It is the same digest the gate above has just proved the ROM against.
    $env:LOG1_MGBA_ROM_SHA256 = $expectedHash

    $process = Start-Process -FilePath $MGBPath -ArgumentList $argumentText -PassThru

    $deadline = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $deadline) {
        $process.Refresh()
        if ($process.HasExited) { throw 'mGBA exited before its window appeared' }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) { break }
        Start-Sleep -Milliseconds 100
    }
    if ('DbzSessionWindow' -as [type]) {
        # 4 = SW_SHOWNOACTIVATE: visible, not foreground.
        [void][DbzSessionWindow]::ShowWindow($process.MainWindowHandle, 4)
        if ($previousForeground -ne [IntPtr]::Zero) {
            [void](Set-SessionWindowFocus -Target $previousForeground)
        }
    }

    $readyDeadline = (Get-Date).AddSeconds($ReadyTimeoutSeconds)
    while ((Get-Date) -lt $readyDeadline) {
        if (Test-Path -LiteralPath $ReadyPath) { break }
        Start-Sleep -Milliseconds 100
    }
    if (-not (Test-Path -LiteralPath $ReadyPath)) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        # A state was asked for and the marker never appeared: the bootstrap recorded the load's own
        # result before it aborted, so the operator gets that reason instead of the generic timeout,
        # and the run directory keeps it beside the identity files.
        $stateLoadRecord = Join-Path $RunDir 'state-load.txt'
        if ($StatePath -and (Test-Path -LiteralPath $stateLoadRecord)) {
            $reason = (Get-Content -LiteralPath $stateLoadRecord -Raw).Trim()
            Set-Content -LiteralPath (Join-Path $RunDir 'state-load-failure.txt') -Value $reason -Encoding ascii
            throw "savestate load failed: $reason"
        }
        throw 'Lua script did not report ready'
    }
    return $process
}
