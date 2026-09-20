"""The gate registry, the marker registry and the documentation must agree.

``tests/gates.py`` assigns the gates, ``pyproject.toml`` registers them as
pytest markers, and ``docs/testing.md`` is what a future ticket actually
reads. Three copies of one list drift apart silently, so they are checked
against each other here, along with the properties that make the gates worth
having: every test is gated, no gate is empty, and no rule has gone stale.
"""

from __future__ import annotations

from fnmatch import fnmatch

import pytest

from tests.gates import (
    GATE_DESCRIPTIONS,
    GATE_RULES,
    REPOSITORY_ROOT,
    gate_files,
    gates_for,
    relative_test_path,
)

TESTS_ROOT = REPOSITORY_ROOT / "tests"

#: The axis that must cover every test: portable or ROM-gated, never neither
#: and never both.
COMPLETENESS_GATES = ("fast", "rom")

#: The subsystem gates, which cut across that axis.
DOMAIN_GATES = ("workbench", "writer", "map", "research")


def _test_files() -> list[str]:
    return sorted(
        relative
        for path in TESTS_ROOT.rglob("test_*.py")
        if (relative := relative_test_path(path)) is not None
    )


def _registered_marker_names(pytestconfig: pytest.Config) -> set[str]:
    return {
        entry.split(":", 1)[0].strip() for entry in pytestconfig.getini("markers")
    }


def _registered_gate_descriptions(pytestconfig: pytest.Config) -> dict[str, str]:
    """The descriptions pytest would print for this project's own markers.

    Built-in markers (``skipif``, ``xfail`` and friends) share the same ini
    value, so the result is narrowed to the gates this registry defines.
    """
    registered: dict[str, str] = {}
    for entry in pytestconfig.getini("markers"):
        name, _, description = entry.partition(":")
        registered[name.strip()] = description.strip()
    return {gate: registered[gate] for gate in GATE_DESCRIPTIONS if gate in registered}


def test_every_gate_is_registered_as_a_pytest_marker(pytestconfig):
    """`-m <gate>` must be a registered marker, or pytest warns on every run."""
    registered = _registered_marker_names(pytestconfig)

    assert set(GATE_DESCRIPTIONS) <= registered


def test_the_marker_descriptions_say_what_the_registry_says(pytestconfig):
    """`pytest --markers` is a gate's discoverability; it must not drift."""
    assert _registered_gate_descriptions(pytestconfig) == GATE_DESCRIPTIONS


def test_the_gates_are_documented_with_a_runnable_command():
    """A gate nobody can find is a gate nobody runs."""
    documented = (REPOSITORY_ROOT / "docs/testing.md").read_text(encoding="utf-8")

    for gate in GATE_DESCRIPTIONS:
        assert f"-m {gate}" in documented, f"docs/testing.md never shows -m {gate}"


def test_every_test_file_sits_on_the_portable_or_the_rom_axis():
    """No file may escape both gates, and none may claim both."""
    for relative in _test_files():
        on_axis = set(gates_for(relative)) & set(COMPLETENESS_GATES)
        assert len(on_axis) == 1, (relative, sorted(on_axis))


def test_the_axis_gates_are_exactly_the_two_test_directories():
    assert all(relative.startswith("unit/") for relative in gate_files({"fast"}))
    assert all(
        relative.startswith("integration/") for relative in gate_files({"rom"})
    )
    assert len(gate_files({"fast"})) + len(gate_files({"rom"})) == len(_test_files())


def test_every_domain_gate_selects_tests():
    """A gate with no membership would be a category invented for its own sake."""
    for gate in DOMAIN_GATES:
        assert gate_files({gate}), f"gate {gate!r} selects no test file"


def test_every_rule_still_matches_a_test_file():
    """A rule that matches nothing is a stale claim about the test tree."""
    files = _test_files()
    for pattern, _ in GATE_RULES:
        assert any(fnmatch(relative, pattern) for relative in files), pattern


def test_gate_lookup_accepts_every_documented_path_form():
    """`gates_for` takes absolute, repository-relative and test-relative paths.

    All three must agree: the repository-relative form was double-prefixed
    once, which silently dropped the `fast` gate instead of failing.
    """
    absolute = TESTS_ROOT / "unit" / "test_map_render.py"
    for form in (
        absolute,
        "tests/unit/test_map_render.py",
        "unit/test_map_render.py",
    ):
        assert set(gates_for(form)) == {"fast", "map"}, form


def test_paths_outside_the_test_tree_carry_no_gate():
    assert gates_for(REPOSITORY_ROOT / "pyproject.toml") == ()
    assert gates_for(TESTS_ROOT / "helpers.py") == ()


def test_the_domain_gates_partition_the_subsystems_they_claim():
    """Spot-check the assignments a ticket is most likely to rely on."""
    expected = {
        "unit/test_workbench_session.py": {"fast", "workbench"},
        "integration/test_workbench_rom_safety.py": {"rom", "workbench", "writer"},
        "unit/test_authored_image.py": {"fast", "writer"},
        "unit/test_map_render.py": {"fast", "map"},
        "integration/test_map_layout_write_rom.py": {"rom", "map", "writer"},
        "unit/test_logx_codec_reference.py": {"fast", "research"},
        "unit/test_text_tables.py": {"fast"},
        "integration/test_text_rom.py": {"rom"},
        # Both spellings of the expansion concern, and the atlas default the
        # `research` gate claims.
        "unit/test_rom_expansion.py": {"fast", "writer"},
        "integration/test_rom_expand_001.py": {"rom", "writer"},
        "unit/test_default_atlas_directory.py": {"fast", "research"},
    }

    for relative, gates in expected.items():
        assert set(gates_for(relative)) == gates, relative


def test_the_gate_markers_reach_the_collected_tests(request):
    """This file lives in `tests/unit`, so the hook must have tagged it `fast`."""
    carried = {marker.name for marker in request.node.iter_markers()}

    assert "fast" in carried
    assert "rom" not in carried
