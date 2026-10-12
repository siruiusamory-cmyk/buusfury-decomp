"""The developer tools' guards: citations, commit messages, the probe worktree.

Each tool exists because a measured failure cost a session, so each guard drives its
own failure rather than asserting that the tool exists.

TWO LAYERS, because CI is Linux and always will be. A `.ps1` tool cannot execute
there, so its behavioural guard skips on a host without PowerShell and a TEXT guard
(a pure-Python assertion over the script's own bytes, the pattern RETRO-ENV-001
established in tests/unit/test_ticket_worktree_setup.py) runs everywhere and pins
the invariant the behaviour depends on. The behavioural proof for a `.ps1` tool is
a Windows run, recorded in the ticket's report; the text guard is the regression
net in CI. The Python tools (check_citations, merge_mr, review_queue_index) keep
real behaviour tests that run on Linux, and there is no skip in them.

The skip is proved rather than assumed: test_the_behavioural_powershell_tests_skip
makes the lookup absent and asserts the tests SKIP instead of failing.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.dev import check_citations as cc  # noqa: E402
from tools.dev import merge_mr as mm  # noqa: E402

COMMIT_MSG = REPOSITORY_ROOT / "tools" / "dev" / "commit_msg.ps1"
PROBE_WORKTREE = REPOSITORY_ROOT / "tools" / "dev" / "probe_worktree.ps1"
SWEEP = REPOSITORY_ROOT / "tools" / "dev" / "worktree_owners.ps1"
CUTTER = REPOSITORY_ROOT / "scripts" / "new-ticket-worktree.ps1"


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _require_powershell() -> str:
    """The host, or a named skip. CI is Linux, where a `.ps1` cannot run."""
    shell = _powershell()
    if shell is None:
        pytest.skip(
            "no PowerShell host on this platform, so the .ps1 tool cannot be "
            "executed; the text guards in this file hold its invariants in CI and "
            "the behaviour is proved on Windows"
        )
    return shell


def _require_windows_powershell() -> str:
    """Windows PowerShell 5.1 by name, for the one test about ITS BOM behaviour.

    `pwsh` is not the same shell: it has `-Encoding utf8NoBOM` and its `utf8` writes
    no byte-order mark, so a probe that preferred `pwsh` would find no failure to
    reproduce and fail its own assertion on a machine that has it.
    """
    shell = shutil.which("powershell.exe") or shutil.which("powershell")
    if shell is None or "powershell.exe" not in Path(shell).name.lower():
        pytest.skip(
            "Windows PowerShell 5.1 is not on this platform; this test asserts the "
            "BOM behaviour of that shell specifically"
        )
    return shell


def _require_python() -> None:
    if not Path(sys.executable).exists():
        pytest.skip("this interpreter is not on disk, so it cannot be run as a child")


# --- B4: check_citations -----------------------------------------------------


@pytest.fixture
def cited_tree(tmp_path: Path) -> dict:
    """A tree with one known-good citation, one moved symbol and one orphan."""
    root = tmp_path / "root"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "alpha.py").write_text(
        "\n".join(
            [
                "def first():",
                "    return 1",
                "",
                "def keep_me():",
                "    return 2",
                "",
                "# padding",
                "def last():",
                "    return 3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "pkg" / "beta.py").write_text("X = 1\n", encoding="utf-8")
    return {"root": root}


def test_a_citation_whose_symbol_is_on_the_line_resolves(cited_tree):
    text = "`pkg/alpha.py:4` `keep_me` is defined there.\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["RESOLVES"], findings


def test_a_citation_whose_symbol_moved_reports_the_new_line(cited_tree):
    """The measured case: the debt node's site had moved and nothing said so."""
    text = "`pkg/alpha.py:2` `keep_me` is defined there.\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["MOVED"], findings
    assert "4" in findings[0]["why"], findings


def test_a_symbol_nowhere_in_the_file_is_an_orphan(cited_tree):
    text = "`pkg/alpha.py:2` `gone_forever` was defined there.\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["ORPHAN"], findings


def test_a_line_past_the_end_of_the_file_is_an_orphan(cited_tree):
    """The ledger row's shape: three citations in a file that has since grown."""
    text = "`pkg/alpha.py:7849` names the `_saved` state.\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["ORPHAN"], findings
    assert "past the end" in findings[0]["why"], findings


def test_a_path_that_does_not_exist_is_an_orphan(cited_tree):
    text = "`workbench/app.py:251-256` `on_project_mutated`\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["ORPHAN"], findings
    assert "no such file" in findings[0]["why"], findings


def test_a_bare_filename_resolves_when_the_tree_has_exactly_one(cited_tree):
    text = "`beta.py:1` `X` is set there.\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["RESOLVES"], findings


def test_a_citation_with_no_named_symbol_only_checks_the_extent(cited_tree):
    """`editors.py:345-378` names nothing, so the answer is the extent alone."""
    text = "`pkg/alpha.py:1-9` is the whole file.\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["RESOLVES"], findings
    assert "no symbol named" in findings[0]["why"], findings


def test_prose_that_is_not_a_citation_is_not_reported(cited_tree):
    text = "The player is at gba:1 and the maps:440 count is published.\n"
    assert cc.check(text, cited_tree["root"], cited_tree["root"]) == []


def test_a_release_word_in_backticks_is_not_read_as_a_symbol(cited_tree):
    """`Merged` is prose, not an identifier: reading it as one invented findings."""
    text = "`pkg/alpha.py:1` `Merged`\n"
    findings = cc.check(text, cited_tree["root"], cited_tree["root"])
    assert [f["state"] for f in findings] == ["RESOLVES"], findings


def test_the_checker_exits_non_zero_for_orphans_only_when_asked(tmp_path: Path):
    _require_python()
    document = tmp_path / "prose.md"
    document.write_text("`missing/nothing.py:3` `gone`\n", encoding="utf-8")
    quiet = subprocess.run(
        [sys.executable, "-m", "tools.dev.check_citations", str(document)],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    failing = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.dev.check_citations",
            "--fail-on-orphan",
            str(document),
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    assert quiet.returncode == 0, quiet.stdout + quiet.stderr
    assert failing.returncode == 1, failing.stdout + failing.stderr
    assert "ORPHAN" in failing.stdout


def test_the_checker_requires_an_explicit_target():
    _require_python()
    result = subprocess.run(
        [sys.executable, "-m", "tools.dev.check_citations"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "a whole-tree default is the noise this avoids"


# --- B9a: commit_msg.ps1 -----------------------------------------------------


def _commit_msg(*args: str) -> subprocess.CompletedProcess:
    shell = _require_powershell()
    return subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(COMMIT_MSG), *args],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )


def test_the_message_writer_writes_no_byte_order_mark():
    """`Set-Content -Encoding utf8` writes one; it has broken line 1 before."""
    _require_powershell()
    message = 'Subject with "quotes" and an apostrophe: it does not split'
    result = _commit_msg("-Message", message, "-NoCommit")
    assert result.returncode == 0, result.stdout + result.stderr
    path = Path(result.stdout.split("message written: ", 1)[1].split(" (no BOM", 1)[0])
    try:
        raw = path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), raw[:3]
        assert raw.decode("utf-8") == message, (
            "the message must survive verbatim: quotes, apostrophe and all")
    finally:
        path.unlink(missing_ok=True)


def test_the_writer_refuses_an_empty_message():
    _require_powershell()
    for empty in ("", "   "):
        result = _commit_msg("-Message", empty, "-NoCommit")
        assert result.returncode != 0, result.stdout + result.stderr
        assert "empty" in (result.stdout + result.stderr)


def test_the_no_bom_claim_is_driven_to_failure():
    """The premise of the tool, watched failing: `utf8` writes the marker.

    Same shape as the retro's measurement: write the same message the other way and
    read the first three bytes. Windows PowerShell 5.1 by name, because `pwsh`'s
    `utf8` writes no mark and would find nothing to reproduce.
    """
    shell = _require_windows_powershell()
    target = Path(tempfile.gettempdir()) / "dev-tools-test-bom.txt"
    script = target.with_suffix(".ps1")
    script.write_text(
        f"Set-Content -LiteralPath '{target}' -Value 'subject' -Encoding utf8\n",
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert target.read_bytes().startswith(b"\xef\xbb\xbf"), (
            "the failure the tool exists to prevent did not reproduce, so the "
            "no-BOM guard proves nothing")
    finally:
        target.unlink(missing_ok=True)
        script.unlink(missing_ok=True)


# --- the .ps1 invariants, as TEXT (this is what runs in Linux CI) -------------


def test_the_message_writer_keeps_the_no_bom_spelling():
    """The bytes-level invariant a Linux runner can still check.

    `[System.IO.File]::WriteAllText` with `UTF8Encoding($false)` is the whole
    mechanism. `Set-Content -Encoding utf8` appears ONCE, in the comment that names
    the defect: an executable occurrence is what the guard forbids, so the assertion
    is on the argument form rather than on the words.
    """
    text = COMMIT_MSG.read_text(encoding="utf-8")
    assert "[System.IO.File]::WriteAllText($MessageFile, $Message" in text
    assert "New-Object System.Text.UTF8Encoding($false)" in text
    assert "-LiteralPath $MessageFile -Value" not in text
    assert re.search(r"^\s*Set-Content[^\n]*-Encoding\s+utf8\s*$", text, re.M) is None
    assert "-Encoding utf8NoBOM" not in text
    assert "throw 'commit_msg.ps1: the message is empty" in text


def test_the_bom_failure_probe_names_the_shell_whose_utf8_writes_a_mark():
    """`pwsh` is not that shell, so a probe that preferred it would fail itself."""
    text = Path(__file__).read_text(encoding="utf-8")
    assert 'shutil.which("powershell.exe")' in text


def test_the_sweep_keeps_the_clean_filter_and_the_three_classes():
    """`--stdin` skips the clean filter and made every file look `authored`."""
    text = SWEEP.read_text(encoding="utf-8")
    # The path form applies the clean filter; the piped form does not.
    assert "hash-object -- $relative" in text
    assert "hash-object --stdin" not in text
    for classification in ("carries-master", "authored", "conflicted"):
        assert f"'{classification}'" in text
    assert "'cat-file', '-e'" in text


def test_the_cutter_ends_with_its_own_exit_code():
    assert CUTTER.read_text(encoding="utf-8").rstrip().endswith("exit 0")


def test_the_probe_refuses_with_both_digests():
    text = PROBE_WORKTREE.read_text(encoding="utf-8")
    assert "Get-FileHash -Algorithm SHA256 -LiteralPath" in text
    assert "source sha256" in text
    assert "copy   sha256" in text
    assert "MISMATCH" in text
    assert "exit 3" in text


@pytest.mark.skipif(
    _powershell() is not None,
    reason="the skip path is only reachable on a host without PowerShell",
)
def test_every_powershell_behavioural_guard_skips_without_a_host(monkeypatch):
    """Prove the skip, not just write it: remove the lookup and assert SKIP.

    Without this, a wrong edit to the skip helper would fail on Linux CI and pass
    on this machine, which is the worst direction. With it, the Linux path is
    exercised here.
    """
    monkeypatch.setattr(shutil, "which", lambda name, *args, **kwargs: None)
    assert _powershell() is None
    for call in (
        _require_powershell,
        _require_windows_powershell,
    ):
        with pytest.raises(pytest.skip.Exception) as caught:
            call()
        assert "no PowerShell host" in str(caught.value) or "Windows PowerShell" in str(
            caught.value
        )


def test_the_launcher_file_declares_the_same_skip_shape():
    """The launcher's guard must skip rather than fail on a host without PowerShell."""
    text = (REPOSITORY_ROOT / "tests" / "unit" / "test_mgba_extra_script.py").read_text(
        encoding="utf-8"
    )
    assert "def _require_host() -> str:" in text
    assert "pytest.skip(" in text[text.index("def _require_host") : text.index("def test_omitting")]
    assert "if shutil.which(\"pwsh\") is None and shutil.which(\"powershell\") is None:" in text


SKIP_PLUGIN = """
import shutil as _shutil

_real_which = _shutil.which


def _no_powershell(name, *args, **kwargs):
    if str(name).lower() in {"pwsh", "powershell", "powershell.exe"}:
        return None
    return _real_which(name, *args, **kwargs)


_shutil.which = _no_powershell
"""


def test_the_behavioural_powershell_tests_skip_rather_than_fail(tmp_path: Path):
    """The Linux path, exercised here: make the lookup absent and run them.

    A real subprocess with `shutil.which` neutered is the only way to see the skip
    happen, because these tests find a host on this machine. Without this, the skip
    could be broken for months and only Linux CI would know.
    """
    _require_python()
    plugin = tmp_path / "no_powershell.py"
    plugin.write_text(SKIP_PLUGIN, encoding="utf-8")
    nodes = [
        "tests/unit/test_dev_tools.py::test_the_message_writer_writes_no_byte_order_mark",
        "tests/unit/test_dev_tools.py::test_the_writer_refuses_an_empty_message",
        "tests/unit/test_dev_tools.py::test_the_probe_worktree_copies_and_verifies_when_the_bytes_match",
    ]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            *nodes,
            "-q",
            "-p",
            "no:cacheprovider",
            "--no-header",
            "-p",
            "no_powershell",
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "3 skipped" in output, output
    # pytest prints "reported, never failed" in every summary, so the check is for a
    # FAILED node id rather than for the word.
    assert "FAILED " not in output, output
    assert "ERROR " not in output, output



# --- B5: the QA probe's --rom flag -------------------------------------------


def test_the_qa_probe_resolves_a_named_rom_without_reading_an_image(tmp_path: Path):
    """A worktree has no `roms/`, so the probe has to be told where the image is.

    No image is opened: the flag's contract is the resolved path, which the harness
    only ever reads when a state runs.
    """
    image = tmp_path / "some-image.gba"
    image.write_bytes(b"not really a rom, and never read")
    sys.path.insert(0, str(REPOSITORY_ROOT))
    from tools.qa import visual_pass_capture as vpc

    original = vpc.ROM
    try:
        assert vpc.main(["--rom", str(image), "--list"]) == 0
        assert vpc.ROM == image
    finally:
        vpc.ROM = original


def test_the_qa_probe_refuses_a_rom_path_that_is_not_a_file(tmp_path: Path, capsys):
    from tools.qa import visual_pass_capture as vpc

    # argparse's own error path: it prints the refusal and exits 2.
    with pytest.raises(SystemExit) as excinfo:
        vpc.main(["--rom", str(tmp_path / "absent.gba"), "--list"])
    assert excinfo.value.code == 2
    assert "--rom names no file" in capsys.readouterr().err


def test_the_qa_probe_still_defaults_to_the_env_override():
    """The env override is the half that already existed; the flag is the other."""
    source = (REPOSITORY_ROOT / "tools" / "qa" / "visual_pass_capture.py").read_text(
        encoding="utf-8"
    )
    assert '"DBZ_QA_ROM"' in source
    assert '"DBZ_QA_ATLAS_DIR"' in source
    assert "ROM = args.rom" in source


# --- B7: the review-queue index ----------------------------------------------


def test_the_review_queue_index_is_read_only_over_the_queue(tmp_path: Path):
    """It lives outside the repository, so this is the only guard it can have.

    The queue is redirected to a fixture directory: the real one belongs to other
    lanes and must not be read or written by a test.
    """
    queue = tmp_path / "review-queue"
    (queue / "requests").mkdir(parents=True)
    (queue / "results").mkdir()
    (queue / "claimed").mkdir()
    (queue / "requests" / "TICKET-001-20261012-010000.json").write_text(
        json.dumps(
            {
                "review_id": "TICKET-001-20261012-010000",
                "ticket": "TICKET-001",
                "review_sha": "a" * 40,
                "worktree": r"C:\worktrees\example",
            }
        ),
        encoding="utf-8",
    )
    (queue / "claimed" / "TICKET-001-20261012-010000").write_text("", encoding="utf-8")
    (queue / "results" / "TICKET-001-20261012-010000.md").write_text("PASS\n", encoding="utf-8")
    before = {
        p.relative_to(queue): p.read_bytes()
        for p in queue.rglob("*")
        if p.is_file()
    }
    from tools.dev import review_queue_index as rqi

    report = rqi.build(queue)
    assert [row["review_id"] for row in report["requests"]] == ["TICKET-001-20261012-010000"]
    row = report["requests"][0]
    assert row["claimed"] is True
    assert row["verdict"] == "PASS"
    assert row["age_hours"] is not None
    after = {
        p.relative_to(queue): p.read_bytes()
        for p in queue.rglob("*")
        if p.is_file()
    }
    assert before == after, "the index must not write into the queue"


def test_the_review_queue_index_default_path_is_outside_the_repository():
    from tools.dev import review_queue_index as rqi

    assert "review-queue" in str(rqi.DEFAULT_QUEUE)
    assert REPOSITORY_ROOT not in rqi.DEFAULT_QUEUE.parents


def test_the_queue_verdict_is_the_last_line_not_the_first_word(tmp_path: Path):
    """The reviewer's bite: prose saying PASS above a BLOCKED verdict read as PASS.

    Every result file in this project ends with its verdict line, so that line is
    the answer and nothing above it is.
    """
    from tools.dev import review_queue_index as rqi

    result = tmp_path / "TICKET-001-20261012-010000.md"
    result.write_text(
        "- SC1: the earlier round PASSed on a different SHA\n"
        "- SC2: this one did not\n"
        "\n"
        "BLOCKED\n",
        encoding="utf-8",
    )
    assert rqi.verdict_of(result) == "BLOCKED"
    result.write_text("PASS\n", encoding="utf-8")
    assert rqi.verdict_of(result) == "PASS"
    assert rqi.verdict_of(None) is None


def test_a_negative_age_is_labelled_not_printed_bare():
    from tools.dev import review_queue_index as rqi

    assert rqi.age_label(2.5) == "2.5h"
    assert rqi.age_label(None) == "?"
    label = rqi.age_label(-1.5)
    assert label.startswith("in the future")
    assert "-1.5h" not in label


# --- B9b: the pinned-SHA merge wrapper ---------------------------------------


class _FakeApi:
    """A Merge API whose answers are scripted, so no MR is ever touched.

    `merges` is one entry per merge call: the return code and text it reports. The
    state it reports is computed the way GitLab's would be - a merge that lands
    moves the MR to `merged` and fills `merge_commit_sha` - so the wrapper's
    no-effect detection is exercised against a real state transition.

    `closes_on` moves the MR to `closed` instead, which is the shape that must NOT
    count as a merge, and `moves_head_after` repoints the MR's head after the
    wrapper's first read, which is what a rebase under a frozen candidate does.
    """

    def __init__(
        self,
        sha: str,
        merges: list[tuple[int, str]],
        lands_on: list[int],
        closes_on: list[int] | None = None,
        moves_head_after: int | None = None,
    ):
        self.state = {"state": "opened", "sha": sha, "merge_commit_sha": None}
        self.calls: list[list[str]] = []
        self.merges = merges
        self.lands_on = lands_on
        self.closes_on = closes_on or []
        self.moves_head_after = moves_head_after
        self.merge_number = 0
        self.api_calls = 0

    def project_api(self, project: str, path: str):
        self.calls.append(["api", path])
        self.api_calls += 1
        if self.moves_head_after is not None and self.api_calls == self.moves_head_after:
            # One-shot: the head moves ON this read and stays moved, which is what a
            # rebase under a frozen candidate does between two reads.
            self.state = {**self.state, "sha": "b" * 40}
        return subprocess.CompletedProcess(
            ["glab", "api", path], 0, json.dumps(self.state), ""
        )

    def merge(self, mr: str, project: str, sha: str):
        # The wrapper must carry the pinned SHA into the call, so the stub refuses a
        # merge for a SHA the MR is not at: a call without the SHA cannot be checked.
        self.calls.append(["merge", mr, sha])
        if sha != self.state["sha"]:
            return subprocess.CompletedProcess(
                ["glab", "mr", "merge", mr], 1, "", "the head does not match --sha"
            )
        self.merge_number += 1
        index = self.merge_number - 1
        returncode, text = self.merges[min(index, len(self.merges) - 1)]
        if self.merge_number in self.lands_on:
            self.state = {
                "state": "merged",
                "sha": self.state["sha"],
                "merge_commit_sha": "f" * 40,
            }
        if self.merge_number in self.closes_on:
            self.state = {**self.state, "state": "closed"}
        return subprocess.CompletedProcess(["glab", "mr", "merge", mr], returncode, text, text)


SHA = "a" * 40


def _fake(merges, lands_on, **kwargs) -> _FakeApi:
    return _FakeApi(SHA, merges, lands_on, **kwargs)


def test_a_merge_that_lands_is_reported_merged_even_when_glab_exits_non_zero():
    """The push-exits-1 pattern: read the STATE, never the exit code alone."""
    api = _fake([(1, "error: exit status 1")], [1])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "merged", outcome.as_dict()
    assert len(outcome.attempts) == 1
    assert outcome.attempts[0].had_effect is True


def test_a_405_with_no_effect_is_retried_once_and_then_merged():
    """The memory store's reading, honoured: retry is allowed with no effect."""
    api = _fake([(1, "HTTP 405 Method Not Allowed"), (0, "merged")], [2])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "merged", outcome.as_dict()
    assert len(outcome.attempts) == 2
    assert outcome.attempts[0].had_effect is False
    assert outcome.attempts[1].had_effect is True


def test_a_405_that_recurs_refuses_and_names_both_readings():
    """The deterministic reading, assumed: it cannot mask a real failure."""
    api = _fake([(1, "HTTP 405 Method Not Allowed")] * 2, [])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert len(outcome.attempts) == 2, "at most one retry"
    assert outcome.attempts[1].error == "405 recurred"
    assert "deterministic" in outcome.detail
    assert "flake" in outcome.detail


def test_a_real_failure_with_no_effect_is_not_retried():
    api = _fake([(1, "remote: something went wrong")] * 3, [])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert len(outcome.attempts) == 1, "a real failure is never retried past itself"
    assert "no server-side effect" in outcome.detail


def test_a_pipeline_number_containing_405_is_not_a_405():
    """The reviewer's bite: `pipeline 4057 failed` earned a second merge attempt.

    Driven to failure by matching the number as a substring: this error text is a
    real failure and must be refused after ONE attempt.
    """
    api = _fake([(1, "pipeline 4057 failed")] * 3, [])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert len(outcome.attempts) == 1, "a substring is not an HTTP status"


def test_a_closed_mr_is_not_a_merge():
    """A move to closed or locked has no merge commit, so it is not an effect."""
    api = _fake([(1, "boom")], [], closes_on=[1])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert outcome.attempts[0].had_effect is False
    assert "no server-side effect" in outcome.detail


def test_a_head_that_moved_after_the_check_is_refused_before_the_retry():
    """The reviewer's bite: the stub moved the head and the wrapper merged anyway.

    The stub moves the head ON the read that follows the first failed attempt, which
    is the read the wrapper must perform before retrying. The merge call then carries
    a SHA the MR is not at, so without the re-check the retry lands.
    """
    api = _fake([(1, "HTTP 405 Method Not Allowed")] * 2, [], moves_head_after=3)
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert len(outcome.attempts) == 2, outcome.as_dict()
    assert outcome.attempts[1].error == "the MR's head is no longer the pinned SHA"
    assert "merged" != outcome.status


def test_a_head_that_moved_before_the_first_merge_is_refused_without_a_merge():
    """The same guard before the first attempt, driven from its own side."""
    api = _fake([(0, "merged")], [1], moves_head_after=2)
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert outcome.attempts[0].had_effect is False
    assert [call[0] for call in api.calls] == ["api", "api"], "no merge was attempted"


def test_success_reported_without_moving_the_mr_is_refused():
    """Exit 0 is not evidence: the MR state is."""
    api = _fake([(0, "merged")], [])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert "never merged" in outcome.detail


def test_a_sha_that_is_not_the_mr_head_is_refused_before_any_merge():
    api = _fake([(0, "merged")], [1])
    outcome = mm.merge("240", "b" * 40, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert outcome.attempts == []
    assert "not this MR's head" in outcome.detail


def test_the_wrapper_assumes_the_deterministic_reading_in_what_it_reports():
    outcome = mm.merge("240", SHA, _fake([(0, "merged")], []))
    assert outcome.reading_assumed == mm.DETERMINISTIC_READING
    assert "405" in mm.FLAKE_READING


def test_the_merge_call_carries_the_pinned_sha():
    """The pin is not only a pre-check: the merge request names the SHA too.

    Driven on the real `GlabApi` through its runner seam, because recording on the
    stub alone cannot fail: the command the wrapper BUILDS is the thing under test.
    """
    recorded: list[list[str]] = []
    api = mm.GlabApi(
        runner=lambda command: (
            recorded.append(list(command)) or subprocess.CompletedProcess(command, 0, "", "")
        )
    )
    api.merge("240", mm.DEFAULT_PROJECT, SHA)
    assert recorded == [["glab", "mr", "merge", "240", "--sha", SHA, "--yes"]], recorded


def test_the_docstring_names_the_exit_codes_the_code_returns():
    source = (
        REPOSITORY_ROOT / "tools" / "dev" / "merge_mr.py"
    ).read_text(encoding="utf-8")
    doc = " ".join(source[: source.index('"""', 3)].split())
    assert "Exit codes: 0 merged" in doc
    assert "3 refused" in doc
    assert "4 the pinned SHA is not the MR's head" in doc
    assert "--ticket" not in doc



# --- B8: probe_worktree.ps1 --------------------------------------------------


def _probe(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    shell = _require_powershell()
    return subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PROBE_WORKTREE), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=600,
    )


@pytest.fixture
def probe_repo(tmp_path: Path) -> dict:
    """A repository whose working tree holds a modified file to probe with."""
    _require_powershell()
    if shutil.which("git") is None:
        pytest.skip("git is required to build a probe worktree")
    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> None:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=300
        )
        assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"

    git("init", "-q", "--initial-branch=master")
    git("config", "user.email", "guard@example.invalid")
    git("config", "user.name", "guard")
    (root / "probe.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "helper.py").write_text("OTHER = 2\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    (root / "probe.py").write_text("VALUE = 2\n", encoding="utf-8")
    return {"root": root}


def test_the_probe_worktree_refuses_a_file_whose_copy_differs(probe_repo):
    """The measured failure: a redirect converted the bytes the probe ran.

    Driven on the real comparison: the probed tree holds different bytes for a
    named file than the source does, which is what the redirect produced, and the
    tool must refuse rather than report a result.
    """
    root = probe_repo["root"]
    probed = root / "probed"
    subprocess.run(
        ["git", "worktree", "add", "--detach", "--quiet", str(probed), "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    # One byte differs from the source's own file, exactly as a CRLF conversion did.
    (probed / "probe.py").write_bytes(b"VALUE = 3\n")
    result = _probe(
        "-Path", "probe.py", "-VerifyOnly", str(probed), "-CheckOnly", cwd=root
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "MISMATCH" in result.stdout.upper(), result.stdout + result.stderr
    assert "REFUSED" in result.stdout.upper(), result.stdout


def test_the_probe_worktree_copies_and_verifies_when_the_bytes_match(probe_repo):
    root = probe_repo["root"]
    result = _probe("-Path", "probe.py", "-CheckOnly", cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    # The full SHAs are printed, which is what makes the probe's provenance usable.
    assert "sha256" in result.stdout.lower()
    assert "probe.py" in result.stdout


def test_the_probe_worktree_is_tracked_in_its_own_launch_site_terms():
    """It starts no emulator, so it needs no identity gate; it must not look like one."""
    text = PROBE_WORKTREE.read_text(encoding="utf-8")
    assert "Start-Process" not in text
    assert "mGBA" not in text


def test_the_probe_worktree_leaves_the_caller_worktree_untouched(probe_repo):
    """A probe worktree is removed after the check, so nothing is left behind."""
    root = probe_repo["root"]
    before = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
    ).stdout
    result = _probe("-Path", "probe.py", "-CheckOnly", cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    after = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
    ).stdout
    assert before == after, "the probe worktree must be removed when the check ends"
    assert os.sep in str(root)
