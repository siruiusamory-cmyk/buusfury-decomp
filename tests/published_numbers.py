"""Where the published map figures live, in one definition.

``src/data/capabilities.json`` owns the measured map and layer figures. The site
(``src/data/project.ts``) and the coverage census
(``docs/research/rom_editor_coverage.json``) quote them, sometimes by rebuilding
the string from the registry and sometimes by writing the number again. The
2026-10-12 retro's 440/12 maps class is that second kind: a published figure
that quietly stopped matching the measuring code.

This module is the one definition both halves of the guard read.
:func:`registry_figures` states what the registry claims; :func:`quotes` states
every artifact phrase that has to carry those figures. The ROM-free half
(``tests/unit/test_published_numbers.py``) holds the artifacts to the registry;
the ROM-gated half
(``tests/integration/test_published_numbers_rom.py``) holds the registry to the
canonical image.

The subject is the map and layer figures. Other published counts, such as the
735 transition records or the census's own cell totals, are not covered here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "data" / "capabilities.json"
SITE = ROOT / "src" / "data" / "project.ts"
COVERAGE = ROOT / "docs" / "research" / "rom_editor_coverage.json"

#: The census row whose read and edit prose state the map figures.
CENSUS_ROW = "map-layout-chunk-grids"

#: The registry prose that states the layer-slot pair, in its own words.
_LAYER_SLOT_PROSE = re.compile(
    r"the form ([\d,]+) of the canonical image's ([\d,]+) layer slots"
)


def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def capability(capability_id: str) -> dict:
    return next(c for c in registry()["capabilities"] if c["id"] == capability_id)


def coverage() -> dict:
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


def census_row() -> dict:
    return next(row for row in coverage()["rows"] if row["id"] == CENSUS_ROW)


def site_source() -> str:
    return SITE.read_text(encoding="utf-8")


def registry_figures() -> dict[str, int]:
    """The map and layer figures the registry claims, measurements first."""
    layout = capability("layout")["measurements"]
    match = _LAYER_SLOT_PROSE.search(" ".join(capability("resize")["limits"]))
    if match is None:
        raise AssertionError(
            "src/data/capabilities.json no longer states the layer-slot pair "
            "in the form this guard reads"
        )
    return {
        "maps": layout["mapsViewable"],
        "editable": layout["editableMaps"],
        "read_only": layout["readOnlyMaps"],
        "dominant_slots": int(match.group(1).replace(",", "")),
        "layer_slots": int(match.group(2).replace(",", "")),
    }


def quotes(figures: dict[str, int]) -> list[tuple[str, str, str]]:
    """``(where, haystack, phrase)`` for every published quotation of the figures.

    The haystack is the slice of the artifact that owns the sentence, so a
    phrase in one field cannot satisfy a check aimed at another.
    """
    maps = figures["maps"]
    editable = figures["editable"]
    read_only = figures["read_only"]
    slots = figures["layer_slots"]
    dominant = figures["dominant_slots"]
    row = census_row()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    site_text = site_source()
    return [
        ("capabilities.json detail",
         registry_text, f"{editable} of the {maps} maps expose an editable layer"),
        ("capabilities.json limits",
         registry_text, f"{read_only} of the {maps} maps are read-only"),
        ("capabilities.json resize limits",
         registry_text, f"the form {dominant:,} of the canonical image's {slots:,} layer slots"),
        (f"coverage row {CENSUS_ROW} read",
         row["read"], f"All {maps} maps and {slots:,} layer slots enumerate; "
                      f"{dominant:,} slots are the dominant chunk-grid form"),
        (f"coverage row {CENSUS_ROW} edit",
         row["edit"], f"{editable} of {maps} maps expose an editable layer"),
        (f"coverage row {CENSUS_ROW} edit",
         row["edit"], f"{read_only} maps are refused"),
        ("project.ts map prose", site_text, f"{editable} of the {maps} maps"),
        ("project.ts corpus prose", site_text, f"{maps} maps and {slots:,} map-layer references"),
        ("project.ts metric", site_text, f"{slots:,} / {slots:,}"),
    ]


def missing_quotes(figures: dict[str, int]) -> list[str]:
    """Every phrase that does not appear in the artifact that should carry it."""
    return [
        f"{where}: {phrase!r}"
        for where, haystack, phrase in quotes(figures)
        if phrase not in haystack
    ]
