"""CQA-23, Maps half: ONE owner for the standard undo and redo keys.

The Graphics tab's own `StandardKey.Undo`/`Redo` pair was removed by
CQA-23-GRAPHICS-UNDO-REACHABILITY-001 (commit a5d7b60), which left the shell's
Edit -> Undo/Redo as the single claimant of Ctrl+Z and Ctrl+Y for the window.
The same duplicate pair survived on both Maps surfaces: `MapWorkspaceTab` (the
Objects mode) and `MapBrowserTab` (Browse and Layout) each bound the standard
keys on their own stack actions and added those actions to themselves, so a
window-wide search for actions on Ctrl+Z found three claimants where the shell
should be the only one.

`MapsEditor.undo_stack` (editors.py:423-434) already routes Edit -> Undo to the
ACTIVE mode's history, so the shell reaches every Maps history the two tabs
used to reach by key; their actions keep their toolbar buttons. That is the
same shape the Graphics fix used, and it applies here even though the Maps
surfaces are composites: the router, not the tab's key, is what makes the route
mode-correct.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QAction, QKeySequence, QUndoCommand  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(qapp) -> MainWindow:
    catalog = RomProfileCatalog.load(os.path.join("config", "roms.yaml"))
    shell = MainWindow(Session(), catalog)
    shell.show_editor("Maps")
    return shell


def _owners(root, sequence):
    """Every descendant `QAction` bound to `sequence`, with its owner's class."""
    return [
        (action.text(), type(action.parent()).__name__)
        for action in root.findChildren(QAction)
        if action.shortcut() == sequence
    ]


class _RecordingCommand(QUndoCommand):
    """A command that writes one key of a dict, so undo is observable."""

    def __init__(self, log, key, value):
        super().__init__("record")
        self._log, self._key, self._value = log, key, value

    def redo(self):
        self._log[self._key] = self._value

    def undo(self):
        self._log[self._key] = None


# --- the counted bindings ---------------------------------------------------


def test_only_the_shell_binds_the_standard_keys_in_the_maps_window(window):
    """Three claimants before this fix, one after: the shell's two actions.

    Measured on the pre-fix baseline, a window-wide search for `QAction`s bound
    to `StandardKey.Undo` returned
    `[('Undo', 'MapWorkspaceTab'), ('Undo paint', 'MapBrowserTab'), ('Undo', 'MainWindow')]`,
    and the same three for redo. The two Maps tabs are the duplicate.
    """
    undo = QKeySequence(QKeySequence.StandardKey.Undo)
    redo = QKeySequence(QKeySequence.StandardKey.Redo)

    assert _owners(window, undo) == [("Undo", "MainWindow")]
    assert _owners(window, redo) == [("Redo", "MainWindow")]
    assert window._action_undo.shortcut() == undo
    assert window._action_redo.shortcut() == redo


def test_the_maps_tabs_keep_their_actions_but_lose_the_keys(window):
    """The buttons are the reason the actions survive; the keys are not."""
    workspace = window._maps.workspace
    browser = window._maps.browser

    assert workspace._undo_action.shortcut().isEmpty()
    assert workspace._redo_action.shortcut().isEmpty()
    assert browser._undo_action.shortcut().isEmpty()
    assert browser._redo_action.shortcut().isEmpty()
    assert workspace._undo_action.text() == "Undo"
    assert browser._undo_action.text() == "Undo paint"


# --- the before-fix behaviour, observed ------------------------------------


def test_the_pressed_key_reaches_the_active_maps_history(window):
    """Ctrl+Z delivered to the shown window runs the shell action exactly once.

    This is the observation the fix changes. Measured with the entries present
    on the pre-fix baseline: three actions claimed the standard sequence, and
    `QTest.keyClick(window, Ctrl+Z)` after `window.show()` fired **none** of
    them - Qt resolves a key with several live claimants to nothing, so the key
    simply did not work in this window. With the two tab pairs gone, the same
    probe fires the one shell action and the undo lands on the ACTIVE mode's
    history.
    """
    window._maps.set_mode("objects")
    workspace = window._maps.workspace
    log = {"value": None}
    fired = []
    window._action_undo.triggered.connect(lambda: fired.append(True))

    workspace._undo_stack.push(_RecordingCommand(log, "value", 7))
    window.show()
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()
    assert window._action_undo.isEnabled() is True

    QTest.keyClick(window, Qt.Key_Z, Qt.KeyboardModifier.ControlModifier)
    QApplication.processEvents()

    assert fired == [True], "the standard key did not reach the shell's action"
    assert log["value"] is None, "the key did not reach the Objects history"


# --- no surface lost a working route to its own history ---------------------


def test_objects_mode_undo_still_works_through_the_shell_and_its_button(window):
    """The Objects history the tab's own Ctrl+Z used to reach is still reachable.

    `window._action_undo.trigger()` is what the shell's Ctrl+Z runs, and it goes
    through `MapsEditor.undo_stack`, which answers the Objects mode's stack. The
    tab's own button drives the same one stack, which is why removing the key
    from that action is not a lost route.
    """
    window._maps.set_mode("objects")
    workspace = window._maps.workspace
    log = {"value": None}

    workspace._undo_stack.push(_RecordingCommand(log, "value", 7))
    assert log["value"] == 7
    assert window._active_undo_stack() is workspace._undo_stack

    window._action_undo.trigger()
    assert log["value"] is None, "Edit Undo no longer reaches the Objects history"
    window._action_redo.trigger()
    assert log["value"] == 7

    workspace._undo_button.click()
    assert log["value"] is None, "the Objects Undo button no longer drives its action"
    workspace._redo_button.click()
    assert log["value"] == 7


def test_browse_undo_still_works_through_the_shell_and_its_button(window):
    """Browse and Layout route to the browser's stack, which the buttons drive."""
    window._maps.set_mode("browse")
    browser = window._maps.browser
    log = {"value": None}

    browser._undo_stack.push(_RecordingCommand(log, "value", 3))
    assert window._active_undo_stack() is browser._undo_stack

    window._action_undo.trigger()
    assert log["value"] is None
    window._action_redo.trigger()
    assert log["value"] == 3

    browser._undo_button.click()
    assert log["value"] is None
    browser._redo_button.click()
    assert log["value"] == 3
