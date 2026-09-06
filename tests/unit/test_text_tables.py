"""Portable proofs for the TOOLKIT-004 text codec.

No ROM bytes appear here. Every fixture is constructed, so the whole file runs
on a machine that has never seen the game - the ROM-gated proofs live in
`tests/integration/test_text_rom.py`.

The codec's contract is one sentence: `encode(decode(x)) == x` for every byte
sequence the format can hold. These tests attack that from both ends - known
inputs decode to known text, and unknown control data survives untouched.
"""

from __future__ import annotations

import pytest

from tools.webfoot.formats import text_tables as tt


def u16(*units: int) -> bytes:
    """Little-endian 16-bit units, the form the pool actually stores."""
    return b"".join(unit.to_bytes(2, "little") for unit in units)


def encoded(text: str) -> bytes:
    return u16(*(ord(c) for c in text), 0x0000)


# --- exit criterion 3: decode correctness --------------------------------


def test_plain_ascii_decodes_to_the_same_characters():
    data = encoded("Start")
    assert tt.decode_string(data, 0) == ("Start", len(data))


def test_decode_reports_the_offset_past_the_terminator():
    """Walking the pool depends on this: the second return IS the next string."""
    data = encoded("ab") + encoded("cd")
    text, end = tt.decode_string(data, 0)
    assert text == "ab"
    assert end == 6  # 'a', 'b', terminator
    assert tt.decode_string(data, end) == ("cd", 12)


def test_empty_string_is_legal_and_decodes_to_empty_text():
    """11 of the canonical pool's 1,534 strings are empty, index 0 included."""
    assert tt.decode_string(u16(0x0000), 0) == ("", 2)


def test_newline_decodes_to_a_real_newline():
    text, _ = tt.decode_string(u16(0x0041, 0x000A, 0x0042, 0x0000), 0)
    assert text == "A\nB"


def test_non_ascii_codepoint_decodes_as_that_codepoint():
    """The canonical pool's single 0x00E9 is the accented e in "Hercule Cafe".

    This is the evidence the encoding is UTF-16LE rather than a game-specific
    glyph table, so it gets a test rather than only a comment.
    """
    text, _ = tt.decode_string(u16(0x00E9, 0x0000), 0)
    assert text == "é"


def test_unterminated_input_is_refused_rather_than_read_past_the_end():
    with pytest.raises(tt.TextCodecError, match="unterminated"):
        tt.decode_string(u16(0x0041, 0x0042), 0)


def test_control_prefix_without_an_operand_is_refused():
    with pytest.raises(tt.TextCodecError, match="no operand"):
        tt.decode_string(u16(0x0041, 0x0008), 0)


# --- exit criterion 4: encode correctness --------------------------------


def test_encode_appends_the_terminator():
    assert tt.encode_string("Hi") == u16(0x0048, 0x0069, 0x0000)


def test_encode_of_empty_text_is_just_the_terminator():
    assert tt.encode_string("") == u16(0x0000)


def test_encoded_size_matches_what_encode_produces():
    for text in ("", "a", "Hello", "A\nB", "x{08:07}y"):
        assert tt.encoded_size(text) == len(tt.encode_string(text))


def test_embedded_nul_is_refused_because_it_would_terminate_the_string():
    with pytest.raises(tt.TextCodecError, match="NUL"):
        tt.encode_string("a\x00b")


def test_astral_characters_are_refused_rather_than_silently_surrogate_paired():
    with pytest.raises(tt.TextCodecError, match="basic multilingual plane"):
        tt.encode_string("\U0001F600")


def test_malformed_control_token_is_refused():
    for bad in ("{08:ZZ}", "{08:7}", "{09:07}", "{", "a{b"):
        with pytest.raises(tt.TextCodecError, match="malformed control token"):
            tt.encode_string(bad)


# --- exit criterion 5: unknown control bytes survive ---------------------


def test_unknown_control_operand_round_trips_byte_for_byte():
    """The 0x08 operand's meaning is UNKNOWN; its bytes must survive anyway.

    0x42 is deliberately not one of the seven operands the canonical pool uses,
    so this proves preservation rather than a lucky lookup in a known set.
    """
    data = u16(0x0041, 0x0008, 0x0042, 0x0043, 0x0000)
    text, _ = tt.decode_string(data, 0)
    assert text == "A{08:42}C"
    assert tt.encode_string(text) == data


@pytest.mark.parametrize("operand", [0x02, 0x03, 0x05, 0x06, 0x07, 0x1D, 0x76, 0x00, 0xFF])
def test_every_control_operand_round_trips(operand: int):
    """The seven operands the canonical pool uses, plus the two extremes."""
    data = u16(0x0008, operand, 0x0000)
    text, _ = tt.decode_string(data, 0)
    assert tt.encode_string(text) == data


def test_literal_brace_in_rom_text_survives_the_escape_syntax():
    """Without doubling, ROM text containing "{08:02}" would re-encode as a
    control code. The pool has no brace today; a modder's text might."""
    data = encoded("{08:02}")
    text, _ = tt.decode_string(data, 0)
    assert text == "{{08:02}"
    assert tt.encode_string(text) == data


def test_literal_backslash_is_not_an_escape_character_here():
    """The escape introducer is "{", not "\\", so a backslash is ordinary."""
    data = encoded("a\\nb")
    text, _ = tt.decode_string(data, 0)
    assert text == "a\\nb"
    assert tt.encode_string(text) == data


def test_bare_control_unit_cannot_be_written_as_a_literal_character():
    with pytest.raises(tt.TextCodecError, match="cannot be written"):
        tt.encode_string("a\x08b")


# --- identity -------------------------------------------------------------


def test_identity_key_is_zero_padded_so_string_order_equals_index_order():
    keys = [tt.TextIdentity(i).key for i in (9, 10, 100, 1533)]
    assert keys == ["text:0009", "text:0010", "text:0100", "text:1533"]
    assert keys == sorted(keys)


def test_identity_refuses_a_negative_or_non_integer_index():
    for bad in (-1, "0", 1.0):
        with pytest.raises(tt.TextCodecError):
            tt.TextIdentity(bad)


def test_identity_accepts_an_index_beyond_this_games_table():
    """The upper bound belongs to the profile, not to this codec.

    TOOLKIT-004 capped the index at Buu's Fury's 1,534 here, which made identity
    - the one concept genuinely shared across games - carry one game's table
    size. Legacy of Goku II declares 217, and a future profile could declare
    more; `webfoot.text` checks the index against the loaded profile's count,
    which is the only place that number is actually known.
    """
    assert tt.TextIdentity(tt.TEXT_ENTRY_COUNT).index == tt.TEXT_ENTRY_COUNT


def test_identity_is_hashable_and_compares_by_value():
    assert tt.TextIdentity(7) == tt.TextIdentity(7)
    assert len({tt.TextIdentity(7), tt.TextIdentity(7), tt.TextIdentity(8)}) == 2


# --- pointer encoding -----------------------------------------------------


def test_pointer_encoding_is_the_gba_address_form():
    assert tt.encode_pointer(0x0005792C) == bytes.fromhex("2c790508")


def test_pointer_round_trips_through_a_synthetic_table():
    """A table entry decodes back to the offset it was built from."""
    image = bytearray(tt.TEXT_TABLE_START + 8)
    image[tt.TEXT_TABLE_START : tt.TEXT_TABLE_START + 4] = tt.encode_pointer(0x1234)
    assert tt.read_pointer(bytes(image), 0) == 0x1234


def test_pointer_outside_the_rom_window_is_refused():
    image = bytearray(tt.TEXT_TABLE_START + 8)
    image[tt.TEXT_TABLE_START : tt.TEXT_TABLE_START + 4] = (0x02000000).to_bytes(4, "little")
    with pytest.raises(tt.TextCodecError, match="not a GBA ROM address"):
        tt.read_pointer(bytes(image), 0)


def test_pointer_past_the_end_of_the_image_is_refused():
    with pytest.raises(tt.TextCodecError, match="out of bounds"):
        tt.read_pointer(b"\x00" * 16, 0)


# --- round trip over a constructed pool ----------------------------------


def test_a_constructed_pool_round_trips_in_full():
    """The whole-extent proof in miniature, with no ROM bytes involved.

    Includes every feature at once: plain text, an empty string, a newline, a
    non-ASCII codepoint, an unknown control operand and a literal brace.
    """
    pieces = [
        encoded("Start"),
        u16(0x0000),
        u16(0x0041, 0x000A, 0x0042, 0x0000),
        u16(0x0048, 0x00E9, 0x0000),
        u16(0x0008, 0x0042, 0x0058, 0x0000),
        encoded("{ok}"),
    ]
    pool = b"".join(pieces)

    rebuilt = b""
    offset = 0
    while offset < len(pool):
        text, offset = tt.decode_string(pool, offset)
        rebuilt += tt.encode_string(text)

    assert rebuilt == pool
