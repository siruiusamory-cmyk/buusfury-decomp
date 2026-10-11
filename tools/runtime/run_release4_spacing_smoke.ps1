<#
.SYNOPSIS
A bounded, visible, self-exiting cold-boot smoke run on a COPY of a battery save.

.DESCRIPTION
The interactive launchers start mGBA and exit, and a human ends the session by
closing the window. That is the right shape when a human is playing, and the wrong
shape for an unattended run: nothing would close the window. This runner starts the
same instrumented session through `mgba_session.ps1` (which keeps the emulator
version gate, the exact ROM digest gate and the observer allowlist), copies the ROM
and the battery save into a fresh run directory, hands the observer a bounded input
driver as its post-injection command, waits a fixed number of seconds, stops mGBA
itself, and summarises what the run produced.

What it refuses: an mGBA that is not the required build, a ROM whose digest or size
is not the exact pair named, a missing battery save, a running mGBA (one at a time),
or a run directory that already exists.

The window is visible and is never minimised: the owner's dashboard docks it.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RomPath,
    [Parameter(Mandatory = $true)][string]$RomSha256,
    [Parameter(Mandatory = $true)][string]$SavePath,
    [Parameter(Mandatory = $true)][string]$Label,
    [ValidateRange(10, 900)][int]$Seconds = 75,
    [string]$LuaPath = 'tools\runtime\friendv3_coldboot_probe.lua',
    [string]$DriverPath = 'tools\runtime\boost001_input_driver.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11',
    [string]$Root = 'build\release4-spacing'
)

$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path

function Resolve-Required([string]$Path, [string]$What) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $workspace $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw "$What is missing: $candidate" }
    return (Resolve-Path -LiteralPath $candidate).Path
}

$resolvedRom = Resolve-Required $RomPath 'ROM'
$resolvedSave = Resolve-Required $SavePath 'Battery save'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$resolvedDriver = Resolve-Required $DriverPath 'Input driver'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}
$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') { throw 'RomSha256 must be a full 64-character SHA-256 digest' }
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romHash -ne $expected) {
    throw "ROM identity mismatch; run refused. Expected $expected, found $romHash"
}

$existing = Get-Process mGBA -ErrorAction SilentlyContinue
if ($existing) { throw "An mGBA process is already running (pid $($existing.Id)); refusing to race it." }

$runDir = Join-Path $workspace (Join-Path $Root $Label)
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$romCopy = Join-Path $runDir 'image.gba'
$saveCopy = Join-Path $runDir 'image.sav'
Copy-Item -LiteralPath $resolvedRom -Destination $romCopy
Copy-Item -LiteralPath $resolvedSave -Destination $saveCopy
$saveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedSave).Hash
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $saveCopy).Hash -ne $saveHash) {
    throw 'Battery save copy hash mismatch'
}

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$csv = Join-Path $runDir 'coldboot.csv'
$env:TOOLKIT031_OUT = $csv
$env:DIALOGUE_ROM_SIZE = $romInfo.Length

. (Join-Path $PSScriptRoot 'mgba_session.ps1')
$process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $romCopy -LuaPath $resolvedLua `
    -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
    -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $expected `
    -PostCommand ('dofile([[{0}]])' -f ([System.IO.Path]::GetFullPath($resolvedDriver) -replace '\\', '/'))

Write-Output 'SESSION LIVE'
Write-Output "  mGBA pid   : $($process.Id)"
Write-Output "  run dir    : $runDir"
Write-Output "  rom        : $romHash"
Write-Output "  save       : $saveHash"
Write-Output "  bounded to : $Seconds seconds"

Start-Sleep -Seconds $Seconds
$process.Refresh()
$exited = $process.HasExited
if (-not $exited) { Stop-Process -Id $process.Id -Force }
$afterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $romCopy).Hash
if ($afterHash -ne $expected) { throw "The ROM copy changed during the run: $afterHash" }

$shots = @(Get-ChildItem -LiteralPath $runDir -Filter 'shot_*.png' -ErrorAction SilentlyContinue |
    Sort-Object Name)
$shotHashes = @($shots | ForEach-Object { (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash })
$distinct = @($shotHashes | Select-Object -Unique)
# The observer writes two row shapes into one CSV: `frame,pc,copier,rom_size` beats
# and `copy,N,registers,...` rows with a different column count. Import-Csv parses
# the copy rows into the beat header and produces nonsense, so the counts are taken
# from the raw lines.
$lines = @(if (Test-Path -LiteralPath $csv) { Get-Content -LiteralPath $csv } else { @() })
$beatRows = @($lines | Where-Object { $_ -match '^\d+,' })
$copierRows = @($lines | Where-Object { $_ -match '^copy,' })
$lastCopier = 0
foreach ($line in $beatRows) {
    $fields = $line.Split(',')
    if ($fields.Count -ge 3 -and $fields[2] -match '^\d+$') {
        $value = [int]$fields[2]
        if ($value -gt $lastCopier) { $lastCopier = $value }
    }
}

$summary = [ordered]@{
    label            = $Label
    mode             = 'bounded cold boot, battery save copy, observer + bounded input driver'
    rom_path         = $resolvedRom
    rom_sha256       = $romHash
    rom_bytes        = $romInfo.Length
    rom_unchanged    = ($afterHash -eq $expected)
    save_path        = $resolvedSave
    save_sha256      = $saveHash
    mgba_path        = $resolvedMGB
    mgba_version     = $mgbVersion
    mgba_pid         = $process.Id
    bounded_seconds  = $Seconds
    exited_by_itself = $exited
    screenshots      = $shots.Count
    distinct_screenshots = $distinct.Count
    csv_rows         = $lines.Count
    copier_rows      = $copierRows.Count
    copier_hits      = $lastCopier
    marker           = if (Test-Path -LiteralPath $marker) { (Get-Content -Raw -LiteralPath $marker).Trim() } else { $null }
    run_dir          = $runDir
}
$summary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $runDir 'summary.json') -Encoding ascii
$summary | ConvertTo-Json -Depth 4

Write-Output ''
Write-Output "screenshots $($shots.Count), distinct $($distinct.Count), copier rows $($copierRows.Count)"
Write-Output "run dir     $runDir"
