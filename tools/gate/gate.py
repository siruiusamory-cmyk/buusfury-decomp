import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from bisect import bisect_right

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "lint"))

import encode_cache
import emitted
import lints
CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
REGION_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
BUILD = os.path.join(ROOT, "rebuild.cmd")
IMAGE = os.path.join(ROOT, "build", "output", "ROM_START")
RETAIL = os.path.join(ROOT, "baserom.gba")
LEDGER = os.path.join(ROOT, "work", "ledger.csv")
LOG = os.path.join(ROOT, "work", "rebuild.log")
ROM_SIZE = 8388608

BUDGETS = {"warm": 10.0, "edit": 15.0, "cold": 300.0, "materialise": 300.0, "partial": 300.0}
EDIT_MISS_SHARE = 0.10
CACHE = "cold-cache"
EXTRACT = os.path.join(ROOT, "extract.cmd")
COLD_DERIVATIONS = ("mapcontainer", "spritecontainer", "structured", "endrom", "spritedefs",
                    "assetdir", "assetdir3", "jcalg1", "animframe", "opcode")
COLD_OUTPUT = "tilebank_0945c0.bin"
COLD_STRINGS = "strings.cpp"
COLD_RECORDS = ("endromrecords.s", "musicrecords.s")


def classify(rows, rewritten=0):
    misses = sum(row[2] for row in rows)
    total = sum(row[4] for row in rows)
    trusted = bool(rows) and all(row[3] == 1 for row in rows)
    if total and misses == 0 and rewritten == 0:
        return "warm"
    if trusted and total and 0 < misses < EDIT_MISS_SHARE * total:
        return "edit"
    if total and misses > 0 and cold_shortfall(rows) is None:
        return "cold"
    if rewritten and misses == 0:
        return "materialise"
    return "partial"


def files_rewritten(log_path):
    total = 0
    for line in open(log_path, errors="replace"):
        match = re.search(r"files rewritten=(\d+)", line)
        if match:
            total += int(match.group(1))
    return total


def emitter_rows(log_path):
    rows = []
    spawns = hits = None
    containers = None
    for line in open(log_path, errors="replace"):
        match = re.search(r"sections=\d+ generated=\d+.*containers=(\d+)", line)
        if match:
            containers = int(match.group(1))
            continue
        match = re.search(r"oracle spawns=(\d+) cache hits=(\d+) misses=(\d+)", line)
        if match:
            spawns, hits = int(match.group(1)), int(match.group(2))
            continue
        match = re.search(r"encode_cache_misses=(\d+) trusted=(\d+) total=(\d+)", line)
        if match:
            rows.append((spawns, hits, int(match.group(1)), int(match.group(2)),
                         int(match.group(3)), containers))
            spawns = hits = None
            containers = None
    return rows


def encode_misses(log_path):
    rows = emitter_rows(log_path)
    return (sum(row[2] for row in rows), sum(row[4] for row in rows),
            bool(rows) and all(row[3] == 1 for row in rows))


def emitter_report(log_path):
    blocks = []
    current = None
    manifest = False
    for line in open(log_path, errors="replace"):
        if line.startswith("manifest path"):
            manifest = True
            continue
        match = re.search(r"sections=(\d+) generated=(\d+)", line)
        if match:
            current = {"generated": int(match.group(2)), "manifest": manifest}
            counts = re.search(r"containers=(\d+) records=(\d+)", line)
            if counts:
                current["containers"] = int(counts.group(1))
                current["records"] = int(counts.group(2))
            manifest = False
            continue
        match = re.search(r"oracle spawns=(\d+) cache hits=(\d+)", line)
        if match and current is not None:
            current["spawns"], current["hits"] = int(match.group(1)), int(match.group(2))
            continue
        match = re.search(r"encode_cache_misses=(\d+) trusted=(\d+) total=(\d+)", line)
        if match and current is not None:
            current["misses"] = int(match.group(1))
            current["trusted"] = int(match.group(2))
            current["total"] = int(match.group(3))
            blocks.append(current)
            current = None
            continue
        match = re.search(r"(\w+)_exit=(\d+)", line)
        if match and blocks and "name" not in blocks[-1]:
            blocks[-1]["name"] = match.group(1)
    return blocks


def generated_shortfall(blocks):
    for block in blocks:
        name = block.get("name", "an unnamed emitter")
        if not block.get("generated"):
            continue
        if block.get("containers") == 0:
            continue
        if block.get("total", 0) <= 0:
            return ("%s wrote generated=%d yet reports an encode population of %d"
                    % (name, block["generated"], block.get("total", 0)))
        if "spawns" in block and not block.get("manifest") \
                and block["spawns"] + block["hits"] <= 0:
            return ("%s wrote generated=%d yet spent no oracle spawn and no cache hit over %d"
                    " member(s)" % (name, block["generated"], block["total"]))
    return None


def cold_shortfall(rows):
    if not rows:
        return "no emitter reported a cache line"
    for index, row in enumerate(rows, 1):
        spawns, hits, misses, _trusted, total = row[:5]
        if len(row) > 5 and row[5] == 0:
            continue
        if total == 0:
            return "emitter %d reports a population of zero" % index
        if spawns is None:
            if misses != total:
                return ("emitter %d printed no oracle line and re-derived %d of its %d population"
                        % (index, misses, total))
        elif spawns == 0 or spawns + hits != total:
            return ("emitter %d spent %s spawn(s) and %s same-run cache hit(s) over %d member(s)"
                    % (index, spawns, hits, total))
    encoded = [row for row in rows if len(row) <= 5 or row[5] != 0]
    if encoded and all(row[3] == 1 for row in encoded):
        return "every emitter met a store with a valid stamp, so the run did not start cold"
    return None


def stage_of(log_path, label=None):
    rows = emitter_rows(log_path)
    return label or classify(rows, files_rewritten(log_path)), sum(row[2] for row in rows)


def timing(log_path, seconds, label=None):
    stage, misses = stage_of(log_path, label)
    budget = BUDGETS[stage]
    ok = seconds <= budget
    print("TIMING %s %.2fs misses=%d budget=%.1fs %s"
          % (stage, seconds, misses, budget, "PASS" if ok else "BREACH"))
    return ok


def rebuild_and_time(label=None, retry=True):
    if rebuild() != 0:
        return 1, False
    stage, _ = stage_of(LOG, label)
    if timing(LOG, rebuild.seconds, stage):
        return 0, True
    if not retry:
        return 0, False
    print("anti-flake: immediate re-run, a lone breach after idle is not a verdict (P-162)")
    if rebuild() != 0:
        return 1, False
    return 0, timing(LOG, rebuild.seconds, stage)


def cold_cache_dir():
    return os.path.join(ROOT, "build", CACHE)


def cold_purge():
    removed = 0
    for name in sorted(os.listdir(ROOT)):
        if name.startswith("baserom.gba_0x") and name.endswith(".extracted"):
            os.remove(os.path.join(ROOT, name))
            removed += 1
    for name in COLD_DERIVATIONS:
        shutil.rmtree(os.path.join(ROOT, "build", name), ignore_errors=True)
    output = os.path.join(ROOT, "build", COLD_OUTPUT)
    if os.path.exists(output):
        os.remove(output)
    strings = os.path.join(ROOT, "build", COLD_STRINGS)
    if os.path.exists(strings):
        os.remove(strings)
    for name in COLD_RECORDS:
        records = os.path.join(ROOT, "build", name)
        if os.path.exists(records):
            os.remove(records)
    return removed


def cold_start():
    cache = cold_cache_dir()
    shutil.rmtree(cache, ignore_errors=True)
    os.environ[encode_cache.CACHE_ENV] = cache
    slices = cold_purge()
    print("cold start: %s isolated and empty, %d INCBIN slice(s) and every generated section purged,"
          " the shared store untouched" % (cache, slices))
    rc = subprocess.call(["cmd.exe", "/c", EXTRACT], cwd=ROOT)
    if rc != 0:
        print("GATE FAIL: extract exit %d" % rc)
    return rc


def cold_promote(target):
    source = cold_cache_dir()
    copied = skipped = 0
    if os.path.abspath(source) == os.path.abspath(target):
        return copied, skipped
    os.makedirs(target, exist_ok=True)
    for name in sorted(os.listdir(source)):
        if name != encode_cache.EXE_STAMP and not name.endswith(".bin"):
            continue
        destination = os.path.join(target, name)
        temporary = "%s.promote-%d" % (destination, os.getpid())
        try:
            shutil.copyfile(os.path.join(source, name), temporary)
            if name == encode_cache.EXE_STAMP:
                os.replace(temporary, destination)
            else:
                os.rename(temporary, destination)
            copied += 1
        except OSError:
            skipped += 1
        finally:
            if os.path.exists(temporary):
                os.remove(temporary)
    return copied, skipped


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def incbin_ranges():
    out = []
    for name in sorted(os.listdir(os.path.join(ROOT, "asm"))):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(ROOT, "asm", name), errors="replace").read()
        for m in re.finditer(r"baserom\.gba_0x([0-9a-fA-F]+)_0x([0-9a-fA-F]+)\.extracted", text):
            start, end = int(m.group(1), 16), int(m.group(2), 16)
            out.append((start, end - start))
    return sorted(out)


def source_bytes():
    named = [("INCBIN", incbin_ranges()), ("identity", identity_ranges())]
    problems = interval_problems(named)
    if problems:
        raise SystemExit("the measured intervals do not partition the image: %s" % "; ".join(problems))
    covered = union_ranges([interval for _owner, intervals in named for interval in intervals])
    return ROM_SIZE - sum(length for _start, length in covered)


def interval_problems(named):
    problems, spans = [], []
    for owner, intervals in named:
        for start, length in intervals:
            if length <= 0 or start < 0 or start + length > ROM_SIZE:
                problems.append("%s interval %#x+%#x is outside 0..%#x"
                                % (owner, start, length, ROM_SIZE))
            else:
                spans.append((start, start + length, owner))
    spans.sort()
    end, who = 0, None
    for start, stop, owner in spans:
        if start < end:
            problems.append("%s interval %#x..%#x overlaps %s ending at %#x"
                            % (owner, start, stop, who, end))
        if stop > end:
            end, who = stop, owner
    return problems


def accounted(raw, copies, source):
    total = raw + copies + source
    if total == ROM_SIZE:
        return total, None
    return total, ("the disjoint class totals raw %d + identity %d + source %d = %d are not the "
                   "image's %d" % (raw, copies, source, total, ROM_SIZE))


def union_ranges(ranges):
    out = []
    for start, length in sorted(ranges):
        if out and start <= out[-1][0] + out[-1][1]:
            end = max(out[-1][0] + out[-1][1], start + length)
            out[-1] = (out[-1][0], end - out[-1][0])
        else:
            out.append((start, length))
    return out


def extract_sites(root=None):
    root = ROOT if root is None else root
    path = os.path.join(root, "tools", "extract", "extract.py")
    spec = importlib.util.spec_from_file_location("_gate_extract_sites", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SITES


def identity_ranges(root=None):
    root = ROOT if root is None else root
    return sorted((start, end - start) for _name, start, end in extract_sites(root))


def fill_run(image):
    start = len(image)
    while start and image[start - 1] == 0xFF:
        start -= 1
    return start, len(image) - start


def strings_class():
    path = os.path.join(ROOT, "tools", "text", "strings_layout.json")
    layout = json.load(open(path, encoding="ascii"))
    return layout.get("class", "codec"), int(layout["count"])


def missing_slices():
    missing = []
    asm = os.path.join(ROOT, "asm")
    for name in sorted(os.listdir(asm)):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(asm, name), errors="replace").read()
        for m in re.finditer(r"INCBIN\s+(\S+\.extracted)", text):
            if not os.path.exists(os.path.join(ROOT, m.group(1))):
                missing.append(m.group(1))
    return missing


def fragment_symbols(root=None):
    root = ROOT if root is None else root
    out = {}
    directory = os.path.join(root, "asm")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".s"):
            continue
        text = open(os.path.join(directory, name), errors="replace").read()
        for start, end, _token, cited in emitted.fragment_symbols(text):
            out[start] = (end, cited)
    return out


def raw_classes():
    sys.path.append(os.path.join(ROOT, "tools", "research"))
    import citations_in_source

    rows, classes, _recorded = citations_in_source.measure()
    raw = sum(row[1] for row in rows)
    return raw, classes["cited"], classes["runtime-cited"], classes["unreferenced"]


def tracked_rom_slices(retail):
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        return None
    hits = []
    for raw in proc.stdout.split(b"\0"):
        path = raw.decode()
        if not path or not os.path.exists(os.path.join(ROOT, path)):
            continue
        blob = open(os.path.join(ROOT, path), "rb").read()
        if 32 <= len(blob) <= len(retail) and retail.find(blob) >= 0:
            hits.append(path)
    return hits


def ledger_rows(path=None):
    path = path or LEDGER
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = (line.split(",") + [""] * 8)[:8]
        rows.append(ledger_parts(parts))
    return rows


def ledger_walk(image, retail, rows, slices):
    reach = []
    for start, length in slices:
        reach.append(max(start + length, reach[-1] if reach else 0))
    ok = True
    total = insn_total = data_total = 0
    for off, length, isa, region, source, kind, evidence, insn in rows:
        same = image[off:off + length] == retail[off:off + length]
        index = bisect_right(reach, off)
        covered = [slices[index][0]] if index < len(slices) and slices[index][0] < off + length \
            else []
        total += length
        insn_total += insn
        data_total += length - insn
        print("  %-40s file 0x%06x..0x%06x %5d B %-5s %-14s %-20s insn=%5d data=%5d %s" %
              (region, off, off + length, length, isa, kind, source, insn, length - insn,
               ("BYTE-EQUAL " + evidence if same else "MISMATCH") if not covered
               else "STILL INCBIN at 0x%x" % covered[0]))
        if not same or covered:
            ok = False
    return ok, total, insn_total, data_total


def diff_runs(a, b, limit=20):
    runs = []
    i, n = 0, min(len(a), len(b))
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            runs.append((i, j - i, a[i:j], b[i:j]))
            i = j
        else:
            i += 1
    print("differing bytes=%d in %d run(s)" % (sum(r[1] for r in runs), len(runs)))
    for off, ln, av, bv in runs[:limit]:
        print("  +0x%06x  %3d B   A=%s  B=%s" % (off, ln, av[:16].hex(" "), bv[:16].hex(" ")))
    if len(runs) > limit:
        print("  ... %d more run(s)" % (len(runs) - limit))
    return runs


LEDGER_CODES = {
    2: {"thumb": "t", "arm": "a", "data": "d"},
    4: {"asm/buu.s": "b", "asm/slice_*.s": "s", "asm/rest_of_the_game.s": "r", "asm/GBARam.s": "G"},
    5: {"transcription": "t", "generated": "g", "c": "c"},
    6: {"byte-proven": "p", "c-matched": "m"},
}
LEDGER_ESCAPE = "\\"
LEDGER_RESERVED = frozenset(code for table in LEDGER_CODES.values() for code in table.values())


def ledger_text(index, word):
    code = LEDGER_CODES.get(index, {}).get(word)
    if code is not None:
        return code
    if word in LEDGER_RESERVED or word.startswith(LEDGER_ESCAPE):
        return LEDGER_ESCAPE + word
    return word


def ledger_word(index, text):
    if text.startswith(LEDGER_ESCAPE):
        return text[1:]
    for word, code in LEDGER_CODES.get(index, {}).items():
        if code == text:
            return word
    return text


def ledger_parts(parts):
    return (int(parts[0], 16), int(parts[1]), ledger_word(2, parts[2]), parts[3],
            ledger_word(4, parts[4]), ledger_word(5, parts[5]), ledger_word(6, parts[6]),
            int(parts[7]) if parts[7] else 0)


def ledger_line(row):
    off, length, isa, region, source, kind, evidence, insn = row
    return "0x%x,%d,%s,%s,%s,%s,%s,%d\n" % (off, length, ledger_text(2, isa), region,
                                            ledger_text(4, source), ledger_text(5, kind),
                                            ledger_text(6, evidence), insn)


def write_ledger(rows, path=None):
    with open(path or LEDGER, "w", encoding="ascii", newline="\n") as handle:
        for row in rows:
            handle.write(ledger_line(row))


def purge_outputs():
    work = os.path.join(ROOT, "build")
    os.makedirs(work, exist_ok=True)
    for name in os.listdir(work):
        if name.endswith(".o"):
            os.remove(os.path.join(work, name))
    if os.path.exists(IMAGE):
        os.remove(IMAGE)


def error_lines(log_path):
    return [line.strip() for line in open(log_path, errors="replace")
            if re.search("error:", line, re.IGNORECASE)]


def rebuild(quiet=False):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    purge_outputs()
    started = time.perf_counter()
    with open(LOG, "w") as log:
        rc = subprocess.call(["cmd.exe", "/c", BUILD], stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
    elapsed = time.perf_counter() - started
    steps, failed = [], []
    for line in open(LOG):
        m = re.search(r"(\w+)_exit=(\d+)", line)
        if m:
            steps.append((m.group(1), int(m.group(2))))
            if m.group(2) != "0":
                failed.append(m.group(1))
    if not quiet:
        if failed:
            print("rebuild exit=%d  FAILED STEPS=%s" % (rc, ",".join(failed)))
        else:
            print("rebuild exit=%d  steps=%d  failed=[]" % (rc, len(steps)))
        for line in error_lines(LOG):
            print("  " + line)
    rebuild.seconds = elapsed
    if rc != 0 or failed or not os.path.exists(IMAGE):
        print("GATE FAIL: the build did not produce an image from every source file")
        return 1
    return 0


def census_check():
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "research",
                                                       "function_bounds.py"), "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    for line in proc.stdout.strip().splitlines() or ["BOUNDS FAIL: no output"]:
        print(line)
    return proc.returncode


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--compare":
        a = open(sys.argv[2], "rb").read()
        b = open(sys.argv[3], "rb").read()
        if len(a) != len(b):
            print("SIZE MISMATCH %d vs %d" % (len(a), len(b)))
        print("A sha256=%s" % hashlib.sha256(a).hexdigest())
        print("B sha256=%s" % hashlib.sha256(b).hexdigest())
        diff_runs(a, b)
        return

    cold = len(sys.argv) == 2 and sys.argv[1] == "--cold"
    shared_cache = encode_cache.default_cache_dir() if cold else ""

    findings = lints.run()
    for name, detail in findings:
        print("LINT FAIL %s: %s" % (name, detail))
    if findings:
        print("GATE FAIL: %d lint finding(s)" % len(findings))
        return 1
    print("LINT PASS %s" % ",".join(lints.CHECKS))

    if census_check() != 0:
        print("GATE FAIL: the function-bounds census is not what the image gives")
        return 1

    if cold and cold_start() != 0:
        return 1

    rc, timing_ok = rebuild_and_time(retry=not cold)
    if rc != 0:
        print("GATE FAIL: rebuild exit %d" % rc)
        return 1
    if cold:
        rows = emitter_rows(LOG)
        for spawns_row, hits_row, misses_row, trusted_row, total_row, *_ in rows:
            print("cold evidence: spawns=%s hits=%s misses=%d trusted=%d total=%d"
                  % (spawns_row, hits_row, misses_row, trusted_row, total_row))
        stage, misses = stage_of(LOG)
        print("cold evidence: stage=%s misses=%d" % (stage, misses))
        if stage != "cold":
            print("GATE FAIL: --cold is not a cold measurement: %s (P-174, P-175)"
                  % cold_shortfall(rows))
            return 1
    shortfall = generated_shortfall(emitter_report(LOG))
    if shortfall:
        for block in emitter_report(LOG):
            print("emitter evidence: %s generated=%s spawns=%s hits=%s total=%s"
                  % (block.get("name", "?"), block.get("generated"), block.get("spawns"),
                     block.get("hits"), block.get("total")))
        print("GATE FAIL: an emitter wrote generated runs it never encoded: %s (P-164)"
              % shortfall)
        return 1
    image = open(IMAGE, "rb").read()
    if len(image) != ROM_SIZE:
        print("GATE FAIL: image size %d" % len(image))
        return 1
    digest = hashlib.sha256(image).hexdigest()
    retail = open(RETAIL, "rb").read()
    print("image sha256=%s" % digest)
    print("canonical    =%s" % CANONICAL_SHA256)

    digest_ok = digest == CANONICAL_SHA256
    print("DIGEST %s" % ("MATCH" if digest_ok else "MISMATCH"))
    ok = digest_ok and timing_ok

    rows = ledger_rows()
    print("ledger regions: %d" % len(rows))
    inc_ranges = incbin_ranges()
    walked, total, insn_total, data_total = ledger_walk(image, retail, rows, inc_ranges)
    ok = ok and walked

    inc = sum(length for _start, length in inc_ranges)
    print("incbin slices=%d total=%d" % (len(inc_ranges), inc))
    copies = tracked_rom_slices(retail)
    print("tracked ROM slices: %s" % ("git ls-files failed" if copies is None
                                      else (", ".join(copies) if copies else "none")))
    ok = ok and copies == []
    miss = missing_slices()
    if miss:
        print("MISSING .extracted files: %s" % miss)
        ok = False
    identity = identity_ranges()
    copies_total = sum(length for _start, length in identity)
    extract_total = sum(end - start for _name, start, end in extract_sites())
    problems = interval_problems([("INCBIN", inc_ranges), ("identity", identity)])
    for problem in problems:
        print("GATE FAIL: %s" % problem)
    ok = ok and not problems
    covered = union_ranges(inc_ranges + identity)
    source = ROM_SIZE - sum(length for _start, length in covered)
    print("identity copies=%d (%.4f %%) extract %d / generator identity %d"
          % (copies_total, 100.0 * copies_total / ROM_SIZE, extract_total,
             copies_total - extract_total))
    fill_start, fill_bytes = fill_run(image)
    print("fill=%d (0x%06X..0x%06X, uniform 0xFF) counted in source"
          % (fill_bytes, fill_start, fill_start + fill_bytes))
    raw, cited, runtime, unreferenced = raw_classes()
    if raw != inc:
        print("GATE FAIL: the classified raw-data total %d is not the INCBIN total %d" % (raw, inc))
        ok = False
    print("raw-data=%d (%.4f %%) cited %d / runtime-cited %d / unreferenced %d"
          % (inc, 100.0 * inc / ROM_SIZE, cited, runtime, unreferenced))
    print("source=%d of %d (%.4f %%)" % (source, ROM_SIZE, 100.0 * source / ROM_SIZE))
    kind, count = strings_class()
    print("strings=%d wide strings by the build-time generator (%s, counted in source)"
          % (count, kind))
    accounted_total, problem = accounted(inc, copies_total, source)
    print("accounted=%d of %d (%.4f %%) raw %d + identity %d + source %d"
          % (accounted_total, ROM_SIZE, 100.0 * accounted_total / ROM_SIZE, inc, copies_total, source))
    if problem:
        print("GATE FAIL: %s" % problem)
        ok = False
    print("transcribed by ledger=%d of which instruction bytes=%d data bytes=%d"
          % (total, insn_total, data_total))
    if cold:
        if ok:
            copied, skipped = cold_promote(shared_cache)
            print("cold promotion: %d entry(ies) copied into %s, %d already present"
                  % (copied, shared_cache, skipped))
        else:
            print("cold promotion skipped: the cold run did not pass")
    print("GATE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
