"""Pure codecs for the Buu's Fury static stat tables.

Provenance
----------
The record layouts are documented in `yoav74/BuusFuryToolkit` (pinned in
`upstreams.lock`), whose `Enemies.txt` and `Base Stats.txt` header lines state
the field orders reproduced below. DATA-001 verified both layouts against the
canonical local ROM `buus_fury_usa_rev0_01c1707f` before this module was
written; the bounds here are the *verified* extent, not the upstream's word -
upstream lists named offsets individually and never states where either table
begins or ends.

Evidence labels follow docs/DEVELOPMENT.md:

- ``CONFIRMED``  record stride, table extent, and the field decode. Established
  by reading the canonical ROM: every record in the extent satisfies the
  layout's structural invariants (both pad bytes zero, plausible level), and
  the three spot values named in DATA-001 all match independent sources.
- ``INFERRED``   the *names* attached to individual records. Those come from
  BuusFuryToolkit's author and were not re-derived. Numbers are trustworthy;
  a name is a label of convenience.

This module performs NO I/O. It is a pure codec over bytes supplied by the
caller, so it carries no ROM path, no profile check, and no file access of its
own - `webfoot.rom` and `webfoot.profile` own identity and safety, and
`webfoot.write` owns emission.

TOOLKIT-001 added encoding to what was originally a read-only decoder. The
purity constraint is unchanged and is load-bearing: because this module only
maps bytes to records and back, the same codec keeps working when the byte
source is a decomp tree rather than a ROM image, which is the backend
abstraction ARCH-TOOL-001 depends on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from ..binary import GBA_ROM_BASE as _GBA_ROM_BASE

# --- Enemy records -------------------------------------------------------
#
# The RECORD SIZE below is format structure the codec enforces. The table
# START/LAST/COUNT that follow are one game's measured extent, kept as the
# EVIDENCE that extent was verified against - the iterators that use them have
# no production caller. `webfoot.stats` and `webfoot.entities` take address,
# count and stride from `profile.enemy_stats` / `profile.character_base_stats`,
# which is the authority for a live read (CQA-15). Relocating a live reader onto
# these constants would reintroduce the duplicate authority this comment exists
# to prevent.

#: CONFIRMED. Bytes per enemy record.
ENEMY_RECORD_SIZE = 0x1C

#: CONFIRMED, EVIDENCE ORACLE. File offset of the first enemy record in the
#: contiguous table. Not a runtime authority: read only by `iter_enemy_records`,
#: whose callers are tests and the `logx_char_probe` research probe.
ENEMY_TABLE_START = 0x00711274

#: CONFIRMED, EVIDENCE ORACLE. File offset of the *last* enemy record
#: (inclusive).
ENEMY_TABLE_LAST = 0x007121C4

#: CONFIRMED, EVIDENCE ORACLE. Records in the contiguous table.
ENEMY_RECORD_COUNT = 141

# --- Character base stats ------------------------------------------------

#: CONFIRMED. Bytes per character base-stat record.
BASE_STAT_RECORD_SIZE = 0x12

#: CONFIRMED, EVIDENCE ORACLE. File offset of Goku's base-stat record; the 9
#: records are contiguous from here.
BASE_STAT_TABLE_START = 0x006FDA4C

#: CONFIRMED, EVIDENCE ORACLE. Playable characters in the base-stat table.
BASE_STAT_RECORD_COUNT = 9

#: INFERRED. Order per BuusFuryToolkit `Base Stats.txt`.
#:
#: Corroboration is real but weaker than a naive name match suggests: each
#: record's `person` byte lands inside the domain of that toolkit's separately
#: authored Person Types table, but the values point at VARIANT rows (Goku's
#: record carries person=0x02, listed there as "Goku (Dead)", not 0x00 "Goku").
#: So the byte is a valid appearance id; it is not a clean name confirmation.
BASE_STAT_NAMES = (
    "Goku",
    "Gohan",
    "Goten",
    "Trunks",
    "Vegeta",
    "Gotenks",
    "Vegito",
    "Gogeta",
    "Hercule",
)

#: GBA cartridge base. A file offset plus this is the address the game sees.
#: The convention is BuusFuryToolkit's README ("ROM offset + 0x08000000"); the
#: value itself is `binary.GBA_ROM_BASE`, the one owner of window semantics.
GBA_ROM_BASE = _GBA_ROM_BASE


@dataclass(frozen=True)
class EnemyRecord:
    """One enemy's static stats.

    ``offset`` is the *file* offset the record was decoded from and is carried
    purely as provenance, so an exported value can always be traced back to the
    bytes that produced it. It is not part of the game's data model.
    """

    offset: int
    exp: int
    hp: int
    type_id: int
    level: int
    strength: int
    power: int
    endurance: int

    @property
    def gba_address(self) -> int:
        return self.offset + GBA_ROM_BASE


@dataclass(frozen=True)
class BaseStatRecord:
    """One playable character's starting stats."""

    offset: int
    level: int
    hp: int
    ep: int
    strength: int
    power: int
    endurance: int
    speed: int
    person: int
    technique_count: int

    @property
    def gba_address(self) -> int:
        return self.offset + GBA_ROM_BASE


def decode_enemy_record(data: bytes, offset: int) -> EnemyRecord:
    """Decode the enemy record at ``offset``.

    Layout, from BuusFuryToolkit `Enemies.txt` line 1, verified against the
    canonical ROM::

        +0x00  u24  experience awarded
        +0x03  u8   pad, always 0
        +0x04  u24  hit points
        +0x07  u8   pad, always 0
        +0x08  u16  enemy type id
        +0x0A  u16  pad
        +0x0C  u8   level
        +0x0D  u8   strength
        +0x0E  u8   power
        +0x0F  u8   endurance
        +0x10  12   after-battle data, not decoded

    The two pad bytes are the structural check that makes a candidate record
    recognisable; `looks_like_enemy_record` relies on them.

    Type ids are unique across the table but only mostly ascending (3 of 140
    transitions decrease), so treat the id as a stable key and never as a
    sort order or an index.
    """
    blob = data[offset : offset + ENEMY_RECORD_SIZE]
    if len(blob) < ENEMY_RECORD_SIZE:
        raise ValueError(f"short enemy record at {offset:#010x}")
    return EnemyRecord(
        offset=offset,
        exp=int.from_bytes(blob[0:3], "little"),
        hp=int.from_bytes(blob[4:7], "little"),
        type_id=int.from_bytes(blob[8:10], "little"),
        level=blob[12],
        strength=blob[13],
        power=blob[14],
        endurance=blob[15],
    )


def decode_base_stat_record(data: bytes, offset: int) -> BaseStatRecord:
    """Decode the character base-stat record at ``offset``.

    Layout, from BuusFuryToolkit `Base Stats.txt` line 1, verified against the
    canonical ROM::

        +0x00  u8   level
        +0x01  u8   pad, always 0
        +0x02  u16  hit points
        +0x04  u16  energy points
        +0x06  u8   strength
        +0x07  u8   power
        +0x08  u8   endurance
        +0x09  u8   speed
        +0x0A  u8   person (appearance id)
        +0x0B  u8   starting technique count
        +0x0C  6    technique ids, not decoded
    """
    blob = data[offset : offset + BASE_STAT_RECORD_SIZE]
    if len(blob) < BASE_STAT_RECORD_SIZE:
        raise ValueError(f"short base-stat record at {offset:#010x}")
    return BaseStatRecord(
        offset=offset,
        level=blob[0],
        hp=int.from_bytes(blob[2:4], "little"),
        ep=int.from_bytes(blob[4:6], "little"),
        strength=blob[6],
        power=blob[7],
        endurance=blob[8],
        speed=blob[9],
        person=blob[10],
        technique_count=blob[11],
    )


def looks_like_enemy_record(data: bytes, offset: int) -> bool:
    """True when the bytes at ``offset`` are structurally a valid enemy record.

    This is the invariant used to establish the table extent: both documented
    pad bytes are zero, the level is a plausible 1..200, and neither 24-bit
    field is absurd. It is a *structural* test, deliberately not a semantic
    one - it says "this decodes cleanly", never "this is a real enemy".
    """
    blob = data[offset : offset + ENEMY_RECORD_SIZE]
    if len(blob) < ENEMY_RECORD_SIZE:
        return False
    if blob[3] != 0 or blob[7] != 0:
        return False
    exp = int.from_bytes(blob[0:3], "little")
    hp = int.from_bytes(blob[4:7], "little")
    if exp >= 400_000 or hp >= 400_000:
        return False
    return 0 < blob[12] <= 200


def iter_enemy_records(data: bytes) -> Iterator[EnemyRecord]:
    """Yield every enemy record in the verified contiguous table.

    EVIDENCE ORACLE, not a production reader: the offsets are this module's
    record of the extent a ticket verified, and the callers are tests and the
    `logx_char_probe` research probe. A production read takes the address, count
    and stride from the profile (`webfoot.stats`).
    """
    for offset in range(
        ENEMY_TABLE_START,
        ENEMY_TABLE_LAST + 1,
        ENEMY_RECORD_SIZE,
    ):
        yield decode_enemy_record(data, offset)


def iter_base_stat_records(data: bytes) -> Iterator[BaseStatRecord]:
    """Yield the 9 playable-character base-stat records. EVIDENCE ORACLE."""
    for index in range(BASE_STAT_RECORD_COUNT):
        offset = BASE_STAT_TABLE_START + index * BASE_STAT_RECORD_SIZE
        yield decode_base_stat_record(data, offset)


def find_enemy_by_hp(data: bytes, hp: int) -> list[EnemyRecord]:
    """Every enemy record in the table with exactly ``hp`` hit points.

    Used by the parity tests: the remake's wolf fixture is identified by
    HP 175, which is unique across the table, so this returning exactly one
    record is itself the assertion.
    """
    return [r for r in iter_enemy_records(data) if r.hp == hp]


# =========================================================================
# TOOLKIT-001: identity, encode, and unknown-byte preservation
# =========================================================================
#
# Everything below turns the read-only decoders above into an editable,
# byte-exact round-tripping codec. Three rules shape it, and each exists
# because getting it wrong is expensive to undo later:
#
# 1. IDENTITY IS NOT LOCATION. A record identity must survive the record
#    moving, being re-indexed, or being renamed. So three separate concepts
#    are kept apart and never collapsed into one another:
#
#        StatIdentity  - stable, durable, the thing a project file stores
#        alias         - human-readable, mutable, a display convenience
#        location      - table index and file offset, valid only right now
#
#    `iter_enemy_records` yields records in table order, and that order is
#    NOT identity: `test_enemy_type_ids_are_unique_but_not_assumed_sorted`
#    pins that 3 of 140 type-id transitions decrease, so position and key
#    genuinely disagree in this data.
#
# 2. UNKNOWN BYTES ARE DATA. Both record layouts have spans this project has
#    not decoded - 12 bytes of enemy after-battle data, 6 character technique
#    ids, and the pad bytes. A writer that emits only known fields destroys
#    them. Each record therefore keeps the exact bytes it was decoded from
#    and re-emits them, overwriting only the spans it actually understands.
#
#    This is deliberately implemented as a BACKING SLICE, not as a named
#    `opaque_tail` field: these two layouts happen to have contiguous
#    undecoded tails, but the general rule is only that unknown information
#    survives unchanged. Formats reached later (scripts, maps) will need
#    opaque nodes, opcodes or regions instead, and this shape does not
#    presume otherwise.
#
# 3. VALIDATE IS A SEPARATE STEP. Field assignment does not validate;
#    `encode_*` does, and refuses to emit a record that cannot fit its
#    original binary widths. Kaitai Struct made the same call in v0.11,
#    where `_write()` raises unless `_check()` ran after the last edit.
#    Setter-time validation cannot see cross-field invariants; emit-time
#    validation can, and it is the last point where refusing is still free.


#: Byte spans this module decodes, per record kind. Everything in a record
#: stride that is NOT listed here is undecoded and is preserved verbatim.
#: Keep these in sync with `decode_enemy_record` / `decode_base_stat_record`.
ENEMY_DECODED_SPANS = (
    (0x00, 3, "exp"),
    (0x04, 3, "hp"),
    (0x08, 2, "type_id"),
    (0x0C, 1, "level"),
    (0x0D, 1, "strength"),
    (0x0E, 1, "power"),
    (0x0F, 1, "endurance"),
)

BASE_STAT_DECODED_SPANS = (
    (0x00, 1, "level"),
    (0x02, 2, "hp"),
    (0x04, 2, "ep"),
    (0x06, 1, "strength"),
    (0x07, 1, "power"),
    (0x08, 1, "endurance"),
    (0x09, 1, "speed"),
    (0x0A, 1, "person"),
    (0x0B, 1, "technique_count"),
)


class StatEncodeError(ValueError):
    """Raised when a stat value cannot fit the width the ROM gave it."""


@dataclass(frozen=True)
class StatIdentity:
    """A durable handle for one stat record.

    Deliberately NOT an address, a file offset, or a table index - all three
    change the moment anything is inserted, removed or relocated, and a mod
    that stored one would break on the next edit.

    `kind` plus `key` is the whole identity. For enemies the key is the
    record type_id, which DATA-001 established is unique across all 141
    records; for characters it is the roster position, which is the only
    discriminator those 9 records currently offer and is marked as such.

    This is intentionally a within-profile identity. TOOLKIT-001 does not
    attempt the cross-game scheme, and nothing here forecloses it: a future
    scheme can wrap this without changing what callers already store.
    """

    kind: str
    key: int

    def __post_init__(self) -> None:
        if self.kind not in ("enemy", "character"):
            raise ValueError(f"unknown stat record kind: {self.kind!r}")
        if type(self.key) is not int or self.key < 0:
            raise ValueError("identity key must be a non-negative integer")

    def __str__(self) -> str:
        return f"{self.kind}:{self.key}"


def enemy_identity(record: EnemyRecord) -> StatIdentity:
    """Identity of an enemy record, keyed on its unique type_id.

    Type ids are unique but only mostly ascending, so this is a stable KEY
    and must never be used as a sort order or an array index.
    """
    return StatIdentity(kind="enemy", key=record.type_id)


def character_identity(index: int, count: int) -> StatIdentity:
    """Identity of a character record, keyed on roster position.

    UNLIKE the enemy key this is positional, because the base-stat records
    carry no verified unique discriminator of their own - the `person` byte
    points at appearance variants and is not confirmed to be one-per-record.
    It is a stable key only so long as the roster does not get reordered,
    which nothing in this ticket does. Recorded here so a future ticket
    replaces it deliberately rather than inheriting it by accident.

    `count` is the profile's declared `character_base_stats.count`, supplied by
    the caller. This is a live index bound, so it is the profile's declaration
    rather than one game's roster size: a copy here would silently accept or
    refuse an index against the wrong table.
    """
    if type(index) is not int or not 0 <= index < count:
        raise ValueError(f"character index out of range: {index}")
    return StatIdentity(kind="character", key=index)


def character_alias(index: int, count: int) -> str:
    """Human-readable name for a character record.

    A display alias, never an identity: these names are INFERRED from
    BuusFuryToolkit and could be renamed without the record changing.

    The names are one game's roster and no profile field declares them yet, so
    this is the one place in this layer that is still per-game data. It refuses
    rather than guessing: `count` is the caller's profile-declared roster size,
    and a profile whose roster is not this one gets a named refusal instead of
    another game's names against its records.
    """
    if count != len(BASE_STAT_NAMES):
        raise ValueError(
            f"no verified display roster for a profile declaring {count} character "
            f"records; the verified roster names are Buu's {len(BASE_STAT_NAMES)}"
        )
    if not 0 <= index < len(BASE_STAT_NAMES):
        raise ValueError(
            f"no verified display alias for character index {index}; the verified "
            f"roster is 0..{len(BASE_STAT_NAMES) - 1}"
        )
    return BASE_STAT_NAMES[index]


def _put_uint(buffer: bytearray, offset: int, width: int, value: int,
              field: str) -> None:
    """Write one little-endian unsigned field, refusing anything that would
    not fit the width the ROM actually gave it."""
    if type(value) is not int:
        raise StatEncodeError(
            f"{field} must be an integer, got {type(value).__name__}"
        )
    maximum = (1 << (width * 8)) - 1
    if not 0 <= value <= maximum:
        raise StatEncodeError(
            f"{field}={value} does not fit an unsigned {width * 8}-bit field "
            f"(0..{maximum})"
        )
    buffer[offset : offset + width] = value.to_bytes(width, "little")


def encode_enemy_record(record: EnemyRecord, original: bytes) -> bytes:
    """Re-encode one enemy record over the bytes it was decoded from.

    `original` must be the exact ENEMY_RECORD_SIZE bytes this record came
    from. Only the decoded spans are overwritten; the two pad bytes and the
    12-byte after-battle block ride through untouched, which is what makes
    an unchanged record re-serialize byte-identically.
    """
    if len(original) != ENEMY_RECORD_SIZE:
        raise StatEncodeError(
            f"enemy record backing must be exactly {ENEMY_RECORD_SIZE} bytes; "
            f"got {len(original)}"
        )
    blob = bytearray(original)
    _put_uint(blob, 0x00, 3, record.exp, "exp")
    _put_uint(blob, 0x04, 3, record.hp, "hp")
    _put_uint(blob, 0x08, 2, record.type_id, "type_id")
    _put_uint(blob, 0x0C, 1, record.level, "level")
    _put_uint(blob, 0x0D, 1, record.strength, "strength")
    _put_uint(blob, 0x0E, 1, record.power, "power")
    _put_uint(blob, 0x0F, 1, record.endurance, "endurance")
    return bytes(blob)


def encode_base_stat_record(record: BaseStatRecord, original: bytes) -> bytes:
    """Re-encode one character base-stat record over its original bytes.

    The pad byte at +0x01 and the 6 technique ids at +0x0C are undecoded and
    are preserved exactly.
    """
    if len(original) != BASE_STAT_RECORD_SIZE:
        raise StatEncodeError(
            f"base-stat record backing must be exactly {BASE_STAT_RECORD_SIZE} "
            f"bytes; got {len(original)}"
        )
    blob = bytearray(original)
    _put_uint(blob, 0x00, 1, record.level, "level")
    _put_uint(blob, 0x02, 2, record.hp, "hp")
    _put_uint(blob, 0x04, 2, record.ep, "ep")
    _put_uint(blob, 0x06, 1, record.strength, "strength")
    _put_uint(blob, 0x07, 1, record.power, "power")
    _put_uint(blob, 0x08, 1, record.endurance, "endurance")
    _put_uint(blob, 0x09, 1, record.speed, "speed")
    _put_uint(blob, 0x0A, 1, record.person, "person")
    _put_uint(blob, 0x0B, 1, record.technique_count, "technique_count")
    return bytes(blob)
