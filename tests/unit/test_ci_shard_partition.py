"""The shard partition: totality, determinism, balance, and the deselect hook.

Part 4 of RETRO-CI-GITHUB-001 runs the portable suite as ten parallel jobs. The
property that makes that legitimate is checked first: every collected node lands
in exactly one shard, for every shard count in play. The rest pins what the
partition must not depend on (process state, the interpreter's randomised
``hash()``), bounds how uneven it is allowed to be, and drives the deselect hook
through pytest itself, so the collection one shard runs is observed rather than
argued. The merge script is checked here too, on synthetic documents.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ElementTree

import pytest

from ci.merge_junit import DuplicateNodeError, merge_texts, totals_of
from tests.gates import REPOSITORY_ROOT, TESTS_DIRECTORY, relative_test_path
from tests.shards import (
    SHARD_COUNT_VARIABLE,
    SHARD_INDEX_VARIABLE,
    node_identifier,
    partition,
    selection_from_environment,
    shard_of,
)

#: The shard counts the workflow uses or this module checks.
SHARD_COUNTS = (4, 10, 16)

#: The module the hook is driven against: three nodes, standard library plus one
#: package module, so the nested run costs about a second.
DRIVEN_MODULE = f"{TESTS_DIRECTORY}/unit/test_hashing.py"

#: ``shard_of`` values computed once from the committed identifiers and pinned
#: with the count each belongs to. They are the proof that the shard is a pure
#: function of the identifier: a version that used ``hash()``, or any process
#: state, cannot reproduce them.
PINNED_SHARDS = (
    (f"{TESTS_DIRECTORY}/unit/test_text_tool_list.py", 10, 1),
    (
        f"{TESTS_DIRECTORY}/unit/test_text_tool_list.py"
        "::test_the_status_cell_paints_no_fill_of_its_own_and_the_divider_runs_its_width",
        10,
        2,
    ),
    (f"{TESTS_DIRECTORY}/integration/test_container_decode_synthetic.py", 16, 9),
)

#: Set by the hook in a sharded run. The nested runs below would inherit it, and
#: a pytest a test started itself must never be sharded a second time.
NESTED_RUN_VARIABLE = "WEBFOOT_PYTEST_IN_PROGRESS"

#: A module of three nodes cannot prove a deselect with a count above that.
MINIMUM_DRIVEN_NODES = 3


def _universe() -> tuple[str, ...]:
    """Every file under ``tests/`` the shared configuration would collect.

    The predicate is imported from the configuration itself rather than restated,
    so a file this walk finds and the configuration would not (or the reverse)
    cannot happen.
    """
    from tests.conftest import _is_test_file

    found = []
    for directory, _, names in os.walk(REPOSITORY_ROOT / TESTS_DIRECTORY):
        for name in sorted(names):
            path = Path(directory) / name
            relative = relative_test_path(path)
            if _is_test_file(path) and relative is not None:
                found.append(f"{TESTS_DIRECTORY}/{relative}")
    return tuple(sorted(found))


def _declared_nodes() -> set[str]:
    """The names of the test functions the driven module declares."""
    source = (REPOSITORY_ROOT / DRIVEN_MODULE).read_text(encoding="utf-8")
    return {
        node.name
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }


def _environment(**overrides: str) -> dict[str, str]:
    """The environment for a nested run: no shard selection unless one is asked for."""
    environment = os.environ.copy()
    environment.pop(NESTED_RUN_VARIABLE, None)
    environment.pop(SHARD_COUNT_VARIABLE, None)
    environment.pop(SHARD_INDEX_VARIABLE, None)
    environment.update(overrides)
    return environment


def _collected(environment: dict[str, str]) -> list[str]:
    """The node ids a collect-only run of the driven module reports."""
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            DRIVEN_MODULE,
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        cwd=str(REPOSITORY_ROOT),
        capture_output=True,
        text=True,
        env=environment,
    )
    assert completed.returncode in (0, 5), completed.stdout + completed.stderr
    return [line for line in completed.stdout.splitlines() if "::" in line]


def _smallest_non_empty(shards: dict[int, list[str]]) -> int:
    """The index of a non-empty shard holding fewer than every node."""
    return min(
        (index for index, members in shards.items() if members),
        key=lambda index: len(shards[index]),
    )


def test_every_file_lands_in_exactly_one_shard():
    """The owner's totality check: the union is the universe, with no overlap."""
    universe = _universe()
    assert len(universe) > 100, universe
    for count in SHARD_COUNTS:
        shards = partition(universe, count)
        assert sorted(shards) == list(range(count))
        collected = [member for members in shards.values() for member in members]
        assert sorted(collected) == sorted(universe), count
        assert len(collected) == len(set(collected)), count
        assert all(members for members in shards.values()), count


def test_the_shard_of_an_identifier_is_pinned_to_its_own_hash():
    """Prevents: a partition resting on ``hash()`` or on process state."""
    for identifier, count, expected in PINNED_SHARDS:
        assert shard_of(identifier, count) == expected, (identifier, count)


def test_a_node_identifier_is_the_collected_node_id():
    """Prevents: the hook hashing a different spelling than the checked universe."""
    assert node_identifier("tests/unit/test_x.py", "test_y") == "tests/unit/test_x.py::test_y"
    assert (
        node_identifier("tests\\unit\\test_x.py", "test_y")
        == "tests/unit/test_x.py::test_y"
    )


def test_the_file_counts_stay_within_a_threefold_spread():
    """Prevents: a partition so uneven that one job carries the suite."""
    sizes = [len(members) for members in partition(_universe(), 10).values()]
    assert min(sizes) >= 1
    assert max(sizes) <= 3 * min(sizes), sizes


def test_no_variables_means_no_sharding(monkeypatch):
    monkeypatch.delenv(SHARD_COUNT_VARIABLE, raising=False)
    monkeypatch.delenv(SHARD_INDEX_VARIABLE, raising=False)
    assert selection_from_environment() is None


def test_a_valid_selection_is_returned_unchanged(monkeypatch):
    monkeypatch.setenv(SHARD_COUNT_VARIABLE, "10")
    monkeypatch.setenv(SHARD_INDEX_VARIABLE, "3")
    assert selection_from_environment() == (10, 3)


@pytest.mark.parametrize(
    ("count", "index", "named"),
    (
        ("0", "0", SHARD_COUNT_VARIABLE),
        ("10", "10", SHARD_INDEX_VARIABLE),
        ("10", "-1", SHARD_INDEX_VARIABLE),
        ("10", "", SHARD_INDEX_VARIABLE),
        ("many", "0", SHARD_COUNT_VARIABLE),
        ("10", "one", SHARD_INDEX_VARIABLE),
    ),
)
def test_a_misconfigured_shard_fails_loudly(monkeypatch, count, index, named):
    """Prevents: a bad shard silently selecting nothing, or everything."""
    monkeypatch.setenv(SHARD_COUNT_VARIABLE, count)
    monkeypatch.setenv(SHARD_INDEX_VARIABLE, index)
    with pytest.raises(RuntimeError) as failure:
        selection_from_environment()
    assert named in str(failure.value), str(failure.value)


def test_without_the_variables_a_run_collects_every_node_of_the_module():
    """The local record's guarantee: the hook is a no-op when nothing is asked."""
    collected = _collected(_environment())
    assert collected, "the driven module collected nothing"
    assert {identifier.split("::", 1)[1] for identifier in collected} == _declared_nodes()


def test_a_shard_collects_only_its_own_nodes():
    """Prevents: a deselect that drops the wrong nodes, or only some of them."""
    identifiers = _collected(_environment())
    assert len(identifiers) >= MINIMUM_DRIVEN_NODES, identifiers
    shards = partition(identifiers, 10)
    index = _smallest_non_empty(shards)
    collected = _collected(
        _environment(**{SHARD_COUNT_VARIABLE: "10", SHARD_INDEX_VARIABLE: str(index)})
    )
    assert sorted(collected) == sorted(shards[index])
    assert 0 < len(collected) < len(identifiers)


def test_a_count_above_the_node_count_still_collects_a_strict_subset():
    """Prevents: a shard wider than the module quietly running all of it."""
    identifiers = _collected(_environment())
    count = len(identifiers) + 1
    shards = partition(identifiers, count)
    index = _smallest_non_empty(shards)
    collected = _collected(
        _environment(
            **{SHARD_COUNT_VARIABLE: str(count), SHARD_INDEX_VARIABLE: str(index)}
        )
    )
    assert sorted(collected) == sorted(shards[index])
    assert 0 < len(collected) < len(identifiers)


def _junit(name: str, tests: int, skipped: int, cases: tuple[tuple[str, str], ...]) -> str:
    """One input document, with the attributes the record's reader sums."""
    body = "".join(
        f'<testcase classname="{classname}" name="{test}" time="0.1"/>'
        for classname, test in cases
    )
    return (
        f'<testsuites tests="{tests}" skipped="{skipped}">'
        f'<testsuite name="{name}" tests="{tests}" failures="0" errors="0" '
        f'skipped="{skipped}" time="1.0">{body}</testsuite>'
        "</testsuites>"
    )


def test_the_merged_totals_are_the_sum_of_the_input_totals():
    """Prevents: a merged report whose counts disagree with what it merged."""
    first = _junit(
        "one", 2, 1, (("tests.unit.test_a", "test_x"), ("tests.unit.test_a", "test_y"))
    )
    second = _junit(
        "two",
        3,
        2,
        (
            ("tests.unit.test_b", "test_p"),
            ("tests.unit.test_b", "test_q"),
            ("tests.unit.test_b", "test_r"),
        ),
    )

    merged = merge_texts([first, second])

    assert totals_of(merged) == {"tests": 5, "failures": 0, "errors": 0, "skipped": 3}
    root = ElementTree.fromstring(merged)
    assert root.tag == "testsuites"
    suites = list(root)
    assert [suite.tag for suite in suites] == ["testsuite", "testsuite"]
    assert [suite.get("name") for suite in suites] == ["one", "two"]
    # The shape scripts/local-ci.ps1 reads: testsuites.testsuite, summed by
    # attribute, and every suite whole.
    assert sum(int(suite.get("tests", "0")) for suite in suites) == 5
    assert sum(int(suite.get("skipped", "0")) for suite in suites) == 3
    assert len(root.findall(".//testcase")) == 5


def test_a_node_two_inputs_share_fails_the_merge_and_names_it():
    """Prevents: a merge that double-counts one node."""
    shared = (("tests.unit.test_a", "test_x"),)

    with pytest.raises(DuplicateNodeError) as failure:
        merge_texts([_junit("one", 1, 0, shared), _junit("two", 1, 0, shared)])

    assert "tests.unit.test_a::test_x" in str(failure.value)
