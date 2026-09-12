<#
.SYNOPSIS
Stage one TEXT-HANDLE-001 capture and RETURN, leaving mGBA running for play.

.DESCRIPTION
TEXT-HANDLE-001 asked where the packed compressed-text handle consumed from
runtime object +0x04 actually comes from. The experiment was atlas-guided LIVE
OBSERVATION first: catch the object at a consumer, arm a write watch on its
+0x04 in the same callback, and let the operator trigger the same dialogue
repeatedly.

RESULT, and the reason this framing changed: there is no producer to find. The
pointer the consumer receives points into a ROM-RESIDENT record, and the packed
handle is already stored at that record's +0x04. Nothing writes the field at
runtime, so the write watch correctly never armed -- its guard requires an
EWRAM address. The persistent ROM record is the durable owner.

The write-watch channel is retained deliberately. It is what distinguishes "the
field is ROM-resident" from "a write exists and was missed", and a capture on a
different text path still needs that discrimination.

This wrapper exists for the same reason stage_toolkit034_trial.ps1 does. Which
capture a JSONL belongs to is otherwise recoverable only from a directory name,
and several captures of the SAME line are the point -- repeatability is the
evidence, so each run has to be labelled and its intent recorded beside it.

It delegates to start_toolkit031_session.ps1, which owns emulator identity, ROM
identity, orphan refusal, injection and state load in the proven order. That
script is NOT modified: the observer takes its output path from the
environment, and a variable set here is inherited by the mGBA process it
launches.

It holds no wait loop and no cleanup, because nothing may own the emulator's
lifetime during human play. Two prior sessions were destroyed by exactly that.
The operator ends the run by closing the mGBA window; evidence is collected
afterwards by finish_toolkit031_session.ps1.

Read-only: no emulated memory is written and no input is driven.

.PARAMETER Capture
  1..N  A repeat of the SAME target line. The ticket requires at least three
        captures of one dialogue so that object address, writer PC and raw
        handle can be classified as stable or transient.

.PARAMETER Contrast
  Switch. Marks this run as the ONE contrast capture: a DIFFERENT compressed
  text message from the same system, used only to discriminate a constant or
  global handle from real per-message selection. Not a corpus; one is enough.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass `
    -File tools\runtime\stage_text_handle_001.ps1 -Capture 1
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 99)]
    [int]$Capture,

    [switch]$Contrast,

    [string]$Suffix,

    # Canonical Buu's Fury. Read-only, never patched, verified before and after.
    [string]$RomPath = 'roms\Dragon Ball Z - Buu''s Fury (U).gba',

    [string]$RomSha256 = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E',

    [string]$StatePath = 'roms\Dragon Ball Z - Buu''s Fury (U).ss1',

    [string]$LuaPath = 'tools\runtime\text_handle_001_producer_watch.lua',

    [string]$MGBPath = 'build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path

$target = if ($Contrast) {
    'CONTRAST: trigger a DIFFERENT compressed-text message from the same system'
} else {
    'TARGET: trigger the "Good luck, Goku!" line'
}

$lookingFor = @(
    'CONSUMER      expected: object latched from r1 at 0x08012230 or 0x080122B4',
    '              (verified statically: 0x08012232 mov r5,r1 / 0x080122BA mov r4,r1)',
    'WATCH-ARMED   expected: a write watch installed on that object +0x04',
    'FIELD-WRITE   THE TARGET: writer PC, raw u32, old value, LR, SP, r0-r12,',
    '              stack window and the instruction halfwords around the writer',
    'LIVENESS      installation control only. The shared interpreter at',
    '              0x08004038 is KNOWN to fire rarely, so a low count proves',
    '              breakpoint installation and nothing more.',
    '',
    'For the target line the decoded handle resolves to container selector 1',
    '= 0x087A04F0, decoded start 0x132, decoded length 0x20. MEASURED: the',
    'record start EQUALS 0x132 and the length is exactly the 16-character',
    'phrase, so here the record boundary IS the phrase. That was not assumed',
    'in advance and does not generalise -- another line may sit mid-record.',
    '',
    'READING A NEGATIVE: a silent CONSUMER channel means nothing on its own.',
    'Silent CONSUMER + firing LIVENESS is a real negative. Silent + silent is',
    'an unproven instrument and must be reported as such, never as absence.'
)

if (-not $Suffix) { $Suffix = Get-Date -Format 'yyyyMMdd-HHmm' }
$kind = if ($Contrast) { 'contrast' } else { 'target' }
$label = "text-handle-001-$kind-$($Capture.ToString('00'))-$Suffix"

$runDir = Join-Path $root ('build\toolkit031\' + $label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists, refusing to overwrite evidence: $runDir"
}

Write-Output "TEXT-HANDLE-001 capture $Capture ($kind)"
Write-Output "  $target"
Write-Output "  label : $label"
Write-Output ''
Write-Output '  what this capture is looking for:'
foreach ($line in $lookingFor) { Write-Output "    $line" }
Write-Output ''

# The observer reads its output path from the environment, and the mGBA process
# started by the delegate inherits this. Setting it here is what lets the shared
# launcher stay unmodified.
$evidence = Join-Path $runDir 'text-handle-001.jsonl'
$env:TEXTHANDLE001_OUT = $evidence

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'start_toolkit031_session.ps1') `
    -RomPath $RomPath -RomSha256 $RomSha256 -StatePath $StatePath `
    -Label $label -LuaPath $LuaPath -MGBPath $MGBPath
if ($LASTEXITCODE -ne 0) {
    throw "Session launch failed for capture $Capture"
}

$intent = [ordered]@{
    ticket          = 'TEXT-HANDLE-001'
    capture         = $Capture
    kind            = $kind
    label           = $label
    intended_target = $target
    looking_for     = $lookingFor
    rom_sha256      = $RomSha256.ToUpperInvariant()
    consumers       = @('0x08012230', '0x080122B4')
    object_register = 'r1'
    field_offset    = '0x04'
    table_base      = '0x087B5B64'
    table_count     = 7
    evidence_path   = $evidence
    note            = 'repeat captures of the SAME line are the evidence. MEASURED: the object pointer is ROM-resident, so it is STABLE across triggers rather than varying as a heap allocation would; the packed handle is likewise constant'
    staged_at_utc   = (Get-Date).ToUniversalTime().ToString('o')
}
$intent | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'capture-intent.json') -Encoding utf8

Write-Output ''
Write-Output "Capture $Capture staged. Trigger the line above, then close mGBA."
Write-Output "  evidence : $evidence"
Write-Output 'Collect with:'
Write-Output "  powershell -NoProfile -ExecutionPolicy Bypass -File tools\runtime\finish_toolkit031_session.ps1 -Label $label"
