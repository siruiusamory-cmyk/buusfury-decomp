"""ROM-gated map proofs against the canonical Buu's Fury image.

Every count asserted here was measured from that ROM, not assumed. The
canonical image is opened read-only on every path; nothing in this file writes
to it, and the build tests emit into pytest's temporary directory.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.cli import main
from tools.webfoot.formats.map_slots import ArrayShape
from tools.webfoot.maps import MapIdentity, load_maps
from tools.webfoot.profile import RomProfileCatalog


LOCAL_ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
CATALOG = "config/roms.yaml"

#: Measured from the canonical ROM, TOOLKIT-007.
MAP_RECORD_COUNT = 452

#: CORRECTED by TOOLKIT-008, from 152 arrays / 873 slots / 6,984 bytes.
#:
#: OLD CLAIM: every MapEntry whose `trigger_count_raw` and `triggers_pointer_raw`
#: describe an in-bounds extent contributes a slot array, giving 152 arrays.
#:
#: NEW EVIDENCE: 40 of those 152 declared extents cover bytes belonging to
#: factory-led placement records (`webfoot.formats.map_placements`), 57 records
#: in total. The two readings cannot both hold, and the placement reading is the
#: better-witnessed one: **33 of the 40** have their first record starting at
#: byte 4 mod 8, *mid slot*, so those bytes cannot be whole 8-byte slots at all.
#: MapEntry 146 declares 12 slots whose extent walks through three complete
#: records - `slots[2]` is the factory word and `slots[5..6]` split a record's
#: constant tail across a slot boundary. Two slots were classified TYPED only
#: because a record's tail constants satisfy the `{type, source_ref}` shape test.
#:
#: RESOLUTION: those 40 extents are refused, exactly as MapEntry 451 already was
#: and for the same reason - a declared extent that provably is not slots is not
#: read as slots. `trigger_count_raw` remains UNKNOWN in meaning, as
#: `docs/research/MAP_FORMAT.md` records; this narrows where it is trusted.
#:
#: The typed corpus is UNCHANGED at 35 arrays / 89 slots: every refused extent
#: was opaque, so TOOLKIT-007's typed rung and connection graph stand as proven.
SLOT_ARRAY_COUNT = 112
SLOT_COUNT = 596
SLOT_BYTES = 4768
TYPED_ARRAY_COUNT = 35
TYPED_SLOT_COUNT = 89

#: TOOLKIT-008. The factory-led placement corpus, measured from the same image.
PLACEMENT_COUNT = 1295
PLACEMENT_MAP_COUNT = 215
PLACEMENT_BYTES = 41440

#: The one instance whose referenced structure `AUTO_RE_<local-state-name>:314` verifies.
CONFIRMED_MAP = 39
CONFIRMED_SLOT = 1
CONFIRMED_TYPE = 0x00020006
CONFIRMED_SOURCE = 0x080755C0
CONFIRMED_BOUNDS = (481, 121, 615, 271)


def catalog():
    return RomProfileCatalog.load(CATALOG)


def require_rom():
    if not LOCAL_ROM.is_file():
        pytest.skip("user-supplied Buu's Fury ROM is not present")


@pytest.fixture
def maps():
    require_rom()
    return load_maps(LOCAL_ROM, catalog())


# --- corpus and round-trip ----------------------------------------------


def test_the_complete_map_corpus_round_trips_byte_identically(maps):
    records = list(maps.entries())
    assert len(records) == MAP_RECORD_COUNT
    for entry in records:
        assert entry.record.to_bytes() == entry.original_bytes, entry.identity


def test_the_complete_slot_extent_round_trips_byte_identically(maps):
    arrays = list(maps.slot_arrays())
    assert len(arrays) == SLOT_ARRAY_COUNT
    assert sum(item.array.slot_count for item in arrays) == SLOT_COUNT
    assert sum(item.array.byte_size for item in arrays) == SLOT_BYTES
    for item in arrays:
        assert item.array.to_bytes() == item.array.original_bytes, item.identity


def test_the_typed_corpus_is_exactly_the_uniform_arrays(maps):
    typed = [item for item in maps.slot_arrays() if item.is_typed]
    assert len(typed) == TYPED_ARRAY_COUNT
    assert sum(item.array.slot_count for item in typed) == TYPED_SLOT_COUNT
    for item in typed:
        assert item.shape is ArrayShape.TYPED


def test_the_typed_corpus_is_insensitive_to_the_threshold(maps):
    """The chosen `_TYPED_HIGH_HALFWORD_LIMIT` must not decide the corpus.

    The bound is hand-picked from one example rather than measured, which is
    only acceptable while the classification does not actually turn on it. Every
    limit from 0x0003 to 0x0100 must yield the same 35 arrays / 89 slots; if one
    day it does not, the constant has become load-bearing and the classifier
    needs real evidence instead of a chosen number.
    """
    from tools.webfoot.formats import map_slots

    image_size = len(maps.base_bytes)
    original = map_slots._TYPED_HIGH_HALFWORD_LIMIT
    try:
        for limit in (0x0003, 0x0008, 0x0010, 0x0020, 0x0100):
            map_slots._TYPED_HIGH_HALFWORD_LIMIT = limit
            typed = [
                item
                for item in maps.slot_arrays()
                if all(
                    slot.is_typed(image_size) for slot in item.array.slots
                )
            ]
            assert len(typed) == TYPED_ARRAY_COUNT, hex(limit)
            assert sum(i.array.slot_count for i in typed) == TYPED_SLOT_COUNT, hex(limit)
    finally:
        map_slots._TYPED_HIGH_HALFWORD_LIMIT = original


def test_no_slot_extent_collides_with_the_map_table(maps):
    """MapEntry 451 declares one that does; it must not have been read.

    Its declared extent covers the start of the table indexing it, which is a
    structural witness that `+0x04` is not a general slot count.
    """
    assert maps.slot_array(MapIdentity(451)) is None


def test_a_readable_extent_never_overlaps_another(maps):
    spans = sorted(
        (item.array.file_offset, item.array.byte_size)
        for item in maps.slot_arrays()
    )
    for (start, size), (next_start, _) in zip(spans, spans[1:]):
        assert start + size <= next_start


# --- the one confirmed example ------------------------------------------


def test_the_confirmed_source_reference_reproduces_exactly(maps):
    """MapEntry 39 slot[1] and its bounds, from `AUTO_RE_<local-state-name>:314`.

    Kept as a regression fixture: this is the single instance whose referenced
    structure this project has verified, and the evidence it rests on.
    """
    array = maps.slot_array(MapIdentity(CONFIRMED_MAP))
    slot = array.array.slots[CONFIRMED_SLOT]
    assert slot.word0 == CONFIRMED_TYPE
    assert slot.word1 == CONFIRMED_SOURCE

    import struct

    bounds = struct.unpack_from(
        "<4h", maps.base_bytes, slot.source_file_offset + 0x08
    )
    assert bounds == CONFIRMED_BOUNDS


def test_the_confirmed_example_is_not_itself_a_typed_array(maps):
    """Its declared count of 11 runs past its four well-formed slots.

    The example is real; the corpus-wide generalisation it was read as is not.
    Asserting this keeps the distinction from quietly eroding.
    """
    array = maps.slot_array(MapIdentity(CONFIRMED_MAP))
    assert array.array.slot_count == 11
    assert array.shape is ArrayShape.OPAQUE


# --- graph ---------------------------------------------------------------


def test_the_connection_graph_is_deterministic(maps):
    other = load_maps(LOCAL_ROM, catalog())
    assert maps.graph().connections == other.graph().connections


def test_the_graph_covers_the_typed_corpus_and_no_more(maps):
    graph = maps.graph()
    assert len(graph.connections) == TYPED_SLOT_COUNT
    typed = {item.identity for item in maps.slot_arrays() if item.is_typed}
    assert {c.source for c in graph.connections} <= typed


def test_every_destination_stays_explicitly_unknown(maps):
    """Sec 15: unknown destinations remain explicit rather than guessed."""
    graph = maps.graph()
    assert graph.resolved_destination_count == 0
    assert all(c.destination is None for c in graph.connections)


# --- project lifecycle ---------------------------------------------------


def test_extraction_is_deterministic_and_the_no_op_build_is_identical(tmp_path):
    require_rom()
    first = tmp_path / "one"
    second = tmp_path / "two"
    extract_project(LOCAL_ROM, first, catalog(), graphics=False)
    extract_project(LOCAL_ROM, second, catalog(), graphics=False)

    authored = first / "maps" / "maps.toml"
    assert authored.is_file()
    assert authored.read_bytes() == (second / "maps" / "maps.toml").read_bytes()

    report = validate_project(first, LOCAL_ROM, catalog())
    assert report.passed, report.problems[:5]
    assert report.map_count == MAP_RECORD_COUNT

    build_project(first, LOCAL_ROM, tmp_path / "a.gba", catalog())
    build_project(first, LOCAL_ROM, tmp_path / "b.gba", catalog())

    base = LOCAL_ROM.read_bytes()
    built = (tmp_path / "a.gba").read_bytes()
    assert hashlib.sha256(built).hexdigest() == hashlib.sha256(base).hexdigest()
    assert built == (tmp_path / "b.gba").read_bytes()


def test_one_semantic_map_edit_changes_only_the_expected_bytes(tmp_path):
    require_rom()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    # Edit map:0039's own block, located by its header. Several maps share a
    # music id, so replacing the first match in the whole file would silently
    # edit a different map and still produce a passing one-byte diff.
    authored = project / "maps" / "maps.toml"
    text = authored.read_text(encoding="utf-8")
    start = text.index('[map."map:0039"]')
    end = text.index("\n[map.", start + 1)
    block = text[start:end]
    assert "music_id = 15" in block
    authored.write_text(
        text[:start] + block.replace("music_id = 15", "music_id = 14", 1) + text[end:],
        encoding="utf-8",
        newline="\n",
    )

    build_project(
        project,
        LOCAL_ROM,
        tmp_path / "edited.gba",
        catalog(),
        manifest_path=tmp_path / "edited.json",
    )

    base = LOCAL_ROM.read_bytes()
    built = (tmp_path / "edited.gba").read_bytes()
    differing = [index for index in range(len(base)) if base[index] != built[index]]
    assert len(differing) == 1

    manifest = json.loads((tmp_path / "edited.json").read_text(encoding="utf-8"))
    assert manifest["changed_byte_count"] == 1
    change = manifest["changes"][0]
    assert change["owner"] == "map:0039"
    assert "music_id" in change["reason"]
    # The changed byte is `music_id_raw` itself, at record `+0x24` - not merely
    # somewhere inside the record the manifest claims.
    assert differing[0] == change["offset"] + 0x24


def test_the_canonical_rom_is_unchanged_by_a_build(tmp_path):
    require_rom()
    before = hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)
    build_project(project, LOCAL_ROM, tmp_path / "out.gba", catalog())
    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == before


def test_a_map_stat_and_text_edit_coexist_in_one_build(tmp_path):
    """Sec 19: three subsystems, one merged plan, three attributed owners."""
    require_rom()
    import re

    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    maps_file = project / "maps" / "maps.toml"
    text = maps_file.read_text(encoding="utf-8")
    start = text.index('[map."map:0039"]')
    end = text.index("\n[map.", start + 1)
    block = text[start:end]
    maps_file.write_text(
        text[:start] + block.replace("music_id = 15", "music_id = 14", 1) + text[end:],
        encoding="utf-8",
        newline="\n",
    )

    enemies_file = project / "enemies" / "enemies.toml"
    enemies = enemies_file.read_text(encoding="utf-8")
    match = re.search(r"\[enemy\.\d+\]\n(.*?)(?=\n\[|\Z)", enemies, re.S)
    enemy_block = match.group(1)
    hp = int(re.search(r"hp = (\d+)", enemy_block).group(1))
    enemies_file.write_text(
        enemies.replace(
            enemy_block, enemy_block.replace(f"hp = {hp}", f"hp = {hp + 1}", 1), 1
        ),
        encoding="utf-8",
        newline="\n",
    )

    strings_file = project / "text" / "strings.toml"
    strings = strings_file.read_text(encoding="utf-8")
    match = re.search(r'\[text\."(text:\d+)"\]\ntext = "([^"\n]{4,20})"', strings)
    key, value = match.group(1), match.group(2)
    strings_file.write_text(
        strings.replace(
            f'[text."{key}"]\ntext = "{value}"',
            f'[text."{key}"]\ntext = "{value[:-1]}X"',
            1,
        ),
        encoding="utf-8",
        newline="\n",
    )

    build_project(
        project,
        LOCAL_ROM,
        tmp_path / "all.gba",
        catalog(),
        manifest_path=tmp_path / "all.json",
    )

    manifest = json.loads((tmp_path / "all.json").read_text(encoding="utf-8"))
    owners = {change["owner"] for change in manifest["changes"]}
    assert any(owner.startswith("map:") for owner in owners)
    assert any(owner.startswith("enemy:") for owner in owners)
    assert any(owner.startswith("text:") for owner in owners)
    assert len(owners) == 3

    base = LOCAL_ROM.read_bytes()
    built = (tmp_path / "all.gba").read_bytes()
    differing = [index for index in range(len(base)) if base[index] != built[index]]
    assert len(differing) == manifest["changed_byte_count"]


def test_two_owners_writing_one_span_is_refused(maps):
    """Sec 19's other direction: overlap fails clearly rather than last-wins.

    Built from the real map plan so the refusal is proven against the machinery
    a build actually uses, not against a hand-made pair of changes.
    """
    from tools.webfoot.write import ByteChange, OverlappingChangeError, plan_changes

    entry = maps.entry(MapIdentity(CONFIRMED_MAP))
    intruder = ByteChange(
        offset=entry.file_offset + 4,
        old=entry.original_bytes[4:8],
        new=entry.original_bytes[4:8],
        owner="text:9999",
        reason="a second owner claiming a map record's bytes",
    )
    with pytest.raises(OverlappingChangeError):
        plan_changes(
            maps.base_bytes,
            list(maps.changes()) + [intruder],
            profile_id=maps.profile.id,
            base_sha256=maps.identification.hashes.sha256,
        )


# --- validation ----------------------------------------------------------


def test_an_out_of_range_field_value_is_refused_before_emission(tmp_path):
    require_rom()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    maps_file = project / "maps" / "maps.toml"
    text = maps_file.read_text(encoding="utf-8")
    start = text.index('[map."map:0039"]')
    end = text.index("\n[map.", start + 1)
    block = text[start:end]
    maps_file.write_text(
        text[:start] + block.replace("zone = 11", "zone = 300", 1) + text[end:],
        encoding="utf-8",
        newline="\n",
    )

    report = validate_project(project, LOCAL_ROM, catalog())
    assert not report.passed
    assert any("zone=300" in problem for problem in report.problems)
    assert not (tmp_path / "never.gba").exists()


def test_a_map_absent_from_the_project_is_reported(tmp_path):
    require_rom()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    maps_file = project / "maps" / "maps.toml"
    text = maps_file.read_text(encoding="utf-8")
    start = text.index('[map."map:0039"]')
    end = text.index("\n[map.", start + 1)
    maps_file.write_text(text[:start] + text[end + 1 :], encoding="utf-8", newline="\n")

    report = validate_project(project, LOCAL_ROM, catalog())
    assert not report.passed
    assert any("map:0039" in problem for problem in report.problems)


def test_a_project_built_against_the_wrong_rom_is_refused(tmp_path):
    """Sec 18: wrong profile. Legacy of Goku II declares no map table."""
    require_rom()
    other = Path("roms/Dragon Ball Z - The Legacy of Goku II (USA).gba")
    if not other.is_file():
        pytest.skip("Legacy of Goku II ROM is not present")

    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    report = validate_project(project, other, catalog())
    assert not report.passed
    assert any("base ROM mismatch" in problem for problem in report.problems)


# --- CLI -----------------------------------------------------------------


def test_cli_round_trip_reports_the_measured_corpus(capsys):
    require_rom()
    exit_code = main(["map", "validate-round-trip", str(LOCAL_ROM)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert f"Map records checked: {MAP_RECORD_COUNT}" in output
    assert f"Slot arrays checked: {SLOT_ARRAY_COUNT}" in output
    assert f"Slots checked: {SLOT_COUNT} ({SLOT_BYTES} bytes)" in output
    assert f"Typed arrays: {TYPED_ARRAY_COUNT}" in output
    assert "Record failures: 0" in output
    assert "Slot failures: 0" in output
    assert "RESULT:\nPASS" in output


def test_cli_show_does_not_leak_raw_offsets_for_an_opaque_map(capsys):
    require_rom()
    assert main(["map", "show", str(LOCAL_ROM), "map:0039"]) == 0
    output = capsys.readouterr().out
    assert "Identity: map:0039" in output
    assert "OPAQUE" in output
    assert "UNKNOWN" in output


def test_cli_connections_marks_destinations_unknown(capsys):
    require_rom()
    assert main(["map", "connections", str(LOCAL_ROM)]) == 0
    output = capsys.readouterr().out
    assert f"Connections: {TYPED_SLOT_COUNT}" in output
    assert "Resolved destinations: 0" in output
    assert "destination UNKNOWN" in output


def test_cli_rejects_a_malformed_identity(capsys):
    require_rom()
    assert main(["map", "show", str(LOCAL_ROM), "0039"]) == 2
    assert "not a map identity" in capsys.readouterr().err


# --- TOOLKIT-008: factory-led placement records -------------------------


def test_the_complete_placement_corpus_round_trips_byte_identically(maps):
    """Exhaustive, not sampled: every reachable record, decoded and re-encoded."""
    placements = list(maps.placements())
    assert len(placements) == PLACEMENT_COUNT
    assert sum(len(item.original_bytes) for item in placements) == PLACEMENT_BYTES
    for item in placements:
        assert item.record.to_bytes() == item.original_bytes


def test_every_placement_belongs_to_exactly_one_map(maps):
    """Exclusive ownership is what lets a placement carry a semantic owner."""
    placements = list(maps.placements())
    owners = {}
    for item in placements:
        assert item.file_offset not in owners
        owners[item.file_offset] = item.identity.map_index
    assert len({item.identity.map_index for item in placements}) == PLACEMENT_MAP_COUNT


def test_placement_identities_are_stable_and_carry_no_address(maps):
    for item in maps.placements():
        assert item.identity.key == (
            f"map:{item.identity.map_index:04d}"
            f"/placement:{item.identity.placement_index:04d}"
        )
        assert hex(item.file_offset) not in item.identity.key


def test_map_to_placement_ownership_is_answerable_without_offsets(maps):
    """A caller asks a map for its placements and never computes an offset."""
    identity = MapIdentity(10)
    owned = maps.map_placements(identity)
    assert owned
    assert all(item.identity.map_index == identity.index for item in owned)
    assert [item.identity.placement_index for item in owned] == list(range(len(owned)))


def test_enumeration_is_deterministic_across_loads():
    require_rom()
    first = [item.identity for item in load_maps(LOCAL_ROM, catalog()).placements()]
    second = [item.identity for item in load_maps(LOCAL_ROM, catalog()).placements()]
    assert first == second


def test_no_slot_extent_overlaps_a_placement_record(maps):
    """The TOOLKIT-008 correction, asserted rather than described.

    40 declared slot extents covered placement-record bytes; those extents are
    refused. If a future change re-admits one, this fails before a build does.
    """
    records = [
        (item.file_offset, item.file_offset + len(item.original_bytes))
        for item in maps.placements()
    ]
    for array_entry in maps.slot_arrays():
        start = array_entry.array.file_offset
        end = start + len(array_entry.array.original_bytes)
        for record_start, record_end in records:
            assert not (start < record_end and record_start < end), (
                f"{array_entry.identity} slot extent covers a placement record"
            )


def test_the_typed_slot_corpus_survives_the_correction(maps):
    """The refused extents were all opaque; TOOLKIT-007's typed rung stands."""
    typed = [item for item in maps.slot_arrays() if item.is_typed]
    assert len(typed) == TYPED_ARRAY_COUNT
    assert sum(item.array.slot_count for item in typed) == TYPED_SLOT_COUNT


def test_a_placement_position_edit_changes_exactly_one_byte(maps):
    """The TOOLKIT-008 closure proof, at the semantic layer."""
    identity = next(iter(maps.placements())).identity
    before = maps.placement(identity)
    original_low = before.record.position_low
    original_high = before.record.position_high

    maps.set_placement_position(identity, low=original_low + 16, high=original_high)

    after = maps.placement(identity)
    assert after.record.position_low == original_low + 16
    assert after.record.position_high == original_high

    edited = [
        change
        for change in maps.plan().changes
        if change.old != change.new
    ]
    assert len(edited) == 1
    change = edited[0]
    assert change.owner == identity.key
    assert change.reason == "placement edit: position"
    differing = [i for i in range(len(change.old)) if change.old[i] != change.new[i]]
    assert differing == [0x0C]


def test_a_placement_edit_leaves_every_other_record_untouched(maps):
    identity = next(iter(maps.placements())).identity
    maps.set_placement_position(identity, low=1, high=1)
    for item in maps.placements():
        if item.identity == identity:
            continue
        assert item.record.to_bytes() == item.original_bytes


def test_an_out_of_range_position_is_refused_before_any_plan(maps):
    from tools.webfoot.formats.map_placements import MapPlacementValueError

    identity = next(iter(maps.placements())).identity
    with pytest.raises(MapPlacementValueError):
        maps.set_placement_position(identity, low=0x10000, high=0)
    assert maps.placement(identity).record.to_bytes() == (
        maps.placement(identity).original_bytes
    )


def test_an_unknown_placement_identity_is_refused(maps):
    from tools.webfoot.maps import PlacementIdentity, UnknownMapError

    with pytest.raises(UnknownMapError):
        maps.placement(PlacementIdentity(9999, 0))


def test_a_no_op_placement_pass_emits_no_differing_bytes(maps):
    assert not [change for change in maps.changes() if change.old != change.new]


def test_cli_round_trip_reports_the_placement_corpus(capsys):
    require_rom()
    assert main(["map", "validate-round-trip", str(LOCAL_ROM)]) == 0
    output = capsys.readouterr().out
    assert f"Placements checked: {PLACEMENT_COUNT} ({PLACEMENT_BYTES} bytes)" in output
    assert f"Maps with placements: {PLACEMENT_MAP_COUNT}" in output
    assert "Placement failures: 0" in output
    assert "RESULT:\nPASS" in output


def test_a_project_round_trip_carries_every_placement(tmp_path):
    require_rom()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    authored = (project / "maps" / "maps.toml").read_text(encoding="utf-8")
    assert authored.count("position_low") == PLACEMENT_COUNT

    report = validate_project(project, LOCAL_ROM, catalog())
    assert not report.problems

    output = tmp_path / "out.gba"
    build_project(project, LOCAL_ROM, output, catalog())
    assert output.read_bytes() == LOCAL_ROM.read_bytes()


def test_an_authored_placement_edit_changes_exactly_one_rom_byte(tmp_path):
    """The TOOLKIT-008 closure proof, through the whole project lifecycle."""
    require_rom()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    authored_file = project / "maps" / "maps.toml"
    text = authored_file.read_text(encoding="utf-8")
    before = '[map."map:0010".placements."placement:0000"]\nposition_low = 60'
    after = '[map."map:0010".placements."placement:0000"]\nposition_low = 76'
    assert before in text
    authored_file.write_text(text.replace(before, after, 1), encoding="utf-8", newline="\n")

    assert not validate_project(project, LOCAL_ROM, catalog()).problems

    output = tmp_path / "out.gba"
    manifest = tmp_path / "manifest.json"
    build_project(project, LOCAL_ROM, output, catalog(), manifest_path=manifest)

    base = LOCAL_ROM.read_bytes()
    built = output.read_bytes()
    differing = [i for i in range(len(base)) if base[i] != built[i]]
    assert differing == [0x72908]
    assert base[0x72908] == 0x3C
    assert built[0x72908] == 0x4C

    entries = [
        change
        for change in json.loads(manifest.read_text())["changes"]
        if change["owner"] == "map:0010/placement:0000"
    ]
    assert len(entries) == 1
    assert entries[0]["reason"] == "placement edit: position"

    repeated = tmp_path / "again.gba"
    build_project(project, LOCAL_ROM, repeated, catalog())
    assert repeated.read_bytes() == built

    assert hashlib.sha256(LOCAL_ROM.read_bytes()).hexdigest() == (
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
    )


def test_an_authored_placement_out_of_range_is_refused_before_a_build(tmp_path):
    require_rom()
    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    authored_file = project / "maps" / "maps.toml"
    text = authored_file.read_text(encoding="utf-8")
    authored_file.write_text(
        text.replace(
            '[map."map:0010".placements."placement:0000"]\nposition_low = 60',
            '[map."map:0010".placements."placement:0000"]\nposition_low = 70000',
            1,
        ),
        encoding="utf-8",
        newline="\n",
    )

    problems = validate_project(project, LOCAL_ROM, catalog()).problems
    assert any("position_low=70000" in problem for problem in problems)

    output = tmp_path / "out.gba"
    with pytest.raises(Exception):
        build_project(project, LOCAL_ROM, output, catalog())
    assert not output.exists()


def test_cli_lists_and_shows_placements_without_leaking_offsets(capsys):
    require_rom()
    assert main(["map", "placements", str(LOCAL_ROM), "map:0010"]) == 0
    listed = capsys.readouterr().out
    assert "map:0010/placement:0000" in listed
    assert "0x728fc" not in listed.lower()

    assert main(
        ["map", "placement", str(LOCAL_ROM), "map:0010/placement:0000"]
    ) == 0
    shown = capsys.readouterr().out
    assert "Identity: map:0010/placement:0000" in shown
    assert "axis UNKNOWN" in shown
    assert "0x728fc" not in shown.lower()


def test_cli_rejects_a_malformed_placement_identity(capsys):
    require_rom()
    assert main(["map", "placement", str(LOCAL_ROM), "map:0010"]) == 2
    assert "not a placement identity" in capsys.readouterr().err


def test_a_placement_edit_merges_with_map_stat_and_text_edits(tmp_path):
    """Sec 30: four subsystems, one merged plan, four attributed owners."""
    require_rom()
    import re

    project = tmp_path / "project"
    extract_project(LOCAL_ROM, project, catalog(), graphics=False)

    maps_file = project / "maps" / "maps.toml"
    text = maps_file.read_text(encoding="utf-8")
    start = text.index('[map."map:0039"]')
    end = text.index("\n[map.", start + 1)
    block = text[start:end]
    text = text[:start] + block.replace("music_id = 15", "music_id = 14", 1) + text[end:]
    text = text.replace(
        '[map."map:0010".placements."placement:0000"]\nposition_low = 60',
        '[map."map:0010".placements."placement:0000"]\nposition_low = 76',
        1,
    )
    maps_file.write_text(text, encoding="utf-8", newline="\n")

    enemies_file = project / "enemies" / "enemies.toml"
    enemies = enemies_file.read_text(encoding="utf-8")
    match = re.search(r"\[enemy\.\d+\]\n(.*?)(?=\n\[|\Z)", enemies, re.S)
    enemy_block = match.group(1)
    hp = int(re.search(r"hp = (\d+)", enemy_block).group(1))
    enemies_file.write_text(
        enemies.replace(
            enemy_block, enemy_block.replace(f"hp = {hp}", f"hp = {hp + 1}", 1), 1
        ),
        encoding="utf-8",
        newline="\n",
    )

    assert not validate_project(project, LOCAL_ROM, catalog()).problems

    manifest = tmp_path / "manifest.json"
    build_project(
        project, LOCAL_ROM, tmp_path / "out.gba", catalog(), manifest_path=manifest
    )
    owners = {
        change["owner"] for change in json.loads(manifest.read_text())["changes"]
    }
    assert "map:0010/placement:0000" in owners
    assert "map:0039" in owners
    assert any(owner.startswith("enemy:") for owner in owners)
