"""The CI-runnable/locally-proved split, made mechanical and self-policing.

Seven guard nodes in this suite need a PowerShell host, which the Linux CI runner
does not have. That is deliberate: a `.ps1` cannot execute there. What is NOT
acceptable is the state the first version of this ticket shipped - a load-bearing
behaviour guarded ONLY by a test that skips in CI, with a prose table claiming
otherwise. This file makes the claim checkable.

Three things are derived, never typed from memory:

1. WHICH NODES SKIP. Every node of the scanned test files is AST-parsed, and a node
   is a skip node when it calls a guard helper that can raise `pytest.skip`, either
   directly or through the one fixture that does (its parameters are followed).
   Adding a new `pytest.skip` to a node puts it in the set automatically, so a new
   skip cannot be forgotten.

2. WHICH TEXT GUARD PROTECTS EACH ONE. `SKIP_GUARD` is the block: one row per skip
   node naming the pure-Python guard node that holds the invariant it asserts. A
   skip node with no row fails, and a row naming a guard that does not exist, or one
   that itself skips, fails.

3. WHAT CANNOT BE PROVED AS TEXT. `LOCALLY_PROVED_ONLY` is a table of invariants
   that need Windows and cannot be asserted as text, each with the reason. It is
   rendered into `docs/dev-tools.md` between markers, and this guard fails when the
   document and the table disagree - so the document cannot drift away from the code
   it describes.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The test modules in scope: every one that guards a `.ps1` tool.
SCANNED = (
    "tests/unit/test_dev_tools.py",
    "tests/unit/test_worktree_owners.py",
)

#: The helper a node calls when it cannot run without PowerShell. A node is a skip
#: node when it calls one of these, or calls a function that does (the fixture), so
#: the set is derived from the code and cannot be forgotten.
SKIP_HELPERS = ("_require_powershell", "_require_windows_powershell")

#: Fixtures that skip, and the file that defines them: their parameters are followed
#: so a node that requests this fixture counts as a skip node even without calling a
#: helper itself.
SKIPPING_FIXTURES = {"synthetic": "tests/unit/test_worktree_owners.py"}

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
        "tests/unit/test_worktree_owners.py::test_the_cutter_ends_with_its_own_exit_code",
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


def _call_names(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            found.add(node.func.id)
    return found


def _scan(relative: str) -> dict[str, dict]:
    """Every node of one test module, with what the guard needs from it."""
    tree = _module(relative)
    nodes: dict[str, dict] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        arguments = {
            arg.arg for arg in node.args.args + node.args.kwonlyargs
        }
        calls = _call_names(node)
        nodes[node.name] = {
            "path": relative,
            "id": f"{relative}::{node.name}",
            "calls_skip_helper": bool(calls & set(SKIP_HELPERS)),
            "asks_skipping_fixture": bool(arguments & set(SKIPPING_FIXTURES)),
        }
    return nodes


def skip_nodes() -> set[str]:
    """Node ids that cannot run on a Linux runner, derived from the code."""
    found: set[str] = set()
    for relative in SCANNED:
        for node in _scan(relative).values():
            if node["calls_skip_helper"] or node["asks_skipping_fixture"]:
                found.add(node["id"])
    return found


def all_nodes() -> dict[str, dict]:
    found: dict[str, dict] = {}
    for relative in SCANNED:
        found.update(_scan(relative))
    return found


def test_every_skip_node_is_in_the_mapping():
    """A new `pytest.skip` cannot be added without naming what covers it."""
    missing = sorted(skip_nodes() - set(SKIP_GUARD))
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
    nodes = all_nodes()
    problems: list[str] = []
    for node, guard in sorted(SKIP_GUARD.items()):
        if guard not in nodes:
            problems.append(f"{node} -> {guard}: no such test node")
            continue
        if guard in skip_nodes():
            problems.append(f"{node} -> {guard}: the guard itself skips in CI")
    assert problems == [], "\n".join(problems)


def test_the_counts_agree_with_the_ci_trace():
    """13 nodes, which is what the test-sdk trace listed.

    The trace is the authority: at b5f80ed it names 6 nodes in test_dev_tools.py
    and 7 in test_worktree_owners.py. The line numbers it gives are checked here
    too, so a node cannot be swapped for another and keep the count right.
    """
    nodes = all_nodes()
    per_file: dict[str, int] = {}
    for node in skip_nodes():
        per_file[node.split("::")[0]] = per_file.get(node.split("::")[0], 0) + 1
    assert sum(per_file.values()) == 13, per_file
    assert per_file.get("tests/unit/test_dev_tools.py") == 6, per_file
    assert per_file.get("tests/unit/test_worktree_owners.py") == 7, per_file
    assert len(nodes) > len(SKIP_GUARD)


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
        by_file[node.split("::")[0]] = by_file.get(node.split("::")[0], 0) + 1
    lines = [
        f"Generated from `tests/unit/test_skip_coverage_guard.py`. "
        f"{len(SKIP_GUARD)} nodes skip on a runner without PowerShell, "
        f"{len(skip_nodes())} in total:",
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


def _fake_scan(monkeypatch, extra_node: str) -> None:
    """Inject one more skip node, the way a future edit would."""
    real = skip_nodes()
    monkeypatch.setattr(
        "tests.unit.test_skip_coverage_guard.skip_nodes",
        lambda: real | {extra_node},
    )


def test_a_new_skip_without_a_mapping_fails(monkeypatch):
    """Failure drive one: a skip added with no row fails this file."""
    _fake_scan(monkeypatch, "tests/unit/test_dev_tools.py::test_a_future_skip")
    with pytest.raises(AssertionError) as caught:
        test_every_skip_node_is_in_the_mapping()
    assert "test_a_future_skip" in str(caught.value)


def test_a_deleted_text_guard_fails_for_its_skip_nodes(monkeypatch):
    """Failure drive two: removing a named guard fails this file."""
    nodes = dict(all_nodes())
    guard = SKIP_GUARD[
        "tests/unit/test_worktree_owners.py::test_a_deleted_file_is_classified_as_deleted_not_unreadable"
    ]
    nodes.pop(guard)
    monkeypatch.setattr(
        "tests.unit.test_skip_coverage_guard.all_nodes", lambda: nodes
    )
    with pytest.raises(AssertionError) as caught:
        test_every_protecting_guard_exists_and_runs_in_ci()
    assert "no such test node" in str(caught.value)


def test_the_rendered_table_is_reproducible():
    """The document's block is exactly what this file renders, byte for byte."""
    first = render_table()
    assert render_table() == first
    assert re.search(r"\| `tests/unit/test_dev_tools.py` \| 6 \|", first), first
    assert re.search(r"\| `tests/unit/test_worktree_owners.py` \| 7 \|", first), first
