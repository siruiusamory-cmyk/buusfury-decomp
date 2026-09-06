"""Read-only parsers for the Buu's Fury static stat tables.

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

This module never writes. It is a pure decoder over bytes supplied by the
caller, so it carries no ROM path, no profile check, and no I/O of its own -
`webfoot.rom` and `webfoot.profile` already own identity and safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

# --- Enemy records -------------------------------------------------------

#: CONFIRMED. Bytes per enemy record.
ENEMY_RECORD_SIZE = 0x1C

#: CONFIRMED. File offset of the first enemy record in the contiguous table.
ENEMY_TABLE_START = 0x00711274

#: CONFIRMED. File offset of the *last* enemy record (inclusive).
ENEMY_TABLE_LAST = 0x007121C4

#: CONFIRMED. Records in the contiguous table.
ENEMY_RECORD_COUNT = 141

# --- Character base stats ------------------------------------------------

#: CONFIRMED. Bytes per character base-stat record.
BASE_STAT_RECORD_SIZE = 0x12

#: CONFIRMED. File offset of Goku's base-stat record; the 9 records are
#: contiguous from here.
BASE_STAT_TABLE_START = 0x006FDA4C

#: CONFIRMED. Playable characters in the base-stat table.
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
#: Convention documented by BuusFuryToolkit's README ("ROM offset + 0x08000000").
GBA_ROM_BASE = 0x08000000


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
    """Yield every enemy record in the verified contiguous table."""
    for offset in range(
        ENEMY_TABLE_START,
        ENEMY_TABLE_LAST + 1,
        ENEMY_RECORD_SIZE,
    ):
        yield decode_enemy_record(data, offset)


def iter_base_stat_records(data: bytes) -> Iterator[BaseStatRecord]:
    """Yield the 9 playable-character base-stat records."""
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
