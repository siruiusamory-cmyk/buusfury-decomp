"""What the two randomizer *releases* must and must not contain.

The products are two frozen executables, and a frozen build contains exactly what
its entry point can reach. Nothing in the ordinary test suite can see that on its
own: a function-local import does not appear in ``sys.modules`` unless it runs,
and a source scan of one file cannot tell what the rest of the graph pulls in. It
was exactly that gap that mattered - until EXE-PACKAGE-HYGIENE-001 moved the ROM
catalog loader out of ``cli.py``, both executables carried the whole command
surface because one module imported the CLI for a single function.

So the graph is walked statically here, starting from the same entry script each
spec template freezes, and every import in every reachable file counts, at any
nesting depth. ``tools/webfoot/catalog.py`` exists so that the products can reach
the shared catalog rule without reaching the CLI, and these tests are what keep
that from being undone.

Two rules live here: one about the module graph, one about the identity the
executable claims. Both are cheap to keep and expensive to lose silently.
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PREFIX = "tools.webfoot"

#: The entry script each spec template freezes, and the product identity beside it.
PRODUCTS = (
    ("enemyrand", "Enemy-Randomizer"),
    ("warprand", "Buu-Fury-Warp-Randomizer"),
)

#: Modules the frozen randomizers carried before EXE-PACKAGE-HYGIENE-001 and must
#: not reach again. Measured, not guessed: this is the difference between the
#: project modules inside the baseline executable and the project modules inside
#: the rebuilt one. A whole package is named once, because a new submodule of a
#: removed package is the same defect.
#:
#: ``tools.webfoot.workbench`` is deliberately NOT here: the window legitimately
#: uses ``workbench.theme``, and forbidding the package by name would fail a
#: correct build.
COMMAND_SURFACE = (
    "tools.webfoot.analysis",
    "tools.webfoot.atlas",
    "tools.webfoot.atlas_build",
    "tools.webfoot.atlas_producers",
    "tools.webfoot.authored_image",
    "tools.webfoot.authored_placements",
    "tools.webfoot.build",
    "tools.webfoot.cli",
    "tools.webfoot.commands",
    "tools.webfoot.compressed_dialogue",
    "tools.webfoot.dialogue",
    "tools.webfoot.graphics",
    "tools.webfoot.graphics_authoring",
    "tools.webfoot.handles",
    "tools.webfoot.map_chunk",
    "tools.webfoot.map_layout_write",
    "tools.webfoot.map_paint",
    "tools.webfoot.map_render",
    "tools.webfoot.map_resize",
    "tools.webfoot.relocation",
    "tools.webfoot.relocation_proof",
    "tools.webfoot.text",
    "tools.webfoot.tileset_compositor",
    "tools.webfoot.data.behavior_triggers",
    "tools.webfoot.data.script_effects",
    "tools.webfoot.formats.ascii_text_tables",
    "tools.webfoot.formats.indexed_png",
)

#: Modules a correct closure must contain. Without these a broken walker could
#: return an empty set and pass every rule below by proving nothing.
REQUIRED = (
    "tools.webfoot.catalog",
    "tools.webfoot.write",
    "tools.webfoot.randomizer.service",
    "tools.webfoot.enemy_randomizer.planner",
)

_VERSION_STRING = re.compile(r'StringStruct\("(\w+)",\s*"((?:[^"\\]|\\.)*)"\)')
_VERSION_TUPLE = re.compile(r"\b(filevers|prodvers)=\(([^)]*)\)")


def _module_path(name: str) -> Path | None:
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, AttributeError, ValueError):
        return None
    if spec is None or not spec.origin or not spec.origin.endswith(".py"):
        return None
    return Path(spec.origin)


def _is_package(name: str) -> bool:
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, AttributeError, ValueError):
        return False
    return spec is not None and spec.submodule_search_locations is not None


def _base_module(node: ast.ImportFrom, package: str) -> str:
    """The absolute module an ``ImportFrom`` resolves against, relative or not."""
    if not node.level:
        return node.module or ""
    parts = package.split(".")
    trimmed = parts[: len(parts) - node.level + 1]
    return ".".join([*trimmed, node.module]) if node.module else ".".join(trimmed)


def _imported_names(source: Path, package: str) -> set[str]:
    """Every project module this file names, including function-local imports.

    Parsed rather than executed, because the defect this guards against was a
    ``from .cli import ...`` inside a function that a frozen build still bundles
    and a live interpreter never runs.

    Only names under :data:`PREFIX` are resolved: resolving a third-party alias
    such as ``PySide6.QtWidgets.QApplication`` would import a widget toolkit to
    answer a question about this project's own modules.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _base_module(node, package)
            if base:
                found.add(base)
            if base != PREFIX and not base.startswith(PREFIX + "."):
                continue
            for alias in node.names:
                if alias.name != "*" and _module_path(f"{base}.{alias.name}"):
                    found.add(f"{base}.{alias.name}")
    return found


def _project_closure(entry: Path) -> set[str]:
    """Every project module reachable from an entry script, packages included.

    Importing ``a.b.c`` also runs ``a`` and ``a.b``, so a package's ``__init__``
    is part of the graph whether or not anything names it.
    """
    reached: set[str] = set()
    pending = list(_imported_names(entry, ""))
    while pending:
        name = pending.pop()
        if name in reached or not name.startswith(PREFIX):
            continue
        reached.add(name)
        parent = name.rpartition(".")[0]
        while parent.startswith(PREFIX) and parent not in reached:
            reached.add(parent)
            pending.append(parent)
            parent = parent.rpartition(".")[0]
        path = _module_path(name)
        if path is not None:
            package = name if _is_package(name) else name.rpartition(".")[0]
            pending.extend(_imported_names(path, package))
    return reached


def _entry(package: str) -> Path:
    return REPO_ROOT / "tools" / "webfoot" / package / "_pyinstaller_entry.py"


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_walk_sees_a_closure_worth_checking(package: str, build_name: str):
    """A control for the two rules below: the graph must actually be walked.

    Measured against the shipped builds, the walk returns the same 68 project
    modules each executable carries. If it ever returns a small set - because an
    entry point moved, or a resolution changed - this fails rather than letting
    the rules pass on nothing.
    """
    reached = _project_closure(_entry(package))

    missing = sorted(name for name in REQUIRED if name not in reached)
    assert missing == [], f"the walk from {package} missed {missing}"
    assert len(reached) >= 60, f"the walk from {package} found only {len(reached)} modules"


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_a_release_reaches_no_part_of_the_command_surface(package: str, build_name: str):
    reached = _project_closure(_entry(package))
    offenders = sorted(
        name
        for name in reached
        if any(name == part or name.startswith(part + ".") for part in COMMAND_SURFACE)
    )

    assert offenders == [], (
        f"the {build_name} release would bundle the command surface it never "
        f"runs: {offenders}. Reach shared code through its own module - for the "
        "ROM catalog that is tools.webfoot.catalog - rather than through "
        "tools.webfoot.cli."
    )


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_version_resource_names_the_product_it_is_built_into(package: str, build_name: str):
    """The Windows metadata must be the product's own identity, not a copy.

    Read by parsing rather than by evaluating the file: the expression in it is
    PyInstaller's, and a build-time dependency on PyInstaller would make this
    test skip in the portable gate, which is where it is worth the most.
    """
    service = REPO_ROOT / "tools" / "webfoot" / package / "service.py"
    source = service.read_text(encoding="utf-8")

    def constant(name: str) -> str:
        match = re.search(rf'^{name} = "([^"]*)"$', source, flags=re.MULTILINE)
        assert match is not None, f"{service.name} does not define {name}"
        return match.group(1)

    resource = REPO_ROOT / f"{build_name}.version.txt"
    text = resource.read_text(encoding="utf-8")
    fields = dict(_VERSION_STRING.findall(text))

    assert fields["ProductName"] == constant("TOOL_NAME"), (
        f"{resource.name} names a different product than {service.name} reports"
    )
    version = constant("TOOL_VERSION")
    padded = ".".join([*version.split("."), *(["0"] * (4 - version.count(".") - 1))])
    assert fields["FileVersion"] == padded
    assert fields["ProductVersion"] == padded
    assert fields["OriginalFilename"] == f"{build_name}.exe"
    assert fields["InternalName"] == build_name

    # The Details tab reads "File version" from the fixed info, not from the
    # strings, so a stale tuple is a wrong number on screen even when the strings
    # agree.
    numeric = {
        name: tuple(int(part) for part in value.split(","))
        for name, value in _VERSION_TUPLE.findall(text)
    }
    expected = tuple(int(part) for part in padded.split("."))
    assert numeric == {"filevers": expected, "prodvers": expected}, (
        f"{resource.name} declares {numeric}, which is not {expected}"
    )


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_spec_freezes_the_identity_and_the_icon_the_release_carries(package: str, build_name: str):
    spec = (REPO_ROOT / f"{build_name}.spec.in").read_text(encoding="utf-8")
    assert f"version='{build_name}.version.txt'" in spec
    assert "icon='scripts/randomizer.ico'" in spec
    assert (REPO_ROOT / "scripts" / "randomizer.ico").is_file()
