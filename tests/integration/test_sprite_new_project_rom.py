"""SPRITE-NEW-PROJECT-SURFACE-001: the Cui case through the ordinary build route.

ROM-gated and read-only. The suite skips cleanly when the private canonical
Buu's Fury image is not configured locally, and it never writes to it: every test
extracts a project into a temporary directory, authors a sprite there, and builds
a new image beside it. The one exact-parity case additionally skips unless the
private source sheets are present, because nothing ROM- or art-derived is
committed here.

What only this file can establish is that the **project workflow** - extract,
edit, validate, build - reproduces what the production planners are already
proven to produce: sprite 307 authored, its actor appended to map 102's object
array, both allocated above canonical EOF, every retail byte preserved, and the
whole thing deterministic. The runtime claim that the engine draws and moves that
actor is owned by ``docs/research/SPRITE_NEW_ATTACHMENT_RUNTIME_PARITY.md``; the
parity case here is byte-for-byte the image that record ran.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from tests.helpers import write_truecolour_png
from tools.webfoot.build import (ProjectValidationError, build_project,
                                 extract_project, validate_project)
from tools.webfoot.formats import rgb_png
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.graphics import CHARACTER_TABLE_REFERENCE_OFFSETS
from tools.webfoot.profile import RomProfileCatalog

ROM_BASE = 0x08000000
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The image SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001 composed from the two
#: production planners and then RAN in the retail engine. It is also the image
#: SPRITE-NEW-RUNTIME-PARITY-001 recorded as its walking build, so one digest ties
#: the project route to both earlier proofs.
RECORDED_RUNTIME_SHA256 = \
    "033e04ba27ac8fcafe99df1f4f6cf2aa6f9a09445eee1ad15b707d2ff694ff57"

#: The proven Cui actor: its map, the identity the runtime experiment authored,
#: the donor whose frame geometry every authored frame copies, the retail sibling
#: record its behaviour entry comes from, and the four values the project states.
MAP_INDEX = 102
SPRITE_ID = 307
DONOR_SPRITE_ID = 10
DONOR_SLOT = 7
FAMILY = "map-sibling-08017da3"
POSITION = (209, 580)
RETAINED_RAW = 0
DATA_POINTER_RAW = 142104172
WANDER_BOX = (192, 544, 272, 624)
ENTRY_CLASS_RAW = 0x0800A7A1
CELL_SIDE = 32

#: The object-palette entries the runtime work measured as drawn by no decoded
#: actor-sprite graphic.
FREE_ENTRIES = (6, 8, 9, 103, 193, 217, 218, 223, 224, 225, 236)

#: Where the private Cui sheets live, when this machine has them. A relative
#: default, so no tracked file names a machine of its own.
SHEET_DIRECTORY_ENV = "SPRITE_NEW_CUI_SHEETS"
SHEET_DIRECTORY_DEFAULT = Path("Cui") / "Cui"


def _rom_path() -> Path:
    return Path(os.environ.get(
        "SPRITE_NEW_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))


def _word(image: bytes, offset: int) -> int:
    return int.from_bytes(image[offset:offset + 4], "little")


def _map_entry_offset(profile) -> int:
    return (profile.map_entries.address.to_file_offset(profile.size)
            + MAP_INDEX * profile.map_entries.record_size)


@pytest.fixture(scope="module")
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def profile(canonical_bytes, catalog):
    from tools.webfoot.rom import identify_rom
    return identify_rom(_rom_path(), catalog).profile_match.profile


@pytest.fixture(scope="module")
def extracted(tmp_path_factory, canonical_bytes, catalog) -> Path:
    """One extracted project, shared: extraction is the expensive half."""
    root = tmp_path_factory.mktemp("sprite-new-project")
    destination = root / "project"
    extract_project(_rom_path(), destination, catalog, name="sprite-new",
                    graphics=False)
    return destination


@pytest.fixture()
def project(extracted, tmp_path) -> Path:
    """A private copy of the extracted project, so tests cannot see each other."""
    destination = tmp_path / "project"
    shutil.copytree(extracted, destination)
    return destination


def author_sprite(project_dir: Path, *, sheets: dict[str, int],
                  free_entries=FREE_ENTRIES, family: str = FAMILY,
                  template: str = f"map:0102/object:{DONOR_SLOT:04d}",
                  position=POSITION, box=WANDER_BOX) -> Path:
    """Write `sprites/sprites.toml`, the whole authored surface of this ticket."""
    animations = "".join(
        f"\n[sprite.cui.animation.{name}]\n"
        f'sheet = "sprites/cui/{name}.png"\n'
        f"frames = {frames}\n"
        for name, frames in sorted(sheets.items())
    )
    text = (
        "[sprite.cui]\n"
        f"sprite_id = {SPRITE_ID}\n"
        f"donor_sprite_id = {DONOR_SPRITE_ID}\n"
        f"free_palette_entries = [{', '.join(str(i) for i in free_entries)}]\n"
        f"{animations}"
        "\n[sprite.cui.actor]\n"
        f'map = "map:{MAP_INDEX:04d}"\n'
        f'family = "{family}"\n'
        f"position = [{position[0]}, {position[1]}]\n"
        f"retained_raw = {RETAINED_RAW}\n"
        f"data_pointer_raw = {DATA_POINTER_RAW}\n"
        f'behaviour_template = "{template}"\n'
        f"wander_box = [{box[0]}, {box[1]}, {box[2]}, {box[3]}]\n"
    )
    path = project_dir / "sprites" / "sprites.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def palette_grid_sheet(path: Path, rgb: bytes, width: int, height: int) -> None:
    """Rewrite every channel to its bit-replicated form, as the recorded image did.

    The sheets are 5-bit art stored in 8-bit channels, and the SDK's published
    RGB->word conversion is exact only for the replicated encoding; the recorded
    runtime image is the replicated one.
    """
    write_truecolour_png(path, bytes(sg.expand_rgb888_channel(channel)
                                     for channel in rgb), width, height)


def private_sheets() -> dict[str, Path] | None:
    directory = Path(os.environ.get(SHEET_DIRECTORY_ENV, SHEET_DIRECTORY_DEFAULT))
    sheets = {name: directory / f"{name}.png" for name in ("stand", "walk")}
    if not all(path.is_file() for path in sheets.values()):
        return None
    return sheets


def copy_sheets(project_dir: Path, sources: dict[str, Path]) -> dict[str, int]:
    """Copy the private sheets in as palette-grid PNGs and describe them."""
    described: dict[str, int] = {}
    for name, source in sources.items():
        rgb, width, _height, _alpha = rgb_png.decode_truecolour(source.read_bytes())
        destination = project_dir / "sprites" / "cui" / f"{name}.png"
        palette_grid_sheet(destination, rgb, width, CELL_SIDE)
        assert width % (CELL_SIDE * 4) == 0
        described[name] = width // (CELL_SIDE * 4)
    return described


def synthetic_sheet(project_dir: Path, image: bytes, profile) -> None:
    """A sheet drawn in colours the object palette already displays.

    Nothing new is needed from the palette, so the authored art reuses entries the
    image already holds - which is the case the planner's reuse path exists for -
    and this test does not depend on which entries are free.
    """
    palette = sg.decode_palette(
        image, profile.actor_sprites.object_palette_address.to_file_offset(
            profile.size))
    body = tuple(sg.expand_bgr555(palette.raw[index]) for index in (5, 6))
    key = (255, 0, 255)
    rgb = bytearray()
    for _y in range(CELL_SIDE):
        for cell in range(4):
            for x in range(CELL_SIDE):
                inside = 8 <= x < 24
                rgb += bytes(key if not inside else body[(cell + x) % 2])
    write_truecolour_png(project_dir / "sprites" / "cui" / "stand.png",
                         bytes(rgb), CELL_SIDE * 4, CELL_SIDE)


def build(project_dir: Path, tmp_path: Path, name: str, catalog):
    output = tmp_path / f"{name}.gba"
    manifest = tmp_path / f"{name}.manifest.json"
    result = build_project(project_dir, _rom_path(), output, catalog,
                           manifest_path=manifest)
    return Path(result.output_path), Path(result.manifest_path)


def changed_offsets(canonical: bytes, produced: bytes) -> set[int]:
    return {index for index in range(len(canonical))
            if produced[index] != canonical[index]}


def expected_canonical_regions(profile, identity: dict) -> list[tuple[int, int]]:
    """The canonical FIELDS an authored sprite and actor are allowed to touch.

    Derived from published structure rather than from the plan: the two 32-bit
    literal words that name the character registry, this map's object bound and
    its object-array field, and each object-palette entry the identity says it
    wrote. A field is a region, not a byte count: how many of its bytes actually
    change depends on how far the new address is from the old one, which is an
    address coincidence rather than a property of the build.
    """
    regions: list[tuple[int, int]] = []
    for start in CHARACTER_TABLE_REFERENCE_OFFSETS:
        regions.append((start, start + 3))
    entry_at = _map_entry_offset(profile)
    regions.append((entry_at + 0x04, entry_at + 0x04))
    regions.append((entry_at + 0x14, entry_at + 0x17))
    for palette_entry in identity["palette_entries"]:
        regions.append((palette_entry["file_offset"], palette_entry["file_offset"] + 1))
    return sorted(regions)


def assert_only_canonical_fields_changed(canonical: bytes, produced: bytes,
                                         profile, identity: dict) -> None:
    """Every canonical byte the build touched lies in one of those fields, and
    every one of those fields was touched."""
    changed = changed_offsets(canonical, produced)
    regions = expected_canonical_regions(profile, identity)
    allowed = {offset for start, end in regions for offset in range(start, end + 1)}
    assert changed <= allowed, sorted(hex(offset) for offset in changed - allowed)
    for start, end in regions:
        assert changed & set(range(start, end + 1)), (hex(start), hex(end))


def assert_retail_object_records_preserved(canonical: bytes, produced: bytes,
                                           profile, actor: dict) -> None:
    """Every retail object record, and the retail array, byte for byte."""
    entry_at = _map_entry_offset(profile)
    array_at = _word(canonical, entry_at + 0x14) - ROM_BASE
    for slot in range(10):
        pointer = _word(canonical, array_at + 4 * slot) - ROM_BASE
        assert produced[pointer:pointer + 0x2C] == canonical[pointer:pointer + 0x2C]
    new_array = int(actor["array_rom_address"], 16) - ROM_BASE
    assert produced[new_array:new_array + 40] == canonical[array_at:array_at + 40]


def edit_map_field(project_dir: Path, name: str = "music_id") -> None:
    """Change one MapEntry field of the actor's own map in the project source."""
    path = project_dir / "maps" / "maps.toml"
    text = path.read_text(encoding="utf-8")
    block = text.index(f'[map."map:{MAP_INDEX:04d}"]')
    at = text.index(f"{name} = ", block)
    end = text.index("\n", at)
    current = int(text[at + len(name) + 3:end])
    path.write_text(text[:at] + f"{name} = {current - 1}" + text[end:],
                    encoding="utf-8", newline="\n")


# --- the only test that needs the private art -------------------------------


def test_the_cui_project_reproduces_the_runtime_parity_image(
        project, tmp_path, catalog, profile, canonical_bytes):
    """Exact ROM SHA parity with the image the retail engine already ran."""
    sources = private_sheets()
    if sources is None:
        pytest.skip("private Cui sheets not configured locally")
    author_sprite(project, sheets=copy_sheets(project, sources))
    report = validate_project(project, _rom_path(), catalog)
    assert report.passed, report.problems
    output, manifest_path = build(project, tmp_path, "cui", catalog)
    produced = output.read_bytes()
    assert len(produced) == 16 * 1024 * 1024
    assert hashlib.sha256(produced).hexdigest() == RECORDED_RUNTIME_SHA256

    entry = json.loads(manifest_path.read_text(encoding="utf-8"))["sprite_authoring"][0]
    identity, actor = entry["identity"], entry["actor"]
    assert identity["sprite_id"] == SPRITE_ID
    assert actor["map_index"] == MAP_INDEX
    assert actor["array_slots"] == 11
    # The two registry words, this map's bound and array field, and the two
    # palette entries the identity wrote - and nothing else in the whole image.
    assert_only_canonical_fields_changed(canonical_bytes, produced, profile, identity)
    assert_retail_object_records_preserved(canonical_bytes, produced, profile, actor)


# --- the same route, on art this repository can draw for itself -------------


def assert_authored_identity_and_actor(canonical: bytes, produced: bytes,
                                       manifest: dict, profile) -> None:
    """Every property the project route has to prove, byte by byte.

    Read from the EMITTED IMAGE wherever the image can answer, and from the
    manifest only for the addresses the planners chose. Shared with the local
    probe that reproduces this case without spending a fresh extraction, so the
    two cannot drift.
    """
    # sprite 307 authored
    entry = manifest["sprite_authoring"][0]
    identity, actor = entry["identity"], entry["actor"]
    assert identity["sprite_id"] == SPRITE_ID
    assert identity["donor_sprite_id"] == DONOR_SPRITE_ID
    structure = identity["structure"]["rom_address"]
    assert len(identity["animations"]) == 1
    assert len(identity["animations"][0]["frames"]) == 4  # one frame, four facings
    # The grown registry's last entry names the new structure; the engine reads a
    # character structure through exactly that entry.
    registry_at = identity["registry"]["range"]["file_offset"]
    assert _word(produced, registry_at + 4 * (identity["registry_entries"] - 1)) \
        == structure

    # the attachment, carrying the fields the project stated
    record = int(actor["record_rom_address"], 16) - ROM_BASE
    array = int(actor["array_rom_address"], 16) - ROM_BASE
    entry_at = _map_entry_offset(profile)
    assert produced[entry_at + 0x04] == 11
    assert _word(produced, entry_at + 0x14) == int(actor["array_rom_address"], 16)
    assert _word(produced, array + 40) == int(actor["record_rom_address"], 16)
    assert _word(produced, record + 0x10) == SPRITE_ID
    assert _word(produced, record + 0x04) == RETAINED_RAW
    assert _word(produced, record + 0x0C) == DATA_POINTER_RAW
    assert _word(produced, record + 0x18) == int(actor["record_rom_address"], 16) + 0x1C
    assert _word(produced, record + 0x1C) == ENTRY_CLASS_RAW
    box = tuple(int.from_bytes(produced[record + 0x24 + 2 * index:
                                         record + 0x26 + 2 * index], "little")
                for index in range(4))
    assert box == WANDER_BOX

    # everything allocated above canonical EOF
    assert len(produced) > len(canonical)
    for allocation in manifest["generated_allocations"]:
        assert allocation["allocated_range"]["file_offset"] >= len(canonical)

    # existing retail data preserved
    assert_retail_object_records_preserved(canonical, produced, profile, actor)
    assert_only_canonical_fields_changed(canonical, produced, profile, identity)


def test_the_project_route_authors_the_identity_and_its_actor(
        project, tmp_path, catalog, profile, canonical_bytes):
    synthetic_sheet(project, canonical_bytes, profile)
    author_sprite(project, sheets={"stand": 1})
    report = validate_project(project, _rom_path(), catalog)
    assert report.passed, report.problems
    output, manifest_path = build(project, tmp_path, "synthetic", catalog)
    produced = output.read_bytes()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert_authored_identity_and_actor(canonical_bytes, produced, manifest, profile)

    # deterministic build
    second_output, second_manifest = build(project, tmp_path, "synthetic-again",
                                           catalog)
    assert second_output.read_bytes() == produced
    assert Path(second_manifest).read_bytes() == manifest_path.read_bytes()


def test_a_new_actor_on_a_map_with_an_authored_field_edit_is_refused(
        project, tmp_path, catalog, profile, canonical_bytes):
    """The attachment emits that map's record, so a field edit would be dropped."""
    synthetic_sheet(project, canonical_bytes, profile)
    author_sprite(project, sheets={"stand": 1})
    edit_map_field(project)
    with pytest.raises(ProjectValidationError, match="field edit would be dropped"):
        build(project, tmp_path, "clash", catalog)
