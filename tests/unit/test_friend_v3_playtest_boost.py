"""The playtest boost changes the maximum number of bytes, and only those bytes.

The synthetic base carries every record at a non-maximum value, so a builder
that skipped a field, wrote a field twice, or patched outside the six fields it
declares is caught here rather than on a real image.
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
    plan,
)


def synthetic_base() -> bytearray:
    """An image whose base-stat table is entirely at a non-maximum value."""
    base = bytearray(BASE_STAT_TABLE + BASE_STAT_COUNT * BASE_STAT_RECORD_SIZE)
    for index in range(BASE_STAT_COUNT):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for name, (rel, width, _) in FIELD_OFFSETS.items():
            value = 1 if name == "level" else 0
            base[record + rel:record + rel + width] = value.to_bytes(width, "little")
    return base


def test_changed_bytes_are_exactly_the_declared_fields() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)

    expected = set()
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for rel, width, _ in FIELD_OFFSETS.values():
            expected.update(range(record + rel, record + rel + width))

    actual = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b}
    assert actual == expected
    assert len(actual) == 5 * 9
    assert [entry["name"] for entry in changes] == ["Goku", "Gohan", "Goten", "Trunks", "Vegeta"]


def test_every_party_field_is_written_at_its_maximum() -> None:
    boosted, _ = plan(bytes(synthetic_base()))
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for name, (rel, width, _) in FIELD_OFFSETS.items():
            got = int.from_bytes(boosted[record + rel:record + rel + width], "little")
            assert got == MAXIMUM[name]


def test_fusion_and_non_party_records_are_untouched() -> None:
    base = bytes(synthetic_base())
    boosted, _ = plan(base)
    for index in (5, 6, 7, 8):
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        assert boosted[record:record + BASE_STAT_RECORD_SIZE] == base[record:record + BASE_STAT_RECORD_SIZE]


def test_an_image_too_small_for_the_table_is_refused() -> None:
    with pytest.raises(BoostError, match="smaller than the character base-stat table"):
        plan(bytes(BASE_STAT_TABLE + 1))


def test_an_already_maxed_image_produces_no_change() -> None:
    base = bytearray(synthetic_base())
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for name, (rel, width, _) in FIELD_OFFSETS.items():
            base[record + rel:record + rel + width] = MAXIMUM[name].to_bytes(width, "little")
    boosted, _ = plan(bytes(base))
    assert boosted == bytes(base)
