"""WORKBENCH-003 - Scene authoring tab.

The Scene tab lets a human clone an existing map placement into a named authored
NPC: pick a map, pick a clone source, set a position, choose a behavior (an
existing descriptor OR an authored `show_centered_sprite_text` script), optionally
attach a trigger, and Apply.

It is a THIN client, mirroring `inspector.py`: it holds no ROM-format knowledge
and calls only the public `scene` facade plus the shared `Session`. Typing/
selecting never mutates the project; the Apply button commits through
`scene.add_authored_npc`, advances project state via `session.scene_mutated()`,
and emits `projectChanged` so validation/build/launch go stale.

The one rule that matters most (WORKBENCH-001 live defect): the Apply slot
catches the SDK exception family PARENT `ProjectError` - the parent of both this
facade's `SceneAuthoringError` and `clone_placement`'s
`ProjectValidationError`/`ProjectLoadError` - so a normal user error becomes a
QMessageBox, never a dead-looking click or a terminal traceback.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import scene as scene_sdk
from ..project import ProjectError
from .session import Session

#: Sentinel tag for an SDK-provided authored-script editor choice.
_AUTHORED_SCRIPT = "authored-script"


class SceneTab(QWidget):
    """Author one NPC by cloning an existing placement. Thin over `scene`."""

    projectChanged = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

        # -- Map selector -----------------------------------------------------
        self._map_select = QComboBox()
        self._map_select.currentIndexChanged.connect(self._on_map_changed)
        self._map_support = QLabel()
        self._map_support.setWordWrap(True)
        map_box = QGroupBox("Maps")
        map_layout = QVBoxLayout(map_box)
        map_layout.addWidget(self._map_select)
        map_layout.addWidget(self._map_support)

        # -- Placements table (read-only) -------------------------------------
        self._placements = QTableWidget(0, 5)
        self._placements.setHorizontalHeaderLabels(
            ("Placement", "Position", "Type", "Classification", "Source")
        )
        self._placements.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._placements.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._placements.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._placements.itemSelectionChanged.connect(self._on_placement_selected)
        placements_box = QGroupBox("Placements")
        placements_layout = QVBoxLayout(placements_box)
        placements_layout.addWidget(self._placements)

        # -- Add NPC form -----------------------------------------------------
        self._source_select = QComboBox()
        self._source_select.currentIndexChanged.connect(self._on_source_changed)

        self._name = QLineEdit()

        placement_constraints = scene_sdk.placement_editor_constraints()
        self._pos_low = QSpinBox()
        self._pos_low.setRange(*placement_constraints["position_low"])
        self._pos_high = QSpinBox()
        self._pos_high.setRange(*placement_constraints["position_high"])
        position_row = QHBoxLayout()
        position_row.addWidget(QLabel("low"))
        position_row.addWidget(self._pos_low)
        position_row.addWidget(QLabel("high"))
        position_row.addWidget(self._pos_high)
        position_widget = QWidget()
        position_widget.setLayout(position_row)

        self._behavior_select = QComboBox()
        self._behavior_select.currentIndexChanged.connect(self._on_behavior_changed)

        # Authored-script editor bounds come from scene.script_effect_options;
        # the widget contains no profile count or screen geometry.
        self._script_text = QSpinBox()
        self._script_text.valueChanged.connect(self._refresh_text_preview)
        self._script_text_preview = QLabel()
        self._script_x = QSpinBox()
        self._script_y = QSpinBox()
        script_row = QHBoxLayout()
        script_row.addWidget(QLabel("text"))
        script_row.addWidget(self._script_text)
        script_row.addWidget(QLabel("X"))
        script_row.addWidget(self._script_x)
        script_row.addWidget(QLabel("Y"))
        script_row.addWidget(self._script_y)
        script_row.addWidget(self._script_text_preview, 1)
        self._script_widget = QWidget()
        self._script_widget.setLayout(script_row)

        self._trigger_select = QComboBox()

        self._add = QPushButton("Add / Apply")
        self._add.clicked.connect(self._on_apply)

        form = QFormLayout()
        form.addRow("Clone source", self._source_select)
        form.addRow("Name", self._name)
        form.addRow("Position", position_widget)
        form.addRow("Behavior", self._behavior_select)
        form.addRow("Visible response", self._script_widget)
        form.addRow("Trigger", self._trigger_select)
        form.addRow(self._add)
        form_box = QGroupBox("Add NPC")
        form_box.setLayout(form)

        # -- Semantic relationship navigator --------------------------------
        self._relationship_labels = {
            "entity": QLabel(), "behavior": QLabel(), "script": QLabel(),
            "dialogue": QLabel(), "used_by": QLabel(),
        }
        for label in self._relationship_labels.values():
            label.setWordWrap(True)
        self._open_entity = QPushButton("Open Entity")
        self._open_behavior = QPushButton("Open Behavior")
        self._open_script = QPushButton("Open Script")
        self._back = QPushButton("Back to Map")
        self._open_entity.clicked.connect(lambda: self._open_related("entity"))
        self._open_behavior.clicked.connect(lambda: self._open_related("behavior"))
        self._open_script.clicked.connect(lambda: self._open_related("script"))
        self._back.clicked.connect(self._navigate_back)
        relationship_actions = QHBoxLayout()
        for button in (self._open_entity, self._open_behavior, self._open_script, self._back):
            relationship_actions.addWidget(button)
        relationship_layout = QFormLayout()
        relationship_layout.addRow("Entity", self._relationship_labels["entity"])
        relationship_layout.addRow("Behavior", self._relationship_labels["behavior"])
        relationship_layout.addRow("Script", self._relationship_labels["script"])
        relationship_layout.addRow("Dialogue", self._relationship_labels["dialogue"])
        relationship_layout.addRow("Used by", self._relationship_labels["used_by"])
        relationship_layout.addRow(relationship_actions)
        relationship_box = QGroupBox("Selected placement")
        relationship_box.setLayout(relationship_layout)
        self._editor = QLabel("Select a placement to inspect its relationships.")
        self._editor.setWordWrap(True)
        editor_box = QGroupBox("Specialized editor")
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.addWidget(self._editor)
        self._relationships = {}
        self._navigation = []
        self._editor_kind = None
        self._editor_identity = None

        # -- Pending semantic project changes --------------------------------
        self._pending = QListWidget()
        self._pending.itemSelectionChanged.connect(self._on_pending_selected)
        self._revert = QPushButton("Revert")
        self._revert.clicked.connect(self._on_revert)
        self._revert.setEnabled(False)
        pending_box = QGroupBox("Pending Changes")
        pending_layout = QVBoxLayout(pending_box)
        pending_layout.addWidget(self._pending)
        pending_layout.addWidget(self._revert)

        self._status = QLabel()

        layout = QVBoxLayout(self)
        layout.addWidget(map_box)
        layout.addWidget(placements_box, 1)
        layout.addWidget(relationship_box)
        layout.addWidget(editor_box)
        layout.addWidget(form_box)
        layout.addWidget(pending_box)
        layout.addWidget(self._status)

        self._populate_maps()

    # -- session-driven population -------------------------------------------

    def on_session_changed(self) -> None:
        """Re-populate from the session (e.g. after a ROM opens)."""
        self._populate_maps()

    def select_placement(self, map_id: str, placement_identity: str) -> None:
        """Focus one semantic placement from the visual Map workspace."""
        map_index = next(
            (
                index
                for index in range(self._map_select.count())
                if (entry := self._map_select.itemData(index))
                and entry["identity"] == map_id
            ),
            -1,
        )
        if map_index < 0:
            return
        self._map_select.setCurrentIndex(map_index)
        for row in range(self._placements.rowCount()):
            item = self._placements.item(row, 0)
            placement = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
            if placement and placement["identity"] == placement_identity:
                self._placements.selectRow(row)
                self._placements.setFocus()
                return

    def _populate_maps(self) -> None:
        """Fill the map selector from `list_authorable_maps`; empty-safe."""
        previous_map = self._session.selected_map
        self._map_select.blockSignals(True)
        self._map_select.clear()
        maps = self._session.maps
        if maps is None:
            self._map_select.blockSignals(False)
            self._set_disabled("No authorable maps for the open ROM.")
            return
        selected_index = 0
        for index, entry in enumerate(scene_sdk.list_maps(maps)):
            self._map_select.addItem(
                f"{entry['label']} - {entry['support']} ({entry['placement_count']} placements)",
                entry,
            )
            if entry["identity"] == previous_map:
                selected_index = index
        self._map_select.blockSignals(False)
        if self._map_select.count() == 0:
            self._set_disabled("No authorable maps for the open ROM.")
            return
        self._map_select.setCurrentIndex(selected_index)
        self._on_map_changed()
        self._refresh_pending()

    def _set_disabled(self, message: str) -> None:
        self._placements.setRowCount(0)
        self._source_select.clear()
        self._trigger_select.clear()
        self._add.setEnabled(False)
        self._session.selected_map = None
        self._map_support.setText(message)
        self._status.setText(message)

    def _on_map_changed(self, *_) -> None:
        map_entry = self._map_select.currentData()
        if map_entry is None:
            self._set_disabled("Select a map to author against.")
            return
        map_id = map_entry["identity"]
        self._session.selected_map = map_id
        self._map_support.setText(
            f"{map_entry['support']}: {map_entry['support_reason']}"
        )
        if not self._fill_placements(map_id):
            return
        self._fill_sources(map_id)
        self._navigation = [("map", map_id)]
        self._show_editor("map", map_id, push=False)
        self._status.clear()

    def _fill_placements(self, map_id: str) -> bool:
        try:
            placements = scene_sdk.scene_placements(
                self._session.maps, map_id, self._session.project_dir
            )
        except (ProjectError, OSError) as exc:
            self._set_disabled(f"Cannot load project scene: {exc}")
            return False
        self._placements.setRowCount(len(placements))
        for row, p in enumerate(placements):
            item = QTableWidgetItem(p["identity"])
            item.setData(Qt.ItemDataRole.UserRole, p)
            self._placements.setItem(row, 0, item)
            self._placements.setItem(
                row, 1, QTableWidgetItem(f"{p['position_low']}, {p['position_high']}")
            )
            self._placements.setItem(
                row, 2, QTableWidgetItem(str(p["placement_type"] or "—"))
            )
            self._placements.setItem(
                row, 3, QTableWidgetItem(str(p["classification"] or "—"))
            )

            self._placements.setItem(row, 4, QTableWidgetItem(p["provenance"]))
        return True

    def _fill_sources(self, map_id: str) -> None:
        self._source_select.blockSignals(True)
        self._source_select.clear()
        for candidate in scene_sdk.clone_source_candidates(self._session.maps, map_id):
            type_label = (
                candidate["placement_type"].split("/")[-1]
                if candidate["placement_type"] else "no type"
            )
            classification = candidate["classification"] or "—"
            self._source_select.addItem(
                f"{candidate['identity']}  [{type_label} / {classification}]",
                candidate["identity"],
            )
        self._source_select.blockSignals(False)
        self._fill_behaviors()
        # Trigger the source-dependent controls (triggers + Add enablement).
        self._on_source_changed()

    def _fill_behaviors(self) -> None:
        """Behavior choices: existing descriptors + the authored-script option."""
        self._behavior_select.blockSignals(True)
        self._behavior_select.clear()
        self._behavior_select.addItem("(none)", None)
        for descriptor in scene_sdk.assignable_descriptors(self._session.maps):
            event = descriptor.get("event") or "—"
            self._behavior_select.addItem(
                f"{descriptor['identity']}  ({event})", descriptor["identity"]
            )
        for effect in scene_sdk.script_effect_options(self._session.maps):
            self._behavior_select.addItem(
                f"authored {effect['label']}", (_AUTHORED_SCRIPT, effect)
            )
        self._behavior_select.blockSignals(False)
        self._on_behavior_changed()

    def _on_behavior_changed(self, *_) -> None:
        choice = self._behavior_select.currentData()
        authored = isinstance(choice, tuple) and choice[0] == _AUTHORED_SCRIPT
        self._script_widget.setEnabled(authored)
        if authored:
            effect = choice[1]
            self._script_text.setRange(0, effect["text_count"] - 1)
            self._script_x.setRange(*effect["coordinate_ranges"]["x"])
            self._script_y.setRange(*effect["coordinate_ranges"]["y"])
            self._refresh_text_preview()

    def _on_source_changed(self, *_) -> None:
        source = self._source_select.currentData()
        self._trigger_select.blockSignals(True)
        self._trigger_select.clear()
        self._trigger_select.addItem("(none)", None)
        if source is not None:
            # on_defeat appears ONLY when trigger_options offers it for this source.
            for option in scene_sdk.trigger_options(self._session.maps, source):
                self._trigger_select.addItem(option, option)
        self._trigger_select.blockSignals(False)
        self._add.setEnabled(source is not None and self._session.project_dir is not None)
        if source is None:
            self._status.setText("No clone source available for this map.")
        elif self._session.project_dir is None:
            self._status.setText("Open a Webfoot project (Build tab) to author.")
        else:
            self._status.clear()

    # -- semantic navigation -------------------------------------------------

    def _on_placement_selected(self) -> None:
        row = self._placements.currentRow()
        item = self._placements.item(row, 0) if row >= 0 else None
        placement = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if not placement:
            self._relationships = {}
            return
        identity = placement["identity"]
        try:
            self._relationships = scene_sdk.placement_relationships(
                self._session.maps, identity, self._session.project_dir
            )
        except (ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Inspect placement", str(exc))
            return
        for key in ("entity", "behavior", "script", "dialogue"):
            self._relationship_labels[key].setText(
                str(self._relationships.get(key) or "Not linked")
            )
        used_by = self._relationships.get("used_by", ())
        if used_by:
            visible = used_by[:5]
            remainder = len(used_by) - len(visible)
            backlink_text = ", ".join(visible)
            if remainder:
                backlink_text += f" (+{remainder} more)"
        else:
            backlink_text = "No known backlinks"
        self._relationship_labels["used_by"].setText(backlink_text)
        self._open_entity.setEnabled(bool(self._relationships.get("entity")))
        self._open_behavior.setEnabled(bool(self._relationships.get("behavior")))
        self._open_script.setEnabled(bool(self._relationships.get("script")))
        source_identity = self._relationships.get("clone_from") or identity
        source_index = self._source_select.findData(source_identity)
        if source_index >= 0:
            self._source_select.setCurrentIndex(source_index)
            self._pos_low.setValue(placement["position_low"])
            self._pos_high.setValue(placement["position_high"])
        self._navigation = [("map", self._session.selected_map), ("placement", identity)]
        self._show_editor("placement", identity, push=False)

    def _open_related(self, kind: str) -> None:
        identity = self._relationships.get(kind)
        if identity:
            self._show_editor(kind, identity)

    def _show_editor(self, kind: str, identity: str, *, push: bool = True) -> None:
        """Small explicit dispatch to specialized semantic views."""
        renderers = {
            "map": lambda value: f"Scene editor for {value}",
            "placement": lambda value: (
                f"Placement editor for {value}. The Add NPC form is configured from "
                "this semantic source."
            ),
            "entity": lambda value: (
                f"Entity editor: {value}. Entity configuration is shared with the "
                "selected placement form."
            ),
            "behavior": lambda value: (
                f"Behavior editor: {value}. Choose a supported behavior in the "
                "placement form."
            ),
            "script": lambda value: (
                f"Script editor: {value}. Authored scripts use the specialized "
                "visible-response controls."
            ),
        }
        renderer = renderers.get(kind)
        if renderer is None:
            raise ValueError(f"no specialized editor for {kind}")
        if push:
            self._navigation.append((kind, identity))
        self._editor_kind = kind
        self._editor_identity = identity
        self._editor.setText(renderer(identity))
        if kind == "entity":
            self._source_select.setFocus()
        elif kind == "behavior":
            behavior_index = self._behavior_select.findData(identity)
            if behavior_index >= 0:
                self._behavior_select.setCurrentIndex(behavior_index)
            self._behavior_select.setFocus()
        elif kind == "script":
            self._script_widget.setFocus()
        self._back.setEnabled(len(self._navigation) > 1)

    def _navigate_back(self) -> None:
        if len(self._navigation) <= 1:
            return
        self._navigation.pop()
        kind, identity = self._navigation[-1]
        self._show_editor(kind, identity, push=False)

    def _refresh_text_preview(self, *_) -> None:
        strings = self._session.text_strings
        if strings is None:
            self._script_text_preview.setText(
                f"text:{self._script_text.value():04d}"
            )
            return
        from ..formats.text_tables import TextIdentity
        try:
            entry = strings.entry(TextIdentity(self._script_text.value()))
        except ValueError:
            self._script_text_preview.setText("Unsupported text identity")
            return
        preview = entry.text.replace("\n", " ")
        self._script_text_preview.setText(
            f"{entry.identity}: {preview[:64]}{'...' if len(preview) > 64 else ''}"
        )

    # -- pending changes -----------------------------------------------------

    def _refresh_pending(self) -> None:
        self._pending.clear()
        if self._session.project_dir is None or self._session.maps is None:
            self._revert.setEnabled(False)
            return
        try:
            changes = scene_sdk.pending_changes(
                self._session.project_dir, self._session.maps
            )
        except (ProjectError, OSError) as exc:
            self._status.setText(str(exc))
            self._revert.setEnabled(False)
            return
        for change in changes:
            body = "\n".join((change.summary, *(f"  - {line}" for line in change.details)))
            item = QListWidgetItem(body)
            item.setData(Qt.ItemDataRole.UserRole, change)
            self._pending.addItem(item)
        if not changes:
            self._pending.addItem("No pending project changes.")
        self._revert.setEnabled(False)

    def _on_pending_selected(self) -> None:
        item = self._pending.currentItem()
        change = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        self._revert.setEnabled(bool(change and change.revertible))

    def _on_revert(self) -> None:
        item = self._pending.currentItem()
        change = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if change is None or not change.revertible or self._session.project_dir is None:
            return
        try:
            changed = scene_sdk.revert_pending_change(
                self._session.project_dir, self._session.maps, change.identity
            )
        except (ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Revert project change", str(exc))
            return
        if changed:
            self._session.scene_mutated()
            self.projectChanged.emit()
            if self._session.selected_map:
                self._fill_placements(self._session.selected_map)
            self._refresh_pending()
            self._status.setText(f"Reverted {change.summary}")

    # -- Apply ----------------------------------------------------------------

    def _on_apply(self) -> None:
        source = self._source_select.currentData()
        map_entry = self._map_select.currentData()
        map_id = map_entry["identity"] if map_entry else None
        if source is None or map_id is None or self._session.project_dir is None:
            return

        behavior_choice = self._behavior_select.currentData()
        behavior = None
        script = None
        if isinstance(behavior_choice, tuple) and behavior_choice[0] == _AUTHORED_SCRIPT:
            # An authored script and this record's own authored behavior are one
            # declaration (placements.py:90); set both or clone_placement rejects
            # it. The behavior string must equal `{identity}/behavior` where the
            # identity is `map:NNNN/authored:<name>` (placements.py:59,196).
            behavior = f"{map_id}/authored:{self._name.text()}/behavior"
            # The runtime-proven descriptor shape ends in `terminate`
            # (test_authored_scene_rom.py:60); emit it so the GUI produces the
            # TOOLKIT-034-proven body.
            effect = behavior_choice[1]
            script = (
                f"{effect['identity']} text:{self._script_text.value():04d} "
                f"{self._script_x.value()} {self._script_y.value()}",
                "terminate",
            )
        elif behavior_choice is not None:
            behavior = behavior_choice

        trigger = self._trigger_select.currentData()

        try:
            identity = scene_sdk.add_authored_npc(
                self._session.project_dir,
                map_id,
                source,
                self._name.text(),
                (self._pos_low.value(), self._pos_high.value()),
                behavior=behavior,
                script=script,
                trigger=trigger,
                maps=self._session.maps,
            )
        except (ProjectError, OSError) as exc:
            # ProjectError is the family parent of SceneAuthoringError AND
            # clone_placement's ProjectValidationError/ProjectLoadError. Catching
            # it here turns a normal user error into a QMessageBox instead of a
            # dead-looking click or a stderr traceback (WORKBENCH-001 lesson).
            QMessageBox.critical(self, "Add NPC", str(exc))
            return

        self._session.scene_mutated()
        self.projectChanged.emit()
        self._fill_placements(map_id)
        for row in range(self._placements.rowCount()):
            placement = self._placements.item(row, 0).data(
                Qt.ItemDataRole.UserRole
            )
            if placement and placement["identity"] == identity:
                self._placements.selectRow(row)
                break
        self._refresh_pending()
        self._status.setText(f"Added {identity}")
