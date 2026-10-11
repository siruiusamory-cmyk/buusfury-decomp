"""What the dialogue box will look like, approximately, at integer scale.

This is the one surface the interface is allowed to look like a Game Boy Advance.
The glyph source is the seam the RE Lab's extracted font implements; until it
lands the source is `ApproximateGlyphs`, the caption says so, and the caption is
never hidden. All wrapping and pagination is a module function so a test asserts
it without painting.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from tools.webfoot import textedit

from . import theme

#: The dialogue box's own colours live in the theme's token table, because a second
#: place carrying a colour would be a second theme. They are the same in both modes
#: on purpose: this surface shows the game, not the application.
CAPTION = "Approximate preview"
#: One neutral marker stands in for every control unit whose glyph is not available.
CHARACTER = "\ufffc"

_MARGIN = 8
_BOX_PAD = 4
_NEWLINE = 0x0A


def box_color(role: str) -> QColor:
    """One of the preview's four tokens, resolved against the active theme."""
    return theme.color(theme.active_theme(), role)


@runtime_checkable
class GlyphSource(Protocol):
    """The seam the RE Lab's extracted font will implement."""

    @property
    def line_height(self) -> int: ...

    @property
    def lines_per_page(self) -> int: ...

    @property
    def box_width(self) -> int: ...

    def advance(self, character: str) -> int: ...

    def draw(self, painter: QPainter, character: str, x: int, y: int) -> None: ...


class ApproximateGlyphs:
    """The v1 source: one system monospace cell per character, labelled approximate."""

    name = "system monospace (approximate)"

    def __init__(self, font=None, box_width: int = 176, lines_per_page: int = 2) -> None:
        self._font = font if font is not None else theme.mono_font(delta=4)
        self._cell = max(1, self._font.pointSize())
        self._box_width = box_width
        self._lines = lines_per_page

    @property
    def line_height(self) -> int:
        return self._cell

    @property
    def lines_per_page(self) -> int:
        return self._lines

    @property
    def box_width(self) -> int:
        return self._box_width

    def advance(self, character: str) -> int:
        return self._cell

    def draw(self, painter: QPainter, character: str, x: int, y: int) -> None:
        """One cell, drawn on the integer grid so nearest-neighbour stays sharp."""
        painter.setFont(self._font)
        painter.setPen(box_color("preview_marker") if character == CHARACTER else box_color("preview_ink"))
        painter.drawText(QRect(x, y, self._cell, self._cell),
                         Qt.AlignmentFlag.AlignCenter, character)


def layout(text: str, source: GlyphSource) -> tuple[tuple[str, ...], ...]:
    """Pages of lines: wrap on the source's advances, break pages at its page size."""
    filled: list[str] = []
    line = ""
    width = 0
    for unit in textedit.units(text):
        run = unit.raw if isinstance(unit, textedit.Control) else unit.value
        for character in run:
            if character == "\n":
                filled.append(line)
                line, width = "", 0
                continue
            cell = source.advance(character)
            if line and width + cell > source.box_width:
                filled.append(line)
                line, width = "", 0
            line += character
            width += cell
    filled.append(line)
    page_size = max(1, source.lines_per_page)
    return tuple(tuple(filled[at:at + page_size]) for at in range(0, len(filled), page_size))


class DialoguePreview(QWidget):
    """A dark viewport with every page of the dialogue box drawn stacked."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._source: GlyphSource = ApproximateGlyphs()
        self._text = ""
        self.setObjectName("dialoguePreview")
        self.setProperty("role", "viewport")

    def set_text(self, text: str) -> None:
        self._text = text
        self.updateGeometry()
        self.update()

    def set_glyph_source(self, source: GlyphSource) -> None:
        """Swap in the RE Lab's extracted font. The caption follows the source."""
        self._source = source
        self.updateGeometry()
        self.update()

    def glyph_source_name(self) -> str:
        return getattr(self._source, "name", type(self._source).__name__)

    def is_approximate(self) -> bool:
        return isinstance(self._source, ApproximateGlyphs)

    def sizeHint(self) -> QSize:  # noqa: N802
        source = self._source
        page = max(source.line_height, 1) * max(source.lines_per_page, 1)
        return QSize(source.box_width + 2 * _MARGIN,
                     len(layout(self._text, source)) * page + 2 * _MARGIN)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Scale 1 is the floor: below it the preview would stop being readable."""
        source = self._source
        return QSize(source.box_width + 2 * _MARGIN,
                     max(source.line_height, 1) * max(source.lines_per_page, 1) + 2 * _MARGIN)

    def paintEvent(self, event) -> None:  # noqa: N802
        source = self._source
        scale = _integer_scale(source, self.width(), self.height())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.fillRect(self.rect(), box_color("preview_screen"))
        painter.save()
        painter.scale(scale, scale)
        box = QSize(source.box_width + 2 * _BOX_PAD,
                    source.lines_per_page * source.line_height + 2 * _BOX_PAD)
        for page in layout(self._text, source):
            painter.fillRect(QRect(0, 0, box.width(), box.height()), box_color("preview_box"))
            for row, line in enumerate(page):
                x = _BOX_PAD
                for character in line:
                    source.draw(painter, character, x, _BOX_PAD + row * source.line_height)
                    x += source.advance(character)
            painter.translate(0, box.height())
        painter.restore()
        if self.is_approximate():
            painter.setPen(QPen(QColor(theme.active_theme().text_secondary), 1))
            painter.setFont(theme.mono_font())
            painter.drawText(self.rect().adjusted(0, 0, -_MARGIN, -4),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                             f"{CAPTION} \u00b7 {self.glyph_source_name()}")


def _integer_scale(source: GlyphSource, width: int, height: int) -> int:
    """Nearest-neighbour only: an integer scale, never a fractional stretch."""
    if source.box_width <= 0 or source.line_height <= 0:
        return 1
    return max(1, min(4, (width - 2 * _MARGIN) // source.box_width,
                      (height - 2 * _MARGIN) // source.line_height))
