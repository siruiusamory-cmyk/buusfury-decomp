from __future__ import annotations

import os
import re
import sys

LINK = re.compile(r"\]\(\s*<?([^)>\s]+)>?\s*\)")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
CITATION = re.compile(
    r"(?i)\b(master|commit|merged|merge|merges|base|baseline|branch|revision|tagged|frozen|"
    r"landed|tip|stacked|worktree|checkout|head)\b[^\n0-9a-f]{0,10}([0-9a-f]{7,40})\b")
LABEL = re.compile(r"sha1|sha256", re.I)
SKIP_DIRS = {".git", "build", "node_modules", "__pycache__", ".pytest_cache"}


def markdown_files(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name.lower().endswith(".md"):
                yield os.path.join(base, name)


def exact_path(root, directory, target):
    if target.startswith("/"):
        directory, target = "", target.lstrip("/")
    relative = "/".join(part for part in (directory, target) if part)
    current = root
    for part in relative.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if current == root:
                return False
            current = os.path.dirname(current)
            continue
        try:
            names = os.listdir(current)
        except OSError:
            return False
        if part not in names:
            return False
        current = os.path.join(current, part)
    return True


def findings(root):
    root = os.path.abspath(root)
    found = []
    for path in markdown_files(root):
        relative = os.path.relpath(path, root).replace(os.sep, "/")
        previous = ""
        for number, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
            for match in LINK.finditer(line):
                target = match.group(1)
                if SCHEME.match(target) or target.startswith("#") or target == "":
                    continue
                target = target.split("#")[0]
                if not exact_path(root, os.path.dirname(relative), target):
                    found.append("%s:%d: link does not resolve: %s" % (relative, number, target))
            if not LABEL.search(line) and not LABEL.search(previous):
                match = CITATION.search(line)
                if match:
                    found.append("%s:%d: commit SHA cited: %s" % (relative, number, match.group(2)))
            previous = line
    return found


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    here = os.path.dirname(os.path.abspath(__file__))
    root = argv[0] if argv else os.path.dirname(here)
    found = findings(root)
    for item in found:
        print(item)
    print("check_links: %d finding(s)" % len(found))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
