"""The playtest boost changes the maximum number of bytes, and only those bytes.

The synthetic base carries every record at a value that is not the maximum, so a
builder that skipped a field, wrote a field twice, or patched outside the five
fields it declares is caught here rather than on a real image. The sentinel in
the hp and ep fields is there because those two are deliberately not written:
writing 0xFFFF into them read back as HP -1 and EP -5 on a live character.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.research.build_friend_v3_playtest_boost import (  # noqa: E402
    BASE_STAT_COUNT,
    BASE_STAT_RECORD_SIZE,
    BASE_STAT_TABLE,
    BoostError,
    FIELD_OFFSETS,
    MAXIMUM,
    PARTY_RECORDS,
    _assert_only_declared_bytes_changed,
    plan,
)


def synthetic_base() -> bytearray:
    """An image whose base-stat table is entirely at a non-maximum value."""
    base = bytearray(BASE_STAT_TABLE + BASE_STAT_COUNT * BASE_STAT_RECORD_SIZE)
    for index in range(BASE_STAT_COUNT):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for name, (rel, width) in FIELD_OFFSETS.items():
            value = 1 if name == "level" else 0
            base[record + rel:record + rel + width] = value.to_bytes(width, "little")
        # The two fields the boost must never touch, at a value no candidate uses.
        base[record + 0x02:record + 0x04] = (0x1234).to_bytes(2, "little")
        base[record + 0x04:record + 0x06] = (0x5678).to_bytes(2, "little")
    return base


def _write(base: bytearray, record: int, field: str, value: int) -> None:
    rel, width = FIELD_OFFSETS[field]
    offset = BASE_STAT_TABLE + record * BASE_STAT_RECORD_SIZE + rel
    base[offset:offset + width] = value.to_bytes(width, "little")


def test_changed_bytes_are_exactly_the_declared_fields() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)

    expected = set()
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for rel, width in FIELD_OFFSETS.values():
            expected.update(range(record + rel, record + rel + width))

    actual = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b}
    assert actual == expected
    assert len(actual) == 25  # five records, five single-byte fields
    assert [entry["name"] for entry in changes] == ["Goku", "Gohan", "Goten", "Trunks", "Vegeta"]


def test_hp_and_ep_keep_their_bytes_because_0xFFFF_reads_as_negative() -> None:
    """The regression this guards: a live character read HP -1 and EP -5."""
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


def test_a_byte_outside_the_declared_spans_is_refused() -> None:
    """The guard's only reachable case: a write the field table did not declare."""
    base = bytes(synthetic_base())
    boosted, changes = plan(base)
    tampered = bytearray(boosted)
    stray = BASE_STAT_TABLE + 0x0C  # inside a record, outside every declared field
    tampered[stray] ^= 0xFF
    with pytest.raises(BoostError, match="outside the declared spans"):
        _assert_only_declared_bytes_changed(base, bytes(tampered), changes)


def test_an_image_too_small_for_the_table_is_refused() -> None:
    with pytest.raises(BoostError, match="smaller than the character base-stat table"):
        plan(bytes(BASE_STAT_TABLE + 1))


def test_an_already_maxed_image_produces_no_change() -> None:
    base = bytearray(synthetic_base())
    for index in PARTY_RECORDS:
        for name, (_, width) in FIELD_OFFSETS.items():
            _write(base, index, name, MAXIMUM[name])
    boosted, _ = plan(bytes(base))
    assert boosted == bytes(base)
