"""The text editor shell: export, its refusal, its digest and its summary."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication  # noqa: E402

from tools.buufury_text import (  # noqa: E402, F401
    renamedialog,
    settings,
    shell as shell_module,
    theme,
)
from tools.buufury_text.session import LINES  # noqa: E402
from tools.webfoot import textedit  # noqa: E402
from tests.unit.text_tool_shell_support import (  # noqa: E402, F401
    _Dialogs,
    _Files,
    accent_share,
    fixture_handle_pool,
    qapp,
    shrink,
    window,
    working,
)


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


def test_a_closed_window_does_not_leave_its_export_summary_shown(
    window, tmp_path, monkeypatch
) -> None:
    """The summary is application-modal, so it may not outlive the window that showed it.

    Measured: this module left three shown summaries on the QApplication, every one of them
    application-modal, and the enemy randomizer's Enter binding - a window shortcut on its
    own window - then never fired when both modules ran in one process. The hand-back
    belongs to the window, because the window is what showed it, and the offer that follows
    a summary answers itself: a window that is closing asks nothing.
    """
    dialogs = _Dialogs()
    monkeypatch.setattr(shell_module, "QMessageBox", dialogs)
    shrink(window)
    assert window.export_to(tmp_path / "edited.gba") is not None
    summary = window.last_export
    assert summary is not None and summary.isVisible()

    window.close()

    assert not summary.isVisible()
    assert QApplication.activeModalWidget() is None
    assert dialogs.questions == []


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
