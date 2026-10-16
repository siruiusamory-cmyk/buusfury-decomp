# The two arm steps of tools/runtime/inject_mgba_lua.ps1 that a human can disturb,
# as pure functions of the caller's own UI Automation access.
#
# They are a separate file so a test can drive the shipped decisions with fakes:
# tests/unit/test_probe_inject_arm.py passes scriptblocks that stand in for the
# Tools menu and the Scripting prompt, so the retry and the read-back are
# exercised as written and never as a copy.
#
# Neither function drives UI itself. The caller passes the pattern calls in, and
# those calls are ExpandCollapsePattern, ValuePattern and InvokePattern only, so
# the flow never needs focus and no key, foreground or input synthesis is made
# here or permitted to be added.
#
# P-370: an operator click closes the Tools popup mid-search, so the item search
# is retried with the popup re-opened on every attempt. A plain re-search of a
# popup that is already gone cannot differ; the re-expand is what changes state.

function Invoke-MgbaMenuWithRetry {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$ReExpand,
        [Parameter(Mandatory = $true)][scriptblock]$FindItem,
        [int]$MinAttempts = 5,
        [int]$MaxAttempts = 10,
        [scriptblock]$Pause = { Start-Sleep -Milliseconds 100 }
    )
    if ($MinAttempts -lt 5) {
        throw "MinAttempts must be at least 5, got $MinAttempts"
    }
    if ($MaxAttempts -gt 10) {
        throw "MaxAttempts must be at most 10, got $MaxAttempts"
    }
    if ($MaxAttempts -lt $MinAttempts) {
        throw "MaxAttempts $MaxAttempts is below MinAttempts $MinAttempts"
    }
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        & $ReExpand
        $item = & $FindItem
        if ($item) {
            Write-Host "Scripting menu item found on attempt $attempt of $MaxAttempts"
            return $item
        }
        if ($attempt -lt $MaxAttempts) { & $Pause }
    }
    throw "Scripting menu item not found after $MaxAttempts attempts"
}

function Set-MgbaPromptCommand {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$ReadValue,
        [Parameter(Mandatory = $true)][scriptblock]$SetValue,
        [Parameter(Mandatory = $true)][string]$Command,
        [int]$MaxAttempts = 5,
        [scriptblock]$Pause = { Start-Sleep -Milliseconds 100 }
    )
    $sets = 0
    while ($true) {
        if ((& $ReadValue) -eq $Command) {
            Write-Host "Scripting prompt held the command ($sets re-set(s) of $MaxAttempts)"
            return $true
        }
        if ($sets -ge $MaxAttempts) {
            throw "Scripting prompt did not hold the command after $MaxAttempts attempts"
        }
        $sets++
        & $SetValue $Command
        & $Pause
    }
}
