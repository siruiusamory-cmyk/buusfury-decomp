"""DRAGONBYTE-Z-DATA-SURFACES-001: the Data destination's page.

The windowed lane runs the real shell offscreen and drives the page a user
drives: the mode switch, the record table, the field editor, Apply, and
`Open bytes`. What it asserts is that the page renders the model's answers and
hands its edit to the shell's one journal - that the window never computes a
support state, a range or a byte effect of its own.

The suite skips without the canonical image.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import replace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.dragonbyte import coverage, datasurface as ds  # noqa: E402
from tools.dragonbyte.datapage import COVERAGE_MODE, MODES  # noqa: E402
from tools.dragonbyte.inspector import SUPPORT_STATES  # noqa: E402
from tools.dragonbyte.romsurface import PendingBytes  # noqa: E402
from tools.dragonbyte.session import Session  # noqa: E402
from tools.dragonbyte.shell import Shell  # noqa: E402
from tools.webfoot.build import extract_project  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.rom import identify_rom  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
    wait_for_text_surface,
)


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
    directory = tmp_path_factory.mktemp("dbz-datapage") / "source"
    extract_project(canonical_rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture(autouse=True)
def no_range_index(monkeypatch):
    """The ROM page's range index is not what this file tests.

    Parsing the assembled atlas in every shell built here would cost seconds per
    test and would race the window's teardown, and neither the byte view nor the
    pending provider needs an index. The module-level loader is replaced, which
    is the same seam the ROM surface's own windowed fixture uses.
    """
    from tools.dragonbyte import rompage

    monkeypatch.setattr(
        rompage,
        "load_index",
        lambda profile, directory=None: (None, "the range index is not loaded here"),
    )


def _open(tmp_path, catalog, canonical_rom, source_project, *, project: bool = True):
    session = Session()
    session.open_rom(canonical_rom)
    if project:
        target = tmp_path / "project"
        shutil.copytree(source_project, target)
        session.open_project(target)
    return session, Shell(session, tmp_path / "config")


@pytest.fixture
def data_page(qapp, tmp_path, catalog, canonical_rom, source_project):
    session, shell = _open(tmp_path, catalog, canonical_rom, source_project)
    shell.show_destination("data")
    yield shell._data_page, shell, session
    _close(shell, session)


# --- the three record tables --------------------------------------------------


def test_the_mode_switch_offers_the_three_tables_and_the_coverage_view(data_page):
    page, _shell, _session_ = data_page

    assert [label for _identifier, label in MODES] == [
        "Enemies",
        "Characters",
        "Map headers",
        "Coverage",
    ]
    assert page._modes.currentText() == "Enemies"
    assert page._model.rowCount() == 141
    assert page._model.columnCount() == 6


def test_every_record_kind_renders_the_models_own_rows(data_page):
    page, _shell, _session_ = data_page

    for kind, label, count in (
        (ds.ENEMY, "Enemies", 141),
        (ds.CHARACTER, "Characters", 9),
        (ds.MAP_HEADER, "Map headers", 452),
    ):
        page._modes.setCurrentText(label)

        assert page._mode == kind
        assert len(page._rows) == count
        assert page._model.rowCount() == count
        first = page._rows[0]
        assert page._model.data(page._model.index(0, 0)) == first.label
        assert page._model.data(page._model.index(0, 1)) == first.identity
        assert page._model.data(page._model.index(0, 2)) == f"0x{first.address:08X}"
        assert page._model.data(page._model.index(0, 3)) == f"0x{first.file_offset:06X}"
        assert page._model.data(page._model.index(0, 5)).endswith(
            "Editable" if first.editable else "Read-only"
        )


def test_the_support_column_uses_the_one_vocabulary(data_page):
    page, _shell, _session_ = data_page

    for kind in ds.KINDS:
        page._modes.setCurrentText(ds.KIND_LABELS[kind])
        for position in range(0, len(page._rows), 7):
            cell = page._model.data(page._model.index(position, 5))
            word = cell.split(" ", 1)[1]
            assert word in SUPPORT_STATES, cell


def test_the_field_editor_offers_the_records_own_fields_and_values(data_page):
    page, _shell, _session_ = data_page
    row = page._rows[0]

    assert [page._field.itemText(index) for index in range(page._field.count())] == [
        field.name for field in row.fields
    ]
    assert page._value.text() == str(row.fields[0].value)
    assert page._apply.isEnabled()
    assert page._open.isEnabled()
    assert "0x%06X" % row.file_offset in page._detail.text()


def test_a_read_only_record_states_its_reason_and_applies_nothing(
    qapp, tmp_path, catalog, canonical_rom, source_project
):
    session, shell = _open(tmp_path, catalog, canonical_rom, source_project, project=False)
    shell.show_destination("data")
    page = shell._data_page

    assert page._rows and not page._rows[0].editable
    assert not page._apply.isEnabled()
    assert "authors no enemy record" in page._apply.toolTip()
    page._value.setText("1")
    # A disabled control cannot be clicked, so the handler is called directly:
    # a signal that arrived anyway must not write anything.
    page._on_apply()

    assert "No project is open" in page._message.text()
    assert session.journal.depth == 0
    _close(shell, session)


def test_the_page_states_when_no_rom_is_open(qapp, tmp_path):
    session = Session()
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("data")
    page = shell._data_page

    assert page._model.rowCount() == 0
    assert "Open a ROM image" in page._message.text()
    assert not page._open.isEnabled()
    _close(shell, session)


# --- the edit path ------------------------------------------------------------


def test_one_edit_through_the_page_is_one_journal_entry_and_one_undo(data_page):
    page, shell, session = data_page
    row = page._rows[0]
    field = row.field("hp")
    value = field.value + 1

    page._field.setCurrentText("hp")
    page._value.setText(str(value))
    page._apply.click()

    assert session.journal.depth == 1
    assert session.journal.is_dirty
    assert session.project.enemies[row.key]["hp"] == value
    assert page._caret_row().field("hp").value == value
    assert str(value) in page._message.text()

    shell.undo_edit()

    assert session.journal.depth == 0
    assert session.project.enemies[row.key]["hp"] == field.value
    assert page._caret_row().field("hp").value == field.value


def test_a_value_outside_the_supported_range_is_refused_without_an_edit(data_page):
    page, _shell, session = data_page

    page._field.setCurrentText("level")
    page._value.setText("255")
    page._apply.click()

    assert "outside the supported range" in page._message.text()
    assert session.journal.depth == 0


def test_a_value_that_is_already_held_is_not_an_edit(data_page):
    page, _shell, session = data_page
    row = page._rows[0]

    page._field.setCurrentText("hp")
    page._value.setText(str(row.field("hp").value))
    page._apply.click()

    assert "already" in page._message.text()
    assert session.journal.depth == 0


def test_a_map_header_edit_is_one_journal_entry_owned_by_the_map_identity(data_page):
    page, _shell, session = data_page
    page._modes.setCurrentText("Map headers")
    row = page._rows[0]
    value = (row.field("zone").value + 1) % 0x100

    page._field.setCurrentText("zone")
    page._value.setText(str(value))
    page._apply.click()

    entry = session.journal.edits()[0]
    assert entry.claimed[0].start.value == row.file_offset
    assert session.project.maps[row.key.index]["zone"] == value


def test_the_inspector_shows_the_selected_records_identities(data_page):
    page, shell, _session_ = data_page
    row = page._rows[0]
    rendered = " ".join(
        child.text() for child in shell._inspector.findChildren(type(page._detail))
    )

    assert row.identity in rendered
    assert row.label in rendered
    assert "Editable" in rendered


# --- the one selection, shared with the ROM surface ---------------------------


def test_open_bytes_hands_the_records_extent_to_the_rom_destination(data_page):
    page, shell, session = data_page
    row = page._rows[0]

    page._open.click()

    assert session.navigation.current.destination == "rom"
    assert shell._page_stack.currentWidget() is shell._rom_page
    assert shell._rom_page._caret == row.file_offset
    assert shell._rom_page._views.currentText() == "Bytes"


def test_a_stat_edit_moves_the_same_bytes_in_the_rom_surface(data_page):
    page, shell, session = data_page
    row = page._rows[0]
    value = row.field("hp").value + 1
    page._field.setCurrentText("hp")
    page._value.setText(str(value))
    page._apply.click()
    page._open.click()

    rom = shell._rom_page

    assert row.file_offset in rom._surface.overlay
    assert rom._surface.pending[row.file_offset] != rom._surface.canonical_bytes(
        row.file_offset, row.size
    )
    assert rom._surface.current_bytes(
        row.file_offset, row.size
    ) != rom._surface.canonical_bytes(row.file_offset, row.size)
    changed = rom._model.data(rom._model.index(0, 4))
    assert changed != "-"

    shell.undo_edit()

    assert row.file_offset not in rom._surface.overlay
    assert row.file_offset not in rom._surface.pending
    assert rom._surface.current_bytes(
        row.file_offset, row.size
    ) == rom._surface.canonical_bytes(row.file_offset, row.size)
    assert rom._model.data(rom._model.index(0, 4)) == "-"


def test_a_data_provider_that_cannot_answer_states_its_reason(data_page, monkeypatch):
    """A Data provider that cannot encode its edit says so; it is never silent.

    The destination's own surface is made to fail after a real stat edit has been
    committed, so the journal holds the claim, no bytes can be encoded for it,
    and the ROM surface must state that instead of showing the canonical value as
    though nothing were pending.
    """
    page, shell, session = data_page
    row = page._rows[0]
    page._field.setCurrentText("hp")
    page._value.setText(str(row.field("hp").value + 1))
    page._apply.click()
    assert session.journal.depth == 1

    reason = "the stat codec refused the record"

    def refuse(_surface, _project):
        raise RuntimeError(reason)

    monkeypatch.setattr(type(page._surface), "pending_bytes", refuse)
    wait_for_text_surface(shell)
    page._open.click()
    rom = shell._rom_page
    merged = shell._pending_bytes()
    stated = f"Data: the pending bytes could not be stated: {reason}"

    print("\nDATA PROVIDER FAILURE | the reason reaches the ROM surface")
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


def test_a_data_destination_that_has_not_read_the_image_states_that(
    qapp, tmp_path, catalog, canonical_rom, source_project, monkeypatch
):
    """An unread destination states that, and the reason clears with the read.

    The first read of the image is made to fail, which is the one way this
    destination is left with no surface while a project is open. That is not "no
    pending bytes": it has not answered at all, and the ROM surface says so
    rather than showing the canonical value as the answer. The second half of the
    proof is that the reason does not survive the successful read, and that the
    destination answers again once it has one.
    """
    loader = ds.load_data_surface

    def refuse(*_args):
        raise ds.DataSurfaceError("the data tables could not be read")

    monkeypatch.setattr(ds, "load_data_surface", refuse)
    session = Session()
    session.open_rom(canonical_rom)
    shutil.copytree(source_project, tmp_path / "project")
    session.open_project(tmp_path / "project")
    shell = Shell(session, tmp_path / "config")
    page = shell._data_page
    wait_for_text_surface(shell)

    assert page._surface is None
    assert page.pending_bytes() == PendingBytes(
        problem="the data tables could not be read"
    )

    shell.show_destination("rom")
    rom = shell._rom_page
    stated = "Data: the data tables could not be read"

    print("\nDATA DESTINATION UNREAD | the reason reaches the ROM surface")
    print(f"  page provider      {page.pending_bytes()}")
    print(f"  ROM summary        {rom._summary.text()}")
    print(f"  ROM pending bytes  {sorted(hex(at) for at in rom._surface.pending)}")
    print(f"  ROM overlay        {sorted(hex(at) for at in rom._surface.overlay)}")

    assert rom._surface.pending_problem == stated
    assert stated in rom._summary.text()
    assert rom._surface.pending == {}
    assert rom._surface.overlay == frozenset()

    monkeypatch.setattr(ds, "load_data_surface", loader)
    page.refresh()
    assert page._surface is not None

    row = page._rows[0]
    page._field.setCurrentText("hp")
    page._value.setText(str(row.field("hp").value + 1))
    page._apply.click()
    shell.open_rom_at(row.file_offset)
    rom = shell._rom_page

    assert rom._surface.pending_problem == ""
    assert stated not in rom._summary.text()
    assert row.file_offset in rom._surface.pending

    _close(shell, session)


def test_the_rom_page_renders_no_pending_bytes_without_a_data_edit(data_page):
    page, shell, _session_ = data_page
    row = page._rows[0]
    page._open.click()

    assert shell._rom_page._surface.overlay == frozenset()
    assert shell._rom_page._surface.current_bytes(
        row.file_offset, row.size
    ) == shell._rom_page._surface.canonical_bytes(row.file_offset, row.size)


# --- the coverage view --------------------------------------------------------


def test_the_coverage_view_renders_the_census_for_the_open_title(data_page):
    page, _shell, session = data_page

    page._modes.setCurrentText("Coverage")
    document = coverage.load_census()
    view = coverage.coverage_view(document, session.profile.id)

    assert page._mode == COVERAGE_MODE
    assert page._model.rowCount() == len(view.rows) == 40
    assert page._model.columnCount() == 6
    assert view.title in page._summary.text()
    assert view.summary() in page._summary.text()
    assert not page._editor.isVisible()
    assert "stored" in page._message.text()


def test_the_coverage_view_shows_a_word_for_every_census_state(data_page):
    page, _shell, _session_ = data_page
    page._modes.setCurrentText("Coverage")

    for group in page._coverage.groups:
        assert group.word in page._summary.text()
        assert str(group.cells) in page._summary.text()
        assert group.sentence


def test_the_coverage_detail_quotes_the_census_token_and_the_evidence(data_page):
    page, _shell, _session_ = data_page
    page._modes.setCurrentText("Coverage")

    page._select_row(1)
    page._render_coverage_detail(1)
    row = page._coverage.rows[1]

    assert row.row_id in page._detail.text()
    assert row.state in page._detail.text()
    assert row.basis in page._detail.text()


def test_the_data_page_keeps_one_table_model_and_no_second_undo(data_page):
    page, shell, _session_ = data_page

    assert page._model.rowCount() == page._table.model().rowCount()
    assert shell.findChildren(type(page._table)) != []
    assert not hasattr(page, "undo")
    assert not hasattr(page, "_history")
    assert not hasattr(page, "journal")
