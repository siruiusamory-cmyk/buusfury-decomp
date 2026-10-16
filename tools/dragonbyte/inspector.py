"""The one inspector every destination shares.

A destination does not own an inspector. It hands this pane a
:class:`InspectorContext` for whatever is selected, or ``None`` when nothing is,
and the pane renders it. That keeps one implementation, one place where the
support vocabulary appears, and no per-destination copy.

The pane is thin on purpose: it holds no ROM logic, calls no SDK function and
never decides what is selected. Colour is decoration - every state is a word
plus a glyph plus an accessible name, so removing colour leaves it readable.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from . import theme
from .destination import Destination

#: The approved user words, in the order the support model lists them. The
#: census token each one stands for is quoted in Technical details, never here.
SUPPORT_STATES: tuple[str, ...] = (
    "Editable",
    "Editable with limits",
    "Read-only",
    "Not supported yet",
    "Not mapped",
    "Not in this game",
)

#: User word -> the status role that paints and glyphs it. Two support states
#: deliberately share a role: they are different facts, not different alarms.
SUPPORT_ROLES = {
    "Editable": "edit",
    "Editable with limits": "warning",
    "Read-only": "readonly",
    "Not supported yet": "info",
    "Not mapped": "neutral",
    "Not in this game": "neutral",
}


def support_state_text() -> str:
    """Every support state as ``glyph + word``, for the About surface."""
    return "\n".join(
        f"{theme.status_glyph(SUPPORT_ROLES[state])} {state}" for state in SUPPORT_STATES
    )


@dataclass(frozen=True, slots=True)
class InspectorContext:
    """What one selection says about itself, in the three identity tiers."""

    #: The friendly display identity, e.g. ``Placement 037``.
    friendly: str
    #: The stable technical identity, e.g. ``map:0012/placement:0037``.
    stable: str
    #: One of :data:`SUPPORT_STATES`.
    support: str
    #: Optional extra fact; empty means no extra line is shown.
    detail: str = ""


class InspectorPane(QWidget):
    """The shared contextual pane: one header and one rendered context."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("inspectorPane")
        self._destination: Destination | None = None

        header = QLabel("Inspector")
        header.setProperty("dbzRole", "panelHeader")
        self._header = header
        self._friendly = QLabel()
        self._friendly.setWordWrap(True)
        self._stable = QLabel()
        self._stable.setProperty("dbzRole", "technical")
        self._stable.setTextInteractionFlags(
            self._stable.textInteractionFlags()
            | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._stable.setWordWrap(True)
        self._support = QLabel()
        self._support.setWordWrap(True)
        self._detail = QLabel()
        self._detail.setProperty("dbzRole", "hint")
        self._detail.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(theme.SPACE_SM)
        layout.addWidget(header)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        body_layout.setSpacing(theme.SPACE_SM)
        for widget in (self._friendly, self._stable, self._support, self._detail):
            body_layout.addWidget(widget)
        body_layout.addStretch(1)
        layout.addWidget(body, 1)

        self.set_context(None)

    def set_destination(self, destination: Destination | None) -> None:
        """Name the destination this pane belongs to, for its empty state."""
        self._destination = destination

    def set_context(self, context: InspectorContext | None) -> None:
        """Show one selection, or the destination's empty state."""
        if context is None:
            self._render_empty()
            return
        self._friendly.setText(context.friendly)
        self._stable.setText(context.stable)
        self._stable.setVisible(bool(context.stable))
        self._render_support(context.support)
        self._detail.setText(context.detail)
        self._detail.setVisible(bool(context.detail))

    def _render_support(self, support: str) -> None:
        """Render a support state as glyph plus word plus accessible name."""
        role = SUPPORT_ROLES.get(support, "neutral")
        self._support.setText(f"{theme.status_glyph(role)} {support}")
        self._support.setAccessibleName(support)
        self._support.setToolTip(support)
        palette = self._support.palette()
        palette.setColor(QPalette.ColorRole.WindowText, theme.state_color(role))
        self._support.setPalette(palette)
        self._support.setVisible(True)

    def _render_empty(self) -> None:
        """The empty state names the destination; it is never a blank pane."""
        self._friendly.setText("Nothing is selected.")
        self._stable.clear()
        self._stable.setVisible(False)
        self._support.clear()
        self._support.setAccessibleName("")
        self._support.setToolTip("")
        self._support.setVisible(False)
        if self._destination is None:
            self._detail.setText("No destination is active yet.")
        else:
            self._detail.setText(
                f"{self._destination.label} is the active destination. Select a "
                "record to see its identity and what can be changed."
            )
        self._detail.setVisible(True)
