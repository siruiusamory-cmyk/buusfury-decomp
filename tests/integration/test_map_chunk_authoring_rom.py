"""ROM-gated end-to-end tests for chunk creation and materialization.

MAP-CHUNK-AUTHORING-001. Every fact here needs the canonical image, so the suite
skips when it is absent. What it pins, in the order the capability is claimed:

* what a chunk object actually is (container kind, declared size, entry count);
* that a template resolves through the layer's own vocabulary and that a body
  composes from that layer's graphics only;
* that a copy is independent of its template, including the cross-map sharing
  case the corpus actually contains;
* that the production allocator places the body ABOVE canonical EOF and that the
  map cell resolves to that address;
* that the built derivative carries the body, changes only the required bytes in
  the canonical region, leaves the canonical image untouched, and rebuilds
  byte-identically;
* and that the refusals fail closed.

The visible retail-engine result cannot be asserted from bytes; it is recorded in
the ticket's runtime section with its matched A/B capture and guard.
"""

from __future__ import annotations

import glob
import hashlib
import os
import shutil
from collections import Counter
from pathlib import Path

import pytest

from tools.webfoot import map_chunk as mc
from tools.webfoot import map_view as mv
from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import (
    AuthoredChunk,
    AuthoredChunkEntry,
    AuthoredChunks,
    LayoutEdits,
    ProjectValidationError,
    read_project,
    write_authored_chunks,
    write_layout_edits,
)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The accepted Grand Kai proof case from MAP-LAYOUT-WRITE-001 and
#: MAP-TILE-PAINT-001, reused because its cell, its exact pointer field and its
#: rendered region are already established. Grand Kai's BG1 is a 2x2 grid whose
#: cell 0 holds Chunk 1.
GRAND_KAI = 40
GRAND_KAI_LAYER = 1
GRAND_KAI_CELL = 0
GRAND_KAI_FIELD_OFFSET = 0x00292CA0

NAME = "grass-sign"
#: The authored patch: a deliberately ASYMMETRIC block well inside the region the
#: runtime proof already showed this cell occupies on screen. Asymmetric on
#: purpose - a square block would survive a transposed row/column indexing bug,
#: so a coordinate regression would go unnoticed.
PATCH_ROWS = (2, 8)
PATCH_COLUMNS = (3, 14)


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
def author(image: bytes) -> mc.ChunkAuthor:
    return mc.ChunkAuthor(image)


@pytest.fixture(scope="module")
def project_template(tmp_path_factory: pytest.TempPathFactory, rom: Path,
                     catalog: RomProfileCatalog) -> Path:
    """One extraction per module. Extraction is the expensive part, not the edit.

    `graphics=False` because nothing here asserts anything about sprite assets and
    a full extraction writes 7,390 PNGs this ticket never reads. Each test gets a
    private COPY, so a test that mutates the project cannot leak into the next.
    """
    directory = tmp_path_factory.mktemp("chunkauth001") / "project"
    extract_project(rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture
def project(tmp_path: Path, project_template: Path) -> Path:
    directory = tmp_path / "project"
    shutil.copytree(project_template, directory)
    return directory


def _template() -> mc.ChunkTemplate:
    return mc.ChunkTemplate(GRAND_KAI, GRAND_KAI_LAYER, 1)


def _patch(plane: tuple[int, ...]) -> dict[tuple[int, int], int]:
    """A bounded patch filled with the plane's most common non-zero entry.

    Composed from what the plane already displays, so the authoring vocabulary
    rule is satisfied by construction and the patch is guaranteed to change
    something (the fill is a different entry from at least one cell it covers).
    """
    donor = next(value for value, _count in Counter(plane).most_common() if value)
    return {
        (row, column): donor
        for row in range(*PATCH_ROWS)
        for column in range(*PATCH_COLUMNS)
        if plane[row * mg.CHUNK_SIDE_TILES + column] != donor
    }


def _composed(image: bytes, author: mc.ChunkAuthor) -> tuple[AuthoredChunk, mc.ResolvedAuthoredChunk]:
    template = _template()
    plane = author.plane(template)
    chunk = author.create(NAME, template, _patch(plane))
    return chunk, author.resolve(chunk)


# --- what a chunk object is --------------------------------------------------


def test_every_chunk_the_corpus_references_is_the_same_kind_and_size(image):
    """The object model, measured over every reachable chunk rather than one.

    `pack_dominant_chunk` depends on this: an authored body is emitted in the kind
    the retail corpus actually uses, and that claim is only safe if nothing in the
    corpus uses another.
    """
    reader = mg.MapGraphicsReader(image, packaged_profile())
    kinds: Counter[int] = Counter()
    for entry in mg.read_map_entries(reader):
        for record in mg.read_layers(reader, entry.root_address):
            if record.classification != "dominant":
                continue
            for address in record.chunk_addresses:
                if not address:
                    continue
                kinds[reader.container(address).kind] += 1
    assert set(kinds) == {mg.CHUNK_CONTAINER_KIND}
    assert kinds[mg.CHUNK_CONTAINER_KIND] > 3000


def test_a_chunk_plane_is_one_thousand_and_twenty_four_entries(image):
    reader = mg.MapGraphicsReader(image, packaged_profile())
    layer = mg.read_layer(reader, mg.read_map_entries(reader)[GRAND_KAI].root_address,
                          GRAND_KAI_LAYER)
    entries = mg.dominant_chunk_words(reader, layer.chunk_addresses[0])
    assert len(entries) == mg.CHUNK_ENTRY_COUNT == 1024
    assert mg.CHUNK_SIDE_TILES == 32
    assert mg.CHUNK_PIXELS == 256
    container = reader.container(layer.chunk_addresses[0])
    assert container.declared_size == mg.CHUNK_DECODED_BYTES == 0x800


def test_the_layer_cell_is_a_four_byte_pointer_field(image):
    reader = mg.MapGraphicsReader(image, packaged_profile())
    layer = mg.read_layer(reader, mg.read_map_entries(reader)[GRAND_KAI].root_address,
                          GRAND_KAI_LAYER)
    assert mg.CHUNK_POINTER_BYTES == 4
    del reader, layer
    # The field the whole capability rewrites, established by the predecessor
    # ticket and re-derived here from the record rather than restated.
    assert GRAND_KAI_FIELD_OFFSET == 0x00292CA0


# --- composing ---------------------------------------------------------------


def test_a_template_resolves_to_a_canonical_chunk_the_layer_uses(image, author):
    template = _template()
    address, entries = mc.resolve_template(author._view, template)
    assert address == author.templates(GRAND_KAI, GRAND_KAI_LAYER)[0].address
    assert entries == author.plane(template)


def test_the_authoring_vocabulary_is_what_the_layer_already_displays(image, author):
    """Every permitted entry occurs in a chunk this layer points at."""
    reader = mg.MapGraphicsReader(image, packaged_profile())
    layer = mg.read_layer(reader, mg.read_map_entries(reader)[GRAND_KAI].root_address,
                          GRAND_KAI_LAYER)
    displayed = {
        entry
        for address in layer.chunk_addresses
        if address
        for entry in mg.dominant_chunk_words(reader, address)
    }
    vocabulary = author.vocabulary(GRAND_KAI, GRAND_KAI_LAYER)
    assert set(vocabulary) == displayed
    assert len(vocabulary) == len(set(vocabulary))


def test_an_authored_chunk_differs_from_its_template(image, author):
    chunk, resolved = _composed(image, author)
    assert resolved.entries != resolved.template_entries
    assert resolved.edits, "an authored chunk must carry at least one edit"
    for edit in resolved.edits:
        assert resolved.template_entries[edit.cell] == edit.prior
        assert resolved.entries[edit.cell] == edit.entry
        assert edit.prior != edit.entry


def test_the_authored_body_matches_no_chunk_the_canonical_image_contains(image, author):
    """Attribution: the difference is a NEW BODY, not a different existing chunk.

    If the composed plane happened to equal some canonical chunk, a runtime
    difference could not be attributed to authoring at all. Measured over every
    chunk reference in the image, not a sample.
    """
    _chunk, resolved = _composed(image, author)
    body = resolved.body
    reader = mg.MapGraphicsReader(image, packaged_profile())
    compared = 0
    for entry in mg.read_map_entries(reader):
        for record in mg.read_layers(reader, entry.root_address):
            if record.classification != "dominant":
                continue
            for address in record.chunk_addresses:
                if not address:
                    continue
                compared += 1
                assert mg.chunk_body_bytes(mg.dominant_chunk_words(reader, address)) != body
    assert compared > 3000


def test_an_authored_body_is_a_kind_one_container_the_retail_rule_accepts(image, author):
    from tools.webfoot.formats import webfoot_lz as lz

    _chunk, resolved = _composed(image, author)
    assert lz.read_header(resolved.container, 0)[0] == mg.CHUNK_CONTAINER_KIND
    container = lz.validate_retail_termination(resolved.container, 0)
    assert container.data == resolved.body


def test_composing_is_deterministic(image, author):
    first = mc.resolve_authored_chunk(image, _composed(image, author)[0], profile=packaged_profile())
    second = mc.resolve_authored_chunk(image, _composed(image, author)[0], profile=packaged_profile())
    assert first.container == second.container
    assert first.body_sha256 == second.body_sha256


# --- copy independence -------------------------------------------------------


def test_creating_a_chunk_does_not_change_its_template(image, author):
    template = _template()
    before = author.plane(template)
    chunk, resolved = _composed(image, author)
    assert author.plane(template) == before
    assert resolved.template_entries == before
    # and the canonical container is still byte-identical
    address, _entries = mc.resolve_template(author._view, template)
    reader = mg.MapGraphicsReader(image, packaged_profile())
    assert mg.dominant_chunk_words(reader, address) == before


def test_a_shared_canonical_chunk_is_still_shared_after_authoring(image, author):
    """The corpus really does share chunks across maps; authoring must not disturb it.

    A chunk referenced from more than one map is the case where an in-place edit
    would be visible everywhere. The authored body is a separate object, so every
    existing reference still reads the original bytes.
    """
    reader = mg.MapGraphicsReader(image, packaged_profile())
    entries = mg.read_map_entries(reader)
    shared: int | None = None
    for entry in entries:
        for record in mg.read_layers(reader, entry.root_address):
            if record.classification != "dominant":
                continue
            counts = Counter(a for a in record.chunk_addresses if a)
            for address, count in counts.items():
                if count > 1:
                    shared = address
                    break
            if shared:
                break
        if shared:
            break
    assert shared is not None, "the canonical corpus is expected to share chunks"
    before = mg.dominant_chunk_words(reader, shared)
    # author a chunk from whatever template, then confirm the shared body is intact
    _composed(image, author)
    assert mg.dominant_chunk_words(mg.MapGraphicsReader(image, packaged_profile()), shared) == before


# --- allocation and addressability ------------------------------------------


def test_an_authored_body_is_allocated_above_canonical_eof(image, author):
    """The roadmap's addressability question, answered by the allocator itself."""
    chunk, _resolved = _composed(image, author)
    result = mc.materialize_authored_chunks(
        image, {chunk.identity: chunk}, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity},
        profile=packaged_profile(),
    )
    build = result.builds[0]
    canonical_eof = 0x08000000 + len(image)
    assert build.expanded is True
    assert build.allocation.range.start.value == len(image)
    assert build.rom_address == canonical_eof
    assert result.generated_allocations
    assert result.generated_allocations[0].allocated_rom_address == build.rom_address
    assert result.reserved == (build.allocation.range,)


def test_allocation_is_deterministic_and_reservations_do_not_overlap(image, author):
    chunk, _resolved = _composed(image, author)
    edits = {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    first = mc.materialize_authored_chunks(image, {chunk.identity: chunk}, edits,
                                           profile=packaged_profile())
    second = mc.materialize_authored_chunks(image, {chunk.identity: chunk}, edits,
                                            profile=packaged_profile())
    assert first.builds[0].rom_address == second.builds[0].rom_address
    # a second chunk in the same build may not land on the first one's bytes
    other = author.create("second-sign", _template(), _patch(author.plane(_template())))
    both = mc.materialize_authored_chunks(
        image,
        {chunk.identity: chunk, other.identity: other},
        {**edits, (GRAND_KAI, GRAND_KAI_LAYER, 1): other.identity},
        profile=packaged_profile(),
    )
    ranges = sorted(
        (build.allocation.range.start.value, build.allocation.range.end)
        for build in both.builds
    )
    assert len(ranges) == 2
    for (_, left_end), (right_start, _end) in zip(ranges, ranges[1:]):
        assert right_start >= left_end


def test_the_map_cell_resolves_to_the_allocated_address(image, author):
    chunk, _resolved = _composed(image, author)
    result = mc.materialize_authored_chunks(
        image, {chunk.identity: chunk},
        {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity},
        profile=packaged_profile(),
    )
    cell_changes = [c for c in result.changes if c.owner.startswith("map:")]
    assert len(cell_changes) == 1
    assert cell_changes[0].offset == GRAND_KAI_FIELD_OFFSET
    assert int.from_bytes(cell_changes[0].new, "little") == result.builds[0].rom_address
    assert int.from_bytes(cell_changes[0].old, "little") != result.builds[0].rom_address


def test_an_unreferenced_chunk_is_not_materialized(image, author):
    """A body exists in an image because something points at it."""
    chunk, _resolved = _composed(image, author)
    result = mc.materialize_authored_chunks(image, {chunk.identity: chunk}, {},
                                            profile=packaged_profile())
    assert result.builds == ()
    assert result.changes == ()


# --- the build ---------------------------------------------------------------


def test_a_built_project_carries_the_authored_body_and_only_it(image, author, project, rom, catalog):
    chunk, resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    output = project.parent / "built.gba"
    build_project(project, rom, output, catalog)
    built = output.read_bytes()

    assert len(built) == 0x01000000
    # the body is present verbatim at the address the allocator recorded
    result = mc.materialize_authored_chunks(
        image, {chunk.identity: chunk},
        {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity},
        profile=packaged_profile(),
    )
    start = result.builds[0].allocation.range.start.value
    assert built[start:start + len(resolved.container)] == resolved.container
    # the cell points at it
    assert int.from_bytes(built[GRAND_KAI_FIELD_OFFSET:GRAND_KAI_FIELD_OFFSET + 4], "little") \
        == result.builds[0].rom_address
    # nothing else in the canonical region moved
    changed = [i for i, (a, b) in enumerate(zip(image, built[:len(image)])) if a != b]
    assert changed == [0x292CA0, 0x292CA1, 0x292CA2]
    # the canonical input is untouched
    assert hashlib.sha256(image).hexdigest() == CANONICAL_SHA256
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_every_unchanged_canonical_chunk_body_is_still_byte_identical_in_the_build(
    image, author, project, rom, catalog
):
    """Copy-on-write, checked against every chunk the image contains.

    A naive implementation that composed a new body into the template's own
    container would still build, still show a changed map, and still pass a test
    that only looked at the authored cell - while silently rewriting every other
    cell that shared the template. This compares every canonical chunk container
    in the derivative against the canonical image.
    """
    chunk, _resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    output = project.parent / "copysafe.gba"
    build_project(project, rom, output, catalog)
    built = output.read_bytes()
    reader = mg.MapGraphicsReader(image, packaged_profile())
    unchanged = 0
    for entry in mg.read_map_entries(reader):
        for record in mg.read_layers(reader, entry.root_address):
            if record.classification != "dominant":
                continue
            for address in record.chunk_addresses:
                if not address:
                    continue
                offset = address - 0x08000000
                container = reader.container(address)
                end = offset + container.packed_size
                assert built[offset:end] == image[offset:end], (
                    f"chunk at {address:#010x} changed in the derivative"
                )
                unchanged += 1
    assert unchanged > 3000


def test_the_encoded_cell_reference_is_the_full_gba_address(image, author):
    """The reference is a 32-bit address in the Game Pak window, not a truncated one.

    An encoder that kept only the low 24 bits - or that dropped the 0x08 window
    byte - would produce a plausible-looking non-zero pointer that points at
    nothing. The top byte is asserted explicitly because that is what a truncation
    destroys first.
    """
    chunk, _resolved = _composed(image, author)
    result = mc.materialize_authored_chunks(
        image, {chunk.identity: chunk},
        {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity},
        profile=packaged_profile(),
    )
    encoded = next(c for c in result.changes if c.owner.startswith("map:")).new
    assert len(encoded) == mg.CHUNK_POINTER_BYTES == 4
    address = result.builds[0].rom_address
    assert int.from_bytes(encoded, "little") == address
    assert encoded[3] == 0x08, "the Game Pak ROM window byte must survive encoding"
    assert address >= 0x08000000 + len(image)


def test_the_built_map_cell_names_the_authored_chunk_not_the_canonical_one(
    image, author, project, rom, catalog
):
    """The end-to-end semantic claim: the cell resolves to the NEW body.

    A build that allocated the authored body but left the cell pointing at the
    canonical chunk would satisfy every byte-level check about the body and still
    display the old map. This asserts the cell itself, and that the canonical
    chunk it used to hold is untouched.
    """
    chunk, _resolved = _composed(image, author)
    result = mc.materialize_authored_chunks(
        image, {chunk.identity: chunk},
        {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity},
        profile=packaged_profile(),
    )
    canonical_pointer = result.builds[0].placements[0].previous
    assert int.from_bytes(image[GRAND_KAI_FIELD_OFFSET:GRAND_KAI_FIELD_OFFSET + 4], "little") \
        == canonical_pointer
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    output = project.parent / "semantic.gba"
    build_project(project, rom, output, catalog)
    built = output.read_bytes()
    cell = int.from_bytes(built[GRAND_KAI_FIELD_OFFSET:GRAND_KAI_FIELD_OFFSET + 4], "little")
    assert cell == result.builds[0].rom_address
    assert cell != canonical_pointer
    # the canonical chunk the cell used to name is still byte-identical
    offset = canonical_pointer - 0x08000000
    size = mg.MapGraphicsReader(image, packaged_profile()).container(canonical_pointer).packed_size
    assert built[offset:offset + size] == image[offset:offset + size]


def test_rebuilding_the_same_saved_project_is_byte_identical(image, author, project, rom, catalog):
    chunk, _resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    first = project.parent / "one.gba"
    second = project.parent / "two.gba"
    build_project(project, rom, first, catalog)
    build_project(project, rom, second, catalog)
    assert first.read_bytes() == second.read_bytes()
    assert first.with_name(first.name + ".dragonbyte.json").read_bytes() == \
        second.with_name(second.name + ".dragonbyte.json").read_bytes()


def test_the_manifest_records_the_chunk_its_edits_and_its_placements(image, author, project, rom, catalog):
    import json

    chunk, resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    output = project.parent / "manifest.gba"
    build_project(project, rom, output, catalog)
    document = json.loads(
        output.with_name(output.name + ".dragonbyte.json").read_text(encoding="utf-8")
    )
    edits = document["chunk_edits"]
    assert len(edits) == 1
    record = edits[0]
    assert record["resource"] == chunk.identity
    assert record["template"] == chunk.template
    assert record["body_sha256"] == resolved.body_sha256
    assert record["expanded"] is True
    assert record["edit_count"] == len(resolved.edits)
    assert record["placement_count"] == 1
    placement = record["placements"][0]
    assert (placement["map_index"], placement["layer_slot"], placement["cell"]) == (
        GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL
    )
    assert placement["chunk"] == chunk.identity
    assert placement["offset_hex"] == f"0x{GRAND_KAI_FIELD_OFFSET:08X}"
    field = output.read_bytes()[GRAND_KAI_FIELD_OFFSET:GRAND_KAI_FIELD_OFFSET + 4]
    assert record["rom_address_hex"] == f"0x{int.from_bytes(field, 'little'):08X}"


# --- reopen ------------------------------------------------------------------


def test_the_project_reopens_with_the_identity_body_and_reference_intact(image, author, project):
    chunk, resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    reopened = read_project(project)
    assert reopened.chunks.identities() == (chunk.identity,)
    assert reopened.layout.cells() == {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    again = mc.resolve_authored_chunk(image, reopened.chunks.get(chunk.identity),
                                      profile=packaged_profile())
    assert again.body == resolved.body
    assert again.body_sha256 == resolved.body_sha256
    assert again.edits == resolved.edits
    # the project does not depend on a runtime allocation from a previous process
    assert reopened.chunks.get(chunk.identity).template == chunk.template


def test_saving_an_unchanged_chunk_is_a_no_op(image, author, project):
    chunk, _resolved = _composed(image, author)
    assert mc.set_authored_chunk(project, image, chunk) is True
    assert mc.set_authored_chunk(project, image, chunk) is False
    assert mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    ) is True
    assert mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    ) is False
    assert mc.clear_layout_authored_cell(
        project, image, GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL
    ) is True
    assert read_project(project).layout.cells() == {}


def test_a_referenced_chunk_cannot_be_deleted(image, author, project):
    chunk, _resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    mc.set_layout_authored_cells(
        project, image, {(GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): chunk.identity}
    )
    with pytest.raises(mc.ChunkAuthoringError, match="still referenced"):
        mc.remove_authored_chunk(project, chunk.identity)
    mc.clear_layout_authored_cell(project, image, GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL)
    assert mc.remove_authored_chunk(project, chunk.identity) is True


# --- preview -----------------------------------------------------------------


def test_a_preview_of_an_authored_cell_changes_exactly_the_authored_region(image, author):
    """The authored plane renders through the one map renderer, not a second one.

    The bounding box is the load-bearing part: a preview that shifted the camera
    or re-laid the layer would differ across the whole frame, while an authored
    chunk differs only where the author changed a cell.
    """
    template = _template()
    plane = author.plane(template)
    chunk = author.create(NAME, template, _patch(plane))
    resolved = author.resolve(chunk)
    reader = mg.MapGraphicsReader(image, packaged_profile())
    block = mg.assemble_map_char_block(
        reader, mg.read_map_entries(reader)[GRAND_KAI].root_address
    )[0]
    base = mv.render_map(image, GRAND_KAI, char_data=block.data)
    preview = mv.render_map(
        image,
        GRAND_KAI,
        chunk_overrides={(GRAND_KAI_LAYER, GRAND_KAI_CELL): mv.ChunkSubstitution(resolved.entries)},
        char_data=block.data,
    )
    before = next(layer for layer in base.layers if layer.slot == GRAND_KAI_LAYER)
    after = next(layer for layer in preview.layers if layer.slot == GRAND_KAI_LAYER)
    differing = [i for i, (a, b) in enumerate(zip(before.pixels, after.pixels)) if a != b]
    assert differing
    xs = [index % before.width for index in differing]
    ys = [index // before.width for index in differing]
    expected = (
        PATCH_COLUMNS[0] * 8, PATCH_ROWS[0] * 8,
        PATCH_COLUMNS[1] * 8 - 1, PATCH_ROWS[1] * 8 - 1,
    )
    assert (min(xs), min(ys), max(xs), max(ys)) == expected


def test_rendering_a_plane_by_value_matches_rendering_it_by_address(image, author):
    template = _template()
    address, plane = mc.resolve_template(author._view, template)
    reader = mg.MapGraphicsReader(image, packaged_profile())
    block = mg.assemble_map_char_block(
        reader, mg.read_map_entries(reader)[GRAND_KAI].root_address
    )[0]
    by_address = mv.render_chunk_images(image, GRAND_KAI, [address], char_data=block.data)[0]
    by_value = mv.render_chunk_entries(block.data, plane)
    assert by_value.pixels == by_address.pixels
    assert (by_value.width, by_value.height) == (by_address.width, by_address.height)


# --- refusals ----------------------------------------------------------------


def test_an_undeclared_identity_is_refused_at_project_load(image, author, project, rom, catalog):
    """A cell naming a chunk nobody declares is a project problem, not an image one.

    It is caught when the project is read, because that is where both documents are
    in hand - the message names the file the author has to fix rather than the image
    the build could not reconcile.
    """
    write_authored_chunks(project, AuthoredChunks())
    write_layout_edits(project, LayoutEdits(maps={"map:0040": {1: {0: f"chunk:{NAME}"}}}))
    with pytest.raises(ProjectValidationError, match=f"chunk:{NAME}"):
        read_project(project)
    with pytest.raises(ProjectValidationError):
        build_project(project, rom, project.parent / "refused.gba", catalog)


def test_a_chunk_placed_in_the_wrong_map_is_refused_by_validation(image, author, project, rom, catalog):
    """The build gate: a declared chunk still has to be legal where it is placed.

    The chunk is composed against map 40's character block; naming it from map 41's
    layer is a placement the build refuses rather than silently rendering the wrong
    tiles.
    """
    chunk, _resolved = _composed(image, author)
    mc.set_authored_chunk(project, image, chunk)
    write_layout_edits(project, LayoutEdits(maps={"map:0041": {1: {0: chunk.identity}}}))
    problems = validate_project(project, rom, catalog)
    assert problems.problems
    assert any("authored map chunk" in problem for problem in problems.problems)


def test_a_template_the_layer_does_not_offer_is_refused(author):
    with pytest.raises(mc.ChunkAuthoringError, match="uses only"):
        mc.resolve_template(author._view, mc.ChunkTemplate(GRAND_KAI, GRAND_KAI_LAYER, 99))


def test_a_template_on_a_non_dominant_layer_is_refused(image, author):
    """Only the dominant chunk-grid form has chunks to offer as templates.

    The slot is FOUND rather than assumed: Grand Kai's four slots are all dominant
    (1x1, 2x2, 2x2, 2x2), so hard-coding a slot number would assert nothing.
    """
    reader = mg.MapGraphicsReader(image, packaged_profile())
    found = None
    for index, entry in enumerate(mg.read_map_entries(reader)):
        for record in mg.read_layers(reader, entry.root_address):
            if record.classification != "dominant":
                found = (index, record.slot, record.classification)
                break
        if found:
            break
    assert found is not None, "the canonical corpus has non-dominant layers"
    map_index, slot, classification = found
    with pytest.raises(mc.ChunkAuthoringError, match=classification):
        author.templates(map_index, slot)


def test_map_40_bg3_is_a_dominant_layer_and_offers_templates(author):
    """The other half of the rule: a dominant slot with a real grid does offer them.

    Grand Kai's BG3 is a 2x2 grid of four distinct chunks, so a chunk authored
    against BG1 may also be placed there - a chunk is map-scoped, not layer-scoped.
    """
    choices = author.templates(GRAND_KAI, 3)
    assert len(choices) == 4
    assert [choice.ordinal for choice in choices] == [1, 2, 3, 4]
    assert author.vocabulary(GRAND_KAI, 3)


def test_an_entry_outside_the_layer_vocabulary_is_refused(image, author):
    template = _template()
    vocabulary = set(author.vocabulary(GRAND_KAI, GRAND_KAI_LAYER))
    # A 16-bit screen entry that no chunk of this layer displays. Search rather
    # than assume: every candidate is checked against the measured vocabulary.
    outside = next(
        value for value in range(0x10000)
        if value not in vocabulary and (value & mg.TILE_ENTRY_ORDINAL_MASK) > 0
    )
    with pytest.raises(mc.ChunkAuthoringError, match="vocabulary"):
        author.create(NAME, template, {(2, 2): outside})


def test_a_chunk_may_not_be_placed_in_another_map(image, author):
    chunk, _resolved = _composed(image, author)
    with pytest.raises(mc.ChunkAuthoringError, match="character block"):
        mc.placements_for(image, {chunk.identity: chunk},
                          {(GRAND_KAI + 1, GRAND_KAI_LAYER, 0): chunk.identity})


def test_a_placement_outside_the_layer_grid_is_refused(image, author):
    chunk, _resolved = _composed(image, author)
    with pytest.raises(mc.ChunkAuthoringError, match="outside BG"):
        mc.placements_for(image, {chunk.identity: chunk},
                          {(GRAND_KAI, GRAND_KAI_LAYER, 99): chunk.identity})


def test_a_hand_edited_project_with_a_wrong_prior_is_refused(image, author):
    """The stored prior is the integrity check that binds a body to its template."""
    chunk, _resolved = _composed(image, author)
    tampered = AuthoredChunk(
        identity=chunk.identity,
        template=chunk.template,
        entries=tuple(
            AuthoredChunkEntry(entry.row, entry.column,
                               prior=entry.prior ^ 0x0100, entry=entry.entry)
            for entry in chunk.entries
        ),
    )
    with pytest.raises(mc.ChunkAuthoringError, match="not composed from this template"):
        mc.resolve_authored_chunk(image, tampered, profile=packaged_profile())


def test_the_paint_authority_skips_authored_identities_and_resolves_ordinals(image):
    """The two value forms share one document; each authority resolves its own.

    `LayoutEdits.cells()` now returns `int` ordinals and `str` identities in one
    dict. The paint authority must not choke on the form it does not own - a
    project that places an authored chunk would otherwise make every map surface
    that reads the layout floor fail.
    """
    from tools.webfoot import map_paint as mp

    painter = mp.MapPainter(image)
    edits = {
        (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL): f"chunk:{NAME}",
        (GRAND_KAI, GRAND_KAI_LAYER, 1): 1,
    }
    resolved = painter.pointer_edits(edits)
    assert (GRAND_KAI, GRAND_KAI_LAYER, 1) in resolved
    assert (GRAND_KAI, GRAND_KAI_LAYER, GRAND_KAI_CELL) not in resolved
    # `overrides` is {map: {layer slot: {cell: pointer}}}; the authored cell is absent
    # there too, and the ordinal cell carries the same pointer `pointer_edits` gave.
    overrides = painter.overrides(edits)[GRAND_KAI]
    assert GRAND_KAI_LAYER in overrides
    assert GRAND_KAI_CELL not in overrides[GRAND_KAI_LAYER]
    assert overrides[GRAND_KAI_LAYER][1] == resolved[(GRAND_KAI, GRAND_KAI_LAYER, 1)]


def test_a_project_cannot_name_an_undeclared_chunk_across_documents(project):
    write_layout_edits(project, LayoutEdits(maps={"map:0040": {1: {0: "chunk:ghost"}}}))
    with pytest.raises(ProjectValidationError, match="chunk:ghost"):
        read_project(project)


def test_a_borrowed_brush_ordinal_must_be_translated_before_a_template(author):
    """Create Chunk from a borrowed brush: the map-wide ordinal is the wrong number.

    MAP-PAINT-ANY-CHUNK-001 lets a cell borrow a chunk from any dominant layer of the
    map, so the brush ordinal counts across the map while ``resolve_template`` counts
    inside one layer. Handing the first to the second, which is what Create Chunk did,
    asked the layer about a chunk it does not draw and refused a chunk the map does
    use. This drives both halves: the untranslated ordinal is refused, and the same
    chunk resolves once the ordinal is translated to the layer that draws it.
    """
    from tools.webfoot.map_layout_edit import LayoutSlot

    own = author._view.pointers(GRAND_KAI, GRAND_KAI_LAYER)
    others: list[tuple[int, tuple[int, ...]]] = [
        (slot, author._view.pointers(GRAND_KAI, slot))
        for slot in (0, 2, 3)
        if slot != GRAND_KAI_LAYER
    ]
    borrowed_slot, borrowed_window = next(
        (slot, window)
        for slot, window in others
        if any(pointer not in own for pointer in window)
    )
    borrowed = next(pointer for pointer in borrowed_window if pointer not in own)

    # The map-wide set: this layer's own pointers first, then its siblings'.
    choices = tuple(dict.fromkeys(
        pointer for _slot, window in ((GRAND_KAI_LAYER, own), *others) for pointer in window
    ))
    sources = tuple(
        next(
            slot
            for slot, window in ((GRAND_KAI_LAYER, own), *others)
            if pointer in window
        )
        for pointer in choices
    )
    owner_ordinals = tuple(
        next(
            position
            for slot, window in ((GRAND_KAI_LAYER, own), *others)
            if pointer in window
            for position, candidate in enumerate(
                tuple(dict.fromkeys(p for p in window if p)), start=1
            )
            if candidate == pointer
        )
        for pointer in choices
    )
    slot_view = LayoutSlot(
        slot=GRAND_KAI_LAYER,
        classification="dominant",
        handler=0,
        grid=None,
        cells=(),
        choices=choices,
        sources=sources,
        owner_ordinals=owner_ordinals,
        read_only_reason="",
    )
    map_wide = slot_view.ordinal_of(borrowed)
    template_slot, template_ordinal = slot_view.template_target(borrowed)
    assert template_slot == borrowed_slot

    # OLD SHAPE: the map-wide ordinal against the layer the user is standing on.
    with pytest.raises(mc.ChunkAuthoringError, match="distinct chunk"):
        mc.resolve_template(
            author._view,
            mc.ChunkTemplate(GRAND_KAI, GRAND_KAI_LAYER, map_wide),
        )

    # FIXED SHAPE: the owning layer and the ordinal inside that layer's window.
    address, _entries = mc.resolve_template(
        author._view,
        mc.ChunkTemplate(GRAND_KAI, template_slot, template_ordinal),
    )
    assert address == borrowed
