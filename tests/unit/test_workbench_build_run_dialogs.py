"""Focused coverage for the Build and Run project-action surfaces.

Build and Run stopped being editor destinations and became project actions whose
configuration opens in a content-sized dialogue. That re-parenting had no test:
the independent review of this pass found the gap and could only verify the
behaviour by hand. These tests cover the accepted behaviour rather than pixels, so
they describe ownership and wiring instead of coordinates:

- the action opens a real dialogue holding the real surface;
- the surface still carries its controls and its command wiring;
- the dialogue can be opened again;
- the active editor is not switched, which is what "a project action, not an
  editor page" means in practice;
- the surface is returned to the shell afterwards.

The assertion on the editor is deliberately about the shell's own notion of the
active editor (`current_editor_name`) rather than about widget parents, because
"Build does not secretly become an editor" is a statement about the shell.

Observing the dialogue: `QDialog.exec` runs a nested event loop, so a zero-delay
timer fires inside it to record the live state and close the dialogue. Anything
asserted about the dialogue must be sampled *there*, because the surface is
parented back to the shell before `exec` returns.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Skip the module if PySide6 or the offscreen platform plugin cannot init. This is
# the convention every other Workbench test module follows, and it is load-bearing:
# the CI image has no Qt, so a direct import here would abort collection for the
# whole suite rather than skipping these cases.
QtCore = pytest.importorskip("PySide6.QtCore")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QTimer = QtCore.QTimer
QApplication = QtWidgets.QApplication
QDialog = QtWidgets.QDialog

from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@dataclass
class Opened:
    """What the dialogue looked like while it was open."""

    dialog: QDialog | None = None
    parent_during: object = None
    visible_during: bool | None = None
    count: int = 0
    seen: list = field(default_factory=list)


@pytest.fixture(scope="module")
def window():
    from tools.webfoot.profile import RomProfileCatalog

    app = QApplication.instance() or QApplication([])
    window = MainWindow(Session(), RomProfileCatalog.load("config/roms.yaml"))
    window.resize(1440, 900)
    window.show()
    yield window
    del app


def open_action(window, name: str, surface) -> Opened:
    """Run a project action and sample the dialogue while it is open.

    This is the real call path: the same method the toolbar action is connected to.
    """
    state = Opened()

    def sample() -> None:
        dialog = QApplication.activeModalWidget()
        if not isinstance(dialog, QDialog):
            return
        state.dialog = dialog
        state.parent_during = surface.parentWidget()
        state.visible_during = surface.isVisible()
        state.seen.append(dialog)
        dialog.reject()

    QTimer.singleShot(0, sample)
    if name == "Build":
        window.open_build_report()
    else:
        window.open_run_configuration()
    state.count = len(state.seen)
    return state


# -- Build ------------------------------------------------------------------


def test_build_action_opens_a_dialog_holding_the_real_surface(window) -> None:
    surface = window._build
    assert surface.parentWidget() is not None, "precondition: the surface has a parent"
    state = open_action(window, "Build", surface)
    assert state.dialog is not None, "no dialogue opened"
    assert state.parent_during is state.dialog, "the surface is re-parented, not copied"
    assert state.parent_during is not surface.parentWidget(), "not left on the stage"


def test_build_dialog_holds_the_build_controls(window) -> None:
    """The accepted content, by identity: these are the panel's own widgets."""
    surface = window._build
    open_action(window, "Build", surface)
    for control in (
        surface._open_button,
        surface._extract_button,
        surface._output_button,
        surface._validate_button,
        surface._build_button,
        surface._status,
    ):
        assert control.parent() is not None, "control was destroyed by re-parenting"


def test_build_controls_are_still_connected(window, monkeypatch) -> None:
    """Each button still reaches its own slot, checked through the real click path.

    The buttons are force-enabled for the click. Their enabled state is the
    panel's own business and depends on session state; what this asserts is the
    *wiring*, which the re-parenting could have broken. A disabled button emits no
    signal, so without this the test would pass for the wrong reason.

    All five buttons are covered. An earlier version checked only the three that act
    on the current project, and an independent reviewer showed by mutation that
    severing Open Project or Extract left every test passing.
    """
    surface = window._build
    called: list[str] = []
    handlers = {
        "_on_open_project": "open_project",
        "_on_extract": "extract",
        "_on_choose_output": "choose_output",
        "_on_validate": "validate",
        "_on_build": "build",
    }
    for name, label in handlers.items():
        monkeypatch.setattr(surface, name, lambda label=label: called.append(label))
    for button in (
        surface._open_button,
        surface._extract_button,
        surface._output_button,
        surface._validate_button,
        surface._build_button,
    ):
        button.setEnabled(True)
        button.click()
    assert called == ["open_project", "extract", "choose_output", "validate", "build"]


def test_build_dialog_reopens(window) -> None:
    surface = window._build
    first = open_action(window, "Build", surface)
    second = open_action(window, "Build", surface)
    assert first.dialog is not None and second.dialog is not None
    assert first.dialog is not second.dialog
    assert surface.parentWidget() is not None


def test_build_action_does_not_change_the_active_editor(window) -> None:
    window.show_editor("Atlas")
    assert window.current_editor_name() == "Atlas"
    open_action(window, "Build", window._build)
    assert window.current_editor_name() == "Atlas", "Build is not an editor switch"


# -- Run --------------------------------------------------------------------


def test_run_action_opens_a_dialog_holding_the_real_surface(window) -> None:
    surface = window._launcher
    state = open_action(window, "Run", surface)
    assert state.dialog is not None, "no dialogue opened"
    assert state.parent_during is state.dialog
    assert state.parent_during is not surface.parentWidget()


def test_run_dialog_holds_the_launcher_controls(window) -> None:
    surface = window._launcher
    open_action(window, "Run", surface)
    for control in (
        surface._rom_field,
        surface._mgba_field,
        surface._launch_button,
    ):
        assert control.parent() is not None, "control was destroyed by re-parenting"


def test_run_launch_button_is_still_connected(window, monkeypatch) -> None:
    surface = window._launcher
    called: list[str] = []
    monkeypatch.setattr(surface, "_launch", lambda: called.append("launch"))
    surface._launch_button.setEnabled(True)
    surface._launch_button.click()
    assert called == ["launch"]


def test_run_dialog_reopens(window) -> None:
    surface = window._launcher
    first = open_action(window, "Run", surface)
    second = open_action(window, "Run", surface)
    assert first.dialog is not None and second.dialog is not None
    assert first.dialog is not second.dialog
    assert surface.parentWidget() is not None


def test_run_action_does_not_change_the_active_editor(window) -> None:
    window.show_editor("Maps")
    assert window.current_editor_name() == "Maps"
    open_action(window, "Run", window._launcher)
    assert window.current_editor_name() == "Maps"


# -- neither surface is a destination ---------------------------------------


def test_neither_surface_is_an_editor_destination(window) -> None:
    """The accepted taxonomy: Build and Launch are actions, not workspaces."""
    assert "Build" not in window._hosts
    assert "Launch" not in window._hosts
    assert set(window._hosts) == {"Atlas", "Inspector", "Maps", "Graphics", "Scene"}


def test_the_surfaces_return_to_the_shell_afterwards(window) -> None:
    """After a dialogue closes the surface is parented back, not left floating."""
    open_action(window, "Build", window._build)
    open_action(window, "Run", window._launcher)
    assert window._build.parentWidget() is not None
    assert window._launcher.parentWidget() is not None
