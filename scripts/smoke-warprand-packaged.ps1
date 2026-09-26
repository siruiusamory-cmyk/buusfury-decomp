# WARPRAND-APP-001 - the packaged-executable smoke, plus the golden hash.
#
#   pwsh scripts/smoke-warprand-packaged.ps1
#
# This drives the ACTUAL RELEASE EXECUTABLE - not a python script, not a pytest
# fixture, not the repository CLI. The frozen build is windowed and has no
# console, so it is asked for a machine-readable report through its own --smoke
# entry, which goes through the same window, the same verification, the same
# worker thread and the same boundary the Randomize button uses.
#
# It records the accepted v0.1.0 golden output SHA-256 for the launch seed Goku
# and proves a second run of the same seed is byte-identical, and that the
# canonical ROM is untouched throughout.

[CmdletBinding()]
param(
    [string] $DistDir = 'dist',
    [string] $BuildName = 'Buu-Fury-Warp-Randomizer',
    [string] $CanonicalRom = "roms/Dragon Ball Z - Buu's Fury (U).gba",
    [string] $WorkDir = 'build/warprand-app-001-packaged',
    [string] $GoldenSeed = 'Goku',
    [string] $GoldenSha256 = 'ed167ca17944e4782cf19bf31245f772e5b7b9f5c66af317ddbedc8906c5abdc'
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $exe = Join-Path $DistDir "$BuildName/$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "no packaged executable at $exe" }
    if (-not (Test-Path $CanonicalRom)) { throw "canonical ROM not found at $CanonicalRom" }

    $exe = (Resolve-Path $exe).Path
    $rom = (Resolve-Path $CanonicalRom).Path
    $work = Join-Path (Get-Location) $WorkDir
    if (Test-Path $work) { Remove-Item $work -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $work | Out-Null

    $source = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
    $beforeHash = (Get-FileHash $rom -Algorithm SHA256).Hash
    if ($beforeHash -ne $source) { throw "the canonical ROM is not canonical before the smoke: $beforeHash" }

    function Invoke-Smoke {
        param([string] $OutputRom, [string] $ReportPath, [string] $Seed)
        # Quoted explicitly: Start-Process joins an -ArgumentList array with
        # spaces and does NOT quote its elements, so "Buu's Fury (U).gba" would
        # reach the executable as two arguments and be read as a shorter path.
        $argumentLine = '--smoke --rom "{0}" --output "{1}" --report "{2}"' -f `
            $rom, $OutputRom, $ReportPath
        if ($Seed) { $argumentLine += ' --seed "{0}"' -f $Seed }
        $process = Start-Process -FilePath $exe -ArgumentList $argumentLine -Wait -PassThru -WindowStyle Hidden
        $report = if (Test-Path $ReportPath) {
            Get-Content $ReportPath -Raw | ConvertFrom-Json
        } else { $null }
        return [pscustomobject]@{ ExitCode = $process.ExitCode; Report = $report }
    }

    # --- run 1: the golden launch-seed run -------------------------------
    $firstRom = Join-Path $work "Buu's Fury - Warp Randomized - $GoldenSeed.gba"
    $firstReport = Join-Path $work 'run1.json'
    $one = Invoke-Smoke -OutputRom $firstRom -ReportPath $firstReport -Seed $null

    if ($one.ExitCode -ne 0) { throw "packaged smoke run 1 exited $($one.ExitCode): $($one.Report.status)" }
    if (-not $one.Report.ok) { throw "packaged smoke run 1 reported failure: $($one.Report.status)" }
    if (-not (Test-Path $firstRom)) { throw "the packaged build reported success but wrote no ROM" }
    if (-not $one.Report.seed_is_launch_seed) {
        throw "the packaged build did not launch on the $GoldenSeed seed"
    }
    if ($one.Report.seed -ne $GoldenSeed) { throw "unexpected seed: $($one.Report.seed)" }

    $firstHash = (Get-FileHash $firstRom -Algorithm SHA256).Hash
    if ($one.Report.output_sha256.ToUpperInvariant() -ne $firstHash) {
        throw "the reported hash is not the file that was written"
    }
    if ($one.Report.manifest -and -not (Test-Path $one.Report.manifest)) {
        throw "the packaged build reported a manifest that does not exist"
    }
    if (-not $one.Report.source_unchanged) { throw "the packaged build reports the source ROM changed" }

    # --- run 2: the same seed to a second path ---------------------------
    $secondRom = Join-Path $work "second-$GoldenSeed.gba"
    $secondReport = Join-Path $work 'run2.json'
    $two = Invoke-Smoke -OutputRom $secondRom -ReportPath $secondReport -Seed $GoldenSeed
    if ($two.ExitCode -ne 0) { throw "packaged smoke run 2 exited $($two.ExitCode)" }
    $secondHash = (Get-FileHash $secondRom -Algorithm SHA256).Hash
    if ($firstHash -ne $secondHash) {
        throw "two runs of the same seed differ: $firstHash vs $secondHash"
    }

    # --- the canonical ROM is still canonical ----------------------------
    $afterHash = (Get-FileHash $rom -Algorithm SHA256).Hash
    if ($afterHash -ne $source) { throw "the canonical ROM changed during the smoke: $afterHash" }

    # --- the recorded golden value ---------------------------------------
    if ($GoldenSha256 -and ($firstHash -ne $GoldenSha256.ToUpperInvariant())) {
        throw ("the $GoldenSeed golden hash moved.`n  expected $($GoldenSha256.ToUpperInvariant())`n  observed $firstHash`n" +
               "If the algorithm, the policy or the seed handling changed on purpose, that is a version bump and this constant moves with it.")
    }

    Write-Host ''
    Write-Host "PACKAGED EXE SMOKE: PASS"
    Write-Host "  executable           : $exe"
    Write-Host "  seed                 : $($one.Report.seed)"
    Write-Host "  supported            : $($one.Report.supported)"
    Write-Host "  randomized           : $($one.Report.randomized)"
    Write-Host "  destinations moved   : $($one.Report.destinations_moved)"
    Write-Host "  skipped              : $($one.Report.skipped)"
    Write-Host "  output               : $firstRom"
    Write-Host "  output SHA-256       : $firstHash"
    Write-Host "  second run identical : $($firstHash -eq $secondHash)"
    Write-Host "  manifest written     : $(Test-Path $one.Report.manifest)"
    Write-Host "  source ROM unchanged : $($afterHash -eq $source)"
    Write-Host "  contract read back   : $($one.Report.policy) / v$($one.Report.version)"
    Write-Host ''
    Write-Host "GOKU GOLDEN v0.1.0 OUTPUT SHA-256: $firstHash"
}
finally {
    Pop-Location
}
