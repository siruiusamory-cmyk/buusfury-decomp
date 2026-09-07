"""Portable tests for the Webfoot container codec (TOOLKIT-010).

Every fixture here is synthetic. The ROM's own containers are exercised by
`tests/integration/test_graphics_rom.py`, which skips when the image is absent;
nothing ROM-derived is committed.

The pairing that matters: `pack` is checked by `unpack`, never against captured
bytes. That is the only claim the encoder makes - it emits a stream the verified
decoder accepts - and testing it against a golden blob would assert a stronger
property than the module is willing to state.
"""

from __future__ import annotations

import struct

import pytest

from tools.webfoot.formats import webfoot_lz as wl


def test_stored_container_round_trips_verbatim() -> None:
    payload = bytes(range(256))
    blob = wl.build_stored(payload)
    container = wl.unpack(blob, 0)
    assert container.kind == wl.STORED
    assert container.data == payload
    assert container.declared_size == len(payload)
    assert container.packed_end == wl.HEADER_SIZE + len(payload)


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
