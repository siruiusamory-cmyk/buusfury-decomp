from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from tools.quality import readability

COMMENT = "# alpha bravo charlie delta echo"
CODE = "value = 1"


def tree(root: Path, files: Mapping[str, str]) -> Path:
    for name, text in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    return root


def source(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def share_for(name: str, text: str, *, changed: Sequence[int] | None = ()) -> readability.FileReport:
    return readability.analyze_file(
        name, text, readability.PYTHON, changed_lines=changed
    )


def result_with(rows: Sequence[readability.CommentShare]) -> readability.ScanResult:
    return readability.ScanResult(
        selector="all",
        revision=None,
        files_scanned=1,
        total_lines=10,
        comment_lines=0,
        findings=(),
        suppressed=(),
        exceptions=readability.ExceptionTable(),
        unused_exceptions=(),
        comment_share=tuple(rows),
    )


def row(name: str, *, added: int, commented: int) -> readability.CommentShare:
    return readability.CommentShare(
        path=name,
        lines=added,
        comment_lines=commented,
        changed_lines=added,
        changed_comment_lines=commented,
    )


def git(root: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=probe@example.invalid",
            "-c",
            "user.name=probe",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.autocrlf=false",
            *args,
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def test_counts_comment_docstring_and_span_lines_for_one_file():
    text = source(
        '"""Module summary."""',
        "",
        COMMENT,
        "",
        "def solve(value):",
        '    """Alpha',
        "    bravo",
        '    charlie."""',
        "    total = value",
        "    return total",
    )
    report = share_for("tools/demo/mod.py", text)
    assert report.lines == 10
    assert report.comment_lines == 1
    assert report.docstring_lines == 4
    share = readability.CommentShare(
        path=report.path,
        lines=report.lines,
        comment_lines=report.comment_lines + report.docstring_lines,
        changed_lines=report.changed_lines,
        changed_comment_lines=report.changed_comment_lines,
    )
    assert share.percent == pytest.approx(50.0)


def test_a_long_user_facing_string_constant_is_not_charged_as_a_docstring(tmp_path):
    help_text = [f"line {index} of the help text" for index in range(30)]
    text = source(
        "HELP_TEXT = (",
        '    """',
        *[f"    {line}" for line in help_text],
        '    """',
        ")",
        "",
        "def solve(value):",
        "    return value",
    )
    tree(tmp_path, {"tools/demo/mod.py": text})
    report = share_for("tools/demo/mod.py", text)
    assert report.lines == 37
    assert report.comment_lines == 0
    assert report.docstring_lines == 0
    result = readability.scan_paths(
        ["tools/demo/mod.py"], root=tmp_path, selector="changed", changed={"tools/demo/mod.py": None}
    )
    assert result.hard_findings == ()
    assert result.comment_share[0].changed_percent == 0.0
    assert result.comment_share[0].percent == 0.0


def test_a_change_that_adds_no_comment_is_measured_on_the_added_lines_only(tmp_path):
    text = source(*(COMMENT for _ in range(19)), CODE)
    tree(tmp_path, {"tools/demo/mod.py": text})
    result = readability.scan_paths(
        ["tools/demo/mod.py"], root=tmp_path, selector="changed", changed={"tools/demo/mod.py": {20}}
    )
    assert result.hard_findings == ()
    share = result.comment_share[0]
    assert share.changed_lines == 1
    assert share.changed_comment_lines == 0
    assert share.percent == pytest.approx(95.0)


def test_a_change_that_adds_mostly_comments_is_failed_and_named(tmp_path):
    text = source(CODE, *(COMMENT for _ in range(12)))
    tree(tmp_path, {"tools/demo/mod.py": text})
    added = set(range(2, 14))
    result = readability.scan_paths(
        ["tools/demo/mod.py"], root=tmp_path, selector="changed", changed={"tools/demo/mod.py": added}
    )
    found = [f for f in result.hard_findings if f.signal == "comment_share"]
    assert len(found) == 1
    assert found[0].path == "tools/demo/mod.py"
    assert found[0].line == 2
    assert found[0].severity == readability.HARD
    assert "12 of 12 added lines" in found[0].text
    assert result.comment_share[0].changed_percent == pytest.approx(100.0)


def test_a_whole_new_file_is_measured_on_every_line(tmp_path):
    text = source(
        "def solve(value):",
        '    """Alpha bravo charlie delta echo."""',
        "    return value",
    )
    tree(tmp_path, {"tools/demo/mod.py": text})
    result = readability.scan_paths(
        ["tools/demo/mod.py"], root=tmp_path, selector="changed", changed={"tools/demo/mod.py": None}
    )
    assert result.comment_share[0].changed_lines == 3
    assert result.comment_share[0].changed_percent == pytest.approx(100 * 1 / 3)
    assert [f.signal for f in result.hard_findings] == ["comment_share"]


def test_the_median_of_the_added_line_shares_gates_the_run(monkeypatch, capsys):
    monkeypatch.setattr(
        readability,
        "scan_repository",
        lambda **_kwargs: result_with(
            [row("tools/a.py", added=10, commented=0), row("tools/b.py", added=10, commented=0)]
        ),
    )
    assert readability.main(["--all"]) == 0

    monkeypatch.setattr(
        readability,
        "scan_repository",
        lambda **_kwargs: result_with(
            [row("tools/a.py", added=10, commented=5), row("tools/b.py", added=10, commented=5)]
        ),
    )
    assert readability.main(["--all"]) == 1
    out = capsys.readouterr().out
    assert "added-lines median .......... 50.0%" in out
    assert readability.main(["--all", "--no-fail"]) == 0


def test_the_real_diff_measures_added_lines_and_whole_new_files(tmp_path):
    if shutil.which("git") is None:
        pytest.skip("git is not available on PATH")
    tree(
        tmp_path,
        {"tools/demo/mod.py": source(*(COMMENT for _ in range(19)), CODE)},
    )
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tools/demo/mod.py")
    git(tmp_path, "commit", "-q", "-m", "baseline")

    (tmp_path / "tools/demo/mod.py").write_text(
        source(*(COMMENT for _ in range(19)), CODE, "other = 2"),
        encoding="utf-8",
        newline="\n",
    )
    after_code = readability.scan_repository(selector="changed", revision="HEAD", root=tmp_path)
    assert after_code.hard_findings == ()
    assert after_code.comment_share[0].changed_lines == 1
    assert after_code.comment_share[0].changed_percent == pytest.approx(0.0)

    tree(
        tmp_path,
        {
            "tools/demo/new.py": source(
                "def solve(value):",
                '    """Alpha bravo charlie delta echo."""',
                "    return value",
            )
        },
    )
    after_new = readability.scan_repository(selector="changed", revision="HEAD", root=tmp_path)
    found = [f for f in after_new.hard_findings if f.signal == "comment_share"]
    assert [f.path for f in found] == ["tools/demo/new.py"]
    assert found[0].line == 1
    rows = {item.path: item for item in after_new.comment_share}
    assert rows["tools/demo/new.py"].changed_lines == 3
    assert rows["tools/demo/mod.py"].changed_comment_lines == 0


def test_tools_dragonbyte_is_out_of_scope_and_named(tmp_path):
    tree(
        tmp_path,
        {
            "tools/dragonbyte/shell.py": source(COMMENT, COMMENT, CODE),
            "tools/demo/mod.py": source(COMMENT, CODE),
        },
    )
    result = readability.scan_paths(
        ["tools/dragonbyte/shell.py", "tools/demo/mod.py"], root=tmp_path
    )
    assert [item.path for item in result.comment_share] == ["tools/demo/mod.py"]
    summary = readability.render_summary(result)
    assert "tools/dragonbyte" in summary
    assert "out of scope" in summary


def test_an_over_bar_added_file_makes_the_gate_exit_non_zero(tmp_path, monkeypatch, capsys):
    if shutil.which("git") is None:
        pytest.skip("git is not available on PATH")
    tree(tmp_path, {"tools/demo/mod.py": source(CODE)})
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tools/demo/mod.py")
    git(tmp_path, "commit", "-q", "-m", "baseline")
    tree(
        tmp_path,
        {
            "tools/demo/new.py": source(
                "def solve(value):",
                '    """Alpha bravo charlie delta echo."""',
                "    return value",
            )
        },
    )
    real = readability.scan_repository
    monkeypatch.setattr(
        readability, "scan_repository", lambda **kwargs: real(root=tmp_path, **kwargs)
    )
    assert readability.main(["--changed", "HEAD"]) == 1
    out = capsys.readouterr().out
    assert "tools/demo/new.py" in out
    assert "HARD: comment_share" in out


def test_the_document_carries_every_file_share_the_aggregate_and_the_median(tmp_path):
    tree(tmp_path, {"tools/demo/mod.py": source(COMMENT, COMMENT, CODE, CODE)})
    result = readability.scan_paths(
        ["tools/demo/mod.py"],
        root=tmp_path,
        selector="changed",
        changed={"tools/demo/mod.py": {3, 4}},
    )
    document = json.loads(readability.to_json(result))
    assert document["comment_share"]["aggregate_percent"] == 50.0
    assert document["comment_share"]["median_percent"] == 0.0
    assert document["comment_share"]["out_of_scope"] == ["tools/dragonbyte"]
    assert document["comment_share"]["files"] == [
        {
            "path": "tools/demo/mod.py",
            "lines": 4,
            "comment_and_docstring_lines": 2,
            "percent": 50.0,
            "changed_lines": 2,
            "changed_comment_and_docstring_lines": 0,
            "changed_percent": 0.0,
        }
    ]
