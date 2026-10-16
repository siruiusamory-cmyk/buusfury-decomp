# ENEMY-RANDOMIZER-EXE-001 - the packaged-executable smoke, plus the golden hash.
#
#   pwsh scripts/smoke-enemy-randomizer-packaged.ps1
#
# This drives the ACTUAL RELEASE EXECUTABLE - not a python script, not a pytest
# fixture, not the repository CLI. The frozen build is windowed and has no console,
# so it is asked for a machine-readable report through its own --smoke entry, which
# goes through the same window, the same verification, the same worker thread and
# the same boundary the Randomize button uses.
#
# It records the accepted golden output SHA-256 for the launch seed
# StreamBlind-0001 - the ticket's own regression seed, and the seed the randomised
# ROM merged to master was produced with - and proves a second run of the same seed
# is byte-identical, that the manifest and the spoiler both exist, and that the
# source ROM is untouched throughout.
#
# It also re-runs the same seed with the enemy-stat module switched off and checks
# that the result differs, which is the only way a packaged build can be shown to
# honour a module toggle rather than always running both.

[CmdletBinding()]
param(
    [string] $DistDir = 'dist',
    [string] $BuildName = 'Enemy-Randomizer',
    [string] $CanonicalRom = "roms/Dragon Ball Z - Buu's Fury (U).gba",
    [string] $WorkDir = 'build/enemy-randomizer-packaged',
    [string] $GoldenSeed = 'StreamBlind-0001',
    [string] $GoldenSha256 = '4d4cf624681803a227c26a44bc08b3c6b6cf71539c0a283a03fabd0561e7895f'
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/randomizer-release.ps1"

$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    # One file: the release is the executable itself, with nothing beside it.
    $exe = Join-Path $DistDir "$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "no packaged executable at $exe - run: pwsh scripts/build-enemy-randomizer.ps1 -Clean" }
    if (-not (Test-Path $CanonicalRom)) { throw "canonical ROM not found at $CanonicalRom" }

    $exe = (Resolve-Path $exe).Path
    $rom = (Resolve-Path $CanonicalRom).Path
    $work = Join-Path (Get-Location) $WorkDir
    if (Test-Path $work) { Remove-Item $work -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $work | Out-Null

    $source = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
    $beforeHash = (Get-FileHash $rom -Algorithm SHA256).Hash
    if ($beforeHash -ne $source) { throw "the canonical ROM is not canonical before the smoke: $beforeHash" }

    # --- run 1: the golden launch-seed run -------------------------------
    $firstRom = Join-Path $work "Buu's Fury - Enemy Randomized - $GoldenSeed.gba"
    $firstReport = Join-Path $work 'run1.json'
    $one = Invoke-RandomizerSmoke -Exe $exe -Rom $rom -OutputRom $firstRom `
        -ReportPath $firstReport -Seed $null

    if ($one.ExitCode -ne 0) { throw "packaged smoke run 1 exited $($one.ExitCode): $($one.Report.status)" }
    if (-not $one.Report.ok) { throw "packaged smoke run 1 reported failure: $($one.Report.status)" }
    if (-not (Test-Path $firstRom)) { throw "the packaged build reported success but wrote no ROM" }
    if (-not $one.Report.seed_is_launch_seed) {
        throw "the packaged build did not launch on the $GoldenSeed seed"
    }
    if ($one.Report.seed -ne $GoldenSeed) { throw "unexpected seed: $($one.Report.seed)" }
    # Joined before comparing: PowerShell's -ne over two arrays is an element-wise
    # filter, not an equality test, so `$a -ne $b` is true even when they match.
    if (($one.Report.modules -join ',') -ne 'enemy-placement,enemy-stat') {
        throw "the launch state did not enable both proven modules: $($one.Report.modules -join ', ')"
    }
    if ($one.Report.delivers_ticket_module_c -ne $false) {
        throw "the packaged build did not record delivers_ticket_module_c: false"
    }

    $firstHash = (Get-FileHash $firstRom -Algorithm SHA256).Hash
    if ($one.Report.output_sha256.ToUpperInvariant() -ne $firstHash) {
        throw "the reported hash is not the file that was written"
    }
    if (-not (Test-Path $one.Report.manifest)) { throw "the packaged build reported a manifest that does not exist" }
    if (-not (Test-Path $one.Report.spoiler_path)) { throw "the packaged build reported a spoiler that does not exist" }
    if (-not $one.Report.source_unchanged) { throw "the packaged build reports the source ROM changed" }

    # --- run 2: the same seed to a second path ---------------------------
    $secondRom = Join-Path $work "second-$GoldenSeed.gba"
    $secondReport = Join-Path $work 'run2.json'
    $two = Invoke-RandomizerSmoke -Exe $exe -Rom $rom -OutputRom $secondRom `
        -ReportPath $secondReport -Seed $GoldenSeed
    if ($two.ExitCode -ne 0) { throw "packaged smoke run 2 exited $($two.ExitCode)" }
    $secondHash = (Get-FileHash $secondRom -Algorithm SHA256).Hash
    if ($firstHash -ne $secondHash) {
        throw "two runs of the same seed differ: $firstHash vs $secondHash"
    }

    # --- run 3: one module off, through the real window ------------------
    $placementRom = Join-Path $work "placement-only-$GoldenSeed.gba"
    $placementReport = Join-Path $work 'run3.json'
    $three = Invoke-RandomizerSmoke -Exe $exe -Rom $rom -OutputRom $placementRom `
        -ReportPath $placementReport -Seed $GoldenSeed `
        -ExtraArguments '--without "enemy-stat"'
    if ($three.ExitCode -ne 0) { throw "packaged smoke run 3 exited $($three.ExitCode)" }
    if (($three.Report.modules -join ',') -ne 'enemy-placement') {
        throw "the packaged build did not honour --without: $($three.Report.modules -join ', ')"
    }
    $placementHash = (Get-FileHash $placementRom -Algorithm SHA256).Hash
    if ($placementHash -eq $firstHash) {
        throw "disabling the stat module did not change the output, so the toggle is not wired"
    }

    # --- the canonical ROM is still canonical ----------------------------
    $afterHash = (Get-FileHash $rom -Algorithm SHA256).Hash
    if ($afterHash -ne $source) { throw "the canonical ROM changed during the smoke: $afterHash" }

    # --- the recorded golden value ---------------------------------------
    if ($GoldenSha256 -and ($firstHash -ne $GoldenSha256.ToUpperInvariant())) {
        throw ("the $GoldenSeed golden hash moved.`n  expected $($GoldenSha256.ToUpperInvariant())`n  observed $firstHash`n" +
               "If the algorithm, a module version or the seed handling changed on purpose, that is a version bump and this constant moves with it.")
    }

    Write-Host ''
    Write-Host "PACKAGED EXE SMOKE: PASS"
    Write-Host "  executable           : $exe"
    Write-Host "  seed                 : $($one.Report.seed)"
    Write-Host "  modules              : $($one.Report.modules -join ', ')"
    Write-Host "  changed bytes        : $($one.Report.changed_byte_count)"
    Write-Host "  module C delivered   : $($one.Report.delivers_ticket_module_c)"
    Write-Host "  output               : $firstRom"
    Write-Host "  output SHA-256       : $firstHash"
    Write-Host "  second run identical : $($firstHash -eq $secondHash)"
    Write-Host "  manifest written     : $(Test-Path $one.Report.manifest)"
    Write-Host "  spoiler written      : $(Test-Path $one.Report.spoiler_path)"
    Write-Host "  placement-only differ: $($placementHash -ne $firstHash)"
    Write-Host "  source ROM unchanged : $($afterHash -eq $source)"
    Write-Host "  contract read back   : $($one.Report.tool) / v$($one.Report.version)"
    Write-Host ''
    Write-Host "STREAMBLIND-0001 GOLDEN OUTPUT SHA-256: $firstHash"
}
finally {
    Pop-Location
}
