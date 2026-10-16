"""CQA-07 cost regression: the palette editor must not do per-element project work.

`CQA-07-WORKBENCH-PERF-AND-CI-001`. The audit's finding (section C.2) is that
the palette editor and `palette_users` did **full-project and full-corpus work
per UI element, on the UI thread**:

* `_populate_palette` built 256 swatches and each one re-read and re-parsed the
  whole project to find the override map the caller had computed one line
  earlier - 257 whole-project parses per repaint;
* `_refresh_pending_ui` and `_on_apply` called `palette_users` once **per
  pending colour**, and each call rescanned every decoded graphic's pixels;
* a single Apply performed **two** full repaints on the UI thread, because the
  shell answers `projectChanged` by calling `on_project_mutated()` on the very
  tab that emitted it.

**Evidence kind: call counts and structural observables only, never wall
clock.** A timing assertion would be flaky on shared CI hardware and would
measure the machine rather than the algorithm; the defect is a *count* defect -
N whole-project parses where 1 is needed - so the count is the honest and
deterministic proof. Every failure message prints the observed count, so the
pre-fix failure is itself the baseline measurement.

Synthetic and ROM-free: the fake `ActorSprites` facade and the real
`GraphicsTab` come from `tests/unit/test_workbench_graphics`, and the project is
a real on-disk project written by the real `write_project`, so the SDK
read/write path under test is the production one.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtGui import QColor  # noqa: E402

from tools.webfoot import graphics as graphics_sdk  # noqa: E402
from tools.webfoot.graphics import (  # noqa: E402
    ActorSprites,
    Graphic,
    GraphicIdentity,
    GraphicsError,
)
from tools.webfoot.project import ProjectMeta, write_project  # noqa: E402
from tools.webfoot.workbench import graphics_tab as gt  # noqa: E402
from tools.webfoot.workbench.graphics_tab import GraphicsTab  # noqa: E402

# Reuse the L2 fake facade + session helper, so the two cannot drift.
from tests.unit.test_workbench_graphics import (  # noqa: E402,F401
    _PROFILE,
    _session_with_sprites,
    qapp,
)


# --- fixtures + helpers -------------------------------------------------------


@pytest.fixture
def project(tmp_path) -> Path:
    meta = ProjectMeta(1, _PROFILE, "Fake Game", "0" * 64, 1024, "palette-cost-test")
    write_project(tmp_path, meta, enemies=[], characters=[])
    return tmp_path


def _fresh_project(root: Path, name: str) -> Path:
    meta = ProjectMeta(1, _PROFILE, "Fake Game", "0" * 64, 1024, name)
    directory = root / name
    write_project(directory, meta, enemies=[], characters=[])
    return directory


def _profile():
    return type("P", (), {"id": _PROFILE})()


def _tab(project=None) -> GraphicsTab:
    tab = GraphicsTab(_session_with_sprites(project))
    tab.on_session_changed()
    return tab


def _auto_yes(monkeypatch) -> None:
    monkeypatch.setattr(
        gt.QMessageBox,
        "question",
        staticmethod(lambda *a, **k: gt.QMessageBox.StandardButton.Yes),
    )


@pytest.fixture
def overrides_calls(monkeypatch) -> list[int]:
    """Count `graphics_sdk.get_palette_overrides` calls, still calling the real one."""
    calls: list[int] = []
    real = graphics_sdk.get_palette_overrides

    def spy(project_dir, profile):
        calls.append(1)
        return real(project_dir, profile)

    monkeypatch.setattr(graphics_sdk, "get_palette_overrides", spy)
    return calls


@pytest.fixture
def parse_calls(monkeypatch) -> list[Path]:
    """Count whole-project parses.

    `tools/webfoot/graphics.py::_load_compatible_project` imports `read_project`
    from the package inside the function, so patching the package attribute is
    what the production call actually resolves.
    """
    import tools.webfoot.project as project_module

    calls: list[Path] = []
    real = project_module.read_project

    def spy(directory):
        calls.append(Path(directory))
        return real(directory)

    monkeypatch.setattr(project_module, "read_project", spy)
    return calls


def _swatch_rgb(swatch) -> tuple[int, int, int]:
    """The colour a swatch displays, read back from its tooltip.

    The tooltip is the swatch's own honest statement of the index and the
    displayed colour (`_palette_swatch`), so this asserts on what the widget
    says rather than on a style-sheet string format.
    """
    for line in swatch.toolTip().split("\n"):
        if line.startswith("#") and len(line) == 7:
            return (int(line[1:3], 16), int(line[3:5], 16), int(line[5:7], 16))
    raise AssertionError(f"swatch tooltip carries no colour: {swatch.toolTip()!r}")


def _spy_repaints(tab: GraphicsTab) -> dict[str, int]:
    """Count `_populate_grid` / `_populate_palette` calls on this instance."""
    calls = {"grid": 0, "palette": 0}
    real_grid = tab._populate_grid
    real_palette = tab._populate_palette

    def grid():
        calls["grid"] += 1
        real_grid()

    def palette(*args, **kwargs):
        calls["palette"] += 1
        real_palette(*args, **kwargs)

    tab._populate_grid = grid
    tab._populate_palette = palette
    return calls


def _reset_repaints(calls: dict[str, int]) -> None:
    calls["grid"] = 0
    calls["palette"] = 0


# --- 1. one repaint, one project read ----------------------------------------


def test_one_full_palette_repaint_reads_the_project_once(qapp, project, overrides_calls):
    tab = _tab(project)
    # A committed override that the repaint must both read and display.
    graphics_sdk.set_palette_override(project, _profile(), 40, 10, 20, 30)
    del overrides_calls[:]

    tab._populate_palette()

    assert len(overrides_calls) == 1, (
        "one 256-swatch repaint must read the committed override map ONCE, not "
        "once per swatch; observed "
        f"{len(overrides_calls)} get_palette_overrides call(s) "
        "(pre-fix baseline for one unscoped repaint: 257)"
    )
    # Control: the palette really was painted, from the EFFECTIVE colours.
    assert len(tab._swatches) == 256
    canonical = tab._session.sprites.palette.rgb
    assert _swatch_rgb(tab._swatches[0]) == tuple(canonical[0])
    assert _swatch_rgb(tab._swatches[5]) == tuple(canonical[5])
    assert _swatch_rgb(tab._swatches[255]) == tuple(canonical[255])
    assert _swatch_rgb(tab._swatches[40]) == (10, 20, 30), (
        "the committed override must be the colour the swatch shows"
    )
    assert "Palette index 40" in tab._swatches[40].toolTip()


# --- 2. the single read still yields correct effective + pending colours ------


def test_a_palette_recolour_superimposes_pending_on_the_effective_colour_once_per_repaint_extra(
    qapp, project, overrides_calls
):
    tab = _tab(project)
    graphics_sdk.set_palette_override(project, _profile(), 40, 10, 20, 30)
    tab._palette_pending[41] = (99, 88, 77)
    del overrides_calls[:]

    tab._populate_palette()

    assert len(overrides_calls) == 1, (
        "a pending recolour must not add a project read per swatch; observed "
        f"{len(overrides_calls)} get_palette_overrides call(s) "
        "(pre-fix baseline for one unscoped repaint: 257)"
    )
    assert _swatch_rgb(tab._swatches[40]) == (10, 20, 30), (
        "index 40 carries a COMMITTED override and no pending edit"
    )
    assert _swatch_rgb(tab._swatches[41]) == (99, 88, 77), (
        "index 41 carries a PENDING edit, previewed on top of the effective colour"
    )

    # ...and a pending edit on a committed index wins over the committed colour.
    tab._palette_pending[40] = (1, 2, 3)
    tab._populate_palette()
    assert _swatch_rgb(tab._swatches[40]) == (1, 2, 3)
    assert _swatch_rgb(tab._swatches[41]) == (99, 88, 77)


# --- 3. one logical edit, one repaint (Apply / Undo / Redo) ------------------


def test_a_logical_edit_repaints_the_grid_and_palette_once(qapp, project, monkeypatch):
    _auto_yes(monkeypatch)
    tab = _tab(project)
    # The shell's real wiring: `app.py:166` + `app.py:249` connect this tab's
    # `projectChanged` to this tab's own `on_project_mutated`, so one logical
    # edit re-enters the tab that emitted it.
    tab.projectChanged.connect(tab.on_project_mutated)
    calls = _spy_repaints(tab)
    tab._grid.setCurrentRow(0)  # a sprite is selected: the selection participates
    # Scope unchecked: the whole shared palette is on screen, which is the shape
    # the audit measured (256 swatches in every repaint).
    tab._scope_used.setChecked(False)
    _reset_repaints(calls)

    tab._palette_pending.update(
        {1: (1, 1, 1), 2: (2, 2, 2), 3: (3, 3, 3), 40: (40, 40, 40)}
    )
    tab._on_apply()
    assert (calls["grid"], calls["palette"]) == (1, 1), (
        "one Apply is ONE repaint; observed "
        f"_populate_grid={calls['grid']} _populate_palette={calls['palette']} "
        "(pre-fix baseline: 2 and 4)"
    )

    _reset_repaints(calls)
    tab._undo_stack.undo()
    assert (calls["grid"], calls["palette"]) == (1, 1), (
        "one Undo is ONE repaint; observed "
        f"_populate_grid={calls['grid']} _populate_palette={calls['palette']} "
        "(pre-fix baseline: 2 and 4)"
    )

    _reset_repaints(calls)
    tab._undo_stack.redo()
    assert (calls["grid"], calls["palette"]) == (1, 1), (
        "one Redo is ONE repaint; observed "
        f"_populate_grid={calls['grid']} _populate_palette={calls['palette']} "
        "(pre-fix baseline: 2 and 4)"
    )


# --- 4. the load-bearing structural claim: no per-element full-project work --


def test_the_project_parse_count_per_logical_edit_does_not_grow_with_pending_count(
    qapp, tmp_path, monkeypatch, parse_calls
):
    _auto_yes(monkeypatch)

    def parses_for_one_apply(pending_count: int, name: str) -> int:
        directory = _fresh_project(tmp_path, name)
        tab = _tab(directory)
        tab.projectChanged.connect(tab.on_project_mutated)  # the shell's re-entry
        tab._grid.setCurrentRow(0)
        # Scope unchecked, as the audit measured it: 256 swatches per repaint.
        tab._scope_used.setChecked(False)
        for index in range(pending_count):
            tab._palette_pending[index] = (1, 2, 3)
        del parse_calls[:]
        tab._on_apply()
        return len(parse_calls)

    one = parses_for_one_apply(1, "one_pending")
    eight = parses_for_one_apply(8, "eight_pending")

    assert one == eight, (
        "the whole-project parse count of one logical edit must not depend on how "
        f"many palette indices are staged in it; observed {one} parse(s) for 1 "
        f"pending colour and {eight} for 8 "
        "(pre-fix baseline: 1040 parses for 4 pending colours, i.e. it scaled "
        "with the pending count)"
    )
    assert one <= 4, (
        "one logical edit must cost a bounded, element-independent number of "
        f"whole-project parses; observed {one} (pre-fix baseline: 1040 for 4 "
        "pending colours)"
    )


# --- 5. the SDK half: one corpus inverse for the whole palette ---------------


def _corpus_sprites(profile_id: str = "corpus_profile_0001"):
    """An `ActorSprites` stand-in with real `Graphic` values, built via `__new__`.

    `tests/unit/test_graphics_cli.py:81` already establishes this precedent for a
    test that must exercise a real `ActorSprites` method without a ROM. The
    corpus here is three graphics in ascending identity order, one of which
    references palette index 0 (which must still be reported).
    """
    graphics = (
        _corpus_graphic(profile_id, 0, [0, 1, 1, 2, 40, 200]),
        _corpus_graphic(profile_id, 1, [40, 40, 7]),
        _corpus_graphic(profile_id, 2, [255, 3]),
    )
    sprites = ActorSprites.__new__(ActorSprites)
    sprites._graphics = {graphic.identity: graphic for graphic in graphics}
    return sprites, graphics


def _corpus_graphic(profile_id: str, index: int, pixels: list[int]) -> Graphic:
    return Graphic(
        identity=GraphicIdentity(profile_id, index),
        file_offset=0x1000 + index * 0x40,
        width=4,
        height=4,
        colour_256=False,
        pixels=bytes(pixels),
        packed_size=len(pixels) // 2,
        consumers=(),
        characters=(),
    )


def _count_graphics_calls(sprites) -> list[int]:
    calls: list[int] = []
    original = sprites.graphics

    def counted():
        calls.append(1)
        return original()

    sprites.graphics = counted
    return calls


def test_pending_consumer_disclosure_walks_the_corpus_once_for_all_256_indices():
    sprites, graphics = _corpus_sprites()
    calls = _count_graphics_calls(sprites)

    # The pre-fix definition, computed independently here: each index maps to the
    # identities (ascending identity order) whose pixels reference it.
    expected = {
        index: tuple(g.identity for g in graphics if bytes((index,)) in g.pixels)
        for index in range(256)
    }

    for index in range(256):
        assert sprites.palette_users(index) == expected[index], (
            f"palette_users({index}) disagrees with the independent scan"
        )

    assert expected[0] == (graphics[0].identity,), "index 0 is referenced and reported"
    assert expected[128] == (), "an index no graphic references yields ()"
    assert len(calls) == 1, (
        "disclosing consumers for all 256 palette indices must read the corpus "
        f"ONCE; corpus enumeration observed {len(calls)} time(s) "
        "(pre-fix baseline: 256, one full rescan per index)"
    )


def test_palette_users_still_validates_the_index_before_any_corpus_read():
    sprites, _graphics = _corpus_sprites()
    calls = _count_graphics_calls(sprites)

    for bad in (256, -1, "40"):
        with pytest.raises(GraphicsError, match=r"outside 0\.\.255"):
            sprites.palette_users(bad)

    assert calls == [], (
        "index validation must reject before any corpus traversal; observed "
        f"{len(calls)} corpus enumeration(s) on the refusal path"
    )
    # The valid path still answers, and only then reads the corpus.
    assert sprites.palette_users(40) == (
        GraphicIdentity("corpus_profile_0001", 0),
        GraphicIdentity("corpus_profile_0001", 1),
    )
    assert len(calls) == 1


# --- 6. correctness / state controls (pass both before and after) ------------


def test_project_mutation_still_preserves_pending_palette_colours(qapp, project):
    """CQA-05's guarantee on this tab: an unrelated mutation keeps staged colours."""
    tab = _tab(project)
    tab._palette_pending[7] = (10, 20, 30)

    tab.on_project_mutated()

    assert tab._palette_pending == {7: (10, 20, 30)}, (
        "a project mutation elsewhere must not discard staged palette colours"
    )


def test_session_change_still_clears_pending_palette_colours(qapp, project):
    """...and a session change is the event that legitimately drops them."""
    tab = _tab(project)
    tab._palette_pending[7] = (10, 20, 30)

    tab.on_session_changed()

    assert tab._palette_pending == {}, "a different image's palette drops them"


def test_apply_commits_exactly_the_pending_overrides_and_undo_reverses_them(
    qapp, project, monkeypatch
):
    """A batch with one authored index and one unauthored, in one gesture."""
    _auto_yes(monkeypatch)
    tab = _tab(project)
    profile = _profile()
    graphics_sdk.set_palette_override(project, _profile(), 40, 1, 2, 3)
    assert graphics_sdk.get_palette_override(project, _profile(), 41) is None

    tab._palette_pending[40] = (10, 20, 30)
    tab._palette_pending[41] = (200, 100, 50)
    tab._on_apply()

    assert graphics_sdk.get_palette_override(project, profile, 40) == (10, 20, 30)
    assert graphics_sdk.get_palette_override(project, profile, 41) == (200, 100, 50)
    assert graphics_sdk.get_palette_overrides(project, profile) == {
        40: (10, 20, 30),
        41: (200, 100, 50),
    }, "the batch touched exactly the staged indices and nothing else"

    tab._undo_stack.undo()
    # Index 40 had a prior override -> undo restores THAT. Index 41 had none ->
    # undo REMOVES it. Both in one command.
    assert graphics_sdk.get_palette_override(project, profile, 40) == (1, 2, 3)
    assert graphics_sdk.get_palette_override(project, profile, 41) is None
    assert graphics_sdk.get_palette_overrides(project, profile) == {40: (1, 2, 3)}

    tab._undo_stack.redo()
    assert graphics_sdk.get_palette_override(project, profile, 40) == (10, 20, 30)
    assert graphics_sdk.get_palette_override(project, profile, 41) == (200, 100, 50)


def test_apply_then_undo_then_redo_keeps_effective_colours_in_step(
    qapp, project, monkeypatch
):
    _auto_yes(monkeypatch)
    tab = _tab(project)
    canonical = tab._session.sprites.palette.rgb

    tab._palette_pending[40] = (10, 20, 30)
    tab._on_apply()
    assert tab._effective_rgb(tab._session.sprites)[40] == (10, 20, 30)
    assert _swatch_rgb(tab._swatches[40]) == (10, 20, 30)

    tab._undo_stack.undo()
    assert tab._effective_rgb(tab._session.sprites)[40] == tuple(canonical[40])
    assert _swatch_rgb(tab._swatches[40]) == tuple(canonical[40])

    tab._undo_stack.redo()
    assert tab._effective_rgb(tab._session.sprites)[40] == (10, 20, 30)
    assert _swatch_rgb(tab._swatches[40]) == (10, 20, 30)


def test_apply_still_emits_project_changed_once_and_bumps_the_revision_once(
    qapp, project, monkeypatch
):
    """Mirrors `test_workbench_graphics_undo::test_undo_redo_bump_revision_and_emit`.

    No shell is attached here, so this pins the standalone shape: exactly one
    emission and one revision bump per Apply, per Undo and per Redo.
    """
    _auto_yes(monkeypatch)
    tab = _tab(project)
    emitted: list[bool] = []
    tab.projectChanged.connect(lambda: emitted.append(True))
    r0 = tab._session.project_revision

    tab._palette_pending[40] = (10, 20, 30)
    tab._on_apply()
    assert len(emitted) == 1
    assert tab._session.project_revision == r0 + 1

    tab._undo_stack.undo()
    assert len(emitted) == 2
    assert tab._session.project_revision == r0 + 2

    tab._undo_stack.redo()
    assert len(emitted) == 3
    assert tab._session.project_revision == r0 + 3


def test_applying_the_pending_palette_clears_the_session_unsaved_count(
    qapp, project, monkeypatch
):
    """N-04: the staged count follows the pending set, in and out."""
    _auto_yes(monkeypatch)
    tab = _tab(project)
    tab._palette_pending[40] = (10, 20, 30)
    tab._refresh_pending_ui()
    assert tab._session.unsaved_edit_count() == 1

    tab._on_apply()

    assert tab._palette_pending == {}
    assert tab._session.unsaved_edit_count() == 0


def test_a_project_switch_repaints_the_discarded_colour_out(
    qapp, project, tmp_path
):
    """N-04: a dropped pending colour must not stay painted on the grid."""
    tab = _tab(project)
    canonical = tuple(tab._session.sprites.palette.rgb[40])
    tab._palette_pending[40] = (10, 20, 30)
    tab._populate_palette()
    assert _swatch_rgb(tab._swatches[40]) == (10, 20, 30)

    other = _fresh_project(tmp_path, "palette-cost-other")
    tab._retire_history_on_project_change(other)

    assert tab._palette_pending == {}
    assert _swatch_rgb(tab._swatches[40]) == canonical


# --- 7. the two remaining per-UI-element project reads -----------------------


def test_one_colour_pick_reads_the_project_once(
    qapp, project, overrides_calls, monkeypatch
):
    tab = _tab(project)
    monkeypatch.setattr(
        gt.QColorDialog,
        "getColor",
        staticmethod(lambda *a, **k: QColor(1, 2, 3)),
    )
    del overrides_calls[:]

    tab._pick_colour(40)

    assert len(overrides_calls) == 1, (
        "one swatch click must read the project ONCE; observed "
        f"{len(overrides_calls)} get_palette_overrides call(s) "
        "(pre-fix baseline: 3 - the dialog's current colour, the detail line and "
        "the pending 'from' colour each re-read it)"
    )
    assert tab._palette_pending[40] == (1, 2, 3), "the picked colour is staged"
    assert "Palette color 40" in tab._pending_label.text(), (
        "the disclosure line still names the staged index"
    )
    assert "#010203" in tab._pending_label.text()


def test_selecting_a_sprite_reads_the_project_once(qapp, project, overrides_calls):
    tab = _tab(project)
    del overrides_calls[:]

    tab._show_selected(GraphicIdentity(_PROFILE, 0))

    assert len(overrides_calls) == 1, (
        "selecting a sprite must read the project ONCE; observed "
        f"{len(overrides_calls)} get_palette_overrides call(s). Pre-fix this call "
        "re-read the project for the selection, again for the preview render, and "
        "then once per swatch in the palette repaint it triggers"
    )
    assert tab._selected == GraphicIdentity(_PROFILE, 0)
    assert not tab._preview.pixmap().isNull()


# --- 8. the audit's literal claim: ONE `_effective_rgb` per repaint ----------


def test_one_effective_palette_read_per_repaint(qapp, project, monkeypatch):
    """Pin the audit's own remediation wording: one `_effective_rgb` per repaint.

    The finding is that the palette editor did whole-project work per UI element;
    its remediation is to hand the already-computed `rgb` map to the swatch
    factory, "one `_effective_rgb` per repaint instead of 257". The tests above
    count `get_palette_overrides`; this one counts calls to the tab's OWN helper,
    which is the literal claim, so both are kept.

    The repaint path is exercised in its worst case: a real on-disk project, a
    sprite selected (so `_show_selected` participates) and staged pending colours
    present at entry (so `_refresh_pending_ui` participates). All three caller
    shapes go through `_repaint_project_state`, the ONE repaint path.
    """
    tab = _tab(project)
    tab._grid.setCurrentRow(0)  # a sprite is selected: the selection participates
    # Scope unchecked: the whole shared palette is on screen, 256 swatches per
    # repaint, which is the shape the audit measured.
    tab._scope_used.setChecked(False)

    calls: list[int] = []
    real_effective = tab._effective_rgb

    def counted(sprites):
        calls.append(1)
        return real_effective(sprites)

    monkeypatch.setattr(tab, "_effective_rgb", counted)

    for clear_pending, keep_selection, shape in (
        (False, True, "a project mutation"),
        (True, True, "an Apply / Undo / Redo"),
        (True, False, "a session change"),
    ):
        # Re-stage before every shape, so each repaint starts from the worst case:
        # a selection plus staged colours on the pending-disclosure surface.
        tab._palette_pending.update({1: (1, 1, 1), 40: (40, 40, 40)})
        del calls[:]
        tab._repaint_project_state(
            clear_pending=clear_pending, keep_selection=keep_selection
        )
        assert len(calls) == 1, (
            f"one repaint ({shape}) must compute the effective palette ONCE - the "
            "audit's claim is one `_effective_rgb` per repaint instead of 257; "
            f"observed {len(calls)} `_effective_rgb` call(s) for "
            f"_repaint_project_state(clear_pending={clear_pending}, "
            f"keep_selection={keep_selection})"
        )


# --- 9. the batch write authority is total over its declared type ------------


def test_set_palette_overrides_rejects_a_malformed_entry_as_a_graphics_error(
    project,
):
    """A malformed batch entry is a `GraphicsError`, never a `TypeError`.

    The batch is the ONE palette write authority and its declared entry type is
    an RGB triple or `None`. A 2-tuple, a 4-tuple or a non-sequence used to raise
    `TypeError` out of argument unpacking - outside the SDK error family a GUI
    slot catches at its boundary, which is this project's documented most
    expensive Workbench failure mode: an escaping sibling reaches stderr and the
    click looks dead. Like the SDK-half tests above, this sits here because the
    two Workbench palette files are the ones this ticket owns.
    """
    profile = _profile()

    for malformed in ((1, 2), (1, 2, 3, 4), 7, "1,2,3", {1: 2, 3: 4}):
        with pytest.raises(GraphicsError) as caught:
            graphics_sdk.set_palette_overrides(
                project, profile, {40: malformed, 41: (4, 5, 6)}
            )
        assert "palette entry 40" in str(caught.value), (
            "the refusal must name the offending index; got "
            f"{str(caught.value)!r} for {malformed!r}"
        )
        assert repr(malformed) in str(caught.value), (
            "the refusal must name the offending value; got "
            f"{str(caught.value)!r} for {malformed!r}"
        )

    assert graphics_sdk.get_palette_overrides(project, profile) == {}, (
        "a batch carrying one malformed entry must write NOTHING - not even the "
        "well-formed siblings it was carrying"
    )
    # The well-formed shape still works, unchanged.
    assert graphics_sdk.set_palette_overrides(project, profile, {40: (1, 2, 3)}) is True
    assert graphics_sdk.get_palette_override(project, profile, 40) == (1, 2, 3)
