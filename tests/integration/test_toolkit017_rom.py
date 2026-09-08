"""Normal-path TOOLKIT-017 proofs. Private canonical input, generated outputs only."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct
import pytest

from tools.webfoot.cli import load_catalog, main
from tools.webfoot.maps import load_maps, MapIdentity, PlacementIdentity
from tools.webfoot.placement_events import PlacementEvents, FAMILY
from tools.webfoot.entities import PlacementTypes
from tools.webfoot.build import extract_project, build_project, validate_project
from tools.webfoot.formats.map_placements import is_legacy_placement_record
from tools.webfoot.formats.script_vm import assemble
from tools.webfoot.scripts import load_scripts, script_families
from tools.webfoot.layout import AnchorId, ReferenceEncoding
from tools.webfoot.project.model import read_project
from tools.webfoot.project.format import load_toml, dump_toml

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
SHA = '940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e'


@pytest.fixture(scope='module')
def maps():
    if not ROM.is_file():
        pytest.skip('canonical local ROM not configured')
    before = ROM.stat()
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == SHA
    yield load_maps(ROM, load_catalog(None))
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == SHA
    assert ROM.stat().st_mtime_ns == before.st_mtime_ns


def test_full_and_legacy_census_identity(maps):
    placements = tuple(maps.placements())
    assert len(placements) == 1442
    assert len(maps.legacy_placements()) == 1295
    # Independent old walk, including stop-at-first-unsupported behavior.
    expected = {}
    for e in maps.entries():
        at = e.record.scripts_pointer_raw - 0x08000000
        ordinal = 0
        while 0 <= at <= len(maps.base_bytes)-4:
            pointer = struct.unpack_from('<I', maps.base_bytes, at)[0]
            offset = pointer - 0x08000000
            if not is_legacy_placement_record(maps.base_bytes, offset):
                break
            expected[str(PlacementIdentity(e.identity.index, ordinal))] = offset
            ordinal += 1
            at += 4
    actual = {str(p.identity):p.file_offset for p in placements}
    assert len(expected) == 1295 and len(actual.keys() - expected.keys()) == 147
    assert all(actual[k] == v for k, v in expected.items())


def test_dynamic_extent_distribution_and_exact_encode(maps):
    assert Counter(p.record.child_count for p in maps.placements()) == {1:1427, 2:7, 3:6, 4:2}
    assert sum(len(p.original_bytes) for p in maps.placements()) == 46244
    for p in maps.placements():
        assert p.record.to_bytes() == p.original_bytes


def test_run_ownership_and_nonoverlap(maps):
    ps = sorted(maps.placements(), key=lambda p:p.file_offset)
    assert len({p.file_offset for p in ps}) == len(ps)
    assert all(a.file_offset + len(a.original_bytes) <= b.file_offset for a,b in zip(ps,ps[1:]))
    assert len({p.identity.map_index for p in ps}) == 240
    runs = []
    for m in maps.entries():
        n = len(maps.map_placements(m.identity))
        if n:
            runs.extend(m.record.scripts_pointer_raw + 4*i for i in range(n))
    assert len(runs) == len(set(runs)) == 1442


def test_corrected_slot_and_type_accounting_keeps_legacy_meaning(maps):
    legacy = maps.legacy_view()
    assert (len(tuple(legacy.slot_arrays())),sum(a.array.slot_count for a in legacy.slot_arrays())) == (112,596)
    assert (len(tuple(maps.slot_arrays())),sum(a.array.slot_count for a in maps.slot_arrays())) == (108,556)
    for view in (maps, legacy):
        assert sum(a.is_typed for a in view.slot_arrays()) == 35
        assert sum(a.array.slot_count for a in view.slot_arrays() if a.is_typed) == 89
    assert PlacementTypes(legacy).summary()['type_count'] == 101
    assert PlacementTypes(maps).summary()['type_count'] == 111


def test_descriptor_sharing_handler_census_and_map_coverage(maps):
    e = PlacementEvents(maps)
    assert len(e.descriptors) == 82
    records, coverage = Counter(), defaultdict(set)
    for p in maps.placements():
        d = e.descriptor_of(p.identity)
        records[d.record.handler_pointer_raw] += 1
        coverage[d.record.handler_pointer_raw].add(p.identity.map_index)
    assert records == {0x0800421D:1361,0x0800421F:57,0x0800424F:24}
    assert {k:len(v) for k,v in coverage.items()} == {0x0800421D:226,0x0800421F:10,0x0800424F:16}
    assert sorted(len(d.placements) for d in e.descriptors if len(d.placements)>1) == [1361]


def test_owned_events_are_normal_family_and_exact(maps):
    assert FAMILY in script_families(ROM,load_catalog(None))
    c = load_scripts(ROM,load_catalog(None),FAMILY)
    assert (len(c.ir.entries),len(c.ir.blocks),c.instruction_count,c.ir.extent) == (25,42,202,514)
    assert len(c.attachments) == 57
    raw = assemble(c.ir)
    for s in c.segments:
        assert raw[s.ir_offset:s.ir_offset+s.size] == maps.base_bytes[s.file_offset:s.file_offset+s.size]
    assert sum(i.opcode == 0x1C for b in c.ir.blocks for i in b.instructions) == 3


def test_derived_attachment_queries_preserve_sharing(maps):
    e = PlacementEvents(maps)
    owned = [p for p in maps.placements() if e.descriptor_of(p.identity).event]
    assert len(owned) == 57 and len({p.identity.map_index for p in owned}) == 10
    assert len(e.events_for_map(MapIdentity(21))) == 1
    assert len(e.events_for_map(MapIdentity(22))) == 1
    assert len(e.events_for_map(MapIdentity(19))) == 10
    assert not e.events_for_map(MapIdentity(10))
    assert len({d.event for d in e.descriptors if d.event}) == 25


def test_common_graph_contains_chain_and_native_references(maps):
    graph = PlacementTypes(maps).reference_document()
    e = PlacementEvents(maps)
    for p in maps.placements():
        d = e.descriptor_of(p.identity)
        assert any(r.source.value == p.file_offset+0x14 for r in graph.inbound(AnchorId(d.identity)))
    for event in e.events:
        assert graph.inbound(AnchorId(event.identity))
    assert any(r.encoding is ReferenceEncoding.INDEX_U8 for r in graph.references)
    assert all(not a.relocatable for a in graph.anchors)
    assert graph.to_json() == PlacementTypes(maps).reference_document().to_json()


def test_normal_path_excludes_unreached_records_and_roots(maps):
    e = PlacementEvents(maps)
    addresses = {p.file_offset+0x08000000 for p in maps.placements()}
    excluded = {0x0807CDF4,0x0807FA1C,0x08081A04,0x08083DA4,0x0808DF58,0x0808E018,0x0808E0CC}
    assert not addresses & excluded
    image = maps.base_bytes
    descriptors = {0x08000000+o for o in range(0,len(image)-8,4)
                   if struct.unpack_from('<I',image,o)[0] == 0x0800421F
                   and 0x08000000 <= struct.unpack_from('<I',image,o+4)[0] < 0x08000000+len(image)}
    owned = {d.file_offset+0x08000000 for d in e.descriptors if d.event}
    assert len(descriptors-owned) == 7+76
    unowned_roots = {struct.unpack_from('<I',image,d-0x08000000+4)[0] for d in descriptors-owned}
    assert len(unowned_roots) == 19
    assert not unowned_roots & {v.file_offset+0x08000000 for v in e.events}


@pytest.fixture
def project(maps,tmp_path):
    root = tmp_path/'project'
    extract_project(ROM,root,load_catalog(None),graphics=False)
    return root


def test_project_structures_deterministic_and_whole_rom_noop(project,tmp_path):
    other = tmp_path/'other'
    extract_project(ROM,other,load_catalog(None),graphics=False)
    def files(root):
        return {p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert files(project) == files(other)
    assert len(files(project)) == 7
    p = read_project(project)
    assert sum(len(m.get('placements',[])) for m in p.maps.values()) == 1442
    assert len(p.placement_events['descriptors']) == 82
    assert len(p.placement_events['events']) == 25
    output = tmp_path/'noop.gba'
    build_project(project,ROM,output,load_catalog(None))
    assert output.read_bytes() == ROM.read_bytes()

@pytest.mark.parametrize('mutation', ['child_count','child_pointers_raw','descriptor','record_size'])
def test_project_malformed_structure_rejected(project,mutation):
    path = project/'maps/maps.toml'
    doc = load_toml(path.read_text())
    p = doc['map']['map:0010']['placements']['placement:0000']
    p[mutation] = {'child_count':4,'child_pointers_raw':[1],'descriptor':'unowned','record_size':44}[mutation]
    path.write_text(dump_toml(doc))
    if mutation == 'descriptor':
        assert not validate_project(project,ROM,load_catalog(None)).passed
    else:
        with pytest.raises(ValueError, match='child|structural'):
            validate_project(project,ROM,load_catalog(None))


def test_no_descriptor_or_event_edit(project):
    path = project/'events/placement_descriptors.json'
    doc = json.loads(path.read_text())
    next(iter(doc['descriptors'].values()))['payload_raw'] = 0
    path.write_text(json.dumps(doc))
    assert not validate_project(project,ROM,load_catalog(None)).passed


def test_position_edit_keeps_historical_exact_byte(project,tmp_path):
    path = project/'maps/maps.toml'
    doc = load_toml(path.read_text())
    p = doc['map']['map:0010']['placements']['placement:0000']
    assert p['position_low'] == 60
    p['position_low'] = 76
    path.write_text(dump_toml(doc))
    output = tmp_path/'edit.gba'
    build_project(project,ROM,output,load_catalog(None))
    assert [(i,a,b) for i,(a,b) in enumerate(zip(ROM.read_bytes(),output.read_bytes())) if a!=b] == [(0x72908,60,76)]


def test_cli_derived_query(maps,capsys):
    assert main(['event','for-map',str(ROM),'map:0021']) == 0
    assert len(json.loads(capsys.readouterr().out)) == 1


def test_exact_legacy_project_remains_buildable(maps,project,tmp_path):
    """Recreate the old authored surface using independently pinned legacy view."""
    legacy = maps.legacy_view()
    (project/'events/placement_descriptors.json').unlink()
    path = project/'maps/maps.toml'
    doc = load_toml(path.read_text())
    for entry in legacy.entries():
        row = doc['map'][str(entry.identity)]
        ps = legacy.map_placements(entry.identity)
        row.pop('placements', None)
        if ps:
            row['placements'] = {f'placement:{p.identity.placement_index:04d}': {
                'position_low':p.record.position_low,'position_high':p.record.position_high,
                'raw':p.original_bytes.hex()} for p in ps}
        array = legacy.slot_array(entry.identity)
        row.pop('slots', None)
        row.pop('shape', None)
        if array:
            row['slots'] = array.array.original_bytes.hex()
            row['shape'] = array.shape.value
    path.write_text(dump_toml(doc))
    (project/'placement_types/types.toml').write_text(dump_toml(PlacementTypes(legacy).project_document()))
    assert validate_project(project,ROM,load_catalog(None)).passed
    output = tmp_path/'legacy.gba'
    build_project(project,ROM,output,load_catalog(None))
    assert output.read_bytes() == ROM.read_bytes()
    row = doc['map']['map:0010']['placements']['placement:0000']
    assert row['position_low'] == 60
    row['position_low'] = 76
    path.write_text(dump_toml(doc))
    edited = tmp_path/'legacy-edit.gba'
    build_project(project,ROM,edited,load_catalog(None))
    assert [(i,a,b) for i,(a,b) in enumerate(zip(ROM.read_bytes(),edited.read_bytes())) if a!=b] == [(0x72908,60,76)]


def test_bad_event_json_fails_as_project_error(project):
    from tools.webfoot.project.model import ProjectLoadError
    (project/'events/placement_descriptors.json').write_text('{')
    with pytest.raises(ProjectLoadError, match='invalid descriptor/event catalog'):
        read_project(project)
    assert main(['validate',str(project),'--rom',str(ROM)]) == 2
