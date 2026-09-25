"""Inspector for Atlas results and supported semantic dialogue authoring.

The tab displays recovered Atlas fields as opaque labels. Dialogue resolution,
validation, project persistence, and retail decoding stay behind the public
dialogue-authoring API; this module contains no ROM-format knowledge.

Visual direction (DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001). This is the surface
that most needed progressive disclosure: it used to lead with eleven recovered
`container_file_offset` / `packed_handle` rows before the game text and the
editing field, which is the HexManiacAdvance failure mode inverted - a hex
editor's worth of raw structure on top of a domain editor. The order is now the
one the design language prescribes:

1. the game content (the text the record actually shows),
2. the editing context (target, original, replacement, validation, Apply/Revert),
3. the editing state (the authoring status, as a state chip),
4. the technical detail (handles, offsets, provenance) behind a `Detail`
   disclosure.

HexManiacAdvance's own mechanism for this is a row/column header that shows the
*name* where an address would go, with the address kept in the footer; the
DragonByte Z equivalent is that the default surface names the target and the
text, and every raw field is one disclosure away and copyable when it is wanted.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
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
from . import theme
from .session import Session
from .widgets import DisclosureRow, PanelHeader, StateChip


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

        # -- 1. the game content: the record's own text, read first ------------
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(theme.mono_font())
        self._text.setAccessibleName("Record text")
        self._text.setMaximumHeight(110)
        text_header = PanelHeader("Record text")

        # -- 2. the editing context: the only authoring this tab performs -------
        self._authoring_status = StateChip(
            "Editing not available for this record yet.", "readonly", plain=True
        )
        self._authoring_status.setObjectName("dbzAuthoringStatus")
        self._target_label = QLabel("Target: \u2014")
        self._original_label = QLabel("Original: \u2014")
        self._original_label.setWordWrap(True)
        self._replacement_label = QLabel("Current project replacement: \u2014")
        self._replacement_label.setWordWrap(True)
        self._edit = QLineEdit()
        self._edit.setEnabled(False)
        self._edit.setAccessibleName("Dialogue replacement text")
        self._edit.textChanged.connect(self._on_editor_changed)
        self._validation_label = QLabel("")
        self._apply = QPushButton("Apply")
        self._apply.setProperty("dbzRole", "primary")
        self._apply.setEnabled(False)
        self._apply.clicked.connect(self._on_apply)
        self._revert = QPushButton("Revert to Original")
        self._revert.setEnabled(False)
        self._revert.clicked.connect(self._on_revert)

        author_buttons = QHBoxLayout()
        author_buttons.setContentsMargins(0, 0, 0, 0)
        author_buttons.setSpacing(theme.SPACE_SM)
        author_buttons.addWidget(self._apply)
        author_buttons.addWidget(self._revert)
        author_buttons.addStretch(1)

        edit_form = QFormLayout()
        edit_form.setContentsMargins(0, 0, 0, 0)
        edit_form.setHorizontalSpacing(theme.SPACE_MD)
        edit_form.setVerticalSpacing(theme.SPACE_XS)
        edit_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        # `_target_label`, `_original_label` and `_replacement_label` each already
        # begin with their own caption ("Target: ...", "Original: ..."), so they go
        # in full-width: giving them a form caption as well would print the same
        # word twice on one row.
        replace_caption = QLabel("Replacement")
        replace_caption.setProperty("dbzRole", "fieldLabel")
        edit_form.addRow(self._target_label)
        edit_form.addRow(replace_caption, self._edit)
        edit_form.addRow(self._original_label)
        edit_form.addRow(self._replacement_label)

        author_box = QWidget()
        author_layout = QVBoxLayout(author_box)
        author_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        author_layout.setSpacing(theme.SPACE_SM)
        author_layout.addWidget(self._authoring_status)
        author_layout.addLayout(edit_form)
        author_layout.addWidget(self._validation_label)
        author_layout.addLayout(author_buttons)
        author_layout.addStretch(1)
        author_header = PanelHeader("Compressed dialogue")

        # -- 3. technical detail, behind one disclosure (Godot's Advanced) ------
        self._handle_form = QFormLayout()
        self._handle_rows: dict[str, QLineEdit] = {}
        handle_body = QWidget()
        handle_body.setLayout(self._handle_form)

        # Citations: the reference sites that make a text record addressable.
        self._refs = QTableWidget(0, 1)
        self._refs.setHorizontalHeaderLabels(("Reference site",))
        self._refs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._refs.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._refs.verticalHeader().setVisible(False)
        self._refs.verticalHeader().setDefaultSectionSize(theme.ROW_HEIGHT)
        self._refs.setShowGrid(False)
        self._refs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._copy_refs = QPushButton("Copy all references")
        self._copy_refs.clicked.connect(self._on_copy_refs)
        refs_rows = QWidget()
        refs_layout = QVBoxLayout(refs_rows)
        refs_layout.setContentsMargins(0, 0, 0, 0)
        refs_layout.setSpacing(theme.SPACE_XS)
        refs_layout.addWidget(self._refs)
        refs_layout.addWidget(self._copy_refs)

        self._detail = DisclosureRow("Provenance", expanded=False)
        self._detail.add_widget(handle_body)
        refs_caption = QLabel("References")
        refs_caption.setProperty("dbzRole", "fieldLabel")
        self._detail.add_widget(refs_caption)
        self._detail.add_widget(refs_rows)
        detail_header = PanelHeader("Provenance")

        # -- assembly ----------------------------------------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(text_header)
        layout.addWidget(self._text)
        layout.addWidget(author_header)
        layout.addWidget(author_box, 1)
        layout.addWidget(detail_header)
        layout.addWidget(self._detail)

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

    def on_project_mutated(self) -> None:
        """A project mutation elsewhere: keep text the user typed but did not apply.

        CQA-05. This editor holds exactly one staged value - the replacement the
        user has typed and not applied - so re-reading the project here would
        silently discard it. A dirty editor is therefore left as the user typed
        it: its committed-value labels are refreshed and its validation re-run
        against the current target, but its text is not replaced. A clean editor
        is re-read, which is also how this tab's own Apply and Revert come to
        show their result: both write first and then emit ``projectChanged``
        with the editor already equal to the committed text.
        """
        if self._editor_is_dirty():
            self._refresh_committed_state()
            self._on_editor_changed(self._edit.text())
            return
        if self._session.selected_result is not None:
            self._refresh_authoring(self._session.selected_result)

    def _editor_is_dirty(self) -> bool:
        """Whether the editor holds a value the project does not.

        False whenever there is no editable target, so an unavailable or
        read-only record is never treated as staged work.
        """
        if self._target is None or not self._edit.isEnabled():
            return False
        committed = (
            self._project_replacement
            if self._project_replacement is not None
            else self._original
        )
        return self._edit.text() != committed

    def _refresh_committed_state(self) -> None:
        """Re-read the committed replacement for the current target.

        Leaves the editor's own text alone: the staged value belongs to the
        user. Only the facts *about* the project are updated, so the
        "current replacement" label and the Revert action cannot go stale while
        a staged edit is being protected.

        A failure here does NOT call `_set_authoring_unavailable`, because that
        clears the editor - which would destroy the very staged text this method
        exists to protect. It reports the reason on the state chip and leaves the
        editor exactly as typed.
        """
        profile = self._session.profile
        if self._target is None or profile is None or self._session.project_dir is None:
            return
        try:
            replacement = dialogue_sdk.get_dialogue_replacement(
                self._session.project_dir, profile, self._target
            )
        except (dialogue_sdk.DialogueAuthoringError, ProjectError, OSError) as exc:
            self._authoring_status.set_state(f"Cannot re-read the project: {exc}", "readonly")
            return
        self._project_replacement = replacement
        self._replacement_label.setText(
            "Current project replacement: "
            + (replacement if replacement is not None else "none")
        )
        self._revert.setEnabled(replacement is not None)

    def _set_authoring_unavailable(self, message: str) -> None:
        self._target = None
        self._original = ""
        self._project_replacement = None
        self._authoring_status.set_state(message, "readonly")
        self._target_label.setText("Target: \u2014")
        self._original_label.setText("Original: \u2014")
        self._replacement_label.setText("Current project replacement: \u2014")
        self._validation_label.clear()
        self._validation_label.setStyleSheet("")
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
            self._authoring_status.set_state(
                "Editing requires an open Webfoot project.", "readonly"
            )
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
        self._authoring_status.set_state("Editing available", "edit")
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
            # The existing `✓ Valid` wording already carries the glyph, so the
            # role only has to add the brightness half of the signal.
            self._validation_label.setText(f"{theme.status_glyph('valid')} Valid")
            self._validation_label.setStyleSheet(
                f"color: {theme.color('success').name()}; background: transparent;"
            )
        else:
            self._validation_label.setText(
                f"{theme.status_glyph('invalid')} "
                + "; ".join(problem.message for problem in validation.problems)
            )
            self._validation_label.setStyleSheet(
                f"color: {theme.color('danger').name()}; background: transparent;"
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
