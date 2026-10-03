"""Architecture rules the randomizer foundation must not lose.

ENEMY-RANDOMIZER-EXE-001's addendum states the rules a future randomizer has to
follow rather than restate: a module is semantics and nothing else. These are the
mechanical half of that - the half a reviewer would otherwise have to re-read four
files to check - and they are deliberately small and targeted rather than a
framework of their own.

Every rule below is checked by *parsing* the source rather than by matching text,
so a rule about what a module imports cannot be satisfied or broken by a comment.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tools.webfoot.randomizer import registry

REPO_ROOT = Path(__file__).resolve().parents[2]
FOUNDATION = REPO_ROOT / "tools" / "webfoot" / "randomizer"
MODULE_DIR = FOUNDATION / "modules"

#: The one file in the foundation allowed to know about a widget toolkit.
GUI_MODULE = FOUNDATION / "gui.py"

#: Qt import roots. Anything here in a module would tie an algorithm to a toolkit
#: and make "run this module headlessly" impossible - which is exactly the
#: property the combined-mode proof depends on.
QT_ROOTS = ("PySide6", "PyQt5", "PyQt6", "shiboken6")

#: Bare calls in a module that would open or publish a file. ``dataclasses.replace``
#: is deliberately not in this set, which is why bare and attribute calls are
#: collected separately: a bare ``replace`` is a dataclass copy, an attribute
#: ``.replace`` is a filesystem rename.
BARE_IO_CALLS = frozenset({"open", "emit_image", "ensure_new_destination"})

#: Attribute calls that reach for a path.
ATTRIBUTE_IO_CALLS = frozenset(
    {
        "read_bytes",
        "read_text",
        "write_bytes",
        "write_text",
        "unlink",
        "rename",
        "replace",
        "ensure_not_source_alias",
    }
)


def _foundation_sources() -> list[Path]:
    return sorted(path for path in FOUNDATION.rglob("*.py") if "__pycache__" not in path.parts)


def _module_sources() -> list[Path]:
    return sorted(path for path in MODULE_DIR.rglob("*.py") if "__pycache__" not in path.parts)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_roots(path: Path) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
            elif node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _called_names(path: Path) -> tuple[set[str], set[str]]:
    """The bare and the attribute names this file calls, separately.

    Separately because the two mean different things: ``replace`` as a bare name
    is :func:`dataclasses.replace`, and ``.replace`` is a filesystem rename. A
    rule that conflated them would fail on a dataclass copy.
    """
    bare: set[str] = set()
    attributes: set[str] = set()
    for node in ast.walk(_tree(path)):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            bare.add(function.id)
        elif isinstance(function, ast.Attribute):
            attributes.add(function.attr)
    return bare, attributes


def test_the_foundation_has_modules_to_check():
    assert _module_sources(), "the module directory is empty; this file would prove nothing"


def test_only_the_window_imports_a_widget_toolkit():
    """One GUI implementation, and it is not inside any module."""
    offenders = []
    for path in _foundation_sources():
        if path == GUI_MODULE:
            continue
        if _imported_roots(path) & set(QT_ROOTS):
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == [], (
        "only tools/webfoot/randomizer/gui.py may import Qt; these do not follow "
        f"that rule: {offenders}"
    )


@pytest.mark.parametrize("path", _module_sources(), ids=lambda p: p.name)
def test_a_module_never_opens_or_writes_a_file(path: Path):
    """A module returns changes; it never reaches for a path."""
    bare, attributes = _called_names(path)
    offenders = sorted(
        (bare & BARE_IO_CALLS) | (attributes & ATTRIBUTE_IO_CALLS)
    )

    assert offenders == [], (
        f"{path.relative_to(REPO_ROOT)} calls {offenders}; a module must return "
        "semantic changes and let the application perform every write"
    )


def test_the_shared_service_is_the_only_foundation_writer():
    """One writer, reachable from one place, so no module can bypass ROM safety."""
    callers = []
    for path in _foundation_sources():
        if path.name == "gui.py":
            continue
        bare, _attributes = _called_names(path)
        if "emit_image" in bare:
            callers.append(path.name)

    assert callers == ["service.py"], (
        "emit_image must be called from the application service and nowhere else "
        f"in the foundation; found {callers}"
    )


def test_the_modules_do_not_construct_their_own_application_context():
    """Modules read the run context they are handed, they do not build one."""
    for path in _module_sources():
        roots = _imported_roots(path)
        assert "cli" not in roots, f"{path.name} reaches for the CLI"
        text = path.read_text(encoding="utf-8")
        assert "RandomizerContext(" not in text, (
            f"{path.name} builds its own context; a module receives one so one "
            "image load serves every module in a run"
        )


def test_no_module_uses_a_process_global_random_source():
    """Determinism is a property of the code, not of a promise."""
    for path in _module_sources():
        roots = _imported_roots(path)
        assert "random" not in roots, f"{path.name} imports the random module"
        assert "secrets" not in roots, f"{path.name} imports secrets"


def test_every_registered_module_is_reachable_through_the_registry_alone():
    """The registry is the only list; nothing enumerates modules on its own."""
    for path in _foundation_sources():
        if path.name in {"registry.py", "gui.py"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert "MODULE_CLASSES" not in text, (
            f"{path.name} reads the registry's private list; go through modules()"
        )


def test_the_package_a_headless_caller_imports_never_pulls_in_the_window():
    """``import tools.webfoot.randomizer`` must stay usable with no display.

    Checked on the import graph rather than by spawning a subprocess, because the
    property is about what the package *names*, and a source check cannot be
    defeated by a machine that happens to have a display.
    """
    for path in (FOUNDATION / "__init__.py", FOUNDATION / "service.py"):
        text = path.read_text(encoding="utf-8")
        assert "from .gui" not in text, f"{path.name} imports the window"
        assert "import gui" not in text, f"{path.name} imports the window"

    enemy_service = REPO_ROOT / "tools" / "webfoot" / "enemyrand" / "service.py"
    assert "gui" not in enemy_service.read_text(encoding="utf-8")
    assert "PySide6" not in enemy_service.read_text(encoding="utf-8")


def test_the_registry_order_is_a_declaration_not_an_iteration_order():
    """The registry's order is written down, not derived from imports or a dict."""
    source = (FOUNDATION / "registry.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    orders = [
        node
        for node in tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "MODULE_ORDER"
    ]
    assert len(orders) == 1
    value = orders[0].value
    assert isinstance(value, ast.Tuple)
    assert tuple(
        element.value for element in value.elts if isinstance(element, ast.Constant)
    ) == registry.MODULE_ORDER
