"""The editor sections and the context pane, offscreen and over a synthetic image.

No ROM and no window: the session is the model, and the two widgets render only
what it answers. Each case drives the widgets the way the shell does, so a
regression in the wiring fails here rather than in a click-through.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtTest import QSignalSpy, QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QTableWidgetItem  # noqa: E402

from tests.text_fixture import (  # noqa: E402
    SPACES,
    build,
    line_payload,
    lowered_record_floor,
)
from tools.buufury_text import chipedit, contextpane  # noqa: E402
from tools.buufury_text import session as app_session  # noqa: E402
from tools.buufury_text import theme  # noqa: E402
from tools.buufury_text.session import State  # noqa: E402

INNER = "Say hello!"
GROWN = INNER + "!"
#: The same length as INNER, so the working image can differ inside its own span.
DIFFERS = "Differs now"
#: The record the image left as the original game wrote it, and the outer carrier.
RETAIL_LINE = "Outer line is here ok!"


def retail_image(payload: bytes, records: list) -> bytes:
    """A build from one payload and one record list, for the pair of fixtures."""
    return build(payloads={1: bytes(payload)}, records=records)


def inner_key(session) -> str:
    """The key of the short spoken line, which is the one every case drives.

    The key is the engine's own identity of the row, never a constant this test
    invents: a fixture whose span arithmetic changes must not silently pass.
    """
    found = [row for row in session.rows_of(app_session.LINES)
             if row.text in (INNER, DIFFERS)]
    assert len(found) == 1, [row.text for row in session.rows_of(app_session.LINES)]
    assert found[0].target in found[0].covering
    return found[0].key


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def window(qapp):
    """The two widgets over one resolved theme, which is what the shell hands them."""
    resolved = theme.apply_theme(qapp, theme.MODE_DARK)
    shape = theme.metrics(qapp)
    yield chipedit.EditorSections(resolved, shape), contextpane.ContextPane(resolved, shape)


@pytest.fixture()
def session(tmp_path):
    """One spoken line inside a longer covering record, opened against a retail image.

    Both images say the same words here, so this fixture is the agreeing case the
    context pane has to fold into one line instead of repeating them.
    """
    payload = bytearray(SPACES)
    payload[0x20:0x20 + len(RETAIL_LINE) * 2] = RETAIL_LINE.encode("utf-16le")
    payload[0x36:0x36 + len(INNER) * 2] = INNER.encode("utf-16le")
    records = [(1, 0x20, len(RETAIL_LINE) * 2), (1, 0x36, len(INNER) * 2)]
    directory = Path(tmp_path)
    image = retail_image(payload, records)
    directory.joinpath("retail.gba").write_bytes(image)
    path = directory / "fixture.gba"
    path.write_bytes(image)
    with lowered_record_floor():
        return app_session.open_image(path, canonical=directory / "retail.gba",
                                      cutters_from_pool=False)


@pytest.fixture()
def differing(tmp_path):
    """The same two spans, but the working image already changed the inner line.

    The inner record's span ends one unit later than the agreeing fixture, so the
    retail wording for that row is the original game's own slice of the same span.
    """
    retail = bytearray(SPACES)
    retail[0x20:0x20 + len(RETAIL_LINE) * 2] = RETAIL_LINE.encode("utf-16le")
    retail[0x36:0x36 + len(INNER) * 2] = INNER.encode("utf-16le")
    working = bytearray(retail)
    working[0x36:0x36 + len(DIFFERS) * 2] = DIFFERS.encode("utf-16le")
    records = [(1, 0x20, len(RETAIL_LINE) * 2), (1, 0x36, len(DIFFERS) * 2)]
    directory = Path(tmp_path)
    directory.joinpath("retail.gba").write_bytes(retail_image(retail, records))
    path = directory / "working.gba"
    path.write_bytes(retail_image(working, records))
    with lowered_record_floor():
        return app_session.open_image(path, canonical=directory / "retail.gba",
                                      cutters_from_pool=False)


def show(editor, session, key: str = "") -> str:
    """Show one row the way the shell does: the row and the session's own answers."""
    key = key or inner_key(session)
    line = session.line(key)
    assert line is not None, key
    editor.set_line(line, session.state(key), session.meter(key),
                    session.differs_from_retail(key), session.refusal_reason(key),
                    session.covering(key), session.sites(key), line.proven)
    return key


# --- the three sections ------------------------------------------------------


def test_three_stacked_sections_build_with_one_emphasis(window) -> None:
    editor, _pane = window
    assert [editor.retail.name, editor.current.name, editor.new.name] == \
        ["RETAIL", "CURRENT", "NEW"]
    assert [section.label.text() for section in
            (editor.retail, editor.current, editor.new)] == ["RETAIL", "CURRENT", "NEW"]
    assert editor.retail.explanation.text() == chipedit.RETAIL_EXPLANATION
    assert editor.current.explanation.text() == chipedit.CURRENT_EXPLANATION
    assert editor.new.explanation.text() == chipedit.NEW_EXPLANATION
    # The two read-only sections refuse the keyboard and carry no caret.
    assert editor.retail.editor.isReadOnly() is True
    assert editor.current.editor.isReadOnly() is True
    assert editor.new.editor.isReadOnly() is False
    assert editor.retail.editor.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert editor.current.editor.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert editor.retail.editor.cursorWidth() == 0
    assert editor.current.editor.cursorWidth() == 0
    assert editor.new.editor.cursorWidth() > 0
    # Exactly one emphasis: the accent hairline sits on NEW's label, nowhere else.
    accent = theme.color(theme.active_theme(), "accent").name().lower()
    sheets = [section.label.styleSheet().lower() for section in
              (editor.retail, editor.current, editor.new)]
    assert ["border-top" in sheet for sheet in sheets] == [False, False, True]
    assert accent in sheets[2] and accent not in sheets[0] and accent not in sheets[1]


def test_set_line_fills_all_three_sections_from_the_session(window, session) -> None:
    editor, _pane = window
    key = inner_key(session)
    line = session.line(key)
    show(editor, session)
    assert line.retail == INNER
    assert editor.retail.editor.serialized() == line.retail
    assert editor.current.editor.serialized() == INNER
    assert editor.new_text() == INNER
    session.set_edit(key, "Say goodbye!")
    editor.set_pending(session.pending_text(key))
    assert editor.new_text() == "Say goodbye!"
    assert editor.current.editor.serialized() == INNER


# --- committing an edit ------------------------------------------------------


def test_typing_in_new_commits_the_key_and_the_text(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    spy = QSignalSpy(editor.committed)
    editor.focus_new()
    cursor = editor.new.editor.textCursor()
    cursor.setPosition(len(editor.new_text()))
    editor.new.editor.setTextCursor(cursor)
    QTest.keyClicks(editor.new.editor, "!")
    assert spy.count() == 1
    assert list(spy.at(0)) == [key, GROWN]


def test_committing_with_no_row_reports_nothing(window, session) -> None:
    """The signal carries a row key, so there is nothing to say without one."""
    editor, _pane = window
    editor.set_line(None)
    spy = QSignalSpy(editor.committed)
    editor.commit()
    assert spy.count() == 0


def test_the_read_only_sections_emit_nothing(window, session) -> None:
    editor, _pane = window
    show(editor, session)
    spy = QSignalSpy(editor.committed)
    for section in (editor.retail, editor.current):
        before = section.editor.serialized()
        QTest.keyClicks(section.editor, "Z")
        assert section.editor.serialized() == before
    assert spy.count() == 0


# --- what a state reads ------------------------------------------------------


def test_a_same_length_edit_reads_edited(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    session.set_edit(key, "Hi there")
    state = session.state(key)
    assert state is State.EDITED
    editor.set_state(state, session.meter(key))
    meter = session.meter(key)
    assert meter is not None
    assert f"{meter.chars} / {meter.chars_limit} chars" in editor.meter.text()
    assert f"{meter.bytes} / {meter.bytes_limit} bytes" in editor.meter.text()


def test_a_growth_past_the_record_reads_will_move(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    session.set_edit(key, GROWN)
    state = session.state(key)
    assert state is State.WILL_MOVE
    editor.set_state(state, session.meter(key))
    assert editor.meter.word.text() == chipedit.MOVE_HEADLINE
    assert session.pending_text(key) == GROWN


def test_a_sibling_line_in_the_same_record_reads_unchanged(window, session, tmp_path) -> None:
    """One record, two spoken lines: editing one leaves the other row alone."""
    editor, _pane = window
    path = Path(tmp_path) / "split.gba"
    path.write_bytes(build(payloads={1: line_payload("One\nTwo")},
                           records=[(1, 0x20, len("One\nTwo") * 2)]))
    with lowered_record_floor():
        split = app_session.open_image(path, cutters_from_pool=False)
    first, sibling = split.rows_of(app_session.LINES)
    assert first.target == sibling.target
    split.set_edit(first.key, "Uno")
    assert split.state(first.key) is State.EDITED
    assert split.state(sibling.key) is State.UNCHANGED
    show(editor, split, sibling.key)
    assert editor.new_text() == sibling.text
    assert editor.meter.chars.text() == chipedit.NO_EDIT


# --- the meter ---------------------------------------------------------------


def test_the_meter_reports_both_units_and_reserves_its_slot(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    assert editor.meter.text() == f"{chipedit.NO_EDIT}     {chipedit.NO_EDIT}"
    assert editor.meter.chars.track.tick_x(100) is None
    session.set_edit(key, GROWN)
    editor.set_state(session.state(key), session.meter(key))
    meter = session.meter(key)
    assert meter.bytes_limit == 20
    assert editor.meter.text() == f"{meter.chars} / 10 chars     {meter.bytes} / 20 bytes"
    assert meter.bytes > meter.bytes_limit
    assert editor.meter.stated() is True
    assert editor.meter.chars.track.tick_x(100) is not None
    assert editor.meter.word_shown() is True


def test_the_meter_marks_an_unstated_limit_as_unstated(window, session) -> None:
    editor, _pane = window
    show(editor, session)
    meter = app_session.Meter(chars=12, chars_limit=None, bytes=24, bytes_limit=None)
    editor.set_state(State.EDITED, meter)
    assert editor.meter.chars.text() == f"12 chars, {chipedit.UNSTATED} chars limit"
    assert editor.meter.bytes.text() == f"24 bytes, {chipedit.UNSTATED} bytes limit"
    assert editor.meter.stated() is False
    assert editor.meter.chars.track.tick_x(100) is None


# --- the move notice ---------------------------------------------------------


def test_the_move_notice_names_the_covering_records_and_the_site_count(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    covering = session.covering(key)
    assert covering
    assert session.sites(key) > 0
    session.set_edit(key, GROWN)
    show(editor, session)
    assert session.state(key) is State.WILL_MOVE
    assert editor.notice_shown() is True
    assert editor.notice.headline.text() == chipedit.MOVE_HEADLINE
    for carrier in covering:
        assert carrier in editor.notice.detail.text()
    assert f"{session.sites(key)} handle site(s)" in editor.notice.detail.text()
    spy = QSignalSpy(editor.notice.records_requested)
    editor.notice.select_button.click()
    assert spy.count() == 1
    assert tuple(spy.at(0)[0]) == covering


def test_the_collapse_button_says_what_it_will_do_next(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    session.set_edit(key, GROWN)
    show(editor, session)
    button = editor.notice.collapse_button
    assert button.text() == chipedit.HIDE_DETAILS
    assert editor.notice.detail_shown() is True
    button.setChecked(True)
    assert editor.notice.detail_shown() is False
    assert button.text() == chipedit.SHOW_DETAILS
    assert editor.notice_shown() is True
    button.setChecked(False)
    assert editor.notice.detail_shown() is True
    assert button.text() == chipedit.HIDE_DETAILS


def test_an_unproven_target_is_said_in_plain_words(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    editor.notice.show_notice(session.covering(key), session.sites(key), True, False)
    assert chipedit.UNPROVEN_TARGET in editor.notice.detail.text()


# --- a refusal ---------------------------------------------------------------


def test_a_refused_row_shows_the_engines_own_reason(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    line = session.line(key)
    session.set_edit(key, "x" * 2100)
    assert session.state(key) is State.REFUSED
    reason = session.refusal_reason(key)
    assert reason
    editor.set_line(line, session.state(key), session.meter(key),
                    session.differs_from_retail(key), reason,
                    session.covering(key), session.sites(key), line.proven)
    assert editor.meter.reason.text() == reason
    assert editor.meter.reason_shown() is True
    assert editor.meter.reason.text() == session.refusal_reason(key)


# --- the context pane --------------------------------------------------------


def test_the_context_pane_agrees_when_retail_and_current_agree(window, session) -> None:
    editor, pane = window
    key = show(editor, session)
    assert session.line(key).retail is not None
    assert session.differs_from_retail(key) is False
    pane.set_line(session, session.line(key))
    assert pane.retail.text() == contextpane.AGREES
    assert INNER not in pane.retail.text()


def test_the_context_pane_shows_the_wording_when_the_two_differ(window, differing) -> None:
    """The wording appears only where the image and the original disagree."""
    editor, pane = window
    key = show(editor, differing)
    line = differing.line(key)
    assert line.text == DIFFERS
    assert line.retail is not None and line.retail.startswith(INNER)
    assert differing.differs_from_retail(key) is True
    pane.set_line(differing, line)
    assert pane.retail.text() == line.retail
    assert pane.retail.text() != contextpane.AGREES


def test_the_carrier_table_shows_each_carriers_own_speaker_label(window, session, qapp) -> None:
    editor, pane = window
    key = show(editor, session)
    covering = session.covering(key)
    pane.set_line(session, session.line(key))
    table = pane.contained
    assert table.columnCount() == 2
    assert [table.horizontalHeaderItem(at).text() for at in range(2)] == \
        ["Record", contextpane.SPEAKER_HEADING]
    assert table.rowCount() == len(covering)
    for row, carrier in enumerate(covering):
        item = table.item(row, 1)
        assert isinstance(item, QTableWidgetItem)
        assert table.item(row, 0).text() == carrier
        assert item.text() == session.line(carrier).speaker_label
    assert table.verticalHeader().defaultSectionSize() == theme.metrics(qapp).row_height
    assert table.showGrid() is False


def test_the_address_disclosure_is_hidden_until_asked_for(window, session) -> None:
    editor, pane = window
    show(editor, session)
    assert pane.raw_field.isVisibleTo(pane) is False
    assert pane.raw_button.isChecked() is False
    assert pane.raw_button.text() == contextpane.ADDRESS_LABEL
    pane.set_address("1:54:20 offset 0x36 size 20")
    assert pane.raw_field.text() == "1:54:20 offset 0x36 size 20"
    assert pane.raw_field.isVisibleTo(pane) is False
    pane.raw_button.click()
    assert pane.raw_button.isChecked() is True
    assert pane.raw_field.isVisibleTo(pane) is True
    assert pane.raw_field.isReadOnly() is True


def test_the_preview_starts_in_its_waiting_state(window) -> None:
    """The pane forwards the text; the preview owns its own state and says what is absent."""
    _editor, pane = window
    assert pane.preview.state() in ("waiting", "ready", "incomplete")
    if pane.preview.state() != "ready":
        assert pane.preview.missing()
    pane.set_preview_state(INNER)
    assert pane.preview.state() in ("waiting", "ready", "incomplete")
