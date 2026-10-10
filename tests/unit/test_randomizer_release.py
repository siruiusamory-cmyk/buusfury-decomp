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

:data:`PRODUCTS` is the release guard's own list rather than a second copy of it,
which is what makes a fourth product impossible to register with the guard and
leave out of these rules. One entry is an installed application instead of an
archive, so the graph rule carries a control for each shape, the firewall rule is
an archive rule and says so, and the identity rules read whichever module owns the
identity for that product.
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import pytest

from tools.quality import public_release

REPO_ROOT = Path(__file__).resolve().parents[2]
PREFIX = "tools.webfoot"
APPLICATION_PREFIX = "tools.dragonbyte"

#: The entry script each spec template freezes, and the product identity beside
#: it. The list is the release guard's own, not a second copy of it: a product
#: added to ``public_release.PRODUCTS`` is checked here in the same run, so a
#: future executable cannot be registered with the release guard and left out of
#: these rules.
PRODUCTS = tuple(
    (product.package, product.build_name) for product in public_release.PRODUCTS
)

#: The packages whose build an installed application's own entry module freezes:
#: the application lives outside ``tools/webfoot``, so the walk below has to be
#: told where to start and which root to follow. Everything else about the rules
#: here - the closure, the identity, the spec wiring - applies to both shapes.
APPLICATION_ENTRY_MODULES = {"dragonbyte": "tools.dragonbyte._pyinstaller_entry"}

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

#: A frozen build of one product shape reaches modules no other shape reaches.
#: Without naming them, a broken walker could return a small set and pass every
#: rule below by proving nothing.
REQUIRED_BY_SHAPE = {
    "archive": (
        "tools.webfoot.catalog",
        "tools.webfoot.write",
        "tools.webfoot.randomizer.service",
        "tools.webfoot.enemy_randomizer.planner",
    ),
    "installed": (
        "tools.dragonbyte.app",
        "tools.dragonbyte.session",
        "tools.dragonbyte.shell",
        "tools.webfoot.catalog",
        "tools.webfoot.write",
        "tools.webfoot.release_identity",
    ),
}

#: The shapes, named once, so the parametrized rules below cannot disagree about
#: which products each applies to.
_ARCHIVE = "archive"
_INSTALLED = "installed"


def _shape(package: str) -> str:
    product = next(item for item in public_release.PRODUCTS if item.package == package)
    return product.release_shape


def _roots(package: str) -> tuple[str, ...]:
    if _shape(package) == _INSTALLED:
        return (PREFIX, APPLICATION_PREFIX)
    return (PREFIX,)


def _identity_module(package: str) -> str:
    """The module that owns a product's identity, per shape.

    A randomizer carries ``TOOL_NAME``/``TOOL_VERSION`` in its own ``service.py``;
    an installed application reads the repository's one identity authority, which
    is the whole reason its version resource is a second spelling of that module
    and not a second identity.
    """
    if _shape(package) == _INSTALLED:
        return "tools/webfoot/release_identity.py"
    return f"tools/webfoot/{package}/service.py"

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

    Only names under :data:`PREFIX` or :data:`APPLICATION_PREFIX` are resolved, and
    a submodule alias is probed only when the base is a package. Both limits exist
    to keep this from importing anything: ``find_spec`` imports a name's parents,
    so probing ``PySide6.QtWidgets.QApplication`` would load a widget toolkit, and
    so would probing ``...enemyrand.gui.main``, whose parent module imports one.
    """
    def is_project(name: str) -> bool:
        return any(
            name == root or name.startswith(root + ".")
            for root in (PREFIX, APPLICATION_PREFIX)
        )

    found: set[str] = set()
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _base_module(node, package)
            if base:
                found.add(base)
            if not is_project(base):
                continue
            if not _is_package(base):
                continue
            for alias in node.names:
                if alias.name != "*" and _module_path(f"{base}.{alias.name}"):
                    found.add(f"{base}.{alias.name}")
    return found


def _project_closure(entry: Path, roots: tuple[str, ...] = (PREFIX,)) -> set[str]:
    """Every project module reachable from an entry script, packages included.

    Importing ``a.b.c`` also runs ``a`` and ``a.b``, so a package's ``__init__``
    is part of the graph whether or not anything names it. ``roots`` names the
    packages whose contents count: a randomizer's graph is ``tools.webfoot`` alone,
    and the installed application's reaches ``tools.dragonbyte`` as well.
    """
    def is_project(name: str) -> bool:
        return any(name == root or name.startswith(root + ".") for root in roots)

    reached: set[str] = set()
    pending = list(_imported_names(entry, ""))
    while pending:
        name = pending.pop()
        if name in reached or not is_project(name):
            continue
        reached.add(name)
        parent = name.rpartition(".")[0]
        while is_project(parent) and parent not in reached:
            reached.add(parent)
            parent = parent.rpartition(".")[0]
        path = _module_path(name)
        if path is not None:
            package = name if _is_package(name) else name.rpartition(".")[0]
            pending.extend(_imported_names(path, package))
    return reached


def _entry(package: str) -> Path:
    if package in APPLICATION_ENTRY_MODULES:
        return REPO_ROOT / Path(*APPLICATION_ENTRY_MODULES[package].split(".")).with_suffix(
            ".py"
        )
    return REPO_ROOT / "tools" / "webfoot" / package / "_pyinstaller_entry.py"


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_walk_sees_a_closure_worth_checking(package: str, build_name: str):
    """A control for the rules below: the graph must actually be walked.

    Measured against the shipped randomizer builds, the walk returns the same 68
    project modules each executable carries. The installed application reaches its
    own package as well, so its required set is its own - and both are checked, so
    a walk that returned a small set for either shape fails here rather than letting
    the rules below pass on nothing.
    """
    reached = _project_closure(_entry(package), _roots(package))

    required = REQUIRED_BY_SHAPE[_shape(package)]
    missing = sorted(name for name in required if name not in reached)
    assert missing == [], f"the walk from {package} missed {missing}"
    assert len(reached) >= 60, f"the walk from {package} found only {len(reached)} modules"


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_an_archive_release_reaches_no_part_of_the_command_surface(
    package: str, build_name: str
):
    """An archive rule, and archived products only.

    A randomizer's release bundles what its entry point can reach, and it runs one
    job; reaching the command surface there means shipping an entire CLI for a
    function that has its own module. The installed application is not held to this
    rule because its destinations legitimately call the atlas, the map reader, the
    text reader and the graphics readers - that is the product, not an accident of
    reachability - and it is named as an exception here rather than left to be
    discovered.
    """
    if _shape(package) != _ARCHIVE:
        pytest.skip(f"{build_name} is an installed application, not an archive")

    reached = _project_closure(_entry(package), _roots(package))
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

    Which module owns the identity depends on the shape (see
    :func:`_identity_module`), and the comparison is between four-field tuples
    built from each side rather than between two spellings of the same number, so a
    three-field randomizer version and a four-field application version are checked
    by one rule.
    """
    source_path = REPO_ROOT / _identity_module(package)
    source = source_path.read_text(encoding="utf-8")

    def constant(name: str) -> str:
        match = re.search(rf'^{name} = "([^"]*)"$', source, flags=re.MULTILINE)
        assert match is not None, f"{source_path.name} does not define {name}"
        return match.group(1)

    def four_fields(spelling: str) -> tuple[int, ...]:
        """The four numeric fields of a version, ignoring a pre-release suffix.

        A Windows resource cannot carry ``dev0``, so the product identity's
        pre-release form (``0.9.0.dev0``) and the resource's four fields
        (``0.9.0.0``) are the SAME version spelled where each is legal. Dropping a
        suffix that is not a number is what lets one rule check both shapes.
        """
        numeric = [part for part in re.split(r"[.,]", spelling.strip("() ")) if part.strip()]
        numeric = [part for part in numeric if part.strip().isdigit()]
        padded = numeric if len(numeric) >= 4 else [*numeric, *(["0"] * (4 - len(numeric)))]
        assert len(padded[:4]) == 4, f"{spelling!r} is not four numeric fields"
        return tuple(int(part) for part in padded[:4])

    if _shape(package) == _INSTALLED:
        product_name = constant("PRODUCT_NAME")
        product_version = constant("PRODUCT_VERSION")
    else:
        product_name = constant("TOOL_NAME")
        product_version = constant("TOOL_VERSION")

    resource = REPO_ROOT / f"{build_name}.version.txt"
    text = resource.read_text(encoding="utf-8")
    fields = dict(_VERSION_STRING.findall(text))

    assert fields["ProductName"] == product_name, (
        f"{resource.name} names a different product than {source_path.name} reports"
    )
    assert fields["FileVersion"] == fields["ProductVersion"]
    assert four_fields(fields["FileVersion"]) == four_fields(product_version)
    assert fields["OriginalFilename"] == f"{build_name}.exe"
    assert fields["InternalName"] == build_name

    # The Details tab reads "File version" from the fixed info, not from the
    # strings, so a stale tuple is a wrong number on screen even when the strings
    # agree.
    numeric = {
        name: tuple(int(part) for part in value.split(","))
        for name, value in _VERSION_TUPLE.findall(text)
    }
    assert numeric == {
        "filevers": four_fields(product_version),
        "prodvers": four_fields(product_version),
    }, f"{resource.name} declares {numeric}"


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_packaging_script_names_the_version_the_product_reports(package: str, build_name: str):
    """One version source, or the downloaded file lies about what it contains.

    ``$Version`` in the packaging script decides the archive's name, and it is an
    independent literal; before RELEASE-ARTEFACT-001 nothing tied it to the
    product's own ``TOOL_VERSION``, so a release could be named v0.2.0 while the
    executable inside reported 0.1.0. N-30's portable half.

    This is an archive rule: it is about the name of a zip. A product that ships an
    installed directory declares no packaging script and no archive name, and is
    skipped here rather than checked against a rule that does not describe it.
    """
    product = next(item for item in public_release.PRODUCTS if item.package == package)
    if product.packager is None:
        pytest.skip(f"{build_name} ships an installed directory, not a named archive")
    script = (REPO_ROOT / product.packager).read_text(encoding="utf-8")

    declared = re.search(r"\$Version\s*=\s*'([^']*)'", script)
    assert declared is not None, f"{product.packager} declares no $Version default"
    assert '"$BuildName-v$Version-win64.zip"' in script, (
        f"{product.packager} builds the archive name from something other than "
        "$Version, so the check below would not cover it"
    )

    service = (REPO_ROOT / "tools" / "webfoot" / package / "service.py").read_text(
        encoding="utf-8"
    )
    reported = re.search(r'^TOOL_VERSION = "([^"]*)"$', service, flags=re.MULTILINE)
    assert reported is not None, f"tools/webfoot/{package}/service.py has no TOOL_VERSION"
    assert declared.group(1) == reported.group(1), (
        f"{product.packager} names the release v{declared.group(1)} while the "
        f"product reports {reported.group(1)}"
    )


@pytest.mark.parametrize("package,build_name", PRODUCTS, ids=[p[0] for p in PRODUCTS])
def test_the_spec_freezes_the_identity_and_the_icon_the_release_carries(package: str, build_name: str):
    spec = (REPO_ROOT / f"{build_name}.spec.in").read_text(encoding="utf-8")
    assert f"version='{build_name}.version.txt'" in spec
    assert "icon='scripts/randomizer.ico'" in spec
    assert (REPO_ROOT / "scripts" / "randomizer.ico").is_file()
