"""Inspector for Atlas results and supported semantic dialogue authoring.

The tab displays recovered Atlas fields as opaque labels. Dialogue resolution,
validation, project persistence, and retail decoding stay behind the public
dialogue-authoring API; this module contains no ROM-format knowledge.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import dialogue as dialogue_sdk
from ..project import ProjectError
from .session import Session


class InspectorTab(QWidget):
    """Inspect any result and author only SDK-mapped dialogue targets."""

    projectChanged = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session
        self._target = None
        self._original = ""
        self._project_replacement: str | None = None
        self._loading_editor = False

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)

        self._handle_form = QFormLayout()
        self._handle_rows: dict[str, QLineEdit] = {}
        handle_box = QGroupBox("Handle / Identity")
        handle_box.setLayout(self._handle_form)

        self._refs = QTableWidget(0, 1)
        self._refs.setHorizontalHeaderLabels(("Reference Site",))
        self._refs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._copy_refs = QPushButton("Copy all references")
        self._copy_refs.clicked.connect(self._on_copy_refs)
        refs_box = QGroupBox("References")
        refs_layout = QVBoxLayout(refs_box)
        refs_layout.addWidget(self._refs)
        refs_layout.addWidget(self._copy_refs)

        self._authoring_status = QLabel("Editing not available for this record yet.")
        self._target_label = QLabel("Target: —")
        self._original_label = QLabel("Original: —")
        self._replacement_label = QLabel("Current project replacement: —")
        self._edit = QLineEdit()
        self._edit.setEnabled(False)
        self._edit.textChanged.connect(self._on_editor_changed)
        self._validation_label = QLabel("")
        self._apply = QPushButton("Apply")
        self._apply.setEnabled(False)
        self._apply.clicked.connect(self._on_apply)
        self._revert = QPushButton("Revert to Original")
        self._revert.setEnabled(False)
        self._revert.clicked.connect(self._on_revert)

        author_buttons = QHBoxLayout()
        author_buttons.addWidget(self._apply)
        author_buttons.addWidget(self._revert)
        author_box = QGroupBox("Compressed Dialogue")
        author_layout = QVBoxLayout(author_box)
        author_layout.addWidget(self._authoring_status)
        author_layout.addWidget(self._target_label)
        author_layout.addWidget(self._original_label)
        author_layout.addWidget(self._replacement_label)
        author_layout.addWidget(QLabel("Replacement"))
        author_layout.addWidget(self._edit)
        author_layout.addWidget(self._validation_label)
        author_layout.addLayout(author_buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(self._text, 1)
        layout.addWidget(handle_box)
        layout.addWidget(refs_box, 1)
        layout.addWidget(author_box)

    def show_result(self, result: dict) -> None:
        self._session.selected_result = result
        self._clear()
        if result.get("_mode") == "address":
            self._show_address(result)
        else:
            self._show_text(result)

    def _show_text(self, result: dict) -> None:
        self._text.setPlainText(result.get("text") or result.get("detail") or "")
        for label in (
            "container_file_offset", "container_rom_address", "decompressor",
            "encoding", "decoded_offset", "decoded_offset_of_phrase", "match",
        ):
            if label in result:
                self._add_handle_row(label, result[label])

        identity = result.get("identity")
        if isinstance(identity, dict):
            because = identity.get("unrecovered_because")
            if because:
                self._add_handle_row("unrecovered_because", because)
            for key in (
                "packed_handle", "handle_selector", "handle_decoded_start",
                "handle_decoded_length", "reference_site_count",
            ):
                if identity.get(key) is not None:
                    self._add_handle_row(key, identity[key])
            self._fill_refs(identity.get("reference_sites") or [])
        self._refresh_authoring(result)

    def _show_address(self, result: dict) -> None:
        coverage = result.get("coverage")
        lines = [
            f"input: {result.get('input', '')}",
            f"file_offset: {result.get('file_offset', '')}",
            f"coverage: {getattr(coverage, 'classification', '')} "
            f"[{getattr(getattr(coverage, 'confidence', None), 'value', '')}]",
            f"objects: {len(result.get('objects', ()))}",
            f"observations: {len(result.get('observations', ()))}",
        ]
        self._text.setPlainText("\n".join(lines))
        self._add_handle_row("objects", len(result.get("objects", ())))
        self._add_handle_row("refs_to", len(result.get("refs_to", ())))
        self._add_handle_row("refs_from", len(result.get("refs_from", ())))
        sites = [str(getattr(ref, "source", "")) for ref in result.get("refs_from", ())]
        sites += [str(getattr(ref, "source", "")) for ref in result.get("refs_to", ())]
        self._fill_refs(sites)

    def on_session_changed(self) -> None:
        """Re-read project override state after project open/extract."""
        if self._session.selected_result is not None:
            self._refresh_authoring(self._session.selected_result)

    def _set_authoring_unavailable(self, message: str) -> None:
        self._target = None
        self._original = ""
        self._project_replacement = None
        self._authoring_status.setText(message)
        self._target_label.setText("Target: —")
        self._original_label.setText("Original: —")
        self._replacement_label.setText("Current project replacement: —")
        self._validation_label.clear()
        self._set_editor_text("")
        self._edit.setEnabled(False)
        self._apply.setEnabled(False)
        self._revert.setEnabled(False)

    def _refresh_authoring(self, result: dict) -> None:
        profile = self._session.profile
        if profile is None:
            self._set_authoring_unavailable("Editing requires an open recognized ROM.")
            return
        target = dialogue_sdk.resolve_dialogue_target(result, profile)
        if target is None:
            self._set_authoring_unavailable("Editing not available for this record yet.")
            return
        try:
            original = dialogue_sdk.get_dialogue_original(
                self._session.rom_image, profile, target
            )
        except (dialogue_sdk.DialogueAuthoringError, OSError) as exc:
            self._set_authoring_unavailable(str(exc))
            return

        self._target = target
        self._original = original
        self._target_label.setText(f"Target: {target.name}")
        self._original_label.setText(f"Original: {original}")
        if self._session.project_dir is None:
            self._set_editor_text(original)
            self._authoring_status.setText("Editing requires an open Webfoot project.")
            self._replacement_label.setText("Current project replacement: none")
            self._edit.setEnabled(False)
            self._apply.setEnabled(False)
            self._revert.setEnabled(False)
            return

        try:
            replacement = dialogue_sdk.get_dialogue_replacement(
                self._session.project_dir, profile, target
            )
        except (ProjectError, OSError) as exc:
            self._set_authoring_unavailable(f"Cannot read project: {exc}")
            return
        self._project_replacement = replacement
        self._authoring_status.setText("Editing available")
        self._replacement_label.setText(
            "Current project replacement: "
            + (replacement if replacement is not None else "none")
        )
        self._set_editor_text(replacement if replacement is not None else original)
        self._edit.setEnabled(True)
        self._revert.setEnabled(replacement is not None)
        self._on_editor_changed(self._edit.text())

    def _set_editor_text(self, text: str) -> None:
        self._loading_editor = True
        self._edit.setText(text)
        self._loading_editor = False

    def _on_editor_changed(self, text: str) -> None:
        if self._loading_editor or self._target is None or not self._edit.isEnabled():
            return
        validation = dialogue_sdk.validate_dialogue_replacement(
            self._target, text, self._session.profile
        )
        if validation.valid:
            self._validation_label.setText("✓ Valid")
        else:
            self._validation_label.setText(
                "✗ " + "; ".join(problem.message for problem in validation.problems)
            )
        current = (
            self._project_replacement
            if self._project_replacement is not None
            else self._original
        )
        self._apply.setEnabled(validation.valid and text != current)

    def _on_apply(self) -> None:
        if self._target is None or self._session.project_dir is None:
            return
        validation = dialogue_sdk.validate_dialogue_replacement(
            self._target, self._edit.text(), self._session.profile
        )
        if not validation.valid:
            self._on_editor_changed(self._edit.text())
            return
        try:
            dialogue_sdk.set_dialogue_replacement(
                self._session.project_dir, self._session.profile,
                self._target, self._edit.text(),
            )
        except (dialogue_sdk.DialogueAuthoringError, ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Apply dialogue", str(exc))
            return
        self._session.project_mutated()
        self.projectChanged.emit()
        self._refresh_authoring(self._session.selected_result)

    def _on_revert(self) -> None:
        if self._target is None or self._session.project_dir is None:
            return
        try:
            changed = dialogue_sdk.remove_dialogue_replacement(
                self._session.project_dir, self._session.profile, self._target
            )
        except (dialogue_sdk.DialogueAuthoringError, ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Revert dialogue", str(exc))
            return
        if changed:
            self._session.project_mutated()
            self.projectChanged.emit()
        self._refresh_authoring(self._session.selected_result)

    def _clear(self) -> None:
        self._text.clear()
        while self._handle_form.count():
            item = self._handle_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._handle_rows.clear()
        self._refs.setRowCount(0)
        self._set_authoring_unavailable("Editing not available for this record yet.")

    def _add_handle_row(self, label: str, value) -> None:
        field = QLineEdit(str(value))
        field.setReadOnly(True)
        copy = QPushButton("Copy")
        copy.clicked.connect(lambda _=False, f=field: self._copy_text(f.text()))
        row = QHBoxLayout()
        row.addWidget(field, 1)
        row.addWidget(copy)
        container = QWidget()
        container.setLayout(row)
        self._handle_form.addRow(label, container)
        self._handle_rows[label] = field

    def _fill_refs(self, sites: list) -> None:
        self._refs.setRowCount(len(sites))
        for row, site in enumerate(sites):
            self._refs.setItem(row, 0, QTableWidgetItem(str(site)))

    def _on_copy_refs(self) -> None:
        sites = [
            self._refs.item(row, 0).text()
            for row in range(self._refs.rowCount())
            if self._refs.item(row, 0)
        ]
        self._copy_text("\n".join(sites))

    @staticmethod
    def _copy_text(text: str) -> None:
        QGuiApplication.clipboard().setText(text)
