"""APPEARANCE-AUTHORING-GATE-001: the authored-appearance Workbench surface.

The tab strip and the dialog that together write a project's
`appearances/appearances.toml`. The project half is REAL here: the project
directory is written by the model, the document is written by the domain's own
`apply_authored_appearances`, and every assertion re-reads it with `read_project`.
Only the image half is stubbed, because a verified 8 MiB image is what the
ROM-gated suite is for; the stubs stand in for the SDK calls the dialog makes and
nothing else, so the write, the reopen and the revision guards are exercised for
real.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path  # noqa: E402
from types import SimpleNamespace  # noqa: E402

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from tools.webfoot import appearance_authoring as aa  # noqa: E402
from tools.webfoot import appearances as ap  # noqa: E402
from tools.webfoot.project.model import (AuthoredAppearance,  # noqa: E402
                                         AuthoredAppearances, ProjectMeta,
                                         ProjectValidationError, read_project,
                                         write_project)
from tools.webfoot.workbench import appearance_dialog as ad  # noqa: E402
from tools.webfoot.workbench.graphics_tab import (  # noqa: E402
    AuthoredAppearanceCommand, GraphicsTab)
from tools.webfoot.workbench.session import Session  # noqa: E402

NAME = "new_face"
TEXT_INDEX = 1188
SPRITE_ID = 137
NAMES = (1188, 996, 1184)
SPRITES = (12, 137, 306)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _project(tmp_path: Path) -> Path:
    write_project(
        tmp_path,
        ProjectMeta(1, "synthetic_profile", "Synthetic Game", "0" * 64, 1024,
                    "appearance-surface-test"),
        enemies=[], characters=[])
    return tmp_path


def _session(project_dir) -> Session:
    """A session over a synthetic image whose profile declares the table.

    The decoded sprite corpus is a stand-in: no 8 MiB image exists here, and the
    status line only asks whether it loaded.
    """
    session = Session(rom_image=b"synthetic",
                      profile=SimpleNamespace(appearances=object()),
                      identification=object())
    session._sprites = object()
    session._sprites_loaded = True
    session.set_project(project_dir)
    return session


@pytest.fixture
def stubbed(monkeypatch):
    """Stand in for the image-side SDK calls; leave the project side real."""
    record = ap.AppearanceRecord(TEXT_INDEX, TEXT_INDEX + 1, SPRITE_ID, 0, -1)
    monkeypatch.setattr(ap, "read_records", lambda image, profile: (record,))
    monkeypatch.setattr(ap, "name_vocabulary", lambda image, profile: NAMES)
    monkeypatch.setattr(ap, "sprite_vocabulary",
                        lambda image, profile, *, extra=None: SPRITES)
    monkeypatch.setattr(aa, "validate_authored_appearances",
                        lambda *args, **kwargs: None)
    return record


def _tab(qapp, session, stubbed) -> GraphicsTab:
    return GraphicsTab(session)


def _fill(dialog, name: str = NAME) -> None:
    """Type and choose a minimal valid draft into the dialog's own widgets."""
    dialog._name.setText(name)
    ad._select(dialog._text, TEXT_INDEX)
    ad._select(dialog._sprite, SPRITE_ID)
    dialog._refresh()


# --- the strip ---------------------------------------------------------------


def test_the_strip_disables_everything_with_no_session(qapp, stubbed):
    tab = _tab(qapp, Session(), stubbed)

    assert not tab._appearance_new.isEnabled()
    assert not tab._appearance_edit.isEnabled()
    assert not tab._appearance_remove.isEnabled()


def test_a_project_without_the_document_offers_create_only(qapp, tmp_path, stubbed):
    tab = _tab(qapp, _session(_project(tmp_path)), stubbed)

    assert tab._appearance_new.isEnabled()
    assert not tab._appearance_edit.isEnabled()
    assert not tab._appearance_remove.isEnabled()
    assert tab._appearance_chip.text() == "No authored appearance."


def test_a_profile_without_the_table_is_not_available(qapp, tmp_path, stubbed):
    session = _session(_project(tmp_path))
    session.profile = SimpleNamespace()

    tab = _tab(qapp, session, stubbed)

    assert not tab._appearance_new.isEnabled()
    assert tab._appearance_chip.text() == "Authoring not available."


def test_a_project_that_cannot_be_read_leaves_the_strip_read_only(qapp, tmp_path,
                                                                 stubbed):
    empty = tmp_path / "not-a-project"
    empty.mkdir()
    tab = _tab(qapp, _session(empty), stubbed)

    assert not tab._appearance_new.isEnabled()
    assert tab._appearance_chip.text() == "Project unreadable."


# --- the commit path ---------------------------------------------------------


def test_creating_through_the_dialog_writes_the_document(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)

    dialog = ad.AppearanceAuthoringDialog(tab, session)
    _fill(dialog)
    assert dialog.definition() is not None
    assert dialog._ok.isEnabled()
    assert not (project / "appearances" / "appearances.toml").exists()

    dialog._on_accept()
    written = dialog.definition()
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={written.name: written}),
        "New authored appearance")

    assert read_project(project).appearances.ordered()[0] == AuthoredAppearance(
        NAME, TEXT_INDEX, SPRITE_ID)
    assert (project / "appearances" / "appearances.toml").is_file()


def test_a_commit_bumps_the_revision_and_rearms_the_project_actions(qapp, tmp_path,
                                                                   stubbed):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    session.record_validation(True)
    before = session.project_revision
    assert session.validation_current
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)

    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={NAME: definition}),
        "New authored appearance")

    assert session.project_revision == before + 1
    assert not session.validation_current
    assert emitted == [True]


def test_undo_removes_the_definition_and_redo_puts_it_back(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={NAME: definition}),
        "New authored appearance")
    assert tab._undo_stack.canUndo()

    tab._undo_stack.undo()
    assert not (project / "appearances" / "appearances.toml").exists()
    assert aa.authored_appearances(project).is_empty()
    assert not tab._undo_stack.canUndo()
    assert tab._undo_stack.canRedo()

    tab._undo_stack.redo()
    assert aa.authored_appearances(project).ordered()[0].name == NAME


def test_removing_writes_an_empty_document_and_undo_restores_it(qapp, tmp_path,
                                                               stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={NAME: definition}),
        "New authored appearance")

    tab._commit_authored_appearances(AuthoredAppearances(),
                                     "Remove authored appearance")
    assert aa.authored_appearances(project).is_empty()

    tab._undo_stack.undo()
    assert aa.authored_appearances(project).ordered()[0].name == NAME


def test_reopening_the_surface_shows_the_committed_definition(qapp, tmp_path,
                                                             stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={NAME: definition}),
        "New authored appearance")

    reopened = _tab(qapp, _session(project), stubbed)

    assert reopened._appearance_chip.text() == "1 authored appearance."
    assert reopened._appearance_edit.isEnabled()
    assert reopened._appearance_remove.isEnabled()
    assert reopened._appearance_pick.currentData() == NAME


def test_editing_reloads_the_committed_definition(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={NAME: definition}),
        "New authored appearance")

    editing = ad.AppearanceAuthoringDialog(tab, session, definition=definition)

    assert editing._name.text() == NAME
    assert editing._text.currentData() == TEXT_INDEX
    assert editing._sprite.currentData() == SPRITE_ID


def test_editing_under_a_new_name_replaces_the_entry(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={NAME: definition}),
        "New authored appearance")
    renamed = AuthoredAppearance("renamed_face", TEXT_INDEX, SPRITE_ID)

    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={"renamed_face": renamed}),
        "Edit authored appearance")

    assert read_project(project).appearances.names() == ("renamed_face",)


def test_a_commit_that_changes_nothing_does_not_touch_the_project(qapp, tmp_path,
                                                                 stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    document = AuthoredAppearances(appearances={NAME: definition})
    tab._commit_authored_appearances(document, "New authored appearance")
    revision = session.project_revision
    depth = tab._undo_stack.count()
    written = (project / "appearances" / "appearances.toml").read_bytes()

    tab._commit_authored_appearances(document, "New authored appearance")

    assert session.project_revision == revision
    assert tab._undo_stack.count() == depth
    assert (project / "appearances" / "appearances.toml").read_bytes() == written


def test_undo_refuses_to_write_into_another_project(qapp, tmp_path, stubbed,
                                                    monkeypatch):
    first = _project(tmp_path / "first")
    second = _project(tmp_path / "second")
    session = _session(first)
    tab = _tab(qapp, session, stubbed)
    definition = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)
    document = AuthoredAppearances(appearances={NAME: definition})
    tab._commit_authored_appearances(document, "New authored appearance")
    command = AuthoredAppearanceCommand(tab, first, AuthoredAppearances(), document,
                                        "New authored appearance")
    other = AuthoredAppearance("bsprite", 996, 12)
    aa.apply_authored_appearances(
        second, AuthoredAppearances(appearances={"bsprite": other}))
    told = []
    monkeypatch.setattr(QMessageBox, "information",
                        lambda *args, **kwargs: told.append(args[2]))

    session.set_project(second)
    tab._refresh_appearance_strip()
    assert tab._undo_stack.count() == 0
    command.undo()

    assert aa.authored_appearances(second).names() == ("bsprite",)
    assert told and "no longer open" in told[0]


# --- refusals ----------------------------------------------------------------


def test_a_definition_the_sdk_refuses_disables_the_dialog(qapp, tmp_path, stubbed,
                                                          monkeypatch):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    monkeypatch.setattr(
        aa, "validate_authored_appearances",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ProjectValidationError("sprite id 400 is outside the 10..306 range")))
    dialog = ad.AppearanceAuthoringDialog(tab, session)

    _fill(dialog)

    assert not dialog._ok.isEnabled()
    assert "10..306" in dialog._summary.text()
    assert dialog.definition() is None


def test_accepting_a_refused_draft_warns_and_returns_nothing(qapp, tmp_path, stubbed,
                                                            monkeypatch):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    dialog = ad.AppearanceAuthoringDialog(tab, session)
    _fill(dialog)
    warned = []
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *args, **kwargs: warned.append(args[2]))
    monkeypatch.setattr(
        aa, "validate_authored_appearances",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            ProjectValidationError("text index 9999 is outside the declared table")))

    dialog._on_accept()

    assert warned == ["text index 9999 is outside the declared table"]
    assert dialog.definition() is None
    assert not (project / "appearances" / "appearances.toml").exists()


def test_a_name_that_is_already_taken_is_refused_by_the_dialog(qapp, tmp_path,
                                                              stubbed):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    dialog = ad.AppearanceAuthoringDialog(
        tab, session, taken=(NAME, "other"))

    _fill(dialog)

    assert not dialog._ok.isEnabled()
    assert "already exists" in dialog._summary.text()

def test_the_merge_refuses_a_second_definition_that_shares_a_sprite_id(
        qapp, tmp_path, stubbed, monkeypatch):
    """The dialog sees one draft at a time, so the collision is only visible when
    the accepted definition is merged with what is already committed."""
    project = _project(tmp_path)
    tab = _tab(qapp, _session(project), stubbed)
    tab._commit_authored_appearances(
        AuthoredAppearances(appearances={
            "first": AuthoredAppearance("first", TEXT_INDEX, SPRITE_ID)}),
        "New authored appearance")

    refused = []
    monkeypatch.setattr(QMessageBox, "critical",
                        lambda *args: refused.append(args[2]))
    tab._merge_authored_appearance(
        AuthoredAppearance("second", TEXT_INDEX + 2, SPRITE_ID), None)

    assert refused and "not added" in refused[0]
    assert tuple(item.name for item in read_project(project).appearances.ordered()) \
        == ("first",)

def test_the_dialog_offers_the_takeover_explicitly_and_warns(qapp, tmp_path, stubbed):
    """The control is off by default, and the wording says what it redirects."""
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    dialog = ad.AppearanceAuthoringDialog(tab, session)
    _fill(dialog)

    assert dialog._override.isChecked() is False
    assert dialog._definition().override is False

    # The wording has to name the redirection AND its scope: the takeover applies to
    # the engine's sprite-only lookup, not to every lookup, and a wording that
    # claimed otherwise would overstate what the author is enabling.
    warning = dialog._override_warning.text().lower()
    assert "redirects existing actors" in warning
    assert "sprite-only lookup" in warning
    assert "stat record" in warning
    assert "unaffected" in warning
    assert "retail" in warning

    dialog._override.setChecked(True)
    assert dialog._definition().override is True


def test_editing_shows_the_stored_takeover(qapp, tmp_path, stubbed):
    """Reopening a definition shows the intent the document carries."""
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    committed = AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID, override=True)

    dialog = ad.AppearanceAuthoringDialog(tab, session, definition=committed)
    assert dialog._override.isChecked() is True
    assert dialog._definition().override is True
