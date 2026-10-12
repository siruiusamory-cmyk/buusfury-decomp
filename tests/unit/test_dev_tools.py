"""The developer tools' guards: citations, commit messages, the probe worktree.

Each of the three tools exists because a measured failure cost a session, so each
guard drives its own failure rather than asserting that the tool exists:

* the citation checker is graded on all three answers it can give, in a fixture
  tree where the right answer is known, and on the exit code it only spends when
  asked (`--fail-on-orphan`);
* the commit-message writer is graded on the byte-level no-BOM claim, on a message
  carrying quotes and an apostrophe surviving VERBATIM, and on refusing an empty
  message - the same "write with `-Encoding utf8` and watch it fail" shape the
  retro used;
* the probe worktree copies named files into a detached worktree, hash-verifies
  each, and refuses when a byte differs. `git` and `powershell` are both required
  for that half; where a host is missing the check skips and names it.
"""

from __future__ import annotations

import json
import os
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


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


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
    result = subprocess.run(
        [sys.executable, "-m", "tools.dev.check_citations"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "a whole-tree default is the noise this avoids"


# --- B9a: commit_msg.ps1 -----------------------------------------------------


def _commit_msg(*args: str) -> subprocess.CompletedProcess:
    shell = _powershell()
    assert shell is not None
    return subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(COMMIT_MSG), *args],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
    )


def test_the_message_writer_writes_no_byte_order_mark():
    """`Set-Content -Encoding utf8` writes one; it has broken line 1 before."""
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
    for empty in ("", "   "):
        result = _commit_msg("-Message", empty, "-NoCommit")
        assert result.returncode != 0, result.stdout + result.stderr
        assert "empty" in (result.stdout + result.stderr)


def test_the_no_bom_claim_is_driven_to_failure():
    """The premise of the tool, watched failing: `utf8` writes the marker.

    Same shape as the retro's measurement: write the same message the other way
    and read the first three bytes.
    """
    shell = _powershell()
    assert shell is not None
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
                "worktree": r"C:\Dev\log1-remake-x",
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


# --- B9b: the pinned-SHA merge wrapper ---------------------------------------


class _FakeApi:
    """A Merge API whose answers are scripted, so no MR is ever touched.

    `merges` is one entry per merge call: the return code and text it reports. The
    state it reports is computed the way GitLab's would be - a merge that lands
    moves the MR to `merged` and fills `merge_commit_sha` - so the wrapper's
    no-effect detection is exercised against a real state transition.
    """

    def __init__(self, sha: str, merges: list[tuple[int, str]], lands_on: list[int]):
        self.state = {"state": "opened", "sha": sha, "merge_commit_sha": None}
        self.calls: list[list[str]] = []
        self.merges = merges
        self.lands_on = lands_on
        self.merge_number = 0

    def project_api(self, project: str, path: str):
        self.calls.append(["api", path])
        return subprocess.CompletedProcess(
            ["glab", "api", path], 0, json.dumps(self.state), ""
        )

    def merge(self, mr: str, project: str):
        self.calls.append(["merge", mr])
        self.merge_number += 1
        index = self.merge_number - 1
        returncode, text = self.merges[min(index, len(self.merges) - 1)]
        if self.merge_number in self.lands_on:
            self.state = {
                "state": "merged",
                "sha": self.state["sha"],
                "merge_commit_sha": "f" * 40,
            }
        return subprocess.CompletedProcess(["glab", "mr", "merge", mr], returncode, text, text)


SHA = "a" * 40


def _fake(merges, lands_on) -> _FakeApi:
    return _FakeApi(SHA, merges, lands_on)


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


def test_success_reported_without_moving_the_mr_is_refused():
    """Exit 0 is not evidence: the MR state is."""
    api = _fake([(0, "merged")], [])
    outcome = mm.merge("240", SHA, api)
    assert outcome.status == "refused", outcome.as_dict()
    assert "never moved" in outcome.detail


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


def test_the_wrapper_never_passes_an_unreviewed_sha():
    """The merge command carries the MR id only: the SHA check is before it."""
    api = _fake([(0, "merged")], [1])
    mm.merge("240", SHA, api)
    merge_calls = [call for call in api.calls if call[0] == "merge"]
    assert merge_calls == [["merge", "240"]]


# --- B8: probe_worktree.ps1 --------------------------------------------------


def _probe(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    shell = _powershell()
    assert shell is not None
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
