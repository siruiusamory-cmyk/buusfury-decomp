"""TOOLKIT-036 proofs that an authored string longer than its body relocates.

TOOLKIT-004's `test_text_relocation.py` proved the relocator itself moves a
string, on a fixture wired straight into `plan_relocation`. This file proves the
WIRING: the same growth reached through `webfoot.text`, the layer an author's
`text/strings.toml` actually arrives at, deciding storage on its own from the
measured image.

No ROM bytes appear here. The fixture is a miniature of the real topology - a
pointer table whose slots are the only inbound references to an exhaustively
tiled pool - because that topology is what the ownership rule measures. The
canonical numbers it stands in for are asserted in the ROM-gated integration
suite; a unit test that needed the ROM would not run at all in CI.

Two things are deliberately proven by SHAPE rather than by index:

* the five canonical bodies a second aligned word also names are refused because
  the fixture plants that same second word, not because any index is listed;
* the author supplies only text. There is no flag that asks for relocation and
  no field that supplies an address.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.helpers import hashes_for, profile_for
from tools.webfoot import text as T
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.formats.text_tables import TextCodecError, TextIdentity
from tools.webfoot.layout import RELOCATION_ELIGIBLE_KINDS
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.write import OverlappingChangeError, apply_plan


#: The fixture's geometry. The pool sits below the table exactly as the canonical
#: one does, and the free region is far above both.
IMAGE_SIZE = 0x8000
POOL = 0x1000
TABLE = 0x2000
FREE = 0x4000
FREE_SIZE = 0x100

#: Three strings, tiled. The middle one grows: moving a body that is neither
#: first nor last is what proves its neighbours are left alone.
STRINGS = ("Start", "Match 2 Fight!", "Options")
GROW = 1

#: Longer than the middle body's 30 bytes, short enough for the free region.
LONGER = "Round 2! Show me your real power!"


def _image(*, second_word_at: int | None = None) -> tuple[bytes, tuple[int, ...]]:
    """The fixture image, optionally carrying a second aligned word at a body.

    `second_word_at` plants a word-aligned u32 elsewhere in the image holding the
    middle body's address. That is the exact measured shape of the five canonical
    coincidences, and it is what the ownership rule refuses - the test never
    names an index.
    """
    data = bytearray(IMAGE_SIZE)
    data[0xA0:0xAC] = b"SYNTHETIC   "
    data[0xAC:0xB0] = b"TEST"
    data[0xB0:0xB2] = b"01"
    data[0xB2] = 0x96
    data[0xBD] = (-(sum(data[0xA0:0xBD]) + 0x19)) & 255

    offsets = []
    cursor = POOL
    for text in STRINGS:
        encoded = tt.encode_string(text)
        data[cursor : cursor + len(encoded)] = encoded
        offsets.append(cursor)
        cursor += len(encoded)
    pool_end = cursor

    for index, offset in enumerate(offsets):
        slot = TABLE + index * 4
        data[slot : slot + 4] = tt.encode_pointer(offset)

    if second_word_at is not None:
        assert second_word_at % 4 == 0
        data[second_word_at : second_word_at + 4] = tt.encode_pointer(offsets[GROW])

    return bytes(data), tuple(offsets), pool_end


def _profile(data: bytes, *, relocatable: bool = True, free: bool = True):
    _, _, pool_end = _image()
    return profile_for(
        data,
        tables={
            "text_strings": {
                "pointer_table_address": TABLE + tt.GBA_ROM_BASE,
                "count": len(STRINGS),
                "pool_address": POOL + tt.GBA_ROM_BASE,
                "pool_size": pool_end - POOL,
                "encoding": "utf16le_nul_terminated",
                "alignment": 2,
                "relocatable": relocatable,
                "evidence": "synthetic fixture construction; no game claim",
            }
        },
        free_regions=(
            [
                {
                    "file_offset": FREE,
                    "size": FREE_SIZE,
                    "status": "CONFIRMED",
                    "evidence": "synthetic fixture construction; no game claim",
                }
            ]
            if free
            else []
        ),
    )


def _strings(*, second_word_at=None, relocatable=True, free=True, image=None):
    """A `TextStrings` over the fixture, loaded through the production reader.

    Built directly rather than through `load_text_strings`, which requires a
    packaged capability contract no synthetic profile can satisfy. Everything
    below the identity gate is the production path: the production enumerator
    reads the pool, the production census decides ownership, and the production
    relocator plans every move.
    """
    data, _, pool_end = _image(second_word_at=second_word_at)
    if image is not None:
        data = image
    profile = _profile(data, relocatable=relocatable, free=free)
    table = profile.text_strings
    codec = T._codec_for(table)
    writable = T._writable_regions(profile)
    vacated = T._vacated_spans(data, table, codec, TABLE, POOL, pool_end)
    entries = tuple(
        T.TextEntry(
            identity=TextIdentity(raw.index),
            text=raw.text,
            location=T.TextLocation(
                index=raw.index,
                file_offset=raw.offset,
                allocation=raw.size,
                pointer_offset=TABLE + raw.index * codec.pointer_size,
            ),
            original_bytes=data[raw.offset : raw.offset + raw.size],
        )
        for raw in codec.enumerate_pool(data, table, TABLE, POOL, pool_end,
                                        vacated, writable)
    )
    # Only the base hash is read below the capability gate, and a synthetic
    # profile cannot satisfy the packaged contract that gate requires.
    strings = T.TextStrings(
        identification=SimpleNamespace(hashes=hashes_for(data)),
        profile=profile,
        entries=entries,
        codec=codec,
    )
    strings._base_bytes = data
    if table.relocatable:
        strings._owned = T._owned_entries(data, entries, codec)
    return strings


def _pointer(image: bytes, index: int) -> int:
    slot = TABLE + index * 4
    return int.from_bytes(image[slot : slot + 4], "little") - tt.GBA_ROM_BASE


# --- SC6: the in-place path is untouched ---------------------------------


def test_text_that_fits_is_still_written_in_place():
    """The fits-in-place path must not have become a relocation.

    Asserted on the CHANGE, not merely on the resulting bytes: a relocation that
    happened to land on the original address would produce the same image, and
    this test would pass while the behaviour had changed completely.
    """
    strings = _strings()
    strings.set_text(TextIdentity(GROW), "Fight!")
    assert strings._relocating == {}
    assert strings.relocations() == ()

    change, = [c for c in strings.plan().effective_changes]
    assert change.offset == POOL + len(tt.encode_string(STRINGS[0]))
    assert change.size == len(tt.encode_string(STRINGS[GROW]))
    assert change.owner == "text:0001"


def test_a_shorter_replacement_is_still_padded_in_place():
    strings = _strings()
    strings.set_text(TextIdentity(GROW), "Go")
    image = apply_plan(strings.base_bytes, strings.plan())
    offset = _pointer(image, GROW)
    assert offset == _pointer(strings.base_bytes, GROW)
    assert tt.decode_string(image, offset)[0] == "Go"


# --- SC9: growth relocates through the production path -------------------


def test_text_longer_than_its_body_is_relocated_into_declared_free_space():
    strings = _strings()
    strings.set_text(TextIdentity(GROW), LONGER)

    provenance, = strings.relocations()
    assert provenance.anchor == "text:0001"
    assert provenance.old_range.size == len(tt.encode_string(STRINGS[GROW]))
    assert FREE <= provenance.new_range.start.value
    assert provenance.new_range.end <= FREE + FREE_SIZE
    assert provenance.new_range.size == len(tt.encode_string(LONGER))


def test_the_relocated_body_decodes_at_its_new_address():
    strings = _strings()
    strings.set_text(TextIdentity(GROW), LONGER)
    image = apply_plan(strings.base_bytes, strings.plan())

    assert tt.decode_string(image, _pointer(image, GROW))[0] == LONGER


def test_the_owning_table_slot_is_the_only_pointer_rewritten():
    strings = _strings()
    strings.set_text(TextIdentity(GROW), LONGER)
    image = apply_plan(strings.base_bytes, strings.plan())

    assert _pointer(image, GROW) >= FREE
    for index in (0, 2):
        assert _pointer(image, index) == _pointer(strings.base_bytes, index)
        assert tt.decode_string(image, _pointer(image, index))[0] == STRINGS[index]


def test_the_vacated_span_is_left_exactly_as_it_was():
    """Retiring, not clearing. The vacated bytes are what later PROVES the hole."""
    strings = _strings()
    original = strings.entry(TextIdentity(GROW)).location
    strings.set_text(TextIdentity(GROW), LONGER)
    image = apply_plan(strings.base_bytes, strings.plan())

    span = slice(original.file_offset, original.file_offset + original.allocation)
    assert image[span] == strings.base_bytes[span]


def test_allocation_is_deterministic_across_identical_builds():
    first = _strings()
    first.set_text(TextIdentity(GROW), LONGER)
    second = _strings()
    second.set_text(TextIdentity(GROW), LONGER)
    assert apply_plan(first.base_bytes, first.plan()) == apply_plan(
        second.base_bytes, second.plan()
    )


def test_the_source_image_is_never_mutated():
    strings = _strings()
    before = bytes(strings.base_bytes)
    strings.set_text(TextIdentity(GROW), LONGER)
    apply_plan(strings.base_bytes, strings.plan())
    assert strings.base_bytes == before


# --- SC9: the generated image reads back through the production reader ---


def test_a_generated_image_decodes_through_the_production_reader():
    """The whole point: the ROM the build emits is one this toolkit can read."""
    strings = _strings()
    strings.set_text(TextIdentity(GROW), LONGER)
    image = apply_plan(strings.base_bytes, strings.plan())

    reread = _strings(image=image)
    assert [e.text for e in reread.entries()] == [STRINGS[0], LONGER, STRINGS[2]]
    assert reread.entry(TextIdentity(GROW)).location.file_offset >= FREE


def test_a_generated_image_accounts_for_its_vacated_span_exactly():
    strings = _strings()
    original = strings.entry(TextIdentity(GROW)).location.allocation
    strings.set_text(TextIdentity(GROW), LONGER)
    image = apply_plan(strings.base_bytes, strings.plan())

    _, _, pool_end = _image()
    table = strings.profile.text_strings
    assert T._vacated_spans(image, table, strings.codec, TABLE, POOL, pool_end) == {
        GROW: original
    }


# --- SC1/SC2: the invariant fails closed ---------------------------------


def test_a_pointer_outside_both_the_pool_and_declared_space_is_refused():
    """W1 accepts declared writable space and nothing else."""
    data, offsets, pool_end = _image()
    broken = bytearray(data)
    stray = FREE + FREE_SIZE + 0x40
    broken[stray : stray + len(tt.encode_string("Loose"))] = tt.encode_string("Loose")
    slot = TABLE + GROW * 4
    broken[slot : slot + 4] = tt.encode_pointer(stray)

    profile = _profile(bytes(broken))
    with pytest.raises(T.TextProfileError, match="verified-writable"):
        list(
            T._enumerate_utf16le(
                bytes(broken), profile.text_strings, TABLE, POOL, pool_end,
                {GROW: len(tt.encode_string(STRINGS[GROW]))},
                T._writable_regions(profile),
            )
        )


# --- TOOLKIT-036 reader invariants: containment, alias, overlap ----------
#
# These are READER contract invariants, not writer ones. Our own writer cannot
# emit any of the three images below - the allocator would refuse - but the
# reader is handed third-party and hand-patched images too, and each of these
# would otherwise be read as a set of sound strings rather than refused. Every
# one is driven straight at `_enumerate_utf16le`, because that is the layer the
# contract belongs to.


def test_a_relocated_body_that_runs_past_its_region_is_refused():
    """Containment is BOTH bounds. A body may not start inside declared space
    and end outside it.

    The body is planted so that it begins within the last bytes of the free
    region and its terminator falls beyond the region's end. A check that only
    established the lower bound would accept it and the reader would then be
    reading, and later authorising writes to, bytes nobody verified.
    """
    data, _offsets, pool_end = _image()
    broken = bytearray(data)
    body = tt.encode_string("Overrun")
    # Starts inside the region, ends past it: 8 bytes of headroom, a longer body.
    start = FREE + FREE_SIZE - 8
    assert start >= FREE and start + len(body) > FREE + FREE_SIZE
    broken[start : start + len(body)] = body
    slot = TABLE + GROW * 4
    broken[slot : slot + 4] = tt.encode_pointer(start)

    profile = _profile(bytes(broken))
    with pytest.raises(T.TextProfileError, match="verified-writable"):
        list(
            T._enumerate_utf16le(
                bytes(broken), profile.text_strings, TABLE, POOL, pool_end,
                {GROW: len(tt.encode_string(STRINGS[GROW]))},
                T._writable_regions(profile),
            )
        )


def test_two_slots_naming_one_relocated_body_are_refused():
    """Alias rejection. One relocated body belongs to exactly one entry.

    Two identities sharing one span means a write attributed to either silently
    rewrites the other, so the reader refuses rather than representing both.
    """
    data, _offsets, pool_end = _image()
    broken = bytearray(data)
    body = tt.encode_string("Shared")
    broken[FREE : FREE + len(body)] = body
    for index in (0, GROW):
        slot = TABLE + index * 4
        broken[slot : slot + 4] = tt.encode_pointer(FREE)

    profile = _profile(bytes(broken))
    vacated = {index: len(tt.encode_string(STRINGS[index])) for index in (0, GROW)}
    with pytest.raises(T.TextProfileError, match="aliased relocation targets"):
        list(
            T._enumerate_utf16le(
                bytes(broken), profile.text_strings, TABLE, POOL, pool_end,
                vacated, T._writable_regions(profile),
            )
        )


def test_two_relocated_bodies_whose_spans_overlap_are_refused():
    """Overlap rejection, at ENUMERATION rather than only at `plan_changes`.

    `plan_changes` refuses a write that would do this, but an image handed to
    the reader may already contain it; reading it as two sound strings would be
    a wrong answer rather than a deferred one.
    """
    data, _offsets, pool_end = _image()
    broken = bytearray(data)
    first = tt.encode_string("Overlapping body")
    broken[FREE : FREE + len(first)] = first
    # The second body starts INSIDE the first, so the two spans intersect while
    # each still decodes normally and each still lies wholly inside the region.
    second_at = FREE + 4
    second = tt.encode_string("Inside")
    broken[second_at : second_at + len(second)] = second

    for index, offset in ((0, FREE), (GROW, second_at)):
        slot = TABLE + index * 4
        broken[slot : slot + 4] = tt.encode_pointer(offset)

    profile = _profile(bytes(broken))
    vacated = {index: len(tt.encode_string(STRINGS[index])) for index in (0, GROW)}
    with pytest.raises(T.TextProfileError, match="may not share bytes"):
        list(
            T._enumerate_utf16le(
                bytes(broken), profile.text_strings, TABLE, POOL, pool_end,
                vacated, T._writable_regions(profile),
            )
        )


def test_an_out_of_pool_target_with_no_vacated_span_is_refused():
    """Condition 3: a relocation must own the pool bytes it left behind."""
    strings = _strings()
    strings.set_text(TextIdentity(GROW), LONGER)
    image = apply_plan(strings.base_bytes, strings.plan())

    _, _, pool_end = _image()
    with pytest.raises(T.TextProfileError, match="vacated span"):
        list(
            T._enumerate_utf16le(
                image, strings.profile.text_strings, TABLE, POOL, pool_end,
                {}, T._writable_regions(strings.profile),
            )
        )


def test_an_unexplained_hole_in_the_pool_fails_closed():
    """A gap belonging to no proven relocation is an error, exactly as before.

    The pointer is moved past the first string, so the pool carries a hole no
    relocation explains - nothing left the pool, so nothing vacated anything.
    """
    data, offsets, pool_end = _image()
    broken = bytearray(data)
    slot = TABLE + GROW * 4
    broken[slot : slot + 4] = tt.encode_pointer(offsets[2])

    profile = _profile(bytes(broken))
    with pytest.raises(T.TextProfileError, match="not exhaustive|exhaustively"):
        list(
            T._enumerate_utf16le(
                bytes(broken), profile.text_strings, TABLE, POOL, pool_end,
                T._vacated_spans(bytes(broken), profile.text_strings,
                                 T._codec_for(profile.text_strings),
                                 TABLE, POOL, pool_end),
                T._writable_regions(profile),
            )
        )


def test_an_in_pool_entry_cannot_borrow_a_vacated_explanation():
    """Condition 3 the other way: a live body may not claim to have moved."""
    data, _, pool_end = _image()
    profile = _profile(data)
    with pytest.raises(T.TextProfileError, match="still resolves into the declared pool"):
        list(
            T._enumerate_utf16le(
                data, profile.text_strings, TABLE, POOL, pool_end,
                {GROW: 30}, T._writable_regions(profile),
            )
        )


# --- SC5/SC7: ownership refuses the multi-referenced body by SHAPE -------


def test_a_body_a_second_aligned_word_also_names_is_refused():
    """The five canonical coincidences, reproduced by their measured shape.

    No index is named. The fixture plants a second word-aligned u32 holding the
    body's address - which is all the five have in common - and the ownership
    census refuses the body on its inbound count.
    """
    strings = _strings(second_word_at=FREE + FREE_SIZE + 0x80)
    assert TextIdentity(GROW) not in strings._owned
    assert TextIdentity(0) in strings._owned

    with pytest.raises(T.TextTooLongError, match="not exactly its own table slot"):
        strings.set_text(TextIdentity(GROW), LONGER)


def test_a_second_aligned_word_does_not_block_an_unrelated_string():
    """Fail-closed must be targeted; blocking every string would be useless."""
    strings = _strings(second_word_at=FREE + FREE_SIZE + 0x80)
    strings.set_text(TextIdentity(0), LONGER)
    assert strings.relocations()[0].anchor == "text:0000"


def test_ownership_is_published_as_the_anchor_s_relocatable_flag():
    strings = _strings(second_word_at=FREE + FREE_SIZE + 0x80)
    document = strings.reference_document(
        [TextIdentity(0), TextIdentity(GROW)]
    )
    assert document.anchor(T._anchor_id(TextIdentity(0))).relocatable is True
    assert document.anchor(T._anchor_id(TextIdentity(GROW))).relocatable is False


def test_each_body_publishes_exactly_its_own_table_slot_as_a_reference():
    strings = _strings()
    document = strings.reference_document([TextIdentity(GROW)])
    reference, = document.references
    assert reference.source.value == TABLE + GROW * 4
    assert reference.target == T._anchor_id(TextIdentity(GROW))
    assert reference.target_delta == 0


# --- SC3/SC4: capability and kind gating ---------------------------------


def test_the_text_kind_is_eligible_through_the_existing_relocation_path():
    assert T.TEXT_STRING_KIND in RELOCATION_ELIGIBLE_KINDS


def test_a_table_that_does_not_declare_relocation_refuses_growth():
    strings = _strings(relocatable=False)
    assert strings._owned == frozenset()
    with pytest.raises(T.TextTooLongError, match="relocatable: false"):
        strings.set_text(TextIdentity(GROW), LONGER)


def test_the_buu_profile_declares_text_relocation_and_logii_does_not():
    """W3, asserted on the shipped config rather than on a fixture."""
    catalog = RomProfileCatalog.load("config/roms.yaml")
    for profile in catalog.profiles:
        table = profile.text_strings
        if table is None:
            continue
        expected = table.encoding == "utf16le_nul_terminated"
        assert table.relocatable is expected, profile.id


def test_the_packaged_mirror_agrees_with_the_shipped_config():
    live = RomProfileCatalog.load("config/roms.yaml")
    packaged = RomProfileCatalog.load("tools/webfoot/data/roms.yaml")
    mirrored = {p.id: p.text_strings for p in packaged.profiles}
    for profile in live.profiles:
        assert mirrored[profile.id] == profile.text_strings, profile.id


# --- SC9: capacity, codec and overlap all fail closed --------------------


def test_insufficient_declared_capacity_fails_closed():
    strings = _strings()
    with pytest.raises(T.TextTooLongError, match="refused"):
        strings.set_text(TextIdentity(GROW), "X" * (FREE_SIZE + 16))
    assert strings._relocating == {}


def test_a_profile_with_no_declared_free_space_fails_closed():
    strings = _strings(free=False)
    with pytest.raises(T.TextTooLongError, match="refused"):
        strings.set_text(TextIdentity(GROW), LONGER)


def test_an_unsupported_character_still_fails_as_a_codec_error():
    """Encodability is decided before storage is, and says so."""
    strings = _strings()
    with pytest.raises(TextCodecError):
        strings.set_text(TextIdentity(GROW), "no NUL\x00here, however long " * 4)


def test_two_strings_grow_into_one_deterministic_batch():
    strings = _strings()
    strings.set_text(TextIdentity(0), LONGER)
    strings.set_text(TextIdentity(2), LONGER)
    moved = {p.anchor for p in strings.relocations()}
    assert moved == {"text:0000", "text:0002"}

    image = apply_plan(strings.base_bytes, strings.plan())
    for index in (0, 2):
        assert tt.decode_string(image, _pointer(image, index))[0] == LONGER


def test_a_relocation_that_collides_with_another_subsystem_is_an_overlap_error():
    """The relocation joins the SAME merged plan, so a collision is hard.

    This is what stops a relocated body from silently overwriting bytes another
    subsystem - TOOLKIT-035's authored entity, descriptor and script bodies among
    them - allocated from the same declared free region.
    """
    from tools.webfoot.write import ByteChange, plan_changes

    strings = _strings()
    strings.set_text(TextIdentity(GROW), LONGER)
    destination = strings.relocations()[0].new_range

    rival = ByteChange(
        destination.start.value,
        strings.base_bytes[destination.start.value : destination.start.value + 4],
        b"\xde\xad\xbe\xef",
        "rival:subsystem",
        "a second subsystem allocating from the same declared region",
    )
    with pytest.raises(OverlappingChangeError):
        plan_changes(
            strings.base_bytes,
            [*strings.changes(), rival],
            profile_id=strings.profile.id,
            base_sha256=strings.profile.sha256,
        )


def test_growth_needs_no_flag_and_no_address_from_the_author():
    """SC8. The only thing the author supplied was the text itself."""
    import inspect

    signature = inspect.signature(T.TextStrings.set_text)
    assert list(signature.parameters) == ["self", "identity", "text"]
