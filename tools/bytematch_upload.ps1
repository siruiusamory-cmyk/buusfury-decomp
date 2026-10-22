param(
    [string]$Objdiff = "objdiff-cli",
    [string]$Version = "BG3E",
    [string]$Owner = "siruiusamory-cmyk",
    [string]$Repo = "buusfury-decomp"
)
$ErrorActionPreference = "Stop"
if (-not $env:BYTEMATCH_TOKEN) { throw "BYTEMATCH_TOKEN is not set" }
if (-not (Get-Command $Objdiff -ErrorAction SilentlyContinue)) { throw "objdiff-cli not found at $Objdiff" }
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python tools\gate\gate.py
if ($LASTEXITCODE -ne 0) { throw "the gate failed, no report was produced" }
python tools\objdiff\objdiff_gen.py --targets
if ($LASTEXITCODE -ne 0) { throw "objdiff.json generation failed" }
$report = Join-Path $root ("build\" + $Version + "\report.json")
New-Item -ItemType Directory -Force (Split-Path -Parent $report) | Out-Null
& $Objdiff report generate -o $report
if ($LASTEXITCODE -ne 0) { throw "objdiff report generation failed" }
$commit = (git rev-parse HEAD).Trim()
$gz = $report + ".gz"
python -c "import gzip,pathlib,sys; pathlib.Path(sys.argv[2]).write_bytes(gzip.compress(pathlib.Path(sys.argv[1]).read_bytes(), 9))" $report $gz
if ($LASTEXITCODE -ne 0) { throw "gzip failed" }
$url = "https://bytematch.dev/api/v1/projects/$Owner/$Repo/reports?version=$Version&commit=$commit"
curl.exe -sS --fail-with-body -X POST $url -H "Authorization: Bearer $env:BYTEMATCH_TOKEN" -H "Content-Type: application/json" -H "Content-Encoding: gzip" --data-binary "@$gz"
if ($LASTEXITCODE -ne 0) { throw "upload failed" }
