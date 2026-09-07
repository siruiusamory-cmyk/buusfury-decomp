"""ROM-gated proofs for the actor-sprite pipeline (TOOLKIT-010).

These skip cleanly when the canonical image is absent, so the portable suite
stays runnable without proprietary data. The ROM is opened read-only and never
written; no ROM-derived fixture is committed.

Where a cheaper spot-check would do, these deliberately enumerate the **whole**
corpus instead. A tile-swizzle or container bug that only shows up on one
unusual shape is exactly what a sample misses, and the corpus is small enough
(7,355 payloads) to check exhaustively.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import graphics
from tools.webfoot.build import extract_project
from tools.webfoot.formats import indexed_png as ip
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.formats import webfoot_lz as wl
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.rom import identify_rom
from tools.webfoot.write import ByteChange, apply_plan, plan_changes

#: The one image these offsets were verified against.
CANONICAL_SHA1 = "f1c4b07554d2a3b1ad2f325307051e775ce68087"

# --- Counts established by the TOOLKIT-010 corpus census. A change to any of
# these is a change to the ROM reading, not a test that needs relaxing. ---
CHARACTER_TABLE_ENTRIES = 297
CHARACTERS_WITH_ART = 295
UNIQUE_ANIMATIONS = 1013
UNIQUE_FRAMES = 10959
UNIQUE_GRAPHICS = 7355
GRAPHICS_SHARED_BY_FRAME = 2986
GRAPHICS_SHARED_BY_CHARACTER = 2644
TOTAL_PACKED_BYTES = 2_724_940
TOTAL_TILE_BYTES = 9_131_136


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    return matches[0]


def _rom_bytes(path: str) -> bytes:
    data = open(path, "rb").read()
    if hashlib.sha1(data).hexdigest() != CANONICAL_SHA1:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return data


@pytest.fixture(scope="module")
def sprites() -> graphics.ActorSprites:
    path = _rom_path()
    image = _rom_bytes(path)
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    return graphics.load_actor_sprites(image, identify_rom(path, catalog))


# --- corpus enumeration ------------------------------------------------------

def test_corpus_matches_the_recorded_census(sprites: graphics.ActorSprites) -> None:
    assert sprites.layout.character_count == CHARACTER_TABLE_ENTRIES
    assert len(sprites.characters()) == CHARACTERS_WITH_ART
    assert len(sprites.graphics()) == UNIQUE_GRAPHICS

    animations = {
        offset for character in sprites.characters() for offset in character.animation_offsets
    }
    assert len(animations) == UNIQUE_ANIMATIONS

    frames = {
        reference.frame_offset
        for graphic in sprites.graphics()
        for reference in graphic.consumers
    }
    assert len(frames) == UNIQUE_FRAMES


def test_sharing_is_measured_not_assumed(sprites: graphics.ActorSprites) -> None:
    """Most payloads have several consumers; an edit is never private."""
    all_graphics = sprites.graphics()
    assert sum(1 for g in all_graphics if g.shared) == GRAPHICS_SHARED_BY_FRAME
    assert sum(1 for g in all_graphics if len(g.characters) > 1) == GRAPHICS_SHARED_BY_CHARACTER
    # Consumers are distinct frames, so they can never exceed the frame count.
    assert sum(len(g.consumers) for g in all_graphics) == UNIQUE_FRAMES


def test_every_frame_in_this_corpus_holds_exactly_one_piece(
    sprites: graphics.ActorSprites,
) -> None:
    """Measured, and the codec still handles the general case."""
    seen = set()
    for graphic in sprites.graphics():
        for reference in graphic.consumers:
            if reference.frame_offset in seen:
                continue
            seen.add(reference.frame_offset)
            frame = sg.decode_frame(sprites.base_bytes, reference.frame_offset)
            assert len(frame.pieces) == 1
    assert len(seen) == UNIQUE_FRAMES


def test_the_whole_corpus_is_eight_bits_per_pixel(
    sprites: graphics.ActorSprites,
) -> None:
    assert all(graphic.colour_256 for graphic in sprites.graphics())


def test_every_container_decodes_and_agrees_with_its_piece(
    sprites: graphics.ActorSprites,
) -> None:
    """The structural cross-check: two independent ROM facts must agree.

    The container declares a decoded length; the piece that points at it
    declares OAM dimensions. Nothing links them in the file, so their agreeing
    on all 7,355 payloads is what makes the format reading verified rather than
    merely plausible.
    """
    packed = 0
    tiles = 0
    for graphic in sprites.graphics():
        assert len(graphic.pixels) == graphic.width * graphic.height
        packed += graphic.packed_size
        tiles += graphic.width * graphic.height
    assert packed == TOTAL_PACKED_BYTES
    assert tiles == TOTAL_TILE_BYTES


def test_containers_are_packed_with_no_slack(sprites: graphics.ActorSprites) -> None:
    """Why growth must fail closed: there is nowhere for a bigger payload to go."""
    spans = sorted(
        (g.file_offset, g.file_offset + g.packed_size) for g in sprites.graphics()
    )
    overlaps = sum(1 for a, b in zip(spans, spans[1:]) if a[1] > b[0])
    adjacent = sum(1 for a, b in zip(spans, spans[1:]) if a[1] == b[0])
    assert overlaps == 0
    assert adjacent == 4014


# --- exact round trips -------------------------------------------------------

def test_tile_codec_round_trips_every_payload_exactly(
    sprites: graphics.ActorSprites,
) -> None:
    """decode -> encode over the entire supported corpus, byte for byte."""
    for graphic in sprites.graphics():
        original = wl.unpack(sprites.base_bytes, graphic.file_offset).data
        assert sg.swizzle_tiles(
            graphic.pixels,
            graphic.width,
            graphic.height,
            colour_256=graphic.colour_256,
        ) == original


def test_png_export_and_import_round_trips_every_asset(
    sprites: graphics.ActorSprites,
) -> None:
    palette = sprites.palette.rgb
    for graphic in sprites.graphics():
        blob = ip.encode(
            graphic.pixels,
            graphic.width,
            graphic.height,
            palette,
            transparent_index=sg.TRANSPARENT_INDEX,
        )
        pixels, width, height, colours, transparent = ip.decode(blob)
        assert pixels == graphic.pixels
        assert (width, height) == (graphic.width, graphic.height)
        assert colours == palette
        assert transparent == sg.TRANSPARENT_INDEX


def test_palette_encodes_back_to_its_exact_source_words(
    sprites: graphics.ActorSprites,
) -> None:
    offset = sprites.layout.object_palette_address.to_file_offset(
        len(sprites.base_bytes)
    )
    original = sprites.base_bytes[offset : offset + sg.PALETTE_BYTES]
    assert sg.encode_palette(sprites.palette) == original


# --- identity and determinism ------------------------------------------------

def test_identities_are_stable_and_carry_no_address(
    sprites: graphics.ActorSprites,
) -> None:
    first = sprites.graphics()[0]
    assert str(first.identity).startswith("buus_fury_usa_rev0_01c1707f/graphic:")
    assert f"{first.file_offset:x}" not in str(first.identity)


def test_two_loads_of_one_image_produce_identical_documents() -> None:
    path = _rom_path()
    image = _rom_bytes(path)
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    first = graphics.load_actor_sprites(image, identify_rom(path, catalog))
    second = graphics.load_actor_sprites(image, identify_rom(path, catalog))
    assert [g.to_document() for g in first.graphics()] == [
        g.to_document() for g in second.graphics()
    ]
    assert [c.to_document() for c in first.characters()] == [
        c.to_document() for c in second.characters()
    ]


# --- the write path ----------------------------------------------------------

def test_palette_edit_changes_exactly_two_bytes_and_nothing_else(
    sprites: graphics.ActorSprites,
) -> None:
    """The primary visual-edit proof, reduced to its byte-level claim."""
    base = sprites.base_bytes
    digest = hashlib.sha256(base).hexdigest()
    offset, new = sprites.plan_palette_entry(40, 0x03E0)
    change = ByteChange(
        offset=offset,
        old=base[offset : offset + 2],
        new=new,
        owner="palette_entry:040",
        reason="TOOLKIT-010 visual edit proof",
    )
    plan = plan_changes(base, [change], profile_id=sprites.profile.id, base_sha256=digest)
    built = apply_plan(base, plan)

    differing = [i for i in range(len(base)) if base[i] != built[i]]
    assert differing == [offset, offset + 1]
    assert plan.changed_byte_count == 2
    # Provenance names the semantic owner, not an address.
    assert plan.changes[0].owner == "palette_entry:040"


def test_repeated_builds_are_byte_identical(sprites: graphics.ActorSprites) -> None:
    base = sprites.base_bytes
    digest = hashlib.sha256(base).hexdigest()
    offset, new = sprites.plan_palette_entry(40, 0x03E0)

    def build() -> bytes:
        change = ByteChange(
            offset=offset,
            old=base[offset : offset + 2],
            new=new,
            owner="palette_entry:040",
            reason="determinism check",
        )
        return apply_plan(
            base,
            plan_changes(
                base, [change], profile_id=sprites.profile.id, base_sha256=digest
            ),
        )

    assert build() == build()


def test_no_op_rebuild_is_whole_rom_byte_identical(
    sprites: graphics.ActorSprites,
) -> None:
    """0 changed bytes. Unchanged payloads are re-emitted verbatim, never repacked."""
    base = sprites.base_bytes
    digest = hashlib.sha256(base).hexdigest()
    plan = plan_changes(base, [], profile_id=sprites.profile.id, base_sha256=digest)
    assert plan.is_noop
    assert apply_plan(base, plan) == base


def test_canonical_input_is_never_modified(sprites: graphics.ActorSprites) -> None:
    path = _rom_path()
    assert hashlib.sha1(open(path, "rb").read()).hexdigest() == CANONICAL_SHA1


def test_palette_edit_reports_every_graphic_it_will_affect(
    sprites: graphics.ActorSprites,
) -> None:
    """A shared-asset edit must not be presented as a private one."""
    users = sprites.palette_users(40)
    assert len(users) > 1
    for identity in users:
        assert bytes([40]) in sprites.graphic(identity).pixels


def test_palette_entry_outside_the_gba_colour_range_is_refused(
    sprites: graphics.ActorSprites,
) -> None:
    with pytest.raises(graphics.GraphicsError, match="15-bit"):
        sprites.plan_palette_entry(0, 0x8000)
    with pytest.raises(graphics.GraphicsError, match="outside 0"):
        sprites.plan_palette_entry(999, 0)


def test_pixel_edit_that_cannot_be_re_encoded_small_enough_is_refused(
    sprites: graphics.ActorSprites,
) -> None:
    """The measured limit, asserted rather than glossed.

    Re-encoding is honest but not competitive, so a pixel write usually will not
    fit its own allocation. The subsystem must refuse rather than overrun, and
    must say so in terms a caller can act on.
    """
    graphic = sprites.graphics()[0]
    noise = bytes((i * 97 + (i * i) % 251) % 256 for i in range(len(graphic.pixels)))
    with pytest.raises(sg.SpriteFormatError, match="growth is refused"):
        sprites.plan_pixels(graphic.identity, noise)


def test_an_unchanged_pixel_plan_still_fits_its_own_allocation(
    sprites: graphics.ActorSprites,
) -> None:
    """Find one asset whose re-encode fits, and prove the applied bytes decode back.

    Roughly one payload in two hundred re-encodes small enough, so this searches
    rather than assuming; a corpus where none fits would be a real finding and
    the skip says so.
    """
    for graphic in sprites.graphics()[:400]:
        try:
            plan = sprites.plan_pixels(graphic.identity, graphic.pixels)
        except sg.SpriteFormatError:
            continue
        offset, blob = sprites.apply_plan(plan)
        assert offset == graphic.file_offset
        assert len(blob) == plan.original_size          # exact extent, no growth
        decoded = wl.unpack(blob, 0)
        assert sg.unswizzle_tiles(
            decoded.data, graphic.width, graphic.height, colour_256=graphic.colour_256
        ) == graphic.pixels
        return
    pytest.skip("no payload in the sampled range re-encodes small enough to fit")


def test_graphics_edit_merges_with_another_subsystem_without_conflict(
    sprites: graphics.ActorSprites,
) -> None:
    """Cross-subsystem build: a palette write and a distant write coexist."""
    base = sprites.base_bytes
    digest = hashlib.sha256(base).hexdigest()
    palette_offset, new = sprites.plan_palette_entry(40, 0x03E0)
    stat_offset = 0x00711BDC          # the wolf enemy record, TOOLKIT-001
    changes = [
        ByteChange(
            offset=palette_offset,
            old=base[palette_offset : palette_offset + 2],
            new=new,
            owner="palette_entry:040",
            reason="graphics edit",
        ),
        ByteChange(
            offset=stat_offset,
            old=base[stat_offset : stat_offset + 2],
            new=b"\x2A\x00",
            owner="enemy:wolf",
            reason="stat edit",
        ),
    ]
    plan = plan_changes(base, changes, profile_id=sprites.profile.id, base_sha256=digest)
    built = apply_plan(base, plan)

    # Both subsystems' bytes land, and nothing outside the two regions moves.
    assert built[palette_offset : palette_offset + 2] == new
    assert built[stat_offset : stat_offset + 2] == b"\x2A\x00"
    differing = {i for i in range(len(base)) if base[i] != built[i]}
    assert differing <= {palette_offset, palette_offset + 1, stat_offset, stat_offset + 1}
    # Each region is attributed to its own owner in the manifest.
    assert {c.owner for c in plan.changes} == {"palette_entry:040", "enemy:wolf"}


def test_two_edits_of_the_same_palette_entry_are_refused(
    sprites: graphics.ActorSprites,
) -> None:
    """Overlapping ownership must fail before any output is emitted."""
    from tools.webfoot.write import OverlappingChangeError

    base = sprites.base_bytes
    digest = hashlib.sha256(base).hexdigest()
    offset, new = sprites.plan_palette_entry(40, 0x03E0)
    old = base[offset : offset + 2]
    changes = [
        ByteChange(offset=offset, old=old, new=new, owner="a", reason="first"),
        ByteChange(offset=offset, old=old, new=b"\x1F\x00", owner="b", reason="second"),
    ]
    with pytest.raises(OverlappingChangeError):
        plan_changes(base, changes, profile_id=sprites.profile.id, base_sha256=digest)


def test_verified_graphics_pointers_join_the_common_reference_graph(
    sprites: graphics.ActorSprites,
) -> None:
    """References are published only where the pointer was walked and decoded.

    `RomDocument.from_bytes` re-validates the whole set, so a bad range or an
    overlapping anchor fails here rather than reaching a relocation plan. Counts
    are asserted exactly: an off-by-one would mean a pointer was invented or one
    was dropped.
    """
    document = sprites.reference_document()

    expected_anchors = UNIQUE_GRAPHICS + CHARACTERS_WITH_ART + 2  # palette + table
    expected_references = UNIQUE_FRAMES + CHARACTERS_WITH_ART
    assert len(document.anchors) == expected_anchors
    assert len(document.references) == expected_references

    # Every reference source is distinct, so no two claims write one word.
    sources = {reference.source_range.start.value for reference in document.references}
    assert len(sources) == expected_references

    kinds = {anchor.kind for anchor in document.anchors}
    assert kinds == {
        "object_palette",
        "character_pointer_table",
        "character_structure",
        "graphics_container",
    }
    # Nothing here is a guess: a scanner is not permitted to grow the graph.
    from tools.webfoot.layout import ReferenceClass

    assert all(
        reference.classification is ReferenceClass.CONFIRMED_REFERENCE
        for reference in document.references
    )


def test_no_enemy_record_points_at_any_graphics_structure(
    sprites: graphics.ActorSprites,
) -> None:
    """The measured negative behind the UNKNOWN linkage, kept as a regression.

    If a future change to the enemy or graphics extents ever makes this pass
    vacuously - or makes it fail because a pointer really is there - that is a
    finding, and it should surface here rather than in a rewritten claim.
    """
    import struct

    image = sprites.base_bytes
    stats = sprites.profile.enemy_stats
    assert stats is not None, "the Buu profile declares enemy stats"

    start = stats.address.to_file_offset(len(image))
    graphics_offsets = {g.file_offset for g in sprites.graphics()}
    structure_offsets = set(sprites._read_structure_table())
    low, high = min(structure_offsets), max(structure_offsets)
    table = sprites.table_offset
    table_end = table + sprites.layout.character_count * 4

    for index in range(stats.count):
        record = start + index * stats.record_size
        for field in range(0, stats.record_size, 4):
            word = struct.unpack_from("<I", image, record + field)[0]
            if not 0x08000000 <= word < 0x08000000 + len(image):
                continue
            offset = word - 0x08000000
            assert offset not in graphics_offsets
            assert offset not in structure_offsets
            assert not low <= offset <= high
            assert not table <= offset < table_end


# --- project extraction ------------------------------------------------------

@pytest.fixture(scope="module")
def extracted(tmp_path_factory) -> Path:
    """One extraction, shared by every test below that only reads it.

    Extraction writes 7,355 PNGs. Doing that once per assertion would mean
    ~29,000 file writes to check four properties of one deterministic output -
    and determinism is exactly what makes sharing safe here: the same ROM
    always produces the same bytes, so a second extraction could only produce
    the same tree. `test_extraction_produces_a_deterministic_project` in
    `test_project_build_rom.py` is what proves that, and it is the one place
    that legitimately extracts twice.
    """
    path = _rom_path()
    _rom_bytes(path)
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    project = tmp_path_factory.mktemp("graphics_project") / "project"
    extract_project(path, project, catalog)
    return project


def test_extraction_writes_one_png_per_distinct_payload(extracted: Path) -> None:
    """Shared payloads are extracted once, so the file count matches the corpus.

    A private copy per consumer would produce 10,959 files for 7,355 real
    assets, and would make an edit look local when the ROM makes it global.
    """
    pngs = sorted((extracted / "graphics" / "assets").glob("*.png"))
    assert len(pngs) == UNIQUE_GRAPHICS
    assert (extracted / "graphics" / "graphics.toml").is_file()


def test_extracted_manifest_carries_the_rom_facts_a_png_cannot(
    extracted: Path,
) -> None:
    """Dimensions, depth, sharing and the packed extent live in the sidecar.

    A PNG carries pixels and a palette. It does not carry the dimensions the
    *piece* declares, the packed extent an edit is bounded by, or who else uses
    the asset - so those are recorded deterministically beside it rather than
    inferred from the image.
    """
    from tools.webfoot.project.format import load_toml

    document = load_toml(
        (extracted / "graphics" / "graphics.toml").read_text(encoding="utf-8")
    )
    assert document["graphics"]["transparent_index"] == sg.TRANSPARENT_INDEX
    assert len(document["graphics"]["palette_raw"]) == sg.PALETTE_ENTRIES
    assert len(document["asset"]) == UNIQUE_GRAPHICS
    assert len(document["character"]) == CHARACTERS_WITH_ART

    for identity, entry in document["asset"].items():
        assert identity.startswith("buus_fury_usa_rev0_01c1707f/graphic:")
        assert entry["bit_depth"] == 8
        assert entry["packed_size"] > 0
        assert entry["file"].startswith("graphics/assets/")


def test_extracted_pngs_decode_back_to_the_assets_they_came_from(
    extracted: Path, sprites: graphics.ActorSprites
) -> None:
    """The extracted representation is lossless against the ROM, not merely pretty."""
    from tools.webfoot.project.format import load_toml

    document = load_toml(
        (extracted / "graphics" / "graphics.toml").read_text(encoding="utf-8")
    )
    for graphic in sprites.graphics():
        entry = document["asset"][str(graphic.identity)]
        blob = (extracted / entry["file"]).read_bytes()
        pixels, width, height, _, transparent = ip.decode(blob)
        assert pixels == graphic.pixels
        assert (width, height) == (graphic.width, graphic.height)
        assert transparent == sg.TRANSPARENT_INDEX


def test_the_project_never_contains_a_copy_of_the_rom(
    extracted: Path, sprites: graphics.ActorSprites
) -> None:
    """A project is source. The base image stays a separately-held input."""
    for candidate in extracted.rglob("*"):
        if candidate.is_file():
            assert candidate.stat().st_size < len(sprites.base_bytes)


def test_skipping_graphics_still_rebuilds_the_rom_byte_identically(tmp_path) -> None:
    """`graphics=False` costs authoring reach, never correctness.

    The flag exists because sprite assets are the bulk of an extraction - 7,355
    PNGs against a few dozen TOML files, measured at 44.0s versus 1.8s - and
    someone editing stats has no use for them. What must not change is the
    build: unchanged graphics are re-emitted from the base image rather than
    from the project, so a graphics-less project still reproduces the ROM
    exactly. That is the claim, and it is asserted rather than assumed.
    """
    from tools.webfoot.build import build_project

    path = _rom_path()
    base = _rom_bytes(path)
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))

    project = tmp_path / "no-graphics"
    extract_project(path, project, catalog, graphics=False)
    assert not (project / "graphics").exists()

    output = tmp_path / "out.gba"
    build_project(project, path, output, catalog)
    assert output.read_bytes() == base


def test_a_profile_that_does_not_declare_the_capability_is_refused_by_name() -> None:
    """The gate answers before any offset is read, and says what was missing.

    Declaration is what authorises the subsystem, so a profile with the
    declaration removed must be refused even though the ROM itself is the right
    one - otherwise the offsets would be trusted because of the bytes rather
    than because a profile vouched for them.
    """
    import dataclasses

    path = _rom_path()
    image = _rom_bytes(path)
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    identification = identify_rom(path, catalog)

    undeclared = dataclasses.replace(
        identification.profile_match.profile, actor_sprites=None
    )
    weakened = dataclasses.replace(
        identification,
        profile_match=dataclasses.replace(
            identification.profile_match, profile=undeclared
        ),
    )
    with pytest.raises(graphics.GraphicsError, match="does not declare actor_sprites"):
        graphics.load_actor_sprites(image, weakened)
