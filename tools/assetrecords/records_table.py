from __future__ import annotations

import argparse
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LAYOUT = os.path.join(HERE, "records_layout.json")
ROM_BASE = 0x08000000
SIZES = {"u16": 2, "u32": 4}


def load_layout(path=None):
    path = path or LAYOUT
    with open(path, encoding="ascii") as handle:
        layout = json.load(handle)
    layout["layout"] = os.path.basename(path)
    layout["base"] = int(layout["base"], 16)
    layout["count"] = int(layout["count"])
    layout["stride"] = int(layout["stride"])
    for field in layout["fields"]:
        block = field.get("pointer")
        if block:
            block["base"] = int(block["base"], 16)
            block["limit"] = int(block["limit"], 16)
    return layout


def size_of(layout):
    return sum(SIZES[field["type"]] for field in layout["fields"])


def parse(rom, layout, count=None, stride=None):
    if stride is not None and stride != layout["stride"]:
        raise ValueError("the stride %d is not the directory's %d" % (stride, layout["stride"]))
    if count is not None and count != layout["count"]:
        raise ValueError("the record count %d is not the directory's %d"
                         % (count, layout["count"]))
    if size_of(layout) != layout["stride"]:
        raise ValueError("the fields cover %d bytes, the stride is %d"
                         % (size_of(layout), layout["stride"]))
    offset = layout["base"] - ROM_BASE
    size = layout["count"] * layout["stride"]
    if offset < 0 or offset + size > len(rom):
        raise ValueError("the record table %#x..%#x is outside the image"
                         % (layout["base"], layout["base"] + size))
    records = []
    for index in range(layout["count"]):
        record = {}
        cursor = offset + index * layout["stride"]
        for field in layout["fields"]:
            fmt = "<H" if field["type"] == "u16" else "<I"
            value = struct.unpack_from(fmt, rom, cursor + field["offset"])[0]
            if "domain" in field and value not in field["domain"]:
                raise ValueError("record %d %s is %#x, not one of %s"
                                 % (index, field["name"], value,
                                    ", ".join("%#x" % one for one in field["domain"])))
            block = field.get("pointer")
            if block:
                inside = block["base"] <= value < block["limit"]
                if not inside and not (field.get("null") and value == 0):
                    raise ValueError("record %d %s is %#010x, outside %#010x..%#010x"
                                     % (index, field["name"], value, block["base"],
                                        block["limit"]))
            record[field["name"]] = value
        records.append(record)
    return records


def blob(records, layout):
    out = bytearray()
    for record in records:
        for field in layout["fields"]:
            fmt = "<H" if field["type"] == "u16" else "<I"
            out += struct.pack(fmt, record[field["name"]])
    return bytes(out)


def source(records, layout):
    lines = ["; %s: %d x %d B at %#010x, generated from the user's own image"
             % (layout.get("title", "record table"), layout["count"], layout["stride"],
                layout["base"]),
             "; layout: tools/assetrecords/%s (field names and types; no values)"
             % layout["layout"],
             ""]
    for index, record in enumerate(records):
        if "asset_id" in record:
            lines.append("\t; record %d, asset_id %#06x" % (index, record["asset_id"]))
        else:
            lines.append("\t; record %d" % index)
        for field in layout["fields"]:
            value = record[field["name"]]
            block = field.get("pointer")
            if field["type"] == "u16":
                lines.append("\tDCW\t0x%04X\t; %s" % (value, field["name"]))
            elif block and value:
                lines.append("\tDCD\t%s + 0x%04X\t; %s"
                             % (block["label"], value - block["base"], field["name"]))
            else:
                lines.append("\tDCD\t0x%08X\t; %s" % (value, field["name"]))
        lines.append("")
    return "\n".join(lines)


def reread(text, layout):
    blocks = {}
    for field in layout["fields"]:
        block = field.get("pointer")
        if block:
            blocks[block["label"]] = block["base"]
    out = bytearray()
    for line in text.splitlines():
        line = line.split(";")[0].strip()
        if not line:
            continue
        parts = line.replace("\t", " ").split()
        if parts[0] not in ("DCW", "DCD"):
            raise ValueError("the generated line is not a DCW or DCD: %r" % line)
        for operand in " ".join(parts[1:]).split(","):
            out += struct.pack("<H" if parts[0] == "DCW" else "<I",
                               value_of(operand.strip(), blocks))
    return bytes(out)


def value_of(operand, blocks):
    if operand.startswith("0x"):
        return int(operand, 16)
    if operand.isdigit():
        return int(operand)
    for label, base in blocks.items():
        if operand.startswith(label):
            rest = operand[len(label):].strip()
            return base + (int(rest.lstrip("+ ").strip(), 0) if rest else 0)
    raise ValueError("the generated operand names no block: %r" % operand)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=os.path.join(ROOT, "baserom.gba"))
    parser.add_argument("--layout", default=LAYOUT)
    parser.add_argument("--out")
    args = parser.parse_args()
    layout = load_layout(args.layout)
    rom = open(args.rom, "rb").read()
    records = parse(rom, layout)
    text = source(records, layout)
    offset = layout["base"] - ROM_BASE
    size = layout["count"] * layout["stride"]
    if reread(text, layout) != rom[offset:offset + size]:
        raise SystemExit("%s: the emitted text is not the image's own bytes" % layout["layout"])
    out = args.out or os.path.join(ROOT, *layout["output"].split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="ascii", newline="\n") as handle:
        handle.write(text)
    print("%s: %d record(s), %d field(s), %d bytes, wrote %s"
          % (layout["layout"], len(records), len(layout["fields"]), size, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
