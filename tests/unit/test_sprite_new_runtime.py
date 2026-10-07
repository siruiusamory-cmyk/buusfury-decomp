"""SPRITE-NEW-RUNTIME-001: the new-identity planner and its SDK additions.

These are the unit-level contracts the runtime experiment depends on. They are
deliberately testable without a ROM: every encoder here is a pure function of
values that were measured once against the canonical image, and the three SDK
capabilities the experiment added are asserted exactly so that a later change to
any of them is visible instead of silent.

What is NOT tested here, because it cannot be: whether the retail engine reads the
new records at runtime. That is the emulator run's claim.
"""
from __future__ import annotations

import importlib.util
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from webfoot.allocation import (DEFAULT_ADDRESSABILITY, Addressability,
                                AllocationKind)
from webfoot.layout import (RELOCATION_ELIGIBLE_KINDS, Anchor, AnchorId,
                            Provenance, Reference, ReferenceClass,
                            ReferenceEncoding, RomRange, relocation_eligible)
from webfoot.binary import FileOffset
from webfoot.relocation import _allocation_kind

_SPEC = importlib.util.spec_from_file_location(
    "sprite_new_runtime", ROOT / "tools/research/sprite_new_runtime.py")
assert _SPEC is not None and _SPEC.loader is not None
snr = importlib.util.module_from_spec(_SPEC)
# `dataclass(slots=True)` resolves annotations through `sys.modules[cls.__module__]`,
# so the module has to be registered before it is executed.
sys.modules[_SPEC.name] = snr
_SPEC.loader.exec_module(snr)


# --- colour: the exactness claim --------------------------------------------


@pytest.mark.parametrize("five,expected", [
    (0, 0), (1, 8), (8, 66), (14, 115), (15, 123), (31, 255),
])
def test_expand_channel_is_the_hardware_expansion(five, expected):
    assert snr.expand_channel(five) == expected


@pytest.mark.parametrize("source,displayed", [
    # The bit-replicated form the retail palette stores.
    ((66, 0, 115), (66, 0, 115)),
    ((140, 107, 255), (140, 107, 255)),
    # The zero-padded form a naive converter writes. Both are the SAME 5-bit
    # colour, which is why no quantisation is needed.
    ((64, 0, 112), (66, 0, 115)),
    ((112, 40, 184), (115, 41, 189)),
    ((248, 248, 248), (255, 255, 255)),
    ((168, 168, 0), (173, 173, 0)),
    ((0, 72, 0), (0, 74, 0)),
])
def test_hardware_colour_reproduces_both_source_forms(source, displayed):
    assert snr.hardware_colour(source) == displayed


def test_hardware_colour_never_rounds():
    """`channel >> 3` is exact for every channel value, so nothing is lost."""
    for channel in range(256):
        five = channel >> 3
        # The displayed value is the expansion of the top five bits, and taking
        # the top five bits back is idempotent.
        assert snr.expand_channel(five) >> 3 == five


# --- palette assignment ------------------------------------------------------


def _palette(entries):
    """A 256-entry RGB palette with the given (index, colour) overrides."""
    rgb = [(0, 0, 0)] * 256
    for index, colour in entries.items():
        rgb[index] = colour
    return tuple(rgb)


def test_chroma_key_goes_to_the_transparent_index():
    assignment = snr.assign_palette(
        _palette({}), [snr.CHROMA_KEY, snr.CHROMA_KEY], free_indices=[7])
    assert assignment.indexed == bytes([0, 0])
    assert assignment.added == ()


def test_black_artwork_does_not_become_transparent():
    """Entries 0 and 1 are both black; art must take the non-zero one."""
    assignment = snr.assign_palette(
        _palette({1: (0, 0, 0)}), [(0, 0, 0)], free_indices=[7])
    assert assignment.indexed == bytes([1])


def test_an_existing_entry_is_reused_rather_than_written():
    assignment = snr.assign_palette(
        _palette({86: (66, 0, 115)}), [(64, 0, 112)], free_indices=[7])
    assert assignment.indexed == bytes([86])
    assert assignment.added == ()


def test_a_missing_colour_takes_a_free_index_and_is_recorded():
    assignment = snr.assign_palette(
        _palette({}), [(115, 115, 115)], free_indices=[9, 7, 8])
    # Deterministic: the free index whose current colour is nearest, then lowest.
    assert assignment.indexed == bytes([7])
    assert assignment.added == ((7, (115, 115, 115)),)


def test_two_missing_colours_never_share_an_index():
    assignment = snr.assign_palette(
        _palette({}), [(115, 115, 115), (173, 173, 173)], free_indices=[7, 9])
    assert len(set(assignment.indexed)) == 2
    assert len(assignment.added) == 2


def test_one_colour_repeated_reuses_the_same_new_index():
    assignment = snr.assign_palette(
        _palette({}), [(115, 115, 115)] * 4, free_indices=[7, 9])
    assert assignment.indexed == bytes([7, 7, 7, 7])
    assert len(assignment.added) == 1


def test_without_a_free_index_it_refuses_rather_than_quantising():
    with pytest.raises(snr.SpriteNewError, match="will not quantise"):
        snr.assign_palette(_palette({}), [(115, 115, 115)], free_indices=[])


# --- record encoders ---------------------------------------------------------


def test_registry_is_297_canonical_entries_plus_the_new_identity():
    entries = list(range(0x08000000, 0x08000000 + 297 * 4, 4))
    encoded = snr.encode_registry(entries, 0x088005B4)
    assert len(encoded) == 298 * 4
    assert struct.unpack_from("<297I", encoded) == tuple(entries)
    assert struct.unpack_from("<I", encoded, 297 * 4)[0] == 0x088005B4


def test_registry_refuses_the_wrong_entry_count():
    with pytest.raises(snr.SpriteNewError, match="expected 297"):
        snr.encode_registry([0] * 296, 0)


def test_structure_clones_the_header_and_repoints_both_slots():
    header = bytes([snr.ANIMATION_SLOT_COUNT]) + bytes(range(1, snr.DONOR_HEADER_SIZE))
    encoded = snr.encode_structure(header, 0x08800610)
    assert encoded[:snr.DONOR_HEADER_SIZE] == header
    assert struct.unpack_from(
        f"<{snr.ANIMATION_SLOT_COUNT}I", encoded, snr.DONOR_HEADER_SIZE
    ) == (0x08800610,) * snr.ANIMATION_SLOT_COUNT


def test_structure_refuses_a_header_of_the_wrong_size():
    with pytest.raises(snr.SpriteNewError, match="donor header"):
        snr.encode_structure(b"\x02" * 0x10, 0)


def test_structure_refuses_a_donor_whose_count_is_not_the_cloned_one():
    header = bytes([99]) + b"\x01" * (snr.DONOR_HEADER_SIZE - 1)
    with pytest.raises(snr.SpriteNewError, match="animation count"):
        snr.encode_structure(header, 0)


def test_animation_has_every_direction_cell_naming_one_frame():
    encoded = snr.encode_animation(0x08800634)
    assert len(encoded) == 4 + 16 * snr.ANIMATION_FRAME_COUNT
    assert struct.unpack_from("<I", encoded)[0] == snr.ANIMATION_FRAME_COUNT
    cells = struct.unpack_from(f"<{snr.ANIMATION_FRAME_COUNT * 4}I", encoded, 4)
    assert set(cells) == {0x08800634}
    # No NULL cell: the compositor dereferences the frame with no null test.
    assert 0 not in cells


def test_frame_is_one_32x32_piece_at_the_donors_anchor():
    encoded = snr.encode_frame(0x08800000)
    assert len(encoded) == 20
    assert struct.unpack_from("<I", encoded)[0] == 1
    assert struct.unpack_from("<bbBB", encoded, 4) == (-8, -24, 32, 32)
    assert struct.unpack_from("<bbBB", encoded, 8) == (-8, -24, 32, 32)
    assert struct.unpack_from("<I", encoded, 12)[0] == 0x80002000
    assert struct.unpack_from("<I", encoded, 16)[0] == 0x08800000


def test_cui_cell_index_reconciles_sheet_order_with_animation_order():
    """The sheet is direction-major; the animation record is frame-major.

    The engine reads ``animation + 4 + 16 * frame + 4 * direction``, so slot
    ``slot`` is frame ``slot // 4`` and direction ``slot % 4``. A sheet stores
    ``direction * frames + frame``. Getting this wrong puts a different FACING in
    each frame slot, and the actor rotates through all four facings while it
    walks - which is exactly what a run showed before this mapping existed.
    """
    # One frame per direction: the two orders coincide, which is why a 4-cell
    # sheet could never reveal the difference.
    assert [snr.cui_cell_index(slot, 1) for slot in range(4)] == [0, 1, 2, 3]

    # Two frames per direction (stand, 8 cells): direction d holds cells 2d, 2d+1.
    assert [snr.cui_cell_index(slot, 2) for slot in range(8)] == [0, 2, 4, 6, 1, 3, 5, 7]

    # Four frames per direction (walk, 16 cells): direction d holds 4d..4d+3, so
    # the four direction slots of frame 0 are cells 0, 4, 8 and 12.
    walk = [snr.cui_cell_index(slot, 4) for slot in range(16)]
    assert walk[:4] == [0, 4, 8, 12]
    assert walk[4:8] == [1, 5, 9, 13]
    assert sorted(walk) == list(range(16))
    for direction in range(4):
        frames_of_one_facing = [walk[frame * 4 + direction] for frame in range(4)]
        assert frames_of_one_facing == [direction * 4 + f for f in range(4)]


def test_cui_sheet_frames_is_four_direction_cells_per_frame(tmp_path):
    """A Cui sheet is four direction cells per frame, not one direction.

    This is a correction, not a convenience: SPRITE-NEW-BOUNDARY-001 recorded
    these sheets as single-direction on the evidence that each is one row of 32x32
    cells, and identity 307 was first built from one cell stamped into all four
    direction slots. The rule is asserted on synthetic sheets so it does not
    depend on the artwork being present.

    Pillow is what writes and reads those synthetic sheets, and it is NOT a
    declared dependency of this repository: the CI job installs
    `.[dev,workbench,research]` and has no PIL, so this test skips there. The
    rule is therefore asserted wherever Pillow is available and is unverified in
    CI, which is recorded rather than hidden. Declaring Pillow, or reading the
    sheet's size without it, is a separate change.
    """
    Image = pytest.importorskip("PIL.Image")

    for cells, frames in ((4, 1), (8, 2), (12, 3), (16, 4)):
        path = tmp_path / f"sheet{cells}.png"
        Image.new("RGB", (cells * 32, 32), (0, 0, 0)).save(path)
        assert snr.cui_sheet_frames(path) == frames

    # A sheet that is not a whole number of four-cell groups is refused rather
    # than silently read at the wrong stride.
    odd = tmp_path / "odd.png"
    Image.new("RGB", (2 * 32, 32), (0, 0, 0)).save(odd)
    with pytest.raises(snr.SpriteNewError, match="four-cell frame groups"):
        snr.cui_sheet_frames(odd)

    wrong_height = tmp_path / "tall.png"
    Image.new("RGB", (8 * 32, 64), (0, 0, 0)).save(wrong_height)
    with pytest.raises(snr.SpriteNewError):
        snr.cui_sheet_frames(wrong_height)


def test_structure_many_writes_the_count_it_actually_wrote():
    """The header's count byte must match the array, not the donor's old count.

    Five engine sites read ``+0x00`` with ``ldrb`` and compare it against the
    animation index they want before loading ``+0x54 + 4*index``, so a count that
    disagrees with the array is a slot the engine refuses to reach.
    """
    header = bytes([snr.ANIMATION_SLOT_COUNT]) + b"\x01" * (snr.DONOR_HEADER_SIZE - 1)
    single = snr.encode_structure_many(header, [0x08800610])
    assert single[0] == 1
    assert struct.unpack_from("<I", single, snr.DONOR_HEADER_SIZE)[0] == 0x08800610

    pair = snr.encode_structure_many(header, [0x08800610, 0x08800644])
    assert pair[0] == 2
    assert struct.unpack_from("<2I", pair, snr.DONOR_HEADER_SIZE) == (
        0x08800610, 0x08800644)

    with pytest.raises(snr.SpriteNewError, match="1..23"):
        snr.encode_structure_many(header, [])


# --- the three SDK capabilities the experiment added -------------------------


def test_sprite_identity_records_are_registered_expanded_only():
    """The registry alone is 1,192 bytes against a 256-byte canonical window."""
    assert (DEFAULT_ADDRESSABILITY[AllocationKind.SPRITE_IDENTITY_RECORD]
            is Addressability.EXPANDED_ONLY)


def test_the_character_registry_is_the_only_newly_eligible_anchor_kind():
    assert "character_pointer_table" in RELOCATION_ELIGIBLE_KINDS
    # A structure is still fixed: moving one is not what this experiment proves.
    assert "character_structure" not in RELOCATION_ELIGIBLE_KINDS


def test_a_moved_registry_gets_the_sprite_identity_kind_not_the_default():
    class _Anchor:
        kind = "character_pointer_table"

    assert _allocation_kind(_Anchor()) is AllocationKind.SPRITE_IDENTITY_RECORD


def test_a_registry_with_two_confirmed_inbound_words_is_eligible():
    provenance = Provenance("fixture", "0" * 64, "fixture")
    table = Anchor(AnchorId("fixture/character_table:0000"),
                   RomRange(FileOffset(0x6B6BDC), 297 * 4),
                   "character_pointer_table", "table", 4, False, provenance)
    inbound = [
        Reference(FileOffset(0x3C0), table.identity, 0,
                  ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                  ReferenceClass.CONFIRMED_REFERENCE, provenance),
        Reference(FileOffset(0x1715C), table.identity, 0,
                  ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                  ReferenceClass.CONFIRMED_REFERENCE, provenance),
    ]
    assert relocation_eligible(table, inbound) is True
    # One unresolved numeric hit withdraws it, as the shared rule requires.
    candidate = Reference(FileOffset(0x4000), table.identity, 0,
                          ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                          ReferenceClass.CANDIDATE_REFERENCE, provenance)
    assert relocation_eligible(table, inbound + [candidate]) is False
    # And an unreferenced registry is not movable on hope.
    assert relocation_eligible(table, ()) is False


# --- the runtime harness -----------------------------------------------------


def test_the_observer_is_allowlisted_for_injection():
    injector = (ROOT / "tools/runtime/inject_mgba_lua.ps1").read_text(
        encoding="utf-8")
    assert "spritenew001_observer.lua" in injector


def test_the_observer_never_writes_emulated_memory():
    """A read-only observer is the whole safety story of the runtime run."""
    source = (ROOT / "tools/runtime/spritenew001_observer.lua").read_text(
        encoding="utf-8")
    for forbidden in ("emu:write8", "emu:write16", "emu:write32",
                      "emu:writeRange", "emu:writes"):
        assert forbidden not in source
    # Its only emulated-state change is controller input, on a named schedule.
    assert "emu:setKeys" in source


def test_the_launcher_passes_the_rom_last_and_bare():
    """mGBA's usage is `[option ...] file`, and a multi-element ArgumentList with
    a quoted path reaches it with the quote characters included.

    The argument text is built in the shared session mechanism now, so the shape is
    asserted there and the launcher is asserted to hand it the staged ROM plus the
    savegame override.
    """
    launcher = (ROOT / "tools/runtime/start_spritenew001_session.ps1").read_text(
        encoding="utf-8")
    helper = (ROOT / "tools/runtime/mgba_session.ps1").read_text(encoding="utf-8")
    assert "Start-MgbaSession" in launcher
    assert "-ArgumentList @('-C', ('savegamePath=' + $saveDir))" in launcher
    # One argument string, options first, the ROM LAST and bare.
    assert "('-t \"{0}\" {1} \"{2}\"' -f" in helper or "$options += @('--script', $bootstrap)" in helper
    assert "(' \"{0}\"' -f $RomPath)" in helper
    # The staged copy is what makes the bare form safe: no spaces in the path.
    assert "Join-Path $runDir 'rom.gba'" in launcher
