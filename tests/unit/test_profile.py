from dataclasses import replace

import pytest

from tests.helpers import hashes_for, make_synthetic_rom, profile_for
from tools.webfoot.gba_header import GbaHeader
from tools.webfoot.profile import (
    ProfileConfigError,
    RomProfileCatalog,
    VerificationStatus,
)


def match(catalog, data):
    return catalog.match(
        size=len(data), hashes=hashes_for(data), header=GbaHeader.from_bytes(data)
    )


def test_exact_hash_and_metadata_match_is_verified():
    data = make_synthetic_rom(game_code="BG3E", revision=0)
    result = match(RomProfileCatalog([profile_for(data)]), data)

    assert result.status is VerificationStatus.VERIFIED
    assert result.profile is not None
    assert result.profile.id == "synthetic_exact"


def test_right_game_code_but_wrong_hash_is_unknown():
    data = make_synthetic_rom(game_code="BG3E", size=0x100)
    other = bytearray(data)
    other[-1] = 1
    result = match(RomProfileCatalog([profile_for(bytes(other))]), data)

    assert result.status is VerificationStatus.UNKNOWN
    assert result.profile is None


def test_right_size_but_wrong_hash_is_unknown():
    data = make_synthetic_rom(game_code="TEST", size=0x100)
    other = bytearray(data)
    other[-1] = 7
    result = match(RomProfileCatalog([profile_for(bytes(other))]), data)

    assert result.status is VerificationStatus.UNKNOWN


def test_empty_catalog_returns_unknown():
    data = make_synthetic_rom()
    result = match(RomProfileCatalog([]), data)

    assert result.status is VerificationStatus.UNKNOWN


def test_revision_mismatch_is_conflict():
    data = make_synthetic_rom(revision=0)
    profile = profile_for(data, revision=1)
    result = match(RomProfileCatalog([profile]), data)

    assert result.status is VerificationStatus.CONFLICT
    assert any("revision" in item for item in result.mismatches)


def test_secondary_hash_mismatch_is_conflict():
    data = make_synthetic_rom()
    profile = profile_for(data, md5="0" * 32)
    result = match(RomProfileCatalog([profile]), data)

    assert result.status is VerificationStatus.CONFLICT
    assert any("md5" in item for item in result.mismatches)


def test_duplicate_profile_id_is_rejected():
    data = make_synthetic_rom()
    different = bytearray(data)
    different[-1] = 1
    first = profile_for(data, id="same")
    second = profile_for(bytes(different), id="same")

    with pytest.raises(ProfileConfigError, match="duplicate profile id"):
        RomProfileCatalog([first, second])


def test_duplicate_hash_identity_is_rejected():
    first = profile_for(make_synthetic_rom(), id="first")
    second = replace(first, id="second")

    with pytest.raises(ProfileConfigError, match="duplicate sha256 identity"):
        RomProfileCatalog([first, second])


def test_profile_without_sha256_is_rejected():
    data = make_synthetic_rom()
    exact = profile_for(data, id="by_sha1")
    by_sha1 = replace(exact, sha256=None, md5=None)

    with pytest.raises(ProfileConfigError, match="must provide sha256"):
        RomProfileCatalog([by_sha1])


@pytest.mark.parametrize("field", ["revision", "size"])
def test_boolean_integer_fields_are_rejected(field):
    with pytest.raises(ProfileConfigError):
        profile_for(make_synthetic_rom(), **{field: True})


def test_unexpected_profile_field_is_rejected():
    with pytest.raises(ProfileConfigError, match="unexpected fields"):
        profile_for(make_synthetic_rom(), sha_256="0" * 64)


@pytest.mark.parametrize(
    "content, message",
    [
        ("not: [valid", "cannot load ROM profiles"),
        ("schema_version: 2\nprofiles: []\n", "schema_version"),
        ("schema_version: 1\nprofiles: nope\n", "profiles list"),
    ],
)
def test_malformed_configuration_is_rejected(tmp_path, content, message):
    path = tmp_path / "roms.yaml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ProfileConfigError, match=message):
        RomProfileCatalog.load(path)


def test_checked_in_profile_configuration_loads():
    catalog = RomProfileCatalog.load("config/roms.yaml")

    assert len(catalog.profiles) == 4
