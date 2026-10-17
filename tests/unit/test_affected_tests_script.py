"""The focused-set script lists a consumer that reaches a changed object without importing it.

The rule this pins is the miss shape: a test file constructs an object whose class is
defined in a changed module, and it never imports that module - it reaches the class
through a re-export. An import scan alone reports nothing, so the consumer is the
case that proves the second rule exists.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "affected-tests.ps1"


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments], capture_output=True, text=True, check=True
    )
    return result.stdout


def commit(repository: Path, message: str) -> str:
    git(repository, "add", "--all")
    git(repository, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "--quiet", "-m", message)
    return git(repository, "rev-parse", "HEAD").strip()


@pytest.fixture()
def repository(tmp_path):
    """A repository whose change edits the module a consumer only reaches by re-export."""
    root = tmp_path / "repository"
    (root / "tools" / "pkg").mkdir(parents=True)
    (root / "tests" / "unit").mkdir(parents=True)
    (root / "tools" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tools" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tools" / "pkg" / "core.py").write_text(
        "class Widget:\n    def __init__(self):\n        self.ready = True\n", encoding="utf-8"
    )
    (root / "tools" / "registry.py").write_text(
        "from tools.pkg.core import Widget  # re-export\n", encoding="utf-8"
    )
    (root / "tests" / "unit" / "test_unrelated.py").write_text(
        "def test_nothing():\n    assert True\n", encoding="utf-8"
    )
    git(root, "init", "--quiet")
    base = commit(root, "the tree before the change")

    # The change edits the defining module only. The re-export module the consumer
    # imports is untouched, so an import scan of the consumer finds nothing.
    (root / "tools" / "pkg" / "core.py").write_text(
        "class Widget:\n    def __init__(self):\n        self.ready = True\n\n"
        "    def describe(self):\n        return 'widget'\n",
        encoding="utf-8",
    )
    (root / "tests" / "unit" / "test_consumer.py").write_text(
        "from tools import registry\n\n\n"
        "def test_the_consumer_builds_the_object():\n"
        "    assert registry.Widget().ready\n",
        encoding="utf-8",
    )
    commit(root, "the change under test")
    return root, base


def test_a_consumer_that_only_reaches_the_object_is_listed(repository):
    root, base = repository
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
         "-Base", base],
        capture_output=True, text=True, cwd=root,
    )
    assert result.returncode == 0, result.stderr
    listed = result.stdout.split()
    assert "tests/unit/test_consumer.py" in listed, result.stdout
    assert "tests/unit/test_unrelated.py" not in listed, result.stdout
