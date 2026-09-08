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
from tools.webfoot.layout import LayoutError, FreeRegion, RomRange
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


def test_synthetic_capacity_does_not_grant_relocation_authority(project, types):
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
    # Exercise the real relocator against the actual synthetic placement graph.
    # Sufficient capacity must not override its fixed-anchor authority guard.
    document = replace(types.reference_document(), profile=profile)
    with pytest.raises(LayoutError, match="non-relocatable anchor"):
        plan_relocation(document, [RelocationRequest(run.identity, run.serialized_records)])
    # TOOLKIT-024 proved the traversal contract; the gate now names the real
    # remaining blocker, an engine count field no write path can express.
    with pytest.raises(LayoutError, match="unwritable engine count"):
        require_materialization_contract((run,))
    assert document.image == types.maps.base_bytes


def test_build_fails_at_the_unwritable_count_and_publishes_nothing(project, types, monkeypatch, tmp_path):
    add(project)
    maps = types.maps
    monkeypatch.setattr(build, "_load_for_project", lambda *args:
        (read_project(project), maps.identification, maps.profile, None, None, maps))
    assert build.validate_project(project, "unused", None).passed
    run, = build.authored_capacity_plan(project, "unused", None)
    assert run.allocation_request.size == 108
    output, manifest = tmp_path / "out.gba", tmp_path / "manifest.json"
    for _ in range(2):
        with pytest.raises(LayoutError, match="108 bytes.*unwritable engine count"):
            build.build_project(project, "unused", output, None, manifest_path=manifest)
    assert not output.exists() and not manifest.exists()


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
