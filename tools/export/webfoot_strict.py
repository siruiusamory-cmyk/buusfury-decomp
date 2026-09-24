"""Strict Webfoot container decoding for the export path.

ASSET-EXPORT-001. The accepted container format is a two-word header over either
stored bytes or a packed bitstream:

    +0x00  u32 LE  dispatch word: 0 = stored, 1 and 2 = packed
    +0x04  u32 LE  declared decoded byte count, excluding the header
    +0x08  ...     stored bytes, or the packed bitstream

The engine's dispatcher is `0x0803D940`; form 0 copies exactly `container[+0x04]`
bytes, forms 1 and 2 run the packed decoder, any other value returns with the
destination untouched. The packed grammar is JCALG1-like/derived: MSB-first bits
over little-endian `u32` words, prefix `1` literal, `0 1` long match with a
distance-biased length ladder, `0 0 0` seven-bit field / end marker, `0 0 1`
four-bit code.

**Why this module exists rather than a call to `tools.webfoot.formats.webfoot_lz`.**
It was written when the shipping decoder carried a real defect, inventoried as
§11.1 of `docs/research/LOGX_SYNTHESIS.md`: its `copy_match` stopped appending once
the output reached the declared size, so an **over-long final match was silently
clipped** and the decode reported as successful. An asset exporter must not build
its completeness claims on a decoder whose success flag did not mean "produced
exactly the declared size", so this module was the export-side strict reader the
ASSET-EXPORT-001 ticket asked for.

**EVIDENCE-RISK-DEBT-001 repaired that decoder** (the `FIX-1` the paragraph above
used to forward to). `webfoot_lz.unpack` now refuses an over-long match, a run of
raw literals that would pass the declared size, a stream that stops short, and a
truncated stream, and the two modules agree on every malformed case in
`tests/unit/test_asset_export_strict_lz.py`. What this module still adds over the
shipping reader is therefore narrower and worth stating: the **end-marker
postcondition** below, and `MAX_INPUT_BYTES` - a bound on the packed input
consumed, so a stream that never terminates cannot make a caller spin. It is kept
rather than deleted because the end-marker check is a genuine independent
postcondition on the canonical corpus, and because rewriting the exporter's reader
is not this ticket's change.

**The two readers agree on decoded bytes, not on `packed_end`.** With
`require_end_marker=True` - which is what the export path uses - the decode does
not stop when the declared size is reached but runs on to the stream's own marker,
so the reader's final word position is up to one word *larger* than the extent an
in-place edit is bounded by. Measured over the 7,390 canonical sprite containers
that difference is 0 bytes for 4,662 of them and 4 bytes for the other 2,728, with
no overlap into the next container either way. `webfoot_lz.packed_end` remains the
extent a write is measured against; this module's position is the
marker-terminated extent and is a different quantity.

**What "strict" means here, stated exactly.**

* A match or literal whose length would carry the output past the declared size
  is an error. Nothing is truncated to fit.
* A stream that ends before producing the declared size is an error.
* Optionally - and the exporter always asks for it - the stream must also reach
  its own end marker, and that marker must fall at exactly the declared size.
  Output reaching the declared size is not on its own evidence that the stream is
  the one the header describes.

The accepted corpus satisfies all three. `LOGX-CODEC-001` measured it over the
4,322 packed containers reachable from the **map** side alone (chunk, selector
stream and bank containers); this exporter's own reachable set is wider, 11,712
packed containers, because it also walks the sprite graph, and every one of those
11,712 also produces exactly its declared size with its end marker at that same
length. Both figures were measured; they count different populations and are
never interchangeable. That is a canonical observation, not a format guarantee -
the engine carries no output counter and performs no size comparison - so this
module treats the observation as a checkable postcondition rather than as an
assumption.

**Why the end-marker check is opt-in.** It is a check on the *stream*, not a
policy of the project decoder, and the two readers serve different callers. It
used to be opt-in for a second reason as well - the project's own
`webfoot_lz.pack` terminated by output length and never emitted the escape, so
requiring the marker would have refused that encoder's output. **That is no longer
true**: CQA-02-PACKED-STREAM-TERMINATION-001 had `pack` write the retail decoder's
own escape after the final token, before the final word is padded, so every current
`pack` output reaches a marker at exactly its declared size. The default here is
unchanged all the same: the marker rule is a strictly stronger postcondition, and
the default decode - exact declared size, no clipping - is the behaviour every
other reader and synthetic fixture in this project relies on. The export path
keeps asking for the stronger check, because every canonical container passes it.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct

from tools.webfoot.binary import GBA_ROM_BASE

#: GBA ROM base; every address in the accepted graph is a GBA address. Taken
#: from `webfoot.binary`, the one owner of address-window semantics, rather
#: than restated here - the conversion must have a single authority.
#:
#: Header is two little-endian words.
HEADER_SIZE = 8

#: Dispatch values the engine's `0x0803D940` knows.
STORED = 0
PACKED_KINDS = (1, 2)

#: Host-side safety bound on a decoded container, mirroring the project
#: decoder's constant. It is NOT a format limit: the synthesis explicitly
#: refutes a ~64 KiB engine or format cap, and the largest declared size in the
#: reachable corpus is `0x4000`.
MAX_OUTPUT = 64 * 1024

#: Host-side bound on packed input consumed, so a corrupt stream cannot spin.
MAX_INPUT_BYTES = 64 * 1024


class ContainerError(ValueError):
    """Raised when a container is malformed, truncated or the wrong size."""


@dataclass(frozen=True, slots=True)
class Container:
    """One strictly decoded container plus the exact input extent consumed."""

    offset: int
    kind: int
    declared_size: int
    packed_end: int
    data: bytes

    @property
    def packed_size(self) -> int:
        """Bytes of the image this container occupies, header included."""
        return self.packed_end - self.offset


class _BitReader:
    """MSB-first bit reader over little-endian 32-bit words."""

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
        value = (self._word >> 31) & 1
        self._word = (self._word << 1) & 0xFFFFFFFF
        self._remaining -= 1
        return value

    def get(self, count: int) -> int:
        if count < 0 or count > 32:
            raise ContainerError(f"bit read of {count} is not representable")
        value = 0
        for _ in range(count):
            value = (value << 1) | self.bit()
        return value

    @property
    def position(self) -> int:
        return self._position


def _gamma(reader: _BitReader) -> int:
    """Elias-gamma-style value: interleaved payload and continuation bits."""
    value = 1
    while True:
        value = (value << 1) | reader.bit()
        if reader.bit() == 0:
            return value


def _bias(distance: int) -> int:
    """The match-length bias the engine adds back for a given distance.

    The thresholds are engine constants read out of the packed decoder's own
    literal pool (`0x087B7CCC` = `0x37FF`, `0x087B7CD0` = `0x027F`). They are
    not derivable from first principles and must not be tidied into a formula.
    """
    if distance >= 0x10000:
        return 3
    if distance >= 0x37FF:
        return 2
    if distance >= 0x027F:
        return 1
    if distance <= 0x007F:
        return 4
    return 0


def _emit_raw(out: bytearray, value: int, declared_size: int) -> None:
    """Append one byte of a raw-literal run, refusing to pass the declared size."""
    if len(out) >= declared_size:
        raise ContainerError(
            f"raw literal run at output {len(out)} overruns the declared "
            f"{declared_size}"
        )
    out.append(value)


def decode_packed(
    data: bytes,
    payload_offset: int,
    declared_size: int,
    initial_literal_bits: int,
    *,
    require_end_marker: bool = False,
) -> tuple[bytes, int, bool]:
    """Strictly decode one packed stream.

    Returns ``(bytes, packed_end, reached_end_marker)``. ``packed_end`` is the
    reader's word-aligned position when decoding stopped, measured by running the
    decoder rather than read from a field: the header declares the *decoded* size
    and says nothing about the packed one.

    With ``require_end_marker`` the stream must consume its own end-marker escape
    and that escape must fall at exactly the declared size. Without it the decode
    stops as soon as the declared size is produced, which is a **host-side
    convenience, not the engine's rule**: the retail packed decoder keeps no output
    counter, compares nothing against its destination cursor, and stops only on
    that escape (`CONFIRMED`;
    `docs/research/CQA_02_PACKED_TERMINATION_RESOLUTION.md` §2.1, adjudicated in
    Phase 1 of CQA-02-PACKED-STREAM-TERMINATION-001). The sentence that used to
    stand here called the declared-size stop "the engine's and the shipping
    decoder's rule"; it was wrong about the engine, and it contradicted this same
    module's docstring, which had the engine's behaviour right. Corrected rather
    than deleted so the superseded claim stays visible.
    """
    if declared_size < 0 or declared_size > MAX_OUTPUT:
        raise ContainerError(
            f"declared size {declared_size} is outside 0..{MAX_OUTPUT}"
        )
    if not 1 <= initial_literal_bits <= 9:
        raise ContainerError(
            f"initial literal width {initial_literal_bits} is outside 1..9"
        )
    if not 0 <= payload_offset <= len(data):
        raise ContainerError(f"payload offset {payload_offset:#x} is outside the image")

    reader = _BitReader(data, payload_offset)
    out = bytearray()
    literal_base = 0
    literal_bits = initial_literal_bits
    distance_bits = 8
    previous_distance = 1
    reached_end_marker = False

    def copy_match(distance: int, count: int) -> None:
        if distance == 0 or distance > len(out):
            raise ContainerError(
                f"back-reference distance {distance} at output {len(out)} points "
                "before the start of the decoded output"
            )
        if len(out) + count > declared_size:
            raise ContainerError(
                f"match at output {len(out)} would produce {len(out) + count} "
                f"bytes against a declared {declared_size}"
            )
        for _ in range(count):
            out.append(out[-distance])

    while not reached_end_marker:
        if len(out) >= declared_size and not require_end_marker:
            break
        if reader.position - payload_offset > MAX_INPUT_BYTES:
            raise ContainerError(
                f"packed stream consumed over {MAX_INPUT_BYTES} input bytes "
                "without reaching its end marker"
            )
        if reader.bit():
            if len(out) >= declared_size:
                raise ContainerError(
                    f"literal at output {len(out)} overruns the declared "
                    f"{declared_size}"
                )
            out.append((literal_base + reader.get(literal_bits)) & 0xFF)
            continue

        if reader.bit():
            distance_code = _gamma(reader)
            if distance_code == 2:
                copy_match(previous_distance, _gamma(reader))
                continue
            distance = reader.get(distance_bits) + ((distance_code - 3) << distance_bits)
            previous_distance = distance
            copy_match(distance, _gamma(reader) + _bias(distance))
            continue

        if reader.bit() == 0:
            distance = reader.get(7)
            if distance != 0:
                previous_distance = distance
                copy_match(distance, reader.get(2) + 2)
                continue
            width = reader.get(2)
            if width == 0:
                reached_end_marker = True
                continue
            distance_bits = reader.get(width + 3)
            continue

        short_distance = reader.get(4) - 1
        if short_distance == 0:
            if len(out) >= declared_size:
                raise ContainerError(
                    f"base-literal at output {len(out)} overruns the declared "
                    f"{declared_size}"
                )
            out.append(literal_base & 0xFF)
        elif short_distance > 0:
            copy_match(short_distance, 1)
        elif reader.bit():
            while True:
                _emit_raw(out, reader.get(8), declared_size)
                _emit_raw(out, reader.get(8), declared_size)
                if reader.bit() == 0:
                    break
        else:
            literal_bits = 7 + reader.bit()
            if literal_bits != 8:
                literal_base = reader.get(8)

    if len(out) != declared_size:
        raise ContainerError(
            f"packed stream decoded {len(out)} bytes against a declared "
            f"{declared_size}"
        )
    if require_end_marker and not reached_end_marker:
        raise ContainerError(
            f"packed stream reached its declared {declared_size} bytes without "
            "consuming its own end marker"
        )
    return bytes(out), reader.position, reached_end_marker


def read_header(data: bytes, offset: int) -> tuple[int, int]:
    """Return ``(kind, declared_size)`` without decoding the payload."""
    if offset < 0 or offset + HEADER_SIZE > len(data):
        raise ContainerError(f"container header at {offset:#x} is outside the image")
    return struct.unpack_from("<II", data, offset)


def unpack(
    data: bytes,
    offset: int,
    *,
    maximum_output: int = MAX_OUTPUT,
    require_end_marker: bool = False,
) -> Container:
    """Strictly decode the container at ``offset``.

    Raises :class:`ContainerError` for a bad header, a declared size over
    ``maximum_output``, a truncated stored payload, or a packed stream that does
    not produce exactly its declared size. With ``require_end_marker`` it also
    requires the packed stream's own end marker to fall at that same length.
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
            raise ContainerError(
                f"stored container at {offset:#x} declares {declared} bytes and "
                "runs past the image"
            )
        return Container(
            offset=offset,
            kind=kind,
            declared_size=declared,
            packed_end=payload + declared,
            data=data[payload : payload + declared],
        )
    if kind in PACKED_KINDS:
        decoded, end, _marker = decode_packed(
            data,
            payload,
            declared,
            kind,
            require_end_marker=require_end_marker,
        )
        return Container(
            offset=offset,
            kind=kind,
            declared_size=declared,
            packed_end=end,
            data=decoded,
        )
    raise ContainerError(f"unsupported Webfoot container kind {kind} at {offset:#x}")


def unpack_address(data: bytes, address: int, **kwargs: object) -> Container:
    """Strictly decode the container at GBA ``address``."""
    return unpack(data, address - GBA_ROM_BASE, **kwargs)  # type: ignore[arg-type]
