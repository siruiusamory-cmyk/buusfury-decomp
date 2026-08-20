import pytest

from tests.helpers import make_synthetic_rom
from tools.webfoot.gba_header import GbaHeader, GbaHeaderError, parse_gba_header


def test_valid_synthetic_header_fields(tmp_path):
    data = make_synthetic_rom(
        title="WEBFOOT TEST", game_code="BG3E", maker_code="70", revision=3
    )
    source = tmp_path / "synthetic.gba"
    source.write_bytes(data)

    header = parse_gba_header(source)

    assert header.title == "WEBFOOT TEST"
    assert header.game_code == "BG3E"
    assert header.maker_code == "70"
    assert header.software_version == 3
    assert header.header_checksum == header.calculated_checksum
    assert header.checksum_valid
    assert header.fixed_value_valid
    assert header.reserved_bytes_valid
    assert header.basic_valid


def test_checksum_tampering_is_reported():
    data = bytearray(make_synthetic_rom())
    data[0xA0] ^= 1

    header = GbaHeader.from_bytes(bytes(data))

    assert not header.checksum_valid
    assert not header.basic_valid


def test_file_too_small_is_rejected(tmp_path):
    source = tmp_path / "tiny.gba"
    source.write_bytes(bytes(0xBF))

    with pytest.raises(GbaHeaderError, match="at least 192 bytes"):
        parse_gba_header(source)


def test_non_ascii_header_field_is_rejected():
    data = bytearray(make_synthetic_rom())
    data[0xAC] = 0xFF

    with pytest.raises(GbaHeaderError, match="game code is not ASCII"):
        GbaHeader.from_bytes(bytes(data))


def test_malformed_fixed_value_is_not_valid():
    data = bytearray(make_synthetic_rom())
    data[0xB2] = 0

    header = GbaHeader.from_bytes(bytes(data))

    assert not header.fixed_value_valid
    assert not header.basic_valid
