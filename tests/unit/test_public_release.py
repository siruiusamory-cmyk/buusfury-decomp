"""The public-release guard, and the boundary of every detector it carries.

:mod:`tools.quality.public_release` keeps the two randomizer executables honest
about what a release is: complete Windows metadata, the project icon, a package
that stages exactly the executable and the README, ROM-free inputs, and no
machine of its own in anything the executable carries.

Two classes of proof live here. The current definitions must pass, and a
deliberately broken release must fail each detector. The broken releases are
synthetic trees under ``tmp_path`` rather than edits to the repository, so a
control can be as wrong as it needs to be without ever touching the product.
"""

from __future__ import annotations

import base64
import json
import struct
from pathlib import Path

import pytest

from tools.quality import public_release as release

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

ReleaseProduct = release.ReleaseProduct

#: A future third product, declared only in the test. Nothing in the guard is
#: allowed to be product-specific, so this must pass every rule the two shipped
#: products pass.
FUTURE = release.ReleaseProduct(
    package="futurerand",
    build_name="Future-Randomizer",
    readme="docs/futurerand/README.txt",
    packager="scripts/package-futurerand.ps1",
)

#: Residue controls travel base64-encoded, for the reason
#: ``tools/quality/_public_surface_tables.py`` states: a file that lists what it
#: forbids must not itself contain it, or the repository-wide screen has to
#: except the file that guards it.
_DRIVE_PATH = base64.b64decode("QzpcRGV2XGxvZzEtcmVtYWtlLWZha2UtMDAx").decode()
_ENVIRONMENT_PATH = base64.b64decode("JVRFTVAlXHJhbmRvbWl6ZXItYnVpbGQ=").decode()

ICON_SIZES = ((16, 16), (32, 32), (48, 48), (0, 0))


def _icon(size_pairs=ICON_SIZES) -> bytes:
    """A structurally valid ``.ico`` whose directory declares ``size_pairs``.

    The image payloads are inert: the guard reads the directory, which is what
    decides whether Windows can draw the file at each size it needs.
    """
    header = struct.pack("<HHH", 0, 1, len(size_pairs))
    directory = b""
    payloads = b""
    for width, height in size_pairs:
        payload = bytes([0x42]) * 16
        offset = 6 + 16 * len(size_pairs) + len(payloads)
        directory += struct.pack(
            "<BBBBHHII", width, height, 0, 0, 1, 32, len(payload), offset
        )
        payloads += payload
    return header + directory + payloads


def _spec(product: ReleaseProduct = FUTURE) -> str:
    return (
        "# a release definition for a future product\n"
        "a = Analysis(\n"
        f"    ['tools/webfoot/{product.package}/_pyinstaller_entry.py'],\n"
        "    pathex=['.'],\n"
        "    datas=[('tools/webfoot/data/roms.yaml', 'tools/webfoot/data')],\n"
        "    hiddenimports=['tools.webfoot.data'],\n"
        ")\n"
        "exe = EXE(\n"
        "    pyz,\n"
        "    a.scripts,\n"
        "    a.binaries,\n"
        "    a.datas,\n"
        "    [],\n"
        f"    name='{product.build_name}',\n"
        f"    icon='{release.ICON}',\n"
        f"    version='{product.version_resource}',\n"
        "    console=False,\n"
        ")\n"
    )


def _version(product: ReleaseProduct = FUTURE, fields: dict | None = None) -> str:
    values = {
        "CompanyName": "Webfoot SDK",
        "FileDescription": "A future randomizer",
        "FileVersion": "0.1.0.0",
        "InternalName": product.build_name,
        "LegalCopyright": "Mozilla Public License 2.0",
        "OriginalFilename": f"{product.build_name}.exe",
        "ProductName": "Future Randomizer",
        "ProductVersion": "0.1.0.0",
    }
    values.update(fields or {})
    entries = "".join(f'          StringStruct("{k}", "{v}"),\n' for k, v in values.items())
    return (
        "VSVersionInfo(\n"
        "  ffi=FixedFileInfo(\n"
        "    filevers=(0, 1, 0, 0),\n"
        "    prodvers=(0, 1, 0, 0),\n"
        "  ),\n"
        "  kids=[StringFileInfo([\n"
        '    StringTable("040904B0", [\n'
        f"{entries}"
        "    ])\n"
        "  ])],\n"
        ")\n"
    )


def _packager(product: ReleaseProduct = FUTURE) -> str:
    return (
        "[CmdletBinding()]\n"
        "param(\n"
        f"    [string] $BuildName = '{product.build_name}',\n"
        f"    [string] $ReadmePath = '{product.readme}',\n"
        '    [string] $CanonicalRom = "roms/Dragon Ball Z - Buu\'s Fury (U).gba"\n'
        ")\n"
        "$ErrorActionPreference = 'Stop'\n"
        '. "$PSScriptRoot/randomizer-release.ps1"\n'
        '$stage = Join-Path "dist" "$BuildName-release"\n'
        'Copy-Item $exe (Join-Path $stage "$BuildName.exe")\n'
        "Copy-Item $ReadmePath (Join-Path $stage 'README.txt')\n"
        "$staged = @(Get-ChildItem -Path $stage -File)\n"
        "$offenders = Assert-RandomizerNoProprietaryContent -Staged $staged "
        "-CanonicalRom $CanonicalRom\n"
        "Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip\n"
    )


def _write(root: Path, relative: str, content) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8", newline="\n")


def _tree(root: Path, product: ReleaseProduct = FUTURE) -> None:
    """A complete, valid release definition for one product."""
    _write(root, product.spec, _spec(product))
    _write(root, product.version_resource, _version(product))
    _write(root, product.readme, "A future randomizer.\n")
    _write(root, product.packager, _packager(product))
    _write(root, release.ICON, _icon())
    _write(
        root,
        release.SHARED_RELEASE_SCRIPT,
        "function Assert-RandomizerNoProprietaryContent { }\n",
    )


def _codes(root: Path, product: ReleaseProduct = FUTURE) -> set[str]:
    return {item["code"] for item in release.scan(root, (product,))["findings"]}


# --- the current definitions pass --------------------------------------------


def test_the_current_release_definitions_are_clean():
    report = release.scan()

    assert report["products"] == ["Buu-Fury-Warp-Randomizer", "Enemy-Randomizer"]
    assert report["files_scanned"] >= 10
    assert report["findings"] == [], json.dumps(report["findings"], indent=2)


def test_the_shipped_icon_covers_the_required_sizes():
    entries = release.icon_entries((REPOSITORY_ROOT / release.ICON).read_bytes())

    assert entries is not None, "the project icon is not an .ico file"
    assert release.ICON_SIZES <= set(entries)


# --- a complete future product passes ---------------------------------------


def test_a_complete_future_release_definition_passes(tmp_path):
    _tree(tmp_path)

    assert _codes(tmp_path) == set()


def test_an_undeclared_release_definition_fails(tmp_path):
    _tree(tmp_path)
    _write(tmp_path, "Other-Randomizer.spec.in", _spec())

    assert "release-unregistered" in _codes(tmp_path)


def test_an_undeclared_packaging_script_fails(tmp_path):
    _tree(tmp_path)
    _write(tmp_path, "scripts/package-other.ps1", _packager())

    assert "release-unregistered" in _codes(tmp_path)


# --- each detector fails on a deliberately bad release ----------------------


@pytest.mark.parametrize(
    "relative",
    ["spec", "version_resource", "readme", "packager"],
    ids=["spec", "version-resource", "readme", "packager"],
)
def test_a_missing_release_file_fails(tmp_path, relative):
    _tree(tmp_path)
    codes = {
        "spec": "spec-missing",
        "version_resource": "version-resource-missing",
        "readme": "readme-missing",
        "packager": "packager-missing",
    }

    (tmp_path / getattr(FUTURE, relative)).unlink()

    assert codes[relative] in _codes(tmp_path)


def test_a_missing_icon_fails(tmp_path):
    _tree(tmp_path)

    (tmp_path / release.ICON).unlink()

    assert "icon-missing" in _codes(tmp_path)


def test_version_metadata_must_be_present_and_well_formed(tmp_path):
    _tree(tmp_path)
    resource = tmp_path / FUTURE.version_resource

    resource.write_text(
        _version(FUTURE, {"CompanyName": ""}), encoding="utf-8", newline="\n"
    )
    assert "version-metadata-missing" in _codes(tmp_path)

    resource.write_text(
        _version().replace("filevers=(0, 1, 0, 0)", "filevers=(0, 1, 0)"),
        encoding="utf-8",
        newline="\n",
    )
    assert "version-metadata-malformed" in _codes(tmp_path)


def test_the_spec_must_wire_the_identity_and_the_icon(tmp_path):
    _tree(tmp_path)
    spec = tmp_path / FUTURE.spec

    spec.write_text(
        _spec().replace(f"version='{FUTURE.version_resource}',\n", ""),
        encoding="utf-8",
        newline="\n",
    )
    assert "spec-version-not-wired" in _codes(tmp_path)

    spec.write_text(
        _spec().replace(f"icon='{release.ICON}',\n", ""),
        encoding="utf-8",
        newline="\n",
    )
    assert "spec-icon-not-wired" in _codes(tmp_path)


def test_the_icon_must_be_a_multi_size_windows_icon(tmp_path):
    _tree(tmp_path)
    icon = tmp_path / release.ICON

    icon.write_bytes(_icon(((16, 16), (32, 32))))
    assert "icon-not-multi-size" in _codes(tmp_path)

    icon.write_bytes(b"not an icon at all")
    assert "icon-not-an-icon" in _codes(tmp_path)


def test_an_unexpected_release_file_fails(tmp_path):
    _tree(tmp_path)
    packager = tmp_path / FUTURE.packager
    valid = _packager()

    packager.write_text(
        valid.replace(
            "Compress-Archive",
            "Copy-Item $Extra (Join-Path $stage 'notes.txt')\nCompress-Archive",
        ),
        encoding="utf-8",
        newline="\n",
    )
    assert "package-contents" in _codes(tmp_path)

    packager.write_text(
        valid.replace(
            "Copy-Item $ReadmePath (Join-Path $stage 'README.txt')",
            "Copy-Item $Other (Join-Path $stage 'CHANGELOG.txt')",
        ),
        encoding="utf-8",
        newline="\n",
    )
    assert "package-contents" in _codes(tmp_path)

    packager.write_text(
        valid.replace("Compress-Archive -Path (Join-Path $stage '*')", "Compress-Archive -Path ."),
        encoding="utf-8",
        newline="\n",
    )
    assert "package-contents" in _codes(tmp_path)


def test_a_package_that_skips_the_shared_probe_fails(tmp_path):
    _tree(tmp_path)
    packager = tmp_path / FUTURE.packager

    packager.write_text(
        _packager()
        .replace('. "$PSScriptRoot/randomizer-release.ps1"\n', "")
        .replace("$offenders = Assert-RandomizerNoProprietaryContent -Staged $staged "
                 "-CanonicalRom $CanonicalRom\n", ""),
        encoding="utf-8",
        newline="\n",
    )

    assert "package-probe-missing" in _codes(tmp_path)


def test_the_packager_must_name_the_declared_readme_and_build(tmp_path):
    _tree(tmp_path)
    packager = tmp_path / FUTURE.packager

    packager.write_text(
        _packager().replace(FUTURE.readme, "docs/other/README.txt"),
        encoding="utf-8",
        newline="\n",
    )
    assert "package-readme-mismatch" in _codes(tmp_path)

    packager.write_text(
        _packager().replace(
            f"$BuildName = '{FUTURE.build_name}'", "$BuildName = 'Other-Randomizer'"
        ),
        encoding="utf-8",
        newline="\n",
    )
    assert "package-build-name-mismatch" in _codes(tmp_path)


def test_a_stage_file_written_by_another_cmdlet_fails(tmp_path):
    _tree(tmp_path)
    packager = tmp_path / FUTURE.packager

    packager.write_text(
        _packager().replace(
            "Compress-Archive",
            "Set-Content (Join-Path $stage 'notes.txt') -Value 'x'\nCompress-Archive",
        ),
        encoding="utf-8",
        newline="\n",
    )

    assert "package-contents" in _codes(tmp_path)


def test_the_archive_glob_cannot_smuggle_a_rom(tmp_path):
    _tree(tmp_path)
    packager = tmp_path / FUTURE.packager

    packager.write_text(
        _packager().replace(
            "(Join-Path $stage '*')", "(Join-Path $stage 'roms/game.gba')"
        ),
        encoding="utf-8",
        newline="\n",
    )
    codes = _codes(tmp_path)

    assert "package-contents" in codes
    assert "forbidden-release-input" in codes


def test_a_developer_path_in_a_release_input_fails(tmp_path):
    _tree(tmp_path)
    spec = tmp_path / FUTURE.spec
    readme = tmp_path / FUTURE.readme

    spec.write_text(_spec() + f"# built at {_DRIVE_PATH}\n", encoding="utf-8", newline="\n")
    assert "private-path-residue" in _codes(tmp_path)

    spec.write_text(_spec(), encoding="utf-8", newline="\n")
    readme.write_text(
        "See the log1-remake-example-001 checkout.\n", encoding="utf-8", newline="\n"
    )
    assert "private-path-residue" in _codes(tmp_path)


def test_the_tree_wide_screens_are_reused_for_release_inputs(tmp_path):
    """A screen this module does not own still fails a release input."""
    _tree(tmp_path)
    _write(tmp_path, FUTURE.readme, f"notes live under {_ENVIRONMENT_PATH}\n")

    assert "private-path-residue" in _codes(tmp_path)


def test_a_rom_save_or_save_state_release_input_fails(tmp_path):
    _tree(tmp_path)
    spec = tmp_path / FUTURE.spec
    packager = tmp_path / FUTURE.packager

    spec.write_text(
        _spec().replace(
            "datas=[('tools/webfoot/data/roms.yaml', 'tools/webfoot/data')]",
            "datas=[('tools/webfoot/data/roms.yaml', 'tools/webfoot/data'), "
            "('roms/game.gba', 'roms')]",
        ),
        encoding="utf-8",
        newline="\n",
    )
    assert "forbidden-release-input" in _codes(tmp_path)

    spec.write_text(_spec(), encoding="utf-8", newline="\n")
    packager.write_text(
        _packager().replace(
            "Copy-Item $ReadmePath (Join-Path $stage 'README.txt')",
            "Copy-Item $SavePath (Join-Path $stage 'progress.ss1')",
        ),
        encoding="utf-8",
        newline="\n",
    )
    assert "forbidden-release-input" in _codes(tmp_path)


# --- the screens have teeth --------------------------------------------------


def test_the_release_residue_screens_carry_a_probe_pair():
    probes = {
        "an absolute path": (_DRIVE_PATH, "https://example.invalid/notes"),
        "a machine environment path": ("$env:LOCALAPPDATA", "the local environment"),
        "a local checkout directory name": (
            "log1-remake-example-001",
            "the repository is called log1-remake",
        ),
    }

    assert {label for label, _ in release.RELEASE_RESIDUE} == set(probes)
    for label, pattern in release.RELEASE_RESIDUE:
        positive, negative = probes[label]
        assert pattern.search(positive), f"{label}: missed its positive control"
        assert not pattern.search(negative), f"{label}: fired on its negative control"


# --- the report and the reading mode ----------------------------------------


def test_the_report_is_deterministic(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    assert release.main(["--json", str(first)]) == 0
    assert release.main(["--json", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()


def test_an_unreadable_release_input_blocks_the_run(tmp_path, monkeypatch):
    _tree(tmp_path)
    resource = tmp_path / FUTURE.version_resource
    resource.write_bytes(
        _version().encode("utf-16")
    )
    monkeypatch.setattr(release, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(release, "PRODUCTS", (FUTURE,))

    report = release.scan(tmp_path, (FUTURE,))
    assert report["unreadable"] == [FUTURE.version_resource]

    # Blindness is BLOCKED, not a reading list: --no-fail does not excuse it.
    assert release.main(["--no-fail"]) == 2
    assert release.main([]) == 2


def test_no_fail_reports_without_failing(tmp_path, monkeypatch):
    _tree(tmp_path)
    (tmp_path / FUTURE.readme).unlink()
    monkeypatch.setattr(release, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(release, "PRODUCTS", (FUTURE,))

    assert release.main(["--no-fail"]) == 0
    assert release.main([]) == 1
