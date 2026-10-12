# The `adjacency` CI job: the fixed app-wide-Qt-state set, one pytest process per
# order. Run it by hand from anywhere, after the job that builds the venv:
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File ci\test_sdk.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File ci\adjacency.ps1 -Order forward
#   powershell -NoProfile -ExecutionPolicy Bypass -File ci\adjacency.ps1 -Order reverse
#
# `test-sdk` runs the suite with `--dist loadfile`, which gives every module its
# own worker process, so no module ever follows another in one process and the
# module-to-module Qt state this exists for is never exercised there. The set,
# the one-member ROM exclusion and the fail-on-skip rule live in
# `scripts/adjacency_run.py`; both orders are named in `.gitlab-ci.yml` so an
# order cannot be dropped from the pipeline without the guard test noticing.

param(
    [Parameter(Mandatory)][ValidateSet('forward', 'reverse')][string]$Order
)

. (Join-Path $PSScriptRoot 'common.ps1')
Set-Location $CiProjectRoot

# `needs: ["test-sdk"]` in `.gitlab-ci.yml`: this job runs in the environment that
# job already built and proved, rather than paying a second 700 MB install of the
# same `.[dev,workbench,research]` extras. `tests/unit/test_ci_gui_surface.py`
# pins that link.
#
# That sharing holds while one runner takes this project's jobs one at a time
# (`concurrent = 1`) and both jobs land on it: `needs` orders jobs, it does not
# pin them to a runner or to a build directory. If that stops being true the venv
# is absent and `Use-CiVenv` fails here naming the job that builds it, rather
# than running the set in some other environment.
$python = Use-CiVenv -Name 'test-sdk'
$env:QT_QPA_PLATFORM = 'offscreen'
# Do not inherit the deployment credential into a test job.
$env:CLOUDFLARE_API_TOKEN = ''

Invoke-CiStep { & $python -m scripts.adjacency_run -Order $Order }
