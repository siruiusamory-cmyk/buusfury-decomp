
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
from ..binary import GBA_ROM_BASE as BASE
from ..analysis import thumb
from ..formats import webfoot_lz as lz
from ..formats.text_tables import CONTROL_NEWLINE, CONTROL_PREFIX
from ._io import read_jsonl, write_jsonl

IMAGE_SIZE = 8388608
PRINT_MIN, PRINT_MAX = 0x20, 0x7E

# TEXT_LATIN1 is a measured three-value allowlist, not a rule about high-byte-zero units: 0x0002, 0x0007, 0x0008, 0x000A and 0x000B also have a zero high byte and remain control units.
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
    if data[offset + 1] != 0:
        return False
    low = data[offset]
    return PRINT_MIN <= low <= PRINT_MAX or low in TEXT_LATIN1


def _prose(text: str) -> bool:
    return bool(_WORD.search(text)) and bool(_VOWEL.search(text)) and " " in text


def _claimed_lookup(seed_rows: list[dict]):
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




# MEASURED: the terminator-free rule yields 681 runs totalling 195,342 characters, and the seven containers hold 196,386 halfwords of which 1,023 are control units (0x0008 328, 0x000B 266, 0x0007 164, 0x0002 164, 0x000A 101).
def scan_runs(data: bytes, *, require_terminator: bool = True):
    """The one run-extraction implementation, shared by the raw-ROM pass (NUL-terminated runs) and the decoded-container pass (terminator-free streams), so the two surfaces cannot drift apart on what counts as a run."""
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
        except Exception as error:
            abandoned += 1
            row["notes"] = f"ABANDONED {type(error).__name__}"
        rows.append(row)
    return rows, abandoned



# The pointer table that defines the compressed-text region: seven consecutive words, each a ROM address of one container.
COMPRESSED_TEXT_TABLE = 0x007B5B64
COMPRESSED_TEXT_COUNT = 7


# The reachability gate is a safety property and not a tuning parameter: the blind compression probe strides 4 bytes and 24,285 of its hits decode and round-trip.
# A record NEVER carries a ROM offset for the text: only the container has a real ROM address, so the two are never summed.
def _decoded_text_rows(data: bytes) -> list[dict]:
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




# The bar is the image's own 90th percentile, and it is PRIORITIZATION only: a high score is never evidence that a block IS code.
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




# Both entropy grids go into one file, because the assembler keeps only the 4 KiB rows for coverage and reads every row as an observation.
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

    text_rows = emit("scan_text", _text_rows(data, in_claimed))

    words = struct.unpack_from(f"<{IMAGE_SIZE // 4}I", data, 0)
    pointer_rows = emit("scan_pointers", _pointer_rows(words, in_claimed))
    table_rows = emit("scan_pointer_tables", _pointer_table_rows(words, in_claimed))

    entropy_rows = emit("scan_entropy",
                        _entropy_rows(data, 4096, in_claimed)
                        + _entropy_rows(data, 1024, in_claimed))

    compression_rows, abandoned = _compression_rows(data, in_claimed)
    compression_rows = emit("scan_compression", compression_rows)

    decoded_text_rows = sorted(
        _decoded_text_rows(data),
        key=lambda row: (row["container_file_offset"], row["decoded_offset"] or 0))
    write_jsonl(out_dir / "scan_decoded_text.jsonl", decoded_text_rows)

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
