param(
    [switch]$SkipUpstreams,
    # The extras a contributor gets. The default is the set CI installs
    # (`-e ".[dev,workbench,research]"`, .gitlab-ci.yml), because the workbench
    # and research gates are gates a contributor is told to run and they skip
    # whole without PySide6 and capstone. `packaging` is left out: it adds
    # PyInstaller for cutting a release, which is an owner-run step.
    [string]$Extra = 'dev,workbench,research'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$VenvPath = Join-Path $ProjectRoot '.venv'
$VenvPython = Join-Path $VenvPath 'Scripts\python.exe'

$KnownExtras = @('dev', 'workbench', 'research', 'packaging')
$ExtraArguments = @()
foreach ($Name in $Extra.Split(',')) {
    $Trimmed = $Name.Trim()
    if (-not $Trimmed) { continue }
    if ($KnownExtras -notcontains $Trimmed) {
        throw "Unknown extra '${Trimmed}'; the project declares $($KnownExtras -join ', ')"
    }
    $ExtraArguments += @('--extra', $Trimmed)
}
if (-not $ExtraArguments) {
    throw 'At least one extra is required; setup installs no test tooling otherwise'
}

function Test-ProjectPython {
    if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        return $false
    }
    & $VenvPython -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'
    if ($LASTEXITCODE -ne 0) { return $false }
    & $VenvPython -m pip --version | Out-Null
    return $LASTEXITCODE -eq 0
}

function Normalize-GitUrl([string]$Url) {
    $Normalized = $Url.Trim().TrimEnd('/').ToLowerInvariant()
    if ($Normalized.EndsWith('.git')) {
        $Normalized = $Normalized.Substring(0, $Normalized.Length - 4)
    }
    return $Normalized
}

$Uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $Uv) {
    throw 'uv is required for the locked Phase 0 setup'
}

$env:UV_CACHE_DIR = Join-Path $ProjectRoot 'build\uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $ProjectRoot 'build\python'
$PythonSelector = $VenvPython
if (-not (Test-ProjectPython)) {
    & $Uv.Source python install 3.12
    if ($LASTEXITCODE -ne 0) { throw 'uv could not install Python 3.12' }
    $PythonSelector = '3.12'
}
& $Uv.Source sync --locked @ExtraArguments --project $ProjectRoot --python $PythonSelector
if ($LASTEXITCODE -ne 0) { throw 'Locked project synchronization failed' }
if (-not (Test-ProjectPython)) { throw 'Synchronized .venv is invalid' }

if (-not $SkipUpstreams) {
    $LockPath = Join-Path $ProjectRoot 'upstreams.lock'
    $Lock = Get-Content -Raw -LiteralPath $LockPath | ConvertFrom-Json
    foreach ($Repository in $Lock.repositories) {
        $Destination = Join-Path $ProjectRoot $Repository.path
        if (-not (Test-Path -LiteralPath (Join-Path $Destination '.git'))) {
            git clone $Repository.url $Destination
            if ($LASTEXITCODE -ne 0) { throw "Clone failed: $($Repository.name)" }
        }
        $Origin = (git -C $Destination remote get-url origin).Trim()
        if ($LASTEXITCODE -ne 0) { throw "Origin read failed: $($Repository.name)" }
        if ((Normalize-GitUrl $Origin) -ne (Normalize-GitUrl $Repository.url)) {
            throw "Upstream origin mismatch: $($Repository.name)"
        }
        $Dirty = git -C $Destination status --porcelain
        if ($Dirty) {
            throw "Upstream clone has local changes; refusing checkout: $Destination"
        }
        git -C $Destination fetch --tags origin
        if ($LASTEXITCODE -ne 0) { throw "Fetch failed: $($Repository.name)" }
        git -C $Destination checkout --detach $Repository.commit
        if ($LASTEXITCODE -ne 0) { throw "Checkout failed: $($Repository.name)" }
        $Actual = (git -C $Destination rev-parse HEAD).Trim()
        if ($Actual -ne $Repository.commit) {
            throw "Pinned commit verification failed: $($Repository.name)"
        }
        git -C $Destination submodule update --init --recursive
        if ($LASTEXITCODE -ne 0) { throw "Submodule update failed: $($Repository.name)" }
    }
}

Write-Host "Phase 0 environment ready: $VenvPython"
