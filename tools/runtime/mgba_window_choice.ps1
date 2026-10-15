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
# so a window is never selected by a loose title, and never by a title alone. A
# desktop child wins; a nested match is the second choice, because a host process
# that adopts the emulator with SetParent + WS_CHILD (the LOG1 Workbench does
# this) leaves the emulator window parented inside the host and invisible to a
# top-level scan. UIA enumerates in pre-order, so the first nested match is the
# outermost one.
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
        $_.ProcessId -eq $TargetProcessId -and $_.Name -match $NamePattern
    })
    $topLevel = @($matched | Where-Object { $_.Parent -eq 0 })
    if ($topLevel.Count -gt 0) { return $topLevel[0] }
    if ($matched.Count -gt 0) { return $matched[0] }
    return $null
}
