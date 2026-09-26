"""Portable tests for authored map transitions. MAP-WARP-PROJECT-AUTHORING-001.

Two layers are covered over a synthetic image and no ROM:

* ``project.model.TransitionEdits`` - what a transition edit *is* on disk: the
  semantic identity, the destination and the positional region, each stored as a
  prior/authored pair, and the refusals that keep a malformed file from being
  silently dropped from a build;
* ``map_transitions.plan_transition_edits`` / ``set_transition_edits`` - the
  authority that turns that stored edit into a byte plan and back into the project,
  exercised against the same synthetic image ``test_map_transitions`` assembles
  from the measured format.

The synthetic image is deliberately *not* a canonical ROM and asserts no canonical
count. The whole-project build, the real record offsets and the byte-locality proof
live in ``tests/integration/test_map_transition_project_rom.py``.
"""

from __future__ import annotations

from dataclasses import replace as dataclasses_replace
import hashlib
from pathlib import Path

import pytest

from tests.unit.test_map_transitions import (
    TABLE_OFFSET,
    GBA_BASE,
    IMAGE_SIZE,
    key_for,
    record_bytes,
    synthetic_image,
)

from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.formats.map_transitions import (
    MapTransitionError,
    MapTransitionFamilyError,
    MapTransitionRegionError,
    TransitionRegion,
)
from tools.webfoot.map_transitions import (
    AuthoredTransitionEdit,
    MapIdentity,
    MapTransitionsError,
    TransitionEdit,
    TransitionFieldError,
    TransitionIdentity,
    plan_transition_edits,
    read_map_transitions,
    read_transition_edits,
    remove_transition_edit,
    set_transition_edits,
)
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import MapEntryTableProfile, RomProfile
from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    TRANSITION_FILE,
    AuthoredTransition,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    TransitionEdits,
    read_project,
    write_project,
    write_transition_edits,
)
from tools.webfoot.write import apply_plan

META = ProjectMeta(
    format_version=PROJECT_FORMAT_VERSION,
    profile_id="synthetic_transition_project",
    game="synthetic",
    base_rom_sha256="0" * 64,
    base_rom_size=IMAGE_SIZE,
    name="synthetic",
)

#: Map 39's second record in the canonical corpus is a deliberately non-square,
#: asymmetric region: all four endpoints differ and the two intervals have
#: different widths, so neither transposing the intervals nor swapping an
#: interval's ends can pass by coincidence. The same shape is used here.
ASYMMETRIC = TransitionRegion(first=(592, 601), second=(136, 241))
OTHER_ASYMMETRIC = TransitionRegion(first=(0x0102, 0x0304), second=(0x0506, 0x0708))

#: Three maps: map 0 leads to map 1, map 1 leads to map 0, map 2 has none.
PER_MAP = [
    [record_bytes(destination_key=tuple(key_for(1)), first=(592, 601), second=(136, 241))],
    [record_bytes(destination_key=tuple(key_for(0)))],
    [],
]
PEER = TransitionIdentity(MapIdentity(0), 0)
SECOND = TransitionIdentity(MapIdentity(1), 0)


def image_bytes(per_map=None) -> bytes:
    return synthetic_image(PER_MAP if per_map is None else per_map)


def profile_for(image: bytes, *, count: int = len(PER_MAP)) -> RomProfile:
    """The packaged profile with this synthetic image's map table and identity.

    Only the facts these tests observe are changed; every other declaration is the
    packaged profile's, so the fixture cannot pass by accidentally matching a
    second, independently invented profile.
    """
    base = packaged_profile()
    assert base.map_entries is not None
    return dataclasses_replace(
        base,
        id="synthetic_transition_project",
        sha256=hashlib.sha256(image).hexdigest(),
        size=len(image),
        map_entries=MapEntryTableProfile(
            address=GbaRomAddress(GBA_BASE + TABLE_OFFSET),
            count=count,
            record_size=base.map_entries.record_size,
        ),
    )


def project_at(tmp_path: Path, transitions: TransitionEdits | None = None) -> Path:
    write_project(tmp_path, META, enemies=[], characters=[], transitions=transitions)
    return tmp_path


def edits_of(entries: dict[tuple[int, int], AuthoredTransition]) -> TransitionEdits:
    return TransitionEdits.from_edits(entries)


def authored(
    *, destination: str | None = None, region: TransitionRegion | None = None,
    prior: str | None = None, prior_region: TransitionRegion | None = None,
) -> AuthoredTransition:
    """One stored entry with the prior defaulting to the image's own values."""
    return AuthoredTransition(
        prior_destination=prior if destination is not None else None,
        destination=destination,
        prior_region=prior_region if region is not None else None,
        region=region,
    )


# --- the value itself --------------------------------------------------------


def test_key_for_is_the_map_identity_form():
    assert TransitionEdits.key_for(0) == "map:0000"
    assert TransitionEdits.key_for(39) == "map:0039"
    assert TransitionEdits.key_for(452) == "map:0452"


def test_edits_flattens_and_from_edits_is_its_inverse():
    entry = authored(destination="map:0041", prior="map:0040")
    flat = {(39, 1): entry, (7, 0): authored(region=ASYMMETRIC, prior_region=ASYMMETRIC)}
    edits = TransitionEdits.from_edits(flat)
    assert edits.edits() == flat
    assert edits.for_map(39) == {1: entry}
    assert edits.for_map(40) == {}
    assert not edits.is_empty()


def test_an_empty_edit_set_is_empty():
    assert TransitionEdits().is_empty()
    assert TransitionEdits().edits() == {}
    assert TransitionEdits(maps={"map:0000": {}}).is_empty()


def test_the_document_is_keyed_for_numeric_and_deterministic_order():
    """Every level sorts as text in the same order it sorts as a number."""
    edits = TransitionEdits.from_edits({
        (400, 3): authored(destination="map:0001", prior="map:0002"),
        (19, 1): authored(destination="map:0003", prior="map:0004"),
    })
    document = edits.to_document()
    assert list(document["transition"]) == ["map:0019", "map:0400"]
    assert list(document["transition"]["map:0019"]) == ["0001"]
    # Same value, same document, whatever order it was built in.
    other = TransitionEdits.from_edits({
        (19, 1): authored(destination="map:0003", prior="map:0004"),
        (400, 3): authored(destination="map:0001", prior="map:0002"),
    })
    assert other.to_document() == document


def test_a_stored_entry_carries_both_field_pairs_and_nothing_else():
    entry = authored(
        destination="map:0041", prior="map:0040",
        region=OTHER_ASYMMETRIC, prior_region=ASYMMETRIC,
    )
    assert entry.to_document() == {
        "prior_destination": "map:0040",
        "destination": "map:0041",
        "prior_region": [[592, 601], [136, 241]],
        "region": [[0x0102, 0x0304], [0x0506, 0x0708]],
    }


def test_a_region_only_entry_stores_no_destination_pair():
    document = authored(region=OTHER_ASYMMETRIC, prior_region=ASYMMETRIC).to_document()
    assert set(document) == {"prior_region", "region"}


def test_an_entry_that_authors_its_own_prior_is_a_no_op():
    entry = authored(destination="map:0001", prior="map:0001")
    assert entry.is_noop()
    assert not authored(destination="map:0002", prior="map:0001").is_noop()


# --- round trip through disk -------------------------------------------------


def test_a_transition_project_round_trips_through_disk(tmp_path):
    edits = TransitionEdits.from_edits({
        (39, 1): authored(destination="map:0041", prior="map:0040"),
        (7, 0): authored(region=OTHER_ASYMMETRIC, prior_region=ASYMMETRIC),
    })
    write_project(tmp_path, META, enemies=[], characters=[], transitions=edits)

    loaded = read_project(tmp_path).transitions
    assert loaded.maps == edits.maps
    assert loaded.edits() == edits.edits()


def test_a_destination_edit_survives_save_and_reopen(tmp_path):
    entry = authored(destination="map:0041", prior="map:0040")
    project_at(tmp_path, edits_of({(39, 1): entry}))

    reopened = read_transition_edits(tmp_path).edits()[(39, 1)]
    assert reopened.destination == "map:0041"
    assert reopened.prior_destination == "map:0040"
    assert reopened.region is None


def test_a_region_edit_survives_save_and_reopen(tmp_path):
    entry = authored(region=OTHER_ASYMMETRIC, prior_region=ASYMMETRIC)
    project_at(tmp_path, edits_of({(39, 1): entry}))

    reopened = read_transition_edits(tmp_path).edits()[(39, 1)]
    assert reopened.region == OTHER_ASYMMETRIC
    assert reopened.prior_region == ASYMMETRIC
    assert reopened.destination is None


def test_a_destination_and_a_region_together_survive_save_and_reopen(tmp_path):
    entry = authored(
        destination="map:0041", prior="map:0040",
        region=OTHER_ASYMMETRIC, prior_region=ASYMMETRIC,
    )
    project_at(tmp_path, edits_of({(39, 1): entry}))

    reopened = read_transition_edits(tmp_path).edits()[(39, 1)]
    assert reopened == entry
    assert reopened.destination != reopened.prior_destination
    assert reopened.region != reopened.prior_region


def test_the_written_file_carries_no_address_and_no_offset(tmp_path):
    """The authored file names a map, a transition and two field pairs - nothing else."""
    write_transition_edits(
        tmp_path,
        edits_of({(39, 1): authored(destination="map:0040", prior="map:0038")}),
    )
    text = (tmp_path / TRANSITION_FILE).read_text(encoding="utf-8")
    # The map key carries a colon, so the TOML emitter quotes it; the transition
    # index is bare because it is bare-key safe.
    assert '[transition."map:0039"]' in text
    assert "[transition.\"map:0039\".0001]" in text
    assert 'destination = "map:0040"' in text
    assert "0x" not in text
    assert "offset" not in text
    assert "address" not in text
    assert "pointer" not in text


def test_a_project_without_a_transition_document_stays_loadable(tmp_path):
    write_project(tmp_path, META, enemies=[], characters=[])
    project = read_project(tmp_path)
    assert project.transitions.is_empty()
    assert project.transitions.edits() == {}
    assert not (tmp_path / TRANSITION_FILE).exists()


def test_an_empty_transition_set_writes_no_document(tmp_path):
    path = write_transition_edits(tmp_path, TransitionEdits())
    assert not path.exists()
    write_transition_edits(
        tmp_path, edits_of({(39, 1): authored(destination="map:0040", prior="map:0038")})
    )
    assert (tmp_path / TRANSITION_FILE).is_file()
    write_transition_edits(tmp_path, TransitionEdits())
    assert not (tmp_path / TRANSITION_FILE).exists()


def test_write_project_omits_an_empty_transition_document(tmp_path):
    write_project(
        tmp_path, META, enemies=[], characters=[], transitions=TransitionEdits()
    )
    assert not (tmp_path / TRANSITION_FILE).exists()


def test_a_malformed_file_on_disk_is_an_error_not_an_empty_edit_set(tmp_path):
    project_at(tmp_path)
    (tmp_path / "maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / TRANSITION_FILE).write_text("[transition]\n", encoding="utf-8", newline="\n")
    with pytest.raises(ProjectLoadError, match="declares no edits"):
        read_project(tmp_path)


# --- refusals ----------------------------------------------------------------


def _document(table):
    return {"transition": table}


@pytest.mark.parametrize(
    "document",
    [
        {},                                                       # no [transition] table
        {"transition": []},                                       # not a table
        {"transition": {}},                                       # declares no edits
        {"transition": {"zone:0001": {"0001": {}}}},              # not a map identity
        {"transition": {"map:1": {"0001": {}}}},                  # not four digits
        {"transition": {"map:0001": []}},                         # entries not a table
        {"transition": {"map:0001": {}}},                         # declares no transitions
        {"transition": {"map:0001": {"one": {}}}},                # index not an integer
    ],
)
def test_a_malformed_transition_document_is_refused(document):
    with pytest.raises(ProjectLoadError):
        TransitionEdits.from_document(document, "synthetic")


def test_an_unknown_field_in_an_authored_transition_is_refused():
    """A field this format does not know must fail loudly, never be dropped."""
    document = _document({"map:0001": {"0001": {"chunk": 2, "destination": "map:0002"}}})
    with pytest.raises(ProjectLoadError, match="unknown key"):
        TransitionEdits.from_document(document, "synthetic")


@pytest.mark.parametrize(
    "entry",
    [
        {"prior_destination": "map:0001"},                # prior without an authored value
        {"destination": "map:0001"},                      # authored value without a prior
        {"prior_region": [[0, 5], [0, 5]]},               # region prior without a value
        {"region": [[0, 5], [0, 5]]},                     # region value without a prior
        {},                                               # authors nothing at all
        {"destination": "zone:0001", "prior_destination": "map:0002"},   # not a map key
        {"destination": "map:0002", "prior_destination": "0x08007675"},  # not a map key
    ],
)
def test_an_incomplete_or_non_semantic_entry_is_refused(entry):
    document = _document({"map:0001": {"0001": entry}})
    with pytest.raises(ProjectValidationError):
        TransitionEdits.from_document(document, "synthetic")


def test_a_non_integer_region_endpoint_is_refused():
    document = _document({
        "map:0001": {"0001": {"prior_region": [[0, 5], [0, 5]],
                              "region": [["a", "b"], [0, 5]]}},
    })
    with pytest.raises(ProjectValidationError, match="must be integers"):
        TransitionEdits.from_document(document, "synthetic")


def test_a_region_that_is_not_two_intervals_is_refused():
    for bad in ([0, 5], [[0, 5]], [[0, 5], [0, 5], [0, 5]], [[0], [0, 5]]):
        document = _document({
            "map:0001": {"0001": {"prior_region": bad, "region": [[0, 5], [0, 5]]}},
        })
        with pytest.raises(ProjectLoadError):
            TransitionEdits.from_document(document, "synthetic")


@pytest.mark.parametrize(
    "region",
    [
        [[20, 10], [0, 5]],       # first interval unordered
        [[0, 5], [20, 10]],       # second interval unordered
        [[7, 7], [0, 5]],         # first interval degenerate
        [[0, 5], [7, 7]],         # second interval degenerate
        [[0, 0x10000], [0, 5]],   # outside the endpoint's u16 field
    ],
)
def test_the_record_codec_is_the_region_authority(region):
    """A region the codec refuses must not be loadable from a project file.

    The rule is not restated in the project layer: the loader constructs
    `formats.map_transitions.TransitionRegion`, so the file cannot carry a region
    the build would then refuse.
    """
    document = _document({
        "map:0001": {"0001": {"prior_region": [[0, 5], [0, 5]], "region": region}},
    })
    with pytest.raises(ProjectValidationError):
        TransitionEdits.from_document(document, "synthetic")
    with pytest.raises(MapTransitionError):
        TransitionRegion(first=(region[0][0], region[0][1]),
                         second=(region[1][0], region[1][1]))


def test_a_prior_and_an_authored_value_must_be_the_same_kind():
    with pytest.raises(ProjectValidationError, match="together"):
        AuthoredTransition(prior_destination="map:0001")
    with pytest.raises(ProjectValidationError, match="must author a destination"):
        AuthoredTransition()


# --- the authority over the synthetic image ----------------------------------


def test_the_synthetic_corpus_loads_and_resolves_its_destinations():
    image = image_bytes()
    corpus = read_map_transitions(image, profile_for(image))
    assert corpus.record_count == 2
    assert corpus.destination(PEER) == MapIdentity(1)
    assert corpus.destination(SECOND) == MapIdentity(0)


def test_set_transition_edits_persists_and_reopens(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    changed = set_transition_edits(
        project, profile_for(image), image,
        {PEER: TransitionEdit(destination=MapIdentity(2))},
    )
    assert changed

    reopened = read_transition_edits(project).edits()[(0, 0)]
    assert reopened.prior_destination == "map:0001"
    assert reopened.destination == "map:0002"
    assert reopened.region is None
    assert reopened.prior_region is None


def test_set_transition_edits_reads_the_prior_from_the_image(tmp_path):
    """The stored prior is measured, never asserted by the caller."""
    image = image_bytes()
    project = project_at(tmp_path)
    set_transition_edits(
        project, profile_for(image), image,
        {PEER: TransitionEdit(region=OTHER_ASYMMETRIC)},
    )
    reopened = read_transition_edits(project).edits()[(0, 0)]
    assert reopened.prior_region == ASYMMETRIC
    assert reopened.region == OTHER_ASYMMETRIC


def test_setting_a_field_back_to_the_base_removes_that_pair(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    profile = profile_for(image)
    set_transition_edits(
        project, profile, image,
        {PEER: TransitionEdit(destination=MapIdentity(2), region=OTHER_ASYMMETRIC)},
    )
    # Re-set the destination to what the base holds: the pair is dropped rather
    # than recorded as a pretend edit, and the region pair survives.
    set_transition_edits(project, profile, image, {PEER: TransitionEdit(MapIdentity(1))})
    reopened = read_transition_edits(project).edits()[(0, 0)]
    assert reopened.destination is None
    assert reopened.prior_destination is None
    assert reopened.region == OTHER_ASYMMETRIC

    # Setting the region back too leaves nothing authored, and the project drops
    # the document entirely.
    set_transition_edits(project, profile, image, {PEER: TransitionEdit(region=ASYMMETRIC)})
    assert read_transition_edits(project).is_empty()
    assert not (project / TRANSITION_FILE).exists()


def test_removing_a_transition_edit_un_authors_it(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    profile = profile_for(image)
    set_transition_edits(
        project, profile, image, {PEER: TransitionEdit(destination=MapIdentity(2))}
    )
    assert remove_transition_edit(project, PEER)
    assert read_transition_edits(project).is_empty()
    assert not remove_transition_edit(project, PEER)


def test_a_batch_with_one_illegal_entry_writes_nothing(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    profile = profile_for(image)
    with pytest.raises(TransitionFieldError):
        set_transition_edits(
            project, profile, image,
            {
                PEER: TransitionEdit(destination=MapIdentity(2)),
                SECOND: TransitionEdit(destination=MapIdentity(9)),   # no such map
            },
        )
    assert read_transition_edits(project).is_empty()
    assert not (project / TRANSITION_FILE).exists()


def test_an_unknown_transition_identity_is_refused(tmp_path):
    image = image_bytes()
    project = project_at(tmp_path)
    profile = profile_for(image)
    with pytest.raises(MapTransitionsError):
        set_transition_edits(
            project, profile, image,
            {TransitionIdentity(MapIdentity(0), 4): TransitionEdit(MapIdentity(2))},
        )
    with pytest.raises(MapTransitionsError):
        set_transition_edits(
            project, profile, image,
            {TransitionIdentity(MapIdentity(9), 0): TransitionEdit(MapIdentity(2))},
        )
    assert read_transition_edits(project).is_empty()


# --- planning: the build's own entry point -----------------------------------


def test_planning_an_edit_rewrites_only_that_record_and_its_own_bytes():
    """Fixed size, in place: two key bytes for a destination edit, and no more."""
    image = image_bytes()
    profile = profile_for(image)
    request = {
        PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(2)
        )
    }
    application = plan_transition_edits(image, request, profile=profile)
    entry = read_map_transitions(image, profile).entry(PEER)
    edited = apply_plan(image, plan_for(image, application, profile))

    assert [i for i in range(len(image)) if image[i] != edited[i]] == [
        entry.file_offset + 0x11,
        entry.file_offset + 0x12,
    ]
    # Every other record re-encodes to its original bytes.
    untouched = [
        change
        for change in application.changes
        if change.owner != str(PEER) and change.is_effective
    ]
    assert untouched == []


def test_planning_a_region_edit_writes_the_positional_slots():
    image = image_bytes()
    profile = profile_for(image)
    request = {
        PEER: AuthoredTransitionEdit(
            prior_region=ASYMMETRIC, region=OTHER_ASYMMETRIC
        )
    }
    application = plan_transition_edits(image, request, profile=profile)
    entry = read_map_transitions(image, profile).entry(PEER)
    edited = apply_plan(image, plan_for(image, application, profile))

    assert [i for i in range(len(image)) if image[i] != edited[i]] == list(
        range(entry.file_offset + 0x08, entry.file_offset + 0x10)
    )
    assert edited[entry.file_offset + 0x08 : entry.file_offset + 0x10] == (
        OTHER_ASYMMETRIC.to_bytes()
    )


def test_planning_a_destination_and_a_region_together_writes_only_those_ten_bytes():
    image = image_bytes()
    profile = profile_for(image)
    request = {
        PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(2),
            prior_region=ASYMMETRIC, region=OTHER_ASYMMETRIC,
        )
    }
    application = plan_transition_edits(image, request, profile=profile)
    entry = read_map_transitions(image, profile).entry(PEER)
    edited = apply_plan(image, plan_for(image, application, profile))
    assert [i for i in range(len(image)) if image[i] != edited[i]] == sorted(
        [entry.file_offset + 0x11, entry.file_offset + 0x12]
        + list(range(entry.file_offset + 0x08, entry.file_offset + 0x10))
    )
    # The unresolved bytes and both unresolved-shaped words are untouched.
    for offset in (0x00, 0x04, 0x10, 0x13, 0x14, 0x16, 0x17):
        assert edited[entry.file_offset + offset] == image[entry.file_offset + offset], (
            hex(offset)
        )


def test_an_unrelated_record_is_byte_identical_after_an_edit():
    image = image_bytes()
    profile = profile_for(image)
    application = plan_transition_edits(
        image,
        {PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(2))},
        profile=profile,
    )
    corpus = read_map_transitions(image, profile)
    edited = apply_plan(image, plan_for(image, application, profile))
    other = corpus.entry(SECOND)
    span = slice(other.file_offset, other.file_offset + 24)
    assert edited[span] == other.original_bytes
    assert [c.owner for c in application.changes if c.is_effective] == [str(PEER)]


def test_a_stored_prior_that_disagrees_with_the_image_is_refused():
    image = image_bytes()
    profile = profile_for(image)
    with pytest.raises(TransitionFieldError, match="authored against destination"):
        plan_transition_edits(
            image,
            {PEER: AuthoredTransitionEdit(
                prior_destination=MapIdentity(2), destination=MapIdentity(0))},
            profile=profile,
        )
    with pytest.raises(TransitionFieldError, match="authored against region"):
        plan_transition_edits(
            image,
            {PEER: AuthoredTransitionEdit(
                prior_region=OTHER_ASYMMETRIC, region=ASYMMETRIC)},
            profile=profile,
        )


def test_an_invalid_destination_is_refused():
    image = image_bytes()
    profile = profile_for(image)
    with pytest.raises(TransitionFieldError):
        plan_transition_edits(
            image,
            {PEER: AuthoredTransitionEdit(
                prior_destination=MapIdentity(1), destination=MapIdentity(7))},
            profile=profile,
        )
    with pytest.raises(TransitionFieldError):
        plan_transition_edits(
            image,
            {PEER: AuthoredTransitionEdit(
                prior_destination=MapIdentity(1), destination="map:0002")},  # type: ignore[arg-type]
            profile=profile,
        )


def test_an_unordered_or_degenerate_region_never_reaches_a_plan():
    image = image_bytes()
    profile = profile_for(image)
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(20, 10), second=(0, 5))
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(7, 7), second=(0, 5))
    # An empty project still plans to nothing at all.
    application = plan_transition_edits(image, {}, profile=profile)
    assert application.changes == ()
    assert application.provenance == ()


def test_an_unknown_transition_identity_never_reaches_a_plan():
    image = image_bytes()
    profile = profile_for(image)
    with pytest.raises(MapTransitionsError):
        plan_transition_edits(
            image,
            {TransitionIdentity(MapIdentity(0), 3): AuthoredTransitionEdit(
                prior_destination=MapIdentity(1), destination=MapIdentity(2))},
            profile=profile,
        )


def test_an_unsupported_record_family_refuses_the_whole_corpus(tmp_path):
    """A record whose class word is unmeasured makes the image unaddressable."""
    image = image_bytes([[record_bytes(class_raw=0x08001234)]])
    profile = profile_for(image, count=1)
    request = {PEER: AuthoredTransitionEdit(
        prior_destination=MapIdentity(1), destination=MapIdentity(2))}
    with pytest.raises(MapTransitionFamilyError):
        read_map_transitions(image, profile)
    with pytest.raises(MapTransitionFamilyError):
        plan_transition_edits(image, request, profile=profile)
    project = project_at(tmp_path)
    with pytest.raises(MapTransitionFamilyError):
        set_transition_edits(
            project, profile, image, {PEER: TransitionEdit(destination=MapIdentity(2))}
        )
    assert read_transition_edits(project).is_empty()


def test_a_no_op_authored_pair_emits_no_effective_change():
    image = image_bytes()
    profile = profile_for(image)
    application = plan_transition_edits(
        image,
        {PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(1),
            prior_region=ASYMMETRIC, region=ASYMMETRIC)},
        profile=profile,
    )
    assert application.changes == ()
    assert application.provenance == ()
    assert apply_plan(image, plan_for(image, application, profile)) == image


def test_planning_is_deterministic_and_ordered_by_identity():
    image = image_bytes()
    profile = profile_for(image)
    request = {
        SECOND: AuthoredTransitionEdit(
            prior_destination=MapIdentity(0), destination=MapIdentity(2)),
        PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(2)),
    }
    first = plan_transition_edits(image, request, profile=profile)
    second = plan_transition_edits(image, request, profile=profile)
    assert first == second
    assert [edit.identity for edit in first.provenance] == [str(PEER), str(SECOND)]


def test_the_provenance_answers_which_transition_changed_and_from_what():
    image = image_bytes()
    profile = profile_for(image)
    application = plan_transition_edits(
        image,
        {PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(2),
            prior_region=ASYMMETRIC, region=OTHER_ASYMMETRIC)},
        profile=profile,
    )
    (edit,) = application.provenance
    assert edit.identity == str(PEER) == "map:0000/transition:0000"
    assert edit.source_map == 0 and edit.index == 0
    assert edit.destination_changed and edit.region_changed
    assert (edit.prior_destination, edit.destination) == ("map:0001", "map:0002")
    assert edit.prior_region == (ASYMMETRIC.first, ASYMMETRIC.second)
    assert edit.region == (OTHER_ASYMMETRIC.first, OTHER_ASYMMETRIC.second)
    # The physical record offset is provenance beside the semantic identity,
    # never the identity itself.
    assert edit.file_offset == read_map_transitions(image, profile).entry(PEER).file_offset
    assert "0x" not in edit.identity


def test_provenance_reports_only_the_group_that_changed():
    image = image_bytes()
    profile = profile_for(image)
    application = plan_transition_edits(
        image,
        {PEER: AuthoredTransitionEdit(
            prior_destination=MapIdentity(1), destination=MapIdentity(2),
            prior_region=ASYMMETRIC, region=ASYMMETRIC)},
        profile=profile,
    )
    (edit,) = application.provenance
    assert edit.destination_changed
    assert not edit.region_changed
    assert edit.region is None and edit.prior_region is None


def plan_for(image: bytes, application, profile: RomProfile):
    """One plan from an application, against the image the authority read."""
    from tools.webfoot.write import plan_changes

    return plan_changes(
        image,
        application.changes,
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
    )
