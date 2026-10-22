import argparse
import hashlib
import os
import shutil
import sys

import gate

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(ROOT, "work", "perturb-base.gba")


def restore(paths):
    for path, text in paths.items():
        open(path, "wb").write(text)
        print("restored %s" % os.path.relpath(path, ROOT))


def parse_edits(a):
    if a.old_hex or a.new_hex:
        if len(a.file) != len(a.old_hex) or len(a.file) != len(a.new_hex):
            print("REFUSE --old-hex/--new-hex must name every edit")
            return None
        return [(f, bytes.fromhex(o), bytes.fromhex(n), off, b, af) for f, o, n, off, b, af
                in zip(a.file, a.old_hex, a.new_hex, a.offset, a.before, a.after)]
    if len(a.file) != len(a.old) or len(a.file) != len(a.new):
        print("REFUSE every --file needs its --old/--new or its --old-hex/--new-hex")
        return None
    return [(f, o.encode(), n.encode(), off, b, af) for f, o, n, off, b, af
            in zip(a.file, a.old, a.new, a.offset, a.before, a.after)]


def main():
    ap = argparse.ArgumentParser()
    for name in ("file", "offset", "before", "after"):
        ap.add_argument("--" + name, required=True, action="append")
    for name in ("old", "new", "old-hex", "new-hex"):
        ap.add_argument("--" + name, action="append", default=[])
    a = ap.parse_args()

    edits = parse_edits(a)
    if edits is None:
        return 1
    paths = {}
    for f, old, new, off, before, after in edits:
        path = os.path.join(ROOT, f)
        paths.setdefault(path, open(path, "rb").read())
        hits = paths[path].count(old)
        if hits != 1:
            print("REFUSE %s: %d occurrence(s) of %r" % (f, hits, old[:48]))
            return 1

    if gate.rebuild() != 0:
        return 1
    base_seconds = gate.rebuild.seconds
    before_hash = hashlib.sha256(open(gate.IMAGE, "rb").read()).hexdigest()
    if before_hash != gate.CANONICAL_SHA256:
        print("REFUSE base image is not canonical")
        return 1
    base_ok = gate.timing(gate.LOG, base_seconds, "warm")
    base_misses = gate.encode_misses(gate.LOG)[0]
    shutil.copyfile(gate.IMAGE, BASE)
    print("base image canonical, saved to %s" % BASE)
    if not base_ok:
        return 1

    for f, old, new, off, before, after in edits:
        path = os.path.join(ROOT, f)
        text = open(path, "rb").read()
        open(path, "wb").write(text.replace(old, new, 1))
        print("perturbed %s at 0x%s" % (f, off))
    if gate.rebuild() != 0:
        restore(paths)
        return 1
    edit_ok = gate.timing(gate.LOG, gate.rebuild.seconds, "edit")
    edit_misses = gate.encode_misses(gate.LOG)[0]
    after = open(gate.IMAGE, "rb").read()
    if hashlib.sha256(after).hexdigest() == gate.CANONICAL_SHA256:
        print("FAIL the perturbation did not reach the image")
        restore(paths)
        return 1
    old_image = open(BASE, "rb").read()
    runs = gate.diff_runs(old_image, after, limit=len(edits) + 5)
    want = sorted((int(off, 16), bytes.fromhex(before), bytes.fromhex(after_))
                  for _, _, _, off, before, after_ in edits)
    got = sorted((off, av, bv) for off, ln, av, bv in runs)
    ok = got == want
    for off, bv, av in want:
        hit = [g for g in got if g[0] == off]
        print("predicted: 0x%06x %s -> %s  %s" %
              (off, bv.hex(" "), av.hex(" "), "found" if hit else "MISSING"))
    print("PERTURBATION %s (%d edit(s), %d differing run(s))"
          % ("PASS" if ok else "FAIL", len(edits), len(runs)))

    restore(paths)
    if gate.rebuild() != 0:
        return 1
    restore_ok = gate.timing(gate.LOG, gate.rebuild.seconds, "warm")
    restore_misses = gate.encode_misses(gate.LOG)[0]
    final = hashlib.sha256(open(gate.IMAGE, "rb").read()).hexdigest()
    print("restored sha256=%s" % final)
    print("misses base=%d edit=%d restore=%d" % (base_misses, edit_misses, restore_misses))
    print("RESTORE %s" % ("PASS" if final == gate.CANONICAL_SHA256 else "FAIL"))
    counted = base_misses == 0 and edit_misses == 1 and restore_misses == 0
    if not counted:
        print("FAIL the miss counts are not 0/1/0")
    return 0 if (ok and edit_ok and restore_ok and counted
                 and final == gate.CANONICAL_SHA256) else 1


if __name__ == "__main__":
    sys.exit(main())
