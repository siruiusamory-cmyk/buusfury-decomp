<#
.SYNOPSIS
Capture the SAME frame from the retail ROM and the authored derivative.

.WARNING - THIS INSTRUMENT IS NOT VALID CAPABILITY EVIDENCE.
It captures straight after a state load, and a state restores the
ALREADY-ASSEMBLED background, so the engine never re-reads the map from ROM. Two
different ROMs captured this way produce byte-identical VRAM and screenblocks -
measured. Retained only as the negative that established the rule and as a
demonstration of that failure.

For a valid proof use tools/runtime/capture_tilepaint001_afterrebuild.ps1, which
refuses to capture unless it has observed a real leave-and-return rebuild.

.DESCRIPTION
MAP-TILE-PAINT-001's question was whether the authored chunk cell is what the
engine displays. Comparing two screenshots taken after a human moved around
cannot answer it, because the camera moves too - measured: the change covered 76%
of the viewport and was dominated by scrolling.

This script attempted to remove the camera variable by using one savestate, which
restores the same camera and player position every time:

  1. launch mGBA on the RETAIL image, load the state, let it settle, capture;
  2. close it, launch mGBA on the DERIVATIVE image, load the SAME state, let it
     settle, capture.

That failed for the reason above: both captures are the same frame of the same map
with only the ROM differing, and they come out identical because the STATE, not
the ROM, supplied the background. See the evidence record.

It launches and exits; it owns no wait loop beyond the settle. Read-only with
respect to the ROMs: both are opened by mGBA, never written; the state is copied
into the run directory and the copy is what mGBA loads.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RetailRom,
    [Parameter(Mandatory = $true)][string]$AuthoredRom,
    [Parameter(Mandatory = $true)][string]$StatePath,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [string]$MGBPath,
    [string]$RetailSha256 = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E',
    [string]$AuthoredSha256,
    [string]$LuaPath = 'tools\runtime\tilepaint001_live_screenblock.lua',
    [string]$RequiredMGBVersion = '0.11',
    [int]$UiSettleSeconds = 12,
    [int]$AfterLoadSeconds = 6
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path

function Resolve-Required([string]$Path, [string]$What) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $root $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw "$What is missing: $candidate" }
    return (Resolve-Path -LiteralPath $candidate).Path
}

if (-not $MGBPath) {
    $MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
}
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua observer'
$retail = Resolve-Required $RetailRom 'retail ROM'
$authored = Resolve-Required $AuthoredRom 'authored ROM'

$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion"
}

if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
$workingState = Join-Path $OutDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState -Force

function Assert-Rom([string]$path, [string]$expected, [string]$what) {
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
    if ($expected -and $hash -ne $expected.Trim().ToUpperInvariant()) {
        throw "$what identity mismatch: expected $expected, found $hash"
    }
    return $hash
}

function Capture-One([string]$romPath, [string]$label, [string]$sha) {
    if (Get-Process mGBA -ErrorAction SilentlyContinue) {
        throw 'an mGBA process is already running; refusing to race it'
    }
    $runDir = Join-Path $OutDir $label
    if (Test-Path -LiteralPath $runDir) { Remove-Item -LiteralPath $runDir -Recurse -Force }
    New-Item -ItemType Directory -Path $runDir -Force | Out-Null

    $marker = Join-Path $runDir 'marker.txt'
    $ready = Join-Path $runDir 'lua-ready.txt'
    $romHash = Assert-Rom $romPath $sha "$label ROM"

    # One mechanism for every launcher: mGBA loads the state with -t and runs the
    # observer with --script, so no Scripting window is opened, nothing takes the
    # operator window, and the identity gates live with the flag that needs them.
    . (Join-Path $PSScriptRoot 'mgba_session.ps1')
    $process = Start-MgbaSession -MGBPath $resolvedMGB -RomPath $romPath `
        -LuaPath $resolvedLua -ReadyPath $ready -MarkerPath $marker -RunDir $runDir `
        -RequiredMGBVersion $RequiredMGBVersion -ExpectedRomSha256 $sha `
        -StatePath $workingState

    Start-Sleep -Seconds $AfterLoadSeconds
    & powershell -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $PSScriptRoot 'capture_mgba_window.ps1') `
        -OutPath (Join-Path $runDir "$label.png") -TitleMatch 'mGBA -'
    if ($LASTEXITCODE -ne 0) { throw "$label : capture failed" }

    $manifest = Get-Content -LiteralPath (Join-Path $runDir 'runtime_manifest.csv') -ErrorAction SilentlyContinue
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 4

    return [ordered]@{
        label    = $label
        rom      = $romPath
        rom_hash = $romHash
        run_dir  = $runDir
        capture  = (Join-Path $runDir "$label.png")
        manifest = ($manifest -join "`n")
    }
}

$retailInfo = Capture-One $retail 'retail' $RetailSha256
$authoredInfo = Capture-One $authored 'authored' $AuthoredSha256

@{
    state_sha256 = $stateHash
    mgba_version = $mgbVersion
    retail       = $retailInfo
    authored     = $authoredInfo
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutDir 'pair.json') -Encoding utf8

Write-Output 'PAIR CAPTURED'
Write-Output "  retail   : $($retailInfo.capture)"
Write-Output "  authored : $($authoredInfo.capture)"
Write-Output "  state    : $stateHash"
