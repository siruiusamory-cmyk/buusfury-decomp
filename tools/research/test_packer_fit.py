from __future__ import annotations

import hashlib
import os
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))
sys.path.insert(0, HERE)

import packer_census as census  # noqa: E402
import packer_fit as fit  # noqa: E402
import webfoot_lz  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")
MARKER_DELTA = {0x3C35B8: 4, 0x3C3808: 4, 0x54AB4C: 4, 0x54AC6C: 4}


def image():
    rom = open(ROM, "rb").read()
    assert hashlib.sha256(rom).hexdigest() == census.ROM_SHA256
    return rom


def oracle():
    return census.Oracle(census.COMPRESS, tempfile.mkdtemp(prefix="packer-test-"))


def tokens_of(rom, offset):
    payload = webfoot_lz.unpack(rom, offset, maximum_output=census.MAX_OUTPUT).data
    blob, error = oracle()(payload)
    assert blob is not None, error
    return payload, blob, fit.stream_tokens(blob, 8, len(payload), 1)[0]


def test_the_marker_extent_is_four_bytes_past_the_default_decode():
    rom = image()
    for offset, delta in MARKER_DELTA.items():
        early = webfoot_lz.unpack(rom, offset, maximum_output=census.MAX_OUTPUT)
        marker = webfoot_lz.validate_retail_termination(rom, offset, maximum_output=census.MAX_OUTPUT)
        assert marker.packed_end - early.packed_end == delta
        assert rom[early.packed_end:marker.packed_end] == bytes(delta)


def test_the_oracle_output_length_equals_the_marker_extent_on_the_fixtures():
    rom = image()
    compress = oracle()
    for offset in census.FIXTURE_PACKED:
        payload = webfoot_lz.unpack(rom, offset, maximum_output=census.MAX_OUTPUT).data
        blob, error = compress(payload)
        assert blob is not None, error
        assert len(blob) == census.retail_extent(rom, offset)[0] - offset
        assert blob == rom[offset:offset + len(blob)]


def test_the_three_stored_fixtures_are_reproduced_by_build_stored():
    rom = image()
    for offset in census.FIXTURE_STORED:
        payload = webfoot_lz.unpack(rom, offset, maximum_output=census.MAX_OUTPUT).data
        extent = census.retail_extent(rom, offset)[0]
        assert webfoot_lz.build_stored(payload) == rom[offset:extent]


def test_the_final_payload_byte_is_never_inside_a_match():
    rom = image()
    for offset in census.FIXTURE_PACKED:
        payload, blob, tokens = tokens_of(rom, offset)
        tail = [token for token in tokens if token[1] != "end"][-1]
        assert tail[1] in ("literal", "base", "one"), tail
        assert tail[2] == len(payload) - 1


def test_every_escape_mode_equals_the_next_1024_bytes_span_rule():
    rom = image()
    for offset in census.FIXTURE_PACKED:
        payload, blob, tokens = tokens_of(rom, offset)
        escapes = [token for token in tokens if token[1] == "litwidth"]
        assert escapes
        for token in escapes:
            assert fit.window_mode(payload, token[2]) == (token[3], token[4])


def test_the_candidate_encoder_is_deterministic_and_round_trips():
    rom = image()
    for offset in census.FIXTURE_PACKED[:4]:
        payload = webfoot_lz.unpack(rom, offset, maximum_output=census.MAX_OUTPUT).data
        first = fit.encode(payload, 1)
        second = fit.encode(payload, 1)
        assert first == second
        kind, declared = struct.unpack_from("<II", first)
        assert (kind, declared) == (1, len(payload))
        assert webfoot_lz.unpack_raw_stream(first, 8, len(payload), initial_literal_bits=1) == payload
        assert webfoot_lz.validate_retail_termination(first, 0, maximum_output=census.MAX_OUTPUT)


if __name__ == "__main__":
    test_the_marker_extent_is_four_bytes_past_the_default_decode()
    test_the_oracle_output_length_equals_the_marker_extent_on_the_fixtures()
    test_the_three_stored_fixtures_are_reproduced_by_build_stored()
    test_the_final_payload_byte_is_never_inside_a_match()
    test_every_escape_mode_equals_the_next_1024_bytes_span_rule()
    test_the_candidate_encoder_is_deterministic_and_round_trips()
    print("PASS packer evidence tests")
