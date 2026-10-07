"""APPEARANCE-AUTHORING-GATE-001: the authored-appearance dialog.

The one surface that CREATES the project's `appearances/appearances.toml`. It
collects only what an author decides for one definition: the name the project
carries, the existing text index the engine draws as the on-screen name, and the
sprite identity the definition binds. The engine record's own identity is its
position in the table, which the build assigns, and its portrait and stat fields
stay at the corpus-legal defaults the SDK states, so none of them is a control
here.

What no shipped surface can author is stated rather than offered: a new text
index (the text table has no growth path), a new portrait slot, and a stat
record. The dialog performs no project write of its own; it validates the draft
through the SDK and reports the definition, and the tab owns the session
currency, the undo stack and the project revision.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                               QLabel, QLineEdit, QMessageBox, QVBoxLayout)

from .. import appearance_authoring as appearance_sdk
from .. import appearances as appearance_format
from ..appearance_authoring import AppearanceAuthoringError
from ..project.model import (AuthoredAppearance, AuthoredAppearances, ProjectError,
                             read_project)
from . import theme
from .widgets import StateChip

#: Every SDK family this dialog can be refused by.
_SDK_ERRORS = (AppearanceAuthoringError, ProjectError, OSError)

_OUT_OF_CONTRACT = (
    "Not offered here, and deliberately: a new text index (creating text-table "
    "ids is not shipped), a new portrait slot, and a stat record. An authored "
    "definition carries no portrait and no stat record, which 98 and 88 of the "
    "232 canonical records already do."
)


class AppearanceAuthoringDialog(QDialog):
    """Collect one authored appearance definition and hand it back."""

    def __init__(self, parent, session, *, definition: AuthoredAppearance | None = None,
                 taken: tuple[str, ...] = ()) -> None:
        super().__init__(parent)
        self._session = session
        self._existing = definition
        self._taken = frozenset(taken) - ({definition.name} if definition else set())
        self._result: AuthoredAppearance | None = None
        self._loading = True
        self.setModal(True)
        self.setWindowTitle("Edit authored appearance" if definition
                            else "New authored appearance")
        self.setMinimumWidth(560)

        self._name = QLineEdit()
        self._name.setPlaceholderText("lowercase name, for example new_face")
        self._text = QComboBox()
        self._sprite = QComboBox()
        self._state = StateChip("Reading the image\u2026", "readonly", plain=True)
        self._state.setWordWrap(False)
        self._summary = QLabel("")
        self._summary.setWordWrap(True)
        self._summary.setProperty("dbzRole", "hint")

        form = QFormLayout()
        form.addRow("Project name", self._name)
        form.addRow("On-screen name", self._text)
        form.addRow("Sprite identity", self._sprite)

        note = QLabel(_OUT_OF_CONTRACT)
        note.setWordWrap(True)
        note.setProperty("dbzRole", "hint")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setText("Create" if definition is None else "Apply")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.setSpacing(theme.SPACE_MD)
        root.addWidget(self._state)
        root.addLayout(form)
        root.addWidget(note)
        root.addWidget(self._summary)
        root.addWidget(buttons)

        self._populate()
        self._name.textChanged.connect(self._refresh)
        self._text.currentIndexChanged.connect(self._refresh)
        self._sprite.currentIndexChanged.connect(self._refresh)
        self._loading = False
        self._refresh()

    # -- the vocabularies ----------------------------------------------------

    def _populate(self) -> None:
        """Fill both selectors from the canonical table and the project's text.

        The labels are what a reader recognises rather than raw numbers: the
        on-screen-name list names the retail string each index resolves to, and
        the sprite list names the retail definition that first selects each id.
        Where the project carries no `text/strings.toml` the indices stand alone
        rather than a label being invented.
        """
        image = self._session.map_image
        profile = self._session.profile
        strings = self._strings()
        records = appearance_format.read_records(image, profile)
        first_by_index = {record.text_index: record for record in records}
        first_by_sprite: dict[int, int] = {}
        for record in records:
            first_by_sprite.setdefault(record.sprite_id, record.text_index)

        for index in appearance_format.name_vocabulary(image, profile):
            self._text.addItem(_label(index, strings.get(index)), index)
        extra = self._authored_sprite_id()
        for sprite_id in appearance_format.sprite_vocabulary(image, profile, extra=extra):
            name_index = first_by_sprite.get(sprite_id)
            suffix = strings.get(name_index, "") if name_index is not None else ""
            text = f"sprite {sprite_id}" + (f" - {suffix}" if suffix else "")
            if sprite_id == extra:
                text += " (the authored sprite identity)"
            self._sprite.addItem(text, sprite_id)
        # The record whose index is edited keeps its own values selectable even
        # when the image no longer offers them, so opening the dialog is never a
        # silent rewrite of a committed definition.
        if self._existing is not None:
            for combo, value, label in (
                (self._text, self._existing.text_index,
                 f"index {self._existing.text_index} (committed)"),
                (self._sprite, self._existing.sprite_id,
                 f"sprite {self._existing.sprite_id} (committed)"),
            ):
                if combo.findData(value) < 0:
                    combo.addItem(label, value)
            _select(self._text, self._existing.text_index)
            _select(self._sprite, self._existing.sprite_id)
            self._name.setText(self._existing.name)

    def _strings(self) -> dict[int, str]:
        """The project's authored strings by text index, or nothing.

        Read through the project model so the labels come from the same document
        the build reads, and so a project without a text file simply labels the
        indices.
        """
        project = self._session.project_dir
        if project is None:
            return {}
        try:
            document = read_project(project)
        except _SDK_ERRORS:
            return {}
        resolved: dict[int, str] = {}
        for identity, text in document.strings.items():
            index = getattr(identity, "index", None)
            if type(index) is int:
                resolved[index] = text.replace("\\n", " ")
        return resolved

    def _authored_sprite_id(self) -> int | None:
        """The engine id this project's authored sprite identity will take."""
        project = self._session.project_dir
        if project is None:
            return None
        try:
            sprites = read_project(project).sprites
        except _SDK_ERRORS:
            return None
        return None if sprites.is_empty() else sprites.only().sprite_id

    # -- validation ----------------------------------------------------------

    def _refresh(self) -> None:
        """Re-state the draft's validity. Typing never writes anything."""
        if self._loading:
            return
        self._result = None
        problem = None
        try:
            self._result = self._definition()
            appearance_sdk.validate_authored_appearances(
                self._session.map_image, self._session.identification,
                self._session.profile,
                AuthoredAppearances(appearances={self._result.name: self._result}),
                authored_sprite_id=self._authored_sprite_id())
        except (*_SDK_ERRORS, ValueError) as exc:
            self._result = None
            problem = str(exc)
        if problem:
            self._state.set_state("Not supported yet.", "invalid")
            self._summary.setText(problem)
            self._ok.setEnabled(False)
            return
        self._state.set_state("Ready to write.", "valid")
        self._summary.setText(
            "Writing appends this definition to the appearance table and makes the "
            "current validation and build stale. Validate checks it again against "
            "this image, and Undo reverses the write.")
        self._ok.setEnabled(True)

    def _definition(self) -> AuthoredAppearance:
        name = self._name.text().strip()
        if name in self._taken:
            raise AppearanceAuthoringError(
                f"appearance {name!r} already exists in this project")
        return AuthoredAppearance(name=name,
                                  text_index=self._text.currentData(),
                                  sprite_id=self._sprite.currentData())

    # -- the answer ----------------------------------------------------------

    def definition(self) -> AuthoredAppearance | None:
        """The definition this dialog would write, or None while it is refused."""
        return self._result

    def _on_accept(self) -> None:
        self._result = None
        try:
            definition = self._definition()
            appearance_sdk.validate_authored_appearances(
                self._session.map_image, self._session.identification,
                self._session.profile,
                AuthoredAppearances(appearances={definition.name: definition}),
                authored_sprite_id=self._authored_sprite_id())
        except (*_SDK_ERRORS, ValueError) as exc:
            self._state.set_state("Not supported yet.", "invalid")
            self._summary.setText(str(exc))
            self._ok.setEnabled(False)
            QMessageBox.warning(self, self.windowTitle(), str(exc))
            return
        self._result = definition
        self.accept()


def _select(combo: QComboBox, value) -> None:
    row = combo.findData(value)
    if row >= 0:
        combo.setCurrentIndex(row)


def _label(index: int, string: str | None) -> str:
    """One on-screen-name entry: the index, and the string when it resolves."""
    return f"{index} - {string}" if string else f"index {index}"
