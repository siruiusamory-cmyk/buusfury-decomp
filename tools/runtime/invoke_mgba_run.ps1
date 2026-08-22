param(
    [Parameter(Mandatory = $true)]
    [int]$TargetProcessId
)

$ErrorActionPreference = 'Stop'
$target = Get-Process -Id $TargetProcessId -ErrorAction Stop
if ($target.ProcessName -ne 'mGBA') {
    throw 'TargetProcessId is not the mGBA Qt frontend'
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
if (-not $scripting) { throw 'Scripting window did not appear' }

$run = $scripting.FindFirst(
    [System.Windows.Automation.TreeScope]::Descendants,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        'Run'
    ))
)
if (-not $run) { throw 'Run button not found' }
$run.GetCurrentPattern(
    [System.Windows.Automation.InvokePattern]::Pattern
).Invoke()
