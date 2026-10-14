
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from ..binary import GBA_ROM_BASE as _GBA_ROM_BASE

# START/LAST/COUNT that follow are one game's measured extent, kept as the

ENEMY_RECORD_SIZE = 0x1C

ENEMY_TABLE_START = 0x00711274

ENEMY_TABLE_LAST = 0x007121C4

ENEMY_RECORD_COUNT = 141


BASE_STAT_RECORD_SIZE = 0x12

BASE_STAT_TABLE_START = 0x006FDA4C

BASE_STAT_RECORD_COUNT = 9

#: record carries person=0x02, listed there as "Goku (Dead)", not 0x00 "Goku").
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

#: The convention is BuusFuryToolkit's README ("ROM offset + 0x08000000"); the
GBA_ROM_BASE = _GBA_ROM_BASE


@dataclass(frozen=True)
class EnemyRecord:

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
    return [r for r in iter_enemy_records(data) if r.hp == hp]


# because getting it wrong is expensive to undo later:
# 1. IDENTITY IS NOT LOCATION. A record identity must survive the record
#    This is deliberately implemented as a BACKING SLICE, not as a named
#    presume otherwise.
#    `encode_*` does, and refuses to emit a record that cannot fit its
#    Setter-time validation cannot see cross-field invariants; emit-time


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
    return StatIdentity(kind="enemy", key=record.type_id)


def character_identity(index: int, count: int) -> StatIdentity:
    if type(index) is not int or not 0 <= index < count:
        raise ValueError(f"character index out of range: {index}")
    return StatIdentity(kind="character", key=index)


def character_alias(index: int, count: int) -> str:
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
