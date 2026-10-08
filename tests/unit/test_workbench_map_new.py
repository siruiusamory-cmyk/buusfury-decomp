"""MAP-NEW-AUTHORING-001: the Workbench new-map surface.

The form and the undoable command, offscreen. What the command must guarantee is
that one gesture writes one document and undo restores exactly the document the
gesture replaced - which is the whole reason the two are carried on the command
rather than re-read from disk at undo time. The image half is
`tests/integration/test_map_authoring_rom.py`'s.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tools.webfoot import map_authoring as map_new  # noqa: E402
from tools.webfoot.project import AuthoredMap, AuthoredMaps  # noqa: E402
from tools.webfoot.workbench.map_browser_tab import (  # noqa: E402
    NewMapCommand,
    NewMapDialog,
)

NAME = "cave"
DONOR = 40


@pytest.fixture()
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _document(*names: str) -> AuthoredMaps:
    return AuthoredMaps(maps={
        name: AuthoredMap(name, DONOR, 0x17, index + 1)
        for index, name in enumerate(names)
    })


class _StubTab:
    """The two calls `NewMapCommand` is allowed to make on its tab."""

    def __init__(self) -> None:
        self.written: list[AuthoredMaps] = []

    def write_authored_maps_document(self, document: AuthoredMaps) -> None:
        self.written.append(document)


def test_the_command_does_not_rewrite_the_document_it_was_pushed_for():
    """The gesture already wrote it; the stack's first redo must be a no-op."""
    tab = _StubTab()
    command = NewMapCommand(tab, _document("cave"), _document("cave", "ruins"),
                            "Create map-new:cave from map:0040")

    command.redo()

    assert tab.written == []


def test_undo_restores_the_document_the_gesture_replaced():
    """The previous document travels on the command, not re-read from disk."""
    tab = _StubTab()
    previous = _document("cave")
    applied = _document("cave", "ruins")
    command = NewMapCommand(tab, previous, applied, "Create map-new:ruins")

    command.undo()

    assert tab.written == [previous]
    assert command.previous == previous
    assert command.applied == applied


def test_redo_after_undo_rewrites_the_gesture_document():
    tab = _StubTab()
    previous = _document("cave")
    applied = _document("cave", "ruins")
    command = NewMapCommand(tab, previous, applied, "Create map-new:ruins")

    command.redo()  # the redo a push performs: the gesture already applied
    command.undo()
    command.redo()

    assert tab.written == [previous, applied]


def test_the_command_family_id_is_its_own():
    """A merge class id shared with another gesture family would merge them."""
    tab = _StubTab()
    command = NewMapCommand(tab, _document("cave"), _document("cave"), "x")

    assert command.id() == 0x4D41
    assert command.mergeWith(command) is False


def _dialog(qapp, preview, applied_log, refuse: bool = False):
    return NewMapDialog(
        None,
        donors=[(40, "West City"), (41, "Ruins")],
        default_name=NAME,
        default_donor=DONOR,
        default_key=(0x17, 0x01),
        preview=preview,
        apply_command=lambda *request: (
            applied_log.append(request), not refuse)[1],
    )


def test_the_form_states_the_sdk_refusal_and_stays_open(qapp):
    def preview(*_request):
        raise map_new.MapAuthoringError("key 0x1701 is already used by a map")

    log: list = []
    dialog = _dialog(qapp, preview, log, refuse=True)

    assert "Not supported" in dialog._summary.text()
    assert "already used" in dialog._summary.text()

    dialog._accept()

    # The tab's own guard ran and refused, so the form stays open.
    assert log == [(NAME, DONOR, 0x17, 0x01)]
    assert dialog.result() != QtWidgets.QDialog.DialogCode.Accepted


def test_the_form_accepts_and_hands_over_its_fields_in_order(qapp):
    log: list = []
    dialog = _dialog(qapp, lambda *request: "Creates map:0452", log)

    assert dialog._summary.text() == "Creates map:0452"

    dialog._accept()

    assert log == [(NAME, DONOR, 0x17, 0x01)]
    assert dialog.result() == QtWidgets.QDialog.DialogCode.Accepted
