"""The summary after an export: the file, what the plan did, and its digest.

A report, not a celebration. Every fact is the engine's own answer from
`textedit.apply`, the digest is shown in the data face and can be copied, and the
single action closes the window. A report that carries a refusal says so in the
heading rather than presenting the result as a clean success.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import theme

#: The fact rows, in reading order. The digest is the one value that identifies
#: itself, and it still gets a label, because a bare hash does not say what it hashes.
FACTS = ("File", "Edits applied", "Records moved", "Output size")


class ExportDialog(QDialog):
    """The one window an export ends in."""

    def __init__(self, report: dict, path: str | Path,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        shape = theme.active_metrics()
        self.setWindowTitle("Export")
        self.setModal(True)
        self.path = Path(path)
        self.message = QLabel()
        self.message.setProperty("role", "heading")
        self.refusal = QLabel()
        self.refusal.setWordWrap(True)
        self.refusal.setProperty("role", "caption")
        self.refusal.setVisible(False)
        self.values: dict[str, QLabel] = {}
        form = QFormLayout()
        form.setHorizontalSpacing(shape.pad_xl)
        form.setVerticalSpacing(shape.pad_sm)
        for name in FACTS:
            self.values[name] = self._fact(form, name)
        self.copy_button = QToolButton()
        self.copy_button.setIcon(theme.icon("copy"))
        self.copy_button.setToolTip("Copy the SHA-256 digest")
        self.copy_button.setAccessibleName("Copy the SHA-256 digest")
        self.copy_button.clicked.connect(self._copy_digest)
        self.values["SHA-256"] = QLabel()
        self.values["SHA-256"].setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        self.values["SHA-256"].setFont(theme.mono_font())
        digest_row = QHBoxLayout()
        digest_row.setSpacing(shape.pad_sm)
        digest_row.addWidget(self.values["SHA-256"], 1)
        digest_row.addWidget(self.copy_button)
        form.addRow(QLabel("SHA-256"), digest_row)
        self.close_button = QPushButton("Close")
        self.close_button.setDefault(True)
        self.close_button.setProperty("role", "primary")
        self.close_button.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        column = QVBoxLayout(self)
        column.setContentsMargins(shape.pad_xl, shape.pad_xl, shape.pad_xl, shape.pad_lg)
        column.setSpacing(shape.gap)
        column.addWidget(self.message)
        column.addWidget(self.refusal)
        column.addLayout(form)
        column.addLayout(buttons)
        self.show_report(report)

    def _fact(self, form: QFormLayout, name: str) -> QLabel:
        """One labelled value. The file reads as a name, the numbers as data."""
        label = QLabel(name)
        label.setProperty("role", "caption")
        value = QLabel()
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        value.setFont(theme.fonts().body if name == "File" else theme.mono_font())
        form.addRow(label, value)
        return value

    def show_report(self, report: dict) -> None:
        """Fill the facts from the engine's own answer."""
        refused = int(report.get("refused", 0) or 0)
        self.message.setText("Export complete" if not refused
                             else f"Export complete, with {refused} refused")
        self.refusal.setText(
            f"{refused} edit(s) were refused and are not in the output. The edit list "
            "names each one, and why." if refused else "")
        self.refusal.setVisible(bool(refused))
        self.values["File"].setText(self.path.name)
        self.values["Edits applied"].setText(str(report.get("in_place", 0)))
        self.values["Records moved"].setText(str(report.get("moved", 0)))
        self.values["Output size"].setText(f"{report.get('output_bytes', 0)} bytes")
        digest = str(report.get("output_sha256", ""))
        self.values["SHA-256"].setText(digest)
        self.copy_button.setEnabled(bool(digest))

    def digest(self) -> str:
        return self.values["SHA-256"].text()

    def _copy_digest(self) -> None:
        digest = self.values["SHA-256"].text()
        if digest:
            QGuiApplication.clipboard().setText(digest)
