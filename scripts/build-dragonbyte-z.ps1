# DRAGONBYTE-Z-SHIP-V1-001 - build the frozen Windows DragonByte Z.
#
#   pwsh scripts/build-dragonbyte-z.ps1
#
# Then:  pwsh scripts/smoke-dragonbyte-z-packaged.ps1
#
# The packaging configuration is `DragonByte Z.spec.in`, which is TRACKED. The
# `.spec` PyInstaller actually consumes is generated from it into the repository
# root and is NOT tracked, because `.gitignore` files `*.spec` under "Generated
# builds" - the same convention the two randomizer templates use. Tracking the
# template keeps the release reproducible from a fresh clone without contradicting
# that convention.
#
# This is the sibling of `build-enemy-randomizer.ps1` and differs from it in the
# artefact shape: DragonByte Z is an onedir COLLECT build, so the executable is
# `dist\DragonByte Z\DragonByte Z.exe` beside its Qt runtime rather than a lone
# file in `dist\`. The reasons are in the spec's docstring.

[CmdletBinding()]
param(
    [string] $BuildName = 'DragonByte Z',
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
    # --version output and every manifest it writes would record a null commit;
    # with it, the packaged executable names the commit it was cut from. The record
    # is ignored by git and regenerated on every build, so it cannot describe an
    # earlier commit.
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

    $exe = Join-Path (Join-Path 'dist' $BuildName) "$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "PyInstaller reported success but no executable is at $exe" }

    # The identity is a build output, so it is read back from the artefact rather
    # than assumed from the source it was built from: a windowed executable writes
    # this to the redirecting parent's stdout, which is what makes it checkable.
    $visible = & $exe --version
    if ($LASTEXITCODE -ne 0) { throw "$exe --version exited $LASTEXITCODE" }
    $expected = (& python -m tools.webfoot.release_identity | Select-Object -First 1).Trim()
    if ($visible.Trim() -ne $expected) {
        throw "the frozen build reports '$($visible.Trim())' and this checkout reports '$expected'"
    }

    $item = Get-Item $exe
    Write-Host ''
    Write-Host "BUILD OK"
    Write-Host "  executable      : $($item.FullName)"
    Write-Host "  size            : $([math]::Round($item.Length / 1MB, 1)) MB (onedir; the runtime is beside it)"
    Write-Host "  visible version : $($visible.Trim())"
    Write-Host "  sha256          : $((Get-FileHash $exe -Algorithm SHA256).Hash)"
}
finally {
    Pop-Location
}
