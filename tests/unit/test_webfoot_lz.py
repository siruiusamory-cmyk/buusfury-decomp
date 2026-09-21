"""Portable tests for the Webfoot container codec (TOOLKIT-010).

Every fixture here is synthetic. The ROM's own containers are exercised by
`tests/integration/test_graphics_rom.py`, which skips when the image is absent;
nothing ROM-derived is committed.

The pairing that matters: `pack` is checked by `unpack`, never against captured
bytes. That is the only claim the encoder makes - it emits a stream the verified
decoder accepts - and testing it against a golden blob would assert a stronger
property than the module is willing to state.

**Strict success (EVIDENCE-RISK-DEBT-001).** The decoder used to stop appending
when a match reached the declared size, so a stream whose final match overran was
clipped and reported as a success. The `_refuses_*` tests below are the negative
proof: a match that would pass the declared size, a stream that stops short, a
truncated stream in each of its three parts, and an impossible back-reference are
each refused. The `_accepts_*` pair next to the overrun case pins where the
boundary now sits - exactly the declared size, and not one byte more.
"""

from __future__ import annotations

import struct

import pytest

from tools.webfoot.formats import webfoot_lz as wl


# --- synthetic stream construction -------------------------------------------
#
# These builders emit the exact token sequences the format defines, so a refusal
# test says *why* the stream is malformed instead of presenting a magic blob.

def _header(kind: int, declared: int) -> bytes:
    return struct.pack("<II", kind, declared)


def _widen_to_eight_bit_literals(writer: "wl._WordBitWriter") -> None:
    """The control escape `pack` opens with: 8-bit literals, no base byte.

    Prefix ``0 0 1`` reaches the four-bit code, a zero field makes it -1, and the
    final ``0 1`` selects ``literal_bits = 7 + 1`` with nothing to read.
    """
    writer.bit(0)
    writer.bit(0)
    writer.bit(1)
    writer.put(0, 4)
    writer.bit(0)
    writer.bit(1)


def _literal(writer: "wl._WordBitWriter", value: int) -> None:
    writer.bit(1)
    writer.put(value, 8)


def _previous_distance_match(writer: "wl._WordBitWriter", count: int) -> None:
    """``0 1`` then distance code 2: re-use the previous distance.

    The decoder starts with ``previous_distance = 1`` and adds no length bias on
    this path, so this is the shortest way to write a match of an exact length
    without first building a 128-byte window.
    """
    writer.bit(0)
    writer.bit(1)
    writer.gamma(2)
    writer.gamma(count)


def _long_match_at_distance_zero(writer: "wl._WordBitWriter", count: int) -> None:
    """``0 1`` long match whose distance field is zero, which is not a distance."""
    writer.bit(0)
    writer.bit(1)
    writer.gamma(3)
    writer.put(0, 8)
    writer.gamma(count)


def _end_marker(writer: "wl._WordBitWriter") -> None:
    """``0 0 0`` then a zero seven-bit field and a zero two-bit width."""
    writer.bit(0)
    writer.bit(0)
    writer.bit(0)
    writer.put(0, 7)
    writer.put(0, 2)


def _raw_literal_run(writer: "wl._WordBitWriter", values: list[int]) -> None:
    """A run of raw 8-bit literals, ended by a clear continuation bit.

    Prefix ``0 0 1`` reaches the four-bit code; a zero field makes it -1, and the
    following set bit selects the run. The decoder then reads the literals two at
    a time, each pair followed by a continuation bit, so ``values`` must have even
    length.
    """
    assert values and len(values) % 2 == 0, "a raw run is read in pairs"
    writer.bit(0)
    writer.bit(0)
    writer.bit(1)
    writer.put(0, 4)
    writer.bit(1)
    for index in range(0, len(values), 2):
        writer.put(values[index], 8)
        writer.put(values[index + 1], 8)
        writer.bit(0 if index + 2 >= len(values) else 1)


def _container(kind: int, declared: int, build) -> bytes:
    writer = wl._WordBitWriter()
    build(writer)
    return _header(kind, declared) + writer.finish()


def test_stored_container_round_trips_verbatim() -> None:
    payload = bytes(range(256))
    blob = wl.build_stored(payload)
    container = wl.unpack(blob, 0)
    assert container.kind == wl.STORED
    assert container.data == payload
    assert container.declared_size == len(payload)
    assert container.packed_end == wl.HEADER_SIZE + len(payload)


def test_headerless_stream_with_eight_bit_literals() -> None:
    # Three literal tokens: prefix 1 followed by each 8-bit byte, padded to a
    # little-endian 32-bit bit word.
    bits = "".join("1" + f"{value:08b}" for value in b"MAP").ljust(32, "0")
    stream = struct.pack("<I", int(bits, 2))
    assert wl.unpack_raw_stream(stream, 0, 3) == b"MAP"


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"\x00",
        b"A" * 4096,                       # one long run
        bytes(range(256)) * 4,            # no useful matches
        b"abcabcabcabcabcabcabcabc",      # short repeating period
        bytes([7]) * 100 + bytes([9]) * 100,
        bytes((i * 37) % 256 for i in range(1000)),
    ],
)
def test_pack_output_decodes_back_to_the_input(payload: bytes) -> None:
    """The encoder's whole contract: the verified decoder reads it back exactly."""
    blob = wl.pack(payload)
    assert wl.unpack(blob, 0).data == payload


def test_pack_is_deterministic() -> None:
    """Same input, same bytes - what makes a project build reproducible."""
    payload = bytes((i * 11) % 251 for i in range(600))
    assert wl.pack(payload) == wl.pack(payload)


def test_pack_declares_a_packed_kind_the_decoder_recognises() -> None:
    blob = wl.pack(b"hello hello hello")
    kind, declared = wl.read_header(blob, 0)
    assert kind in wl.PACKED_KINDS
    assert declared == len(b"hello hello hello")


def test_packed_extent_is_measured_not_declared() -> None:
    """`packed_end` must come from decoding, since no header field carries it."""
    payload = b"repeat " * 40
    blob = wl.pack(payload)
    container = wl.unpack(blob + b"\xAA" * 64, 0)
    assert container.packed_size <= len(blob)
    assert container.data == payload


def test_header_outside_the_image_is_refused() -> None:
    with pytest.raises(wl.ContainerError, match="outside the image"):
        wl.read_header(b"\x00" * 4, 0)


def test_unsupported_kind_is_refused_by_name() -> None:
    blob = struct.pack("<II", 9, 4) + b"data"
    with pytest.raises(wl.ContainerError, match="unsupported Webfoot container kind 9"):
        wl.unpack(blob, 0)


def test_declared_size_over_the_safety_limit_is_refused_before_allocating() -> None:
    blob = struct.pack("<II", 0, 1 << 30)
    with pytest.raises(wl.ContainerError, match="safety limit"):
        wl.unpack(blob, 0)


def test_stored_container_running_past_the_image_is_refused() -> None:
    blob = struct.pack("<II", 0, 64) + b"short"
    with pytest.raises(wl.ContainerError, match="runs past the image"):
        wl.unpack(blob, 0)


def test_truncated_packed_stream_is_refused() -> None:
    """A stream that ends mid-word must raise, never return partial pixels.

    The payload is deliberately incompressible. A long run packs into a handful
    of words, so truncating it would land *past* a stream that had already
    finished and the decoder would rightly not complain - the test would pass
    for the wrong reason.
    """
    payload = bytes((i * 179 + (i * i) % 251) % 256 for i in range(512))
    blob = wl.pack(payload)
    assert len(blob) > wl.HEADER_SIZE + 16
    with pytest.raises(wl.ContainerError):
        wl.unpack(blob[: wl.HEADER_SIZE + 8], 0)


def test_back_reference_before_the_output_start_is_refused() -> None:
    """A distance larger than the output so far is corruption, not a wrap-around."""
    # Hand-built: literal-width escape, then a long match at distance 0x0100
    # before any byte has been emitted.
    writer = wl._WordBitWriter()
    for bit in (0, 0, 1):
        writer.bit(bit)
    writer.put(0, 4)
    writer.bit(0)
    writer.bit(1)
    writer.bit(0)
    writer.bit(1)
    writer.gamma(4)          # distance code -> (4 - 3) << 8 = 0x100
    writer.put(0, 8)
    writer.gamma(2)
    blob = struct.pack("<II", 2, 16) + writer.finish()
    with pytest.raises(wl.ContainerError, match="outside the decoded output"):
        wl.unpack(blob, 0)


def test_looks_like_container_filters_without_deciding() -> None:
    good = wl.build_stored(b"\x01" * 64)
    assert wl.looks_like_container(good, 0, minimum_size=32, maximum_size=1024)
    # Right shape, wrong size band: the filter rejects on the caller's bounds.
    assert not wl.looks_like_container(good, 0, minimum_size=128, maximum_size=1024)
    # Off the end of the buffer.
    assert not wl.looks_like_container(good, len(good), minimum_size=1)
    # A kind the header does not define.
    assert not wl.looks_like_container(struct.pack("<II", 5, 8), 0)


def test_gamma_encoder_and_decoder_agree_over_a_wide_range() -> None:
    """The one piece of the grammar with no obvious inverse; check it directly."""
    for value in list(range(2, 300)) + [1000, 4095, 65535]:
        writer = wl._WordBitWriter()
        writer.gamma(value)
        reader = wl._WordBitReader(writer.finish(), 0)
        assert wl._gamma(reader) == value


def test_gamma_cannot_encode_below_two() -> None:
    writer = wl._WordBitWriter()
    with pytest.raises(wl.ContainerError):
        writer.gamma(1)


# --- strict success: exact declared size, no clipping -------------------------
#
#: The canonical reproduction of the clipping defect, quoted from
#: `docs/research/LOGX_SYNTHESIS.md` §11.1: packed form 1, declared 4, whose final
#: match produces 15 bytes. The old decoder clipped it to 4 and returned success.
CLIPPING_REPRODUCTION = bytes.fromhex("01000000040000000558d020000000c0")


def test_the_over_long_final_match_reproduction_is_refused() -> None:
    """The defect this ticket fixed, pinned as a refusal."""
    with pytest.raises(wl.ContainerError, match="declared 4"):
        wl.unpack(CLIPPING_REPRODUCTION, 0)


def test_a_one_byte_overrun_is_refused_and_the_exact_size_is_accepted() -> None:
    """The boundary sits exactly at the declared size.

    ``A`` then a two-byte match on the initial previous-distance of 1 produces
    three bytes. Declared as three it is a valid stream; declared as two the same
    token stream is malformed and must be refused rather than clipped to ``AA``.
    """
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, ord("A"))
        _previous_distance_match(writer, 2)

    accepted = _container(1, 3, build)
    assert wl.unpack(accepted, 0).data == b"AAA"

    refused = _container(1, 2, build)
    with pytest.raises(wl.ContainerError, match="would produce 3 bytes against a declared 2"):
        wl.unpack(refused, 0)


def test_a_larger_match_overrun_is_refused() -> None:
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        for value in b"ABCD":
            _literal(writer, value)
        _previous_distance_match(writer, 64)

    with pytest.raises(wl.ContainerError, match="would produce 68 bytes against a declared 6"):
        wl.unpack(_container(2, 6, build), 0)
    # The same stream is accepted at the size it really produces.
    assert wl.unpack(_container(2, 68, build), 0).data == b"ABCD" + bytes([ord("D")] * 64)


@pytest.mark.parametrize("kind", wl.PACKED_KINDS)
def test_both_packed_forms_enforce_the_declared_size(kind: int) -> None:
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, 0x5A)
        _previous_distance_match(writer, 4)

    assert wl.unpack(_container(kind, 5, build), 0).data == bytes([0x5A] * 5)
    with pytest.raises(wl.ContainerError):
        wl.unpack(_container(kind, 4, build), 0)


@pytest.mark.parametrize("kind", wl.PACKED_KINDS)
def test_a_raw_literal_run_that_fills_the_declared_size_exactly_is_accepted(
    kind: int,
) -> None:
    """The other clip path, in its valid form: a run that lands on the size."""
    def build(writer: "wl._WordBitWriter") -> None:
        _raw_literal_run(writer, [0x58, 0xAC])

    container = wl.unpack(_container(kind, 2, build), 0)
    assert container.data == b"X\xac"


@pytest.mark.parametrize("kind", wl.PACKED_KINDS)
def test_a_raw_literal_run_that_would_overrun_the_declared_size_is_refused(
    kind: int,
) -> None:
    """The second silent-clip path, found by an independent review.

    ``copy_match`` was repaired first; the raw-literal-run branch still stopped
    appending once the output reached the declared size, so the same token stream
    was *accepted* as ``b'X\\xac\\xad'`` with the run's fourth literal dropped,
    while ``tools.export.webfoot_strict`` refused it. The run carries its own
    terminator, so the stream is malformed and must be refused.
    """
    def build(writer: "wl._WordBitWriter") -> None:
        _raw_literal_run(writer, [0x58, 0xAC, 0xAD, 0x41])

    assert wl.unpack(_container(kind, 4, build), 0).data == b"X\xac\xadA"
    with pytest.raises(
        wl.ContainerError, match="raw literal run at output offset 3 overruns"
    ):
        wl.unpack(_container(kind, 3, build), 0)
    with pytest.raises(
        wl.ContainerError, match="raw literal run at output offset 1 overruns"
    ):
        wl.unpack(_container(kind, 1, build), 0)


def test_a_raw_literal_run_that_continues_past_the_declared_size_is_refused() -> None:
    """A clear continuation bit means more literals follow; there is no room.

    The old rule short-circuited on the size and never read that bit, so a run
    that explicitly declared another pair past the declared size was accepted.
    """
    def build(writer: "wl._WordBitWriter") -> None:
        _raw_literal_run(writer, [0x58, 0xAC, 0xAD, 0x41])

    with pytest.raises(wl.ContainerError, match="overruns the declared 2"):
        wl.unpack(_container(1, 2, build), 0)


def test_the_removed_run_clip_would_still_be_visible_if_it_came_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A discriminating control for the refusal above.

    ``_emit_raw`` is restored to the pre-fix behaviour - stop appending once the
    output reaches the declared size - and the same malformed stream must be
    *accepted* again. Without this, the corpus-wide "no container needed the clip"
    assertion could pass because the rule never fires rather than because no
    container needs it.
    """
    def build(writer: "wl._WordBitWriter") -> None:
        _raw_literal_run(writer, [0x58, 0xAC, 0xAD, 0x41])

    blob = _container(1, 3, build)
    with pytest.raises(wl.ContainerError, match="overruns the declared 3"):
        wl.unpack(blob, 0)

    def clipping(out: bytearray, value: int, expected: int) -> None:
        if len(out) >= expected:
            return                      # the removed behaviour: drop the surplus
        out.append(value)

    monkeypatch.setattr(wl, "_emit_raw", clipping)
    assert wl.unpack(blob, 0).data == b"X\xac\xad"


def test_output_underflow_is_refused() -> None:
    """A terminating stream is not a success when it stops short of the header."""
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, 0x11)
        _literal(writer, 0x22)
        _end_marker(writer)

    assert wl.unpack(_container(1, 2, build), 0).data == b"\x11\x22"
    with pytest.raises(wl.ContainerError, match="decoded 2 bytes against a declared 4"):
        wl.unpack(_container(1, 4, build), 0)


def test_truncated_control_data_is_refused() -> None:
    """No payload word at all: the first control bit cannot be read."""
    with pytest.raises(wl.ContainerError, match="ended inside a bit word"):
        wl.unpack(_header(1, 4), 0)


def test_truncated_literal_data_is_refused() -> None:
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        for index in range(24):
            _literal(writer, (index * 37) % 256)

    blob = _container(1, 24, build)
    assert wl.unpack(blob, 0).declared_size == 24
    # One word of payload cannot hold 24 nine-bit literals.
    with pytest.raises(wl.ContainerError, match="ended inside a bit word"):
        wl.unpack(blob[: wl.HEADER_SIZE + 4], 0)


def test_truncated_match_data_is_refused() -> None:
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        for value in b"AB":
            _literal(writer, value)
        _previous_distance_match(writer, 8)

    blob = _container(1, 10, build)
    assert wl.unpack(blob, 0).data == b"AB" + b"B" * 8
    with pytest.raises(wl.ContainerError, match="ended inside a bit word"):
        wl.unpack(blob[: wl.HEADER_SIZE + 4], 0)


def test_truncated_input_is_refused_rather_than_partially_decoded() -> None:
    """Whatever the truncation removes, the result is a refusal, never short output."""
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        for index in range(64):
            _literal(writer, index)

    blob = _container(1, 64, build)
    for length in range(wl.HEADER_SIZE, len(blob)):
        with pytest.raises(wl.ContainerError):
            wl.unpack(blob[:length], 0)


def test_a_zero_distance_is_refused() -> None:
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, 0x33)
        _long_match_at_distance_zero(writer, 2)

    with pytest.raises(wl.ContainerError, match="distance 0"):
        wl.unpack(_container(1, 4, build), 0)


def test_an_unreachable_distance_is_refused() -> None:
    """A match cannot reference a byte the output has not produced yet."""
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, 0x33)
        # A long match at distance 0x40 with only one byte of output so far.
        writer.bit(0)
        writer.bit(1)
        writer.gamma(3)
        writer.put(0x40, 8)
        writer.gamma(2)

    with pytest.raises(wl.ContainerError, match="points outside the decoded output"):
        wl.unpack(_container(1, 66, build), 0)


def test_a_stream_that_stops_at_its_declared_size_is_still_accepted() -> None:
    """The engine's own rule, kept: reaching the declared size ends the decode.

    The stream past that point is not examined, which is what makes
    `webfoot_lz.pack`'s output - which never emits an end marker - decodable.
    """
    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        for value in b"MAP":
            _literal(writer, value)
        # Trailing tokens the decoder must not have to understand.
        _literal(writer, 0xFF)

    blob = _container(1, 3, build)
    assert wl.unpack(blob, 0).data == b"MAP"


@pytest.mark.parametrize("size", (1, 2, 3, 7, 64, 300, 4096))
def test_pack_output_still_decodes_exactly_after_the_strictness_change(size: int) -> None:
    """Valid-stream parity: the encoder's whole contract, unchanged."""
    payload = bytes((index * 29 + size) % 256 for index in range(size))
    encoded = wl.pack(payload)
    container = wl.unpack(encoded, 0)
    assert container.data == payload
    assert container.declared_size == size
    assert len(container.data) == size
