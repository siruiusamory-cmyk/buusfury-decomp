#Requires -Version 5.1
<#
.SYNOPSIS
    Build build/buusfury.gba from the baserom plus source/disassembly inputs.

.DESCRIPTION
    Strict by default. The build verifies the baserom's canonical SHA-1, then
    rebuilds every region the region map says is reproducible and FAILS CLOSED
    on anything it cannot rebuild. It never silently copies a region it was
    supposed to rebuild.

    Without ARM Developer Suite 1.2 the strict build stops with a precise
    blocker report naming the exact commands and the exact missing sources.
    That is the correct outcome and is documented in docs/DECOMP_BASELINE.md.

    -AllowPassthrough assembles a complete image anyway. Such an image HAS the
    canonical SHA-1, which proves the region map is correct - but the build
    report (build/build-report.json) labels every passthrough region, so the
    result is never mistaken for a full source reproduction.

.PARAMETER AllowPassthrough
    Permit copying regions that the reference build rebuilds from source.

.PARAMETER Output
    Output path. Default: build/buusfury.gba

.PARAMETER Reference
    Root of the fetched 2genkidev/buusfury checkout (needed for asset regions).

.PARAMETER Ads12Root
    Root of an ARM Developer Suite 1.2 installation. Defaults to $ADS12_ROOT.

.EXAMPLE
    powershell -File scripts/build.ps1
.EXAMPLE
    .\build.cmd -AllowPassthrough
#>
[CmdletBinding()]
param(
    [string] $Rom,
    [string] $Output,
    [string] $Reference,
    [string] $Ads12Root,
    [switch] $AllowPassthrough
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repoRoot 'tools'

$pythonCmd = Get-Command python, python3, py -ErrorAction SilentlyContinue |
    Select-Object -First 1
if (-not $pythonCmd) { throw "No Python interpreter found on PATH (need 3.11+)." }
$python = $pythonCmd.Source

if (-not $Output) { $Output = Join-Path $repoRoot 'build/buusfury.gba' }

# NOTE: not $args - that is an automatic variable in PowerShell.
$cliArgs = @('-m', 'buusfury', 'build', '-o', $Output)
if ($Rom)              { $cliArgs += @('--rom', $Rom) }
if ($Reference)        { $cliArgs += @('--reference', $Reference) }
if ($Ads12Root)        { $cliArgs += @('--ads12-root', $Ads12Root) }
if ($AllowPassthrough) { $cliArgs += '--allow-passthrough' }

& $python @cliArgs
exit $LASTEXITCODE
