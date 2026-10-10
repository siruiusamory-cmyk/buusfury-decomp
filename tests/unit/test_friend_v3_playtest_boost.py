"""The playtest boost changes the maximum number of bytes, and only those bytes.

Two properties are pinned here beyond the stat fields:

  * the Bandana hook and its trampoline are the only other regions the builder may touch;
  * the trampoline's frame leaves LR on the stack for the init's own epilogue to pop into
    pc, and restores r0-r4 itself. An earlier version pushed r4, r5 and an epilogue address
    and popped {r4, r5, pc}, which handed pc the ORIGINAL r4. The word count stayed
    balanced, so only an order-aware assertion catches that.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.research.build_friend_v3_playtest_boost import (  # noqa: E402
    BANDANA_ID,
    BASE_STAT_COUNT,
    BASE_STAT_RECORD_SIZE,
    BASE_STAT_TABLE,
    BoostError,
    FIELD_OFFSETS,
    HOOK,
    HOOK_FILE,
    INIT_ADDRESS,
    MAXIMUM,
    PARTY_RECORDS,
    TRAMPOLINE,
    TRAMPOLINE_FILE,
    TRAMPOLINE_LENGTH,
    TRAMPOLINE_RETURN,
    _assert_only_declared_bytes_changed,
    bandana_patch,
    encode_bl,
    plan,
)


def synthetic_base() -> bytearray:
    """A base whose stat table is below maximum and which is large enough for the patch."""
    size = max(BASE_STAT_TABLE + BASE_STAT_COUNT * BASE_STAT_RECORD_SIZE, TRAMPOLINE_FILE + 64)
    base = bytearray(size)
    for index in range(BASE_STAT_COUNT):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for name, (rel, width) in FIELD_OFFSETS.items():
            value = 1 if name == "level" else 0
            base[record + rel:record + rel + width] = value.to_bytes(width, "little")
        base[record + 0x02:record + 0x04] = (0x1234).to_bytes(2, "little")
        base[record + 0x04:record + 0x06] = (0x5678).to_bytes(2, "little")
    return base


def _write(base: bytearray, record: int, field: str, value: int) -> None:
    rel, width = FIELD_OFFSETS[field]
    offset = BASE_STAT_TABLE + record * BASE_STAT_RECORD_SIZE + rel
    base[offset:offset + width] = value.to_bytes(width, "little")


def _half(patched: bytes, index: int) -> int:
    off = TRAMPOLINE_FILE + index * 2
    return int.from_bytes(patched[off:off + 2], "little")


def test_changed_bytes_are_the_stat_fields_plus_the_hook_and_trampoline() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)

    expected = set()
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for rel, width in FIELD_OFFSETS.values():
            expected.update(range(record + rel, record + rel + width))

    actual = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b}
    assert expected <= actual
    allowed = expected | set(range(HOOK_FILE, HOOK_FILE + 4)) | set(
        range(TRAMPOLINE_FILE, TRAMPOLINE_FILE + TRAMPOLINE_LENGTH[0])
    )
    assert actual <= allowed, sorted(actual - allowed)
    assert [entry["name"] for entry in changes] == ["Goku", "Gohan", "Goten", "Trunks", "Vegeta"]


def test_hp_and_ep_keep_their_bytes_because_0xFFFF_reads_as_negative() -> None:
    base = bytes(synthetic_base())
    boosted, _ = plan(base)
    for index in range(BASE_STAT_COUNT):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        assert boosted[record + 0x02:record + 0x04] == (0x1234).to_bytes(2, "little")
        assert boosted[record + 0x04:record + 0x06] == (0x5678).to_bytes(2, "little")


def test_every_party_field_is_written_at_its_maximum() -> None:
    boosted, _ = plan(bytes(synthetic_base()))
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for name, (rel, width) in FIELD_OFFSETS.items():
            got = int.from_bytes(boosted[record + rel:record + rel + width], "little")
            assert got == MAXIMUM[name]


def test_the_level_value_is_the_game_ceiling_and_not_the_u8_bound() -> None:
    assert MAXIMUM["level"] == 200
    boosted, _ = plan(bytes(synthetic_base()))
    assert boosted[BASE_STAT_TABLE] == 200


def test_fusion_and_non_party_records_are_untouched() -> None:
    base = bytes(synthetic_base())
    boosted, _ = plan(base)
    for index in (5, 6, 7, 8):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        assert boosted[record:record + BASE_STAT_RECORD_SIZE] == base[record:record + BASE_STAT_RECORD_SIZE]


def test_an_image_too_small_for_the_table_is_refused() -> None:
    with pytest.raises(BoostError, match="smaller than the character base-stat table"):
        plan(bytes(BASE_STAT_TABLE + 1))


def test_an_already_maxed_image_changes_only_the_hook_and_the_trampoline() -> None:
    base = bytearray(synthetic_base())
    for index in PARTY_RECORDS:
        for name, (_, width) in FIELD_OFFSETS.items():
            _write(base, index, name, MAXIMUM[name])
    boosted, _ = plan(bytes(base))
    changed = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b}
    allowed = set(range(HOOK_FILE, HOOK_FILE + 4)) | set(
        range(TRAMPOLINE_FILE, TRAMPOLINE_FILE + TRAMPOLINE_LENGTH[0])
    )
    assert changed <= allowed, sorted(changed - allowed)


def _operands(text: str) -> list[str]:
    """Register names from a capstone operand string like `{r4, pc}` or `r4, r5`."""
    import re

    return re.findall(r"r\d+|pc|lr|sp", text)


def _instructions(patched: bytes, count: int) -> list[tuple[int, str, list[str]]]:
    import capstone

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    blob = patched[TRAMPOLINE_FILE:TRAMPOLINE_FILE + count * 2]
    return [(ins.address, ins.mnemonic, _operands(ins.op_str)) for ins in md.disasm(blob, TRAMPOLINE)]


def _literal_value(patched: bytes, address: int) -> int:
    """What the PC-relative LDR at `address` reads, computed the way the processor does."""
    offset = address - TRAMPOLINE
    half = int.from_bytes(patched[TRAMPOLINE_FILE + offset:TRAMPOLINE_FILE + offset + 2], "little")
    literal = ((address + 4) & ~3) + (half & 0xFF) * 4
    return int.from_bytes(patched[literal - 0x08000000:literal - 0x08000000 + 4], "little")


def test_the_frame_delivers_the_epilogue_to_pc_and_restores_r4() -> None:
    """Decode which pushed word reaches which pop slot, using the disassembler's own operands.

    Asserting the emitted halfwords is not enough: two single-register pushes build the reverse
    of one merged push, and an earlier version sent the caller's r4 to pc while its halfword
    assertions still passed.
    """
    patched = bandana_patch(bytes(synthetic_base()))
    instructions = _instructions(patched, 12)

    pushed: list[str] = []
    popped: list[str] = []
    for _, mnemonic, operands in instructions:
        if mnemonic == "push":
            pushed += operands
        elif mnemonic == "pop":
            popped = operands
            break

    assert pushed, "no push found"
    assert popped, "no pop found"
    # A pop takes the lowest address first, and the last word pushed is at the lowest address.
    mapping = dict(zip(popped, reversed(pushed)))
    assert mapping.get("r4") == "r4", f"r4 receives {mapping.get('r4')}, not the caller's r4"
    assert "pc" in mapping, f"pc is not popped: {popped}"

    # Whatever register pc takes must be loaded from the epilogue literal before the pop.
    epilogue_reg = mapping["pc"]
    loads = [
        address
        for address, mnemonic, operands in instructions
        if mnemonic == "ldr" and operands and operands[0] == epilogue_reg
    ]
    assert loads, f"nothing loads {epilogue_reg}, the register pc takes"
    assert _literal_value(patched, loads[0]) == TRAMPOLINE_RETURN, (
        f"{epilogue_reg} holds {_literal_value(patched, loads[0]):#x}, not the epilogue"
    )


def test_the_gear_id_literal_lands_where_its_ldr_computes() -> None:
    patched = bandana_patch(bytes(synthetic_base()))
    off = TRAMPOLINE_FILE
    here = TRAMPOLINE + 0
    h = int.from_bytes(patched[off:off + 2], "little")
    literal = ((here + 4) & ~3) + (h & 0xFF) * 4
    got = int.from_bytes(patched[literal - 0x08000000:literal - 0x08000000 + 4], "little")
    assert got == BANDANA_ID, f"the gear id literal is {got:#x}, wanted {BANDANA_ID}"


def test_the_hook_branches_to_the_trampoline() -> None:
    patched = bandana_patch(bytes(synthetic_base()))
    assert patched[HOOK_FILE:HOOK_FILE + 4] == encode_bl(HOOK, TRAMPOLINE)


def test_the_trampoline_calls_the_add_routine() -> None:
    patched = bandana_patch(bytes(synthetic_base()))
    bl_at = TRAMPOLINE_FILE + 10
    assert patched[bl_at:bl_at + 4] == encode_bl(TRAMPOLINE + 10, INIT_ADDRESS)


def test_the_displaced_adds_is_replayed_before_and_after_the_call() -> None:
    """r0 is live at the continuation, so it is replayed after the call as well."""
    patched = bandana_patch(bytes(synthetic_base()))
    off = TRAMPOLINE_FILE
    assert int.from_bytes(patched[off + 8:off + 10], "little") == 0x1C20
    assert int.from_bytes(patched[off + 14:off + 16], "little") == 0x1C20


def test_a_byte_outside_the_declared_spans_is_refused() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)
    tampered = bytearray(boosted)
    stray = BASE_STAT_TABLE + 0x0C
    tampered[stray] ^= 0xFF
    with pytest.raises(BoostError, match="outside the declared spans"):
        _assert_only_declared_bytes_changed(base, bytes(tampered), changes)
