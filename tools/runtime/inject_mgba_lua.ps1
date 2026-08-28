param(
    [Parameter(Mandatory = $true)]
    [int]$TargetProcessId,
    [Parameter(Mandatory = $true)]
    [string]$LuaPath,
    [string]$ReadyPath,
    [string]$MarkerPath
)

$ErrorActionPreference = 'Stop'
$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$allowedLua = @(
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom007_move_south.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom009_clean_route.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom009_post_transition_route.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom011_human_ready.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom011_stop_setup.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom011_idle_benchmark.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p002_walk_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_attack_scout.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_move_attack.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_punch_timing.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_hit_dump.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_hit_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_wander.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_kihit.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_watcher.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_mash.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_armed_punch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_armed_mash.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_armed_one.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_human_play.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p003_zdump.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_human_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_punch_label.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_full_label.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_fine.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_actor_focus.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_aggro.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p004_actor_enum.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_reaction_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_anchor_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_dev_breakpoint_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_ctrl_stack.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_scan_timing_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_ctrl_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_pool_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006c_punch_field_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p007_wolf_ai_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_ewram_hp_scan.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_hit_bracket_scan.lua')
    )
)
$resolvedLua = [System.IO.Path]::GetFullPath($LuaPath)
if ($resolvedLua -notin $allowedLua) {
    throw 'LuaPath is not an allowlisted tracked movement script'
}
$resolvedReady = $null
if ($ReadyPath) {
    $resolvedReady = [System.IO.Path]::GetFullPath($ReadyPath)
    $allowedReadyRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'build')
    ).TrimEnd('\') + '\'
    if (-not $resolvedReady.StartsWith(
        $allowedReadyRoot,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'ReadyPath must remain beneath ignored build directory'
    }
    if ($resolvedReady.Contains(']]')) {
        throw 'ReadyPath contains unsupported Lua long-string terminator'
    }
    if (Test-Path -LiteralPath $resolvedReady) {
        throw 'ReadyPath already exists'
    }
}
$resolvedMarker = $null
if ($MarkerPath) {
    $resolvedMarker = [System.IO.Path]::GetFullPath($MarkerPath)
    $allowedMarkerRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'build')
    ).TrimEnd('\') + '\'
    if (-not $resolvedMarker.StartsWith(
        $allowedMarkerRoot,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'MarkerPath must remain beneath ignored build directory'
    }
    if ($resolvedMarker.Contains(']]')) {
        throw 'MarkerPath contains unsupported Lua long-string terminator'
    }
    if (Test-Path -LiteralPath $resolvedMarker) {
        throw 'MarkerPath already exists'
    }
}

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$processCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $TargetProcessId
)
$scriptingCondition = New-Object System.Windows.Automation.AndCondition(
    $processCondition,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Scripting'
    ))
)
$scripting = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    $scriptingCondition
)

$mainWindow = $null
for ($attempt = 0; $attempt -lt 200 -and -not $mainWindow; $attempt++) {
    Start-Sleep -Milliseconds 100
    $windows = $desktop.FindAll(
        [System.Windows.Automation.TreeScope]::Children,
        $processCondition
    )
    foreach ($window in $windows) {
        if ($window.Current.Name -match "Buu's Fury|DBZBUUSFURY") {
            $mainWindow = $window
            break
        }
    }
}
if (-not $mainWindow) {
    throw 'mGBA did not report the loaded Buu''s Fury ROM title'
}

if (-not $scripting) {
    $tools = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty,
            'Tools'
        ))
    )
    if (-not $tools) {
        $allNames = @()
        foreach ($el in $mainWindow.FindAll(
                [System.Windows.Automation.TreeScope]::Descendants,
                [System.Windows.Automation.Condition]::TrueCondition)) {
            $allNames += $el.Current.Name
        }
        Write-Output ("UIA tree: " + ($allNames -join ' | '))
        throw 'Tools menu not found'
    }
    $tools.GetCurrentPattern(
        [System.Windows.Automation.ExpandCollapsePattern]::Pattern
    ).Expand()

    $scriptCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Scripting...'
    )
    $scriptMenu = $null
    for ($attempt = 0; $attempt -lt 50 -and -not $scriptMenu; $attempt++) {
        Start-Sleep -Milliseconds 100
        $scriptMenu = $desktop.FindFirst(
            [System.Windows.Automation.TreeScope]::Descendants,
            $scriptCondition
        )
    }
    if (-not $scriptMenu) { throw 'Scripting menu item not found' }
    $scriptMenu.GetCurrentPattern(
        [System.Windows.Automation.InvokePattern]::Pattern
    ).Invoke()

    for ($attempt = 0; $attempt -lt 50 -and -not $scripting; $attempt++) {
        Start-Sleep -Milliseconds 100
        $scripting = $desktop.FindFirst(
            [System.Windows.Automation.TreeScope]::Children,
            $scriptingCondition
        )
    }
    if (-not $scripting) { throw 'Scripting window did not appear' }
}

$edits = $scripting.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    ))
)
# Identify the prompt by control identity, not by IsReadOnly. The Scripting
# window exposes three Edit elements - the log pane, the script buffer, and the
# prompt - and Qt does not always report IsReadOnly for them. When that property
# comes back empty, "-not IsReadOnly" is true for the log pane, which is the
# first descendant, so SetValue then fails with "Value is read-only."
$prompt = $null
foreach ($edit in $edits) {
    $automationId = $edit.Current.AutomationId
    if ($automationId -and $automationId.EndsWith('.prompt')) {
        $prompt = $edit
        break
    }
}
if (-not $prompt) {
    foreach ($edit in $edits) {
        if ($edit.Current.ClassName -eq 'QGBA::HistoryLineEdit') {
            $prompt = $edit
            break
        }
    }
}
if (-not $prompt) {
    foreach ($edit in $edits) {
        if ($edit.Current.IsReadOnly -eq $false) { $prompt = $edit; break }
    }
}
if (-not $prompt) { throw 'Scripting prompt not found' }
$command = ''
if ($resolvedMarker) {
    $luaMarker = $resolvedMarker -replace '\\', '/'
    $command = 'rom011_marker_path = [[' + $luaMarker + ']]; '
}
$command += 'dofile([[' + ($resolvedLua -replace '\\', '/') + ']])'
if ($resolvedReady) {
    $luaReady = $resolvedReady -replace '\\', '/'
    $command += '; local f=assert(io.open([[' + $luaReady + ']], [[w]])); ' +
        'f:write([[ready]]); f:close()'
}
$prompt.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($command)

$invokeScript = Join-Path $PSScriptRoot 'invoke_mgba_run.ps1'
$invokeArguments = @(
    '-NoProfile',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $invokeScript,
    '-TargetProcessId',
    [string]$TargetProcessId
)
$invokeProcess = $null
try {
    $invokeProcess = Start-Process `
        -FilePath 'powershell.exe' `
        -ArgumentList $invokeArguments `
        -WindowStyle Hidden `
        -PassThru
    if ($resolvedReady) {
        $readyConfirmed = $false
        for ($attempt = 0; $attempt -lt 100 -and -not $readyConfirmed; $attempt++) {
            if ((Test-Path -LiteralPath $resolvedReady) -and
                [System.IO.File]::ReadAllText($resolvedReady) -eq 'ready') {
                $readyConfirmed = $true
                break
            }
            $invokeProcess.Refresh()
            if ($invokeProcess.HasExited -and $invokeProcess.ExitCode -ne 0) {
                throw 'Asynchronous Run invocation failed'
            }
            Start-Sleep -Milliseconds 100
        }
        if (-not $readyConfirmed) {
            throw 'Lua script did not report ready'
        }
    } else {
        if (-not $invokeProcess.WaitForExit(10000)) {
            throw 'Asynchronous Run invocation did not complete'
        }
        if ($invokeProcess.ExitCode -ne 0) {
            throw 'Asynchronous Run invocation failed'
        }
    }
} finally {
    if ($invokeProcess) {
        $invokeProcess.Refresh()
        if (-not $invokeProcess.HasExited) {
            Stop-Process -Id $invokeProcess.Id -Force -ErrorAction SilentlyContinue
            $invokeProcess.WaitForExit(5000) | Out-Null
        }
    }
}
