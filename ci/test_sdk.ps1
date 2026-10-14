# The `test-sdk` CI job: the portable suite across xdist worker processes, then
# the tree-wide quality gates. Run it by hand from anywhere:
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File ci\test_sdk.ps1
#
# The suite is the `fast` gate of docs/testing.md. The order below is the order
# the Linux job ran: install the shipping extras, run the suite, then the gates.

. (Join-Path $PSScriptRoot 'common.ps1')
Set-Location $CiProjectRoot

# `workbench` is the shipping GUI surface and `research` is capstone: without
# them fifteen modules under tests/unit skip as a whole. The venv is fresh, so
# this is the install the job's environment is.
$python = New-CiVenv -Name 'test-sdk' -Extras '.[dev,workbench,research]'

# The runner has no display and several Workbench modules construct a real
# QApplication. `.gitlab-ci.yml` sets this as a job variable too, which is where
# `tests/unit/test_ci_gui_surface.py` asserts it; set here as well so a hand run
# cannot be the one run that differs.
$env:QT_QPA_PLATFORM = 'offscreen'
# Do not inherit the deployment credential into a test job.
$env:CLOUDFLARE_API_TOKEN = ''

# The worker count is capped at 4 rather than `-n auto`, which is 8 on this
# machine's 8 cores. Measured 2026-10-12: at 8 workers the run produced
# `Windows fatal exception: code 0x8007000e` (E_OUTOFMEMORY) from
# `platform.platform()`'s WMI query inside xdist workers at sessionstart, and the
# box had 8.7 GB free while other work was running. The lead measured a 4-worker
# run of this suite at a peak of 2,862 MB across 12 python processes on the same
# machine, where free memory fell to 4.2 GB during the day. The 8-worker peak was
# not measured, so 8 workers are not claimed to be safe. The core count and the
# free memory stay in the log as the reading the cap was chosen against.
Invoke-CiStep { & $python -c "import os; print('cores:', os.cpu_count())" }
Invoke-CiStep { & $python -c "import os; print('xdist workers:', 4)" }
Get-CimInstance Win32_OperatingSystem | ForEach-Object {
    Write-Host ("memory: {0:N1} GB total, {1:N1} GB free" -f ($_.TotalVisibleMemorySize / 1MB), ($_.FreePhysicalMemory / 1MB))
}

# A shell runner's checkout persists, so a `dist/` left behind by an earlier
# `test-site` job would survive into this one. Six artifact-dependent modules
# then run against an artifact that may belong to another commit, instead of
# skipping the way they do in the Linux job's fresh container: measured, 46
# passed with `dist/` present against 6 skips without it. They must skip here.
# `test-site` is the job that builds the site and validates the artifact.
Remove-Item -LiteralPath (Join-Path $CiProjectRoot 'dist') -Recurse -Force -ErrorAction SilentlyContinue

# The JUnit report is what makes a failure legible in the merge request without
# downloading the raw job log, and xdist merges every worker's results into this
# one file. It is written to the repository root, where the job's
# `artifacts:reports:junit` names it.
Invoke-CiStep { & $python -m pytest tests/unit -q -n 4 --dist loadfile --junitxml=report.xml }
# The gates a reviewer is told to run, run here as well: the readability gate is
# only asserted over the shipping package inside the suite, so the tree-wide form
# has to be its own step or a finding outside `tools/webfoot/` would pass CI.
Invoke-CiStep { & $python -m tools.quality.public_surface --all }
Invoke-CiStep { & $python -m tools.quality.architecture }
Invoke-CiStep { & $python -m tools.quality.public_release }
Invoke-CiStep { & $python -m tools.quality.readability --all }
# The comment bar is measured on the lines a change adds, against the base the
# pipeline is judged on: the merge request's own diff base when there is one, and
# the default branch otherwise. The same signal, the same step, no second job.
Invoke-CiStep {
    $base = $env:CI_MERGE_REQUEST_DIFF_BASE_SHA
    if (-not $base) {
        & git rev-parse --verify --quiet 'origin/master' > $null 2>$null
        if ($LASTEXITCODE -ne 0) {
            & git fetch --quiet --no-tags origin '+refs/heads/master:refs/remotes/origin/master'
            if ($LASTEXITCODE -ne 0) { throw "ci: the comment bar base origin/master cannot be resolved" }
        }
        # The fork, not the branch tip: diffing against a master that has moved on
        # charges this branch for every commit master landed since it left.
        $base = & git merge-base 'origin/master' 'HEAD'
        if (-not $base) { throw "ci: the comment bar cannot find the merge base with origin/master" }
    }
    Write-Host "readability: comment bar against $base"
    & $python -m tools.quality.readability --changed $base
}
