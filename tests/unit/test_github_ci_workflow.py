"""The GitHub gate workflow: its triggers, its pinned actions and its five jobs.

Part 4 changes the shape from one serial job to parallel jobs: the portable suite
is sharded across ten runners, and the quality gates, the ROM-free integration
member and the adjacency orders are jobs of their own rather than steps queued
behind the suite.

That duplication has to stay tied to the reviewed bodies. The workflow no longer
calls the ``ci\\*.ps1`` scripts - it runs their commands directly, which is what
lets the shards be separate jobs - so this module parses the ``-m <module>``
invocations out of ``ci\\test_sdk.ps1``, ``ci\\adjacency.ps1`` and
``ci\\test_integration.ps1`` and requires every one of them in the workflow, with
``--all`` preserved for ``public_surface`` and ``readability``. A command dropped
from either side fails here.
"""

from __future__ import annotations

import re

import yaml

from tests.gates import REPOSITORY_ROOT
from tools.quality import architecture

WORKFLOW_PATH = REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml"

PINNED_ACTION = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}\Z")
FLOATING_REF = re.compile(r"@(?:main|master|latest|v[0-9]+)\b")
USES_LINE = re.compile(r"^[ \t]*uses:[ \t]*(\S+)(.*)$", re.MULTILINE)
MODULE_INVOCATION = re.compile(r"-m\s+([A-Za-z_][A-Za-z0-9_.]*)")

#: Every job the workflow must carry.
JOB_NAMES = ("shard", "gates", "integration", "adjacency", "report")

#: The tracked bodies whose command lists the workflow has to keep carrying.
TRACKED_GATE_BODIES = (
    r"ci\test_sdk.ps1",
    r"ci\adjacency.ps1",
    r"ci\test_integration.ps1",
)

#: The gates whose tree-wide form is a `--all` invocation on both sides.
ALL_TREE_GATES = ("public_surface", "readability")

#: The ROM-free integration member, by name.
INTEGRATION_MEMBER = "tests/integration/test_container_decode_synthetic.py"

#: Built from parts: the public-tree gates screen for these literals, so neither
#: this file nor the workflow may carry them whole.
ROM_NEEDLES = ("." + "gba", "." + "agb", "." + "sav", "save" + "state")
SECRET_NEEDLES = ("sec" + "rets", "gh" + "p_", "api" + "_key", "pass" + "word", "to" + "ken")

#: The two preconditions every job repeats, and the pin every job installs.
AUTOCRLF_OFF = "git config --global core.autocrlf false"
AUTOCRLF_READ_BACK = "git config --get core.autocrlf"
VOLUME_FROM_WORKSPACE = "Split-Path -Qualifier $env:GITHUB_WORKSPACE"
LEDGER_PATH = "docs/research/ROM_EDITOR_COVERAGE_LEDGER.md"
CHECKOUT_OWNER = "actions/checkout"
SETUP_PYTHON_OWNER = "actions/setup-python"
UPLOAD_OWNER = "actions/upload-artifact"
DOWNLOAD_OWNER = "actions/download-artifact"
SHARD_JOB = "shard"
SHARD_MATRIX_SIZE = 10


def _text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _document() -> dict:
    return yaml.safe_load(_text())


def _jobs() -> dict:
    return _document()["jobs"]


def _job(name: str) -> dict:
    return _jobs()[name]


def _steps(name: str) -> list[dict]:
    return _job(name)["steps"]


def _step(job: str, owner: str) -> dict:
    matches = [
        step for step in _steps(job)
        if str(step.get("uses", "")).startswith(owner + "@")
    ]
    assert len(matches) == 1, (job, owner)
    return matches[0]


def _uses_index(job: str, owner: str) -> int:
    matches = [
        index
        for index, step in enumerate(_steps(job))
        if str(step.get("uses", "")).startswith(owner + "@")
    ]
    assert len(matches) == 1, (job, owner)
    return matches[0]


def _run_indices(job: str, fragment: str) -> list[int]:
    return [
        index
        for index, step in enumerate(_steps(job))
        if fragment in str(step.get("run", ""))
    ]


def _run_index(job: str, fragment: str) -> int:
    matches = _run_indices(job, fragment)
    assert len(matches) == 1, (job, fragment)
    return matches[0]


def _run_script(job: str, fragment: str) -> str:
    return str(_steps(job)[_run_index(job, fragment)]["run"])


def test_the_workflow_parses_with_the_two_triggers_and_the_five_windows_jobs():
    """Prevents: a trigger or the runner label being dropped."""
    document = _document()
    # YAML reads the bare ``on`` key as the boolean True.
    triggers = document.get("on") or document.get(True)
    assert triggers is not None
    for trigger in ("push", "pull_request"):
        assert trigger in triggers
    assert document["defaults"]["run"]["shell"] == "pwsh"
    assert set(_jobs()) == set(JOB_NAMES)
    for name, job in _jobs().items():
        assert job["runs-on"] == "windows-latest", name
        assert isinstance(job["timeout-minutes"], int), name


def test_every_action_is_pinned_to_a_commit_with_its_tag_in_a_comment():
    """Prevents: a mutable major tag silently changing what CI runs."""
    text = _text()
    references = USES_LINE.findall(text)
    owners = []
    for reference, rest in references:
        assert PINNED_ACTION.fullmatch(reference), reference
        assert re.search(r"#\s*v?\d", rest), reference
        owners.append(reference.split("@")[0])
    for required in (CHECKOUT_OWNER, SETUP_PYTHON_OWNER, UPLOAD_OWNER, DOWNLOAD_OWNER):
        assert required in owners
    assert FLOATING_REF.search(text) is None


def test_the_shard_job_runs_ten_parallel_slices_of_the_portable_suite():
    """Prevents: a shard count or an environment variable drifting apart."""
    job = _job(SHARD_JOB)
    assert job["strategy"]["fail-fast"] is False
    assert len(job["strategy"]["matrix"]["shard"]) == SHARD_MATRIX_SIZE
    assert str(job["env"]["WEBFOOT_SHARD_COUNT"]) == str(SHARD_MATRIX_SIZE)
    assert job["env"]["WEBFOOT_SHARD_INDEX"] == "${{ matrix.shard }}"

    script = _run_script(SHARD_JOB, "tests/unit -q -n 4 --dist loadfile")
    assert "report-shard-${{ matrix.shard }}.xml" in script

    upload = _step(SHARD_JOB, UPLOAD_OWNER)
    assert upload["if"] == "always()"
    assert "report-shard-${{ matrix.shard }}.xml" in upload["with"]["path"]
    assert "artifacts/steps" in upload["with"]["path"]


def test_the_four_quality_gates_are_their_own_job_one_step_each():
    """Prevents: the gates being folded back into the suite's job."""
    for gate in ("public_surface", "architecture", "public_release", "readability"):
        assert len(_run_indices("gates", f"-m tools.quality.{gate}")) == 1, gate


def test_the_gates_job_fills_the_pip_cache_it_asks_for_and_installs_first():
    """Prevents: a cached pip setup whose cache the job never creates.

    Run 38504730899's gates job failed its post step with "Cache folder path is
    retrieved for pip but doesn't exist on disk": the job declares `cache: pip`
    with `cache-dependency-path: pyproject.toml` and never ran pip, so there was
    no directory to save. The gates themselves passed in that run without an
    install, so this step is the cache fix plus the hardening that they run
    against the project's declared environment, and the order matters: the
    install has to precede every gate.
    """
    install = _run_index("gates", "-m pip install")
    script = _run_script("gates", "-m pip install")
    assert script.strip().startswith("python -m pip install"), script
    assert "--quiet" in script, script
    assert re.search(r"-e\s+\.(\s|$)", script), script
    assert "[" not in script, "the gates job installs extras the gate set does not need"
    for gate in ("public_surface", "architecture", "public_release", "readability"):
        assert install < _run_index("gates", f"-m tools.quality.{gate}"), gate


def test_the_integration_job_runs_the_rom_free_member_by_name():
    """Prevents: the integration member widening to the ROM-gated directory."""
    script = _run_script("integration", INTEGRATION_MEMBER)
    assert "-q" in script
    install = _run_script("integration", "-m pip install")
    assert '.[dev]' in install and 'workbench' not in install


def test_the_adjacency_job_runs_both_orders_in_one_step_and_carries_the_exit():
    """Prevents: an exit after the forward order skipping the reverse order."""
    forward = _run_indices("adjacency", "-Order forward")
    assert forward, "the forward order is not run"
    assert forward == _run_indices("adjacency", "-Order reverse")
    script = _steps("adjacency")[forward[0]]["run"]
    assert "-m scripts.adjacency_run" in script
    assert "$forward = $LASTEXITCODE" in script
    assert "$forward -ne 0" in script


def test_the_report_job_needs_the_shards_and_always_publishes():
    """Prevents: the red run being the one with no merged report."""
    job = _job("report")
    assert SHARD_JOB in job["needs"]
    assert job["if"] == "always()"
    _step("report", DOWNLOAD_OWNER)
    assert "ci/merge_junit.py" in _run_script("report", "ci/merge_junit.py")
    assert "merged-suite.log" in _run_script("report", "merged-suite.log")
    upload = _step("report", UPLOAD_OWNER)
    assert upload["if"] == "always()"
    assert "report.xml" in upload["with"]["path"]


def test_every_job_keeps_the_committed_bytes_and_the_temporary_root():
    """Prevents: one job quietly losing a precondition the others carry."""
    for name in JOB_NAMES:
        checkout = _uses_index(name, CHECKOUT_OWNER)
        assert _run_index(name, AUTOCRLF_OFF) < checkout, name
        assert AUTOCRLF_READ_BACK in _run_script(name, AUTOCRLF_OFF)
        assert _run_index(name, LEDGER_PATH) > checkout, name
        assert "[char]13" in _run_script(name, LEDGER_PATH)
        root = _run_index(name, VOLUME_FROM_WORKSPACE)
        assert root > checkout, name
        script = _run_script(name, VOLUME_FROM_WORKSPACE)
        assert 'Add-Content -Path $env:GITHUB_ENV -Value "TMP=' in script
        assert 'Add-Content -Path $env:GITHUB_ENV -Value "TEMP=' in script

    # Defined once as anchors and referenced by every job: each body appears a
    # single time in the file, while the loop above proves all five jobs run it.
    text = _text()
    assert text.count(AUTOCRLF_OFF) == 1
    assert text.count(VOLUME_FROM_WORKSPACE) == 1
    assert text.count(LEDGER_PATH) == 1
    assert _run_index(SHARD_JOB, VOLUME_FROM_WORKSPACE) < _run_index(
        SHARD_JOB, "tests/unit -q -n 4 --dist loadfile"
    )


def test_the_runner_python_is_the_minor_version_the_project_declares():
    """Prevents: the gate running on an interpreter the project does not declare."""
    for name in JOB_NAMES:
        step = _step(name, SETUP_PYTHON_OWNER)
        assert step["with"]["python-version"] == "3.12", name
        assert step["with"]["cache"] == "pip", name
        assert step["with"]["cache-dependency-path"] == "pyproject.toml", name


def test_every_checkout_keeps_no_credential_and_fetches_the_history_the_gate_diffs():
    """Prevents: a shallow clone failing the gate's own history check."""
    for name in JOB_NAMES:
        step = _step(name, CHECKOUT_OWNER)
        assert step["with"]["persist-credentials"] is False, name
        # tests/unit/test_local_ci_script.py diffs 34da2e67..HEAD.
        assert step["with"]["fetch-depth"] == 0, name


def test_the_workflow_commands_are_the_gate_set_the_tracked_bodies_carry():
    """Prevents: the workflow and the reviewed gate bodies drifting apart."""
    workflow = _text()
    for body in TRACKED_GATE_BODIES:
        text = (REPOSITORY_ROOT / body).read_text(encoding="utf-8")
        for module in sorted(set(MODULE_INVOCATION.findall(text))):
            assert module in workflow, (body, module)
    for gate in ALL_TREE_GATES:
        assert f"-m tools.quality.{gate} --all" in workflow
    assert INTEGRATION_MEMBER in workflow


def test_the_workflow_directory_is_a_declared_top_level_root():
    """Prevents: the workflow tripping the repository purity rule it lives under."""
    assert architecture._rule_top_level_roots([".github/workflows/ci.yml"]) == []


def test_the_workflow_names_no_rom_file_and_no_secret():
    """Prevents: a commercial image or a credential entering a public workflow."""
    lowered = _text().lower()
    for needle in ROM_NEEDLES + SECRET_NEEDLES:
        assert needle not in lowered, needle
