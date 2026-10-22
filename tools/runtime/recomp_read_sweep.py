"""Sweep the target maps through one retargeted warp, and turn each run's reads into citations.

The route is the one this ticket measured (A1): one input trace opens the saved game and walks down
through `map:0038/transition:0000` at frame 1920. That record is retargeted in a private ROM copy to
each map of the coverage (B1/B2), the logging runtime records every ROM read inside the plan's range
file, and `recomp_cited.citations` applies RUNTIME_READ_PLAN P2.

Per run the driver records the arrival map, the liveness witness count, the log's digest and line
count, and the citation rows; the raw log is deleted once those are recorded (A6).

    READ_LOG_EXE=<runtime binary> python tools/runtime/recomp_read_sweep.py --rom <private copy> \
        --save <private save> --ranges <range file> --maps 76,374,316 --out <private dir>
    READ_LOG_EXE=<runtime binary> python tools/runtime/recomp_read_sweep.py ... --cover

Kills: only a PID this driver started is stopped, never by name.
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "research"))

import recomp_cited  # noqa: E402
import warp_patch  # noqa: E402

EXE = os.environ.get("READ_LOG_EXE", "")
OWNERS = os.path.join(ROOT, "docs", "research", "MAP_ROW_OWNERS.csv")
RECORD = 0x295C3C
TARGETS = os.path.join(ROOT, "docs", "research", "RUNTIME_TARGETS.csv")
LEDGER = os.path.join(ROOT, "work", "ledger.csv")
LIVENESS_OFFSET = 0x8E2E0
LIVENESS = 0x08000000 + LIVENESS_OFFSET
LIVENESS_PC = 0x08008A0E
FIELDS = ("run",) + recomp_cited.FIELDS
MANIFEST_FIELDS = ("run", "scene", "status", "arrival", "witness", "witness_pc", "log_sha256",
                   "log_lines", "patched_sha256", "patched_sha1", "changed_offsets", "seconds",
                   "note")
HIT_FIELDS = ("run", "start", "hits", "pcs", "max_address")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def cover(path=OWNERS, targets=TARGETS):
    with open(path, newline="") as handle:
        owned = {}
        for row in csv.DictReader(handle):
            keys = row["owners"]
            if keys == "owner unknown":
                continue
            for token in keys.split(";"):
                owned.setdefault(int(token.split(":")[1]), set()).add(
                    (int(row["start"], 16), int(row["end"], 16)))
    left = {(row["start"], row["end"]) for row in recomp_cited.read_targets(targets)}
    picked = []
    while left:
        best = max(owned, key=lambda index: len(owned[index] & left), default=None)
        if best is None or not owned[best] & left:
            break
        picked.append(best)
        left -= owned[best]
        owned.pop(best)
    return picked


def quiet(pid):
    kernel = ctypes.windll.kernel32
    handle = kernel.OpenProcess(0x0100 | 0x0200, False, pid)
    if handle:
        kernel.SetPriorityClass(handle, 0x4000)
        kernel.SetProcessAffinityMask(handle, 0x3F)
        kernel.CloseHandle(handle)


def arrival(iwram):
    data = open(iwram, "rb").read()
    pointer = int.from_bytes(data[0x1980:0x1984], "little")
    if not 0x0808E2E0 <= pointer < 0x0808E2E0 + 452 * 0x38:
        return None
    if (pointer - 0x0808E2E0) % 0x38:
        return None
    return (pointer - 0x0808E2E0) // 0x38


def run_one(args, index, run_dir):
    patched = os.path.join(run_dir, "warp-%04d.gba" % index)
    report = json.loads(_patch(args.rom, index, patched))
    sha1 = hashlib.sha1(open(patched, "rb").read()).hexdigest()
    log = os.path.join(run_dir, "hits-%04d.csv" % index)
    save = os.path.join(run_dir, "save-%04d.sav" % index)
    shutil.copy2(args.save, save)
    iwram = os.path.join(run_dir, "iwram-%04d.bin" % index)
    environment = dict(os.environ,
                       GBARECOMP_INPUT_REPLAY=args.trace, GBARECOMP_READ_LOG=log,
                       GBARECOMP_READ_LOG_RANGES=args.ranges, GBARECOMP_IWRAM_DUMP=iwram)
    if os.environ.get("READ_LOG_PATH_PREFIX"):
        environment["PATH"] = os.environ["READ_LOG_PATH_PREFIX"] + os.pathsep + os.environ["PATH"]
    if not EXE:
        raise SystemExit("READ_LOG_EXE must name the read-logging runtime binary")
    started = time.monotonic()
    process = subprocess.Popen(
        [EXE, "--no-window", "--frames", str(args.frames), "--rom", patched,
         "--rom-sha1", sha1, "--save", save, "--quiet"],
        env=environment, creationflags=0x4000, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    quiet(process.pid)
    try:
        _out, err = process.communicate(timeout=args.run_timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        process.kill()
        _out, err = process.communicate()
        timed_out = True
    elapsed = time.monotonic() - started
    hits = list(recomp_cited.read_hits(log)) if os.path.exists(log) else []
    row_hits = {}
    for hit in hits:
        offset = recomp_cited.offset_of(hit["addr"])
        if offset is None:
            continue
        for target in args.targets_rows:
            if target["start"] <= offset < target["end"]:
                entry = row_hits.setdefault(target["start"], {"hits": 0, "pcs": set(), "max": 0})
                entry["hits"] += 1
                entry["pcs"].add(hit["pc"])
                entry["max"] = max(entry["max"], offset)
                break
    witness = sum(1 for hit in hits if hit["addr"] == LIVENESS)
    witness_pc = next((hit["pc"] for hit in hits if hit["addr"] == LIVENESS), 0)
    rows = recomp_cited.citations(hits, args.targets_rows, args.ledger_rows)
    digest = sha256(log) if os.path.exists(log) else None
    lines = len(hits)
    if os.path.exists(log):
        os.remove(log)
    os.remove(patched)
    arrived = arrival(iwram) if os.path.exists(iwram) else None
    if os.path.exists(iwram):
        os.remove(iwram)
    os.remove(save)
    note = ("timeout after %gs" % args.run_timeout) if timed_out else \
        " ".join(err.decode("ascii", "replace").strip().splitlines()[-1:])
    return {"run": index, "scene": args.scene,
            "status": ("timeout" if timed_out else "ok" if witness else "silent-dead-log"
                       if process.returncode == 0 else "recomp-exit-%d" % process.returncode),
            "arrival": arrived, "witness": witness, "witness_pc": witness_pc,
            "log_sha256": digest, "log_lines": lines, "note": note,
            "patched_sha256": report["patched_sha256"], "patched_sha1": sha1,
            "changed_offsets": report["changed_offsets"], "seconds": round(elapsed, 1),
            "citations": rows, "row_hits": row_hits}


def _patch(rom, index, out):
    with open(rom, "rb") as handle:
        source = handle.read()
    key = warp_patch.map_key(source, index)
    patched = warp_patch.apply(source, RECORD, key)
    changed = [offset for offset in range(len(source)) if source[offset] != patched[offset]]
    warp_patch.guard([RECORD + warp_patch.KEY_OFFSET + position for position in range(2)])
    legal = {RECORD + warp_patch.KEY_OFFSET, RECORD + warp_patch.KEY_OFFSET + 1}
    if not set(changed) <= legal:
        raise SystemExit("the patch changed bytes outside the key span: %s"
                         % ["0x%06x" % offset for offset in changed])
    with open(out, "wb") as handle:
        handle.write(patched)
    return json.dumps({"changed_offsets": ["0x%06x" % offset for offset in changed],
                       "patched_sha256": hashlib.sha256(patched).hexdigest().upper()})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rom", required=True)
    parser.add_argument("--save", required=True)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--ranges", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--maps", help="comma list; default the greedy cover of MAP_ROW_OWNERS.csv")
    parser.add_argument("--frames", type=int, default=2600)
    parser.add_argument("--scene", default="saved-game-warp",
                        help="the entry this run measures (recorded in the manifest)")
    parser.add_argument("--budget-seconds", type=float, default=14400)
    parser.add_argument("--run-timeout", type=float, default=300)
    parser.add_argument("--targets", default=TARGETS)
    parser.add_argument("--ledger", default=LEDGER)
    args = parser.parse_args(argv)
    args.targets_rows = recomp_cited.read_targets(args.targets)
    args.ledger_rows = recomp_cited.read_ledger(args.ledger)
    maps = [int(token) for token in args.maps.split(",")] if args.maps else cover()
    os.makedirs(args.out, exist_ok=True)
    with open(args.ranges, encoding="ascii") as handle:
        ranges_text = handle.read().rstrip("\n")
    live_ranges = os.path.join(args.out, "ranges-live.txt")
    with open(live_ranges, "w", encoding="ascii", newline="\n") as handle:
        handle.write(ranges_text + "\n%x %x\n" % (LIVENESS_OFFSET, LIVENESS_OFFSET + 0x10))
    args.ranges = live_ranges
    manifest = os.path.join(args.out, "runs.csv")
    citations = os.path.join(args.out, "citations.csv")
    hit_rows = os.path.join(args.out, "row-hits.csv")
    started, spent = time.monotonic(), 0.0
    with open(manifest, "w", encoding="ascii", newline="") as manifest_handle, \
            open(citations, "w", encoding="ascii", newline="") as citations_handle, \
            open(hit_rows, "w", encoding="ascii", newline="") as hit_handle:
        manifest_writer = csv.writer(manifest_handle, lineterminator="\n")
        citations_writer = csv.writer(citations_handle, lineterminator="\n")
        hit_writer = csv.writer(hit_handle, lineterminator="\n")
        manifest_writer.writerow(MANIFEST_FIELDS)
        citations_writer.writerow(FIELDS)
        hit_writer.writerow(HIT_FIELDS)
        for index in maps:
            if time.monotonic() - started > args.budget_seconds:
                print("budget reached before map %d" % index)
                break
            result = run_one(args, index, args.out)
            spent += result["seconds"]
            status = result["status"]
            if result.get("witness") and result.get("witness_pc") != LIVENESS_PC:
                status = "wrong-liveness-pc"
            if status == "ok" and result.get("arrival") != index:
                status = "wrong-arrival-%s" % result.get("arrival")
            manifest_writer.writerow(str(value) for value in (
                index, result["scene"], status, result.get("arrival", ""),
                result.get("witness", 0),
                "0x%08x" % result.get("witness_pc", 0),
                result.get("log_sha256", ""), result.get("log_lines", 0),
                result.get("patched_sha256", ""), result.get("patched_sha1", ""),
                ";".join(result.get("changed_offsets", [])), result["seconds"],
                (result.get("note") or "").encode("ascii", "replace").decode("ascii")))
            for row in result.get("citations", []):
                citations_writer.writerow(
                    ("0x%06x" % row[field]) if field in ("start", "end", "reader_start",
                                                         "reader_end")
                    else ("0x%08x" % row[field]) if field in ("address", "pc")
                    else str(index) if field == "run" else str(row[field])
                    for field in FIELDS)
            for start, entry in sorted(result.get("row_hits", {}).items()):
                hit_writer.writerow((index, "0x%06x" % start, entry["hits"],
                                     ";".join("0x%08x" % pc for pc in sorted(entry["pcs"])),
                                     "0x%06x" % entry["max"]))
            print("map %d %s witness=%s citations=%d %.1fs"
                  % (index, status, result.get("witness"), len(result.get("citations", [])),
                     result["seconds"]))
    print("runs: %d maps, %.1f s of recomp wall time, manifest %s"
          % (len(maps), spent, manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
