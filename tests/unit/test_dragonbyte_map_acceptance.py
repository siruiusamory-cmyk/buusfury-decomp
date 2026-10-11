"""DRAGONBYTE-Z-MAPS-DESTINATION-001: the roadmap S7 acceptance proof for Maps.

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

import hashlib
import json
import os
import shutil
from dataclasses import replace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.dragonbyte import mapsurface as ms  # noqa: E402
from tools.dragonbyte.romsurface import PendingBytes  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.binary import FileOffset  # noqa: E402
from tools.webfoot.build import build_project, extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.layout import RomRange  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.dragonbyte_acceptance_support import (  # noqa: E402, F401
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
    one_decode,
    surfaces,
    wait_for_text_surface,
)

#: A map whose dominant layer offers more than one chunk, so a cell can be
#: repainted: the journey's own bounded operation.
PAINT_MAP = 0

#: A map whose dominant grid is a single chunk, so no cell may be repainted.
ONE_CHUNK_MAP = 1

#: A map the image carries a transition out of.
DOORED_MAP = 33


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
    directory = tmp_path_factory.mktemp("dbz-map-acceptance") / "source"
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
    """A shell with the canonical image and a project, on the Maps destination."""
    session = Session()
    session.open_rom(canonical_rom)
    shutil.copytree(source_project, tmp_path / "project")
    session.open_project(tmp_path / "project")
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("maps")
    yield shell._map_page, shell, session, tmp_path / "project"
    _close(shell, session)


# --- driving the page, through the widgets a user drives ----------------------


def _choose_map(page, index: int) -> None:
    page._maps.setCurrentIndex(page._maps.findData(index))
    assert page._map_index == index


def _choose_layer(page, slot: int) -> None:
    layers = page._surface.layers(page._map_index)
    position = next(at for at, entry in enumerate(layers) if entry.slot == slot)
    page._layers.setCurrentIndex(position)
    assert page._slot == slot


def drive_one_cell_edit(page, map_index: int):
    """Paint one cell of the map's first paintable layer, through Apply."""
    _choose_map(page, map_index)
    layer = next(
        entry
        for entry in page._surface.layers(map_index)
        if entry.editable and entry.chunk_count > 1
    )
    _choose_layer(page, layer.slot)
    row = page._rows[0]
    assert row.ordinal != layer.chunk_count

    page._value.setText(str(layer.chunk_count))
    page._apply.click()

    return row


def drive_one_warp_edit(page, map_index: int):
    """Retarget the map's first transition, through Apply."""
    _choose_map(page, map_index)
    page._modes.setCurrentText("Warps")
    row = page._rows[0]
    assert row.editable

    page._value.setText(str(row.destination + 1))
    page._apply.click()

    return row


@pytest.fixture
def edited(armed):
    """One cell paint and one retarget, both committed through the page."""
    page, shell, session, project_dir = armed

    cell = drive_one_cell_edit(page, PAINT_MAP)
    warp = drive_one_warp_edit(page, DOORED_MAP)

    assert session.journal.depth == 2
    return page, shell, session, project_dir, cell, warp


@pytest.fixture
def built(edited, canonical_rom, catalog):
    """The same session, saved and built through the SDK's own build."""
    page, shell, session, project_dir, cell, warp = edited
    session.save_project()
    output = project_dir.parent / "built.gba"
    result = build_project(project_dir, canonical_rom, output, catalog)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    return page, shell, session, cell, warp, output, manifest


def _ctrl_z(shell) -> None:
    """The Undo action the platform's Ctrl+Z is bound to."""
    action = shell._edit_actions["Undo"]
    assert action.isEnabled()
    action.trigger()


# --- clause 1: the round-trip build -------------------------------------------


def test_clause_1_the_build_asserts_the_owner_the_change_count_and_the_manifest(
    built, canonical_rom
):
    page, shell, session, cell, warp, output, manifest = built
    changes = manifest["changes"]
    by_owner = {change["owner"]: change for change in changes}
    canonical = canonical_rom.read_bytes()
    built_bytes = output.read_bytes()

    print("\nCLAUSE 1 | one round-trip build: owner identity, change count, manifest")
    print(f"  project            {session.project.meta.name}")
    print(f"  cell row           {cell.identity} at 0x{cell.offset:06X}")
    print(f"  warp row           {warp.identity} at 0x{warp.file_offset:06X}")
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
    assert set(by_owner) == {cell.identity, warp.identity}
    assert len(changes) == 2

    cell_change = by_owner[cell.identity]
    assert cell_change["offset"] == cell.offset
    assert cell_change["size"] == 4
    assert bytes.fromhex(cell_change["old"]) == canonical[
        cell.offset : cell.offset + 4
    ]
    assert bytes.fromhex(cell_change["new"]) == page._surface.pending_bytes(
        session.project
    )[cell.offset]

    warp_change = by_owner[warp.identity]
    assert warp_change["offset"] == warp.file_offset
    assert warp_change["size"] == warp.size
    assert bytes.fromhex(warp_change["old"]) == canonical[
        warp.file_offset : warp.file_offset + warp.size
    ]

    counted = sum(
        sum(
            1
            for old, new in zip(bytes.fromhex(c["old"]), bytes.fromhex(c["new"]))
            if old != new
        )
        for c in changes
    )
    assert manifest["changed_byte_count"] == counted

    differing = {
        at
        for at, (old, new) in enumerate(zip(canonical, built_bytes))
        if old != new
    }
    claimed: set[int] = set()
    for change in changes:
        old = bytes.fromhex(change["old"])
        new = bytes.fromhex(change["new"])
        claimed.update(
            change["offset"] + at
            for at, (before, after) in enumerate(zip(old, new))
            if before != after
        )
        assert built_bytes[
            change["offset"] : change["offset"] + change["size"]
        ] == new
    assert differing == claimed
    assert manifest["changed_byte_count"] == len(claimed)


def test_clause_1_the_transition_provenance_names_the_same_identity(built):
    _page, _shell, _session, _cell, warp, _output, manifest = built

    provenance = manifest["transition_edits"]

    print("\nCLAUSE 1 | the manifest's transition provenance")
    print(f"  {provenance}")

    assert provenance
    assert provenance[0]["identity"] == warp.identity
    assert provenance[0]["file_offset"] == warp.file_offset
    assert provenance[0]["destination"] != provenance[0]["prior_destination"]


def test_clause_1_a_rebuild_of_the_same_project_is_byte_identical(
    built, canonical_rom, catalog
):
    _page, _shell, _session, _cell, _warp, output, _manifest = built
    project_dir = output.parent / "project"
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
    page, shell, session, _project_dir, cell, warp = edited
    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")

    shell.open_rom_at(warp.file_offset)
    warp_cells = _visible_changed_cells(rom)
    shell.open_rom_at(cell.offset)
    cell_cells = _visible_changed_cells(rom)

    print("\nCLAUSE 2 | the same bytes are visible in the ROM surface")
    print(f"  ROM caret last        file offset 0x{rom._caret:06X}")
    print(f"  ROM changed column    {cell_cells} (cell edit) / {warp_cells} (warp edit)")
    print(f"  ROM overlay           {sorted(hex(at) for at in rom._surface.overlay)}")
    print(f"  shell's one provider  {sorted(hex(at) for at in shell._pending_bytes().mapping)}")

    assert session.navigation.current.destination == "rom"
    assert rom._caret == cell.offset
    assert {cell.offset, warp.file_offset} <= set(rom._surface.overlay)
    assert cell_cells and warp_cells
    for offset, size in ((cell.offset, 4), (warp.file_offset, warp.size)):
        assert rom._surface.current_bytes(offset, size) != rom._surface.canonical_bytes(
            offset, size
        )
        assert rom._surface.pending[offset] == shell._pending_bytes().mapping[offset]


def test_a_maps_provider_that_cannot_answer_states_its_reason(edited, monkeypatch):
    """A Maps provider that cannot encode its edit says so; it is never silent.

    The destination's own surface is made to fail after a real edit has been
    committed, so the case is the one a user hits: the journal holds the claim,
    the encoder cannot turn it into bytes, and the ROM surface must state that
    rather than showing canonical bytes as though nothing were pending.
    """
    page, shell, _session, _project_dir, cell, _warp = edited
    reason = "the layout codec refused the cell"

    def refuse(_surface, _project):
        raise RuntimeError(reason)

    monkeypatch.setattr(type(page._surface), "pending_bytes", refuse)
    wait_for_text_surface(shell)
    shell.open_rom_at(cell.offset)
    rom = shell._rom_page
    merged = shell._pending_bytes()
    stated = f"Maps: the pending bytes could not be stated: {reason}"

    print("\nMAPS PROVIDER FAILURE | the reason reaches the ROM surface")
    print(f"  page provider      {page.pending_bytes()}")
    print(f"  shell's merge      {merged.problem}")
    print(f"  ROM summary        {rom._summary.text()}")
    print(f"  ROM pending bytes  {sorted(hex(at) for at in rom._surface.pending)}")

    assert page.pending_bytes() == PendingBytes(
        problem=f"the pending bytes could not be stated: {reason}"
    )
    assert stated in merged.problem.split("; ")
    assert stated in rom._surface.pending_problem.split("; ")
    assert stated in rom._summary.text()
    assert cell.offset in rom._surface.overlay
    assert cell.offset not in rom._surface.pending
    assert rom._surface.current_bytes(cell.offset, 4) == rom._surface.canonical_bytes(
        cell.offset, 4
    )


# --- clause 3: one stack ------------------------------------------------------


def test_clause_3_the_write_goes_through_the_one_stack(edited):
    _page, shell, session, project_dir, cell, warp = edited
    entries = session.journal.edits()

    print("\nCLAUSE 3 | one journal, one stack, one selection")
    print(f"  entries            {len(entries)}")
    print(f"  targets            {[entry.target for entry in entries]}")
    print(f"  owners             {[entry.owner for entry in entries]}")
    print(
        f"  claimed            "
        f"{[span.to_json() for entry in entries for span in entry.claimed]}"
    )

    assert len(entries) == 2
    assert {entry.target for entry in entries} == {ms.MAPS_TARGET}
    assert [entry.claimed for entry in entries] == [
        (ms.layout_span(cell),),
        (RomRange(FileOffset(warp.file_offset), warp.size),),
    ]
    assert not (project_dir / "maps" / "layout.toml").exists(), (
        "an unsaved edit must not have reached the project's documents"
    )

    session.save_project()

    assert (project_dir / "maps" / "layout.toml").is_file()
    assert (project_dir / "maps" / "transitions.toml").is_file()

    _ctrl_z(shell)

    assert session.journal.depth == 1
    assert session.project.transitions.edits() == {}
    assert session.project.layout.cells() == {(cell.map_index, cell.slot, cell.cell): cell.maximum}


def test_clause_3_one_edit_is_one_undo_entry_and_the_page_follows_it(edited):
    page, shell, session, _project_dir, cell, warp = edited

    _ctrl_z(shell)
    page.refresh()
    live = {change.offset for change in page._surface.changes(session.project)}

    print("\nCLAUSE 3 | one edit, one undo entry")
    print(f"  undo depth         {session.journal.depth}")
    print(f"  redo available     {session.journal.can_redo}")
    print(f"  live claimed bytes {sorted(hex(offset) for offset in live)}")

    assert session.journal.depth == 1
    assert session.journal.can_redo
    assert shell._edit_actions["Redo"].isEnabled()
    assert warp.file_offset not in live
    assert cell.offset in live


# --- clause 4: unsupported rows -----------------------------------------------


def test_clause_4_an_unsupported_layer_offers_no_edit_affordance(armed):
    page, _shell, _session, _project_dir = armed
    _choose_map(page, ONE_CHUNK_MAP)
    layer = next(
        entry
        for entry in page._surface.layers(ONE_CHUNK_MAP)
        if not entry.editable and entry.note
    )
    _choose_layer(page, layer.slot)

    print("\nCLAUSE 4 | an unsupported layer row")
    print(f"  layer      {layer.identity}")
    print(f"  support    read-only")
    print(f"  reason     {layer.note}")
    print(f"  apply      {page._apply.isEnabled()}")
    print(f"  open bytes {page._open.isEnabled()}")

    assert page._layers.currentText().endswith("(read-only)")
    assert page._model.rowCount() == 0
    assert page._message.text() == layer.note
    assert not page._apply.isEnabled()
    assert not page._open.isEnabled()
    assert page._caret_row() is None


def test_clause_4_a_read_only_warp_states_its_reason(armed, monkeypatch):
    page, _shell, _session, _project_dir = armed
    _choose_map(page, DOORED_MAP)
    page._modes.setCurrentText("Warps")
    row = replace(
        page._rows[0],
        destination=None,
        destination_text="unresolved",
        editable=False,
        note="its destination key resolves to no map in this profile's table",
    )
    monkeypatch.setattr(page._surface, "warps", lambda project, map_index: (row,))
    page.refresh()

    print("\nCLAUSE 4 | an unsupported warp row")
    print(f"  row     {row.identity}")
    print(f"  reason  {row.note}")

    assert not page._apply.isEnabled()
    assert row.note in page._detail.text()
    assert "Read-only" in page._model.data(page._model.index(0, 5))


# --- clause 5: no unproven relation -------------------------------------------


def test_clause_5_no_unproven_relation_appears_anywhere(armed):
    """The map region's only proven map-to-map edge is the transition record."""
    page, _shell, _session, _project_dir = armed

    graph = page._surface.maps.graph()
    resolved = [
        connection
        for connection in graph.connections
        if connection.destination is not None
    ]

    print("\nCLAUSE 5 | the unproven edge")
    print(f"  MapGraph connections          {len(graph.connections)}")
    print(f"  with a resolved destination   {resolved}")
    print(f"  warps shown for map 0033      {len(page._surface.warps(map_index=DOORED_MAP))}")

    assert resolved == [], (
        "the map graph resolves no destination, so no surface may show one"
    )
    assert "destination" not in ms.MapRow.__dataclass_fields__
    for row in page._surface.warps():
        if row.editable:
            assert row.destination is not None
            entry = page._surface.maps.entry(ms.MapIdentity(row.destination))
            assert entry.identity.index == row.destination


def test_clause_5_the_model_reads_the_graph_nowhere(armed):
    """A source-level guard: the module must not import the unproven edge."""
    import ast
    from pathlib import Path

    page, _shell, _session, _project_dir = armed
    names = set()
    for module in (ms, __import__("tools.dragonbyte.mappage", fromlist=["x"])):
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names.update(alias.name for alias in node.names)

    print("\nCLAUSE 5 | imported names the product modules may not use")
    print(f"  MapGraph imported      {'MapGraph' in names}")
    print(f"  MapConnection imported {'MapConnection' in names}")

    assert "MapGraph" not in names
    assert "MapConnection" not in names
