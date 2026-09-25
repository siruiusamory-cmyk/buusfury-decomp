"""Packed text-handle decode, AUTHORING and recovery for one verified ROM profile.

A decoded string has no ROM address of its own; the durable identity is the
packed u32 an event-resource record stores to address it. This module is the
**only** place in the toolkit that knows that word's bit layout: it decodes,
it validates, and - since DIALOGUE-VARIABLE-LENGTH-001 - it *authors* a
replacement handle from semantic fields. Every writer path calls
:class:`DialogueHandle`; none of them shifts bits itself.

The bit layout (CONFIRMED)
--------------------------

::

    bits 21-31   decoded length, in halfwords   (11 bits, 0..0x7FF)
    bits  6-20   decoded start,  in halfwords   (15 bits, 0..0x7FFF)
    bits  0-5    container/selector identity    ( 6 bits, 0..0x3F)

6 + 15 + 11 is exactly 32, so **there are no reserved bits** and no field
overlaps another.

The layout is not inferred from this field's shape. It was corroborated in situ
by the ``lsls #26 / lsrs #24`` pair at ``0x08012244``/``0x08012246`` behind the
retail consumer at ``0x08012240``, which loads the handle from the record's
``+0x04`` and then isolates these three fields (TEXT-HANDLE-001, TEXT-HANDLE-002,
both runtime-proven). The canonical target decodes under it to
``(selector 1, decoded start 0x132, decoded length 0x20)``, which is exactly the
span the live engine read and displayed.

Both offset fields are counted in HALFWORDS because the payload is UTF-16LE:
every legal record therefore starts on an even byte and has an even byte length.
A zero decoded length is not a legal handle - it names nothing - and
:class:`DialogueHandle` refuses it rather than letting an empty record into an
image.

What the field can hold, and what has been proven (DIALOGUE-VARIABLE-LENGTH-001)
------------------------------------------------------------------------------

These are deliberately separate numbers and must not be collapsed:

* **ENCODABLE** - the 11-bit length field holds up to ``0x7FF`` halfwords =
  **4094 decoded bytes**, and the 15-bit start field addresses up to
  ``0x7FFF`` halfwords = **65534 bytes** into a decoded container. Both are
  arithmetic properties of the layout.
* **PRODUCTION-BOUNDED** - the toolkit's own container decoder refuses a
  declared decoded size above ``webfoot_lz.DEFAULT_MAX_OUTPUT`` (64 KiB), which
  a retail dialogue container already nearly fills, so the *practical* growth a
  replacement can buy is much smaller than the field's arithmetic maximum. The
  refusal is enforced at the layout, not here.
* **ENGINE-PROVEN** - the longest decoded record a real derivative has had
  displayed by the retail engine is **72 bytes** (this ticket's authored line).
  Nothing here claims the field's maximum is runtime-safe merely because it
  encodes; see ``docs/research/ROM_DIALOGUE_VARIABLE_LENGTH.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct

from .binary import GBA_ROM_BASE


class HandleError(ValueError):
    """A semantic handle request cannot be encoded, or a word is not a handle.

    One class, because every caller either uses a handle or refuses it; nothing
    in this project branches on which field was wrong beyond the message.
    """


# --- the ONE bit layout -------------------------------------------------------
#
# Every constant below is defined once and used by both directions. `_split` and
# `_join` are the only two functions in the toolkit that perform handle bit
# arithmetic; `unpack_handle` and `DialogueHandle` are thin semantic layers over
# them. A second implementation is how a writer and a reader silently disagree
# about a record's identity.

#: Bits 0-5: the decoded container the record lives in.
HANDLE_SELECTOR_BITS = 6
HANDLE_SELECTOR_MASK = 0x3F
#: Bits 6-20: the record's start inside that container, in halfwords.
HANDLE_START_SHIFT = 6
HANDLE_START_BITS = 15
HANDLE_START_MASK = 0x7FFF
#: Bits 21-31: the record's length, in halfwords.
HANDLE_LENGTH_SHIFT = 21
HANDLE_LENGTH_BITS = 11
HANDLE_LENGTH_MASK = 0x7FF

#: Both offset fields count UTF-16LE code units, so one unit is two bytes.
HANDLE_UNIT_BYTES = 2
#: The decoded byte offset the start field can address: 0x7FFF halfwords.
HANDLE_START_MAX_BYTES = HANDLE_START_MASK * HANDLE_UNIT_BYTES
#: The decoded byte length the length field can encode: 0x7FF halfwords.
HANDLE_LENGTH_MAX_BYTES = HANDLE_LENGTH_MASK * HANDLE_UNIT_BYTES

#: The toolkit's only measured structural bound on selector identity: the
#: container table holds **seven** pointers (ROM-CAPACITY-AND-ALLOCATION-001
#: Checkpoint A). It is recorded here as evidence, not enforced as a format
#: limit - the field itself is six bits wide.
HANDLE_MEASURED_CONTAINER_COUNT = 7


def _split(value: int) -> tuple[int, int, int]:
    """``(selector, start in halfwords, length in halfwords)``. THE decode."""
    return (value & HANDLE_SELECTOR_MASK,
            (value >> HANDLE_START_SHIFT) & HANDLE_START_MASK,
            (value >> HANDLE_LENGTH_SHIFT) & HANDLE_LENGTH_MASK)


def _join(selector: int, start_halfwords: int, length_halfwords: int) -> int:
    """Pack three validated fields. THE encode.

    Private on purpose: callers name semantic byte fields through
    :class:`DialogueHandle`, so no writer path performs a shift of its own.
    """
    return (selector
            | (start_halfwords << HANDLE_START_SHIFT)
            | (length_halfwords << HANDLE_LENGTH_SHIFT))


def unpack_handle(value: int) -> tuple[int, int, int]:
    """``(selector, decoded start, decoded length)``, the last two in BYTES.

    TOTAL over every u32, including words that are not legal handles: this is
    the *filter* the reference inventory scans with, so it must answer for any
    word it is handed. Words whose length field is zero decode to a length of
    zero and are rejected by the caller's own in-gate test, never here.
    """
    selector, start_halfwords, length_halfwords = _split(value)
    return (selector,
            start_halfwords * HANDLE_UNIT_BYTES,
            length_halfwords * HANDLE_UNIT_BYTES)


def validate_selector(selector: object) -> int:
    """The selector as a 6-bit container identity, or :class:`HandleError`."""
    if type(selector) is not int or not 0 <= selector <= HANDLE_SELECTOR_MASK:
        raise HandleError(
            f"handle selector {selector!r} is not an integer in "
            f"0..{HANDLE_SELECTOR_MASK}"
        )
    return selector


def validate_decoded_start(decoded_start: object) -> int:
    """A decoded byte offset the start field can hold, or :class:`HandleError`."""
    if type(decoded_start) is not int or decoded_start < 0:
        raise HandleError(
            f"decoded start {decoded_start!r} is not a non-negative byte offset"
        )
    if decoded_start % HANDLE_UNIT_BYTES:
        raise HandleError(
            f"decoded start {decoded_start} is not a whole number of "
            f"{HANDLE_UNIT_BYTES}-byte units; the field counts halfwords"
        )
    if decoded_start > HANDLE_START_MAX_BYTES:
        raise HandleError(
            f"decoded start {decoded_start} exceeds the "
            f"{HANDLE_START_MAX_BYTES}-byte maximum the start field addresses"
        )
    return decoded_start


def validate_decoded_length(decoded_length: object) -> int:
    """A decoded byte length the length field can hold, or :class:`HandleError`."""
    if type(decoded_length) is not int or decoded_length <= 0:
        raise HandleError(
            f"decoded length {decoded_length!r} is not a positive byte count; a "
            "handle of length zero names no record"
        )
    if decoded_length % HANDLE_UNIT_BYTES:
        raise HandleError(
            f"decoded length {decoded_length} is not a whole number of "
            f"{HANDLE_UNIT_BYTES}-byte units; the field counts halfwords"
        )
    if decoded_length > HANDLE_LENGTH_MAX_BYTES:
        raise HandleError(
            f"decoded length {decoded_length} exceeds the "
            f"{HANDLE_LENGTH_MAX_BYTES}-byte maximum the length field encodes"
        )
    return decoded_length


@dataclass(frozen=True, slots=True)
class DialogueHandle:
    """One dialogue record's durable identity, as semantic fields.

    This is the authoring representation the ticket asks for: a caller decodes
    an existing handle, changes a field, and encodes the result::

        handle = DialogueHandle.decode(0x02002641)
        widened = replace(handle, decoded_length=72)
        widened.encode()

    Every field is validated on construction, so an unencodable handle cannot
    reach a writer, and the round trip is exact for every legal handle.
    """

    #: Which decoded container holds the record (bits 0-5).
    selector: int
    #: Byte offset of the record inside that container's decoded data.
    decoded_start: int
    #: Byte length of the record's decoded data.
    decoded_length: int

    def __post_init__(self) -> None:
        validate_selector(self.selector)
        validate_decoded_start(self.decoded_start)
        validate_decoded_length(self.decoded_length)

    @classmethod
    def decode(cls, value: int) -> "DialogueHandle":
        """Build a handle from a packed word, refusing a word that is not one.

        The inverse of :meth:`encode`, and the entry point a replacement edit
        starts from: the existing durable handle is decoded, its length field is
        modified, and the result is encoded again.
        """
        if type(value) is not int:
            raise HandleError(f"a packed handle must be an integer, not {value!r}")
        selector, decoded_start, decoded_length = unpack_handle(value)
        return cls(selector, decoded_start, decoded_length)

    def encode(self) -> int:
        """The packed u32 a record stores in its ``+0x04`` handle field."""
        return _join(self.selector,
                     self.decoded_start // HANDLE_UNIT_BYTES,
                     self.decoded_length // HANDLE_UNIT_BYTES)

    def replace(self, **fields: int) -> "DialogueHandle":
        """This handle with named semantic fields changed.

        ``handle.replace(decoded_length=72)`` is the whole authoring operation;
        no caller writes a shift or a mask.
        """
        unknown = set(fields) - {"selector", "decoded_start", "decoded_length"}
        if unknown:
            raise HandleError(
                f"unknown durable-handle field(s): {', '.join(sorted(unknown))}"
            )
        return DialogueHandle(*(fields.get(name, getattr(self, name))
                                for name in ("selector", "decoded_start",
                                             "decoded_length")))

    @property
    def decoded_end(self) -> int:
        """Exclusive end of the record inside the decoded container."""
        return self.decoded_start + self.decoded_length

    def to_json(self) -> dict:
        return {
            "packed_handle": f"0x{self.encode():08X}",
            "selector": self.selector,
            "decoded_start": self.decoded_start,
            "decoded_length": self.decoded_length,
            "decoded_end": self.decoded_end,
        }


def pack_handle(selector: int, decoded_start: int, decoded_length: int) -> int:
    """Encode three semantic fields, refusing anything the field cannot hold."""
    return DialogueHandle(selector, decoded_start, decoded_length).encode()


def recover_handle(image: bytes, container_index: int, phrase_start: int,
                   phrase_size: int) -> dict:
    """Name one decoded phrase by the ROM-resident handle that defines it.

    A decoded string has no ROM address of its own — it exists only after
    decompression — so the durable identity is the packed u32 an event-resource
    record stores to address it. This walks the record pool for word-aligned
    occurrences of the handle the phrase's own span implies.

    The span must be the PHRASE's, never the indexed run's. Runs are segmented
    by control units and routinely merge several handle-defined records: the
    real run at decoded offset 0x12A spans nine distinct handles, so keying on
    it would return nine identities for one phrase. That is the same collapse
    the result shape forbids, in mirror image.

    A phrase is a SUBSTRING of the record that holds it — a searcher types part
    of a message, not all of it — so the record is the one whose span CONTAINS
    the phrase's. Containment alone is not enough to name one record, because
    long records overlap short ones: searching the target phrase finds thirteen
    containing records, most of them unrelated messages that merely span the
    same bytes. The narrowest containing record is the answer, being the
    tightest one that still covers every character searched for.

    Returns ONE identity or none. Never a guess: a span no record covers
    reports its absence and says why.
    """
    from .data.placement_contracts import CONTRACTS

    resource = CONTRACTS["buus_fury_usa_rev0_01c1707f"]["event_resource"]
    pool = resource["pool_start"] - GBA_ROM_BASE
    table = resource["table"] - GBA_ROM_BASE
    if not 0 <= pool < table <= len(image):
        return {"packed_handle": None,
                "unrecovered_because": "the event-resource record pool lies "
                                       "outside this image"}

    phrase_end = phrase_start + phrase_size
    sites: dict[int, list[int]] = {}
    handle = None
    narrowest = None
    for offset in range(pool, table, 4):
        value = struct.unpack_from("<I", image, offset)[0]
        selector, start, size = unpack_handle(value)
        if (selector != container_index or not size
                or start > phrase_start or phrase_end > start + size):
            continue
        sites.setdefault(value, []).append(GBA_ROM_BASE + offset)
        # Ties break on the handle value so one image always answers the same
        # way; a search result that reordered between runs would not be citable.
        if narrowest is None or (size, value) < narrowest:
            narrowest, handle = (size, value), value

    references = [] if handle is None else sites[handle]

    if handle is None:
        return {"packed_handle": None,
                "unrecovered_because": "no event-resource record addresses this "
                                       "exact decoded span; the phrase may sit "
                                       "inside a larger record rather than at "
                                       "its boundary"}

    selector, start, size = unpack_handle(handle)
    return {
        "packed_handle": f"0x{handle:08X}",
        "handle_selector": selector,
        "handle_decoded_start": f"0x{start:X}",
        "handle_decoded_length": f"0x{size:X}",
        # One identity, a LIST of sites. The handle NAMES the string; these are
        # the places a patcher would rewrite to repoint it. Collapsing the two
        # would turn one message into several.
        "reference_sites": [f"0x{site:08X}" for site in references],
        "reference_site_count": len(references),
    }
