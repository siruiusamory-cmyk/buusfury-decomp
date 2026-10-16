"""DRAGONBYTE-Z-DATA-SURFACES-001: the roadmap S6 acceptance proof, clause by clause.

The proof, verbatim from the roadmap:

    One stat edit produces one change owned by the record identity; the same
    offset is visible in the ROM surface; one Ctrl+Z reverts both views; the
    coverage view's counts equal the census totals recomputed from the census
    data file.

Each clause is one test, measured rather than asserted where a measurement is
possible, and the measurements are printed so the closure report can quote them
(`pytest -q -s`). Everything goes through the product's own path: the page's
Apply, the shell's one journal, the README's own Ctrl+Z action, and the rendered
cells a user reads.

The suite skips without the canonical image.
"""

from __future__ import annotations

import os
import shutil

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.dragonbyte import coverage  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.build import extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.dragonbyte_acceptance_support import (  # noqa: E402, F401
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
    one_decode,
    surfaces,
)

GAMES = ("buus_fury", "logii", "log1")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


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
def source_project(tmp_path_factory, catalog, canonical_rom):
    directory = tmp_path_factory.mktemp("dbz-data-acceptance") / "source"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture(autouse=True)
def no_range_index(monkeypatch):
    """The atlas is not part of this proof; the byte view needs no index."""
    from tools.dragonbyte import rompage

    monkeypatch.setattr(
        rompage,
        "load_index",
        lambda profile, directory=None: (None, "the range index is not loaded here"),
    )


@pytest.fixture
def armed(qapp, tmp_path, canonical_rom, source_project):
    """A shell with the canonical image and a project, on the Data destination."""
    session = Session()
    session.open_rom(canonical_rom)
    shutil.copytree(source_project, tmp_path / "project")
    session.open_project(tmp_path / "project")
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("data")
    yield shell._data_page, shell, session
    _close(shell, session)


def _apply(page, field: str, value: int) -> None:
    page._field.setCurrentText(field)
    page._value.setText(str(value))
    page._apply.click()


def _ctrl_z(shell) -> None:
    """The Undo action the platform's Ctrl+Z is bound to."""
    action = shell._edit_actions["Undo"]
    assert action.isEnabled()
    action.trigger()


# --- clause 1 -----------------------------------------------------------------


def test_clause_1_one_stat_edit_produces_one_change_owned_by_the_record_identity(
    armed,
):
    page, shell, session = armed
    row = page._rows[0]
    value = row.field("hp").value + 1

    _apply(page, "hp", value)

    changes = page._surface.changes(session.project)
    entries = session.journal.edits()

    print("\nCLAUSE 1 | one stat edit -> one change owned by the record identity")
    print(f"  record identity   {row.identity}")
    print(f"  file offset       0x{row.file_offset:06X}")
    print(f"  edits committed   {len(entries)}")
    print(f"  changes           {len(changes)}")
    for change in changes:
        print(
            f"  change.owner      {change.owner}\n"
            f"  change.offset     0x{change.offset:06X}\n"
            f"  change.old        {change.old.hex()}\n"
            f"  change.new        {change.new.hex()}"
        )

    assert len(entries) == 1
    assert len(changes) == 1
    assert changes[0].owner == row.identity
    assert changes[0].offset == row.file_offset
    assert changes[0].old != changes[0].new
    assert session.project.enemies[row.key]["hp"] == value


# --- clause 2 -----------------------------------------------------------------


def test_clause_2_the_same_offset_is_visible_in_the_rom_surface(armed):
    page, shell, session = armed
    row = page._rows[0]
    value = row.field("hp").value + 1

    _apply(page, "hp", value)
    page._open.click()
    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")
    changed = rom._model.data(rom._model.index(0, 4))
    visible = rom._surface.current_bytes(row.file_offset, row.size)

    print("\nCLAUSE 2 | the same offset is visible in the ROM surface")
    print(f"  Data record        {row.identity} at 0x{row.file_offset:06X}")
    print(f"  ROM caret          file offset 0x{rom._caret:06X}")
    print(f"  ROM overlay        {sorted(hex(at) for at in rom._surface.overlay)[:4]} ...")
    print(f"  ROM pending at it  {rom._surface.pending[row.file_offset].hex()}")
    print(f"  ROM current bytes  {visible.hex()}")
    print(f"  ROM canonical      {rom._surface.canonical_bytes(row.file_offset, row.size).hex()}")
    print(f"  ROM changed column {changed}")

    assert session.navigation.current.destination == "rom"
    assert rom._caret == row.file_offset
    assert row.file_offset in rom._surface.overlay
    assert rom._surface.current_bytes(row.file_offset, row.size) != (
        rom._surface.canonical_bytes(row.file_offset, row.size)
    )
    assert changed != "-"
    assert rom._surface.pending[row.file_offset] == page._surface.pending_bytes(
        session.project
    )[row.file_offset]


# --- clause 3 -----------------------------------------------------------------


def test_clause_3_one_ctrl_z_reverts_both_views(armed):
    page, shell, session = armed
    row = page._rows[0]
    before_bytes = page._surface.tables.enemy(row.key).original_bytes
    value = row.field("hp").value + 1

    _apply(page, "hp", value)
    page._open.click()
    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")
    edited_data_cell = page._caret_row().field("hp").value
    edited_rom_cell = rom._model.data(rom._model.index(0, 4))

    _ctrl_z(shell)

    # The Data view is read where a user reads it: showing the destination
    # refreshes it, exactly as it refreshes the ROM page.
    shell.show_destination("data")
    reverted_data_cell = page._caret_row().field("hp").value
    reverted_rom_cell = rom._model.data(rom._model.index(0, 4))
    reverted_bytes = rom._surface.current_bytes(row.file_offset, row.size)

    print("\nCLAUSE 3 | one Ctrl+Z reverts both views")
    print(f"  Data before / edited / after  {row.field('hp').value} / {edited_data_cell} / {reverted_data_cell}")
    print(f"  ROM changed before / after    {edited_rom_cell} / {reverted_rom_cell}")
    print(f"  ROM bytes after               {reverted_bytes.hex()}")
    print(f"  canonical bytes               {before_bytes.hex()}")
    print(f"  journal depth after            {session.journal.depth}")

    assert edited_data_cell == value
    assert edited_rom_cell != "-"
    assert reverted_data_cell == row.field("hp").value
    assert session.journal.depth == 0
    assert reverted_rom_cell == "-"
    assert row.file_offset not in rom._surface.overlay
    assert reverted_bytes == before_bytes
    assert session.project.enemies[row.key]["hp"] == row.field("hp").value


def test_clause_3_one_edit_is_one_undo_entry_not_two(armed):
    page, shell, session = armed
    row = page._rows[0]

    _apply(page, "hp", row.field("hp").value + 1)

    assert session.journal.depth == 1
    assert shell._edit_actions["Undo"].isEnabled()
    assert shell._edit_actions["Redo"].isEnabled() is False

    _ctrl_z(shell)

    assert session.journal.depth == 0
    assert shell._edit_actions["Undo"].isEnabled() is False
    assert shell._edit_actions["Redo"].isEnabled()


# --- clause 4 -----------------------------------------------------------------


def test_clause_4_the_coverage_counts_equal_the_census_recomputed_from_the_file(
    armed,
):
    page, _shell, session = armed
    page._modes.setCurrentText("Coverage")
    document = coverage.load_census()

    states = tuple(document["vocabularies"]["coverage_states"])
    expected = {
        state: sum(
            1
            for row in document["rows"]
            if row["games"][page._coverage.game_id]["state"] == state
        )
        for state in states
    }
    rendered = {group.state: group.cells for group in page._coverage.groups}

    print("\nCLAUSE 4 | coverage counts == census totals recomputed from the data file")
    print(f"  profile           {session.profile.id}")
    print(f"  title             {page._coverage.title}")
    print(f"  census rows       {len(document['rows'])}")
    print(f"  published totals  {{k: v for k, v in document['totals']['by_game'][page._coverage.game_id].items()}}")
    print(f"  recomputed        {expected}")
    print(f"  view              {rendered}")
    print(f"  rendered rows     {page._model.rowCount()}")

    assert rendered == expected
    assert page._model.rowCount() == len(document["rows"])
    published = document["totals"]["by_game"][page._coverage.game_id]
    assert rendered == {state: published[state] for state in states}


def test_clause_4_holds_for_every_title_the_census_names():
    """The same equality for each title, so the view is not right by accident."""
    document = coverage.load_census()
    states = tuple(document["vocabularies"]["coverage_states"])

    for game in document["games"]:
        view = coverage.coverage_view(document, game["profile_id"])
        recomputed = {
            state: sum(
                1
                for row in document["rows"]
                if row["games"][game["id"]]["state"] == state
            )
            for state in states
        }

        print(f"CLAUSE 4 | {game['id']}: {recomputed}")

        assert {group.state: group.cells for group in view.groups} == recomputed
