"""Focused validation gates for this repository's test suite.

The suite has two shapes, and every test belongs to exactly one of them:

``fast``
    everything under ``tests/unit`` - synthetic fixtures only, no ROM, no
    network. This is the whole portable suite (~2 minutes).
``rom``
    everything under ``tests/integration`` - needs a canonical local ROM,
    and skips cleanly without one. This is the expensive shape, ~90 minutes
    for the whole thing, which is why it is never the default gate.

Four further gates cut across that axis by subsystem, so a ticket can name
its blast radius instead of reconstructing a path list:

``workbench``, ``writer``, ``map``, ``research``

A test file carries *every* gate whose concern it exercises, so a map-layout
write test can be ``map`` and ``writer`` at once. Membership is by filename
pattern, which is stable under the repository's existing naming (a file's
prefix names the SDK subsystem it tests); the rules below are the whole
definition, and ``tests/unit/test_test_gates.py`` checks them against the
collection, the pytest marker registry and ``docs/testing.md``.

Adding a test file needs no edit here unless it opens a genuinely new
concern: an ordinary new ``tests/unit/test_something.py`` is ``fast``
automatically, and a ``tests/integration/test_something_rom.py`` is ``rom``.
"""

from __future__ import annotations

from fnmatch import fnmatch
import os
from pathlib import Path

#: Where the gate registry lives relative to the repository root.
TESTS_DIRECTORY = "tests"

GATE_DESCRIPTIONS: dict[str, str] = {
    "fast": "portable, deterministic tests under tests/unit; the default gate",
    "workbench": "DragonByte Z Workbench UI, session and editor regressions",
    "writer": "authored-image, provenance, allocation and output-safety tests",
    "map": "map reading, placement, rendering and layout regressions",
    "research": "research and runtime tooling tests",
    "rom": "tests that need a canonical local ROM image (tests/integration)",
}

#: Every rule that assigns a gate to a test file, in the order they are
#: declared. Patterns match a path relative to ``tests/`` with forward
#: slashes. Rules are additive: a file carries the union of what it matches.
GATE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    # --- the totality axis: directory decides fast vs rom ------------------
    ("unit/*", ("fast",)),
    ("integration/*", ("rom",)),

    # --- workbench: the PySide6 client and its panels ----------------------
    ("*/test_workbench_*.py", ("workbench",)),
    ("*/test_build_panel_*.py", ("workbench",)),
    # The map browser *tab* is a Workbench surface over the map model; the
    # model's own tests are `map`.
    ("*/test_workbench_map_*.py", ("map",)),

    # --- writer: everything that emits or emits-into an image --------------
    ("*/test_authored_*.py", ("writer",)),
    ("*/test_*write*.py", ("writer",)),
    ("*/test_*safety*.py", ("writer",)),
    ("*/test_*relocat*.py", ("writer",)),
    ("*/test_*allocation*.py", ("writer",)),
    ("*/test_*expansion*.py", ("writer",)),
    ("*/test_*capacity*.py", ("writer",)),
    ("*/test_free_space_audit*.py", ("writer",)),
    ("*/test_*authoring*.py", ("writer",)),
    ("*/test_text_growth.py", ("writer",)),
    # `expand` and `expansion` are the same concern under two spellings; the
    # ROM-gated expansion proof is `test_rom_expand_001.py`.
    ("*/test_rom_expand*.py", ("writer",)),
    # A map-layout edit is a written image with provenance: both gates.
    ("*/test_map_layout_*.py", ("writer",)),
    ("*/test_project_build_rom.py", ("writer",)),
    ("*/test_graphics_override_build_rom.py", ("writer",)),
    ("*/test_cross_profile_invariants.py", ("writer",)),
    ("*/test_gameplay_effect_native*.py", ("writer",)),

    # --- map: reading, placing, rendering and laying out maps --------------
    ("*/test_map_*.py", ("map",)),
    ("*/test_maps.py", ("map",)),
    ("*/test_placement_types.py", ("map",)),
    ("*/test_variable_placements.py", ("map",)),
    ("*/test_variation_array_first_words.py", ("map",)),
    ("*/test_bg_tilemap.py", ("map",)),
    ("*/test_local_*.py", ("map",)),
    ("*/test_buu_map_*.py", ("map",)),
    ("*/test_buu_placement_*.py", ("map",)),

    # --- research: tooling that measures the ROM ---------------------------
    ("*/test_atlas*.py", ("research",)),
    ("*/test_default_atlas*.py", ("research",)),
    ("*/test_mgba_*.py", ("research",)),
    ("*/test_rom0*_runtime.py", ("research",)),
    ("*/test_thumb_*.py", ("research",)),
    ("*/test_logx_*.py", ("research",)),
    ("*/test_ui_graphics_*.py", ("research",)),
    ("*/test_ghidra_helpers.py", ("research",)),
    ("*/test_p009_crit_report.py", ("research",)),
    ("*/test_decoded_text_*.py", ("research",)),
)

#: The repository root, derived from this file's location.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def relative_test_path(path: str | Path) -> str | None:
    """Return ``path`` as a forward-slashed path under ``tests/``, or None.

    Accepts an absolute path (what pytest collects), a repository-relative
    path (``tests/unit/test_x.py``) or a test-relative one (``unit/test_x.py``).
    ``None`` means the file is not part of the test tree (a stray doctest, a
    plugin), and no gate applies.
    """
    candidate = Path(path)
    # Repository-relative first: ``tests/unit/test_x.py`` resolves under the
    # repository, and a bare ``unit/test_x.py`` still resolves under `tests/`.
    # The other order would double-prefix the repository-relative form and
    # silently return no gate at all.
    bases = (
        (REPOSITORY_ROOT,)
        if candidate.is_absolute()
        else (REPOSITORY_ROOT, REPOSITORY_ROOT / TESTS_DIRECTORY)
    )
    for base in bases:
        try:
            relative = (base / candidate).resolve().relative_to(
                (REPOSITORY_ROOT / TESTS_DIRECTORY).resolve()
            )
        except ValueError:
            continue
        return relative.as_posix()
    return None


def gates_for(path: str | Path) -> tuple[str, ...]:
    """The gates carried by the test file at ``path``, in declaration order."""
    relative = relative_test_path(path)
    if relative is None:
        return ()
    gates: list[str] = []
    for pattern, assigned in GATE_RULES:
        if fnmatch(relative, pattern):
            for gate in assigned:
                if gate not in gates:
                    gates.append(gate)
    return tuple(gates)


def gate_files(gates: set[str] | frozenset[str]) -> tuple[str, ...]:
    """Every test file under ``tests/`` carrying at least one of ``gates``."""
    discovered = []
    for directory, _, names in os.walk(REPOSITORY_ROOT / TESTS_DIRECTORY):
        for name in sorted(names):
            if not (name.startswith("test_") and name.endswith(".py")):
                continue
            path = Path(directory) / name
            if set(gates_for(path)) & set(gates):
                discovered.append(relative_test_path(path))
    return tuple(sorted(discovered))
