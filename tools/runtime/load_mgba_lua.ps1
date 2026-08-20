param(
    [Parameter(Mandatory = $true)]
    [string]$RomPath,
    [Parameter(Mandatory = $true)]
    [string]$LuaPath,
    [Parameter(Mandatory = $true)]
    [string]$ExpectedState,
    [string]$MgbaPath = 'C:\Program Files\mGBA\mGBA.exe'
)

$ErrorActionPreference = 'Stop'
$expectedHash = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
$workspaceRoot = [System.IO.Path]::GetFullPath('<checkout>')
$allowedRuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot 'build\rom006'))
$resolvedLuaPath = [System.IO.Path]::GetFullPath($LuaPath)
$resolvedExpectedState = [System.IO.Path]::GetFullPath($ExpectedState)
$allowedPairs = @{
    ([System.IO.Path]::GetFullPath((Join-Path $workspaceRoot 'tools\runtime\rom006_bootstrap.lua'))) =
        [System.IO.Path]::GetFullPath((Join-Path $allowedRuntimeRoot 'bootstrap.mss'))
    ([System.IO.Path]::GetFullPath((Join-Path $workspaceRoot 'tools\runtime\rom006_bootstrap_map4.lua'))) =
        [System.IO.Path]::GetFullPath((Join-Path $allowedRuntimeRoot 'bootstrap-map4.mss'))
}
if (-not $allowedPairs.ContainsKey($resolvedLuaPath)) {
    throw 'LuaPath is not a tracked ROM-006 bootstrap script'
}
if ($allowedPairs[$resolvedLuaPath] -ne $resolvedExpectedState) {
    throw 'ExpectedState does not match the selected ROM-006 bootstrap script'
}
if ((Split-Path -Parent $resolvedExpectedState) -ne $allowedRuntimeRoot) {
    throw 'ExpectedState must be directly beneath build\rom006'
}
$LuaPath = $resolvedLuaPath
$ExpectedState = $resolvedExpectedState

$rom = Get-Item -LiteralPath $RomPath
$beforeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $RomPath).Hash
$beforeMtime = $rom.LastWriteTimeUtc.Ticks
if ($rom.Length -ne 8388608 -or $beforeHash -ne $expectedHash) {
    throw 'Verified ROM identity mismatch before mGBA bootstrap'
}

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

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

$process = Start-Process -FilePath $MgbaPath -ArgumentList $arguments -PassThru
try {
    $desktop = [System.Windows.Automation.AutomationElement]::RootElement
    $processCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
        $process.Id
    )

    $mainWindow = $null
    for ($attempt = 0; $attempt -lt 100 -and -not $mainWindow; $attempt++) {
        Start-Sleep -Milliseconds 100
        if ($process.HasExited) {
            throw "mGBA exited before creating a window (exit code $($process.ExitCode))"
        }
        $mainWindow = $desktop.FindFirst(
            [System.Windows.Automation.TreeScope]::Children,
            $processCondition
        )
    }
    if (-not $mainWindow) { throw 'mGBA main window did not appear' }

    for ($attempt = 0; $attempt -lt 200; $attempt++) {
        $mainWindow = $desktop.FindFirst(
            [System.Windows.Automation.TreeScope]::Children,
            $processCondition
        )
        if ($mainWindow -and $mainWindow.Current.Name -match "Buu's Fury") { break }
        Start-Sleep -Milliseconds 100
    }
    if (-not $mainWindow -or $mainWindow.Current.Name -notmatch "Buu's Fury") {
        throw "mGBA did not report loaded ROM; window title: $($mainWindow.Current.Name)"
    }
    Start-Sleep -Milliseconds 500

    $tools = $mainWindow.FindFirst(
        [System.Windows.Automation.TreeScope]::Descendants,
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty,
            'Tools'
        ))
    )
    if (-not $tools) { throw 'Tools menu not found' }
    $tools.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand()

    $scriptMenu = $null
    $scriptCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Scripting...'
    )
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
        if (-not $edit.Current.IsReadOnly) {
            $prompt = $edit
            break
        }
    }
    if (-not $prompt) { throw 'Scripting prompt not found' }
    $command = 'dofile([[' + ($LuaPath -replace '\\', '/') + ']])'
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
