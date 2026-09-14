"""WORKBENCH-005 Layer 1: SDK graphics-edit unit proofs.

Pure over bytes and text; no ROM. The ROM-gated build proof lives in
`tests/integration/test_graphics_override_build_rom.py`.
"""

from __future__ import annotations

import pytest

from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.project.model import GraphicsOverrides, ProjectLoadError
from tools.webfoot.project import ProjectValidationError


# --- SC1: RGB -> GBA word packing, exact inverse of the decode ---------------


def test_pack_gba_colour_is_the_exact_inverse_of_the_word_decode() -> None:
    """Round-trips for every 5-bit-representable colour, all 32768 words."""
    for word in range(0x8000):
        rgb = sg.Palette(raw=(word,) + (0,) * 255).rgb[0]
        assert sg.pack_gba_colour(*rgb) == word


def test_pack_colour_quantises_to_the_top_five_bits() -> None:
    # 255 -> top 5 bits 31 -> word 0x7FFF; 0 -> 0.
    assert sg.pack_gba_colour(255, 255, 255) == 0x7FFF
    assert sg.pack_gba_colour(0, 0, 0) == 0x0000
    # Channel order is r | g<<5 | b<<10.
    assert sg.pack_gba_colour(255, 0, 0) == 0x001F
    assert sg.pack_gba_colour(0, 255, 0) == 0x03E0
    assert sg.pack_gba_colour(0, 0, 255) == 0x7C00


def test_pack_colour_rounds_to_nearest_not_truncate() -> None:
    # WB-005 L4 FIX #2: a freely-picked value maps to the NEAREST 5-bit step,
    # not the truncated one. Channel 13: old truncating pack (13>>3) = step 1;
    # round-to-nearest = step 2 (13 is closer to 16 than to 8).
    assert 13 >> 3 == 1  # what the old truncating pack produced
    assert sg.pack_gba_colour(13, 0, 0) == 2  # rounds up to the nearer step
    # 250: truncate (250>>3) = 31; round = 30 (250 is nearer step 30's 247).
    assert 250 >> 3 == 31
    assert sg.pack_gba_colour(250, 0, 0) == 30  # rounds down to the nearer step


def test_pack_colour_refuses_out_of_range_channels() -> None:
    with pytest.raises(sg.SpriteFormatError, match="8-bit"):
        sg.pack_gba_colour(256, 0, 0)
    with pytest.raises(sg.SpriteFormatError, match="8-bit"):
        sg.pack_gba_colour(0, -1, 0)


# --- SC2: project graphics-override round trip -------------------------------


def test_palette_override_project_round_trips_to_disk_and_back(tmp_path) -> None:
    overrides = GraphicsOverrides(palette={40: (0, 255, 0), 12: (255, 0, 0)})
    path = tmp_path / "overrides.toml"
    from tools.webfoot.project.format import dump_toml, load_toml

    path.write_text(dump_toml(overrides.to_document()), encoding="utf-8", newline="\n")
    reloaded = GraphicsOverrides.from_document(
        load_toml(path.read_text(encoding="utf-8")), path
    )
    assert reloaded == overrides


def test_graphics_override_write_and_read_through_the_project(tmp_path) -> None:
    from tools.webfoot.project import read_project, write_project
    from tools.webfoot.project.model import ProjectMeta, PROJECT_FORMAT_VERSION

    meta = ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id="p",
        game="g",
        base_rom_sha256="a" * 64,
        base_rom_size=1,
        name="n",
    )
    overrides = GraphicsOverrides(palette={7: (255, 128, 0)})
    write_project(
        tmp_path, meta, enemies=[], characters=[], graphics_overrides=overrides
    )
    loaded = read_project(tmp_path)
    assert loaded.graphics_overrides == overrides


def test_project_without_overrides_loads_with_empty_overrides(tmp_path) -> None:
    from tools.webfoot.project import read_project, write_project
    from tools.webfoot.project.model import ProjectMeta, PROJECT_FORMAT_VERSION

    meta = ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id="p",
        game="g",
        base_rom_sha256="a" * 64,
        base_rom_size=1,
        name="n",
    )
    write_project(tmp_path, meta, enemies=[], characters=[])
    assert read_project(tmp_path).graphics_overrides.palette == {}


def test_override_document_rejects_out_of_range_channel(tmp_path) -> None:
    from tools.webfoot.project.format import load_toml

    doc = load_toml('[palette."007"]\nred = 300\ngreen = 0\nblue = 0\n')
    with pytest.raises(ProjectValidationError, match="outside 0..255"):
        GraphicsOverrides.from_document(doc, tmp_path)


def test_override_document_rejects_unknown_field(tmp_path) -> None:
    from tools.webfoot.project.format import load_toml

    doc = load_toml('[palette."007"]\nred = 0\ngreen = 0\nblue = 0\nalpha = 5\n')
    with pytest.raises(ProjectLoadError, match="unknown field"):
        GraphicsOverrides.from_document(doc, tmp_path)
