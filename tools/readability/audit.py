from __future__ import annotations

import ast
import collections
import csv
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASM = "asm/"
SRC = ("src/", "include/")
HEX = re.compile(r"0x[0-9A-Fa-f]+")
SLICE = re.compile(r"^asm/(?:sub|loc|dat|unk|g)_([0-9A-Fa-f]{8})\.s$")
START_LABEL = re.compile(r"^\|((?:sub|loc|dat|unk|g)_[0-9A-Fa-f]{8})\|\s*$")
ANY_LABEL = re.compile(r"^\|([A-Za-z_][A-Za-z0-9_]*)\|\s*$")
EXPORT = re.compile(r"^\s*EXPORT\s+(\S+)\s*$")
INCBIN = re.compile(r"^\s*INCBIN\s+(\S+)\s*$")
EQU = re.compile(r"^\s*\|?([A-Za-z0-9_]+)\|?\s+EQU\s+", re.I)
COMMENT = re.compile(r"^\s*[;#]")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ADDRESS_NAME = re.compile(r"^(?:sub|loc|dat|unk|g)_[0-9A-Fa-f]{8}$")
IO_START, IO_END = 0x04000000, 0x040003FF
PLTT_START, PLTT_END = 0x05000000, 0x050003FF
VRAM_START, VRAM_END = 0x06000000, 0x0601FFFF
OAM_START, OAM_END = 0x07000000, 0x070003FF
EWRAM_START, EWRAM_END = 0x02000000, 0x0203FFFF
IWRAM_START, IWRAM_END = 0x03000000, 0x03007FFF
PATH_STEPS = (
    ("clone", "git clone"),
    ("extract", "extract.cmd"),
    ("build", "rebuild.cmd"),
    ("gate", "python tools\\gate\\gate.py"),
    ("find", "ASM_INDEX"),
    ("change", "NAMING_LEDGER"),
)
PATH_DOC = "docs/NEWCOMER.md"
DOC_TREE = ("README.md", "INSTALL.md", "CONTRIBUTING.md", "docs/NEWCOMER.md", "docs/NAMING.md",
            "docs/ASM_INDEX.md", "docs/DEFINITION_OF_DONE.md")


def tracked(suffix):
    proc = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                          cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        return []
    return sorted(name for name in proc.stdout.decode("utf-8", "replace").split("\0")
                  if name.endswith(suffix))


def read(name):
    try:
        return open(os.path.join(ROOT, *name.split("/")), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def band(value, start, end):
    return start <= value <= end


def asm_lines():
    for name in tracked(".s") + tracked(".inc"):
        if not name.startswith(ASM):
            continue
        label = ""
        for number, line in enumerate(read(name).splitlines(), 1):
            found = ANY_LABEL.match(line)
            if found:
                label = found.group(1)
            yield name, number, line, label


def asm_tokens():
    for name, number, line, label in asm_lines():
        if COMMENT.match(line) or EQU.match(line):
            continue
        for match in HEX.finditer(line):
            yield name, number, int(match.group(0), 16), line, label


def literal_sites(bands, skip=()):
    sites = []
    for name, number, value, line, label in asm_tokens():
        if name in skip:
            continue
        if any(band(value, start, end) for start, end in bands):
            sites.append((name, number, value, line, label))
    for name in tracked(".c") + tracked(".h"):
        if not (name.startswith(SRC[0]) or name.startswith(SRC[1])) or name in skip:
            continue
        for number, line in enumerate(read(name).splitlines(), 1):
            if line.strip().startswith("#define"):
                continue
            for match in HEX.finditer(line):
                value = int(match.group(0), 16)
                if any(band(value, start, end) for start, end in bands):
                    sites.append((name, number, value, line, ""))
    return sites


def starts_per_file():
    bounds = list(csv.DictReader(io.StringIO(read("docs/research/FUNCTION_BOUNDS.csv"))))
    starts = [int(row["address"], 16) for row in bounds if row["kind"] in ("start", "unreferenced")]
    counts = collections.Counter()
    for name in tracked(".s"):
        found = SLICE.match(name)
        if found:
            counts[name] = starts.count(int(found.group(1), 16))
    return counts, starts


def data_tables():
    lines = []
    for name, number, line, label in asm_lines():
        found = INCBIN.match(line)
        if found:
            lines.append((name, found.group(1)))
    rows = list(csv.DictReader(io.StringIO(read("docs/research/RAW_REMAINDER.csv"))))
    named = sum(1 for row in rows if not row["token"].startswith(("baserom.gba_", "inc_")))
    total = sum(int(row["bytes"]) for row in rows)
    return lines, len(rows), named, total


def magic_sites():
    bands = ((IO_START, IO_END), (PLTT_START, PLTT_END), (VRAM_START, VRAM_END),
             (OAM_START, OAM_END), (EWRAM_START, EWRAM_END), (IWRAM_START, IWRAM_END))
    sites = []
    for name in tracked(".c") + tracked(".h"):
        if not (name.startswith(SRC[0]) or name.startswith(SRC[1])):
            continue
        for number, line in enumerate(read(name).splitlines(), 1):
            if line.strip().startswith("#define"):
                continue
            for match in HEX.finditer(line):
                value = int(match.group(0), 16)
                if value in (0, 1) or any(band(value, start, end) for start, end in bands):
                    continue
                sites.append((name, number, value))
    return sites


def magic_constants():
    sites = magic_sites()
    return len(sites), len({site[2] for site in sites})


def equ_names():
    named = set()
    address_named = set()
    for name, number, line, label in asm_lines():
        found = EQU.match(line)
        if not found:
            continue
        value = HEX.search(line)
        ram = value is not None and any(band(int(value.group(0), 16), start, end)
                                        for start, end in ((EWRAM_START, EWRAM_END),
                                                           (IWRAM_START, IWRAM_END)))
        if not ram:
            continue
        if ADDRESS_NAME.match(found.group(1)):
            address_named.add(found.group(1))
        else:
            named.add(found.group(1))
    return named, address_named


def exports():
    names = set()
    for name, number, line, label in asm_lines():
        found = EXPORT.match(line)
        if found and "$" not in found.group(1):
            names.add(found.group(1).strip("|"))
    return names


def tool_modules():
    return [name for name in tracked(".py")
            if name.startswith("tools/") and not os.path.basename(name).startswith("test_")]


def tool_definitions():
    defined = {}
    imports = {}
    for name in tool_modules():
        text = read(name)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined[(name, node.name)] = node.lineno
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    bound = (alias.asname or alias.name).split(".")[0]
                    imports[(name, bound)] = node.lineno
    used = collections.Counter()
    for name in tracked(".py"):
        for token in IDENT.findall(read(name)):
            used[token] += 1
    return defined, imports, used


def tool_counts():
    defined, imports, used = tool_definitions()
    unused_functions = [key for key in defined if used[key[1]] <= 1]
    unused_imports = [key for key in imports if used[key[1]] <= 1]
    short = [key for key in defined if len(key[1]) <= 2]
    return defined, unused_functions, unused_imports, short


def test_coverage():
    modules = {os.path.basename(name)[:-3] for name in tool_modules()}
    tests = {os.path.basename(name)[5:-3] for name in tracked(".py")
             if os.path.basename(name).startswith("test_")}
    return sorted(modules), sorted(modules - tests), sorted(tests)


def doc_gaps():
    path = read(PATH_DOC).lower()
    tree = "\n".join(read(name) for name in DOC_TREE).lower()
    in_path = [label for label, needle in PATH_STEPS if needle.lower() in path]
    absent = [label for label, needle in PATH_STEPS if needle.lower() not in tree]
    return in_path, absent, [label for label, _needle in PATH_STEPS if label not in in_path]


def main():
    counts, starts = starts_per_file()
    asm_files = [name for name in tracked(".s") if name.startswith(ASM)]
    code_files = sorted({name for name, number, line, label in asm_lines()
                         if EXPORT.match(line)})
    biggest = sorted(counts.items(), key=lambda item: -item[1])[:3]
    multi = sum(1 for count in counts.values() if count > 1)
    print("layout files=%d code=%d function_files=%d functions=%d multi_function_files=%d"
          % (len(asm_files), len(code_files),
             sum(1 for name in asm_files if SLICE.match(name)), len(starts), multi))
    for name, count in biggest:
        print("  %s %d function start(s)" % (name, count))
    io = literal_sites(((IO_START, IO_END),))
    regions = literal_sites(((PLTT_START, PLTT_END), (VRAM_START, VRAM_END),
                             (OAM_START, OAM_END)))
    print("hardware io=%d distinct=%d regions=%d distinct=%d"
          % (len(io), len({site[2] for site in io}), len(regions),
             len({site[2] for site in regions})))
    for site in io[:3] + regions[:3]:
        print("  %s:%d 0x%08X %s" % (site[0], site[1], site[2], site[3]))
    ram = literal_sites(((EWRAM_START, EWRAM_END), (IWRAM_START, IWRAM_END)))
    inline = [site for site in ram if EQU.match(site[3]) is None]
    named, address_named = equ_names()
    print("ram literals=%d distinct=%d named=%d equ_address=%d"
          % (len(inline), len({site[2] for site in inline}), len(named),
             len(address_named)))
    for site in inline[:3]:
        print("  %s:%d 0x%08X %s" % (site[0], site[1], site[2], site[3]))
    lines, rows, raw_named, raw_bytes = data_tables()
    print("tables incbin=%d payloads=%d raw_rows=%d raw_bytes=%d raw_named=%d"
          % (len(lines), len({line[1] for line in lines}), rows, raw_bytes, raw_named))
    for line in lines[:3]:
        print("  %s %s" % line)
    sites, values = magic_constants()
    print("magic sites=%d distinct=%d" % (sites, values))
    for name, number, value in magic_sites()[:3]:
        print("  %s:%d 0x%X" % (name, number, value))
    in_path, absent, missing = doc_gaps()
    print("docs steps=%d in_path=%d missing=%s absent_in_tree=%s"
          % (len(PATH_STEPS), len(in_path), ",".join(missing) or "none",
             ",".join(absent) or "none"))
    defined, unused_functions, unused_imports, short = tool_counts()
    print("tools defs=%d unused_defs=%d unused_imports=%d short_names=%d"
          % (len(defined), len(unused_functions), len(unused_imports), len(short)))
    for key in unused_functions[:3]:
        print("  unused %s:%d %s" % (key[0], defined[key], key[1]))
    modules, untested, tests = test_coverage()
    print("tests files=%d modules=%d modules_without_test=%d"
          % (len(tests), len(modules), len(untested)))
    for name in untested[:3]:
        print("  untested %s" % name)
    exports_now = exports()
    print("symbols exports=%d named=%d address=%d"
          % (len(exports_now), sum(1 for name in exports_now if not ADDRESS_NAME.match(name)),
             sum(1 for name in exports_now if ADDRESS_NAME.match(name))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
