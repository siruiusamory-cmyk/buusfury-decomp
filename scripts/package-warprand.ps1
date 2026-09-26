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
# WHAT THE CONTENT CHECK DOES AND DOES NOT CATCH. The single executable is a
# compressed PyInstaller archive, so a byte-run probe against it can only see
# what is NOT compressed: a whole ROM appended to the file, or an uncompressed
# blob. The compressed payload is not searchable this way, so the probe's real
# guarantee here is narrower than it was for a directory of loose DLLs. What
# carries the weight instead is that the build has no ROM as an input at all -
# the only data file bundled is the profile catalog, a table of addresses and
# hashes - and the extension and exact-hash checks still run. Blind spots, stated:
# a carve inside the compressed payload, a transformed copy, content in a nested
# container, and a header-stripped or trimmed copy.

[CmdletBinding()]
param(
    [string] $Version = '0.1.0',
    [string] $DistDir = 'dist',
    [string] $BuildName = 'Buu-Fury-Warp-Randomizer',
    [string] $CanonicalRom = "roms/Dragon Ball Z - Buu's Fury (U).gba",
    [switch] $SkipRomProbe
)

$ErrorActionPreference = 'Stop'

# Byte-run search over a byte[]. ISO-8859-1 (code page 28591) maps each byte to
# the identical code point, so round-tripping both sides through it is lossless
# and lets the runtime's own optimized ordinal string search do the scanning.
# `[System.Text.Encoding]::Latin1` is the PowerShell 7 spelling and does not
# exist on Windows PowerShell 5.1, which ships with Windows.
$Latin1 = [System.Text.Encoding]::GetEncoding(28591)

function Test-ContainsBytes {
    param([byte[]] $Haystack, [byte[]] $Needle)
    $text = $Latin1.GetString($Haystack)
    $pattern = $Latin1.GetString($Needle)
    return $text.IndexOf($pattern, [System.StringComparison]::Ordinal) -ge 0
}

# Whether a window is worth using as a needle: enough distinct byte values, and
# no long run of one value. Padding and any other degenerate run is rejected,
# because a 48-byte run of 0x00 occurs in every large binary and would flag the
# runtime as "ROM data".
function Test-IsInformative {
    param([byte[]] $Window, [int] $MinimumDistinct, [int] $MaximumRun)
    $seen = New-Object 'bool[]' 256
    $distinct = 0
    $run = 1
    for ($i = 0; $i -lt $Window.Length; $i++) {
        $value = $Window[$i]
        if (-not $seen[$value]) { $seen[$value] = $true; $distinct++ }
        if ($i -gt 0 -and $value -eq $Window[$i - 1]) {
            $run++
            if ($run -gt $MaximumRun) { return $false }
        }
        else { $run = 1 }
    }
    return $distinct -ge $MinimumDistinct
}

# The per-file scan, in one place so the positive control exercises the SAME
# code path the real pass uses rather than a shortcut beside it.
function Test-FileForRomData {
    param([string] $Path, [byte[][]] $Needles)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    foreach ($needle in $Needles) {
        if (Test-ContainsBytes -Haystack $bytes -Needle $needle) { return $true }
    }
    return $false
}

$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $exe = Join-Path $DistDir "$BuildName.exe"
    if (-not (Test-Path $exe)) {
        throw "no packaged build at $exe - run: pwsh scripts/build-warprand.ps1 -Clean"
    }

    # --- 1. the two files the user gets ----------------------------------
    $stage = Join-Path $DistDir "$BuildName-release"
    if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    Copy-Item $exe (Join-Path $stage "$BuildName.exe")
    Copy-Item 'docs/warprand/README.txt' (Join-Path $stage 'README.txt')
    $staged = Get-ChildItem -Path $stage -File
    Write-Host ("staged {0} file(s): {1}" -f $staged.Count, (($staged | ForEach-Object { $_.Name }) -join ', '))

    # --- 2. no proprietary content ---------------------------------------
    $forbidden = @('.gba', '.agb', '.sav', '.ss0', '.ss1', '.ss2', '.ss3',
                   '.ss4', '.ss5', '.ss6', '.ss7', '.ss8', '.ss9', '.sps',
                   '.state', '.srm')
    $offenders = @()
    foreach ($file in $staged) {
        if ($forbidden -contains $file.Extension.ToLowerInvariant()) {
            $offenders += "forbidden extension: $($file.FullName)"
        }
    }

    $canonicalSha = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
    $canonicalSize = 8388608
    foreach ($file in $staged) {
        if ($file.Length -ne $canonicalSize) { continue }
        if ((Get-FileHash $file.FullName -Algorithm SHA256).Hash -eq $canonicalSha) {
            $offenders += "the canonical ROM itself: $($file.FullName)"
        }
    }

    if (-not $SkipRomProbe) {
        if (-not (Test-Path $CanonicalRom)) {
            throw "cannot run the ROM-content probe: $CanonicalRom is not present. Re-run with -SkipRomProbe only if you accept that the package was NOT checked for game data."
        }
        $rom = [System.IO.File]::ReadAllBytes((Resolve-Path $CanonicalRom))
        if ($rom.Length -ne $canonicalSize) {
            throw "the canonical ROM probe needs the $canonicalSize-byte image"
        }

        # Needles must be INFORMATIVE (a run of one value occurs in every large
        # binary, which is how an earlier version "found ROM data" in a DLL) and
        # drawn from across the whole image (an earlier version covered the first
        # 2.35% while claiming the whole thing).
        $needleLength = 48
        $needleTarget = 48
        $minimumDistinctBytes = 24
        $maximumConstantRun = 8
        $stride = 4096

        $candidates = New-Object System.Collections.ArrayList
        $candidateOffsets = New-Object System.Collections.ArrayList
        for ($offset = 0; $offset -lt ($rom.Length - $needleLength); $offset += $stride) {
            $window = New-Object byte[] $needleLength
            [Array]::Copy($rom, $offset, $window, 0, $needleLength)
            if (-not (Test-IsInformative -Window $window -MinimumDistinct $minimumDistinctBytes -MaximumRun $maximumConstantRun)) {
                continue
            }
            [void]$candidates.Add($window)
            [void]$candidateOffsets.Add($offset)
        }
        if ($candidates.Count -lt 16) {
            throw "the ROM-content probe found only $($candidates.Count) informative window(s) in the canonical image; refusing to report a check that could not run"
        }

        $needles = @()
        $needleOffsets = @()
        $take = [math]::Min($needleTarget, $candidates.Count)
        for ($i = 0; $i -lt $take; $i++) {
            $index = if ($take -le 1) {
                0
            } else {
                [int][math]::Floor($i * ($candidates.Count - 1) / ($take - 1))
            }
            $needles += ,$candidates[$index]
            $needleOffsets += $candidateOffsets[$index]
        }
        $coverageFrom = ($needleOffsets | Measure-Object -Minimum).Minimum
        $coverageTo = ($needleOffsets | Measure-Object -Maximum).Maximum

        # Positive control through the real per-file scan.
        $control = Join-Path ([System.IO.Path]::GetTempPath()) ("warprand-control-" + [guid]::NewGuid().ToString('N') + ".bin")
        $filler = New-Object byte[] 4096
        (New-Object System.Random 1234).NextBytes($filler)
        [System.IO.File]::WriteAllBytes($control, ($filler + $needles[0] + $filler))
        $controlCaught = Test-FileForRomData -Path $control -Needles $needles
        Remove-Item $control -Force
        if (-not $controlCaught) {
            throw "the ROM-content probe failed its own positive control and cannot be trusted"
        }

        foreach ($file in $staged) {
            if (Test-FileForRomData -Path $file.FullName -Needles $needles) {
                $offenders += "ROM data found in $($file.FullName)"
            }
        }
        Write-Host ("scanned {0} file(s) against {1} informative needle(s), offsets {2:N0}..{3:N0} of {4:N0} ({5:P1} of the image spanned; {6:N0} of {4:N0} bytes actually searched)" -f `
            $staged.Count, $needles.Count, $coverageFrom, $coverageTo, $rom.Length, `
            (($coverageTo - $coverageFrom) / $rom.Length), ($needles.Count * $needleLength))
        Write-Host ("  candidates kept {0} of {1} sampled window(s); positive control PASSED" -f $candidates.Count, [int][math]::Floor($rom.Length / $stride))
    }
    else {
        Write-Warning 'ROM-content probe SKIPPED - only the extension and exact-hash checks ran'
    }

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
    $archive = [System.IO.Compression.ZipFile]::OpenRead($zip)
    Write-Host ("archive contents: {0}" -f (($archive.Entries | ForEach-Object { $_.FullName }) -join ', '))
    $archive.Dispose()
}
finally {
    Pop-Location
}
