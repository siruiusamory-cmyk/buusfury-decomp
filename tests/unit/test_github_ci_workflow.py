"""The GitHub gate workflow: its triggers, its pinned actions and its four steps.

The workflow calls the reviewed ``ci\\*.ps1`` bodies rather than restating their
command lists, so the wiring around them is what needs a guard: the two triggers,
one Windows job, a 40-hex pin on every action, the four gate bodies in order, and
an upload that still runs after a failure.
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

#: The four gate bodies in the order the local record runs them. The last two
#: share one step, so the reverse order still runs when the forward one fails.
GATE_BODIES = (
    r"ci\test_sdk.ps1",
    r"ci\test_integration.ps1",
    r"ci\adjacency.ps1 -Order forward",
    r"ci\adjacency.ps1 -Order reverse",
)

#: Built from parts: the public-tree gates screen for these literals, so neither
#: this file nor the workflow may carry them whole.
ROM_NEEDLES = ("." + "gba", "." + "agb", "." + "sav", "save" + "state")
SECRET_NEEDLES = ("sec" + "rets", "gh" + "p_", "api" + "_key", "pass" + "word", "to" + "ken")

#: The two preconditions the first Windows runner run measured: the bytes on
#: disk must be the committed bytes, and the temporary root must share the
#: checkout's volume.
AUTOCRLF_OFF = "git config --global core.autocrlf false"
AUTOCRLF_READ_BACK = "git config --get core.autocrlf"
VOLUME_FROM_WORKSPACE = "Split-Path -Qualifier $env:GITHUB_WORKSPACE"
LEDGER_PATH = "docs/research/ROM_EDITOR_COVERAGE_LEDGER.md"


def _text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _document() -> dict:
    return yaml.safe_load(_text())


def _job() -> dict:
    jobs = _document()["jobs"]
    assert len(jobs) == 1
    return next(iter(jobs.values()))


def _steps() -> list[dict]:
    return _job()["steps"]


def _run_index(fragment: str) -> int:
    """The index of the one step whose script carries ``fragment``."""
    matches = [
        index
        for index, step in enumerate(_steps())
        if fragment in str(step.get("run", ""))
    ]
    assert len(matches) == 1, fragment
    return matches[0]


def _run_script(fragment: str) -> str:
    return str(_steps()[_run_index(fragment)]["run"])


def _uses_index(owner: str) -> int:
    matches = [
        index
        for index, step in enumerate(_steps())
        if str(step.get("uses", "")).startswith(owner + "@")
    ]
    assert len(matches) == 1, owner
    return matches[0]


def _step(owner: str) -> dict:
    matches = [
        step
        for step in _job()["steps"]
        if str(step.get("uses", "")).startswith(owner + "@")
    ]
    assert len(matches) == 1, owner
    return matches[0]


def test_the_workflow_parses_with_the_two_triggers_and_one_windows_job():
    """Prevents: a trigger or the runner label being dropped."""
    document = _document()
    # YAML reads the bare ``on`` key as the boolean True.
    triggers = document.get("on") or document.get(True)
    assert triggers is not None
    for trigger in ("push", "pull_request"):
        assert trigger in triggers
    job = _job()
    assert job["runs-on"] == "windows-latest"
    assert isinstance(job["timeout-minutes"], int)


def test_every_action_is_pinned_to_a_commit_with_its_tag_in_a_comment():
    """Prevents: a mutable major tag silently changing what CI runs."""
    text = _text()
    references = USES_LINE.findall(text)
    owners = []
    for reference, rest in references:
        assert PINNED_ACTION.fullmatch(reference), reference
        assert re.search(r"#\s*v?\d", rest), reference
        owners.append(reference.split("@")[0])
    for required in ("actions/checkout", "actions/setup-python", "actions/upload-artifact"):
        assert required in owners
    assert FLOATING_REF.search(text) is None


def test_the_four_gate_bodies_run_in_the_order_the_local_record_runs_them():
    """Prevents: a dropped gate, a reordered gate, or a skipped reverse order."""
    text = _text()
    missing = [body for body in GATE_BODIES if body not in text]
    assert not missing, missing
    offset = -1
    for body in GATE_BODIES:
        at = text.index(body)
        assert at > offset, f"{body} is out of order"
        offset = at


def test_the_runner_python_is_the_minor_version_the_project_declares():
    """Prevents: the gate running on an interpreter the project does not declare."""
    assert _step("actions/setup-python")["with"]["python-version"] == "3.12"


def test_the_upload_step_always_runs_and_carries_the_report_and_the_captures():
    """Prevents: the failed run being the one with no log to read."""
    upload = _step("actions/upload-artifact")
    assert upload["if"] == "always()"
    paths = upload["with"]["path"]
    assert "report.xml" in paths
    assert "artifacts/steps" in paths


def test_the_checkout_keeps_no_credential_in_the_worktree():
    """Prevents: the job credential being left in the checkout's git config."""
    assert _step("actions/checkout")["with"]["persist-credentials"] is False


def test_the_checkout_fetches_the_history_the_gate_diffs():
    """Prevents: a shallow clone failing the gate's own history check."""
    assert _step("actions/checkout")["with"]["fetch-depth"] == 0


def test_the_workflow_directory_is_a_declared_top_level_root():
    """Prevents: the workflow tripping the repository purity rule it lives under."""
    assert architecture._rule_top_level_roots([".github/workflows/ci.yml"]) == []


def test_the_workflow_names_no_rom_file_and_no_secret():
    """Prevents: a commercial image or a credential entering a public workflow."""
    lowered = _text().lower()
    for needle in ROM_NEEDLES + SECRET_NEEDLES:
        assert needle not in lowered, needle


def test_the_checkout_is_told_to_keep_committed_bytes_before_it_runs():
    """Prevents: a CRLF checkout failing the renderer's byte comparison."""
    script = _run_script(AUTOCRLF_OFF)
    assert AUTOCRLF_READ_BACK in script
    assert _run_index(AUTOCRLF_OFF) < _uses_index("actions/checkout")


def test_the_temporary_root_shares_the_checkout_volume_before_the_gates():
    """Prevents: a cross-volume hardlink clone failing the local-CI fixture."""
    script = _run_script(VOLUME_FROM_WORKSPACE)
    assert 'Add-Content -Path $env:GITHUB_ENV -Value "TMP=' in script
    assert 'Add-Content -Path $env:GITHUB_ENV -Value "TEMP=' in script
    assert _run_index(VOLUME_FROM_WORKSPACE) < _run_index(GATE_BODIES[0])


def test_the_checkout_is_proved_to_carry_no_cr_afterwards():
    """Prevents: the bytes arriving mangled with no stated precondition."""
    script = _run_script(LEDGER_PATH)
    assert "[char]13" in script
    assert _run_index(LEDGER_PATH) > _uses_index("actions/checkout")
