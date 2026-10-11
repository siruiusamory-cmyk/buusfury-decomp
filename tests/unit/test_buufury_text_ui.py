"""The widget layer: the theme tokens, the chip atoms, and the dialogue preview.

Everything here runs offscreen and over plain strings, so no ROM and no window are
needed and the gate stays portable. The session fixture file is shared with the
other lane, so these cases sit in clearly named functions.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QMimeData, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QTextEdit, QWidget  # noqa: E402

from tests.text_fixture import SPACES, build, lowered_record_floor  # noqa: E402
from tools.buufury_text import chips, preview, renamedialog, settings, status, theme  # noqa: E402
from tools.buufury_text import session as app_session  # noqa: E402
from tools.buufury_text.renamedialog import DECISION_COLUMN, ROLE_CHOSEN  # noqa: E402
from tools.buufury_text.session import State  # noqa: E402
from tools.buufury_text.shell import Shell, pending_text  # noqa: E402
from tools.webfoot import textedit  # noqa: E402

#: Two prose runs around an interior 0x0A, then a 0x08 unit with an operand.
CURRENT = "AB\nCD\x08\x03EF"
ATOMS = ((2, 3), (5, 7))
HEX = re.compile(r"#[0-9A-Fa-f]{6}")


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _key(widget: QWidget, key: Qt.Key.Key) -> None:
    QTest.keyClick(widget, key)


def _caret(widget: QTextEdit, position: int) -> None:
    cursor = widget.textCursor()
    cursor.setPosition(position)
    widget.setTextCursor(cursor)


# --- protected_edit refusals -------------------------------------------------


def test_protected_edit_refuses_typing_inside_an_atom() -> None:
    for atom in ATOMS:
        for at in range(*atom):
            assert chips.protected_edit(CURRENT, at, 0, "Q") == CURRENT


def test_protected_edit_refuses_backspace_at_each_edge_of_an_atom() -> None:
    for start, stop in ATOMS:
        assert chips.protected_edit(CURRENT, start, 1, "") == CURRENT
        assert chips.protected_edit(CURRENT, stop - 1, 1, "") == CURRENT
    assert chips.protected_edit(CURRENT, 6, 1, "") == CURRENT


def test_protected_edit_refuses_a_delete_that_would_clip_an_atom() -> None:
    assert chips.protected_edit(CURRENT, 6, 1, "") == CURRENT
    # Deleting "D" at 4 removes prose only; the atom starts at 5 and survives.
    assert chips.protected_edit(CURRENT, 4, 1, "") == "AB\nC\x08\x03EF"


def test_protected_edit_refuses_a_removal_that_swallows_a_whole_atom() -> None:
    assert chips.protected_edit(CURRENT, 5, 2, "") == CURRENT
    assert chips.protected_edit(CURRENT, 4, 3, "") == CURRENT


def test_protected_edit_refuses_a_paste_that_carries_a_control_unit() -> None:
    assert chips.protected_edit(CURRENT, 8, 0, "hey\n") == CURRENT
    assert chips.protected_edit(CURRENT, 8, 0, "\x08\x01") == CURRENT


def test_protected_edit_refuses_a_drag_range_that_crosses_an_atom() -> None:
    assert chips.protected_edit(CURRENT, 3, 3, "") == CURRENT


def test_protected_edit_accepts_ordinary_typing_and_deletion() -> None:
    assert chips.protected_edit(CURRENT, 0, 0, "Z") == "ZAB\nCD\x08\x03EF"
    assert chips.protected_edit(CURRENT, 0, 1, "") == "B\nCD\x08\x03EF"


def test_protected_edit_accepts_a_paste_of_plain_prose() -> None:
    assert chips.protected_edit(CURRENT, 0, 0, "x y") == "x yAB\nCD\x08\x03EF"
    assert chips.protected_edit(CURRENT, 3, 0, "x y") == "AB\nx yCD\x08\x03EF"
    assert chips.protected_edit(CURRENT, len(CURRENT), 0, "% d\u00e9j\u00e0") == \
        CURRENT + "% d\u00e9j\u00e0"


# --- atom_ranges -------------------------------------------------------------


def test_atom_ranges_finds_an_interior_unit_and_one_with_an_operand() -> None:
    assert chips.atom_ranges(CURRENT) == ATOMS
    assert chips.atom_ranges("plain prose") == ()


def test_atom_ranges_spans_the_operand_of_a_0x0008_unit() -> None:
    units = textedit.units(CURRENT)
    control = next(unit for unit in units if isinstance(unit, textedit.Control)
                   and unit.code == 0x08)
    assert control.raw == "\x08\x03"
    assert control.operand == "\x03"
    assert control.raw == CURRENT[5:7]


# --- the chip editor ---------------------------------------------------------


def test_chip_edit_round_trips_the_serialized_text(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    assert editor.serialized() == CURRENT
    assert editor.atom_count() == len(ATOMS)


def test_chip_edit_rebuilds_its_document_from_the_string(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text("plain prose")
    editor.set_text(CURRENT)
    assert editor.serialized() == CURRENT
    assert editor.toPlainText() == "AB\ufffcCD\ufffcEF"
    assert editor.atom_count() == len(ATOMS)


def test_chip_edit_refuses_backspace_inside_an_atom(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    editor.setFocus()
    _caret(editor, 3)
    _key(editor, Qt.Key.Key_Backspace)
    assert editor.serialized() == CURRENT


def test_chip_edit_refuses_delete_at_an_atom_edge(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    editor.setFocus()
    _caret(editor, 5)
    _key(editor, Qt.Key.Key_Delete)
    assert editor.serialized() == CURRENT


def test_chip_edit_rejects_a_paste_that_carries_a_control_unit(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    payload = QMimeData()
    payload.setText("hey\n")
    assert editor.canInsertFromMimeData(payload) is False
    editor.insertFromMimeData(payload)
    assert editor.serialized() == CURRENT


def test_chip_edit_takes_an_ordinary_typed_character(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text("CD")
    editor.setFocus()
    _caret(editor, 1)
    QTest.keyClicks(editor, "x")
    assert editor.serialized() == "CxD"


def test_chip_edit_accepts_a_paste_of_plain_prose(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text("AB")
    _caret(editor, 2)
    payload = QMimeData()
    payload.setText(" %")
    assert editor.canInsertFromMimeData(payload) is True
    editor.insertFromMimeData(payload)
    assert editor.serialized() == "AB %"


def test_chip_edit_leaves_a_read_only_instance_editable_by_set_text_only(qapp) -> None:
    editor = chips.ChipTextEdit(editable=False)
    editor.set_text(CURRENT)
    assert editor.isReadOnly() is True
    assert editor.serialized() == CURRENT


def test_chip_edit_refuses_a_shifted_key_event_inside_an_atom(qapp) -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    _caret(editor, 3)
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Backspace, Qt.KeyboardModifier.NoModifier)
    editor.keyPressEvent(event)
    assert editor.serialized() == CURRENT


def test_chip_edit_is_a_text_edit_with_a_registered_object_handler(qapp) -> None:
    editor = chips.ChipTextEdit()
    assert isinstance(editor, QTextEdit)
    handler = editor.document().documentLayout().handlerForObject(chips.OBJECT_TYPE)
    assert handler is not None
    assert isinstance(handler, chips.ChipObject)


# --- the theme ---------------------------------------------------------------


def test_theme_for_returns_distinct_light_and_dark_palettes() -> None:
    light = theme.theme_for(theme.MODE_LIGHT, False)
    dark = theme.theme_for(theme.MODE_DARK, True)
    assert light.mode == "light"
    assert dark.mode == "dark"
    assert light != dark
    assert light.surface != dark.surface
    assert theme.theme_for(theme.MODE_SYSTEM, True).mode == "dark"
    assert theme.theme_for(theme.MODE_SYSTEM, False).mode == "light"


def test_state_colors_give_each_state_its_own_fill_and_ink() -> None:
    for mode in (theme.MODE_LIGHT, theme.MODE_DARK):
        resolved = theme.theme_for(mode, False)
        pairs = {state: theme.state_colors(resolved, state) for state in State}
        assert len({(fill.name(), ink.name()) for fill, ink in pairs.values()}) == len(State)
        for fill, ink in pairs.values():
            assert fill.name() != ink.name()


def test_state_marker_gives_each_state_its_own_shape() -> None:
    resolved = theme.theme_for(theme.MODE_LIGHT, False)
    shapes = set()
    for state in State:
        pen = theme.state_marker(resolved, state)
        shapes.add((pen.style().name, pen.width()))
    assert len(shapes) == len(State)
    assert theme.state_marker(resolved, State.UNCHANGED).style() == Qt.PenStyle.NoPen
    assert theme.state_marker(resolved, State.REFUSED).width() == 4


def test_the_auxiliary_marker_is_a_sixth_shape_outside_the_state_set() -> None:
    markers = {status.PRESENTATION[state].marker for state in State}
    assert markers == {"none", "solid", "dashed", "block", "double"}
    assert status.AUXILIARY.marker == "aux"


def test_app_stylesheet_uses_only_token_colours() -> None:
    for mode in (theme.MODE_LIGHT, theme.MODE_DARK):
        resolved = theme.theme_for(mode, False)
        tokens = {token.lower() for token in theme.theme_tokens(resolved).values()}
        sheet = theme.app_stylesheet(resolved)
        assert HEX.findall(sheet)
        assert {found.lower() for found in HEX.findall(sheet)} <= tokens


def test_apply_theme_installs_the_proxy_style_without_raising(qapp) -> None:
    resolved = theme.apply_theme(qapp, theme.MODE_DARK)
    assert isinstance(resolved, theme.Theme)
    assert resolved.mode == "dark"
    proxy = theme.proxy_style()
    assert proxy is not None
    assert "EditorProxyStyle" in proxy.metaObject().className()
    assert qapp.palette().color(qapp.palette().ColorRole.Window) == theme.color(
        resolved, "window")


def test_every_presentation_icon_exists_or_degrades_to_its_glyph() -> None:
    for entry in (*status.PRESENTATION.values(), status.AUXILIARY):
        icon = theme.icon(entry.icon)
        assert icon is not None
        if icon.isNull():
            assert entry.glyph
    assert theme.icon("no-such-icon").isNull()


def test_mono_font_is_smaller_than_its_base_by_delta() -> None:
    base = theme.mono_font(0).pointSize()
    assert theme.mono_font(-1).pointSize() == base - 1


# --- the dialogue preview ----------------------------------------------------


class StubGlyphs:
    """A stand-in for the RE Lab's extracted font: a 4 px cell, 2 lines a page."""

    name = "stub game font"

    def __init__(self, box_width: int = 20) -> None:
        self._box_width = box_width

    @property
    def line_height(self) -> int:
        return 4

    @property
    def lines_per_page(self) -> int:
        return 2

    @property
    def box_width(self) -> int:
        return self._box_width

    def advance(self, character: str) -> int:
        return 4

    def draw(self, painter, character: str, x: int, y: int) -> None:
        painter.drawText(x, y, character)


def test_preview_layout_wraps_a_long_line() -> None:
    pages = preview.layout("A" * 15, StubGlyphs(box_width=20))
    assert pages == (("AAAAA", "AAAAA"), ("AAAAA",))


def test_preview_layout_wraps_and_pages_a_long_line() -> None:
    stub = StubGlyphs(box_width=8)
    pages = preview.layout("Z" * 100, stub)
    assert len(pages) > 1
    assert all(all(len(line) <= 2 for line in page) for page in pages)


def test_preview_layout_breaks_pages_on_the_0x000a_unit() -> None:
    pages = preview.layout("AB\nCD\nEF", StubGlyphs())
    assert pages == (("AB", "CD"), ("EF",))


def test_preview_layout_keeps_an_empty_text_as_one_empty_page() -> None:
    assert preview.layout("", StubGlyphs()) == (("",),)


def test_preview_is_approximate_until_the_real_font_arrives(qapp) -> None:
    widget = preview.DialoguePreview()
    assert widget.is_approximate() is True
    assert preview.CAPTION in "Approximate preview"
    widget.set_glyph_source(StubGlyphs())
    assert widget.is_approximate() is False
    assert widget.glyph_source_name() == "stub game font"


def test_preview_paints_offscreen_with_each_source(qapp) -> None:
    widget = preview.DialoguePreview()
    widget.resize(240, 160)
    widget.set_text("Say hello!\nSecond page.")
    widget.grab()
    widget.set_glyph_source(StubGlyphs())
    widget.grab()
    assert widget.sizeHint().width() > 0


# --- the shell: one window over the synthetic image ---------------------------


INNER_KEY = "1:54:20"
OUTER_KEY = "1:32:64"
INNER = "Inner line"
APPENDED = "Inner line is longer now"
NO_RETAIL_NOTE = "no retail reference loaded"


def covering_image() -> bytes:
    """Two records in one container: the outer span contains the inner one."""
    payload = bytearray(SPACES)
    payload[0x20:0x20 + 22] = "Outer line ".encode("utf-16le")
    payload[0x36:0x36 + 20] = INNER.encode("utf-16le")
    return build(payloads={1: bytes(payload)}, records=[(1, 0x20, 0x40), (1, 0x36, 20)])


def write_image(path: Path, canonical: Path | None = None):
    """Open the synthetic image, offscreen, with no ROM and no repository file touched."""
    path.write_bytes(covering_image())
    with lowered_record_floor():
        return app_session.open_image(path, canonical=canonical)


@pytest.fixture()
def session(tmp_path):
    return write_image(tmp_path / "fixture.gba")


def shown_shell(session_, qapp, tmp_path, monkeypatch) -> Shell:
    """A shown window whose settings file is a temporary one, not the user's."""
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    window = Shell(session_, theme.apply_theme(qapp, theme.MODE_DARK))
    window.show()
    return window


@pytest.fixture()
def shell(qapp, session, tmp_path, monkeypatch):
    window = shown_shell(session, qapp, tmp_path, monkeypatch)
    yield window
    window.close()


def test_the_window_builds_over_a_synthetic_image_and_every_pane_is_reachable(shell) -> None:
    assert [name for name, _pane in shell.panes()] == ["list", "editor", "context"]
    assert shell.walk_panes() == ("list", "editor", "context")
    keys = [line.key for line in shell.pane.rows()]
    assert INNER_KEY in keys
    assert OUTER_KEY in keys
    key = shell.pane.selected()
    assert key in (INNER_KEY, OUTER_KEY)
    assert shell.editor.current.serialized() == shell.session.line(key).text
    assert shell.editor.retail.serialized() == NO_RETAIL_NOTE
    assert shell.offset_label.text().startswith(key)
    assert shell.editor.meter.text() == "no pending edit"


def test_one_apply_edit_is_one_undo_step_and_undo_empties_the_edit_list(shell) -> None:
    key = shell.pane.selected()
    loaded = shell.session.line(key).text
    grown = loaded + "!"
    shell.apply_edit(key, grown)
    assert shell.stack.count() == 1
    assert pending_text(shell.session, key) == grown
    assert shell.unsaved_label.isVisible()
    shell.stack.undo()
    assert shell.session.edits == {}
    assert pending_text(shell.session, key) == loaded
    shell.stack.redo()
    assert pending_text(shell.session, key) == grown


def test_a_two_record_rename_batch_is_one_undo_step(qapp, tmp_path, monkeypatch) -> None:
    retail = tmp_path / "retail.gba"
    retail.write_bytes(covering_image())
    session_ = write_image(tmp_path / "working.gba", canonical=retail)
    hits = session_.rename_hits("Inner")
    assert len(hits) == 2
    window = shown_shell(session_, qapp, tmp_path, monkeypatch)
    try:
        dialog = renamedialog.RenameDialog(session_, "Inner", "Lazuli", window.metrics,
                                           window.theme, window)
        for row in range(dialog.model.rowCount()):
            dialog.model.setData(dialog.model.index(row, DECISION_COLUMN), textedit.RENAME,
                                 ROLE_CHOSEN)
        assert dialog.apply_button.text() == "Apply 2 decisions"
        chosen = dialog.renamed()
        assert len(chosen) == 2
        window.apply_rename("Inner", "Lazuli", chosen)
        assert window.stack.count() == 1
        assert window.stack.undoText() == "rename 2 record(s)"
        assert "Lazuli" in pending_text(session_, INNER_KEY)
        assert "Lazuli" in pending_text(session_, OUTER_KEY)
        window.stack.undo()
        assert session_.edits == {}
        assert pending_text(session_, INNER_KEY) == INNER
    finally:
        window.close()


def test_export_refusal_surfaces_the_engine_message_and_writes_nothing(shell) -> None:
    key = shell.pane.selected()
    shell.apply_edit(key, shell.session.line(key).text + "!")
    source = Path(shell.session.model.path)
    before = source.read_bytes()
    with pytest.raises(textedit.TextEditError) as caught:
        shell.session.export(source)
    assert str(caught.value).startswith("REFUSED:")
    assert shell.export_to(source) is None
    assert shell.last_export is not None
    assert shell.last_export.error_text() == str(caught.value)
    assert shell.last_export.error.isVisible()
    assert source.read_bytes() == before
    assert [item.name for item in source.parent.iterdir()] == [source.name]


def test_the_move_notice_appears_for_a_grown_line_and_names_its_covering_records(shell) -> None:
    shell.show_line(INNER_KEY)
    shell.apply_edit(INNER_KEY, APPENDED)
    assert shell.session.state(INNER_KEY) is State.WILL_MOVE
    assert shell.session.covering(INNER_KEY) == (OUTER_KEY,)
    assert shell.editor.notice.isVisible()
    assert OUTER_KEY in shell.editor.notice.detail.text()
    assert shell.editor.notice.select_button.isEnabled()
    shell.editor.notice.collapse_button.setChecked(True)
    assert shell.editor.notice.detail.isVisible() is False
    assert shell.editor.notice.headline.text() == "This edit will move to appended space"
    assert shell.editor.notice.isVisible()


def test_the_meter_reports_both_units_and_marks_an_unstated_limit(shell) -> None:
    shell.show_line(INNER_KEY)
    shell.apply_edit(INNER_KEY, "Inner")
    assert shell.session.state(INNER_KEY) is State.EDITED
    meter = shell.session.meter(INNER_KEY)
    assert (meter.chars, meter.chars_limit, meter.bytes, meter.bytes_limit) == (5, 10, 10, 20)
    assert shell.editor.meter.text() == "5 / 10 chars     10 / 20 bytes"
    assert shell.editor.meter.stated() is True
    assert shell.editor.meter.chars_bar.tick_at(100) is not None
    assert shell.editor.meter.badge.isVisible()

    shell.apply_edit(INNER_KEY, "x" * 2100)
    assert shell.session.state(INNER_KEY) is State.REFUSED
    assert shell.session.meter(INNER_KEY).bytes_limit is None
    assert "2100 chars" in shell.editor.meter.text()
    assert "4200 bytes" in shell.editor.meter.text()
    assert "unstated" in shell.editor.meter.text()
    assert shell.editor.meter.stated() is False
    assert shell.editor.meter.bytes_bar.tick_at(100) is None
    assert "above the 4094-byte length field" in shell.editor.meter.reason.text()
