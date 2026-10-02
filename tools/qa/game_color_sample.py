"""QA tooling: sample the REAL Buu's Fury palette from the game's own output.

Reads actual rendered game material through the shipped SDK - decoded sprites,
rendered maps, and the game's own ROM palette - and reports representative colours
per visual range. This is the evidence behind `docs/research/UI_GAME_COLOR_SOURCE.md`.

Nothing here generates artwork or invents a colour: every value printed is read
from bytes the game itself supplies.

Run:

    python -m tools.qa.game_color_sample --out docs/research/UI_GAME_COLOR_SOURCE.md
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

def _hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Hue in degrees, saturation and value in 0..1."""
    import colorsys

    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360.0, s, v


def _in(hue: float, low: float, high: float) -> bool:
    return low <= hue < high


#: The ranges the colour direction asks for, as hue bands over hue/saturation/value.
#: A band is how image tools classify colour and it is what makes the study
#: reproducible: the same number always lands in the same range, so "the game's
#: blue" cannot quietly become "the blue I wanted". Brightness and saturation gates
#: keep near-black shadows and near-white highlights out of every band.
RANGES = {
    "dark blue / blue-gray": lambda h, s, v: _in(h, 195, 260) and v < 0.72 and s > 0.18,
    "sky / water / ki blue": lambda h, s, v: _in(h, 195, 260) and v >= 0.55 and s > 0.35,
    "cyan": lambda h, s, v: _in(h, 165, 195) and s > 0.30 and v > 0.35,
    "forest / grass green": lambda h, s, v: _in(h, 70, 165) and s > 0.28 and v > 0.20,
    "orange": lambda h, s, v: _in(h, 20, 45) and s > 0.45 and v > 0.45,
    "red": lambda h, s, v: (_in(h, 0, 20) or _in(h, 345, 360)) and s > 0.45 and v > 0.35,
    "purple": lambda h, s, v: _in(h, 260, 320) and s > 0.25 and v > 0.25,
    "earth / sand": lambda h, s, v: _in(h, 20, 55) and 0.15 < s <= 0.55 and v > 0.40,
    "light neutral": lambda h, s, v: s <= 0.16 and v >= 0.72,
}


def _hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _sprites():
    """The decoded sprite façade for the canonical image, or None."""
    from tools.webfoot import cli as cli_module
    from tools.webfoot.workbench import session as workbench_session
    from tools.webfoot.cli import load_catalog
    from tools.webfoot.workbench.session import Session

    # The worktree holds no `build/` of its own (it is generated and ignored), so
    # point the CLI's default atlas directory at the configured one rather than
    # creating a junction git will refuse to resolve.
    atlas = Path(os.environ.get("DBZ_QA_ATLAS_DIR", _ROOT / "build" / "atlas"))
    resolver = lambda: atlas  # noqa: E731 - a one-line stand-in
    cli_module._default_atlas_directory = resolver
    workbench_session._default_atlas_directory = resolver

    rom = Path(os.environ.get("DBZ_QA_ROM", _ROOT / "roms"))
    candidates = sorted(rom.glob("*Buu*Fury*.gba")) if rom.is_dir() else []
    if not candidates:
        return None, None
    session = Session()
    session.open_rom(candidates[0], load_catalog(None))
    return session, session.sprites


def collect() -> dict[str, Counter]:
    """Every game-sourced pixel, bucketed by range."""
    found: dict[str, Counter] = {name: Counter() for name in RANGES}
    session, sprites = _sprites()
    if sprites is None:
        return found
    # The game's own object palette is the single richest source: 256 real colours,
    # as the SDK decodes them (`Palette.rgb`).
    try:
        rgb = [tuple(int(channel) for channel in entry[:3])
               for entry in sprites.palette.rgb]
    except Exception:  # noqa: BLE001 - a QA probe, never a production path
        rgb = []

    def bucket(r: int, g: int, b: int, weight: int) -> None:
        h, s, v = _hsv(r, g, b)
        for name, predicate in RANGES.items():
            if predicate(h, s, v):
                found[name][(r, g, b)] += weight

    for entry in rgb:
        if max(entry) < 12:
            continue  # index 0 is the transparent slot in most banks
        bucket(*entry, 25)  # the palette is authoritative: weight it up

    # Then real sprite pixels, so the counts reflect actual artwork rather than one
    # palette table.
    try:
        graphics = sprites.graphics()[:400]
    except Exception:  # noqa: BLE001
        graphics = []
    for graphic in graphics:
        for index in graphic.pixels:
            if not (0 <= index < len(rgb)):
                continue
            bucket(*rgb[index], 1)
    return found


def _muted(rgb, keep: float) -> tuple[int, int, int]:
    """The same hue pulled toward a dark neutral for desktop chrome.

    `keep` is how much of the original saturation survives. A 1.0 keeps the game
    colour exactly, which belongs on the canvas and never on a panel.
    """
    r, g, b = rgb
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    return tuple(int(gray + (channel - gray) * keep) for channel in (r, g, b))


def report(found: dict[str, Counter]) -> str:
    lines = [
        "# UI game colour source study",
        "",
        "`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`, colour-direction revision. This",
        "file is the evidence that the workbench palette is derived from **Buu's",
        "Fury itself** rather than from a generic dark-theme recipe. Every colour",
        "below was sampled from material the game supplies: its own decoded object",
        "palette and the pixels of its decoded sprites, read through the shipped SDK",
        "by `tools/qa/game_color_sample.py`.",
        "",
        "No colour here is generated, guessed, or taken from promotional artwork.",
        "",
        "## How the sample was taken",
        "",
        "```text",
        "python -m tools.qa.game_color_sample",
        "```",
        "",
        "Sources, in order of authority:",
        "",
        "1. the canonical image's **decoded object palette** (256 real RGB entries,",
        "   weighted as the authoritative source because the game indexes it);",
        "2. the **decoded pixels of the first 400 sprites**, so the counts reflect",
        "   actual artwork rather than one table.",
        "",
        "## Sampled source colours",
        "",
        "| Visual range | Source | Sampled | Muted for chrome | UI role |",
        "|---|---|---|---|---|",
    ]

    roles = {
        "dark blue / blue-gray": ("shell background, panels, borders", 0.55),
        "sky / water / ki blue": ("selection and primary interaction", 0.42),
        "cyan": ("keyboard focus, active mode", 0.40),
        "forest / grass green": ("valid / safe / confirmed", 0.34),
        "orange": ("authored-content marker, rare emphasis (`accent_secondary`)", 0.30),
        "red": ("destructive / error / validation failure", 0.32),
        "purple": ("research / specialized state", 0.30),
        "earth / sand": ("neutral surfaces and secondary text warmth", 0.16),
        "light neutral": ("primary text", 0.06),
    }
    for name, predicate in RANGES.items():
        counter = found.get(name) or Counter()
        if not counter:
            lines.append(f"| {name} | (none sampled) | | | {roles[name][0]} |")
            continue
        # The most common colour in the range is the game's own representative;
        # ties break on the more saturated entry, which is the more distinctive one.
        top = max(
            counter.items(),
            key=lambda item: (item[1], max(item[0]) - min(item[0])),
        )
        raw = top[0]
        keep = roles[name][1]
        lines.append(
            f"| {name} | decoded palette + {top[1]:,} sprite pixels | "
            f"`{_hex(raw)}` | `{_hex(_muted(raw, keep))}` | {roles[name][0]} |"
        )

    lines += [
        "",
        "## How much each colour was muted",
        "",
        "A game colour is not a UI colour. Buu's Fury's artwork is pitched for a",
        "240x160 screen at high saturation; a panel of that saturation at desktop",
        "size is unreadable and it competes with the map. Each sampled colour was",
        "pulled a measured amount toward its own luminance, and the exact factor is",
        "recorded above:",
        "",
        "- **0.55** for the shell: the game's dark blues stay recognisably blue but",
        "  dark enough for a background.",
        "- **0.30-0.42** for the interaction and semantic colours: enough to read as",
        "  the game's own hue, far enough from it that chrome never fights artwork.",
        "- **0.34** for green and **0.32** for red: semantic roles must stay clearly",
        "  distinguishable from each other under red-green colour blindness, which",
        "  is why they are not muted further and never carry state by hue alone.",
        "- **0.16** and **0.06** for neutrals: type stays neutral. Ordinary text is",
        "  never tinted with a game colour.",
        "",
        "## The rule this encodes",
        "",
        "```text",
        "GAME-INSPIRED, NOT GAME-THEMED",
        "```",
        "",
        "The source is the game. The *code* names UI semantics, never game objects:",
        "`selection`, `accent_secondary`, `success`, `danger`, `research`. There is no",
        "`kiBlue` and no `gokuOrange` in the workbench, because a role name that",
        "describes the inspiration rather than the purpose cannot survive the next",
        "art-direction change.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the study to this path")
    args = parser.parse_args(argv)
    found = collect()
    text = report(found)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
