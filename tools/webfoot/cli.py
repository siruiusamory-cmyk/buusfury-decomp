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
from .layout import LayoutError
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
    placement = subparsers.add_parser("placement", help="author placement clones and inspect capacity plans")
    placement_commands = placement.add_subparsers(dest="placement_command", required=True)
    clone = placement_commands.add_parser("clone", help="add a named canonical-template clone to a project")
    clone.add_argument("project", type=Path)
    clone.add_argument("--map", required=True)
    clone.add_argument("--source", required=True, help="map:NNNN/placement:NNNN")
    clone.add_argument("--name", required=True, help="stable lowercase name; never an address")
    clone.add_argument("--position-low", type=int, required=True)
    clone.add_argument("--position-high", type=int, required=True)
    clone.add_argument("--behavior", default=None,
                       help="attach an existing descriptor by identity, "
                            "map:NNNN/placement:NNNN/descriptor; omit to inherit the template's")
    clone.add_argument("--trigger", choices=("on_defeat",), default=None,
                       help="deliberate condition that starts --behavior")
    planning = placement_commands.add_parser("plan", help="validate and serialize; report ownership/capacity requirements")
    planning.add_argument("project", type=Path)
    planning.add_argument("--rom", type=Path, required=True)
    entity = subparsers.add_parser("entity", help="verified static placement/type relationships")
    entity_commands = entity.add_subparsers(dest="entity_command", required=True)
    for command in ("list", "show", "type", "types", "placements-of-type", "summary", "references"):
        child = entity_commands.add_parser(command)
        child.add_argument("rom", type=Path)
        if command in ("show", "type", "placements-of-type"):
            child.add_argument("identity")
        if command == "list":
            child.add_argument("--map", dest="map_identity")
    # TOOLKIT-013. Read-only inspection of the verified script/event corpus.
    # There is no event editor and no authoring command: the corpus is
    # fixed-size (free capacity is zero), so anything that could grow a stream
    # is deliberately absent rather than refused at runtime.
    event = subparsers.add_parser(
        "event", help="inspect the verified static script/event corpus"
    )
    event_commands = event.add_subparsers(dest="event_command", required=True)
    # `families` and the owner queries exist only because TOOLKIT-014 proved a
    # static owner. Commands are not added for symmetry: a family with no
    # proven owner simply reports no attachments.
    # TOOLKIT-018 adds two reference queries. `references` reports what an event
    # selects; `consumers-of` answers the reverse, which is the practically
    # useful direction: where in the game is this resource used. There is no
    # text query here because no map-scene event-to-text edge exists.
    # TOOLKIT-019 adds `resource-show`: the record's exact extent and the
    # engine's own dialog type. Read-only, like every verb above it.
    # TOOLKIT-020 adds `dialog-refs` and `dialogs-for-text`: the proven
    # dialog-to-text edge and its reverse. Read-only, and deliberately silent
    # for a dialog whose text index is computed at runtime.
    for command in ("summary", "list", "show", "validate-round-trip",
                    "families", "attachments", "for-owner", "owners-of", "for-map",
                    "for-placement", "references", "consumers-of",
                    "resource-show", "dialog-refs", "dialogs-for-text"):
        child = event_commands.add_parser(command)
        child.add_argument("rom", type=Path)
        if command == "show":
            child.add_argument("identity", help="entry identity from `event list`")
        if command in ("for-owner", "for-map", "for-placement"):
            child.add_argument("owner", help="owner identity, e.g. item:0000")
        if command == "owners-of":
            child.add_argument("identity", help="entry identity from `event list`")
        if command == "resource-show":
            child.add_argument("resource",
                               help="resource identity, e.g. event_resource:0508")
        if command == "dialog-refs":
            child.add_argument("resource", nargs="?", default=None,
                               help="resource identity, e.g. event_resource:0290; "
                                    "omit for the whole corpus")
        if command == "dialogs-for-text":
            child.add_argument("index", help="text entry index, e.g. 1525")
        if command == "consumers-of":
            child.add_argument("resource",
                               help="resource identity, e.g. event_resource:0508 "
                                    "or save_flag:0266")
        if command == "list":
            child.add_argument("--limit", type=int, default=None)
        if command != "families":
            child.add_argument("--family", default=None,
                               help="script family; defaults to the first declared")
    # TOOLKIT-010. Inspection only: normal project extraction stays the
    # authoring workflow, and nothing here is a sprite editor.
    graphics_parser = subparsers.add_parser(
        "graphics", help="inspect verified actor sprite assets and their consumers"
    )
    graphics_commands = graphics_parser.add_subparsers(
        dest="graphics_command", required=True
    )
    graphics_summary = graphics_commands.add_parser(
        "summary", help="corpus totals and sharing distribution"
    )
    graphics_summary.add_argument("rom", type=Path)

    graphics_list = graphics_commands.add_parser(
        "list", help="list graphic assets with dimensions and sharing"
    )
    graphics_list.add_argument("rom", type=Path)
    graphics_list.add_argument("--limit", type=int, default=40)
    graphics_list.add_argument(
        "--shared-only", action="store_true",
        help="only assets reached by more than one frame",
    )

    graphics_show = graphics_commands.add_parser(
        "show", help="print one graphic asset's fields"
    )
    graphics_show.add_argument("rom", type=Path)
    graphics_show.add_argument("identity", help="e.g. <profile>/graphic:0768")

    graphics_consumers = graphics_commands.add_parser(
        "consumers",
        help="every frame and character an edit to this asset would affect",
    )
    graphics_consumers.add_argument("rom", type=Path)
    graphics_consumers.add_argument("identity", help="e.g. <profile>/graphic:0768")

    graphics_characters = graphics_commands.add_parser(
        "characters", help="list character-table slots that reached art"
    )
    graphics_characters.add_argument("rom", type=Path)
    graphics_characters.add_argument("--limit", type=int, default=40)

    graphics_export = graphics_commands.add_parser(
        "export", help="write one asset as an indexed PNG"
    )
    graphics_export.add_argument("rom", type=Path)
    graphics_export.add_argument("identity", help="e.g. <profile>/graphic:0768")
    graphics_export.add_argument("--out", type=Path, required=True)

    graphics_references = graphics_commands.add_parser(
        "references",
        help="publish the verified graphics pointers into the common graph",
    )
    graphics_references.add_argument("rom", type=Path)

    graphics_palette = graphics_commands.add_parser(
        "palette", help="print the object palette, or who uses one entry"
    )
    graphics_palette.add_argument("rom", type=Path)
    graphics_palette.add_argument(
        "--index", type=int, default=None,
        help="report the graphics referencing this palette index",
    )

    # ROM-ATLAS-001. Queries against the assembled atlas JSONL, never the ROM:
    # this block opens no image, so it is self-contained like `graphics` and
    # cannot change how any ROM-loading command behaves.
    atlas_parser = subparsers.add_parser(
        "atlas", help="query the assembled structural atlas; reads no ROM"
    )
    atlas_parser.add_argument(
        "--atlas", type=Path, default=None,
        help="atlas JSONL (default: build/atlas/atlas.jsonl)",
    )
    atlas_commands = atlas_parser.add_subparsers(dest="atlas_command", required=True)

    atlas_build_cmd = atlas_commands.add_parser(
        "build", help="assemble the evidence artifacts into atlas.jsonl"
    )
    atlas_build_cmd.add_argument(
        "--artifacts", type=Path, default=None,
        help="artifact directory (default: build/atlas)",
    )

    atlas_addr = atlas_commands.add_parser(
        "addr", help="coverage, objects and observations at one offset"
    )
    atlas_addr.add_argument("offset", help="file offset or GBA address; 0x... or decimal")

    atlas_refs_to = atlas_commands.add_parser("refs-to", help="inbound references")
    atlas_refs_to.add_argument("offset")
    atlas_refs_to.add_argument("--size", type=int, default=1,
                               help="treat the offset as a range of this many bytes")
    atlas_refs_to.add_argument("--limit", type=int, default=40)

    atlas_refs_from = atlas_commands.add_parser("refs-from", help="outbound references")
    atlas_refs_from.add_argument("offset")
    atlas_refs_from.add_argument("--size", type=int, default=1)
    atlas_refs_from.add_argument("--limit", type=int, default=40)

    atlas_range = atlas_commands.add_parser("range", help="everything intersecting a range")
    atlas_range.add_argument("start")
    atlas_range.add_argument("end")
    atlas_range.add_argument("--limit", type=int, default=40)

    atlas_unknown = atlas_commands.add_parser(
        "unknown", help="unclassified coverage, largest first"
    )
    atlas_unknown.add_argument("--largest", type=int, default=20)

    atlas_objects = atlas_commands.add_parser("objects", help="located structures")
    atlas_objects.add_argument("--kind", default=None)
    atlas_objects.add_argument("--limit", type=int, default=40)

    atlas_text = atlas_commands.add_parser(
        "text", help="phrase search over the located text-run prefixes"
    )
    atlas_text.add_argument("phrase")
    atlas_text.add_argument("--limit", type=int, default=40)

    atlas_commands.add_parser("summary", help="coverage statistics and confidence distribution")

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
    extract.add_argument(
        "--no-graphics",
        action="store_true",
        help=(
            "skip sprite assets. They are the bulk of an extraction (7,355 "
            "indexed PNGs against a few dozen TOML files); a build from such a "
            "project is still byte-exact, because unchanged graphics come from "
            "the base image"
        ),
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
    print(f"descriptor_pointer_raw: 0x{record.descriptor_pointer_raw:08X}")
    print(f"child_count: {record.child_count}; record_size: {record.consumed_length}")
    print('child_pointers_raw: ' + ', '.join(f'0x{p:08X}' for p in record.child_pointers_raw))



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


def _parse_graphic_identity(value: str):
    """`<profile>/graphic:NNNN` -> a GraphicIdentity, or a clear refusal."""
    from .graphics import GraphicIdentity

    profile_id, separator, digits = value.partition("/graphic:")
    if not separator or not digits.isdecimal():
        raise ValueError("expected a profile-qualified graphic:NNNN identity")
    return GraphicIdentity(profile_id, int(digits))


def _default_atlas_directory() -> Path:
    return Path(__file__).resolve().parents[2] / "build" / "atlas"


def _run_atlas(args) -> int:
    """ROM-ATLAS-001 queries. Reads the assembled JSONL only; never a ROM."""
    from .atlas import (Atlas, AtlasError, AtlasReference, addr as atlas_addr,
                        in_range, objects_of_kind, refs_from, refs_to, unknowns)
    from .atlas_build import (AtlasBuildError, build_atlas, coverage_statistics,
                              load_atlas, parse_offset, write_atlas)
    from .binary import FileOffset
    from .layout import RomRange

    default_directory = _default_atlas_directory()
    atlas_path = args.atlas if args.atlas is not None else default_directory / "atlas.jsonl"

    try:
        if args.atlas_command == "build":
            directory = args.artifacts if args.artifacts is not None else default_directory
            report = build_atlas(directory)
            write_atlas(report, atlas_path)
            print(json.dumps({
                "atlas": str(atlas_path),
                "artifact_rows": dict(report.rows_read),
                "conflicts": len(report.conflicts),
                **coverage_statistics(report.atlas),
            }, indent=2, sort_keys=True))
            return 0

        atlas = load_atlas(atlas_path)

        def reference_json(reference) -> dict:
            return {"source_file_offset": f"0x{reference.source.value:06X}",
                    "target_file_offset": f"0x{reference.target.value:06X}"
                    if isinstance(reference, AtlasReference) else str(reference.target),
                    "confidence": getattr(reference, "confidence",
                                          getattr(reference, "classification", None)).value}

        def span_json(span) -> dict:
            return {"file_offset": f"0x{span.range.start.value:06X}",
                    "size": span.range.size, "classification": span.classification,
                    "confidence": span.confidence.value,
                    "evidence": span.provenance.evidence}

        def object_json(object) -> dict:
            return {"identity": object.identity,
                    "file_offset": f"0x{object.range.start.value:06X}",
                    "size": object.range.size, "kind": object.kind,
                    "confidence": object.confidence.value,
                    "attributes": dict(object.attributes)}

        def observation_json(observation) -> dict:
            return {"file_offset": f"0x{observation.range.start.value:06X}",
                    "size": observation.range.size, "kind": observation.kind,
                    "detail": observation.detail,
                    "confidence": observation.confidence.value}

        command = args.atlas_command
        if command == "summary":
            result = coverage_statistics(atlas)
        elif command == "unknown":
            result = [span_json(s) for s in unknowns(atlas, limit=args.largest)]
        elif command == "objects":
            found = (atlas.objects if args.kind is None
                     else objects_of_kind(atlas, args.kind))
            result = {"matched": len(found),
                      "objects": [object_json(o) for o in
                                  sorted(found, key=lambda o: o.range.start.value)
                                  [:args.limit]]}
        elif command == "text":
            # The scanner truncates each prefix at 40 characters, so this
            # searches the located prefixes rather than the full corpus.
            needle = args.phrase.lower()
            hits = [o for o in atlas.observations
                    if o.kind.startswith("text-run-") and needle in o.detail.lower()]
            result = {"searched": "located text-run prefixes only; scan_text.jsonl "
                                  "truncates each prefix at 40 characters, so a phrase "
                                  "longer than 40 characters cannot match",
                      "matched": len(hits),
                      "runs": [observation_json(o) for o in
                               sorted(hits, key=lambda o: o.range.start.value)[:args.limit]]}
        elif command == "addr":
            offset, how = parse_offset(args.offset)
            found = atlas_addr(atlas, FileOffset(offset))
            result = {"interpretation": how,
                      "coverage": span_json(found["coverage"]),
                      "objects": [object_json(o) for o in found["objects"]],
                      "observations": [observation_json(o) for o in found["observations"]]}
        elif command in ("refs-to", "refs-from"):
            offset, how = parse_offset(args.offset)
            wanted = RomRange(FileOffset(offset), max(1, args.size))
            edges = (refs_to(atlas, wanted) if command == "refs-to"
                     else refs_from(atlas, wanted))
            result = {"interpretation": how, "matched": len(edges),
                      "references": [reference_json(r) for r in edges[:args.limit]]}
        else:
            start, start_how = parse_offset(args.start)
            end, end_how = parse_offset(args.end)
            if end <= start:
                raise AtlasBuildError("range end must be greater than its start")
            found = in_range(atlas, RomRange(FileOffset(start), end - start))
            result = {"interpretation": [start_how, end_how],
                      "coverage": [span_json(s) for s in found["coverage"]],
                      "objects": [object_json(o) for o in found["objects"][:args.limit]],
                      "object_count": len(found["objects"]),
                      "reference_count": len(found["references"]),
                      "references": [reference_json(r) for r in
                                     found["references"][:args.limit]],
                      "observation_count": len(found["observations"]),
                      "observations": [observation_json(o) for o in
                                       found["observations"][:args.limit]]}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (AtlasError, AtlasBuildError, LayoutError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _run_graphics(args) -> int:
    """TOOLKIT-010 inspection commands.

    Self-contained like the `entity` block: it owns its ROM load and its error
    handling, so adding graphics cannot change how any existing command behaves.
    """
    from .formats import indexed_png, sprite_graphics
    from .graphics import GraphicsError, load_actor_sprites

    try:
        catalog = load_catalog(args.profiles)
        identification = identify_rom(args.rom, catalog)
        image = Path(args.rom).read_bytes()
        sprites = load_actor_sprites(image, identification)

        command = args.graphics_command
        if command == "summary":
            assets = sprites.graphics()
            result = {
                "profile": sprites.profile.id,
                "characters": len(sprites.characters()),
                "character_table_entries": sprites.layout.character_count,
                "graphics": len(assets),
                "frames": sum(len(a.consumers) for a in assets),
                "shared_by_frame": sum(1 for a in assets if a.shared),
                "shared_by_character": sum(1 for a in assets if len(a.characters) > 1),
                "packed_bytes": sum(a.packed_size for a in assets),
                "tile_bytes": sum(a.width * a.height for a in assets),
            }
        elif command == "list":
            assets = [
                a for a in sprites.graphics()
                if not args.shared_only or a.shared
            ][: args.limit]
            result = [a.to_document() for a in assets]
        elif command == "show":
            result = sprites.graphic(_parse_graphic_identity(args.identity)).to_document()
        elif command == "consumers":
            identity = _parse_graphic_identity(args.identity)
            result = {
                "id": str(identity),
                "characters": [str(c) for c in sprites.characters_using(identity)],
                "frames": [
                    {
                        "frame_offset": reference.frame_offset,
                        "character": reference.character_index,
                        "animation": reference.animation_index,
                        "frame": reference.frame_index,
                        "direction_slot": reference.direction,
                    }
                    for reference in sprites.consumers_of(identity)
                ],
            }
        elif command == "characters":
            result = [c.to_document() for c in sprites.characters()[: args.limit]]
        elif command == "references":
            result = sprites.reference_document().to_json()
        elif command == "export":
            asset = sprites.graphic(_parse_graphic_identity(args.identity))
            blob = indexed_png.encode(
                asset.pixels,
                asset.width,
                asset.height,
                sprites.palette.rgb,
                transparent_index=sprite_graphics.TRANSPARENT_INDEX,
            )
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(blob)
            result = {"id": str(asset.identity), "path": str(out), "bytes": len(blob)}
        else:  # palette
            if args.index is None:
                result = {
                    "entries": [
                        {"index": i, "raw": word, "rgb": list(sprites.palette.rgb[i])}
                        for i, word in enumerate(sprites.palette.raw)
                    ]
                }
            else:
                users = sprites.palette_users(args.index)
                result = {
                    "index": args.index,
                    "raw": sprites.palette.raw[args.index],
                    "rgb": list(sprites.palette.rgb[args.index]),
                    "graphics_using": len(users),
                    "graphics": [str(g) for g in users],
                }
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (GraphicsError, ProfileConfigError, RomReadError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _event_instruction_json(instruction, opcode_set) -> dict:
    """One instruction, named structurally. No gameplay meaning is asserted."""
    spec = opcode_set.lookup(instruction.opcode)
    payload = {
        "offset": instruction.source_offset,
        "opcode": f"0x{instruction.opcode:02X}",
        "name": spec.name,
        "encoded_length": instruction.encoded_length,
        "operands": [operand.value for operand in instruction.operands],
        "semantics": spec.semantics.value,
    }
    if instruction.target is not None:
        payload["target"] = instruction.target
    return payload


def _run_event(args) -> int:
    from .scripts import load_scripts, script_families
    from .formats.script_vm import ScriptError

    try:
        catalog = load_catalog(args.profiles)
        command = args.event_command
        if command == "families":
            print(json.dumps(list(script_families(args.rom, catalog)),
                             sort_keys=True, indent=2))
            return 0
        if command in ('for-map', 'for-placement', 'references', 'consumers-of',
                       'resource-show', 'dialog-refs', 'dialogs-for-text'):
            from .placement_events import PlacementEvents
            from .maps import load_maps
            relationships = PlacementEvents(load_maps(args.rom, catalog))
            if command == 'for-map':
                result = relationships.events_for_map(_parse_map_identity(args.owner))
            elif command == 'for-placement':
                descriptor = relationships.descriptor_of(_parse_placement_identity(args.owner))
                result = {'descriptor': descriptor.identity, 'event': descriptor.event}
            elif command == 'references':
                result = [{'kind': r.kind, 'event': r.event, 'index': r.index,
                           'access': r.access, 'source_file_offset': r.source,
                           'encoded_length': r.encoded_length}
                          for r in relationships.operand_references()]
            elif command == 'resource-show':
                kind, _, index = args.resource.rpartition(':')
                if kind != 'event_resource' or not index.isdigit():
                    raise ValueError(f"unknown resource identity {args.resource!r}")
                result = relationships.resource_show(int(index))
            elif command == 'dialog-refs':
                scope = None
                if args.resource is not None:
                    kind, _, index = args.resource.rpartition(':')
                    if kind != 'event_resource' or not index.isdigit():
                        raise ValueError(f"unknown resource identity {args.resource!r}")
                    scope = int(index)
                result = [{'dialog': f'event_resource:{r.dialog:04d}',
                           'text': r.index, 'x': r.x, 'y': r.y,
                           'block': r.block, 'ir_offset': r.ir_offset,
                           'source_file_offset': r.source,
                           'encoded_length': r.encoded_length}
                          for r in relationships.dialog_text_references(scope)]
            elif command == 'dialogs-for-text':
                if not args.index.isdigit():
                    raise ValueError(f"unknown text index {args.index!r}")
                result = [f'event_resource:{d:04d}'
                          for d in relationships.dialogs_for_text(int(args.index))]
            else:
                kind, _, index = args.resource.rpartition(':')
                if kind not in ('event_resource', 'save_flag') or not index.isdigit():
                    raise ValueError(f"unknown resource identity {args.resource!r}")
                result = relationships.consumers_of(kind, int(index))
            print(json.dumps(result, sort_keys=True, indent=2))
            return 0
        corpus = load_scripts(args.rom, catalog, args.family)
        opcode_set = corpus.ir.opcode_set
        if command == "summary":
            result = {
                "profile_id": corpus.profile_id,
                "family": corpus.family,
                "opcode_set": opcode_set.name,
                "entries": len(corpus.ir.entries),
                "blocks": len(corpus.ir.blocks),
                "instructions": corpus.instruction_count,
                "extent_bytes": corpus.ir.extent,
                "uncovered_bytes": sum(len(raw) for _, raw in corpus.ir.opaque),
                "attachments": len(corpus.attachments),
            }
        elif command == "attachments":
            result = [{"owner": a.owner, "owner_kind": a.owner_kind,
                       "event": a.event, "label_text_ids": list(a.label_text_ids)}
                      for a in corpus.attachments]
        elif command == "for-owner":
            result = list(corpus.events_of(args.owner))
        elif command == "owners-of":
            result = list(corpus.owners_of(args.identity))
        elif command == "list":
            entries = corpus.ir.entries
            if args.limit is not None:
                entries = entries[: args.limit]
            result = [e.identity for e in entries]
        elif command == "show":
            entry = next((e for e in corpus.ir.entries if e.identity == args.identity), None)
            if entry is None:
                raise ValueError(f"unknown event identity {args.identity!r}")
            starts = {b.instructions[0].source_offset: b for b in corpus.ir.blocks}
            block = starts[entry.offset]
            result = {
                "identity": entry.identity,
                "instructions": [_event_instruction_json(i, opcode_set)
                                 for i in block.instructions],
                "edges": [{"kind": e.kind, "target": e.target} for e in block.edges],
            }
        else:
            # load_scripts already refuses a corpus that does not re-encode
            # byte-identically, so reaching here is itself the proof.
            from .formats.script_vm import assemble
            result = {"round_trip": True, "bytes": len(assemble(corpus.ir))}
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (ScriptError, ProfileConfigError, RomReadError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "entity":
        from .entities import load_placement_types, PlacementTypeIdentity
        try:
            types = load_placement_types(args.rom, load_catalog(args.profiles))
            command = args.entity_command
            if command == "summary":
                result = types.summary()
            elif command == "references":
                result = types.reference_document().to_json()
            elif command == "types":
                result = [t.to_json() for t in types.types()]
            elif command == "placements-of-type":
                profile_id, separator, digits = args.identity.partition("/placement_type:")
                if not separator or not digits.isdecimal():
                    raise ValueError("expected profile-qualified placement_type:NNNN identity")
                identity = PlacementTypeIdentity(profile_id, int(digits))
                result = [str(p) for p in types.placements_of_type(identity)]
            elif command in ("show", "type"):
                identity = _parse_placement_identity(args.identity)
                item = types.type_of(identity)
                result = ({**item.to_json(), "factory": types.factory_of(item.identity)}
                          if command == "show" else {"placement_id": str(identity), "type_id": str(item.identity)})
            else:
                placements = (types.maps.placements() if args.map_identity is None else
                              types.maps.map_placements(_parse_map_identity(args.map_identity)))
                result = [{"placement_id": str(p.identity), "type_id": str(types.type_of(p.identity).identity)}
                          for p in placements]
            print(json.dumps(result, sort_keys=True, indent=2))
            return 0
        except (ValueError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.command == "event":
        return _run_event(args)

    if args.command == "graphics":
        return _run_graphics(args)

    if args.command == "atlas":
        return _run_atlas(args)

    if args.command == "relocation-proof":
        from .relocation_proof import synthetic_relocation_proof
        print(json.dumps(synthetic_relocation_proof().to_json(), indent=2, sort_keys=True))
        return 0

    # TOOLKIT-002 commands are dispatched before the ROM-loading block below,
    # which assumes every command takes a positional `rom` and would otherwise
    # load one for commands whose base ROM arrives as `--rom`.
    if args.command == "placement":
        try:
            from .project.placements import clone_placement
            from .build import authored_capacity_plan
            if args.placement_command == "clone":
                clone = clone_placement(args.project, map_index=_parse_map_identity(args.map).index,
                    source=args.source, name=args.name, position_low=args.position_low,
                    position_high=args.position_high, behavior=args.behavior,
                    trigger=args.trigger)
                print(clone.identity)
            else:
                runs = authored_capacity_plan(args.project, args.rom, load_catalog(args.profiles))
                print(json.dumps([r.to_json() for r in runs], indent=2, sort_keys=True))
            return 0
        except (ValueError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.command in ("extract", "validate", "build"):
        try:
            catalog = load_catalog(args.profiles)
            if args.command == "extract":
                _print_extract(
                    args.rom,
                    args.project,
                    extract_project(
                        args.rom,
                        args.project,
                        catalog,
                        name=args.name,
                        graphics=not args.no_graphics,
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
            LayoutError,
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
