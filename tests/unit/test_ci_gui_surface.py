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
  finding CQA-20 records the hole this asserts shut. The same requirement covers
  every test-stage job the default branch can run, and deliberately not a
  test-stage job whose rules narrow it off the default branch: that job cannot be
  in the deploy job's pipeline at all, and a ``needs:`` entry for an excluded job
  fails pipeline creation instead of gating it.
- the ``test-integration`` job must run the ROM-gated directory's one ROM-free
  member by name rather than collecting the directory, because every other file
  there skips without the canonical image and a job that skipped everything
  would exit 0 without running anything; and its install must stay ``.[dev]``,
  because that selection imports no PySide6 and no capstone.
- the ``adjacency`` job must run the fixed app-wide-Qt-state set in both orders,
  because ``test-sdk``'s ``--dist loadfile`` means no module ever follows
  another in one process, and module-to-module Qt state is exactly what that
  hides.

The job bodies live in ``ci\\*.ps1`` and the YAML names the file, because the
four test-stage jobs run on a shell executor on Windows, where ``image:`` is
ignored. Every claim about a job's environment is therefore read from the script
that builds it - the file the YAML step names, resolved here, so a step pointing
at a body that does not exist fails instead of being skipped over. The routing
itself (which jobs run on the self-hosted runner, and that the deploy job does
not) is asserted too, so it cannot drift silently.

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

#: The job that validates the built site. Named alongside the suite in the deploy
#: job's dependencies, because `needs` bypasses the stage barrier.
SITE_JOB = "test-site"

#: The job that runs the one ROM-free member of the ROM-gated directory, and the
#: member itself. The selection must be that file by name: every other file under
#: ``tests/integration`` skips without the canonical image, so collecting the
#: directory would produce a job that exits 0 over a wall of skips.
INTEGRATION_JOB = "test-integration"
INTEGRATION_MEMBER = "tests/integration/test_container_decode_synthetic.py"

#: The job that runs the app-wide-Qt-state adjacency set in one process per
#: order. It is the only place the shipping GUI modules follow one another in a
#: single process, because ``test-sdk`` distributes at module granularity.
ADJACENCY_JOB = "adjacency"

#: The tag of the self-hosted runner on the owner's PC, and the job that must
#: NOT carry it. The four test-stage jobs run there; ``deploy-site`` publishes,
#: reads the protected Cloudflare credential and stays on the shared runners.
LOCAL_CI_TAG = "local-ci"
LOCAL_CI_JOBS = (TEST_JOB, INTEGRATION_JOB, ADJACENCY_JOB, SITE_JOB)
DEPLOY_JOB = "deploy-site"

#: Extras the test job must install for the shipping surface to execute.
REQUIRED_CI_EXTRAS = ("dev", "workbench", "research")

#: Import names the CI job must make available (the distribution names are
#: PySide6 and capstone; the import names are what the guards probe).
REQUIRED_CI_IMPORTS = ("PySide6", "capstone")

#: The editable install's extras. The routed jobs install through the venv
#: helper in ``ci\common.ps1``, so the extras are the ``-Extras`` parameter of
#: ``New-CiVenv``. The claim the assertions below make is unchanged - the project
#: is installed with these extras - and this is the spelling that reaches disk.
_EDITABLE_EXTRAS = re.compile(r"-Extras\s+['\"]?\.\[(?P<extras>[^\]]*)\]['\"]?")

#: The PowerShell body a routed job runs, named in the YAML as ``ci\<name>.ps1``.
#: The job bodies were moved out of ``.gitlab-ci.yml`` so the same script can be
#: run by hand for a measurement; every environment claim about a routed job is
#: therefore asserted against the script that builds the environment rather than
#: against a YAML step that no longer exists.
_CI_SCRIPT = re.compile(r"ci[\\/](?P<name>[A-Za-z0-9_.-]+\.ps1)")


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


def _ci_script_path(job_name: str) -> Path:
    """The ``ci\\<name>.ps1`` body ``job_name``'s ``script`` runs.

    The name is read from the YAML step rather than kept in a second table here,
    so the file this asserts against is the file the job runs: a step that names
    a body which does not exist fails instead of asserting about some other file.
    """
    steps = [str(step) for step in _ci_config()[job_name].get("script") or []]
    for step in steps:
        match = _CI_SCRIPT.search(step)
        if match:
            path = REPOSITORY_ROOT / "ci" / match.group("name")
            assert path.is_file(), (
                f"{_cited_in(job_name, 'script')}: {job_name} runs "
                f"ci\\{match.group('name')}, which does not exist at {path}"
            )
            return path
    raise AssertionError(
        f"{_cited_in(job_name, 'script')}: {job_name} must run its body from "
        f"ci\\<name>.ps1; its script is {steps!r}"
    )


def _ci_script_text(job_name: str) -> str:
    """The PowerShell body ``job_name`` runs, as text."""
    return _ci_script_path(job_name).read_text(encoding="utf-8")


def _job_line(job_name: str, needle: str) -> int | None:
    """The 1-based line of ``needle`` inside ``job_name``'s own block.

    A bare ``_line_number`` search can cite another job: every routed job names a
    ``ci\\*.ps1`` body, so the first such line in the file is ``test-sdk``'s. The
    block is found by the job's own key and ends at the next top-level key, so a
    message about one job cites that job.
    """
    lines = _ci_config_text().splitlines()
    start = _line_number(f"{job_name}:")
    if start is None:
        return None
    end = len(lines)
    for offset in range(start, len(lines)):
        line = lines[offset]
        if line and not line[0].isspace() and ":" in line:
            end = offset
            break
    for offset in range(start, end):
        if needle in lines[offset]:
            return offset + 1
    return None


def _cited_in(job_name: str, needle: str) -> str:
    """``.gitlab-ci.yml:<line>`` for ``needle`` inside ``job_name``."""
    line = _job_line(job_name, needle)
    location = f"{CI_CONFIG}:{line}" if line else f"{CI_CONFIG} ({job_name})"
    return f"{location}: {needle}"


def _installed_extras(job_name: str) -> set[str]:
    """The extras of ``job_name``'s one editable install."""
    script = _ci_script_text(job_name)
    match = _EDITABLE_EXTRAS.search(script)
    assert match, (
        f"{_ci_script_path(job_name)}: {job_name} must install the project with "
        "extras, as `-Extras '.[dev]'`; the install is what that parameter is for"
    )
    return {extra.strip() for extra in match.group("extras").split(",")}


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
    never executed. The install lives in ``ci\\test_sdk.ps1`` after the port to
    the Windows runner: the same claim, read from the script that makes it.
    """
    script = _ci_script_path(TEST_JOB)
    match = _EDITABLE_EXTRAS.search(script.read_text(encoding="utf-8"))
    assert match, (
        f"{script}: the test job must install the project with extras, as "
        "`-Extras '.[dev,workbench,research]'`, because the extras are what turn "
        "fifteen GUI and capstone modules from whole-file skips into executions"
    )
    installed = {extra.strip() for extra in match.group("extras").split(",")}
    missing = [extra for extra in REQUIRED_CI_EXTRAS if extra not in installed]
    assert not missing, (
        f"{script}: the install is missing the {missing} extra(s); the shipping "
        "Workbench modules (tests/gates.py REQUIRED_GUI_MODULES) and the three "
        "capstone modules then collapse to whole-file skips and CI reports green "
        "over a surface it never executed"
    )


def test_the_ci_job_configures_a_headless_qt_platform():
    """Prevents: a GUI job that fails (or hangs) because the runner has no display.

    A CI runner has no display, and these modules construct a real
    ``QApplication`` and real widgets; without this the Qt platform plugin
    cannot initialise. On the Windows runner the setting is also what keeps the
    job independent of a logged-in desktop session.
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
            f"in the {TEST_JOB} job, which installs .[dev,workbench,research]; "
            f"the {INTEGRATION_JOB} job installs .[dev] only. Outside CI this "
            "file only checks the contract text"
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


def _runs_on_the_default_branch(job: dict) -> bool:
    """Whether ``job``'s rules can select it in a default-branch pipeline.

    ``deploy-site`` matches only ``$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH``, and
    it is the only job that can publish. A ``needs:`` entry naming a job that
    pipeline excludes does not wait for it - it fails pipeline creation - so a
    test-stage job whose every rule is explicitly narrowed off the default branch
    cannot be a dependency of the deploy job, and requiring it would break the
    deploy pipeline rather than gate it. Such a job is also unable to publish
    anything on its own. The requirement in the test below is therefore over the
    test-stage jobs the default branch can actually run, and over all of them.

    This is not an opt-out: the only way to leave the set is to give the job
    rules that genuinely exclude the default branch from every one of its
    pipelines, which is what removes it from the deploy path in the first place.

    ponytail: the check is textual - a rule whose condition compares
    ``!= $CI_DEFAULT_BRANCH``. A condition that ORs that comparison with
    something true on the default branch would be judged excluded while still
    being able to run there; that is a ceiling, named here rather than left
    implicit.
    """
    rules = [rule for rule in job.get("rules") or [] if isinstance(rule, dict)]
    if not rules:
        return True
    return not all(
        "!= $CI_DEFAULT_BRANCH" in str(rule.get("if", ""))
        or str(rule.get("when")) == "never"
        for rule in rules
    )


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
    Every test-stage job the default branch can run is required, which is what
    ``_runs_on_the_default_branch`` decides.
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
    # must be waited on too, or `needs` will silently bypass it. GitLab defaults a
    # job's stage to `test`, so a job with no `stage:` key belongs in this set;
    # `script`, `trigger` or `extends` is what makes a top-level block a job
    # rather than a global such as `variables:`. A job the default branch can
    # never run is not in the set, for the reason `_runs_on_the_default_branch`
    # gives.
    test_stage = {
        name
        for name, job in config.items()
        if isinstance(job, dict)
        and any(key in job for key in ("script", "trigger", "extends"))
        and job.get("stage", "test") == "test"
        and _runs_on_the_default_branch(job)
    }
    assert test_stage, f"{_cited('stage: test')}: no test-stage job found"
    assert required == test_stage, (
        f"{_cited('deploy-site')}: deploy-site must require a non-optional "
        f"`needs:` entry for every test-stage job {sorted(test_stage)}; its "
        f"required needs are {sorted(required)}, so a pipeline whose jobs were "
        f"excluded by their rules can still publish the site without them"
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
    tokens = _ci_script_text(INTEGRATION_JOB).split()

    assert job.get("stage") == "test", (INTEGRATION_JOB, job.get("stage"))
    assert INTEGRATION_MEMBER in tokens, (
        f"{_ci_script_path(INTEGRATION_JOB)}: {INTEGRATION_JOB} must run "
        f"{INTEGRATION_MEMBER} by name; it is not among the arguments that "
        "script passes to pytest"
    )
    assert (
        "tests/integration" not in tokens and "tests/integration/" not in tokens
    ), (
        f"{_ci_script_path(INTEGRATION_JOB)}: {INTEGRATION_JOB} must not collect "
        "the ROM-gated directory; every member of it except the named file skips "
        "without the canonical image, so the job would exit 0 having run nothing"
    )
    assert (REPOSITORY_ROOT / INTEGRATION_MEMBER).is_file(), INTEGRATION_MEMBER
    assert "rom" in gates_for(INTEGRATION_MEMBER), gates_for(INTEGRATION_MEMBER)
    assert job.get("rules") == config[TEST_JOB].get("rules"), (
        f"{_cited('test-integration')}: {INTEGRATION_JOB} must run wherever "
        f"{TEST_JOB} runs, so the ROM-free member cannot be silently excluded "
        "from the pipelines the suite gate runs in"
    )


def test_the_integration_job_installs_only_what_its_selection_imports():
    """Prevents: paying for PySide6 and capstone on every merge request.

    The four members of ``tests/integration/test_container_decode_synthetic.py``
    import ``hashlib``, ``json``, ``pathlib``, ``__future__`` and
    ``tools.webfoot.formats``, and that package imports nothing at all. `pytest`
    is the only non-stdlib need, and it is the ``dev`` extra. The job used to
    install ``.[dev,workbench,research]`` - a Qt wheel of about 100 MiB plus
    capstone - for a selection that imports neither.

    ``workbench`` and ``research`` are asserted *absent* rather than merely not
    required, so re-adding one is a failing named test and not a quiet cost.
    ``test-sdk`` keeps them: it runs the shipping GUI and needs them.
    """
    installed = _installed_extras(INTEGRATION_JOB)
    for extra in ("workbench", "research"):
        assert extra not in installed, (
            f"{_ci_script_path(INTEGRATION_JOB)}: {INTEGRATION_JOB} "
            f"installs the {extra!r} extra; {INTEGRATION_MEMBER} imports no PySide6 "
            f"and no capstone, and its install is {sorted(installed)}. Widen the "
            "test above first if the selection really grew a Qt or capstone member"
        )
    assert "dev" in installed, (
        f"{_ci_script_path(INTEGRATION_JOB)}: {INTEGRATION_JOB} must "
        "install the 'dev' extra, which carries pytest; the selection needs no "
        "other test runner"
    )


def test_the_adjacency_job_runs_the_fixed_set_in_both_orders():
    """Prevents: a job that proves Qt state adjacency without exercising it.

    ``test-sdk`` runs the suite under ``--dist loadfile``, so no module ever
    follows another in the same process. This job is the one place the shipping
    GUI modules run back to back in a single process, and both orders are named
    so that neither direction of module-to-module state can be dropped. The set
    itself, the one-member ROM exclusion and the fail-on-skip rule live in
    ``scripts/adjacency_run.py`` and are pinned by
    ``tests/unit/test_adjacency.py``; this test pins the CI half: the job exists,
    is a ``stage: test`` job (so ``deploy-site`` must wait for it), runs both
    orders as separate commands, and runs them in the environment the suite job
    already built and proved.
    """
    config = _ci_config()
    job = config[ADJACENCY_JOB]
    script = [str(step) for step in job.get("script") or []]

    assert job.get("stage") == "test", (ADJACENCY_JOB, job.get("stage"))
    for order in ("forward", "reverse"):
        matching = [step for step in script if f"-Order {order}" in step]
        assert matching, (
            f"{_cited('adjacency')}: {ADJACENCY_JOB} must run "
            f"`-Order {order}`; its script is {script!r}"
        )
    assert "-m scripts.adjacency_run " in _ci_script_text(ADJACENCY_JOB), (
        f"{_ci_script_path(ADJACENCY_JOB)}: {ADJACENCY_JOB} must run "
        "scripts/adjacency_run.py, which is the module that holds the set and "
        "fails on a skip"
    )
    assert job.get("rules") == config[TEST_JOB].get("rules"), (
        f"{_cited('adjacency')}: {ADJACENCY_JOB} must run wherever {TEST_JOB} runs, "
        "so the adjacency orders cannot be silently excluded from the pipelines "
        "the suite gate runs in"
    )
    # The set is the shipping GUI surface, so this job needs the same
    # `.[dev,workbench,research]` install the suite job makes - but it does not
    # make a second one: on the Windows runner it opens that job's venv by name,
    # which is also what `needs: ["test-sdk"]` means here. The claim is therefore
    # split across two scripts and pinned in both: `test-sdk` builds the venv
    # named `test-sdk` with the required extras (the test above asserts those),
    # and this job runs in it. Cutting either half fails here.
    assert "Use-CiVenv -Name 'test-sdk'" in _ci_script_text(ADJACENCY_JOB), (
        f"{_ci_script_path(ADJACENCY_JOB)}: {ADJACENCY_JOB} must run in the "
        f"{TEST_JOB} venv, not build a second environment; the extras the set "
        "needs are the ones that script installs"
    )
    assert "New-CiVenv -Name 'test-sdk'" in _ci_script_text(TEST_JOB), (
        f"{_ci_script_path(TEST_JOB)}: {TEST_JOB} must build the venv the "
        f"{ADJACENCY_JOB} job opens by that name"
    )


def test_the_test_jobs_run_on_the_self_hosted_runner_and_the_deploy_job_does_not():
    """Prevents: silent drift of which runner executes what.

    The four test-stage jobs run on the owner's own machine, tagged
    ``local-ci``, because the shared runners' free monthly quota is spent. They
    are a shell executor on Windows, so they carry no ``image:`` at all - one
    there would be ignored rather than honoured, which is worse than absent
    because it reads like a claim.

    ``deploy-site`` is the opposite: it is the only job that publishes and the
    only one that reads the protected Cloudflare credential, so it stays on the
    shared runners with its ``image:``. Routing it to the owner's PC would put
    the credential on an unprotected runner for no gain, and it is the job that
    has to keep failing loudly while the quota is spent.
    """
    config = _ci_config()
    for name in LOCAL_CI_JOBS:
        job = config[name]
        assert job.get("tags") == [LOCAL_CI_TAG], (
            f"{_cited(name)}: {name} must run on the self-hosted runner, tagged "
            f"{LOCAL_CI_TAG!r}; its tags are {job.get('tags')!r}"
        )
        assert "image" not in job, (
            f"{_cited(name)}: {name} runs on a shell executor, which ignores "
            f"`image:`; its image is {job.get('image')!r} and belongs removed "
            "rather than left reading like a claim"
        )

    deploy = config[DEPLOY_JOB]
    assert LOCAL_CI_TAG not in (deploy.get("tags") or []), (
        f"{_cited(DEPLOY_JOB)}: {DEPLOY_JOB} must stay on the shared runners; it "
        "reads the protected deployment credential and is the job that publishes"
    )
    assert deploy.get("image") == "node:22", (
        f"{_cited(DEPLOY_JOB)}: {DEPLOY_JOB} must keep the image it builds the "
        f"site in; it is {deploy.get('image')!r}"
    )
