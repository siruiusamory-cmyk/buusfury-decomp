"""Controls for the readability gate.

Two rules shape this file.

Every heuristic has a positive control (a synthetic file that triggers it and is
reported) and a negative control (a synthetic near-miss that must not be). The
near-misses are not invented: each one is the shape that actually produced a
false positive when the detector was first run over this tree.

No test names a forbidden term. Fixtures are built from the decoded table's own
samples, so the words live in one encoded place and a reader of this file cannot
mistake a fixture for residue. The last test in the file proves that.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path

import pytest

from tools.quality import readability

REPO_ROOT: Path = readability.REPO_ROOT
EXCEPTIONS_PATH: Path = REPO_ROOT / "config" / "readability_exceptions.json"

#: The exclusion list is a blind spot, so its size is pinned here rather than
#: left to whatever the module happens to contain.
EXPECTED_EXCLUSIONS = 2

#: A floor rather than an exact count: it asserts the scan reaches the source
#: rather than passing vacuously, and does not fail when a file is added.
MINIMUM_FILES_SCANNED = 400


# --- helpers ---------------------------------------------------------------


def findings(text: str, path: str = "synthetic.ts") -> tuple[readability.Finding, ...]:
    return readability.analyze_text(path, text)


def signals(text: str, path: str = "synthetic.ts") -> dict[str, readability.Finding]:
    return {finding.signal: finding for finding in findings(text, path)}


def sample(key: str) -> str:
    """A decoded term sample, so no fixture here spells a forbidden term."""
    entries = readability.term_entries(key)
    assert entries, key
    return entries[0].sample


@pytest.fixture(scope="module")
def real_scan() -> readability.ScanResult:
    return readability.scan_repository()


def synthetic_result(
    *findings_in: readability.Finding, blocked: str | None = None
) -> readability.ScanResult:
    return readability.ScanResult(
        selector="all",
        revision=None,
        files_scanned=1,
        total_lines=1,
        comment_lines=0,
        findings=tuple(findings_in),
        suppressed=(),
        exceptions=readability.ExceptionTable(),
        unused_exceptions=(),
        unreadable=(),
        blocked=blocked,
    )


HARD_FINDING = readability.Finding("probe.py", 4, "debug_residue", readability.HARD, "text")
ADVISORY_FINDING = readability.Finding(
    "probe.py", 9, "oversized_comment_block", readability.ADVISORY, "text"
)


# --- the encoded table -----------------------------------------------------


def test_the_encoded_table_decodes_to_a_non_empty_list():
    assert len(readability.TERM_TABLE) >= 10
    assert readability.TERM_KEYS
    for entry in readability.TERM_TABLE:
        assert entry.key in readability.TERM_KEYS
        assert entry.sample and entry.pattern


def test_every_decoded_sample_matches_its_own_pattern():
    for entry in readability.TERM_TABLE:
        assert entry.pattern.search(entry.sample), entry.key
        # The needle gates the pattern before it runs, so a needle that is not
        # in the sample would silently retire the term.
        assert entry.needle in entry.sample.lower(), entry.key


def test_a_value_built_from_the_decoded_table_is_reported():
    entry = readability.term_entries("provider-name")[0]
    assert [f.signal for f in findings(f"// written with {entry.sample} here\n")] == [
        "process_narration"
    ]


def test_the_module_never_spells_out_what_it_forbids():
    # The table is the only place these terms live, which is why this module is
    # on the self-exclusion list and why this assertion must hold.
    source = (REPO_ROOT / "tools/quality/readability.py").read_text(encoding="utf-8")
    for entry in readability.TERM_TABLE:
        assert entry.pattern.search(source) is None, entry.key


def test_this_test_file_never_names_a_forbidden_term():
    source = Path(__file__).read_text(encoding="utf-8")
    for entry in readability.TERM_TABLE:
        assert entry.pattern.search(source) is None, entry.key


# --- hard signal 1: development-process vocabulary -------------------------


def test_process_narration_positive_control():
    found = signals(f"// this was produced with help from {sample('provider-name')}\n")
    assert set(found) == {"process_narration"}
    assert found["process_narration"].severity == readability.HARD


@pytest.mark.parametrize(
    "line",
    [
        "// the debugger session records a gdb session id per run",
        "# a GUI session is restored from the project file",
        "// the build pipeline runs extract, then validate, then build",
    ],
)
def test_process_narration_ignores_ordinary_technical_senses(line):
    assert findings(line + "\n") == ()


def test_the_build_sense_guard_is_what_makes_that_true():
    entry = next(
        candidate
        for candidate in readability.term_entries("workflow-word")
        if candidate.guard == "build-pipeline"
    )
    guarded = f"// the {entry.sample} stage runs the build, then the extract\n"
    assert findings(guarded) == ()
    unguarded = f"// hand the {entry.sample} to the workers and wait\n"
    assert [f.signal for f in findings(unguarded)] == ["process_narration"]


def test_the_desktop_session_sense_guard_is_what_makes_that_true():
    entry = next(
        candidate
        for candidate in readability.term_entries("workflow-phrase")
        if candidate.guard == "gui-session"
    )
    assert findings(f"// the panel keeps its {entry.sample} across a click\n") == ()
    assert [
        f.signal for f in findings(f"// the run writes {entry.sample} to a file\n")
    ] == ["process_narration"]


def test_the_enemy_behaviour_sense_is_covered_by_a_written_exception(real_scan):
    # The real probe uses the abbreviation for the wolf's own controller. Without
    # the configured exception it is a hard finding; with it, the file is clean
    # and the suppression is counted rather than hidden.
    relative = "tools/runtime/p007_wolf_ai_trace.lua"
    source = REPO_ROOT / relative
    if not source.is_file():
        pytest.skip("the probe is not present in this checkout")
    plain = readability.analyze_text(relative, source.read_text(encoding="utf-8"))
    assert any(f.signal == "process_narration" for f in plain)
    assert [f for f in real_scan.findings if f.path == relative] == []
    assert [f for f in real_scan.suppressed if f.path == relative]


# --- hard signal 2: commented-out code -------------------------------------


def test_commented_out_code_positive_control():
    text = (
        "def run():\n"
        "    pass\n"
        "# result = compute(1)\n"
        "# if result:\n"
        "#     return result\n"
    )
    found = [f for f in findings(text, "synthetic.py") if f.signal == "commented_out_code"]
    assert len(found) == 1
    assert found[0].line == 3


@pytest.mark.parametrize(
    "text,suffix",
    [
        (
            "# ========================================\n"
            "# The next section explains what the resolver does, and why it refuses\n"
            "# a span from another profile before that span becomes a fact about it.\n"
            "# ========================================\n",
            "synthetic.py",
        ),
        # Real shape from the runtime probes: it looks like assignments, but every
        # line starts with a literal, which is not a statement.
        (
            "-- RUNTIME-PROVEN ADDRESSES (do NOT re-derive):\n"
            "--   0x03001980 = live MapEntry pointer. table base 0x0808E2E0, stride 0x38.\n"
            "--   0x03001C34 = the player slot, stored by 0x080109AA (080109E6 str r4,[r0]).\n"
            "--   0x03001A34 = the player-subclass selector, read at 08008DA6..08008DB0.\n",
            "synthetic.lua",
        ),
        (
            "# An empty *string* is checked before ``Path()`` sees it: ``Path(\"\")`` is\n"
            "# ``Path(\".\")``, which would otherwise be reported as a folder, not a\n"
            "# file - a true statement about the wrong thing.\n",
            "synthetic.py",
        ),
        ("# x = 1\n# y = 2\n\n", "synthetic.py"),
    ],
    ids=[
        "banners and prose",
        "a documented address table",
        "prose that quotes a call",
        "a run of three",
    ],
)
def test_commented_out_code_ignores_what_is_not_code(text, suffix):
    assert "commented_out_code" not in signals(text, suffix)


# --- hard signal 3: debug residue ------------------------------------------


def test_debug_residue_positive_control():
    assert "debug_residue" in signals("# TODO: remove this print(x) before release\n", "synthetic.py")


def test_an_ordinary_todo_is_debt_not_residue():
    found = signals("# TODO: split this table when the census lands\n", "synthetic.py")
    assert "debug_residue" not in found
    assert "todo_debt" in found


def test_a_fixme_naming_a_local_path_is_residue():
    text = '# FIXME: for now, the output lands in "D:\\scratch\\out"\n'
    assert "debug_residue" in signals(text, "synthetic.py")


# --- hard signal 4: proprietary and content patterns -----------------------


def test_a_user_profile_path_is_a_hard_finding():
    text = 'STATE = r"C:\\Users\\alice\\Documents\\roms\\canonical.gba"\n'
    assert "proprietary_user_path" in signals(text, "synthetic.py")


def test_a_placeholder_path_is_not_a_finding():
    text = 'STATE = r"%LOCALAPPDATA%\\roms\\canonical.gba"\n'
    assert findings(text, "synthetic.py") == ()


def test_an_absolute_commercial_rom_path_is_a_hard_finding():
    text = 'STATE = r"C:\\roms\\Dragon Ball Z - Buu\'s Fury (U).ss1"\n'
    assert "proprietary_rom_filename" in signals(text, "synthetic.py")


def test_the_documented_relative_rom_path_is_not_a_finding():
    # 99 tracked references use exactly this shape to name the user's own copy.
    text = 'CANONICAL = "roms/Dragon Ball Z - Buu\'s Fury (U).gba"\n'
    assert findings(text, "synthetic.py") == ()


def test_a_credential_shaped_value_is_a_hard_finding():
    text = 'api_key = "' + "0123456789abcdef" * 2 + '"\n'
    assert "credential_shaped" in signals(text, "synthetic.py")


def test_a_variable_named_like_a_credential_is_not_a_finding():
    assert findings("token = route[index]\n", "synthetic.lua") == ()


# --- advisories ------------------------------------------------------------


def test_oversized_comment_block_threshold_is_load_bearing():
    body = "# a note about the region\n"
    over = body * (readability.COMMENT_BLOCK_MAX_LINES + 1)
    under = body * readability.COMMENT_BLOCK_MAX_LINES
    assert "oversized_comment_block" in signals(over, "synthetic.py")
    assert "oversized_comment_block" not in signals(under, "synthetic.py")


def test_excessive_prose_threshold_is_load_bearing():
    prose = "# a sentence about what this file is for\n"
    over = prose * (readability.FILE_PROSE_MIN_LINES + 5)
    assert "excessive_prose" in signals(over, "synthetic.py")


def test_a_short_prose_file_is_not_reported():
    assert "excessive_prose" not in signals("# one line\n" * 10, "synthetic.py")


def test_placeholder_identifier_positive_and_negative():
    assert "placeholder_identifier" in signals("foo = 1\n", "synthetic.py")
    assert "placeholder_identifier" in signals("def f(tmp2):\n    return tmp2\n", "synthetic.py")
    assert "placeholder_identifier" not in signals("food = 1\n", "synthetic.py")


def test_deep_nesting_threshold_is_load_bearing():
    over = "".join("    " * depth + "if x:\n" for depth in range(1, readability.NESTING_MAX_DEPTH + 3))
    under = "".join(
        "    " * depth + "if x:\n" for depth in range(1, readability.NESTING_MAX_DEPTH + 1)
    )
    assert "deep_nesting" in signals(over, "synthetic.py")
    assert "deep_nesting" not in signals(under, "synthetic.py")


def test_giant_function_threshold_is_load_bearing():
    body = '    print("step")\n'
    over = "def big():\n" + body * (readability.FUNCTION_MAX_LINES + 5)
    under = "def small():\n" + body * 4
    assert "giant_function" in signals(over, "synthetic.py")
    assert "giant_function" not in signals(under, "synthetic.py")


def test_a_one_line_lua_definition_is_not_a_giant_function():
    text = "local function r8(a) return safe_read(emu.read8, a) end\n" + "local x = 1\n" * 200
    assert "giant_function" not in signals(text, "synthetic.lua")


def test_address_arithmetic_positive_and_negative():
    assert "duplicated_address_arithmetic" in signals("value = 0x08000000 + 0x1234\n")
    assert "duplicated_address_arithmetic" not in signals("value = GBA_ROM_BASE + 0x1234\n")
    assert "duplicated_address_arithmetic" not in signals("value = 0x104 - 0xC4\n")


def test_repeated_magic_value_threshold_is_load_bearing():
    literal = "0x082928DC"
    over = "".join(f"x = {literal}\n" for _ in range(readability.MAGIC_VALUE_MIN_COUNT + 1))
    under = "".join(f"x = {literal}\n" for _ in range(readability.MAGIC_VALUE_MIN_COUNT))
    assert "repeated_magic_value" in signals(over, "synthetic.py")
    assert "repeated_magic_value" not in signals(under, "synthetic.py")


def test_stale_temporary_positive_and_negative():
    assert "stale_temporary" in signals("# temporary hack until the parser lands\n", "synthetic.py")
    assert "stale_temporary" not in signals("# the row keeps its absent placeholder record\n")
    assert "stale_temporary" not in signals("# a temporary project directory for the run\n")


def test_a_provisional_marker_retires_the_wording():
    text = "# temporary bound, unmeasured; see CENSUS-004 for the derivation\n"
    assert "stale_temporary" not in signals(text, "synthetic.py")


# --- scope -----------------------------------------------------------------


def test_self_exclusion_is_exactly_the_detector_and_its_controls():
    assert len(readability.SELF_EXCLUSION) == EXPECTED_EXCLUSIONS
    assert {exclusion.path for exclusion in readability.SELF_EXCLUSION} == {
        "tools/quality/readability.py",
        "tests/unit/test_readability.py",
    }
    for exclusion in readability.SELF_EXCLUSION:
        assert exclusion.reason.strip()
        assert readability.is_scanned_path(exclusion.path) is False


@pytest.mark.parametrize(
    "path,expected",
    [
        ("tools/webfoot/rom.py", True),
        ("tools/runtime/p007_wolf_ai_trace.lua", True),
        ("tests/unit/test_binary.py", True),
        ("scripts/build-warprand.ps1", True),
        ("src/data/project.ts", True),
        ("build/generated.py", False),
        ("node_modules/pkg/index.js", False),
        ("docs/example.py", False),
        ("config/readability_exceptions.json", False),
        ("tools/webfoot/notes.md", False),
        ("tools/quality/readability.py", False),
    ],
)
def test_path_scope(path, expected):
    assert readability.is_scanned_path(path) is expected


@pytest.mark.parametrize(
    "path,marker",
    [
        ("synthetic.py", "#"),
        ("synthetic.ts", "//"),
        ("synthetic.mjs", "//"),
        ("synthetic.ps1", "#"),
        ("synthetic.lua", "--"),
    ],
)
def test_each_covered_language_is_scanned(path, marker):
    assert [f.signal for f in findings(f"{marker} {sample('product-name')} here\n", path)] == [
        "process_narration"
    ]


def test_scanning_never_executes_what_it_reads(tmp_path):
    victim = tmp_path / "dangerous.py"
    victim.write_text(
        "raise SystemExit('this must never run')\nimport os\nos.remove('x')\n",
        encoding="utf-8",
    )
    result = readability.scan_paths(["dangerous.py"], root=tmp_path)
    assert result.files_scanned == 1


# --- exceptions ------------------------------------------------------------


def test_every_configured_exception_has_a_reason_and_a_real_signal():
    table = readability.load_exceptions(EXCEPTIONS_PATH)
    assert table.invalid == ()
    assert table.rules
    for rule in table.rules:
        assert rule.reason.strip(), rule.path
        assert rule.signal in readability.SIGNAL_BY_ID


def test_every_configured_exception_path_matches_a_tracked_file():
    table = readability.load_exceptions(EXCEPTIONS_PATH)
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\n")
    for rule in table.rules:
        assert any(
            path and fnmatch.fnmatchcase(path, rule.path) for path in tracked
        ), rule.path


def test_a_reasonless_exception_is_rejected_not_honoured(tmp_path):
    path = tmp_path / "exceptions.json"
    path.write_text(
        json.dumps(
            {
                "exceptions": [
                    {"path": "tools/webfoot/rom.py", "signal": "process_narration", "reason": "  "}
                ]
            }
        ),
        encoding="utf-8",
    )
    table = readability.load_exceptions(path)
    assert table.rules == ()
    assert len(table.invalid) == 1


def test_a_malformed_exceptions_file_blocks_rather_than_silently_dropping_rules(tmp_path):
    path = tmp_path / "exceptions.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        readability.load_exceptions(path)


def test_an_unused_exception_is_reported():
    rule = readability.ExceptionRule(
        "tools/webfoot/rom.py", "credential_shaped", "invented for this test only"
    )
    table = readability.ExceptionTable(rules=(rule,))
    result = readability.scan_paths(["tools/webfoot/rom.py"], table=table)
    assert result.unused_exceptions == (rule,)


def test_a_load_bearing_exception_suppresses_exactly_its_own_hits(real_scan):
    table = readability.load_exceptions(EXCEPTIONS_PATH)
    assert real_scan.unused_exceptions == (), "a configured exception matched nothing"

    by_rule = {
        rule: [
            finding
            for finding in real_scan.suppressed
            if finding.signal == rule.signal and fnmatch.fnmatchcase(finding.path, rule.path)
        ]
        for rule in table.rules
    }
    load_bearing = [(rule, hits) for rule, hits in by_rule.items() if hits]
    assert load_bearing, "no configured exception changes the result"

    rule, hits = load_bearing[0]
    paths = sorted({finding.path for finding in hits})
    without = readability.ExceptionTable(
        rules=tuple(candidate for candidate in table.rules if candidate != rule)
    )

    with_rule = readability.scan_paths(paths, table=table)
    without_rule = readability.scan_paths(paths, table=without)

    assert with_rule.findings == ()
    assert len(without_rule.findings) == len(hits) >= 1
    for finding in without_rule.findings:
        assert finding.signal == rule.signal
        assert fnmatch.fnmatchcase(finding.path, rule.path)


# --- the real tree ---------------------------------------------------------


def test_the_real_tree_reports_nothing_in_the_shipping_toolkit(real_scan):
    offenders = [f for f in real_scan.hard_findings if f.path.startswith("tools/webfoot/")]
    assert offenders == []


def test_the_real_tree_scan_reaches_the_source_files(real_scan):
    assert real_scan.blocked is None
    assert real_scan.files_scanned >= MINIMUM_FILES_SCANNED
    assert real_scan.total_lines > 0


def test_findings_are_ordered_by_path_line_signal(real_scan):
    ordered = sorted(real_scan.findings, key=lambda f: (f.path, f.line, f.signal))
    assert list(real_scan.findings) == ordered


def test_only_configured_terms_are_suppressed(real_scan):
    for finding in real_scan.suppressed:
        assert finding.severity == readability.HARD


# --- reporting, determinism and exit codes ---------------------------------


def test_the_json_document_has_a_stable_schema(tmp_path):
    path = tmp_path / "report.json"
    assert readability.main(["--all", "--json", str(path), "--no-fail"]) == 0
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["schema"] == readability.SCHEMA_VERSION
    assert document["selector"] == "all"
    assert document["revision"] is None
    assert document["scan_roots"]
    assert set(document["metrics"]) >= {
        "files_scanned",
        "total_lines",
        "comment_lines",
        "hard_hits",
        "advisory_hits",
        "suppressed_hits",
    }
    assert document["thresholds"] == readability.THRESHOLDS
    assert document["findings"] == sorted(
        document["findings"], key=lambda f: (f["path"], f["line"], f["signal"])
    )
    assert document["metrics"]["files_scanned"] >= MINIMUM_FILES_SCANNED


def test_two_runs_write_byte_identical_json(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    assert readability.main(["--all", "--json", str(first), "--no-fail"]) == 0
    assert readability.main(["--all", "--json", str(second), "--no-fail"]) == 0
    assert first.read_bytes() == second.read_bytes()


def test_the_summary_says_advisories_never_change_the_exit_code(capsys):
    readability.main(["--all", "--no-fail"])
    out = capsys.readouterr().out
    assert "Advisories are a reading list and never change the exit code." in out
    assert "trends (counts only, not a score)" in out
    assert "per-signal counts" in out


def test_hard_findings_fail_the_run_and_no_fail_overrides_that(monkeypatch, capsys):
    monkeypatch.setattr(
        readability, "scan_repository", lambda **_kwargs: synthetic_result(HARD_FINDING)
    )
    assert readability.main(["--all"]) == 1
    assert readability.main(["--all", "--no-fail"]) == 0
    capsys.readouterr()


def test_advisories_alone_do_not_fail_the_run(monkeypatch, capsys):
    monkeypatch.setattr(
        readability, "scan_repository", lambda **_kwargs: synthetic_result(ADVISORY_FINDING)
    )
    assert readability.main(["--all"]) == 0
    capsys.readouterr()


def test_the_changed_selector_passes_its_revision_through(monkeypatch, capsys):
    seen: dict[str, object] = {}

    def fake_scan(**kwargs: object) -> readability.ScanResult:
        seen.update(kwargs)
        return synthetic_result()

    monkeypatch.setattr(readability, "scan_repository", fake_scan)
    assert readability.main(["--changed"]) == 0
    assert seen == {"selector": "changed", "revision": "HEAD"}
    assert readability.main(["--changed", "HEAD~3"]) == 0
    assert seen == {"selector": "changed", "revision": "HEAD~3"}
    assert readability.main(["--all"]) == 0
    assert seen == {"selector": "all", "revision": None}
    capsys.readouterr()


def test_a_blocked_scan_exits_two_with_one_line_of_reason(monkeypatch, capsys):
    monkeypatch.setattr(
        readability,
        "scan_repository",
        lambda **_kwargs: synthetic_result(blocked="git is not available on PATH"),
    )
    assert readability.main(["--all"]) == 2
    assert "BLOCKED: git is not available on PATH" in capsys.readouterr().out
    assert readability.main(["--all", "--no-fail"]) == 2
    capsys.readouterr()


def test_a_directory_that_is_not_a_checkout_is_blocked(tmp_path):
    result = readability.scan_repository(root=tmp_path)
    assert result.blocked is not None
    assert result.findings == ()
    assert result.files_scanned == 0


def test_missing_git_is_blocked(monkeypatch):
    monkeypatch.setattr(readability.shutil, "which", lambda _name: None)
    result = readability.scan_repository()
    assert result.blocked == "git is not available on PATH"


def test_the_exceptions_file_must_parse_or_the_scan_blocks(monkeypatch):
    monkeypatch.setattr(
        readability,
        "load_exceptions",
        lambda _path: (_ for _ in ()).throw(ValueError("broken")),
    )
    result = readability.scan_repository()
    assert result.blocked is not None
    assert "exceptions file unreadable" in result.blocked


# --- house style -----------------------------------------------------------


def test_the_quality_tooling_carries_no_em_dash():
    for relative in (
        "tools/quality/__init__.py",
        "tools/quality/readability.py",
        "tests/unit/test_readability.py",
        "config/readability_exceptions.json",
    ):
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        assert "\u2014" not in text, relative
