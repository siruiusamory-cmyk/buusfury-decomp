"""ROM-gated proofs for the TOOLKIT-001 write path.

These are the exit criteria that cannot be demonstrated on synthetic data:
the full 141+9 record round-trip, the whole-image no-op emit, and the wolf
HP edit changing exactly one byte with full attribution.

They skip cleanly when the canonical ROM is absent, so the portable suite
stays runnable without proprietary data. The ROM is opened read-only and is
verified unchanged afterwards; no ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

import pytest

from tools.webfoot.formats import stat_tables as st
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.stats import (
    StatProfileError,
    StatTableError,
    UnknownFieldError,
    UnknownRecordError,
    load_stat_tables,
)
from tools.webfoot.write import WriteError, apply_plan, emit_image

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: P-010 runtime capture; HP 175 is unique across the enemy table, which is
#: what makes it a legitimate way to find the wolf without hardcoding a slot.
WOLF_HP = 175
WOLF_TYPE_ID = 434
WOLF_RECORD_OFFSET = 0x00711BDC
#: The HP field sits at record +0x04, so a 175 -> 200 edit touches only the
#: low byte of that u24.
WOLF_HP_BYTE_OFFSET = WOLF_RECORD_OFFSET + 0x04


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(open(matches[0], "rb").read()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return matches[0]


@pytest.fixture
def rom() -> str:
    return _rom_path()


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture
def tables(rom: str, catalog: RomProfileCatalog):
    return load_stat_tables(rom, catalog)


# --- exit criteria 1, 2, 3: full round-trip ------------------------------


def test_all_enemy_records_load_from_the_profile_declared_extent(tables) -> None:
    """Count comes from the profile, not from a module constant."""
    assert len(list(tables.enemies())) == 141
    assert tables.profile.enemy_stats.count == 141


def test_all_character_records_load_from_the_profile(tables) -> None:
    assert len(list(tables.characters())) == 9
    assert tables.profile.character_base_stats.count == 9


def test_every_record_re_serializes_byte_identically(tables) -> None:
    """Exit criteria 1 and 2: all 150 records round-trip with no edits."""
    plan = tables.plan()
    assert len(plan.changes) == 150
    assert plan.effective_changes == ()
    assert plan.is_noop
    assert plan.changed_byte_count == 0


def test_undecoded_bytes_are_carried_on_every_record(tables) -> None:
    """Exit criterion 3, checked at the record level rather than in aggregate.

    Each enemy record has 12 undecoded after-battle bytes; a re-encode must
    reproduce them exactly. At least one record must actually have non-zero
    bytes there, or this test would pass vacuously.
    """
    saw_nonzero_tail = False
    for entry in tables.enemies():
        encoded = st.encode_enemy_record(entry.record, entry.original_bytes)
        assert encoded[0x10:0x1C] == entry.original_bytes[0x10:0x1C]
        if any(entry.original_bytes[0x10:0x1C]):
            saw_nonzero_tail = True
    assert saw_nonzero_tail, "fixture would pass vacuously: all tails were zero"

    for entry in tables.characters():
        encoded = st.encode_base_stat_record(entry.record, entry.original_bytes)
        assert encoded[0x0C:0x12] == entry.original_bytes[0x0C:0x12]


# --- exit criterion 8: whole-image no-op emit ----------------------------


def test_noop_whole_image_emit_is_byte_identical(rom, tables) -> None:
    """The first reproducible-build invariant, on the real 8 MiB image."""
    base = open(rom, "rb").read()
    output = apply_plan(base, tables.plan())
    assert output == base
    assert hashlib.sha256(output).hexdigest() == CANONICAL_SHA256


def test_noop_emit_to_disk_matches_the_input_hash(rom, tables, tmp_path) -> None:
    destination = tmp_path / "noop.gba"
    manifest = emit_image(rom, destination, tables.plan())
    assert manifest.output_sha256 == CANONICAL_SHA256
    assert manifest.base_sha256 == CANONICAL_SHA256
    assert manifest.changes == ()
    assert destination.read_bytes() == open(rom, "rb").read()


# --- exit criteria 5, 6, 7: the wolf edit --------------------------------


def test_wolf_is_identified_by_value_not_position(tables) -> None:
    wolves = tables.find_enemies_by_hp(WOLF_HP)
    assert len(wolves) == 1, "HP 175 is supposed to be unique across the table"
    wolf = wolves[0]
    assert wolf.identity == st.StatIdentity("enemy", WOLF_TYPE_ID)
    assert wolf.location.file_offset == WOLF_RECORD_OFFSET
    # Location is knowable but is NOT the identity.
    assert wolf.identity.key != wolf.location.index


def test_wolf_hp_edit_changes_exactly_one_byte(rom, tables) -> None:
    """Exit criteria 5 and 6."""
    base = open(rom, "rb").read()
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    tables.set_enemy_field(wolf.identity, "hp", 200)

    output = apply_plan(base, tables.plan())
    differing = [i for i in range(len(base)) if base[i] != output[i]]
    assert differing == [WOLF_HP_BYTE_OFFSET]
    assert len(output) == len(base)


def test_wolf_hp_edit_is_attributable_to_its_semantic_owner(
    rom, tables, tmp_path
) -> None:
    """Exit criterion 7: the manifest answers WHY those bytes changed."""
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    tables.set_enemy_field(wolf.identity, "hp", 200)

    destination = tmp_path / "wolf.gba"
    manifest_path = tmp_path / "wolf.json"
    manifest = emit_image(
        rom, destination, tables.plan(), manifest_path=manifest_path
    )

    assert len(manifest.changes) == 1
    change = manifest.changes[0]
    assert change.owner == "enemy:434"
    assert "hp" in change.reason
    assert change.offset == WOLF_RECORD_OFFSET
    assert manifest.base_sha256 == CANONICAL_SHA256
    assert manifest.output_sha256 != CANONICAL_SHA256

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["changed_byte_count"] == 1
    assert payload["changes"][0]["owner"] == "enemy:434"
    # Old and new bytes are both recorded, so the change is self-verifying.
    assert bytes.fromhex(payload["changes"][0]["old"])[4] == WOLF_HP
    assert bytes.fromhex(payload["changes"][0]["new"])[4] == 200


def test_edited_output_decodes_back_to_the_new_value(rom, tables) -> None:
    base = open(rom, "rb").read()
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    tables.set_enemy_field(wolf.identity, "hp", 200)
    output = apply_plan(base, tables.plan())
    assert st.decode_enemy_record(output, WOLF_RECORD_OFFSET).hp == 200
    # And the undecoded tail survived into the output image.
    assert output[WOLF_RECORD_OFFSET + 0x10 : WOLF_RECORD_OFFSET + 0x1C] == (
        base[WOLF_RECORD_OFFSET + 0x10 : WOLF_RECORD_OFFSET + 0x1C]
    )


def test_character_edit_is_attributed_with_its_alias(rom, tables) -> None:
    # The bound is the profile's declared character count, which is the same
    # number `load_stat_tables` used to build this table.
    count = tables.profile.character_base_stats.count
    goku = tables.character(st.character_identity(0, count))
    assert goku.alias == "Goku"
    tables.set_character_field(goku.identity, "hp", 200)
    plan = tables.plan()
    changes = plan.effective_changes
    assert len(changes) == 1
    assert changes[0].owner == "character:0"
    assert "Goku" in changes[0].reason


# --- exit criterion 4: validation ----------------------------------------


def test_edit_rejects_a_level_above_the_engine_cap(tables) -> None:
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    with pytest.raises(StatTableError, match="maximum"):
        tables.set_enemy_field(wolf.identity, "level", 201)


def test_edit_rejects_a_value_too_wide_for_the_field(tables) -> None:
    """Semantic edit passes; the codec refuses at encode time."""
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    tables.set_enemy_field(wolf.identity, "hp", 1 << 24)
    with pytest.raises(st.StatEncodeError, match="hp"):
        tables.plan()


def test_edit_rejects_an_unknown_field(tables) -> None:
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    with pytest.raises(UnknownFieldError):
        tables.set_enemy_field(wolf.identity, "offset", 0)


def test_edit_rejects_an_unknown_identity(tables) -> None:
    with pytest.raises(UnknownRecordError):
        tables.set_enemy_field(st.StatIdentity("enemy", 999999), "hp", 1)


def test_boolean_is_not_accepted_as_an_integer_field(tables) -> None:
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    with pytest.raises(StatTableError):
        tables.set_enemy_field(wolf.identity, "hp", True)


# --- exit criterion 9: the canonical ROM is immutable --------------------


def test_canonical_rom_is_unchanged_by_the_whole_write_path(
    rom, catalog, tmp_path
) -> None:
    before = hashlib.sha256(open(rom, "rb").read()).hexdigest()
    tables = load_stat_tables(rom, catalog)
    wolf = tables.find_enemies_by_hp(WOLF_HP)[0]
    tables.set_enemy_field(wolf.identity, "hp", 200)
    emit_image(rom, tmp_path / "out.gba", tables.plan())
    after = hashlib.sha256(open(rom, "rb").read()).hexdigest()
    assert before == after == CANONICAL_SHA256


def test_emit_refuses_to_write_over_the_input(rom, tables) -> None:
    with pytest.raises(WriteError, match="read-only"):
        emit_image(rom, rom, tables.plan())


def test_emit_refuses_to_overwrite_an_existing_output(rom, tables, tmp_path) -> None:
    destination = tmp_path / "existing.gba"
    destination.write_bytes(b"already here")
    with pytest.raises(WriteError, match="refusing to overwrite"):
        emit_image(rom, destination, tables.plan())
    assert destination.read_bytes() == b"already here"


# --- profile contract enforcement ----------------------------------------


def test_tampered_profile_extents_are_refused(rom, tmp_path) -> None:
    """A supplied catalog cannot redirect where the write path reads or writes.

    Identity verification authenticates the ROM, not the metadata describing
    it, so a hand-edited profile could otherwise keep the hashes intact while
    pointing the stat tables at an arbitrary region. `map_entry` guards its
    read path this way; a write path needs it at least as much.
    """
    original = open("config/roms.yaml", encoding="utf-8").read()
    tampered = original.replace("address: 0x08711274", "address: 0x08711280")
    assert tampered != original, "fixture did not actually change the extent"

    path = tmp_path / "tampered.yaml"
    path.write_text(tampered, encoding="utf-8")

    with pytest.raises(StatProfileError, match="conflicts with the packaged"):
        load_stat_tables(rom, RomProfileCatalog.load(path))
