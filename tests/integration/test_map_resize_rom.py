"""ROM-gated end-to-end tests for map resizing and layer authoring.

MAP-RESIZE-AND-LAYERS-001. Every fact here needs the canonical image, so the
suite skips when it is absent. What it pins, in the order the capability is
claimed:

* what a supported dominant layer's structural model actually is on the real
  corpus (record size is exactly header plus window, the root's extent is the
  camera maximum, roots and records are shared and that sharing is refused);
* that a resize maps the retail cells by coordinate, initializes only the added
  region, relocates the record and raises the extent to cover the grown plane;
* that an authored layer activates only a slot the canonical image leaves unused
  and never mutates its template;
* that the production allocator places every record ABOVE canonical EOF, that the
  map root's own slot field resolves to it, and that the derivative changes only
  the required bytes in the canonical region and rebuilds byte-identically;
* that the project reopens with the structure and the cell content intact;
* and that every refusal fails closed.

The visible retail-engine result cannot be asserted from bytes; it is recorded in
the ticket's runtime section with its matched A/B capture and guard.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import map_chunk as mc
from tools.webfoot import map_paint as mp
from tools.webfoot import map_resize as mr
from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import (
    AuthoredChunk,
    AuthoredChunkEntry,
    AuthoredChunks,
    LayerResize,
    LayoutEdits,
    MapStructure,
    ProjectValidationError,
    read_project,
    write_authored_chunks,
    write_layout_edits,
    write_map_structure,
)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: Grand Kai. Its BG1 is the 2x2 chunk grid whose cell 0 is the accepted proof
#: case from MAP-LAYOUT-WRITE-001, MAP-TILE-PAINT-001 and MAP-CHUNK-AUTHORING-001,
#: and the savestate the runtime proof uses loads this map.
GRAND_KAI = 40
GRAND_KAI_BG1 = 1
GRAND_KAI_BG1_RECORD = 0x08292C88
#: The map root's own BG1 slot pointer field: root 0x08293474 + ROOT_LAYER_SLOTS[1].
GRAND_KAI_BG1_SLOT_OFFSET = 0x0029348C
#: The first cell of the retail chunk window: record + LAYER_CHUNK_WINDOW_OFFSET.
GRAND_KAI_BG1_WINDOW_OFFSET = 0x00292CA0

#: Map 39 is on the runtime route (40 -> 39 -> 40) and leaves BG0 unused, which is
#: what makes it the layer-authoring target.
OVERLAY_MAP = 39
OVERLAY_SLOT = 0
OVERLAY_TEMPLATE = "map:0039/BG1"


def _rom_path() -> Path:
    configured = os.environ.get("LOGX_CANONICAL_ROM") or os.environ.get("WEBFOOT_BUU_ROM")
    if configured:
        path = Path(configured)
        if not path.is_file():
            pytest.skip(f"canonical ROM does not exist: {path}")
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


@pytest.fixture(scope="module")
def resizer(image: bytes) -> mr.MapResizer:
    return mr.MapResizer(image)


@pytest.fixture(scope="module")
def project_template(rom: Path, catalog: RomProfileCatalog) -> Path:
    """One extraction per module, reused when it is already on disk.

    Extraction is the expensive part (~10 s), not the edit, and several tests need
    a private copy of it. The directory is a fixed ignored build path rather than
    pytest's temporary tree, because `--basetemp` is cleared at the start of every
    run and a module-scoped fixture must not depend on that.
    """
    directory = Path("build") / "tmp" / "resize001-template"
    if not (directory / "project.toml").is_file():
        import shutil

        shutil.rmtree(directory, ignore_errors=True)
        extract_project(rom, directory, catalog, graphics=False)
    return directory


def _project(project_template: Path, tmp_path: Path) -> Path:
    import shutil

    target = tmp_path / "project"
    shutil.copytree(project_template, target)
    return target


# --- the structural model on the real corpus ---------------------------------

def test_a_dominant_record_is_exactly_its_header_plus_its_window(image: bytes):
    """Measured over the whole corpus, restated as the record's contract.

    Nothing else belongs to the record, which is why a grid that grows needs the
    record relocated: the bytes right after the window are live.
    """
    reader = mg.MapGraphicsReader(image, packaged_profile())
    checked = 0
    for entry in mg.read_map_entries(reader):
        for slot in mg.read_layers(reader, entry.root_address):
            if slot.classification != "dominant":
                continue
            size = mg.layer_record_size(slot.chunk_x, slot.chunk_y)
            assert size == mg.LAYER_CHUNK_WINDOW_OFFSET + 4 * slot.chunk_cells
            # On map 40 BG1 the word after the window is a container header, so the
            # next structure really does begin there.
            checked += 1
    assert checked == 1516


def test_the_canonical_slot_after_grand_kais_bg1_window_is_a_live_container(image: bytes):
    """The bytes right after the window belong to the next structure.

    That is the measurement which makes "widen the window in place" impossible and
    a relocated record necessary.
    """
    reader = mg.MapGraphicsReader(image, packaged_profile())
    layer = mg.read_layer(reader, mg.read_map_entries(reader)[GRAND_KAI].root_address,
                          GRAND_KAI_BG1)
    assert layer.address == GRAND_KAI_BG1_RECORD
    end = layer.address + mg.layer_record_size(layer.chunk_x, layer.chunk_y)
    assert end == 0x08292CB0
    # that word is the kind-1 container header BG2's cell 0 points at
    assert reader.u32(end) == 0x00000001
    bg2 = mg.read_layer(reader, mg.read_map_entries(reader)[GRAND_KAI].root_address, 2)
    assert bg2.chunk_addresses[0] == end


def test_the_extent_word_is_the_camera_maximum_on_the_real_map(image: bytes):
    """Map 40's declared extent is (90, 186) pixels, stored as extent - 1."""
    reader = mg.MapGraphicsReader(image, packaged_profile())
    entry = mg.read_map_entries(reader)[GRAND_KAI]
    assert reader.u16(entry.root_address + mg.ROOT_EXTENT_X_OFFSET) == 89
    assert reader.u16(entry.root_address + mg.ROOT_EXTENT_Y_OFFSET) == 185


def test_the_corpus_really_contains_shared_roots_and_they_are_refused(resizer):
    """Shared state is refused, and Grand Kai's own root is not shared."""
    assert resizer.target(GRAND_KAI).shared_with == ()
    # map 23 and 32 load one definition (measured: 11 shared roots over 452 maps)
    shared = resizer.target(23)
    assert shared.shared_with == (32,)
    assert shared.editable is False
    with pytest.raises(mr.MapStructureError, match="shared state"):
        resizer.resize(23, 0, 3, 2, 1)


def test_the_supported_map_family_is_the_ordinary_dominant_chunk_grid(resizer):
    """A special form is refused with its own reason rather than forced."""
    target = resizer.target(19)
    terrain = next(layer for layer in target.slots if layer.classification
                   == "static_graphical_terrain_field")
    assert terrain.read_only_reason and "terrain-field" in terrain.read_only_reason
    with pytest.raises(mr.MapStructureError, match="terrain-field"):
        resizer.resize(19, terrain.slot, 2, 2, 1)


def test_only_a_slot_the_image_leaves_unused_can_be_activated(resizer):
    with pytest.raises(mr.MapStructureError, match="fixed at 4"):
        resizer.authored_layer("overlay", GRAND_KAI, 0, "map:0040/BG1", 3, 2, 1)
    assert resizer.target(OVERLAY_MAP).free_slots == (OVERLAY_SLOT,)


# --- the resize transform on the real map ------------------------------------

def test_grand_kais_bg1_grows_by_coordinate_and_only_the_added_cells_change(
    image: bytes, resizer: mr.MapResizer
):
    """Top-left anchored: retail cell (x, y) lands at new cell (x, y).

    The check is at the boundary (the whole first added column) and at every
    retail cell, which is what a wrong row stride or a wrong anchor breaks.
    """
    resize = resizer.resize(GRAND_KAI, GRAND_KAI_BG1, 3, 2, 2)
    resolved = mr.resolve_layer_record(image, resize)
    assert (resolved.retail_columns, resolved.retail_rows) == (2, 2)
    assert (resolved.columns, resolved.rows) == (3, 2)
    addresses = [entry[1] for entry in resolved.window]
    assert addresses[0] == 0x082928DC      # retail (0, 0)
    assert addresses[1] == 0x08292A54      # retail (1, 0)
    assert addresses[3] == 0x08292AFC      # retail (0, 1)
    assert addresses[4] == 0x08292BD8      # retail (1, 1)
    # the whole first added column is the initialization chunk (the layer's 2nd)
    assert addresses[2] == 0x08292A54
    assert addresses[5] == 0x08292A54


def test_the_resized_record_is_the_header_copied_bit_for_bit(image: bytes):
    resize = mr.MapResizer(image).resize(GRAND_KAI, GRAND_KAI_BG1, 3, 2, 2)
    resolved = mr.resolve_layer_record(image, resize)
    canonical = image[GRAND_KAI_BG1_RECORD - 0x08000000:][:0x18]
    assert resolved.record[:0x14] == canonical[:0x14]
    assert resolved.record[0x16:0x18] == canonical[0x16:0x18]
    assert resolved.record[0x14] == 3 and resolved.record[0x15] == 2
    assert len(resolved.record) == 0x18 + 4 * 6


def test_the_resize_raises_the_extent_to_the_grown_planes_reach(image: bytes):
    resize = mr.MapResizer(image).resize(GRAND_KAI, GRAND_KAI_BG1, 3, 2, 2)
    resolved = mr.resolve_layer_record(image, resize)
    assert resolved.extent_changes == (
        ("x", 0x0829347C, mg.declared_extent_raw(3 * mg.CHUNK_PIXELS, 240)),
        ("y", 0x0829347E, mg.declared_extent_raw(2 * mg.CHUNK_PIXELS, 160)),
    )
    assert 528 == mg.declared_extent_raw(3 * mg.CHUNK_PIXELS, 240)


def test_a_shrink_is_refused_with_its_reason(resizer):
    with pytest.raises(mr.MapStructureError, match="not supported"):
        resizer.resize(GRAND_KAI, GRAND_KAI_BG1, 1, 2, 1)


# --- layer authoring on the real map -----------------------------------------

def test_an_authored_layer_composes_from_its_templates_own_chunks(
    image: bytes, resizer: mr.MapResizer
):
    layer = resizer.authored_layer("overlay", OVERLAY_MAP, OVERLAY_SLOT,
                                   OVERLAY_TEMPLATE, 3, 2, 2)
    assert layer.map_index == OVERLAY_MAP and layer.layer_slot == OVERLAY_SLOT
    resolved = mr.resolve_layer_record(image, layer)
    template = resizer.vocabulary(OVERLAY_MAP, 1)
    assert resolved.template_address == mg.read_layer(
        mg.MapGraphicsReader(image, packaged_profile()),
        mg.read_map_entries(mg.MapGraphicsReader(image, packaged_profile()))[OVERLAY_MAP].root_address,
        1,
    ).address
    fill = template[1].address
    assert [entry[1] for entry in resolved.window] == [fill] * 6
    assert resolved.record[0x14] == 3 and resolved.record[0x15] == 2
    # an authored layer adds pixels; it does not move the camera's reach
    assert resolved.extent_changes == ()


def test_the_authored_layer_never_writes_over_its_template(image: bytes, resizer):
    layer = resizer.authored_layer("overlay", OVERLAY_MAP, OVERLAY_SLOT,
                                   OVERLAY_TEMPLATE, 3, 2, 2)
    structure = MapStructure(resizes={}, layers={layer.identity: layer})
    materialization = mr.materialize_map_structure(image, structure)
    template_record = _template_address(image)
    template_bytes = image[template_record - 0x08000000:][:0x28]
    for change in materialization.changes:
        if change.offset < len(image):
            assert not (
                change.offset < template_record - 0x08000000 + 0x28
                and change.offset + len(change.old) > template_record - 0x08000000
            )
    assert image[template_record - 0x08000000:][:0x28] == template_bytes
    # The authored record is a DIFFERENT record at a different address: the
    # template is read and named, never rewritten. (An earlier version of this
    # node compared the canonical image against itself in a loop, which asserted
    # nothing - caught by the independent review and replaced with the two facts
    # the copy-independence claim actually rests on.)
    assert materialization.builds[0].record_address != template_record
    assert materialization.builds[0].resolved.template_address == template_record
    # and every chunk body the template layer draws is still readable, with the
    # container header it had: the build did not scribble over the template's art.
    for choice in resizer.vocabulary(OVERLAY_MAP, 1):
        container = mg.MapGraphicsReader(image, packaged_profile()).container(
            choice.address, expected=mg.CHUNK_DECODED_BYTES
        )
        assert len(container.data) == mg.CHUNK_DECODED_BYTES


def _template_address(image: bytes) -> int:
    reader = mg.MapGraphicsReader(image, packaged_profile())
    entry = mg.read_map_entries(reader)[OVERLAY_MAP]
    return mg.read_layer(reader, entry.root_address, 1).address


# --- a created layer that is then grown, on the real map ----------------------

def test_a_project_authored_layer_is_created_and_then_grown(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    image: bytes, resizer: mr.MapResizer,
):
    """The pair, driven the way an author drives it: persistence, reopen, build.

    Map 39's BG0 is the free slot and its BG1 is the template. The layer is
    created at 1x1 and then grown to 2x1 through `set_authored_layer` and
    `set_layer_resize`, so the capability is proven on the authoring path rather
    than on a hand-assembled structure.

    The grown plane is 512x256 px and map 39's declared extent already covers it,
    so the ONE canonical byte-range this project changes is the map root's own BG0
    slot pointer: the created layer's cell keeps its coordinate and only the added
    cell takes the resize's initialization.
    """
    project = _project(project_template, tmp_path)
    layer = resizer.authored_layer(
        "grown", OVERLAY_MAP, OVERLAY_SLOT, OVERLAY_TEMPLATE, 1, 1, 1
    )
    assert mr.set_authored_layer(project, image, layer) is True
    resize = LayerResize(OVERLAY_MAP, OVERLAY_SLOT, 2, 1, 2)
    assert mr.set_layer_resize(project, image, resize) is True

    reopened = read_project(project)
    assert (reopened.structure.layer_at(OVERLAY_MAP, OVERLAY_SLOT).columns,
            reopened.structure.layer_at(OVERLAY_MAP, OVERLAY_SLOT).rows) == (1, 1)
    assert reopened.structure.resize_for(OVERLAY_MAP, OVERLAY_SLOT) == resize

    output = tmp_path / "grown.gba"
    result = build_project(project, rom, output, catalog)
    derivative = output.read_bytes()
    reader = mg.MapGraphicsReader(derivative, packaged_profile())
    entries = mg.read_map_entries(reader)
    bg0 = mg.read_layer(reader, entries[OVERLAY_MAP].root_address, OVERLAY_SLOT)
    assert (bg0.chunk_x, bg0.chunk_y) == (2, 1)
    assert bg0.handler == mg.DOMINANT_LAYER_HANDLER
    assert bg0.address >= 0x08000000 + len(image)

    vocabulary = resizer.vocabulary(OVERLAY_MAP, 1)
    assert bg0.chunk_addresses == (vocabulary[0].address, vocabulary[1].address)

    assert len(result.manifest.structure_edits) == 1
    provenance = result.manifest.structure_edits[0]
    assert provenance.owner == "layer:grown"
    assert provenance.kind == "resize"
    assert provenance.authored is True
    assert provenance.authored_layer == "layer:grown"
    assert (provenance.authored_columns, provenance.authored_rows) == (1, 1)
    assert (provenance.columns, provenance.rows) == (2, 1)
    assert provenance.template_address == _template_address(image)
    assert len(provenance.extents) == 0

    slot_offset = (
        entries[OVERLAY_MAP].root_address + mg.ROOT_LAYER_SLOTS[OVERLAY_SLOT]
    ) - 0x08000000
    canonical = [c for c in result.manifest.changes if c.offset < len(image)]
    assert [c.offset for c in canonical] == [slot_offset]
    assert canonical[0].new == bg0.address.to_bytes(4, "little")


# --- placement, addressability and the emitted derivative ---------------------

def _authored_structure(image: bytes, resizer: mr.MapResizer) -> MapStructure:
    resize = resizer.resize(GRAND_KAI, GRAND_KAI_BG1, 3, 2, 2)
    layer = resizer.authored_layer("overlay", OVERLAY_MAP, OVERLAY_SLOT,
                                   OVERLAY_TEMPLATE, 3, 2, 2)
    return MapStructure(
        resizes={resize.key: resize}, layers={layer.identity: layer}
    )


def test_every_authored_record_lands_above_the_canonical_eof(image: bytes, resizer):
    structure = _authored_structure(image, resizer)
    materialization = mr.materialize_map_structure(image, structure)
    assert len(materialization.builds) == 2
    for build in materialization.builds:
        assert build.expanded
        assert build.allocation.range.start.value >= len(image)
        assert build.record_address == 0x08000000 + build.allocation.range.start.value
        assert len(materialization.reserved) == 2
    spans = sorted((b.allocation.range for b in materialization.builds),
                   key=lambda span: span.start.value)
    assert not spans[0].overlaps(spans[1])


def test_the_root_slot_field_really_resolves_to_the_relocated_record(image: bytes, resizer):
    structure = _authored_structure(image, resizer)
    materialization = mr.materialize_map_structure(image, structure)
    resize_build = next(b for b in materialization.builds if b.resolved.kind == "resize")
    assert resize_build.slot_offset == GRAND_KAI_BG1_SLOT_OFFSET
    assert resize_build.previous_record_address == GRAND_KAI_BG1_RECORD
    change = next(c for c in materialization.changes
                  if c.offset == GRAND_KAI_BG1_SLOT_OFFSET)
    assert change.old == GRAND_KAI_BG1_RECORD.to_bytes(4, "little")
    assert change.new == resize_build.record_address.to_bytes(4, "little")
    assert resize_build.record_address >= 0x08000000 + len(image)


def test_allocation_is_deterministic_across_two_resolutions(image: bytes, resizer):
    structure = _authored_structure(image, resizer)
    first = mr.materialize_map_structure(image, structure)
    second = mr.materialize_map_structure(image, structure)
    assert [b.record_address for b in first.builds] == [b.record_address for b in second.builds]
    assert [c.offset for c in first.changes] == [c.offset for c in second.changes]


def _built(tmp_path: Path, project_template: Path, rom: Path,
           catalog: RomProfileCatalog, resizer: mr.MapResizer):
    project = _project(project_template, tmp_path)
    structure = _authored_structure(rom.read_bytes(), resizer)
    write_map_structure(project, structure)
    output = tmp_path / "authored.gba"
    result = build_project(project, rom, output, catalog)
    return project, output, result


def test_the_canonical_region_differs_only_where_the_manifest_says(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    resizer: mr.MapResizer, image: bytes,
):
    """Unchanged-resource safety, stated as bytes rather than as an intention.

    The derivative's canonical region is compared against the canonical image
    byte for byte; every differing offset must lie inside a declared change, and
    the declared changes must account for every difference. That is what makes
    "unrelated maps, unrelated layers and every chunk body are untouched" a
    measurement instead of a claim.
    """
    _project_dir, output, result = _built(tmp_path, project_template, rom, catalog, resizer)
    derivative = output.read_bytes()[:len(image)]
    declared = set()
    for change in result.manifest.changes:
        if change.offset < len(image):
            declared.update(range(change.offset, min(change.end, len(image))))
    differ = {
        offset for offset in range(len(image)) if derivative[offset] != image[offset]
    }
    assert differ, "the build changed nothing in the canonical region"
    # Every byte that differs is inside a declared change: nothing was written
    # that the manifest does not attribute.
    assert differ <= declared, sorted(differ - declared)[:8]
    # And the count agrees with what the changes themselves declare, so a change
    # that silently wrote something other than its `new` bytes cannot hide here.
    from_changes = sum(
        1
        for change in result.manifest.changes
        if change.offset < len(image)
        for old, new in zip(change.old, change.new)
        if old != new
    )
    assert len(differ) == from_changes


def test_a_built_map_carries_the_resized_grid_and_the_authored_layer(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    resizer: mr.MapResizer, image: bytes,
):
    _project_dir, output, result = _built(tmp_path, project_template, rom, catalog, resizer)
    derivative = output.read_bytes()
    assert len(derivative) > len(image)
    reader = mg.MapGraphicsReader(derivative, packaged_profile())
    entries = mg.read_map_entries(reader)

    bg1 = mg.read_layer(reader, entries[GRAND_KAI].root_address, GRAND_KAI_BG1)
    assert (bg1.chunk_x, bg1.chunk_y) == (3, 2)
    assert bg1.address >= 0x08000000 + len(image)
    assert bg1.chunk_addresses == (
        0x082928DC, 0x08292A54, 0x08292A54, 0x08292AFC, 0x08292BD8, 0x08292A54,
    )
    assert reader.u16(entries[GRAND_KAI].root_address + mg.ROOT_EXTENT_X_OFFSET) == 528
    assert reader.u16(entries[GRAND_KAI].root_address + mg.ROOT_EXTENT_Y_OFFSET) == 352

    bg0 = mg.read_layer(reader, entries[OVERLAY_MAP].root_address, OVERLAY_SLOT)
    assert bg0.handler == mg.DOMINANT_LAYER_HANDLER
    assert (bg0.chunk_x, bg0.chunk_y) == (3, 2)
    assert bg0.address >= 0x08000000 + len(image)

    # the unrelated layers are byte-identical to retail
    for index in (GRAND_KAI, OVERLAY_MAP):
        for slot in range(4):
            if (index, slot) in ((GRAND_KAI, GRAND_KAI_BG1), (OVERLAY_MAP, OVERLAY_SLOT)):
                continue
            before = mg.read_layer(
                mg.MapGraphicsReader(image, packaged_profile()),
                mg.read_map_entries(mg.MapGraphicsReader(image, packaged_profile()))[index].root_address,
                slot,
            )
            after = mg.read_layer(reader, entries[index].root_address, slot)
            assert before.address == after.address
            assert before.chunk_addresses == after.chunk_addresses
            assert before.handler == after.handler

    # the canonical region changed only in the declared, attributed places
    for change in result.manifest.changes:
        if change.offset < len(image):
            assert change.owner in {
                f"map:{GRAND_KAI:04d}/BG{GRAND_KAI_BG1}",
                f"layer:overlay",
            }
    assert result.manifest.structure_edits
    kinds = {prov.kind for prov in result.manifest.structure_edits}
    assert kinds == {"resize", "layer"}
    assert all(prov.expanded for prov in result.manifest.structure_edits)


def test_the_build_is_deterministic_and_the_canonical_image_is_untouched(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    resizer: mr.MapResizer,
):
    project, output, _result = _built(tmp_path, project_template, rom, catalog, resizer)
    second = tmp_path / "again.gba"
    build_project(project, rom, second, catalog)
    assert output.read_bytes() == second.read_bytes()
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_the_project_reopens_with_the_structure_and_the_cell_content_intact(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    resizer: mr.MapResizer,
):
    project = _project(project_template, tmp_path)
    structure = _authored_structure(rom.read_bytes(), resizer)
    write_map_structure(project, structure)
    write_layout_edits(
        project, LayoutEdits(maps={f"map:{OVERLAY_MAP:04d}": {OVERLAY_SLOT: {0: 3, 5: 2}}})
    )
    reopened = read_project(project)
    assert reopened.structure == structure
    assert reopened.structure.resize_for(GRAND_KAI, GRAND_KAI_BG1).columns == 3
    assert reopened.structure.layer_at(OVERLAY_MAP, OVERLAY_SLOT).identity == "layer:overlay"
    assert reopened.layout.cells()[(OVERLAY_MAP, OVERLAY_SLOT, 0)] == 3
    # and the resolved grid honours the authored cells over the initialization
    resolved = mr.resolve_layer_record(
        rom.read_bytes(),
        reopened.structure.layer_at(OVERLAY_MAP, OVERLAY_SLOT),
        layout=reopened.layout,
    )
    vocabulary = resizer.vocabulary(OVERLAY_MAP, 1)
    assert resolved.window[0][1] == vocabulary[2].address
    assert resolved.window[5][1] == vocabulary[1].address


# --- the paint authority understands the authored structure -------------------

def test_the_map_painter_reads_the_authored_grid_and_vocabulary(
    image: bytes, resizer: mr.MapResizer
):
    """The normal painter is what a Workbench surface drives, so it must see the
    authored dimensions and the same brush set the SDK accepts."""
    structure = _authored_structure(image, resizer)
    painter = mp.MapPainter(image, structure=structure)
    bg1 = painter.layer(GRAND_KAI, GRAND_KAI_BG1)
    assert bg1.structural and bg1.editable
    assert (bg1.columns, bg1.rows) == (3, 2)
    assert [cell.offset for cell in bg1.cells] == [
        0x00292CA0, 0x00292CA4, -1, 0x00292CA8, 0x00292CAC, -1,
    ]
    # painting the added column is accepted, and it is persisted semantically
    edit = painter.resolve(GRAND_KAI, GRAND_KAI_BG1, 2, 1)
    assert edit.replacement == resizer.vocabulary(GRAND_KAI, GRAND_KAI_BG1)[0].address
    assert edit.offset == -1
    with pytest.raises(mp.MapPaintError, match="no canonical four-byte field"):
        edit.to_change(image)

    overlay = painter.layer(OVERLAY_MAP, OVERLAY_SLOT)
    assert overlay.structural and overlay.editable
    assert (overlay.columns, overlay.rows) == (3, 2)
    assert all(cell.offset == -1 for cell in overlay.cells)
    # The structural grid's own fill vocabulary leads - so an ordinal a project
    # already stored keeps resolving - and the map's sibling chunks follow it.
    fill = [choice.address for choice in resizer.vocabulary(OVERLAY_MAP, 1)]
    assert [choice.pointer for choice in overlay.vocabulary][: len(fill)] == fill
    # The same set the canonical grids of this map offer, no wider and no narrower.
    canonical = set()
    for slot in range(4):
        if slot == OVERLAY_SLOT:
            continue
        canonical.update(
            choice.pointer for choice in painter.layer(OVERLAY_MAP, slot).vocabulary
        )
    assert set(choice.pointer for choice in overlay.vocabulary) == set(fill) | canonical


def test_the_painter_refuses_a_cell_outside_the_authored_grid(
    image: bytes, resizer: mr.MapResizer
):
    structure = _authored_structure(image, resizer)
    painter = mp.MapPainter(image, structure=structure)
    with pytest.raises(mp.MapPaintError, match="outside"):
        painter.resolve(GRAND_KAI, GRAND_KAI_BG1, 6, 1)


def test_an_ordinal_paint_on_a_canonical_layer_is_unchanged_by_the_structure(
    image: bytes, resizer: mr.MapResizer
):
    """A structure document must not change what a canonical slot offers."""
    structure = _authored_structure(image, resizer)
    plain = mp.MapPainter(image)
    structured = mp.MapPainter(image, structure=structure)
    for map_index in (GRAND_KAI, OVERLAY_MAP):
        for slot in range(4):
            if (map_index, slot) in ((GRAND_KAI, GRAND_KAI_BG1), (OVERLAY_MAP, OVERLAY_SLOT)):
                continue
            left, right = plain.layer(map_index, slot), structured.layer(map_index, slot)
            assert (left.columns, left.rows) == (right.columns, right.rows)
            assert [c.offset for c in left.cells] == [c.offset for c in right.cells]
            assert [c.pointer for c in left.vocabulary] == [
                c.pointer for c in right.vocabulary
            ]


# --- refusals fail closed ----------------------------------------------------

def test_validation_reports_a_structural_problem_without_building(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    image: bytes, resizer: mr.MapResizer,
):
    """A structurally illegal but textually valid document is reported by
    `validate_project`, and the build refuses it too."""
    project = _project(project_template, tmp_path)
    # map 19's BG3 is the terrain-field form, not a chunk grid: the document parses
    # and the semantics refuse it.
    write_map_structure(
        project,
        MapStructure(
            resizes={
                LayerResize(19, 2, 2, 2, 1).key: LayerResize(19, 2, 2, 2, 1)
            }
        ),
    )
    assert read_project(project).structure.resize_for(19, 2) is not None
    report = validate_project(project, rom, catalog)
    assert report.problems
    assert any("terrain" in problem for problem in report.problems)
    with pytest.raises(ProjectValidationError):
        build_project(project, rom, tmp_path / "out.gba", catalog)


def test_a_malformed_persisted_dimension_is_refused_by_the_project_reader(
    tmp_path: Path, project_template: Path,
):
    """A hand-edited document cannot reach a build."""
    project = _project(project_template, tmp_path)
    (project / "maps").mkdir(parents=True, exist_ok=True)
    (project / "maps" / "structure.toml").write_text(
        '[resize."map:0040/BG1"]\ncolumns = 99\nrows = 2\nfill = 1\n',
        encoding="utf-8", newline="\n",
    )
    with pytest.raises(ProjectValidationError, match="supported range"):
        read_project(project)


def test_a_build_refuses_a_resize_of_an_unsupported_slot(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    image: bytes,
):
    """The build re-checks what the project file claims, so a hand-edited file
    cannot slip a structural edit past the facade."""
    project = _project(project_template, tmp_path)
    (project / "maps" / "structure.toml").write_text(
        '[resize."map:0019/BG2"]\ncolumns = 2\nrows = 2\nfill = 1\n',
        encoding="utf-8", newline="\n",
    )
    with pytest.raises(ProjectValidationError):
        build_project(project, rom, tmp_path / "out.gba", catalog)


def test_the_layout_reader_refuses_a_cell_outside_the_authored_grid(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    resizer: mr.MapResizer,
):
    project = _project(project_template, tmp_path)
    structure = _authored_structure(rom.read_bytes(), resizer)
    write_map_structure(project, structure)
    write_layout_edits(project, LayoutEdits(maps={f"map:{OVERLAY_MAP:04d}": {OVERLAY_SLOT: {9: 1}}}))
    with pytest.raises(ProjectValidationError, match="outside the 3x2 grid"):
        read_project(project)


def test_an_unplaced_authored_chunk_fill_is_refused_by_the_build(
    tmp_path: Path, project_template: Path, rom: Path, catalog: RomProfileCatalog,
    resizer: mr.MapResizer,
):
    """A fill naming an authored chunk the project does not declare is refused
    with the document that should have declared it."""
    project = _project(project_template, tmp_path)
    resize = resizer.resize(GRAND_KAI, GRAND_KAI_BG1, 3, 2, "chunk:missing")
    write_map_structure(project, MapStructure(resizes={resize.key: resize}))
    with pytest.raises(ProjectValidationError, match="does not declare"):
        build_project(project, rom, tmp_path / "out.gba", catalog)
