"""DRAGONBYTE-Z-ENTITIES-DESTINATION-001: the Entities destination's model.

What this file proves is that the model passes the SDK's answers through rather
than inventing any of its own: the placement identities `webfoot.maps` publishes,
the behaviour and attachment identities `webfoot.placement_events` publishes
where its contract decodes one, the owner-bearing change one placement edit
produces, and the three object families this build does not model, which appear
with their pointer slot and stride and no name at all.

The project fixture is a real extraction, not a hand-written one, because the
whole point of the model is that it agrees with documents the SDK itself wrote.
The suite skips without the canonical image.
"""

from __future__ import annotations

from dataclasses import fields, replace

import pytest

from tools.dragonbyte import entitysurface as es
from tools.dragonbyte.inspector import SUPPORT_STATES
from tools.webfoot.build import extract_project
from tools.webfoot.catalog import load_catalog
from tools.webfoot.formats import map_placements as mp
from tools.webfoot.maps import MapIdentity, PlacementIdentity, load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom

from tests.unit.test_dragonbyte_state import CANONICAL_SHA256, SIBLING_CHECKOUT

#: A map whose placements are recorded in the canonical image.
PLACED_MAP = 10

#: A map with a different placement count, so a count is not assumed.
OTHER_MAP = 40

#: A map whose placement reaches the script-dispatch handler: the worked example.
SCRIPT_MAP = 19


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(None)


@pytest.fixture(scope="module")
def canonical_rom(catalog):
    roms = SIBLING_CHECKOUT / "roms"
    for candidate in sorted(roms.glob("*.gba")) if roms.is_dir() else []:
        try:
            identification = identify_rom(candidate, catalog)
        except Exception:  # noqa: BLE001 - any unreadable file is simply not it
            continue
        if identification.hashes.sha256 == CANONICAL_SHA256:
            return candidate
    pytest.skip(f"no canonical image in {roms}")


@pytest.fixture(scope="module")
def identification(catalog, canonical_rom):
    return identify_rom(canonical_rom, catalog)


@pytest.fixture(scope="module")
def profile(identification):
    return identification.profile_match.profile


@pytest.fixture(scope="module")
def surface(catalog, canonical_rom, identification, profile):
    return es.load_entity_surface(
        canonical_rom, catalog, identification, profile, canonical_rom.read_bytes()
    )


@pytest.fixture(scope="module")
def maps(catalog, canonical_rom):
    return load_maps(canonical_rom, catalog)


@pytest.fixture(scope="module")
def project(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-entity-project") / "project"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return read_project(directory)


@pytest.fixture(scope="module")
def events(maps):
    return PlacementEvents(maps)


def _row(surface, index, project):
    return next(
        row for row in surface.placements(index, project) if row.placement_index == 0
    )


# --- the placement family ------------------------------------------------------


def test_a_map_shows_exactly_the_placement_records_the_sdk_owns(
    surface, maps, project
):
    for index in (PLACED_MAP, OTHER_MAP):
        owned = maps.map_placements(MapIdentity(index))
        rows = surface.placements(index, project)

        print(f"\nMODEL | map {index}: {len(owned)} placement record(s)")
        for row in rows:
            print(
                f"  {row.label}  {row.identity}  slot {row.slot_index}  "
                f"({row.x}, {row.y})  {row.size} bytes  at 0x{row.file_offset:06X}"
            )

        assert [row.identity for row in rows] == [str(entry.identity) for entry in owned]
        assert [row.slot_index for row in rows] == [entry.slot_index for entry in owned]
        for row, entry in zip(rows, owned):
            assert row.map_index == index
            assert row.label == f"Placement {row.placement_index:03d}"
            assert row.size == len(entry.original_bytes)
            assert row.address == entry.file_offset + 0x08000000
            assert (row.x, row.y) == mp.decode_position(
                entry.record.position_low, entry.record.position_high
            )
            assert (row.position_low, row.position_high) == (
                entry.record.position_low,
                entry.record.position_high,
            )


def test_the_authored_position_is_what_the_row_shows(surface, project):
    moved = replace(
        project,
        maps={
            **project.maps,
            PLACED_MAP: {
                **project.maps[PLACED_MAP],
                "placements": tuple(
                    {**item, "position_low": 0x0102, "position_high": 0xFFFE}
                    if item["index"] == 0
                    else item
                    for item in project.maps[PLACED_MAP]["placements"]
                ),
            },
        },
    )
    row = _row(surface, PLACED_MAP, moved)

    print(f"\nMODEL | authored position 0x0102/0xFFFE decodes to ({row.x}, {row.y})")

    assert (row.position_low, row.position_high) == (0x0102, 0xFFFE)
    assert (row.x, row.y) == mp.decode_position(0x0102, 0xFFFE)
    assert row.editable


def test_a_project_that_authors_no_placement_record_says_so(surface):
    row = _row(surface, PLACED_MAP, None)

    print(f"\nMODEL | with no project open: editable={row.editable} note={row.note!r}")

    assert not row.editable
    assert row.note == f"this project authors no placement record for {row.identity}"


# --- behaviours and attachments ------------------------------------------------


def test_every_placement_names_the_behaviour_the_sdk_publishes(
    surface, events, project
):
    seen = 0
    for index in (PLACED_MAP, OTHER_MAP, SCRIPT_MAP):
        for row in surface.placements(index, project):
            descriptor = events.descriptor_of(row.identity)
            assert row.behaviour == descriptor.identity
            assert row.attachment == (descriptor.event or "")
            seen += 1

    print(f"\nMODEL | {seen} placement row(s) name the SDK's own descriptor identity")
    assert seen


def test_an_attachment_is_shown_only_where_the_contract_decodes_one(surface, events):
    attached = [
        row
        for index in (PLACED_MAP, OTHER_MAP, SCRIPT_MAP)
        for row in surface.placements(index, None)
        if row.attachment
    ]
    unattached = [
        row
        for index in (PLACED_MAP, OTHER_MAP, SCRIPT_MAP)
        for row in surface.placements(index, None)
        if not row.attachment
    ]

    print("\nMODEL | attachment presence, and the reason where there is none")
    for row in attached[:2]:
        print(f"  {row.identity} -> {row.attachment}")
    for row in unattached[:2]:
        print(f"  {row.identity} -> none: {row.behaviour_note}")

    assert attached and unattached
    for row in attached:
        assert row.behaviour_note == ""
    for row in unattached:
        assert row.behaviour_note


def test_a_script_handler_outside_the_contract_states_that_reason(surface, events):
    uncovered = [
        descriptor
        for descriptor in events.descriptors
        if descriptor.record.handler_pointer_raw == mp.SCRIPT_DISPATCH_HANDLER
        and descriptor.event is None
    ]

    print(
        f"\nMODEL | descriptors dispatching the script handler with no decoded "
        f"attachment: {len(uncovered)}"
    )
    assert uncovered, "the worked example of an undecoded attachment has gone"

    attachment, note = es.EntitySurface._attachment(uncovered[0])

    print(f"  {uncovered[0].identity} -> {note}")

    assert attachment == ""
    assert "does not cover it" in note


def test_a_placement_whose_handler_is_not_the_script_handler_says_so(surface):
    null = next(
        row
        for row in surface.placements(OTHER_MAP, None)
        if not row.attachment and row.behaviour
    )
    descriptor = None
    for candidate in surface.events.descriptors:
        if candidate.identity == null.behaviour:
            descriptor = candidate
    assert descriptor is not None
    assert descriptor.record.handler_pointer_raw != mp.SCRIPT_DISPATCH_HANDLER

    print(f"\nMODEL | {null.identity}: {null.behaviour_note}")

    assert "not the script-dispatch handler" in null.behaviour_note


def test_a_behaviour_row_carries_the_handler_the_sdk_names(surface, project):
    rows = surface.behaviours(SCRIPT_MAP, project)
    attached = [row for row in rows if row.attachment]

    print(f"\nMODEL | map {SCRIPT_MAP}: {len(rows)} behaviour(s), {len(attached)} with a script")
    for row in rows:
        print(
            f"  {row.identity}  {row.handler}  attachment={row.attachment or 'none'}  "
            f"{row.size} bytes at 0x{row.file_offset:06X}"
        )

    assert attached
    for row in rows:
        descriptor = surface.events.descriptor_of(row.identity.rsplit("/descriptor", 1)[0])
        assert row.handler == mp.HANDLERS[descriptor.record.handler_pointer_raw]
        assert row.attachment == (descriptor.event or "")
        assert row.size == len(descriptor.record.to_bytes())
        assert "not editable here" in row.note


def test_without_the_descriptor_contract_the_reason_is_stated_not_hidden(surface):
    blinded = replace(
        surface, events=None, behaviour_problem="no verified placement descriptor contract"
    )
    rows = blinded.placements(PLACED_MAP, None)

    print(f"\nMODEL | with no descriptor contract: {rows[0].behaviour_note!r}")

    assert rows
    for row in rows:
        assert row.behaviour == ""
        assert row.attachment == ""
        assert row.behaviour_note == "no verified placement descriptor contract"
    assert blinded.behaviours(PLACED_MAP, None) == ()


# --- the unmodelled families ---------------------------------------------------


def test_the_family_list_is_one_modelled_and_three_unnamed_not_modelled(surface):
    rows = surface.families()

    print("\nMODEL | the four per-area object families")
    for row in rows:
        print(
            f"  {row.label:22} slot {row.pointer_slot}  stride {row.stride}  "
            f"{row.support}  | {row.basis}"
        )
    print(f"  {es.family_summary(rows)}")

    assert es.family_summary(rows) == "Object families: 1 of 4 modelled"
    assert len(rows) == 4
    assert sum(1 for row in rows if row.modelled) == 1
    assert [(row.pointer_slot, row.stride) for row in rows] == [
        ("+0x14", 4),
        ("+0x18", 4),
        ("+0x1C", 4),
        ("+0x20", 8),
    ]
    assert rows[0].support == "Editable with limits"
    for row in rows:
        assert row.support in SUPPORT_STATES
    for row in rows[1:]:
        assert row.label == es.NOT_MODELLED == "Family not modelled"
        assert row.support == "Not supported yet"
        assert not row.modelled
        assert "not decoded" in row.note
        assert "INFERRED and disputed" in row.basis


def test_no_row_type_carries_a_relation_the_evidence_does_not_support():
    """The closed field set is the guard: a new relation needs a new field here."""
    expected = {
        es.PlacementRow: {
            "identity",
            "label",
            "map_index",
            "placement_index",
            "slot_index",
            "file_offset",
            "size",
            "address",
            "x",
            "y",
            "position_low",
            "position_high",
            "type_raw",
            "id_raw",
            "behaviour",
            "attachment",
            "behaviour_note",
            "editable",
            "note",
        },
        es.BehaviourRow: {
            "identity",
            "file_offset",
            "size",
            "handler",
            "handler_address",
            "attachment",
            "placements",
            "note",
        },
        es.FamilyRow: {
            "label",
            "pointer_slot",
            "stride",
            "support",
            "modelled",
            "note",
            "basis",
        },
    }
    forbidden = {"sprite", "destination", "trigger", "audio", "shop", "item", "text"}

    for kind, names in expected.items():
        actual = {field.name for field in fields(kind)}
        print(f"\nMODEL | {kind.__name__} fields: {sorted(actual)}")
        assert actual == names
        assert not (actual & forbidden)


# --- the one edit path ---------------------------------------------------------


def test_one_edit_produces_one_change_owned_by_the_placement_identity(surface, project):
    row = _row(surface, PLACED_MAP, project)
    after = es.with_position(project, row, row.x + 3, row.y + 4)
    changes = surface.changes(after)

    print("\nMODEL | one position edit, as the SDK's own owner-bearing change")
    for change in changes:
        print(
            f"  {change.owner}  0x{change.offset:06X}  {change.old.hex()[:16]} -> "
            f"{change.new.hex()[:16]}  ({change.reason})"
        )

    assert len(changes) == 1
    change = changes[0]
    assert change.owner == row.identity
    assert change.offset == row.file_offset
    assert change.old == bytes(
        surface.maps.placement(
            PlacementIdentity(row.map_index, row.placement_index)
        ).original_bytes
    )
    assert change.old != change.new
    assert change.reason == "placement edit: position"
    assert surface.pending_bytes(after) == {change.offset: change.new}


def test_an_unchanged_project_stages_nothing(surface, project):
    print(f"\nMODEL | changes for the untouched project: {surface.changes(project)}")

    assert surface.changes(project) == ()
    assert surface.pending_bytes(project) == {}


def test_the_edit_returns_a_new_payload_and_mutates_nothing(surface, project):
    row = _row(surface, PLACED_MAP, project)
    before = project.maps[PLACED_MAP]["placements"]
    after = es.with_position(project, row, 7, 9)

    print(
        f"\nMODEL | authored payload untouched: {before[0]['position_low']}, "
        f"returned payload: {after.maps[PLACED_MAP]['placements'][0]['position_low']}"
    )

    assert after is not project
    assert project.maps[PLACED_MAP]["placements"][0]["position_low"] == (
        before[0]["position_low"]
    )
    assert after.maps[PLACED_MAP]["placements"][0]["position_low"] == 7
    assert after.maps[PLACED_MAP]["placements"][0]["position_high"] == 9
    assert len(after.maps[PLACED_MAP]["placements"]) == len(before)
    assert after.maps[PLACED_MAP]["placements"][-1] == before[-1]


def test_a_project_naming_a_placement_this_image_lacks_is_skipped_not_crashed(
    surface, project
):
    alien = replace(
        project,
        maps={
            **project.maps,
            PLACED_MAP: {
                **project.maps[PLACED_MAP],
                "placements": (*project.maps[PLACED_MAP]["placements"],),
            },
            4000: {"placements": [{"index": 0, "position_low": 1, "position_high": 2}]},
        },
    )

    print(f"\nMODEL | an unknown map in the document stages nothing: {surface.changes(alien)}")

    assert surface.changes(alien) == ()


def test_the_map_selector_counts_what_each_map_owns(surface, maps):
    rows = surface.map_rows()
    counts: dict[int, int] = {}
    for entry in maps.placements():
        counts[entry.identity.map_index] = counts.get(entry.identity.map_index, 0) + 1

    print(f"\nMODEL | {len(rows)} map(s), {sum(1 for row in rows if row.placements)} with a placement")

    assert len(rows) == len(tuple(maps.entries()))
    assert [row.index for row in rows] == [entry.identity.index for entry in maps.entries()]
    for row in rows:
        assert row.placements == counts.get(row.index, 0)
    assert rows[PLACED_MAP].placements
