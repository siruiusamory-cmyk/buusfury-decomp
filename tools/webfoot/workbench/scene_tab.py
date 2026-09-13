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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

#: The one authored semantic script operation this profile family exposes
#: (TOOLKIT-033). The tab assembles the mnemonic from three numeric inputs; the
#: facade forwards it to clone_placement, which assembles the actual bytes.
_SCRIPT_MNEMONIC = "show_centered_sprite_text"
#: Sentinel userData for the behavior selector's authored-script choice.
_AUTHORED_SCRIPT = "__authored_script__"


class SceneTab(QWidget):
    """Author one NPC by cloning an existing placement. Thin over `scene`."""

    projectChanged = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session

        # -- Map selector -----------------------------------------------------
        self._map_select = QComboBox()
        self._map_select.currentIndexChanged.connect(self._on_map_changed)
        map_box = QGroupBox("Map")
        map_layout = QVBoxLayout(map_box)
        map_layout.addWidget(self._map_select)

        # -- Placements table (read-only) -------------------------------------
        self._placements = QTableWidget(0, 4)
        self._placements.setHorizontalHeaderLabels(
            ("Placement", "Position", "Type", "Classification")
        )
        self._placements.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        placements_box = QGroupBox("Existing placements")
        placements_layout = QVBoxLayout(placements_box)
        placements_layout.addWidget(self._placements)

        # -- Add NPC form -----------------------------------------------------
        self._source_select = QComboBox()
        self._source_select.currentIndexChanged.connect(self._on_source_changed)

        self._name = QLineEdit()

        self._pos_low = QSpinBox()
        self._pos_low.setRange(0, 65535)
        self._pos_high = QSpinBox()
        self._pos_high.setRange(0, 65535)
        position_row = QHBoxLayout()
        position_row.addWidget(QLabel("low"))
        position_row.addWidget(self._pos_low)
        position_row.addWidget(QLabel("high"))
        position_row.addWidget(self._pos_high)
        position_widget = QWidget()
        position_widget.setLayout(position_row)

        self._behavior_select = QComboBox()
        self._behavior_select.currentIndexChanged.connect(self._on_behavior_changed)

        # Authored show_centered_sprite_text operands (text index + X + Y).
        # Fail-closed at input to the SDK's verified bounds (authored_placements.py):
        # text index 0..text_count-1 (text_count=1534, script_effects.py:11 -> 0..1533);
        # 0 <= X < 240 and 0 <= Y < 160 (authored_placements.py:200).
        self._script_text = QSpinBox()
        self._script_text.setRange(0, 1533)
        self._script_x = QSpinBox()
        self._script_x.setRange(0, 239)
        self._script_y = QSpinBox()
        self._script_y.setRange(0, 159)
        script_row = QHBoxLayout()
        script_row.addWidget(QLabel("text"))
        script_row.addWidget(self._script_text)
        script_row.addWidget(QLabel("X"))
        script_row.addWidget(self._script_x)
        script_row.addWidget(QLabel("Y"))
        script_row.addWidget(self._script_y)
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
        form.addRow(f"{_SCRIPT_MNEMONIC}", self._script_widget)
        form.addRow("Trigger", self._trigger_select)
        form.addRow(self._add)
        form_box = QGroupBox("Add NPC")
        form_box.setLayout(form)

        self._status = QLabel()

        layout = QVBoxLayout(self)
        layout.addWidget(map_box)
        layout.addWidget(placements_box, 1)
        layout.addWidget(form_box)
        layout.addWidget(self._status)

        self._populate_maps()

    # -- session-driven population -------------------------------------------

    def on_session_changed(self) -> None:
        """Re-populate from the session (e.g. after a ROM opens)."""
        self._populate_maps()

    def _populate_maps(self) -> None:
        """Fill the map selector from `list_authorable_maps`; empty-safe."""
        self._map_select.blockSignals(True)
        self._map_select.clear()
        maps = self._session.maps
        if maps is None:
            self._map_select.blockSignals(False)
            self._set_disabled("No authorable maps for the open ROM.")
            return
        for entry in scene_sdk.list_authorable_maps(maps):
            self._map_select.addItem(
                f"{entry['label']} ({entry['placement_count']} placements)",
                entry["identity"],
            )
        self._map_select.blockSignals(False)
        if self._map_select.count() == 0:
            self._set_disabled("No authorable maps for the open ROM.")
            return
        self._map_select.setCurrentIndex(0)
        self._on_map_changed()

    def _set_disabled(self, message: str) -> None:
        self._placements.setRowCount(0)
        self._source_select.clear()
        self._trigger_select.clear()
        self._add.setEnabled(False)
        self._session.selected_map = None
        self._status.setText(message)

    def _on_map_changed(self, *_) -> None:
        map_id = self._map_select.currentData()
        if map_id is None:
            self._set_disabled("Select a map to author against.")
            return
        self._session.selected_map = map_id
        self._fill_placements(map_id)
        self._fill_sources(map_id)
        self._status.clear()

    def _fill_placements(self, map_id: str) -> None:
        placements = scene_sdk.map_placements(self._session.maps, map_id)
        self._placements.setRowCount(len(placements))
        for row, p in enumerate(placements):
            self._placements.setItem(row, 0, QTableWidgetItem(p["identity"]))
            self._placements.setItem(
                row, 1, QTableWidgetItem(f"{p['position_low']}, {p['position_high']}")
            )
            self._placements.setItem(
                row, 2, QTableWidgetItem(str(p["placement_type"] or "—"))
            )
            self._placements.setItem(
                row, 3, QTableWidgetItem(str(p["classification"] or "—"))
            )

    def _fill_sources(self, map_id: str) -> None:
        self._source_select.blockSignals(True)
        self._source_select.clear()
        for candidate in scene_sdk.clone_source_candidates(self._session.maps, map_id):
            type_label = candidate["placement_type"] or "no type"
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
        self._behavior_select.addItem(
            f"authored {_SCRIPT_MNEMONIC}", _AUTHORED_SCRIPT
        )
        self._behavior_select.blockSignals(False)
        self._on_behavior_changed()

    def _on_behavior_changed(self, *_) -> None:
        self._script_widget.setEnabled(
            self._behavior_select.currentData() == _AUTHORED_SCRIPT
        )

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

    # -- Apply ----------------------------------------------------------------

    def _on_apply(self) -> None:
        source = self._source_select.currentData()
        map_id = self._map_select.currentData()
        if source is None or map_id is None or self._session.project_dir is None:
            return

        behavior_choice = self._behavior_select.currentData()
        behavior = None
        script = None
        if behavior_choice == _AUTHORED_SCRIPT:
            # An authored script and this record's own authored behavior are one
            # declaration (placements.py:90); set both or clone_placement rejects
            # it. The behavior string must equal `{identity}/behavior` where the
            # identity is `map:NNNN/authored:<name>` (placements.py:59,196).
            behavior = f"{map_id}/authored:{self._name.text()}/behavior"
            # The runtime-proven descriptor shape ends in `terminate`
            # (test_authored_scene_rom.py:60); emit it so the GUI produces the
            # TOOLKIT-034-proven body.
            script = (
                f"{_SCRIPT_MNEMONIC} text:{self._script_text.value():04d} "
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
        except ProjectError as exc:
            # ProjectError is the family parent of SceneAuthoringError AND
            # clone_placement's ProjectValidationError/ProjectLoadError. Catching
            # it here turns a normal user error into a QMessageBox instead of a
            # dead-looking click or a stderr traceback (WORKBENCH-001 lesson).
            QMessageBox.critical(self, "Add NPC", str(exc))
            return

        self._session.scene_mutated()
        self.projectChanged.emit()
        self._status.setText(f"Added {identity}")
