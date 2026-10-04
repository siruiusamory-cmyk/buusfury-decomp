"""SPRITE-NEW-PARITY-HYGIENE-001: reproduce the parity run's facing check.

The runtime-parity record states that every sampled position change was paired
with the frame record the actor was drawing at that instant, and that no pair
mismatched. This script is that pairing, so the claim is auditable from the tree
rather than from a scratch file that was never committed.

It reads one observer run directory - the ``out`` directory
``tools/runtime/spritenew005_parity.lua`` writes - together with the parity
manifest that recorded the identity's own frame records, and prints:

* the identity's resolution rows (sprite 307 resolving to the authored structure);
* the actor the observer identified as the authored one, its position span, and
  how many of its sampled position changes were paired with a facing;
* the pairing result: for every sampled position change, the direction the actor
  moved (from ``+0x1A0``/``+0x1A4``) against the direction of the frame record it
  was drawing (from ``actor+0x54``), which is the facing the engine selected;
* every other sampled actor, and whether it moved;
* the authored actor's walk-action results.

Read-only: nothing is written, and no file outside the run directory and the
manifest is opened.

    python tools/research/sprite_new_parity_report.py \\
        --manifest <parity json> --variant as-authored --run-dir <observer out dir>
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_TOOLS = _HERE.parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

DIRECTIONS = {0: "down", 1: "up", 2: "left", 3: "right"}


class ReportError(ValueError):
    """A run directory or manifest this report cannot read."""


def read_rows(run_dir: Path, name: str, columns: int):
    """Data rows of one observer log, with its ``#`` header lines dropped."""
    path = run_dir / name
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != columns:
            continue
        rows.append(parts)
    return rows


def number(text: str):
    return None if text in ("-", "?") else int(text, 0)


def frame_directions(manifest: dict, variant: str) -> dict:
    """Frame-record ROM address -> the direction that cell draws, from the plan."""
    variants = manifest.get("variants") or {}
    if variant not in variants:
        raise ReportError(
            f"the manifest has no {variant!r} variant; it has {sorted(variants)}")
    return {int(frame["rom_address"], 16): frame["direction"]
            for frame in variants[variant]["frame_map"]}


def moved_direction(previous, current) -> int | None:
    """The engine's direction index for one sampled displacement, or None."""
    dx = current[1] - previous[1]
    dy = current[2] - previous[2]
    if dx == 0 and dy == 0:
        return None
    if abs(dx) >= abs(dy) and dx != 0:
        return 3 if dx > 0 else 2
    return 0 if dy > 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True,
                        help="the parity manifest whose frame map names the "
                             "identity's own frame records")
    parser.add_argument("--variant", default="as-authored",
                        help="which variant's frame map to use (default as-authored)")
    parser.add_argument("--run-dir", required=True,
                        help="an observer out directory, holding actors.txt, "
                             "walk.txt and resolutions.txt")
    parser.add_argument("--json", action="store_true",
                        help="emit the summary as JSON instead of text")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        raise ReportError(f"not a run directory: {run_dir}")
    directions = frame_directions(
        json.loads(Path(args.manifest).read_text(encoding="utf-8")), args.variant)

    actors = read_rows(run_dir, "actors.txt", 7)
    walk = read_rows(run_dir, "walk.txt", 7)
    resolutions = read_rows(run_dir, "resolutions.txt", 6)
    if not actors:
        raise ReportError(f"{run_dir}/actors.txt holds no sample rows")

    authored = sorted({int(row[1], 0) for row in actors if row[6] == "1"})
    if not authored:
        raise ReportError(
            "no sampled actor drew one of the identity's frame records, so the "
            "authored actor was never observed")

    summary = {
        "run_dir": str(run_dir),
        "variant": args.variant,
        "authored_frame_records": len(directions),
        "resolutions": len(resolutions),
        "new_identity_resolutions": sum(1 for row in resolutions if row[4] == "1"),
        "resolution_rows": [
            {"frame": int(row[0]), "record": row[1], "sprite": row[2],
             "structure": row[3], "is_new": row[4] == "1", "map": row[5]}
            for row in resolutions],
        "actors": [],
    }

    for actor in authored:
        series = [(int(row[0]), number(row[2]), number(row[3]), number(row[4]),
                   number(row[5]), row[5]) for row in actors
                  if int(row[1], 0) == actor]
        facings = collections.Counter(row[5] for row in series)
        matches = 0
        mismatches = []
        changes = 0
        for previous, current in zip(series, series[1:]):
            if previous[1] is None or current[1] is None:
                continue
            moved = moved_direction(previous, current)
            if moved is None:
                continue
            changes += 1
            drawn = current[4]
            if drawn is None:
                continue
            if drawn == moved:
                matches += 1
            else:
                mismatches.append({
                    "frame": current[0], "moved": DIRECTIONS[moved],
                    "drew": DIRECTIONS.get(drawn, str(drawn)),
                    "dx": current[1] - previous[1],
                    "dy": current[2] - previous[2]})
        ours_walk = [row for row in walk if int(row[1], 0) == actor]
        summary["actors"].append({
            "actor": f"0x{actor:08X}",
            "authored": True,
            "samples": len(series),
            "frames": [series[0][0], series[-1][0]],
            "first_position": [series[0][1], series[0][2]],
            "last_position": [series[-1][1], series[-1][2]],
            "facings_drawn": {DIRECTIONS.get(int(k), k): v
                              for k, v in sorted(facings.items())},
            "position_changes": changes,
            "facing_matches": matches,
            "facing_mismatches": mismatches,
            "walk_calls": len(ours_walk),
            "walk_accepts": sum(1 for row in ours_walk if row[2] == "1"),
        })

    for actor in sorted({int(row[1], 0) for row in actors} - set(authored)):
        series = [(int(row[0]), number(row[2]), number(row[3])) for row in actors
                  if int(row[1], 0) == actor]
        moved = any(series[index][1] != series[index + 1][1]
                    or series[index][2] != series[index + 1][2]
                    for index in range(len(series) - 1))
        summary["actors"].append({
            "actor": f"0x{actor:08X}", "authored": False, "samples": len(series),
            "moved": moved,
            "first_position": [series[0][1], series[0][2]],
            "last_position": [series[-1][1], series[-1][2]]})

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    print(f"run directory : {run_dir}")
    print(f"variant       : {args.variant} ({len(directions)} authored frame records)")
    print(f"resolutions   : {summary['resolutions']} rows, "
          f"{summary['new_identity_resolutions']} resolving the authored identity")
    for row in summary["resolution_rows"]:
        marker = "  <- authored identity" if row["is_new"] else ""
        print(f"   frame {row['frame']:>5}  record {row['record']}  "
              f"sprite {row['sprite']:>4}  structure {row['structure']}  "
              f"map {row['map']}{marker}")
    for entry in summary["actors"]:
        if entry["authored"]:
            print(f"\nauthored actor {entry['actor']}")
            print(f"   samples {entry['samples']} over frames "
                  f"{entry['frames'][0]}..{entry['frames'][1]}")
            print(f"   position 0x{entry['first_position'][0]:X},"
                  f"0x{entry['first_position'][1]:X} -> "
                  f"0x{entry['last_position'][0]:X},"
                  f"0x{entry['last_position'][1]:X}")
            print(f"   facings drawn: {entry['facings_drawn']}")
            print(f"   position changes {entry['position_changes']}, "
                  f"facing matched {entry['facing_matches']}, "
                  f"mismatched {len(entry['facing_mismatches'])}")
            for item in entry["facing_mismatches"][:10]:
                print(f"      frame {item['frame']}: moved {item['moved']}, "
                      f"drew {item['drew']}, delta {item['dx']},{item['dy']}")
            print(f"   walk calls {entry['walk_calls']}, "
                  f"accepted {entry['walk_accepts']}")
    retail = [entry for entry in summary["actors"] if not entry["authored"]]
    moved = sum(1 for entry in retail if entry["moved"])
    print(f"\nretail actors sampled {len(retail)}, of which moved {moved}")
    for entry in retail:
        print(f"   {entry['actor']} moved={entry['moved']} "
              f"0x{entry['first_position'][0]:X},0x{entry['first_position'][1]:X} -> "
              f"0x{entry['last_position'][0]:X},0x{entry['last_position'][1]:X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
