"""The measured hard-coded address surface of ``tools/``.

This module holds the pins and the exemption table for the census guard in
``tests/unit/test_hardcoded_address_census.py``. It measures nothing by itself:
every function here reads the tracked tree and returns a count, and the guard
compares that count against a pin.

The census set is every path from ``tools.quality.architecture.tracked_files()``
starting with ``tools/``. The enforcement set is that set minus the four
instrument directories named in ``INSTRUMENT_DIRECTORIES``. Three units are
counted, always per line and never per match, so a line carrying eleven
addresses counts once:

* ``HEX5`` - a hexadecimal literal of five or more digits. Its parent pair is
  the one ``INVENTORY.md`` section 4 reports, 2884 lines in 272 files.
* ``ROM_HEX`` - a complete ROM-space word. A bare ``0x08...`` prefix inside a
  longer constant is not a hit, and the octal-hazard ``0x0[89]`` form is
  included on purpose.
* ``DECIMAL`` - an integer token whose value lands in
  ``[0x08000000, 0x0A000000)``. The decimal spelling is invisible to every
  hexadecimal pattern, which is the falsifier the migration order names; the
  value is range-checked as an integer, never by a pattern.

What this module does NOT cover, stated so a reader does not expect more:

* it does not decide whether a hit is a real address. A file is counted by what
  it spells, and a counted file is a row with a reason, which is why the one
  row whose hit is a Windows creation flag rather than an address says so.
* it counts literals per file, so it detects a change in how many literals a
  file carries and not a swap of one address for another at constant count.
* it governs the index, not the disk. A path that exists only on disk is not in
  the set, so the guard never fires on a bytecode cache, an editor backup or
  generated output, and it never sees a file that was not added to the index.
* it says nothing about the four instrument directories, deliberately.

ponytail: a row pins three counts, not the literal values. A swap of one address
for another at the same count is invisible. The one-line upgrade, when a swap
starts to matter, is a digest over the sorted distinct literals of the row; the
stated aim is that this surface does not grow, so the digest is not built.
"""

from __future__ import annotations

import re
from typing import Mapping, NamedTuple, Sequence

from tools.quality.architecture import REPOSITORY_ROOT, tracked_files

#: A hexadecimal literal of five or more digits.
HEX5 = re.compile(r"0x[0-9A-Fa-f]{5,}")

#: A complete ROM-space hexadecimal word. Both boundaries are load-bearing: the
#: lookarounds keep a longer constant from matching at its prefix.
ROM_HEX = re.compile(r"(?<![0-9A-Fa-f])0x0[89][0-9A-Fa-f]{6}(?![0-9A-Fa-f])")

#: A decimal integer token of eight digits or more, underscores allowed.
DECIMAL = re.compile(r"(?<![\w.])\d[\d_]{7,}\d(?![\w.])")

#: ROM space, as the Game Pak window the readers subtract a base from.
ROM_START = 0x08000000
ROM_END = 0x0A000000

#: ``INVENTORY.md`` section 4's parent pair: conventional hex lines and files in
#: the whole tracked ``tools/`` tree. The per-file rows that document reports are
#: lane-reported and are not reproducible under any single unit, so only this
#: pair is pinned.
CENSUS_INVENTORY_S4 = (2884, 272)

#: The enforcement set at the baseline: conventional hex, ROM-space hex, and the
#: decimal ROM-range corpus, each as (lines, files).
ENFORCEMENT_HEX5 = (661, 70)
ENFORCEMENT_ROM_HEX = (486, 53)
ENFORCEMENT_DECIMAL = (404, 1)

#: Directories the migration order leaves out of scope deliberately: they hold
#: evidence instruments whose addresses are inputs to a mapping effort rather
#: than consumers of the pinned map, and migrating them would put the probe
#: corpus at risk for no product gain. This is a scan-set definition and not an
#: exemption row, and a directory not named here is inside the enforcement set
#: by construction, so a new directory under ``tools/`` is covered as soon as it
#: is tracked.
INSTRUMENT_DIRECTORIES: tuple[tuple[str, str], ...] = (
    (
        "tools/runtime/",
        "runtime capture instruments; the migration order leaves them out of "
        "scope because their addresses are evidence inputs, not consumers",
    ),
    (
        "tools/research/",
        "read-only archaeology instruments; the migration order leaves them out "
        "of scope for the same reason",
    ),
    (
        "tools/ghidra/",
        "Ghidra analysis scripts; their addresses are analysis inputs for the "
        "same mapping effort and are not read by a shipping module",
    ),
    (
        "tools/mgba_probe/",
        "the emulator probe harness and its patch; its addresses belong to its "
        "own probes and are not read by a shipping module",
    ),
)


class CensusError(RuntimeError):
    """A measurement that cannot be trusted, raised instead of counting zero."""


class Row(NamedTuple):
    """One enforced file: its per-line counts and the reason it is exempt."""

    path: str
    hex5: int
    rom_hex: int
    decimal: int
    reason: str


#: One row per enforced file that carries a ROM-space or decimal literal, keyed
#: by path and generated by re-running the scan, never typed from memory. A row
#: asserts equality in both directions, and a row whose file stops carrying a
#: literal, whose count moves either way, or that names a path which is not
#: tracked fails the guard by name.
EXEMPTIONS: tuple[Row, ...] = (
    Row(
        "tools/buufury_text/preview.py", 19, 11, 0,
        "the preview's portrait-index selectors, the layout and art containers "
        "they select, and a module base constant: 0x08012012, 0x08012104, "
        "0x0801210A, 0x08071720..0x08071A6C, 0x08000000, cited in the docstring "
        "as measured portrait-record layout. No ticket covers this file yet: "
        "recorded debt.",
    ),
    Row(
        "tools/dragonbyte/textsurface.py", 9, 1, 0,
        "one docstring range naming the packed-dialogue container span "
        "0x0877C5A4..0x0879B704, quoted while counting those containers. No "
        "ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/export/buu_resource_export.py", 6, 6, 0,
        "comments and docstrings citing engine sites: the decompressing "
        "constructor 0x08007B63, the marker installer 0x0800897B, the occupancy "
        "test 0x08008076, the default container 0x08070808 and the 24-byte-record "
        "table 0x086B82EC. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/export/canonical.py", 11, 11, 0,
        "named export constants and their citations: the bank table 0x08179764, "
        "the default chunk container 0x08070808, the sprite-definition run "
        "0x086B6BDC, the party-alias accessor and re-entry words 0x08000158 and "
        "0x0801713C, the party-alias index table 0x086B82EC and the portrait and "
        "palette words. PINMAP-06 moves the two shadowed table addresses "
        "0x086B6BDC and 0x0874D380 into the profile and leaves the rest as rows.",
    ),
    Row(
        "tools/export/render.py", 2, 1, 0,
        "one docstring citation of the payload-streaming constructor "
        "0x080088BD, quoted to explain what its bytes mean. No ticket covers "
        "this file yet: recorded debt.",
    ),
    Row(
        "tools/export/webfoot_strict.py", 5, 3, 0,
        "the engine dispatcher 0x0803D940 cited in comments and in the dispatch "
        "comment, plus the two form words 0x087B7CCC and 0x087B7CD0 read from "
        "its literal pool. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/quality/readability.py", 1, 1, 0,
        "the single hit is the ROM base used as an example inside the comment "
        "that documents this scanner's own combined-hex rule. It is prose about "
        "a spelling, not a target address; no ticket covers it yet: recorded "
        "debt.",
    ),
    Row(
        "tools/save_catalogue/geometry.py", 13, 4, 0,
        "comments citing the record access sites 0x0800493C..0x08004942 and the "
        "header read and write routines 0x08006B88, 0x08006B7E, 0x08006B5E, "
        "0x08006AF0 and 0x08006B0C. No ticket covers this file yet: recorded "
        "debt.",
    ),
    Row(
        "tools/webfoot/allocation.py", 6, 6, 0,
        "comments citing the engine key lookup 0x080089FC, the count reader "
        "0x080125E0 and the Game Pak window bounds 0x08000000, 0x08800000 and "
        "0x09FFFFFF. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/appearance_authoring.py", 14, 14, 0,
        "comments citing the two-loop appearance search 0x08027948..0x080279CE, "
        "the sibling factory words 0x086AED8C and 0x086AEBF0, and the accessor "
        "and write sites 0x0802794E, 0x08010312 and 0x0800FB72. No ticket covers "
        "this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/atlas_producers/code_functions.py", 17, 14, 0,
        "the ARM entry point 0x080000C0 and the table of function addresses the "
        "atlas producer emits, 0x080728AC and 0x087B6904 with their per-family "
        "runs 0x080123E8..0x08012464 and 0x0803E4E4..0x0803EC5A. No ticket "
        "covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/atlas_producers/seed.py", 223, 186, 0,
        "168 distinct ROM words: the seed's function anchors, dispatch tables "
        "and per-row evidence strings, which restate the profile's own tables. "
        "PINMAP-09 reads the rows that duplicate a profile key from the profile "
        "and either resolves or records the one conflict the seed reports at "
        "seed.py:491-508.",
    ),
    Row(
        "tools/webfoot/authored_placements.py", 2, 2, 0,
        "two comments citing the map entry byte read at 0x08008CA2 and "
        "0x08008CD2 and the loader 0x08008C9E. No ticket covers this file yet: "
        "recorded debt.",
    ),
    Row(
        "tools/webfoot/binary.py", 2, 1, 0,
        "GBA_ROM_BASE, the image base every reader here subtracts to reach a "
        "file offset. It names the address space, not a location in it; no "
        "ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/compressed_dialogue.py", 5, 3, 0,
        "two comments and one note citing the record loop 0x08012552 that "
        "branches on the record word and the compressed-dialogue consumer "
        "0x08012230. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/data/placement_contracts.py", 40, 40, 404,
        "the placement and event corpus itself: 404 decimal ROM addresses in 347 "
        "distinct values, plus 40 hex lines naming the VM roots, handlers and "
        "record tables those entries hang from. PINMAP-10 gives the corpus a "
        "map-shaped home and is the largest row; it waits on an owner decision "
        "about that shape.",
    ),
    Row(
        "tools/webfoot/data/roms.yaml", 42, 36, 0,
        "the profile's own declared table addresses: character table, object and "
        "background palettes, factory raw, constructor, and the per-title rows "
        "the shipping tools resolve against, in both hex spellings. This file is "
        "the destination the PINMAP-04 to PINMAP-09 removals read from rather "
        "than a removal target; no ticket removes the profile's own rows. "
        "Recorded debt.",
    ),
    Row(
        "tools/webfoot/data/script_effects.py", 3, 3, 0,
        "the native handler word 0x08003031 in the effect table plus docstring "
        "citations of the handler 0x08003030 and the routine 0x0806BCE8. No "
        "ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/data/script_specs.py", 8, 8, 0,
        "the per-script handler run 0x08003C75..0x08003FEF held in the script "
        "spec table as the words the VM dispatches on. No ticket covers this "
        "file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/dialogue_edit.py", 3, 1, 0,
        "one ROM base constant, used to convert a record address to a file "
        "offset. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/dialogue_repack.py", 2, 1, 0,
        "one ROM base constant, used to convert a record address to a file "
        "offset. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/enemy_randomizer/compatibility.py", 3, 3, 0,
        "comments citing the shared placement table 0x080555A0 and the one "
        "factory and constructor pair 0x0800FD55 and 0x0800F68C that serve the "
        "whole corpus. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/enemy_randomizer/config.py", 1, 1, 0,
        "one comment citing the level-cap comparison site 0x08013A00 where the "
        "cap of 200 was read. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/enemy_randomizer/eligibility.py", 1, 1, 0,
        "one comment citing the verified script handler 0x0800421F that a "
        "candidate record dispatches through. No ticket covers this file yet: "
        "recorded debt.",
    ),
    Row(
        "tools/webfoot/enemy_randomizer/enemy_type.py", 1, 1, 0,
        "one comment citing the actor character pointer table 0x086B6BDC that "
        "the randomizer indexes. PINMAP-06 removes the same address from the "
        "export path only; this file is not named by any ticket yet, so it is "
        "recorded debt.",
    ),
    Row(
        "tools/webfoot/formats/map_entry.py", 1, 1, 0,
        "one comment citing the loader 0x08008C9E whose byte read bounds the "
        "entry count. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/formats/map_graphics.py", 20, 17, 0,
        "the layer-handler words DOMINANT_LAYER_HANDLER 0x08008087, "
        "ABSENT_LAYER_HANDLER 0x08007A41 and ABSENT_LAYER_RECORD 0x080707FC, "
        "plus citations of the container constructors 0x08007B63, 0x0800897B and "
        "the descriptor reads 0x080088E6, 0x08008924. PINMAP-07 moves every "
        "handler word into a named code anchor.",
    ),
    Row(
        "tools/webfoot/formats/map_placements.py", 12, 9, 0,
        "FACTORY_RAW 0x0800FD55, RECORD_TAIL, the three script handler words "
        "0x0800421D, 0x0800421F and 0x0800424F, and citations of the layout and "
        "loader sites 0x080555A0, 0x080716EC, 0x08017DA3, 0x080111A9 and "
        "0x08008C9E. PINMAP-07 reads FACTORY_RAW from "
        "placement_types.factory_raw and names the handler words as anchors.",
    ),
    Row(
        "tools/webfoot/formats/map_slots.py", 3, 1, 0,
        "one comment citing the slot source 0x080755C0 and the halfwords at its "
        "header. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/formats/map_transitions.py", 20, 14, 0,
        "TRANSITION_CLASS_A_RAW and TRANSITION_CLASS_B_RAW, 0x08007675 and "
        "0x080072CD, plus comments citing the class methods 0x080075AC and "
        "0x080071F8, the record layouts 0x08008d44, 0x0800CEF4 and the pool "
        "words 0x080159B0, 0x0800A890 and 0x080707D8. No ticket names this file "
        "yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/formats/placement_links.py", 3, 3, 0,
        "comments citing the byte-branch sites 0x080040BA..0x080040C2, the "
        "dialog block 0x080040EA and the handler 0x08003030 that routes into "
        "0x0802BFBC. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/formats/sprite_graphics.py", 6, 6, 0,
        "comments citing the frame arithmetic sites 0x0800F3C0..0x0800F3CE and "
        "the attribute reads 0x0800F204, 0x0800F22A, 0x0800F206, 0x0800F22E, "
        "0x0800F1C2 and 0x0800F24C. No ticket covers this file yet: recorded "
        "debt.",
    ),
    Row(
        "tools/webfoot/formats/stat_tables.py", 4, 1, 0,
        "one comment quoting the toolkit's ROM offset convention with the base "
        "0x08000000. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/formats/webfoot_lz.py", 6, 2, 0,
        "one docstring citation of the retail packed decoder 0x087B79E4 and the "
        "Thumb-to-ARM veneer 0x08049120 it is reached through. No ticket covers "
        "this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/graphics.py", 6, 5, 0,
        "comments citing the sprite-id accessor 0x08000158 and its literal site "
        "0x0800015E, the party re-entry path 0x0801713C and its site 0x0801713E, "
        "and the character pointer table 0x086B6BDC. No ticket covers this file "
        "yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/graphics_authoring.py", 1, 1, 0,
        "one comment citing the declared expansion window 0x08800000 that the "
        "profile maps a file offset into. No ticket covers this file yet: "
        "recorded debt.",
    ),
    Row(
        "tools/webfoot/handles.py", 3, 2, 0,
        "comments citing the handle pack and unpack sites 0x08012240, 0x08012244 "
        "and 0x08012246. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/layout.py", 10, 8, 0,
        "comments citing the character pointer table 0x086B6BDC, the accessor "
        "and re-entry words 0x08000158, 0x0800015E, 0x0801713C and 0x0801713E, "
        "the map entry table 0x0808E2E0, the key lookup 0x08008A0A and "
        "0x080089FC and the count reader 0x080125E0. No ticket covers this file "
        "yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/map_authoring.py", 11, 10, 0,
        "comments and one subtraction citing the key lookup 0x080089FC, the "
        "count reader 0x080125E0, the literal pool site 0x08008A0A and the ROM "
        "base 0x08000000. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/map_chunk.py", 1, 1, 0,
        "one line subtracting the ROM base 0x08000000 from a resolved template "
        "address to get a file offset. No ticket covers this file yet: recorded "
        "debt.",
    ),
    Row(
        "tools/webfoot/map_render.py", 4, 4, 0,
        "SUPPORTED_LAYER_HANDLER 0x08008087, the background palette address "
        "0x080701B0 repeated in two provenance strings, and a comment citing the "
        "engine loop 0x08009C02..0x08009C12. PINMAP-07 names this file and moves "
        "the handler word into a code anchor.",
    ),
    Row(
        "tools/webfoot/map_resize.py", 3, 3, 0,
        "comments citing the camera clamp 0x080094F0 and the camera update "
        "0x08009744, plus one ROM base subtraction 0x08000000. No ticket covers "
        "this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/map_transitions.py", 5, 4, 0,
        "comments citing the pair loader 0x08009676, the registry walk "
        "0x08012664 and the key-scan sites 0x08008A0E, 0x08008A14 and "
        "0x080089FC. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/maps.py", 7, 3, 0,
        "comments citing map entry 39's slot word 0x080755C0, the factory word "
        "0x0800FD55 in a slot and the engine loop bounds 0x08008CA2 and "
        "0x08008CD2. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/placement_events.py", 2, 2, 0,
        "the two script dispatch handler words 0x0800424F and 0x0800421F, cited "
        "in comments over the counts the codec already verifies. PINMAP-07 names "
        "this file and moves the handler words into code anchors.",
    ),
    Row(
        "tools/webfoot/project/model.py", 6, 3, 0,
        "comments citing the unresolved byte 0x08007282, the count reader "
        "0x080125E0 and the key lookup 0x080089FC. No ticket covers this file "
        "yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/release_identity.py", 1, 1, 0,
        "the one hit is a Windows process creation-flag fallback spelled "
        "0x08000000, not a ROM address. It is a pattern coincidence kept visible "
        "as a row; no ticket covers it and none is needed. Recorded debt.",
    ),
    Row(
        "tools/webfoot/relocation_proof.py", 1, 1, 0,
        "the one hit writes the Game Pak entry point 0x08000100 into the image "
        "header at 0xC0 while proving a relocation. No ticket covers this file "
        "yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/sprite_attachment.py", 9, 7, 0,
        "the object factory words 0x08017DA3 and 0x080111A9, the entry class "
        "0x0800A7A1, the placement family 0x0800FD55 and the record run the "
        "comment measures from 0x0807831C. PINMAP-07 names this file and moves "
        "the handler and factory words into code anchors.",
    ),
    Row(
        "tools/webfoot/sprite_swap.py", 10, 10, 0,
        "REGISTRY_TABLE_ADDRESS 0x086B6BDC, OBJECT_PALETTE_ADDRESS 0x0805652C "
        "and PORTRAIT_ARRAY_ADDRESS 0x086F393C, with the accessor 0x08011F20 "
        "cited in a comment and the ROM base 0x08000000 used to convert offsets. "
        "PINMAP-04 resolves the two shadowed addresses from the profile and "
        "gives the portrait array a declared key.",
    ),
    Row(
        "tools/webfoot/stats.py", 1, 1, 0,
        "one comment citing the level-cap comparison site 0x08013A00 where the "
        "cap was read. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/textedit/engine.py", 17, 5, 0,
        "the text tool's private per-title row at engine.py:178-199: the layout "
        "container 0x087B5B64, the packed-dialogue address range "
        "0x0877C5A4..0x0879B704, the placement family 0x0800FD55 and the "
        "resource handler 0x0800424F. PINMAP-05 resolves every value in that row "
        "from the profile with no code edit.",
    ),
    Row(
        "tools/webfoot/workbench/map_browser_tab.py", 2, 2, 0,
        "two comments, one naming the address space base 0x08000000 while "
        "explaining why -1 cannot be a pointer, one quoting the key lookup "
        "0x080089FC as the engine's map identity. No ticket covers this file "
        "yet: recorded debt.",
    ),
)


def census_paths() -> list[str]:
    """Every tracked path under ``tools/``.

    The index is the only source. Nothing here walks the disk, so a path that
    exists on disk but was never added is invisible by construction.
    """
    return [path for path in tracked_files() if path.startswith("tools/")]


def enforcement_paths() -> list[str]:
    """The census set minus the instrument directories."""
    excluded = tuple(directory for directory, _ in INSTRUMENT_DIRECTORIES)
    return [path for path in census_paths() if not path.startswith(excluded)]


def decimal_in_rom_space(line: str) -> bool:
    """Whether ``line`` carries a decimal integer token inside ROM space."""
    for match in DECIMAL.finditer(line):
        try:
            value = int(match.group().replace("_", ""))
        except ValueError:
            continue
        if ROM_START <= value < ROM_END:
            return True
    return False


def scan(paths: Sequence[str]) -> dict[str, tuple[int, int, int]]:
    """Per-line counts for every path that carries a literal.

    Returns only the paths with at least one hit. An empty path list, or a path
    that cannot be read, is a ``CensusError``: a measurement nobody can trust is
    never reported as a count of zero.
    """
    if not paths:
        raise CensusError("the scan was handed no path to read")
    counted: dict[str, tuple[int, int, int]] = {}
    for path in paths:
        try:
            text = (REPOSITORY_ROOT / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise CensusError(f"{path}: cannot be read ({error})") from error
        lines = text.splitlines()
        hex5 = sum(1 for line in lines if HEX5.search(line))
        rom_hex = sum(1 for line in lines if ROM_HEX.search(line))
        decimal = sum(1 for line in lines if decimal_in_rom_space(line))
        if hex5 or rom_hex or decimal:
            counted[path] = (hex5, rom_hex, decimal)
    return counted


def totals(
    per_file: Mapping[str, tuple[int, int, int]],
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """``((hex5 lines, files), (rom hex lines, files), (decimal lines, files))``."""
    columns: list[tuple[int, int]] = []
    for index in range(3):
        values = [counts[index] for counts in per_file.values()]
        columns.append((sum(values), sum(1 for value in values if value)))
    return columns[0], columns[1], columns[2]


def carrying_paths(per_file: Mapping[str, tuple[int, int, int]]) -> list[str]:
    """The sorted paths that carry a ROM-space hex or decimal literal."""
    return sorted(
        path for path, counts in per_file.items() if counts[1] or counts[2]
    )
