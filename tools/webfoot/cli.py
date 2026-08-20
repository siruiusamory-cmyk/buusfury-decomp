"""Command-line interface for safe Webfoot ROM research."""

from __future__ import annotations

import argparse
from importlib import resources
from pathlib import Path
import sys

from .analysis.map_entry_pointers import (
    MapEntryPointerCensus,
    census_map_entry_pointers,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="webfoot")
    parser.add_argument(
        "--profiles",
        type=Path,
        default=None,
        help="ROM profile YAML (default: project config or packaged catalog)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.profiles)
        if args.command == "identify":
            identification = identify_rom(args.rom, catalog)
        elif args.command == "validate-map-entries":
            validation = validate_map_entry_round_trips(args.rom, catalog)
        else:
            census = census_map_entry_pointers(args.rom, catalog)
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

    _print_identification(identification)
    if identification.profile_match.status is VerificationStatus.VERIFIED:
        return 0
    if identification.profile_match.status is VerificationStatus.UNKNOWN:
        return 1
    return 2
