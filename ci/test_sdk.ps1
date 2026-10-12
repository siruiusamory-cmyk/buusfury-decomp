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

# The worker count and the memory reading stay in the log as evidence: this is
# the machine's own 8 cores, not the shared runner's 2, and `-n auto` is
# pytest-xdist's reading of it rather than a number that can drift from the
# machine. `-q` suppresses the header where xdist would otherwise report it.
Invoke-CiStep { & $python -c "import os; print('cores:', os.cpu_count())" }
Invoke-CiStep { & $python -c "import os; print('xdist workers (auto):', os.cpu_count())" }
Get-CimInstance Win32_OperatingSystem | ForEach-Object {
    Write-Host ("memory: {0:N1} GB total, {1:N1} GB free" -f ($_.TotalVisibleMemorySize / 1MB), ($_.FreePhysicalMemory / 1MB))
}

# The JUnit report is what makes a failure legible in the merge request without
# downloading the raw job log, and xdist merges every worker's results into this
# one file. It is written to the repository root, where the job's
# `artifacts:reports:junit` names it.
Invoke-CiStep { & $python -m pytest tests/unit -q -n auto --dist loadfile --junitxml=report.xml }
# The gates a reviewer is told to run, run here as well: the readability gate is
# only asserted over the shipping package inside the suite, so the tree-wide form
# has to be its own step or a finding outside `tools/webfoot/` would pass CI.
Invoke-CiStep { & $python -m tools.quality.public_surface --all }
Invoke-CiStep { & $python -m tools.quality.architecture }
Invoke-CiStep { & $python -m tools.quality.public_release }
Invoke-CiStep { & $python -m tools.quality.readability --all }
