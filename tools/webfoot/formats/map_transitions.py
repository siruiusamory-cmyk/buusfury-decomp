"""Pure codec for the Buu's Fury selector-1-root connection records.
* the record's engine-accessed extent is ``+0x00..+0x17`` - 24 bytes, read at
  the engine's own access widths (claims 8, 11, 15, 16, 18, 20);
* ``+0x00`` is the constructor/class word the registry calls through the
  ``bx r1`` trampoline (claim 9a). Two values occur in the canonical corpus,
  ``0x08007675`` (566 records) and ``0x080072CD`` (169); the *meaning* of the
  two classes is UNRESOLVED (claim 10), so the word is carried and never
  interpreted or authored;
* ``+0x08`` is four little-endian ``u16`` that form two ordered intervals,
  ``A <= C`` and ``B <= D`` on 735/735 canonical records with no degenerate
  case (claim 12). Which interval is horizontal, and what the unit is, are
  UNRESOLVED (claims 13, 14), so the four words are named **positionally** and
  no axis name is invented;
* the destination is **two independent bytes**, `+0x11` high and `+0x12` low -
  the engine loads them with two separate ``ldrb`` on the producer and two on
  the consumer (claim 16), and resolves them through the ``MapEntry +0x00``
  two-byte key scan (claim 17). It is not a halfword-typed field (claim 22);
* ``+0x13`` remains an engine-read field whose semantics are UNRESOLVED (claim
  19), so it is preserved byte-for-byte and is not editable. ``+0x10``,
  ``+0x14``, ``+0x16`` and ``+0x17`` are no longer in that list: the arrival pair
  (:attr:`TransitionRecord.arrival`) and the arrival facing
  (:attr:`TransitionRecord.facing`) are decoded and authorable, with the parts
  that remain unresolved - the low-nibble gate's meaning, and which of the two
  record classes shares the pair's semantics - stated as unresolved in their own
  docstrings rather than implied here;
* ``+0x04`` is one invariant word on all 735 canonical records, and no evidence
  establishes what it is. It is preserved and deliberately **not** validated:
"""

from __future__ import annotations

from dataclasses import dataclass, replace, fields
import struct

TRANSITION_SIZE = 24

TRANSITION_CLASS_A_RAW = 0x08007675
TRANSITION_CLASS_B_RAW = 0x080072CD

SUPPORTED_CLASS_RAW = frozenset({TRANSITION_CLASS_A_RAW, TRANSITION_CLASS_B_RAW})

BOUND_MINIMUM = 0x0000
BOUND_MAXIMUM = 0xFFFF

#: Supporting engine evidence: the 566-class method ``0x080075AC`` passes
#: ``record + 0x14`` itself to the warp routine (``08007600 adds r3,#0x14`` then
#: ``0800760A bl 0x08008d44``), and the 169-class method ``0x080071F8`` reads
#: ``+0x14`` and ``+0x16`` with ``ldrsh`` before building its own pair. **The
#: earlier citation of ``0x0800CEF4`` here was withdrawn** - that routine's
#: argument is an element of the scene's separate 24-byte array at ``scene+0x28``,
#: not a transition record, so it is not evidence about this one.
ARRIVAL_UNSET_MINIMUM = 0xFFF8


class MapTransitionError(ValueError):
    """Base error for the selector-1-root connection record."""


class MapTransitionLengthError(MapTransitionError):
    """Raised when a record is not exactly 24 bytes."""


class MapTransitionValueError(MapTransitionError):
    """Raised when a field cannot fit its physical width."""


class MapTransitionFamilyError(MapTransitionError):
    """Raised when a record is a transition form this project has not measured."""


class MapTransitionRegionError(MapTransitionError):
    """Raised for a region that is not two ordered, non-degenerate intervals."""


@dataclass(frozen=True, slots=True)
class TransitionField:
    offset: int
    width: int
    name: str


TRANSITION_LAYOUT = (
    TransitionField(0x00, 4, "class_raw"),
    TransitionField(0x04, 4, "constant_raw"),
    TransitionField(0x08, 2, "bound_a_raw"),
    TransitionField(0x0A, 2, "bound_b_raw"),
    TransitionField(0x0C, 2, "bound_c_raw"),
    TransitionField(0x0E, 2, "bound_d_raw"),
    TransitionField(0x10, 1, "byte_0x10_raw"),
    TransitionField(0x11, 1, "destination_key_high"),
    TransitionField(0x12, 1, "destination_key_low"),
    TransitionField(0x13, 1, "byte_0x13_raw"),
    TransitionField(0x14, 2, "word_0x14_raw"),
    TransitionField(0x16, 1, "byte_0x16_raw"),
    TransitionField(0x17, 1, "byte_0x17_raw"),
)

_RECORD_STRUCT = struct.Struct("<IIHHHHBBBBHBB")


def _check_size() -> None:
    declared = sum(item.width for item in TRANSITION_LAYOUT)
    if declared != TRANSITION_SIZE or _RECORD_STRUCT.size != TRANSITION_SIZE:
        raise AssertionError(
            f"internal error: transition layout declares {declared} bytes and "
            f"packs {_RECORD_STRUCT.size}, expected {TRANSITION_SIZE}"
        )


_check_size()


def _require_uint(value: int, bits: int, name: str) -> int:
    if type(value) is not int or not 0 <= value < (1 << bits):
        raise MapTransitionValueError(
            f"{name} must be an unsigned {bits}-bit integer, got {value!r}"
        )
    return value


def _require_interval(pair: object, name: str) -> tuple[int, int]:
    if not isinstance(pair, tuple) or len(pair) != 2:
        raise MapTransitionRegionError(
            f"{name} must be a (low, high) pair, got {pair!r}"
        )
    low = _require_uint(pair[0], 16, f"{name}[0]")
    high = _require_uint(pair[1], 16, f"{name}[1]")
    if low > high:
        raise MapTransitionRegionError(
            f"{name} is ({low}, {high}); the canonical corpus orders every "
            "interval low <= high on 735 of 735 records"
        )
    if low == high:
        raise MapTransitionRegionError(
            f"{name} is ({low}, {high}); the canonical corpus has no "
            "degenerate interval on 735 of 735 records"
        )
    return low, high


_REGION_STRUCT = struct.Struct("<HHHH")


@dataclass(frozen=True, slots=True)
class TransitionRegion:

    first: tuple[int, int]
    second: tuple[int, int]

    def __post_init__(self) -> None:
        _require_interval(self.first, "region first")
        _require_interval(self.second, "region second")

    def to_bytes(self) -> bytes:
        """The eight bytes as they appear at ``+0x08``: a, b, c, d."""
        return _REGION_STRUCT.pack(
            self.first[0], self.second[0], self.first[1], self.second[1]
        )


@dataclass(frozen=True, slots=True)
class TransitionRecord:

    class_raw: int
    constant_raw: int
    bound_a_raw: int
    bound_b_raw: int
    bound_c_raw: int
    bound_d_raw: int
    byte_0x10_raw: int
    destination_key_high: int
    destination_key_low: int
    byte_0x13_raw: int
    word_0x14_raw: int
    byte_0x16_raw: int
    byte_0x17_raw: int


    @classmethod
    def from_bytes(cls, data: bytes | bytearray | memoryview) -> "TransitionRecord":
        """Decode exactly 24 bytes. Length is the only thing checked here."""
        if len(data) != TRANSITION_SIZE:
            raise MapTransitionLengthError(
                f"a transition record is {TRANSITION_SIZE} bytes; got {len(data)}"
            )
        return cls(*_RECORD_STRUCT.unpack(bytes(data)))

    def to_bytes(self) -> bytes:
        """Re-encode to exactly 24 bytes, byte-identically for a decoded record."""
        return _RECORD_STRUCT.pack(*self._values())

    def _values(self) -> tuple[int, ...]:
        values = tuple(getattr(self, item.name) for item in fields(self))
        if len(values) != len(TRANSITION_LAYOUT):
            raise AssertionError("internal error: transition field list mismatch")
        for item, value in zip(TRANSITION_LAYOUT, values, strict=True):
            _require_uint(value, item.width * 8, item.name)
        return values


    @property
    def destination_key(self) -> bytes:
        """The destination map's two-byte ``MapEntry`` key, high byte first."""
        return bytes((self.destination_key_high, self.destination_key_low))

    @property
    def region(self) -> TransitionRegion:
        return TransitionRegion(
            first=(self.bound_a_raw, self.bound_c_raw),
            second=(self.bound_b_raw, self.bound_d_raw),
        )

    @property
    def is_supported_class(self) -> bool:
        return self.class_raw in SUPPORTED_CLASS_RAW


    def validate(self) -> "TransitionRecord":
        self._values()
        if not self.is_supported_class:
            raise MapTransitionFamilyError(
                f"class word {self.class_raw:#010x} is not a measured transition "
                "form; this project supports "
                + " and ".join(f"{value:#010x}" for value in sorted(SUPPORTED_CLASS_RAW))
            )
        # Reading `region` is the region check: `TransitionRegion` refuses an
        # unordered or degenerate interval in its own constructor, so there is
        # one statement of that rule rather than two.
        self.region
        return self


    def with_destination_key(self, key: bytes | bytearray | memoryview) -> "TransitionRecord":
        raw = bytes(key)
        if len(raw) != 2:
            raise MapTransitionValueError(
                f"a destination key is two bytes; got {len(raw)}"
            )
        return replace(
            self,
            destination_key_high=raw[0],
            destination_key_low=raw[1],
        )

    def with_region(self, region: TransitionRegion) -> "TransitionRecord":
        if not isinstance(region, TransitionRegion):
            raise MapTransitionRegionError(
                f"region must be a TransitionRegion, got {region!r}"
            )
        first_low, first_high = region.first
        second_low, second_high = region.second
        return replace(
            self,
            bound_a_raw=first_low,
            bound_b_raw=second_low,
            bound_c_raw=first_high,
            bound_d_raw=second_high,
        )

    @property
    def raw_coordinate_pair(self) -> "TransitionArrival | None":
        """The stored ``+0x14``/``+0x16`` pair verbatim, with NO semantics."""
        x = self.word_0x14_raw
        y = self.byte_0x16_raw | (self.byte_0x17_raw << 8)
        if x >= ARRIVAL_UNSET_MINIMUM or y >= ARRIVAL_UNSET_MINIMUM:
            return None
        return TransitionArrival(x=x, y=y)

    @property
    def arrival(self) -> "TransitionArrival | None":
        if not self.has_raw_arrival_pair:
            raise MapTransitionValueError(
                "a 169-class record's +0x14/+0x16 pair is a scene-relative delta, "
                "not an arrival point; use arrival_relative(scene_x, scene_y) for a "
                "point, or raw_coordinate_pair for the stored bytes"
            )
        return self.raw_coordinate_pair

    def with_arrival(self, arrival: "TransitionArrival | None") -> "TransitionRecord":
        if arrival is None:
            return replace(
                self,
                word_0x14_raw=0xFFFF,
                byte_0x16_raw=0xFF,
                byte_0x17_raw=0xFF,
            )
        if not isinstance(arrival, TransitionArrival):
            raise MapTransitionValueError(
                f"an arrival must be a TransitionArrival or None, got {arrival!r}"
            )
        return replace(
            self,
            word_0x14_raw=arrival.x,
            byte_0x16_raw=arrival.y & 0xFF,
            byte_0x17_raw=(arrival.y >> 8) & 0xFF,
        )


    @property
    def has_raw_arrival_pair(self) -> bool:
        """Whether ``+0x14``/``+0x16`` is the arrival **as stored**.
        * the **566 class** (``0x08007675``) passes the pair itself -
          ``08007600 adds r3,#0x14`` then ``0800760A bl 0x08008d44`` - so the
          stored pair IS the coordinate handed to the warp routine, and
          :attr:`arrival` is that value;
        * the **169 class** (``0x080072CD``) does not. It reads both halves and
          builds ``(scene_x + rec[+0x14] - rec[+0x08], scene_y + rec[+0x16] -
          rec[+0x0A])`` before handing that over, so the stored pair is a
          **scene-relative delta**, not an arrival. See
          :meth:`arrival_relative`.
        """
        return self.class_raw == TRANSITION_CLASS_A_RAW

    def arrival_relative(self, scene_x: int, scene_y: int) -> "TransitionArrival":
        """Only valid for the 169 class; a 566-class record is refused rather than given a delta."""
        if self.has_raw_arrival_pair:
            raise MapTransitionValueError(
                "a 566-class record's pair is already an absolute arrival; "
                "arrival_relative applies only to the 169 class"
            )
        for value, name in ((scene_x, "scene_x"), (scene_y, "scene_y")):
            if type(value) is not int:
                raise MapTransitionValueError(f"{name} must be an integer, got {value!r}")

        def signed16(value: int) -> int:
            value &= 0xFFFF
            return value - 0x10000 if value & 0x8000 else value

        x = (scene_x + signed16(self.word_0x14_raw) - signed16(self.bound_a_raw)) & 0xFFFF
        y = (scene_y + signed16(self.byte_0x16_raw | (self.byte_0x17_raw << 8))
             - signed16(self.bound_b_raw)) & 0xFFFF
        if x >= ARRIVAL_UNSET_MINIMUM or y >= ARRIVAL_UNSET_MINIMUM:
            raise MapTransitionValueError(
                f"the scene-relative arrival for this record is ({x}, {y}), which "
                "lands in the measured sentinel range and is therefore not a point"
            )
        return TransitionArrival(x=x, y=y)


    @property
    def facing(self) -> "TransitionFacing":
        """The ``+0x10`` byte, split the way the engine splits it.
        * the **low two bits are the door gate**, not the arrival facing. The 566
          constructor masks them - ``08007696 ldrb r0,[r5,#0x10]``,
          ``08007698 lsls r0,r0,#0x1c``, ``0800769A lsrs r0,r0,#0x1c`` - and uses
          them to index the four-byte table ``80 40 20 10`` at ``0x080707D8``,
          storing ``1 << (7 - (v & 3))`` at object ``+0x11``. That bit is compared
          against the door gate word at ``*(u16*)0x03003302``
          (``080075C2``/``080075C6``/``080075C8``).
        **Two different gate words, and they are not interchangeable.** This
        field's low bits select a bit of the door gate word at ``*(u16*)0x03003302``
        (compared at ``080075C6``). The word ``0x03001A34`` used by the runtime
        observer and by the tickets is a different address - the selector read at
        ``08008DA6``..``08008DB0`` - and what it selects is UNRESOLVED. Do not
        treat one as the other.
        """
        return TransitionFacing(raw=self.byte_0x10_raw)

    def with_gate_direction(self, direction: int) -> "TransitionRecord":
        if type(direction) is not int or not 0 <= direction <= FACING_MASK:
            raise MapTransitionValueError(
                f"a gate direction is 0..{FACING_MASK}, got {direction!r}"
            )
        return replace(
            self,
            byte_0x10_raw=(self.byte_0x10_raw & ~FACING_MASK) | direction,
        )

    def with_arrival_facing(self, direction: "int | None") -> "TransitionRecord":
        if direction is None:
            return replace(
                self, byte_0x10_raw=self.byte_0x10_raw & FACING_PRESERVED_MASK
            )
        if type(direction) is not int or not 0 <= direction <= FACING_MASK:
            raise MapTransitionValueError(
                f"an arrival facing is 0..{FACING_MASK} or None, got {direction!r}"
            )
        return replace(
            self,
            byte_0x10_raw=((direction + 1) << 4)
            | (self.byte_0x10_raw & FACING_PRESERVED_MASK),
        )

    def with_facing_raw(self, raw: int) -> "TransitionRecord":
        """Return this record with the whole ``+0x10`` byte replaced verbatim."""
        _require_uint(raw, 8, "facing byte")
        return replace(self, byte_0x10_raw=raw)


@dataclass(frozen=True, slots=True)
class TransitionFacing:
    """The ``+0x10`` byte: a door gate direction and an arrival-facing override.
    The direction order is ``0 = South, 1 = North, 2 = West, 3 = East``: the axis
    split (``{0,1}`` vertical by the sign of ``dy`` at actor ``+0x1A4``, ``{2,3}``
    horizontal by ``dx`` at ``+0x1A0``) is CONFIRMED at ``0x080159B0`` and
    ``0x0800A890``; the South/North/West/East labelling is INFERRED, not
    independently observed.
    """

    raw: int

    def __post_init__(self) -> None:
        _require_uint(self.raw, 8, "facing byte")

    @property
    def gate_direction(self) -> int:
        return self.raw & FACING_MASK

    @property
    def override_raw(self) -> int:
        return self.raw >> 4

    @property
    def arrival_direction(self) -> int | None:
        """The direction the record forces on arrival, or None when it is silent."""
        if self.override_raw == 0:
            return None
        return self.override_raw - 1

    @property
    def states_arrival_facing(self) -> bool:
        return self.override_raw != 0

    @property
    def direction(self) -> int | None:
        """Alias for :attr:`arrival_direction`; None means "not stated"."""
        return self.arrival_direction


FACING_MASK = 0x03

FACING_PRESERVED_MASK = 0x0F
FACING_SOUTH = 0
FACING_NORTH = 1
FACING_WEST = 2
FACING_EAST = 3

FACING_NAMES = {
    FACING_SOUTH: "South",
    FACING_NORTH: "North",
    FACING_WEST: "West",
    FACING_EAST: "East",
}


#: Creation does not support the 169 class, and the reason is measured rather than
#: stylistic: the 169 record's ``+0x14``/``+0x16`` pair is a **scene-relative
#: delta** - the engine builds ``(scene + delta - region_low)`` before handing the
#: point over (``0x08007234``..``0x08007258``, see
#: :meth:`TransitionRecord.arrival_relative`) - so "where the player arrives" is not
#: a value a project can state for that class without also measuring the scene
#: origin. The 566 class passes the pair through unchanged, which is what makes an
#: authored arrival a statement about the record alone.
CREATED_CLASS_RAW = TRANSITION_CLASS_A_RAW


#: * ``byte_0x10_raw`` - the high nibble is the authored arrival-facing override
#:   (``(direction + 1) << 4``, or ``0`` for "the record states none"), and the low
#:   nibble - the door gate bits and the two bits nothing was traced reading - is
#:   the template's, because no measured authoring vocabulary for the gate exists;
#: * ``class_raw`` and ``constant_raw`` are ``0`` because their meaning is
#:   UNRESOLVED: the created record carries the template's own class/constructor word
#:   and the corpus's invariant word rather than a value this project would be
#:   inventing;
#: * ``byte_0x13_raw`` is ``0`` for the same reason - an engine-read field
#:   (``0x08007282``) whose census is ``{0: 561, 1: 174}`` and whose meaning is
#:   UNRESOLVED.
CREATED_FIELD_AUTHORED_MASKS: dict[str, int] = {
    "class_raw": 0x00000000,
    "constant_raw": 0x00000000,
    "bound_a_raw": 0xFFFF,
    "bound_b_raw": 0xFFFF,
    "bound_c_raw": 0xFFFF,
    "bound_d_raw": 0xFFFF,
    "byte_0x10_raw": 0xFF & ~FACING_PRESERVED_MASK,
    "destination_key_high": 0xFF,
    "destination_key_low": 0xFF,
    "byte_0x13_raw": 0x00,
    "word_0x14_raw": 0xFFFF,
    "byte_0x16_raw": 0xFF,
    "byte_0x17_raw": 0xFF,
}

if set(CREATED_FIELD_AUTHORED_MASKS) != {item.name for item in TRANSITION_LAYOUT}:
    raise AssertionError(
        "internal error: the created-record field table does not name every "
        "physical field of the record"
    )


def compose_created_record(
    template: "TransitionRecord",
    *,
    destination_key: bytes | bytearray | memoryview,
    region: "TransitionRegion",
    arrival: "TransitionArrival | None",
    facing: int | None,
) -> "TransitionRecord":
    _require_uint(
        facing if facing is not None else 0, 8, "created arrival facing"
    )
    if facing is not None and not 0 <= facing <= FACING_MASK:
        raise MapTransitionValueError(
            f"a created arrival facing is 0..{FACING_MASK} or None, got {facing!r}"
        )
    record = (
        template.with_destination_key(destination_key)
        .with_region(region)
        .with_arrival(arrival)
    )
    override = ((facing + 1) << 4) if facing is not None else 0
    return replace(
        record,
        byte_0x10_raw=override | (template.byte_0x10_raw & FACING_PRESERVED_MASK),
    )


@dataclass(frozen=True, slots=True)
class TransitionArrival:

    x: int
    y: int

    def __post_init__(self) -> None:
        _require_uint(self.x, 16, "arrival x")
        _require_uint(self.y, 16, "arrival y")
        if self.x >= ARRIVAL_UNSET_MINIMUM or self.y >= ARRIVAL_UNSET_MINIMUM:
            raise MapTransitionValueError(
                f"arrival ({self.x}, {self.y}) overlaps the measured sentinel "
                f"range at or above {ARRIVAL_UNSET_MINIMUM:#06x}, which means "
                "'no authored arrival'; use None for that"
            )
