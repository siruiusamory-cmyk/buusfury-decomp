<#
.SYNOPSIS
Stage one TOOLKIT-034 runtime trial and RETURN, leaving mGBA running for play.

.DESCRIPTION
TOOLKIT-034 asks whether an authored behavior can be made to run at a
deliberate gameplay moment, and specifically whether the condition is DEFEAT or
merely OBJECT RELEASE. The authored `trigger` is planning attribution and emits
no ROM bytes, so trial A and trial B load the SAME image by design and are
separated by what the operator does, not by what was built.

That is the whole reason this wrapper exists: it names the trial, records the
intended condition alongside the run, and refuses a label that would silently
overwrite earlier evidence. It then delegates to start_toolkit031_session.ps1,
which owns launch, injection and state load in the proven order.

It holds no wait loop and no cleanup, because nothing may own the emulator's
lifetime during human play. Two prior sessions were destroyed by exactly that.
The operator ends the run by closing the mGBA window; evidence is collected
afterwards by finish_toolkit031_session.ps1.

Read-only: no emulated memory is written and no input is driven.

.PARAMETER Trial
  A  defeat the authored type-0086 enemy on map 40
  B  leave the map without defeating it, same setup and route
  C  canonical control: defeat a non-authored enemy so the observer's
     death channel is shown to detect a known event
  D  replacement A/B in ONE capture: stand on map 40 with the authored enemy
     visible and DO NOT TOUCH IT for a long measured window, then defeat it.
     The alive window and the defeat are the same run, so the negative and the
     positive share one instrument and one residency proof.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass `
    -File tools\runtime\stage_toolkit034_trial.ps1 -Trial A
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('A', 'B', 'C', 'D')]
    [string]$Trial,

    [string]$Suffix,

    [string]$RomPath = 'build\toolkit034\runtime-triggered\toolkit034-on-defeat.gba',

    # The authored image built by the TOOLKIT-034 on_defeat project. Equality
    # test only; there is no wildcard and no skip.
    [string]$RomSha256 = 'BBD0BBBE1F01B4D715B89BB20A22F63276E36EC4FD2DC443E34AE3B99880FF35',

    [string]$StatePath = '<checkout>\roms\Dragon Ball Z - Buu''s Fury (U).ss1',

    [string]$LuaPath = 'tools\runtime\toolkit034_dispatch_caller_watch.lua',

    # build/ is gitignored, so this git worktree has no emulator of its own.
    # Point at the main checkout's 0.11 dev build rather than copying an 8 MiB
    # binary per worktree. Naming a path proves nothing on its own, and
    # start_toolkit031_session.ps1 still reads the version out of the binary and
    # fails closed on a mismatch, so that guard is unchanged.
    [string]$MGBPath = '<checkout>\build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe'
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path

$conditions = @{
    A = 'DEFEAT the authored type-0086 enemy on map 40'
    B = 'LEAVE map 40 without defeating the authored enemy, same setup and route as A'
    C = 'CANONICAL CONTROL: defeat a NON-authored enemy so the death channel is shown to fire'
    D = 'ALIVE WINDOW then DEFEAT, one capture: leave the authored enemy untouched for a long window, THEN defeat it'
}

$expectations = @{
    A = @(
        'DEATH-CALLBACK / AUTHORED-ACTOR-DEATH  expected',
        'SCRIPT + NATIVE-HANDLER               expected if the trigger is defeat',
        'visible MATCH 2 FIGHT! banner          expected if the trigger is defeat'
    )
    B = @(
        'DEATH-CALLBACK                         expected ABSENT',
        'DESTRUCTOR-* on map exit               expected PRESENT',
        'SCRIPT + NATIVE-HANDLER                DECIDES THE NAME: present here means',
        '                                       release, not defeat, and the honest',
        '                                       name becomes on_object_release'
    )
    C = @(
        'DEATH-CALLBACK / CANONICAL-NULL-ACTOR-DEATH  expected',
        'proves the death channel detects a known event before any negative counts'
    )
    D = @(
        'PHASE 1, alive window:',
        '  ACTOR-EVENT-CREATE / AUTHORED-ACTOR        expected, proves instantiation',
        '  ACTOR-HEARTBEAT / AUTHORED-ACTOR-ALIVE     expected REPEATEDLY, proves',
        '                                             resident AND HP > 0 the whole window',
        '  SCRIPT / NATIVE-OPCODE / NATIVE-HANDLER    expected ABSENT for the window',
        'PHASE 2, after you defeat it:',
        '  DEATH-CALLBACK / AUTHORED-ACTOR-DEATH      expected',
        '  DESTRUCTOR-DISPATCH -> TRAMPOLINE -> SCRIPT expected',
        '  NATIVE-OPCODE slot 0xB2 -> handler args     expected 1525 / 120 / 105',
        '  visible MATCH 2 FIGHT! banner               expected'
    )
}

if (-not $Suffix) { $Suffix = Get-Date -Format 'yyyyMMdd-HHmm' }
$label = "tk034-trial-$($Trial.ToLowerInvariant())-$Suffix"

$runDir = Join-Path $root ("build\toolkit031\" + $label)
if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists, refusing to overwrite evidence: $runDir"
}

Write-Output "TOOLKIT-034 trial $Trial"
Write-Output "  condition : $($conditions[$Trial])"
Write-Output "  label     : $label"
Write-Output ''
Write-Output '  what this trial is looking for:'
foreach ($line in $expectations[$Trial]) { Write-Output "    $line" }
Write-Output ''

& powershell -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $PSScriptRoot 'start_toolkit031_session.ps1') `
    -RomPath $RomPath -RomSha256 $RomSha256 -StatePath $StatePath `
    -Label $label -LuaPath $LuaPath -MGBPath $MGBPath
if ($LASTEXITCODE -ne 0) {
    throw "Session launch failed for trial $Trial"
}

# Record the intended condition next to the evidence. Which trial a CSV belongs
# to is otherwise recoverable only from the directory name, and the A/B pair is
# indistinguishable by ROM hash by design.
$intent = [ordered]@{
    ticket             = 'TOOLKIT-034'
    trial              = $Trial
    label              = $label
    intended_condition = $conditions[$Trial]
    looking_for        = $expectations[$Trial]
    rom_sha256         = $RomSha256.ToUpperInvariant()
    note               = 'trigger is planning attribution and emits no ROM bytes; A and B load the same image and differ only in operator action'
    staged_at_utc      = (Get-Date).ToUniversalTime().ToString('o')
}
$intent | ConvertTo-Json -Depth 4 |
    Set-Content -LiteralPath (Join-Path $runDir 'trial-intent.json') -Encoding utf8

Write-Output ''
Write-Output "Trial $Trial staged. Play the condition above, then close mGBA."
Write-Output "Collect with:"
Write-Output "  powershell -NoProfile -ExecutionPolicy Bypass -File tools\runtime\finish_toolkit031_session.ps1 -Label $label"
