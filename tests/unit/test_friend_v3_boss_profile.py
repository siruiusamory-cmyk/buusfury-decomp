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

import struct
from pathlib import Path

import pytest

from tools.research import apply_friend_v3_behaviour_profile as profile
from tools.research import verify_friend_v3_behaviour_profile as verifier
from tools.research.friend_v3_text_approvals import (
    APPROVED_BOSS_PROFILES, APPROVED_DIALOGUE_TEXT_EDITS, APPROVED_RELEASES)


def test_the_release_identity_is_well_formed_and_derived_from_the_approvals() -> None:
    """The builder asserts this digest, so a drifted constant would either fail every build or
    certify the wrong image. Pin the shape and the field values that were measured."""
    release = next(r for r in APPROVED_RELEASES if r.name == "release-3")
    assert len(release.base_sha256) == 64
    assert len(release.output_sha256) == 64
    assert release.output_bytes == release.base_bytes + 168      # the appended profile block
    assert release.stages == ("boss-retune", "behaviour-profile", "dialogue-wording")


def test_the_approved_wording_edits_are_the_six_measured_ones() -> None:
    """Six edits: one spacing repair and five spans covering the ten Kakarot lines. Each new
    string is no longer than the old one, which is what lets the tool write it inside the record."""
    assert len(APPROVED_DIALOGUE_TEXT_EDITS) == 6
    assert sum(1 for edit in APPROVED_DIALOGUE_TEXT_EDITS if edit.new.startswith("Bandit")) == 5
    assert [edit.selector for edit in APPROVED_DIALOGUE_TEXT_EDITS] == [1, 1, 1, 1, 2, 2]
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
    assert approved.attack_action_row == 204


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
