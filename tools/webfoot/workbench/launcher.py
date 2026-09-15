"""WORKBENCH-001 T2B.2 - Launch tab.

`LauncherTab` runs the built ROM in mGBA. v1 flow is exactly: locate mGBA ->
verify the executable exists -> launch. It is a direct, fire-and-forget
`subprocess.Popen([mgba_exe, rom_path])` (list form, no shell): control returns
to the UI at once, and a short QTimer debounce re-enables the button.

Deliberately NOT here (the maintainer RESOLVED): no Lua injection (`inject_mgba_lua.ps1`
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

from . import settings
from .session import Session

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
        self._sync_rom_from_session()
        rom_browse = QPushButton("Browse...")
        rom_browse.clicked.connect(self._pick_rom)

        self._mgba_field = QLineEdit(_initial_mgba())
        self._mgba_field.setPlaceholderText("mGBA executable")
        mgba_browse = QPushButton("Browse...")
        mgba_browse.clicked.connect(self._pick_mgba)

        self._launch_button = QPushButton("Launch in mGBA")
        self._launch_button.clicked.connect(self._launch)

        rom_row = QHBoxLayout()
        rom_row.addWidget(QLabel("ROM:"))
        rom_row.addWidget(self._rom_field, 1)
        rom_row.addWidget(rom_browse)

        mgba_row = QHBoxLayout()
        mgba_row.addWidget(QLabel("mGBA:"))
        mgba_row.addWidget(self._mgba_field, 1)
        mgba_row.addWidget(mgba_browse)

        layout = QVBoxLayout(self)
        layout.addLayout(rom_row)
        layout.addLayout(mgba_row)
        layout.addWidget(self._launch_button)
        layout.addStretch(1)

    def _sync_rom_from_session(self) -> None:
        """Populate the ROM field from the last build, if any."""
        last = getattr(self._session.last_build, "output_path", None)
        if last is not None:
            self._rom_field.setText(str(last))
        else:
            self._rom_field.clear()

    def on_session_changed(self) -> None:
        """Re-read session state (e.g. after a build sets last_build)."""
        self._sync_rom_from_session()

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
