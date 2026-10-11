$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'Missing .venv. Run scripts\setup.ps1 first.'
}

& $Python -m pytest -m fast @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Python -m tools.webfoot --help | Out-Null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
