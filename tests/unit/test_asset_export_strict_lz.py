"""Portable tests for the strict export-side Webfoot container decoder.

The strict decoder was written because the shipping decoder used to clip an
over-long final match and report success. **EVIDENCE-RISK-DEBT-001 removed that
defect from the shipping decoder**, so this module is no longer the only reader
that refuses a malformed stream: what it still adds is the *end-marker*
postcondition and a bound on the input consumed. These tests pin the refusal, the
agreement between the two decoders on both well-formed and malformed streams, and
the structural checks the export path relies on. No ROM is required.
"""

from __future__ import annotations

import struct

import pytest

from tools.export import webfoot_strict as ws
from tools.research import webfoot_codec_reference as reference
from tools.webfoot.formats import webfoot_lz as project


def _header(kind: int, declared: int) -> bytes:
    return struct.pack("<II", kind, declared)


#: The canonical reproduction of the clipping defect, from `LOGX-SYNTHESIS.md`
#: §11.1: form 1, declared 4.
CLIPPING_CASE = bytes.fromhex("01000000040000000558d020000000c0")


def test_the_shipping_decoder_now_refuses_the_reproduction_case():
    """The defect this module was written around has been repaired.

    This test used to assert the opposite - that the shipping decoder returned
    four clipped bytes - and was inverted by EVIDENCE-RISK-DEBT-001 together with
    the decoder. It is kept inverted rather than deleted so the regression is
    pinned in both directions.
    """
    with pytest.raises(project.ContainerError, match="declared 4"):
        project.unpack(CLIPPING_CASE, 0)
    assert len(CLIPPING_CASE) == ws.HEADER_SIZE + 8


def test_the_strict_decoder_refuses_the_over_long_final_match():
    with pytest.raises(ws.ContainerError) as excinfo:
        ws.unpack(CLIPPING_CASE, 0)
    assert "15 bytes against a declared 4" in str(excinfo.value)


def test_the_independent_reference_agrees_the_case_is_malformed():
    with pytest.raises(reference.CodecError):
        reference.decode_packed(CLIPPING_CASE, ws.HEADER_SIZE, declared_size=4)


def test_both_shipping_decoders_refuse_every_malformed_case():
    """The repaired decoder and the export reader agree on rejection.

    Before EVIDENCE-RISK-DEBT-001 the first entry of this list was *accepted* by
    the shipping decoder and refused only here, which is why this module had to
    exist as a separate reader.
    """
    malformed = [
        CLIPPING_CASE,                                    # final match overrun
        _raw_run_overrun(),                               # raw literal run overrun
        _header(1, 4),                                    # no payload at all
        _header(0, 64) + b"short",                         # stored past the image
        _header(2, 4) + b"\x00\x00",                       # stream ends in a word
        _header(7, 4) + b"\x00" * 8,                       # unknown kind
    ]
    for blob in malformed:
        with pytest.raises(project.ContainerError):
            project.unpack(blob, 0)
        with pytest.raises(ws.ContainerError):
            ws.unpack(blob, 0)
    # The repaired decoder no longer needs the end-marker rule to refuse this one.
    with pytest.raises(project.ContainerError):
        project.unpack(CLIPPING_CASE, 0)


def _raw_run_overrun() -> bytes:
    """A raw literal run of four bytes behind a header that declares three.

    Built with the project module's own bit writer so the fixture is the format
    rather than a captured blob: prefix ``0 0 1``, a zero four-bit field, a set
    run bit, then two literal pairs with a continuation bit after each.
    """
    writer = project._WordBitWriter()
    for bit in (0, 0, 1):
        writer.bit(bit)
    writer.put(0, 4)
    writer.bit(1)
    for index, value in enumerate((0x58, 0xAC, 0xAD, 0x41)):
        writer.put(value, 8)
        if index % 2 == 1:
            writer.bit(0 if index == 3 else 1)
    return _header(1, 3) + writer.finish()


def test_stored_container_is_returned_verbatim():
    payload = bytes(range(16))
    container = ws.unpack(_header(0, len(payload)) + payload, 0)
    assert container.kind == 0
    assert container.data == payload
    assert container.packed_end == ws.HEADER_SIZE + len(payload)


def test_stored_container_refuses_a_declared_size_past_the_image():
    with pytest.raises(ws.ContainerError):
        ws.unpack(_header(0, 64) + b"\x00" * 8, 0)


def test_zero_length_stored_container_is_legal():
    container = ws.unpack(_header(0, 0), 0)
    assert container.data == b""
    assert container.declared_size == 0


def test_unknown_kind_is_refused():
    with pytest.raises(ws.ContainerError):
        ws.unpack(_header(7, 4) + b"\x00" * 8, 0)


def test_declared_size_over_the_safety_limit_is_refused():
    with pytest.raises(ws.ContainerError):
        ws.unpack(_header(1, ws.MAX_OUTPUT + 1), 0)


def test_header_outside_the_image_is_refused():
    with pytest.raises(ws.ContainerError):
        ws.read_header(b"\x00" * 4, 0)


def test_a_stream_that_ends_inside_a_bit_word_is_refused():
    with pytest.raises(ws.ContainerError):
        ws.decode_packed(b"\x00\x00", 0, 4, 1)


def test_the_project_encoder_output_decodes_strictly_at_the_declared_size():
    """The default strict rule - exact declared size, no clipping - accepts every
    `webfoot_lz.pack` output, exactly as it accepts the canonical corpus."""
    for size in (1, 2, 3, 7, 64, 300, 1024):
        payload = bytes((index * 37 + size) % 256 for index in range(size))
        encoded = project.pack(payload)
        kind, declared = ws.read_header(encoded, 0)
        assert kind in ws.PACKED_KINDS
        assert declared == size
        assert project.unpack(encoded, 0).data == payload
        assert ws.unpack(encoded, 0).data == payload


def test_the_project_encoder_output_satisfies_the_end_marker_rule():
    """The stronger check the export path uses now accepts the project encoder.

    **Inverted by CQA-02-PACKED-STREAM-TERMINATION-001.** This test used to assert
    the opposite - that `webfoot_lz.pack` never wrote the end-marker escape, so a
    two-byte payload's encoding was refused by the marker rule while the size rule
    accepted it - and it is kept inverted rather than deleted so the regression is
    pinned in both directions. The pre-fix byte fixture that the marker rule still
    refuses is pinned in `tests/unit/test_webfoot_lz.py`.

    The engine's rule is the marker rule: it carries no output counter and stops
    only on the stream's own escape. The canonical corpus carries a marker at the
    declared size for every one of the 11,712 packed containers this exporter
    reaches, and `pack` now does the same by construction rather than by luck.
    """
    for size in (1, 2, 3, 7, 64, 300, 1024):
        payload = bytes((index * 7 + size) % 256 for index in range(size))
        encoded = project.pack(payload)
        assert ws.unpack(encoded, 0).data == payload
        strict = ws.unpack(encoded, 0, require_end_marker=True)
        assert strict.data == payload
        assert strict.declared_size == size


def test_strict_reading_agrees_with_the_research_reference():
    for size in (5, 33, 512):
        payload = bytes((index * 11) % 256 for index in range(size))
        encoded = project.pack(payload)
        kind, declared = ws.read_header(encoded, 0)
        strict = ws.unpack(encoded, 0).data
        got = reference.decode_packed(
            encoded, ws.HEADER_SIZE, declared_size=declared
        )
        assert strict == got.data


def test_strict_decoder_accepts_a_stream_that_ends_on_its_marker():
    """The literal-1 opening escape, one literal, then the end marker."""
    bits = "0" "0" "1" "0000" "0" "1" + "1" + "01011010" + "0" "0" "0" + "0000000" + "00"
    bits += "0" * ((32 - len(bits) % 32) % 32)
    words = [
        int(bits[index : index + 32], 2) for index in range(0, len(bits), 32)
    ]
    blob = _header(2, 1) + b"".join(struct.pack("<I", word) for word in words)
    container = ws.unpack(blob, 0)
    assert container.data == bytes([0x5A])


def test_a_stream_that_keeps_going_past_the_declared_size_is_refused():
    """With the end-marker check on, the stream must stop, not merely fill.

    The opening escape widens literals to eight bits, one literal completes the
    declared single byte, and the following bit opens another literal instead of
    the end-marker escape. Both decoders still produce the declared byte; only the
    strict end-marker rule notices that the stream did not stop.
    """
    bits = "001" "0000" "01" + "1" + "01011010" + "1" + "00000000"
    bits += "0" * ((32 - len(bits) % 32) % 32)
    word = int(bits, 2)
    blob = _header(2, 1) + struct.pack("<I", word)
    assert project.unpack(blob, 0).data == bytes([0x5A])
    assert ws.unpack(blob, 0).data == bytes([0x5A])
    with pytest.raises(ws.ContainerError):
        ws.unpack(blob, 0, require_end_marker=True)


def test_the_end_marker_rule_accepts_a_stream_that_ends_on_its_marker():
    bits = "001" "0000" "01" + "1" + "01011010" + "000" + "0000000" + "00"
    bits += "0" * ((32 - len(bits) % 32) % 32)
    word = int(bits, 2)
    blob = _header(2, 1) + struct.pack("<I", word)
    container = ws.unpack(blob, 0, require_end_marker=True)
    assert container.data == bytes([0x5A])


def test_unpack_address_uses_the_gba_base():
    payload = b"abcdefgh"
    rom = _header(0, len(payload)) + payload
    container = ws.unpack_address(rom, ws.GBA_ROM_BASE)
    assert container.data == payload
    assert container.offset == 0


def test_unpack_address_uses_the_gba_base():
    payload = b"abcdefgh"
    rom = _header(0, len(payload)) + payload
    container = ws.unpack_address(rom, ws.GBA_ROM_BASE)
    assert container.data == payload
    assert container.offset == 0


def test_bad_literal_width_is_refused():
    with pytest.raises(ws.ContainerError):
        ws.decode_packed(b"\x00" * 8, 0, 4, 0)
    with pytest.raises(ws.ContainerError):
        ws.decode_packed(b"\x00" * 8, 0, 4, 10)
