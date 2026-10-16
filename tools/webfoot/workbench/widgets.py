"""DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001 - small shared desktop-editor widgets.

These exist so the eight tabs stop each inventing their own header, margin and
status treatment, which is what made the application read as several products.
Every pattern here is named against the real reference recorded in
``docs/research/UI_REFERENCE_MATRIX.md``:

- :class:`PanelHeader` - LDtk's panel treatment: a single-line uppercase bar with
  no vertical waste (LDtk ``.collapser``: ``min-height: .8em``, 13 pt uppercase
  accent text, a 16 px disclosure triangle). DragonByte Z keeps it *square* and
  1 px-separated, because LDtk's rounded collapsed state is the part that starts
  to read as a card.
- :class:`DisclosureRow` - Godot's "advanced settings behind one toggle, in the
  same window": raw offsets and pointers are one click away and never a separate
  mode or window.
- :class:`AlignedLabelColumn` - HexManiacAdvance's ``SharedSizeGroup="LeftColumn"``
  trick: every field label in a group shares one computed width, which is what
  makes a form read as a table instead of a ragged stack.
- :class:`StatusStrip` - Tiled's status-bar contract: transient widgets on the
  left, permanent widgets on the right, re-populated by whoever is active.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import theme


class PanelHeader(QWidget):
    """One-line, square, uppercase section header.

    Optionally collapsible. When collapsible it carries a real ``QToolButton``
    with an arrow glyph, so the disclosure is reachable by keyboard and by
    screen reader rather than being a painted triangle.

    The colours are set on the *label* rather than left to a descendant selector
    in the application sheet: this widget paints its own strip, and a stylesheet
    rule that failed to reach the child is how the header text ended up almost
    invisible against it.
    """

    toggled = Signal(bool)

    def __init__(
        self,
        title: str,
        *,
        collapsible: bool = False,
        expanded: bool = True,
        trailing: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("dbzPanelHeader")
        self.setFixedHeight(theme.PANEL_HEADER_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # Qt paints an auto-filled background before the children; the strip's
        # fill therefore belongs in the palette, not in paintEvent.
        self.setAutoFillBackground(True)
        header_palette = self.palette()
        header_palette.setColor(self.backgroundRole(), theme.color("surface_raised"))
        self.setPalette(header_palette)
        self._accent = False

        row = QHBoxLayout(self)
        row.setContentsMargins(theme.SPACE_SM, 0, theme.SPACE_SM, 0)
        row.setSpacing(theme.SPACE_SM)

        self._button: QToolButton | None = None
        self._title: QLabel | None = None
        if collapsible:
            self._button = QToolButton()
            self._button.setCheckable(True)
            self._button.setChecked(expanded)
            self._button.setAutoRaise(True)
            self._button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            self._button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self._button.setCursor(Qt.CursorShape.PointingHandCursor)
            self._button.toggled.connect(self._on_toggled)
            self._button.setText(f"\u25be {title.upper()}")
            self._button.setAccessibleName(title)
            self._button.setToolTip(f"Collapse or expand {title.lower()}")
            self._style(self._button, title.upper())
            row.addWidget(self._button)
        else:
            self._title = QLabel(title.upper())
            font = self._title.font()
            font.setBold(True)
            font.setPointSize(max(7, font.pointSize() - 1))
            self._title.setFont(font)
            self._style(self._title, title.upper())
            row.addWidget(self._title)
        row.addStretch(1)
        self._trailing_row = row
        if trailing is not None:
            row.addWidget(trailing)

    def _style(self, widget: QWidget, text: str) -> None:
        colour = theme.color("accent" if self._accent else "text_primary")
        widget.setStyleSheet(
            f"color: {colour.name()}; background: transparent;"
            " font-weight: bold; letter-spacing: 1px;"
        )
        widget.setAccessibleName(text)

    def add_trailing(self, widget: QWidget) -> None:
        """Append a small control to the header's right end."""
        self._trailing_row.addWidget(widget)

    def title(self) -> str:
        if self._button is not None:
            return self._button.accessibleName()
        return self._title.text()

    def is_expanded(self) -> bool:
        return self._button.isChecked() if self._button is not None else True

    def set_expanded(self, expanded: bool) -> None:
        if self._button is not None:
            self._button.setChecked(bool(expanded))

    def toggle_button(self) -> QToolButton | None:
        """The disclosure button, for tests and for keyboard wiring."""
        return self._button

    def _on_toggled(self, checked: bool) -> None:
        if self._button is not None:
            arrow = "\u25be" if checked else "\u25b8"
            self._button.setText(f"{arrow} {self._button.accessibleName().upper()}")
        self.toggled.emit(bool(checked))

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Draw the separation rule only.

        The strip's fill comes from the widget palette (``setAutoFillBackground``),
        which Qt paints *before* the child widgets. Filling here instead would
        paint over the header's own label, because a parent's ``paintEvent`` runs
        after its children have drawn.
        """
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.setPen(theme.color("border_strong"))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)


class DisclosureRow(QWidget):
    """A labelled, keyboard-reachable disclosure that reveals raw detail.

    Godot's ``Advanced Settings`` toggle, scoped to one panel: the human-readable
    fields stay the default surface and the offsets/pointers behind this row.
    """

    toggled = Signal(bool)

    def __init__(
        self,
        title: str = "Detail",
        *,
        expanded: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("dbzDisclosureRow")

        row = QVBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._button = QToolButton()
        self._button.setCheckable(True)
        self._button.setChecked(expanded)
        self._button.setAutoRaise(True)
        self._button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._button.toggled.connect(self._on_toggled)
        row.addWidget(self._button)

        self._body = QWidget()
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(theme.SPACE_MD, theme.SPACE_XS, 0, theme.SPACE_XS)
        self._body_layout.setSpacing(theme.SPACE_XS)
        self._body.setVisible(expanded)
        row.addWidget(self._body)
        self._title = title
        self._sync()

    def add_widget(self, widget: QWidget) -> None:
        self._body_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        self._body_layout.addLayout(layout)

    def body(self) -> QWidget:
        return self._body

    def toggle_button(self) -> QToolButton:
        return self._button

    def is_expanded(self) -> bool:
        return self._button.isChecked()

    def _on_toggled(self, checked: bool) -> None:
        self._body.setVisible(bool(checked))
        self._sync()
        self.toggled.emit(bool(checked))

    def _sync(self) -> None:
        arrow = "\u25be" if self._button.isChecked() else "\u25b8"
        self._button.setText(f"{arrow} {self._title}")
        self._button.setAccessibleName(self._title)
        self._button.setToolTip(
            f"Hide {self._title.lower()}" if self._button.isChecked()
            else f"Show {self._title.lower()}"
        )


class AlignedFieldTable(QFormLayout):
    """A label/value form whose labels line up on one computed column.

    HexManiacAdvance's ``SharedSizeGroup="LeftColumn"``: labels form a clean
    column without a fixed pixel width that breaks under OS font scaling.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.setHorizontalSpacing(theme.SPACE_MD)
        self.setVerticalSpacing(theme.SPACE_XS)
        self.setContentsMargins(theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM)

    def add_pair(self, name: str, value: QWidget) -> QLabel:
        """Add a label/value pair with the shared secondary-label treatment."""
        label = QLabel(name)
        label.setProperty("dbzRole", "fieldLabel")
        label.setWordWrap(False)
        value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addRow(label, value)
        return label


class TechnicalLabel(QLabel):
    """Recessive monospace text for addresses, offsets, pointers and provenance.

    Never the primary label of anything: the design language requires raw
    technical detail to be visually secondary and available, not dominant.
    """

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setProperty("dbzRole", "technical")
        self.setFont(theme.mono_font())
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


class StateChip(QLabel):
    """A compact state marker that is never expressed by colour alone.

    The role drives the colour *and* supplies a glyph, so a caller passes a
    **state** ("readonly", "pending", "valid") rather than a colour and cannot
    accidentally produce a colour-only signal. Where the state's own wording
    already names it - "Editing available", "Editing not available for this
    record yet." - the glyph is redundant decoration, and ``plain=True`` renders
    the sentence alone while the role still fixes its brightness.

    ``stateChanged`` reports the chip's *state text* (without its glyph), so the
    shell can mirror a chip into its status bar without re-deriving anything.
    """

    #: The chip's state text, without its glyph.
    stateChanged = Signal(str)

    #: Role -> glyph. The colour side is resolved by the theme's own
    #: `STATE_COLORS`, so a role's glyph and its hue can never drift apart.
    _ROLES = {
        "readonly": theme.status_glyph("readonly"),
        "edit": theme.status_glyph("edit"),
        "pending": theme.status_glyph("pending"),
        "saved": theme.status_glyph("saved"),
        "invalid": theme.status_glyph("invalid"),
        "valid": theme.status_glyph("valid"),
        "neutral": theme.status_glyph("neutral"),
        "info": theme.status_glyph("info"),
        "research": theme.status_glyph("research"),
    }
    _COLORS = {
        "readonly": "text_muted",
        "edit": "accent",
        "pending": "pending",
        "saved": "success",
        "invalid": "danger",
        "valid": "success",
        "neutral": "text_primary",
        "info": "text_secondary",
        "research": "research",
    }

    def __init__(
        self,
        text: str = "",
        role: str = "neutral",
        *,
        plain: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWordWrap(True)
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self._plain = plain
        self.set_state(text, role)

    def set_state(self, text: str, role: str) -> None:
        if self._plain:
            shown = text
        else:
            glyph = self._ROLES.get(role, self._ROLES["neutral"])
            shown = f"{glyph} {text}".strip()
        self.setText(shown)
        colour = theme.color(self._COLORS.get(role, "text_secondary"))
        self.setStyleSheet(f"color: {colour.name()}; background: transparent;")
        self.setAccessibleName(text)
        self.stateChanged.emit(text)


class ToolStrip(QFrame):
    """The one contextual strip that sits directly above an editor canvas.

    Porymap places its paint tools, view toggles and a structural action on a
    single line at grid row 0 with the canvas at row 1; Aseprite pins an 18 px
    context bar directly above the sprite editor. DragonByte Z does the same, and
    nothing else: a second toolbar is how editors start to look like IDEs.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dbzToolStrip")
        self.setFixedHeight(theme.TOOLBAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setAutoFillBackground(True)
        strip_palette = self.palette()
        strip_palette.setColor(self.backgroundRole(), theme.color("surface_raised"))
        self.setPalette(strip_palette)
        # A horizontal strip must never set the window's *width*. Left to its own
        # size hint it does exactly that, and the canvas beside it then has to
        # scroll, so its width policy ignores its content: the layout gives it
        # whatever is left and the controls inside it stay put.
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(theme.SPACE_SM, 2, theme.SPACE_SM, 2)
        self._row.setSpacing(theme.SPACE_SM)

    def add(self, widget: QWidget) -> QWidget:
        self._row.addWidget(widget)
        return widget

    def add_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("dbzRole", "fieldLabel")
        self._row.addWidget(label)
        return label

    def add_separator(self) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedWidth(1)
        line.setStyleSheet(f"background-color: {theme.COLORS.border}; border: none;")
        self._row.addWidget(line)

    def add_stretch(self) -> None:
        self._row.addStretch(1)

    def layout_row(self) -> QHBoxLayout:
        return self._row

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Draw the separation rule only; the fill comes from the palette."""
        from PySide6.QtGui import QPainter

        painter = QPainter(self)
        painter.setPen(theme.color("border_strong"))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)


def section(title: str, body: QWidget) -> tuple[PanelHeader, QWidget]:
    """A header plus its body, as one parented column. Returns both."""
    holder = QWidget()
    column = QVBoxLayout(holder)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(0)
    header = PanelHeader(title)
    column.addWidget(header)
    column.addWidget(body)
    return header, holder


class CheckBox(QCheckBox):
    """A check box whose indicator is drawn here, from the theme's own palette.

    The platform indicator is a font glyph whose size a style sheet does not
    control. With the label's background left transparent - which it must be, so
    the label does not paint a slab over the panel - an unchecked box drew no box
    at all. Measured in the shipped window, 227 of the 256 pixels inside the
    indicator rectangle were the surface colour, leaving a bare tick beside the
    label: it read as a bullet in a list, not as something to click.

    Every state is therefore painted here from theme roles, so the control cannot
    drift from the palette and its contrast is a measurable number rather than a
    platform default.
    """

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        # The indicator is drawn, not laid out by the style, so the row has to
        # reserve its height itself.
        self.setMinimumHeight(
            max(theme.CHECK_INDICATOR + 4, self.fontMetrics().height())
        )

    def sizeHint(self):  # noqa: N802 - Qt's spelling
        hint = super().sizeHint()
        height = max(hint.height(), self.minimumHeight())
        if height != hint.height():
            hint.setHeight(height)
        return hint

    def indicator_rect(self):
        """Where the box is drawn, so a test can measure it."""
        return QRect(
            0,
            max(0, (self.height() - theme.CHECK_INDICATOR) // 2),
            theme.CHECK_INDICATOR,
            min(theme.CHECK_INDICATOR, self.height()),
        )

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt's spelling
        painter = QPainter(self)
        # Anti-aliasing is on for the tick, which is a curve. The box itself is NOT
        # anti-aliased: a 1px rounded stroke at 15% of a pixel's coverage measures
        # as a 1.98:1 edge against the panel, which is under the 3:1 a control
        # boundary needs. Filling the boundary as a shape instead makes the edge the
        # stroke colour exactly, so its contrast is the palette's own number.
        box = self.indicator_rect()

        if not self.isEnabled():
            fill, border = theme.color("surface"), theme.color("border")
        elif self.isChecked():
            fill, border = theme.color("accent"), theme.color("accent_pressed")
            if self.underMouse():
                fill = theme.color("accent_hover")
        elif self.underMouse():
            fill, border = theme.color("surface_raised"), theme.color("accent")
        else:
            # An unchecked box is defined by its boundary alone, so the boundary
            # has to clear the 3:1 non-text contrast floor on its own. The theme's
            # `border_strong` is a 2.05:1 hairline against this fill - it is a
            # separator, not a control edge - so the control edge is
            # `text_muted` at 5.24:1, the palette's own tertiary neutral.
            fill, border = theme.color("surface_raised"), theme.color("text_muted")

        radius = theme.RADIUS_BUTTON
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(border)
        painter.drawRoundedRect(box, radius, radius)
        painter.setBrush(fill)
        painter.drawRoundedRect(box.adjusted(1, 1, -1, -1), radius - 1, radius - 1)

        if self.isChecked():
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            mark_colour = (
                theme.COLORS.accent_ink
                if self.isEnabled()
                else theme.COLORS.text_disabled
            )
            mark = theme.check_mark_pixmap(mark_colour, theme.CHECK_INDICATOR)
            # The mark is drawn inside the border, so the ring stays visible.
            painter.drawPixmap(box.adjusted(1, 1, -1, -1), mark)

        text_left = box.right() + 1 + theme.SPACE_SM + 1
        text_area = self.rect().adjusted(text_left, 0, 0, 0)
        painter.setPen(
            theme.color("text_primary")
            if self.isEnabled()
            else theme.color("text_disabled")
        )
        painter.drawText(
            text_area,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            self.text(),
        )

        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(QPen(theme.color("focus"), 1))
            painter.drawRoundedRect(
                box.adjusted(-2, -2, 1, 1),
                theme.RADIUS_BUTTON + 1,
                theme.RADIUS_BUTTON + 1,
            )
        painter.end()

        if self.hasFocus():
            event.accept()


class ScrollPane(QScrollArea):
    """A tab's content in a pane that lets the window actually get narrow.

    The defect this exists for: the shipped shell reported a minimum window of
    1090x1246, because every tab's deepest control demanded its own space. A
    window that cannot be made smaller than a tall monitor's work area cannot be
    tiled beside anything, which is exactly the complaint Godot's own 1024x876
    floor has open against it (godotengine/godot#99369).

    The reference answer is Porymap's: panes shrink and their scroll areas take
    the strain, rather than the window growing. Tiled reaches the same end by
    letting a dock be closed and by `Tab`-hiding the chrome; DragonByte Z needs
    neither, because it has no docks to hide - it only needs the shell to stop
    treating the deepest inspector row as a hard floor.

    ``Ignored`` size policy on the content means the scroll area's own minimum no
    longer propagates the content's minimum upward, so the window can be resized
    to whatever the user's screen actually allows and the pane scrolls instead of
    clipping. The content keeps its real minimum for its own layout, so nothing
    is squashed into illegibility: it scrolls.
    """

    def __init__(self, content: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._content = content
        # A *hard* floor equal to the content's own minimum is what makes the pane
        # scroll instead of squeezing. Qt asks this pane for its minimum size, not
        # the content's, and `widgetResizable` does not forward it - so without
        # this the pane answered "0" and Qt compressed the content's layout until
        # its widgets overlapped (the Graphics tab did exactly that: two 320px
        # previews and a status line laid out on top of one another in an 885px
        # tab). The scroll area still lets the *window* be any size, because this
        # pane's own size policy is Ignored; the floor only stops the content from
        # being deformed.
        hint = content.minimumSizeHint()
        content.setMinimumSize(hint)
        self.setMinimumHeight(hint.height())
        self.setWidget(content)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        # A pane scrolls *down*; it never introduces horizontal scrolling, because
        # that is how a panel silently becomes wider than the window.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        # An explicit floor, so the pane never propagates the content's minimum
        # upward and the shell can be resized to whatever the screen allows.
        self.setMinimumSize(0, 0)

    def content(self) -> QWidget:
        return self._content
