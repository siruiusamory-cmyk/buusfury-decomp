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
from PySide6.QtWidgets import QApplication, QHeaderView, QTextEdit, QWidget  # noqa: E402

from tests.text_fixture import SPACES, build, line_payload, lowered_record_floor  # noqa: E402
from tools.buufury_text import (  # noqa: E402
    chipedit,
    chips,
    contextpane,
    lineview,
    preview,
    renamedialog,
    settings,
    status,
    theme,
)
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(covering_image())
    with lowered_record_floor():
        return app_session.open_image(path, canonical=canonical)


@pytest.fixture()
def session(tmp_path):
    # The image lives in its own directory, so the settings the window writes during a
    # test never land beside it.
    return write_image(tmp_path / "image" / "fixture.gba")


def shown_shell(session_, qapp, tmp_path, monkeypatch, shape=None) -> Shell:
    """A shown window whose settings file is a temporary one, not the user's.

    ``shape`` forces the dialogue list back to RECORDS for the record-level cases the
    earlier lane wrote; the window restores its own stored shape at start-up.
    """
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    window = Shell(session_, theme.apply_theme(qapp, theme.MODE_DARK))
    if shape is not None:
        window.pane.set_view(shape)
    window.show()
    return window


@pytest.fixture()
def shell(qapp, session, tmp_path, monkeypatch):
    window = shown_shell(session, qapp, tmp_path, monkeypatch, shape=app_session.RECORDS)
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
    window = shown_shell(session_, qapp, tmp_path, monkeypatch, shape=app_session.RECORDS)
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


# --- the dialogue list: shape, speaker, grouping and order --------------------

ALPHA = "Alpha line"
BETA = "Beta line"
GAMMA = "Gamma line"
TWO_LINES = "One\nTwo"
#: The synthetic image carries no appearance table, so the portrait join is stood in
#: for. The column only has to render whatever the session answered.
PORTRAITS = {1: textedit.Portrait(8, textedit.NAMED_PORTRAIT, "Bulma"),
             2: textedit.Portrait(0, textedit.NO_PORTRAIT)}
SHAPE_KEYS = {"gamma": "3:32:20", "alpha": "1:32:20", "beta": "2:32:18"}


def shape_image() -> bytes:
    """Three records in three containers, in the reverse of their handle order."""
    return build(
        payloads={1: line_payload(ALPHA), 2: line_payload(BETA), 3: line_payload(GAMMA)},
        records=[(3, 0x20, len(GAMMA) * 2), (1, 0x20, len(ALPHA) * 2),
                 (2, 0x20, len(BETA) * 2)])


def split_image() -> bytes:
    """One record holding two spoken lines, so the two views differ in row count."""
    return build(payloads={1: line_payload(TWO_LINES)},
                 records=[(1, 0x20, len(TWO_LINES) * 2)])


def named_portraits(model):
    """A stand-in join, because a synthetic image carries no appearance table."""
    return {record.key: PORTRAITS[record.selector] for record in model.records
            if record.selector in PORTRAITS}


def opened(tmp_path: Path, name: str, image: bytes):
    """A session over a synthetic image; no event pool exists, so every record cuts."""
    path = tmp_path / name
    path.write_bytes(image)
    with lowered_record_floor():
        return app_session.open_image(path, cutters_from_pool=False)


@pytest.fixture()
def shape_session(tmp_path):
    return opened(tmp_path, "shape.gba", shape_image())


@pytest.fixture()
def shape_window(qapp, shape_session, tmp_path, monkeypatch):
    window = shown_shell(shape_session, qapp, tmp_path, monkeypatch)
    yield window
    window.close()


@pytest.fixture()
def named_window(qapp, tmp_path, monkeypatch):
    monkeypatch.setattr(textedit, "portraits", named_portraits)
    window = shown_shell(opened(tmp_path, "named.gba", shape_image()), qapp, tmp_path,
                         monkeypatch)
    yield window
    window.close()


@pytest.fixture()
def split_window(qapp, tmp_path, monkeypatch):
    window = shown_shell(opened(tmp_path, "split.gba", split_image()), qapp, tmp_path,
                         monkeypatch)
    yield window
    window.close()


@pytest.fixture()
def shared_key_window(qapp, tmp_path, monkeypatch):
    """The one image whose line key and record key are the same string."""
    path = tmp_path / "shared.gba"
    path.write_bytes(covering_image())
    with lowered_record_floor():
        session_ = app_session.open_image(path, cutters_from_pool=False)
    window = shown_shell(session_, qapp, tmp_path, monkeypatch)
    yield window
    window.close()


def test_switching_shape_keeps_a_row_the_other_view_also_holds(shared_key_window) -> None:
    pane = shared_key_window.pane
    assert shared_key_window.session.view == app_session.LINES
    pane.set_view(app_session.RECORDS)
    assert pane.select_key(INNER_KEY)
    pane.set_view(app_session.LINES)
    assert pane.selected() == INNER_KEY
    assert [line.key for line in pane.rows()] == ["1:32:22", "1:54:20"]
    # A row the other view does not hold cannot stay selected.
    pane.set_view(app_session.RECORDS)
    assert pane.select_key(OUTER_KEY)
    pane.set_view(app_session.LINES)
    assert pane.selected() != OUTER_KEY


def test_the_dialogue_list_defaults_to_lines_and_records_switches_the_shape(split_window) -> None:
    pane = split_window.pane
    assert pane.view() == app_session.LINES
    assert split_window.session.view == app_session.LINES
    assert [line.key for line in pane.rows()] == ["1:32:6", "1:40:6"]
    assert split_window.session.view_size(app_session.RECORDS) == 1
    pane.set_view(app_session.RECORDS)
    assert split_window.session.view == app_session.RECORDS
    assert pane.view_box.currentData() == app_session.RECORDS
    assert split_window.shape_actions.checkedAction().data() == app_session.RECORDS
    assert [line.key for line in pane.rows()] == ["1:32:14"]
    # The View menu reaches the same control, which is why it carries the actions.
    split_window.shape_actions.actions()[0].trigger()
    assert pane.view() == app_session.LINES
    assert split_window.session.view == app_session.LINES


def test_the_speaker_column_shows_the_name_the_gap_word_and_the_unknown_word(named_window) -> None:
    pane = named_window.pane
    model = pane.table.model()
    rows = {entry.key: row for row, entry in enumerate(model.entries())}
    assert model.headerData(lineview.COLUMN_SPEAKER, Qt.Orientation.Horizontal,
                            Qt.ItemDataRole.DisplayRole) == "Speaker (by portrait)"

    def cell(key: str, role: int) -> object:
        return model.data(model.index(rows[key], lineview.COLUMN_SPEAKER), role)

    assert cell(SHAPE_KEYS["alpha"], Qt.ItemDataRole.DisplayRole) == "Bulma"
    assert cell(SHAPE_KEYS["beta"], Qt.ItemDataRole.DisplayRole) == "No portrait"
    assert cell(SHAPE_KEYS["gamma"], Qt.ItemDataRole.DisplayRole) == \
        app_session.UNKNOWN_SPEAKER
    assert cell(SHAPE_KEYS["alpha"], Qt.ItemDataRole.ForegroundRole) is None
    for key in (SHAPE_KEYS["beta"], SHAPE_KEYS["gamma"]):
        muted = cell(key, Qt.ItemDataRole.ForegroundRole)
        assert muted is not None
        assert muted.name() == theme.color(theme.active_theme(), "text_secondary").name()
    assert pane.speaker_caption.text() == "Speaker (by portrait)"
    pane.set_kind(app_session.SLOT)
    assert pane.table.isColumnHidden(lineview.COLUMN_SPEAKER)
    assert pane.rows()
    pane.set_kind(app_session.RECORD)
    assert not pane.table.isColumnHidden(lineview.COLUMN_SPEAKER)


def test_the_speaker_filter_leaves_only_that_speaker_or_that_gap(named_window) -> None:
    pane = named_window.pane
    pane.speaker_box.setCurrentIndex(pane.speaker_box.findData("Bulma"))
    assert [line.speaker_label for line in pane.rows()] == ["Bulma"]
    assert [line.text for line in pane.rows()] == [ALPHA]
    pane.speaker_box.setCurrentIndex(pane.speaker_box.findData("No portrait"))
    assert [line.text for line in pane.rows()] == [BETA]


def test_speaker_grouping_heads_each_name_and_puts_the_unknown_last(named_window) -> None:
    pane = named_window.pane
    pane.set_group(app_session.BY_SPEAKER)
    model = pane.table.model()
    headings = [entry for entry in model.entries() if isinstance(entry, lineview.Group)]
    assert [group.label for group in headings] == ["Bulma", "No portrait",
                                                   app_session.UNKNOWN_SPEAKER]
    assert [len(group.rows) for group in headings] == [1, 1, 1]
    assert model.data(model.index(0, 0), lineview.ROLE_HEADING) == ("Bulma (1)", "")
    assert model.flags(model.index(0, 0)) == Qt.ItemFlag.NoItemFlags
    assert pane.table.columnSpan(0, 0) == model.columnCount()


def test_place_grouping_is_one_heading_that_names_the_gap(shape_window) -> None:
    pane = shape_window.pane
    pane.set_group(app_session.BY_PLACE)
    model = pane.table.model()
    headings = [entry for entry in model.entries() if isinstance(entry, lineview.Group)]
    assert len(headings) == 1
    assert headings[0].label == app_session.UNPLACED
    assert len(headings[0].rows) == 3
    assert model.data(model.index(0, 0), lineview.ROLE_HEADING) == \
        ("Unplaced (3)", lineview.NO_PLACE_LINK)


def test_a_group_heading_is_painted_as_a_raised_heading_row(shape_window) -> None:
    pane = shape_window.pane
    pane.set_group(app_session.BY_PLACE)
    table = pane.table
    image = table.grab().toImage()
    assert table.viewport().width() > 200

    def band(entry_row: int) -> str:
        y = table.rowViewportPosition(entry_row) + table.rowHeight(entry_row) // 2
        return image.pixelColor(200, y).name()

    assert band(0) == theme.color(theme.active_theme(), "surface_raised").name()
    assert band(3) == theme.color(theme.active_theme(), "surface").name()


def test_appearance_and_storage_order_differ_in_the_first_row_only(shape_window) -> None:
    pane = shape_window.pane
    appearance = [line.key for line in pane.rows()]
    pane.set_order(app_session.STORAGE)
    storage = [line.key for line in pane.rows()]
    assert appearance[0] == SHAPE_KEYS["gamma"]
    assert storage[0] == SHAPE_KEYS["alpha"]
    assert set(appearance) == set(storage)


def test_editing_one_line_of_a_record_leaves_its_sibling_row_unchanged(split_window) -> None:
    pane = split_window.pane
    first, sibling = pane.rows()
    assert first.target == sibling.target == "1:32:14"
    # A same-length edit stays inside the record's own span.
    split_window.apply_edit(first.key, "Uno")
    assert split_window.session.state(first.key) is State.EDITED
    assert split_window.session.state(sibling.key) is State.UNCHANGED
    assert split_window.session.pending_text(first.key) == "Uno"
    assert split_window.session.pending_text(sibling.key) == "Two"
    # Growing the record past its own span moves it, and still leaves the sibling alone.
    split_window.apply_edit(first.key, "Uno!")
    assert split_window.session.state(first.key) is State.WILL_MOVE
    assert split_window.session.state(sibling.key) is State.UNCHANGED
    assert split_window.session.pending_text(sibling.key) == "Two"


def test_switching_shape_keeps_the_search_term_and_the_filter_chips(shape_window) -> None:
    pane = shape_window.pane
    shape_window.search.setText(BETA)
    assert [line.text for line in pane.rows()] == [BETA]
    pane.chips[0].setChecked(True)
    assert pane.rows() == ()
    pane.set_view(app_session.RECORDS)
    assert shape_window.session.view == app_session.RECORDS
    assert shape_window.search.text() == BETA
    assert pane.chips[0].isChecked() is True
    assert pane.rows() == ()
    pane.set_view(app_session.LINES)
    assert shape_window.session.view == app_session.LINES
    assert shape_window.search.text() == BETA
    assert pane.chips[0].isChecked() is True
    assert pane.rows() == ()


def test_an_unproven_line_is_still_listed_and_its_target_is_called_unproven(shape_window) -> None:
    pane = shape_window.pane
    key = pane.rows()[0].key
    assert shape_window.session.line(key).proven is False
    shape_window.show_line(key)
    assert key in [entry.key for entry in pane.table.model().entries()
                   if isinstance(entry, lineview.Line)]
    assert shape_window.context.proven.isVisible()
    assert shape_window.context.proven.text() == contextpane.NO_PROOF


def test_the_speaker_control_leads_with_the_unknown_count_and_the_pane_states_the_share(
        named_window) -> None:
    pane = named_window.pane
    assert pane.speaker_box.itemText(0) == lineview.ALL_SPEAKERS
    assert pane.speaker_box.itemText(1) == "Unknown speaker (1 line)"
    assert pane.speaker_box.itemText(2) == "Bulma"
    assert pane.speaker_box.itemText(3) == "No portrait"
    assert named_window.session.speaker_share() == (1, 3)
    named_window.show_line(pane.rows()[1].key)
    assert named_window.context.share.text() == "speaker known for 1 of 3 lines"


def test_the_context_pane_names_each_carrier_and_its_own_face(named_window) -> None:
    pane = named_window.pane
    table = named_window.context.contained
    assert table.columnCount() == 2
    assert [table.horizontalHeaderItem(column).text() for column in range(2)] == \
        ["Record", "Speaker"]
    seen = {}
    for line in pane.rows():
        named_window.show_line(line.key)
        assert table.rowCount() == len(named_window.session.covering(line.key))
        seen[line.key] = table.item(0, 1).text()
    assert seen[SHAPE_KEYS["alpha"]] == "Bulma"
    assert seen[SHAPE_KEYS["beta"]] == "No portrait"
    assert seen[SHAPE_KEYS["gamma"]] == app_session.UNKNOWN_SPEAKER


def test_the_list_says_what_is_empty_and_offers_one_way_out(shell) -> None:
    pane = shell.pane
    shell.search.setText("nothing at all matches this")
    assert pane.empty_state.isVisible()
    assert 'No line matches "nothing at all matches this"' in pane.empty_label.text()
    assert pane.empty_button.text() == lineview.CLEAR_SEARCH
    pane.empty_button.click()
    assert shell.search.text() == ""
    assert pane.empty_state.isVisible() is False

    pane.chips[0].setChecked(True)
    assert pane.empty_state.isVisible()
    assert pane.empty_button.text() == lineview.CLEAR_FILTERS
    # The checked state carries a glyph, so it does not rest on the fill alone.
    assert pane.chips[0].text().startswith("\u2713 ")
    pane.empty_button.click()
    assert pane.chips[0].isChecked() is False
    assert pane.empty_state.isVisible() is False


def test_the_move_notice_collapse_button_says_what_it_will_do(shell) -> None:
    shell.show_line(INNER_KEY)
    shell.apply_edit(INNER_KEY, APPENDED)
    button = shell.editor.notice.collapse_button
    assert button.text() == chipedit.HIDE_DETAILS
    button.setChecked(True)
    assert shell.editor.notice.detail.isVisible() is False
    assert button.text() == chipedit.SHOW_DETAILS


def test_a_search_typed_on_the_other_list_offers_the_tab_switch(shape_window) -> None:
    pane = shape_window.pane
    shape_window.search.setText(ALPHA)
    pane.set_kind(app_session.SLOT)
    assert pane.rows() == ()
    assert pane.empty_state.isVisible()
    assert pane.empty_button.text() == lineview.SHOW_DIALOGUE
    pane.empty_button.click()
    assert pane.kind() == app_session.RECORD
    assert [line.text for line in pane.rows()] == [ALPHA]


def test_the_table_elides_the_text_column_and_holds_the_status_width(shell) -> None:
    table = shell.pane.table
    assert table.textElideMode() == Qt.TextElideMode.ElideRight
    header = table.horizontalHeader()
    assert header.sectionResizeMode(lineview.COLUMN_TEXT) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(lineview.COLUMN_STATUS) == QHeaderView.ResizeMode.Fixed
    assert header.sectionResizeMode(lineview.COLUMN_SPEAKER) == QHeaderView.ResizeMode.Fixed
    assert table.columnWidth(lineview.COLUMN_STATUS) == lineview.STATUS_WIDTH
    assert shell.pane.tabs.height() == shell.metrics.row_height
