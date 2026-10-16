# Shared plumbing for the self-hosted Windows CI runner.
#
# The job bodies live in `ci\*.ps1` rather than in `.gitlab-ci.yml` so that the
# same script a job runs can be run by hand for a measurement. This file is
# dot-sourced by each of them and defines no job of its own. It is Windows
# PowerShell 5.1: no `??`, no ternary, no `-Parallel`.

$ErrorActionPreference = 'Stop'

#: A job-level `variables:` entry in `.gitlab-ci.yml` does NOT override a project
#: CI variable: project scope wins
#: (https://docs.gitlab.com/ci/variables/#cicd-variable-precedence). The
#: credential must therefore be removed from THIS process's environment, and
#: every routed entry point dot-sources this file before it runs anything, so
#: the scrub lands before the first pip, npm or python child is created.
$env:CLOUDFLARE_API_TOKEN = ''

#: Resolved once, at dot-source time, from this file's own location: a function's
#: `$PSScriptRoot` is not a reliable way to ask. Every job script sets its
#: location to this, because the editable install and pytest both need the
#: repository root.
$CiProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path

#: The interpreter the job venvs are built from. This machine's `python` is
#: 3.12.10, the version the Linux job's `python:3.12-slim` image carried.
function Get-CiPython {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "ci: no 'python' on PATH for this runner; the job venvs are built from it"
    }
    return $command.Source
}

#: Where one job's venv lives. Outside every repository by construction: the
#: runner's own build directory when GitLab supplies one, a user-local directory
#: otherwise, so a hand run and a CI run do not share a venv.
function Get-CiVenvDirectory {
    param([Parameter(Mandatory)][string]$Name)
    $base = if ($env:CI_BUILDS_DIR) {
        Join-Path $env:CI_BUILDS_DIR 'log1-ci'
    } else {
        Join-Path $env:LOCALAPPDATA 'log1-ci'
    }
    return (Join-Path $base "venv-$Name")
}

#: A directory removal that tolerates a transient Windows handle. Three attempts,
#: because the measured failure is a file another process still holds open.
function Remove-CiVenvDirectory {
    param([Parameter(Mandatory)][string]$Path)
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            return
        } catch {
            if ($attempt -eq 3) { throw }
            Start-Sleep -Seconds 2
        }
    }
}

#: Build this job's venv FRESH, then install the project into it.
#:
#: Fresh every run, and not `--system-site-packages`: the job is a gate on the
#: project's own declared environment, and a venv that inherits the machine's
#: 162 site-packages would let a test that imports an undeclared package pass
#: here and fail for a user. Reusing a previous run's venv has the same hole from
#: the other side - pip reconciles versions but never removes a package the
#: project stopped declaring. Measured cost of the fresh install on this machine,
#: warm pip cache: 23.7 s to create the venv plus 123.5 s to install
#: `.[dev,workbench,research]`, 696 MB.
function New-CiVenv {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Extras
    )
    $venv = Get-CiVenvDirectory -Name $Name
    if (Test-Path -LiteralPath $venv) {
        try {
            Remove-CiVenvDirectory -Path $venv
        } catch {
            # Measured on master: a later job's cleanup can hit a handle a previous
            # run still holds (Remove-Item refused on capstone.dll under
            # venv-test-sdk), and failing the job there blocks the whole pipeline
            # before a single test runs. A fresh path costs one 700 MB install and
            # keeps the job independent of the previous run's handles; the
            # lingering directory is removed by a later fresh run.
            $venv = "$venv-$PID"
            Write-Host "ci: $Name venv is locked; building a fresh one at $venv"
        }
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $venv) | Out-Null
    Write-Host "ci: building $venv"
    # `| Out-Host` rather than a bare call: a function returns everything it
    # writes to the output stream, and pip's lines would be prepended to the
    # interpreter path this function hands back.
    & (Get-CiPython) -m venv $venv 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "ci: venv creation failed at $venv" }
    $python = Join-Path $venv 'Scripts\python.exe'
    & $python -m pip install --quiet --disable-pip-version-check --upgrade pip 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "ci: pip upgrade failed in $venv" }
    & $python -m pip install --quiet --disable-pip-version-check -e $Extras 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "ci: install of $Extras failed in $venv" }
    return $python
}

#: The venv a sibling job already built. `adjacency` carries `needs: ["test-sdk"]`
#: and runs the same shipping surface, so it runs in that job's environment
#: rather than paying a second 700 MB install for the same extras.
#:
#: THIS IS CORRECT ONLY WHILE ONE RUNNER TAKES THIS PROJECT'S JOBS ONE AT A TIME
#: AND BOTH JOBS LAND ON IT (`concurrent = 1`). `needs` orders jobs; it does not
#: pin them to a runner or to a build directory. A second runner with this tag,
#: or a build directory that moves between the two jobs, fails the consumer here
#: with the message below rather than testing the wrong environment. Building a
#: second venv in `adjacency` would remove the constraint for about 124 s and
#: 700 MB per pipeline; that trade is recorded in `.gitlab-ci.yml`.
function Use-CiVenv {
    param([Parameter(Mandatory)][string]$Name)
    $venv = Get-CiVenvDirectory -Name $Name
    $python = Join-Path $venv 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        # `New-CiVenv` moves to a fresh path when the venv it was handed is locked.
        # Resolve that path rather than failing the consumer on the original name.
        $fallback = Get-ChildItem -LiteralPath (Split-Path -Parent $venv) -Directory -Filter "$(Split-Path -Leaf $venv)-*" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($fallback) {
            $venv = $fallback.FullName
            $python = Join-Path $venv 'Scripts\python.exe'
        }
    }
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "ci: no venv at $venv; run ci\test_sdk.ps1 first (the job that builds it), or the CI job that owns it"
    }
    Write-Host "ci: using $venv"
    return $python
}

#: Run one job step and fail the job when it fails. A native command's non-zero
#: exit does not stop a PowerShell 5.1 script on its own, so every step goes
#: through here rather than through a repeated `if ($LASTEXITCODE ...)`.
function Invoke-CiStep {
    param([Parameter(Mandatory)][scriptblock]$Step)
    & $Step
    if ($LASTEXITCODE -ne 0) {
        throw "ci: step exited $LASTEXITCODE"
    }
}
