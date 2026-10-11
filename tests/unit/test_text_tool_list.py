"""The list pane, the rename window and the export summary, offscreen and ROM-free.

Every case runs over `tests.text_fixture`, so no ROM, no save and no window server is
needed. The portrait join the synthetic image does not carry is stood in for where a
case needs a speaker name or a gap; nothing here asserts a ROM value.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QSize, Qt  # noqa: E402
from PySide6.QtGui import QFontMetrics  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QHeaderView,
    QInputDialog,
    QPushButton,
    QToolButton,
)

from tests.text_fixture import (  # noqa: E402
    TEXT_SLOTS,
    build,
    line_payload,
    lowered_record_floor,
)
from tools.buufury_text import (  # noqa: E402
    exportdialog,
    lineview,
    renamedialog,
    settings,
    status,
    theme,
)
from tools.buufury_text import session as app_session  # noqa: E402
from tools.webfoot import textedit  # noqa: E402

ALPHA = "Alpha line"
BETA = "Beta line"
GAMMA = "Gamma line"
TWO_LINES = "One\nTwo"
NOTHING = "nothing at all matches this"

#: The synthetic image carries no appearance table, so the portrait join is stood in
#: for. Selector 3 is absent from the join, which is the unknown-speaker case.
PORTRAITS = {1: textedit.Portrait(8, textedit.NAMED_PORTRAIT, "Bulma"),
             2: textedit.Portrait(0, textedit.NO_PORTRAIT)}
SHAPE_KEYS = {"alpha": "1:32:20", "beta": "2:32:18", "gamma": "3:32:20"}

DIGEST = "a1" * 32


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def temporary_settings(tmp_path, monkeypatch):
    """A window that remembers its shape must not write the user's settings file."""
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")


@pytest.fixture()
def applied(qapp):
    return theme.apply_theme(qapp, theme.MODE_DARK)


# --- the synthetic images ----------------------------------------------------


def shape_image() -> bytes:
    """Three records in three containers, in the reverse of their handle order."""
    texts = (ALPHA, BETA, GAMMA)
    return build(payloads={1: line_payload(texts[0]), 2: line_payload(texts[1]),
                           3: line_payload(texts[2])},
                 records=[(3, 0x20, len(texts[2]) * 2), (1, 0x20, len(texts[0]) * 2),
                          (2, 0x20, len(texts[1]) * 2)])


def split_image() -> bytes:
    """One record holding two spoken lines, so the two views differ in row count."""
    return build(payloads={1: line_payload(TWO_LINES)},
                 records=[(1, 0x20, len(TWO_LINES) * 2)])


def gap_image() -> bytes:
    """One record whose span is only spaces, so the line list holds nothing."""
    return build(records=[(1, 0x20, 8)])


def opened(tmp_path, name: str, image: bytes, canonical=None):
    """A session over a synthetic image; no event pool exists, so every record cuts."""
    path = tmp_path / name
    path.write_bytes(image)
    with lowered_record_floor():
        return app_session.open_image(path, canonical=canonical, cutters_from_pool=False)


def pane_over(session, applied) -> lineview.LinePane:
    widget = lineview.LinePane(session, theme.active_metrics(), applied)
    widget.resize(760, 420)
    widget.show()
    return widget


def entry_row(model, key: str) -> int:
    for row, entry in enumerate(model.entries()):
        if isinstance(entry, lineview.Line) and entry.key == key:
            return row
    raise AssertionError(f"{key} is not in the list")


@pytest.fixture()
def shape_session(tmp_path, applied, monkeypatch):
    return opened(tmp_path, "shape.gba", shape_image())


@pytest.fixture()
def shape_pane(shape_session, applied):
    pane = pane_over(shape_session, applied)
    yield pane
    pane.close()


@pytest.fixture()
def named_session(tmp_path, applied, monkeypatch):
    monkeypatch.setattr(textedit, "portraits", lambda model: {
        record.key: PORTRAITS[record.selector] for record in model.records
        if record.selector in PORTRAITS})
    return opened(tmp_path, "named.gba", shape_image())


@pytest.fixture()
def named_pane(named_session, applied):
    pane = pane_over(named_session, applied)
    yield pane
    pane.close()


@pytest.fixture()
def split_session(tmp_path):
    return opened(tmp_path, "split.gba", split_image())


@pytest.fixture()
def split_pane(split_session, applied):
    pane = pane_over(split_session, applied)
    yield pane
    pane.close()


@pytest.fixture()
def gap_pane(tmp_path, applied):
    pane = pane_over(opened(tmp_path, "gap.gba", gap_image()), applied)
    yield pane
    pane.close()


# --- the list ----------------------------------------------------------------


def test_the_pane_lists_one_row_per_line_and_the_shape_switches_the_count(
        split_pane, split_session) -> None:
    assert split_pane.view() == app_session.LINES
    assert [line.text for line in split_pane.rows()] == ["One", "Two"]
    assert split_pane.kind() == app_session.RECORD
    # The count sits on the counters line beside the tabs, not inside the tab label,
    # because the two labels together elided their counts away at the pane's width.
    assert split_pane.tabs.tabText(0) == "Dialogue"
    assert split_pane.tabs.tabText(1) == "Names && bios"
    assert split_pane.tabs.tabToolTip(0) == "2 lines"
    assert split_pane.tabs.tabToolTip(1) == f"{TEXT_SLOTS} names"
    assert split_pane.counters.text().startswith("2 lines")
    assert split_pane.table.isColumnHidden(lineview.COLUMN_ID)
    assert split_pane.table.isColumnHidden(lineview.COLUMN_SPEAKER) is False

    split_pane.set_view(app_session.RECORDS)
    assert split_pane.view() == app_session.RECORDS
    assert split_session.view == app_session.RECORDS
    assert len(split_pane.rows()) == 1
    assert split_session.view_size(app_session.RECORDS) == 1
    assert split_pane.table.isColumnHidden(lineview.COLUMN_ID) is False

    split_pane.set_view(app_session.LINES)
    assert len(split_pane.rows()) == 2
    assert split_pane.tabs.height() == theme.active_metrics().tab_height


def test_the_speaker_column_shows_the_name_the_gap_word_and_the_unknown_word(
        named_pane) -> None:
    model = named_pane.table.model()
    assert model.headerData(lineview.COLUMN_SPEAKER, Qt.Orientation.Horizontal,
                            Qt.ItemDataRole.DisplayRole) == "Speaker (by portrait)"
    keys = {line.key: line for line in named_pane.rows()}
    assert keys[SHAPE_KEYS["alpha"]].speaker_label == "Bulma"
    assert keys[SHAPE_KEYS["beta"]].speaker_label == "No portrait"
    assert keys[SHAPE_KEYS["gamma"]].speaker_label == app_session.UNKNOWN_SPEAKER

    def cell(key: str, role: int) -> object:
        return model.data(model.index(entry_row(model, key), lineview.COLUMN_SPEAKER), role)

    muted = theme.color(theme.active_theme(), "text_secondary").name()
    assert cell(SHAPE_KEYS["alpha"], Qt.ItemDataRole.DisplayRole) == "Bulma"
    assert cell(SHAPE_KEYS["alpha"], Qt.ItemDataRole.ForegroundRole) is None
    for key in (SHAPE_KEYS["beta"], SHAPE_KEYS["gamma"]):
        assert cell(key, Qt.ItemDataRole.ForegroundRole).name() == muted
    assert named_pane.speaker_caption.text() == lineview.SPEAKER_HEADER
    assert named_pane.speaker_box.itemText(0) == lineview.ALL_SPEAKERS
    assert named_pane.speaker_box.itemText(1) == "Unknown speaker (1 line)"


def test_the_speaker_control_narrows_the_list_and_gives_it_back(named_pane) -> None:
    named_pane.set_speaker("Bulma")
    assert [line.text for line in named_pane.rows()] == [ALPHA]
    assert named_pane.speaker() == "Bulma"
    named_pane.set_speaker(app_session.UNKNOWN_SPEAKER)
    assert [line.text for line in named_pane.rows()] == [GAMMA]
    named_pane.set_speaker(None)
    assert len(named_pane.rows()) == 3
    assert named_pane.speaker() is None


def test_the_state_chips_narrow_the_list_and_the_clear_action_restores_it(
        split_pane, split_session) -> None:
    first, second = split_pane.rows()
    split_session.set_edit(first.key, "Uno")
    assert split_session.state(first.key) is app_session.State.EDITED
    split_pane.chips[0].setChecked(True)
    assert split_pane.chips[0].text().startswith("\u2713 ")
    assert [line.key for line in split_pane.rows()] == [first.key]
    split_pane.chips[0].setChecked(False)

    # Nothing is refused, so that chip leaves nothing and offers the one way out.
    split_pane.chips[2].setChecked(True)
    assert split_pane.rows() == ()
    assert split_pane.empty_state.isVisible()
    assert split_pane.empty_action.text() == lineview.CLEAR_FILTERS
    assert len(split_pane.empty_state.findChildren(QPushButton)) == 1
    split_pane.empty_action.click()
    assert [chip.isChecked() for chip in (*split_pane.chips, split_pane.control_chip)] == \
        [False, False, False, False]
    assert [line.key for line in split_pane.rows()] == [first.key, second.key]
    assert split_pane.empty_state.isVisible() is False
    assert split_pane.filters() == (frozenset(), None)


def test_speaker_grouping_heads_each_label_with_its_count_and_unknown_last(
        named_pane) -> None:
    named_pane.set_group(app_session.BY_SPEAKER)
    model = named_pane.table.model()
    headings = [entry for entry in model.entries() if isinstance(entry, lineview.Group)]
    assert [group.label for group in headings] == ["Bulma", "No portrait",
                                                   app_session.UNKNOWN_SPEAKER]
    assert [len(group.rows) for group in headings] == [1, 1, 1]
    assert model.data(model.index(0, 0), lineview.ROLE_HEADING) == ("Bulma (1)", "")
    assert model.flags(model.index(0, 0)) == Qt.ItemFlag.NoItemFlags
    assert named_pane.table.columnSpan(0, 0) == model.columnCount()


def test_place_grouping_is_ordered_by_map_table_and_names_why_a_row_is_unplaced(
        shape_pane, shape_session) -> None:
    shape_pane.set_group(app_session.BY_PLACE)
    model = shape_pane.table.model()
    headings = [entry for entry in model.entries() if isinstance(entry, lineview.Group)]
    placed, total = shape_session.place_coverage()
    # The synthetic image carries no map table, so every row falls in the one group
    # that says why. The order property is asserted over whatever groups come back.
    assert headings[-1].label == app_session.UNPLACED
    assert all(group.label and group.label != app_session.UNPLACED
               for group in headings[:-1])
    assert sum(len(group.rows) for group in headings
               if group.label != app_session.UNPLACED) == placed
    assert len(headings[-1].rows) == total - placed
    assert model.data(model.index(0, 0), lineview.ROLE_HEADING) == \
        (f"Unplaced ({total})", lineview.NO_PLACE_LINK)
    # A heading that carries its reason is a two-line row, so it is taller than a row,
    # and the room above its label is larger than the room below it.
    assert shape_pane.table.rowHeight(0) > shape_pane.table.rowHeight(1)
    assert shape_session.map_order() == ()


def test_the_place_tooltip_states_the_coverage_and_where_the_link_comes_from(
        shape_pane, shape_session) -> None:
    index = shape_pane.group_box.findData(app_session.BY_PLACE)
    tooltip = shape_pane.group_box.itemData(index, Qt.ItemDataRole.ToolTipRole)
    placed, total = shape_session.place_coverage()
    assert f"{placed} of {total} lines have one" in tooltip
    assert app_session.PLACE_EVIDENCE in tooltip
    assert "no proven map" not in tooltip


def test_appearance_and_storage_hold_the_same_rows_in_a_different_first_row(
        shape_pane) -> None:
    appearance = [line.key for line in shape_pane.rows()]
    assert appearance[0] == SHAPE_KEYS["gamma"]
    shape_pane.set_order(app_session.STORAGE)
    storage = [line.key for line in shape_pane.rows()]
    assert shape_pane.order() == app_session.STORAGE
    assert storage[0] == SHAPE_KEYS["alpha"]
    assert set(appearance) == set(storage)


def test_a_term_that_matches_nothing_offers_one_action_and_a_gap_offers_none(
        shape_pane, gap_pane) -> None:
    cleared = []
    shape_pane.search_cleared.connect(lambda: cleared.append(True))
    shape_pane.set_term(NOTHING)
    assert shape_pane.rows() == ()
    assert shape_pane.empty_state.isVisible()
    assert f'No line matches "{NOTHING}"' in shape_pane.empty_label.text()
    assert shape_pane.empty_action.isVisible()
    assert shape_pane.empty_action.text() == lineview.CLEAR_SEARCH
    shape_pane.empty_action.click()
    assert shape_pane.rows()
    assert cleared == [True]

    # The image itself carries no spoken line, and no action could change that.
    assert gap_pane.rows() == ()
    assert gap_pane.empty_state.isVisible()
    assert "no line" in gap_pane.empty_label.text()
    assert gap_pane.empty_action.text() == ""
    assert gap_pane.empty_action.isVisible() is False


def test_the_text_column_stretches_the_status_keeps_its_width_and_the_text_elides(
        shape_pane) -> None:
    header = shape_pane.table.horizontalHeader()
    assert header.sectionResizeMode(lineview.COLUMN_TEXT) == QHeaderView.ResizeMode.Stretch
    for column in (lineview.COLUMN_ID, lineview.COLUMN_SPEAKER, lineview.COLUMN_STATUS):
        assert header.sectionResizeMode(column) == QHeaderView.ResizeMode.Fixed
    assert shape_pane.table.columnWidth(lineview.COLUMN_STATUS) == shape_pane.status_width
    assert shape_pane.table.textElideMode() == Qt.TextElideMode.ElideRight
    assert header.textElideMode() == Qt.TextElideMode.ElideRight
    widest = max((entry.word for entry in status.PRESENTATION.values()), key=len)
    assert shape_pane.status_width >= lineview.MARKER_COLUMN + QFontMetrics(
        theme.fonts().strong).horizontalAdvance(widest)


def test_the_row_is_drawn_with_one_divider_the_selection_and_the_state_badge(
        split_pane, split_session) -> None:
    table = split_pane.table
    applied = theme.active_theme()
    selected = table.currentIndex()
    assert selected.isValid() and selected.row() == 0
    other = table.model().index(1, lineview.COLUMN_TEXT)
    # The viewport has no header and no frame in it, so a row position is a pixel here.
    image = table.viewport().grab().toImage()

    def pixel(row: int, x: int) -> str:
        y = table.rowViewportPosition(row) + table.rowHeight(row) // 2
        return image.pixelColor(x, y).name()

    # The selection fill spans the row, and the accent indicator survives a colour
    # check at the left edge. The row every other row is the surface: no zebra.
    assert image.pixelColor(1, table.rowHeight(0) // 2).name() == \
        theme.color(applied, "accent").name()
    assert pixel(0, 240) == theme.color(applied, "selection").name()
    assert pixel(1, 240) == theme.color(applied, "surface").name()

    # The state cell carries its badge fill, and the row ends in one 1 px divider.
    state = split_session.state(split_session.lines[0].key)
    badge_x = table.columnViewportPosition(lineview.COLUMN_STATUS) + 48
    inside_badge = table.rowViewportPosition(0) + theme.active_metrics().pad_sm
    assert image.pixelColor(badge_x, inside_badge).name() == \
        theme.state_colors(applied, state)[0].name()
    bottom = table.rowViewportPosition(1) + table.rowHeight(1) - 1
    assert image.pixelColor(240, bottom).name() == theme.color(applied, "divider").name()


def test_home_and_end_move_to_the_row_ends_and_never_stop_on_a_heading(named_pane) -> None:
    named_pane.set_group(app_session.BY_SPEAKER)
    table = named_pane.table
    model = table.model()
    rows = model.row_rows()
    assert len(rows) == 3 and len(model.entries()) == 6
    table.setCurrentIndex(model.index(rows[0], table.cursor_column()))
    QTest.keyClick(table, Qt.Key.Key_End)
    assert table.currentIndex().row() == rows[-1]
    QTest.keyClick(table, Qt.Key.Key_Home)
    assert table.currentIndex().row() == rows[0]
    QTest.keyClick(table, Qt.Key.Key_Down)
    assert table.currentIndex().row() in rows
    assert table.currentIndex().row() != rows[0]
    assert model.key_at(table.currentIndex().row())


def test_a_row_can_be_selected_by_key_and_counted(named_pane) -> None:
    keys = [line.key for line in named_pane.rows()]
    assert named_pane.selected() == keys[0]
    assert named_pane.select_rows([keys[1], keys[2], "no such key"]) == 2
    assert named_pane.selected() == keys[1]
    assert named_pane.select_rows(["no such key"]) == 0
    assert named_pane.select_key(keys[2]) is True
    assert named_pane.selected() == keys[2]
    assert named_pane.select_key("no such key") is False
    assert named_pane.select_first([keys[0], keys[1]]) is True


# --- the rename window -------------------------------------------------------


#: One record whose two occurrences of the same word read differently in retail, so
#: one row will change and the other will not.
BETA_WORKING = "Beta and Beta"
BETA_RETAIL = "Beta and Red "


@pytest.fixture()
def rename_session(tmp_path):
    records = [(1, 0x20, len(BETA_WORKING) * 2)]
    working = tmp_path / "working.gba"
    retail = tmp_path / "retail.gba"
    working.write_bytes(build(payloads={1: line_payload(BETA_WORKING)}, records=records))
    retail.write_bytes(build(payloads={1: line_payload(BETA_RETAIL)}, records=records))
    with lowered_record_floor():
        return app_session.open_image(working, canonical=retail, cutters_from_pool=False)


def test_the_rename_window_counts_only_the_rows_that_change(rename_session) -> None:
    hits = rename_session.rename_hits("Beta")
    assert [(hit.at, hit.decision) for hit in hits] == \
        [(0, textedit.RENAME), (9, textedit.KEEP)]
    dialog = renamedialog.RenameDialog(rename_session, "Beta", "Arena")
    dialog.show()
    try:
        assert dialog.default_choice() == textedit.UNCLEAR
        assert dialog.model.effective(1) == textedit.KEEP
        assert dialog.apply_button.text() == "Apply 1 decisions"
        assert dialog.chosen() == ((hits[0].key, frozenset({0})),)
        assert dialog.focusWidget() is dialog.table
        assert dialog.minimumSize() == QSize(720, 420)
        assert dialog.cancel_button.text() == "Cancel"

        # Accepting the row retail declined adds its offset to the same record.
        index = dialog.model.index(1, renamedialog.DECISION_COLUMN)
        assert dialog.model.setData(index, textedit.RENAME, renamedialog.ROLE_CHOSEN)
        assert dialog.apply_button.text() == "Apply 2 decisions"
        assert dialog.chosen() == ((hits[0].key, frozenset({0, 9})),)

        # Space cycles one row through Rename, Keep and Ask.
        dialog.table.setCurrentIndex(dialog.model.index(0, renamedialog.DECISION_COLUMN))
        QTest.keyClick(dialog.table, Qt.Key.Key_Space)
        assert dialog.model.effective(0) == textedit.KEEP
        assert dialog.apply_button.text() == "Apply 1 decisions"
        assert dialog.chosen() == ((hits[0].key, frozenset({9})),)

        # The default control answers every undecided row at once: once both rows are
        # back to Ask, a Keep default leaves nothing to change.
        for row in (0, 1):
            dialog.model.setData(dialog.model.index(row, renamedialog.DECISION_COLUMN),
                                 textedit.UNCLEAR, renamedialog.ROLE_CHOSEN)
        assert dialog.apply_button.text() == "Apply 0 decisions"
        dialog.default_box.setCurrentIndex(dialog.default_box.findData(textedit.RENAME))
        assert dialog.default_choice() == textedit.RENAME
        assert dialog.apply_button.text() == "Apply 2 decisions"
        assert dialog.chosen() == ((hits[0].key, frozenset({0, 9})),)
        dialog.default_box.setCurrentIndex(dialog.default_box.findData(textedit.KEEP))
        assert dialog.default_choice() == textedit.KEEP
        assert dialog.chosen() == ()
        assert dialog.apply_button.text() == "Apply 0 decisions"
    finally:
        dialog.close()


def test_the_two_names_can_be_typed_here_and_refill_the_table_without_a_prompt(
        rename_session) -> None:
    dialog = renamedialog.RenameDialog(rename_session)
    dialog.show()
    try:
        # Nothing was passed in, so the window collects both names itself.
        assert dialog.findChildren(QInputDialog) == []
        assert dialog.model.rowCount() == 0
        assert dialog.notice.isVisible()
        assert dialog.apply_button.isEnabled() is False

        dialog.old_edit.setText("B")
        assert dialog.model.rowCount() == 0
        assert "two characters" in dialog.notice.text()
        assert dialog.apply_button.isEnabled() is False

        dialog.old_edit.setText("Beta")
        assert dialog.model.rowCount() == 2
        assert dialog.notice.isVisible() is False
        assert dialog.old_edit.font().pixelSize() == theme.fonts().body.pixelSize()
        # A count is not yet an apply: there is no name to put in its place.
        assert dialog.apply_button.text() == "Apply 1 decisions"
        assert dialog.apply_button.isEnabled() is False
        dialog.new_edit.setText("Arena")
        assert dialog.apply_button.isEnabled() is True
        assert dialog.apply_button.text() == "Apply 1 decisions"
        assert dialog.default_choice() == textedit.UNCLEAR

        dialog.old_edit.setText("")
        assert dialog.model.rowCount() == 0
        assert dialog.notice.isVisible()
        assert dialog.chosen() == ()
        assert dialog.apply_button.isEnabled() is False
    finally:
        dialog.close()


# --- the export summary ------------------------------------------------------


def export_report(refused: int = 0) -> dict:
    return {"input": "fixture.gba", "input_sha256": "b2" * 32,
            "output_sha256": DIGEST, "output_bytes": 123456, "in_place": 3,
            "moved": 1, "refused": refused, "warnings": 0}


def test_the_export_window_shows_the_facts_the_digest_and_one_close_action(
        tmp_path, applied) -> None:
    path = tmp_path / "out" / "fixture-edited.gba"
    dialog = exportdialog.ExportDialog(export_report(), path)
    dialog.show()
    try:
        assert dialog.message.text() == "Export complete"
        assert dialog.refusal.isVisible() is False
        assert dialog.values["File"].text() == path.name
        assert dialog.values["Edits applied"].text() == "3"
        assert dialog.values["Records moved"].text() == "1"
        assert dialog.values["Output size"].text() == "123456 bytes"
        assert dialog.digest() == DIGEST
        assert dialog.values["SHA-256"].font().family() == theme.mono_font().family()
        assert dialog.copy_button.isEnabled()
        assert dialog.findChildren(QPushButton) == [dialog.close_button]
        assert dialog.close_button.text() == "Close"
        assert dialog.close_button.isDefault()
        QTest.mouseClick(dialog.copy_button, Qt.MouseButton.LeftButton)
        assert QApplication.clipboard().text() == DIGEST
    finally:
        dialog.close()


def test_the_export_window_never_presents_a_refusal_as_a_success(tmp_path, applied) -> None:
    dialog = exportdialog.ExportDialog(export_report(refused=2), tmp_path / "out.gba")
    dialog.show()
    try:
        assert dialog.message.text() != "Export complete"
        assert "refused" in dialog.message.text()
        assert dialog.refusal.isVisible()
        assert "2" in dialog.refusal.text()
        assert dialog.values["Records moved"].text() == "1"
        assert dialog.close_button.text() == "Close"
        assert dialog.findChildren(QToolButton) == [dialog.copy_button]
    finally:
        dialog.close()
