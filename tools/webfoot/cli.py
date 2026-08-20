"""Command-line interface for safe Webfoot ROM research."""

from __future__ import annotations

import argparse
from importlib import resources
from pathlib import Path
import sys

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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.profiles)
        if args.command == "identify":
            identification = identify_rom(args.rom, catalog)
        else:
            validation = validate_map_entry_round_trips(args.rom, catalog)
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

    _print_identification(identification)
    if identification.profile_match.status is VerificationStatus.VERIFIED:
        return 0
    if identification.profile_match.status is VerificationStatus.UNKNOWN:
        return 1
    return 2
