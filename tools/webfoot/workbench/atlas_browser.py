"""WORKBENCH-001 T2A.1 - Atlas Browser tab.

The one tab enabled at launch. It owns "Open ROM" (the locked UX: the button
lives inside this tab's content, not a toolbar or menu), a search box with a
Text / Address mode switch, and a results table. A row activation emits
`resultActivated(dict)`; MainWindow routes that to the Inspector.

THIN by contract: this widget computes no ROM-format values. It hands phrases
and offsets to the SDK (`atlas.search_text`, `atlas.addr`/`refs_to`/`refs_from`,
`atlas_build.parse_offset`) and displays whatever those return. Each result dict
gets one added transport key `_mode` ("decoded" / "raw" / "address") so the
Inspector can branch without re-deriving anything about the bytes.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QFileDialog,
                               QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from .. import atlas as atlas_sdk
from .. import atlas_build
from .session import Session, SessionError

_COLUMNS = ("Container/Offset", "Identity", "Match Type", "Preview")
_MODE_TEXT = "Text Search"
_MODE_ADDRESS = "Address Lookup"


class AtlasBrowserTab(QWidget):
    """Open a ROM, search it, and activate a result for the Inspector."""

    resultActivated = Signal(dict)
    romOpened = Signal()  # MainWindow enables the post-ROM tabs on this.

    def __init__(self, session: Session, catalog) -> None:
        super().__init__()
        self._session = session
        self._catalog = catalog

        self._open_button = QPushButton("Open ROM")
        self._open_button.clicked.connect(self._on_open_rom)

        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("Search text, or an address in Address Lookup mode")
        self._search_field.returnPressed.connect(self._on_search)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems((_MODE_TEXT, _MODE_ADDRESS))

        self._search_button = QPushButton("Search")
        self._search_button.clicked.connect(self._on_search)

        self._results = QTableWidget(0, len(_COLUMNS))
        self._results.setHorizontalHeaderLabels(_COLUMNS)
        self._results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._results.cellActivated.connect(self._on_activate)

        self._load_status = QLabel("No ROM loaded.")

        top = QHBoxLayout()
        top.addWidget(self._open_button)
        top.addWidget(self._search_field, 1)
        top.addWidget(self._mode_combo)
        top.addWidget(self._search_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._load_status)
        layout.addWidget(self._results, 1)

        # Row payloads, one per table row, carrying the added _mode key.
        self._row_results: list[dict] = []

    # -- Open ROM ------------------------------------------------------------

    def _on_open_rom(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open ROM", "", "ROM files (*.gba);;All files (*)")
        if not path:
            return
        try:
            self._session.open_rom(path, self._catalog)
        except SessionError as exc:
            self._load_status.setText(f"Load failed: {exc}")
            QMessageBox.critical(self, "Open ROM", str(exc))
            return
        profile_id = getattr(self._session.profile, "id", "?")
        self._load_status.setText(f"Loaded: {self._session.rom_path}  (profile {profile_id})")
        self.romOpened.emit()

    # -- Search --------------------------------------------------------------

    def _on_search(self) -> None:
        if self._session.atlas is None:
            QMessageBox.information(self, "Search", "Open a ROM first.")
            return
        if self._mode_combo.currentText() == _MODE_ADDRESS:
            self._search_address()
        else:
            self._search_text()

    def _search_text(self) -> None:
        phrase = self._search_field.text().strip()
        if not phrase:  # empty/whitespace: no query (GAP-04/05)
            return
        result = atlas_sdk.search_text(
            self._session.atlas, phrase, self._session.decoded_text,
            rom_image=self._session.rom_image)

        rows: list[dict] = []
        for run in result["runs"]:
            rows.append({**run, "_mode": "raw"})
        for decoded in result["decoded"]:
            rows.append({**decoded, "_mode": "decoded"})
        self._populate(rows, self._text_row_cells)

    def _search_address(self) -> None:
        text = self._search_field.text().strip()
        if not text:
            return
        try:
            offset, _how = atlas_build.parse_offset(text)
        except ValueError as exc:  # AtlasBuildError + bare int(text,0) ValueError (GAP-03)
            QMessageBox.critical(self, "Address Lookup", str(exc))
            return

        from ..binary import FileOffset
        where = FileOffset(offset)
        info = atlas_sdk.addr(self._session.atlas, where)
        result = {
            "_mode": "address",
            "input": text,
            "file_offset": offset,
            "coverage": info["coverage"],
            "objects": info["objects"],
            "observations": info["observations"],
            "refs_to": atlas_sdk.refs_to(self._session.atlas, where),
            "refs_from": atlas_sdk.refs_from(self._session.atlas, where),
        }
        self._populate([result], self._address_row_cells)

    # -- Table plumbing ------------------------------------------------------

    def _populate(self, rows: list[dict], cell_fn) -> None:
        self._row_results = rows
        self._results.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, text in enumerate(cell_fn(row)):
                self._results.setItem(r, c, QTableWidgetItem(text))

    @staticmethod
    def _text_row_cells(row: dict) -> tuple[str, str, str, str]:
        if row["_mode"] == "raw":
            return (str(row.get("file_offset", "")), row.get("kind", ""),
                    row.get("match", ""), row.get("detail", ""))
        # decoded
        identity = row.get("identity") or {}
        return (str(row.get("container_file_offset", "")),
                str(identity.get("packed_handle") or "-"),
                row.get("match", ""), row.get("text", ""))

    @staticmethod
    def _address_row_cells(row: dict) -> tuple[str, str, str, str]:
        coverage = row.get("coverage")
        classification = getattr(coverage, "classification", "")
        n_refs = len(row.get("refs_to", ())) + len(row.get("refs_from", ()))
        return (row.get("input", ""), str(len(row.get("objects", ()))),
                "address", f"{classification} ({n_refs} refs)")

    def _on_activate(self, r: int, _c: int) -> None:
        if 0 <= r < len(self._row_results):
            self.resultActivated.emit(self._row_results[r])
