"""Every character that reaches each sprite word the release-4 fix restored (N7).

The nine restored sites are named by file offset. Six of them sit inside compressed
character animation frames, and a frame can be shared: the atlas's first
reachability path names one character, while the toolkit's own `characters_using`
reports every character that would see the repaired bytes. This prints that full
set, which is what `docs/research/RELEASE4_SPRITEFIX.md` cites and what
`tests/unit/test_spritefix_attribution.py` pins.

Read-only: it opens the image, walks the actor sprites and prints. The three sites
that are not inside a reached graphic (the two uncompressed tile words and the
unclassified one) are reported as such rather than omitted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.graphics import load_actor_sprites  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

#: Restored site offset -> the container that holds it, when one does.
SITES: tuple[tuple[int, int | None], ...] = (
    (0x316A18, None),
    (0x40E178, 0x40E0DC),
    (0x4567CC, 0x4565CC),
    (0x46C29C, 0x46C1D8),
    (0x4D99A8, 0x4D995C),
    (0x545A04, 0x5459C4),
    (0x5C6FB4, 0x5C6DF0),
    (0x725474, None),
    (0x726074, None),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="the canonical image to walk")
    args = parser.parse_args()

    path = Path(args.image)
    sprites = load_actor_sprites(path.read_bytes(), identify_rom(path, load_catalog(None)))
    by_offset = {graphic.file_offset: graphic for graphic in sprites.graphics()}

    for site, container in SITES:
        if container is None:
            print(f"{site:#010x}  inside no reached graphic")
            continue
        graphic = by_offset.get(container)
        if graphic is None:
            print(f"{site:#010x}  container {container:#010x} is not a reached graphic")
            continue
        characters = sprites.characters_using(graphic.identity)
        names = ", ".join(str(item.index) for item in characters)
        print(f"{site:#010x}  container {container:#010x}  {graphic.identity}  "
              f"characters {names}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
