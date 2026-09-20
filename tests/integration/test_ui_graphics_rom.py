"""ROM-gated evidence for the UI/HUD graphics probe (UI-HUD-GRAPHICS-001).

Asserts the measured code-referenced UI/HUD container population and its
disjointness from the accepted sprite / tileset / map corpus.  Every expected
value is a count, an address, a size or a raw halfword - no decoded payload is
committed.  The suite skips cleanly when the private canonical image is not
configured.

Run with ``LOGX_CANONICAL_ROM`` pointing at the image (the name the other LOGX
gates use), or place it at the default ``roms/Dragon Ball Z - Buu's Fury (U).gba``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import ui_graphics_probe as probe

ROM_PATH = Path(
    os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
)

pytestmark = pytest.mark.skipif(
    not ROM_PATH.is_file(),
    reason="canonical Buu's Fury image not configured locally",
)


@pytest.fixture(scope="module")
def rom() -> bytes:
    return probe.load_rom(ROM_PATH)


@pytest.fixture(scope="module")
def corpus(rom: bytes):
    """The accepted 11,715-container corpus, built once for the whole module."""
    from tools.research import logx_gfxscan_probe as gfxscan

    return gfxscan.build_known_corpus(rom)


@pytest.fixture(scope="module")
def report(rom: bytes, corpus) -> dict:
    return probe.enumerate_ui_containers(rom, known_addresses=set(corpus.resources))


# --- the population ----------------------------------------------------------


def test_population_is_34_code_referenced_containers_not_in_the_known_corpus(report):
    """The measured population of UI-HUD-GRAPHICS-001.

    The count is a *literal-named* count: a Thumb pool load names the address, the
    container is word-aligned with a header the container decoder selects on and an
    exact decode, and it is absent from the 11,715-container accepted corpus.  It
    is not claimed to be every UI graphic in the image; the probe's own
    ``scan_gap`` states what it cannot see.
    """
    assert report["known_corpus_size"] == 11715
    assert report["container_count"] == 34
    assert report["container_kinds"] == {0: 23, 1: 11}


def test_every_enumerated_container_is_absent_from_the_known_corpus(report, corpus):
    """The report's own disjointness flag, asserted against the corpus directly."""
    assert not (set(corpus.resources) & {item["address"] for item in report["containers"]})
    assert all(not item["in_known_corpus"] for item in report["containers"])


def test_population_is_disjoint_from_the_accepted_corpus(rom: bytes, corpus):
    """The disjointness cross-check, computed on the PRE-FILTER set.

    ``literal_container_values`` is the number of literal-named accepted
    containers before the corpus filter runs, so the intersection is a
    measurement: a hit would raise it above ``enumerated_count`` and would appear
    in ``overlap``.
    """
    overlap = probe.overlap_with_known_corpus(rom, corpus)
    assert overlap["overlap_count"] == 0
    assert overlap["overlap"] == []
    assert overlap["enumerated_count"] == 34
    assert overlap["literal_container_values"] == 34
    assert overlap["known_corpus_size"] == 11715
    # The filter removed nothing: on the canonical image the two populations are
    # already disjoint, so this is a real result and not an artefact of the order.
    assert overlap["literal_container_values"] == overlap["enumerated_count"]


def test_only_ten_of_the_population_are_observed_dispatched(report):
    """The literal names the container; it does not by itself prove the decode.

    Only a load site with a ``bl 0x0803D940`` within a short window is *observed*
    handed to the dispatcher.  The other 24 are named by a literal whose consumer
    was not observed, and that is reported rather than smoothed over.
    """
    dispatched = set(report["containers_observed_dispatched"])
    assert report["containers_observed_dispatched_count"] == 10
    assert dispatched == {
        "0x08055620",
        "0x08071758",
        "0x0807248C",
        "0x083BE3D4",
        "0x086B7E8C",
        "0x086F9EC8",
        "0x086FA398",
        "0x086FABF4",
        "0x087317C8",
        "0x08732604",
    }
    assert dispatched <= {item["address"] for item in report["containers"]}


def test_every_enumerated_container_decodes_to_its_declared_size(report):
    for item in report["containers"]:
        assert item["kind"] in (0, 1)
        assert item["declared_size"] > 0
        assert item["decoded_size"] == item["declared_size"], item["address"]


def test_every_enumerated_container_has_at_least_one_literal_load_site(report):
    for item in report["containers"]:
        assert item["literal_load_site_count"] >= 1, item["address"]
        assert item["owning_function_entries"], item["address"]


# --- the container format ----------------------------------------------------


def test_whole_screen_containers_are_exactly_240x160_at_8bpp(report):
    """Six of the 34 decode to 38400 bytes = 240 * 160, the GBA screen."""
    screens = [
        item for item in report["containers"] if item["decoded_size"] == 240 * 160
    ]
    assert len(screens) == 6
    for item in screens:
        assert item["kind"] == 1
        assert any(
            entry["readings"][0] == "240x160"
            for entry in item["shape_candidates"]
            if entry["bits_per_pixel"] == 8
        )


def test_named_container_addresses_and_sizes(report):
    """The specific containers this ticket's evidence rests on."""
    by_address = {item["address"]: item for item in report["containers"]}
    expected = {
        "0x08055620": (1, 38400),   # legal/copyright screen
        "0x083BE3D4": (1, 38400),   # title screen
        "0x086F9EC8": (1, 38400),   # publisher logo
        "0x086FA398": (1, 38400),   # publisher logo
        "0x086FABF4": (1, 38400),   # publisher logo
        "0x08732604": (1, 38400),   # full-screen bitmap
        "0x0807248C": (1, 3840),    # 240x16 strip
        "0x08071758": (1, 10240),
        "0x08071A6C": (1, 10240),
        "0x086B7E8C": (1, 256),
        "0x086B8088": (0, 1024),
        "0x087317C8": (1, 2048),
    }
    for address, (kind, size) in expected.items():
        assert address in by_address, address
        assert by_address[address]["kind"] == kind
        assert by_address[address]["decoded_size"] == size


def test_shared_containers_are_reported(report):
    shared = probe.shared_resources(report)
    assert shared["shared_by_multiple_code_sites_count"] == 20
    addresses = {item["address"] for item in shared["shared_by_multiple_code_sites"]}
    assert "0x0807248C" in addresses
    assert "0x08071758" in addresses
    assert "0x083BE3D4" in addresses


# --- the leads GRAPHICS-COVERAGE-001 recorded --------------------------------


def test_context_word_0x08071700_is_a_pool_word_not_a_graphics_table(rom: bytes):
    """The lead's own word is an EWRAM subsystem block pointer."""
    leads = probe.damage_number_lead_report(rom)
    assert leads["context_pool_word_0x08071700"] == "0x03001C4C"
    assert leads["context_pool_word_is_ewram"] is True


def test_damage_number_records_do_not_name_containers(rom: bytes):
    """``0x0806E050`` / ``0x0806F150`` are text/format records, not graphics.

    Their ``+0x00`` pointer names an all-zero-at-rest region, so the graphics the
    damage number is drawn with are not reached through them.
    """
    leads = probe.damage_number_lead_report(rom)
    for address in ("0x0806E050", "0x0806F150", "0x0806EE6C"):
        record = leads["descriptor_records"][address]
        assert record["target_is_a_container"] is False
    assert (
        leads["descriptor_records"]["0x0806E050"]["field_04_small_count"] == 7
    )
    assert (
        leads["descriptor_records"]["0x0806EE6C"]["field_04_small_count"] == 11
    )
    assert (
        leads["descriptor_records"]["0x0806F150"]["field_04_small_count"] == 0
    )


# --- the engine binding, asserted from raw halfwords -------------------------


#: Each entry is a site the enumeration rests on and the halfword the image holds
#: there.  Asserting the halfword means a re-transcription cannot drift: if the
#: instruction shape this ticket describes is not in the image, this fails.
BINDING_HALFWORDS: dict[int, int] = {
    0x0800AB54: 0xB530,  # push {r4,r5,lr} - the number-object painter
    0x0800AB66: 0x4985,  # ldr r1,[pc,#0x214] -> the context word @0x0800AD7C
    0x0800AB6A: 0x69E2,  # ldr r2,[r4,#0x1c] - the critical flag
    0x0800AB6E: 0xD100,  # bne over the normal-side read
    0x0800AB70: 0x6888,  # ldr r0,[r1,#8]
    0x0800E94E: 0x6832,  # ldr r2,[r6] - the discriminator load
    0x0800E952: 0x2A00,  # cmp r2,#0
    0x0800E954: 0xD004,  # beq to the normal arm
    0x0800E958: 0x2204,  # movs r2,#4 - critical mode
    0x0800E962: 0x2203,  # movs r2,#3 - normal mode
}

#: The context words the painter reads, and what they hold.
CONTEXT_WORDS: dict[int, int] = {
    0x08071700: 0x03001C4C,
    0x08071704: 0x0806F150,
    0x08071708: 0x0806E050,
    0x08071740: 0x08071758,
    0x08071754: 0x08071A6C,
}


def test_engine_binding_halfwords_are_present(rom: bytes):
    for address, expected in BINDING_HALFWORDS.items():
        observed = int.from_bytes(
            rom[address - probe.GBA_BASE:address - probe.GBA_BASE + 2], "little"
        )
        assert observed == expected, f"0x{address:08X}"


def test_context_words_hold_the_expected_values(rom: bytes):
    for address, expected in CONTEXT_WORDS.items():
        observed = int.from_bytes(
            rom[address - probe.GBA_BASE:address - probe.GBA_BASE + 4], "little"
        )
        assert observed == expected, f"0x{address:08X}"


def test_each_enumerated_container_load_site_resolves_to_its_container(rom: bytes):
    """Independently re-derive every pool load the enumeration rests on."""
    expected = {
        0x08004E40: 0x08055620,
        0x080051FA: 0x083BE3D4,
        0x0801E4B2: 0x083BE3D4,
        0x0801E786: 0x083BE3D4,
        0x08017A4C: 0x086F9EC8,
        0x08017A90: 0x086FA398,
        0x08017B26: 0x086FABF4,
        0x08026426: 0x08732604,
        0x08026498: 0x08732604,
        0x0800BEA4: 0x0807248C,
        0x0800BEDA: 0x0807248C,
        0x0800C14A: 0x0807248C,
        0x080364DA: 0x0807248C,
        0x08027F84: 0x08071758,
        0x08028050: 0x08071758,
        0x080281C2: 0x08071758,
        0x08024AFA: 0x087317C8,
        0x08016236: 0x086B7E8C,
        0x08017924: 0x086B7E8C,
        0x08071510: 0x08071A6C,
    }
    for site, container in expected.items():
        halfword = int.from_bytes(
            rom[site - probe.GBA_BASE:site - probe.GBA_BASE + 2], "little"
        )
        assert (halfword & 0xF800) == 0x4800, f"0x{site:08X}"
        pool = ((site + 4) & ~3) + (halfword & 0xFF) * 4
        value = int.from_bytes(
            rom[pool - probe.GBA_BASE:pool - probe.GBA_BASE + 4], "little"
        )
        assert value == container, f"0x{site:08X}"


def test_rom_hash_is_reported_and_unchanged(rom: bytes):
    assert hashlib.sha256(rom).hexdigest().upper() == probe.CANONICAL_SHA256
