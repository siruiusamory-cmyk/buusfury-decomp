<#
.SYNOPSIS
Run one bounded Checkpoint D observation on a GENERATED (expanded) ROM.

.DESCRIPTION
ROM-CAPACITY-AND-ALLOCATION-001 Checkpoint D needs the retail engine observed
consuming a resource that the PRODUCTION allocator placed above canonical EOF.
The generated image is therefore not the canonical ROM, and the tracked
`run_toolkit031_watch.ps1` refuses anything but an 8 MiB canonical image. This
wrapper drives the same proven injection path for a generated image, and keeps
every guarantee the canonical path has:

  * the CALLER names the generated image's exact SHA-256 and size; there is no
    "accept anything" path and no pattern match;
  * the CANONICAL ROM's digest is verified before and after, so a run can never
    be evidence about a modified original;
  * the savestate is hashed and copied into a unique ignored run directory, and
    the copy is what is loaded;
  * an orphan mGBA process is refused rather than raced;
  * Lua reaches the core through `tools/runtime/inject_mgba_lua.ps1`, which is
    allowlisted and PID-scoped;
  * only the PID this script started is stopped.

It never writes emulated memory and never patches a ROM. The probe it injects
does write INPUT, and says so in its own header.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RomPath,
    [Parameter(Mandatory = $true)]
    [string]$RomSha256,
    [Parameter(Mandatory = $true)]
    [int]$RomSize,
    [Parameter(Mandatory = $true)]
    [string]$StatePath,
    [Parameter(Mandatory = $true)]
    [string]$Label,
    # The allocator's chosen ROM address for the relocated resource, taken from
    # the derivative's own provenance by the caller. The probe asserts it.
    [Parameter(Mandatory = $true)]
    [string]$ExpectedPointer,
    [string]$LuaPath = 'tools\runtime\capacity001_expanded_dialogue_probe.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11',
    [int]$RunSeconds = 240
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$canonicalSha256 = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
$canonicalSize = 8388608
$canonicalRom = Join-Path $root 'roms\Dragon Ball Z - Buu''s Fury (U).gba'

function Resolve-Required([string]$Path, [string]$Label) {
    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path $root $Path }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        throw "$Label is missing: $candidate"
    }
    return (Resolve-Path -LiteralPath $candidate).Path
}

$resolvedRom = Resolve-Required $RomPath 'Generated ROM'
$resolvedState = Resolve-Required $StatePath 'Savestate'
$resolvedLua = Resolve-Required $LuaPath 'Lua probe'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'

$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}

# The generated image's own identity, named exactly by the caller.
$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') {
    throw 'RomSha256 must be a full 64-character SHA-256 hex digest'
}
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romInfo.Length -ne $RomSize -or $romHashBefore -ne $expected) {
    throw "Generated ROM identity mismatch; run refused. Expected $expected size $RomSize, found $romHashBefore size $($romInfo.Length)"
}
if ($RomSize -le $canonicalSize) {
    throw 'This runner is for an EXPANDED image; the generated size must exceed canonical EOF'
}

# The canonical ROM is the thing that must not move. Verify it, then verify it
# again at the end: a run that modified the verified input is not evidence.
if (-not (Test-Path -LiteralPath $canonicalRom -PathType Leaf)) {
    throw "Canonical ROM is missing: $canonicalRom"
}
$canonicalBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $canonicalRom).Hash
if ($canonicalBefore -ne $canonicalSha256) {
    throw "Canonical ROM identity mismatch before the run: $canonicalBefore"
}

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; refusing to race it. Stop it first.'
}

$runDir = Join-Path $root ("build\capacity-checkpoint-d\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir"
}
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
$workingState = Join-Path $runDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingState).Hash -ne $stateHash) {
    throw 'Savestate copy hash mismatch'
}

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$csv = Join-Path $runDir 'capacity001-dialogue.csv'
$env:CAPACITY001_OUT = $csv
$env:CAPACITY001_EXPECTED_POINTER = $ExpectedPointer

[ordered]@{
    label            = $Label
    rom_path         = $resolvedRom
    rom_sha256       = $romHashBefore
    rom_size         = $romInfo.Length
    canonical_sha256 = $canonicalBefore
    state_path       = $resolvedState
    state_sha256     = $stateHash
    lua_path         = $resolvedLua
    mgba_path        = $resolvedMGB
    mgba_version     = $mgbVersion
    expected_pointer = $ExpectedPointer
    run_seconds      = $RunSeconds
} | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'inputs.json') -Encoding utf8

$process = $null
try {
    $process = Start-Process -FilePath $resolvedMGB -ArgumentList @('"' + $resolvedRom + '"') -PassThru
    Start-Sleep -Seconds 8

    & powershell -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $root 'tools\runtime\inject_mgba_lua.ps1') `
        -TargetProcessId $process.Id -LuaPath $resolvedLua `
        -ReadyPath $ready -MarkerPath $marker
    if ($LASTEXITCODE -ne 0) { throw 'Lua injection failed' }

    # Load the state only AFTER the probe is attached, so its breakpoints are
    # already armed when the fixture resumes (the skill's section 5 ordering).
    #
    # The load is retried once. `toolkit031_load_state.ps1` confirms the load from
    # the Scripting log pane rather than assuming the Run click worked, and that
    # confirmation can race the Run helper when it runs seconds after injection:
    # measured here as "Savestate load was not confirmed" on one attempt and a
    # confirmed load on the next from the same inputs. Retrying is honest - a
    # failed confirmation means no load happened, so a retry cannot double-apply.
    $loaded = $false
    for ($attempt = 1; $attempt -le 2 -and -not $loaded; $attempt++) {
        & powershell -NoProfile -ExecutionPolicy Bypass `
            -File (Join-Path $PSScriptRoot 'toolkit031_load_state.ps1') `
            -TargetProcessId $process.Id -StatePath $workingState
        if ($LASTEXITCODE -eq 0) {
            $loaded = $true
        } else {
            Start-Sleep -Seconds 3
        }
    }
    if (-not $loaded) { throw 'Savestate load failed after two attempts' }

    # The probe holds its input schedule until this appears, because the load goes
    # through mGBA's Scripting prompt and takes seconds of wall clock while the
    # core keeps running. Without the signal a schedule counted from injection
    # time photographs the boot title and reports a false negative.
    Set-Content -LiteralPath (Join-Path $runDir 'state-loaded.txt') -Value 'loaded' -Encoding utf8

    # The probe is frame-scheduled and bounded, so the marker arrives on its own;
    # -RunSeconds is a backstop, not the normal ending.
    #
    # The marker's CONTENT is the completion signal, not its existence. The probe
    # writes "armed" as soon as it attaches, and an earlier version of this loop
    # broke on any marker at all - which stopped mGBA about two seconds after the
    # state load, before the observation schedule could run, and produced an
    # empty CSV that looked like a negative result.
    $deadline = (Get-Date).AddSeconds($RunSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $marker) {
            $note = (Get-Content -LiteralPath $marker -Raw -ErrorAction SilentlyContinue)
            if ($note -and $note.Trim() -and $note.Trim() -ne 'armed') {
                Start-Sleep -Seconds 2      # let the final rows flush
                break
            }
        }
        if ($process.HasExited) { break }
        Start-Sleep -Milliseconds 500
    }
} finally {
    if ($process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
    Remove-Item Env:\CAPACITY001_OUT -ErrorAction SilentlyContinue
    Remove-Item Env:\CAPACITY001_EXPECTED_POINTER -ErrorAction SilentlyContinue
}

$romHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romHashAfter -ne $romHashBefore) {
    throw "Generated image changed during the run: $romHashBefore -> $romHashAfter"
}
$canonicalAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $canonicalRom).Hash
if ($canonicalAfter -ne $canonicalBefore) {
    throw "Canonical ROM changed during the run: $canonicalBefore -> $canonicalAfter"
}

Write-Output "run directory: $runDir"
if (Test-Path -LiteralPath $csv) {
    $rows = Get-Content -LiteralPath $csv
    Write-Output ("rows: " + $rows.Count)
    Write-Output ("CONSUMER rows: " + (@($rows | Where-Object { $_ -like 'CONSUMER,*' }).Count))
    Write-Output ("LIVENESS rows: " + (@($rows | Where-Object { $_ -like 'LIVENESS,*' }).Count))
    $target = @($rows | Where-Object { $_ -like '*target expanded selector consumed*' })
    Write-Output ("target rows: " + $target.Count)
    $target | ForEach-Object { Write-Output $_ }
    Write-Output ("RESULT: " + (@($rows | Where-Object { $_ -like 'RESULT,*' }) -join ' '))
} else {
    Write-Output 'no probe output'
}
Write-Output ("marker: " + (Get-Content -LiteralPath $marker -ErrorAction SilentlyContinue))
Write-Output 'canonical ROM unchanged: YES'
