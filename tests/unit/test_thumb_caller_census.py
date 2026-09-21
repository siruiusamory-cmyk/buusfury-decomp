"""Portable tests for the authoritative Thumb caller census.

EVIDENCE-RISK-DEBT-001. The helper these tests pin replaced a raw halfword
predicate that matched a first halfword in ``0xF000..0xF7FF`` followed by a second
halfword masked to ``0xF800`` or ``0xE800``. Measured on the canonical image that
predicate invented 1,552 sites, recognised only one J1/J2 combination of each
encoding, and resolved every ``BLX`` at a non-word-aligned address two bytes high.

Every fixture here is **generated** from the architectural encoding, not copied out
of the image: :func:`_encode_branch` builds the halfword pair for a requested
``(address, target)`` pair, and the encoding tests first assert that Capstone
decodes the fixture to the target it was built for. That makes the fixture
generator itself part of what is under test - a generator that could not produce a
valid encoding could not silently pass by producing nothing.

The ROM-gated half of this ticket lives in
``tests/integration/test_thumb_caller_census_rom.py``, which reproduces the
accepted whole-image census.

``tools.research.thumb_disasm`` needs **capstone**, which is research tooling
rather than a declared dependency of the shipping SDK, and the CI image installs
only ``.[dev]``. The module raises ``SystemExit`` when capstone is missing, which
pytest reports as a collection INTERNALERROR, so capstone is probed *before* the
import and an environment without it skips this file cleanly.
"""

from __future__ import annotations

import struct

import pytest

pytest.importorskip(
    "capstone", reason="the Thumb decoder under test requires capstone"
)

import capstone  # noqa: E402

from tools.research.thumb_disasm import (  # noqa: E402
    ROM_BASE,
    THUMB_CALL_SECOND_HALFWORDS,
    ThumbCallSite,
    iter_thumb_calls,
    resolve_thumb_bl,
    scan_thumb_bl_callers,
    scan_thumb_calls,
)

_CS = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
_CS.detail = True


# --- fixture construction ----------------------------------------------------

def _encode_branch(offset: int, *, blx: bool) -> tuple[int, int]:
    """The halfword pair encoding ``BL``/``BLX`` with the given 25-bit offset.

    Written straight from the encoding table: ``11110 S imm10`` then
    ``11 J1 1 J2 imm11`` for ``BL`` (T1) and ``11 J1 0 J2 imm10H 0`` for ``BLX``
    (T2), with ``I1 = NOT(J1 XOR S)`` and ``I2 = NOT(J2 XOR S)``.
    """
    assert -(1 << 24) <= offset < (1 << 24), "offset is not a 25-bit signed value"
    assert offset % (4 if blx else 2) == 0, "offset breaks the encoding's low bits"
    sign = (offset >> 24) & 1
    i1 = (offset >> 23) & 1
    i2 = (offset >> 22) & 1
    imm10 = (offset >> 12) & 0x3FF
    j1 = 1 - (i1 ^ sign)
    j2 = 1 - (i2 ^ sign)
    high = 0xF000 | (sign << 10) | imm10
    if blx:
        low = 0xC000 | (j1 << 13) | (j2 << 11) | (((offset >> 2) & 0x3FF) << 1)
    else:
        # ``11 J1 1 J2 imm11``: 0xD000 supplies the two leading ones and the
        # bit-12 discriminator, leaving both J positions clear so ``j1``/``j2``
        # are *set* rather than OR-ed onto a base that already held them.
        low = 0xD000 | (j1 << 13) | (j2 << 11) | ((offset >> 1) & 0x7FF)
    return high, low


def _target_of(address: int, offset: int, kind: str) -> int:
    """The target the architecture produces for an offset under ``kind``."""
    if kind == "bl":
        return address + 4 + offset
    return ((address + 4) & ~3) + offset


def _halfwords(address: int, target: int, kind: str) -> tuple[int, int]:
    return _encode_branch(_offset_for(address, target, kind), blx=(kind == "blx"))


def _offset_for(address: int, target: int, kind: str) -> int:
    if kind == "bl":
        return target - (address + 4)
    return target - ((address + 4) & ~3)


def _thumb(*halfwords: int) -> bytes:
    return b"".join(struct.pack("<H", halfword) for halfword in halfwords)


def _decoded(address: int, image: bytes) -> tuple[str, int]:
    """What Capstone itself makes of the four bytes at ``address``.

    ``("", 0)`` means the window holds no decodable instruction at all, which is
    also not a call site.
    """
    offset = address - ROM_BASE
    item = next(_CS.disasm(image[offset : offset + 4], address, 1), None)
    if item is None:
        return "", 0
    return item.mnemonic, item.operands[0].imm


def _decodes_as(high: int, low: int) -> tuple[str, int]:
    """Capstone's reading of one halfword pair, laid out at ``ROM_BASE``."""
    return _decoded(ROM_BASE, _thumb(high, low))


def _image(requests: list[tuple[int, str, int]]) -> tuple[bytes, list[ThumbCallSite]]:
    """Lay out ``(file offset, kind, target)`` requests into a synthetic image."""
    size = max(offset + 4 for offset, _, _ in requests)
    buffer = bytearray(size)
    expected: list[ThumbCallSite] = []
    for offset, kind, target in requests:
        address = ROM_BASE + offset
        high, low = _halfwords(address, target, kind)
        struct.pack_into("<HH", buffer, offset, high, low)
        expected.append(ThumbCallSite(address=address, kind=kind, target=target))
    return bytes(buffer), sorted(expected, key=lambda site: site.address)


def _assert_fixture_decodes(address: int, target: int, kind: str) -> None:
    """The generator produced a real instruction, not just matching bits.

    The pair is laid out at its own file offset, because both encodings compute
    their target from the *address* and a pair moved to ``ROM_BASE`` would decode
    to a different one.
    """
    image, _ = _image([(address - ROM_BASE, kind, target)])
    assert _decoded(address, image) == (kind, target)


# --- the fixture generator is itself checked --------------------------------

@pytest.mark.parametrize("address_mod", (0, 2))
@pytest.mark.parametrize("kind", ("bl", "blx"))
@pytest.mark.parametrize(
    "offset", (2, 4, 0x40, 0x1234, 0x0FFF_FFC, -4, -0x1234, -0x0FFF_FFC)
)
def test_the_fixture_encoder_produces_encodings_capstone_agrees_with(
    address_mod: int, kind: str, offset: int
) -> None:
    if kind == "blx" and offset % 4:
        return
    address = ROM_BASE + 0x100 + address_mod
    _assert_fixture_decodes(address, _target_of(address, offset, kind), kind)


# --- BL and BLX are recovered, with architectural targets --------------------

def test_a_bl_site_is_recovered_with_its_exact_target() -> None:
    image, expected = _image([(0x10, "bl", ROM_BASE + 0x400)])
    assert scan_thumb_calls(image) == expected
    _assert_fixture_decodes(ROM_BASE + 0x10, ROM_BASE + 0x400, "bl")


def test_a_blx_site_is_recovered_with_its_exact_target() -> None:
    image, expected = _image([(0x10, "blx", ROM_BASE + 0x404)])
    assert scan_thumb_calls(image) == expected
    _assert_fixture_decodes(ROM_BASE + 0x10, ROM_BASE + 0x404, "blx")


@pytest.mark.parametrize("kind", ("bl", "blx"))
@pytest.mark.parametrize("backwards", (False, True))
def test_the_target_is_exact_for_both_encodings_in_both_directions(
    kind: str, backwards: bool
) -> None:
    address = ROM_BASE + 0x100
    target = ROM_BASE + 0x40 if backwards else ROM_BASE + 0x900
    image, _ = _image([(0x100, kind, target)])
    assert [site.target for site in scan_thumb_calls(image)] == [target]
    assert _decoded(address, image)[1] == target


@pytest.mark.parametrize("address_mod", (0, 2))
@pytest.mark.parametrize("kind", ("bl", "blx"))
def test_resolution_covers_the_whole_encoding_space(
    address_mod: int, kind: str
) -> None:
    """A spread of S/I1/I2/imm combinations, at both address alignments.

    The old resolver was exact for ``BL`` and wrong for ``BLX``, and the
    difference is architectural rather than a slip in the immediate arithmetic, so
    one worked example cannot pin it.
    """
    address = ROM_BASE + 0x4000 + address_mod
    offsets = [
        2, 4, 6, 0x10, 0x7FE, 0x800, 0x1234, 0x3F_FFE, 0x7F_FFE, 0x0FF_FFC,
        -2, -4, -6, -0x7FE, -0x1234, -0x3F_FFE, -0x7F_FFE, -0x0FF_FFC,
    ]
    checked = 0
    for offset in offsets:
        if kind == "blx" and offset % 4:
            continue
        target = _target_of(address, offset, kind)
        high, low = _halfwords(address, target, kind)
        assert resolve_thumb_bl(address, high, low) == target
        _assert_fixture_decodes(address, target, kind)
        checked += 1
    assert checked >= 8


def test_a_blx_target_cannot_be_odd() -> None:
    """``BLX`` (T2) reserves bit 0 of its immediate, so its target is word-aligned."""
    address = ROM_BASE + 0x200
    for target in (ROM_BASE + 0x400, ROM_BASE + 0x800, ROM_BASE + 0x1000):
        high, low = _halfwords(address, target, "blx")
        assert low & 1 == 0
        assert resolve_thumb_bl(address, high, low) % 2 == 0


# --- the BLX alignment rule, pinned ------------------------------------------

@pytest.mark.parametrize("address_mod", (0, 2))
def test_blx_pc_is_aligned_down_and_bl_pc_is_not(address_mod: int) -> None:
    """The one architectural difference between the two encodings.

    ``BL`` adds its immediate to ``address + 4``; ``BLX`` adds it to
    ``Align(address + 4, 4)``. At an address that is not word-aligned those differ
    by two bytes, and a resolver that ignores the alignment reports every such
    ``BLX`` target two bytes high.
    """
    address = ROM_BASE + 0x800 + address_mod
    offset = 0x100
    bl_target = address + 4 + offset
    blx_target = ((address + 4) & ~3) + offset

    assert resolve_thumb_bl(address, *_halfwords(address, bl_target, "bl")) == bl_target
    assert resolve_thumb_bl(address, *_halfwords(address, blx_target, "blx")) == blx_target
    _assert_fixture_decodes(address, bl_target, "bl")
    _assert_fixture_decodes(address, blx_target, "blx")
    if address_mod == 2:
        assert blx_target != address + 4 + offset


def test_the_unaligned_reading_of_a_blx_site_is_two_bytes_high() -> None:
    """The regression the old resolver had, stated as an inequality."""
    address = ROM_BASE + 0x902  # not word-aligned
    offset = 0x40
    target = ((address + 4) & ~3) + offset
    assert resolve_thumb_bl(address, *_halfwords(address, target, "blx")) == target
    assert address + 4 + offset == target + 2


# --- validity: what the old predicate invented -------------------------------

def test_a_blx_second_halfword_with_bit_zero_set_is_not_a_site() -> None:
    """``BLX`` (T2) reserves bit 0 of its second halfword.

    The refuted predicate masked the second halfword to ``0xE800`` and accepted any
    pair matching it, so a bit-0-set pair - not an encoding at all - was reported as
    a caller. All 1,552 false positives the old helper produced were exactly this.
    """
    high, low = 0xF000, 0xE801
    assert (high & 0xF800) == 0xF000 and (low & 0xF800) == 0xE800
    assert low & 1, "the fixture must have bit 0 set"
    assert scan_thumb_calls(_thumb(high, low)) == []
    with pytest.raises(ValueError, match="not a Thumb BL/BLX encoding"):
        resolve_thumb_bl(ROM_BASE, high, low)


def test_validity_of_the_second_halfword_is_decided_as_the_architecture_does() -> None:
    """Every one of the 65,536 second halfwords, against Capstone.

    The accepted set is exactly the second halfwords that make the four bytes a
    four-byte ``bl`` or ``blx``: the eight masked forms, minus a bit-0-set
    ``BLX``.  The halfword pair itself and a decode of it are the only two
    opinions consulted, and they must never disagree.
    """
    high = 0xF000
    accepted_forms: set[int] = set()
    for low in range(0x10000):
        site = scan_thumb_calls(_thumb(high, low))
        mnemonic, _ = _decodes_as(high, low)
        decoded_is_call = mnemonic in ("bl", "blx")
        if decoded_is_call:
            assert len(site) == 1, f"{low:#06x} is a {mnemonic} but was not a site"
            accepted_forms.add(low & 0xF800)
        else:
            assert site == [], f"{low:#06x} is not a call but was reported"
    assert sorted(accepted_forms) == sorted(THUMB_CALL_SECOND_HALFWORDS)


def test_a_first_halfword_outside_the_wide_branch_range_is_not_a_site() -> None:
    for high in (0xEFFF, 0xF800, 0xB500, 0x0000):
        assert scan_thumb_calls(_thumb(high, 0xF800)) == []
        with pytest.raises(ValueError):
            resolve_thumb_bl(ROM_BASE, high, 0xF800)


def test_the_old_predicate_would_have_seen_two_of_the_eight_forms() -> None:
    """The recall defect, in one line: the refuted mask names one J1/J2 combination.

    ``0xD000``/``0xD800``/``0xF000`` (the other three ``BL`` forms) and
    ``0xC000``/``0xC800``/``0xE000`` (three ``BLX`` forms) are all outside the old
    mask, which is why it recovered 16,196 of the accepted 29,509 sites.
    """
    old_mask = (0xF800, 0xE800)
    recognised = [form for form in THUMB_CALL_SECOND_HALFWORDS if form in old_mask]
    assert recognised == [0xE800, 0xF800]
    for form in THUMB_CALL_SECOND_HALFWORDS:
        low = form  # a zero immediate in both encodings
        assert len(scan_thumb_calls(_thumb(0xF000, low))) == 1
    for form in (0xC000, 0xC800, 0xD000, 0xD800, 0xE000, 0xF000):
        assert (form & 0xF800) not in old_mask


# --- caller projection -------------------------------------------------------

def test_scan_thumb_bl_callers_projects_sites_onto_cleared_targets() -> None:
    image, _ = _image(
        [
            (0x10, "bl", ROM_BASE + 0x400),
            (0x20, "blx", ROM_BASE + 0x404),
            (0x30, "bl", ROM_BASE + 0x900),
        ]
    )
    found = scan_thumb_bl_callers(image, {ROM_BASE + 0x401, ROM_BASE + 0x900})
    assert found == {
        ROM_BASE + 0x400: [ROM_BASE + 0x10],
        ROM_BASE + 0x900: [ROM_BASE + 0x30],
    }
    # A requested target with no caller is present and empty, not absent.
    assert scan_thumb_bl_callers(image, {ROM_BASE + 0x1000}) == {ROM_BASE + 0x1000: []}


def test_include_blx_selects_only_calls_that_stay_in_thumb_code() -> None:
    image, _ = _image(
        [
            (0x10, "bl", ROM_BASE + 0x400),
            (0x20, "blx", ROM_BASE + 0x400),
        ]
    )
    targets = {ROM_BASE + 0x400}
    assert scan_thumb_bl_callers(image, targets) == {
        ROM_BASE + 0x400: [ROM_BASE + 0x10, ROM_BASE + 0x20]
    }
    assert scan_thumb_bl_callers(image, targets, include_blx=False) == {
        ROM_BASE + 0x400: [ROM_BASE + 0x10]
    }


def test_the_kind_is_reported_rather_than_flattened() -> None:
    image, _ = _image(
        [
            (0x10, "bl", ROM_BASE + 0x400),
            (0x20, "blx", ROM_BASE + 0x400),
        ]
    )
    sites = scan_thumb_calls(image)
    assert [site.kind for site in sites] == ["bl", "blx"]
    assert all(isinstance(site, ThumbCallSite) for site in sites)


def test_the_scan_range_is_respected() -> None:
    image, _ = _image([(0x40, "bl", ROM_BASE + 0x400)])
    assert len(list(iter_thumb_calls(image))) == 1
    assert scan_thumb_calls(image, start=ROM_BASE, end=ROM_BASE + 0x40) == []
    assert len(scan_thumb_calls(image, start=ROM_BASE, end=ROM_BASE + 0x44)) == 1
    assert scan_thumb_calls(image, start=ROM_BASE + 0x42) == []


def test_every_halfword_aligned_site_is_considered_not_just_sweep_boundaries() -> None:
    """The stride is two bytes, so a site behind a wider instruction is not lost.

    A resynchronising sweep advances by the size of what it decodes, so four bytes
    at ``+0`` that decode as one Thumb-2 instruction hide a real site at ``+2``. A
    caller census must not depend on which of two overlapping decodes a library
    prefers, so the enumeration strides two bytes and offers every site a
    four-byte window.
    """
    address = ROM_BASE + 2
    target = ROM_BASE + 0xC00
    high, low = _halfwords(address, target, "bl")
    # ``pop.w`` occupies the four bytes at ROM_BASE, so a sweep advancing by the
    # decoded size steps straight from 0 to 4 and never looks at 2. Its own bytes
    # are irrelevant to the census: the site's window starts at the site.
    image = _thumb(0xE8BD) + _thumb(high, low)
    first = next(_CS.disasm(image[0:4], ROM_BASE, 1), None)
    assert first is not None and first.size == 4
    assert first.mnemonic not in ("bl", "blx")
    sites = scan_thumb_calls(image)
    assert ThumbCallSite(address=address, kind="bl", target=target) in sites
    assert _decoded(address, image)[1] == target
