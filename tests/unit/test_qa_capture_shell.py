"""The QA capture harness targets the current editor-strip shell, and refuses.

`tools/qa/visual_pass_capture.py` produced the published captures, so a path in it
that silently resolves to the wrong surface is worse than a crash: it photographs
one editor and files it under another's name. These tests pin that resolution goes
through the shell's own editor-host registry, that the Maps modes are driven and
checked, and that the retired multi-tab shell is gone from the module entirely.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tools.qa import visual_pass_capture as vpc  # noqa: E402
from tools.webfoot.workbench.app import (  # noqa: E402
    MainWindow,
    _EDITORS,
)
from tools.webfoot.workbench.atlas_browser import AtlasBrowserTab  # noqa: E402
from tools.webfoot.workbench.editors import MapsEditor  # noqa: E402
from tools.webfoot.workbench.graphics_tab import GraphicsTab  # noqa: E402
from tools.webfoot.workbench.inspector import InspectorTab  # noqa: E402
from tools.webfoot.workbench.scene_tab import SceneTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def harness(qapp, tmp_path):
    """A harness over the real shell, built the way the capture tool builds it.

    The output directory is created the way `main` creates it before any state
    runs, because `grab` writes straight into it and `QPixmap.save` returns False
    rather than raising when the directory is missing.
    """
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    value = vpc.Harness(out, tmp_path / "workspace")
    value.pump(2)
    return value


# --- editor resolution -------------------------------------------------------


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Atlas", AtlasBrowserTab),
        ("Inspector", InspectorTab),
        ("Maps", MapsEditor),
        ("Graphics", GraphicsTab),
        ("Scene", SceneTab),
    ],
)
def test_each_editor_resolves_to_its_live_widget(harness, name, expected):
    """Every editor the shell has resolves to that editor's own widget.

    `Scene` is in the registry but not on the strip, so this also pins that the
    harness reaches the detail editor the placement flow opens.
    """
    widget = harness.editor(name)
    assert isinstance(widget, expected)


def test_the_resolver_covers_exactly_the_shells_editors(harness):
    """`editors()` reports the shell's registry, not a second hard-coded list."""
    assert set(harness.editors()) == set(harness.window._hosts)
    for name in _EDITORS:
        assert name in harness.editors()


def test_an_unknown_editor_fails_loudly(harness):
    """A name this shell cannot show is refused, never substituted."""
    with pytest.raises(SystemExit) as excinfo:
        harness.editor("Map")
    message = str(excinfo.value)
    assert "unknown editor 'Map'" in message
    # The refusal names what does exist, so the caller can correct the capture.
    assert "Atlas" in message and "Maps" in message


def test_showing_an_unknown_editor_fails_loudly(harness):
    """`MainWindow.show_editor` returns silently; the harness must not."""
    with pytest.raises(SystemExit, match="unknown editor 'Warps'"):
        harness.show_editor("Warps")


def test_showing_an_editor_makes_it_the_shown_one(harness):
    for name in ("Atlas", "Inspector", "Maps", "Graphics"):
        harness.show_editor(name)
        assert harness.window._hosts[name].isVisible()
        others = [n for n in harness.editors() if n != name]
        assert not any(harness.window._hosts[n].isVisible() for n in others)


# --- Maps modes --------------------------------------------------------------


def test_every_maps_mode_is_selectable_and_lands(harness):
    """Each mode the product offers becomes the shown mode."""
    harness.show_editor("Maps")
    for key in ("browse", "layout", "objects", "warps"):
        harness.maps.set_mode(key)
        assert harness.maps.mode() == key
        assert harness.editor("Maps").mode() == key


def test_an_unknown_maps_mode_fails_loudly(harness):
    """A mode the strip does not have is refused rather than silently ignored."""
    harness.show_editor("Maps")
    harness.maps.set_mode("browse")
    with pytest.raises(SystemExit) as excinfo:
        harness.maps.set_mode("teleport")
    assert "unknown Maps mode 'teleport'" in str(excinfo.value)
    # And the refusal did not move the surface it was asked to move.
    assert harness.maps.mode() == "browse"


def test_maps_accessors_reach_the_current_editor(harness):
    """The accessor drives the real Maps editor, not a retired-shell stand-in."""
    harness.show_editor("Maps")
    editor = harness.editor("Maps")
    assert harness.maps.browser is editor.browser
    assert harness.maps.warps is editor.warps
    assert harness.maps.workspace is editor.workspace
    assert harness.browser is editor.browser


# --- the retired shell -------------------------------------------------------


def test_the_module_keeps_no_retired_tab_path():
    """No lookup may reach a tab strip, a legacy index or a shell fallback.

    Source-level on purpose: the failure this guards against is a *reachable*
    fallback, and importing the module cannot prove absence.
    """
    source = Path(vpc.__file__).read_text(encoding="utf-8")
    for retired in (
        "_tabs",
        "_LegacyMaps",
        "_LEGACY_MAP_INDEX",
        "show_tab",
        "tab_name",
        "TAB_ATLAS",
        "TAB_BROWSER",
        "TAB_MAPS",
    ):
        assert retired not in source, f"retired shell path {retired!r} is back"


def test_the_module_exposes_no_tab_accessor():
    assert not hasattr(vpc.Harness, "tab")
    assert not hasattr(vpc.Harness, "tabs")
    assert not hasattr(vpc.Harness, "show_tab")
    assert not hasattr(vpc, "_LegacyMaps")


def test_a_window_without_the_host_registry_is_refused(qapp, tmp_path, monkeypatch):
    """The harness targets the current shell, and says so when it is not given it."""
    harness = vpc.Harness(tmp_path / "out", tmp_path / "workspace")
    monkeypatch.delattr(harness.window, "_hosts", raising=False)
    with pytest.raises(SystemExit, match="no editor host registry"):
        harness.editor("Maps")


# --- capture output ----------------------------------------------------------


def test_a_capture_of_a_named_editor_writes_the_state_png(harness):
    """The shot lands under the state's own name, through the new navigation.

    This is the end-to-end contract the published captures depend on: select an
    editor by name, grab the shell, get the PNG the state list names.
    """
    harness.show_editor("Maps")
    path = harness.grab("02-maps-browse")
    assert path == harness.out / "02-maps-browse.png"
    assert path.is_file()
    assert path.stat().st_size > 0


def test_the_narrow_capture_still_resizes_the_shell(harness):
    harness.show_editor("Maps")
    path = harness.grab("05-maps-narrow", size=vpc.NARROW)
    assert path.is_file()
    assert harness.window.size() == vpc.NARROW


def test_the_state_names_are_unchanged(harness):
    """Output naming is a published contract, so the state list keeps its names."""
    names = dict(vpc.STATES)
    assert names[2] == "02-maps-browse"
    assert names[3] == "03-maps-layout"
    assert names[40] == "40-retail-map-before-resize"

