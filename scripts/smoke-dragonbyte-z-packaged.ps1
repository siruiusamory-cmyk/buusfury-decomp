# DRAGONBYTE-Z-SHIP-V1-001 - the packaged-executable smoke.
#
#   pwsh scripts/smoke-dragonbyte-z-packaged.ps1
#
# This drives the ACTUAL RELEASE EXECUTABLE - not a python script, not a pytest
# fixture, not the interpreter from the checkout. The frozen build is windowed and
# has no console, so it is asked for a machine-readable report through its own
# `--smoke` entry, which opens a real project directory through the same session,
# project reader and ROM identification the window uses.
#
# What it proves, in order:
#   * the frozen build reports the version this checkout records;
#   * the frozen build OPENS A PROJECT, which is the acceptance clause, and names
#     it in its own report rather than exiting 0 and hoping;
#   * the same build identifies the canonical image by digest when one is named;
#   * the artefact's own sha256 and visible version are recorded, because an
#     artefact is evidence only when both are;
#   * the canonical image is byte-identical before and after.

[CmdletBinding()]
param(
    [string] $DistDir = 'build/packaged',
    [string] $BuildName = 'DragonByte Z',
    [string] $CanonicalRom = "roms/Dragon Ball Z - Buu's Fury (U).gba",
    [string] $WorkDir = 'build/dragonbyte-z-packaged'
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $script:Utf8 = New-Object System.Text.UTF8Encoding($false)

    $exe = Join-Path (Join-Path $DistDir $BuildName) "$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "no packaged executable at $exe - run: pwsh scripts/build-dragonbyte-z.ps1 -Clean" }
    if (-not (Test-Path $CanonicalRom)) { throw "canonical ROM not found at $CanonicalRom" }
    $exe = (Resolve-Path $exe).Path
    $rom = (Resolve-Path $CanonicalRom).Path

    $source = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
    $before = (Get-FileHash $rom -Algorithm SHA256).Hash
    if ($before -ne $source) { throw "the canonical ROM is not canonical before the smoke: $before" }

    # --- the project the frozen build is asked to open --------------------
    # The profile and the base digest come from the tracked catalog rather than
    # from a literal here: a smoke run that invented them would test the fixture.
    $catalog = Get-Content 'config/roms.yaml' -Raw
    $profileId = ([regex]'id:\s*(\S+)').Match($catalog).Groups[1].Value
    $baseSha = ([regex]'sha256:\s*([0-9a-f]{64})').Match($catalog).Groups[1].Value
    $baseSize = ([regex]'size:\s*(\d+)').Match($catalog).Groups[1].Value
    if (-not $profileId -or -not $baseSha -or -not $baseSize) {
        throw 'could not read the profile id, digest and size from config/roms.yaml'
    }

    $work = Join-Path (Get-Location) $WorkDir
    if (Test-Path $work) { Remove-Item $work -Recurse -Force }
    $project = Join-Path $work 'project'
    New-Item -ItemType Directory -Force -Path $project | Out-Null

    $toml = @"
[project]
format_version = 1
name = "packaged-smoke"

[base]
profile_id = "$profileId"
game = "Dragon Ball Z: Buu's Fury"
sha256 = "$baseSha"
size = $baseSize
"@
    [System.IO.File]::WriteAllText((Join-Path $project 'project.toml'), $toml, $script:Utf8)

    # --- the frozen build reports its version ------------------------------
    # Through Start-Process rather than `& $exe`: a GUI-subsystem process has no
    # console for PowerShell to redirect, so `& $exe --version` returned no output
    # and no exit code at all. Measured here.
    #
    # Every argument is quoted: Start-Process joins the list into one command line
    # itself and does NOT quote an item that contains spaces, so an unquoted
    # `roms\Dragon Ball Z - Buu's Fury (U).gba` reached the application as
    # `...\roms\Dragon` and the ROM open failed. Also measured here.
    function Invoke-Packaged {
        param([string[]] $Arguments, [string] $StdOut)
        $quoted = @($Arguments | ForEach-Object { '"' + $_ + '"' })
        $process = Start-Process -FilePath $exe -ArgumentList $quoted -NoNewWindow `
            -Wait -PassThru -RedirectStandardOutput $StdOut -RedirectStandardError "$StdOut.err"
        return $process.ExitCode
    }

    $versionFile = Join-Path $work 'version.txt'
    $versionExit = Invoke-Packaged -Arguments @('--version') -StdOut $versionFile
    if ($versionExit -ne 0) { throw "$exe --version exited $versionExit" }
    $visible = (Get-Content $versionFile -Raw).Trim()
    $recorded = (& python -m tools.webfoot.release_identity | Select-Object -First 1).Trim()
    if ($visible -ne $recorded) {
        throw "the packaged build reports '$visible' and this checkout records '$recorded'"
    }

    # --- the frozen build opens the project --------------------------------
    $report = Join-Path $work 'packaged-smoke.json'
    $exitCode = Invoke-Packaged -Arguments @(
        '--smoke', $project, '--smoke-rom', $rom, '--smoke-report', $report
    ) -StdOut (Join-Path $work 'smoke-stdout.txt')
    if (-not (Test-Path $report)) { throw "the packaged build exited $exitCode and wrote no report" }
    if ($exitCode -ne 0) { throw "the packaged build exited $exitCode (see $report)" }

    $document = Get-Content $report -Raw | ConvertFrom-Json
    if ($document.error) { throw "the packaged build reported: $($document.error)" }
    if (-not $document.project.opened) { throw 'the packaged build did not open the project it was given' }
    if ($document.project.name -ne 'packaged-smoke') { throw "unexpected project name: $($document.project.name)" }
    if (-not $document.rom.opened) { throw 'the packaged build did not identify the canonical image' }
    if ($document.rom.sha256.ToUpperInvariant() -ne $source) {
        throw "the packaged build identified sha256 $($document.rom.sha256), not the canonical image"
    }
    if ($document.identity.product.name -ne $BuildName) {
        throw "the packaged build reports product '$($document.identity.product.name)'"
    }
    if ("$($document.identity.product.name) $($document.identity.product.version)" -ne $visible) {
        throw "the packaged build's report and its --version disagree"
    }

    # --- the canonical image is still canonical ----------------------------
    $after = (Get-FileHash $rom -Algorithm SHA256).Hash
    if ($after -ne $source) { throw "the canonical ROM changed during the smoke: $after" }

    $digest = (Get-FileHash $exe -Algorithm SHA256).Hash
    $item = Get-Item $exe

    Write-Host ''
    Write-Host "PACKAGED EXE SMOKE: PASS"
    Write-Host "  executable        : $($item.FullName)"
    Write-Host "  executable sha256 : $digest"
    Write-Host "  executable mtime  : $($item.LastWriteTimeUtc.ToString('o'))"
    Write-Host "  visible version   : $visible"
    Write-Host "  build commit      : $($document.identity.build.commit)"
    Write-Host "  build source      : $($document.identity.build.source)"
    Write-Host "  project opened    : $($document.project.opened) ($($document.project.name))"
    Write-Host "  ROM identified    : $($document.rom.sha256)"
    Write-Host "  report            : $report"
    Write-Host "  canonical before  : $before"
    Write-Host "  canonical after   : $after"
}
finally {
    Pop-Location
}
