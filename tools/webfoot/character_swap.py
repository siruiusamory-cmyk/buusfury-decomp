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

from tools.webfoot.dialogue_edit import (DialogueEditError, DialogueRewrite, LineEdit,
                                         rewrite_dialogue)
from tools.webfoot.sprite_swap import (DONOR_GEOMETRY, PortraitSwap, SheetSlot, SpriteGeometry,
                                       SpriteSwap, SpriteSwapError, swap)
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


#: Keys a spec may carry, per operation kind. An unknown key is refused rather than ignored,
#: because a typo like "cropx" would otherwise silently write the wrong window.
_SPRITE_KEYS = {"kind", "sprite_id", "slots", "frame", "cell", "crop_x", "anchor",
                "composition_size"}
_PORTRAIT_KEYS = {"kind", "slot", "png", "side"}
_DIALOGUE_KEYS = {"kind", "selector", "lines"}
_LINE_KEYS = {"speaker", "old", "new", "record"}
_SLOT_KEYS = {"slot", "sheet", "frames"}


def _reject_unknown(entry: dict[str, Any], allowed: set[str], where: str) -> None:
    if not isinstance(entry, dict):
        raise SwapSpecError(f"{where} must be an object, not {type(entry).__name__}")
    unknown = sorted(set(entry) - allowed)
    if unknown:
        raise SwapSpecError(
            f"{where} carries {unknown}, which this spec does not define; refusing rather than "
            f"ignoring {unknown} and writing something else"
        )


def _require(entry: dict[str, Any], key: str, where: str) -> Any:
    if key not in entry:
        raise SwapSpecError(f"{where} is missing {key!r}")
    return entry[key]


def _integer(value: Any, where: str) -> int:
    """A real integer. A bool is not one, and a float is not truncated into one."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise SwapSpecError(f"{where} must be an integer, not {value!r}")
    return value


def _text(value: Any, where: str) -> str:
    """A real string, required.

    Coercing with ``str()`` is how a JSON ``null`` becomes the literal line "None" and then
    passes its own read-back, because the read-back compares the sentence the engine was given.
    Refusing here is the only place that can be caught.
    """
    if not isinstance(value, str):
        raise SwapSpecError(
            f"{where} must be a string, not {value!r}; a null or a number here would be written "
            "into the game as text, so it is refused"
        )
    return value


def _geometry(entry: dict[str, Any], where: str) -> SpriteGeometry:
    frame = entry.get("frame", [DONOR_GEOMETRY.frame_width, DONOR_GEOMETRY.frame_height])
    anchor = entry.get("anchor", list(DONOR_GEOMETRY.frame_anchor))
    if not isinstance(frame, list) or len(frame) != 2:
        raise SwapSpecError(f"{where}: 'frame' is [width, height], not {frame!r}")
    if not isinstance(anchor, list) or len(anchor) != 2:
        raise SwapSpecError(f"{where}: 'anchor' is [x, y], not {anchor!r}")
    geometry = SpriteGeometry(
        frame_width=_integer(frame[0], f"{where}: frame width"),
        frame_height=_integer(frame[1], f"{where}: frame height"),
        cell_side=_integer(entry.get("cell", DONOR_GEOMETRY.cell_side),
                           f"{where}: cell"),
        crop_x=_integer(entry.get("crop_x", DONOR_GEOMETRY.crop_x), f"{where}: crop_x"),
        frame_anchor=(_integer(anchor[0], f"{where}: anchor x"),
                      _integer(anchor[1], f"{where}: anchor y")),
        composition_size=_integer(entry.get("composition_size",
                                           DONOR_GEOMETRY.composition_size),
                                  f"{where}: composition_size"))
    if geometry.cell_side % 8 or geometry.frame_width > geometry.cell_side:
        raise SwapSpecError(
            f"{where}: a {geometry.cell_side}-pixel cell must be a whole number of 8-pixel "
            f"tiles and at least as wide as the {geometry.frame_width}-pixel frame"
        )
    if geometry.crop_x < 0 or geometry.crop_x + geometry.frame_width > geometry.cell_side:
        raise SwapSpecError(
            f"{where}: crop_x {geometry.crop_x} puts a {geometry.frame_width}-pixel frame "
            f"outside a {geometry.cell_side}-pixel cell"
        )
    return geometry


def parse_spec(document: dict[str, Any]) -> tuple[tuple[SpriteSwap, ...],
                                                  tuple[PortraitSwap, ...],
                                                  tuple[DialogueRewrite, ...]]:
    """Read the operations, refusing anything that would have to be guessed at."""
    if not isinstance(document, dict):
        raise SwapSpecError("the spec must be a JSON object")
    operations = document.get("operations")
    if not isinstance(operations, list) or not operations:
        raise SwapSpecError("the spec needs a non-empty 'operations' list")
    sprites: list[SpriteSwap] = []
    portraits: list[PortraitSwap] = []
    rewrites: list[DialogueRewrite] = []
    for index, entry in enumerate(operations):
        where = f"operation {index}"
        kind = entry.get("kind") if isinstance(entry, dict) else None
        if kind == "sprite":
            _reject_unknown(entry, _SPRITE_KEYS, where)
            slots = _require(entry, "slots", where)
            if not isinstance(slots, list) or not slots:
                raise SwapSpecError(f"{where}: a sprite needs a non-empty 'slots'")
            parsed = []
            for position, slot in enumerate(slots):
                slot_where = f"{where} slot {position}"
                _reject_unknown(slot, _SLOT_KEYS, slot_where)
                parsed.append(SheetSlot(
                    _integer(_require(slot, "slot", slot_where), f"{slot_where}: slot"),
                    _text(_require(slot, "sheet", slot_where), f"{slot_where}: sheet"),
                    _integer(_require(slot, "frames", slot_where), f"{slot_where}: frames")))
            sprites.append(SpriteSwap(
                sprite_id=_integer(_require(entry, "sprite_id", where),
                                   f"{where}: sprite_id"),
                slots=tuple(parsed),
                geometry=_geometry(entry, where)))
        elif kind == "portrait":
            _reject_unknown(entry, _PORTRAIT_KEYS, where)
            portraits.append(PortraitSwap(
                slot=_integer(_require(entry, "slot", where), f"{where}: slot"),
                png=_text(_require(entry, "png", where), f"{where}: png"),
                side=_integer(entry.get("side", 64), f"{where}: side")))
        elif kind == "dialogue":
            _reject_unknown(entry, _DIALOGUE_KEYS, where)
            lines = _require(entry, "lines", where)
            if not isinstance(lines, list) or not lines:
                raise SwapSpecError(f"{where}: a dialogue edit needs 'lines'")
            edits = []
            for position, line in enumerate(lines):
                line_where = f"{where} line {position}"
                _reject_unknown(line, _LINE_KEYS, line_where)
                record = line.get("record")
                if record is not None and (not isinstance(record, list) or len(record) != 2):
                    raise SwapSpecError(
                        f"{line_where}: 'record' is [decoded start, decoded length], "
                        f"not {record!r}"
                    )
                edits.append(LineEdit(
                    speaker=("unstated" if "speaker" not in line
                             else _text(line["speaker"], f"{line_where}: speaker")),
                    old_text=_text(_require(line, "old", line_where), f"{line_where}: old"),
                    new_text=_text(_require(line, "new", line_where), f"{line_where}: new"),
                    decoded_start=None if record is None else _integer(
                        record[0], f"{line_where}: record start"),
                    decoded_length=None if record is None else _integer(
                        record[1], f"{line_where}: record length")))
            rewrites.append(DialogueRewrite(
                selector=_integer(_require(entry, "selector", where), f"{where}: selector"),
                lines=tuple(edits)))
        else:
            raise SwapSpecError(
                f"{where}: unknown kind {kind!r}; expected sprite, portrait or dialogue"
            )
    return tuple(sprites), tuple(portraits), tuple(rewrites)


def apply_spec(image: bytes, spec_path: Path) -> tuple[bytes, dict]:
    """Apply a spec's operations to an image and return the new image and its report."""
    try:
        document = json.loads(spec_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SwapSpecError(f"{spec_path} is not readable JSON text: {exc}") from exc
    except OSError as exc:
        raise SwapSpecError(f"{spec_path} could not be read: {exc}") from exc
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
    try:
        image = image_path.read_bytes()
    except OSError as exc:
        raise error(f"{image_path} could not be read: {exc}") from exc
    digest = sha256(image)
    if digest != expect_sha256.lower():
        raise error(
            f"{image_path} is {digest}, not the image this swap was proven against "
            f"({expect_sha256.lower()})"
        )
    try:
        out, report = transform(image)
    except OSError as exc:
        # A missing sheet or portrait is an operator error, not a crash: report it as a refusal
        # so the message names the file rather than a traceback.
        raise error(f"a file the swap needs could not be read: {exc}") from exc
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
    except (SwapSpecError, WriteError, DialogueEditError, SpriteSwapError) as exc:
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
                key = f"{handle['new_start']}:{handle['new_length']}"
                print(f"  dialogue: {handle['speaker']} {handle['was']} -> "
                      f"({handle['new_start']}, {handle['new_length']}) reads "
                      f"{entry['verification']['read_back'][key]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
