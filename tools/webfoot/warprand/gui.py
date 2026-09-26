"""WARPRAND-APP-001 - the one window of the *Buu's Fury Warp Randomizer*.

The window is deliberately thin. Everything it knows how to do is
:meth:`~tools.webfoot.warprand.service.WarpRandomizerService.verify_rom` or
:meth:`~tools.webfoot.warprand.service.WarpRandomizerService.randomize_warps`;
nothing here computes a destination, chooses a policy, derives an arrival or
decides whether an image is supported. The one rule it does apply itself is the
source/output alias check, and it asks the boundary for that answer rather than
re-deriving it, so the button and the refusal can never disagree.

Appearance
==========

**This window is a client of the one DragonByte Z theme** -
:mod:`tools.webfoot.workbench.theme` - and holds no colour of its own. That
module already derives its palette from Buu's own sprite (`#f2ccdf` shell,
`#a81560` identity, `#fdfbfc` work surface) and the published Webfoot site
carries the same tokens (`src/styles/global.css`: ``--pink-soft``,
``--pink-strong``, ``--surface``), so applying it makes this utility, the editor
and the site one product rather than three light-or-dark accidents.

Two consequences follow, and both are deliberate:

* the window uses the theme's **roles**, not values - ``dbzRole="primary"`` for
  the one emphasized action, ``hint`` for secondary prose, ``fieldLabel`` for
  field labels, ``technical`` for the raw readout, and
  :func:`~tools.webfoot.workbench.theme.mono_font` for the hash and paths;
* there is **no second palette here**. ``tests/unit/test_warp_randomizer_gui.py``
  asserts that this module contains no hex colour literal at all, so a later
  "small tweak" cannot fork the product's colours into a private copy.

The shell follows the editor's own shape, using only rules the theme already
publishes: a pink status bar (``QStatusBar``) under a white work surface, with
the product name and version on the surface itself, and the OS title bar
carrying the same name.

Threading
=========

A randomization reads, parses and rewrites an 8 MB image and takes a couple of
seconds, which is long enough for Windows to paint "not responding" over the
window. The work therefore runs on one :class:`QThread`; the button is disabled
and the status reads "Randomizing..." until a signal comes back. That is the
whole task framework - one worker, four outcomes, no queue and no pool.

What is *not* on the worker thread is the ROM verification, which hashes the
selected image the moment it is chosen. That is a few tens of milliseconds and
is the feedback the user is waiting for; pushing it through a thread would make
"did I pick the right file?" arrive late for no benefit.

Failure surfaces
================

A user error (a wrong ROM, an unwritable folder, an existing output) arrives
from the core as a :class:`~tools.webfoot.warprand.service.WarpRandomizerAppError`
subclass and is shown as an ordinary message. Anything else is a bug: it is shown
with a "Show Details..." button carrying the traceback, and it is not swallowed,
because a window that hides a programmer error is a window that cannot be
debugged.

Every dialog goes through :meth:`MainWindow.notify`, :meth:`MainWindow.confirm`
or :meth:`MainWindow.show_details`, so a test can answer a prompt without a human
and without a modal loop.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
import time
import traceback

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..workbench import theme
from . import service as warprand

#: The window title, and so the OS title bar's text and the task-bar entry.
WINDOW_TITLE = f"{warprand.TOOL_NAME} v{warprand.TOOL_VERSION}"

#: The file dialog filter. GBA first, everything else still reachable, because a
#: user whose dump is named ``.bin`` should not be told their file cannot be seen.
ROM_FILTER = "Game Boy Advance ROM (*.gba *.agb *.bin);;All files (*)"

#: The status shown before anything has happened.
READY_STATUS = "Ready. Choose your clean US Buu's Fury ROM."

#: While a run is in flight.
RUNNING_STATUS = "Randomizing..."

#: The placeholder for the ROM row before a file is chosen.
NO_ROM_TEXT = "No ROM selected."


class RandomizeWorker(QThread):
    """One run of the boundary, off the GUI thread.

    Four distinct outcomes rather than one error channel, because the window
    treats them differently: a collision can be *resolved* by confirming an
    overwrite, a refusal cannot, and a crash must show a traceback.
    """

    succeeded = Signal(object)
    collided = Signal(str)
    refused = Signal(str)
    crashed = Signal(str, str)
    #: ``(step, total, label)``, forwarded from the boundary's own phase reports.
    progressed = Signal(int, int, str)

    def __init__(
        self,
        service,
        source: str,
        output: str,
        seed: str,
        *,
        overwrite: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._source = source
        self._output = output
        self._seed = seed
        self._overwrite = overwrite

    def run(self) -> None:  # pragma: no cover - driven through the window
        try:
            outcome = self._service.randomize_warps(
                self._source,
                self._output,
                self._seed,
                overwrite=self._overwrite,
                on_progress=self._report_progress,
            )
        except warprand.OutputAlreadyExistsError as exc:
            self.collided.emit(str(exc))
        except warprand.WarpRandomizerAppError as exc:
            self.refused.emit(str(exc))
        except Exception as exc:  # a bug, not a user error: keep the traceback
            self.crashed.emit(f"{type(exc).__name__}: {exc}", traceback.format_exc())
        else:
            self.succeeded.emit(outcome)

    def _report_progress(self, step: int, total: int, label: str) -> None:
        """Called from this worker's thread; Qt queues the emit to the window."""
        self.progressed.emit(step, total, label)


class MainWindow(QMainWindow):
    """The single window. Construct it with a boundary, ``show()``, done."""

    def __init__(self, service=None, *, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service if service is not None else warprand.default_service()
        self._verification: warprand.RomVerification | None = None
        self._outcome: warprand.RandomizationOutcome | None = None
        self._worker: RandomizeWorker | None = None
        #: Set by :meth:`confirm` when the user accepts replacing an existing
        #: output; acted on in :meth:`_on_worker_finished`, never from inside the
        #: collision signal, so the window never starts a second run while the
        #: first thread is still unwinding.
        self._retry_with_overwrite = False
        #: True while the output name is the one this window derived, so a seed
        #: or ROM change may update it. The moment the user types or browses an
        #: output, the window stops overwriting their choice.
        self._output_is_derived = True

        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumWidth(620)
        self._build()
        self._apply_initial_state()

    # --- construction ----------------------------------------------------

    def _build(self) -> None:
        body = QWidget()
        self.setCentralWidget(body)
        outer = QVBoxLayout(body)
        outer.setContentsMargins(
            theme.SPACE_XL, theme.SPACE_LG, theme.SPACE_XL, theme.SPACE_LG
        )
        outer.setSpacing(theme.SPACE_LG)

        outer.addLayout(self._build_identity_row())
        outer.addWidget(self._separator())

        grid = QGridLayout()
        grid.setHorizontalSpacing(theme.SPACE_MD)
        grid.setVerticalSpacing(theme.SPACE_MD)
        grid.setColumnStretch(1, 1)
        outer.addLayout(grid)

        # --- ROM row ---
        self.rom_edit = QLineEdit()
        self.rom_edit.setPlaceholderText("Select your clean US Buu's Fury ROM")
        self.rom_edit.setClearButtonEnabled(True)
        self.rom_edit.textChanged.connect(self._on_rom_text_changed)
        self.rom_edit.editingFinished.connect(self._on_rom_path_edited)
        self.browse_rom_button = QPushButton("Browse...")
        self.browse_rom_button.clicked.connect(self.browse_for_rom)
        grid.addWidget(self._field_label("ROM:"), 0, 0)
        grid.addWidget(self.rom_edit, 0, 1)
        grid.addWidget(self.browse_rom_button, 0, 2)

        self.rom_status_label = QLabel(NO_ROM_TEXT)
        self.rom_status_label.setObjectName("romStatusLabel")
        self.rom_status_label.setWordWrap(True)
        # A refusal is two or three wrapped lines ("...only. This file's SHA-256
        # is ... Expected SHA-256: ..."). A wrapping QLabel inside a grid does not
        # reliably grow its row when its text is replaced after the first layout
        # pass, which put the second line on top of the Seed row. Reserving the
        # height of three lines up front makes the row's size independent of when
        # the text arrives, so no state can overlap its neighbour.
        status_font = self.rom_status_label.fontMetrics()
        self.rom_status_label.setMinimumHeight(status_font.lineSpacing() * 3 + 2)
        self.rom_status_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        grid.addWidget(self.rom_status_label, 1, 1, 1, 2)

        # --- seed row ---
        self.seed_edit = QLineEdit(warprand.DEFAULT_SEED)
        self.seed_edit.textChanged.connect(self._on_seed_changed)
        self.random_seed_button = QPushButton("Random Seed")
        self.random_seed_button.clicked.connect(self.generate_seed)
        self.copy_seed_button = QPushButton("Copy Seed")
        self.copy_seed_button.clicked.connect(self.copy_seed)
        grid.addWidget(self._field_label("Seed:"), 2, 0)
        grid.addWidget(self.seed_edit, 2, 1)
        seed_buttons = QHBoxLayout()
        seed_buttons.setContentsMargins(0, 0, 0, 0)
        seed_buttons.setSpacing(theme.SPACE_SM)
        seed_buttons.addWidget(self.random_seed_button)
        seed_buttons.addWidget(self.copy_seed_button)
        grid.addLayout(seed_buttons, 2, 2)

        # --- output row ---
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText(
            "The randomized ROM to create (a new file, never your ROM)"
        )
        self.output_edit.setClearButtonEnabled(True)
        self.output_edit.textEdited.connect(self._on_output_edited)
        self.browse_output_button = QPushButton("Browse...")
        self.browse_output_button.clicked.connect(self.browse_for_output)
        grid.addWidget(self._field_label("Output:"), 3, 0)
        grid.addWidget(self.output_edit, 3, 1)
        grid.addWidget(self.browse_output_button, 3, 2)

        # --- the action: the ONE emphasized control on this surface ---------
        self.randomize_button = QPushButton("Randomize")
        self.randomize_button.setProperty("dbzRole", "primary")
        self.randomize_button.setMinimumHeight(theme.TOOLBAR_HEIGHT)
        self.randomize_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.randomize_button.clicked.connect(self._on_randomize_clicked)
        outer.addWidget(self.randomize_button)

        self.disclaimer_label = QLabel(warprand.PROGRESSION_DISCLAIMER)
        self.disclaimer_label.setProperty("dbzRole", "hint")
        self.disclaimer_label.setWordWrap(True)
        outer.addWidget(self.disclaimer_label)

        # The progress panel appears only while a run is in flight. It is driven
        # by the boundary's own phase reports, so it can lag the truth but never
        # invent it: the caption names the phase, which is what actually tells a
        # user where a run is, because the phases are unevenly expensive.
        self.progress_panel = QWidget()
        progress_layout = QVBoxLayout(self.progress_panel)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(theme.SPACE_SM)
        self.progress_caption = QLabel("")
        self.progress_caption.setProperty("dbzRole", "hint")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, len(warprand.PROGRESS_STEPS))
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_caption)
        progress_layout.addWidget(self.progress_bar)
        self.progress_panel.setVisible(False)
        outer.addWidget(self.progress_panel)

        outer.addWidget(self._separator())

        outer.addWidget(self._field_label("Status:"))
        self.status_view = QPlainTextEdit()
        self.status_view.setReadOnly(True)
        self.status_view.setObjectName("statusView")
        # The readout is addresses, paths and a digest: the theme's technical
        # role, which is monospace and recessive by design.
        self.status_view.setFont(theme.mono_font())
        # Wrap at the viewport rather than never: a refusal sentence is longer
        # than a narrow window and must be readable without a horizontal scroll,
        # and a path or a 64-character hash that wraps is still fully visible.
        self.status_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        # Tall enough for the full success block without scrolling, which is the
        # state a user actually reads, plus a wrapped line or two.
        self.status_view.setFixedHeight(232)
        self.status_view.setPlainText(READY_STATUS)
        outer.addWidget(self.status_view)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(theme.SPACE_SM)
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.copy_hash_button = QPushButton("Copy Hash")
        self.copy_hash_button.clicked.connect(self.copy_hash)
        actions.addWidget(self.open_folder_button)
        actions.addWidget(self.copy_hash_button)
        actions.addStretch(1)
        outer.addLayout(actions)

        # The theme's own chrome: a QStatusBar is painted `background` with a
        # hairline top rule, which is the persistent-context band the editor uses.
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.policy_label = QLabel(f"Policy: {warprand.POLICY_ID}")
        self.status_bar.addWidget(self.policy_label)

    def _build_identity_row(self) -> QHBoxLayout:
        """The product name and version, on the surface, as the editor does."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(theme.SPACE_MD)

        self.title_label = QLabel(warprand.TOOL_NAME)
        title_font = self.title_label.font()
        title_font.setPointSize(title_font.pointSize() + 3)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        self.version_label = QLabel(f"v{warprand.TOOL_VERSION}")
        self.version_label.setProperty("dbzRole", "hint")

        row.addWidget(self.title_label)
        row.addWidget(self.version_label)
        row.addStretch(1)
        return row

    def _field_label(self, text: str) -> QLabel:
        """A form label. ``fieldLabel`` is the theme's role for exactly this."""
        label = QLabel(text)
        label.setProperty("dbzRole", "fieldLabel")
        return label

    @staticmethod
    def _separator() -> QFrame:
        """A hairline rule. One pixel of the theme's own border value.

        Painted from :data:`theme.COLORS` rather than from a literal, and given a
        fixed 1 px height because the sheet's ``QFrame`` background would
        otherwise make a sunken frame read as a filled block.
        """
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(
            f"background-color: {theme.COLORS.border}; border: none;"
        )
        return line

    def _apply_initial_state(self) -> None:
        self.rom_status_label.setText(NO_ROM_TEXT)
        self._set_status(READY_STATUS)
        self.randomize_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.copy_hash_button.setEnabled(False)
        # The keyboard path starts where the task does. Left to Qt, the first
        # focusable widget in creation order is the read-only readout, which then
        # draws the theme's focus ring around a panel the user cannot type into.
        self.rom_edit.setFocus()

    # --- dialogs (overridable so a test never blocks on a modal loop) -----

    def notify(self, message: str) -> None:
        """Show a user-facing message."""
        QMessageBox.warning(self, warprand.TOOL_NAME, message)

    def confirm(self, message: str) -> bool:
        """Ask a yes/no question. Defaults to No, the safe answer."""
        answer = QMessageBox.question(
            self,
            warprand.TOOL_NAME,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def show_details(self, message: str, details: str) -> None:
        """Report a bug, keeping its traceback one click away."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle(warprand.TOOL_NAME)
        box.setText("The randomizer hit an unexpected problem.")
        box.setInformativeText(
            "This is a defect in the tool, not something you did. The details "
            "below are what a bug report needs."
        )
        box.setDetailedText(f"{message}\n\n{details}")
        box.setStandardButtons(QMessageBox.StandardButton.Close)
        box.exec()

    # --- small shared helpers -------------------------------------------

    def _set_status(self, text: str) -> None:
        self.status_view.setPlainText(text)

    def _set_status_lines(self, lines: list[str]) -> None:
        self.status_view.setPlainText("\n".join(lines))

    def _copy(self, text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def _refresh_randomize_enabled(self) -> None:
        running = self._worker is not None and self._worker.isRunning()
        verified = self._verification is not None and self._verification.ok
        has_output = bool(self.output_edit.text().strip())
        self.randomize_button.setEnabled(verified and has_output and not running)

    # --- state a caller or a test reads ---------------------------------

    @property
    def active_worker(self) -> RandomizeWorker | None:
        """The run in flight, so a caller can wait for it deterministically."""
        return self._worker

    @property
    def verification(self) -> warprand.RomVerification | None:
        return self._verification

    @property
    def outcome(self) -> warprand.RandomizationOutcome | None:
        return self._outcome

    def status_text(self) -> str:
        return self.status_view.toPlainText()

    def seed_text(self) -> str:
        return self.seed_edit.text()

    def rom_path(self) -> str:
        return self.rom_edit.text()

    def output_path(self) -> str:
        return self.output_edit.text()

    # --- the ROM ---------------------------------------------------------

    def set_rom_path(self, path: str | Path) -> None:
        """Set the selected image, verify it, and re-derive the output name.

        Verification happens here rather than at Randomize time so the user is
        told immediately that they picked the wrong file, which is the whole
        point of validating on selection.

        There is deliberately no ``verify=False`` escape: a caller could use one to
        leave the *previous* file's verdict cached against a new path, which is the
        same class of stale-state defect an independent review found in this file.
        An earlier revision had that parameter; it was dead in production and is
        gone.
        """
        self.rom_edit.setText(str(path))
        self._after_rom_change()
        self.verify_selected_rom()

    def _after_rom_change(self) -> None:
        if self._output_is_derived or not self.output_edit.text().strip():
            self._derive_output_path()

    def _on_rom_text_changed(self, text: str) -> None:
        """Any change to the path invalidates the verdict *immediately*.

        Invalidated rather than re-verified, because verifying here would hash the
        image on every keystroke. The point is that no intermediate state may keep
        showing the previous file's "Verified supported ROM" while the field holds
        something else - which is how clearing the field with its own clear button
        (or retyping it) used to leave a verified verdict and an enabled Randomize
        button over an empty path. A round-2 review measured exactly that.

        Verification itself still happens on browse and on Enter/focus-out.
        """
        if self._verification is None:
            return
        self._verification = None
        self._paint_unchecked(text)
        self._refresh_randomize_enabled()

    def _paint_unchecked(self, text: str) -> None:
        """The neutral state between "nothing chosen" and "checked"."""
        self.rom_status_label.setText(
            "Not checked yet." if text.strip() else NO_ROM_TEXT
        )
        self.rom_status_label.setStyleSheet(
            f"color: {theme.color('text_secondary').name()}; background: transparent;"
        )

    def verify_selected_rom(self) -> warprand.RomVerification | None:
        """Verify whatever is in the ROM field and reflect it in the window.

        The cached verdict is cleared *first*, before anything can go wrong. If
        this method could ever exit with the previous file's verdict still cached,
        the window would show "Verified supported ROM" for a file that is not a
        ROM and leave Randomize enabled - which is exactly the defect an
        independent review found here, when the boundary raised on a file it
        could not parse instead of returning a verdict.
        """
        text = self.rom_edit.text().strip()
        self._verification = None
        if not text:
            self._paint_verdict(None)
            self._refresh_randomize_enabled()
            return None

        try:
            verification = self._service.verify_rom(text)
        except Exception as exc:  # the boundary promised never to raise
            self._paint_unreadable(exc)
            self._refresh_randomize_enabled()
            self.show_details(
                f"{type(exc).__name__}: {exc}",
                traceback.format_exc(),
            )
            return None

        self._verification = verification
        self._paint_verdict(verification)
        self._refresh_randomize_enabled()
        return verification

    def _paint_unreadable(self, exc: BaseException) -> None:
        """Report a file the boundary could not even return a verdict for.

        Randomize stays disabled, because there is no verdict saying the image is
        supported. This state exists only for a defect in the boundary; ordinary
        unreadable files come back as an UNSUPPORTED verdict with a sentence.
        """
        self.rom_status_label.setText(
            f"Unsupported ROM \u2717  This file could not be checked "
            f"({type(exc).__name__})."
        )
        self.rom_status_label.setStyleSheet(
            f"color: {theme.color('danger').name()}; background: transparent;"
        )

    def _paint_verdict(self, verification: warprand.RomVerification | None) -> None:
        """Show the verdict as the theme's state role, glyph included.

        The theme requires a state never be carried by hue alone - the maintainer
        is red-green colourblind - so the colour is the *second* channel here and
        the check/cross glyph the service already puts in the headline is the
        first.
        """
        if verification is None:
            self.rom_status_label.setText(NO_ROM_TEXT)
            self.rom_status_label.setStyleSheet(
                f"color: {theme.color('text_secondary').name()}; background: transparent;"
            )
            return
        if verification.ok:
            self.rom_status_label.setText(
                f"{verification.headline}  \u2014  SHA-256 "
                f"{verification.actual_sha256_short()}"
            )
            role = "success"
        else:
            self.rom_status_label.setText(
                f"{verification.headline}  {verification.problem}"
            )
            role = "danger"
        self.rom_status_label.setStyleSheet(
            f"color: {theme.color(role).name()}; background: transparent;"
        )

    def _on_rom_path_edited(self) -> None:
        """A hand-typed path: verify on Enter or focus-out, not per keystroke.

        Verifying per keystroke would hash an 8 MB image on every character,
        which is exactly the kind of freeze the worker thread exists to avoid.
        """
        self._after_rom_change()
        self.verify_selected_rom()

    def browse_for_rom(self) -> str | None:
        start = self._start_directory(self.rom_edit.text())
        path, _ = QFileDialog.getOpenFileName(
            self, "Select your clean US Buu's Fury ROM", start, ROM_FILTER
        )
        if not path:
            return None
        self.set_rom_path(path)
        return path

    @staticmethod
    def _start_directory(current: str) -> str:
        """Where a file dialog opens: beside the current file, else home."""
        if current.strip():
            parent = Path(current).expanduser().parent
            if parent.is_dir():
                return str(parent)
        return str(Path.home())

    # --- the seed --------------------------------------------------------

    def generate_seed(self) -> str:
        """A short, shareable seed: ``Saiyan-4821``. Not a 64-character UUID."""
        seed = self._service.generate_seed()
        self.seed_edit.setText(seed)
        return seed

    def _on_seed_changed(self, _text: str) -> None:
        if self._output_is_derived:
            self._derive_output_path()
        self._refresh_randomize_enabled()

    def copy_seed(self) -> None:
        self._copy(self.seed_edit.text())

    # --- the output ------------------------------------------------------

    def _on_output_edited(self, _text: str) -> None:
        # A hand-typed output is the user's decision and stops being re-derived.
        self._output_is_derived = False
        self._refresh_randomize_enabled()

    def _derive_output_path(self) -> None:
        rom = self.rom_edit.text().strip()
        if not rom:
            self.output_edit.setText("")
            return
        try:
            derived = self._service.default_output_path(rom, self.seed_edit.text())
        except (OSError, ValueError):
            # A path the boundary cannot turn into a name is not fatal: the user
            # can still type one, and an empty output keeps Randomize disabled.
            return
        self.output_edit.setText(str(derived))
        # setText does not emit textEdited, so the derived flag survives.
        self._output_is_derived = True
        self._refresh_randomize_enabled()

    def set_output_path(self, path: str | Path) -> None:
        self.output_edit.setText(str(path))
        self._output_is_derived = False
        self._refresh_randomize_enabled()

    def browse_for_output(self) -> str | None:
        current = self.output_edit.text().strip()
        if not current:
            rom = self.rom_edit.text().strip()
            if rom:
                current = str(
                    self._service.default_output_path(rom, self.seed_edit.text())
                )
            else:
                # Named from the same template and the same seed rule the service
                # uses, rather than from a second literal that could drift.
                current = str(
                    Path.home()
                    / warprand.OUTPUT_TEMPLATE.format(
                        seed=warprand.sanitize_seed_for_filename(self.seed_edit.text())
                    )
                )
        path, _ = QFileDialog.getSaveFileName(
            self, "Choose the randomized ROM to create", current, ROM_FILTER
        )
        if not path:
            return None
        self.set_output_path(path)
        return path

    # --- the run ---------------------------------------------------------

    def _on_randomize_clicked(self) -> None:
        self.start_randomization()

    def start_randomization(self, *, overwrite: bool = False) -> RandomizeWorker | None:
        """Begin a run, or refuse before starting one that cannot succeed.

        Returns the worker so a caller - a test, or a script - can wait for it
        deterministically. ``None`` means the run was refused synchronously and
        the reason is on screen.
        """
        if self._worker is not None and self._worker.isRunning():
            return None

        source = self.rom_edit.text().strip()
        seed = self.seed_edit.text()
        output = self.output_edit.text().strip()

        if not source:
            self._refuse("Choose your clean US Buu's Fury ROM first.")
            return None
        verification = self._verification
        if verification is None or not verification.ok:
            verification = self.verify_selected_rom()
        if verification is None:
            self._refuse("Choose your clean US Buu's Fury ROM first.")
            return None
        if not verification.ok:
            self._refuse(verification.problem)
            return None
        if not output:
            self._refuse("Choose an output file name for the randomized ROM.")
            return None
        if self._service.output_is_the_input(source, output):
            # The same rule the boundary enforces, asked of the boundary, so the
            # button and the refusal cannot disagree.
            self._refuse(
                "The output file is the input ROM. Choose a different output name; "
                "this tool never writes to the ROM you selected."
            )
            return None

        worker = RandomizeWorker(
            self._service, source, output, seed, overwrite=overwrite, parent=self
        )
        worker.succeeded.connect(self._on_succeeded)
        worker.collided.connect(self._on_collided)
        worker.refused.connect(self._on_refused)
        worker.crashed.connect(self._on_crashed)
        worker.progressed.connect(self._on_progress)
        worker.finished.connect(self._on_worker_finished)
        self._worker = worker

        self._set_status(RUNNING_STATUS)
        self._start_progress()
        self.randomize_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.copy_hash_button.setEnabled(False)
        worker.start()
        return worker

    # --- progress --------------------------------------------------------

    def _start_progress(self) -> None:
        self.progress_bar.setRange(0, len(warprand.PROGRESS_STEPS))
        self.progress_bar.setValue(0)
        self.progress_caption.setText(warprand.PROGRESS_STEPS[0] + "\u2026")
        self.progress_panel.setVisible(True)

    def _stop_progress(self) -> None:
        """Hide the panel once the run is over.

        Never left showing a finished bar: "100%" beside a success block reads as
        a second, competing statement of the same thing, and beside a refusal it
        reads as a lie.
        """
        self.progress_panel.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_caption.setText("")

    def _on_progress(self, step: int, total: int, label: str) -> None:
        """Show the phase now beginning, and the phases already finished.

        The boundary reports ``step`` as the phase being *entered*, so the bar
        shows ``step - 1``: it can lag the truth but can never claim work that
        has not completed.
        """
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(max(0, step - 1))
        self.progress_caption.setText(label + "\u2026")

    def _refuse(self, message: str) -> None:
        self._set_status(f"Cannot randomize:\n{message}")
        self.notify(message)

    def _on_succeeded(self, outcome: warprand.RandomizationOutcome) -> None:
        self._outcome = outcome
        self._set_status_lines(
            [
                "Success",
                "ROM verified \u2713",
                f"Seed: {outcome.seed}",
                f"Policy: {outcome.policy_id}",
                f"Supported: {outcome.supported}",
                f"Randomized: {outcome.randomized}",
                f"Destinations moved: {outcome.destinations_moved}",
                f"Skipped: {outcome.skipped}",
                f"Output: {outcome.output_path}",
                f"SHA-256: {outcome.output_sha256}",
                f"Manifest: {outcome.manifest_path}",
                f"Source ROM unchanged: {'yes' if outcome.source_unchanged else 'NO'}",
            ]
        )
        self.open_folder_button.setEnabled(True)
        self.copy_hash_button.setEnabled(True)

    def _on_collided(self, message: str) -> None:
        """An existing output: ask now, retry after this thread has unwound."""
        self._set_status(f"Cannot randomize:\n{message}")
        if self.confirm(f"{message}\n\nReplace the existing file?"):
            self._retry_with_overwrite = True

    def _on_refused(self, message: str) -> None:
        self._refuse(message)

    def _on_crashed(self, message: str, details: str) -> None:
        """A bug, not a user error: say so and keep the traceback reachable."""
        self._set_status(
            "The randomizer hit an unexpected problem.\n"
            f"{message}\n\n"
            "This is a defect in the tool, not something you did. "
            'Use "Show Details..." to copy the report.'
        )
        self.show_details(message, details)

    def _on_worker_finished(self) -> None:
        self._stop_progress()
        if self._retry_with_overwrite:
            self._retry_with_overwrite = False
            self._worker = None
            self.start_randomization(overwrite=True)
            return
        self._refresh_randomize_enabled()

    # --- closing ----------------------------------------------------------

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt's spelling
        """Let a run in flight finish before the window goes away.

        A run takes a few seconds and publishes its ROM through a staged
        temporary file, so abandoning it is safe on disk - but a ``QThread``
        destroyed while it is still running is a hard error at interpreter exit,
        and a user who clicks the X a second early should not see one. The wait
        is bounded so a genuinely stuck run cannot make the window unclosable.
        """
        worker = self._worker
        if worker is not None and worker.isRunning():
            worker.wait(60_000)
        super().closeEvent(event)

    # --- post-success actions -------------------------------------------

    def open_output_folder(self) -> bool:
        """Reveal the folder holding the generated ROM. Success state only."""
        if self._outcome is None:
            return False
        folder = Path(self._outcome.output_path).parent
        if not str(folder) or not folder.is_dir():
            return False
        # QDesktopServices rather than os.startfile: one code path that also
        # works if this is ever run on another platform.
        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def copy_hash(self) -> bool:
        if self._outcome is None:
            return False
        self._copy(self._outcome.output_sha256)
        return True


def configure_application(app: QApplication) -> None:
    """Name the application and apply the one DragonByte Z theme to it.

    Called once from :func:`main`. A client of
    :func:`tools.webfoot.workbench.theme.apply_app_theme`, never a copy of it:
    the palette, the style sheet, the focus ring and the control metrics all come
    from the module the editor and the published site already agree on, so this
    utility cannot drift into its own look.
    """
    app.setOrganizationName("Webfoot")
    app.setApplicationName(warprand.TOOL_NAME)
    theme.apply_app_theme(app)


# --- the release-verification entry ------------------------------------------
#
# The shipped build is a windowed executable: it has no console, so it cannot be
# verified by piping anything into it. The smoke entry exists so a *released
# binary* can be driven end to end - the same window, the same verification, the
# same worker thread, the same boundary - and asked for a machine-readable
# report. It is a release hook, not product configuration: it cannot change what
# the randomizer does, and with no arguments nothing about the window changes.

SMOKE_FLAG = "--smoke"

#: Printed by ``--help``. Short, because the whole product is short.
USAGE = f"""\
{warprand.TOOL_NAME} v{warprand.TOOL_VERSION}

  Buu-Fury-Warp-Randomizer                       open the window

  Buu-Fury-Warp-Randomizer {SMOKE_FLAG} --rom <rom> --output <rom>
      [--seed <seed>] [--report <file>]
        perform one run through the same window and write a JSON report.
        Used to verify a packaged release without a human at the keyboard.
"""


@dataclass(frozen=True, slots=True)
class SmokeRequest:
    """One release-verification run, as asked for on the command line."""

    rom: str
    output: str
    seed: str | None
    report: str | None


def parse_smoke_arguments(argv: list[str]) -> SmokeRequest | None:
    """The smoke request in ``argv``, or ``None`` for an ordinary launch.

    Parsed by hand rather than with :mod:`argparse` on purpose: a windowed build
    has nowhere to print a usage error, and ``argparse`` would call ``sys.exit``
    on a typo before the window could say anything.
    """
    if SMOKE_FLAG not in argv:
        return None
    values: dict[str, str] = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in ("--rom", "--output", "--seed", "--report"):
            if index + 1 >= len(argv):
                raise warprand.WarpRandomizerAppError(f"{token} needs a value")
            values[token[2:]] = argv[index + 1]
            index += 2
            continue
        index += 1
    for required in ("rom", "output"):
        if not values.get(required):
            raise warprand.WarpRandomizerAppError(
                f"{SMOKE_FLAG} needs --{required}. Usage:\n\n{USAGE}"
            )
    return SmokeRequest(
        rom=values["rom"],
        output=values["output"],
        seed=values.get("seed"),
        report=values.get("report"),
    )


def run_smoke(
    app: QApplication,
    request: SmokeRequest,
    *,
    service=None,
    timeout_ms: int = 600_000,
) -> tuple[int, dict]:
    """Drive one real run through the real window and report what happened.

    Everything here goes through the window's own public path - the same
    :meth:`MainWindow.set_rom_path` the Browse button calls, the same
    :meth:`MainWindow.start_randomization` the Randomize button calls - so a
    passing smoke is evidence about the shipped wiring and not about a shortcut
    beside it. ``service`` exists so this path can be tested against a stand-in
    boundary; :func:`main` never passes one.
    """
    window = MainWindow(service)
    # No human is at the keyboard, so no dialog may open: a modal warning would
    # block the process forever and a refused smoke would look like a hang
    # instead of a refusal. The window's own dialog seams exist for this.
    messages: list[str] = []
    window.notify = messages.append
    window.confirm = lambda message: (messages.append(message), False)[1]
    window.show_details = lambda message, details: messages.append(
        f"{message}\n{details}"
    )
    window.set_rom_path(request.rom)
    if request.seed is not None:
        window.seed_edit.setText(request.seed)
    window.set_output_path(request.output)

    worker = window.start_randomization()
    if worker is not None:
        worker.wait(timeout_ms)
        # The worker's result signals are queued into this thread, so the window
        # has not necessarily taken delivery of one just because the thread has
        # stopped. Pump until the running state ends, then once more for any
        # signal still in flight.
        deadline = time.monotonic() + 30.0
        while window.status_text() == RUNNING_STATUS:
            app.processEvents()
            if time.monotonic() > deadline:
                break
            time.sleep(0.01)
        for _ in range(20):
            app.processEvents()
            time.sleep(0.005)

    outcome = window.outcome
    report = {
        "tool": warprand.TOOL_NAME,
        "version": warprand.TOOL_VERSION,
        "policy": warprand.POLICY_ID,
        "ok": outcome is not None,
        "seed": window.seed_text(),
        "seed_is_launch_seed": window.seed_text() == warprand.DEFAULT_SEED,
        "rom": str(request.rom),
        "output": outcome.output_path.as_posix() if outcome else str(request.output),
        "output_sha256": outcome.output_sha256 if outcome else None,
        "manifest": outcome.manifest_path.as_posix() if outcome else None,
        "supported": outcome.supported if outcome else None,
        "randomized": outcome.randomized if outcome else None,
        "destinations_moved": outcome.destinations_moved if outcome else None,
        "skipped": outcome.skipped if outcome else None,
        "source_sha256": outcome.source_sha256 if outcome else None,
        "source_unchanged": outcome.source_unchanged if outcome else None,
        "status": window.status_text(),
        "messages": messages,
        "progress_hidden": not window.progress_panel.isVisible(),
    }
    window.close()
    return (0 if outcome is not None else 1), report


def main(argv: list[str] | None = None) -> int:
    """``python -m tools.webfoot.warprand`` - show the window and run Qt."""
    arguments = list(sys.argv if argv is None else argv)
    if "--help" in arguments or "-h" in arguments:
        print(USAGE)
        return 0
    try:
        request = parse_smoke_arguments(arguments)
    except warprand.WarpRandomizerAppError as exc:
        print(f"error: {exc}")
        return 2

    app = QApplication(arguments)
    configure_application(app)
    if request is not None:
        code, report = run_smoke(app, request)
        if request.report:
            Path(request.report).write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        print(json.dumps(report, indent=2, sort_keys=True))
        return code

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover - the module entry point
    raise SystemExit(main())
