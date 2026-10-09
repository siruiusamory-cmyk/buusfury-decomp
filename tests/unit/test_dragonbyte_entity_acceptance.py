"""DRAGONBYTE-Z-ENTITIES-DESTINATION-001: the roadmap S7 acceptance proof.

The proof, verbatim from the roadmap:

    Per destination: one round-trip build asserting the owner identity, the
    change count and the manifest content; the change is visible in the ROM
    surface; the write goes through the one stack; each destination's
    unsupported rows offer no edit affordance and state their reason. No
    unproven relation appears anywhere.

Each clause is one test, measured rather than asserted where a measurement is
possible, and the measurements are printed so the closure report can quote them
(`pytest -q -s`). Everything goes through the product's own path: the page's own
switches and Apply, the shell's one journal, the platform's own Ctrl+Z action,
the ROM destination's own caret, and the SDK's own build and manifest.

The suite skips without the canonical image.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
from dataclasses import fields, replace
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.dragonbyte import dataedits  # noqa: E402
from tools.dragonbyte import entitypage  # noqa: E402
from tools.dragonbyte import entitysurface as es  # noqa: E402
from tools.dragonbyte.romsurface import PendingBytes  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.build import build_project, extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.formats import map_placements as mp  # noqa: E402
from tools.webfoot.placement_events import Descriptor  # noqa: E402
from tools.webfoot.project import read_project  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
    wait_for_text_surface,
)

#: The lowest map index whose placements the canonical image records, so the
#: destination opens on a map that owns the family it is about.
PLACED_MAP = 10

#: A map whose placement reaches the script-dispatch handler, so the attachment
#: columns have something to show and something to refuse.
SCRIPT_MAP = 19

#: The placement of PLACED_MAP the proof moves.
MOVED_PLACEMENT = 0


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
    directory = tmp_path_factory.mktemp("dbz-entity-acceptance") / "source"
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
def armed(qapp, tmp_path, catalog, canonical_rom, source_project):
    """A shell with the canonical image and a project, on the Entities destination."""
    session = Session()
    session.open_rom(canonical_rom)
    shutil.copytree(source_project, tmp_path / "project")
    session.open_project(tmp_path / "project")
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("entities")
    yield shell._entity_page, shell, session, tmp_path / "project"
    _close(shell, session)


# --- driving the page, through the widgets a user drives ----------------------


def _choose_map(page, index: int) -> None:
    page._maps.setCurrentIndex(page._maps.findData(index))
    assert page._map_index == index


def drive_one_position_edit(page, map_index: int, placement: int):
    """Move one placement's X, through the page's own field editor and Apply."""
    _choose_map(page, map_index)
    row = next(item for item in page._rows if item.placement_index == placement)
    assert row.editable

    page._field.setCurrentText("x")
    page._value.setText(str(row.x + 3))
    page._apply.click()

    return row


def _ctrl_z(shell) -> None:
    """The Undo action the platform's Ctrl+Z is bound to."""
    action = shell._edit_actions["Undo"]
    assert action.isEnabled()
    action.trigger()


def _authored_position(project_dir, map_index: int, placement: int) -> tuple[int, int]:
    """The position the project document on disk holds for one placement."""
    document = read_project(project_dir)
    item = next(
        row
        for row in document.maps[map_index]["placements"]
        if row["index"] == placement
    )
    return item["position_low"], item["position_high"]


@pytest.fixture
def edited(armed):
    """One placement move, committed through the page."""
    page, shell, session, project_dir = armed

    row = drive_one_position_edit(page, PLACED_MAP, MOVED_PLACEMENT)

    assert session.journal.depth == 1
    return page, shell, session, project_dir, row


@pytest.fixture
def built(edited, canonical_rom, catalog):
    """The same session, saved and built through the SDK's own build."""
    page, shell, session, project_dir, row = edited
    session.save_project()
    output = project_dir.parent / "built.gba"
    result = build_project(project_dir, canonical_rom, output, catalog)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    return page, shell, session, row, project_dir, output, manifest


# --- clause 1: the round-trip build -------------------------------------------


def test_clause_1_the_build_asserts_the_owner_the_change_count_and_the_manifest(
    built, canonical_rom
):
    page, shell, session, row, project_dir, output, manifest = built
    changes = manifest["changes"]
    canonical = canonical_rom.read_bytes()
    built_bytes = output.read_bytes()

    print("\nCLAUSE 1 | one round-trip build: owner identity, change count, manifest")
    print(f"  project            {session.project.meta.name}")
    print(f"  placement row      {row.identity} at 0x{row.file_offset:06X} ({row.size} bytes)")
    print(f"  journal entries    {session.journal.depth}")
    print(f"  manifest changes   {len(changes)}")
    print(f"  changed bytes      {manifest['changed_byte_count']}")
    for change in changes:
        print(
            f"  {change['owner']}  0x{change['offset']:06X} "
            f"{change['old']} -> {change['new']}  ({change['reason']})"
        )

    assert manifest["base"]["sha256"] == CANONICAL_SHA256
    assert manifest["project"]["name"] == session.project.meta.name
    assert manifest["output"]["sha256"] == hashlib.sha256(built_bytes).hexdigest()
    assert len(changes) == 1

    change = changes[0]
    assert change["owner"] == row.identity
    assert change["reason"] == "placement edit: position"
    assert change["offset"] == row.file_offset
    assert change["size"] == row.size
    assert bytes.fromhex(change["old"]) == canonical[
        row.file_offset : row.file_offset + row.size
    ]
    assert bytes.fromhex(change["new"]) == page._surface.pending_bytes(
        session.project
    )[row.file_offset]

    differing = {
        at
        for at, (old, new) in enumerate(zip(canonical, built_bytes))
        if old != new
    }
    claimed = {
        change["offset"] + at
        for at, (before, after) in enumerate(
            zip(bytes.fromhex(change["old"]), bytes.fromhex(change["new"]))
        )
        if before != after
    }
    assert differing == claimed
    assert manifest["changed_byte_count"] == len(claimed)
    assert built_bytes[
        change["offset"] : change["offset"] + change["size"]
    ] == bytes.fromhex(change["new"])
    assert _authored_position(project_dir, PLACED_MAP, MOVED_PLACEMENT) == (
        row.x + 3,
        row.y,
    )


def test_clause_1_a_rebuild_of_the_same_project_is_byte_identical(
    built, canonical_rom, catalog
):
    _page, _shell, _session, _row, project_dir, output, _manifest = built
    again = output.parent / "built-again.gba"
    build_project(project_dir, canonical_rom, again, catalog)

    print("\nCLAUSE 1 | a second build of the same project")
    print(f"  first   {hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(f"  second  {hashlib.sha256(again.read_bytes()).hexdigest()}")

    assert again.read_bytes() == output.read_bytes()


# --- clause 2: visible in the ROM surface -------------------------------------


def _visible_changed_cells(rom) -> list[str]:
    """Every changed-byte cell the rendered byte view is showing."""
    return [
        rom._model.data(rom._model.index(at, 4))
        for at in range(rom._model.rowCount())
        if rom._model.data(rom._model.index(at, 4)) != "-"
    ]


def test_clause_2_the_change_is_visible_in_the_rom_surface(edited):
    _page, shell, session, _project_dir, row = edited
    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")

    shell.open_rom_at(row.file_offset)
    cells = _visible_changed_cells(rom)

    print("\nCLAUSE 2 | the same bytes are visible in the ROM surface")
    print(f"  ROM caret             file offset 0x{rom._caret:06X}")
    print(f"  ROM changed column    {cells}")
    print(f"  ROM overlay           {sorted(hex(at) for at in rom._surface.overlay)}")
    print(f"  shell's one provider  {sorted(hex(at) for at in shell._pending_bytes().mapping)}")

    assert session.navigation.current.destination == "rom"
    assert rom._caret == row.file_offset
    assert row.file_offset in rom._surface.overlay
    assert cells
    assert rom._surface.current_bytes(row.file_offset, row.size) != (
        rom._surface.canonical_bytes(row.file_offset, row.size)
    )
    assert (
        rom._surface.pending[row.file_offset]
        == shell._pending_bytes().mapping[row.file_offset]
    )


def test_an_entities_provider_that_cannot_answer_states_its_reason(edited, monkeypatch):
    """An Entities provider that cannot encode its edit says so; never silent.

    This destination had no boundary of its own: a raise from the SDK used to
    reach the shell and be dropped. It now states the reason that the shell
    aggregates onto the ROM surface, beside the journal claim it could not fill.
    """
    page, shell, _session, _project_dir, row = edited
    reason = "the placement codec refused the record"

    def refuse(_surface, _project):
        raise RuntimeError(reason)

    monkeypatch.setattr(type(page._surface), "pending_bytes", refuse)
    wait_for_text_surface(shell)
    shell.open_rom_at(row.file_offset)
    rom = shell._rom_page
    merged = shell._pending_bytes()
    stated = f"Entities: the pending bytes could not be stated: {reason}"

    print("\nENTITIES PROVIDER FAILURE | the reason reaches the ROM surface")
    print(f"  page provider      {page.pending_bytes()}")
    print(f"  shell's merge      {merged.problem}")
    print(f"  ROM summary        {rom._summary.text()}")
    print(f"  ROM pending bytes  {sorted(hex(at) for at in rom._surface.pending)}")

    assert page.pending_bytes() == PendingBytes(
        problem=f"the pending bytes could not be stated: {reason}"
    )
    assert merged.problem == stated
    assert rom._surface.pending_problem == stated
    assert stated in rom._summary.text()
    assert row.file_offset in rom._surface.overlay
    assert row.file_offset not in rom._surface.pending
    assert rom._surface.current_bytes(
        row.file_offset, row.size
    ) == rom._surface.canonical_bytes(row.file_offset, row.size)


# --- clause 3: one stack ------------------------------------------------------


def test_clause_3_the_write_goes_through_the_one_stack(edited):
    _page, shell, session, project_dir, row = edited
    entries = session.journal.edits()
    canonical = _authored_position(project_dir, PLACED_MAP, MOVED_PLACEMENT)

    print("\nCLAUSE 3 | one journal, one stack, one selection")
    print(f"  entries            {len(entries)}")
    print(f"  targets            {[entry.target for entry in entries]}")
    print(f"  claimed            {[span.to_json() for entry in entries for span in entry.claimed]}")
    print(f"  authored on disk   {canonical} (before Save)")

    assert len(entries) == 1
    assert {entry.target for entry in entries} == {dataedits.DATA_TARGET}
    assert entries[0].claimed == (es.span(row),)
    assert canonical == (row.x, row.y), (
        "an unsaved edit must not have reached the project's documents"
    )

    session.save_project()

    assert _authored_position(project_dir, PLACED_MAP, MOVED_PLACEMENT) == (
        row.x + 3,
        row.y,
    )

    _ctrl_z(shell)

    undone = next(
        item
        for item in session.project.maps[PLACED_MAP]["placements"]
        if item["index"] == MOVED_PLACEMENT
    )
    print(
        f"  after Ctrl+Z       project holds "
        f"({undone['position_low']}, {undone['position_high']}); the document on "
        f"disk still holds the last save, {_authored_position(project_dir, PLACED_MAP, MOVED_PLACEMENT)}"
    )

    assert session.journal.depth == 0
    assert (undone["position_low"], undone["position_high"]) == (row.x, row.y)


def test_clause_3_one_edit_is_one_undo_entry_and_the_page_follows_it(edited):
    page, shell, session, _project_dir, row = edited

    _ctrl_z(shell)
    page.refresh()
    live = {change.offset for change in page._surface.changes(session.project)}

    print("\nCLAUSE 3 | one edit, one undo entry")
    print(f"  undo depth         {session.journal.depth}")
    print(f"  redo available     {session.journal.can_redo}")
    print(f"  live claimed bytes {sorted(hex(offset) for offset in live)}")

    assert session.journal.depth == 0
    assert session.journal.can_redo
    assert shell._edit_actions["Redo"].isEnabled()
    assert live == set()
    assert page._surface.pending_bytes(session.project) == {}


# --- clause 4: unsupported rows -----------------------------------------------


def test_clause_4_an_unmodelled_family_offers_no_edit_affordance(armed):
    page, _shell, _session, _project_dir = armed
    page._modes.setCurrentText("Object families")
    rows = page._rows

    print("\nCLAUSE 4 | the unmodelled family rows")
    print(f"  summary    {page._summary.text()}")
    print(f"  apply      {page._apply.isEnabled()}")
    print(f"  open bytes {page._open.isEnabled()}")
    print(f"  editor     {page._editor.isVisible()}")
    print(f"  message    {page._message.text()}")
    for row in rows[1:]:
        print(f"  {row.label:22} slot {row.pointer_slot}  stride {row.stride}  {row.support}")

    assert page._summary.text() == "Object families: 1 of 4 modelled"
    assert page._model.rowCount() == 4
    assert not page._apply.isEnabled()
    assert not page._open.isEnabled()
    assert not page._editor.isVisible()
    assert page._message.text() == entitypage._NO_FAMILY_EDITOR
    for row in rows[1:]:
        assert row.label == "Family not modelled"
        assert row.support == "Not supported yet"
        assert row.note
        assert row.basis


def test_clause_4_a_behaviour_row_states_why_it_is_read_only(armed):
    page, _shell, _session, _project_dir = armed
    _choose_map(page, SCRIPT_MAP)
    page._modes.setCurrentText("Behaviours")
    position = next(
        at for at, item in enumerate(page._rows) if item.attachment
    )
    row = page._rows[position]
    page._table.selectRow(position)

    print("\nCLAUSE 4 | a behaviour row")
    print(f"  behaviour  {row.identity}")
    print(f"  handler    {row.handler} at 0x{row.handler_address:08X}")
    print(f"  attachment {row.attachment}")
    print(f"  reason     {row.note}")
    print(f"  apply      {page._apply.isEnabled()}  open bytes {page._open.isEnabled()}")

    assert page._caret == row.identity
    assert not page._apply.isEnabled()
    assert page._open.isEnabled()
    assert "not editable here" in row.note
    assert row.attachment in page._detail.text()


def test_clause_4_an_undeclared_handler_states_a_reason_through_the_page(armed):
    """A handler raw outside the verified table must not reach the page as a raise."""
    page, _shell, _session, _project_dir = armed
    _choose_map(page, PLACED_MAP)
    page._modes.setCurrentText("Behaviours")

    descriptor = Descriptor(
        identity="undeclared/descriptor",
        record=mp.DescriptorRecord(handler_pointer_raw=0x08004219, payload_raw=0),
        file_offset=0,
        placements=(f"map:{PLACED_MAP:04d}/placement:0000",),
        event=None,
    )

    class _Undeclared:
        def descriptor_of(self, placement):
            return descriptor

    page._surface = replace(page._surface, events=_Undeclared())
    page.refresh()

    row = page._rows[0]
    handler_cell = page._model.data(page._model.index(0, 1))

    print("\nCLAUSE 4 | a behaviour row whose handler the table does not declare")
    print(f"  handler cell  {handler_cell!r}")
    print(f"  reason        {row.note}")
    print(f"  apply         {page._apply.isEnabled()}")

    assert page._model.rowCount() == 1
    assert row.handler == ""
    assert handler_cell == "not declared"
    assert "verified handler table does not declare" in row.note
    assert "does not declare" in page._detail.text()
    assert not page._apply.isEnabled()


def test_clause_4_a_placement_with_no_project_states_its_reason(
    qapp, tmp_path, catalog, canonical_rom
):
    """Without a project the family is readable and nothing may be edited."""
    session = Session()
    session.open_rom(canonical_rom)
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("entities")
    page = shell._entity_page
    row = page._rows[0]

    print("\nCLAUSE 4 | a placement row with no project open")
    print(f"  row        {row.identity}")
    print(f"  reason     {row.note}")
    print(f"  apply      {page._apply.isEnabled()}")
    print(f"  summary    {page._summary.text()}")
    print(f"  message    {page._message.text()}")
    print(f"  provider   {page.pending_bytes()}")

    assert not row.editable
    assert row.note == f"this project authors no placement record for {row.identity}"
    assert not page._apply.isEnabled()
    assert page._open.isEnabled()
    assert page.pending_bytes() == PendingBytes()
    assert "nothing to edit" in page._message.text()
    assert "Open a project to move one" in page._summary.text()

    _close(shell, session)


# --- clause 5: no unproven relation -------------------------------------------


def test_clause_5_an_attachment_appears_only_where_the_contract_decodes_one(armed):
    """The discriminating pair: one map attaches a script, another does not."""
    page, _shell, _session, _project_dir = armed

    _choose_map(page, SCRIPT_MAP)
    attached = [row for row in page._rows if row.attachment]
    _choose_map(page, PLACED_MAP)
    silent = [row for row in page._rows if not row.attachment]

    print("\nCLAUSE 5 | attachments, both ways")
    print(f"  map {SCRIPT_MAP} rows with an attachment   {[row.attachment for row in attached]}")
    print(f"  map {PLACED_MAP} rows without one           {silent[0].behaviour_note}")
    for row in attached + silent:
        descriptor = page._surface.events.descriptor_of(row.identity)
        assert row.attachment == (descriptor.event or "")
        if row.attachment:
            assert descriptor.record.handler_pointer_raw == 0x0800421F

    assert attached, "the worked example's attachment is missing"
    assert silent, "the null-handler case is missing"


def test_clause_5_the_product_modules_name_no_relation_the_evidence_refuses():
    """A source-level guard over the two modules the destination is made of."""
    sources = {
        "entitysurface": Path(es.__file__).read_text(encoding="utf-8"),
        "entitypage": Path(entitypage.__file__).read_text(encoding="utf-8"),
    }
    imported = set()
    for source in sources.values():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Import):
                imported.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)

    row_fields = {field.name for field in fields(es.PlacementRow)}
    forbidden_fields = {"sprite", "destination", "trigger", "audio", "shop", "item"}

    print("\nCLAUSE 5 | imported names and fields the product modules may not use")
    print(f"  MapGraph imported      {'MapGraph' in imported}")
    print(f"  MapConnection imported {'MapConnection' in imported}")
    print(f"  PlacementTypes imported {'PlacementTypes' in imported}")
    print(f"  'on_defeat' in source  {any('on_defeat' in source for source in sources.values())}")
    print(f"  placement row fields   {sorted(row_fields)}")

    assert "MapGraph" not in imported
    assert "MapConnection" not in imported
    assert "PlacementTypes" not in imported
    assert not (row_fields & forbidden_fields)
    for source in sources.values():
        assert "on_defeat" not in source, (
            "an attachment's trigger is not established for a canonical placement, "
            "so no surface may name one beside it"
        )
