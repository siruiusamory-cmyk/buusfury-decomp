"""The text editor shell: settings, start-up, smoke and interpreter exit."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication  # noqa: E402

from tests.text_fixture import SPACES, build, lowered_record_floor  # noqa: E402
from tools.buufury_text import app as app_module  # noqa: E402
from tools.buufury_text import project as project_file, settings, theme  # noqa: E402
from tools.buufury_text import shell as shell_module  # noqa: E402
from tools.buufury_text import session as text_session  # noqa: E402
from tools.buufury_text.session import (  # noqa: E402
    APPEARANCE,
    BY_SPEAKER,
    LINES,
    RECORDS,
    STORAGE,
    UNGROUPED,
)
from tests.unit.text_tool_shell_support import (  # noqa: E402, F401
    _Dialogs,
    covering_image,
    fixture_handle_pool,
    qapp,
    two_line_window,
    working,
)


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


def test_a_saved_project_edit_survives_editing_and_undoing_in_the_window(
        qapp, tmp_path, monkeypatch) -> None:
    """Reopen a saved edit through the window, edit the other row, then undo.

    Measured: an edit adopted from a project lived only in the session's edit list, so the
    next edit of that record composed from the original text and silently discarded the
    saved change, and the undo that followed erased it. The project is written to a file
    and read back here, because that is the route a reader takes.
    """
    shell, session, target, rows = two_line_window(qapp, tmp_path, monkeypatch)
    shell.close()
    session.set_edit(rows[0].key, "Une")
    path = tmp_path / f"saved{project_file.SUFFIX}"
    project_file.save(session.project(), path)

    with lowered_record_floor():
        reopened = text_session.open_image(
            tmp_path / "two-line" / "working.gba",
            canonical=tmp_path / "two-line" / "retail.gba",
            view=text_session.LINES, cutters_from_pool=False,
            project=project_file.load(path))
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    window = shell_module.Shell(reopened, applied, theme.MODE_DARK)
    window.show()
    QApplication.processEvents()
    try:
        again = sorted((row for row in reopened.lines if row.target == target),
                       key=lambda row: row.position[1])
        assert reopened.pending_text(again[0].key) == "Une"
        window.apply_edit(again[1].key, "Tvo")
        assert reopened.pending_text(again[0].key) == "Une", "the saved edit was discarded"
        assert reopened.pending_text(target) == "Une\nTvo"
        window.stack.undo()
        assert reopened.pending_text(again[1].key) == again[1].text
        assert reopened.pending_text(again[0].key) == "Une", "the undo erased the saved edit"
        assert reopened.pending_text(target) == "Une\nTwo"
    finally:
        window.close()


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
