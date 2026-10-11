"""Release 4: collapse the interior double spaces the rename pass left.

WHY THE STREAM IS REBUILT AND NOT THE RECORD. The dialogue containers are
chain-shared: one record's bytes are read by every longer record covering them.
An edit inside a record's own span is therefore read by all of them, and paying a
shorter text back as trailing spaces inside that span re-creates the run in a
covering record. That was measured on 2026-10-10 (pitfall P-023): 118 runs
collapsed, the corpus total barely moved. This builder collapses the run in the
DECODED STREAM instead, so every view loses it at once, and rewrites every handle
word that the deletion moved. No record keeps a length it paid for, so no payback
space exists to re-create a run.

WHAT IS KEPT. A run survives where the canonical image's record at the same
identity carries a 2+ space run at the same unit offset. That is retail spacing,
not a rename artifact, and it is the only spacing this pass preserves.

WHAT IS NOT TOUCHED. Every non-space character of every record is unchanged by
construction (only 0x0020 units are removed), and the edit writes only inside the
seven dialogue containers and at the handle words that name those records. The
stat table, the sprite and portrait containers and every other byte of the image
are outside both ranges, which the verifier proves independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot import textedit  # noqa: E402


class Release4SpacingError(ValueError):
    """The build refused rather than writing a byte it could not verify."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--canonical", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    source = Path(args.image)
    image = source.read_bytes()
    got = sha256_bytes(image)
    if got != args.expect_sha256.lower():
        raise Release4SpacingError(
            f"REFUSED: {source} is {got}, expected {args.expect_sha256.lower()}")

    model = textedit.open_rom(source, canonical=Path(args.canonical))
    built = textedit.plan(model, [textedit.SpacingEdit()])
    refusals = built.refusals
    if refusals:
        raise Release4SpacingError("REFUSED: " + "; ".join(
            f"{item.target}: {item.reason}" for item in refusals))

    document = {
        "release": "release-4-spacing",
        "input": str(source),
        "input_sha256": got,
        "input_bytes": len(image),
        "canonical": str(args.canonical),
        "canonical_sha256": model.retail_sha256,
        "records": len(model.records),
        "rows": [],
        "warnings": list(built.warnings),
        "kept_retail_runs": [],
        "deleted_units": 0,
        "handle_words_rewritten": 0,
        "output_bytes": None,
        "output_sha256": None,
    }
    for row in built.spacing:
        document["rows"].append({
            "selector": row.selector,
            "payload_before": len(model.layout.streams[row.selector]),
            "payload_after": len(model.layout.streams[row.selector]) - 2 * len(row.deleted),
            "deleted_units": len(row.deleted),
            "handle_words_rewritten": len(row.handles),
            "kept_retail_runs": list(row.kept_retail),
        })
        document["deleted_units"] += len(row.deleted)
        document["handle_words_rewritten"] += len(row.handles)
        document["kept_retail_runs"].extend(row.kept_retail)

    report = textedit.apply(built, Path(args.out))
    document["output"] = report["output"]
    document["output_sha256"] = report["output_sha256"]
    document["output_bytes"] = report["output_bytes"]
    document["changed_ranges"] = len(built.changes)
    Path(args.manifest).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    for row in document["rows"]:
        print(f"  selector {row['selector']}: {row['payload_before']} -> "
              f"{row['payload_after']} bytes, {row['deleted_units']} unit(s) deleted, "
              f"{row['handle_words_rewritten']} handle word(s), "
              f"{len(row['kept_retail_runs'])} retail run(s) kept")
    for warning in built.warnings:
        print(f"  {warning}")
    print(f"# {len(model.records)} record(s) read back; {document['deleted_units']} interior "
          f"space unit(s) removed; {document['handle_words_rewritten']} handle word(s) rewritten")
    print(f"# wrote {report['output']} {report['output_bytes']} bytes "
          f"sha256 {report['output_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
