from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = "build/asm-cache"
COLD_ENV = "BUUSFURY_COLD_BUILD"
INCLUDE = re.compile(r"^\s*INCLUDE\s+(\S+)\s*$", re.M)
INCBIN = re.compile(r"INCBIN\s+(\S+\.extracted)")
UNITS = {"buu": ("asm/buu.s", "build/buu.o"),
         "rest": ("asm/rest_of_the_game.s", "build/rest_of_the_game.o")}


EMIT_STAMP = "build/asm-cache/emit.sha256"
EMIT_OUTPUTS = ("build/endromrecords.s", "build/musicrecords.s", "build/strings.cpp",
                "build/tilebank_0945c0.bin", "build/opcode", "build/jcalg1",
                "build/mapcontainer", "build/spritecontainer", "build/structured",
                "build/endrom", "build/spritedefs", "build/assetdir", "build/assetdir3")


def read(path):
    with open(path, "rb") as handle:
        return handle.read()


def inside(root, name):
    return os.path.join(root, *name.split("/"))


def relative(root, base, name):
    beside = base + "/" + name if base else name
    if os.path.exists(inside(root, beside)):
        return beside
    return name


def assembler(root):
    stock = os.path.normpath(os.path.join(root, "..", "toolchains", "ads12-build805", "Bin",
                                         "armasm.exe"))
    return stock if os.path.exists(stock) else shutil.which("armasm")


def inputs(root, source):
    files = []
    seen = set()
    pending = [source]
    while pending:
        name = pending.pop(0)
        if name in seen:
            continue
        seen.add(name)
        data = read(inside(root, name))
        files.append((name, data))
        text = data.decode("utf-8", "replace")
        base = os.path.dirname(name)
        for found in INCLUDE.findall(text):
            pending.append(relative(root, base, found))
        for found in INCBIN.findall(text):
            path = inside(root, found)
            files.append((found, read(path) if os.path.exists(path) else b"absent"))
    tool = assembler(root)
    if tool:
        files.append((tool, read(tool)))
    return files


def digest(root, source):
    state = hashlib.sha256()
    for name, data in inputs(root, source):
        state.update(name.encode("utf-8") + b"\0" + hashlib.sha256(data).digest())
    return state.hexdigest()


def entry_of(root, unit, key):
    return inside(root, "%s/%s-%s.o" % (CACHE, unit, key))


def restore(root, unit, source, output):
    entry = entry_of(root, unit, digest(root, source))
    if not os.path.exists(entry):
        return False
    os.makedirs(os.path.dirname(inside(root, output)), exist_ok=True)
    shutil.copyfile(entry, inside(root, output))
    return True


def keep(root, unit, source, output):
    entry = entry_of(root, unit, digest(root, source))
    os.makedirs(os.path.dirname(entry), exist_ok=True)
    temporary = "%s.%d.tmp" % (entry, os.getpid())
    shutil.copyfile(inside(root, output), temporary)
    os.replace(temporary, entry)
    return entry


def slices(root):
    sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
    import gate
    gate.ROOT = root
    missing = gate.missing_slices()
    for name in missing[:10]:
        print("slice absent: %s" % name)
    print("slices missing=%d" % len(missing))
    return 0 if not missing else 1


def emit_digest(root):
    state = hashlib.sha256()
    for base, dirs, names in os.walk(inside(root, "tools")):
        dirs[:] = sorted(name for name in dirs if name != "__pycache__")
        for name in sorted(names):
            path = os.path.join(base, name)
            state.update(os.path.relpath(path, root).replace(os.sep, "/").encode("utf-8") + b"\0")
            state.update(hashlib.sha256(read(path)).digest())
    state.update(hashlib.sha256(read(inside(root, "baserom.gba"))).digest())
    return state.hexdigest()


def emit_ready(root):
    if os.environ.get(COLD_ENV):
        return False
    if not all(os.path.exists(inside(root, name)) for name in EMIT_OUTPUTS):
        return False
    stamp = inside(root, EMIT_STAMP)
    return os.path.exists(stamp) and read(stamp).decode("ascii").strip() == emit_digest(root)


def emit_record(root):
    stamp = inside(root, EMIT_STAMP)
    os.makedirs(os.path.dirname(stamp), exist_ok=True)
    temporary = "%s.%d.tmp" % (stamp, os.getpid())
    with open(temporary, "w", encoding="ascii", newline="") as handle:
        handle.write(emit_digest(root))
    os.replace(temporary, stamp)


def main(argv=None, root=ROOT):
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["slices"]:
        return slices(root)
    if args[:1] == ["emit"]:
        if emit_ready(root):
            print("asm-cache emit: restored")
            return 0
        return 1
    if args[:1] == ["emit-keep"]:
        emit_record(root)
        return 0
    unit = args[0] if args else ""
    if unit not in UNITS:
        print("usage: build_cache.py slices|<%s>" % "|".join(sorted(UNITS)))
        return 2
    source, output = UNITS[unit]
    if not os.environ.get(COLD_ENV) and restore(root, unit, source, output):
        print("asm-cache %s: restored" % unit)
        return 0
    os.makedirs(os.path.dirname(inside(root, output)), exist_ok=True)
    code = subprocess.call(["armasm", source, "-o", output], cwd=root)
    print("asm-cache %s: assembled exit=%d" % (unit, code))
    if code == 0:
        keep(root, unit, source, output)
    return code


if __name__ == "__main__":
    sys.exit(main())
