"""DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001 - the one DragonByte Z theme.

**Where this palette comes from.** It is derived from *Buu's own in-game sprite*,
not from a generic theme, not from the game's maps, and not from Dragon Ball brand
colours. `docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md` records the sampling and
`tools/qa/buu_sprite_palette.py` reproduces it from ROM data alone. The canonical
source is graphic 903 (32x64) together with graphic 904 (64x64), the Majin Buu
actor sprite.

The sprite's own palette is pink skin (``#ff73b5``, ``#de5294``, ``#9c185a``),
white mantle and trousers (``#ffffff``, ``#dedede``, ``#c6c6c6``), a gold belt
(``#ffad00``, ``#ad4a00``), a red eye (``#c60000``) and a near-black outline
(``#000000``, ``#636363``). Every value below is a lightness/saturation
translation of one of those, so the hue relationships survive while the values
become editor-safe.

Three rules the colour direction set, and how this module meets them:

1. **Light / mid-light, not dark-first.** The sprite's white mantle family becomes
   the surfaces and its outline becomes the type ramp: familiar desktop-editor
   depth, tinted warm-cool rather than neutral grey.
2. **Identity from Buu's own hue, not from convention.** Buu's pink-magenta is the
   interaction family - active editor, active mode, selection, focus, primary
   action. There is no conventional desktop blue anywhere in this file. Buu's gold
   belt is the secondary accent, spent only on authored content and brand detail.
3. **Neutrals trace to the sprite too.** Text and borders come from the sprite's
   own outline and mid-grey ramp, so removing the game artwork still leaves a
   palette that is not any stock UI's.

Two constraints learned from the reference set remain in force:

1. **Most UI is neutral.** A source colour marks a *state* or an *interaction*:
   the active workspace, the active mode, a selection, a pending edit, success,
   danger, research. It is never a background wash and never body text.
2. **State is never colour alone.** The maintainer here is red-green colourblind,
   so every status role also carries a glyph and a brightness difference
   (:func:`status_glyph`), and no surface may express a state by hue alone.

Qt style sheets cannot express everything (notably per-widget focus rings on
composite views), so :func:`apply_app_theme` sets both a ``QPalette`` and the
application-wide style sheet, and the few widgets that must draw themselves call
:func:`color`, :func:`qcolor` and :func:`mono_font` directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True, slots=True)
class Palette:
    """The semantic colour roles. Every value traces to Buu's sprite palette.

    The names describe UI semantics, never the character: there is no ``buu_pink``
    here, because a role named after its source cannot survive the next art
    direction. Each field records the sampled sprite colour it came from.
    """

    # -- BUU'S PINK RAMP: the product identity, used deliberately ----------
    #
    # Pink is DragonByte Z's primary product colour, taken from Buu's skin ramp.
    # It is not a neutral to be apologised for, and it is not decoration either:
    # the four steps below are a *hierarchy*, so the pink does the work a grey ramp
    # would do in a conventional editor. Read them as one ladder:
    #
    #   pink_soft     large, low-priority shell areas
    #   pink_mid      chrome: menu bar, editor strip, status bar
    #   pink_strong   interaction: active editor/mode, selection, primary action
    #   pink_deep     small high-contrast edges and text
    #
    # Each step is a lightness/saturation translation of a real index on Buu's
    # sprite (see `docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md`).

    #: Step 1 - the widest, quietest pink: the application background. From the
    #: skin's specular (`#ffd6e7`) and highlight (`#ffa5ce`), muted into a desktop
    #: chrome value. Large areas use the LIGHTEST step, exactly as a grey ramp would.
    pink_soft: str = "#f2ccdf"
    #: Step 2 - chrome: the menu bar, the editor strip and the status bar, one value
    #: deeper so the shell bands read as distinct from the window behind them.
    pink_mid: str = "#eebfd6"
    #: Step 3 - interaction: active editor, active mode, selection, primary action,
    #: focus. The sprite's skin base (`#de5294`) deepened so it separates from the
    #: chrome and carries white text on the white panels.
    pink_strong: str = "#a81560"
    #: Step 4 - the deepest magenta: small high-contrast edges and text where the
    #: strong step is not enough. The sprite's deepest skin shadow (`#8c0052`).
    pink_deep: str = "#6d0c3c"

    # -- surfaces: Buu's white mantle as the work surfaces -----------------
    #: LEVEL 0 - the application background. An ALIAS of `pink_soft`, because the
    #: shell IS the pink: there is one value, two names for the two roles it plays.
    background: str = "#f2ccdf"
    #: The shell's mid step. An alias of `pink_mid`, for the same reason.
    chrome: str = "#eebfd6"
    #: LEVEL 1 - the main editor surface where content is worked on: the sprite's
    #: mantle, one step off white so the pink shell frames it.
    surface: str = "#fdfbfc"
    #: LEVEL 2 - sidebars, inspector, tool areas: the pure mantle white.
    surface_raised: str = "#ffffff"
    #: LEVEL 3 - inputs, list rows, editable cells: the same white as the panels,
    #: because here the *border* is what separates a field, not another value step.
    surface_input: str = "#ffffff"
    #: The editing canvas, below artwork. Deeper than every panel, so game content is
    #: the brightest and most saturated thing on screen. From the sprite's grey ramp,
    #: warmed toward the skin so it belongs to the same world.
    canvas: str = "#c3a3b4"

    # -- borders: the sprite's outline ramp, kept light --------------------
    #: Quiet separators inside one panel. On white panels these are the main
    #: separator, so they carry a little more value than a hairline would.
    border: str = "#e4d2db"
    #: Region and panel boundaries, and the boundary between panel and pink shell.
    border_strong: str = "#cbadbc"

    # -- text: the sprite's outline, expanded into a type ramp --------------
    #: Primary text: the sprite's outline (`#000000`) lifted off pure black.
    text_primary: str = "#2a2229"
    #: Secondary text: a lighter step of the same ramp.
    text_secondary: str = "#5c525a"
    #: Tertiary / technical text: recessive but readable, never a primary label.
    text_muted: str = "#756970"
    #: Clearly disabled, and still legible.
    text_disabled: str = "#938990"

    # -- the primary identity: Buu's pink-magenta --------------------------
    #: The interaction family: selected editor, active mode, selection, focus,
    #: primary action. Step 3 of the pink ramp.
    accent: str = "#a81560"
    #: Hover on an accented control: the sprite's `#ff73b5` pulled back.
    accent_hover: str = "#930f53"
    #: Pressed / committed accent: the sprite's `#9c185a`, pushed to ramp step 4.
    accent_pressed: str = "#6d0c3c"
    #: A tinted ground for an accented control, so an active control reads as active
    #: by value as well as by hue. The sprite's lightest skin (`#ffd6e7`) muted.
    accent_ground: str = "#f7dbe8"
    #: Text drawn on a solid accent fill.
    accent_ink: str = "#ffffff"

    # -- the secondary accent: Buu's gold belt ----------------------------
    #: Authored-content markers, one rare emphasized action, brand detail. Sampled
    #: from the sprite's belt (`#ad4a00`), deepened for legibility on light.
    accent_secondary: str = "#9a5300"
    #: Hover on a secondary-accented control (`#ffad00` pulled back).
    accent_secondary_hover: str = "#7d4200"

    # -- interaction -------------------------------------------------------
    #: Pointer hover on a neutral white control.
    hover: str = "#fbeef4"
    #: A selected row, list item, sprite or map cell. STRONGER than the chrome, on
    #: purpose: the pale pink shell must never be mistaken for a selection, so this
    #: is a saturated band from ramp step 3 rather than a tint of the background.
    selection: str = "#f2b3d0"
    #: The edge that marks a selected row, so selection is not a fill alone. Ramp
    #: step 4, which gives a selected row a high-contrast outline against both the
    #: white panels and the pink chrome.
    selection_edge: str = "#8f1350"
    #: The keyboard-focus ring. Drawn at 1-2px width *and* in this colour, so focus
    #: never depends on hue alone.
    focus: str = "#c9186a"

    # -- semantic state ----------------------------------------------------
    #: Valid / safe / confirmed. Buu's sprite carries no green at all, so this is
    #: the one documented exception: a conventional editor green, darkened for a
    #: light surface. Recorded in the colour-source document.
    success: str = "#1f7a3d"
    #: Pending / unsaved: the sprite's gold belt, so "waiting on you" is the
    #: authored-change colour rather than an unrelated amber.
    pending: str = "#8a5a00"
    #: Destructive / error: the sprite's own eye red (`#c60000`), darkened, which is
    #: the alarm colour the character already carries and stays separable from
    #: `pending`.
    danger: str = "#b3261e"
    #: Specialized / research: the sprite's cape violet, so this role needs no
    #: exception either.
    research: str = "#6b3fa0"

    # -- canvas instrumentation -------------------------------------------
    #: The transparency squares behind a rendered map or a chunk thumbnail: two
    #: close values from the sprite's mid-neutral ramp, present but quiet enough not
    #: to compete with artwork.
    checker_dark: str = "#cdbcc6"
    #: The lighter square of the same checkerboard.
    checker_light: str = "#ded1d8"
    #: The selected-sprite preview canvas. A light technical ground, NOT black: on a
    #: light editor a black field read as a hole, and it is not needed to judge
    #: transparency because the preview draws its own checkerboard.
    preview: str = "#e8dae1"
    #: The chunk-cell grid drawn over the map in Layout mode: the identity pink at
    #: partial alpha, drawn cosmetic and thin, so it reads as a rule over the
    #: artwork rather than as a highlight competing with it.
    grid: str = "#b81f6b"
    #: A placement the project authored: the secondary accent, because an authored
    #: marker IS authored content.
    marker_authored: str = "#9a5300"
    #: A retail placement, which the base image supplies: the identity colour, so
    #: the two provenances are separable at a glance and neither is a "warning".
    marker_retail: str = "#b81f6b"
    #: The halo drawn around a marker so it stays visible over bright game art.
    marker_halo: str = "#ffffff"
    #: The outline that separates a marker from the artwork under it.
    marker_outline: str = "#2a2229"

    # -- the review's token names ------------------------------------------
    # The colour review listed the exact token names it expects. They are all
    # present above under the project's established role vocabulary; these
    # read-only aliases mean either name resolves to the same single value, so
    # there is still ONE palette and no duplicate shades.

    @property
    def surfaceRaised(self) -> str:  # noqa: N802 - the review's spelling
        return self.surface_raised

    @property
    def surfaceInput(self) -> str:  # noqa: N802
        return self.surface_input

    @property
    def borderStrong(self) -> str:  # noqa: N802
        return self.border_strong

    @property
    def textPrimary(self) -> str:  # noqa: N802
        return self.text_primary

    @property
    def textSecondary(self) -> str:  # noqa: N802
        return self.text_secondary

    @property
    def textMuted(self) -> str:  # noqa: N802
        return self.text_muted

    @property
    def accentHover(self) -> str:  # noqa: N802
        return self.accent_hover

    @property
    def accentPressed(self) -> str:  # noqa: N802
        return self.accent_pressed

    @property
    def accentSecondary(self) -> str:  # noqa: N802
        return self.accent_secondary

    @property
    def warning(self) -> str:
        """The review's name for the pending/unsaved state. One hue, two names."""
        return self.pending


#: One instance; the palette is a value, not per-widget state.
COLORS = Palette()

#: Spacing scale. Every margin in the workbench is one of these.
SPACE_XS = 2
SPACE_SM = 4
SPACE_MD = 8
SPACE_LG = 12
SPACE_XL = 16

#: Corner radii. Small on purpose: Aseprite's chrome is hard 1 px bevels and
#: LDtk's base button has no radius at all, so a large radius would read as a web
#: card rather than a desktop tool. The accepted site uses 3px and this matches it.
RADIUS_INPUT = 3
RADIUS_BUTTON = 2

#: Control geometry. One row height everywhere a list or field appears.
ROW_HEIGHT = 20
TOOLBAR_HEIGHT = 28
PANEL_HEADER_HEIGHT = 22
STATUS_HEIGHT = 22

#: Bottom-left glyph in the window title when edits are pending (Godot places its
#: ``(*)`` first so the OS task bar shows it; this is the DragonByte Z equivalent).
TITLE_DIRTY = "\u25cf"


def color(name: str) -> QColor:
    """The ``QColor`` for a palette role name."""
    return QColor(getattr(COLORS, name))


def qcolor(name: str, alpha: int | None = None) -> QColor:
    """A palette colour, optionally with an explicit alpha.

    Widgets that must draw over game artwork need a translucent version of a role
    (a selection fill, a marker halo). Exposing it here keeps the hex value in this
    module rather than in the painter.
    """
    value = QColor(getattr(COLORS, name))
    if alpha is not None:
        value.setAlpha(alpha)
    return value


def css_rgba(name: str, alpha: int) -> str:
    """A palette colour as a CSS ``rgba(...)`` string for a widget stylesheet.

    A handful of widgets draw a translucent ground behind text that sits over
    arbitrary artwork (the scoped palette's index labels). They need the value in
    CSS form, and it must still come from here rather than from a literal in the
    widget.
    """
    value = QColor(getattr(COLORS, name))
    return f"rgba({value.red()}, {value.green()}, {value.blue()}, {alpha / 255:.3f})"


def mono_font(size_delta: int = -1) -> QFont:
    """The fixed-width face used for addresses, offsets and raw records.

    Uses the platform's fixed font rather than a named family, so the workbench
    does not depend on a font being installed.
    """
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setPointSize(max(7, font.pointSize() + size_delta))
    return font


def status_glyph(role: str) -> str:
    """The non-colour half of a status state.

    Every status role must be distinguishable by brightness *and* glyph, so
    callers render ``f"{status_glyph(role)} {text}"`` instead of colouring text.
    """
    return _GLYPHS.get(role, _GLYPHS["neutral"])


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
    "research": "\u2697",  # alembic, research only
}

#: Role -> the palette attribute that paints it. One table, so a caller names a
#: *state* and the theme resolves both its colour and its glyph.
STATE_COLORS = {
    "success": "success",
    "valid": "success",
    "saved": "success",
    "pending": "pending",
    "warning": "pending",
    "error": "danger",
    "invalid": "danger",
    "danger": "danger",
    "research": "research",
    "readonly": "text_muted",
    "info": "text_secondary",
    "neutral": "text_secondary",
}


def state_color(role: str) -> QColor:
    """The colour for a status role, resolved through :data:`STATE_COLORS`."""
    return color(STATE_COLORS.get(role, "text_secondary"))


def apply_app_theme(app: QApplication) -> None:
    """Apply the DragonByte Z palette and style sheet to a whole application.

    Called once from the shell entry point. Widgets must not carry their own
    stylesheet afterwards: a per-tab sheet is what let the Map Browser drift away
    from the rest of the product.
    """
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, color("background"))
    palette.setColor(QPalette.ColorRole.WindowText, color("text_primary"))
    palette.setColor(QPalette.ColorRole.Base, color("surface_input"))
    palette.setColor(QPalette.ColorRole.AlternateBase, color("surface"))
    palette.setColor(QPalette.ColorRole.Text, color("text_primary"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, color("text_muted"))
    palette.setColor(QPalette.ColorRole.Button, color("surface_raised"))
    palette.setColor(QPalette.ColorRole.ButtonText, color("text_primary"))
    # A selected row is the identity pink at low strength with dark text.
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
    app.setStyleSheet(app_stylesheet())


def app_stylesheet() -> str:
    """The one application style sheet.

    Sets surfaces, separators, the focus ring and the control metrics; leaves
    widget-specific decoration to the widgets. Panel regions are square with 1px
    separators (Tiled's dock idiom) and only inputs and buttons carry a radius.
    """
    c = COLORS
    mono = mono_font().family()
    return f"""
    QWidget {{
        background-color: {c.surface};
        color: {c.text_primary};
    }}
    QMainWindow, QDialog {{ background-color: {c.background}; }}

    /* Qt's containers carry a default base colour; here they are named rather than
       inherited, because QTabWidget and the item views do not inherit one and would
       otherwise punch a stock grey through the shell. */
    QStackedWidget, QSplitter, QScrollArea, QAbstractScrollArea,
    QGroupBox, QDialogButtonBox, QTabWidget, QTabWidget::pane, QFrame {{
        background-color: {c.surface};
    }}

    /* THE TOP SHELL reads as one band, not three stacked bars. It sits one value
       below the pink application background so the chrome is quieter than the
       window, and its parts are separated by hairlines rather than by heavy
       borders or value jumps. */
    QMenuBar, QToolBar, QStatusBar {{
        background-color: {c.chrome};
        color: {c.text_primary};
    }}
    QMenuBar {{ border-bottom: 1px solid {c.border}; padding: 0px; }}
    QMenuBar::item {{ padding: 4px 10px; background: transparent; }}
    QMenuBar::item:selected {{ background-color: {c.selection}; color: {c.text_primary}; }}
    QMenuBar::item:pressed {{ background-color: {c.accent_ground}; color: {c.accent}; }}

    QMenu {{
        background-color: {c.surface_raised};
        border: 1px solid {c.border_strong};
        padding: 2px;
    }}
    QMenu::item {{ padding: 4px 22px 4px 22px; }}
    QMenu::item:selected {{ background-color: {c.selection}; color: {c.text_primary}; }}
    QMenu::item:disabled {{ color: {c.text_disabled}; }}
    QMenu::separator {{ height: 1px; background: {c.border}; margin: 4px 6px; }}

    QToolBar {{
        border-bottom: 1px solid {c.border};
        spacing: {SPACE_SM}px;
        padding: 3px 6px;
    }}
    QToolBar::separator {{ background: {c.border_strong}; width: 1px; margin: 5px 7px; }}

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
    QToolButton:pressed {{ background-color: {c.selection}; }}
    /* ACTIVE WORKSPACE / MODE: Buu's pink-magenta on a tinted ground at a bolder
       weight, so an active control reads as active by value as well as by hue. */
    QToolButton:checked {{
        background-color: {c.accent_ground};
        color: {c.accent};
        border-color: {c.selection_edge};
        font-weight: bold;
    }}
    QToolButton:focus {{ border-color: {c.focus}; }}
    QToolButton:disabled {{ color: {c.text_disabled}; }}
    QToolButton::menu-indicator {{ width: 0px; }}

    QTabWidget::pane {{
        border: none;
        border-top: 1px solid {c.border};
        background-color: {c.surface};
    }}
    QTabBar {{ background-color: {c.background}; qproperty-drawBase: 0; }}
    QTabBar::tab {{
        background-color: transparent;
        color: {c.text_secondary};
        border: 1px solid transparent;
        border-bottom: 2px solid transparent;
        padding: 5px 9px;
        margin-right: 1px;
        font-size: 9pt;
    }}
    QTabBar::tab:hover {{ background-color: {c.surface_raised}; color: {c.text_primary}; }}
    QTabBar::tab:selected {{
        background-color: {c.surface};
        color: {c.accent};
        border-bottom: 2px solid {c.accent};
        font-weight: bold;
    }}
    QTabBar::tab:disabled {{ color: {c.text_disabled}; }}

    QTabWidget[dbzRole="panel"]::pane {{
        border: 1px solid {c.border};
        background-color: {c.surface};
    }}
    QTabWidget[dbzRole="panel"] > QTabBar::tab {{
        background-color: {c.background};
        padding: 3px 9px;
        font-size: 8pt;
    }}
    QTabWidget[dbzRole="panel"] > QTabBar::tab:selected {{
        background-color: {c.surface_raised};
        border-bottom: 2px solid {c.accent};
    }}

    QLabel {{ background: transparent; }}
    /* Panel headers are a raised strip with hairline rules and NEUTRAL text: a
       heading is not an accent. Depth comes from value, not from colour. */
    QLabel[dbzRole="panelHeader"] {{
        background-color: {c.surface_raised};
        border-top: 1px solid {c.border};
        border-bottom: 1px solid {c.border};
        color: {c.text_primary};
        padding: 2px 6px;
        font-weight: bold;
    }}
    QLabel[dbzRole="fieldLabel"] {{ color: {c.text_secondary}; }}
    QLabel[dbzRole="technical"] {{
        color: {c.text_muted};
        font-family: "{mono}";
    }}
    QLabel[dbzRole="count"] {{ color: {c.text_muted}; padding: 0px 4px; }}
    QLabel[dbzRole="hint"] {{ color: {c.text_secondary}; }}
    /* Branding detail: the one place the secondary accent may be a heading. */
    QLabel[dbzRole="brand"] {{ color: {c.accent_secondary}; font-weight: bold; }}

    QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {c.surface_input};
        border: 1px solid {c.border_strong};
        border-radius: {RADIUS_INPUT}px;
        padding: 2px 5px;
        color: {c.text_primary};
        selection-background-color: {c.selection};
        selection-color: {c.text_primary};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus,
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {c.focus};
    }}
    QLineEdit:disabled, QPlainTextEdit:disabled, QTextEdit:disabled,
    QSpinBox:disabled, QDoubleSpinBox:disabled {{
        color: {c.text_disabled};
        background-color: {c.surface};
        border-color: {c.border};
    }}

    QComboBox {{
        background-color: {c.surface_input};
        border: 1px solid {c.border_strong};
        border-radius: {RADIUS_INPUT}px;
        padding: 2px 5px;
        min-height: {ROW_HEIGHT - 8}px;
        color: {c.text_primary};
    }}
    QComboBox:hover {{ border-color: {c.text_muted}; }}
    QComboBox:focus {{ border: 1px solid {c.focus}; }}
    QComboBox:disabled {{
        color: {c.text_disabled};
        background-color: {c.surface};
        border-color: {c.border};
    }}
    QComboBox::drop-down {{ border: none; width: 16px; }}
    QComboBox QAbstractItemView {{
        background-color: {c.surface_raised};
        border: 1px solid {c.border_strong};
        selection-background-color: {c.selection};
        selection-color: {c.text_primary};
    }}

    QPushButton {{
        background-color: {c.surface_raised};
        border: 1px solid {c.border_strong};
        border-radius: {RADIUS_BUTTON}px;
        padding: 3px 10px;
        min-height: {ROW_HEIGHT - 6}px;
        color: {c.text_primary};
    }}
    QPushButton:hover {{ background-color: {c.hover}; border-color: {c.text_muted}; }}
    QPushButton:pressed {{ background-color: {c.selection}; }}
    QPushButton:focus {{ border: 1px solid {c.focus}; }}
    QPushButton:checked {{
        background-color: {c.accent_ground};
        color: {c.accent};
        border: 1px solid {c.selection_edge};
    }}
    QPushButton:disabled {{
        color: {c.text_disabled};
        background-color: {c.surface};
        border-color: {c.border};
    }}
    /* PRIMARY INTERACTION: Buu's identity pink. */
    QPushButton[dbzRole="primary"] {{
        background-color: {c.accent};
        border: 1px solid {c.accent_pressed};
        color: {c.accent_ink};
        font-weight: bold;
    }}
    QPushButton[dbzRole="primary"]:hover {{
        background-color: {c.accent_hover};
        border-color: {c.accent};
        color: {c.accent_ink};
    }}
    QPushButton[dbzRole="primary"]:disabled {{
        background-color: {c.surface};
        border-color: {c.border};
        color: {c.text_disabled};
    }}
    /* SECONDARY/BRAND ACCENT: Buu's gold belt, for a rare emphasized action. */
    QPushButton[dbzRole="secondary"] {{
        border: 1px solid {c.accent_secondary};
        color: {c.accent_secondary};
    }}
    QPushButton[dbzRole="secondary"]:hover {{
        background-color: {c.hover};
        color: {c.accent_secondary_hover};
    }}
    QPushButton[dbzRole="secondary"]:disabled {{
        border-color: {c.border};
        color: {c.text_disabled};
    }}
    QPushButton[dbzRole="destructive"] {{ color: {c.danger}; }}
    QPushButton[dbzRole="destructive"]:hover {{
        border-color: {c.danger};
        background-color: {c.hover};
    }}

    QListWidget, QListView, QTreeWidget, QTreeView, QTableWidget, QTableView {{
        background-color: {c.surface_input};
        alternate-background-color: {c.surface};
        border: 1px solid {c.border};
        border-radius: 0px;
        outline: none;
        color: {c.text_primary};
    }}
    QListWidget::item, QTreeWidget::item, QTableWidget::item, QTableView::item {{
        padding: 2px 4px;
        border: 1px solid transparent;
        color: {c.text_primary};
    }}
    QListWidget::item:hover, QTreeWidget::item:hover,
    QTableWidget::item:hover, QTableView::item:hover {{
        background-color: {c.hover};
    }}
    /* SELECTED DATA ROW / ASSET: the identity pink at low strength with a lit
       edge, so the selection is unmistakable and belongs to the same family as the
       active mode. */
    QListWidget::item:selected, QTreeWidget::item:selected,
    QTableWidget::item:selected, QTableView::item:selected {{
        background-color: {c.selection};
        color: {c.text_primary};
        border: 1px solid {c.selection_edge};
    }}
    QListWidget::item:disabled, QTableWidget::item:disabled {{
        color: {c.text_disabled};
    }}
    QListWidget:focus, QTreeWidget:focus, QTableView:focus, QTableWidget:focus {{
        border: 1px solid {c.focus};
    }}
    QTableCornerButton::section {{ background-color: {c.surface_raised}; border: none; }}

    QHeaderView::section {{
        background-color: {c.surface_raised};
        color: {c.text_secondary};
        border: none;
        border-right: 1px solid {c.border};
        border-bottom: 1px solid {c.border_strong};
        padding: 3px 6px;
    }}

    QCheckBox, QRadioButton {{ background: transparent; spacing: 5px; }}
    QCheckBox:disabled, QRadioButton:disabled {{ color: {c.text_disabled}; }}

    QGroupBox {{
        border: none;
        border-top: 1px solid {c.border};
        margin-top: 0px;
        padding-top: {SPACE_SM}px;
        background-color: {c.surface};
    }}

    QSplitter::handle {{ background-color: {c.border}; }}
    QSplitter::handle:horizontal {{ width: 1px; }}
    QSplitter::handle:vertical {{ height: 1px; }}
    QSplitter::handle:hover {{ background-color: {c.selection_edge}; }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: {c.chrome}; width: 10px; margin: 0px; }}
    QScrollBar:horizontal {{ background: {c.chrome}; height: 10px; margin: 0px; }}
    QScrollBar::handle {{ background: {c.border_strong}; min-height: 20px; min-width: 20px; }}
    QScrollBar::handle:hover {{ background: {c.text_muted}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0px; width: 0px; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

    /* The status bar keeps its own slightly differentiated surface and a hairline,
       so it neither disappears into the editor body nor reads as a third band. */
    QStatusBar {{
        background-color: {c.background};
        border-top: 1px solid {c.border};
        color: {c.text_secondary};
        min-height: {STATUS_HEIGHT}px;
    }}
    QStatusBar::item {{ border: none; }}
    QStatusBar QLabel,
    QLabel[dbzRole="status"],
    QLabel#dbzStatusLine {{
        color: {c.text_secondary};
        padding-left: {SPACE_XL}px;
        padding-right: {SPACE_XL}px;
        background: transparent;
    }}

    QToolTip {{
        background-color: {c.surface_raised};
        color: {c.text_primary};
        border: 1px solid {c.border_strong};
        padding: 3px 5px;
    }}
    """
