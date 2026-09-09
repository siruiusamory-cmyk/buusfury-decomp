"""TOOLKIT-028 canonical capacity verification. Read-only; no emulator, no fixtures.

This pins the EVIDENCE behind the profile's free-region declaration against the
canonical image, so the declaration cannot drift away from what was verified.
"""
import hashlib
from pathlib import Path

import pytest

from tools.research.capacity_proof import report, scan_candidate_observations
from tools.research.free_space_audit import build_model, positive_control_windows
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog

SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

#: The window this ticket verified and the profile declares.
REGION_START, REGION_SIZE = 0x7EA400, 256


def canonical_rom():
    candidates = sorted(Path("roms").glob("*Buu*.gba"))
    if not candidates:
        pytest.skip("canonical Buu ROM not configured locally")
    rom = candidates[0]
    if hashlib.sha256(rom.read_bytes()).hexdigest() != SHA:
        pytest.skip("local ROM does not match exact canonical Buu identity")
    return rom


def test_declared_region_is_exactly_the_verified_window():
    """The profile declares the window this ticket proved, not a wider one."""
    catalog = RomProfileCatalog.load("config/roms.yaml")
    profile = next(p for p in catalog.profiles if p.id == "buus_fury_usa_rev0_01c1707f")
    region, = profile.free_regions
    assert (region.range.start.value, region.range.size) == (REGION_START, REGION_SIZE)
    # It is a carve of TOOLKIT-011's tail, and far smaller than it.
    assert 0x7B89A8 <= region.range.start.value and region.range.end <= 0x800000
    assert region.range.size < 0x47658
    assert "TOOLKIT-028" in region.evidence


def test_canonical_window_verifies_with_working_positive_controls():
    rom = canonical_rom()
    stamp = rom.stat().st_mtime_ns
    try:
        result = report(rom, RomRange(FileOffset(REGION_START), REGION_SIZE),
                        catalog_path="config/roms.yaml")
        assert result["profile_id"] == "buus_fury_usa_rev0_01c1707f"
        assert result["base_sha256"] == SHA
        # Every check passes on the canonical bytes.
        assert result["window"]["verdict"] == "VERIFIED"
        assert result["window"]["failed_checks"] == []
        assert result["decision"] == "WINDOW_VERIFIED_PENDING_REVIEW"
        # TOOLKIT-011's measured candidate population is reproduced exactly, so this
        # is a carve of the SAME evidence rather than a differently-scanned tail.
        assert result["candidate_observations_in_tail"] == 516
        assert result["distinct_candidate_targets"] == 475
        # A negative result only counts with working controls.
        assert result["positive_controls_pass"] is True
        for control in result["positive_controls"]:
            assert control["verdict"] == "REJECTED", control
            assert control["pass"] is True, control
        names = {c["control"].split(":")[0] for c in result["positive_controls"]}
        assert names == {"header_startup", "declared_table", "referenced_target",
                         "candidate_target"}
    finally:
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == SHA
        assert rom.stat().st_mtime_ns == stamp


def test_the_candidate_control_is_fill_inside_the_same_tail():
    """The decisive control: rejected on the candidate alone, not on fill.

    A control that were rejected merely for holding live bytes would prove nothing
    about candidate detection. This one sits in the same all-FF tail as the verified
    window, so `candidate_target` is the only thing separating them.
    """
    rom = canonical_rom()
    stamp = rom.stat().st_mtime_ns
    try:
        model = build_model(rom, catalog_path="config/roms.yaml")
        controls = {name: (span, expect)
                    for name, span, expect in positive_control_windows(model)}
        name = next(n for n in controls if n.startswith("candidate_target"))
        span, _ = controls[name]
        image = model["image"]
        assert set(image[span.start.value:span.end]) == {0xFF}
        assert model["tail"].start.value <= span.start.value < model["tail"].end
    finally:
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == SHA
        assert rom.stat().st_mtime_ns == stamp


def test_no_historical_candidate_can_overlap_the_declared_region():
    """All 516 of TOOLKIT-011's candidates stay outside the declared bytes.

    They are not resolved and not whitelisted; the region is simply carved to
    contain none of them, and each still blocks the bytes it addresses.
    """
    rom = canonical_rom()
    stamp = rom.stat().st_mtime_ns
    try:
        model = build_model(rom, catalog_path="config/roms.yaml")
        observations = scan_candidate_observations(model["image"], model["tail"])
        assert len(observations) == 516
        end = REGION_START + REGION_SIZE
        assert not [o for o in observations if REGION_START <= o["target"] < end]
        assert not [o for o in observations if REGION_START <= o["source"] < end]
        # The nearest candidate on either side clears the required margin.
        targets = sorted({o["target"] for o in observations})
        below = [t for t in targets if t < REGION_START]
        above = [t for t in targets if t >= end]
        assert REGION_START - max(below) == 1717
        assert min(above) - end == 2816
    finally:
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == SHA
        assert rom.stat().st_mtime_ns == stamp
