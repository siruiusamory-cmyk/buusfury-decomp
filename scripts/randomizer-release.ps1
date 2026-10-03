# ENEMY-RANDOMIZER-EXE-001 - the release checks both randomizer tools share.
#
#   . "$PSScriptRoot/randomizer-release.ps1"
#
# Dot-source this, do not run it: it defines functions and has no side effects.
# It exists because the Map Warp Randomizer and the Enemy Randomizer are released
# by the same procedure and, before this file, would have carried two copies of
# it. The copies would have been identical on the day they were written and would
# not have stayed that way - and the copy that matters is the proprietary-content
# probe, where a divergence means one product's release is checked and the other's
# is not.
#
# What the probe does and does not catch is stated once, here, because the
# limitation belongs to the technique rather than to either product:
#
#   * the executable is a compressed PyInstaller archive, so a byte-run probe
#     against it can only see what is NOT compressed: a whole ROM appended to the
#     file, or an uncompressed blob. A carve inside the compressed payload is not
#     searchable this way;
#   * the needles are 48 informative 48-byte windows, so their OFFSETS span most
#     of the image while the bytes actually searched are 0.027% of it. A carve is
#     caught only if it contains one of those exact windows.
#
# What carries the weight instead is that neither build has a ROM as an input at
# all: the only data file bundled is the ROM profile catalog, a table of addresses
# and hashes. The extension check, the exact-hash check and the positive control
# below are the rest of it.

# ISO-8859-1 (code page 28591) maps each byte to the identical code point, so
# round-tripping both sides through it is lossless and lets the runtime's own
# optimized ordinal string search do the scanning. `[System.Text.Encoding]::Latin1`
# is the PowerShell 7 spelling and does not exist on Windows PowerShell 5.1.
$script:RandomizerLatin1 = [System.Text.Encoding]::GetEncoding(28591)

#: Extensions that must never appear in a release archive.
$script:RandomizerForbiddenExtensions = @(
    '.gba', '.agb', '.sav', '.ss0', '.ss1', '.ss2', '.ss3', '.ss4', '.ss5',
    '.ss6', '.ss7', '.ss8', '.ss9', '.sps', '.state', '.srm'
)

function Test-RandomizerContainsBytes {
    param([byte[]] $Haystack, [byte[]] $Needle)
    $text = $script:RandomizerLatin1.GetString($Haystack)
    $pattern = $script:RandomizerLatin1.GetString($Needle)
    return $text.IndexOf($pattern, [System.StringComparison]::Ordinal) -ge 0
}

# Whether a window is worth using as a needle: enough distinct byte values, and no
# long run of one value. Padding and any other degenerate run is rejected, because
# a 48-byte run of 0x00 occurs in every large binary and would flag the runtime as
# "ROM data" - which is exactly what an earlier version of this probe did.
function Test-RandomizerInformative {
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

# The per-file scan, in one place so the positive control exercises the SAME code
# path the real pass uses rather than a shortcut beside it.
function Test-RandomizerFileForRomData {
    param([string] $Path, [byte[][]] $Needles)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    foreach ($needle in $Needles) {
        if (Test-RandomizerContainsBytes -Haystack $bytes -Needle $needle) { return $true }
    }
    return $false
}

<#
.SYNOPSIS
    Fail-closed check that a staged release contains no proprietary content.

.DESCRIPTION
    Returns the list of offences, so the caller decides how to report them. An
    empty list means the checks that could run all passed; it is never a proof of
    absence, for the reasons stated at the top of this file.

.PARAMETER Staged
    The files that will go into the archive.

.PARAMETER CanonicalRom
    The canonical image, used only to build needles and to recognise a copy of
    itself. Never copied anywhere.

.PARAMETER ExpectedSha256
    The canonical image's digest, so a staged file that IS the ROM is caught.

.PARAMETER ExpectedSize
    The canonical image's size in bytes.

.PARAMETER ProbeNeedles
    How many informative windows to draw. 48 by default, as the warp tool's
    release was measured with.

.PARAMETER SkipRomProbe
    Skip the byte probe. The extension and exact-hash checks still run, and the
    caller is expected to say so out loud.
#>
function Assert-RandomizerNoProprietaryContent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [System.IO.FileInfo[]] $Staged,
        [Parameter(Mandatory)] [string] $CanonicalRom,
        [Parameter(Mandatory)] [string] $ExpectedSha256,
        [Parameter(Mandatory)] [int] $ExpectedSize,
        [int] $ProbeNeedles = 48,
        [switch] $SkipRomProbe
    )

    $offenders = @()

    foreach ($file in $Staged) {
        if ($script:RandomizerForbiddenExtensions -contains $file.Extension.ToLowerInvariant()) {
            $offenders += "forbidden extension: $($file.FullName)"
        }
    }

    foreach ($file in $Staged) {
        if ($file.Length -ne $ExpectedSize) { continue }
        if ((Get-FileHash $file.FullName -Algorithm SHA256).Hash -eq $ExpectedSha256) {
            $offenders += "the canonical ROM itself: $($file.FullName)"
        }
    }

    if ($SkipRomProbe) {
        Write-Warning 'ROM-content probe SKIPPED - only the extension and exact-hash checks ran'
        return $offenders
    }

    if (-not (Test-Path $CanonicalRom)) {
        throw "cannot run the ROM-content probe: $CanonicalRom is not present. Re-run with -SkipRomProbe only if you accept that the package was NOT checked for game data."
    }
    $rom = [System.IO.File]::ReadAllBytes((Resolve-Path $CanonicalRom))
    if ($rom.Length -ne $ExpectedSize) {
        throw "the canonical ROM probe needs the $ExpectedSize-byte image"
    }

    $needleLength = 48
    $minimumDistinctBytes = 24
    $maximumConstantRun = 8
    $stride = 4096

    $candidates = New-Object System.Collections.ArrayList
    $candidateOffsets = New-Object System.Collections.ArrayList
    for ($offset = 0; $offset -lt ($rom.Length - $needleLength); $offset += $stride) {
        $window = New-Object byte[] $needleLength
        [Array]::Copy($rom, $offset, $window, 0, $needleLength)
        if (-not (Test-RandomizerInformative -Window $window -MinimumDistinct $minimumDistinctBytes -MaximumRun $maximumConstantRun)) {
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
    $take = [math]::Min($ProbeNeedles, $candidates.Count)
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

    # Positive control through the real per-file scan: a probe that never fires
    # proves nothing about the files it cleared.
    $control = Join-Path ([System.IO.Path]::GetTempPath()) ("randomizer-control-" + [guid]::NewGuid().ToString('N') + ".bin")
    $filler = New-Object byte[] 4096
    (New-Object System.Random 1234).NextBytes($filler)
    [System.IO.File]::WriteAllBytes($control, ($filler + $needles[0] + $filler))
    $controlCaught = Test-RandomizerFileForRomData -Path $control -Needles $needles
    Remove-Item $control -Force
    if (-not $controlCaught) {
        throw "the ROM-content probe failed its own positive control and cannot be trusted"
    }

    foreach ($file in $Staged) {
        if (Test-RandomizerFileForRomData -Path $file.FullName -Needles $needles) {
            $offenders += "ROM data found in $($file.FullName)"
        }
    }

    Write-Host ("scanned {0} file(s) against {1} informative needle(s), offsets {2:N0}..{3:N0} of {4:N0} ({5:P1} of the image spanned; {6:N0} of {4:N0} bytes actually searched)" -f `
        $Staged.Count, $needles.Count, $coverageFrom, $coverageTo, $rom.Length, `
        (($coverageTo - $coverageFrom) / $rom.Length), ($needles.Count * $needleLength))
    Write-Host ("  candidates kept {0} of {1} sampled window(s); positive control PASSED" -f $candidates.Count, [int][math]::Floor($rom.Length / $stride))

    return $offenders
}

<#
.SYNOPSIS
    Run one packaged executable through its own --smoke entry and read the report.

.DESCRIPTION
    A released build is windowed and has no console, so it is asked for a
    machine-readable report through the same window, verification, worker thread
    and boundary the Randomize button uses. The argument line is assembled as a
    STRING with explicit quotes: Start-Process joins an -ArgumentList array with
    spaces and does not quote its elements, so a ROM path containing a space (and
    "Buu's Fury (U).gba" contains two) would arrive as two arguments.
#>
function Invoke-RandomizerSmoke {
    param(
        [Parameter(Mandatory)] [string] $Exe,
        [Parameter(Mandatory)] [string] $Rom,
        [Parameter(Mandatory)] [string] $OutputRom,
        [Parameter(Mandatory)] [string] $ReportPath,
        [string] $Seed,
        [string] $ExtraArguments
    )

    $argumentLine = '--smoke --rom "{0}" --output "{1}" --report "{2}"' -f `
        $Rom, $OutputRom, $ReportPath
    if ($Seed) { $argumentLine += ' --seed "{0}"' -f $Seed }
    if ($ExtraArguments) { $argumentLine += ' ' + $ExtraArguments }

    $process = Start-Process -FilePath $Exe -ArgumentList $argumentLine -Wait -PassThru -WindowStyle Hidden
    $report = if (Test-Path $ReportPath) {
        Get-Content $ReportPath -Raw | ConvertFrom-Json
    } else { $null }

    return [pscustomobject]@{ ExitCode = $process.ExitCode; Report = $report }
}
