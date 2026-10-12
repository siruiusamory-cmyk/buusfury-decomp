"""Canonical-ROM-gated proofs for MAP-TILE-PAINT-001.

The capability claim this file has to carry is not "bytes can be written". It is:

    open a project -> paint cells on a supported map -> commit them to the
    project -> build a NEW image -> reopen the project -> the same map shows the
    authored layout, and the canonical ROM is untouched.

Nothing here writes to the canonical image: it is read, hashed before and after,
and every output lands in pytest's temporary directory. The suite skips cleanly
when the private ROM is not configured, so the portable suite stays runnable
without proprietary data and no ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot import map_paint as mp
from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats import bg_tilemap
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.map_layout_edit import MapLayoutEditor
from tools.webfoot.map_layout_write import MapLayoutWriteError
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import (
    LAYOUT_FILE,
    LayoutEdits,
    ProjectLoadError,
    ProjectValidationError,
    read_project,
)
from tools.webfoot.write import paths_are_the_same_file

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: The accepted Grand Kai proof case from MAP-LAYOUT-WRITE-001, reused so the
#: paint proof lands on a cell whose exact pixel consequence is already known.
#: Grand Kai's BG1 is a 2x2 grid: cell 0 holds Chunk 1, cell 1 holds Chunk 2.
GRAND_KAI = 40
GRAND_KAI_LAYER = 1
GRAND_KAI_CELL = 0
GRAND_KAI_ORDINALS = (1, 2)
GRAND_KAI_FIELD_OFFSET = 0x00292CA0
GRAND_KAI_CHANGED_PIXELS = 29_208

#: A second ordinary map, so the "neighbouring resources are untouched" claim is
#: checked against a different record rather than against nothing. Its cell is
#: chosen by what it currently holds, not assumed, in `_other_edit` below: a
#: paint of the value a cell already holds is a no-op by design, so hard-coding
#: the pair would make this suite assert nothing.
OTHER_MAP = 46
OTHER_LAYER = 3

#: Map:0040's BG0 is the 1x1 grid holding one chunk of its own that the widened
#: rule makes paintable: its sibling records hold others. This is the wall the
#: ticket exists to remove, so it is asserted directly rather than assumed.
ONE_CHUNK_LAYER = 0

#: A map whose dominant layers between them hold a single chunk, so no widening
#: reaches it: map:0001 is BG3 alone, a 1x1 grid holding one chunk.
STILL_READ_ONLY_MAP = 1
STILL_READ_ONLY_LAYER = 3


def _other_edit(image: bytes) -> tuple[tuple[int, int, int], int]:
    """One effective paint on a second map: a cell and an ordinal that differs."""
    layer = mp.MapPainter(image).target(OTHER_MAP).layer(OTHER_LAYER)
    cell = next(
        index
        for index, item in enumerate(layer.cells)
        if layer.ordinal_of(item.pointer) != 1
    )
    return (OTHER_MAP, OTHER_LAYER, cell), 1


def _rom_path() -> Path:
    """The canonical image, from the configured path or the local `roms/` glob.

    `LOGX_CANONICAL_ROM` first, exactly as the sibling layout-editor suite reads
    it, so a run that configures the image explicitly cannot silently skip here.
    """
    configured = os.environ.get("LOGX_CANONICAL_ROM")
    if configured:
        path = Path(configured)
        if not path.is_file():
            pytest.skip(f"LOGX_CANONICAL_ROM does not exist: {path}")
    else:
        matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
        if not matches:
            pytest.skip("canonical Buu's Fury ROM not present locally")
        path = Path(matches[0])
    if hashlib.sha256(path.read_bytes()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return path


@pytest.fixture(scope="module")
def rom() -> Path:
    return _rom_path()


@pytest.fixture(scope="module")
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture(scope="module")
def image(rom: Path) -> bytes:
    return rom.read_bytes()


@pytest.fixture
def project(tmp_path: Path, rom: Path, catalog: RomProfileCatalog) -> Path:
    """A private, writable project, extracted without graphics.

    `graphics=False` because nothing here asserts anything about sprite assets and
    a full extraction writes 7,390 PNGs this ticket never reads. A build from
    such a project is still byte-identical to the canonical image, which the
    whole-image round trip below re-proves.
    """
    directory = tmp_path / "project"
    extract_project(rom, directory, catalog, graphics=False)
    return directory


def _layer_pixels(data: bytes, map_index: int, slot: int) -> tuple[int, bytes]:
    """One dominant layer's pixels, rendered from an arbitrary image."""
    reader = mg.MapGraphicsReader(data, packaged_profile())
    entry = mg.read_map_entries(reader)[map_index]
    layer = mg.read_layer(reader, entry.root_address, slot)
    block = mg.assemble_map_char_block(reader, entry.root_address)[0]
    entries = mg.stitch_dominant_entries(reader, layer)
    pixels, width, _height = bg_tilemap.render_entry_words(
        block.data,
        entries,
        map_width_tiles=layer.chunk_tiles_x,
        map_height_tiles=layer.chunk_tiles_y,
        color_256=True,
    )
    return width, pixels


def _count_differing(a: bytes, b: bytes) -> int:
    return sum(1 for left, right in zip(a, b) if left != right)


# --- what the paint authority reports for a real map -------------------------


def test_grand_kai_offers_its_layers_and_their_chunk_vocabularies(image: bytes):
    painter = mp.MapPainter(image)
    target = painter.target(GRAND_KAI)
    assert target.name == "Grand Kai's Planet"
    assert target.editable
    assert [layer.slot for layer in target.editable_layers] == [0, 1, 2, 3]

    layer = target.layer(GRAND_KAI_LAYER)
    assert (layer.columns, layer.rows) == (2, 2)
    assert layer.cell_count == 4
    assert layer.width == 2 * mg.CHUNK_PIXELS
    # The vocabulary is 1-based and ordered by first appearance: the layer's own
    # chunks first, then whatever its sibling records add.
    assert len(layer.vocabulary) >= 2
    assert [chunk.ordinal for chunk in layer.vocabulary] == list(
        range(1, len(layer.vocabulary) + 1)
    )
    assert layer.pointer(1) == layer.cells[0].pointer
    assert layer.ordinal_of(layer.cells[1].pointer) == 2
    # Every vocabulary entry is a chunk some dominant layer of this map already
    # uses; the ones this layer does not hold come from a sibling and say so.
    map_pointers = {
        pointer
        for slot in range(4)
        for cell in painter.target(GRAND_KAI).layer(slot).cells
        for pointer in (cell.pointer,)
    }
    own = {cell.pointer for cell in layer.cells}
    assert all(chunk.pointer in map_pointers for chunk in layer.vocabulary)
    for chunk in layer.vocabulary:
        if chunk.pointer in own:
            assert chunk.source_slot is None
        else:
            assert chunk.source_slot in (0, 2, 3)
            assert chunk.cell_count == 0
            assert chunk.label.endswith(f"BG{chunk.source_slot}")
    # The ordinals of the layer's own chunks are unchanged by the widening: the
    # first entries are exactly this layer's own pointers, in window order.
    assert [c.pointer for c in layer.vocabulary[: len(own)]] == list(
        dict.fromkeys(cell.pointer for cell in layer.cells)
    )
    assert sum(chunk.cell_count for chunk in layer.vocabulary) == layer.cell_count


def test_paint_ordinals_match_the_accepted_grand_kai_proof(image: bytes):
    """The ordinals this ticket publishes resolve to the proven pointers."""
    layer = mp.MapPainter(image).target(GRAND_KAI).layer(GRAND_KAI_LAYER)
    first, second = GRAND_KAI_ORDINALS
    assert layer.pointer(first) == 0x082928DC
    assert layer.pointer(second) == 0x08292A54
    assert layer.cells[GRAND_KAI_CELL].pointer == layer.pointer(first)
    assert layer.cells[1].pointer == layer.pointer(second)
    assert layer.cells[GRAND_KAI_CELL].offset == GRAND_KAI_FIELD_OFFSET


def test_a_layer_using_one_chunk_is_paintable_from_its_siblings(image: bytes):
    """The wall this ticket removes, shown before and after on the same layer.

    Before the widening map:0040 BG0 - a 1x1 grid holding one chunk of its own -
    was read-only with "a grid of 1 cell(s) using a single chunk". It is the case
    the limit existed to describe, and the case the widening has to reach.
    """
    layer = mp.MapPainter(image).target(GRAND_KAI).layer(ONE_CHUNK_LAYER)
    assert (layer.columns, layer.rows) == (1, 1)
    assert layer.editable, layer.read_only_reason
    assert layer.read_only_reason == ""
    # One chunk of its own, plus the chunks its sibling records hold.
    assert layer.ordinal_of(layer.cells[0].pointer) == 1
    borrowed = next(
        chunk for chunk in layer.vocabulary if chunk.pointer != layer.cells[0].pointer
    )
    assert borrowed.source_slot in (1, 2, 3)
    assert borrowed.cell_count == 0
    # And the paint of it plans one four-byte write at that layer's own field.
    edit = mp.MapPainter(image).resolve(
        GRAND_KAI, ONE_CHUNK_LAYER, 0, borrowed.ordinal
    )
    assert edit.replacement == borrowed.pointer
    assert edit.original == layer.cells[0].pointer
    assert edit.offset == layer.cells[0].offset


def test_a_map_whose_layers_share_one_chunk_is_still_read_only(image: bytes):
    """The refusal that survives widening: nothing on the map offers a second chunk."""
    layer = mp.MapPainter(image).target(STILL_READ_ONLY_MAP).layer(
        STILL_READ_ONLY_LAYER
    )
    assert not layer.editable
    assert "single chunk" in layer.read_only_reason
    with pytest.raises(mp.MapPaintError):
        mp.MapPainter(image).resolve(STILL_READ_ONLY_MAP, STILL_READ_ONLY_LAYER, 0, 1)


def test_a_special_handler_map_is_read_only_for_painting(image: bytes):
    """Map 19's terrain-field layer must fail closed, not be painted anyway."""
    painter = mp.MapPainter(image)
    target = painter.target(19)
    assert not target.editable
    assert target.read_only_kind in {"unsupported", "mixed"}
    for slot in (0, 1, 2, 3):
        with pytest.raises(mp.MapPaintError):
            painter.resolve(19, slot, 0, 1)


# --- the paint operation itself ----------------------------------------------


def test_painting_one_cell_plans_exactly_one_four_byte_write(image: bytes):
    edits = {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[1]}
    changes = mp.plan_layout_cells(image, edits)
    assert len(changes) == 1
    change = changes[0]
    assert change.offset == GRAND_KAI_FIELD_OFFSET
    assert change.size == 4
    assert change.old == (0x082928DC).to_bytes(4, "little")
    assert change.new == (0x08292A54).to_bytes(4, "little")
    assert change.owner == "map:0040 layer 1 cell 0"
    assert change.is_effective


def test_a_paint_of_a_value_the_cell_already_holds_plans_nothing(image: bytes):
    """A no-op paint is planned as nothing, not refused.

    A drag re-enters cells it already painted, a merged gesture replays its own
    work, and an author may re-issue a gesture at any time: refusing the case
    would turn ordinary painting into an error.
    """
    edits = {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[0]}
    assert mp.plan_layout_cells(image, edits) == ()
    edit = mp.MapPainter(image).resolve(
        GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_ORDINALS[0]
    )
    assert not edit.is_effective
    assert edit.original == edit.replacement


def test_painting_changes_only_the_selected_cell_region(image: bytes):
    """The authored edit is visible in the layer, and nowhere else in it."""
    painter = mp.MapPainter(image)
    overrides = painter.overrides_for(
        GRAND_KAI, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[1]}
    )
    assert overrides == {(GRAND_KAI_LAYER, GRAND_KAI_CELL): 0x08292A54}

    before = mp.MapPainter(image).target(GRAND_KAI)
    _w, plain = _layer_pixels(image, GRAND_KAI, GRAND_KAI_LAYER)
    # Render through the session, which is what the Workbench previews with.
    editor = MapLayoutEditor(image)
    editor.set_cell(
        GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, overrides[(GRAND_KAI_LAYER, GRAND_KAI_CELL)]
    )
    painted = editor.preview(GRAND_KAI)
    layer = next(item for item in painted.layers if item.slot == GRAND_KAI_LAYER)
    changed = _count_differing(plain, layer.pixels)
    assert changed == GRAND_KAI_CHANGED_PIXELS
    # The layer's own geometry is unchanged: painting never resizes anything.
    assert (layer.width, layer.height) == (
        before.layer(GRAND_KAI_LAYER).width,
        before.layer(GRAND_KAI_LAYER).height,
    )


def test_a_drag_of_many_cells_plans_one_write_per_changed_cell(image: bytes):
    edits = {
        (GRAND_KAI, GRAND_KAI_LAYER, 0): GRAND_KAI_ORDINALS[1],
        (GRAND_KAI, GRAND_KAI_LAYER, 2): GRAND_KAI_ORDINALS[1],
    }
    changes = mp.plan_layout_cells(image, edits)
    assert len(changes) == 2
    assert {change.offset for change in changes} == {
        GRAND_KAI_FIELD_OFFSET,
        GRAND_KAI_FIELD_OFFSET + 8,
    }


# --- refusals ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("map_index", "slot", "cell", "ordinal"),
    [
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, 0),        # ordinals are 1-based
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, -1),
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, 99),       # past the vocabulary
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, True),     # a bool is not an ordinal
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, "2"),
        (GRAND_KAI, GRAND_KAI_LAYER, 4, 1),                     # cell outside the grid
        (GRAND_KAI, GRAND_KAI_LAYER, -1, 1),
        (STILL_READ_ONLY_MAP, STILL_READ_ONLY_LAYER, 0, 1),     # one chunk on the map
        (452, GRAND_KAI_LAYER, 0, 1),                           # no such map
        (5, 0, 0, 1),                                           # absent slot
    ],
)
def test_an_illegal_paint_is_refused(image: bytes, map_index, slot, cell, ordinal):
    with pytest.raises(mp.MapPaintError):
        mp.MapPainter(image).resolve(map_index, slot, cell, ordinal)


def test_a_bad_paint_in_a_batch_refuses_the_whole_batch(image: bytes):
    edits = {
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[1],
        (GRAND_KAI, GRAND_KAI_LAYER, 99): GRAND_KAI_ORDINALS[1],
    }
    with pytest.raises(mp.MapPaintError):
        mp.plan_layout_cells(image, edits)


def test_the_paint_authority_refuses_any_non_canonical_image():
    with pytest.raises(mp.MapPaintError):
        mp.MapPainter(b"\x00" * 8_388_608)
    with pytest.raises(mp.MapPaintError):
        mp.MapPainter(b"")


# --- the project is the authoring surface ------------------------------------


def test_committing_a_paint_writes_the_semantic_document(image: bytes, project: Path):
    changed = mp.set_layout_cell(
        project,
        packaged_profile(),
        image,
        GRAND_KAI,
        GRAND_KAI_LAYER,
        GRAND_KAI_CELL,
        GRAND_KAI_ORDINALS[1],
    )
    assert changed
    document = read_project(project).layout
    assert document.cells() == {
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[1]
    }
    # The file names the map, the layer, the cell and the chunk - and no address.
    text = (project / LAYOUT_FILE).read_text(encoding="utf-8")
    assert "map:0040" in text
    assert "BG1" in text
    assert "0x" not in text


def test_committing_the_same_paint_twice_changes_nothing(image: bytes, project: Path):
    """A no-op paint must not create a project revision."""
    profile = packaged_profile()
    first = mp.set_layout_cell(
        project, profile, image, GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL,
        GRAND_KAI_ORDINALS[1],
    )
    assert first
    stamp = (project / LAYOUT_FILE).read_bytes()
    second = mp.set_layout_cell(
        project, profile, image, GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL,
        GRAND_KAI_ORDINALS[1],
    )
    assert not second
    assert (project / LAYOUT_FILE).read_bytes() == stamp


def test_unpainting_a_cell_removes_it_and_the_document_when_nothing_is_left(
    image: bytes, project: Path
):
    profile = packaged_profile()
    mp.set_layout_cell(
        project, profile, image, GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL,
        GRAND_KAI_ORDINALS[1],
    )
    assert (project / LAYOUT_FILE).is_file()
    assert mp.clear_layout_cell(
        project, profile, image, GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL
    )
    assert read_project(project).layout.is_empty()
    assert not (project / LAYOUT_FILE).exists()


def test_a_batch_with_one_illegal_cell_writes_nothing(image: bytes, project: Path):
    with pytest.raises(mp.MapPaintError):
        mp.set_layout_cells(
            project,
            packaged_profile(),
            image,
            {
                (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[1],
                (GRAND_KAI, GRAND_KAI_LAYER, 99): GRAND_KAI_ORDINALS[1],
            },
        )
    assert read_project(project).layout.is_empty()
    assert not (project / LAYOUT_FILE).exists()


def test_a_malformed_batch_key_is_the_sdk_error_family(image: bytes, project: Path):
    """A bad key must not raise TypeError or ValueError out of unpacking."""
    for bad in [("a", 1, 2), (1, 1), (1.0, 1, 2), "nonsense", (1, None, 2)]:
        with pytest.raises(mp.MapPaintError):
            mp.set_layout_cells(project, packaged_profile(), image, {bad: 1})


def test_committing_against_the_wrong_image_is_refused(project: Path):
    with pytest.raises(mp.MapPaintError):
        mp.set_layout_cell(
            project, packaged_profile(), b"\x00" * 8_388_608,
            GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, 2,
        )


# --- build, reopen, and the canonical image ----------------------------------


def test_a_complete_paint_project_builds_reopens_and_renders_the_authored_layout(
    image: bytes, project: Path, catalog: RomProfileCatalog, tmp_path: Path
):
    """The capability chain, end to end, on one named map and layer."""
    profile = packaged_profile()
    other_key, other_ordinal = _other_edit(image)
    edits = {
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_ORDINALS[1],
        other_key: other_ordinal,
    }
    assert mp.set_layout_cells(project, profile, image, edits)

    output = tmp_path / "painted.gba"
    result = build_project(
        project,
        _rom_path(),
        output,
        catalog,
        manifest_path=tmp_path / "painted.manifest.json",
    )
    assert result.output_path == output

    # 0. The authored cells are what the build was given.
    assert read_project(project).layout.cells() == edits

    # 1. Only the painted four-byte fields differ from the canonical image.
    painter = mp.MapPainter(image)
    built = output.read_bytes()
    changed = [index for index, (a, b) in enumerate(zip(image, built)) if a != b]
    allowed = {
        index
        for (map_index, layer_slot, cell) in edits
        for index in range(
            painter.target(map_index).layer(layer_slot).cells[cell].offset,
            painter.target(map_index).layer(layer_slot).cells[cell].offset + 4,
        )
    }
    assert changed
    assert set(changed) <= allowed
    assert len(built) == len(image)

    # 2. Neighbouring layers of the painted map are byte-identical.
    for slot in (0, 2, 3):
        _w, before_pixels = _layer_pixels(image, GRAND_KAI, slot)
        _w, after_pixels = _layer_pixels(built, GRAND_KAI, slot)
        assert before_pixels == after_pixels
    # ...and so is the map the OTHER edit did not touch at all.
    untouched = next(index for index in range(0, 5) if index != GRAND_KAI and index != OTHER_MAP)
    _w, before_pixels = _layer_pixels(image, untouched, 0)
    _w, after_pixels = _layer_pixels(built, untouched, 0)
    assert before_pixels == after_pixels

    # 3. The painted layer really renders the authored chunk.
    _w, plain = _layer_pixels(image, GRAND_KAI, GRAND_KAI_LAYER)
    _w, painted = _layer_pixels(built, GRAND_KAI, GRAND_KAI_LAYER)
    assert _count_differing(plain, painted) == GRAND_KAI_CHANGED_PIXELS

    # 4. Reopening the PROJECT shows the same authored cells, and the session
    #    built from the reopened project renders them without re-painting.
    reopened = read_project(project).layout.cells()
    assert reopened == edits
    session = MapLayoutEditor(
        image,
        floor=mp.MapPainter(image).pointer_edits(reopened),
    )
    assert session.edit(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL) is None
    assert session.committed_overrides(GRAND_KAI)[(GRAND_KAI_LAYER, GRAND_KAI_CELL)] == (
        painter.target(GRAND_KAI).layer(GRAND_KAI_LAYER).pointer(GRAND_KAI_ORDINALS[1])
    )
    # 5. ...and a REBUILD of that project produces the same image byte for byte.
    again = tmp_path / "painted-again.gba"
    build_project(
        project, _rom_path(), again, catalog, manifest_path=tmp_path / "again.json"
    )
    assert again.read_bytes() == built


def test_an_unchanged_paint_project_rebuilds_the_whole_rom_byte_identically(
    image: bytes, project: Path, catalog: RomProfileCatalog, tmp_path: Path
):
    output = tmp_path / "unchanged.gba"
    build_project(project, _rom_path(), output, catalog, manifest_path=tmp_path / "m.json")
    assert output.read_bytes() == image


def test_a_build_refuses_a_paint_the_image_cannot_carry(
    image: bytes, project: Path, catalog: RomProfileCatalog, tmp_path: Path
):
    """An authored cell the layer does not offer is a build refusal, not silence."""
    (project / "maps").mkdir(parents=True, exist_ok=True)
    write_layout_edits_document(
        project, LayoutEdits(maps={"map:0040": {GRAND_KAI_LAYER: {0: 99}}})
    )
    output = tmp_path / "refused.gba"
    with pytest.raises(ProjectValidationError):
        build_project(
            project, _rom_path(), output, catalog, manifest_path=tmp_path / "m.json"
        )
    assert not output.exists()


def test_validation_names_an_illegal_authored_cell(
    image: bytes, project: Path, catalog: RomProfileCatalog
):
    (project / "maps").mkdir(parents=True, exist_ok=True)
    write_layout_edits_document(
        project, LayoutEdits(maps={"map:0040": {GRAND_KAI_LAYER: {0: 99}}})
    )
    report = validate_project(project, _rom_path(), catalog)
    assert not report.passed
    assert any("authored map layout" in problem for problem in report.problems)


def test_validation_refuses_a_paint_on_a_layer_that_cannot_be_painted(
    image: bytes, project: Path, catalog: RomProfileCatalog
):
    (project / "maps").mkdir(parents=True, exist_ok=True)
    write_layout_edits_document(project, LayoutEdits(maps={"map:0019": {2: {0: 1}}}))
    report = validate_project(project, _rom_path(), catalog)
    assert not report.passed
    assert any("authored map layout" in problem for problem in report.problems)


def test_a_project_naming_a_map_this_rom_lacks_is_refused(
    image: bytes, project: Path, catalog: RomProfileCatalog
):
    (project / "maps").mkdir(parents=True, exist_ok=True)
    write_layout_edits_document(project, LayoutEdits(maps={"map:0452": {1: {0: 1}}}))
    report = validate_project(project, _rom_path(), catalog)
    assert not report.passed
    assert any("authored map layout" in problem for problem in report.problems)


# --- the layout session's committed layer ------------------------------------


def test_a_session_with_a_committed_floor_renders_it_without_staging_anything(
    image: bytes,
):
    floor = {
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): mp.MapPainter(image)
        .target(GRAND_KAI)
        .layer(GRAND_KAI_LAYER)
        .pointer(GRAND_KAI_ORDINALS[1])
    }
    session = MapLayoutEditor(image, floor=floor)
    assert session.edits() == ()
    assert session.floor_cell_count == 1
    assert session.working_pointer(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL) == (
        floor[(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)]
    )
    assert session.committed_pointer(
        GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL
    ) == floor[(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)]
    # Painting the retail chunk back over the project's value is a real edit.
    retail = session.pointer(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    edit = session.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, retail)
    assert edit is not None
    assert edit.original == floor[(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)]
    assert edit.replacement == retail
    # ...and un-staging it returns the cell to the project's value, not to retail.
    assert session.clear_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    assert session.edits() == ()
    # The session builds canonical + committed: the project's paint is still in
    # the image its own writer would emit, at that cell's four-byte field only.
    built = session.build()
    assert built != image
    assert built[GRAND_KAI_FIELD_OFFSET : GRAND_KAI_FIELD_OFFSET + 4] == floor[
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    ].to_bytes(4, "little")
    assert [index for index, (a, b) in enumerate(zip(image, built)) if a != b] == [
        GRAND_KAI_FIELD_OFFSET,
        GRAND_KAI_FIELD_OFFSET + 1,
    ]


def test_a_floor_cell_that_does_not_exist_on_the_map_is_ignored(image: bytes):
    """A stale project entry must not be rendered onto a map that lacks the cell."""
    session = MapLayoutEditor(image, floor={(GRAND_KAI, 3, 99): 0x08292A54})
    assert session.committed_overrides(GRAND_KAI) == {}


def test_painting_over_a_committed_value_and_undoing_it_restores_the_committed_one(
    image: bytes,
):
    """The exact undo contract, at the session level, with a project layer present."""
    painter = mp.MapPainter(image)
    layer = painter.target(GRAND_KAI).layer(GRAND_KAI_LAYER)
    third = layer.pointer(3)
    floor = {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): layer.pointer(2)}
    session = MapLayoutEditor(image, floor=floor)

    assert session.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, third) is not None
    assert session.working_pointer(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL) == third
    # Undo: the cell's pre-gesture value was the PROJECT's, so un-stage to it.
    session.clear_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    assert session.working_pointer(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL) == (
        layer.pointer(2)
    )
    assert session.edits() == ()
    # The committed value is still what the session's own build emits.
    assert session.build() != image
    assert session._writer.pending_offsets == (
        layer.cells[GRAND_KAI_CELL].offset,
    )


# --- ROM safety ---------------------------------------------------------------


def test_the_canonical_image_is_unchanged_by_the_whole_suite(rom: Path, image: bytes):
    after = rom.read_bytes()
    assert after == image
    assert hashlib.sha256(after).hexdigest() == CANONICAL_SHA256
    assert len(after) == 8_388_608


def test_a_paint_never_offers_the_source_rom_as_an_output(
    rom: Path, project: Path, image: bytes
):
    """The one write path the ticket adds is the project document, not the ROM."""
    mp.set_layout_cell(
        project, packaged_profile(), image, GRAND_KAI, GRAND_KAI_LAYER,
        GRAND_KAI_CELL, GRAND_KAI_ORDINALS[1],
    )
    # The authored document is inside the project, and the ROM is untouched.
    assert (project / LAYOUT_FILE).is_file()
    assert not paths_are_the_same_file(project / LAYOUT_FILE, rom)
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == CANONICAL_SHA256


def write_layout_edits_document(project: Path, layout: LayoutEdits) -> None:
    """Write a layout document directly, for the refusal cases."""
    from tools.webfoot.project import write_layout_edits

    write_layout_edits(project, layout)
