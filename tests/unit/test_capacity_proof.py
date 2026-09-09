"""TOOLKIT-028 synthetic capacity-verification discipline.

These are portable: they build small images rather than reading any ROM, so they
pin the POLICY - what the verifier accepts, what it refuses, and that a negative
result is only reported alongside working positive controls.
"""
import struct

import pytest

from tools.research.capacity_proof import (DEFAULT_MARGIN, HEADER_END, positive_controls,
                                           scan_candidate_observations, verify_window)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import ProfileConfigError, _free_regions


def image_with(size=0x2000, fill=0xFF, live_end=0x1000):
    """Live content below `live_end`, tail fill above it."""
    return bytearray(b"\x00" * live_end + bytes((fill,)) * (size - live_end))


def window(start, size):
    return RomRange(FileOffset(start), size)


def test_clean_window_in_fill_verifies():
    image = image_with()
    report = verify_window(bytes(image), window(0x1400, 0x100),
                           observations=[], owned=[], references=[])
    assert report["verdict"] == "VERIFIED"
    assert report["failed_checks"] == []
    assert set(report["checks"]) == {"bounds", "fill", "known_inbound", "known_overlap",
                                     "candidate_target", "candidate_source", "margin"}


def test_candidate_target_inside_window_blocks_it():
    """The load-bearing refusal: an unresolved candidate still blocks its bytes."""
    image = image_with()
    obs = [{"source": 0x20, "target": 0x1450, "source_word_aligned": True}]
    report = verify_window(bytes(image), window(0x1400, 0x100),
                           observations=obs, owned=[], references=[])
    assert report["verdict"] == "REJECTED"
    assert "candidate_target" in report["failed_checks"]
    assert report["checks"]["candidate_target"]["count"] == 1


def test_unaligned_candidate_target_blocks_it_too():
    """An unaligned observation is not dismissed as coincidence by this scanner."""
    image = image_with()
    obs = [{"source": 0x21, "target": 0x1451, "source_word_aligned": False}]
    report = verify_window(bytes(image), window(0x1400, 0x100),
                           observations=obs, owned=[], references=[])
    assert "candidate_target" in report["failed_checks"]


def test_candidate_sourced_inside_window_blocks_it():
    """Writing the window must not alter a word some unknown consumer reads."""
    image = image_with()
    obs = [{"source": 0x1440, "target": 0x1900, "source_word_aligned": True}]
    report = verify_window(bytes(image), window(0x1400, 0x100),
                           observations=obs, owned=[], references=[])
    assert "candidate_source" in report["failed_checks"]


def test_known_reference_and_annotation_block_the_window():
    image = image_with()
    refs = [{"source": 0x10, "target": 0x1410, "classification": "CONFIRMED_REFERENCE"}]
    owned = [{"start": 0x1480, "end": 0x1490, "kind": "declared_table", "owner": "t"}]
    report = verify_window(bytes(image), window(0x1400, 0x100),
                           observations=[], owned=owned, references=refs)
    assert set(report["failed_checks"]) == {"known_inbound", "known_overlap"}


def test_non_fill_bytes_block_the_window():
    image = image_with()
    image[0x1450] = 0x01
    report = verify_window(bytes(image), window(0x1400, 0x100),
                           observations=[], owned=[], references=[])
    assert report["failed_checks"] == ["fill"]


def test_window_below_the_header_is_refused():
    image = image_with(live_end=0)
    report = verify_window(bytes(image), window(0, 0x100),
                           observations=[], owned=[], references=[])
    assert "bounds" in report["failed_checks"]
    assert HEADER_END == 0x158


def test_margin_is_enforced_against_the_nearest_candidate():
    """A window clear of every candidate can still be refused for sitting too close."""
    image = image_with(size=0x8000, live_end=0x1000)
    near = 0x4000
    obs = [{"source": 0x20, "target": near, "source_word_aligned": True}]
    # Flush against the candidate: no candidate is INSIDE, but the margin fails.
    tight = verify_window(bytes(image), window(near + 4, 0x40),
                          observations=obs, owned=[], references=[])
    assert tight["checks"]["candidate_target"]["pass"] is True
    assert tight["failed_checks"] == ["margin"]
    # Beyond the required clearance the same window verifies.
    far = verify_window(bytes(image), window(near + DEFAULT_MARGIN, 0x40),
                        observations=obs, owned=[], references=[])
    assert far["verdict"] == "VERIFIED"


def test_scan_finds_targets_at_every_byte_position():
    image = bytearray(0x2000)
    image[0x1000:] = b"\xff" * 0x1000
    struct.pack_into("<I", image, 0x10, 0x08001400)   # aligned source
    struct.pack_into("<I", image, 0x25, 0x08001500)   # unaligned source
    hits = scan_candidate_observations(bytes(image), window(0x1000, 0x1000))
    found = {(h["source"], h["target"], h["source_word_aligned"]) for h in hits}
    assert (0x10, 0x1400, True) in found
    assert (0x25, 0x1500, False) in found


def test_positive_controls_report_pass_only_on_the_named_check():
    """A control that fails for the WRONG reason does not count as a control."""
    image = image_with()
    obs = [{"source": 0x20, "target": 0x1450, "source_word_aligned": True}]
    controls = [
        # Fails on candidate_target, as named: a real control.
        ("candidate", window(0x1450, 4), ("candidate_target",)),
        # Fails, but on `fill`, not on the named check: NOT a valid control.
        ("mislabelled", window(0x0400, 4), ("candidate_target",)),
    ]
    results = positive_controls(bytes(image), obs, [], [], controls)
    by_name = {r["control"]: r for r in results}
    assert by_name["candidate"]["pass"] is True
    assert by_name["mislabelled"]["verdict"] == "REJECTED"
    assert by_name["mislabelled"]["pass"] is False


def test_a_blind_scanner_fails_its_own_control():
    """If the verifier stopped detecting candidates, the control would catch it."""
    image = image_with()
    # No observations supplied at all - the scanner is 'blind' by construction.
    controls = [("candidate", window(0x1450, 4), ("candidate_target",))]
    results = positive_controls(bytes(image), [], [], [], controls)
    assert results[0]["verdict"] == "VERIFIED"
    assert results[0]["pass"] is False


@pytest.mark.parametrize("status", ["CANDIDATE", "CANDIDATE_REFERENCE", "UNKNOWN",
                                    "WINDOW_VERIFIED_PENDING_REVIEW"])
def test_a_verification_verdict_is_not_itself_a_production_declaration(status):
    """The research verdict cannot be pasted into a profile; review must promote it."""
    with pytest.raises(ProfileConfigError, match="CONFIRMED"):
        _free_regions([{"file_offset": 0x1400, "size": 0x100, "status": status,
                        "evidence": "TOOLKIT-028 window verification"}], 0x2000)
