"""Shared pytest configuration: focused gates and a usable temporary root.

Two things live here, both test-infrastructure only - no shipped behaviour is
configured from this file.

**Focused gates.** Every collected test is tagged with the gates defined in
``tests/gates.py`` (``fast``, ``workbench``, ``writer``, ``map``,
``research``, ``rom``), so a ticket can run ``pytest -m writer`` instead of
reconstructing a path list. The tagging is additive and does not change what
an unqualified ``pytest`` run collects. ``docs/testing.md`` documents the
gates; ``tests/unit/test_test_gates.py`` checks the registry.

**A usable temporary root.** ``tmp_path`` must not resolve inside the
repository, and must not resolve into a temp root the process cannot read or
write. A ``tmp_path`` under the work tree makes the generated-output guards
refuse paths they are right to refuse (the tests that expect an accepted
output fail by design), and an unusable default root makes every ``tmp_path``
test error out before it runs. This module therefore states the requirement
once, up front, instead of leaving it to whoever reads the thirtieth
``PermissionError``.
"""

from __future__ import annotations

import getpass
import os
from pathlib import Path
import tempfile

import pytest

from tests.gates import GATE_DESCRIPTIONS, REPOSITORY_ROOT, gates_for

#: Set by :func:`pytest_configure` when pytest's own temporary root is unusable
#: and this module redirected the process temp root to an isolated one.
_REDIRECTED_TEMPROOT: tuple[Path, str] | None = None

#: The canonical Buu's Fury image every ROM-gated family reads, in the two
#: spellings the suite accepts, plus the default location under the repo root.
_ROM_ENVIRONMENT_VARIABLES = ("WEBFOOT_BUU_ROM", "LOGX_CANONICAL_ROM")
_ROM_DEFAULT = Path("roms") / "Dragon Ball Z - Buu's Fury (U).gba"
_CANONICAL_ROM_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


def pytest_configure(config: pytest.Config) -> None:
    """Make the temp root one ``tmp_path`` can actually live in.

    pytest derives its basetemp from ``tempfile.gettempdir()``, so redirecting
    that root - rather than pinning ``--basetemp`` - keeps every other property
    of the default path: a numbered ``pytest-N`` subdirectory, the
    ``tmp_path_retention_count`` pruning of old failed runs, removal of the
    whole root after a green run, and safety between two runs that happen to
    share a worktree (a pinned ``--basetemp`` is deleted at startup, so
    concurrent runs would destroy each other's directories mid-run).

    ``tempfile.tempdir`` is read lazily, on the first basetemp request, so this
    does not depend on hook ordering relative to ``_pytest.tmpdir``. Nothing in
    this repository reads the process temp root itself; only pytest's own
    temporary directories move.
    """
    global _REDIRECTED_TEMPROOT

    if config.option.basetemp is not None:
        # An explicit --basetemp is the caller's choice and wins outright.
        return

    temproot = Path(tempfile.gettempdir()).resolve()
    default_root = temproot / f"pytest-of-{_user_name()}"
    problem = _temp_root_problem(default_root)
    if problem is None:
        return

    isolated_root = temproot / f"webfoot-pytest-temproot-{_user_name()}"
    if _temp_root_problem(isolated_root) is not None:
        # Nothing better to offer: let pytest report its own failure rather
        # than redirecting to a root that is just as unusable.
        return
    tempfile.tempdir = str(isolated_root)
    _REDIRECTED_TEMPROOT = (isolated_root, problem)


def pytest_report_header(config: pytest.Config) -> list[str]:
    """State the gates, the temporary root and the ROM situation, once."""
    lines = [
        "test gates: " + " | ".join(f"-m {gate}" for gate in GATE_DESCRIPTIONS),
        "gate docs: docs/testing.md",
    ]

    if _REDIRECTED_TEMPROOT is not None:
        root, problem = _REDIRECTED_TEMPROOT
        lines.append(
            f"temp root: {root} (pytest's own {problem}; the process temp root "
            "was redirected, and --basetemp overrides it)"
        )
    else:
        basetemp = config.option.basetemp
        root = Path(basetemp) if basetemp else Path(tempfile.gettempdir())
        lines.append(f"temp root: {root}")
        if basetemp and Path(basetemp).resolve().is_relative_to(REPOSITORY_ROOT):
            lines.append(
                "temp root WARNING: --basetemp is inside the repository, so the "
                "generated-output guards will refuse those paths and the "
                "output-safety tests that expect an accepted output will fail by "
                "design (test_asset_export_output_safety, and the mGBA capture "
                "build-tree check when the root is under build/); choose a "
                "directory outside the work tree"
            )

    lines.append(_rom_status())
    if Path.cwd().resolve() != REPOSITORY_ROOT:
        lines.append(
            f"working directory WARNING: {Path.cwd()} is not {REPOSITORY_ROOT}; "
            "tests that read config/, upstreams.lock or roms/ relatively will fail"
        )
    return lines


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Tag every collected test with the gates its file belongs to."""
    for item in items:
        for gate in gates_for(item.path):
            item.add_marker(getattr(pytest.mark, gate))


def _user_name() -> str:
    try:
        return getpass.getuser()
    except Exception:  # pragma: no cover - platform user lookup failure
        return "unknown"


def _temp_root_problem(root: Path) -> str | None:
    """Why ``root`` cannot serve as pytest's temporary root, or None if it can.

    Mirrors what ``_pytest.tmpdir.TempPathFactory.getbasetemp`` needs: create
    the directory if absent, enumerate it to pick a free run number, and write
    inside it. A fence that denies any of those turns *every* ``tmp_path`` test
    into an error, which is worth detecting before the run rather than after
    it. The reason names which of the three failed, and the probe file is
    removed again immediately.
    """
    probe = root / f".webfoot-writable-{os.getpid()}"
    try:
        root.mkdir(mode=0o700, exist_ok=True)
    except OSError as exc:
        return f"{root.name} cannot be created here ({_os_error_detail(exc)})"
    try:
        with os.scandir(root):
            pass
    except OSError as exc:
        return f"{root.name} cannot be read here ({_os_error_detail(exc)})"
    try:
        probe.write_bytes(b"")
        probe.unlink()
    except OSError as exc:
        return f"{root.name} cannot be written here ({_os_error_detail(exc)})"
    return None


def _os_error_detail(exc: OSError) -> str:
    return exc.strerror or type(exc).__name__


def _rom_status() -> str:
    """A one-line statement of which ROM, if any, the ROM gate will use."""
    for variable in _ROM_ENVIRONMENT_VARIABLES:
        configured = os.environ.get(variable)
        if configured and Path(configured).is_file():
            return f"rom gate: {variable}={configured}"
    if _ROM_DEFAULT.is_file():
        return f"rom gate: {_ROM_DEFAULT} ({_CANONICAL_ROM_SHA256[:12]}...)"
    return (
        "rom gate: no canonical image found, `-m rom` will skip; set "
        + " or ".join(_ROM_ENVIRONMENT_VARIABLES)
        + f", or place {_ROM_DEFAULT}"
    )
