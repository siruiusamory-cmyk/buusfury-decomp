"""Command-line interface for safe Webfoot ROM research."""

from __future__ import annotations

import argparse
import json
from importlib import resources
from pathlib import Path
import sys

from .analysis.map_entry_pointers import (
    MapEntryPointerCensus,
    census_map_entry_pointers,
)
from .analysis.variation_arrays import (
    VariationArrayFirstWordCensus,
    census_variation_array_first_words,
    find_first_word_observations,
)
from .gba_header import GbaHeaderError
from .formats.map_entry import (
    MAP_ENTRY_SIZE,
    MapEntryError,
    MapEntryValidationResult,
    validate_map_entry_round_trips,
)
from .profile import ProfileConfigError, RomProfileCatalog, VerificationStatus
from .rom import RomIdentification, RomReadError, identify_rom


def development_profile_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "roms.yaml"


def load_catalog(profile_path: Path | None) -> RomProfileCatalog:
    if profile_path is not None:
        return RomProfileCatalog.load(profile_path)

    development_path = development_profile_path()
    if development_path.is_file():
        return RomProfileCatalog.load(development_path)

    packaged = resources.files("tools.webfoot.data").joinpath("roms.yaml")
    return RomProfileCatalog.loads(
        packaged.read_text(encoding="utf-8"),
        source="packaged tools.webfoot.data/roms.yaml",
    )


def _parse_u32(value: str) -> int:
    try:
        parsed = int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"expected a 32-bit integer, got {value!r}"
        ) from exc
    if not 0 <= parsed <= 0xFFFFFFFF:
        raise argparse.ArgumentTypeError(
            f"expected a 32-bit integer, got {value!r}"
        )
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="webfoot")
    parser.add_argument(
        "--profiles",
        type=Path,
        default=None,
        help="ROM profile YAML (default: project config or packaged catalog)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("relocation-proof", help="validate synthetic relocation and print JSON; no ROM I/O")
    identify = subparsers.add_parser("identify", help="hash and identify a local GBA ROM")
    identify.add_argument("rom", type=Path)
    validate = subparsers.add_parser(
        "validate-map-entries",
        help="validate every configured Buu's Fury MapEntry round trip",
    )
    validate.add_argument("rom", type=Path)
    map_entries = subparsers.add_parser(
        "map-entries",
        help="read-only MapEntry research commands",
    )
    map_entry_commands = map_entries.add_subparsers(
        dest="map_entries_command", required=True
    )
    pointer_census = map_entry_commands.add_parser(
        "pointer-census",
        help="classify and summarize raw pointer-labelled fields",
    )
    pointer_census.add_argument("rom", type=Path)
    variation_arrays = subparsers.add_parser(
        "variation-arrays",
        help="read-only variation-array research commands",
    )
    variation_commands = variation_arrays.add_subparsers(
        dest="variation_arrays_command", required=True
    )
    first_word_census = variation_commands.add_parser(
        "first-word-census",
        help="read and summarize exactly the first u32 at each target",
    )
    first_word_census.add_argument("rom", type=Path)
    find_first_word = variation_commands.add_parser(
        "find-first-word",
        help="find MapEntries with an exact observed first-word value",
    )
    find_first_word.add_argument("rom", type=Path)
    find_first_word.add_argument("value", type=_parse_u32)
    return parser


def _print_identification(identification: RomIdentification) -> None:
    header = identification.header
    match = identification.profile_match
    checksum_status = "VALID" if header.checksum_valid else "INVALID"
    header_status = "VALID" if header.basic_valid else "INVALID"

    print("ROM Identification")
    print("------------------")
    print()
    print(f"File: {identification.path}")
    print(f"Size: {identification.size} bytes")
    print()
    print(f"CRC32:  {identification.hashes.crc32.upper()}")
    print(f"MD5:    {identification.hashes.md5}")
    print(f"SHA1:   {identification.hashes.sha1}")
    print(f"SHA256: {identification.hashes.sha256}")
    print()
    print(f"GBA Title: {header.title}")
    print(f"Game Code: {header.game_code}")
    print(f"Maker Code: {header.maker_code}")
    print(f"Revision: {header.software_version}")
    print(
        f"Header Checksum: 0x{header.header_checksum:02X} "
        f"(calculated 0x{header.calculated_checksum:02X}, {checksum_status})"
    )
    print(f"Basic Header: {header_status}")
    print()
    print("Profile:")
    print(match.profile.id if match.profile is not None else "NONE")
    print()
    print("Status:")
    print(match.status.value)
    print(f"Reason: {match.reason}")
    for mismatch in match.mismatches:
        print(f"Conflict: {mismatch}")


def _print_map_entry_validation(result: MapEntryValidationResult) -> None:
    table = result.table
    match = table.identification.profile_match
    profile_id = match.profile.id if match.profile is not None else "NONE"
    print("Buu's Fury MapEntry Validation")
    print("--------------------------------")
    print()
    print(f"Profile: {profile_id}")
    print(f"Table GBA address: 0x{table.table_address.raw:08X}")
    print(f"Table file offset: 0x{table.table_offset:08X}")
    print(f"Record size: 0x{MAP_ENTRY_SIZE:X}")
    print(f"Entries parsed: {len(table.records)}")
    print(f"Entries serialized: {result.serialized_count}")
    print(f"Round-trip failures: {len(result.mismatches)}")
    print(f"Byte mismatches: {result.byte_mismatch_count}")
    for mismatch in result.mismatches:
        print(
            f"Mismatch: index {mismatch.index}, file 0x{mismatch.file_offset:08X}, "
            f"record +0x{mismatch.record_byte_offset:02X}"
        )
    print()
    print("RESULT:")
    print("PASS" if result.passed else "FAIL")


def _format_optional_address(value: int | None) -> str:
    return "-" if value is None else f"0x{value:08X}"


def _print_map_entry_pointer_census(census: MapEntryPointerCensus) -> None:
    print("Buu's Fury MapEntry Pointer-Field Census")
    print("------------------------------------------")
    print()
    print(f"Profile: {census.profile_id}")
    print(f"MapEntries analyzed: {census.entry_count}")
    print(f"Pointer fields analyzed: {census.pointer_field_count}")
    print(f"Total observations: {census.total_observation_count}")
    print(f"Null: {census.null_count}")
    print(f"Valid ROM addresses: {census.valid_rom_count}")
    print(f"Out of range: {census.out_of_range_count}")
    print()
    print(
        f"{'Field':32} {'Null':>5} {'Valid':>5} {'OOR':>5} "
        f"{'A2':>5} {'A4':>5} {'Unique':>6} {'Dup':>5}"
    )
    for stats in census.field_stats:
        print(
            f"{stats.field_name:32} {stats.null_count:5} "
            f"{stats.valid_rom_count:5} {stats.out_of_range_count:5} "
            f"{stats.aligned_2_count:5} {stats.aligned_4_count:5} "
            f"{stats.unique_valid_target_count:6} "
            f"{stats.duplicate_reference_count:5}"
        )
    print()
    print("Valid target ranges")
    print(f"{'Field':32} {'Minimum GBA':>12} {'Maximum GBA':>12}")
    for stats in census.field_stats:
        print(
            f"{stats.field_name:32} "
            f"{_format_optional_address(stats.minimum_gba_address):>12} "
            f"{_format_optional_address(stats.maximum_gba_address):>12}"
        )
    print()
    print("Count / pointer correlation")
    print(
        f"{'Pointer field':32} {'0/null':>7} {'0/non':>7} "
        f"{'>0/null':>7} {'>0/valid':>8} {'>0/OOR':>7}"
    )
    for correlation in census.correlations:
        print(
            f"{correlation.pointer_field_name:32} "
            f"{correlation.count_zero_pointer_null:7} "
            f"{correlation.count_zero_pointer_non_null:7} "
            f"{correlation.count_positive_pointer_null:7} "
            f"{correlation.count_positive_pointer_valid:8} "
            f"{correlation.count_positive_pointer_out_of_range:7}"
        )
    print()
    print("RESULT:")
    print("COMPLETE")


def _format_signed_hex(value: int) -> str:
    sign = "-" if value < 0 else "+"
    return f"{sign}0x{abs(value):X}"


def _print_variation_array_first_word_census(
    census: VariationArrayFirstWordCensus,
) -> None:
    print("Buu's Fury Variation-Array First-Word Census")
    print("---------------------------------------------")
    print()
    print(f"Profile: {census.profile_id}")
    print(f"MapEntries: {census.pointer_count}")
    print(f"Valid source pointers: {census.source_valid_address_count}")
    print(f"Null source pointers: {census.source_null_count}")
    print(f"Out-of-range source pointers: {census.source_out_of_range_count}")
    print(f"Unique valid source pointers: {census.unique_valid_source_address_count}")
    print(f"Pointers validated: {census.successful_read_count}")
    print(f"Words read: {census.successful_read_count}")
    print(f"Bounds failures: {census.bounds_failure_count}")
    print()
    print(f"Zero: {census.zero_count}")
    print(f"Nonzero: {census.nonzero_count}")
    print(f"Unique values: {census.unique_value_count}")
    print(f"Duplicate references: {census.duplicate_reference_count}")
    print(f"Repeated values: {census.repeated_value_count}")
    print(f"Minimum raw value: {_format_optional_address(census.minimum_raw_value)}")
    print(f"Maximum raw value: {_format_optional_address(census.maximum_raw_value)}")
    print()
    print(f"ROM-address-shaped: {census.rom_address_shaped_count}")
    print(f"Non-ROM values: {census.non_rom_value_count}")
    print(f"Odd nonzero values: {census.odd_count}")
    print(f"2-byte aligned nonzero values: {census.aligned_2_count}")
    print(f"4-byte aligned nonzero values: {census.aligned_4_count}")
    print()
    ordering = census.ordering
    print("Source address ordering")
    print(f"Unique source addresses: {ordering.unique_address_count}")
    print(f"Strictly increasing: {'YES' if ordering.strictly_increasing else 'NO'}")
    print(f"Increases: {ordering.increase_count}")
    print(f"Decreases: {ordering.decrease_count}")
    print(f"Equal: {ordering.equal_count}")
    print(
        "Positive delta range: "
        f"{_format_optional_address(ordering.minimum_positive_delta)} .. "
        f"{_format_optional_address(ordering.maximum_positive_delta)}"
    )
    if ordering.common_deltas:
        common = ", ".join(
            f"{_format_signed_hex(item.raw_value)} x{item.count}"
            for item in ordering.common_deltas
        )
        print(f"Common deltas: {common}")
    print()
    print("Duplicate-value metadata correlation")
    print(f"{'Raw metadata field':18} {'Groups':>7} {'Same':>7} {'Vary':>7}")
    for correlation in census.correlations:
        print(
            f"{correlation.field_name:18} "
            f"{correlation.duplicate_first_word_group_count:7} "
            f"{correlation.constant_metadata_group_count:7} "
            f"{correlation.varying_metadata_group_count:7}"
        )
    if census.most_frequent_values:
        print()
        print("Most frequent raw values")
        for item in census.most_frequent_values:
            print(f"0x{item.raw_value:08X}: {item.count}")
    for failure in census.failures:
        print(
            f"Failure: entry {failure.map_entry_index}, "
            f"source 0x{failure.source_pointer_raw:08X}: {failure.reason}"
        )
    print()
    print("RESULT:")
    print("COMPLETE" if not census.failures else "INCOMPLETE")


def _print_first_word_matches(
    census: VariationArrayFirstWordCensus,
    first_word_raw: int,
) -> None:
    matches = find_first_word_observations(census, first_word_raw)
    print("Buu's Fury Variation-Array First-Word Lookup")
    print("---------------------------------------------")
    print()
    print(f"Profile: {census.profile_id}")
    print(f"First word: 0x{first_word_raw:08X}")
    print(f"Matches: {len(matches)}")
    print()
    print(
        f"{'Index':>5} {'Source':>10} {'Output':>6} "
        f"{'Zone':>4} {'Area':>4} {'Variation':>9}"
    )
    for item in matches:
        print(
            f"{item.map_entry_index:5} 0x{item.source_pointer_raw:08X} "
            f"{item.output_raw:6} {item.zone_raw:4} "
            f"{item.area_raw:4} {item.variation_raw:9}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "relocation-proof":
        from .relocation_proof import synthetic_relocation_proof
        print(json.dumps(synthetic_relocation_proof().to_json(), indent=2, sort_keys=True))
        return 0

    try:
        catalog = load_catalog(args.profiles)
        if args.command == "identify":
            identification = identify_rom(args.rom, catalog)
        elif args.command == "validate-map-entries":
            validation = validate_map_entry_round_trips(args.rom, catalog)
        elif args.command == "map-entries":
            census = census_map_entry_pointers(args.rom, catalog)
        else:
            variation_census = census_variation_array_first_words(args.rom, catalog)
    except (
        ProfileConfigError,
        GbaHeaderError,
        MapEntryError,
        RomReadError,
        OSError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.command == "validate-map-entries":
        _print_map_entry_validation(validation)
        return 0 if validation.passed else 2
    if args.command == "map-entries":
        _print_map_entry_pointer_census(census)
        return 0
    if args.command == "variation-arrays":
        if args.variation_arrays_command == "find-first-word":
            _print_first_word_matches(variation_census, args.value)
        else:
            _print_variation_array_first_word_census(variation_census)
        return 0 if not variation_census.failures else 2

    _print_identification(identification)
    if identification.profile_match.status is VerificationStatus.VERIFIED:
        return 0
    if identification.profile_match.status is VerificationStatus.UNKNOWN:
        return 1
    return 2
