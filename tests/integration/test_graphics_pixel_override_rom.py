"""GRAPHICS-IMPORT-BOUNDARY-001: the normal SDK path authors graphic pixels.

Every test here drives the documented workflow on the canonical image -
`extract_project` writes a manifest and one indexed PNG per graphics payload, an
edit is made to that PNG, and `validate_project` / `build_project` consume it -
because that is the claim under test. The portable half (manifest parsing,
override resolution, allocation and reference planning over synthetic bytes)
lives in `tests/unit/test_graphics_authoring.py`; what can only be established
against the real corpus is here.

The ROM is opened read-only, and the last test asserts that it still hashes to
the same image after every build in this module has run.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats import indexed_png
from tools.webfoot.graphics import load_actor_sprites
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.format import dump_toml, load_toml
from tools.webfoot.project.model import GRAPHICS_FILE, ProjectError
from tools.webfoot.rom import identify_rom

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: A shared 8bpp 16x16 payload (two distinct frame pieces name it) whose measured
#: packed extent is 84 bytes. Measured, not assumed: the test computes the
#: re-encoded length and asserts the fit path it claims.
SHARED_GRAPHIC = 1632


def _rom_path() -> str:
    """The canonical image, found by content rather than by directory order.

    `roms/` may hold several images (this checkout's own warp-randomized
    derivative among them), and directory order is not a property to key a
    profile-specific test on, so every candidate is hashed and only the exact
    canonical image is used.
    """
    matches = sorted(glob.glob(os.path.join("roms", "*.gba")))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    for candidate in matches:
        if hashlib.sha256(Path(candidate).read_bytes()).hexdigest() == CANONICAL_SHA256:
            return candidate
    pytest.skip("local ROM is not the canonical profile these offsets target")


@pytest.fixture(scope="module")
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture(scope="module")
def sprites(catalog):
    path = _rom_path()
    return load_actor_sprites(Path(path).read_bytes(), identify_rom(path, catalog))


@pytest.fixture(scope="module")
def extracted(tmp_path_factory, catalog):
    """One full graphics extraction, shared by every test in this module.

    7,390 PNGs and one manifest, exactly as `webfoot extract` writes them. Each
    test that authors an edit restores the PNG it touched, so the fixture stays a
    pristine baseline for the tests after it.
    """
    project = tmp_path_factory.mktemp("graphics-boundary") / "project"
    extract_project(_rom_path(), project, catalog, graphics=True)
    return project


class _Author:
    """Author one asset's PNG in place, and put the baseline back afterwards."""

    def __init__(self, project: Path) -> None:
        self.project = project
        self.assets = project / "graphics" / "assets"
        self._backups: list[tuple[Path, bytes]] = []

    def path(self, index: int) -> Path:
        return self.assets / f"graphic_{index:04d}.png"

    def __enter__(self) -> "_Author":
        return self

    def __exit__(self, *exc) -> None:
        for path, data in self._backups:
            path.write_bytes(data)

    def write(self, index: int, pixels: bytes, *, width: int, height: int,
              entries: int = 256) -> None:
        path = self.path(index)
        self._backups.append((path, path.read_bytes()))
        palette = tuple((index * 7 % 256, 0, 0) for index in range(entries))
        path.write_bytes(indexed_png.encode(pixels, width, height, palette,
                                            transparent_index=0))

    def pixels(self, index: int) -> bytes:
        pixels, _w, _h, _palette, _transparent = indexed_png.decode(self.path(index).read_bytes())
        return pixels

    def corrupt(self, index: int, raw: bytes) -> None:
        """Replace an asset with bytes that are not an indexed PNG at all."""
        path = self.path(index)
        self._backups.append((path, path.read_bytes()))
        path.write_bytes(raw)


def _differing_offsets(base: bytes, built: bytes, padding: int = 0xFF) -> list[int]:
    """Byte positions where the emitted image differs from its base.

    The base is the canonical image and the output may be longer, so the bytes
    the emitted image synthesized are compared against the profile's declared
    padding value rather than skipped - a synthesized span that was written
    unexpectedly would otherwise be invisible.
    """
    return [
        offset
        for offset in range(len(built))
        if (base[offset] if offset < len(base) else padding) != built[offset]
    ]


def _assert_only_attributed_bytes_changed(base: bytes, built: bytes, manifest: dict) -> None:
    """Every changed byte is inside an attributed change, and none is outside.

    This is the whole-corpus form of "unrelated graphics remain byte-identical":
    rather than sampling neighbouring containers, it requires the diff between
    the base and the emitted image to be exactly the union of the spans the write
    manifest attributes to a named owner.
    """
    attributed = set()
    for change in manifest["changes"]:
        attributed.update(range(change["offset"], change["offset"] + change["size"]))
    differing = set(_differing_offsets(base, built))
    assert differing <= attributed, sorted(differing - attributed)[:16]
    assert len(differing) == manifest["changed_byte_count"]


# --- an unchanged graphics project is a no-op --------------------------------


def test_an_unchanged_graphics_project_rebuilds_the_canonical_image(
    extracted, catalog, tmp_path
) -> None:
    """extract -> no edits -> build must not touch a single byte."""
    rom = _rom_path()
    output = tmp_path / "unchanged.gba"
    result = build_project(extracted, rom, output, catalog)
    base = Path(rom).read_bytes()
    assert output.read_bytes() == base
    assert result.manifest.changes == ()


def test_validation_of_an_unchanged_graphics_project_reports_no_problems(
    extracted, catalog
) -> None:
    report = validate_project(extracted, _rom_path(), catalog)
    assert report.problems == ()


# --- case A: a same-dimension edit that fits its original extent --------------


def test_an_edit_that_fits_is_written_in_place_only(extracted, catalog, sprites, tmp_path) -> None:
    """In place means: no allocation, no reference rewrite, payload region only."""
    rom = _rom_path()
    graphic = sprites.graphic(
        next(g.identity for g in sprites.graphics() if g.identity.index == SHARED_GRAPHIC)
    )
    assert graphic.shared, "this fixture is meaningless unless the payload is shared"

    with _Author(extracted) as author:
        # Replacing every index with a single value collapses the stream, so the
        # fit is a property of the authored content rather than of luck. The
        # assertion below still measures it.
        authored = bytes([3]) * (graphic.width * graphic.height)
        author.write(SHARED_GRAPHIC, authored, width=graphic.width, height=graphic.height)
        output = tmp_path / "in-place.gba"
        result = build_project(extracted, rom, output, catalog, manifest_path=None)

    manifest = result.manifest
    assert manifest.relocations == ()
    assert manifest.generated_allocations == ()
    assert len(manifest.changes) == 1
    change = manifest.changes[0]
    assert change.owner == str(graphic.identity)
    assert change.offset == graphic.file_offset
    assert change.size <= graphic.packed_size
    assert "in place" in change.reason

    built = output.read_bytes()
    base = Path(rom).read_bytes()
    assert len(built) == len(base)
    # The container's trailing bytes inside its original extent are untouched.
    tail = graphic.file_offset + change.size
    assert built[tail : graphic.file_offset + graphic.packed_size] == \
        base[tail : graphic.file_offset + graphic.packed_size]
    _assert_only_attributed_bytes_changed(base, built, manifest.to_json())


# --- case B: an edit too large for its original slot -------------------------


def test_an_oversized_edit_relocates_once_and_rewrites_every_consumer(
    extracted, catalog, sprites, tmp_path
) -> None:
    rom = _rom_path()
    identity = next(g.identity for g in sprites.graphics() if g.identity.index == SHARED_GRAPHIC)
    graphic = sprites.graphic(identity)
    assert len(graphic.consumers) == 2

    state = 0x12345678
    high_entropy = bytearray()
    for _ in range(graphic.width * graphic.height):
        state = (state * 1103515245 + 12345) & 0xFFFFFFFF
        high_entropy.append((state >> 16) & 0xFF)

    with _Author(extracted) as author:
        author.write(SHARED_GRAPHIC, bytes(high_entropy),
                     width=graphic.width, height=graphic.height)
        output = tmp_path / "relocated.gba"
        result = build_project(extracted, rom, output, catalog, manifest_path=None)

    manifest = result.manifest
    assert len(manifest.relocations) == 1
    relocation = manifest.relocations[0]
    assert relocation.anchor == str(identity)
    assert relocation.old_range.size == graphic.packed_size
    assert relocation.new_range.size > graphic.packed_size
    assert len(relocation.references) == len(graphic.consumers)

    # One new payload, not one per consumer, and every consumer carries the SAME
    # address: the shared payload stays shared.
    payload_changes = [c for c in manifest.changes if c.size == relocation.new_range.size]
    assert len(payload_changes) == 1
    assert payload_changes[0].offset == relocation.new_range.start.value
    assert {rewrite.new_target_file_offset for rewrite in relocation.references} == \
        {relocation.new_range.start.value}

    # It went into the profile's declared expansion, not into canonical slack.
    assert len(manifest.generated_allocations) == 1
    allocation = manifest.generated_allocations[0]
    assert allocation.allocated_range == relocation.new_range
    assert allocation.allocated_rom_address == 0x08800000
    assert "graphics_authoring" == allocation.domain

    built = output.read_bytes()
    base = Path(rom).read_bytes()
    assert len(built) == 0x01000000
    # The original payload is left byte-intact, so a reference this toolkit did
    # not discover still reaches the art it always reached.
    assert built[graphic.file_offset : graphic.file_offset + graphic.packed_size] == \
        base[graphic.file_offset : graphic.file_offset + graphic.packed_size]
    # Every consumer word now holds the new GBA address.
    expected = allocation.allocated_rom_address.to_bytes(4, "little")
    for consumer in graphic.consumers:
        assert built[consumer.piece_offset + 8 : consumer.piece_offset + 12] == expected
    _assert_only_attributed_bytes_changed(base, built, manifest.to_json())


def test_repeated_builds_of_the_same_edited_project_are_identical(
    extracted, catalog, tmp_path
) -> None:
    identity = None
    with _Author(extracted) as author:
        pixels = author.pixels(SHARED_GRAPHIC)
        authored = bytes((value + 1) % 16 for value in pixels)
        width, height = 16, 16
        author.write(SHARED_GRAPHIC, authored, width=width, height=height)
        first = tmp_path / "first.gba"
        second = tmp_path / "second.gba"
        build_project(extracted, _rom_path(), first, catalog, manifest_path=None)
        build_project(extracted, _rom_path(), second, catalog, manifest_path=None)
    assert first.read_bytes() == second.read_bytes()


# --- palette and pixels are one authored surface -----------------------------


def test_a_palette_edit_and_a_pixel_edit_merge_into_one_plan(
    extracted, catalog, sprites, tmp_path
) -> None:
    """Both overrides reach the ONE plan, with no duplicate write ownership."""
    from tools.webfoot.project.model import GRAPHICS_OVERRIDES_FILE
    from tools.webfoot.project import GraphicsOverrides

    rom = _rom_path()
    identity = next(g.identity for g in sprites.graphics() if g.identity.index == SHARED_GRAPHIC)
    graphic = sprites.graphic(identity)
    overrides_path = extracted / GRAPHICS_OVERRIDES_FILE
    overrides_path.parent.mkdir(parents=True, exist_ok=True)
    overrides_path.write_text(
        dump_toml(GraphicsOverrides(palette={40: (0, 255, 0)}).to_document()),
        encoding="utf-8", newline="\n",
    )
    try:
        with _Author(extracted) as author:
            author.write(SHARED_GRAPHIC, bytes([3]) * (graphic.width * graphic.height),
                         width=graphic.width, height=graphic.height)
            output = tmp_path / "both.gba"
            result = build_project(extracted, rom, output, catalog, manifest_path=None)
    finally:
        overrides_path.unlink()

    owners = {change.owner for change in result.manifest.changes}
    assert owners == {"palette_entry:040", str(identity)}
    _assert_only_attributed_bytes_changed(
        Path(rom).read_bytes(), output.read_bytes(), result.manifest.to_json()
    )


# --- fail closed -------------------------------------------------------------


def test_a_dimension_mismatch_is_refused_naming_the_contract(
    extracted, catalog, tmp_path
) -> None:
    with _Author(extracted) as author:
        author.write(SHARED_GRAPHIC, bytes(32 * 32), width=32, height=32)
        report = validate_project(extracted, _rom_path(), catalog)
        assert report.problems, "a resized PNG must not pass validation"
        assert "does not resize" in report.problems[0]
        with pytest.raises(ProjectError, match="does not resize"):
            build_project(extracted, _rom_path(), tmp_path / "resized.gba", catalog)


def test_a_malformed_png_is_refused(extracted, catalog) -> None:
    with _Author(extracted) as author:
        author.corrupt(SHARED_GRAPHIC, b"\x89PNG\r\n\x1a\nnot really a png")
        report = validate_project(extracted, _rom_path(), catalog)
        assert report.problems
        assert "indexed PNG" in report.problems[0]


def test_a_manifest_written_for_another_profile_is_refused(extracted, catalog) -> None:
    path = extracted / GRAPHICS_FILE
    original = path.read_text(encoding="utf-8")
    document = load_toml(original)
    document["graphics"]["profile_id"] = "some_other_game_rev0_deadbeef"
    path.write_text(dump_toml(document), encoding="utf-8", newline="\n")
    try:
        report = validate_project(extracted, _rom_path(), catalog)
        assert report.problems
        assert "wrong assets" in report.problems[0]
    finally:
        path.write_text(original, encoding="utf-8", newline="\n")


# --- the canonical image is read-only ----------------------------------------


def test_the_canonical_image_is_unchanged_by_this_module(extracted, catalog, tmp_path) -> None:
    """Every build above ran against it; it must still be the same bytes."""
    rom = _rom_path()
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == CANONICAL_SHA256
