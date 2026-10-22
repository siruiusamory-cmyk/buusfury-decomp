from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable, Sequence

import webfoot_lz

HEADER_SIZE = 8
MAX_PAYLOAD = 0x4000
ZERO_TAIL_SLACK = 4


class TileBankError(ValueError):
    pass


@dataclass(frozen=True)
class Bank:
    kind: int
    declared_size: int
    payload: bytes
    stored_size: int | None = None


def decode(blob: bytes) -> Bank:
    container = webfoot_lz.unpack(blob, 0, maximum_output=MAX_PAYLOAD)
    if container.packed_end > len(blob):
        raise TileBankError("container in a %d-byte blob runs past it" % len(blob))
    return Bank(container.kind, container.declared_size, container.data, container.packed_size)


def decode_block(block: bytes, offsets: Sequence[int]) -> list[Bank]:
    if not offsets or offsets[0] < 0 or list(offsets) != sorted(set(offsets)):
        raise TileBankError("offsets must be a strictly increasing list inside the block")
    banks = []
    for offset in offsets:
        if offset >= len(block):
            raise TileBankError("offset %#x is outside the block" % offset)
        container = webfoot_lz.unpack(block, offset, maximum_output=MAX_PAYLOAD)
        if container.packed_end > len(block):
            raise TileBankError("container at %#x runs past the block" % offset)
        banks.append(Bank(container.kind, container.declared_size, container.data,
                          container.packed_size))
    return banks


def encode(bank: Bank, compress: Callable[[bytes], bytes]) -> bytes:
    if bank.declared_size != len(bank.payload):
        raise TileBankError("declared %d against a %d-byte payload"
                            % (bank.declared_size, len(bank.payload)))
    blob = compress(bank.payload)
    header = struct.pack("<II", bank.kind, bank.declared_size)
    if blob[:HEADER_SIZE] != header:
        raise TileBankError("compressor header %s is not %s"
                            % (blob[:HEADER_SIZE].hex(), header.hex()))
    if bank.stored_size is None:
        return blob
    if abs(len(blob) - bank.stored_size) > ZERO_TAIL_SLACK:
        raise TileBankError("re-encoded %d bytes against a stored %d"
                            % (len(blob), bank.stored_size))
    if any(blob[bank.stored_size:]):
        raise TileBankError("re-encoded container holds non-zero bytes past its stored length")
    fitted = blob[:bank.stored_size]
    return fitted + bytes(bank.stored_size - len(fitted))


def encode_block(banks: Sequence[Bank], offsets: Sequence[int], block_len: int,
                 compress: Callable[[bytes], bytes]) -> bytes:
    if len(banks) != len(offsets):
        raise TileBankError("%d banks against %d offsets" % (len(banks), len(offsets)))
    if not offsets or offsets[0] < 0 or list(offsets) != sorted(set(offsets)):
        raise TileBankError("offsets must be a strictly increasing list inside the block")
    if offsets[-1] >= block_len:
        raise TileBankError("last offset %#x is outside a %d-byte block" % (offsets[-1], block_len))
    block = bytearray(block_len)
    for index, (bank, offset) in enumerate(zip(banks, offsets)):
        end = offsets[index + 1] if index + 1 < len(offsets) else block_len
        blob = encode(bank, compress)
        if offset + len(blob) > end:
            raise TileBankError("bank %d overruns the %d bytes before the next offset"
                                % (index, end - offset))
        block[offset:offset + len(blob)] = blob
    return bytes(block)
