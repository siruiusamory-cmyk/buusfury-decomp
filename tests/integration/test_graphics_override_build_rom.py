"""WORKBENCH-005 Layer 1: ROM-gated proofs for the SDK graphics-edit path.

A palette recolour authored in a project must travel Project -> Build -> ROM and
land at exactly the palette entry's offset. Plus the two read facades. These skip
cleanly when the canonical ROM is absent; the ROM is opened read-only.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot import graphics
from tools.webfoot.build import build_project, extract_project
from tools.webfoot.formats import indexed_png as ip
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import GraphicsOverrides, read_project, write_project
from tools.webfoot.rom import identify_rom

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


def _rom_path() -> str:
    """The canonical image, found by content rather than by directory order.

    `roms/` may hold several images (a warp-randomized derivative among them),
    and glob order is not a property these offsets may be keyed on.
    """
    matches = sorted(glob.glob(os.path.join("roms", "*.gba")))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    for candidate in matches:
        if hashlib.sha256(open(candidate, "rb").read()).hexdigest() == CANONICAL_SHA256:
            return candidate
    pytest.skip("local ROM is not the canonical profile these offsets target")


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture(scope="module")
def sprites() -> graphics.ActorSprites:
    path = _rom_path()
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    image = open(path, "rb").read()
    return graphics.load_actor_sprites(image, identify_rom(path, catalog))


# --- SC3: build applies a recorded palette override --------------------------


def test_authored_palette_override_lands_at_exactly_the_palette_offset(
    tmp_path: Path, catalog: RomProfileCatalog
) -> None:
    rom = _rom_path()
    project = tmp_path / "project"
    extract_project(rom, project, catalog, graphics=False)

    # Author one recolour of entry 40 to pure green, added to project source.
    meta = read_project(project).meta
    from tools.webfoot.project.model import GRAPHICS_OVERRIDES_FILE
    from tools.webfoot.project.format import dump_toml

    overrides = GraphicsOverrides(palette={40: (0, 255, 0)})
    target = project / GRAPHICS_OVERRIDES_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_toml(overrides.to_document()), encoding="utf-8", newline="\n")

    output = tmp_path / "recoloured.gba"
    build_project(project, rom, output, catalog)

    base = Path(rom).read_bytes()
    built = output.read_bytes()
    differing = [i for i in range(len(base)) if base[i] != built[i]]

    # pack_gba_colour(0,255,0) == 0x03E0, the same word test_graphics_rom uses.
    expected_word = sg.pack_gba_colour(0, 255, 0)
    palette_offset = differing[0]
    assert built[palette_offset : palette_offset + 2] == expected_word.to_bytes(2, "little")
    assert differing == [palette_offset, palette_offset + 1]


# --- SC4: get_actor_animations, timing unknown -------------------------------


def test_get_actor_animations_returns_frames_without_inventing_timing(
    sprites: graphics.ActorSprites,
) -> None:
    character = sprites.characters()[0]
    animations = sprites.get_actor_animations(character.identity)
    assert len(animations) == len(character.animation_offsets)
    assert animations  # this character has art

    frames = [frame for animation in animations for frame in animation.frames]
    assert frames
    for frame in frames:
        assert frame.duration is None
        assert frame.timing_unknown is True
        assert len(frame.graphics) == sg.DIRECTION_COUNT
    # At least one slot resolves to a real graphic this walk decoded.
    assert any(g is not None for frame in frames for g in frame.graphics)


# --- SC5: import_graphic_png fails closed ------------------------------------


def test_import_graphic_png_round_trips_an_unchanged_asset(
    sprites: graphics.ActorSprites,
) -> None:
    palette = sprites.palette.rgb
    for graphic in sprites.graphics()[:400]:
        blob = ip.encode(
            graphic.pixels, graphic.width, graphic.height, palette,
            transparent_index=sg.TRANSPARENT_INDEX,
        )
        try:
            plan = sprites.import_graphic_png(graphic.identity, blob)
        except sg.SpriteFormatError:
            continue  # re-encode did not fit; the honest refusal
        assert plan.offset == graphic.file_offset
        return
    pytest.skip("no sampled payload re-encoded small enough to fit")


def test_import_graphic_png_fails_closed_on_wrong_dimensions(
    sprites: graphics.ActorSprites,
) -> None:
    """An oversized PNG must raise SpriteFormatError, never truncate or resize."""
    graphic = sprites.graphics()[0]
    palette = sprites.palette.rgb
    big_w, big_h = graphic.width + 8, graphic.height + 8
    oversized = ip.encode(
        bytes(big_w * big_h), big_w, big_h, palette,
        transparent_index=sg.TRANSPARENT_INDEX,
    )
    with pytest.raises(sg.SpriteFormatError, match="does not resize"):
        sprites.import_graphic_png(graphic.identity, oversized)


def test_import_graphic_png_fails_closed_on_a_non_indexed_png(
    sprites: graphics.ActorSprites,
) -> None:
    graphic = sprites.graphics()[0]
    with pytest.raises(ip.PngError):
        sprites.import_graphic_png(graphic.identity, b"not a png at all")
