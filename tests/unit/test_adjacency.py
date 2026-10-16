"""The adjacency set, the two orders, and the CI job that runs them.

``test-sdk`` runs the portable suite with ``--dist loadfile``: every module gets
its own worker process, so no module ever follows another in the same process.
That hides a real hazard, because several shipping GUI modules mutate
process-wide state on the ``QApplication`` singleton - the application name, the
organisation name, and the theme's application style sheet and palette - and a
module that measures a widget against ``theme.CONTROL_HEIGHT`` is measuring
whatever the module before it left behind.

``scripts/adjacency_run.py`` is the runner that exercises that interaction in one
process per order. This file is its guard: the set it holds is exactly the
repository's own ``REQUIRED_GUI_MODULES`` registry plus the two randomizer
neighbours, both orders are named, and the CI job runs both of them. A change to
``REQUIRED_GUI_MODULES`` fails here by design, so the set is re-measured rather
than silently drifting.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re

import yaml

from scripts.adjacency_run import (
    ADJACENCY_SET,
    ORDERS,
    ROM_GATED_MEMBER,
    plan,
)
from tests.gates import (
    REPOSITORY_ROOT,
    REQUIRED_GUI_MODULES,
    gates_for,
)

CI_CONFIG = REPOSITORY_ROOT / ".gitlab-ci.yml"
ADJACENCY_JOB = "adjacency"

#: The two modules that are in the set as neighbours rather than as entries of
#: ``REQUIRED_GUI_MODULES``: the module that applies the app-wide surface
#: (``tools/webfoot/randomizer/gui.py:1296`` -> ``theme.apply_app_theme``) and the
#: module that measures widgets against it
#: (``tests/unit/test_enemy_randomizer_gui.py:665`` asserts
#: ``theme.CONTROL_HEIGHT``). Registered here so that dropping one is a failure
#: with a reason, not a quiet shrink.
NEIGHBOURS = (
    "tests/unit/test_warp_randomizer_gui.py",
    "tests/unit/test_enemy_randomizer_gui.py",
)


def _module_text(relative: str) -> str:
    return (REPOSITORY_ROOT / relative).read_text(encoding="utf-8")


def test_the_set_is_the_required_gui_modules_plus_the_two_neighbours():
    """Prevents: the set shrinking, widening, or drifting from the registry.

    ``REQUIRED_GUI_MODULES`` is the repository's own statement about which GUI
    modules CI is required to execute, so the adjacency set is that list rather
    than a hand-picked one. A change to the registry therefore fails this test
    and forces the two-order run to be re-measured, which is the point: the
    counts in ``docs/testing.md`` are a measurement, not a maintained fact.
    """
    required = {f"tests/{relative}" for relative in REQUIRED_GUI_MODULES}
    expected = required | set(NEIGHBOURS)
    assert set(ADJACENCY_SET) == expected, {
        "missing": sorted(expected - set(ADJACENCY_SET)),
        "extra": sorted(set(ADJACENCY_SET) - expected),
    }
    assert len(ADJACENCY_SET) == len(set(ADJACENCY_SET)), "the set has a duplicate"


def test_every_member_exists_and_carries_the_fast_gate():
    """Prevents: a member that moved or was renamed leaving a dead path behind.

    Every member is under ``tests/unit``, so ``tests/gates.py`` gives each one
    the ``fast`` gate from the directory axis. The two neighbours are the
    randomizer windows: neither name carries ``workbench``, and both therefore
    carry ``fast`` alone. That is recorded here rather than assumed, because the
    set is justified member by member and a rename is what would change it.
    """
    for relative in ADJACENCY_SET:
        path = REPOSITORY_ROOT / relative
        assert path.is_file(), f"{relative} is in the adjacency set and does not exist"
        assert "fast" in gates_for(relative), (relative, gates_for(relative))
    for relative in NEIGHBOURS:
        assert gates_for(relative) == ("fast",), (relative, gates_for(relative))


def test_each_neighbour_is_the_surface_or_the_measurement_it_is_here_for():
    """Prevents: keeping a neighbour that no longer does what it is cited for.

    The set is justified member by member in ``scripts/adjacency_run.py``, so the
    two claims that are not structural - that one neighbour applies the app-wide
    theme and that the other measures a widget against the theme's control
    height - are asserted against the source here.
    """
    applier = _module_text(NEIGHBOURS[0])
    assert "configure_application" in applier, NEIGHBOURS[0]
    assert "apply_app_theme" in applier or "app_stylesheet" in applier, NEIGHBOURS[0]
    measurer = _module_text(NEIGHBOURS[1])
    assert "CONTROL_HEIGHT" in measurer, NEIGHBOURS[1]
    assert "tools.webfoot.workbench import theme" in measurer, NEIGHBOURS[1]


def test_the_two_orders_are_exact_reverses_of_one_another():
    """Prevents: a second order that is the first one under another name."""
    assert set(ORDERS) == {"forward", "reverse"}
    assert ORDERS["forward"] == ADJACENCY_SET
    assert ORDERS["reverse"] == tuple(reversed(ADJACENCY_SET))
    assert ORDERS["forward"] != ORDERS["reverse"]


def test_the_plan_runs_one_process_and_excludes_exactly_one_named_member():
    """Prevents: the run hidden behind a worker, or a member skipped in silence.

    The plan is pinned as the WHOLE argument vector, by equality, against the
    literal prefix plus the module tuple in order: exactly one ``--deselect``,
    naming exactly the one ROM member. Presence plus a tail slice is not enough,
    because ``--deselect=X``, ``-k<expr>`` or any other filter inserted in the
    prefix passes both; equality forbids every one of them, ``-n`` and ``--dist``
    included, since xdist is what hides this hazard and a distributed run would
    prove nothing. The node id must still exist in the file it names, so the
    exclusion cannot outlive the test it was written for.
    """
    for order in ORDERS:
        expected = ["-q", "-p", "no:cacheprovider", "--deselect", ROM_GATED_MEMBER]
        expected += list(ORDERS[order])
        assert plan(order) == expected, plan(order)
    path, _, name = ROM_GATED_MEMBER.partition("::")
    assert name, ROM_GATED_MEMBER
    assert f"def {name}(" in _module_text(path), ROM_GATED_MEMBER
    assert "pytest.skip" in _module_text(path), path


def test_the_adjacency_job_runs_both_orders_in_the_test_stage():
    """Prevents: the runner existing with no CI job calling it in both orders.

    The job must be a ``stage: test`` job, which is also what makes
    ``deploy-site``'s non-optional ``needs`` have to name it:
    ``tests/unit/test_ci_gui_surface.py`` computes that set from the stage.
    """
    config = yaml.safe_load(CI_CONFIG.read_text(encoding="utf-8"))
    job = config[ADJACENCY_JOB]
    assert job.get("stage") == "test", (ADJACENCY_JOB, job.get("stage"))
    script = [str(step) for step in job.get("script") or []]
    for order in ORDERS:
        assert any(f"-Order {order}" in step for step in script), (order, script)
    required = {
        need.get("job") if isinstance(need, dict) else need
        for need in config["deploy-site"].get("needs") or []
        if not (isinstance(need, dict) and need.get("optional"))
    }
    assert ADJACENCY_JOB in required, required


def test_the_runner_module_is_importable_the_way_the_job_invokes_it():
    """Prevents: a module name that does not resolve.

    The job runs ``python -m scripts.adjacency_run``, which needs
    ``scripts/adjacency_run.py`` importable as a module from the repository root,
    and the module's own name is what the argument parser's choices come from.
    """
    spec = importlib.util.find_spec("scripts.adjacency_run")
    assert spec is not None, "scripts/adjacency_run.py is not importable"
    origin = Path(spec.origin or "")
    assert origin.name == "adjacency_run.py", origin
    assert origin.parent.name == "scripts", origin
    assert re.search(r"^ADJACENCY_SET: tuple\[str, \.\.\.\] = \(", _module_text(
        "scripts/adjacency_run.py"
    ), re.MULTILINE), "the script no longer declares ADJACENCY_SET as a tuple literal"
