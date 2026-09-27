"""MAP-WARP-CREATE-WORKBENCH-001: the Warps surface's Create Transition action.

Focused regressions for CREATING a transition - one the canonical image does not
contain - from the shipped Maps -> Warps surface. The synthetic image is the one
`test_map_transitions` assembles from the measured format (a 0x38-stride map table,
a selector-1 root reached from `MapEntry + 0x2C`, and 24-byte records), extended
here with the two root words the destination's walkable extent comes from. The
project is a real on-disk project written by the real `write_project`, and every
creation goes through the real authority - no mocked SDK path.

Covered by name: Create-action availability and the fail-closed refusals, valid
566-class base filtering with the 169 class excluded, the durable authored name
validated by the production model, duplicate identity, the trigger region, the
semantic destination, the required arrival (never derived), the facing vocabulary,
low-nibble preservation through the authority, the staged new row, Apply/Revert,
Undo/Redo, the no-op rule, cancel without residue, CQA-05, CQA-06, CQA-07 and
save/reopen.

The synthetic image is deliberately not a canonical ROM and asserts no canonical
count. The real image, its real map 40 and the build are exercised in
``tests/integration/test_map_transition_create_rom.py``.
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
    CREATED_CLASS_RAW,
    FACING_EAST,
    FACING_NORTH,
    FACING_PRESERVED_MASK,
    TRANSITION_CLASS_B_RAW,
    TransitionArrival,
    TransitionRegion,
)
from tools.webfoot.maps import MapIdentity  # noqa: E402
from tools.webfoot.project import (  # noqa: E402
    PROJECT_FORMAT_VERSION,
    TRANSITION_CREATION_FILE,
    TRANSITION_FILE,
    ProjectMeta,
    read_project,
    write_project,
)
from tools.webfoot.workbench import warp_tab as wt  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402
from tools.webfoot.workbench.warp_tab import CreationDraft, WarpTab  # noqa: E402

from tests.unit.test_map_transitions import (  # noqa: E402
    GBA_BASE,
    ROOT_BASE,
    ROOT_STRIDE,
    SOURCE_BASE,
    key_for,
    record_bytes,
    synthetic_image,
)

#: One word pair per map. Maps 0-2 are 1008x1008 walkable; map 3 is 304x304 so an
#: off-map arrival has somewhere small to be off; map 4 mirrors map 0's size and is
#: used only by the shared-root fixture.
EXTENTS = (
    (0x02FF, 0x02FF),
    (0x02FF, 0x02FF),
    (0x02FF, 0x02FF),
    (0x003F, 0x003F),
    (0x02FF, 0x02FF),
)

#: The template's own unresolved bytes: a gate of 2 with NO arrival-facing override,
#: so "the created record states no override" and "it inherited the base's" differ,
#: and a low nibble a creation must carry through untouched.
TEMPLATE_BYTE_0X10 = 0x0E
TEMPLATE_BYTE_0X13 = 0x01
TEMPLATE_REGION = TransitionRegion(first=(100, 140), second=(20, 60))
TEMPLATE_ARRIVAL = TransitionArrival(48, 40)

#: Five maps:
#:
#: * map 0 - a 566-class record (the only valid base) at index 0, and a 169-class
#:   record at index 1, which must never be offered as a base;
#: * map 1 - one 566-class record: a destination a valid creation may lead to;
#: * map 2 - one 169-class record only: a map with NO valid creation base;
#: * map 3 - no records at all, and a small walkable extent;
#: * map 4 - no records at all (the shared-root fixture points it at map 3's root).
PER_MAP = [
    [
        record_bytes(
            destination_key=tuple(key_for(1)),
            first=TEMPLATE_REGION.first,
            second=TEMPLATE_REGION.second,
            byte_0x10=TEMPLATE_BYTE_0X10,
            byte_0x13=TEMPLATE_BYTE_0X13,
            word_0x14=TEMPLATE_ARRIVAL.x,
            byte_0x16=TEMPLATE_ARRIVAL.y & 0xFF,
            byte_0x17=TEMPLATE_ARRIVAL.y >> 8,
        ),
        record_bytes(
            class_raw=TRANSITION_CLASS_B_RAW,
            destination_key=tuple(key_for(1)),
            first=(10, 40),
            second=(10, 40),
            byte_0x10=0x02,
            word_0x14=8,
            byte_0x16=8,
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
            byte_0x10=0x02,
            word_0x14=8,
            byte_0x16=8,
            byte_0x17=0,
        )
    ],
    [],
    [],
]

TEMPLATE = mt.TransitionIdentity(MapIdentity(0), 0)
SCENE_RELATIVE = mt.TransitionIdentity(MapIdentity(0), 1)
#: The destination every valid creation in this file uses.
DESTINATION = MapIdentity(1)
#: Authored values that differ from the base in every field a creation authors, so a
#: staged creation is never an accidental alias of its template.
REGION = ((232, 273), (0, 17))
ARRIVAL = (16, 24)
NAME = "kai-shop"
NEW_DOOR = mt.CreatedTransitionIdentity(MapIdentity(0), NAME)


def image_bytes() -> bytes:
    """The synthetic corpus with each root's walkable extent written in."""
    data = bytearray(synthetic_image(PER_MAP))
    for index, (width, height) in enumerate(EXTENTS):
        root = ROOT_BASE + index * ROOT_STRIDE
        data[root + 0x08 : root + 0x0A] = (width - 1).to_bytes(2, "little")
        data[root + 0x0A : root + 0x0C] = (height - 1).to_bytes(2, "little")
    return bytes(data)


def shared_root_image() -> bytes:
    """The same image with maps 3 and 4 resolving to ONE connection root.

    Both roots carry a count of 0, which is the shape every one of the canonical
    image's 11 shared roots has, so the corpus still loads and the refusal is about
    the sharing rather than about a malformed image.
    """
    data = bytearray(image_bytes())
    data[SOURCE_BASE + 4 * 8 : SOURCE_BASE + 4 * 8 + 4] = (
        GBA_BASE + ROOT_BASE + 3 * ROOT_STRIDE
    ).to_bytes(4, "little")
    return bytes(data)


def profile_for(image: bytes):
    """The packaged profile with this synthetic image's table and identity.

    ``free_regions`` is emptied because the packaged profile's single declared
    VERIFIED_FREE region lies past this 32 KiB image, which the storage model would
    refuse - and because a creation is ``EXPANDED_ONLY``, so canonical free space is
    not something these tests should accidentally depend on.
    """
    from dataclasses import replace

    from tools.webfoot.binary import GbaRomAddress
    from tools.webfoot.packaged import packaged_profile
    from tools.webfoot.profile import MapEntryTableProfile

    base = packaged_profile()
    assert base.map_entries is not None
    return replace(
        base,
        id="synthetic_warp_creation",
        sha256=hashlib.sha256(image).hexdigest(),
        size=len(image),
        free_regions=(),
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(GBA_BASE + 0x0100),
            count=len(PER_MAP),
            record_size=base.map_entries.record_size,
        ),
    )


def project_meta(image: bytes) -> ProjectMeta:
    return ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id="synthetic_warp_creation",
        game="synthetic",
        base_rom_sha256=hashlib.sha256(image).hexdigest(),
        base_rom_size=len(image),
        name="warp-creation-test",
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


def author_one(tab: WarpTab, *, name: str = NAME) -> bool:
    """Author one complete, valid creation through the surface's own gestures."""
    tab.open_creation()
    tab.stage_creation_name(name)
    tab.stage_creation_region(*REGION)
    tab.stage_creation_destination(DESTINATION.index)
    tab.stage_creation_arrival(*ARRIVAL)
    tab.stage_creation_facing(FACING_EAST)
    return tab.staged_creation(f"map:0000/transition:{name}") is not None


def built_creation(image: bytes, project: Path, name: str = NAME):
    """The record the production build would materialize for one stored creation."""
    profile = profile_for(image)
    requests = mt.read_project_transition_creations(project)
    result = mt.materialize_transition_creations(image, requests, profile=profile)
    return result, result.provenance


# --- the Create action -------------------------------------------------------


def test_the_create_action_is_available_and_opens_a_form(tab):
    """The action is present, enabled and opens the creation surface."""
    assert tab.create_action_enabled() is True
    assert tab.creation_refusal() is None
    assert tab.creation_open() is False
    assert tab.open_creation() is True
    assert tab.creation_open() is True
    state = tab.creation_form_state()
    assert state["open"] is True
    assert state["source"] == 0
    assert state["name"] == ""
    assert state["template"] == str(TEMPLATE)
    # The base's own values are the visible starting point, and the facing starts at
    # Unchanged because the SDK deliberately does not inherit the base's override.
    assert state["region"] == (TEMPLATE_REGION.first, TEMPLATE_REGION.second)
    assert state["destination"] == 1
    assert state["arrival"] == (TEMPLATE_ARRIVAL.x, TEMPLATE_ARRIVAL.y)
    assert state["facing"] is None
    assert state["staged"] is False
    assert state["identity"] is None
    assert "name" in (state["reason"] or "").lower()
    # Opening a form is not a gesture.
    assert tab.undo_stack().count() == 0


def test_the_create_action_is_refused_without_a_project(qapp, image):
    tab = WarpTab(session_for(image, None, selected_map="map:0000"))
    assert tab.create_action_enabled() is True
    refusal = tab.creation_refusal()
    assert refusal is not None and "maps/transition_creations.toml" in refusal
    assert tab.open_creation() is False
    assert tab.creation_open() is False
    assert "maps/transition_creations.toml" in tab.status_line()


def test_the_create_action_is_refused_without_an_image(qapp, project):
    tab = WarpTab(Session(rom_image=None, rom_path=None))
    tab._session.project_dir = project
    assert tab.open_creation() is False
    assert "Open a game image" in tab.status_line()


# --- the base filter ---------------------------------------------------------


def test_only_566_class_transitions_are_offered_as_a_base(tab):
    """M1's regression: a 169-class record must never be a creation base."""
    assert tab.open_creation()
    offered = tab.creation_templates()
    identities = [template for _label, template in offered]
    assert identities == [TEMPLATE]
    assert SCENE_RELATIVE not in identities
    every_cell = " ".join(label for label, _template in offered)
    assert "0x" not in every_cell
    assert every_cell.startswith("transition 0000")
    # And the exclusion is the authority's own rule, not this surface's opinion.
    corpus = mt.read_map_transitions(image_bytes(), profile_for(image_bytes()))
    assert SCENE_RELATIVE not in {
        entry.identity for entry in mt.creation_templates(corpus, MapIdentity(0))
    }
    assert [entry.identity for entry in mt.creation_templates(corpus, MapIdentity(0))] == [
        TEMPLATE
    ]


def test_a_map_with_no_566_class_base_is_refused_safely(qapp, image, project):
    """A map whose only records are 169-class cannot be created on, and says why."""
    tab = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert tab.select_source_map(2)
    assert tab.creation_templates() == ()
    refusal = tab.creation_refusal()
    assert refusal is not None and "566-class" in refusal
    assert tab.open_creation() is False
    assert tab.creation_open() is False
    # Nothing is authorable and nothing is staged.
    assert tab.staged_creation_count() == 0
    assert tab.undo_stack().count() == 0
    assert "566-class" in tab.status_line()


def test_a_shared_connection_root_refuses_creation(qapp, project):
    """A root shared with another map would give that map the new connection too."""
    image = shared_root_image()
    tab = WarpTab(session_for(image, project, selected_map="map:0000"))
    corpus = mt.read_map_transitions(image, profile_for(image))
    assert corpus.shared_root_maps(MapIdentity(3)) == (MapIdentity(4),)
    assert tab.select_source_map(3)
    refusal = tab.creation_refusal()
    assert refusal is not None
    assert "shared with map:0004" in refusal
    assert tab.open_creation() is False
    assert tab.creation_open() is False


# --- the authored identity ---------------------------------------------------


def test_the_authored_name_becomes_a_durable_identity(tab):
    assert tab.open_creation()
    assert tab.stage_creation_name(NAME)
    assert tab.creation_identity() == NEW_DOOR.key
    assert tab.creation_draft().identity() == NEW_DOOR
    # No array index, no address, no raw byte: the identity is a map key and a name.
    assert "0x" not in NEW_DOOR.key
    assert NEW_DOOR.key.count(":") == 2


@pytest.mark.parametrize("name", ["", "Door", "1door", "-door", "door name", "dÃ¸or"])
def test_an_invalid_name_is_refused_with_the_production_wording(tab, name):
    """The name rule is the production model's, and its message is what is shown."""
    assert tab.open_creation()
    if name:
        assert tab.stage_creation_name(name) is True
    else:
        tab.stage_creation_name(name)
    assert tab.creation_identity() is None
    assert tab.staged_creation_count() == 0
    reason = tab.creation_reason()
    assert reason is not None
    if name == "":
        assert "Author a name" in reason
    else:
        assert "lowercase" in reason and "start with a letter" in reason


def test_an_invalid_name_stages_nothing_and_creates_no_row(tab):
    rows_before = tab.row_count()
    assert tab.open_creation()
    tab.stage_creation_name("Door")
    assert tab.row_count() == rows_before
    assert tab.staged_creation_count() == 0
    assert not (tab._session.project_dir / TRANSITION_CREATION_FILE).exists()


def test_a_duplicate_authored_identity_is_refused(tab, project):
    """M2's regression: a durable identity is claimed by one creation only."""
    assert author_one(tab)
    assert tab.apply_creations() is True
    stored = (project / TRANSITION_CREATION_FILE).read_bytes()

    # Author a SECOND creation, with different values, under the same name.
    assert tab.close_creation() is True
    assert tab.open_creation() is True
    tab.stage_creation_name(NAME)
    tab.stage_creation_region((1, 2), (3, 4))
    tab.stage_creation_destination(2)
    tab.stage_creation_arrival(5, 6)
    assert tab.staged_creation_count() == 0
    reason = tab.creation_reason()
    assert reason is not None and "durable" in reason
    assert NEW_DOOR.key in reason
    assert (project / TRANSITION_CREATION_FILE).read_bytes() == stored
    # The saved creation is still exactly what the project holds.
    saved = tab.saved_creation(NEW_DOOR.key)
    assert saved is not None and saved.region == TransitionRegion(
        first=REGION[0], second=REGION[1]
    )
    # ...and the row opened FROM that saved creation MAY be re-authored, which is
    # the update path a refusal must not block.
    assert tab.select_row(2) is True
    assert tab.stage_creation_arrival(60, 70) is True
    assert tab.staged_creation_count() == 1
    assert tab.creation_reason() is None
    assert tab.apply_creations() is True
    assert tab.saved_creation(NEW_DOOR.key).arrival == TransitionArrival(60, 70)


def test_a_duplicate_of_a_staged_creation_is_refused(tab):
    """Two drafts may not claim one durable identity before either is applied."""
    assert author_one(tab)
    staged = tab.staged_creation(NEW_DOOR.key)
    assert staged is not None
    # A second form, authoring the same name with different values.
    assert tab.close_creation() is True
    assert tab.open_creation() is True
    tab.stage_creation_destination(3)
    tab.stage_creation_arrival(11, 22)
    tab.stage_creation_name(NAME)
    reason = tab.creation_reason()
    assert reason is not None and "already staged" in reason
    assert tab.staged_creation(NEW_DOOR.key) == staged
    assert tab.staged_creation_count() == 1


# --- the base -----------------------------------------------------------------


def test_a_169_class_record_cannot_be_selected_as_a_base(tab):
    """The refusal is the authority's, not only the surface's absence of a choice."""
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    assert tab.stage_creation_template(SCENE_RELATIVE) is True
    reason = tab.creation_reason()
    assert reason is not None
    assert "scene-relative delta" in reason
    assert tab.staged_creation_count() == 0


def test_a_base_from_another_map_is_refused(tab):
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    assert tab.stage_creation_template(mt.TransitionIdentity(MapIdentity(1), 0))
    reason = tab.creation_reason()
    assert reason is not None and "same source map" in reason
    assert tab.staged_creation_count() == 0


def test_a_creation_that_equals_its_base_is_refused_as_an_alias(tab):
    """Authoring only a name over the seeded base is a copy, not a creation."""
    assert tab.open_creation()
    assert tab.stage_creation_name(NAME) is True
    reason = tab.creation_reason()
    assert reason is not None and "byte-identical" in reason
    assert tab.staged_creation_count() == 0


def test_a_template_prior_conflict_is_reported(tab, project, image):
    """CQA-06, the template prior: a project authored against other template bytes.

    The template's ``+0x10`` and ``+0x13`` are pinned in the document, so an image
    whose template record holds different bytes is refused rather than silently
    initializing the created record from them. The build reports that refusal
    through the same authority call this asserts (its own entry point returns early
    for a non-canonical profile, which a synthetic image necessarily is - so the
    authority is what is checked here).
    """
    from tools.webfoot.project import (
        AuthoredTransitionCreation as StoredCreation,
        TransitionCreations,
        write_transition_creations,
    )

    assert author_one(tab)
    assert tab.apply_creations() is True
    entry = read_project(project).transition_creations.edits()[(0, NAME)]
    drifted = StoredCreation(
        source=entry.source,
        name=entry.name,
        template=entry.template,
        destination=entry.destination,
        region=entry.region,
        arrival=entry.arrival,
        prior_facing_raw=entry.prior_facing_raw ^ 0x01,
        prior_unresolved_raw=entry.prior_unresolved_raw,
    )
    write_transition_creations(
        project, TransitionCreations.from_edits({(0, NAME): drifted})
    )
    # The surface still lists the project's creation rather than hiding it...
    reopened = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert NEW_DOOR.key in reopened.creation_row_keys()
    assert reopened.row_values(2)[5] == "New (saved)"
    # ...and materializing what the project stored is refused, naming the byte.
    requests = mt.transition_creations_to_requests(
        read_project(project).transition_creations
    )
    with pytest.raises(mt.TransitionFieldError, match=r"\+0x10"):
        mt.materialize_transition_creations(
            image, requests, profile=profile_for(image)
        )


# --- trigger region ----------------------------------------------------------


def test_the_trigger_region_is_authored_positionally(tab):
    assert tab.open_creation()
    assert tab.stage_creation_region((232, 273), (0, 17)) is True
    assert tab.creation_draft().region == ((232, 273), (0, 17))
    state = tab.creation_form_state()
    assert state["region"] == ((232, 273), (0, 17))
    # The form's own labels are the codec's positional names, and no axis name or
    # unit is invented anywhere on it.
    labels = [
        label.text()
        for label in tab._creation_region_spins[0].parent().findChildren(wt.QLabel)
    ]
    assert "first" in labels and "second" in labels
    assert not any(
        word in " ".join(labels).lower() for word in ("horizontal", "vertical", "pixel")
    )


def test_a_degenerate_or_unordered_region_is_refused(tab):
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    tab.stage_creation_region((10, 10), (0, 4))
    reason = tab.creation_reason()
    assert reason is not None and "degenerate" in reason
    assert tab.staged_creation_count() == 0
    tab.stage_creation_region((10, 4), (0, 4))
    reason = tab.creation_reason()
    assert reason is not None and "low <= high" in reason
    assert tab.staged_creation_count() == 0


# --- destination and arrival -------------------------------------------------


def test_the_destination_selector_is_semantic_and_never_an_address(tab):
    assert tab.open_creation()
    choices = [
        (tab._creation_destination.itemText(row), tab._creation_destination.itemData(row))
        for row in range(tab._creation_destination.count())
    ]
    assert [index for _label, index in choices] == list(range(len(PER_MAP)))
    assert all(label.startswith("map:") for label, _index in choices)
    assert all("0x" not in label for label, _index in choices)


def test_an_unknown_destination_is_refused(tab):
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    tab.stage_creation_destination(9)
    reason = tab.creation_reason()
    assert reason is not None and "declared map-entry range" in reason
    assert tab.staged_creation_count() == 0


def test_the_arrival_is_required_and_never_derived_from_the_destination(tab):
    """A new transition has no existing link, so its arrival is authored."""
    assert tab.open_creation()
    seeded = tab.creation_form_state()["arrival"]
    # The seed is the BASE's own point, not a point derived from the destination.
    assert seeded == (TEMPLATE_ARRIVAL.x, TEMPLATE_ARRIVAL.y)
    assert "Required" in tab._creation_arrival_hint.text()
    assert tab.stage_creation_destination(3) is True
    assert tab.creation_form_state()["arrival"] == seeded
    assert tab.stage_creation_arrival(400, 260) is True
    assert tab.creation_form_state()["arrival"] == (400, 260)


def test_an_arrival_off_the_destination_is_refused(tab):
    """CQA-06: the authority's own bounds refusal reaches the form."""
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    tab.stage_creation_region(*REGION)
    tab.stage_creation_destination(3)  # map 3 is 304x304
    tab.stage_creation_arrival(700, 700)
    reason = tab.creation_reason()
    assert reason is not None and "off the map" in reason
    assert tab.staged_creation_count() == 0


# --- facing ------------------------------------------------------------------


def test_the_facing_control_offers_five_choices_and_no_raw_byte(tab):
    assert tab.open_creation()
    choices = tuple(
        (tab._creation_facing.itemText(row), tab._creation_facing.itemData(row))
        for row in range(tab._creation_facing.count())
    )
    assert choices == (
        ("Unchanged", None),
        ("South", 0),
        ("North", 1),
        ("West", 2),
        ("East", 3),
    )
    assert "0x" not in tab._creation_facing.currentText()


def test_an_invalid_facing_is_refused(tab):
    """Facing is a semantic direction 0..3 or Unchanged; anything else is refused."""
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    tab.stage_creation_region(*REGION)
    tab.stage_creation_destination(3)
    tab.stage_creation_arrival(100, 100)
    tab.stage_creation_facing(9)
    reason = tab.creation_reason()
    assert reason is not None and "facing" in reason
    assert tab.staged_creation_count() == 0


def test_unchanged_authors_no_override_and_keeps_the_base_gate(tab, project, image):
    assert author_one(tab)
    tab.stage_creation_facing(None)
    assert tab.creation_draft().facing is None
    assert tab.apply_creations() is True
    _result, provenance = built_creation(image, project)
    assert provenance[0].facing is None
    assert provenance[0].facing_raw & ~FACING_PRESERVED_MASK == 0
    assert provenance[0].facing_raw & FACING_PRESERVED_MASK == (
        TEMPLATE_BYTE_0X10 & FACING_PRESERVED_MASK
    )


def test_the_created_record_preserves_the_bases_low_nibble(tab, project, image):
    """M5's regression: the low nibble is carried, never replaced."""
    assert author_one(tab)
    assert tab.apply_creations() is True
    _result, provenance = built_creation(image, project)
    entry = provenance[0]
    # 0x0E's low nibble is 0xE and East authors ((3 + 1) << 4) = 0x40.
    assert entry.facing_raw == 0x4E
    assert entry.facing == FACING_EAST
    assert entry.prior_facing_raw == TEMPLATE_BYTE_0X10
    assert entry.prior_unresolved_raw == TEMPLATE_BYTE_0X13


# --- the staged row ----------------------------------------------------------


def test_a_staged_creation_appears_immediately_as_a_new_row(tab):
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    tab.stage_creation_region(*REGION)
    tab.stage_creation_destination(DESTINATION.index)
    tab.stage_creation_arrival(*ARRIVAL)
    tab.stage_creation_facing(FACING_EAST)
    assert tab.staged_creation_count() == 1
    # Two canonical rows (566 and 169), then the created one.
    assert tab.row_count() == 3
    assert tab.row_kind(2) == "created"
    row = tab.row_values(2)
    assert row[0] == NAME
    assert row[1] == "map:0001"
    assert row[2] == "first 232\u2013273 \u00b7 second 0\u201317"
    assert row[3] == "16, 24"
    assert row[4] == "East"
    assert row[5] == "New (staged)"
    # Distinguishable from the canonical rows, and free of addresses.
    assert tab.row_values(0)[5] == "Retail"
    assert tab.row_values(1)[5] == "Read-only"
    assert "0x" not in " ".join(row)
    assert "0x" not in tab._table.item(2, 0).toolTip()


def test_a_saved_creation_row_says_so(tab):
    assert author_one(tab)
    assert tab.apply_creations() is True
    assert tab.row_count() == 3
    assert tab.row_values(2)[5] == "New (saved)"
    assert tab.row_values(2)[0] == NAME
    assert tab.creation_row_keys() == (NEW_DOOR.key,)


def test_selecting_a_created_row_reopens_it_in_the_form(tab):
    assert author_one(tab)
    assert tab.apply_creations() is True
    tab.close_creation()
    assert tab.creation_open() is False
    assert tab.select_row(2) is True
    assert tab.creation_open() is True
    state = tab.creation_form_state()
    assert state["name"] == NAME
    assert state["identity"] == NEW_DOOR.key
    assert state["region"] == REGION
    assert state["destination"] == 1
    assert state["arrival"] == ARRIVAL
    assert state["facing"] == FACING_EAST
    # A saved identity's name is durable, so the field is fixed while its other
    # values stay authorable.
    assert state["name_editable"] is False


# --- apply / revert ----------------------------------------------------------


def test_apply_writes_only_the_creation_document(tab, project):
    """M3's regression: the creation is never written into transitions.toml."""
    assert author_one(tab)
    before = {
        path: path.read_bytes()
        for path in (project / TRANSITION_FILE, project / TRANSITION_CREATION_FILE)
        if path.exists()
    }
    assert before == {}
    assert tab.apply_creations() is True
    assert (project / TRANSITION_CREATION_FILE).is_file()
    assert not (project / TRANSITION_FILE).exists()
    text = (project / TRANSITION_CREATION_FILE).read_text(encoding="utf-8")
    assert f'[creation."map:0000".{NAME}]' in text
    assert 'template = "map:0000/transition:0000"' in text
    assert "0x" not in text
    for banned in ("offset", "address", "index", "record"):
        assert banned not in text
    assert mt.read_project_transition_requests(project) == {}
    assert set(mt.read_project_transition_creations(project)) == {NEW_DOOR}
    assert tab.staged_creation_count() == 0
    assert tab.unsaved_edit_count() == 0
    assert tab.undo_stack().count() == 0
    assert tab.row_values(2)[5] == "New (saved)"
    assert "maps/transition_creations.toml" in tab.status_line()


def test_apply_with_nothing_staged_writes_nothing(tab, project):
    assert tab.open_creation()
    assert tab.apply_creations() is False
    assert "no staged new transition" in tab.status_line()
    assert not (project / TRANSITION_CREATION_FILE).exists()


def test_apply_of_the_same_creation_twice_changes_no_file(tab, project):
    assert author_one(tab)
    assert tab.apply_creations() is True
    before = (project / TRANSITION_CREATION_FILE).read_bytes()
    # Re-authoring the values the project now holds asks for nothing at all.
    assert tab.stage_creation_facing(FACING_EAST) is False
    assert tab.staged_creation_count() == 0
    assert tab.apply_creations() is False
    assert (project / TRANSITION_CREATION_FILE).read_bytes() == before


def test_apply_reports_an_sdk_refusal_instead_of_a_dead_click(tab, project, image, monkeypatch):
    """A refused Apply reaches the user through the normal error surface."""
    shown: list[str] = []
    monkeypatch.setattr(
        wt.QMessageBox, "warning", staticmethod(lambda *a, **k: shown.append(a[2]))
    )
    assert author_one(tab)
    # An illegal entry injected past the form, which is the first gate.
    tab._staged_creations[
        mt.CreatedTransitionIdentity(MapIdentity(0), "bad-door")
    ] = mt.TransitionCreation(
        identity=mt.CreatedTransitionIdentity(MapIdentity(0), "bad-door"),
        template=TEMPLATE,
        destination=MapIdentity(9),
        region=TransitionRegion(first=(1, 2), second=(3, 4)),
        arrival=TransitionArrival(4, 4),
    )
    assert tab.apply_creations() is False
    assert shown and "map-entry range" in shown[0]
    assert tab.staged_creation_count() == 2
    assert not (project / TRANSITION_CREATION_FILE).exists()


def test_revert_discards_a_staged_creation_without_residue(tab, project):
    assert author_one(tab)
    assert tab.row_count() == 3
    assert tab.revert_creation() is True
    assert tab.staged_creation_count() == 0
    # The status line says what happened to the author's work, not just that the
    # form is back at some state.
    assert "Discarded the staged new transition" in tab.status_line()
    assert not (project / TRANSITION_CREATION_FILE).exists()
    assert not (project / TRANSITION_FILE).exists()
    assert tab.row_count() == 2
    # The gesture is itself undoable, and undo returns the exact authored values.
    assert tab.undo_stack().canUndo()
    tab.undo_stack().undo()
    assert tab.staged_creation_count() == 1
    assert tab.staged_creation(NEW_DOOR.key).arrival == TransitionArrival(*ARRIVAL)
    assert tab.row_values(2)[5] == "New (staged)"


def test_revert_of_a_saved_creation_returns_the_saved_values(tab):
    assert author_one(tab)
    assert tab.apply_creations() is True
    # Change a value, then revert: the form returns to what the project holds.
    assert tab.stage_creation_facing(FACING_NORTH) is True
    assert tab.creation_draft().facing == FACING_NORTH
    assert tab.revert_creation() is True
    assert tab.creation_draft().facing == FACING_EAST
    assert tab.staged_creation_count() == 0
    assert tab.saved_creation(NEW_DOOR.key).facing == FACING_EAST
    # ...and a revert with nothing staged to discard changes nothing.
    assert tab.revert_creation() is False
    assert "already states the last saved values" in tab.status_line()


def test_close_keeps_a_staged_creation_and_selecting_a_connection_closes_the_form(tab):
    assert author_one(tab)
    assert tab.close_creation() is True
    assert tab.creation_open() is False
    assert tab.staged_creation_count() == 1
    assert tab.open_creation() is True
    assert tab.creation_form_state()["identity"] is None
    assert tab.select_row(0) is True
    assert tab.creation_open() is False
    # A staged creation survived both moves.
    assert tab.staged_creation_count() == 1


def test_a_source_map_change_closes_the_form_and_keeps_the_staged_creation(tab):
    assert author_one(tab)
    assert tab.select_source_map(1) is True
    assert tab.creation_open() is False
    assert tab.staged_creation_count() == 1
    assert tab.staged_creation(NEW_DOOR.key) is not None
    # Back on map 0 the created row is still there, and reopening it works.
    assert tab.select_source_map(0) is True
    assert tab.row_values(2) == (
        NAME,
        "map:0001",
        "first 232\u2013273 \u00b7 second 0\u201317",
        "16, 24",
        "East",
        "New (staged)",
    )
    assert tab.select_row(2) is True
    assert tab.creation_form_state()["identity"] == NEW_DOOR.key


def test_undo_after_a_source_map_change_does_not_reopen_the_form(tab):
    """A creation belongs to one map, so a gesture cannot be undone onto another.

    The creation state rides the shared undo stack, and the map bar is a context
    switch: undoing a gesture while a different map is shown must leave the form
    closed and the staged creation staged, exactly as undoing an existing
    connection's edit does not select a row of the map that is no longer shown.

    The staged creation must then SURVIVE the transition that follows - an
    unrelated project mutation, which re-derives the form against what the project
    now holds. A form that is not installed must not be treated as a binding whose
    entry is to be dropped, or the author's staged work disappears with no message
    and no undo entry.
    """
    assert author_one(tab)
    assert tab.select_source_map(1) is True
    assert tab.creation_open() is False
    assert tab.undo_stack().canUndo() is True
    tab.undo_stack().undo()
    assert tab.creation_open() is False
    assert tab.source_map_index() == 1
    assert tab.staged_creation_count() == 1
    # The state the surface reports is coherent: no form, and a staged creation.
    state = tab.creation_form_state()
    assert state["open"] is False and state["staged"] is False
    assert tab.unsaved_edit_count() == 1

    tab.on_project_mutated()
    assert tab.staged_creation_count() == 1
    assert tab.creation_open() is False

    tab.undo_stack().redo()
    assert tab.creation_open() is False
    assert tab.staged_creation_count() == 1
    # The staged creation is intact on its own map, staged and applicable.
    assert tab.select_source_map(0) is True
    assert tab.row_values(2)[5] == "New (staged)"
    assert tab.apply_creations() is True
    assert tab.saved_creation(NEW_DOOR.key) is not None


def test_closing_the_form_leaves_no_row_highlighted(tab):
    """The pane and the list agree: nothing selected means nothing highlighted."""
    assert author_one(tab)
    assert tab.select_row(2) is True
    assert tab.creation_open() is True
    assert tab.close_creation() is True
    assert tab.creation_open() is False
    assert tab.selected_identity() is None
    assert tab._table.currentRow() == -1
    assert "Select a connection" in tab._identity.text()


def test_a_project_mutation_does_not_install_a_refused_form(tab, project, image):
    """A refusal must not become a staged creation because the project moved.

    A form whose name the project already creates is refused, and it is NOT bound to
    that identity. A mutation that inferred a binding from the draft's own identity
    would stage the refusal, enable Apply, and let one click overwrite the saved
    creation - a new value the author never asked to apply.
    """
    assert author_one(tab)
    assert tab.apply_creations() is True
    saved = tab.saved_creation(NEW_DOOR.key)

    assert tab.close_creation() is True
    assert tab.open_creation() is True
    tab.stage_creation_destination(3)
    tab.stage_creation_arrival(11, 22)
    tab.stage_creation_name(NAME)
    assert tab.staged_creation_count() == 0
    assert "durable" in (tab.creation_reason() or "")

    tab.on_project_mutated()
    assert tab.staged_creation_count() == 0
    assert "durable" in (tab.creation_reason() or "")
    assert tab.creation_form_state()["apply_enabled"] is False
    assert tab.apply_creations() is False
    after = tab.saved_creation(NEW_DOOR.key)
    assert after.destination == saved.destination
    assert after.arrival == saved.arrival
    assert after.region == saved.region


def test_a_project_mutation_does_not_replace_another_drafts_staged_creation(tab):
    """A second form may not take over an identity another draft already stages."""
    assert author_one(tab)
    staged = tab.staged_creation(NEW_DOOR.key)
    assert staged is not None

    assert tab.close_creation() is True
    assert tab.open_creation() is True
    tab.stage_creation_destination(3)
    tab.stage_creation_arrival(200, 200)
    tab.stage_creation_name(NAME)
    assert "already staged" in (tab.creation_reason() or "")
    assert tab.staged_creation(NEW_DOOR.key) == staged

    tab.on_project_mutated()
    assert tab.staged_creation_count() == 1
    assert tab.staged_creation(NEW_DOOR.key) == staged
    assert tab.row_values(2)[3] == "16, 24"


def test_a_project_mutation_keeps_a_bound_forms_staged_creation(tab, project, image):
    """The form that DOES own the staged entry keeps it across a mutation."""
    assert author_one(tab)
    staged = tab.staged_creation(NEW_DOOR.key)
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
    assert tab.staged_creation(NEW_DOOR.key) == staged
    assert tab.creation_open() is True
    assert tab.creation_form_state()["staged"] is True
    assert tab.creation_form_state()["state"] == "New (staged)"


def test_a_refused_creation_records_no_binding(tab):
    """A refusal must not make the form the owner of the identity it was refused for.

    The binding is what lets a later gesture treat this form as re-authoring an
    existing creation. Recording one on a refusal meant that - once the project came
    to create that name - one ordinary gesture staged an overwrite of the saved
    creation, with no conflict ever shown.
    """
    assert tab.open_creation() is True
    assert tab.stage_creation_name(NAME) is True
    # The seeded draft is byte-identical to its base, so the authority refuses it.
    assert "byte-identical" in (tab.creation_reason() or "")
    state = tab.creation_form_state()
    assert state["staged"] is False
    assert state["binding"] is None


def test_a_refusal_cannot_become_an_overwrite_of_a_saved_creation(tab, project, image):
    """The end-to-end hazard: refuse, the project gains the name, next gesture stages.

    Every assertion the earlier pin made still holds in the harmful state, which is
    why this one continues: after the project holds the identity, a corrective
    gesture must state the conflict and stage nothing, not turn the form into that
    identity's owner.
    """
    assert tab.open_creation() is True
    assert tab.stage_creation_name(NAME) is True
    assert "byte-identical" in (tab.creation_reason() or "")
    assert tab.creation_form_state()["binding"] is None

    # The project comes to create that identity: another tab's Apply, a Save As, or
    # a project opened over this session.
    assert mt.set_transition_creations(
        project,
        profile_for(image),
        image,
        {
            NEW_DOOR: mt.TransitionCreation(
                identity=NEW_DOOR,
                template=TEMPLATE,
                destination=DESTINATION,
                region=TransitionRegion(first=REGION[0], second=REGION[1]),
                arrival=TransitionArrival(*ARRIVAL),
                facing=FACING_EAST,
            )
        },
    ) is True
    tab.on_project_mutated()
    assert tab.staged_creation_count() == 0
    assert tab.creation_form_state()["binding"] is None

    # A corrective gesture must NOT stage an overwrite of the saved creation.
    tab.stage_creation_arrival(16, 24)
    assert tab.staged_creation_count() == 0
    assert "durable" in (tab.creation_reason() or "")
    assert tab.creation_form_state()["apply_enabled"] is False
    assert tab.apply_creations() is False
    saved = tab.saved_creation(NEW_DOOR.key)
    assert saved.destination == DESTINATION
    assert saved.arrival == TransitionArrival(*ARRIVAL)
    assert saved.facing == FACING_EAST


def test_a_saved_row_opened_into_the_form_keeps_its_binding(tab):
    """A form that LEARNED the binding keeps it, refusal or not.

    The rule is about provenance, not about refusals: a saved creation opened from
    its row owns that identity, so a value the authority refuses leaves it bound -
    and a corrected value then stages the update it was always authoring.
    """
    assert author_one(tab)
    assert tab.apply_creations() is True
    assert tab.close_creation() is True
    assert tab.select_row(2) is True
    assert tab.creation_form_state()["binding"] == NEW_DOOR.key

    tab.stage_creation_arrival(5000, 5000)  # off map:0001, the seeded destination
    assert "off the map" in (tab.creation_reason() or "")
    assert tab.creation_form_state()["binding"] == NEW_DOOR.key
    assert tab.staged_creation_count() == 0

    tab.stage_creation_arrival(60, 70)
    assert tab.staged_creation_count() == 1
    assert tab.creation_reason() is None
    assert tab.apply_creations() is True
    assert tab.saved_creation(NEW_DOOR.key).arrival == TransitionArrival(60, 70)


@pytest.fixture
def quiet_dialogs(monkeypatch):
    """A refused Apply raises a warning dialog; the tests record it instead."""
    shown: list[str] = []
    monkeypatch.setattr(
        wt.QMessageBox, "warning", staticmethod(lambda *a, **k: shown.append(a[2]))
    )
    return shown


def project_creation(*, arrival=ARRIVAL, destination=None, facing=FACING_EAST):
    """A creation the PROJECT holds, for the conflict shapes."""
    return mt.TransitionCreation(
        identity=NEW_DOOR,
        template=TEMPLATE,
        destination=destination if destination is not None else MapIdentity(2),
        region=TransitionRegion(first=(1, 2), second=(3, 4)),
        arrival=TransitionArrival(*arrival),
        facing=facing,
    )


def the_project_gains(project, image, *, arrival=ARRIVAL):
    """The project comes to create NEW_DOOR itself: a peer Apply, a Save As, a CLI."""
    request = project_creation(arrival=arrival)
    assert mt.set_transition_creations(
        project, profile_for(image), image, {NEW_DOOR: request}
    ) is True
    return request


def stored_in(project, identity=NEW_DOOR):
    """What the project's own DOCUMENT holds: the surface's cache may be stale."""
    authored = mt.read_project_transition_creations(project).get(identity)
    return None if authored is None else authored.creation


def test_a_closed_form_cannot_write_a_staged_creation_the_project_now_holds(
    tab, project, image, quiet_dialogs
):
    """CLOSED FORM: the write boundary must refuse a stale staged creation.

    A form that is not open cannot own anything, so a staged creation it left behind
    is refused if the project has come to hold that identity - even when no
    broadcast has reached this tab, because the boundary reads the project's own
    document rather than trusting cached state.
    """
    assert author_one(tab)
    assert tab.close_creation() is True
    held = the_project_gains(project, image, arrival=(11, 12))
    # No on_project_mutated(): the staged entry is stale and the surface cannot know.
    assert tab.apply_creations() is False
    assert quiet_dialogs and "already a transition this project creates" in quiet_dialogs[0]
    stored = stored_in(project)
    assert stored is not None and stored.arrival == held.arrival
    assert stored.destination == held.destination
    assert stored.region == held.region


def test_a_project_mutation_conflict_is_refused_and_writes_nothing(
    tab, project, image, quiet_dialogs
):
    """A broadcast plus Apply must refuse too, and write nothing at all."""
    assert author_one(tab)
    assert tab.close_creation() is True
    held = the_project_gains(project, image, arrival=(11, 12))
    tab.on_project_mutated()
    assert tab.apply_creations() is False
    assert quiet_dialogs
    assert stored_in(project).arrival == held.arrival
    text = (project / TRANSITION_CREATION_FILE).read_text(encoding="utf-8")
    assert "arrival = [11, 12]" in text


def test_an_undone_stale_binding_cannot_write_over_the_project_creation(
    tab, project, image, quiet_dialogs
):
    """UNDO: reinstating a captured staged state must not reopen the write."""
    assert author_one(tab)
    held = the_project_gains(project, image, arrival=(11, 12))
    tab.on_project_mutated()
    assert tab.staged_creation_count() == 0
    tab.undo_stack().undo()
    assert tab.staged_creation_count() == 1
    assert tab.creation_form_state()["owned"] is False
    assert tab.apply_creations() is False
    assert quiet_dialogs
    assert tab.saved_creation(NEW_DOOR.key).arrival == held.arrival


def test_clicking_a_staged_row_does_not_claim_the_project_entry(tab, project, image):
    """STAGED ROW: ownership follows the source of the values, not the click."""
    assert author_one(tab)
    assert tab.close_creation() is True
    assert tab.select_row(2) is True
    # The row's values are the author's STAGED creation, not the project's entry.
    assert tab.creation_form_state()["owned"] is False
    assert tab.creation_form_state()["binding"] == NEW_DOOR.key
    # The project then comes to create the name, with different values.
    held = the_project_gains(project, image, arrival=(11, 12))
    tab.on_project_mutated()
    assert tab.creation_form_state()["owned"] is False
    assert tab.apply_creations() is False
    assert tab.saved_creation(NEW_DOOR.key).arrival == held.arrival


def test_cqa06_a_shadowed_row_cannot_write_over_the_project_creation(
    tab, project, image, quiet_dialogs
):
    """THE EXACT ORDER: author, stage, close, the project gains it, click the row.

    This is the order that produced the last ownership defect. Once the project
    comes to create the SAME identity the author staged - with different values -
    the row this tab lists is SHADOWED: its values come from the staged set, so the
    form is not editing the project's entry and must claim no ownership of it.
    Clicking that row must not adopt the project's creation, Apply must refuse, no
    file may be written, the project's own authored values must be exactly what they
    were, and the author's staged creation must still be there: stale, not destroyed.
    """
    assert author_one(tab)
    assert tab.close_creation() is True
    held = the_project_gains(project, image, arrival=(11, 12))
    tab.on_project_mutated()
    assert tab.staged_creation_count() == 1

    # The row still shows the STAGED creation, not the project's: the mutation did
    # not quietly adopt the project's entry as the values this form is editing.
    assert tab.select_row(2) is True
    state = tab.creation_form_state()
    assert state["arrival"] == ARRIVAL
    assert state["destination"] == DESTINATION.index
    assert state["owned"] is False
    # The refused form stages nothing of its own, but the author's staged creation
    # is still in the set: it is this row's source, and a form that was never given
    # it may not remove it. It is discarded only by the form that staged it, by a
    # successful Apply, or by the session boundary the end of this test exercises.
    assert state["staged"] is False
    assert state["binding"] is None
    assert tab.staged_creation_count() == 1
    assert "already a transition this project creates" in (state["reason"] or "")

    # The write boundary refuses, states why, and writes NOTHING: the project's
    # document is byte-for-byte what the project itself wrote.
    before = (project / TRANSITION_CREATION_FILE).read_bytes()
    assert tab.apply_creations() is False
    assert quiet_dialogs and "does not own it" in quiet_dialogs[0]
    assert (project / TRANSITION_CREATION_FILE).read_bytes() == before
    stored = stored_in(project)
    assert stored is not None and stored.arrival == held.arrival
    assert stored.destination == held.destination
    assert stored.region == held.region

    # ...and the author's staged creation survived the refusal: it is stale, not
    # lost. Staged work is scoped to the session, so the session boundary is the
    # exit from this conflict - and the project's creation is untouched by it.
    staged = tab.staged_creation(NEW_DOOR.key)
    assert staged is not None and staged.arrival == TransitionArrival(*ARRIVAL)
    tab.on_session_changed()
    assert tab.staged_creation_count() == 0
    assert stored_in(project).arrival == held.arrival


def test_a_conflicting_batch_is_refused_atomically(tab, project, image, quiet_dialogs):
    """ONE conflicting member refuses the WHOLE batch: nothing is written."""
    second = mt.CreatedTransitionIdentity(MapIdentity(0), "second-door")
    assert author_one(tab)
    assert tab._staged_creations.get(NEW_DOOR) is not None
    # A second, perfectly valid staged creation alongside the one that will conflict.
    other = project_creation(arrival=(21, 22))
    other = mt.TransitionCreation(
        identity=second,
        template=TEMPLATE,
        destination=MapIdentity(3),
        region=TransitionRegion(first=(5, 6), second=(7, 8)),
        arrival=TransitionArrival(21, 22),
        facing=None,
    )
    tab._staged_creations[second] = other
    assert tab.staged_creation_count() == 2

    held = the_project_gains(project, image, arrival=(11, 12))
    assert tab.apply_creations() is False
    assert quiet_dialogs
    # Neither member was written, and the project's own values are untouched.
    assert stored_in(project).arrival == held.arrival
    assert stored_in(project, second) is None
    text = (project / TRANSITION_CREATION_FILE).read_text(encoding="utf-8")
    assert "second-door" not in text
    assert tab.staged_creation_count() == 2


def test_an_unreadable_project_document_fails_closed_and_writes_nothing(
    tab, project, image, quiet_dialogs, monkeypatch
):
    """AMBIGUOUS OWNERSHIP: a document this surface cannot read is not permission.

    The write boundary re-reads the project's own created transitions instead of
    trusting the last broadcast. When that read FAILS, falling back to the cached
    copy would turn "this surface does not know what the project holds" into "the
    project holds nothing" - exactly the state that permits an overwrite of authored
    data. So the whole Apply fails closed, states why, and writes no file.
    """
    assert author_one(tab)
    assert not (project / TRANSITION_CREATION_FILE).exists()

    def unreadable(_project):
        raise mt.MapTransitionsError("the created transitions document is damaged")

    monkeypatch.setattr(mt, "read_project_transition_creations", unreadable)
    assert tab.apply_creations() is False
    assert quiet_dialogs and "could not be read" in quiet_dialogs[0]
    # Nothing was written, and the author's staged creation is untouched.
    assert not (project / TRANSITION_CREATION_FILE).exists()
    assert tab.staged_creation_count() == 1
    assert tab.staged_creation(NEW_DOOR.key) is not None


def test_ownership_clears_when_the_binding_goes(tab, project, monkeypatch):
    """No stale ``owned`` may survive the binding it describes."""
    assert author_one(tab)
    assert tab.apply_creations() is True
    assert tab.close_creation() is True
    assert tab.select_row(2) is True
    assert tab.creation_form_state()["owned"] is True  # the project's own entry
    assert tab.close_creation() is True
    state = tab.creation_form_state()
    assert state["binding"] is None and state["owned"] is False
    # Selecting a canonical row clears both, and so does a source-map change.
    assert tab.select_row(2) is True
    assert tab.creation_form_state()["owned"] is True
    assert tab.select_row(0) is True
    state = tab.creation_form_state()
    assert state["binding"] is None and state["owned"] is False
    assert tab.select_row(2) is True
    assert tab.select_source_map(1) is True
    state = tab.creation_form_state()
    assert state["binding"] is None and state["owned"] is False
    # The sixth reset site: a REFUSED Create action is a reset too. The refusal
    # itself is forced here - the six real ones are covered one by one elsewhere -
    # because what this pins is the reset behind it: a form that used to own a
    # saved creation must not leave that authority behind for the next form.
    assert tab.select_source_map(0) is True
    assert tab.select_row(2) is True
    assert tab.creation_form_state()["owned"] is True
    monkeypatch.setattr(tab, "creation_refusal", lambda: "no 566-class base here")
    assert tab.open_creation() is False
    state = tab.creation_form_state()
    assert state["binding"] is None and state["owned"] is False


def test_staging_a_name_does_not_claim_a_creation_the_project_later_gains(
    tab, project, image
):
    """Staging a name is not the same as being given the project's entry for it.

    The saved-identity gate needs both halves: the binding must be this identity AND
    it must have come from the project - a saved row opened into this form, or this
    form's Apply. A form that merely STAGED the name has not been given the project's
    entry, so when the project comes to create that name (a peer Apply, a Save As, a
    project opened over this session) its next gesture must state the conflict
    instead of staging an overwrite of authored data.
    """
    assert author_one(tab)
    staged = tab.staged_creation(NEW_DOOR.key)
    assert staged is not None
    assert tab.creation_form_state()["binding"] == NEW_DOOR.key

    # The project gains that identity with DIFFERENT values.
    other = mt.TransitionCreation(
        identity=NEW_DOOR,
        template=TEMPLATE,
        destination=MapIdentity(2),
        region=TransitionRegion(first=(1, 2), second=(3, 4)),
        arrival=TransitionArrival(11, 12),
        facing=None,
    )
    assert mt.set_transition_creations(
        project, profile_for(image), image, {NEW_DOOR: other}
    ) is True
    tab.on_project_mutated()
    assert tab.saved_creation(NEW_DOOR.key).arrival == TransitionArrival(11, 12)

    # One ordinary gesture must state the conflict, not stage an overwrite.
    tab.stage_creation_arrival(60, 70)
    assert tab.staged_creation_count() == 0
    assert "durable" in (tab.creation_reason() or "")
    assert tab.creation_form_state()["apply_enabled"] is False
    assert tab.apply_creations() is False
    stored = tab.saved_creation(NEW_DOOR.key)
    assert stored.arrival == TransitionArrival(11, 12)
    assert stored.destination == MapIdentity(2)
    assert stored.region == TransitionRegion(first=(1, 2), second=(3, 4))


def test_the_project_s_own_entry_may_still_be_re_authored(tab, project, image):
    """The other half of the rule: a form GIVEN the project's entry may update it."""
    assert author_one(tab)
    assert tab.apply_creations() is True
    assert tab.close_creation() is True
    assert tab.select_row(2) is True
    assert tab.creation_form_state()["binding"] == NEW_DOOR.key
    # Opened from the project's own row, so a value change is an update, not a claim.
    tab.stage_creation_arrival(60, 70)
    assert tab.staged_creation_count() == 1
    assert tab.creation_reason() is None
    assert tab.apply_creations() is True
    assert tab.saved_creation(NEW_DOOR.key).arrival == TransitionArrival(60, 70)


def test_a_closed_form_reports_no_stale_state(tab):
    """The chip states the FORM's condition whether or not a form is open.

    A closed form that kept the last "New (staged)" would report a state the form
    does not have - to a probe, a capture, or the next reader of the record. What is
    staged is still staged, and Apply still writes it: closing a form is not a
    gesture, so the row and the enabled Apply are the other half of the same fact.
    """
    assert author_one(tab)
    assert tab.creation_form_state()["state"] == "New (staged)"
    assert tab.close_creation() is True
    state = tab.creation_form_state()
    assert state["open"] is False
    assert state["staged"] is False
    assert state["binding"] is None
    assert state["state"] == "Not staged"
    # The staged set is untouched by closing, so the row and Apply still say so.
    assert tab.staged_creation_count() == 1
    assert state["apply_enabled"] is True
    assert tab.row_values(2)[5] == "New (staged)"
    assert tab.apply_creations() is True


def test_a_retail_read_of_an_identity_the_corpus_lacks_is_state_not_an_exception(tab):
    """The install path is callable from undo()/redo(), so it must not raise.

    `_retail` is reached through `_install_creation_state` -> `_populate_rows` ->
    `_fill_row` -> `_effective` -> `_base`, and every corpus call on that path is
    guarded, so a record the corpus does not hold reads as the on-screen state
    ("unresolved", "not stated") instead of an exception unwinding through Qt's
    undo stack.
    """
    created = mt.CreatedTransitionIdentity(MapIdentity(0), NAME)
    assert tab._retail(created) == (None, None, None)
    assert tab._base(created) == (None, None, None)
    assert tab._effective(created) == (None, None, None)
    assert tab._refusal_for(created) is not None


# --- undo / redo -------------------------------------------------------------


def test_undo_and_redo_return_each_creation_gesture_exactly(tab):
    assert tab.open_creation()
    assert tab.stage_creation_name(NAME) is True
    assert tab.undo_stack().count() == 1
    assert tab.stage_creation_region(*REGION) is True
    # A destination OTHER than the seeded one, so the gesture authors a value.
    assert tab.stage_creation_destination(3) is True
    assert tab.stage_creation_arrival(*ARRIVAL) is True
    assert tab.stage_creation_facing(FACING_EAST) is True
    assert tab.undo_stack().count() == 5

    # Undo the facing, then the arrival, then the destination, then the region.
    tab.undo_stack().undo()
    assert tab.creation_draft().facing is None
    tab.undo_stack().undo()
    assert tab.creation_draft().arrival == (TEMPLATE_ARRIVAL.x, TEMPLATE_ARRIVAL.y)
    tab.undo_stack().undo()
    assert tab.creation_draft().destination == DESTINATION
    tab.undo_stack().undo()
    assert tab.creation_draft().region == (TEMPLATE_REGION.first, TEMPLATE_REGION.second)
    # The name is the first gesture, so undoing it empties the identity.
    tab.undo_stack().undo()
    assert tab.creation_draft().name == ""
    assert tab.creation_identity() is None
    assert tab.staged_creation_count() == 0
    assert not tab.undo_stack().canUndo()

    # Redo returns every authored value, in order and exactly.
    for _ in range(5):
        tab.undo_stack().redo()
    draft = tab.creation_draft()
    assert draft.name == NAME
    assert draft.region == REGION
    assert draft.destination == MapIdentity(3)
    assert draft.arrival == ARRIVAL
    assert draft.facing == FACING_EAST
    assert tab.creation_form_state()["staged"] is True


def test_undo_of_a_rename_puts_the_previous_identity_back(tab):
    """Staging is derived from the form, so a rename leaves no entry behind."""
    assert tab.open_creation()
    tab.stage_creation_name("first-door")
    tab.stage_creation_region(*REGION)
    tab.stage_creation_destination(DESTINATION.index)
    tab.stage_creation_arrival(*ARRIVAL)
    assert tab.staged_creation_count() == 1
    first = mt.CreatedTransitionIdentity(MapIdentity(0), "first-door")
    assert first.key in [key.key for key in tab._staged_creations]

    assert tab.stage_creation_name("second-door") is True
    second = mt.CreatedTransitionIdentity(MapIdentity(0), "second-door")
    assert [key.key for key in tab._staged_creations] == [second.key]
    tab.undo_stack().undo()
    assert [key.key for key in tab._staged_creations] == [first.key]
    assert tab.creation_identity() == first.key
    tab.undo_stack().redo()
    assert [key.key for key in tab._staged_creations] == [second.key]


def test_a_no_op_creation_gesture_enters_no_history(tab):
    assert tab.open_creation()
    tab.stage_creation_name(NAME)
    tab.stage_creation_region(*REGION)
    count = tab.undo_stack().count()
    # The same base, the same name and the same region change nothing.
    tab.stage_creation_template(TEMPLATE)
    tab.stage_creation_name(NAME)
    tab.stage_creation_region(*REGION)
    assert tab.undo_stack().count() == count
    assert "already holds these values" in tab.status_line()


# --- CQA-05 ------------------------------------------------------------------


def test_a_project_mutation_keeps_the_staged_creation(tab, project, image):
    """M4's regression: an unrelated project mutation must not discard staging."""
    assert author_one(tab)
    staged = tab.staged_creation(NEW_DOOR.key)
    history = tab.undo_stack().count()
    mt.set_transition_edits(
        project,
        profile_for(image),
        image,
        {
            mt.TransitionIdentity(MapIdentity(0), 0): mt.TransitionEdit(
                destination=MapIdentity(3)
            )
        },
    )
    tab.on_project_mutated()
    assert tab.staged_creation(NEW_DOOR.key) == staged
    assert tab.undo_stack().count() == history
    assert tab.staged_creation_count() == 1
    # The open form still states exactly the staged creation, field for field.
    assert tab.creation_open() is True
    assert tab.creation_draft() == wt._draft_from_creation(staged)
    # The unrelated edit is visible as saved work beside the staged creation.
    assert tab.row_values(0)[5] == "Saved"
    assert tab.row_values(2)[5] == "New (staged)"


def test_a_project_mutation_keeps_a_staged_creation_whose_form_is_closed(
    tab, project, image
):
    """The staged set is durable on its own, not a side effect of an open form.

    With the form closed there is nothing to re-derive from, so a mutation that
    discarded the staged entry - or rebuilt the surface from the project - would
    lose work the author had already staged.
    """
    assert author_one(tab)
    staged = tab.staged_creation(NEW_DOOR.key)
    assert tab.close_creation() is True
    assert tab.creation_open() is False
    history = tab.undo_stack().count()
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
    assert tab.staged_creation_count() == 1
    assert tab.staged_creation(NEW_DOOR.key) == staged
    assert tab.undo_stack().count() == history
    assert tab.creation_open() is False
    assert tab.row_values(2)[5] == "New (staged)"
    assert tab.select_row(2) is True
    assert tab.creation_draft() == wt._draft_from_creation(staged)


def test_a_session_replacement_resets_the_creation_state(tab, project):
    assert author_one(tab)
    assert tab.staged_creation_count() == 1
    tab.on_session_changed()
    assert tab.staged_creation_count() == 0
    assert tab.creation_open() is False
    assert tab.creation_draft() is None
    assert tab.undo_stack().count() == 0
    assert tab.row_count() == 2
    assert "New (staged)" not in " ".join(tab.row_values(0) + tab.row_values(1))


# --- CQA-06 ------------------------------------------------------------------


def test_cqa06_every_expected_failure_reaches_the_surface(tab):
    """One place, so the list of refusals the surface must state is readable.

    Each refusal is the authority's own, stated on the form beside the field that
    caused it, and none of them writes anything.
    """
    assert tab.open_creation()
    # an invalid authored name
    tab.stage_creation_name("Door")
    assert "lowercase" in (tab.creation_reason() or "")
    assert tab.creation_identity() is None
    # a valid name and region, so the later refusals are not masked by a gap
    tab.stage_creation_name(NAME)
    tab.stage_creation_region(*REGION)
    assert tab.creation_reason() is None and tab.staged_creation_count() == 1
    # an invalid trigger region
    tab.stage_creation_region((10, 10), (0, 4))
    assert "degenerate" in (tab.creation_reason() or "")
    tab.stage_creation_region(*REGION)
    # an invalid destination
    tab.stage_creation_destination(9)
    assert "declared map-entry range" in (tab.creation_reason() or "")
    # an invalid arrival
    tab.stage_creation_destination(3)
    tab.stage_creation_arrival(700, 700)
    assert "off the map" in (tab.creation_reason() or "")
    # an invalid facing
    tab.stage_creation_arrival(10, 10)
    tab.stage_creation_facing(9)
    assert "facing" in (tab.creation_reason() or "")
    # a 169-class base
    tab.stage_creation_facing(FACING_EAST)
    tab.stage_creation_template(SCENE_RELATIVE)
    assert "scene-relative delta" in (tab.creation_reason() or "")
    # a base whose class is fine but whose map is not
    tab.stage_creation_template(mt.TransitionIdentity(MapIdentity(1), 0))
    assert "same source map" in (tab.creation_reason() or "")
    # the last refusal unstaged the creation, and nothing was ever written
    assert tab.staged_creation_count() == 0
    assert not (tab._session.project_dir / TRANSITION_CREATION_FILE).exists()
    assert not (tab._session.project_dir / TRANSITION_FILE).exists()


def test_cqa06_a_programmer_error_in_a_slot_is_loud(tab, monkeypatch):
    """The command slots catch the SDK families, never bare `Exception`.

    The failure is raised where the authority is consulted - BEFORE the gesture
    enters the undo history - so it is loud, and it leaves no half-applied command
    inside Qt's undo stack.
    """
    def boom(*_a, **_k):
        raise RuntimeError("a bug, not a refusal")

    monkeypatch.setattr(mt, "check_transition_creation", boom)
    assert tab.open_creation()
    with pytest.raises(RuntimeError):
        tab.stage_creation_name(NAME)
    assert tab.undo_stack().count() == 0
    assert tab.creation_draft().name == ""
    assert tab.staged_creation_count() == 0


# --- CQA-07 ------------------------------------------------------------------


@pytest.fixture
def reads(monkeypatch):
    """Count the whole-image and whole-project reads, and the creation writes."""
    import tools.webfoot.project as project_module

    counts = {"corpus": 0, "project": 0, "labels": 0, "checks": 0, "writes": 0}
    real_corpus = mt.read_map_transitions
    real_project = project_module.read_project
    real_labels = mv.read_map_index
    real_check = mt.check_transition_creation
    real_writes = mt.set_transition_creations

    def corpus(*a, **k):
        counts["corpus"] += 1
        return real_corpus(*a, **k)

    def project(*a, **k):
        counts["project"] += 1
        return real_project(*a, **k)

    def labels(*a, **k):
        counts["labels"] += 1
        return real_labels(*a, **k)

    def check(*a, **k):
        counts["checks"] += 1
        return real_check(*a, **k)

    def writes(*a, **k):
        counts["writes"] += 1
        return real_writes(*a, **k)

    monkeypatch.setattr(mt, "read_map_transitions", corpus)
    monkeypatch.setattr(project_module, "read_project", project)
    monkeypatch.setattr(mv, "read_map_index", labels)
    monkeypatch.setattr(mt, "check_transition_creation", check)
    monkeypatch.setattr(mt, "set_transition_creations", writes)
    return counts


def test_opening_the_creation_form_reads_nothing(tab, reads):
    for key in reads:
        reads[key] = 0
    assert tab.open_creation() is True
    assert tab.stage_creation_name(NAME) is True
    assert tab.stage_creation_region(*REGION) is True
    assert tab.stage_creation_destination(3) is True
    assert tab.stage_creation_arrival(*ARRIVAL) is True
    assert tab.stage_creation_facing(FACING_EAST) is True
    tab.undo_stack().undo()
    tab.undo_stack().redo()
    tab.select_source_map(1)
    tab.select_source_map(0)
    tab.close_creation()
    # Every gesture is checked against the corpus already in memory, so NOTHING is
    # re-read: not the image, not the project, not the map labels. `checks` counts
    # the authority calls - one per authored gesture, and none at all for the undo
    # or the redo, which install the states the gestures already resolved.
    assert reads == {
        "corpus": 0,
        "project": 0,
        "labels": 0,
        "checks": 5,
        "writes": 0,
    }


def test_one_creation_apply_is_one_write_and_one_reproject_read(tab, reads):
    assert author_one(tab)
    for key in reads:
        reads[key] = 0
    assert tab.apply_creations() is True
    # Exact counts, not a bound: the authority reads the canonical corpus once, the
    # surface reads the project's own document once at the write boundary so the
    # ownership gate is authoritative rather than trusting cached state, and the
    # authority parses the project once itself; the surface then re-reads it to show
    # what was just written. Nothing grows with the number of controls, rows or
    # staged creations.
    assert reads == {
        "corpus": 1,
        "project": 3,
        "labels": 0,
        "checks": 0,
        "writes": 1,
    }


def test_reopening_the_surface_reads_each_domain_once(qapp, reads, image, project):
    WarpTab(session_for(image, project, selected_map="map:0000"))
    assert reads == {
        "corpus": 1,
        "project": 1,
        "labels": 1,
        "checks": 0,
        "writes": 0,
    }


def test_the_form_state_agrees_with_the_row_beside_it(tab, project):
    """The visual-QA pass found the chip and the row disagreeing; these pin them.

    Four defects the captures showed, each now a named expectation:
    an applied creation read "Not staged" while its row read "New (saved)"; a form
    that collided with a saved name locked the very field its refusal told the
    author to change; a refused Create action stated its reason only in the
    one-line status bar; and Revert was offered with nothing to revert.
    """
    # A fresh form offers nothing to revert, and says so by being disabled.
    assert tab.open_creation() is True
    assert tab._create_revert_button.isEnabled() is False
    assert tab.creation_form_state()["state"] == "Not staged"

    assert author_one(tab)
    assert tab.creation_form_state()["state"] == "New (staged)"
    assert tab.apply_creations() is True
    # The chip now uses the same words as the row beside it.
    assert tab.creation_form_state()["state"] == "New (saved)"
    assert tab.row_values(2)[5] == "New (saved)"
    assert tab._create_revert_button.isEnabled() is False
    # A saved creation's identity is durable, so its name is fixed...
    assert tab.creation_form_state()["name_editable"] is False

    # ...but a NEW form that merely collides with that name stays editable: its
    # refusal tells the author to author a different one.
    assert tab.close_creation() is True
    assert tab.open_creation() is True
    tab.stage_creation_name(NAME)
    assert tab.creation_reason() is not None and "durable" in tab.creation_reason()
    assert tab.creation_form_state()["name_editable"] is True
    assert tab._creation_name.isEnabled() is True


def test_a_refused_create_action_states_its_reason_in_the_pane(tab):
    """The status bar elides a long refusal; the line the button lives on must not."""
    assert tab.select_source_map(2) is True
    assert tab.open_creation() is False
    assert tab.creation_open() is False
    assert "566-class" in tab._map_support.text()
    assert "566-class" in tab.status_line()
    # A different map has its own answer, so the old refusal does not follow it.
    assert tab.select_source_map(0) is True
    assert "566-class" not in tab._map_support.text()
    assert "566-class" not in tab.status_line()


# --- save / reopen -----------------------------------------------------------


def test_save_and_reopen_reproduces_the_created_transition(qapp, image, project):
    """M6's regression: the authored identity and every value survive a reopen."""
    first = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert author_one(first)
    assert first.apply_creations() is True
    assert first.staged_creation_count() == 0

    # Close and reopen: a fresh session, the same project, a fresh surface.
    reopened = read_project(project)
    assert not reopened.transition_creations.is_empty()
    second = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert second.row_count() == 3
    assert second.row_values(2) == (
        NAME,
        "map:0001",
        "first 232\u2013273 \u00b7 second 0\u201317",
        "16, 24",
        "East",
        "New (saved)",
    )
    assert second.creation_row_keys() == (NEW_DOOR.key,)
    state = second.creation_form_state()
    assert state["identity"] is None  # the form is closed until a row is selected
    assert second.select_row(2) is True
    state = second.creation_form_state()
    assert state["identity"] == NEW_DOOR.key
    assert state["template"] == str(TEMPLATE)
    assert state["region"] == REGION
    assert state["destination"] == 1
    assert state["arrival"] == ARRIVAL
    assert state["facing"] == FACING_EAST

    # And the production build materializes exactly that record.
    _result, provenance = built_creation(image, project)
    assert len(provenance) == 1
    entry = provenance[0]
    assert entry.identity == NEW_DOOR.key
    assert entry.template == str(TEMPLATE)
    assert entry.region == REGION
    assert entry.arrival == ARRIVAL
    assert entry.destination == str(DESTINATION)
    assert entry.facing == FACING_EAST
    assert entry.facing_raw == 0x4E
    assert entry.prior_facing_raw == TEMPLATE_BYTE_0X10
    assert entry.prior_unresolved_raw == TEMPLATE_BYTE_0X13


def test_the_materialized_creation_is_the_record_the_author_stated(image, project, qapp):
    """The end of the flow: the composed record carries the authored values."""
    tab = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert author_one(tab)
    assert tab.apply_creations() is True
    result, _provenance = built_creation(image, project)
    from tools.webfoot.write import apply_plan, plan_changes

    profile = profile_for(image)
    plan = plan_changes(
        image,
        result.changes,
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
        generated_image=result.generated_image,
        generated_allocations=result.generated_allocations,
        transition_creations=result.provenance,
    )
    built = apply_plan(image, plan)
    corpus = mt.read_map_transitions(built, profile)
    created = corpus.entry(mt.TransitionIdentity(MapIdentity(0), 2)).record
    assert created.class_raw == CREATED_CLASS_RAW
    assert created.region == TransitionRegion(first=REGION[0], second=REGION[1])
    assert created.destination_key == key_for(DESTINATION.index)
    assert created.arrival == TransitionArrival(*ARRIVAL)
    assert created.facing.arrival_direction == FACING_EAST
    assert created.facing.gate_direction == TEMPLATE_BYTE_0X10 & 0x03
    assert created.byte_0x13_raw == TEMPLATE_BYTE_0X13
    # Every canonical record is untouched.
    before = mt.read_map_transitions(image, profile)
    for entry in before.entries():
        assert corpus.entry(entry.identity).record == entry.record


def test_the_draft_helpers_round_trip_a_creation():
    """The form's value type is the authority's types, not a parallel model."""
    creation = mt.TransitionCreation(
        identity=NEW_DOOR,
        template=TEMPLATE,
        destination=DESTINATION,
        region=TransitionRegion(first=REGION[0], second=REGION[1]),
        arrival=TransitionArrival(*ARRIVAL),
        facing=FACING_EAST,
    )
    draft = wt._draft_from_creation(creation)
    assert isinstance(draft, CreationDraft)
    assert draft.source == MapIdentity(0)
    assert draft.identity() == NEW_DOOR
    assert draft.region == REGION
    assert draft.arrival == ARRIVAL
    assert draft.replaced(name="other").name == "other"
    assert draft.replaced(name="other").identity().key == "map:0000/transition:other"


def test_a_malformed_creation_document_is_reported(qapp, image, project):
    """A malformed maps/transition_creations.toml is stated, not raised at the user."""
    (project / "maps").mkdir(parents=True, exist_ok=True)
    (project / TRANSITION_CREATION_FILE).write_text(
        "[creation]\n", encoding="utf-8", newline="\n"
    )
    tab = WarpTab(session_for(image, project, selected_map="map:0000"))
    assert "could not be read" in tab.status_line()
    refusal = tab.creation_refusal()
    assert refusal is not None and "could not be read" in refusal
    assert tab.open_creation() is False
