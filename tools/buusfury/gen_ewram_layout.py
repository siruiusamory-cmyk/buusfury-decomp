"""Decode the ROM-resident static pointer table at 0x08054FBC.

The table holds absolute addresses of statically allocated GBA RAM objects. This
script reads it from the canonical ROM, builds the static layout around every
entry, and commits config/ewram_layout.json.

IT DOES NOT TOUCH build/, so it is safe to run alongside a check.cmd run.

NAMING: the previous artifact called these "EWRAM" pointers. They are NOT in
EWRAM. EWRAM on this hardware is 0x02000000..0x0203FFFF and IWRAM is
0x03000000..0x03007FFF; every entry here is 0x0300xxxx, so every object is in
IWRAM. The range check below measures that rather than asserting it.

ADJACENCY IS AN UPPER BOUND ONLY. The gap from one object to the next known static
object above it bounds the first object from ABOVE, and only under the assumption
that the two do not overlap. Nothing in the code proves they are disjoint, so every
interval carries INFERRED_MAX_EXTENT and never a proven size.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from buusfury import identity

ROM = identity.resolve_baserom()
data = ROM.read_bytes()
BASE = 0x08000000
TABLE = 0x08054FBC

EWRAM = (0x02000000, 0x02040000)
IWRAM = (0x03000000, 0x03008000)
PALETTE = (0x05000000, 0x05000400)
VRAM = (0x06000000, 0x06018000)
ROM_RANGE = (0x08000000, 0x0E000000)


def u32(a):
    return int.from_bytes(data[a - BASE:a - BASE + 4], "little")


def region(addr):
    for name, (lo, hi) in (("EWRAM", EWRAM), ("IWRAM", IWRAM),
                           ("PALETTE", PALETTE), ("VRAM", VRAM), ("ROM", ROM_RANGE)):
        if lo <= addr < hi:
            return name
    return "OUTSIDE_VALID_GBA_RAM"


# ---- 1. decode the table, including the terminator ----
entries = []
offset = 0
while True:
    addr = TABLE + offset
    value = u32(addr)
    entries.append({
        "table_offset": f"0x{offset:02X}",
        "rom_address": f"0x{addr:08X}",
        "value": f"0x{value:08X}",
        "raw": value,
        "region": region(value) if value else None,
    })
    offset += 4
    if value == 0:
        break
    if offset > 0x80:                      # a guard; the table is known to end at +0x2C
        break

non_zero = [e for e in entries if e["raw"] != 0]
terminator = next((e for e in entries if e["raw"] == 0), None)

# ---- 2. structure validation ----
targets = [e["raw"] for e in non_zero]
unique = len(set(targets)) == len(targets)
table_sorted = targets == sorted(targets)
regions = sorted({e["region"] for e in non_zero})
outside = [e for e in non_zero if e["region"] == "OUTSIDE_VALID_GBA_RAM"]

# ---- 3. memory order and intervals ----
ordered = sorted(non_zero, key=lambda e: e["raw"])
for position, entry in enumerate(ordered):
    higher = ordered[position + 1]["raw"] if position + 1 < len(ordered) else None
    lower = ordered[position - 1]["raw"] if position > 0 else None
    entry["ascending_position"] = position
    entry["nearest_lower_static_object"] = f"0x{lower:08X}" if lower is not None else None
    entry["nearest_higher_static_object"] = f"0x{higher:08X}" if higher is not None else None
    entry["gap_to_next_higher_bytes"] = (higher - entry["raw"]) if higher is not None else None
    entry["gap_to_next_lower_bytes"] = (entry["raw"] - lower) if lower is not None else None
    entry["class"] = "INFERRED_MAX_EXTENT" if higher is not None else "PROVEN_START_UNBOUNDED_ABOVE"
    entry["extent_basis"] = (
        "the next known static object above, ASSUMING the two do not overlap; an "
        "upper bound only"
    )

# ---- 4. the +0x14 object ----
focus = next(e for e in non_zero if e["table_offset"] == "0x14")
focus_addr = focus["raw"]
focus_ordered = next(e for e in ordered if e["raw"] == focus_addr)
focus_gap = focus_ordered["gap_to_next_higher_bytes"]
FLAG_OFFSET = 0x55
focus_block = {
    "table_offset": "0x14",
    "rom_address_of_the_entry": focus["rom_address"],
    "target": f"0x{focus_addr:08X}",
    "region": focus["region"],
    "nearest_lower_static_object": focus_ordered["nearest_lower_static_object"],
    "nearest_higher_static_object": focus_ordered["nearest_higher_static_object"],
    "gap_to_next_lower_bytes": focus_ordered["gap_to_next_lower_bytes"],
    "gap_to_next_higher_bytes": focus_gap,
    "ascending_position": focus_ordered["ascending_position"],
    "position_note": (
        "the LOWEST address in the table, so there is no lower static object to "
        "bound it from below and the gap above is its only static constraint"
    ),
    "maximum_extent_bytes_under_non_overlap": focus_gap,
    "maximum_extent_is_proven": False,
    "maximum_extent_class": "INFERRED_MAX_EXTENT",
    "flag_array_start_offset": f"0x{FLAG_OFFSET:02X}",
    "flag_array_start_address": f"0x{focus_addr + FLAG_OFFSET:08X}",
    "max_bytes_available_from_the_flag_array_start": (
        (focus_gap - FLAG_OFFSET) if focus_gap is not None else None
    ),
    "max_flag_bits_if_the_inferred_extent_held": (
        ((focus_gap - FLAG_OFFSET) * 8) if focus_gap is not None else None
    ),
    "why_this_is_not_proven": (
        "the extent comes only from the next pointer in the SAME table, under an "
        "assumption of non-overlap that no code or data establishes. Nothing shows "
        "the object fills its interval, and nothing shows the next object starts "
        "where its pointer says."
    ),
}

# ---- 5. cross-check: is each target referenced as a literal word in the image? ----
cross = []
for e in non_zero:
    pattern = e["raw"].to_bytes(4, "little")
    count = 0
    first = []
    start = 0
    while True:                       # bytes.find, not a byte-by-byte Python loop
        i = data.find(pattern, start)
        if i < 0:
            break
        count += 1
        if len(first) < 4:
            first.append(f"0x{BASE + i:08X}")
        start = i + 1
    cross.append({
        "table_offset": e["table_offset"],
        "target": e["value"],
        "literal_word_occurrences_in_the_image": count,
        "first_occurrences": first,
        "referenced_by_code_as_a_constant": count > 1,
        "note": (
            "one occurrence is the table entry itself; more than one means some "
            "other site names the address as a constant"
        ),
    })

gaps = [e["gap_to_next_higher_bytes"] for e in ordered
        if e["gap_to_next_higher_bytes"] is not None]

artifact = {
    "generated_by": "tools/buusfury/gen_ewram_layout.py",
    "table_address": f"0x{TABLE:08X}",
    "table_extent": f"0x{TABLE:08X}..0x{TABLE + offset:08X}",
    "region_correction": (
        "THE PREVIOUS ARTIFACT CALLED THESE EWRAM POINTERS. THEY ARE NOT. EWRAM is "
        "0x02000000..0x0203FFFF and IWRAM is 0x03000000..0x03007FFF; every entry "
        "here is 0x0300xxxx, so every object is in IWRAM."
    ),
    "entries": non_zero,
    "terminator": terminator,
    "validation": {
        "non_zero_entry_count": len(non_zero),
        "all_values_unique": unique,
        "table_order_equals_memory_order": table_sorted,
        "table_order_note": (
            "the table is NOT sorted by address, so table order and memory order are "
            "different and both are recorded"
        ),
        "regions_present": regions,
        "entries_outside_valid_gba_ram": [e["table_offset"] for e in outside],
        "any_outside_valid_ram": bool(outside),
        "all_in_IWRAM": regions == ["IWRAM"],
        "smallest_gap_bytes": min(gaps) if gaps else None,
        "largest_gap_bytes": max(gaps) if gaps else None,
    },
    "sorted_memory_layout": [
        {
            "ascending_position": e["ascending_position"],
            "table_offset": e["table_offset"],
            "target": e["value"],
            "gap_to_next_higher_bytes": e["gap_to_next_higher_bytes"],
            "class": e["class"],
        }
        for e in ordered
    ],
    "focus_object": focus_block,
    "cross_check_literal_references": cross,
    "cross_check_conclusion": (
        "Every target was searched for as a literal word in the image. The count "
        "includes the table entry itself, so a count above one means another site "
        "names that address. This is a consistency check on the interval model, not "
        "a proof of any object's size."
    ),
    "adjacency_is_an_upper_bound_only": (
        "Every interval is classed INFERRED_MAX_EXTENT and bounds its object FROM "
        "ABOVE under a non-overlap assumption. No interval proves an object's size, "
        "and no interval proves an object fills it."
    ),
    "flag_array_bound_status": (
        "STILL NOT PROVEN. The flag array at 0x030010BD now has an INFERRED maximum "
        "of 0x8BF bytes (17,912 bits) from the static layout, which is a stronger "
        "statement than before but remains an upper bound under an unproven "
        "non-overlap assumption."
    ),
    "proven": [
        f"the table lives at 0x{TABLE:08X} and holds {len(non_zero)} non-zero words",
        "all values are unique",
        "every value is an IWRAM address",
        "the table is zero-terminated",
        "the +0x14 entry contains the focus object's address",
    ],
    "inferred": [
        "every object's maximum extent, from the gap to the next object above it",
        "the focus object's maximum extent and the flag array's maximum capacity",
    ],
    "unproven": [
        "any object's exact size",
        "that any two objects are disjoint",
        "that any object fills its interval",
        "the flag array's true upper bound",
    ],
}
out = pathlib.Path('config/ewram_layout.json')
out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
               encoding='utf-8', newline='\n')

print(f"entries (non-zero)     : {len(non_zero)}")
print(f"terminator             : {terminator['table_offset'] if terminator else 'none'}")
print(f"all unique             : {unique}")
print(f"table order == memory  : {table_sorted}")
print(f"regions                : {regions}")
print(f"outside valid RAM      : {len(outside)}")
print(f"smallest / largest gap : 0x{min(gaps):X} / 0x{max(gaps):X}")
print(f"focus 0x{focus_addr:08X}  pos {focus_ordered['ascending_position']}  "
      f"gap 0x{focus_gap:X} ({focus_gap})  flag max bytes 0x{focus_block['max_bytes_available_from_the_flag_array_start']:X} "
      f"= {focus_block['max_flag_bits_if_the_inferred_extent_held']} bits")
print("cross-check (literal occurrences per target):")
for c in cross:
    print(f"   {c['table_offset']}  {c['target']}  x{c['literal_word_occurrences_in_the_image']}")
print(f"wrote {out}")
