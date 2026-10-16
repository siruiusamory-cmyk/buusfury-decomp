
from __future__ import annotations

from dataclasses import dataclass
import struct
import zlib

MAGIC = b"BPS1"

FOOTER_SIZE = 12

SOURCE_READ = 0
TARGET_READ = 1
SOURCE_COPY = 2
TARGET_COPY = 3
_ACTION_MASK = 0x03

_MAX_SHIFT = 1 << 70

MAX_IMAGE_SIZE = 32 * 1024 * 1024


class BpsError(ValueError):
    """Base error for encoding, reading or applying a BPS patch."""


class BpsFormatError(BpsError):
    """The bytes are not a well-formed BPS patch, or a checksum disagrees."""


class BpsSourceError(BpsError):
    """The supplied source image is not the one this patch was made for."""


@dataclass(frozen=True, slots=True)
class BpsHeader:

    source_size: int
    target_size: int
    metadata: bytes
    source_crc32: int
    target_crc32: int
    patch_crc32: int
    action_offset: int


def crc32(data: bytes) -> int:
    """The CRC-32 BPS stores, which is the same one `tools.webfoot.hashing` reports."""
    return zlib.crc32(data) & 0xFFFFFFFF


def encode_number(value: int) -> bytes:
    """A BPS number, in the format's own variable-length form."""
    if value < 0:
        raise ValueError("a BPS number is unsigned")
    out = bytearray()
    while True:
        group = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(group | 0x80)
            return bytes(out)
        out.append(group)
        value -= 1


def decode_number(data: bytes, offset: int, limit: int) -> tuple[int, int]:
    """`limit` bounds the readable body, so a malformed field cannot run into the next."""
    value = 0
    shift = 1
    while True:
        if offset >= limit:
            raise BpsFormatError("a number runs past the end of the patch body")
        group = data[offset]
        offset += 1
        value += (group & 0x7F) * shift
        if group & 0x80:
            return value, offset
        if shift > _MAX_SHIFT:
            raise BpsFormatError("a number is wider than the format allows")
        shift <<= 7
        value += shift


def _signed_offset(value: int) -> int:
    distance = value >> 1
    return -distance if value & 1 else distance


def encode(source: bytes, target: bytes, metadata: bytes = b"") -> bytes:
    if not isinstance(metadata, (bytes, bytearray)):
        raise TypeError("metadata must be bytes")
    body = bytearray(MAGIC)
    body += encode_number(len(source))
    body += encode_number(len(target))
    body += encode_number(len(metadata))
    body += bytes(metadata)

    limit = min(len(source), len(target))
    index = 0
    while index < limit:
        if source[index] == target[index]:
            run = index + 1
            while run < limit and source[run] == target[run]:
                run += 1
            body += encode_number(((run - index - 1) << 2) | SOURCE_READ)
            index = run
        else:
            run = index + 1
            while run < limit and source[run] != target[run]:
                run += 1
            body += encode_number(((run - index - 1) << 2) | TARGET_READ)
            body += target[index:run]
            index = run

    if len(target) > limit:
        tail = len(target) - limit
        body += encode_number(((tail - 1) << 2) | TARGET_READ)
        body += target[limit:]

    body += struct.pack("<I", crc32(source))
    body += struct.pack("<I", crc32(target))
    body += struct.pack("<I", crc32(bytes(body)))
    return bytes(body)


def inspect(patch: bytes) -> BpsHeader:
    data = bytes(patch)
    if len(data) < len(MAGIC) + FOOTER_SIZE:
        raise BpsFormatError(
            f"a BPS patch is at least {len(MAGIC) + FOOTER_SIZE} bytes; this one is "
            f"{len(data)}"
        )
    if data[: len(MAGIC)] != MAGIC:
        raise BpsFormatError("the patch does not start with the BPS1 signature")

    body_end = len(data) - FOOTER_SIZE
    source_size, offset = decode_number(data, len(MAGIC), body_end)
    target_size, offset = decode_number(data, offset, body_end)
    metadata_size, offset = decode_number(data, offset, body_end)
    if offset + metadata_size > body_end:
        raise BpsFormatError("the metadata block runs past the patch body")
    metadata = data[offset : offset + metadata_size]

    for label, size in (("source", source_size), ("target", target_size)):
        if size > MAX_IMAGE_SIZE:
            raise BpsFormatError(
                f"the patch declares a {size}-byte {label}; this applier builds "
                f"images up to {MAX_IMAGE_SIZE} bytes"
            )

    source_crc32, target_crc32, patch_crc32 = struct.unpack_from("<III", data, body_end)
    # The patch checksum covers the two image checksums as well, so a footer whose
    # values were substituted cannot be made to agree by recomputing only the body.
    computed = crc32(data[:-4])
    if computed != patch_crc32:
        raise BpsFormatError(
            f"patch checksum mismatch: the file declares {patch_crc32:08x} and its "
            f"bytes compute {computed:08x}"
        )
    return BpsHeader(
        source_size=source_size,
        target_size=target_size,
        metadata=metadata,
        source_crc32=source_crc32,
        target_crc32=target_crc32,
        patch_crc32=patch_crc32,
        action_offset=offset + metadata_size,
    )


def apply(source: bytes, patch: bytes) -> bytes:
    """A source read can never exceed the source it names; the bound is checked on both sides."""
    # The walk is bounded twice: by the size the patch declares, checked before each
    # action writes, and by MAX_IMAGE_SIZE in `inspect`, so a patch cannot make the
    # applier spend an unbounded amount of memory or time reaching a target it named.
    header = inspect(patch)
    if len(source) != header.source_size:
        raise BpsSourceError(
            f"this patch is for a {header.source_size}-byte source, and the supplied "
            f"source is {len(source)} bytes"
        )
    computed_source = crc32(source)
    if computed_source != header.source_crc32:
        raise BpsSourceError(
            f"this patch is not for this source: it declares CRC-32 "
            f"{header.source_crc32:08x} and the supplied source computes "
            f"{computed_source:08x}"
        )

    data = bytes(patch)
    body_end = len(data) - FOOTER_SIZE
    output = bytearray()
    source_relative = 0
    target_relative = 0
    position = header.action_offset

    while position < body_end:
        value, position = decode_number(data, position, body_end)
        action = value & _ACTION_MASK
        length = (value >> 2) + 1

        if len(output) + length > header.target_size:
            raise BpsFormatError(
                "an action writes past the target size the patch declares"
            )

        if action == SOURCE_READ:
            if len(output) + length > header.source_size:
                raise BpsFormatError("a source read runs past the end of the source")
            output += source[len(output) : len(output) + length]
        elif action == TARGET_READ:
            if position + length > body_end:
                raise BpsFormatError("a literal run runs past the end of the patch body")
            output += data[position : position + length]
            position += length
        elif action == SOURCE_COPY:
            distance, position = decode_number(data, position, body_end)
            source_relative += _signed_offset(distance)
            if source_relative < 0 or source_relative + length > header.source_size:
                raise BpsFormatError("a source copy reads outside the source")
            output += source[source_relative : source_relative + length]
            source_relative += length
        else:
            distance, position = decode_number(data, position, body_end)
            target_relative += _signed_offset(distance)
            if target_relative < 0:
                raise BpsFormatError("a target copy reads before the output starts")
            for _ in range(length):
                if target_relative >= len(output):
                    raise BpsFormatError(
                        "a target copy reads a byte that has not been written yet"
                    )
                output.append(output[target_relative])
                target_relative += 1

    if len(output) != header.target_size:
        raise BpsFormatError(
            f"the patch declares a {header.target_size}-byte target and its actions "
            f"produce {len(output)} bytes"
        )
    computed_target = crc32(bytes(output))
    if computed_target != header.target_crc32:
        raise BpsFormatError(
            f"the rebuilt image does not match the patch: it declares CRC-32 "
            f"{header.target_crc32:08x} and the rebuild computes {computed_target:08x}"
        )
    return bytes(output)
