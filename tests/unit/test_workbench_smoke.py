"""T1.4 headless GUI smoke test for the workbench `MainWindow`.

Proves the window constructs and the shell's structure contract holds. The
contract was re-pointed by `DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`'s human
correction: the shell is a ROM-editor layout - menu bar, one compact editor
strip, then the active editor - not a global tab strip listing every
implementation panel.

What is asserted now:

- the four primary editors are exactly Atlas, Inspector, Maps, Graphics;
- the shell opens on Atlas;
- Build, Launch and the Scene editor are reachable but are NOT primary
  destinations, because they are a project action, a project action, and a
  relation of a selected placement respectively;
- the menu bar carries the five ROM-editor menus.

Offscreen Qt is set BEFORE PySide6 is imported; the whole module skips cleanly
if PySide6 (or the offscreen plugin) is unavailable, so CI without Qt does not
error.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Skip the module if PySide6 or the offscreen platform plugin can't init.
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.workbench.app import _EDITORS  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    # Singleton-safe: reuse the process-wide QApplication if one exists.
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


@pytest.fixture(scope="module")
def window(qapp):
    catalog = RomProfileCatalog.load("config/roms.yaml")
    return MainWindow(Session(), catalog)


def test_primary_editors_are_the_four_workspaces(window) -> None:
    """Only editors where a user works are primary destinations."""
    assert _EDITORS == ("Atlas", "Inspector", "Maps", "Graphics")
    assert set(window._editor_buttons) == set(_EDITORS)


def test_shell_opens_on_atlas(window) -> None:
    assert window.current_editor_name() == "Atlas"
    assert window._editor_buttons["Atlas"].isChecked()


def test_every_primary_editor_can_be_shown(window) -> None:
    for title in _EDITORS:
        window.show_editor(title)
        assert window.current_editor_name() == title
        assert window._editor_buttons[title].isChecked()
    window.show_editor("Atlas")


def test_project_actions_are_not_primary_destinations(window) -> None:
    """Build and Run are project actions; they must not be editor destinations."""
    assert "Build" not in _EDITORS
    assert "Launch" not in _EDITORS
    assert "Build" not in window._hosts
    assert "Launch" not in window._hosts
    # ...but neither is deleted: each has a surface the actions open.
    assert window._build is not None
    assert window._launcher is not None


def test_scene_editor_is_reached_from_a_placement_not_the_strip(window) -> None:
    """The Scene editor is a relation of a selected placement, not a workspace."""
    assert "Scene" in window._hosts
    assert "Scene" not in _EDITORS
    # It is only offered while the Maps editor is in its Objects mode.
    window.show_editor("Maps")
    window._maps.set_mode("browse")
    assert not window._scene_action.isEnabled()
    window._maps.set_mode("objects")
    assert window._scene_action.isEnabled()
    window.show_editor("Atlas")


def test_menu_bar_carries_the_rom_editor_menus(window) -> None:
    labels = [action.text().replace("&", "") for action in window.menuBar().actions()]
    assert labels == ["File", "Edit", "View", "Tools", "Help"]
