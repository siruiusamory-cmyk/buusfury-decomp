"""Run the app-wide-Qt-state adjacency set in ONE pytest process.

``test-sdk`` runs the portable suite with ``--dist loadfile``, which gives every
module its own worker process. That is the right shape for speed and the wrong
shape for this hazard: several of the shipping GUI modules mutate process-wide
state - ``QApplication`` is a singleton, so the application name
(``tools/webfoot/randomizer/gui.py:1294``), the organisation name and the theme's
application style sheet (``tools/webfoot/workbench/theme.py:430``,
``apply_app_theme``) outlive the module that set them, and a module that measures
a widget's height against ``theme.CONTROL_HEIGHT`` (24,
``tools/webfoot/workbench/theme.py:291``) is measuring whatever the module before
it left behind. Under ``--dist loadfile`` no module ever follows another in the
same process, so that interaction is never exercised.

This script runs the fixed set in one normal pytest process, in one of two
orders, and fails on anything other than a clean run:

- every member must be collected and must actually execute; a skip, a failure or
  an error is a hard failure, because a module that does not run makes the
  adjacency claim a lie rather than a finding;
- the set is explicit. The modules the run actually executed are read back from
  its JUnit report and compared with the set, so a silent widening to the whole
  unit suite, or a module that silently disappeared, is a failure;
- the counts are printed, so the two orders can be compared from their own
  output.

``tests/unit/test_adjacency.py`` pins the set, the two orders and the counts, so
the script cannot be reduced to a `pytest tests/unit` invocation in passing.

Usage::

    python -m scripts.adjacency_run -Order forward
    python -m scripts.adjacency_run -Order reverse
"""

from __future__ import annotations

import argparse
import contextlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

#: The adjacency set. The first seventeen members are exactly
#: ``REQUIRED_GUI_MODULES`` in ``tests/gates.py`` - the repository's own registry
#: of dependency-guarded shipping GUI modules, which is what makes them the
#: app-wide-surface modules rather than a hand-picked list. Each one either
#: constructs the workbench ``MainWindow``/``Session`` or drives a panel of it, so
#: each reads the process-wide ``QApplication`` the previous module may have
#: restyled.
#:
#: The last two are the neighbours, and they are the reason the order matters:
#:
#: ``test_warp_randomizer_gui.py`` is the one module in the tree that actually
#: applies the app-wide surface - its
#: ``test_the_application_is_configured_with_the_shared_dragonbyte_z_theme``
#: calls ``gui.configure_application(qapp)``, which is
#: ``tools/webfoot/randomizer/gui.py:1296`` -> ``theme.apply_app_theme(app)`` ->
#: ``app.setStyleSheet``/``app.setPalette``, and it sets the application and
#: organisation name. It saves and restores the style sheet and the palette; the
#: application name it cannot restore, and does not.
#:
#: ``test_enemy_randomizer_gui.py`` is the neighbour that measures widgets: it
#: imports ``tools.webfoot.workbench.theme`` and asserts, at
#: ``tests/unit/test_enemy_randomizer_gui.py:665``, that every visible button in
#: one randomizer window is ``theme.CONTROL_HEIGHT`` tall. A style sheet left
#: behind by a module before it is exactly what changes that measurement.
#:
#: Neither neighbour is in ``REQUIRED_GUI_MODULES``. Both are the randomizer
#: windows, so neither name carries ``workbench`` and ``tests/gates.py`` gives
#: each one ``fast`` alone - the set's own test records that rather than
#: assuming it.
ADJACENCY_SET: tuple[str, ...] = (
    "tests/unit/test_build_panel_guard.py",
    "tests/unit/test_build_panel_overwrite.py",
    "tests/unit/test_workbench_build_manifest.py",
    "tests/unit/test_workbench_build_run_dialogs.py",
    "tests/unit/test_workbench_dialogue.py",
    "tests/unit/test_workbench_graphics.py",
    "tests/unit/test_workbench_graphics_undo.py",
    "tests/unit/test_workbench_launcher_settings.py",
    "tests/unit/test_workbench_map_browser.py",
    "tests/unit/test_workbench_map_tab.py",
    "tests/unit/test_workbench_warp_transitions.py",
    "tests/unit/test_workbench_palette_cost.py",
    "tests/unit/test_workbench_project_status.py",
    "tests/unit/test_workbench_scene.py",
    "tests/unit/test_workbench_sprite_authoring.py",
    "tests/unit/test_workbench_smoke.py",
    "tests/unit/test_workbench_state_and_errors.py",
    "tests/unit/test_enemy_randomizer_gui.py",
    "tests/unit/test_warp_randomizer_gui.py",
)

#: The one member of the set that cannot run in CI, by node id and by reason.
#: ``tests/unit/test_workbench_graphics.py:1010`` skips when no canonical image is
#: present, and ``test-sdk`` installs no ROM. It is deselected rather than left in
#: place, because this script fails on a skip: excluded with a reason, not skipped
#: silently.
ROM_GATED_MEMBER = (
    "tests/unit/test_workbench_graphics.py::test_real_rom_thumbnail_is_non_empty"
)
ROM_GATED_REASON = "canonical Buu's Fury ROM is not present in CI"

ORDERS = {"forward": ADJACENCY_SET, "reverse": tuple(reversed(ADJACENCY_SET))}


def plan(order: str) -> list[str]:
    """The exact pytest argument vector for ``order``, without the interpreter."""
    # One process, no worker processes: the whole point of this run.
    arguments = ["-q", "-p", "no:cacheprovider"]
    arguments += ["--deselect", ROM_GATED_MEMBER]
    arguments += list(ORDERS[order])
    return arguments


def summaries(report: Path) -> tuple[dict[str, int], set[str]]:
    """``(counts, executed modules)`` from a JUnit report.

    ``collected`` is the report's own testcase count, so it is what ran rather
    than what was asked for.
    """
    tree = ElementTree.parse(report)
    counts = {"collected": 0, "passed": 0, "skipped": 0, "failed": 0, "error": 0}
    modules: set[str] = set()
    for case in tree.iter("testcase"):
        counts["collected"] += 1
        classname = case.get("classname") or ""
        # pytest writes the module's dotted path, e.g.
        # `tests.unit.test_workbench_smoke` for tests/unit/test_workbench_smoke.py.
        modules.add(classname.replace(".", "/") + ".py")
        outcome = "passed"
        for child in case:
            if child.tag == "skipped":
                outcome = "skipped"
            elif child.tag == "failure":
                outcome = "failed"
            elif child.tag == "error":
                outcome = "error"
        counts[outcome] += 1
    return counts, modules


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=doc_first_line())
    parser.add_argument("-Order", choices=sorted(ORDERS), required=True)
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    selection = ORDERS[args.Order]
    arguments = plan(args.Order)
    print(
        f"adjacency_run: order={args.Order} modules={len(selection)} "
        f"one pytest process, no xdist"
    )
    print(f"adjacency_run: deselecting {ROM_GATED_MEMBER} ({ROM_GATED_REASON})")

    with tempfile.TemporaryDirectory(prefix="adjacency-") as directory:
        report = Path(directory) / "report.xml"
        invocation = [
            sys.executable,
            "-m",
            "pytest",
            *arguments,
            f"--junitxml={report}",
        ]
        print("adjacency_run: " + " ".join(invocation))
        completed = subprocess.run(invocation, cwd=root, check=False)
        counts, executed = summaries(report)

    print(
        "adjacency_run: collected={collected} passed={passed} skipped={skipped} "
        "failed={failed} error={error}".format(**counts)
    )
    expected = {member.replace("/", ".")[: -len(".py")] for member in selection}
    expected = {member.replace(".", "/") + ".py" for member in expected}
    unexpected = sorted(executed - expected)
    missing = sorted(expected - executed)

    failures = []
    if completed.returncode != 0:
        failures.append(f"pytest exited {completed.returncode}")
    for count in ("skipped", "failed", "error"):
        if counts[count]:
            failures.append(f"{count}={counts[count]}")
    if unexpected:
        failures.append(f"modules outside the set executed: {unexpected}")
    if missing:
        failures.append(f"set members did not execute: {missing}")
    if failures:
        print("adjacency_run: FAIL - " + "; ".join(failures))
        return 1
    print(f"adjacency_run: OK - order={args.Order} ran {len(selection)} modules clean")
    return 0


def doc_first_line() -> str:
    """The module docstring's first line, for the CLI help."""
    return (__doc__ or "").strip().splitlines()[0]


if __name__ == "__main__":
    with contextlib.suppress(BrokenPipeError):
        raise SystemExit(main())
