"""Unit tests for the Map Browser facade's ROM-free pieces.

Synthetic only: no ROM, no extracted assets. The ROM-coupled behaviour is pinned
in the ROM-gated integration suite (`tests/integration/test_map_browser_rom.py`).
"""

from __future__ import annotations

import pytest

from tools.export import map_browser as mb
from tools.export import profile_authority

PALETTE = tuple((i, i, i) for i in range(256))


def _layer(slot: int, addend: int, width: int, height: int, value: int) -> mb.MapBrowserLayer:
    return mb.MapBrowserLayer(
        slot=slot,
        classification="dominant",
        handler=0x08008087,
        addend=addend,
        width=width,
        height=height,
        pixels=bytes([value]) * (width * height),
    )


def test_rgba_expands_index0_transparent_and_others_opaque() -> None:
    rgba = mb.rgba(bytes([0, 7, 255]), PALETTE)
    # 3 pixels x 4 channels (RGBA). Index 0 is a transparent hole.
    assert rgba[3] == 0
    assert rgba[4] == 7 and rgba[5] == 7 and rgba[6] == 7 and rgba[7] == 255
    assert rgba[11] == 255


def test_compose_draws_lower_addend_on_top() -> None:
    bottom = _layer(1, 3, 2, 1, 0x11)
    top = _layer(0, 2, 2, 1, 0x22)
    assert mb.compose((top, bottom), 2, 1) == bytes([0x22, 0x22])


def test_compose_treats_index0_as_transparent() -> None:
    bottom = _layer(1, 3, 2, 1, 0x11)
    top = _layer(0, 2, 2, 1, 0)
    assert mb.compose((top, bottom), 2, 1) == bytes([0x11, 0x11])


def test_compose_refuses_a_mismatched_layer() -> None:
    with pytest.raises(mb.MapBrowserError):
        mb.compose((_layer(0, 2, 3, 1, 0x22),), 2, 1)


def test_render_map_rejects_an_out_of_range_index() -> None:
    with pytest.raises(mb.MapBrowserError):
        mb.render_map(b"", 452)


def test_read_map_index_rejects_a_non_canonical_rom() -> None:
    """The refusal names the profile whose identity the reader resolves against."""
    with pytest.raises(mb.MapBrowserError, match="profile 'buus_fury_usa_rev0_01c1707f'"):
        mb.read_map_index(b"\x00" * 8_388_608)


def test_render_map_rejects_a_non_canonical_rom() -> None:
    with pytest.raises(mb.MapBrowserError, match="profile 'buus_fury_usa_rev0_01c1707f'"):
        mb.render_map(b"\x00" * 8_388_608, 0)


def test_the_reader_bound_is_the_profiles_declared_map_count() -> None:
    """The map-index bound is the profile declaration, not a literal.

    `render_map(b"", 452)` is refused for the empty image as well as the index,
    so this asserts the specific bound by comparing against the resolved
    profile rather than against the number 452.
    """
    profile = profile_authority.canonical_export_profile()
    assert profile.map_entries is not None
    just_past = profile.map_entries.count
    with pytest.raises(mb.MapBrowserError, match=f"0\\.\\.{just_past - 1}"):
        mb.map_label(b"\x00" * 8_388_608, just_past)
