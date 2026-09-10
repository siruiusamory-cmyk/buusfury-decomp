"""ARCH-REFACTOR-001: the authored-materialization policy, tested where it lives.

These exercise the two entry points extracted from `build.py` directly, on the
synthetic `types` graph, so every decision they own is pinned without the
canonical ROM. The build-driver-level proofs of the same paths stay in
`test_authored_placements.py`; these are about the policy itself.
"""
from dataclasses import replace

import pytest

from tests.unit.test_placement_types import types  # shared synthetic graph fixture
from tools.webfoot import build, placement_events
from tools.webfoot.binary import FileOffset
from tools.webfoot.authored_placements import (check_authored_placement_policy,
                                               materialize_for_build)
from tools.webfoot.data import placement_contracts
from tools.webfoot.layout import FreeRegion, LayoutError, RomRange
from tools.webfoot.maps import MapIdentity
from tools.webfoot.project import ProjectMeta, read_project, write_project
from tools.webfoot.project.placements import clone_placement


@pytest.fixture
def project(tmp_path, types):
    maps = types.maps
    meta = ProjectMeta(1, maps.profile.id, maps.profile.game, maps.profile.sha256,
                       len(maps.base_bytes), "synthetic-clone")
    write_project(tmp_path, meta, enemies=[], characters=[], maps=build._map_documents(maps))
    return tmp_path


def add(project, name="wolf", **changes):
    args = dict(map_index=0, source="map:0000/placement:0000", name=name,
                position_low=123, position_high=456)
    args.update(changes)
    return clone_placement(project, **args)


# --- materialize_for_build: the four decisions --------------------------------


def test_missing_document_reports_the_ownership_contract(project, types):
    """Decision 1: no reference graph REPORTS the contract; it does not just fail.

    The gate is reached with the image but no document, so its message is the
    measured one - the serialized capacity request and the modelled bodies - and
    it names the absent document as the reason rather than an allocator error.
    """
    add(project)
    with pytest.raises(LayoutError) as caught:
        materialize_for_build(read_project(project), types.maps, lambda maps: None)
    message = str(caught.value)
    assert "map:0000/placement_references" in message
    assert "proposed capacity request 108 bytes, alignment 4" in message
    assert "bodies are MODELLED (map:0000/authored:wolf)" in message
    assert "no reference document was supplied, so materialization was not attempted" in message


def test_layout_error_is_raised_through_the_gate(project, types):
    """Decision 2: the gate runs FIRST, so the blocker carries measured context.

    Against the synthetic profile the real allocator refuses the body for want of
    declared capacity. What proves the re-raise went through the gate rather than
    escaping raw is that the message carries the gate's measured framing AND names
    the production refusal inside it.
    """
    add(project)
    with pytest.raises(LayoutError) as caught:
        materialize_for_build(read_project(project), types.maps,
                              lambda maps: types.reference_document())
    message = str(caught.value)
    # The gate's own measured context - a bare allocator error carries none of it.
    assert "valid authored placement content serialized" in message
    assert "proposed capacity request 108 bytes" in message
    assert "array anchor IS relocatable" in message
    # ...and the real production refusal, reported rather than predicted.
    assert "InsufficientSpaceError" in message


def test_authored_map_identities_name_every_authoring_map(project, types):
    """Decision 3: the set handed to `Maps.changes` is derived from the runs."""
    add(project)
    capacity = replace(types.profile, free_regions=(
        FreeRegion(RomRange(FileOffset(0x10000), 1024),
                   "synthetic verified capacity"),))
    document = replace(types.reference_document(), profile=capacity)
    changes, identities = materialize_for_build(
        read_project(project), types.maps, lambda maps: document)
    assert changes
    assert identities == frozenset({MapIdentity(0)})
    assert isinstance(identities, frozenset)


def test_no_authored_runs_returns_empty_and_never_reaches_the_gate(project, types):
    """A canonical project authors nothing, so nothing is planned and no gate runs.

    The factory is made to explode: reaching it at all would be the bug, because a
    project with no authored runs must not consult a reference graph.
    """
    def explode(maps):  # pragma: no cover - reaching this IS the failure
        raise AssertionError("no authored runs must never build a reference document")

    changes, identities = materialize_for_build(read_project(project), types.maps, explode)
    assert changes == []
    assert identities == frozenset()


def test_runs_without_maps_still_reach_the_gate(project, types):
    """Decision 4's sibling: authored content is never silently dropped.

    `prepare_authored_runs` refuses authored placements against no maps at all, so
    the `elif` branch is reached by way of that refusal rather than by a run that
    exists without a table. Pinned so the branch keeps failing closed.
    """
    add(project)
    from tools.webfoot.project import ProjectValidationError
    with pytest.raises(ProjectValidationError, match="authored placements require verified maps"):
        materialize_for_build(read_project(project), None, lambda maps: None)


def test_the_document_factory_is_injected_not_imported(project, types):
    """The graph is the driver's to supply: whatever it returns is what is used."""
    add(project)
    seen = []

    def factory(maps):
        seen.append(maps)
        return None

    with pytest.raises(LayoutError):
        materialize_for_build(read_project(project), types.maps, factory)
    assert seen == [types.maps]


# --- check_authored_placement_policy ------------------------------------------


def test_structured_vs_legacy_determination(project, types):
    """A project whose placements carry `descriptor` is structured, not legacy.

    The synthetic profile is not in CONTRACTS, so a structured project is refused
    as unsupported - which is the same determination reported from the other side.
    """
    model = read_project(project)
    # The synthetic extraction carries no descriptor column, so this is legacy.
    problems, policy = check_authored_placement_policy(model, types.maps)
    assert problems == []
    # Legacy against a non-CONTRACTS profile substitutes nothing.
    assert policy.map_view is types.maps

    model.maps[0]["placements"][0]["descriptor"] = "map:0000/placement:0000/descriptor"
    problems, _ = check_authored_placement_policy(model, types.maps)
    assert problems == ["placement descriptor/event data requires verified profile support"]


def test_descriptor_catalog_requires_verified_profile_support(project, types):
    """An events catalog against a profile without contract support is refused."""
    model = replace(read_project(project), placement_events={"schema": 1})
    problems, _ = check_authored_placement_policy(model, types.maps)
    assert problems == ["placement descriptor/event data requires verified profile support"]


def test_unsupported_structured_noncontracts_preserves_unbound_relationships_path(
        project, types):
    """The extraction preserves the baseline uncaught exception, not a repair.

    The old `_check_maps` bound `relationships` only inside the CONTRACTS branch
    but read it during the later structural comparison. This successful generic
    reconciliation reaches that exact read and must remain `UnboundLocalError`.
    """
    model = read_project(project)
    model.maps[0]["placements"][0]["descriptor"] = (
        "map:0000/placement:0000/descriptor")
    with pytest.raises(UnboundLocalError, match="relationships"):
        build._check_maps(model, types.maps)


def test_contract_legacy_view_substitution_reaches_downstream_map_checks(
        project, types, monkeypatch):
    """Every generic `_check_maps` consumer uses the domain's legacy map view."""
    model = read_project(project)
    seen = []

    class SourceMaps:
        profile = types.maps.profile

        def legacy_view(self):
            seen.append("legacy_view")
            return types.maps

        def entries(self):  # pragma: no cover - use means substitution was ignored
            raise AssertionError("downstream reconciliation used the source map table")

    monkeypatch.setitem(placement_contracts.CONTRACTS, types.maps.profile.id, {})
    monkeypatch.setattr(placement_events, "PlacementEvents", lambda maps: object())
    assert build._check_maps(model, SourceMaps()) == []
    assert seen == ["legacy_view"]


def test_placement_type_catalog_mismatch_is_reported(project, types):
    """A type catalog that differs from the verified base is refused, not merged."""
    model = replace(read_project(project),
                    placement_types={"placement_types": {}, "placements": {}})
    problems, _ = check_authored_placement_policy(model, types.maps)
    assert problems == [
        "placement type catalog differs from verified base; type reassignment is unsupported"]
    # The matching catalog is accepted.
    matching = replace(read_project(project), placement_types=types.project_document())
    assert check_authored_placement_policy(matching, types.maps)[0] == []


def test_placement_type_catalog_without_maps_is_refused(project, types):
    """No loaded table means the catalog cannot be checked, so it is not accepted."""
    model = replace(read_project(project), placement_types=types.project_document())
    problems, policy = check_authored_placement_policy(model, None)
    assert problems == ["placement type catalog requires verified map/type support"]
    assert policy.map_view is None


def test_invalid_placement_type_catalog_is_named(project, types):
    """A catalog the type layer refuses is reported as invalid, not as a mismatch."""
    model = replace(read_project(project), placement_types={"placement_types": object()})
    problems, _ = check_authored_placement_policy(model, types.maps)
    assert len(problems) == 1
    assert problems[0].startswith("invalid placement type catalog: ")


def test_structural_field_mismatch_is_reported(project, types, monkeypatch):
    """The structural comparison refuses a mirrored field the project changed."""
    from tools.webfoot.maps import PlacementIdentity

    live = types.maps.placement(PlacementIdentity(0, 0))

    class Relationships:
        def project_document(self):
            return {"schema": 1}

        def extend_references(self, document):
            return document

        def descriptor_of(self, identity):
            return type("D", (), {"identity": "map:0000/placement:0000/descriptor"})()

    expected_events = {"schema": 1,
                       "reference_graph": types.reference_document().to_compact_json()}
    monkeypatch.setitem(placement_contracts.CONTRACTS, types.maps.profile.id, {})
    monkeypatch.setattr(placement_events, "PlacementEvents", lambda maps: Relationships())
    model = replace(read_project(project), placement_events=expected_events)
    problems, policy = check_authored_placement_policy(model, types.maps)
    assert problems == []

    faithful = {
        "descriptor": "map:0000/placement:0000/descriptor",
        "child_count": live.record.child_count,
        "child_pointers_raw": list(live.record.child_pointers_raw),
        "record_size": live.record.consumed_length,
    }
    assert policy.placement_problems(faithful, live) == []

    for field, value in (("descriptor", "fabricated"), ("child_count", 99),
                         ("child_pointers_raw", [1, 2, 3]), ("record_size", 4)):
        assert policy.placement_problems({**faithful, field: value}, live) == [
            f"{live.identity}: structural placement fields differ from base"]


# --- the terminal domain validation -------------------------------------------


def test_terminal_validation_surfaces_a_refusal_as_a_problem_string(project, types):
    """A `prepare_authored_runs` refusal becomes a problem, never an exception."""
    model = read_project(project)
    _, policy = check_authored_placement_policy(model, types.maps)
    assert policy.final_problems() == []
    # Authored placements against no maps: a ValueError subclass, reported as text.
    add(project)
    _, policy = check_authored_placement_policy(read_project(project), None)
    assert policy.final_problems() == ["authored placements require verified maps"]


def test_terminal_validation_surfaces_a_key_error_as_a_problem_string(project, types):
    """A KeyError out of run preparation is reported rather than escaping.

    Dropping the extracted row a clone template needs makes `prepare_authored_runs`
    raise `KeyError`; terminal domain validation turns it into a problem.
    """
    add(project)
    model = read_project(project)
    model.maps[0]["placements"] = ()
    _, policy = check_authored_placement_policy(model, types.maps)
    problems = policy.final_problems()
    assert len(problems) == 1
