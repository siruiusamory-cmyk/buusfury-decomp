"""Semantic access to the Buu's Fury stat tables.

TOOLKIT-001. This is the layer callers are meant to use:

    table = load_stat_tables(rom_path, catalog)
    wolf, = table.find_enemies_by_hp(175)
    table.set_enemy_field(wolf.identity, "hp", 200)
    plan = table.plan()

A caller names a record by identity and a field by name. It never computes a
file offset, never sees a table index, and never touches raw bytes - those are
provenance carried alongside a value, which is the boundary ARCH-TOOL-001
requires so a decomp backend can later replace the binary one underneath.

The table extents come from the ROM profile rather than from module constants,
so a second game or revision is a data change rather than a code change.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cache
from importlib import resources
import os
from pathlib import Path
from typing import Iterator

from .formats import stat_tables as st
from .hashing import hash_stream
from .profile import (
    RecordTableProfile,
    RomProfile,
    RomProfileCatalog,
    VerificationStatus,
)
from .rom import RomChangedError, RomIdentification, identify_rom
from .write import ByteChange, WritePlan, plan_changes


class StatTableError(ValueError):
    """Base error for semantic stat-table access."""


class StatProfileError(StatTableError):
    """Raised when a ROM or profile is not authorized for stat access."""


class UnknownRecordError(StatTableError):
    """Raised when an identity names no record in this table."""


class UnknownFieldError(StatTableError):
    """Raised when a field name is not editable on this record kind."""


#: Editable fields per record kind, with the invariants that hold beyond mere
#: byte-width fitting. Width is enforced in the codec at encode time; these are
#: the *semantic* bounds, which are stricter and are checked at edit time.
#:
#: Level is capped at 200 because P-010 read `cmp r6,#0xc8` at 0x08013A00 in
#: the EXP award path - the game itself treats 200 as the ceiling. The rest are
#: bounded only by their field width, and are listed with `None` rather than an
#: invented limit, because guessing a maximum would be fabricating a constraint
#: the ROM does not express.
ENEMY_FIELDS: dict[str, tuple[int, int | None]] = {
    "exp": (0, None),
    "hp": (0, None),
    "level": (1, 200),
    "strength": (0, None),
    "power": (0, None),
    "endurance": (0, None),
}

CHARACTER_FIELDS: dict[str, tuple[int, int | None]] = {
    "level": (1, 200),
    "hp": (0, None),
    "ep": (0, None),
    "strength": (0, None),
    "power": (0, None),
    "endurance": (0, None),
    "speed": (0, None),
}


@dataclass(frozen=True, slots=True)
class StatLocation:
    """Where a record currently sits. Provenance, never identity.

    Held separately from `StatIdentity` on purpose: an index and an offset are
    both true right now and both meaningless after anything moves.
    """

    index: int
    file_offset: int

    @property
    def gba_address(self) -> int:
        return self.file_offset + st.GBA_ROM_BASE


@dataclass(frozen=True, slots=True)
class EnemyEntry:
    """One enemy: durable identity, current values, current location, bytes."""

    identity: st.StatIdentity
    record: st.EnemyRecord
    location: StatLocation
    original_bytes: bytes


@dataclass(frozen=True, slots=True)
class CharacterEntry:
    """One playable character. `alias` is a display name, never an identity."""

    identity: st.StatIdentity
    alias: str
    record: st.BaseStatRecord
    location: StatLocation
    original_bytes: bytes


#: The profile whose stat extents DATA-001 verified against the canonical ROM.
SUPPORTED_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"


@cache
def _supported_profile_contract() -> RomProfile:
    """The packaged, in-repo statement of where the stat tables live.

    Read from the packaged catalog rather than from whatever the caller passed
    to `--profiles`, so it cannot be redirected by a supplied file.
    """
    packaged = resources.files("tools.webfoot.data").joinpath("roms.yaml")
    catalog = RomProfileCatalog.loads(
        packaged.read_text(encoding="utf-8"),
        source="packaged tools.webfoot.data/roms.yaml",
    )
    try:
        profile = next(
            item for item in catalog.profiles if item.id == SUPPORTED_PROFILE_ID
        )
    except StopIteration as exc:
        raise StatProfileError(
            f"packaged catalog has no {SUPPORTED_PROFILE_ID!r} profile"
        ) from exc
    if profile.enemy_stats is None or profile.character_base_stats is None:
        raise StatProfileError(
            "packaged target profile does not declare the stat tables"
        )
    return profile


def _require_stat_profile(identification: RomIdentification) -> RomProfile:
    """Fail closed unless this exact ROM is verified and declares both tables.

    The supplied profile is then cross-checked against the packaged contract,
    mirroring `formats.map_entry._require_target_profile`. This matters more on
    a write path than on a read one: without it, a hand-edited `--profiles`
    YAML could keep the ROM hashes intact while moving the declared table
    extents, and the toolkit would dutifully write records into whatever region
    that file named. Identity verification alone does not prevent that, because
    it authenticates the ROM rather than the metadata describing it.

    The cost is deliberate and recorded: adding a new game profile means adding
    it to the packaged catalog, not only to a local file. That is the intended
    direction anyway - a verified extent is a project fact, not a user setting.
    """
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise StatProfileError("stat-table access requires an exactly verified ROM")
    profile = match.profile
    if profile.enemy_stats is None or profile.character_base_stats is None:
        raise StatProfileError(
            f"profile {profile.id!r} does not declare the stat tables; "
            "stat access is unavailable for this ROM"
        )
    if profile.id != SUPPORTED_PROFILE_ID:
        raise StatProfileError(
            f"stat-table access supports only profile {SUPPORTED_PROFILE_ID!r}; "
            f"got {profile.id!r}"
        )

    contract = _supported_profile_contract()
    if (
        profile.enemy_stats != contract.enemy_stats
        or profile.character_base_stats != contract.character_base_stats
    ):
        raise StatProfileError(
            "supplied profile stat-table metadata conflicts with the packaged "
            "contract; refusing to read or write against unverified extents"
        )
    if (
        identification.hashes.sha256 != contract.sha256
        or identification.size != contract.size
    ):
        raise StatProfileError(
            "stat-table access requires the exact DATA-001 target identity"
        )
    return profile


def _table_offset(table: RecordTableProfile, rom_size: int, name: str) -> int:
    offset = table.address.to_file_offset(rom_size)
    if table.total_size > rom_size - offset:
        raise StatProfileError(f"configured {name} table extends beyond the ROM")
    return offset


class StatTables:
    """Loaded stat tables plus any pending semantic edits.

    Edits accumulate in memory and become a `WritePlan` only when `plan()` is
    called. Nothing here writes, and nothing here knows a destination path.
    """

    def __init__(
        self,
        *,
        identification: RomIdentification,
        profile: RomProfile,
        enemies: tuple[EnemyEntry, ...],
        characters: tuple[CharacterEntry, ...],
    ) -> None:
        self.identification = identification
        self.profile = profile
        self._enemies = {entry.identity: entry for entry in enemies}
        self._characters = {entry.identity: entry for entry in characters}
        self._enemy_order = tuple(entry.identity for entry in enemies)
        self._character_order = tuple(entry.identity for entry in characters)
        self._edits: dict[st.StatIdentity, list[str]] = {}
        #: Full base image, set by `load_stat_tables`. Retained so `plan()`
        #: validates against exactly the bytes the records were decoded from.
        self._base_bytes: bytes = b""

    # --- reading -------------------------------------------------------

    @property
    def base_bytes(self) -> bytes:
        """The exact image these records were decoded from.

        Exposed so a caller merging several subsystems into one plan can name
        the base every change was computed against, rather than re-reading a
        file whose identity this object already settled.
        """
        return self._base_bytes

    def enemies(self) -> Iterator[EnemyEntry]:
        """Every enemy, in table order. Order is presentation, not identity."""
        for identity in self._enemy_order:
            yield self._enemies[identity]

    def characters(self) -> Iterator[CharacterEntry]:
        for identity in self._character_order:
            yield self._characters[identity]

    def enemy(self, identity: st.StatIdentity) -> EnemyEntry:
        try:
            return self._enemies[identity]
        except KeyError:
            raise UnknownRecordError(f"no enemy record with identity {identity}") from None

    def character(self, identity: st.StatIdentity) -> CharacterEntry:
        try:
            return self._characters[identity]
        except KeyError:
            raise UnknownRecordError(
                f"no character record with identity {identity}"
            ) from None

    def find_enemies_by_hp(self, hp: int) -> tuple[EnemyEntry, ...]:
        """Locate by a value rather than a position.

        Used by the wolf test, where HP 175 is unique across the table and that
        uniqueness is itself the identification.
        """
        return tuple(e for e in self.enemies() if e.record.hp == hp)

    # --- editing -------------------------------------------------------

    def set_enemy_field(self, identity: st.StatIdentity, field: str, value: int) -> None:
        entry = self.enemy(identity)
        self._validate(ENEMY_FIELDS, field, value, kind="enemy")
        self._enemies[identity] = replace(entry, record=replace(entry.record, **{field: value}))
        self._edits.setdefault(identity, []).append(field)

    def set_character_field(
        self, identity: st.StatIdentity, field: str, value: int
    ) -> None:
        entry = self.character(identity)
        self._validate(CHARACTER_FIELDS, field, value, kind="character")
        self._characters[identity] = replace(
            entry, record=replace(entry.record, **{field: value})
        )
        self._edits.setdefault(identity, []).append(field)

    @staticmethod
    def _validate(
        allowed: dict[str, tuple[int, int | None]],
        field: str,
        value: int,
        *,
        kind: str,
    ) -> None:
        if field not in allowed:
            raise UnknownFieldError(
                f"{field!r} is not an editable {kind} field; "
                f"editable: {', '.join(sorted(allowed))}"
            )
        if type(value) is not int or isinstance(value, bool):
            raise StatTableError(f"{field} must be an integer, got {value!r}")
        minimum, maximum = allowed[field]
        if value < minimum:
            raise StatTableError(f"{field}={value} is below the minimum {minimum}")
        if maximum is not None and value > maximum:
            raise StatTableError(f"{field}={value} exceeds the maximum {maximum}")

    # --- planning ------------------------------------------------------

    def changes(self) -> tuple[ByteChange, ...]:
        """Encode every record into an attributed change.

        Every record is encoded, not just edited ones, because that is what
        proves round-trip: an untouched record must re-encode to exactly its
        original bytes, and `plan_changes` drops it as a no-op. A record that
        differed without having been edited would surface as an unexplained
        change rather than passing silently.

        Returned as changes rather than as a finished plan so a caller building
        several subsystems at once can put them all in one plan. TOOLKIT-004
        needed that: overlap detection is per-plan, so stats and text in two
        separate plans could each look valid while together writing the same
        bytes.
        """
        changes: list[ByteChange] = []

        for entry in self.enemies():
            encoded = st.encode_enemy_record(entry.record, entry.original_bytes)
            changes.append(
                ByteChange(
                    offset=entry.location.file_offset,
                    old=entry.original_bytes,
                    new=encoded,
                    owner=str(entry.identity),
                    reason=self._reason(entry.identity, "enemy"),
                )
            )

        for entry in self.characters():
            encoded = st.encode_base_stat_record(entry.record, entry.original_bytes)
            changes.append(
                ByteChange(
                    offset=entry.location.file_offset,
                    old=entry.original_bytes,
                    new=encoded,
                    owner=str(entry.identity),
                    reason=self._reason(entry.identity, "character", entry.alias),
                )
            )

        return tuple(changes)

    def plan(self) -> WritePlan:
        """Validate this subsystem's changes alone and return an applicable plan."""
        return plan_changes(
            self._base_bytes,
            self.changes(),
            profile_id=self.profile.id,
            base_sha256=self.identification.hashes.sha256,
        )

    def _reason(
        self, identity: st.StatIdentity, kind: str, alias: str | None = None
    ) -> str:
        fields = self._edits.get(identity)
        label = f"{kind} {alias}" if alias else kind
        if not fields:
            return f"{label} unchanged"
        unique = sorted(set(fields))
        return f"{label} edit: {', '.join(unique)}"


def load_stat_tables(path: str | Path, catalog: RomProfileCatalog) -> StatTables:
    """Identify `path`, then read both stat tables from it. Never writes.

    The whole image is retained so `plan()` can validate changes against the
    exact bytes they were computed from. At 8 MiB that is affordable, and the
    alternative - re-reading during planning - would reopen the identity
    question this function already settled.
    """
    source = Path(path)
    identification = identify_rom(source, catalog)
    profile = _require_stat_profile(identification)

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, _ = hash_stream(stream)
        if hashes != identification.hashes:
            raise RomChangedError(f"ROM identity changed before stat read: {source}")
        stream.seek(0)
        data = stream.read()
        after = os.fstat(stream.fileno())

    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise RomChangedError(f"ROM changed while stats were read: {source}")

    enemy_table = profile.enemy_stats
    character_table = profile.character_base_stats
    assert enemy_table is not None and character_table is not None

    enemy_base = _table_offset(enemy_table, len(data), "enemy_stats")
    character_base = _table_offset(character_table, len(data), "character_base_stats")

    enemies: list[EnemyEntry] = []
    for index in range(enemy_table.count):
        offset = enemy_base + index * enemy_table.record_size
        original = data[offset : offset + enemy_table.record_size]
        record = st.decode_enemy_record(data, offset)
        enemies.append(
            EnemyEntry(
                identity=st.enemy_identity(record),
                record=record,
                location=StatLocation(index=index, file_offset=offset),
                original_bytes=original,
            )
        )

    identities = {entry.identity for entry in enemies}
    if len(identities) != len(enemies):
        # Identity must be unique or it is not identity. DATA-001 verified this
        # holds for the canonical profile; a future profile where it does not
        # needs a different key, and must fail loudly rather than silently
        # dropping records into a dict.
        raise StatProfileError(
            f"profile {profile.id!r} has duplicate enemy type ids; "
            "type_id is not a usable identity for this ROM"
        )

    characters: list[CharacterEntry] = []
    for index in range(character_table.count):
        offset = character_base + index * character_table.record_size
        original = data[offset : offset + character_table.record_size]
        record = st.decode_base_stat_record(data, offset)
        characters.append(
            CharacterEntry(
                identity=st.character_identity(index),
                alias=st.character_alias(index),
                record=record,
                location=StatLocation(index=index, file_offset=offset),
                original_bytes=original,
            )
        )

    tables = StatTables(
        identification=identification,
        profile=profile,
        enemies=tuple(enemies),
        characters=tuple(characters),
    )
    tables._base_bytes = data
    return tables
