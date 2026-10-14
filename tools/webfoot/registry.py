from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum

from .capability import Capability
from .formats import (
    ascii_text_tables,
    bg_tilemap,
    bps,
    indexed_png,
    map_entry,
    map_graphics,
    map_placements,
    map_slots,
    map_transitions,
    placement_links,
    rgb_png,
    script_vm,
    sprite_graphics,
    stat_tables,
    text_tables,
    webfoot_lz,
)


class RegistryError(ValueError):
    pass


class RoundTrip(str, Enum):
    BYTE_EXACT = "byte_exact"
    SELF_CONSISTENT = "self_consistent"
    DECODE_ONLY = "decode_only"
    UNPROVEN = "unproven"


@dataclass(frozen=True, slots=True)
class Converter:
    id: str
    family: str
    capabilities: tuple[Capability, ...]
    decode: Callable[..., object] | None
    encode: Callable[..., bytes] | None
    round_trip: RoundTrip
    evidence: str


#: ``capabilities`` is a tuple because one container codec serves every subsystem
#: that stores a payload, and naming a single owner would be a false statement.
CONVERTERS: tuple[Converter, ...] = (
    Converter(
        id="webfoot-lz",
        family="container",
        capabilities=(
            Capability.ACTOR_SPRITES,
            Capability.TEXT_STRINGS,
            Capability.MAP_ENTRIES,
            Capability.SCRIPTS,
        ),
        decode=webfoot_lz.unpack,
        encode=webfoot_lz.pack,
        round_trip=RoundTrip.SELF_CONSISTENT,
        evidence="tests/unit/test_webfoot_lz.py::test_pack_output_decodes_back_to_the_input",
    ),
    Converter(
        id="sprite-graphics-piece",
        family="sprite",
        capabilities=(Capability.ACTOR_SPRITES,),
        decode=sprite_graphics.decode_piece,
        encode=sprite_graphics.encode_piece,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_sprite_graphics.py::test_piece_round_trips_all_twelve_bytes",
    ),
    Converter(
        id="text-tables",
        family="text",
        capabilities=(Capability.TEXT_STRINGS, Capability.MAP_ENTRIES),
        decode=text_tables.decode_string,
        encode=text_tables.encode_string,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_text_tables.py::test_unknown_control_operand_round_trips_byte_for_byte",
    ),
    Converter(
        id="ascii-text-tables",
        family="text",
        capabilities=(Capability.TEXT_STRINGS,),
        decode=ascii_text_tables.decode_string,
        encode=ascii_text_tables.encode_string,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/integration/test_logii_text_rom.py::test_the_whole_pool_round_trips_byte_for_byte",
    ),
    Converter(
        id="indexed-png",
        family="image",
        capabilities=(Capability.ACTOR_SPRITES,),
        decode=indexed_png.decode,
        encode=indexed_png.encode,
        round_trip=RoundTrip.SELF_CONSISTENT,
        evidence="tests/unit/test_indexed_png.py::test_round_trip_preserves_pixels_palette_and_dimensions",
    ),
    Converter(
        id="rgb-png",
        family="image",
        capabilities=(),
        decode=rgb_png.decode_truecolour,
        encode=None,
        round_trip=RoundTrip.DECODE_ONLY,
        evidence="tools/webfoot/formats/rgb_png.py:33",
    ),
    Converter(
        id="bps-patch",
        family="patch",
        capabilities=(),
        decode=bps.apply,
        encode=bps.encode,
        round_trip=RoundTrip.SELF_CONSISTENT,
        evidence="tests/unit/test_bps.py::test_round_trip_returns_the_target",
    ),
    Converter(
        id="map-entry",
        family="map",
        capabilities=(Capability.MAP_ENTRIES,),
        decode=map_entry.MapEntry.from_bytes,
        encode=map_entry.MapEntry.to_bytes,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_map_entry.py::test_distinct_byte_pattern_round_trips_without_normalization",
    ),
    Converter(
        id="map-graphics-chunk",
        family="map",
        capabilities=(Capability.MAP_ENTRIES,),
        decode=map_graphics.dominant_chunk_words,
        encode=map_graphics.chunk_body_bytes,
        round_trip=RoundTrip.SELF_CONSISTENT,
        evidence="tests/unit/test_map_chunk_authoring.py::test_a_chunk_body_round_trips_through_its_container",
    ),
    Converter(
        id="map-placements",
        family="map",
        capabilities=(Capability.PLACEMENT_TYPES, Capability.MAP_ENTRIES),
        decode=map_placements.PlacementRecord.from_bytes,
        encode=map_placements.PlacementRecord.to_bytes,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_map_placements.py::test_a_record_round_trips_to_exactly_its_original_bytes",
    ),
    Converter(
        id="map-slots",
        family="map",
        capabilities=(Capability.MAP_ENTRIES,),
        decode=map_slots.decode_slot_array,
        encode=map_slots.MapSlotArray.to_bytes,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_map_slots.py::test_opaque_array_round_trips_byte_identically",
    ),
    Converter(
        id="map-transitions",
        family="map",
        capabilities=(Capability.MAP_ENTRIES,),
        decode=map_transitions.TransitionRecord.from_bytes,
        encode=map_transitions.TransitionRecord.to_bytes,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_map_transitions.py::test_every_record_round_trips_byte_identically",
    ),
    Converter(
        id="placement-links",
        family="script",
        capabilities=(Capability.SCRIPTS,),
        decode=placement_links.operand_references,
        encode=None,
        round_trip=RoundTrip.DECODE_ONLY,
        evidence="tools/webfoot/formats/placement_links.py:115",
    ),
    Converter(
        id="script-vm",
        family="script",
        capabilities=(Capability.SCRIPTS,),
        decode=script_vm.disassemble,
        encode=script_vm.assemble,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_script_vm.py::test_deterministic_and_termination",
    ),
    Converter(
        id="stat-tables",
        family="stats",
        capabilities=(Capability.ENEMY_STATS, Capability.CHARACTER_BASE_STATS),
        decode=stat_tables.decode_enemy_record,
        encode=stat_tables.encode_enemy_record,
        round_trip=RoundTrip.BYTE_EXACT,
        evidence="tests/unit/test_stat_write.py::test_unedited_enemy_record_re_encodes_byte_identically",
    ),
    Converter(
        id="bg-tilemap",
        family="map",
        capabilities=(Capability.MAP_ENTRIES,),
        decode=bg_tilemap.ScreenEntry.decode,
        encode=bg_tilemap.encode_screen_entry,
        round_trip=RoundTrip.UNPROVEN,
        evidence="tools/webfoot/formats/bg_tilemap.py:124",
    ),
)


def index_converters(entries: Iterable[Converter]) -> dict[str, Converter]:
    indexed: dict[str, Converter] = {}
    for entry in entries:
        if entry.id in indexed:
            raise RegistryError(f"duplicate converter id: {entry.id}")
        if entry.round_trip is RoundTrip.BYTE_EXACT and not entry.evidence.strip():
            raise RegistryError(f"a byte-exact converter needs an evidence locator: {entry.id}")
        indexed[entry.id] = entry
    return indexed


CONVERTER_BY_ID: dict[str, Converter] = index_converters(CONVERTERS)


def converter(converter_id: str) -> Converter:
    try:
        return CONVERTER_BY_ID[converter_id]
    except KeyError:
        known = ", ".join(sorted(CONVERTER_BY_ID))
        raise RegistryError(f"no converter named {converter_id!r}; known ids: {known}") from None


def converter_for(capability: Capability) -> tuple[Converter, ...]:
    return tuple(entry for entry in CONVERTERS if capability in entry.capabilities)


@dataclass(frozen=True, slots=True)
class RoundTripRow:
    id: str
    family: str
    round_trip: str
    evidence: str


def round_trip_report() -> tuple[RoundTripRow, ...]:
    return tuple(
        RoundTripRow(
            id=entry.id,
            family=entry.family,
            round_trip=entry.round_trip.value,
            evidence=entry.evidence,
        )
        for entry in CONVERTERS
    )
