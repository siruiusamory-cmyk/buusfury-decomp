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


def _text_rows(data: bytes, in_claimed) -> list[dict]:
    """UTF-16LE and ASCII NUL-terminated runs, then adjacency clustering.

    CONTROL_NEWLINE (0x000A) and the CONTROL_PREFIX pair (0x0008 + operand) are
    IN-STRING units per `text_tables.decode_string`, not terminators, so a run
    must carry them. Breaking on 0x000A hid the entire shop-dialogue region,
    whose lines are newline-separated and so never reach a bare NUL.
    """
    size = len(data)
    rows: list[dict] = []
    offset = 0
    while offset + 1 < size:
        if data[offset + 1] == 0 and PRINT_MIN <= data[offset] <= PRINT_MAX:
            cursor = offset
            chars: list[str] = []
            while cursor + 1 < size:
                unit = data[cursor] | (data[cursor + 1] << 8)
                if data[cursor + 1] == 0 and PRINT_MIN <= data[cursor] <= PRINT_MAX:
                    chars.append(chr(data[cursor]))
                    cursor += 2
                elif unit == CONTROL_NEWLINE:
                    chars.append("\n")
                    cursor += 2
                elif unit == CONTROL_PREFIX and cursor + 3 < size and data[cursor + 3] == 0:
                    chars.append(f"{{08:{data[cursor + 2]:02X}}}")
                    cursor += 4
                else:
                    break
            # require a NUL terminator halfword
            if (len(chars) >= 4 and cursor + 1 < size
                    and data[cursor] == 0 and data[cursor + 1] == 0):
                text = "".join(chars)
                rows.append({
                    "file_offset": offset, "gba_address": f"0x{BASE + offset:08X}",
                    "size": (cursor - offset) + 2, "encoding": "utf16le",
                    "char_count": len(chars),
                    "prose_score": "prose" if _prose(text) else "pattern",
                    "cluster_id": None, "prefix": text[:40],
                    "in_claimed_region": in_claimed(offset), "notes": "",
                })
                offset = cursor + 2
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
            if (cursor - offset) >= 6 and cursor < size and data[cursor] == 0:
                text = data[offset:cursor].decode("ascii")
                rows.append({
                    "file_offset": offset, "gba_address": f"0x{BASE + offset:08X}",
                    "size": (cursor - offset) + 1, "encoding": "ascii",
                    "char_count": cursor - offset,
                    "prose_score": "prose" if _prose(text) else "pattern",
                    "cluster_id": None, "prefix": text[:40],
                    "in_claimed_region": in_claimed(offset), "notes": "",
                })
            offset = cursor + 1
        else:
            offset += 1

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

    # pass 5
    code_shape_rows, bar = _code_shape_rows(data, seed_rows, in_claimed)
    code_shape_rows = emit("scan_code_shape", code_shape_rows)

    sha_after = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    assert sha_after == sha_before, "ROM changed during the scan"

    summary = {
        "scan_text": len(text_rows), "scan_pointers": len(pointer_rows),
        "scan_pointer_tables": len(table_rows), "scan_entropy": len(entropy_rows),
        "scan_compression": len(compression_rows),
        "scan_code_shape": len(code_shape_rows),
        "abandoned": abandoned, "code_shape_p90_bar": bar,
        "sha_before": sha_before, "sha_after": sha_after,
    }
    if report_path is not None:
        Path(report_path).write_text(json.dumps(summary, indent=1, sort_keys=True),
                                     encoding="utf-8")
    return summary
