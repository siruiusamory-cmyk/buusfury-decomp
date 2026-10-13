"""Executable/public-release guard for the repository's frozen products.

The Map Warp Randomizer and the Enemy Randomizer are two frozen executables that
a stranger downloads and runs. DragonByte Z is the third frozen product and the
one that is an installed application rather than a two-file archive. What makes
each of them a *public release* rather than a build is a small set of facts spread
across a handful of files: the spec template that freezes the module graph, the
version resource that names the product on screen, the project icon, the README
that travels in the archive, and the packaging script that decides what the
archive contains. Those facts were established one product at a time by
WARPRAND-APP-001, ENEMY-RANDOMIZER-EXE-001 and EXE-PACKAGE-HYGIENE-001. This
module is what keeps a fourth product from inheriting only some of them.

What is deliberately NOT repeated here
--------------------------------------

Three neighbouring checks already own their ground, and duplicating them would
mean two implementations that can disagree:

* the import closure of each frozen build, and the agreement between a version
  resource and its product's own ``TOOL_NAME``/``TOOL_VERSION``, are enforced by
  ``tests/unit/test_randomizer_release.py``, which takes its product list from
  this module rather than keeping a second one;
* the byte-level proprietary-content probe over the real staged files is
  ``scripts/randomizer-release.ps1``, which runs at packaging time;
* the tree-wide wording and machine-path screens are
  ``tools/quality/public_surface.py``, whose screens this module reuses rather
  than re-implements.

What is left, and what this module checks, is the static release DEFINITION: that
the packaging shape is complete for every product, that it is the two-file
release it claims to be, and that no release input carries a machine of its own.
Those are the facts no other gate reads on its own.

The wiring this module proves (that the spec points at the version resource and
the icon) overlaps one assertion in that test on purpose: this guard is meant to
be runnable by a release engineer with `python -m tools.quality.public_release`
and nothing else, so it does not defer the whole question to pytest. What it does
NOT repeat is the value agreement, which the test alone can prove.

What "no ROM input" means here
------------------------------

The canonical image is a *probe* input to the packaging script, never a staged
one, so its default path is expected to appear in the script and is not a
finding. The check is on the edges that decide what travels: the spec's
``datas`` list and every path the script touches under the stage directory. A
ROM, save or save state named on any of those is a release defect.

Fail closed
-----------

A release input that exists but cannot be decoded is a finding of its own kind
and stops the run, exactly as ``tools/quality/public_surface.py`` treats an
unreadable file: counting it as checked while checking nothing would make the
guard cleanest where it is blind.

Adding a product
----------------

Append one :class:`ReleaseProduct` to :data:`PRODUCTS` and add the four files it
names. Nothing else is product-specific: every product runs through the same
loop, a ``*.spec.in`` at the repository root or a ``scripts/package-*.ps1`` that
no product declares fails the run, and the identity test beside this module
reads the same list. A future randomizer release therefore cannot be defined
without being held to the same rules.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.quality import public_surface

#: Bumped when the report document's shape changes in a way a reader must notice.
SCHEMA = 1

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The one icon both products ship, generated from the project's own
#: ``public/favicon.svg`` by ``scripts/make-randomizer-icon.py``.
ICON = "scripts/randomizer.ico"

#: The shared release checks both packaging scripts dot-source. A product that
#: does not reach it is not running the proprietary-content probe at all.
SHARED_RELEASE_SCRIPT = "scripts/randomizer-release.ps1"

#: The Windows resource fields every shipped product must declare. The values
#: are checked against the product's own identity constants by
#: ``tests/unit/test_randomizer_release.py``; here it is enough that each field
#: exists and is non-empty, so a blank property dialog cannot ship.
REQUIRED_METADATA = (
    "CompanyName",
    "FileDescription",
    "FileVersion",
    "InternalName",
    "LegalCopyright",
    "OriginalFilename",
    "ProductName",
    "ProductVersion",
)

#: Suffixes that are never a release input. The same set the shared PowerShell
#: probe refuses at packaging time, kept here so the static definition check
#: catches it before a build is ever run.
FORBIDDEN_SUFFIXES = frozenset(
    {
        ".gba", ".agb", ".sav", ".srm", ".sps", ".state", ".dump",
        ".ss0", ".ss1", ".ss2", ".ss3", ".ss4", ".ss5", ".ss6", ".ss7",
        ".ss8", ".ss9",
    }
)

#: The icon sizes a Windows application icon must cover: the shell's small and
#: large list sizes, the taskbar, and the high-DPI view.
ICON_SIZES = frozenset({(16, 16), (32, 32), (48, 48), (256, 256)})

#: The residue a release input can still carry, and that the tree-wide screen
#: deliberately does not claim. Its machine-path screen rejects a path into a
#: user profile; a release input must also be repository-relative, so any
#: drive-letter path is a finding here, as is the name of the local worktree the
#: file was written in.
RELEASE_RESIDUE: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "an absolute path",
        re.compile(r"(?<![A-Za-z0-9+.\-/])[A-Za-z]:[\\/](?![\\/])"),
    ),
    (
        "a machine environment path",
        re.compile(
            r"\$(?:env:)?(?:USERPROFILE|TEMP|TMP|LOCALAPPDATA|APPDATA)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "a local checkout directory name",
        re.compile(r"\blog1-remake-[A-Za-z0-9][A-Za-z0-9._-]*"),
    ),
)

_STRING_STRUCT = re.compile(r'StringStruct\("(\w+)",\s*"((?:[^"\\]|\\.)*)"\)')
_FIXED_INFO = re.compile(r"\b(filevers|prodvers)=\(([^)]*)\)")
_VERSION_TUPLE = re.compile(r"\s*\d+(\s*,\s*\d+){3}\s*")
_STAGE_LITERAL = re.compile(r"Join-Path\s+\$stage\s+(?:'([^']*)'|\"([^\"]*)\")")
_STAGE_DESTINATION = re.compile(
    r"Copy-Item\s+\S+\s+\(Join-Path\s+\$stage\s+(?:'([^']*)'|\"([^\"]*)\")\)"
)
_COPY_ITEM = re.compile(r"(?m)^\s*Copy-Item\b")
_SPEC_DATAS = re.compile(r"datas\s*=\s*\[(.*?)\]", re.DOTALL)
_SPEC_ANALYSIS = re.compile(r"Analysis\(\s*\[([^\]]*)\]", re.DOTALL)
_SPEC_RESOURCE_PAIR = re.compile(r"\(\s*'([^']*)'\s*,\s*'([^']*)'\s*\)")
_QUOTED = re.compile(r"'([^']*)'|\"([^\"]*)\"")
_COPY_SOURCE = re.compile(r"(?m)^\s*Copy-Item\s+(\S+)")
_PARAMETER = re.compile(r"\$(BuildName|ReadmePath)\s*=\s*(?:'([^']*)'|\"([^\"]*)\")")


@dataclass(frozen=True)
class ReleaseProduct:
    """One frozen product, and the files that define its release.

    A product that is not a randomizer declares no ``readme`` and no ``packager``:
    it ships as an installed directory rather than as a two-file archive, and the
    staged-package rules below belong to the archive shape that has one. What every
    registered product keeps is the spec, the version resource and the icon, which
    is the release DEFINITION, and the checks for those do not depend on the shape.

    The frozen-BUILD facts live here too - the script the spec freezes, the module
    that owns the identity, the package a frozen application also reaches - because
    ``tests/unit/test_randomizer_release.py`` reads this one list rather than
    keeping a table of its own. A product added here is therefore walked, identified
    and version-checked by the same rules as every other, with no second edit.
    """

    package: str
    build_name: str
    readme: str | None
    packager: str | None
    #: The module the spec's ``Analysis`` freezes, dotted. Required: a frozen build
    #: whose entry script nobody can name is a product nothing can walk.
    entry_module: str
    #: The module that owns the product's identity, dotted. A randomizer's own
    #: ``service.py`` carries ``TOOL_NAME``/``TOOL_VERSION``; an installed
    #: application's ``identity`` module carries ``PRODUCT_NAME``/``PRODUCT_VERSION``.
    #: Which pair is read follows the shape, but which FILE is read is this field.
    identity_module: str
    #: The package root a frozen application's walk also counts. ``None`` for an
    #: archive, whose graph is ``tools.webfoot`` alone.
    application_root: str | None = None
    #: Modules a walk from ``entry_module`` must reach. A walk that stopped early
    #: would otherwise pass every rule below by proving nothing.
    required_modules: tuple[str, ...] = ()
    #: The smallest module closure that walk was measured to return for THIS product.
    #: One number for every product would be a reading of the largest of them.
    closure_floor: int = 60
    #: ``"archive"`` for a randomizer's two-file release, ``"installed"`` for an
    #: application shipped as a directory beside its runtime. It is a declared
    #: shape rather than something a reader infers from the two optional files, so
    #: a reader that has to treat the two differently has one fact to read.
    release_shape: str = "archive"

    @property
    def spec(self) -> str:
        return f"{self.build_name}.spec.in"

    @property
    def version_resource(self) -> str:
        return f"{self.build_name}.version.txt"


#: The SDK modules a frozen randomizer must reach: the ROM catalog reader it
#: identifies an image with, the write path it produces one through, the randomizer
#: service and the planner it runs. Measured as the difference between the shipped
#: build and the rebuild that followed EXE-PACKAGE-HYGIENE-001. The two archives are
#: one build shape and reach the same modules, so the names are declared once and
#: named by both rows rather than copied into each.
ARCHIVE_REQUIRED_MODULES = (
    "tools.webfoot.catalog",
    "tools.webfoot.write",
    "tools.webfoot.randomizer.service",
    "tools.webfoot.enemy_randomizer.planner",
)

#: The one place a product is declared. Adding a product means adding an entry here
#: and the files it names; every rule below then applies to it without an edit.
PRODUCTS: tuple[ReleaseProduct, ...] = (
    ReleaseProduct(
        package="enemyrand",
        build_name="Enemy-Randomizer",
        readme="docs/enemyrand/README.txt",
        packager="scripts/package-enemy-randomizer.ps1",
        entry_module="tools.webfoot.enemyrand._pyinstaller_entry",
        identity_module="tools.webfoot.enemyrand.service",
        required_modules=ARCHIVE_REQUIRED_MODULES,
    ),
    ReleaseProduct(
        package="warprand",
        build_name="Buu-Fury-Warp-Randomizer",
        readme="docs/warprand/README.txt",
        packager="scripts/package-warprand.ps1",
        entry_module="tools.webfoot.warprand._pyinstaller_entry",
        identity_module="tools.webfoot.warprand.service",
        required_modules=ARCHIVE_REQUIRED_MODULES,
    ),
    # The frozen desktop application. It is registered here for the same reason
    # the randomizers are: its spec, its version resource and its icon are a
    # release definition, and a definition nobody declares is exactly what
    # `_unregistered` exists to catch. Its release is `dist/<name>/<name>.exe`
    # beside the Qt runtime, so no packager is declared yet and the two-file
    # archive rules below do not apply to it.
    #
    # Its identity lives outside its own package, in the repository's one identity
    # authority, which is also where its version resource is checked from.
    ReleaseProduct(
        package="dragonbyte",
        build_name="DragonByte Z",
        readme=None,
        packager=None,
        release_shape="installed",
        entry_module="tools.dragonbyte._pyinstaller_entry",
        identity_module="tools.webfoot.release_identity",
        application_root="tools.dragonbyte",
        required_modules=(
            "tools.dragonbyte.app",
            "tools.dragonbyte.session",
            "tools.dragonbyte.shell",
            "tools.webfoot.catalog",
            "tools.webfoot.write",
            "tools.webfoot.release_identity",
        ),
    ),
    # The second frozen desktop application, registered in the same one list for the
    # same reason: a spec template, a version resource and the shared icon are a
    # release definition whether or not a build has been run over them. It ships an
    # installed directory beside its Qt runtime, so like the application above it
    # declares no README and no packager.
    #
    # Its identity is its own package's `identity.py`, and its closure is measured
    # rather than borrowed: it is a smaller application than the one above, so the
    # shape-wide floor would be a reading of that product and not of this one.
    ReleaseProduct(
        package="buufury_text",
        build_name="Buu's Fury Text Editor",
        readme=None,
        packager=None,
        release_shape="installed",
        entry_module="tools.buufury_text._pyinstaller_entry",
        identity_module="tools.buufury_text.identity",
        application_root="tools.buufury_text",
        required_modules=(
            "tools.buufury_text.app",
            "tools.buufury_text.session",
            "tools.buufury_text.shell",
            "tools.buufury_text.theme",
            "tools.webfoot.textedit",
            "tools.webfoot.write",
        ),
        closure_floor=35,
    ),
)


@dataclass(frozen=True)
class Finding:
    code: str
    product: str
    path: str
    detail: str
    line: int = 0

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "product": self.product,
            "path": self.path,
            "line": self.line,
            "detail": self.detail,
        }


def _read_text(base: Path, relative: str) -> str | None:
    try:
        return (base / relative).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _read_bytes(base: Path, relative: str) -> bytes | None:
    try:
        return (base / relative).read_bytes()
    except OSError:
        return None


def icon_entries(data: bytes) -> list[tuple[int, int]] | None:
    """The ``(width, height)`` of every image in an ``.ico`` file, or None.

    None means the file is not an icon at all. A zero width byte means 256, the
    convention the format uses because the field is a byte.
    """
    if len(data) < 6 or data[:2] != b"\x00\x00":
        return None
    if struct.unpack_from("<H", data, 2)[0] != 1:
        return None
    count = struct.unpack_from("<H", data, 4)[0]
    entries: list[tuple[int, int]] = []
    for index in range(count):
        offset = 6 + 16 * index
        if offset + 2 > len(data):
            return None
        entries.append((data[offset] or 256, data[offset + 1] or 256))
    return entries


def _definition_findings(base: Path, product: ReleaseProduct) -> list[Finding]:
    """Every file the release definition names must exist.

    A product that declares no README and no packager names neither, so neither is
    a finding: the shape of a product's release is declared by the entry, and this
    check is about a declared file that is missing.
    """
    findings = []
    for code, label, relative in (
        ("spec-missing", "packaging spec template", product.spec),
        ("packager-missing", "release packaging script", product.packager),
        ("readme-missing", "release README", product.readme),
        ("version-resource-missing", "version resource", product.version_resource),
        ("icon-missing", "application icon", ICON),
    ):
        if relative is None:
            continue
        if not (base / relative).is_file():
            findings.append(
                Finding(code, product.build_name, relative, f"no {label}")
            )
    return findings


def _metadata_findings(
    product: ReleaseProduct, relative: str, text: str
) -> list[Finding]:
    findings = []
    fields = dict(_STRING_STRUCT.findall(text))
    missing = [name for name in REQUIRED_METADATA if not fields.get(name)]
    if missing:
        findings.append(
            Finding(
                "version-metadata-missing",
                product.build_name,
                relative,
                "the version resource does not declare "
                + ", ".join(missing),
            )
        )
    fixed = dict(_FIXED_INFO.findall(text))
    malformed = [name for name, value in fixed.items() if not _VERSION_TUPLE.fullmatch(value)]
    if set(fixed) != {"filevers", "prodvers"} or malformed:
        findings.append(
            Finding(
                "version-metadata-malformed",
                product.build_name,
                relative,
                "filevers/prodvers must both be four numeric fields",
            )
        )
    return findings


def _packaging_findings(
    product: ReleaseProduct, relative: str, text: str
) -> list[Finding]:
    """The packaging script stages the executable and the README, and nothing else.

    The screen reads the ``Join-Path $stage '<literal>'`` form the established
    scripts use, plus the archive's own ``*`` glob, so any extra target written
    through that form is counted whether or not a ``Copy-Item`` put it there. A
    path assembled into the staged directory some other way (a quoted ``$stage``
    path, ``Join-Path -Path $stage -ChildPath``, ``New-Item -Name``) is not
    matched by this static screen; what still covers it is the packaging-time
    probe in ``scripts/randomizer-release.ps1``, which scans the files that
    actually got staged.

    A product that declares no packaging script is not checked by any of this: the
    rules here describe the two-file archive a randomizer ships, and a product that
    ships an installed directory declares no packager and so makes no such claim.
    """
    if product.packager is None:
        return []
    findings = []
    targets = [first or second for first, second in _STAGE_LITERAL.findall(text)]
    destinations = [
        first or second for first, second in _STAGE_DESTINATION.findall(text)
    ]
    copies = len(_COPY_ITEM.findall(text))
    executable = [
        target
        for target in destinations
        if target.lower() in ("$buildname.exe", f"{product.build_name}.exe".lower())
    ]
    readme = [target for target in destinations if target.upper() == "README.TXT"]

    if (
        copies != len(destinations)
        or len(destinations) != 2
        or len(executable) != 1
        or len(readme) != 1
        or sorted(targets) != sorted([*destinations, "*"])
    ):
        findings.append(
            Finding(
                "package-contents",
                product.build_name,
                relative,
                f"the package stages {destinations} and touches {targets} under the "
                "stage directory; the release is the executable and README.txt, "
                "archived as one glob",
            )
        )

    declared = {
        name: first or second
        for name, first, second in _PARAMETER.findall(text)
    }
    if declared.get("ReadmePath") != product.readme:
        findings.append(
            Finding(
                "package-readme-mismatch",
                product.build_name,
                relative,
                f"the packaged README default is {declared.get('ReadmePath')!r}, "
                f"not {product.readme!r}",
            )
        )
    if declared.get("BuildName") != product.build_name:
        findings.append(
            Finding(
                "package-build-name-mismatch",
                product.build_name,
                relative,
                f"the packaged build name default is {declared.get('BuildName')!r}, "
                f"not {product.build_name!r}",
            )
        )
    if (
        Path(SHARED_RELEASE_SCRIPT).name not in text
        or "Assert-RandomizerNoProprietaryContent" not in text
    ):
        findings.append(
            Finding(
                "package-probe-missing",
                product.build_name,
                relative,
                "the packaging script does not run the shared proprietary-content probe",
            )
        )
    return findings


def _forbidden_input_findings(
    product: ReleaseProduct, relative: str, text: str
) -> list[Finding]:
    """No ROM, save or save state is a staged release input."""
    named: list[str] = []
    datas = _SPEC_DATAS.search(text)
    if datas:
        named.extend(first or second for first, second in _QUOTED.findall(datas.group(1)))
    named.extend(_COPY_SOURCE.findall(text))
    named.extend(first or second for first, second in _STAGE_LITERAL.findall(text))
    return [
        Finding(
            "forbidden-release-input",
            product.build_name,
            relative,
            f"{name} is a ROM, save or save state and cannot travel in a release",
        )
        for name in named
        if Path(name).suffix.lower() in FORBIDDEN_SUFFIXES
    ]


def residue_signals(
    relative: str, text: str, table: public_surface.ExceptionTable
) -> list[tuple[int, str]]:
    """Every residue signal in one text, as ``(line, detail)`` pairs.

    The one owner of "what counts as residue in a release input": the release-local
    screens (`RELEASE_RESIDUE`) plus the tree-wide screens
    (`tools/quality/public_surface.py`), reused with its exception table intact.
    Two release checks ask this question - the definition guard and the staged
    package census - and a second copy of the loop is a second answer waiting to
    drift from the first.
    """
    signals: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        for label, pattern in RELEASE_RESIDUE:
            if pattern.search(line):
                signals.append((number, f"{label}: {line.strip()[:120]}"))
    shared, _ = public_surface.scan(relative=relative, exceptions=table, text=text)
    for item in shared:
        signals.append((item["line"], f"{item['signal']}: {item['text'][:120]}"))
    return signals


def _residue_findings(
    product_name: str,
    relative: str,
    text: str,
    table: public_surface.ExceptionTable,
) -> list[Finding]:
    """The release-local residue screens, plus the tree-wide screens, reused."""
    return [
        Finding("private-path-residue", product_name, relative, detail, number)
        for number, detail in residue_signals(relative, text, table)
    ]


def _spec_wiring_findings(
    product: ReleaseProduct, relative: str, text: str
) -> list[Finding]:
    """The spec must actually point at the identity and the icon it ships.

    The values behind these references are checked against the product's own
    constants by ``tests/unit/test_randomizer_release.py``; what is checked here
    is that the wiring exists at all, for every registered product, so a future
    product cannot be left pointing at nothing.
    """
    findings = []
    if f"version='{product.version_resource}'" not in text:
        findings.append(
            Finding(
                "spec-version-not-wired",
                product.build_name,
                relative,
                f"the spec does not freeze {product.version_resource}",
            )
        )
    if f"icon='{ICON}'" not in text:
        findings.append(
            Finding(
                "spec-icon-not-wired",
                product.build_name,
                relative,
                f"the spec does not apply {ICON}",
            )
        )
    return findings


def _spec_resource_findings(
    base: Path, product: ReleaseProduct, relative: str, text: str
) -> list[Finding]:
    """The spec must name a frozen entry script and resources that exist.

    RELEASE-ARTEFACT-001 added this because the wiring check below reads the
    ``datas`` list only to hunt forbidden suffixes, so a spec that staged a file
    nobody had written passed the guard and failed at build time - or, worse,
    produced a package whose resource was silently absent. Both halves are release
    DEFINITION facts, which is what this module exists to check.
    """
    findings: list[Finding] = []
    analysis = _SPEC_ANALYSIS.search(text)
    if analysis is None:
        findings.append(
            Finding(
                "spec-analysis-missing",
                product.build_name,
                relative,
                "the spec does not declare an Analysis entry script",
            )
        )
    else:
        scripts = [first or second for first, second in _QUOTED.findall(analysis.group(1))]
        if not scripts:
            findings.append(
                Finding(
                    "spec-analysis-missing",
                    product.build_name,
                    relative,
                    "the spec's Analysis names no entry script",
                )
            )
        for script in scripts:
            if not (base / script).is_file():
                findings.append(
                    Finding(
                        "spec-entry-script-missing",
                        product.build_name,
                        relative,
                        f"the frozen entry script {script!r} is not in the tree",
                    )
                )

    datas = _SPEC_DATAS.search(text)
    if datas is None:
        # A product with no data files is legitimate, so an absent ``datas`` list is
        # not itself a finding. Whether the resources a packaged application NEEDS
        # actually arrived is answered against the staged directory, by
        # `tools/quality/package_content.py --require`; this check is about a
        # definition naming a file that does not exist at all.
        return findings
    for source, _destination in _SPEC_RESOURCE_PAIR.findall(datas.group(1)):
        if not (base / source).is_file():
            findings.append(
                Finding(
                    "spec-resource-missing",
                    product.build_name,
                    relative,
                    f"the spec stages {source!r} and it is not in the tree",
                )
            )
    return findings


def _product_findings(
    base: Path,
    product: ReleaseProduct,
    table: public_surface.ExceptionTable,
    unreadable: list[str],
) -> tuple[list[Finding], list[str]]:
    """Every finding for one product, and the definition files actually read."""
    findings = _definition_findings(base, product)
    scanned: list[str] = []

    texts: dict[str, str] = {}
    for relative in (
        product.spec,
        product.packager,
        product.readme,
        product.version_resource,
    ):
        if relative is None or not (base / relative).is_file():
            continue
        text = _read_text(base, relative)
        if text is None:
            unreadable.append(relative)
            continue
        texts[relative] = text
        scanned.append(relative)

    if product.version_resource in texts:
        findings.extend(
            _metadata_findings(
                product, product.version_resource, texts[product.version_resource]
            )
        )
    if product.spec in texts:
        findings.extend(
            _spec_wiring_findings(product, product.spec, texts[product.spec])
        )
        findings.extend(
            _spec_resource_findings(
                base, product, product.spec, texts[product.spec]
            )
        )
    if product.packager in texts:
        findings.extend(
            _packaging_findings(product, product.packager, texts[product.packager])
        )
    for relative, text in texts.items():
        findings.extend(_forbidden_input_findings(product, relative, text))
        findings.extend(
            _residue_findings(product.build_name, relative, text, table)
        )

    if (base / ICON).is_file():
        icon = _read_bytes(base, ICON)
        if icon is None:
            unreadable.append(ICON)
        else:
            scanned.append(ICON)
            entries = icon_entries(icon)
            if entries is None:
                findings.append(
                    Finding(
                        "icon-not-an-icon", product.build_name, ICON, "not an .ico file"
                    )
                )
            elif not ICON_SIZES <= set(entries):
                findings.append(
                    Finding(
                        "icon-not-multi-size",
                        product.build_name,
                        ICON,
                        "the icon does not cover "
                        + ", ".join(f"{w}x{h}" for w, h in sorted(ICON_SIZES))
                        + "; it declares "
                        + ", ".join(f"{w}x{h}" for w, h in sorted(set(entries))),
                    )
                )
    return findings, scanned


def _unregistered(base: Path, products: tuple[ReleaseProduct, ...]) -> list[Finding]:
    """A release definition or packaging script no product declares.

    Spec templates are read from the repository root because that is where the
    build scripts resolve them (``$BuildName.spec.in`` beside the generated
    ``.spec``); a packaging script is found by the ``package-*.ps1`` naming the
    existing two use.
    """
    declared = set()
    for product in products:
        declared.add(product.spec)
        declared.add(product.packager)
    findings = []
    for pattern in ("*.spec.in", "scripts/package-*.ps1"):
        for path in sorted(base.glob(pattern)):
            if path.relative_to(base).as_posix() in declared:
                continue
            findings.append(
                Finding(
                    "release-unregistered",
                    path.stem,
                    path.relative_to(base).as_posix(),
                    "no ReleaseProduct in PRODUCTS declares this release definition",
                )
            )
    return findings


def scan(
    root: Path | None = None,
    products: tuple[ReleaseProduct, ...] | None = None,
) -> dict:
    """The whole report document: findings, products and files read.

    ``unreadable`` is separate from ``findings`` for the same reason
    ``tools/quality/public_surface.py`` keeps it separate: a file that could not
    be read is not a finding to weigh, it is a check that did not run.
    """
    base = Path(root) if root is not None else REPOSITORY_ROOT
    selected = PRODUCTS if products is None else products
    table = public_surface.ExceptionTable.load(
        base / "config" / "public_surface_exceptions.json"
    )

    findings: list[Finding] = []
    scanned: list[str] = []
    unreadable: list[str] = []
    for product in selected:
        found, names = _product_findings(base, product, table, unreadable)
        findings.extend(found)
        scanned.extend(names)

    if not (base / SHARED_RELEASE_SCRIPT).is_file():
        findings.append(
            Finding(
                "shared-release-script-missing",
                "",
                SHARED_RELEASE_SCRIPT,
                "the shared release checks are gone, so no product runs the probe",
            )
        )
    else:
        shared_text = _read_text(base, SHARED_RELEASE_SCRIPT)
        if shared_text is None:
            unreadable.append(SHARED_RELEASE_SCRIPT)
        else:
            scanned.append(SHARED_RELEASE_SCRIPT)
            findings.extend(
                _residue_findings(
                    "", SHARED_RELEASE_SCRIPT, shared_text, table
                )
            )

    findings.extend(_unregistered(base, selected))
    findings.sort(key=lambda item: (item.product, item.path, item.line, item.code))

    counts: dict[str, int] = {}
    for item in findings:
        counts[item.code] = counts.get(item.code, 0) + 1
    return {
        "schema": SCHEMA,
        "products": sorted(product.build_name for product in selected),
        "files_scanned": len(set(scanned)),
        "unreadable": sorted(set(unreadable)),
        "findings": [item.as_dict() for item in findings],
        "code_counts": dict(sorted(counts.items())),
    }


def _render(report: dict, stream) -> None:
    print(
        f"public release: {len(report['products'])} product(s), "
        f"{report['files_scanned']} release input(s) read, "
        f"{len(report['findings'])} finding(s)",
        file=stream,
    )
    for item in report["findings"]:
        where = f"{item['path']}:{item['line']}" if item["line"] else item["path"]
        prefix = f"{item['product']} " if item["product"] else ""
        print(f"  {prefix}{where}: {item['code']}: {item['detail']}", file=stream)
    for relative in report["unreadable"]:
        print(f"  {relative}: release-input-unreadable", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="public-release",
        description=(
            "Check the randomizer release definitions: metadata, icon, the "
            "two-file package and ROM-free inputs."
        ),
    )
    parser.add_argument("--json", metavar="PATH", help="write the report document as JSON")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="report findings but always exit 0",
    )
    arguments = parser.parse_args(argv)

    try:
        report = scan()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2

    if arguments.json:
        Path(arguments.json).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    _render(report, sys.stdout)

    if report["unreadable"]:
        print(
            "\nSome release inputs could not be read, so they were not checked. "
            "Write them as UTF-8 text: a release input that cannot be decoded is "
            "not a release input that passed.",
            file=sys.stderr,
        )
        # A file that cannot be read is not a file that passed, and --no-fail
        # reframes findings rather than blindness, so this is BLOCKED.
        return 2
    if report["findings"] and not arguments.no_fail:
        print(
            "\nA public randomizer release does not meet the shared release "
            "rules. Fix the definition, or extend PRODUCTS in "
            "tools/quality/public_release.py deliberately.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
