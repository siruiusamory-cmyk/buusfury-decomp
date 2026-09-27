"""MAP-WARP-WORKBENCH-001: the Maps editor's Warps mode over a synthetic image.

Focused regressions for the EXISTING-transition authoring surface. The synthetic
image is the same one `test_map_transitions` assembles from the measured format
(a 0x38-stride map table, a selector-1 root reached from `MapEntry + 0x2C`, and
24-byte records), extended here with the two root words the engine's own walkable
extent comes from, so a derived arrival can be bounds-checked. The project is a
real on-disk project written by the real `write_project`, and every edit goes
through the real authority - no mocked SDK path.

Covered by name: list population, selection, destination edit, arrival edit,
facing edit, combined retarget, low-nibble preservation, the class-169 refusal,
Apply/Revert, Undo/Redo, the no-op rule, CQA-05 (mutation vs session lifecycle),
CQA-06 (expected failures reach the surface), CQA-07 (bounded project I/O) and
save/reopen.

The synthetic image is deliberately not a canonical ROM and asserts no canonical
count. The real corpus and the runtime proof live in the integration files.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from tools.webfoot import map_transitions as mt  # noqa: E402
from tools.webfoot import map_view as mv  # noqa: E402
from tools.webfoot.formats.map_transitions import (  # noqa: E402
    TRANSITION_CLASS_B_RAW,
    MapTransitionValueError,
    TransitionArrival,
)
from tools.webfoot.maps import MapIdentity  # noqa: E402
from tools.webfoot.project import (  # noqa: E402
    PROJECT_FORMAT_VERSION,
    TRANSITION_FILE,
    ProjectMeta,
    ProjectLoadError,
    read_project,
    write_project,
)
from tools.webfoot.workbench import warp_tab as wt  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402
from tools.webfoot.workbench.warp_tab import WarpTab  # noqa: E402

from tests.unit.test_map_transitions import (  # noqa: E402
    GBA_BASE,
    ROOT_BASE,
    ROOT_STRIDE,
    key_for,
    record_bytes,
    synthetic_image,
)

#: One word pair per map: the engine's camera clamp is `extent - 1`, so the
#: walkable world is `extent + screen` (`MapTransitions.destination_bounds`). The
#: synthetic image's roots start at zero, which would make every map 241x161 and
#: would refuse the regions and arrivals these tests use.
EXTENTS = ((0x02FF, 0x02FF), (0x02FF, 0x02FF), (0x02FF, 0x02FF), (0x003F, 0x003F))

#: Five maps:
#:
#: * map 0 - two 566-class connections: index 0 leads to map 1 with `+0x10 = 0x02`
#:   (low bits only, so NO facing override), index 1 leads to map 2 with
#:   `+0x10 = 0x0E` (no override either, and an unresolved low nibble to preserve);
#: * map 1 - one 566-class connection back to map 0, whose region is map 0's door
#:   back and is therefore what a retarget's arrival is derived from;
#: * map 2 - one 169-class connection back to map 0: the family the toolkit
#:   refuses to retarget;
#: * map 3 - one 566-class connection back to map 0, on a much smaller map;
#: * map 4 - no connections at all, and none back to map 0 (an underivable link).
#:
#: The regions are asymmetric on purpose: every endpoint differs, so a transposed
#: interval cannot pass by coincidence.
PER_MAP = [
    [
        record_bytes(
            destination_key=tuple(key_for(1)),
            first=(100, 140),
            second=(20, 60),
            byte_0x10=0x02,
            word_0x14=48,
            byte_0x16=40,
            byte_0x17=0,
        ),
        record_bytes(
            destination_key=tuple(key_for(2)),
            first=(200, 240),
            second=(70, 90),
            byte_0x10=0x0E,
            word_0x14=12,
            byte_0x16=34,
            byte_0x17=0,
        ),
    ],
    [
        record_bytes(
            destination_key=tuple(key_for(0)),
            first=(660, 700),
            second=(120, 160),
            byte_0x10=0x01,
            word_0x14=110,
            byte_0x16=35,
            byte_0x17=0,
        )
    ],
    [
        record_bytes(
            class_raw=TRANSITION_CLASS_B_RAW,
            destination_key=tuple(key_for(0)),
            first=(10, 40),
            second=(10, 40),
            word_0x14=8,
            byte_0x16=8,
            byte_0x17=0,
        )
    ],
    [
        record_bytes(
            destination_key=tuple(key_for(0)),
            first=(100, 140),
            second=(20, 60),
            byte_0x10=0x03,
            word_0x14=120,
            byte_0x16=40,
            byte_0x17=0,
        )
    ],
    [],
]

#: map:0000/transition:0000 - the 566-class connection every edit test drives.
TARGET = "map:0000/transition:0000"
#: map:0002/transition:0000 - the 169-class connection.
SCENE_RELATIVE = "map:0002/transition:0000"


def image_bytes() -> bytes:
    """The synthetic corpus with each root's walkable extent written in."""
    data = bytearray(synthetic_image(PER_MAP))
    for index, (width, height) in enumerate(EXTENTS):
        root = ROOT_BASE + index * ROOT_STRIDE
        data[root + 0x08 : root + 0x0A] = (width - 1).to_bytes(2, "little")
        data[root + 0x0A : root + 0x0C] = (height - 1).to_bytes(2, "little")
    return bytes(data)


def profile_for(image: bytes):
    """The packaged profile with this synthetic image's table and identity.

    Only the facts these tests observe are changed, exactly as
    `test_map_transition_project` does, so the fixture cannot pass by accidentally
    matching an independently invented profile.
    """
    from dataclasses import replace

    from tools.webfoot.binary import GbaRomAddress
    from tools.webfoot.packaged import packaged_profile
    from tools.webfoot.profile import MapEntryTableProfile

    base = packaged_profile()
    assert base.map_entries is not None
    return replace(
        base,
        id="synthetic_warp_workbench",
        sha256=hashlib.sha256(image).hexdigest(),
        size=len(image),
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(GBA_BASE + 0x0100),
            count=len(PER_MAP),
            record_size=base.map_entries.record_size,
        ),
    )


def project_meta(image: bytes) -> ProjectMeta:
    return ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id="synthetic_warp_workbench",
        game="synthetic",
        base_rom_sha256=hashlib.sha256(image).hexdigest(),
        base_rom_size=len(image),
        name="warp-workbench-test",
    )


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def image() -> bytes:
    return image_bytes()


@pytest.fixture
def project(tmp_path, image) -> Path:
    write_project(tmp_path, project_meta(image), enemies=[], characters=[])
    return tmp_path


def session_for(image: bytes, project: Path | None, selected_map: str | None = None) -> Session:
    session = Session(rom_image=image, rom_path=Path("synthetic.gba"))
    session.profile = profile_for(image)
    session.project_dir = project
    session.selected_map = selected_map
    return session


@pytest.fixture
def tab(qapp, image, project) -> WarpTab:
    widget = WarpTab(session_for(image, project, selected_map="map:0000"))
    widget.select_source_map(0)
    return widget


def build_image(image: bytes, application):
    """Apply the production authority's own change set, through the writer."""
    from tools.webfoot.write import apply_plan, plan_changes

    profile = profile_for(image)
    plan = plan_changes(
        image,
        application.changes,
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
    )
    return apply_plan(image, plan)


def edited_record(project: Path, image: bytes, identity):
    """The record the production build would write for one authored transition."""
    profile = profile_for(image)
    requests = mt.read_project_transition_requests(project)
    application = mt.plan_transition_edits(image, requests, profile=profile)
    built = build_image(image, application)
    corpus = mt.read_map_transitions(built, profile)
    return corpus.entry(identity).record, application


# --- the list ----------------------------------------------------------------


def test_the_list_shows_the_maps_connections_without_addresses(tab):
    """List population: one row per record, and no ROM address anywhere."""
    assert tab.source_map_index() == 0
    assert tab.row_count() == 2
    first = tab.row_values(0)
    assert first[0] == "0000"
    assert first[1] == "map:0001"
    # Positional, exactly as the codec names the intervals.
    assert first[2] == "first 100\u2013140 \u00b7 second 20\u201360"
    assert first[3] == "48, 40"
    assert first[4] == "Unchanged"
    assert first[5] == "Retail"
    second = tab.row_values(1)
    assert second[1] == "map:0002"
    assert second[3] == "12, 34"
    every_cell = " ".join(tab.row_values(0) + tab.row_values(1))
    assert "0x" not in every_cell
    assert "0x" not in tab._table.item(0, 0).toolTip()


def test_a_map_with_no_connections_says_so(tab):
    tab.select_source_map(4)
    assert tab.row_count() == 0
    assert tab.selected_identity() is None
    assert "no connections" in tab.status_line()
    # Nothing of the previous selection is left on screen.
    state = tab.form_state()
    assert state["destination"] is None
    assert state["arrival"] == (0, 0)
    assert state["state"] == "No connection selected"
    assert tab._destination.isEnabled() is False
    assert tab._arrival_hint.text() == ""
    assert tab._facing_hint.text() == ""


def test_selecting_a_row_loads_its_editable_state(tab):
    """Selection: the row's own values reach the editor, with no editing yet."""
    assert tab.select_row(1)
    state = tab.form_state()
    assert state["identity"] == "map:0000/transition:0001"
    assert state["destination"] == 2
    assert state["arrival"] == (12, 34)
    assert state["facing"] is None
    assert state["state"] == "Retail"
    assert state["editable"] is True
    assert tab._identity.text() == "map:0000/transition:0001"
    assert "200\u2013240" in tab._region_label.text()
    assert tab.unsaved_edit_count() == 0


def test_the_destination_picker_is_semantic_and_never_an_address(tab):
    choices = tab.destination_choices()
    assert len(choices) == len(PER_MAP)
    assert [index for _label, index in choices] == list(range(len(PER_MAP)))
    assert all(label.startswith("map:") for label, _index in choices)
    assert all("0x" not in label for label, _index in choices)


# --- the edits ---------------------------------------------------------------


def test_a_combined_retarget_stages_destination_arrival_and_facing(tab):
    """One gesture: retarget, derive the safe arrival, default the facing."""
    assert tab.stage_destination(3)
    draft = tab.staged_edit(TARGET)
    assert draft is not None
    assert draft.destination == MapIdentity(3)
    # The centre of map 3's own record back to map 0: (100+140)//2, (20+60)//2.
    assert draft.arrival == TransitionArrival(120, 40)
    # map 3 is 304x304, and the arrival is 40 px from its south edge, so the SDK's
    # documented authoring default turns the player South.
    assert draft.facing == 0
    assert tab.undo_stack().count() == 1
    # The row now states the staged values, not the retail ones.
    row = tab.row_values(0)
    assert row[1] == "map:0003"
    assert row[3] == "120, 40"
    assert row[4] == "South"
    assert row[5] == "Staged"
    assert tab.unsaved_edit_count() == 1


def test_an_arrival_edit_stages_only_the_arrival(tab):
    assert tab.stage_arrival(55, 66)
    draft = tab.staged_edit(TARGET)
    assert draft.destination is None
    assert draft.facing is None
    assert draft.arrival == TransitionArrival(55, 66)
    assert tab.undo_stack().count() == 1
    assert tab.row_values(0)[3] == "55, 66"
    assert tab.row_values(0)[1] == "map:0001"


def test_a_facing_edit_authors_the_override_for_the_chosen_direction(tab):
    assert tab.stage_facing(2)
    draft = tab.staged_edit(TARGET)
    assert draft.facing == 2
    assert draft.destination is None
    assert draft.arrival is None
    assert tab.row_values(0)[4] == "West"


def test_the_facing_control_offers_five_choices_and_no_raw_byte(tab):
    """M2's regression: the low bits are a gate, never a direction."""
    assert tab.facing_choices() == (
        ("Unchanged", None),
        ("South", 0),
        ("North", 1),
        ("West", 2),
        ("East", 3),
    )
    # The selected record's byte is 0x02: a gate, no override. It must read
    # Unchanged, and the hint must say the record states no facing at all.
    tab.select_row(0)
    assert tab.facing_choice() is None
    assert "states no facing" in tab._facing_hint.text()
    # A record whose byte is 0x0E also states no override.
    tab.select_row(1)
    assert tab.facing_choice() is None
    assert "0x" not in tab._facing.currentText()
    assert "0x" not in tab._facing_hint.text()


def test_a_facing_edit_preserves_the_unresolved_low_nibble(tab, project, image):
    """The low nibble is carried through: 0x0E -> South authors 0x1E, not 0x10."""
    tab.select_row(1)
    assert tab.stage_facing(0)
    assert tab.apply_to_project()
    record, _application = edited_record(
        project, image, mt.TransitionIdentity(MapIdentity(0), 1)
    )
    assert record.byte_0x10_raw == 0x1E
    assert record.facing.arrival_direction == 0
    assert record.facing.gate_direction == 2


def test_a_retarget_to_a_map_with_no_connection_back_is_refused(tab):
    """The toolkit will not leave an arrival belonging to the old destination."""
    assert tab.stage_destination(4) is False
    assert tab.staged_edit(TARGET) is None
    assert tab.undo_stack().count() == 0
    assert "no connection back" in tab.status_line()
    assert "no connection back" in tab._reason.text()


def test_an_arrival_outside_the_destination_is_refused(tab):
    """CQA-06: an invalid arrival reaches the surface and stages nothing."""
    assert tab.stage_destination(3)
    before = tab.staged_edit(TARGET)
    # map 3 is 304x304, so 700 is off it. The refusal is the authority's own.
    assert tab.stage_arrival(700, 700) is False
    assert tab.staged_edit(TARGET) == before
    assert "off the map" in tab.status_line()
    assert "off the map" in tab._reason.text()


def test_an_edit_that_changes_nothing_is_not_staged_and_leaves_no_undo(tab, project):
    """The no-op rule: a gesture that asks for the base value authors nothing."""
    assert tab.stage_destination(1) is False
    assert tab.stage_arrival(48, 40) is False
    assert tab.stage_facing(None) is False
    assert tab.staged_edit(TARGET) is None
    assert tab.undo_stack().count() == 0
    assert tab.unsaved_edit_count() == 0
    assert not (project / TRANSITION_FILE).exists()
    assert tab.apply_to_project() is False
    assert not (project / TRANSITION_FILE).exists()


# --- the class-169 refusal ---------------------------------------------------


def test_a_169_class_connection_is_read_only_with_a_reason(tab):
    """M3's regression: the surface cannot present it as retargetable."""
    tab.select_row(1)
    tab.select_source_map(2)
    assert tab.select_row(0)
    assert tab.selected_identity() == SCENE_RELATIVE
    assert tab.selected_editable() is False
    refusal = tab.edit_refusal()
    assert refusal is not None and "169-class" in refusal
    assert tab.form_state()["state"] == "Read-only"
    assert tab._destination.isEnabled() is False
    assert tab._arrival_x.isEnabled() is False
    assert tab._arrival_y.isEnabled() is False
    assert tab._facing.isEnabled() is False
    assert tab._apply_button.isEnabled() is False
    assert tab._revert_button.isEnabled() is False
    # The row states the refusal too, and shows no arrival for a delta.
    assert tab.row_values(0)[3] == "\u2014"
    assert tab.row_values(0)[5] == "Read-only"
    # And every gesture refuses, staging nothing.
    assert tab.stage_destination(0) is False
    assert tab.stage_arrival(10, 10) is False
    assert tab.stage_facing(0) is False
    assert tab.staged_edit(SCENE_RELATIVE) is None
    assert tab.unsaved_edit_count() == 0


def test_the_authority_refuses_a_169_class_arrival_on_its_own(tab):
    """The refusal is the authority's, not only the surface's."""
    corpus = mt.read_map_transitions(image_bytes(), profile_for(image_bytes()))
    identity = mt.TransitionIdentity(MapIdentity(2), 0)
    record = corpus.entry(identity).record
    assert record.class_raw == TRANSITION_CLASS_B_RAW
    assert record.has_raw_arrival_pair is False
    # The stored pair is a delta, so asking for it as a point is refused...
    with pytest.raises(MapTransitionValueError):
        record.arrival
    # ...and so is authoring one, through the same entry point the surface uses.
    with pytest.raises(mt.TransitionFieldError):
        corpus.check_edit(identity, mt.TransitionEdit(arrival=TransitionArrival(4, 4)))
    with pytest.raises(mt.TransitionFieldError):
        corpus.set_arrival(identity, TransitionArrival(4, 4))
    with pytest.raises(mt.TransitionFieldError):
        corpus.derive_arrival(identity, MapIdentity(0))


def test_check_edit_records_nothing(tab):
    corpus = mt.read_map_transitions(image_bytes(), profile_for(image_bytes()))
    identity = mt.TransitionIdentity(MapIdentity(0), 0)
    before = corpus.entry(identity).record
    corpus.check_edit(
        identity,
        mt.TransitionEdit(destination=MapIdentity(3), arrival=TransitionArrival(120, 40)),
    )
    assert corpus.entry(identity).record == before
    assert corpus.destination(identity) == MapIdentity(1)


# --- apply / revert ----------------------------------------------------------


def test_apply_writes_the_project_and_revert_un_authors_it(tab, project):
    assert tab.stage_facing(1)
    assert tab.apply_to_project() is True
    assert (project / TRANSITION_FILE).is_file()
    authored = mt.read_project_transition_requests(project)
    identity = mt.TransitionIdentity(MapIdentity(0), 0)
    assert authored[identity].facing_raw == 0x22  # ((North + 1) << 4) | gate 2
    assert authored[identity].prior_facing_raw == 0x02
    assert tab.row_values(0)[4] == "North"
    assert tab.row_values(0)[5] == "Saved"
    assert tab.unsaved_edit_count() == 0
    assert tab.undo_stack().count() == 0

    # Revert with nothing staged un-authors the saved edit.
    assert tab.revert_selected() is True
    assert mt.read_project_transition_requests(project) == {}
    assert not (project / TRANSITION_FILE).exists()
    assert tab.row_values(0)[5] == "Retail"
    assert tab.row_values(0)[4] == "Unchanged"


def test_apply_does_not_write_when_the_project_already_holds_it(tab, project):
    assert tab.stage_facing(1)
    assert tab.apply_to_project() is True
    before = (project / TRANSITION_FILE).read_bytes()
    # Staging the value the project now already holds asks for nothing, and a
    # subsequent Apply writes nothing at all.
    assert tab.stage_facing(1) is False
    assert tab.unsaved_edit_count() == 0
    assert tab.apply_to_project() is False
    assert (project / TRANSITION_FILE).read_bytes() == before


def test_revert_discards_a_staged_edit_and_is_undoable(tab, project):
    assert tab.stage_facing(3)
    assert tab.revert_selected() is True
    assert tab.staged_edit(TARGET) is None
    assert tab.undo_stack().canUndo()
    tab.undo_stack().undo()
    assert tab.staged_edit(TARGET).facing == 3
    assert not (project / TRANSITION_FILE).exists()


# --- undo / redo -------------------------------------------------------------


def test_undo_and_redo_return_each_authored_value_exactly(tab):
    # destination
    assert tab.stage_destination(3)
    assert tab.undo_stack().count() == 1
    tab.undo_stack().undo()
    assert tab.staged_edit(TARGET) is None
    assert tab.row_values(0)[1] == "map:0001"
    tab.undo_stack().redo()
    assert tab.staged_edit(TARGET).destination == MapIdentity(3)

    # arrival, on top of the retarget
    assert tab.stage_arrival(200, 100)
    assert tab.undo_stack().count() == 2
    tab.undo_stack().undo()
    assert tab.staged_edit(TARGET).arrival == TransitionArrival(120, 40)
    assert tab.staged_edit(TARGET).destination == MapIdentity(3)
    tab.undo_stack().redo()
    assert tab.staged_edit(TARGET).arrival == TransitionArrival(200, 100)

    # facing, on top of both
    assert tab.stage_facing(3)
    assert tab.undo_stack().count() == 3
    tab.undo_stack().undo()
    assert tab.staged_edit(TARGET).facing == 0
    tab.undo_stack().redo()
    assert tab.staged_edit(TARGET).facing == 3
    # The combined retarget is still one entry per gesture, in order.
    assert tab.staged_edit(TARGET).destination == MapIdentity(3)
    assert tab.staged_edit(TARGET).arrival == TransitionArrival(200, 100)
    assert tab.form_state()["facing"] == 3


def test_undoing_a_retarget_puts_the_arrival_and_facing_back(tab):
    assert tab.stage_destination(3)
    tab.undo_stack().undo()
    assert tab.staged_edit(TARGET) is None
    assert tab.form_state()["destination"] == 1
    assert tab.form_state()["arrival"] == (48, 40)
    assert tab.undo_stack().canRedo()


def test_a_no_op_gesture_never_enters_the_undo_history(tab):
    tab.stage_facing(2)
    count = tab.undo_stack().count()
    # Setting the same direction again, and the base destination, change nothing.
    tab.stage_facing(2)
    tab.stage_destination(1)
    assert tab.undo_stack().count() == count
    assert tab.staged_edit(TARGET).facing == 2


# --- CQA-05: mutation vs session lifecycle ------------------------------------


def test_a_project_mutation_keeps_the_staged_connection_edit(tab, project, image, monkeypatch):
    assert tab.stage_destination(3)
    staged = tab.staged_edit(TARGET)
    history = tab.undo_stack().count()
    # An unrelated project mutation, through the SDK, then the shell's broadcast.
    mt.set_transition_edits(
        project,
        profile_for(image),
        image,
        {
            mt.TransitionIdentity(MapIdentity(0), 1): mt.TransitionEdit(
                destination=MapIdentity(3)
            )
        },
    )
    tab.on_project_mutated()
    assert tab.staged_edit(TARGET) == staged
    assert tab.undo_stack().count() == history
    assert tab.unsaved_edit_count() == 1
    # The unrelated edit is visible as saved work beside the staged one.
    assert tab.row_values(1)[5] == "Saved"
    assert tab.row_values(0)[5] == "Staged"


def test_a_session_replacement_clears_the_staged_connection_edit(tab, project):
    assert tab.stage_destination(3)
    assert tab.unsaved_edit_count() == 1
    tab.on_session_changed()
    assert tab.unsaved_edit_count() == 0
    assert tab.staged_edit(TARGET) is None
    assert tab.undo_stack().count() == 0
    assert tab.selected_identity() == TARGET
    assert tab.row_values(0)[5] == "Retail"


# --- CQA-06: expected failures reach the surface ------------------------------


def test_a_malformed_project_connection_document_is_reported(qapp, image, project, monkeypatch):
    """A malformed maps/transitions.toml is stated, not raised at the user."""
    (project / "maps").mkdir(parents=True, exist_ok=True)
    (project / TRANSITION_FILE).write_text("[transition]\n", encoding="utf-8", newline="\n")
    tab = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert "could not be read" in tab.status_line()
    # Editing is refused while the project document cannot be read at all.
    assert tab.selected_editable() is False
    assert tab._destination.isEnabled() is False


def test_apply_reports_an_sdk_refusal_instead_of_a_dead_click(tab, project, image, monkeypatch):
    """A refused Apply reaches the user through the normal error surface.

    The illegal batch is injected rather than produced by the form, because the
    form is the first gate and refuses it before it can be staged. What is under
    test is the second gate: if anything reaches Apply that the authority refuses,
    the user sees the reason instead of a dead click.
    """
    shown: list[str] = []
    monkeypatch.setattr(
        wt.QMessageBox, "warning", staticmethod(lambda *a, **k: shown.append(a[2]))
    )
    assert tab.stage_facing(1)
    tab._staged[mt.TransitionIdentity(MapIdentity(0), 9)] = mt.TransitionEdit(facing=0)
    assert tab.apply_to_project() is False
    assert shown and "no transition with identity" in shown[0]
    # The staged edits are intact, so the user can fix and retry.
    assert tab.unsaved_edit_count() == 2
    assert not (project / TRANSITION_FILE).exists()


def test_apply_without_a_project_is_refused_with_a_reason(tab, image, monkeypatch):
    shown: list[str] = []
    monkeypatch.setattr(
        wt.QMessageBox, "warning", staticmethod(lambda *a, **k: shown.append(a[2]))
    )
    assert tab.stage_facing(1)
    # The project source goes away after the edit was staged: the same state a user
    # reaches by closing the project in the Build panel.
    tab._session.project_dir = None
    assert tab.apply_to_project() is False
    assert "Open a Webfoot project" in tab.status_line()
    assert shown and "Open a Webfoot project" in shown[0]
    assert tab.unsaved_edit_count() == 1


# --- CQA-07: bounded project and corpus I/O -----------------------------------


@pytest.fixture
def reads(monkeypatch):
    """Count the whole-image and whole-project reads, and the project writes.

    ``project`` is the parse that matters: ONE `read_project` supplies BOTH of the
    project's transition documents, and the two counters next to it are the SDK's
    own conversions of what that one parse produced
    (`transition_edits_to_requests`, `transition_creations_to_requests`) - so the
    surface cannot read the same project twice per mutation as it grows.
    MAP-WARP-CREATE-WORKBENCH-001 added the second document; the parse count is
    unchanged.
    """
    import tools.webfoot.project as project_module

    counts = {
        "corpus": 0,
        "project": 0,
        "labels": 0,
        "conversions": 0,
        "writes": 0,
    }
    real_corpus = mt.read_map_transitions
    real_project = project_module.read_project
    real_labels = mv.read_map_index
    real_edits_to_requests = mt.transition_edits_to_requests
    real_creations_to_requests = mt.transition_creations_to_requests
    real_writes = mt.set_transition_edits

    def corpus(*a, **k):
        counts["corpus"] += 1
        return real_corpus(*a, **k)

    def project(*a, **k):
        counts["project"] += 1
        return real_project(*a, **k)

    def labels(*a, **k):
        counts["labels"] += 1
        return real_labels(*a, **k)

    def edits_to_requests(*a, **k):
        counts["conversions"] += 1
        return real_edits_to_requests(*a, **k)

    def creations_to_requests(*a, **k):
        counts["conversions"] += 1
        return real_creations_to_requests(*a, **k)

    def writes(*a, **k):
        counts["writes"] += 1
        return real_writes(*a, **k)

    monkeypatch.setattr(mt, "read_map_transitions", corpus)
    monkeypatch.setattr(project_module, "read_project", project)
    monkeypatch.setattr(mv, "read_map_index", labels)
    monkeypatch.setattr(mt, "transition_edits_to_requests", edits_to_requests)
    monkeypatch.setattr(
        mt, "transition_creations_to_requests", creations_to_requests
    )
    monkeypatch.setattr(mt, "set_transition_edits", writes)
    return counts


def test_loading_the_surface_reads_each_domain_once(qapp, reads, image, project):
    WarpTab(session_for(image, project, selected_map="map:0000"))
    assert reads == {
        "corpus": 1,
        "project": 1,
        "labels": 1,
        "conversions": 2,
        "writes": 0,
    }


def test_selecting_and_editing_read_nothing(tab, reads):
    for key in reads:
        reads[key] = 0
    tab.select_row(0)
    tab.select_row(1)
    tab.select_row(0)
    tab.stage_destination(3)
    tab.stage_arrival(200, 100)
    tab.stage_facing(3)
    tab.undo_stack().undo()
    tab.undo_stack().redo()
    tab.select_source_map(1)
    tab.select_source_map(0)
    assert reads == {
        "corpus": 0,
        "project": 0,
        "labels": 0,
        "conversions": 0,
        "writes": 0,
    }


def test_one_apply_is_one_write_and_one_reproject_read(tab, reads):
    tab.stage_destination(3)
    for key in reads:
        reads[key] = 0
    assert tab.apply_to_project() is True
    # Exact counts, not a bound: the authority reads the canonical corpus once and
    # parses the project once itself, and the surface re-reads the project once to
    # show what was just written - from which both transition documents are derived.
    # Nothing here grows with the number of controls, rows or staged fields.
    assert reads == {
        "corpus": 1,
        "project": 2,
        "labels": 0,
        "conversions": 2,
        "writes": 1,
    }


# --- save / reopen -----------------------------------------------------------


def test_save_and_reopen_shows_the_same_authored_values(qapp, image, project):
    first = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert first.stage_destination(3)
    assert first.stage_arrival(200, 100)
    assert first.stage_facing(3)
    assert first.apply_to_project() is True
    assert first.unsaved_edit_count() == 0

    # Close and reopen: a fresh session, the same project, a fresh surface.
    reopened_project = read_project(project)
    assert not reopened_project.transitions.is_empty()
    second = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert second.row_count() == first.row_count()
    row = second.row_values(0)
    assert row[1] == "map:0003"
    assert row[3] == "200, 100"
    assert row[4] == "East"
    assert row[5] == "Saved"
    assert second.form_state()["destination"] == 3
    assert second.form_state()["arrival"] == (200, 100)
    assert second.form_state()["facing"] == 3
    # The reopened values are the authored ones, and the authored document is the
    # one the production authority builds.
    record, application = edited_record(
        project, image, mt.TransitionIdentity(MapIdentity(0), 0)
    )
    assert record.destination_key == key_for(3)
    assert record.arrival == TransitionArrival(200, 100)
    assert record.facing.arrival_direction == 3
    assert [entry.owner for entry in application.changes if entry.is_effective] == [
        TARGET
    ]


def test_the_applied_retarget_is_byte_local_to_one_record(image, project, qapp):
    tab = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert tab.stage_destination(3)
    assert tab.apply_to_project()
    requests = mt.read_project_transition_requests(project)
    application = mt.plan_transition_edits(image, requests, profile=profile_for(image))
    built = build_image(image, application)
    identity = mt.TransitionIdentity(MapIdentity(0), 0)
    entry = mt.read_map_transitions(image, profile_for(image)).entry(identity)
    changed = [
        index
        for index in range(len(image))
        if image[index] != built[index]
    ]
    record_span = set(range(entry.file_offset, entry.file_offset + 24))
    assert changed, "the applied retarget must change bytes"
    assert set(changed) <= record_span
    # The other record on the same map is untouched.
    other = mt.read_map_transitions(image, profile_for(image)).entry(
        mt.TransitionIdentity(MapIdentity(0), 1)
    )
    other_span = range(other.file_offset, other.file_offset + 24)
    assert not any(index in other_span for index in changed)


def test_a_malformed_project_document_is_refused_by_the_loader(project, image):
    """The refusal the surface reports is the project layer's own."""
    (project / "maps").mkdir(parents=True, exist_ok=True)
    (project / TRANSITION_FILE).write_text("[transition]\n", encoding="utf-8", newline="\n")
    with pytest.raises(ProjectLoadError):
        read_project(project)
