"""The right pane: what retail said, what contains the line, its sites, the preview.

Sections are separated by spacing and one-pixel rules, never by cards. Raw
addresses, offsets and sizes stay behind one disclosure and are copyable there.
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

from . import preview, theme

NO_RETAIL = "No retail reference is loaded, so there is nothing to compare with."
NO_LINE = "No line is selected."
PREVIEW_CAPTION = "Approximate preview"


def rule() -> QFrame:
    """One pixel between two sections."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Plain)
    return line


class ContextPane(QWidget):
    """Everything the window knows about the selected line, beside the editor."""

    def __init__(self, theme_, metrics, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme_
        self.retail_heading = self._heading("Retail says")
        self.retail = QLabel(NO_LINE)
        self.retail.setWordWrap(True)
        self.retail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.contained_heading = self._heading("Contained by")
        self.contained = QTableWidget(0, 1)
        self.contained.setHorizontalHeaderLabels(["Record"])
        self.contained.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.contained.verticalHeader().setVisible(False)
        self.contained.verticalHeader().setDefaultSectionSize(metrics.row_height)
        self.contained.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.contained.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.contained.setShowGrid(False)
        self.sites_heading = self._heading("Sites")
        self.sites = QLabel(NO_LINE)
        self.sites.setWordWrap(True)
        self.preview_heading = self._heading("In-game preview")
        self.preview = preview.DialoguePreview(self)
        self.caption = QLabel(PREVIEW_CAPTION)
        self.caption.setEnabled(False)
        self.raw_button = QToolButton()
        self.raw_button.setText("Address, offset and size")
        self.raw_button.setCheckable(True)
        self.raw_button.toggled.connect(self._raw_toggled)
        self.raw_field = QLineEdit()
        self.raw_field.setReadOnly(True)
        self.raw_field.setFont(theme.mono_font())
        self.raw_field.setVisible(False)
        column = QVBoxLayout(self)
        column.setContentsMargins(10, 8, 10, 8)
        column.setSpacing(metrics.gap)
        for widget in (self.retail_heading, self.retail, rule(), self.contained_heading,
                       self.contained, rule(), self.sites_heading, self.sites, rule(),
                       self.preview_heading, self.preview, self.caption):
            column.addWidget(widget)
        column.addStretch(1)
        column.addWidget(self.raw_button)
        column.addWidget(self.raw_field)

    def _heading(self, text: str) -> QLabel:
        label = QLabel(text)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        return label

    def _raw_toggled(self, shown: bool) -> None:
        self.raw_field.setVisible(shown)

    def show_line(self, session, key: str, text: str, raw: str) -> None:
        line = None if session is None or key == "" else session.line(key)
        if line is None:
            self.retail.setText(NO_LINE)
            self._set_covering(())
            self.sites.setText(NO_LINE)
        else:
            self.retail.setText(line.retail if line.retail is not None else NO_RETAIL)
            self._set_covering(session.covering(key))
            self.sites.setText(f"{session.sites(key)} handle site(s) name this line in the image.")
        self.raw_field.setText(raw)
        self.preview.set_text(text)
        self.caption.setText(PREVIEW_CAPTION if self.preview.is_approximate()
                             else f"{self.preview.glyph_source_name()} glyphs")

    def _set_covering(self, covering: tuple[str, ...]) -> None:
        self.contained.setRowCount(len(covering))
        for row, key in enumerate(covering):
            self.contained.setItem(row, 0, QTableWidgetItem(key))
