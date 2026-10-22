"""Census of the retail packed containers against the external re-encoder.

The comparison basis is the container's retail-terminating extent: for a packed
container ``rom[offset:offset + len(oracle_output)]``, where the extent is the
one ``webfoot_lz.validate_retail_termination`` measures (the stream's own
escape, not the declared size).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritecontainer"))

import webfoot_lz  # noqa: E402
import spritecontainer  # noqa: E402

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000
COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")
CHARACTER_TABLE = 0x6B6BDC
CHARACTER_COUNT = 297
BANK_TABLE = 0x179764
BANK_COUNT = 187
SPRITE_CONTAINERS = 7390
SPRITE_BYTES = 2752020
MAX_OUTPUT = 0x4000

FIXTURE_PACKED = (0x3C34D0, 0x3C35B8, 0x3C36A0, 0x3C3754, 0x3C3808, 0x3C3918,
                  0x54A5C8, 0x54A6C0, 0x54A7E4, 0x54A910, 0x54AB4C, 0x54AC6C)
FIXTURE_STORED = (0x0154CC, 0x047F60, 0x0555B8)


def read_rom(path):
    data = open(path, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ROM_SHA256 or len(data) != 0x800000:
        raise SystemExit("ROM is %d bytes sha256 %s" % (len(data), digest))
    return data


def word(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def retail_extent(rom, offset):
    kind, _declared = webfoot_lz.read_header(rom, offset)
    if kind == webfoot_lz.STORED:
        container = webfoot_lz.unpack(rom, offset, maximum_output=MAX_OUTPUT)
        return container.packed_end, container.declared_size, kind
    container = webfoot_lz.validate_retail_termination(rom, offset, maximum_output=MAX_OUTPUT)
    return container.packed_end, container.declared_size, kind


def sprite_containers(rom):
    return spritecontainer.references(rom)


def tilebank_containers(rom):
    return {word(rom, BANK_TABLE + 4 * index) - ROM_BASE for index in range(BANK_COUNT)}


class Oracle:
    def __init__(self, exe, scratch):
        self.exe = exe
        self.scratch = scratch
        self.run = itertools.count()

    def __call__(self, payload):
        stem = os.path.join(self.scratch, "census-%06d" % next(self.run))
        with open(stem + ".in", "wb") as handle:
            handle.write(payload)
        proc = subprocess.run([self.exe, stem + ".in", stem + ".out"], capture_output=True)
        blob = None
        if proc.returncode == 0:
            try:
                with open(stem + ".out", "rb") as handle:
                    blob = handle.read()
            except OSError:
                blob = None
        for suffix in (".in", ".out"):
            try:
                os.remove(stem + suffix)
            except OSError:
                pass
        if blob is None:
            return None, "exit %d %s" % (proc.returncode,
                                         proc.stderr.decode("utf-8", "replace").strip())
        return blob, ""


def census(rom, offsets, oracle, label, limit=None):
    rows = []
    equal = 0
    failures = []
    walked = sorted(offsets)
    if limit:
        walked = walked[:limit]
    for position, offset in enumerate(walked):
        try:
            payload = webfoot_lz.unpack(rom, offset, maximum_output=MAX_OUTPUT).data
        except webfoot_lz.ContainerError as exc:
            failures.append({"offset": offset, "reason": "decode: %s" % exc})
            rows.append({"offset": offset, "equal": False, "reason": "decode: %s" % exc})
            continue
        extent, declared, kind = retail_extent(rom, offset)
        blob, error = oracle(payload)
        row = {
            "offset": offset,
            "declared": declared,
            "kind": kind,
            "retail_extent": extent - offset,
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
        }
        if blob is None:
            row["equal"] = False
            row["reason"] = "oracle %s" % error
            failures.append(row)
            rows.append(row)
            continue
        row["oracle_size"] = len(blob)
        retail = rom[offset:offset + len(blob)]
        row["retail_sha256"] = hashlib.sha256(retail).hexdigest()
        row["oracle_sha256"] = hashlib.sha256(blob).hexdigest()
        if blob == retail:
            row["equal"] = True
            equal += 1
        else:
            first = next((index for index in range(min(len(blob), len(retail)))
                          if blob[index] != retail[index]), min(len(blob), len(retail)))
            row["equal"] = False
            row["first_difference"] = first
            failures.append(row)
        rows.append(row)
        if position % 500 == 0:
            print("  %s %d/%d equal %d" % (label, position, len(walked), equal), flush=True)
    print("%s: walked %d, oracle-run %d, byte-equal %d, failures %d"
          % (label, len(walked), sum(1 for row in rows if "oracle_size" in row), equal,
             len(failures)), flush=True)
    return {"label": label, "walked": len(walked), "equal": equal,
            "failures": failures, "rows": rows}


def cmd_fixtures(args):
    rom = read_rom(args.rom)
    os.makedirs(args.outdir, exist_ok=True)
    oracle = Oracle(COMPRESS, args.outdir)
    index = []
    for offset in FIXTURE_PACKED + FIXTURE_STORED:
        container = webfoot_lz.unpack(rom, offset, maximum_output=MAX_OUTPUT)
        extent, declared, kind = retail_extent(rom, offset)
        if kind == webfoot_lz.STORED:
            blob, error = webfoot_lz.build_stored(container.data), ""
        else:
            blob, error = oracle(container.data)
        if blob is None:
            raise SystemExit("oracle failed on fixture %#x: %s" % (offset, error))
        name = "fixture_%06x" % offset
        with open(os.path.join(args.outdir, name + ".payload"), "wb") as handle:
            handle.write(container.data)
        with open(os.path.join(args.outdir, name + ".container"), "wb") as handle:
            handle.write(rom[offset:extent])
        with open(os.path.join(args.outdir, name + ".oracle"), "wb") as handle:
            handle.write(blob)
        index.append({
            "offset": offset,
            "kind": kind,
            "declared": declared,
            "retail_extent": extent - offset,
            "oracle_size": len(blob),
            "equal": blob == rom[offset:offset + len(blob)],
            "payload_sha256": hashlib.sha256(container.data).hexdigest(),
            "container_sha256": hashlib.sha256(rom[offset:extent]).hexdigest(),
            "oracle_sha256": hashlib.sha256(blob).hexdigest(),
        })
        print("%s kind %d declared %d extent %d oracle %d %s"
              % (name, kind, declared, extent - offset, len(blob),
                 "EQUAL" if index[-1]["equal"] else "DIFFER"))
    with open(os.path.join(args.outdir, "index.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=1, sort_keys=True)
    return 0


def cmd_census(args):
    rom = read_rom(args.rom)
    scratch = os.path.join(ROOT, "build", "packer-census-scratch")
    os.makedirs(scratch, exist_ok=True)
    oracle = Oracle(COMPRESS, scratch)
    report = {}
    banks = tilebank_containers(rom)
    report["tilebanks"] = census(rom, banks, oracle, "tilebanks")
    sprites = sprite_containers(rom)
    if len(sprites) != SPRITE_CONTAINERS:
        raise SystemExit("sprite walk reached %d containers, not %d"
                         % (len(sprites), SPRITE_CONTAINERS))
    report["sprite_containers"] = len(sprites)
    report["sprite_reference_count"] = sum(sprites.values())
    report["sprites"] = census(rom, sprites, oracle, "sprites")
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1, sort_keys=True)
    print("report %s" % args.out)
    return 0


def cmd_verify_fixtures(args):
    rom = read_rom(args.rom)
    index = json.load(open(os.path.join(args.fixtures, "index.json"), encoding="utf-8"))
    oracle = Oracle(COMPRESS, args.fixtures)
    reproduced = 0
    for row in index:
        payload = open(os.path.join(args.fixtures, "fixture_%06x.payload" % row["offset"]), "rb").read()
        if hashlib.sha256(payload).hexdigest() != row["payload_sha256"]:
            raise SystemExit("fixture %#x payload digest changed" % row["offset"])
        if row["kind"] == webfoot_lz.STORED:
            blob = webfoot_lz.build_stored(payload)
        else:
            blob, error = oracle(payload)
            if blob is None:
                raise SystemExit("oracle failed on %#x: %s" % (row["offset"], error))
        if len(blob) != row["oracle_size"] or hashlib.sha256(blob).hexdigest() != row["oracle_sha256"]:
            raise SystemExit("fixture %#x does not reproduce" % row["offset"])
        if hashlib.sha256(rom[row["offset"]:row["offset"] + len(blob)]).hexdigest() != row["container_sha256"]:
            raise SystemExit("fixture %#x retail bytes changed" % row["offset"])
        reproduced += 1
    print("fixtures: %d of %d reproduce their recorded digests" % (reproduced, len(index)))
    return 0


def cmd_summary(args):
    report = json.load(open(args.census, encoding="utf-8"))
    for key in ("tilebanks", "sprites"):
        section = report[key]
        print("%s: walked %d byte-equal %d failures %d"
              % (key, section["walked"], section["equal"], len(section["failures"])))
        for row in section["failures"][:40]:
            print("   %#08x declared %s extent %s oracle %s %s"
                  % (row["offset"], row.get("declared"), row.get("retail_extent"),
                     row.get("oracle_size"), row.get("reason", "first diff at %s" % row.get("first_difference"))))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fixtures = commands.add_parser("fixtures")
    fixtures.add_argument("--rom", required=True)
    fixtures.add_argument("--outdir", required=True)
    fixtures.set_defaults(run=cmd_fixtures)
    run = commands.add_parser("census")
    run.add_argument("--rom", required=True)
    run.add_argument("--out", required=True)
    run.set_defaults(run=cmd_census)
    summary = commands.add_parser("summary")
    summary.add_argument("--census", required=True)
    summary.set_defaults(run=cmd_summary)
    verify = commands.add_parser("verify-fixtures")
    verify.add_argument("--rom", required=True)
    verify.add_argument("--fixtures", required=True)
    verify.set_defaults(run=cmd_verify_fixtures)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
