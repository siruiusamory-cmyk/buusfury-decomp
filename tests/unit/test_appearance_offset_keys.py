"""APPEARANCE-OFFSET-KEYS-001: the declared appearance offset families."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot import appearances as ap
from tools.webfoot.profile import (
    AppearanceOffsetProfile,
    ProfileConfigError,
    RomProfileCatalog,
)

BUU = "buus_fury_usa_rev0_01c1707f"
TABLE_ADDRESS = 0x0874D380
CANONICAL_COUNT = 232
POOL_WORD_OFFSETS = (0x00025310, 0x000256B8, 0x0002618C, 0x00027474, 0x000279D8)
COUNT_WORD_OFFSETS = (0x00024F92, 0x00027998, 0x000279CC)


def declaration(**overrides) -> dict[str, object]:
    """One well-formed declaration, with any single family replaced."""
    value: dict[str, object] = {
        "table_reference_offsets": list(POOL_WORD_OFFSETS),
        "count_offsets": list(COUNT_WORD_OFFSETS),
    }
    value.update(overrides)
    return value


def document(value) -> str:
    """A whole version-1 catalogue around one synthetic profile."""
    mapping = {
        "id": "synthetic_appearances_offsets",
        "game": "synthetic",
        "region": "test",
        "game_code": "TEST",
        "size": 0x100,
        "sha256": "0" * 64,
    }
    if value is not None:
        mapping["appearances_offsets"] = value
    return yaml.safe_dump({"schema_version": 1, "profiles": [mapping]})


def test_the_module_literals_are_the_measured_census():
    """Pinned here, not derived: a moved census result has to move this file too."""
    assert ap.APPEARANCE_TABLE_REFERENCE_OFFSETS == POOL_WORD_OFFSETS
    assert ap.APPEARANCE_COUNT_OFFSETS == COUNT_WORD_OFFSETS


def test_a_well_formed_declaration_loads_both_families():
    profile = profile_for(make_synthetic_rom(), appearances_offsets=declaration())

    assert profile.appearances_offsets == AppearanceOffsetProfile(
        table_reference_offsets=POOL_WORD_OFFSETS,
        count_offsets=COUNT_WORD_OFFSETS,
    )


def test_an_absent_key_means_the_modules_own_measured_values():
    """Acceptance 1: absence is the census, never an error and never a zero."""
    profile = profile_for(make_synthetic_rom())

    assert profile.appearances_offsets is None
    assert ap.reference_offsets(profile) == POOL_WORD_OFFSETS
    assert ap.count_offsets(profile) == COUNT_WORD_OFFSETS


def test_a_declared_family_is_what_the_module_uses():
    """Acceptance 5: the read is live, with no code edit and no second source."""
    declared = (0x00010000, 0x00020000)
    profile = profile_for(
        make_synthetic_rom(),
        appearances_offsets=declaration(
            table_reference_offsets=list(declared),
            count_offsets=list(reversed(declared)),
        ),
    )

    assert ap.reference_offsets(profile) == declared
    assert ap.count_offsets(profile) == tuple(reversed(declared))


@pytest.mark.parametrize(
    "path",
    ["config/roms.yaml", "tools/webfoot/data/roms.yaml"],
    ids=["development", "packaged"],
)
def test_each_shipped_catalogue_copy_declares_the_measured_offsets(path):
    catalog = RomProfileCatalog.loads(Path(path).read_text(encoding="utf-8"))
    buu = next(profile for profile in catalog.profiles if profile.id == BUU)

    assert buu.appearances_offsets == AppearanceOffsetProfile(
        table_reference_offsets=POOL_WORD_OFFSETS,
        count_offsets=COUNT_WORD_OFFSETS,
    )
    assert buu.appearances.address.raw == TABLE_ADDRESS
    assert buu.appearances.count == CANONICAL_COUNT


def test_every_other_catalogue_profile_states_no_offsets():
    catalog = RomProfileCatalog.load("config/roms.yaml")

    assert [
        profile.appearances_offsets for profile in catalog.profiles
        if profile.id != BUU
    ] == [None, None, None]


@pytest.mark.parametrize("value", [list(POOL_WORD_OFFSETS), "0x00025310"])
def test_a_non_mapping_refuses_naming_the_key(value):
    with pytest.raises(ProfileConfigError, match="appearances_offsets must be a mapping"):
        RomProfileCatalog.loads(document(value))


def test_an_unexpected_inner_key_refuses_naming_the_key():
    with pytest.raises(
        ProfileConfigError,
        match="appearances_offsets contains unexpected fields: address",
    ):
        RomProfileCatalog.loads(document(declaration(address=TABLE_ADDRESS)))


@pytest.mark.parametrize(
    "offsets",
    [
        [POOL_WORD_OFFSETS[0], "0x000256b8"],
        [True],
        [POOL_WORD_OFFSETS[0], -1],
    ],
    ids=["string-member", "boolean-member", "negative-member"],
)
def test_a_non_integer_member_refuses_naming_the_family(offsets):
    with pytest.raises(
        ProfileConfigError,
        match="appearances_offsets table_reference_offsets must be non-negative integers",
    ):
        RomProfileCatalog.loads(
            document(declaration(table_reference_offsets=offsets))
        )


@pytest.mark.parametrize("offsets", [[], None, 1], ids=["empty", "null", "scalar"])
def test_a_family_that_is_not_a_non_empty_list_refuses_naming_it(offsets):
    with pytest.raises(
        ProfileConfigError,
        match="appearances_offsets count_offsets must be a non-empty list of file offsets",
    ):
        RomProfileCatalog.loads(document(declaration(count_offsets=offsets)))


def test_a_declaration_missing_a_family_refuses_naming_it():
    incomplete = {"table_reference_offsets": list(POOL_WORD_OFFSETS)}

    with pytest.raises(
        ProfileConfigError,
        match="appearances_offsets count_offsets must be a non-empty list of file offsets",
    ):
        RomProfileCatalog.loads(document(incomplete))


def test_schema_version_stays_one():
    with pytest.raises(ProfileConfigError, match="requires schema_version: 1"):
        RomProfileCatalog.loads(
            yaml.safe_dump({"schema_version": 2, "profiles": []})
        )
