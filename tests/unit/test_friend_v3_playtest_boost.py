"""The playtest boost changes the maximum number of bytes, and only those bytes.

Two properties are pinned here beyond the stat fields:

  * the Bandana hook and its trampoline are the only other regions the builder may touch;
  * the trampoline's PUSH ORDER puts the epilogue address where the pop delivers it to pc.
    The earlier defect pushed r4, then r5, then the epilogue address and popped
    {r4, r5, pc}, which handed pc the original r4. The word count was balanced, so only an
    order-aware assertion catches it.
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


def test_the_trampoline_push_order_puts_the_epilogue_where_pc_reads_it() -> None:
    """Assert the ORDER, not the count: a balanced frame can still pop the wrong word."""
    patched = bandana_patch(bytes(synthetic_base()))
    assert _half(patched, 2) == 0xB410, f"+4 is not push {{r4}}: {_half(patched, 2):#06x}"
    assert _half(patched, 3) == 0xB420, f"+6 is not push {{r5}}: {_half(patched, 3):#06x}"
    assert _half(patched, 7) == 0xBD10, f"+14 is not pop {{r4, pc}}: {_half(patched, 7):#06x}"


def test_both_trampoline_literals_land_where_their_ldr_computes() -> None:
    patched = bandana_patch(bytes(synthetic_base()))
    for index, wanted in ((0, BANDANA_ID), (1, TRAMPOLINE_RETURN)):
        here = TRAMPOLINE + index * 2
        half = _half(patched, index)
        literal = ((here + 4) & ~3) + (half & 0xFF) * 4
        got = int.from_bytes(patched[literal - 0x08000000:literal - 0x08000000 + 4], "little")
        assert got == wanted, f"literal for +{index * 2} is {got:#x}, wanted {wanted:#x}"


def test_the_hook_branches_to_the_trampoline() -> None:
    patched = bandana_patch(bytes(synthetic_base()))
    assert patched[HOOK_FILE:HOOK_FILE + 4] == encode_bl(HOOK, TRAMPOLINE)


def test_the_trampoline_calls_the_add_routine() -> None:
    patched = bandana_patch(bytes(synthetic_base()))
    bl_at = TRAMPOLINE_FILE + 10
    assert patched[bl_at:bl_at + 4] == encode_bl(TRAMPOLINE + 10, INIT_ADDRESS)


def test_a_byte_outside_the_declared_spans_is_refused() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)
    tampered = bytearray(boosted)
    stray = BASE_STAT_TABLE + 0x0C
    tampered[stray] ^= 0xFF
    with pytest.raises(BoostError, match="outside the declared spans"):
        _assert_only_declared_bytes_changed(base, bytes(tampered), changes)
