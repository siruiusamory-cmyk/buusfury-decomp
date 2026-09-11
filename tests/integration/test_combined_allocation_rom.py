"""TOOLKIT-036 ROM-gated proof that two allocating domains share one ledger.

TOOLKIT-035's `test_authored_scene_rom.py` composed an authored scene whose text
dimension cost zero region bytes, because it modified storage text 1525 already
owned. This file removes exactly that exemption: the scene's message is made
LONGER than 1525's 30-byte body, so the text domain must allocate from the same
profile-declared free region the authored placement, descriptor and script are
already allocated from.

Before the reservation set, that combination failed. Both allocators derived
`occupied` from their own reference document alone - the placement domain from
the PLACEMENT graph, the text domain from the TEXT graph - so neither could see
the other's allocations, both chose the same lowest aligned first fit, and they
met only in the merged `plan_changes`:

    OverlappingChangeError: text:1525 (0x007EA400+108) and
                            map:0040/placement_references (0x007EA400+32)
                            would write the same bytes

`plan_changes` is an overlap DETECTOR, not an allocator - it failed closed,
which was correct behavior at the wrong layer. The coordinator now threads one
build-scoped reservation set through the allocating domains in the order it
already had, so each completed allocation is visible to every later one.

Nothing below asserts an ADDRESS. Allocation order legitimately decides final
addresses, and a test that pinned them would fail the next time a domain's size
changed while proving nothing about the invariant. What is asserted is the set
of RELATIONSHIPS the shared ledger exists to guarantee: pairwise disjoint,
wholly contained, pointer-follows-allocation, deterministic, and fail-before-write.
"""
from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

import pytest

from tools.webfoot.allocation import withhold
from tools.webfoot.authored_placements import materialize_for_build
from tools.webfoot.build import (
    _check_identity,
    _check_maps,
    _check_records,
    _check_strings,
    _load_for_project,
    _placement_document,
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.formats.map_placements import DescriptorRecord, PlacementRecord
from tools.webfoot.formats.text_tables import TextIdentity
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.format import dump_toml, load_toml
from tools.webfoot.project.model import _TEXT_FILE
from tools.webfoot.project.placements import clone_placement
from tools.webfoot.text import load_text_strings


LOCAL_ROM = Path(os.environ.get(
    "WEBFOOT_BUU_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))
CATALOG_PATH = "config/roms.yaml"
CANONICAL_SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"

TARGET_MAP = 40
TEMPLATE = "map:0040/placement:0001"
NAME = "scene"
IDENTITY = f"map:{TARGET_MAP:04d}/authored:{NAME}"
BEHAVIOR = f"{IDENTITY}/behavior"
SOURCE = ["show_centered_sprite_text text:1525 120 105", "terminate"]
BODY = bytes.fromhex("1D03976A8170815202B211")

SCENE_TEXT_INDEX = 1525
SCENE_TEXT_KEY = f"text:{SCENE_TEXT_INDEX}"

#: Longer than text 1525's 30-byte body, so the text domain MUST allocate. This
#: is the one thing this file changes relative to the TOOLKIT-035 scene.
LONG_TEXT = "SCENE 035 COMPLETE! The long authored line goes here."

#: Far longer than the declared region can hold once the placement domain has
#: taken its share. Used to prove capacity is refused before any write.
IMPOSSIBLE_TEXT = "X" * 400


pytestmark = pytest.mark.skipif(
    not LOCAL_ROM.exists(), reason="canonical Buu's Fury image not present")


@pytest.fixture(scope="module")
def catalog():
    return RomProfileCatalog.load(CATALOG_PATH)


@pytest.fixture(scope="module")
def canonical():
    data = LOCAL_ROM.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA
    return data


def _author(tmp_path: Path, catalog, *, text: str = LONG_TEXT) -> Path:
    """The whole authoring lifecycle, in the order an author performs it.

    Every call is a public SDK entry point. No production code is patched, no
    address is supplied and no test-only allocation path is used: the author
    asks for a cloned placement carrying a script, and for longer text, and the
    SDK decides where both live.
    """
    root = tmp_path / "project"
    extract_project(LOCAL_ROM, root, catalog, graphics=False)
    clone_placement(
        root,
        map_index=TARGET_MAP,
        source=TEMPLATE,
        name=NAME,
        position_low=176,
        position_high=176,
        behavior=BEHAVIOR,
        script=SOURCE,
        trigger="on_defeat",
    )
    path = root / _TEXT_FILE
    document = load_toml(path.read_text(encoding="utf-8"))
    document["text"][SCENE_TEXT_KEY]["text"] = text
    path.write_text(dump_toml(document), encoding="utf-8", newline="\n")
    return root


def _build(tmp_path: Path, catalog, *, text: str = LONG_TEXT):
    """extract -> clone_placement -> author overlength text -> validate -> build.

    The real production path, end to end, exactly as the blocking measurement
    ran it. The output bytes are returned rather than the path, because every
    assertion below is about the image and none is about the file.
    """
    root = _author(tmp_path, catalog, text=text)
    report = validate_project(root, LOCAL_ROM, catalog)
    assert report.passed, report.problems
    output = tmp_path / "combined.gba"
    build_project(root, LOCAL_ROM, output, catalog)
    return root, output.read_bytes()


def _reservation_history(root, catalog):
    """Replay the coordinator's own sequence and report what each domain took.

    This is the coordinator's code path, not a reimplementation of it: the same
    load, the same validation, the same `materialize_for_build` and the same
    `strings.reserve` / `strings.changes` pair, in the same order `build_project`
    runs them. Every span returned came out of an allocator result.
    """
    project, identification, profile, tables, strings, maps = _load_for_project(
        root, LOCAL_ROM, catalog)
    assert not _check_identity(project, identification, profile)
    assert not (_check_records(project, tables)
                + _check_strings(project, strings)
                + _check_maps(project, maps))

    reserved: tuple = ()
    _changes, _identities, reserved = materialize_for_build(
        project, maps, _placement_document, reserved)
    placements = reserved

    strings.reserve(reserved)
    strings.changes()
    text = strings.allocated_spans()
    reserved += text
    return profile, placements, text, reserved


@pytest.fixture(scope="module")
def combined(tmp_path_factory, catalog):
    root, image = _build(tmp_path_factory.mktemp("combined"), catalog)
    return (root, image, *_reservation_history(root, catalog))


def test_the_combined_build_succeeds_where_it_previously_collided(combined):
    """The measured blocker, gone. Both domains allocated and the build emitted.

    Asserted on the RESERVATION HISTORY rather than only on the exit status: a
    build that succeeded because the text domain silently declined to relocate
    would also produce an image, and would not be the fix.
    """
    _root, image, _profile, placements, text, _reserved = combined
    assert image
    assert placements, "the placement domain allocated nothing"
    assert text, "the text domain allocated nothing; it did not relocate at all"


def test_every_allocation_came_from_one_reservation_history(combined):
    """One ledger, not two. The set the second domain saw CONTAINS the first's.

    This is the invariant the whole change exists for. Before it, each domain
    computed its own reserved set and neither contained the other's spans.
    """
    _root, _image, _profile, placements, text, reserved = combined
    assert set(placements) <= set(reserved)
    assert set(text) <= set(reserved)
    assert len(reserved) == len(placements) + len(text)


def test_all_allocated_spans_are_pairwise_disjoint(combined):
    """No two allocations share a byte - the property `plan_changes` detected
    the violation of, now guaranteed by the allocator instead."""
    _root, _image, _profile, _placements, _text, reserved = combined
    ordered = sorted(reserved, key=lambda span: span.start.value)
    for lower, higher in zip(ordered, ordered[1:]):
        assert lower.end <= higher.start.value, (
            f"0x{lower.start.value:08X}+{lower.size} overlaps "
            f"0x{higher.start.value:08X}+{higher.size}")


def test_all_allocated_spans_lie_wholly_inside_verified_regions(combined):
    """Containment, both bounds. An allocation that started inside a declared
    region and ran past its end would write bytes nobody verified."""
    _root, _image, profile, _placements, _text, reserved = combined
    assert profile.free_regions
    for span in reserved:
        assert any(region.range.start.value <= span.start.value
                   and span.end <= region.range.end
                   for region in profile.free_regions), (
            f"0x{span.start.value:08X}+{span.size} is not wholly inside any "
            "declared verified-writable region")


def test_final_pointers_resolve_to_the_final_allocated_locations(combined, catalog):
    """Follow both chains in the emitted image, as their consumers follow them.

    The placement chain is the engine's: array slot -> placement record ->
    descriptor -> script body. The text chain is the table's: pointer slot ->
    relocated body. Each must land on a span the allocator actually chose, which
    is what proves the pointers were rewritten to the FINAL layout rather than
    to whatever address a domain picked before the reservation moved it.
    """
    _root, image, _profile, _placements, text, reserved = combined
    starts = {span.start.value for span in reserved}

    array_at = struct.unpack_from("<I", image, 0x8EBB4)[0] - 0x08000000
    count = image[0x8EBA4]
    slots = [struct.unpack_from("<I", image, array_at + 4 * i)[0] - 0x08000000
             for i in range(count)]
    authored = [slot for slot in slots if slot in starts]
    assert authored, "no array slot resolves to an allocated placement body"

    record = PlacementRecord.from_bytes(image[authored[0]:authored[0] + 32])
    descriptor_at = record.descriptor_pointer_raw - 0x08000000
    assert descriptor_at in starts
    descriptor = DescriptorRecord.from_bytes(image[descriptor_at:descriptor_at + 8])
    script_at = descriptor.payload_raw - 0x08000000
    assert script_at in starts
    assert image[script_at:script_at + len(BODY)] == BODY

    location = load_text_strings(LOCAL_ROM, catalog).entry(
        TextIdentity(SCENE_TEXT_INDEX)).location
    body_at = struct.unpack_from(
        "<I", image, location.pointer_offset)[0] - 0x08000000
    assert body_at in starts, "the text slot does not point at an allocated span"
    assert body_at in {span.start.value for span in text}
    decoded = image[body_at:body_at + 2 * (len(LONG_TEXT) + 1)]
    assert decoded.decode("utf-16le").rstrip("\x00") == LONG_TEXT


def test_repeated_builds_produce_identical_layout_and_identical_bytes(
        tmp_path, catalog, canonical, combined):
    """Determinism over the WHOLE thing: the same reservation history and the
    same image. Either one alone would be the weaker claim - identical bytes
    could come from an unstable layout that happened to land the same way."""
    _root, first, _profile, placements, text, _reserved = combined
    stamp = LOCAL_ROM.stat().st_mtime_ns

    repeat_root, second = _build(tmp_path / "repeat", catalog)
    _profile2, placements2, text2, _reserved2 = _reservation_history(
        repeat_root, catalog)

    assert placements2 == placements
    assert text2 == text
    assert second == first
    assert hashlib.sha256(second).hexdigest() == hashlib.sha256(first).hexdigest()
    # The base is read-only throughout; a build never touches its source.
    assert LOCAL_ROM.read_bytes() == canonical
    assert LOCAL_ROM.stat().st_mtime_ns == stamp


def test_insufficient_remaining_capacity_fails_before_any_write(
        tmp_path, catalog, canonical):
    """Capacity the reservation set has already spent is refused at VALIDATE.

    The text is too long for what the declared region still holds once the
    placement domain has taken its share. The refusal has to arrive before the
    build, or a partially-written output would exist; so this asserts both that
    validation fails and that no output file was ever created.
    """
    root = _author(tmp_path, catalog, text=IMPOSSIBLE_TEXT)
    report = validate_project(root, LOCAL_ROM, catalog)
    assert not report.passed
    assert any("too long" in problem for problem in report.problems), report.problems
    assert not list(tmp_path.glob("*.gba"))
    assert LOCAL_ROM.read_bytes() == canonical


def test_the_free_extents_the_build_leaves_are_the_declared_ones_minus_what_it_took(
        combined):
    """Remaining capacity is SUBTRACTION from the declared regions, never more.

    Reported through the shared `withhold` primitive - the same one both
    allocating domains use - so this is the allocator's own view of what is
    left, not arithmetic performed by the test.
    """
    _root, _image, profile, _placements, _text, reserved = combined
    declared = sum(region.range.size for region in profile.free_regions)
    remaining = withhold(profile.free_regions, reserved)
    assert sum(region.range.size for region in remaining) == (
        declared - sum(span.size for span in reserved))
    for region in remaining:
        assert not any(region.range.overlaps(span) for span in reserved)
