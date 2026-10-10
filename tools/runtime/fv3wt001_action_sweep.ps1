# FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3: the action lottery sweep.
#
# WHY. The enemy's swing cadence is bounded by his swing animation, and the only data lever into
# that animation is which action row the swing's own SET pushes (retail 206). Neither the chance
# leaf nor the post-attack wait moved the measured rate, so the rows have to be tried and the
# cadence measured. This runs the whole lottery without the owner: for each candidate action row
# it builds an image, launches the stand-still driver (which loads the read-only observer), lets
# the fight run, stops the emulator, and reads the swing count out of the run directory.
#
# NOT EVIDENCE ABOUT THE PLAYER. The driver's key presses are stimulus only. Every number this
# reports comes from the observer's breakpoint on the game's own spawn leaf.
#
# Usage: pwsh -File tools\runtime\fv3wt001_action_sweep.ps1 -Actions 204,205,207,208,209 -Seconds 75

param(
    [string]$Actions = '204,205,207,208,209',
    [int]$Seconds = 75,
    [string]$Base = 'build\fv3wt001\release3\v3-bosses-l-base.gba',
    [string]$BaseSha = '8849726cbd0eff849aead8a4b1b78c70ed9b3310a45af786eb6ece15d8d3071d',
    [int]$RomSize = 10146136
)

$candidates = @($Actions -split ',' | ForEach-Object { [int]$_.Trim() })

$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
Set-Location $root

$env:FV3WT001_OBSERVER = (Join-Path $root 'tools\runtime\fv3wt001_bossfight_watch.lua')
$mgba = 'C:\Dev\log1-remake\build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
$state = Join-Path $root 'build\friendv3-coldboot\fv3wt001-boss-olibu2\friendv3.ss1'

$results = @()
foreach ($action in $candidates) {
    $out = Join-Path $root "build\fv3wt001\release3\v3-bosses-action$action.gba"
    $manifest = Join-Path $root "build\fv3wt001\release3\v3-bosses-action$action.manifest.json"
    Write-Host "=== action $action ==="
    python tools\research\apply_friend_v3_behaviour_profile.py `
        --image $Base --expect-sha256 $BaseSha --out $out --manifest $manifest `
        --gate-radius 22500 --attack-radius 22500 --attack-percent 50 --attack-first `
        --attack-action $action --record 85 --record 45 | Select-Object -Last 1
    if ($LASTEXITCODE -ne 0) { Write-Host "  build refused, skipping"; continue }

    $sha = (Get-FileHash $out -Algorithm SHA256).Hash
    $label = "fv3wt001-action$action"
    $run = Join-Path $root "build\toolkit031\$label"
    if (Test-Path $run) { Remove-Item $run -Recurse -Force }

    $existing = @(Get-Process mGBA -ErrorAction SilentlyContinue)
    if ($existing.Count -gt 0) { Write-Host "  an emulator is already running, skipping"; continue }

    & powershell -NoProfile -ExecutionPolicy Bypass -File tools\runtime\start_toolkit031_session.ps1 `
        -RomPath $out -RomSha256 $sha -StatePath $state -Label $label `
        -LuaPath tools\runtime\fv3wt001_stand_still.lua -MGBPath $mgba -ExpectedRomSize $RomSize |
        Select-Object -Last 2

    Start-Sleep -Seconds $Seconds
    Get-Process mGBA -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2

    $swings = 0
    $swing_file = Join-Path $run 'swings.csv'
    if (Test-Path $swing_file) { $swings = (@(Get-Content $swing_file).Count - 1) }
    $frame_first = 0; $frame_last = 0
    if ($swings -gt 0) {
        $rows = @(Get-Content $swing_file | Select-Object -Skip 1)
        $frame_first = [int](($rows[0] -split ',')[1])
        $frame_last = [int](($rows[-1] -split ',')[1])
    }
    $drive = Join-Path $run 'drive.txt'
    $span = if ($frame_last -gt $frame_first) { $frame_last - $frame_first } else { 0 }
    $per = if ($span -gt 0) { [math]::Round($span / $swings, 1) } else { 0 }
    $results += [pscustomobject]@{
        action = $action; swings = $swings; first = $frame_first; last = $frame_last
        frames_per_swing = $per; drive = (Test-Path $drive); sha = $sha.Substring(0, 12)
    }
}

Write-Host ''
Write-Host 'action  swings  swing span  frames/swing'
foreach ($r in $results) {
    '{0,6}  {1,6}  {2,5}..{3,-5}  {4}' -f $r.action, $r.swings, $r.first, $r.last, $r.frames_per_swing
}
$results | ConvertTo-Json | Set-Content (Join-Path $root 'build\fv3wt001\release3\action-sweep.json')
