# The frozen Windows build of Buu's Fury Text Editor.
#
#   pwsh scripts/build-buufury-text.ps1
#
# Then:  pwsh scripts/smoke-buufury-text-packaged.ps1
#
# The packaging configuration is `Buu's Fury Text Editor.spec.in`, which is TRACKED.
# The `.spec` PyInstaller actually consumes is generated from it into the repository
# root and is NOT tracked, because `.gitignore` files `*.spec` under "Generated
# builds" - the same convention the other templates use. Tracking the template keeps
# the release reproducible from a fresh clone without contradicting that convention.
#
# This is the sibling of `build-dragonbyte-z.ps1` and differs from it in two places:
# the product it freezes, and the staged-artefact checks below, which refuse a
# bundle whose Qt SVG image plugin or icon set did not travel. Everything else -
# the onedir COLLECT shape, the baked build identity, the distpath, the read-back of
# the visible version from the artefact - is the established shape, on purpose.
#
# `dist\` is shared with the public site: `npm run build` (Astro) empties it, with no
# prompt, and removed a finished freeze once. The freeze therefore lands under the
# ignored build tree instead, which leaves `dist\` to the site alone.

[CmdletBinding()]
param(
    [string] $BuildName = "Buu's Fury Text Editor",
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

    # Bake the build identity in BEFORE the analysis runs. A packaged build has no
    # checkout and no git to ask, so without this the manifests it writes would record
    # a null commit; with it, the packaged build names the commit it was cut from. The
    # record is generated, ignored by git and rewritten on every build, so it cannot
    # describe an earlier commit. It is the repository's one build-identity authority,
    # shared with the other frozen products rather than reimplemented here.
    & python -m tools.webfoot.release_identity --write-record
    if ($LASTEXITCODE -ne 0) { throw "could not write the build identity record" }

    $arguments = @('-m', 'PyInstaller', '--noconfirm')
    if ($Clean) { $arguments += '--clean' }
    $arguments += @('--distpath', 'build/packaged')
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

    $folder = Join-Path 'build/packaged' $BuildName
    $exe = Join-Path $folder "$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "PyInstaller reported success but no executable is at $exe" }

    # What the frozen build needs and an import graph cannot promise, checked against
    # the artefact rather than assumed. A missing SVG image plugin is invisible in a
    # checkout and blank icons in a release, so the build fails here instead.
    #
    # Onedir contents live in `_internal` and that directory is what `sys._MEIPASS`
    # names for a frozen build, which is why the icons are declared with `icons` as
    # their destination and found here under the same name.
    $internals = Join-Path $folder '_internal'
    $svgPlugin = Join-Path $internals 'PySide6\plugins\imageformats\qsvg.dll'
    $svgLibrary = Join-Path $internals 'PySide6\Qt6Svg.dll'
    if (-not (Test-Path $svgPlugin)) { throw "the staged build has no Qt SVG image plugin at $svgPlugin" }
    if (-not (Test-Path $svgLibrary)) { throw "the staged build has no Qt SVG library at $svgLibrary" }
    $icons = @(Get-ChildItem (Join-Path $internals 'icons') -Filter '*.svg' -ErrorAction SilentlyContinue)
    if ($icons.Count -eq 0) { throw "the staged build carries no icons under $internals\icons" }

    # The identity is a build output, so it is read back from the artefact rather
    # than assumed from the source it was built from. The frozen build is windowed,
    # so its stdout only exists when a file was opened for it: PowerShell's own
    # redirection captures nothing from a GUI-subsystem process.
    $versionFile = Join-Path 'build' 'buufury-text-version.txt'
    $process = Start-Process -FilePath $exe -ArgumentList '--version' -NoNewWindow -Wait `
        -PassThru -RedirectStandardOutput $versionFile
    if ($process.ExitCode -ne 0) { throw "$exe --version exited $($process.ExitCode)" }
    $visible = (Get-Content $versionFile -Raw).Trim()
    $expected = (& python -c "import tools.buufury_text.identity as identity; print(identity.PRODUCT_NAME, identity.PRODUCT_VERSION)").Trim()
    if ($visible -ne $expected) {
        throw "the frozen build reports '$visible' and this checkout records '$expected'"
    }

    $item = Get-Item $exe
    $staged = Get-ChildItem $folder -Recurse -File | Measure-Object -Property Length -Sum
    Write-Host ''
    Write-Host "BUILD OK"
    Write-Host "  executable      : $($item.FullName)"
    Write-Host "  staged folder   : $folder"
    Write-Host "  staged size     : $([math]::Round($staged.Sum / 1MB, 1)) MB in $($staged.Count) files"
    Write-Host "  svg plugin      : $svgPlugin"
    Write-Host "  svg library     : $svgLibrary"
    Write-Host "  icons staged    : $($icons.Count)"
    Write-Host "  visible version : $visible"
    Write-Host "  sha256          : $((Get-FileHash $exe -Algorithm SHA256).Hash)"

    # Measured on the sibling: PyInstaller writes INFO to stderr after stdout is
    # closed, Python's final TextIOWrapper flush then raises, and PowerShell surfaces
    # that as an exit code of 1 even though every check above passed and the artefact
    # is complete. A release script that reported failure for a build it just proved
    # would fail every wrapper that reads the code, so the proof above is the signal.
    exit 0
}
finally {
    Pop-Location
}
