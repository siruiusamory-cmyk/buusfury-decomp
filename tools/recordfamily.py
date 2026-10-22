from __future__ import annotations

import struct


def base_word(rom: bytes, own: str, literal: int, base: int) -> None:
    word = struct.unpack_from("<I", rom, literal)[0]
    if word != base:
        raise ValueError("%s's base literal at file %#x is %#010x, not %#010x"
                         % (own, literal, word, base))
    pattern = struct.pack("<I", base)
    hits, at = [], rom.find(pattern)
    while at != -1:
        hits.append(at)
        at = rom.find(pattern, at + 1)
    if hits != [literal]:
        raise ValueError("%s's base word occurs at %s, not once at file %#x"
                         % (own, ["%#x" % hit for hit in hits], literal))


def consumer_pins(rom: bytes, own: str, pins) -> None:
    for address, halfword in pins:
        got = struct.unpack_from("<H", rom, address)[0]
        if got != halfword:
            raise ValueError("%s's consumer instruction at file %#x is %#06x, not %#06x"
                             % (own, address, got, halfword))


def held_contract(measured: dict, expected: dict, own: str) -> dict:
    if measured != expected:
        raise ValueError("%s measures %s, the contract says %s" % (own, measured, expected))
    return measured


def serialize_record(rom: bytes, family: str, own: str, offset: int, size: int,
                     fields, serialize) -> bytes:
    if family != own:
        raise ValueError("%s is not this module's family" % family)
    return serialize(fields(rom, offset, size), size)


def extents(rom: bytes, family: str, own: str, assert_contract, rows) -> dict:
    if family not in (None, own):
        raise ValueError("%s is not this module's family" % family)
    contract = assert_contract(rom)
    if contract["last_end"] > len(rom):
        raise ValueError("%s ends at %#x, past the %d-byte image"
                         % (own, contract["last_end"], len(rom)))
    return {own: rows}


def packed(out: bytearray, size: int, own: str) -> bytes:
    if len(out) != size:
        raise ValueError("%s serializes to %d bytes, its extent is %d" % (own, len(out), size))
    return bytes(out)


def round_trip(rom: bytes, own: str, base: int, stride: int, count: int,
               serialize_record) -> dict[str, int]:
    equal = 0
    for index in range(count):
        offset = base + stride * index
        equal += serialize_record(rom, own, offset, stride) == rom[offset:offset + stride]
    return {"records": count, "equal": equal, "bytes": count * stride}


def round_trip_one(rom: bytes, own: str, base: int, extent: int,
                   serialize_record) -> dict[str, int]:
    equal = serialize_record(rom, own, base, extent) == rom[base:base + extent]
    return {"records": 1, "equal": int(equal), "bytes": extent}


def main(family: str, assert_contract, round_trip, argv) -> None:
    image = open(argv[1] if len(argv) > 1 else "baserom.gba", "rb").read()
    print("%s measure %s" % (family, assert_contract(image)))
    print("%s verify  round trip %s" % (family, round_trip(image)))
