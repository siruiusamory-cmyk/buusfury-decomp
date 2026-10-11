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
from .session import UNKNOWN_SPEAKER

NO_RETAIL = "No retail reference is loaded, so there is nothing to compare with."
NO_LINE = "No line is selected."
PREVIEW_CAPTION = "Approximate preview"
#: A line no proven handle site reaches stays editable and says what its target is worth.
NO_PROOF = ("This line is drawn from bytes no proven handle site reaches, so its edit "
            "target is unproven.")


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
        self.contained = QTableWidget(0, 2)
        self.contained.setHorizontalHeaderLabels(["Record", "Speaker"])
        self.contained.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.contained.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents)
        self.contained.verticalHeader().setVisible(False)
        self.contained.verticalHeader().setDefaultSectionSize(metrics.row_height)
        self.contained.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.contained.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.contained.setShowGrid(False)
        # The join is a measured minority report, so the pane states the share.
        self.share = QLabel()
        self.share.setWordWrap(True)
        self.share.setProperty("role", "hint")
        self.proven = QLabel(NO_PROOF)
        self.proven.setWordWrap(True)
        self.proven.setProperty("role", "hint")
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
                       self.contained, self.share, rule(), self.sites_heading, self.sites,
                       self.proven, rule(), self.preview_heading, self.preview, self.caption):
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
            self._set_covering(session, ())
            self.sites.setText(NO_LINE)
        else:
            self.retail.setText(line.retail if line.retail is not None else NO_RETAIL)
            self._set_covering(session, session.covering(key))
            self.sites.setText(f"{session.sites(key)} handle site(s) name this line in the image.")
        self.proven.setVisible(line is not None and not line.proven)
        self._set_share(session)
        self.raw_field.setText(raw)
        self.preview.set_text(text)
        self.caption.setText(PREVIEW_CAPTION if self.preview.is_approximate()
                             else f"{self.preview.glyph_source_name()} glyphs")

    def _set_share(self, session) -> None:
        """How much of the dialogue list carries a name, from the session's own count."""
        resolved, total = (0, 0) if session is None else session.speaker_share()
        self.share.setText("" if not total else
                           f"speaker known for {resolved} of {total} lines")
        self.share.setVisible(bool(total))

    def _set_covering(self, session, covering: tuple[str, ...]) -> None:
        """The records that contain the line, each with the face it draws itself."""
        self.contained.setRowCount(len(covering))
        for index, key in enumerate(covering):
            self.contained.setItem(index, 0, QTableWidgetItem(key))
            row = None if session is None else session.line(key)
            item = QTableWidgetItem(UNKNOWN_SPEAKER if row is None else row.speaker_label)
            if row is None or not row.speaker:
                item.setForeground(theme.color(self._theme, "text_secondary"))
            self.contained.setItem(index, 1, item)
