"""The graphic identity numbering rule, on the canonical image (N6).

`GraphicIdentity` numbers a graphics payload by its position in ASCENDING FILE
OFFSET over everything the actor-sprite walk reaches. That makes the number a
function of the image rather than of the walk: the same ROM always yields the same
identity for the same payload, whichever character happens to reach it first.

The rule needs pinning because it is invisible in the identity string and because a
snapshot can disagree with it. `build/atlas/graphics_extents.jsonl` is generated
output, and the copy this project carried gave `graphics.container.1016` for a
payload the code now numbers 1030. A refactor to walk-order enumeration would
renumber every identity the same silent way, so the shape is asserted here rather
than trusted to a comment.

Needs the canonical image; skips without it, like the other ROM-gated families.
"""

from __future__ import annotations

import pytest

from tests.rom_support import canonical_rom_bytes, canonical_rom_path
from tools.webfoot.catalog import load_catalog
from tools.webfoot.graphics import load_actor_sprites
from tools.webfoot.rom import identify_rom


def test_graphic_identities_are_numbered_by_ascending_file_offset() -> None:
    path = canonical_rom_path()
    if path is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    image = canonical_rom_bytes()
    identification = identify_rom(path, load_catalog(None))
    graphics = load_actor_sprites(image, identification).graphics()

    offsets = [graphic.file_offset for graphic in graphics]
    assert offsets == sorted(offsets)
    assert len(set(offsets)) == len(offsets)
    assert [graphic.identity.index for graphic in graphics] == list(range(len(graphics)))
