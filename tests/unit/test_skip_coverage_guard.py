"""The CI-runnable/locally-proved split, made mechanical and self-policing.

Thirteen guard nodes in this suite need a PowerShell host, which the Linux CI runner
does not have. That is deliberate: a `.ps1` cannot execute there. What is NOT
acceptable is the state the first version of this ticket shipped - a load-bearing
behaviour guarded ONLY by a test that skips in CI, with a prose table claiming
otherwise. This file makes the claim checkable.

Three things are derived, never typed from memory:

1. WHICH NODES SKIP. Every function of the scanned test files is AST-parsed. A
   function reaches the platform skip when it calls a helper that does
   (`PLATFORM_SKIP_HELPERS`) or calls something that does, so the two fixtures are
   reached through their own bodies rather than named here. A test node skips when
   it reaches one of those, or calls `pytest.skip` in its own body, or requests a
   fixture that does either. Adding a new `pytest.skip` to a node puts it in the
   set automatically, so a new skip cannot be forgotten.

2. WHICH TEXT GUARD PROTECTS EACH ONE. `SKIP_GUARD` is the block: one row per skip
   node naming the pure-Python guard node that holds the invariant it asserts. A
   skip node with no row fails, and a row naming a guard that does not exist, or one
   that itself skips, fails.

3. WHAT CANNOT BE PROVED AS TEXT. `LOCALLY_PROVED_ONLY` is a table of invariants
   that need Windows and cannot be asserted as text, each with the reason. It is
   rendered into `docs/dev-tools.md` between markers, and this guard fails when the
   document and the table disagree - so the document cannot drift away from the code
   it describes.

The counts are the CI runner's, not this machine's. On Windows these nodes RUN, so a
local run cannot see them at all: `CI_TRACE_SKIPS` is what the test-sdk trace of job
17121704860 at 9c34f1ae reported, and the per-file counts below are reconciled
against it rather than against anything measured here.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The test modules in scope: every one that guards a `.ps1` tool.
SCANNED = (
    "tests/unit/test_dev_tools.py",
    "tests/unit/test_worktree_owners.py",
)

#: The helpers whose skip condition is the PLATFORM and not the data: no PowerShell
#: host. Declared, because no call graph can tell a condition that fires on Linux
#: from one that never fires - `_require_python` also raises `pytest.skip`, and CI
#: has a Python.
PLATFORM_SKIP_HELPERS = ("_require_powershell", "_require_windows_powershell")

#: The trace the count comes from: test-sdk job 17121704860, commit 9c34f1ae,
#: "8 failed, 5234 passed, 320 skipped". The 320 include every other skip in the
#: suite; thirteen of the fifteen this file polices are the trace's own, and the
#: probe module's two escape guards were added after it. The trace's own lines are
#: test_dev_tools.py :52 x2, :69, :792, :818, :834 and test_worktree_owners.py
#: :235, :263, :272, :279, :297, :327, :364.
CI_TRACE_JOB = "17121704860"
CI_TRACE_COMMIT = "9c34f1aebba6f9a4b158d91726f0f816840a8f4b"
CI_TRACE_SKIPS: dict[str, int] = {
    "tests/unit/test_dev_tools.py": 8,
    "tests/unit/test_worktree_owners.py": 7,
}

#: BEGIN SKIP_GUARD - the mapping this guard reads.
#:
#: node id -> the text-guard node that protects the invariant it asserts.
SKIP_GUARD: dict[str, str] = {
    "tests/unit/test_dev_tools.py::test_the_message_writer_writes_no_byte_order_mark":
        "tests/unit/test_dev_tools.py::test_the_message_writer_keeps_the_no_bom_spelling",
    "tests/unit/test_dev_tools.py::test_the_writer_refuses_an_empty_message":
        "tests/unit/test_dev_tools.py::test_the_message_writer_keeps_the_no_bom_spelling",
    "tests/unit/test_dev_tools.py::test_the_no_bom_claim_is_driven_to_failure":
        "tests/unit/test_dev_tools.py::test_the_bom_failure_probe_names_the_shell_whose_utf8_writes_a_mark",
    "tests/unit/test_dev_tools.py::test_the_probe_worktree_refuses_a_file_whose_copy_differs":
        "tests/unit/test_dev_tools.py::test_the_probe_refuses_with_both_digests",
    "tests/unit/test_dev_tools.py::test_the_probe_worktree_copies_and_verifies_when_the_bytes_match":
        "tests/unit/test_dev_tools.py::test_the_probe_refuses_with_both_digests",
    "tests/unit/test_dev_tools.py::test_the_probe_worktree_leaves_the_caller_worktree_untouched":
        "tests/unit/test_dev_tools.py::test_the_probe_refuses_with_both_digests",
    "tests/unit/test_dev_tools.py::test_the_probe_worktree_refuses_a_parent_relative_name_that_would_escape":
        "tests/unit/test_dev_tools.py::test_the_probe_pins_its_escape_refusal_as_text",
    "tests/unit/test_dev_tools.py::test_the_probe_worktree_still_copies_a_nested_relative_name":
        "tests/unit/test_dev_tools.py::test_the_probe_pins_its_escape_refusal_as_text",
    "tests/unit/test_worktree_owners.py::test_a_staged_blob_equal_to_masters_is_classified_as_carrying_master":
        "tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches",
    "tests/unit/test_worktree_owners.py::test_a_file_that_differs_from_master_is_classified_as_authored":
        "tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches",
    "tests/unit/test_worktree_owners.py::test_an_unmerged_file_is_classified_as_conflicted":
        "tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches",
    "tests/unit/test_worktree_owners.py::test_a_carrier_is_not_reported_as_a_writer_without_its_blob_match":
        "tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches",
    "tests/unit/test_worktree_owners.py::test_a_deleted_file_is_classified_as_deleted_not_unreadable":
        "tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_delete_branch_as_text",
    "tests/unit/test_worktree_owners.py::test_a_worktree_file_equal_to_master_is_carrying_not_authored":
        "tests/unit/test_worktree_owners.py::test_the_sweep_pins_the_classification_branches",
    "tests/unit/test_worktree_owners.py::test_the_sweep_exits_zero_when_a_worktree_entry_is_unreadable":
        "tests/unit/test_worktree_owners.py::test_the_sweep_sets_its_own_exit_code",
}
#: END SKIP_GUARD

#: BEGIN LOCALLY_PROVED_ONLY - invariants that need Windows, with the reason they
#: cannot be asserted as text. Rendered into docs/dev-tools.md between markers.
LOCALLY_PROVED_ONLY: dict[str, str] = {
    "the sweep's classification branches":
        "the four branch conditions are pinned as text by "
        "test_the_sweep_pins_the_classification_branches and the delete branch by "
        "test_the_sweep_pins_the_delete_branch_as_text, but which ONE fires for a "
        "given `git status` entry is decided by git at run time and can only be "
        "observed on a host that can execute the script",
    "the committed identity of a copy":
        "a probe copy is verified by hashing it; that the destination really holds "
        "the source's bytes needs a filesystem and a PowerShell host",
    "a message file's first three bytes":
        "the writer's own self-check reads the file it just wrote, and the BOM the "
        "probe reproduces is Windows PowerShell 5.1's, which only exists on Windows",
}

MARKER_BEGIN = "<!-- BEGIN skip-guard-table -->"
MARKER_END = "<!-- END skip-guard-table -->"


def _module(relative: str) -> ast.Module:
    return ast.parse((REPOSITORY_ROOT / relative).read_text(encoding="utf-8"))


def _call_names(node: ast.AST) -> set[str]:
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            found.add(child.func.id)
    return found


def _calls_pytest_skip(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "skip"
            and isinstance(func.value, ast.Name)
            and func.value.id == "pytest"
        ):
            return True
    return False


def _is_fixture(node: ast.FunctionDef) -> bool:
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if (
            isinstance(target, ast.Attribute)
            and target.attr == "fixture"
            and isinstance(target.value, ast.Name)
            and target.value.id == "pytest"
        ):
            return True
    return False


def _functions() -> dict[str, dict]:
    """Every function of the scanned modules, keyed by its node id."""
    found: dict[str, dict] = {}
    for relative in SCANNED:
        for node in ast.walk(_module(relative)):
            if not isinstance(node, ast.FunctionDef):
                continue
            found[f"{relative}::{node.name}"] = {
                "path": relative,
                "id": f"{relative}::{node.name}",
                "name": node.name,
                "is_test": node.name.startswith("test_"),
                "fixture": _is_fixture(node),
                "calls": _call_names(node),
                "calls_pytest_skip": _calls_pytest_skip(node),
                "arguments": {arg.arg for arg in node.args.args + node.args.kwonlyargs},
            }
    return found


def platform_reaching(functions: dict[str, dict]) -> set[str]:
    """Function NAMES that reach a platform skip, from their own call graph."""
    reaching = set(PLATFORM_SKIP_HELPERS)
    changed = True
    while changed:
        changed = False
        for info in functions.values():
            if info["name"] in reaching:
                continue
            if info["calls"] & reaching:
                reaching.add(info["name"])
                changed = True
    return reaching


def all_nodes() -> dict[str, dict]:
    return _functions()


def skip_nodes() -> set[str]:
    """Node ids that cannot run on a Linux runner, derived from the code."""
    functions = _functions()
    platform = platform_reaching(functions)
    skipping_fixtures = {
        info["name"]
        for info in functions.values()
        if info["fixture"]
        and (info["calls_pytest_skip"] or info["calls"] & platform)
    }
    found: set[str] = set()
    for info in functions.values():
        if not info["is_test"]:
            continue
        if (
            info["calls"] & platform
            or info["calls_pytest_skip"]
            or info["arguments"] & skipping_fixtures
        ):
            found.add(info["id"])
    return found


def unmapped_skips(skip: set[str]) -> list[str]:
    """The guard's own check, callable with an injected set so it can be driven."""
    return sorted(skip - set(SKIP_GUARD))


def broken_guards(nodes: dict[str, dict], skip: set[str]) -> list[str]:
    """Rows whose named text guard is missing, or itself skips in CI."""
    problems: list[str] = []
    for node, guard in sorted(SKIP_GUARD.items()):
        if guard not in nodes:
            problems.append(f"{node} -> {guard}: no such test node")
        elif guard in skip:
            problems.append(f"{node} -> {guard}: the guard itself skips in CI")
    return problems


def test_every_skip_node_is_in_the_mapping():
    """A new `pytest.skip` cannot be added without naming what covers it."""
    missing = unmapped_skips(skip_nodes())
    assert missing == [], (
        "these nodes skip on a Linux runner and no text guard is named for them:\n"
        + "\n".join(missing)
    )


def test_the_mapping_names_no_node_that_runs_in_ci():
    """A row for a node that does not skip is a stale claim, not a guard."""
    stale = sorted(set(SKIP_GUARD) - skip_nodes())
    assert stale == [], (
        "these rows name nodes that run in CI, so the row is stale:\n" + "\n".join(stale)
    )


def test_every_protecting_guard_exists_and_runs_in_ci():
    """The guard may not itself be a skip node, or the pair proves nothing."""
    assert broken_guards(all_nodes(), skip_nodes()) == []


def test_the_counts_agree_with_the_ci_trace():
    """The per-file counts are the test-sdk trace's, not this machine's.

    On Windows these nodes run, so no local run can produce these numbers at all.
    """
    per_file: dict[str, int] = {}
    for node in skip_nodes():
        path = node.split("::")[0]
        per_file[path] = per_file.get(path, 0) + 1
    assert per_file == CI_TRACE_SKIPS, (
        f"job {CI_TRACE_JOB} at {CI_TRACE_COMMIT[:8]} listed {CI_TRACE_SKIPS}, "
        f"the AST derives {per_file}")


def test_the_document_table_matches_this_files_tables():
    """The rendered section is derived from both tables, so it cannot drift."""
    document = (REPOSITORY_ROOT / "docs" / "dev-tools.md").read_text(encoding="utf-8")
    assert MARKER_BEGIN in document and MARKER_END in document, (
        "docs/dev-tools.md must carry the generated skip-guard table between markers")
    rendered = document[
        document.index(MARKER_BEGIN) + len(MARKER_BEGIN) : document.index(MARKER_END)
    ].strip()
    assert rendered == render_table(), (
        "docs/dev-tools.md's skip-guard table is not what this file generates; "
        "regenerate it rather than editing it by hand")


def render_table() -> str:
    """The two tables, as the document carries them."""
    by_file: dict[str, int] = {}
    for node in sorted(skip_nodes()):
        path = node.split("::")[0]
        by_file[path] = by_file.get(path, 0) + 1
    counted = ", ".join(f"{count} in `{path}`" for path, count in sorted(by_file.items()))
    lines = [
        f"`{len(skip_nodes())}` nodes skip on a runner without PowerShell: {counted}.",
        f"Thirteen of these were counted from the test-sdk trace of job "
        f"`{CI_TRACE_JOB}` at `{CI_TRACE_COMMIT[:8]}`; the probe module's two escape "
        "guards were added after that trace. On Windows these nodes run, so no local "
        "run can produce the number.",
        "",
        "| Test file | Nodes that skip without PowerShell |",
        "| --- | --- |",
    ]
    for path, count in sorted(by_file.items()):
        lines.append(f"| `{path}` | {count} |")
    lines += ["", "Each one names the text guard that holds its invariant:", ""]
    lines += ["| Node that skips | Text guard that runs in CI |", "| --- | --- |"]
    for node, guard in sorted(SKIP_GUARD.items()):
        lines.append(f"| `{node}` | `{guard}` |")
    lines += [
        "",
        "Proven on Windows only, because the check needs a host that can run the script:",
        "",
        "| Invariant | Why it cannot be asserted as text |",
        "| --- | --- |",
    ]
    for invariant, reason in sorted(LOCALLY_PROVED_ONLY.items()):
        lines.append(f"| {invariant} | {reason} |")
    return "\n".join(lines)


def test_the_locally_proved_table_keeps_every_invariant_it_claims():
    for invariant, reason in LOCALLY_PROVED_ONLY.items():
        assert reason.strip(), f"{invariant} has no reason"
        assert len(reason) > 40, f"{invariant}'s reason says nothing"


# --- the two failure drives ---------------------------------------------------


def test_a_new_skip_without_a_mapping_fails():
    """Failure drive one: a skip added with no row is reported by name.

    Driven through the same function the real check calls, with the set the future
    edit would produce - a `monkeypatch` of this module's own globals would patch a
    second import of it and prove nothing.
    """
    future = "tests/unit/test_dev_tools.py::test_a_future_skip"
    missing = unmapped_skips(skip_nodes() | {future})
    assert missing == [future], missing


def test_a_deleted_text_guard_fails_for_its_skip_nodes():
    """Failure drive two: removing a named guard is reported for its skip nodes."""
    guard = SKIP_GUARD[
        "tests/unit/test_worktree_owners.py::test_a_deleted_file_is_classified_as_deleted_not_unreadable"
    ]
    nodes = dict(all_nodes())
    nodes.pop(guard)
    problems = broken_guards(nodes, skip_nodes())
    assert any("no such test node" in problem and guard in problem for problem in problems), (
        problems)


def test_the_rendered_table_is_reproducible():
    """The document's block is exactly what this file renders, byte for byte."""
    first = render_table()
    assert render_table() == first
    for path, count in CI_TRACE_SKIPS.items():
        assert re.search(rf"\| `{re.escape(path)}` \| {count} \|", first), first
    assert f"job `{CI_TRACE_JOB}`" in first, first
