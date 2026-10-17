"""The text editor shell: the one edit path, undo redo and refusal."""

from __future__ import annotations

from PySide6.QtCore import QMimeData

from tools.buufury_text import chips, shell as shell_module  # noqa: F401
from tools.buufury_text import session as text_session
from tools.webfoot import textedit
from tests.unit.text_tool_shell_support import (  # noqa: F401
    fixture_handle_pool,
    prose_row,
    qapp,
    select_first,
    shrink,
    two_line_window,
    window,
    working,
)


def test_one_edit_is_one_undo_step_and_undo_empties_the_edit_list(window) -> None:
    key = select_first(window)
    target = window.session.line(key).target or key
    loaded = window.session.pending_text(target)
    grown = window.session.line(key).text + "!"
    window.apply_edit(key, grown)
    assert window.stack.count() == 1
    # The RECORD carries the edit. A row shows the export's own text for its own span, and
    # in this fixture the first row ends where the inner record begins, so the added
    # character is in the row after it rather than in this one.
    assert grown in window.session.pending_text(target)
    assert window.windowTitle().startswith("* ")
    window.stack.undo()
    assert window.session.edited_keys() == ()
    assert window.session.pending_text(target).rstrip() == loaded.rstrip()
    assert window.windowTitle().startswith("* ") is False
    window.stack.redo()
    assert grown in window.session.pending_text(target)
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

    hits = window.session.rename_hits("Inner")
    assert hits, "the fixture's two occurrences reach the dialog"
    window.rename_action.trigger()

    assert len(opened) == 1, "the Edit menu's own item opens the rename dialog"
    dialog = opened[0]
    assert dialog.session is window.session
    assert (dialog.old_edit.text(), dialog.new_edit.text()) == ("Inner", "Lazuli")
    assert not hasattr(shell_module, "QInputDialog"), "both names come from the dialog"
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
