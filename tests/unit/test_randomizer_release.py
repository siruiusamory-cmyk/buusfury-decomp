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
which is what makes a further product impossible to register with the guard and
leave out of these rules. Everything product-specific - the frozen entry script,
the identity module, the package a frozen application also reaches, the modules a
walk must arrive at and the smallest closure it was measured to return - is data
on that product's own :class:`~tools.quality.public_release.ReleaseProduct` row.
This file therefore branches on the release SHAPE, which is two facts, and never on
which product it is looking at.
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

#: The entry script each spec template freezes, the identity module beside it and the
#: modules a walk from it must reach. The list is the release guard's own, not a
#: second copy of it: a product added to ``public_release.PRODUCTS`` is checked here
#: in the same run, so a future executable cannot be registered with the release
#: guard and left out of these rules.
PRODUCTS = public_release.PRODUCTS

#: Modules the frozen randomizers carried before EXE-PACKAGE-HYGIENE-001 and must
#: not reach again. Measured, not guessed: this is the difference between the
#: project modules inside the baseline executable and the project modules inside
#: the rebuilt one. A whole package is named once, because a new submodule of a
#: removed package is the same defect.
#:
#: ``tools.webfoot.workbench`` is deliberately NOT here: an application legitimately
#: uses ``workbench.theme``, and forbidding the package by name would fail a correct
#: build.
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

#: The shapes, named once, so the rules below cannot disagree about which products
#: each applies to.
_ARCHIVE = "archive"
_INSTALLED = "installed"

_VERSION_STRING = re.compile(r'StringStruct\("(\w+)",\s*"((?:[^"\\]|\\.)*)"\)')
_VERSION_TUPLE = re.compile(r"\b(filevers|prodvers)=\(([^)]*)\)")


def _module_file(module: str) -> Path:
    """The file one dotted module name resolves to, from the repository root."""
    return REPO_ROOT / Path(*module.split(".")).with_suffix(".py")


def _entry(product: public_release.ReleaseProduct) -> Path:
    """The script this product's spec template freezes.

    Read from the product's own row rather than assembled from its package name:
    an application lives outside ``tools/webfoot``, and a rule that guessed the
    path would have walked a file that does not exist.
    """
    return _module_file(product.entry_module)


def _roots(product: public_release.ReleaseProduct) -> tuple[str, ...]:
    """The package roots a walk from this product counts.

    An archive's graph is ``tools.webfoot`` alone. A frozen application also reaches
    its own package, and which package that is is the product's declaration rather
    than a constant here. A product that declares neither is a stated failure, not a
    quiet walk of somebody else's tree.
    """
    if product.release_shape == _ARCHIVE:
        return (PREFIX,)
    if not product.application_root:
        raise AssertionError(
            f"{product.build_name} is an installed application and declares no "
            "application_root in public_release.PRODUCTS"
        )
    return (PREFIX, product.application_root)


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


def _imported_names(source: Path, package: str, roots: tuple[str, ...]) -> set[str]:
    """Every project module this file names, including function-local imports.

    Parsed rather than executed, because the defect this guards against was a
    ``from .cli import ...`` inside a function that a frozen build still bundles
    and a live interpreter never runs.

    ``roots`` names the packages that count, and it is passed in rather than read
    from a constant: an application reaches its own package, an archive does not,
    and ``from . import theme`` in an application is a real import that a walker
    which only knew about ``tools.webfoot`` would silently drop.

    Only names under ``roots`` are resolved, and a submodule alias is probed only
    when the base is a package. Both limits exist to keep this from importing
    anything: ``find_spec`` imports a name's parents, so probing
    ``PySide6.QtWidgets.QApplication`` would load a widget toolkit, and so would
    probing ``...enemyrand.gui.main``, whose parent module imports one.
    """
    def is_project(name: str) -> bool:
        return any(name == root or name.startswith(root + ".") for root in roots)

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


def _project_closure(
    entry: Path, roots: tuple[str, ...] = (PREFIX,)
) -> set[str]:
    """Every project module reachable from an entry script, packages included.

    Importing ``a.b.c`` also runs ``a`` and ``a.b``, so a package's ``__init__``
    is part of the graph whether or not anything names it. ``roots`` names the
    packages whose contents count: a randomizer's graph is ``tools.webfoot`` alone,
    and a frozen application's reaches its own package as well.
    """
    def is_project(name: str) -> bool:
        return any(name == root or name.startswith(root + ".") for root in roots)

    reached: set[str] = set()
    pending = list(_imported_names(entry, "", roots))
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
            pending.extend(_imported_names(path, package, roots))
    return reached


@pytest.mark.parametrize("product", PRODUCTS, ids=[p.package for p in PRODUCTS])
def test_the_walk_sees_a_closure_worth_checking(product: public_release.ReleaseProduct):
    """A control for the rules below: the graph must actually be walked.

    Measured against the shipped randomizer builds, the walk returns the same 68
    project modules each executable carries. A frozen application reaches its own
    package as well, and it is not the same size as either archive, so both the
    modules that must be reached and the smallest acceptable closure are that
    product's own measured numbers rather than one shape-wide threshold.
    """
    reached = _project_closure(_entry(product), _roots(product))

    assert product.required_modules, (
        f"{product.build_name} declares no required_modules in "
        "public_release.PRODUCTS, so this control would prove nothing"
    )
    missing = sorted(name for name in product.required_modules if name not in reached)
    assert missing == [], f"the walk from {product.package} missed {missing}"
    assert len(reached) >= product.closure_floor, (
        f"the walk from {product.package} found only {len(reached)} modules, below "
        f"the {product.closure_floor} this product was measured to reach"
    )


@pytest.mark.parametrize("product", PRODUCTS, ids=[p.package for p in PRODUCTS])
def test_an_archive_release_reaches_no_part_of_the_command_surface(
    product: public_release.ReleaseProduct,
):
    """An archive rule, and archived products only.

    A randomizer's release bundles what its entry point can reach, and it runs one
    job; reaching the command surface there means shipping an entire CLI for a
    function that has its own module. An installed application is not held to this
    rule because its destinations legitimately call the atlas, the map reader, the
    text reader and the graphics readers - that is the product, not an accident of
    reachability - and it is named as an exception here rather than left to be
    discovered.
    """
    if product.release_shape != _ARCHIVE:
        pytest.skip(f"{product.build_name} is an installed application, not an archive")

    reached = _project_closure(_entry(product), _roots(product))
    offenders = sorted(
        name
        for name in reached
        if any(name == part or name.startswith(part + ".") for part in COMMAND_SURFACE)
    )

    assert offenders == [], (
        f"the {product.build_name} release would bundle the command surface it never "
        f"runs: {offenders}. Reach shared code through its own module - for the "
        "ROM catalog that is tools.webfoot.catalog - rather than through "
        "tools.webfoot.cli."
    )


@pytest.mark.parametrize("product", PRODUCTS, ids=[p.package for p in PRODUCTS])
def test_the_version_resource_names_the_product_it_is_built_into(
    product: public_release.ReleaseProduct,
):
    """The Windows metadata must be the product's own identity, not a copy.

    Read by parsing rather than by evaluating the file: the expression in it is
    PyInstaller's, and a build-time dependency on PyInstaller would make this
    test skip in the portable gate, which is where it is worth the most.

    Which module owns the identity comes from the product's own row, and which pair
    of constants that module carries follows the shape: a randomizer's ``service.py``
    has ``TOOL_NAME``/``TOOL_VERSION``, an application's ``identity`` module has
    ``PRODUCT_NAME``/``PRODUCT_VERSION``. The comparison is between four-field tuples
    built from each side rather than between two spellings of the same number, so a
    three-field randomizer version and a four-field application version are checked
    by one rule.
    """
    source_path = _module_file(product.identity_module)
    source = source_path.read_text(encoding="utf-8")

    def constant(name: str) -> str:
        match = re.search(rf'^{name} = "([^"]*)"$', source, flags=re.MULTILINE)
        assert match is not None, f"{source_path.name} does not define {name}"
        return match.group(1)

    def four_fields(spelling: str) -> tuple[int, ...]:
        """The four numeric fields of a version, ignoring a pre-release suffix.

        A Windows resource cannot carry ``dev0``, so a product identity's
        pre-release form (``0.9.0.dev0``) and the resource's four fields
        (``0.9.0.0``) are the SAME version spelled where each is legal. Dropping a
        suffix that is not a number is what lets one rule check both shapes.
        """
        numeric = [part for part in re.split(r"[.,]", spelling.strip("() ")) if part.strip()]
        numeric = [part for part in numeric if part.strip().isdigit()]
        padded = numeric if len(numeric) >= 4 else [*numeric, *(["0"] * (4 - len(numeric)))]
        assert len(padded[:4]) == 4, f"{spelling!r} is not four numeric fields"
        return tuple(int(part) for part in padded[:4])

    if product.release_shape == _INSTALLED:
        product_name = constant("PRODUCT_NAME")
        product_version = constant("PRODUCT_VERSION")
    else:
        product_name = constant("TOOL_NAME")
        product_version = constant("TOOL_VERSION")

    resource = REPO_ROOT / f"{product.build_name}.version.txt"
    text = resource.read_text(encoding="utf-8")
    fields = dict(_VERSION_STRING.findall(text))

    assert fields["ProductName"] == product_name, (
        f"{resource.name} names a different product than {source_path.name} reports"
    )
    assert fields["FileVersion"] == fields["ProductVersion"]
    assert four_fields(fields["FileVersion"]) == four_fields(product_version)
    assert fields["OriginalFilename"] == f"{product.build_name}.exe"
    assert fields["InternalName"] == product.build_name

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


@pytest.mark.parametrize("product", PRODUCTS, ids=[p.package for p in PRODUCTS])
def test_the_packaging_script_names_the_version_the_product_reports(
    product: public_release.ReleaseProduct,
):
    """One version source, or the downloaded file lies about what it contains.

    ``$Version`` in the packaging script decides the archive's name, and it is an
    independent literal; before RELEASE-ARTEFACT-001 nothing tied it to the
    product's own ``TOOL_VERSION``, so a release could be named v0.2.0 while the
    executable inside reported 0.1.0. N-30's portable half.

    This is an archive rule: it is about the name of a zip. A product that ships an
    installed directory declares no packaging script and no archive name, and is
    skipped here rather than checked against a rule that does not describe it.
    """
    if product.packager is None:
        pytest.skip(f"{product.build_name} ships an installed directory, not a named archive")
    script = (REPO_ROOT / product.packager).read_text(encoding="utf-8")

    declared = re.search(r"\$Version\s*=\s*'([^']*)'", script)
    assert declared is not None, f"{product.packager} declares no $Version default"
    assert '"$BuildName-v$Version-win64.zip"' in script, (
        f"{product.packager} builds the archive name from something other than "
        "$Version, so the check below would not cover it"
    )

    service = _module_file(product.identity_module).read_text(encoding="utf-8")
    reported = re.search(r'^TOOL_VERSION = "([^"]*)"$', service, flags=re.MULTILINE)
    assert reported is not None, f"{product.identity_module} has no TOOL_VERSION"
    assert declared.group(1) == reported.group(1), (
        f"{product.packager} names the release v{declared.group(1)} while the "
        f"product reports {reported.group(1)}"
    )


@pytest.mark.parametrize("product", PRODUCTS, ids=[p.package for p in PRODUCTS])
def test_the_spec_freezes_the_identity_and_the_icon_the_release_carries(
    product: public_release.ReleaseProduct,
):
    spec = (REPO_ROOT / f"{product.build_name}.spec.in").read_text(encoding="utf-8")
    assert f"version='{product.build_name}.version.txt'" in spec
    assert "icon='scripts/randomizer.ico'" in spec
    assert (REPO_ROOT / "scripts" / "randomizer.ico").is_file()
