"""WORKBENCH-001 T2B.1 - Build panel tab.

The Build tab. It owns the project lifecycle the CLI already exposes - extract a
new project from the open ROM, open an existing one, validate it against the
base ROM, and build a NEW image - and nothing else. Every ROM-format decision
stays behind the SDK (`build.extract_project`/`validate_project`/`build_project`);
this widget carries paths and renders the structured `ValidationReport` /
`BuildResult` those functions return.

THE SAFETY INVARIANT: the Workbench must NEVER overwrite the canonical source
ROM. The generated output ROM FILE path is compared against `session.rom_path`
BEFORE `build_project` is called, and a match is refused here in the GUI. The
output DIRECTORY being the source ROM's parent is allowed; only the final FILE
path is compared. `is_safe_output_path` is a module-level, Qt-free function so
that guard is unit-testable without a GUI, and it delegates the comparison
itself to the SDK's one ownership of path identity
(`write.paths_are_the_same_file`) rather than deriving a second, weaker one.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QMessageBox,
                               QPlainTextEdit, QPushButton, QVBoxLayout,
                               QWidget)

from .. import build as build_sdk
from ..project import ProjectError
from ..write import WriteError, paths_are_the_same_file
from . import theme
from .session import Session
from .widgets import PanelHeader, StateChip

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

    Compares the resolved final FILE paths, so the same parent directory with a
    different filename is safe and an identical file path is not. The comparison
    is the SDK's (`write.paths_are_the_same_file`), which also recognises a
    hard-link or junction alias of the source - the GUI keeps only this named
    wrapper, so the invariant has one implementation and the Build tab and the
    Map Browser share it. Kept Qt-free so it is testable without a GUI
    (critical-path test 4).
    """
    return not paths_are_the_same_file(output_path, rom_path)


def _build_artefacts_for(output_path: Path) -> tuple[Path, ...]:
    """Every file one build publishes for `output_path`, in publication order.

    A build publishes more than its image: `build_project` defaults to
    `MANIFEST_BESIDE_OUTPUT`, so the provenance document lands beside the image it
    describes (CQA-12). The manifest name comes from the SDK's own authority rather
    than being rebuilt here, so the panel cannot disagree with the build about what
    a build writes.

    WORKBENCH-OVERWRITE-ATOMICITY-001. Replacing only the image left this companion
    behind, and `emit_image` refuses a destination that already exists, so the
    rebuild failed with the user's previous output already deleted.
    """
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)
    if manifest_path is None:  # pragma: no cover - MANIFEST_BESIDE_OUTPUT is set
        return (Path(output_path),)
    return (Path(output_path), Path(manifest_path))


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

        self._output_button = QPushButton("Choose Output Directory\u2026")
        self._output_button.setToolTip("Where a built ROM is written")
        self._output_button.clicked.connect(self._on_choose_output)

        self._validate_button = QPushButton("Validate")
        self._validate_button.setToolTip(
            "Check the open project against the open ROM (Ctrl+Shift+V)"
        )
        self._validate_button.clicked.connect(self._on_validate)

        self._build_button = QPushButton("Build")
        self._build_button.setProperty("dbzRole", "primary")
        self._build_button.setToolTip(
            "Build a NEW ROM from the validated project (Ctrl+B); the base ROM is "
            "never modified"
        )
        self._build_button.clicked.connect(self._on_build)

        self._status = QPlainTextEdit()
        self._status.setReadOnly(True)
        self._status.setFont(theme.mono_font())
        self._status.setAccessibleName("Validate and build output")

        self._stage_chip = StateChip("No ROM open", "readonly", plain=True)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(theme.SPACE_SM)
        buttons.addWidget(self._open_button)
        buttons.addWidget(self._extract_button)
        buttons.addWidget(self._output_button)
        buttons.addStretch(1)
        buttons.addWidget(self._validate_button)
        buttons.addWidget(self._build_button)

        actions = QWidget()
        actions_layout = QVBoxLayout(actions)
        actions_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        actions_layout.setSpacing(theme.SPACE_SM)
        actions_layout.addWidget(self._stage_chip)
        actions_layout.addLayout(buttons)

        self._rom_label_widget = self._rom_label
        history_header = PanelHeader("Output")
        self._log = self._status
        self._status.setPlaceholderText(
            "Validate and build output appears here: the validation report, any "
            "problem it names, and the path of the ROM a build writes."
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._rom_label)
        layout.addWidget(actions)
        layout.addWidget(history_header)
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
        self._rom_label.setProperty("dbzRole", "technical" if rom_open else "hint")
        # Extract: only when a ROM is open AND no project is loaded.
        self._extract_button.setEnabled(rom_open and not has_project)
        # Validate: once a project is set AND a compatible ROM is open.
        self._validate_button.setEnabled(rom_open and has_project)
        # Build: only when the last ValidationReport passed.
        self._build_button.setEnabled(self._session.validation_current)
        # The one line that says what stage the deliverable is at. Words rather
        # than colour: the chip is plain because it already names the stage.
        if not has_project:
            stage = "No project open"
        elif self._session.build_current:
            stage = "Built; a new ROM exists"
        elif self._session.validation_current:
            stage = "Validated; ready to build"
        else:
            stage = "Not validated"
        self._stage_chip.set_state(stage, "valid" if self._session.validation_current else "readonly")

    def _output_dir(self) -> Path | None:
        return self._session.output_dir

    # -- Open Project --------------------------------------------------------

    def _on_open_project(self) -> None:
        self.open_project_dialog()

    def open_project_dialog(self) -> None:
        """Choose an extracted project directory.

        One implementation, shared by the tab's button and the shell toolbar, so
        the global action and the panel cannot disagree about what opening a
        project does.
        """
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
        self.extract_project_dialog()

    def extract_project_dialog(self) -> None:
        """Write a project from the open ROM. One implementation, shared by the
        panel's own button and the shell's File menu."""
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
        self.choose_output_dialog()

    def choose_output_dialog(self) -> None:
        """Choose where a built ROM is written. One implementation, two callers."""
        chosen = QFileDialog.getExistingDirectory(self, "Choose Output Directory")
        if not chosen:
            return
        self._session.output_dir = Path(chosen)
        self._refresh()

    # -- Validate ------------------------------------------------------------

    def validate_project(self) -> None:
        """Run the established validation action for another authoring surface."""
        self._on_validate()

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

    def build_project(self) -> None:
        """Run the established build action for another authoring surface."""
        self._on_build()

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
            # only pre-existing-file case is the writer's refusal to replace an
            # existing destination; gate the overwrite offer on a file ACTUALLY
            # existing, never on the message text, and NEVER auto-delete on other
            # WriteErrors.
            if not Path(output_path).exists():
                QMessageBox.critical(self, "Build", str(exc))
                return
            # WORKBENCH-OVERWRITE-ATOMICITY-001. One build publishes the image AND
            # its beside-output manifest, and the writer refuses any destination
            # that already exists. Replacing only the image left the stale manifest
            # to fail the retry, after the previous output had been deleted, so the
            # set this build is about to replace is what gets removed - and only
            # that set.
            occupied = tuple(
                path for path in _build_artefacts_for(output_path) if path.exists()
            )
            # SAFETY: every path is re-checked against the source ROM before the
            # one irreversible act here. The pre-build guard proved the image; the
            # manifest is derived from it and is judged by the same policy.
            unsafe = [
                path for path in occupied
                if not is_safe_output_path(path, self._session.rom_path)
            ]
            if unsafe:
                QMessageBox.critical(
                    self, "Build refused",
                    "Refusing to delete - these paths are the source ROM:\n"
                    + "\n".join(str(path) for path in unsafe)
                )
                return
            answer = QMessageBox.question(
                self, "Overwrite existing output?",
                "These files already exist:\n"
                + "\n".join(str(path) for path in occupied)
                + "\nOverwrite them and rebuild?",
                QMessageBox.Yes | QMessageBox.No)
            if answer != QMessageBox.Yes:
                self._status.setPlainText("Build cancelled - existing output kept.")
                return
            # The image goes last, mirroring the writer's own publish order, so a
            # failure part-way leaves the artefact the user asked for rather than
            # deleting it and stopping.
            try:
                for path in reversed(occupied):
                    path.unlink()
            except OSError as unlink_error:
                QMessageBox.critical(
                    self, "Build refused",
                    f"The existing output could not be replaced: {unlink_error}"
                )
                return
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
