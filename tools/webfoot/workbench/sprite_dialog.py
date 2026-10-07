"""SPRITE-PROJECT-SURFACE-001: the authored-sprite dialog.

The one surface that CREATES a project's `sprites/sprites.toml`. The document, the
build path and the engine proof already existed; what was missing was any product
entry point that writes it, so an author had to hand-write TOML and point the
build at it.

The dialog collects only what an author decides. The engine id, the object family
and the two carried header words are shown read-only, because the image fixes the
first, one measured layout fixes the second, and the third pair is carried from
the chosen behaviour template rather than invented. What the shipped write path
cannot author at all - piece or OAM composition, piece counts, tile indices,
frame geometry, animation timing - is stated as out of contract instead of being
offered as a control that cannot work.

It performs no project write of its own. It validates the draft through the SDK,
then reports the document to write; the tab owns the session currency, the undo
stack and the project revision, exactly as it does for a palette recolour.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog,
                               QFormLayout, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QListWidget, QMessageBox, QPushButton,
                               QScrollArea, QSpinBox, QVBoxLayout, QWidget)

from .. import sprite_project as sprite_sdk
from ..project.model import (AuthoredSprite, AuthoredSpriteAnimation,
                             AuthoredSprites, ProjectError)
from ..sprite_authoring import (ActorTemplate, SourceSheet, SpriteAuthoringError,
                                read_source_sheet)
from . import theme
from .widgets import DisclosureRow, PanelHeader, StateChip, TechnicalLabel

#: Every SDK family this dialog can be refused by: the facade's own refusals, the
#: project model's, and the filesystem. A leaf-only catch leaves the sibling
#: families uncaught, and the click would look dead.
_SDK_ERRORS = (SpriteAuthoringError, ProjectError, OSError)

#: A sheet cell is 8 to 64 pixels. At 1:1 an author cannot judge their own art.
_PREVIEW_SCALE = 4

_OUT_OF_CONTRACT = (
    "Out of contract here, and deliberately not offered: piece or OAM composition, "
    "piece counts, tile indices, frame geometry and animation timing. An authored "
    "frame keeps the donor's own composition, which is the shape the retail engine "
    "has been observed to draw."
)


@dataclass(slots=True)
class _AnimationDraft:
    """One animation row as it is being typed, before the model sees it."""

    name: str
    sheet: str
    frames: int

    def to_model(self) -> AuthoredSpriteAnimation:
        return AuthoredSpriteAnimation(name=self.name, sheet=self.sheet,
                                       frames=self.frames)


class SpriteAuthoringDialog(QDialog):
    """Collect one authored actor sprite and hand back the document to write."""

    def __init__(self, parent: QWidget, session, *, editing: bool = False) -> None:
        super().__init__(parent)
        self._session = session
        self._animations: list[_AnimationDraft] = []
        self._document: AuthoredSprites | None = None
        self._probe = None
        self._sheets: list[SourceSheet] = []
        self._donor_text: dict[int, str] = {}
        self._template_text = ""
        self._loading = False
        self.setModal(True)
        self.setWindowTitle("Edit authored sprite" if editing else "New authored sprite")
        self.setMinimumWidth(660)
        # Tall enough that the sheet preview, the donor disclosure and the summary
        # are all visible when the dialog first opens; the body still scrolls.
        self.resize(760, 780)

        self._name = QLineEdit()
        self._name.setPlaceholderText("lowercase name, for example cui")
        self._donor = QComboBox()
        self._donor.currentIndexChanged.connect(self._on_donor_changed)

        self._anim_list = QListWidget()
        self._anim_list.setMaximumHeight(96)
        self._anim_list.currentRowChanged.connect(self._on_animation_chosen)
        self._anim_name = QLineEdit()
        self._anim_sheet = QLineEdit()
        self._anim_sheet.setPlaceholderText("project-relative path to a PNG sheet")
        self._anim_browse = QPushButton("Browse\u2026")
        self._anim_browse.clicked.connect(self._on_browse_sheet)
        self._anim_frames = QSpinBox()
        self._anim_frames.setRange(1, 64)
        self._anim_add = QPushButton("Add animation")
        self._anim_add.clicked.connect(self._on_add_animation)
        self._anim_remove = QPushButton("Remove")
        self._anim_remove.clicked.connect(self._on_remove_animation)
        self._sheet_preview = QLabel("No sheet cell to show yet.")
        self._sheet_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sheet_preview.setMinimumHeight(80)

        self._template = QComboBox()
        self._template.currentIndexChanged.connect(self._on_template_changed)
        self._position_x = self._coordinate(-32768, 32767)
        self._position_y = self._coordinate(-32768, 32767)
        self._box = tuple(self._coordinate(0, 0xFFFF) for _ in range(4))
        self._palette = QLineEdit()
        self._palette.setPlaceholderText(
            "object-palette entries this art may use, for example 8, 9, 103")

        self._derived = TechnicalLabel("")
        self._carried = TechnicalLabel("")
        self._state = StateChip("Not checked yet.", "neutral", plain=True)
        self._summary = QLabel("")
        self._summary.setWordWrap(True)
        self._summary.setProperty("dbzRole", "hint")

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setText("Save" if editing else "Create")
        self._ok.setProperty("dbzRole", "primary")
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self._on_accept)

        self._build_layout()
        for field in (self._name, self._anim_name, self._anim_sheet, self._palette):
            field.textChanged.connect(self._refresh)
        self._anim_frames.valueChanged.connect(self._refresh)
        for field in (self._position_x, self._position_y, *self._box):
            field.valueChanged.connect(self._refresh)
        self._load()

    # -- construction ---------------------------------------------------------

    def _coordinate(self, low: int, high: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(low, high)
        return box

    def _build_layout(self) -> None:
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD,
                                  theme.SPACE_MD)
        layout.setSpacing(theme.SPACE_MD)

        identity = QFormLayout()
        identity.addRow("Name", self._name)
        identity.addRow("Donor sprite", self._donor)
        layout.addLayout(identity)

        layout.addWidget(PanelHeader("Animations"))
        layout.addWidget(self._anim_list)
        animation_form = QFormLayout()
        animation_form.addRow("Name", self._anim_name)
        sheet_row = QWidget()
        sheet_layout = QHBoxLayout(sheet_row)
        sheet_layout.setContentsMargins(0, 0, 0, 0)
        sheet_layout.setSpacing(theme.SPACE_SM)
        sheet_layout.addWidget(self._anim_sheet, 1)
        sheet_layout.addWidget(self._anim_browse)
        animation_form.addRow("Sheet", sheet_row)
        animation_form.addRow("Frames per facing", self._anim_frames)
        layout.addLayout(animation_form)
        animation_buttons = QHBoxLayout()
        animation_buttons.setSpacing(theme.SPACE_SM)
        animation_buttons.addWidget(self._anim_add)
        animation_buttons.addWidget(self._anim_remove)
        animation_buttons.addStretch(1)
        layout.addLayout(animation_buttons)
        layout.addWidget(self._sheet_preview)

        layout.addWidget(PanelHeader("Actor"))
        actor_form = QFormLayout()
        actor_form.addRow("Behaviour template", self._template)
        actor_form.addRow("Position (x, y)", self._pair(self._position_x, self._position_y))
        actor_form.addRow("Wander box (x1, y1, x2, y2)", self._quad(*self._box))
        actor_form.addRow("Free palette entries", self._palette)
        layout.addLayout(actor_form)

        derived = DisclosureRow("Donor and engine identity")
        derived.add_widget(self._derived)
        derived.add_widget(self._carried)
        layout.addWidget(derived)

        boundary = QLabel(_OUT_OF_CONTRACT)
        boundary.setProperty("dbzRole", "hint")
        boundary.setWordWrap(True)
        layout.addWidget(boundary)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(body)
        root = QVBoxLayout(self)
        root.setContentsMargins(theme.SPACE_MD, theme.SPACE_MD, theme.SPACE_MD,
                                theme.SPACE_MD)
        root.setSpacing(theme.SPACE_SM)
        root.addWidget(scroll, 1)
        root.addWidget(self._state)
        root.addWidget(self._summary)
        root.addWidget(self._buttons)

    def _pair(self, first: QSpinBox, second: QSpinBox) -> QWidget:
        return self._row(first, second)

    def _quad(self, *boxes: QSpinBox) -> QWidget:
        return self._row(*boxes)

    def _row(self, *widgets: QWidget) -> QWidget:
        holder = QWidget()
        row = QHBoxLayout(holder)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(theme.SPACE_SM)
        for widget in widgets:
            row.addWidget(widget)
        row.addStretch(1)
        return holder

    # -- population -----------------------------------------------------------

    def _load(self) -> None:
        """Fill the pickers the image can answer, then any committed document.

        The template's own position and box are a STARTING point for a new
        identity. A document that already states them keeps what it says: applying
        the defaults after loading a committed document is what silently replaced
        an author's own placement with the template's.
        """
        committed = None
        self._loading = True
        try:
            self._populate_donors()
            self._populate_templates()
            committed = sprite_sdk.authored_sprite(self._session.project_dir)
            if committed is not None:
                self._load_committed(committed)
        finally:
            self._loading = False
        if committed is None:
            self._apply_template_defaults(
                self._template_facts(self._template.currentData()))
        self._refresh()

    def _populate_donors(self) -> None:
        """Every registry entry the image holds, so a donor can be chosen by id."""
        try:
            self._probe = sprite_sdk.probe_sprite_authoring(
                self._session.map_image, self._session.identification,
                profile=self._session.profile)
        except _SDK_ERRORS as exc:
            self._state.set_state("Not available in this image.", "invalid")
            self._summary.setText(str(exc))
            self._ok.setEnabled(False)
            return
        first = self._probe.sprite_id - self._probe.character_count
        for offset in range(self._probe.character_count):
            self._donor.addItem(f"sprite {first + offset}", first + offset)

    def _populate_templates(self) -> None:
        """Every object slot an authored actor can start from, by identity."""
        try:
            templates = sprite_sdk.supported_actor_templates(
                self._session.map_image, self._session.profile)
        except _SDK_ERRORS as exc:
            self._summary.setText(str(exc))
            return
        for template in templates:
            self._template.addItem(template.identity, template.identity)

    def _load_committed(self, sprite: AuthoredSprite) -> None:
        self._name.setText(sprite.name)
        self._donor.setCurrentIndex(
            self._select_or_add(self._donor, sprite.donor_sprite_id,
                                f"sprite {sprite.donor_sprite_id}"))
        self._animations = [_AnimationDraft(animation.name, animation.sheet,
                                            animation.frames)
                            for animation in sprite.ordered_animations()]
        self._reload_animations()
        self._template.setCurrentIndex(
            self._select_or_add(self._template, sprite.actor.behaviour_template,
                                sprite.actor.behaviour_template))
        self._position_x.setValue(sprite.actor.position[0])
        self._position_y.setValue(sprite.actor.position[1])
        for box, value in zip(self._box, sprite.actor.wander_box):
            box.setValue(value)
        self._palette.setText(", ".join(str(entry)
                                        for entry in sprite.free_palette_entries))

    def _select_or_add(self, combo: QComboBox, data, label: str) -> int:
        """The index of ``data``, adding it when the open image does not offer it.

        A document naming a donor or template this image no longer lists must be
        shown as what it says. Falling back to the combo's first entry would let
        Save silently swap in a different donor or behaviour, and validation is the
        right place to refuse it instead.
        """
        index = combo.findData(data)
        if index < 0:
            combo.addItem(label, data)
            index = combo.count() - 1
        return index

    def _reload_animations(self) -> None:
        current = self._anim_list.currentRow()
        self._anim_list.clear()
        for animation in self._animations:
            self._anim_list.addItem(self._row_text(animation))
        if self._animations:
            self._anim_list.setCurrentRow(min(max(current, 0), len(self._animations) - 1))
        else:
            self._anim_name.clear()
            self._anim_sheet.clear()
            self._anim_frames.setValue(1)
            self._sheet_preview.setText("No sheet cell to show yet.")

    def _row_text(self, animation: _AnimationDraft) -> str:
        sheet = Path(animation.sheet).name or "no sheet"
        return f"{animation.name}  \u00b7  {animation.frames} frame(s) per facing  \u00b7  {sheet}"

    # -- animation rows -------------------------------------------------------

    def _selected_row(self) -> int:
        return self._anim_list.currentRow()

    def _on_animation_chosen(self, row: int) -> None:
        self._loading = True
        try:
            if 0 <= row < len(self._animations):
                animation = self._animations[row]
                self._anim_name.setText(animation.name)
                self._anim_sheet.setText(animation.sheet)
                self._anim_frames.setValue(animation.frames)
        finally:
            self._loading = False
        self._refresh()

    def _on_add_animation(self) -> None:
        self._animations.append(_AnimationDraft(self._next_animation_name(), "", 1))
        self._reload_animations()
        self._anim_list.setCurrentRow(len(self._animations) - 1)
        self._refresh()

    def _next_animation_name(self) -> str:
        taken = {animation.name for animation in self._animations}
        for candidate in ("stand", "walk", "attack", "idle"):
            if candidate not in taken:
                return candidate
        return f"animation{len(taken) + 1}"

    def _on_remove_animation(self) -> None:
        row = self._selected_row()
        if not 0 <= row < len(self._animations):
            return
        del self._animations[row]
        self._reload_animations()
        self._refresh()

    def _commit_animation_fields(self) -> None:
        """Keep the edited row in step with its fields as they are typed."""
        row = self._selected_row()
        if not 0 <= row < len(self._animations):
            return
        draft = self._animations[row]
        draft.name = self._anim_name.text().strip()
        draft.sheet = self._anim_sheet.text().strip()
        draft.frames = self._anim_frames.value()
        item = self._anim_list.item(row)
        if item is not None:
            item.setText(self._row_text(draft))

    def _on_browse_sheet(self) -> None:
        project = self._session.project_dir
        start = str(Path(project) / "sprites") if project is not None else ""
        chosen, _filter = QFileDialog.getOpenFileName(
            self, "Choose a sheet PNG", start, "PNG images (*.png)")
        if not chosen:
            return
        try:
            self._anim_sheet.setText(Path(chosen).relative_to(project).as_posix())
        except ValueError:
            # Outside the project. The field states what was chosen and the
            # model's own refusal explains why a project records no such path.
            self._anim_sheet.setText(Path(chosen).as_posix())

    # -- donor, template and the read-only rows -------------------------------

    def _donor_id(self) -> int | None:
        data = self._donor.currentData()
        return None if data is None else int(data)

    def _on_donor_changed(self, _index: int) -> None:
        donor = self._donor_id()
        if donor is not None and donor not in self._donor_text:
            self._donor_text[donor] = self._describe_donor(donor)
        self._refresh()

    def _describe_donor(self, donor: int) -> str:
        """What this donor proves, or the planner's own refusal, read once."""
        try:
            probe = sprite_sdk.probe_sprite_authoring(
                self._session.map_image, self._session.identification,
                donor_sprite_id=donor, profile=self._session.profile)
        except _SDK_ERRORS as exc:
            return f"donor sprite {donor}: {exc}"
        envelope = probe.donor
        return (f"donor sprite {donor} proves exactly one frame rect "
                f"{envelope.width}x{envelope.height} at anchor {envelope.anchor}, "
                f"drawn as {envelope.piece_count} piece(s) ({envelope.pixels} pixels)")

    def _on_template_changed(self, _index: int) -> None:
        """A new template offers its own placement, and states what it carries."""
        identity = self._template.currentData()
        if identity is not None:
            template = self._template_facts(str(identity))
            if template is not None:
                self._template_text = (
                    f"behaviour template {template.identity} on {template.map}: "
                    f"carried verbatim, meaning unresolved - "
                    f"retained_raw 0x{template.retained_raw:08X}, "
                    f"data_pointer_raw 0x{template.data_pointer_raw:08X}")
                if not self._loading:
                    self._apply_template_defaults(template)
        if not self._loading:
            self._refresh()

    def _apply_template_defaults(self, template: ActorTemplate | None) -> None:
        """Offer the template's own position and box without disturbing a document.

        Written quietly, so filling five spin boxes is not five validations, and
        without touching the loading guard: this is called from inside `_load`.
        """
        if template is None:
            return
        widgets = (self._position_x, self._position_y, *self._box)
        blockers = [QSignalBlocker(widget) for widget in widgets]
        try:
            self._position_x.setValue(template.position[0])
            self._position_y.setValue(template.position[1])
            for box, value in zip(self._box, template.wander_box):
                box.setValue(value)
        finally:
            blockers.clear()

    def _template_facts(self, identity: str | None) -> ActorTemplate | None:
        if identity is None:
            return None
        try:
            return sprite_sdk.supported_template(
                self._session.map_image, self._session.profile, identity)
        except _SDK_ERRORS as exc:
            self._template_text = str(exc)
            return None

    # -- validation -----------------------------------------------------------

    def _refresh(self) -> None:
        """Re-state the draft's validity. Typing never writes anything.

        Every check here is the production one and every one of them is cheap: the
        model's own validation, the donor probe (one registry word plus that
        donor's own frames) and the planner's sheet reader and cell-geometry guard.
        The four-minute half of the plan - the palette claim against the decoded
        graphics, the allocation and the relocation census - belongs to Validate
        and Build, which report it with the same text.
        """
        if self._loading:
            return
        self._commit_animation_fields()
        self._document = None
        # The sheets are read first and on their own: a donor the planner refuses
        # must not also blank the preview of a sheet that is perfectly fine.
        self._read_sheets()
        problem = None
        try:
            self._document = sprite_sdk.validate_authored_sprite(
                self._session.map_image, self._session.identification,
                self._session.profile, self._request(),
                project_dir=self._session.project_dir)
        except (*_SDK_ERRORS, ValueError) as exc:
            problem = str(exc)
        self._update_derived()
        if problem:
            self._state.set_state("Not supported yet.", "invalid")
            self._summary.setText(problem)
            self._ok.setEnabled(False)
            return
        self._state.set_state("Ready to create.", "valid")
        self._summary.setText(
            "Creating writes sprites/sprites.toml and makes the current validation "
            "and build stale. The plan is checked again by Validate against this "
            "image, and Undo reverses the write.")
        self._ok.setEnabled(True)

    def _request(self) -> sprite_sdk.AuthoredSpriteRequest:
        if not self._animations:
            raise SpriteAuthoringError(
                "an authored sprite needs at least one animation slot; add one and "
                "choose the sheet it draws from")
        donor = self._donor_id()
        if donor is None:
            raise SpriteAuthoringError("choose the donor sprite this identity copies")
        identity = self._template.currentData()
        if identity is None:
            raise SpriteAuthoringError(
                "choose the behaviour template: an existing object slot of the map "
                "the new actor is appended to")
        return sprite_sdk.AuthoredSpriteRequest(
            name=self._name.text().strip(),
            donor_sprite_id=donor,
            animations=tuple(draft.to_model() for draft in self._animations),
            free_palette_entries=self._palette_entries(),
            behaviour_template=str(identity),
            position=(self._position_x.value(), self._position_y.value()),
            wander_box=tuple(box.value() for box in self._box),
        )

    def _palette_entries(self) -> tuple[int, ...]:
        text = self._palette.text().strip()
        if not text:
            return ()
        entries = []
        for part in text.replace(";", ",").split(","):
            part = part.strip()
            if not part:
                continue
            try:
                entries.append(int(part, 0))
            except ValueError:
                raise SpriteAuthoringError(
                    f"{part!r} is not a palette entry; give whole numbers separated "
                    "by commas") from None
        return tuple(entries)

    def _read_sheets(self) -> None:
        """Read every sheet the draft names, through the planner's own reader.

        A sheet that cannot be read leaves the preview empty and the refusal to the
        planner's own message, rather than a second opinion here.
        """
        where = f"sprite {self._name.text().strip()!r}"
        sheets: list[SourceSheet] = []
        try:
            for draft in self._animations:
                sheets.append(read_source_sheet(self._session.project_dir,
                                                draft.to_model(), where=where))
        except (*_SDK_ERRORS, ValueError):
            sheets = []
        self._sheets = sheets

    def _update_derived(self) -> None:
        """The read-only rows: what the image fixes and what the template carries."""
        if self._probe is not None:
            self._derived.setText(
                f"engine id {self._probe.sprite_id}, the only id a grown {self._probe.character_count}"
                f"-entry registry can address  \u00b7  family {sprite_sdk.ACTOR_FAMILY}")
        donor = self._donor_id()
        lines = ([self._donor_text[donor]] if donor in self._donor_text else [])
        if self._template_text:
            lines.append(self._template_text)
        self._carried.setText("\n".join(lines))
        self._show_sheet_preview()

    def _show_sheet_preview(self) -> None:
        """The chosen cell of the edited animation, decoded through the SDK."""
        row = self._selected_row()
        if not 0 <= row < len(self._sheets):
            self._sheet_preview.setText("No sheet cell to show yet.")
            self._sheet_preview.setPixmap(QPixmap())
            return
        sheet = self._sheets[row]
        side = sheet.cell_width
        image = QImage(sheet.pixels[: side * side * 3], side, side, side * 3,
                       QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(image).scaled(
            side * _PREVIEW_SCALE, side * _PREVIEW_SCALE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation)
        self._sheet_preview.setPixmap(pixmap)
        self._sheet_preview.setToolTip(
            f"{self._animations[row].name}: first cell of the sheet, {side}x{side} "
            "pixels, composed with the donor's own placement")

    # -- the answer -----------------------------------------------------------

    def document(self) -> AuthoredSprites | None:
        """The document this dialog would write, or None while the draft is refused."""
        return self._document

    def _on_accept(self) -> None:
        """Validate through the SDK, then report the document. No project write."""
        self._commit_animation_fields()
        try:
            document = sprite_sdk.validate_authored_sprite(
                self._session.map_image, self._session.identification,
                self._session.profile, self._request(),
                project_dir=self._session.project_dir)
        except (*_SDK_ERRORS, ValueError) as exc:
            self._state.set_state("Not supported yet.", "invalid")
            self._summary.setText(str(exc))
            self._ok.setEnabled(False)
            QMessageBox.warning(self, self.windowTitle(), str(exc))
            return
        self._document = document
        self.accept()
