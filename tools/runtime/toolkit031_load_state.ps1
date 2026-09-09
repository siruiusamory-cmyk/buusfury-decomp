<#
.SYNOPSIS
Load one savestate into an already-running, already-instrumented mGBA PID.

.DESCRIPTION
The TOOLKIT-031 observer must be attached BEFORE the map's entities are
constructed, because its evidence is a breakpoint at the script trampoline and
construction is one of the trigger classes under test. So the ordering is
inject-then-load, and this script performs the load through the same Scripting
prompt the injector uses.

It sends exactly one `emu:loadStateFile(...)` call and nothing else. It writes
no emulated memory and presses no keys.

Two details are load-bearing and were measured rather than assumed:

  * The prompt is identified by AutomationId ending '.prompt'. Qt reports an
    EMPTY IsReadOnly for every Edit in the Scripting window, so selecting the
    first "not read-only" element picks the log pane instead and SetValue then
    fails with "Value is read-only."
  * The Lua is written with long-bracket strings [[...]]. Quote characters do
    not survive the PowerShell -> UI Automation SetValue path.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [int]$TargetProcessId,
    [Parameter(Mandatory = $true)]
    [string]$StatePath
)

$ErrorActionPreference = 'Stop'
$target = Get-Process -Id $TargetProcessId -ErrorAction Stop
if ($target.ProcessName -ne 'mGBA') {
    throw 'TargetProcessId is not the mGBA Qt frontend'
}
if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
    throw "Savestate is missing: $StatePath"
}
$resolvedState = (Resolve-Path -LiteralPath $StatePath).Path
if ($resolvedState -match '\]\]') {
    throw 'StatePath contains unsupported Lua long-string terminator'
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
$scripting = $null
for ($attempt = 0; $attempt -lt 50 -and -not $scripting; $attempt++) {
    Start-Sleep -Milliseconds 100
    $scripting = $desktop.FindFirst(
        [System.Windows.Automation.TreeScope]::Children,
        $scriptingCondition
    )
}
if (-not $scripting) { throw 'Scripting window not found' }

$edits = $scripting.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    ))
)
$prompt = $null
foreach ($edit in $edits) {
    $automationId = $edit.Current.AutomationId
    if ($automationId -and $automationId.EndsWith('.prompt')) { $prompt = $edit; break }
}
if (-not $prompt) {
    foreach ($edit in $edits) {
        if ($edit.Current.ClassName -eq 'QGBA::HistoryLineEdit') { $prompt = $edit; break }
    }
}
if (-not $prompt) { throw 'Scripting prompt not found' }

$luaState = $resolvedState -replace '\\', '/'
$command = 'print([[toolkit031-load=]]..tostring(emu:loadStateFile([[' + $luaState + ']])))'
$prompt.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($command)

# The Run button click is performed in a bounded helper process: mGBA connects
# it to a synchronous handler, so Invoke can fail to return even though the
# command ran.
$invokeScript = Join-Path $PSScriptRoot 'invoke_mgba_run.ps1'
$invoke = Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -PassThru -ArgumentList @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $invokeScript,
    '-TargetProcessId', [string]$TargetProcessId
)
$null = $invoke.WaitForExit(15000)
if (-not $invoke.HasExited) { Stop-Process -Id $invoke.Id -Force -ErrorAction SilentlyContinue }

# Confirm from the log pane that the load actually reported true, rather than
# assuming the click worked.
$log = $scripting.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::AutomationIdProperty,
        'QGBA__ScriptingView.centralwidget.splitter.verticalLayoutWidget.splitter_1.log'
    ))
)
$confirmed = $false
for ($attempt = 0; $attempt -lt 40 -and -not $confirmed; $attempt++) {
    Start-Sleep -Milliseconds 250
    if ($log) {
        $text = $log.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Current.Value
        if ($text -match 'toolkit031-load=true') { $confirmed = $true }
        elseif ($text -match 'toolkit031-load=false') { throw 'Savestate load reported false' }
    }
}
if (-not $confirmed) { throw 'Savestate load was not confirmed' }
Write-Output 'savestate loaded'
