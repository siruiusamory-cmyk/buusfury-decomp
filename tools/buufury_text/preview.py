"""The in-game dialogue preview: a real render, or a line that says it is waiting.

This pane shows the GAME, so it may not be approximated. Until the RE Lab's
extracted data is present in full, the pane draws one line of text and nothing
else: no box, no glyph, no invented palette, no stand-in font. When the data is
present every glyph comes from the game's own tiles, every wrap from the game's
declared column count, every page break from the game's declared rule, and every
scale is an integer factor with nearest-neighbour sampling only.

**The data contract** (design note section 9), read from `build/gamedata/dialogue/`:

| Part | Shape this seam reads |
| --- | --- |
| `palette.json` | `{"palette": [<RGB555 int>, ...]}`, index 0 first |
| `glyphs.png` or `glyphs.bin` | PNG: a tile sheet, `glyph_width` x `glyph_height` tiles, blank = absent. BIN: consecutive tiles, `glyph_height` bytes each, 1 bit per pixel, MSB leftmost |
| `glyph_widths.json` | codepoint -> pixels the glyph advances, `0` or absent = no glyph |
| `glyph_tiles.json` | codepoint -> tile index in the sheet or the bin. Absent: the codepoint is the tile index |
| `box.png` or `box.bin` | the dialogue box art at its native size, indexed into `palette` |
| `metrics.json` | `origin` [x, y] in box pixels, `line_stride`, `box_rect` [x, y, w, h], `columns`, `page_stride`, `page_count`, and for the BIN forms `glyph_width`, `glyph_height`, `box_width` |
| `rules.md` | the wrap and page-break rules as the game implements them, with the addresses they were measured at |
| `captures/` | reference mGBA screenshots: `<name>.png` beside `<name>.json` `{"line": ..., "portrait": ...}`, for the harness |

`glyphs.bin` and `box.bin` are tile-major and palette-indexed. The per-glyph advance
width and the tile index both come from JSON, because the sheet carries neither.
`box_rect` is the box art's native size, so the art is blitted at that size.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFontMetrics, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget

from tools.webfoot import textedit

from . import theme

#: Where the RE Lab's extraction lands. Ignored by git, never committed.
GAMEDATA = Path("build") / "gamedata" / "dialogue"
#: The one line the pane shows while it cannot render for real.
WAITING = "In-game preview: waiting on extracted game font"
#: The parts whose absence keeps the pane in its waiting state, in read order.
PARTS = ("palette.json", "glyphs.png or glyphs.bin", "box.png or box.bin",
         "metrics.json", "rules.md")
#: The one neutral mark for a control unit whose glyph the font does not carry.
CHARACTER = "\ufffc"

_MARGIN = 8
_MAX_SCALE = 4
_NEWLINE = 0x0A
#: RGB555: five bits per channel, blue in the low bits.
_CHANNEL_BITS = 5
_CHANNEL_MAX = 31


# --- the loaded data ----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Glyph:
    """One font tile: the pixels it draws and how far it advances."""

    code: int
    width: int
    image: QImage


@dataclass(frozen=True, slots=True)
class Font:
    """The game's font, as the extraction describes it."""

    height: int
    width: int
    glyphs: dict[int, Glyph]
    blank: int = 0


@dataclass(frozen=True, slots=True)
class Box:
    """The dialogue box art, as the game draws it."""

    art: QImage
    palette: tuple[QColor, ...]


@dataclass(frozen=True, slots=True)
class Metrics:
    """Where the text lands, how it wraps and where the page breaks."""

    origin: tuple[int, int]
    line_stride: int
    box_rect: tuple[int, int, int, int]
    columns: int
    page_stride: int
    page_count: int


@dataclass(frozen=True, slots=True)
class DialogueData:
    """Every part the renderer needs, or a tuple naming what is still absent."""

    missing: tuple[str, ...]
    palette: tuple[QColor, ...] = ()
    font: Font | None = None
    box: Box | None = None
    metrics: Metrics | None = None
    portraits: dict[int, QImage] = field(default_factory=dict)


def dialogue_directory() -> Path:
    """Where the extraction is read from, relative to the repository root."""
    return Path(__file__).resolve().parents[2] / GAMEDATA


def load_data(directory: Path | None = None) -> DialogueData:
    """Load the extraction, naming every part that is absent or unreadable.

    Every part is checked even when an earlier one has already failed, so the
    `missing` tuple always names the whole story in one fixed order. Nothing is
    invented: a part that cannot be read is a missing part, and a missing part
    keeps the pane in its waiting state.
    """
    root = Path(directory) if directory is not None else dialogue_directory()
    if not root.is_dir():
        return DialogueData(missing=PARTS)
    detail: list[str] = []
    palette = _load_palette(root, detail)
    metrics = _load_metrics(root, detail)
    font = _load_font(root, palette, metrics, detail)
    box = _load_box(root, palette, detail)
    rules = root / "rules.md"
    if not rules.is_file() or not rules.read_text(encoding="utf-8").strip():
        detail.append("rules.md")
    missing = tuple(part for part in PARTS if not _present(part, root))
    if missing:
        return DialogueData(missing=missing)
    return DialogueData(missing=(), palette=palette, font=font, box=box, metrics=metrics,
                        portraits=_load_portraits(root, palette))


def _present(part: str, root: Path) -> bool:
    """Whether one contract part is on disk. A part either form satisfies counts."""
    if part == "glyphs.png or glyphs.bin":
        return any((root / f"glyphs.{suffix}").is_file() for suffix in ("png", "bin"))
    if part == "box.png or box.bin":
        return any((root / f"box.{suffix}").is_file() for suffix in ("png", "bin"))
    return (root / part).is_file()


def _rgb555(value: int) -> QColor:
    red = (value >> 2 * _CHANNEL_BITS) & _CHANNEL_MAX
    green = (value >> _CHANNEL_BITS) & _CHANNEL_MAX
    blue = value & _CHANNEL_MAX
    return QColor(*((channel * 255 + _CHANNEL_MAX // 2) // _CHANNEL_MAX
                    for channel in (red, green, blue)))


def _load_palette(root: Path, missing: list[str]) -> tuple[QColor, ...]:
    path = root / "palette.json"
    try:
        values = json.loads(path.read_text(encoding="utf-8"))["palette"]
    except (OSError, ValueError, KeyError, TypeError):
        missing.append("palette.json")
        return ()
    return tuple(_rgb555(int(value)) for value in values)


def _load_metrics(root: Path, missing: list[str]) -> Metrics | None:
    path = root / "metrics.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Metrics(
            origin=(int(raw["origin"][0]), int(raw["origin"][1])),
            line_stride=int(raw["line_stride"]),
            box_rect=tuple(int(part) for part in raw["box_rect"]),
            columns=int(raw["columns"]),
            page_stride=int(raw["page_stride"]),
            page_count=int(raw["page_count"]),
        )
    except (OSError, ValueError, KeyError, TypeError):
        missing.append("metrics.json")
        return None


def _load_font(root: Path, palette: tuple[QColor, ...], metrics: Metrics | None,
               missing: list[str]) -> Font | None:
    sheet = root / "glyphs.png"
    raw = root / "glyphs.bin"
    if sheet.is_file():
        image = QImage(str(sheet))
        if image.isNull():
            missing.append("glyphs.png")
            return None
        return _sheet_font(image, root, missing)
    if raw.is_file():
        return _tile_font(raw, root, metrics, missing)
    missing.append("glyphs.png or glyphs.bin")
    return None


def _widths(root: Path) -> dict[int, int] | None:
    """codepoint -> advance width, or None when the table is absent or unreadable."""
    try:
        values = json.loads((root / "glyph_widths.json").read_text(encoding="utf-8"))
        return {int(code): int(width) for code, width in values.items()}
    except (OSError, ValueError, TypeError):
        return None


def _tile_of(code: int, tiles: dict[int, int]) -> int:
    return tiles.get(code, code)


def _tiles(root: Path) -> dict[int, int]:
    """codepoint -> tile index. Absent, the codepoint is the tile index."""
    try:
        values = json.loads((root / "glyph_tiles.json").read_text(encoding="utf-8"))
        return {int(code): int(tile) for code, tile in values.items()}
    except (OSError, ValueError, TypeError):
        return {}


def _sheet_font(image: QImage, root: Path, missing: list[str]) -> Font | None:
    widths = _widths(root)
    tiles = _tiles(root)
    try:
        declared = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
        width = int(declared["glyph_width"])
        height = int(declared["glyph_height"])
        columns = image.width() // width
        rows = image.height() // height
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError):
        missing.append("glyphs.png (glyph_width and glyph_height)")
        return None
    if widths is None or width <= 0 or height <= 0 or columns <= 0 or rows <= 0:
        missing.append("glyph_widths.json")
        return None
    glyphs = {}
    for code, advance in widths.items():
        if not advance:
            continue
        index = _tile_of(code, tiles)
        column, row = index % columns, index // columns
        if row >= rows:
            continue
        glyphs[code] = Glyph(code, advance,
                             image.copy(column * width, row * height, width, height))
    if not glyphs:
        missing.append("glyphs.png (every tile is blank)")
        return None
    return Font(height=height, width=width, glyphs=glyphs)


def _tile_font(raw: Path, root: Path, metrics: Metrics | None, missing: list[str]) -> Font | None:
    widths = _widths(root)
    tiles = _tiles(root)
    try:
        declared = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
        width = int(declared["glyph_width"])
        height = int(declared["glyph_height"])
        data = raw.read_bytes()
    except (OSError, ValueError, KeyError, TypeError):
        missing.append("glyphs.bin (glyph_width and glyph_height)")
        return None
    if widths is None:
        missing.append("glyph_widths.json")
        return None
    if width <= 0 or height <= 0 or len(data) < height:
        missing.append("glyphs.bin")
        return None
    glyphs = {}
    for code, advance in widths.items():
        if not advance:
            continue
        index = _tile_of(code, tiles)
        if (index + 1) * height > len(data):
            continue
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        for row in range(height):
            bits = data[index * height + row]
            for column in range(min(8, width)):
                if bits & (0x80 >> column):
                    # A 1 bpp tile carries no colour of its own; it carries which
                    # pixels the glyph sets, which the index covers.
                    image.setPixelColor(column, row, QColor(Qt.GlobalColor.white))
        glyphs[code] = Glyph(code, advance, image)
    if not glyphs:
        missing.append("glyphs.bin (every tile is blank)")
        return None
    return Font(height=height, width=width, glyphs=glyphs)


def _load_box(root: Path, palette: tuple[QColor, ...], missing: list[str]) -> Box | None:
    art = QImage(str(root / "box.png")) if (root / "box.png").is_file() else None
    if art is None or art.isNull():
        raw = root / "box.bin"
        if not raw.is_file():
            missing.append("box.png or box.bin")
            return None
        try:
            declared = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
            width = int(declared["box_width"])
        except (OSError, ValueError, KeyError, TypeError):
            missing.append("box.bin (box_width)")
            return None
        art = _indexed(raw.read_bytes(), width, palette)
        if art is None:
            missing.append("box.bin")
            return None
    return Box(art=art, palette=palette)


def _indexed(data: bytes, width: int, palette: tuple[QColor, ...]) -> QImage | None:
    """Palette indices, row-major, resolved through the loaded palette."""
    if width <= 0 or not palette or len(data) % width:
        return None
    image = QImage(width, len(data) // width, QImage.Format.Format_ARGB32)
    for at, index in enumerate(data):
        image.setPixelColor(at % width, at // width,
                            palette[index] if index < len(palette)
                            else QColor(Qt.GlobalColor.transparent))
    return image


def _load_portraits(root: Path, palette: tuple[QColor, ...]) -> dict[int, QImage]:
    """Portrait art by operand, when the extraction carries it. Never invented."""
    directory = root / "portraits"
    if not directory.is_dir():
        return {}
    found: dict[int, QImage] = {}
    for path in sorted(directory.iterdir()):
        art = QImage(str(path)) if path.suffix.lower() == ".png" else None
        if art is None or art.isNull():
            continue
        stem = path.stem.lower().removeprefix("portrait").removeprefix("_")
        try:
            found[int(stem, 16)] = art
        except ValueError:
            continue
    return found


# --- wrapping and pagination, pure -------------------------------------------


@runtime_checkable
class GlyphSource(Protocol):
    """What `layout` needs from a font: the wrap width, the advance, the page size."""

    @property
    def columns(self) -> int: ...

    @property
    def page_lines(self) -> int: ...

    def advance(self, character: str) -> int: ...


@dataclass(frozen=True, slots=True)
class _StubSource:
    """The game's own wrapping rule, read off the loaded font and metrics."""

    columns: int
    page_lines: int
    advances: dict[int, int]
    fallback: int

    def advance(self, character: str) -> int:
        return self.advances.get(ord(character), self.fallback)


def source_for(data: DialogueData) -> GlyphSource:
    """The wrap rule the renderer and the harness both use."""
    advances = {} if data.font is None else {
        code: glyph.width for code, glyph in data.font.glyphs.items()}
    fallback = 0 if data.font is None else data.font.width
    columns = 1 if data.metrics is None else max(1, data.metrics.columns)
    page_lines = 1 if data.metrics is None else max(1, data.metrics.page_count)
    return _StubSource(columns, page_lines, advances, fallback)


def layout(text: str, source: GlyphSource) -> tuple[tuple[str, ...], ...]:
    """Pages of lines: wrap at the game's column count, break at its page count.

    A line break is the game's own 0x0A unit; a column break happens only between
    written units, so a word longer than the box is never clipped. A unit whose
    glyph the font does not carry still advances and is drawn as one neutral mark.
    """
    pages: list[list[str]] = []
    line = ""
    column = 0
    for unit in textedit.units(text):
        if isinstance(unit, textedit.Control):
            if unit.raw and ord(unit.raw[0]) == _NEWLINE:
                _push(pages, line, source)
                line, column = "", 0
                continue
            written = CHARACTER
        else:
            written = unit.value
        for character in written:
            if character == "\n":
                _push(pages, line, source)
                line, column = "", 0
                continue
            if column >= source.columns:
                _push(pages, line, source)
                line, column = "", 0
            line += character
            column += 1
    _push(pages, line, source)
    return tuple(tuple(page) for page in pages)


def _push(pages: list[list[str]], line: str, source: GlyphSource) -> None:
    """Append one wrapped line, starting a page when the page is full."""
    page_lines = max(1, source.page_lines)
    if not pages or len(pages[-1]) >= page_lines:
        pages.append([])
    pages[-1].append(line)


# --- rendering ----------------------------------------------------------------


def render_line(data: DialogueData, text: str, portrait: int | None = None,
                scale: int = 1) -> QImage:
    """One line, rendered at an integer scale with nearest-neighbour sampling."""
    if data.metrics is None or data.box is None or data.font is None:
        raise ValueError("no render is possible: the extracted data is incomplete")
    metrics = data.metrics
    left, top, width, height = metrics.box_rect
    factor = max(1, int(scale))
    image = QImage(width * factor, height * factor, QImage.Format.Format_ARGB32)
    image.fill(QColor(theme.active_theme().preview_screen))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
    _draw_page(painter, data, text, portrait, factor)
    painter.end()
    return image


def _draw_page(painter: QPainter, data: DialogueData, text: str, portrait: int | None,
               factor: int) -> None:
    metrics = data.metrics
    left, top, width, height = metrics.box_rect
    painter.drawImage(QRect(left * factor, top * factor, width * factor, height * factor),
                      data.box.art)
    if portrait is not None and portrait in data.portraits:
        art = data.portraits[portrait]
        painter.drawImage(QRect(left * factor, top * factor,
                                art.width() * factor, art.height() * factor), art)
    source = source_for(data)
    ox, oy = metrics.origin
    for page_number, page in enumerate(layout(text, source)[:max(1, metrics.page_count)]):
        for row, line in enumerate(page):
            x = ox
            y = oy + row * metrics.line_stride + page_number * metrics.page_stride
            for character in line:
                glyph = data.font.glyphs.get(ord(character))
                if glyph is None:
                    x += source.advance(character)
                    continue
                painter.drawImage(
                    QRect((left + x) * factor, (top + y) * factor,
                          glyph.image.width() * factor, glyph.image.height() * factor),
                    glyph.image)
                x += glyph.width


# --- the validation harness ---------------------------------------------------


@dataclass(frozen=True, slots=True)
class Comparison:
    """One reference capture against the render for the same line."""

    name: str
    rendered: QImage
    captured: QImage
    differing: int
    first: tuple[int, int] | None

    @property
    def matches(self) -> bool:
        return self.differing == 0 and self.rendered.size() == self.captured.size()


def compare(rendered: QImage, captured: QImage) -> tuple[int, tuple[int, int] | None]:
    """Pixel by pixel: how many differ, and where the first one is."""
    if rendered.size() != captured.size():
        return (rendered.width() * rendered.height(), (0, 0))
    differing = 0
    first: tuple[int, int] | None = None
    for y in range(rendered.height()):
        for x in range(rendered.width()):
            if rendered.pixel(x, y) != captured.pixel(x, y):
                differing += 1
                if first is None:
                    first = (x, y)
    return differing, first


def references(directory: Path | None = None) -> tuple[tuple[str, str, int | None], ...]:
    """The declared line of every reference capture, from the capture sidecars."""
    root = Path(directory) if directory is not None else dialogue_directory() / "captures"
    if not root.is_dir():
        return ()
    found: list[tuple[str, str, int | None]] = []
    for sidecar in sorted(root.glob("*.json")):
        try:
            raw = json.loads(sidecar.read_text(encoding="utf-8"))
            found.append((sidecar.stem, str(raw["line"]), raw.get("portrait")))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return tuple(found)


def harness(directory: Path | None = None) -> tuple[Comparison, ...]:
    """Render every reference capture's line and compare it pixel for pixel.

    An empty result means the data or the captures are absent, which the caller
    reports loudly rather than reading as a pass.
    """
    root = Path(directory) if directory is not None else dialogue_directory()
    data = load_data(root)
    captures = root / "captures"
    if data.missing or not captures.is_dir():
        return ()
    done: list[Comparison] = []
    for name, line, portrait in references(captures):
        path = captures / f"{name}.png"
        captured = QImage(str(path))
        if captured.isNull():
            continue
        rendered = render_line(data, line, portrait)
        differing, first = compare(rendered, captured)
        done.append(Comparison(name, rendered, captured, differing, first))
    return tuple(done)


# --- the widget ---------------------------------------------------------------


class DialoguePreview(QWidget):
    """The pane: the waiting line until the data lands, the real render after."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data: DialogueData | None = None
        self._text = ""
        self._portrait: int | None = None
        self.setObjectName("dialoguePreview")
        self.setProperty("role", "viewport")
        self.set_source(None)

    def set_text(self, text: str) -> None:
        self._text = text
        self.update()

    def set_portrait(self, operand: int | None) -> None:
        """The portrait operand the record stores, or None when the record has none."""
        self._portrait = operand
        self.update()

    def set_source(self, source) -> None:
        """A `DialogueData`, a directory to load it from, or None to discover it."""
        if isinstance(source, DialogueData):
            self._data = source
        elif source is None:
            self._data = load_data()
        else:
            self._data = load_data(Path(source))
        self.update()

    def source_name(self) -> str:
        """What the render is drawn from, or the name of the state it waits in."""
        if not self.ready():
            return self.state()
        return GAMEDATA.as_posix()

    def state(self) -> str:
        """`waiting` with nothing extracted at all, `incomplete` with a part, else `ready`."""
        if self._data is None or len(self._data.missing) == len(PARTS):
            # Every part absent is the state that ships: no extraction has happened.
            return "waiting"
        if not self._data.missing:
            return "ready"
        return "incomplete"

    def missing(self) -> tuple[str, ...]:
        """Every part of the contract that is absent or unreadable."""
        return PARTS if self._data is None else self._data.missing

    def ready(self) -> bool:
        return self.state() == "ready"

    def sizeHint(self) -> QSize:  # noqa: N802
        if not self.ready():
            # Room for the waiting line plus the wrapped list of what is absent. One
            # line cut that list off at the pane's edge, which loses the one fact this
            # state exists to give the reader.
            line = QFontMetrics(theme.type_scale().caption).height()
            return QSize(260, 3 * line + 2 * _MARGIN)
        width, height = self._data.metrics.box_rect[2], self._data.metrics.box_rect[3]
        return QSize(width + 2 * _MARGIN, height + 2 * _MARGIN)

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
            # One wrapped line and nothing else. No box, no glyph, no placeholder: a
            # drawn approximation is the failure this requirement exists to prevent.
            painter.setPen(QPen(QColor(active.preview_marker), 1))
            painter.setFont(theme.type_scale().caption)
            painter.drawText(self.rect().adjusted(_MARGIN, _MARGIN, -_MARGIN, -_MARGIN),
                             int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                                 | Qt.TextFlag.TextWordWrap),
                             f"{WAITING}. Missing: {', '.join(self.missing())}")
            painter.end()
            return
        factor = _integer_scale(self._data.metrics, self.width(), self.height())
        painter.save()
        painter.scale(factor, factor)
        _draw_page(painter, self._data, self._text, self._portrait, 1)
        painter.restore()
        painter.end()


def _integer_scale(metrics: Metrics, width: int, height: int) -> int:
    """Nearest-neighbour only: an integer factor, never a fractional stretch."""
    if metrics.box_rect[2] <= 0 or metrics.box_rect[3] <= 0:
        return 1
    return max(1, min(_MAX_SCALE, (width - 2 * _MARGIN) // metrics.box_rect[2],
                      (height - 2 * _MARGIN) // metrics.box_rect[3]))
