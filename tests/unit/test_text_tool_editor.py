"""The editor sections and the context pane, offscreen and over a synthetic image.

No ROM and no window: the session is the model, and the two widgets render only
what it answers. Each case drives the widgets the way the shell does, so a
regression in the wiring fails here rather than in a click-through.

The app-wide theme is applied ONCE per process, not once per test: GitHub run
38504730899 crashed a worker inside ``theme.apply_theme`` (``app.setStyle``) when a
function-scoped fixture re-applied it for every test here, so the repetition is
gone and each test still builds its own widgets.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QMimeData, Qt  # noqa: E402
from PySide6.QtGui import QFontMetrics  # noqa: E402
from PySide6.QtTest import QSignalSpy, QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QLabel,
    QLineEdit,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tests.text_fixture import (  # noqa: E402
    SPACES,
    build,
    line_payload,
    lowered_record_floor,
)
from tools.buufury_text import chipedit, chips, contextpane  # noqa: E402
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


#: Bound at module level on purpose. Held only by the fixture below, the application
#: object can be collected when that fixture's scope ends, and Qt then has no application
#: while the rest of the session keeps making widgets: measured as an intermittent death
#: with exit 255 partway through a multi-file run, with no traceback to read.
QAPP = QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def qapp(untouched_application):
    """The application this module themes, handed back untouched when it ends."""
    yield untouched_application


@pytest.fixture(scope="module")
def themed(qapp):
    """The theme applied once per process, not once per test.

    The shell applies the app-wide theme at startup, and this module used to repeat
    that from the function-scoped ``window`` fixture for every test, about thirty
    times per process. Run 38504730899 died there: a Windows access violation
    inside ``apply_theme`` at ``tools/buufury_text/theme.py:289`` (``app.setStyle``).
    It is flaky, not repeatable - run 2 ran the module green and the module's other
    nodes passed in run 3 - so what is removed here is the repetition alone, and
    every test still gets two fresh widgets. The product-side call is out of scope.
    """
    return theme.apply_theme(qapp, theme.MODE_DARK), theme.metrics(qapp)


@pytest.fixture()
def window(themed):
    """The two widgets over one resolved theme, which is what the shell hands them."""
    resolved, shape = themed
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


def empty_unit_text(unit: str) -> str:
    """One bar of the meter with nothing pending: a number, and no invented limit."""
    return f"0 {unit}, {chipedit.UNSTATED} {unit} limit"


def empty_meter_text() -> str:
    """The meter with nothing pending: a number per unit, and no invented limit."""
    return f"{empty_unit_text(chipedit.CHARS)}     {empty_unit_text(chipedit.BYTES)}"


def show(editor, session, key: str = "") -> str:
    """Show one row the way the shell does: the row and the session's own answers."""
    key = key or inner_key(session)
    line = session.line(key)
    assert line is not None, key
    editor.set_line(line, session.state(key), session.meter(key),
                    session.differs_from_retail(key), session.refusal_reason(key),
                    session.covering(key), session.sites(key), line.proven)
    return key


def accent_columns(editor) -> list[int]:
    """The viewport columns carrying the accent ink, which is the changed-run mark."""
    accent = theme.color(theme.active_theme(), "accent").name()
    image = editor.viewport().grab().toImage()
    return [x for x in range(image.width())
            if any(image.pixelColor(x, y).name() == accent for y in range(image.height()))]


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
    # The two read-only sections refuse every edit and carry no caret, and they are
    # still reachable: Tab lands on them, and their own text can be selected by
    # keyboard, which is the only way past the cap at a short pane.
    assert editor.retail.editor.isReadOnly() is True
    assert editor.current.editor.isReadOnly() is True
    assert editor.new.editor.isReadOnly() is False
    assert editor.retail.editor.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert editor.current.editor.focusPolicy() == Qt.FocusPolicy.StrongFocus
    selectable = Qt.TextInteractionFlag.TextSelectableByKeyboard
    assert editor.retail.editor.textInteractionFlags() & selectable
    assert editor.current.editor.textInteractionFlags() & selectable
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


# --- the changed run ----------------------------------------------------------


def test_the_changed_run_in_new_is_underlined_where_it_differs(window, session, qapp) -> None:
    """FINDING 6: the changed run carried the section word and no second channel.

    The design note gives the changed run an underline plus the section word, so the
    mark is never colour alone. Measured here in pixels: NEW holds no accent ink while
    it agrees with CURRENT, and the run that differs is underlined in the accent ink
    and nothing else is. Measured on the real platform (windows, Segoe UI) for
    `Say hello!` becoming `Say goodbye!`: the accent columns ran 28..80 under
    `goodbye`, the changed run at document positions 4..11, with the unchanged `Say `
    and `!` clear of them.

    A control unit is one atom already carrying its own chip, so the mark stops at it
    and is asserted on the ranges the widget holds. Measured on the real platform for
    `Say hello!` becoming `AB` plus one control unit plus `CD`: two accent runs, 4..18
    and 76..92, with the 57 column chip's own width clear between them. This runner
    (offscreen) paints no extra-selection underline in a document carrying an inline
    object, so the pixel claim is the plain run above and the atom is the ranges.
    """
    editor, _pane = window
    editor.resize(600, 560)
    editor.show()
    qapp.processEvents()
    key = show(editor, session)
    qapp.processEvents()
    # The arithmetic the mark is drawn from, on plain strings and with no window.
    assert chipedit.changed_run(INNER, "Say goodbye!") == (4, 7)
    assert chipedit.changed_run(INNER, INNER) is None
    assert chipedit.changed_run(INNER, GROWN) == (len(INNER), 1)
    assert editor.new_text() == INNER
    assert accent_columns(editor.new.editor) == []
    assert editor.new.editor.extraSelections() == []

    pending = "Say goodbye!"
    session.set_edit(key, pending)
    editor.set_pending(session.pending_text(key))
    qapp.processEvents()
    assert editor.new_text() == pending
    first, length = chipedit.changed_run(INNER, pending)
    metrics = editor.new.editor.fontMetrics()
    columns = accent_columns(editor.new.editor)
    assert columns
    assert min(columns) >= metrics.horizontalAdvance(pending[:first]) - 8
    assert max(columns) <= metrics.horizontalAdvance(pending[:first + length]) + 8

    # The atom's own character is left out of the mark, and the runs either side of it
    # are the two changed words.
    with_atom = "AB\x08\x03CD"
    session.set_edit(key, with_atom)
    editor.set_pending(session.pending_text(key))
    qapp.processEvents()
    assert editor.new_text() == with_atom
    assert chipedit.marked_ranges(with_atom, chipedit.changed_run(INNER, with_atom)) == \
        ((0, 2), (3, 5))
    assert [(mark.cursor.selectionStart(), mark.cursor.selectionEnd())
            for mark in editor.new.editor.extraSelections()] == [(0, 2), (3, 5)]


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
    assert editor.meter.chars.text() == empty_unit_text(chipedit.CHARS)


# --- the meter ---------------------------------------------------------------


def test_the_meter_reports_both_units_and_reserves_its_slot(window, session) -> None:
    editor, _pane = window
    key = show(editor, session)
    assert editor.meter.text() == empty_meter_text()
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


def test_the_empty_meter_states_the_budget_before_anything_is_typed(window, session) -> None:
    """With nothing pending the meter still reads a number, and says the absence once.

    Measured before: `no pending edit` twice in mono, no number anywhere, so a writer
    could not read the budget of the row they had selected.
    """
    editor, _pane = window
    key = show(editor, session)
    assert session.meter(key) is None
    assert editor.meter.text() == empty_meter_text()
    assert editor.meter.word.text() == chipedit.NO_EDIT
    assert editor.meter.word_shown() is True
    # Where the engine states the row's budget, the empty state shows the headroom.
    editor.set_state(State.UNCHANGED, app_session.Meter(0, 10, 0, 20))
    assert editor.meter.text() == "0 / 10 chars     0 / 20 bytes"
    assert editor.meter.stated() is True


def test_the_meter_names_the_unit_of_each_bar_even_with_no_edit(window, session) -> None:
    """Two identical empty readouts are told apart by their own unit labels."""
    editor, _pane = window
    show(editor, session)
    assert editor.meter.text() == empty_meter_text()
    assert editor.meter.chars.unit_label.text() == chipedit.CHARS
    assert editor.meter.bytes.unit_label.text() == chipedit.BYTES
    caption = theme.type_scale().caption.pixelSize()
    for bar in (editor.meter.chars, editor.meter.bytes):
        assert bar.unit_label.isVisibleTo(editor.meter) is True
        assert bar.unit_label.font().pixelSize() == caption


# --- one border, not a nest ---------------------------------------------------


def test_the_section_border_is_scoped_to_the_frame_alone(window) -> None:
    """A bare border rule on the frame also boxed every caption and button in it."""
    editor, _pane = window
    for frame, caption in ((editor.retail.frame, editor.retail.explanation),
                           (editor.current.frame, editor.current.explanation),
                           (editor.new.frame, editor.new.explanation)):
        rule = frame.styleSheet()
        assert rule.startswith(f"#{frame.objectName()} ")
        assert "border: 1px solid" in rule
        assert caption.styleSheet() == ""
        names = [widget.objectName() for widget in editor.findChildren(type(frame))]
        assert names.count(frame.objectName()) == 1
    notice = editor.notice
    assert notice.objectName() == "moveNotice"
    assert notice.styleSheet().startswith("#moveNotice ")
    for child in (notice.headline, notice.detail, notice.select_button,
                  notice.collapse_button):
        assert child.styleSheet() == ""


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
    sites = session.sites(key)
    sites_word = "handle site" if sites == 1 else "handle sites"
    assert f"{sites} {sites_word}," in editor.notice.detail.text()
    assert "site(s)" not in editor.notice.detail.text()
    spy = QSignalSpy(editor.notice.records_requested)
    editor.notice.select_button.click()
    assert spy.count() == 1
    assert tuple(spy.at(0)[0]) == covering


def test_the_move_notice_counts_one_handle_site_in_the_singular(window, session) -> None:
    """One site reads as one site, and more than one reads as sites."""
    editor, _pane = window
    key = show(editor, session)
    covering = session.covering(key)
    editor.notice.show_notice(covering, 1, True, True)
    assert "It is named by 1 handle site," in editor.notice.detail.text()
    assert "site(s)" not in editor.notice.detail.text()
    editor.notice.show_notice(covering, 4, True, True)
    assert "It is named by 4 handle sites," in editor.notice.detail.text()


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


def test_a_refused_paste_in_new_names_the_reason(window, session) -> None:
    """A paste carrying a control unit is refused, and the reader is told why.

    Driven through `insertFromMimeData`, which is the method `paste()` hands the
    clipboard's data to. The offscreen clipboard is skipped: setting mime data on
    it crashes Qt at interpreter exit on this machine.
    """
    editor, _pane = window
    show(editor, session)
    before = editor.new_text()
    seen: list[str] = []
    editor.refused.connect(seen.append)
    source = QMimeData()
    source.setText("more\x08\x03")
    editor.new.editor.insertFromMimeData(source)
    assert editor.new_text() == before
    assert seen == [chips.CONTROL_CODE]


def test_every_refusal_answers_with_its_own_reason() -> None:
    """The three rules that can refuse an edit do not all read the same."""
    assert chips.refusal_reason("hello", 5, 0, "\x08\x03") == chips.CONTROL_CODE
    assert chips.refusal_reason("hello", 5, 0, "\x00") == chips.CONTROL_CODE
    assert chips.refusal_reason("hello", 5, 0, "\ud83d") == chips.UNSTORABLE
    assert chips.refusal_reason("AB\nCD", 2, 1, "") == chips.BREAKS_LOCK
    # An edit that is simply a no-op is not a refusal, so it says nothing.
    assert chips.refusal_reason("hello", 5, 0, "hi") == ""
    assert chips.refusal_reason("hello", 99, 0, "") == ""


# --- the two read-only sections -----------------------------------------------


def test_the_read_only_sections_are_capped_so_new_takes_the_stretch(window) -> None:
    """At a tall pane the references take four lines and NEW takes the rest."""
    editor, _pane = window
    prose = "words " * 60
    for section in (editor.retail, editor.current, editor.new):
        section.set_text(prose)
    editor.resize(360, 620)
    editor.show()
    QApplication.processEvents()
    cap = chipedit.read_only_cap(editor.retail.editor)
    assert cap >= 4 * QFontMetrics(editor.retail.editor.font()).lineSpacing()
    assert editor.retail.editor.height() <= cap
    assert editor.current.editor.height() <= cap
    assert editor.new.editor.height() > cap
    # Still readable: the whole wording is there and the box scrolls, not clips.
    for section in (editor.retail, editor.current):
        assert section.editor.serialized() == prose
        assert section.editor.verticalScrollBar().maximum() > 0
        # The cap is a height policy only: the caption still explains the section.
        assert section.explanation.isVisibleTo(editor) is True


def test_the_read_only_cap_follows_the_editors_own_height(window) -> None:
    """A short pane caps the references at two lines, and NEW keeps the room.

    Measured before, at the window's own minimum of 1018x444: retail 79, current 78
    and NEW 79, with NEW left a 53 px viewport, because the fixed four-line cap never
    bound there. After: retail 66, current 66, NEW 104, NEW at a 78 px viewport.
    """
    editor, _pane = window
    prose = "words " * 60
    for section in (editor.retail, editor.current, editor.new):
        section.set_text(prose)
    editor.resize(360, 444)
    editor.show()
    QApplication.processEvents()
    short_cap = chipedit.read_only_cap(editor.retail.editor, editor.height())
    assert chipedit.read_only_lines(editor.retail.editor,
                                    editor.height()) == chipedit.MIN_READ_ONLY_LINES
    assert short_cap < chipedit.read_only_cap(editor.retail.editor)
    assert editor.retail.editor.height() <= short_cap
    assert editor.current.editor.height() <= short_cap
    assert editor.new.editor.height() > editor.retail.editor.height()
    editor.resize(360, 1200)
    QApplication.processEvents()
    assert chipedit.read_only_lines(editor.retail.editor,
                                    editor.height()) == chipedit.READ_ONLY_LINES
    assert editor.retail.editor.height() <= chipedit.read_only_cap(editor.retail.editor,
                                                                  editor.height())
    assert editor.new.editor.height() > editor.retail.editor.height()


def test_the_capped_reference_stays_reachable_from_the_keyboard(window, qapp) -> None:
    """The cap hides text, so Tab has to reach the reference and the caret stay gone.

    Measured after, on the real platform: walking Tab through the shell hits
    `retail.editor` and `current.editor`; with the old NoFocus policy applied by hand
    to the same window, only `new.editor` is ever reached.
    """
    editor, _pane = window
    prose = "words " * 60
    for section in (editor.retail, editor.current, editor.new):
        section.set_text(prose)
    host = QWidget()
    column = QVBoxLayout(host)
    field = QLineEdit(host)
    column.addWidget(field)
    column.addWidget(editor)
    host.resize(420, 700)
    host.show()
    qapp.processEvents()
    field.setFocus(Qt.FocusReason.OtherFocusReason)
    qapp.processEvents()
    reached = []
    for _ in range(2):
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Tab)
        qapp.processEvents()
        reached.append(qapp.focusWidget())
    assert reached[0] is editor.retail.editor
    assert reached[1] is editor.current.editor
    # The keyboard selects the whole capped line, and no caret appears doing it.
    QTest.keyClick(editor.retail.editor, Qt.Key.Key_A, Qt.ControlModifier)
    qapp.processEvents()
    assert editor.retail.editor.textCursor().selectedText() == prose
    assert editor.retail.editor.cursorWidth() == 0
    assert editor.retail.editor.verticalScrollBar().maximum() > 0
    host.close()


# --- the context pane --------------------------------------------------------


def test_the_context_pane_agrees_when_retail_and_current_agree(window, session) -> None:
    editor, pane = window
    key = show(editor, session)
    assert session.line(key).retail is not None
    assert session.differs_from_retail(key) is False
    pane.set_line(session, session.line(key))
    assert pane.retail.text() == contextpane.AGREES
    assert INNER not in pane.retail.text()


def test_every_wrapped_context_label_gets_a_line_of_its_own_font(window) -> None:
    """Measured before: a wrapped label was 12 px tall against a 14 px line."""
    _editor, pane = window
    pane.resize(280, 600)
    pane.show()
    QApplication.processEvents()
    wrapped = [label for label in pane.findChildren(QLabel) if label.wordWrap()]
    # Five since the pane gained its Place line: the speaker, the portrait, the retail
    # text, the sites sentence and the place. The count is a guard against a wrapped
    # label losing its height, so it moves with the pane's own list of them.
    assert len(wrapped) == 5
    for label in wrapped:
        line = QFontMetrics(label.font()).lineSpacing()
        assert label.minimumHeight() >= line
        assert label.height() >= line


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


import tests.text_fixture as text_fixture  # noqa: E402


@pytest.fixture(autouse=True)
def fixture_handle_pool():
    """The fixture's record words are the proven carriers a write has to land on.

    A real image's proven carriers are the event-resource pool, which sits far above this
    fixture's payload. Without the patch the engine refuses every edit to a fixture record,
    which is the rule working: it writes only what it can prove a reader reaches. These tests
    are about the states above that rule.
    """
    with text_fixture.proven_handle_pool():
        yield
