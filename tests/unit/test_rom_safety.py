import os

import pytest

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot.profile import RomProfileCatalog, VerificationStatus
from tools.webfoot.rom import RomChangedError, RomReadError, identify_rom
import tools.webfoot.rom as rom_module


def test_identify_does_not_modify_input(tmp_path):
    source = tmp_path / "synthetic.gba"
    source.write_bytes(make_synthetic_rom())
    before_bytes = source.read_bytes()
    before_stat = source.stat()
    catalog = RomProfileCatalog([profile_for(before_bytes)])

    result = identify_rom(source, catalog)

    after_stat = source.stat()
    assert result.profile_match.status is VerificationStatus.VERIFIED
    assert source.read_bytes() == before_bytes
    assert after_stat.st_size == before_stat.st_size
    assert after_stat.st_mtime_ns == before_stat.st_mtime_ns


def test_unknown_rom_is_safe_and_explicit(tmp_path):
    source = tmp_path / "unknown.gba"
    source.write_bytes(make_synthetic_rom())
    before = source.read_bytes()

    result = identify_rom(source, RomProfileCatalog([]))

    assert result.profile_match.status is VerificationStatus.UNKNOWN
    assert source.read_bytes() == before


def test_missing_path_fails_cleanly(tmp_path):
    missing = tmp_path / "missing.gba"

    try:
        identify_rom(missing, RomProfileCatalog([]))
    except RomReadError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("identify_rom accepted a missing path")


def test_metadata_change_during_read_fails_loudly(tmp_path, monkeypatch):
    source = tmp_path / "changing.gba"
    data = make_synthetic_rom()
    source.write_bytes(data)
    catalog = RomProfileCatalog([profile_for(data)])
    original_hash_stream = rom_module.hash_stream

    def hash_then_touch(stream, **kwargs):
        result = original_hash_stream(stream, **kwargs)
        stat = source.stat()
        os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000))
        return result

    monkeypatch.setattr(rom_module, "hash_stream", hash_then_touch)

    with pytest.raises(RomChangedError, match="changed while being identified"):
        identify_rom(source, catalog)
