"""The region map: loading, tiling validation, reporting.

The region map (config/regions.json) partitions the ROM into ranges and says, for
each range, whether the reference build rebuilds it from source or copies it
verbatim out of the baserom.

Everything here is deterministic and side-effect free except render_markdown(),
which returns a string rather than writing it.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from . import identity as _identity

#: A region the reference build copies verbatim from the baserom.
CLASS_INCBIN = "incbin"
#: A region built from a source asset with grit and/or JCALG1.
CLASS_ASSET = "asset"
#: A region built from source by the ARM Developer Suite 1.2 toolchain.
CLASS_ADS = "ads"

VALID_CLASSES = (CLASS_INCBIN, CLASS_ASSET, CLASS_ADS)


class RegionMapError(RuntimeError):
    """Raised when the region map is structurally invalid or does not tile."""


@dataclasses.dataclass(frozen=True)
class Region:
    id: str
    start: int
    end: int
    cls: str
    note: str = ""
    reference_source: str = ""
    tool: str = ""
    source_asset: str = ""
    pipeline: tuple[str, ...] = ()

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def extent(self) -> str:
        return f"0x{self.start:06X}-0x{self.end:06X}"

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "start": f"0x{self.start:06X}",
            "end": f"0x{self.end:06X}",
            "length": self.length,
            "class": self.cls,
            "tool": self.tool,
            "source_asset": self.source_asset,
            "reference_source": self.reference_source,
            "note": self.note,
        }


def _as_int(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(value, 0)


def load_regions(path: Path | None = None) -> list[Region]:
    """Load and structurally validate config/regions.json."""
    config_path = path or (_identity.CONFIG_DIR / "regions.json")
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    regions: list[Region] = []
    seen: set[str] = set()
    for entry in raw["regions"]:
        region = Region(
            id=entry["id"],
            start=_as_int(entry["start"]),
            end=_as_int(entry["end"]),
            cls=entry["class"],
            note=entry.get("note", ""),
            reference_source=entry.get("reference_source", ""),
            tool=entry.get("tool", ""),
            source_asset=entry.get("source_asset", ""),
            pipeline=tuple(entry.get("pipeline", ())),
        )
        if region.id in seen:
            raise RegionMapError(f"duplicate region id: {region.id}")
        seen.add(region.id)
        if region.cls not in VALID_CLASSES:
            raise RegionMapError(
                f"region {region.id}: unknown class {region.cls!r}; "
                f"expected one of {VALID_CLASSES}"
            )
        if region.end <= region.start:
            raise RegionMapError(
                f"region {region.id}: end 0x{region.end:X} is not after "
                f"start 0x{region.start:X}"
            )
        regions.append(region)
    regions.sort(key=lambda r: r.start)
    return regions


def load_rom_size(path: Path | None = None) -> int:
    config_path = path or (_identity.CONFIG_DIR / "regions.json")
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return _as_int(raw["rom_size"])


def validate_tiling(regions: list[Region], rom_size: int) -> None:
    """Fail unless the regions tile [0, rom_size) with no gap and no overlap.

    Both failure modes are reported together, and the report names the offending
    offsets, because a silent hole in the map is exactly the defect that would
    make a "matching" build reproduce a ROM it never actually accounted for.
    """
    problems: list[str] = []
    cursor = 0
    for region in sorted(regions, key=lambda r: r.start):
        if region.start < cursor:
            problems.append(
                f"region {region.id} starts at 0x{region.start:06X} but the previous "
                f"region already extends to 0x{cursor:06X} (overlap of "
                f"{cursor - region.start} bytes)"
            )
            cursor = max(cursor, region.end)
            continue
        if region.start > cursor:
            problems.append(
                f"gap of {region.start - cursor} bytes at 0x{cursor:06X}.."
                f"0x{region.start:06X}, before region {region.id}"
            )
        cursor = region.end

    if cursor != rom_size:
        problems.append(
            f"map ends at 0x{cursor:06X} but the ROM is 0x{rom_size:06X} bytes "
            f"({rom_size - cursor:+d} bytes)"
        )

    if problems:
        body = "\n".join(f"  - {p}" for p in problems)
        raise RegionMapError(
            "region map does not tile the ROM exactly:\n" + body
        )


def class_totals(regions: list[Region]) -> dict[str, int]:
    totals = {cls: 0 for cls in VALID_CLASSES}
    for region in regions:
        totals[region.cls] = totals.get(region.cls, 0) + region.length
    return totals


def regions_by_class(regions: list[Region], cls: str) -> list[Region]:
    return [r for r in regions if r.cls == cls]


def render_markdown(
    regions: list[Region],
    rom_size: int,
    title: str = "Buu's Fury - ROM region map",
) -> str:
    """Render the map as a committed Markdown document."""
    totals = class_totals(regions)
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(
        "Generated by `python -m buusfury map --write`. Do not edit by hand; "
        "edit [`config/regions.json`](../config/regions.json) instead."
    )
    lines.append("")
    lines.append(f"ROM size: **{rom_size} bytes** (0x{rom_size:06X})")
    lines.append("")
    lines.append("## Coverage by class")
    lines.append("")
    lines.append("| class | meaning | bytes | share | regions |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    meaning = {
        CLASS_INCBIN: "opaque - copied verbatim from the baserom",
        CLASS_ASSET: "rebuilt from a source asset (grit / JCALG1 / palette)",
        CLASS_ADS: "rebuilt from source by ARM Developer Suite 1.2",
    }
    for cls in VALID_CLASSES:
        members = regions_by_class(regions, cls)
        share = 100.0 * totals[cls] / rom_size if rom_size else 0.0
        lines.append(
            f"| `{cls}` | {meaning[cls]} | {totals[cls]:,} | {share:.3f}% | "
            f"{len(members)} |"
        )
    lines.append(
        f"| **total** | | **{sum(totals.values()):,}** | **100.000%** | "
        f"**{len(regions)}** |"
    )
    lines.append("")
    lines.append("## Regions")
    lines.append("")
    lines.append("| # | id | file extent | bytes | class | tool | reference source |")
    lines.append("| ---: | --- | --- | ---: | --- | --- | --- |")
    for index, region in enumerate(sorted(regions, key=lambda r: r.start), start=1):
        ref = region.reference_source or "-"
        ref = ref.replace("|", "\\|")
        lines.append(
            f"| {index} | `{region.id}` | `{region.extent}` | {region.length:,} | "
            f"`{region.cls}` | {region.tool or '-'} | {ref} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for region in sorted(regions, key=lambda r: r.start):
        if not region.note:
            continue
        lines.append(f"### `{region.id}` ({region.extent}, {region.length:,} bytes)")
        lines.append("")
        lines.append(region.note)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
