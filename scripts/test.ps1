param(
    # Resolve and print the interpreter, then stop before running any gate.
    [switch]$ResolveOnly
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path

# Interpreter resolution. A worktree's own `.venv` wins; a lane that cut a
# worktree without one gets the shared test venv instead of a hand setup. The
# choice is printed because the two environments do not skip the same tests. The
# primary checkout's venv is deliberately not a candidate: it is read-only and
# has no pytest-xdist, so no lane may run it by accident. `-ResolveOnly` stops
# after this block, which is how the fallback is measured without paying for a
# gate run.
#
# The shared venv is the sibling worktree named below, so it is searched for
# upward from this checkout rather than written as one machine's path: worktrees
# cut straight under the checkout parent, one level deeper under a ticket
# directory, and nested under `build\worktrees` all find it. When the search
# finds nothing the loop below fails, and the message names the sibling to
# junction instead.
$SharedSibling = 'log1-remake-test-speed-003\build\test-speed-003\venv'
$SharedVenv = $null
$search = $ProjectRoot
while ($search) {
    $probe = Join-Path $search $SharedSibling
    if (Test-Path -LiteralPath (Join-Path $probe 'Scripts\python.exe') -PathType Leaf) { $SharedVenv = $probe; break }
    $up = Split-Path $search -Parent
    if (-not $up -or $up -eq $search) { break }
    $search = $up
}
if (-not $SharedVenv) { $SharedVenv = Join-Path (Split-Path $ProjectRoot -Parent) $SharedSibling }

$candidates = @(
    @{ Python = (Join-Path $ProjectRoot '.venv\Scripts\python.exe'); Why = 'the worktree .venv' }
    @{ Python = (Join-Path $SharedVenv 'Scripts\python.exe'); Why = 'the shared test venv' }
)
$Python = $null
foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate.Python -PathType Leaf) {
        $Python = $candidate.Python
        Write-Host "test.ps1: interpreter $Python ($($candidate.Why))"
        break
    }
}
if (-not $Python) {
    throw "No test interpreter. Tried: $(($candidates | ForEach-Object { $_.Python }) -join '; '). Run scripts\setup.ps1, or junction .venv to $SharedSibling."
}
if ($ResolveOnly) { exit 0 }

# Parallel by default: worker processes at module granularity, because the
# suite's slowest modules are dominated by per-module decode setup. `-n 0` is
# the explicit serial opt-out, spelled as two arguments because Windows
# PowerShell 5.1 splits the pair before it reaches the child, so it is detected
# as the pair rather than as one string. The default flags go FIRST and the
# caller's arguments AFTER, so a caller that passes its own `-n` or `--dist`
# overrides the default instead of colliding with it.
#
# `--%` exists from PowerShell 3 and is NOT used here, for a measured reason: in
# 5.1 it stops parsing where it appears, so a caller must put it before every
# argument, and even then the shell passes its own redirection tokens through as
# literal arguments. The pair detection below needs neither of those surprises.
$serial = $false
for ($i = 0; $i -lt $args.Count - 1; $i++) {
    if ($args[$i] -eq '-n' -and $args[$i + 1] -eq '0') { $serial = $true }
}
$step = [System.Diagnostics.Stopwatch]::StartNew()
if ($serial) {
    & $Python -m pytest -m fast @args
} else {
    & $Python -m pytest -m fast -n 4 --dist loadfile @args
}
Write-Host ("test.ps1: pytest took {0:N1}s" -f $step.Elapsed.TotalSeconds)
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$step.Restart()
& $Python -m tools.webfoot --help | Out-Null
Write-Host ("test.ps1: tools.webfoot --help took {0:N1}s" -f $step.Elapsed.TotalSeconds)
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
