# WARPRAND-APP-001 - build the standalone Windows executable.
#
#   pwsh scripts/build-warprand.ps1
#
# Then:  pwsh scripts/smoke-warprand-packaged.ps1
#        pwsh scripts/package-warprand.ps1
#
# The packaging configuration is `Buu-Fury-Warp-Randomizer.spec.in`, which is
# TRACKED. The `.spec` PyInstaller actually consumes is generated from it into
# the repository root and is NOT tracked, because `.gitignore` files `*.spec`
# under "Generated builds" - the same convention that leaves the existing
# `DragonByte Z.spec` untracked. Tracking the template keeps the release
# reproducible from a fresh clone without contradicting that convention.

[CmdletBinding()]
param(
    [string] $BuildName = 'Buu-Fury-Warp-Randomizer',
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
