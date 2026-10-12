"""The one-shot palette write and the draw-loop bank lookup, with no ROM and no emulator.

What is checked, and why each check exists:

* every instruction of both hand-assembled stubs is asserted against a disassembly (P-083), and the
  verifier is shown to be live by feeding it a wrong halfword;
* the Thumb `bl` encoder round-trips through the decoder, because a wrong J1/J2 pair found a target 8 MB
  away while looking like a healthy stub;
* the hook replaces exactly the four bytes of the scene loader's OBJ palette copy and refuses any image
  whose call, literals or continuation are not the measured ones;
* the palette-RAM marker is one constant, shared by the writer and the body, and the body's fallback arm
  still sets bank 0 when no marker is found.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import palette_oneshot as oneshot  # noqa: E402
from tools.research import palette_writer as writer  # noqa: E402

CODE = 0x08900000
PALETTES = 0x088FF000
BODY = 0x08901000


def decoder():
    pytest.importorskip("capstone", reason="the project disassembler needs capstone")
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    return Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def listing(code: bytes, address: int) -> list[tuple[str, str]]:
    return [(instruction.mnemonic, instruction.op_str) for instruction in decoder().disasm(code, address)]


def test_every_one_shot_instruction_is_the_intended_one() -> None:
    code = oneshot.assemble(CODE, PALETTES)
    assert writer.disassemble(code, CODE), "an empty disassembly is not a pass"


def test_a_wrong_halfword_is_caught_before_it_reaches_an_image(monkeypatch) -> None:
    """The verifier must be live: a one-bit change in one entry has to fail the assembly."""
    want = oneshot.steps(oneshot.DEFAULT_MINIMUM_USED)

    def corrupted(minimum_used: int):
        steps = list(want)
        for index, step in enumerate(steps):
            if step[0] == "word" and step[2] == "movs" and step[3] == "r4, #0":
                steps[index] = ("word", 0x2401, "movs", "r4, #0")
        return steps

    monkeypatch.setattr(oneshot, "steps", corrupted)
    with pytest.raises(AssertionError, match="expected `movs r4, #0`"):
        oneshot.assemble(CODE, PALETTES)


def test_the_one_shot_calls_the_engine_copy_and_returns_to_the_loader() -> None:
    code = oneshot.assemble(CODE, PALETTES)
    decoded = listing(code, CODE)
    assert decoded[0] == ("push", "{r4, r5, r6, r7, lr}")
    assert decoded[1] == ("bl", f"#0x{oneshot.COPY_VENEER:x}"), (
        "the stub performs the OBJ palette copy it replaced")
    literals = [struct.unpack_from("<I", code, offset)[0] for offset in range(0, len(code) - 3, 4)]
    for value in (oneshot.OBJ_PALETTE_RAM, oneshot.OAM, oneshot.OBJ_VRAM, PALETTES,
                  oneshot.RESUME | 1):
        assert value in literals, f"literal 0x{value:08X} is not in the stub"
    assert ("bx", "r3") in decoded, "the stub ends by branching to the loader's continuation"


def test_the_thumb_bl_encoder_round_trips_through_the_decoder() -> None:
    """Both directions of the sign, and a target near the reach limit, all decoded back exactly."""
    for target in (0x08049144, 0x0800658A, CODE + 0x00E00000, CODE - 0x00E00000):
        encoded = oneshot.thumb_bl(CODE, target)
        decoded = list(decoder().disasm(encoded, CODE))
        assert len(decoded) == 1 and decoded[0].mnemonic == "bl"
        assert int(decoded[0].op_str[1:], 16) == target, f"bl to 0x{target:08X} decoded elsewhere"
    with pytest.raises(ValueError):
        oneshot.thumb_bl(CODE, CODE + (1 << 24) + 4)


def test_the_hook_replaces_only_the_palette_copy_call() -> None:
    image = planted()
    before = bytes(image[oneshot.RESUME - oneshot.ROM_BASE:oneshot.RESUME - oneshot.ROM_BASE + 4])
    replaced = oneshot.hook(image, STUB)
    assert replaced == oneshot.EXPECTED_HOOK
    assert bytes(image[0x6586:0x658A]) != oneshot.EXPECTED_HOOK, "the retail call must be gone"
    decoded = list(decoder().disasm(bytes(image[0x6586:0x658A]), oneshot.HOOK_SITE))
    assert decoded[0].mnemonic == "bl" and int(decoded[0].op_str[1:], 16) == STUB
    assert bytes(image[oneshot.RESUME - oneshot.ROM_BASE:oneshot.RESUME - oneshot.ROM_BASE + 4]) == before


STUB = 0x08008000
ROM_BASE = oneshot.ROM_BASE


def planted() -> bytearray:
    """A blank image carrying the measured bytes of the scene palette loader's OBJ copy."""
    image = bytearray(0x9000)
    image[0x6586:0x658A] = oneshot.EXPECTED_HOOK
    struct.pack_into("<I", image, oneshot.LITERAL_TABLE_SITE - ROM_BASE, oneshot.OBJ_PALETTE_TABLE)
    struct.pack_into("<I", image, oneshot.LITERAL_RAM_SITE - ROM_BASE, oneshot.OBJ_PALETTE_RAM)
    image[oneshot.RESUME - ROM_BASE:oneshot.RESUME - ROM_BASE + 4] = oneshot.EXPECTED_RESUME
    return image


def test_the_hook_refuses_an_image_that_is_not_the_measured_site() -> None:
    image = planted()
    image[0x6586] = 0x43
    with pytest.raises(AssertionError, match="not the retail call"):
        oneshot.hook(image, STUB)
    for offset in (oneshot.LITERAL_TABLE_SITE, oneshot.LITERAL_RAM_SITE):
        image = planted()
        struct.pack_into("<I", image, offset - ROM_BASE, 0xDEADBEEF)
        with pytest.raises(AssertionError, match="literals"):
            oneshot.hook(image, STUB)
    image = planted()
    image[oneshot.RESUME - ROM_BASE] = 0x01
    with pytest.raises(AssertionError, match="does not return"):
        oneshot.hook(image, STUB)


def test_the_hook_refuses_a_stub_it_cannot_reach() -> None:
    with pytest.raises(AssertionError, match="cannot reach"):
        oneshot.hook(planted(), 0x0A006586)


def test_the_marker_is_one_constant_shared_by_the_writer_and_the_body() -> None:
    assert oneshot.MARKER_BASE == writer.MARKER_BASE
    text = oneshot.assemble(CODE, PALETTES).hex()
    assert "4b23" in text and "1b02" in text, "the marker base is built from 0x4b shifted left by 8"
    for index in (1, 2, 3):
        assert f"{index:02x}33" in text, (
            f"the marker for index {index} is not written (adds r3, #{index} follows the shift)")


def test_the_body_writes_the_bank_and_falls_back_to_bank_zero() -> None:
    listing_ = listing(writer.assemble(BODY), BODY)
    operands = [operands for _, operands in listing_]
    index = operands.index("r3, [r5, #4]")
    assert listing_[index - 1] == ("movs", "r2, #0"), (
        "the no-marker path must reach the OAM write holding bank 0: that is the coded 16-colour mapping")
    assert ("lsls", "r2, r2, #0xc") in listing_, "the bank does not reach attr2"
    assert ("bx", "r4") in listing_, "the body must resume absolutely"
    assert ("bx", "lr") not in listing_, (
        "lr is live draw-loop state at the resume address, so the return cannot use it")


def test_the_8bpp_tile_scan_uses_the_hardware_slot_addressing() -> None:
    """A tile number indexes 32-byte slots and an 8bpp tile's low bit is ignored: (tile & ~1) * 32.

    `tile * 64` reads a neighbouring tile, so the occupancy scan would name the wrong banks and the
    picker could hand the character a bank something visible is already drawing from. P-103.
    """
    text = [f"{mnemonic} {operands}" for mnemonic, operands in listing(oneshot.assemble(CODE, PALETTES), CODE)]
    index = text.index("lsrs r3, r3, #0x16")
    assert text[index + 1] == "lsrs r3, r3, #1", "the low bit of the tile number must be cleared"
    assert text[index + 2] == "lsls r3, r3, #6", "then the slot stride is 32 bytes, so shift 6 after shift 1"


def test_the_picker_rule_is_the_lowest_free_banks_and_a_short_scene_writes_nothing() -> None:
    """The measured map-137 runtime free set (8, 10, 11, 14, 15) is the case with evidence behind it."""
    measured_used = 0
    for bank in range(16):
        if bank not in (8, 10, 11, 14, 15):
            measured_used |= 1 << bank
    assert oneshot.free_banks(measured_used) == [8, 10, 11]
    assert oneshot.free_banks(0) == [0, 1, 2], "an empty mask must never be trusted: the guard runs first"
    nearly_full = 0xFFFF & ~(1 << 15)
    assert oneshot.free_banks(nearly_full) == [15], "fewer than three free banks is not three"
    assert oneshot.free_banks(0xFFFF) == []
