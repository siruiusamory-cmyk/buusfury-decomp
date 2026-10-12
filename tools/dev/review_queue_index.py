"""Index the review queue: what is open, what has a verdict, what is claimed.

The need (dbz-dev retro 1.5): six requests were filed and six results read in one
session, and "is anything open for this lane" was answered by listing
`review-queue\\results` by mtime and joining the two directories by hand.

The queue lives outside this repository, so no repository test polices it. What
this module does instead, and what its guard asserts, is that it is READ-ONLY over
the queue: it lists, joins and prints, and never writes a request, a claim or a
result. `build()` is a pure function over a queue directory so the guard can run it
against a fixture instead of the live queue other lanes are using.

    python -m tools.dev.review_queue_index
    python -m tools.dev.review_queue_index --ticket RETRO-TOOLS-001
    python -m tools.dev.review_queue_index --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

#: The queue the coordinator route uses. One machine path, not a repository path:
#: it is outside the checkout by design (docs: the queue is not versioned).
DEFAULT_QUEUE = Path.home() / ".dsh" / "review-queue"

VERDICT_STATES = ("PASS", "BLOCKED")


def parse_stamp(review_id: str) -> datetime | None:
    """`<TICKET>-<yyyyMMdd-HHmmss>` is the queue's own naming rule."""
    stamp = review_id.rsplit("-", 1)[-1]
    # The queue writes `yyyyMMdd-HHmmss`, so the id splits on the SECOND dash and
    # the stamp is the last two fields joined: the first is 8 digits, the second 6.
    parts = review_id.split("-")
    if len(parts) < 2:
        return None
    stamp = "-".join(parts[-2:])
    if len(stamp) != 15 or not stamp[:8].isdigit() or not stamp[9:].isdigit():
        return None
    try:
        return datetime.strptime(stamp, "%Y%m%d-%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def verdict_of(result: Path | None) -> str | None:
    """The LAST non-blank line, which is where every result file puts its verdict.

    Scanning the head of the file for the first of PASS/BLOCKED reads a BLOCKED
    review as PASS whenever the prose above the verdict contains the word, which
    is exactly what the long form of this queue's results does.
    """
    if result is None or not result.is_file():
        return None
    lines = result.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in reversed(lines):
        stripped = line.strip()
        if not stripped:
            continue
        return stripped if stripped in VERDICT_STATES else "UNKNOWN"
    return "UNKNOWN"


def age_label(hours: float | None) -> str:
    """A negative age would be a clock skew, so it is labelled, not printed bare."""
    if hours is None:
        return "?"
    if hours < 0:
        return f"in the future by {abs(hours)}h (the request timestamp is ahead of this clock)"
    return f"{hours}h"


def build(queue: Path, now: datetime | None = None) -> dict:
    """Read the queue and return the index. Writes nothing, anywhere."""
    now = now or datetime.now(timezone.utc)
    requests = []
    for request in sorted((queue / "requests").glob("*.json"), key=lambda p: p.name):
        try:
            payload = json.loads(request.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            requests.append({"review_id": request.stem, "error": str(error)})
            continue
        review_id = payload.get("review_id") or request.stem
        result = queue / "results" / f"{review_id}.md"
        stamp = parse_stamp(review_id)
        requests.append(
            {
                "review_id": review_id,
                "ticket": payload.get("ticket"),
                "review_sha": payload.get("review_sha"),
                "worktree": payload.get("worktree"),
                "focused_tests": payload.get("focused_tests", []),
                "age_hours": None
                if stamp is None
                else round((now - stamp).total_seconds() / 3600.0, 1),
                "claimed": (queue / "claimed" / review_id).exists(),
                "verdict": verdict_of(result if result.is_file() else None),
                "result": result.name if result.is_file() else None,
            }
        )
    return {
        "queue": str(queue),
        "generated": now.isoformat(),
        "requests": requests,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--ticket", help="only this ticket's requests")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if not (args.queue / "requests").is_dir():
        print(f"no review queue at {args.queue}", file=sys.stderr)
        return 2

    report = build(args.queue)
    rows = report["requests"]
    if args.ticket:
        rows = [row for row in rows if row.get("ticket") == args.ticket]
    if args.json:
        print(json.dumps({"queue": report["queue"], "requests": rows}, indent=2))
        return 0

    outstanding = [row for row in rows if row.get("verdict") is None]
    claimed = [row for row in rows if row.get("claimed") and row.get("verdict") is None]
    print(f"queue: {report['queue']}")
    print(
        f"{len(rows)} request(s), {len(outstanding)} without a verdict, "
        f"{len(claimed)} claimed and awaiting one"
    )
    for row in sorted(rows, key=lambda r: r.get("age_hours") or 0, reverse=True):
        print(
            "  {0}  {1}  {2}  age {3}  {4}".format(
                row.get("verdict") or "OPEN",
                row.get("ticket") or "?",
                (row.get("review_sha") or "?")[:12],
                age_label(row.get("age_hours")),
                "claimed" if row.get("claimed") else "unclaimed",
            )
        )
        print(f"    {row['review_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
