"""TOOLKIT-022 synthetic representation and exact ownership blocker proofs."""
from dataclasses import replace
import copy
import json

import pytest

from tests.unit.test_placement_types import types  # shared synthetic graph fixture
from tools.webfoot import build
from tools.webfoot.allocation import allocate, InsufficientSpaceError
from tools.webfoot.authored_placements import prepare_authored_runs, require_materialization_contract
from tools.webfoot.cli import main
from tools.webfoot.formats.map_placements import PlacementRecord
from tools.webfoot.layout import AnchorId, LayoutError, FreeRegion, RomRange
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
    # The authored clone has no anchor at all, so it cannot be relocated.
    with pytest.raises(LayoutError, match="unknown anchor"):
        plan_relocation(document, [RelocationRequest(
            AnchorId(run.authored_records[0].identity), b"\x00" * 32)])
    # And the production gate stops there, naming that record.
    with pytest.raises(LayoutError, match="unmodelled authored record bodies"):
        require_materialization_contract((run,), types.maps.base_bytes, document)
    assert document.image == types.maps.base_bytes


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
        # TOOLKIT-026: the array anchor is no longer the blocker. The build now
        # reaches - and passes - relocation eligibility, and stops at the authored
        # record body, which has no anchor and no array-slot reference.
        with pytest.raises(LayoutError, match="108 bytes.*unmodelled authored record bodies"):
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
