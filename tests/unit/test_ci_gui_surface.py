"""The CI environment contract for the shipping GUI surface.

A GUI suite that passes locally can still never run in CI. When the test job
installs only ``.[dev]``, every PySide6 module and every capstone module
collapses to a single ``SKIPPED`` line, and the job exits 0 while reporting a
green Workbench suite that never executed the shipping surface at all. The tests
in this file therefore do not test the Workbench - they test the *environment CI
promises the Workbench*, so that breaking that promise fails a named test
instead of silently reducing the suite:

- the pip install line must name the ``workbench`` and ``research`` extras;
- the job must set a headless Qt platform, because the runner has no display;
- under CI, PySide6 and capstone must actually be importable here;
- every module in ``REQUIRED_GUI_MODULES`` must exist, carry the ``workbench``
  gate and hold a module-level ``PySide6`` import guard, so the list stays a
  claim about dependency-guarded GUI modules rather than an arbitrary path list;
- the list must cover the named editor regressions (the state and error-surface
  regression, the palette editor, undo/redo and palette cost), which is what
  pins the acceptance criterion durably;
- ``deploy-site`` must need ``test-sdk``, because the deploy job's only rule is
  the default branch while the test job's second rule can exclude it from
  exactly that pipeline, and a rule-excluded job cannot fail anything. Audit
  finding CQA-20 records the hole this asserts shut.

This module imports no PySide6 (and no capstone) at module scope, so it is
always collected and never skips as a whole: the failure it reports must be
visible even in the environment it is complaining about. The companion runtime
half of the guard - a required module that is collected but contributes nothing
fails the session - lives in ``tests/conftest.py``.
"""

from __future__ import annotations

import ast
import importlib.util
import os
from pathlib import Path
import re

import pytest
import yaml

from tests.gates import (
    REPOSITORY_ROOT,
    REQUIRED_GUI_MODULES,
    TESTS_DIRECTORY,
    gates_for,
)

CI_CONFIG = REPOSITORY_ROOT / ".gitlab-ci.yml"

#: The job that runs the portable suite, and therefore the one that must carry
#: the shipping GUI dependency set.
TEST_JOB = "test-sdk"

#: Extras the test job must install for the shipping surface to execute.
REQUIRED_CI_EXTRAS = ("dev", "workbench", "research")

#: Import names the CI job must make available (the distribution names are
#: PySide6 and capstone; the import names are what the guards probe).
REQUIRED_CI_IMPORTS = ("PySide6", "capstone")

_EDITABLE_EXTRAS = re.compile(r"-e\s+\"?'?\.\[(?P<extras>[^\]]*)\]\"?'?")


def _ci_config_text() -> str:
    return CI_CONFIG.read_text(encoding="utf-8")


def _ci_config() -> dict:
    """The parsed CI configuration, so assertions survive YAML line folding."""
    return yaml.safe_load(_ci_config_text())


def _line_number(needle: str, text: str | None = None) -> int | None:
    """The 1-based line of the first occurrence of ``needle``, or None."""
    for number, line in enumerate((text or _ci_config_text()).splitlines(), start=1):
        if needle in line:
            return number
    return None


def _cited(needle: str) -> str:
    """``.gitlab-ci.yml:<line>`` for a message, instead of a bare path."""
    line = _line_number(needle)
    location = f"{CI_CONFIG}:{line}" if line else str(CI_CONFIG)
    return f"{location}: {needle}"


def _job_step(job: dict, *needles: str) -> str:
    """The single ``before_script`` step containing every needle."""
    steps = [str(step) for step in job.get("before_script") or []]
    for step in steps:
        if all(needle in step for needle in needles):
            return step
    raise AssertionError(
        f"{CI_CONFIG}: no {TEST_JOB} before_script step contains "
        + " and ".join(repr(needle) for needle in needles)
        + f"; steps are {steps!r}"
    )


def _in_ci() -> bool:
    return bool(os.environ.get("GITLAB_CI") or os.environ.get("CI"))


def _importable(name: str) -> bool:
    """Whether ``name`` can be imported, without importing it.

    An unavailable dependency normally just has no spec, but a ``sys.meta_path``
    finder that raises (a shim, a broken plugin) means "cannot import" too, and
    this test exists to catch exactly that, so a raise is a False rather than an
    error.
    """
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _has_module_level_pyside6_guard(source: str) -> bool:
    """True when the module body probes PySide6 with ``pytest.importorskip``.

    Parsed rather than grepped: the guard has to be at module level (a probe
    inside a test function would still let the module collapse), and two
    spellings are in use - ``pytest.importorskip("PySide6")`` and
    ``QtWidgets = pytest.importorskip("PySide6.QtWidgets")``.
    """
    for statement in ast.parse(source).body:
        if isinstance(statement, ast.Expr):
            call = statement.value
        elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
            call = statement.value
        else:
            continue
        if not isinstance(call, ast.Call):
            continue
        func = call.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name != "importorskip" or not call.args:
            continue
        try:
            target = ast.literal_eval(call.args[0])
        except ValueError:  # a computed probe target is not a static claim
            continue
        if isinstance(target, str) and target.split(".")[0] == "PySide6":
            return True
    return False


def test_the_ci_job_installs_the_shipping_gui_and_research_extras():
    """Prevents: dropping the extra and turning 15 GUI modules into skips.

    The one-line install is asserted as a whole, so an edit that removes
    ``workbench`` fails this test by name instead of quietly restoring the
    failure this file exists to catch: a green job with the Workbench surface
    never executed.
    """
    job = _ci_config()[TEST_JOB]
    install = _job_step(job, "pip install", "-e")
    match = _EDITABLE_EXTRAS.search(install)
    assert match, (
        "the test job must install the project with extras, as "
        '`-e ".[dev,workbench,research]"`; found: ' + _cited(install)
    )
    installed = {extra.strip() for extra in match.group("extras").split(",")}
    missing = [extra for extra in REQUIRED_CI_EXTRAS if extra not in installed]
    assert not missing, (
        f"{_cited(install)} is missing the {missing} extra(s); the shipping "
        "Workbench modules (tests/gates.py REQUIRED_GUI_MODULES) and the three "
        "capstone modules then collapse to whole-file skips and CI reports green "
        "over a surface it never executed"
    )


def test_the_ci_job_configures_a_headless_qt_platform():
    """Prevents: a GUI job that fails (or hangs) because the runner has no X.

    A Linux CI runner has no display, and these modules construct a real
    ``QApplication`` and real widgets; without this the Qt platform plugin
    cannot initialise.
    """
    job = _ci_config()[TEST_JOB]
    variables = job.get("variables") or {}
    platform = variables.get("QT_QPA_PLATFORM")
    assert platform == "offscreen", (
        f"{_cited('QT_QPA_PLATFORM')}: the {TEST_JOB} job must set "
        f"QT_QPA_PLATFORM=offscreen for the headless runner; it is {platform!r}"
    )


def test_the_required_gui_surface_is_installed_in_this_environment():
    """Prevents: "CI is missing PySide6" reporting as a skip instead of a failure.

    Outside CI this is not a claim about the machine, so it skips with the
    reason. Under CI it is the assertion that turns a broken GUI environment
    into a red job - the direct opposite of the silent whole-file skip this
    file guards against.
    """
    if not _in_ci():
        pytest.skip(
            "CI environment contract: PySide6 and capstone must be importable "
            "in the CI test job, which installs .[dev,workbench,research]; "
            "outside CI this file only checks the contract text"
        )
    missing = [
        name for name in REQUIRED_CI_IMPORTS if not _importable(name)
    ]
    assert not missing, (
        f"CI installs .[dev,workbench,research] and sets QT_QPA_PLATFORM=offscreen "
        f"so that the shipping GUI surface executes, but {missing} cannot be "
        f"imported in this environment; {CI_CONFIG} "
        f"(before_script of {TEST_JOB}) is where that is fixed"
    )


def test_every_required_gui_module_exists_and_is_dependency_guarded():
    """Prevents: the required list decaying into a list of paths nobody checked.

    Each entry must be a real file, carry the ``workbench`` gate and hold a
    module-level PySide6 import guard, which is what makes it a *dependency-
    guarded shipping GUI module* rather than an arbitrary test file, and what
    makes a whole-file skip the failure mode the list is guarding.
    """
    for relative in REQUIRED_GUI_MODULES:
        path = REPOSITORY_ROOT / TESTS_DIRECTORY / relative
        assert path.is_file(), (
            f"{relative} is named in REQUIRED_GUI_MODULES (tests/gates.py) but "
            f"{path} does not exist"
        )
        assert "workbench" in gates_for(relative), (
            f"{relative} is named in REQUIRED_GUI_MODULES but carries the gates "
            f"{gates_for(relative)}, not `workbench`; the gate rules in "
            "tests/gates.py assign that gate to Workbench surfaces"
        )
        source = path.read_text(encoding="utf-8")
        assert _has_module_level_pyside6_guard(source), (
            f"{relative} is named in REQUIRED_GUI_MODULES but has no module-level "
            'pytest.importorskip("PySide6...") guard, so it is not a dependency-'
            "guarded GUI module and does not belong in that list"
        )


def test_the_required_gui_surface_covers_the_named_editor_regressions():
    """Prevents: silently dropping a regression the guarded list must execute.

    The contract names the editor surfaces CI must execute: the state and
    error-surface regression, and the palette editor, undo/redo and palette cost
    regressions. Keeping them named here means a later reorganisation cannot
    "simplify" the guarded list past them.
    """
    required = {
        "unit/test_workbench_state_and_errors.py": (
            "the state and error-surface regression"
        ),
        "unit/test_workbench_graphics.py": "the palette editor",
        "unit/test_workbench_graphics_undo.py": "undo/redo",
        "unit/test_workbench_palette_cost.py": "palette cost",
    }
    missing = sorted(set(required) - set(REQUIRED_GUI_MODULES))
    assert not missing, (
        "REQUIRED_GUI_MODULES (tests/gates.py) must cover the editor regressions "
        "CI is required to execute: "
        + ", ".join(f"{name} ({required[name]})" for name in missing)
    )


def test_a_pyside6_collapse_outside_the_named_list_still_fails_the_session():
    """N-12: the named list is the regression set; the guard covers the rest.

    ``REQUIRED_GUI_MODULES`` names the surfaces CI is required to execute, but a
    Workbench module that carries its own module-level ``pytest.importorskip`` and
    was never registered collapsed to one SKIPPED line and left the job green. The
    guard in ``tests/conftest.py`` is therefore keyed on pytest's own collection
    report: any opened test file whose whole-file skip names PySide6 counts, and a
    file that collapsed for another reason (a missing ROM, say) does not.
    """
    from tests import conftest

    guarded = (
        REPOSITORY_ROOT
        / TESTS_DIRECTORY
        / "unit/test_unregistered_gui_surface_probe.py"
    )
    other = REPOSITORY_ROOT / TESTS_DIRECTORY / "unit/test_map_render.py"
    guarded_key = conftest._path_key(guarded)
    other_key = conftest._path_key(other)
    reason = "could not import 'PySide6.QtTest': No module named 'PySide6'"
    saved = (
        set(conftest._CANDIDATE_TEST_FILES),
        set(conftest._ATTEMPTED_TEST_FILES),
        set(conftest._COLLECTED_TEST_FILES),
        dict(conftest._COLLAPSED_REASONS),
    )
    try:
        conftest._CANDIDATE_TEST_FILES.update({guarded_key, other_key})
        conftest._ATTEMPTED_TEST_FILES.update({guarded_key, other_key})
        conftest._COLLAPSED_REASONS[guarded_key] = reason
        conftest._COLLAPSED_REASONS[other_key] = (
            "canonical ROM or map40 VRAM dump not present"
        )

        collapsed = dict(conftest._collapsed_gui_modules())

        assert collapsed == {
            "unit/test_unregistered_gui_surface_probe.py": reason
        }
    finally:
        (
            conftest._CANDIDATE_TEST_FILES,
            conftest._ATTEMPTED_TEST_FILES,
            conftest._COLLECTED_TEST_FILES,
            conftest._COLLAPSED_REASONS,
        ) = saved


def test_the_deploy_job_needs_the_test_job():
    """Prevents: publishing a commit whose portable suite never ran.

    ``deploy-site`` matches only the default branch, while ``test-sdk``'s second
    rule skips it when that branch push has an open merge request. A
    rule-excluded job cannot fail anything, so without this dependency the deploy
    job publishes regardless of whether the suite ran. The dependency must be
    required, not ``optional``: an optional need is silently dropped when the
    job is absent from the pipeline, which is the exact case being closed.
    """
    deploy = _ci_config().get("deploy-site") or {}
    needs = deploy.get("needs") or []
    required = {
        need.get("job") if isinstance(need, dict) else need
        for need in needs
        if not (isinstance(need, dict) and need.get("optional"))
    }
    assert TEST_JOB in required, (
        f"{_cited('deploy-site:')}: deploy-site must require a `needs:` entry "
        f"naming {TEST_JOB}; its needs are {needs!r}, so a pipeline whose "
        f"{TEST_JOB} was excluded by its rules can still publish the site"
    )
