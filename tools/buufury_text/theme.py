"""The one place a colour, a font or a metric is decided.

Every token value in this module comes from the Cartridge Workbench table. A
widget that carried its own colour would be a second theme, so nothing outside
this file holds a hex value.

The look is Fusion + QPalette + a thin QProxyStyle + delegates; the stylesheet is
deliberately small and carries only object-name and dynamic-property hooks.
"""

from __future__ import annotations

import base64
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from PySide6.QtCore import QByteArray, Qt
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
TOKENS: dict[str, tuple[str, str]] = {
    "window": ("#F3F4F6", "#17191D"),
    "surface": ("#FFFFFF", "#1E2126"),
    "surface_raised": ("#F8F9FB", "#252931"),
    "text_primary": ("#20242A", "#EEF1F4"),
    "text_secondary": ("#5D6672", "#AEB6C0"),
    "border": ("#C7CDD5", "#414852"),
    "splitter": ("#77808A", "#6F7883"),
    "accent": ("#235FAE", "#7DB0FF"),
    "selection": ("#D8E8FF", "#243B5A"),
    "focus": ("#1F6FEB", "#8BB9FF"),
    "state_unchanged": ("#6B7280", "#9AA3AE"),
    "state_edited": ("#1F64C8", "#83B8FF"),
    "state_move": ("#8A5A00", "#F1BE5C"),
    "state_refused": ("#7A2E8A", "#E59AEF"),
    "state_base_changed": ("#5A4FB5", "#B7A9FF"),
    # The dialogue preview is the one surface that shows the GAME rather than the
    # application, so its four tokens are the same in both modes: a dark viewport
    # and the light box the game draws in it.
    "preview_screen": ("#0B0F14", "#0B0F14"),
    "preview_box": ("#F8F8F8", "#F8F8F8"),
    "preview_ink": ("#101418", "#101418"),
    "preview_marker": ("#8A8F96", "#8A8F96"),
}

#: Badge fill and ink, light then dark. The table names four of the five states.
#: UNCHANGED is the quiet one, so it borrows the unchanged hue for its ink and the
#: raised surface for its fill rather than inventing a value.
BADGES: dict[State, tuple[tuple[str, str], tuple[str, str]]] = {
    State.UNCHANGED: (("#F8F9FB", "#6B7280"), ("#252931", "#9AA3AE")),
    State.EDITED: (("#E7F0FD", "#1F5CA8"), ("#28476A", "#DCEAFF")),
    State.WILL_MOVE: (("#FFF0C2", "#5C4000"), ("#F1BE5C", "#201B12")),
    State.REFUSED: (("#513457", "#FFFFFF"), ("#5D3A66", "#FFFFFF")),
    State.BASE_CHANGED: (("#EEEAFB", "#4B4098"), ("#3C355E", "#E2DDFF")),
}

#: A row fill is legible only if it is nearly the surface it sits on.
LOCAL_FILL_ALPHA = 0.24

_MONO_PREFERENCE = ("Cascadia Mono", "Consolas")
_FAMILIES: frozenset[str] = frozenset()
_ICON_CACHE: dict[str, QIcon] = {}


@dataclass(frozen=True, slots=True)
class Metrics:
    """Density derived from the application font, never from a frozen pixel."""

    row_height: int
    field_height: int
    chip_height: int
    header_height: int
    status_height: int
    pad: int
    gap: int
    radius: int


@dataclass(frozen=True, slots=True)
class Theme:
    """One resolved mode. `mode` is light or dark, never system."""

    mode: str
    window: str
    surface: str
    surface_raised: str
    text_primary: str
    text_secondary: str
    border: str
    splitter: str
    accent: str
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


_FALLBACK = Theme(
    mode=MODE_DARK, window="#17191D", surface="#1E2126", surface_raised="#252931",
    text_primary="#EEF1F4", text_secondary="#AEB6C0", border="#414852",
    splitter="#6F7883", accent="#7DB0FF", selection="#243B5A", focus="#8BB9FF",
    state_unchanged="#9AA3AE", state_edited="#83B8FF", state_move="#F1BE5C",
    state_refused="#E59AEF", state_base_changed="#B7A9FF",
    preview_screen="#0B0F14", preview_box="#F8F8F8", preview_ink="#101418",
    preview_marker="#8A8F96",
)

_ACTIVE = _FALLBACK
_SHAPE: Metrics | None = None
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
        palette.setColor(group.Disabled, disabled, QColor(theme.border))
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

    def _font_height(self) -> int:
        app = self._app if self._app is not None else QApplication.instance()
        return max(10, QFontMetrics(app.font()).height())

    def pixelMetric(self, metric, option=None, widget=None) -> int:  # noqa: N802
        shape = self._shape()
        name = QStyle.PixelMetric
        if metric == name.PM_DefaultFrameWidth:
            return 1
        if metric in (name.PM_SmallIconSize, name.PM_ToolBarIconSize):
            return 16
        if metric == name.PM_ScrollBarExtent:
            return min(16, max(12, self._font_height()))
        if metric in (name.PM_LayoutLeftMargin, name.PM_LayoutRightMargin,
                      name.PM_LayoutTopMargin, name.PM_LayoutBottomMargin):
            return shape.pad
        if metric in (name.PM_LayoutHorizontalSpacing, name.PM_LayoutVerticalSpacing):
            return shape.gap
        return super().pixelMetric(metric, option, widget)

    def sizeFromContents(self, contents_type, option, size, widget=None):  # noqa: N802
        shape = self._shape()
        kind = QStyle.ContentsType
        if contents_type == kind.CT_PushButton:
            size.setHeight(max(size.height(), shape.field_height))
        elif contents_type == kind.CT_ToolButton:
            size.setHeight(max(size.height(), shape.field_height, 16))
        elif contents_type in (kind.CT_LineEdit, kind.CT_ComboBox):
            size.setHeight(max(size.height(), shape.field_height))
        return super().sizeFromContents(contents_type, option, size, widget)

    def drawPrimitive(self, element, option, painter, widget=None) -> None:  # noqa: N802
        if element == QStyle.PrimitiveElement.PE_FrameFocusRect:
            # Focus is a 2 px ring and is never removed.
            painter.save()
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(_ACTIVE.focus), 2))
            painter.drawRect(option.rect.adjusted(1, 1, -1, -1))
            painter.restore()
            return
        super().drawPrimitive(element, option, painter, widget)


def apply_theme(app: QApplication, mode: str = MODE_SYSTEM) -> Theme:
    """Install Fusion under the proxy style, the palette and the small stylesheet."""
    global _ACTIVE, _FAMILIES, _SHAPE, _PROXY
    _FAMILIES = frozenset(QFontDatabase.families())
    theme = theme_for(mode, _system_is_dark(app))
    _ACTIVE = theme
    _SHAPE = metrics(app)
    proxy = EditorProxyStyle(_SHAPE, app)
    proxy.setBaseStyle(QStyleFactory.create("Fusion"))
    app.setStyle(proxy)
    app.setPalette(build_palette(theme))
    app.setStyleSheet(app_stylesheet(theme))
    _PROXY = proxy
    return theme


def metrics(app: QApplication | None = None) -> Metrics:
    """Row, field and chip heights derived from the application font."""
    global _SHAPE
    app = app if app is not None else QApplication.instance()
    if app is None:
        return _SHAPE if _SHAPE is not None else Metrics(30, 28, 22, 26, 26, 6, 6, 3)
    text_height = QFontMetrics(app.font()).height()
    shape = Metrics(
        row_height=max(30, text_height + 12),
        field_height=max(28, text_height + 10),
        chip_height=max(22, text_height + 6),
        header_height=26,
        status_height=26,
        pad=6,
        gap=6,
        radius=3,
    )
    _SHAPE = shape
    return shape


def active_theme() -> Theme:
    """The theme `apply_theme` installed, for painting code that has no app."""
    return _ACTIVE


def active_metrics() -> Metrics:
    """The shape `apply_theme` installed, for painting code that has no app."""
    return _SHAPE if _SHAPE is not None else metrics()


def proxy_style() -> EditorProxyStyle | None:
    """The proxy style `apply_theme` installed, or None before it ran."""
    return _PROXY


def color(theme: Theme, role: str) -> QColor:
    """A token, or the state hue as a local fill, by role name."""
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


#: The two pixel sizes one icon is rendered at, so a 2x display gets a real 2x
#: pixmap rather than a scaled 1x one.
_ICON_PIXEL_SIZES = (16, 32)


def icon(name: str, ink: str | None = None) -> QIcon:
    """A bundled Tabler outline icon, recoloured, or a null QIcon.

    The bundled SVGs carry `stroke="currentColor"`, and Qt's SVG renderer does not
    resolve that: loaded straight from the file, every icon paints BLACK, which is
    invisible on the dark theme and the wrong ink on the light one. The stroke is
    substituted here and the icon is rendered at both pixel sizes. Pass `ink` to
    match the surface the icon lands on; the default is the active theme's primary
    text. A missing icon is a null QIcon, so the glyph channel carries the state.
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


def mono_font(delta: int = -1) -> QFont:
    """Cascadia Mono then Consolas, else the system fixed font, resized by delta.

    Tabular figures are declared rather than inherited: the length meter rewrites
    its numbers on every keystroke, and proportional digits would shift the layout
    under the reader while they type.
    """
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    families = _FAMILIES or frozenset(QFontDatabase.families())
    for family in _MONO_PREFERENCE:
        if family in families:
            font.setFamily(family)
            break
    font.setPointSize(max(1, font.pointSize() + delta))
    if hasattr(font, "setFeature") and hasattr(QFont, "Tag"):
        font.setFeature(QFont.Tag("tnum"), 1)
    return font


def app_stylesheet(theme: Theme) -> str:
    """Object-name and dynamic-property hooks only; every colour is a theme token."""
    shape = metrics()
    check = _icon_uri("check", theme.text_primary)
    rules = [
        f'QLabel[role="heading"], QLabel[role="sectionLabel"] '
        f"{{ color: {theme.text_primary}; font-weight: 600; }}",
        f'QLabel[role="hint"], QLabel[role="caption"] {{ color: {theme.text_secondary}; }}',
        f'QLabel[role="mono"] {{ color: {theme.text_secondary}; '
        f'font-family: "{mono_font().family()}"; }}',
        f'QWidget[role="editorHeader"] {{ background: {theme.surface_raised}; '
        f"border-bottom: 1px solid {theme.border}; }}",
        f'QWidget[role="paneRule"] {{ border-top: 1px solid {theme.border}; }}',
        f'QWidget[role="viewport"] {{ background: {theme.window}; '
        f"border: 1px solid {theme.border}; }}",
        f'QToolButton[filterChip="true"] {{ background: {theme.surface_raised}; '
        f"border: 1px solid {theme.border}; border-radius: {shape.radius}px; "
        f"padding: 0 8px; }}",
        f'QToolButton[filterChip="true"]:hover {{ border-color: {theme.accent}; }}',
        f'QToolButton[filterChip="true"]:checked {{ background: {theme.selection}; '
        f"border-color: {theme.accent}; }}",
    ]
    if check:
        rules.append(f'QToolButton[filterChip="true"]:checked {{ image: url({check}); }}')
    rules += [
        f"QStatusBar {{ background: {theme.surface_raised}; "
        f"border-top: 1px solid {theme.border}; }}",
        "QStatusBar::item { border: none; }",
        f"QSplitter::handle {{ background: {theme.splitter}; }}",
        "QSplitter::handle:horizontal { width: 5px; }",
        "QSplitter::handle:vertical { height: 5px; }",
        f"QTabBar::tab:selected {{ color: {theme.text_primary}; font-weight: 600; }}",
        f"QTabBar::tab:!selected {{ color: {theme.text_secondary}; }}",
        f"QTableView {{ gridline-color: {theme.border}; }}",
        f"QHeaderView::section {{ background: {theme.surface_raised}; "
        f"color: {theme.text_secondary}; border: none; "
        f"border-right: 1px solid {theme.border}; "
        f"border-bottom: 1px solid {theme.border}; padding: 0 6px; }}",
    ]
    return "\n".join(rules)


#: role name -> the state hue it resolves to, and the state whose marker uses it.
_STATE_ROLE = {
    "state_unchanged": lambda theme: theme.state_unchanged,
    "state_edited": lambda theme: theme.state_edited,
    "state_move": lambda theme: theme.state_move,
    "state_refused": lambda theme: theme.state_refused,
    "state_base_changed": lambda theme: theme.state_base_changed,
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
    path = _icon_directory() / f"{name}.svg"
    if not path.is_file():
        return ""
    svg = path.read_text(encoding="utf-8").replace("currentColor", ink)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def theme_tokens(theme: Theme) -> Mapping[str, str]:
    """Every resolved token of one theme, for a test that greps for stray hex."""
    return asdict(theme)
