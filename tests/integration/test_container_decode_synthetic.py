"""The one ROM-free member of the ROM-gated directory, and a committed fixture.

Every other file under ``tests/integration`` carries its own guard - a hardcoded
``roms/...`` path or an environment variable plus a module-level skip - and skips
without the canonical image. ``tests/gates.py`` marks the directory ``rom`` as a
convention; the skip is the file's own. This file is the deliberate exception: it
reads no image, needs no ``roms/`` directory, opens nothing, and never skips.

It stays in this directory rather than moving to ``tests/unit`` because the
CI selection is the point: the ``test-integration`` job runs this file by name,
and the directory axis in ``tests/gates.py`` (``integration/*`` is ``rom``) is
what keeps that name a stable statement about where ROM-gated work belongs. The
exception, and the reason the job does not collect the directory around it, are
stated in ``docs/testing.md``.

**Why a digest pin, when the round-trip tests already exist.** Kind 0 and kind 1
synthetic decode coverage is in ``tests/unit/test_logx_codec_reference.py`` and
is not duplicated here. What is not covered there is the *bytes*: a self-consistent
change to both ``pack`` and ``unpack`` keeps every round trip passing while
changing what the format emits, and this format has to keep matching what the
retail image contains. The committed fixture is the frozen witness of the
encoder's output, and each member's decoded payload is pinned separately from the
encoded form, so the two directions fail apart rather than together.

**The recipe is proven, not asserted.** ``synthetic_container()`` is the whole
recipe - two literal payloads, one stored container and one packed container -
and the first test requires the committed fixture to be byte-identical to what it
emits. The fixture therefore cannot drift from the code that claims to produce
it, and re-running the recipe is what every run of this file does.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.webfoot.formats import webfoot_lz as wl

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_containers.json"

#: Literal payloads, authored here rather than read from anywhere: no byte in the
#: fixture is ROM-derived.
STORED_PAYLOAD = b"WEBFOOT-SYNTHETIC-STORED-PAYLOAD-0123"
PACKED_PAYLOAD = b"WEBFOOT-SYNTHETIC-PACKED-PAYLOAD-" * 2

#: The kind of the packed member. Kind 1 is the kind the retail corpus uses.
PACKED_KIND = 1

#: Offset of the packed member: the stored container is its own header plus its
#: payload, and the packed container follows it immediately.
PACKED_OFFSET = wl.HEADER_SIZE + len(STORED_PAYLOAD)

#: sha256 of the committed container (not of the JSON wrapper around it, whose
#: whitespace is not part of the format) and of each member's decoded payload.
FIXTURE_SHA256 = "d6f5fa0610c8a899170cbbc6cc0e5dcb23d7926ce3c361312f16beffe1892e4d"
STORED_SHA256 = "aa222c26efc71690921004f4320f498967cda3be7dbbabe12cd376c7b96c83d2"
PACKED_SHA256 = "c55af76caba46fed0b8549b2f8f65e833b36552a90c6f506f06becc9d0b62438"


def synthetic_container() -> bytes:
    """The recipe for the committed fixture: literals in, containers out."""
    return wl.build_stored(STORED_PAYLOAD) + wl.pack(PACKED_PAYLOAD, kind=PACKED_KIND)


def committed_container() -> bytes:
    """The committed fixture exactly as it is stored on disk."""
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return bytes.fromhex(document["container_hex"])


def test_the_committed_fixture_is_byte_identical_to_the_recipe() -> None:
    assert committed_container() == synthetic_container()


def test_the_committed_fixture_is_pinned_by_digest() -> None:
    assert hashlib.sha256(committed_container()).hexdigest() == FIXTURE_SHA256


def test_the_stored_member_decodes_to_its_pinned_payload() -> None:
    member = wl.unpack(committed_container(), 0)
    assert member.kind == wl.STORED
    assert hashlib.sha256(member.data).hexdigest() == STORED_SHA256


def test_the_packed_member_decodes_to_its_pinned_payload() -> None:
    member = wl.unpack(committed_container(), PACKED_OFFSET)
    assert member.kind == PACKED_KIND
    assert hashlib.sha256(member.data).hexdigest() == PACKED_SHA256
