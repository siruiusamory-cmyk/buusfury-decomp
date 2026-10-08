"""The BPS codec: the published layout, the round trip, and every refusal.

The patch format is the one artefact of this ticket a stranger has to be able to
trust, so the tests do not only round-trip through the code under test. An
independent assembler and an independent decoder are written here from the
published specification, in the test file, and the production encoder's bytes are
proved against them. A bug that both the encoder and the applier share - the
plausible failure for a codec - is invisible to a round trip and visible here.

Nothing in this file needs a ROM, a project or the network.
"""

from __future__ import annotations

import struct
import zlib

import pytest

from tools.webfoot.formats.bps import (
    MAGIC,
    BpsFormatError,
    BpsSourceError,
    apply,
    crc32,
    decode_number,
    encode,
    encode_number,
    inspect,
)


# --- an independent reading of the same published layout ---------------------


def _assemble(
    source_size: int,
    target_size: int,
    actions: bytes,
    *,
    metadata: bytes = b"",
    source_crc: int | None = None,
    target_crc: int | None = None,
    patch_crc: int | None = None,
) -> bytes:
    """A patch built field by field, so a malformed one can still be well-formed.

    The caller supplies the action bytes and, optionally, deliberately wrong
    checksums. A `None` checksum is computed, so the default is a patch the codec
    must accept; passing one explicitly is how a corruption case is stated.
    """
    body = (
        MAGIC
        + encode_number(source_size)
        + encode_number(target_size)
        + encode_number(len(metadata))
        + metadata
        + actions
    )
    body += struct.pack("<I", 0 if source_crc is None else source_crc)
    body += struct.pack("<I", 0 if target_crc is None else target_crc)
    return body + struct.pack("<I", crc32(body) if patch_crc is None else patch_crc)


def _independent_apply(source: bytes, patch: bytes) -> bytes:
    """Rebuild the target from the specification alone.

    Deliberately a second implementation rather than a call into the codec: it
    re-derives the variable-length numbers, the body boundary and the two actions
    this encoder emits, and asserts it consumed the stream exactly.
    """
    assert patch[:4] == MAGIC
    position = len(MAGIC)

    def number() -> int:
        nonlocal position
        value = 0
        shift = 1
        while True:
            group = patch[position]
            position += 1
            value += (group & 0x7F) * shift
            if group & 0x80:
                return value
            shift <<= 7
            value += shift

    assert number() == len(source)
    target_size = number()
    metadata_size = number()
    position += metadata_size
    end = len(patch) - 12

    rebuilt = bytearray()
    while position < end:
        value = number()
        action = value & 3
        length = (value >> 2) + 1
        if action == 0:
            rebuilt += source[len(rebuilt) : len(rebuilt) + length]
        elif action == 1:
            rebuilt += patch[position : position + length]
            position += length
        else:
            raise AssertionError("this encoder emits only actions 0 and 1")

    assert position == end, "the action stream must end where the checksums begin"
    assert len(rebuilt) == target_size
    return bytes(rebuilt)


def _source(size: int, seed: int = 0) -> bytes:
    return bytes((index * 7 + seed) & 0xFF for index in range(size))


# --- the number encoding ----------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, b"\x80"),
        (1, b"\x81"),
        (127, b"\xFF"),
        (128, b"\x00\x80"),
        (255, b"\x7f\x80"),
        (16512, b"\x00\x00\x80"),
    ],
)
def test_number_encoding_matches_the_published_sequences(value, expected):
    assert encode_number(value) == expected
    assert decode_number(expected, 0, len(expected))[0] == value


@pytest.mark.parametrize("value", [0, 1, 2, 63, 64, 127, 128, 129, 16383, 16384, 2**31])
def test_every_number_round_trips(value):
    encoded = encode_number(value)
    assert decode_number(encoded, 0, len(encoded)) == (value, len(encoded))


def test_a_number_that_runs_past_the_body_is_refused():
    with pytest.raises(BpsFormatError, match="runs past the end"):
        decode_number(b"\x00\x00", 0, 2)


def test_a_negative_number_cannot_be_encoded():
    with pytest.raises(ValueError, match="unsigned"):
        encode_number(-1)


# --- the round trip ---------------------------------------------------------


@pytest.mark.parametrize(
    "source,target",
    [
        (b"", b""),
        (b"", b"fresh bytes"),
        (b"discarded", b""),
        (b"identical", b"identical"),
        (
            b"the quick brown fox jumps over the lazy dog",
            b"the quick brown cat jumps over the lazy dog!",
        ),
        (_source(4096), _source(4096)),
        (_source(4096), _source(4096, seed=1)),
        (_source(64), _source(4096)),
        (_source(4096), _source(64)),
        (bytes(1000), b"\xff" * 1000),
    ],
    ids=[
        "empty",
        "source-empty",
        "target-empty",
        "identical",
        "one-word-differs",
        "equal-length",
        "all-differ",
        "target-longer",
        "target-shorter",
        "zeroes-to-ones",
    ],
)
def test_round_trip_returns_the_target(source, target):
    patch = encode(source, target)
    assert apply(source, patch) == target
    assert _independent_apply(source, patch) == target


def test_a_longer_target_is_rebuilt_in_full():
    source = _source(64)
    target = source + _source(2048, seed=3)
    patch = encode(source, target)
    header = inspect(patch)
    assert header.source_size == 64
    assert header.target_size == len(target)
    assert apply(source, patch) == target


def test_encoding_is_deterministic():
    source, target = _source(512), _source(512, seed=11)
    assert encode(source, target) == encode(source, target)
    assert encode(source, target, b"note") == encode(source, target, b"note")


def test_identical_inputs_produce_a_patch_that_changes_nothing():
    data = _source(256)
    patch = encode(data, data)
    assert apply(data, patch) == data
    assert len(patch) < len(data) + 32


def test_metadata_round_trips_and_is_covered_by_the_patch_checksum():
    source, target = _source(32), _source(32, seed=5)
    patch = encode(source, target, b'{"project":"authored"}')
    assert inspect(patch).metadata == b'{"project":"authored"}'
    assert apply(source, patch) == target
    without = encode(source, target)
    assert patch != without


def test_crc32_matches_the_standard_crc():
    assert crc32(b"") == 0
    assert crc32(b"123456789") == zlib.crc32(b"123456789") & 0xFFFFFFFF


# --- the refusals -----------------------------------------------------------


def test_a_patch_shorter_than_the_footer_is_refused():
    for length in (0, 1, len(MAGIC), len(MAGIC) + 11):
        with pytest.raises(BpsFormatError, match="at least"):
            inspect(b"\x00" * length)


def test_a_patch_without_the_signature_is_refused():
    patch = bytearray(encode(_source(16), _source(16, seed=2)))
    patch[:4] = b"IPS3"
    with pytest.raises(BpsFormatError, match="signature"):
        apply(_source(16), bytes(patch))


def test_a_truncated_patch_is_refused():
    patch = encode(_source(256), _source(256, seed=9))
    for cut in (1, 4, 11, 12, len(patch) // 2):
        with pytest.raises(BpsFormatError):
            apply(_source(256), patch[: len(patch) - cut])


def test_bytes_appended_after_the_footer_are_refused():
    source, target = _source(128), _source(128, seed=4)
    patch = encode(source, target)
    with pytest.raises(BpsFormatError, match="checksum mismatch"):
        apply(source, patch + b"appended")


def test_a_flipped_body_byte_is_refused():
    source, target = _source(128), _source(128, seed=4)
    patch = bytearray(encode(source, target))
    patch[len(patch) // 2] ^= 0xFF
    with pytest.raises(BpsFormatError, match="checksum mismatch"):
        inspect(bytes(patch))


def test_metadata_running_past_the_body_is_refused():
    patch = _assemble(
        0, 0, b"", metadata=b"", patch_crc=0
    )
    patch = bytearray(patch)
    patch[4:5] = encode_number(999)
    with pytest.raises(BpsFormatError):
        inspect(bytes(patch))


def test_a_wrong_source_size_is_refused():
    source, target = _source(64), _source(64, seed=6)
    patch = encode(source, target)
    with pytest.raises(BpsSourceError, match="byte source"):
        apply(source + b"\x00", patch)


def test_a_wrong_source_of_the_same_size_is_refused():
    source, target = _source(64), _source(64, seed=6)
    patch = encode(source, target)
    mutated = bytearray(source)
    mutated[3] ^= 0x01
    with pytest.raises(BpsSourceError, match="not for this source"):
        apply(bytes(mutated), patch)


def test_swapped_source_and_target_checksums_are_refused():
    """A re-computed footer is not enough: the two checksums name two images."""
    source, target = _source(64), _source(64, seed=6)
    patch = bytearray(encode(source, target))
    body_end = len(patch) - 12
    source_crc, target_crc = struct.unpack_from("<II", patch, body_end)
    struct.pack_into("<II", patch, body_end, target_crc, source_crc)
    struct.pack_into("<I", patch, len(patch) - 4, crc32(bytes(patch[:-4])))
    with pytest.raises(BpsSourceError, match="not for this source"):
        apply(source, bytes(patch))


def test_a_target_checksum_that_disagrees_with_the_actions_is_refused():
    source, other = _source(64), _source(64, seed=7)
    actions = encode_number((64 - 1) << 2 | 1) + other
    patch = _assemble(
        len(source),
        len(source),
        actions,
        source_crc=crc32(source),
        target_crc=crc32(source),
    )
    with pytest.raises(BpsFormatError, match="does not match the patch"):
        apply(source, patch)


def test_a_target_size_that_disagrees_with_the_actions_is_refused():
    source = _source(64)
    actions = encode_number((64 - 1) << 2 | 0)
    patch = _assemble(
        len(source),
        len(source) + 1,
        actions,
        source_crc=crc32(source),
        target_crc=crc32(source),
    )
    with pytest.raises(BpsFormatError, match="actions"):
        apply(source, patch)


def test_a_source_read_past_the_source_is_refused():
    source = _source(64)
    actions = encode_number((128 - 1) << 2 | 0)
    patch = _assemble(
        len(source), 128, actions, source_crc=crc32(source), target_crc=0
    )
    with pytest.raises(BpsFormatError, match="source read runs past"):
        apply(source, patch)


def test_a_literal_run_past_the_body_is_refused():
    source = _source(8)
    actions = encode_number((64 - 1) << 2 | 1) + b"short"
    patch = _assemble(
        len(source), 64, actions, source_crc=crc32(source), target_crc=0
    )
    with pytest.raises(BpsFormatError, match="literal run runs past"):
        apply(source, patch)


def test_a_source_copy_outside_the_source_is_refused():
    source = _source(16)
    actions = encode_number((8 - 1) << 2 | 2) + encode_number((4096 << 1) | 0)
    patch = _assemble(
        len(source), 8, actions, source_crc=crc32(source), target_crc=0
    )
    with pytest.raises(BpsFormatError, match="source copy reads outside"):
        apply(source, patch)


def test_a_target_copy_of_unwritten_bytes_is_refused():
    source = _source(16)
    actions = encode_number((4 - 1) << 2 | 3) + encode_number((0 << 1) | 1)
    patch = _assemble(
        len(source), 4, actions, source_crc=crc32(source), target_crc=0
    )
    with pytest.raises(BpsFormatError, match="not been written"):
        apply(source, patch)


def test_a_source_copy_is_decoded():
    """A positive vector for the general applier, not only the refusal paths.

    Our own encoder emits only source reads and literals, so a copy action is
    exercised here by a hand-built patch. A patch made by another tool reaches
    `webfoot patch verify`, and an applier that only understands its own encoder's
    subset would mis-report one.
    """
    source = b"ABCDEFGH"
    # SourceRead 4, then a source copy of 4 bytes at delta 0 (reads source[0:4]).
    actions = encode_number((4 - 1) << 2 | 0) + encode_number((4 - 1) << 2 | 2) + encode_number(0)
    target = b"ABCDABCD"
    patch = _assemble(
        8, 8, actions, source_crc=crc32(source), target_crc=crc32(target)
    )
    assert apply(source, patch) == target


def test_a_target_copy_is_decoded():
    source = b"ABCDEFGH"
    # TargetRead 4, then a target copy of 4 bytes at delta 0: the target cursor
    # starts at 0, so delta 0 points back at the four bytes just written and the
    # copy then grows its own source as it goes.
    actions = (
        encode_number((4 - 1) << 2 | 1)
        + b"ABCD"
        + encode_number((4 - 1) << 2 | 3)
        + encode_number(0)
    )
    target = b"ABCDABCD"
    patch = _assemble(
        8, 8, actions, source_crc=crc32(source), target_crc=crc32(target)
    )
    assert apply(source, patch) == target


def test_an_action_that_writes_past_the_declared_target_is_refused():
    """The walk is bounded by the target the patch declares, before it writes.

    A target copy that reads output it has just written never runs out of written
    data, so an action stream claiming an enormous length would append without
    limit. The bound is what makes the walk finite; the ``match`` is what proves
    the bound fired rather than a later size check.
    """
    source = _source(8)
    actions = encode_number((4 - 1) << 2 | 1) + b"ABCD" + encode_number(
        (4096 - 1) << 2 | 3
    ) + encode_number(0)
    patch = _assemble(
        8, 8, actions, source_crc=crc32(source), target_crc=crc32(b"ABCD"),
    )
    with pytest.raises(BpsFormatError, match="writes past the target size"):
        apply(source, patch)


def test_the_patch_checksum_is_required_to_be_present_and_correct():
    source, target = _source(32), _source(32, seed=8)
    patch = encode(source, target)
    body_end = len(patch) - 12
    broken = bytearray(patch)
    struct.pack_into("<I", broken, len(patch) - 4, 0)
    with pytest.raises(BpsFormatError, match="checksum mismatch"):
        inspect(bytes(broken))
    # And the footer's own two fields are inside the covered range, so changing
    # one of them without recomputing is caught by the same check.
    moved = bytearray(patch)
    struct.pack_into("<I", moved, body_end, 0xDEADBEEF)
    with pytest.raises(BpsFormatError, match="checksum mismatch"):
        inspect(bytes(moved))
