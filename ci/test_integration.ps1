# The `test-integration` CI job: the one ROM-free member of the ROM-gated
# directory, by name. Run it by hand from anywhere:
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File ci\test_integration.ps1
#
# The selection's runtime import graph is `hashlib`, `json`, `pathlib`,
# `__future__` and `tools.webfoot.formats`, and that package imports nothing at
# all: `.[dev]` is the whole install and there is no Qt platform to select,
# because the selection imports no Qt. `tests/unit/test_ci_gui_surface.py`
# asserts both halves.

. (Join-Path $PSScriptRoot 'common.ps1')
Set-Location $CiProjectRoot

$python = New-CiVenv -Name 'test-integration' -Extras '.[dev]'
# Do not inherit the deployment credential into a test job.
$env:CLOUDFLARE_API_TOKEN = ''

Invoke-CiStep { & $python -m pytest tests/integration/test_container_decode_synthetic.py -q }
