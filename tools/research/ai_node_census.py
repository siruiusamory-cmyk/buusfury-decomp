"""Census and decoder for the enemy behaviour behaviour language, over an image supplied by the caller.

The language was recovered by walking the row table and reading each node's four fields. This tool makes that
walk repeatable and separates the parts that need an image from the parts that do not: every function here
takes bytes, so a test can drive them with a synthetic image and no ROM.

Measured constants (see docs/research/ENEMY_AI_NODE_LANGUAGE.md):

* a ROW is `{+0x00 primary node, +0x04 secondary node}`, 8 bytes, at `0x0870F514 + 8*selector`.
* a NODE is `+0x00` handler (odd Thumb pointer, called with `(node, actor)`), `+0x04` evaluator, `+0x08`
  release, `+0x0C` param. Conditional leaves come in two forms: SCALAR keeps the child node pointer at `+0x10`
  and a scalar param at `+0x0C`, while POINTER keeps the CHILD POINTER IN THE PARAM SLOT `+0x0C`.
* the form is a property of the HANDLER, so it is tabulated from measurement rather than guessed.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROM_BASE = 0x08000000
ROW_TABLE = 0x0870F514
ROW_COUNT = 828
ROW_BYTES = 8
NODE_FIELDS = 4
POINTER_SLOT = 0x0C
CHILD_SLOT = 0x10

#: Composite handlers whose param is a CHILD COUNT and whose children are node pointers at `+0x10+4i`
#: (OR and AND through the child-setup helper `0x080190AA`, SEQ by inlining the same loop).
COMPOSITE_HANDLERS = frozenset({0x0801920E, 0x080191C6, 0x080191E8, 0x08018F90})

#: Handlers whose conditional leaf keeps its CHILD NODE POINTER in the param slot instead of at `+0x10`.
POINTER_FORM_HANDLERS = frozenset({
    0x08029FE6, 0x08029BB6, 0x0802AAD0, 0x0803D478, 0x08030156, 0x0802692C, 0x0802B5B0, 0x08033F04,
    0x08039102, 0x08035EE2, 0x08036302, 0x08036328, 0x0803634E, 0x08037A04, 0x08037B96, 0x080327FE,
    0x0802F976, 0x0803AE64, 0x0803AE82, 0x0803CE70, 0x0803B2BA, 0x080332E0, 0x08036F44, 0x080345FC,
})

#: Handlers whose states carry the shared latched condition class, with the class each one allocates.
CONDITION_HANDLERS = {
    0x080188A8: ("scalar", 0x080499E4, "rand16() < param (unsigned)"),
    0x08029660: ("scalar", 0x0804A6E8, "squared centre distance actor<->player > param (signed)"),
    0x08029C64: ("scalar", 0x08049C28, "squared centre distance <= param"),
    0x08029D14: ("scalar", 0x08049C40, "squared centre distance <= param (twin)"),
    0x08029FE6: ("pointer", 0x08049DF0, "[player] != 0 and [player+0x1CC] != 0"),
    0x08039854: ("scalar", 0x08049DD8, "[0x03000F94] - [actor+0x210] > param"),
    0x0802AA3C: ("scalar", 0x0804A668, "[0x03000F94] - [actor+0x1E8] > param"),
    0x08029E7C: ("scalar", 0x0804CBB0, "[actor+0x1E4] == param (gate counter)"),
    0x08029B30: ("pointer", 0x0804B6B8, "u8(actor+0x10) == (u8(player+0x10) ^ 1) (facing)"),
    0x080299DC: ("scalar", 0x0804AABC, "own HP below ((class+0x80(actor) * param) >> 16) << 10"),
    0x0802AA80: ("scalar", 0x0804AA5C, "[0x03000F94] - [actor+0x1EC] > param"),
    0x0803923A: ("scalar", 0x0804AAA4, "counts a chain at [actor+0x1F0] and compares with param"),
}

#: Composite and leaf handlers whose semantics are established, with their param meaning.
LEAF_HANDLERS = {
    0x0801890A: "SET: param is a ROW index, switches the behaviour system to that row",
    0x08019284: "AUX: param is a ROW index; activates the row PRIMARY and evaluates its SECONDARY",
    0x0801920E: "OR: param is the child count, children at +0x10+4i, first true child wins (priority order)",
    0x080191C6: "AND: param is the child count; ORs on the state path and ANDs on the node path",
    0x08018F90: "SEQ: param is the child count, children at +0xC+4i, position at +4, count at +8",
    0x080188A8: "RAND: param is a 16-bit threshold",
    0x08029FE6: "SPAWN: param is a node pointer, requires the player to be acting",
    0x0802968C: "POSE: param reaches class 0x0804BDD0 and is parked at actor+0x1E4",
    0x08018C08: "WAIT: param is a frame count",
    0x080369FA: "APPROACH: 8-byte leaf {class 0x0804AD38, param}; param flows into the walk helper",
    0x0800A9B0: "stub leaf",
}


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def is_code_pointer(value: int, image: bytes) -> bool:
    """A stored CODE pointer is an odd Thumb address inside the image (handler, evaluator, release)."""
    return bool(value & 1) and ROM_BASE <= (value & ~1) < ROM_BASE + len(image)


def is_node_pointer(value: int, image: bytes) -> bool:
    """A NODE pointer is a data address, so it is normally EVEN: row words and child slots are these.

    This is the distinction a first version of this tool got wrong - a row's `+0x00` holds the address of a
    NODE STRUCTURE, not of code, so requiring the Thumb bit there found no rows at all.
    """
    return value != 0 and ROM_BASE <= value < ROM_BASE + len(image)


def row_address(selector: int) -> int:
    return ROW_TABLE + ROW_BYTES * selector


def row(image: bytes, selector: int) -> dict:
    if not 0 <= selector < ROW_COUNT:
        raise ValueError(f"selector {selector} is outside the row table")
    base = row_address(selector) - ROM_BASE
    return {"selector": selector, "primary": word(image, base), "secondary": word(image, base + 4)}


def node_form(handler: int) -> str:
    if handler in POINTER_FORM_HANDLERS:
        return "pointer"
    if handler in CONDITION_HANDLERS:
        return CONDITION_HANDLERS[handler][0]
    if handler in LEAF_HANDLERS:
        return "leaf"
    return "unknown"


def node(image: bytes, address: int) -> dict:
    """Read one node. The child slot reported is the one the handler's form actually uses."""
    base = (address & ~1) - ROM_BASE
    handler = word(image, base)
    form = node_form(handler & ~1) if is_code_pointer(handler, image) else "null-handler"
    param_offset = POINTER_SLOT if form == "pointer" else 0x0C
    child_offset = POINTER_SLOT if form == "pointer" else CHILD_SLOT
    return {
        "address": address & ~1,
        "handler": handler,
        "evaluate": word(image, base + 4),
        "release": word(image, base + 8),
        "param": word(image, base + param_offset),
        "child_slot": child_offset,
        "child": word(image, base + child_offset),
        "form": form,
        "handler_meaning": LEAF_HANDLERS.get(handler & ~1),
        "condition": CONDITION_HANDLERS.get(handler & ~1, (None, None, None))[2] if form != "leaf" else None,
    }


def walk_row(image: bytes, selector: int, limit: int = 4096) -> list[dict]:
    """Every node reachable from one row, following the child slot each handler's form uses."""
    seen: set[int] = set()
    found: list[dict] = []
    entry = row(image, selector)
    pending = [entry[name] for name in ("primary", "secondary") if is_node_pointer(entry[name], image)]
    while pending:
        address = pending.pop()
        if address in seen or len(found) >= limit:
            continue
        seen.add(address)
        entry = node(image, address)
        found.append(entry)
        handler = entry["handler"] & ~1
        if handler in COMPOSITE_HANDLERS:
            # A composite's param is its child count and its children are 4-byte pointers at +0x10+4i.
            count = min(entry["param"], 64)
            base = (address & ~1) - ROM_BASE + CHILD_SLOT
            for index in range(count):
                child = word(image, base + 4 * index)
                if is_node_pointer(child, image):
                    pending.append(child)
            continue
        child = entry["child"]
        if is_node_pointer(child, image):
            pending.append(child)
    return found


def census(image: bytes, limit: int = 4096) -> dict:
    """Walk every row and report the shape of the language: nodes, handlers, forms, conditions."""
    handlers: dict[int, int] = {}
    forms: dict[str, int] = {}
    conditions: dict[str, int] = {}
    meanings: dict[int, int] = {}
    nodes = 0
    null_handlers = 0
    for selector in range(ROW_COUNT):
        for entry in walk_row(image, selector, limit):
            nodes += 1
            handler = entry["handler"] & ~1
            if entry["form"] == "null-handler":
                null_handlers += 1
                continue
            handlers[handler] = handlers.get(handler, 0) + 1
            forms[entry["form"]] = forms.get(entry["form"], 0) + 1
            if entry["condition"]:
                conditions[entry["condition"]] = conditions.get(entry["condition"], 0) + 1
            if entry["handler_meaning"]:
                meanings[handler] = meanings.get(handler, 0) + 1
    return {
        "rows": ROW_COUNT,
        "nodes_reached": nodes,
        "distinct_handlers": len(handlers),
        "null_handler_nodes": null_handlers,
        "forms": forms,
        "conditions": conditions,
        "named_leaf_placements": meanings,
        "top_handlers": sorted(handlers.items(), key=lambda item: -item[1])[:15],
    }


def secondary_handler_census(image: bytes) -> dict:
    """A row's +0x04 word is the node the per-frame NODE path evaluates.

    A LITERAL ZERO secondary word (12 rows in retail) is reported on its own key, because it means the row
    has no secondary tree at all, which is not the same as a secondary whose handler word happens to be zero.
    """
    counts: dict = {}
    for selector in range(ROW_COUNT):
        secondary = row(image, selector)["secondary"]
        if secondary == 0:
            counts[-1] = counts.get(-1, 0) + 1
            continue
        if not is_node_pointer(secondary, image):
            counts[-2] = counts.get(-2, 0) + 1
            continue
        handler = word(image, (secondary & ~1) - ROM_BASE) & ~1
        counts[handler] = counts.get(handler, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: -item[1]))


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Census the enemy behaviour node language, read-only")
    parser.add_argument("--image", required=True, help="a GBA image to read")
    parser.add_argument("--row", type=int, default=None, help="print one row's node tree")
    parser.add_argument("--secondaries", action="store_true", help="census the secondary node handlers")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    image = Path(args.image).read_bytes()
    if args.row is not None:
        for entry in walk_row(image, args.row):
            print(f"  0x{entry['address']:08X} {entry['form']:>13} handler 0x{entry['handler']:08X} "
                  f"param 0x{entry['param']:08X} child 0x{entry['child']:08X} "
                  f"{entry['handler_meaning'] or entry['condition'] or ''}")
        return 0
    if args.secondaries:
        for handler, count in secondary_handler_census(image).items():
            label = { -1: "LITERAL ZERO secondary word", -2: "not a code pointer" }.get(handler)
            label = label or LEAF_HANDLERS.get(handler, "unreadable")
            print(f"  {count:>4} row(s)  secondary handler 0x{handler:08X}  {label}")
        return 0

    report = census(image)
    print(json.dumps(report, indent=2) if args.json else
          "\n".join(f"{key}: {value}" for key, value in report.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
