"""LOGX-GFXSCAN-001: measure an ImageScan-style graphics discovery scanner.

Read-only, deterministic research tool.  It answers, against the canonical Buu's
Fury image and the project's accepted resource graphs:

* what ``mainant/LOGExtractor``'s ``ImageScan`` tool actually recognises, byte
  for byte, reproduced as an explicit model rather than paraphrased;
* how many of the engine-reachable graphics containers that model finds, and how
  many it misses;
* how many of its candidates are already reachable through an accepted resource
  graph, and what the remainder actually is;
* what false-positive classes the method produces;
* whether an engine-informed variant trades recall for precision.

Three models are kept strictly apart and are never conflated:

``EXTERNAL``
    A faithful reproduction of ``ImageScan/MainForm.cs`` ``ScanForImages`` plus
    ``ImageScan/Gba/JCALG1.cs``.  It walks every byte from ``0x200``, requires the
    first word to be exactly ``1``, requires ``1 <= declared < 0x20000`` and
    ``declared % 4 == 0``, leaves the literal state at the C# field default of
    zero - the declared-size word does **not** seed it - and accepts any stream
    that runs to the declared output size or its own end marker without raising.
    Two deviations from the source, both listed in the fidelity comment below, are
    each stricter than the source and each cost at most one candidate.

``ENGINE``
    The same byte-level search population with the rules the engine's own
    dispatcher implies: wrapper forms ``{0, 1, 2}``, an in-bounds stored copy,
    and the packed stream's own terminator required to agree with the declared
    size (LOGX-CODEC-001 measured that agreement on 4,322 of 4,322 canonical
    packed containers).

``ENGINE_ALIGNED``
    ``ENGINE`` plus word alignment of the wrapper start.

The word "graphics" is never used as a synonym for "decodes".  Every candidate
lands in one of the ticket's categories (``A``..``F``) and the known-positive
corpus keeps its resource classes apart: the map chunk and selector classes are
known engine-reachable containers whose payloads are *not* graphics, and they are
counted as such rather than as scanner failures.

No decoded payload is written anywhere, by default or otherwise: results carry
addresses, lengths and SHA-256 digests only.  The ROM is SHA-gated and opened
read-only.  The module imports only the standard library, the project's own
research modules and the project's container decoder; nothing optional is needed
to import it, and capstone is not imported at all.

Usage::

    python -m tools.research.logx_gfxscan_probe <rom> --external-model
    python -m tools.research.logx_gfxscan_probe <rom> --engine-model
    python -m tools.research.logx_gfxscan_probe <rom> --known
    python -m tools.research.logx_gfxscan_probe <rom> --classify
    python -m tools.research.logx_gfxscan_probe <rom> --diff
    python -m tools.research.logx_gfxscan_probe <rom> --residual
    python -m tools.research.logx_gfxscan_probe <rom> --references
    python -m tools.research.logx_gfxscan_probe <rom> --unknown-header
    python -m tools.research.logx_gfxscan_probe <rom> --summary
    python -m tools.research.logx_gfxscan_probe <rom> --json out.json
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import struct
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.research import logx_codec_probe as codec  # noqa: E402,F401
from tools.research import logx_frame_probe as frame  # noqa: E402
from tools.research import webfoot_codec_reference as reference  # noqa: E402
from tools.webfoot.formats import webfoot_lz as wl  # noqa: E402

ROM_BASE = 0x08000000
ROM_SIZE = 8 * 1024 * 1024
CANONICAL_SHA256 = "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"

# --- the external model's own constants (LOGExtractor ImageScan) -------------

#: ``ImageScan/MainForm.cs`` ``ScanForImages``: ``for (int i = 0x200; ...; i += 1)``.
EXTERNAL_SCAN_START = 0x200

#: ``if (magic != 0x1) continue;`` - the dispatch word must be exactly one.
EXTERNAL_REQUIRED_KIND = 1

#: ``if (length > 0 && length < 0x20000 && length % 4 == 0)``.
EXTERNAL_SIZE_MIN = 1
EXTERNAL_SIZE_MAX_EXCLUSIVE = 0x20000
EXTERNAL_SIZE_MULTIPLE = 4

#: ``bool isPrio = decompressed.Length == 16 * 16;`` - the tool's only
#: post-decode distinction, and it only reorders the result list.
EXTERNAL_PRIORITY_LENGTH = 16 * 16

#: The prefix ``JCALG1.DecompressUnknownHeader`` skips.  Present in the external
#: source, never called by ``ScanForImages``; measured here as an external
#: heuristic, never as a container form (LOGX-CODEC-001 REFUTED that reading).
EXTERNAL_UNKNOWN_HEADER_SKIP = 4

# --- host-side bounds (stated as host policy, never as format facts) ---------

#: The largest declared size the external scanner will even attempt is
#: ``0x20000``; this is the host bound the reproduction allocates against.
HOST_MAX_OUTPUT = EXTERNAL_SIZE_MAX_EXCLUSIVE

#: The canonical decoder's own host guard, from ``webfoot_codec_reference``.
HOST_CANONICAL_MAX_OUTPUT = reference.MAX_OUTPUT

#: Working bound on one scan run, so a caller cannot make the probe walk an
#: unbounded image.  The canonical image is 8 MiB and is well inside this.
HOST_MAX_SCAN_POSITIONS = 16 * 1024 * 1024

# --- candidate categories (the ticket's explicit populations) ----------------

CATEGORY_KNOWN_GRAPHICS = "A_known_engine_reachable_graphics"
CATEGORY_KNOWN_NON_GRAPHICS = "B_known_engine_reachable_non_graphics"
CATEGORY_UNRESOLVED_CONTAINER = "C_valid_container_semantics_unresolved"
CATEGORY_NEW_ENGINE_REFERENCED = "D_engine_referenced_not_previously_catalogued"
CATEGORY_NO_REFERENCE = "E_structurally_plausible_no_engine_reference"
CATEGORY_FALSE_POSITIVE = "F_malformed_or_scanner_false_positive"

#: ``C`` and ``E`` are the same population and are reported as such.  The ticket's
#: ``C`` is "a valid engine-format container whose semantics are unresolved" and
#: its ``E`` is "structurally plausible but no engine reference found"; for a
#: candidate with no known match, no engine reference and a clean exact decode,
#: both descriptions hold and there is no measurement that separates them.  ``C``
#: is assigned and ``E`` is reported as empty, rather than inventing a distinction
#: that is not measured.
CATEGORY_EQUIVALENT_NOTE = (
    "C and E describe the same predicate on this corpus: a valid container with "
    "no known match, no engine reference and a clean exact decode. C is assigned "
    "and E is reported as empty; no measurement separates them."
)

CATEGORY_LABELS = (
    CATEGORY_KNOWN_GRAPHICS,
    CATEGORY_KNOWN_NON_GRAPHICS,
    CATEGORY_UNRESOLVED_CONTAINER,
    CATEGORY_NEW_ENGINE_REFERENCED,
    CATEGORY_NO_REFERENCE,
    CATEGORY_FALSE_POSITIVE,
)

#: False-positive sub-classes, named so a report never has to describe one in
#: prose.  Each is a distinct mechanism, not a severity.
FP_CLIPPED_DECODE = "clipped_decode_against_declared_size"
FP_SHORT_VIA_END_MARKER = "end_marker_before_the_declared_size"
FP_INSIDE_KNOWN_CONTAINER = "wrapper_start_inside_a_known_container"
FP_NOT_WORD_ALIGNED = "wrapper_start_not_word_aligned"
FP_INSIDE_ANOTHER_CANDIDATE = "wrapper_start_inside_another_candidate"
FP_STORED_RUN_PAST_IMAGE = "stored_form_runs_past_the_image"
FP_DECODE_RAISED = "decoder_raised_on_the_candidate"

# --- known-positive resource classes -----------------------------------------

CLASS_SPRITE_PIECES = "sprite_piece_graphics"
CLASS_MAP_CHUNKS = "map_dominant_layer_chunks"
CLASS_BANK_CONTAINERS = "root_4c_graphics_banks"
CLASS_SELECTOR_STREAMS = "root_48_selector_streams"
CLASS_ZERO_HEADER = "zero_header_form0_containers"
CLASS_ENGINE_DEFAULT = "engine_installed_default_container"

#: Whether a class's *graphics* identity is established by an accepted graph.
#: A class can have confirmed slot semantics and still not be graphics: this is
#: the whole point of keeping the populations apart.
GRAPHICS_CLASSES = frozenset({CLASS_SPRITE_PIECES})

#: What a container's decoded slots are, where a prior ticket established it.
SLOT_SEMANTICS: dict[str, str] = {
    CLASS_SPRITE_PIECES: (
        "CONFIRMED: packed GBA OBJ tile data. The referring piece's own OAM "
        "dimension bytes multiply to the container's declared decoded size on "
        "every canonical piece (LOGX-FRAME-001)."
    ),
    CLASS_MAP_CHUNKS: (
        "CONFIRMED: an array of u16 tile indices feeding the accepted selector "
        "recurrence (LOGX-TILE-001). NOT graphics: it is the chunk's map data."
    ),
    CLASS_BANK_CONTAINERS: "UNRESOLVED: decoded bytes; semantics not established here.",
    CLASS_SELECTOR_STREAMS: (
        "CONFIRMED: an array of u16 selectors indexing the root +0x4C bank "
        "(LOGX-TILE-001). NOT graphics."
    ),
    CLASS_ZERO_HEADER: (
        "CONFIRMED: form 0, a raw copy of the declared bytes (LOGX-CODEC-001)."
    ),
    CLASS_ENGINE_DEFAULT: (
        "CONFIRMED: form 0 with declared size 0 (LOGX-CODEC-001). Contains no "
        "resource at all."
    ),
}

GRAPHICS_IDENTITY: dict[str, str] = {
    CLASS_SPRITE_PIECES: (
        "CONFIRMED graphics: OBJ tile data referenced by a piece's OAM decode."
    ),
    CLASS_MAP_CHUNKS: "REFUTED as graphics: tile-index map data, not pixels.",
    CLASS_BANK_CONTAINERS: "UNRESOLVED: not claimed as graphics by this ticket.",
    CLASS_SELECTOR_STREAMS: "REFUTED as graphics: u16 selector array.",
    CLASS_ZERO_HEADER: "UNRESOLVED: raw bytes; identity follows the owning record.",
    CLASS_ENGINE_DEFAULT: "REFUTED as graphics: zero-length default container.",
}

CLASS_NOTES: dict[str, dict[str, str]] = {
    CLASS_SPRITE_PIECES: {
        "source_graph": "LOGX-FRAME-001 piece +0x08",
        "evidence": "CONFIRMED",
    },
    CLASS_MAP_CHUNKS: {
        "source_graph": "LOGX-TILE-001 dominant handler +0x18 array",
        "evidence": "CONFIRMED",
    },
    CLASS_BANK_CONTAINERS: {
        "source_graph": "LOGX-TILE-001 root +0x4C bank table",
        "evidence": "PARTIALLY CONFIRMED",
    },
    CLASS_SELECTOR_STREAMS: {
        "source_graph": "LOGX-MAP-RENDER-001 root +0x48",
        "evidence": "CONFIRMED",
    },
    CLASS_ZERO_HEADER: {
        "source_graph": "LOGX-CODEC-001 form 0 instances",
        "evidence": "CONFIRMED",
    },
    CLASS_ENGINE_DEFAULT: {
        "source_graph": "LOGX-CODEC-001 engine default",
        "evidence": "CONFIRMED",
    },
}

#: Classes that form the recall denominator.  A class is listed only when its
#: graphics identity is established; a class without one contributes no recall
#: claim and is reported separately.
RECALL_CLASSES: tuple[str, ...] = (CLASS_SPRITE_PIECES,)

# --- model names --------------------------------------------------------------
#
# Three models, never mixed:
#
# * ``EXTERNAL``             - LOGExtractor's ImageScan, reproduced faithfully;
# * ``ENGINE_ALIGNED``       - forms {0,1,2}, word-aligned starts, exact decodes;
# * ``ENGINE_UNCONSTRAINED`` - the same with the alignment rule removed, kept only
#                              to measure how much of a scan's yield alignment
#                              accounts for.

MODEL_EXTERNAL = "external"
MODEL_ENGINE_ALIGNED = "engine_aligned"
MODEL_ENGINE_UNCONSTRAINED = "engine_unconstrained"
#: Retained name for the canonical engine model, so callers that ask for "engine"
#: get the aligned one rather than the measurement variant.
MODEL_ENGINE = MODEL_ENGINE_ALIGNED


class GfxScanError(RuntimeError):
    """Canonical-ROM gate, or a malformed probe input."""


# --- ROM access ---------------------------------------------------------------


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def verify_canonical(data: bytes) -> None:
    """Fail closed unless ``data`` is the canonical Buu's Fury image."""
    if len(data) != ROM_SIZE:
        raise GfxScanError(f"image is {len(data)} bytes, expected {ROM_SIZE}")
    actual = sha256_of(data)
    if actual != CANONICAL_SHA256:
        raise GfxScanError(
            f"refusing non-canonical image: expected {CANONICAL_SHA256}, got {actual}"
        )


def load_rom(path: str | Path) -> bytes:
    data = Path(path).read_bytes()
    verify_canonical(data)
    return data


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def to_address(offset: int) -> int:
    return ROM_BASE + offset


def resolve_offset(value: int) -> int | None:
    """The file offset a stored word names, in either of its two stored forms.

    Kept as the probe's own statement of the resolution rule
    ``logx_frame_probe.to_file_offset`` implements, so a reader of this module can
    see which words the scanner's address comparisons accept without following an
    import.  The classification path itself works in whole GBA addresses.
    """
    if ROM_BASE <= value < ROM_BASE + ROM_SIZE:
        return value - ROM_BASE
    if 0 <= value < ROM_SIZE:
        return value
    return None


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# --- the external decoder model ----------------------------------------------
#
# A transcription of ``ImageScan/Gba/JCALG1.cs`` (revision pinned in the
# provenance document), not a port of the project's decoder.  The external
# reader's fields are named as the external source names them - ``literalBits``,
# ``literalOffset``, ``indexBase``, ``lastIndex`` - so the two can be diffed.
#
# Four details decide whether the model reproduces the canonical corpus, and each
# is pinned by the tests against real containers rather than by synthetic fixtures
# alone:
#
# 1. ``GetInteger`` reads a **payload** bit first and a **continuation** bit
#    second, and repeats while the continuation bit is set:
#    ``do { result = (result << 1) + GetBit(); } while (GetBit() != 0);``.  This
#    reproduction exits when that bit is clear, which is the same loop written
#    from the other side.  Reading the pair in the other order, or reading two
#    bits before the first continuation test, makes the model fail on every
#    canonical container while still decoding synthetic fixtures.
# 2. the initial literal state is the C# field default: both ``literalBits`` and
#    ``literalOffset`` are zero until the first width/base escape sets them.  The
#    escape's next bit chooses 7 bits with a base byte or 8 bits with no base, so
#    the initial values are inert on the canonical corpus: no known container
#    emits a literal before its first escape (measured over all 11,712).
# 3. the four-bit code's ``value == 0`` arm writes a **literal zero**
#    (``destination[w++] = 0``), not the literal base.  The project decoder writes
#    its base there; the difference is real and is measured - it moves one known
#    container's decoded payload and is the reason the two grammars disagree on 78
#    of 11,712 known kind-1 containers rather than 77.
# 4. the external loop is ``while (true)``: it has **no** output-size test.  The
#    declared size is enforced only by the CLR array-bounds check, which throws,
#    and ``MainForm.cs``'s ``catch { }`` then discards that position.  The
#    reproduction instead stops at the declared bound and accepts.  The two rules
#    agree wherever the stream's own end marker falls at the declared size - which
#    is every canonical packed container, and every accepted position on this
#    image: measured with a faithful write-counting transcription over all 13,463
#    submitted positions, **zero** accepted decodes reach a write offset above
#    their declared size, so the source's ``catch`` never discards one for that
#    reason and the reproduction's ``overrun`` is zero throughout.
#
# Two further deviations are each stricter than the source and are recorded here
# because they are the only places where the reproduction can reject a position
# the source would accept:
#
# * ``get(0)`` returns 0, where the C# ``GetBits(0)`` returns the buffered word
#   without shifting it.  Only reachable when a literal is read before the first
#   escape, which the first clause of this comment shows never happens on the
#   canonical corpus, so the deviation is inert there.
# * ``transfer_match`` refuses a zero distance, where the C# would write a zero
#   byte and advance.  Measured cost of both deviations together: the committed
#   reproduction yields 12,990 candidates, 175 raises, 12,912 unique payload
#   digests and 14 end-marker-short decodes; with both removed it yields 12,991,
#   174, 12,915 and 15.  That is one candidate and three digests, all class F, and
#   no recall or precision figure changes.


class _BitStream:
    """The external reader's source: whole little-endian words, bit 31 first.

    This is the external ``CompressionSource``: ``AdvanceBuffer`` loads
    ``rom.ReadInt()`` - a little-endian ``u32`` - into a bit buffer and consumes it
    from bit 31 down.  The source pointer therefore moves a whole word at a time,
    which is why a stream's consumed length is always a multiple of four and the
    engine over-reads up to three bytes past its final token.

    ``_bits_of`` spells the same framing out as an explicit sequence; the tests
    assert the two agree, so the order this class relies on is inspectable.
    """

    __slots__ = ("data", "position", "buf", "left", "start")

    def __init__(self, data: bytes, payload: int) -> None:
        self.data = data
        self.position = payload
        self.buf = 0
        self.left = 0
        self.start = payload

    def _advance(self) -> None:
        if self.position + 4 > len(self.data):
            raise GfxScanError("bit word would leave the image")
        self.buf = struct.unpack_from("<I", self.data, self.position)[0]
        self.position += 4
        self.left = 32

    def bit(self) -> int:
        if not self.left:
            self._advance()
        value = (self.buf >> 31) & 1
        self.buf = (self.buf << 1) & 0xFFFFFFFF
        self.left -= 1
        return value

    def get(self, count: int) -> int:
        if count < 0 or count > 32:
            raise GfxScanError(f"bit read of {count} is not representable")
        if count == 0:
            return 0
        if count <= self.left:
            value = (self.buf >> (32 - count)) & ((1 << count) - 1)
            self.buf = (self.buf << count) & 0xFFFFFFFF
            self.left -= count
            return value
        # The remainder is kept and the next word is shifted in behind it, exactly
        # as the external ``GetBits`` does across a word boundary.
        value = self.buf >> (32 - self.left) if self.left else 0
        remaining = count - self.left
        self._advance()
        value = (value << remaining) | (self.buf >> (32 - remaining))
        self.buf = (self.buf << remaining) & 0xFFFFFFFF
        self.left -= remaining
        return value

    def integer(self) -> int:
        """``GetInteger``: a payload bit, then a continuation bit.

        The external source writes

            do { result = (result << 1) + GetBit(); } while (GetBit() != 0);

        so the **payload** bit is read first and the **continuation** bit second,
        and the loop repeats while the continuation bit is *set*.  This method
        exits when that bit is clear, which is the same loop written from the other
        side - ``while (bit != 0)`` and ``if (bit == 0) return`` accept and reject
        exactly the same bit sequences.  The project decoder's ``gamma`` is the
        same loop again, so there is no transcription difference here at all.

        What does differ, and what this docstring exists to pin, is the *bit
        order*: reading the continuation bit first, or reading two bits before the
        first continuation test, produces a model that decodes hand-built streams
        and fails on every canonical container.  ``tests/unit`` pins the order on
        synthetic input; ``tests/integration/test_logx_gfxscan_rom.py`` pins the
        whole grammar against real containers.
        """
        value = 1
        while True:
            value = (value << 1) + self.bit()
            if self.bit() == 0:
                return value

    @property
    def source_consumed(self) -> int:
        """Bytes the engine's ``ldr rX,[rY],#4`` would have advanced."""
        return self.position - self.start


def _bits_of(data: bytes, position: int, limit: int) -> tuple[int, ...]:
    """The MSB-first bit sequence the external reader sees from ``position``.

    Whole little-endian words, consumed from bit 31 down; a trailing partial word
    is dropped exactly as ``AdvanceBuffer``'s ``Remaining >= 4`` test drops it.
    This is the readable statement of the bit order :class:`_BitStream` relies on,
    and the portable tests assert the two agree.
    """
    bits: list[int] = []
    cursor = position
    while cursor + 4 <= limit:
        word = struct.unpack_from("<I", data, cursor)[0]
        for shift in range(31, -1, -1):
            bits.append((word >> shift) & 1)
        cursor += 4
    return tuple(bits)


def external_decode_stream(
    data: bytes,
    payload: int,
    declared: int,
    *,
    max_output: int = HOST_MAX_OUTPUT,
) -> tuple[bytes, int, int, str]:
    """``JCALG1.DecompressInternal`` over the packed stream at ``payload``.

    Returns ``(accepted, overrun, source_end, terminator)``:

    * ``accepted`` - what ``Array.Resize(ref data, size)`` would hand the
      caller, i.e. the bytes written up to the declared size;
    * ``overrun`` - bytes the model produced past ``declared`` before the
      declared-size loop test caught it, i.e. what the engine would have written
      past the host allocation.  Reported so a clipped decode is never counted as
      an exact one;
    * ``source_end`` - the source position the reader reached, counted as whole
      words past ``payload``;
    * ``terminator`` - ``"declared_size"`` or ``"end_marker"``, the external
      reader's own two loop exits.

    The model raises where the external reader would throw: ``TransferMatch``
    indexing before the start of the destination, a bit word past the image, or a
    read that leaves the image.
    """
    if declared < 0 or declared > max_output:
        raise GfxScanError(f"declared size {declared} outside 0..{max_output}")
    if payload < 0 or payload > len(data):
        raise GfxScanError(f"payload offset {payload:#x} is outside the image")
    source = _BitStream(data, payload)
    out = bytearray()
    # The C# ``CompressionState`` leaves both fields at the CLR default of zero;
    # only the first width/base escape changes them.
    literal_bits = 0
    literal_offset = 0
    index_base = 8
    last_index = 1

    def transfer_match(offset: int, length: int) -> None:
        """``TransferMatch``: ``do { destination[w] = destination[w++ - offset]; }
        while (--length > 0);``.  Indexing before the start of the destination is
        the host's out-of-range exception, which the tool's ``catch`` swallows."""
        if offset <= 0 or offset > len(out):
            raise GfxScanError(
                f"back-reference offset {offset} at output {len(out)} runs before "
                "the start of the destination"
            )
        for _ in range(length):
            out.append(out[len(out) - offset])

    while True:
        if len(out) >= declared:
            return _finish(out, declared, source, "declared_size")
        if source.bit():
            # literal
            out.append((literal_offset + source.get(literal_bits)) & 0xFF)
            continue
        if source.bit():
            # normal phrase
            high_index = source.integer()
            if high_index == 2:
                transfer_match(last_index, source.integer())
                continue
            last_index = ((high_index - 3) << index_base) + source.get(index_base)
            phrase_length = source.integer()
            # The match length is biased by its own distance.  These four
            # thresholds are the engine's own constants, not a tidy formula
            # (LOGX-CODEC-001 section 8.3).
            if last_index >= 0x10000:
                phrase_length += 3
            elif last_index >= 0x37FF:
                phrase_length += 2
            elif last_index >= 0x27F:
                phrase_length += 1
            elif last_index <= 127:
                phrase_length += 4
            transfer_match(last_index, phrase_length)
            continue
        if source.bit():
            # one-byte phrase or literal size change
            value = source.get(4) - 1
            if value == 0:
                # The external source writes a plain zero here
                # (``destination[w++] = 0;``).  The project decoder writes its
                # literal base instead, and the difference is real: it is what
                # makes the two grammars disagree on 78 of the 11,712 known
                # kind-1 containers rather than 77.
                out.append(0)
            elif value > 0:
                transfer_match(value, 1)
            elif source.bit():
                # a run of raw 8-bit bytes, terminated by a clear bit
                while True:
                    for _ in range(256):
                        out.append(source.get(8))
                    if source.bit() == 0:
                        break
            else:
                literal_bits = 7 + source.bit()
                literal_offset = 0
                if literal_bits != 8:
                    literal_offset = source.get(8)
            continue
        # short phrase
        index = source.get(7)
        length = source.get(2) + 2
        if index == 0:
            if length == 2:
                return _finish(out, declared, source, "end_marker")
            index_base = source.get(length + 1)
        else:
            last_index = index
            transfer_match(last_index, length)


def _finish(
    out: bytearray,
    declared: int,
    source: "_BitStream",
    terminator: str,
) -> tuple[bytes, int, int, str]:
    """The external reader's exit: ``Array.Resize`` plus the source position.

    ``Array.Resize(ref data, size)`` truncates to what was actually written, so
    the tool's accepted payload can be *shorter* than the declared size.  The
    accepted bytes and the overrun are both reported; the caller decides.
    """
    overrun = max(0, len(out) - declared)
    accepted = bytes(out[:declared])
    return accepted, overrun, source.source_consumed, terminator


def external_decode(
    data: bytes,
    wrapper: int,
    *,
    max_output: int = HOST_MAX_OUTPUT,
) -> tuple[bytes, int, int, str]:
    """``JCALG1.Decompress`` at ``wrapper``: ``(accepted, overrun, consumed, terminator)``.

    ``consumed`` is the whole extent the model read, header included.  The stored
    arm is the external reader's own loop: it reads ``declared`` bytes and raises
    when the image ends first, which is exactly the behaviour ``ScanForImages``
    swallows.  ``terminator`` is ``"stored_memcpy"`` on that arm.
    """
    if wrapper < 0 or wrapper + 2 * 4 > len(data):
        raise GfxScanError(f"container header at {wrapper:#x} is outside the image")
    kind = _u32(data, wrapper)
    declared = _u32(data, wrapper + 4)
    payload = wrapper + 8
    if kind == 0:
        if declared < 0 or declared > max_output:
            raise GfxScanError(f"declared size {declared} outside 0..{max_output}")
        if payload + declared > len(data):
            raise GfxScanError("stored payload runs past the image")
        return data[payload : payload + declared], 0, 8 + declared, "stored_memcpy"
    if kind not in (1, 2):
        raise GfxScanError(f"unsupported dispatch word {kind}")
    accepted, overrun, source, terminator = external_decode_stream(
        data, payload, declared, max_output=max_output
    )
    return accepted, overrun, 8 + source, terminator


# --- scan population ----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScanPosition:
    """One wrapper position a scanner hands to its decompressor."""

    offset: int
    kind: int
    declared: int


@dataclass(frozen=True, slots=True)
class ScanPopulation:
    """What a search actually walks, as explicit quantities."""

    #: Byte positions the loop body executes at.
    positions_tested: int
    #: Positions whose first word passes the model's form test.
    kind_word_matches: int
    #: ``kind_word_matches`` whose declared size passes the size filter.
    size_filter_passes: int
    #: ``kind_word_matches`` whose declared size fails the filter.
    size_filter_rejects: int
    #: How many matched positions are word-aligned.
    kind_word_matches_aligned: int
    #: Positions handed to the decoder, ascending.
    submitted: tuple[ScanPosition, ...]


def scan_population(
    data: bytes,
    *,
    start: int = EXTERNAL_SCAN_START,
    end: int | None = None,
    require_kind: bool = True,
    size_multiple: int | None = EXTERNAL_SIZE_MULTIPLE,
    size_max_exclusive: int = EXTERNAL_SIZE_MAX_EXCLUSIVE,
    allowed_kinds: tuple[int, ...] | None = None,
    aligned_only: bool = False,
) -> ScanPopulation:
    """Reproduce a scan loop's selection, without decoding anything.

    ``require_kind`` keeps the external tool's ``magic != 0x1 -> continue``.
    ``allowed_kinds`` replaces that test with a form set; the engine model uses
    ``(0, 1, 2)``.  ``require_kind=False`` with ``allowed_kinds=None`` measures
    the raw population.

    The walk is genuinely every byte, which is what the external loop does.  The
    aligned subset is reported alongside because a wrapper is only itself at its
    own alignment: an unaligned match is a different four-byte window unless the
    bytes repeat, so the two counts are never mixed.
    """
    limit = len(data) if end is None else min(end, len(data))
    if limit - 3 > HOST_MAX_SCAN_POSITIONS:
        raise GfxScanError(
            f"scan population {limit - 3} exceeds the {HOST_MAX_SCAN_POSITIONS} "
            "position host bound"
        )
    submitted: list[ScanPosition] = []
    kind_word_matches = 0
    kind_word_matches_aligned = 0
    size_filter_passes = 0
    size_filter_rejects = 0

    for position in range(start, max(start, limit - 3)):
        if aligned_only and position % 4:
            continue
        kind = _u32(data, position)
        if require_kind:
            if kind != EXTERNAL_REQUIRED_KIND:
                continue
        elif allowed_kinds is not None and kind not in allowed_kinds:
            continue
        kind_word_matches += 1
        if position % 4 == 0:
            kind_word_matches_aligned += 1
        declared = _u32(data, position + 4)
        if not (EXTERNAL_SIZE_MIN <= declared < size_max_exclusive):
            size_filter_rejects += 1
            continue
        if size_multiple is not None and declared % size_multiple:
            size_filter_rejects += 1
            continue
        size_filter_passes += 1
        submitted.append(ScanPosition(offset=position, kind=kind, declared=declared))

    return ScanPopulation(
        positions_tested=max(0, limit - 3 - start),
        kind_word_matches=kind_word_matches,
        size_filter_passes=size_filter_passes,
        size_filter_rejects=size_filter_rejects,
        kind_word_matches_aligned=kind_word_matches_aligned,
        submitted=tuple(submitted),
    )


# --- candidates ---------------------------------------------------------------


@dataclass(slots=True)
class Candidate:
    """One accepted scanner candidate, with everything needed to classify it."""

    model: str
    position: int
    kind: int
    declared: int
    decoded_length: int
    decoded_sha256: str
    overrun: int
    source_end: int
    terminator: str
    aligned: bool
    priority: int
    category: str = ""
    details: dict[str, object] = field(default_factory=dict)

    @property
    def address(self) -> int:
        return to_address(self.position)

    @property
    def exact(self) -> bool:
        """No byte was produced past the declared size.

        Kept apart from :attr:`full_length`: a stream whose own end marker fires
        early is accepted by the external tool (``Array.Resize`` keeps what was
        written) but is not the container's declared output.
        """
        return self.overrun == 0

    @property
    def full_length(self) -> bool:
        return self.decoded_length == self.declared

    @property
    def extent_end(self) -> int:
        """Address one past the source the model consumed, header included."""
        return self.address + self.source_end


def run_external_model(
    data: bytes,
    population: ScanPopulation,
    *,
    max_candidates: int | None = None,
) -> tuple[list[Candidate], dict[str, int]]:
    """Run the external tool's acceptance rule over ``population``.

    A candidate is accepted exactly where ``ScanForImages`` would add a
    ``ScanResult``: the decompressor returned a non-empty array without raising.
    Nothing here interprets the payload.

    The literal state is zero at construction and changes only at a width/base
    escape.  It is **not** seeded from the declared-size word, and the authority
    for that is the **source**: ``CompressionState``'s constructor assigns only
    ``lastIndex`` and ``indexBase``, leaving ``literalBits`` and ``literalOffset``
    at the C# field default of zero.

    The corpus cannot discriminate the initial value, and this docstring says so
    rather than claiming otherwise: measured over all 11,712 kind-1 known
    containers and all 7,390 sprites, **zero** emit a literal before their first
    width/base escape, so the initial value is always overwritten before it can be
    read.  Seeding it with ``declared & 0xFF``, ``(declared >> 8) & 0xFF``,
    ``0x80`` or ``0xFF`` leaves the known-corpus result identical.
    """
    candidates: list[Candidate] = []
    stats = {
        "submitted": 0,
        "decode_ok": 0,
        "decode_raised": 0,
        "empty_output": 0,
        "exact_output": 0,
        "short_output_via_end_marker": 0,
        "clipped_output": 0,
        "stored_arm": 0,
    }
    for item in population.submitted:
        if max_candidates is not None and len(candidates) >= max_candidates:
            break
        stats["submitted"] += 1
        try:
            payload, overrun, consumed, terminator = external_decode(data, item.offset)
        except Exception:  # noqa: BLE001 - the external tool swallows every failure
            stats["decode_raised"] += 1
            continue
        if not payload:
            stats["empty_output"] += 1
            continue
        stats["decode_ok"] += 1
        if overrun:
            stats["clipped_output"] += 1
        else:
            stats["exact_output"] += 1
        if len(payload) != item.declared:
            stats["short_output_via_end_marker"] += 1
        if item.kind == 0:
            stats["stored_arm"] += 1
        candidates.append(
            Candidate(
                model=MODEL_EXTERNAL,
                position=item.offset,
                kind=item.kind,
                declared=item.declared,
                decoded_length=len(payload),
                decoded_sha256=_digest(payload),
                overrun=overrun,
                source_end=consumed,
                terminator=terminator,
                aligned=item.offset % 4 == 0,
                priority=1 if len(payload) == EXTERNAL_PRIORITY_LENGTH else 9,
            )
        )
    return candidates, stats


def run_engine_model(
    data: bytes,
    *,
    aligned_only: bool = True,
    max_candidates: int | None = None,
) -> tuple[list[Candidate], dict[str, int], ScanPopulation]:
    """Run the engine-informed variant: forms ``{0,1,2}``, aligned, exact.

    ``0x0803D940`` accepts only forms 0, 1 and 2; every accepted container start in
    the canonical image is word-aligned; and LOGX-CODEC-001 measured that the
    packed stream's own terminator agrees with the declared size on every
    canonical packed container.  The variant therefore requires word alignment and
    an exact decode, and reports each rejection reason separately rather than
    folding them into one count.

    ``aligned_only=False`` is the *unconstrained* variant, kept so the report can
    measure how much of a scan's yield is an alignment artefact.  The engine never
    forms a container start at an odd address, so the unconstrained variant is a
    measurement, not a model of the engine.
    """
    population = scan_population(
        data,
        require_kind=False,
        allowed_kinds=(0, 1, 2),
        size_multiple=None,
        size_max_exclusive=HOST_CANONICAL_MAX_OUTPUT + 1,
        aligned_only=aligned_only,
    )
    candidates: list[Candidate] = []
    stats = {
        "submitted": 0,
        "accepted": 0,
        "rejected_unrepresentable_kind": 0,
        "rejected_declared_over_host_bound": 0,
        "rejected_payload_past_image": 0,
        "rejected_decode_error": 0,
        "rejected_terminator_disagrees": 0,
        "stored_arm": 0,
        "packed_arm": 0,
    }
    for item in population.submitted:
        if max_candidates is not None and len(candidates) >= max_candidates:
            break
        stats["submitted"] += 1
        if item.kind not in (0, 1, 2):
            stats["rejected_unrepresentable_kind"] += 1
            continue
        if item.declared > HOST_CANONICAL_MAX_OUTPUT:
            stats["rejected_declared_over_host_bound"] += 1
            continue
        payload, source, terminator, reason = _engine_decode_one(
            data, item.kind, item.declared, item.offset
        )
        if reason:
            stats[f"rejected_{reason}"] += 1
            continue
        stats["accepted"] += 1
        stats["stored_arm" if item.kind == 0 else "packed_arm"] += 1
        candidates.append(
            Candidate(
                model=MODEL_ENGINE_ALIGNED if aligned_only else MODEL_ENGINE_UNCONSTRAINED,
                position=item.offset,
                kind=item.kind,
                declared=item.declared,
                decoded_length=len(payload),
                decoded_sha256=_digest(payload),
                overrun=0,
                source_end=source,
                terminator=terminator,
                aligned=item.offset % 4 == 0,
                priority=1 if len(payload) == EXTERNAL_PRIORITY_LENGTH else 9,
            )
        )
    return candidates, stats, population


def _engine_decode_one(
    data: bytes, kind: int, declared: int, offset: int
) -> tuple[bytes, int, str, str]:
    """One engine-model decode: ``(payload, source_end, terminator, reject_reason)``."""
    payload_offset = offset + 8
    if kind == 0:
        if declared < 0:
            return b"", 0, "", "payload_past_image"
        if payload_offset + declared > len(data):
            return b"", 0, "", "payload_past_image"
        return (
            data[payload_offset : payload_offset + declared],
            8 + declared,
            "stored_memcpy",
            "",
        )
    try:
        decoded = reference.decode_packed(
            data, payload_offset, declared_size=declared, stop_on="declared_size"
        )
    except reference.CodecError:
        return b"", 0, "", "decode_error"
    if decoded.terminator != "declared_size":
        return b"", 0, "", "terminator_disagrees"
    return decoded.data, 8 + decoded.source_consumed, decoded.terminator, ""


# --- the known-positive corpus ------------------------------------------------


@dataclass(slots=True)
class KnownResource:
    """One engine-reachable container, with the graph that reaches it."""

    address: int
    resource_class: str
    references: tuple[str, ...]
    kind: int
    declared_size: int
    decoded_length: int
    decoded_sha256: str
    packed_end: int
    slot_semantics: str
    graphics_identity: str
    decode_error: str = ""

    @property
    def extent(self) -> tuple[int, int]:
        """``(wrapper start, end)`` of the packed extent the container occupies."""
        return self.address, self.packed_end


@dataclass(slots=True)
class KnownCorpus:
    """Every known-positive population, kept apart by resource class.

    ``classes`` is a mapping, not a partition: one address can appear in more
    than one class, and :data:`CLASS_ZERO_HEADER` is deliberately a **subset** of
    :data:`CLASS_SELECTOR_STREAMS`.  Summing the per-class sizes therefore
    over-counts by exactly the size of that subset.  The authoritative totals are
    ``len(resources)`` and ``len(by_digest)``;
    :meth:`class_size_sum` states the over-count rather than hiding it.
    """

    resources: dict[int, KnownResource]
    classes: dict[str, list[int]]
    by_digest: dict[str, list[int]]
    _ranges: list[tuple[int, int, int]] = field(default_factory=list)
    _range_starts: list[int] = field(default_factory=list)

    def addresses(self) -> set[int]:
        return set(self.resources)

    def resource(self, address: int) -> KnownResource | None:
        return self.resources.get(address)

    def class_size_sum(self) -> int:
        return sum(len(addresses) for addresses in self.classes.values())

    def class_overlap(self) -> dict[int, list[str]]:
        """Addresses listed in more than one class, with the classes."""
        seen: dict[int, list[str]] = {}
        for name, addresses in self.classes.items():
            for address in addresses:
                seen.setdefault(address, []).append(name)
        return {
            address: names for address, names in seen.items() if len(names) > 1
        }

    def index_ranges(self) -> None:
        """Build the sorted extent tables used by :meth:`container_containing`."""
        self._ranges = sorted(
            (resource.address, resource.packed_end, resource.address)
            for resource in self.resources.values()
            if not resource.decode_error and resource.packed_end > resource.address
        )
        self._range_starts = [row[0] for row in self._ranges]

    def container_containing(self, address: int) -> int | None:
        """The known container whose extent contains ``address``, if any.

        The extent is the wrapper start plus the packed bytes the decoder
        actually consumed - measured, never read from a length field - so a
        candidate that starts inside another container's payload is caught here
        instead of being counted as a second discovery.
        """
        if not self._ranges:
            self.index_ranges()
        index = bisect.bisect_right(self._range_starts, address) - 1
        floor = address - HOST_MAX_OUTPUT
        while index >= 0:
            start, end, owner = self._ranges[index]
            if address < end:
                return owner
            if start < floor:
                break
            index -= 1
        return None


def build_known_corpus(data: bytes) -> KnownCorpus:
    """Enumerate every accepted resource graph's container population.

    Seeded from the accepted graphs only: a container is known because a named
    graph reaches it, never because a sweep found it.
    """
    groups: dict[str, dict[int, set[str]]] = {}

    def add(resource_class: str, address: int, reference: str) -> None:
        groups.setdefault(resource_class, {}).setdefault(address, set()).add(reference)

    # 1. sprite piece +0x08 graphics containers (LOGX-FRAME-001)
    for frame_address in frame.frame_addresses(data):
        record = frame.read_frame(data, frame_address)
        for index, piece in enumerate(record.pieces):
            offset = frame.to_file_offset(piece.graphics_raw)
            if offset is None:
                continue
            add(
                CLASS_SPRITE_PIECES,
                to_address(offset),
                f"frame:{frame_address:08X}/piece:{index}",
            )

    # 2. dominant map-layer chunk containers (LOGX-TILE-001)
    for address, references in codec.iter_dominant_chunk_targets(data).items():
        for reference in sorted(references):
            add(CLASS_MAP_CHUNKS, address, reference)

    # 3. root + 0x4C selector-bank containers
    for address, references in codec.iter_bank_containers(data).items():
        for reference in sorted(references):
            add(CLASS_BANK_CONTAINERS, address, reference)

    # 4. root + 0x48 selector streams, kept separate because their slot
    #    semantics is a u16 selector, not a tile index and not a tile
    for address, references in codec.iter_selector_streams(data).items():
        for reference in sorted(references):
            add(CLASS_SELECTOR_STREAMS, address, reference)

    # 5. the engine's own zero-header default container (LOGX-CODEC-001)
    add(
        CLASS_ENGINE_DEFAULT,
        codec.ENGINE_DEFAULT_CONTAINER,
        "engine:dominant_layer_constructor_default",
    )

    resources: dict[int, KnownResource] = {}
    classes: dict[str, list[int]] = {}
    by_digest: dict[str, list[int]] = {}
    for resource_class, members in groups.items():
        classes[resource_class] = sorted(members)
        for address in sorted(members):
            kind, declared = wl.read_header(data, address - ROM_BASE)
            payload = b""
            packed_end = address + wl.HEADER_SIZE
            decode_error = ""
            try:
                container = wl.unpack(data, address - ROM_BASE)
                payload = container.data
                packed_end = ROM_BASE + container.packed_end
            except wl.ContainerError as error:
                decode_error = str(error)
            digest = "" if decode_error else _digest(payload)
            resources[address] = KnownResource(
                address=address,
                resource_class=resource_class,
                references=tuple(sorted(members[address])),
                kind=kind,
                declared_size=declared,
                decoded_length=len(payload),
                decoded_sha256=digest,
                packed_end=packed_end,
                slot_semantics=SLOT_SEMANTICS.get(resource_class, "UNRESOLVED"),
                graphics_identity=GRAPHICS_IDENTITY.get(resource_class, "UNRESOLVED"),
                decode_error=decode_error,
            )
            if digest:
                by_digest.setdefault(digest, []).append(address)

    # Form-0 containers among the selector streams are a named population of
    # their own, because they are the stored-form instances the external model's
    # ``kind == 1`` filter cannot see.  It is a **subset**, not a sibling: the two
    # addresses stay in ``root_48_selector_streams`` so the classes partition the
    # corpus.  Reporting it as a separate top-level class would double-count them
    # in any sum over classes, which is exactly the arithmetic error the ticket
    # requires keeping apart.
    stored = [
        address
        for address in classes.get(CLASS_SELECTOR_STREAMS, [])
        if resources[address].kind == wl.STORED
    ]
    if stored:
        classes[CLASS_ZERO_HEADER] = stored

    corpus = KnownCorpus(resources=resources, classes=classes, by_digest=by_digest)
    corpus.index_ranges()
    return corpus


# --- classification -----------------------------------------------------------


def classify_candidates(
    candidates: list[Candidate],
    corpus: KnownCorpus,
    *,
    reference_index: dict[int, list[int]] | None = None,
) -> dict[str, int]:
    """Place every candidate in one of the ticket's categories.

    The order is explicit and is the whole argument of the ticket:

    1. the wrapper address is a known engine-reachable container -> ``A`` or
       ``B`` by that class's graphics identity;
    2. otherwise the decoded payload digest equals a known container's -> ``A``
       or ``B``, with ``same_payload_as`` recorded rather than counted as new;
    3. otherwise a decode the model itself did not perform exactly -> ``F``;
    4. otherwise a wrapper start inside a known container's extent -> ``F``;
    5. otherwise an independent engine reference -> ``D``;
    6. otherwise unaligned -> ``F``;
    7. otherwise ``E``.

    Step 5 never promotes a scan hit to graphics: graphics identity comes from an
    accepted graph, and a decode is not a graph.
    """
    tally = {label: 0 for label in CATEGORY_LABELS}
    for candidate in candidates:
        resource = corpus.resource(candidate.address)
        if resource is not None:
            candidate.category = (
                CATEGORY_KNOWN_GRAPHICS
                if resource.resource_class in GRAPHICS_CLASSES
                else CATEGORY_KNOWN_NON_GRAPHICS
            )
            candidate.details.update(
                {
                    "known_resource_class": resource.resource_class,
                    "known_reference": "wrapper_address",
                    "known_slot_semantics": resource.slot_semantics,
                    "known_graphics_identity": resource.graphics_identity,
                }
            )
            tally[candidate.category] += 1
            continue

        matches = [
            address
            for address in corpus.by_digest.get(candidate.decoded_sha256, [])
            if address != candidate.address
        ]
        if matches:
            match = corpus.resources[matches[0]]
            candidate.category = (
                CATEGORY_KNOWN_GRAPHICS
                if match.resource_class in GRAPHICS_CLASSES
                else CATEGORY_KNOWN_NON_GRAPHICS
            )
            candidate.details.update(
                {
                    "known_resource_class": match.resource_class,
                    "known_reference": "decoded_payload_digest",
                    "same_payload_as": [f"{address:08X}" for address in matches[:8]],
                    "same_payload_count": len(matches),
                    "known_slot_semantics": match.slot_semantics,
                    "known_graphics_identity": match.graphics_identity,
                }
            )
            tally[candidate.category] += 1
            continue

        if not candidate.exact:
            candidate.category = CATEGORY_FALSE_POSITIVE
            candidate.details["false_positive_class"] = FP_CLIPPED_DECODE
            candidate.details["overrun"] = candidate.overrun
            tally[candidate.category] += 1
            continue

        if not candidate.full_length:
            # the stream's own end marker fired before the declared size: the
            # external tool accepts this, a canonical container never does
            candidate.category = CATEGORY_FALSE_POSITIVE
            candidate.details["false_positive_class"] = FP_SHORT_VIA_END_MARKER
            candidate.details["terminator"] = candidate.terminator
            tally[candidate.category] += 1
            continue

        owner = corpus.container_containing(candidate.address)
        if owner is not None:
            candidate.category = CATEGORY_FALSE_POSITIVE
            candidate.details["false_positive_class"] = FP_INSIDE_KNOWN_CONTAINER
            candidate.details["inside_container"] = f"{owner:08X}"
            tally[candidate.category] += 1
            continue

        nested_owner = candidate.details.get("nested_inside_candidate")
        if nested_owner is not None:
            candidate.category = CATEGORY_FALSE_POSITIVE
            candidate.details["false_positive_class"] = FP_INSIDE_ANOTHER_CANDIDATE
            tally[candidate.category] += 1
            continue

        cited = (reference_index or {}).get(candidate.address, [])
        if cited:
            candidate.category = CATEGORY_NEW_ENGINE_REFERENCED
            candidate.details["engine_references"] = [
                f"{site:08X}" for site in cited[:16]
            ]
            candidate.details["engine_reference_count"] = len(cited)
            tally[candidate.category] += 1
            continue

        if not candidate.aligned:
            candidate.category = CATEGORY_FALSE_POSITIVE
            candidate.details["false_positive_class"] = FP_NOT_WORD_ALIGNED
            tally[candidate.category] += 1
            continue

        candidate.category = CATEGORY_UNRESOLVED_CONTAINER
        tally[candidate.category] += 1
    return tally


def flag_nested_candidates(candidates: list[Candidate]) -> int:
    """Flag candidates whose wrapper starts inside another *candidate's* extent.

    Two different things are kept apart here and in
    :func:`classify_candidates`, because collapsing them was a real defect of an
    earlier revision of this probe:

    * starting inside a **known engine-reachable container's** extent is
      :data:`FP_INSIDE_KNOWN_CONTAINER`, and only
      :meth:`KnownCorpus.container_containing` can establish it;
    * starting inside **another candidate's** measured extent is
      :data:`FP_INSIDE_ANOTHER_CANDIDATE`, which is what this function records.

    This function is a **pre-pass**: it runs before classification and records an
    address, not a category, so it never depends on a category that does not exist
    yet.  ``classify_candidates`` reads the recorded address and decides.
    Extents are the model's own measured source consumption, not a declared
    length, and the index is built once and sorted, so the pass is a bounded sweep
    rather than a pairwise comparison.
    """
    spans = sorted(
        (candidate.position, candidate.position + candidate.source_end, candidate)
        for candidate in candidates
        if candidate.source_end > 0
    )
    if not spans:
        return 0
    starts = [span[0] for span in spans]
    flagged = 0
    for start, _end, candidate in spans:
        index = bisect.bisect_right(starts, start) - 1
        floor = start - HOST_MAX_OUTPUT
        while index >= 0:
            other_start, other_end, other = spans[index]
            if other is not candidate and other_start <= start < other_end:
                candidate.details["nested_inside_candidate"] = f"{other.address:08X}"
                flagged += 1
                break
            if other_start < floor:
                break
            index -= 1
    return flagged


# --- reference search ---------------------------------------------------------


def reference_search(
    data: bytes,
    targets: set[int],
    *,
    word_aligned_only: bool = True,
) -> tuple[dict[int, list[int]], dict[str, object]]:
    """Find ROM words that name each target address.

    Two stored forms are searched, because the canonical corpus uses both, and
    they are kept apart in the result:

    * the **full GBA-address form** ``0x08000000 + offset``, which is a
      high-entropy word and therefore a strong hit;
    * the **bare file-offset form**, which for a small offset is a tiny integer
      that occurs by the thousand in code and data, so a lone bare-form hit is
      weak evidence and is reported as such.

    Coverage is stated rather than implied: this is a complete sweep of every word
    position in the image (or every word-aligned position), and it finds *data*
    references only.  A consumer reached through computed arithmetic, a folded
    base, or an ``LDM``/``STM`` aggregate is **not** covered, so an empty result is
    reported as "no reference found within the stated coverage", never as
    "unused".
    """
    if not targets:
        return {}, {
            "targets": 0,
            "word_positions_scanned": 0,
            "word_aligned_only": word_aligned_only,
            "stored_forms": ["gba_address", "file_offset"],
            "coverage": "no targets; nothing searched",
        }
    by_address: dict[int, int] = {target: target for target in targets}
    by_offset: dict[int, list[int]] = {}
    for target in targets:
        bare = target - ROM_BASE
        if bare >= 0:
            by_offset.setdefault(bare, []).append(target)

    hits: dict[int, list[int]] = {}
    forms: dict[int, dict[str, int]] = {}
    limit = len(data) - 3
    step = 4 if word_aligned_only else 1
    positions = 0
    for position in range(0, limit, step):
        positions += 1
        value = _u32(data, position)
        target = by_address.get(value)
        if target is not None:
            hits.setdefault(target, []).append(to_address(position))
            bucket = forms.setdefault(target, {"gba_address": 0, "file_offset": 0})
            bucket["gba_address"] += 1
            continue
        for candidate_target in by_offset.get(value, ()):
            hits.setdefault(candidate_target, []).append(to_address(position))
            bucket = forms.setdefault(
                candidate_target, {"gba_address": 0, "file_offset": 0}
            )
            bucket["file_offset"] += 1
    return hits, {
        "targets": len(targets),
        "targets_with_a_hit": len(hits),
        "targets_with_a_gba_address_hit": sum(
            1 for target in hits if forms.get(target, {}).get("gba_address")
        ),
        "targets_with_only_a_file_offset_hit": sum(
            1
            for target in hits
            if forms.get(target, {}).get("file_offset")
            and not forms.get(target, {}).get("gba_address")
        ),
        "word_positions_scanned": positions,
        "word_aligned_only": word_aligned_only,
        "stored_forms": ["gba_address", "file_offset"],
        "coverage": (
            "complete sweep for the two stored pointer forms; computed, folded "
            "and aggregate accesses are not covered; a lone file-offset-form hit "
            "is weak evidence because a small integer occurs throughout the image"
        ),
    }


# --- recall -------------------------------------------------------------------


@dataclass(slots=True)
class ClassRecall:
    """Recall and hit fidelity for one known-positive resource class."""

    resource_class: str
    known_references: int
    known_unique_resources: int
    scanner_hits: int
    scanner_misses: int
    digests_agreeing: int
    graphics_identity: str
    fail_reasons: dict[str, int]

    @property
    def hit_rate(self) -> float:
        if not self.known_unique_resources:
            return 0.0
        return self.scanner_hits / self.known_unique_resources


def recall_for(
    corpus: KnownCorpus,
    candidates: list[Candidate],
    resource_class: str,
) -> ClassRecall:
    """Measure one class against one model's accepted candidates.

    A hit is a candidate whose wrapper address is the container's address.  A
    digest match is reported separately, because the external model's decoder is
    not the project decoder: "found" and "decoded the same bytes" are different
    claims and are never merged into one number.
    """
    addresses = corpus.classes.get(resource_class, [])
    by_address = {candidate.address: candidate for candidate in candidates}
    found = [address for address in addresses if address in by_address]
    agreeing = sum(
        1
        for address in found
        if corpus.resources[address].decoded_sha256
        and by_address[address].decoded_sha256
        == corpus.resources[address].decoded_sha256
    )

    reasons: dict[str, int] = {}
    for address in addresses:
        if address in by_address:
            continue
        resource = corpus.resources[address]
        if resource.kind == 0:
            reason = "form_0_stored_not_matched_by_the_model"
        elif resource.declared_size >= EXTERNAL_SIZE_MAX_EXCLUSIVE:
            reason = "declared_size_over_the_external_size_filter"
        elif resource.declared_size % EXTERNAL_SIZE_MULTIPLE:
            reason = "declared_size_not_a_multiple_of_four"
        else:
            reason = "decodable_container_not_found_by_the_model"
        reasons[reason] = reasons.get(reason, 0) + 1

    references = sum(len(corpus.resources[address].references) for address in addresses)
    return ClassRecall(
        resource_class=resource_class,
        known_references=references,
        known_unique_resources=len(addresses),
        scanner_hits=len(found),
        scanner_misses=len(addresses) - len(found),
        digests_agreeing=agreeing,
        graphics_identity=GRAPHICS_IDENTITY.get(resource_class, "UNRESOLVED"),
        fail_reasons=reasons,
    )


# --- reporting ----------------------------------------------------------------


def _population_dict(population: ScanPopulation) -> dict[str, object]:
    return {
        "positions_tested": population.positions_tested,
        "kind_word_matches": population.kind_word_matches,
        "kind_word_matches_word_aligned": population.kind_word_matches_aligned,
        "size_filter_passes": population.size_filter_passes,
        "size_filter_rejects": population.size_filter_rejects,
        "submitted_to_decoder": len(population.submitted),
    }


def _candidate_totals(candidates: list[Candidate]) -> dict[str, object]:
    addresses = {candidate.address for candidate in candidates}
    digests = {candidate.decoded_sha256 for candidate in candidates}
    return {
        "raw_candidates": len(candidates),
        "unique_addresses": len(addresses),
        "unique_decoded_digests": len(digests),
        "aligned_candidates": sum(1 for c in candidates if c.aligned),
        "unaligned_candidates": sum(1 for c in candidates if not c.aligned),
        "no_overrun_decodes": sum(1 for c in candidates if c.exact),
        "full_declared_length_decodes": sum(1 for c in candidates if c.full_length),
        "short_via_end_marker_decodes": sum(
            1 for c in candidates if not c.full_length and c.terminator == "end_marker"
        ),
        "stored_arm_candidates": sum(1 for c in candidates if c.kind == 0),
        "packed_arm_candidates": sum(1 for c in candidates if c.kind != 0),
        "duplicate_reference_count": len(candidates) - len(addresses),
        "shared_payload_instances": len(candidates) - len(digests),
        "priority_length_candidates": sum(1 for c in candidates if c.priority == 1),
        "match_basis": _match_basis(candidates),
    }


def _match_basis(candidates: list[Candidate]) -> dict[str, int]:
    tally = {"wrapper_address": 0, "payload_digest": 0, "no_known_match": 0}
    for candidate in candidates:
        basis = candidate.details.get("known_reference")
        if basis == "wrapper_address":
            tally["wrapper_address"] += 1
        elif basis == "decoded_payload_digest":
            tally["payload_digest"] += 1
        else:
            tally["no_known_match"] += 1
    return tally


def _histogram(values) -> dict[int, int]:
    out: dict[int, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


def known_report(corpus: KnownCorpus) -> dict[str, object]:
    classes: dict[str, object] = {}
    for name, addresses in sorted(corpus.classes.items()):
        resources = [corpus.resources[address] for address in addresses]
        digests = {
            resource.decoded_sha256
            for resource in resources
            if resource.decoded_sha256
        }
        classes[name] = {
            "references": sum(len(resource.references) for resource in resources),
            "unique_containers": len(addresses),
            "unique_payload_digests": len(digests),
            "wrapper_kinds": _histogram(resource.kind for resource in resources),
            "declared_size_min": min((r.declared_size for r in resources), default=0),
            "declared_size_max": max((r.declared_size for r in resources), default=0),
            "decode_failures": sum(1 for resource in resources if resource.decode_error),
            "slot_semantics": SLOT_SEMANTICS.get(name, "UNRESOLVED"),
            "graphics_identity": GRAPHICS_IDENTITY.get(name, "UNRESOLVED"),
            "source_graph": CLASS_NOTES.get(name, {}).get("source_graph", ""),
            "evidence": CLASS_NOTES.get(name, {}).get("evidence", "UNRESOLVED"),
            "address_min": f"{min(addresses):08X}" if addresses else "",
            "address_max": f"{max(addresses):08X}" if addresses else "",
        }
    return {
        "classes": classes,
        "unique_containers": len(corpus.resources),
        "unique_payload_digests": len(corpus.by_digest),
        "class_size_sum": corpus.class_size_sum(),
        "class_overlap": {
            f"{address:08X}": names
            for address, names in sorted(corpus.class_overlap().items())
        },
        "class_overlap_note": (
            "class_size_sum exceeds unique_containers by the size of each "
            "subset class; CLASS_ZERO_HEADER is a subset of "
            "CLASS_SELECTOR_STREAMS, not a sibling"
        ),
        "shared_payload_digest_groups": sum(
            1 for addresses in corpus.by_digest.values() if len(addresses) > 1
        ),
        "shared_payload_addresses": sum(
            len(addresses) for addresses in corpus.by_digest.values() if len(addresses) > 1
        ),
    }


@dataclass(slots=True)
class ModelRun:
    """One model's candidates plus the populations they came from."""

    name: str
    population: ScanPopulation
    stats: dict[str, int]
    candidates: list[Candidate]


def run_model(data: bytes, name: str, *, max_candidates: int | None = None) -> ModelRun:
    if name == MODEL_EXTERNAL:
        population = scan_population(data)
        candidates, stats = run_external_model(
            data, population, max_candidates=max_candidates
        )
        return ModelRun(name, population, stats, candidates)
    if name in (MODEL_ENGINE_ALIGNED, MODEL_ENGINE_UNCONSTRAINED):
        candidates, stats, population = run_engine_model(
            data,
            aligned_only=name == MODEL_ENGINE_ALIGNED,
            max_candidates=max_candidates,
        )
        return ModelRun(name, population, stats, candidates)
    raise GfxScanError(f"unknown model {name!r}")


def model_report(run: ModelRun, corpus: KnownCorpus) -> dict[str, object]:
    return {
        "model": run.name,
        "scan_population": _population_dict(run.population),
        "decoder_stats": dict(run.stats),
        "totals": _candidate_totals(run.candidates),
        "recall": {
            name: asdict(recall_for(corpus, run.candidates, name))
            for name in RECALL_CLASSES
        },
        "category_tally": _category_tally(run.candidates),
        "false_positive_classes": _false_positive_classes(run.candidates),
    }


def _category_tally(candidates: list[Candidate]) -> dict[str, int]:
    tally = {label: 0 for label in CATEGORY_LABELS}
    for candidate in candidates:
        tally[candidate.category] = tally.get(candidate.category, 0) + 1
    return tally


def external_model_report(data: bytes, *, max_candidates: int | None = None) -> dict[str, object]:
    corpus = build_known_corpus(data)
    run = run_model(data, MODEL_EXTERNAL, max_candidates=max_candidates)
    hits, coverage = reference_search(
        data,
        {
            candidate.address
            for candidate in run.candidates
            if corpus.resource(candidate.address) is None
            and not corpus.by_digest.get(candidate.decoded_sha256)
        },
    )
    flag_nested_candidates(run.candidates)
    classify_candidates(run.candidates, corpus, reference_index=hits)
    report = model_report(run, corpus)
    report["source"] = (
        "mainant/LOGExtractor ImageScan ScanForImages + Gba/JCALG1.cs "
        "(pinned revision in docs/research/LOGX_GFXSCAN_PROVENANCE.md)"
    )
    report["reference_search_coverage"] = coverage
    report["recall_by_class"] = recall_table(
        corpus, run.candidates, list(corpus.classes)
    )
    return report


def engine_model_report(
    data: bytes, *, aligned_only: bool = True, max_candidates: int | None = None
) -> dict[str, object]:
    corpus = build_known_corpus(data)
    name = MODEL_ENGINE_ALIGNED if aligned_only else MODEL_ENGINE_UNCONSTRAINED
    run = run_model(data, name, max_candidates=max_candidates)
    hits, coverage = reference_search(
        data,
        {
            candidate.address
            for candidate in run.candidates
            if corpus.resource(candidate.address) is None
            and not corpus.by_digest.get(candidate.decoded_sha256)
        },
    )
    flag_nested_candidates(run.candidates)
    classify_candidates(run.candidates, corpus, reference_index=hits)
    report = model_report(run, corpus)
    report["reference_search_coverage"] = coverage
    report["recall_by_class"] = recall_table(
        corpus, run.candidates, list(corpus.classes)
    )
    return report


def full_report(data: bytes, *, max_candidates: int | None = None) -> dict[str, object]:
    """Every model, classified, with the reference search and the residual set."""
    corpus = build_known_corpus(data)
    runs = {
        name: run_model(data, name, max_candidates=max_candidates)
        for name in (
            MODEL_EXTERNAL,
            MODEL_ENGINE_ALIGNED,
            MODEL_ENGINE_UNCONSTRAINED,
        )
    }

    unknown_engine_addresses = {
        candidate.address
        for candidate in runs[MODEL_ENGINE_ALIGNED].candidates
        if corpus.resource(candidate.address) is None
        and not corpus.by_digest.get(candidate.decoded_sha256)
    }
    hits, coverage = reference_search(data, unknown_engine_addresses)

    nested = {}
    for name, run in runs.items():
        nested[name] = flag_nested_candidates(run.candidates)
        classify_candidates(run.candidates, corpus, reference_index=hits)

    return {
        "rom_sha256": CANONICAL_SHA256,
        "known": known_report(corpus),
        "models": {name: model_report(run, corpus) for name, run in runs.items()},
        "recall_by_class": recall_table(corpus, runs[MODEL_EXTERNAL].candidates, list(corpus.classes)),
        "reference_search_coverage": coverage,
        "reference_search_targets": len(unknown_engine_addresses),
        "reference_search_targets_with_hits": len(hits),
        "nested_candidate_flags": nested,
        "residual": residual_report(
            corpus, runs[MODEL_ENGINE_ALIGNED], runs[MODEL_EXTERNAL], hits
        ),
    }


def recall_table(
    corpus: KnownCorpus, candidates: list[Candidate], classes: list[str]
) -> dict[str, object]:
    """Recall per known-positive class, with the graphics classes marked."""
    table: dict[str, object] = {}
    for name in sorted(classes):
        row = asdict(recall_for(corpus, candidates, name))
        row["is_graphics_class"] = name in GRAPHICS_CLASSES
        row["counts_toward_recall"] = name in RECALL_CLASSES
        table[name] = row
    return table


# --- the residual set ---------------------------------------------------------


#: Categories a residual candidate can carry.  ``F`` is reported separately: a
#: candidate the model itself could not decode cleanly is not a discovery.
RESIDUAL_CATEGORIES = (
    CATEGORY_UNRESOLVED_CONTAINER,
    CATEGORY_NEW_ENGINE_REFERENCED,
    CATEGORY_NO_REFERENCE,
)


def residual_report(
    corpus: KnownCorpus,
    run: "ModelRun",
    external_run: "ModelRun",
    reference_hits: dict[int, list[int]],
) -> dict[str, object]:
    """The residual set: candidates no accepted graph reaches, classified.

    Two questions are kept apart and both are answered:

    * **Is the payload already in the image?**  A candidate whose decoded bytes
      equal a known container's bytes is not new content even when its wrapper
      address is new; that is counted as ``payload_already_known`` rather than as
      a discovery.
    * **Does anything name it?**  The search coverage is restated with every
      claim, so an empty result reads as "no reference found within the stated
      coverage", never as "unused".

    Cross-model agreement is reported too: a residual candidate the external model
    also produced, at the same address with the same digest, is the strongest
    structural evidence available for it, and a candidate only one model produced
    is weaker.
    """
    external_by_address = {candidate.address: candidate for candidate in external_run.candidates}
    rows: list[dict[str, object]] = []
    for candidate in sorted(run.candidates, key=lambda c: c.address):
        if candidate.category not in RESIDUAL_CATEGORIES:
            continue
        same_payload = [
            f"{address:08X}"
            for address in corpus.by_digest.get(candidate.decoded_sha256, [])
        ]
        other = external_by_address.get(candidate.address)
        rows.append(
            {
                "address": f"{candidate.address:08X}",
                "file_offset": f"{candidate.position:#08x}",
                "model": candidate.model,
                "wrapper_kind": candidate.kind,
                "declared_size": candidate.declared,
                "decoded_length": candidate.decoded_length,
                "decoded_sha256": candidate.decoded_sha256,
                "packed_extent_end": f"{candidate.extent_end:08X}",
                "source_bytes_consumed": candidate.source_end,
                "aligned": candidate.aligned,
                "category": candidate.category,
                "payload_already_known": bool(same_payload),
                "same_payload_as": same_payload[:8],
                "engine_reference_status": (
                    "ENGINE-REFERENCED"
                    if candidate.category == CATEGORY_NEW_ENGINE_REFERENCED
                    else "NO REFERENCE FOUND WITHIN THE DOCUMENTED COVERAGE"
                ),
                "engine_references": candidate.details.get("engine_references", []),
                "external_model_agrees": bool(
                    other is not None
                    and other.decoded_sha256 == candidate.decoded_sha256
                ),
                "graphics_evidence": graphics_evidence(candidate),
                "confidence": confidence(candidate),
            }
        )

    novel = [row for row in rows if not row["payload_already_known"]]
    cited = [row for row in novel if row["engine_references"]]
    return {
        "model": run.name,
        "candidate_universe": len(run.candidates),
        "residual_candidates": len(rows),
        "residual_by_category": _tally_rows(rows, "category"),
        "residual_with_a_known_payload": len(rows) - len(novel),
        "residual_with_a_novel_payload": len(novel),
        "residual_engine_referenced": len(cited),
        "residual_no_reference_found": len(novel) - len(cited),
        "residual_confirmed_by_both_models": sum(
            1 for row in novel if row["external_model_agrees"]
        ),
        "candidate_universe_by_category": _category_tally(run.candidates),
        "false_positive_classes": _false_positive_classes(run.candidates),
        "reference_search_coverage": (
            "complete word sweep for the two stored pointer forms; computed, "
            "folded and aggregate accesses are not covered; a lone file-offset-form "
            "hit is weak evidence because a small integer occurs throughout the image"
        ),
        "rows": rows,
    }


def _tally_rows(rows: list[dict[str, object]], key: str) -> dict[str, int]:
    tally: dict[str, int] = {}
    for row in rows:
        value = str(row[key])
        tally[value] = tally.get(value, 0) + 1
    return dict(sorted(tally.items()))


def _false_positive_classes(candidates: list[Candidate]) -> dict[str, int]:
    tally: dict[str, int] = {}
    for candidate in candidates:
        if candidate.category != CATEGORY_FALSE_POSITIVE:
            continue
        label = str(candidate.details.get("false_positive_class", "unclassified"))
        tally[label] = tally.get(label, 0) + 1
    return dict(sorted(tally.items()))


def graphics_evidence(candidate: Candidate) -> str:
    """What is actually established about a residual candidate's payload.

    Never "graphics" from a decode.  A residual candidate has no accepted graph
    reaching it, so at most its *shape* is known: length, tile divisibility and
    whether the decoded bytes could be a whole number of 8x8 tiles at 4bpp or
    8bpp.  Tile divisibility is necessary and nowhere near sufficient - the
    dominant-layer chunks are exactly 2,048 bytes of u16 tile indices and are not
    pixels.

    The wording is deliberately about the **rendering consumer**, not about
    engine references: a residual candidate may well be named by a word in the
    image (``engine_reference_status`` says so), and what is missing is a
    consumer whose role is established, not the existence of a pointer.
    """
    length = candidate.decoded_length
    if candidate.kind == 0:
        form = "form 0 stored"
    else:
        form = f"form {candidate.kind} packed"
    whole_tiles = length % 32 == 0
    return (
        f"{form}; decoded length {length} bytes; "
        f"{'a' if whole_tiles else 'not a'} whole number of 8x8 GBA tiles "
        "(32 bytes at 4bpp, 64 at 8bpp); no rendering consumer established"
    )


def confidence(candidate: Candidate) -> str:
    if candidate.category == CATEGORY_NEW_ENGINE_REFERENCED:
        return "INFERRED: a word in the image names this address"
    if candidate.category == CATEGORY_NO_REFERENCE:
        return "UNKNOWN: structurally valid container, no consumer found"
    if candidate.category == CATEGORY_UNRESOLVED_CONTAINER:
        return "UNKNOWN: container semantics unresolved"
    return "UNRESOLVED"


def reference_report(data: bytes, *, max_candidates: int | None = None) -> dict[str, object]:
    """Reference status for every engine-model candidate outside the graphs."""
    corpus = build_known_corpus(data)
    run = run_model(data, MODEL_ENGINE, max_candidates=max_candidates)
    unknown = {
        candidate.address
        for candidate in run.candidates
        if corpus.resource(candidate.address) is None
        and not corpus.by_digest.get(candidate.decoded_sha256)
    }
    hits, coverage = reference_search(data, unknown)
    rows = []
    for candidate in sorted(run.candidates, key=lambda c: c.address):
        if candidate.address not in unknown:
            continue
        cited = hits.get(candidate.address, [])
        rows.append(
            {
                "address": f"{candidate.address:08X}",
                "wrapper_kind": candidate.kind,
                "decoded_length": candidate.decoded_length,
                "status": (
                    "ENGINE-REFERENCED" if cited else
                    "NO REFERENCE FOUND WITHIN THE DOCUMENTED COVERAGE"
                ),
                "reference_count": len(cited),
                "references": [f"{site:08X}" for site in cited[:16]],
            }
        )
    return {
        "coverage": coverage,
        "candidates_outside_graphs": len(rows),
        "engine_referenced": sum(1 for row in rows if row["reference_count"]),
        "no_reference_found": sum(1 for row in rows if not row["reference_count"]),
        "rows": rows,
    }


# --- CLI ----------------------------------------------------------------------


def diff_report(full: dict[str, object]) -> dict[str, object]:
    """The external model against the engine-informed model, side by side.

    The point of the comparison is which constraints the external method lacks,
    so the differences are stated as differences rather than as a score.
    """
    models = full["models"]
    external = models[MODEL_EXTERNAL]
    engine = models[MODEL_ENGINE_ALIGNED]
    unconstrained = models[MODEL_ENGINE_UNCONSTRAINED]
    return {
        "external_candidates": external["totals"]["raw_candidates"],
        "engine_aligned_candidates": engine["totals"]["raw_candidates"],
        "engine_unconstrained_candidates": unconstrained["totals"]["raw_candidates"],
        "alignment_artefact_candidates": (
            unconstrained["totals"]["raw_candidates"]
            - engine["totals"]["raw_candidates"]
        ),
        "external_unique_digests": external["totals"]["unique_decoded_digests"],
        "engine_aligned_unique_digests": engine["totals"]["unique_decoded_digests"],
        "external_match_basis": external["totals"]["match_basis"],
        "engine_aligned_match_basis": engine["totals"]["match_basis"],
        "external_recall_by_class": full["recall_by_class"],
        "external_category_tally": external["category_tally"],
        "engine_aligned_category_tally": engine["category_tally"],
        "engine_unconstrained_category_tally": unconstrained["category_tally"],
        "external_false_positive_classes": _false_positive_classes_detail(models),
        "external_rejected_by_decode": external["decoder_stats"]["decode_raised"],
        "external_empty_output": external["decoder_stats"]["empty_output"],
        "engine_rejection_reasons": {
            key: value
            for key, value in engine["decoder_stats"].items()
            if key.startswith("rejected_")
        },
    }


def _false_positive_classes_detail(models: dict[str, object]) -> dict[str, object]:
    return {
        "external": models[MODEL_EXTERNAL]["false_positive_classes"],
        "engine_aligned": models[MODEL_ENGINE_ALIGNED]["false_positive_classes"],
        "engine_unconstrained": models[MODEL_ENGINE_UNCONSTRAINED][
            "false_positive_classes"
        ],
    }


# --- the external UnknownHeader heuristic ------------------------------------


def unknown_header_report(data: bytes) -> dict[str, object]:
    """Measure ``JCALG1.DecompressUnknownHeader`` as an external heuristic.

    The routine does ``PushPosition(address); Skip(0x4);`` and then creates a
    fresh ``CompressionSource``, whose first ``AdvanceBuffer`` reads the word at
    the *new* position.  So the first stream byte it reads is ``container + 4`` -
    the declared-size word - and its destination is 64 KiB rather than the
    declared size, with the literal state left at the C# field default of zero.
    ``ScanForImages`` never calls it, and LOGX-CODEC-001 REFUTED headerless
    streams as an engine container form, so this is measured only as an external
    heuristic: it decodes bytes that are not the stream the wrapper names.

    The population is bounded and named: the first 2,048 known packed containers
    in ascending address order.  Results are digests and counts, never payloads.
    """
    checked = 0
    accepted = 0
    agreeing = 0
    examples: list[dict[str, object]] = []
    corpus = build_known_corpus(data)
    packed = [
        address
        for address in sorted(corpus.resources)
        if corpus.resources[address].kind in wl.PACKED_KINDS
    ][:2048]
    for address in packed:
        resource = corpus.resources[address]
        checked += 1
        # Skip(0x4) then the reader's first AdvanceBuffer: the first word read is
        # at container + 4, not container + 8.
        payload = address - ROM_BASE + EXTERNAL_UNKNOWN_HEADER_SKIP
        try:
            decoded, overrun, source, _term = external_decode_stream(
                data, payload, resource.declared_size
            )
        except Exception:  # noqa: BLE001 - the heuristic's own failure mode
            continue
        accepted += 1
        if resource.decoded_sha256 and _digest(decoded) == resource.decoded_sha256:
            agreeing += 1
        if len(examples) < 8:
            examples.append(
                {
                    "container_address": f"{address:08X}",
                    "heuristic_first_word_offset": f"{payload:#08x}",
                    "declared": resource.declared_size,
                    "overrun": overrun,
                    "source_end": source,
                    "digest_agrees_with_canonical": bool(
                        resource.decoded_sha256
                        and _digest(decoded) == resource.decoded_sha256
                    ),
                }
            )
    return {
        "external_routine": (
            "JCALG1.DecompressUnknownHeader (Skip(4), then a fresh source whose "
            "first word is at container + 4; 64 KiB destination; literal state at "
            "the C# default of zero)"
        ),
        "called_by_scan_for_images": False,
        "engine_container_form": (
            "REFUTED by LOGX-CODEC-001 as an engine container form; measured here "
            "only as an external heuristic"
        ),
        "population": "first 2,048 known packed containers, ascending address",
        "checked_known_packed_containers": checked,
        "accepted": accepted,
        "digest_agrees_with_canonical": agreeing,
        "examples": examples,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom")
    parser.add_argument("--external-model", action="store_true")
    parser.add_argument("--engine-model", action="store_true")
    parser.add_argument("--known", action="store_true")
    parser.add_argument("--classify", action="store_true")
    parser.add_argument("--diff", action="store_true")
    parser.add_argument("--residual", action="store_true")
    parser.add_argument("--references", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--unknown-header", action="store_true",
                        help="measure the external UnknownHeader heuristic separately")
    parser.add_argument("--max-candidates", type=int, default=None,
                        help="host bound on candidates per model (deterministic prefix)")
    parser.add_argument("--json")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    out: dict[str, object] = {"rom_sha256": CANONICAL_SHA256}
    do_all = args.summary or not (
        args.external_model
        or args.engine_model
        or args.known
        or args.classify
        or args.diff
        or args.residual
        or args.references
        or args.unknown_header
    )

    if args.known:
        out["known"] = known_report(build_known_corpus(data))
        print(json.dumps(out["known"], indent=2))

    if args.external_model:
        out["external_model"] = external_model_report(
            data, max_candidates=args.max_candidates
        )
        print(json.dumps(out["external_model"], indent=2))

    if args.engine_model:
        for aligned in (True, False):
            key = "engine_model" if aligned else "engine_model_unconstrained"
            out[key] = engine_model_report(
                data, aligned_only=aligned, max_candidates=args.max_candidates
            )
            print(json.dumps(out[key], indent=2))

    if args.residual or args.references or args.classify or args.diff or do_all:
        full = full_report(data, max_candidates=args.max_candidates)
        out["full"] = full
        if args.classify or do_all:
            print(json.dumps(full, indent=2))

    if args.diff and not do_all:
        out["diff"] = diff_report(out["full"])
        print(json.dumps(out["diff"], indent=2))

    if args.residual:
        out["residual"] = out["full"]["residual"]
        print(json.dumps(out["residual"], indent=2))

    if args.references:
        out["references"] = reference_report(data, max_candidates=args.max_candidates)
        print(json.dumps(out["references"], indent=2))

    if args.unknown_header:
        out["unknown_header"] = unknown_header_report(data)
        print(json.dumps(out["unknown_header"], indent=2))

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
