"""The right pane: who is drawn, what retail said, what contains the line, its sites,
the in-game preview, and the addresses behind one disclosure.

Sections are separated by 1 px dividers and spacing, never by cards. Raw addresses,
offsets and sizes are copyable and stay behind one disclosure, because they are
diagnostics rather than the primary label.

Every answer here comes from `session.py`, including each carrier's own speaker
label, so the table and the list cannot disagree.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import preview
from . import theme as theme_module
from .session import UNKNOWN_SPEAKER

NO_RETAIL = "No retail reference is loaded, so there is nothing to compare with."
NO_LINE = "No line is selected."
AGREES = "Retail and this image say the same words."
PREVIEW_CAPTION = "In-game preview"
ADDRESS_LABEL = "Address, offset and size"
#: The heading says what the label means: the record stores a portrait operand and
#: never a speaker field.
SPEAKER_HEADING = "Speaker (by portrait)"
SITE_LINE = "{count} handle site(s) name this line in the image."

RULE = "border-top: 1px solid %s;"
INK = "color: %s;"


def rule(theme) -> QFrame:
    """One full-width pixel between two sections, never a card."""
    line = QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet(RULE % getattr(theme, "divider"))
    return line


class ContextPane(QWidget):
    """Everything the window knows about the selected line, beside the editor."""

    def __init__(self, theme, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._metrics = metrics
        self._speaker_label = QLabel(NO_LINE, self)
        self._speaker_label.setWordWrap(True)
        self._speaker_label.setFont(theme_module.type_scale().body)
        self.portrait = QLabel("", self)
        self.portrait.setWordWrap(True)
        self.portrait.setProperty("role", "caption")
        self.portrait.setFont(theme_module.type_scale().caption)
        self.retail_heading = self._heading("Retail says")
        self.retail = QLabel(NO_LINE, self)
        self.retail.setWordWrap(True)
        self.retail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.retail.setFont(theme_module.type_scale().prose)
        self.contained_heading = self._heading("Contained by")
        self.contained = self._table(metrics)
        self.sites = QLabel(NO_LINE, self)
        self.sites.setWordWrap(True)
        self.sites.setFont(theme_module.type_scale().caption)
        self.preview_heading = self._heading(PREVIEW_CAPTION)
        self.preview = preview.DialoguePreview(self)
        self.raw_button = QToolButton(self)
        self.raw_button.setText(ADDRESS_LABEL)
        self.raw_button.setCheckable(True)
        self.raw_button.setAutoRaise(True)
        self.raw_button.toggled.connect(self._raw_toggled)
        self.raw_field = QLineEdit(self)
        self.raw_field.setReadOnly(True)
        self.raw_field.setFont(theme_module.type_scale().data)
        self.raw_field.setVisible(False)
        column = QVBoxLayout(self)
        column.setContentsMargins(metrics.pad_lg, metrics.pad_md, metrics.pad_lg,
                                  metrics.pad_md)
        column.setSpacing(metrics.gap)
        for widget in (self._speaker_label, self.portrait, rule(theme),
                       self.retail_heading, self.retail, rule(theme),
                       self.contained_heading, self.contained, self.sites, rule(theme),
                       self.preview_heading, self.preview):
            column.addWidget(widget)
        column.addStretch(1)
        column.addWidget(self.raw_button)
        column.addWidget(self.raw_field)

    # --- the shell's API -----------------------------------------------------

    def set_line(self, session, line) -> None:
        """Show one row, or clear every section when there is none."""
        if session is None or line is None:
            self._speaker_label.setText(NO_LINE)
            self.portrait.setVisible(False)
            self.retail.setText(NO_LINE)
            self.contained.setRowCount(0)
            self.sites.setText(NO_LINE)
            return
        self._show_speaker(session, line)
        self._show_retail(session, line)
        self._show_covering(session, session.covering(line.key))
        self.sites.setText(SITE_LINE.format(count=session.sites(line.key)))

    def set_preview_state(self, text: str) -> None:
        """The preview draws its own waiting state; the pane only forwards the text."""
        self.preview.set_text(text)

    def set_address(self, raw: str) -> None:
        """The row's address, offset and size, revealed on request and copyable."""
        self.raw_field.setText(raw)

    # --- sections ------------------------------------------------------------

    def _show_speaker(self, session, line) -> None:
        self._speaker_label.setText(line.speaker_label)
        found = session.portraits.get(line.target or line.key)
        operand = getattr(found, "operand", None)
        self.portrait.setText("" if operand is None
                              else f"Portrait operand 0x{operand:02X}")
        self.portrait.setVisible(operand is not None)

    def _show_retail(self, session, line) -> None:
        """The retail wording appears only where it differs, never as a repeat."""
        if line.retail is None:
            self.retail.setText(NO_RETAIL)
            return
        self.retail.setText(line.retail if session.differs_from_retail(line.key)
                            else AGREES)

    def _show_covering(self, session, covering: tuple[str, ...]) -> None:
        """Each carrier's own speaker label, so the table and the list agree."""
        self.contained.setRowCount(len(covering))
        for row, key in enumerate(covering):
            self.contained.setItem(row, 0, QTableWidgetItem(key))
            carrier = session.line(key)
            self.contained.setItem(
                row, 1,
                QTableWidgetItem(UNKNOWN_SPEAKER if carrier is None
                                 else carrier.speaker_label))

    def _heading(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setProperty("role", "sectionLabel")
        label.setFont(theme_module.type_scale().label)
        return label

    def _table(self, metrics) -> QTableWidget:
        table = QTableWidget(0, 2, self)
        table.setHorizontalHeaderLabels(["Record", SPEAKER_HEADING])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(metrics.row_height)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setShowGrid(False)
        table.setFont(theme_module.type_scale().body)
        return table

    def _raw_toggled(self, shown: bool) -> None:
        self.raw_field.setVisible(shown)
