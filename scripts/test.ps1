$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'Missing .venv. Run scripts\setup.ps1 first.'
}

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
if ($serial) {
    & $Python -m pytest -m fast @args
} else {
    & $Python -m pytest -m fast -n 4 --dist loadfile @args
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m tools.webfoot --help | Out-Null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
