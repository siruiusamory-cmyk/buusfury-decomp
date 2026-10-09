"""The one theme: every colour literal, spacing value and state glyph.

**Where the palette comes from.** It is derived from *Buu's own in-game sprite*
rather than from a stock theme, and the provenance is recorded in
``docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md``. The four-step pink ladder is
the product identity: large quiet areas take the lightest step, chrome the next,
interaction the strong step, and small high-contrast edges and text the deepest.

**One theme, one stylesheet.** The values live here and nowhere else; a widget
that carried its own colour would be a second theme. :func:`apply_theme` is
called once from the application entry point, and the style sheet covers the
chrome the window actually renders rather than a speculative widget inventory.

**State is never colour alone.** Every status role also carries a glyph as well
as a brightness difference (:func:`status_glyph`), and no surface may express a
state by hue by itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication

#: The pink ladder's four values, named once so the role fields below alias them
#: rather than restating a literal.
PINK_SOFT = "#f2ccdf"
PINK_MID = "#eebfd6"
PINK_STRONG = "#a81560"
PINK_DEEP = "#6d0c3c"

#: One spacing scale. Every margin in the window is one of these.
SPACE_XS = 2
SPACE_SM = 4
SPACE_MD = 8
SPACE_LG = 12
SPACE_XL = 16

#: Small radii: a large one reads as a web card rather than a desktop tool.
RADIUS_INPUT = 3
RADIUS_BUTTON = 2

#: Control geometry. One row height everywhere a list or field appears.
ROW_HEIGHT = 20
#: The height an action control is drawn at. The style sheet derives the height
#: from the button metrics, and a control that sets its own smaller minimum
#: instead comes out visibly lighter than the buttons beside it.
CONTROL_HEIGHT = 24
TOOLBAR_HEIGHT = 28
PANEL_HEADER_HEIGHT = 22
STATUS_HEIGHT = 22

#: The inspector's default width and its floor.
INSPECTOR_WIDTH = 320
INSPECTOR_MIN_WIDTH = 260


@dataclass(frozen=True, slots=True)
class Palette:
    """The semantic colour roles this window renders."""

    # -- the pink ladder: the product identity -------------------------------
    #: Step 1 - the widest, quietest pink: the application background.
    pink_soft: str = PINK_SOFT
    #: Step 2 - chrome: the menu bar, the action bar, the strip and the status bar.
    pink_mid: str = PINK_MID
    #: Step 3 - interaction: the active destination, selection, focus.
    pink_strong: str = PINK_STRONG
    #: Step 4 - the deepest magenta: small high-contrast edges and text.
    pink_deep: str = PINK_DEEP

    # -- surfaces: the sprite's white mantle as the work surfaces ------------
    #: The application background. The same value as `pink_soft`, one role each.
    background: str = PINK_SOFT
    #: The shell's mid step. The same value as `pink_mid`.
    chrome: str = PINK_MID
    #: The main work surface, one step off white so the pink shell frames it.
    surface: str = "#fdfbfc"
    #: Sidebars, the inspector, tool areas: the pure mantle white.
    surface_raised: str = "#ffffff"
    #: Inputs and editable rows: the border is what separates a field.
    surface_input: str = "#ffffff"

    # -- borders: the sprite's outline ramp, kept light ----------------------
    #: Quiet separators inside one panel.
    border: str = "#e4d2db"
    #: Region boundaries and the boundary between a panel and the pink shell.
    border_strong: str = "#cbadbc"

    # -- text: the sprite's outline, expanded into a type ramp ---------------
    text_primary: str = "#2a2229"
    text_secondary: str = "#5c525a"
    #: Technical and recessive text, never a primary label.
    text_muted: str = "#756970"
    #: Clearly disabled, and still legible.
    text_disabled: str = "#938990"

    # -- the primary identity: the sprite's pink-magenta ---------------------
    accent: str = PINK_STRONG
    accent_hover: str = "#930f53"
    accent_pressed: str = PINK_DEEP
    #: A tinted ground for an active control, so it reads as active by value as
    #: well as by hue.
    accent_ground: str = "#f7dbe8"
    #: Text drawn on a solid accent fill.
    accent_ink: str = "#ffffff"

    # -- interaction ---------------------------------------------------------
    #: Pointer hover on a neutral white control.
    hover: str = "#fbeef4"
    #: A selected row or item. Stronger than the chrome on purpose: the pale
    #: pink shell must never be mistaken for a selection.
    selection: str = "#f2b3d0"
    #: The edge that marks a selection, so selection is not a fill alone.
    selection_edge: str = "#8f1350"
    #: The keyboard focus ring, drawn at 1 px AND in this colour.
    focus: str = "#c9186a"

    # -- semantic state ------------------------------------------------------
    #: Valid / safe / confirmed. The sprite carries no green: this is the one
    #: recorded exception, and the reason is in the colour-source document.
    success: str = "#1f7a3d"
    #: Pending / unsaved, from the sprite's gold belt.
    pending: str = "#8a5a00"
    #: Destructive / error, from the sprite's own eye red.
    danger: str = "#b3261e"


#: One instance; the palette is a value, not per-widget state.
COLORS = Palette()

#: The non-colour half of a status state. Every state is glyph plus word, so
#: removing colour leaves it readable.
_GLYPHS = {
    "success": "\u2713",  # check
    "valid": "\u2713",
    "saved": "\u2714",  # heavy check, for a completed write
    "warning": "\u25cf",  # filled circle
    "pending": "\u25cf",
    "error": "\u2717",  # ballot cross
    "invalid": "\u2717",
    "danger": "\u2717",
    "info": "\u2139",  # information
    "readonly": "\u2298",  # circled division slash
    "edit": "\u25b8",  # small triangle
    "neutral": "\u00b7",  # middle dot
}

#: Role -> the palette attribute that paints it. One table, so a caller names a
#: state and the theme resolves both its glyph and its colour.
STATE_COLORS = {
    "success": "success",
    "valid": "success",
    "saved": "success",
    "pending": "pending",
    "warning": "pending",
    "error": "danger",
    "invalid": "danger",
    "danger": "danger",
    "readonly": "text_muted",
    "edit": "accent",
    "info": "text_secondary",
    "neutral": "text_secondary",
}


def status_glyph(role: str) -> str:
    """The glyph for a status role, so callers render ``glyph + word``."""
    return _GLYPHS.get(role, _GLYPHS["neutral"])


def state_color(role: str) -> QColor:
    """The colour for a status role, resolved through :data:`STATE_COLORS`."""
    return color(STATE_COLORS.get(role, "text_secondary"))


def color(name: str) -> QColor:
    """The ``QColor`` for a palette role name."""
    return QColor(getattr(COLORS, name))


def mono_font(size_delta: int = -1) -> QFont:
    """The fixed-width face used for addresses, digests and technical identity.

    The platform's fixed font rather than a named family, so the application
    does not depend on a font being installed.
    """
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setPointSize(max(7, font.pointSize() + size_delta))
    return font


def apply_theme(app: QApplication) -> None:
    """Apply the palette and the one style sheet to a whole application.

    Called once from the entry point. Widgets must not carry their own style
    sheet afterwards: a per-surface sheet is how a window drifts away from the
    rest of the product.
    """
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, color("background"))
    palette.setColor(QPalette.ColorRole.WindowText, color("text_primary"))
    palette.setColor(QPalette.ColorRole.Base, color("surface_input"))
    palette.setColor(QPalette.ColorRole.AlternateBase, color("surface"))
    palette.setColor(QPalette.ColorRole.Text, color("text_primary"))
    palette.setColor(QPalette.ColorRole.Button, color("surface_raised"))
    palette.setColor(QPalette.ColorRole.ButtonText, color("text_primary"))
    palette.setColor(QPalette.ColorRole.Highlight, color("selection"))
    palette.setColor(QPalette.ColorRole.HighlightedText, color("text_primary"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, color("surface_raised"))
    palette.setColor(QPalette.ColorRole.ToolTipText, color("text_primary"))
    palette.setColor(QPalette.ColorRole.Link, color("accent"))
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        palette.setColor(QPalette.ColorGroup.Disabled, role, color("text_disabled"))
    app.setPalette(palette)
    app.setStyleSheet(stylesheet())


def stylesheet() -> str:
    """The one application style sheet, for the chrome this window renders."""
    c = COLORS
    mono = mono_font().family()
    return f"""
    QWidget, QMainWindow, QDialog {{
        background-color: {c.surface};
        color: {c.text_primary};
    }}
    QMainWindow, QDialog {{ background-color: {c.background}; }}
    QStackedWidget, QSplitter, QScrollArea, QAbstractScrollArea, QFrame {{
        background-color: {c.surface};
    }}

    /* The top shell reads as one band: chrome one value below the application
       background, its parts separated by hairlines. */
    QMenuBar, QToolBar, QStatusBar {{
        background-color: {c.chrome};
        color: {c.text_primary};
    }}
    QMenuBar {{ border-bottom: 1px solid {c.border}; padding: 0px; }}
    QMenuBar::item {{ padding: 4px 10px; background: transparent; }}
    QMenuBar::item:selected {{ background-color: {c.selection}; }}
    QMenu::item:disabled {{ color: {c.text_disabled}; }}

    QToolBar#actionBar, QToolBar#destinationStrip {{
        border-bottom: 1px solid {c.border};
        spacing: {SPACE_SM}px;
        padding: 2px 6px;
        min-height: {TOOLBAR_HEIGHT}px;
    }}
    QToolBar::separator {{ background: {c.border_strong}; width: 1px; margin: 4px 6px; }}
    /* The expanding gap between two groups of toolbar controls is a spacer, not
       a panel: the blanket QWidget rule would paint it as an opaque slab sitting
       in the middle of the chrome band. */
    QWidget#toolbarSpacer {{ background: transparent; }}

    QToolButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: {RADIUS_BUTTON}px;
        padding: 3px 8px;
        color: {c.text_secondary};
    }}
    QToolButton:hover {{
        background-color: {c.hover};
        border-color: {c.border_strong};
        color: {c.text_primary};
    }}
    QToolButton:focus {{ border-color: {c.focus}; }}
    /* The active destination: a tinted ground, a strong edge AND bold, so it is
       never marked by colour alone. */
    QToolButton:checked {{
        background-color: {c.accent_ground};
        color: {c.accent};
        border-color: {c.selection_edge};
        font-weight: bold;
    }}
    QToolButton:disabled {{ color: {c.text_disabled}; }}
    QToolButton::menu-indicator {{ width: 0px; }}

    QLabel {{ background: transparent; }}
    /* The inspector is a raised panel beside the work surface, with one hairline
       between them, so the pane and the centre read as two regions. */
    QWidget#inspectorPane {{ background-color: {c.surface_raised}; }}
    /* A panel header is a raised strip with hairline rules and neutral text: a
       heading is not an accent. */
    QLabel[dbzRole="panelHeader"] {{
        background-color: {c.surface_raised};
        border-top: 1px solid {c.border};
        border-bottom: 1px solid {c.border};
        color: {c.text_primary};
        padding: 2px 6px;
        min-height: {PANEL_HEADER_HEIGHT}px;
        font-weight: bold;
    }}
    QLabel[dbzRole="hint"] {{ color: {c.text_secondary}; }}
    /* Technical identity is the one place a fixed-width face belongs. */
    QLabel[dbzRole="technical"] {{
        color: {c.text_muted};
        font-family: "{mono}";
    }}
    QLabel[dbzRole="status"] {{ color: {c.text_secondary}; }}
    QLabel:disabled {{ color: {c.text_disabled}; }}

    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox {{
        background-color: {c.surface_input};
        border: 1px solid {c.border_strong};
        border-radius: {RADIUS_INPUT}px;
        padding: 2px 5px;
        color: {c.text_primary};
        selection-background-color: {c.selection};
        selection-color: {c.text_primary};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {c.focus};
    }}
    QLineEdit:disabled, QPlainTextEdit:disabled, QTextEdit:disabled,
    QComboBox:disabled {{
        color: {c.text_disabled};
        background-color: {c.surface};
        border-color: {c.border};
    }}

    QPushButton {{
        background-color: {c.surface_raised};
        border: 1px solid {c.border_strong};
        border-radius: {RADIUS_BUTTON}px;
        padding: 3px 10px;
        color: {c.text_primary};
    }}
    QPushButton:hover {{ background-color: {c.hover}; border-color: {c.text_muted}; }}
    QPushButton:pressed {{ background-color: {c.selection}; }}
    QPushButton:focus {{ border: 1px solid {c.focus}; }}
    QPushButton:disabled {{
        color: {c.text_disabled};
        background-color: {c.surface};
        border-color: {c.border};
    }}

    QSplitter::handle {{ background-color: {c.border}; }}
    QSplitter::handle:horizontal {{ width: 1px; }}
    QSplitter::handle:hover {{ background-color: {c.selection_edge}; }}

    QStatusBar {{
        background-color: {c.background};
        border-top: 1px solid {c.border};
        color: {c.text_secondary};
        min-height: {STATUS_HEIGHT}px;
    }}
    QStatusBar::item {{ border: none; }}
    QStatusBar QLabel {{ background: transparent; padding: 0px {SPACE_MD}px; }}

    QToolTip {{
        background-color: {c.surface_raised};
        color: {c.text_primary};
        border: 1px solid {c.border_strong};
        padding: 3px 5px;
    }}
    """
