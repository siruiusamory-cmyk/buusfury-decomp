"""Headless tests for WORKBENCH-005 Layer 3: palette Undo/Redo (SC1-SC8).

Drives the real `GraphicsTab` against a real on-disk project (so the SDK
`set/get/remove_palette_override` trio runs for real) with the fake sprite
facade injected onto the Session's lazy `sprites` slot, exactly as
test_workbench_graphics.py does. Undo is asserted SEMANTICALLY through the SDK
(`get_palette_override`), never by comparing ROM bytes.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from tools.webfoot import graphics as graphics_sdk  # noqa: E402
from tools.webfoot.project import ProjectMeta, write_project  # noqa: E402
from tools.webfoot.workbench import graphics_tab as gt  # noqa: E402
from tools.webfoot.workbench.graphics_tab import GraphicsTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402

# Reuse the fake facade + session helper from the L2 test module.
from tests.unit.test_workbench_graphics import (  # noqa: E402
    _PROFILE,
    _session_with_sprites,
    qapp,  # noqa: F401  (fixture)
)


@pytest.fixture
def project(tmp_path) -> Path:
    meta = ProjectMeta(1, _PROFILE, "Fake Game", "0" * 64, 1024, "undo-test")
    write_project(tmp_path, meta, enemies=[], characters=[])
    return tmp_path


@pytest.fixture(autouse=True)
def _auto_confirm(qapp, monkeypatch):
    """Ensure a QApplication exists (via qapp) and auto-approve the apply dialog.

    Requesting `qapp` here means every test builds its GraphicsTab under a live
    QApplication - constructing a QWidget with none present crashes the Qt
    runtime rather than raising a Python error.
    """
    monkeypatch.setattr(
        gt.QMessageBox,
        "question",
        staticmethod(lambda *a, **k: gt.QMessageBox.StandardButton.Yes),
    )


def _tab(project) -> GraphicsTab:
    t = GraphicsTab(_session_with_sprites(project))
    t.on_session_changed()
    return t


def _apply(tab, index, rgb):
    tab._palette_pending[index] = rgb
    tab._on_apply()


def _profile():
    return type("P", (), {"id": _PROFILE})()


# --- SC1: one apply -> exactly one command, canUndo -------------------------


def test_apply_pushes_one_command(project):
    tab = _tab(project)
    _apply(tab, 40, (10, 20, 30))
    assert tab._undo_stack.count() == 1
    assert tab._undo_stack.canUndo() is True


# --- SC2: undo reverses through the SDK (semantic) --------------------------


def test_undo_removes_override_when_none_prior(project):
    tab = _tab(project)
    p = _profile()
    assert graphics_sdk.get_palette_override(project, p, 40) is None
    _apply(tab, 40, (10, 20, 30))
    assert graphics_sdk.get_palette_override(project, p, 40) == (10, 20, 30)
    tab._undo_stack.undo()
    # No prior override existed -> undo REMOVES it (semantic reversal).
    assert graphics_sdk.get_palette_override(project, p, 40) is None


def test_undo_restores_prior_override(project):
    tab = _tab(project)
    p = _profile()
    graphics_sdk.set_palette_override(project, p, 40, 1, 2, 3)  # a prior override
    _apply(tab, 40, (200, 100, 50))
    assert graphics_sdk.get_palette_override(project, p, 40) == (200, 100, 50)
    tab._undo_stack.undo()
    # Prior override existed -> undo restores THAT rgb, not remove.
    assert graphics_sdk.get_palette_override(project, p, 40) == (1, 2, 3)


# --- SC3: redo re-applies ----------------------------------------------------


def test_redo_reapplies(project):
    tab = _tab(project)
    p = _profile()
    _apply(tab, 40, (10, 20, 30))
    tab._undo_stack.undo()
    assert graphics_sdk.get_palette_override(project, p, 40) is None
    tab._undo_stack.redo()
    assert graphics_sdk.get_palette_override(project, p, 40) == (10, 20, 30)


# --- SC4: undo and redo each bump revision + emit projectChanged ------------


def test_undo_redo_bump_revision_and_emit(project):
    tab = _tab(project)
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))

    r0 = tab._session.project_revision
    _apply(tab, 40, (10, 20, 30))
    assert tab._session.project_revision == r0 + 1
    assert len(emitted) == 1

    tab._undo_stack.undo()
    assert tab._session.project_revision == r0 + 2
    assert len(emitted) == 2

    tab._undo_stack.redo()
    assert tab._session.project_revision == r0 + 3
    assert len(emitted) == 3


# --- SC5: merging (same index-set collapses; different does not) ------------


def test_same_index_recolours_merge_to_one_entry(project):
    tab = _tab(project)
    p = _profile()
    _apply(tab, 40, (10, 20, 30))
    _apply(tab, 40, (99, 88, 77))  # same index, one continuous gesture
    assert tab._undo_stack.count() == 1
    assert graphics_sdk.get_palette_override(project, p, 40) == (99, 88, 77)
    # One undo restores the ORIGINAL prior state (none), not the intermediate.
    tab._undo_stack.undo()
    assert graphics_sdk.get_palette_override(project, p, 40) is None


def test_different_indices_do_not_merge(project):
    tab = _tab(project)
    _apply(tab, 40, (10, 20, 30))
    _apply(tab, 7, (1, 2, 3))  # different index-set -> separate entry
    assert tab._undo_stack.count() == 2


# --- SC6: a redo that fails surfaces the SDK error, no traceback ------------


def test_apply_redo_failure_surfaces_and_does_not_corrupt(project, monkeypatch):
    tab = _tab(project)
    warnings = []
    monkeypatch.setattr(
        gt.QMessageBox, "critical", lambda *a, **k: warnings.append(a[-1])
    )
    # CQA-07 assertion change: the apply path now commits its whole batch through
    # `set_palette_overrides` - one whole-project write per gesture instead of one
    # per staged index - so the SDK write whose failure this test drives is the
    # batch function. The intent and every assertion below are unchanged: an SDK
    # write failure is surfaced and leaves the undo stack and the revision intact.
    monkeypatch.setattr(
        gt.graphics_sdk,
        "set_palette_overrides",
        lambda *a, **k: (_ for _ in ()).throw(graphics_sdk.GraphicsError("boom")),
    )
    before = tab._session.project_revision
    tab._palette_pending[40] = (1, 2, 3)
    tab._on_apply()  # must not raise a traceback

    assert warnings == ["boom"]
    # Stack not corrupted: nothing recorded, revision unchanged.
    assert tab._undo_stack.count() == 0
    assert tab._session.project_revision == before


# --- SC8: existing L2 behaviour intact (apply still records + emits) --------


def test_apply_still_records_and_emits(project):
    tab = _tab(project)
    p = _profile()
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))
    _apply(tab, 40, (5, 6, 7))
    assert emitted == [True]
    assert graphics_sdk.get_palette_override(project, p, 40) == (5, 6, 7)
