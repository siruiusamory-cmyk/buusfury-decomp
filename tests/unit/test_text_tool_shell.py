"""The shell: the window, the one edit path, the menus and the settings.

Everything here runs offscreen, over the synthetic image, with no ROM and no
repository file touched. The window is the only thing built; the engine is the
real one.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QMimeData  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from tests.text_fixture import SPACES, build, lowered_record_floor  # noqa: E402
from tools.buufury_text import app as app_module  # noqa: E402
from tools.buufury_text import chips, renamedialog, settings, theme  # noqa: E402
from tools.buufury_text import shell as shell_module  # noqa: E402
from tools.buufury_text import session as text_session  # noqa: E402
from tools.buufury_text.session import (  # noqa: E402
    APPEARANCE,
    BY_PLACE,
    BY_SPEAKER,
    LINES,
    RECORDS,
    STORAGE,
    UNGROUPED,
    State,
)
from tools.webfoot import textedit  # noqa: E402


#: Bound at module level on purpose, so the application cannot be collected when the
#: fixture's scope ends and leave the rest of the session building widgets under Qt with
#: no application. See the same note in `test_text_tool_editor.py`.
QAPP = QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def qapp():
    yield QAPP


class _Dialogs:
    """A stand-in for QMessageBox that records instead of blocking.

    Every case that reaches a dialog installs this, so no test can hang on a
    modal question nobody answers.
    """

    StandardButton = QMessageBox.StandardButton

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.questions: list[str] = []
        self.answers = self.StandardButton.No

    def warning(self, _parent, _title, message) -> None:
        self.warnings.append(message)

    def critical(self, _parent, _title, message) -> None:
        self.warnings.append(message)

    def question(self, _parent, _title, message, *_args):
        self.questions.append(message)
        return self.answers

    def about(self, *_args) -> None:
        return None


class _Files:
    """A stand-in for the file dialogs, so no test opens a native chooser."""

    def __init__(self, chosen: str = "") -> None:
        self.chosen = chosen
        self.asked: list[str] = []

    def getOpenFileName(self, _parent, title, *_args):
        self.asked.append(title)
        return self.chosen, ""

    getSaveFileName = getOpenFileName


def covering_image() -> bytes:
    """Two records in one container: the outer span contains the inner one."""
    payload = bytearray(SPACES)
    payload[0x20:0x20 + 22] = "Outer line ".encode("utf-16le")
    payload[0x36:0x36 + 20] = "Inner".encode("utf-16le")
    return build(payloads={1: bytes(payload)}, records=[(1, 0x20, 0x40), (1, 0x36, 20)])


@pytest.fixture()
def working(tmp_path):
    """The synthetic image on disk, with a canonical copy beside it.

    `cutters_from_pool=False` because a fixture carries no handle site inside the
    profile's event pool, so the pool-limited cutters would leave the line list
    empty and the window would be tested over nothing.
    """
    folder = tmp_path / "image"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "retail.gba").write_bytes(covering_image())
    path = folder / "working.gba"
    path.write_bytes(covering_image())
    with lowered_record_floor():
        return text_session.open_image(path, canonical=folder / "retail.gba",
                                       cutters_from_pool=False)


@pytest.fixture()
def window(qapp, working, tmp_path, monkeypatch):
    """A shown window whose settings file is a temporary one, not the user's."""
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    shell = shell_module.Shell(working, applied, theme.MODE_DARK)
    shell.show()
    shell.activateWindow()
    QApplication.processEvents()
    yield shell
    shell.close()


def select_first(window) -> str:
    """Select and show the first row, so a case never leans on a default."""
    key = window.pane.rows()[0].key
    assert window.pane.select_key(key)
    window.show_line(key)
    return key


def prose_row(window) -> str:
    """Select and show the row the rename and the shortening both act on."""
    key = next((row.key for row in window.pane.rows() if "Inner" in row.text), "")
    assert key, [row.text for row in window.pane.rows()]
    assert window.pane.select_key(key)
    window.show_line(key)
    return key


def shrink(window) -> str:
    """One in-place edit: a shorter wording, which the engine can always keep."""
    key = prose_row(window)
    loaded = window.session.line(key).text
    changed = loaded.replace("Inner", "Innr")
    assert changed != loaded
    window.apply_edit(key, changed)
    assert window.session.state(key) is not State.REFUSED
    return key


def accent_share(button, applied) -> float:
    """The share of a button's own pixels the theme's accent fills.

    A property can be set and a stylesheet can still paint over it, so this reads
    the pixels the widget actually drew rather than the property it was given.
    """
    shot = button.grab().toImage()
    accent = theme.color(applied, "accent")
    total = shot.width() * shot.height()
    filled = sum(1 for y in range(shot.height()) for x in range(shot.width())
                 if shot.pixelColor(x, y) == accent)
    return filled / total if total else 0.0


def test_the_move_notice_action_selects_the_records_that_carry_the_row(window) -> None:
    """The notice's one action has to land somewhere, and it lands in the list.

    A notice that names records and then does nothing when its button is pressed
    would be worse than no button, so this drives it through the real signal.
    """
    key = prose_row(window)
    loaded = window.session.line(key).text
    window.apply_edit(key, loaded + " and more words")
    window.show_line(key)
    assert window.session.state(key) is State.WILL_MOVE
    covered = window.session.covering(key)
    assert covered, "the fixture's inner record is carried by the outer one"
    assert window.pane.view() == LINES

    window.editor.notice.select_button.click()

    assert window.pane.view() == RECORDS, "the action shows the records it named"
    assert window.pane.selected() in covered


def test_the_notice_action_says_so_when_nothing_can_be_selected(window) -> None:
    """No covering records, no claim: the button is disabled rather than inert."""
    key = select_first(window)
    window.show_line(key)
    notice = window.editor.notice
    assert notice.select_button.isEnabled() == bool(window.session.covering(key))


# --- the window --------------------------------------------------------------


def test_the_window_opens_with_its_first_row_already_shown(window) -> None:
    """The pane selects row 0 while it is built, which is before this window can hear.

    Measured: the editor and the context pane opened empty beside a highlighted row,
    and clicking that same row did nothing, because a table does not report a
    current-row change for the row that is already current.
    """
    selected = window.pane.selected()
    assert selected, "the pane selects a first row"
    assert window._editor_key == selected
    assert window.editor.new_text() == window.session.line(selected).text
    assert window.context.retail.text() != "No line is selected."


def test_the_window_builds_and_every_pane_is_reachable(window) -> None:
    assert [name for name, _pane in window.panes()] == ["list", "editor", "context"]
    assert window.walk_panes() == ("list", "editor", "context")
    key = select_first(window)
    assert window.pane.selected() == key
    assert window.detail_label.text().startswith(key)
    assert window.image_label.text() == "working.gba"
    assert window.state_label.text().startswith("\u00b7 UNCHANGED")
    assert window.windowTitle() == "working.gba - Buu's Fury Text Editor"
    assert window.export_button.isEnabled() is False
    assert window.export_action.toolTip() == shell_module.EXPORT_EMPTY


def test_a_status_message_hands_the_row_identity_back_on_the_next_selection(window) -> None:
    """A message is transient; the row's identity, offset and span are not.

    Measured: eight `showMessage` call sites and no `clearMessage` in the package,
    so the last message, up to a whole `export_reason` sentence, took the status
    bar's left region and kept the selected row's own numbers hidden until the
    window closed.
    """
    first = select_first(window)
    assert window.detail_label.isVisible() is True

    window.prompt_export()  # nothing to export, so the reason takes the region

    assert window.statusBar().currentMessage() == shell_module.EXPORT_EMPTY
    assert window.detail_label.isVisible() is False

    second = next(row.key for row in window.pane.rows() if row.key != first)
    assert window.pane.select_key(second)

    assert window.statusBar().currentMessage() == ""
    assert window.detail_label.isVisible() is True
    assert window.detail_label.text().startswith(second)
    assert "container 0x" in window.detail_label.text()
    assert "span " in window.detail_label.text()


def test_one_edit_is_one_undo_step_and_undo_empties_the_edit_list(window) -> None:
    key = select_first(window)
    loaded = window.session.line(key).text
    grown = loaded + "!"
    window.apply_edit(key, grown)
    assert window.stack.count() == 1
    assert window.session.pending_text(key) == grown
    assert window.windowTitle().startswith("* ")
    window.stack.undo()
    assert window.session.edited_keys() == ()
    assert window.session.pending_text(key) == loaded
    assert window.windowTitle().startswith("* ") is False
    window.stack.redo()
    assert window.session.pending_text(key) == grown
    assert window.stack.count() == 1


def test_a_two_record_rename_batch_is_one_undo_step(window) -> None:
    hits = window.session.rename_hits("Inner")
    assert [hit.decision for hit in hits] == [textedit.RENAME, textedit.RENAME]
    chosen = tuple((hit.key, frozenset({hit.at})) for hit in hits)
    assert window.apply_rename("Inner", "Lazuli", chosen) == 2
    assert window.stack.undoText() == "rename 2 record(s)"
    assert all("Lazuli" in window.session.pending_text(hit.key) for hit in hits)
    window.stack.undo()
    assert window.session.edited_keys() == ()
    assert all("Inner" in window.session.line(hit.key).text for hit in hits)
    assert window.stack.undoText() == ""
    assert window.stack.redoText() == "rename 2 record(s)"
    window.stack.redo()
    assert all("Lazuli" in window.session.pending_text(hit.key) for hit in hits)


def test_the_edit_menu_opens_the_rename_dialog_and_the_batch_is_one_undo_step(
        window, monkeypatch) -> None:
    """The per-occurrence flow is reachable, and it is one action.

    An audit measured `prompt_rename` with no caller in the package or the tests,
    and the dialog itself instantiated only by tests, so the default control, the
    per-hit answers and the Apply count were all unreachable. The two names are
    collected by the dialog that already asks for them.
    """
    opened: list = []
    original = shell_module.renamedialog.RenameDialog

    class Recording(original):
        def exec(self) -> int:
            opened.append(self)
            self.old_edit.setText("Inner")
            self.new_edit.setText("Lazuli")
            return self.DialogCode.Accepted

    monkeypatch.setattr(shell_module.renamedialog, "RenameDialog", Recording)
    assert window.rename_action.isEnabled() is True

    window.rename_action.trigger()

    assert len(opened) == 1, "the Edit menu's own item opens the rename dialog"
    dialog = opened[0]
    assert dialog.session is window.session
    assert (dialog.old_edit.text(), dialog.new_edit.text()) == ("Inner", "Lazuli")
    assert not hasattr(shell_module, "QInputDialog"), "both names come from the dialog"
    hits = window.session.rename_hits("Inner")
    assert hits, "the fixture's two occurrences reach the dialog"
    assert window.stack.undoText() == f"rename {len(hits)} record(s)"
    assert all("Lazuli" in window.session.pending_text(hit.key) for hit in hits)
    window.stack.undo()
    assert window.session.edited_keys() == ()
    assert all("Inner" in window.session.line(hit.key).text for hit in hits)


def test_clear_this_edit_is_one_undo_step(window) -> None:
    key = shrink(window)
    target = window.session.line(key).target or key
    assert window.session.edited_keys() == (target,)
    window.clear_edit()
    assert window.session.edited_keys() == ()
    window.stack.undo()
    assert window.session.edited_keys() == (target,)


def test_clear_all_edits_is_one_undo_step(window) -> None:
    hits = window.session.rename_hits("Inner")
    chosen = tuple((hit.key, frozenset({hit.at})) for hit in hits)
    assert window.apply_rename("Inner", "Lazuli", chosen) == 2
    window.clear_all_edits()
    assert window.session.edited_keys() == ()
    window.stack.undo()
    assert sorted(window.session.edited_keys()) == sorted(hit.key for hit in hits)


# --- export ------------------------------------------------------------------


def test_the_export_refusal_surfaces_the_engine_message(window, monkeypatch) -> None:
    dialogs = _Dialogs()
    monkeypatch.setattr(shell_module, "QMessageBox", dialogs)
    shrink(window)
    source = Path(window.session.model.path)
    before = source.read_bytes()
    with pytest.raises(textedit.TextEditError) as caught:
        window.session.export(source)
    assert str(caught.value).startswith("REFUSED:")
    assert window.export_to(source) is None
    assert dialogs.warnings == [str(caught.value)]
    assert window.statusBar().currentMessage() == str(caught.value)
    assert source.read_bytes() == before
    assert sorted(item.name for item in source.parent.iterdir()) == \
        ["retail.gba", "working.gba"]


def test_an_export_clears_the_unsaved_marker_and_reports_its_digest(window, tmp_path,
                                                                   monkeypatch) -> None:
    dialogs = _Dialogs()
    monkeypatch.setattr(shell_module, "QMessageBox", dialogs)
    shrink(window)
    assert window.windowTitle().startswith("* ")
    out = tmp_path / "out" / "edited.gba"
    out.parent.mkdir()
    report = window.export_to(out)
    assert report is not None
    assert out.is_file()
    assert window.stack.isClean()
    assert window.windowTitle().startswith("* ") is False
    assert str(report["output_sha256"])[:12] in window.export_label.text()
    assert dialogs.warnings == []


def test_a_primary_button_paints_the_accent_fill(window, tmp_path, monkeypatch) -> None:
    """Each primary action is the accent-filled control, measured on the paint.

    An audit measured the Export button's palette write retargeted by the widget's
    own stylesheet: all 2,128 interior pixels were the raised surface with no accent
    anywhere in the region, `setAutoFillBackground` read False at runtime, and
    nothing in the package ever set the role that the theme's own rule fills.
    """
    dialogs = _Dialogs()
    monkeypatch.setattr(shell_module, "QMessageBox", dialogs)
    shrink(window)
    applied = window.theme

    assert window.export_button.isEnabled() is True
    assert accent_share(window.export_button, applied) > 0.5

    out = tmp_path / "edited.gba"
    assert window.export_to(out) is not None
    summary = window.last_export
    assert accent_share(summary.close_button, applied) > 0.5

    rename = renamedialog.RenameDialog(window.session, parent=window)
    rename.old_edit.setText("Inner")
    rename.new_edit.setText("Lazuli")
    rename.show()
    try:
        assert rename.apply_button.isEnabled() is True
        assert accent_share(rename.apply_button, applied) > 0.5
        # The measurement separates a filled control from a plain one.
        assert accent_share(rename.cancel_button, applied) < 0.5
    finally:
        rename.close()


def test_open_exported_says_when_no_handler_is_registered(window, tmp_path,
                                                          monkeypatch) -> None:
    dialogs = _Dialogs()
    monkeypatch.setattr(shell_module, "QMessageBox", dialogs)
    shrink(window)
    out = tmp_path / "edited.gba"
    assert window.export_to(out) is not None

    class NoHandler:
        @staticmethod
        def openUrl(_url) -> bool:
            return False

    monkeypatch.setattr(shell_module, "QDesktopServices", NoHandler)
    assert window.open_exported() is False
    assert "No application is registered" in window.statusBar().currentMessage()


def test_an_open_that_would_drop_edits_asks_first(window, monkeypatch) -> None:
    dialogs = _Dialogs()
    files = _Files()
    monkeypatch.setattr(shell_module, "QMessageBox", dialogs)
    monkeypatch.setattr(shell_module, "QFileDialog", files)
    shrink(window)
    window.prompt_open()
    assert dialogs.questions and "pending edit" in dialogs.questions[0]
    assert files.asked == []
    assert window.session.edited_keys() != ()
    dialogs.answers = dialogs.StandardButton.Discard
    window.prompt_open()
    assert len(dialogs.questions) == 2
    assert files.asked == ["Open image"]


# --- the menus and the panes in step -----------------------------------------


def test_the_view_menu_and_the_pane_stay_in_step_both_ways(window) -> None:
    lines, records = window.view_actions.actions()
    assert lines.isChecked()
    records.trigger()
    assert window.pane.view() == RECORDS
    assert records.isChecked() and not lines.isChecked()
    window.pane.set_view(LINES)
    assert lines.isChecked() and not records.isChecked()

    appearance, storage = window.order_actions.actions()
    storage.trigger()
    assert window.pane.order() == STORAGE
    assert storage.isChecked()
    window.pane.set_order(APPEARANCE)
    assert appearance.isChecked() and not storage.isChecked()

    none, speaker, place = window.group_actions.actions()
    place.trigger()
    assert window.pane.group() == BY_PLACE
    assert place.isChecked()
    speaker.trigger()
    assert window.pane.group() == BY_SPEAKER
    assert speaker.isChecked() and not place.isChecked()
    window.pane.set_group(UNGROUPED)
    assert none.isChecked() and not speaker.isChecked()


def test_the_view_menu_shows_and_hides_a_pane(window) -> None:
    assert window.pane_actions["list"].isChecked() is True
    window.pane_actions["list"].trigger()
    assert window.pane_actions["list"].isChecked() is False
    assert window.pane.isVisible() is False
    window.pane_actions["list"].trigger()
    assert window.pane.isVisible() is True


def test_ctrl_f_focuses_the_search_and_a_term_reaches_the_list(window) -> None:
    rows = len(window.pane.rows())
    assert rows
    window.find_action.trigger()
    assert window.search.hasFocus()
    window.search.setText("Inner")
    assert 0 < len(window.pane.rows()) <= rows
    window.search.setText("zzzz not in this image")
    assert window.pane.rows() == ()
    window.clear_search()
    assert window.search.text() == ""
    assert len(window.pane.rows()) == rows


def test_a_refused_paste_reaches_the_status_bar(window) -> None:
    """The one refusal a reader can cause by pasting says why, in the status bar.

    `insertFromMimeData` is the method `paste()` hands the clipboard's data to.
    """
    prose_row(window)
    before = window.editor.new_text()
    source = QMimeData()
    source.setText("more\x08\x03")
    window.editor.new.editor.insertFromMimeData(source)
    assert window.editor.new_text() == before
    assert window.statusBar().currentMessage() == chips.CONTROL_CODE


def test_the_window_without_an_image_shows_what_to_do(qapp, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    empty = shell_module.Shell(None, applied, theme.MODE_DARK)
    empty.show()
    try:
        assert empty.panes() == (("empty", empty.empty),)
        assert empty.walk_panes() == ("empty",)
        assert "No image open" in empty.empty.text()
        assert empty.windowTitle() == "no image - Buu's Fury Text Editor"
        assert empty.export_action.isEnabled() is False
        assert empty.open_project_action.toolTip() == shell_module.NO_IMAGE_TIP
        assert empty.rename_action.isEnabled() is False
        assert empty.rename_action.toolTip() == shell_module.NO_IMAGE_TIP
    finally:
        empty.close()


def test_the_pure_answers_need_no_window(working) -> None:
    assert shell_module.export_reason(None) == shell_module.NO_IMAGE_TIP
    assert shell_module.export_reason(working) == shell_module.EXPORT_EMPTY
    key = working.keys(LINES)[0]
    detail = shell_module.span_detail(working, key)
    assert detail.startswith(key)
    assert "container 0x" in detail and "span " in detail and "bytes" in detail
    assert shell_module.project_text(working).startswith("\u00b7 UNCHANGED")
    assert shell_module.project_text(None) == ""


# --- the settings ------------------------------------------------------------


def test_the_settings_round_trip_the_shape_and_the_theme(qapp, working, tmp_path,
                                                         monkeypatch) -> None:
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    applied = theme.apply_theme(qapp, theme.MODE_LIGHT)
    first = shell_module.Shell(working, applied, theme.MODE_LIGHT)
    first.pane.set_view(RECORDS)
    first.pane.set_order(STORAGE)
    first.pane.set_group(BY_SPEAKER)
    first.show()
    first.splitter.setSizes([500, 400, 300])
    sizes = list(first.splitter.sizes())
    first.close()

    stored = settings.load()
    assert stored["theme"] == theme.MODE_LIGHT
    assert stored["view"] == RECORDS
    assert stored["order"] == STORAGE
    assert stored["group"] == BY_SPEAKER
    assert stored["splitter"] == sizes

    second = shell_module.Shell(working, applied, theme.MODE_LIGHT)
    second.show()
    try:
        assert second.pane.view() == RECORDS
        assert second.pane.order() == STORAGE
        assert second.pane.group() == BY_SPEAKER
        assert second.splitter.sizes() == sizes
    finally:
        second.close()


def test_a_corrupt_settings_file_answers_the_defaults(qapp, working, tmp_path,
                                                      monkeypatch) -> None:
    folder = tmp_path / "user-config"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "settings.json").write_text("{ this is not json at all", encoding="utf-8")
    monkeypatch.setattr(settings, "directory", lambda: folder)
    assert settings.load() == settings.DEFAULTS
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    shell = shell_module.Shell(working, applied, theme.MODE_DARK)
    shell.show()
    try:
        assert shell.pane.view() == LINES
        assert shell.pane.order() == APPEARANCE
        assert shell.pane.group() == UNGROUPED
    finally:
        shell.close()


# --- start-up ----------------------------------------------------------------


#: A whole session in a child process, because the defect appears when the window
#: outlives the event loop: teardown deletes the QActions and the stack still
#: emits. In-process the shell is collected before shutdown, which hides it.
_EXIT_PROBE = '''
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, sys.argv[1])

from PySide6.QtWidgets import QApplication

from tests.text_fixture import SPACES, build, lowered_record_floor
from tools.buufury_text import settings, theme
from tools.buufury_text import shell as shell_module
from tools.buufury_text import session as text_session

payload = bytearray(SPACES)
encoded = "Circle\\x08\\x03 here".encode("utf-16le")
payload[0x20:0x20 + len(encoded)] = encoded
image = build(payloads={1: bytes(payload)}, records=[(1, 0x20, len(encoded))])
folder = Path(tempfile.mkdtemp())
(folder / "working.gba").write_bytes(image)
app = QApplication.instance() or QApplication([])
applied = theme.apply_theme(app, theme.MODE_DARK)
settings.directory = lambda: folder / "config"
with lowered_record_floor():
    session = text_session.open_image(folder / "working.gba",
                                      canonical=folder / "working.gba",
                                      cutters_from_pool=False)
shell = shell_module.Shell(session, applied, theme.MODE_DARK)
shell.show()
key = shell.pane.rows()[0].key
shell.pane.select_key(key)
shell.show_line(key)
shell.editor.new.editor.setText("typed words")
print("typed into", key, "stack", shell.stack.count())
'''


def test_the_exit_is_clean_after_typing_into_a_row_carrying_a_control_unit(
        tmp_path) -> None:
    """The window survives into interpreter shutdown without a stray traceback.

    Measured 3 runs out of 3: stderr carried `RuntimeError: libshiboken: Internal
    C++ object (PySide6.QtGui.QAction) already deleted` from the stack's
    `cleanChanged`, connected through a context-free lambda that nothing
    disconnects when the actions die.
    """
    script = tmp_path / "exit_probe.py"
    script.write_text(_EXIT_PROBE, encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run([sys.executable, str(script), str(root)],
                            capture_output=True, text=True, cwd=root, timeout=300)
    assert result.returncode == 0, result.stderr
    assert "typed into" in result.stdout and "stack 1" in result.stdout
    assert "already deleted" not in result.stderr, result.stderr


def test_smoke_exits_zero(qapp, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    assert app_module.main(["--smoke"]) == 0


def test_smoke_exits_zero_over_the_synthetic_image(qapp, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    path = tmp_path / "image" / "fixture.gba"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(covering_image())
    with lowered_record_floor():
        assert app_module.main(["--smoke", str(path)]) == 0


def test_a_refused_image_answers_two_without_a_traceback(qapp, tmp_path, monkeypatch) -> None:
    dialogs = _Dialogs()
    monkeypatch.setattr(app_module, "QMessageBox", dialogs)
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    broken = tmp_path / "not-an-image.gba"
    broken.write_bytes(b"\x00" * 0x200)
    assert app_module.main([str(broken)]) == 2
    assert dialogs.warnings and dialogs.warnings[0].startswith("REFUSED:")


def two_line_window(qapp, tmp_path, monkeypatch):
    """A shown window over one record whose text is two spoken lines."""
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    folder = tmp_path / "two-line"
    folder.mkdir()
    payload = bytearray(SPACES)
    payload[0x20:0x20 + 8] = "One\nTwo".encode("utf-16le")
    image = build(payloads={1: bytes(payload)}, records=[(1, 0x20, 14)])
    (folder / "retail.gba").write_bytes(image)
    path = folder / "working.gba"
    path.write_bytes(image)
    with lowered_record_floor():
        session = text_session.open_image(path, canonical=folder / "retail.gba",
                                          view=text_session.LINES, cutters_from_pool=False)
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    shell = shell_module.Shell(session, applied, theme.MODE_DARK)
    shell.show()
    QApplication.processEvents()
    target = session.model.records[0].key
    rows = sorted((row for row in session.lines if row.target == target),
                  key=lambda row: row.position[1])
    assert len(rows) == 2, [row.text for row in rows]
    return shell, session, target, rows


def test_undo_of_a_rename_beside_a_line_edit_restores_and_does_not_wedge(
        qapp, tmp_path, monkeypatch) -> None:
    """The review's own repro: edit line 2, rename line 1, undo.

    Measured before: the undo wrote the pre-rename composed text back as a whole record,
    the line entry was then looked for by its old text inside it, and the write raised.
    The record was left unable to answer later questions and a second undo baked the line
    edit into it. Snapshots cannot be refused, so undo restores and every reader answers.
    """
    shell, session, target, rows = two_line_window(qapp, tmp_path, monkeypatch)
    try:
        shell.apply_edit(rows[1].key, "Tvo")
        assert shell.apply_rename("One", "Uno", ((target, frozenset({0})),)) == 1
        assert session.pending_text(target) == "Uno\nTvo"
        shell.stack.undo()
        assert session.pending_text(target) == "One\nTvo"
        assert session.pending_text(rows[1].key) == "Tvo"
        assert session.state(rows[0].key) is not None
        assert session.counts(text_session.LINES)
        assert session.matching(kind=text_session.LINES) is not None
        shell.stack.undo()
        assert session.edited_keys() == ()
        assert session.pending_text(target) == "One\nTwo"
    finally:
        shell.close()


def test_two_renames_of_one_record_both_survive_and_undo_separately(
        qapp, tmp_path, monkeypatch) -> None:
    """Measured: two rename batches on one record kept only the second.

    Both are spans of the original text now, so each lands and each undoes on its own.
    """
    shell, session, target, _rows = two_line_window(qapp, tmp_path, monkeypatch)
    try:
        assert shell.apply_rename("One", "Uno", ((target, frozenset({0})),)) == 1
        assert shell.apply_rename("Two", "Dos", ((target, frozenset({4})),)) == 1
        assert session.pending_text(target) == "Uno\nDos"
        shell.stack.undo()
        assert session.pending_text(target) == "Uno\nTwo"
        shell.stack.undo()
        assert session.edited_keys() == ()
    finally:
        shell.close()


def test_undo_returns_each_line_of_one_record_separately(qapp, tmp_path, monkeypatch) -> None:
    """Measured: an edit of a second line discarded the first, so undo restored one.

    Each row's edit is its own undo command, and the record's text is rebuilt from the
    original with every pending row applied, so undoing the two edits puts both back.
    """
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    folder = tmp_path / "two-line"
    folder.mkdir()
    payload = bytearray(SPACES)
    payload[0x20:0x20 + 8] = "One\nTwo".encode("utf-16le")
    image = build(payloads={1: bytes(payload)}, records=[(1, 0x20, 14)])
    (folder / "retail.gba").write_bytes(image)
    path = folder / "working.gba"
    path.write_bytes(image)
    with lowered_record_floor():
        session = text_session.open_image(path, canonical=folder / "retail.gba",
                                          view=text_session.LINES, cutters_from_pool=False)
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    shell = shell_module.Shell(session, applied, theme.MODE_DARK)
    shell.show()
    QApplication.processEvents()
    try:
        target = session.model.records[0].key
        rows = sorted((row for row in session.lines if row.target == target),
                      key=lambda row: row.position[1])
        assert len(rows) == 2, [row.text for row in rows]
        shell.apply_edit(rows[0].key, "Une")
        shell.apply_edit(rows[1].key, "Tvo")
        assert session.pending_text(rows[0].key) == "Une"
        assert session.pending_text(rows[1].key) == "Tvo"
        assert len(session.edits) == 1
        shell.stack.undo()
        assert session.pending_text(rows[0].key) == "Une"
        assert session.pending_text(rows[1].key) == rows[1].text
        shell.stack.undo()
        assert session.edited_keys() == ()
    finally:
        shell.close()
