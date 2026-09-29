"""Fixed-format regions: generated from project facts, then proven against the ROM.

Split into two halves on purpose:

* PORTABLE tests assert that generation is deterministic and self-consistent -
  the header's checksum validates, the logo is the mandated platform constant,
  declared values round-trip through the serialiser. These need no ROM.
* ROM-GATED tests assert byte-identity with the cartridge, which is the claim
  that actually matters. They skip cleanly when no baserom is present.
"""

from __future__ import annotations

import json

import pytest

from buusfury import fixed, gba, identity


@pytest.fixture(scope="module")
def config() -> dict:
    return fixed.load_config()


# ---------------------------------------------------------------------------
# portable: generation is deterministic and internally valid
# ---------------------------------------------------------------------------
def test_config_declares_exactly_the_three_promoted_regions(config):
    ids = {entry["id"] for entry in config["regions"]}
    assert ids == {"rom_header", "gbaram_literals", "titlescreen_data"}
    assert ids == set(fixed.GENERATORS)


def test_declared_extents_match_their_lengths(config):
    lengths = {"rom_header": 0xC0, "gbaram_literals": 16, "titlescreen_data": 104}
    for entry in config["regions"]:
        start = int(entry["start"], 0)
        end = int(entry["end"], 0)
        assert end - start == lengths[entry["id"]], entry["id"]


def test_generated_header_is_the_right_length(config):
    assert len(fixed.generate_header(config)) == gba.HEADER_END


def test_generated_header_checksum_validates(config):
    header = fixed.generate_header(config)
    stored = header[gba.HEADER_CHECKSUM_OFFSET]
    assert stored == gba.compute_header_checksum(header)


def test_generated_header_decodes_to_the_declared_fields(config):
    header = gba.decode_header(fixed.generate_header(config))
    fields = config["rom_header"]["fields"]
    assert header.title == fields["title"] == "DBZBUUSFURY"
    assert header.game_code == fields["game_code"] == "BG3E"
    assert header.maker_code == fields["maker_code"] == "70"
    assert header.fixed_value == fields["fixed_value"] == 0x96
    assert header.checksum_ok
    assert header.logo_is_standard


def test_generated_header_entry_branch_points_at_the_declared_target(config):
    header = fixed.generate_header(config)
    first = next(gba_instruction(first_four(header)))
    assert first.mnemonic == "b"
    assert first.operands[0].imm == config["rom_header"]["entry_target"]


def first_four(header: bytes) -> bytes:
    return header[:4]


def gba_instruction(raw: bytes):
    from buusfury import analysis

    return analysis.MD_ARM.disasm(raw, gba.ROM_BASE)


def test_branch_encoding_is_derived_from_the_target():
    """Changing the target must change the bytes; it is not a copied constant."""
    a = fixed.encode_branch(0x08000000, 0x080000C0)
    b = fixed.encode_branch(0x08000000, 0x08000100)
    assert a != b
    assert a == bytes.fromhex("2e0000ea")  # b 0x080000C0
    with pytest.raises(fixed.FixedRegionError):
        fixed.encode_branch(0x08000000, 0x08000002)  # unaligned target


def test_generation_is_deterministic(config):
    for generator in fixed.GENERATORS.values():
        assert generator(config) == generator(config)


def test_word_tables_serialise_little_endian(config):
    raw = fixed.generate_gbaram_literals(config)
    assert len(raw) == 16
    assert raw[:4] == bytes.fromhex("00080002")  # 0x02000800 little-endian


def test_word_table_refuses_a_value_wider_than_32_bits():
    with pytest.raises(fixed.FixedRegionError):
        fixed.generate_word_table([{"value": 1 << 32}])


def test_the_allocator_pool_is_documented_as_loaded(config):
    """Every word must say how it is used, and the unknown ones must say unknown."""
    words = config["gbaram_literals"]["words"]
    assert len(words) == 4
    assert [w["offset"] for w in words] == ["0x03D730", "0x03D734", "0x03D738", "0x03D73C"]
    for word in words:
        assert word["kind"]
        assert word["meaning"]
        assert word["confidence"] in ("proven", "high", "medium", "low", "unknown")


def test_titlescreen_words_do_not_invent_meaning(config):
    """The 104-byte table is understood only partly; it must not claim more."""
    words = config["titlescreen_data"]["words"]
    assert len(words) == 26
    for word in words:
        assert word["meaning"] == "unknown"
        assert word["confidence"] == "unknown"
        assert word["space"] in {
            "rom", "ewram", "iwram", "io", "palette", "vram", "oam", "bios",
            "rom_mirror_1", "rom_mirror_2", "sram", "none",
        }


def test_regions_config_is_lf_only():
    text = (gba.DATA_DIR / "fixed_regions.json").read_bytes()
    assert b"\r\n" not in text


def test_config_is_valid_json():
    raw = (gba.DATA_DIR / "fixed_regions.json").read_text(encoding="utf-8")
    assert json.loads(raw)["regions"]


# ---------------------------------------------------------------------------
# ROM-gated: byte identity with the cartridge
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("region_id", sorted(fixed.GENERATORS))
def test_fixed_region_reproduces_the_rom_exactly(rom_bytes, config, region_id):
    start, end = fixed.region_extent(config, region_id)
    generated = fixed.GENERATORS[region_id](config)
    expected = rom_bytes[start:end]
    assert len(generated) == len(expected)
    if generated != expected:
        first = next(i for i in range(len(expected)) if expected[i] != generated[i])
        pytest.fail(
            f"{region_id} differs from the cartridge at file 0x{start + first:06X}: "
            f"expected 0x{expected[first]:02X}, generated 0x{generated[first]:02X}"
        )


def test_verify_all_reports_every_region_as_matching(rom_bytes, config):
    results = fixed.verify_all(rom_bytes, config)
    assert len(results) == 3
    for result in results:
        assert result.matches_rom, result.detail
        assert result.generated_length == result.end - result.start


def test_verify_all_reports_a_mismatch_instead_of_raising(rom_bytes, config):
    """A tampered image must produce a failure RESULT, not an exception."""
    tampered = bytearray(rom_bytes)
    tampered[0x3D738] ^= 0xFF
    results = fixed.verify_all(bytes(tampered), config)
    by_id = {r.region_id: r for r in results}
    assert not by_id["gbaram_literals"].matches_rom
    assert by_id["gbaram_literals"].first_difference == 8
    assert by_id["rom_header"].matches_rom


def test_the_header_region_is_confirmed_against_the_identity_config(rom_bytes):
    """The generated header must agree with config/rom.json, the identity gate."""
    canonical = identity.load_canonical()
    header = gba.decode_header(rom_bytes)
    assert header.title == canonical["gba_header"]["title"]
    assert header.game_code == canonical["gba_header"]["game_code"]
    assert header.header_checksum == canonical["gba_header"]["header_checksum"]
