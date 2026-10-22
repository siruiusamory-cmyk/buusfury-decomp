from __future__ import annotations

import ast
import csv
import io
import os
import re
import subprocess
import sys
import tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QUOTED_INTERPRETER = re.compile(r"""["']cmd["']""")
SWITCH_INTERPRETER = re.compile(r"(?<![\w.\\/:-])cmd\s+[/-][ck]\b", re.I)
BATCH_INTERPRETER = re.compile(r"(?<![\w.\\/:-])cmd(?![A-Za-z0-9_.\-])")
POOL_SOURCE = re.compile(r"(?m)^\s*(?:import\s+multiprocessing\b"
                         r"|from\s+multiprocessing[\w.]*\s+import\b"
                         r"|from\s+concurrent\.futures\s+import\b[^\n]*ProcessPool)")
POOL_CALL = re.compile(r"\b(?:multiprocessing\.Pool|ProcessPoolExecutor)\s*\(")
MAIN_GUARD = re.compile(r"(?m)^if\s+__name__\s*==\s*[\"']__main__[\"']\s*:")
SEARCH_PATH = re.compile(r"sys\.path\.(?:insert|append)\s*\([^)]*")
WINDOWS_PATH = re.compile(r"[A-Za-z]:[\\/]")

C_SOURCES = (".c",)
CONTROL_KEYWORDS = frozenset(("if", "for", "while", "switch", "return", "do", "else", "sizeof"))
FUNCTION_DEFINITION = re.compile(r"^[^\s#/].*\)\s*\{\s*$")
FUNCTION_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*(?:_[A-Z][A-Za-z0-9]*)+$")
UNKNOWN_FUNCTION_NAME = re.compile(r"^sub_[0-9A-F]{8}$")
MARKER = re.compile(r"NONMATCHING-REFERENCE")
COMPILE_C = re.compile(r"src/[^\s\"]+\.c\b")
TRACKED_IMAGE = re.compile(r"\.gba$")
SIZE_LIMIT = 1024 * 1024
ASSETS = "assets/"

CHECKS = ("P-148-repo-module-path", "P-159-bare-interpreter", "P-167-pool-guard",
          "NAMING-function-name", "NAMING-c-status", "ROM-tracked-image", "README-numbers",
          "TEST-silent-return", "P-518-stale-incbin-call", "DUP-block")
STALE_CALL = re.compile(r"incbin\.bat\s+baserom\.gba\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)")
TEST_FILE = re.compile(r"^test_[^/\\]*\.py$")
DUP_MINIMUM = 8
DUP_PYTHON_ROOT = "tools/"
DUP_C_ROOTS = ("src/", "include/")
DUP_IMPORT_LINE = re.compile(r"^(?:from|import|#include)\b")
DUP_ALLOWLIST = (
    ("tools/gate/gate.py", 441, "tools/match/compare_rows.py", 24,
     "11 identical lines: gate.diff_runs and compare_rows.differing_runs are the same loop, and "
     "tools/match belongs to a separate unit, which this ticket forbids editing; compare_rows imports "
     "gate, so gate cannot import it back. Reported for the other ticket. The "
     "line moved 522 -> 567 -> 446 -> 444 -> 440 as guards and identity ranges left the file above "
     "diff_runs (P-646)."),
)
README_PERCENT = re.compile(r"([\d.]+)\s*%")
README_BYTES = re.compile(r"([\d,]+)\s+of\s+([\d,]+)\s+bytes")
README_ROWS = re.compile(r"([\d,]+)\s+ledger rows")
README_IDENTIFIED = re.compile(r"([\d.]+)\s*%\s+is identified binary\s+\(([\d,]+)\s+B\b")
README_COMMAND = re.compile(r"python tools\\gate\\gate\.py")
BATCH = (".cmd", ".bat")
SOURCES = (".py", ".cmd", ".bat")


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def source_files():
    argv = ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        return None
    return sorted(name for name in proc.stdout.decode("utf-8", "replace").split("\0")
                  if name.endswith(SOURCES))


def bare_interpreter(name, text):
    patterns = [QUOTED_INTERPRETER, SWITCH_INTERPRETER]
    if name.endswith(BATCH):
        patterns.append(BATCH_INTERPRETER)
    hits = []
    reported = set()
    for pattern in patterns:
        for match in pattern.finditer(text):
            line = line_of(text, match.start())
            if line in reported:
                continue
            reported.add(line)
            hits.append(("P-159-bare-interpreter",
                         "%s:%d: %s" % (name, line, text.splitlines()[line - 1].strip())))
    return hits


def pool_without_guard(name, text):
    match = POOL_SOURCE.search(text) or POOL_CALL.search(text)
    if match is None or MAIN_GUARD.search(text):
        return []
    line = line_of(text, match.start())
    return [("P-167-pool-guard", "%s:%d: a process pool in a module with no main guard: %s"
             % (name, line, text.splitlines()[line - 1].strip()))]


def out_of_repo_module_path(name, text):
    hits = []
    for match in SEARCH_PATH.finditer(text):
        if WINDOWS_PATH.search(match.group(0)):
            hits.append(("P-148-repo-module-path",
                         "%s:%d: %s" % (name, line_of(text, match.start()), match.group(0).strip())))
    return hits


def tracked_files():
    argv = ["git", "ls-files", "-z", "--cached"]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        return None
    return sorted(name for name in proc.stdout.decode("utf-8", "replace").split("\0") if name)


def c_source_files():
    argv = ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        return None
    return sorted(name for name in proc.stdout.decode("utf-8", "replace").split("\0")
                  if name.startswith("src/") and name.endswith(C_SOURCES))


def compiled_c_sources():
    try:
        text = open(os.path.join(ROOT, "rebuild.cmd"), encoding="utf-8", errors="replace").read()
    except OSError:
        return set()
    return set(match.group(0) for match in COMPILE_C.finditer(text))


def read_source(name):
    path = name if os.path.isabs(name) else os.path.join(ROOT, name)
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def defined_functions(text):
    for number, line in enumerate(text.splitlines(), 1):
        if FUNCTION_DEFINITION.match(line) is None:
            continue
        words = re.findall(r"[A-Za-z_]\w*", line.split("(", 1)[0])
        if not words or words[-1] in CONTROL_KEYWORDS:
            continue
        yield number, words[-1]


def function_name_findings(name, text):
    findings = []
    for number, function in defined_functions(text):
        if FUNCTION_NAME.match(function) or UNKNOWN_FUNCTION_NAME.match(function):
            continue
        findings.append(("NAMING-function-name",
                         "%s:%d: %s is not Module_Verb or sub_08XXXXXX" % (name, number, function)))
    return findings


def c_status_findings(name, text, compiled=None):
    if compiled is None:
        compiled = compiled_c_sources()
    marked = MARKER.search(header_text(text)) is not None
    if name in compiled:
        if marked:
            return [("NAMING-c-status",
                     "%s:1: rebuild.cmd compiles this file and it carries NONMATCHING-REFERENCE"
                     % name)]
        return []
    if marked:
        return []
    return [("NAMING-c-status",
             "%s:1: rebuild.cmd does not compile this file and it carries no "
             "NONMATCHING-REFERENCE marker" % name)]


def header_text(text):
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("/*", "*", "//")):
            break
        lines.append(line)
    return "\n".join(lines)


def tracked_image_name(name):
    if TRACKED_IMAGE.search(name):
        return [("ROM-tracked-image", "%s: a tracked *.gba path" % name)]
    return []


def oversize_tracked(name, size):
    if name.startswith(ASSETS) or size is None or size <= SIZE_LIMIT:
        return []
    return [("ROM-tracked-image", "%s: %d tracked bytes outside assets/" % (name, size))]


def c_source_findings():
    names = c_source_files()
    if names is None:
        return [("lint-enumeration", "git ls-files failed, the C source checks cannot see the tree")]
    findings = []
    compiled = compiled_c_sources()
    for name in names:
        text = read_source(name)
        if text is None:
            findings.append(("lint-read", "%s: cannot be read" % name))
            continue
        findings += function_name_findings(name, text)
        findings += c_status_findings(name, text, compiled)
    return findings


def tracked_rom_findings(tracked=None):
    if tracked is None:
        tracked = tracked_files()
        if tracked is None:
            return [("lint-enumeration",
                     "git ls-files failed, the tracked-path check cannot see the tree")]
    findings = []
    for name in tracked:
        findings += tracked_image_name(name)
        if name.startswith(ASSETS):
            continue
        try:
            size = os.path.getsize(os.path.join(ROOT, name))
        except OSError:
            continue
        findings += oversize_tracked(name, size)
    return findings


def uncomma(text):
    return int(text.replace(",", ""))


def identified_share():
    path = os.path.join(ROOT, "docs", "research", "RESIDUAL_LEDGER.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="", encoding="utf-8") as handle:
        identified = sum(int(row["bytes"]) for row in csv.DictReader(handle)
                         if row["status"] == "identified binary")
    sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
    import gate
    return "%.4f" % (100.0 * identified / gate.ROM_SIZE), identified


def readme_numbers_findings(text, built, total, percent, rows, identified=None):
    findings = []
    percents = README_PERCENT.findall(text)
    allowed = [percent] + ([identified[0]] if identified is not None else [])
    spans = README_BYTES.findall(text)
    counts = README_ROWS.findall(text)
    for value, wanted in [(percent, 1)] + ([(identified[0], 1)] if identified is not None else []):
        found = percents.count(value)
        if found != wanted:
            findings.append(("README-numbers",
                             "README.md: %s %% expected exactly %d time(s), found %d"
                             % (value, wanted, found)))
    if identified is not None:
        figures = README_IDENTIFIED.findall(text)
        if len(figures) != 1:
            findings.append(("README-numbers",
                             "README.md: one '<percent> %% is identified binary (<bytes> B' figure "
                             "expected, found %d" % len(figures)))
        for listed, size in figures:
            if (listed, uncomma(size)) != identified:
                findings.append(("README-numbers",
                                 "README.md: identified binary reads %s %% / %s B, not the ledger's "
                                 "%s %% / %d B" % (listed, size, identified[0], identified[1])))
    if len(spans) != 1:
        findings.append(("README-numbers",
                         "README.md: one <built> of <size> bytes span expected, found %d"
                         % len(spans)))
    if len(counts) > 1:
        findings.append(("README-numbers",
                         "README.md: at most one <rows> ledger rows count expected, found %d"
                         % len(counts)))
    if README_COMMAND.search(text) is None:
        findings.append(("README-numbers",
                         "README.md: the progress line must name the command that prints it: "
                         "python tools\\gate\\gate.py"))
    for listed in percents:
        if listed not in allowed:
            findings.append(("README-numbers",
                             "README.md: %s %% is neither the gate's %s %%%s"
                             % (listed, percent, "" if identified is None else
                                " nor the ledger's identified-binary %s %%" % identified[0])))
    for first, second in spans:
        if (uncomma(first), uncomma(second)) != (built, total):
            findings.append(("README-numbers",
                             "README.md: %s of %s bytes is not the gate's %d of %d bytes"
                             % (first, second, built, total)))
    for listed in counts:
        if uncomma(listed) != rows:
            findings.append(("README-numbers",
                             "README.md: %s ledger rows is not work/ledger.csv's %d" % (listed, rows)))
    return findings


def readme_findings():
    text = read_source("README.md")
    if text is None:
        return [("README-numbers", "README.md: cannot be read")]
    sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
    import gate
    built = gate.source_bytes()
    return readme_numbers_findings(text, built, gate.ROM_SIZE,
                                   "%.4f" % (100.0 * built / gate.ROM_SIZE),
                                   len(gate.ledger_rows()), identified_share())


def stale_call_findings(text, named):
    findings = []
    for match in STALE_CALL.finditer(text):
        start, end = int(match.group(1), 16), int(match.group(2), 16)
        if (start, end - start) not in named:
            findings.append(("P-518-stale-incbin-call",
                             "rebuild.cmd:%d: %s names a slice no asm/*.s INCBINs"
                             % (line_of(text, match.start()), match.group(0))))
    return findings


def stale_call_tree_findings():
    text = read_source("rebuild.cmd")
    if text is None:
        return [("P-518-stale-incbin-call", "rebuild.cmd: cannot be read")]
    sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
    import gate
    return stale_call_findings(text, set(gate.incbin_ranges()))


def normalised_lines(name, text):
    rows = python_lines(text) if name.endswith(".py") else c_lines(text)
    return [(number, line) for number, line in rows
            if line and DUP_IMPORT_LINE.match(line) is None]


def python_lines(text):
    out = {}
    strings = set()
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return c_lines(text)
    for token in tokens:
        if token.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                          tokenize.DEDENT, tokenize.ENDMARKER):
            continue
        if token.start[0] != token.end[0]:
            continue
        out.setdefault(token.start[0], []).append(token.string)
        if token.type == tokenize.STRING:
            strings.add(token.start[0])
    return [(number, " ".join(parts)) for number, parts in sorted(out.items())
            if len(parts) > 1 or number not in strings]


def c_lines(text):
    out = []
    index = 0
    while index < len(text):
        if text[index] in "\"'":
            end = index + 1
            while end < len(text) and text[end] != text[index]:
                end += 2 if text[end] == "\\" else 1
            end = min(end + 1, len(text))
            out.append(text[index:end])
            index = end
        elif text.startswith("//", index):
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            out.append(" " * (end - index))
            index = end
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)
            end = len(text) if end < 0 else end + 2
            out.append("".join("\n" if letter == "\n" else " " for letter in text[index:end]))
            index = end
        else:
            out.append(text[index])
            index += 1
    text = "".join(out)
    return [(number, " ".join(line.split())) for number, line in enumerate(text.splitlines(), 1)]


def dup_scan_files():
    proc = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                          cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        return None
    keep = []
    for name in proc.stdout.decode("utf-8", "replace").split("\0"):
        path = name.replace("\\", "/")
        if path.startswith(DUP_PYTHON_ROOT) and path.endswith(".py"):
            keep.append(name)
        elif path.startswith(DUP_C_ROOTS) and path.endswith((".c", ".h")):
            keep.append(name)
    return sorted(keep)


def duplicate_blocks(names):
    lines = {}
    index = {}
    for name in names:
        text = read_source(name)
        lines[name] = [] if text is None else normalised_lines(name, text)
        for position in range(len(lines[name]) - DUP_MINIMUM + 1):
            key = tuple(text for _, text in lines[name][position:position + DUP_MINIMUM])
            index.setdefault(key, []).append((name, position))
    found = []
    for key in sorted(index):
        places = index[key]
        if len(places) < 2:
            continue
        first = places[0]
        for other in places[1:]:
            if same_before(lines, first, other):
                continue
            found.append((site_of(lines, first), site_of(lines, other),
                          run_length(lines, first, other)))
    return found


def site_of(lines, place):
    name, position = place
    return name, lines[name][position][0]


def same_before(lines, first, other):
    if not first[1] or not other[1]:
        return False
    return lines[first[0]][first[1] - 1][1] == lines[other[0]][other[1] - 1][1]


def run_length(lines, first, other):
    length = DUP_MINIMUM
    while (first[1] + length < len(lines[first[0]])
           and other[1] + length < len(lines[other[0]])
           and lines[first[0]][first[1] + length][1] == lines[other[0]][other[1] + length][1]):
        length += 1
    return length


def dup_allowed(first, second):
    for entry in DUP_ALLOWLIST:
        if ((entry[0], entry[1]), (entry[2], entry[3])) in ((first, second), (second, first)):
            return True
    return False


def dup_block_findings(names=None):
    if names is None:
        names = dup_scan_files()
        if names is None:
            return [("lint-enumeration",
                     "git ls-files failed, the duplicate check cannot see the tree")]
    findings = []
    for first, second, length in duplicate_blocks(names):
        if dup_allowed(first, second):
            continue
        findings.append(("DUP-block", "%s:%d and %s:%d: %d identical lines"
                         % (first[0], first[1], second[0], second[1], length)))
    return findings


def silent_return_findings(name, text):
    if TEST_FILE.match(os.path.basename(name)) is None:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [("TEST-silent-return", "%s:%d: cannot be parsed: %s" % (name, exc.lineno, exc.msg))]
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        for line in returns_in(node.body):
            findings.append(("TEST-silent-return",
                             "%s:%d: %s returns instead of asserting, skipping or failing"
                             % (name, line, node.name)))
    return sorted(findings, key=lambda finding: finding[1])


def returns_in(body, checked=False):
    found = []
    for statement in body:
        if isinstance(statement, ast.Return):
            if not checked:
                found.append(statement.lineno)
            continue
        for nested in nested_bodies(statement):
            found += returns_in(nested, checked)
        checked = checked or checks_or_refuses(statement)
    return sorted(found)


def nested_bodies(statement):
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
        return []
    bodies = []
    for field in ("body", "orelse", "finalbody"):
        value = getattr(statement, field, None)
        if isinstance(value, list):
            bodies.append(value)
    bodies += [handler.body for handler in getattr(statement, "handlers", [])]
    bodies += [case.body for case in getattr(statement, "cases", [])]
    return bodies


def checks_or_refuses(statement):
    if isinstance(statement, (ast.Assert, ast.Raise)):
        return True
    if not (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)):
        return False
    function = statement.value.func
    return (isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name)
            and function.value.id == "pytest" and function.attr in ("skip", "fail", "xfail"))


def run(files=None):
    whole_tree = files is None
    if whole_tree:
        files = source_files()
        if files is None:
            return [("lint-enumeration", "git ls-files failed, the lints cannot see the tree")]
    findings = []
    for name in files:
        path = name if os.path.isabs(name) else os.path.join(ROOT, name)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            findings.append(("lint-read", "%s: %s" % (name, exc)))
            continue
        findings += bare_interpreter(name, text)
        if name.endswith(".py"):
            findings += pool_without_guard(name, text)
            findings += out_of_repo_module_path(name, text)
        findings += silent_return_findings(name, text)
    if whole_tree:
        findings += c_source_findings()
        findings += tracked_rom_findings()
        findings += readme_findings()
        findings += stale_call_tree_findings()
        findings += dup_block_findings()
    else:
        findings += dup_block_findings(files)
    return findings


def main(argv=None):
    files = list(argv) if argv else None
    findings = run(files)
    for name, detail in findings:
        print("LINT FAIL %s: %s" % (name, detail))
    print("LINT %s: %d finding(s) over %d file(s)"
          % ("FAIL" if findings else "PASS", len(findings),
             len(files) if files else len(source_files() or [])))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
