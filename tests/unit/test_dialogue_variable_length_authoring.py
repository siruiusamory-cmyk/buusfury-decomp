"""DIALOGUE-VARIABLE-LENGTH-001: variable-length dialogue replacement.

The production operation this file pins is "replace this existing dialogue record
with this text", where the text may encode to a different number of decoded bytes
than the retail record. That needs three things to hold at once, and each gets
its own set of tests here:

* **the durable handle is authored**, not frozen - a new length (and any shifted
  start) is compiled through the one encoder, and an unencodable request is
  refused rather than truncated;
* **the decoded container is re-laid out deterministically** - the replacement is
  spliced into the record's own span, every record at or after its old end is
  shifted, and every record that did NOT move still decodes to exactly its own
  bytes;
* **every true reference is repointed and no unrelated word is touched** - the
  reference inventory is the engine's own handle-carrying structure, so a word
  that merely equals a superseded handle is left alone.

The fixture is synthetic: a zero-filled image large enough to hold the real
container table and record pool, one packed container, and the record objects
that name its spans. No commercial bytes are used or committed.

The last block runs the ticket's five mutations M1-M5 as permanent tests: each
one breaks a specific production property and asserts the property's own test
notices. They are named `test_mN_...` so the mutation run can select exactly the
node it expects to fail.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from tools.webfoot.allocation import InsufficientSpaceError
from tools.webfoot.binary import FileOffset
from tools.webfoot.compressed_dialogue import (CompressedDialogueError,
                                                CompressedDialogueTarget,
                                                DialogueLayout, DialogueRecord,
                                                dialogue_record_inventory,
                                                materialize_dialogues, read_container_layout,
                                                relayout_for_length, validate_container_layout,
                                                validate_relayout)
from tools.webfoot.formats.webfoot_lz import DEFAULT_MAX_OUTPUT, pack
from tools.webfoot.handles import DialogueHandle, HandleError, pack_handle
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.write import ByteChange, ChangeValidationError, plan_changes


PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

# --- the synthetic layout ----------------------------------------------------
#: The measured container table's file offset and the target's selector, so the
#: container-table arithmetic under test is the production arithmetic.
TABLE_OFFSET = 0x7B5B64
SELECTOR = 1
TABLE_SLOT = TABLE_OFFSET + SELECTOR * 4
NEXT_SLOT = TABLE_SLOT + 4
CONTAINER_OFFSET = 0x1000
IMAGE_SIZE = TABLE_SLOT + 8
#: The event-resource record pool, where the real image keeps its handle
#: carriers. Inside IMAGE_SIZE, so the inventory scan sees the fixture.
POOL = 0x77C5A4

ORIGINAL_TEXT = "Good luck, Goku!"
LONGER_TEXT = "Hot take: SSJ3 is the worst form imo"
SHORTER_TEXT = "Hi!"
DECODED_SIZE = 0x292
TARGET_START = 0x132
TARGET_LENGTH = 0x20
#: A word that equals the retail handle but is NOT a record: the byte at +0x02
#: of the word before it is 0xAA, so no engine dispatch reaches it.
STRAY_SITE = 0x3000

TARGET = CompressedDialogueTarget(
    "goku-greeting", SELECTOR, TABLE_OFFSET, 0x02002641, TARGET_START, TARGET_LENGTH,
    PROFILE_ID,
)

#: ``(site, selector, decoded start, decoded length)``. Sites are 8 bytes apart
#: because a record object is ``[word, handle]``: two sites four bytes apart
#: would have the second one's word overwrite the first one's handle. Two
#: records share start 0 and two share start 0x192 with different lengths,
#: because a start alone does not name one record in this container.
RECORDS = (
    (POOL + 0x30, SELECTOR, 0x000, 0x132),
    (POOL + 0x38, SELECTOR, 0x000, 0x040),
    (POOL + 0x40, SELECTOR, TARGET_START, TARGET_LENGTH),
    (POOL + 0x48, SELECTOR, TARGET_START, TARGET_LENGTH),
    (POOL + 0x50, SELECTOR, TARGET_START, TARGET_LENGTH),
    (POOL + 0x58, SELECTOR, 0x152, 0x040),
    (POOL + 0x60, SELECTOR, 0x192, 0x040),
    (POOL + 0x68, SELECTOR, 0x192, 0x100),
    (POOL + 0x70, SELECTOR, 0x252, 0x040),
)


@pytest.fixture(scope="module")
def profile():
    return the_profile()


def the_profile():
    """The verified profile, cached: helpers below are not fixtures."""
    global _PROFILE
    if _PROFILE is None:
        catalog = RomProfileCatalog.load("config/roms.yaml")
        _PROFILE = next(item for item in catalog.profiles if item.id == PROFILE_ID)
    return _PROFILE


_PROFILE = None


def reserve_canonical_free(profile) -> tuple[RomRange, ...]:
    """Reserve the profile's canonical free window, so allocation must expand."""
    return tuple(RomRange(FileOffset(region.range.start.value), region.range.size)
                 for region in profile.free_regions)


def decoded_body() -> bytes:
    """Non-uniform filler, so a suppressed shift really changes a record's bytes.

    A constant fill would let a record that was NOT shifted still "decode to its
    own bytes", because every position holds the same byte - which is exactly the
    M3 mutation's escape route.
    """
    body = bytearray((index * 37 + 11) % 256 for index in range(DECODED_SIZE))
    body[TARGET_START:TARGET_START + TARGET_LENGTH] = ORIGINAL_TEXT.encode("utf-16le")
    return bytes(body)


def build_image(*, allocation: int | None = None) -> bytes:
    """A synthetic image: one packed container, its table words, its records."""
    container = pack(decoded_body())
    image = bytearray(IMAGE_SIZE)
    image[CONTAINER_OFFSET:CONTAINER_OFFSET + len(container)] = container
    image[TABLE_SLOT:TABLE_SLOT + 4] = (0x08000000 + CONTAINER_OFFSET).to_bytes(4, "little")
    span = len(container) if allocation is None else allocation
    image[NEXT_SLOT:NEXT_SLOT + 4] = (0x08000000 + CONTAINER_OFFSET + span).to_bytes(4, "little")
    for site, selector, start, length in RECORDS:
        image[site - 4:site] = bytes((0x01, 0x00, 0x05, 0x68))
        image[site:site + 4] = pack_handle(selector, start, length).to_bytes(4, "little")
    # The unrelated equal word: byte +0x02 of the preceding word is 0xAA, so no
    # dispatch reaches it and no record covers it.
    image[STRAY_SITE - 2] = 0xAA
    image[STRAY_SITE:STRAY_SITE + 4] = TARGET.packed_handle.to_bytes(4, "little")
    return bytes(image)


def layout_of(image: bytes) -> DialogueLayout:
    return read_container_layout(image, the_profile(), TARGET)


def relayout_of(image: bytes, text: str = LONGER_TEXT):
    return relayout_for_length(layout_of(image), TARGET, text.encode("utf-16le"),
                               f"compressed-dialogue:{TARGET.name}", image)


def apply_changes(image: bytes, changes) -> bytes:
    out = bytearray(image)
    for change in changes:
        out[change.offset:change.end] = change.new
    return bytes(out)


# --- the container layout is read, not guessed --------------------------------


def test_the_inventory_is_the_engine_structure_not_a_value_pattern():
    image = build_image()
    records = dialogue_record_inventory(image, SELECTOR, DECODED_SIZE)
    spans = sorted((r.handle.decoded_start, r.handle.decoded_length) for r in records)
    for _site, selector, start, length in RECORDS:
        assert (start, length) in spans, (selector, start, length)
    # The stray word equals the retail handle but is not a record.
    carriers = {site for record in records for site in record.sites}
    assert STRAY_SITE not in carriers
    target = next(r for r in records
                  if (r.handle.decoded_start, r.handle.decoded_length)
                  == (TARGET_START, TARGET_LENGTH))
    assert set(target.sites) == {POOL + 0x40, POOL + 0x48, POOL + 0x50}


def test_a_start_alone_does_not_name_one_record():
    layout = layout_of(build_image())
    assert len(layout.records_starting_at(0x192)) == 2
    assert layout.sole_record_starting_at(0x192) is None
    assert layout.record_with_span(0x192, 0x40) is not None
    assert layout.record_with_span(0x192, 0x40) != layout.record_with_span(0x192, 0x100)
    assert layout.sole_record_starting_at(TARGET_START) is not None


# --- the authoring operation --------------------------------------------------


def test_growing_a_record_shifts_only_what_follows_it():
    image = build_image()
    relayout = relayout_of(image)

    assert relayout.edited.handle == DialogueHandle(SELECTOR, TARGET_START, TARGET_LENGTH)
    assert relayout.new_handle.decoded_length == len(LONGER_TEXT.encode("utf-16le"))
    assert relayout.new_handle.decoded_start == TARGET_START
    assert relayout.decoded_delta == 40
    assert len(relayout.decoded) == DECODED_SIZE + 40
    # Records entirely before the edited span are untouched, and exactly the
    # records at or after its old end are displaced.
    moved_starts = sorted(old.decoded_start for old, _new in relayout.moved)
    assert 0x000 not in moved_starts
    assert moved_starts == [0x152, 0x192, 0x192, 0x252]
    for old, new in relayout.moved:
        assert new.decoded_start == old.decoded_start + 40
        assert new.decoded_length == old.decoded_length


def test_shrinking_a_record_shifts_the_same_records_backwards():
    relayout = relayout_of(build_image(), SHORTER_TEXT)
    assert relayout.decoded_delta == len(SHORTER_TEXT.encode("utf-16le")) - TARGET_LENGTH
    assert relayout.decoded_delta < 0
    for old, new in relayout.moved:
        assert new.decoded_start == old.decoded_start + relayout.decoded_delta
    validate_relayout(relayout, build_image())


def test_the_same_length_replacement_is_still_a_no_op_for_identity():
    """Section 26: the equal-length edit must not regress.

    Nothing moves, no handle changes, and therefore no ROM word is rewritten -
    the payload-only behaviour the fixed-length path already had.
    """
    image = build_image()
    relayout = relayout_of(image, ORIGINAL_TEXT)
    assert relayout.decoded_delta == 0
    assert relayout.moved == ()
    assert relayout.reference_changes == ()
    assert relayout.decoded == decoded_body()
    assert relayout.new_handle == relayout.edited.handle


def test_every_carrier_of_a_changed_record_is_rewritten_once():
    image = build_image()
    relayout = relayout_of(image)
    offsets = [change.offset for change in relayout.reference_changes]
    assert len(offsets) == len(set(offsets)), "a site was written twice"
    for site in relayout.edited.sites:
        assert site in offsets
    # Every displaced record's own sites are present too.
    expected = {site for record in layout_of(image).records
                if record.handle.decoded_start >= 0x152
                for site in record.sites}
    assert expected <= set(offsets)


def test_unedited_records_still_decode_to_their_own_bytes():
    image = build_image()
    layout = layout_of(image)
    relayout = relayout_of(image)
    validate_relayout(relayout, image)
    renamed = dict(relayout.moved)
    for record in layout.records:
        if record.handle == relayout.edited.handle:
            continue
        new = renamed.get(record.handle, record.handle)
        before = layout.decoded[record.handle.decoded_start:record.handle.decoded_end]
        after = relayout.decoded[new.decoded_start:new.decoded_end]
        assert before == after
    authored = relayout.decoded[TARGET_START:TARGET_START + 72]
    assert authored.decode("utf-16le") == LONGER_TEXT


# --- negative cases the format actually imposes -------------------------------


def test_an_empty_replacement_is_refused():
    with pytest.raises(CompressedDialogueError, match="must not be empty"):
        relayout_of(build_image(), "")


def test_a_replacement_wider_than_the_length_field_is_refused():
    with pytest.raises(CompressedDialogueError, match="durable handle"):
        relayout_of(build_image(), "a" * 2048)      # 4096 encoded bytes > 4094


def test_a_container_whose_rebuild_would_exceed_the_decoder_limit_is_refused():
    """The toolkit's own container limit binds long before the field's maximum.

    A replacement's decoded length is bounded by ``HANDLE_LENGTH_MAX_BYTES``
    (4094) in the field, but the container it lands in is bounded by the
    decoder's 64 KiB safety limit - and a retail dialogue container already
    decodes to within 62 bytes of that. The refusal names the limit rather than
    truncating the container.
    """
    near = DEFAULT_MAX_OUTPUT - 4
    decoded = b"B" * (near + 2)
    record = DialogueRecord(DialogueHandle(SELECTOR, near, 2), (0x1000,))
    layout = DialogueLayout(SELECTOR, 0, 0, decoded, (record,))
    with pytest.raises(CompressedDialogueError, match="container decoder limit"):
        relayout_for_length(layout, replace(TARGET, decoded_start=near, decoded_length=2),
                            b"Z" * 72, "owner", bytes(0x2000))


def test_a_record_that_crosses_the_edited_span_is_refused():
    """A straddling record would have to change content, and nothing defines how."""
    image = bytearray(build_image())
    crossing = POOL + 0x80
    image[crossing - 4:crossing] = bytes((0x01, 0x00, 0x05, 0x68))
    image[crossing:crossing + 4] = pack_handle(SELECTOR, 0x100, 0x100).to_bytes(4, "little")
    with pytest.raises(CompressedDialogueError, match="cross the edited span"):
        relayout_of(bytes(image))


def test_the_shifted_start_field_cannot_overflow_while_the_decoder_limit_holds():
    """Two independent bounds, and the decoder's is the stricter one.

    A displaced record's new start is ``old start + delta``, and the container
    may only decode to ``DEFAULT_MAX_OUTPUT`` bytes, so with the production limit
    in force ``new start <= 65536 - length <= 65534`` - inside the 15-bit field.
    The field guard is therefore defence in depth rather than a live limit, and
    this test states the relation and then exercises the guard directly by
    lifting the container limit for one call.
    """
    from tools.webfoot import compressed_dialogue as dialogue
    from tools.webfoot.handles import HANDLE_START_MAX_BYTES, HANDLE_UNIT_BYTES

    assert dialogue.DEFAULT_MAX_OUTPUT <= HANDLE_START_MAX_BYTES + HANDLE_UNIT_BYTES

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(dialogue, "DEFAULT_MAX_OUTPUT", 1 << 20)
    try:
        edited_start = 0x1000
        later = HANDLE_START_MAX_BYTES - 14          # +70 overflows the field
        records = (
            DialogueRecord(DialogueHandle(SELECTOR, edited_start, 2), (0x1000,)),
            DialogueRecord(DialogueHandle(SELECTOR, later, 4), (0x1008,)),
        )
        layout = DialogueLayout(SELECTOR, 0, 0, b"A" * (later + 4), records)
        with pytest.raises(CompressedDialogueError, match="overflows the durable handle"):
            dialogue.relayout_for_length(
                layout, replace(TARGET, decoded_start=edited_start, decoded_length=2),
                b"Z" * 72, "owner", bytes(0x2000))
    finally:
        monkeypatch.undo()


def test_a_missing_selector_is_refused(profile):
    image = bytearray(build_image())
    image[TABLE_SLOT:TABLE_SLOT + 4] = (0x03004A68).to_bytes(4, "little")
    with pytest.raises(CompressedDialogueError):
        read_container_layout(bytes(image), profile, TARGET)


def test_a_container_with_no_records_is_refused():
    layout = DialogueLayout(SELECTOR, CONTAINER_OFFSET, CONTAINER_OFFSET + 16, b"A" * 64, ())
    with pytest.raises(CompressedDialogueError, match="no handle-carrying record"):
        validate_container_layout(layout)


def test_a_record_outside_its_container_is_refused():
    record = dialogue_record_inventory(build_image(), SELECTOR, DECODED_SIZE)[0]
    layout = DialogueLayout(SELECTOR, CONTAINER_OFFSET, CONTAINER_OFFSET + 16, b"A" * 8,
                            (record,))
    with pytest.raises(CompressedDialogueError, match="outside the"):
        validate_container_layout(layout)


def test_a_record_naming_another_selector_is_refused():
    record = dialogue_record_inventory(build_image(), SELECTOR, DECODED_SIZE)[0]
    other = replace(record, handle=record.handle.replace(selector=2))
    layout = DialogueLayout(SELECTOR, CONTAINER_OFFSET, CONTAINER_OFFSET + 16,
                            b"A" * DECODED_SIZE, (other,))
    with pytest.raises(CompressedDialogueError, match="names selector"):
        validate_container_layout(layout)


# --- the production path: allocation, provenance, and the plan ----------------


def test_a_payload_that_no_longer_fits_its_retail_allocation_uses_the_allocator(profile):
    image = build_image()
    build, _reserved, generated_image, provenance = materialize_dialogues(
        image, profile, {TARGET.name: LONGER_TEXT})
    result = build[0]
    assert len(result.payload) > result.old_allocation
    assert result.allocation is not None
    assert result.allocation.request.kind.value == "packed_stream"
    assert result.dialogue_edit is not None
    assert result.dialogue_edit.new_handle == result.relayout.new_handle.encode()
    assert result.dialogue_edit.old_handle == TARGET.packed_handle
    assert result.dialogue_edit.old_decoded_length == TARGET_LENGTH
    assert result.dialogue_edit.new_decoded_length == 72
    assert result.dialogue_edit.old_decoded_start == result.dialogue_edit.new_decoded_start
    assert result.dialogue_edit.reference_site_count == len(
        result.relayout.reference_changes)
    if result.allocation.is_expanded:
        assert provenance and generated_image is not None


def test_the_expanded_branch_records_allocator_provenance(profile):
    image = build_image()
    reserved = reserve_canonical_free(profile)
    builds, _taken, generated_image, provenance = materialize_dialogues(
        image, profile, {TARGET.name: LONGER_TEXT}, reserved=reserved)
    build = builds[0]
    assert build.allocation is not None and build.allocation.is_expanded
    assert build.generated_allocation is not None
    assert provenance == (build.generated_allocation,)
    assert generated_image is not None
    assert build.dialogue_edit.pointer_moved is True
    assert build.dialogue_edit.container_pointer_address == build.allocation.rom_address


def test_the_target_record_must_be_the_measured_retail_span(profile):
    """An image that is not the measured base is refused, not patched."""
    mismatch = replace(TARGET, decoded_length=0x30)
    with pytest.raises(CompressedDialogueError, match="no record spanning"):
        relayout_for_length(layout_of(build_image()), mismatch,
                            LONGER_TEXT.encode("utf-16le"), "owner", build_image())


# --- the ticket's five mutations, kept as permanent tests ---------------------


def test_m1_keeping_the_old_decoded_length_is_refused():
    """M1: encode the old 32-byte length after the 72-byte replacement.

    The splice is right and the handle is wrong, so the record would name only
    the first 32 bytes of the authored line - a truncated display the old
    exact-length rule was never going to catch, because it is the new contract's
    job to author the length and the layout proof's job to check it.
    """
    image = build_image()
    relayout = relayout_of(image)
    mutated = replace(relayout, new_handle=relayout.edited.handle)
    with pytest.raises(CompressedDialogueError, match="does not carry the"):
        validate_relayout(mutated, image)


def test_m2_skipping_one_reference_update_is_refused():
    """M2: drop one required site and the consistency proof must notice."""
    image = build_image()
    relayout = relayout_of(image)
    dropped = relayout.reference_changes[:-1]
    mutation = replace(relayout, reference_changes=dropped)
    with pytest.raises(CompressedDialogueError, match="reference update is incomplete"):
        validate_relayout(mutation, image)


def test_m3_suppressing_one_downstream_shift_is_refused():
    """M3: leave one displaced record's start alone and its bytes no longer match.

    The layout genuinely requires the shift - 410 of selector 1's 446 adjacent
    record pairs are consecutive on the real image - so a suppressed update makes
    that record decode into the middle of another.
    """
    image = build_image()
    relayout = relayout_of(image)
    assert relayout.moved, "this fixture must have downstream records to shift"
    victim, _new = relayout.moved[-1]
    victim_sites = {site for record in layout_of(image).records
                    if record.handle == victim for site in record.sites}
    mutation = replace(
        relayout,
        moved=relayout.moved[:-1],
        reference_changes=tuple(change for change in relayout.reference_changes
                                if change.offset not in victim_sites),
    )
    with pytest.raises(CompressedDialogueError, match="no longer decodes to its own"):
        validate_relayout(mutation, image)


def test_m4_a_global_word_replace_would_touch_an_unrelated_equal_word():
    """M4: a value-pattern replace reaches words the engine never reads.

    The stray word here is byte-identical to the retail handle. The production
    edit leaves it alone because no record object carries it; a global replace
    would rewrite it, and this test would fail.
    """
    image = build_image()
    relayout = relayout_of(image)
    assert int.from_bytes(image[STRAY_SITE:STRAY_SITE + 4], "little") == TARGET.packed_handle
    offsets = {change.offset for change in relayout.reference_changes}
    assert STRAY_SITE not in offsets
    assert STRAY_SITE not in relayout.edited.sites
    # A global replace of this value would have produced a different edit set.
    global_offsets = [index for index in range(0, len(image) - 4, 4)
                      if int.from_bytes(image[index:index + 4], "little")
                      == TARGET.packed_handle]
    assert STRAY_SITE in global_offsets
    assert set(global_offsets) != offsets
    after = apply_changes(image, relayout.reference_changes)
    assert after[STRAY_SITE:STRAY_SITE + 4] == image[STRAY_SITE:STRAY_SITE + 4]


def test_m5_a_hand_placed_growing_payload_is_refused_without_allocator_provenance(profile):
    """M5: bypass the allocator and the write transaction refuses the plan.

    Two ways to try it, and both fail closed: writing past the base at a chosen
    address with no generated image at all, and writing inside a generated image
    that no allocator-issued provenance record owns.
    """
    from tools.webfoot.write import GeneratedImage

    image = build_image()
    builds, _taken, _generated_image, _provenance = materialize_dialogues(
        image, profile, {TARGET.name: LONGER_TEXT}, reserved=reserve_canonical_free(profile))
    payload = builds[0].payload
    owner = f"compressed-dialogue:{TARGET.name}"

    # (1) Past the end of the base with no generated-image policy at all.
    manual = ByteChange(len(image), bytes(len(payload)), payload, owner,
                        "manually placed payload")
    with pytest.raises(ChangeValidationError, match="extends past"):
        plan_changes(image, [manual], profile_id=profile.id, base_sha256=profile.sha256)

    # (2) Inside a declared expansion that no allocation record owns. The image's
    #     span list is left consistent with an empty provenance list, so the gate
    #     under test is authorization rather than span agreement.
    expansion = GeneratedImage(
        output_size=len(image) + len(payload), padding_byte=0x00,
        expansion_range=RomRange(FileOffset(len(image)), len(payload)),
        expansion_evidence="M5 control: a hand-declared expansion")
    with pytest.raises(ChangeValidationError, match="not authorized"):
        plan_changes(image, [manual], profile_id=profile.id, base_sha256=profile.sha256,
                     generated_image=expansion, generated_allocations=())


def test_the_production_code_names_no_destination_literal():
    """The destination is the allocator's, so there is no address to hard-code."""
    from pathlib import Path

    source = Path("tools/webfoot/compressed_dialogue.py").read_text(encoding="utf-8")
    for literal in ("0x800000", "0x00800000", "0x08800000", "8388608", "16777216"):
        assert literal not in source, literal


def test_an_unallocatable_growing_payload_still_fails_cleanly(profile):
    """With every declared region reserved, allocation refuses rather than guesses."""
    expansion = profile.generated_expansion
    expansion_region = expansion.free_region(profile.size).range
    reserved = tuple(RomRange(FileOffset(region.range.start.value), region.range.size)
                     for region in profile.free_regions)
    reserved += (RomRange(FileOffset(expansion_region.start.value), expansion_region.size),)
    with pytest.raises(InsufficientSpaceError):
        materialize_dialogues(build_image(), profile, {TARGET.name: LONGER_TEXT},
                              reserved=reserved)


def test_an_odd_decoded_length_cannot_be_encoded():
    """Halfword units are a format fact, so an odd byte count is not a handle."""
    with pytest.raises(HandleError):
        pack_handle(SELECTOR, TARGET_START, 3)
