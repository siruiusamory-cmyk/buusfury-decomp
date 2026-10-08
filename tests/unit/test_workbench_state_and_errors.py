"""CQA-05/CQA-06 regression tests: staged Workbench state and the open boundary.

`CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001`. The two findings are one ticket
because they interact - an error path can itself be a state-loss path - so the
combined case is pinned here as well.

**CQA-05.** `MainWindow._on_project_changed` answered ANY editor's
`projectChanged` by calling every peer's `on_session_changed`, and that entry
point is where staged in-memory authoring state is legitimately dropped. A
placement drag, a dialogue Apply or a palette Apply therefore silently discarded
the Map Browser's staged layout edits, the placement undo history, the pending
palette colours and the typed-but-unapplied dialogue text, and left the Maps
mode strip checked on a mode the editor was no longer in.

**CQA-06.** `Session.open_rom` was not total, so `rom.RomReadError`,
`maps.MapError` and the bare byte-read `OSError` left the Open ROM slot, which
caught `SessionError` alone - the documented dead-click failure.

Synthetic: every ROM-touching SDK read is stubbed, so this file needs neither
the canonical ROM nor the assembled atlas. The duck-typed edit session and the
map/render doubles come from `test_workbench_map_browser`, which already owns
them; duplicating that fake here would let the two drift.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtGui = pytest.importorskip("PySide6.QtGui")

from tools.export import map_browser as mb  # noqa: E402
from tools.webfoot import atlas as atlas_sdk  # noqa: E402
from tools.webfoot import atlas_build  # noqa: E402
from tools.webfoot import capability  # noqa: E402
from tools.webfoot import maps as maps_sdk  # noqa: E402
from tools.webfoot import rom as rom_sdk  # noqa: E402
from tools.webfoot import text as text_sdk  # noqa: E402
from tools.webfoot.formats.map_entry import MapEntryProfileError  # noqa: E402
from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.project import ProjectError  # noqa: E402
from tools.webfoot.workbench import atlas_browser as ab  # noqa: E402
from tools.webfoot.workbench import graphics_tab as gt  # noqa: E402
from tools.webfoot.workbench import inspector as insp  # noqa: E402
from tools.webfoot.workbench import map_browser_tab as mbt  # noqa: E402
from tools.webfoot.workbench import session as session_mod  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.map_tab import MapWorkspaceTab  # noqa: E402
from tools.webfoot.workbench.session import Session, SessionError  # noqa: E402
from tests.unit.test_workbench_map_browser import (  # noqa: E402,F401
    CHUNKS,
    MAP,
    SLOT,
    _FakeEditor,
    _entry,
    _result,
    _target,
)

#: Every SDK family the Open ROM path can meet, as an instance. CQA-06 is the
#: claim that none of these escapes the slot, so each one is exercised.
ESCAPING_FAMILIES = (
    ("SessionError (control)", SessionError("session refused the image")),
    ("RomReadError", rom_sdk.RomReadError("ROM does not exist")),
    ("RomChangedError", rom_sdk.RomChangedError("ROM changed while read")),
    ("MapError", maps_sdk.MapError("placement overlaps map table")),
    ("UnknownMapError", maps_sdk.UnknownMapError("no map record with identity 7")),
    ("MapEntryProfileError", MapEntryProfileError("not authorized for map access")),
    ("CapabilityError", capability.CapabilityError("capability not proven")),
    ("AtlasError", atlas_sdk.AtlasError("malformed atlas line")),
    ("AtlasBuildError", atlas_build.AtlasBuildError("missing artifact atlas.jsonl")),
    ("TextTableError", text_sdk.TextTableError("text table is truncated")),
    ("TextProfileError", text_sdk.TextProfileError("no text table in this profile")),
    ("OSError", OSError("the file is locked by another process")),
)


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture(scope="module")
def catalog():
    return RomProfileCatalog.load("config/roms.yaml")


def _chunk_images(rom, index, addresses, *, char_data=None):
    return tuple(
        mb.ChunkImage(
            address=address, width=256, height=256, pixels=bytes([7]) * (256 * 256)
        )
        for address in addresses
    )


@pytest.fixture
def shell(qapp, catalog, monkeypatch, tmp_path):
    """A real `MainWindow` over a synthetic image, with a working layout session.

    The doubles are the same ones `test_workbench_map_browser` drives its edit
    mode with, so this exercises the real shell, the real `MapsEditor` mode strip
    and the real `MapBrowserTab` state machine - only the ROM-coupled reads are
    replaced.
    """
    entries = (_entry(MAP, "Synthetic Map"),)
    base = _result(MAP)
    preview = _result(MAP)
    fake = _FakeEditor(_target(), preview)
    monkeypatch.setattr(mbt.mv, "read_map_index", lambda rom: entries)
    monkeypatch.setattr(mbt.mv, "render_map", lambda rom, index, **kwargs: base)
    monkeypatch.setattr(mbt.mv, "render_chunk_images", _chunk_images)
    monkeypatch.setattr(mbt, "MapLayoutEditor", lambda rom_image: fake)

    session = Session(rom_image=b"synthetic", rom_path=tmp_path / "rom.gba")
    session.profile = SimpleNamespace(id="buus_fury_usa_rev0_01c1707f")
    session.project_dir = tmp_path
    window = MainWindow(session, catalog)
    window._on_rom_opened()
    return SimpleNamespace(window=window, fake=fake, session=session)


def stage_layout_edit(shell) -> mbt.MapBrowserTab:
    """One committed layout edit in Layout mode, made the way a user makes it."""
    shell.window._maps.set_mode("layout")
    shell.window.show_editor("Maps")
    browser = shell.window._maps.browser
    browser._list.setCurrentRow(0)
    # MAP-TILE-PAINT-001: the palette selects the BRUSH and a click paints, so
    # the edit is made by choosing a value and then painting a cell with it.
    browser._chooser.blockSignals(True)
    browser._chooser.setCurrentRow(1)
    browser._chooser.blockSignals(False)
    browser._on_chunk_selected(browser._chooser.item(1))
    browser.begin_paint_stroke()
    browser.paint_cell(0)
    browser.end_paint_stroke()
    return browser


def staged_state(browser: mbt.MapBrowserTab) -> tuple:
    """Everything the Map Browser stages, in one comparable value."""
    return (
        browser._edit_mode,
        browser._editor is not None,
        browser.unsaved_edit_count(),
        browser._selected_cell,
        browser._draft,
        tuple(browser._saved),
        browser._brush_ordinal,
        tuple((edit.map_index, edit.layer_slot, edit.cell) for edit in browser._editor.edits())
        if browser._editor is not None
        else (),
        browser._undo_stack.count(),
    )


# --- CQA-05: a project mutation must not discard staged work -----------------


def test_a_project_mutation_preserves_staged_layout_edits_and_the_mode_strip(shell):
    """The audit's exact path: stage an edit, mutate the project, keep the edit.

    Also pins the second half of the finding - the strip must not claim a mode
    the editor is not in - because the two halves were one defect.
    """
    browser = stage_layout_edit(shell)
    before = staged_state(browser)
    assert before[2] == 1, "one unsaved layout edit is staged"
    assert "1 unsaved" in shell.window.windowTitle()

    # An unrelated project mutation, through the real shell entry point.
    shell.window._on_project_changed()

    assert staged_state(browser) == before
    assert shell.window._maps.mode() == "layout"
    assert shell.window._maps.mode_buttons()["layout"].isChecked()
    assert browser._edit_mode, "the strip's mode and the editor still agree"
    assert shell.window._maps.unsaved_edit_count() == 1
    assert "1 unsaved" in shell.window.windowTitle()


def test_a_rom_change_still_resets_the_layout_session(shell):
    """The control for the test above: the session reset is not simply gone.

    A different image is a different base, so this is the one event that may -
    and must - discard the session.
    """
    browser = stage_layout_edit(shell)
    assert browser.unsaved_edit_count() == 1

    shell.window._on_rom_opened()

    assert browser._editor is None
    assert browser.unsaved_edit_count() == 0
    assert not browser._edit_mode
    # ...and the strip follows the editor into view mode rather than staying on
    # a mode the editor is no longer in.
    assert shell.window._maps.mode() != "layout"


def test_a_project_mutation_preserves_the_paint_undo_history_and_the_gesture(shell):
    """MAP-TILE-PAINT-001's own CQA-05 case, on the paint surface.

    The audit path, exactly: stage painted cells, perform an unrelated supported
    project mutation, and require that the staged cells, their exact previous
    values and the undo/redo history are all still valid - then that undo still
    restores the values the stroke captured.
    """
    browser = stage_layout_edit(shell)
    command = browser._undo_stack.command(0)
    staged = staged_state(browser)
    assert staged[2] == 1, "one staged paint"
    assert staged[8] == 1, "one undo entry for the gesture"
    captured = command.previous

    # An unrelated project mutation, through the real shell entry point.
    shell.window._on_project_changed()

    assert staged_state(browser) == staged
    assert browser._undo_stack.command(0).previous == captured
    assert browser._undo_stack.canUndo() and not browser._undo_stack.canRedo()
    assert shell.window._maps.unsaved_edit_count() == 1

    # The history is still VALID, not merely present: undo un-stages the cell,
    # and redo puts the gesture's own value back.
    browser._undo_stack.undo()
    assert browser._editor.edits_for(MAP) == ()
    assert browser._undo_stack.canRedo()
    browser._undo_stack.redo()
    redone = browser._editor.edits_for(MAP)
    assert [edit.cell for edit in redone] == [0]
    assert redone[0].replacement == CHUNKS[1]
    assert redone[0].original == CHUNKS[0]


def test_a_session_change_still_clears_the_paint_history(shell):
    """The control: the paint history is not simply immortal."""
    browser = stage_layout_edit(shell)
    assert browser._undo_stack.count() == 1
    shell.window._on_rom_opened()
    assert browser._editor is None
    assert browser._undo_stack.count() == 0
    assert browser.unsaved_edit_count() == 0



    """CQA-05's second surface: the placement history must survive.

    A real `QUndoStack` is used rather than a stub stack, because the claim is
    about the object the shell's Edit-menu Undo is routed to.
    """
    from PySide6.QtGui import QUndoCommand

    class _Noop(QUndoCommand):
        def redo(self):
            pass

        def undo(self):
            pass

    tab = MapWorkspaceTab(Session())
    tab._undo_stack.push(_Noop())
    assert tab._undo_stack.count() == 1

    tab.on_project_mutated()

    assert tab._undo_stack.count() == 1
    assert tab._undo_stack.canUndo()

    # And a session change is still the event that clears it.
    tab.on_session_changed()
    assert tab._undo_stack.count() == 0


def test_a_project_mutation_preserves_pending_palette_colours(qapp):
    """The same root cause on the Graphics editor's staged recolours."""
    tab = gt.GraphicsTab(Session())
    tab._palette_pending[7] = (10, 20, 30)

    tab.on_project_mutated()

    assert tab._palette_pending == {7: (10, 20, 30)}

    tab.on_session_changed()
    assert tab._palette_pending == {}, "a different image's palette drops them"


def test_a_project_mutation_preserves_typed_dialogue_text(qapp, monkeypatch, tmp_path):
    """The same root cause on the Inspector's typed-but-unapplied replacement."""
    session = Session(rom_image=b"synthetic")
    session.project_dir = tmp_path
    session.profile = SimpleNamespace(id="synthetic_profile")
    tab = insp.InspectorTab(session)
    tab._target = SimpleNamespace(name="dialog 0")
    tab._original = "the original line"
    tab._project_replacement = None
    tab._set_editor_text("typed but not applied")
    tab._edit.setEnabled(True)

    monkeypatch.setattr(
        insp.dialogue_sdk, "get_dialogue_replacement", lambda *a, **k: "committed line"
    )

    tab.on_project_mutated()

    assert tab._edit.text() == "typed but not applied"
    # ...while the committed facts ABOUT the project are refreshed, so the
    # protected editor cannot leave a stale "current replacement" label.
    assert tab._project_replacement == "committed line"
    assert "committed line" in tab._replacement_label.text()


def test_a_clean_dialogue_editor_is_re_read_from_the_project(qapp, monkeypatch):
    """The other half: nothing staged means the project is re-read as before."""
    tab = insp.InspectorTab(Session())
    tab._target = SimpleNamespace(name="dialog 0")
    tab._original = "the original line"
    tab._project_replacement = "the committed line"
    tab._set_editor_text("the committed line")
    tab._edit.setEnabled(True)
    tab._session.selected_result = {"_mode": "decoded", "text": "a record"}
    reread: list[object] = []
    monkeypatch.setattr(tab, "_refresh_authoring", lambda result: reread.append(result))

    tab.on_project_mutated()

    assert reread == [tab._session.selected_result]


def test_the_shell_routes_a_project_mutation_to_on_project_mutated(shell, monkeypatch):
    """The ownership fix itself: one event, one entry point per peer.

    This is the shared change CQA-05 is really about. Before it, the shell sent
    a project mutation to `on_session_changed` on every peer, which is the
    method that drops staged state by design.
    """
    calls: list[tuple[str, str]] = []

    def record(name: str, method: str):
        def spy(*_args, **_kwargs) -> None:
            calls.append((name, method))

        return spy

    for name in ("_inspector", "_launcher", "_scene", "_maps", "_graphics", "_build"):
        peer = getattr(shell.window, name)
        for method in ("on_project_mutated", "on_session_changed"):
            if hasattr(peer, method):
                monkeypatch.setattr(peer, method, record(name, method))

    shell.window._on_project_changed()

    assert calls == [
        ("_inspector", "on_project_mutated"),
        ("_launcher", "on_project_mutated"),
        ("_scene", "on_project_mutated"),
        ("_maps", "on_project_mutated"),
        ("_graphics", "on_project_mutated"),
        ("_build", "on_project_mutated"),
    ]


# --- CQA-05: an operation that cannot preserve staged work must ask ----------


def test_opening_another_image_asks_before_discarding_staged_edits(
    shell, monkeypatch, tmp_path
):
    """A ROM change cannot preserve layout edits, so it must ask - not discard."""
    browser = stage_layout_edit(shell)
    asked: list[str] = []
    opened: list[str] = []
    monkeypatch.setattr(
        ab.QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *a, **k: (str(tmp_path / "other.gba"), "")),
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "question",
        staticmethod(
            lambda *a, **k: (
                asked.append(a[2]),
                QtWidgets.QMessageBox.StandardButton.Cancel,
            )[1]
        ),
    )
    monkeypatch.setattr(
        shell.session, "open_rom", lambda *a, **k: opened.append("open")
    )

    shell.window._open_rom()

    assert asked and "unsaved edit" in asked[0]
    assert opened == [], "cancelling the prompt does not open anything"
    assert browser.unsaved_edit_count() == 1
    assert browser._edit_mode


def test_opening_another_image_proceeds_when_the_user_discards(shell, monkeypatch, tmp_path):
    """The other answer to the same prompt: the user chose to discard."""
    stage_layout_edit(shell)
    opened: list[str] = []
    monkeypatch.setattr(
        ab.QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *a, **k: (str(tmp_path / "other.gba"), "")),
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "question",
        staticmethod(
            lambda *a, **k: QtWidgets.QMessageBox.StandardButton.Discard
        ),
    )
    monkeypatch.setattr(shell.session, "open_rom", lambda *a, **k: opened.append("open"))

    shell.window._open_rom()

    assert opened == ["open"]


def test_closing_refuses_to_discard_unwritten_layout_edits(shell, monkeypatch):
    """The other irreversible case: the process ends, nothing is recoverable."""
    stage_layout_edit(shell)
    monkeypatch.setattr(
        QtWidgets.QMessageBox,
        "question",
        staticmethod(lambda *a, **k: QtWidgets.QMessageBox.StandardButton.Cancel),
    )
    event = QtGui.QCloseEvent()

    shell.window.closeEvent(event)

    assert not event.isAccepted(), "a cancelled close must not accept the event"


# --- CQA-06: the Open ROM slot is total over the SDK families ---------------


@pytest.mark.parametrize(
    "family,error", ESCAPING_FAMILIES, ids=[name for name, _ in ESCAPING_FAMILIES]
)
def test_every_escaping_family_is_contained_at_the_open_rom_slot(
    shell, monkeypatch, tmp_path, family, error
):
    """Drive each family through the REAL slot and require a reported failure.

    Not one of these may reach Qt as an unhandled exception, and none may leave
    the click looking dead: the surface states what failed and shows a dialogue.
    """
    reported: list[str] = []
    monkeypatch.setattr(
        ab.QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *a, **k: (str(tmp_path / "image.gba"), "")),
    )
    monkeypatch.setattr(
        shell.session, "open_rom", lambda *a, **k: (_ for _ in ()).throw(error)
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "critical", staticmethod(lambda *a: reported.append(a[-1]))
    )

    shell.window._atlas.open_rom_dialog()  # must not raise

    assert reported == [str(error)], f"{family} was not reported to the user"
    assert shell.window._atlas._load_status.text().startswith("Load failed:")
    assert str(error) in shell.window._atlas._load_status.text()


@pytest.mark.parametrize(
    "family,error", ESCAPING_FAMILIES, ids=[name for name, _ in ESCAPING_FAMILIES]
)
def test_open_rom_is_total_over_the_sdk_families(
    catalog, monkeypatch, tmp_path, family, error
):
    """The boundary itself: the SDK family leaves `open_rom` as `SessionError`.

    `identify_rom` is the real first call, so this proves the conversion happens
    for each family there rather than only at the slot.
    """
    monkeypatch.setattr(
        session_mod, "identify_rom", lambda *a, **k: (_ for _ in ()).throw(error)
    )
    session = Session()

    with pytest.raises(SessionError) as excinfo:
        session.open_rom(tmp_path / "image.gba", catalog)

    assert str(error) in str(excinfo.value)
    if not isinstance(error, SessionError):
        assert not isinstance(excinfo.value, type(error)), "converted, not passed through"


def test_a_programmer_error_is_not_converted_into_a_user_facing_open_failure(
    shell, catalog, monkeypatch, tmp_path
):
    """The overcatch control (audit mutation M4).

    An indiscriminate boundary - `except Exception`, or a bare `ValueError`
    catch, since every family above derives from `ValueError` - would report a
    defect in the SDK as "your ROM could not be opened" and hide the traceback
    the developer policy requires to stay visible. A programmer error must still
    leave `open_rom`, and still leave the slot.
    """
    def _boom(*args, **kwargs):
        raise RuntimeError("an invariant inside the reader was violated")

    monkeypatch.setattr(session_mod, "identify_rom", _boom)
    monkeypatch.setattr(
        ab.QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *a, **k: (str(tmp_path / "image.gba"), "")),
    )
    reported: list[str] = []
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "critical", staticmethod(lambda *a: reported.append(a[-1]))
    )

    with pytest.raises(RuntimeError):
        Session().open_rom(tmp_path / "image.gba", catalog)
    with pytest.raises(RuntimeError):
        shell.window._atlas.open_rom_dialog()
    assert reported == [], "a programmer error is not dressed up as a user-facing one"


def test_a_malformed_decoded_text_artifact_is_a_typed_failure(
    shell, monkeypatch, tmp_path
):
    """A corrupt artifact is an expected failure, not a bare `JSONDecodeError`.

    `load_decoded_text` read its artifact with an unwrapped `json.loads`, so a
    malformed line raised a `JSONDecodeError` - a `ValueError` belonging to no
    SDK family, which therefore escaped both the session's conversion and the
    slot's catch list. It is now the module's own `AtlasBuildError`.
    """
    artifact = tmp_path / f"{atlas_build.DECODED_TEXT_ARTIFACT}.jsonl"
    artifact.write_text("{ not json\n", encoding="utf-8")

    with pytest.raises(atlas_build.AtlasBuildError) as excinfo:
        atlas_build.load_decoded_text(tmp_path)

    assert not isinstance(excinfo.value, json.JSONDecodeError)
    assert "malformed artifact" in str(excinfo.value)


def test_a_panel_that_cannot_re_read_an_opened_image_is_reported(
    shell, monkeypatch, tmp_path
):
    """A peer's failure is contained, reported, and does not stop the others.

    The image is open and the session holds it, so reporting a failed open would
    be false; and a panel failing must not leave the panels after it still
    showing the previous image, which is the session inconsistency CQA-06 is
    about.
    """
    warnings: list[str] = []
    monkeypatch.setattr(
        ab.QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *a, **k: (str(tmp_path / "image.gba"), "")),
    )

    def _open(path, catalog):
        shell.session.rom_path = Path(path)
        shell.session.profile = SimpleNamespace(id="synthetic_profile")

    monkeypatch.setattr(shell.session, "open_rom", _open)
    monkeypatch.setattr(
        mbt.MapBrowserTab,
        "on_session_changed",
        lambda self: (_ for _ in ()).throw(maps_sdk.MapError("panel re-read failed")),
    )
    refreshed: list[str] = []
    monkeypatch.setattr(
        shell.window._launcher, "on_session_changed", lambda: refreshed.append("launcher")
    )
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "warning", staticmethod(lambda *a: warnings.append(a[-1]))
    )

    shell.window._atlas.open_rom_dialog()  # must not raise

    assert warnings and "could not re-read" in warnings[0]
    assert "Maps" in warnings[0] and "panel re-read failed" in warnings[0]
    assert refreshed == ["launcher"], "the panels after the failing one still refreshed"
    assert "could not refresh" in shell.window._status_context.text()
    assert shell.session.rom_path == tmp_path / "image.gba"


# --- CQA-05 + CQA-06: an unrelated failure must not lose staged work --------


def test_an_unrelated_failed_action_leaves_staged_edits_and_the_session_usable(
    shell, monkeypatch
):
    """The key combined criterion.

    pending staged edit -> an unrelated operation mutates the project -> an
    unrelated operation then FAILS with an expected SDK exception -> the error is
    shown, the staged edit is intact, and the session is still usable.

    Both halves are dialogue actions, which is the audit's own example of an
    "unrelated" mutation, and neither can touch a map layout edit.
    """
    browser = stage_layout_edit(shell)
    before = staged_state(browser)
    inspector = shell.window._inspector
    inspector._target = SimpleNamespace(name="dialog 0")
    inspector._original = "the original line"
    inspector._project_replacement = None
    inspector._set_editor_text("typed but not applied")
    inspector._edit.setEnabled(True)
    monkeypatch.setattr(
        insp.dialogue_sdk, "validate_dialogue_replacement",
        lambda *a, **k: SimpleNamespace(valid=True, problems=()),
    )
    monkeypatch.setattr(
        insp.dialogue_sdk, "get_dialogue_replacement", lambda *a, **k: None
    )
    errors: list[str] = []
    monkeypatch.setattr(
        QtWidgets.QMessageBox, "critical", staticmethod(lambda *a: errors.append(a[-1]))
    )

    # An unrelated mutation succeeds and fans out through the shell.
    shell.window._on_project_changed()
    # ...and an unrelated action then fails with a typed SDK failure.
    monkeypatch.setattr(
        insp.dialogue_sdk,
        "set_dialogue_replacement",
        lambda *a, **k: (_ for _ in ()).throw(
            insp.dialogue_sdk.DialogueAuthoringError("the replacement is too long")
        ),
    )
    inspector._on_apply()

    assert errors == ["the replacement is too long"], "the failure was shown to the user"
    assert staged_state(browser) == before, "the staged layout edit survived"
    assert browser._edit_mode
    assert shell.window._maps.mode() == "layout"
    assert shell.window._maps.unsaved_edit_count() == 1
    assert shell.session.rom_path is not None, "the session is still open and usable"
