"""The playtest image changes the maxed stat fields, and nothing else.

The Bandana startup injection was cancelled by the owner on 2026-10-09 because the hook it used
made the main menu selection arrow visibly wrong. These tests therefore pin the opposite of what
they used to: the delivered image must contain the stat boost and must NOT contain the hook,
the trampoline, or any other byte outside the five declared fields.
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
    HOOK_FILE,
    MAXIMUM,
    PARTY_RECORDS,
    TRAMPOLINE_FILE,
    TRAMPOLINE_LENGTH,
    _assert_only_declared_bytes_changed,
    plan,
)


def synthetic_base() -> bytearray:
    """A base whose stat table is below maximum and large enough for the patch."""
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


def _declared_bytes() -> set[int]:
    declared: set[int] = set()
    for index in PARTY_RECORDS:
        record = BASE_STAT_TABLE + index * BASE_STAT_RECORD_SIZE
        for rel, width in FIELD_OFFSETS.values():
            declared.update(range(record + rel, record + rel + width))
    return declared


def test_changed_bytes_are_exactly_the_declared_stat_fields() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)
    actual = {i for i, (a, b) in enumerate(zip(base, boosted)) if a != b}
    assert actual == _declared_bytes(), sorted(actual ^ _declared_bytes())
    assert [entry["name"] for entry in changes] == ["Goku", "Gohan", "Goten", "Trunks", "Vegeta"]


def test_the_bandana_hook_is_not_applied() -> None:
    """The cancelled injection must not reach a playtest image."""
    base = bytes(synthetic_base())
    boosted, _ = plan(base)
    assert boosted[HOOK_FILE:HOOK_FILE + 4] == base[HOOK_FILE:HOOK_FILE + 4], (
        "the hook region changed: the cancelled Bandana injection is active"
    )
    run = TRAMPOLINE_LENGTH[0] or 64
    assert boosted[TRAMPOLINE_FILE:TRAMPOLINE_FILE + run] == base[TRAMPOLINE_FILE:TRAMPOLINE_FILE + run], (
        "the trampoline region changed: the cancelled Bandana injection is active"
    )


def test_bandana_patch_has_no_caller_in_the_build_path() -> None:
    """A caller reappearing means the cancelled hook became reachable again."""
    source = (ROOT / "tools" / "research" / "build_friend_v3_playtest_boost.py").read_text(encoding="utf-8")
    assert "boosted = bandana_patch(" not in source
    assert "bandana_patch(bytes(out))" not in source


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


def test_an_already_maxed_image_is_returned_unchanged() -> None:
    base = bytearray(synthetic_base())
    for index in PARTY_RECORDS:
        for name, (_, width) in FIELD_OFFSETS.items():
            _write(base, index, name, MAXIMUM[name])
    boosted, _ = plan(bytes(base))
    assert boosted == bytes(base)


def test_a_byte_outside_the_declared_spans_is_refused() -> None:
    base = bytes(synthetic_base())
    boosted, changes = plan(base)
    tampered = bytearray(boosted)
    stray = BASE_STAT_TABLE + 0x0C
    tampered[stray] ^= 0xFF
    with pytest.raises(BoostError, match="outside the declared spans"):
        _assert_only_declared_bytes_changed(base, bytes(tampered), changes)
