from __future__ import annotations

from typing import Iterable


def union(rows: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    out: list[list[int]] = []
    for start, end in sorted(rows):
        if end <= start:
            continue
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return [(start, end) for start, end in out]
