"""Swap a character's sprites or portrait, or rewrite spoken lines, in a friend image.

ONE COMMAND, ONE SPEC. This is the invocable front end for the friend chain's two edits, so a
later swap does not need a new script. Both engines are pure (bytes in, bytes out); this module
owns the file system, which is where the two rules that must not be duplicated live:

* the source is an input on every path and an output on none, checked by file identity before
  anything is read, so a hard link of the image cannot be written through;
* an image and a report are staged into sibling temporary files and renamed into place, so a
  reader never sees a partial write.

SPEC. A JSON document, relative to which any asset name resolves against the spec file's own
directory::

    {
      "operations": [
        {"kind": "sprite", "sprite_id": 41,
         "slots": [{"slot": 0, "sheet": "stand.png", "frames": 2},
                   {"slot": 1, "sheet": "walk.png", "frames": 4}],
         "frame": [16, 32], "cell": 32, "crop_x": 8,
         "anchor": [0, -24], "composition_size": 512},
        {"kind": "portrait", "slot": 17, "png": "portrait.png", "side": 64},
        {"kind": "dialogue", "selector": 2,
         "lines": [{"speaker": "tulma",
                    "old": "the wording the record holds now",
                    "new": "the wording to write",
                    "record": [60182, 112]}]}
      ]
    }

``frame``, ``cell``, ``crop_x``, ``anchor`` and ``composition_size`` are optional and default to
the geometry every donor measured so far uses. A dialogue ``record`` is optional: the line is
found by its wording, and that wording must match exactly one record, or the run is refused.
The ``speaker`` is the caller's claim about who says the line, recorded in the report and
labelled as a claim, never inferred from the wording, a label or a position.

ORDER. Every sprite and portrait operation is applied in one pass; dialogue operations are
applied afterwards in spec order. Each pass proves its own diff confinement, so disjoint
regions make the final bytes independent of that order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from tools.webfoot.dialogue_edit import DialogueRewrite, LineEdit, rewrite_dialogue
from tools.webfoot.sprite_swap import (DONOR_GEOMETRY, PortraitSwap, SheetSlot, SpriteGeometry,
                                       SpriteSwap, swap)
from tools.webfoot.write import WriteError, ensure_not_source_alias


class SwapSpecError(ValueError):
    """Raised when a spec cannot be read as an instruction rather than guessed at."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_staged(path: Path, data: bytes) -> None:
    """Write through a sibling temporary file, then rename, so a partial is never visible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".",
                                     suffix=".partial", delete=False) as handle:
        staged = Path(handle.name)
        try:
            handle.write(data)
        except BaseException:
            handle.close()
            staged.unlink(missing_ok=True)
            raise
    staged.replace(path)


def _geometry(entry: dict[str, Any]) -> SpriteGeometry:
    frame = entry.get("frame", [DONOR_GEOMETRY.frame_width, DONOR_GEOMETRY.frame_height])
    anchor = entry.get("anchor", list(DONOR_GEOMETRY.frame_anchor))
    if len(frame) != 2 or len(anchor) != 2:
        raise SwapSpecError(f"frame and anchor are [width, height] and [x, y]: {entry!r}")
    return SpriteGeometry(frame_width=int(frame[0]), frame_height=int(frame[1]),
                          cell_side=int(entry.get("cell", DONOR_GEOMETRY.cell_side)),
                          crop_x=int(entry.get("crop_x", DONOR_GEOMETRY.crop_x)),
                          frame_anchor=(int(anchor[0]), int(anchor[1])),
                          composition_size=int(entry.get("composition_size",
                                                         DONOR_GEOMETRY.composition_size)))


def parse_spec(document: dict[str, Any]) -> tuple[tuple[SpriteSwap, ...],
                                                  tuple[PortraitSwap, ...],
                                                  tuple[DialogueRewrite, ...]]:
    """Read the operations, refusing anything that would have to be guessed at."""
    operations = document.get("operations")
    if not isinstance(operations, list) or not operations:
        raise SwapSpecError("the spec needs a non-empty 'operations' list")
    sprites: list[SpriteSwap] = []
    portraits: list[PortraitSwap] = []
    rewrites: list[DialogueRewrite] = []
    for index, entry in enumerate(operations):
        kind = entry.get("kind")
        if kind == "sprite":
            slots = entry.get("slots")
            if not isinstance(slots, list) or not slots:
                raise SwapSpecError(f"operation {index}: a sprite needs a non-empty 'slots'")
            sprites.append(SpriteSwap(
                sprite_id=int(entry["sprite_id"]),
                slots=tuple(SheetSlot(int(slot["slot"]), str(slot["sheet"]),
                                      int(slot["frames"])) for slot in slots),
                geometry=_geometry(entry)))
        elif kind == "portrait":
            portraits.append(PortraitSwap(slot=int(entry["slot"]), png=str(entry["png"]),
                                          side=int(entry.get("side", 64))))
        elif kind == "dialogue":
            lines = entry.get("lines")
            if not isinstance(lines, list) or not lines:
                raise SwapSpecError(f"operation {index}: a dialogue edit needs 'lines'")
            edits = []
            for line in lines:
                record = line.get("record")
                if record is not None and len(record) != 2:
                    raise SwapSpecError(
                        f"operation {index}: 'record' is [decoded start, decoded length]")
                edits.append(LineEdit(
                    speaker=str(line.get("speaker", "unstated")),
                    old_text=str(line["old"]),
                    new_text=str(line["new"]),
                    decoded_start=None if record is None else int(record[0]),
                    decoded_length=None if record is None else int(record[1])))
            rewrites.append(DialogueRewrite(selector=int(entry["selector"]),
                                            lines=tuple(edits)))
        else:
            raise SwapSpecError(
                f"operation {index}: unknown kind {kind!r}; expected sprite, portrait or "
                "dialogue"
            )
    return tuple(sprites), tuple(portraits), tuple(rewrites)


def apply_spec(image: bytes, spec_path: Path) -> tuple[bytes, dict]:
    """Apply a spec's operations to an image and return the new image and its report."""
    document = json.loads(spec_path.read_text(encoding="utf-8"))
    sprites, portraits, rewrites = parse_spec(document)
    assets = spec_path.parent
    report: dict[str, Any] = {"spec": str(spec_path), "operations": [], "passes": []}

    current = image
    if sprites or portraits:
        current, graphics = swap(current, assets, sprites=sprites, portraits=portraits)
        report["passes"].append({"kind": "graphics", "sprites": graphics["sprites"],
                                 "portraits": graphics["portraits"],
                                 "containers_written": graphics["containers_written"],
                                 "diff": graphics["diff"], "reopen": graphics["reopen"],
                                 "assets": graphics["assets"],
                                 "palette_changed": graphics["palette_changed"]})
    for rewrite in rewrites:
        current, result = rewrite_dialogue(current, rewrite)
        report["passes"].append({"kind": "dialogue", **result})
    report["operations"] = [entry.get("kind") for entry in document["operations"]]
    return current, report


def guarded_apply(image_path: Path, expect_sha256: str, out_path: Path,
                  report_path: Path | None, transform, *,
                  error: type[ValueError] = SwapSpecError) -> dict:
    """The guard, the read, the caller's transform, the staged write, and the source re-hash.

    One implementation of the two rules that must not be duplicated: the source-alias refusal
    and the staged write. A caller supplies its own transform (bytes to bytes plus a report)
    and its own error type, so a preset refuses in the vocabulary its callers already match.
    """
    ensure_not_source_alias(image_path, out_path)
    if report_path is not None:
        ensure_not_source_alias(image_path, report_path)
        ensure_not_source_alias(out_path, report_path)
    image = image_path.read_bytes()
    digest = sha256(image)
    if digest != expect_sha256.lower():
        raise error(
            f"{image_path} is {digest}, not the image this swap was proven against "
            f"({expect_sha256.lower()})"
        )
    out, report = transform(image)
    report["image"] = {
        "path": str(image_path), "sha256": digest, "size": len(image),
        "output_path": str(out_path), "output_sha256": sha256(out), "output_size": len(out),
    }
    write_staged(out_path, out)
    if report_path is not None:
        write_staged(report_path,
                     (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    if sha256(image_path.read_bytes()) != digest:
        raise error("the source image changed during the build")
    return report


def run(image_path: Path, expect_sha256: str, spec_path: Path, out_path: Path,
        report_path: Path | None = None) -> dict:
    """The whole command: guard, read, apply, verify, stage, and re-hash the source."""
    return guarded_apply(image_path, expect_sha256, out_path, report_path,
                         lambda image: apply_spec(image, spec_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = run(args.image, args.expect_sha256, args.spec, args.out, args.report)
    except (SwapSpecError, WriteError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(f"output {report['image']['output_sha256']}  {report['image']['output_size']} bytes")
    for entry in report["passes"]:
        if entry["kind"] == "graphics":
            print(f"  graphics: {entry['containers_written']} containers, "
                  f"{entry['diff']['changed_bytes_inside_declared_spans']} bytes inside, "
                  f"{entry['diff']['changed_bytes_outside']} outside")
        else:
            for handle in entry["handles"]:
                print(f"  dialogue: {handle['speaker']} {handle['was']} -> "
                      f"({handle['new_start']}, {handle['new_length']}) reads "
                      f"{entry['verification']['read_back'][handle['speaker']]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
