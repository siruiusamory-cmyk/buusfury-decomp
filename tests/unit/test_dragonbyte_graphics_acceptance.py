"""DRAGONBYTE-Z-GRAPHICS-DESTINATION-001: the roadmap S7 acceptance proof.

The proof, verbatim from the roadmap:

    Per destination: one round-trip build asserting the owner identity, the
    change count and the manifest content; the change is visible in the ROM
    surface; the write goes through the one stack; each destination's unsupported
    rows offer no edit affordance and state their reason. No unproven relation
    appears anywhere.

Each clause is one test, measured rather than asserted where a measurement is
possible, and the measurements are printed so the closure report can quote them
(`pytest -q -s`). Everything goes through the product's own path: the page's own
mode switch and Apply, the shell's one journal, the platform's own Ctrl+Z action,
the ROM destination's own caret and overlay, and the SDK's own build and manifest.

This destination has ONE editable relation, the object-palette entry, and the proof
edits two entries rather than one: an entry the decoded actor-sprite corpus uses
and an entry it does not. The second is the point of the corpus-scoped consumer
count, so the build's own answer for it is measured rather than assumed.

The suite skips without the canonical image.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
from dataclasses import fields
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.dragonbyte import graphicsedits  # noqa: E402
from tools.dragonbyte import graphicspage  # noqa: E402
from tools.dragonbyte import graphicsurface as gs  # noqa: E402
from tools.dragonbyte.romsurface import PendingBytes  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.build import build_project, extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.project import read_project  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
)

#: The three colours the proof tries, in order, for an entry whose edit must
#: actually change bytes: a written palette word is packed from these channels, so
#: a colour that quantises onto the canonical word would be a no-op and would make
#: the first clause vacuous.
CANDIDATE_COLOURS = ((31, 0, 0), (0, 31, 0), (0, 0, 31))


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
    directory = tmp_path_factory.mktemp("dbz-graphics-acceptance") / "source"
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


def wait_for_surface(page, timeout_ms: int = 180_000) -> None:
    """Wait for the worker's read to land, exactly as a user's window does."""
    from PySide6.QtCore import QDeadlineTimer, QEventLoop

    deadline = QDeadlineTimer(timeout_ms)
    while page._surface_loading and not deadline.hasExpired():
        QEventLoop().processEvents()
    assert not page._surface_loading, "the graphics surface never finished loading"
    assert page._surface is not None, page._problem


@pytest.fixture
def armed(qapp, tmp_path, catalog, canonical_rom, source_project):
    """A shell with the canonical image and a project, on Graphics."""
    session = Session()
    session.open_rom(canonical_rom)
    shutil.copytree(source_project, tmp_path / "project")
    session.open_project(tmp_path / "project")
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("graphics")
    wait_for_surface(shell._graphics_page)
    yield shell._graphics_page, shell, session, tmp_path / "project"
    _close(shell, session)


# --- driving the page, through the widgets a user drives ----------------------


def _choose_mode(page, label: str) -> None:
    page._modes.setCurrentText(label)
    assert page._mode == {text: identifier for identifier, text in graphicspage.MODES}[
        label
    ]


def _point_at(page, row):
    """Put the page's caret on one row, without a Qt selection round trip."""
    page._caret = graphicspage._key(row)
    page._render_editor()
    return row


def _select(page, predicate):
    return _point_at(page, next(item for item in page._rows if predicate(item)))


def _pick_colour(surface, index) -> tuple[int, int, int]:
    """A colour that actually changes this entry's two bytes."""
    for rgb in CANDIDATE_COLOURS:
        problem, changes, _claimed = surface.plan(index, rgb)
        if problem == "" and changes:
            return rgb
    raise AssertionError(f"no candidate colour changes palette entry {index}")


def drive_palette_edit(page, row, rgb):
    """Recolour one object-palette entry, through the page's field and Apply."""
    _choose_mode(page, "Object palette")
    _point_at(page, row)
    assert page._apply.isEnabled(), page._apply.toolTip()

    page._value.setText(f"{rgb[0]}, {rgb[1]}, {rgb[2]}")
    page._apply.click()

    return row


def _ctrl_z(shell) -> None:
    """The Undo action the platform's Ctrl+Z is bound to."""
    action = shell._edit_actions["Undo"]
    assert action.isEnabled()
    action.trigger()


def _authored_palette(project_dir) -> dict:
    return read_project(project_dir).graphics_overrides.palette


# --- clause 1: the round-trip build -------------------------------------------


@pytest.fixture
def edited(armed):
    """Two palette edits through the page: one used by the corpus, one not."""
    page, shell, session, project_dir = armed
    rows = page._surface.palette_rows()
    used = next(row for row in rows if row.editable and row.users)
    free = next(row for row in rows if row.editable and not row.users)
    used_rgb = _pick_colour(page._surface, used.index)
    free_rgb = _pick_colour(page._surface, free.index)

    drive_palette_edit(page, used, used_rgb)
    assert session.journal.depth == 1, session.journal.depth
    drive_palette_edit(page, free, free_rgb)
    assert session.journal.depth == 2, session.journal.depth

    return page, shell, session, project_dir, (used, used_rgb), (free, free_rgb)


@pytest.fixture
def built(edited, canonical_rom, catalog):
    """The same session, saved and built through the SDK's own build."""
    page, shell, session, project_dir, used, free = edited
    session.save_project()
    output = project_dir.parent / "built.gba"
    result = build_project(project_dir, canonical_rom, output, catalog)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    return page, shell, session, project_dir, used, free, output, manifest


def test_clause_1_the_build_asserts_the_owner_the_change_count_and_the_manifest(
    built, canonical_rom
):
    page, shell, session, project_dir, used, free, output, manifest = built
    (used_row, used_rgb) = used
    (free_row, free_rgb) = free
    changes = manifest["changes"]
    canonical = canonical_rom.read_bytes()
    built_bytes = output.read_bytes()

    print("\nCLAUSE 1 | one round-trip build: owner identity, change count, manifest")
    print(f"  project            {session.project.meta.name}")
    print(f"  used entry         {used_row.index:03d} "
          f"({len(used_row.users)} of {used_row.corpus} decoded graphics)")
    print(f"  unreferenced entry {free_row.index:03d} "
          f"(0 of {free_row.corpus} decoded graphics)")
    print(f"  journal entries    {session.journal.depth}")
    print(f"  manifest changes   {len(changes)}")
    print(f"  changed bytes      {manifest['changed_byte_count']}")
    for change in changes:
        print(
            f"  {change['owner']}  0x{change['offset']:06X} "
            f"{change['old']} -> {change['new']}  ({change['reason']})"
        )

    assert manifest["base"]["sha256"] == CANONICAL_SHA256
    assert manifest["output"]["sha256"] == hashlib.sha256(built_bytes).hexdigest()

    # Two edits, two changes, one two-byte write each: a palette recolour rewrites
    # the entry in place and nothing else.
    assert len(changes) == 2
    assert {change["owner"] for change in changes} == {
        f"palette_entry:{used_row.index:03d}",
        f"palette_entry:{free_row.index:03d}",
    }
    by_owner = {change["owner"]: change for change in changes}
    for row, rgb in (used, free):
        change = by_owner[f"palette_entry:{row.index:03d}"]
        assert change["offset"] == page._surface.palette_address + row.index * 2
        assert change["size"] == 2
        assert bytes.fromhex(change["old"]) == canonical[
            change["offset"] : change["offset"] + 2
        ]
        assert bytes.fromhex(change["new"]) == page._surface.pending_bytes(
            session.project
        )[change["offset"]]
        print(f"  entry {row.index:03d} asked for {rgb}, manifest says "
              f"{change['reason']}")

    claimed = {
        item["offset"] + at
        for item in changes
        for at, (before, after) in enumerate(
            zip(bytes.fromhex(item["old"]), bytes.fromhex(item["new"]))
        )
        if before != after
    }
    overlap = range(min(len(canonical), len(built_bytes)))
    differing = {at for at in overlap if canonical[at] != built_bytes[at]}
    assert differing == claimed, "the built image differs outside the manifest's claim"
    assert manifest["changed_byte_count"] == len(claimed)

    # The authored document holds exactly the two entries, and the SDK's own reader
    # agrees with the manifest about which they are.
    document = _authored_palette(project_dir)
    assert document == {used_row.index: used_rgb, free_row.index: free_rgb}


def test_clause_1_a_rebuild_of_the_same_project_is_byte_identical(
    built, canonical_rom, catalog
):
    _page, _shell, _session, project_dir, _used, _free, output, _manifest = built
    again = project_dir.parent / "rebuilt.gba"

    build_project(project_dir, canonical_rom, again, catalog)

    print("\nCLAUSE 1 | rebuild")
    print(f"  first   {hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(f"  again   {hashlib.sha256(again.read_bytes()).hexdigest()}")

    assert again.read_bytes() == output.read_bytes()


# --- clause 2: visible in the ROM surface -------------------------------------


def _visible_changed_cells(rom) -> list[str]:
    """Every changed-byte cell the rendered byte view is showing."""
    return [
        rom._model.data(rom._model.index(at, 4))
        for at in range(rom._model.rowCount())
        if rom._model.data(rom._model.index(at, 4)) != "-"
    ]


def test_clause_2_the_palette_change_is_visible_in_the_rom_surface(edited):
    page, shell, session, _project_dir, (used_row, _used_rgb), _free = edited
    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")
    offset = page._surface.palette_address + used_row.index * 2

    shell.open_rom_at(offset)
    cells = _visible_changed_cells(rom)

    print("\nCLAUSE 2 | the palette entry's bytes are visible in the ROM surface")
    print(f"  ROM caret             file offset 0x{rom._caret:06X}")
    print(f"  ROM changed column    {cells[:3]}")
    print(f"  shell's one provider  "
          f"{sorted(hex(at) for at in shell._pending_bytes().mapping)}")

    assert session.navigation.current.destination == "rom"
    assert rom._caret == offset
    assert offset in rom._surface.overlay
    assert cells
    assert rom._surface.pending[offset] == shell._pending_bytes().mapping[offset]


def test_a_graphics_provider_that_cannot_answer_states_its_reason(edited, monkeypatch):
    """The fifth provider is not a silent one: a refusal is stated, never empty.

    A Graphics provider that cannot encode its edit reports the reason, which
    travels into the ROM summary, while the pending mapping stays empty and the
    overlay is untouched. A bare mapping here would leave the ROM surface showing
    canonical bytes beside the journal's claim with nothing saying why.
    """
    page, shell, session, _project_dir, (used_row, _used_rgb), _free = edited
    reason = "the palette codec refused the entry"
    offset = page._surface.palette_address + used_row.index * 2

    def refuse(_surface, _project):
        raise RuntimeError(reason)

    monkeypatch.setattr(type(page._surface), "pending_bytes", refuse)
    shell.open_rom_at(offset)
    rom = shell._rom_page
    merged = shell._pending_bytes()
    stated = f"Graphics: the pending palette bytes could not be stated: {reason}"

    print("\nGRAPHICS PROVIDER FAILURE | the reason reaches the ROM surface")
    print(f"  page provider      {page.pending_bytes()}")
    print(f"  shell's merge      {merged.problem}")
    print(f"  ROM summary        {rom._summary.text()}")
    print(f"  ROM pending bytes  {sorted(hex(at) for at in rom._surface.pending)}")

    assert page.pending_bytes() == PendingBytes(
        problem=f"the pending palette bytes could not be stated: {reason}"
    )
    # Membership, because the shell's one merge carries every destination's own
    # reason and another destination may still be reading its records.
    assert stated in merged.problem.split("; ")
    assert stated in rom._surface.pending_problem.split("; ")
    assert stated in rom._summary.text()
    assert offset in rom._surface.overlay
    assert offset not in rom._surface.pending
    assert rom._surface.current_bytes(offset, 2) == rom._surface.canonical_bytes(
        offset, 2
    )


def test_a_graphics_page_that_cannot_read_yet_states_that_and_never_nothing(armed):
    """The unread case, which is the one a user actually meets on a cold open."""
    page, shell, _session, _project_dir = armed

    page._surface = None
    page._problem = "the graphics records are still loading"

    print("\nCLAUSE 2 | the unread provider")
    print(f"  page provider  {page.pending_bytes()}")

    assert page.pending_bytes() == PendingBytes(
        problem="the graphics records are still loading"
    )


# --- clause 3: one stack ------------------------------------------------------


def test_clause_3_the_write_goes_through_the_one_stack(edited):
    page, shell, session, project_dir, (used_row, used_rgb), (free_row, free_rgb) = edited
    entries = session.journal.edits()
    on_disk = _authored_palette(project_dir)

    print("\nCLAUSE 3 | one journal, one stack, one target")
    print(f"  entries            {len(entries)}")
    print(f"  targets            {[entry.target for entry in entries]}")
    print(f"  owners             {[entry.owner for entry in entries]}")
    print(f"  reasons            {[entry.reason for entry in entries]}")
    print(f"  claimed            {[span.to_json() for entry in entries for span in entry.claimed]}")
    print(f"  authored on disk   {on_disk} (before Save)")

    assert len(entries) == 2
    assert {entry.target for entry in entries} == {graphicsedits.GRAPHICS_TARGET}
    assert on_disk == {}, (
        "an unsaved edit must not have reached the project's documents"
    )

    # The bytes the one journal protects are the bytes the plan writes, as a set.
    problem, plan_changes, plan_spans = page._surface.plan(used_row.index, used_rgb)
    assert problem == ""
    entry = entries[0]
    assert tuple(entry.claimed) == tuple(plan_spans)
    assert {span.start.value for span in entry.claimed} == {
        change.offset for change in plan_changes
    }

    session.save_project()

    assert _authored_palette(project_dir) == {
        used_row.index: used_rgb,
        free_row.index: free_rgb,
    }

    _ctrl_z(shell)

    print(f"  after Ctrl+Z       {session.project.graphics_overrides.palette}")

    assert session.journal.depth == 1
    assert session.project.graphics_overrides.palette == {used_row.index: used_rgb}


def test_clause_3_one_edit_is_one_undo_entry_and_the_page_follows_it(edited):
    page, shell, session, project_dir, (used_row, used_rgb), (free_row, _free_rgb) = edited

    print("\nCLAUSE 3 | one edit, one undo entry")
    for step in (1, 2):
        _ctrl_z(shell)
        assert session.journal.depth == 2 - step

    # Every step back, and the byte effect of the whole destination with it: the
    # project authors nothing and the provider contributes no pending bytes.
    assert session.project.graphics_overrides.palette == {}
    assert page._surface.pending_bytes(session.project) == {}

    _point_at(page, used_row)
    page._value.setText(f"{used_rgb[0]}, {used_rgb[1]}, {used_rgb[2]}")
    page._apply.click()

    assert session.journal.depth == 1
    assert session.project.graphics_overrides.palette == {used_row.index: used_rgb}
    assert page._surface.pending_bytes(session.project)

    shell.undo_edit()

    assert session.project.graphics_overrides.palette == {}


# --- clause 4: unsupported rows offer no affordance and state their reason ------


def test_clause_4_the_transparent_entry_offers_no_edit_and_states_its_reason(armed):
    page, _shell, _session, _project_dir = armed
    _choose_mode(page, "Object palette")
    row = _select(page, lambda item: item.index == gs.TRANSPARENT_INDEX)

    print("\nCLAUSE 4 | an unsupported row")
    print(f"  entry            {row.index}")
    print(f"  editable         {row.editable}")
    print(f"  reason           {row.unsupported_reason}")
    print(f"  Apply enabled    {page._apply.isEnabled()}")
    print(f"  field enabled    {page._value.isEnabled()}")
    print(f"  Apply tooltip    {page._apply.toolTip()}")
    print(f"  page message     {page._message.text()}")

    assert row.editable is False
    assert page._apply.isEnabled() is False
    assert page._value.isEnabled() is False
    assert page._apply.toolTip() == row.unsupported_reason
    assert row.unsupported_reason.lower() in page._message.text().lower()
    assert "not offered" in page._message.text()


def test_clause_4_every_read_only_mode_offers_no_edit_at_all(armed):
    page, _shell, _session, _project_dir = armed

    print("\nCLAUSE 4 | the read-only modes")
    for label in ("Actor sprites", "Sprite payloads", "Appearance records"):
        _choose_mode(page, label)
        row = _select(page, lambda item: True)
        print(f"  {label:20s} editor visible {page._editor.isVisible()} "
              f"Apply enabled {page._apply.isEnabled()} rows {len(page._rows)}")
        assert page._editor.isVisible() is False
        assert page._apply.isEnabled() is False
        assert page._rows
        assert row is not None

    _choose_mode(page, "Other graphics systems")
    rows = page._rows
    print(f"  {'Other systems':20s} editor visible {page._editor.isVisible()} "
          f"Apply enabled {page._apply.isEnabled()} rows {len(rows)}")
    assert page._editor.isVisible() is False
    assert page._apply.isEnabled() is False
    assert len(rows) == len(gs.OTHER_SYSTEMS)
    assert all(row.reason and row.status and row.evidence for row in rows)


def test_clause_4_a_palette_edit_without_a_project_states_its_reason(
    qapp, tmp_path, catalog, canonical_rom
):
    session = Session()
    session.open_rom(canonical_rom)
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("graphics")
    page = shell._graphics_page
    wait_for_surface(page)

    try:
        _choose_mode(page, "Object palette")
        row = _select(
            page, lambda item: item.editable and item.users
        )

        print("\nCLAUSE 4 | no project open")
        print(f"  entry          {row.index}")
        print(f"  Apply enabled  {page._apply.isEnabled()}")
        print(f"  Apply tooltip  {page._apply.toolTip()}")
        print(f"  page message   {page._message.text()}")

        assert page._apply.isEnabled() is False
        assert page._apply.toolTip() == graphicspage._NO_PROJECT
        assert page._message.text() == graphicspage._NO_PROJECT
        assert page.pending_bytes() == PendingBytes()
    finally:
        _close(shell, session)


# --- clause 5: no unproven relation -------------------------------------------


def test_clause_5_the_product_modules_name_no_relation_the_evidence_refuses():
    """A source-level guard over the three modules this destination is made of."""
    sources = {
        "graphicsurface": Path(gs.__file__).read_text(encoding="utf-8"),
        "graphicspage": Path(graphicspage.__file__).read_text(encoding="utf-8"),
        "graphicsedits": Path(graphicsedits.__file__).read_text(encoding="utf-8"),
    }
    imported = set()
    for source in sources.values():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Import):
                imported.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)

    forbidden_fields = {"placement", "shop", "trigger", "item", "audio", "bank",
                        "palette_bank"}
    rows = (gs.CharacterRow, gs.PayloadRow, gs.AppearanceRow, gs.PaletteRow,
            gs.OtherRow)
    named = {field.name for cls in rows for field in fields(cls)}

    print("\nCLAUSE 5 | imported names and fields the product modules may not use")
    print(f"  imported names        {sorted(imported)}")
    print(f"  row fields            {sorted(named)}")

    assert "workbench" not in " ".join(sorted(imported)), (
        "the application never imports the beta desktop package"
    )
    assert not (named & forbidden_fields), named & forbidden_fields
    # No second graphics decoder: the model reaches the image only through the
    # SDK's own actor-sprite walk, and decodes no tile, palette or container of
    # its own.
    assert not (
        imported
        & {"unswizzle_tiles", "swizzle_tiles", "pack_gba_colour", "decode_palette",
           "decode_piece", "decode_frame", "decode_graphic", "indexed_png"}
    ), imported
    # No name is invented for a system the evidence does not name: every row of
    # the coverage view carries the matrix's own words and its citation.
    assert all(
        entry[3].startswith("docs/research/GRAPHICS_COVERAGE.md:")
        for entry in gs.OTHER_SYSTEMS
    )


def test_clause_5_the_consumer_count_always_names_its_corpus(armed):
    """The trap: a consumer count that reads as "unused anywhere"."""
    page, _shell, _session, _project_dir = armed
    _choose_mode(page, "Object palette")
    rows = page._surface.palette_rows()
    corpus = len(page._surface.sprites.graphics())

    print("\nCLAUSE 5 | every palette row states the corpus it counted")
    print(f"  corpus                 {corpus} decoded actor-sprite graphics")
    print(f"  entries the corpus uses {sum(1 for row in rows if row.users)}")
    print(f"  entries it does not     {sum(1 for row in rows if not row.users)}")
    print(f"  disclosure             {page._surface.palette_disclosure(rows[0].index)[:200]}")

    assert corpus > 0
    for row in rows:
        assert "not counted and not excluded" in row.consumer_text
        assert not row.consumer_text.startswith("0 consumer")
        assert "unused" not in row.consumer_text
        if not row.users:
            assert row.consumer_text.startswith(
                f"0 of {corpus} decoded actor-sprite graphics"
            )


def test_clause_5_no_per_sprite_palette_is_presented_anywhere(armed):
    page, _shell, _session, _project_dir = armed
    from PySide6.QtCore import Qt

    _choose_mode(page, "Object palette")
    headers = [
        page._model.headerData(
            at, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
        )
        for at in range(page._model.columnCount())
    ]
    identity = page._identity_line.text()

    print("\nCLAUSE 5 | no per-sprite palette")
    print(f"  headers        {headers}")
    print(f"  identity line  {identity[:200]}")

    assert headers
    assert "bank" not in " ".join(headers).lower()
    assert "is not decoded anywhere in this project" in identity
    assert "A recolour is an exact two-byte write" in identity
