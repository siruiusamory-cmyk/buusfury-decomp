"""Decode a P-009 damage-apply capture into per-hit critical evidence.

The capture breaks at ``0x0800FA2A`` (the damage-apply function) with
``--dump-register r1``, so each stop's dump is the incoming damage record.
This program joins ``events.csv`` with ``dumps.wfcap`` and reports, per hit,
the fields the ticket needs:

* ``LR``            -- the concrete caller, which is the damage producer that
  static analysis could not reach (``0x0800FA2A`` has no direct BL callers).
* ``record+0x10``   -- the boolean that selects the special damage-number
  style at ``0x0800E94E``; the critical-presentation flag candidate.
* ``record+0x18``   -- the applied damage in raw fixed-point units.

Damage and HP are stored scaled by 1024.  The player-facing number is
``(raw + 1023) >> 10`` per the display path at ``0x0800AB9A``, so both forms
are reported and no caller has to redo the conversion.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from tools.runtime.mgba_capture import iter_capture_records

# Display conversion, from the number-refresh path at 0x0800AB9A:
#   r0 = accumulator; r0 += 1023; r2 = r0 >> 10
HP_FRACTIONAL_BITS = 10
HP_ROUND_ADD = (1 << HP_FRACTIONAL_BITS) - 1

# Damage record layout, established statically in P-009.
RECORD_SPECIAL_FLAG = 0x10
RECORD_DAMAGE = 0x18


def displayed(raw: int) -> int:
    """Convert a raw fixed-point damage/HP value to the on-screen integer."""
    return (raw + HP_ROUND_ADD) >> HP_FRACTIONAL_BITS


def _u32(blob: bytes, offset: int) -> int | None:
    if offset + 4 > len(blob):
        return None
    return int.from_bytes(blob[offset : offset + 4], "little")


def load_dumps(path: Path) -> dict[int, tuple[int, bytes]]:
    if not path.exists():
        return {}
    blob = path.read_bytes()
    return {stop: (address, data) for stop, address, data in iter_capture_records(blob)}


def load_events(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_rows(run_dir: Path) -> list[dict[str, object]]:
    events = load_events(run_dir / "events.csv")
    dumps = load_dumps(run_dir / "dumps.wfcap")

    rows: list[dict[str, object]] = []
    for event in events:
        stop = int(event["stop"])
        entry = dumps.get(stop)
        record_address, blob = entry if entry else (None, b"")
        flag = _u32(blob, RECORD_SPECIAL_FLAG)
        damage = _u32(blob, RECORD_DAMAGE)
        rows.append(
            {
                "stop": stop,
                "tick": event.get("gameplay_tick", ""),
                "lr": event.get("lr", ""),
                "record": f"0x{record_address:08X}" if record_address else "",
                "flag": flag,
                "damage_raw": damage,
                "damage_shown": displayed(damage) if damage is not None else None,
            }
        )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[str]:
    """Report what the capture settles and, explicitly, what it does not."""
    lines: list[str] = []
    hits = [row for row in rows if row["damage_raw"] is not None]
    lines.append(f"stops: {len(rows)}  decoded records: {len(hits)}")
    if not hits:
        lines.append("no damage records decoded; nothing can be concluded")
        return lines

    callers: dict[str, int] = {}
    for row in hits:
        callers[str(row["lr"])] = callers.get(str(row["lr"]), 0) + 1
    lines.append("callers (LR -> count), the producer candidates:")
    for caller, count in sorted(callers.items(), key=lambda item: -item[1]):
        lines.append(f"  {caller}  x{count}")

    flagged = [row for row in hits if row["flag"]]
    plain = [row for row in hits if not row["flag"]]
    lines.append(f"record+0x10 nonzero: {len(flagged)}   zero: {len(plain)}")

    def mean(values: list[int]) -> float:
        return sum(values) / len(values) if values else float("nan")

    if plain:
        base = mean([int(row["damage_raw"]) for row in plain])
        lines.append(f"mean damage, flag=0: {base:.1f} raw ({displayed(int(base))} shown)")
        if flagged:
            special = mean([int(row["damage_raw"]) for row in flagged])
            lines.append(
                f"mean damage, flag=1: {special:.1f} raw "
                f"({displayed(int(special))} shown), ratio {special / base:.3f}"
            )
        else:
            lines.append("no flag=1 events captured; the flag's meaning stays UNKNOWN")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()

    rows = build_rows(args.run_dir)
    header = f"{'stop':>4}  {'tick':>7}  {'LR':>10}  {'record':>10}  {'flag':>10}  {'raw':>8}  {'shown':>5}"
    print(header)
    print("-" * len(header))
    for row in rows:
        flag = row["flag"]
        damage = row["damage_raw"]
        print(
            f"{row['stop']:>4}  {row['tick']:>7}  {row['lr']:>10}  {row['record']:>10}  "
            f"{('0x%08X' % flag) if flag is not None else '?':>10}  "
            f"{damage if damage is not None else '?':>8}  "
            f"{row['damage_shown'] if damage is not None else '?':>5}"
        )
    print()
    for line in summarize(rows):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
