"""Serialization shared by the producers.

The `newline=""` / `encoding="utf-8"` pairing and the exact `json.dumps` keyword
sets are load-bearing for determinism and are reproduced from each original
script rather than unified: `seed_knowledge.jsonl` was written with
`ensure_ascii=False` and no key sort (`build_seed.py:589`), every other
artifact with `sort_keys=True, separators=(",", ":")`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def write_jsonl(path: Path, rows: Iterable[dict], *, sort_keys: bool = True,
                compact: bool = True, ensure_ascii: bool = True) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    separators = (",", ":") if compact else None
    with path.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=sort_keys, separators=separators,
                                    ensure_ascii=ensure_ascii) + "\n")
            count += 1
    return count


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]
