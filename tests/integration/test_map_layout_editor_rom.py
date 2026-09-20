"""Canonical-ROM-gated evidence for DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001.

Everything here reads the immutable canonical image and writes only to pytest's
temporary directory; the suite skips cleanly when the private ROM is not
configured, and it re-hashes the source at the end to prove it was only read.

It pins, in order:

* which maps and layers the edit session declares editable (and why the rest are
  read-only), including the two independent Map 19 reasons;
* the accepted Grand Kai proof case from MAP-LAYOUT-WRITE-001 - cell 0 of
  ``map:0040`` dominant layer 1, ``0x082928DC`` -> ``0x08292A54``, 29,208 changed
  pixels in that cell's 256x256 region and none elsewhere in the layer;
* the same cell-region property on other ordinary dominant-layer maps;
* the exact requested write set, no-op byte identity, revert/reset, Save As,
  reopening the emitted ROM, and the refusal of null, cross-layer and
  unsupported targets.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil

import pytest

from tools.export import canonical as canon
from tools.export import map_browser as mb
from tools.export import render as render_sdk
from tools.webfoot import map_layout_provenance as prov
from tools.webfoot import write as write_sdk
from tools.webfoot.map_layout_edit import MapLayoutEditError, MapLayoutEditor
from tools.webfoot.map_layout_write import MapLayoutWriteError, MapLayoutWriter

#: The accepted canonical Buu's Fury USA rev0 image.
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: The Grand Kai proof case, exactly as MAP-LAYOUT-WRITE-001 measured it.
GRAND_KAI = 40
GRAND_KAI_LAYER = 1
GRAND_KAI_CELL = 0
GRAND_KAI_ORIGINAL = 0x082928DC
GRAND_KAI_REPLACEMENT = 0x08292A54
GRAND_KAI_FIELD_OFFSET = 0x00292CA0
GRAND_KAI_CHANGED_PIXELS = 29_208

#: Two further ordinary dominant-layer maps with multi-chunk layouts.
OTHER_MAPS = ((46, 3, 1, 2), (359, 3, 3, 1))

#: Corpus census, measured on the canonical image.
EXPECTED_MAPS = 452
EXPECTED_EDITABLE = 341
EXPECTED_READ_ONLY = 111


def _rom_path() -> Path:
    return Path(
        os.environ.get(
            "LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"
        )
    )


@pytest.fixture(scope="module")
def canonical_rom() -> tuple[Path, bytes]:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return path, data


@pytest.fixture(scope="module")
def editor(canonical_rom: tuple[Path, bytes]) -> MapLayoutEditor:
    _path, data = canonical_rom
    return MapLayoutEditor(data)


def _layer_pixels(result: mb.MapBrowserResult, slot: int) -> tuple[int, int, bytes]:
    layer = next(layer for layer in result.layers if layer.slot == slot)
    return layer.width, layer.height, layer.pixels


def _count_differing(before: bytes, after: bytes) -> int:
    return sum(1 for a, b in zip(before, after) if a != b)


def _count_differing_in_rect(
    before: bytes, after: bytes, width: int, rect: tuple[int, int, int, int]
) -> int:
    x, y, w, h = rect
    total = 0
    for row in range(y, y + h):
        start = row * width + x
        total += _count_differing(before[start : start + w], after[start : start + w])
    return total


def _render_dominant_layer(data: bytes, map_index: int, slot: int) -> bytes:
    """Render one dominant layer of any image through the accepted readers.

    The Map Browser facade refuses anything but the canonical image on purpose, so
    reopening an emitted ROM is checked here with the same accepted readers it
    composes (the approach MAP-LAYOUT-WRITE-001 used for its own proof).
    """
    rom = canon.Rom(data)
    entry = canon.read_map_entries(rom)[map_index]
    layer = canon.read_layer(rom, entry.root_address, slot)
    block, _selectors, _animated = canon.assemble_map_char_block(rom, entry.root_address)
    entries = mb._stitch_dominant(rom, layer, {})
    return render_sdk.render_entries(
        entries,
        block.data,
        layer.chunk_x * canon.CHUNK_SIDE_TILES,
        layer.chunk_y * canon.CHUNK_SIDE_TILES,
    )


def _first_null_cell(editor: MapLayoutEditor) -> tuple[int, int, int]:
    """One editable cell whose stored pointer is null, as ``(map, slot, cell)``."""
    for index in range(canon.MAP_ENTRY_COUNT):
        for slot in editor.target(index).editable_slots:
            for cell in slot.cells:
                if cell.pointer == 0 and slot.choices:
                    return index, slot.slot, cell.cell
    raise AssertionError("the corpus no longer contains a fillable null dominant cell")


# --- what the editor declares editable ---------------------------------------


def test_corpus_census_and_editable_detection(editor: MapLayoutEditor) -> None:
    editable: list[int] = []
    read_only: list[int] = []
    dominating: set[int] = set()
    for index in range(canon.MAP_ENTRY_COUNT):
        target = editor.target(index)
        (editable if target.editable else read_only).append(index)
        for slot in target.slots:
            if slot.classification == "dominant":
                dominating.add(index)
                # Every editable slot offers at least two existing chunks, and
                # every read-only one explains itself.
                if slot.editable:
                    assert len(slot.choices) >= 2
                    assert all(slot.cells)
                    assert slot.grid.cell_count == len(slot.cells)
                else:
                    assert slot.read_only_reason
    assert len(editable) + len(read_only) == EXPECTED_MAPS
    assert len(editable) == EXPECTED_EDITABLE
    assert len(read_only) == EXPECTED_READ_ONLY
    # One map (map:0008) has no dominant layer at all: the census is not a single
    # rule, it is per-slot.
    assert 8 not in dominating
    assert 8 in read_only


def test_grand_kai_target_offers_the_three_multi_chunk_layers(
    editor: MapLayoutEditor,
) -> None:
    target = editor.target(GRAND_KAI)
    assert target.name == "Grand Kai's Planet"
    assert target.editable
    assert [slot.slot for slot in target.editable_slots] == [1, 2, 3]
    layer = target.slots[GRAND_KAI_LAYER]
    assert layer.grid.columns == 2 and layer.grid.rows == 2
    assert layer.cells[GRAND_KAI_CELL].pointer == GRAND_KAI_ORIGINAL
    assert layer.cells[1].pointer == GRAND_KAI_REPLACEMENT
    assert layer.cells[GRAND_KAI_CELL].offset == GRAND_KAI_FIELD_OFFSET
    assert len(layer.choices) == 4
    assert GRAND_KAI_REPLACEMENT in layer.choices
    # Slot 0 is a 1x1 grid holding one chunk, so it has nothing to substitute.
    assert not target.slots[0].editable
    assert "single chunk" in target.slots[0].read_only_reason


def test_map_19_stays_read_only_for_two_independent_reasons(
    editor: MapLayoutEditor,
) -> None:
    target = editor.target(19)
    assert not target.editable
    classifications = [slot.classification for slot in target.slots]
    assert classifications == [
        "dominant",
        "static_graphical_screenblock",
        "static_graphical_terrain_field",
        "absent_placeholder",
    ]
    # Its dominant slot is a single-chunk 1x1 grid, and its other graphical slots
    # are forms this ticket does not edit. Both reasons are stated, neither is an
    # error.
    assert not target.slots[0].editable
    assert "single chunk" in target.slots[0].read_only_reason
    assert "screen-entry" in target.slots[1].read_only_reason
    assert "terrain-field" in target.slots[2].read_only_reason
    assert "Map 19" in target.slots[2].read_only_reason
    with pytest.raises(MapLayoutEditError):
        editor.set_cell(19, 0, 0, GRAND_KAI_ORIGINAL)
    with pytest.raises(MapLayoutEditError):
        editor.overrides(19, (0, 0, GRAND_KAI_ORIGINAL))
    # It still renders: read-only means uneditable, not unusable.
    assert editor.preview(19).width > 0


# --- the accepted Grand Kai proof case ---------------------------------------


def test_grand_kai_cell_0_replacement_matches_the_accepted_proof(
    editor: MapLayoutEditor,
) -> None:
    editor.reset()
    before = editor.preview(GRAND_KAI)
    edit = editor.set_cell(
        GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT
    )
    assert edit is not None
    assert (edit.original, edit.replacement) == (
        GRAND_KAI_ORIGINAL,
        GRAND_KAI_REPLACEMENT,
    )
    assert edit.offset == GRAND_KAI_FIELD_OFFSET
    assert editor.describe_edits(GRAND_KAI) == (
        "BG1 · column 0, row 0: Chunk 1 → Chunk 2",
    )
    after = editor.preview(GRAND_KAI)

    width, _height, before_pixels = _layer_pixels(before, GRAND_KAI_LAYER)
    _w, _h, after_pixels = _layer_pixels(after, GRAND_KAI_LAYER)
    cell = (0, 0, canon.CHUNK_PIXELS, canon.CHUNK_PIXELS)
    changed = _count_differing_in_rect(before_pixels, after_pixels, width, cell)
    assert changed == GRAND_KAI_CHANGED_PIXELS
    assert _count_differing(before_pixels, after_pixels) == GRAND_KAI_CHANGED_PIXELS
    # The remaining three chunk regions of that layer, and every other layer, are
    # pixel-identical.
    for slot in (0, 2, 3):
        _w2, _h2, other_before = _layer_pixels(before, slot)
        _w3, _h3, other_after = _layer_pixels(after, slot)
        assert other_before == other_after
    editor.reset()


def test_the_write_set_is_exactly_the_four_byte_field(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor
) -> None:
    _path, source = canonical_rom
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    built = editor.build()
    changed = [index for index, (a, b) in enumerate(zip(source, built)) if a != b]
    assert changed == [GRAND_KAI_FIELD_OFFSET, GRAND_KAI_FIELD_OFFSET + 1]
    assert built[GRAND_KAI_FIELD_OFFSET : GRAND_KAI_FIELD_OFFSET + 4] == (
        GRAND_KAI_REPLACEMENT.to_bytes(4, "little")
    )
    assert len(built) == len(source)
    assert built[:0xC0] == source[:0xC0]  # header and checksum untouched
    editor.reset()


@pytest.mark.parametrize(("map_index", "slot", "cell", "replacement_cell"), OTHER_MAPS)
def test_other_dominant_maps_change_only_the_selected_cell_region(
    editor: MapLayoutEditor, map_index: int, slot: int, cell: int, replacement_cell: int
) -> None:
    editor.reset()
    target = editor.target(map_index)
    assert target.editable
    layer = target.slots[slot]
    assert layer.editable
    replacement = layer.cells[replacement_cell].pointer
    assert replacement != layer.cells[cell].pointer
    assert replacement in layer.choices

    before = editor.preview(map_index)
    editor.set_cell(map_index, slot, cell, replacement)
    after = editor.preview(map_index)

    width, _height, before_pixels = _layer_pixels(before, slot)
    _w, _h, after_pixels = _layer_pixels(after, slot)
    rect = layer.grid.cell_rect(cell)
    inside = _count_differing_in_rect(before_pixels, after_pixels, width, rect)
    total = _count_differing(before_pixels, after_pixels)
    assert inside > 0
    assert inside == total, "a substitution must not disturb any other chunk cell"
    # Previewing never wrote anything.
    editor.reset()
    assert editor.build() == _rom_path().read_bytes()


# --- preview, revert, reset --------------------------------------------------


def test_preview_leaves_the_source_rom_and_the_session_bytes_untouched(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor
) -> None:
    path, data = canonical_rom
    before_stat = path.stat()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    for _ in range(2):
        editor.preview(GRAND_KAI)
        editor.preview(GRAND_KAI, draft=(1, 3, GRAND_KAI_ORIGINAL))
    editor.overrides(GRAND_KAI)
    after_stat = path.stat()
    assert (after_stat.st_size, after_stat.st_mtime_ns) == (
        before_stat.st_size,
        before_stat.st_mtime_ns,
    )
    assert path.read_bytes() == data
    assert isinstance(editor.build(), bytes)
    editor.reset()


def test_revert_and_reset_restore_the_canonical_image(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor
) -> None:
    _path, source = canonical_rom
    editor.reset()
    assert editor.build() == source

    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    layer3 = editor.target(GRAND_KAI).slots[3]
    editor.set_cell(
        GRAND_KAI,
        3,
        3,
        next(pointer for pointer in layer3.choices if pointer != layer3.cells[3].pointer),
    )
    assert editor.changed_cell_count == 2
    assert editor.build() != source

    assert editor.revert_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    assert not editor.revert_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    assert editor.changed_cell_count == 1
    assert editor.revert_map(GRAND_KAI) == 1
    assert editor.build() == source

    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    assert editor.reset() == 1
    assert editor.build() == source
    assert not editor.has_changes
    assert editor.overrides(GRAND_KAI) == {}


def test_setting_a_cell_back_to_its_original_is_not_a_change(
    editor: MapLayoutEditor,
) -> None:
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    assert editor.changed_cell_count == 1
    assert editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_ORIGINAL) is None
    assert editor.changed_cell_count == 0
    assert editor.build() == _rom_path().read_bytes()


# --- refusals ----------------------------------------------------------------


def test_unsupported_replacements_and_targets_fail_closed(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor
) -> None:
    _path, source = canonical_rom
    editor.reset()
    target = editor.target(GRAND_KAI)
    layer = target.slots[GRAND_KAI_LAYER]
    # A pointer used by the map's other dominant layer is a real chunk that this
    # layer does not use: the writer must refuse it.
    cross_layer = target.slots[2].choices[0]
    assert cross_layer not in layer.choices
    for bad in (0, True, -1, 0x100000000, 0x08292884, cross_layer, None, "x"):
        with pytest.raises(MapLayoutEditError):
            editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, bad)
    with pytest.raises(MapLayoutEditError):
        editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, 4, GRAND_KAI_REPLACEMENT)
    with pytest.raises(MapLayoutEditError):
        editor.set_cell(GRAND_KAI, 0, 0, GRAND_KAI_ORIGINAL)  # single-chunk layer
    with pytest.raises(MapLayoutEditError):
        editor.set_cell(GRAND_KAI, 2, 0, 0)  # the null pointer is never a target
    with pytest.raises(MapLayoutEditError):
        editor.target(EXPECTED_MAPS)
    assert not editor.has_changes
    assert editor.build() == source


def test_null_cells_accept_only_an_existing_layer_chunk(
    editor: MapLayoutEditor,
) -> None:
    """A layer with a null cell may fill it - and revert it - from its own chunks."""
    found = None
    for index in range(canon.MAP_ENTRY_COUNT):
        for slot in editor.target(index).editable_slots:
            nulls = [cell for cell in slot.cells if cell.pointer == 0]
            if nulls and slot.choices:
                found = (index, slot, nulls[0])
                break
        if found:
            break
    assert found is not None, "the corpus no longer contains a fillable null dominant cell"
    index, slot, cell = found
    source = _rom_path().read_bytes()
    edit = editor.set_cell(index, slot.slot, cell.cell, slot.choices[0])
    assert edit is not None and edit.original == 0
    built = editor.build()
    assert built[edit.offset : edit.offset + 4] == edit.replacement.to_bytes(4, "little")
    # The cell's own stored value was null, so reverting puts null back. Restoring
    # a stored value is not a replacement and must not be held to the replacement
    # policy.
    assert editor.revert_cell(index, slot.slot, cell.cell)
    assert editor.build() == source
    assert editor.set_cell(index, slot.slot, cell.cell, slot.choices[0]) is not None
    assert editor.revert_map(index) == 1
    assert editor.build() == source
    editor.reset()


def test_writer_restores_a_null_cell_and_still_refuses_a_null_replacement(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor
) -> None:
    """The writer's early-out covers a revert; the policy still guards a write."""
    _path, source = canonical_rom
    writer = MapLayoutWriter(source)
    index, slot, cell = _first_null_cell(editor)
    pointer = editor.choices(index, slot)[0]
    writer.set_chunk_pointer(index, slot, cell, pointer)
    assert writer.pending_offsets == (editor.set_cell(index, slot, cell, pointer).offset,)
    writer.set_chunk_pointer(index, slot, cell, 0)
    assert writer.pending_offsets == ()
    assert writer.build() == source
    # A null value is still refused when it is not the cell's stored value:
    # setting a *non-null* cell back to null would erase a reference.
    editor.reset()
    with pytest.raises(MapLayoutWriteError):
        writer.set_chunk_pointer(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, 0)
    assert writer.pending_offsets == ()


# --- Save As -----------------------------------------------------------------


def test_no_op_save_is_byte_identical(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    path, source = canonical_rom
    editor.reset()
    output = tmp_path / "no-op.gba"
    saved = editor.save(output, source_path=path, profile_id=PROFILE_ID)
    assert saved.no_op
    assert saved.changes == ()
    assert saved.changed_offsets == ()
    assert saved.verified == ()
    assert output.read_bytes() == source
    assert saved.output_sha256 == CANONICAL_SHA256
    assert saved.output_size == len(source)


def test_save_publishes_a_provenance_manifest_beside_the_image(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    """Save As emits the ROM *and* the manifest that lets DragonByte Z reopen it."""
    path, source = canonical_rom
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    output = tmp_path / "derived.gba"
    saved = editor.save(output, source_path=path, profile_id=PROFILE_ID)
    assert saved.manifest_path == prov.manifest_path_for(output)
    assert saved.manifest_path.is_file()
    document = json.loads(saved.manifest_path.read_text(encoding="utf-8"))
    assert document["schema_version"] == prov.SUPPORTED_SCHEMA_VERSION
    assert document["base"] == {
        "profile_id": PROFILE_ID,
        "sha256": CANONICAL_SHA256,
    }
    assert document["output"]["sha256"] == saved.output_sha256
    assert len(document["changes"]) == 1

    # The published pair verifies, and the verifier reconstructs the canonical
    # image from the derivative alone.
    authored = prov.verify_authored_rom(output)
    assert authored.profile_id == PROFILE_ID
    assert authored.output_sha256 == saved.output_sha256
    assert authored.canonical_image == source
    assert [(e.map_index, e.layer_slot, e.cell) for e in authored.edits] == [
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    ]
    assert authored.edits[0].new == GRAND_KAI_REPLACEMENT
    assert authored.overrides_for(GRAND_KAI) == {
        (GRAND_KAI_LAYER, GRAND_KAI_CELL): GRAND_KAI_REPLACEMENT
    }
    assert authored.overrides_for(41) == {}
    assert "map:0040" in authored.summary()
    # And the derivative's declared layout is what the accepted renderer shows.
    plain = mb.render_map(source, GRAND_KAI)
    derived = mb.render_map(
        authored.canonical_image,
        GRAND_KAI,
        chunk_overrides=authored.overrides_for(GRAND_KAI),
    )
    _w, _h, plain_pixels = _layer_pixels(plain, GRAND_KAI_LAYER)
    _w2, _h2, derived_pixels = _layer_pixels(derived, GRAND_KAI_LAYER)
    assert _count_differing(plain_pixels, derived_pixels) == GRAND_KAI_CHANGED_PIXELS
    editor.reset()


def test_a_no_op_save_still_publishes_a_manifest_and_stays_byte_identical(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    path, source = canonical_rom
    editor.reset()
    output = tmp_path / "copy.gba"
    saved = editor.save(output, source_path=path, profile_id=PROFILE_ID)
    assert saved.no_op
    assert output.read_bytes() == source
    assert saved.manifest_path.is_file()
    # A copy is the canonical image, so it needs no provenance: the accepted
    # readers take it by identity, and the derivative path refuses it explicitly.
    assert prov.manifest_path_for(output).is_file()
    with pytest.raises(prov.ProvenanceError):
        prov.verify_authored_rom(output)


def test_arbitrary_modified_roms_are_refused(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    """No manifest, a mutated image, or a foreign base all fail closed."""
    path, source = canonical_rom
    editor.reset()

    # 1. A one-byte mutation of the canonical image, with no provenance at all.
    mutated = tmp_path / "mutated.gba"
    data = bytearray(source)
    data[0x00292CA0] ^= 0x01
    mutated.write_bytes(bytes(data))
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(mutated)
    assert "provenance manifest" in str(excinfo.value)

    # 2. The same mutation carrying the canonical image's *derivative* manifest:
    #    the image no longer matches the declared output.
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    derived = tmp_path / "derived.gba"
    editor.save(derived, source_path=path, profile_id=PROFILE_ID)
    tampered = tmp_path / "tampered.gba"
    payload = bytearray(derived.read_bytes())
    payload[0x100] ^= 0xFF  # outside every declared field
    tampered.write_bytes(bytes(payload))
    shutil.copyfile(prov.manifest_path_for(derived), prov.manifest_path_for(tampered))
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(tampered)
    assert "does not match its provenance" in str(excinfo.value)

    # 3. A byte flipped *inside* a declared field, with a manifest that still
    #    matches by hash: the reconstruction then fails, which is what bounds an
    #    accepted derivative to canonical-plus-declared-edits.
    inside = tmp_path / "inside.gba"
    payload = bytearray(derived.read_bytes())
    payload[GRAND_KAI_FIELD_OFFSET + 3] ^= 0x40
    inside.write_bytes(bytes(payload))
    document = json.loads(prov.manifest_path_for(derived).read_text(encoding="utf-8"))
    document["output"]["sha256"] = hashlib.sha256(bytes(payload)).hexdigest()
    prov.manifest_path_for(inside).write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError):
        prov.verify_authored_rom(inside)

    # 4. A manifest whose base is a different image is refused outright.
    foreign = json.loads(prov.manifest_path_for(derived).read_text(encoding="utf-8"))
    foreign["base"]["sha256"] = "ab" * 32
    prov.manifest_path_for(inside).write_text(json.dumps(foreign), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(inside)
    assert "canonical base" in str(excinfo.value)
    editor.reset()


def test_a_manifest_claiming_an_unsupported_edit_is_refused(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    """The declared edits must be the one operation the writer is allowed."""
    path, source = canonical_rom
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    derived = tmp_path / "derived.gba"
    editor.save(derived, source_path=path, profile_id=PROFILE_ID)
    document = json.loads(prov.manifest_path_for(derived).read_text(encoding="utf-8"))

    def reissue(change: dict) -> None:
        tampered = tmp_path / "claim.gba"
        tampered.write_bytes(derived.read_bytes())
        claim = json.loads(json.dumps(document))
        claim["changes"][0].update(change)
        claim["output"]["sha256"] = hashlib.sha256(tampered.read_bytes()).hexdigest()
        prov.manifest_path_for(tampered).write_text(json.dumps(claim), encoding="utf-8")
        with pytest.raises(prov.ProvenanceError):
            prov.verify_authored_rom(tampered)

    # A layer that is not a dominant chunk grid (map:0040 BG0 is 1x1 dominant and
    # map:0019 BG2 is a terrain field): use the terrain-field slot.
    reissue({"owner": "map:0019 layer 2 cell 0"})
    # A map index that does not exist.
    reissue({"owner": "map:0452 layer 1 cell 0"})
    # A change reason this tool never writes.
    reissue({"reason": "something else"})
    # A replacement that is not an existing non-null chunk of that layer: a null
    # pointer, and a pointer the layer does not use.
    reissue({"new": (0).to_bytes(4, "little").hex()})
    reissue({"new": 0x08292884 .to_bytes(4, "little").hex()})
    # A field width that is not the proven four bytes.
    reissue({"size": 2})
    editor.reset()


def test_a_failed_emit_or_verification_preserves_an_existing_destination(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    """The destination is only ever replaced after a verified emission."""
    path, source = canonical_rom
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    destination = tmp_path / "existing.gba"
    destination.write_bytes(b"the user's previous build")
    manifest_destination = prov.manifest_path_for(destination)
    manifest_destination.write_bytes(b"the user's previous provenance")

    # 1. The emit itself fails.
    def failing_emit(*args, **kwargs):
        raise write_sdk.WriteError("emit refused")

    original_emit = write_sdk.emit_image
    try:
        write_sdk.emit_image = failing_emit
        with pytest.raises(write_sdk.WriteError):
            editor.save(destination, source_path=path, profile_id=PROFILE_ID)
    finally:
        write_sdk.emit_image = original_emit
    assert destination.read_bytes() == b"the user's previous build"
    assert manifest_destination.read_bytes() == b"the user's previous provenance"

    # 2. The emit succeeds but verification fails.
    def failing_verify(*args, **kwargs):
        raise MapLayoutEditError("verification refused")

    original_verify = MapLayoutEditor._verify_output
    try:
        MapLayoutEditor._verify_output = failing_verify
        with pytest.raises(MapLayoutEditError):
            editor.save(destination, source_path=path, profile_id=PROFILE_ID)
    finally:
        MapLayoutEditor._verify_output = original_verify
    assert destination.read_bytes() == b"the user's previous build"
    assert manifest_destination.read_bytes() == b"the user's previous provenance"

    # No temporary sibling is left behind by either failure.
    leftovers = sorted(
        part.name for part in tmp_path.iterdir() if "webfoot-partial" in part.name
    )
    assert leftovers == []

    # 3. A successful save does replace both, and verifies.
    saved = editor.save(destination, source_path=path, profile_id=PROFILE_ID)
    assert destination.read_bytes() != b"the user's previous build"
    assert destination.read_bytes() == editor.build()
    assert prov.verify_authored_rom(destination).edits
    assert saved.manifest_path == manifest_destination
    editor.reset()


def test_save_as_writes_a_new_rom_that_reopens_with_the_requested_cells(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    path, source = canonical_rom
    source_stat = path.stat()
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    other_map, other_slot, other_cell, other_source_cell = OTHER_MAPS[0]
    other_layer = editor.target(other_map).slots[other_slot]
    editor.set_cell(
        other_map, other_slot, other_cell, other_layer.cells[other_source_cell].pointer
    )
    requested = editor.edits()

    output = tmp_path / "Dragon Ball Z - Buu's Fury - Edited.gba"
    saved = editor.save(output, source_path=path, profile_id=PROFILE_ID)
    assert not saved.no_op
    assert saved.output_path == output
    assert len(saved.changes) == len(requested)
    assert saved.verified == requested
    assert output.is_file() and output.stat().st_size == len(source)
    # Only the requested four-byte fields changed, and every changed byte lies in
    # one of them.
    allowed = {
        index
        for edit in requested
        for index in range(edit.offset, edit.offset + 4)
    }
    assert saved.changed_offsets
    assert set(saved.changed_offsets) <= allowed
    assert len(saved.changed_offsets) <= 4 * len(requested)
    assert {edit.offset for edit in requested} == set(
        edit.offset for edit in saved.verified
    )
    # Reopening the emitted ROM reads back the requested pointers.
    reopened = output.read_bytes()
    rom = canon.Rom(reopened)
    entries = canon.read_map_entries(rom)
    assert (
        canon.read_layer(
            rom, entries[GRAND_KAI].root_address, GRAND_KAI_LAYER
        ).chunk_addresses[GRAND_KAI_CELL]
        == GRAND_KAI_REPLACEMENT
    )
    assert (
        canon.read_layer(rom, entries[other_map].root_address, other_slot).chunk_addresses[
            other_cell
        ]
        == other_layer.cells[other_source_cell].pointer
    )
    # The reopened image renders the edited layout, and the source ROM is intact.
    plain_pixels = _render_dominant_layer(source, GRAND_KAI, GRAND_KAI_LAYER)
    edited_pixels = _render_dominant_layer(reopened, GRAND_KAI, GRAND_KAI_LAYER)
    assert _count_differing(plain_pixels, edited_pixels) == GRAND_KAI_CHANGED_PIXELS
    assert (
        _count_differing_in_rect(
            plain_pixels,
            edited_pixels,
            canon.CHUNK_PIXELS * 2,
            (0, 0, canon.CHUNK_PIXELS, canon.CHUNK_PIXELS),
        )
        == GRAND_KAI_CHANGED_PIXELS
    )
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CANONICAL_SHA256
    after_stat = path.stat()
    assert (after_stat.st_size, after_stat.st_mtime_ns) == (
        source_stat.st_size,
        source_stat.st_mtime_ns,
    )
    editor.reset()


def test_save_refuses_the_source_path_and_an_existing_output(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor, tmp_path: Path
) -> None:
    path, _source = canonical_rom
    editor.reset()
    editor.set_cell(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL, GRAND_KAI_REPLACEMENT)
    with pytest.raises(MapLayoutEditError):
        editor.save(path, source_path=path, profile_id=PROFILE_ID)
    with pytest.raises(MapLayoutEditError):
        editor.save(path, source_path=path, profile_id="")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CANONICAL_SHA256

    # An existing destination is replaced only by a verified emission: the
    # placeholder is gone afterwards, and the file that lands is the emitted image.
    existing = tmp_path / "already-there.gba"
    existing.write_bytes(b"previous build")
    saved = editor.save(existing, source_path=path, profile_id=PROFILE_ID)
    assert existing.read_bytes() == editor.build()
    assert hashlib.sha256(existing.read_bytes()).hexdigest() == saved.output_sha256
    assert saved.manifest_path.is_file()
    editor.reset()


def test_canonical_source_is_unchanged_after_the_whole_suite(
    canonical_rom: tuple[Path, bytes], editor: MapLayoutEditor
) -> None:
    path, data = canonical_rom
    editor.reset()
    assert path.read_bytes() == data
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CANONICAL_SHA256
    assert editor.build() == data
