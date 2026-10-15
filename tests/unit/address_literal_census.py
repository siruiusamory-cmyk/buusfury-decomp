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

* ``HEX5`` - a hexadecimal literal token of five or more digits. The metric was
  widened once, after a review found two spellings that evaded it, an uppercase
  prefix and a digit separator; it measures 2882 lines in 272 files.
* ``ROM_HEX`` - a hexadecimal token whose parsed integer lands in
  ``[0x08000000, 0x0A000000)``. Deciding by value rather than by the ``0[89]``
  digit shape is what makes a seven-digit spelling such as ``0x82ed222`` count.
* ``DECIMAL`` - an integer token whose value lands in
  ``[0x08000000, 0x0A000000)``. The decimal spelling is invisible to every
  hexadecimal pattern, which is the falsifier the migration order names; the
  value is range-checked as an integer, never by a pattern.

``INVENTORY.md`` section 4 publishes the parent pair 2884 lines in 272 files for
its ``0x[0-9A-Fa-f]{5,}`` count. That pattern and the token measured here differ
by exactly one line, ``tools/runtime/rom008_query_probe.py:105``, which spells
its literal with a digit separator. Both pairs are pinned and the difference was
asserted to be exactly one line and no files, so the reconciliation with section
4 was machine-checked rather than discarded. PINMAP-04 then moved the tree itself
and the published pair was not re-measured with it, so that pinned difference is
the one thing this module cannot restate from inside its own write surface; see
the ``CENSUS_HEX5`` note below for the arithmetic, which is stated so a reader can
reproduce it line by line.

Named limits: ``0o`` and ``0b`` spellings are not detected at all, and no such
spelling exists in the tracked tree today. The two hex boundary rules differ on
purpose: the historical lowercase form keeps the historical boundary so a Java
suffix such as ``0x080126D4L`` still counts and no tracked line lost a count
(measured), while the widened form must also exclude identifier characters, or the
name ``byte_at_0x10_census`` reads as the literal ``0x10ce``.

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
from typing import Iterable, Mapping, NamedTuple, Sequence

from tools.quality.architecture import REPOSITORY_ROOT, tracked_files

#: A hex literal token, two spellings of boundary on purpose. The first
#: alternative is the historical spelling and keeps the historical boundary, so
#: a Java suffix such as 0x080126D4L still counts, and no tracked line lost a count
#: (measured). The second adds the upper-case prefix and the digit separator;
#: its boundary must also exclude identifier characters, or the name
#: byte_at_0x10_census reads as the literal 0x10ce.
HEX_TOKEN = re.compile(
    r"(?<![0-9A-Fa-f])0x[0-9A-Fa-f]{5,}(?![0-9A-Fa-f])"
    r"|(?<![0-9A-Za-z_.])0[xX][0-9A-Fa-f_]*[0-9A-Fa-f](?![0-9A-Za-z_])"
)

#: A decimal integer token of eight digits or more, underscores allowed.
DECIMAL = re.compile(r"(?<![\w.])\d[\d_]{7,}\d(?![\w.])")

#: ROM space, as the Game Pak window the readers subtract a base from.
ROM_START = 0x08000000
ROM_END = 0x0A000000

#: ``INVENTORY.md`` section 4's published parent pair, quoted as published: its
#: ``0x[0-9A-Fa-f]{5,}`` count, per line, over the 560 tracked ``tools/`` files.
#: The per-file rows that document reports are lane-reported and are not
#: reproducible under any single unit, so only this pair is quoted.
#: PINMAP-04 moved the measured pair and left this one at the published value on
#: purpose: it is a quotation of an external document, not a restatement of the
#: tree, and rewriting it to keep a pinned difference true would make it lie about
#: what section 4 says. The consequence is stated where a reader meets it, in the
#: ``CENSUS_HEX5`` note here and in the reconciliation node's own failure message.
CENSUS_INVENTORY_S4 = (2884, 272)

#: The whole-tree measurement under this module's widened token. PINMAP-04 moved
#: it by -3 lines and 0 files, and the arithmetic is one line, not three: FOUR
#: counted lines left ``tools/webfoot/sprite_swap.py`` and ONE counted line
#: arrived in the profile catalogue pair.
#:
#: Left, each a counted hex5 and rom_hex line: the constant
#: ``REGISTRY_TABLE_ADDRESS = 0x086B6BDC`` at sprite_swap.py:61, the constant
#: ``OBJECT_PALETTE_ADDRESS = 0x0805652C`` at :63, the comment
#: ``#: The portrait pointer array (accessor 0x08011F20).`` at :67, and the
#: constant ``PORTRAIT_ARRAY_ADDRESS = 0x086F393C`` at :68.
#: Arrived: ``portrait_table_address: 0x086f393c`` at
#: ``tools/webfoot/data/roms.yaml:21``, and the byte-identical copy of the same
#: line at ``config/roms.yaml:21``, which is outside the ``tools/`` census set.
#: Measured 2885 -> 2882 lines, 272 -> 272 files.
#: PINMAP-05 moved 2882 -> 2879; the entry it appended names all nineteen lines.
#: PINMAP-06 moved 2879 -> 2877; the entry it appended names both lines.
#: PINMAP-07a moved 2877 -> 2887; the entry it appended names all ten lines.
#: PINMAP-07b moved 2887 -> 2875; the entry it appended names all twelve lines.
#: PINMAP-09 moved 2875 -> 2866; the entry it appended names all eleven lines.
CENSUS_HEX5 = (2866, 272)

#: The enforcement set: conventional hex, ROM-space hex, and the decimal
#: ROM-range corpus, each as (lines, files). All three moved at PINMAP-04, by the
#: same four removals and the one added key the ``CENSUS_HEX5`` note lists; the
#: enforcement set is the whole-tree set minus the four instrument directories, so
#: the three move together. PINMAP-07a then moved the first two, ten lines each.
#: PINMAP-07b moved them back down by the twelve hex lines it removed.
ENFORCEMENT_HEX5 = (642, 70)
ENFORCEMENT_ROM_HEX = (474, 53)
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
        "tools/export/canonical.py", 9, 9, 0,
        "the literals PINMAP-06 leaves, each named with its role at its line in "
        "this file after those removals: the bank container table 0x08179764 at "
        ":150, the absent-layer placeholder container 0x08070808 at :154, the "
        "engine code sites 0x08000158 and 0x0801713C at :170-171, the party-alias "
        "index table 0x086B82EC at :172, the portrait pointer array 0x086F393C at "
        ":232, which PINMAP-04 declared as actor_sprites.portrait_table_address, "
        "and the terrain-field handler word 0x080088BD cited at :308, :321 and "
        ":330, which is PINMAP-07's surface. The two this row used to spell, the "
        "sprite-definition run 0x086B6BDC and the appearance table 0x0874D380, now "
        "resolve from the profile through the module's existing accessor pattern.",
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
        "tools/webfoot/atlas_producers/seed.py", 214, 177, 0,
        "168 distinct ROM words: the seed's function anchors, dispatch tables "
        "and per-row evidence strings. PINMAP-09 reads the TEN rows that "
        "duplicated a profile key from the profile instead of restating it; "
        "nine counted lines left this file and two arrived in the rewritten "
        "conflict note and its guard, so the pair is -9 lines and no files. "
        "The seed's one reported conflict is recorded as one named row.",
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
        "tools/webfoot/data/roms.yaml", 61, 55, 0,
        "the profile's own declared table addresses: character table, object and "
        "background palettes, the portrait pointer array, factory raw, constructor, "
        "and the per-title rows the shipping tools resolve against, in both hex "
        "spellings. This file is the destination the PINMAP-04 to PINMAP-09 removals "
        "read from rather than a removal target; no ticket removes the profile's own "
        "rows. PINMAP-05 added eight of them, the optional keys the text-edit row now "
        "reads, seven as full GBA addresses: :86, :89, :90, :91 and :93-96. PINMAP-07a "
        "added the ten declared code anchors at :152-188, which is what moved this row "
        "51 -> 61 and its ROM-space count 45 -> 55. Recorded debt.",
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
        "tools/webfoot/formats/map_graphics.py", 17, 14, 0,
        "the layer-handler words DOMINANT_LAYER_HANDLER, "
        "ABSENT_LAYER_HANDLER and ABSENT_LAYER_RECORD, "
        "plus citations of the container constructors 0x08007B63, 0x0800897B and "
        "the descriptor reads 0x080088E6, 0x08008924. PINMAP-07b resolved the two "
        "handler words by name through the profile's code anchors; the record "
        "address and the constructor citations stay because they are citations "
        "rather than consumers.",
    ),
    Row(
        "tools/webfoot/formats/map_placements.py", 6, 3, 0,
        "the record tail 0x080555A0 and 0x080716EC plus citations of the layout "
        "and loader sites 0x08008C9E and 0x08017DA3. PINMAP-07b read FACTORY_RAW "
        "from placement_types.factory_raw and the handler and sibling words from "
        "their named anchors, which removed three hex lines.",
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
        "tools/webfoot/map_render.py", 3, 3, 0,
        "the background palette address "
        "0x080701B0 repeated in two provenance strings, and a comment citing the "
        "engine loop 0x08009C02..0x08009C12. PINMAP-07b resolved "
        "SUPPORTED_LAYER_HANDLER by name; the palette strings stay because they "
        "are provenance text that shadows a profile key rather than code words.",
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
        "in comments over the counts the codec already verifies. PINMAP-07b did "
        "not need a line here: the module already reads HANDLERS and "
        "SCRIPT_DISPATCH_HANDLER from map_placements by name.",
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
        "tools/webfoot/sprite_attachment.py", 7, 5, 0,
        "the object factory word 0x08017DA3 and the other sibling factory "
        "0x080111A9 in the module docstring, the entry class 0x0800A7A1, the "
        "placement family 0x0800FD55 and the record run the comment measures "
        "from 0x0807831C. PINMAP-07b resolved the two live words by name; the "
        "docstring and comment citations stay.",
    ),
    Row(
        "tools/webfoot/sprite_swap.py", 6, 6, 0,
        "the ROM base 0x08000000, used at six sites to convert an offset to the "
        "address a reference word holds and back. No target address is spelled "
        "here: PINMAP-04 removed the three that shadowed live profile keys, and "
        "the character table, the object palette and the portrait pointer array "
        "now resolve from the actor-sprite layout the caller hands in. The "
        "animation pointer offset 0x54 is still a local constant shadowing the "
        "live key animation_pointer_offset; recorded debt.",
    ),
    Row(
        "tools/webfoot/stats.py", 1, 1, 0,
        "one comment citing the level-cap comparison site 0x08013A00 where the "
        "cap was read. No ticket covers this file yet: recorded debt.",
    ),
    Row(
        "tools/webfoot/textedit/engine.py", 6, 1, 0,
        "the text tool's private per-title row at engine.py:178-199 is gone: its nine "
        "already-carried values read from the packaged profile and its twelve "
        "carrierless ones arrive through new optional catalogue keys, so no number in "
        "that range is spelled here and a profile edit moves the tool. What remains is "
        "the RETAIL container-table offset 0x7B5B64 at :135, a dataclass default with "
        "no profile key; the comments at :155-156, :1087, :1652 and :1690-1691 cite it "
        "and the 0x6F393C art array as evidence; and :253-256 keeps the proven-reference "
        "range, whose evidence is the in-pool 11-of-2,639 against the out-of-pool "
        "281-of-907 measured on the Release 4A image. Debt: the retail offset should "
        "become a profile key so the row has no defaulted address.",
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


def count_line(line: str) -> tuple[int, int, int]:
    """``(hex5, rom_hex, decimal)`` for one line, each 0 or 1.

    The whole parser lives here, so a spelling is exercised at the level the
    patterns live and ``scan`` stays a file-reading wrapper.
    """
    hex5 = rom_hex = 0
    for match in HEX_TOKEN.finditer(line):
        token = match.group()
        if len(token[2:].replace("_", "")) >= 5:
            hex5 = 1
        try:
            value = int(token, 16)  # accepts 0x / 0X and the digit separators
        except ValueError:
            continue  # a token that will not parse counts by length, not as address
        if ROM_START <= value < ROM_END:
            rom_hex = 1
    return hex5, rom_hex, 1 if decimal_in_rom_space(line) else 0


def count_lines(lines: Iterable[str]) -> tuple[int, int, int]:
    """The three per-line counts summed over ``lines``."""
    total = [0, 0, 0]
    for line in lines:
        for index, value in enumerate(count_line(line)):
            total[index] += value
    return total[0], total[1], total[2]


def scan(paths: Sequence[str]) -> dict[str, tuple[int, int, int]]:
    """Per-line counts for every path that carries a literal.

    Returns only the paths with at least one hit. An empty path list, or a path
    that cannot be read, is a ``CensusError``: a measurement nobody can trust is
    never reported as a count of zero. An absolute path is read where it points,
    which is what lets a caller measure a file outside the worktree.
    """
    if not paths:
        raise CensusError("the scan was handed no path to read")
    counted: dict[str, tuple[int, int, int]] = {}
    for path in paths:
        try:
            text = (REPOSITORY_ROOT / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise CensusError(f"{path}: cannot be read ({error})") from error
        counts = count_lines(text.splitlines())
        if any(counts):
            counted[path] = counts
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


class LedgerEntry(NamedTuple):
    """One ticket's declared move of the whole-tree pair, against the publication.

    ``lines`` and ``files`` are signed deltas of that tree measurement, and ``named``
    is the evidence: every ``path:line`` that left or arrived, so the arithmetic can be
    re-measured line by line instead of taken on trust. A move that is not here fails
    the reconciliation guard by name.
    """

    ticket: str
    lines: int
    files: int
    named: tuple[str, ...]
    reason: str


#: Every declared move of the ``HEX5`` tree pair since ``INVENTORY.md`` section 4 was
#: published. Append-only: a ticket that moves the measured pair appends its own entry
#: in its own commit, and no entry is rewritten in place.
RECONCILIATION_LEDGER: tuple[LedgerEntry, ...] = (
    LedgerEntry(
        "PINMAP-02", 1, 0,
        ("tools/runtime/rom008_query_probe.py:105",),
        "the widened token found one line section 4's pattern cannot see: the literal "
        "is spelled with a digit separator",
    ),
    LedgerEntry(
        "PINMAP-04", -3, 0,
        (
            "tools/webfoot/sprite_swap.py:61",
            "tools/webfoot/sprite_swap.py:63",
            "tools/webfoot/sprite_swap.py:67",
            "tools/webfoot/sprite_swap.py:68",
            "tools/webfoot/data/roms.yaml:21",
        ),
        "four counted lines left the sprite swap planner - the character-table and "
        "object-palette constants at :61 and :63, the comment citing the portrait "
        "accessor at :67, and the portrait-array constant at :68 - and one arrived in "
        "the profile catalogue, which is a net -3",
    ),
    LedgerEntry(
        "PINMAP-05", -3, 0,
        (
            "tools/webfoot/textedit/engine.py:155",
            "tools/webfoot/textedit/engine.py:156",
            "tools/webfoot/textedit/engine.py:158",
            "tools/webfoot/textedit/engine.py:179",
            "tools/webfoot/textedit/engine.py:186",
            "tools/webfoot/textedit/engine.py:187",
            "tools/webfoot/textedit/engine.py:189",
            "tools/webfoot/textedit/engine.py:191",
            "tools/webfoot/textedit/engine.py:194",
            "tools/webfoot/textedit/engine.py:195",
            "tools/webfoot/textedit/engine.py:197",
            "tools/webfoot/data/roms.yaml:86",
            "tools/webfoot/data/roms.yaml:89",
            "tools/webfoot/data/roms.yaml:90",
            "tools/webfoot/data/roms.yaml:91",
            "tools/webfoot/data/roms.yaml:93",
            "tools/webfoot/data/roms.yaml:94",
            "tools/webfoot/data/roms.yaml:95",
            "tools/webfoot/data/roms.yaml:96",
        ),
        "eleven counted lines left the text-edit engine - the comments at :155-156 and "
        ":186 and the row's literals at :158, :179, :187, :189, :191, :194, :195 and "
        ":197 - and eight arrived in the profile catalogue, the new optional keys at "
        ":86, :89, :90, :91 and :93-96, which is a net -3. The engine row fell 17 -> 6 "
        "lines and its ROM-space count 5 -> 1; the catalogue row rose 43 -> 51 and its "
        "ROM-space count 37 -> 45 because seven of the new keys are full GBA addresses",
    ),
    LedgerEntry(
        "PINMAP-06", -2, 0,
        (
            "tools/export/canonical.py:164",
            "tools/export/canonical.py:228",
        ),
        "two counted lines left the export reader: the sprite-definition run constant "
        "at :164 and the appearance-table constant at :228, both replaced by a read of "
        "the profile keys tables.actor_sprites.character_table_address and "
        "tables.appearances.address, which is a net -2 and no files. The canonical.py "
        "row fell 11 -> 9 lines and its ROM-space count 11 -> 9, and the enforcement "
        "pair fell by the same two lines because that file is in the enforcement set",
    ),
    LedgerEntry(
        "PINMAP-07a", 10, 0,
        (
            "tools/webfoot/data/roms.yaml:152",
            "tools/webfoot/data/roms.yaml:156",
            "tools/webfoot/data/roms.yaml:160",
            "tools/webfoot/data/roms.yaml:164",
            "tools/webfoot/data/roms.yaml:168",
            "tools/webfoot/data/roms.yaml:172",
            "tools/webfoot/data/roms.yaml:176",
            "tools/webfoot/data/roms.yaml:180",
            "tools/webfoot/data/roms.yaml:184",
            "tools/webfoot/data/roms.yaml:188",
        ),
        "ten counted lines arrived in the profile catalogue: the ten declared code "
        "anchor addresses, the placement factory raw word, the three placement "
        "handlers, the two sibling factories, the three layer handlers and the entry "
        "class, which the profile's resolver now reads by name. No line left and no "
        "file arrived, so the tree pair is +10 lines and the enforcement pair moved "
        "with it; the catalogue row rose 51 -> 61 and its ROM-space count 45 -> 55",
    ),
    LedgerEntry(
        "PINMAP-07b", -12, 0,
        (
            "tools/webfoot/formats/map_placements.py:8",
            "tools/webfoot/formats/map_placements.py:13",
            "tools/webfoot/formats/map_placements.py:14",
            "tools/webfoot/formats/map_placements.py:15",
            "tools/webfoot/formats/map_placements.py:16",
            "tools/webfoot/formats/map_placements.py:176",
            "tools/webfoot/formats/map_graphics.py:133",
            "tools/webfoot/formats/map_graphics.py:134",
            "tools/webfoot/formats/map_graphics.py:166",
            "tools/webfoot/map_render.py:73",
            "tools/webfoot/sprite_attachment.py:218",
            "tools/webfoot/sprite_attachment.py:228",
        ),
        "twelve counted lines left the three consuming modules and none arrived, so the "
        "tree pair is -12 lines and no files and the enforcement pair fell with it. "
        "map_placements.py lines 8, 13, 14, 15, 16 and 176 held FACTORY_RAW, the three "
        "handler keys, SCRIPT_DISPATCH_HANDLER and SIBLING_FACTORIES; map_graphics.py "
        "lines 133, 134 and 166 held DOMINANT_LAYER_HANDLER, ABSENT_LAYER_HANDLER and "
        "TERRAIN_FIELD_LAYER_HANDLER; map_render.py line 73 held SUPPORTED_LAYER_HANDLER; "
        "sprite_attachment.py lines 218 and 228 held the family factory and the entry "
        "class. Those are pre-move line numbers, because the lines no longer exist: each "
        "word now reads its declared anchor by name. placement_events.py keeps its two "
        "citations and is not in the census set",
    ),
    LedgerEntry(
        "PINMAP-09", -9, 0,
        (
            "tools/webfoot/atlas_producers/seed.py:132",
            "tools/webfoot/atlas_producers/seed.py:140",
            "tools/webfoot/atlas_producers/seed.py:254",
            "tools/webfoot/atlas_producers/seed.py:267",
            "tools/webfoot/atlas_producers/seed.py:293",
            "tools/webfoot/atlas_producers/seed.py:425",
            "tools/webfoot/atlas_producers/seed.py:464",
            "tools/webfoot/atlas_producers/seed.py:483",
            "tools/webfoot/atlas_producers/seed.py:511",
            "tools/webfoot/atlas_producers/seed.py:507",
            "tools/webfoot/atlas_producers/seed.py:533",
        ),
        "nine counted lines left tools/webfoot/atlas_producers/seed.py and two arrived, "
        "so the tree pair is -9 lines and no files. The nine held a value the seed now "
        "reads from the profile instead: the placement-type constructor and factory raw "
        "at :132 and :140, the text pool base and its pointer table at :254 and :267, the "
        "MapEntry table base and the character table base at :293 and :425, the "
        "base-stat and enemy-stat table bases at :464 and :483, and the free-window file "
        "offset at :511. The two arrived inside the rewrite that RECORDS the seed's one "
        "conflict as one named row: the consolidated note states the raw base the two "
        "declarations share at :507, and the guard that refuses a moved free window "
        "states the window it requires at :533. Each of the ten rows that restated a "
        "profile key now reads its own declaring key. Those two are current line "
        "numbers because those lines exist; the nine are pre-move line numbers, "
        "because those lines no longer exist",
    ),
)


def expected_census_hex5() -> tuple[int, int]:
    """Section 4's published pair plus every declared move, as the tree pair to expect.

    The publication is quoted, never restated: a ticket that moves the tree declares
    its move here rather than rewriting what section 4 says.
    """
    lines = CENSUS_INVENTORY_S4[0] + sum(entry.lines for entry in RECONCILIATION_LEDGER)
    files = CENSUS_INVENTORY_S4[1] + sum(entry.files for entry in RECONCILIATION_LEDGER)
    return lines, files
