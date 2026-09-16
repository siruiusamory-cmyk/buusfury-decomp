"""Synthetic regression tests for :mod:`tools.research.thumb_mem_operands`.

These are hand-computed halfwords, not ROM-derived fixtures, so they run
without the private canonical image.  They exist because a wrong bit-field
position in a constant-offset scan does not raise: it silently reports an empty
or misattributed result that reads exactly like evidence of absence.  Each
encoding is therefore pinned on an instruction whose bytes and operands are
written out here by hand.

The measured coverage claim lives in
``tests/integration/test_logx_connector_rom.py::test_the_operand_scan_agrees_with_capstone``,
which runs this decoder against Capstone over the whole canonical image; this
file is the fast, portable regression net.
"""

from __future__ import annotations

import pytest

from tools.research.thumb_mem_operands import (
    ROM_BASE,
    MemoryOperand,
    coverage_note,
    decode_memory_operands,
    find_field_accesses,
    iter_memory_operands,
)


def image(*halfwords: int) -> bytes:
    """Little-endian halfwords placed at the image start."""
    out = bytearray(0x100)
    for index, value in enumerate(halfwords):
        out[2 * index] = value & 0xFF
        out[2 * index + 1] = (value >> 8) & 0xFF
    return bytes(out)


AT = ROM_BASE


def site(data: bytes, address: int = AT) -> MemoryOperand:
    found = decode_memory_operands(data, address)
    assert len(found) == 1, found
    return found[0]


# --- 16-bit forms ------------------------------------------------------------
#
# Encoding is `0110 L imm5 rn rt` (word), `0111 L imm5 rn rt` (byte) and
# `1000 L imm5 rn rt` (halfword), where `L` is bit 11.  Real canonical-image
# examples are named in the comments.


def test_16bit_word_load_and_store() -> None:
    # 0x0800004A holds 9A 61 -> str r2,[r3,#0x18]
    store = site(image(0x619A))
    assert (store.mnemonic, store.rt_name, store.rn_name, store.immediate) == (
        "str",
        "r2",
        "r3",
        0x18,
    )
    # The same encoding with L set is the load.
    load = site(image(0x699A))
    assert (load.mnemonic, load.rt_name, load.rn_name, load.immediate) == (
        "ldr",
        "r2",
        "r3",
        0x18,
    )
    # `0110 0 00011 001 000` = 0x60C8 -> str r0,[r1,#0xC]
    assert site(image(0x60C8)).immediate == 0xC


def test_16bit_byte_forms() -> None:
    # 0x08000040 holds 13 72 -> strb r3,[r2,#8]
    store = site(image(0x7213))
    assert (store.mnemonic, store.rt_name, store.rn_name, store.immediate) == (
        "strb",
        "r3",
        "r2",
        8,
    )
    # 0x08000138 holds 00 7E -> ldrb r0,[r0,#0x18]
    load = site(image(0x7E00))
    assert (load.mnemonic, load.rt_name, load.rn_name, load.immediate) == (
        "ldrb",
        "r0",
        "r0",
        0x18,
    )


def test_16bit_halfword_forms_scale_the_immediate_by_two() -> None:
    # `1000 1 00011 100 101` = 0x88E5 -> ldrh r5,[r4,#6]
    load = site(image(0x88E5))
    assert (load.mnemonic, load.rt_name, load.rn_name, load.immediate) == (
        "ldrh",
        "r5",
        "r4",
        6,
    )
    # 0x0800000C holds 3D 84 -> strh r5,[r7,#0x20]
    store = site(image(0x843D))
    assert (store.mnemonic, store.rt_name, store.rn_name, store.immediate) == (
        "strh",
        "r5",
        "r7",
        0x20,
    )
    # 0x08000096 holds E4 8B -> ldrh r4,[r4,#0x1E]
    assert site(image(0x8BE4)).immediate == 0x1E


def test_the_two_register_fields_are_not_interchangeable() -> None:
    """Swapping rt and rn keeps the address and displacement but misnames the base.

    This is the exact silent failure the module docstring warns about, so the
    asymmetry is asserted rather than assumed: 0x699A must not decode as
    ``ldr r3, [r2, #0x18]``.
    """
    operand = site(image(0x699A))
    assert (operand.rt_name, operand.rn_name) == ("r2", "r3")
    assert (operand.rt_name, operand.rn_name) != ("r3", "r2")
    # The mirror image, which differs only by exchanging the two fields.
    mirrored = site(image(0x6993))
    assert (mirrored.rt_name, mirrored.rn_name) == ("r3", "r2")


def test_the_class_is_a_four_bit_opcode() -> None:
    """The byte class is the four-bit opcode 0111, so the class mask is 0xF000.

    Masking with 0xF800 splits `0110 L` from `0111 L` incorrectly and drops
    every word load; masking with 0x7800 drops every byte access instead.
    """
    assert (0x7213 & 0xF000) == 0x7000
    assert (0x7213 & 0xF800) != 0x7800
    assert (0x699A & 0xF000) == 0x6000
    assert (0x699A & 0xF800) == 0x6800
    assert site(image(0x7213)).mnemonic == "strb"
    assert site(image(0x699A)).mnemonic == "ldr"
    assert site(image(0x8BE4)).mnemonic == "ldrh"


def test_16bit_groups_outside_the_scan_report_nothing() -> None:
    """The literal, register-offset and SP-relative 16-bit groups are not covered."""
    assert decode_memory_operands(image(0x5C88), AT) == ()  # ldrb r0,[r1,r2]
    assert decode_memory_operands(image(0x9802), AT) == ()  # ldr r0,[sp,#8]
    assert decode_memory_operands(image(0x9A02), AT) == ()  # ldr r2,[sp,#8]
    assert decode_memory_operands(image(0x4801), AT) == ()  # ldr r0,[pc,#4]


# --- 32-bit positive-immediate forms ----------------------------------------
#
# Layout (ARM "Load/store single data item", 12-bit positive immediate):
#   first  halfword `1111 1000 op(4) Rn`, op = bits 7:4
#     0x8 strb, 0x9 ldrb, 0xA strh, 0xB ldrh, 0xC str, 0xD ldr
#   second halfword `Rt imm12`, Rt = bits 15:12, imm12 = bits 11:0 unscaled


def test_32bit_positive_immediate_forms() -> None:
    # `ldr r4,[r6,#0xC]`, the encoding the ROM uses at 0x080093B2.
    load = site(image(0xF8D6, 0x400C))
    assert (load.mnemonic, load.rt_name, load.rn_name, load.immediate) == (
        "ldr",
        "r4",
        "r6",
        0x0C,
    )
    # `str r1,[r4,#0x3C]`, at 0x0800CB60.
    store = site(image(0xF8C4, 0x103C))
    assert (store.mnemonic, store.rt_name, store.rn_name, store.immediate) == (
        "str",
        "r1",
        "r4",
        0x3C,
    )
    # `ldrb r1,[r4,#0x13]`, the destination high byte at 0x08007282.
    assert (site(image(0xF894, 0x1013)).mnemonic, site(image(0xF894, 0x1013)).immediate) == (
        "ldrb",
        0x13,
    )
    # `ldrb r2,[r4,#0x12]`, the destination low byte at 0x0800728C.
    assert (site(image(0xF894, 0x2012)).mnemonic, site(image(0xF894, 0x2012)).immediate) == (
        "ldrb",
        0x12,
    )
    # `ldrh` and `strh` share the layout at op 0xB / 0xA.
    assert site(image(0xF8B4, 0x1016)).mnemonic == "ldrh"
    assert site(image(0xF8A4, 0x1016)).mnemonic == "strh"


def test_the_32bit_size_and_load_fields_are_separate() -> None:
    """SIZE is bits 6:5 and L is bit 4, both inside the op nibble.

    Enumerating the whole field rather than trusting one comment is what makes
    the table trustworthy: a wrong size bit silently turns every ``ldrb`` into a
    ``str`` or drops it.
    """
    for size, loads in ((0, ("ldrb", "strb")), (1, ("ldrh", "strh")), (2, ("ldr", "str"))):
        for load, expected in ((1, loads[0]), (0, loads[1])):
            first = 0xF800 | ((0x8 | (size << 1) | load) << 4) | 4
            operand = site(image(first, 0x3018))
            assert operand.mnemonic == expected, (size, load, hex(first))
            assert (operand.rt_name, operand.rn_name, operand.immediate) == (
                "r3",
                "r4",
                0x18,
            )


def test_the_second_halfword_has_no_fixed_prefix() -> None:
    """A `second & 0xF000 == 0xF000` requirement would drop every real access.

    The imm12 lives in bits 11:0 with no fixed high nibble, so `Rt` and a small
    immediate share the halfword.
    """
    assert decode_memory_operands(image(0xF8D6, 0x400C), AT) != ()
    # Register-offset and negative-immediate families are out of scope.
    assert decode_memory_operands(image(0xF851, 0x0002), AT) == ()
    assert decode_memory_operands(image(0xF851, 0x3F04), AT) == ()


def test_hint_and_undefined_encodings_are_suppressed() -> None:
    """Two architecture-level aliases must not be reported as data accesses.

    ``ldrb``/``ldrh`` with ``Rt = 15`` is the ``pld``/``pldw`` prefetch hint, and
    ``str``/``strb``/``strh`` with ``Rn = 15`` is a PC-relative store the
    architecture leaves UNDEFINED.  ``ldr`` with ``Rt = 15`` (branch via load)
    and loads based on PC remain reported.
    """
    assert decode_memory_operands(image(0xF89F, 0xF018), AT) == ()  # pld
    assert decode_memory_operands(image(0xF88F, 0x3018), AT) == ()  # undefined
    assert decode_memory_operands(image(0xF8DF, 0x0018), AT) != ()  # ldr pc,[pc,#imm]


def test_32bit_out_of_scope_op_nibbles_report_nothing() -> None:
    for op in (0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0xE, 0xF):
        first = 0xF800 | (op << 4) | 4
        assert decode_memory_operands(image(first, 0x3018), AT) == (), hex(op)


# --- scanning helpers --------------------------------------------------------


def test_scan_finds_every_halfword_offset_and_filters() -> None:
    data = image(0x619A, 0x7213, 0x8BE4)
    everything = find_field_accesses(data, {0x18, 8, 0x1E}, end=ROM_BASE + 6)
    assert [(item.address, item.mnemonic, item.immediate) for item in everything] == [
        (ROM_BASE + 0, "str", 0x18),
        (ROM_BASE + 2, "strb", 8),
        (ROM_BASE + 4, "ldrh", 0x1E),
    ]
    only_bytes = find_field_accesses(
        data, {8}, end=ROM_BASE + 6, mnemonics={"ldrb", "strb"}
    )
    assert [item.mnemonic for item in only_bytes] == ["strb"]
    only_r4 = find_field_accesses(data, {0x1E}, end=ROM_BASE + 6, base_registers={4})
    assert [item.rn_name for item in only_r4] == ["r4"]
    assert find_field_accesses(data, {0x40}, end=ROM_BASE + 6) == []


def test_decoding_stops_cleanly_at_the_image_edge() -> None:
    data = image(0x619A)
    assert decode_memory_operands(data, ROM_BASE - 2) == ()
    assert decode_memory_operands(data, ROM_BASE + 0x100) == ()
    # A 32-bit first halfword with no room for its second is dropped.
    assert decode_memory_operands(image(0xF8D6)[:2], AT) == ()


def test_iteration_yields_the_same_sites_as_the_point_query() -> None:
    data = image(0x619A, 0x7213, 0x8BE4)
    iterated = list(iter_memory_operands(data, ROM_BASE, ROM_BASE + 6))
    for address in (ROM_BASE, ROM_BASE + 2, ROM_BASE + 4):
        assert decode_memory_operands(data, address)[0] in iterated


def test_coverage_note_states_what_is_not_scanned() -> None:
    note = coverage_note(0x08000000, 0x08007000)
    assert "0x08000000" in note and "0x08007000" in note
    for gap in ("PC-relative", "SP-relative", "register-offset"):
        assert gap in note


@pytest.mark.parametrize("halfword", [0x0000, 0xFFFF, 0x4800, 0xB510, 0xE7FE])
def test_non_memory_halfwords_report_nothing(halfword: int) -> None:
    assert decode_memory_operands(image(halfword), AT) == ()


@pytest.mark.parametrize(
    ("halfword", "mnemonic"),
    [
        (0x619A, "str"),
        (0x699A, "ldr"),
        (0x7213, "strb"),
        (0x7E00, "ldrb"),
        (0x843D, "strh"),
        (0x8BE4, "ldrh"),
    ],
)
def test_every_16bit_encoding_round_trips(halfword: int, mnemonic: str) -> None:
    assert site(image(halfword)).mnemonic == mnemonic
