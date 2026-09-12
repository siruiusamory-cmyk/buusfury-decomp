"""ROM-ATLAS-001 Layer D broad discovery passes: the six `scan_*.jsonl` files.

Ported from scratchpad/atlas_scan.py (session
afdddff1-9c87-4859-818c-7a33efc68a28). Read-only against the ROM.

**The pass selector is gone, deliberately.** The original gated its writes behind
`ONLY = set((sys.argv[2] if len(sys.argv) > 2 else "1,2,3,4,5").split(","))`
(atlas_scan.py:23) at :190, :279, :289 and :313, and the artifact mtimes prove it
ran in three separate partial invocations (entropy 09:15, compression 09:32, the
other four 09:47) whose argv was never recorded. The six passes are mutually
independent — `text_rows`, `ptr_rows`, `tables`, entropy, `comp_rows` and
`code_rows` each derive from the ROM bytes and the seed rows only, and the one
cross-reference (`_by_off`, atlas_scan.py:181) lives inside pass 1's own body —
so `build` runs all six, always, in the source order of the original file.

Every threshold is the historical one: UTF-16 runs >= 4 chars, ASCII runs >= 6
chars, text clustering gap <= 64, pointer tables >= 8 entries, entropy grids of
4096 and 1024 bytes with the 7.5 / 3.0 bit bars, the compression probe striding
4 bytes, and a code-shape bar at the image's own 90th percentile.

Both self-checks are kept: the three known-genuine text regions must be found
(atlas_scan.py:179-187), and every seed function must land in a flagged
code-shape block (atlas_scan.py:361-368).
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import re
import struct
from collections import Counter
from pathlib import Path

from .. import atlas
from ..analysis import thumb
from ..formats import webfoot_lz as lz
from ..formats.text_tables import CONTROL_NEWLINE, CONTROL_PREFIX
from ._io import read_jsonl, write_jsonl

BASE = 0x08000000
IMAGE_SIZE = 8388608
PRINT_MIN, PRINT_MAX = 0x20, 0x7E

#: Latin-1 halfwords that are TEXT, not control units. Measured: these are the
#: only three units in the seven compressed-text containers whose low byte
#: exceeds PRINT_MAX, and each sits mid-word (U+00A0 between words, U+00E9 in
#: "decor", U+00EF in "naive"). Treating them as run boundaries split those
#: words in half. This is an explicit three-value allowlist, NOT a rule about
#: high-byte-zero units in general: 0x0002, 0x0007, 0x0008, 0x000A and 0x000B
#: also have a zero high byte and remain control units.
TEXT_LATIN1 = frozenset({0x00A0, 0x00E9, 0x00EF})
TEXT_CLUSTER_GAP = 64
POINTER_TABLE_MIN_ENTRIES = 8
ENTROPY_HIGH_BITS = 7.5
ENTROPY_LOW_BITS = 3.0
CODE_SHAPE_BLOCK = 4096
CODE_SHAPE_PERCENTILE = 0.9

_WORD = re.compile(r"[A-Za-z]{3,}")
_VOWEL = re.compile(r"[AEIOUaeiou]")

#: Regions BUU_DIALOGUE_TEXT_STORES.md documents as genuine prose. 0x77F09A is
#: the one an earlier newline-terminator bug hid, so the check is load-bearing.
_TEXT_SELF_CHECK = ((0x0005794A, "prose"), (0x0077F09A, "prose"), (0x006B7400, "prose"))


def _is_text_halfword(data: bytes, offset: int) -> bool:
    """True when the UTF-16LE halfword at `offset` is a text character.

    ASCII printable, plus the three measured Latin-1 units in `TEXT_LATIN1`.
    """
    if data[offset + 1] != 0:
        return False
    low = data[offset]
    return PRINT_MIN <= low <= PRINT_MAX or low in TEXT_LATIN1


def _prose(text: str) -> bool:
    return bool(_WORD.search(text)) and bool(_VOWEL.search(text)) and " " in text


def _claimed_lookup(seed_rows: list[dict]):
    """Merged extents of every seed row that states a size."""
    claimed = sorted((row["file_offset"], row["file_offset"] + row["size"])
                     for row in seed_rows if row.get("size"))
    merged: list[list[int]] = []
    for start, end in claimed:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    spans = [(start, end) for start, end in merged]
    starts = [start for start, _ in spans]

    def in_claimed(offset: int) -> bool:
        index = bisect.bisect_right(starts, offset) - 1
        return index >= 0 and offset < spans[index][1]

    return in_claimed


# --- pass 1: text ------------------------------------------------------------


def scan_runs(data: bytes, *, require_terminator: bool = True):
    """Yield every UTF-16LE and ASCII text run in `data`.

    The ONE run-extraction implementation. Both the raw-ROM pass (`_text_rows`)
    and the decoded-container pass (`_decoded_text_rows`) go through it, so the
    two surfaces can never drift apart on what counts as a run.

    Each item is `(offset, size, encoding, text)` where `offset` is relative to
    the start of `data` — the caller decides what that offset MEANS. It is a ROM
    file offset only when `data` is the ROM image; for a decoded stream it is an
    offset within that stream and nothing else.

    CONTROL_NEWLINE (0x000A) and the CONTROL_PREFIX pair (0x0008 + operand) are
    IN-STRING units per `text_tables.decode_string`, not terminators, so a run
    must carry them. Breaking on 0x000A hid the entire shop-dialogue region,
    whose lines are newline-separated and so never reach a bare NUL.

    `require_terminator` is what separates the two byte sources, and it is a
    MEASURED difference, not a convenience.

    - Raw ROM (True): a run counts only when it ends on a NUL halfword, and the
      control grammar above is carried IN-string. The pool is NUL-terminated,
      and dropping that requirement would let any printable byte sequence
      anywhere in the image register as a string.
    - A decoded container (False): these streams contain ZERO NUL halfwords —
      measured across all seven containers, 196,386 halfwords, of which 195,363
      are text units and 1,023 are control units (0x0008 328, 0x000B 266, 0x0007 164,
      0x0002 164, 0x000A 101). There is no terminator to require, so a run is
      instead a maximal text span and EVERY control unit ends it, 0x000A and
      0x0008 included.

    "Text" is ASCII printable plus the three Latin-1 units in `TEXT_LATIN1`.
    Those three (0x00A0 seven times, 0x00E9 once, 0x00EF once) are the ONLY
    units in the corpus whose low byte exceeds PRINT_MAX, every one of them
    occurs mid-word, and treating them as boundaries split those words in half.

    That second rule is the one the region was measured with: it yields 681 runs
    of >= 4 characters totalling 195,342 characters across the seven containers.
    The run total is below the 195,363 text units because a run shorter than 4
    characters is not emitted.

    UNKNOWN: what 0x0002, 0x0007 and 0x000B mean, and whether 0x000A separates
    strings here or formats one. They are treated as run boundaries because
    nothing establishes them as in-string units in THIS byte source; that is a
    boundary decision, not a claim about their semantics.

    A run boundary is NOT a string boundary. These streams are indexed by a
    structure this producer does not read, and two logically separate strings
    can sit adjacent with no delimiter between them — so one run may hold
    several strings, and a run's start offset is where printable text starts,
    not where a string is declared to start.
    """
    size = len(data)
    offset = 0
    while offset + 1 < size:
        if _is_text_halfword(data, offset):
            cursor = offset
            chars: list[str] = []
            while cursor + 1 < size:
                unit = data[cursor] | (data[cursor + 1] << 8)
                if _is_text_halfword(data, cursor):
                    chars.append(chr(data[cursor]))
                    cursor += 2
                elif not require_terminator:
                    # Terminator-free source: any non-printable unit ends the run.
                    break
                elif unit == CONTROL_NEWLINE:
                    chars.append("\n")
                    cursor += 2
                elif unit == CONTROL_PREFIX and cursor + 3 < size and data[cursor + 3] == 0:
                    chars.append(f"{{08:{data[cursor + 2]:02X}}}")
                    cursor += 4
                else:
                    break
            terminated = (cursor + 1 < size
                          and data[cursor] == 0 and data[cursor + 1] == 0)
            if len(chars) >= 4 and (terminated or not require_terminator):
                # The size covers the terminator only when there is one.
                span = (cursor - offset) + (2 if terminated else 0)
                yield offset, span, "utf16le", "".join(chars)
                # Resume past this run. `cursor` is always > `offset` here
                # because a run of >= 4 characters was consumed, so this
                # always advances and the walk cannot stall.
                offset = cursor + (2 if terminated else 0)
                continue
            offset = cursor if cursor > offset else offset + 1
        else:
            offset += 1

    offset = 0
    while offset < size:
        if PRINT_MIN <= data[offset] <= PRINT_MAX:
            cursor = offset
            while cursor < size and PRINT_MIN <= data[cursor] <= PRINT_MAX:
                cursor += 1
            terminated = cursor < size and data[cursor] == 0
            if (cursor - offset) >= 6 and (terminated or not require_terminator):
                yield (offset, (cursor - offset) + (1 if terminated else 0), "ascii",
                       data[offset:cursor].decode("ascii"))
            offset = cursor + 1
        else:
            offset += 1


def _text_rows(data: bytes, in_claimed) -> list[dict]:
    """Raw-ROM text runs, then adjacency clustering.

    `text` is the FULL run. `prefix` is kept as the historical 40-character
    preview because existing consumers read it; nothing truncates the searchable
    form any more.
    """
    rows = [{
        "file_offset": offset, "gba_address": f"0x{BASE + offset:08X}",
        "size": size, "encoding": encoding, "char_count": len(text),
        "prose_score": "prose" if _prose(text) else "pattern",
        "cluster_id": None, "prefix": text[:40], "text": text,
        "in_claimed_region": in_claimed(offset), "notes": "",
    } for offset, size, encoding, text in scan_runs(data)]

    rows.sort(key=lambda row: row["file_offset"])
    cluster_id = 0
    previous_end = None
    for row in rows:
        if previous_end is None or row["file_offset"] - previous_end > TEXT_CLUSTER_GAP:
            cluster_id += 1
        row["cluster_id"] = cluster_id
        previous_end = row["file_offset"] + row["size"]

    by_offset = {row["file_offset"]: row for row in rows}
    for offset, want in _TEXT_SELF_CHECK:
        row = by_offset.get(offset)
        assert row is not None, f"self-check: no text run at {offset:#x}"
        assert row["prose_score"] == want, f"self-check: {offset:#x} is {row['prose_score']}"
    return rows


# --- pass 2: pointers and pointer tables -------------------------------------


def _pointer_rows(words, in_claimed) -> list[dict]:
    low, high = BASE, BASE + IMAGE_SIZE
    rows = []
    for index, word in enumerate(words):
        if low <= word < high:
            source = index * 4
            rows.append({
                "file_offset": source, "source_file_offset": source,
                "source_gba": f"0x{BASE + source:08X}",
                "target_file_offset": word - BASE, "target_gba": f"0x{word:08X}",
                "source_in_claimed": in_claimed(source),
                "target_in_claimed": in_claimed(word - BASE),
            })
    return rows


def _pointer_table_rows(words, in_claimed) -> list[dict]:
    low, high = BASE, BASE + IMAGE_SIZE
    is_pointer = [low <= word < high for word in words]
    total = len(words)
    tables = []
    index = 0
    while index < total:
        if not is_pointer[index]:
            index += 1
            continue
        end = index
        while end < total and is_pointer[end]:
            end += 1
        count = end - index
        if count >= POINTER_TABLE_MIN_ENTRIES:
            targets = [words[k] - BASE for k in range(index, end)]
            before_ok = (index == 0) or (not is_pointer[index - 1])
            after_ok = (end == total) or (not is_pointer[end])
            tables.append({
                "file_offset": index * 4, "size": count * 4, "entry_count": count,
                "stride": 4,
                "targets_ascending": all(targets[k] <= targets[k + 1]
                                         for k in range(count - 1)),
                "targets_distinct": len(set(targets)),
                "target_min": targets and min(targets),
                "target_max": targets and max(targets),
                "target_span": max(targets) - min(targets),
                "boundary_sharp": bool(before_ok and after_ok),
                "overlaps_claimed": any(in_claimed(offset) for offset in
                                        range(index * 4, end * 4, 4)),
                "notes": "",
            })
        index = end
    return tables


# --- pass 3: entropy ---------------------------------------------------------


def _entropy_rows(data: bytes, block: int, in_claimed) -> list[dict]:
    rows = []
    for offset in range(0, IMAGE_SIZE, block):
        chunk = data[offset:offset + block]
        counts = Counter(chunk)
        total = len(chunk)
        bits = -sum((count / total) * math.log2(count / total) for count in counts.values())
        distinct = len(counts)
        zero = distinct == 1 and 0 in counts
        ff = distinct == 1 and 0xFF in counts
        if zero or ff:
            classification = atlas.PADDING_CANDIDATE
        elif bits > ENTROPY_HIGH_BITS:
            classification = atlas.UNKNOWN_HIGH_ENTROPY
        elif bits < ENTROPY_LOW_BITS:
            classification = atlas.UNKNOWN_STRUCTURED
        else:
            classification = atlas.UNKNOWN
        rows.append({"file_offset": offset, "size": total,
                     "entropy_bits": round(bits, 4), "zero_run": zero, "ff_run": ff,
                     "distinct_bytes": distinct, "suggested_class": classification,
                     "in_claimed_region": in_claimed(offset),
                     "block_size": block})
    return rows


# --- pass 4: compression -----------------------------------------------------


def _compression_rows(data: bytes, in_claimed) -> tuple[list[dict], int]:
    rows = []
    abandoned = 0
    for offset in range(0, IMAGE_SIZE - lz.HEADER_SIZE + 1, 4):
        if not lz.looks_like_container(data, offset):
            continue
        _kind, declared = lz.read_header(data, offset)
        row = {"file_offset": offset, "gba_address": f"0x{BASE + offset:08X}",
               "declared_decoded_size": declared, "actual_decoded_size": None,
               "packed_size": None, "decode_ok": False, "round_trip_ok": False,
               "in_claimed_region": in_claimed(offset), "notes": ""}
        try:
            container = lz.unpack(data, offset)
            row["decode_ok"] = True
            row["actual_decoded_size"] = len(container.data)
            row["packed_size"] = container.packed_size
            try:
                repacked = lz.pack(container.data)
                row["round_trip_ok"] = lz.unpack(repacked, 0).data == container.data
            except Exception as error:
                row["notes"] = f"repack: {type(error).__name__}"
        except lz.ContainerError as error:
            row["notes"] = str(error)[:120]
        except Exception as error:  # pathological input guard
            abandoned += 1
            row["notes"] = f"ABANDONED {type(error).__name__}"
        rows.append(row)
    return rows, abandoned


# --- pass 4b: text inside decoded containers ---------------------------------

#: The pointer table that DEFINES the compressed-text region, seeded by
#: `seed.py` as `compressed_text.pointer_table` from
#: docs/research/BUU_MAP_EVENT_REFERENCES.md:247. Seven consecutive words, each
#: a ROM address of one container.
COMPRESSED_TEXT_TABLE = 0x007B5B64
COMPRESSED_TEXT_COUNT = 7


def _decoded_text_rows(data: bytes) -> list[dict]:
    """Text runs found INSIDE the decoded compressed-text containers.

    Compression validity is necessary but not sufficient for text-container
    membership. Decoded-text indexing is restricted to structurally supported
    reachable containers to avoid indexing compression-probe noise. That gate is
    a safety property, not a tuning parameter: it is not widened to find more
    text.

    Scope is the pointer-reachable set only. The blind `_compression_rows` probe
    strides 4 bytes over the whole image and 24,285 of its hits "decode and
    round-trip" — 68.7 MiB of decoded output that is overwhelmingly probe noise.
    Indexing that would turn false-positive compression probes into thousands of
    bogus text sources, which is exactly what the atlas must not do. A container
    earns indexing by being REACHED from the seeded table, not by surviving a
    decode.

    A record NEVER carries a ROM offset for the text. Only the container has a
    real ROM address; `decoded_offset` is an offset within the decompressed
    stream and is meaningless as a ROM address, so the two are never summed.
    """
    rows: list[dict] = []
    for index in range(COMPRESSED_TEXT_COUNT):
        word = struct.unpack_from("<I", data, COMPRESSED_TEXT_TABLE + index * 4)[0]
        if not (BASE <= word < BASE + IMAGE_SIZE):
            continue
        container_offset = word - BASE
        if not lz.looks_like_container(data, container_offset):
            continue
        try:
            container = lz.unpack(data, container_offset)
        except Exception as error:  # a wild pointer must not kill the producer
            rows.append({
                "source_kind": "decoded-container-text",
                "container_index": index,
                "container_file_offset": container_offset,
                "container_rom_address": f"0x{word:08X}",
                "decompressor": "webfoot_lz",
                "container_kind": None, "decoded_size": None,
                "decoded_offset": None, "size": None, "encoding": None,
                "char_count": 0, "text": "", "prose_score": "pattern",
                "notes": f"{type(error).__name__}: {str(error)[:100]}",
            })
            continue
        try:
            repacked = lz.pack(container.data)
            round_trip_ok = lz.unpack(repacked, 0).data == container.data
        except Exception:
            round_trip_ok = False
        if not round_trip_ok:
            continue
        for offset, size, encoding, text in scan_runs(container.data,
                                                      require_terminator=False):
            rows.append({
                "source_kind": "decoded-container-text",
                "container_index": index,
                "container_file_offset": container_offset,
                "container_rom_address": f"0x{word:08X}",
                "decompressor": "webfoot_lz",
                "container_kind": container.kind,
                "decoded_size": len(container.data),
                "decoded_offset": offset, "size": size, "encoding": encoding,
                "char_count": len(text), "text": text,
                "prose_score": "prose" if _prose(text) else "pattern",
                "notes": "",
            })
    return rows


# --- pass 5: code shape ------------------------------------------------------


def _code_shape_rows(data: bytes, seed_rows: list[dict], in_claimed) -> tuple[list[dict], int]:
    halfwords = struct.unpack_from(f"<{IMAGE_SIZE // 2}H", data, 0)
    low, high = BASE, BASE + IMAGE_SIZE
    rows = []
    for offset in range(0, IMAGE_SIZE, CODE_SHAPE_BLOCK):
        first = offset // 2
        last = first + CODE_SHAPE_BLOCK // 2
        prologues = branches = branches_in_range = literals = 0
        for index in range(first, last):
            halfword = halfwords[index]
            if thumb.is_push_with_lr(halfword):
                prologues += 1
            if (halfword & 0xF800) == 0xF000 and index + 1 < len(halfwords):
                decoded = thumb.decode_bl(halfword, halfwords[index + 1], BASE + index * 2)
                if decoded is not None:
                    branches += 1
                    if low <= decoded.target < high:
                        branches_in_range += 1
            if thumb.ldr_literal_address(halfword, BASE + index * 2) is not None:
                literals += 1
        score = prologues * 4 + branches_in_range * 2 + literals
        rows.append({"file_offset": offset, "size": CODE_SHAPE_BLOCK,
                     "suggested_class": atlas.UNKNOWN,
                     "prologue_count": prologues, "bl_count": branches,
                     "bl_in_range_count": branches_in_range,
                     "literal_load_count": literals,
                     "code_shape_score": score,
                     "in_claimed_region": in_claimed(offset)})

    # The executable-candidate bar is the image's own 90th percentile, not a
    # number picked in advance. This is PRIORITIZATION only — a high score is
    # never evidence that a block IS code.
    scores = sorted(row["code_shape_score"] for row in rows)
    bar = scores[int(CODE_SHAPE_PERCENTILE * len(scores))]
    for row in rows:
        row["suggested_class"] = (atlas.UNKNOWN_EXECUTABLE_CANDIDATE
                                  if row["code_shape_score"] >= bar else atlas.UNKNOWN)

    # Positive control: every seed function must land in a flagged block, or the
    # probe is broken and its output must not be trusted.
    by_block = {row["file_offset"]: row for row in rows}
    missed = [row["identity"] for row in seed_rows if row.get("kind") == "function"
              and by_block[(row["file_offset"] // CODE_SHAPE_BLOCK)
                           * CODE_SHAPE_BLOCK]["code_shape_score"] < bar]
    assert not missed, f"positive control FAILED for: {missed}"
    return rows, bar


# --- orchestration -----------------------------------------------------------


def build(rom_path: Path, out_dir: Path, report_path: Path | None = None) -> dict:
    """Run all six passes and write all six artifacts. Opens the ROM read-only."""
    rom_path, out_dir = Path(rom_path), Path(out_dir)
    data = rom_path.read_bytes()
    assert len(data) == IMAGE_SIZE, len(data)
    sha_before = hashlib.sha256(data).hexdigest()

    seed_rows = read_jsonl(out_dir / "seed_knowledge.jsonl")
    in_claimed = _claimed_lookup(seed_rows)

    def emit(name: str, rows: list[dict]) -> list[dict]:
        rows = sorted(rows, key=lambda row: row["file_offset"])
        write_jsonl(out_dir / f"{name}.jsonl", rows)
        return rows

    # pass 1
    text_rows = emit("scan_text", _text_rows(data, in_claimed))

    # pass 2
    words = struct.unpack_from(f"<{IMAGE_SIZE // 4}I", data, 0)
    pointer_rows = emit("scan_pointers", _pointer_rows(words, in_claimed))
    table_rows = emit("scan_pointer_tables", _pointer_table_rows(words, in_claimed))

    # pass 3 — both grids, in one file, as the assembler expects (it keeps only
    # the 4 KiB rows for coverage but reads every row as an observation).
    entropy_rows = emit("scan_entropy",
                        _entropy_rows(data, 4096, in_claimed)
                        + _entropy_rows(data, 1024, in_claimed))

    # pass 4
    compression_rows, abandoned = _compression_rows(data, in_claimed)
    compression_rows = emit("scan_compression", compression_rows)

    # pass 4b — the decoded-text index. Its own artifact with its own record
    # shape: decoded text has no ROM offset of its own, so it cannot honestly be
    # an `Observation`, which is defined by a RomRange.
    decoded_text_rows = sorted(
        _decoded_text_rows(data),
        key=lambda row: (row["container_file_offset"], row["decoded_offset"] or 0))
    write_jsonl(out_dir / "scan_decoded_text.jsonl", decoded_text_rows)

    # pass 5
    code_shape_rows, bar = _code_shape_rows(data, seed_rows, in_claimed)
    code_shape_rows = emit("scan_code_shape", code_shape_rows)

    sha_after = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    assert sha_after == sha_before, "ROM changed during the scan"

    summary = {
        "scan_text": len(text_rows), "scan_pointers": len(pointer_rows),
        "scan_pointer_tables": len(table_rows), "scan_entropy": len(entropy_rows),
        "scan_compression": len(compression_rows),
        "scan_decoded_text": len(decoded_text_rows),
        "scan_code_shape": len(code_shape_rows),
        "abandoned": abandoned, "code_shape_p90_bar": bar,
        "sha_before": sha_before, "sha_after": sha_after,
    }
    if report_path is not None:
        Path(report_path).write_text(json.dumps(summary, indent=1, sort_keys=True),
                                     encoding="utf-8")
    return summary
