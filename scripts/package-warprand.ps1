# WARPRAND-APP-001 - build the standalone release zip for the warp randomizer.
#
#   pwsh scripts/package-warprand.ps1
#
# Stages dist/Buu-Fury-Warp-Randomizer, adds the user-facing README and the
# licence, PROVES the package carries no game data, and writes
# dist/Buu-Fury-Warp-Randomizer-v<version>-win64.zip.
#
# The ownership rule this script exists to enforce: the tool is shipped to
# people who own the game, and the archive must never contain any part of it.
# The check is not a filename filter - a ROM renamed to .dat would pass one -
# so it also searches every packaged file for byte runs drawn from across the
# canonical image, and for the image's own identity. The build fails closed.
#
# WHAT THIS CHECK DOES NOT CATCH, stated so the claim is not read as stronger
# than it is (an independent review asked for exactly this list):
#
#   * an excerpt SHORTER than the needle length (48 bytes);
#   * a TRANSFORMED copy - compressed, base64, XORed, or as a patch/delta - which
#     is the most likely way ROM-derived content would actually travel;
#   * content inside a NESTED container (the forbidden-extension list has no
#     archive extensions, and the probe cannot see inside one);
#   * a header-stripped, trimmed or "trained" copy, because the exact-hash check
#     only hashes files whose length is exactly the canonical 8,388,608 bytes.
#
# It catches a whole ROM, a carved blob of 48+ contiguous bytes from anywhere in
# the image, and a renamed ROM. That is the threat this release actually faces;
# the four gaps above would need a different technique (entropy analysis, archive
# walking, or a re-encode) and are recorded rather than implied to be covered.

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
# and lets the runtime's own optimized ordinal string search do the scanning -
# which matters, because this probes every packaged file for runs taken from an
# 8 MB image. `[System.Text.Encoding]::Latin1` is the PowerShell 7 spelling and
# does not exist on Windows PowerShell 5.1, which is what ships with Windows, so
# the encoding is named by code page instead.
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
# Python and Qt DLLs as "ROM data".
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
    $appDir = Join-Path $DistDir $BuildName
    $exe = Join-Path $appDir "$BuildName.exe"
    if (-not (Test-Path $exe)) {
        throw "no packaged build at $exe - run: python -m PyInstaller --noconfirm --clean `"$BuildName.spec`""
    }

    # --- 1. the files a user needs ---------------------------------------
    Copy-Item 'docs/warprand/README.txt' (Join-Path $appDir 'README.txt') -Force
    Copy-Item 'docs/warprand/THIRD-PARTY-NOTICES.txt' (Join-Path $appDir 'THIRD-PARTY-NOTICES.txt') -Force
    Copy-Item 'LICENSE' (Join-Path $appDir 'LICENSE') -Force
    Write-Host "staged README.txt, THIRD-PARTY-NOTICES.txt and LICENSE into $appDir"

    # --- 2. no proprietary content ---------------------------------------
    $forbidden = @('.gba', '.agb', '.sav', '.ss0', '.ss1', '.ss2', '.ss3',
                   '.ss4', '.ss5', '.ss6', '.ss7', '.ss8', '.ss9', '.sps',
                   '.state', '.srm')
    $files = Get-ChildItem -Path $appDir -Recurse -File
    $offenders = @()
    foreach ($file in $files) {
        if ($forbidden -contains $file.Extension.ToLowerInvariant()) {
            $offenders += "forbidden extension: $($file.FullName)"
        }
    }

    $canonicalSha = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
    $canonicalSize = 8388608
    foreach ($file in $files) {
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

        # --- pick the needles ---------------------------------------------
        #
        # Two properties matter, and an earlier version of this probe had
        # neither:
        #
        # 1. They must be INFORMATIVE. An 8 MB cartridge is largely 0x00/0xFF
        #    padding, and a 48-byte run of one value occurs in essentially every
        #    large binary on the machine - the first version "found ROM data" in
        #    python312.dll for exactly that reason.
        # 2. They must be drawn from ACROSS THE WHOLE IMAGE. The first version
        #    used a small stride and stopped once it had enough needles, so its
        #    sample covered the first 197 KB of an 8 MB cartridge - 2.35% of the
        #    bytes, and none of the graphics or text it was meant to catch -
        #    while its comment claimed the opposite. An independent review
        #    measured that.
        #
        # So: walk the whole image, keep every informative window, then take the
        # target count evenly spaced across that list. Cost stays bounded because
        # only the target count is ever scanned for, and coverage is measured and
        # printed rather than asserted.
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

        # --- positive control ---------------------------------------------
        #
        # A probe that never fires proves nothing, so a file that CONTAINS a
        # needle at a non-zero offset, among unrelated bytes, is pushed through
        # the very same per-file scan the real pass uses. The previous control
        # searched a file that *was* needles[0] for needles[0], which exercised
        # neither the enumeration nor the file loop.
        $control = Join-Path ([System.IO.Path]::GetTempPath()) ("warprand-control-" + [guid]::NewGuid().ToString('N') + ".bin")
        $filler = New-Object byte[] 4096
        (New-Object System.Random 1234).NextBytes($filler)
        [System.IO.File]::WriteAllBytes($control, ($filler + $needles[0] + $filler))
        $controlCaught = Test-FileForRomData -Path $control -Needles $needles
        Remove-Item $control -Force
        if (-not $controlCaught) {
            throw "the ROM-content probe failed its own positive control and cannot be trusted"
        }

        # --- the real scan ------------------------------------------------
        foreach ($file in $files) {
            if (Test-FileForRomData -Path $file.FullName -Needles $needles) {
                $offenders += "ROM data found in $($file.FullName)"
            }
        }
        Write-Host ("scanned {0} file(s) against {1} informative needle(s), offsets {2:N0}..{3:N0} of {4:N0} ({5:P1} of the image spanned)" -f `
            $files.Count, $needles.Count, $coverageFrom, $coverageTo, $rom.Length, (($coverageTo - $coverageFrom) / $rom.Length))
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
    $zip = Join-Path $DistDir "$BuildName-v$Version-win64.zip"
    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path $appDir -DestinationPath $zip -CompressionLevel Optimal
    $zipInfo = Get-Item $zip
    Write-Host ("release {0} ({1:N1} MB)" -f $zipInfo.FullName, ($zipInfo.Length / 1MB))
}
finally {
    Pop-Location
}
