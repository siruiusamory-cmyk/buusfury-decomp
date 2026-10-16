"""TEXT-TOOL-UI-001 - the release surface of Buu's Fury Text Editor.

Four claims, each proved where it can actually fail:

* **the frozen build is *this* product.** The spec names the package's own entry
  shim and not another product's, which is the mistake this repository has already
  paid for once.
* **the one identity is spelled the same way four times.** The version resource a
  stranger reads in the file's properties dialog, the ``--version`` string and the
  four integers the resource carries all come from ``identity.py``; a drift between
  them is how a release ends up named one version and reporting another.
* **the resources a frozen build needs at runtime travel.** The icons are reached by
  name at runtime rather than by an import, so the packaging template is the only
  place that can declare them, and this is the check that it did.
* **the release definition is registered.** The shared release guard reads one
  product list, and a product that is not in it is not held to the shared rules.

The executable half of the release - that the frozen artefact starts and reports its
version - cannot run in CI at all, because PyInstaller does not cross-compile to
win64. It is driven by ``scripts/smoke-buufury-text-packaged.ps1``, which asserts the
same visible version this file reads from the resource.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import tomllib  # noqa: E402

import pytest  # noqa: E402

from tools.buufury_text.identity import PRODUCT_NAME, PRODUCT_VERSION, VERSION_TUPLE  # noqa: E402
from tools.quality import public_release  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPOSITORY_ROOT / f"{PRODUCT_NAME}.spec.in"
VERSION_RESOURCE = REPOSITORY_ROOT / f"{PRODUCT_NAME}.version.txt"
LAUNCHER = REPOSITORY_ROOT / f"{PRODUCT_NAME}.cmd"
PRODUCT_PACKAGE = REPOSITORY_ROOT / "tools" / "buufury_text"
ENTRY_SCRIPT = "tools/buufury_text/_pyinstaller_entry.py"
ENTRY_MODULE = "tools.buufury_text._pyinstaller_entry"

#: The module that owns the identity. It is the one file allowed to spell the
#: version literal, and the test below is what keeps it the only one.
IDENTITY_MODULE = PRODUCT_PACKAGE / "identity.py"

_VERSION_STRING = re.compile(r'StringStruct\("(\w+)",\s*"((?:[^"\\]|\\.)*)"\)')
_VERSION_TUPLE = re.compile(r"\b(filevers|prodvers)=\(([^)]*)\)")


def _spec_text() -> str:
    return SPEC.read_text(encoding="utf-8")


def _frozen_arguments(text: str) -> str:
    """The argument list of the one EXE() call, which is what PyInstaller reads.

    Read as a block rather than searched for across the file: the template documents
    the release guard's spelling of the version wiring in its own prose, and a search
    over the whole file would read that sentence instead of the argument.
    """
    match = re.search(r"^exe = EXE\((.*?)^\)", text, re.DOTALL | re.MULTILINE)
    assert match is not None, "the spec declares no EXE()"
    return match.group(1)


def _argument(text: str, name: str) -> str | None:
    """The value of ``name=``, whichever quoting style it uses.

    The value is read rather than the line, because a product name with an
    apostrophe in it cannot be spelled with single quotes in Python source and the
    release guard's own screen, which is documented in the template, reads the
    single-quoted form.
    """
    match = re.search(rf"\b{name}=(\"([^\"]*)\"|'([^']*)')", text)
    if match is None:
        return None
    return match.group(2) if match.group(2) is not None else match.group(3)


def _version_quad() -> str:
    return ".".join(str(field) for field in VERSION_TUPLE)


# --- the packaging definition ------------------------------------------------


def test_the_spec_freezes_this_product_and_no_other():
    """The frozen script list names this package's shim, and nothing else's.

    The sibling application's shim and the beta workbench are both real modules that
    a spec could name by accident, and a released executable that runs the wrong one
    is the defect this checks for.
    """
    spec = _spec_text()

    assert f"'{ENTRY_SCRIPT}'" in spec
    frozen = re.search(r"Analysis\(\s*\[([^\]]*)\]", spec)
    assert frozen is not None
    assert f"'{ENTRY_SCRIPT}'" in frozen.group(1)
    assert "workbench" not in frozen.group(1)
    assert "dragonbyte" not in frozen.group(1)

    shim = (PRODUCT_PACKAGE / "_pyinstaller_entry.py").read_text(encoding="utf-8")
    assert "from tools.buufury_text.app import main" in shim


def test_the_console_script_runs_the_product():
    """``buufury-text`` is what a user types after an install."""
    document = tomllib.loads(
        (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert (
        document["project"]["scripts"]["buufury-text"]
        == "tools.buufury_text.app:main"
    )


def test_the_launcher_a_user_double_clicks_runs_the_product():
    """The front door. A comment naming another product is fine, so the check reads
    the command line rather than the prose."""
    launcher = LAUNCHER.read_text(encoding="utf-8")
    started = [
        line.strip()
        for line in launcher.splitlines()
        if line.strip().lower().startswith(("start ", "python", ".venv"))
    ]

    assert started, "the launcher starts nothing"
    for line in started:
        assert "-m tools.buufury_text" in line, line
        assert "workbench" not in line, line
        assert "dragonbyte" not in line, line


def test_the_spec_declares_the_version_resource_the_icon_and_the_icon_directory():
    spec = _spec_text()
    frozen = _frozen_arguments(spec)

    assert _argument(frozen, "version") == VERSION_RESOURCE.name
    assert _argument(frozen, "icon") == public_release.ICON
    # The release guard reads the wiring as a single-quoted literal, which Python
    # source cannot spell while the product name carries an apostrophe. The template
    # records that form in its own documentation, and this keeps the sentence from
    # being tidied away and the guard from going blind to the version resource.
    assert f"version='{VERSION_RESOURCE.name}'" in spec

    # The icons are resolved by name at runtime and by nothing in the import graph,
    # so a directory that travels is the whole of the declaration.
    icon_source = re.search(r"^_ICON_DIRECTORY = '([^']*)'$", spec, re.MULTILINE)
    assert icon_source is not None, "the spec declares no icon directory"
    icons = REPOSITORY_ROOT / icon_source.group(1)
    assert icons.is_dir(), icons
    assert list(icons.glob("*.svg")), f"no SVG icons under {icons}"
    datas = re.search(r"^\s*datas=\[(.*?)\]", spec, re.MULTILINE)
    assert datas is not None, "the spec declares no datas list"
    assert "_ICON_DIRECTORY" in datas.group(1), datas.group(1)

    # A file-extension lookup, not an import: the Qt SVG module has to be named for
    # the build to carry the plugin that reads these files.
    assert "'PySide6.QtSvg'" in spec
    # The frozen build is a directory: an editor with a Qt runtime is not the single
    # executable a randomizer's release is, and the shape is declared, not implied.
    assert "exclude_binaries=True" in spec
    assert "COLLECT(" in spec


def test_the_icon_directory_travels_to_where_the_theme_looks_for_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """The frozen lookup and the packaging destination are one fact, checked together.

    In a checkout the theme reads the icons beside its own module, so a spec that
    staged them anywhere else would look correct here and show no icons at all in a
    release.
    """
    pytest.importorskip("PySide6.QtWidgets")
    from tools.buufury_text import theme

    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    destination = theme._icon_directory().relative_to(tmp_path).as_posix()

    datas = re.search(r"^\s*datas=\[(.*?)\]", _spec_text(), re.MULTILINE)
    assert datas is not None, "the spec declares no datas list"
    assert f"(_ICON_DIRECTORY, '{destination}')" in datas.group(1), datas.group(1)


def test_the_spec_and_its_entry_script_are_registered_with_the_shared_guard():
    """The one product list, not a second copy of the release rules."""
    product = next(
        (item for item in public_release.PRODUCTS if item.package == "buufury_text"),
        None,
    )
    assert product is not None, "the product is not in public_release.PRODUCTS"
    assert product.build_name == PRODUCT_NAME
    assert product.release_shape == "installed"
    assert product.spec == SPEC.name
    assert product.version_resource == VERSION_RESOURCE.name

    findings = [
        item
        for item in public_release.scan()["findings"]
        if item["product"] == PRODUCT_NAME
    ]
    assert findings == []


# --- the one identity --------------------------------------------------------


def test_the_version_resource_matches_the_identity_authority():
    """The resource is a second spelling of one identity, and this fails when the
    two disagree - which is the whole reason ``identity.py`` is the only place the
    version literal is allowed to live."""
    text = VERSION_RESOURCE.read_text(encoding="utf-8")
    fields = dict(_VERSION_STRING.findall(text))
    fixed = dict(_VERSION_TUPLE.findall(text))

    assert fields["ProductName"] == PRODUCT_NAME
    assert fields["InternalName"] == PRODUCT_NAME
    assert fields["OriginalFilename"] == f"{PRODUCT_NAME}.exe"
    assert fields["FileVersion"] == _version_quad()
    assert fields["ProductVersion"] == _version_quad()
    assert fields["FileVersion"] == fields["ProductVersion"]
    assert set(fixed) == {"filevers", "prodvers"}
    assert {tuple(int(part) for part in value.split(",")) for value in fixed.values()} == {
        VERSION_TUPLE
    }


def test_only_the_identity_module_spells_the_version_in_the_product_package():
    """A second literal is how a release reports one version and ships another."""
    for path in sorted(PRODUCT_PACKAGE.rglob("*.py")):
        if path == IDENTITY_MODULE:
            continue
        assert PRODUCT_VERSION not in path.read_text(encoding="utf-8"), path
