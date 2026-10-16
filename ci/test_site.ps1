# The `test-site` CI job: type-check the site source, build the artifact, then
# validate the artifact and the data behind it. Run it by hand from anywhere:
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File ci\test_site.ps1
#
# node here is v24.16.0 and the Linux job's image was node:22. That is a
# difference, not parity: this job runs the machine's own node, and
# `docs/testing.md` records the version it was measured with.
#
# `tools/quality/site_check.py` is standard-library Python, so the machine's
# interpreter is the whole dependency and there is no venv to build. No
# Cloudflare token is read, written or printed by this job.

. (Join-Path $PSScriptRoot 'common.ps1')
Set-Location $CiProjectRoot

Invoke-CiStep { & node -v }
Invoke-CiStep { & npm ci }
Invoke-CiStep { & npm run check }
Invoke-CiStep { & npm run build }
Invoke-CiStep { & python tools/quality/site_check.py }
