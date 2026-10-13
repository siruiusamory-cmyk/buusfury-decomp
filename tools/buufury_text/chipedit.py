"""The editor: RETAIL, CURRENT and NEW over one line, the meter and the move notice.

The three sections are the same widget with the same frame, padding and label
style, because a read-only section must not read as a lesser one. RETAIL and
CURRENT differ from NEW in exactly two ways: they refuse every edit and take no
caret, and NEW carries one weight step on its label plus the accent hairline
above its frame. Nothing else in the editor competes for attention.

Every number here comes from `session.py`: the meter, the covering records, the
site count and the refusal reason. This module computes no ROM value.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QFontMetrics, QPainter, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import chips
from . import theme as theme_module
from .session import State

RETAIL = "RETAIL"
CURRENT = "CURRENT"
NEW = "NEW"

RETAIL_EXPLANATION = "original game, read-only"
CURRENT_EXPLANATION = "loaded ROM, read-only"
NEW_EXPLANATION = "editable"

#: The section-level word that carries the same fact as the run's underline, so the
#: mark is never colour alone.
CHANGED = "changed"
NO_RETAIL = "no retail reference loaded"
NO_EDIT = "no pending edit"
UNSTATED = "unstated"
CHARS = "chars"
BYTES = "bytes"
OVER = "over the limit"
AT_LIMIT = "at the limit"

MOVE_HEADLINE = "This edit will move to appended space"
HIDE_DETAILS = "Hide details"
SHOW_DETAILS = "Show details"
SELECT_RECORDS = "Select covering records"
#: The target an unproven line still edits, stated where the edit is made.
UNPROVEN_TARGET = "Its edit target is unproven: no proven handle site reaches this line."

#: One accent hairline above NEW, and one 1 px control border around every section.
HAIRLINE = "border-top: 1px solid %s;"
INK = "color: %s;"
#: The most lines of the prose role a read-only reference may take, and the least.
#: The cap follows the editor's own height: at the window minimum a fixed four lines
#: never bound, because the three sections split the height evenly, and NEW, the
#: surface the reader types into, was left a 53 px viewport (measured, retail 79 /
#: current 78 / new 79 at 1018x444). A reference may take a sixth of the editor's
#: height instead, which is two lines there and four once the window is tall. The
#: labels, the frames and the explanations stay identical; only the height differs.
READ_ONLY_LINES = 4
MIN_READ_ONLY_LINES = 2
READ_ONLY_SHARE = 6


def _token(theme, role: str) -> str:
    """One theme token by name, in the form a stylesheet needs it."""
    return getattr(theme, role)


def _frame_rule(widget: QWidget, theme) -> str:
    """One 1 px control border, scoped to `widget` alone.

    A stylesheet set on a widget is applied to it AND to its children, so a bare
    `border` rule also boxed every caption and every button inside the frame.
    """
    return f"#{widget.objectName()} {{ border: 1px solid {_token(theme, 'border')}; }}"


def _chrome(editor) -> int:
    """The box's own document margin and frame, which any cap has to carry too."""
    return 2 * int(editor.document().documentMargin()) + 2 * editor.frameWidth()


def read_only_lines(editor, pane_height: int | None = None) -> int:
    """How many lines of this editor's font a read-only reference may take.

    Without a height the whole cap is allowed, which is what a caller measuring one
    box on its own wants. With the editor's own height the reference gives way to
    NEW: a sixth of the pane, floored at two lines and capped at four.
    """
    if pane_height is None:
        return READ_ONLY_LINES
    per_line = QFontMetrics(editor.font()).lineSpacing() + _chrome(editor)
    return max(MIN_READ_ONLY_LINES, min(READ_ONLY_LINES,
                                        pane_height // (READ_ONLY_SHARE * per_line)))


def read_only_cap(editor, pane_height: int | None = None) -> int:
    """The capped text box, in the editor's own font, for an editor `pane_height` tall."""
    line = QFontMetrics(editor.font()).lineSpacing()
    return read_only_lines(editor, pane_height) * line + _chrome(editor)


def changed_run(held: str, pending: str) -> tuple[int, int] | None:
    """The run of `pending` that `held` does not already say, or None when they agree.

    A common prefix and a common suffix leave the changed run between them, which is
    all the mark needs: the reader sees where the wording moved.
    """
    if held == pending:
        return None
    start = 0
    shared = min(len(held), len(pending))
    while start < shared and held[start] == pending[start]:
        start += 1
    tail_held, tail_pending = len(held), len(pending)
    while tail_held > start and tail_pending > start \
            and held[tail_held - 1] == pending[tail_pending - 1]:
        tail_held -= 1
        tail_pending -= 1
    return start, tail_pending - start


def marked_ranges(text: str, run: tuple[int, int] | None) -> tuple[tuple[int, int], ...]:
    """The document ranges a canonical run covers, with every control atom left out.

    A control unit already carries its own chip, and its canonical characters are one
    document character, so a run that reaches one is split around it rather than
    underlined.
    """
    if run is None:
        return ()
    start, length = run
    atoms = {chips.document_index(text, at) for at, _end in chips.atom_ranges(text)}
    runs: list[list[int]] = []
    for at in range(chips.document_index(text, start),
                    chips.document_index(text, start + length)):
        if at in atoms:
            continue
        if runs and runs[-1][1] == at:
            runs[-1][1] = at + 1
        else:
            runs.append([at, at + 1])
    return tuple((first, last) for first, last in runs)


class Section:
    """One editor section: its label, its explanation, its frame and its text."""

    def __init__(self, owner: QWidget, name: str, explanation: str, editable: bool,
                 theme, metrics, emphasised: bool = False) -> None:
        self.name = name
        self.frame = QFrame(owner)
        self.frame.setObjectName(f"section{name}")
        self.frame.setStyleSheet(_frame_rule(self.frame, theme))
        self.label = QLabel(name, self.frame)
        self.label.setProperty("role", "sectionLabel")
        self.label.setFont(theme_module.type_scale().label)
        # The one accent hairline in the editor sits above NEW and nowhere else.
        self.label.setStyleSheet(HAIRLINE % _token(theme, "accent") if emphasised else "")
        self.explanation = QLabel(explanation, self.frame)
        self.explanation.setProperty("role", "caption")
        self.explanation.setFont(theme_module.type_scale().caption)
        self.word = QLabel("", self.frame)
        self.word.setProperty("role", "caption")
        self.word.setFont(theme_module.type_scale().caption)
        self.word.setStyleSheet(INK % _token(theme, "accent"))
        self.word.setVisible(False)
        self.editor = chips.ChipTextEdit(self.frame, editable=editable)
        self.editor.setFont(theme_module.type_scale().prose)
        # The changed run's own channel: the accent underline. Qt draws an underline at
        # the font's own thickness and exposes no width, so this is thinner than the
        # design note's 2 px. Painting the text by hand is the upgrade if that matters.
        self.changed_ink = QTextCharFormat()
        self.changed_ink.setFontUnderline(True)
        self.changed_ink.setUnderlineColor(theme_module.color(theme, "accent"))
        self._cap: int | None = None
        if not editable:
            # Selectable by mouse and by keyboard, never editable. A keyboard-only
            # reader has to be able to reach, read and copy the part of a long line
            # the cap hides, and the caret still belongs to NEW: cursorWidth stays 0,
            # so a focused reference shows no blinking cursor on static text.
            self.editor.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
                | Qt.TextInteractionFlag.TextSelectableByKeyboard)
            self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.editor.setCursorWidth(0)
        head = QHBoxLayout()
        head.setContentsMargins(metrics.pad_md, metrics.pad_sm, metrics.pad_md, 0)
        head.setSpacing(metrics.pad_md)
        head.addWidget(self.label)
        head.addWidget(self.explanation)
        head.addStretch(1)
        head.addWidget(self.word)
        body = QVBoxLayout(self.frame)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(metrics.pad_xs)
        body.addLayout(head)
        body.addWidget(self.editor, 1)
        self.head = head
        self.body = body

    def set_text(self, text: str) -> None:
        self.editor.set_text(text)

    def mark_changed(self, held: str) -> None:
        """Underline the run of this section's text that `held` does not already say.

        An extra selection paints over the document and never edits it, so the
        canonical text the editor reports stays exactly what the writer typed. The
        design note gives the changed run two channels, this and the section word,
        so the mark is never colour alone.
        """
        text = self.editor.serialized()
        marks = []
        for first, last in marked_ranges(text, changed_run(held, text)):
            cursor = QTextCursor(self.editor.document())
            cursor.setPosition(first)
            cursor.setPosition(last, QTextCursor.MoveMode.KeepAnchor)
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = self.changed_ink
            marks.append(selection)
        self.editor.setExtraSelections(marks)

    def cap_text_height(self, height: int) -> None:
        """At most `height` px of text here, whatever the column offers.

        The frame is capped as well as the text box: capping the box alone left the
        frame stretched to its old share with the freed space dead inside it. The
        cap follows the editor's own height and is re-applied on every resize, so
        the same height arrives more than once and setting it again is a no-op.
        """
        if height == self._cap:
            return
        self._cap = height
        self.editor.setMaximumHeight(height)
        self.frame.setMaximumHeight(height + self.head.sizeHint().height()
                                    + self.body.spacing())


class BarTrack(QWidget):
    """The discrete segments and the in-place threshold tick, drawn by the theme."""

    def __init__(self, theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._value = 0
        self._limit: int | None = None
        self._over = False
        self.setFixedHeight(metrics.segment_height + 4)

    def show_measure(self, value: int, limit: int | None, over: bool) -> None:
        self._value, self._limit, self._over = value, limit, over
        self.update()

    def scale(self) -> int:
        """The denominator: whichever is larger, so a value past the limit shows."""
        return max(self._value, self._limit or 0, 1)

    def tick_x(self, width: int) -> int | None:
        """Where the in-place threshold sits, or None when the engine stated none."""
        if self._limit is None:
            return None
        return round(width * self._limit / self.scale())

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        rect = QRect(0, 0, self.width(), self.height())
        total = self._value if self._limit is None else self._limit
        theme_module.paint_segments(painter, rect, total, self._value, self._theme,
                                    accent=self._over or self._at_limit(),
                                    over=self._over)
        tick = self.tick_x(self.width())
        if tick is not None:
            painter.setPen(theme_module.color(self._theme, "text_secondary"))
            painter.drawLine(min(tick, self.width() - 1), 0,
                             min(tick, self.width() - 1), self.height() - 1)

    def _at_limit(self) -> bool:
        return self._limit is not None and self._value == self._limit


class SegmentBar(QWidget):
    """One unit of the meter: its unit label, a tabular readout, and its segments."""

    def __init__(self, unit: str, theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.unit = unit
        self._theme = theme
        # The static unit label keeps the two readouts apart: each readout states its
        # own unit in every state, the empty one included, where the number is 0.
        self.unit_label = QLabel(unit, self)
        self.unit_label.setProperty("role", "caption")
        self.unit_label.setFont(theme_module.type_scale().caption)
        self.readout = QLabel("", self)
        self.readout.setFont(theme_module.type_scale().data)
        self.readout.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.track = BarTrack(theme, metrics, self)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(metrics.pad_xs)
        column.addWidget(self.unit_label)
        column.addWidget(self.readout)
        column.addWidget(self.track)
        self.show_measure(0, None)
        self.setFixedHeight(self.unit_label.sizeHint().height()
                            + self.readout.sizeHint().height() + 2 * metrics.pad_xs
                            + self.track.height())

    def show_measure(self, value: int, limit: int | None) -> None:
        over = limit is not None and value > limit
        self.readout.setText(
            f"{value} / {limit} {self.unit}" if limit is not None
            else f"{value} {self.unit}, {UNSTATED} {self.unit} limit")
        self.readout.setStyleSheet(
            INK % _token(self._theme, "accent")
            if limit is not None and value >= limit else "")
        self.track.show_measure(value, limit, over)

    def text(self) -> str:
        return self.readout.text()


class LengthMeter(QWidget):
    """Both units, one aligned bar each, and the engine's refusal reason below."""

    def __init__(self, theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.chars = SegmentBar(CHARS, theme, metrics, self)
        self.bytes = SegmentBar(BYTES, theme, metrics, self)
        self.word = QLabel("", self)
        self.word.setProperty("role", "caption")
        self.word.setFont(theme_module.type_scale().caption)
        self.word.setVisible(False)
        self.reason = QLabel("", self)
        self.reason.setWordWrap(True)
        self.reason.setFont(theme_module.type_scale().caption)
        self.reason.setStyleSheet(INK % _token(theme, "text_secondary"))
        self.reason.setVisible(False)
        bars = QHBoxLayout()
        bars.setContentsMargins(metrics.pad_md, 0, metrics.pad_md, 0)
        bars.setSpacing(metrics.pad_lg)
        bars.addWidget(self.chars, 1)
        bars.addWidget(self.bytes, 1)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(metrics.pad_xs)
        column.addWidget(self.word)
        column.addLayout(bars)
        column.addWidget(self.reason)
        # The meter opens in its empty state, stated the one way, so a window with no
        # row shown reads the same as a row with nothing pending.
        self.show_meter(None)

    def show_meter(self, meter, word: str = "") -> None:
        """`meter` is the session's own answer; None means there is no pending edit.

        The empty state still carries a number for both units, because the design
        note pairs the segmented bar with a numeric readout and the reader needs the
        budget before typing. Zero is the pending edit's own size; a limit the
        engine did not state stays said in words rather than invented. The words
        `no pending edit` are then stated once, as the meter's own state word,
        instead of twice with no number at all.
        """
        empty = meter is None
        self.chars.show_measure(0 if empty else meter.chars,
                                None if empty else meter.chars_limit)
        self.bytes.show_measure(0 if empty else meter.bytes,
                                None if empty else meter.bytes_limit)
        self.word.setText(word or (NO_EDIT if empty else ""))
        self.word.setVisible(bool(self.word.text()))

    def show_reason(self, reason: str) -> None:
        self.reason.setText(reason)
        self.reason.setVisible(bool(reason))

    def reason_shown(self) -> bool:
        """Whether the engine's refusal reason is disclosed under the meter."""
        return self.reason.isVisibleTo(self)

    def word_shown(self) -> bool:
        return self.word.isVisibleTo(self)

    def text(self) -> str:
        return "     ".join((self.chars.text(), self.bytes.text()))

    def stated(self) -> bool:
        """Whether the engine stated a span, so a threshold tick means something."""
        return self.chars.track.tick_x(100) is not None or \
            self.bytes.track.tick_x(100) is not None


class MoveNotice(QFrame):
    """A persistent inline disclosure. It collapses, and it never expires."""

    records_requested = Signal(tuple)

    def __init__(self, theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._covering: tuple[str, ...] = ()
        self.setObjectName("moveNotice")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(_frame_rule(self, theme))
        self.headline = QLabel(MOVE_HEADLINE, self)
        self.headline.setWordWrap(True)
        self.headline.setFont(theme_module.type_scale().body)
        self.detail = QLabel("", self)
        self.detail.setWordWrap(True)
        self.detail.setProperty("role", "caption")
        self.detail.setFont(theme_module.type_scale().caption)
        self.select_button = QToolButton(self)
        self.select_button.setText(SELECT_RECORDS)
        self.select_button.setAutoRaise(True)
        self.select_button.clicked.connect(
            lambda: self.records_requested.emit(tuple(self._covering)))
        self.collapse_button = QToolButton(self)
        self.collapse_button.setText(HIDE_DETAILS)
        self.collapse_button.setAutoRaise(True)
        self.collapse_button.setCheckable(True)
        self.collapse_button.toggled.connect(self._collapsed)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(metrics.pad_md)
        buttons.addWidget(self.collapse_button)
        buttons.addWidget(self.select_button)
        buttons.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(metrics.pad_md, metrics.pad_sm, metrics.pad_md,
                                  metrics.pad_sm)
        column.setSpacing(metrics.pad_xs)
        column.addWidget(self.headline)
        column.addWidget(self.detail)
        column.addLayout(buttons)

    def _collapsed(self, hidden: bool) -> None:
        self.detail.setVisible(not hidden)
        self.collapse_button.setText(SHOW_DETAILS if hidden else HIDE_DETAILS)

    def detail_shown(self) -> bool:
        return self.detail.isVisibleTo(self)

    def show_notice(self, covering: tuple[str, ...], sites: int, visible: bool,
                    proven: bool) -> None:
        self._covering = tuple(covering)
        self.setVisible(visible)
        if not visible:
            return
        self.detail.setText(self._detail(covering, sites, proven))
        self.select_button.setEnabled(bool(covering))
        self.detail.setVisible(not self.collapse_button.isChecked())

    @staticmethod
    def _detail(covering: tuple[str, ...], sites: int, proven: bool) -> str:
        names = ", ".join(covering) if covering else "no other record"
        sites_word = "handle site" if sites == 1 else "handle sites"
        second = (f"It is named by {sites} {sites_word}, and the original bytes are "
                  f"also referenced by {names}.")
        return second if proven else f"{second} {UNPROVEN_TARGET}"


class EditorSections(QWidget):
    """RETAIL, CURRENT and NEW over one line, then the meter and the move notice."""

    committed = Signal(str, str)
    #: NEW refused an edit, so the shell can say why in its own status bar.
    refused = Signal(str)

    def __init__(self, theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._metrics = metrics
        self._key = ""
        self.retail = Section(self, RETAIL, RETAIL_EXPLANATION, False, theme, metrics)
        self.current = Section(self, CURRENT, CURRENT_EXPLANATION, False, theme, metrics)
        self.new = Section(self, NEW, NEW_EXPLANATION, True, theme, metrics,
                           emphasised=True)
        # The two references are one short paragraph each, so they are capped and
        # NEW takes the stretch; the frame, label and explanation stay identical.
        for section in (self.retail, self.current):
            section.cap_text_height(read_only_cap(section.editor))
        self.meter = LengthMeter(theme, metrics, self)
        self.notice = MoveNotice(theme, metrics, self)
        # A hidden notice keeps its slot, so the editor does not jump when it shows.
        self.notice.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.notice.hide()
        self.new.editor.edited.connect(self._edited)
        self.new.editor.refused.connect(self.refused.emit)
        column = QVBoxLayout(self)
        column.setContentsMargins(metrics.pad_lg, metrics.pad_md, metrics.pad_lg,
                                  metrics.pad_md)
        column.setSpacing(metrics.pad_sm)
        for section in (self.retail, self.current):
            column.addWidget(section.label)
            column.addWidget(section.frame, 1)
        column.addWidget(self.new.label)
        column.addWidget(self.new.frame, 1)
        column.addWidget(self.meter)
        column.addWidget(self.notice)
        self._cap_references()

    def resizeEvent(self, event) -> None:  # noqa: N802
        """Re-apply the references' cap, so it holds at every height the pane takes."""
        super().resizeEvent(event)
        self._cap_references()

    def _cap_references(self) -> None:
        for section in (self.retail, self.current):
            section.cap_text_height(read_only_cap(section.editor, self.height()))

    # --- the shell's API -----------------------------------------------------

    def set_line(self, line, state: State = State.UNCHANGED, meter=None,
                 differs: bool = False, decision_reason: str = "", covering=(),
                 sites: int = 0, proven: bool = True) -> None:
        """Show one row. Everything shown here is the session's own answer."""
        self._key = "" if line is None else line.key
        self.retail.set_text("" if line is None else (line.retail or NO_RETAIL))
        self.current.set_text("" if line is None else line.text)
        self.new.set_text("" if line is None else line.text)
        self.new.word.setText(CHANGED if line is not None and differs else "")
        self.new.word.setVisible(bool(line is not None and differs))
        self.set_state(state, meter, differs, decision_reason)
        self.notice.show_notice(tuple(covering), sites, bool(covering), proven)
        self._mark_changed()

    def set_state(self, state: State, meter=None, differs: bool = False,
                  decision_reason: str = "") -> None:
        """The meter, the engine's own words for a refusal, and the changed word."""
        self.meter.show_meter(meter, self._state_word(state, meter))
        self.meter.show_reason(decision_reason if state is State.REFUSED else "")
        self.new.word.setText(CHANGED if differs else "")
        self.new.word.setVisible(bool(differs))

    def set_pending(self, text: str) -> None:
        """Show what the project will make this row say, without stealing typing."""
        if self.new.editor.serialized() != text and not self.has_focus():
            self.new.set_text(text)
        self._mark_changed()

    def focus_new(self) -> None:
        self.new.editor.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def new_text(self) -> str:
        return self.new.editor.serialized()

    def notice_shown(self) -> bool:
        """Whether the move notice is disclosed, whatever the window's own state."""
        return self.notice.isVisibleTo(self.notice.parentWidget()) or \
            self.notice.isVisible()

    def has_focus(self) -> bool:
        """Whether NEW carries the caret, rather than any child of the editor."""
        return self.new.editor.hasFocus()

    def commit(self) -> None:
        """Send NEW's text for the current row, as typing in it would."""
        if self._key:
            self.committed.emit(self._key, self.new_text())

    # --- internals -----------------------------------------------------------

    def _edited(self, text: str) -> None:
        self._mark_changed()
        if self._key:
            self.committed.emit(self._key, text)

    def _mark_changed(self) -> None:
        """Mark NEW's changed run against what CURRENT holds, which is the image.

        The mark follows the three ways NEW's text arrives: the row the shell shows,
        the pending text it refreshes with, and what the writer types here.
        """
        self.new.mark_changed(self.current.editor.serialized())

    @staticmethod
    def _state_word(state: State, meter) -> str:
        if state is State.WILL_MOVE:
            return MOVE_HEADLINE
        if meter is None:
            return ""
        pairs = ((meter.chars, meter.chars_limit), (meter.bytes, meter.bytes_limit))
        if any(limit is not None and value > limit for value, limit in pairs):
            return OVER
        if any(limit is not None and value == limit for value, limit in pairs):
            return AT_LIMIT
        return ""
