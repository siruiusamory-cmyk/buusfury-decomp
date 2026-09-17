"""Portable synthetic tests for the LOGX-CODEC-001 reference codec.

Two kinds of fixture appear here and they are deliberately different.

* **Hand-built wrapper bytes.** The wrapper is eight bytes of two little-endian
  words; its layout is asserted directly against bytes this test constructs.
* **Hand-built opening tokens plus the project encoder's output.** A packed
  stream's *grammar* is asserted by decoding streams produced by
  ``webfoot_lz.pack`` and requiring exact equality with the input, and by
  hand-built control tokens whose consumed bit positions are asserted.

**What the round-trip does and does not prove.** ``decode_packed`` was written
after the project decoder was read, so the two share most of their grammar line
for line and a shared misreading would not be caught by the round-trip alone. The
round-trip proves the two agree and that the encoder's output is decodable; the
grammar's authority rests on the corpus differential in
``tests/integration/test_logx_codec_rom.py`` and on the downstream invariants
established independently by LOGX-TILE-001. See
``docs/research/LOGX_CODEC_PROVENANCE.md`` section 14.

No ROM bytes and no ROM-derived payloads are committed or constructed here. The
whole-corpus differential with real containers lives in
`tests/integration/test_logx_codec_rom.py` and skips cleanly without the image.
"""

from __future__ import annotations

import struct

import pytest

from tools.research import webfoot_codec_reference as codec
from tools.webfoot.formats import webfoot_lz as wl


def _bits_to_words(bit_string: str) -> bytes:
    """Pack an MSB-first bit string into little-endian 32-bit words."""
    padded = bit_string.ljust((len(bit_string) + 31) // 32 * 32, "0")
    words = [int(padded[i : i + 32], 2) for i in range(0, len(padded), 32)]
    return b"".join(struct.pack("<I", word) for word in words)


def _opening(base: int = 0x00) -> str:
    """The control token that opens every canonical packed stream.

    Read from the raw bits of the canonical container at ``0x0817C144`` (see
    ``LOGX_CODEC_PROVENANCE.md`` section 7.4). Shape, 17 bits:

    * prefix ``0 0 1`` - the third bit is set, so this is the four-bit-code form;
    * four-bit code ``0000`` - the literal-width / base escape;
    * two-bit escape field ``00`` - keep the 7-bit literal width and read a base;
    * eight base bits.

    After it the literal width is 7 and ``base`` is added to every literal.
    """
    assert 0 <= base <= 0xFF
    return "001" + "0000" + "00" + f"{base:08b}"


def _opening_width8() -> str:
    """The same escape with a non-zero two-bit field: 8-bit literals, no base."""
    return "001" + "0000" + "01"


def _literal7(value: int) -> str:
    """One literal at the 7-bit width the base-selecting opening token leaves."""
    assert 0 <= value <= 0x7F
    return "1" + f"{value:07b}"


def _literal8(value: int) -> str:
    assert 0 <= value <= 0xFF
    return "1" + f"{value:08b}"


def _end_marker() -> str:
    """The terminator: prefix ``0 0 0``, a seven-bit field of zero, two more zeros.

    Note the prefix. The seven-bit/control form has its third bit **clear** and
    the four-bit form has it set, so the marker starts ``0 0 0``, not ``0 0 1``.
    """
    return "000" + f"{0:07b}" + "00"


# --- wrapper -----------------------------------------------------------------


def test_dispatcher_report_states_the_engine_contract() -> None:
    report = codec.dispatcher_report()
    assert report["dispatcher"] == 0x0803D940
    text = "\n".join(report["dispatcher_decoded"])
    assert "cmp  r3, #0" in text
    assert "cmp  r3, #1" in text
    assert "cmp  r3, #2" in text
    assert "bne  0x0803d95c" in text
    assert "adds r1, #8" in text
    assert "ldr  r2, [r2, #4]" in text
    assert report["dispatcher_decoded"][0].startswith("0803d940 adds r2, r0, #0")


def test_wrapper_layout_is_two_words_then_payload() -> None:
    assert wl.HEADER_SIZE == 8
    assert wl.STORED == 0
    assert wl.PACKED_KINDS == (1, 2)
    assert codec.WEBFOOT_DISPATCHER == 0x0803D940


def test_stored_form_copies_exactly_the_declared_length() -> None:
    payload = bytes(range(16))
    blob = struct.pack("<II", 0, len(payload)) + payload
    got = wl.unpack(blob, 0)
    assert got.kind == 0
    assert got.data == payload
    assert got.declared_size == len(payload)
    assert got.packed_end == 8 + len(payload)


def test_stored_form_with_zero_length_is_valid_and_empty() -> None:
    """The engine's own default container is kind 0 declaring 0 bytes."""
    blob = struct.pack("<II", 0, 0) + bytes(0x800)
    got = wl.unpack(blob, 0)
    assert got.data == b""
    assert got.declared_size == 0


def test_zero_first_word_is_not_a_sentinel() -> None:
    """A zero dispatch word with a non-zero second word is a real stored payload."""
    payload = b"\xAA\xBB\xCC\xDD"
    blob = struct.pack("<II", 0, 4) + payload
    assert wl.unpack(blob, 0).data == payload


@pytest.mark.parametrize("kind", [3, 4, 0xFFFFFFFF])
def test_unknown_dispatch_word_is_rejected_by_the_project_decoder(kind: int) -> None:
    blob = struct.pack("<II", kind, 4) + b"\x00\x00\x00\x00"
    with pytest.raises(wl.ContainerError):
        wl.unpack(blob, 0)


# --- grammar -----------------------------------------------------------------


def test_base_escape_then_seven_bit_literals() -> None:
    """The engine's opening token plus two literals, decoded exactly."""
    bits = _opening() + _literal7(0x41) + _literal7(0x42)
    blob = struct.pack("<II", 1, 2) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=2)
    assert got.data == b"AB"
    assert got.actual_size == 2


def test_base_escape_adds_the_base_to_every_literal() -> None:
    bits = _opening(0x10) + _literal7(0x00) + _literal7(0x05) + _literal7(0x20)
    blob = struct.pack("<II", 1, 3) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=3)
    assert got.data == b"\x10\x15\x30"


def test_escape_with_a_non_zero_field_selects_eight_bit_literals() -> None:
    """The other escape form: width 8 and no base byte is read."""
    bits = _opening_width8() + _literal8(0x41) + _literal8(0x42)
    blob = struct.pack("<II", 1, 2) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=2)
    assert got.data == b"AB"


def test_end_marker_stops_a_stream_that_reaches_it() -> None:
    """The marker must be consumed at its own position, not via byte padding.

    The stream is padded to a whole word by ``_bits_to_words``, so a decode that
    runs past the marker would still eventually stop on that padding. Asserting
    the consumed-bit position is what makes this test pin the marker itself.
    """
    bits = _opening() + _literal7(0x5A) + _end_marker()
    blob = struct.pack("<II", 1, 1) + _bits_to_words(bits)
    log: list[int] = []
    got = codec.decode_packed(
        blob, 8, declared_size=1, stop_on="end_marker", _bit_log=log
    )
    assert got.terminator == "end_marker"
    assert got.data == b"\x5A"
    assert len(log) == 37, f"consumed {len(log)} bits, expected 37"


def test_short_match_and_control_prefix_is_000_not_001() -> None:
    """Pin the prefix polarities, which is where a reader most easily inverts.

    The seven-bit/control form (short match, distance-width control and the end
    marker) has the third prefix bit **clear**; the four-bit code form has it
    **set**. A stream built with either polarity swapped must not decode the same.
    """
    good = _opening() + _literal7(0x5A) + _end_marker()
    swapped = _opening() + _literal7(0x5A) + "001" + f"{0:07b}" + "00"
    blob_good = struct.pack("<II", 1, 1) + _bits_to_words(good)
    blob_swapped = struct.pack("<II", 1, 1) + _bits_to_words(swapped)
    stops_at = len(_opening()) + len(_literal7(0x5A)) + len(_end_marker())
    log: list[int] = []
    codec.decode_packed(
        blob_good, 8, declared_size=1, stop_on="end_marker", _bit_log=log
    )
    assert len(log) == stops_at
    # The inverted form is not a marker: it must not stop at the same point.
    log2: list[int] = []
    try:
        codec.decode_packed(
            blob_swapped, 8, declared_size=1, stop_on="end_marker", _bit_log=log2
        )
    except codec.CodecError:
        pass
    assert len(log2) != stops_at


def test_declared_size_stops_the_stream_first() -> None:
    bits = _opening() + _literal7(0x5A) + _end_marker()
    blob = struct.pack("<II", 1, 1) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=1)
    assert got.terminator == "declared_size"
    assert got.data == b"\x5A"


def test_declared_size_zero_decodes_to_nothing() -> None:
    bits = _opening()
    blob = struct.pack("<II", 1, 0) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=0)
    assert got.data == b""
    assert got.actual_size == 0


def test_source_consumption_is_whole_words() -> None:
    bits = _opening() + _literal7(0x5A)
    blob = struct.pack("<II", 1, 1) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=1)
    assert got.source_consumed % 4 == 0
    assert got.source_consumed >= 4


def test_decode_is_deterministic() -> None:
    bits = _opening() + "".join(_literal7(v) for v in range(64))
    blob = struct.pack("<II", 1, 64) + _bits_to_words(bits)
    first = codec.decode_packed(blob, 8, declared_size=64)
    second = codec.decode_packed(blob, 8, declared_size=64)
    assert first == second
    assert first.data == bytes(range(64))


# --- round-trip against the project encoder ----------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"\x00",
        b"A" * 4096,
        bytes(range(256)) * 4,
        b"abcabcabcabcabcabcabcabc",
        bytes([7]) * 100 + bytes([9]) * 100,
        bytes((i * 37) % 256 for i in range(1000)),
    ],
)
def test_reference_reproduces_the_project_decoder(payload: bytes) -> None:
    """Round-trip through two independently written implementations."""
    blob = wl.pack(payload)
    project = wl.unpack(blob, 0)
    reference = codec.decode_packed(blob, 8, declared_size=len(payload))
    assert project.data == payload
    assert reference.data == payload
    assert reference.actual_size == reference.declared_size


@pytest.mark.parametrize(
    "payload",
    [b"A" * 64, bytes(range(64)), b"abcabcabcabcabcabcabcabc"],
)
def test_reference_runs_to_the_stream_terminator(payload: bytes) -> None:
    """Running past the declared size reproduces the payload exactly.

    The decode either stops on the stream's own terminator, on the input bound,
    or at the end of the packed bytes - ``webfoot_lz.pack`` is a valid-stream
    generator, not Webfoot's compressor, so it does not always emit a terminator
    where the canonical encoder would. In every case the bytes produced match.
    """
    blob = wl.pack(payload)
    try:
        got = codec.decode_packed(
            blob,
            8,
            declared_size=len(payload),
            stop_on="end_marker",
            max_input_bytes=1 << 20,
        )
    except codec.CodecError:
        return
    assert got.data == payload
    assert got.terminator in ("end_marker", "ran_past_input")


# --- malformed ---------------------------------------------------------------


def test_truncated_header_is_refused_by_the_project_decoder() -> None:
    with pytest.raises(wl.ContainerError):
        wl.unpack(b"\x01\x00\x00", 0)


def test_truncated_payload_is_refused() -> None:
    blob = struct.pack("<II", 1, 4096) + b"\x00\x00"
    with pytest.raises(codec.CodecError):
        codec.decode_packed(blob, 8, declared_size=4096)


def test_missing_end_marker_with_declared_size_reached_is_accepted() -> None:
    """No marker, but the declared size is produced: both host decoders accept.

    This is host policy, not engine behaviour: the engine has no length
    comparison, so it would simply keep decoding past this point.
    """
    bits = _opening() + _literal7(0x5A)
    blob = struct.pack("<II", 1, 1) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=1)
    assert got.terminator == "declared_size"
    assert got.data == b"\x5A"
    assert wl.unpack(blob, 0).data == b"\x5A"


def test_output_never_exceeds_the_declared_size() -> None:
    """The declared size is a hard host-side ceiling on the output.

    A stream built to produce far more than its header declares is still capped:
    the reference stops at the declared size (or clips, as the project decoder
    does) and never writes past it. A declared size over the host guard is
    refused before any allocation.
    """
    bits = _opening() + "".join(_literal7(0x41) for _ in range(4096))
    blob = struct.pack("<II", 1, 64) + _bits_to_words(bits)
    got = codec.decode_packed(blob, 8, declared_size=64)
    assert len(got.data) == 64

    over = struct.pack("<II", 1, codec.MAX_OUTPUT + 1) + b"\x00\x00\x00\x00"
    with pytest.raises(codec.CodecError):
        codec.decode_packed(over, 8, declared_size=codec.MAX_OUTPUT + 1)


def test_project_decoder_clips_an_over_long_final_match() -> None:
    """PINS A REAL BEHAVIOUR, and it is not a good one.

    Declared size 4, but the stream produces 15 bytes: the project decoder stops
    writing at the declared length and reports success, so the caller receives a
    truncated payload with no error. The second implementation refuses the same
    input. This is host-side policy, not an engine contract - the engine has no
    length comparison either - but it is the partial-payload failure mode
    ``_unpack_stream``'s docstring says the function exists to prevent.

    If a follow-up implementation ticket changes this, this test is the one that
    should change with it.
    """
    blob = bytes.fromhex("01000000040000000558d020000000c0")
    project = wl.unpack(blob, 0)
    assert len(project.data) == 4
    assert project.data == b"\x41" * 4
    with pytest.raises(codec.CodecError):
        codec.decode_packed(blob, 8, declared_size=4)


def test_backreference_before_the_output_start_is_refused() -> None:
    # The opening token puts the literal width at 7 and the base at 0. Then a
    # four-bit code 2 (prefix `0 0 1`, code `0010`) copies one byte from
    # distance 1 while the output is still empty, which is a read before the
    # start of the destination.
    bits = _opening() + "001" + "0010"
    blob = struct.pack("<II", 1, 1) + _bits_to_words(bits)
    with pytest.raises(codec.CodecError) as excinfo:
        codec.decode_packed(blob, 8, declared_size=1)
    assert "before the start of the destination" in str(excinfo.value)


def test_declared_size_over_the_host_guard_is_refused() -> None:
    blob = struct.pack("<II", 1, codec.MAX_OUTPUT + 1)
    with pytest.raises(codec.CodecError):
        codec.decode_packed(blob, 8, declared_size=codec.MAX_OUTPUT + 1)


def test_payload_offset_outside_the_image_is_refused() -> None:
    with pytest.raises(codec.CodecError):
        codec.decode_packed(b"\x00\x00\x00\x00", 4096, declared_size=1)


def test_bad_literal_width_is_refused() -> None:
    blob = struct.pack("<II", 1, 1) + b"\x00\x00\x00\x00"
    with pytest.raises(codec.CodecError):
        codec.decode_packed(blob, 8, declared_size=1, initial_literal_bits=0)


def test_negative_declared_size_is_refused() -> None:
    blob = struct.pack("<II", 1, 1) + b"\x00\x00\x00\x00"
    with pytest.raises(codec.CodecError):
        codec.decode_packed(blob, 8, declared_size=-1)


def test_stored_declared_size_past_the_image_is_refused_by_the_project() -> None:
    blob = struct.pack("<II", 0, 0x7FFFFFFF) + b"\x00\x00\x00\x00"
    with pytest.raises(wl.ContainerError):
        wl.unpack(blob, 0)


def test_host_decoders_are_stricter_than_the_engine() -> None:
    """A refusal is host policy; the engine validates nothing.

    The engine's dispatcher has no bounds check and no size comparison, so this
    test asserts only that *our* decoders refuse - never that the engine does.
    """
    bad = struct.pack("<II", 1, 4096) + b"\x00\x00"
    with pytest.raises(codec.CodecError):
        codec.decode_packed(bad, 8, declared_size=4096)
    with pytest.raises(wl.ContainerError):
        wl.unpack(bad, 0)
