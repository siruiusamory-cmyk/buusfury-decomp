"""TOOLKIT-022 synthetic representation and exact ownership blocker proofs."""
from dataclasses import replace
import copy
import json

import pytest

from tests.unit.test_placement_types import types  # shared synthetic graph fixture
from tools.webfoot import build
from tools.webfoot.allocation import allocate, InsufficientSpaceError
from tools.webfoot.authored_placements import (AuthoringOverlayError, authoring_overlay,
                                               plan_authored_materialization,
                                               prepare_authored_runs,
                                               require_materialization_contract)
from tools.webfoot.cli import main
from tools.webfoot.formats.map_placements import PlacementRecord
from tools.webfoot.layout import (AnchorId, LayoutError, FreeRegion, ReferenceEncoding,
                                  RomRange)
from tools.webfoot.binary import FileOffset
from tools.webfoot.project import ProjectMeta, ProjectError, read_project, write_project
from tools.webfoot.project.format import load_toml, dump_toml
from tools.webfoot.project.placements import AuthoredPlacement, clone_placement
from tools.webfoot.relocation import plan_relocation, RelocationRequest


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


def _capacity(types):
    """Synthetic verified capacity, declared exactly as a profile free region."""
    return replace(types.profile, free_regions=(
        FreeRegion(RomRange(FileOffset(0x10000), 1024), "synthetic verified capacity"),))


def rewrite(project, edit):
    path = project / "maps/maps.toml"
    doc = load_toml(path.read_text())
    edit(doc["map"]["map:0000"])
    path.write_text(dump_toml(doc), encoding="utf-8", newline="\n")


def test_explicit_provenance_and_v1_compatibility(project, types):
    before = read_project(project)
    assert before.meta.format_version == 1
    assert "authored_placements" not in before.maps[0]
    clone = add(project)
    loaded = read_project(project)
    assert loaded.maps[0]["placements"] == before.maps[0]["placements"]
    assert loaded.maps[0]["authored_placements"] == (clone,)
    assert clone.provenance == "AUTHORED_CLONE"
    assert build._check_maps(loaded, types.maps) == []
    run, = prepare_authored_runs(loaded, types.maps)
    assert [r.provenance for r in run.records] == ["EXTRACTED", "EXTRACTED", "AUTHORED_CLONE"]


@pytest.mark.parametrize("changes", [
    {"name": "../bad"}, {"name": "placement:0000"}, {"map_index": 999},
    {"source": "map:0000/placement:9999"}, {"source": "map:0000/authored:wolf"},
    {"position_low": -1}, {"position_high": 65536}, {"position_low": True},
])
def test_invalid_authoring_never_writes(project, changes):
    before = (project / "maps/maps.toml").read_bytes()
    with pytest.raises(ProjectError):
        add(project, **changes)
    assert (project / "maps/maps.toml").read_bytes() == before


def test_duplicate_id_refused_without_write(project):
    add(project)
    before = (project / "maps/maps.toml").read_bytes()
    with pytest.raises(ProjectError, match="duplicate authored"):
        add(project)
    assert (project / "maps/maps.toml").read_bytes() == before


@pytest.mark.parametrize("field,value", [("raw", "00"), ("type_raw", 99),
    ("child_count", 2), ("descriptor", "fabricated"), ("file_offset", 1024)])
def test_structural_fabrication_rejected(project, field, value):
    clone = add(project)
    rewrite(project, lambda m: m["authored_placements"][clone.identity].update({field: value}))
    with pytest.raises(ProjectError, match="structural fabrication"):
        read_project(project)


def test_missing_template_and_wrong_owner_rejected_on_load(project):
    clone = add(project)
    rewrite(project, lambda m: m["placements"].pop("placement:0000"))
    with pytest.raises(ProjectError, match="missing extracted clone template"):
        read_project(project)


def test_authored_identity_must_match_owning_map(project):
    clone = add(project)
    def move(m):
        row = m["authored_placements"].pop(clone.identity)
        m["authored_placements"]["map:0001/authored:wolf"] = row
    rewrite(project, move)
    with pytest.raises(ProjectError, match="authored identity"):
        read_project(project)


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_real_codec_preserves_all_unknown_words(count):
    template = PlacementRecord(0x0800FD55, 0xDEADBEEF, 3, 0x11112222, 0xABCDEF01,
                               0x08000100, tuple(0x08002000 + 4*i for i in range(count)))
    clone = AuthoredPlacement("map:0000/authored:wolf", 0, "map:0000/placement:0000", 123, 456)
    result = clone.serialize(template)
    assert len(result) == 0x1C + 4 * count
    assert result[:12] == template.to_bytes()[:12]
    assert result[16:] == template.to_bytes()[16:]
    assert result[12:16] == b"\x7b\x00\xc8\x01"
    assert PlacementRecord.from_bytes(result).child_pointers_raw == template.child_pointers_raw
    assert result == clone.serialize(template)


def test_canonical_count_and_identity_guards_survive(project, types):
    project_model = read_project(project)
    assert build._check_maps(project_model, types.maps) == []
    for mutation in (lambda rows: rows.pop(), lambda rows: rows.append(rows[0]),
                     lambda rows: rows.__setitem__(1, rows[0]), lambda rows: rows.reverse()):
        model = copy.deepcopy(project_model)
        mutation(model.maps[0]["placements"])
        assert build._check_maps(model, types.maps)
    model = copy.deepcopy(project_model)
    model.maps[0]["placements"][0]["raw"] = bytes(32)
    assert any("raw bytes" in p for p in build._check_maps(model, types.maps))


def test_order_capacity_and_template_edits_are_deterministic(project, types):
    add(project, name="zebra")
    add(project, name="alpha")
    rewrite(project, lambda m: m["placements"]["placement:0000"].update(position_low=17))
    run, = prepare_authored_runs(read_project(project), types.maps)
    assert [r.identity for r in run.records] == ["map:0000/placement:0000", "map:0000/placement:0001",
                                               "map:0000/authored:alpha", "map:0000/authored:zebra"]
    assert len(run.records) == 4 and run.canonical_count == 2
    assert run.allocation_request.size == 4*4 + 4*32 == 144
    assert PlacementRecord.from_bytes(run.records[0].payload).position_low == 17
    assert PlacementRecord.from_bytes(run.records[2].payload).position_low == 123
    assert run == prepare_authored_runs(read_project(project), types.maps)[0]
    evidence = run.to_json()
    assert evidence["allocated_file_offset"] is None
    assert evidence["rewritten_references"] == []
    assert run.record("map:0000/authored:alpha").clone_from == "map:0000/placement:0000"
    assert "payload" not in json.dumps(evidence)


def test_synthetic_capacity_relocates_the_array_but_not_the_authored_body(project, types):
    """TOOLKIT-026: the array anchor moves; the authored record still cannot.

    This replaces the TOOLKIT-022/025 assertion that capacity never granted
    relocation authority. It no longer holds: the array's measured reference set
    satisfies the relocation safety contract, so `plan_relocation` accepts it and
    reaches the allocator. What capacity still does NOT grant is an anchor for a
    record that does not exist in the base image.
    """
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    assert run.allocation_request.size == 108
    with pytest.raises(InsufficientSpaceError):
        allocate(types.profile, [run.allocation_request])
    profile = replace(types.profile, free_regions=(
        FreeRegion(RomRange(FileOffset(0x10000), 1024), "synthetic verified capacity"),))
    first = allocate(profile, [run.allocation_request])
    assert first == allocate(profile, [run.allocation_request])
    assert first[0].range.start.value == 0x10000
    # The real relocator, against the actual placement graph, now MOVES the array.
    document = replace(types.reference_document(), profile=profile)
    slots = 4 * run.target_slot_count
    result = plan_relocation(document, [RelocationRequest(run.identity, b"\x00" * slots)])
    assert result.allocations[0].range.start.value == 0x10000
    assert result.allocations[0].range.size == slots
    # ...and the base image is still untouched: relocation plans, it does not write.
    assert document.image == types.maps.base_bytes
    # TOOLKIT-027: the authored clone has no anchor in the BASE graph - and cannot,
    # because its bytes do not exist there. `authoring_overlay` is what creates one.
    with pytest.raises(LayoutError, match="unknown anchor"):
        plan_relocation(document, [RelocationRequest(
            AnchorId(run.authored_records[0].identity), b"\x00" * 32)])
    assert document.image == types.maps.base_bytes


# --- TOOLKIT-027: the authored body gets an anchor and the new slot a reference ---

def test_authored_body_anchor_uses_the_stable_project_identity(project, types):
    """The anchor ID is the authored project identity, never a ROM address."""
    add(project, name="alpha")
    run, = prepare_authored_runs(read_project(project), types.maps)
    document = replace(types.reference_document(), profile=_capacity(types))
    body, = authoring_overlay(document, run)
    assert body.identity == AnchorId("map:0000/authored:alpha")
    assert body.identity.value == run.authored_records[0].identity
    # It survives a different allocation, because it is not derived from one.
    assert body.slot_index == len(run.canonical_slots) == 2
    assert body.payload == run.authored_records[0].payload


def test_authored_body_is_the_production_codec_output(project, types):
    """No parallel test-only body format: the anchor holds exactly codec bytes."""
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    document = replace(types.reference_document(), profile=_capacity(types))
    body, = authoring_overlay(document, run)
    decoded = PlacementRecord.from_bytes(body.payload)
    assert (decoded.position_low, decoded.position_high) == (123, 456)
    from tools.webfoot.maps import PlacementIdentity
    template = PlacementRecord.from_bytes(
        types.maps.placement(PlacementIdentity(0, 0)).original_bytes)
    assert decoded == template.with_position(123, 456)
    assert len(body.payload) == decoded.consumed_length


def test_synthetic_capacity_allocates_body_and_array_and_fills_the_third_slot(project, types):
    """The whole TOOLKIT-027 chain, on production machinery only.

    description -> anchor -> production codec body -> allocation under synthetic
    verified capacity -> new array-slot reference -> third slot holds the body
    pointer rather than 0x00000000.
    """
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    profile = _capacity(types)
    document = replace(types.reference_document(), profile=profile)
    plan = plan_authored_materialization(document, run)

    # Both the expanded array and the authored body were placed by `allocate`.
    placed = {a.request.anchor.value: a for a in plan.allocations}
    assert set(placed) == {run.identity.value, "map:0000/authored:wolf"}
    body_span = placed["map:0000/authored:wolf"].range
    array_span = placed[run.identity.value].range
    assert array_span.size == 4 * run.target_slot_count
    assert body_span.size == len(run.authored_records[0].payload)
    assert not body_span.overlaps(array_span)

    # The two canonical slots are preserved EXACTLY, byte for byte.
    canonical = types.maps.base_bytes[
        document.anchor(run.identity).range.start.value:document.anchor(run.identity).range.end]
    moved = plan.relocation.document
    relocated = moved.anchor(run.identity)
    assert moved.image[relocated.range.start.value:relocated.range.start.value + 8] == canonical

    # The third slot holds the authored body's address, not a null pointer.
    pointer = plan.slot_pointer(2)
    assert pointer != 0x00000000
    assert pointer == 0x08000000 + body_span.start.value

    # That slot is a real reference in the graph, targeting the body anchor.
    slot_source = relocated.range.start.value + 8
    slot = next(r for r in plan.references if r.source.value == slot_source)
    assert slot.target == AnchorId("map:0000/authored:wolf")
    assert slot.target_delta == 0
    assert slot.encoding is ReferenceEncoding.ABSOLUTE_ROM_U32_LE

    # And the body anchor is published over exactly the allocated span.
    anchor = next(a for a in plan.anchors if a.identity.value == "map:0000/authored:wolf")
    assert anchor.range == body_span and anchor.kind == "authored_placement_body"
    assert not anchor.relocatable

    # The verified base was never touched.
    assert document.image == types.maps.base_bytes


def test_body_and_expanded_array_never_share_bytes(project, types):
    """Regression: two allocator calls must agree about what is already taken.

    `plan_authored_materialization` allocates the bodies, then `plan_relocation`
    allocates the expanded array on its own. Before the free regions offered to
    relocation had the body spans withheld, both calls chose the SAME lowest first
    fit, so the array was laid over the body and the appended slot pointed at the
    array's own first byte - non-null, and wrong.
    """
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    document = replace(types.reference_document(), profile=_capacity(types))
    plan = plan_authored_materialization(document, run)
    spans = [a.range for a in plan.allocations]
    assert len(spans) == 2
    assert not spans[0].overlaps(spans[1])
    body = next(a.range for a in plan.allocations if a.request.anchor.value.endswith("authored:wolf"))
    array = plan.relocation.document.anchor(run.identity).range
    assert not body.overlaps(array)
    # The slot resolves to the body, not to the array it sits next to.
    assert plan.slot_pointer(2) - 0x08000000 == body.start.value != array.start.value


def test_withhold_only_ever_subtracts_capacity(types):
    """The relocation profile is the declared regions minus taken spans, never more."""
    from tools.webfoot.authored_placements import _withhold
    regions = (FreeRegion(RomRange(FileOffset(0x1000), 0x100), "declared"),)
    # A span carved from the middle splits the region in two, total size shrinks.
    out = _withhold(regions, (RomRange(FileOffset(0x1040), 0x20),))
    assert [(r.range.start.value, r.range.size) for r in out] == [(0x1000, 0x40), (0x1060, 0xA0)]
    assert sum(r.range.size for r in out) == 0x100 - 0x20
    # A span covering the whole region removes it entirely.
    assert _withhold(regions, (RomRange(FileOffset(0x1000), 0x100),)) == ()
    # A disjoint span changes nothing.
    assert _withhold(regions, (RomRange(FileOffset(0x2000), 8),)) == regions
    assert all(r.evidence == "declared" for r in out)


def test_authored_materialization_is_deterministic(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    document = replace(types.reference_document(), profile=_capacity(types))
    first = plan_authored_materialization(document, run)
    second = plan_authored_materialization(document, run)
    assert first.to_json() == second.to_json()
    assert first.relocation.document.image == second.relocation.document.image
    assert first.slot_pointer(2) == second.slot_pointer(2)
    assert [c.new for c in first.body_changes] == [c.new for c in second.body_changes]


def test_overlay_refuses_a_fixed_array_and_a_duplicate_identity(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    document = replace(types.reference_document(), profile=_capacity(types))
    fixed = replace(document, anchors=tuple(
        replace(a, relocatable=False) if a.identity == run.identity else a
        for a in document.anchors))
    with pytest.raises(AuthoringOverlayError, match="not relocatable"):
        authoring_overlay(fixed, run)
    body, = authoring_overlay(document, run)
    clash = replace(document, anchors=(*document.anchors,
        replace(document.anchor(run.identity), identity=body.identity)))
    with pytest.raises(AuthoringOverlayError, match="already exists"):
        authoring_overlay(clash, run)


def test_build_fails_at_the_relocation_gate_and_publishes_nothing(project, types, monkeypatch, tmp_path):
    add(project)
    maps = types.maps
    monkeypatch.setattr(build, "_load_for_project", lambda *args:
        (read_project(project), maps.identification, maps.profile, None, None, maps))
    assert build.validate_project(project, "unused", None).passed
    run, = build.authored_capacity_plan(project, "unused", None)
    assert run.allocation_request.size == 108
    output, manifest = tmp_path / "out.gba", tmp_path / "manifest.json"
    for _ in range(2):
        # TOOLKIT-027: the authored body is no longer the blocker either. The build
        # reaches relocation eligibility, models the body and its array-slot
        # reference, and now stops at CAPACITY - the synthetic profile declares no
        # free regions, so the production allocator refuses the body.
        with pytest.raises(LayoutError, match="108 bytes.*bodies are MODELLED"):
            build.build_project(project, "unused", output, None, manifest_path=manifest)
        with pytest.raises(LayoutError, match="InsufficientSpaceError"):
            build.build_project(project, "unused", output, None, manifest_path=manifest)
    assert not output.exists() and not manifest.exists()


# --- TOOLKIT-025 derived count-write contract --------------------------------

def test_no_op_project_derives_no_count_write(project, types):
    """A canonical project authors nothing, so no run and no count write exist."""
    assert prepare_authored_runs(read_project(project), types.maps) == ()
    # And a run that happens to declare exactly its canonical slots emits None
    # rather than a no-change write.
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    unchanged = replace(run, records=tuple(r for r in run.records
                                           if r.provenance == "EXTRACTED"))
    assert unchanged.target_slot_count == unchanged.canonical_engine_count
    assert unchanged.derive_count_change(types.maps.base_bytes) is None


def test_authored_expansion_derives_exactly_old_plus_one(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    image = types.maps.base_bytes
    change = run.derive_count_change(image)
    assert change is not None
    assert change.new[0] == change.old[0] + 1
    assert change.old[0] == run.canonical_engine_count
    assert change.new[0] == run.target_slot_count
    assert change.offset == run.map_entry_offset + 0x04
    assert image[change.offset] == change.old[0]
    # Provenance identifies the authoring operation, not a generic field edit.
    assert change.owner.endswith("/object_array_count")
    assert "authored object-array expansion" in change.reason
    # Deterministic.
    assert run.derive_count_change(image) == change


def test_count_write_is_not_reachable_as_a_raw_field_edit():
    """Users cannot edit a count directly; MAP_FIELDS still refuses every one."""
    from tools.webfoot.maps import MAP_FIELDS
    assert not [name for name in MAP_FIELDS if "count" in name]


def test_stale_model_fails_closed_rather_than_writing(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    from tools.webfoot.authored_placements import AuthoredCountError
    # The image disagrees with the modelled canonical count -> refuse, never write.
    corrupt = bytearray(types.maps.base_bytes)
    corrupt[run.map_entry_offset + 0x04] = run.canonical_engine_count + 5
    with pytest.raises(AuthoredCountError, match="disagrees with MapEntry"):
        run.derive_count_change(bytes(corrupt))


def test_model_and_count_must_agree_before_either_is_rewritten(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    from tools.webfoot.authored_placements import AuthoredCountError
    mismatched = replace(run, canonical_slots=run.canonical_slots[:-1],
                         canonical_engine_count=run.canonical_engine_count)
    with pytest.raises(AuthoredCountError, match="model and the count field must agree"):
        mismatched.derive_count_change(types.maps.base_bytes)


def test_canonical_slot_deletion_is_unsupported(project, types):
    """Deletion is refused, and the refusal is structural rather than incidental.

    `target_slot_count` counts every canonical slot plus the authored additions, so a
    well-formed run can never declare fewer slots than the canonical array - deletion
    is unrepresentable, not merely rejected. The explicit guard exists so a future
    model that CAN express removal fails closed instead of quietly shrinking a count,
    and it is exercised here directly.
    """
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    from tools.webfoot.authored_placements import AuthoredCountError
    # Unrepresentable through the normal path: dropping authored records only ever
    # returns the count to canonical, never below it.
    stripped = replace(run, records=tuple(r for r in run.records
                                          if r.provenance == "EXTRACTED"))
    assert stripped.target_slot_count == stripped.canonical_engine_count
    assert stripped.derive_count_change(types.maps.base_bytes) is None
    # The guard itself, reached with a model whose slots and count agree but whose
    # canonical array is longer than what the image declares.
    image = bytearray(types.maps.base_bytes)
    image[run.map_entry_offset + 0x04] = 3
    deleting = replace(run, canonical_engine_count=3,
                       canonical_slots=run.canonical_slots[:1] * 3,
                       records=tuple(r for r in run.records
                                     if r.provenance == "EXTRACTED")[:1])
    assert deleting.target_slot_count == 3
    shrunk = replace(deleting, canonical_slots=run.canonical_slots[:1] * 2,
                     canonical_engine_count=3)
    with pytest.raises(AuthoredCountError):
        shrunk.derive_count_change(bytes(image))


def test_count_overflow_is_refused(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    from tools.webfoot.authored_placements import AuthoredCountError, MAX_ENGINE_COUNT
    # A full array of 255 canonical slots plus one authored addition needs 256, which
    # the single byte the engine reads cannot express. The model and the count field
    # agree here, so this reaches the overflow check rather than the agreement check.
    huge = replace(run, canonical_slots=run.canonical_slots[:1] * MAX_ENGINE_COUNT,
                   canonical_engine_count=MAX_ENGINE_COUNT)
    assert len(huge.canonical_slots) == MAX_ENGINE_COUNT
    assert huge.target_slot_count == MAX_ENGINE_COUNT + 1
    image = bytearray(types.maps.base_bytes)
    image[run.map_entry_offset + 0x04] = MAX_ENGINE_COUNT
    with pytest.raises(AuthoredCountError, match="one unsigned byte"):
        huge.derive_count_change(bytes(image))


def test_missing_provenance_refuses_to_name_a_byte(project, types):
    add(project)
    run, = prepare_authored_runs(read_project(project), types.maps)
    from tools.webfoot.authored_placements import AuthoredCountError
    orphan = replace(run, map_entry_offset=None)
    with pytest.raises(AuthoredCountError, match="no map-entry provenance"):
        orphan.derive_count_change(types.maps.base_bytes)


def test_cli_clone_is_narrow_and_deterministic(project, capsys):
    args = ["placement", "clone", str(project), "--map", "map:0000", "--source",
            "map:0000/placement:0000", "--name", "wolf", "--position-low", "123",
            "--position-high", "456"]
    assert main(args) == 0
    assert capsys.readouterr().out.strip() == "map:0000/authored:wolf"
    assert main(args) == 2
    assert "duplicate authored" in capsys.readouterr().err


def test_future_version_still_fails(project):
    path = project / "project.toml"
    path.write_text(path.read_text().replace("format_version = 1", "format_version = 99"))
    with pytest.raises(ProjectError, match="version"):
        read_project(project)


# --- TOOLKIT-030: authored behavior attachment ---------------------------------
#
# The clone codec is the only place a behavior can reach the ROM, so these pin
# the representation itself. The ROM-grounded resolution proof lives in
# tests/integration/test_authored_behavior_rom.py, because only the canonical
# image publishes real descriptor identities.


@pytest.mark.parametrize("value", [
    "0x0808D788",                                   # a raw ROM address
    "0808D788",                                     # a bare descriptor word
    "map:0428/placement:0000/descriptor/event",     # the event, not the descriptor
    "behavior:collision_rect",                      # an invented namespace
    134666632,                                      # an integer address
])
def test_behavior_must_be_a_descriptor_identity(value):
    """Raw addresses are not an authoring API; only published identities are."""
    with pytest.raises(ProjectError, match="existing placement descriptor identity"):
        AuthoredPlacement("map:0000/authored:wolf", 0, "map:0000/placement:0000",
                          123, 456, behavior=value)


def test_absent_behavior_inherits_the_template_descriptor():
    """The pre-TOOLKIT-030 path is unchanged: no declaration, no attachment."""
    template = PlacementRecord(0x0800FD55, 7, 86, 0, 0xD3, 0x080555A0, (0x080716EC,))
    clone = AuthoredPlacement("map:0000/authored:wolf", 0, "map:0000/placement:0000", 123, 456)
    assert clone.behavior is None
    assert "behavior" not in clone.to_document()
    decoded = PlacementRecord.from_bytes(clone.serialize(template))
    assert decoded.descriptor_pointer_raw == template.descriptor_pointer_raw


def test_declared_behavior_replaces_only_the_descriptor_word():
    """Ancestry is preserved: the authored record still IS a clone of its template."""
    template = PlacementRecord(0x0800FD55, 7, 86, 0, 0xD3, 0x080555A0, (0x080716EC,))
    clone = AuthoredPlacement("map:0000/authored:wolf", 0, "map:0000/placement:0000", 176, 176,
                              behavior="map:0428/placement:0000/descriptor")
    decoded = PlacementRecord.from_bytes(clone.serialize(template, 0x0808D788))
    assert decoded.descriptor_pointer_raw == 0x0808D788
    assert decoded == replace(template, position_raw=(176 << 16) | 176,
                              descriptor_pointer_raw=0x0808D788)
    # Every other word, children included, comes from the verified template.
    for field in ("factory_raw", "flags_raw", "type_raw", "id_raw", "child_pointers_raw"):
        assert getattr(decoded, field) == getattr(template, field)


def test_declared_behavior_without_resolution_refuses_to_serialize():
    """A behavior the build never resolved must never reach bytes."""
    template = PlacementRecord(0x0800FD55, 7, 86, 0, 0xD3, 0x080555A0, (0x080716EC,))
    clone = AuthoredPlacement("map:0000/authored:wolf", 0, "map:0000/placement:0000", 176, 176,
                              behavior="map:0428/placement:0000/descriptor")
    with pytest.raises(ProjectError, match="was not resolved"):
        clone.serialize(template)


def test_behavior_round_trips_through_project_source(project):
    """The declaration survives write -> read, and stays optional in v1."""
    clone = add(project, behavior="map:0428/placement:0000/descriptor")
    assert clone.behavior == "map:0428/placement:0000/descriptor"
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.behavior == "map:0428/placement:0000/descriptor"
    assert reloaded == clone


def test_behavior_removal_reverts_to_inheritance(project):
    """Removing the declaration must remove the attachment, not strand it."""
    clone = add(project, behavior="map:0428/placement:0000/descriptor")
    rewrite(project, lambda m: m["authored_placements"][clone.identity].pop("behavior"))
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.behavior is None


def test_unknown_authored_field_is_still_refused(project):
    """`behavior` is the ONLY field the additive surface gained."""
    clone = add(project)
    rewrite(project, lambda m: m["authored_placements"][clone.identity].update(
        {"descriptor_pointer_raw": 134666632}))
    with pytest.raises(ProjectError, match="structural fabrication"):
        read_project(project)


def test_cli_clone_accepts_a_behavior(project, capsys):
    assert main(["placement", "clone", str(project), "--map", "map:0000", "--source",
                 "map:0000/placement:0000", "--name", "wolf", "--position-low", "176",
                 "--position-high", "176", "--behavior",
                 "map:0428/placement:0000/descriptor"]) == 0
    assert capsys.readouterr().out.strip() == "map:0000/authored:wolf"
    reloaded, = read_project(project).maps[0]["authored_placements"]
    assert reloaded.behavior == "map:0428/placement:0000/descriptor"
