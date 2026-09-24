<#
.SYNOPSIS
Start a HUMAN check of the production above-EOF dialogue relocation, then exit.

.DESCRIPTION
ROM-CAPACITY-AND-ALLOCATION-001 Checkpoint D. The retail engine has to be seen
consuming the resource the production allocator placed above canonical EOF, and a
conversation is the natural trigger. Scripting that trigger is fragile (the
reload path and the input schedule have to line up to the frame); playing it is
not, and this repository already has the convention: a human-session launcher
STARTS the emulator, arms the observer, and RETURNS.

What this script does NOT do, deliberately, and what past bugs make mandatory:

  * it owns no wait loop and no cleanup -- the operator ends the session;
  * it never stops mGBA, and it is never wrapped in a background job, because two
    separate bugs killed live sessions that way (a deadline that counted setup
    time, and a `finally` block firing when the job hosting it was torn down);
  * it writes nothing to the ROM.

What it DOES verify before arming anything: the generated image's exact digest and
size (named by the caller, never a pattern), the canonical ROM's digest, that no
orphan mGBA is running, and the emulator's version from the binary rather than its
path -- the scripted-breakpoint API this needs only exists in the 0.11 dev build.

Evidence lands in `build/capacity-checkpoint-d/<label>/` and is collected
afterwards by `finish_capacity001_expansion_session.ps1`.
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
    [string]$Label,
    # The allocator's chosen ROM address, from the derivative's own provenance.
    [Parameter(Mandatory = $true)]
    [string]$ExpectedPointer,
    # The private deterministic fixture. Loading it is what puts the operator in
    # front of the NPC rather than at the title screen, and the load happens AFTER
    # injection for the ordering reason the runtime skill states (section 5).
    [Parameter(Mandatory = $true)]
    [string]$StatePath,
    [string]$LuaPath = 'tools\runtime\capacity001_expanded_dialogue_probe.lua',
    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe',
    [string]$RequiredMGBVersion = '0.11'
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
$resolvedLua = Resolve-Required $LuaPath 'Lua probe'
$resolvedMGB = Resolve-Required $MGBPath 'mGBA'
$resolvedState = Resolve-Required $StatePath 'Savestate'

$mgbVersion = (Get-Item -LiteralPath $resolvedMGB).VersionInfo.FileVersion
if (-not $mgbVersion.StartsWith($RequiredMGBVersion)) {
    throw "mGBA version mismatch: required $RequiredMGBVersion, found $mgbVersion at $resolvedMGB"
}

$expected = $RomSha256.Trim().ToUpperInvariant()
if ($expected -notmatch '^[0-9A-F]{64}$') {
    throw 'RomSha256 must be a full 64-character SHA-256 hex digest'
}
$romInfo = Get-Item -LiteralPath $resolvedRom
$romHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedRom).Hash
if ($romInfo.Length -ne $RomSize -or $romHashBefore -ne $expected) {
    throw "Generated ROM identity mismatch; session refused. Expected $expected size $RomSize, found $romHashBefore size $($romInfo.Length)"
}
if ($RomSize -le $canonicalSize) {
    throw 'This session is for an EXPANDED image; the generated size must exceed canonical EOF'
}
if (-not (Test-Path -LiteralPath $canonicalRom -PathType Leaf)) {
    throw "Canonical ROM is missing: $canonicalRom"
}
$canonicalBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $canonicalRom).Hash
if ($canonicalBefore -ne $canonicalSha256) {
    throw "Canonical ROM identity mismatch before the session: $canonicalBefore"
}

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    throw 'An mGBA process is already running; refusing to race it. Close it first.'
}

$runDir = Join-Path $root ("build\capacity-checkpoint-d\" + $Label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir"
}
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$marker = Join-Path $runDir 'marker.txt'
$ready = Join-Path $runDir 'lua-ready.txt'
$csv = Join-Path $runDir 'capacity001-dialogue.csv'
$env:CAPACITY001_OUT = $csv
$env:CAPACITY001_EXPECTED_POINTER = $ExpectedPointer
$env:CAPACITY001_MODE = 'human'

$stateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedState).Hash
$workingState = Join-Path $runDir 'working-state.ss1'
Copy-Item -LiteralPath $resolvedState -Destination $workingState
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $workingState).Hash -ne $stateHash) {
    throw 'Savestate copy hash mismatch'
}

[ordered]@{
    label            = $Label
    mode             = 'human'
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
} | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'session.json') -Encoding utf8

# Start the emulator on the generated image and return. The observer is armed
# through the tracked, allowlisted injector; nothing here waits for the session.
$process = Start-Process -FilePath $resolvedMGB -ArgumentList @('"' + $resolvedRom + '"') -PassThru
Start-Sleep -Seconds 8

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $root 'tools\runtime\inject_mgba_lua.ps1') `
    -TargetProcessId $process.Id -LuaPath $resolvedLua `
    -ReadyPath $ready -MarkerPath $marker
if ($LASTEXITCODE -ne 0) { throw 'Lua injection failed' }

# Load the fixture AFTER the probe is armed, so its breakpoints are installed
# before the resumed state constructs and speaks. Retried once: the tracked
# loader confirms the load from the Scripting log pane, and that confirmation can
# race the Run helper when it runs seconds after injection.
$loaded = $false
for ($attempt = 1; $attempt -le 2 -and -not $loaded; $attempt++) {
    & powershell -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $root 'tools\runtime\toolkit031_load_state.ps1') `
        -TargetProcessId $process.Id -StatePath $workingState
    if ($LASTEXITCODE -eq 0) { $loaded = $true } else { Start-Sleep -Seconds 3 }
}
if (-not $loaded) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw 'Savestate load failed after two attempts'
}

Remove-Item Env:\CAPACITY001_OUT -ErrorAction SilentlyContinue
Remove-Item Env:\CAPACITY001_EXPECTED_POINTER -ErrorAction SilentlyContinue
Remove-Item Env:\CAPACITY001_MODE -ErrorAction SilentlyContinue

$canonicalAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $canonicalRom).Hash
if ($canonicalAfter -ne $canonicalBefore) {
    throw "Canonical ROM changed while arming the session: $canonicalBefore -> $canonicalAfter"
}

Write-Output 'CAPACITY-001 expanded-dialogue session is ARMED and live.'
Write-Output ''
Write-Output ("  mGBA PID : " + $process.Id)
Write-Output ("  ROM      : " + $resolvedRom)
Write-Output ("  SHA-256  : " + $romHashBefore)
Write-Output ("  watching : selector table " + '0x087B5B64' + ", expecting selector 1 -> " + $ExpectedPointer)
Write-Output ("  evidence : " + $runDir)
Write-Output ''
Write-Output 'Play to the greeting that says "Good luck, Goku!" in retail. With the'
Write-Output 'relocated resource in use it reads "Nice work, Goku!". The probe records'
Write-Output 'every compressed-dialogue handle the engine consumes and screenshots each'
Write-Output 'time the target selector is consumed, so a run that never reaches the NPC'
Write-Output 'reports no target row rather than a false negative.'
Write-Output ''
Write-Output 'Close the mGBA window when finished; then run:'
Write-Output ("  tools/runtime/finish_capacity001_expansion_session.ps1 -Label " + $Label)
