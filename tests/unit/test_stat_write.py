"""Portable tests for the TOOLKIT-001 stat write path.

SYNTHETIC fixtures only, per docs/DEVELOPMENT.md: no ROM bytes are committed and this
suite runs without the proprietary image. The ROM-gated proofs (all 141+9
records, the whole-image no-op emit, the wolf edit) live in
`tests/integration/test_stat_write_rom.py`.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from tools.webfoot.formats import stat_tables as st
from tools.webfoot import write as w


# --- fixtures ------------------------------------------------------------


def _enemy_bytes(**over) -> bytes:
    """One synthetic enemy record with a NON-ZERO undecoded tail.

    The tail is deliberately not zeros: a preservation bug that merely zeroed
    unknown bytes would pass against a zero-filled fixture.
    """
    blob = bytearray(st.ENEMY_RECORD_SIZE)
    blob[0:3] = over.get("exp", 225).to_bytes(3, "little")
    blob[3] = 0
    blob[4:7] = over.get("hp", 175).to_bytes(3, "little")
    blob[7] = 0
    blob[8:10] = over.get("type_id", 434).to_bytes(2, "little")
    blob[10:12] = (0).to_bytes(2, "little")
    blob[12] = over.get("level", 60)
    blob[13] = over.get("strength", 10)
    blob[14] = over.get("power", 0)
    blob[15] = over.get("endurance", 20)
    blob[16:28] = bytes(range(0xA0, 0xAC))  # undecoded after-battle block
    return bytes(blob)


def _base_bytes(**over) -> bytes:
    blob = bytearray(st.BASE_STAT_RECORD_SIZE)
    blob[0] = over.get("level", 60)
    blob[1] = 0
    blob[2:4] = over.get("hp", 135).to_bytes(2, "little")
    blob[4:6] = over.get("ep", 90).to_bytes(2, "little")
    blob[6] = over.get("strength", 27)
    blob[7] = over.get("power", 27)
    blob[8] = over.get("endurance", 26)
    blob[9] = over.get("speed", 50)
    blob[10] = over.get("person", 0x02)
    blob[11] = over.get("technique_count", 4)
    blob[12:18] = bytes(range(0xB0, 0xB6))  # undecoded technique ids
    return bytes(blob)


# --- identity ------------------------------------------------------------


def test_identity_is_not_an_offset_or_an_index() -> None:
    """The whole point of StatIdentity: it survives the record moving."""
    early = st.decode_enemy_record(_enemy_bytes(type_id=434), 0)
    moved = st.decode_enemy_record(_enemy_bytes(type_id=434), 0)
    # Same record decoded from a different offset keeps the same identity.
    shifted = st.EnemyRecord(**{**moved.__dict__, "offset": 0x999999})
    assert st.enemy_identity(early) == st.enemy_identity(shifted)
    assert early.offset != shifted.offset


def test_identity_distinguishes_records_by_key_not_position() -> None:
    a = st.decode_enemy_record(_enemy_bytes(type_id=10), 0)
    b = st.decode_enemy_record(_enemy_bytes(type_id=20), 0)
    assert st.enemy_identity(a) != st.enemy_identity(b)


def test_identity_rejects_unknown_kinds_and_negative_keys() -> None:
    with pytest.raises(ValueError):
        st.StatIdentity(kind="sprite", key=1)
    with pytest.raises(ValueError):
        st.StatIdentity(kind="enemy", key=-1)


def test_character_alias_is_separate_from_identity() -> None:
    """A rename must not change identity; they are different concepts."""
    identity = st.character_identity(0, st.BASE_STAT_RECORD_COUNT)
    assert identity == st.StatIdentity(kind="character", key=0)
    assert st.character_alias(0) == "Goku"
    assert str(identity) != st.character_alias(0)


def test_character_identity_rejects_out_of_range_index() -> None:
    """The bound is the caller's declared count, not this module's constant."""
    with pytest.raises(ValueError):
        st.character_identity(st.BASE_STAT_RECORD_COUNT, st.BASE_STAT_RECORD_COUNT)
    # A profile declaring a shorter roster refuses an index it cannot have.
    with pytest.raises(ValueError):
        st.character_identity(9, 5)


def test_character_alias_refuses_an_index_it_has_no_name_for() -> None:
    """A roster index past the verified names fails loudly, never wraps."""
    with pytest.raises(ValueError, match="no verified display alias"):
        st.character_alias(len(st.BASE_STAT_NAMES))


# --- round-trip and unknown-byte preservation ----------------------------


def test_unedited_enemy_record_re_encodes_byte_identically() -> None:
    original = _enemy_bytes()
    record = st.decode_enemy_record(original, 0)
    assert st.encode_enemy_record(record, original) == original


def test_unedited_character_record_re_encodes_byte_identically() -> None:
    original = _base_bytes()
    record = st.decode_base_stat_record(original, 0)
    assert st.encode_base_stat_record(record, original) == original


def test_editing_enemy_hp_preserves_every_undecoded_byte() -> None:
    """The core preservation guarantee, stated as bytes rather than intent."""
    original = _enemy_bytes(hp=175)
    record = st.decode_enemy_record(original, 0)
    edited = st.encode_enemy_record(
        st.EnemyRecord(**{**record.__dict__, "hp": 200}), original
    )
    # The 12-byte after-battle block and both pad bytes are untouched.
    assert edited[16:28] == original[16:28]
    assert edited[3] == original[3] == 0
    assert edited[7] == original[7] == 0
    assert edited[10:12] == original[10:12]
    # Exactly the HP field changed.
    differing = [i for i in range(len(original)) if original[i] != edited[i]]
    assert differing == [4]


def test_editing_character_hp_preserves_technique_ids_and_pad() -> None:
    original = _base_bytes(hp=135)
    record = st.decode_base_stat_record(original, 0)
    edited = st.encode_base_stat_record(
        st.BaseStatRecord(**{**record.__dict__, "hp": 400}), original
    )
    assert edited[12:18] == original[12:18]
    assert edited[1] == original[1] == 0
    assert st.decode_base_stat_record(edited, 0).hp == 400


def test_every_decoded_span_survives_a_decode_encode_cycle() -> None:
    """Each declared span is genuinely covered by the encoder."""
    original = _enemy_bytes()
    record = st.decode_enemy_record(original, 0)
    encoded = st.encode_enemy_record(record, original)
    for offset, width, name in st.ENEMY_DECODED_SPANS:
        assert encoded[offset : offset + width] == original[offset : offset + width], name


# --- encode validation ---------------------------------------------------


def test_encode_refuses_a_value_too_wide_for_its_field() -> None:
    original = _enemy_bytes()
    record = st.decode_enemy_record(original, 0)
    too_big = st.EnemyRecord(**{**record.__dict__, "level": 256})
    with pytest.raises(st.StatEncodeError, match="level"):
        st.encode_enemy_record(too_big, original)


def test_encode_refuses_a_negative_value() -> None:
    original = _enemy_bytes()
    record = st.decode_enemy_record(original, 0)
    negative = st.EnemyRecord(**{**record.__dict__, "hp": -1})
    with pytest.raises(st.StatEncodeError):
        st.encode_enemy_record(negative, original)


def test_encode_refuses_a_backing_slice_of_the_wrong_size() -> None:
    original = _enemy_bytes()
    record = st.decode_enemy_record(original, 0)
    with pytest.raises(st.StatEncodeError, match="exactly"):
        st.encode_enemy_record(record, original[:-1])


def test_u24_fields_accept_values_above_16_bits() -> None:
    original = _enemy_bytes()
    record = st.decode_enemy_record(original, 0)
    big = st.EnemyRecord(**{**record.__dict__, "hp": 125000, "exp": 96175})
    encoded = st.encode_enemy_record(big, original)
    back = st.decode_enemy_record(encoded, 0)
    assert back.hp == 125000
    assert back.exp == 96175


# --- write plan ----------------------------------------------------------


def _plan(base: bytes, *changes: w.ByteChange) -> w.WritePlan:
    return w.plan_changes(
        base,
        changes,
        profile_id="test_profile",
        base_sha256=hashlib.sha256(base).hexdigest(),
    )


def test_noop_plan_reproduces_the_input_exactly() -> None:
    """The first reproducible-build invariant, in miniature."""
    base = bytes(range(256))
    plan = _plan(base, w.ByteChange(0, base[0:4], base[0:4], "owner:1", "unchanged"))
    assert plan.is_noop
    assert w.apply_plan(base, plan) == base


def test_plan_rejects_a_change_whose_old_bytes_do_not_match() -> None:
    base = bytes(range(256))
    bad = w.ByteChange(0, b"\xff\xff", b"\x00\x00", "owner:1", "wrong base")
    with pytest.raises(w.ChangeValidationError, match="different image"):
        _plan(base, bad)


def test_plan_rejects_a_change_past_the_end_of_the_image() -> None:
    base = bytes(range(16))
    over = w.ByteChange(14, b"\x0e\x0f\x00\x00", b"\x00\x00\x00\x00", "o", "past end")
    with pytest.raises(w.ChangeValidationError, match="past the"):
        _plan(base, over)


def test_plan_rejects_overlapping_changes_from_different_owners() -> None:
    base = bytes(range(256))
    a = w.ByteChange(0, base[0:4], b"\x01\x01\x01\x01", "owner:a", "a")
    b = w.ByteChange(2, base[2:6], b"\x02\x02\x02\x02", "owner:b", "b")
    with pytest.raises(w.OverlappingChangeError):
        _plan(base, a, b)


def test_change_rejects_a_resize() -> None:
    """Relocation is a later milestone; a resize must fail loudly now."""
    with pytest.raises(w.ChangeValidationError, match="fixed-length"):
        w.ByteChange(0, b"\x00\x00", b"\x00", "owner:1", "resize")


def test_change_requires_a_semantic_owner() -> None:
    with pytest.raises(w.ChangeValidationError, match="semantic owner"):
        w.ByteChange(0, b"\x00", b"\x01", "", "no owner")


def test_apply_plan_refuses_a_mismatched_base() -> None:
    base = bytes(range(256))
    plan = _plan(base, w.ByteChange(0, base[0:2], b"\xaa\xbb", "o", "edit"))
    with pytest.raises(w.ChangeValidationError, match="plan targets"):
        w.apply_plan(bytes(range(255, -1, -1)), plan)


def test_apply_plan_changes_only_the_planned_bytes() -> None:
    base = bytes(256)
    plan = _plan(base, w.ByteChange(100, base[100:102], b"\xaa\xbb", "o", "edit"))
    out = w.apply_plan(base, plan)
    assert len(out) == len(base)
    assert [i for i in range(len(base)) if base[i] != out[i]] == [100, 101]


# --- manifest ------------------------------------------------------------


def test_manifest_attributes_bytes_to_a_semantic_owner() -> None:
    change = w.ByteChange(0x1000, b"\xaf\x00", b"\xc8\x00", "enemy:434", "hp edit")
    manifest = w.WriteManifest(
        base_profile_id="p",
        base_sha256="a" * 64,
        output_sha256="b" * 64,
        output_size=8,
        changes=(change,),
    )
    payload = json.loads(manifest.dumps())
    assert payload["changed_byte_count"] == 1
    entry = payload["changes"][0]
    assert entry["owner"] == "enemy:434"
    assert entry["reason"] == "hp edit"
    assert entry["old"] == "af00"
    assert entry["new"] == "c800"
    assert payload["base"]["sha256"] == "a" * 64
    assert payload["output"]["sha256"] == "b" * 64


def test_manifest_can_be_queried_by_owner() -> None:
    a = w.ByteChange(0, b"\x00", b"\x01", "enemy:1", "r")
    b = w.ByteChange(4, b"\x00", b"\x02", "enemy:2", "r")
    manifest = w.WriteManifest("p", "a" * 64, "b" * 64, 8, (a, b))
    assert manifest.changes_for("enemy:1") == (a,)


def test_manifest_json_is_deterministic() -> None:
    """A build artefact that differs run to run undermines its own claim."""
    change = w.ByteChange(0x10, b"\x01", b"\x02", "enemy:1", "r")
    manifest = w.WriteManifest("p", "a" * 64, "b" * 64, 8, (change,))
    assert manifest.dumps() == manifest.dumps()
