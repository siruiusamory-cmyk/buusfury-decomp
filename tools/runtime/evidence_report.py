"""Offline inspection of one runtime evidence bundle: read, verify, print.

The bundle is written by a probe at capture time
(``tools/runtime/evidence_bundle.py``) and is the only input here, so a capture
can be inspected on a machine with no emulator, no ROM and no build tree.

What the report states, and nothing more:

- which ROM the bundle recorded, and whether that file's bytes still match the
  digest it recorded;
- which emulator executable, digest, build class and label it recorded, and
  whether that file still matches;
- which probe produced the run, and with what arguments;
- the repository revision and dirty flag the probe measured;
- the recorded observations, printed as recorded;
- for every referenced artifact, whether it is still present and still matches.

A field the bundle does not carry is printed as ``absent``. It is never filled
from a default, a filename, or a version string: once printed, an inference and
a measurement look the same. A malformed, unsupported or incomplete bundle is
refused with exit status 2 and a message naming the problem, and
``read_bundle`` owns that validation - this module does not keep a second
schema.

Nothing here creates a process. The report is a pure function of bytes on disk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.mgba_probe.runtime import sha256 as file_sha256
from tools.runtime.evidence_bundle import read_bundle

#: Printed for any field the bundle does not carry. The exact word matters: a
#: blank, a zero or a plausible version would read as a measurement.
ABSENT = "absent"

MATCHES = "present, bytes match the recorded digest"
DIFFERS = "present, bytes DO NOT match the recorded digest"
UNRECORDED = "present, digest not recorded"

USAGE = "usage: python -m tools.runtime.evidence_report <bundle path>"


def _lookup(container: object, key: str) -> Any:
    """The raw recorded value, or None when the container does not carry it."""
    if isinstance(container, Mapping) and key in container:
        return container[key]
    return None


def _show(container: object, key: str) -> str:
    """A recorded value as text, or ``absent`` when there is no value there."""
    value = _lookup(container, key)
    if value is None:
        return ABSENT
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _file_lines(
    path_text: object, recorded_sha256: object, *, indent: str = "  "
) -> list[str]:
    """Existence and digest verdict for one referenced file, measured now."""
    if not isinstance(path_text, str) or not path_text:
        return [f"{indent}file: {ABSENT} (the bundle records no path)"]
    path = Path(path_text)
    if not path.is_file():
        return [f"{indent}file: {ABSENT}"]
    observed = file_sha256(path)
    if recorded_sha256 is None:
        # No recorded digest - absent key or explicit null - means unknown. The
        # bytes are stated as an observation and no match is claimed in either
        # direction: there is nothing for them to match, or fail to match.
        return [f"{indent}file: {UNRECORDED}", f"{indent}observed sha256: {observed}"]
    if observed.upper() == str(recorded_sha256).upper():
        return [f"{indent}file: {MATCHES}"]
    return [f"{indent}file: {DIFFERS}", f"{indent}observed sha256: {observed}"]


def _identity_lines(title: str, entry: object, extra_keys: Sequence[str]) -> list[str]:
    """One recorded file identity: its fields, then its current verdict."""
    lines = [f"{title}: {_show(entry, 'path')}"]
    lines.append(f"  recorded sha256: {_show(entry, 'sha256')}")
    lines.append(f"  recorded bytes: {_show(entry, 'bytes')}")
    for key in extra_keys:
        lines.append(f"  recorded {key}: {_show(entry, key)}")
    lines.extend(_file_lines(_lookup(entry, "path"), _lookup(entry, "sha256")))
    return lines


def build_report(bundle_path: Path | str) -> str:
    """Read and validate one bundle, and describe it without reinterpreting it."""
    bundle = read_bundle(Path(bundle_path))
    lines = [
        f"bundle: {Path(bundle_path)}",
        f"schema: {_show(bundle, 'schema')}",
        f"run_id: {_show(bundle, 'run_id')}",
        f"created_utc: {_show(bundle, 'created_utc')}",
    ]

    repository = _lookup(bundle, "repository")
    lines.append(
        "repository: sha="
        f"{_show(repository, 'sha')} dirty={_show(repository, 'dirty')}"
    )

    probe = _lookup(bundle, "probe")
    lines.append(f"probe: tool={_show(probe, 'tool')}")
    lines.append(f"probe arguments: {_show(probe, 'arguments')}")

    lines.extend(_identity_lines("rom", _lookup(bundle, "rom"), ()))
    lines.extend(
        _identity_lines(
            "emulator",
            _lookup(bundle, "emulator"),
            ("build_class", "label", "file_version", "instrumented"),
        )
    )

    lines.append("observations:")
    observations = _lookup(bundle, "observations")
    if isinstance(observations, Mapping) and observations:
        for key in sorted(observations, key=str):
            lines.append(f"  {key}: {_show(observations, str(key))}")
    else:
        lines.append("  none recorded")

    artifacts = _lookup(bundle, "artifacts")
    entries = artifacts if isinstance(artifacts, list) else []
    lines.append(f"artifacts: {len(entries)}")
    for entry in entries:
        lines.append(f"  {_show(entry, 'path')} role={_show(entry, 'role')}")
        lines.append(f"    recorded sha256: {_show(entry, 'sha256')}")
        lines.append(f"    recorded bytes: {_show(entry, 'bytes')}")
        lines.extend(
            _file_lines(
                _lookup(entry, "path"), _lookup(entry, "sha256"), indent="    "
            )
        )

    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    """Print the report for one bundle path; 0 on success, 2 on any refusal."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        report = build_report(arguments[0])
    except (ValueError, TypeError, KeyError, OSError) as problem:
        print(f"refused: {arguments[0]}: {problem}", file=sys.stderr)
        return 2
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
