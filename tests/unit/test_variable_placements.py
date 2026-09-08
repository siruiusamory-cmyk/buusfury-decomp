"""TOOLKIT-017 synthetic contracts: dynamic extents, losslessness, fail closed."""
import struct
from dataclasses import replace
import pytest

from tools.webfoot.formats.map_placements import (
    FACTORY_RAW, ROM_BASE, PlacementRecord, MapPlacementError,
    read_placement_record, iter_placement_offsets, DescriptorRecord,
)
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import (Reference, ReferenceEncoding, ReferenceClass,
                                  Provenance, AnchorId, LayoutError)


def raw(n):
    return struct.pack('<7I', FACTORY_RAW, 0xFFFFFFFF, 0x81234567, 0x12345678,
                       0xABCDEF01, ROM_BASE + 0x100, n) + struct.pack(
                           f'<{n}I', *(ROM_BASE + 0x120 + 4*i for i in range(n)))


@pytest.mark.parametrize('n', [1, 2, 3, 4])
def test_dynamic_ordered_lossless_record(n):
    data = raw(n)
    r = read_placement_record(data, 0, end=len(data))
    assert r.child_count == n
    assert r.consumed_length == 0x1C + 4*n
    assert r.child_pointers_raw == tuple(ROM_BASE + 0x120 + 4*i for i in range(n))
    assert r.descriptor_pointer_raw == ROM_BASE + 0x100
    assert r.to_bytes() == data
    edited = r.with_position(0x5679, 0x1234).to_bytes()
    assert [i for i, (a, b) in enumerate(zip(data, edited)) if a != b] == [12]


@pytest.mark.parametrize('n', [1, 2, 3, 4])
def test_truncated_child_array_is_an_error(n):
    with pytest.raises(MapPlacementError):
        read_placement_record(raw(n)[:-1], 0)


@pytest.mark.parametrize('n', [0, 5, 0xFFFFFFFF])
def test_unsupported_count_cannot_allocate_or_overflow(n):
    data = bytearray(raw(1))
    struct.pack_into('<I', data, 0x18, n)
    with pytest.raises(MapPlacementError):
        read_placement_record(data, 0)


def test_declared_extent_limits_read_even_when_more_image_bytes_exist():
    with pytest.raises(MapPlacementError):
        read_placement_record(raw(4) + b'\0'*64, 0, end=40)


def test_unknown_child_values_preserved_without_normalization():
    r = replace(PlacementRecord.from_bytes(raw(3)), child_pointers_raw=(0, 3, 0xFFFFFFFF))
    assert PlacementRecord.from_bytes(r.to_bytes()) == r


def test_descriptor_unknown_payload_round_trip():
    data = struct.pack('<II', 0x0800424F, 0xFFFFFFFF)
    assert DescriptorRecord.from_bytes(data).to_bytes() == data
    with pytest.raises(MapPlacementError):
        DescriptorRecord.from_bytes(data[:-1])


def test_malformed_factory_record_does_not_silently_terminate_walk():
    data = bytearray(256)
    struct.pack_into('<I', data, 0, ROM_BASE + 32)
    data[32:64] = raw(1)
    struct.pack_into('<I', data, 32+24, 0xFFFFFFFF)
    with pytest.raises(MapPlacementError):
        iter_placement_offsets(data, 0)


def test_declared_pointer_run_truncation():
    with pytest.raises(MapPlacementError):
        iter_placement_offsets(b'\0'*4, 0, count=2)


def test_duplicate_bodies_rejected():
    data = bytearray(128)
    struct.pack_into('<II', data, 0, ROM_BASE + 32, ROM_BASE + 32)
    data[32:64] = raw(1)
    with pytest.raises(MapPlacementError, match='overlapping'):
        iter_placement_offsets(data, 0, count=2)


def test_native_byte_index_is_structural_read_only():
    p = Provenance('synthetic', '0'*64, 'synthetic test')
    ref = Reference(FileOffset(1), AnchorId('native:2'), 0, ReferenceEncoding.INDEX_U8,
                    ReferenceClass.CONFIRMED_REFERENCE, p, FileOffset(16), 4)
    assert ref.source_range.size == 1
    assert ref.decode_target(b'\x02', 128) == FileOffset(24)
    with pytest.raises(LayoutError):
        ref.decode_target(b'\x02\0', 128)
    with pytest.raises(LayoutError, match='read-only'):
        ref.encoding.encode(FileOffset(24), ref.source, 128)
