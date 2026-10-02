"""QA tooling: identify Buu's sprite from the ROM and extract its real palette.

The colour direction makes Buu's own in-game sprite the identity source, so the
sprite must be found by evidence and not by eye. This tool scans the decoded
graphics for the colour signature of Buu (skin pink/magenta, cape purple, white
gloves/mantle, dark outline) using the ACTUAL palette entries the game indexes,
ranks the candidates, and then reads the palette of the chosen sprite so the
result is reproducible from ROM data alone.

Run:

    python -m tools.qa.buu_sprite_palette --out docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md
"""

from __future__ import annotations

import argparse
import colorsys
import os
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _sprites():
    """The decoded sprite façade for the canonical image, or None."""
    from tools.webfoot import cli as cli_module
    from tools.webfoot.workbench import session as session_module
    from tools.webfoot.cli import load_catalog
    from tools.webfoot.workbench.session import Session

    # The worktree holds no `build/` of its own (it is generated and ignored), so
    # point the CLI's default atlas directory at the configured one rather than
    # creating a junction git will refuse to resolve.
    atlas = Path(os.environ.get("DBZ_QA_ATLAS_DIR", _ROOT / "build" / "atlas"))
    resolver = lambda: atlas  # noqa: E731 - a one-line stand-in
    cli_module._default_atlas_directory = resolver
    session_module._default_atlas_directory = resolver

    rom_dir = Path(os.environ.get("DBZ_QA_ROM", _ROOT / "roms"))
    candidates = sorted(rom_dir.glob("*Buu*Fury*.gba")) if rom_dir.is_dir() else []
    if not candidates:
        return None, None
    session = Session()
    session.open_rom(candidates[0], load_catalog(None))
    return session, session.sprites


def _hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb[:3])


def _hsv(rgb):
    r, g, b = (channel / 255 for channel in rgb[:3])
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360.0, s, v


def _is_skin(rgb) -> bool:
    """Buu's skin: a warm pink/magenta - red-dominant with real saturation."""
    h, s, v = _hsv(rgb)
    return (330 <= h or h < 20) and s > 0.28 and v > 0.45


def _is_cape(rgb) -> bool:
    """Buu's cape/vest: a purple - blue-dominant violet, not a blue."""
    h, s, v = _hsv(rgb)
    return 260 <= h < 330 and s > 0.30 and v > 0.30


def _is_white(rgb) -> bool:
    h, s, v = _hsv(rgb)
    return s <= 0.14 and v >= 0.86


def _is_outline(rgb) -> bool:
    h, s, v = _hsv(rgb)
    return v <= 0.30


def signature(graphic, rgb_table) -> dict[str, int]:
    """Count a sprite's pixels in each of Buu's four signature colour families."""
    counts = {"skin": 0, "cape": 0, "white": 0, "outline": 0, "opaque": 0}
    for index in graphic.pixels:
        if index == 0 or not (0 <= index < len(rgb_table)):
            continue  # index 0 is the transparent slot
        entry = rgb_table[index]
        counts["opaque"] += 1
        if _is_skin(entry):
            counts["skin"] += 1
        elif _is_cape(entry):
            counts["cape"] += 1
        elif _is_white(entry):
            counts["white"] += 1
        if _is_outline(entry):
            counts["outline"] += 1
    return counts


def find_candidates(limit: int = 12) -> list[tuple[float, object, dict]]:
    """Rank decoded graphics by how much they look like Buu's colour scheme.

    The score rewards a sprite that carries ALL FOUR families at once, because
    that combination - pink skin, purple cape, white mantle, dark outline - is
    Buu's character design rather than any single hue, of which the game has many.
    """
    session, sprites = _sprites()
    if sprites is None:
        return []
    rgb_table = [tuple(int(c) for c in entry[:3]) for entry in sprites.palette.rgb]
    scored: list[tuple[float, object, dict]] = []
    for graphic in sprites.graphics():
        counts = signature(graphic, rgb_table)
        if counts["opaque"] < 40:
            continue
        total = counts["opaque"]
        share = {key: counts[key] / total for key in ("skin", "cape", "white", "outline")}
        # Every family must be present, and skin must be a real part of the sprite.
        if min(share["skin"], share["cape"], share["white"], share["outline"]) < 0.03:
            continue
        if share["skin"] < 0.12:
            continue
        score = (
            share["skin"] * 3.0
            + share["cape"] * 2.0
            + share["white"] * 1.0
            + share["outline"] * 0.5
        )
        scored.append((score, graphic, counts))
    scored.sort(key=lambda row: row[0], reverse=True)
    return scored[:limit]


def sprite_palette(graphic, rgb_table) -> Counter:
    """The colours this sprite actually uses, by pixel count."""
    used: Counter = Counter()
    for index in graphic.pixels:
        if index == 0 or not (0 <= index < len(rgb_table)):
            continue
        used[(index, rgb_table[index])] += 1
    return used


def part_of_sprite(entry, counts_hint) -> str:
    """Where a colour appears on the sprite, from its own hue and value."""
    if _is_white(entry):
        return "mantle / gloves / eyes (the light neutral)"
    if _is_outline(entry):
        return "outline and shadow"
    if _is_skin(entry):
        return "skin"
    if _is_cape(entry):
        return "cape / vest"
    h, s, v = _hsv(entry)
    if 20 <= h < 70:
        return "accent detail (belt / trim)"
    if 160 <= h < 260:
        return "cool detail"
    return "detail"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--show", type=int, default=8, help="candidates to list")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    session, sprites = _sprites()
    if sprites is None:
        print("no canonical ROM available")
        return 1
    rgb_table = [tuple(int(c) for c in entry[:3]) for entry in sprites.palette.rgb]
    print(f"object palette entries: {len(rgb_table)}")
    ranked = find_candidates(limit=args.show)
    if not ranked:
        print("no candidate carried all four Buu colour families")
        return 1
    for score, graphic, counts in ranked:
        print(
            f"  graphic:{graphic.identity.index:<6d} score {score:.2f}  "
            f"skin {counts['skin']:>5d}  cape {counts['cape']:>5d}  "
            f"white {counts['white']:>5d}  outline {counts['outline']:>5d}  "
            f"size {graphic.width}x{graphic.height}"
        )
    score, graphic, counts = ranked[0]
    used = sprite_palette(graphic, rgb_table)
    print(f"\ncanonical: graphic:{graphic.identity.index} ({graphic.width}x{graphic.height})")
    for (index, entry), pixels in used.most_common(24):
        print(f"  idx {index:>3d}  {_hex(entry)}  {pixels:>5d}px  {part_of_sprite(entry, counts)}")
    del session
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
