"""The Graphics model: actor sprites, payloads, appearances and the one palette.

The acceptance proof next door measures the round trip on a real build. This file
measures the model directly, because the facts it pins are the ones a build cannot
show: which corpus a palette consumer count covers, that no per-sprite palette or
bank label exists to be shown, and that every read-only row states its reason.

The suite skips without the canonical image.
"""

from __future__ import annotations

from dataclasses import fields, replace

import pytest

from tools.dragonbyte import graphicsurface as gs
from tools.webfoot.binary import GBA_ROM_BASE
from tools.webfoot.catalog import load_catalog
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.graphics import GraphicIdentity
from tools.webfoot.project import GraphicsOverrides, ProjectMeta, StatProject
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
    identification = identify_rom(canonical_rom, catalog)
    profile = identification.profile_match.profile
    return gs.load_graphics_surface(
        identification, profile, canonical_rom.read_bytes()
    )


@pytest.fixture(scope="module")
def project(surface):
    meta = ProjectMeta(
        format_version=1,
        profile_id=surface.profile.id,
        game=surface.profile.id,
        base_rom_sha256=surface.profile.sha256,
        base_rom_size=len(surface.image),
        name="staging",
    )
    return StatProject(meta=meta, enemies={}, characters={})


# --- what the four views hold -------------------------------------------------


def test_the_actor_sprite_identity_and_payload_views_are_the_sdk_corpus(surface):
    characters = surface.character_rows()
    payloads = surface.payload_rows()

    print("\nMODEL | actor sprites")
    print(f"  character slots  {len(characters)}")
    print(f"  distinct payloads {len(payloads)}")
    print(f"  shared payloads  {sum(1 for row in payloads if row.shared)}")
    print(f"  first character  {characters[0].identity} animations "
          f"{characters[0].animations} payloads {characters[0].payloads}")

    assert len(characters) == len(surface.sprites.characters())
    assert len(payloads) == len(surface.sprites.graphics())
    assert characters[0].identity.startswith(surface.profile.id + "/character:")
    assert payloads[0].identity.startswith(surface.profile.id + "/graphic:")
    assert all(row.payloads > 0 for row in characters)
    assert all(row.note.startswith("read-only") for row in characters)
    assert all(row.note.startswith("read-only") for row in payloads)


def test_a_payload_discloses_the_frames_and_characters_that_reach_it(surface):
    """The consumers a shared payload affects, from the walk that decoded them."""
    rows = surface.payload_rows()
    shared = [row for row in rows if row.shared]

    assert shared, "no shared payload on the canonical image, which is unexpected"

    row = shared[0]
    graphic = surface.sprites.graphic(
        GraphicIdentity(surface.profile.id, row.index)
    )

    print("\nMODEL | shared payload")
    print(f"  payload          {row.identity}")
    print(f"  frames           {len(row.frames)}")
    print(f"  characters       {len(row.characters)}")
    print(f"  disclosure       {row.disclosure[:120]}")

    assert row.frames == tuple(c.frame_offset for c in graphic.consumers)
    assert len(row.frames) > 1
    assert "frame record" in row.disclosure


def test_the_appearance_rows_are_the_profile_declared_table(surface):
    from tools.webfoot.appearances import read_records

    rows = surface.appearance_rows()
    records = read_records(surface.image, surface.profile)

    print("\nMODEL | appearance definitions")
    print(f"  records          {len(rows)}")
    print(f"  first            text {rows[0].text_index} sprite {rows[0].sprite_id} "
          f"portrait {rows[0].portrait_slot} stat {rows[0].stat_index}")

    assert len(rows) == len(records) == surface.profile.appearances.count
    for row, record in zip(rows, records):
        assert (row.text_index, row.description_index, row.sprite_id) == (
            record.text_index,
            record.description_index,
            record.sprite_id,
        )
        assert row.portrait_slot == record.portrait_slot
        assert row.stat_index == record.stat_index
        assert row.address == row.file_offset + GBA_ROM_BASE
    assert all(row.note.startswith("read-only") for row in rows)


# --- the one palette, and the corpus its count covers --------------------------


def test_the_palette_view_is_one_table_of_256_entries(surface):
    rows = surface.palette_rows()

    print("\nMODEL | object palette")
    print(f"  entries          {len(rows)}")
    print(f"  address          0x{surface.palette_address + GBA_ROM_BASE:08X}")
    print(f"  entry 0          {rows[0].rgb} editable {rows[0].editable}")
    print(f"  identity line    {surface.palette_identity_line()}")

    assert len(rows) == gs.PALETTE_ENTRIES == 256
    assert [row.index for row in rows] == list(range(256))
    assert rows[0].raw == surface.sprites.palette.raw[0]
    assert rows[17].rgb == surface.sprites.palette.rgb[17]

    # The narrow truth about editing through RGB: the SDK packs the word from the
    # channels, so an entry whose canonical word carries a bit the round trip does
    # not reproduce changes even when the displayed colour is the same. Measured,
    # and stated so the claim above is not a guess.
    not_round_tripping = [
        row.index
        for row in rows
        if sg.pack_gba_colour(*row.rgb) != row.raw
    ]

    print(f"  words not reproduced by an RGB round trip: "
          f"{len(not_round_tripping)} {not_round_tripping[:8]}")


def test_every_palette_count_names_the_corpus_it_counted(surface):
    """The trap this pins: a count without its corpus reads as "unused"."""
    rows = surface.palette_rows()
    corpus = len(surface.sprites.graphics())
    used = [row for row in rows if row.users]
    unused = [row for row in rows if not row.users]

    print("\nMODEL | palette consumers")
    print(f"  corpus           {corpus} decoded actor-sprite graphics")
    print(f"  entries in use   {len(used)}")
    print(f"  entries unused   {len(unused)}")
    print(f"  example used     {used[0].consumer_text[:150]}")
    print(f"  example unused   {unused[0].consumer_text}")

    assert used and unused
    for row in used:
        assert f"{len(row.users)} of {corpus} decoded actor-sprite graphics" in (
            row.consumer_text
        )
        assert row.users == tuple(
            str(identity)
            for identity in surface.sprites.palette_users(row.index)
        )
    for row in unused:
        assert row.consumer_text.startswith(f"0 of {corpus} decoded actor-sprite")
    for row in rows:
        assert "not counted and not excluded" in row.consumer_text
        assert "unused" not in row.consumer_text


def test_no_per_sprite_palette_and_no_bank_label_exists_to_be_shown(surface):
    """Which palette bank a sprite uses is not decoded, so no field names one."""
    forbidden = {"bank", "palette_bank", "palette", "sprite_palette"}

    for cls in (gs.PaletteRow, gs.PayloadRow, gs.CharacterRow, gs.AppearanceRow):
        names = {field.name for field in fields(cls)}
        assert not (names & forbidden), (cls.__name__, names & forbidden)

    palette = surface.palette_rows()[0]
    assert not hasattr(palette, "bank")
    assert "is not decoded anywhere in this project" in (
        surface.palette_disclosure(palette.index)
    )


def test_the_transparent_entry_offers_no_edit_and_states_its_reason(surface):
    rows = surface.palette_rows()
    entry_zero = rows[gs.TRANSPARENT_INDEX]

    print("\nMODEL | unsupported row")
    print(f"  index            {entry_zero.index}")
    print(f"  editable         {entry_zero.editable}")
    print(f"  reason           {entry_zero.unsupported_reason}")

    assert entry_zero.editable is False
    assert "transparent" in entry_zero.unsupported_reason
    assert all(row.editable for row in rows[1:])


def test_the_systems_outside_the_actor_sprite_pipeline_are_inert_and_reasoned(surface):
    rows = surface.other_rows()

    print("\nMODEL | other graphics systems")
    for row in rows:
        print(f"  {row.name}: {row.status}")

    assert len(rows) == len(gs.OTHER_SYSTEMS)
    assert all(row.reason and row.status for row in rows)
    assert all(row.evidence.startswith("docs/research/GRAPHICS_COVERAGE.md:") for row in rows)
    # No row carries an address, an identity or an edit flag: there is nothing to
    # offer an affordance for, which is the point.
    names = {field.name for field in fields(gs.OtherRow)}
    assert names == {"name", "status", "reason", "evidence"}


# --- the edit -----------------------------------------------------------------


def test_the_plan_names_the_builds_own_owner_and_the_exact_two_bytes(surface):
    index = next(
        row.index for row in surface.palette_rows() if row.editable and row.users
    )
    rgb = (31, 0, 0)

    problem, changes, claimed = surface.plan(index, rgb)

    print("\nMODEL | plan")
    print(f"  index            {index}")
    print(f"  problem          {problem!r}")
    print(f"  owner            {changes[0].owner}")
    print(f"  offset           0x{changes[0].offset:06X}")
    print(f"  old -> new       {changes[0].old.hex()} -> {changes[0].new.hex()}")
    print(f"  claimed          {[(c.start.value, c.size) for c in claimed]}")

    assert problem == ""
    assert len(changes) == 1
    change = changes[0]
    assert change.owner == f"palette_entry:{index:03d}"
    assert change.offset == surface.palette_address + index * 2
    assert change.old == surface.image[change.offset : change.offset + 2]
    assert len(change.new) == 2
    assert change.old != change.new
    assert [(span.start.value, span.size) for span in claimed] == [
        (change.offset, 2)
    ]


def test_a_recolour_to_the_colour_already_there_plans_no_change(surface):
    row = next(row for row in surface.palette_rows() if row.editable and row.users)

    problem, changes, claimed = surface.plan(row.index, row.rgb)

    print("\nMODEL | no-op recolour")
    print(f"  index            {row.index}")
    print(f"  canonical rgb    {row.rgb}")
    print(f"  changes          {len(changes)}")

    assert problem == ""
    assert changes == ()
    assert claimed == ()


@pytest.mark.parametrize("index", [-1, 256, "1", None])
def test_an_index_outside_the_palette_is_refused_with_its_reason(surface, index):
    problem, changes, claimed = surface.plan(index, (1, 2, 3))

    assert problem
    assert changes == ()
    assert claimed == ()


def test_the_pending_bytes_are_the_authored_entries_and_only_where_they_differ(
    surface, project
):
    rows = surface.palette_rows()
    used = [row for row in rows if row.editable and row.users]
    changed = used[0]
    # An entry whose canonical word carries the bit an RGB round trip cannot
    # reproduce is deliberately not the "already that colour" case: recolouring it
    # to its own displayed colour is a real byte change, and that is the honest
    # reason this test picks an entry that does round trip.
    same = next(
        row for row in used[1:] if sg.pack_gba_colour(*row.rgb) == row.raw
    )
    authored = replace(
        project,
        graphics_overrides=GraphicsOverrides(
            palette={changed.index: (0, 0, 31), same.index: same.rgb}
        ),
    )

    pending = surface.pending_bytes(authored)
    changes = surface.changes(authored)

    print("\nMODEL | pending bytes")
    print(f"  changed entry    {changed.index} -> {pending}")
    print(f"  owners           {[c.owner for c in changes]}")

    offset = surface.palette_address + changed.index * 2
    assert set(pending) == {offset}
    assert len(pending[offset]) == 2
    assert [c.owner for c in changes] == [f"palette_entry:{changed.index:03d}"]


def test_an_image_without_a_decoded_corpus_states_the_reason_and_rows_nothing(
    surface,
):
    broken = replace(
        surface,
        sprites=None,
        sprites_problem="this image declares no actor-sprite family",
    )

    print("\nMODEL | corpus absent")
    print(f"  palette rows     {len(broken.palette_rows())}")
    print(f"  palette summary  {broken.palette_summary(None)}")
    print(f"  sprite summary   {broken.sprite_summary()}")

    assert broken.palette_rows() == ()
    assert broken.character_rows() == ()
    assert broken.payload_rows() == ()
    assert "no actor-sprite family" in broken.palette_summary(None)
    assert "no actor-sprite family" in broken.sprite_summary()
    # The other two views still answer: an absent sprite family is not an absent
    # appearance table, and the destination states each family's own problem.
    assert broken.appearance_rows() == surface.appearance_rows()
    assert broken.other_rows() == surface.other_rows()
    assert broken.plan(1, (1, 2, 3))[0] == broken.sprites_problem
