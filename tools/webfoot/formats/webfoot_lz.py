"""The Webfoot container: an eight-byte header over a packed bitstream.

TOOLKIT-010. This is the compression layer that every Buu's Fury sprite payload
sits behind, and it is deliberately the *only* module in this project that knows
how those bits are laid out. It does no I/O and takes no addresses: callers hand
it ``bytes`` and an offset, exactly as `webfoot.formats` requires.

**Provenance.** The bit grammar is promoted from `spicybung/DragonByteZ`
(`src/compression.cpp`, MIT licensed, pinned in `upstreams.lock`), so this is
VERIFIED_UPSTREAM rather than a fresh derivation. It was not taken on trust: see
`docs/research/GRAPHICS_FORMAT.md` for the independent check against the
canonical image, in which all **7,390** container offsets reachable by a sprite
piece decode with zero failures *and* every decoded length equals the width times
height that the referring piece record independently declares - 11,005 of 11,005
piece references. Two unrelated structures agreeing on all 7,390 samples is what
promoted this from plausible to CONFIRMED_ROM. (The earlier published figure was
7,355, from the refuted reading that modelled a 16-byte piece stride and could not
see the 21 multi-piece frames; it is exactly the single-piece subset, so it is a
*population*, not the corpus total.)

**Header.** Two little-endian words:

    +0x00  kind            0 = stored, 1 and 2 = packed
    +0x04  declared_size   length of the decoded output, in bytes

``kind`` is not merely a tag. For a packed stream it *is* the initial literal
width in bits, which is why the two packed kinds share one decoder rather than
needing two. Every sprite container in the canonical image is kind 1; kind 0 and
kind 2 are implemented because the header defines them, and are exercised by
synthetic fixtures rather than by ROM data.

**Bit order.** Bits are consumed most-significant-first out of little-endian
32-bit words. A decoder that reads bytes instead of words produces plausible
garbage on the first back-reference, so the word framing is load-bearing.

**What the packed grammar encodes.** A prefix code selects between a literal, a
long back-reference with an Elias-gamma-style length, a re-use of the previous
distance, a short 7-bit distance, a run of raw bytes, and two control escapes
that re-tune the distance width and the literal base/width mid-stream. The
length of a long match is biased by its own distance, which is the one part of
the format that cannot be guessed from first principles and the strongest single
reason to promote a verified implementation rather than invent one.

**On re-encoding.** :func:`pack` produces a *valid* stream - one this module's
own decoder reads back exactly - and nothing more. It is not Webfoot's original
compressor and does not reproduce its bytes. Measured over the canonical corpus
it lands at a median 1.06x the original packed size, which matters because the
corpus has no slack: roughly one payload in two hundred re-encodes small enough
to fit its own allocation. That is a stated limit, not a defect to be worked
around by writing past a container's end.

**Strictness: what "decoded successfully" means here.** The decoder returns a
container only when it produced *exactly* the declared number of bytes under the
whole format contract, and it raises :class:`ContainerError` otherwise. Stated
exactly, a stream succeeds only when all of these hold:

* the header is inside the image and the declared size is within the caller's
  safety limit, checked before any allocation;
* the bit reader never has to read a word past the end of the image, so a
  truncated control, literal or match field is a failure rather than a short read;
* every back-reference names an offset strictly inside the output produced so
  far - distance 0 and a distance greater than the output so far are both
  malformed, never a wrap-around;
* no token carries the output *past* the declared size. A match that would
  produce more bytes than the header declares is malformed, and so is a
  raw-literal run that would: both carry their own extent, so the decoder refuses
  them rather than writing what fits and reporting success;
* the token stream reaches the declared size exactly. A stream that stops early -
  by its end marker or by exhaustion - is refused.

The one thing it does not require is the stream's own end marker, because this
project's :func:`pack` terminates by output length and never emits one. The engine
has no output counter either - it writes until the stream's own escape and performs
no size comparison at all, as `tools/research/webfoot_codec_reference.py` records
from the `strb`/`ldr` reads and the dispatcher's two-argument call. In this corpus
that escape falls at exactly the declared length: the export-side reader requires
it there and all 7,390 containers pass that stronger check, which is why the marker
is an additional canonical-corpus observation rather than a requirement here.

**The defect this replaced (EVIDENCE-RISK-DEBT-001).** Two token classes used to
stop appending once the output reached the declared size, so a stream whose final
match - or whose raw-literal run - overran was *clipped* and reported as a
success. The match path (``copy_match``) was repaired first; an independent review
of that fix found the raw-literal-run path still open, and it was closed in the
same ticket. Measured on the canonical image, refusing instead of clipping changes
no accepted decode, and the two paths are provably inert there for different
reasons: no container's match reaches the bound (all 7,390 already produce exactly
their declared size, checked with the reference's end-marker mode), and **no
canonical container uses the raw-literal-run token at all**, so the run-path rule
cannot fire. The negative tests that pin both refusals are
in `tests/unit/test_webfoot_lz.py`; the previously documented reproduction is
`test_a_final_match_overrunning_the_declared_size_is_refused`.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct


#: Container kinds the header defines. ``kind`` doubles as the initial literal
#: width for packed streams, so this is a value set rather than an enum: the
#: number is used arithmetically, not merely compared.
STORED = 0
PACKED_KINDS = (1, 2)

#: Header is two words. Payload begins immediately after.
HEADER_SIZE = 8

#: A decoded sprite payload is at most 4 KiB in this corpus (the largest OBJ
#: shape is 64x64 at 8bpp). The cap sits an order of magnitude above that so a
#: corrupt or misread header cannot make the decoder allocate without bound; it
#: is a safety limit, not a format fact.
DEFAULT_MAX_OUTPUT = 64 * 1024


class ContainerError(ValueError):
    """Raised when a container header or its packed stream is not well formed.

    One class, because every caller either decodes or refuses. Callers that need
    to tell a bad header from a truncated stream read the message; nothing in
    this project branches on the distinction.
    """


@dataclass(frozen=True)
class Container:
    """One decoded container plus the exact input extent it consumed.

    ``packed_end`` is the field that makes safe editing possible at all: the
    difference between it and ``offset`` is the only capacity a re-encoded
    payload may occupy, because the corpus is packed with no slack. It is
    computed by running the decoder, never by trusting a length field, because
    the header declares the *decoded* size and says nothing about the packed one.
    """

    offset: int
    kind: int
    declared_size: int
    packed_end: int
    data: bytes

    @property
    def packed_size(self) -> int:
        """Bytes of the image this container occupies, header included."""
        return self.packed_end - self.offset


class _WordBitReader:
    """MSB-first bit reader over little-endian 32-bit words.

    Kept private: the word framing is a property of this container format, not a
    general-purpose utility, and exposing it would invite reuse for a format that
    frames its bits differently.
    """

    __slots__ = ("_data", "_position", "_word", "_remaining")

    def __init__(self, data: bytes, offset: int) -> None:
        self._data = data
        self._position = offset
        self._word = 0
        self._remaining = 0

    def bit(self) -> int:
        if self._remaining == 0:
            if self._position + 4 > len(self._data):
                raise ContainerError("packed stream ended inside a bit word")
            self._word = struct.unpack_from("<I", self._data, self._position)[0]
            self._position += 4
            self._remaining = 32
        result = (self._word >> 31) & 1
        self._word = (self._word << 1) & 0xFFFFFFFF
        self._remaining -= 1
        return result

    def get(self, count: int) -> int:
        value = 0
        for _ in range(count):
            value = (value << 1) | self.bit()
        return value

    @property
    def position(self) -> int:
        return self._position


def _gamma(reader: _WordBitReader) -> int:
    """Elias-gamma-style value: interleaved payload and continuation bits."""
    value = 1
    while True:
        value = (value << 1) | reader.bit()
        if reader.bit() == 0:
            return value


def _emit_raw(out: bytearray, value: int, expected: int) -> None:
    """Append one byte of a raw-literal run, refusing to pass the declared size.

    The run is delimited by its own terminator bit, so a run that would write
    past the declared size is a malformed stream - not a run to shorten. The
    export-side reader states the same rule in its own ``_emit_raw``; the two
    are deliberately separate implementations rather than one shared helper,
    because the export reader exists to be an independent check on this one.
    """
    if len(out) >= expected:
        raise ContainerError(
            f"raw literal run at output offset {len(out)} overruns the declared "
            f"{expected}"
        )
    out.append(value)


def _unpack_stream(
    data: bytes,
    payload: int,
    expected: int,
    initial_literal_bits: int,
) -> tuple[bytes, int]:
    """Decode ``expected`` bytes starting at ``payload``.

    Returns the bytes and the reader's final word position. The module docstring
    states the full success contract; the short version is that a token which
    would carry the output past ``expected`` is refused rather than clipped, so a
    returned container always means "exactly this many bytes were produced
    honestly". A stream that ends early is refused for the same reason: silently
    yielding a partial tile would put wrong pixels into a sprite without anything
    downstream noticing.
    """
    reader = _WordBitReader(data, payload)
    out = bytearray()
    literal_base = 0
    literal_bits = initial_literal_bits
    distance_bits = 8
    previous_distance = 1

    def copy_match(distance: int, count: int) -> None:
        if distance == 0 or distance > len(out):
            raise ContainerError(
                f"back-reference distance {distance} at output offset {len(out)} "
                "points outside the decoded output"
            )
        if len(out) + count > expected:
            raise ContainerError(
                f"match at output offset {len(out)} would produce "
                f"{len(out) + count} bytes against a declared {expected}"
            )
        for _ in range(count):
            out.append(out[-distance])

    while len(out) < expected:
        if reader.bit():
            out.append((literal_base + reader.get(literal_bits)) & 0xFF)
            continue

        if reader.bit():
            distance_code = _gamma(reader)
            if distance_code == 2:
                copy_match(previous_distance, _gamma(reader))
                continue
            distance = reader.get(distance_bits) + ((distance_code - 3) << distance_bits)
            previous_distance = distance
            count = _gamma(reader)
            # The match length is biased by its own distance. This ladder is
            # verbatim from the verified upstream; the thresholds are not
            # derivable from first principles and must not be "tidied" into a
            # formula.
            if distance >= 0x10000:
                count += 3
            elif distance >= 0x37FF:
                count += 2
            elif distance >= 0x027F:
                count += 1
            elif distance <= 0x007F:
                count += 4
            copy_match(distance, count)
            continue

        if reader.bit() == 0:
            distance = reader.get(7)
            if distance != 0:
                previous_distance = distance
                copy_match(distance, reader.get(2) + 2)
                continue
            width = reader.get(2)
            if width == 0:
                break
            distance_bits = reader.get(width + 3)
            continue

        short_distance = reader.get(4) - 1
        if short_distance == 0:
            out.append(literal_base & 0xFF)
        elif short_distance > 0:
            copy_match(short_distance, 1)
        elif reader.bit():
            # A run of raw 8-bit literals, ended by a clear bit. It is emitted
            # whole or refused: the run carries its own terminator, so stopping
            # once the output reached the declared size would discard literals
            # the stream actually encodes - the same silent clip the match path
            # no longer performs. EVIDENCE-RISK-DEBT-001 closed both paths; an
            # independent review found this one still open in the first pass.
            while True:
                _emit_raw(out, reader.get(8), expected)
                _emit_raw(out, reader.get(8), expected)
                if reader.bit() == 0:
                    break
        else:
            literal_bits = 7 + reader.bit()
            if literal_bits != 8:
                literal_base = reader.get(8)

    if len(out) != expected:
        raise ContainerError(
            f"packed stream decoded {len(out)} bytes against a declared {expected}"
        )
    return bytes(out), reader.position


def read_header(data: bytes, offset: int) -> tuple[int, int]:
    """Return ``(kind, declared_size)`` without decoding the payload."""
    if offset < 0 or offset + HEADER_SIZE > len(data):
        raise ContainerError(f"container header at {offset:#x} is outside the image")
    kind, declared = struct.unpack_from("<II", data, offset)
    return kind, declared


def looks_like_container(
    data: bytes,
    offset: int,
    *,
    minimum_size: int = 1,
    maximum_size: int = DEFAULT_MAX_OUTPUT,
) -> bool:
    """Cheap structural plausibility test, used while walking pointers.

    This is a filter, not a decision: it rejects obvious non-containers without
    paying for a decode. Callers needing certainty call :func:`unpack`, which
    either produces bytes or raises.
    """
    if offset < 0 or offset + HEADER_SIZE > len(data):
        return False
    kind, declared = struct.unpack_from("<II", data, offset)
    return kind <= 2 and minimum_size <= declared <= maximum_size


def unpack(
    data: bytes,
    offset: int,
    *,
    maximum_output: int = DEFAULT_MAX_OUTPUT,
) -> Container:
    """Decode the container at ``offset``.

    ``maximum_output`` is checked against the *declared* size before any
    allocation, so a wild header is refused rather than honoured.
    """
    kind, declared = read_header(data, offset)
    if declared > maximum_output:
        raise ContainerError(
            f"container at {offset:#x} declares {declared} bytes, over the "
            f"{maximum_output}-byte safety limit"
        )

    payload = offset + HEADER_SIZE
    if kind == STORED:
        if payload + declared > len(data):
            raise ContainerError(f"stored container at {offset:#x} runs past the image")
        return Container(
            offset=offset,
            kind=kind,
            declared_size=declared,
            packed_end=payload + declared,
            data=data[payload : payload + declared],
        )
    if kind in PACKED_KINDS:
        decoded, end = _unpack_stream(data, payload, declared, kind)
        return Container(
            offset=offset,
            kind=kind,
            declared_size=declared,
            packed_end=end,
            data=decoded,
        )
    raise ContainerError(f"unsupported Webfoot container kind {kind} at {offset:#x}")


def unpack_raw_stream(
    data: bytes,
    offset: int,
    expected_size: int,
    *,
    initial_literal_bits: int = 8,
) -> bytes:
    """Decode a headerless Webfoot bitstream of a caller-proven size.

    Some engine-owned records store the same packed grammar without the usual
    eight-byte container header.  Their surrounding record supplies both the
    decoded byte count and initial literal width.  This entry point preserves
    that distinction: it never guesses a size from the stream and it rejects
    invalid widths and bounds before delegating to the shared decoder.
    """
    if expected_size < 0:
        raise ContainerError(f"negative raw-stream size {expected_size}")
    if expected_size > DEFAULT_MAX_OUTPUT:
        raise ContainerError(
            f"raw stream declares {expected_size} bytes, over the "
            f"{DEFAULT_MAX_OUTPUT}-byte safety limit"
        )
    if initial_literal_bits not in range(1, 9):
        raise ContainerError(
            f"raw stream literal width {initial_literal_bits} is outside 1..8"
        )
    if not 0 <= offset <= len(data):
        raise ContainerError(f"raw stream at {offset:#x} is outside the image")
    decoded, _packed_end = _unpack_stream(
        data, offset, expected_size, initial_literal_bits
    )
    return decoded


def build_stored(payload: bytes) -> bytes:
    """Build a ``kind 0`` container carrying ``payload`` verbatim.

    Correct by construction - a stored container is the identity transform
    behind a header this project has verified - but almost never *usable* for an
    in-place edit in this corpus. Measured over all 7,390 sprite containers the
    packed form is between 1.6% and 73.5% of the header-plus-raw size (median
    32.6%), so a stored rewrite exceeds the original allocation in every single
    case: 0 of 7,390 would fit. It is kept because the header defines the kind and
    a profile that one day declares free space could use it. Nothing in the
    current write path does.
    """
    return struct.pack("<II", STORED, len(payload)) + payload


# --- packing -----------------------------------------------------------------
#
# The encoder below mirrors `_unpack_stream` and nothing more. It is NOT a
# reimplementation of Webfoot's compressor and does not attempt to match its
# output: it emits tokens the verified decoder accepts, and correctness is
# established by decoding its output again rather than by comparing against
# original bytes. What it cannot promise is size - see the module docstring.

#: Distance bits the encoder uses. The format permits retuning this mid-stream;
#: the encoder holds it at the decoder's initial value so it never has to track
#: a second piece of state, costing a few bits on the longest matches.
_ENCODER_DISTANCE_BITS = 8
_ENCODER_DISTANCE_MASK = (1 << _ENCODER_DISTANCE_BITS) - 1

#: Longest match emitted, and the widest window searched.
_MAX_MATCH = 255
_MAX_WINDOW = 0xFFFF

#: Candidate positions examined per offset. The cap keeps packing near-linear on
#: highly repetitive tile data; raising it buys fractions of a percent.
_CHAIN_LIMIT = 32


class _WordBitWriter:
    """MSB-first bit writer producing little-endian 32-bit words."""

    __slots__ = ("_words", "_current", "_count")

    def __init__(self) -> None:
        self._words: list[int] = []
        self._current = 0
        self._count = 0

    def bit(self, value: int) -> None:
        self._current = ((self._current << 1) | (value & 1)) & 0xFFFFFFFF
        self._count += 1
        if self._count == 32:
            self._words.append(self._current)
            self._current = 0
            self._count = 0

    def put(self, value: int, width: int) -> None:
        for shift in range(width - 1, -1, -1):
            self.bit((value >> shift) & 1)

    def gamma(self, value: int) -> None:
        """Inverse of :func:`_gamma`: payload bits interleaved with continuations."""
        if value < 2:
            raise ContainerError(f"gamma cannot encode {value}")
        for shift in range(value.bit_length() - 2, -1, -1):
            self.bit((value >> shift) & 1)
            self.bit(0 if shift == 0 else 1)

    def finish(self) -> bytes:
        # Trailing bits are padded with zeroes to a whole word. The decoder
        # stops on the declared output length, so the padding is never read.
        while self._count:
            self.bit(0)
        return b"".join(struct.pack("<I", word) for word in self._words)


def _length_bias(distance: int) -> int:
    """The count bias `_unpack_stream` adds back for a match at this distance."""
    if distance >= 0x10000:
        return 3
    if distance >= 0x37FF:
        return 2
    if distance >= 0x027F:
        return 1
    if distance <= 0x007F:
        return 4
    return 0


def _gamma_cost(value: int) -> int:
    return 2 * (value.bit_length() - 1)


def pack(payload: bytes) -> bytes:
    """Encode ``payload`` into a ``kind 2`` container the decoder accepts.

    Greedy: at each position the cheapest token by bits-per-byte wins. An
    optimal parse was tried and did not pay for itself, so the simpler one
    stands.
    """
    writer = _WordBitWriter()
    # Kind 2 begins with 2-bit literals, which are useless for tile data. The
    # opening tokens take the control escape that widens literals to 8 bits:
    # prefix 0,0,1 reaches the short-distance branch, a zero 4-bit field makes
    # it -1, then 0,1 selects "literal_bits = 7 + 1" with no base byte to read.
    writer.bit(0)
    writer.bit(0)
    writer.bit(1)
    writer.put(0, 4)
    writer.bit(0)
    writer.bit(1)

    positions: dict[bytes, list[int]] = {}
    total = len(payload)
    cursor = 0
    previous_distance = 1

    while cursor < total:
        best_cost = 1 + 8
        best_length = 1
        best_token: tuple[str, int, int] = ("literal", 0, 1)

        # A one-byte copy costs 8 bits against a literal's 9 whenever a byte
        # within 14 of here already holds this value. Bounded by the cursor so
        # the distance can never reach behind the start of the output.
        for short in range(1, min(15, cursor + 1)):
            if payload[cursor - short] == payload[cursor]:
                if 8 < best_cost:
                    best_cost, best_length = 8, 1
                    best_token = ("one", short, 1)
                break

        if cursor + 3 <= total:
            key = payload[cursor : cursor + 3]
            for start in reversed(positions.get(key, ())[-_CHAIN_LIMIT:]):
                distance = cursor - start
                if distance <= 0 or distance > _MAX_WINDOW:
                    continue
                length = 3
                limit = min(_MAX_MATCH, total - cursor)
                while (
                    length < limit
                    and payload[start + length] == payload[cursor + length]
                ):
                    length += 1

                if 1 <= distance <= 127 and 2 <= length <= 5:
                    cost = 3 + 7 + 2
                    if cost / length < best_cost / best_length:
                        best_cost, best_length = cost, length
                        best_token = ("short", distance, length)

                if distance == previous_distance:
                    cost = 2 + _gamma_cost(2) + _gamma_cost(length)
                    if cost / length < best_cost / best_length:
                        best_cost, best_length = cost, length
                        best_token = ("previous", distance, length)

                count = length - _length_bias(distance)
                if count >= 2:
                    code = (distance >> _ENCODER_DISTANCE_BITS) + 3
                    cost = (
                        2
                        + _gamma_cost(code)
                        + _ENCODER_DISTANCE_BITS
                        + _gamma_cost(count)
                    )
                    if cost / length < best_cost / best_length:
                        best_cost, best_length = cost, length
                        best_token = ("long", distance, count)

        kind, distance, argument = best_token
        if kind == "literal":
            writer.bit(1)
            writer.put(payload[cursor], 8)
        elif kind == "one":
            writer.bit(0)
            writer.bit(0)
            writer.bit(1)
            writer.put(distance + 1, 4)
        elif kind == "short":
            writer.bit(0)
            writer.bit(0)
            writer.bit(0)
            writer.put(distance, 7)
            writer.put(argument - 2, 2)
            previous_distance = distance
        elif kind == "previous":
            writer.bit(0)
            writer.bit(1)
            writer.gamma(2)
            writer.gamma(argument)
        else:
            writer.bit(0)
            writer.bit(1)
            writer.gamma((distance >> _ENCODER_DISTANCE_BITS) + 3)
            writer.put(distance & _ENCODER_DISTANCE_MASK, _ENCODER_DISTANCE_BITS)
            writer.gamma(argument)
            previous_distance = distance

        for index in range(cursor, min(cursor + best_length, total - 2)):
            positions.setdefault(payload[index : index + 3], []).append(index)
        cursor += best_length

    return struct.pack("<II", PACKED_KINDS[1], total) + writer.finish()
