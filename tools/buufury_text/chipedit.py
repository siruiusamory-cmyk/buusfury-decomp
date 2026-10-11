"""The three editor sections, the length meter and the move notice.

RETAIL and CURRENT are the same read-only renderer, so reference text and
editable text cannot disagree visually. The meter and the notice read the
engine's own answer through the session; nothing here computes a ROM value.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QPainter, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import chips, status as status_words, theme
from .session import State

#: The spec's prose size. Monospace belongs to chip internals and to numbers.
PROSE_POINT_SIZE = 10

RETAIL_EXPLANATION = "original game, read-only"
CURRENT_EXPLANATION = "loaded ROM, read-only"
NEW_EXPLANATION = "editable"
NO_RETAIL = "no retail reference loaded"
NO_EDIT = "no pending edit"
UNSTATED = "limit unstated"
MOVE_HEADLINE = "This edit will move to appended space"
HIDE_DETAILS = "Hide details"
SHOW_DETAILS = "Show details"
#: The target an unproven line still edits, stated where the edit is made.
UNPROVEN_TARGET = "Its edit target is unproven: no proven handle site reaches this line."


class SectionHeader(QWidget):
    """One section's name and its secondary explanation, on a fixed header line."""

    def __init__(self, name: str, explanation: str, height: int,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.name = QLabel(name)
        self.explanation = QLabel(explanation)
        font = QFont(self.name.font())
        font.setBold(True)
        self.name.setFont(font)
        self.explanation.setEnabled(False)
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 0, 2, 0)
        row.setSpacing(8)
        row.addWidget(self.name)
        row.addWidget(self.explanation)
        row.addStretch(1)
        self.setFixedHeight(height)


class ThresholdBar(QWidget):
    """One unit's fill, and a one-pixel tick at the in-place limit.

    The bar is scaled by whichever is larger, the value or the limit, so a value
    past the limit is visible as a bar that crosses the tick.
    """

    HEIGHT = 4

    def __init__(self, parent: QWidget | None = None, theme_=None) -> None:
        super().__init__(parent)
        self._theme = theme_
        self._value = 0
        self._limit: int | None = None
        self.setFixedHeight(self.HEIGHT)

    def set_measure(self, value: int, limit: int | None) -> None:
        self._value, self._limit = value, limit
        self.update()

    def tick_at(self, width: int) -> int | None:
        """Where the in-place limit sits in a bar of ``width``, or None when unstated."""
        if self._limit is None:
            return None
        scale = max(self._value, self._limit, 1)
        return round(width * self._limit / scale)

    def fill_width(self, width: int) -> int:
        if self._limit is None:
            return 0
        scale = max(self._value, self._limit, 1)
        return min(width, round(width * self._value / scale))

    def paintEvent(self, _event) -> None:
        if self._theme is None:
            return
        painter = QPainter(self)
        painter.fillRect(self.rect(), theme.color(self._theme, "surface_raised"))
        painter.setPen(theme.color(self._theme, "border"))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        fill = self.fill_width(self.width() - 2)
        if fill:
            painter.fillRect(1, 1, fill, self.HEIGHT - 2, theme.color(self._theme, "accent"))
        tick = self.tick_at(self.width() - 2)
        if tick is not None:
            painter.fillRect(1 + tick, 0, 1, self.HEIGHT, theme.color(self._theme, "text_primary"))


class StateBadge(QWidget):
    """The semantic result of the meter: an icon and the full words."""

    def __init__(self, theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_
        self.icon_label = QLabel()
        self.word_label = QLabel()
        row = QHBoxLayout(self)
        row.setContentsMargins(6, 1, 6, 1)
        row.setSpacing(4)
        row.addWidget(self.icon_label)
        row.addWidget(self.word_label)
        self.setAutoFillBackground(True)

    def show_state(self, state: State, icon: str, word: str) -> None:
        fill, ink = theme.state_colors(self._theme, state)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, fill)
        palette.setColor(QPalette.ColorRole.WindowText, ink)
        self.setPalette(palette)
        self.icon_label.setPixmap(theme.icon(icon).pixmap(16, 16))
        self.word_label.setText(word)


class LengthMeter(QWidget):
    """Both units, two labelled bars, and the state badge on the same header line."""

    def __init__(self, theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_
        self.numbers = QLabel()
        self._stated = False
        self.numbers.setFont(theme.mono_font())
        self.badge = StateBadge(theme_, self)
        self.reason = QLabel()
        self.reason.setWordWrap(True)
        self.reason.setVisible(False)
        self.char_label = QLabel("Chars")
        self.byte_label = QLabel("Bytes")
        for label in (self.char_label, self.byte_label):
            label.setFont(theme.mono_font())
        self.chars_bar = ThresholdBar(theme_=theme_)
        self.bytes_bar = ThresholdBar(theme_=theme_)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        header.addWidget(self.numbers)
        header.addStretch(1)
        header.addWidget(self.badge)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(2)
        column.addLayout(header)
        column.addLayout(self._bar_row(self.char_label, self.chars_bar))
        column.addLayout(self._bar_row(self.byte_label, self.bytes_bar))
        column.addWidget(self.reason)

    @staticmethod
    def _bar_row(label: QLabel, track: ThresholdBar) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(label)
        row.addWidget(track, 1)
        return row

    def text(self) -> str:
        return self.numbers.text()

    def stated(self) -> bool:
        """Whether the engine stated a span, so a tick and a fill mean something."""
        return self._stated

    def show_meter(self, session, key: str) -> None:
        meter = None if session is None or key == "" else session.meter(key)
        decision = None if session is None or key == "" else session.decision(key)
        state = State.UNCHANGED if session is None or key == "" else session.state(key)
        if meter is None:
            self._stated = False
            self.numbers.setText(NO_EDIT)
            self.chars_bar.set_measure(0, None)
            self.bytes_bar.set_measure(0, None)
            self.badge.setVisible(False)
            self.reason.setVisible(False)
            return
        self._stated = meter.chars_limit is not None and meter.bytes_limit is not None
        self.numbers.setText(self._numbers(meter))
        self.chars_bar.set_measure(meter.chars, meter.chars_limit)
        self.bytes_bar.set_measure(meter.bytes, meter.bytes_limit)
        self._show_result(state, decision, meter)

    @staticmethod
    def _numbers(meter) -> str:
        characters = f"{meter.chars} / {meter.chars_limit} chars" if meter.chars_limit is not None \
            else f"{meter.chars} chars"
        size = f"{meter.bytes} / {meter.bytes_limit} bytes" if meter.bytes_limit is not None \
            else f"{meter.bytes} bytes"
        unstated = "" if meter.chars_limit is not None and meter.bytes_limit is not None \
            else f"     {UNSTATED}"
        return f"{characters}     {size}{unstated}"

    def _show_result(self, state: State, decision, _meter) -> None:
        if state is State.REFUSED:
            entry = status_words.presentation(State.REFUSED)
            self.badge.show_state(State.REFUSED, entry.icon, entry.word)
        elif state is State.WILL_MOVE:
            entry = status_words.presentation(State.WILL_MOVE)
            self.badge.show_state(State.WILL_MOVE, entry.icon, entry.word)
        elif decision is None:
            self.badge.setVisible(False)
            self.reason.setVisible(False)
            return
        else:
            self.badge.show_state(State.EDITED, "check", "FITS IN PLACE")
        self.badge.setVisible(True)
        reason = "" if decision is None or state is not State.REFUSED else decision.reason
        self.reason.setText(reason)
        self.reason.setVisible(bool(reason))


class MoveNotice(QFrame):
    """A persistent inline disclosure under the meter. It collapses, never expires."""

    records_requested = Signal(tuple)

    def __init__(self, theme_, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, theme.color(theme_, "surface_raised"))
        self.setPalette(palette)
        self.headline = QLabel(MOVE_HEADLINE)
        self.detail = QLabel()
        self.detail.setWordWrap(True)
        self.select_button = QToolButton()
        self.select_button.setText("Select covering records")
        self.select_button.clicked.connect(
            lambda: self.records_requested.emit(tuple(self._covering)))
        self.collapse_button = QToolButton()
        self.collapse_button.setText(HIDE_DETAILS)
        self.collapse_button.setCheckable(True)
        self.collapse_button.toggled.connect(self._collapsed)
        self._covering: tuple[str, ...] = ()
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self.select_button)
        row.addWidget(self.collapse_button)
        row.addStretch(1)
        column = QVBoxLayout(self)
        column.setContentsMargins(8, 6, 8, 6)
        column.setSpacing(4)
        column.addWidget(self.headline)
        column.addWidget(self.detail)
        column.addLayout(row)

    def _collapsed(self, hidden: bool) -> None:
        self.detail.setVisible(not hidden)
        self.collapse_button.setText(SHOW_DETAILS if hidden else HIDE_DETAILS)

    def show_notice(self, covering: tuple[str, ...], sites: int, visible: bool,
                    proven: bool = True) -> None:
        self._covering = covering
        self.setVisible(visible)
        if not visible:
            return
        names = ", ".join(covering) if covering else "no other record"
        detail = (f"Original bytes are also referenced by {names}. "
                  f"{sites} handle site(s) name this line in the image.")
        if not proven:
            detail = f"{detail} {UNPROVEN_TARGET}"
        self.detail.setText(detail)
        self.select_button.setEnabled(bool(covering))
        self.detail.setVisible(not self.collapse_button.isChecked())


def prose_font() -> QFont:
    """The 10 pt proportional face the three editor surfaces share."""
    font = QFont(QApplication.font())
    font.setPointSize(PROSE_POINT_SIZE)
    return font


class EditorSections(QWidget):
    """RETAIL, CURRENT and NEW over one line, with the meter and the move notice."""

    edited = Signal(str)

    def __init__(self, theme_, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_
        self._metrics = metrics
        self._key = ""
        self.retail_header = SectionHeader("RETAIL", RETAIL_EXPLANATION, metrics.header_height)
        self.current_header = SectionHeader("CURRENT", CURRENT_EXPLANATION, metrics.header_height)
        self.new_header = SectionHeader("NEW", NEW_EXPLANATION, metrics.header_height)
        self.retail = self._surface(read_only=True)
        self.current = self._surface(read_only=True)
        self.new = self._surface(read_only=False)
        self.new.edited.connect(self.edited)
        self.meter = LengthMeter(theme_, self)
        self.notice = MoveNotice(theme_, self)
        column = QVBoxLayout(self)
        column.setContentsMargins(10, 8, 10, 8)
        column.setSpacing(6)
        column.addWidget(self.retail_header)
        column.addWidget(self.retail, 3)
        column.addWidget(self.current_header)
        column.addWidget(self.current, 3)
        column.addWidget(self.new_header)
        column.addWidget(self.new, 4)
        column.addWidget(self.meter)
        column.addWidget(self.notice)

    def _surface(self, read_only: bool) -> chips.ChipTextEdit:
        editor = chips.ChipTextEdit(self)
        editor.setReadOnly(read_only)
        editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        editor.setFont(prose_font())
        editor.setFrameShape(QFrame.Shape.StyledPanel)
        return editor

    def show_line(self, session, key: str, text: str, keep_editor: bool = False) -> None:
        """Show one line. The editor is only rewritten when the selection moved."""
        moved = key != self._key
        self._key = key
        line = None if session is None or key == "" else session.line(key)
        if line is None:
            self.retail.set_text("")
        elif line.retail is None:
            self.retail.set_text(NO_RETAIL)
        else:
            self.retail.set_text(line.retail)
        self.current.set_text("" if line is None else line.text)
        if moved or not keep_editor:
            self.new.set_text(text)
        self.meter.show_meter(session, key)
        state = State.UNCHANGED if line is None else session.state(key)
        self.notice.show_notice(() if line is None else session.covering(key),
                                0 if line is None else session.sites(key),
                                state is State.WILL_MOVE,
                                True if line is None else line.proven)
