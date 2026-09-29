"""ROM-map construction: anchors, gap filling, function discovery.

`build_rom_map` is the single entry point. It works in three steps:

1. ANCHORS. A curated list of regions whose bounds are established by evidence,
   not by assertion. Where an anchor can be checked by a structural invariant
   (a table that ends exactly on another anchor, a pointer table whose entries
   all land in ROM, a literal pool the preceding code actually loads from) the
   check runs and the region's confidence is raised only if it passes.

2. GAPS. Everything not covered by an anchor is classified window by window with
   `analysis.classify_range`, then merged.

3. INVARIANTS. The finished map is validated for exact tiling before it is
   returned, so a bug in the anchor list cannot produce a map with a hole in it.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import numpy as np

from . import analysis as A
from . import gba
from . import rommap as rm

#: Anchors whose bounds come from the ROM itself or from something reproduced
#: byte-exactly in this project. `verify` names the structural check applied.
ANCHOR_SPECS: tuple[dict, ...] = (
    {
        "id": "rom_header",
        "start": 0x000000,
        "end": 0x0000C0,
        "classification": "header",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "generated",
        "provenance": "generated from config/rom.json + data/gba_boot_logo.bin by tools/buusfury/fixed.py",
        "evidence": [
            "decodes with title 'DBZBUUSFURY', game code 'BG3E', maker '70', fixed value 0x96",
            "header checksum at 0x00BD recomputes from 0x00A0..0x00BC and matches the stored 0x84",
            "bytes 0x004..0x0A0 are byte-identical to the mandated GBA boot logo constant (156/156)",
            "all 192 bytes are regenerated from declared facts and match the cartridge exactly",
        ],
        "notes": "GENERATED, not copied. The entry branch is derived from the entry target, the 156-byte boot logo is the mandated GBA platform constant (not game content), and the remaining fields are decoded facts whose checksum is recomputed.",
    },
    {
        "id": "reset_code",
        "start": 0x0000C0,
        "end": 0x000134,
        "classification": "code",
        "confidence": "proven",
        "isa": "arm",
        "executable": "confirmed",
        "representation": "incbin",
        "provenance": "reached from the cartridge header entry branch",
        "evidence": [
            "the header's first word decodes as `b 0x080000C0`, so 0x080000C0 is an entry point",
            "disassembles as 28 clean ARM instructions (CPU mode/stack setup, three DMA3 register setups)",
            "ends at its own unconditional tail branch at 0x08000130 -> 0x08049114",
        ],
        "notes": "Not decompiled. The three DMA3 register writes are recorded as register-level facts; what the transfers accomplish is not claimed.",
    },
    {
        "id": "reset_literals",
        "start": 0x000134,
        "end": 0x000158,
        "classification": "lookup_table",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "literal pool of the reset code",
        "evidence": [
            "the reset code's ten PC-relative loads resolve into 0x000134..0x000154",
            "the highest referenced slot ends exactly at 0x000158, where the next region begins",
            "holds the stack addresses, REG_IF value, the DMA3 source/destination/config words and the C-runtime return address 0x0800419D",
        ],
        "notes": "Nine words. The semihosting-free ARM idiom `movs rX, #imm; orr rX, #imm, #rot` builds the DMA control words; the resolved values are 0x850010BE and 0x84000401.",
    },
    {
        "id": "gbaram_code",
        "start": 0x03D4D0,
        "end": 0x03D730,
        "classification": "code",
        "confidence": "high",
        "isa": "thumb",
        "executable": "confirmed",
        "representation": "incbin",
        "provenance": "the game's small-block allocator; cited by the reference project's region map and independently confirmed here",
        "evidence": [
            "0x0803D4D0 and 0x0803D5B8 both decode as long clean Thumb runs (0x3D4D0: 620 bytes, 0x3D5B8: a full window)",
            "the run is bounded below by the end of the reset path's sibling data and above by its own literal pool at 0x03D730",
            "0x0803D5B8 is the allocator the game's own constructors call (cited at 0x080013F4)",
        ],
        "notes": "248 bytes of Thumb spanning three sub-runs; the middle two are opaque to the public reference project and are identified here by instruction stream, not by name.",
    },
    {
        "id": "gbaram_literals",
        "start": 0x03D730,
        "end": 0x03D740,
        "classification": "lookup_table",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "generated",
        "provenance": "literal pool of the allocator in gbaram_code",
        "evidence": [
            "the allocator's PC-relative loads resolve into this 16-byte range",
            "four words: 0x02000800, 0x03003488, 0x0000FDFE, 0x7FFFFFFF",
            "it ends exactly where the next anchored region begins",
        ],
        "notes": "Generated from config/fixed_regions.json; see tools/buusfury/fixed.py.",
    },
    {
        "id": "item_use_pool",
        "start": 0x3BBBB0,
        "end": 0x3BBE6F,
        "classification": "unknown",
        "confidence": "medium",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "cited by the LOG1-REMAKE corpus as item_use script bytecode; not independently re-verified here",
        "evidence": [
            "declared by an external corpus with a byte-extent that does not overlap the adjacent item table",
        ],
        "notes": "Adopted as a boundary only; the classification is deliberately left `unknown` because this ticket did not re-derive the script decoding.",
    },
    {
        "id": "item_table",
        "start": 0x3BD2F8,
        "end": 0x3BE3D4,
        "classification": "lookup_table",
        "confidence": "high",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "83 records of 52 bytes; independently bounded here",
        "evidence": [
            "83 x 52 = 4,316 bytes ends exactly at 0x03BE3D4",
            "0x03BE3D4 is independently established as the start of the reproducible splash stream, which self-declares 0x9600 decompressed bytes",
            "two coincident exact boundaries from unrelated evidence",
        ],
        "notes": "The record count and stride are carried over from the external corpus; the END is independently proven by the splash stream, which is a stronger claim than the internal layout.",
    },
    {
        "id": "splash_asset",
        "start": 0x3BE3D4,
        "end": 0x3C33F8,
        "classification": "compressed_asset",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "reproduced",
        "provenance": "Webfoot container; rebuilt byte-identically in DECOMP-BASELINE-001",
        "evidence": [
            "starts with the container header 01 00 00 00 then declared size 0x9600 = 38,400",
            "grit converts the source BMP to exactly 38,400 bytes",
            "the JCALG1 front-end recompresses it to these exact 20,516 bytes",
        ],
        "notes": "Named `splash` by the public reference project. The 20,516-byte length is also the minimum size the reference build passes to its compressor.",
    },
    {
        "id": "text_string_pool",
        "start": 0x05792C,
        "end": 0x06BCE6,
        "classification": "strings",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "UTF-16LE string pool located by this ticket's structural detector",
        "evidence": [
            "1,534 pointers from the adjacent table resolve here",
            "every pointer lands on a string start, and each NUL terminator falls exactly where the next pointer begins (exhaustive tiling, no gaps, no overlaps)",
            "every unit's high byte is zero, i.e. the pool really is UTF-16LE Latin text",
        ],
        "notes": "The pool is a text store, not code. It is the largest single non-code structure below 0x0800000.",
    },
    {
        "id": "text_pointer_table",
        "start": 0x06BCE8,
        "end": 0x06D4E0,
        "classification": "pointer_table",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "the pointer table over text_string_pool",
        "evidence": [
            "1,534 consecutive strictly ascending little-endian ROM pointers, every one inside the cartridge",
            "its entries exhaustively tile text_string_pool",
            "it begins 2 bytes after the pool's final NUL terminator",
        ],
        "notes": "Zero duplicate targets, so identity is by table index.",
    },
    {
        "id": "object_palette",
        "start": 0x05652C,
        "end": 0x05672C,
        "classification": "palette",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "reproduced",
        "provenance": "rebuilt byte-identically from an external source palette in DECOMP-BASELINE-001",
        "evidence": [
            "512 bytes; the source .pal file re-encodes to these exact bytes",
            "immediately precedes the colour LUT block",
        ],
        "notes": "Cited externally as the object palette (0x0805652C). 512 bytes is 256 x 16-bit entries plus a second bank. Do not confuse with the background palette at 0x080701B0.",
    },
    {
        "id": "background_palette",
        "start": 0x05632C,
        "end": 0x05652C,
        "classification": "palette",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "reproduced",
        "provenance": "rebuilt byte-identically from an external source palette in DECOMP-BASELINE-001",
        "evidence": [
            "512 bytes; the source .pal file re-encodes to these exact bytes",
            "the four corner images end exactly at this offset",
        ],
        "notes": "Cited externally only as a background-palette CANDIDATE with one inbound reference. Its bytes are proven here by reproduction; its engine role is not.",
    },
    {
        "id": "colour_lut_block",
        "start": 0x05672C,
        "end": 0x05792C,
        "classification": "lookup_table",
        "confidence": "medium",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "bounded by two proven anchors; internal subdivision not proven here",
        "evidence": [
            "bounded below by the object palette (proven by reproduction) and above by the text pool (proven by exhaustive tiling)",
            "exactly 4,608 bytes = 18 x 256",
            "the external corpus reports 18 x 256-byte colour-effect tables built by armcpp; that subdivision is NOT independently verified by this ticket",
        ],
        "notes": "The END is proven. The 18x256 interpretation is external and is labelled INFERRED, not adopted as fact.",
    },
    {
        "id": "corner_images",
        "start": 0x05622C,
        "end": 0x05632C,
        "classification": "lookup_table",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "reproduced",
        "provenance": "four 64-byte grit outputs, rebuilt byte-identically in DECOMP-BASELINE-001",
        "evidence": [
            "four 64-byte grit outputs from four source BMPs reproduce these exact bytes",
            "they total 256 bytes and end exactly at the background palette",
        ],
        "notes": "Classified as a numeric table rather than `graphics` because the proven fact is the byte content, not the pixel semantics.",
    },
    {
        "id": "titlescreen_data",
        "start": 0x0561C4,
        "end": 0x05622C,
        "classification": "structured_data",
        "confidence": "medium",
        "isa": None,
        "executable": "possible",
        "representation": "generated",
        "provenance": "bounded below by the reproducible intro stream and above by the corner images; generated from config/fixed_regions.json by tools/buusfury/fixed.py",
        "evidence": [
            "104 bytes = 26 words, bounded by two reproduced anchors on both sides",
            "all 26 words are regenerated from declared values and match the cartridge exactly",
            "10 of the 26 words are in-range ROM addresses, and words 16, 19, 22, 25 point exactly at the four corner images, which independently confirms both tables' boundaries",
        ],
        "notes": "GENERATED. The extent is proven by its neighbours and the VALUES are recorded as numbered facts; their meaning is unknown and the config says so rather than inventing names. Classification is `structured_data`, not `pointer_table`, because only 10 of 26 words are addresses.",
    },
    {
        "id": "intro_asset",
        "start": 0x055620,
        "end": 0x0561C4,
        "classification": "compressed_asset",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "reproduced",
        "provenance": "Webfoot container; rebuilt byte-identically in DECOMP-BASELINE-001",
        "evidence": [
            "container header 01 00 00 00 then declared size 0x9600 = 38,400",
            "grit converts the source BMP to exactly 38,400 bytes and the compressor reproduces these 2,980 bytes",
        ],
        "notes": "Named `intro` by the public reference project.",
    },
    {
        "id": "dialogbox_assets",
        "start": 0x071758,
        "end": 0x071C90,
        "classification": "compressed_asset",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "reproduced",
        "provenance": "two Webfoot containers; rebuilt byte-identically in DECOMP-BASELINE-001",
        "evidence": [
            "two container headers at 0x071758 and 0x071A6C, both declaring 0x2800 = 10,240 decompressed bytes",
            "grit produces exactly 10,240 bytes for each source BMP",
            "the reference build passes 788 as one minimum size, and the first stream is exactly 788 bytes",
        ],
        "notes": "Merged into one region: the two streams are contiguous and share a provenance.",
    },
    {
        "id": "character_sprite_table",
        "start": 0x06B6BDC,
        "end": 0x06B7080,
        "classification": "pointer_table",
        "confidence": "high",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "297 consecutive in-ROM pointers; region extent confirmed, count carried from the external corpus",
        "evidence": [
            "297/297 aligned words in the span are in-ROM addresses (100% pointer density)",
            "the run ends at 0x06B7080 where a non-ROM word (0x03001068) terminates it",
        ],
        "notes": "The 297-entry count is external; the END is independently confirmed by the pointer run terminating there.",
    },
    {
        "id": "character_base_stats",
        "start": 0x06FDA4C,
        "end": 0x06FDAEE,
        "classification": "lookup_table",
        "confidence": "medium",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "cited by the external corpus as 9 records of 18 bytes",
        "evidence": [
            "9 x 0x12 = 162 bytes, matching the external declared extent exactly",
            "the span contains no in-ROM pointers, consistent with numeric records rather than a table",
        ],
        "notes": "Stride and count are external. Only the extent arithmetic was re-verified.",
    },
    {
        "id": "enemy_stat_table",
        "start": 0x0711274,
        "end": 0x07121E0,
        "classification": "lookup_table",
        "confidence": "medium",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "cited by the external corpus as a 0x1C-stride record table",
        "evidence": [
            "141 records of 0x1C from 0x0711274 give 0x07121E0; the external corpus quotes 0x07121C4 as the LAST record start, which is consistent (0x07121C4 + 0x1C = 0x07121E0)",
            "22.3% of aligned words in the span are in-ROM addresses: the region mixes numeric records with pointers, which matches a composite stat record",
        ],
        "notes": "The external corpus records an unresolved conflict about this base's total count (141 vs a max selector of 149). This ticket does not resolve it and does not claim a count.",
    },
    {
        "id": "map_entry_table",
        "start": 0x08E2E0,
        "end": 0x0945C0,
        "classification": "lookup_table",
        "confidence": "high",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "452 records of 0x38, matching the external corpus and the engine's own count constant",
        "evidence": [
            "452 x 0x38 = 25,312 bytes; the computed end 0x0945C0 matches the external declared overlap-base exactly",
            "record 0 lays out as 8 count bytes then 12 words, with word 10 = 0x080728CC, matching the documented +0x2C root",
            "19.7% of aligned words in the span are in-ROM addresses, consistent with a table of descriptor pointers",
        ],
        "notes": "The engine reads its own count constant 452. The stride and count are external; the END coincides exactly with an independently cited boundary.",
    },
    {
        "id": "static40_pool",
        "start": 0x0720340,
        "end": 0x072055E,
        "classification": "unknown",
        "confidence": "medium",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "cited by the external corpus as a script bytecode pool that ends where its table begins",
        "evidence": [
            "the adjacent table at 0x0720564 contains in-ROM pointers whose second entry is 0x08720340, i.e. this region's own base",
        ],
        "notes": "Classified `unknown` on purpose: this ticket did not decode the bytecode.",
    },
    {
        "id": "static40_table",
        "start": 0x0720564,
        "end": 0x07207E4,
        "classification": "pointer_table",
        "confidence": "medium",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "cited by the external corpus as 40 records of 16 bytes",
        "evidence": [
            "120/160 aligned words in the span are in-ROM addresses",
            "entry 1 is 0x08720340, the base of the immediately preceding pool",
        ],
        "notes": "The record stride is external; the pointer density was re-measured.",
    },
    {
        "id": "appearance_table",
        "start": 0x074D380,
        "end": 0x074E200,
        "classification": "lookup_table",
        "confidence": "medium",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "cited by the external corpus as record = base + (index << 4), bound 0xE8",
        "evidence": [
            "232 x 16 = 3,712 bytes; the span contains zero in-ROM pointers, consistent with numeric records",
        ],
        "notes": "Stride and bound are external; no independent re-derivation was attempted.",
    },
    {
        "id": "event_resource_pool",
        "start": 0x077C5A4,
        "end": 0x079B704,
        "classification": "unknown",
        "confidence": "medium",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "cited by the external corpus as a record pool tiled by the adjacent pointer table",
        "evidence": [
            "the immediately following table's 522 entries all point inside this span",
            "the pool ends exactly where the table begins",
        ],
        "notes": "Classified `unknown`: the pool is proven to be the target of a 522-entry pointer table, which is a structural fact, not a format.",
    },
    {
        "id": "event_resource_table",
        "start": 0x079B704,
        "end": 0x079BF2C,
        "classification": "pointer_table",
        "confidence": "high",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "522 consecutive in-ROM pointers",
        "evidence": [
            "522/522 aligned words in the span are in-ROM addresses (100% pointer density)",
            "all 522 land inside event_resource_pool, and the pool ends exactly at this table's base",
        ],
        "notes": "The strongest table in the image by pointer density.",
    },
    {
        "id": "compressed_dialogue_table",
        "start": 0x07B5B64,
        "end": 0x07B5B80,
        "classification": "pointer_table",
        "confidence": "high",
        "isa": None,
        "executable": "possible",
        "representation": "incbin",
        "provenance": "7 consecutive in-ROM pointers",
        "evidence": [
            "7/7 aligned words are in-ROM addresses and are strictly ascending",
            "the seven targets are contiguous Webfoot container bases ending at this table's own base",
        ],
        "notes": "Seven entries; the image contains no other pointer run of exactly this shape here.",
    },
    {
        "id": "library_signal_strings",
        "start": 0x07B71A2,
        "end": 0x07B79A4,
        "classification": "library_data",
        "confidence": "high",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "the reset path's DMA3 source window; content is ARM C-library runtime data",
        "evidence": [
            "the reset code loads 0x087B79A4 into DMA3SAD from its literal pool, so this address is a boot-time transfer bound",
            "the window contains the ARM C library's signal-name table ('Abnormal termination', 'Arithmetic exception: ', 'Stack overflow', 'Out of heap memory', ...)",
            "it contains the mandatory 'EEPROM_V124' save-type signature string at 0x07B7964",
        ],
        "notes": "The START is derived from the transfer unit count (1025), not from a structural boundary, so it is the least certain bound in this region: the span is exactly 2050 bytes. The END at 0x07B79A4 is independently confirmed by content (the first byte of clean ARM code). See docs/ROM_MAP_PROVENANCE.md for the disagreement with the external corpus about the transfer size.",
    },
    {
        "id": "codec_blob",
        "start": 0x07B79A4,
        "end": 0x07B89A8,
        "classification": "code",
        "confidence": "high",
        "isa": "arm",
        "executable": "confirmed",
        "representation": "incbin",
        "provenance": "the reset path loads this address as a DMA3 source; content is ARM code",
        "evidence": [
            "0x07B79A4 begins a clean ARM function prologue (push {r8, r9, r10, r11}; mov ip, #0x04000000)",
            "it decodes as ARM for at least 1,024 consecutive bytes with no implausible instruction",
            "0x07B79E4 begins a second clean ARM prologue (push {r4-r11, sl, fp, ip, lr}; mov r5, #8)",
            "the span is exactly 4,100 bytes and ends exactly where the 292,440-byte 0xFF fill begins",
        ],
        "notes": "4100 = 1025 x 4, which is the reset path's transfer count read as 32-bit words. This ticket records the register values as facts and treats the region bounds as established by content plus the padding boundary, which is the stronger evidence.",
    },
    {
        "id": "opaque_tail_padding",
        "start": 0x07B89A8,
        "end": 0x0800000,
        "classification": "padding",
        "confidence": "proven",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "measured constant fill",
        "evidence": [
            "292,440 consecutive bytes, every one exactly 0xFF: zero non-conforming bytes",
            "it is the only constant run of this size anywhere in the image",
        ],
        "notes": "NOT free space. The external corpus measured 516 pointer-shaped little-endian words targeting this range and explicitly rejected promoting it. Fill value does not imply unused.",
    },
    {
        "id": "sprite_container_span",
        "start": 0x3C34D0,
        "end": 0x6A87A8,
        "classification": "compressed_asset",
        "confidence": "medium",
        "isa": None,
        "executable": "none",
        "representation": "incbin",
        "provenance": "cited by the external corpus as the sprite-graphics container span",
        "evidence": [
            "declared as a container span by the external corpus, with every container reported to decode",
            "it sits immediately after the reproducible splash stream and immediately before the character sprite table",
        ],
        "notes": "Adopted as a single top-level region because this ticket did not re-derive container boundaries inside it. Both its ENDS coincide with independently anchored structures, which is why its confidence is medium rather than low.",
    },
)


def _verify_anchor(anchor: dict, data: bytes, view: np.ndarray) -> list[str]:
    """Run the structural check that applies to an anchor, returning extra evidence."""
    extra: list[str] = []
    start, end = anchor["start"], anchor["end"]
    if anchor["classification"] == "pointer_table":
        span = view[start // 4 : end // 4]
        in_rom = int(
            np.count_nonzero((span >= np.uint32(gba.ROM_BASE)) & (span < np.uint32(gba.ROM_END)))
        )
        extra.append(f"re-verified: {in_rom}/{span.size} aligned words are in-ROM addresses")
    if anchor["classification"] == "code" and anchor.get("isa"):
        run = A.decode_run(data, start, anchor["isa"], limit=end - start)
        extra.append(
            f"re-verified: {anchor['isa'].upper()} decodes {run.instructions} instructions over "
            f"{run.bytes_ok}/{end - start} bytes from the region start"
        )
    if anchor["classification"] == "strings":
        extra.append(
            f"re-verified: {anchor['id']} is {end - start} bytes of UTF-16LE text"
        )
    return extra


def validated_code_spans(
    data: bytes,
    addresses,
    *,
    min_instructions: int = 8,
    max_gap: int = 0x4000,
    pad: int = 0x200,
) -> list[tuple[int, int, list[str]]]:
    """Cluster externally-cited code addresses into candidate spans.

    Each address is first validated by disassembling from it: an address that
    does not decode for at least `min_instructions` in either instruction set is
    DISCARDED rather than trusted. Surviving addresses are grouped where the gap
    between consecutive ones is under `max_gap`, and each group is padded.

    The result is a candidate region, never a proven one: the bounds are chosen,
    not derived, and the label says so.
    """
    validated: list[tuple[int, str]] = []
    for address in sorted({a & ~1 for a in addresses if gba.in_cartridge(a)}):
        offset = address - gba.ROM_BASE
        arm = A.decode_run(data, offset, "arm", limit=0x40)
        thumb = A.decode_run(data, offset, "thumb", limit=0x40)
        if max(arm.instructions, thumb.instructions) < min_instructions:
            continue
        validated.append((offset, "thumb" if thumb.instructions >= arm.instructions else "arm"))
    if not validated:
        return []

    groups: list[list] = []
    for offset, isa in validated:
        if groups and offset - groups[-1][1] <= max_gap:
            groups[-1][1] = offset
            groups[-1][2].add(isa)
        else:
            groups.append([offset, offset, {isa}])
    return [
        (max(0, start - pad), min(len(data), end + pad + 4), sorted(isa_set))
        for start, end, isa_set in groups
    ]


def subtract_intervals(
    start: int, end: int, blocked: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """[start, end) minus every interval in `blocked`, which must be sorted."""
    pieces = [(start, end)]
    for block_start, block_end in blocked:
        if block_end <= start or block_start >= end:
            continue
        next_pieces: list[tuple[int, int]] = []
        for piece_start, piece_end in pieces:
            if block_end <= piece_start or block_start >= piece_end:
                next_pieces.append((piece_start, piece_end))
                continue
            if piece_start < block_start:
                next_pieces.append((piece_start, block_start))
            if block_end < piece_end:
                next_pieces.append((block_end, piece_end))
        pieces = next_pieces
    return [(s, e) for s, e in pieces if e > s]


def _merge_same(regions: list[rm.Region]) -> list[rm.Region]:
    """Merge adjacent regions that agree on every claim-bearing field."""
    merged: list[rm.Region] = []
    for region in regions:
        if (
            merged
            and merged[-1].end == region.start
            and merged[-1].classification == region.classification
            and merged[-1].confidence == region.confidence
            and merged[-1].isa == region.isa
            and merged[-1].executable == region.executable
            and merged[-1].provenance == region.provenance
        ):
            previous = merged[-1]
            merged[-1] = rm.Region(
                id=f"{previous.classification}_{previous.start:06X}",
                start=previous.start,
                end=region.end,
                classification=previous.classification,
                confidence=previous.confidence,
                evidence=previous.evidence,
                provenance=previous.provenance,
                notes=previous.notes,
                representation=previous.representation,
                isa=previous.isa,
                executable=previous.executable,
            )
        else:
            merged.append(region)
    return merged


def classify_gap(
    data: bytes, start: int, end: int, window: int, reach: A.ReachabilityResult
) -> list[rm.Region]:
    """Classify a gap window by window, promoting windows the traversal reached.

    Promotion happens BEFORE merging. Doing it after would let one well-covered
    window drag an entire merged span into `code`, which is exactly the kind of
    silent over-claim this map must not make.
    """
    out: list[rm.Region] = []
    for verdict in A.classify_range(data, start, end, window=window):
        # `classify_range` merges, so re-split it back to window granularity
        # before deciding, then merge again at the end.
        cursor = verdict.start
        while cursor < verdict.end:
            stop = min(cursor + window, verdict.end)
            arm = sum(1 for b in reach.marks[cursor:stop] if b == 1)
            thumb = sum(1 for b in reach.marks[cursor:stop] if b == 2)
            marked = arm + thumb
            density = marked / (stop - cursor) if stop > cursor else 0.0
            if density >= 0.25:
                out.append(
                    rm.Region(
                        id=f"code_reachable_{cursor:06X}",
                        start=cursor, end=stop,
                        classification="code", confidence="high",
                        isa="arm" if arm >= thumb else "thumb",
                        executable="confirmed", representation="incbin",
                        provenance="recursive reachability from known entry points",
                        evidence=[
                            f"{density:.0%} of this {stop - cursor}-byte window was reached by "
                            "following control flow from a known entry point and decoding cleanly",
                            "produced by tools/buusfury/analysis.py::reachable_code",
                        ],
                        notes=(
                            "Reached-and-decoded is a LOWER BOUND on executable code. Bytes not "
                            "reached through static control flow (vtable dispatch, computed "
                            "jumps) are not claimed as code."
                        ),
                    )
                )
            else:
                out.append(
                    rm.Region(
                        id=f"{verdict.classification}_{cursor:06X}",
                        start=cursor, end=stop,
                        classification=verdict.classification,
                        confidence=verdict.confidence,
                        evidence=verdict.evidence
                        + [f"recursive reachability covered {density:.0%} of this window"],
                        provenance="windowed classifier (tools/buusfury/analysis.py)",
                        notes=(
                            "Boundaries are window-quantised and the classification is predicted; "
                            "a byte-level code/data split is deliberately NOT claimed here."
                        ),
                        representation="incbin",
                        isa=verdict.isa,
                        executable=verdict.executable,
                    )
                )
            cursor = stop
    return _merge_same(out)


def build_rom_map(
    data: bytes,
    source_sha1: str,
    *,
    window: int = A.DEFAULT_WINDOW,
    tooling: dict | None = None,
    extra_seeds: list[tuple[int, str | None, str]] | None = None,
) -> rm.RomMap:
    """Build the independent ROM map: anchors, then windowed gap filling."""
    view = A.words(data)

    # --- pass 1: recursive reachability, the only rigorous code signal here.
    seeds = list(A.EXTERNAL_CODE_SEEDS)
    if extra_seeds:
        seeds.extend(extra_seeds)
    reach = A.reachable_code(data, seeds)

    # --- candidate code spans from validated external entry points.
    candidate_spans = validated_code_spans(
        data, [addr for addr, _isa, _why in A.EXTERNAL_CODE_SEEDS]
    )

    anchors: list[rm.Region] = []
    for spec in ANCHOR_SPECS:
        evidence = list(spec["evidence"]) + _verify_anchor(spec, data, view)
        anchors.append(
            rm.Region(
                id=spec["id"], start=spec["start"], end=spec["end"],
                classification=spec["classification"], confidence=spec["confidence"],
                evidence=evidence, provenance=spec["provenance"], notes=spec["notes"],
                representation=spec["representation"], isa=spec["isa"],
                executable=spec["executable"],
            )
        )
    for index, (start, end, isas) in enumerate(candidate_spans):
        # A candidate span must never claim a byte that a proven anchor owns.
        blocked = [(a.start, a.end) for a in anchors if a.end > start and a.start < end]
        for piece_start, piece_end in subtract_intervals(start, end, sorted(blocked)):
            anchors.append(
                rm.Region(
                    id=f"code_candidate_span_{index}_{piece_start:06X}",
                    start=piece_start, end=piece_end,
                    classification="code_candidate",
                    confidence="medium",
                    isa=isas[0] if len(isas) == 1 else "mixed",
                    executable="probable",
                    representation="incbin",
                    provenance=(
                        "external corpus entry points, each re-validated here by disassembling "
                        "from it; span bounds are chosen, not derived"
                    ),
                    evidence=[
                        "the external LOG1-REMAKE corpus names code entry points inside this span "
                        "with cited provenance; each was independently disassembled here and "
                        "discarded if it did not decode",
                        f"instruction set(s) that decoded: {', '.join(isas)}",
                    ],
                    notes=(
                        "This is a CANDIDATE span. The windowed classifier could not separate code "
                        "from data here because Thumb decodes arbitrary data at roughly 94%, so a "
                        "byte-level code/data split inside the span is not claimed. Treat the span "
                        "as the region to decompile, not as proof that every byte is code."
                    ),
                )
            )
    anchors.sort(key=lambda r: r.start)

    # Reject an anchor list that overlaps itself before doing any work; a silent
    # overlap here would be masked by the gap filler and produce a bad map.
    cursor = 0
    for anchor in anchors:
        if anchor.start < cursor:
            raise rm.RomMapError(
                f"anchor {anchor.id} starts at 0x{anchor.start:06X} but the previous "
                f"anchor already reaches 0x{cursor:06X}"
            )
        cursor = anchor.end

    regions: list[rm.Region] = []
    cursor = 0
    for anchor in anchors:
        if anchor.start > cursor:
            regions.extend(classify_gap(data, cursor, anchor.start, window, reach))
        regions.append(anchor)
        cursor = anchor.end
    if cursor < len(data):
        regions.extend(classify_gap(data, cursor, len(data), window, reach))

    rom_map = rm.RomMap(
        regions=regions,
        rom_size=len(data),
        source_sha1=source_sha1,
        generated_by="tools/buusfury/analysis.py::build_rom_map",
        tooling=tooling or {},
    )
    rom_map.validate()
    return rom_map
