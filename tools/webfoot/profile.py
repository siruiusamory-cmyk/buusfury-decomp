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
}
_ALLOWED_TABLES = {"map_entries", "enemy_stats", "character_base_stats", "text_strings"}
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

    `relocatable` is a property of the *pool*, and it is False for every profile
    shipped today: relocation additionally requires declared free space, which
    no verified profile has. Declaring it True without free space still cannot
    move anything - the allocator refuses - so the flag records intent, never
    permission.
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
            free_regions=_free_regions(data.get("free_regions", []), size),
        )


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
