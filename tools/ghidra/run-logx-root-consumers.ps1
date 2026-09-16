[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GhidraInstallDir,

    [Parameter(Mandatory = $true)]
    [string]$ProjectDir,

    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [Parameter(Mandatory = $true)]
    [string]$ProgramName,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [string[]]$Addresses
)

$ErrorActionPreference = 'Stop'

$headless = Join-Path $GhidraInstallDir 'support\analyzeHeadless.bat'
if (-not (Test-Path -LiteralPath $headless -PathType Leaf)) {
    throw "analyzeHeadless.bat not found: $headless"
}

$scriptDir = Split-Path -Parent $PSCommandPath
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..\..')).Path
$resolvedProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$resolvedScriptDir = (Resolve-Path -LiteralPath $scriptDir).Path
$absoluteOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$allowedReportRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $repositoryRoot 'build\ghidra\reports')
).TrimEnd('\', '/')
$allowedReportPrefix = $allowedReportRoot + [System.IO.Path]::DirectorySeparatorChar
if (-not $absoluteOutputPath.StartsWith(
        $allowedReportPrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
    throw "OutputPath must be below ignored directory: $allowedReportRoot"
}

$reportDir = Split-Path -Parent $absoluteOutputPath
if (-not (Test-Path -LiteralPath $reportDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}

$startedAtUtc = [DateTime]::UtcNow

& $headless `
    $resolvedProjectDir `
    $ProjectName `
    -process $ProgramName `
    -noanalysis `
    -readOnly `
    -scriptPath $resolvedScriptDir `
    -postScript 'LogxRootConsumers.java' $absoluteOutputPath @Addresses

if ($LASTEXITCODE -ne 0) {
    throw "Ghidra headless LOGX consumer report failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path -LiteralPath $absoluteOutputPath -PathType Leaf)) {
    throw "Ghidra did not produce the LOGX consumer report: $absoluteOutputPath"
}

$report = Get-Item -LiteralPath $absoluteOutputPath
if ($report.LastWriteTimeUtc -lt $startedAtUtc) {
    throw "Ghidra did not refresh the LOGX consumer report: $absoluteOutputPath"
}
