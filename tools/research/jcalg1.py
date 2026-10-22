from __future__ import annotations

import struct

HEADER_SIZE = 8

INITIAL_LITERAL_BITS = 1

INITIAL_DISTANCE_BITS = 8

INITIAL_PREVIOUS_DISTANCE = 1

RAW_RUN_BLOCK = 256

MAX_OUTPUT = 4 * 1024 * 1024

LENGTH_LADDER = ((0x10000, 3), (0x37FF, 2), (0x027F, 1), (0x0080, 0), (0x0000, 4))

OK = "ok"
LIMIT = "limit"
OUTPUT = "output"
DISTANCE = "distance"

REASONS = (OK, LIMIT, OUTPUT, DISTANCE)


class _Refused(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class _Reader:

    __slots__ = ("_image", "_offset", "_position", "_limit", "_word", "_remaining")

    def __init__(self, image: bytes, offset: int, limit: int) -> None:
        self._image = image
        self._offset = offset
        self._position = offset
        self._limit = limit
        self._word = 0
        self._remaining = 0

    def bit(self) -> int:
        if self._remaining == 0:
            if self._position + 4 > self._limit:
                raise _Refused(LIMIT)
            self._word = struct.unpack_from("<I", self._image, self._position)[0]
            self._position += 4
            self._remaining = 32
        value = (self._word >> 31) & 1
        self._word = (self._word << 1) & 0xFFFFFFFF
        self._remaining -= 1
        return value

    def get(self, count: int) -> int:
        value = 0
        for _ in range(count):
            value = (value << 1) | self.bit()
        return value

    @property
    def consumed(self) -> int:
        return self._position - self._offset


def _gamma(reader: _Reader) -> int:
    value = 1
    while True:
        value = (value << 1) | reader.bit()
        if value > MAX_OUTPUT + 3:
            raise _Refused(OUTPUT)
        if reader.bit() == 0:
            return value


def _length_bias(distance: int) -> int:
    for threshold, added in LENGTH_LADDER:
        if distance >= threshold:
            return added
    raise AssertionError(distance)


def _put(out: bytearray, value: int) -> None:
    if len(out) >= MAX_OUTPUT:
        raise _Refused(OUTPUT)
    out.append(value)


def _copy(out: bytearray, distance: int, count: int) -> None:
    if distance == 0 or distance > len(out):
        raise _Refused(DISTANCE)
    if len(out) + count > MAX_OUTPUT:
        raise _Refused(OUTPUT)
    for _ in range(count):
        out.append(out[-distance])


def _decode(image: bytes, offset: int, limit: int) -> tuple[bytes, int]:
    if offset < 0 or offset >= len(image) or limit > len(image) or limit <= offset:
        raise _Refused(LIMIT)

    reader = _Reader(image, offset, limit)
    out = bytearray()
    literal_bits = INITIAL_LITERAL_BITS
    literal_base = 0
    distance_bits = INITIAL_DISTANCE_BITS
    previous_distance = INITIAL_PREVIOUS_DISTANCE

    while True:
        if reader.bit():
            _put(out, (literal_base + reader.get(literal_bits)) & 0xFF)
            continue

        if reader.bit():
            code = _gamma(reader)
            if code == 2:
                _copy(out, previous_distance, _gamma(reader))
                continue
            distance = ((code - 3) << distance_bits) + reader.get(distance_bits)
            previous_distance = distance
            _copy(out, distance, _gamma(reader) + _length_bias(distance))
            continue

        if reader.bit() == 0:
            short_distance = reader.get(7)
            if short_distance:
                previous_distance = short_distance
                _copy(out, short_distance, reader.get(2) + 2)
                continue
            escape_width = reader.get(2)
            if escape_width == 0:
                break
            distance_bits = reader.get(escape_width + 3)
            continue

        short_distance = reader.get(4) - 1
        if short_distance == 0:
            _put(out, literal_base & 0xFF)
            continue
        if short_distance > 0:
            _copy(out, short_distance, 1)
            continue
        if reader.bit():
            while True:
                for _ in range(RAW_RUN_BLOCK):
                    _put(out, reader.get(8))
                if reader.bit() == 0:
                    break
            continue
        literal_bits = 7 + reader.bit()
        if literal_bits == 8:
            literal_base = 0
        else:
            literal_base = reader.get(8)

    return bytes(out), reader.consumed


def decompress(image: bytes, offset: int, limit: int) -> tuple[bytes, int] | None:
    try:
        return _decode(image, offset, limit)
    except _Refused:
        return None


def probe(image: bytes, offset: int, limit: int) -> dict:
    try:
        data, consumed = _decode(image, offset, limit)
    except _Refused as refusal:
        return {"ok": False, "reason": refusal.reason, "size": 0, "consumed": 0, "data": None}
    return {"ok": True, "reason": OK, "size": len(data), "consumed": consumed, "data": data}
