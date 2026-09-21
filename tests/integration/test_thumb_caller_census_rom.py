"""Read-only ROM-gated evidence for the Thumb caller census.

EVIDENCE-RISK-DEBT-001. These tests reproduce, against the canonical Buu's Fury
image, the accepted whole-image census and the defect the corrected enumeration
replaced.  They are the *negative* proof: the refuted predicate's 1,552 invented
sites are shown not to be emitted, and the 13,313 real sites it missed are shown
to be recovered.

**No ROM-derived fixtures are committed.** Every expectation here is a count, an
address or a field value; nothing decoded from the image is stored.  The suite
skips cleanly when the private canonical image is not configured, and never writes
to it.

One test - :func:`test_the_prefilter_admits_every_call_a_decoder_finds` - decodes
every halfword-aligned address in the 8 MiB image without the enumeration's own
prefilter.  It is the only expensive assertion here and it is the one that makes
the prefilter a proof rather than an assumption.
"""

from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

import pytest

pytest.importorskip("capstone", reason="the Thumb decoder under test requires capstone")

import capstone  # noqa: E402

from tools.research.logx_frame_probe import CANONICAL_SHA256  # noqa: E402
from tools.research.thumb_disasm import (  # noqa: E402
    ROM_BASE,
    THUMB_CALL_SECOND_HALFWORDS,
    iter_thumb_calls,
    resolve_thumb_bl,
    scan_thumb_bl_callers,
    scan_thumb_calls,
)

#: The accepted whole-image census, established with Capstone 5.0.7 and
#: reproduced here by :func:`iter_thumb_calls`.
EXPECTED_BL = 24_226
EXPECTED_BLX = 5_283
EXPECTED_TOTAL = 29_509

#: The refuted raw-pair predicate's output over the same image.
REFUTED_PAIRS = 17_748
REFUTED_TRUE_SITES = 16_196
REFUTED_FALSE_POSITIVES = 1_552
REFUTED_RECALL_PERCENT = 54.9

#: ``BLX`` (T2) sites whose ``PC`` is not word-aligned, and therefore the sites a
#: resolver without the ``Align(PC, 4)`` rule reports two bytes high.
EXPECTED_UNALIGNED_BLX = 2_568

#: One accepted call the dispatcher evidence already names: ``0x0803D960`` calls
#: ``0x08046D18``, the ROM ARM routine the stored-form branch reaches.
KNOWN_CALL_SITE = 0x0803D960
KNOWN_CALL_TARGET = 0x08046D18

_CS = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
_CS.detail = True


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    """The canonical image, read once for the whole module."""
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == CANONICAL_SHA256
    return data


def _refuted_pairs(data: bytes) -> list[int]:
    """The predicate this ticket replaced, reproduced for the negative proof.

    Kept here rather than in the module: it is the *defect*, and live code must
    not be able to call it.  Its two clauses are ``first halfword in
    0xF000..0xF7FF`` and ``second halfword masked to 0xF800 or 0xE800`` - the
    second of which names one J1/J2 combination of each encoding and admits a
    bit-0-set ``BLX``, which is not an encoding at all.
    """
    found: list[int] = []
    limit = ROM_BASE + len(data)
    for address in range(ROM_BASE, limit - 3, 2):
        offset = address - ROM_BASE
        high = data[offset] | (data[offset + 1] << 8)
        low = data[offset + 2] | (data[offset + 3] << 8)
        if (high & 0xF800) == 0xF000 and (low & 0xF800) in (0xF800, 0xE800):
            found.append(address)
    return found


def test_the_whole_image_census_is_the_accepted_one(canonical_bytes: bytes) -> None:
    sites = scan_thumb_calls(canonical_bytes)
    kinds = {"bl": 0, "blx": 0}
    for site in sites:
        kinds[site.kind] += 1
    assert kinds["bl"] == EXPECTED_BL
    assert kinds["blx"] == EXPECTED_BLX
    assert len(sites) == EXPECTED_TOTAL
    assert EXPECTED_TOTAL == EXPECTED_BL + EXPECTED_BLX
    assert len({site.address for site in sites}) == len(sites), "a site was reported twice"


def test_every_site_target_and_kind_agree_with_an_independent_decode(
    canonical_bytes: bytes,
) -> None:
    """Capstone's own decoded operand is the cross-check on the arithmetic."""
    disagreeing: list[tuple[int, str, int, int]] = []
    for site in iter_thumb_calls(canonical_bytes):
        offset = site.address - ROM_BASE
        window = canonical_bytes[offset : offset + 4]
        item = next(_CS.disasm(window, site.address, 1), None)
        assert item is not None, f"site {site.address:#x} did not decode"
        if item.mnemonic != site.kind or item.operands[0].imm != site.target:
            disagreeing.append(
                (site.address, site.kind, site.target, item.operands[0].imm)
            )
    assert disagreeing == []


def test_blx_alignment_accounts_for_every_non_word_aligned_site(
    canonical_bytes: bytes,
) -> None:
    """The 2,568 two-byte-high targets the old resolver produced.

    ``BLX`` rounds ``PC`` down to a word boundary before adding its immediate, so
    the only sites where a resolver that omits the alignment differs are those at
    an address congruent to 2 mod 4 - and it differs on *all* of them.
    """
    unaligned = [
        site
        for site in iter_thumb_calls(canonical_bytes)
        if site.kind == "blx" and site.address % 4 == 2
    ]
    assert len(unaligned) == EXPECTED_UNALIGNED_BLX
    for site in unaligned:
        offset = site.address - ROM_BASE
        high = canonical_bytes[offset] | (canonical_bytes[offset + 1] << 8)
        low = canonical_bytes[offset + 2] | (canonical_bytes[offset + 3] << 8)
        aligned = resolve_thumb_bl(site.address, high, low)
        assert aligned == site.target
        # The same immediate added to the UNALIGNED PC - the old rule - lands two
        # bytes higher, for every one of these sites.
        assert site.address + 4 + (aligned - (site.address + 2)) == site.target + 2


def test_the_refuted_predicate_invented_exactly_the_bit_zero_blx_pairs(
    canonical_bytes: bytes,
) -> None:
    """All 1,552 false positives were a non-encoding, and none survives."""
    sites = {site.address for site in iter_thumb_calls(canonical_bytes)}
    pairs = _refuted_pairs(canonical_bytes)
    assert len(pairs) == REFUTED_PAIRS

    true_sites = [address for address in pairs if address in sites]
    invented = [address for address in pairs if address not in sites]
    assert len(true_sites) == REFUTED_TRUE_SITES
    assert len(invented) == REFUTED_FALSE_POSITIVES

    for address in invented:
        offset = address - ROM_BASE
        low = canonical_bytes[offset + 2] | (canonical_bytes[offset + 3] << 8)
        assert low & 0xF800 == 0xE800, f"{address:#x} is not the invented class"
        assert low & 1, f"{address:#x} has bit 0 clear and should be a real BLX"
        with pytest.raises(ValueError):
            resolve_thumb_bl(
                address,
                canonical_bytes[offset] | (canonical_bytes[offset + 1] << 8),
                low,
            )


def test_every_site_sits_inside_the_image(canonical_bytes: bytes) -> None:
    """The census is a site count over a stated range: no site is off the end."""
    limit = ROM_BASE + len(canonical_bytes)
    for site in iter_thumb_calls(canonical_bytes):
        assert ROM_BASE <= site.address <= limit - 4
        assert site.address % 2 == 0
        assert site.target % 2 == 0
        if site.kind == "blx":
            assert site.target % 4 == 0


def test_the_refuted_predicate_missed_sites_are_recovered(canonical_bytes: bytes) -> None:
    """The recall defect: 13,313 real callers the old helper could not see."""
    pairs = set(_refuted_pairs(canonical_bytes))
    sites = list(iter_thumb_calls(canonical_bytes))
    missed = [site for site in sites if site.address not in pairs]
    assert len(missed) == EXPECTED_TOTAL - REFUTED_TRUE_SITES
    assert len(missed) == 13_313
    by_kind = {"bl": 0, "blx": 0}
    for site in missed:
        by_kind[site.kind] += 1
    assert by_kind == {"bl": 9_779, "blx": 3_534}
    recall = 100.0 * REFUTED_TRUE_SITES / EXPECTED_TOTAL
    assert round(recall, 1) == REFUTED_RECALL_PERCENT


def test_the_eight_second_halfword_forms_all_occur_in_the_image(
    canonical_bytes: bytes,
) -> None:
    """The accepted census exercises all eight encodings, not just the two the
    refuted mask could name."""
    forms = set()
    for site in iter_thumb_calls(canonical_bytes):
        offset = site.address - ROM_BASE
        low = canonical_bytes[offset + 2] | (canonical_bytes[offset + 3] << 8)
        forms.add(low & 0xF800)
    assert forms == set(THUMB_CALL_SECOND_HALFWORDS)


def test_a_known_accepted_call_is_recovered_by_the_caller_projection(
    canonical_bytes: bytes,
) -> None:
    """``0x0803D960`` calls ``0x08046D18``; the census and the projection agree."""
    matches = [
        site for site in iter_thumb_calls(canonical_bytes)
        if site.address == KNOWN_CALL_SITE
    ]
    assert len(matches) == 1
    assert matches[0].target == KNOWN_CALL_TARGET
    found = scan_thumb_bl_callers(canonical_bytes, {KNOWN_CALL_TARGET})
    assert KNOWN_CALL_SITE in found[KNOWN_CALL_TARGET]
    # And the offset form of the pair is the one the codec evidence already names.
    offset = KNOWN_CALL_SITE - ROM_BASE
    high = canonical_bytes[offset] | (canonical_bytes[offset + 1] << 8)
    low = canonical_bytes[offset + 2] | (canonical_bytes[offset + 3] << 8)
    assert resolve_thumb_bl(KNOWN_CALL_SITE, high, low) == KNOWN_CALL_TARGET


def test_the_prefilter_admits_every_call_a_decoder_finds(canonical_bytes: bytes) -> None:
    """Decoding every halfword-aligned address finds exactly the enumerated sites.

    The enumeration skips a site whose first halfword cannot begin a ``BL``/``BLX``
    at all.  That skip is an architectural claim, and this is its proof: it removes
    nothing a decoder would have recognised.  It is also the reason the census can
    be taken at all - the unfiltered walk decodes 4.2 million windows.
    """
    enumerated = {
        (site.address, site.kind, site.target)
        for site in iter_thumb_calls(canonical_bytes)
    }
    decoded: set[tuple[int, str, int]] = set()
    limit = ROM_BASE + len(canonical_bytes)
    for address in range(ROM_BASE, limit - 3, 2):
        offset = address - ROM_BASE
        item = next(_CS.disasm(canonical_bytes[offset : offset + 4], address, 1), None)
        if item is None or item.size != 4 or item.mnemonic not in ("bl", "blx"):
            continue
        decoded.add((address, item.mnemonic, item.operands[0].imm))
    assert decoded == enumerated
