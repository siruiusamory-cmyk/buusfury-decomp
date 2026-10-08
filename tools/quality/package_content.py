"""Portable census of a staged package: what travels, and what must not.

A release is a directory of files that a stranger receives. Before DragonByte Z or
a randomizer is packaged, one question has to be answerable without a Windows
runner and without the commercial image: *what is in this thing, and is any of it
something that may not leave the machine that built it?* This module answers that
from the staged files alone, so it runs on any platform, in CI, and against a
directory a release engineer points it at.

What is deliberately NOT repeated here
--------------------------------------

Three neighbouring checks already own their ground:

* the static release DEFINITION (spec template, version resource, icon, the
  two-file package shape, ROM-free inputs) is ``tools/quality/public_release.py``,
  and this module imports its forbidden-suffix list rather than keeping a second
  one that could disagree with it;
* the tree-wide machine-path and user-name screens are
  ``tools/quality/public_surface.py``, reused here with its exception table intact;
* the byte probe that searches a built executable for the canonical image's bytes
  is ``scripts/randomizer-release.ps1``, which needs the ROM and therefore cannot
  run where this can.

What is left, and what this module does, is the artefact census itself.

The limit of the method, stated in the report it produces
---------------------------------------------------------

A PyInstaller executable is one compressed file. This census cannot enumerate what
travels inside it, so "no finding" here is not the claim "this package contains no
private content"; it is the claim "every file in this directory was examined, and
nothing examined is a ROM, a save, a machine path or a user name". The two checks
together are what make the release claim, which is why the limitation is printed
with the result rather than left to a reader to remember.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys

from tools.quality import public_surface
from tools.quality.public_release import FORBIDDEN_SUFFIXES, RELEASE_RESIDUE

#: Bumped when the report document's shape changes in a way a reader must notice.
SCHEMA = 1

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXCEPTIONS_FILE = "config/public_surface_exceptions.json"

#: What this check cannot see. Printed with every report, including a clean one.
LIMITATIONS: tuple[str, ...] = (
    "a file is searched only when it decodes as UTF-8; anything else is counted as "
    "binary and left unsearched",
    "the members of a compressed PyInstaller executable are not enumerated here, so "
    "a clean census is not a statement that the executable is free of private bytes",
    "only the files present are examined: a resource that never reached the staging "
    "directory is reported only when it was named as required",
)


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    path: str
    detail: str
    line: int = 0

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "path": self.path,
            "line": self.line,
            "detail": self.detail,
        }


def _read_text(path: Path) -> str | None:
    """The file's text, or None when it is not readable UTF-8 text."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def census(
    directory: Path | str,
    *,
    required: tuple[str, ...] | list[str] = (),
    exceptions: public_surface.ExceptionTable | None = None,
) -> dict:
    """Every finding for one staged package directory.

    ``required`` names files the package cannot work without. A missing one is a
    finding, because an artifact that would fail on the user's machine the moment
    they open a project should fail here instead.

    A file that cannot be read at all is reported separately from a finding, for
    the same reason the other gates do it: a check that could not run is not a
    check that passed.
    """
    root = Path(directory)
    table = exceptions or public_surface.ExceptionTable.load(
        REPOSITORY_ROOT / EXCEPTIONS_FILE
    )
    findings: list[Finding] = []
    unreadable: list[str] = []
    binary = 0
    text_files = 0
    forbidden = 0
    total_bytes = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        try:
            size = path.stat().st_size
        except OSError:
            unreadable.append(relative)
            continue
        total_bytes += size

        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(
                Finding(
                    "forbidden-artifact",
                    relative,
                    f"{path.suffix.lower()} is a ROM, save or save state and cannot "
                    "travel in a release",
                )
            )
            # Counted, not searched: the suffix is the finding, and reading eight
            # megabytes of it as text to hunt for a machine path would find nothing
            # the suffix has not already said.
            forbidden += 1
            continue

        text = _read_text(path)
        if text is None:
            binary += 1
            continue
        text_files += 1
        for number, line in enumerate(text.splitlines(), 1):
            for label, pattern in RELEASE_RESIDUE:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            "private-path-residue",
                            relative,
                            f"{label}: {line.strip()[:120]}",
                            number,
                        )
                    )
        shared, _ = public_surface.scan(
            relative=relative, exceptions=table, text=text
        )
        for item in shared:
            findings.append(
                Finding(
                    "private-path-residue",
                    relative,
                    f"{item['signal']}: {item['text'][:120]}",
                    item["line"],
                )
            )

    for name in required:
        if not (root / name).is_file():
            findings.append(
                Finding(
                    "required-resource-missing",
                    name,
                    "the package declares this file and it is not staged",
                )
            )

    findings.sort(key=lambda item: (item.path, item.line, item.code))
    counts: dict[str, int] = {}
    for item in findings:
        counts[item.code] = counts.get(item.code, 0) + 1
    return {
        "schema": SCHEMA,
        "directory": root.name,
        "files": text_files + binary + forbidden,
        "text_files": text_files,
        "binary_files": binary,
        "forbidden_files": forbidden,
        "bytes": total_bytes,
        "required": sorted(required),
        "unreadable": sorted(set(unreadable)),
        "findings": [item.as_dict() for item in findings],
        "code_counts": dict(sorted(counts.items())),
        "limitations": list(LIMITATIONS),
    }


def _render(report: dict, stream) -> None:
    print(
        f"package content: {report['files']} file(s) in {report['directory']!r}, "
        f"{report['bytes']} byte(s), {len(report['findings'])} finding(s)",
        file=stream,
    )
    for item in report["findings"]:
        where = f"{item['path']}:{item['line']}" if item["line"] else item["path"]
        print(f"  {where}: {item['code']}: {item['detail']}", file=stream)
    for relative in report["unreadable"]:
        print(f"  {relative}: package-file-unreadable", file=stream)
    print("this census cannot see inside a compressed executable:", file=stream)
    for statement in report["limitations"]:
        print(f"  - {statement}", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="package-content",
        description=(
            "Census a staged package directory: the files it holds, any ROM, save "
            "or save state, any machine path or user name, and any declared "
            "resource that is missing."
        ),
    )
    parser.add_argument("directory", type=Path, help="the staged package directory")
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="NAME",
        help="a file the package cannot work without; repeatable",
    )
    parser.add_argument("--json", metavar="PATH", help="write the report as JSON")
    parser.add_argument(
        "--no-fail", action="store_true", help="report findings but always exit 0"
    )
    arguments = parser.parse_args(argv)

    if not arguments.directory.is_dir():
        print(f"BLOCKED: {arguments.directory} is not a directory", file=sys.stderr)
        return 2

    try:
        report = census(arguments.directory, required=tuple(arguments.require))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2

    if arguments.json:
        Path(arguments.json).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    _render(report, sys.stdout)

    if report["unreadable"]:
        print(
            "\nSome package files could not be read, so they were not examined. "
            "A file that cannot be read is not a file that passed.",
            file=sys.stderr,
        )
        return 2
    if report["findings"] and not arguments.no_fail:
        print(
            "\nThis package does not meet the release rules. Fix the staging step, "
            "or extend this module deliberately.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
