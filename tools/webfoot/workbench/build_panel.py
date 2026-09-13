"""WORKBENCH-001 T2B.1 - Build panel tab.

The Build tab. It owns the project lifecycle the CLI already exposes - extract a
new project from the open ROM, open an existing one, validate it against the
base ROM, and build a NEW image - and nothing else. Every ROM-format decision
stays behind the SDK (`build.extract_project`/`validate_project`/`build_project`);
this widget carries paths and renders the structured `ValidationReport` /
`BuildResult` those functions return.

THE SAFETY INVARIANT: the Workbench must NEVER overwrite the canonical source
ROM. The generated output ROM FILE path is compared against `session.rom_path`
BEFORE `build_project` is called, and a match is refused here in the GUI - the
check is never delegated to the SDK. The output DIRECTORY being the source ROM's
parent is allowed; only the final FILE path is compared. `is_safe_output_path`
is a module-level, Qt-free function so that guard is unit-testable without a GUI.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMessageBox,
                               QPlainTextEdit, QPushButton, QVBoxLayout,
                               QWidget)

from .. import build as build_sdk
from ..project import ProjectError
from ..write import WriteError
from .session import Session

#: The generated ROM filename convention (reviewed-solution, RESOLVED): the
#: output FILE is the profile id plus `_modified.gba`, inside the chosen output
#: directory. build_project takes a FILE path, not a directory, so the panel
#: must construct this - and the safety guard compares THIS resolved file path.
_OUTPUT_SUFFIX = "_modified.gba"


def output_file_for(output_dir: Path, profile_id: str) -> Path:
    """The generated ROM file path for `profile_id` inside `output_dir`."""
    return Path(output_dir) / f"{profile_id}{_OUTPUT_SUFFIX}"


def is_safe_output_path(output_path, rom_path) -> bool:
    """True iff the generated ROM file would NOT overwrite the source ROM.

    Compares the resolved final FILE paths. Same parent directory with a
    different filename is safe; identical file path is not. This is the #1
    safety invariant of WORKBENCH-001, kept Qt-free so it is testable without a
    GUI (critical-path test 4).
    """
    return Path(output_path).resolve() != Path(rom_path).resolve()


class BuildPanelTab(QWidget):
    """Extract / open, validate, and build a project against the open ROM."""

    buildFinished = Signal()  # emitted after a successful build; Launcher re-reads session.
    projectChanged = Signal()  # emitted after open/extract so Inspector can re-evaluate editing.

    def __init__(self, session: Session, catalog) -> None:
        super().__init__()
        self._session = session
        self._catalog = catalog
        self._open_button = QPushButton("Open Project")
        self._open_button.clicked.connect(self._on_open_project)

        self._extract_button = QPushButton("Extract")
        self._extract_button.clicked.connect(self._on_extract)

        self._rom_label = QLabel()
        self._rom_label.setTextInteractionFlags(self._rom_label.textInteractionFlags())

        self._output_button = QPushButton("Choose Output Directory")
        self._output_button.clicked.connect(self._on_choose_output)

        self._validate_button = QPushButton("Validate")
        self._validate_button.clicked.connect(self._on_validate)

        self._build_button = QPushButton("Build")
        self._build_button.clicked.connect(self._on_build)

        self._status = QPlainTextEdit()
        self._status.setReadOnly(True)

        buttons = QHBoxLayout()
        buttons.addWidget(self._open_button)
        buttons.addWidget(self._extract_button)
        buttons.addWidget(self._output_button)
        buttons.addWidget(self._validate_button)
        buttons.addWidget(self._build_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._rom_label)
        layout.addLayout(buttons)
        layout.addWidget(self._status, 1)

        self._refresh()

    # -- state ---------------------------------------------------------------

    def _rom_open(self) -> bool:
        return self._session.rom_path is not None

    def on_session_changed(self) -> None:
        """Re-sync the panel from the session (e.g. after a ROM opens)."""
        self._refresh()

    def _refresh(self) -> None:
        """Enable each control by the state its action needs, per the contract."""
        rom_open = self._rom_open()
        has_project = self._session.project_dir is not None
        self._rom_label.setText(
            f"Base ROM: {self._session.rom_path}" if rom_open
            else "No ROM open - open the required base ROM in the Atlas tab."
        )
        # Extract: only when a ROM is open AND no project is loaded.
        self._extract_button.setEnabled(rom_open and not has_project)
        # Validate: once a project is set AND a compatible ROM is open.
        self._validate_button.setEnabled(rom_open and has_project)
        # Build: only when the last ValidationReport passed.
        self._build_button.setEnabled(self._session.validation_current)

    def _output_dir(self) -> Path | None:
        return self._session.output_dir

    # -- Open Project --------------------------------------------------------

    def _on_open_project(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Open Project")
        if not chosen:
            return
        # A directory with no project.toml raises when validated; catch here so
        # an invalid pick is a QMessageBox, not a traceback (GAP-11). Validation
        # itself is the operator's next step, so we only record the dir now and
        # let _on_validate surface any read_project error.
        self._session.set_project(Path(chosen))
        if self._rom_open():
            self._status.setPlainText(f"Project set: {chosen}\nValidate to continue.")
        else:
            self._status.setPlainText(
                f"Project set: {chosen}\n"
                "Open the required base ROM in the Atlas tab before validating."
            )
        self._refresh()
        self.projectChanged.emit()

    # -- Extract -------------------------------------------------------------

    def _on_extract(self) -> None:
        if not self._rom_open():
            QMessageBox.information(self, "Extract", "Open a ROM first.")
            return
        chosen = QFileDialog.getExistingDirectory(self, "Extract project into")
        if not chosen:
            return
        try:
            build_sdk.extract_project(self._session.rom_path, chosen, self._catalog)
        except (build_sdk.BuildError, ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Extract", str(exc))
            return
        self._session.set_project(Path(chosen))
        self._status.setPlainText(f"Extracted project: {chosen}\nValidate to continue.")
        self._refresh()
        self.projectChanged.emit()

    # -- Output directory ----------------------------------------------------

    def _on_choose_output(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Choose Output Directory")
        if not chosen:
            return
        self._session.output_dir = Path(chosen)
        self._refresh()

    # -- Validate ------------------------------------------------------------

    def _on_validate(self) -> None:
        try:
            report = build_sdk.validate_project(
                self._session.project_dir, self._session.rom_path, self._catalog)
        except (build_sdk.BuildError, ProjectError, OSError) as exc:
            # Invalid project dir (no project.toml) surfaces here (GAP-11).
            self._session.record_validation(False)
            QMessageBox.critical(self, "Validate", str(exc))
            self._refresh()
            return

        self._session.record_validation(report.passed)
        if report.passed:
            self._status.setPlainText(
                f"Validation passed for {report.project_name} "
                f"(profile {report.profile_id}).\n"
                f"enemies={report.enemy_count} characters={report.character_count} "
                f"strings={report.string_count} maps={report.map_count}\n"
                "Build is now available."
            )
        else:
            problems = "\n".join(f"  - {p}" for p in report.problems)
            self._status.setPlainText(
                f"Validation FAILED with {len(report.problems)} problem(s):\n{problems}"
            )
        self._refresh()

    # -- Build ---------------------------------------------------------------

    def _on_build(self) -> None:
        if not self._session.validation_current:
            QMessageBox.information(
                self, "Build", "Project validation is stale. Validate again before building."
            )
            self._refresh()
            return
        if self._output_dir() is None:
            QMessageBox.information(self, "Build", "Choose an output directory first.")
            return
        output_path = output_file_for(self._output_dir(), self._session.profile.id)

        # THE SAFETY INVARIANT: refuse before calling the SDK if the generated
        # file would overwrite the source ROM. The GUI does this itself.
        if not is_safe_output_path(output_path, self._session.rom_path):
            QMessageBox.critical(
                self, "Build refused",
                f"The generated ROM would overwrite the source ROM:\n{output_path}\n"
                "Choose a different output directory or the source ROM would be lost."
            )
            return

        try:
            self._run_build(output_path)
        except (build_sdk.BuildError, ProjectError) as exc:
            QMessageBox.critical(self, "Build", str(exc))
            return
        except WriteError as exc:
            # WriteError is NOT a BuildError/ProjectError subclass, so it would
            # otherwise escape to the terminal (WORKBENCH-001 live defect). The
            # only pre-existing-file case is the "output already exists" refusal;
            # gate the overwrite offer on the file ACTUALLY existing, never on
            # the message text, and NEVER auto-delete on other WriteErrors.
            if not Path(output_path).exists():
                QMessageBox.critical(self, "Build", str(exc))
                return
            # SAFETY: re-assert the output is not the source ROM before deleting.
            # The pre-build guard already proved this, but the delete is the one
            # irreversible act here, so it re-checks against exactly output_path.
            if not is_safe_output_path(output_path, self._session.rom_path):
                QMessageBox.critical(
                    self, "Build refused",
                    f"Refusing to delete - the output path is the source ROM:\n{output_path}"
                )
                return
            answer = QMessageBox.question(
                self, "Overwrite existing output?",
                f"Output already exists:\n{output_path}\nOverwrite it and rebuild?",
                QMessageBox.Yes | QMessageBox.No)
            if answer != QMessageBox.Yes:
                self._status.setPlainText("Build cancelled - existing output kept.")
                return
            Path(output_path).unlink()
            try:
                self._run_build(output_path)
            except (build_sdk.BuildError, ProjectError, WriteError) as exc2:
                QMessageBox.critical(self, "Build", str(exc2))
                return

    def _run_build(self, output_path) -> None:
        """Build, record the result, and emit buildFinished. Raises on failure."""
        result = build_sdk.build_project(
            self._session.project_dir, self._session.rom_path,
            output_path, self._catalog)
        self._session.record_build(result)
        self._status.setPlainText(f"Build succeeded: {result.output_path}")
        self.buildFinished.emit()

    def on_project_mutated(self) -> None:
        """Refresh immediately after an Inspector Apply/Revert invalidates state."""
        self._status.setPlainText("Project changed. Validate again before building.")
        self._refresh()
