<#
.SYNOPSIS
Close out a TOOLKIT-031 play session and summarise its evidence.

.DESCRIPTION
The companion to start_toolkit031_session.ps1. That script deliberately exits
while mGBA keeps running, so the post-run steps of the canonical procedure --
verifying the ROM was not modified, and reporting what was actually measured --
live here instead.

Run this AFTER closing the mGBA window.

It never kills the emulator. If mGBA is still up, it says so and stops, because
summarising a session that is still producing evidence would report a partial
result as a final one.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Label
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runDir = Join-Path $root ("build\toolkit031\" + $Label)
if (-not (Test-Path -LiteralPath $runDir)) { throw "No such run: $runDir" }

$inputsPath = Join-Path $runDir 'inputs.json'
if (-not (Test-Path -LiteralPath $inputsPath)) { throw "Run has no inputs.json: $runDir" }
$inputs = Get-Content -LiteralPath $inputsPath -Raw | ConvertFrom-Json

if (Get-Process mGBA -ErrorAction SilentlyContinue) {
    Write-Output 'mGBA is STILL RUNNING; close its window before collecting evidence.'
    Write-Output 'Refusing to summarise a session that is still in progress.'
    exit 2
}

# Post-run identity check, the same one the tracked GDB launcher performs.
$romHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $inputs.rom_path).Hash
if ($romHashAfter -ne $inputs.rom_sha256) {
    throw "ROM changed during the run: $($inputs.rom_sha256) -> $romHashAfter"
}

$csv = $inputs.csv_path
if (-not (Test-Path -LiteralPath $csv)) {
    Write-Output 'no observer output'
    exit 1
}

$rows = @(Import-Csv -LiteralPath $csv)
# Historical TOOLKIT-031 rows are EXEC/INTERP. TOOLKIT-034 keeps the same
# observer contract but names its evidence rows after the sampled code site.
# Treat both spellings as their same channels so a live new observer cannot be
# summarised as a zero-hit, liveness-unproven run.
$exec = @($rows | Where-Object { $_.kind -in @('EXEC', 'TRAMPOLINE') })
$interp = @($rows | Where-Object { $_.kind -in @('INTERP', 'INTERPRETER') })
$struct = @($rows | Where-Object { $_.kind -eq 'STRUCT' })
$historicalExec = @($exec | Where-Object { $_.kind -eq 'EXEC' })
$callerExec = @($exec | Where-Object { $_.kind -eq 'TRAMPOLINE' })
$maps = @($rows | Where-Object { $_.map_index } | Select-Object -ExpandProperty map_index -Unique | Sort-Object)
$lastFrame = if ($rows.Count) { ($rows | Select-Object -Last 1).frame } else { 0 }

Write-Output "run       : $runDir"
Write-Output "rom sha   : $romHashAfter (unchanged)"
Write-Output "frames    : $lastFrame"
Write-Output "maps seen : $($maps -join ', ')"
Write-Output ''
Write-Output "TRAMPOLINE (execution)  : $($exec.Count)"
Write-Output "INTERPRETER (liveness)  : $($interp.Count)"
Write-Output "STRUCT (attachment)     : $($struct.Count)"
Write-Output ''

if ($exec.Count -gt 0) {
    Write-Output 'EXECUTION OBSERVED - descriptors reaching the trampoline:'
    # Preserve the historical descriptor grouping for EXEC rows. TOOLKIT-034
    # deliberately records the equivalent values under attribution/r0/payload,
    # so presenting it through descriptor_kind/descriptor would create blank
    # groups and hide the caller evidence.
    $historicalExec | Group-Object descriptor_kind, descriptor |
        ForEach-Object { Write-Output ("  {0}  x{1}" -f $_.Name, $_.Count) }
    if ($callerExec.Count -gt 0) {
        Write-Output 'TOOLKIT-034 caller snapshots (attribution, descriptor, payload):'
        $callerExec | Group-Object attribution, r0, payload |
            ForEach-Object { Write-Output ("  {0}  x{1}" -f $_.Name, $_.Count) }
    }
} elseif ($interp.Count -gt 0) {
    # This is the case the liveness channel exists to distinguish: scripts DID
    # run, so the instrument sees execution, and the placement-descriptor path
    # specifically was not taken. That is a measurement, not a blind spot.
    Write-Output 'NO trampoline execution, but the interpreter WAS reached.'
    Write-Output 'The instrument sees execution; the placement path was not taken.'
} else {
    # Neither channel fired, so nothing can be concluded in either direction.
    Write-Output 'NEITHER channel fired: instrument liveness UNPROVEN.'
    Write-Output 'This is not negative evidence.'
}
