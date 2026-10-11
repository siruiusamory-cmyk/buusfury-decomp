"""Portable tests for the Webfoot container codec (TOOLKIT-010).

Every fixture here is synthetic. The ROM's own containers are exercised by
`tests/integration/test_graphics_rom.py`, which skips when the image is absent;
nothing ROM-derived is committed.

The pairing that matters: `pack` is checked by `unpack`, never against captured
bytes. That is the only claim the encoder makes - it emits a stream the verified
decoder accepts - and testing it against a golden blob would assert a stronger
property than the module is willing to state. The single frozen blob in this file
is the opposite kind of fixture: the pre-fix encoding of a known payload, kept as
the *negative* half of the CQA-02 termination regression so the discriminator can
never silently become vacuous.

**Stream termination (CQA-02-PACKED-STREAM-TERMINATION-001).** The retail decoder
has no output counter and stops only on the stream's own escape - twelve zero bits
at a token boundary. `pack` writes that escape before the final word is padded, and
`validate_retail_termination` re-decodes a payload to the escape and requires it at
exactly the declared length. The `_marker_` and `_retail_termination_` tests below
pin the marker's exact bits, its position, the corpus-wide postcondition, and the
pre-fix streams that must still be refused.

**Strict success (EVIDENCE-RISK-DEBT-001).** The decoder used to stop appending
when a match reached the declared size, so a stream whose final match overran was
clipped and reported as a success. The `_refuses_*` tests below are the negative
proof: a match that would pass the declared size, a stream that stops short, a
truncated stream in each of its three parts, and an impossible back-reference are
each refused. The `_accepts_*` pair next to the overrun case pins where the
boundary now sits - exactly the declared size, and not one byte more.
"""

from __future__ import annotations

import hashlib
import random
import struct
import time

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
        assert wl._gamma(reader, wl._GAMMA_LIMIT) == value


def test_gamma_cannot_encode_below_two() -> None:
    writer = wl._WordBitWriter()
    with pytest.raises(wl.ContainerError):
        writer.gamma(1)


# --- bounded consumption (CQA-19-BOUNDED-GAMMA-001) ---------------------------
#
# `_gamma` is a `while True` loop that shifts its accumulator left once per
# iteration, so a malformed stream's cost is quadratic in the bits it consumes,
# and those bits come from the whole image rather than from the container. Two
# bounds close it: `_gamma` itself refuses an accumulator past the ceiling its
# caller derives from the output bound it declared, and the decode loop now applies
# its input-consumption limit in both modes instead of only under `require_end_marker`.

#: Packed input the unbounded-gamma reproduction carries. Before the fix, a
#: quarter of this (256 KiB) was directly measured on this machine at 19.9 s and
#: it is refused after the fix in tens of microseconds. The budget sits between
#: the two by five orders of magnitude, so it cannot be flaky on load.
_UNBOUNDED_GAMMA_FILL = 1024 * 1024
_UNBOUNDED_GAMMA_BUDGET = 1.0


def _unbounded_gamma_stream(fill_bytes: int) -> bytes:
    """A stream whose opening match token cannot be read.

    The opening word is the long-match prefix ``0 1`` followed by all set bits, and
    every following word is ``0xFF``, so every bit the gamma loops read is a one:
    both the payload bit and the continuation bit stay set, so a gamma field cannot
    return and cannot stop shifting its accumulator. That is the malformed shape the
    recon measured, and it is what drives the quadratic cost.
    """
    first = "0" "1" "1" "1" "0" + "1" * 27
    assert len(first) == 32
    return (
        struct.pack("<II", 1, wl.DEFAULT_MAX_OUTPUT)
        + struct.pack("<I", int(first, 2))
        + b"\xff" * fill_bytes
    )


def test_a_malformed_gamma_cannot_walk_the_whole_image() -> None:
    """Before the fix this ran for seconds and never refused on its own bound.

    The honest pre-fix behaviour was not a token-level assertion failure: the decode
    ran for 19.9 s over 256 KiB of this shape, consuming the image whole, and only
    stopped when the bit reader ran out of words - ``packed stream ended inside a bit
    word``. Both decoders refuse the stream, on different grounds, so what
    distinguishes the fix is not the refusal but refusing immediately instead of
    after walking the image. This asserts elapsed time against a budget five orders
    of magnitude above the fixed cost, which is what makes the before-fix run a
    failure rather than a hang. Reverted to the pre-fix ``_gamma``, the measured
    cost of the shape used here scales faster than the input, and this test fails on
    the budget.

    The premise is synthetic and read-only: the buffer is not a ROM and nothing here
    is ROM-derived.
    """
    blob = _unbounded_gamma_stream(_UNBOUNDED_GAMMA_FILL)
    started = time.perf_counter()
    with pytest.raises(wl.ContainerError, match="gamma value reached"):
        wl.unpack(blob, 0)
    elapsed = time.perf_counter() - started
    assert elapsed < _UNBOUNDED_GAMMA_BUDGET, (
        f"the malformed stream took {elapsed:.3f}s for {len(blob)} input bytes, "
        f"over the {_UNBOUNDED_GAMMA_BUDGET}s budget"
    )


def test_the_gamma_bound_cannot_fire_on_a_valid_corpus(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The ceiling is above every value a default-bounded stream carries, measured.

    The corpus is the one this file already round-trips
    (:func:`_termination_corpus`), replayed here with every gamma value the decode
    actually produces recorded, so the ceiling is checked against measurement
    rather than against the derivation alone. Every payload here declares a size
    within the default bound, whose derived ceiling is `_GAMMA_LIMIT`, so a corpus
    value above it fails here before the decoder ever refuses one; the per-call
    derivation itself is pinned by the tests that follow.
    """
    largest = 0
    real_gamma = wl._gamma

    def recording_gamma(reader, minimum):
        nonlocal largest
        value = real_gamma(reader, minimum)
        largest = max(largest, value)
        return value

    monkeypatch.setattr(wl, "_gamma", recording_gamma)
    cases = _termination_corpus()
    assert len(cases) >= 35
    for name, payload in cases:
        encoded = wl.pack(payload)
        assert wl.unpack(encoded, 0).data == payload, f"A: {name}"
        assert wl.validate_retail_termination(encoded).data == payload, f"B: {name}"
    assert 0 < largest < wl._GAMMA_LIMIT, f"largest corpus gamma value: {largest}"


# --- the ceiling follows the call's own bound ---------------------------------
#
# `_GAMMA_LIMIT` is derived from the 64 KiB default output bound and the 16-bit
# distance window, but `maximum_output` is a parameter of the decode entry points.
# A caller that declares a larger output can carry a legitimately larger gamma
# field, and one that declares a smaller output deserves a ceiling no looser than
# its own bound, so the ceiling is derived per call from the bound that call
# declared. CQA-19-GAMMA-CEILING-DERIVATION-001.


def test_a_match_length_above_the_default_ceiling_decodes_when_the_call_declares_it() -> None:
    """The correctness half: a larger declared bound admits a larger field.

    One literal, then a match of ``2**17`` bytes at the decoder's initial
    previous-distance of 1, declared as the ``2**17 + 1`` bytes it really produces
    and decoded with ``maximum_output`` raised to that. ``2**17`` was the fixed
    ceiling, and this match is legitimate for a caller whose own limit is above the
    64 KiB default, so a decode that judges the field against that fixed value
    refuses a valid stream. This is the test that fails on the pre-derivation module.
    """
    length = 1 << 17

    def build(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, 0x00)
        _previous_distance_match(writer, length)

    expected = 1 + length
    blob = _container(1, expected, build)
    assert wl.unpack(blob, 0, maximum_output=expected).data == b"\x00" * expected


def test_the_gamma_ceiling_is_derived_from_the_declared_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The tie half: the ceiling handed to `_gamma` moves with the caller's bound.

    One container is decoded twice under two different `maximum_output` declarations,
    with every ceiling the decode passes recorded. A ceiling that does not track the
    call's own bound is the same number for both, which the final assertion refuses;
    a ceiling derived from something other than that bound - or a fixed constant -
    leaves the declared limit behind, which the per-call bounds refuse. Each ceiling
    must clear the bound, because a distance code carries its distance plus three and
    a distance can be the whole output produced so far, and must stay within a few
    bytes of it, because the derivation adds that token's own offset rather than a
    separate scale.
    """
    seen: list[int] = []
    real_gamma = wl._gamma

    def recording_gamma(reader, minimum):
        seen.append(minimum)
        return real_gamma(reader, minimum)

    monkeypatch.setattr(wl, "_gamma", recording_gamma)

    def ceilings(maximum_output: int) -> tuple[int, list[int]]:
        def build(writer: "wl._WordBitWriter") -> None:
            _widen_to_eight_bit_literals(writer)
            _literal(writer, 0x00)
            _previous_distance_match(writer, 4)

        seen.clear()
        assert wl.unpack(
            _container(1, 5, build), 0, maximum_output=maximum_output
        ).declared_size == 5
        return maximum_output, list(seen)

    small_bound, small = ceilings(64)
    large_bound, large = ceilings(4096)
    assert small and large, "both decodes must gamma-read at least one field"
    for bound, minima in ((small_bound, small), (large_bound, large)):
        for minimum in minima:
            assert bound < minimum <= bound + 8, (
                f"a call bounded at {bound} bytes passed the ceiling {minimum}"
            )
    assert small != large, (
        f"the ceiling did not move with the declared bound: {small} for "
        f"{small_bound}, {large} for {large_bound}"
    )


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
    """Host policy, kept: reaching the declared size ends the default decode.

    The stream past that point is not examined. This is the host-side rule and
    deliberately NOT the engine's - the retail decoder carries no output counter
    and would keep reading - so this test describes what `unpack` does by default,
    not what the write path accepts. `validate_retail_termination` is the check
    that speaks for the engine.
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


# --- stream termination: the retail escape (CQA-02) ---------------------------
#
# The retail packed decoder takes `(source, destination)`, keeps no output count
# and compares nothing against its destination cursor, so it stops only on the
# stream's own escape: twelve zero bits - prefix `000`, seven-bit field `0000000`,
# two-bit selector `00` - read where a token would begin. `pack` emits that escape
# itself, before the final word is padded, and `validate_retail_termination`
# re-decodes to the escape and requires it at exactly the declared length.

#: `pack(b"A" * 64)` **before** CQA-02-PACKED-STREAM-TERMINATION-001, byte for
#: byte, from the ticket's own pre-fix worktree (`git show 659db0e:...`). Its
#: final token ends flush on the 32-bit boundary, so it emits exactly zero padding
#: bits and its packed stream contains no escape at all - the case the audit
#: described as "only appears valid because of what happens to follow it". Frozen
#: here so the discriminator below cannot decay into a test that passes for the
#: wrong reason.
_A_TIMES_64_BEFORE_CQA_02 = bytes.fromhex("0200000040000000fe53d020")

#: The same payload after remediation: the identical token stream, then the
#: escape. Because the pre-fix token stream ended flush, the marker begins a fresh
#: word, so the whole added word is zero.
_A_TIMES_64_AFTER_CQA_02 = bytes.fromhex("0200000040000000fe53d02000000000")


def test_the_a64_flush_payload_is_the_pinned_cqa_02_discriminator() -> None:
    """The named regression, in both directions.

    Before the fix this payload's stream ended flush against a word boundary with
    no escape, so the host decoder accepted it and the retail termination rule
    refused it. After the fix the token stream is unchanged, the escape follows it,
    and both accept. A regression that dropped the marker would make the second
    half fail on `_A_TIMES_64_BEFORE_CQA_02` and the first half fail on the
    mismatch against `_A_TIMES_64_AFTER_CQA_02`.
    """
    payload = b"A" * 64
    assert wl.pack(payload) == _A_TIMES_64_AFTER_CQA_02
    assert wl.pack(payload)[: len(_A_TIMES_64_BEFORE_CQA_02)] == _A_TIMES_64_BEFORE_CQA_02

    # Host-side rule: the pre-fix stream decodes fine, which is why the defect was
    # invisible to every caller that only decoded it.
    assert wl.unpack(_A_TIMES_64_BEFORE_CQA_02, 0).data == payload
    # Retail rule: it does not terminate inside its own bytes.
    with pytest.raises(wl.ContainerError):
        wl.validate_retail_termination(_A_TIMES_64_BEFORE_CQA_02)

    # The corrected stream satisfies both, and its escape is inside it.
    assert wl.unpack(_A_TIMES_64_AFTER_CQA_02, 0).data == payload
    assert wl.validate_retail_termination(_A_TIMES_64_AFTER_CQA_02).data == payload


def test_the_end_marker_is_twelve_zero_bits_written_at_the_token_boundary() -> None:
    """The marker's width and value, asserted at the bit level.

    Built through the module's own writer so this is a statement about bit
    positions rather than about which bytes happen to differ: the twelve bits that
    follow the final token are zero, the token bits before them are untouched, and
    the writer consumed exactly twelve more bits. Those twelve are the decoder's
    ``000`` + ``0000000`` + ``00``.
    """
    def body(writer: "wl._WordBitWriter") -> None:
        _widen_to_eight_bit_literals(writer)
        _literal(writer, 0x5A)

    counting = wl._WordBitWriter()
    body(counting)
    assert counting._count == 18
    counting.write_end_marker()
    assert counting._count == 30

    marked = wl._WordBitWriter()
    body(marked)
    marked.write_end_marker()
    bits = f"{int.from_bytes(marked.finish(), 'little'):032b}"
    tokens_only = wl._WordBitWriter()
    body(tokens_only)
    token_bits = f"{int.from_bytes(tokens_only.finish(), 'little'):032b}"
    assert bits[:18] == token_bits[:18]
    assert bits[18:30] == "0" * 12
    assert bits[30:] == "0" * 2


@pytest.mark.parametrize("flipped", range(12))
def test_altering_any_bit_of_the_marker_defeats_retail_validation(flipped: int) -> None:
    """Every one of the twelve bits is load-bearing.

    A stream whose escape differs in a single bit is still well formed enough for
    the host decoder if the declared size is reached first, but it no longer
    terminates on the engine's rule - so the stricter consumer must refuse it. This
    is the automated form of the ticket's M3 mutation, kept as a permanent test
    rather than run once by hand.
    """
    writer = wl._WordBitWriter()
    _widen_to_eight_bit_literals(writer)
    _literal(writer, 0x5A)
    for index in range(12):
        writer.bit(1 if index == flipped else 0)
    blob = _header(2, 1) + writer.finish()

    assert wl.unpack(blob, 0).data == b"\x5A"
    with pytest.raises(wl.ContainerError):
        wl.validate_retail_termination(blob)


def test_a_marker_less_stream_is_refused_however_it_is_padded() -> None:
    """Termination must be inside the payload, not borrowed from what follows it.

    The pre-fix stream is refused on its own, refused with `0xFF` expansion fill
    after it, and only "accepted" when a caller happens to append enough zero bytes
    - which is precisely the accident the fix removes. The corrected stream does not
    care what follows it.
    """
    pre_fix = _A_TIMES_64_BEFORE_CQA_02
    with pytest.raises(wl.ContainerError):
        wl.validate_retail_termination(pre_fix)
    with pytest.raises(wl.ContainerError):
        wl.validate_retail_termination(pre_fix + b"\xFF" * 64)
    # A run of zero bytes supplies the missing bits - the pre-fix stream's success
    # was conditional on its neighbours, which is the defect.
    assert wl.validate_retail_termination(pre_fix + b"\x00" * 4).data == b"A" * 64

    fixed = _A_TIMES_64_AFTER_CQA_02
    for tail in (b"", b"\xFF" * 64, b"\x00" * 64, bytes(range(64))):
        assert wl.validate_retail_termination(fixed + tail).data == b"A" * 64


def _termination_corpus() -> list[tuple[str, bytes]]:
    """Deterministic payloads covering the alignment and content cases that matter.

    Names are carried so a failure says which shape broke. Every payload is
    synthetic; nothing here is ROM-derived.
    """
    rng = random.Random(20260924)
    cases: list[tuple[str, bytes]] = [
        ("empty", b""),
        ("one-byte", b"\x41"),
        ("two-byte", b"\x41\x41"),
        ("shortest-repeating", b"\x41\x41\x41"),
        ("all-zero-3", b"\x00" * 3),
        ("repeat-255", b"\xFF" * 255),
        ("repeat-256", b"\x00" * 256),
        ("repeat-4096", b"A" * 4096),
        ("alternating-256", (b"\xAA\x55" * 128)),
        ("pattern-1024", (bytes(range(16)) * 64)),
        ("incompressible-256", bytes(rng.randrange(256) for _ in range(256))),
        ("incompressible-4096", bytes(rng.randrange(256) for _ in range(4096))),
        ("ramp-1000", bytes((index * 37) % 256 for index in range(1000))),
    ]
    # Powers of two, and the 31/32/33-style boundaries where the final token is most
    # likely to land flush against a word (the pre-fix defect's case).
    for size in (4, 8, 16, 32, 64, 128, 512, 1024):
        cases.append((f"incompressible-{size}", bytes(rng.randrange(256) for _ in range(size))))
    for size in (15, 30, 31, 32, 33, 62, 63, 64, 65, 127, 128, 129):
        cases.append((f"repeat-{size}", b"Q" * size))
        cases.append((f"incompressible-{size}", bytes(rng.randrange(256) for _ in range(size))))
    return cases


def test_every_packed_payload_is_self_terminating() -> None:
    """The universal postcondition, over a generated corpus.

    For every supported input:

    * A - the ordinary host decode returns the source exactly;
    * B - the retail termination validator accepts;
    * C - the escape falls at the declared decompressed boundary, which is what the
      validator requires;
    * D - no *earlier* boundary escape exists. This follows from the validator's
      own construction rather than from a second scan: it consumes tokens in order
      and stops at the first escape, so an earlier one would end the decode short
      and fail the length comparison. `tests/unit/test_logx_codec_reference.py`
      corroborates it with an independently written reader;
    * E - the payload terminates on its own. The validator is run on the payload
      with nothing after it, so no following byte can be supplying the escape.
    """
    cases = _termination_corpus()
    assert len(cases) >= 35
    for name, payload in cases:
        encoded = wl.pack(payload)
        assert wl.unpack(encoded, 0).data == payload, f"A: {name}"
        verified = wl.validate_retail_termination(encoded)
        assert verified.data == payload, f"B: {name}"
        assert verified.declared_size == len(payload), f"C: {name}"
        # The whole payload is whole words, header included: nothing here leans on
        # a byte outside the encoded stream.
        assert (len(encoded) - wl.HEADER_SIZE) % 4 == 0, f"E: {name}"


def test_a_payload_whose_packed_form_exceeds_64kib_still_validates() -> None:
    """The escape scan is bounded by the declared size, not by a fixed ceiling.

    A legitimate packed stream can be larger than the bytes it produces - this
    encoder's literal-only worst case is nine bits per byte - so a fixed ceiling
    around 64 KiB refuses a valid incompressible payload near the top of the
    supported range. That was a real false refusal while the bound was a constant,
    and this case pins it.
    """
    payload = b"".join(
        hashlib.sha256(index.to_bytes(4, "little")).digest()
        for index in range(60 * 1024 // 32)
    )
    encoded = wl.pack(payload)
    assert len(encoded) - wl.HEADER_SIZE > 64 * 1024, "premise: packed over 64 KiB"
    assert wl.validate_retail_termination(encoded).data == payload


def test_the_marker_costs_nothing_or_one_packed_word_and_never_more(monkeypatch) -> None:
    """Marker emission is bounded, and the bound is measured rather than assumed.

    The escape is twelve bits written immediately after the final token, so it fits
    inside the final partial word whenever at least twelve bits of it are free and
    costs exactly one more packed word otherwise. The ticket is explicit that the
    increase is not always four bytes; both cases occur in this corpus, and the
    token stream itself is unchanged either way.
    """
    deltas: set[int] = set()
    for name, payload in _termination_corpus():
        with_marker = wl.pack(payload)
        monkeypatch.setattr(wl._WordBitWriter, "write_end_marker", lambda self: None)
        try:
            without_marker = wl.pack(payload)
        finally:
            monkeypatch.undo()
        assert with_marker[: len(without_marker)] == without_marker, f"tokens: {name}"
        deltas.add(len(with_marker) - len(without_marker))
    assert deltas == {0, 4}, f"unexpected marker cost: {sorted(deltas)}"


def _narrow_to_seven_bit_literals(writer: "wl._WordBitWriter", base: int) -> None:
    """The other half of the literal-width control escape: 7 bits plus a base.

    Prefix ``0 0 1`` reaches the four-bit code, a zero field makes it -1, the next
    bit is clear (not a raw run), and the final ``0`` selects ``literal_bits = 7``,
    which the format then follows with an 8-bit base.
    """
    writer.bit(0)
    writer.bit(0)
    writer.bit(1)
    writer.put(0, 4)
    writer.bit(0)
    writer.bit(0)
    writer.put(base, 8)


def _base_switch_stream(writer: "wl._WordBitWriter") -> None:
    """One container that narrows to 7-bit literals and widens back to 8.

    Tokens, in order: an initial 1-bit literal (``0x00``), the narrowing control
    with base ``0x40``, a 7-bit literal ``0x40 + 3``, the widening control, and a
    final 8-bit literal of ``0x11``. Only the last byte can tell the two grammars
    apart, and only because it is a literal rather than a match.
    """
    writer.bit(1)          # a literal at the initial width: kind 1 -> 1 bit
    writer.put(0, 1)
    _narrow_to_seven_bit_literals(writer, 0x40)
    writer.bit(1)          # 7-bit literal: 0x40 + 3
    writer.put(3, 7)
    _widen_to_eight_bit_literals(writer)
    writer.bit(1)          # 8-bit literal: the engine emits 0x11 itself
    writer.put(0x11, 8)
    _end_marker(writer)


def test_widening_back_to_eight_bit_literals_clears_the_literal_base() -> None:
    """The engine's rule for the literal-base control, on a synthetic stream.

    A corpus cannot settle this one: a base only survives if a 7-bit run is
    followed by a return to 8-bit literals *inside one container*, and the byte
    that exposes it must be a literal rather than a match. It was found instead by
    comparing the SDK's decode against the retail engine's own character memory,
    where bank 141 differs at 1,762 of its bytes, every one by exactly the
    retained base (`docs/research/BUU_MAP_GRAPHICS_DIAG.md` §3.6-3.7).

    The stream below makes the difference visible in one byte: with the base
    cleared the final literal is the engine's ``0x11``; with the base retained it
    decodes as ``0x11 + 0x40 == 0x51``. This test carried a strict ``xfail``
    while the defect shipped, and MAP-GFX-DIAG-001's correction removed it.
    """
    assert wl.unpack(_container(1, 3, _base_switch_stream), 0).data == bytes(
        [0x00, 0x43, 0x11]
    )


def test_a_retained_literal_base_would_decode_the_engine_s_byte_wrong() -> None:
    """The mutation control for the rule above: the old behaviour is not silent.

    Replays the same stream under the pre-correction grammar - the one line this
    ticket changed - and requires the third byte to come out ``0x51``. If a future
    change restores the retained base, this test still passes and the one above
    fails, which is what makes the pair a regression rather than a restatement.
    """
    data = _container(1, 3, _base_switch_stream)
    reader = wl._WordBitReader(data, wl.HEADER_SIZE)
    out = bytearray()
    literal_base = 0
    literal_bits = 1
    while len(out) < 3:
        if reader.bit():
            out.append((literal_base + reader.get(literal_bits)) & 0xFF)
            continue
        assert reader.bit() == 0, "the fixture uses no match tokens"
        assert reader.bit() == 1, "the fixture uses no 000-prefix tokens"
        short_distance = reader.get(4) - 1
        assert short_distance < 0, "the fixture uses no short-distance tokens"
        assert reader.bit() == 0, "the fixture uses no raw-literal-run tokens"
        literal_bits = 7 + reader.bit()
        if literal_bits != 8:  # the pre-correction grammar
            literal_base = reader.get(8)
    assert bytes(out) == bytes([0x00, 0x43, 0x51])
