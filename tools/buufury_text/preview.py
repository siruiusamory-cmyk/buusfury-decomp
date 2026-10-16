"""The in-game dialogue preview: the record the engine draws, or one line saying why not.

The pane shows the GAME, so it may not be approximated. Every part of it is decoded at
RUN TIME from the image the reader opened: the font through its descriptor, the box art
through its container, the ink through the object palette. Nothing derived from a game
image is written down here or committed beside it.

The rules, each of them measured from the image bytes or from native 240x160 captures:

* the font is reached through the 12-byte descriptor at file ``0x6EE6C``; the table it
  names holds 256 code-to-record offsets in halfwords, and a record is a width then
  width plus one columns, column k being pixel column k and bit r of a column being
  pixel row r with row 0 at the top;
* the advance is the stored width plus one; a code below ``0x20`` has no record and
  advances one; a code at or above ``0xFF`` takes the fixed advance and draws nothing;
* text origin ``(8, 3)`` in the surface's own coordinates, a 14-pixel line spacing, a
  16-row glyph cell, four lines to the box;
* the surface is the box-art container decoded by the image's own codec: 160 by 64,
  one byte per pixel, stride ``0xA0``, indexed by the object palette at file ``0x5652C``;
* the dialogue path paints index 2, and the ``0x0008`` unit sets the ink and consumes
  its own operand;
* the line fitter is a greedy word wrap against the LIMIT OF THE LAYOUT RECORD the
  record selects (144 or 128), breaking at the last space it saw, so a trailing space
  is never drawn, with ``0x0A`` ending the line and ``0x0B`` the record;
* the layout record is the one the record's own portrait OPERAND selects, and it carries
  BOTH the limit and the art, so the two are never mixed: the box constructor at
  ``0x08012012`` takes index 1 only when the operand is exactly ``7`` (``0x08012104`` to
  ``0x0801210A``) and index 0 otherwise, index ``i`` being ``0x08071720 + 0x10 + 0x14*i``
  (``0x0800B29E``): index 0 is layout ``0x08071730``, limit 144, art container
  ``0x08071758``; index 1 is layout ``0x08071744``, limit 128, art container
  ``0x08071A6C``. Operand 0 means no portrait and still takes index 0.

Three things this pane refuses to do. It does not guess a scroll window: a record whose
wrapped text needs more lines than the box holds is drawn by the engine as a window
into the record, the rule that advances that window is not established, and the case is
reported instead. It does not draw past a ``0x0B`` soft end into text the record keeps
after it: the fitter stops at that unit, the rule that carries the reveal past it is not
established, and the case is reported the same way. And it draws nothing at all while it
cannot render this record - no box, no glyph, no stand-in font - only one line naming
what is missing.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFontMetrics, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget

from tools.webfoot.formats import webfoot_lz

from . import theme

#: File offsets, not addresses: where the descriptor, the palette and the two layout
#: records' art containers sit in the image.
FONT_DESCRIPTOR = 0x6EE6C
OBJ_PALETTE = 0x5652C
ROM_BASE = 0x08000000

#: The two layout records' own limit field, and the art container each one draws. The
#: limit is a field of the record, never a constant of the renderer, and the record
#: carries the art too, so the pair is taken together or not at all.
LAYOUT_LIMITS = (144, 128)
BOX_ART = {144: 0x71758, 128: 0x71A6C}
#: The one portrait operand that selects the SECOND layout record, the 128 one.
SECOND_LAYOUT_OPERAND = 7

#: The surface: 160 by 64 at one byte per pixel, and the length its decoder must yield.
SURFACE_WIDTH = 160
SURFACE_HEIGHT = 64
SURFACE_BYTES = SURFACE_WIDTH * SURFACE_HEIGHT

#: Measured placement and page size.
TEXT_ORIGIN = (8, 3)
LINE_HEIGHT = 14
GLYPH_ROWS = 16
LINES_PER_PAGE = 4

#: Unit values on the dialogue path.
NEWLINE = 0x0A
SOFT_END = 0x0B
TERMINATOR = 0x0000
SPACE = 0x20
INK_ESCAPE = 0x0008
WIDE_CODE = 0xFF

#: The index the dialogue path paints, and the palette's own entry count.
DEFAULT_INK = 2
PALETTE_ENTRIES = 256

#: The one line each state shows, and the name of what keeps it there.
WAITING_IMAGE = "In-game preview: no image is open, so there is nothing to render."
NO_FONT = "In-game preview: the font will not decode from this image."
NO_BOX = "In-game preview: the box art will not decode from this image."
LIMITED = "In-game preview: "
SCROLL_RULE = "the scroll-advance rule"
SOFT_RULE = "the reveal rule after the 0x0B soft end"
NO_DIALOGUE_BOX = "no box is drawn, because this row is a string slot"

_MARGIN = 8
_MAX_SCALE = 4


class DecodeError(ValueError):
    """A refusal: this image does not hold the part the pane needs, and here is why."""


# --- the font, read through its descriptor -----------------------------------


@dataclass(frozen=True, slots=True)
class Glyph:
    """One glyph record: its ink width and one column word per pixel column."""

    width: int
    columns: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Font:
    """The image's dialogue font, with the engine's own lookup rules."""

    image: bytes
    table: int
    wide_advance: int
    offsets: tuple[int, ...]

    def glyph(self, code: int) -> Glyph | None:
        """The glyph for a code, or None where the engine draws nothing."""
        if not 0 <= code < WIDE_CODE or not self.offsets[code]:
            return None
        record = self.table + 2 * self.offsets[code]
        width = int.from_bytes(self.image[record:record + 2], "little")
        columns = tuple(
            int.from_bytes(self.image[record + 2 + 2 * column:record + 4 + 2 * column],
                           "little")
            for column in range(width + 1)
        )
        return Glyph(width, columns)

    def advance(self, code: int) -> int:
        """How far the cursor moves after this code, exactly as the engine computes it."""
        if code >= WIDE_CODE:
            return self.wide_advance + 1
        glyph = self.glyph(code)
        return 1 if glyph is None else glyph.width + 1


def decode_font(image: bytes) -> Font:
    """Read the font through its descriptor, or refuse the whole font.

    Every record the map names is checked against the image here rather than while a
    line is being drawn, so a malformed table is one stated missing part instead of a
    surprise halfway through the record.
    """
    if len(image) < FONT_DESCRIPTOR + 12:
        raise DecodeError("the descriptor is outside the image")
    pointer = int.from_bytes(image[FONT_DESCRIPTOR:FONT_DESCRIPTOR + 4], "little")
    wide_advance = int.from_bytes(image[FONT_DESCRIPTOR + 4:FONT_DESCRIPTOR + 6], "little")
    if pointer < ROM_BASE:
        raise DecodeError("the descriptor names no table")
    table = pointer - ROM_BASE
    if table + 2 * PALETTE_ENTRIES > len(image):
        raise DecodeError("the table is outside the image")
    offsets = tuple(int.from_bytes(image[table + 2 * code:table + 2 * code + 2], "little")
                    for code in range(PALETTE_ENTRIES))
    for offset in offsets:
        if not offset:
            continue
        record = table + 2 * offset
        if record + 2 > len(image):
            raise DecodeError("a glyph record is outside the image")
        width = int.from_bytes(image[record:record + 2], "little")
        if record + 2 + 2 * (width + 1) > len(image):
            raise DecodeError("a glyph record runs past the image")
    return Font(image=image, table=table, wide_advance=wide_advance, offsets=offsets)


def decode_palette(image: bytes) -> tuple[tuple[int, int, int], ...]:
    """The 256-entry object palette, as 8-bit channels, index 0 first."""
    if len(image) < OBJ_PALETTE + 2 * PALETTE_ENTRIES:
        raise DecodeError("the palette is outside the image")
    return tuple(
        _rgb555(int.from_bytes(image[OBJ_PALETTE + 2 * index:OBJ_PALETTE + 2 * index + 2],
                               "little"))
        for index in range(PALETTE_ENTRIES)
    )


def _rgb555(word: int) -> tuple[int, int, int]:
    """One BGR555 word as 8-bit channels: red in the low five bits, replicated up."""
    channels = []
    for shift in (0, 5, 10):
        channel = (word >> shift) & 0x1F
        channels.append((channel << 3) | (channel >> 2))
    return channels[0], channels[1], channels[2]


# --- the box, chosen from the record's portrait ------------------------------


def box_for(operand: int | None) -> int:
    """The layout limit this record's box uses: 128 only for the operand that is 7.

    MEASURED, from the box constructor at ``0x08012012``: index 1 is chosen only when the
    record's portrait operand is exactly ``7`` (``0x08012104`` to ``0x0801210A``) and
    index 0 otherwise, index ``i`` being ``0x08071720 + 0x10 + 0x14*i`` (``0x0800B29E``).
    Index 0 is layout ``0x08071730`` with limit 144 and art ``0x08071758``; index 1 is
    layout ``0x08071744`` with limit 128 and art ``0x08071A6C``. Operand 0 means no
    portrait and takes index 0, so what selects the second layout is the OPERAND VALUE,
    not whether a portrait is drawn.

    The addresses above are stated here rather than left to a document, because the RE
    Lab's write-up of this rule lives on its own branch and a reader of the default branch
    cannot open it. It is ``docs/research/DIALOGUE_PREVIEW_SEAM.md``, the section "Which
    layout record a box takes", on ``origin/ticket/dialogue-seam-layout-rule``.
    """
    return (LAYOUT_LIMITS[1] if operand == SECOND_LAYOUT_OPERAND
            else LAYOUT_LIMITS[0])


def decode_box(image: bytes, limit: int) -> bytes:
    """The box surface: the art container's payload, 160 by 64 at one byte per pixel."""
    offset = BOX_ART.get(limit)
    if offset is None:
        raise DecodeError(f"no container is known for the {limit}-pixel layout")
    try:
        payload = bytes(webfoot_lz.unpack(image, offset).data)
    except (ValueError, IndexError) as error:
        raise DecodeError(f"the container at 0x{offset:X} will not decode") from error
    if len(payload) != SURFACE_BYTES:
        raise DecodeError(f"the container at 0x{offset:X} decodes to {len(payload)} bytes, "
                          f"not the {SURFACE_BYTES} the surface is")
    return payload


# --- the fitter, the ink and the surface -------------------------------------


def units_of(text: str) -> tuple[int, ...]:
    """The record's text as the engine's own 16-bit units.

    A character outside the basic plane is two units, because the engine reads UTF-16
    and a code point passed through whole would be priced as one unit of the wrong class.
    """
    units: list[int] = []
    for character in text:
        code = ord(character)
        if code < 0x10000:
            units.append(code)
            continue
        code -= 0x10000
        units.append(0xD800 + (code >> 10))
        units.append(0xDC00 + (code & 0x3FF))
    return tuple(units)


def fit_line(font: Font, units: tuple[int, ...], cursor: int,
             limit: int) -> tuple[int, int, bool]:
    """One line, cut the way the engine's fitter cuts it.

    Returns ``(start, stop, ended)``: the units the line draws, and whether the record
    ended. Leading spaces and ``0x0A``/``0x0B`` are skipped; a space records the break
    point BEFORE it; an overflow rewinds to the last space seen, or stops where it is
    when no space was seen; ``0x0008`` skips its own operand.
    """
    end = len(units)
    while cursor < end and units[cursor] in (SPACE, NEWLINE, SOFT_END):
        cursor += 1
    start = cursor
    if cursor >= end or units[cursor] == TERMINATOR:
        return start, cursor, True
    width = 0
    break_at = -1
    break_width = 0
    position = cursor
    while position < end:
        unit = units[position]
        if unit == TERMINATOR:
            return start, position, True
        if unit == SPACE:
            break_at, break_width = position, width
        elif unit == NEWLINE:
            return start, position, False
        elif unit == SOFT_END:
            return start, position, True
        elif unit == INK_ESCAPE:
            # The escape consumes its own operand. At the record's end there is none,
            # so the line stops there rather than reading past the record.
            position = min(position + 2, end)
            continue
        candidate = width + font.advance(unit)
        if candidate > limit:
            if break_at < 0:
                return start, position, False
            return start, break_at, False
        position += 1
        width = candidate
    return start, position, True


def wrap(font: Font, units: tuple[int, ...], limit: int) -> tuple[tuple[int, int], ...]:
    """Every line of the record, as spans of its units, in the order the box draws them."""
    lines: list[tuple[int, int]] = []
    cursor = 0
    while True:
        start, stop, ended = fit_line(font, units, cursor, limit)
        lines.append((start, stop))
        if ended or stop <= start:
            # `stop <= start` is unreachable while every advance is under both limits;
            # it is here so a table that says otherwise cannot spin this loop.
            return tuple(lines)
        cursor = stop


def carries_soft_end(units: tuple[int, ...]) -> bool:
    """Whether the record keeps a drawable unit after its own ``0x0B``.

    The fitter sets the record's end flag at a soft end and leaves its cursor ON that
    unit, so text after it belongs to a segment the engine starts at the soft end, and
    the reveal rule for that segment is not established. That is a separate question
    from how the first segment lays out, so `wrap` answers only the first and this
    answers the second. Whitespace after the soft end is not a second segment, and a
    ``0x0B`` that ends the record is the ordinary case.
    """
    for position, unit in enumerate(units):
        if unit != SOFT_END:
            continue
        return any(later not in (TERMINATOR, NEWLINE, SOFT_END, SPACE)
                   for later in units[position + 1:])
    return False


def paint(font: Font, art: bytes, units: tuple[int, ...],
          lines: tuple[tuple[int, int], ...], ink: int = DEFAULT_INK) -> bytes:
    """The box surface with the record drawn on it, as palette indices."""
    surface = bytearray(art)
    current = ink
    for row, (start, stop) in enumerate(lines):
        x = TEXT_ORIGIN[0]
        y = TEXT_ORIGIN[1] + row * LINE_HEIGHT
        position = start
        while position < stop:
            unit = units[position]
            if unit == INK_ESCAPE:
                current = units[position + 1] & 0xFF if position + 1 < len(units) else current
                position += 2
                continue
            glyph = font.glyph(unit)
            if glyph is not None and y + GLYPH_ROWS <= SURFACE_HEIGHT:
                for column in range(min(glyph.width, SURFACE_WIDTH - x)):
                    bits = glyph.columns[column]
                    for bit in range(GLYPH_ROWS):
                        if (bits >> bit) & 1:
                            surface[(y + bit) * SURFACE_WIDTH + x + column] = current
            x += font.advance(unit)
            position += 1
    return bytes(surface)


@dataclass(frozen=True, slots=True)
class Render:
    """One record's surface, or the stated reason there is none."""

    surface: bytes = b""
    lines: int = 0
    limit: int = 0
    problem: str = ""
    #: The one rule that is missing where there is no surface, named for the reader.
    missing: str = ""

    @property
    def drawn(self) -> bool:
        """Whether this render may be painted at all."""
        return not self.problem


def render(font: Font, art: bytes, text: str, portrait: int | None = None) -> Render:
    """Render one record the way the engine draws it, or say why there is none.

    A record that needs more lines than the box holds is drawn by the engine as a
    window into the record, and a record that keeps text past its ``0x0B`` soft end is
    a segment the reveal rule is not established for. Neither is guessed here: both are
    reported and the surface is empty, so a caller cannot paint an approximation of one
    by accident.
    """
    limit = box_for(portrait)
    units = units_of(text)
    lines = wrap(font, units, limit)
    if carries_soft_end(units):
        return Render(lines=len(lines), limit=limit,
                      problem=("this record keeps text after its own 0x0B soft end, and "
                               "the rule that draws what follows is not established"),
                      missing=SOFT_RULE)
    if len(lines) > LINES_PER_PAGE:
        return Render(lines=len(lines), limit=limit,
                      problem=(f"this record needs {len(lines)} lines and the box holds "
                               f"{LINES_PER_PAGE}"),
                      missing=SCROLL_RULE)
    return Render(surface=paint(font, art, units, lines), lines=len(lines), limit=limit)


# --- the widget ---------------------------------------------------------------


class DialoguePreview(QWidget):
    """The pane: the engine's own render of the selected record, or why there is none."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._image: bytes | None = None
        self._name = ""
        self._text = ""
        self._portrait: int | None = None
        self._font: Font | None = None
        self._palette: tuple[tuple[int, int, int], ...] = ()
        self._arts: dict[int, bytes] = {}
        self._problem = WAITING_IMAGE
        self._missing: tuple[str, ...] = ("an open image",)
        self._no_box = False
        self._render: Render | None = None
        self.setObjectName("dialoguePreview")
        self.setProperty("role", "viewport")

    def set_image(self, image: bytes | None, name: str = "") -> None:
        """The image the reader opened, read-only, and the name to show for it."""
        if image is self._image and name == self._name:
            return
        self._image = image
        self._name = name
        self._font = None
        self._palette = ()
        self._arts = {}
        if image is None:
            self._no_box = False
        self._refresh()

    def set_text(self, text: str) -> None:
        """The selected record's text, as the editor currently holds it."""
        if text == self._text:
            return
        self._text = text
        self._refresh()

    def set_portrait(self, operand: int | None) -> None:
        """The portrait operand the record stores, or None when the record has none."""
        if operand == self._portrait:
            return
        self._portrait = operand
        self._refresh()

    def set_no_box(self, no_box: bool) -> None:
        """Whether this row has no dialogue box at all.

        A string slot is not drawn in a dialogue box by the engine, so the pane says
        what the row is rather than drawing an empty box for it.
        """
        if no_box == self._no_box:
            return
        self._no_box = no_box
        self._refresh()

    # --- what the window asks -------------------------------------------------

    def state(self) -> str:
        """`ready`, `limited` for a case the measurement leaves open, or `waiting`."""
        if self._render is None:
            return "waiting"
        return "ready" if self._render.drawn else "limited"

    def missing(self) -> tuple[str, ...]:
        """What keeps the pane out of its ready state, named for the reader."""
        return self._missing

    def ready(self) -> bool:
        return self.state() == "ready"

    def source_name(self) -> str:
        """The image the render comes from, or the name of the state it waits in."""
        return (self._name or "the open image") if self.ready() else self.state()

    # --- decoding and rendering ----------------------------------------------

    def _refresh(self) -> None:
        """Decode what this image can give and render this record. It never raises."""
        self._render = None
        if self._image is None:
            self._problem = WAITING_IMAGE
            self._missing = ("an open image",)
            self.update()
            return
        source = self._source()
        if source is None:
            self.update()
            return
        font, art = source
        self._render = render(font, art, self._text, self._portrait)
        if self._render.drawn:
            self._problem, self._missing = "", ()
        else:
            self._problem = f"{LIMITED}{self._render.problem}."
            self._missing = (self._render.missing,)
        self.update()

    def _source(self) -> tuple[Font, bytes] | None:
        """This image's font and its box art for the selected portrait, or None."""
        if self._no_box:
            # A row that is not a dialogue record has no box to decode, so the decode
            # is not attempted and the pane says what the row is instead.
            self._problem = f"{LIMITED}{NO_DIALOGUE_BOX}."
            self._missing = ("a dialogue record",)
            return None
        if self._font is None:
            try:
                self._font = decode_font(self._image)
                self._palette = decode_palette(self._image)
            except DecodeError as error:
                self._problem = NO_FONT
                self._missing = (f"the font at 0x{FONT_DESCRIPTOR:X} ({error})",)
                return None
        limit = box_for(self._portrait)
        if limit not in self._arts:
            try:
                self._arts[limit] = decode_box(self._image, limit)
            except DecodeError as error:
                self._problem = NO_BOX
                self._missing = (f"the box art at 0x{BOX_ART[limit]:X} ({error})",)
                return None
        return self._font, self._arts[limit]

    def _surface(self) -> QImage:
        """The rendered surface as an indexed image through the image's own palette."""
        image = QImage(self._render.surface, SURFACE_WIDTH, SURFACE_HEIGHT, SURFACE_WIDTH,
                       QImage.Format.Format_Indexed8)
        image.setColorTable([0xFF000000 | red << 16 | green << 8 | blue
                             for red, green, blue in self._palette])
        return image

    # --- the widget's own size and paint -------------------------------------

    def sizeHint(self) -> QSize:  # noqa: N802
        if not self.ready():
            # Room for the waiting line plus the wrapped list of what is absent.
            line = QFontMetrics(theme.type_scale().caption).height()
            return QSize(260, 3 * line + 2 * _MARGIN)
        return QSize(SURFACE_WIDTH + 2 * _MARGIN, SURFACE_HEIGHT + 2 * _MARGIN)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Scale 1 is the floor wherever the box is drawn at all."""
        return self.sizeHint()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        active = theme.active_theme()
        painter.fillRect(self.rect(), QColor(active.preview_screen))
        if not self.ready():
            # One line and nothing else: a drawn approximation is the failure this
            # state exists to prevent.
            painter.setPen(QPen(QColor(active.preview_marker), 1))
            painter.setFont(theme.type_scale().caption)
            painter.drawText(self.rect().adjusted(_MARGIN, _MARGIN, -_MARGIN, -_MARGIN),
                             int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                                 | Qt.TextFlag.TextWordWrap),
                             f"{self._problem} Missing: {', '.join(self._missing)}")
            painter.end()
            return
        factor = _integer_scale(self.width(), self.height())
        painter.translate(_MARGIN, _MARGIN)
        painter.scale(factor, factor)
        painter.drawImage(0, 0, self._surface())
        painter.end()


def _integer_scale(width: int, height: int) -> int:
    """Nearest-neighbour only: an integer factor, never a fractional stretch."""
    return max(1, min(_MAX_SCALE, (width - 2 * _MARGIN) // SURFACE_WIDTH,
                      (height - 2 * _MARGIN) // SURFACE_HEIGHT))
