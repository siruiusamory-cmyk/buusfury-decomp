"""Synthetic placement/type and common indexed-reference proofs; no private inputs."""
from dataclasses import replace
from pathlib import Path
import struct

import pytest

from tests.helpers import make_synthetic_rom, profile_for, hashes_for
from tools.webfoot import capability
from tools.webfoot.binary import FileOffset
from tools.webfoot.entities import PlacementTypes, PlacementTypeIdentity, PlacementTypeError
from tools.webfoot.formats.map_entry import MapEntry
from tools.webfoot.formats.map_placements import PlacementRecord, FACTORY_RAW, RECORD_TAIL
from tools.webfoot.formats.stat_tables import decode_enemy_record, encode_enemy_record
from tools.webfoot.gba_header import GbaHeader
from tools.webfoot.layout import AnchorId, LayoutError, Reference, ReferenceClass, ReferenceEncoding, Provenance
from tools.webfoot.maps import Maps, MapEntryEntry, MapIdentity, PlacementEntry, PlacementIdentity
from tools.webfoot.profile import RomProfileCatalog, ProfileConfigError
from tools.webfoot.rom import RomIdentification


@pytest.fixture
def types(monkeypatch):
    data = bytearray(make_synthetic_rom(size=0x20000))
    entries, placements = [], []
    for index, selectors in enumerate(((1, 3), (1,))):
        base = 0x100 + index * 56
        array = 0x200 + index * 16
        struct.pack_into('<I', data, base + 0x14, 0x08000000 + array)
        for slot, selector in enumerate(selectors):
            offset = 0x400 + len(placements) * 32
            raw = struct.pack('<8I', FACTORY_RAW, 0x12345678, selector, 0x12340056, 9, *RECORD_TAIL)
            data[offset:offset+32] = raw
            struct.pack_into('<I', data, array + slot*4, 0x08000000 + offset)
            placements.append(PlacementEntry(PlacementIdentity(index, slot), PlacementRecord.from_bytes(raw), offset, raw))
        raw = bytes(data[base:base+56])
        entries.append(MapEntryEntry(MapIdentity(index), MapEntry.from_bytes(raw), base, raw))
    for index in range(3):
        raw = bytearray(range(28))
        struct.pack_into('<I', raw, 8, 434 + index)
        data[0x800+index*28:0x800+(index+1)*28] = raw
    data = bytes(data)
    profile = profile_for(data, tables={
        'placement_types': {'table_address': 0x08000800, 'stride': 28, 'max_selector': 3,
                            'factory_raw': FACTORY_RAW, 'constructor_address': 0x08000320,
                            'evidence': 'synthetic indexed constructor'},
        'enemy_stats': {'address': 0x08000800, 'count': 3, 'record_size': 28}})
    catalog = RomProfileCatalog([profile])
    monkeypatch.setattr(capability, '_packaged_catalog', lambda: catalog)
    hashes = hashes_for(data)
    header = GbaHeader.from_bytes(data)
    ident = RomIdentification(Path('synthetic'), len(data), hashes, header,
                              catalog.match(size=len(data), hashes=hashes, header=header))
    maps = Maps(identification=ident, profile=profile, entries=tuple(entries), arrays=(),
                placements=tuple(placements), base_bytes=data)
    return PlacementTypes(maps)


def test_shared_type_and_map_traversal(types):
    one, three = types.types()
    assert one.identity.selector == 1
    assert len(one.placements) == 2 and len(one.maps) == 2
    assert types.type_of(PlacementIdentity(1, 0)) is one
    assert types.for_map(MapIdentity(0))[0] == (PlacementIdentity(0, 0), one.identity)
    assert types.placements_of_type(one.identity) == one.placements
    assert three.identity.selector == 3


def test_identity_stable_when_type_address_moves(types):
    item = types.types()[0]
    assert replace(item, file_offset=0x900).identity == item.identity
    assert str(item.identity) == 'synthetic_exact/placement_type:0001'
    assert PlacementTypeIdentity('different_profile', 1) != item.identity


def test_enemy_link_uses_selected_record_identity_not_selector(types):
    item = types.types()[0]
    assert item.enemy_identity.key == 435
    assert item.identity.selector == 1
    assert item.classification == 'CONFIRMED_ENEMY_STAT_LINK'


def test_outside_verified_stat_extent_has_no_codec_or_enemy(types):
    item = types.types()[1]
    assert item.enemy_identity is None and item.original_bytes is None
    assert item.classification == 'UNKNOWN_CATEGORY'


def test_existing_codec_preserves_every_unknown_byte(types):
    raw = types.types()[0].original_bytes
    assert raw is not None
    assert encode_enemy_record(decode_enemy_record(raw, 0), raw) == raw
    assert raw[16:] == bytes(range(16, 28))


def test_factory_link_and_no_gameplay_taxonomy(types):
    factory = types.factory_of(types.types()[0].identity)
    assert factory['raw_pointer'] == FACTORY_RAW
    assert factory['fetch_address'] + 1 == FACTORY_RAW
    for key in ('npc_friendly', 'item_pickup', 'script_event', 'graphics_resource'):
        assert types.summary()[key] == 'UNKNOWN'


def test_deterministic_enumeration_and_project_dedup(types):
    assert [t.identity.selector for t in types.types()] == [1, 3]
    doc = types.project_document()
    assert len(doc['placements']) == 3 and len(doc['placement_types']) == 2
    assert all('raw' not in t for t in doc['placement_types'].values())
    assert doc == PlacementTypes(types.maps).project_document()


@pytest.mark.parametrize('selector', [-1, True, 2**32, '1'])
def test_invalid_type_identity(selector):
    with pytest.raises(PlacementTypeError):
        PlacementTypeIdentity('profile', selector)


def test_unknown_and_wrong_profile_type_fail_closed(types):
    with pytest.raises(PlacementTypeError):
        types.type(PlacementTypeIdentity('wrong', 1))
    with pytest.raises(PlacementTypeError):
        types.type(PlacementTypeIdentity(types.profile.id, 2))
    with pytest.raises(PlacementTypeError):
        types.type_of(PlacementIdentity(88, 0))


@pytest.mark.parametrize('field,value', [('factory_raw', 0x08000301), ('type_raw', 4)])
def test_unsupported_family_and_selector(types, field, value):
    key = PlacementIdentity(0, 0)
    entry = types.maps._placements[key]
    types.maps._placements[key] = replace(entry, record=replace(entry.record, **{field: value}))
    with pytest.raises(PlacementTypeError):
        PlacementTypes(types.maps)


def test_common_graph_indexed_traversal_and_thumb_raw(types):
    doc = types.reference_document()
    item = types.types()[0]
    inbound = doc.inbound(AnchorId(str(item.identity)))
    assert len(inbound) == 2
    assert all(r.encoding is ReferenceEncoding.INDEX_U32_LE for r in inbound)
    assert all(doc.target_offset(r).value == item.file_offset for r in inbound)
    factory = doc.inbound(AnchorId(types.factory_of(item.identity)['id']))
    assert len(factory) == 3 and all(r.target_delta == 1 for r in factory)
    assert all(not a.relocatable for a in doc.anchors)


def test_index_wrong_target_and_encoding_fail_closed(types):
    doc = types.reference_document()
    ref = next(r for r in doc.references if r.encoding is ReferenceEncoding.INDEX_U32_LE)
    altered = replace(ref, index_stride=29)
    with pytest.raises(LayoutError, match='target mismatch'):
        replace(doc, references=tuple(altered if r is ref else r for r in doc.references)).validate()
    with pytest.raises(LayoutError, match='read-only'):
        ref.encoding.encode(FileOffset(0x900), ref.source, len(doc.image))
    with pytest.raises(LayoutError):
        ref.decode_target((2**32-1).to_bytes(4, 'little'), len(doc.image))


@pytest.mark.parametrize('base,stride', [(None, 28), (FileOffset(0), 0), (FileOffset(0), True)])
def test_index_requires_explicit_context(base, stride):
    with pytest.raises(LayoutError):
        Reference(FileOffset(0), AnchorId('t'), 0, ReferenceEncoding.INDEX_U32_LE,
                  ReferenceClass.CONFIRMED_REFERENCE, Provenance('p','hash','synthetic'), base, stride)


def test_wrong_profile_provenance_and_overlapping_owner(types):
    doc = types.reference_document()
    bad = replace(doc.references[0], provenance=Provenance('wrong', types.profile.sha256, 'test'))
    with pytest.raises(LayoutError, match='provenance'):
        replace(doc, references=(bad, *doc.references[1:])).validate()
    other = replace(doc.anchors[0], identity=AnchorId('other'), owner='other')
    with pytest.raises(LayoutError, match='overlapping ownership'):
        replace(doc, anchors=(*doc.anchors, other)).validate()


@pytest.mark.parametrize('field,value', [
    ('stride', 0), ('stride', True), ('stride', 27), ('max_selector', -1),
    ('max_selector', 2**32), ('factory_raw', 0x08000300),
    ('factory_raw', 0x09000001), ('table_address', 0x08000801),
    ('constructor_address', 0x08000321), ('evidence', ''), ('extra', 1)])
def test_malformed_profile_type_contract(field, value):
    contract = {'table_address': 0x08000800, 'stride': 28, 'max_selector': 3,
                'factory_raw': 0x08000301, 'constructor_address': 0x08000320,
                'evidence': 'synthetic'}
    contract[field] = value
    with pytest.raises(ProfileConfigError):
        profile_for(make_synthetic_rom(size=0x1000), tables={'placement_types': contract})


def test_missing_contract_field_rejected():
    with pytest.raises(ProfileConfigError):
        profile_for(make_synthetic_rom(), tables={'placement_types': {}})


def test_missing_capability_and_metadata_mismatch(types, monkeypatch):
    # Trusted packaged metadata cannot be replaced by a caller's altered layout.
    profile = replace(types.profile, placement_types=None)
    monkeypatch.setattr(capability, '_packaged_catalog', lambda: RomProfileCatalog([profile]))
    with pytest.raises(PlacementTypeError):
        PlacementTypes(types.maps)
