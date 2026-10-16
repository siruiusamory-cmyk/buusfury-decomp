# The arm steps of tools/runtime/inject_mgba_lua.ps1 that a human can disturb, as
# pure functions of the caller's own UI Automation access (ExpandCollapse, Value and
# Invoke patterns only), so a test drives them without a GUI and no focus is needed.
# An operator click closes the Tools popup, so every attempt re-expands it: a plain
# re-search of a popup that is already gone cannot differ (P-370).

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
