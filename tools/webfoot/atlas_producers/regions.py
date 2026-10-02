"""ROM-ATLAS-001 code regions: `code_regions.jsonl`, from upstream evidence only.

**This module replaces the earlier `regen.py`, which was broken.** regen.py read the
existing `code_regions.jsonl` (regen.py:19-21), copied its `jump_table` rows
verbatim (regen.py:104-106) and reused its `code_reached` / `literal_pool`
extents as the wave-2 reach record (regen.py:31-40), then overwrote that same
file (regen.py:121). The artifact therefore depended on a now-lost earlier
version of itself, and its docstring says the method was "reconstructed from the
wave-2 artifact itself".

Nothing here reads a prior `code_regions.jsonl`. Every row is derived from:

* the canonical ROM,
* the wave-2 traversal's per-byte reach record and literal-pool word addresses,
* the wave-4 traversal's same two records,
* jump tables re-derived from ROM bytes by `Traversal.jump_tables`, which is the
  surviving `trace.py:234-258` logic.

The emission (classification names, confidence levels, note strings, the
`(file_offset, size)` sort) is `trace.py:358-432`, which is the form
`atlas_build._code_region_claims` consumes.

regen.py's carve/row shape (regen.py:66-102) is reproduced implicitly: literal
pools are subtracted from the reached bytes before the runs are cut, so a pool
word inside a reached run splits it exactly as regen.py's explicit carve did.
"""

from __future__ import annotations

from pathlib import Path

from ..analysis.thumb import addr_to_offset, offset_to_addr
from ._io import write_jsonl
from .traversal import Traversal, spans_from

#: Minimum size of a hole inside the reached span worth recording (trace.py:419).
MIN_DATA_BETWEEN_CODE = 4


def build(out_dir: Path, wave2: Traversal, wave4: Traversal | None = None) -> Path:
    """Write `code_regions.jsonl` from the traversal records.

    `wave4` is optional so the wave-2 set alone can be rendered; the canonical
    pipeline always passes both, giving the merged 694-function coverage.
    """
    out_dir = Path(out_dir)
    walkers = [w for w in (wave2, wave4) if w is not None]
    size = wave2.size

    pool_offsets: set[int] = set()
    reached: set[int] = set()
    for walker in walkers:
        pool_offsets |= walker.pool_offsets()
        reached |= walker.reached_bytes
    # Literal pool words are DATA, never executable: subtract them from the
    # reached code bytes before the runs are cut.
    reached -= pool_offsets

    code_spans = spans_from(reached)
    pool_spans = spans_from(pool_offsets)

    # Jump tables are re-derived from ROM bytes over the union of the scan
    # windows the two traversals used, never copied from a prior artifact.
    from .code_functions import WAVE2_JUMP_TABLE_SCAN_HI

    scan_hi = min(size, WAVE2_JUMP_TABLE_SCAN_HI)
    if reached:
        scan_hi = max(scan_hi, min(size, (max(reached) + 0x400) | 3))
    tables = wave2.jump_tables(0, scan_hi)

    # The merged function set: wave 2's plus wave 4's delta.
    function_starts = sorted({addr_to_offset(fetch, size)
                              for walker in walkers for fetch in walker.functions})

    rows = []
    for start, end in code_spans:
        count = sum(1 for offset in function_starts if start <= offset < end)
        rows.append({
            "file_offset": start, "size": end - start,
            "gba_address": f"0x{offset_to_addr(start, size):08X}",
            "classification": "code_reached", "confidence": "INFERRED",
            "function_count": count, "coverage_bytes": end - start, "notes": "",
        })
    for start, end in pool_spans:
        rows.append({
            "file_offset": start, "size": end - start,
            "gba_address": f"0x{offset_to_addr(start, size):08X}",
            "classification": "literal_pool", "confidence": "INFERRED",
            "function_count": 0, "coverage_bytes": end - start,
            "notes": "PC-relative literal word(s) resolved during traversal",
        })
    for table in tables:
        rows.append({
            "file_offset": table["file_offset"], "size": table["size"],
            "gba_address": table["gba_address"],
            "classification": "jump_table", "confidence": "INFERRED",
            "function_count": 0, "coverage_bytes": table["size"],
            "notes": f"{table['entries']} consecutive aligned odd in-ROM "
                     "(Thumb) pointers",
        })

    # data_between_code: holes inside the overall reached span. Unreached does
    # NOT mean non-code, which is why the confidence stays CANDIDATE.
    if code_spans:
        span_lo, span_hi = code_spans[0][0], code_spans[-1][1]
        claimed: set[int] = set()
        for start, end in code_spans + pool_spans:
            claimed |= set(range(start, end))
        for table in tables:
            claimed |= set(range(table["file_offset"],
                                 table["file_offset"] + table["size"]))
        gaps: list[tuple[int, int]] = []
        gap_start = None
        for offset in range(span_lo, span_hi):
            if offset in claimed:
                if gap_start is not None:
                    gaps.append((gap_start, offset))
                    gap_start = None
            elif gap_start is None:
                gap_start = offset
        if gap_start is not None:
            gaps.append((gap_start, span_hi))
        for start, end in gaps:
            if end - start < MIN_DATA_BETWEEN_CODE:
                continue
            rows.append({
                "file_offset": start, "size": end - start,
                "gba_address": f"0x{offset_to_addr(start, size):08X}",
                "classification": "data_between_code", "confidence": "CANDIDATE",
                "function_count": 0, "coverage_bytes": 0,
                "notes": "inside the reached code span but never reached by "
                         "traversal; unreached does NOT mean non-code",
            })

    rows.sort(key=lambda row: (row["file_offset"], row["size"]))
    path = out_dir / "code_regions.jsonl"
    write_jsonl(path, rows)
    return path
