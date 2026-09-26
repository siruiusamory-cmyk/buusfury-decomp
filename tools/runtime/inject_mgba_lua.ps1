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
    # Added by MAP-WARP-RUNTIME-EDIT-001: the read-only transition observer. It
    # reads the live map identity each frame plus the target record's destination
    # key through the engine's own MapEntry+0x2C -> root+0x44 route, and writes
    # only host files inside the run directory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\warpedit001_transition_watch.lua')
    )
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
        (Join-Path $workspaceRoot 'tools\runtime\p008_clip_sequence.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p008_mash_driver.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p008_contact_trace.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p010_death_timeline.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p011_wolf_speed_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p012_rng_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p013_knockback_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p015_bodyrect_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p016_anchor_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_ewram_hp_scan.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\p006_hit_bracket_scan.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit029_placement_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit030_behavior_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit031_api_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit031_execution_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit034_dispatch_caller_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit032_authored_script_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit033_gameplay_effect_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit036_text_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit037_dialogue_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom_expand_001_dialogue_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom_expand_001_dialogue_driver.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\rom_expand_001_snapshot.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\capacity001_expanded_dialogue_probe.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\toolkit038_scenario_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\text_handle_001_producer_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\text_handle_002_handler_watch.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapvis001_vram_dump.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapvis001_vram_dump_any.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapvis002_bg_provenance.lua')
    )
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\placementpos001_construct_watch.lua')
    )
    # Added by ASSET-EXPORT-MAP19-001: read-only BG/VRAM placement observer
    # for the terrain-field layer. It reads registers and VRAM and writes
    # only host text.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\map19_bg_placement.lua')
    )
    # Added by DIALOGUE-VARIABLE-LENGTH-001: the same read-only consumer
    # observation and screenshot schedule as the Checkpoint D probe, retargeted
    # at a RE-AUTHORED handle and widened decoded length. It writes input only in
    # its `scripted` mode, which the tracked runner does not select, and never
    # writes emulated memory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\varlen001_dialogue_variable_length_probe.lua')
    )
    # Added by MAP-TILE-PAINT-001: the read-only live-screenblock observer. It
    # reads emulated memory and its own latched registers and writes host files
    # under the run directory; it contains none of the input- or memory-writing
    # API names the read-only guard in tests/unit/test_mgba_capture.py greps for,
    # so the observer guarantee holds, and that test names this file explicitly.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\tilepaint001_live_screenblock.lua')
    )
    # The leave-and-re-enter watcher: same read-only guarantees, but it latches a
    # numbered snapshot whenever the engine's screenblock content changes, which
    # is how an area rebuild is captured without timing a keypress.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\tilepaint001_watch_rebuild.lua')
    )
    # The same watcher for MAP-CHUNK-AUTHORING-001. It additionally accepts the
    # profile's generated 16 MiB image size - the authored chunk body lives above
    # the canonical EOF, so the parent observer's 8 MiB assert refuses the image
    # under test - records the observed ROM size on every row, and records the
    # address the engine's own loaded layer record holds for the watched chunk
    # cell. Read-only in exactly the same sense.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\chunkauth001_watch_rebuild.lua')
    )
    # Added by MAP-GFX-DIAG-001: the read-only assembled-background observer. It
    # dumps the engine's own VRAM, palette and IO once a target map has been
    # departed and re-entered, and records the root, layer records and extent the
    # LIVE image holds. Read-only in exactly the same sense as the observers
    # above; tests/unit/test_mgba_capture.py names this file explicitly.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\mapgfxdiag001_map_layer_dump.lua')
    )
    # Added by ROMHACK-WARP-RANDOMIZER-001: the read-only map-arrival observer for
    # the human-operated randomized playthrough. It latches the live map identity
    # on every map change, and the identity it came from, so each naturally
    # encountered warp has a source and a destination that came out of the
    # running engine rather than a map-name guess. It reads emulated memory and
    # writes only host files inside the run directory.
    [System.IO.Path]::GetFullPath(
        (Join-Path $workspaceRoot 'tools\runtime\warprand001_map_watch.lua')
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
