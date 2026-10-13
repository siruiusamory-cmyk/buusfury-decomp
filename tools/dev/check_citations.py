"""Check `path:line` citations in ticket, debt and ledger prose against the tree.

The class this exists for is measured drift (dbz-dev retro 1.2): a debt node cited
`journal.py:662-664` for a site that had moved to `:702`, the reconciliation
ledger's CQA-27 row cited three line numbers in a file that has since grown, and
every one of those was re-derived by hand, twice by an independent reviewer.

The three answers, and how each is earned:

* `RESOLVES` - the path exists, the line (or range) is inside the file, and a
  symbol named beside the citation is on that line.
* `MOVED` - the named symbol is not on the cited line but is in the file, and the
  report carries its new line. A moved citation is drift you can fix from the
  output, not a guess: `MOVED` is only ever earned by finding the symbol.
* `ORPHAN` - the file does not exist at that path, the line is past the end of the
  file, or the named symbol is nowhere in the file.

It takes an explicit target, always. There is no whole-tree default, because a
checker that scans `docs/` unbidden is noise.

    python -m tools.dev.check_citations docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md
    python -m tools.dev.check_citations --fail-on-orphan path/to/prose.md

Exit codes: 0 when every citation resolves or moves, 1 with `--fail-on-orphan` when
any is an orphan. Without the flag it always exits 0, because printing the drift is
the job and the caller decides whether a moved citation blocks a freeze.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: `path/to/file.ext:12` or `path/to/file.ext:12-14`. The path must contain a dot
#: or a slash so that prose like `map:19` is not read as a citation.
CITATION = re.compile(
    r"(?P<path>[A-Za-z0-9_][A-Za-z0-9_./\\-]*\.[A-Za-z0-9_]+)"
    r":(?P<start>\d+)(?:\s*[-\u2013]\s*(?P<end>\d+))?"
)

#: A backticked token that is a name this can search for. A bare word in backticks
#: ("Merged", "SUPERSEDED", a commit sha) is prose about the citation, not a symbol
#: in the file, and reading it as one invented three false findings in the first
#: measurement. Prose goes unmarked, which the report says out loud: a citation with
#: no name beside it costs nothing when the file grows, because no symbol can move.
SYMBOL = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")

#: What a nameable site looks like in this repository's prose: an underscore or an
#: inner capital is the marker, so `_saved`, `unsaved_edit_count`, `open_rom` and
#: `_repaint_project_state` all count and `Merged`, `none` and `appearance` do not.
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]+$|^[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*$")

#: Window after a citation in which a named symbol belongs to it. Short on
#: purpose: a wider one reaches into the next sentence and reads its identifier as
#: this citation's symbol, which reported `validate` for `cli.py:520` where the
#: document names nothing at all.
SYMBOL_WINDOW = 60


def resolve(path_text: str, anchor: Path, root: Path) -> Path | None:
    """Resolve a citation path against the repository root, then the document."""
    candidate = Path(path_text.replace("\\", "/"))
    for base in (root, anchor, root / "tools" / "webfoot" / "workbench"):
        resolved = (base / candidate) if not candidate.is_absolute() else candidate
        if resolved.is_file():
            return resolved
    # A document often cites a bare filename; find it under the repository once.
    matches = sorted(root.rglob(candidate.name))
    return matches[0] if len(matches) == 1 else None


def named_symbol(text: str, match: re.Match) -> str | None:
    """The identifier the citation is talking about, if one is named beside it."""
    window = text[match.end() : match.end() + SYMBOL_WINDOW]
    for found in SYMBOL.finditer(window):
        token = found.group(1)
        if IDENTIFIER.match(token):
            return token
    return None


def check(text: str, anchor: Path, root: Path | None = None) -> list[dict]:
    root = root or REPOSITORY_ROOT
    findings: list[dict] = []
    for match in CITATION.finditer(text):
        path_text = match.group("path")
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        target = resolve(path_text, anchor, root)
        if target is None:
            findings.append({"citation": match.group(0), "state": "ORPHAN", "why": "no such file"})
            continue
        body = target.read_text(encoding="utf-8", errors="replace").splitlines()
        if start > len(body):
            findings.append(
                {
                    "citation": match.group(0),
                    "state": "ORPHAN",
                    "why": f"line {start} is past the end of {target.name} ({len(body)} lines)",
                }
            )
            continue
        symbol = named_symbol(text, match)
        if symbol is None:
            findings.append(
                {
                    "citation": match.group(0),
                    "state": "RESOLVES",
                    "why": f"{target} line {start} exists (no symbol named to check)",
                }
            )
            continue
        cited = "\n".join(body[start - 1 : end])
        if symbol in cited:
            findings.append(
                {"citation": match.group(0), "state": "RESOLVES", "why": f"`{symbol}` is at {start}"}
            )
            continue
        hits = [number for number, line in enumerate(body, 1) if symbol in line]
        if hits:
            findings.append(
                {
                    "citation": match.group(0),
                    "state": "MOVED",
                    "why": f"`{symbol}` is at {', '.join(str(h) for h in hits[:8])}, not {start}",
                }
            )
        else:
            findings.append(
                {
                    "citation": match.group(0),
                    "state": "ORPHAN",
                    "why": f"`{symbol}` is nowhere in {target.name}",
                }
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="+", help="files or directories to check")
    parser.add_argument(
        "--fail-on-orphan",
        action="store_true",
        help="exit non-zero when any citation is an ORPHAN",
    )
    parser.add_argument("--quiet", action="store_true", help="print only MOVED and ORPHAN")
    args = parser.parse_args(argv)

    documents: list[Path] = []
    for target in args.targets:
        path = Path(target)
        if path.is_dir():
            documents.extend(sorted(p for p in path.rglob("*") if p.suffix in {".md", ".txt"}))
        elif path.is_file():
            documents.append(path)
        else:
            print(f"no such target: {target}", file=sys.stderr)
            return 2

    counts = {"RESOLVES": 0, "MOVED": 0, "ORPHAN": 0}
    for document in documents:
        findings = check(document.read_text(encoding="utf-8", errors="replace"), document)
        if not findings:
            continue
        print(f"{document}")
        for finding in findings:
            counts[finding["state"]] += 1
            if args.quiet and finding["state"] == "RESOLVES":
                continue
            print(f"  {finding['state']:<9} {finding['citation']}  {finding['why']}")

    print(
        f"\n{counts['RESOLVES']} RESOLVES, {counts['MOVED']} MOVED, "
        f"{counts['ORPHAN']} ORPHAN in {len(documents)} document(s)"
    )
    if args.fail_on_orphan and counts["ORPHAN"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
