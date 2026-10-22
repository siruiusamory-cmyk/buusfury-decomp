"""Candidate re-encoder fitted to the oracle's observable token stream.

Not byte-exact and unused by the build; docs/research/PACKER_ORACLE.md is the record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))

import packer_census as census  # noqa: E402
import webfoot_lz  # noqa: E402

MAX_OUTPUT = 0x4000
ONESHOT_LIMIT = 14
SHORT_DISTANCE = 127
DISTANCE_BITS = 8
ESCAPE_SEVEN_BIT = 17
ESCAPE_EIGHT_BIT = 9
MODE_WINDOW = 1024
CHAIN_CAP = 64


def window_mode(payload, pos):
    chunk = payload[pos:pos + MODE_WINDOW]
    if not chunk:
        return (8, 0)
    low, high = min(chunk), max(chunk)
    return (7, low) if high - low <= 127 else (8, 0)


def extend(payload, pos, limit, distance, best_len):
    if best_len and payload[pos + best_len] != payload[pos + best_len - distance]:
        return best_len
    length = 0
    while length < limit and payload[pos + length] == payload[pos + length - distance]:
        length += 1
    return max(best_len, length)


def find_chain(payload, pos, chain):
    limit = len(payload) - pos - 1
    if limit < 1:
        return 0, 0
    if pos < 3:
        return find(payload, pos)
    best_len, best_dist = 0, 0
    for start in reversed(chain.get(payload[pos:pos + 3], ())[-CHAIN_CAP:]):
        distance = pos - start
        if distance <= 0:
            continue
        length = extend(payload, pos, limit, distance, best_len)
        if length > best_len:
            best_len, best_dist = length, distance
    return best_len, best_dist


def bias(distance):
    return webfoot_lz.length_bias(distance)


def gamma_bits(value):
    return 2 * (value.bit_length() - 1)


def find(payload, pos):
    limit = len(payload) - pos - 1
    if limit < 1:
        return 0, 0
    best_len, best_dist = 0, 0
    for distance in range(1, pos + 1):
        if best_len >= limit:
            break
        length = extend(payload, pos, limit, distance, best_len)
        if length > best_len:
            best_len, best_dist = length, distance
    return best_len, best_dist


def single_distance(payload, pos):
    for distance in range(1, min(ONESHOT_LIMIT, pos) + 1):
        if payload[pos - distance] == payload[pos]:
            return distance
    return 0


def form_cost(length, distance):
    options = []
    if distance <= SHORT_DISTANCE and 2 <= length <= 5:
        options.append(3 + 7 + 2)
    count = length - bias(distance)
    if count >= 2:
        code = (distance >> DISTANCE_BITS) + 3
        options.append(2 + gamma_bits(code) + DISTANCE_BITS + gamma_bits(count))
    return min(options) if options else None


def parse(payload, chain=None):
    pos, total = 0, len(payload)
    tokens = []
    inserted = 0
    while pos < total:
        if chain is not None:
            while inserted < pos:
                if inserted + 3 <= total:
                    chain.setdefault(payload[inserted:inserted + 3], []).append(inserted)
                inserted += 1
            length, distance = find_chain(payload, pos, chain)
        else:
            length, distance = find(payload, pos)
        if length >= 2 and pos + 1 < total and _length_at(payload, pos + 1, chain) > length:
            tokens.append((pos, "single", 1, single_distance(payload, pos)))
            pos += 1
            continue
        if length >= 2 and form_cost(length, distance) is not None:
            tokens.append((pos, "match", length, distance))
            pos += length
            continue
        tokens.append((pos, "single", 1, single_distance(payload, pos)))
        pos += 1
    return tokens


def _length_at(payload, pos, chain):
    if chain is None:
        return find(payload, pos)[0]
    return find_chain(payload, pos, chain)[0]


def choose_modes(payload, runs, first):
    choices = []
    state = first
    for run in runs:
        state = window_mode(payload, run[0][0])
        choices.append(state)
    return choices


def write_literal_mode(writer, state):
    bits, base = state
    writer.bit(0), writer.bit(0), writer.bit(1)
    writer.put(0, 4)
    if bits == 7:
        writer.bit(0), writer.bit(0)
        writer.put(base, 8)
    else:
        writer.bit(0), writer.bit(1)


class Writer:
    def __init__(self):
        self.words = []
        self.current = 0
        self.count = 0

    def bit(self, value):
        self.current = ((self.current << 1) | (value & 1)) & 0xFFFFFFFF
        self.count += 1
        if self.count == 32:
            self.words.append(self.current)
            self.current = 0
            self.count = 0

    def put(self, value, width):
        for shift in range(width - 1, -1, -1):
            self.bit((value >> shift) & 1)

    def gamma(self, value):
        if value < 2:
            raise ValueError("gamma cannot encode %d" % value)
        for shift in range(value.bit_length() - 2, -1, -1):
            self.bit((value >> shift) & 1)
            self.bit(0 if shift == 0 else 1)

    def finish(self):
        while self.count:
            self.bit(0)
        return b"".join(struct.pack("<I", word) for word in self.words)


def runs_of(payload, tokens):
    runs, token_run, run = [], [None] * len(tokens), []
    for index, token in enumerate(tokens):
        if token[1] == "single":
            run.append(token)
            token_run[index] = len(runs)
            continue
        if run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    return token_run, runs


def encode(payload, kind=1, chain=None):
    tokens = parse(payload, chain)
    token_run, runs = runs_of(payload, tokens)
    modes = choose_modes(payload, runs, (8, 0))
    writer = Writer()
    literal_bits, literal_base = kind, 0
    current_run = -1
    previous_distance = 1
    for index, (pos, name, length, distance) in enumerate(tokens):
        if name == "single":
            run = token_run[index]
            if run != current_run:
                current_run = run
                if modes[run] != (literal_bits, literal_base):
                    write_literal_mode(writer, modes[run])
                    literal_bits, literal_base = modes[run]
            value = payload[pos]
            if literal_bits == 7 and value == literal_base:
                writer.bit(0), writer.bit(0), writer.bit(1)
                writer.put(1, 4)
            elif distance:
                writer.bit(0), writer.bit(0), writer.bit(1)
                writer.put(distance + 1, 4)
            else:
                writer.bit(1)
                writer.put((value - literal_base) & 0xFF, literal_bits)
            continue
        count = length - bias(distance)
        short = distance <= SHORT_DISTANCE and 2 <= length <= 5
        long_cost = None
        if count >= 2:
            long_cost = 2 + gamma_bits((distance >> DISTANCE_BITS) + 3) + DISTANCE_BITS + gamma_bits(count)
        prev_cost = 2 + gamma_bits(2) + gamma_bits(length) if distance == previous_distance else None
        options = []
        if short:
            options.append((3 + 7 + 2, "short"))
        if long_cost is not None:
            options.append((long_cost, "long"))
        if prev_cost is not None:
            options.append((prev_cost, "prev"))
        _, chosen = min(options)
        if chosen == "short":
            writer.bit(0), writer.bit(0), writer.bit(0)
            writer.put(distance, 7)
            writer.put(length - 2, 2)
        elif chosen == "prev":
            writer.bit(0), writer.bit(1)
            writer.gamma(2)
            writer.gamma(length)
        else:
            writer.bit(0), writer.bit(1)
            writer.gamma((distance >> DISTANCE_BITS) + 3)
            writer.put(distance & ((1 << DISTANCE_BITS) - 1), DISTANCE_BITS)
            writer.gamma(count)
        previous_distance = distance
        current_run = -1
    writer.put(0, 12)
    return struct.pack("<II", kind, len(payload)) + writer.finish()


def stream_tokens(data, offset, expected, kind):
    reader = webfoot_lz._WordBitReader(data, offset)  # noqa: SLF001
    tokens = []
    produced = 0
    literal_base, literal_bits = 0, kind
    distance_bits = 8
    while True:
        start = reader.position - 4
        if reader.bit():
            reader.get(literal_bits)
            tokens.append((start, "literal", produced))
            produced += 1
            continue
        if reader.bit():
            code = webfoot_lz._gamma(reader, expected + 3)  # noqa: SLF001
            if code == 2:
                count = webfoot_lz._gamma(reader, expected + 3)  # noqa: SLF001
                tokens.append((start, "prev", produced))
                produced += count
                continue
            distance = reader.get(distance_bits) + ((code - 3) << distance_bits)
            count = webfoot_lz._gamma(reader, expected + 3)  # noqa: SLF001
            tokens.append((start, "long", produced))
            produced += count + bias(distance)
            continue
        if reader.bit() == 0:
            distance = reader.get(7)
            if distance != 0:
                count = reader.get(2) + 2
                tokens.append((start, "short", produced))
                produced += count
                continue
            width = reader.get(2)
            if width == 0:
                tokens.append((start, "end", produced))
                break
            distance_bits = reader.get(width + 3)
            tokens.append((start, "distbits", produced))
            continue
        short_distance = reader.get(4) - 1
        if short_distance == 0:
            tokens.append((start, "base", produced))
            produced += 1
        elif short_distance > 0:
            tokens.append((start, "one", produced))
            produced += 1
        elif reader.bit():
            while True:
                reader.get(8), reader.get(8)
                if reader.bit() == 0:
                    break
            tokens.append((start, "raw", produced))
        else:
            literal_bits = 7 + reader.bit()
            if literal_bits == 7:
                literal_base = reader.get(8)
            tokens.append((start, "litwidth", produced, literal_bits, literal_base))
    return tokens, produced


def divergence(retail, candidate, declared, kind):
    index = next((i for i in range(min(len(retail), len(candidate)))
                  if retail[i] != candidate[i]), min(len(retail), len(candidate)))
    row = {"first_difference": index}
    try:
        mine, _ = stream_tokens(candidate, 8, declared, kind)
        recent = None
        for token in mine:
            if token[0] > index:
                break
            recent = token
        row["candidate_token"] = recent[1] if recent else None
    except Exception as exc:  # noqa: BLE001
        row["candidate_parse"] = "refused: %s" % exc
    try:
        theirs, _ = stream_tokens(retail, 8, declared, kind)
        recent = None
        for token in theirs:
            if token[0] > index:
                break
            recent = token
        row["oracle_token"] = recent[1] if recent else None
    except Exception:  # noqa: BLE001
        pass
    return row


def measure(rom, offsets, label, limit=None, exhaustive=False):
    rows = []
    equal = 0
    walked = sorted(offsets)[:limit] if limit else sorted(offsets)
    for offset in walked:
        container = webfoot_lz.unpack(rom, offset, maximum_output=MAX_OUTPUT)
        extent, declared, kind = census.retail_extent(rom, offset)
        retail = rom[offset:extent]
        chain = None if exhaustive else {}
        candidate = encode(container.data, kind, chain)
        row = {"offset": offset, "declared": declared, "retail_size": len(retail),
               "candidate_size": len(candidate),
               "retail_sha256": hashlib.sha256(retail).hexdigest(),
               "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
               "payload_sha256": hashlib.sha256(container.data).hexdigest()}
        if candidate == retail:
            equal += 1
            row["equal"] = True
        else:
            row["equal"] = False
            row.update(divergence(retail, candidate, declared, kind))
        rows.append(row)
    summary = {"label": label, "walked": len(walked), "byte_equal": equal,
               "failures": [row for row in rows if not row.get("equal")], "rows": rows}
    print("%s: walked %d byte-equal %d failures %d"
          % (label, summary["walked"], equal, len(summary["failures"])), flush=True)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--corpus", default="fixtures",
                        choices=("fixtures", "tilebanks", "sprites", "all"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--exhaustive", action="store_true")
    args = parser.parse_args(argv)
    rom = census.read_rom(args.rom)
    report = {}
    if args.corpus in ("fixtures", "all"):
        report["fixtures"] = measure(rom, census.FIXTURE_PACKED, "fixtures", args.limit, args.exhaustive)
    if args.corpus in ("tilebanks", "all"):
        report["tilebanks"] = measure(rom, census.tilebank_containers(rom), "tilebanks", args.limit, args.exhaustive)
    if args.corpus in ("sprites", "all"):
        report["sprites"] = measure(rom, census.sprite_containers(rom), "sprites", args.limit, args.exhaustive)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1, sort_keys=True)
    for key, section in sorted(report.items()):
        print("%s: byte-equal %d of %d" % (key, section["byte_equal"], section["walked"]))
        for row in section["failures"][:6]:
            print("   %#08x declared %s retail %s candidate %s %s"
                  % (row["offset"], row.get("declared"), row.get("retail_size"),
                     row.get("candidate_size"),
                     {k: v for k, v in row.items() if k in
                      ("first_difference", "oracle_token", "candidate_token")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
