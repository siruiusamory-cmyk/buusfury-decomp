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
    [string]$OutputPath
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
$startedAtUtc = [DateTime]::UtcNow

& $headless `
    $resolvedProjectDir `
    $ProjectName `
    -process $ProgramName `
    -noanalysis `
    -readOnly `
    -scriptPath $resolvedScriptDir `
    -postScript 'CalibrationReport.java' $absoluteOutputPath

if ($LASTEXITCODE -ne 0) {
    throw "Ghidra headless calibration failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path -LiteralPath $absoluteOutputPath -PathType Leaf)) {
    throw "Ghidra did not produce the calibration report: $absoluteOutputPath"
}

$report = Get-Item -LiteralPath $absoluteOutputPath
if ($report.LastWriteTimeUtc -lt $startedAtUtc) {
    throw "Ghidra did not refresh the calibration report: $absoluteOutputPath"
}
