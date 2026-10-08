"""The BPS patch format: encode a source/target pair, apply one back.

BPS is the ecosystem's interchange format for a single binary difference. A patch
is a small file that turns one exact input image into one exact output image, and
it carries the CRC-32 of both so an applier can refuse a file it was not made for.
The format is published and in the public domain, so this repository implements it
directly instead of depending on a patch library: the encoder below is a few dozen
lines, the format has no versioning of its own, and a dependency has to earn its
place. The consequence to keep in mind is that the correctness of these bytes
rests on the published layout and on the round-trip proof in
`tests/unit/test_bps.py`, not on someone else's well-tested parser.

This module is a pure codec over `bytes`: no I/O, no file paths, no ROM profile,
no project. `tools.webfoot.patch` owns the product behaviour around it, and the
format facts stay here so a second caller cannot restate them differently.

Layout, from the published specification:

    "BPS1"
    number  source size
    number  target size
    number  metadata size
    bytes   metadata
    actions
    uint32  source CRC-32, little endian
    uint32  target CRC-32, little endian
    uint32  patch CRC-32, little endian, over every byte before it

A *number* is a variable-length unsigned integer: seven bits per byte, low group
first, high bit marking the last byte. An action is one number whose low two bits
name the action and whose remaining bits encode its length minus one. Two actions
read the source (a run of unchanged bytes, and a copy from a chosen offset) and two
write literal bytes (into the target, and a repeat of output already written).

Because the patch CRC-32 covers the two checksums before it, a patch cannot be
assembled from a valid body and a substituted footer without the change being
detected; `inspect` is therefore the single gate every reader passes through.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
import zlib

#: The four-byte signature every patch starts with.
MAGIC = b"BPS1"

#: The three trailing CRC-32 values, the last of which covers all the bytes before it.
FOOTER_SIZE = 12

#: The four action codes. 0 and 1 are the only two this module's encoder emits.
SOURCE_READ = 0
TARGET_READ = 1
SOURCE_COPY = 2
TARGET_COPY = 3
_ACTION_MASK = 0x03

#: The widest a number may get before the file is refused. The format is read with
#: 64-bit arithmetic by its reference implementation, so anything past that is a
#: malformed file rather than a large one, and refusing here keeps a corrupt header
#: from growing an unbounded integer while it is being decoded.
_MAX_SHIFT = 1 << 70

#: The largest image this applier will build, and the largest source it will accept.
#: The format allows far more, and this toolkit's subject is a 32 MiB address space,
#: so the ceiling is a deliberate domain limit rather than a format rule: without it,
#: a patch may declare a target of any size and a valid-checksum patch from a
#: stranger would spend the machine's memory and time reaching it. A caller that
#: genuinely needs a larger image must raise this and say why.
MAX_IMAGE_SIZE = 32 * 1024 * 1024


class BpsError(ValueError):
    """Base error for encoding, reading or applying a BPS patch."""


class BpsFormatError(BpsError):
    """The bytes are not a well-formed BPS patch, or a checksum disagrees."""


class BpsSourceError(BpsError):
    """The supplied source image is not the one this patch was made for."""


@dataclass(frozen=True, slots=True)
class BpsHeader:
    """What a patch declares about itself, with its own checksum already verified."""

    source_size: int
    target_size: int
    metadata: bytes
    source_crc32: int
    target_crc32: int
    patch_crc32: int
    #: Where the action stream starts, i.e. just past the metadata block.
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
        # The continuation byte carries the next group's base implicitly, so the
        # remaining value is decremented before it is split again. Without this the
        # encoding would not be injective and two numbers would share bytes.
        value -= 1


def decode_number(data: bytes, offset: int, limit: int) -> tuple[int, int]:
    """Read one number at `offset`, returning it and the offset after it.

    `limit` bounds the readable body, so a malformed field cannot run into the
    checksum footer and still be accepted as a number.
    """
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
    """The signed distance a source or target copy moves its cursor by."""
    distance = value >> 1
    return -distance if value & 1 else distance


def encode(source: bytes, target: bytes, metadata: bytes = b"") -> bytes:
    """The patch that turns `source` into `target`, deterministically.

    One forward pass over the length the two images share: a SourceRead for every
    run of equal bytes, a TargetRead for every run that differs, and a final
    TargetRead for a target longer than its source. Nothing searches for repeated
    spans, so no SourceCopy or TargetCopy is emitted and the output is a pure
    function of the two inputs - the same bytes on any platform and any Python
    version, which is what a reproducible build needs. The ceiling that buys is
    patch size; an encoder that searched for repeated runs would emit a smaller
    patch, and that is the only thing it would improve.

    A target shorter than its source is legal and is covered by the shared prefix
    alone. Identical inputs produce a valid patch that changes nothing; refusing
    that is the caller's policy, not the format's.
    """
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
    """The header and footer of `patch`, or a refusal.

    Every reader starts here, so the patch's own CRC-32 is checked before any
    other fact in the file is believed, including the sizes and the two image
    checksums the rest of the reading depends on.
    """
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
    """Rebuild the target from `source` and `patch`, or refuse.

    This is the whole verification path, and it fails closed at every step: the
    patch's own checksum (in `inspect`), then the source's size and CRC-32, then a
    bounded walk of the action stream, then the target's size and CRC-32. The
    source is read at the output offset the format has already written to, so a
    source read can never exceed the source it names; the same bound is checked
    again here rather than trusted.
    """
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

        # Every action appends exactly `length` bytes, so this single bound keeps
        # the whole walk inside the target the patch declares. It is not an
        # optimisation: without it a crafted patch that passes its own checksum can
        # claim an enormous length, and a target copy that reads output it has just
        # written advances its read cursor and the output together, so it never runs
        # out of written data and the loop never ends.
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
            # The cursor follows the copy, one step per byte read. Without this the
            # next source copy would re-read the same window, and a patch from an
            # encoder that emits runs of source copies would be mis-decoded rather
            # than applied.
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
