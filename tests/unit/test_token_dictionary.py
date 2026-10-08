"""The expansion-token dictionary: every rule is a refusal, and each is asserted.

DIALOGUE-TOKEN-PRODUCTIZATION-001. The shipped module is
`tools.webfoot.token_dictionary`; the contract it implements is measured and
recorded in `docs/research/DIALOGUE_EXPANSION_TOKEN_DESIGN.md` sections 3, 4, 5,
8 and 14. Nothing here needs a ROM: the blob, the document and the encoder are
pure data, and the one image-dependent rule is driven through the `has_glyph`
seam the build passes in.

One case per rule, and the message is asserted rather than the exception type, so
a rule that starts reporting the wrong reason fails here.
"""

from __future__ import annotations

import pytest

from tools.webfoot.token_dictionary import (ENTRY_STRIDE_HALFWORDS, LINE_WIDTH_FLOOR,
                                            MAX_TOKENS, TERMINATOR, TOKEN_BASE,
                                            TokenDictionary, TokenDictionaryError,
                                            assert_authored_text, build_blob,
                                            check_widths, decode_blob, decode_text,
                                            encode_text, encode_to_length,
                                            expansion_advance, glyph_admissible,
                                            token_unit)

#: The allocation this ticket verifies: the five approved two-glyph expansions and
#: the uppercase forms the all-caps records need. Ten entries, one page of ids.
APPROVED = ("Ya", "ha", "Kr", "in", "Ti")
UPPERCASE = ("YA", "HA", "KR", "IN", "TI")


def dictionary(*expansions: str) -> TokenDictionary:
    return TokenDictionary(tuple(expansions) if expansions else APPROVED)


def expect(blob: bytes, fragment: str, has_glyph=None) -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        decode_blob(blob, has_glyph=has_glyph)
    assert fragment in str(caught.value), str(caught.value)


# --- the blob -----------------------------------------------------------------


def test_the_approved_allocation_round_trips_through_its_blob() -> None:
    source = dictionary(*APPROVED, *UPPERCASE)
    blob = build_blob(source)
    assert len(blob) == 12 + source.count * ENTRY_STRIDE_HALFWORDS * 2
    assert decode_blob(blob) == source


def test_entry_i_is_the_unit_e000_plus_i_in_document_order() -> None:
    source = dictionary("Kr", "in")
    assert [entry.unit for entry in source.entries()] == [TOKEN_BASE, TOKEN_BASE + 1]
    assert source.unit_for("in") == token_unit(1)
    assert source.unit_for("ZZ") is None


def test_a_blob_without_its_magic_is_refused() -> None:
    blob = build_blob(dictionary())
    expect(b"XXXX" + blob[4:], "wrong magic")


def test_a_blob_from_another_version_is_refused() -> None:
    blob = bytearray(build_blob(dictionary()))
    blob[4] = 2
    expect(bytes(blob), "unsupported dictionary version/flags")


def test_a_blob_with_another_stride_is_refused() -> None:
    blob = bytearray(build_blob(dictionary()))
    blob[9] = 3
    expect(bytes(blob), "stride or max glyphs")


def test_a_count_above_the_window_is_refused() -> None:
    blob = bytearray(build_blob(dictionary()))
    blob[6:8] = (MAX_TOKENS + 1).to_bytes(2, "little")
    expect(bytes(blob), "above the 256 window")


def test_a_length_that_disagrees_with_the_header_is_refused() -> None:
    expect(build_blob(dictionary()) + b"\x00\x00", "length does not match its header")


def test_an_entry_without_a_terminator_is_refused() -> None:
    blob = (b"DTKN" + bytes([1, 0]) + (1).to_bytes(2, "little")
            + bytes([3, ENTRY_STRIDE_HALFWORDS]) + bytes([0, 0])
            + b"".join(value.to_bytes(2, "little")
                       for value in (0x41, 0x42, TERMINATOR, TERMINATOR)))
    assert decode_blob(blob).expansions == ("AB",)
    # Fill both terminator halfwords (entry offset 12, halfwords 2 and 3 at 16 and
    # 18) with glyphs: the entry is then four glyphs with no terminator at all.
    missing = bytearray(blob)
    missing[16:18] = (0x0043).to_bytes(2, "little")
    missing[18:20] = (0x0044).to_bytes(2, "little")
    expect(bytes(missing), "terminator")


# --- the entries --------------------------------------------------------------


def test_a_one_glyph_expansion_is_refused() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        TokenDictionary(("a",))
    assert "holds 1 glyphs" in str(caught.value)


def test_a_four_glyph_expansion_is_refused() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        TokenDictionary(("abcd",))
    assert "1..3" not in str(caught.value) and "holds 4 glyphs" in str(caught.value)


def test_a_glyph_at_the_wide_class_threshold_is_refused() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        TokenDictionary(("A\u00ff",))
    assert "wide-class threshold" in str(caught.value)


def test_a_stream_control_inside_an_expansion_is_refused() -> None:
    for control in (0x0A, 0x0B, 0x20, 0x2D, 0x08, 0x00):
        assert not glyph_admissible(control)
        with pytest.raises(TokenDictionaryError) as caught:
            TokenDictionary(("A" + chr(control),))
        assert "instruction rather than as text" in str(caught.value)


def test_a_glyph_with_no_glyph_record_is_refused_by_the_build() -> None:
    source = dictionary("Ya")
    with pytest.raises(TokenDictionaryError) as caught:
        build_blob(source, has_glyph=lambda glyph: glyph != ord("a"))
    assert "has no glyph record" in str(caught.value)
    assert build_blob(source, has_glyph=lambda glyph: True)


def test_two_expansions_with_the_same_text_are_refused() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        dictionary("in", "in")
    assert "share the same text" in str(caught.value)


def test_a_character_outside_the_basic_plane_is_refused() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        TokenDictionary(("\U0001F600x",))
    assert "basic multilingual plane" in str(caught.value)


def test_more_expansions_than_the_window_holds_are_refused() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        TokenDictionary(tuple(f"a{chr(0x61 + index % 26)}{index}"[:3]
                              for index in range(MAX_TOKENS + 1)))
    assert "exceed the 256-token window" in str(caught.value)


# --- the document -------------------------------------------------------------


def test_the_document_is_a_list_of_text_tables_in_file_order() -> None:
    from tools.webfoot.token_dictionary import (dictionary_from_document,
                                                dictionary_to_document)
    document = {"token": [{"text": "Ya"}, {"text": "in"}]}
    assert dictionary_from_document(document) == dictionary("Ya", "in")
    assert dictionary_to_document(dictionary("Ya", "in")) == document


def test_a_document_token_without_text_is_refused() -> None:
    from tools.webfoot.token_dictionary import dictionary_from_document
    with pytest.raises(TokenDictionaryError) as caught:
        dictionary_from_document({"token": [{"glyph": 0x41}]})
    assert "needs a string 'text'" in str(caught.value)


def test_a_document_that_is_not_a_list_of_tables_is_refused() -> None:
    from tools.webfoot.token_dictionary import dictionary_from_document
    with pytest.raises(TokenDictionaryError) as caught:
        dictionary_from_document({"token": "Ya"})
    assert "not a list of tables" in str(caught.value)


# --- the window is refused in authored text -----------------------------------


@pytest.mark.parametrize("unit", [TOKEN_BASE, TOKEN_BASE + 1, TOKEN_BASE + MAX_TOKENS - 1])
def test_authored_text_may_not_contain_the_token_window(unit: int) -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        assert_authored_text(f"nice {chr(unit)}", what="the replacement")
    assert "reserved code point" in str(caught.value)
    assert "the replacement" in str(caught.value)
    assert_authored_text("nice text")


def test_the_encoder_refuses_authored_text_that_already_holds_a_token() -> None:
    with pytest.raises(TokenDictionaryError):
        encode_text(f"a{chr(TOKEN_BASE)}b", dictionary())


def test_the_dialogue_validator_refuses_the_window_as_a_product_error() -> None:
    """The seat every authoring entry point already funnels through."""
    from tools.webfoot.compressed_dialogue import AUTHORED_DIALOGUE_TARGETS
    from tools.webfoot.dialogue import validate_dialogue_replacement

    target = next(iter(AUTHORED_DIALOGUE_TARGETS.values()))
    refused = validate_dialogue_replacement(target, f"Nice work{chr(TOKEN_BASE)}, Goku!")
    assert not refused.valid
    assert refused.problems[0].code == "reserved_token_window"
    assert "cannot be authored" in refused.problems[0].message
    assert validate_dialogue_replacement(target, "Nice work, Goku!").valid


# --- the encoder --------------------------------------------------------------


def test_the_encoder_matches_longest_first_and_never_overlaps() -> None:
    source = TokenDictionary(("ab", "abc"))
    assert encode_text("abcab", source) == f"{token_unit(1)}{token_unit(0)}"


def test_the_encoder_round_trips_every_approved_expansion() -> None:
    source = dictionary(*APPROVED, *UPPERCASE)
    text = "Yamcha and Krillin are in Tien, YAMCHA and KRILLIN too"
    encoded = encode_text(text, source)
    assert len(encoded) < len(text)
    assert decode_text(encoded, source) == text


def test_a_unit_in_the_window_with_no_entry_fails_closed() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        decode_text(f"a{chr(TOKEN_BASE + 5)}", dictionary("Ya", "ha"))
    assert "only 2 entries" in str(caught.value)


def test_an_empty_dictionary_encodes_to_the_same_text() -> None:
    assert encode_text("Yamcha", TokenDictionary(())) == "Yamcha"


# --- landing exactly on a record's length -------------------------------------


def test_the_encoder_lands_exactly_on_the_target_unit_count() -> None:
    source = dictionary(*APPROVED, *UPPERCASE)
    for text, target in (("Yamcha learned it", 16), ("in in in", 5),
                         ("KRILLIN and YAMCHA", 17)):
        encoded = encode_to_length(text, source, target)
        assert len(encoded) == target
        assert decode_text(encoded, source) == text


def test_a_target_longer_than_the_text_is_refused_rather_than_padded() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        encode_to_length("Yamcha", dictionary(), 8)
    assert "already shorter" in str(caught.value)


def test_a_text_that_cannot_close_its_record_is_refused_by_name() -> None:
    with pytest.raises(TokenDictionaryError) as caught:
        encode_to_length("Yamcha Yamcha", dictionary("in"), 5)
    assert "cannot close the record" in str(caught.value)


def test_a_three_glyph_entry_that_would_overshoot_is_skipped() -> None:
    source = TokenDictionary(("the", "in"))
    # "the" would save two units and overshoot a one-unit target, so the encoder
    # falls through to the two-glyph entry at the end of the word instead.
    encoded = encode_to_length("thein", source, 4)
    assert encoded == f"the{token_unit(1)}"
    assert decode_text(encoded, source) == "thein"


def test_a_target_equal_to_the_text_is_returned_untouched() -> None:
    assert encode_to_length("Yamcha", dictionary(), 6) == "Yamcha"


# --- the width rule -----------------------------------------------------------


def test_an_expansion_wider_than_the_narrowest_line_is_refused() -> None:
    narrow = lambda glyph: 40  # noqa: E731 - a width function, not a name
    with pytest.raises(TokenDictionaryError) as caught:
        check_widths(TokenDictionary(("abc",)), narrow)
    assert f"over the {LINE_WIDTH_FLOOR} px narrowest line" in str(caught.value)
    assert expansion_advance("abc", narrow) == 123


def test_an_expansion_that_fits_the_narrowest_line_is_accepted() -> None:
    assert expansion_advance("Ya", lambda glyph: 9) == 20
    check_widths(dictionary(*APPROVED, *UPPERCASE), lambda glyph: 11)
