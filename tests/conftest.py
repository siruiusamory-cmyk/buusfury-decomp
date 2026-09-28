"""Pytest bootstrap.

Two jobs:

1. Put the harness package on sys.path so the tests run from a bare checkout
   with no installation step: `python -m pytest tests` from the repository root.

2. Own the temporary-directory fixtures.

   pytest's stock tmp_path / tmp_path_factory root themselves in the system temp
   directory (`%TEMP%/pytest-of-<user>`). On this machine that path exists with
   broken ACLs, so every test that asks for tmp_path dies at collection with
   `PermissionError: [WinError 5] ... pytest-of-hears` before a single assertion
   runs. Rather than depend on an environment variable and a special command
   line, the fixtures are redefined here to live under `build/`, which is
   gitignored and always writable. The test suite is then reproducible on any
   machine, which is the whole point of a baseline.

These tests are PORTABLE: they must never require a baserom, a reference
checkout, ARM Developer Suite, grit, or a working JCALG1 build. Anything that
needs those lives in the CLI gates (scripts/check.ps1), not here.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

TMP_ROOT = REPO_ROOT / "build" / "pytest-tmp"


def _safe(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "test"
    return cleaned[:100]


def _unique_dir(nodeid: str) -> Path:
    """A short, collision-free directory name derived from a pytest node id."""
    digest = hashlib.sha1(nodeid.encode("utf-8")).hexdigest()[:8]
    return TMP_ROOT / f"{_safe(nodeid)}-{digest}"


@pytest.fixture
def tmp_path(request):
    """Replacement for pytest's tmp_path, rooted under build/ instead of %TEMP%."""
    target = _unique_dir(request.node.nodeid)
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


class _LocalTmpFactory:
    """Minimal stand-in for pytest's TempPathFactory."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._counter = 0

    def mktemp(self, basename: str, numbered: bool = True) -> Path:
        self._counter += 1
        name = f"{_safe(basename)}-{self._counter}" if numbered else _safe(basename)
        target = self._root / name
        target.mkdir(parents=True, exist_ok=True)
        return target

    def getbasetemp(self) -> Path:
        self._root.mkdir(parents=True, exist_ok=True)
        return self._root


@pytest.fixture(scope="session")
def tmp_path_factory():
    """Replacement for pytest's session-scoped tmp_path_factory."""
    shutil.rmtree(TMP_ROOT, ignore_errors=True)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    yield _LocalTmpFactory(TMP_ROOT)
    shutil.rmtree(TMP_ROOT, ignore_errors=True)
