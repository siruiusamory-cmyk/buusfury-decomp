"""Portable synthetic tests for the UI/HUD graphics probe (UI-HUD-GRAPHICS-001).

No ROM is read here.  Every fixture is a synthetic image built in memory, so the
suite proves the probe's *arithmetic* and its refusals, and the canonical
population is asserted separately by the ROM-gated integration test.

``tools.research.thumb_disasm`` needs **capstone**, which is research tooling
rather than a declared dependency of the shipping SDK, and the CI image installs
only ``.[dev]``.  The module raises ``SystemExit`` when capstone is missing, which
pytest reports as a collection INTERNALERROR, so capstone is probed *before* the
import and an environment without it skips this file cleanly instead of failing
the pipeline.  This is the same guard
``tests/unit/test_thumb_disasm_field_extraction.py`` already uses.
"""

from __future__ import annotations

import struct

import pytest

pytest.importorskip(
    "capstone",
    reason="the Thumb decoder the probe sweeps with requires capstone",
    exc_type=ImportError,
)

from tools.research import ui_graphics_probe as probe  # noqa: E402

GBA = 0x08000000

#: Host size of the synthetic fixture image.  The probe's own address arithmetic
#: is relative to ``GBA_BASE`` and independent of the image length, so a small
#: fixture exercises the same paths; the canonical 8 MiB length is asserted by the
#: ROM gate tests through ``ROM_SIZE`` directly.
FIXTURE_ROM_SIZE = 0x20000


def _image() -> bytearray:
    """A blank fixture image, large enough for the fixture addresses used here."""
    return bytearray(FIXTURE_ROM_SIZE)


def _put_word(image: bytearray, addr: int, value: int) -> None:
    struct.pack_into("<I", image, addr - GBA, value)


def _put_halfword(image: bytearray, addr: int, value: int) -> None:
    struct.pack_into("<H", image, addr - GBA, value)


def _stored_container(image: bytearray, addr: int, payload: bytes) -> None:
    """A kind-0 container: a stored copy of ``payload``."""
    _put_word(image, addr, 0)
    _put_word(image, addr + 4, len(payload))
    image[addr - GBA + 8:addr - GBA + 8 + len(payload)] = payload


# --- the 16-bit ldr-literal encoding -----------------------------------------


def test_ldr_literal_pool_arithmetic_is_pc_relative_and_word_aligned():
    """``ldr r1,[pc,#0x214]`` at 0x0800AB66 addresses 0x0800AD7C.

    The two properties that matter are checked together: the base is the
    instruction address plus four, rounded *down* to a word boundary, and the
    immediate is scaled by four.  Getting either wrong silently reads a data
    region and reports a plausible container address.
    """
    image = _image()
    site = 0x0800AB66
    _put_halfword(image, site, 0x4985)
    _put_word(image, 0x0800AD7C, 0x08055620)

    targets = probe.literal_load_targets(image, start=site, end=site + 4)
    assert len(targets) == 1
    assert targets[0]["site"] == site
    assert targets[0]["register"] == 1
    assert targets[0]["pool"] == 0x0800AD7C
    assert targets[0]["value"] == 0x08055620


def test_ldr_literal_rejects_the_sp_register_form():
    """``01001 111 imm8`` is ``ldr sp,[pc,#imm]``: a different instruction.

    Accepting it would let a data word be reported as a container literal, so
    the probe refuses it rather than resolving a pool address from it.
    """
    image = _image()
    site = 0x08000200
    _put_halfword(image, site, 0x4F00 | 0x01)  # Rt == 7 is sp
    assert probe.literal_load_targets(image, start=site, end=site + 2) == []


def test_ldr_literal_sweep_resynchronises_past_an_undecodable_halfword():
    """A dead halfword before the load site must not hide it."""
    image = _image()
    site = 0x08000200
    _put_halfword(image, site - 2, 0xDE00)  # not a valid Thumb instruction here
    _put_halfword(image, site, 0x4805)      # ldr r0,[pc,#0x14]
    pool = ((site + 4) & ~3) + 5 * 4
    _put_word(image, pool, 0x08018000)

    targets = probe.literal_load_targets(image, start=site - 2, end=site + 2)
    assert [t["site"] for t in targets] == [site]


# --- container acceptance -----------------------------------------------------


def test_stored_container_is_accepted_and_measured():
    image = _image()
    addr = 0x08018000
    _stored_container(image, addr, b"\x01\x02\x03\x04")
    assert probe.is_valid_container(image, addr)
    assert probe.container_extent(image, addr) == 8 + 4


def test_container_with_an_unrepresentable_kind_is_refused():
    image = _image()
    addr = 0x08018000
    _put_word(image, addr, 3)
    _put_word(image, addr + 4, 16)
    assert not probe.is_valid_container(image, addr)


def test_container_with_a_zero_declared_size_is_refused():
    """Kind 0 with size 0 is the engine's default container, not an asset."""
    image = _image()
    addr = 0x08018000
    _put_word(image, addr, 0)
    _put_word(image, addr + 4, 0)
    assert not probe.is_valid_container(image, addr)


def test_stored_container_running_past_the_image_is_refused():
    image = _image()
    addr = GBA + FIXTURE_ROM_SIZE - 16
    _put_word(image, addr, 0)
    _put_word(image, addr + 4, 0x1000)
    assert not probe.is_valid_container(image, addr)


def test_packed_container_whose_terminator_disagrees_is_refused():
    """A declared size no packed stream reaches exactly is not accepted.

    The packed stream here writes one literal byte and then leaves the declared
    size unreached, which the engine's own terminator rule rejects.
    """
    image = _image()
    addr = 0x08018000
    _put_word(image, addr, 1)
    _put_word(image, addr + 4, 4096)
    # A single set bit then zeros: the decoder cannot reach 4096 bytes.
    _put_word(image, addr + 8, 0x80000000)
    assert not probe.is_valid_container(image, addr)


# --- shape reading -----------------------------------------------------------


def test_shape_candidates_are_empty_for_a_non_tile_size():
    assert probe.graphics_shape_candidates(37) == []
    assert probe.graphics_shape_candidates(0) == []


def test_shape_candidates_lead_with_a_whole_screen_reading_for_8bpp_only():
    readings = probe.graphics_shape_candidates(240 * 160)
    by_depth = {entry["bits_per_pixel"]: entry for entry in readings}
    assert by_depth[8]["readings"][0] == "240x160"
    # 240x160 at 4bpp is 19,200 bytes, not 38,400: the named reading must not be
    # carried into the wrong depth.
    assert "240x160" not in by_depth[4]["readings"]


def test_every_shape_reading_fits_the_payload_at_its_own_depth():
    """The invariant that makes the function useful.

    A named reading copied into the wrong bit depth is silently 2x too large, and
    a consumer taking ``readings[0]`` would then get a framing that cannot hold
    the data.  Checked over every reading of every entry, for every size the
    canonical population presents.
    """
    sizes = [38400, 10240, 4096, 3840, 2048, 1024, 768, 672, 448, 256]
    for size in sizes:
        for entry in probe.graphics_shape_candidates(size):
            assert entry["readings"], size
            for reading in entry["readings"]:
                width, height = (int(part) for part in reading.split("x"))
                assert width * height * entry["bits_per_pixel"] // 8 == size, (
                    size,
                    entry["bits_per_pixel"],
                    reading,
                )


def test_shape_candidates_offer_both_bit_depths_when_both_divide():
    readings = probe.graphics_shape_candidates(4096)
    depths = {entry["bits_per_pixel"] for entry in readings}
    assert depths == {4, 8}
    assert all(entry["readings"] for entry in readings)


def test_shape_candidates_first_reading_always_fits_the_payload():
    for entry in probe.graphics_shape_candidates(3840):
        width, height = (int(part) for part in entry["readings"][0].split("x"))
        assert width * height * entry["bits_per_pixel"] // 8 == 3840


# --- the enumeration join ----------------------------------------------------


def _image_with_one_literal_container() -> tuple[bytearray, int]:
    """An image whose code names a stored container the corpus does not know."""
    image = _image()
    addr = 0x08018000
    _stored_container(image, addr, bytes(range(64)))
    site = 0x08001000
    _put_halfword(image, site, 0x4800 | (0 << 8) | 6)  # ldr r0,[pc,#0x18]
    pool = ((site + 4) & ~3) + 6 * 4
    _put_word(image, pool, addr)
    return image, addr


def test_enumeration_reports_the_literal_container_and_its_owner():
    image, addr = _image_with_one_literal_container()
    report = probe.enumerate_ui_containers(image, known_addresses=set(), reference_scan_end=GBA + FIXTURE_ROM_SIZE,
        code_region_end=GBA + FIXTURE_ROM_SIZE,
    )
    assert report["container_count"] == 1
    entry = report["containers"][0]
    assert entry["address"] == f"0x{addr:08X}"
    assert entry["kind"] == 0
    assert entry["declared_size"] == 64
    assert entry["packed_extent"] == 72
    assert entry["literal_load_sites"] == ["0x08001000"]


def test_enumeration_removes_containers_the_known_corpus_reaches():
    image, addr = _image_with_one_literal_container()
    report = probe.enumerate_ui_containers(image, known_addresses={addr}, reference_scan_end=GBA + FIXTURE_ROM_SIZE,
        code_region_end=GBA + FIXTURE_ROM_SIZE,
    )
    assert report["container_count"] == 0
    assert report["literal_values_that_are_not_containers"] == 0


def test_enumeration_ignores_literals_that_are_not_containers():
    image = _image()
    site = 0x08001000
    _put_halfword(image, site, 0x4800 | 6)
    pool = ((site + 4) & ~3) + 6 * 4
    _put_word(image, pool, 0x08019000)  # nothing at this address
    report = probe.enumerate_ui_containers(image, known_addresses=set(), reference_scan_end=GBA + FIXTURE_ROM_SIZE,
        code_region_end=GBA + FIXTURE_ROM_SIZE,
    )
    assert report["container_count"] == 0
    assert report["literal_values_that_are_not_containers"] == 1


def test_shared_resources_reports_a_container_named_twice():
    image = _image()
    addr = 0x08018000
    _stored_container(image, addr, bytes(64))
    for index, site in enumerate((0x08001000, 0x08001010)):
        _put_halfword(image, site, 0x4800 | 6)
        pool = ((site + 4) & ~3) + 6 * 4
        _put_word(image, pool, addr)
    report = probe.enumerate_ui_containers(image, known_addresses=set(), reference_scan_end=GBA + FIXTURE_ROM_SIZE,
        code_region_end=GBA + FIXTURE_ROM_SIZE,
    )
    shared = probe.shared_resources(report)
    assert shared["shared_by_multiple_code_sites_count"] == 1
    assert shared["shared_by_multiple_code_sites"][0]["address"] == f"0x{addr:08X}"


def test_report_states_its_own_scan_gap():
    """A negative claim must name what the sweep cannot see."""
    report = probe.enumerate_ui_containers(
        _image(), known_addresses=set(), reference_scan_end=GBA + FIXTURE_ROM_SIZE
    )
    assert "add Rd,pc,#imm" in report["scan_gap"]
    assert report["scan_gap"]


def test_container_acceptance_requires_word_alignment():
    """A container start in this engine is always word-aligned.

    Without the test, an odd address inside another container's payload passes the
    header test and is reported as a second container.
    """
    image = _image()
    addr = 0x08018000
    _stored_container(image, addr, bytes(64))
    assert probe.is_valid_container(image, addr)
    assert not probe.is_valid_container(image, addr + 1)
    assert probe.container_extent(image, addr + 1) is None


def test_report_records_the_pre_filter_corpus_hits():
    """The disjointness cross-check must be able to see a hit.

    The report records how many literal-named containers the corpus filter
    removed, so ``overlap_with_known_corpus`` intersects the pre-filter set and
    its zero is a measurement rather than a tautology.
    """
    image, addr = _image_with_one_literal_container()
    in_corpus = probe.enumerate_ui_containers(
        image,
        known_addresses={addr},
        reference_scan_end=GBA + FIXTURE_ROM_SIZE,
        code_region_end=GBA + FIXTURE_ROM_SIZE,
    )
    assert in_corpus["container_count"] == 0
    assert in_corpus["literal_values_that_are_containers"] == 1
    assert in_corpus["literal_container_values_in_known_corpus"] == [f"0x{addr:08X}"]

    not_in_corpus = probe.enumerate_ui_containers(
        image,
        known_addresses=set(),
        reference_scan_end=GBA + FIXTURE_ROM_SIZE,
        code_region_end=GBA + FIXTURE_ROM_SIZE,
    )
    assert not_in_corpus["container_count"] == 1
    assert not_in_corpus["literal_container_values_in_known_corpus"] == []


# --- the ROM gate ------------------------------------------------------------


def test_rom_gate_refuses_a_non_canonical_image():
    with pytest.raises(probe.UiGraphicsError):
        probe.verify_image(bytes(probe.ROM_SIZE))


def test_rom_gate_refuses_a_wrong_length_image():
    with pytest.raises(probe.UiGraphicsError):
        probe.verify_image(bytes(1024))
