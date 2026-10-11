"""The one place a colour, a font, a metric or a painting rule is decided.

Every token value is adopted from the Cartridge Workbench token table held by the
coordinator, never invented here, so nothing outside this file holds a hex value and
no widget can build a second theme.

Four roles are named separately even though three of them share a value, because
they are different jobs: `border` outlines a control, `divider` separates content,
`accent_ink` is the ink that sits on the accent fill, and `text_disabled` is the
disabled text colour and nothing else.

Metrics and type come from the application font, never from a frozen pixel, and the
type ladder is fixed whole pixels so it survives 100, 125 and 150 percent scaling.
Two weights only, 400 and 600. No italic, no shadow, no animation: a state change
moves a background, an outline or a text colour and never a border width.
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from PySide6.QtCore import QByteArray, QRect, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QIcon,
    QImage,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QApplication, QProxyStyle, QStyle, QStyleFactory

from . import status
from .session import State

MODE_SYSTEM = "system"
MODE_LIGHT = "light"
MODE_DARK = "dark"
MODES = (MODE_SYSTEM, MODE_LIGHT, MODE_DARK)

#: The Cartridge Workbench table, light then dark. The only hex in the codebase.
#: `divider` repeats `border` deliberately: it is a separate NAME, so the day the
#: two roles need separate values it is one edit and no caller moves.
TOKENS: dict[str, tuple[str, str]] = {
    "window": ("#F3F4F6", "#17191D"),
    "surface": ("#FFFFFF", "#1E2126"),
    "surface_raised": ("#F8F9FB", "#252931"),
    "text_primary": ("#20242A", "#EEF1F4"),
    "text_secondary": ("#5D6672", "#AEB6C0"),
    # The neutral ladder's quiet step. Disabled text ONLY; it is below the 4.5:1
    # floor the other two text colours carry, which is what makes it read disabled.
    "text_disabled": ("#8A9199", "#767E88"),
    "border": ("#C7CDD5", "#414852"),
    "divider": ("#C7CDD5", "#414852"),
    "splitter": ("#77808A", "#6F7883"),
    "accent": ("#235FAE", "#7DB0FF"),
    # The ink on the accent fill. It is the surface token, which is what the
    # existing export button already paints its label with.
    "accent_ink": ("#FFFFFF", "#1E2126"),
    "selection": ("#D8E8FF", "#243B5A"),
    "focus": ("#1F6FEB", "#8BB9FF"),
    "state_unchanged": ("#6B7280", "#9AA3AE"),
    "state_edited": ("#1F64C8", "#83B8FF"),
    "state_move": ("#8A5A00", "#F1BE5C"),
    "state_refused": ("#7A2E8A", "#E59AEF"),
    "state_base_changed": ("#5A4FB5", "#B7A9FF"),
    # The dialogue preview is the one surface that shows the GAME rather than the
    # application, so its four tokens are the same in both modes.
    "preview_screen": ("#0B0F14", "#0B0F14"),
    "preview_box": ("#F8F8F8", "#F8F8F8"),
    "preview_ink": ("#101418", "#101418"),
    "preview_marker": ("#8A8F96", "#8A8F96"),
}

#: Badge fill and ink, light then dark. The table names four of the five states.
BADGES: dict[State, tuple[tuple[str, str], tuple[str, str]]] = {
    State.UNCHANGED: (("#F8F9FB", "#6B7280"), ("#252931", "#9AA3AE")),
    State.EDITED: (("#E7F0FD", "#1F5CA8"), ("#28476A", "#DCEAFF")),
    State.WILL_MOVE: (("#FFF0C2", "#5C4000"), ("#F1BE5C", "#201B12")),
    State.REFUSED: (("#513457", "#FFFFFF"), ("#5D3A66", "#FFFFFF")),
    State.BASE_CHANGED: (("#EEEAFB", "#4B4098"), ("#3C355E", "#E2DDFF")),
}

#: A row fill is legible only if it is nearly the surface it sits on.
LOCAL_FILL_ALPHA = 0.24

#: The fixed integer ladder. Whole pixels are what survive 100, 125 and 150 percent
#: display scaling, so no ratio and no point size reaches a role.
TYPE_SIZES: dict[str, int] = {
    "label": 11, "caption": 12, "body": 12, "prose": 13, "data": 12, "strong": 12,
}
#: 0.08 em at 11 px, in the absolute spacing units Qt takes.
LABEL_TRACKING_EM = 0.08
TYPE_WEIGHTS: dict[str, int] = {
    "label": 600, "caption": 400, "body": 400, "prose": 400, "data": 400, "strong": 600,
}

_MONO_PREFERENCE = ("Cascadia Mono", "Consolas")
_FAMILIES: frozenset[str] = frozenset()
_ICON_CACHE: dict[str, QIcon] = {}
#: The directory holding the recoloured stylesheet copies, created on first use.
_ICON_FILES: Path | None = None
_TEXT_HEIGHT_FALLBACK = 12
#: The two pixel sizes one icon is rendered at, so a 2x display gets a real 2x
#: pixmap rather than a scaled 1x one.
_ICON_PIXEL_SIZES = (16, 32)


@dataclass(frozen=True, slots=True)
class Theme:
    """One resolved mode. `mode` is light or dark, never system."""

    mode: str
    window: str
    surface: str
    surface_raised: str
    text_primary: str
    text_secondary: str
    text_disabled: str
    border: str
    divider: str
    splitter: str
    accent: str
    accent_ink: str
    selection: str
    focus: str
    state_unchanged: str
    state_edited: str
    state_move: str
    state_refused: str
    state_base_changed: str
    preview_screen: str
    preview_box: str
    preview_ink: str
    preview_marker: str


@dataclass(frozen=True, slots=True)
class Metrics:
    """Density derived from the application font, never from a frozen pixel."""

    text_height: int
    row_height: int
    header_height: int
    field_height: int
    chip_height: int
    segment_height: int
    status_height: int
    tab_height: int
    pad_xs: int
    pad_sm: int
    pad_md: int
    pad_lg: int
    pad_xl: int
    gap: int
    radius: int
    touch: int


@dataclass(frozen=True, slots=True)
class Type:
    """The six type roles. Each is a ready QFont; `data` is the mono data role."""

    label: QFont
    caption: QFont
    body: QFont
    prose: QFont
    data: QFont
    strong: QFont


_ACTIVE: Theme | None = None
_SHAPE: Metrics | None = None
_TYPES: Type | None = None
_PROXY: EditorProxyStyle | None = None


def theme_for(mode: str, system_is_dark: bool) -> Theme:
    """Resolve a mode to the palette the rest of the window paints with."""
    resolved = MODE_DARK if system_is_dark else MODE_LIGHT
    if mode == MODE_LIGHT:
        resolved = MODE_LIGHT
    elif mode == MODE_DARK:
        resolved = MODE_DARK
    column = 1 if resolved == MODE_DARK else 0
    return Theme(mode=resolved, **{name: pair[column] for name, pair in TOKENS.items()})


def build_palette(theme: Theme) -> QPalette:
    """The roles the window actually uses, plus the Disabled group."""
    palette = QPalette()
    role = QPalette.ColorRole
    group = QPalette.ColorGroup
    palette.setColor(role.Window, QColor(theme.window))
    palette.setColor(role.WindowText, QColor(theme.text_primary))
    palette.setColor(role.Base, QColor(theme.surface))
    palette.setColor(role.AlternateBase, QColor(theme.surface_raised))
    palette.setColor(role.Text, QColor(theme.text_primary))
    palette.setColor(role.Button, QColor(theme.surface_raised))
    palette.setColor(role.ButtonText, QColor(theme.text_primary))
    palette.setColor(role.Highlight, QColor(theme.selection))
    palette.setColor(role.HighlightedText, QColor(theme.text_primary))
    palette.setColor(role.ToolTipBase, QColor(theme.surface_raised))
    palette.setColor(role.ToolTipText, QColor(theme.text_primary))
    placeholder = getattr(role, "PlaceholderText", None)
    if placeholder is not None:
        palette.setColor(placeholder, QColor(theme.text_secondary))
    for disabled in (role.WindowText, role.Text, role.ButtonText, role.HighlightedText):
        palette.setColor(group.Disabled, disabled, QColor(theme.text_disabled))
    return palette


class EditorProxyStyle(QProxyStyle):
    """A deliberate set of overrides over Fusion; everything else defers to it."""

    def __init__(self, shape: Metrics | None = None, app: QApplication | None = None) -> None:
        super().__init__()
        self._metrics = shape
        self._app = app

    def _shape(self) -> Metrics:
        global _SHAPE
        if self._metrics is None:
            app = self._app if self._app is not None else QApplication.instance()
            self._metrics = metrics(app)
        _SHAPE = self._metrics
        return self._metrics

    def pixelMetric(self, metric, option=None, widget=None) -> int:  # noqa: N802
        shape = self._shape()
        name = QStyle.PixelMetric
        if metric == name.PM_DefaultFrameWidth:
            return 1
        if metric in (name.PM_SmallIconSize, name.PM_ToolBarIconSize):
            return 16
        if metric == name.PM_ScrollBarExtent:
            return min(16, max(12, shape.text_height))
        if metric in (name.PM_LayoutLeftMargin, name.PM_LayoutRightMargin,
                      name.PM_LayoutTopMargin, name.PM_LayoutBottomMargin):
            return shape.pad_md
        if metric in (name.PM_LayoutHorizontalSpacing, name.PM_LayoutVerticalSpacing):
            return shape.gap
        return super().pixelMetric(metric, option, widget)

    def sizeFromContents(self, contents_type, option, size, widget=None):  # noqa: N802
        shape = self._shape()
        kind = QStyle.ContentsType
        # One shared height: an input and the button beside it are the same height
        # in every state, which is the whole reason this override exists.
        if contents_type in (kind.CT_PushButton, kind.CT_ToolButton, kind.CT_LineEdit,
                             kind.CT_ComboBox):
            size.setHeight(max(size.height(), shape.field_height))
        return super().sizeFromContents(contents_type, option, size, widget)

    def drawPrimitive(self, element, option, painter, widget=None) -> None:  # noqa: N802
        if element == QStyle.PrimitiveElement.PE_FrameFocusRect:
            # Focus is a 2 px ring, drawn at once, and never removed.
            paint_focus_edge(painter, option.rect, active_theme())
            return
        super().drawPrimitive(element, option, painter, widget)


def apply_theme(app: QApplication, mode: str = MODE_SYSTEM) -> Theme:
    """Install Fusion under the proxy style, the palette and the small stylesheet."""
    global _ACTIVE, _FAMILIES, _SHAPE, _TYPES, _PROXY
    _FAMILIES = frozenset(QFontDatabase.families())
    theme = theme_for(mode, _system_is_dark(app))
    _ACTIVE = theme
    _SHAPE = metrics(app)
    _TYPES = type_scale(app)
    proxy = EditorProxyStyle(_SHAPE, app)
    proxy.setBaseStyle(QStyleFactory.create("Fusion"))
    app.setStyle(proxy)
    app.setPalette(build_palette(theme))
    app.setStyleSheet(app_stylesheet(theme))
    _PROXY = proxy
    return theme


def metrics(app: QApplication | None = None) -> Metrics:
    """Row, field, chip and status heights derived from the application font."""
    global _SHAPE
    if app is None and _SHAPE is not None:
        return _SHAPE
    source = app if app is not None else QApplication.instance()
    height = _TEXT_HEIGHT_FALLBACK if source is None else QFontMetrics(source.font()).height()
    shape = _shape_from(height)
    if source is not None:
        _SHAPE = shape
    return shape


def _shape_from(text_height: int) -> Metrics:
    return Metrics(
        text_height=text_height,
        row_height=max(28, text_height + 12),
        header_height=max(24, text_height + 8),
        field_height=max(26, text_height + 10),
        chip_height=max(24, text_height + 8),
        segment_height=5,
        status_height=max(24, text_height + 8),
        tab_height=max(28, text_height + 12),
        pad_xs=2, pad_sm=4, pad_md=8, pad_lg=12, pad_xl=16, gap=8, radius=3, touch=40,
    )


def active_theme() -> Theme:
    """The theme `apply_theme` installed, for painting code that has no app."""
    return _ACTIVE if _ACTIVE is not None else theme_for(MODE_LIGHT, False)


def active_metrics() -> Metrics:
    """The shape `apply_theme` installed, for painting code that has no app."""
    return _SHAPE if _SHAPE is not None else metrics()


def proxy_style() -> EditorProxyStyle | None:
    """The proxy style `apply_theme` installed, or None before it ran."""
    return _PROXY


def _role_font(base: QFont, size: int, weight: int) -> QFont:
    font = QFont(base)
    font.setPixelSize(size)
    font.setWeight(QFont.Weight(weight))
    font.setItalic(False)
    return font


def type_scale(app: QApplication | None = None) -> Type:
    """The six roles, from the application font. Labels take 0.08 em tracking."""
    global _TYPES
    if app is None and _TYPES is not None:
        return _TYPES
    source = app if app is not None else QApplication.instance()
    base = QFont(source.font()) if source is not None else QFont()
    font = _role_font(base, TYPE_SIZES["label"], TYPE_WEIGHTS["label"])
    font.setCapitalization(QFont.Capitalization.AllUppercase)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing,
                          TYPE_SIZES["label"] * LABEL_TRACKING_EM)
    scale = Type(
        label=font,
        caption=_role_font(base, TYPE_SIZES["caption"], TYPE_WEIGHTS["caption"]),
        body=_role_font(base, TYPE_SIZES["body"], TYPE_WEIGHTS["body"]),
        prose=_role_font(base, TYPE_SIZES["prose"], TYPE_WEIGHTS["prose"]),
        data=mono_font(),
        strong=_role_font(base, TYPE_SIZES["strong"], TYPE_WEIGHTS["strong"]),
    )
    if source is not None:
        _TYPES = scale
    return scale


def fonts() -> Type:
    """The installed type scale, resolved from the app font if one is needed."""
    return type_scale()


def mono_font(delta: int = 0) -> QFont:
    """Cascadia Mono then Consolas, else the system fixed font, resized by delta.

    This is the DATA role: ids, offsets, sizes, hashes, meter figures and chip
    internals. It is never handed to prose and never to a button label. Tabular
    figures are declared rather than inherited, because the meter rewrites its
    numbers on every keystroke and proportional digits would shift the layout
    under the reader while they type.
    """
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    families = _FAMILIES or frozenset(QFontDatabase.families())
    for family in _MONO_PREFERENCE:
        if family in families:
            font.setFamily(family)
            break
    font.setPixelSize(max(1, TYPE_SIZES["data"] + delta))
    font.setWeight(QFont.Weight(400))
    font.setItalic(False)
    if hasattr(font, "setFeature") and hasattr(QFont, "Tag"):
        font.setFeature(QFont.Tag("tnum"), 1)
    return font


def color(theme: Theme, role: str) -> QColor:
    """A token, or a state hue as a local row fill, by role name."""
    token = getattr(theme, role, None)
    if token is None:
        raise KeyError(f"{role!r} is not a theme token")
    value = QColor(token)
    if role in _STATE_ROLE:
        value.setAlphaF(LOCAL_FILL_ALPHA)
    return value


def state_colors(theme: Theme, state: State) -> tuple[QColor, QColor]:
    """The badge fill and ink for one state. Every state reads differently."""
    fill, ink = BADGES[state][1 if theme.mode == MODE_DARK else 0]
    return QColor(fill), QColor(ink)


def state_marker(theme: Theme, state: State) -> QPen:
    """The shape channel: the marker geometry, never the hue, carries the state."""
    pen = QPen(QColor(getattr(theme, _STATE_TOKEN[state])))
    marker = status.presentation(state).marker
    if marker == "none":
        pen.setStyle(Qt.PenStyle.NoPen)
    elif marker == "solid":
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(2)
    elif marker == "dashed":
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(2)
    elif marker == "block":
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(4)
    elif marker == "double":
        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setWidth(1)
        pen.setDashPattern([2, 1, 2, 3])
    else:
        pen.setStyle(Qt.PenStyle.DotLine)
        pen.setWidth(1)
    return pen


def icon(name: str, ink: str | None = None) -> QIcon:
    """A bundled Tabler outline icon, recoloured, or a null QIcon.

    The bundled SVGs carry `stroke="currentColor"`, and Qt's SVG renderer does not
    resolve that: loaded straight from the file, every icon paints BLACK, which is
    invisible on the dark theme and the wrong ink on the light one. The stroke is
    substituted here and the icon is rendered at 1x and 2x. Pass `ink` to match the
    surface the icon lands on; the default is the active theme's primary text. A
    missing icon is a null QIcon, so the glyph channel carries the state.
    """
    chosen = ink or active_theme().text_primary
    key = f"{name}@{chosen}"
    if key not in _ICON_CACHE:
        path = _icon_directory() / f"{name}.svg"
        _ICON_CACHE[key] = _render_icon(path, chosen) if path.is_file() else QIcon()
    return _ICON_CACHE[key]


def _render_icon(path: Path, ink: str) -> QIcon:
    svg = path.read_text(encoding="utf-8").replace("currentColor", ink).encode("utf-8")
    try:
        from PySide6.QtSvg import QSvgRenderer
    except ImportError:
        # Without the SVG plugin this still paints, in the wrong ink; the packaging
        # gate is what proves the plugin travels with a frozen build.
        return QIcon(str(path))
    renderer = QSvgRenderer(QByteArray(svg))
    result = QIcon()
    base = _ICON_PIXEL_SIZES[0]
    for size in _ICON_PIXEL_SIZES:
        image = QImage(size, size, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        image.setDevicePixelRatio(size / base)
        result.addPixmap(QPixmap.fromImage(image))
    return result


# --- the painting helpers three lanes share ----------------------------------


def paint_row_background(painter: QPainter, option, theme: Theme) -> None:
    """One row's own fill, plus the accent indicator that survives a colour check.

    The selection fill is the spec's; the 2 px accent bar at the left edge is
    Nothing's, and it is why the selection is still readable to a reader who cannot
    separate the selection hue from the surface.
    """
    state = QStyle.StateFlag
    rect = option.rect
    if option.state & state.State_Selected:
        painter.fillRect(rect, QColor(theme.selection))
        width = active_metrics().pad_xs
        painter.fillRect(QRect(rect.left(), rect.top(), width, rect.height()),
                         QColor(theme.accent))
    elif option.state & state.State_MouseOver:
        painter.fillRect(rect, QColor(theme.surface_raised))


def paint_divider(painter: QPainter, rect: QRect, theme: Theme) -> None:
    """One full-width 1 px content divider at the bottom of `rect`."""
    painter.fillRect(QRect(rect.left(), rect.bottom(), rect.width(), 1),
                     QColor(theme.divider))


def paint_focus_edge(painter: QPainter, rect: QRect, theme: Theme) -> None:
    """The 2 px focus ring. Drawn instantly, never animated, never removed."""
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor(theme.focus), 2))
    painter.drawRect(rect.adjusted(1, 1, -1, -1))
    painter.restore()

def paint_marker(painter: QPainter, rect: QRect, marker: str, pen: QPen) -> None:
    """The shape channel: the same state reads without any colour at all."""
    height = rect.height() - 6
    if height <= 0 or marker == "none" or pen.style() == Qt.PenStyle.NoPen:
        return
    left, top = rect.left() + 2, rect.top() + 3
    if marker == "block":
        painter.fillRect(QRect(left, top, 8, 8), pen.color())
        return
    if marker == "double":
        painter.fillRect(QRect(left, top, 2, height), pen.color())
        painter.fillRect(QRect(left + 4, top, 2, height), pen.color())
        return
    if marker == "dashed":
        third = max(2, height // 3)
        painter.fillRect(QRect(left, top, 3, third), pen.color())
        painter.fillRect(QRect(left, top + height - third, 3, third), pen.color())
        return
    painter.fillRect(QRect(left, top, 3, height), pen.color())


def paint_badge(painter: QPainter, rect: QRect, fill: QColor, ink: QColor,
                icon_name: str, word: str) -> None:
    """A state badge: its fill, its icon and its word. The word is never dropped.

    The icon is the second channel beside the word, never instead of it.
    """
    shape = active_metrics()
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(fill)
    painter.drawRoundedRect(rect, shape.radius, shape.radius)
    painter.setPen(ink)
    left = rect.left() + shape.pad_sm
    art = icon(icon_name, ink.name())
    if not art.isNull():
        painter.drawPixmap(QRect(left, rect.top() + max(0, (rect.height() - 16) // 2), 16, 16),
                           art.pixmap(16, 16))
        left += 16 + shape.pad_sm
    text_rect = QRect(left, rect.top(), max(0, rect.right() - left - shape.pad_sm),
                      rect.height())
    painter.setFont(type_scale().strong)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                     painter.fontMetrics().elidedText(word, Qt.TextElideMode.ElideRight,
                                                      text_rect.width()))
    painter.restore()


def paint_segments(painter: QPainter, rect: QRect, total: int, filled: int, theme: Theme,
                   accent: bool = False, over: bool = False) -> None:
    """The length meter: `filled` of `total` square-ended discrete blocks.

    No track behind the blocks and no radius, and the gap is always 2 px. When
    `over` is true the blocks past `total` change SHAPE, not only colour: they rise
    and take a cap mark, so a value past the limit is readable in grayscale.
    """
    if total <= 0 or rect.width() <= 0 or rect.height() <= 0:
        return
    shape = active_metrics()
    drawn = max(0, filled)
    # A value past the limit grows the count, so the block width shrinks to keep
    # every block inside `rect` and to keep the run of blocks an honest proportion.
    columns = max(total, drawn)
    step = rect.width() / columns
    width = max(1, int(step) - shape.pad_xs)
    for index in range(min(drawn, total)):
        painter.fillRect(QRect(rect.left() + int(index * step), rect.top(), width,
                               rect.height()),
                         QColor(theme.accent if accent else theme.text_primary))
    if drawn > total:
        # The blocks the value runs past change SHAPE, not only colour: the body
        # sits lower and takes a cap mark, so the overflow reads in grayscale.
        for index in range(total, drawn):
            left = rect.left() + int(index * step)
            height = max(1, rect.height() - shape.pad_xs)
            painter.fillRect(QRect(left, rect.top() + shape.pad_xs, width, height),
                             QColor(theme.accent))
            painter.fillRect(QRect(left, rect.top() + shape.pad_xs - 1, width, 1),
                             QColor(theme.accent))


# --- the stylesheet -----------------------------------------------------------

def app_stylesheet(theme: Theme) -> str:
    """Object-name and dynamic-property hooks only; every colour is a theme token."""
    shape = active_metrics()
    check = _icon_uri("check", theme.text_primary)
    rules = [
        f'QLabel[role="heading"] {{ color: {theme.text_primary}; font-weight: 600; }}',
        f'QLabel[role="sectionLabel"] {{ color: {theme.text_primary}; font-weight: 600; }}',
        f'QLabel[role="hint"] {{ color: {theme.text_secondary}; }}',
        f'QLabel[role="caption"] {{ color: {theme.text_secondary}; }}',
        f'QLabel[role="mono"] {{ color: {theme.text_secondary}; '
        f'font-family: "{mono_font().family()}"; }}',
        f'QLabel[role="disabled"] {{ color: {theme.text_disabled}; }}',
        f'QWidget[role="editorHeader"] {{ background: {theme.surface_raised}; '
        f"border-bottom: 1px solid {theme.divider}; }}",
        f'QWidget[role="paneRule"] {{ border-top: 1px solid {theme.divider}; }}',
        f'QWidget[role="viewport"] {{ background: {theme.window}; '
        f"border: 1px solid {theme.border}; }}",
        f'QToolButton[filterChip="true"] {{ background: {theme.surface_raised}; '
        f"border: 1px solid {theme.border}; border-radius: {shape.radius}px; "
        f"padding: 0 {shape.pad_md}px; }}",
        f'QToolButton[filterChip="true"]:hover {{ border-color: {theme.accent}; }}',
        f'QToolButton[filterChip="true"]:checked {{ background: {theme.selection}; '
        f"border-color: {theme.accent}; }}",
    ]
    if check:
        rules.append(f'QToolButton[filterChip="true"]:checked {{ image: url({check}); }}')
    rules += [
        f"QStatusBar {{ background: {theme.surface_raised}; "
        f"border-top: 1px solid {theme.divider}; }}",
        "QStatusBar::item { border: none; }",
        f"QSplitter::handle {{ background: {theme.splitter}; }}",
        "QSplitter::handle:horizontal { width: 5px; }",
        "QSplitter::handle:vertical { height: 5px; }",
        f"QTabBar::tab:selected {{ color: {theme.text_primary}; font-weight: 600; }}",
        f"QTabBar::tab:!selected {{ color: {theme.text_secondary}; }}",
        f"QTableView {{ gridline-color: {theme.divider}; }}",
        f"QHeaderView::section {{ background: {theme.surface_raised}; "
        f"color: {theme.text_secondary}; border: none; "
        f"border-right: 1px solid {theme.divider}; "
        f"border-bottom: 1px solid {theme.divider}; padding: 0 {shape.pad_md}px; }}",
    ]
    rules += _control_rules(theme, shape)
    return "\n".join(rules)


def _control_rules(theme: Theme, shape) -> list[str]:
    """Every class Qt draws with its own fallback ink, named and given a token.

    Measured, and the reason this function exists: with a stylesheet installed but no
    rule naming it, an unstyled QComboBox or QMenuBar is painted with ink that is not
    the theme's. In the light theme the menu bar, the four combo boxes and the address
    disclosure rendered as white on a `#F3F4F6` window, which measures about 1.1 to 1,
    and the same widgets in the dark theme rendered correctly, so the defect is
    invisible in a dark pass. Naming each class and giving it a token removes the
    dependency on that fallback entirely, which is what the design note already
    requires of every surface: the theme decides, not Qt's default.
    """
    arrow = _icon_uri("chevron-down", theme.text_primary)
    field = (f"background: {theme.surface}; color: {theme.text_primary}; "
             f"border: 1px solid {theme.border}; border-radius: {shape.radius}px; "
             f"padding: 0 {shape.pad_md}px; min-height: {shape.field_height - 2}px;")
    item = (f"background: {theme.surface_raised}; color: {theme.text_primary}; "
            f"padding: {shape.pad_sm}px {shape.pad_lg}px;")
    button = (f"color: {theme.text_primary}; background: {theme.surface_raised}; "
              f"border: 1px solid {theme.border}; border-radius: {shape.radius}px; "
              f"padding: 0 {shape.pad_lg}px; min-height: {shape.field_height - 2}px;")
    return [
        # Text entry, including the search field and the rename dialog's two fields.
        f"QLineEdit {{ {field} }}",
        f"QLineEdit:focus {{ border-color: {theme.focus}; }}",
        f"QLineEdit:disabled {{ color: {theme.text_disabled}; }}",
        # The combo boxes that reshape the list, and the speaker filter.
        f"QComboBox {{ {field} }}",
        f"QComboBox:focus {{ border-color: {theme.focus}; }}",
        f"QComboBox:disabled {{ color: {theme.text_disabled}; }}",
        f"QComboBox::drop-down {{ border: none; "
        f"width: {shape.pad_xl + shape.pad_md}px; subcontrol-origin: padding; "
        f"subcontrol-position: center right; }}",
    ] + ([f"QComboBox::down-arrow {{ image: url({arrow}); width: 12px; height: 12px; }}"]
         if arrow else []) + [
        f"QComboBox QAbstractItemView {{ background: {theme.surface_raised}; "
        f"color: {theme.text_primary}; border: 1px solid {theme.border}; "
        f"selection-background-color: {theme.selection}; "
        f"selection-color: {theme.text_primary}; }}",
        # The menu bar and its menus.
        f"QMenuBar {{ background: {theme.window}; color: {theme.text_primary}; }}",
        f"QMenuBar::item {{ background: transparent; color: {theme.text_primary}; "
        f"padding: {shape.pad_xs}px {shape.pad_md}px; }}",
        f"QMenuBar::item:selected {{ background: {theme.selection}; }}",
        f"QMenu {{ background: {theme.surface_raised}; color: {theme.text_primary}; "
        f"border: 1px solid {theme.border}; }}",
        f"QMenu::item {{ {item} }}",
        f"QMenu::item:selected {{ background: {theme.selection}; }}",
        f"QMenu::item:disabled {{ color: {theme.text_disabled}; }}",
        f"QMenu::separator {{ height: 1px; background: {theme.divider}; "
        f"margin: {shape.pad_sm}px 0; }}",
        # A plain tool button: the address disclosure, and the notice's two buttons.
        # Transparent, so an inline disclosure reads as text rather than as another box.
        f"QToolButton {{ color: {theme.text_primary}; background: transparent; "
        f"border: 1px solid transparent; border-radius: {shape.radius}px; "
        f"padding: 0 {shape.pad_md}px; min-height: {shape.field_height - 2}px; }}",
        f"QToolButton:hover {{ border-color: {theme.accent}; }}",
        f"QToolButton:disabled {{ color: {theme.text_disabled}; }}",
        # A plain push button: the dialogs, and any action without its own role.
        f"QPushButton {{ {button} }}",
        f"QPushButton:hover {{ border-color: {theme.accent}; }}",
        f"QPushButton:disabled {{ color: {theme.text_disabled}; }}",
        f'QPushButton[role="primary"] {{ background: {theme.accent}; '
        f"color: {theme.accent_ink}; border-color: {theme.accent}; }}",
        # Dialog surfaces and the tab strip's own fills, which Qt otherwise invents.
        f"QDialog {{ background: {theme.window}; }}",
        f"QTabBar::tab {{ background: transparent; }}",
        f"QTabBar::tab:selected {{ background: {theme.surface_raised}; "
        f"border-bottom: 2px solid {theme.accent}; }}",
        f"QToolTip {{ background: {theme.surface_raised}; color: {theme.text_primary}; "
        f"border: 1px solid {theme.divider}; }}",
        # The scrollbar keeps Qt's own drawing on purpose. Styling it with a background
        # and a handle left the sub-page area unpainted, which renders as a 1 px
        # checkerboard down the track where Qt draws nothing at all. The palette is
        # correct, so the base style already draws it in the theme's own colours.
    ]


#: role name -> the token it resolves to, for the five state hues.
_STATE_ROLE = {
    "state_unchanged", "state_edited", "state_move", "state_refused", "state_base_changed",
}

#: The state's hue token. The words differ: WILL_MOVE reads as "state_move".
_STATE_TOKEN = {
    State.UNCHANGED: "state_unchanged",
    State.EDITED: "state_edited",
    State.WILL_MOVE: "state_move",
    State.REFUSED: "state_refused",
    State.BASE_CHANGED: "state_base_changed",
}


def _system_is_dark(app: QApplication) -> bool:
    hints = app.styleHints()
    scheme = hints.colorScheme() if hasattr(hints, "colorScheme") else None
    return scheme == Qt.ColorScheme.Dark


def _icon_directory() -> Path:
    bundle = getattr(sys, "_MEIPASS", None)
    base = Path(bundle) if bundle else Path(__file__).resolve().parent
    return base / "icons"


def _icon_uri(name: str, ink: str) -> str:
    """A stylesheet `url()` for one icon, recoloured into `ink`.

    Measured, and this is why the icon is written to a file rather than inlined: a
    base64 data URI is accepted by Qt's stylesheet parser and then paints NOTHING,
    silently and with no warning. The check glyph on a checked filter chip is the
    channel the owner reads a state by, and it had never appeared. A file path paints:
    the same rule returned 40 ink pixels for a data URI, which is only the button's own
    text, and 100 for a path. The recoloured copies live in one temporary directory for
    the life of the run and are never committed.
    """
    path = _icon_directory() / f"{name}.svg"
    if not path.is_file():
        return ""
    svg = path.read_text(encoding="utf-8").replace("currentColor", ink)
    target = _icon_cache() / f"{name}-{ink.lstrip('#')}.svg"
    if not target.is_file():
        target.write_text(svg, encoding="utf-8")
    return target.as_posix()


def _icon_cache() -> Path:
    """One directory for the recoloured copies, created on first use."""
    global _ICON_FILES
    if _ICON_FILES is None or not _ICON_FILES.is_dir():
        _ICON_FILES = Path(tempfile.mkdtemp(prefix="buufury-icons-"))
    return _ICON_FILES


def theme_tokens(theme: Theme) -> Mapping[str, str]:
    """Every resolved token of one theme, for a test that greps for stray hex."""
    return asdict(theme)
