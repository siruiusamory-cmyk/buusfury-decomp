"""ROM-gated parity tests for the static stat tables (DATA-001).

Three-way cross-check:

    public table interpretation  (BuusFuryToolkit @4353f6a2 layouts)
      <->  canonical ROM bytes   (buus_fury_usa_rev0_01c1707f)
      <->  existing runtime findings (P-010 mGBA capture)

These skip cleanly when the local ROM is absent, so the portable suite stays
runnable without proprietary data. The ROM is opened read-only and never
written; no ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import os

import pytest

from tools.webfoot.formats import stat_tables as st

#: The one image these offsets were verified against. A different dump is a
#: different profile and must not silently reuse these constants.
CANONICAL_SHA1 = "f1c4b07554d2a3b1ad2f325307051e775ce68087"

# --- Values established independently by the P-010 runtime capture ---
# initial HP 179200 raw = 175 displayed; base EXP 225. Both are runtime
# measurements, not readings of the static table.
RUNTIME_WOLF_HP_DISPLAYED = 175
RUNTIME_WOLF_BASE_EXP = 225
#: The fixed-point HP scale fixed by the runtime capture: 1024 raw units = 1
#: displayed HP; see the damage-scale section of
#: ``docs/research/AUTO_RE_STATE.md``.
HP_RAW_PER_POINT = 1024
RUNTIME_WOLF_HP_RAW = 179200


def _rom_bytes() -> bytes:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    data = open(matches[0], "rb").read()
    if hashlib.sha1(data).hexdigest() != CANONICAL_SHA1:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return data


def test_wolf_record_matches_the_p010_runtime_capture() -> None:
    """The headline parity check: static table vs runtime measurement."""
    rom = _rom_bytes()
    matches = st.find_enemy_by_hp(rom, RUNTIME_WOLF_HP_DISPLAYED)
    # Uniqueness IS the identification: no other record shares this HP, which is
    # what lets us claim the static record and the runtime wolf are the same
    # enemy rather than merely similar.
    assert len(matches) == 1, f"HP {RUNTIME_WOLF_HP_DISPLAYED} is not unique: {matches}"
    wolf = matches[0]
    assert wolf.offset == 0x00711BDC
    assert wolf.exp == RUNTIME_WOLF_BASE_EXP
    assert wolf.hp == RUNTIME_WOLF_HP_DISPLAYED


def test_wolf_displayed_hp_reconciles_with_the_runtime_raw_value() -> None:
    """175 displayed x 1024 raw-per-point == the 179200 raw the probe saw."""
    rom = _rom_bytes()
    wolf = st.find_enemy_by_hp(rom, RUNTIME_WOLF_HP_DISPLAYED)[0]
    assert wolf.hp * HP_RAW_PER_POINT == RUNTIME_WOLF_HP_RAW


def test_goku_base_hp_is_the_value_data001_promotes() -> None:
    rom = _rom_bytes()
    goku = next(iter(st.iter_base_stat_records(rom)))
    assert goku.offset == 0x006FDA4C
    assert goku.hp == 135


def test_enemy_table_extent_is_exactly_the_declared_contiguous_run() -> None:
    """Every record inside the extent decodes; the neighbours on both sides do not.

    This is what upgrades the bounds from "where upstream's hand list happens to
    stop" to a verified extent.
    """
    rom = _rom_bytes()
    for offset in range(st.ENEMY_TABLE_START, st.ENEMY_TABLE_LAST + 1,
                        st.ENEMY_RECORD_SIZE):
        assert st.looks_like_enemy_record(rom, offset), f"gap at {offset:#08x}"

    before = st.ENEMY_TABLE_START - st.ENEMY_RECORD_SIZE
    after = st.ENEMY_TABLE_LAST + st.ENEMY_RECORD_SIZE
    assert not st.looks_like_enemy_record(rom, before)
    assert not st.looks_like_enemy_record(rom, after)


def test_enemy_table_yields_the_declared_record_count() -> None:
    rom = _rom_bytes()
    assert len(list(st.iter_enemy_records(rom))) == st.ENEMY_RECORD_COUNT


def test_enemy_type_ids_are_unique_but_not_assumed_sorted() -> None:
    """Type id is a stable key, NOT an ordering.

    3 of 140 transitions decrease, so any future code that binary-searches or
    indexes by position would be wrong. This test pins both halves of that.
    """
    rom = _rom_bytes()
    ids = [r.type_id for r in st.iter_enemy_records(rom)]
    assert len(set(ids)) == len(ids)
    assert ids != sorted(ids)


def test_every_base_stat_record_is_structurally_sane() -> None:
    rom = _rom_bytes()
    records = list(st.iter_base_stat_records(rom))
    assert len(records) == st.BASE_STAT_RECORD_COUNT
    for rec in records:
        assert 0 < rec.level <= 200
        assert 0 < rec.hp
        assert rec.technique_count <= 6


def test_rom_is_not_modified_by_reading_it() -> None:
    rom_path = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not rom_path:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    before = hashlib.sha256(open(rom_path[0], "rb").read()).hexdigest()
    list(st.iter_enemy_records(_rom_bytes()))
    list(st.iter_base_stat_records(_rom_bytes()))
    after = hashlib.sha256(open(rom_path[0], "rb").read()).hexdigest()
    assert before == after
