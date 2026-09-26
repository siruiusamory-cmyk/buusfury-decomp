"""Pure codec for the Buu's Fury selector-1-root connection records.

MAP-WARP-FORMAT-001. This module owns exactly one structure and nothing else:
the 24-byte record a map's selector-1 root reaches through its ``+0x40`` count /
``+0x44`` array pair. It performs no I/O, knows no profile and reaches no
address; a caller hands it 24 bytes and gets named fields back, or hands it
fields and gets 24 bytes.

**Evidence.** Every claim encoded here is established in
``docs/research/LOGX_CONNECTOR_PROVENANCE.md`` and nowhere else:

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
* ``+0x10``, ``+0x13``, ``+0x14``, ``+0x16`` and ``+0x17`` are engine-read
  fields whose semantics are UNRESOLVED (claims 19, 21), so they are preserved
  byte-for-byte and are not editable;
* ``+0x04`` is one invariant word on all 735 canonical records, and no evidence
  establishes what it is. It is preserved and deliberately **not** validated:
  enforcing a constant read off one image would turn a corpus coincidence into
  a format rule.

**Fail closed.** :meth:`TransitionRecord.validate` refuses a record whose class
word is outside the measured corpus, and refuses a region whose intervals are
unordered or degenerate. Both are refusals of *forms this project has not
measured*, not claims about what the engine would accept: the engine's own
limits are unknown, and the rule is stated as the corpus invariant it is.
"""

from __future__ import annotations

from dataclasses import dataclass, replace, fields
import struct

#: The record's engine-accessed extent, `+0x00..+0x17`.
TRANSITION_SIZE = 24

#: The two class words the canonical corpus tags records with.
TRANSITION_CLASS_A_RAW = 0x08007675
TRANSITION_CLASS_B_RAW = 0x080072CD

#: Every class word this codec has measured.
SUPPORTED_CLASS_RAW = frozenset({TRANSITION_CLASS_A_RAW, TRANSITION_CLASS_B_RAW})

#: ``u16`` endpoints are unsigned by their physical width. No evidence
#: establishes a signed interpretation, so none is applied.
BOUND_MINIMUM = 0x0000
BOUND_MAXIMUM = 0xFFFF


class MapTransitionError(ValueError):
    """Base error for the selector-1-root connection record."""


class MapTransitionLengthError(MapTransitionError):
    """Raised when a record is not exactly 24 bytes."""


class MapTransitionValueError(MapTransitionError):
    """Raised when a field cannot fit its physical width."""


class MapTransitionFamilyError(MapTransitionError):
    """Raised when a record is a transition form this project has not measured.

    Raised for an unrecognised class word. The supported family is the one the
    canonical corpus produced; anything else is refused rather than carried
    through a schema nothing establishes.
    """


class MapTransitionRegionError(MapTransitionError):
    """Raised for a region that is not two ordered, non-degenerate intervals."""


@dataclass(frozen=True, slots=True)
class TransitionField:
    offset: int
    width: int
    name: str


#: The record's physical layout, in the order the bytes appear. Names are
#: positional wherever the engine does not name the field, and a name never
#: claims a semantic the evidence does not carry.
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

#: `class_raw`, `constant_raw`, four `u16`, four bytes, one `u16`, two bytes.
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
    """Validate one ``(low, high)`` pair against the measured corpus rule."""
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
    """The record's two ordered intervals, named by position, not by axis.

    ``first`` is the pair stored at ``+0x08`` (low) and ``+0x0C`` (high);
    ``second`` the pair at ``+0x0A`` (low) and ``+0x0E`` (high). The engine
    copies these eight bytes into an object it compares as ordered intervals,
    which is what makes "two ordered pairs" a CONFIRMED reading. Whether
    ``first`` is horizontal or vertical, and what unit the endpoints are in, is
    **UNRESOLVED**; no axis name is used here for that reason.

    Both intervals are non-degenerate and no wider than their ``u16`` fields.
    """

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
    """One connection record, decoded without interpreting an unknown field."""

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

    # --- physical access -------------------------------------------------

    @classmethod
    def from_bytes(cls, data: bytes | bytearray | memoryview) -> "TransitionRecord":
        """Decode exactly 24 bytes. Length is the only thing checked here.

        A caller that needs the record to be a *supported* form asks
        :meth:`validate`; keeping the two apart is what lets an unsupported
        record be reported with its own reason rather than as a decode failure.
        """
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

    # --- semantic access -------------------------------------------------

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

    # --- validation ------------------------------------------------------

    def validate(self) -> "TransitionRecord":
        """Refuse an unsupported form. Returns ``self`` so a caller can chain.

        Refused here, each because this project has not measured the form and a
        schema for it would therefore be invented:

        * a class word outside :data:`SUPPORTED_CLASS_RAW`;
        * a region whose intervals are unordered or degenerate.

        Deliberately **not** checked: ``constant_raw``, whose single canonical
        value is a corpus coincidence rather than a rule, and the four
        `UNRESOLVED` bytes at ``+0x10``, ``+0x13``, ``+0x16`` and ``+0x17``,
        whose canonical spread is real retail data.
        """
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

    # --- controlled edits ------------------------------------------------

    def with_destination_key(self, key: bytes | bytearray | memoryview) -> "TransitionRecord":
        """Return this record pointed at the two-byte destination ``key``.

        The key is the destination map's own ``MapEntry`` two-byte lookup key,
        which is the only thing the engine resolves from a record. Nothing else
        in the record moves.
        """
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
        """Return this record with a different pair of intervals.

        ``region`` is validated before it is written, so an unordered or
        degenerate interval never reaches a plan.
        """
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
