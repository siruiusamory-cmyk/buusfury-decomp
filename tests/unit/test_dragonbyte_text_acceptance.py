"""DRAGONBYTE-Z-SCRIPTS-TEXT-DESTINATION-001: the roadmap S7 acceptance proof.

The proof, verbatim from the roadmap:

    Per destination: one round-trip build asserting the owner identity, the
    change count and the manifest content; the change is visible in the ROM
    surface; the write goes through the one stack; each destination's unsupported
    rows offer no edit affordance and state their reason. No unproven relation
    appears anywhere.

Each clause is one test, measured rather than asserted where a measurement is
possible, and the measurements are printed so the closure report can quote them
(`pytest -q -s`). Everything goes through the product's own path: the page's own
switch and Apply, the shell's one journal, the platform's own Ctrl+Z action, the
ROM destination's own caret, and the SDK's own build and manifest.

This destination carries TWO text systems and the proof edits one of each, because
a green suite that quietly offered the wrong system's editor is the failure this
ticket exists to prevent.

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

from tools.dragonbyte import textedits  # noqa: E402
from tools.dragonbyte import textpage  # noqa: E402
from tools.dragonbyte import textsurface as ts  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.build import build_project, extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.formats.text_tables import TextIdentity  # noqa: E402
from tools.webfoot.project import read_project  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
)

#: The string-table slot the proof edits, and what it holds on the canonical
#: image. A slot is identity: the address it sits at is not.
SLOT = TextIdentity(2)
SLOT_TEXT = "Options"
SLOT_REPLACEMENT = "Fight!"

#: The one spoken-dialogue record the SDK publishes as an authored target. Its
#: identity is a packed handle, never the text.
TARGET_NAME = "goku-greeting"
TARGET_TEXT = "Good luck, Goku!"
TARGET_REPLACEMENT = "Nice work, Goku!"


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
    directory = tmp_path_factory.mktemp("dbz-text-acceptance") / "source"
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


def wait_for_surface(page, timeout_ms: int = 120_000) -> None:
    """Wait for the worker's read to land. The page renders a loading state until it does.

    The read is off the UI thread by design (`docs/desktop-ui.md`), so a test that
    asserted rows immediately would be measuring the wrong thing. This spins the
    event loop, exactly as a user's window does, and fails loudly rather than
    silently asserting an empty page.
    """
    from PySide6.QtCore import QDeadlineTimer, QEventLoop

    deadline = QDeadlineTimer(timeout_ms)
    while page._surface_loading and not deadline.hasExpired():
        QEventLoop().processEvents()
    assert not page._surface_loading, "the text surface never finished loading"
    assert page._surface is not None, page._problem


@pytest.fixture
def armed(qapp, tmp_path, catalog, canonical_rom, source_project):
    """A shell with the canonical image and a project, on Scripts & Text."""
    session = Session()
    session.open_rom(canonical_rom)
    shutil.copytree(source_project, tmp_path / "project")
    session.open_project(tmp_path / "project")
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("scripts_text")
    wait_for_surface(shell._text_page)
    yield shell._text_page, shell, session, tmp_path / "project"
    _close(shell, session)


# --- driving the page, through the widgets a user drives ----------------------


def _choose_mode(page, label: str) -> None:
    page._modes.setCurrentText(label)
    assert page._mode == {text: identifier for identifier, text in textpage.MODES}[label]


def _point_at(page, row):
    """Put the page's caret on one row, without a Qt selection round trip."""
    page._caret = row.identity
    page._render_editor()
    return row


def _select(page, predicate):
    return _point_at(page, next(item for item in page._rows if predicate(item)))


def _select_at(page, position: int):
    return _point_at(page, page._rows[position])


def drive_string_edit(page):
    """Replace one string-table slot, through the page's own field and Apply."""
    _choose_mode(page, "String tables")
    row = _select(page, lambda item: item.identity == str(SLOT))
    assert row.text == SLOT_TEXT, row.text
    assert page._apply.isEnabled()

    page._value.setText(SLOT_REPLACEMENT)
    page._apply.click()

    return row


def drive_dialogue_edit(page):
    """Replace the one authored spoken-dialogue record, through the page."""
    _choose_mode(page, "Spoken dialogue")
    row = _select(page, lambda item: item.authoring_name == TARGET_NAME)
    assert row.editable
    assert page._apply.isEnabled()

    page._value.setText(TARGET_REPLACEMENT)
    page._apply.click()

    return row


def _ctrl_z(shell) -> None:
    """The Undo action the platform's Ctrl+Z is bound to."""
    action = shell._edit_actions["Undo"]
    assert action.isEnabled()
    action.trigger()


def _authored_string(project_dir, identity) -> str:
    """The text the project document on disk holds for one slot."""
    return read_project(project_dir).strings[identity]


@pytest.fixture
def edited(armed):
    """One string edit and one spoken-dialogue replacement, both through the page."""
    page, shell, session, project_dir = armed

    string_row = drive_string_edit(page)
    assert session.journal.depth == 1
    dialogue_row = drive_dialogue_edit(page)
    assert session.journal.depth == 2

    return page, shell, session, project_dir, string_row, dialogue_row


@pytest.fixture
def built(edited, canonical_rom, catalog):
    """The same session, saved and built through the SDK's own build."""
    page, shell, session, project_dir, string_row, dialogue_row = edited
    session.save_project()
    output = project_dir.parent / "built.gba"
    result = build_project(project_dir, canonical_rom, output, catalog)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    return (
        page,
        shell,
        session,
        string_row,
        dialogue_row,
        project_dir,
        output,
        manifest,
    )


# --- clause 1: the round-trip build -------------------------------------------


def test_clause_1_the_build_asserts_the_owner_the_change_count_and_the_manifest(
    built, canonical_rom
):
    (
        page,
        shell,
        session,
        string_row,
        dialogue_row,
        project_dir,
        output,
        manifest,
    ) = built
    changes = manifest["changes"]
    canonical = canonical_rom.read_bytes()
    built_bytes = output.read_bytes()

    print("\nCLAUSE 1 | one round-trip build: owner identity, change count, manifest")
    print(f"  project            {session.project.meta.name}")
    print(f"  string row         {string_row.identity} at 0x{string_row.file_offset:06X}")
    print(f"  dialogue row       {dialogue_row.identity} target {dialogue_row.authoring_name}")
    print(f"  journal entries    {session.journal.depth}")
    print(f"  manifest changes   {len(changes)}")
    print(f"  changed bytes      {manifest['changed_byte_count']}")
    for change in changes:
        print(
            f"  {change['owner']}  0x{change['offset']:06X} "
            f"{change['old']} -> {change['new']}  ({change['reason']})"
        )
    dialogue_edits = manifest.get("dialogue_edits", [])
    print(f"  dialogue edits     {json.dumps(dialogue_edits)[:400]}")

    assert manifest["base"]["sha256"] == CANONICAL_SHA256
    assert manifest["output"]["sha256"] == hashlib.sha256(built_bytes).hexdigest()

    # Two edits, three changes: the string's own byte range, and the dialogue
    # replacement's two - the container pointer the engine reads, and the rebuilt
    # payload the pointer now names past the end of the canonical image.
    string_changes = [item for item in changes if item["owner"] == str(SLOT)]
    dialogue_changes = [
        item
        for item in changes
        if item["owner"] == f"compressed-dialogue:{TARGET_NAME}"
    ]
    assert len(changes) == 3
    assert len(string_changes) == 1
    assert len(dialogue_changes) == 2

    change = string_changes[0]
    assert change["reason"] == "text edit"
    assert change["offset"] == string_row.file_offset
    assert change["size"] == string_row.allocation
    assert bytes.fromhex(change["old"]) == canonical[
        string_row.file_offset : string_row.file_offset + string_row.allocation
    ]
    assert bytes.fromhex(change["new"]) == page._surface.pending_bytes(
        session.project
    )[string_row.file_offset]

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
    assert differing <= claimed, "the built image differs outside the manifest's claim"
    assert manifest["changed_byte_count"] == len(claimed)
    assert built_bytes[
        change["offset"] : change["offset"] + change["size"]
    ] == bytes.fromhex(change["new"])
    assert _authored_string(project_dir, SLOT) == SLOT_REPLACEMENT
    assert read_project(project_dir).dialogues[TARGET_NAME] == TARGET_REPLACEMENT

    # The relocated payload is past the canonical image, and its range is the
    # manifest's own generated allocation rather than an in-place claim.
    payload = next(item for item in dialogue_changes if item["offset"] >= len(canonical))
    allocations = manifest["generated_allocations"]
    assert len(allocations) == 1
    assert allocations[0]["allocated_range"]["file_offset"] == payload["offset"]
    assert allocations[0]["allocated_range"]["size"] == payload["size"]
    assert (
        len(built_bytes)
        == manifest["generated_image"]["output_size"]
        > len(canonical)
    )


def test_clause_1_a_rebuild_of_the_same_project_is_byte_identical(
    built, canonical_rom, catalog
):
    _page, _shell, _session, _string, _dialogue, project_dir, output, _manifest = built
    again = output.parent / "built-again.gba"
    build_project(project_dir, canonical_rom, again, catalog)

    print("\nCLAUSE 1 | a second build of the same project")
    print(f"  first   {hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(f"  second  {hashlib.sha256(again.read_bytes()).hexdigest()}")

    assert again.read_bytes() == output.read_bytes()


def test_clause_1_the_manifest_carries_the_dialogue_records_own_provenance(built):
    _page, _shell, _session, _string, dialogue_row, _dir, _output, manifest = built
    edits = manifest.get("dialogue_edits") or []

    print("\nCLAUSE 1 | the spoken-dialogue replacement's own provenance")
    print(f"  resource     {TARGET_NAME}")
    print(f"  provenance   {json.dumps(edits)[:600]}")

    assert edits, "the manifest carries no dialogue provenance for a dialogue edit"
    record = edits[0]
    assert record["resource"] == TARGET_NAME
    assert record["selector"] == dialogue_row.selector
    assert record["old_decoded_length"] == dialogue_row.decoded_length
    assert record["new_decoded_start"] == dialogue_row.decoded_start
    assert record["old_decoded_start"] == dialogue_row.decoded_start
    assert record["owner"] == f"compressed-dialogue:{TARGET_NAME}"
    assert record["pointer_moved"] is True
    assert record["packed_size_delta"] > 0


# --- clause 2: visible in the ROM surface -------------------------------------


def _visible_changed_cells(rom) -> list[str]:
    """Every changed-byte cell the rendered byte view is showing."""
    return [
        rom._model.data(rom._model.index(at, 4))
        for at in range(rom._model.rowCount())
        if rom._model.data(rom._model.index(at, 4)) != "-"
    ]


def test_clause_2_the_string_change_is_visible_in_the_rom_surface(edited):
    _page, shell, session, _project_dir, string_row, _dialogue = edited
    rom = shell._rom_page
    rom._views.setCurrentText("Bytes")

    shell.open_rom_at(string_row.file_offset)
    cells = _visible_changed_cells(rom)

    print("\nCLAUSE 2 | the string's bytes are visible in the ROM surface")
    print(f"  ROM caret             file offset 0x{rom._caret:06X}")
    print(f"  ROM changed column    {cells}")
    print(f"  shell's one provider  {sorted(hex(at) for at in shell._pending_bytes())}")

    assert session.navigation.current.destination == "rom"
    assert rom._caret == string_row.file_offset
    assert string_row.file_offset in rom._surface.overlay
    assert cells
    assert rom._surface.pending[string_row.file_offset] == shell._pending_bytes()[
        string_row.file_offset
    ]


# --- clause 3: one stack ------------------------------------------------------


def test_clause_3_the_write_goes_through_the_one_stack(edited):
    page, shell, session, project_dir, string_row, dialogue_row = edited
    entries = session.journal.edits()
    on_disk = _authored_string(project_dir, SLOT)

    print("\nCLAUSE 3 | one journal, one stack, two text targets")
    print(f"  entries            {len(entries)}")
    print(f"  targets            {[entry.target for entry in entries]}")
    print(f"  owners             {[entry.owner for entry in entries]}")
    print(f"  claimed            {[span.to_json() for entry in entries for span in entry.claimed]}")
    print(f"  authored on disk   {on_disk!r} (before Save)")

    assert len(entries) == 2
    assert {entry.target for entry in entries} == {
        textedits.TEXT_TARGET,
        textpage.DIALOGUE_TARGET,
    }
    assert on_disk == SLOT_TEXT, (
        "an unsaved edit must not have reached the project's documents"
    )

    # The bytes the one journal protects are the bytes the plan will write, as a
    # set. A claim taken from the record's canonical position would protect bytes
    # this edit never touches and leave the ones it does outside the raw write's
    # collision guard, which is a real safety hole rather than a cosmetic one.
    plan_problem, plan_changes, plan_spans = page._surface.plan(
        SLOT, SLOT_REPLACEMENT
    )
    assert plan_problem == ""
    string_entry = next(entry for entry in entries if entry.target == textedits.TEXT_TARGET)
    print(
        f"  plan changes       "
        f"{[(hex(change.offset), change.size) for change in plan_changes]}"
    )
    assert tuple(string_entry.claimed) == tuple(plan_spans)
    assert {span.start.value for span in string_entry.claimed} == {
        change.offset for change in plan_changes
    }

    session.save_project()

    assert _authored_string(project_dir, SLOT) == SLOT_REPLACEMENT
    assert read_project(project_dir).dialogues[TARGET_NAME] == TARGET_REPLACEMENT

    _ctrl_z(shell)

    print(
        f"  after Ctrl+Z       dialogue overrides {session.project.dialogues}; "
        f"string {session.project.strings[SLOT]!r}"
    )

    assert session.journal.depth == 1
    assert TARGET_NAME not in session.project.dialogues
    assert session.project.strings[SLOT] == SLOT_REPLACEMENT


def test_clause_3_one_edit_is_one_undo_entry_and_the_page_follows_it(edited):
    page, shell, session, _project_dir, _string, _dialogue = edited

    print("\nCLAUSE 3 | one edit, one undo entry")
    for step in (1, 2):
        _ctrl_z(shell)
        page.refresh()
        live = {change.offset for change in page._surface.changes(session.project)}
        print(
            f"  undo {step}            depth {session.journal.depth}  "
            f"live claimed bytes {sorted(hex(offset) for offset in live)}"
        )

    assert session.journal.depth == 0
    assert session.journal.can_redo
    assert shell._edit_actions["Redo"].isEnabled()
    assert live == set()
    assert page._surface.pending_bytes(session.project) == {}


# --- clause 4: unsupported rows -----------------------------------------------


def test_clause_4_a_spoken_record_with_no_proven_site_offers_no_edit(armed):
    page, _shell, _session, _project_dir = armed
    _choose_mode(page, "Spoken dialogue")
    position = next(
        at for at, item in enumerate(page._rows) if not item.sites
    )
    row = _select_at(page, position)

    print("\nCLAUSE 4 | a spoken-dialogue record with no proven relation")
    print(f"  row        {row.identity}")
    print(f"  support    {page._model.data(page._model.index(position, 9))}")
    print(f"  reason     {row.note}")
    print(f"  provenance {row.provenance}")
    print(f"  apply      {page._apply.isEnabled()}  open bytes {page._open.isEnabled()}")

    assert not row.editable
    assert not row.event_resources
    assert "no authored target is registered" in row.note
    assert "no event-resource record in this image carries this handle" in row.provenance
    assert not page._apply.isEnabled()
    assert not page._open.isEnabled()


def test_clause_4_the_script_and_event_modes_offer_no_edit_at_all(armed):
    page, _shell, _session, _project_dir = armed

    _choose_mode(page, "Scripts")
    root = page._rows[0]
    print("\nCLAUSE 4 | the scripts mode")
    print(f"  summary    {page._summary.text()}")
    print(f"  editor     {page._editor.isVisible()}")
    print(f"  apply      {page._apply.isEnabled()}  open bytes {page._open.isEnabled()}")
    print(f"  message    {page._message.text()}")
    assert not page._editor.isVisible()
    assert not page._apply.isEnabled()
    assert page._open.isEnabled()
    assert page._message.text() == textpage._NO_SCRIPT_EDITOR
    assert root.identity

    _choose_mode(page, "Event resources")
    event = page._rows[0]
    print("CLAUSE 4 | the event resources mode")
    print(f"  summary    {page._summary.text()}")
    print(f"  editor     {page._editor.isVisible()}")
    print(f"  apply      {page._apply.isEnabled()}  open bytes {page._open.isEnabled()}")
    print(f"  message    {page._message.text()}")
    assert not page._editor.isVisible()
    assert not page._apply.isEnabled()
    assert not page._open.isEnabled()
    assert page._message.text() == textpage._NO_EVENT_EDITOR
    assert event.note


def test_clause_4_a_mode_with_no_rows_offers_nothing_and_states_its_reason(armed):
    """The zero-row case: no row means no editor, no Apply and no Open bytes.

    Measured on the empty-mode shape a family switch can produce, so a read-only
    mode whose rows are all filtered away cannot leave a live button behind.
    """
    page, _shell, _session, _project_dir = armed
    _choose_mode(page, "Scripts")
    page._family = ""
    page._families.setCurrentIndex(-1)
    page._rows = ()
    page._caret = ""
    page._render_editor()

    print("\nCLAUSE 4 | a mode with no rows")
    print(f"  rows       {len(page._rows)}")
    print(f"  apply      {page._apply.isEnabled()}  open bytes {page._open.isEnabled()}")

    assert not page._apply.isEnabled()
    assert not page._open.isEnabled()
    assert page._detail.text() == ""


def test_clause_4_a_string_edit_without_a_project_states_its_reason(
    qapp, tmp_path, catalog, canonical_rom
):
    """Without a project nothing on the page may be edited."""
    session = Session()
    session.open_rom(canonical_rom)
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("scripts_text")
    page = shell._text_page
    wait_for_surface(page)
    _choose_mode(page, "String tables")
    row = page._rows[SLOT.index]

    print("\nCLAUSE 4 | a string row with no project open")
    print(f"  row        {row.identity}")
    print(f"  apply      {page._apply.isEnabled()}")
    print(f"  message    {page._message.text()}")
    print(f"  provider   {page.pending_bytes()}")

    assert not page._apply.isEnabled()
    assert "Open a project" in page._message.text()
    assert page.pending_bytes() == {}
    assert page._open.isEnabled()

    _close(shell, session)


# --- clause 5: no unproven relation -------------------------------------------


def test_a_relocating_string_edit_claims_the_bytes_the_plan_writes(armed):
    """The reviewed defect, driven THROUGH THE PAGE and measured at the guard.

    `text:0000` holds an empty string in a 2-byte allocation, so a real
    replacement must relocate. The page commits under the plan's own spans, the
    journal's guard therefore protects the pointer-table slot and the allocated
    body, and the raw write that would have overwritten the relocated body
    unguarded is refused.
    """
    from tools.dragonbyte.journal import RawContext, RawRequest
    from tools.dragonbyte.rawbytes import RawWrite

    page, _shell, session, _project_dir = armed
    _choose_mode(page, "String tables")
    row = _select(page, lambda item: item.identity == "text:0000")
    original = (row.file_offset, row.allocation)
    replacement = "Relocate me"
    _problem, changes, spans = page._surface.plan(TextIdentity(0), replacement)

    page._value.setText(replacement)
    page._apply.click()

    print("\nCLAIM | a relocating string edit, through the page")
    print(f"  record           text:0000 at 0x{original[0]:06X} alloc {original[1]}")
    print(f"  plan changes     {[(hex(c.offset), c.size, c.reason) for c in changes]}")
    print(f"  journal claimed  {[span.to_json() for span in session.journal.pending_spans()]}")
    print(f"  message          {page._message.text()!r}")

    entry = session.journal.edits()[0]
    assert entry.target == textedits.TEXT_TARGET
    assert tuple(entry.claimed) == tuple(spans)
    assert {span.start.value for span in entry.claimed} == {
        change.offset for change in changes
    }
    assert original not in {
        (span.start.value, span.size) for span in entry.claimed
    }, "the claim must not be the record's canonical position"
    assert session.project.strings[TextIdentity(0)] == replacement

    # The guard the journal shows a raw write: the allocated body is claimed, so
    # a write into it is refused rather than landing unguarded.
    body = max(entry.claimed, key=lambda span: span.start.value)
    refusal = session.journal.raw_refusal(
        RawRequest(
            write=RawWrite(
                offset=body.start.value,
                before=session.base_image[body.start.value : body.end],
                new=b"\xff" * body.size,
                confirmed=True,
            ),
            context=RawContext(
                base_image=session.base_image, profile=session.profile
            ),
        )
    )

    print(f"  raw write into  0x{body.start.value:06X} (+{body.size}) -> "
          f"{refusal.message if refusal else 'ACCEPTED'}")

    assert refusal is not None
    assert str(entry.owner) in refusal.message or entry.owner in refusal.message


def test_clause_5_the_two_text_systems_are_never_one_row(armed):
    """The discriminating pair: a string's identity and a dialogue's are disjoint."""
    page, _shell, _session, _project_dir = armed

    _choose_mode(page, "String tables")
    string_rows = page._rows
    _choose_mode(page, "Spoken dialogue")
    dialogue_rows = page._rows

    string_keys = {row.identity for row in string_rows}
    dialogue_keys = {row.identity for row in dialogue_rows}

    print("\nCLAUSE 5 | the two text systems, side by side")
    print(f"  string rows        {len(string_rows)}  identity form "
          f"{string_rows[0].identity_form}")
    print(f"  dialogue rows      {len(dialogue_rows)}  identity form "
          f"{dialogue_rows[0].identity_form}")
    print(f"  shared identities  {len(string_keys & dialogue_keys)}")
    print(f"  string identity line  {ts.STRING_IDENTITY_LINE}")
    print(f"  spoken identity line  {ts.SPOKEN_IDENTITY_LINE}")

    assert string_keys & dialogue_keys == set()
    assert {row.system for row in string_rows} == {ts.STRING_SYSTEM}
    assert {row.system for row in dialogue_rows} == {ts.SPOKEN_SYSTEM}
    assert {row.identity_form for row in string_rows} == {"pointer-table slot"}
    assert {row.identity_form for row in dialogue_rows} == {"packed handle"}
    assert all(row.identity.startswith("text:") for row in string_rows)
    assert all(row.identity.startswith("dialogue:") for row in dialogue_rows)


def test_clause_5_a_dialogue_record_is_linked_only_to_records_that_carry_it(armed):
    page, _shell, _session, _project_dir = armed
    _choose_mode(page, "Spoken dialogue")
    with_sites = [row for row in page._rows if row.sites]
    without = [row for row in page._rows if not row.sites]

    print("\nCLAUSE 5 | dialogue reference sites, both ways")
    print(f"  records with a proven site     {len(with_sites)}")
    print(f"  records with none              {len(without)}")
    print(f"  sites outside the pool         {sum(row.sites_outside for row in page._rows)}")

    assert with_sites and without
    for row in with_sites:
        assert row.event_resources, row.identity
        for index in row.event_resources:
            assert index in range(len(page._surface.events.resource_records()))
    for row in without:
        assert row.event_resources == ()


def test_clause_5_the_product_modules_name_no_relation_the_evidence_refuses():
    """A source-level guard over the two modules the destination is made of."""
    sources = {
        "textsurface": Path(ts.__file__).read_text(encoding="utf-8"),
        "textpage": Path(textpage.__file__).read_text(encoding="utf-8"),
        "textedits": Path(textedits.__file__).read_text(encoding="utf-8"),
    }
    imported = set()
    for source in sources.values():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Import):
                imported.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)

    dialogue_fields = {field.name for field in fields(ts.DialogueRow)}
    string_fields = {field.name for field in fields(ts.StringRow)}
    forbidden_fields = {"sprite", "item", "shop", "trigger", "string_slot"}

    print("\nCLAUSE 5 | imported names and fields the product modules may not use")
    print(f"  TokenDictionary imported  {'TokenDictionary' in imported}")
    print(f"  dialogue row fields       {sorted(dialogue_fields)}")
    print(f"  string row fields         {sorted(string_fields)}")

    assert "TokenDictionary" not in imported, (
        "the token dictionary is a build-time expansion window, not a reader: no "
        "surface may present a stored unit as an expansion"
    )
    assert not (dialogue_fields & forbidden_fields)
    assert not (string_fields & forbidden_fields)
    assert not (string_fields & {"selector", "decoded_start", "decoded_length"}), (
        "a string-table row must not carry a dialogue record's own geometry"
    )
