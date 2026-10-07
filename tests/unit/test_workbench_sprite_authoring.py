"""SPRITE-PROJECT-SURFACE-001: the authored-sprite Workbench surface.

The tab strip and the dialog that together write a project's
`sprites/sprites.toml`. The project half is REAL here: the synthetic project
directory is written by the model, the document is written by the facade's own
`apply_authored_sprite`, and every assertion re-reads it with `read_project`. Only
the image half is stubbed, because a decoded 8 MiB validated image is what the
ROM-gated suite is for; the stubs stand in for the SDK calls the dialog makes and
nothing else, so the write, the reopen and the revision guards are exercised for
real.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from tests.unit.test_sprite_project_surface import (  # noqa: E402
    SPRITE_ID, TEMPLATE, _template)
from tools.webfoot import sprite_project as sp  # noqa: E402
from tools.webfoot.project.model import (AuthoredSpriteAnimation,  # noqa: E402
                                         AuthoredSprites, ProjectMeta,
                                         ProjectValidationError, read_project,
                                         write_project)
from tools.webfoot.sprite_authoring import SourceSheet  # noqa: E402
from tools.webfoot.sprite_identity import DonorEnvelope  # noqa: E402
from tools.webfoot.workbench import sprite_dialog as sd  # noqa: E402
from tools.webfoot.workbench.graphics_tab import (AuthoredSpriteCommand,  # noqa: E402
                                                  GraphicsTab)
from tools.webfoot.workbench.session import Session  # noqa: E402

CELL = 8


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _project(tmp_path) -> Path:
    write_project(
        tmp_path,
        ProjectMeta(1, "synthetic_profile", "Synthetic Game", "0" * 64, 1024,
                    "sprite-surface-test"),
        enemies=[], characters=[])
    return tmp_path


def _session(project_dir) -> Session:
    """A session over a synthetic image, with the corpus cached as unbuildable.

    The corpus is a stand-in object: no decoded 8 MiB corpus exists here, and the
    dialog only ever hands it back to the SDK call that was stubbed.
    """
    session = Session(rom_image=b"synthetic", profile=object(),
                      identification=object())
    session._sprites = object()
    session._sprites_loaded = True
    session.set_project(project_dir)
    return session


def _sheet(frames: int = 1):
    """A direction-major sheet whose cells are solid, cheap to build."""
    side = CELL
    return SourceSheet(frames_per_direction=frames, cell_width=side,
                       cell_height=side,
                       pixels=bytes((12, 34, 56)) * (side * side * frames * 4))


@pytest.fixture
def stubbed(monkeypatch):
    """Stand in for the image-side SDK calls; leave the project side real."""
    envelope = DonorEnvelope(width=CELL, height=CELL, anchor=(-4, -8), piece_count=1)
    monkeypatch.setattr(sp, "probe_sprite_authoring",
                        lambda image, identification, *, donor_sprite_id=None,
                        profile=None, corpus=None: sp.SpriteAuthoringProbe(
                            sprite_id=SPRITE_ID, character_count=297,
                            donor=None if donor_sprite_id is None else envelope))
    monkeypatch.setattr(sp, "supported_actor_templates",
                        lambda image, profile: (_template(),))
    monkeypatch.setattr(sp, "supported_template",
                        lambda image, profile, identity: _template())
    monkeypatch.setattr(sp, "validate_authored_sprite",
                        lambda image, identification, profile, request, *,
                        project_dir: AuthoredSprites(
                            sprites={request.name: request.to_sprite(
                                template=_template(), sprite_id=SPRITE_ID)}))
    monkeypatch.setattr(sd, "read_source_sheet",
                        lambda project_dir, animation, *, where, **kwargs: _sheet(
                            animation.frames))
    return envelope


def _tab(qapp, session, stubbed) -> GraphicsTab:
    return GraphicsTab(session)


def _fill(dialog, name: str = "cui") -> None:
    """Type a minimal valid draft into the dialog's own widgets."""
    dialog._name.setText(name)
    dialog._on_add_animation()
    dialog._anim_sheet.setText("sprites/cui/stand.png")
    dialog._refresh()


# --- the strip ---------------------------------------------------------------


def test_the_strip_states_the_project_and_disables_what_cannot_run(qapp, tmp_path,
                                                                   stubbed):
    session = Session()
    tab = _tab(qapp, session, stubbed)

    assert not tab._authored_new.isEnabled()
    assert not tab._authored_edit.isEnabled()
    assert not tab._authored_remove.isEnabled()


def test_a_project_without_a_sprite_offers_create_only(qapp, tmp_path, stubbed):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)

    assert tab._authored_new.isEnabled()
    assert not tab._authored_edit.isEnabled()
    assert not tab._authored_remove.isEnabled()
    assert tab._authored_chip.text() == "No authored sprite."


# --- the commit path ---------------------------------------------------------


def test_creating_through_the_dialog_writes_the_document(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)

    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    # A valid draft is fully described while the dialog is open, and nothing has
    # been written yet: the write is the tab's, after the dialog is accepted.
    assert dialog.document() is not None
    assert dialog._ok.isEnabled()
    assert not (project / "sprites" / "sprites.toml").exists()

    dialog._on_accept()

    assert dialog.document() is not None
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    written = read_project(project).sprites.only()
    assert written.name == "cui"
    assert written.sprite_id == SPRITE_ID
    assert written.actor.behaviour_template == TEMPLATE
    assert (project / "sprites" / "sprites.toml").is_file()


def test_a_commit_bumps_the_revision_and_rearms_the_project_actions(qapp, tmp_path,
                                                                    stubbed):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    session.record_validation(True)
    before = session.project_revision
    assert session.validation_current
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))

    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    assert session.project_revision == before + 1
    assert not session.validation_current  # a stale validation is refused a build
    assert emitted == [True]


def test_undo_removes_the_sprite_and_redo_puts_it_back(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)

    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")
    assert tab._undo_stack.canUndo()

    tab._undo_stack.undo()
    assert not (project / "sprites" / "sprites.toml").exists()
    assert sp.authored_sprite(project) is None
    assert not tab._undo_stack.canUndo()
    assert tab._undo_stack.canRedo()
    assert tab._undo_button.isEnabled() is False
    assert tab._redo_button.isEnabled() is True

    tab._undo_stack.redo()
    assert sp.authored_sprite(project).name == "cui"


def test_removing_writes_an_empty_document_and_undo_restores_it(qapp, tmp_path,
                                                                stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    tab._commit_authored_sprite(AuthoredSprites(), "Remove authored sprite")
    assert sp.authored_sprite(project) is None

    tab._undo_stack.undo()
    assert sp.authored_sprite(project).name == "cui"


def test_reopening_the_surface_shows_the_committed_identity(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    # A fresh tab over the same project, as reopening the project produces.
    reopened = _tab(qapp, _session(project), stubbed)

    assert reopened._authored_chip.text() == "Authored: cui"
    assert "engine id 307" in reopened._authored_summary.text()
    assert reopened._authored_edit.isEnabled()
    assert reopened._authored_remove.isEnabled()


def test_editing_reloads_the_committed_document(qapp, tmp_path, stubbed):
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    editing = sd.SpriteAuthoringDialog(tab, session, editing=True)

    assert editing._name.text() == "cui"
    assert editing._donor.currentData() == 10
    assert editing._animations[0].name == "stand"
    assert editing._anim_sheet.text() == "sprites/cui/stand.png"


def test_editing_keeps_the_placement_the_document_states(qapp, tmp_path, stubbed):
    """The template's own position and box are a default, never an override."""
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._position_x.setValue(5)
    dialog._position_y.setValue(6)
    for box, value in zip(dialog._box, (1, 2, 300, 400)):
        box.setValue(value)
    dialog._refresh()
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    editing = sd.SpriteAuthoringDialog(tab, session, editing=True)

    assert (editing._position_x.value(), editing._position_y.value()) == (5, 6)
    assert tuple(box.value() for box in editing._box) == (1, 2, 300, 400)
    editing._on_accept()
    assert editing.document() == read_project(project).sprites


def test_editing_keeps_a_template_the_image_no_longer_offers(qapp, tmp_path, stubbed):
    """A saved template that is missing must be kept, not silently swapped."""
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    sprite = sp.AuthoredSpriteRequest(
        name="cui", donor_sprite_id=10,
        animations=(AuthoredSpriteAnimation(name="stand",
                                            sheet="sprites/cui/stand.png",
                                            frames=1),),
        free_palette_entries=(), behaviour_template="map:0102/object:0001",
        position=(1, 2), wander_box=(1, 2, 3, 4)).to_sprite(
            template=_template(identity="map:0102/object:0001", slot_index=1),
            sprite_id=SPRITE_ID)
    sp.apply_authored_sprite(project, AuthoredSprites(sprites={sprite.name: sprite}))

    editing = sd.SpriteAuthoringDialog(tab, session, editing=True)

    assert editing._template.currentData() == "map:0102/object:0001"


# --- refusals ----------------------------------------------------------------


def test_a_project_that_cannot_be_read_leaves_the_strip_read_only(qapp, tmp_path,
                                                                  stubbed):
    empty = tmp_path / "not-a-project"
    empty.mkdir()
    session = _session(empty)
    tab = _tab(qapp, session, stubbed)

    assert not tab._authored_new.isEnabled()
    assert tab._authored_chip.text() == "Project unreadable."


def test_a_commit_that_changes_nothing_does_not_touch_the_project(qapp, tmp_path,
                                                                  stubbed):
    """An unchanged save must not make a good validation or build stale."""
    project = _project(tmp_path)
    session = _session(project)
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    revision = session.project_revision
    depth = tab._undo_stack.count()
    written = (project / "sprites" / "sprites.toml").read_bytes()

    tab._commit_authored_sprite(dialog.document(), "New authored sprite")

    assert session.project_revision == revision
    assert tab._undo_stack.count() == depth
    assert (project / "sprites" / "sprites.toml").read_bytes() == written


def test_undo_refuses_to_write_into_another_project(qapp, tmp_path, stubbed,
                                                    monkeypatch):
    """The history names one project; opening another must not redirect it."""
    first = _project(tmp_path / "first")
    second = _project(tmp_path / "second")
    session = _session(first)
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._on_accept()
    tab._commit_authored_sprite(dialog.document(), "New authored sprite")
    prior = AuthoredSprites()
    current = read_project(first).sprites
    command = AuthoredSpriteCommand(tab, first, prior, current, "New authored sprite")

    other = sp.AuthoredSpriteRequest(
        name="bsprite", donor_sprite_id=10,
        animations=(AuthoredSpriteAnimation(name="stand",
                                            sheet="sprites/cui/stand.png",
                                            frames=1),),
        free_palette_entries=(), behaviour_template=TEMPLATE,
        position=(1, 2), wander_box=(1, 2, 3, 4)).to_sprite(
            template=_template(), sprite_id=SPRITE_ID)
    sp.apply_authored_sprite(second, AuthoredSprites(sprites={other.name: other}))
    told = []
    monkeypatch.setattr(QMessageBox, "information",
                        lambda *args, **kwargs: told.append(args[2]))

    session.set_project(second)
    # The strip is the method that reads the open project, so it is also the one
    # that notices the project changed and retires the history with it.
    tab._refresh_authored_strip()
    assert tab._undo_stack.count() == 0  # the history went with the project
    command.undo()

    assert sp.authored_sprite(second).name == "bsprite"
    assert told and "no longer open" in told[0]



    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)

    dialog._refresh()

    assert not dialog._ok.isEnabled()
    assert "at least one animation" in dialog._summary.text()


def test_a_sheet_outside_the_project_is_refused_by_the_model(qapp, tmp_path, stubbed):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._anim_sheet.setText("C:/elsewhere/stand.png")
    dialog._refresh()

    assert not dialog._ok.isEnabled()
    assert "inside the project" in dialog._summary.text()


def test_a_missing_palette_entry_is_refused(qapp, tmp_path, stubbed):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    _fill(dialog)
    dialog._palette.setText("eight")
    dialog._refresh()

    assert not dialog._ok.isEnabled()
    assert "not a palette entry" in dialog._summary.text()


def test_accepting_a_refused_draft_warns_and_stays_open(qapp, tmp_path, stubbed,
                                                        monkeypatch):
    session = _session(_project(tmp_path))
    tab = _tab(qapp, session, stubbed)
    dialog = sd.SpriteAuthoringDialog(tab, session, editing=False)
    warned = []
    monkeypatch.setattr(QMessageBox, "warning",
                        lambda *args, **kwargs: warned.append(args[2]))
    monkeypatch.setattr(sp, "validate_authored_sprite",
                        lambda *args, **kwargs: (_ for _ in ()).throw(
                            ProjectValidationError("the donor proves no single shape")))

    _fill(dialog)
    dialog._on_accept()

    assert warned == ["the donor proves no single shape"]
    assert dialog.document() is None
