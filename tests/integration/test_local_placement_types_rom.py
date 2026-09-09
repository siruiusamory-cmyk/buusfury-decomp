"""TOOLKIT-009 canonical static proofs. No runtime inputs; generated outputs only."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.cli import main
from tools.webfoot.entities import load_placement_types, PlacementTypeIdentity, PlacementTypeError
from tools.webfoot.formats.stat_tables import decode_enemy_record, encode_enemy_record
from tools.webfoot.layout import AnchorId, ReferenceEncoding
from tools.webfoot.maps import MapIdentity, PlacementIdentity
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.model import PLACEMENT_TYPES_FILE, read_project
from tools.webfoot.project.format import dump_toml, load_toml
from tools.webfoot.write import ByteChange, plan_changes, OverlappingChangeError

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'


@pytest.fixture(scope='module')
def types():
    if not ROM.is_file():
        pytest.skip('canonical local ROM not configured')
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == SHA
    result = load_placement_types(ROM, RomProfileCatalog.load('config/roms.yaml'))
    yield result
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == SHA


def test_complete_corpus_and_shared_distribution(types):
    summary = types.summary()
    # TOOLKIT-025 remeasured every figure here over the complete engine-counted census.
    # The old tuple (1442, 240, 111) described what a frozen run contract could reach,
    # not the canonical corpus: that contract held 240 of the 316 arrays the engine
    # counts and stored a truncated count for one more. Deriving the bound from
    # `MapEntry+0x04` adds 117 placement-family records, which also moves the enemy
    # links (1420/105 -> 1534/118) and the per-type distribution. Nothing here is
    # adjusted by hand; all of it is measured.
    assert (summary['placement_count'], summary['map_count'], summary['type_count']) == (1559, 268, 125)
    assert (summary['enemy_linked_placements'], summary['enemy_linked_types']) == (1534, 118)
    assert summary['placements_per_type_distribution'][1] == 31
    assert max(summary['placements_per_type_distribution']) == 88
    assert sum(n*count for n,count in summary['placements_per_type_distribution'].items()) == 1559
    assert len({p.identity for p in types.maps.placements()}) == 1559
    assert sum(len(p.original_bytes) for p in types.maps.placements()) == 49988


def test_selector_factory_literal_and_exact_targets(types):
    data = types.maps.base_bytes
    # Static literal, not an inferred pointer scan; FD5C loads this word.
    assert int.from_bytes(data[0xfd70:0xfd74], 'little') == types.layout.table_address.raw
    assert types.layout.stride == 28
    assert types.layout.factory_raw == 0x0800fd55
    assert types.layout.constructor_address.raw == 0x0800f68c
    for p in types.maps.placements():
        assert types.type_of(p.identity).file_offset == types.table_offset + p.record.type_raw*28


def test_enemy_link_proven_by_selected_record_not_numeric_adjacency(types):
    one = types.type(PlacementTypeIdentity(types.profile.id, 1))
    assert one.enemy_identity.key == 23  # selector is not enemy ID
    for t in types.types():
        if t.enemy_identity:
            word = int.from_bytes(types.maps.base_bytes[t.file_offset+8:t.file_offset+12], 'little')
            assert word == t.enemy_identity.key  # actual u32 controller selector, including zero high half


def test_outside_stat_extent_stays_reference_only(types):
    unknown = {t.identity.selector: len(t.placements) for t in types.types() if t.enemy_identity is None}
    # TOOLKIT-025: remeasured over the complete census. Selector 145 is reachable only
    # from records the frozen run contract could not express, and 147/148 each gain one.
    # The property under test is unchanged - every selector outside the verified stat
    # extent stays reference-only, with no invented record extent.
    assert unknown == {141:12, 142:6, 145:1, 146:1, 147:2, 148:2, 149:1}
    assert all(t.original_bytes is None for t in types.types() if t.enemy_identity is None)
    assert types.profile.enemy_stats.count == 141


def test_exhaustive_existing_type_codec_roundtrip(types):
    total = 0
    for t in types.types():
        if t.original_bytes is None:
            continue
        raw = t.original_bytes
        assert encode_enemy_record(decode_enemy_record(raw, 0), raw) == raw
        total += len(raw)
    # TOOLKIT-025: 3,304 bytes over the complete census (was 2,940); 13 further stat
    # records are selected by placements the frozen run contract could not reach.
    assert total == 3304


def test_common_graph_ownership_index_and_factory_links(types):
    doc = types.reference_document()
    indexed = [r for r in doc.references if r.encoding is ReferenceEncoding.INDEX_U32_LE]
    assert len(indexed) == 1559
    assert len(doc.references) > 268 + 3 * 1559  # descriptor/event/native edges now included
    for t in types.types():
        assert len(doc.inbound(AnchorId(str(t.identity)))) == len(t.placements)
    assert all(not a.relocatable for a in doc.anchors)
    assert doc.to_json()['profile_id'] == types.profile.id


def test_project_catalog_determinism_and_old_v1_noop(types, tmp_path):
    catalog = RomProfileCatalog.load('config/roms.yaml')
    roots = [tmp_path/'one', tmp_path/'two']
    for root in roots:
        extract_project(ROM, root, catalog, graphics=False)
    def files(root):
        return {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert files(roots[0]) == files(roots[1])
    project = read_project(roots[0])
    assert project.placement_types == types.project_document()
    for index in range(2):
        output = tmp_path/f'noop{index}.gba'
        build_project(roots[0], ROM, output, catalog)
        assert hashlib.sha256(output.read_bytes()).hexdigest() == SHA
    # Old v1 projects lack the optional relationship catalog and stay valid.
    (roots[1]/PLACEMENT_TYPES_FILE).unlink()
    assert validate_project(roots[1], ROM, catalog).passed
    output = tmp_path/'old-v1.gba'
    build_project(roots[1], ROM, output, catalog)
    assert hashlib.sha256(output.read_bytes()).hexdigest() == SHA


@pytest.mark.parametrize('field,value', [('enemy_id','enemy:9999'), ('selector',True), ('classification','NPC')])
def test_invalid_or_reassigned_catalog_fails_before_output(types, tmp_path, field, value):
    catalog = RomProfileCatalog.load('config/roms.yaml')
    root = tmp_path/'project'
    extract_project(ROM, root, catalog, graphics=False)
    path = root/PLACEMENT_TYPES_FILE
    doc = load_toml(path.read_text())
    first = next(iter(doc['placement_types'].values()))
    first[field] = value
    path.write_text(dump_toml(doc))
    assert not validate_project(root, ROM, catalog).passed
    output = tmp_path/'refused.gba'
    with pytest.raises(ValueError, match='catalog'):
        build_project(root, ROM, output, catalog)
    assert not output.exists()


def test_existing_position_edit_and_no_cross_subsystem_owner_collision(types):
    # Clone the loaded collection; never mutate module fixture or canonical ROM.
    maps = types.maps
    from tools.webfoot.maps import Maps
    edited = Maps(identification=maps.identification, profile=maps.profile,
                  entries=tuple(maps.entries()), arrays=tuple(maps.slot_arrays()),
                  placements=tuple(maps.placements()), base_bytes=maps.base_bytes)
    key = PlacementIdentity(10,0)
    edited.set_placement_position(key, low=76, high=edited.placement(key).record.position_high)
    changes = edited.changes()
    changed = [c for c in changes if c.old != c.new]
    assert len(changed) == 1 and changed[0].owner == str(key)
    assert [i for i,(a,b) in enumerate(zip(changed[0].old, changed[0].new)) if a!=b] == [12]
    plan = edited.plan()
    assert plan is not None
    clash = ByteChange(changed[0].offset, changed[0].old, changed[0].new, 'different_owner', 'conflict')
    with pytest.raises(OverlappingChangeError):
        plan_changes(maps.base_bytes, (*changes, clash), profile_id=maps.profile.id, base_sha256=SHA)


def test_wrong_profile_metadata_rejected(types):
    bad = replace(types.profile, placement_types=replace(types.layout, stride=32))
    with pytest.raises(PlacementTypeError):
        load_placement_types(ROM, RomProfileCatalog([bad]))


def test_cli_semantic_queries(types, capsys):
    assert main(['entity','list',str(ROM),'--map','map:0010']) == 0
    result = json.loads(capsys.readouterr().out)
    key = result[0]['placement_id']
    assert main(['entity','show',str(ROM),key]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown['factory']['status'] == 'CONFIRMED'
    assert main(['entity','placements-of-type',str(ROM),shown['id']]) == 0
    assert key in json.loads(capsys.readouterr().out)
    assert main(['entity','type',str(ROM),'map:9999/placement:0000']) == 2
