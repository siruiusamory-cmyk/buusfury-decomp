"""ROM-ATLAS-001 code cartography: `code_functions.jsonl` and the wave-4 delta.

Ported from scratchpad/trace.py and scratchpad/wave4.py (session
afdddff1-9c87-4859-818c-7a33efc68a28). Read-only against the ROM; the shared
traversal body lives in `traversal.py`.

`build_wave2` is trace.py's seed set and worklist: seed functions from
`seed_knowledge.jsonl`, the two doc-evidenced PC4 entry points, the two dispatch
tables, then jump-table entries found by scanning ROM bytes.

`build_wave4` is wave4.py's delta pass over the 25 dispatch-table seeds. Two
changes from the original: the hardcoded repository root is a parameter, and the
coverage report no longer reads `code_regions.jsonl` for its "before" figures
(wave4.py:396-405). That read made the wave-4 artifact depend on the very file
the broken `regen.py` then overwrote; the "before" baseline is now recomputed
from the wave-2 traversal that is run in the same pipeline, which is the same
evidence without the loop. `code_functions_wave4.jsonl` itself is unaffected —
it never depended on the regions file.

Neither function writes `code_regions.jsonl`. That artifact is `regions.py`'s.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from ..analysis.thumb import addr_to_offset, offset_to_addr
from ..capability import Capability, packaged_contract
from ._io import read_jsonl, write_jsonl
from .traversal import BASE, MAX_DEPTH, MAX_FUNC_SCAN, Traversal

#: The image this pass was measured against. Read from the packaged profile -
#: the one authority for that identity - rather than restated as a literal that
#: could drift from it (CQA-15).
_CANONICAL_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"
EXPECTED_SHA = packaged_contract(
    _CANONICAL_PROFILE_ID, Capability.MAP_ENTRIES
).identity.sha256
#: The ticket's dark code region, in file offsets. Reporting only.
REGION_LO, REGION_HI = 0x0012846, 0x00554C0
#: trace.py scanned this window for jump tables (trace.py:248-249).
WAVE2_JUMP_TABLE_SCAN_HI = 0x60000
#: The GBA header's ARM entry. Recorded, never traversed: thumb.py has no ARM
#: decoder, so an ARM walk would be invention rather than evidence.
ARM_ENTRY = 0x080000C0

#: wave4.py:54-60 — the 25 dispatch-table targets absent from the wave-2 set.
_WAVE4_TABLES = (
    (0x080728AC, (0x080123E8, 0x080123FA, 0x0801240A, 0x0801241C,
                  0x0801242C, 0x0801243A, 0x0801244A, 0x08012464)),
    (0x087B6904, (0x0803E4E4, 0x0803E574, 0x0803E58A, 0x0803E608, 0x0803E6AA,
                  0x0803E738, 0x0803E848, 0x0803E904, 0x0803E9A8, 0x0803EA6C,
                  0x0803EB6C, 0x0803EBC4, 0x0803EC10, 0x0803EC3C, 0x0803EC5A,
                  0x0803ECA6)),
    (0x087B8954, (0x0803F3D8,)),
)


def _load_rom(rom_path: Path) -> bytes:
    data = Path(rom_path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA, "ROM hash mismatch"
    return data


def _row(walker: Traversal, fetch: int, seed_function_addrs: set[int],
         *, wave4: bool) -> dict:
    found = walker.functions[fetch]
    size = found["end"] - fetch if found["end"] is not None else None
    if wave4:
        confidence = "INFERRED"
        notes = (f"extent ends at 0x{found['end']:08X} on {found['end_reason']}"
                 if found["end"] is not None
                 else "size null: no end instruction reached within scan window")
    else:
        confidence = "CONFIRMED" if fetch in seed_function_addrs else "INFERRED"
        notes = ("" if found["end"] is not None
                 else "size null: no end instruction reached within scan window")
    return {
        "file_offset": addr_to_offset(fetch, walker.size),
        "gba_address": found["raw_hex"],
        "fetch_address": f"0x{fetch:08X}",
        "thumb": True,
        "size": size,
        "extent_confidence": "INFERRED" if size is not None else "UNKNOWN",
        "identity": f"func.{fetch:08X}",
        "discovered_via": found["via"],
        "depth": found["depth"],
        "callers": sorted(f"0x{c:08X}" for c in walker.callers.get(fetch, set())),
        "callees": sorted(f"0x{c:08X}" for c in walker.callees.get(fetch, set())),
        "prologue": found["prologue"],
        "confidence": confidence,
        "source": "tools/webfoot/analysis/thumb.py:84",
        "notes": notes,
    }


def build_wave2(rom_path: Path, out_dir: Path) -> tuple[Path, Traversal]:
    """Traverse from the evidenced seeds; write `code_functions.jsonl`.

    Returns the artifact path and the live `Traversal`, whose reached bytes and
    literal pools are the upstream evidence `regions.py` needs.
    """
    out_dir = Path(out_dir)
    data = _load_rom(rom_path)
    walker = Traversal(data)

    seeds: dict[int, tuple[str, str]] = {}

    def add_seed(raw: int, via: str) -> None:
        fetch = raw & ~1
        if not walker.in_rom(fetch) or fetch % 2:
            return
        seeds.setdefault(fetch, (f"0x{raw:08X}", via))

    seed_rows = read_jsonl(out_dir / "seed_knowledge.jsonl")
    seed_function_addrs = set()
    for row in seed_rows:
        if row.get("kind") == "function":
            address = int(row["gba_address"], 16)
            seed_function_addrs.add(address & ~1)
            add_seed(address, f"seed:{row['identity']}")

    # PC4 entry points. BUU_SCRIPT_OWNERSHIP.md:102-112 documents the two
    # item-script call sites 0x0800D742 / 0x0800DDC2 -> 0x0801E164 with table
    # 0x083BD2F8 stride 52. Their containing functions have NO BL caller and NO
    # stored Thumb pointer anywhere in the ROM, so no traversal from any other
    # seed can reach them; they are evidenced entry points in their own right.
    for function, site in ((0x0800D72E, 0x0800D742), (0x0800DD90, 0x0800DDC2)):
        add_seed(function, "doc_evidenced:BUU_SCRIPT_OWNERSHIP.md:102 "
                           f"item_script_consumer@0x{site:08X}")

    # Dispatch tables. Primary 0x080554C0 (31 slots, measured in
    # BUU_SCRIPT_VM.md). Native table 0x08055098 (283 slots).
    for table_address, count in ((0x080554C0, 31), (0x08055098, 283)):
        for index in range(count):
            word = walker.u32(table_address + 4 * index)
            if word == 0:
                continue
            if walker.in_rom(word) and (word & 1):
                add_seed(word, f"dispatch_table:0x{table_address:08X}[{index}]")

    for fetch, (raw_hex, via) in sorted(seeds.items()):
        walker.seed(fetch, 0, raw_hex, via)
    walker.drain()

    # Jump tables: derived from ROM bytes, then every entry seeded.
    for table in walker.jump_tables(0, min(walker.size, WAVE2_JUMP_TABLE_SCAN_HI)):
        address = int(table["gba_address"], 16)
        for index in range(table["entries"]):
            word = walker.u32(address + 4 * index)
            target = word & ~1
            if target in walker.functions:
                continue
            walker.seed(target, 1, f"0x{word:08X}",
                        f"jump_table:0x{address:08X}[{index}]")
    walker.drain()

    rows = [_row(walker, fetch, seed_function_addrs, wave4=False)
            for fetch in sorted(walker.functions)]
    path = out_dir / "code_functions.jsonl"
    write_jsonl(path, rows)
    return path, walker


def build_wave4(rom_path: Path, out_dir: Path,
                wave2: Traversal) -> tuple[Path, Traversal]:
    """Re-run the traversal from the 25 dispatch-table seeds; write the delta.

    Only functions absent from the wave-2 set are emitted; edges are still
    followed THROUGH known functions. `wave2` supplies the "before" coverage
    baseline that the original read out of `code_regions.jsonl`.
    """
    out_dir = Path(out_dir)
    data = _load_rom(rom_path)
    walker = Traversal(data)
    existing_fetch = set(wave2.functions)

    seeds: dict[int, tuple[str, str]] = {}
    provenance: dict[int, str] = {}

    def slot_of(table_base: int, target_fetch: int) -> int | None:
        """Locate the concrete slot by reading the table words, not by guessing."""
        for index in range(64):
            address = table_base + 4 * index
            if address + 4 > walker.code_hi:
                break
            value = walker.u32(address)
            if not (walker.in_rom(value) and (value & 1)):
                break
            if (value & ~1) == target_fetch:
                return index
        return None

    for table, targets in _WAVE4_TABLES:
        for target in targets:
            index = slot_of(table, target)
            via = (f"dispatch_table:0x{table:08X}[{index}]" if index is not None
                   else f"dispatch_table:0x{table:08X}[?]")
            provenance[target] = via
            raw = target | 1  # the raw pointer as stored in the table (odd)
            fetch = raw & ~1
            if walker.in_rom(fetch) and not fetch % 2:
                seeds.setdefault(fetch, (f"0x{raw:08X}", via))

    assert len(seeds) == 25, len(seeds)
    for fetch, (raw_hex, via) in sorted(seeds.items()):
        walker.seed(fetch, 0, raw_hex, via)
    walker.drain()

    # Jump tables found in-flight: a run of >= 8 aligned odd in-ROM words
    # intersecting the span this pass actually reached. Every entry is seeded.
    reached = set(walker.reached_bytes)
    scan_lo = max(0, (min(reached) - 0x400) & ~3) if reached else 0
    scan_hi = min(walker.size, (max(reached) + 0x400) | 3) if reached else 0
    tables = walker.jump_tables(scan_lo, scan_hi)
    for table in tables:
        address = int(table["gba_address"], 16)
        for index in range(table["entries"]):
            word = walker.u32(address + 4 * index)
            target = word & ~1
            if target in walker.functions:
                continue
            walker.seed(target, 1, f"0x{word:08X}",
                        f"jump_table:0x{address:08X}[{index}]")
    walker.drain()

    rows = [_row(walker, fetch, set(), wave4=True)
            for fetch in sorted(walker.functions) if fetch not in existing_fetch]
    rows.sort(key=lambda row: row["file_offset"])
    path = out_dir / "code_functions_wave4.jsonl"
    write_jsonl(path, rows)
    return path, walker


def write_coverage(out_dir: Path, rom_path: Path, wave2: Traversal,
                   wave4: Traversal) -> Path:
    """Write `code_coverage_wave4.json`: what the wave-4 pass added.

    The "before" figures come from the wave-2 traversal directly (wave4.py read
    them out of `code_regions.jsonl`, which is the dependency this chain breaks).
    """
    import json

    rom_path, out_dir = Path(rom_path), Path(out_dir)
    size = wave2.size
    before_code = set(wave2.reached_bytes) - wave2.pool_offsets()
    before_pool = wave2.pool_offsets()
    new_code = set(wave4.reached_bytes) - wave4.pool_offsets()
    new_pool = wave4.pool_offsets()
    merged_code = before_code | new_code
    merged_pool = (before_pool | new_pool) - merged_code

    region_total = REGION_HI - REGION_LO

    def in_region(offsets: set[int]) -> int:
        return sum(1 for offset in offsets if REGION_LO <= offset < REGION_HI)

    claimed = merged_code | merged_pool
    holes: list[tuple[int, int]] = []
    start = None
    for offset in range(REGION_LO, REGION_HI):
        if offset in claimed:
            if start is not None:
                holes.append((start, offset))
                start = None
        elif start is None:
            start = offset
    if start is not None:
        holes.append((start, REGION_HI))
    holes.sort(key=lambda hole: -(hole[1] - hole[0]))

    wave4_rows = [_row(wave4, fetch, set(), wave4=True)
                  for fetch in sorted(wave4.functions)
                  if fetch not in wave2.functions]
    sha = hashlib.sha256(rom_path.read_bytes()).hexdigest()
    before_region = in_region(before_code)
    merged_region = in_region(merged_code)

    coverage = {
        "rom": {"path_basename": rom_path.name, "size": size,
                "sha256_before": sha, "sha256_after": sha,
                "profile": "buus_fury_usa_rev0_01c1707f"},
        "method": {
            "traversal": "recursive Thumb worklist over BL / short-branch / "
                         "PC-relative-literal edges, depth cap "
                         f"{MAX_DEPTH}, per-function scan cap 0x{MAX_FUNC_SCAN:X}; "
                         "decoders are tools/webfoot/analysis/thumb.py only",
            "seed_source": "the 25 dispatch-table target addresses that appear in "
                           "no row of code_functions.jsonl",
            "delta_rule": "a function is emitted only if its fetch address is absent "
                          "from the wave-2 rows; edges are still followed THROUGH "
                          "known functions",
            "linear_sweep": "not used; forbidden by contract",
            "baseline_source": "the wave-2 traversal run in the same pipeline, not a "
                               "prior code_regions.jsonl",
            "arm_blocker": "tools/webfoot/analysis/thumb.py is Thumb-only; the GBA ARM "
                           f"entry 0x{ARM_ENTRY:08X} remains untraversable",
        },
        "seeds": {"supplied": 25,
                  "by_table": {f"0x{table:08X}": len(targets)
                               for table, targets in _WAVE4_TABLES}},
        "new_functions": {
            "count": len(wave4_rows),
            "by_depth": dict(sorted(Counter(r["depth"] for r in wave4_rows).items())),
            "by_mechanism": dict(Counter(r["discovered_via"].split(":")[0]
                                         for r in wave4_rows)),
            "with_justified_extent": sum(1 for r in wave4_rows if r["size"] is not None),
            "size_null": sum(1 for r in wave4_rows if r["size"] is None),
            "max_depth_reached": max((r["depth"] for r in wave4_rows), default=None),
            "bytes_in_justified_extents": sum(r["size"] for r in wave4_rows if r["size"]),
        },
        "code_region_0x0012846_0x00554C0": {
            "file_offset_lo": REGION_LO, "file_offset_hi": REGION_HI,
            "gba_lo": f"0x{offset_to_addr(REGION_LO, size):08X}",
            "gba_hi": f"0x{offset_to_addr(REGION_HI, size):08X}",
            "total_bytes": region_total,
            "before": {"code_reached_bytes": before_region,
                       "code_reached_percent": round(100 * before_region / region_total, 2),
                       "literal_pool_bytes": in_region(before_pool)},
            "after_merge": {"code_reached_bytes": merged_region,
                            "code_reached_percent": round(100 * merged_region / region_total, 2),
                            "literal_pool_bytes": in_region(merged_pool)},
            "new_code_bytes_attributable_to_this_pass": in_region(new_code - before_code),
            "largest_remaining_holes": [
                {"file_offset_lo": lo, "file_offset_hi": hi, "bytes": hi - lo,
                 "gba_lo": f"0x{offset_to_addr(lo, size):08X}"}
                for lo, hi in holes[:10]],
        },
        "whole_image": {
            "rom_bytes": size,
            "before": {"code_reached_bytes": len(before_code),
                       "literal_pool_bytes": len(before_pool),
                       "percent_of_image": round(100 * len(before_code) / size, 4)},
            "after_merge": {"code_reached_bytes": len(merged_code),
                            "literal_pool_bytes": len(merged_pool),
                            "percent_of_image": round(100 * len(merged_code) / size, 4)},
            "new_code_bytes_attributable_to_this_pass": len(new_code - before_code),
        },
        "structure": {
            "literal_pool_words_resolved_this_pass": len(wave4.all_pools),
            "literal_pool_bytes_this_pass": len(new_pool),
            "caveat": "PC-relative literal words resolving inside a code region are "
                      "recorded as literal_pool (DATA), never as executable.",
        },
    }
    path = out_dir / "code_coverage_wave4.json"
    with path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(coverage, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
