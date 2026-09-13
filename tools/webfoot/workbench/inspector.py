"""WORKBENCH-001 T2A.2 - Inspector tab.

Shows one activated search result. It renders BOTH result shapes the Atlas
browser can emit (tagged by the `_mode` transport key):

  (a) decoded-text - handle fields come from the `identity` sub-dict, while
      container/decompressor come from the OUTER row (different dict levels);
  (b) address-mode - coverage / objects / observations from the address query.

THIN by contract: no bit arithmetic, no handle masks, no offset literals, no
record-type constants. Recovered fields are displayed as OPAQUE LABELS exactly
as the SDK returned them. The "Edit Text" field is DISABLED - no compressed-text
authoring API exists (Outcome B).
"""

from __future__ import annotations

from PySide6.QtWidgets import (QAbstractItemView, QFormLayout, QGroupBox,
                               QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)
from PySide6.QtGui import QGuiApplication

_EDIT_DISABLED_LABEL = "Edit Text - Not yet supported"


class InspectorTab(QWidget):
    """Read-only view of the selected result; copy buttons for RE workflow."""

    def __init__(self) -> None:
        super().__init__()

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)

        # Handle fields, each with a copy button (RE workflow).
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

        self._edit = QLineEdit()
        self._edit.setEnabled(False)
        self._edit.setPlaceholderText(_EDIT_DISABLED_LABEL)
        self._edit.setToolTip(
            "No compressed-text authoring API exists yet; this field is a "
            "placeholder for a future capability.")

        layout = QVBoxLayout(self)
        layout.addWidget(self._text, 1)
        layout.addWidget(handle_box)
        layout.addWidget(refs_box, 1)
        layout.addWidget(QLabel(_EDIT_DISABLED_LABEL))
        layout.addWidget(self._edit)

    # -- rendering -----------------------------------------------------------

    def show_result(self, result: dict) -> None:
        self._clear()
        if result.get("_mode") == "address":
            self._show_address(result)
        else:
            self._show_text(result)

    def _show_text(self, result: dict) -> None:
        self._text.setPlainText(result.get("text") or result.get("detail") or "")

        # Container / decompressor from the OUTER row.
        for label in ("container_file_offset", "container_rom_address",
                      "decompressor", "encoding", "decoded_offset",
                      "decoded_offset_of_phrase", "match"):
            if label in result:
                self._add_handle_row(label, result[label])

        # Handle fields from the identity sub-dict (opaque labels).
        identity = result.get("identity")
        if isinstance(identity, dict):
            because = identity.get("unrecovered_because")
            if because:
                self._add_handle_row("unrecovered_because", because)
            for key in ("packed_handle", "handle_selector",
                        "handle_decoded_start", "handle_decoded_length",
                        "reference_site_count"):
                if identity.get(key) is not None:
                    self._add_handle_row(key, identity[key])
            self._fill_refs(identity.get("reference_sites") or [])

    def _show_address(self, result: dict) -> None:
        coverage = result.get("coverage")
        lines = [f"input: {result.get('input', '')}",
                 f"file_offset: {result.get('file_offset', '')}",
                 f"coverage: {getattr(coverage, 'classification', '')} "
                 f"[{getattr(getattr(coverage, 'confidence', None), 'value', '')}]",
                 f"objects: {len(result.get('objects', ()))}",
                 f"observations: {len(result.get('observations', ()))}"]
        self._text.setPlainText("\n".join(lines))

        self._add_handle_row("objects", len(result.get("objects", ())))
        self._add_handle_row("refs_to", len(result.get("refs_to", ())))
        self._add_handle_row("refs_from", len(result.get("refs_from", ())))

        sites = [str(getattr(ref, "source", "")) for ref in result.get("refs_from", ())]
        sites += [str(getattr(ref, "source", "")) for ref in result.get("refs_to", ())]
        self._fill_refs(sites)

    # -- widget helpers ------------------------------------------------------

    def _clear(self) -> None:
        self._text.clear()
        while self._handle_form.count():
            item = self._handle_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._handle_rows.clear()
        self._refs.setRowCount(0)

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
        for r, site in enumerate(sites):
            self._refs.setItem(r, 0, QTableWidgetItem(str(site)))

    def _on_copy_refs(self) -> None:
        sites = [self._refs.item(r, 0).text()
                 for r in range(self._refs.rowCount())
                 if self._refs.item(r, 0)]
        self._copy_text("\n".join(sites))

    @staticmethod
    def _copy_text(text: str) -> None:
        QGuiApplication.clipboard().setText(text)
