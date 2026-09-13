"""Data-driven exact ROM profiles and conservative matching."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import yaml

from .gba_header import GbaHeader
from .hashing import RomHashes
from .binary import BinaryAddressError, GBA_ROM_BASE, GbaRomAddress
from .binary import FileOffset
from .layout import FreeRegion, LayoutError, RomRange, check_alignment


_HEX_LENGTHS = {"crc32": 8, "md5": 32, "sha1": 40, "sha256": 64}
_ALLOWED_KEYS = {
    "id",
    "game",
    "region",
    "revision",
    "game_code",
    "size",
    "crc32",
    "md5",
    "sha1",
    "sha256",
    "sources",
    "notes",
    "tables",
    "free_regions",
    "generated_expansion",
}
_ALLOWED_TABLES = {"map_entries", "enemy_stats", "character_base_stats", "text_strings", "scripts", "placement_types", "actor_sprites"}
_ALLOWED_MAP_ENTRY_TABLE_KEYS = {"address", "count", "record_size"}
_ALLOWED_RECORD_TABLE_KEYS = {"address", "count", "record_size"}
_ALLOWED_TEXT_TABLE_KEYS = {
    "pointer_table_address",
    "count",
    "pool_address",
    "pool_size",
    "encoding",
    "alignment",
    "relocatable",
    "evidence",
}

#: Encodings a text codec implements. A profile naming anything else is refused
#: rather than decoded with the wrong reader.
#:
#: This set is what makes the codec choice *data*: `webfoot.text` selects a
#: reader by looking the profile's declared encoding up in its own registry, so
#: supporting a game whose strings are shaped differently means adding an
#: encoding and a codec, never a branch on which game is loaded.
_SUPPORTED_TEXT_ENCODINGS = {
    "utf16le_nul_terminated",
    "ascii_nul_terminated",
}


class ProfileConfigError(ValueError):
    """Raised for malformed or duplicate profile configuration."""


class AmbiguousProfileError(ProfileConfigError):
    """Raised when multiple profiles exactly identify one ROM."""


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True, slots=True)
class MapEntryTableProfile:
    address: GbaRomAddress
    count: int
    record_size: int


@dataclass(frozen=True, slots=True)
class RecordTableProfile:
    """A fixed-stride table of records, located by address rather than offset.

    Address is stored as a `GbaRomAddress` so the ROM-window check and the
    offset conversion stay in `binary`, and no caller is tempted to treat a
    file offset and a cartridge address as interchangeable.
    """

    address: GbaRomAddress
    count: int
    record_size: int

    @property
    def total_size(self) -> int:
        return self.count * self.record_size


@dataclass(frozen=True, slots=True)
class TextTableProfile:
    """A pointer-indexed pool of variable-length strings.

    Unlike `RecordTableProfile` there is no stride: entries are located through
    the pointer table, and the pool is described by its extent instead. The
    encoding is named rather than assumed, so a profile whose text this codec
    cannot read is refused instead of being decoded with the wrong reader.

    `relocatable` authorises relocation of this table's ENTRIES, not of the pool
    as a whole: no ticket has supplied evidence for moving a pool, and nothing
    reads this flag as permission to. TOOLKIT-036 set it True for canonical Buu,
    whose 1,534 pointers resolve to 1,534 distinct in-pool targets, and False
    stays correct for Legacy of Goku II, whose table aliases. It remains
    necessary and never sufficient: `webfoot.text` proves each entry's ownership
    from the measured image before publishing its anchor as movable, and the
    allocator still refuses a profile that declares no free space.
    """

    pointer_table_address: GbaRomAddress
    count: int
    pool_address: GbaRomAddress
    pool_size: int
    encoding: str
    alignment: int
    relocatable: bool
    evidence: str

    @property
    def pointer_table_size(self) -> int:
        return self.count * 4


@dataclass(frozen=True, slots=True)
class GeneratedExpansionProfile:
    """Verified capacity created after, and separate from, a retail image.

    ``RomProfile.size`` remains the measured canonical input size. This object
    describes only the deterministic generated output and its append-only
    allocation range; it must never be reported as canonical free space.
    """

    output_size: int
    padding_byte: int
    evidence: str

    def free_region(self, canonical_size: int) -> FreeRegion:
        return FreeRegion(
            RomRange(FileOffset(canonical_size), self.output_size - canonical_size),
            self.evidence,
        )

    def generated_image(self, canonical_size: int, allocated_spans: tuple[RomRange, ...]):
        """Make the write-layer contract from this profile declaration only."""
        from .write import GeneratedImage
        return GeneratedImage(
            self.output_size,
            self.padding_byte,
            self.free_region(canonical_size).range,
            self.evidence,
            allocated_spans,
        )


def _optional_text_table(
    tables: Mapping[str, Any] | None,
    name: str = "text_strings",
) -> TextTableProfile | None:
    if tables is None:
        return None
    table = tables.get(name)
    if table is None:
        return None
    if not isinstance(table, Mapping):
        raise ProfileConfigError(f"{name} table must be a mapping")
    unexpected = set(table) - _ALLOWED_TEXT_TABLE_KEYS
    if unexpected:
        joined = ", ".join(sorted(str(key) for key in unexpected))
        raise ProfileConfigError(f"{name} contains unexpected fields: {joined}")
    missing = _ALLOWED_TEXT_TABLE_KEYS - set(table)
    if missing:
        joined = ", ".join(sorted(missing))
        raise ProfileConfigError(f"{name} is missing required fields: {joined}")

    for key in ("pointer_table_address", "pool_address"):
        if type(table[key]) is not int:
            raise ProfileConfigError(f"{name} {key} must be an integer GBA address")
    for key in ("count", "pool_size"):
        if type(table[key]) is not int or table[key] <= 0:
            raise ProfileConfigError(f"{name} {key} must be a positive integer")

    encoding = table["encoding"]
    if encoding not in _SUPPORTED_TEXT_ENCODINGS:
        supported = ", ".join(sorted(_SUPPORTED_TEXT_ENCODINGS))
        raise ProfileConfigError(
            f"{name} encoding {encoding!r} is not implemented; supported: {supported}"
        )

    alignment = table["alignment"]
    try:
        check_alignment(alignment)
    except LayoutError as exc:
        raise ProfileConfigError(f"invalid {name} alignment: {exc}") from exc

    relocatable = table["relocatable"]
    if type(relocatable) is not bool:
        raise ProfileConfigError(f"{name} relocatable must be a boolean")

    evidence = table["evidence"]
    if not isinstance(evidence, str) or not evidence.strip():
        raise ProfileConfigError(f"{name} evidence must be a non-empty string")

    addresses = {}
    for key in ("pointer_table_address", "pool_address"):
        try:
            addresses[key] = GbaRomAddress(table[key])
        except BinaryAddressError as exc:
            raise ProfileConfigError(f"invalid {name} {key}: {exc}") from exc
        if addresses[key].raw < GBA_ROM_BASE:
            raise ProfileConfigError(f"{name} {key} must be in the GBA ROM window")

    return TextTableProfile(
        pointer_table_address=addresses["pointer_table_address"],
        count=table["count"],
        pool_address=addresses["pool_address"],
        pool_size=table["pool_size"],
        encoding=encoding,
        alignment=alignment,
        relocatable=relocatable,
        evidence=evidence.strip(),
    )


def _optional_record_table(
    tables: Mapping[str, Any] | None,
    name: str,
) -> RecordTableProfile | None:
    if tables is None:
        return None
    table = tables.get(name)
    if table is None:
        return None
    if not isinstance(table, Mapping):
        raise ProfileConfigError(f"{name} table must be a mapping")
    unexpected = set(table) - _ALLOWED_RECORD_TABLE_KEYS
    if unexpected:
        joined = ", ".join(sorted(str(key) for key in unexpected))
        raise ProfileConfigError(f"{name} contains unexpected fields: {joined}")

    address = table.get("address")
    count = table.get("count")
    record_size = table.get("record_size")
    if type(address) is not int:
        raise ProfileConfigError(f"{name} address must be an integer GBA address")
    if type(count) is not int or count <= 0:
        raise ProfileConfigError(f"{name} count must be a positive integer")
    if type(record_size) is not int or record_size <= 0:
        raise ProfileConfigError(f"{name} record_size must be a positive integer")
    try:
        gba_address = GbaRomAddress(address)
    except BinaryAddressError as exc:
        raise ProfileConfigError(f"invalid {name} address: {exc}") from exc
    if gba_address.raw < GBA_ROM_BASE:
        raise ProfileConfigError(f"{name} address must be in the GBA ROM window")
    return RecordTableProfile(
        address=gba_address,
        count=count,
        record_size=record_size,
    )


def _optional_map_entry_table(data: Mapping[str, Any]) -> MapEntryTableProfile | None:
    tables = data.get("tables")
    if tables is None:
        return None
    if not isinstance(tables, Mapping):
        raise ProfileConfigError("profile tables must be a mapping")
    unexpected_tables = set(tables) - _ALLOWED_TABLES
    if unexpected_tables:
        joined = ", ".join(sorted(str(key) for key in unexpected_tables))
        raise ProfileConfigError(f"profile contains unexpected tables: {joined}")

    map_entries = tables.get("map_entries")
    if map_entries is None:
        return None
    if not isinstance(map_entries, Mapping):
        raise ProfileConfigError("map_entries table must be a mapping")
    unexpected_keys = set(map_entries) - _ALLOWED_MAP_ENTRY_TABLE_KEYS
    if unexpected_keys:
        joined = ", ".join(sorted(str(key) for key in unexpected_keys))
        raise ProfileConfigError(f"map_entries contains unexpected fields: {joined}")

    address = map_entries.get("address")
    count = map_entries.get("count")
    record_size = map_entries.get("record_size")
    if type(address) is not int:
        raise ProfileConfigError("map_entries address must be an integer GBA address")
    if type(count) is not int or count <= 0:
        raise ProfileConfigError("map_entries count must be a positive integer")
    if type(record_size) is not int or record_size <= 0:
        raise ProfileConfigError("map_entries record_size must be a positive integer")
    try:
        gba_address = GbaRomAddress(address)
    except BinaryAddressError as exc:
        raise ProfileConfigError(f"invalid map_entries address: {exc}") from exc
    if gba_address.raw < GBA_ROM_BASE:
        raise ProfileConfigError("map_entries address must be in the GBA ROM window")
    return MapEntryTableProfile(
        address=gba_address,
        count=count,
        record_size=record_size,
    )


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProfileConfigError(f"profile field {key!r} must be a non-empty string")
    return value.strip()


def _optional_hash(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ProfileConfigError(f"profile field {key!r} must be a hexadecimal string")
    normalized = value.strip().lower()
    expected_length = _HEX_LENGTHS[key]
    if len(normalized) != expected_length or re.fullmatch(r"[0-9a-f]+", normalized) is None:
        raise ProfileConfigError(
            f"profile field {key!r} must contain {expected_length} hexadecimal characters"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class ScriptProfile:
    encoding: str
    family: str
    table_address: GbaRomAddress
    count: int
    stride: int
    slots: tuple[int, ...]
    pool_address: GbaRomAddress
    pool_size: int
    evidence: str
    # An owner-attached family names the static record kind that owns each
    # script and the label field, so an attachment carries a semantic owner
    # identity rather than a physical address. None means "no owner proven".
    owner_kind: str | None = None
    owner_label_slots: tuple[int, ...] = ()


def _optional_scripts(tables, size):
    """Return the declared script families, or None when the profile has none.

    A profile may declare one family as a mapping or several as a list. Every
    family is validated identically; multiple families exist because one VM can
    be entered from unrelated static owners, and merging their corpora would
    lose the ownership distinction that makes an attachment meaningful.
    """
    value = (tables or {}).get("scripts")
    if value is None:
        return None
    declarations = value if isinstance(value, list) else [value]
    if not declarations:
        raise ProfileConfigError("scripts requires at least one family")
    families = tuple(_one_script_family(item, size) for item in declarations)
    names = [family.family for family in families]
    if len(set(names)) != len(names):
        raise ProfileConfigError("scripts families must have distinct names")
    for left in range(len(families)):
        for right in range(left + 1, len(families)):
            _refuse_overlapping_pools(families[left], families[right], size)
    return families


def _refuse_overlapping_pools(first, second, size):
    """Two families must not claim the same bytes; overlap would double-own."""
    first_start = first.pool_address.to_file_offset(size)
    second_start = second.pool_address.to_file_offset(size)
    if (first_start < second_start + second.pool_size and
            second_start < first_start + first.pool_size):
        raise ProfileConfigError("script family pools overlap")


def _one_script_family(value, size):
    keys = {"encoding", "family", "table_address", "count", "stride", "slots",
            "pool_address", "pool_size", "evidence"}
    optional = {"owner_kind", "owner_label_slots"}
    if not isinstance(value, Mapping) or not keys <= set(value) or set(value) - keys - optional:
        raise ProfileConfigError("scripts requires exact contract fields")
    for key in ("encoding", "family", "evidence"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise ProfileConfigError(f"scripts {key} requires a string")
    for key in ("count", "stride", "pool_size"):
        if type(value[key]) is not int or value[key] <= 0:
            raise ProfileConfigError(f"scripts {key} requires a positive integer")
    slots = value["slots"]
    if (not isinstance(slots, list) or not slots or
            any(type(x) is not int or x < 0 or x % 4 or x+4 > value["stride"] for x in slots)
            or len(set(slots)) != len(slots)):
        raise ProfileConfigError("scripts slots invalid")
    try:
        table = GbaRomAddress(value["table_address"])
        pool = GbaRomAddress(value["pool_address"])
        if table.raw % 4 or value["stride"] % 4:
            raise ProfileConfigError("scripts pointer records must be word aligned")
        table_start = table.to_file_offset(size)
        pool_start = pool.to_file_offset(size)
        if (table_start < pool_start + value["pool_size"] and
                pool_start < table_start + value["count"] * value["stride"]):
            raise ProfileConfigError("scripts pointer table overlaps code pool")
        if (table.to_file_offset(size)+value["count"]*value["stride"] > size
                or pool.to_file_offset(size)+value["pool_size"] > size):
            raise ProfileConfigError("scripts extent outside ROM")
    except BinaryAddressError as exc:
        raise ProfileConfigError(str(exc)) from exc
    owner_kind = value.get("owner_kind")
    if owner_kind is not None and (not isinstance(owner_kind, str) or not owner_kind.strip()):
        raise ProfileConfigError("scripts owner_kind requires a string")
    label_slots = value.get("owner_label_slots", [])
    if (not isinstance(label_slots, list) or
            any(type(x) is not int or x < 0 or x + 2 > value["stride"] for x in label_slots) or
            len(set(label_slots)) != len(label_slots)):
        raise ProfileConfigError("scripts owner_label_slots invalid")
    if label_slots and owner_kind is None:
        raise ProfileConfigError("scripts owner_label_slots requires owner_kind")
    return ScriptProfile(value["encoding"], value["family"], table,
                         value["count"], value["stride"], tuple(slots), pool,
                         value["pool_size"], value["evidence"],
                         owner_kind, tuple(label_slots))


@dataclass(frozen=True, slots=True)
class PlacementTypeProfile:
    table_address: GbaRomAddress
    stride: int
    max_selector: int
    factory_raw: int
    constructor_address: GbaRomAddress
    evidence: str


@dataclass(frozen=True, slots=True)
class ActorSpriteProfile:
    """A profile's declaration of its actor-sprite graphics family.

    Every field is an extent the profile vouches for, never something a scanner
    inferred. ``animation_pointer_offset`` is where a character structure's
    animation pointers begin; it is declared rather than hard-coded because the
    header layout is a per-game fact, and the one place a wrong value could
    silently produce plausible-but-wrong assets.
    """

    character_table_address: GbaRomAddress
    character_count: int
    animation_pointer_offset: int
    object_palette_address: GbaRomAddress
    evidence: str


def _optional_actor_sprites(tables, size):
    value = (tables or {}).get("actor_sprites")
    if value is None:
        return None
    keys = {"character_table_address", "character_count",
            "animation_pointer_offset", "object_palette_address", "evidence"}
    if not isinstance(value, Mapping) or set(value) != keys:
        raise ProfileConfigError("actor_sprites requires exact contract fields")
    if type(value["character_count"]) is not int or value["character_count"] <= 0:
        raise ProfileConfigError("actor_sprites character_count must be a positive integer")
    offset = value["animation_pointer_offset"]
    if type(offset) is not int or offset < 0 or offset % 4:
        raise ProfileConfigError(
            "actor_sprites animation_pointer_offset must be a non-negative multiple of 4"
        )
    if not isinstance(value["evidence"], str) or not value["evidence"].strip():
        raise ProfileConfigError("actor_sprites requires non-empty evidence")
    try:
        table = GbaRomAddress(value["character_table_address"])
        palette = GbaRomAddress(value["object_palette_address"])
        start = table.to_file_offset(size)
        palette_start = palette.to_file_offset(size)
        if table.raw % 4 or palette.raw % 2:
            raise ProfileConfigError("actor_sprites address alignment mismatch")
        if start + value["character_count"] * 4 > size:
            raise ProfileConfigError("actor_sprites character table runs past the ROM")
        # A palette is 256 little-endian halfwords; a declaration whose palette
        # would run off the end is refused here rather than truncated later.
        if palette_start + 512 > size:
            raise ProfileConfigError("actor_sprites object palette runs past the ROM")
    except BinaryAddressError as exc:
        raise ProfileConfigError(str(exc)) from exc
    return ActorSpriteProfile(table, value["character_count"], offset, palette,
                              value["evidence"])


def _optional_placement_types(tables, size):
    value = (tables or {}).get("placement_types")
    if value is None:
        return None
    keys = {"table_address", "stride", "max_selector", "factory_raw",
            "constructor_address", "evidence"}
    if not isinstance(value, Mapping) or set(value) != keys:
        raise ProfileConfigError("placement_types requires exact contract fields")
    for key in ("stride", "max_selector", "factory_raw"):
        if type(value[key]) is not int or value[key] <= 0:
            raise ProfileConfigError(f"placement_types {key} must be positive integer")
    if value["stride"] % 4 or not isinstance(value["evidence"], str) or not value["evidence"].strip():
        raise ProfileConfigError("invalid placement type stride/evidence")
    try:
        table = GbaRomAddress(value["table_address"])
        ctor = GbaRomAddress(value["constructor_address"])
        start = table.to_file_offset(size)
        ctor.to_file_offset(size)
        GbaRomAddress(value["factory_raw"]).to_file_offset(size)
        if table.raw % 4 or ctor.raw % 2 or not value["factory_raw"] & 1:
            raise ProfileConfigError("placement type address alignment/state mismatch")
        if start + value["max_selector"] * value["stride"] >= size:
            raise ProfileConfigError("placement type selector target outside ROM")
    except BinaryAddressError as exc:
        raise ProfileConfigError(str(exc)) from exc
    return PlacementTypeProfile(table, value["stride"], value["max_selector"],
                                value["factory_raw"], ctor, value["evidence"])


@dataclass(frozen=True, slots=True)
class RomProfile:
    id: str
    game: str
    region: str
    revision: int | None
    game_code: str
    size: int
    crc32: str | None
    md5: str | None
    sha1: str | None
    sha256: str | None
    sources: tuple[str, ...]
    notes: str
    map_entries: MapEntryTableProfile | None
    enemy_stats: RecordTableProfile | None
    character_base_stats: RecordTableProfile | None
    text_strings: TextTableProfile | None = None
    free_regions: tuple[FreeRegion, ...] = ()
    scripts: tuple[ScriptProfile, ...] | None = None
    placement_types: PlacementTypeProfile | None = None
    actor_sprites: ActorSpriteProfile | None = None
    generated_expansion: GeneratedExpansionProfile | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RomProfile":
        if not isinstance(data, Mapping):
            raise ProfileConfigError("each profile must be a mapping")

        unexpected = set(data) - _ALLOWED_KEYS
        if unexpected:
            joined = ", ".join(sorted(str(key) for key in unexpected))
            raise ProfileConfigError(f"profile contains unexpected fields: {joined}")

        revision = data.get("revision")
        if revision is not None and (
            type(revision) is not int or revision < 0 or revision > 255
        ):
            raise ProfileConfigError("profile revision must be an integer from 0 through 255")

        size = data.get("size")
        if type(size) is not int or size <= 0:
            raise ProfileConfigError("profile size must be a positive integer")

        game_code = _required_string(data, "game_code").upper()
        if len(game_code) != 4 or not game_code.isascii() or not game_code.isalnum():
            raise ProfileConfigError("profile game_code must be four alphanumeric ASCII characters")

        sources_value = data.get("sources", [])
        if not isinstance(sources_value, list) or not all(
            isinstance(source, str) and source.strip() for source in sources_value
        ):
            raise ProfileConfigError("profile sources must be a list of non-empty strings")

        tables_value = data.get("tables")
        if tables_value is not None and not isinstance(tables_value, Mapping):
            raise ProfileConfigError("profile tables must be a mapping")

        hashes = {key: _optional_hash(data, key) for key in _HEX_LENGTHS}
        if hashes["sha256"] is None:
            raise ProfileConfigError("profile must provide sha256 for exact verification")

        notes = data.get("notes", "")
        if not isinstance(notes, str):
            raise ProfileConfigError("profile notes must be a string")

        return cls(
            id=_required_string(data, "id"),
            game=_required_string(data, "game"),
            region=_required_string(data, "region"),
            revision=revision,
            game_code=game_code,
            size=size,
            crc32=hashes["crc32"],
            md5=hashes["md5"],
            sha1=hashes["sha1"],
            sha256=hashes["sha256"],
            sources=tuple(source.strip() for source in sources_value),
            notes=notes.strip(),
            map_entries=_optional_map_entry_table(data),
            enemy_stats=_optional_record_table(tables_value, "enemy_stats"),
            character_base_stats=_optional_record_table(
                tables_value, "character_base_stats"
            ),
            text_strings=_optional_text_table(tables_value),
            scripts=_optional_scripts(tables_value, size),
            placement_types=_optional_placement_types(tables_value, size),
            actor_sprites=_optional_actor_sprites(tables_value, size),
            free_regions=_free_regions(data.get("free_regions", []), size),
            generated_expansion=_optional_generated_expansion(
                data.get("generated_expansion"), size
            ),
        )


def _optional_generated_expansion(
    value: Any, canonical_size: int
) -> GeneratedExpansionProfile | None:
    if value is None:
        return None
    if not isinstance(value, Mapping) or set(value) != {
        "output_size", "padding_byte", "evidence"
    }:
        raise ProfileConfigError(
            "generated_expansion requires output_size, padding_byte, evidence"
        )
    output_size = value["output_size"]
    padding_byte = value["padding_byte"]
    evidence = value["evidence"]
    if (type(output_size) is not int or output_size <= canonical_size or
            output_size > 0x02000000):
        raise ProfileConfigError(
            "generated_expansion output_size must be above canonical size and at most 32 MiB"
        )
    if output_size & (output_size - 1):
        raise ProfileConfigError("generated_expansion output_size must be a power of two")
    if type(padding_byte) is not int or not 0 <= padding_byte <= 0xFF:
        raise ProfileConfigError("generated_expansion padding_byte must be one byte")
    if not isinstance(evidence, str) or not evidence.strip():
        raise ProfileConfigError("generated_expansion evidence must be non-empty")
    return GeneratedExpansionProfile(output_size, padding_byte, evidence.strip())


def _free_regions(value: Any, size: int) -> tuple[FreeRegion, ...]:
    if not isinstance(value, list):
        raise ProfileConfigError("free_regions must be a list of verified declarations")
    regions = []
    for item in value:
        if not isinstance(item, Mapping) or set(item) != {"file_offset", "size", "status", "evidence"}:
            raise ProfileConfigError("free region requires file_offset, size, status, evidence")
        if item["status"] != "CONFIRMED":
            raise ProfileConfigError("production free regions must be CONFIRMED")
        try:
            region = FreeRegion(RomRange(FileOffset(item["file_offset"]), item["size"]), item["evidence"])
            region.range.validate(size)
        except (LayoutError, BinaryAddressError) as exc:
            raise ProfileConfigError(str(exc)) from exc
        regions.append(region)
    regions.sort(key=lambda r: r.range.start.value)
    for left, right in zip(regions, regions[1:]):
        if left.range.overlaps(right.range):
            raise ProfileConfigError("overlapping profile free regions")
    return tuple(regions)


@dataclass(frozen=True, slots=True)
class ProfileMatch:
    status: VerificationStatus
    profile: RomProfile | None
    reason: str
    mismatches: tuple[str, ...] = ()


class RomProfileCatalog:
    def __init__(self, profiles: Sequence[RomProfile]) -> None:
        self.profiles = tuple(profiles)
        self._validate_unique()

    @classmethod
    def load(cls, path: str | Path) -> "RomProfileCatalog":
        config_path = Path(path)
        try:
            text = config_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProfileConfigError(f"cannot load ROM profiles from {config_path}: {exc}") from exc
        return cls.loads(text, source=str(config_path))

    @classmethod
    def loads(cls, text: str, *, source: str = "<profiles>") -> "RomProfileCatalog":
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ProfileConfigError(f"cannot load ROM profiles from {source}: {exc}") from exc

        if not isinstance(raw, Mapping):
            raise ProfileConfigError("ROM profile configuration must be a mapping")
        if raw.get("schema_version") != 1:
            raise ProfileConfigError("ROM profile configuration requires schema_version: 1")
        profile_data = raw.get("profiles")
        if not isinstance(profile_data, list):
            raise ProfileConfigError("ROM profile configuration requires a profiles list")
        return cls([RomProfile.from_mapping(item) for item in profile_data])

    def _validate_unique(self) -> None:
        ids: set[str] = set()
        identities: dict[tuple[str, str], str] = {}
        for profile in self.profiles:
            if profile.sha256 is None:
                raise ProfileConfigError(
                    f"profile {profile.id!r} must provide sha256 for exact verification"
                )
            if profile.id in ids:
                raise ProfileConfigError(f"duplicate profile id: {profile.id}")
            ids.add(profile.id)
            for algorithm in ("sha256", "sha1", "md5"):
                value = getattr(profile, algorithm)
                if value is None:
                    continue
                key = (algorithm, value)
                prior = identities.get(key)
                if prior is not None:
                    raise ProfileConfigError(
                        f"duplicate {algorithm} identity in profiles {prior!r} and {profile.id!r}"
                    )
                identities[key] = profile.id

    def match(
        self,
        *,
        size: int,
        hashes: RomHashes,
        header: GbaHeader,
    ) -> ProfileMatch:
        candidates: list[RomProfile] = []
        conflicts: list[tuple[RomProfile, tuple[str, ...]]] = []

        for profile in self.profiles:
            if hashes.sha256 != profile.sha256:
                continue

            mismatches = self._mismatches(
                profile, size=size, hashes=hashes, header=header
            )
            if mismatches:
                conflicts.append((profile, mismatches))
            else:
                candidates.append(profile)

        if len(candidates) > 1:
            joined = ", ".join(profile.id for profile in candidates)
            raise AmbiguousProfileError(f"ROM matches multiple profiles: {joined}")
        if candidates:
            return ProfileMatch(
                status=VerificationStatus.VERIFIED,
                profile=candidates[0],
                reason="all configured hashes and metadata match exactly",
            )
        if conflicts:
            profile, mismatches = conflicts[0]
            return ProfileMatch(
                status=VerificationStatus.CONFLICT,
                profile=profile,
                reason="a cryptographic identity matched but configured metadata conflicted",
                mismatches=mismatches,
            )
        return ProfileMatch(
            status=VerificationStatus.UNKNOWN,
            profile=None,
            reason="no configured cryptographic identity matched",
        )

    @staticmethod
    def _mismatches(
        profile: RomProfile,
        *,
        size: int,
        hashes: RomHashes,
        header: GbaHeader,
    ) -> tuple[str, ...]:
        mismatches: list[str] = []
        if profile.size != size:
            mismatches.append(f"size: expected {profile.size}, got {size}")
        if profile.game_code != header.game_code:
            mismatches.append(
                f"game_code: expected {profile.game_code}, got {header.game_code}"
            )
        if profile.revision is not None and profile.revision != header.software_version:
            mismatches.append(
                f"revision: expected {profile.revision}, got {header.software_version}"
            )
        for algorithm in ("crc32", "md5", "sha1", "sha256"):
            expected = getattr(profile, algorithm)
            actual = getattr(hashes, algorithm)
            if expected is not None and expected != actual:
                mismatches.append(f"{algorithm}: expected {expected}, got {actual}")
        return tuple(mismatches)
