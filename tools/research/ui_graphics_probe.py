"""UI-HUD-GRAPHICS-001: enumerate the UI/HUD graphics containers the engine
addresses directly from its own code.

This is a *research probe*, not a shipping exporter.  It reads the canonical
image read-only, refuses any other image by SHA-256, and emits addresses, counts,
sizes and extents only - never a decoded payload, never a written asset.

Why this population and not a byte scan
---------------------------------------
GRAPHICS-COVERAGE-001 left the UI/HUD family PARTIAL / UNRESOLVED with three
leads: a descriptor system "around ``0x08071700``" and the damage-number assets
``0x0806E050`` / ``0x0806F150``.  This probe records what those leads actually
are, from the image, and enumerates the population that *is* deterministic.

* ``0x08071700`` is **not** a graphics table.  It is a word inside a table of
  subsystem blocks that ``0x0800AB54`` reaches by a PC-relative literal load and
  then reads ``[base+4]`` / ``[base+8]`` from, which land on ``0x0806F150`` and
  ``0x0806E050``.  Those two words are themselves residents of the same table,
  not container headers: each is ``{u32 rom_ptr, u32 small_count}``.
* ``0x0806E050`` / ``0x0806F150`` / ``0x0806EE6C`` are **text/format descriptor
  records**, not graphics.  Their ``+0x00`` names a region that is all zero at
  rest (``0x0806D4E0``), their ``+0x04`` is a small count, and at ``+0x40`` /
  ``+0x48`` they carry u16 pair tables that ascend like glyph layout metrics.
  They are selected by the critical-hit flag and handed to the text/OAM path, so
  the damage *number* is drawn through the font/OAM machinery; the damage-number
  *graphics* are therefore not a separate container family reachable from them.
* The real UI/HUD graphics are reached the way every other engine-reachable
  container in this project is reached: a Thumb ``ldr Rt,[pc,#imm]`` loads the
  container address out of the code's own literal pool and hands it to the
  container dispatcher ``0x0803D940``.

Enumeration rule
----------------
1. Decode the code region (``0x08000000..CODE_REGION_END``) as Thumb, with
   resynchronisation, and record every ``ldr Rt,[pc,#imm8*4]`` and the word it
   addresses.  This is the *only* way the engine names a container address; no
   accepted graph in this project reaches a sprite, map or portrait container by
   a data-embedded pointer either.
2. Keep the literal values that are valid Webfoot containers (kind 0/1/2, a
   non-zero declared size, and - for the packed kinds - an exact decode).
3. Remove the ones the accepted known corpus already reaches (the 11,715
   containers of ``logx_gfxscan_probe.build_known_corpus``), so the probe reports
   the family that is *outside* the map/tile/sprite pipelines.
4. For each survivor, join every aligned word occurrence anywhere in the image,
   split into code-region and data-region references, and report the containing
   Thumb function prologue for each code reference.

The result is a *code-referenced* population, deliberately not a scanner
population: a successful decode is not proof of graphics (GRAPHICS-COVERAGE-001,
and LOGX-GFXSCAN-001's false-positive classes), and bytes that merely decode are
not enumerated here.

Scope, stated rather than implied
---------------------------------
The rule is complete only *relative to its own scan gap*.  ``add Rd,pc,#imm``,
``ldr`` from a register-computed base and any ARM-state or IWRAM-resident loader
are outside the sweep; a container named only that way would be missed.  The
probe reports that gap in its own output rather than leaving it in prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.research import logx_gfxscan_probe as gfxscan
from tools.research import thumb_disasm
from tools.research import webfoot_codec_reference as reference

CANONICAL_SHA256 = "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"
GBA_BASE = 0x08000000
ROM_SIZE = 8 * 1024 * 1024

#: End of the executable region the probe decodes as Thumb.  The image's own code
#: is well inside this; the bound is host policy, and the sweep reports it.
CODE_REGION_END = 0x080BB000

#: The container dispatcher the engine hands every container address to.
CONTAINER_DISPATCHER = 0x0803D940

#: Container forms the dispatcher accepts: kind ``0`` is a stored copy, ``1`` and
#: ``2`` are the packed forms (LOGX-CODEC-001).
DISPATCHER_KINDS = (0, 1, 2)

#: Sizes that are a whole number of 8x8 tiles at one of the two bit depths the
#: canonical corpus uses.  Reported as a *shape* candidate only; see
#: :func:`graphics_shape_candidates`.
TILE_BYTES_8BPP = 64
TILE_BYTES_4BPP = 32

#: Decoded sizes the canonical UI population presents.  Named so the report does
#: not have to describe them in prose, and so a drift is visible.
FULL_SCREEN_8BPP = 240 * 160
MENU_CELL_8BPP = 128 * 80

_SCAN_GAP = (
    "add Rd,pc,#imm, ldr from a register-computed base, ARM-state code, and any "
    "IWRAM-resident loader are outside this sweep; a container named only that "
    "way is not enumerated here"
)


class UiGraphicsError(RuntimeError):
    """Canonical-ROM gate, or a malformed probe input."""


# --- ROM access ---------------------------------------------------------------


def verify_image(data: bytes) -> bytes:
    """Fail closed unless ``data`` is the canonical Buu's Fury image.

    Split out from :func:`load_rom` so the gate is testable without a filesystem:
    the gate is the part that must not be wrong, and a test that has to create a
    temporary file to exercise it is a test that can be skipped for the wrong
    reason.
    """
    if len(data) != ROM_SIZE:
        raise UiGraphicsError(f"image is {len(data)} bytes, expected {ROM_SIZE}")
    actual = hashlib.sha256(data).hexdigest().upper()
    if actual != CANONICAL_SHA256:
        raise UiGraphicsError(
            f"refusing non-canonical image: expected {CANONICAL_SHA256}, got {actual}"
        )
    return data


def load_rom(path: str | Path) -> bytes:
    """Read the canonical image, failing closed on any other hash."""
    return verify_image(Path(path).read_bytes())


def _u16(data: bytes, addr: int) -> int:
    return struct.unpack_from("<H", data, addr - GBA_BASE)[0]


def _u32(data: bytes, addr: int) -> int:
    return struct.unpack_from("<I", data, addr - GBA_BASE)[0]


def is_rom_pointer(data: bytes, value: int) -> bool:
    return GBA_BASE <= value < GBA_BASE + len(data)


# --- the sweep ----------------------------------------------------------------


def literal_load_targets(
    data: bytes,
    *,
    start: int = GBA_BASE,
    end: int = CODE_REGION_END,
) -> list[dict]:
    """Every Thumb ``ldr Rt,[pc,#imm8*4]``: ``(site, register, pool, value)``.

    Kept as a thin wrapper over the project's own resynchronising Thumb decoder,
    so this probe cannot drift from the accepted disassembly methodology.  The
    sweep advances two bytes past an undecodable halfword rather than stopping,
    which is the property ``docs/research-conventions.md`` requires of a negative
    claim; the *positive* claim here is only that these sites exist.

    ``ldr`` from ``pc`` is a 16-bit instruction whose encoding is fixed and
    checked here (``01001 Rt imm8``, ``Rt != sp``), so a pool word is never read
    out of a data region that merely happened to decode.

    This is the **decodable-instruction** population, not every halfword that
    encodes the opcode: ``thumb_disasm.iter_thumb_wide`` runs Capstone on a
    Thumb-2-enabled decoder against an ARMv4T image, so it produces 4-byte decodes
    the real CPU would not and steps over 118 `ldr Rt,[pc,#imm8*4]` halfwords a
    raw scan finds.  All 118 were checked and none names an accepted container, so
    the population is unaffected - but a caller that needs "every encoding" must
    scan halfwords, not this.
    """
    targets: list[dict] = []
    for instruction in sweep_code(data, start=start, end=end):
        target = _literal_target_of(data, instruction)
        if target is not None:
            targets.append(target)
    return targets


def sweep_code(data: bytes, *, start: int = GBA_BASE, end: int = CODE_REGION_END) -> list:
    """Every decodable Thumb instruction in ``[start, end)``, in one pass.

    The single sweep both the literal-load join and the owner attribution read, so
    the two cannot disagree about where the code is and the image is decoded once.
    Resynchronising: an undecodable halfword advances two bytes and is skipped
    rather than ending the sweep.
    """
    return [
        item
        for item in thumb_disasm.iter_thumb_wide(data, start, end)
        if not isinstance(item, int)
    ]


def _literal_target_of(data: bytes, instruction) -> dict | None:
    """``{site, register, pool, value}`` when ``instruction`` is a pool load.

    ``ldr`` from ``pc`` is a 16-bit instruction whose encoding is fixed
    (``01001 Rt imm8``, ``Rt != sp``) and is re-checked here from the halfword, so
    a pool word is never read out of a data region that merely happened to decode
    and never from the ``ldr sp,[pc,#imm]`` form.
    """
    if instruction.mnemonic != "ldr":
        return None
    halfword = _u16(data, instruction.address)
    if (halfword & 0xF800) != 0x4800 or ((halfword >> 8) & 7) == 7:
        return None
    pool = ((instruction.address + 4) & ~3) + (halfword & 0xFF) * 4
    if pool + 4 > GBA_BASE + len(data):
        return None
    return {
        "site": instruction.address,
        "register": (halfword >> 8) & 7,
        "pool": pool,
        "value": _u32(data, pool),
    }


def is_valid_container(data: bytes, address: int) -> bool:
    """Whether ``address`` carries a container the engine's decoder would accept.

    Three tests, and the docstring says which is whose so the instrument is not
    mistaken for the engine:

    * **the engine's**: the wrapper's first word is one of the forms the container
      dispatcher ``0x0803D940`` selects on, ``0`` (stored), ``1`` or ``2``
      (packed).  Anything else falls through the dispatcher without a decode.
    * **host policy**: a non-zero declared size inside the codec's host bound.
    * **the format's**: for the packed forms, a decode that exactly reaches the
      declared size - which LOGX-CODEC-001 measured on every canonical packed
      container.  A stored container is accepted when its payload fits the image.

    Word alignment is required, because a container start in this engine is always
    word-aligned (LOGX-CODEC-001's aligned scan population, and every one of the
    11,715 accepted corpus containers).  Without the test, an odd address inside
    another container's payload can pass the header test and be reported as a
    second container.
    """
    if address & 3:
        return False
    offset = address - GBA_BASE
    if offset < 0 or offset + 8 > len(data):
        return False
    kind = _u32(data, address)
    declared = _u32(data, address + 4)
    if kind not in DISPATCHER_KINDS or declared == 0:
        return False
    if declared > reference.MAX_OUTPUT:
        return False
    if kind == 0:
        return offset + 8 + declared <= len(data)
    try:
        decoded = reference.decode_packed(
            data, offset + 8, declared_size=declared, stop_on="declared_size"
        )
    except reference.CodecError:
        return False
    return decoded.terminator == "declared_size"


def container_extent(data: bytes, address: int) -> int | None:
    """Bytes the container occupies from ``address``, header included."""
    if not is_valid_container(data, address):
        return None
    kind = _u32(data, address)
    declared = _u32(data, address + 4)
    if kind == 0:
        return 8 + declared
    decoded = reference.decode_packed(
        data, address - GBA_BASE + 8, declared_size=declared, stop_on="declared_size"
    )
    return 8 + decoded.source_consumed


def graphics_shape_candidates(decoded_size: int) -> list[dict]:
    """Whole-tile-block readings of a decoded size, one entry per bit depth.

    Pure arithmetic, no image and no palette: the container header carries no
    dimension field (measured for portraits too, PORTRAIT-COMPLETENESS-001), so a
    dimension is always a *reading* of the size, never a stored fact.  A size
    that is not a whole number of tiles at a depth yields no entry for that depth,
    which is what keeps this from inventing a shape for a non-graphics payload.

    **Every reading of every entry fits the payload at that entry's depth** -
    ``w * h * bpp // 8 == decoded_size``.  That invariant is the whole point of
    the function and is asserted by a test, because the screen- and cell-shaped
    readings are *named* (``240x160``, ``128x80``) and a named reading carried
    into the wrong depth would silently be 2x too large: ``240 * 160`` is 38,400
    bytes at 8bpp but only 19,200 at 4bpp.

    ``readings`` is ordered widest-first within a depth, and the payload's exact
    size is always the first reading, so a consumer that takes ``readings[0]``
    gets a framing that fits - not necessarily a screen-like one.  No claim is
    made that the first reading is the *right* one.
    """
    if decoded_size <= 0:
        return []
    named = {FULL_SCREEN_8BPP: (240, 160), MENU_CELL_8BPP: (128, 80)}
    candidates: list[dict] = []
    for bpp, tile_bytes in ((8, TILE_BYTES_8BPP), (4, TILE_BYTES_4BPP)):
        if decoded_size % tile_bytes:
            continue
        tiles = decoded_size // tile_bytes
        readings: list[tuple[int, int]] = []
        if bpp == 8 and decoded_size in named:
            readings.append(named[decoded_size])
        # Every factorisation into whole 8x8 tiles, widest first.
        for width_tiles in range(tiles, 0, -1):
            if tiles % width_tiles:
                continue
            height_tiles = tiles // width_tiles
            reading = (width_tiles * 8, height_tiles * 8)
            if reading not in readings:
                readings.append(reading)
        candidates.append(
            {
                "bits_per_pixel": bpp,
                "tile_bytes": tile_bytes,
                "tile_count": tiles,
                "readings": [f"{w}x{h}" for w, h in readings[:4]],
            }
        )
    return candidates


# --- owner attribution --------------------------------------------------------


def function_entries(data: bytes, *, start: int = GBA_BASE, end: int = CODE_REGION_END) -> list[int]:
    """Thumb ``push {..,lr}`` prologues as candidate function boundaries."""
    return sorted(
        instruction.address
        for instruction in sweep_code(data, start=start, end=end)
        if instruction.mnemonic == "push" and "lr" in instruction.operands
    )


def _owning_entry(entries: list[int], site: int) -> int | None:
    import bisect

    index = bisect.bisect_right(entries, site) - 1
    return entries[index] if index >= 0 else None


#: How far after a container's literal load a `bl 0x0803D940` still counts as
#: "this load is what gets dispatched".  The engine's own shape is `ldr r0,[pc,…]`
#: then one or two register moves then the `bl`; 32 bytes covers it with margin
#: and is a **host** window, not an engine rule.
DISPATCH_WINDOW = 32


def observed_dispatch(
    data: bytes,
    values: list[int],
    *,
    start: int = GBA_BASE,
    end: int = CODE_REGION_END,
) -> list[int]:
    """Which of ``values`` is *observed* handed to the dispatcher ``0x0803D940``.

    The literal load says the code names a container address; it does not say what
    the code then does with it.  This helper closes that gap where it can: it
    collects the literal load sites of each value and asks whether a
    ``bl 0x0803D940`` follows within :data:`DISPATCH_WINDOW` bytes.

    A **positive** here is strong evidence of the role.  A **negative is not
    evidence of absence** - the dispatch may be further away, may go through a
    helper, or may reach the address by a route this window does not cover - so
    the caller reports the observed set separately from the population rather than
    filtering the population by it.
    """
    targets = set(values)
    instructions = sweep_code(data, start=start, end=end)
    sites_by_value: dict[int, list[int]] = {}
    dispatch_sites: set[int] = set()
    for instruction in instructions:
        target = _literal_target_of(data, instruction)
        if target is not None and target["value"] in targets:
            sites_by_value.setdefault(target["value"], []).append(target["site"])
        if instruction.mnemonic in ("bl", "blx"):
            try:
                resolved = thumb_disasm.resolve_thumb_bl(
                    instruction.address, _u16(data, instruction.address),
                    _u16(data, instruction.address + 2),
                )
            except (IndexError, ValueError):
                continue
            if resolved & ~1 == CONTAINER_DISPATCHER:
                dispatch_sites.add(instruction.address)

    observed: list[int] = []
    for value, sites in sites_by_value.items():
        if any(
            0 <= dispatch - site <= DISPATCH_WINDOW
            for site in sites
            for dispatch in dispatch_sites
        ):
            observed.append(value)
    return sorted(observed)


def word_references(data: bytes, address: int, *, end: int | None = None) -> list[int]:
    """Every aligned 32-bit word in ``[GBA_BASE, end)`` equal to ``address``.

    ``end`` defaults to the whole image.  A caller that only cares about the code
    region passes it, which is what keeps the sweep bounded: the join is over the
    image the caller is actually interpreting, not over whatever bytes happen to
    follow it.
    """
    needle = address.to_bytes(4, "little")
    limit = len(data) if end is None else min(len(data), end - GBA_BASE)
    found: list[int] = []
    offset = 0
    while offset + 4 <= limit:
        index = data.find(needle, offset, limit)
        if index < 0:
            break
        if index % 4 == 0:
            found.append(GBA_BASE + index)
        offset = index + 1
    return found


# --- the report ---------------------------------------------------------------


def enumerate_ui_containers(
    data: bytes,
    *,
    known_addresses: set[int] | None = None,
    reference_scan_end: int | None = None,
    code_region_end: int = CODE_REGION_END,
) -> dict:
    """The code-referenced, corpus-disjoint container population.

    ``known_addresses`` is the accepted-corpus baseline.  When it is ``None`` the
    probe builds it with ``logx_gfxscan_probe.build_known_corpus`` - the accepted
    graph-derived corpus, never a scan - so disjointness is computed against the
    same 11,715-container baseline GRAPHICS-COVERAGE-001 and
    PORTRAIT-COMPLETENESS-001 used.

    ``reference_scan_end`` bounds the word-reference join; ``None`` scans the
    whole image, which is what the canonical report uses.  ``code_region_end``
    bounds the Thumb sweep.  A caller interpreting only part of an image passes
    the same bounds it interpreted, so a truncated fixture does not report the
    absent tail as "no reference" and does not pay for a full sweep.
    """
    if known_addresses is None:
        known_addresses = set(gfxscan.build_known_corpus(data).resources)

    instructions = sweep_code(data, end=code_region_end)
    literal_sites: dict[int, list[int]] = {}
    for instruction in instructions:
        target = _literal_target_of(data, instruction)
        if target is not None:
            literal_sites.setdefault(target["value"], []).append(target["site"])
    entries = sorted(
        instruction.address
        for instruction in instructions
        if instruction.mnemonic == "push" and "lr" in instruction.operands
    )

    containers: list[dict] = []
    skipped_non_containers = 0
    accepted_literal_values: list[int] = []
    for value in sorted(literal_sites):
        if not is_rom_pointer(data, value) or not is_valid_container(data, value):
            skipped_non_containers += 1
            continue
        # Recorded BEFORE the corpus filter, so the disjointness cross-check can
        # be computed on the pre-filter set.  Filtering first and then
        # intersecting with the filter's own input would make zero overlap a
        # tautology rather than a measurement.
        accepted_literal_values.append(value)
        if value in known_addresses:
            continue
        kind = _u32(data, value)
        declared = _u32(data, value + 4)
        extent = container_extent(data, value) or 0
        decoded_size = declared if kind == 0 else _decoded_size(data, value)
        sites = sorted(literal_sites[value])
        refs = word_references(data, value, end=reference_scan_end)
        code_refs = [ref for ref in refs if ref < code_region_end]
        data_refs = [ref for ref in refs if ref >= code_region_end]
        containers.append(
            {
                "address": f"0x{value:08X}",
                "kind": kind,
                "declared_size": declared,
                "decoded_size": decoded_size,
                "packed_extent": extent,
                "literal_load_sites": [f"0x{site:08X}" for site in sites],
                "literal_load_site_count": len(sites),
                "code_region_word_references": [f"0x{ref:08X}" for ref in code_refs],
                "data_region_word_references": [f"0x{ref:08X}" for ref in data_refs],
                "owning_function_entries": sorted(
                    {
                        f"0x{entry:08X}"
                        for entry in (_owning_entry(entries, site) for site in sites)
                        if entry is not None
                    }
                ),
                "shape_candidates": graphics_shape_candidates(decoded_size),
                "in_known_corpus": False,
            }
        )

    counts: dict[int, int] = {}
    for item in containers:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1

    # The pre-filter population, so the disjointness cross-check is a measurement
    # and not a restatement of the filter (see `accepted_literal_values`).
    in_corpus = [value for value in accepted_literal_values if value in known_addresses]
    dispatched = observed_dispatch(
        data, accepted_literal_values, start=GBA_BASE, end=code_region_end
    )

    return {
        "rom_sha256": CANONICAL_SHA256,
        "known_corpus_size": len(known_addresses),
        "code_region": f"0x{GBA_BASE:08X}..0x{code_region_end:08X}",
        "container_dispatcher": f"0x{CONTAINER_DISPATCHER:08X}",
        "literal_load_site_count": sum(len(sites) for sites in literal_sites.values()),
        "distinct_literal_values": len(literal_sites),
        "literal_values_that_are_not_containers": skipped_non_containers,
        "literal_values_that_are_containers": len(accepted_literal_values),
        "literal_container_values_in_known_corpus": [f"0x{value:08X}" for value in in_corpus],
        "literal_container_values_in_known_corpus_count": len(in_corpus),
        "containers_observed_dispatched": [
            f"0x{value:08X}" for value in dispatched
        ],
        "containers_observed_dispatched_count": len(dispatched),
        "container_count": len(containers),
        "container_kinds": counts,
        "containers": containers,
        "scan_gap": _SCAN_GAP,
    }


def _decoded_size(data: bytes, address: int) -> int:
    """The decoded length of a packed container, or 0 when it does not decode."""
    if not is_valid_container(data, address):
        return 0
    kind = _u32(data, address)
    declared = _u32(data, address + 4)
    if kind == 0:
        return declared
    return len(
        reference.decode_packed(
            data, address - GBA_BASE + 8, declared_size=declared, stop_on="declared_size"
        ).data
    )


def shared_resources(report: dict) -> dict:
    """Containers named by more than one code site, or from code and data.

    Sharing is the normal case in this engine (GRAPHICS_FORMAT.md section 4 for
    sprites), and a UI graphic used by several screens is what a shared entry
    looks like.  Reported rather than folded into the counts.
    """
    multi: list[dict] = []
    both: list[dict] = []
    for item in report["containers"]:
        if item["literal_load_site_count"] > 1:
            multi.append(
                {
                    "address": item["address"],
                    "literal_load_site_count": item["literal_load_site_count"],
                }
            )
        if item["code_region_word_references"] and item["data_region_word_references"]:
            both.append(
                {
                    "address": item["address"],
                    "code_sites": len(item["code_region_word_references"]),
                    "data_sites": len(item["data_region_word_references"]),
                }
            )
    return {
        "shared_by_multiple_code_sites": multi,
        "shared_by_multiple_code_sites_count": len(multi),
        "referenced_from_code_and_data": both,
        "referenced_from_code_and_data_count": len(both),
    }


def damage_number_lead_report(data: bytes) -> dict:
    """What GRAPHICS-COVERAGE-001's UI/HUD leads actually are, measured.

    Reports the word at ``0x08071700`` and the two "asset" records the coverage
    matrix named.  Nothing here claims graphics: the point of the report is that
    these are text/format descriptors and literal-pool residents, so the family
    they belong to is not a container population.
    """
    base = _u32(data, 0x08071700)
    records = {}
    for address in (0x0806E050, 0x0806F150, 0x0806EE6C):
        pointer = _u32(data, address)
        count = _u32(data, address + 4)
        target_kind = _u32(data, pointer) if is_rom_pointer(data, pointer) else None
        target_declared = _u32(data, pointer + 4) if is_rom_pointer(data, pointer) else None
        records[f"0x{address:08X}"] = {
            "field_00_rom_pointer": f"0x{pointer:08X}",
            "field_04_small_count": count,
            "target_is_a_container": bool(
                is_rom_pointer(data, pointer) and is_valid_container(data, pointer)
            ),
            "target_kind": target_kind,
            "target_declared_size": target_declared,
        }
    return {
        "context_pool_word_0x08071700": f"0x{base:08X}",
        "context_pool_word_is_ewram": 0x02000000 <= base < 0x04000000,
        "descriptor_records": records,
        "reading": (
            "0x08071700 is a word in a table of subsystem blocks; 0x0800AB54 "
            "reads [base+4] and [base+8], which are the residents 0x0806F150 and "
            "0x0806E050. Each of those is a {u32 pointer, u32 small count} "
            "text/format record whose pointer names an all-zero-at-rest region, "
            "not a container."
        ),
    }


def overlap_with_known_corpus(data: bytes, corpus=None) -> dict:
    """Exact intersection of the **pre-filter** literal-container set with the corpus.

    The intersection is taken on the values *before* the corpus filter removes
    them.  Computing it after the filter would make ``overlap_count == 0`` a
    tautology - the filter's own input cannot survive it - which is exactly the
    kind of check that cannot fail and therefore proves nothing.

    ``corpus`` may be a prebuilt ``KnownCorpus``; building it costs a full sprite
    and map graph walk, so a caller that already has one passes it rather than
    paying twice.
    """
    if corpus is None:
        corpus = gfxscan.build_known_corpus(data)
    known = set(corpus.resources)
    report = enumerate_ui_containers(data, known_addresses=known)
    # Pre-filter set: the disjoint survivors reported by the enumeration, plus
    # the values the filter removed (which are exactly the ones that could make
    # the overlap non-zero).
    accepted = {int(item["address"], 16) for item in report["containers"]}
    accepted |= {
        int(value, 16)
        for value in report["literal_container_values_in_known_corpus"]
    }
    overlap = sorted(accepted & known)
    return {
        "known_corpus_size": len(known),
        "literal_container_values": len(accepted),
        "enumerated_count": report["container_count"],
        "overlap_count": len(overlap),
        "overlap": [f"0x{value:08X}" for value in overlap],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", help="canonical Buu's Fury ROM (read-only)")
    parser.add_argument("--json", help="write the report to this path")
    parser.add_argument(
        "--leads",
        action="store_true",
        help="emit the GRAPHICS-COVERAGE-001 lead measurement only",
    )
    parser.add_argument(
        "--overlap",
        action="store_true",
        help="emit the known-corpus overlap check only",
    )
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    if args.leads:
        report = damage_number_lead_report(data)
    elif args.overlap:
        report = overlap_with_known_corpus(data)
    else:
        population = enumerate_ui_containers(data)
        report = population | {
            "shared": shared_resources(population),
            "leads": damage_number_lead_report(data),
            "known_corpus_overlap": overlap_with_known_corpus(data),
        }
    text = json.dumps(report, indent=2)
    print(text)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
