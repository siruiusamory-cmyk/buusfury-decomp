"""One window, every randomizer product.

This module is the warp randomizer's window with the product taken out of it. That
is not a rewrite for its own sake: the window that shipped with WARPRAND-APP-001
was already about ninety per cent product-agnostic - a ROM row with an immediate
verdict, a seed row, an output row, one emphasized button, a progress panel, a
monospace status readout and two post-success actions - and the ten per cent that
was not is enumerated in :class:`ProductPresentation`. Two products over one
window is a smaller thing to maintain than two windows, and the eventual combined
tool is the same window again with three module ids instead of one.

What a product supplies
=======================

A :class:`ProductPresentation` - its name, version, wording, default seed, output
template, the modules it offers, and whether it offers a spoiler - plus a
*service* with five methods (``verify_rom``, ``default_output_path``,
``generate_seed``, ``output_is_the_input``, ``randomize``). The window owns the
widgets, the states, the worker thread and the four failure outcomes; the product
owns the words and the module set.

Nothing here decides anything about randomization. The one rule the window does
apply itself - "the output may not be the input" - is asked of the service rather
than re-derived, so the button and the refusal can never disagree.

Appearance
==========

**This window is a client of the one DragonByte Z theme** -
:mod:`tools.webfoot.workbench.theme` - and holds no colour of its own. The theme
already derives its palette from Buu's own sprite, and the published site carries
the same tokens, so the editor, the site and every randomizer are one product
rather than three light-or-dark accidents. The window names theme *roles*
(``dbzRole``), and an architecture test fails if a hex literal ever appears in
this module's executable code.

Threading and failure surfaces
==============================

A randomization reads, parses and rewrites an 8 MB image, which is long enough for
Windows to paint "not responding" over the window, so the work runs on one
:class:`QThread` with four outcomes: success, collision (which a user can resolve
by confirming an overwrite), refusal (a sentence) and crash (a defect, with its
traceback one click away). Every dialog goes through :meth:`notify`,
:meth:`confirm` or :meth:`show_details`, so a test can answer a prompt without a
human and without a modal loop.

Keyboard
========

Every control is reachable with Tab in the order it is read, a disabled control is
passed over rather than focused, and Enter performs the one emphasized action from
anywhere on the form - the default-button behaviour a Windows user expects, which
a ``QMainWindow`` does not provide for free.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
import sys
import time
import traceback
from typing import Callable, Mapping, Sequence

from PySide6.QtCore import Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
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
from ..workbench.widgets import CheckBox
from . import registry
from .errors import OutputAlreadyExistsError, RandomizerAppError
from .module import SETTING_CHOICE
from .service import ProgressCallback, RandomizerRequest

#: The file dialog filter. GBA first, everything else still reachable, because a
#: user whose dump is named ``.bin`` should not be told their file cannot be seen.
ROM_FILTER = "Game Boy Advance ROM (*.gba *.agb *.bin);;All files (*)"

#: While a run is in flight.
RUNNING_STATUS = "Randomizing..."


@dataclass(frozen=True, slots=True)
class ModuleToggle:
    """One module as a checkbox."""

    module_id: str
    label: str
    help: str = ""


@dataclass(frozen=True, slots=True)
class ProductPresentation:
    """Everything about a product that is not behaviour.

    Kept as data so the window can be driven by a product module that contains no
    Qt at all, and so a test can present a synthetic product without a window
    subclass.
    """

    tool_name: str
    tool_version: str
    window_title: str
    executable_stem: str
    ready_status: str
    rom_placeholder: str
    rom_dialog_title: str
    choose_rom_first: str
    output_placeholder: str
    output_dialog_title: str
    choose_output: str
    output_is_input: str
    default_seed: str
    output_template: str
    disclaimer: str
    status_note: str
    #: The modules this product offers, in registry order. The window draws a
    #: checkbox for each *only when there is more than one*, so a single-module
    #: product's window is exactly the window it always was.
    module_toggles: tuple[ModuleToggle, ...] = ()
    offers_spoiler: bool = False
    spoiler_default: bool = True
    spoiler_label: str = "Generate spoiler log"
    spoiler_help: str = ""
    #: A named conservative preset, offered as a button that restores every
    #: declared default. ``None`` for a product with nothing to restore.
    preset_label: str | None = None
    preset_help: str = ""
    options_title: str = "Options"
    running_status: str = RUNNING_STATUS
    no_rom_text: str = "No ROM selected."

    @property
    def shows_module_toggles(self) -> bool:
        return len(self.module_toggles) > 1

    @property
    def allowed_modules(self) -> tuple[str, ...]:
        return tuple(toggle.module_id for toggle in self.module_toggles)

    def offers_options(self) -> bool:
        """Whether this product needs an options area at all.

        A product with one module, no settings, no spoiler and no preset must not
        grow an empty box: the warp window's layout is a published interface and an
        empty group would move every control below it.
        """
        if self.shows_module_toggles or self.offers_spoiler or self.preset_label:
            return True
        return any(
            registry.module_for(toggle.module_id).settings
            for toggle in self.module_toggles
        )


class RandomizeWorker(QThread):
    """One run of the application boundary, off the GUI thread.

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

    def __init__(self, service, request: RandomizerRequest, *, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        # The progress callback is bound here rather than by the caller, so the
        # request a caller builds carries no thread-bound state.
        self._request = replace(request, on_progress=self._report_progress)

    def run(self) -> None:  # pragma: no cover - driven through the window
        try:
            outcome = self._service.randomize(self._request)
        except OutputAlreadyExistsError as exc:
            self.collided.emit(str(exc))
        except RandomizerAppError as exc:
            self.refused.emit(str(exc))
        except Exception as exc:  # a bug, not a user error: keep the traceback
            self.crashed.emit(f"{type(exc).__name__}: {exc}", traceback.format_exc())
        else:
            self.succeeded.emit(outcome)

    def _report_progress(self, step: int, total: int, label: str) -> None:
        """Called from this worker's thread; Qt queues the emit to the window."""
        self.progressed.emit(step, total, label)


class RandomizerWindow(QMainWindow):
    """The single window. Construct it with a presentation and a boundary.

    The boundary is whatever the product's service exposes. Its result object is
    treated **opaquely** except for three attributes the window itself needs -
    ``output_path``, ``output_sha256`` and ``manifest_path`` - so a product may
    report in its own shape (the warp executable still returns its v0.1.0
    ``RandomizationOutcome``) or in the shared one. A product whose result is not
    the shared :class:`~tools.webfoot.randomizer.service.RandomizerResult` must
    override :meth:`success_lines`, because the shared default is written against
    that shape.
    """

    def __init__(
        self,
        presentation: ProductPresentation,
        service,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.presentation = presentation
        self._service = service
        self._outcome = None
        self._verification = None
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
        #: One check box per offered module, and one widget per declared setting.
        self.module_checks: dict[str, QCheckBox] = {}
        self.setting_widgets: dict[tuple[str, str], QWidget] = {}
        self.spoiler_check: QCheckBox | None = None
        self.preset_button: QPushButton | None = None

        self.setWindowTitle(presentation.window_title)
        self.setMinimumWidth(620)
        self._build()
        self._apply_initial_state()
        self._size_to_the_layout()

    def _size_to_the_layout(self) -> None:
        """Open at a height the layout can honour.

        A window shown without an explicit size takes a platform default that can
        be *shorter* than the layout's own hint, and Qt then compresses whichever
        rows it must. Measured on the enemy product: the window opened 44 px short,
        which silently shrank the two buttons in the options box and both
        post-success actions from 24 px to 22 px. Nothing was clipped, so it was
        invisible in a screenshot review and only showed up as controls that were
        each two pixels lighter than the ones beside them.

        ``activate()`` first, because the layout hint is only complete once the
        layout has run; the resulting size is the larger of what the layout wants
        and what the window already demands.
        """
        layout = self.centralWidget().layout()
        if layout is not None:
            layout.activate()
        hint = self.sizeHint()
        self.resize(
            max(self.minimumWidth(), hint.width()),
            max(self.minimumHeight(), hint.height()),
        )

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
        self.rom_edit = self._field()
        self.rom_edit.setPlaceholderText(self.presentation.rom_placeholder)
        self.rom_edit.setClearButtonEnabled(True)
        self.rom_edit.textChanged.connect(self._on_rom_text_changed)
        self.rom_edit.editingFinished.connect(self._on_rom_path_edited)
        self.browse_rom_button = self._button("Browse...")
        self.browse_rom_button.clicked.connect(self.browse_for_rom)
        grid.addWidget(self._field_label("Original ROM:"), 0, 0)
        grid.addWidget(self.rom_edit, 0, 1)
        grid.addWidget(self.browse_rom_button, 0, 2)

        self.rom_status_label = QLabel(self.presentation.no_rom_text)
        self.rom_status_label.setObjectName("romStatusLabel")
        self.rom_status_label.setWordWrap(True)
        # A refusal is two or three wrapped lines. A wrapping QLabel inside a grid
        # does not reliably grow its row when its text is replaced after the first
        # layout pass, which put the second line on top of the Seed row. Reserving
        # the height of three lines up front makes the row's size independent of
        # when the text arrives, so no state can overlap its neighbour.
        status_font = self.rom_status_label.fontMetrics()
        self.rom_status_label.setMinimumHeight(status_font.lineSpacing() * 3 + 2)
        self.rom_status_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        grid.addWidget(self.rom_status_label, 1, 1, 1, 2)

        # --- seed row ---
        self.seed_edit = self._field(self.presentation.default_seed)
        self.seed_edit.textChanged.connect(self._on_seed_changed)
        self.random_seed_button = self._button("Random Seed")
        self.random_seed_button.clicked.connect(self.generate_seed)
        self.copy_seed_button = self._button("Copy Seed")
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
        self.output_edit = self._field()
        self.output_edit.setPlaceholderText(self.presentation.output_placeholder)
        self.output_edit.setClearButtonEnabled(True)
        self.output_edit.textEdited.connect(self._on_output_edited)
        self.browse_output_button = self._button("Browse...")
        self.browse_output_button.clicked.connect(self.browse_for_output)
        grid.addWidget(self._field_label("Randomized ROM:"), 3, 0)
        grid.addWidget(self.output_edit, 3, 1)
        grid.addWidget(self.browse_output_button, 3, 2)

        # --- options: only for a product that has any ------------------------
        self.options_group: QGroupBox | None = None
        if self.presentation.offers_options():
            self.options_group = self._build_options()
            outer.addWidget(self.options_group)

        # --- the action: the ONE emphasized control on this surface ---------
        self.randomize_button = self._button("Randomize", role="primary")
        self.randomize_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.randomize_button.clicked.connect(self._on_randomize_clicked)
        outer.addWidget(self.randomize_button)
        self._bind_enter_to_the_primary_action()

        self.disclaimer_label = QLabel(self.presentation.disclaimer)
        self.disclaimer_label.setProperty("dbzRole", "hint")
        self.disclaimer_label.setWordWrap(True)
        outer.addWidget(self.disclaimer_label)

        # The progress panel appears only while a run is in flight. It is driven
        # by the boundary's own phase reports, so it can lag the truth but never
        # invent it.
        self.progress_panel = QWidget()
        progress_layout = QVBoxLayout(self.progress_panel)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(theme.SPACE_SM)
        self.progress_caption = QLabel("")
        self.progress_caption.setProperty("dbzRole", "hint")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, len(self.progress_phases()))
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
        self.status_view.setFont(theme.mono_font())
        self.status_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.status_view.setFixedHeight(232)
        self.status_view.setPlainText(self.presentation.ready_status)
        outer.addWidget(self.status_view)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(theme.SPACE_SM)
        self.open_folder_button = self._button("Open Folder")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.copy_hash_button = self._button("Copy Hash")
        self.copy_hash_button.clicked.connect(self.copy_hash)
        actions.addWidget(self.open_folder_button)
        actions.addWidget(self.copy_hash_button)
        actions.addStretch(1)
        outer.addLayout(actions)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_note_label = QLabel(self.presentation.status_note)
        self.status_bar.addWidget(self.status_note_label)

    def _field(self, text: str = "") -> QLineEdit:
        """One text field, at the one control height every other control uses."""
        field = QLineEdit(text)
        field.setMinimumHeight(theme.CONTROL_HEIGHT)
        return field

    def _button(self, text: str, role: str = "") -> QPushButton:
        """One button, at the one control height and the one radius.

        The height is the theme's ``CONTROL_HEIGHT`` rather than ``TOOLBAR_HEIGHT``:
        the two are different values, and a single control that takes the larger one
        is drawn taller than every button beside it, which is what the primary
        action used to do.
        """
        button = QPushButton(text)
        if role:
            button.setProperty("dbzRole", role)
        button.setMinimumHeight(theme.CONTROL_HEIGHT)
        return button

    def _bind_enter_to_the_primary_action(self) -> None:
        """Let Enter do what the one emphasized button does.

        Qt gives the Enter key to a *default button*, and a default button only
        exists inside a ``QDialog``; this product's window is a ``QMainWindow``, so
        ``setDefault(True)`` alone binds nothing and Enter used to be inert on the
        form. A window shortcut is the mechanism that does work here.

        It is deliberately routed through :meth:`_on_randomize_clicked` rather than
        through the button's own ``click()``: the click path consults the same
        guards the button consults, so Enter can only ever do what a click would
        have done. That is also why a disabled button's state needs no special
        case - switching it off is what keeps the run it describes from starting.
        """
        self.enter_shortcuts: list[QShortcut] = []
        for key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            shortcut.activated.connect(self._on_randomize_clicked)
            self.enter_shortcuts.append(shortcut)

    def _build_options(self) -> QGroupBox:
        """The module toggles, the declared settings and the spoiler option.

        Built from declarations, not from product code: a module's settings come
        from :attr:`~tools.webfoot.randomizer.module.RandomizerModule.settings`,
        so a future module adds a control by declaring one rather than by editing
        this window.
        """
        group = QGroupBox(self.presentation.options_title)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(
            theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD
        )
        layout.setSpacing(theme.SPACE_SM)

        if self.presentation.shows_module_toggles:
            for toggle in self.presentation.module_toggles:
                module = registry.module_for(toggle.module_id)
                check = CheckBox(toggle.label)
                check.setChecked(module.default_enabled)
                check.setToolTip(toggle.help or module.description)
                check.toggled.connect(self._on_module_toggled)
                self.module_checks[toggle.module_id] = check
                layout.addWidget(check)

        for toggle in self.presentation.module_toggles:
            module = registry.module_for(toggle.module_id)
            for setting in module.settings:
                row = QHBoxLayout()
                row.setContentsMargins(0, 0, 0, 0)
                row.setSpacing(theme.SPACE_SM)
                label = self._field_label(setting.label + ":")
                label.setToolTip(setting.help)
                row.addWidget(label)
                if setting.kind == SETTING_CHOICE:
                    combo = QComboBox()
                    # The declared default is listed first and selected, so the
                    # control opens on the choice the module ships rather than on
                    # whichever option happens to sort first.
                    ordered = [setting.default] + [
                        choice for choice in setting.choices if choice != setting.default
                    ]
                    for choice in ordered:
                        combo.addItem(_choice_label(choice), choice)
                    combo.setCurrentIndex(0)
                    combo.setToolTip(setting.help)
                    combo.currentIndexChanged.connect(self._refresh_randomize_enabled)
                    self.setting_widgets[(module.id, setting.key)] = combo
                    row.addWidget(combo)
                else:
                    check = CheckBox()
                    check.setChecked(bool(setting.default))
                    check.setToolTip(setting.help)
                    check.toggled.connect(self._refresh_randomize_enabled)
                    self.setting_widgets[(module.id, setting.key)] = check
                    row.addWidget(check)
                row.addStretch(1)
                layout.addLayout(row)

        if self.presentation.offers_spoiler:
            self.spoiler_check = CheckBox(self.presentation.spoiler_label)
            self.spoiler_check.setChecked(self.presentation.spoiler_default)
            self.spoiler_check.setToolTip(self.presentation.spoiler_help)
            self.spoiler_check.toggled.connect(self._refresh_randomize_enabled)
            layout.addWidget(self.spoiler_check)

        if self.presentation.preset_label:
            self.preset_button = self._button(self.presentation.preset_label)
            self.preset_button.setToolTip(self.presentation.preset_help)
            self.preset_button.clicked.connect(self.apply_preset)
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.addWidget(self.preset_button)
            row.addStretch(1)
            layout.addLayout(row)

        self._sync_setting_enabled()
        return group

    def apply_preset(self) -> None:
        """Restore every declared default: modules, settings and the spoiler.

        This is what "the STREAM SAFE preset" means in the window, and it is
        deliberately not a second copy of the preset: each value restored is the
        one the module or the product *declares*, so a preset can never drift from
        the configuration the core ships.
        """
        for module_id, check in self.module_checks.items():
            check.setChecked(registry.module_for(module_id).default_enabled)
        for (module_id, key), widget in self.setting_widgets.items():
            descriptor = next(
                setting
                for setting in registry.module_for(module_id).settings
                if setting.key == key
            )
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(max(0, widget.findData(descriptor.default)))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(descriptor.default))
        if self.spoiler_check is not None:
            self.spoiler_check.setChecked(self.presentation.spoiler_default)
        self._sync_setting_enabled()
        self._refresh_randomize_enabled()

    def _build_identity_row(self) -> QHBoxLayout:
        """The product name and version, on the surface, as the editor does."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(theme.SPACE_MD)

        self.title_label = QLabel(self.presentation.tool_name)
        title_font = self.title_label.font()
        title_font.setPointSize(title_font.pointSize() + 3)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        self.version_label = QLabel(f"v{self.presentation.tool_version}")
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
        """A hairline rule, painted from the theme rather than from a literal."""
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(
            f"background-color: {theme.COLORS.border}; border: none;"
        )
        return line

    def _apply_initial_state(self) -> None:
        self.rom_status_label.setText(self.presentation.no_rom_text)
        self._set_status(self.presentation.ready_status)
        self.randomize_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.copy_hash_button.setEnabled(False)
        self.rom_edit.setFocus()

    # --- dialogs (overridable so a test never blocks on a modal loop) -----

    def notify(self, message: str) -> None:
        QMessageBox.warning(self, self.presentation.tool_name, message)

    def confirm(self, message: str) -> bool:
        """Ask a yes/no question. Defaults to No, the safe answer."""
        answer = QMessageBox.question(
            self,
            self.presentation.tool_name,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def show_details(self, message: str, details: str) -> None:
        """Report a bug, keeping its traceback one click away."""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle(self.presentation.tool_name)
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

    def _set_status_lines(self, lines: Sequence[str]) -> None:
        self.status_view.setPlainText("\n".join(lines))

    def _copy(self, text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    # --- the enabled set and its settings ---------------------------------

    def enabled_modules(self) -> frozenset[str]:
        """Which modules this window would run right now."""
        if not self.module_checks:
            return frozenset(
                module_id
                for module_id in self.presentation.allowed_modules
                if registry.module_for(module_id).default_enabled
            )
        return frozenset(
            module_id for module_id, check in self.module_checks.items() if check.isChecked()
        )

    def module_settings(self) -> dict[str, dict[str, object]]:
        settings: dict[str, dict[str, object]] = {
            module_id: {} for module_id in self.presentation.allowed_modules
        }
        for (module_id, key), widget in self.setting_widgets.items():
            if isinstance(widget, QComboBox):
                settings.setdefault(module_id, {})[key] = widget.currentData()
            elif isinstance(widget, QCheckBox):
                settings.setdefault(module_id, {})[key] = widget.isChecked()
        return settings

    def spoiler_enabled(self) -> bool:
        return bool(self.spoiler_check is not None and self.spoiler_check.isChecked())

    def progress_phases(self) -> tuple[str, ...]:
        """The phases this window's current module selection would produce."""
        return registry.progress_steps(self.enabled_modules())

    def _on_module_toggled(self, _checked: bool = False) -> None:
        self._sync_setting_enabled()
        self._refresh_randomize_enabled()

    def _sync_setting_enabled(self) -> None:
        """Grey out the settings of a module that is switched off."""
        enabled = self.enabled_modules()
        for (module_id, _key), widget in self.setting_widgets.items():
            widget.setEnabled(module_id in enabled)

    def _refresh_randomize_enabled(self) -> None:
        running = self._worker is not None and self._worker.isRunning()
        verified = self._verification is not None and self._verification.ok
        has_output = bool(self.output_edit.text().strip())
        has_module = bool(self.enabled_modules())
        self.randomize_button.setEnabled(
            verified and has_output and not running and has_module
        )

    # --- state a caller or a test reads ---------------------------------

    @property
    def active_worker(self) -> RandomizeWorker | None:
        """The run in flight, so a caller can wait for it deterministically."""
        return self._worker

    @property
    def verification(self):
        return self._verification

    @property
    def outcome(self):
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
        point of validating on selection. There is deliberately no
        ``verify=False`` escape: a caller could use one to leave the *previous*
        file's verdict cached against a new path.
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
        something else.
        """
        if self._verification is None:
            return
        self._verification = None
        self._paint_unchecked(text)
        self._refresh_randomize_enabled()

    def _paint_unchecked(self, text: str) -> None:
        """The neutral state between "nothing chosen" and "checked"."""
        self.rom_status_label.setText(
            "Not checked yet." if text.strip() else self.presentation.no_rom_text
        )
        self.rom_status_label.setStyleSheet(
            f"color: {theme.color('text_secondary').name()}; background: transparent;"
        )

    def verify_selected_rom(self):
        """Verify whatever is in the ROM field and reflect it in the window.

        The cached verdict is cleared *first*, before anything can go wrong. If
        this method could ever exit with the previous file's verdict still cached,
        the window would show "Verified supported ROM" for a file that is not a
        ROM and leave Randomize enabled.
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

    def _paint_verdict(self, verification) -> None:
        """Show the verdict as the theme's state role, glyph included.

        The theme requires a state never be carried by hue alone, so the colour is
        the *second* channel here and the check/cross glyph the service already
        puts in the headline is the first.
        """
        if verification is None:
            self.rom_status_label.setText(self.presentation.no_rom_text)
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
        """A hand-typed path: verify on Enter or focus-out, not per keystroke."""
        self._after_rom_change()
        self.verify_selected_rom()

    def browse_for_rom(self) -> str | None:
        start = self._start_directory(self.rom_edit.text())
        path, _ = QFileDialog.getOpenFileName(
            self, self.presentation.rom_dialog_title, start, ROM_FILTER
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

    def default_output_name(self) -> str:
        """The output file name for the current seed, without a directory.

        Asked of the boundary rather than formatted here, so the window cannot
        drift from the name the service would actually produce.
        """
        return str(
            self._service.default_output_path(
                self.rom_edit.text().strip() or "rom.gba", self.seed_edit.text()
            ).name
        )

    def browse_for_output(self) -> str | None:
        current = self.output_edit.text().strip()
        if not current:
            rom = self.rom_edit.text().strip()
            if rom:
                current = str(
                    self._service.default_output_path(rom, self.seed_edit.text())
                )
            else:
                current = str(Path.home() / self.default_output_name())
        path, _ = QFileDialog.getSaveFileName(
            self, self.presentation.output_dialog_title, current, ROM_FILTER
        )
        if not path:
            return None
        self.set_output_path(path)
        return path

    # --- the run ---------------------------------------------------------

    def _on_randomize_clicked(self) -> None:
        self.start_randomization()

    def build_request(self, *, overwrite: bool) -> RandomizerRequest | None:
        """The request this window currently describes, or ``None`` with a reason.

        Overridable, but almost never overridden: a product that had to build its
        own request would be deciding application policy in a widget.
        """
        source = self.rom_edit.text().strip()
        output = self.output_edit.text().strip()
        enabled = self.enabled_modules()
        return RandomizerRequest(
            source_rom=Path(source),
            output_rom=Path(output),
            master_seed=self.seed_edit.text(),
            enabled=enabled,
            module_settings=self.module_settings(),
            tool_name=self.presentation.tool_name,
            tool_version=self.presentation.tool_version,
            progression=self.presentation.disclaimer,
            spoiler=self.presentation.offers_spoiler and self.spoiler_enabled(),
            overwrite=overwrite,
        )

    def start_randomization(self, *, overwrite: bool = False) -> RandomizeWorker | None:
        """Begin a run, or refuse before starting one that cannot succeed.

        Returns the worker so a caller - a test, or a script - can wait for it
        deterministically. ``None`` means the run was refused synchronously and
        the reason is on screen.
        """
        if self._worker is not None and self._worker.isRunning():
            return None

        source = self.rom_edit.text().strip()
        output = self.output_edit.text().strip()

        if not source:
            self._refuse(self.presentation.choose_rom_first)
            return None
        verification = self._verification
        if verification is None or not verification.ok:
            verification = self.verify_selected_rom()
        if verification is None:
            self._refuse(self.presentation.choose_rom_first)
            return None
        if not verification.ok:
            self._refuse(verification.problem)
            return None
        if not output:
            self._refuse(self.presentation.choose_output)
            return None
        if not self.enabled_modules():
            self._refuse(
                "No randomization is selected. Tick at least one option."
            )
            return None
        if self._service.output_is_the_input(source, output):
            # The same rule the boundary enforces, asked of the boundary, so the
            # button and the refusal cannot disagree.
            self._refuse(self.presentation.output_is_input)
            return None

        worker = RandomizeWorker(
            self._service, self.build_request(overwrite=overwrite), parent=self
        )
        worker.succeeded.connect(self._on_succeeded)
        worker.collided.connect(self._on_collided)
        worker.refused.connect(self._on_refused)
        worker.crashed.connect(self._on_crashed)
        worker.progressed.connect(self._on_progress)
        worker.finished.connect(self._on_worker_finished)
        self._worker = worker

        self._set_status(self.presentation.running_status)
        self._start_progress()
        self.randomize_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.copy_hash_button.setEnabled(False)
        worker.start()
        return worker

    # --- progress --------------------------------------------------------

    def _start_progress(self) -> None:
        phases = self.progress_phases()
        self.progress_bar.setRange(0, len(phases))
        self.progress_bar.setValue(0)
        self.progress_caption.setText(phases[0] + "\u2026")
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

    # --- outcomes ---------------------------------------------------------

    def success_lines(self, outcome) -> Sequence[str]:
        """The success block. Overridden by a product with its own vocabulary.

        The shared default is deliberately neutral: it names the seed, the
        modules and their reported summaries, and the three paths. A product that
        has shown the same block since v0.1.0 overrides this to keep it.
        """
        return outcome.success_lines()

    def _on_succeeded(self, outcome) -> None:
        self._outcome = outcome
        self._set_status_lines(list(self.success_lines(outcome)))
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

        A run publishes its ROM through a staged temporary file, so abandoning it
        is safe on disk - but a ``QThread`` destroyed while it is still running is
        a hard error at interpreter exit, and a user who clicks the X a second
        early should not see one. The wait is bounded so a genuinely stuck run
        cannot make the window unclosable.
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


def _choice_label(choice: str) -> str:
    """``stream-safe`` -> ``Stream safe``. One place, so both products agree."""
    return choice.replace("-", " ").replace("_", " ").capitalize()


# --- the release-verification entry ------------------------------------------
#
# A shipped build is a windowed executable: it has no console, so it cannot be
# verified by piping anything into it. The smoke entry exists so a *released
# binary* can be driven end to end - the same window, the same verification, the
# same worker thread, the same boundary - and asked for a machine-readable
# report. It is a release hook, not product configuration: it cannot change what
# the randomizer does, and with no arguments nothing about the window changes.

SMOKE_FLAG = "--smoke"


@dataclass(frozen=True, slots=True)
class SmokeRequest:
    """One release-verification run, as asked for on the command line."""

    rom: str
    output: str
    seed: str | None
    report: str | None
    #: Product-specific extras, so a product can smoke its own options without
    #: this shared parser growing a branch per product.
    options: Mapping[str, str] = field(default_factory=dict)


def parse_smoke_arguments(
    argv: Sequence[str],
    *,
    usage: str,
    extra_flags: Sequence[str] = (),
    boolean_flags: Sequence[str] = (),
    error_type: type[Exception] = RandomizerAppError,
) -> SmokeRequest | None:
    """The smoke request in ``argv``, or ``None`` for an ordinary launch.

    Parsed by hand rather than with :mod:`argparse` on purpose: a windowed build
    has nowhere to print a usage error, and ``argparse`` would call ``sys.exit``
    on a typo before the window could say anything.

    ``extra_flags`` take a value; ``boolean_flags`` do not, and are recorded as
    ``"1"`` in ``options`` so a product can smoke its own switches without this
    parser growing a branch per product.
    """
    if SMOKE_FLAG not in argv:
        return None
    known = ("--rom", "--output", "--seed", "--report", *extra_flags)
    options: dict[str, str] = {}
    values: dict[str, str] = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in known:
            if index + 1 >= len(argv):
                raise error_type(f"{token} needs a value")
            values[token[2:]] = argv[index + 1]
            index += 2
            continue
        if token in boolean_flags:
            options[token[2:]] = "1"
            index += 1
            continue
        index += 1
    for required in ("rom", "output"):
        if not values.get(required):
            raise error_type(f"{SMOKE_FLAG} needs --{required}. Usage:\n\n{usage}")
    options.update(
        {flag[2:]: values[flag[2:]] for flag in extra_flags if values.get(flag[2:])}
    )
    return SmokeRequest(
        rom=values["rom"],
        output=values["output"],
        seed=values.get("seed"),
        report=values.get("report"),
        options=options,
    )


def drive_smoke(
    app: QApplication,
    window: RandomizerWindow,
    request: SmokeRequest,
    *,
    timeout_ms: int = 600_000,
    apply_options: Callable[[RandomizerWindow, SmokeRequest], None] | None = None,
) -> list[str]:
    """Drive one real run through the real window; return the dialogs it hit.

    Everything here goes through the window's own public path - the same
    :meth:`~RandomizerWindow.set_rom_path` the Browse button calls, the same
    :meth:`~RandomizerWindow.start_randomization` the Randomize button calls - so
    a passing smoke is evidence about the shipped wiring and not about a shortcut
    beside it. No human is at the keyboard, so no dialog may open: a modal warning
    would block the process forever and a refused smoke would look like a hang
    instead of a refusal.
    """
    messages: list[str] = []
    window.notify = messages.append
    window.confirm = lambda message: (messages.append(message), False)[1]
    window.show_details = lambda message, details: messages.append(f"{message}\n{details}")

    window.set_rom_path(request.rom)
    if request.seed is not None:
        window.seed_edit.setText(request.seed)
    if apply_options is not None:
        apply_options(window, request)
    window.set_output_path(request.output)

    worker = window.start_randomization()
    if worker is not None:
        worker.wait(timeout_ms)
        # The worker's result signals are queued into this thread, so the window
        # has not necessarily taken delivery of one just because the thread has
        # stopped. Pump until the running state ends, then once more for any
        # signal still in flight.
        deadline = time.monotonic() + 30.0
        while window.status_text() == window.presentation.running_status:
            app.processEvents()
            if time.monotonic() > deadline:
                break
            time.sleep(0.01)
        for _ in range(20):
            app.processEvents()
            time.sleep(0.005)
    return messages


def configure_application(app: QApplication, presentation: ProductPresentation) -> None:
    """Name the application and apply the one DragonByte Z theme to it.

    A client of :func:`tools.webfoot.workbench.theme.apply_app_theme`, never a
    copy of it: the palette, the style sheet, the focus ring and the control
    metrics all come from the module the editor and the published site already
    agree on, so no randomizer can drift into its own look.
    """
    app.setOrganizationName("Webfoot")
    app.setApplicationName(presentation.tool_name)
    theme.apply_app_theme(app)


def run_window(presentation: ProductPresentation, service, argv: Sequence[str]) -> int:
    """The ordinary launch: show the window and run Qt."""
    app = QApplication(list(argv))
    configure_application(app, presentation)
    window = RandomizerWindow(presentation, service)
    window.show()
    return app.exec()
