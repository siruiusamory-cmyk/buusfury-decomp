"""WORKBENCH-001 T2B.2 - Launch tab.

`LauncherTab` runs the built ROM in mGBA. v1 flow is exactly: locate mGBA ->
verify the executable exists -> launch. It is a direct, fire-and-forget
`subprocess.Popen([mgba_exe, rom_path])` (list form, no shell): control returns
to the UI at once, and a short QTimer debounce re-enables the button.

Deliberately NOT here (a review decision): no Lua injection (`inject_mgba_lua.ps1`
is future Debug/Runtime tooling), no runtime-config module, no required-version
accessor. A version is DISPLAY-ONLY and never gates launch - a wrong/old mGBA
must not reject the user's install.

THIN: no ROM-format knowledge. The built-ROM path comes from
`session.last_build.output_path` or a manual file picker; the mGBA path comes
from `shutil.which` or a manual override.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)

from . import settings, theme
from .session import Session
from .widgets import PanelHeader

# mGBA's PATH names (README executable-name conventions); which() adds .exe on Windows.
_MGBA_NAMES = ("mgba-qt", "mgba")
_DEBOUNCE_MS = 750


def _detect_mgba() -> str:
    """First mGBA on PATH, or '' if none. shutil.which handles the .exe suffix."""
    for name in _MGBA_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return ""


def _initial_mgba() -> str:
    """Saved path if it still exists, else PATH detection. A stale saved path
    falls back to detection rather than showing a dead path. Fails safe."""
    try:
        saved = settings.load_mgba_path()
    except Exception:  # pragma: no cover - helper already fails safe
        saved = None
    if saved and Path(saved).is_file():
        return saved
    return _detect_mgba()


class LauncherTab(QWidget):
    """Pick the built ROM + mGBA, then launch mGBA on the ROM (fire-and-forget)."""

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

        self._rom_field = QLineEdit()
        self._rom_field.setPlaceholderText("Built ROM (.gba)")
        self._rom_field.setAccessibleName("Built ROM path")
        self._sync_rom_from_session()
        rom_browse = QPushButton("Browse\u2026")
        rom_browse.clicked.connect(self._pick_rom)

        self._mgba_field = QLineEdit(_initial_mgba())
        self._mgba_field.setPlaceholderText("mGBA executable")
        self._mgba_field.setAccessibleName("mGBA executable path")
        mgba_browse = QPushButton("Browse\u2026")
        mgba_browse.clicked.connect(self._pick_mgba)

        self._launch_button = QPushButton("Launch in mGBA")
        self._launch_button.setProperty("dbzRole", "primary")
        self._launch_button.setToolTip(
            "Run the built ROM in mGBA (Ctrl+R); this never writes a ROM"
        )
        self._launch_button.clicked.connect(self._launch)

        rom_row = QHBoxLayout()
        self._rom_caption = QLabel("ROM:")
        self._rom_caption.setProperty("dbzRole", "fieldLabel")
        rom_row.addWidget(self._rom_caption)
        rom_row.addWidget(self._rom_field, 1)
        rom_row.addWidget(rom_browse)

        mgba_row = QHBoxLayout()
        self._mgba_caption = QLabel("mGBA:")
        self._mgba_caption.setProperty("dbzRole", "fieldLabel")
        mgba_row.addWidget(self._mgba_caption)
        mgba_row.addWidget(self._mgba_field, 1)
        mgba_row.addWidget(mgba_browse)

        self._launcher_state = QLabel(
            "Run the Validate \u2192 Build chain first; this tab only launches what "
            "already exists."
        )
        self._launcher_state.setProperty("dbzRole", "hint")
        self._launcher_state.setWordWrap(True)

        # What this tab does NOT do, said once, so an empty pane is information
        # rather than dead space. It is a statement about the product's design, not
        # a slogan: launching never writes, and Save As lives where the edit is.
        self._launcher_note = QLabel(
            "DragonByte Z never writes a ROM from this tab. A layout edit is saved "
            "through Save As New ROM in the Map Browser; a project is built on the "
            "Build tab. This tab only starts mGBA on a file that already exists."
        )
        self._launcher_note.setProperty("dbzRole", "hint")
        self._launcher_note.setWordWrap(True)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        body_layout.setSpacing(theme.SPACE_SM)
        body_layout.addLayout(rom_row)
        body_layout.addLayout(mgba_row)
        body_layout.addWidget(self._launch_button)
        body_layout.addWidget(self._launcher_state)
        body_layout.addWidget(self._launcher_note)
        body_layout.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(PanelHeader("Launch"))
        layout.addWidget(body, 1)

    def _sync_rom_from_session(self) -> None:
        """Populate the ROM field from the last build, if any."""
        last = getattr(self._session.last_build, "output_path", None)
        if last is not None:
            self._rom_field.setText(str(last))
        else:
            self._rom_field.clear()

    def on_project_mutated(self) -> None:
        """A project mutation: re-arm from the session, as a session change does.

        Recorded explicitly rather than left implicit, because this surface is
        the one editor-shaped surface that stages no authoring content: the ROM
        field names a file to launch and the state text describes the session's
        last build. ``Session.project_mutated()`` has just invalidated that
        build, so re-reading the session is the whole correct response - there
        is no staged value here for CQA-05 to preserve.
        """
        self.on_session_changed()

    def on_session_changed(self) -> None:
        """Re-read session state (e.g. after a build sets last_build)."""
        self._sync_rom_from_session()
        built = getattr(self._session.last_build, "output_path", None)
        if built is not None:
            self._launcher_state.setText(
                f"Ready to launch the last build: {Path(built).name}"
            )
            self._launch_button.setEnabled(True)
        else:
            self._launcher_state.setText(
                "No built ROM yet. Run Validate then Build; this tab only launches "
                "what already exists."
            )
        self._launch_button.setEnabled(self._rom_field.text().strip() != "")

    def _pick_rom(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Built ROM", "", "ROM files (*.gba);;All files (*)")
        if path:
            self._rom_field.setText(path)

    def _pick_mgba(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "mGBA executable", "", "All files (*)")
        if path:
            self._mgba_field.setText(path)
            # Persist the moment the user picks it - not only after a launch, or
            # a set-but-not-launched path is lost on close. Never crash the app.
            try:
                settings.save_mgba_path(path)
            except Exception:  # pragma: no cover - helper already fails safe
                pass

    def _launch(self) -> None:
        mgba = self._mgba_field.text().strip()
        rom = self._rom_field.text().strip()
        if not mgba or not Path(mgba).is_file():
            QMessageBox.critical(
                self, "Launch",
                "mGBA executable not found. Set its path with Browse.")
            return
        if not rom or not Path(rom).is_file():
            QMessageBox.critical(self, "Launch", "Built ROM not found. Set its path with Browse.")
            return
        try:
            subprocess.Popen([mgba, rom])  # list form, no shell (SEC-03); fire-and-forget
        except OSError as exc:  # FileNotFoundError et al. on immediate start failure
            QMessageBox.critical(self, "Launch", f"mGBA failed to start: {exc}")
            return
        # Popen succeeded: the path was just proven runnable, so remember it.
        # A settings write must never crash the app or block launch.
        try:
            settings.save_mgba_path(mgba)
        except Exception:  # pragma: no cover - helper already fails safe
            pass
        # Debounce: re-enable after a beat so a double-click can't spawn twice.
        self._launch_button.setEnabled(False)
        QTimer.singleShot(_DEBOUNCE_MS, lambda: self._launch_button.setEnabled(True))

    def launch_built_rom(self) -> None:
        """Launch the selected built ROM through the normal launcher action."""
        self._launch()
