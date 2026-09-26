"""Portable tests for the transition arrival and facing semantics.

MAP-WARP-ARRIVAL-SEMANTICS-001. Synthetic and codec-level only: these pin what the
two record classes mean, how the arrival sentinel differs from the origin, how the
facing byte splits into a candidate direction and unresolved flag bits, and the
project document's prior/authored rules for both fields.

What needs the real image - deriving an arrival from a destination's return door,
the walkable-extent bounds check, and the default-facing heuristic over a real
map - lives in ``tests/integration/test_map_arrival_semantics_rom.py``.
"""

from __future__ import annotations

import pytest

from tests.unit.test_map_transition_project import (
    PEER,
    image_bytes,
    profile_for,
    project_at,
)

from tools.webfoot.formats.map_transitions import (
    ARRIVAL_UNSET_MINIMUM,
    FACING_EAST,
    FACING_MASK,
    FACING_NAMES,
    FACING_NORTH,
    FACING_SOUTH,
    FACING_WEST,
    TRANSITION_CLASS_A_RAW,
    TRANSITION_CLASS_B_RAW,
    MapTransitionValueError,
    TransitionArrival,
    TransitionRecord,
)
from tools.webfoot.map_transitions import (
    TransitionEdit,
    TransitionFieldError,
    read_transition_edits,
    set_transition_edits,
)
from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    AuthoredTransition,
    ProjectMeta,
    ProjectValidationError,
    TransitionEdits,
    read_project,
    write_project,
)

META = ProjectMeta(
    format_version=PROJECT_FORMAT_VERSION,
    profile_id="synthetic_arrival",
    game="synthetic",
    base_rom_sha256="0" * 64,
    base_rom_size=0x8000,
    name="synthetic",
)


def record(
    *,
    class_raw: int = TRANSITION_CLASS_A_RAW,
    first: tuple[int, int] = (10, 20),
    second: tuple[int, int] = (30, 40),
    arrival: tuple[int, int] = (100, 200),
    facing: int = 0,
) -> TransitionRecord:
    """One record with the fields these tests care about under control."""
    return TransitionRecord(
        class_raw=class_raw,
        constant_raw=0x0800776D,
        bound_a_raw=first[0],
        bound_b_raw=second[0],
        bound_c_raw=first[1],
        bound_d_raw=second[1],
        byte_0x10_raw=facing,
        destination_key_high=0x01,
        destination_key_low=0x0B,
        byte_0x13_raw=0,
        word_0x14_raw=arrival[0],
        byte_0x16_raw=arrival[1] & 0xFF,
        byte_0x17_raw=(arrival[1] >> 8) & 0xFF,
    )


# --- the arrival, and the class split ----------------------------------------


def test_the_566_class_pair_is_the_arrival_as_stored() -> None:
    """The 566 class hands record+0x14 to the warp routine itself."""
    item = record(class_raw=TRANSITION_CLASS_A_RAW, arrival=(599, 196))
    assert item.has_raw_arrival_pair
    assert item.arrival == TransitionArrival(x=599, y=196)
    # y spans both bytes: +0x16 low, +0x17 high.
    assert item.byte_0x16_raw == 196 & 0xFF
    assert item.byte_0x17_raw == 196 >> 8


def test_the_169_class_does_not_pass_the_pair_raw() -> None:
    """The two classes must never be treated as sharing semantics."""
    item = record(class_raw=TRANSITION_CLASS_B_RAW, arrival=(100, 200))
    assert not item.has_raw_arrival_pair


def test_the_169_class_scene_relative_transform_is_reproduced() -> None:
    """(scene + stored - region low) per axis, truncating to 16 bits.

    Measured at 08007234/08007238/0800723C/08007240 for x and the +0x16/+0x0A pair
    for y. The stored pair is a delta, so the scene origin is part of the answer.
    """
    item = record(
        class_raw=TRANSITION_CLASS_B_RAW,
        first=(10, 20),
        second=(30, 40),
        arrival=(100, 200),
    )
    assert item.arrival_relative(1000, 2000) == TransitionArrival(
        x=1000 + 100 - 10, y=2000 + 200 - 30
    )
    # The halves are read as SIGNED halfwords, so a high bit subtracts.
    negative = record(
        class_raw=TRANSITION_CLASS_B_RAW,
        first=(0, 0),
        second=(0, 0),
        arrival=(0xFFF0, 5),
    )
    assert negative.arrival_relative(0, 0).x == 0xFFF0 - 0x10000 + 0x10000 & 0xFFFF


def test_each_accessor_refuses_the_class_it_is_not_true_of() -> None:
    """BOTH directions, which is the half an earlier revision of this file missed.

    A 169 record's pair is a delta, and a delta is a small number that every
    bounds check downstream accepts - so returning it as a point is a silent
    wrong answer rather than a loud failure. The arrival accessor must refuse that
    class, and a test that only inspected ``has_raw_arrival_pair`` would pass
    with exactly that defect present.
    """
    point = record(class_raw=TRANSITION_CLASS_A_RAW, arrival=(100, 200))
    assert point.arrival == TransitionArrival(x=100, y=200)
    assert point.raw_coordinate_pair == point.arrival
    with pytest.raises(MapTransitionValueError):
        point.arrival_relative(0, 0)

    delta = record(class_raw=TRANSITION_CLASS_B_RAW, arrival=(100, 200))
    assert not delta.has_raw_arrival_pair
    # The bytes stay readable - the round trip and the prior checks need them -
    # but they are not offered under a name that claims to be a position.
    assert delta.raw_coordinate_pair == TransitionArrival(x=100, y=200)
    with pytest.raises(MapTransitionValueError):
        delta.arrival


def test_an_unset_arrival_is_a_sentinel_and_not_the_origin() -> None:
    """``(0, 0)`` is a real point; the sentinel range is a different answer."""
    origin = record(arrival=(0, 0))
    assert origin.arrival == TransitionArrival(x=0, y=0)
    for sentinel in (0xFFF8, 0xFFFC, 0xFFFE, 0xFFFF):
        item = record(arrival=(sentinel, 5))
        assert item.arrival is None
        item = record(arrival=(5, sentinel))
        assert item.arrival is None
    assert ARRIVAL_UNSET_MINIMUM == 0xFFF8


def test_a_record_can_be_given_and_stripped_of_an_arrival() -> None:
    item = record(arrival=(1, 2))
    moved = item.with_arrival(TransitionArrival(x=300, y=400))
    assert moved.arrival == TransitionArrival(x=300, y=400)
    assert item.with_arrival(None).arrival is None
    with pytest.raises(MapTransitionValueError):
        item.with_arrival(TransitionArrival(x=0xFFF8, y=0))
    with pytest.raises(MapTransitionValueError):
        item.with_arrival((1, 2))  # type: ignore[arg-type]


# --- the facing byte ---------------------------------------------------------


def test_the_facing_byte_splits_into_a_gate_and_an_arrival_override() -> None:
    """Low two bits gate the door; the high nibble forces the arrival facing.

    CONFIRMED at 08007696/98/9A (the 566 constructor masks v & 3 and indexes the
    gate table at 0x080707D8) and at 08007638/3A/3C/42/44/48 (the update tests
    v & 0xF0 and writes (v >> 4) - 1 into the player).
    """
    for gate in (0, 1, 2, 3):
        plain = record(facing=gate)
        assert plain.facing.gate_direction == gate
        assert plain.facing.override_raw == 0
        # A zero high nibble states NO arrival facing; it is not "face South".
        assert plain.facing.arrival_direction is None
        assert not plain.facing.states_arrival_facing
        assert plain.facing.direction is None

    # The ten corpus values above 3 are ((arrival + 1) << 4) | gate.
    for arrival in (0, 1, 2, 3):
        for gate in (0, 1, 2, 3):
            packed = ((arrival + 1) << 4) | gate
            item = record(facing=packed)
            assert item.facing.arrival_direction == arrival
            assert item.facing.gate_direction == gate
            assert item.facing.override_raw == arrival + 1
            assert item.facing.raw == packed
            assert item.facing.states_arrival_facing
    assert FACING_MASK == 0x03


def test_setting_an_arrival_facing_writes_the_override_not_the_gate() -> None:
    """The whole point: an unstated facing is what leaves the actor walking."""
    item = record(facing=2)
    stated = item.with_arrival_facing(FACING_NORTH)
    assert stated.byte_0x10_raw == ((FACING_NORTH + 1) << 4) | 2
    assert stated.facing.arrival_direction == FACING_NORTH
    assert stated.facing.gate_direction == 2, "the gate bits must survive"
    # Clearing the override returns the record to "do not state a facing".
    assert stated.with_arrival_facing(None).byte_0x10_raw == 2
    for bad in (4, -1, 17, "1", None if False else True):
        with pytest.raises(MapTransitionValueError):
            stated.with_arrival_facing(bad)  # type: ignore[arg-type]


def test_setting_the_gate_direction_preserves_the_arrival_override() -> None:
    item = record(facing=((FACING_NORTH + 1) << 4) | 1)
    moved = item.with_gate_direction(FACING_EAST)
    assert moved.facing.gate_direction == FACING_EAST
    assert moved.facing.arrival_direction == FACING_NORTH, "the override must survive"
    with pytest.raises(MapTransitionValueError):
        item.with_gate_direction(4)


def test_the_whole_facing_byte_can_be_restored_verbatim() -> None:
    """The round trip needs the byte, not just a decode of it."""
    item = record(facing=0)
    assert item.with_facing_raw(65).byte_0x10_raw == 65
    assert item.with_facing_raw(65).facing.override_raw == 4
    assert item.with_facing_raw(65).facing.arrival_direction == 3
    with pytest.raises(MapTransitionValueError):
        item.with_facing_raw(0x100)


def test_every_corpus_facing_value_has_a_name() -> None:
    assert set(FACING_NAMES) == {0, 1, 2, 3}
    assert FACING_NAMES[FACING_SOUTH] == "South"
    assert FACING_NAMES[FACING_NORTH] == "North"
    assert FACING_NAMES[FACING_WEST] == "West"
    assert FACING_NAMES[FACING_EAST] == "East"


# --- the project document ----------------------------------------------------


def test_a_project_round_trips_arrival_and_facing(tmp_path) -> None:
    edits = TransitionEdits.from_edits({
        (40, 0): AuthoredTransition(
            prior_destination="map:0039", destination="map:0378",
            prior_arrival=(599, 196), arrival=(120, 364), arrival_authored=True,
            prior_facing_raw=2, facing_raw=1, facing_authored=True,
        )
    })
    write_project(tmp_path, META, enemies=[], characters=[], transitions=edits)
    reopened = read_project(tmp_path).transitions.edits()[(40, 0)]
    assert reopened.destination == "map:0378"
    assert reopened.prior_arrival == (599, 196)
    assert reopened.arrival == (120, 364)
    assert reopened.arrival_authored
    assert reopened.prior_facing_raw == 2
    assert reopened.facing_raw == 1
    assert reopened.facing_authored
    assert not reopened.is_noop()


def test_an_absent_arrival_or_facing_is_not_stored(tmp_path) -> None:
    """Absence is a statement, and it must not become a zero."""
    edits = TransitionEdits.from_edits({
        (40, 0): AuthoredTransition(prior_destination="map:0039", destination="map:0038")
    })
    write_project(tmp_path, META, enemies=[], characters=[], transitions=edits)
    reopened = read_project(tmp_path).transitions.edits()[(40, 0)]
    assert reopened.arrival is None and not reopened.arrival_authored
    assert reopened.facing_raw is None and not reopened.facing_authored
    text = (tmp_path / "maps" / "transitions.toml").read_text(encoding="utf-8")
    assert "arrival" not in text and "facing" not in text


def test_a_facing_or_arrival_stated_without_its_group_is_refused() -> None:
    with pytest.raises(ProjectValidationError):
        AuthoredTransition(destination="map:0001", facing_raw=1)
    with pytest.raises(ProjectValidationError):
        AuthoredTransition(destination="map:0001", arrival=(1, 2))
    with pytest.raises(ProjectValidationError):
        AuthoredTransition(facing_raw=300, facing_authored=True)
    with pytest.raises(ProjectValidationError):
        AuthoredTransition(arrival=(1, 70000), arrival_authored=True)


def test_an_entry_that_authors_only_a_facing_is_legal_and_round_trips(tmp_path) -> None:
    edits = TransitionEdits.from_edits({
        (40, 0): AuthoredTransition(
            prior_facing_raw=2, facing_raw=1, facing_authored=True
        )
    })
    write_project(tmp_path, META, enemies=[], characters=[], transitions=edits)
    reopened = read_project(tmp_path).transitions.edits()[(40, 0)]
    assert reopened.facing_raw == 1 and reopened.destination is None
    assert not reopened.is_noop()
    assert AuthoredTransition(
        prior_facing_raw=1, facing_raw=1, facing_authored=True
    ).is_noop()


def test_the_facing_group_survives_a_malformed_high_byte() -> None:
    """A byte above 3 is data, not an error: it round-trips with its flags."""
    edits = TransitionEdits.from_edits({
        (40, 0): AuthoredTransition(
            prior_facing_raw=17, facing_raw=16, facing_authored=True
        )
    })
    assert edits.edits()[(40, 0)].facing_raw == 16


# --- through the authoring API, over the synthetic corpus --------------------


def test_a_facing_edit_persists_and_reopens(tmp_path) -> None:
    image = image_bytes()
    project = project_at(tmp_path)
    assert set_transition_edits(
        project, profile_for(image), image, {PEER: TransitionEdit(facing=FACING_NORTH)}
    )
    stored = read_transition_edits(project).edits()[(0, 0)]
    assert stored.facing_authored
    # The stored byte is the OVERRIDE form, ((north + 1) << 4) | gate, because
    # that is what forces the facing; the low bits alone would not.
    assert stored.facing_raw == ((FACING_NORTH + 1) << 4)
    assert stored.prior_facing_raw == 0
    # Untouched groups stay absent.
    assert stored.destination is None and not stored.arrival_authored
    text = (project / "maps" / "transitions.toml").read_text(encoding="utf-8")
    assert "facing_raw = 32" in text and "facing_authored = true" in text


def test_a_facing_edit_leaves_the_arrival_bytes_untouched(tmp_path) -> None:
    """The plan must move the facing byte and nothing else."""
    from tools.webfoot.write import plan_changes

    image = image_bytes()
    profile = profile_for(image)
    from tools.webfoot.map_transitions import (
        AuthoredTransitionEdit,
        plan_transition_edits,
        read_map_transitions,
    )

    corpus = read_map_transitions(image, profile)
    entry = corpus.entry(PEER)
    application = plan_transition_edits(
        image,
        {PEER: AuthoredTransitionEdit(
            prior_facing_raw=0, facing_raw=1, facing_authored=True
        )},
        profile=profile,
    )
    plan = plan_changes(
        image, application.changes, profile_id=profile.id,
        base_sha256=profile.identity.sha256,
    )
    (edit,) = application.provenance
    assert edit.facing_changed and edit.facing_raw == 1 and edit.prior_facing_raw == 0
    assert not edit.arrival_changed and not edit.destination_changed
    assert not edit.region_changed
    changed = [c for c in plan.changes if c.is_effective]
    # A plan's change is the record's whole 24-byte extent, so locality is the
    # set of bytes that differ INSIDE it - here exactly the facing byte.
    assert [c.offset for c in changed] == [entry.file_offset]
    (change,) = changed
    differing = [i for i in range(len(change.old)) if change.old[i] != change.new[i]]
    assert differing == [0x10], (
        "a facing edit must move exactly the +0x10 byte"
    )
    assert change.new[0x10] == 1


def test_a_facing_prior_that_disagrees_with_the_image_is_refused() -> None:
    from tools.webfoot.map_transitions import (
        AuthoredTransitionEdit,
        plan_transition_edits,
    )

    image = image_bytes()
    profile = profile_for(image)
    with pytest.raises(TransitionFieldError, match="authored against facing"):
        plan_transition_edits(
            image,
            {PEER: AuthoredTransitionEdit(
                prior_facing_raw=3, facing_raw=1, facing_authored=True
            )},
            profile=profile,
        )


def test_re_authoring_the_same_facing_is_a_no_op(tmp_path) -> None:
    """Authoring the same facing twice must not create a second record."""
    image = image_bytes()
    project = project_at(tmp_path)
    profile = profile_for(image)
    set_transition_edits(project, profile, image, {PEER: TransitionEdit(facing=1)})
    first = read_transition_edits(project).edits()[(0, 0)]
    set_transition_edits(project, profile, image, {PEER: TransitionEdit(facing=1)})
    again = read_transition_edits(project).edits()[(0, 0)]
    assert again == first
    assert len(read_transition_edits(project).edits()) == 1


def test_an_arrival_facing_override_survives_a_gate_edit() -> None:
    """The two halves of +0x10 are independent, so one edit cannot erase the other."""
    from tools.webfoot.map_transitions import read_map_transitions

    image = image_bytes()
    corpus = read_map_transitions(image, profile_for(image))
    corpus.set_facing(PEER, 1)
    assert corpus.entry(PEER).record.byte_0x10_raw == ((1 + 1) << 4)
    corpus.set_gate_direction(PEER, 3)
    assert corpus.entry(PEER).record.byte_0x10_raw == ((1 + 1) << 4) | 3
    assert corpus.facing(PEER) == 1 and corpus.gate_direction(PEER) == 3
    # ...and the gate edit is what a facing edit must not disturb in reverse.
    corpus.set_facing(PEER, 2)
    assert corpus.entry(PEER).record.byte_0x10_raw == ((2 + 1) << 4) | 3
    assert corpus.gate_direction(PEER) == 3


def test_an_invalid_facing_value_is_refused_before_anything_is_written(tmp_path) -> None:
    image = image_bytes()
    project = project_at(tmp_path)
    for bad in (4, -1, 99):
        with pytest.raises(TransitionFieldError):
            set_transition_edits(
                project, profile_for(image), image, {PEER: TransitionEdit(facing=bad)}
            )
    with pytest.raises(TransitionFieldError):
        TransitionEdit(facing=17)
    assert read_transition_edits(project).is_empty()


def test_the_default_facing_heuristic_is_documented_as_a_default() -> None:
    """The heuristic must never read as engine law."""
    from tools.webfoot.map_transitions import MapTransitions

    doc = MapTransitions.default_facing.__doc__ or ""
    assert "DEFAULT" in doc
    assert "not engine law" in doc
    assert "heuristic" in doc
    # And the retarget docstring must point at it as a default too.
    retarget_doc = MapTransitions.retarget.__doc__ or ""
    assert "default_facing" in retarget_doc
