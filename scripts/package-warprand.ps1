# WARPRAND-APP-001 - build the standalone release zip for the warp randomizer.
#
#   pwsh scripts/package-warprand.ps1
#
# The release is deliberately minimal, at the owner's direction: the archive
# contains the single executable and a brief README, and nothing else. Download,
# extract, run.
#
# That shape is why the build is ONE FILE (`Buu-Fury-Warp-Randomizer.spec.in`
# has no COLLECT): an onedir build cannot be reduced to a lone executable - the
# .exe needs its `_internal/` runtime directory beside it - so shipping just the
# executable required switching to one-file packaging.
#
# The ownership rule this script still enforces: the tool is shipped to people
# who own the game, and the archive must never contain any part of it. The build
# fails closed.
#
# ENEMY-RANDOMIZER-EXE-001 moved the content probe itself into
# `scripts/randomizer-release.ps1`, which the Enemy Randomizer's package script
# dot-sources as well. The probe, its positive control and the precise list of
# what it does and does not catch are one implementation now, because the failure
# mode of two copies is that one product's release gets checked and the other's
# does not. What this script still owns is its own staging list, its own README
# and its own archive name.

[CmdletBinding()]
param(
    [string] $Version = '0.1.0',
    [string] $DistDir = 'dist',
    [string] $BuildName = 'Buu-Fury-Warp-Randomizer',
    [string] $CanonicalRom = "roms/Dragon Ball Z - Buu's Fury (U).gba",
    [string] $ReadmePath = 'docs/warprand/README.txt',
    [switch] $SkipRomProbe
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/randomizer-release.ps1"

$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $exe = Join-Path $DistDir "$BuildName.exe"
    if (-not (Test-Path $exe)) {
        throw "no packaged build at $exe - run: pwsh scripts/build-warprand.ps1 -Clean"
    }
    if (-not (Test-Path $ReadmePath)) { throw "no README to stage at $ReadmePath" }

    # --- 1. the two files the user gets ----------------------------------
    $stage = Join-Path $DistDir "$BuildName-release"
    if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    Copy-Item $exe (Join-Path $stage "$BuildName.exe")
    Copy-Item $ReadmePath (Join-Path $stage 'README.txt')
    $staged = @(Get-ChildItem -Path $stage -File)
    Write-Host ("staged {0} file(s): {1}" -f $staged.Count, (($staged | ForEach-Object { $_.Name }) -join ', '))

    # --- 2. no proprietary content ---------------------------------------
    $offenders = Assert-RandomizerNoProprietaryContent `
        -Staged $staged `
        -CanonicalRom $CanonicalRom `
        -ExpectedSha256 $script:RandomizerCanonicalSha256 `
        -ExpectedSize $script:RandomizerCanonicalSize `
        -SkipRomProbe:$SkipRomProbe

    if ($offenders.Count -gt 0) {
        throw ("proprietary content in the release package:`n  " + ($offenders -join "`n  "))
    }
    if ($SkipRomProbe) {
        Write-Host 'proprietary-content check: NONE FOUND by the extension and exact-hash checks (ROM byte probe SKIPPED - this is NOT the full check)'
    }
    else {
        Write-Host 'proprietary-content check: NONE'
    }

    # --- 3. the archive ---------------------------------------------------
    # Only the exe and the README, at the archive root, so "extract and run" is
    # the whole procedure.
    $zip = Join-Path $DistDir "$BuildName-v$Version-win64.zip"
    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
    $zipInfo = Get-Item $zip
    Write-Host ("release {0} ({1:N1} MB)" -f $zipInfo.FullName, ($zipInfo.Length / 1MB))

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    # An absolute path: the .NET file APIs use the PROCESS working directory, which
    # PowerShell's Push-Location does not change, while every cmdlet above uses the
    # PowerShell location. Resolving here keeps the two views of "where am I" from
    # disagreeing.
    $archive = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path $zip).Path)
    Write-Host ("archive contents: {0}" -f (($archive.Entries | ForEach-Object { $_.FullName }) -join ', '))
    $archive.Dispose()
}
finally {
    Pop-Location
}
