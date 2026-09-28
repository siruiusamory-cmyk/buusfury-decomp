#Requires -Version 5.1
<#
.SYNOPSIS
    Fetch the public Buu's Fury disassembly into reference/ (gitignored), and
    optionally build its JCALG1 compression front-end.

.DESCRIPTION
    The reference project is 2genkidev/buusfury. It is pinned to one commit so
    that the region map's provenance is reproducible.

    LICENCE WARNING - READ THIS.
    The GitHub API reports "license": null for 2genkidev/buusfury. There is no
    licence file and no licence grant. Under default copyright that means
    all rights are reserved. This script therefore fetches it into a directory
    that .gitignore excludes, for reading and for running the build path only.
    Do NOT copy its source into this repository, and do NOT commit it.

    It also carries ROM-derived content (the BMP assets are extracted from the
    commercial game) and a prebuilt third-party Windows binary
    (tools/compress/jcalg1/JCALG1.dll). Neither may be committed.

.PARAMETER Destination
    Where to clone. Default: <repo>/reference/buusfury

.PARAMETER Commit
    The commit to check out. Default: cc53d0cd2d1c167e749419187e2d92017ac07468
    (the tip of master as of 2025-07-27, and the revision the region map was
    derived from).

.PARAMETER BuildTools
    Also build tools/compress (the JCALG1 front-end) into build/tools/compress.exe,
    which the asset-rebuild gate needs. Requires the Visual Studio CMake.

.EXAMPLE
    powershell -File scripts/fetch-reference.ps1 -BuildTools
#>
[CmdletBinding()]
param(
    [string] $Destination,
    [string] $Commit = 'cc53d0cd2d1c167e749419187e2d92017ac07468',
    [switch] $BuildTools
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Destination) { $Destination = Join-Path $repoRoot 'reference/buusfury' }

$url = 'https://github.com/2genkidev/buusfury.git'

Write-Host "reference project : $url"
Write-Host "pinned commit     : $Commit"
Write-Host "destination       : $Destination"
Write-Host ""
Write-Host "NOTE: this project has NO licence. It is fetched for reading and for" -ForegroundColor Yellow
Write-Host "      running its build path only. Never copy its source into this" -ForegroundColor Yellow
Write-Host "      repository and never commit this directory." -ForegroundColor Yellow
Write-Host ""

if (Test-Path (Join-Path $Destination '.git')) {
    Write-Host "already present; fetching and checking out the pinned commit"
    git -C $Destination fetch --all --tags
} else {
    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    git clone $url $Destination
}
git -C $Destination checkout $Commit
git -C $Destination submodule update --init --recursive

$head = git -C $Destination rev-parse HEAD
Write-Host ""
Write-Host "HEAD is now $head"
if ($head -ne $Commit) {
    Write-Warning "HEAD does not equal the pinned commit; the region map's provenance no longer matches."
}

# Confirm the fetch landed somewhere Git will not publish.
Push-Location $repoRoot
try {
    $ignored = git check-ignore -q 'reference/buusfury' 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "confirmed: reference/ is gitignored and cannot be committed" -ForegroundColor Green
    } else {
        Write-Warning "reference/ does not appear to be gitignored. Stop and check .gitignore."
    }
} finally {
    Pop-Location
}

if ($BuildTools) {
    Write-Host ""
    Write-Host "building the JCALG1 compression front-end"
    $python = (Get-Command python, python3, py -ErrorAction SilentlyContinue |
        Select-Object -First 1).Source
    $env:PYTHONPATH = Join-Path $repoRoot 'tools'
    & $python -c @"
from pathlib import Path
from buusfury import assets
out = Path(r'$repoRoot') / 'build' / 'tools'
exe = assets.build_compress_exe(Path(r'$Destination'), out)
print('built', exe)
"@
    if ($LASTEXITCODE -ne 0) { throw "failed to build the JCALG1 front-end" }
}
