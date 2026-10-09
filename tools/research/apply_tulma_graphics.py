"""Tulma's graphics in the friend v3 image, as a preset over the reusable sprite-swap engine.

WHAT THIS IS NOW. The engine lives in `tools/webfoot/sprite_swap.py` and the invocable front end
in `tools/webfoot/character_swap.py`; this module is the ticket's own invocation of them, and it
exists so the ticket's measurements stay reproducible through one command. A future swap should
be a spec for `character_swap`, not another writer.

THE TARGET, AND THE TRAP THIS AVOIDS. In the foundation the only appearance record whose label
reads `Bulma` is record 22, which is retail CHI-CHI. Retail BULMA is record 20, labelled `Tulma`
there. Nothing here keys on a label: the target is the sprite-definition registry entry for
sprite id 41 and portrait slot 17, and both are address-identical in the canonical image and in
the foundation this ticket extends.

WHAT IS WRITTEN. Nine populated facing containers across three slots, plus the portrait, from
four supplied PNGs. Each sheet is the donor's own art recoloured, cropped to the 16-wide window
at x=8 of each 32x32 cell, so no pixel is dropped and every colour is already carried by the
object palette at 5-bit resolution. The palette is not written at all.

The report is the same shape this ticket's evidence record cites: base and output digests, the
diff confinement, the reopen check, and every container record with its reference words.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The repository root, so this preset runs as a script as well as a module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.webfoot import character_swap as cs  # noqa: E402
from tools.webfoot.sprite_swap import (ANIMATION_ARRAY_OFFSET, CHROMA_KEY, DONOR_GEOMETRY,  # noqa: E402
                                       OBJECT_PALETTE_ADDRESS, PORTRAIT_ARRAY_ADDRESS,
                                       REGISTRY_TABLE_ADDRESS, SPRITE_ID_BASE, Cell, Plan,
                                       PortraitSwap, SheetSlot, SpriteGeometry, SpriteSwap,
                                       SpriteSwapError, Target, Write, apply, containers,
                                       file_offset, index_for_colour, mirror, palette_indices,
                                       plan_container, plan_portrait, raster_from_png, read_u32,
                                       sha256, swap, verify, verify_reopen)

TICKET = "FRIEND-V3-TULMA-GRAPHICS-001"

#: The run index of sprite id 41: ids run 10..306, so index = id - 10.
BULMA_SPRITE_ID = 41
BULMA_CHARACTER_INDEX = BULMA_SPRITE_ID - SPRITE_ID_BASE
BULMA_PORTRAIT_SLOT = 17
PORTRAIT_SIDE = 64
#: The three populated slots of sprite 41, and the sheet that fills each. Slot 1 is walk by
#: frame count alone (4 per facing); stand against arms-up is the raised silhouette. Slots 2..11
#: are null and carry no art.
SHEET_SLOTS = (SheetSlot(0, "stand.png", 2), SheetSlot(1, "walk.png", 4),
               SheetSlot(12, "arms_up.png", 2))
#: One 16x32 piece at anchor (0,-24), which is the composition size the structure declares.
FRAME_WIDTH, FRAME_HEIGHT = DONOR_GEOMETRY.frame_width, DONOR_GEOMETRY.frame_height
FRAME_ANCHOR = DONOR_GEOMETRY.frame_anchor
COMPOSITION_SIZE = DONOR_GEOMETRY.composition_size
CELL_SIDE = DONOR_GEOMETRY.cell_side
CELL_CROP_X = DONOR_GEOMETRY.crop_x

TULMA_SPRITE = SpriteSwap(sprite_id=BULMA_SPRITE_ID, slots=SHEET_SLOTS,
                          geometry=DONOR_GEOMETRY)
TULMA_PORTRAIT = PortraitSwap(slot=BULMA_PORTRAIT_SLOT, png="portrait.png", side=PORTRAIT_SIDE)

#: The engine's error type, under the name this ticket's tests and record already use.
TulmaGraphicsError = SpriteSwapError


def donor_cells(data: bytes, assets: Path) -> list[Cell]:
    """The donor walk, bound to this ticket's sprite."""
    from tools.webfoot import sprite_swap
    return sprite_swap.donor_cells(data, assets, TULMA_SPRITE)


def run(base_path: Path, expect_sha256: str, assets: Path, out_path: Path,
        report_path: Path) -> dict:
    """Reproduce this ticket's candidate from the base, the four assets and the digest."""

    def transform(image: bytes) -> tuple[bytes, dict]:
        out, report = swap(image, assets, sprites=(TULMA_SPRITE,), portraits=(TULMA_PORTRAIT,))
        report.update({
            "ticket": TICKET,
            "base_path": str(base_path),
            "base_sha256": sha256(image),
            "base_size": len(image),
            "output_path": str(out_path),
            "output_sha256": sha256(out),
            "output_size": len(out),
        })
        return out, report

    return cs.guarded_apply(base_path, expect_sha256, out_path, report_path, transform,
                            error=SpriteSwapError)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = run(args.base, args.expect_sha256, args.assets, args.out, args.report)
    except (SpriteSwapError, cs.WriteError) as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(f"output  {report['output_sha256']}  {report['output_size']} bytes")
    print(f"wrote   {report['containers_written']} containers")
    print(f"diff    {report['diff']['changed_bytes_inside_declared_spans']} inside, "
          f"{report['diff']['changed_bytes_outside']} outside")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
