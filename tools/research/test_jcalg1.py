import hashlib
import os
import struct
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))

import jcalg1  # noqa: E402
import webfoot_lz  # noqa: E402

ROM = os.path.join(ROOT, "baserom.gba")
ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")

INTRO_CONTAINER = 0x55620
INTRO_END = 0x561C4
INTRO_DECODED = 38400
INTRO_DECODED_SHA256 = "f2f20104d217e0e108f964912e233bf18140caa3958d5ad7688abf409447e5cf"

PAYLOAD = b"the quick brown fox jumps over the lazy dog " * 24 + bytes(range(256)) * 4


class _Writer:

    def __init__(self):
        self._bits = []

    def put(self, value, width):
        for shift in range(width - 1, -1, -1):
            self._bits.append((value >> shift) & 1)

    def gamma(self, value):
        for shift in range(value.bit_length() - 2, -1, -1):
            self.put((value >> shift) & 1, 1)
            self.put(0 if shift == 0 else 1, 1)

    def finish(self):
        bits = self._bits + [0] * ((-len(self._bits)) % 32)
        out = bytearray()
        for start in range(0, len(bits), 32):
            word = 0
            for bit in bits[start:start + 32]:
                word = (word << 1) | bit
            out += struct.pack("<I", word)
        return bytes(out)


def _container(body, *, kind=1, declared=0):
    return struct.pack("<II", kind, declared) + body


def _raw_run_stream(blocks):
    writer = _Writer()
    writer.put(0b001, 3)
    writer.put(0, 4)
    writer.put(1, 1)
    for index, block in enumerate(blocks):
        for value in block:
            writer.put(value, 8)
        writer.put(1 if index + 1 < len(blocks) else 0, 1)
    writer.put(0, 12)
    return writer.finish()


def test_the_round_trip_over_both_packed_kinds():
    for kind in (1, 2):
        packed = webfoot_lz.pack(PAYLOAD, kind=kind)
        assert jcalg1.decompress(packed, 8, len(packed)) == (PAYLOAD, len(packed) - 8)
        assert jcalg1.probe(packed, 8, len(packed))["reason"] == jcalg1.OK


def test_a_truncated_stream_is_refused():
    packed = webfoot_lz.pack(PAYLOAD)
    assert jcalg1.decompress(packed, 8, len(packed))[1] > 4
    assert jcalg1.decompress(packed, 8, 8 + 4) is None
    assert jcalg1.probe(packed, 8, 8 + 4)["reason"] == jcalg1.LIMIT


def test_a_stream_whose_end_code_is_past_the_limit_is_refused():
    packed = webfoot_lz.pack(PAYLOAD)
    consumed = jcalg1.decompress(packed, 8, len(packed))[1]
    assert jcalg1.probe(packed, 8, 8 + consumed)["ok"]
    refusal = jcalg1.probe(packed, 8, 8 + consumed - 4)
    assert refusal["ok"] is False
    assert refusal["reason"] == jcalg1.LIMIT


def test_a_raw_run_is_read_in_256_byte_blocks():
    first = bytes(range(256))
    second = bytes(reversed(range(256)))
    one = _container(_raw_run_stream([first]))
    decoded, consumed = jcalg1.decompress(one, 8, len(one))
    assert decoded == first
    assert consumed == len(one) - 8

    two = _container(_raw_run_stream([first, second]))
    decoded, _ = jcalg1.decompress(two, 8, len(two))
    assert decoded == first + second


def test_a_back_reference_outside_the_output_is_refused():
    writer = _Writer()
    writer.put(0, 1)
    writer.put(1, 1)
    writer.put(1, 1)
    writer.put(0, 1)
    writer.put(1, 8)
    image = _container(writer.finish())
    refusal = jcalg1.probe(image, 8, len(image))
    assert refusal["ok"] is False
    assert refusal["reason"] == jcalg1.DISTANCE


def test_the_initial_literal_width_is_the_callers_one_bit():
    writer = _Writer()
    writer.put(1, 1)
    writer.put(1, 1)
    writer.put(0, 12)
    image = _container(writer.finish())
    assert jcalg1.decompress(image, 8, len(image)) == (b"\x01", len(image) - 8)


def test_an_output_explosion_is_refused_not_allocated():
    for count in (1 << 22, 1 << 24):
        writer = _Writer()
        writer.put(1, 1)
        writer.put(0, 1)
        writer.put(0, 1)
        writer.put(1, 1)
        writer.gamma(2)
        writer.gamma(count)
        image = _container(writer.finish())
        refusal = jcalg1.probe(image, 8, len(image))
        assert refusal["ok"] is False
        assert refusal["reason"] == jcalg1.OUTPUT


def test_the_known_intro_stream_decodes_and_re_compresses_byte_for_byte(tmp_path):
    if not os.path.exists(ROM):
        pytest.skip("baserom.gba is not on disk")
    if not os.path.exists(COMPRESS):
        pytest.skip("tools/compress/compress.exe is not on disk")
    image = open(ROM, "rb").read()
    assert hashlib.sha256(image).hexdigest() == ROM_SHA256
    retail = image[INTRO_CONTAINER:INTRO_END]
    kind, declared = struct.unpack_from("<II", image, INTRO_CONTAINER)
    assert kind == 1 and declared == INTRO_DECODED

    decoded, consumed = jcalg1.decompress(image, INTRO_CONTAINER + 8, INTRO_END)
    assert len(decoded) == INTRO_DECODED == declared
    assert hashlib.sha256(decoded).hexdigest() == INTRO_DECODED_SHA256
    assert consumed == INTRO_END - INTRO_CONTAINER - 8
    assert webfoot_lz.unpack(image, INTRO_CONTAINER, maximum_output=1 << 20).data == decoded

    payload = tmp_path / "asset_intro.img.bin"
    payload.write_bytes(decoded)
    out = tmp_path / "asset_intro.compressed"
    proc = subprocess.run([COMPRESS, str(payload), str(out)], capture_output=True)
    assert proc.returncode == 0, proc.stderr
    assert out.read_bytes() == retail
