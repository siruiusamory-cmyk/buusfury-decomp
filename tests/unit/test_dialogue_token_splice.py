"""The rename splice: every replacement must be the length of what it replaces.

DIALOGUE-TOKEN-PRODUCTIZATION-001. The property under test is the one that keeps a
rename from moving any other word in the image: a replacement occupies exactly as
many units as the text it replaces, so no prefix of a record changes length and no
offset in the container moves. Nothing here needs a ROM - the substitution table,
the regions and the encoder are pure functions of the two texts and the dictionary.
"""

from __future__ import annotations

import pytest

from tools.research.splice_dialogue_tokens import (SpliceError, encode_record,
                                                   local_replacement,
                                                   substitution_regions,
                                                   substitution_table)
from tools.webfoot.token_dictionary import TokenDictionary

DICTIONARY = TokenDictionary(("Ya", "ha", "Kr", "in", "Ti", "YA", "HA", "KR", "IN", "TI"))


def row(old: str, new: str) -> dict:
    return {"old_selector": 0, "old_start": 0, "old_length": len(old) * 2,
            "old_text": old, "new_text": new}


def test_a_growing_name_is_paid_for_inside_the_name() -> None:
    """Goku -> Yamcha grows by two; "Ya" and "ha" inside it pay for exactly that."""
    replacement = local_replacement("Goku", "Yamcha", DICTIONARY)
    assert len(replacement) == len("Goku")
    from tools.webfoot.token_dictionary import decode_text
    assert decode_text(replacement, DICTIONARY) == "Yamcha"


def test_a_shrinking_name_is_paid_for_with_spaces_right_after_it() -> None:
    replacement = local_replacement("Trunks", "Uub", DICTIONARY)
    assert len(replacement) == len("Trunks")
    assert replacement == "Uub   "


def test_a_same_length_name_is_left_alone() -> None:
    assert local_replacement("Goten", "Videl", DICTIONARY) == "Videl"


def test_a_growth_the_dictionary_cannot_pay_for_is_refused() -> None:
    """Fail closed rather than pad a growth, which no amount of spaces can fix."""
    with pytest.raises(Exception) as caught:
        local_replacement("Goku", "Yamcha", TokenDictionary(("zz", "qq")))
    assert "cannot close the record" in str(caught.value)


def test_the_table_is_taken_from_the_map_and_must_be_consistent() -> None:
    consistent = substitution_table({"a": row("Goku learned it", "Yamcha learned it")})
    assert consistent == {"Goku": "Yamcha"}
    with pytest.raises(SpliceError) as caught:
        substitution_table({"a": row("Goku learned it", "Yamcha learned it"),
                            "b": row("Goku learned it", "Krillin learned it")})
    assert "can only apply one of them" in str(caught.value)


def test_regions_name_the_positions_that_may_differ() -> None:
    regions = substitution_regions("Goku learned Instant", "Yamcha learned Instant",
                                  DICTIONARY, {"Goku": "Yamcha"})
    assert len(regions) == 1
    start, length, replacement = regions[0]
    assert (start, length) == (0, 4)
    assert len(replacement) == 4


def test_a_multi_word_substitution_is_one_region() -> None:
    old, new = "Android 18 wins", "Chi-Chi wins"
    regions = substitution_regions(old, new, DICTIONARY, {"Android 18": "Chi-Chi"})
    assert len(regions) == 1
    start, length, replacement = regions[0]
    assert old[start:start + length] == "Android 18"
    assert len(replacement) == len("Android 18")


def test_the_encoded_record_is_the_same_length_as_retail() -> None:
    old = "Goku learned Instant Transmission Level 2!"
    new = "Yamcha learned Instant Transmission Level 2!"
    text, method = encode_record(row(old, new), DICTIONARY,
                                 substitution_table({"a": row(old, new)}))
    assert len(text) == len(old)
    assert method == "tokenised"


def test_every_prefix_including_the_name_is_the_retail_length() -> None:
    """The strong form: not just the total, but every prefix.

    A record's total length being right is not enough - the first version of this
    code padded at the END, which kept the total and slid every character after the
    name. This asserts the property that actually prevents that.
    """
    old = "Goku learned it. Gohan too."
    new = "Yamcha learned it. Krillin too."
    text, _ = encode_record(row(old, new), DICTIONARY,
                            substitution_table({"a": row(old, new)}))
    assert len(text) == len(old)
    # Every substitution region must be length-neutral, which is what makes every
    # prefix neutral.
    regions = substitution_regions(old, new, DICTIONARY,
                                   substitution_table({"a": row(old, new)}))
    for start, length, replacement in regions:
        assert len(replacement) == length


def test_text_outside_the_substitutions_is_copied_character_for_character() -> None:
    old = "Goku learned it. Gohan too."
    new = "Yamcha learned it. Krillin too."
    table = substitution_table({"a": row(old, new)})
    text, _ = encode_record(row(old, new), DICTIONARY, table)
    for start, length, replacement in substitution_regions(old, new, DICTIONARY, table):
        assert len(replacement) == length
    # Cut each region out of both texts and the remainders must be identical.
    def remainder(source: str) -> str:
        out, position = [], 0
        for start, length, _ in substitution_regions(old, new, DICTIONARY, table):
            out.append(source[position:start])
            position = start + length
        out.append(source[position:])
        return "".join(out)
    assert remainder(text) == remainder(old)


def test_the_encoder_refuses_a_substitution_the_map_does_not_perform() -> None:
    old, new = "Goku wins", "Yamcha wins"
    with pytest.raises(SpliceError):
        encode_record(row(old, new), DICTIONARY, {"Vegeta": "Tien"})


@pytest.mark.parametrize("old,new", [("Goku", "Yamcha"), ("Trunks", "Uub"),
                                     ("Goten", "Videl")])
def test_a_reserved_code_point_in_the_map_is_refused_on_every_path(old: str,
                                                                   new: str) -> None:
    """Growth, shrink and same-length all take the same refusal.

    Only the growth path used to check, so a U+E000..U+E0FF character in a map
    reached the image as text on the other two.
    """
    planted = new[:1] + chr(0xE000) + new[1:]
    with pytest.raises(Exception) as caught:
        local_replacement(old, planted, DICTIONARY)
    assert "cannot be authored" in str(caught.value)
