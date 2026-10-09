"""The Scripts & Text model, its journal adapter and its page, without a build.

The acceptance proof next door measures the round trip on a real build. This file
measures the model and the adapter directly, so a regression in a row's identity,
in the two systems' separation or in the write path fails in seconds rather than
after a build.

The suite skips without the canonical image.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from tools.dragonbyte import textedits
from tools.dragonbyte.journal import DOCUMENT_ADAPTERS
from tools.webfoot.binary import GBA_ROM_BASE, FileOffset
from tools.webfoot.catalog import load_catalog
from tools.webfoot.formats.text_tables import TextIdentity
from tools.webfoot.layout import RomRange
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom

from tests.unit.test_dragonbyte_state import CANONICAL_SHA256, SIBLING_CHECKOUT


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
def surface(canonical_rom, catalog):
    from tools.dragonbyte import textsurface as ts

    identification = identify_rom(canonical_rom, catalog)
    profile = identification.profile_match.profile
    return ts.load_text_surface(
        canonical_rom,
        catalog,
        identification,
        profile,
        canonical_rom.read_bytes(),
    )


# --- the model ---------------------------------------------------------------


def test_every_family_the_profile_declares_loads_and_states_its_roots(surface):
    from tools.dragonbyte import textsurface as ts

    families = {row.family for row in surface.families}

    print("\nMODEL | script families")
    print(f"  families  {sorted(families)}")
    print(f"  summary   {ts.family_summary(surface.families)}")

    assert families == {"static40", "item_use", "placement_descriptor_event"}
    assert surface.family_problem == ""
    for family in families:
        roots = surface.script_roots(family)
        assert roots, family
        for root in roots:
            assert root.identity
            assert root.size > 0
            assert root.address == root.file_offset + 0x08000000


def test_a_script_attachment_comes_only_from_the_verified_contract(surface):
    owned = surface.script_attachments("placement_descriptor_event")
    item = surface.script_attachments("item_use")

    print("\nMODEL | attachments")
    print(f"  descriptors {len(owned)}  items {len(item)}")

    assert len(item) == 23
    assert all(name.startswith("item:") for name in item)
    assert all(name.endswith("/descriptor") for name in owned)
    assert not surface.script_attachments("static40")


def test_the_event_corpus_and_its_proven_text_references(surface):
    from tools.dragonbyte import textsurface as ts

    rows = surface.event_rows()
    with_text = [row for row in rows if row.text_indices]

    print("\nMODEL | event resources")
    print(f"  records            {len(rows)}")
    print(f"  proven text refs   {sum(len(row.text_indices) for row in rows)}")
    print(f"  summary            {ts.event_summary(rows)}")

    assert len(rows) == 522
    assert sum(len(row.text_indices) for row in rows) == 7
    assert with_text
    for row in rows:
        assert row.dialog_type
        assert row.note


def test_the_string_table_is_the_pointer_table_and_nothing_else(surface):
    from tools.dragonbyte import textsurface as ts

    rows = surface.string_rows()

    print("\nMODEL | string tables")
    print(f"  slots     {len(rows)}")
    print(f"  identity  {rows[0].identity} .. {rows[-1].identity}")
    print(f"  summary   {ts.string_summary(rows)}")

    assert len(rows) == 1534
    assert {row.system for row in rows} == {ts.STRING_SYSTEM}
    assert {row.identity_form for row in rows} == {"pointer-table slot"}
    assert rows[0].identity == "text:0000"
    assert rows[-1].identity == "text:1533"
    assert all(row.editable for row in rows)
    assert {row.index for row in rows} == set(range(1534))


def test_the_two_text_systems_cannot_be_confused(surface):
    from tools.dragonbyte import textsurface as ts

    strings = surface.string_rows()
    dialogue = surface.dialogue_rows()

    print("\nMODEL | the two systems")
    print(f"  string rows    {len(strings)}  {ts.STRING_IDENTITY_LINE}")
    print(f"  dialogue rows  {len(dialogue)}  {ts.SPOKEN_IDENTITY_LINE}")

    assert strings and dialogue
    assert {row.identity for row in strings} & {
        row.identity for row in dialogue
    } == set()
    assert {row.system for row in dialogue} == {ts.SPOKEN_SYSTEM}
    assert {row.identity_form for row in dialogue} == {"packed handle"}
    string_fields = {item.name for item in dc_fields(strings[0])}
    dialogue_fields = {item.name for item in dc_fields(dialogue[0])}
    assert not (string_fields & {"selector", "decoded_start", "decoded_length"})
    assert not (dialogue_fields & {"allocation", "index"})


def dc_fields(row):
    from dataclasses import fields

    return fields(row)


def test_one_dialogue_edit_has_an_authored_target_and_all_others_state_why_not(surface):
    authored = surface.authored_dialogue()
    editable = [row for row in surface.dialogue_rows() if row.editable]
    unsupported = [row for row in surface.dialogue_rows() if not row.editable]

    print("\nMODEL | the authored target")
    print(f"  targets      {[target.name for target in authored]}")
    print(f"  editable     {len(editable)}")
    print(f"  unsupported  {len(unsupported)}")

    assert len(authored) == 1
    assert len(editable) == 1
    assert editable[0].authoring_name == authored[0].name
    assert editable[0].text == surface.dialogue_text(authored[0])
    for row in unsupported:
        assert row.note
        assert row.event_resources == () or not row.editable


def test_a_dialogue_record_is_never_linked_to_a_string_slot(surface):
    """The relation the evidence refuses: a record is not a text index."""
    for row in surface.dialogue_rows():
        assert not hasattr(row, "text_index")
        assert not hasattr(row, "string")
        assert all(isinstance(index, int) for index in row.event_resources)
        assert row.sites_outside >= 0
        if not row.sites:
            assert row.event_resources == ()


def test_a_replacement_the_container_cannot_hold_is_refused_by_the_sdk(surface):
    target = surface.authored_dialogue()[0]

    print("\nMODEL | refusals")
    print(f"  a good replacement   {surface.dialogue_problem(target, 'Nice work, Goku!')!r}")
    print(f"  an empty one         {surface.dialogue_problem(target, '')!r}")
    print(f"  an over-long one     {surface.dialogue_problem(target, 'z' * 200)[:80]!r}")

    assert surface.dialogue_problem(target, "Nice work, Goku!") == ""
    assert "empty" in surface.dialogue_problem(target, "")
    assert "container decoder" in surface.dialogue_problem(target, "z" * 200)


def test_an_over_long_string_states_the_sdk_refusal_and_a_fitting_one_does_not(surface):
    identity = TextIdentity(2)
    entry = surface.strings.entry(identity)
    _problem, changes, claimed = surface.plan(identity, "Fight!")
    refused, _changes, _spans = surface.plan(identity, "z" * 200)

    print("\nMODEL | string refusals")
    print(f"  allocation          {entry.location.allocation}")
    print(f"  a fitting edit      changes {[(hex(c.offset), c.size) for c in changes]}")
    print(f"                      claimed {[span.to_json() for span in claimed]}")
    print(f"  an over-long edit   {refused[:80]!r}")

    assert "bytes too long" in refused
    assert claimed == (RomRange(FileOffset(entry.location.file_offset), entry.location.allocation),)


def test_a_relocating_edit_claims_the_bytes_the_plan_actually_writes(surface):
    """The defect this pins: a claim taken from the canonical position is wrong.

    `text:0000` holds an empty string in a 2-byte allocation, so any real text
    must relocate. The plan then writes the body at the allocator's span and
    rewrites this entry's POINTER-TABLE slot to name it, and nothing at all at
    0x05792C. A claim computed from the record's own position would mark the old
    address in the ROM surface and leave the bytes that change unguarded.
    """
    from tools.webfoot.formats.text_tables import TEXT_POINTER_SIZE

    identity = TextIdentity(0)
    entry = surface.strings.entry(identity)
    problem, changes, claimed = surface.plan(identity, "Relocate me")

    print("\nMODEL | a relocating edit's claim")
    print(f"  record     {identity} at 0x{entry.location.file_offset:06X} "
          f"allocation {entry.location.allocation}")
    print(f"  problem    {problem!r}")
    print(f"  changes    {[(hex(change.offset), change.size, change.reason) for change in changes]}")
    print(f"  claimed    {[span.to_json() for span in claimed]}")

    assert problem == ""
    assert len(claimed) == len(changes)
    # The plan's own changes as a set, which is the whole requirement.
    assert {span.start.value for span in claimed} == {
        change.offset for change in changes
    }
    assert RomRange(
        FileOffset(entry.location.file_offset), entry.location.allocation
    ) not in claimed
    # One change is the pointer-table slot this entry is reached through, so the
    # new body is reachable; the other is the body at the span the allocator chose.
    table_offset = (
        surface.profile.text_strings.pointer_table_address.raw - GBA_ROM_BASE
    )
    assert table_offset in {change.offset for change in changes}
    assert all(change.new != change.old for change in changes)


def test_the_surface_stages_every_pending_string_edit_it_is_handed(surface):
    identity = TextIdentity(2)
    project = _empty_project(surface, {identity: "Fight!"})

    changes = surface.changes(project)

    print("\nMODEL | staged changes")
    print(f"  changes  {[(change.owner, hex(change.offset)) for change in changes]}")

    assert len(changes) == 1
    assert changes[0].owner == "text:0002"
    assert changes[0].reason == "text edit"
    assert surface.pending_bytes(project) == {changes[0].offset: changes[0].new}


def test_a_string_whose_text_already_matches_stages_no_change(surface):
    identity = TextIdentity(2)
    project = _empty_project(surface, {identity: "Options"})

    assert surface.changes(project) == ()
    assert surface.pending_bytes(project) == {}


def _empty_project(surface, strings):
    """A project carrying only the documents a string edit needs."""
    from tools.webfoot.project import ProjectMeta, StatProject

    meta = ProjectMeta(
        format_version=1,
        profile_id=surface.profile.id,
        game=surface.profile.id,
        base_rom_sha256=surface.profile.sha256,
        base_rom_size=len(surface.image),
        name="staging",
    )
    return StatProject(meta=meta, enemies={}, characters={}, strings=dict(strings))


# --- the adapter -------------------------------------------------------------


def test_the_journal_registers_the_string_target_beside_the_dialogue_one():
    assert textedits.TEXT_TARGET in DOCUMENT_ADAPTERS
    assert "dialogues" in DOCUMENT_ADAPTERS
    assert textedits.TEXT_TARGET != "dialogues"


def test_the_adapter_round_trips_the_string_document(canonical_rom, catalog, tmp_path):
    from tools.webfoot.build import extract_project

    source = tmp_path / "source"
    extract_project(canonical_rom, source, catalog, graphics=False)
    project = read_project(source)
    payload = textedits.read(project)
    identity = TextIdentity(2)

    assert payload.strings[identity] == "Options"

    edited = replace(payload, strings={**payload.strings, identity: "Fight!"})
    written = tmp_path / "written"
    textedits.write(written, edited)
    again = read_project(written)

    print("\nADAPTER | round trip")
    print(f"  source slot 2   {payload.strings[identity]!r}")
    print(f"  written slot 2  {again.strings[identity]!r}")
    print(f"  strings written {len(again.strings)}")

    assert again.strings[identity] == "Fight!"
    assert len(again.strings) == len(project.strings)
    assert (written / "text" / "strings.toml").is_file()


def test_a_payload_carrying_another_identity_or_a_foreign_key_is_refused(
    canonical_rom, catalog, tmp_path
):
    from tools.webfoot.build import extract_project

    source = tmp_path / "source2"
    extract_project(canonical_rom, source, catalog, graphics=False)
    project = read_project(source)
    payload = textedits.read(project)

    with pytest.raises(textedits.TextEditError):
        textedits.validate(project, replace(payload, meta=replace(payload.meta, name="other")))
    with pytest.raises(textedits.TextEditError):
        textedits.validate(project, replace(payload, strings={"text:0002": "x"}))
    with pytest.raises(textedits.TextEditError):
        textedits.validate(project, "not a string document")
