"""SPRITE-NEW-AUTHORING-CORE-001: the planner against the canonical image.

ROM-gated and read-only. The suite skips cleanly when the private canonical Buu's
Fury image is not configured locally, and it never writes to it: every test plans
an in-memory derivative, and one test re-hashes the file afterwards to prove that.

What only this file can establish: that the production planner reproduces the
measured shape on the real 297-entry registry - the two published literal-pool
words repointed and no others, every canonical entry carried verbatim, no
existing structure, animation, frame or container byte changed, and an identity
the image never contained resolving end to end out of the emitted image through
the retail decoders. What the retail ENGINE does with that image is a separate,
runtime claim owned by ``docs/research/SPRITE_NEW_RUNTIME.md`` and its mGBA run;
nothing here is evidence for it.

**No ROM-derived fixture is committed.** The artwork this test plans is generated
in memory from the image's own palette, so no commercial pixel data is stored
here, and every expectation below is a count, an address, an index or a comparison
against bytes read from the file at run time.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import sprite_identity as sid
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.graphics import (CHARACTER_TABLE_REFERENCE_OFFSETS,
                                    load_actor_sprites)
from tools.webfoot.layout import AnchorId
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.rom import identify_rom
from tools.webfoot.write import apply_plan, plan_changes

ROM_BASE = 0x08000000
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The identity the runtime proof authored, and the donor whose own 32x32 frame
#: geometry every authored frame copies.
NEW_SPRITE_ID = 307
DONOR_SPRITE_ID = 10

#: The two object-palette entries SPRITE-NEW-RUNTIME-001 wrote, and that this
#: image's decoded actor-sprite graphics do not draw.
FREE_PALETTE_ENTRIES = (217, 236)

DONOR_HEADER_SIZE = 0x54


def _rom_path() -> Path:
    return Path(os.environ.get(
        "SPRITE_NEW_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


class _CachedCorpus:
    """The real corpus with its reference document built once for the module.

    `ActorSprites.reference_document` is a full rebuild - every anchor's
    relocation eligibility is re-decided against every reference - and it costs
    about a minute on the canonical image, so a module that planned a dozen
    derivatives without caching would spend a quarter of an hour rebuilding the
    same immutable document. The corpus never changes after construction, so the
    cached document cannot go stale.
    """

    def __init__(self, sprites) -> None:
        self._sprites = sprites
        self._document = None

    def reference_document(self):
        if self._document is None:
            self._document = self._sprites.reference_document()
        return self._document

    def registry_references(self):
        """The published inbound words, read from the cached document."""
        return tuple(reference for reference in self.reference_document().references
                     if reference.target == AnchorId(self.registry_identity))

    @property
    def profile(self):
        return self._sprites.profile

    @property
    def registry_identity(self) -> str:
        return self._sprites.registry_identity

    @property
    def layout(self):
        return self._sprites.layout

    @property
    def table_offset(self) -> int:
        return self._sprites.table_offset

    def palette_users(self, index: int):
        return self._sprites.palette_users(index)


@pytest.fixture(scope="module")
def corpus(canonical_bytes: bytes):
    """The real decoded corpus, walked once for the whole module."""
    path = _rom_path()
    identification = identify_rom(path, RomProfileCatalog.load("config/roms.yaml"))
    return _CachedCorpus(load_actor_sprites(canonical_bytes, identification))


def _donor_geometry(image: bytes, table: int) -> tuple:
    """The donor's own first frame geometry, read from the image."""
    structure = int.from_bytes(image[table:table + 4], "little") - ROM_BASE
    animation = int.from_bytes(
        image[structure + 0x54:structure + 0x58], "little") - ROM_BASE
    decoded = sg.decode_animation(image, animation)
    frame = sg.decode_frame(
        image, decoded.pointer_for(0, 0) - ROM_BASE)
    assert frame.piece_count == 1
    return frame.pieces[0]


def _sheet(image: bytes, palette, sprites, *, frames: int = 2,
           entries=None) -> sid.SourceSheet:
    """A direction-major sheet painted with the image's OWN palette entries.

    Cell ``c`` is solid in the display colour of palette entry
    ``entries[c]``, so the artwork packs back to a word the palette already holds
    and no entry is written. Nothing here is ROM-derived content: the pixels are a
    flat fill of a colour the palette itself names.
    """
    piece = _donor_geometry(image, sprites.table_offset)
    indices = entries or [1 + index for index in range(frames * sg.DIRECTION_COUNT)]
    pixels = bytearray()
    for cell in range(frames * sg.DIRECTION_COUNT):
        colour = sg.expand_bgr555(palette.raw[indices[cell]])
        pixels += bytes(colour) * (piece.dim_0 * piece.dim_1)
    return sid.SourceSheet(
        frames_per_direction=frames, cell_width=piece.dim_0,
        cell_height=piece.dim_1, pixels=bytes(pixels))


def _identity(*animations, free=()) -> sid.NewSpriteIdentity:
    return sid.NewSpriteIdentity(
        sprite_id=NEW_SPRITE_ID, donor_sprite_id=DONOR_SPRITE_ID,
        animations=tuple(animations), free_palette_entries=tuple(free))


def _plan(canonical_bytes, corpus, identity):
    return sid.plan_new_sprite_identity(canonical_bytes, None, identity,
                                        sprites=corpus)


def _apply(canonical_bytes, corpus, materialization) -> bytes:
    profile = corpus.profile
    generated = profile.generated_expansion.generated_image(
        len(canonical_bytes),
        tuple(a.allocated_range for a in materialization.generated_allocations))
    plan = plan_changes(
        canonical_bytes, materialization.changes, profile_id=profile.id,
        base_sha256=profile.sha256, relocations=materialization.relocations,
        generated_image=generated,
        generated_allocations=materialization.generated_allocations)
    return apply_plan(canonical_bytes, plan)


def _differing_offsets(image: bytes, output: bytes) -> list[int]:
    """Every canonical offset the derivative changed, without a byte-by-byte loop."""
    differing: list[int] = []
    window = 0x10000
    for start in range(0, len(image), window):
        left = image[start:start + window]
        right = output[start:start + window]
        if left != right:
            differing.extend(start + index for index in range(len(left))
                             if left[index] != right[index])
    return differing


def _assert_only_fields_changed(image: bytes, output: bytes, *fields) -> None:
    """No canonical byte outside these ``(start, size)`` fields may differ.

    A field that keeps one of its bytes - a repointed address whose high byte is
    unchanged - reports fewer differing bytes than it has, so the claim is stated
    in both directions: nothing outside the fields moved, and every field did move.
    """
    differing = _differing_offsets(image, output)
    inside = {offset + delta for offset, size in fields for delta in range(size)}
    assert not set(differing) - inside, sorted(set(differing) - inside)
    for offset, size in fields:
        assert any(offset <= value < offset + size for value in differing), hex(offset)


def _palette(canonical_bytes: bytes, corpus):
    return sg.decode_palette(
        canonical_bytes,
        corpus.layout.object_palette_address.to_file_offset(len(canonical_bytes)))


def _slots(image: bytes, materialization, piece, animation_slot=0):
    """Resolve the identity the way the engine's accessor would, end to end."""
    authored = materialization.identity
    entry = (authored.registry_range.start.value
             + 4 * (authored.sprite_id - sid.SPRITE_ID_FLOOR))
    structure = int.from_bytes(image[entry:entry + 4], "little") - ROM_BASE
    assert image[structure] == len(authored.animations)
    animation = int.from_bytes(
        image[structure + 0x54 + 4 * animation_slot:
              structure + 0x58 + 4 * animation_slot], "little") - ROM_BASE
    frame_count = int.from_bytes(image[animation:animation + 4], "little")
    found = []
    for slot in range(frame_count * sg.DIRECTION_COUNT):
        pointer = int.from_bytes(image[animation + 4 + 4 * slot:
                                       animation + 8 + 4 * slot], "little")
        frame = pointer - ROM_BASE
        assert int.from_bytes(image[frame:frame + 4], "little") == 1
        container = int.from_bytes(image[frame + 16:frame + 20], "little")
        decoded = sg.decode_graphic(image, container - ROM_BASE, piece.dim_0,
                                    piece.dim_1, colour_256=True)
        found.append((decoded.pixels, container))
    return found


# --- the registry ------------------------------------------------------------


@pytest.fixture(scope="module")
def stand_plan(canonical_bytes, corpus):
    """The default identity, planned and applied ONCE for the module.

    Planning this identity costs a full container encode per frame plus a write
    plan over a 16 MiB image, and five of the assertions below are about the same
    derivative; sharing one immutable result keeps the suite's runtime about the
    image rather than about repetition.
    """
    palette = _palette(canonical_bytes, corpus)
    result = _plan(canonical_bytes, corpus, _identity(
        sid.AnimationSource(name="stand",
                            sheet=_sheet(canonical_bytes, palette, corpus))))
    return result, _apply(canonical_bytes, corpus, result)


def test_the_canonical_registry_is_the_published_297_entry_one(canonical_bytes, corpus):
    """Positive control: the fixture's own assumptions about the image."""
    anchor = corpus.reference_document().anchor(AnchorId(corpus.registry_identity))
    assert corpus.layout.character_count == 297
    assert anchor.range.start.value == corpus.table_offset
    assert anchor.range.size == 297 * 4
    assert anchor.relocatable
    assert tuple(reference.source.value for reference in
                 corpus.registry_references()) == CHARACTER_TABLE_REFERENCE_OFFSETS


def test_the_published_words_are_the_whole_census_of_the_table_address(
        canonical_bytes, corpus):
    """The graph's words are also every word the image itself holds.

    The published pair is a measured census that the reference document re-checks
    against the image, so comparing the graph to that constant alone is circular.
    This scans the image for the table's address and requires the published set to
    be exactly what the scan finds: a word the graph did not publish would be a
    reader left pointing at the retired table.
    """
    needle = (ROM_BASE + corpus.table_offset).to_bytes(4, "little")
    aligned = []
    at = canonical_bytes.find(needle)
    while at != -1:
        if at % 4 == 0:
            aligned.append(at)
        at = canonical_bytes.find(needle, at + 1)
    assert aligned == sorted(CHARACTER_TABLE_REFERENCE_OFFSETS)
    published = tuple(reference.source.value for reference in
                      corpus.registry_references())
    assert sorted(published) == aligned


def test_the_planner_grows_the_registry_from_297_to_298(canonical_bytes, corpus,
                                                        stand_plan):
    result, output = stand_plan
    assert result.identity.registry_entries == 298
    assert result.identity.sprite_id == NEW_SPRITE_ID
    assert result.identity.registry_range.size == 298 * 4

    start = result.identity.registry_range.start.value
    canonical = canonical_bytes[corpus.table_offset:corpus.table_offset + 297 * 4]
    assert output[start:start + 297 * 4] == canonical
    assert int.from_bytes(output[start + 297 * 4:start + 298 * 4], "little") == \
        result.identity.structure_rom_address


def test_both_confirmed_words_are_repointed_and_they_are_the_published_pair(
        canonical_bytes, corpus, stand_plan):
    result, output = stand_plan
    rewrites = sorted(rewrite.reference.source.value
                      for rewrite in result.relocations[0].references)
    assert rewrites == sorted(CHARACTER_TABLE_REFERENCE_OFFSETS)

    for word in CHARACTER_TABLE_REFERENCE_OFFSETS:
        assert int.from_bytes(canonical_bytes[word:word + 4], "little") == \
            ROM_BASE + corpus.table_offset
        assert int.from_bytes(output[word:word + 4], "little") == \
            result.identity.registry_rom_address


def test_the_only_canonical_bytes_that_change_are_those_two_words(
        canonical_bytes, stand_plan):
    result, output = stand_plan
    assert result.identity.palette_entries == ()
    _assert_only_fields_changed(canonical_bytes, output,
                                *[(word, 4) for word in CHARACTER_TABLE_REFERENCE_OFFSETS])


def test_every_existing_character_structure_is_byte_identical(
        canonical_bytes, corpus, stand_plan):
    """No structure moves and none is rewritten: only its name in the table moves."""
    _result, output = stand_plan
    table = corpus.table_offset
    checked = 0
    for slot in range(corpus.layout.character_count):
        address = int.from_bytes(
            canonical_bytes[table + 4 * slot:table + 4 * slot + 4], "little")
        if not ROM_BASE <= address < ROM_BASE + len(canonical_bytes):
            continue
        offset = address - ROM_BASE
        assert output[offset:offset + DONOR_HEADER_SIZE] == \
            canonical_bytes[offset:offset + DONOR_HEADER_SIZE]
        checked += 1
    assert checked == corpus.layout.character_count


# --- the new identity --------------------------------------------------------


def test_the_new_identity_resolves_out_of_the_emitted_image(canonical_bytes, corpus):
    """Registry entry -> structure -> animation -> frame -> container, decoded."""
    palette = _palette(canonical_bytes, corpus)
    frames = 2
    result = _plan(canonical_bytes, corpus, _identity(
        sid.AnimationSource(name="stand",
                            sheet=_sheet(canonical_bytes, palette, corpus,
                                         frames=frames))))
    output = _apply(canonical_bytes, corpus, result)
    authored = result.identity
    assert authored.registry_rom_address > ROM_BASE + len(canonical_bytes)
    assert authored.structure_rom_address > ROM_BASE + len(canonical_bytes)
    assert authored.containers_range.start.value >= len(canonical_bytes)

    piece = _donor_geometry(canonical_bytes, corpus.table_offset)
    slots = _slots(output, result, piece)
    assert len(slots) == frames * sg.DIRECTION_COUNT
    for frame_index in range(frames):
        for direction in range(sg.DIRECTION_COUNT):
            pixels, _container = slots[frame_index * 4 + direction]
            sheet_cell = direction * frames + frame_index
            assert set(pixels) == {1 + sheet_cell}
            assert len(pixels) == piece.dim_0 * piece.dim_1
    assert len({container for _pixels, container in slots}) == frames * 4


def test_the_authored_structure_copies_the_donor_header_verbatim(
        canonical_bytes, corpus, stand_plan):
    result, output = stand_plan
    donor = int.from_bytes(
        canonical_bytes[corpus.table_offset:corpus.table_offset + 4], "little") \
        - ROM_BASE
    start = result.identity.structure_range.start.value
    authored = output[start:start + DONOR_HEADER_SIZE]
    donor_header = canonical_bytes[donor:donor + DONOR_HEADER_SIZE]
    assert authored[sid.STRUCTURE_COUNT_OFFSET] == 1
    assert authored[1:] == donor_header[1:]
    # The authored piece is the donor's own geometry, with our container.
    donor_frame = _donor_geometry(canonical_bytes, corpus.table_offset)
    slots = _slots(output, result, donor_frame)
    record = result.identity.animations[0].frames[0].record_range.start.value
    frame = output[record:record + 20]
    assert frame[4:8] == bytes([donor_frame.x & 0xFF, donor_frame.y & 0xFF,
                                donor_frame.dim_0, donor_frame.dim_1])
    assert int.from_bytes(frame[12:16], "little") == donor_frame.attributes
    assert int.from_bytes(frame[16:20], "little") == slots[0][1]


# --- colour ------------------------------------------------------------------


def test_a_colour_the_palette_lacks_takes_a_requested_free_entry(
        canonical_bytes, corpus):
    palette = _palette(canonical_bytes, corpus)
    # The entry's effective colour is its low 15 bits: bit 15 is not part of a
    # GBA palette colour, and one canonical entry carries it.
    held = {word & 0x7FFF for word in palette.raw[1:]}
    absent = next(word for word in range(1, 0x8000) if word not in held)
    colour = sg.expand_bgr555(absent)
    assert sg.pack_gba_colour(*colour) == absent
    for index in FREE_PALETTE_ENTRIES:
        assert corpus.palette_users(index) == ()

    piece = _donor_geometry(canonical_bytes, corpus.table_offset)
    sheet = sid.SourceSheet(
        frames_per_direction=1, cell_width=piece.dim_0, cell_height=piece.dim_1,
        pixels=bytes(colour) * (piece.dim_0 * piece.dim_1 * sg.DIRECTION_COUNT))
    result = _plan(canonical_bytes, corpus, _identity(
        sid.AnimationSource(name="stand", sheet=sheet),
        free=FREE_PALETTE_ENTRIES))
    assert len(result.identity.palette_entries) == 1
    entry = result.identity.palette_entries[0]
    assert entry.index in FREE_PALETTE_ENTRIES
    assert entry.word == absent
    assert entry.colour == colour
    assert entry.previous_word == palette.raw[entry.index]

    output = _apply(canonical_bytes, corpus, result)
    fields = [(word, 4) for word in CHARACTER_TABLE_REFERENCE_OFFSETS]
    fields.append((entry.file_offset, 2))
    _assert_only_fields_changed(canonical_bytes, output, *fields)
    assert int.from_bytes(output[entry.file_offset:entry.file_offset + 2],
                          "little") == absent
    assert entry.file_offset == \
        corpus.layout.object_palette_address.to_file_offset(len(canonical_bytes)) \
        + 2 * entry.index
    assert _slots(output, result, piece)[0][0] == bytes([entry.index]) * (
        piece.dim_0 * piece.dim_1)


def test_a_free_entry_the_corpus_draws_is_refused(canonical_bytes, corpus):
    drawn = next(index for index in range(1, sg.PALETTE_ENTRIES)
                 if corpus.palette_users(index))
    palette = _palette(canonical_bytes, corpus)
    with pytest.raises(sid.SpriteIdentityError, match="draw it"):
        _plan(canonical_bytes, corpus, _identity(
            sid.AnimationSource(name="stand",
                                sheet=_sheet(canonical_bytes, palette, corpus)),
            free=(drawn,)))


# --- determinism and safety --------------------------------------------------


def test_planning_the_canonical_image_twice_is_identical(canonical_bytes, corpus):
    palette = _palette(canonical_bytes, corpus)
    identity = _identity(
        sid.AnimationSource(name="stand",
                            sheet=_sheet(canonical_bytes, palette, corpus)),
        sid.AnimationSource(name="walk",
                            sheet=_sheet(canonical_bytes, palette, corpus, frames=4,
                                         entries=[1 + index for index in range(16)])))
    first = _plan(canonical_bytes, corpus, identity)
    second = _plan(canonical_bytes, corpus, identity)
    assert first.changes == second.changes
    assert first.reserved == second.reserved
    assert first.generated_allocations == second.generated_allocations
    assert first.relocations == second.relocations
    assert first.identity.to_json() == second.identity.to_json()
    assert _apply(canonical_bytes, corpus, first) == \
        _apply(canonical_bytes, corpus, second)


def test_the_identity_carries_four_facings_per_frame(canonical_bytes, corpus):
    """Every direction slot names a real frame, because the engine null-tests none."""
    palette = _palette(canonical_bytes, corpus)
    result = _plan(canonical_bytes, corpus, _identity(
        sid.AnimationSource(name="walk",
                            sheet=_sheet(canonical_bytes, palette, corpus, frames=4,
                                         entries=[1 + index for index in range(16)]))))
    output = _apply(canonical_bytes, corpus, result)
    animation = int.from_bytes(
        output[result.identity.animations[0].animation_range.start.value:
               result.identity.animations[0].animation_range.start.value + 4],
        "little")
    assert animation == 4
    piece = _donor_geometry(canonical_bytes, corpus.table_offset)
    assert all(container != 0 for _pixels, container in _slots(output, result, piece))


def test_the_canonical_file_is_only_read(canonical_bytes, corpus):
    before = hashlib.sha256(_rom_path().read_bytes()).hexdigest()
    palette = _palette(canonical_bytes, corpus)
    _apply(canonical_bytes, corpus, _plan(canonical_bytes, corpus, _identity(
        sid.AnimationSource(name="stand",
                            sheet=_sheet(canonical_bytes, palette, corpus)))))
    assert hashlib.sha256(_rom_path().read_bytes()).hexdigest() == before
    assert before == CANONICAL_SHA256
