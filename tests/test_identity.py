"""Identity verification: the fail-closed gate.

Everything here is synthetic. No commercial ROM is read, and no ROM-derived
fixture is committed.
"""

from __future__ import annotations

import json

import pytest

from buusfury import identity


def _synthetic_rom(
    *,
    title: bytes = b"DBZBUUSFURY\x00",
    game_code: bytes = b"BG3E",
    maker: bytes = b"70",
    size: int = 0x1000,
    pad: int = 0xFF,
    break_checksum: bool = False,
) -> bytes:
    """Build a small file with a well-formed GBA-style header at 0xA0."""
    data = bytearray([pad] * size)
    data[0:4] = b"\x2e\x00\x00\xea"
    data[0xA0:0xAC] = title
    data[0xAC:0xB0] = game_code
    data[0xB0:0xB2] = maker
    data[0xB2] = 0x96
    data[0xB3] = 0x00
    data[0xB4] = 0x00
    data[0xBC] = 0x00
    total = sum(data[0xA0:0xBD])
    data[0xBD] = (-(0x19 + total)) & 0xFF
    if break_checksum:
        data[0xBD] ^= 0xFF
    return bytes(data)


def _write(tmp_path, name: str, data: bytes):
    p = tmp_path / name
    p.write_bytes(data)
    return p


# --------------------------------------------------------------------------
# header parsing and the checksum algorithm
# --------------------------------------------------------------------------
def test_header_fields_are_read_from_the_right_offsets(tmp_path):
    rom = _write(tmp_path, "a.gba", _synthetic_rom())
    found = identity.identify(rom)
    assert found.header is not None
    assert found.header.title == "DBZBUUSFURY"
    assert found.header.game_code == "BG3E"
    assert found.header.maker_code == "70"
    assert found.header.fixed_value == 0x96


def test_generated_header_checksum_validates(tmp_path):
    rom = _write(tmp_path, "a.gba", _synthetic_rom())
    found = identity.identify(rom)
    assert found.header_checksum_ok()


def test_a_single_flipped_checksum_byte_is_detected(tmp_path):
    rom = _write(tmp_path, "a.gba", _synthetic_rom(break_checksum=True))
    found = identity.identify(rom)
    assert not found.header_checksum_ok()


def test_header_checksum_is_the_negated_sum_seeded_with_0x19():
    data = _synthetic_rom()
    expected = (-(0x19 + sum(data[0xA0:0xBD]))) & 0xFF
    assert data[0xBD] == expected


def test_a_file_too_small_for_a_header_reports_rather_than_crashes(tmp_path):
    rom = _write(tmp_path, "tiny.gba", b"\x00" * 0x40)
    found = identity.identify(rom)
    assert found.header is None


# --------------------------------------------------------------------------
# compare(): every mismatch is reported, and reported specifically
# --------------------------------------------------------------------------
def _config_for(data: bytes, **hash_overrides) -> dict:
    import hashlib
    import zlib

    hashes = {
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
        "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08x}",
    }
    hashes.update(hash_overrides)
    return {
        "size_bytes": len(data),
        "hashes": hashes,
        "gba_header": {
            "title": "DBZBUUSFURY",
            "game_code": "BG3E",
            "maker_code": "70",
            "fixed_value": 0x96,
            "main_unit_code": 0,
            "device_type": 0,
            "software_version": 0,
            "header_checksum": data[0xBD],
        },
    }


def test_a_matching_rom_produces_no_mismatches(tmp_path):
    data = _synthetic_rom()
    rom = _write(tmp_path, "a.gba", data)
    assert identity.compare(identity.identify(rom), _config_for(data)) == []


def test_a_wrong_revision_is_named_by_game_code(tmp_path):
    data = _synthetic_rom()
    rom = _write(tmp_path, "a.gba", data)
    config = _config_for(data)
    config["gba_header"]["game_code"] = "ALFE"  # Legacy of Goku II
    problems = identity.compare(identity.identify(rom), config)
    assert any("game_code" in p and "ALFE" in p for p in problems)


def test_a_single_flipped_byte_fails_the_sha1_check(tmp_path):
    data = _synthetic_rom()
    tampered = bytearray(data)
    tampered[0x800] ^= 0x01
    rom = _write(tmp_path, "a.gba", bytes(tampered))
    problems = identity.compare(identity.identify(rom), _config_for(data))
    assert any(p.startswith("sha1:") for p in problems)


def test_wrong_size_is_reported(tmp_path):
    data = _synthetic_rom()
    rom = _write(tmp_path, "a.gba", data[:-1])
    problems = identity.compare(identity.identify(rom), _config_for(data))
    assert any(p.startswith("size:") for p in problems)


def test_verify_raises_and_lists_every_problem_at_once(tmp_path):
    data = _synthetic_rom()
    rom = _write(tmp_path, "a.gba", data)
    config = _config_for(data, sha1="0" * 40)
    config["size_bytes"] = len(data) + 1
    with pytest.raises(identity.IdentityError) as excinfo:
        identity.verify(rom, config)
    # size, sha1, and the header-checksum cross-check are all fail-closed.
    assert len(excinfo.value.mismatches) >= 2


def test_verify_returns_the_identity_when_everything_matches(tmp_path):
    data = _synthetic_rom()
    rom = _write(tmp_path, "a.gba", data)
    found = identity.verify(rom, _config_for(data))
    assert found.sha1 == _config_for(data)["hashes"]["sha1"]


def test_a_missing_rom_raises_RomNotFoundError(tmp_path):
    with pytest.raises(identity.RomNotFoundError):
        identity.identify(tmp_path / "nope.gba")


# --------------------------------------------------------------------------
# baserom resolution never invents a path
# --------------------------------------------------------------------------
def test_resolve_baserom_prefers_the_explicit_argument(tmp_path):
    rom = _write(tmp_path, "explicit.gba", _synthetic_rom())
    assert identity.resolve_baserom(rom) == rom


def test_resolve_baserom_rejects_a_bogus_explicit_path(tmp_path):
    with pytest.raises(identity.RomNotFoundError):
        identity.resolve_baserom(tmp_path / "absent.gba")


def test_resolve_baserom_explains_where_it_looked(tmp_path, monkeypatch):
    monkeypatch.delenv("BUUSFURY_ROM", raising=False)
    with pytest.raises(identity.RomNotFoundError) as excinfo:
        identity.resolve_baserom(None, repo_root=tmp_path)
    message = str(excinfo.value)
    assert "baserom.gba" in message
    assert "never tracked by Git" in message


def test_environment_variable_is_honoured(tmp_path, monkeypatch):
    rom = _write(tmp_path, "env.gba", _synthetic_rom())
    monkeypatch.setenv("BUUSFURY_ROM", str(rom))
    assert identity.resolve_baserom(None, repo_root=tmp_path) == rom


# --------------------------------------------------------------------------
# the committed canonical config is internally consistent
# --------------------------------------------------------------------------
def test_canonical_config_shape():
    config = identity.load_canonical()
    assert config["size_bytes"] == 8388608
    assert config["hashes"]["sha1"] == "f1c4b07554d2a3b1ad2f325307051e775ce68087"
    assert len(config["hashes"]["sha1"]) == 40
    assert len(config["hashes"]["sha256"]) == 64
    assert len(config["hashes"]["md5"]) == 32
    assert len(config["hashes"]["crc32"]) == 8
    assert config["gba_header"]["title"] == "DBZBUUSFURY"
    assert config["gba_header"]["game_code"] == "BG3E"


def test_canonical_config_records_the_log1_remake_alias():
    """One ROM, two naming conventions - the alias must not drift."""
    config = identity.load_canonical()
    aliases = config["aliases"]
    assert any(
        a["crc32"] == config["hashes"]["crc32"] and a["profile_id"].endswith(a["crc32"])
        for a in aliases
    )


def test_canonical_config_is_valid_json_utf8():
    raw = (identity.CONFIG_DIR / "rom.json").read_text(encoding="utf-8")
    assert json.loads(raw)["profile_id"].startswith("buus_fury_usa_rev0")
