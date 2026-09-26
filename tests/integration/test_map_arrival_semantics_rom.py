"""ROM-gated proofs for the arrival and facing semantics.

MAP-WARP-ARRIVAL-SEMANTICS-001. These are the claims a synthetic image cannot
settle: that the canonical corpus really does split into two classes with
different arrival semantics, that the 566-class pair lands at the destination's
return door, that the 169-class transform is a different thing, that a derived
arrival comes from the return door, and that the default facing reproduces the
corpus's own values on the links where both are known.

The canonical image is opened read-only and re-hashed at the end. The whole file
skips cleanly when the private image is absent.
"""

from __future__ import annotations

import glob
import hashlib
import os
from pathlib import Path

import pytest

from tools.webfoot.formats.map_transitions import (
    FACING_NAMES,
    FACING_NORTH,
    TRANSITION_CLASS_A_RAW,
    TRANSITION_CLASS_B_RAW,
    MapTransitionValueError,
    TransitionArrival,
    TransitionRegion,
)
from tools.webfoot.map_transitions import (
    TransitionFieldError,
    TransitionIdentity,
    load_map_transitions,
)
from tools.webfoot.maps import MapIdentity
from tools.webfoot.profile import RomProfileCatalog

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
CATALOG = "config/roms.yaml"
CLASS_A_COUNT = 566
CLASS_B_COUNT = 169
VOLCANO = MapIdentity(378)
MAP_39 = MapIdentity(39)
MAP_40 = MapIdentity(40)
MAP_41 = MapIdentity(41)
TARGET = TransitionIdentity(MAP_40, 0)


def _rom_path() -> str:
    """The canonical image, or a skip. ``LOGX_CANONICAL_ROM`` overrides the path.

    The override exists for the same reason the other ROM-gated files have it: a
    ticket worktree never carries the ignored image, so a run there points at the
    main checkout's copy and still never writes to it.
    """
    override = os.environ.get("LOGX_CANONICAL_ROM")
    if override:
        path = Path(override)
        if not path.is_file():
            pytest.skip(f"LOGX_CANONICAL_ROM is not a file: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != CANONICAL_SHA256:
            pytest.skip("LOGX_CANONICAL_ROM is not the canonical image")
        return str(path)
    matches = sorted(glob.glob(os.path.join("roms", "*Buu*.gba")))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(Path(matches[0]).read_bytes()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these facts target")
    return matches[0]


@pytest.fixture(scope="module")
def rom() -> str:
    return _rom_path()


@pytest.fixture(scope="module")
def authority(rom: str):
    return load_map_transitions(rom, RomProfileCatalog.load(CATALOG))


@pytest.fixture
def fresh(rom: str):
    """A corpus per test, because the tests below stage edits on it."""
    return load_map_transitions(rom, RomProfileCatalog.load(CATALOG))


def contains(region: TransitionRegion, point: TransitionArrival) -> bool:
    (low_x, high_x), (low_y, high_y) = region.first, region.second
    return low_x <= point.x <= high_x and low_y <= point.y <= high_y


# --- the class split, on the real corpus -------------------------------------


def test_the_canonical_corpus_splits_into_two_classes(authority) -> None:
    counts: dict[int, int] = {}
    for entry in authority.entries():
        counts[entry.record.class_raw] = counts.get(entry.record.class_raw, 0) + 1
    assert counts[TRANSITION_CLASS_A_RAW] == CLASS_A_COUNT
    assert counts[TRANSITION_CLASS_B_RAW] == CLASS_B_COUNT
    # ...and the split is exactly the one that governs the arrival reading.
    raw_pair = sum(1 for e in authority.entries() if e.record.has_raw_arrival_pair)
    assert raw_pair == CLASS_A_COUNT
    assert raw_pair != authority.record_count


def test_the_566_class_arrival_lands_at_the_destination_return_door(authority) -> None:
    """The pair is the door the player comes back through, measured."""
    checked = 0
    for source in (38, 39, 40, 41):
        for entry in authority.for_map(MapIdentity(source)):
            if not entry.record.has_raw_arrival_pair:
                continue
            arrival = entry.record.arrival
            if arrival is None:
                continue
            destination = authority.destination(entry.identity)
            doors = authority.reciprocal_doors(entry.identity.source, destination)
            if not doors:
                continue
            assert any(contains(door.record.region, arrival) for door in doors), (
                f"{entry.identity.key} arrival {arrival} is not at any door back to "
                f"{entry.identity.source}"
            )
            checked += 1
    assert checked >= 4


def test_the_169_class_pair_is_not_an_arrival_on_its_own(authority) -> None:
    """Its stored pair is a delta, so the transform is what produces a point."""
    entry = authority.entry(TransitionIdentity(MapIdentity(39), 0))
    assert entry.record.class_raw == TRANSITION_CLASS_B_RAW
    assert not entry.record.has_raw_arrival_pair
    # The stored bytes are readable; asking for them as an arrival is not.
    stored = entry.record.raw_coordinate_pair
    assert stored is not None
    # The scene origin is an input, so two origins give two different arrivals.
    first = entry.record.arrival_relative(0, 0)
    second = entry.record.arrival_relative(100, 100)
    assert first != second
    assert second.x - first.x == 100 and second.y - first.y == 100
    with pytest.raises(MapTransitionValueError):
        # And a 566 record refuses the transform, because its pair is already a
        # point - the two families are never treated as interchangeable.
        authority.entry(TARGET).record.arrival_relative(0, 0)


def test_a_169_class_record_refuses_to_be_an_arrival(authority, fresh) -> None:
    """The real corpus's second class must not answer as a point anywhere.

    This is the fail-closed half: a 169 record's pair is a delta, and a delta is
    inside every map's bounds, so an accessor that returned it as an arrival
    would be accepted by the bound check and written by a build.
    """
    entry = authority.entry(TransitionIdentity(MapIdentity(39), 0))
    assert entry.record.class_raw == TRANSITION_CLASS_B_RAW
    stored = entry.record.raw_coordinate_pair
    assert stored is not None
    with pytest.raises(MapTransitionValueError):
        entry.record.arrival
    with pytest.raises(MapTransitionValueError):
        authority.arrival(entry.identity)
    with pytest.raises(TransitionFieldError):
        authority.set_arrival(entry.identity, TransitionArrival(x=1, y=1))
    with pytest.raises(TransitionFieldError):
        fresh.derive_arrival(entry.identity, MapIdentity(38))
    # The delta is still readable as bytes, which is what the round trip needs.
    assert fresh.entry(entry.identity).record.raw_coordinate_pair == stored


# --- deriving a safe arrival -------------------------------------------------


def test_deriving_an_arrival_prefers_the_value_the_game_already_uses(fresh) -> None:
    """Map 41 leads back to map 40, so an arrival can be derived - and is.

    Where the source map already has a record reaching the same destination, its
    stored arrival is the engine's own answer for that link and is preferred over
    the door centre. Failing that, the door's centre is used.
    """
    sibling = fresh.entry(TransitionIdentity(MAP_40, 1))
    assert fresh.destination(sibling.identity) == MAP_41
    derived = fresh.derive_arrival(TARGET, MAP_41)
    assert derived == sibling.record.arrival, (
        "the game's own arrival for this link must be preferred"
    )
    doors = fresh.reciprocal_doors(MAP_40, MAP_41)
    assert len(doors) == 1
    (low_x, high_x), (low_y, high_y) = doors[0].record.region.first, doors[0].record.region.second
    assert low_x <= derived.x <= high_x and low_y <= derived.y <= high_y
    width, height = fresh.destination_bounds(MAP_41)
    assert 0 <= derived.x < width and 0 <= derived.y < height


def test_deriving_refuses_a_destination_with_no_return_door(fresh) -> None:
    """Volcano has no record back to map 40, so nothing can be derived."""
    assert fresh.reciprocal_doors(MAP_40, VOLCANO) == ()
    with pytest.raises(TransitionFieldError, match="no record leading back"):
        fresh.derive_arrival(TARGET, VOLCANO)


def test_an_arrival_off_the_destination_is_refused(fresh) -> None:
    fresh.set_destination(TARGET, VOLCANO)
    width, height = fresh.destination_bounds(VOLCANO)
    with pytest.raises(TransitionFieldError, match="off the map"):
        fresh.set_arrival(TARGET, TransitionArrival(x=width + 1, y=10))
    with pytest.raises(TransitionFieldError, match="off the map"):
        fresh.set_arrival(TARGET, TransitionArrival(x=10, y=height + 1))
    # The retired value - map 39's door - is exactly the case that softlocked.
    with pytest.raises(TransitionFieldError, match="off the map"):
        fresh.set_arrival(TARGET, TransitionArrival(x=599, y=196))


# --- the default facing ------------------------------------------------------


def test_the_canonical_corpus_usually_states_no_arrival_facing(fresh) -> None:
    """The common case is SILENCE, and that silence is the behaviour that bit.

    A ``+0x10`` whose high nibble is zero carries no arrival-facing override:
    ``0800763A``/``0800763C`` test ``v & 0xF0`` and only a non-zero result writes a
    facing. So for the ordinary record the engine leaves the actor facing whatever
    it was already walking - which is precisely the reported symptom of a retarget
    leaving the sprite walking West out of a south door.

    The low two bits are the door gate, and where the level design makes the gate
    direction coincide with "away from the arrival door" the default heuristic
    agrees with them. That agreement is a convention, not engine law.
    """
    silent = stated = 0
    agree = disagree = 0
    for source in (39, 40, 41):
        for entry in fresh.for_map(MapIdentity(source)):
            facing = entry.record.facing
            if facing.override_raw == 0:
                silent += 1
                assert facing.arrival_direction is None
            else:
                stated += 1
                assert facing.arrival_direction is not None
            if not entry.record.has_raw_arrival_pair or entry.record.arrival is None:
                continue
            default = fresh.default_facing(
                fresh.destination(entry.identity), entry.record.arrival
            )
            if default == facing.gate_direction:
                agree += 1
            else:
                disagree += 1
    assert silent >= 5, "the common case must be an unstated facing"
    assert agree >= 4, "the convention should hold on most of this chain"


def test_an_override_is_what_forces_the_facing(fresh) -> None:
    """Stating a facing writes the override, and the gate bits survive it."""
    before = fresh.entry(TARGET).record
    assert before.facing.override_raw == 0, "the canonical record is silent"
    assert before.facing.gate_direction == 2
    fresh.set_facing(TARGET, FACING_NORTH)
    after = fresh.entry(TARGET).record
    assert after.facing.arrival_direction == FACING_NORTH
    assert after.facing.gate_direction == 2, "the gate bits must be preserved"
    assert after.byte_0x10_raw == ((FACING_NORTH + 1) << 4) | 2
    # The region and the destination are untouched by a facing edit.
    assert after.region == before.region
    assert after.destination_key == before.destination_key


def test_retarget_defaults_the_facing_to_north_for_volcano(fresh) -> None:
    """The runtime observation: arriving at Volcano's south door must face North."""
    arrival, facing = fresh.retarget(
        TARGET, VOLCANO, arrival=TransitionArrival(x=120, y=364)
    )
    assert arrival == TransitionArrival(x=120, y=364)
    assert facing == FACING_NORTH
    staged = fresh.entry(TARGET).record
    assert staged.facing.arrival_direction == FACING_NORTH
    assert staged.facing.gate_direction == 2, "the canonical gate bits must survive"
    assert fresh.facing(TARGET) == FACING_NORTH
    assert fresh.destination(TARGET) == VOLCANO
    # The region is never touched by a retarget.
    assert staged.region == load_map_transitions(
        Path(_rom_path()), RomProfileCatalog.load(CATALOG)
    ).entry(TARGET).record.region


def test_retarget_accepts_an_explicit_facing_override(fresh) -> None:
    _arrival, facing = fresh.retarget(
        TARGET, VOLCANO, arrival=TransitionArrival(x=120, y=364), facing=3
    )
    assert facing == 3 and FACING_NAMES[facing] == "East"
    assert fresh.entry(TARGET).record.facing.direction == 3


def test_retarget_refuses_an_invalid_facing(fresh) -> None:
    with pytest.raises(TransitionFieldError):
        fresh.retarget(
            TARGET, VOLCANO, arrival=TransitionArrival(x=120, y=364), facing=4
        )
    with pytest.raises(TransitionFieldError):
        fresh.set_facing(TARGET, 99)


def test_a_facing_edit_moves_only_the_facing_byte(fresh) -> None:
    """Byte locality on the real record: +0x10 and nothing else."""
    entry = fresh.entry(TARGET)
    before = entry.record
    fresh.set_facing(TARGET, 1)
    after = fresh.entry(TARGET).record
    differing = [
        offset
        for offset in range(24)
        if before.to_bytes()[offset] != after.to_bytes()[offset]
    ]
    assert differing == [0x10]
    plan = fresh.plan()
    effective = [c for c in plan.changes if c.is_effective]
    assert [c.offset for c in effective] == [entry.file_offset]


def test_the_canonical_rom_is_unchanged_by_reading_it(rom: str) -> None:
    before = hashlib.sha256(Path(rom).read_bytes()).hexdigest()
    authority = load_map_transitions(rom, RomProfileCatalog.load(CATALOG))
    for entry in authority.for_map(MAP_40):
        entry.record.arrival
        entry.record.facing
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == before
    assert before == CANONICAL_SHA256
