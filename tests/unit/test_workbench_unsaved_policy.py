"""CQA-27: ONE unsaved-edit policy for the destructive transitions.

Before this ticket the guard counted one surface: `MapsEditor.unsaved_edit_count`
returned only `MapBrowserTab`'s total, so staged Warp transitions were dropped by a
close or an image change with no prompt at all while the title said the session was
clean. A project switch was not guarded at all, which is worse in a different way:
staged layout work names records in the OUTGOING project, and carrying it across
would commit one project's work into another.

The policy under test is the session's, not a widget's: `Session` sums every
registered editor's staged count, and `MainWindow._project_change` is the one gate
a project-setting action passes through.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtGui import QCloseEvent  # noqa: E402
from PySide6.QtWidgets import QMessageBox  # noqa: E402

from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.project import write_project  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.editors import MapsEditor  # noqa: E402

from tests.unit.test_workbench_warp_transitions import (  # noqa: E402
    image_bytes,
    profile_for,  # noqa: F401  (kept beside its sibling helpers)
    project_meta,
    session_for,
)


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def image() -> bytes:
    return image_bytes()


@pytest.fixture
def project(tmp_path, image):
    write_project(tmp_path, project_meta(image), enemies=[], characters=[])
    return tmp_path


@pytest.fixture
def catalog():
    return RomProfileCatalog.load(os.path.join("config", "roms.yaml"))


@pytest.fixture
def session(qapp, tmp_path, image, project):
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(image)
    value = session_for(image, project, selected_map="map:0000")
    value.rom_path = rom
    return value


def _stage_one_warp(warps) -> None:
    """Stage one connection edit through the real Warps surface."""
    warps.select_source_map(0)
    assert warps.stage_destination(3)
    assert warps.unsaved_edit_count() == 1


def _window(session, catalog) -> MainWindow:
    window = MainWindow(session, catalog)
    _stage_one_warp(window._maps.warps)
    return window


def _answer(monkeypatch, button):
    """Answer every prompt with `button`, recording that it was asked."""
    asked = []
    monkeypatch.setattr(
        QMessageBox,
        "question",
        staticmethod(lambda *a, **k: (asked.append(a), button)[1]),
    )
    return asked


# --- the count has one authority --------------------------------------------


def test_the_unsaved_total_covers_every_layout_surface(session):
    """A staged Warp transition is unsaved work, and the session says so."""
    editor = MapsEditor(session)
    _stage_one_warp(editor.warps)

    assert editor.unsaved_edit_count() == 1, "the Maps total must include Warps"
    assert session.unsaved_edit_count() == 1, "one session authority answers"


def test_a_clean_session_reports_no_unsaved_work(session):
    editor = MapsEditor(session)

    assert editor.unsaved_edit_count() == 0
    assert session.unsaved_edit_count() == 0


# --- closing the application -------------------------------------------------


def test_closing_asks_when_only_staged_warp_work_is_unwritten(session, catalog, monkeypatch):
    window = _window(session, catalog)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)

    event = QCloseEvent()
    window.closeEvent(event)

    assert asked, "closing must ask when staged Warp work is unwritten"
    assert not event.isAccepted(), "Cancel must really cancel the close"
    assert window._maps.warps.unsaved_edit_count() == 1, "and must keep the work"


def test_closing_proceeds_when_nothing_is_unwritten(session, catalog, monkeypatch):
    window = MainWindow(session, catalog)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)

    event = QCloseEvent()
    window.closeEvent(event)

    assert asked == [], "a clean session must not be asked anything"
    assert event.isAccepted()


# --- switching project -------------------------------------------------------


def test_switching_project_asks_and_cancel_keeps_the_project_and_the_work(
    session, catalog, tmp_path, image, monkeypatch
):
    window = _window(session, catalog)
    other = tmp_path / "other"
    other.mkdir()
    write_project(other, project_meta(image), enemies=[], characters=[])
    original = session.project_dir
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)

    window._project_change(
        "Opening another project", lambda: session.set_project(other)
    )

    assert asked, "switching project must ask before it discards staged work"
    assert session.project_dir == original, "Cancel must keep the open project"
    assert window._maps.unsaved_edit_count() == 1, "and must keep the staged work"


def test_switching_project_discards_only_when_the_user_confirms(
    session, catalog, tmp_path, image, monkeypatch
):
    """Staged work names records in the OUTGOING project; it must not travel."""
    window = _window(session, catalog)
    other = tmp_path / "other"
    other.mkdir()
    write_project(other, project_meta(image), enemies=[], characters=[])
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Discard)

    window._project_change(
        "Opening another project", lambda: session.set_project(other)
    )

    assert asked
    assert session.project_dir == other, "Discard must still switch the project"
    assert window._maps.unsaved_edit_count() == 0, "and take the staged work with it"
    assert session.unsaved_edit_count() == 0


def test_a_cancelled_project_dialog_discards_nothing(session, catalog, monkeypatch):
    """Cancel inside the directory dialog is not a discard."""
    window = _window(session, catalog)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Discard)

    # The dialog runs and returns without changing the project, which is what the
    # user gets when they cancel out of the directory picker.
    window._project_change("Opening another project", lambda: None)

    assert asked
    assert window._maps.unsaved_edit_count() == 1, "nothing was discarded with it"


# --- a staged palette colour is unsaved work too (N-04) ----------------------


def _stage_one_palette_colour(window) -> None:
    """Stage one colour through the tab's own refresh, as a pick does."""
    window._graphics._palette_pending[7] = (10, 20, 30)
    window._graphics._refresh_pending_ui()


def test_a_pending_palette_colour_is_unsaved_work(session, catalog):
    window = MainWindow(session, catalog)
    _stage_one_palette_colour(window)

    assert session.unsaved_edit_count() == 1, "the session's one authority counts it"
    assert "1 unsaved" in window.windowTitle(), "and the title says so"


def test_a_clean_graphics_session_still_reports_clean(session, catalog):
    window = MainWindow(session, catalog)
    window._graphics._refresh_pending_ui()

    assert session.unsaved_edit_count() == 0
    assert "unsaved" not in window.windowTitle()


def test_closing_asks_when_only_a_palette_colour_is_unwritten(session, catalog, monkeypatch):
    window = MainWindow(session, catalog)
    _stage_one_palette_colour(window)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)

    event = QCloseEvent()
    window.closeEvent(event)

    assert asked, "closing must ask when a staged colour is unwritten"
    assert not event.isAccepted()
    assert window._graphics._palette_pending == {7: (10, 20, 30)}


def test_switching_project_asks_when_only_a_palette_colour_is_staged(
    session, catalog, tmp_path, image, monkeypatch
):
    window = MainWindow(session, catalog)
    _stage_one_palette_colour(window)
    other = tmp_path / "other"
    other.mkdir()
    write_project(other, project_meta(image), enemies=[], characters=[])
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)

    window._project_change(
        "Opening another project", lambda: session.set_project(other)
    )

    assert asked, "a staged palette colour must reach the one guard"
    assert session.project_dir != other
    assert session.unsaved_edit_count() == 1, "Cancel keeps the staged colour"


def test_a_confirmed_switch_clears_the_palette_and_the_count(
    session, catalog, tmp_path, image, monkeypatch
):
    from tools.webfoot.workbench import build_panel as bp

    window = MainWindow(session, catalog)
    _stage_one_palette_colour(window)
    other = tmp_path / "other"
    other.mkdir()
    write_project(other, project_meta(image), enemies=[], characters=[])
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Discard)
    monkeypatch.setattr(
        bp.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: str(other))
    )

    window._build.open_project_dialog()

    assert asked
    assert session.project_dir == other
    assert window._graphics._palette_pending == {}
    assert session.unsaved_edit_count() == 0


# --- every entry point passes the one gate -----------------------------------
#
# The Build panel has its own Open Project and Extract buttons beside the shell's
# File menu. They used to call the dialogs directly, so the panel could change the
# project with no prompt while the menu asked - the same defect, reachable one
# button to the left.


def test_the_build_panels_own_open_button_is_gated(session, catalog, tmp_path, monkeypatch):
    from tools.webfoot.workbench import build_panel as bp

    window = _window(session, catalog)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)
    picked = []
    monkeypatch.setattr(
        bp.QFileDialog,
        "getExistingDirectory",
        staticmethod(lambda *a, **k: picked.append(a) or str(tmp_path)),
    )
    original = session.project_dir

    window._build.open_project_dialog()  # exactly what the panel's button calls

    assert asked, "the panel's own entry point must pass the unsaved-work guard"
    assert picked == [], "Cancel must not even open the directory picker"
    assert session.project_dir == original
    assert window._maps.unsaved_edit_count() == 1


def test_the_build_panels_own_extract_button_is_gated(session, catalog, monkeypatch):
    from tools.webfoot.workbench import build_panel as bp

    window = _window(session, catalog)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)
    monkeypatch.setattr(
        bp.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: "")
    )

    window._build.extract_project_dialog()

    assert asked, "the panel's own Extract button must pass the same guard"
    assert window._maps.unsaved_edit_count() == 1


def test_a_file_menu_project_change_asks_exactly_once(session, catalog, tmp_path, monkeypatch):
    """One gate: the shell must not ask and then have the panel ask again."""
    from tools.webfoot.workbench import build_panel as bp

    window = _window(session, catalog)
    asked = _answer(monkeypatch, QMessageBox.StandardButton.Cancel)
    monkeypatch.setattr(
        bp.QFileDialog,
        "getExistingDirectory",
        staticmethod(lambda *a, **k: str(tmp_path)),
    )

    window._action_open_project.trigger()

    assert len(asked) == 1, "exactly one prompt for one project change"
    assert window._maps.unsaved_edit_count() == 1
