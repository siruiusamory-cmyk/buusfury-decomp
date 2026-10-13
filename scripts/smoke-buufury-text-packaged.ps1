# The packaged-executable smoke for Buu's Fury Text Editor.
#
#   pwsh scripts/smoke-buufury-text-packaged.ps1
#
# This drives the ACTUAL RELEASE EXECUTABLE - not a python script, not a pytest
# fixture, not the interpreter from the checkout. The frozen build is windowed and
# has no console, so it is asked for its answer through its own headless flags:
# `--smoke` builds the real window offscreen, walks every pane, closes and returns
# without ever showing one.
#
# What it proves, in order:
#   * the frozen build runs its own smoke path and EXITS. That is the no-window
#     check: a build that fell through to the ordinary launch would enter the Qt
#     event loop and never return, so the bounded wait below ends in a refusal
#     rather than a pass;
#   * the frozen build reports the version this checkout records;
#   * the artefact's own sha256, mtime and size are recorded, because an artefact is
#     evidence only when they are;
#   * the run is given nothing to write: both flags only read, so no ROM, save or
#     save state can be touched by it.
#
# The smoke run drives tools/buufury_text/app.py, which is where `--smoke` lives.
# Nothing here reads the report the interpreter-side tests read, so a change to that
# report does not silently change what this script asserts.

[CmdletBinding()]
param(
    [string] $DistDir = 'build/packaged',
    [string] $BuildName = "Buu's Fury Text Editor",
    [string] $WorkDir = 'build/buufury-text-packaged',
    [int] $TimeoutSeconds = 120
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location $repo
try {
    $exe = Join-Path (Join-Path $DistDir $BuildName) "$BuildName.exe"
    if (-not (Test-Path $exe)) { throw "no packaged executable at $exe - run: pwsh scripts/build-buufury-text.ps1 -Clean" }
    $exe = (Resolve-Path $exe).Path

    $work = Join-Path (Get-Location) $WorkDir
    if (Test-Path $work) { Remove-Item $work -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $work | Out-Null

    # Through System.Diagnostics rather than `& $exe`: a GUI-subsystem process has no
    # console for PowerShell to redirect, so `& $exe --smoke` returns no output and no
    # exit code at all, and `Start-Process -PassThru` without -Wait returns a process
    # whose ExitCode is not readable. This is the one route that gives both a bounded
    # wait and a real exit code. Every argument is quoted because a value that
    # contains spaces must survive as one argument.
    function Invoke-Packaged {
        param([string[]] $Arguments)
        $info = New-Object System.Diagnostics.ProcessStartInfo
        $info.FileName = $exe
        $info.Arguments = (($Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' ')
        $info.UseShellExecute = $false
        $info.CreateNoWindow = $true
        $info.RedirectStandardOutput = $true
        $info.RedirectStandardError = $true
        $process = [System.Diagnostics.Process]::Start($info)
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            $process.Kill()
            throw "$exe $($info.Arguments) did not return within $TimeoutSeconds seconds: it opened a window instead of answering, or it hung"
        }
        [pscustomobject]@{
            ExitCode = $process.ExitCode
            StdOut = $process.StandardOutput.ReadToEnd()
            StdErr = $process.StandardError.ReadToEnd()
        }
    }

    $smoke = Invoke-Packaged -Arguments @('--smoke')
    $smoke.StdOut | Set-Content (Join-Path $work 'smoke-stdout.txt') -Encoding utf8
    $smoke.StdErr | Set-Content (Join-Path $work 'smoke-stderr.txt') -Encoding utf8
    if ($smoke.ExitCode -ne 0) {
        throw "$exe --smoke exited $($smoke.ExitCode). $($smoke.StdErr.Trim())"
    }

    $version = Invoke-Packaged -Arguments @('--version')
    if ($version.ExitCode -ne 0) { throw "$exe --version exited $($version.ExitCode)" }
    $visible = $version.StdOut.Trim()
    $expected = (& python -c "import tools.buufury_text.identity as identity; print(identity.PRODUCT_NAME, identity.PRODUCT_VERSION)").Trim()
    if ($visible -ne $expected) {
        throw "the packaged build reports '$visible' and this checkout records '$expected'"
    }

    $item = Get-Item $exe
    $digest = (Get-FileHash $exe -Algorithm SHA256).Hash
    $staged = Get-ChildItem (Split-Path -Parent $exe) -Recurse -File | Measure-Object -Property Length -Sum

    Write-Host ''
    Write-Host "PACKAGED EXE SMOKE: PASS"
    Write-Host "  executable        : $($item.FullName)"
    Write-Host "  executable sha256 : $digest"
    Write-Host "  executable mtime  : $($item.LastWriteTimeUtc.ToString('o'))"
    Write-Host "  staged size       : $([math]::Round($staged.Sum / 1MB, 1)) MB in $($staged.Count) files"
    Write-Host "  visible version   : $visible"
    Write-Host "  smoke exit code   : 0 (returned inside $TimeoutSeconds s, no window)"
    Write-Host "  smoke output      : $(Join-Path $work 'smoke-stdout.txt')"
}
finally {
    Pop-Location
}
