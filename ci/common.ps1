# Shared plumbing for the self-hosted Windows CI runner.
#
# The job bodies live in `ci\*.ps1` rather than in `.gitlab-ci.yml` so that the
# same script a job runs can be run by hand for a measurement. This file is
# dot-sourced by each of them and defines no job of its own. It is Windows
# PowerShell 5.1: no `??`, no ternary, no `-Parallel`.

$ErrorActionPreference = 'Stop'

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
    if (Test-Path -LiteralPath $venv) { Remove-Item -LiteralPath $venv -Recurse -Force }
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
function Use-CiVenv {
    param([Parameter(Mandatory)][string]$Name)
    $venv = Get-CiVenvDirectory -Name $Name
    $python = Join-Path $venv 'Scripts\python.exe'
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
