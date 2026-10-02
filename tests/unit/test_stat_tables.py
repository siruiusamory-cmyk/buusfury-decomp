"""Portable tests for the static stat-table parsers (DATA-001).

These use SYNTHETIC fixtures only, per ``docs/ROM_SAFETY.md``: no ROM bytes are
committed and the suite runs without the proprietary image. The ROM-gated
cross-checks against real data live in `tests/integration/test_stat_tables_rom.py`.
"""

from __future__ import annotations

import pytest

from tools.webfoot.formats import stat_tables as st


def _enemy_bytes(exp: int, hp: int, type_id: int, level: int,
                 strength: int, power: int, endurance: int) -> bytes:
    """Build one synthetic enemy record in the documented layout."""
    blob = bytearray(st.ENEMY_RECORD_SIZE)
    blob[0:3] = exp.to_bytes(3, "little")
    blob[3] = 0
    blob[4:7] = hp.to_bytes(3, "little")
    blob[7] = 0
    blob[8:10] = type_id.to_bytes(2, "little")
    blob[12] = level
    blob[13] = strength
    blob[14] = power
    blob[15] = endurance
    return bytes(blob)


def _base_bytes(level: int, hp: int, ep: int, strength: int, power: int,
                endurance: int, speed: int, person: int, techs: int) -> bytes:
    blob = bytearray(st.BASE_STAT_RECORD_SIZE)
    blob[0] = level
    blob[1] = 0
    blob[2:4] = hp.to_bytes(2, "little")
    blob[4:6] = ep.to_bytes(2, "little")
    blob[6] = strength
    blob[7] = power
    blob[8] = endurance
    blob[9] = speed
    blob[10] = person
    blob[11] = techs
    return bytes(blob)


def test_enemy_record_round_trips_every_documented_field() -> None:
    data = bytearray(st.ENEMY_TABLE_START + st.ENEMY_RECORD_SIZE)
    data[st.ENEMY_TABLE_START:] = _enemy_bytes(
        exp=225, hp=175, type_id=434, level=60,
        strength=10, power=0, endurance=20,
    )
    rec = st.decode_enemy_record(bytes(data), st.ENEMY_TABLE_START)
    assert rec.exp == 225
    assert rec.hp == 175
    assert rec.type_id == 434
    assert rec.level == 60
    assert rec.strength == 10
    assert rec.power == 0
    assert rec.endurance == 20


def test_enemy_24bit_fields_decode_beyond_16_bits() -> None:
    """Kid Buu's real values exceed 16 bits; the u24 decode must not truncate."""
    data = bytearray(st.ENEMY_TABLE_START + st.ENEMY_RECORD_SIZE)
    data[st.ENEMY_TABLE_START:] = _enemy_bytes(
        exp=96175, hp=125000, type_id=285, level=150,
        strength=66, power=110, endurance=100,
    )
    rec = st.decode_enemy_record(bytes(data), st.ENEMY_TABLE_START)
    assert rec.exp == 96175
    assert rec.hp == 125000


def test_gba_address_is_file_offset_plus_cartridge_base() -> None:
    data = bytearray(st.ENEMY_TABLE_START + st.ENEMY_RECORD_SIZE)
    data[st.ENEMY_TABLE_START:] = _enemy_bytes(1, 1, 1, 1, 1, 1, 1)
    rec = st.decode_enemy_record(bytes(data), st.ENEMY_TABLE_START)
    assert rec.gba_address == rec.offset + 0x08000000


def test_base_stat_record_round_trips_every_documented_field() -> None:
    data = bytearray(st.BASE_STAT_TABLE_START + st.BASE_STAT_RECORD_SIZE)
    data[st.BASE_STAT_TABLE_START:] = _base_bytes(
        level=60, hp=135, ep=90, strength=27, power=27,
        endurance=26, speed=50, person=0x02, techs=4,
    )
    rec = st.decode_base_stat_record(bytes(data), st.BASE_STAT_TABLE_START)
    assert rec.level == 60
    assert rec.hp == 135
    assert rec.ep == 90
    assert rec.strength == 27
    assert rec.power == 27
    assert rec.endurance == 26
    assert rec.speed == 50
    assert rec.person == 0x02
    assert rec.technique_count == 4


def test_structural_check_rejects_nonzero_pad_bytes() -> None:
    """Both pad bytes are what make a record recognisable; either one kills it."""
    good = bytearray(_enemy_bytes(225, 175, 434, 60, 10, 0, 20))
    assert st.looks_like_enemy_record(bytes(good), 0)

    pad_a = bytearray(good)
    pad_a[3] = 1
    assert not st.looks_like_enemy_record(bytes(pad_a), 0)

    pad_b = bytearray(good)
    pad_b[7] = 1
    assert not st.looks_like_enemy_record(bytes(pad_b), 0)


def test_structural_check_rejects_implausible_level() -> None:
    zero = _enemy_bytes(225, 175, 434, 0, 10, 0, 20)
    assert not st.looks_like_enemy_record(zero, 0)
    huge = _enemy_bytes(225, 175, 434, 201, 10, 0, 20)
    assert not st.looks_like_enemy_record(huge, 0)


def test_structural_check_rejects_truncated_input() -> None:
    assert not st.looks_like_enemy_record(b"\x00" * 4, 0)


def test_short_records_raise_rather_than_decode_garbage() -> None:
    with pytest.raises(ValueError):
        st.decode_enemy_record(b"\x00" * 4, 0)
    with pytest.raises(ValueError):
        st.decode_base_stat_record(b"\x00" * 4, 0)


def test_declared_extent_matches_declared_count() -> None:
    """The three published constants must stay mutually consistent."""
    span = st.ENEMY_TABLE_LAST - st.ENEMY_TABLE_START
    assert span % st.ENEMY_RECORD_SIZE == 0
    assert span // st.ENEMY_RECORD_SIZE + 1 == st.ENEMY_RECORD_COUNT


def test_base_stat_names_match_declared_count() -> None:
    assert len(st.BASE_STAT_NAMES) == st.BASE_STAT_RECORD_COUNT
