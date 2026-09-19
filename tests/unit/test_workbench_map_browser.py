"""Focused interaction tests for the read-only Map Browser tab.

Synthetic only: the ROM-touching facade functions are monkeypatched so the tab's
list, search, selection, layer-toggle, info-panel and error paths are exercised
headlessly without a ROM.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tools.export import map_browser as mb  # noqa: E402
from tools.webfoot.workbench import map_browser_tab as mbt  # noqa: E402
from tools.webfoot.workbench.map_browser_tab import MapBrowserTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _entry(index: int, name: str | None) -> mb.MapIndexEntry:
    return mb.MapIndexEntry(index=index, name=name, text_index=0 if name else None)


def _result(index: int, *, width: int = 512, height: int = 512) -> mb.MapBrowserResult:
    layer = mb.MapBrowserLayer(
        slot=0,
        classification="dominant",
        handler=0x08008087,
        addend=2,
        width=width,
        height=height,
        pixels=bytes([5]) * (width * height),
    )
    return mb.MapBrowserResult(
        index=index,
        name=None,
        width=width,
        height=height,
        layers=(layer,),
        composite=layer.pixels,
        palette=tuple((i, i, i) for i in range(256)),
        warnings=("composite placement is derived",),
    )


@pytest.fixture
def tab(qapp, monkeypatch):
    entries = (_entry(0, "West City"), _entry(1, None), _entry(2, "Buu's House"))
    calls: list[int] = []
    monkeypatch.setattr(mbt.mb, "read_map_index", lambda rom: entries)

    def render(rom, index):
        calls.append(index)
        return _result(index)

    monkeypatch.setattr(mbt.mb, "render_map", render)
    value = MapBrowserTab(Session(rom_image=b"synthetic"))
    value.on_session_changed()
    value._render_calls = calls
    return value


def test_list_uses_names_and_neutral_fallbacks(tab):
    texts = [tab._list.item(i).text() for i in range(tab._list.count())]
    assert texts == ["West City  ·  map:0000", "map:0001", "Buu's House  ·  map:0002"]


def test_search_filters_by_name_and_identity(tab):
    tab._search.setText("west")
    assert not tab._list.item(0).isHidden()
    assert tab._list.item(1).isHidden()
    assert tab._list.item(2).isHidden()

    tab._search.setText("map:0001")
    assert tab._list.item(0).isHidden()
    assert not tab._list.item(1).isHidden()
    assert tab._list.item(2).isHidden()

    tab._search.setText("")
    assert all(not tab._list.item(i).isHidden() for i in range(tab._list.count()))


def test_selection_renders_on_demand_and_fills_info_panel(tab):
    tab._list.setCurrentRow(0)
    assert tab._render_calls == [0]
    assert tab._identity.text() == "map:0000"
    assert tab._dimensions.text() == "512 × 512 px"
    assert tab._layer_count.text() == "1 graphical · 1 slot(s)"
    assert tab._layer_types.text() == "BG0 · dominant (512×512)"
    assert tab._notes.text() == "composite placement is derived"


def test_render_cache_skips_redundant_work(tab):
    tab._list.setCurrentRow(0)
    tab._list.setCurrentRow(0)
    assert tab._render_calls == [0]


def test_layer_toggle_recomposes_visible_layers(tab, monkeypatch):
    composed: list[list] = []
    monkeypatch.setattr(mbt.mb, "compose", lambda visible, w, h: composed.append(list(visible)) or b"")
    monkeypatch.setattr(mbt.mb, "rgba", lambda indices, palette: b"\x00" * (512 * 512 * 4))
    tab._list.setCurrentRow(0)
    composed.clear()

    check = tab._layer_checks[0]
    check.setChecked(False)  # no visible layers: short-circuits, no compose
    assert composed == []

    check.setChecked(True)  # one visible layer: compose runs once
    assert len(composed) == 1 and len(composed[-1]) == 1


def test_render_error_is_a_message_not_a_crash(tab, monkeypatch):
    def boom(rom, index):
        raise mb.MapBrowserError("boom")

    monkeypatch.setattr(mbt.mb, "render_map", boom)
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "warning", lambda *args: errors.append(args[-1]))

    tab._list.setCurrentRow(0)
    assert errors == ["boom"]
    assert tab._current is None


def test_index_error_is_a_message_not_a_crash(tab, monkeypatch):
    def boom(rom):
        raise mb.MapBrowserError("cannot enumerate maps")

    monkeypatch.setattr(mbt.mb, "read_map_index", boom)
    errors: list[str] = []
    monkeypatch.setattr(mbt.QMessageBox, "critical", lambda *args: errors.append(args[-1]))

    tab.on_session_changed()
    assert errors == ["cannot enumerate maps"]
    assert tab._list.count() == 0
