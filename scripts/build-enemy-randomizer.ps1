# ENEMY-RANDOMIZER-EXE-001 - build the standalone Windows Enemy Randomizer.
#
#   pwsh scripts/build-enemy-randomizer.ps1
#
# Then:  pwsh scripts/smoke-enemy-randomizer-packaged.ps1
#        pwsh scripts/package-enemy-randomizer.ps1
#
# The packaging configuration is `Enemy-Randomizer.spec.in`, which is TRACKED.
# The `.spec` PyInstaller actually consumes is generated from it into the
# repository root and is NOT tracked, because `.gitignore` files `*.spec` under
# "Generated builds" - the convention that also leaves `DragonByte Z.spec`
# untracked. Tracking the template keeps the release reproducible from a fresh
# clone without contradicting that convention.
#
# This script is the sibling of `build-warprand.ps1` and holds the same logic; the
# two differ only in the build name, which is why the spec template carries each
# product's own entry script and name.

[CmdletBinding()]
param(
    [string] $BuildName = 'Enemy-Randomizer',
    [switch] $Clean
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $template = "$BuildName.spec.in"
    $spec = "$BuildName.spec"
    if (-not (Test-Path $template)) { throw "no packaging template at $template" }

    Copy-Item $template $spec -Force
    Write-Host "generated $spec from $template (the .spec is a build artifact)"

    # RELEASE-ARTEFACT-001 / N-26. Bake the build identity in BEFORE the analysis
    # runs. A packaged build has no checkout and no git to ask, so without this the
    # manifest it writes records a null commit; with it, the packaged executable
    # names the commit it was cut from. The record is ignored by git and is
    # regenerated on every build, so it cannot describe an earlier commit.
    & python -m tools.webfoot.release_identity --write-record
    if ($LASTEXITCODE -ne 0) { throw "could not write the build identity record" }

    $arguments = @('-m', 'PyInstaller', '--noconfirm')
    if ($Clean) { $arguments += '--clean' }
    $arguments += $spec

    # PyInstaller logs INFO to stderr, and Windows PowerShell treats a native
    # command's stderr as a terminating error while $ErrorActionPreference is
    # 'Stop'. The exit code is the signal that matters here, so it is read
    # explicitly instead of inferred from the stream.
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & python @arguments
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previous
    if ($exitCode -ne 0) { throw "PyInstaller exited $exitCode" }

    # One file: the release IS the executable, so there is no build directory to
    # measure and nothing has to sit beside it for it to run.
    $exe = Join-Path 'dist' "$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "PyInstaller reported success but no executable is at $exe" }

    $item = Get-Item $exe
    Write-Host ''
    Write-Host "BUILD OK"
    Write-Host "  executable : $($item.FullName)"
    Write-Host "  size       : $([math]::Round($item.Length / 1MB, 1)) MB (single file)"
}
finally {
    Pop-Location
}
