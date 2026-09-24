"""CQA-15: the surviving copies of the load-bearing values are pinned to one owner.

The migration removed the live duplicates, but a literal that is legitimately
retained elsewhere - a test oracle, a research probe's independent measurement,
an evidence label - can still drift silently. These assert the relationships
that must hold, so a reintroduced or drifted copy fails loudly instead of
quietly disagreeing with the profile.

They deliberately do NOT assert "constant == constant" between two production
copies: that pattern cannot distinguish a real single owner from two copies that
happen to agree today. Each assertion names which side is authoritative.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.export import profile_authority
from tools.webfoot import atlas_build, capability, map_render
from tools.webfoot.formats import stat_tables as st
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.profile import RomProfileCatalog

REPO = Path(__file__).resolve().parents[2]
BUU = "buus_fury_usa_rev0_01c1707f"


@pytest.fixture(scope="module")
def development() -> RomProfileCatalog:
    return RomProfileCatalog.load(REPO / "config" / "roms.yaml")


@pytest.fixture(scope="module")
def packaged() -> RomProfileCatalog:
    return capability._packaged_catalog()


@pytest.fixture(scope="module")
def buu(development):
    return next(p for p in development.profiles if p.id == BUU)


# --- the catalog itself is one authority, in two places on disk ---------------


def test_the_two_catalog_copies_are_byte_identical():
    """`config/roms.yaml` and the packaged copy must not drift.

    Both exist because the CLI prefers the in-repo file while
    `webfoot.capability` always reads the packaged one, so a difference between
    them would make "the verified profile" depend on which path was taken.
    """
    development = REPO / "config" / "roms.yaml"
    packaged = REPO / "tools" / "webfoot" / "data" / "roms.yaml"
    assert development.read_bytes() == packaged.read_bytes()


def test_capability_and_the_export_stack_resolve_the_same_profile(development, buu):
    """One identity, whatever entry point asks for it."""
    via_capability = capability.packaged_contract(buu.id, capability.Capability.MAP_ENTRIES)
    via_export = profile_authority.canonical_export_profile()
    assert via_capability.identity == via_export.identity == buu.identity


# --- the migrated production copies -------------------------------------------


def test_atlas_build_stamps_the_profiles_identity(buu):
    """The identity the atlas publishes is the profile's, not a second literal."""
    assert atlas_build.PROFILE_ID == buu.id
    assert atlas_build.BASE_SHA256 == buu.sha256
    assert atlas_build.IMAGE_SIZE == buu.size


def test_the_map_renderer_gate_is_the_profiles_identity(buu):
    """The renderer resolves the packaged profile; it owns no hash of its own."""
    resolved = map_render.canonical_profile()
    assert resolved.identity == buu.identity
    assert not hasattr(map_render, "SUPPORTED_ROM_SHA256"), (
        "map_render must not own a second copy of the canonical hash; the "
        "profile authority is the one owner"
    )
    assert not hasattr(map_render, "MAP_ENTRY_TABLE_ADDRESS"), (
        "the MapEntry table address is the profile's declaration"
    )


def test_the_export_stack_owns_no_identity_or_extent_literal():
    """The export readers read identity and extents through the profile."""
    from tools.export import canonical as canon
    from tools.export import map_browser as mb

    for module in (canon, mb):
        for name in (
            "SUPPORTED_ROM_SHA256",
            "MAP_ENTRY_TABLE_ADDRESS",
            "MAP_ENTRY_COUNT",
            "TEXT_POINTER_TABLE_ADDRESS",
            "TEXT_POINTER_COUNT",
            "OBJECT_PALETTE_ADDRESS",
        ):
            assert not hasattr(module, name), (
                f"{module.__name__}.{name} is a second owner of a fact the "
                "profile declares"
            )


def test_the_text_codec_owns_no_game_extent(buu):
    """The codec carries format facts only, never one game's table extent."""
    for name in (
        "TEXT_ENTRY_COUNT",
        "TEXT_TABLE_START",
        "TEXT_POOL_START",
        "TEXT_POOL_END",
    ):
        assert not hasattr(tt, name), (
            f"formats.text_tables.{name} is a game constant, not format structure"
        )
    # The format facts it does own are still there.
    assert tt.TEXT_POINTER_SIZE == 4
    assert tt.TERMINATOR == 0x0000


def test_the_stat_strides_agree_with_the_profile_declarations(buu):
    """A stride is a format fact; the profile's declaration must match it."""
    assert buu.enemy_stats.record_size == st.ENEMY_RECORD_SIZE
    assert buu.character_base_stats.record_size == st.BASE_STAT_RECORD_SIZE


def test_the_stat_extent_constants_are_not_a_second_address_authority(buu):
    """The stat table ADDRESS comes from the profile, and the constant differs.

    `stat_tables.ENEMY_TABLE_START` is a FILE OFFSET kept as the evidence the
    extent was verified against; the profile declares a GBA ADDRESS. They
    describe the same bytes, so the relationship is asserted rather than the
    values, which is what makes the constant an oracle instead of an authority.
    """
    from tools.webfoot.binary import GBA_ROM_BASE

    assert buu.enemy_stats.address.raw == st.ENEMY_TABLE_START + GBA_ROM_BASE
    assert buu.character_base_stats.address.raw == (
        st.BASE_STAT_TABLE_START + GBA_ROM_BASE
    )


# --- retained evidence oracles still agree with the profile -------------------


def test_the_atlas_producers_identity_matches_the_profile(buu):
    """The producers' evidence label is the profile's identity, not a rival."""
    from tools.webfoot.atlas_producers import code_functions, graphics_extents

    assert code_functions.EXPECTED_SHA == buu.sha256
    # `graphics_extents` no longer carries a literal at all.
    assert not hasattr(graphics_extents, "EXPECTED_SHA")


def test_the_data_contract_hashes_agree_with_the_profile(development):
    """Each `data/*` contract's `sha256` must match its profile's declaration.

    Those hashes are no longer the runtime authority, they are compared against
    the profile by `authored_placements` and `placement_events`. This asserts the
    relationship for every catalogued profile, so a contract entry that drifts
    from the catalog fails here as well as at the gate.
    """
    from tools.webfoot.data.behavior_triggers import BEHAVIOR_TRIGGER_CONTRACTS
    from tools.webfoot.data.placement_contracts import CONTRACTS

    by_id = {profile.id: profile for profile in development.profiles}
    for label, contracts in (
        ("placement_contracts", CONTRACTS),
        ("behavior_triggers", BEHAVIOR_TRIGGER_CONTRACTS),
    ):
        assert contracts, f"{label} is empty"
        for profile_id, contract in contracts.items():
            profile = by_id.get(profile_id)
            assert profile is not None, (
                f"{label} names profile {profile_id!r}, which the catalog does not "
                "configure"
            )
            assert contract["sha256"] == profile.sha256, (
                f"{label}[{profile_id!r}]['sha256'] disagrees with the profile; the "
                "profile is the authority"
            )


def test_the_retained_stat_oracles_are_geometrically_consistent():
    """The evidence extents describe a whole number of records.

    This is the check that keeps the retained oracle honest: if the artifact it
    describes is re-measured, these three values must move together.
    """
    span = st.ENEMY_TABLE_LAST - st.ENEMY_TABLE_START
    assert span % st.ENEMY_RECORD_SIZE == 0
    assert span // st.ENEMY_RECORD_SIZE + 1 == st.ENEMY_RECORD_COUNT
    assert len(st.BASE_STAT_NAMES) == st.BASE_STAT_RECORD_COUNT
