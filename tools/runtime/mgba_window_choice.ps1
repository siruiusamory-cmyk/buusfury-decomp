# The mGBA window choice, as a pure function of a candidate list.
#
# It is a separate file so a test can drive it without a GUI:
# tests/unit/test_mgba_capture.py feeds it synthetic candidate lists and checks
# both window shapes.
#
# A candidate is a window with:
#   ProcessId  the owning process
#   Parent     the parent window's handle, 0 when the window is a desktop child
#   Name       the window title
#   Element    the caller's own handle on the window, carried back unread
#
# A match needs the target process id AND a name pattern that the caller anchors,
# so a window is never selected by a loose title, and never by a title alone.
function Select-MgbaWindow {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]]$Candidates,
        [Parameter(Mandatory = $true)]
        [int]$TargetProcessId,
        [Parameter(Mandatory = $true)]
        [string]$NamePattern
    )
    $matched = @($Candidates | Where-Object {
        $_.ProcessId -eq $TargetProcessId -and $_.Name -match $NamePattern -and
            $_.Parent -eq 0
    })
    if ($matched.Count -gt 0) { return $matched[0] }
    return $null
}
