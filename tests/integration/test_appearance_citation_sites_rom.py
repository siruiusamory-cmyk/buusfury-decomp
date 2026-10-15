"""The appearance citation sites, tied to the declared profile keys they cite."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import appearance_authoring as aa
from tools.webfoot import appearances as ap
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.rom import identify_rom

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
POOL_WORD_OFFSETS = (0x00025310, 0x000256B8, 0x0002618C, 0x00027474, 0x000279D8)
COUNT_WORD_OFFSETS = (0x00024F92, 0x00027998, 0x000279CC)
TABLE_ADDRESS = 0x0874D380
CANONICAL_COUNT = 232
RECORD_SIZE = 0x10


def _rom_path() -> Path:
    return Path(os.environ.get(
        "SPRITE_NEW_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))


@pytest.fixture(scope="module")
def image() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def identified(image):
    return identify_rom(_rom_path(), RomProfileCatalog.load("config/roms.yaml"))


@pytest.fixture(scope="module")
def profile(identified):
    return identified.profile_match.profile


def test_the_five_pool_word_offsets_are_the_module_constants():
    assert ap.APPEARANCE_TABLE_REFERENCE_OFFSETS == POOL_WORD_OFFSETS


def test_every_pool_word_holds_the_address_the_profile_declares(image, profile):
    assert profile.appearances.address.raw == TABLE_ADDRESS
    for offset in POOL_WORD_OFFSETS:
        assert image[offset:offset + 4] == TABLE_ADDRESS.to_bytes(4, "little")


def test_the_three_count_word_offsets_are_the_module_constants():
    assert ap.APPEARANCE_COUNT_OFFSETS == COUNT_WORD_OFFSETS


def test_every_count_word_states_the_count_the_profile_declares(image, profile):
    assert profile.appearances.count == CANONICAL_COUNT
    assert ap.APPEARANCE_CANONICAL_COUNT == CANONICAL_COUNT
    assert ap.APPEARANCE_COUNT_OFFSET_WIDTH == 1
    for offset in COUNT_WORD_OFFSETS:
        # Thumb `cmp rN,#imm8`: high five bits 0b00101, low byte the immediate.
        assert image[offset + 1] & 0xF8 == 0x28
        assert image[offset] == CANONICAL_COUNT


def test_the_record_size_is_the_one_the_profile_declares(profile):
    assert profile.appearances.record_size == RECORD_SIZE
    assert ap.APPEARANCE_RECORD_SIZE == RECORD_SIZE


def _spoil(image: bytes, offset: int) -> bytes:
    spoiled = bytearray(image)
    spoiled[offset] ^= 0x01
    return bytes(spoiled)


def test_a_count_word_that_lost_the_canonical_immediate_is_refused(image):
    with pytest.raises(aa.AppearanceAuthoringError) as refused:
        aa._count_changes(_spoil(image, COUNT_WORD_OFFSETS[0]), CANONICAL_COUNT + 1)

    assert "published as one of the appearance count bounds" in str(refused.value)


def test_a_roster_site_that_lost_its_canonical_bytes_is_refused(image):
    site = ap.ROSTER_PATCH_SITES[0]

    with pytest.raises(ap.AppearanceError) as refused:
        site.check(_spoil(image, site.offset))

    assert "published as the roster object size" in str(refused.value)
