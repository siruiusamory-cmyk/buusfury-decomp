
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
from typing import BinaryIO, Sequence

from ..binary import BinaryAddressError, GbaRomAddress, UINT32_MAX
from ..formats.map_entry import MapEntry, MapEntryError, read_map_entry_table
from ..hashing import hash_stream
from ..profile import RomProfileCatalog
from ..rom import RomChangedError


FIRST_WORD_SIZE = 4
METADATA_FIELDS = ("output_raw", "zone_raw", "area_raw", "variation_raw")


class VariationArrayAnalysisError(MapEntryError):
    """Raised when a first-word analysis cannot be completed safely."""


class VariationArrayBoundsError(VariationArrayAnalysisError):
    """Raised when a source address cannot supply one complete u32."""


class FirstWordClassification(str, Enum):
    ZERO = "ZERO"
    ROM_ADDRESS_SHAPED = "ROM_ADDRESS_SHAPED"
    NON_ROM_VALUE = "NON_ROM_VALUE"


@dataclass(frozen=True, slots=True)
class VariationArrayFirstWordObservation:
    map_entry_index: int
    source_pointer_raw: int
    source_file_offset: int
    first_word_raw: int
    classification: FirstWordClassification
    output_raw: int
    zone_raw: int
    area_raw: int
    variation_raw: int

    @property
    def odd(self) -> bool:
        return self.first_word_raw != 0 and self.first_word_raw % 2 == 1

    @property
    def aligned_2(self) -> bool:
        return self.first_word_raw != 0 and self.first_word_raw % 2 == 0

    @property
    def aligned_4(self) -> bool:
        return self.first_word_raw != 0 and self.first_word_raw % 4 == 0


@dataclass(frozen=True, slots=True)
class VariationArrayReadFailure:
    map_entry_index: int
    source_pointer_raw: int
    reason: str


@dataclass(frozen=True, slots=True)
class ValueFrequency:
    raw_value: int
    count: int


@dataclass(frozen=True, slots=True)
class SourceAddressOrdering:
    address_count: int
    unique_address_count: int
    increase_count: int
    decrease_count: int
    equal_count: int
    minimum_positive_delta: int | None
    maximum_positive_delta: int | None
    minimum_negative_delta: int | None
    maximum_negative_delta: int | None
    common_deltas: tuple[ValueFrequency, ...]

    @property
    def strictly_increasing(self) -> bool:
        return (
            self.address_count > 1
            and self.increase_count == self.address_count - 1
        )


@dataclass(frozen=True, slots=True)
class MetadataCorrelation:
    field_name: str
    duplicate_first_word_group_count: int
    constant_metadata_group_count: int
    varying_metadata_group_count: int
    unique_pair_count: int


@dataclass(frozen=True, slots=True)
class VariationArrayFirstWordCensus:
    profile_id: str
    rom_size: int
    pointer_count: int
    observations: tuple[VariationArrayFirstWordObservation, ...]
    failures: tuple[VariationArrayReadFailure, ...]
    ordering: SourceAddressOrdering
    correlations: tuple[MetadataCorrelation, ...]
    most_frequent_values: tuple[ValueFrequency, ...]

    @property
    def successful_read_count(self) -> int:
        return len(self.observations)

    @property
    def bounds_failure_count(self) -> int:
        return len(self.failures)

    @property
    def source_null_count(self) -> int:
        return sum(item.source_pointer_raw == 0 for item in self.failures)

    @property
    def source_valid_address_count(self) -> int:
        count = 0
        for raw_value in self._source_values:
            if raw_value == 0:
                continue
            try:
                GbaRomAddress(raw_value).to_file_offset(self.rom_size)
            except BinaryAddressError:
                continue
            count += 1
        return count

    @property
    def source_out_of_range_count(self) -> int:
        return self.pointer_count - self.source_null_count - self.source_valid_address_count

    @property
    def unique_valid_source_address_count(self) -> int:
        valid = set()
        for raw_value in self._source_values:
            if raw_value == 0:
                continue
            try:
                GbaRomAddress(raw_value).to_file_offset(self.rom_size)
            except BinaryAddressError:
                continue
            valid.add(raw_value)
        return len(valid)

    @property
    def _source_values(self) -> tuple[int, ...]:
        indexed = {
            item.map_entry_index: item.source_pointer_raw for item in self.observations
        }
        indexed.update(
            {item.map_entry_index: item.source_pointer_raw for item in self.failures}
        )
        return tuple(indexed[index] for index in range(self.pointer_count))

    @property
    def zero_count(self) -> int:
        return sum(
            item.classification is FirstWordClassification.ZERO
            for item in self.observations
        )

    @property
    def nonzero_count(self) -> int:
        return self.successful_read_count - self.zero_count

    @property
    def rom_address_shaped_count(self) -> int:
        return sum(
            item.classification is FirstWordClassification.ROM_ADDRESS_SHAPED
            for item in self.observations
        )

    @property
    def non_rom_value_count(self) -> int:
        return sum(
            item.classification is FirstWordClassification.NON_ROM_VALUE
            for item in self.observations
        )

    @property
    def unique_value_count(self) -> int:
        return len({item.first_word_raw for item in self.observations})

    @property
    def duplicate_reference_count(self) -> int:
        return self.successful_read_count - self.unique_value_count

    @property
    def repeated_value_count(self) -> int:
        frequencies = Counter(item.first_word_raw for item in self.observations)
        return sum(count > 1 for count in frequencies.values())

    @property
    def minimum_raw_value(self) -> int | None:
        values = tuple(item.first_word_raw for item in self.observations)
        return min(values) if values else None

    @property
    def maximum_raw_value(self) -> int | None:
        values = tuple(item.first_word_raw for item in self.observations)
        return max(values) if values else None

    @property
    def odd_count(self) -> int:
        return sum(item.odd for item in self.observations)

    @property
    def aligned_2_count(self) -> int:
        return sum(item.aligned_2 for item in self.observations)

    @property
    def aligned_4_count(self) -> int:
        return sum(item.aligned_4 for item in self.observations)


def find_first_word_observations(
    census: VariationArrayFirstWordCensus,
    first_word_raw: int,
) -> tuple[VariationArrayFirstWordObservation, ...]:
    """Return census observations whose exact raw first word matches *value*."""
    if not isinstance(census, VariationArrayFirstWordCensus):
        raise VariationArrayAnalysisError(
            "first-word lookup requires a VariationArrayFirstWordCensus"
        )
    if type(first_word_raw) is not int or not 0 <= first_word_raw <= UINT32_MAX:
        raise VariationArrayAnalysisError(
            "first-word lookup value must be a raw 32-bit value"
        )
    return tuple(
        item
        for item in census.observations
        if item.first_word_raw == first_word_raw
    )


def read_variation_array_first_word(
    stream: BinaryIO,
    *,
    source_pointer_raw: int,
    rom_size: int,
) -> tuple[int, int]:
    """Read target[0:4] exactly once and return (file offset, raw LE u32)."""
    if type(source_pointer_raw) is not int or not 0 <= source_pointer_raw <= UINT32_MAX:
        raise VariationArrayBoundsError("source pointer must be a raw 32-bit value")
    if type(rom_size) is not int or rom_size < 0:
        raise VariationArrayBoundsError("ROM size must be a non-negative integer")
    if source_pointer_raw == 0:
        raise VariationArrayBoundsError("source variation-array pointer is null")
    try:
        file_offset = GbaRomAddress(source_pointer_raw).to_file_offset(rom_size)
    except BinaryAddressError as exc:
        raise VariationArrayBoundsError(str(exc)) from exc
    if file_offset > rom_size - FIRST_WORD_SIZE:
        raise VariationArrayBoundsError(
            f"four-byte read at 0x{file_offset:08X} extends beyond the ROM"
        )

    stream.seek(file_offset)
    raw = stream.read(FIRST_WORD_SIZE)
    if len(raw) != FIRST_WORD_SIZE:
        raise VariationArrayBoundsError(
            f"short first-word read at 0x{file_offset:08X}: "
            f"expected {FIRST_WORD_SIZE}, got {len(raw)}"
        )
    return file_offset, int.from_bytes(raw, byteorder="little", signed=False)


def _classify_first_word(raw_value: int, rom_size: int) -> FirstWordClassification:
    if raw_value == 0:
        return FirstWordClassification.ZERO
    try:
        GbaRomAddress(raw_value).to_file_offset(rom_size)
    except BinaryAddressError:
        return FirstWordClassification.NON_ROM_VALUE
    return FirstWordClassification.ROM_ADDRESS_SHAPED


def _source_ordering(
    source_pointer_values: Sequence[int],
) -> SourceAddressOrdering:
    addresses = tuple(source_pointer_values)
    deltas = tuple(current - previous for previous, current in zip(addresses, addresses[1:]))
    positive = tuple(delta for delta in deltas if delta > 0)
    negative = tuple(delta for delta in deltas if delta < 0)
    frequencies = sorted(Counter(deltas).items(), key=lambda item: (-item[1], item[0]))
    return SourceAddressOrdering(
        address_count=len(addresses),
        unique_address_count=len(set(addresses)),
        increase_count=len(positive),
        decrease_count=len(negative),
        equal_count=sum(delta == 0 for delta in deltas),
        minimum_positive_delta=min(positive) if positive else None,
        maximum_positive_delta=max(positive) if positive else None,
        minimum_negative_delta=min(negative) if negative else None,
        maximum_negative_delta=max(negative) if negative else None,
        common_deltas=tuple(
            ValueFrequency(raw_value=delta, count=count)
            for delta, count in frequencies[:5]
        ),
    )


def _metadata_correlations(
    observations: Sequence[VariationArrayFirstWordObservation],
) -> tuple[MetadataCorrelation, ...]:
    frequencies = Counter(item.first_word_raw for item in observations)
    duplicate_values = {value for value, count in frequencies.items() if count > 1}
    result = []
    for field_name in METADATA_FIELDS:
        grouped: dict[int, set[int]] = {}
        for item in observations:
            if item.first_word_raw in duplicate_values:
                grouped.setdefault(item.first_word_raw, set()).add(
                    getattr(item, field_name)
                )
        result.append(
            MetadataCorrelation(
                field_name=field_name,
                duplicate_first_word_group_count=len(grouped),
                constant_metadata_group_count=sum(
                    len(values) == 1 for values in grouped.values()
                ),
                varying_metadata_group_count=sum(
                    len(values) > 1 for values in grouped.values()
                ),
                unique_pair_count=len(
                    {
                        (item.first_word_raw, getattr(item, field_name))
                        for item in observations
                    }
                ),
            )
        )
    return tuple(result)


def analyze_variation_array_first_words(
    entries: Sequence[MapEntry],
    stream: BinaryIO,
    *,
    rom_size: int,
    profile_id: str = "<synthetic>",
) -> VariationArrayFirstWordCensus:
    """Read exactly one target u32 per source pointer and summarize raw values."""
    if type(rom_size) is not int or rom_size < 0:
        raise VariationArrayAnalysisError("ROM size must be a non-negative integer")
    if not isinstance(profile_id, str) or not profile_id:
        raise VariationArrayAnalysisError("profile id must be a non-empty string")
    frozen_entries = tuple(entries)
    if not all(isinstance(entry, MapEntry) for entry in frozen_entries):
        raise VariationArrayAnalysisError("entries must contain only MapEntry values")
    source_pointer_values = tuple(
        entry.variation_array_pointer_raw for entry in frozen_entries
    )
    if not all(
        type(raw_value) is int and 0 <= raw_value <= UINT32_MAX
        for raw_value in source_pointer_values
    ):
        raise VariationArrayAnalysisError(
            "variation-array sources must be raw 32-bit values"
        )

    observations = []
    failures = []
    for index, entry in enumerate(frozen_entries):
        source_pointer_raw = entry.variation_array_pointer_raw
        try:
            source_file_offset, first_word_raw = read_variation_array_first_word(
                stream,
                source_pointer_raw=source_pointer_raw,
                rom_size=rom_size,
            )
        except VariationArrayBoundsError as exc:
            failures.append(
                VariationArrayReadFailure(
                    map_entry_index=index,
                    source_pointer_raw=source_pointer_raw,
                    reason=str(exc),
                )
            )
            continue
        observations.append(
            VariationArrayFirstWordObservation(
                map_entry_index=index,
                source_pointer_raw=source_pointer_raw,
                source_file_offset=source_file_offset,
                first_word_raw=first_word_raw,
                classification=_classify_first_word(first_word_raw, rom_size),
                output_raw=entry.output_raw,
                zone_raw=entry.zone_raw,
                area_raw=entry.area_raw,
                variation_raw=entry.variation_raw,
            )
        )

    frequencies = sorted(
        Counter(item.first_word_raw for item in observations).items(),
        key=lambda item: (-item[1], item[0]),
    )
    census = VariationArrayFirstWordCensus(
        profile_id=profile_id,
        rom_size=rom_size,
        pointer_count=len(frozen_entries),
        observations=tuple(observations),
        failures=tuple(failures),
        ordering=_source_ordering(source_pointer_values),
        correlations=_metadata_correlations(observations),
        most_frequent_values=tuple(
            ValueFrequency(raw_value=value, count=count)
            for value, count in frequencies[:5]
        ),
    )
    if census.successful_read_count + census.bounds_failure_count != census.pointer_count:
        raise AssertionError("variation-array read accounting mismatch")
    if census.zero_count + census.nonzero_count != census.successful_read_count:
        raise AssertionError("first-word zero accounting mismatch")
    if (
        census.zero_count
        + census.rom_address_shaped_count
        + census.non_rom_value_count
        != census.successful_read_count
    ):
        raise AssertionError("first-word classification accounting mismatch")
    return census


def _file_identity(stat_result: os.stat_result) -> tuple[int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
    )


def census_variation_array_first_words(
    path: str | Path,
    catalog: RomProfileCatalog,
) -> VariationArrayFirstWordCensus:
    """Run the trusted-profile census through one stable read-only target handle."""
    source = Path(path)
    table = read_map_entry_table(source, catalog)
    profile = table.identification.profile_match.profile
    assert profile is not None

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, _ = hash_stream(stream)
        after_hash = os.fstat(stream.fileno())
        if hashes != table.identification.hashes:
            raise RomChangedError(f"ROM identity changed before first-word reads: {source}")
        census = analyze_variation_array_first_words(
            tuple(record.entry for record in table.records),
            stream,
            rom_size=before.st_size,
            profile_id=profile.id,
        )
        after_read = os.fstat(stream.fileno())

    path_after = source.stat()
    identity = _file_identity(before)
    if (
        identity != _file_identity(after_hash)
        or identity != _file_identity(after_read)
        or identity != _file_identity(path_after)
    ):
        raise RomChangedError(f"ROM changed while first words were read: {source}")
    return census
