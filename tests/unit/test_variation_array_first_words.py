from dataclasses import replace
from io import BytesIO

import pytest

from tools.webfoot.analysis.variation_arrays import (
    FirstWordClassification,
    VariationArrayAnalysisError,
    VariationArrayBoundsError,
    analyze_variation_array_first_words,
    find_first_word_observations,
    read_variation_array_first_word,
)
from tools.webfoot.binary import GBA_ROM_BASE
from tools.webfoot.formats.map_entry import MAP_ENTRY_LAYOUT, MapEntry


ZERO_ENTRY = MapEntry(*([0] * len(MAP_ENTRY_LAYOUT)))


class TrackingBytesIO(BytesIO):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


def entry_at(offset, **metadata):
    return replace(
        ZERO_ENTRY,
        variation_array_pointer_raw=GBA_ROM_BASE + offset,
        **metadata,
    )


def write_u32(buffer, offset, value):
    buffer[offset : offset + 4] = value.to_bytes(4, "little")


def test_reader_accepts_lowest_address_and_decodes_little_endian():
    stream = TrackingBytesIO(bytes.fromhex("78563412") + bytes(12))

    offset, raw = read_variation_array_first_word(
        stream,
        source_pointer_raw=GBA_ROM_BASE,
        rom_size=16,
    )

    assert offset == 0
    assert raw == 0x12345678
    assert stream.read_sizes == [4]


def test_reader_accepts_highest_complete_four_byte_read():
    data = bytearray(16)
    write_u32(data, 12, 0xA1B2C3D4)
    stream = TrackingBytesIO(bytes(data))

    offset, raw = read_variation_array_first_word(
        stream,
        source_pointer_raw=GBA_ROM_BASE + 12,
        rom_size=16,
    )

    assert offset == 12
    assert raw == 0xA1B2C3D4
    assert stream.read_sizes == [4]


def test_reader_rejects_in_range_start_when_four_bytes_cross_end():
    stream = TrackingBytesIO(bytes(16))

    with pytest.raises(VariationArrayBoundsError, match="extends beyond"):
        read_variation_array_first_word(
            stream,
            source_pointer_raw=GBA_ROM_BASE + 13,
            rom_size=16,
        )

    assert stream.read_sizes == []


@pytest.mark.parametrize(
    "raw,message",
    [
        (0, "null"),
        (GBA_ROM_BASE - 1, "not an address"),
        (GBA_ROM_BASE + 16, "outside"),
    ],
)
def test_reader_rejects_null_and_out_of_range_sources_without_reading(raw, message):
    stream = TrackingBytesIO(bytes(16))

    with pytest.raises(VariationArrayBoundsError, match=message):
        read_variation_array_first_word(
            stream,
            source_pointer_raw=raw,
            rom_size=16,
        )

    assert stream.read_sizes == []


def test_reader_reports_short_stream_without_widening_read():
    stream = TrackingBytesIO(bytes(8))

    with pytest.raises(VariationArrayBoundsError, match="short first-word read"):
        read_variation_array_first_word(
            stream,
            source_pointer_raw=GBA_ROM_BASE + 12,
            rom_size=16,
        )

    assert stream.read_sizes == [4]


def test_census_classifies_zero_rom_shaped_and_non_rom_values():
    data = bytearray(0x40)
    write_u32(data, 0x00, 0)
    write_u32(data, 0x04, GBA_ROM_BASE + 0x20)
    write_u32(data, 0x08, 3)
    write_u32(data, 0x0C, 2)
    stream = TrackingBytesIO(bytes(data))

    census = analyze_variation_array_first_words(
        [entry_at(0), entry_at(4), entry_at(8), entry_at(12)],
        stream,
        rom_size=len(data),
    )

    assert [item.classification for item in census.observations] == [
        FirstWordClassification.ZERO,
        FirstWordClassification.ROM_ADDRESS_SHAPED,
        FirstWordClassification.NON_ROM_VALUE,
        FirstWordClassification.NON_ROM_VALUE,
    ]
    assert census.zero_count == 1
    assert census.nonzero_count == 3
    assert census.rom_address_shaped_count == 1
    assert census.non_rom_value_count == 2
    assert census.odd_count == 1
    assert census.aligned_2_count == 2
    assert census.aligned_4_count == 1
    assert stream.read_sizes == [4, 4, 4, 4]


def test_duplicate_and_unique_value_statistics_are_consistent():
    data = bytearray(0x20)
    write_u32(data, 0, 7)
    write_u32(data, 4, 7)
    write_u32(data, 8, 9)

    census = analyze_variation_array_first_words(
        [entry_at(0), entry_at(4), entry_at(8)],
        BytesIO(data),
        rom_size=len(data),
    )

    assert census.unique_value_count == 2
    assert census.duplicate_reference_count == 1
    assert census.repeated_value_count == 1
    assert census.most_frequent_values[0].raw_value == 7
    assert census.most_frequent_values[0].count == 2
    assert census.minimum_raw_value == 7
    assert census.maximum_raw_value == 9


def test_first_word_lookup_returns_all_duplicate_observations_in_entry_order():
    data = bytearray(0x20)
    write_u32(data, 0, 7)
    write_u32(data, 4, 9)
    write_u32(data, 8, 7)
    census = analyze_variation_array_first_words(
        [entry_at(0), entry_at(4), entry_at(8)],
        BytesIO(data),
        rom_size=len(data),
    )

    matches = find_first_word_observations(census, 7)

    assert [item.map_entry_index for item in matches] == [0, 2]
    assert [item.source_pointer_raw for item in matches] == [
        GBA_ROM_BASE,
        GBA_ROM_BASE + 8,
    ]


@pytest.mark.parametrize("value", [-1, 0x1_0000_0000, True, "7"])
def test_first_word_lookup_rejects_non_u32_values(value):
    census = analyze_variation_array_first_words(
        [entry_at(0)], BytesIO(bytes(16)), rom_size=16
    )

    with pytest.raises(VariationArrayAnalysisError, match="raw 32-bit"):
        find_first_word_observations(census, value)


def test_source_address_ordering_retains_signed_deltas():
    data = bytearray(0x40)
    entries = [entry_at(4), entry_at(12), entry_at(8), entry_at(8)]

    census = analyze_variation_array_first_words(
        entries,
        BytesIO(data),
        rom_size=len(data),
    )
    ordering = census.ordering

    assert ordering.address_count == 4
    assert ordering.unique_address_count == 3
    assert ordering.increase_count == 1
    assert ordering.decrease_count == 1
    assert ordering.equal_count == 1
    assert ordering.minimum_positive_delta == 8
    assert ordering.maximum_positive_delta == 8
    assert ordering.minimum_negative_delta == -4
    assert ordering.maximum_negative_delta == -4
    assert not ordering.strictly_increasing
    assert {(item.raw_value, item.count) for item in ordering.common_deltas} == {
        (-4, 1),
        (0, 1),
        (8, 1),
    }


def test_duplicate_value_metadata_correlation_does_not_claim_semantics():
    data = bytearray(0x20)
    write_u32(data, 0, 0x55)
    write_u32(data, 4, 0x55)
    write_u32(data, 8, 0x55)
    entries = [
        entry_at(0, variation_raw=1, area_raw=2),
        entry_at(4, variation_raw=1, area_raw=3),
        entry_at(8, variation_raw=1, area_raw=3),
    ]

    census = analyze_variation_array_first_words(
        entries,
        BytesIO(data),
        rom_size=len(data),
    )
    by_field = {item.field_name: item for item in census.correlations}

    assert by_field["variation_raw"].constant_metadata_group_count == 1
    assert by_field["variation_raw"].varying_metadata_group_count == 0
    assert by_field["area_raw"].constant_metadata_group_count == 0
    assert by_field["area_raw"].varying_metadata_group_count == 1
    assert by_field["area_raw"].unique_pair_count == 2


def test_census_preserves_bounds_failures_and_accounting():
    data = bytes(16)
    census = analyze_variation_array_first_words(
        [
            entry_at(0),
            entry_at(13),
            ZERO_ENTRY,
            replace(
                ZERO_ENTRY,
                variation_array_pointer_raw=GBA_ROM_BASE - 1,
            ),
        ],
        BytesIO(data),
        rom_size=len(data),
    )

    assert census.pointer_count == 4
    assert census.source_valid_address_count == 2
    assert census.source_null_count == 1
    assert census.source_out_of_range_count == 1
    assert census.unique_valid_source_address_count == 2
    assert census.successful_read_count == 1
    assert census.bounds_failure_count == 3
    assert census.successful_read_count + census.bounds_failure_count == 4
    assert [item.map_entry_index for item in census.failures] == [1, 2, 3]
    assert census.ordering.address_count == 4


@pytest.mark.parametrize(
    "entries,rom_size,profile_id,message",
    [
        ([object()], 16, "synthetic", "only MapEntry"),
        ([ZERO_ENTRY], -1, "synthetic", "ROM size"),
        ([ZERO_ENTRY], True, "synthetic", "ROM size"),
        ([ZERO_ENTRY], 16, "", "profile id"),
        (
            [replace(ZERO_ENTRY, variation_array_pointer_raw=True)],
            16,
            "synthetic",
            "raw 32-bit",
        ),
    ],
)
def test_malformed_analysis_inputs_are_rejected(entries, rom_size, profile_id, message):
    with pytest.raises(VariationArrayAnalysisError, match=message):
        analyze_variation_array_first_words(
            entries,
            BytesIO(bytes(16)),
            rom_size=rom_size,
            profile_id=profile_id,
        )
