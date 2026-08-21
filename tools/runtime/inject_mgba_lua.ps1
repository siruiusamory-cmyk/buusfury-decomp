param(
    [Parameter(Mandatory = $true)]
    [int]$TargetProcessId,
    [Parameter(Mandatory = $true)]
    [string]$LuaPath,
    [string]$ReadyPath
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

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$processCondition = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
    $TargetProcessId
)
$mainWindow = $null
for ($attempt = 0; $attempt -lt 200 -and -not $mainWindow; $attempt++) {
    Start-Sleep -Milliseconds 100
    $mainWindow = $desktop.FindFirst(
        [System.Windows.Automation.TreeScope]::Children,
        $processCondition
    )
}
if (-not $mainWindow) { throw 'mGBA window did not appear' }

for ($attempt = 0; $attempt -lt 200; $attempt++) {
    if ($mainWindow.Current.Name -match "Buu's Fury") { break }
    Start-Sleep -Milliseconds 100
}
if ($mainWindow.Current.Name -notmatch "Buu's Fury") {
    throw 'mGBA did not report the loaded Buu''s Fury ROM'
}

$tools = $mainWindow.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Tools'
    ))
)
if (-not $tools) { throw 'Tools menu not found' }
$tools.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand()

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
$scriptMenu.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()

$scriptingCondition = New-Object System.Windows.Automation.AndCondition(
    $processCondition,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Scripting'
    ))
)
$scripting = $null
for ($attempt = 0; $attempt -lt 50 -and -not $scripting; $attempt++) {
    Start-Sleep -Milliseconds 100
    $scripting = $desktop.FindFirst(
        [System.Windows.Automation.TreeScope]::Children,
        $scriptingCondition
    )
}
if (-not $scripting) { throw 'Scripting window did not appear' }

$edits = $scripting.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    ))
)
$prompt = $null
foreach ($edit in $edits) {
    if (-not $edit.Current.IsReadOnly) { $prompt = $edit; break }
}
if (-not $prompt) { throw 'Scripting prompt not found' }
$command = 'dofile([[' + ($resolvedLua -replace '\\', '/') + ']])'
if ($resolvedReady) {
    $luaReady = $resolvedReady -replace '\\', '/'
    $command += '; local f=assert(io.open([[' + $luaReady + ']], [[w]])); ' +
        'f:write([[ready]]); f:close()'
}
$prompt.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($command)

$run = $scripting.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Run'
    ))
)
if (-not $run) { throw 'Run button not found' }
$run.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()

if ($resolvedReady) {
    $readyConfirmed = $false
    for ($attempt = 0; $attempt -lt 100 -and -not $readyConfirmed; $attempt++) {
        if ((Test-Path -LiteralPath $resolvedReady) -and
            [System.IO.File]::ReadAllText($resolvedReady) -eq 'ready') {
            $readyConfirmed = $true
            break
        }
        Start-Sleep -Milliseconds 100
    }
    if (-not $readyConfirmed) {
        throw 'Lua script did not report ready'
    }
}
