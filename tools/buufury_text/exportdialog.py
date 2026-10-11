"""The summary after an export, and the engine's own refusal text when it refuses.

A conventional report, not a celebration: the file, what the plan did, the size
and the digest, with the two useful buttons. The error area carries the engine's
message verbatim, because those messages are written for a user.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from . import theme

ROWS = ("File", "Applied", "Moved", "Refused", "Output size", "SHA-256")


class ExportDialog(QDialog):
    """One window, used for a successful export and for a refusal."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export")
        self.message = QLabel()
        self.message.setWordWrap(True)
        self.error = QLabel()
        self.error.setWordWrap(True)
        self.error.setVisible(False)
        self.values: dict[str, QLabel] = {}
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(4)
        for row, name in enumerate(ROWS):
            label = QLabel(name)
            value = QLabel()
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            if name == "SHA-256":
                value.setFont(theme.mono_font())
            if name in ("Output size", "Applied", "Moved", "Refused"):
                value.setFont(theme.mono_font())
            self.values[name] = value
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
        self.copy_button = QPushButton("Copy SHA-256")
        self.copy_button.clicked.connect(self._copy_digest)
        self.folder_button = QPushButton("Open containing folder")
        self.folder_button.clicked.connect(self._open_folder)
        buttons = QDialogButtonBox()
        buttons.addButton(self.copy_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(self.folder_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        self._path: Path | None = None
        column = QVBoxLayout(self)
        column.addWidget(self.message)
        column.addWidget(self.error)
        column.addLayout(grid)
        column.addWidget(buttons)

    def show_report(self, report: dict, path: Path) -> None:
        """Fill the report from `textedit.apply`'s own answer."""
        self._path = Path(path)
        self.error.setVisible(False)
        self.message.setText("Export complete")
        self.values["File"].setText(self._path.name)
        self.values["Applied"].setText(f"{report.get('in_place', 0) + report.get('moved', 0)}"
                                       " text edits")
        self.values["Moved"].setText(f"{report.get('moved', 0)} records")
        self.values["Refused"].setText(f"{report.get('refused', 0)}")
        self.values["Output size"].setText(f"{report.get('output_bytes', 0)} bytes")
        self.values["SHA-256"].setText(str(report.get("output_sha256", "")))
        self.copy_button.setEnabled(bool(report.get("output_sha256")))
        self.folder_button.setEnabled(True)

    def show_error(self, message: str) -> None:
        """Show the engine's own sentence, with nothing written beside it."""
        self._path = None
        self.message.setText("Export refused")
        self.error.setText(message)
        self.error.setVisible(True)
        for value in self.values.values():
            value.setText("")
        self.copy_button.setEnabled(False)
        self.folder_button.setEnabled(False)

    def error_text(self) -> str:
        return self.error.text()

    def _copy_digest(self) -> None:
        digest = self.values["SHA-256"].text()
        if digest:
            QGuiApplication.clipboard().setText(digest)

    def _open_folder(self) -> None:
        if self._path is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._path.parent)))
