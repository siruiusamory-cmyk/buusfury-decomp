from __future__ import annotations

import bisect
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import gate

SCHEMA = 1
GAME = "buus_fury"
MAP_SOURCE = "armlink -map -symbols"
ROM_BASE = 0x08000000
ROM_END = 0x08800000
IMAGE_SIZE = 8388608
EVIDENCE = ("byte-proven", "c-matched", "ghidra", "runtime-proven", "declared", "inferred")
TYPE_KIND = {"ARM Code": "arm", "Thumb Code": "thumb", "Data": "data"}
STATE_KIND = {"$a": "arm", "$t": "thumb", "$b": "thumb", "$d": "data"}
ISA_KIND = {"arm": "arm", "thumb": "thumb", "data": "data"}
ENTRY_KEYS = ("name", "address", "size", "kind", "evidence", "format", "region", "source",
              "instructions")
NAME_MAX = 160
SYMBOL = re.compile(r"^\s{4}(.+?)\s+0x([0-9a-f]{8})\s+"
                    r"(ARM Code|Thumb Code|Data|Number)\s+(\d+)\s+(\S.*?)\s*$")
STATE = re.compile(r"^\s{4}(\$\S)\s+0x([0-9a-f]{8})\s+\S+\s*$")
HEX_RUN = re.compile(r"[0-9a-fA-F]{24,}")
HEX_DUMP = re.compile(r"([0-9a-fA-F]{2} ){8,}")


def digest_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def toolchain():
    try:
        proc = subprocess.run(["armlink", "-vsn"], capture_output=True, text=True)
    except OSError as exc:
        raise SystemExit("the linker cannot be queried for its version: %s" % exc)
    text = (proc.stdout + proc.stderr).strip()
    if not text:
        raise SystemExit("armlink -vsn printed nothing")
    return text.splitlines()[0].strip()


def commit_date(root=ROOT):
    proc = subprocess.run(["git", "show", "-s", "--format=%cI", "HEAD"], cwd=root,
                          capture_output=True, text=True)
    text = proc.stdout.strip()
    if proc.returncode != 0 or not text:
        raise SystemExit("HEAD's commit date cannot be read: %s" % proc.stderr.strip())
    return text


def read_map(path):
    symbols = []
    states = []
    region = None
    for line in open(path, errors="replace"):
        line = line.rstrip("\r\n")
        if line.startswith("Image Symbol Table"):
            region = "symbols"
            continue
        if line.startswith("Memory Map of the image"):
            region = None
            continue
        if line.startswith("    Mapping Symbols"):
            region = "states"
            continue
        if line.startswith("    Local Symbols") or line.startswith("    Global Symbols"):
            region = "symbols"
            continue
        if not line.strip():
            continue
        if region == "states":
            match = STATE.match(line)
            if match:
                states.append((int(match.group(2), 16), match.group(1)))
            continue
        if region != "symbols":
            continue
        match = SYMBOL.match(line)
        if not match:
            continue
        symbols.append((match.group(1), int(match.group(2), 16), match.group(3),
                        int(match.group(4)), match.group(5)))
    if not symbols or not states:
        raise SystemExit("%s holds %d symbol(s) and %d mapping symbol(s)"
                         % (path, len(symbols), len(states)))
    states.sort()
    return symbols, states


def ledger_rows(path):
    if os.path.abspath(path) != os.path.abspath(gate.LEDGER):
        previous = gate.LEDGER
        gate.LEDGER = path
        try:
            rows = gate.ledger_rows()
        finally:
            gate.LEDGER = previous
    else:
        rows = gate.ledger_rows()
    rows.sort()
    for before, after in zip(rows, rows[1:]):
        if before[0] + before[1] > after[0]:
            raise SystemExit("ledger rows %s and %s overlap" % (before[3], after[3]))
    return rows


def slices():
    return [(start + ROM_BASE, length) for start, length in gate.incbin_ranges()]


def state_at(states, address):
    index = bisect.bisect_right(states, (address, "\xff")) - 1
    if index < 0:
        raise SystemExit("no mapping symbol at or before 0x%08x" % address)
    return states[index][1]


def covering(starts, spans, address, size):
    index = bisect.bisect_right(starts, address) - 1
    if index < 0:
        return None
    span = spans[index]
    return span if span[1] >= address + size else None


def touched(incbin, address, size):
    index = bisect.bisect_right(incbin, (address,)) - 1
    for start, length in incbin[max(index, 0):index + 2]:
        if size == 0:
            inside = start <= address < start + length
        else:
            inside = start < address + size and address < start + length
        if inside:
            return (start, length), start <= address and address + size <= start + length
    return None, False


def slice_name(start, length):
    return "slice_0x%08x_0x%08x" % (start, start + length)


def ledger_entries(rows, states, incbin):
    entries = []
    for off, length, isa, region, source, kind, evidence, insn in rows:
        address = off + ROM_BASE
        state = state_at(states, address)
        if state not in STATE_KIND:
            raise SystemExit("mapping symbol %s at 0x%08x names no kind" % (state, address))
        if STATE_KIND[state] != ISA_KIND[isa]:
            raise SystemExit("ledger %s says %s at 0x%08x, the mapping symbol says %s"
                             % (region, isa, address, state))
        if evidence not in EVIDENCE:
            raise SystemExit("ledger %s carries evidence %r" % (region, evidence))
        hit, whole = touched(incbin, address, length)
        entry = {"name": region, "address": "0x%08x" % address, "size": length,
                 "kind": STATE_KIND[state], "source": source,
                 "region": slice_name(*hit) if whole else region}
        if insn:
            entry["instructions"] = insn
        entry["evidence"] = "inferred" if hit else "byte-proven"
        entries.append(entry)
    return entries


def symbol_entries(symbols, starts, spans, incbin, taken):
    kept = []
    names = {}
    for name, address, type_, size, obj in symbols:
        if not ROM_BASE <= address < ROM_END or type_ not in TYPE_KIND:
            continue
        if re.search(r"[A-Za-z]:[\\/]|\\", name):
            raise SystemExit("symbol %r carries a host path" % name)
        names[name] = names.get(name, 0) + 1
        kept.append((name, address, type_, size, obj))
    entries = []
    for name, address, type_, size, obj in kept:
        if names[name] > 1:
            continue
        if name in taken:
            if taken[name] != address:
                raise SystemExit("symbol %s at 0x%08x collides with the ledger's 0x%08x"
                                 % (name, address, taken[name]))
            continue
        taken[name] = address
        if address + size > ROM_END:
            raise SystemExit("symbol %s runs past the image: 0x%08x + %d"
                             % (name, address, size))
        span = covering(starts, spans, address, size)
        hit, whole = touched(incbin, address, size)
        entry = {"name": name, "address": "0x%08x" % address, "size": size,
                 "kind": TYPE_KIND[type_], "source": obj}
        if span and not hit:
            entry["evidence"] = "byte-proven"
            entry["region"] = span[2]
        else:
            entry["evidence"] = "inferred"
            if whole:
                entry["region"] = slice_name(*hit)
        entries.append(entry)
    return entries


def document(map_path, ledger_path, image_path, commit, toolchain_name):
    symbols, states = read_map(map_path)
    rows = ledger_rows(ledger_path)
    spans = [(row[0] + ROM_BASE, row[0] + ROM_BASE + row[1], row[3]) for row in rows]
    starts = [span[0] for span in spans]
    incbin = slices()
    rom_digest = digest_file(gate.RETAIL)
    if rom_digest != gate.CANONICAL_SHA256:
        raise SystemExit("baserom.gba sha256 %s is not the canonical %s"
                         % (rom_digest, gate.CANONICAL_SHA256))
    image_digest = digest_file(image_path)
    image_bytes = os.path.getsize(image_path)
    if image_bytes != IMAGE_SIZE:
        raise SystemExit("the image is %d bytes, not %d" % (image_bytes, IMAGE_SIZE))
    entries = ledger_entries(rows, states, incbin)
    taken = {entry["name"]: int(entry["address"], 16) for entry in entries}
    entries += symbol_entries(symbols, starts, spans, incbin, taken)
    entries.sort(key=lambda entry: (int(entry["address"], 16), entry["size"], entry["name"]))
    for entry in entries:
        for key in entry:
            if key not in ENTRY_KEYS:
                raise SystemExit("entry %s carries %r" % (entry["name"], key))
        for key, value in entry.items():
            if isinstance(value, str) and (len(value) > NAME_MAX or HEX_RUN.search(value)
                                           or HEX_DUMP.search(value)):
                raise SystemExit("entry %s carries %s=%r" % (entry["name"], key, value))
    return {"schema": SCHEMA, "game": GAME, "rom_sha256": rom_digest,
            "build": {"toolchain": toolchain_name, "image_sha256": image_digest,
                      "image_size": image_bytes, "map_source": MAP_SOURCE,
                      "generated": commit},
            "symbols": entries}


def emit(map_path=None, ledger_path=None, out_path=None, image_path=None, commit=None,
         toolchain_name=None):
    map_path = map_path or os.path.join(gate.ROOT, "build", "buu.map")
    ledger_path = ledger_path or gate.LEDGER
    out_path = out_path or os.path.join(gate.ROOT, "build", "output", "symbols.json")
    image_path = image_path or gate.IMAGE
    key_path = out_path + ".key"
    for label, path in (("map", map_path), ("ledger", ledger_path), ("image", image_path)):
        if not os.path.exists(path):
            raise SystemExit("the %s is missing: %s" % (label, path))
    commit = commit or commit_date(gate.ROOT)
    key = ":".join((digest_file(map_path), digest_file(ledger_path), digest_file(image_path),
                    commit))
    if os.path.exists(out_path) and os.path.exists(key_path):
        if open(key_path).read().strip() == key:
            print("symbols: map, ledger, image and commit date unchanged, no re-emit")
            return -1
    toolchain_name = toolchain_name or toolchain()
    built = document(map_path, ledger_path, image_path, commit, toolchain_name)
    blob = json.dumps(built, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as handle:
        handle.write(blob)
    with open(key_path, "w", newline="\n") as handle:
        handle.write(key + "\n")
    counts = {}
    for entry in built["symbols"]:
        counts[entry["evidence"]] = counts.get(entry["evidence"], 0) + 1
    print("symbols: %d entries %d B evidence=%s"
          % (len(built["symbols"]), len(blob),
             ",".join("%s=%d" % item for item in sorted(counts.items()))))
    return len(built["symbols"])


def main():
    emit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
