"""ROM-gated proof that a distributed patch reproduces a real build exactly.

The claim that needs the commercial image, and the only one that makes a patch
worth distributing:

    verified canonical source + project build -> patch
    canonical source + patch                  -> exactly the built image

Everything here also re-checks the safety invariant around it: the canonical image
is byte-identical before and after, the patch is a small fraction of an 8 MiB image
rather than a copy of it, two exports of one project produce the same bytes, and a
source that is not the one the patch was made for is refused.

These skip cleanly when the canonical ROM is absent, so the portable suite stays
runnable without proprietary data. No ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot.build import build_project
from tools.webfoot.formats.bps import (
    BpsFormatError,
    apply as apply_bps,
    crc32,
    inspect as inspect_bps,
)
from tools.webfoot.patch import (
    PatchError,
    PatchSourceError,
    export_patch,
    read_patch_metadata,
    verify_patch,
)
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.write import OutputPathError

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)
PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: The same measured edit `tests/integration/test_project_build_rom.py` authors:
#: P-010 runtime capture identified the wolf's HP field, which is unique across
#: the enemy table, so this change is a real authored modification rather than a
#: byte poked at a guessed offset.
WOLF_TYPE_ID = 434
WOLF_HP = 175
WOLF_NEW_HP = 200
WOLF_HP_BYTE_OFFSET = 0x00711BDC + 0x04


def _rom_path() -> str:
    """The canonical image, found by content rather than by being the first match.

    `glob` returns entries in filesystem order, and a worktree that also holds
    randomized derivatives - every one of them matching `*Buu*.gba` - otherwise
    makes this test skip while reporting that the canonical ROM is absent. The
    digest decides.
    """
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    for candidate in matches:
        with open(candidate, "rb") as stream:
            if hashlib.sha256(stream.read()).hexdigest() == CANONICAL_SHA256:
                return candidate
    pytest.skip("no local image is the canonical profile these offsets target")


def _edit_wolf_hp(project: Path, value: int) -> None:
    path = project / "enemies" / "enemies.toml"
    text = path.read_text(encoding="utf-8")
    marker = f"[enemy.{WOLF_TYPE_ID}]"
    start = text.index(marker)
    field = text.index(f"\nhp = {WOLF_HP}\n", start)
    path.write_text(
        text[: field + 1]
        + f"hp = {value}\n"
        + text[field + len(f"\nhp = {WOLF_HP}\n") :],
        encoding="utf-8",
        newline="\n",
    )


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    """One extraction, one authored edit, one build, one exported patch.

    Module-scoped because every step here costs seconds against the canonical
    image, and the artefacts are read-only once made. Each test then proves one
    property of the same patch rather than paying for it again.
    """
    from tools.webfoot.build import extract_project

    rom = _rom_path()
    catalog = RomProfileCatalog.load("config/roms.yaml")
    root = tmp_path_factory.mktemp("patch-export")

    project = root / "project"
    extract_project(rom, project, catalog, graphics=False)
    _edit_wolf_hp(project, WOLF_NEW_HP)

    derivative = root / "derivative.gba"
    built = build_project(project, rom, derivative, catalog, manifest_path=None)

    patch_path = root / "authored.bps"
    result = export_patch(project, rom, patch_path, catalog)

    return {
        "rom": rom,
        "catalog": catalog,
        "project": project,
        "root": root,
        "derivative": derivative.read_bytes(),
        "built_sha256": built.manifest.output_sha256,
        "patch_path": patch_path,
        "result": result,
    }


def test_the_patch_rebuilds_the_independently_built_image(world):
    source = Path(world["rom"]).read_bytes()
    patch = world["patch_path"].read_bytes()

    rebuilt = apply_bps(source, patch)

    assert rebuilt == world["derivative"]
    assert hashlib.sha256(rebuilt).hexdigest() == world["built_sha256"]
    assert len(rebuilt) == 8388608


def test_the_rebuilt_image_carries_the_authored_edit(world):
    """The point of the patch is the modification, not merely a byte difference."""
    source = Path(world["rom"]).read_bytes()
    rebuilt = apply_bps(source, world["patch_path"].read_bytes())

    assert source[WOLF_HP_BYTE_OFFSET] == WOLF_HP
    assert rebuilt[WOLF_HP_BYTE_OFFSET] == WOLF_NEW_HP


def test_the_canonical_image_is_byte_identical_afterwards(world):
    assert hashlib.sha256(Path(world["rom"]).read_bytes()).hexdigest() == CANONICAL_SHA256


def test_the_patch_is_a_small_fraction_of_the_image_and_names_its_source(world):
    patch = world["patch_path"].read_bytes()
    source = Path(world["rom"]).read_bytes()

    header = inspect_bps(patch)
    assert header.source_size == len(source)
    assert header.source_crc32 == crc32(source)
    assert header.target_size == len(world["derivative"])
    assert crc32(world["derivative"]) == header.target_crc32
    # A patch that carried the image would be at least as large as the image.
    assert len(patch) < 1024 * 1024
    assert len(patch) < len(source) // 8


def test_the_provenance_record_identifies_the_base_target_and_project(world):
    document = read_patch_metadata(world["patch_path"].read_bytes())

    assert document["base"]["profile_id"] == PROFILE_ID
    assert document["base"]["sha256"] == CANONICAL_SHA256
    assert document["base"]["size"] == 8388608
    assert document["target"]["sha256"] == world["built_sha256"]
    assert document["project"]["name"]
    assert document["patch_format"] == "bps"
    assert "\\" not in world["patch_path"].read_bytes().decode("utf-8", "ignore")


def test_verification_reports_the_same_target_as_the_export(world):
    verification = verify_patch(world["patch_path"], world["rom"], world["catalog"])

    assert verification.target_sha256 == world["built_sha256"]
    assert verification.source_sha256 == CANONICAL_SHA256
    assert verification.patch_sha256 == hashlib.sha256(
        world["patch_path"].read_bytes()
    ).hexdigest()


def test_two_exports_of_one_project_are_byte_identical(world):
    second = world["root"] / "authored-again.bps"
    export_patch(world["project"], world["rom"], second, world["catalog"])

    assert second.read_bytes() == world["patch_path"].read_bytes()


def test_a_source_that_is_not_the_intended_one_is_refused(world, tmp_path):
    mutated = tmp_path / "mutated.gba"
    data = bytearray(Path(world["rom"]).read_bytes())
    data[0x100] ^= 0xFF
    mutated.write_bytes(bytes(data))

    with pytest.raises(PatchSourceError):
        verify_patch(world["patch_path"], mutated, world["catalog"])


def test_a_truncated_or_corrupted_patch_is_refused(world, tmp_path):
    patch = world["patch_path"].read_bytes()

    truncated = tmp_path / "truncated.bps"
    truncated.write_bytes(patch[:-8])
    with pytest.raises(BpsFormatError):
        verify_patch(truncated, world["rom"], world["catalog"])

    corrupted = tmp_path / "corrupted.bps"
    damaged = bytearray(patch)
    damaged[len(damaged) // 2] ^= 0x01
    corrupted.write_bytes(bytes(damaged))
    with pytest.raises(BpsFormatError):
        verify_patch(corrupted, world["rom"], world["catalog"])


def test_an_export_may_not_alias_the_canonical_image(world):
    with pytest.raises(OutputPathError, match="input image"):
        export_patch(world["project"], world["rom"], world["rom"], world["catalog"])
    assert hashlib.sha256(Path(world["rom"]).read_bytes()).hexdigest() == CANONICAL_SHA256


def test_an_export_may_not_replace_an_existing_patch(world):
    previous = world["patch_path"].read_bytes()
    with pytest.raises(OutputPathError, match="refusing to overwrite"):
        export_patch(
            world["project"], world["rom"], world["patch_path"], world["catalog"]
        )
    assert world["patch_path"].read_bytes() == previous


def test_a_project_that_builds_to_its_base_image_exports_no_patch(tmp_path):
    """The unedited project: a patch would describe no modification at all."""
    from tools.webfoot.build import extract_project

    rom = _rom_path()
    catalog = RomProfileCatalog.load("config/roms.yaml")
    project = tmp_path / "unchanged"
    extract_project(rom, project, catalog, graphics=False)

    output = tmp_path / "no-modification.bps"
    with pytest.raises(PatchError, match="identical to its base ROM"):
        export_patch(project, rom, output, catalog)
    assert not output.exists()
