"""The behaviour-profile builder, on a hand-built image.

What these tests pin is the pair of failures the tool already made or could make: a build that
silently accepts an image which already carries a profile, and a build whose nodes do not follow
the manifest the verifier reads. The family's own node bytes come from the retail image, so the
synthetic image copies those regions verbatim and only the parts the tool reads are synthetic.

The point of the profile is that it is PER-ENEMY: it copies the family's nodes into an appended
block and repoints only the named records' behaviour rows. These tests assert exactly that, so a
future edit that reaches the shared hub fails here instead of shipping.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import pytest

from tools.research import apply_friend_v3_behaviour_profile as profile
from tools.research import verify_friend_v3_behaviour_profile as verifier
from tools.research.friend_v3_text_approvals import (
    APPROVED_BOSS_PROFILES, APPROVED_DIALOGUE_TEXT_EDITS, APPROVED_RELEASES)
from tools.webfoot.handles import unpack_handle as _unpack


def test_the_copied_spawn_is_the_one_the_leaf_reaches() -> None:
    """B1. The block is serialised AFTER the probability leaf's child is patched. An earlier
    version serialised first, so the leaf still pointed at the retail shared spawn and the copied
    spawn and SET nodes were dead bytes - while the verifier, asserting the retail pointer,
    confirmed it. This asserts the leaf reaches the copy, which is the whole point of copying it."""
    image = synthetic()
    block, offsets = profile.build_block(image, IMAGE_SIZE, 22500, 22500, 32768, 799, 90,
                                         attack_first=True, attack_action=204)
    leaf = offsets["attack_rand"] - IMAGE_SIZE
    child = struct.unpack_from("<I", block, leaf + 0x10)[0]
    assert child == ROM_BASE + offsets["spawn"], "the leaf must reach the copied spawn"
    assert child != ROM_BASE + profile.FAMILY_ATTACK_SPAWN, "the retail spawn is not the copy"


def test_a_populated_behaviour_row_is_refused() -> None:
    """B2. Rows 799 and 90 are borrowed, so the tool must prove nothing resolves them: a record's
    `+0x08` or a SET/AUX parameter that names a row means something else already runs it."""
    image = synthetic()
    free, _why = profile.row_is_free(image, 799)
    assert free, "row 799 is unnamed in the canonical image and is the profile's to borrow"
    # A record that names the row makes it live, and the proof must then refuse it.
    live = bytearray(image)
    struct.pack_into("<I", live, RECORD_AT + profile.BEHAVIOUR_FIELD, 799)
    free, why = profile.row_is_free(bytes(live), 799)
    assert not free and "names row 799" in why
    # The shared hub row is named by a SET node, which is the other way a row goes live.
    free, why = profile.row_is_free(image, 204)
    assert not free and "pushes row 204" in why


def test_a_record_span_is_bytes_not_units() -> None:
    """B3. `unpack_handle` returns decoded start and length in BYTES, so a record's text is
    `stream[start:start+length]`. Scaling by the two-byte unit again doubles the window and moves
    the edit: that defect corrupted 28 records in an earlier release-3 build."""
    from tools.research.apply_friend_v3_dialogue_text import record_text
    stream = ("0123456789" * 40).encode("utf-16le")          # 800 bytes
    handle = 1 | (50 << 6) | (10 << 21)                     # 50 halfwords in, 10 halfwords long
    selector, start, length = _unpack(handle)
    assert (selector, start, length) == (1, 100, 20), "the decoder's fields are bytes"
    assert record_text(stream, start, length) == stream[100:120].decode("utf-16le")
    assert record_text(stream, start, length) != stream[200:240].decode("utf-16le")


def test_the_release_identity_is_well_formed_and_derived_from_the_approvals() -> None:
    """The builder asserts this digest, so a drifted constant would either fail every build or
    certify the wrong image. Pin the shape and the field values that were measured."""
    release = next(r for r in APPROVED_RELEASES if r.name == "release-3")
    assert len(release.base_sha256) == 64
    assert len(release.output_sha256) == 64
    assert release.output_bytes == release.base_bytes + 136      # the appended profile block
    assert release.stages == ("boss-retune", "behaviour-profile", "dialogue-wording")


def test_the_approved_wording_edits_are_the_measured_ones() -> None:
    """Five edits: one spacing repair and four spans covering seven of the ten Kakarot lines. Each
    new string is no longer than the old one, which is what lets the tool write it inside the
    record. The spans are BYTE coordinates (B3). The phrase "If Yamcha  is" is deliberately absent:
    every span carrying it has another record's boundary inside it, so it moves to release 4."""
    assert len(APPROVED_DIALOGUE_TEXT_EDITS) == 5
    assert sum(1 for edit in APPROVED_DIALOGUE_TEXT_EDITS if edit.new.startswith("Bandit")) == 4
    assert sum(1 for edit in APPROVED_DIALOGUE_TEXT_EDITS if edit.new == "Great Soyman") == 1
    assert [edit.selector for edit in APPROVED_DIALOGUE_TEXT_EDITS] == [1, 1, 1, 1, 2]
    for edit in APPROVED_DIALOGUE_TEXT_EDITS:
        assert len(edit.new) <= len(edit.old), edit
        assert edit.old != edit.new


ROM_BASE = 0x08000000
IMAGE_SIZE = 0x800000
SELECTOR = 85
RECORD_AT = profile.RECORD_TABLE + SELECTOR * profile.RECORD_STRIDE


def retail() -> bytes:
    """The canonical image, read-only. Tests that need it skip when it is absent."""
    for candidate in ("roms/Dragon Ball Z - Buu's Fury (U).gba",
                      "roms/DragonBallZ-BuusFury.gba"):
        try:
            return open(candidate, "rb").read()
        except OSError:
            continue
    pytest.skip("the canonical image is not present")


def synthetic() -> bytes:
    """A retail image whose chosen record resolves the family's own entry node."""
    image = bytearray(retail())
    struct.pack_into("<I", image, RECORD_AT + profile.BEHAVIOUR_FIELD, 433)
    row = profile.BEHAVIOUR_TABLE + 433 * profile.BEHAVIOUR_ROW_STRIDE
    struct.pack_into("<I", image, row, profile.FAMILY_ENTRY_NODE)
    for row_number in (799, 90):
        at = profile.BEHAVIOUR_TABLE + row_number * profile.BEHAVIOUR_ROW_STRIDE
        image[at:at + 8] = b"\x00" * 8
    return bytes(image[:IMAGE_SIZE])


def test_the_approved_profile_matches_what_was_measured() -> None:
    """The tracked authority is the measurement, and a silent edit to it is a defect."""
    assert len(APPROVED_BOSS_PROFILES) == 1
    approved = APPROVED_BOSS_PROFILES[0]
    assert approved.selectors == (45, 85)
    assert approved.gate_radius_squared == 22500
    assert approved.attack_radius_squared == 22500
    assert approved.attack_percent == 50.0
    assert approved.attack_first is True
    # B1: the action-row lever was unreachable in every build, because the appended copy's leaf
    # still pointed at the retail spawn. The approved profile therefore carries the retail swing
    # chain, which is what the owner fought and approved.
    assert approved.attack_action_row is None


def test_the_profile_refuses_an_image_that_already_carries_it() -> None:
    """The second build on the same image would repoint rows at a block the family no longer
    holds. The refusal is the check that caught exactly that during the action sweep."""
    image = synthetic()
    assert profile.family_row(image, SELECTOR) == 433
    once = bytearray(image)
    for row_number in (799, 90):
        at = profile.BEHAVIOUR_TABLE + row_number * profile.BEHAVIOUR_ROW_STRIDE
        struct.pack_into("<I", once, at, ROM_BASE + IMAGE_SIZE)
    struct.pack_into("<I", once, RECORD_AT + profile.BEHAVIOUR_FIELD, 799)
    with pytest.raises(profile.ProfileError, match="not the family entry"):
        profile.family_row(bytes(once), SELECTOR)


def test_the_block_changes_only_the_two_attack_numbers_and_the_action_row() -> None:
    """Retail hub, gate and leaves except the declared patches: the family's own bytes plus the
    radius, the probability, the arm order and the swing's action row."""
    image = synthetic()
    block, offsets = profile.build_block(image, IMAGE_SIZE, 22500, 22500, 32768, 799, 90,
                                         attack_first=True, attack_action=204)
    assert len(block) == 168
    retail_gate = image[profile.FAMILY_GATE:profile.FAMILY_GATE + 20]
    gate = block[offsets["gate"] - IMAGE_SIZE:offsets["gate"] - IMAGE_SIZE + 20]
    assert gate[0x0C:0x10] == struct.pack("<I", 22500)
    assert gate[:0x0C] == retail_gate[:0x0C]
    assert struct.unpack_from("<I", block, offsets["attack_rand"] - IMAGE_SIZE + 0x0C)[0] == 32768
    hub = offsets["hub"] - IMAGE_SIZE
    assert struct.unpack_from("<I", block, hub + 0x10)[0] == ROM_BASE + offsets["attack_dist"]
    action = offsets["set_action"] - IMAGE_SIZE
    assert struct.unpack_from("<I", block, action + 0x0C)[0] == 204
    assert struct.unpack_from("<I", block, action)[0] == profile.SET_ENTRY


def test_the_verifier_reads_its_sites_from_the_manifest() -> None:
    """P-018: a verifier that infers how many sites a change has fails on a correct build. The
    check is that the verifier's row loop takes each row's node from the manifest entry, so a
    build with a third row passes without editing the verifier."""
    source = Path(verifier.__file__).read_text(encoding="utf-8")
    assert 'expected = int(entry["node"], 16)' in source
    image = synthetic()
    block, offsets = profile.build_block(image, IMAGE_SIZE, 22500, 22500, 32768, 799, 90,
                                         attack_first=True, attack_action=204)
    assert set(offsets) >= {"gate", "hub", "attack_dist", "attack_rand", "spawn", "set_action"}
    assert len(block) == 16 + 20 + 16 + 44 + 20 + 20 + 16 + 16


def test_the_action_branch_reads_a_rom_address_as_a_file_offset(
        tmp_path: Path, monkeypatch, capsys) -> None:
    """C1. `manifest["nodes"]["set_action"]` is a ROM ADDRESS, and a SET node pushes its row from
    the parameter word at +0x0C. The branch indexed the image with that address, so the one build
    path that carries an action change died with `struct.error` instead of returning a verdict;
    reading the node's first word instead would compare the node's own entry, not the row."""
    image = synthetic()
    block_bytes, offsets = profile.build_block(image, IMAGE_SIZE, 22500, 22500, 32768, 799, 90,
                                               attack_first=True, attack_action=204)
    out = bytearray(image)
    struct.pack_into("<I", out, RECORD_AT + profile.BEHAVIOUR_FIELD, 799)
    row_at = profile.BEHAVIOUR_TABLE + 799 * profile.BEHAVIOUR_ROW_STRIDE
    struct.pack_into("<I", out, row_at, ROM_BASE + offsets["gate"])
    struct.pack_into("<I", out, row_at + 4, profile.FAMILY_ROW_SECONDARY)
    (tmp_path / "base.gba").write_bytes(image)
    (tmp_path / "profile.gba").write_bytes(bytes(out) + block_bytes)
    (tmp_path / "manifest.json").write_text(json.dumps({
        "block_file_offset": IMAGE_SIZE,
        "output_bytes": IMAGE_SIZE + len(block_bytes),
        "profile": {"entry_gate_radius_squared": 22500, "attack_radius_squared": 22500,
                    "attack_probability_raw": 32768, "entry_gate_radius": 150.0,
                    "retail_entry_gate_radius": 100, "attack_radius": 150.0,
                    "attack_percent": 50.0, "retail_attack_radius": 50,
                    "retail_attack_percent": 12.0, "attack_action_row": 204},
        "nodes": {"spawn": f"0x{ROM_BASE + offsets['spawn']:08X}",
                  "set_action": f"0x{ROM_BASE + offsets['set_action']:08X}"},
        "records": [{"selector": SELECTOR, "behaviour_row_after": 799,
                     "behaviour_field_file_offset": RECORD_AT + profile.BEHAVIOUR_FIELD}],
        "rows": [{"row": 799, "file_offset": row_at,
                  "node": f"0x{ROM_BASE + offsets['gate']:08X}"}],
    }), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["verify", "--image", str(tmp_path / "profile.gba"),
                                      "--against", str(tmp_path / "base.gba"),
                                      "--manifest", str(tmp_path / "manifest.json")])
    assert verifier.main() == 0
    assert "PASS the copied SET node carries the requested action row" in capsys.readouterr().out
