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
- the ``test-integration`` job must run the ROM-gated directory's one ROM-free
  member by name rather than collecting the directory, because every other file
  there skips without the canonical image and a job that skipped everything
  would exit 0 without running anything.

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
import subprocess
import sys

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

#: The job that validates the built site. Named alongside the suite in the deploy
#: job's dependencies, because `needs` bypasses the stage barrier.
SITE_JOB = "test-site"

#: The job that runs the one ROM-free member of the ROM-gated directory, and the
#: member itself. The selection must be that file by name: every other file under
#: ``tests/integration`` skips without the canonical image, so collecting the
#: directory would produce a job that exits 0 over a wall of skips.
INTEGRATION_JOB = "test-integration"
INTEGRATION_MEMBER = "tests/integration/test_container_decode_synthetic.py"

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


def test_the_deploy_job_needs_both_test_jobs():
    """Prevents: publishing a commit whose portable suite or site check never ran.

    ``deploy-site`` matches only the default branch, while both test jobs' second
    rule skips them when that branch push has an open merge request. A
    rule-excluded job cannot fail anything, so without these dependencies the
    deploy job publishes regardless of whether they ran. The dependencies must be
    required, not ``optional``: an optional need is silently dropped when the job
    is absent from the pipeline, which is the exact case being closed. Both jobs
    are named because ``needs`` bypasses the stage barrier, so naming only the
    suite would drop the wait on the site job that the barrier used to give.
    """
    config = _ci_config()
    deploy = config.get("deploy-site") or {}
    needs = deploy.get("needs") or []
    required = {
        need.get("job") if isinstance(need, dict) else need
        for need in needs
        if not (isinstance(need, dict) and need.get("optional"))
    }
    # Every job in the test stage, not a fixed pair: a new test job added later
    # must be waited on too, or `needs` will silently bypass it.
    test_stage = {
        name
        for name, job in config.items()
        if isinstance(job, dict) and job.get("stage") == "test"
    }
    assert test_stage, f"{_cited('stage: test')}: no test-stage job found"
    assert required == test_stage, (
        f"{_cited('deploy-site')}: deploy-site must require a non-optional "
        f"`needs:` entry for every test-stage job {sorted(test_stage)}; its "
        f"required needs are {sorted(required)}, so a pipeline whose jobs were "
        f"excluded by their rules can still publish the site without them"
    )


def test_a_collapsed_required_module_fails_the_process_exit_code(tmp_path) -> None:
    """Under CI a collapsed required GUI module must leave the PROCESS non-zero.

    The guard has always reported the collapse; what was measured is that the exit path
    carried the status it read before the guard decided, so the process exited 0 over a
    collapsed shipping surface and the job went green. PySide6 is forced unimportable by
    shadowing it with a package that raises, which is what a missing Qt does, so the module
    collapses through its own module-level guard exactly as it does in a bare environment.
    """
    shadow = tmp_path / "shadow" / "PySide6"
    shadow.mkdir(parents=True)
    (shadow / "__init__.py").write_text("raise ImportError('forced by the test')\n")
    repository = Path(__file__).resolve().parents[2]
    module = sorted(REQUIRED_GUI_MODULES)[0]
    environment = dict(os.environ, GITLAB_CI="1", PYTHONPATH=str(shadow.parent))
    environment.pop("WEBFOOT_KEEP_INTERPRETER_EXIT", None)
    # A passing file beside the collapse is what makes this the real case: at the moment the
    # session status is first readable it is 0, because nothing failed, and only the guard
    # raises it. With the collapse alone the status is already 5, so an exit path that read it
    # too early would still look correct.
    run = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/{module}",
         "tests/unit/test_public_release.py", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=repository, env=environment)
    assert "COLLAPSED" in run.stdout, run.stdout[-2000:]
    assert run.returncode != 0, (
        f"a collapsed required module beside a passing file exited {run.returncode}\n"
        f"{run.stdout[-2000:]}")


def test_the_exit_status_is_read_after_the_guard_decides_it(monkeypatch) -> None:
    """The status the CI exit path carries must be the one the guard decided.

    This is the defect itself, at the hook, rather than at the process: the guard raises the
    session to TESTS_FAILED, and a status read before it carries the 0 the passing tests left
    behind, so `pytest_unconfigure` exits clean over a collapsed shipping surface. The
    subprocess test above shows the end-to-end exit; this one fails the moment the read moves
    back above the guard, which is what the control run checks.
    """
    import types

    from tests import conftest

    monkeypatch.setattr(conftest, "_collapsed_required_modules",
                        lambda: [("unit/test_build_panel_guard.py", "contributed no test")])
    monkeypatch.setattr(conftest, "_collapsed_gui_modules", lambda: [])
    monkeypatch.setattr(conftest, "_required_gui_surface_is_enforced", lambda: True)
    monkeypatch.setattr(conftest, "_report_collapsed_modules", lambda *a, **k: None)
    monkeypatch.setattr(conftest, "_report_skipped_tests", lambda *a, **k: None)
    monkeypatch.setattr(conftest, "_SESSION_EXIT_STATUS", int(pytest.ExitCode.INTERNAL_ERROR))
    session = types.SimpleNamespace(exitstatus=0, config=None)
    conftest.pytest_sessionfinish(session, 0)
    assert conftest._SESSION_EXIT_STATUS == pytest.ExitCode.TESTS_FAILED, (
        "the exit path would carry a status the guard had already overruled")
    # And the decision reaches the process: the same hook that must not report SUCCESS
    # over an unfinished session reports exactly the status the guard decided here.
    monkeypatch.setenv("CI", "1")
    monkeypatch.delenv("WEBFOOT_KEEP_INTERPRETER_EXIT", raising=False)
    captured: list[int] = []

    def capture(code):
        captured.append(int(code))
        raise SystemExit(code)

    monkeypatch.setattr(conftest.os, "_exit", capture)
    with pytest.raises(SystemExit):
        conftest.pytest_unconfigure(types.SimpleNamespace())
    assert captured == [int(pytest.ExitCode.TESTS_FAILED)], (
        f"the exit path carried {captured} instead of the status the guard decided")


def test_the_ci_exit_path_carries_the_runs_status(monkeypatch) -> None:
    """The exit path carries a status that is not SUCCESS when no session finished.

    The status is a module global that only ``pytest_sessionfinish`` overwrites, and the
    hook does not run when the session dies before it: a raising ``pytest_sessionstart``,
    or an earlier ``sessionfinish`` hook doing the same, as an xdist worker that cannot
    start would. Seeded with ``pytest.ExitCode.OK`` the exit path would then publish a
    green pipeline over an errored run, which is worse than the crash it hides. The exit
    is captured rather than taken, so the status handed to the process is read directly.
    """
    import types

    from tests import conftest

    assert conftest._SESSION_EXIT_STATUS == int(pytest.ExitCode.INTERNAL_ERROR), (
        f"the seed is {conftest._SESSION_EXIT_STATUS!r}, so a session that never reached "
        "pytest_sessionfinish would be reported with that status")
    monkeypatch.setenv("CI", "1")
    monkeypatch.delenv("WEBFOOT_KEEP_INTERPRETER_EXIT", raising=False)
    captured: list[int] = []

    def capture(code):
        captured.append(int(code))
        raise SystemExit(code)

    monkeypatch.setattr(conftest.os, "_exit", capture)
    with pytest.raises(SystemExit):
        conftest.pytest_unconfigure(types.SimpleNamespace())
    assert captured and captured[0] != pytest.ExitCode.OK, (
        f"the exit path carried {captured} for a run that never reached sessionfinish")


def test_the_session_hooks_are_defined_and_have_run() -> None:
    """A scripted edit consumed an anchor line once and took ``pytest_configure`` with it.

    The insertion replaced an anchor line that carried
    ``def pytest_configure(config: pytest.Config) -> None:``, so the definition vanished and
    its body stayed behind as unreachable code inside ``capture_application``. Everything it
    did - the temp-root redirect, the fault handler and the rootdir capture - silently
    stopped running while the rest of the suite passed, and the ``tmp_path`` failures that
    resulted read like the machine rather than this file. Reading the two things the hook is
    responsible for makes that deletion fail here instead of there.
    """
    from tests import conftest

    assert callable(getattr(conftest, "pytest_configure", None)), (
        "tests/conftest.py does not define pytest_configure at module level, so pytest "
        "never calls it and its body is dead code: the temp-root redirect, the fault "
        "handler and the rootdir capture are all lost"
    )
    assert conftest._ROOTDIR == Path(__file__).resolve().parents[2], (
        f"pytest_configure did not run: _ROOTDIR is {conftest._ROOTDIR!r}, and a collection "
        "report's node id is resolved against it"
    )


def test_the_integration_job_runs_the_rom_free_member_by_name():
    """Prevents: an integration job that cannot fail because everything skipped.

    Every file under ``tests/integration`` except the one named here carries its
    own ``roms/...`` guard, so a job whose selection is that directory collects
    over a thousand members, skips all of them and exits 0: a green pipeline that
    executed nothing. The named selection is the whole defence, so it is asserted
    rather than described - against the directory being collected, against the
    member being renamed away or losing the ``rom`` gate that keeps it in the
    directory the name points at, and against a rule edit that silently excludes
    this job from the pipelines its sibling runs in.
    """
    config = _ci_config()
    job = config[INTEGRATION_JOB]
    tokens = [
        token for step in job.get("script") or [] for token in str(step).split()
    ]

    assert job.get("stage") == "test", (INTEGRATION_JOB, job.get("stage"))
    assert INTEGRATION_MEMBER in tokens, (
        f"{_cited('test-integration')}: {INTEGRATION_JOB} must run "
        f"{INTEGRATION_MEMBER} by name; its script is {job.get('script')!r}"
    )
    assert (
        "tests/integration" not in tokens and "tests/integration/" not in tokens
    ), (
        f"{_cited('test-integration')}: {INTEGRATION_JOB} must not collect the "
        "ROM-gated directory; every member of it except the named file skips "
        "without the canonical image, so the job would exit 0 having run nothing"
    )
    assert (REPOSITORY_ROOT / INTEGRATION_MEMBER).is_file(), INTEGRATION_MEMBER
    assert "rom" in gates_for(INTEGRATION_MEMBER), gates_for(INTEGRATION_MEMBER)
    assert job.get("rules") == config[TEST_JOB].get("rules"), (
        f"{_cited('test-integration')}: {INTEGRATION_JOB} must run wherever "
        f"{TEST_JOB} runs, so the ROM-free member cannot be silently excluded "
        "from the pipelines the suite gate runs in"
    )
