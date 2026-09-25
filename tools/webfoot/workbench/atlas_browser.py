"""WORKBENCH-001 T2A.1 - Atlas Browser tab.

The one tab enabled at launch. It owns "Open ROM" (the button lives inside this
tab's content), a search box with a Text / Address mode switch, and a results
table. A row activation emits
`resultActivated(dict)`; MainWindow routes that to the Inspector.

THIN by contract: this widget computes no ROM-format values. It hands phrases
and offsets to the SDK (`atlas.search_text`, `atlas.addr`/`refs_to`/`refs_from`,
`atlas_build.parse_offset`) and displays whatever those return. Each result dict
gets one added transport key `_mode` ("decoded" / "raw" / "address") so the
Inspector can branch without re-deriving anything about the bytes.

Visual direction (DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001): the tab is the
project's entry surface, so it takes GB Studio's shape rather than an editor's -
one global action row, one identity line that says which image is open and by
which profile, then the search controls directly over the results they fill. The
identity line carries a state glyph and the profile in technical type, because
"which ROM am I looking at" is the one question this surface must answer at a
glance.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QFileDialog,
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from .. import atlas as atlas_sdk
from .. import atlas_build
from . import theme
from .session import OPEN_ROM_FAILURES, Session
from .widgets import PanelHeader, StateChip, ToolStrip

_COLUMNS = ("Offset", "Identity", "Match", "Preview")
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
        #: Set by `EditorHost.add_surface`. This surface publishes its status
        #: through the host rather than drawing it, so the shell's one status bar
        #: is the only place the line is rendered.
        self._host = None

        # -- one identity row: this surface owns NO project action -------------
        #
        # Atlas used to carry its own "Open ROM…" button while the shell's strip
        # already owned ROM loading, so the same command existed twice on one
        # screen. Atlas is a search and inspection surface; loading an image is a
        # project action with exactly one owner (the shell's Open ROM action, which
        # calls this module's dialog). From here the row states identity only, and
        # reacts to the session.
        #
        # `_load_status` is this editor's status HOLDER, not a second status row.
        # It is deliberately absent from the layout below: the shell owns the one
        # physical status bar and mirrors this text into it, which is the same
        # arrangement the Graphics, Maps, Scene and Inspector editors use. It used
        # to be drawn here as well, so "No ROM loaded." and the profile identity
        # appeared at both the top and the foot of the same screen.
        self._load_status = QLabel("No ROM loaded.")
        self._load_status.setProperty("dbzRole", "status")
        self._load_status.setWordWrap(True)
        self._load_status.setVisible(False)
        self._identity_chip = StateChip("No image open", "neutral")
        actions = ToolStrip()
        actions.add(self._identity_chip)
        actions.layout_row().setStretchFactor(self._identity_chip, 1)

        # -- search -----------------------------------------------------------
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText(
            "Search text, or an address in Address Lookup mode"
        )
        self._search_field.setClearButtonEnabled(True)
        self._search_field.setAccessibleName("Atlas search")
        self._search_field.returnPressed.connect(self._on_search)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems((_MODE_TEXT, _MODE_ADDRESS))
        self._mode_combo.setAccessibleName("Search mode")

        self._search_button = QPushButton("Search")
        self._search_button.setProperty("dbzRole", "primary")
        self._search_button.clicked.connect(self._on_search)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        search_row.setSpacing(theme.SPACE_SM)
        search_row.addWidget(self._search_field, 1)
        search_row.addWidget(self._mode_combo)
        search_row.addWidget(self._search_button)

        self._results = QTableWidget(0, len(_COLUMNS))
        self._results.setHorizontalHeaderLabels(_COLUMNS)
        self._results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._results.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._results.setAlternatingRowColors(True)
        self._results.verticalHeader().setVisible(False)
        self._results.verticalHeader().setDefaultSectionSize(theme.ROW_HEIGHT)
        self._results.setShowGrid(False)
        self._results.cellActivated.connect(self._on_activate)
        self._results.setAccessibleName("Atlas results")
        self._results_count = QLabel("no results")
        self._results_count.setProperty("dbzRole", "count")
        header = self._results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # -- assembly ---------------------------------------------------------
        self._results_header = PanelHeader("Results", trailing=self._results_count)
        head = QLabel("Search the open image")
        head.setProperty("dbzRole", "panelHeader")
        head_font = head.font()
        head_font.setBold(True)
        head_font.setPointSize(max(7, head_font.pointSize() - 1))
        head.setFont(head_font)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(actions)
        layout.addWidget(head)
        layout.addLayout(search_row)
        layout.addWidget(self._results_header)
        layout.addWidget(self._results, 1)

        # Row payloads, one per table row, carrying the added _mode key.
        self._row_results: list[dict] = []

    # -- Open ROM ------------------------------------------------------------

    def open_rom_dialog(self) -> None:
        """Choose and open a game image.

        The ONE implementation of "load an image". The shell's global Open ROM
        action calls exactly this, which is why Atlas itself carries no Open ROM
        button: one command, one owner, one place it can drift from.

        The slot is TOTAL over everything an open can fail with (CQA-06).
        `Session.open_rom` already converts the SDK families into `SessionError`,
        and `OPEN_ROM_FAILURES` names those same families here so that a family
        which ever stops being converted is still contained at the click instead
        of escaping to stderr - where this GUI has no console - and leaving the
        click looking dead (the WORKBENCH-001 lesson).

        The re-read that follows a successful open is guarded separately and
        reported in its own terms: by then the image IS open and the session
        holds it, so calling that a failed open would be untrue.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open ROM", "", "ROM files (*.gba);;All files (*)")
        if not path:
            return
        try:
            self._session.open_rom(path, self._catalog)
        except OPEN_ROM_FAILURES as exc:
            self._report_open_failure(str(exc))
            return
        profile_id = getattr(self._session.profile, "id", "?")
        self._host.set_status_text(
            f"Loaded: {self._session.rom_path}  (profile {profile_id})"
        )
        # This surface's OWN re-read is called directly, so a failure here is
        # caught. The peers reached through `romOpened` are not covered by this
        # `try`: an exception raised inside a slot driven by a signal is printed
        # and swallowed by PySide, and never reaches the emitter. The shell's
        # `_on_rom_opened` contains those, one peer at a time.
        try:
            self.on_session_changed()
        except OPEN_ROM_FAILURES as exc:
            self._report_open_refresh_failure(exc)
            return
        self.romOpened.emit()

    def _report_open_failure(self, reason: str) -> None:
        """One place a failed open becomes status text and one dialogue.

        The reason is the SDK's own message; it already names what could not be
        read or identified, so nothing is re-worded or re-derived here.
        """
        self._host.set_status_text(f"Load failed: {reason}")
        self._identity_chip.set_state("No image open", "invalid")
        QMessageBox.critical(self, "Open ROM", reason)

    def _report_open_refresh_failure(self, exc: Exception) -> None:
        """Report a surface that could not re-read an image that DID open.

        Identity is restated from the session, because the chip is the one thing
        here that says which image is open and the failed refresh may have left
        it stale. The message names the operation that failed, the reason, and
        what the user can still do.
        """
        rom = self._session.rom_path
        if rom is not None:
            kind = " \u00b7 derivative" if self._session.authored is not None else ""
            self._identity_chip.set_state(f"Open: {rom.name}{kind}", "valid")
        self._host.set_status_text(f"Opened, but a panel could not refresh: {exc}")
        QMessageBox.warning(
            self,
            "Open ROM",
            f"The image opened ({rom}), but a panel could not re-read it:\n{exc}\n\n"
            "The image is open and the session holds it. Open it again, or use "
            "the panel's own action, to retry the re-read.",
        )

    def on_session_changed(self) -> None:
        """Re-read the open image into the identity chip.

        The chip is the one thing on this surface that states *which* image is
        open, so it must never disagree with the session. It is refreshed from the
        session rather than only from this tab's own dialog, because a ROM can also
        be opened for the shell (and by a capture harness) without going through
        that dialog.
        """
        rom = self._session.rom_path
        profile = self._session.profile
        if rom is None:
            self._identity_chip.set_state("No image open", "neutral")
            self._identity_chip.setToolTip("")
            self._host.set_status_text("No ROM loaded.")
            return
        profile_id = getattr(profile, "id", "?")
        kind = " \u00b7 derivative" if self._session.authored is not None else ""
        self._identity_chip.set_state(f"Open: {rom.name}{kind}", "valid")
        self._identity_chip.setToolTip(f"{rom}\nprofile {profile_id}")
        # The chip above already names the open image, and the shell's status bar
        # states it too. The line this editor publishes therefore carries only what
        # the chip does not: the resolved profile identity.
        self._host.set_status_text(f"profile {profile_id}")

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
                item = QTableWidgetItem(text)
                if c <= 2:
                    # Offsets and identities are technical detail; they must be
                    # readable and recessive, never the primary reading surface.
                    item.setFont(theme.mono_font())
                self._results.setItem(r, c, item)
        self._results_count.setText(f"{len(rows)} result(s)" if rows else "no results")

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
