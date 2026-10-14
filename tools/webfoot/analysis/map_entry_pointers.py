
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence

from ..binary import BinaryAddressError, GbaRomAddress, UINT32_MAX
from ..formats.map_entry import (
    MAP_ENTRY_LAYOUT,
    MapEntry,
    MapEntryError,
    read_map_entry_table,
)
from ..profile import RomProfileCatalog


DEFAULT_REGION_SIZE = 0x10000


class PointerCensusError(MapEntryError):
    """Raised when pointer-census inputs are internally inconsistent."""


class PointerClassification(str, Enum):
    NULL = "NULL"
    VALID_ROM_ADDRESS = "VALID_ROM_ADDRESS"
    OUT_OF_RANGE = "OUT_OF_RANGE"


@dataclass(frozen=True, slots=True)
class PointerCandidateField:
    field_name: str
    count_field_name: str | None = None


POINTER_CANDIDATE_FIELDS = (
    PointerCandidateField("triggers_pointer_raw", "trigger_count_raw"),
    PointerCandidateField("scripts_pointer_raw", "script_count_raw"),
    PointerCandidateField("items_pointer_raw", "item_count_raw"),
    PointerCandidateField("objects_pointer_raw", "object_count_raw"),
    PointerCandidateField("npcs_pointer_raw", "npc_count_raw"),
    PointerCandidateField("variation_script_pointer_raw"),
    PointerCandidateField("variation_array_pointer_raw"),
    PointerCandidateField("entry_script_pointer_raw"),
    PointerCandidateField("exit_script_pointer_raw"),
)


@dataclass(frozen=True, slots=True)
class PointerObservation:
    entry_index: int
    field_name: str
    raw_value: int
    classification: PointerClassification
    file_offset: int | None
    aligned_2: bool
    aligned_4: bool

    @property
    def gba_address(self) -> GbaRomAddress | None:
        if self.classification is not PointerClassification.VALID_ROM_ADDRESS:
            return None
        return GbaRomAddress(self.raw_value)


@dataclass(frozen=True, slots=True)
class TargetFrequency:
    raw_value: int
    reference_count: int


@dataclass(frozen=True, slots=True)
class RegionFrequency:
    start_file_offset: int
    reference_count: int
    unique_target_count: int


@dataclass(frozen=True, slots=True)
class PointerFieldStats:
    field_name: str
    total_count: int
    null_count: int
    valid_rom_count: int
    out_of_range_count: int
    aligned_2_count: int
    aligned_4_count: int
    unique_valid_target_count: int
    duplicate_reference_count: int
    repeated_target_count: int
    minimum_gba_address: int | None
    maximum_gba_address: int | None
    minimum_file_offset: int | None
    maximum_file_offset: int | None
    most_frequent_targets: tuple[TargetFrequency, ...]
    regions: tuple[RegionFrequency, ...]


@dataclass(frozen=True, slots=True)
class CountPointerCorrelation:
    count_field_name: str
    pointer_field_name: str
    count_zero_pointer_null: int
    count_zero_pointer_non_null: int
    count_positive_pointer_null: int
    count_positive_pointer_valid: int
    count_positive_pointer_out_of_range: int

    @property
    def total_count(self) -> int:
        return (
            self.count_zero_pointer_null
            + self.count_zero_pointer_non_null
            + self.count_positive_pointer_null
            + self.count_positive_pointer_valid
            + self.count_positive_pointer_out_of_range
        )


@dataclass(frozen=True, slots=True)
class MapEntryPointerCensus:
    profile_id: str
    rom_size: int
    entry_count: int
    region_size: int
    observations: tuple[PointerObservation, ...]
    field_stats: tuple[PointerFieldStats, ...]
    correlations: tuple[CountPointerCorrelation, ...]

    @property
    def pointer_field_count(self) -> int:
        return len(self.field_stats)

    @property
    def total_observation_count(self) -> int:
        return len(self.observations)

    @property
    def null_count(self) -> int:
        return sum(item.null_count for item in self.field_stats)

    @property
    def valid_rom_count(self) -> int:
        return sum(item.valid_rom_count for item in self.field_stats)

    @property
    def out_of_range_count(self) -> int:
        return sum(item.out_of_range_count for item in self.field_stats)


def _validate_candidate_fields(
    candidates: Sequence[PointerCandidateField],
) -> None:
    layout = {item.name: item for item in MAP_ENTRY_LAYOUT}
    seen = set()
    for candidate in candidates:
        if candidate.field_name in seen:
            raise PointerCensusError(
                f"duplicate pointer candidate field: {candidate.field_name}"
            )
        seen.add(candidate.field_name)
        field = layout.get(candidate.field_name)
        if field is None or field.width != 4:
            raise PointerCensusError(
                f"pointer candidate is not a 32-bit MapEntry field: {candidate.field_name}"
            )
        if candidate.count_field_name is not None:
            count_field = layout.get(candidate.count_field_name)
            if count_field is None or count_field.width != 1:
                raise PointerCensusError(
                    "paired count is not an 8-bit MapEntry field: "
                    f"{candidate.count_field_name}"
                )


def _observe(
    entry_index: int,
    field_name: str,
    raw_value: int,
    rom_size: int,
) -> PointerObservation:
    if type(raw_value) is not int or not 0 <= raw_value <= UINT32_MAX:
        raise PointerCensusError(
            f"{field_name} in entry {entry_index} is not a raw 32-bit value"
        )
    if raw_value == 0:
        return PointerObservation(
            entry_index=entry_index,
            field_name=field_name,
            raw_value=raw_value,
            classification=PointerClassification.NULL,
            file_offset=None,
            aligned_2=False,
            aligned_4=False,
        )

    try:
        file_offset = GbaRomAddress(raw_value).to_file_offset(rom_size)
    except BinaryAddressError:
        return PointerObservation(
            entry_index=entry_index,
            field_name=field_name,
            raw_value=raw_value,
            classification=PointerClassification.OUT_OF_RANGE,
            file_offset=None,
            aligned_2=False,
            aligned_4=False,
        )
    return PointerObservation(
        entry_index=entry_index,
        field_name=field_name,
        raw_value=raw_value,
        classification=PointerClassification.VALID_ROM_ADDRESS,
        file_offset=file_offset,
        aligned_2=raw_value % 2 == 0,
        aligned_4=raw_value % 4 == 0,
    )


def _field_stats(
    field_name: str,
    observations: Sequence[PointerObservation],
    region_size: int,
) -> PointerFieldStats:
    null_count = sum(
        item.classification is PointerClassification.NULL for item in observations
    )
    valid = tuple(
        item
        for item in observations
        if item.classification is PointerClassification.VALID_ROM_ADDRESS
    )
    out_of_range_count = sum(
        item.classification is PointerClassification.OUT_OF_RANGE
        for item in observations
    )
    frequencies = Counter(item.raw_value for item in valid)
    ordered_frequencies = sorted(
        frequencies.items(), key=lambda item: (-item[1], item[0])
    )
    most_frequent = tuple(
        TargetFrequency(raw_value=raw_value, reference_count=count)
        for raw_value, count in ordered_frequencies[:3]
    )

    region_references = Counter()
    region_targets: dict[int, set[int]] = {}
    for item in valid:
        assert item.file_offset is not None
        start = (item.file_offset // region_size) * region_size
        region_references[start] += 1
        region_targets.setdefault(start, set()).add(item.raw_value)
    regions = tuple(
        RegionFrequency(
            start_file_offset=start,
            reference_count=region_references[start],
            unique_target_count=len(region_targets[start]),
        )
        for start in sorted(region_references)
    )

    valid_addresses = tuple(item.raw_value for item in valid)
    valid_offsets = tuple(
        item.file_offset for item in valid if item.file_offset is not None
    )
    unique_count = len(frequencies)
    return PointerFieldStats(
        field_name=field_name,
        total_count=len(observations),
        null_count=null_count,
        valid_rom_count=len(valid),
        out_of_range_count=out_of_range_count,
        aligned_2_count=sum(item.aligned_2 for item in valid),
        aligned_4_count=sum(item.aligned_4 for item in valid),
        unique_valid_target_count=unique_count,
        duplicate_reference_count=len(valid) - unique_count,
        repeated_target_count=sum(count > 1 for count in frequencies.values()),
        minimum_gba_address=min(valid_addresses) if valid_addresses else None,
        maximum_gba_address=max(valid_addresses) if valid_addresses else None,
        minimum_file_offset=min(valid_offsets) if valid_offsets else None,
        maximum_file_offset=max(valid_offsets) if valid_offsets else None,
        most_frequent_targets=most_frequent,
        regions=regions,
    )


def _correlation(
    entries: Sequence[MapEntry],
    candidate: PointerCandidateField,
    observations: Sequence[PointerObservation],
) -> CountPointerCorrelation:
    assert candidate.count_field_name is not None
    zero_null = 0
    zero_non_null = 0
    positive_null = 0
    positive_valid = 0
    positive_out_of_range = 0
    for entry, observation in zip(entries, observations, strict=True):
        count = getattr(entry, candidate.count_field_name)
        if type(count) is not int or not 0 <= count <= 0xFF:
            raise PointerCensusError(
                f"{candidate.count_field_name} is not a raw 8-bit value"
            )
        if count == 0:
            if observation.classification is PointerClassification.NULL:
                zero_null += 1
            else:
                zero_non_null += 1
        elif observation.classification is PointerClassification.NULL:
            positive_null += 1
        elif observation.classification is PointerClassification.VALID_ROM_ADDRESS:
            positive_valid += 1
        else:
            positive_out_of_range += 1
    return CountPointerCorrelation(
        count_field_name=candidate.count_field_name,
        pointer_field_name=candidate.field_name,
        count_zero_pointer_null=zero_null,
        count_zero_pointer_non_null=zero_non_null,
        count_positive_pointer_null=positive_null,
        count_positive_pointer_valid=positive_valid,
        count_positive_pointer_out_of_range=positive_out_of_range,
    )


def analyze_map_entry_pointers(
    entries: Sequence[MapEntry],
    *,
    rom_size: int,
    profile_id: str = "<synthetic>",
    candidates: Sequence[PointerCandidateField] = POINTER_CANDIDATE_FIELDS,
    region_size: int = DEFAULT_REGION_SIZE,
) -> MapEntryPointerCensus:
    """Classify raw candidates without reading any pointed-to target bytes."""
    if type(rom_size) is not int or rom_size <= 0:
        raise PointerCensusError("ROM size must be a positive integer")
    if type(region_size) is not int or region_size <= 0:
        raise PointerCensusError("region size must be a positive integer")
    if not isinstance(profile_id, str) or not profile_id:
        raise PointerCensusError("profile id must be a non-empty string")
    _validate_candidate_fields(candidates)
    frozen_entries = tuple(entries)
    if not all(isinstance(entry, MapEntry) for entry in frozen_entries):
        raise PointerCensusError("entries must contain only MapEntry values")

    observations = []
    observations_by_field: dict[str, tuple[PointerObservation, ...]] = {}
    for candidate in candidates:
        field_observations = tuple(
            _observe(
                entry_index=index,
                field_name=candidate.field_name,
                raw_value=getattr(entry, candidate.field_name),
                rom_size=rom_size,
            )
            for index, entry in enumerate(frozen_entries)
        )
        observations.extend(field_observations)
        observations_by_field[candidate.field_name] = field_observations

    stats = tuple(
        _field_stats(
            candidate.field_name,
            observations_by_field[candidate.field_name],
            region_size,
        )
        for candidate in candidates
    )
    correlations = tuple(
        _correlation(
            frozen_entries,
            candidate,
            observations_by_field[candidate.field_name],
        )
        for candidate in candidates
        if candidate.count_field_name is not None
    )
    census = MapEntryPointerCensus(
        profile_id=profile_id,
        rom_size=rom_size,
        entry_count=len(frozen_entries),
        region_size=region_size,
        observations=tuple(observations),
        field_stats=stats,
        correlations=correlations,
    )
    if (
        census.null_count + census.valid_rom_count + census.out_of_range_count
        != census.total_observation_count
    ):
        raise AssertionError("pointer census classification accounting mismatch")
    return census


def census_map_entry_pointers(
    path: str | Path,
    catalog: RomProfileCatalog,
) -> MapEntryPointerCensus:
    table = read_map_entry_table(path, catalog)
    profile = table.identification.profile_match.profile
    assert profile is not None
    return analyze_map_entry_pointers(
        tuple(record.entry for record in table.records),
        rom_size=table.identification.size,
        profile_id=profile.id,
    )
