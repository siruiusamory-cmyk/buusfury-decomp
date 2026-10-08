"""The token engine builder may never write its own source image.

DIALOGUE-TOKEN-PRODUCTIZATION-001. The first candidate's guard compared resolved
paths, which cannot see a hard-link alias; the second staged through a predictable
`<destination>.partial` name, which an alias could also occupy. Both are
regression cases here.

The guard runs before the source is read or parsed, so these tests need no image:
any file will do, and the refusal is asserted on the message the repository's own
alias rule produces.
"""

from __future__ import annotations

import os

import pytest

from tools.research.build_dialogue_token_engine import Emitter, bl_decode, bl_encode, patch


def test_refuses_a_destination_that_is_the_source(tmp_path) -> None:
    source = tmp_path / "image.gba"
    source.write_bytes(b"an image")
    with pytest.raises(SystemExit, match="input image"):
        patch(source, source, "unused")
    assert source.read_bytes() == b"an image"


def test_refuses_a_hard_link_alias_of_the_source(tmp_path) -> None:
    source = tmp_path / "image.gba"
    source.write_bytes(b"an image")
    alias = tmp_path / "alias.gba"
    try:
        os.link(source, alias)
    except OSError:
        pytest.skip("this filesystem cannot make a hard link")
    with pytest.raises(SystemExit, match="input image"):
        patch(source, alias, "unused")
    assert source.read_bytes() == b"an image"


def test_refuses_a_destination_reached_through_a_relative_spelling(tmp_path) -> None:
    source = tmp_path / "image.gba"
    source.write_bytes(b"an image")
    spelled = tmp_path / "." / "image.gba"
    with pytest.raises(SystemExit, match="input image"):
        patch(source, spelled, "unused")
    assert source.read_bytes() == b"an image"


# --- the cave's encoder -------------------------------------------------------
#
# bl_encode is what turns a branch into bytes, and the whole cave rests on it: a
# wrong encoding is not a wrong answer, it is an undefined instruction or a branch
# into the wrong place. It is pure arithmetic, so it is tested directly rather than
# only through a built image.


def test_a_thumb_bl_round_trips_across_its_whole_range() -> None:
    origin = 0x08000000
    for offset in (-(1 << 22) + 4, -0x2E21AA, -4, 4, 0x2E22D2, (1 << 22) - 4):
        high, low = bl_encode(origin, origin + 4 + offset)
        assert bl_decode(origin, high, low) == origin + 4 + offset


def test_a_thumb_bl_matches_its_hand_computed_encoding() -> None:
    """The round trip above compares the encoder with its own decoder.

    This states the encoding independently, from the ARMv7-M manual's T1 layout for
    the ARMv4T 23-bit BL: 11110 S imm10 in the first halfword and 11111 imm11 in the
    second, where the J1 and J2 bits of the Thumb-2 form are both 1 here. A
    displacement of +4 halfwords is S=0, imm10=0, imm11=2.
    """
    origin = 0x08000000
    assert bl_encode(origin, origin + 4 + 4) == (0xF000, 0xF802)
    assert bl_encode(origin, origin + 4 - 4) == (0xF7FF, 0xFFFE)


def test_a_thumb_bl_refuses_a_displacement_arm7tdmi_cannot_decode() -> None:
    origin = 0x08000000
    with pytest.raises(ValueError) as caught:
        bl_encode(origin, origin + 4 + (1 << 22))
    assert "23-bit range" in str(caught.value)
    with pytest.raises(ValueError):
        bl_encode(origin, origin + 4 + 1)          # unaligned


def test_a_conditional_branch_offset_is_signed() -> None:
    """The Thumb B<cond> offset is a signed 8-bit halfword count: -128..127.

    An earlier range check accepted 0..255, so a forward branch of 128 halfwords or
    more would have encoded as a BACKWARD one.
    """
    site = 0x08000000
    forward_max = site + 4 + 127 * 2
    backward_max = site + 4 - 128 * 2
    assert Emitter._branch_word(0x0, site, forward_max) == 0xD000 | 0x7F
    assert Emitter._branch_word(0x0, site, backward_max) == 0xD000 | 0x80
    for target in (site + 4 + 128 * 2, site + 4 - 129 * 2):
        with pytest.raises(SystemExit):
            Emitter._branch_word(0x0, site, target)
