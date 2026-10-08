"""Headless Workbench dialogue controller/state tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.project import (  # noqa: E402
    PROJECT_FORMAT_VERSION,
    ProjectMeta,
    read_project,
    write_project,
)
from tools.webfoot.workbench.inspector import InspectorTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


PROFILE_ID = "buus_fury_usa_rev0_01c1707f"
SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
SUPPORTED = {
    "_mode": "decoded",
    "source": "decoded-container-text",
    "text": "- NoGood luck, Goku!Be sure to talk",
    "identity": {"packed_handle": "0x02002641"},
}


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def project(tmp_path: Path):
    root = tmp_path / "project"
    write_project(
        root,
        ProjectMeta(
            format_version=PROJECT_FORMAT_VERSION,
            profile_id=PROFILE_ID,
            game="buus_fury",
            base_rom_sha256=SHA256,
            base_rom_size=8388608,
            name="workbench-dialogue",
        ),
        enemies=[],
        characters=[],
    )
    return root


@pytest.fixture
def session(project):
    profile = next(
        item for item in RomProfileCatalog.load("config/roms.yaml").profiles
        if item.id == PROFILE_ID
    )
    value = Session(profile=profile, rom_image=b"canonical")
    value.set_project(project)
    return value


@pytest.fixture
def inspector(qapp, session, monkeypatch):
    monkeypatch.setattr(
        "tools.webfoot.dialogue.get_dialogue_original",
        lambda canonical, profile, target: "Good luck, Goku!",
    )
    return InspectorTab(session)


def test_supported_target_enables_editing_without_typing_mutation(inspector, project):
    inspector.show_result(SUPPORTED)
    assert inspector._authoring_status.text() == "Editing available"
    assert inspector._target_label.text() == "Target: goku-greeting"
    assert inspector._original_label.text() == "Original: Good luck, Goku!"
    assert inspector._edit.isEnabled()

    inspector._edit.setText("Nice work, Goku!")
    assert read_project(project).dialogues == {}
    assert inspector._validation_label.text() == "✓ Valid"


def test_unsupported_result_and_no_project_fail_closed(qapp, session, inspector, monkeypatch):
    unsupported = {**SUPPORTED, "identity": {"packed_handle": "0x00000000"}}
    inspector.show_result(unsupported)
    assert not inspector._edit.isEnabled()
    assert "not available" in inspector._authoring_status.text()

    session.project_dir = None
    inspector.show_result(SUPPORTED)
    assert not inspector._edit.isEnabled()
    assert "requires an open Webfoot project" in inspector._authoring_status.text()


def test_profile_mismatched_project_remains_read_only(
    qapp, tmp_path, session, inspector
):
    other = tmp_path / "other-profile"
    write_project(
        other,
        ProjectMeta(
            format_version=PROJECT_FORMAT_VERSION,
            profile_id="legacy_of_goku_ii_usa_rev0_204142e1",
            game="legacy_of_goku_ii",
            base_rom_sha256="0" * 64,
            base_rom_size=8388608,
            name="wrong-profile",
        ),
        enemies=[],
        characters=[],
    )
    session.set_project(other)

    inspector.show_result(SUPPORTED)

    assert not inspector._edit.isEnabled()
    assert not inspector._apply.isEnabled()
    assert "does not match open ROM profile" in inspector._authoring_status.text()


def test_invalid_apply_does_not_mutate_project(inspector, project):
    inspector.show_result(SUPPORTED)
    # 4096 encoded bytes: one past what a durable handle's 11-bit halfword length
    # field can describe. Shorter-than-retail text is VALID since
    # DIALOGUE-VARIABLE-LENGTH-001, so the input has to exceed the field to be
    # invalid at all.
    inspector._edit.setText("a" * 2048)
    inspector._on_apply()
    assert read_project(project).dialogues == {}
    assert not inspector._apply.isEnabled()


def test_a_longer_than_retail_line_is_editable_through_the_existing_path(
    inspector, project
):
    """Section 28: the new capability reaches the editor with no new surface.

    The Inspector calls the same validation and apply entry points it always did.
    What changed is the production contract behind them, so a line that does not
    encode to the retail record's 32 bytes is now valid, applies, and persists as
    the one semantic entry - not a second one keyed on the new handle.
    """
    inspector.show_result(SUPPORTED)
    longer = "Hot take: SSJ3 is the worst form imo"
    inspector._edit.setText(longer)
    assert inspector._validation_label.text() == "✓ Valid"
    assert inspector._apply.isEnabled()

    inspector._on_apply()
    assert read_project(project).dialogues == {"goku-greeting": longer}


def test_apply_invalidates_validation_and_build_and_reopens_override(
    inspector, session, project
):
    inspector.show_result(SUPPORTED)
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision

    inspector._edit.setText("Nice work, Goku!")
    inspector._on_apply()

    assert read_project(project).dialogues == {"goku-greeting": "Nice work, Goku!"}
    assert not session.validation_current
    assert not session.build_current
    assert session.last_build is None
    inspector.show_result(SUPPORTED)
    assert inspector._edit.text() == "Nice work, Goku!"
    assert inspector._revert.isEnabled()


def test_revert_removes_override_and_invalidates_state(inspector, session, project):
    inspector.show_result(SUPPORTED)
    inspector._edit.setText("Nice work, Goku!")
    inspector._on_apply()
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision

    inspector._on_revert()

    assert read_project(project).dialogues == {}
    assert not session.validation_current
    assert not session.build_current
    assert session.last_build is None
    assert inspector._edit.text() == "Good luck, Goku!"


def test_a_new_image_empties_the_record_panel(inspector, session):
    """N-07: the record, handle rows and references belong to one image.

    The panel used to keep the previous image's text while re-reading its
    authoring labels against the new image's bytes, so "Original:" and "Record
    text" could describe two different ROMs with nothing naming which.
    """
    with_refs = {
        **SUPPORTED,
        "identity": {**SUPPORTED["identity"], "reference_sites": [0x08001234]},
    }
    inspector.show_result(with_refs)
    assert inspector._text.toPlainText()
    assert inspector._handle_rows
    assert inspector._refs.rowCount() == 1
    assert inspector._handle_form.rowCount() >= 1

    session.selected_result = None
    inspector.on_session_changed()

    assert inspector._text.toPlainText() == ""
    assert inspector._handle_rows == {}
    assert inspector._refs.rowCount() == 0
    # Every row must actually be removed, not merely detached: the form owns the
    # rows the next record's rows stack below. (A detached label becomes a stray
    # top-level widget rather than a row, and a shared QApplication makes that
    # count unstable to assert from a portable test.)
    assert inspector._handle_form.rowCount() == 0
    assert inspector._handle_form.count() == 0
    assert not inspector._edit.isEnabled()


def test_typed_text_does_not_cross_a_project_switch(inspector, session, tmp_path):
    """N-09 shape: the staged value names the outgoing project's intent.

    An unrelated project mutation keeps what the user typed (CQA-05). A mutation
    that swapped the open project is not unrelated: applying the typed value would
    write it into the incoming project's dialogues document.
    """
    inspector.show_result(SUPPORTED)
    inspector._edit.setText("typed against the first project")
    assert inspector._editor_is_dirty()

    other = tmp_path / "second-project"
    write_project(
        other,
        ProjectMeta(
            format_version=PROJECT_FORMAT_VERSION,
            profile_id=PROFILE_ID,
            game="buus_fury",
            base_rom_sha256=SHA256,
            base_rom_size=8388608,
            name="second",
        ),
        enemies=[],
        characters=[],
    )
    session.project_dir = other
    inspector.on_project_mutated()

    assert inspector._edit.text() == "Good luck, Goku!"
    assert not inspector._editor_is_dirty()
