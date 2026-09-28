"""Build assembly logic: fail closed in strict mode, label provenance otherwise.

Portable. Uses a small synthetic ROM and a monkeypatched region map, so the core
provenance logic is exercised without a commercial ROM and without ADS 1.2.
"""

from __future__ import annotations

import hashlib
import json
import zlib

import pytest

from buusfury import build, identity, regions


def _synthetic_rom(size: int = 0x100) -> bytes:
    data = bytearray([0xAA] * size)
    data[0:4] = b"\x2e\x00\x00\xea"
    data[0xA0:0xAC] = b"DBZBUUSFURY\x00"
    data[0xAC:0xB0] = b"BG3E"
    data[0xB0:0xB2] = b"70"
    data[0xB2] = 0x96
    data[0xB3] = 0x00  # main unit code
    data[0xB4] = 0x00  # device type
    data[0xBC] = 0x00  # software version
    total = sum(data[0xA0:0xBD])
    data[0xBD] = (-(0x19 + total)) & 0xFF
    return bytes(data)


def _config_for(data: bytes) -> dict:
    return {
        "profile_id": "synthetic",
        "size_bytes": len(data),
        "hashes": {
            "sha1": hashlib.sha1(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "md5": hashlib.md5(data).hexdigest(),
            "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08x}",
        },
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


def _region(rid: str, start: int, end: int, cls: str) -> regions.Region:
    return regions.Region(
        id=rid, start=start, end=end, cls=cls, reference_source=f"asm/{rid}.s"
    )


@pytest.fixture
def synthetic(tmp_path, monkeypatch):
    data = _synthetic_rom()
    config = _config_for(data)
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)

    region_map = [
        _region("head", 0x00, 0x40, regions.CLASS_INCBIN),
        _region("engine", 0x40, 0x80, regions.CLASS_ADS),
        _region("tail", 0x80, 0x100, regions.CLASS_INCBIN),
    ]

    monkeypatch.setattr(regions, "load_regions", lambda path=None: list(region_map))
    monkeypatch.setattr(regions, "load_rom_size", lambda path=None: len(data))
    monkeypatch.setattr(identity, "load_canonical", lambda path=None: config)
    # The build must not reach for a real reference checkout / toolchain here.
    monkeypatch.setattr(build._assets, "default_reference_dir", lambda root=None: None)
    monkeypatch.setattr(build._assets, "default_compress_exe", lambda root=None: None)
    monkeypatch.setattr(build._toolchain, "find_grit", lambda: None)

    return rom, config, region_map


# --------------------------------------------------------------------------
# strict mode
# --------------------------------------------------------------------------
def test_strict_build_blocks_on_an_ads_region(synthetic):
    rom, _, _ = synthetic
    with pytest.raises(build.BuildBlocker) as excinfo:
        build.assemble(rom, output=None, allow_passthrough=False)
    assert excinfo.value.code == "ADS12_UNAVAILABLE"
    assert "ARM Developer Suite 1.2" in excinfo.value.summary


def test_the_blocker_names_the_affected_regions(synthetic):
    rom, _, _ = synthetic
    with pytest.raises(build.BuildBlocker) as excinfo:
        build.assemble(rom, output=None, allow_passthrough=False)
    joined = "\n".join(excinfo.value.details)
    assert "armasm" in joined
    assert "armcpp" in joined
    assert "license" in joined.lower()


def test_the_blocker_records_the_reference_link_commands(synthetic):
    rom, _, _ = synthetic
    with pytest.raises(build.BuildBlocker) as excinfo:
        build.assemble(rom, output=None, allow_passthrough=False)
    joined = "\n".join(excinfo.value.details)
    # -noremove is load-bearing and must appear in the recorded command.
    assert "-noremove" in joined
    assert "fromelf" in joined


def test_asset_region_without_a_spec_blocks_in_strict_mode(synthetic, monkeypatch):
    rom, _, _ = synthetic
    monkeypatch.setattr(
        regions,
        "load_regions",
        lambda path=None: [
            _region("head", 0x00, 0x40, regions.CLASS_INCBIN),
            _region("art", 0x40, 0x80, regions.CLASS_ASSET),
            _region("tail", 0x80, 0x100, regions.CLASS_INCBIN),
        ],
    )
    with pytest.raises(build.BuildBlocker) as excinfo:
        build.assemble(rom, output=None, allow_passthrough=False)
    assert excinfo.value.code == "ASSET_SPEC_MISSING"


# --------------------------------------------------------------------------
# passthrough mode
# --------------------------------------------------------------------------
def test_passthrough_build_reproduces_the_input_exactly(synthetic):
    rom, _, _ = synthetic
    report = build.assemble(rom, output=None, allow_passthrough=True)
    assert report.byte_identical
    assert report.output_sha1 == report.baserom_sha1


def test_passthrough_build_labels_the_ads_region_as_passthrough(synthetic):
    rom, _, _ = synthetic
    report = build.assemble(rom, output=None, allow_passthrough=True)
    by_id = {o.region_id: o for o in report.region_outcomes}
    assert by_id["engine"].provenance == build.PROVENANCE_PASSTHROUGH
    assert "PASSTHROUGH" in by_id["engine"].detail
    assert by_id["engine"].cls == regions.CLASS_ADS


def test_passthrough_build_accounts_for_every_byte(synthetic):
    rom, _, _ = synthetic
    report = build.assemble(rom, output=None, allow_passthrough=True)
    total = report.rebuilt_bytes + report.passthrough_bytes
    assert total == rom.stat().st_size


def test_passthrough_build_reports_the_blocker_without_raising(synthetic):
    rom, _, _ = synthetic
    report = build.assemble(rom, output=None, allow_passthrough=True)
    assert report.blockers
    assert report.blockers[0]["code"] == "ADS12_UNAVAILABLE"
    assert report.strict is False


def test_passthrough_build_writes_the_output_and_matches_it(synthetic, tmp_path):
    rom, _, _ = synthetic
    out = tmp_path / "out" / "image.gba"
    report = build.assemble(rom, output=out, allow_passthrough=True)
    assert out.is_file()
    assert hashlib.sha1(out.read_bytes()).hexdigest() == report.baserom_sha1


def test_build_report_serialises_to_json(synthetic, tmp_path):
    rom, _, _ = synthetic
    report = build.assemble(rom, output=None, allow_passthrough=True)
    target = tmp_path / "report.json"
    build.write_report(report, target)
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["byte_identical"] is True
    assert len(payload["region_outcomes"]) == 3


# --------------------------------------------------------------------------
# a wrong baserom must stop the build before it does anything
# --------------------------------------------------------------------------
def test_build_refuses_a_wrong_rom(tmp_path, monkeypatch):
    good = _synthetic_rom()
    config = _config_for(good)
    monkeypatch.setattr(identity, "load_canonical", lambda path=None: config)
    bad = bytearray(good)
    bad[0x10] ^= 0xFF
    rom = tmp_path / "impostor.gba"
    rom.write_bytes(bytes(bad))
    with pytest.raises(identity.IdentityError):
        build.assemble(rom, output=None, allow_passthrough=True)


def test_build_refuses_a_wrong_size(tmp_path, monkeypatch):
    good = _synthetic_rom()
    config = _config_for(good)
    monkeypatch.setattr(identity, "load_canonical", lambda path=None: config)
    rom = tmp_path / "short.gba"
    rom.write_bytes(good[:-1])
    with pytest.raises(identity.IdentityError):
        build.assemble(rom, output=None, allow_passthrough=True)
