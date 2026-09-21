"""Engine-side reference codec for Buu's Fury Webfoot containers.

Scope, and what each part rests on
----------------------------------

This module supports ``LOGX-CODEC-001``. Two different things live in it and
they carry different evidence.

**The wrapper** - :data:`WEBFOOT_DISPATCHER`, :func:`dispatcher_report`, the
veneer table - is transcribed from the engine's own instructions and is the part
this ticket establishes directly. ``0x0803D940`` dispatches on
``container[+0x00]``: kind 0 memcpys ``container[+0x04]`` bytes from
``container + 8``; kinds 1 and 2 run the packed decoder; any other value returns
with the destination untouched. The dispatcher takes exactly ``(source,
destination)``: its first instruction is ``adds r2, r0, #0``, which discards its
incoming third argument, and it never reads ``container[+0x04]`` on the packed
path.

**The packed grammar** - :func:`decode_packed` - is an independent
reimplementation of the same bit grammar as
``tools.webfoot.formats.webfoot_lz``. It exists so this ticket can run a
differential over the whole canonical corpus without two copies of one
implementation agreeing by construction, and so the two termination rules can be
measured separately. It is *not* a second claim about the format: the
authoritative statement is the project decoder plus the engine wrapper above.
Agreement is asserted by ``tests/integration/test_logx_codec_rom.py``.

Departure from the engine, stated explicitly
--------------------------------------------

The engine performs no bounds checks: it stores with ``strb`` without comparing
against a destination limit and loads with ``ldr`` without comparing against the
end of the image. This module keeps the grammar and the output exactly and adds
host-side guards that raise :class:`CodecError` instead of reading or writing
outside the buffers it was given. A :class:`CodecError` from a **grammar guard**
- a back-reference before the start of the output, or a bit read past the end of
the image - means "the engine's instructions would have left the buffers", never
"the engine refuses this input".

The module's other raises are **host-side checks of different kinds**, and none of
them is an engine behaviour claim: argument validation (a payload offset outside
the image, a literal width outside 1..9, a declared size over ``MAX_OUTPUT``, an
unknown ``stop_on`` rule, an unrepresentable bit read), the ``MAX_OUTPUT`` output
guard that stands in for the destination buffer the engine does not check, and the
**declared-size postcondition** below - with the default
``stop_on="declared_size"`` the module raises when the output does not reach
exactly the declared size. That last one is a *policy* postcondition rather than a
grammar rule: an over-long match or raw-literal run is a stream the engine would
happily execute, writing past the declared length into whatever follows, and the
postcondition exists so a truncated or over-long payload cannot be reported as a
success. The same rule is what the shipping decoder enforces and what the export
reader's end-marker rule is layered on.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

ROM_BASE = 0x08000000

#: The Thumb dispatcher the dominant-layer and selector call sites use.
WEBFOOT_DISPATCHER = 0x0803D940

#: IWRAM addresses the Thumb->ARM veneers at 0x08049120.. resolve to. Measured
#: from each veneer's own ``ldr pc, [pc, #-4]`` literal.
IWRAM_PACKED = 0x03000040         # <- 0x08049120 ; the packed decoder
IWRAM_MEMSET = 0x030007A8         # <- 0x0804912C ; broadcast-store memset
IWRAM_MEMCPY = 0x03000768         # <- 0x08049138 ; block memcpy
IWRAM_ALT_LOOKUP_A = 0x030002DC   # <- 0x0804918C ; r2-indexed alternate decode
IWRAM_ALT_LOOKUP_B = 0x03000CA0   # <- 0x080491A8 ; r2-indexed alternate decode

#: ROM address the startup DMA3 copies to IWRAM 0x03000000, so the packed
#: decoder is the function at blob base + 0x40.
IWRAM_BLOB_ROM_BASE = 0x087B79A4
PACKED_DECODER_ROM = 0x087B79E4

#: Initial literal width, in bits, the canonical corpus decodes under.
INITIAL_LITERAL_BITS = 8

#: Host-side safety limit, NOT an engine limit. The engine has no such bound.
MAX_OUTPUT = 64 * 1024

#: Host-side bound on source bytes consumed, NOT an engine limit. Used only when
#: a caller asks to run past the declared output size to find a stream's own
#: terminator.
MAX_INPUT_BYTES = 64 * 1024


class CodecError(RuntimeError):
    """The engine's instructions would have left the given buffers."""


@dataclass(frozen=True)
class Decoded:
    """One decoded payload plus what the decode cost and how it stopped."""

    data: bytes
    declared_size: int
    actual_size: int
    #: ``end_marker`` - the stream's own control escape was reached before the
    #: declared length; ``declared_size`` - the output reached the header's
    #: declared length; ``ran_past`` - the host guard fired.
    terminator: str
    #: Source bytes consumed, counted as the engine's own ``ldr r6,[r1],#4``
    #: advances ``r1``. Always a multiple of four; the engine over-reads up to
    #: three bytes past the final token.
    source_consumed: int
    final_literal_bits: int

    @property
    def actual_equals_declared(self) -> bool:
        return self.actual_size == self.declared_size


class _BitReader:
    """MSB-first bits over little-endian 32-bit words."""

    __slots__ = ("data", "position", "word", "left", "consumed", "log")

    def __init__(self, data: bytes, position: int) -> None:
        self.data = data
        self.position = position
        self.word = 0
        self.left = 0
        self.consumed = 0
        self.log: list[int] | None = None

    def _refill(self) -> None:
        if self.position + 4 > len(self.data):
            raise CodecError("reading a bit word would leave the image")
        self.word = struct.unpack_from("<I", self.data, self.position)[0]
        self.position += 4
        self.left = 32

    def bit(self) -> int:
        if self.left == 0:
            self._refill()
        value = (self.word >> 31) & 1
        self.word = (self.word << 1) & 0xFFFFFFFF
        self.left -= 1
        self.consumed += 1
        if self.log is not None:
            self.log.append(value)
        return value

    def get(self, count: int) -> int:
        if count < 0 or count > 32:
            raise CodecError(f"bit read of {count} is not representable")
        value = 0
        for _ in range(count):
            value = (value << 1) | self.bit()
        return value


def _gamma(reader: _BitReader) -> int:
    value = 1
    while True:
        value = (value << 1) | reader.bit()
        if reader.bit() == 0:
            return value


def decode_packed(
    data: bytes,
    payload_offset: int,
    *,
    declared_size: int,
    initial_literal_bits: int = INITIAL_LITERAL_BITS,
    stop_on: str = "declared_size",
    max_input_bytes: int = MAX_INPUT_BYTES,
    _trace: list | None = None,
    _bit_log: list[int] | None = None,
) -> Decoded:
    """Decode one packed stream.

    ``stop_on`` selects which termination is modelled:

    * ``"declared_size"`` - stop once ``declared_size`` bytes are written. This
      is the project decoder's rule and, per the ticket's measurement, also the
      engine's: the engine carries no output counter, and the packed streams'
      own escape fires consistently at or after this point.
    * ``"end_marker"`` - ignore ``declared_size`` and run to the stream's own
      control escape. Used to measure where that escape actually falls.
    """
    if not 0 <= payload_offset <= len(data):
        raise CodecError(f"payload offset {payload_offset:#x} is outside the image")
    if initial_literal_bits < 1 or initial_literal_bits > 9:
        raise CodecError(f"literal width {initial_literal_bits} outside 1..9")
    if declared_size < 0 or declared_size > MAX_OUTPUT:
        raise CodecError(f"declared size {declared_size} outside 0..{MAX_OUTPUT}")
    if stop_on not in ("declared_size", "end_marker"):
        raise CodecError(f"unknown stop rule {stop_on!r}")

    reader = _BitReader(data, payload_offset)
    reader.log = _bit_log
    out = bytearray()
    literal_base = 0
    literal_bits = initial_literal_bits
    distance_bits = 8
    previous_distance = 1
    output_limit = MAX_OUTPUT if stop_on == "end_marker" else declared_size
    input_limit = max_input_bytes

    def note(*args: object) -> None:
        if _trace is not None:
            _trace.append(args)

    def finish(terminator: str) -> Decoded:
        return Decoded(
            data=bytes(out),
            declared_size=declared_size,
            actual_size=len(out),
            terminator=terminator,
            source_consumed=reader.position - payload_offset,
            final_literal_bits=literal_bits,
        )

    def copy_match(distance: int, count: int) -> None:
        if distance == 0 or distance > len(out):
            raise CodecError(
                f"back-reference distance {distance} at output {len(out)} runs "
                "before the start of the destination"
            )
        for _ in range(count):
            if len(out) >= MAX_OUTPUT:
                raise CodecError(f"output exceeded the {MAX_OUTPUT}-byte guard")
            out.append(out[-distance])

    while len(out) < output_limit:
        if len(out) > MAX_OUTPUT:
            return finish("ran_past")
        if reader.position - payload_offset > input_limit:
            return finish("ran_past_input")

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
            # The match length is biased by its own distance. The thresholds are
            # engine constants, read out of the IWRAM blob's literal pool
            # (0x087B7CCC = 0x37FF, 0x087B7CD0 = 0x027F).
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
                if stop_on == "end_marker":
                    return finish("end_marker")
                break
            distance_bits = reader.get(width + 3)
            continue

        short_distance = reader.get(4) - 1
        if short_distance == 0:
            out.append(literal_base & 0xFF)
        elif short_distance > 0:
            copy_match(short_distance, 1)
        elif reader.bit():
            # A run of raw 8-bit literals, terminated by a clear bit. The run is
            # emitted whole and the declared-size decision is left to the
            # post-loop check, exactly as the match path leaves it: stopping here
            # at ``declared_size`` would silently drop literals, which is the
            # class of clip this reference exists to detect. An earlier revision
            # stopped at the declared size on this path while the match path did
            # not, so this module accepted a stream that both the repaired
            # shipping decoder and the export reader refuse.
            while True:
                for _ in range(2):
                    if len(out) >= MAX_OUTPUT:
                        raise CodecError(
                            f"output exceeded the {MAX_OUTPUT}-byte guard"
                        )
                    out.append(reader.get(8))
                if reader.bit() == 0:
                    break
        else:
            literal_bits = 7 + reader.bit()
            if literal_bits != 8:
                literal_base = reader.get(8)

    if len(out) != declared_size and stop_on == "declared_size":
        raise CodecError(
            f"packed stream decoded {len(out)} bytes against a declared "
            f"{declared_size}"
        )
    return finish("declared_size")


# --- wrapper reporting -------------------------------------------------------


def _u32(data: bytes, address: int) -> int:
    return struct.unpack_from("<I", data, address - ROM_BASE)[0]


def veneer_table(data: bytes) -> list[dict[str, object]]:
    """Every Thumb->ARM interworking stub in the run at ``0x08049120``.

    Slots are **8 bytes** for the Thumb ``bx pc`` / ``nop`` prologue plus one ARM
    instruction. Only the ``ldr pc`` form carries a fourth word (its literal), so
    those slots are 12 bytes; the branch form is 8. The walk stops at the first
    slot that is neither form, so ``len(veneer_table(...))`` is the run's extent.
    """
    rows: list[dict[str, object]] = []
    address = 0x08049120
    while address < 0x08049200:
        offset = address - ROM_BASE
        chunk = data[offset : offset + 12]
        if len(chunk) < 8:
            break
        if chunk[0:2] != b"\x78\x47" or chunk[2:4] != b"\xc0\x46":
            break
        # `bx pc` / `nop`, then either an ARM `ldr pc, [pc, #-4]` with its
        # literal, or an ARM `b <target>`.
        word = struct.unpack_from("<I", chunk, 4)[0]
        if word == 0xE51FF004:
            rows.append(
                {
                    "veneer": address,
                    "form": "ldr_pc",
                    "instruction_bytes": chunk[:12].hex(),
                    "size": 12,
                    "iwram_target": struct.unpack_from("<I", chunk, 8)[0],
                }
            )
            address += 12
            continue
        if (word & 0xFF000000) == 0xEA000000:
            delta = word & 0x00FFFFFF
            if delta & 0x00800000:
                delta -= 0x01000000
            rows.append(
                {
                    "veneer": address,
                    "form": "branch",
                    "instruction_bytes": chunk[:8].hex(),
                    "size": 8,
                    "iwram_target": None,
                    # ARM branch semantics: the branch sits at `address + 4`
                    # (after `bx pc` / `nop`) and PC reads as that instruction's
                    # address plus 8.
                    "arm_branch_target": (address + 12 + (delta << 2)) & 0xFFFFFFFF,
                }
            )
            address += 8
            continue
        break
    return rows


def dispatcher_report(data: bytes | None = None) -> dict[str, object]:
    """The wrapper's contract, as the engine's own Thumb code states it."""
    return {
        "dispatcher": WEBFOOT_DISPATCHER,
        "dispatcher_decoded": [
            "0803d940 adds r2, r0, #0        ; r2 = source container",
            "0803d942 adds r0, r1, #0        ; r0 = destination",
            "0803d944 push {r3, lr}",
            "0803d946 ldr  r3, [r2]          ; dispatch word = container[+0x00]",
            "0803d948 adds r1, r2, #0",
            "0803d94a adds r1, #8            ; payload = container + 8",
            "0803d94c cmp  r3, #0",
            "0803d94e beq  0x0803d95e        ; kind 0 -> stored branch",
            "0803d950 cmp  r3, #1",
            "0803d952 beq  0x0803d958        ; kind 1 -> packed decoder",
            "0803d954 cmp  r3, #2",
            "0803d956 bne  0x0803d95c        ; other  -> return, dest untouched",
            "0803d958 bl   0x08049120        ; -> IWRAM 0x03000040",
            "0803d95c pop  {r3, pc}",
            "0803d95e ldr  r2, [r2, #4]      ; declared decoded size = container[+0x04]",
            "0803d960 bl   0x08046d18        ; ROM ARM memcpy, not a veneer",
            "0803d964 b    0x0803d95c",
        ],
        "arguments": (
            "(source_container, destination). 0x0803D940 executes "
            "`adds r2, r0, #0` as its first instruction, so its incoming r2 is "
            "dead: it takes exactly two arguments and knows no output length."
        ),
        "second_entry": {
            "address": 0x0803D966,
            "decoded": [
                "0803d966 adds r3, r0, #0",
                "0803d968 adds r0, r1, #0",
                "0803d96a adds r1, r3, #0",
                "0803d96c adds r1, #8            ; payload = container + 8",
                "0803d96e push {r4, lr}",
                "0803d970 ldr  r4, [r3]          ; dispatch word",
                "0803d972 cmp  r2, #0",
                "0803d974 bne  0x0803d98c        ; r2 non-NULL -> alternate path",
                "0803d976 cmp  r4, #0",
                "0803d978 beq  0x0803d984        ; kind 0 -> stored",
                "0803d97a cmp  r4, #1",
                "0803d97c bne  0x0803d982",
                "0803d97e bl   0x08049120        ; kind 1 -> the same packed decoder",
                "0803d984 ldr  r2, [r3, #4]",
                "0803d986 bl   0x08049138        ; -> IWRAM 0x03000768 (block memcpy)",
                "0803d98c cmp  r4, #0            ; r2 non-NULL, kind 0",
                "0803d994 bl   0x080491a8        ; -> alternate decoder, r2-indexed",
                "0803d99c bl   0x0804918c        ; -> alternate decoder, r2-indexed",
            ],
            "note": (
                "A second dispatcher entry exists. r2 is NOT a length: it is "
                "only tested for NULL and then handed to two alternate routines "
                "as a table pointer for a per-byte lookup, so the non-NULL branch "
                "is a remapping path. It has exactly one BL caller (0x0800F3D2) "
                "and is not used by the dominant-layer or selector call sites. "
                "On its NULL path it computes r1 = container + 8 exactly as "
                "0x0803D940 does."
            ),
        },
        "veneer_run": veneer_table(data) if data else [],
        "iwram_targets": {
            "packed": IWRAM_PACKED,
            "memset": IWRAM_MEMSET,
            "memcpy": IWRAM_MEMCPY,
            "alt_lookup_a": IWRAM_ALT_LOOKUP_A,
            "alt_lookup_b": IWRAM_ALT_LOOKUP_B,
        },
        "iwram_blob": {
            "rom_base": IWRAM_BLOB_ROM_BASE,
            "iwram_base": 0x03000000,
            "copied_bytes": 2050,
            "dma3_source_literal": 0x08000148,
            "dma3_destination_literal": 0x0800014C,
            "dma3_control_literal": 0x08000150,
            "packed_decoder_rom": PACKED_DECODER_ROM,
            "packed_decoder_iwram": IWRAM_PACKED,
            "note": (
                "The packed decoder is blob base + 0x40. 0x087B7A9C "
                "(base + 0xF8) is an interior bit-loop label, not an entry."
            ),
        },
    }
