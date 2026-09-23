"""The compressed-dialogue write path must reject a payload retail cannot stop.

CQA-02-PACKED-STREAM-TERMINATION-001. The retail packed decoder carries no output
counter and stops only on the stream's own escape, so the dialogue build - the one
shipped consumer of `webfoot_lz.pack` - must never plan a payload that reaches its
declared length without reaching that escape. These tests drive the real shipping
planning entry point, `compressed_dialogue.materialize_dialogues` (the function
`build.build_project` calls), against a synthetic image that reproduces the
measured retail layout of the `goku-greeting` target: the same container-table
offset, selector and decoded span, so the container-table arithmetic and the
allocation branch under test are the production ones.

Nothing here is ROM-derived. The image is zero fill with one packed container and
two table pointers; the only real bytes in it are the ones this file builds.

The escape's *absence* is reproduced rather than simulated: the pre-fix encoder is
obtained by disabling `_WordBitWriter.write_end_marker` through monkeypatch, which
is what the ticket's M2 check does.
"""

from __future__ import annotations

import pytest

from tools.webfoot import compressed_dialogue
from tools.webfoot.allocation import InsufficientSpaceError
from tools.webfoot.binary import FileOffset
from tools.webfoot.compressed_dialogue import (CompressedDialogueError,
                                                materialize_dialogues)
from tools.webfoot.formats import webfoot_lz as wl
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog


PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: The `goku-greeting` target's measured identity, as the registry holds it.
TABLE_OFFSET = 0x7B5B64
SELECTOR = 1
TABLE_SLOT = TABLE_OFFSET + SELECTOR * 4          # 0x7B5B68
NEXT_SLOT = TABLE_SLOT + 4                        # 0x7B5B6C
DECODED_START = 0x132
DECODED_LENGTH = 0x20
DECODED_END = DECODED_START + DECODED_LENGTH

#: The synthetic image must extend past the real container-table slot; everything
#: in it except the container and the two pointers is zero fill.
CONTAINER_OFFSET = 0x1000
IMAGE_SIZE = TABLE_SLOT + 8

ORIGINAL_TEXT = "Good luck, Goku!"
REPLACEMENT_TEXT = "Nice work, Goku!"             # exactly DECODED_LENGTH bytes
TARGET_NAME = "goku-greeting"

#: Chooses a decoded body whose pre-fix encoding ends with fewer than twelve bits
#: of padding, i.e. one of the 140/406 measured dialogue cases whose escape had to
#: come from the bytes after the payload rather than from the payload itself.
#: `test_the_pre_fix_dialogue_payload_really_lacks_its_escape` asserts that it does.
FILLER = 20


@pytest.fixture(scope="module")
def profile():
    catalog = RomProfileCatalog.load("config/roms.yaml")
    return next(item for item in catalog.profiles if item.id == PROFILE_ID)


def _original_decoded() -> bytes:
    data = bytearray(bytes((index * 37 + FILLER) % 256 for index in range(DECODED_END)))
    data[DECODED_START:DECODED_END] = ORIGINAL_TEXT.encode("utf-16le")
    return bytes(data)


def _replaced_decoded() -> bytes:
    original = _original_decoded()
    return (original[:DECODED_START]
            + REPLACEMENT_TEXT.encode("utf-16le")
            + original[DECODED_END:])


def _pointer(offset: int) -> bytes:
    return (0x08000000 + offset).to_bytes(4, "little")


def _image(container: bytes, *, allocation: int) -> bytes:
    """One synthetic image: a packed container plus the two container-table words.

    ``allocation`` is the distance from the container to the next table entry,
    which is the retail allocation the in-place branch is measured against.
    """
    assert allocation >= len(container)
    image = bytearray(IMAGE_SIZE)
    image[CONTAINER_OFFSET:CONTAINER_OFFSET + len(container)] = container
    image[TABLE_SLOT:TABLE_SLOT + 4] = _pointer(CONTAINER_OFFSET)
    image[NEXT_SLOT:NEXT_SLOT + 4] = _pointer(CONTAINER_OFFSET + allocation)
    return bytes(image)


def _payload_without_marker(monkeypatch, payload: bytes) -> bytes:
    """The pre-fix encoder's output: `pack` with the escape emission removed."""
    monkeypatch.setattr(wl._WordBitWriter, "write_end_marker", lambda self: None)
    try:
        return wl.pack(payload)
    finally:
        monkeypatch.undo()


def _accepts(payload: bytes) -> bool:
    try:
        wl.validate_retail_termination(payload)
    except wl.ContainerError:
        return False
    return True


def _plan(profile, container: bytes, allocation: int, replacement: str = REPLACEMENT_TEXT):
    image = _image(container, allocation=allocation)
    results, reserved, generated_image, provenance = materialize_dialogues(
        image, profile, {TARGET_NAME: replacement}
    )
    return results[0], reserved, generated_image, provenance


# --- the escape is present, and it is what the fit decision is charged ---------


def test_the_dialogue_planner_plans_a_self_terminating_payload(profile):
    """The corrected path: the planned payload reaches the escape inside itself."""
    replaced = _replaced_decoded()
    payload = wl.pack(replaced)
    build, _reserved, _image_bytes, _provenance = _plan(
        profile, payload, allocation=len(payload)
    )
    assert build.payload == payload
    assert build.allocation is None, "an exact fit stays in place"
    assert wl.validate_retail_termination(build.payload).data == replaced
    assert wl.unpack(build.payload, 0).data[DECODED_START:DECODED_END] == (
        REPLACEMENT_TEXT.encode("utf-16le")
    )
    assert build.changes, "the in-place branch still emits its ByteChange"


def test_the_marker_is_charged_to_the_dialogue_fit_decision(profile, monkeypatch):
    """An allocation that fits the pre-marker length alone must not be used.

    The container in this image is the *pre-fix* encoding and the next table entry
    sits exactly at its end, so the retail allocation is precisely the pre-marker
    length: the old size fitted by construction and only the terminator pushes the
    corrected payload past it. An implementation that kept pre-marker length
    bookkeeping - or subtracted the terminator so the old allocation would still
    fit - would take the in-place branch here instead of relocating.
    """
    replaced = _replaced_decoded()
    before_marker = _payload_without_marker(monkeypatch, replaced)
    after_marker = wl.pack(replaced)
    assert len(after_marker) > len(before_marker), "this case must be marker-costing"
    assert not _accepts(before_marker), "the pre-fix payload is not self-terminating"

    build, _reserved, generated_image, provenance = _plan(
        profile, before_marker, allocation=len(before_marker)
    )
    assert build.old_allocation == len(before_marker)
    assert build.payload == after_marker
    assert len(build.payload) > build.old_allocation
    assert build.allocation is not None, "the corrected size must drive relocation"
    assert build.allocation.range.start.value == 0x800000
    assert build.allocation.range.size >= len(build.payload)
    assert provenance and provenance[0].allocated_range == build.allocation.range
    assert generated_image is not None
    # The relocated payload is still self-terminating and still carries the text.
    assert wl.validate_retail_termination(build.payload).data == replaced


# --- the guard is wired, and it fails closed ----------------------------------


def test_the_pre_fix_dialogue_payload_really_lacks_its_escape(monkeypatch):
    """Positive control for the guard tests below.

    If this ever stops holding, the case in this file no longer reproduces the
    defect the guard exists for, and the guard tests would be passing for the wrong
    reason.
    """
    before_marker = _payload_without_marker(monkeypatch, _replaced_decoded())
    assert wl.unpack(before_marker, 0).data == _replaced_decoded()
    assert not _accepts(before_marker)


def test_the_write_path_refuses_a_dialogue_payload_without_an_in_stream_escape(
    profile, monkeypatch
):
    """M2, kept as a permanent test: bypass marker emission and planning stops.

    The image gives the payload room to spare, so without the guard this exact
    payload would be planned in place and reported as a successful build. A planner
    that merely warned, or that fell back to ordinary expected-length decoding,
    would return a build here; the assertion is an exception instead, raised before
    any ByteChange, allocation or plan can be produced.
    """
    before_marker = _payload_without_marker(monkeypatch, _replaced_decoded())
    monkeypatch.setattr(compressed_dialogue, "pack", lambda payload: before_marker)

    with pytest.raises(CompressedDialogueError) as excinfo:
        _plan(profile, before_marker, allocation=len(before_marker) + 4096)
    message = str(excinfo.value)
    assert TARGET_NAME in message
    assert "retail termination contract" in message
    assert isinstance(excinfo.value.__cause__, wl.ContainerError)


def test_the_guard_runs_before_the_allocation_branch(profile, monkeypatch):
    """A refused payload never reaches the allocator.

    The forced payload here is larger than the container table allows, so an
    implementation that asked the allocator before validating would reach
    `allocate` and take the relocation branch. It must be the codec guard that
    refuses, and it must refuse first.
    """
    before_marker = _payload_without_marker(monkeypatch, _replaced_decoded())
    oversized = before_marker + b"\xFF" * 64
    monkeypatch.setattr(compressed_dialogue, "pack", lambda payload: oversized)

    def explode(*_args, **_kwargs):
        raise AssertionError("the allocator must not be consulted")

    monkeypatch.setattr(compressed_dialogue, "allocate", explode)
    with pytest.raises(CompressedDialogueError):
        _plan(profile, before_marker, allocation=len(before_marker))


def test_a_short_replacement_is_still_refused_by_the_pre_existing_rule(profile):
    """Termination validation did not replace, and did not loosen, the length rule."""
    payload = wl.pack(_replaced_decoded())
    with pytest.raises(CompressedDialogueError, match="durable handle requires"):
        _plan(profile, payload, allocation=len(payload), replacement="too short")


def test_an_unallocatable_payload_still_fails_cleanly(profile, monkeypatch):
    """Refusal stays clean when the profile permits no allocation for the payload.

    Termination validation is not the only refusal on this path: a payload that
    passes it must still fail through the ordinary allocation error rather than
    being written somewhere it does not belong.
    """
    before_marker = _payload_without_marker(monkeypatch, _replaced_decoded())
    image = _image(before_marker, allocation=len(before_marker))
    reserved = (RomRange(FileOffset(0x800000), 0x800000),)
    with pytest.raises(InsufficientSpaceError):
        materialize_dialogues(
            image, profile, {TARGET_NAME: REPLACEMENT_TEXT}, reserved=reserved
        )
