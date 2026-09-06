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
from .build import (
    BuildError,
    BuildResult,
    ValidationReport,
    build_project,
    extract_project,
    validate_project,
)
from .profile import ProfileConfigError, RomProfileCatalog, VerificationStatus
from .project import ProjectError
from .rom import RomIdentification, RomReadError, identify_rom
from .formats.stat_tables import StatEncodeError, StatIdentity
from .formats.text_tables import TextCodecError, TextIdentity, encode_string
from .stats import StatTableError, load_stat_tables
from .text import TextTableError, load_text_strings
from .maps import (
    MAP_FIELDS,
    MapError,
    MapIdentity,
    PlacementIdentity,
    load_maps,
)
from .write import WriteError, emit_image


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

    stats = subparsers.add_parser(
        "stats",
        help="read, validate and edit the static stat tables",
    )
    stats_commands = stats.add_subparsers(dest="stats_command", required=True)

    stats_list = stats_commands.add_parser(
        "list", help="list stat records with identity, alias and location"
    )
    stats_list.add_argument("rom", type=Path)
    stats_list.add_argument(
        "--kind", choices=("enemy", "character", "all"), default="all"
    )

    stats_round_trip = stats_commands.add_parser(
        "validate-round-trip",
        help="prove every stat record re-serializes byte-identically",
    )
    stats_round_trip.add_argument("rom", type=Path)

    stats_set = stats_commands.add_parser(
        "set",
        help="edit one stat field and emit a NEW ROM image plus a manifest",
    )
    stats_set.add_argument("rom", type=Path)
    stats_set.add_argument(
        "identity",
        help="record identity, e.g. enemy:434 or character:0",
    )
    stats_set.add_argument("field")
    stats_set.add_argument("value", type=int)
    stats_set.add_argument(
        "--output", type=Path, required=True, help="output ROM path (must not exist)"
    )
    stats_set.add_argument(
        "--manifest", type=Path, default=None, help="write the change manifest here"
    )

    # TOOLKIT-004. Mirrors `stats`: list, prove the round trip, edit one entry.
    # Deliberately not a research dump - there is no "scan for strings" command,
    # because enumeration comes from the verified pointer table and a heuristic
    # scan would produce a different, unreproducible answer.
    text = subparsers.add_parser(
        "text",
        help="read, validate and edit the string table",
    )
    text_commands = text.add_subparsers(dest="text_command", required=True)

    text_list = text_commands.add_parser(
        "list", help="list strings with identity, location and text"
    )
    text_list.add_argument("rom", type=Path)
    text_list.add_argument(
        "--contains",
        default=None,
        help="only strings containing this substring (case-sensitive)",
    )
    text_list.add_argument(
        "--limit", type=int, default=None, help="stop after this many strings"
    )

    text_show = text_commands.add_parser(
        "show", help="print one string's text, identity and location"
    )
    text_show.add_argument("rom", type=Path)
    text_show.add_argument("identity", help="string identity, e.g. text:0010")

    text_round_trip = text_commands.add_parser(
        "validate-round-trip",
        help="prove every string re-serializes byte-identically",
    )
    text_round_trip.add_argument("rom", type=Path)

    text_set = text_commands.add_parser(
        "set",
        help="edit one string and emit a NEW ROM image plus a manifest",
    )
    text_set.add_argument("rom", type=Path)
    text_set.add_argument("identity", help="string identity, e.g. text:0010")
    text_set.add_argument(
        "value",
        help='replacement text; "{08:XX}" is a control code, "{{" a literal brace',
    )
    text_set.add_argument(
        "--output", type=Path, required=True, help="output ROM path (must not exist)"
    )
    text_set.add_argument(
        "--manifest", type=Path, default=None, help="write the change manifest here"
    )

    # TOOLKIT-007. Maps are read and inspected here; they are *edited* through
    # the project files, because a map edit is one field among 452 records and
    # belongs in reviewable source rather than in a shell command. No command
    # below takes or prints a raw address as its normal interface.
    maps_parser = subparsers.add_parser(
        "map",
        help="list and inspect map records, slot extents and connections",
    )
    map_commands = maps_parser.add_subparsers(dest="map_command", required=True)

    map_list = map_commands.add_parser(
        "list", help="list maps with identity, editable fields and slot shape"
    )
    map_list.add_argument("rom", type=Path)
    map_list.add_argument(
        "--limit", type=int, default=None, help="stop after this many maps"
    )
    map_list.add_argument(
        "--typed-only",
        action="store_true",
        help="only maps whose slot extent is fully typed",
    )

    map_show = map_commands.add_parser(
        "show", help="print one map's fields, slot extent and classification"
    )
    map_show.add_argument("rom", type=Path)
    map_show.add_argument("identity", help="map identity, e.g. map:0039")

    map_connections = map_commands.add_parser(
        "connections",
        help="print the verified connections a map declares",
    )
    map_connections.add_argument("rom", type=Path)
    map_connections.add_argument(
        "identity", nargs="?", default=None, help="map identity; omit for all"
    )

    map_placements_parser = map_commands.add_parser(
        "placements",
        help="list the factory-led placement records a map owns",
    )
    map_placements_parser.add_argument("rom", type=Path)
    map_placements_parser.add_argument(
        "identity", nargs="?", default=None, help="map identity; omit for all"
    )
    map_placements_parser.add_argument("--limit", type=int, default=40)

    map_placement_show = map_commands.add_parser(
        "placement",
        help="print one placement record's fields",
    )
    map_placement_show.add_argument("rom", type=Path)
    map_placement_show.add_argument(
        "identity", help="placement identity, e.g. map:0010/placement:0000"
    )

    map_round_trip = map_commands.add_parser(
        "validate-round-trip",
        help="prove every map record and slot extent re-serializes byte-identically",
    )
    map_round_trip.add_argument("rom", type=Path)

    # TOOLKIT-002. These call the same project/build APIs a GUI or automation
    # would; the CLI parses arguments and formats output and does nothing else.
    extract = subparsers.add_parser(
        "extract",
        help="extract a verified ROM into a deterministic project directory",
    )
    extract.add_argument("rom", type=Path)
    extract.add_argument("project", type=Path)
    extract.add_argument(
        "--name",
        default=None,
        help="project name recorded in project.toml (default: the profile id)",
    )

    validate_project_parser = subparsers.add_parser(
        "validate",
        help="validate a project against its base ROM, writing nothing",
    )
    validate_project_parser.add_argument("project", type=Path)
    validate_project_parser.add_argument("--rom", type=Path, required=True)

    build = subparsers.add_parser(
        "build",
        help="build a project into a NEW ROM image; the base ROM is never modified",
    )
    build.add_argument("project", type=Path)
    build.add_argument("--rom", type=Path, required=True)
    build.add_argument(
        "--output", type=Path, required=True, help="output ROM path (must not exist)"
    )
    build.add_argument(
        "--manifest", type=Path, default=None, help="write the build manifest here"
    )
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



def _parse_identity(text: str) -> StatIdentity:
    kind, _, key = text.partition(":")
    if not key:
        raise StatTableError(
            f"identity must look like 'enemy:434' or 'character:0'; got {text!r}"
        )
    try:
        return StatIdentity(kind=kind, key=int(key, 0))
    except ValueError as exc:
        raise StatTableError(f"invalid identity {text!r}: {exc}") from exc


def _print_stats_list(tables, kind: str) -> None:
    print("Buu's Fury Stat Records")
    print("-------------------------")
    print()
    print(f"Profile: {tables.profile.id}")
    print()
    if kind in ("enemy", "all"):
        print(f"{'Identity':>14}  {'Idx':>4}  {'Offset':>10}  {'HP':>7}  "
              f"{'EXP':>7}  {'Lv':>3}  {'Str':>4}  {'Pow':>4}  {'End':>4}")
        for entry in tables.enemies():
            r = entry.record
            print(
                f"{str(entry.identity):>14}  {entry.location.index:4}  "
                f"0x{entry.location.file_offset:08X}  {r.hp:7}  {r.exp:7}  "
                f"{r.level:3}  {r.strength:4}  {r.power:4}  {r.endurance:4}"
            )
        print()
    if kind in ("character", "all"):
        print(f"{'Identity':>14}  {'Alias':>9}  {'Offset':>10}  {'HP':>6}  "
              f"{'EP':>6}  {'Lv':>3}  {'Spd':>4}")
        for entry in tables.characters():
            r = entry.record
            print(
                f"{str(entry.identity):>14}  {entry.alias:>9}  "
                f"0x{entry.location.file_offset:08X}  {r.hp:6}  {r.ep:6}  "
                f"{r.level:3}  {r.speed:4}"
            )
        print()
    print("Identity is durable; index and offset are current location only.")


def _print_round_trip(tables) -> bool:
    plan = tables.plan()
    print("Buu's Fury Stat Round-Trip Validation")
    print("---------------------------------------")
    print()
    print(f"Profile: {tables.profile.id}")
    print(f"Base SHA256: {plan.base_sha256}")
    print(f"Records encoded: {len(plan.changes)}")
    print(f"Records differing from original: {len(plan.effective_changes)}")
    print(f"Bytes differing: {plan.changed_byte_count}")
    for change in plan.effective_changes:
        print(
            f"Mismatch: {change.owner} at 0x{change.offset:08X}: "
            f"{change.old.hex()} -> {change.new.hex()}"
        )
    print()
    print("RESULT:")
    print("PASS" if plan.is_noop else "FAIL")
    return plan.is_noop


def _print_stats_set(tables, args) -> int:
    identity = _parse_identity(args.identity)
    if identity.kind == "enemy":
        entry = tables.enemy(identity)
        before = getattr(entry.record, args.field, None)
        tables.set_enemy_field(identity, args.field, args.value)
    else:
        entry = tables.character(identity)
        before = getattr(entry.record, args.field, None)
        tables.set_character_field(identity, args.field, args.value)

    plan = tables.plan()
    manifest = emit_image(
        args.rom, args.output, plan, manifest_path=args.manifest
    )

    print("Buu's Fury Stat Edit")
    print("----------------------")
    print()
    print(f"Profile: {manifest.base_profile_id}")
    print(f"Record: {identity}")
    print(f"Field: {args.field}  {before} -> {args.value}")
    print()
    print(f"Base SHA256:   {manifest.base_sha256}")
    print(f"Output SHA256: {manifest.output_sha256}")
    print(f"Output: {args.output}")
    if args.manifest is not None:
        print(f"Manifest: {args.manifest}")
    print()
    print("Changes")
    for change in manifest.changes:
        differing = [
            change.offset + i
            for i, (a, b) in enumerate(zip(change.old, change.new))
            if a != b
        ]
        print(f"  {change.owner}: {change.reason}")
        print(f"    record at 0x{change.offset:08X} (+{change.size})")
        print(f"    bytes changed: {', '.join(f'0x{d:08X}' for d in differing)}")
    print()
    print("RESULT:")
    print("COMPLETE")
    return 0

def _parse_text_identity(value: str) -> TextIdentity:
    """Parse `text:0010`. Accepts unpadded digits, since a person types those."""
    prefix, separator, digits = value.partition(":")
    if prefix != "text" or not separator or not digits.isdigit():
        raise TextTableError(
            f"{value!r} is not a string identity; expected the form text:0010"
        )
    return TextIdentity(int(digits, 10))


def _format_text(text: str) -> str:
    """One-line form for listings. Real newlines would break column alignment."""
    return text.replace("\n", "\\n")


def _print_text_list(strings, contains: str | None, limit: int | None) -> None:
    entries = strings.find(contains) if contains is not None else tuple(strings.entries())
    shown = entries if limit is None else entries[:limit]

    print("Buu's Fury Strings")
    print("--------------------")
    print()
    print(f"Profile: {strings.profile.id}")
    print(f"Encoding: {strings.layout.encoding}")
    print(f"Strings: {len(entries)} shown {len(shown)}")
    print()
    for entry in shown:
        print(
            f"  {entry.identity}  0x{entry.location.gba_address:08X}  "
            f"{entry.location.allocation:>4}B  {_format_text(entry.text)}"
        )
    if limit is not None and len(entries) > len(shown):
        print(f"  ... {len(entries) - len(shown)} more")


def _parse_map_identity(value: str) -> MapIdentity:
    prefix, _, digits = value.partition(":")
    if prefix != "map" or not digits.isdigit():
        raise MapError(f'{value!r} is not a map identity; expected "map:0039"')
    return MapIdentity(int(digits, 10))


def _parse_placement_identity(value: str) -> PlacementIdentity:
    map_part, _, placement_part = value.partition("/")
    map_prefix, _, map_digits = map_part.partition(":")
    kind, _, index_digits = placement_part.partition(":")
    if (
        map_prefix != "map"
        or not map_digits.isdigit()
        or kind != "placement"
        or not index_digits.isdigit()
    ):
        raise MapError(
            f"{value!r} is not a placement identity; "
            'expected "map:0010/placement:0000"'
        )
    return PlacementIdentity(int(map_digits, 10), int(index_digits, 10))


def _print_map_placements(maps, identity: MapIdentity | None, limit: int | None) -> None:
    items = (
        list(maps.placements())
        if identity is None
        else list(maps.map_placements(identity))
    )
    print("Map Placements")
    print("--------------")
    print()
    if identity is not None:
        print(f"Map: {identity}")
    print(f"Placements: {len(items)}")
    print()
    if not items:
        return
    # Halfwords are labelled by position in the word, never by axis: no
    # evidence in this project establishes which one is X.
    print("  identity                      type    id   pos.low  pos.high")
    for item in items[:limit] if limit else items:
        record = item.record
        print(
            f"  {item.identity.key:<28}  "
            f"{record.type_raw:>4}  {record.id_raw:>4}  "
            f"{record.position_low:>8}  {record.position_high:>8}"
        )
    if limit and len(items) > limit:
        print(f"  ... {len(items) - limit} more")


def _print_placement_show(maps, identity: PlacementIdentity) -> None:
    entry = maps.placement(identity)
    record = entry.record
    print("Placement Record")
    print("----------------")
    print()
    print(f"Identity: {entry.identity}")
    print(f"Owner map: map:{entry.identity.map_index:04d}")
    print()
    print(f"factory_raw:  0x{record.factory_raw:08X}  (family constant)")
    print(f"flags_raw:    0x{record.flags_raw:08X}  UNKNOWN")
    print(f"type_raw:     0x{record.type_raw:08X}  UNKNOWN")
    print(f"position_raw: 0x{record.position_raw:08X}")
    print(f"  low halfword:  {record.position_low}  (axis UNKNOWN)")
    print(f"  high halfword: {record.position_high}  (axis UNKNOWN)")
    print(f"id_raw:       0x{record.id_raw:08X}  UNKNOWN")
    print(
        f"tail:         0x{record.tail0_raw:08X} "
        f"0x{record.tail1_raw:08X} 0x{record.tail2_raw:08X}  (family constants)"
    )


def _print_map_list(maps, limit: int | None, typed_only: bool) -> None:
    entries = [
        entry
        for entry in maps.entries()
        if not typed_only
        or (maps.slot_array(entry.identity) is not None
            and maps.slot_array(entry.identity).is_typed)
    ]
    shown = entries if limit is None else entries[:limit]

    print("Map Records")
    print("-----------")
    print()
    print(f"Profile: {maps.profile.id}")
    print(f"Maps: {len(entries)} shown {len(shown)}")
    print()
    for entry in shown:
        array = maps.slot_array(entry.identity)
        extent = "-" if array is None else f"{array.array.slot_count:>3} {array.shape.value}"
        print(
            f"  {entry.identity}  zone {maps.field(entry.identity, 'zone'):>3}  "
            f"area {maps.field(entry.identity, 'area'):>3}  "
            f"var {maps.field(entry.identity, 'variation'):>3}  "
            f"music {maps.field(entry.identity, 'music_id'):>5}  slots {extent}"
        )
    if limit is not None and len(entries) > len(shown):
        print(f"  ... {len(entries) - len(shown)} more")


def _print_map_show(maps, identity: MapIdentity) -> None:
    entry = maps.entry(identity)
    array = maps.slot_array(identity)

    print("Map Record")
    print("----------")
    print()
    print(f"Identity: {entry.identity}")
    for name in MAP_FIELDS:
        print(f"{name}: {maps.field(identity, name)}")
    print()
    if array is None:
        print("Slot extent: none declared")
        return
    print(f"Slot extent: {array.array.slot_count} slot(s), "
          f"{array.array.byte_size} bytes, {array.shape.value}")
    if not array.is_typed:
        # Stated rather than left implicit: an opaque extent is carried exactly
        # but this toolkit does not claim what its words mean.
        print("Slot fields: UNKNOWN (carried verbatim; not typed)")
        return
    print()
    print("Typed slots:")
    for index, slot in enumerate(array.array.slots):
        print(f"  [{index:>2}] type 0x{slot.word0:08X} -> source 0x{slot.word1:08X}")


def _print_map_connections(maps, identity: MapIdentity | None) -> None:
    graph = maps.graph()
    connections = graph.connections if identity is None else graph.from_map(identity)

    print("Map Connections")
    print("---------------")
    print()
    print(f"Profile: {maps.profile.id}")
    print(f"Connections: {len(connections)}")
    print(f"Resolved destinations: {graph.resolved_destination_count}")
    print()
    for connection in connections:
        reference = connection.reference
        print(
            f"  {connection.source} slot[{reference.slot_index}] "
            f"type 0x{reference.type_raw:08X} -> source "
            f"0x{reference.target_address:08X} -> destination UNKNOWN"
        )
    if connections:
        print()
        print(
            "Destinations are UNKNOWN: resolving one needs the layout of the "
            "referenced structure, which is verified for a single instance."
        )


def _print_map_round_trip(maps) -> bool:
    """Re-encode every map record and slot extent; report the whole extent."""
    record_failures = []
    slot_failures = []
    records = 0
    for entry in maps.entries():
        records += 1
        if entry.record.to_bytes() != entry.original_bytes:
            record_failures.append(entry.identity)

    arrays = 0
    slots = 0
    slot_bytes = 0
    typed_arrays = 0
    for item in maps.slot_arrays():
        arrays += 1
        slots += item.array.slot_count
        slot_bytes += item.array.byte_size
        if item.is_typed:
            typed_arrays += 1
        if item.array.to_bytes() != item.array.original_bytes:
            slot_failures.append(item.identity)

    placement_failures: list[str] = []
    placements = 0
    placement_bytes = 0
    placement_maps: set[int] = set()
    for placement in maps.placements():
        placements += 1
        placement_bytes += len(placement.original_bytes)
        placement_maps.add(placement.identity.map_index)
        if placement.record.to_bytes() != placement.original_bytes:
            placement_failures.append(str(placement.identity))

    print("Map Round-Trip")
    print("--------------")
    print()
    print(f"Profile: {maps.profile.id}")
    print(f"Map records checked: {records}")
    print(f"Slot arrays checked: {arrays}")
    print(f"Slots checked: {slots} ({slot_bytes} bytes)")
    print(f"Typed arrays: {typed_arrays}")
    print(f"Placements checked: {placements} ({placement_bytes} bytes)")
    print(f"Maps with placements: {len(placement_maps)}")
    print(f"Record failures: {len(record_failures)}")
    print(f"Slot failures: {len(slot_failures)}")
    print(f"Placement failures: {len(placement_failures)}")
    if record_failures or slot_failures or placement_failures:
        print()
        for identity in (
            [str(item) for item in record_failures]
            + [str(item) for item in slot_failures]
            + placement_failures
        )[:20]:
            print(f"  {identity}")
    print()
    print("RESULT:")
    passed = not record_failures and not slot_failures and not placement_failures
    print("PASS" if passed else "FAIL")
    return passed


def _print_text_show(strings, identity: TextIdentity) -> None:
    entry = strings.entry(identity)
    print("Buu's Fury String")
    print("-------------------")
    print()
    print(f"Identity: {entry.identity}")
    print(f"Address: 0x{entry.location.gba_address:08X}")
    print(f"File offset: 0x{entry.location.file_offset:08X}")
    print(f"Allocation: {entry.location.allocation} bytes")
    print(f"Pointer slot: 0x{entry.location.pointer_offset:08X}")
    print()
    print("Text:")
    print(entry.text)


def _print_text_round_trip(strings) -> bool:
    """Re-encode every string and report whether the whole extent is exact.

    This is the ROUND_TRIP proof in command form: it covers every string the
    pointer table enumerates, which - because the table tiles the pool - is
    every byte of the pool.
    """
    failures = []
    total = 0
    for entry in strings.entries():
        total += 1
        if encode_string(entry.text) != entry.original_bytes:
            failures.append(entry.identity)

    print("Buu's Fury String Round-Trip")
    print("------------------------------")
    print()
    print(f"Profile: {strings.profile.id}")
    print(f"Strings checked: {total}")
    print(f"Byte-identical: {total - len(failures)}")
    print(f"Failures: {len(failures)}")
    if failures:
        print()
        for identity in failures[:20]:
            print(f"  {identity}")
    print()
    print("RESULT:")
    print("COMPLETE" if not failures else "FAILED")
    return not failures


def _print_text_set(strings, args) -> int:
    identity = _parse_text_identity(args.identity)
    entry = strings.entry(identity)
    before = entry.text
    strings.set_text(identity, args.value)

    manifest = emit_image(
        args.rom, args.output, strings.plan(), manifest_path=args.manifest
    )

    print("Buu's Fury String Edit")
    print("------------------------")
    print()
    print(f"Profile: {manifest.base_profile_id}")
    print(f"String: {identity}")
    print(f"Text: {_format_text(before)} -> {_format_text(args.value)}")
    print()
    print(f"Base SHA256:   {manifest.base_sha256}")
    print(f"Output SHA256: {manifest.output_sha256}")
    print(f"Output: {args.output}")
    if args.manifest is not None:
        print(f"Manifest: {args.manifest}")
    print()
    print("Changes")
    for change in manifest.changes:
        differing = [
            change.offset + i
            for i, (a, b) in enumerate(zip(change.old, change.new))
            if a != b
        ]
        print(f"  {change.owner}: {change.reason}")
        print(f"    string at 0x{change.offset:08X} (+{change.size})")
        print(f"    bytes changed: {', '.join(f'0x{d:08X}' for d in differing)}")
    print()
    print("RESULT:")
    print("COMPLETE")
    return 0


def _print_extract(rom: Path, project: Path, written: list[Path]) -> None:
    print("Webfoot Project Extract")
    print("-------------------------")
    print()
    print(f"Base ROM: {rom}")
    print(f"Project: {project}")
    print()
    print("Files written")
    for path in written:
        print(f"  {path}")
    print()
    print("The base ROM was not modified and was not copied into the project.")
    print()
    print("RESULT:")
    print("COMPLETE")


def _print_validate(report: ValidationReport) -> None:
    print("Webfoot Project Validation")
    print("----------------------------")
    print()
    print(f"Project: {report.project_name}")
    print(f"Profile: {report.profile_id}")
    print(f"Base SHA256: {report.base_sha256}")
    print(f"Enemy records: {report.enemy_count}")
    print(f"Character records: {report.character_count}")
    print(f"Strings: {report.string_count}")
    print(f"Maps: {report.map_count}")
    print(f"Problems: {len(report.problems)}")
    for problem in report.problems:
        print(f"  {problem}")
    print()
    print("RESULT:")
    print("PASS" if report.passed else "FAIL")


def _print_build(result: BuildResult) -> None:
    manifest = result.manifest
    print("Webfoot Project Build")
    print("-----------------------")
    print()
    print(f"Project: {result.project_name}")
    print(f"Profile: {manifest.base_profile_id}")
    print()
    print(f"Base SHA256:   {manifest.base_sha256}")
    print(f"Output SHA256: {manifest.output_sha256}")
    print(f"Output: {result.output_path}")
    if result.manifest_path is not None:
        print(f"Manifest: {result.manifest_path}")
    print()
    print(f"Semantic edits applied: {len(manifest.changes)}")
    for change in manifest.changes:
        differing = [
            change.offset + i
            for i, (a, b) in enumerate(zip(change.old, change.new))
            if a != b
        ]
        print(f"  {change.owner}: {change.reason}")
        print(f"    record at 0x{change.offset:08X} (+{change.size})")
        print(f"    bytes changed: {', '.join(f'0x{d:08X}' for d in differing)}")
    if not manifest.changes:
        print("  none; this build reproduces the base image exactly")
    print()
    print("The base ROM was not modified.")
    print()
    print("RESULT:")
    print("COMPLETE")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "relocation-proof":
        from .relocation_proof import synthetic_relocation_proof
        print(json.dumps(synthetic_relocation_proof().to_json(), indent=2, sort_keys=True))
        return 0

    # TOOLKIT-002 commands are dispatched before the ROM-loading block below,
    # which assumes every command takes a positional `rom` and would otherwise
    # load one for commands whose base ROM arrives as `--rom`.
    if args.command in ("extract", "validate", "build"):
        try:
            catalog = load_catalog(args.profiles)
            if args.command == "extract":
                _print_extract(
                    args.rom,
                    args.project,
                    extract_project(
                        args.rom, args.project, catalog, name=args.name
                    ),
                )
                return 0
            if args.command == "validate":
                report = validate_project(args.project, args.rom, catalog)
                _print_validate(report)
                return 0 if report.passed else 2
            _print_build(
                build_project(
                    args.project,
                    args.rom,
                    args.output,
                    catalog,
                    manifest_path=args.manifest,
                )
            )
            return 0
        except (
            ProfileConfigError,
            GbaHeaderError,
            RomReadError,
            ProjectError,
            BuildError,
            StatTableError,
            StatEncodeError,
            WriteError,
            OSError,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    try:
        catalog = load_catalog(args.profiles)
        if args.command == "stats":
            tables = load_stat_tables(args.rom, catalog)
        elif args.command == "text":
            strings = load_text_strings(args.rom, catalog)
        elif args.command == "map":
            maps = load_maps(args.rom, catalog)
        elif args.command == "identify":
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
        MapError,
        RomReadError,
        StatTableError,
        StatEncodeError,
        TextTableError,
        TextCodecError,
        WriteError,
        OSError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.command == "map":
        try:
            if args.map_command == "list":
                _print_map_list(maps, args.limit, args.typed_only)
                return 0
            if args.map_command == "show":
                _print_map_show(maps, _parse_map_identity(args.identity))
                return 0
            if args.map_command == "connections":
                _print_map_connections(
                    maps,
                    None
                    if args.identity is None
                    else _parse_map_identity(args.identity),
                )
                return 0
            if args.map_command == "placements":
                _print_map_placements(
                    maps,
                    None
                    if args.identity is None
                    else _parse_map_identity(args.identity),
                    args.limit,
                )
                return 0
            if args.map_command == "placement":
                _print_placement_show(
                    maps, _parse_placement_identity(args.identity)
                )
                return 0
            return 0 if _print_map_round_trip(maps) else 2
        except (MapError, MapEntryError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.command == "text":
        try:
            if args.text_command == "list":
                _print_text_list(strings, args.contains, args.limit)
                return 0
            if args.text_command == "show":
                _print_text_show(strings, _parse_text_identity(args.identity))
                return 0
            if args.text_command == "validate-round-trip":
                return 0 if _print_text_round_trip(strings) else 2
            return _print_text_set(strings, args)
        except (TextTableError, TextCodecError, WriteError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.command == "stats":
        if args.stats_command == "list":
            _print_stats_list(tables, args.kind)
            return 0
        if args.stats_command == "validate-round-trip":
            return 0 if _print_round_trip(tables) else 2
        try:
            return _print_stats_set(tables, args)
        except (StatTableError, StatEncodeError, WriteError, OSError) as exc:
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
