"""The character attribution of the restored sprite words, on the canonical image (N7).

`docs/research/RELEASE4_SPRITEFIX.md` names, for each restored site, every character
that reaches the payload it sits in. The first reachability path through the atlas
naming one character was not enough: `characters_using` reports the full set, and two
of the repaired frames are shared by two characters while a third is shared by three.

Those sets are a measured property of the canonical image, so they are pinned here.
A change to the walk that quietly widens or narrows who is affected by the repaired
bytes fails this test instead of going unnoticed, which is the whole point of
recording the attribution at all.

Needs the canonical image; skips without it, like the other ROM-gated families.
"""

from __future__ import annotations

import pytest

from tests.rom_support import canonical_rom_bytes, canonical_rom_path
from tools.webfoot.catalog import load_catalog
from tools.webfoot.graphics import load_actor_sprites
from tools.webfoot.rom import identify_rom

#: site offset -> the container that holds it, when one does.
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

#: container offset -> every character that reaches it. Measured on the canonical
#: image with `characters_using`; the sites with no container have no character.
EXPECTED: dict[int, tuple[int, ...]] = {
    0x40E0DC: (33,),
    0x4565CC: (42, 43),
    0x46C1D8: (42, 43),
    0x4D995C: (99,),
    0x5459C4: (114,),
    0x5C6DF0: (123, 177, 220),
}


def test_every_character_that_reaches_a_restored_frame_is_recorded() -> None:
    path = canonical_rom_path()
    if path is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    image = canonical_rom_bytes()
    sprites = load_actor_sprites(image, identify_rom(path, load_catalog(None)))
    by_offset = {graphic.file_offset: graphic for graphic in sprites.graphics()}

    measured = {}
    for _site, container in SITES:
        if container is None:
            continue
        graphic = by_offset.get(container)
        assert graphic is not None, f"container {container:#x} is not a reached graphic"
        measured[container] = tuple(
            item.index for item in sprites.characters_using(graphic.identity))
    assert measured == EXPECTED
