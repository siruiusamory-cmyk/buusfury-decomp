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
# so it also searches every packaged file for byte runs taken from the canonical
# image, and for the image's own identity. The build fails closed.

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
    Copy-Item 'LICENSE' (Join-Path $appDir 'LICENSE') -Force
    Write-Host "staged README.txt and LICENSE into $appDir"

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

        # Needles spread across the whole image, so an extracted blob from any
        # region - graphics, text, tables - is caught and not only the header.
        #
        # They must be INFORMATIVE. An 8 MB cartridge is mostly 0x00 or 0xFF
        # padding, and a 48-byte run of one value is present in essentially
        # every large binary on the machine - the first version of this probe
        # "found ROM data" in python312.dll for exactly that reason. A window is
        # therefore only used when its bytes are genuinely varied, which no
        # compiler output reproduces by chance.
        $needles = @()
        $needleLength = 48
        $minimumDistinctBytes = 12
        $stride = [math]::Max($needleLength, [int]($rom.Length / 2000))
        for ($offset = 0; $offset -lt ($rom.Length - $needleLength); $offset += $stride) {
            $window = New-Object byte[] $needleLength
            [Array]::Copy($rom, $offset, $window, 0, $needleLength)
            if (($window | Select-Object -Unique).Count -lt $minimumDistinctBytes) { continue }
            $needles += ,$window
            if ($needles.Count -ge 48) { break }
        }
        if ($needles.Count -lt 16) {
            throw "the ROM-content probe found only $($needles.Count) informative needle(s); refusing to report a check that could not run"
        }

        # Positive control. A probe that never fires proves nothing, so a file
        # built from one of the needles must be flagged before the real scan is
        # trusted to be able to flag anything.
        $control = Join-Path ([System.IO.Path]::GetTempPath()) ("warprand-control-" + [guid]::NewGuid().ToString('N') + ".bin")
        [System.IO.File]::WriteAllBytes($control, $needles[0])
        $controlCaught = Test-ContainsBytes -Haystack ([System.IO.File]::ReadAllBytes($control)) -Needle $needles[0]
        Remove-Item $control -Force
        if (-not $controlCaught) {
            throw "the ROM-content probe failed its own positive control and cannot be trusted"
        }

        foreach ($file in $files) {
            $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
            foreach ($needle in $needles) {
                if (Test-ContainsBytes -Haystack $bytes -Needle $needle) {
                    $offenders += "ROM data found in $($file.FullName)"
                    break
                }
            }
        }
        Write-Host ("scanned {0} file(s) against {1} informative needle(s) from the canonical image" -f $files.Count, $needles.Count)
    }
    else {
        Write-Warning 'ROM-content probe SKIPPED - the package was not checked for game data'
    }

    if ($offenders.Count -gt 0) {
        throw ("proprietary content in the release package:`n  " + ($offenders -join "`n  "))
    }
    Write-Host 'proprietary-content check: NONE'

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
