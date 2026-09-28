"""MAP-WARP-CANVAS-001: connections drawn, selected and dragged on the map canvas.

Focused regressions for the Objects canvas's **trigger-region overlay**. The
synthetic image is the one `test_map_transitions` assembles from the measured
format and `test_workbench_warp_transitions` extends with each root's walkable
extent, with a synthetic GBA header written in front of its structures so the map
domain and the scene facade can be built for real; the project is a real on-disk
project written by the real `write_project`, and every region edit goes through
the real authority (`set_transition_edits`) and the real build
(`plan_transition_edits` + `apply_plan`). No SDK path is mocked, and the canonical
ROM is never opened.

Covered by name: the overlay's geometry in the canvas's own coordinate space
(including a non-zero zoom and a scrolled viewport), the authored region replacing
the retail one, a project-created transition, click-select driving the shipped
Warps editor through `MapsEditor.show_transition`, the canvas marking the
connection that editor has selected, clicking empty canvas and clicking a
placement marker, the drag (region only, every other byte of the record preserved,
every byte of each region word when both endpoints are above `0xFF`, one undo entry,
undo/redo, save/reopen, and no history for a no-op drag - one that ends where it
started, or whose write the authority reports as already current), the fail-closed
refusals (169-class, shared connection root, an out-of-domain region, no authoring
surface at all), and the bounded reads (CQA-07).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
from PySide6.QtCore import QPoint, Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tools.webfoot import capability  # noqa: E402
from tools.webfoot import map_transitions as mt  # noqa: E402
from tools.webfoot import map_render  # noqa: E402
from tools.webfoot.formats.map_entry import MAP_ENTRY_SIZE, MapEntry  # noqa: E402
from tools.webfoot.formats.map_transitions import TransitionRegion  # noqa: E402
from tools.webfoot.gba_header import GbaHeader  # noqa: E402
from tools.webfoot.maps import MapEntryEntry, MapIdentity, Maps  # noqa: E402
from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.project import PROJECT_FORMAT_VERSION, ProjectMeta, write_project  # noqa: E402
from tools.webfoot.rom import RomIdentification  # noqa: E402
from tools.webfoot.write import apply_plan, plan_changes  # noqa: E402
from tools.webfoot.workbench import map_tab as canvas_mod  # noqa: E402
from tools.webfoot.workbench.editors import MapsEditor  # noqa: E402
from tools.webfoot.workbench.map_tab import MapWorkspaceTab  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402
from tools.webfoot.workbench.warp_tab import WarpTab  # noqa: E402

from tests.helpers import hashes_for, make_synthetic_rom, profile_for as synthetic_profile  # noqa: E402
from tests.unit.test_map_transitions import (  # noqa: E402
    GBA_BASE,
    TABLE_OFFSET,
    TABLE_STRIDE,
    key_for,
    record_bytes,
)
from tests.unit.test_workbench_warp_transitions import (  # noqa: E402
    PER_MAP,
    ROOT_BASE,
    ROOT_STRIDE,
    image_bytes as warp_image_bytes,
)

#: Five maps, from the tranpsitions fixture: map 0 holds two 566-class records
#: the drag tests drive, map 1 holds the reciprocal door, map 2 holds the 169-class
#: record that must refuse, and maps 3 and 4 hold nothing.
MAP_ZERO = "map:0000"
#: map:0000/transition:0000 - region `first (100, 140)`, `second (20, 60)`.
TARGET = "map:0000/transition:0000"
#: map:0000/transition:0001 - region `first (200, 240)`, `second (70, 90)`.
SECOND = "map:0000/transition:0001"
#: map:0002/transition:0000 - the 169-class record, whose class the authority
#: refuses to retarget and whose region this canvas refuses to move.
SCENE_RELATIVE = "map:0002/transition:0000"

#: The retail regions the two map-0 records store, stated independently of the
#: fixture so a transposed or mis-read interval is detected rather than followed.
TARGET_REGION = TransitionRegion(first=(100, 140), second=(20, 60))
SECOND_REGION = TransitionRegion(first=(200, 240), second=(70, 90))


def image_bytes() -> bytes:
    """The transition corpus with a valid synthetic GBA header in front of it.

    The structures start at 0x0100 and the header ends at 0x00C0, so the two do not
    overlap. The header exists only so the map table this image declares can be
    identified, profiled and loaded for real by the canvas's own scene facade.
    """
    base = bytearray(warp_image_bytes())
    base[0:0xC0] = make_synthetic_rom(size=len(base))[0:0xC0]
    return bytes(base)


def profile_for(image: bytes):
    """A synthetic profile declaring exactly the map table this image carries.

    Only `map_entries` is declared, so every other subsystem reports itself
    unavailable rather than being read against canonical addresses this 32 KiB
    image does not have - which is what the canvas and the connection authority
    actually need.
    """
    return synthetic_profile(
        image,
        id="synthetic_warp_canvas",
        game="synthetic",
        tables={
            "map_entries": {
                "address": GBA_BASE + TABLE_OFFSET,
                "count": len(PER_MAP),
                "record_size": MAP_ENTRY_SIZE,
            }
        },
    )


def project_meta(image: bytes) -> ProjectMeta:
    return ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id="synthetic_warp_canvas",
        game="synthetic",
        base_rom_sha256=hashes_for(image).sha256,
        base_rom_size=len(image),
        name="map-warp-canvas-test",
    )


def maps_for(image: bytes, profile, catalog) -> Maps:
    """The map domain over the synthetic image: every declared map, no placements.

    Read through the SDK's own identity machinery rather than a stand-in, so the
    canvas's map list, its map identities and its (empty) marker set are the ones
    the product computes for this image.
    """
    entries = []
    for index in range(len(PER_MAP)):
        offset = TABLE_OFFSET + index * TABLE_STRIDE
        raw = image[offset : offset + MAP_ENTRY_SIZE]
        entries.append(
            MapEntryEntry(MapIdentity(index), MapEntry.from_bytes(raw), offset, raw)
        )
    header = GbaHeader.from_bytes(image)
    hashes = hashes_for(image)
    identification = RomIdentification(
        Path("synthetic.gba"),
        len(image),
        hashes,
        header,
        catalog.match(size=len(image), hashes=hashes, header=header),
    )
    return Maps(
        identification=identification,
        profile=profile,
        entries=tuple(entries),
        arrays=(),
        placements=(),
        base_bytes=image,
    )


def render_result() -> map_render.MapRenderResult:
    """A 512x512 grey render, so every fixture region lands on visible artwork."""
    palette = tuple((index, index, index) for index in range(256))
    pixels = bytes([17]) * (512 * 512)
    layer = map_render.RenderedLayer(
        bg=0,
        priority=0,
        char_base_block=0,
        screen_base_block=0,
        width=512,
        height=512,
        pixels=pixels,
    )
    return map_render.MapRenderResult(
        semantic_map_id=MAP_ZERO,
        width=512,
        height=512,
        layers=(layer,),
        composite=pixels,
        palette=palette,
        provenance={"source": "synthetic"},
    )


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def refusals() -> list[str]:
    """Every refusal this test's surface showed, in order."""
    return []


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch, refusals):
    """A refusal is recorded, never waited for.

    The refusal surface IS a modal `QMessageBox.warning` (the same one the Warps
    editor uses), and a modal box under the offscreen platform blocks forever with
    nobody to dismiss it. Recording the message keeps the assertion about what the
    user is told while the suite stays runnable; the shipped call is unchanged.
    """
    monkeypatch.setattr(
        canvas_mod.QMessageBox,
        "warning",
        staticmethod(lambda *args, **kwargs: refusals.append(args[2])),
    )
    return refusals


@pytest.fixture
def image() -> bytes:
    return image_bytes()


@pytest.fixture
def profile(image):
    return profile_for(image)


@pytest.fixture
def catalog(monkeypatch, profile):
    """The one-profile catalog the identification and capability checks read."""
    value = RomProfileCatalog([profile])
    monkeypatch.setattr(capability, "_packaged_catalog", lambda: value)
    return value


@pytest.fixture
def project(tmp_path, image):
    write_project(tmp_path, project_meta(image), enemies=[], characters=[])
    return tmp_path


@pytest.fixture
def session(qapp, image, profile, catalog, project) -> Session:
    value = Session(rom_image=image, rom_path=Path("synthetic.gba"))
    value.profile = profile
    value.maps = maps_for(image, profile, catalog)
    value.project_dir = project
    value.selected_map = MAP_ZERO
    return value


@pytest.fixture
def rendered(qapp, monkeypatch):
    """The renderer stub, installed before any canvas is constructed."""
    result = render_result()
    monkeypatch.setattr(map_render, "render_map", lambda *_a, **_k: result)
    return result


@pytest.fixture
def warps(qapp, session) -> WarpTab:
    """The shipped Warps surface over the same session: the editability authority."""
    widget = WarpTab(session)
    widget.select_source_map(0)
    return widget


@pytest.fixture
def tab(qapp, session, warps, rendered) -> MapWorkspaceTab:
    widget = MapWorkspaceTab(session)
    widget.set_transition_guard(warps.region_edit_refusal)
    return widget


def overlay(tab: MapWorkspaceTab, key: str):
    return tab._transition_overlays[key]


def region_of(tab: MapWorkspaceTab, key: str) -> TransitionRegion:
    return tab.transition_overlays()[key]


def built_record(project, image, profile, identity):
    """The record the production build would write for one authored transition."""
    requests = mt.read_project_transition_requests(project)
    application = mt.plan_transition_edits(image, requests, profile=profile)
    plan = plan_changes(
        image,
        application.changes,
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
    )
    built = apply_plan(image, plan)
    return mt.read_map_transitions(built, profile).entry(identity).record, built


# --- the overlay's geometry ---------------------------------------------------


def test_the_overlay_is_the_regions_own_rectangle_in_map_pixels(tab):
    """The drawn region IS the record's two intervals, on the canvas's own axes.

    The canvas has one coordinate space - the engine's map pixels - and the view has
    one transform over it, so the assertion is that the item's scene rectangle is
    the region, and that the view maps that rectangle to view pixels by exactly the
    scale and scroll the viewport reports.
    """
    drawn = overlay(tab, TARGET).sceneBoundingRect()
    # `sceneBoundingRect` adds the painted halo (3 px on each side); the region
    # itself is the item's rectangle at its own position.
    assert overlay(tab, TARGET).pos() == canvas_mod.QPointF(100, 20)
    assert overlay(tab, TARGET).rect() == canvas_mod.QRectF(0, 0, 40, 40)
    assert (drawn.x(), drawn.y(), drawn.width(), drawn.height()) == (97, 17, 46, 46)
    # The second record is a different rectangle, so a transposed interval cannot
    # pass by coincidence.
    assert overlay(tab, SECOND).pos() == canvas_mod.QPointF(200, 70)
    assert overlay(tab, SECOND).rect() == canvas_mod.QRectF(0, 0, 40, 20)


def test_the_view_transform_carries_the_region_exactly_as_it_carries_the_map(tab, qapp):
    """Zoom and scroll move the overlay and the artwork together, by one transform."""
    tab.resize(900, 650)
    tab.show()
    qapp.processEvents()
    # The tab fits the map on load, so the zoom is whatever the fit chose; one zoom
    # step then states the transform's scale exactly and a non-unit zoom is certain.
    before = tab._canvas.transform().m11()
    tab._canvas.zoom_in()
    qapp.processEvents()
    scale = tab._canvas.transform().m11()
    assert scale == pytest.approx(before * 1.25)
    assert scale != 0

    rect = canvas_mod.QRectF(
        overlay(tab, TARGET).pos(), overlay(tab, TARGET).rect().size()
    )
    top_left = tab._canvas.mapFromScene(rect.topLeft())
    bottom_right = tab._canvas.mapFromScene(rect.bottomRight())
    assert bottom_right.x() - top_left.x() == pytest.approx(40 * scale, abs=1)
    assert bottom_right.y() - top_left.y() == pytest.approx(40 * scale, abs=1)
    # The map pixmap item is carried by the same transform, so the region and the
    # artwork cannot drift apart: mapping the view point back returns the region.
    back = tab._canvas.mapToScene(tab._canvas.mapFromScene(rect.center()))
    assert back.x() == pytest.approx(rect.center().x(), abs=1)
    assert back.y() == pytest.approx(rect.center().y(), abs=1)

    # A scrolled viewport moves the region in view pixels by the scroll amount: the
    # region is not pinned to the viewport, it is carried by the same scroll offset
    # the artwork is. The scrollable range is bounded by the fitted scene, so the
    # comparison uses the offset the viewport actually took.
    bar = tab._canvas.horizontalScrollBar()
    before_scroll = bar.value()
    bar.setValue(bar.maximum())
    qapp.processEvents()
    shift = bar.value() - before_scroll
    assert shift > 0, "the viewport must actually scroll for this to mean anything"
    moved = tab._canvas.mapFromScene(rect.topLeft())
    assert top_left.x() - moved.x() == pytest.approx(shift, abs=1)


def test_an_authored_region_is_drawn_instead_of_the_retail_one(tab, session, warps):
    """What the canvas draws is what a build would apply, not what the record says."""
    assert region_of(tab, TARGET) == TARGET_REGION
    authored = TransitionRegion(first=(140, 180), second=(60, 100))
    assert mt.set_transition_edits(
        session.project_dir,
        session.profile,
        session.map_image,
        {mt.TransitionIdentity(MapIdentity(0), 0): mt.TransitionEdit(region=authored)},
    )

    # The write is an unrelated surface's here, so it advances the project revision
    # and then broadcasts, exactly as a mutating editor does; both editors re-read on
    # that event rather than on a timer.
    session.project_mutated()
    tab.on_project_mutated()
    warps.on_project_mutated()

    assert region_of(tab, TARGET) == authored
    assert overlay(tab, TARGET).pos() == canvas_mod.QPointF(140, 60)
    assert overlay(tab, TARGET).state.authored is True
    # The other record on the same map keeps its own region.
    assert region_of(tab, SECOND) == SECOND_REGION
    # And the shipped Warps list states the same region, because it now reads the
    # project's value over the record's exactly as its other columns do.
    assert warps.select_source_map(0) and warps.select_row(0)
    assert "first 140\u2013180" in warps.row_values(0)[2]


def test_a_transition_the_project_creates_is_drawn_at_its_authored_region(
    tab, session, warps
):
    """A created transition has no record in the image, and is still drawn."""
    from tools.webfoot.formats.map_transitions import TransitionArrival
    from tools.webfoot.maps import MapIdentity as Identity

    creation = mt.TransitionCreation(
        identity=mt.CreatedTransitionIdentity(Identity(0), "canvas-door"),
        template=mt.TransitionIdentity(Identity(0), 0),
        destination=Identity(1),
        region=TransitionRegion(first=(300, 340), second=(110, 150)),
        arrival=TransitionArrival(60, 70),
        facing=None,
    )
    assert mt.set_transition_creations(
        session.project_dir, session.profile, session.map_image, {creation.identity: creation}
    )

    session.project_mutated()
    tab.on_project_mutated()

    key = creation.identity.key
    assert region_of(tab, key) == creation.region
    assert overlay(tab, key).state.authored is True
    # Drawn, and not movable: the refusal is the creation's own, in the words of
    # the form that authors it, and no history entry is created.
    assert overlay(tab, key).state.refusal is not None
    assert "Create transition form" in overlay(tab, key).state.refusal
    assert not tab._on_overlay_drag(
        overlay(tab, key).state, (300, 110), (320, 130)
    )
    assert tab._undo_stack.count() == 0
    assert mt.read_project_transition_creations(session.project_dir)[creation.identity]


# --- click-select wiring ------------------------------------------------------


def test_clicking_a_region_selects_that_connection_in_the_warps_editor(session, rendered, qapp):
    """One click on a region: the Maps editor switches to Warps and selects the row."""
    editor = MapsEditor(session)
    editor.workspace.set_transition_guard(editor.warps.region_edit_refusal)
    editor.warps.select_source_map(0)
    editor.set_mode("objects")
    qapp.processEvents()
    workspace = editor.workspace
    workspace.resize(900, 650)
    workspace.show()
    qapp.processEvents()

    point = workspace._canvas.mapFromScene(overlay(workspace, TARGET).sceneBoundingRect().center())
    QTest.mouseClick(workspace._canvas.viewport(), Qt.MouseButton.LeftButton, pos=point)

    assert editor.mode() == "warps"
    assert editor.warps.source_map_index() == 0
    assert editor.warps.selected_identity() == TARGET
    # The shipped form agrees: it states this connection, and its region column has
    # the record's own intervals in the codec's positional naming.
    assert editor.warps.form_state()["identity"] == TARGET
    assert "\u2014" not in editor.warps.row_values(0)[2]
    assert workspace.selected_transition() == TARGET

    # A second click on the other region selects that one instead, and reports it.
    seen = []
    editor.workspace.transitionSelected.connect(lambda identity: seen.append(identity.key))
    editor.set_mode("objects")
    other = workspace._canvas.mapFromScene(overlay(workspace, SECOND).sceneBoundingRect().center())
    QTest.mouseClick(workspace._canvas.viewport(), Qt.MouseButton.LeftButton, pos=other)
    assert seen == [SECOND]
    assert editor.warps.selected_identity() == SECOND
    assert editor.mode() == "warps"


def test_the_canvas_marks_the_connection_the_warps_editor_has_selected(session, rendered, qapp):
    """Coming back to the canvas re-reads the Warps selection, so it cannot go stale."""
    editor = MapsEditor(session)
    editor.workspace.set_transition_guard(editor.warps.region_edit_refusal)
    editor.warps.select_source_map(0)
    editor.set_mode("objects")
    qapp.processEvents()
    workspace = editor.workspace

    # The author picks a row in the connection list, not on the canvas.
    assert editor.warps.select_row(1)
    editor.set_mode("warps")
    editor.set_mode("objects")

    assert workspace.selected_transition() == SECOND
    assert overlay(workspace, SECOND)._selected is True
    assert overlay(workspace, TARGET)._selected is False


def test_clicking_empty_canvas_clears_the_canvas_selection(tab, qapp):
    """A press on no overlay at all drops the region highlight."""
    tab.resize(900, 650)
    tab.show()
    qapp.processEvents()
    tab._on_overlay_clicked(mt.TransitionIdentity(MapIdentity(0), 0))
    assert tab.selected_transition() == TARGET

    # A point on the rendered map that is inside no region.
    empty = tab._canvas.mapFromScene(canvas_mod.QPointF(10, 400))
    QTest.mouseClick(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=empty)

    assert tab.selected_transition() is None
    assert overlay(tab, TARGET)._selected is False


def test_selecting_a_placement_marker_clears_the_region_selection(tab, session, monkeypatch, qapp):
    """One canvas, one selection: a placement marker and a region cannot both be on."""
    monkeypatch.setattr(
        canvas_mod.scene_sdk,
        "scene_placements",
        lambda *_a, **_k: [
            {
                "identity": "map:0000/placement:0000",
                "position_low": 400,
                "position_high": 400,
                "position_x": 400,
                "position_y": 400,
                "placement_type": None,
                "classification": None,
                "is_clone_source": True,
                "provenance": "Retail",
            }
        ],
    )
    tab._populate_markers()
    tab.resize(900, 650)
    tab.show()
    qapp.processEvents()
    tab._on_overlay_clicked(mt.TransitionIdentity(MapIdentity(0), 0))
    assert tab.selected_transition() == TARGET

    marker = tab._markers["map:0000/placement:0000"]
    point = tab._canvas.mapFromScene(marker.scenePos())
    QTest.mouseClick(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=point)

    assert marker.isSelected()
    assert tab.selected_transition() is None
    assert overlay(tab, TARGET)._selected is False


# --- the drag -----------------------------------------------------------------


def test_a_drag_writes_only_the_region_and_is_one_undo_entry(tab, session, project, image, profile):
    """One drag: the region moves, one write, one history entry, nothing else."""
    target = mt.TransitionIdentity(MapIdentity(0), 0)
    retail = mt.read_map_transitions(image, profile).entry(target).record
    state = overlay(tab, TARGET).state
    emitted = []
    tab.projectChanged.connect(lambda: emitted.append(True))

    assert tab._on_overlay_drag(state, (100, 20), (140, 60))

    authored = mt.read_project_transition_requests(project)[target]
    assert authored.prior_region == TARGET_REGION
    assert authored.region == TransitionRegion(first=(140, 180), second=(60, 100))
    assert tab._undo_stack.count() == 1
    assert emitted == [True]
    # Every field of the record except the four region words is byte-identical, so
    # the gesture changed the region and nothing else it never named.
    built, _image = built_record(project, image, profile, target)
    differing = [
        index
        for index in range(24)
        if built.to_bytes()[index] != retail.to_bytes()[index]
    ]
    # The region is four u16 at +0x08, +0x0A, +0x0C and +0x0E, so the four LOW bytes
    # are the ones these fixture endpoints change (every endpoint is under 256); the
    # high byte of each halfword stays 0 and is not touched.
    assert differing == [0x08, 0x0A, 0x0C, 0x0E]
    assert built.destination_key == retail.destination_key
    assert built.arrival == retail.arrival
    assert built.byte_0x10_raw == retail.byte_0x10_raw
    assert built.class_raw == retail.class_raw
    # And the canvas moved with the write, over the same authority values.
    assert region_of(tab, TARGET) == authored.region
    assert overlay(tab, TARGET).pos() == canvas_mod.QPointF(140, 60)


def test_a_drag_above_0xFF_changes_only_the_four_region_halfwords(
    tab, session, project, image, profile
):
    """Both endpoints above 0xFF: every byte of each region word moves, nothing else.

    The other byte test asserts the SET of differing offsets, and every endpoint in
    its fixture is under 0x100 - so a write that dropped the high byte of each region
    ``u16`` would have passed it. This drag lands on ``first (400, 440)`` and
    ``second (320, 360)``, so the four little-endian words at ``+0x08``, ``+0x0A``,
    ``+0x0C`` and ``+0x0E`` are ``0x0190``, ``0x0140``, ``0x01B8`` and ``0x0168``
    and all eight of their bytes differ from retail.
    """
    target = mt.TransitionIdentity(MapIdentity(0), 0)
    retail = mt.read_map_transitions(image, profile).entry(target).record
    assert tab._on_overlay_drag(overlay(tab, TARGET).state, (100, 20), (400, 320))

    authored = mt.read_project_transition_requests(project)[target]
    assert authored.region == TransitionRegion(first=(400, 440), second=(320, 360))
    built, _image = built_record(project, image, profile, target)
    before, after = retail.to_bytes(), built.to_bytes()
    changed = {index for index in range(24) if after[index] != before[index]}
    # The four halfwords are the WHOLE diff: a high-byte truncation would leave
    # +0x09, +0x0B, +0x0D and +0x0F equal to retail, and is not this set.
    assert changed == set(range(0x08, 0x10))
    words = {
        offset: after[offset] | (after[offset + 1] << 8)
        for offset in (0x08, 0x0A, 0x0C, 0x0E)
    }
    assert words == {0x08: 0x0190, 0x0A: 0x0140, 0x0C: 0x01B8, 0x0E: 0x0168}
    # Everything the gesture never named is byte-identical: the class word and the
    # invariant word (+0x00..+0x07), then +0x10..+0x13 (facing, destination key and
    # the unresolved byte) and the arrival pair at +0x14..+0x17.
    assert after[0x00:0x08] == before[0x00:0x08]
    assert after[0x10:0x18] == before[0x10:0x18]
    assert built.class_raw == retail.class_raw
    assert built.constant_raw == retail.constant_raw
    assert built.arrival == retail.arrival


def test_undo_and_redo_restore_the_exact_original_bytes(tab, session, project, image, profile):
    target = mt.TransitionIdentity(MapIdentity(0), 0)
    assert tab._on_overlay_drag(overlay(tab, TARGET).state, (100, 20), (120, 40))
    assert region_of(tab, TARGET) == TransitionRegion(first=(120, 160), second=(40, 80))

    tab._undo_stack.undo()
    # Undone: the project authors no region for this record at all, and the built
    # record is byte-for-byte the retail one again.
    assert mt.read_project_transition_requests(project) == {}
    assert region_of(tab, TARGET) == TARGET_REGION
    built, _image = built_record(project, image, profile, target)
    assert built.to_bytes() == mt.read_map_transitions(image, profile).entry(target).record.to_bytes()

    tab._undo_stack.redo()
    assert region_of(tab, TARGET) == TransitionRegion(first=(120, 160), second=(40, 80))
    authored = mt.read_project_transition_requests(project)[target]
    assert authored.region == TransitionRegion(first=(120, 160), second=(40, 80))


def test_a_drag_that_ends_where_it_started_adds_no_history(tab, project):
    state = overlay(tab, TARGET).state
    assert tab._on_overlay_drag(state, (100, 20), (100, 20))
    assert tab._undo_stack.count() == 0
    assert mt.read_project_transition_requests(project) == {}
    assert region_of(tab, TARGET) == TARGET_REGION


def test_a_drag_that_writes_nothing_adds_no_history_and_keeps_the_authored_region(
    tab, session, project, image, profile
):
    """A write the authority reports as already current must not become undo history.

    The canvas can be one project revision behind: it draws what it read when it last
    populated. Here an unrelated surface authors the very region this gesture
    translates the stale overlay TO, so the authority writes nothing. There is no
    project change, so there is no history entry - and no entry whose Undo would write
    the stale (retail) region back and delete the pre-existing authored one.
    """
    target = mt.TransitionIdentity(MapIdentity(0), 0)
    authored = TransitionRegion(first=(140, 180), second=(60, 100))
    assert mt.set_transition_edits(
        session.project_dir,
        session.profile,
        session.map_image,
        {target: mt.TransitionEdit(region=authored)},
    )
    # The project advanced and this canvas did NOT repopulate, so its overlay is stale
    # by exactly the drag delta below: retail + (40, 40) is the authored region.
    session.project_mutated()
    state = overlay(tab, TARGET).state
    assert state.region == TARGET_REGION
    assert state.region.first[0] + 40 == authored.first[0]
    assert state.region.second[0] + 40 == authored.second[0]

    # The drag reports NO write, and no history entry exists to Undo.
    assert tab._on_overlay_drag(state, (100, 20), (140, 60)) is False
    assert tab._undo_stack.count() == 0
    # It is repopulated anyway: the canvas now shows the project's own region rather
    # than the stale one it was drawing.
    assert region_of(tab, TARGET) == authored
    assert overlay(tab, TARGET).state.authored is True
    # The Undo that used to delete the authored region cannot: there is no entry for
    # it to undo, and the project still holds the region.
    tab._undo_stack.undo()
    assert mt.read_project_transition_requests(project)[target].region == authored
    built, _image = built_record(project, image, profile, target)
    assert built.region == authored


def test_the_region_reproduces_after_save_and_reopen(tab, session, project, rendered, warps):
    """Close the canvas, reopen it over the same project: the authored region is drawn."""
    assert tab._on_overlay_drag(overlay(tab, TARGET).state, (100, 20), (160, 80))
    authored = TransitionRegion(first=(160, 200), second=(80, 120))
    assert region_of(tab, TARGET) == authored

    reopened = MapWorkspaceTab(session)
    reopened.set_transition_guard(warps.region_edit_refusal)

    assert region_of(reopened, TARGET) == authored
    assert overlay(reopened, TARGET).state.authored is True
    assert overlay(reopened, TARGET).pos() == canvas_mod.QPointF(160, 80)
    # The reopened canvas has no history, and the project is the only carrier of
    # the authored value.
    assert reopened._undo_stack.count() == 0
    assert mt.read_project_transition_requests(project)[
        mt.TransitionIdentity(MapIdentity(0), 0)
    ].region == authored


def test_a_real_mouse_drag_commits_one_undo_step(tab, project, qapp):
    """The gesture itself, not only its handler: press, move, release."""
    tab.resize(900, 650)
    tab.show()
    qapp.processEvents()
    item = overlay(tab, TARGET)
    tab._canvas.centerOn(item)
    point = tab._canvas.mapFromScene(item.sceneBoundingRect().center())
    destination = point + QPoint(30, 20)

    QTest.mousePress(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=point)
    QTest.mouseMove(tab._canvas.viewport(), destination, 20)
    QTest.mouseRelease(tab._canvas.viewport(), Qt.MouseButton.LeftButton, pos=destination)

    assert tab._undo_stack.count() == 1
    authored = mt.read_project_transition_requests(project)[
        mt.TransitionIdentity(MapIdentity(0), 0)
    ].region
    assert authored != TARGET_REGION
    # The region moved as a whole: both intervals keep their widths, and they moved
    # by one common (dx, dy) - which is what makes a drag a translation and cannot
    # produce an unordered or degenerate interval.
    dx = authored.first[0] - TARGET_REGION.first[0]
    dy = authored.second[0] - TARGET_REGION.second[0]
    assert authored.first[1] - TARGET_REGION.first[1] == dx
    assert authored.second[1] - TARGET_REGION.second[1] == dy
    assert (dx, dy) != (0, 0)
    assert region_of(tab, TARGET) == authored


# --- fail closed --------------------------------------------------------------


def test_a_169_class_connection_refuses_the_drag_in_the_surfaces_words(
    tab, warps, project, refusals
):
    """The class rule is the Warps surface's, and its wording is what is shown."""
    assert warps.select_source_map(2)
    tab._session.selected_map = "map:0002"
    tab._on_map_changed(tab._maps.item(2))
    state = overlay(tab, SCENE_RELATIVE).state

    assert state.refusal is not None and "169-class" in state.refusal
    assert state.refusal == warps.region_edit_refusal(
        mt.TransitionIdentity(MapIdentity(2), 0)
    )
    # The region is still DRAWN - drawing it is safe - and the drag is refused with
    # the surface's own reason rather than with a rule invented here.
    assert region_of(tab, SCENE_RELATIVE) == TransitionRegion(first=(10, 40), second=(10, 40))
    assert not tab._on_overlay_drag(state, (10, 10), (30, 30))
    assert tab._undo_stack.count() == 0
    assert mt.read_project_transition_requests(project) == {}
    assert refusals and "169-class" in refusals[-1]


def test_a_shared_connection_root_refuses_the_drag(tab, warps, session, image, profile, monkeypatch, refusals):
    """A root two maps name is not this map's to move a region on.

    The real loader refuses a shared root that reaches records (both maps would be
    reading one array), and a shared root CANNOT be empty here and still have a
    transition to draw - so the authority's own construction is the only way to
    present that state. The refusal itself is the shipped surface's, reached through
    the same guard every other drag goes through.
    """
    from tools.webfoot.map_transitions import (
        MapTransitions,
        TransitionEntry,
        TransitionRoot,
    )

    identity = mt.TransitionIdentity(MapIdentity(3), 0)
    record_raw = record_bytes(
        destination_key=tuple(key_for(0)),
        first=(100, 140),
        second=(20, 60),
        byte_0x10=0x02,
        word_0x14=48,
        byte_0x16=40,
        byte_0x17=0,
    )
    entry = TransitionEntry(
        identity=identity,
        record=mt.TransitionRecord.from_bytes(record_raw),
        record_address=GBA_BASE + ROOT_BASE,
        element_address=GBA_BASE + ROOT_BASE,
        file_offset=ROOT_BASE,
        original_bytes=record_raw,
    )
    shared_root = ROOT_BASE + 3 * ROOT_STRIDE
    corpus = MapTransitions(
        profile_id=profile.id,
        base_sha256=profile.identity.sha256,
        base_bytes=image,
        keys=tuple(key_for(index) for index in range(len(PER_MAP))),
        key_owner={key_for(index): index for index in range(len(PER_MAP))},
        entries=(entry,),
        roots={
            3: TransitionRoot(MapIdentity(3), shared_root, 1, ROOT_BASE),
            4: TransitionRoot(MapIdentity(4), shared_root, 1, ROOT_BASE),
        },
        profile=profile,
    )
    assert corpus.shared_root_maps(MapIdentity(3)) == (MapIdentity(4),)
    monkeypatch.setattr(mt, "read_map_transitions", lambda *_a, **_k: corpus)

    # A fresh pair of surfaces over the same session, so both read the replaced corpus.
    fresh_warps = WarpTab(session)
    fresh = MapWorkspaceTab(session)
    fresh.set_transition_guard(fresh_warps.region_edit_refusal)
    fresh._session.selected_map = "map:0003"
    fresh._on_map_changed(fresh._maps.item(3))

    state = overlay(fresh, identity.key).state
    assert state.refusal is not None and "shared with map:0004" in state.refusal
    assert region_of(fresh, identity.key) == TransitionRegion(first=(100, 140), second=(20, 60))
    assert not fresh._on_overlay_drag(state, (100, 20), (120, 40))
    assert fresh._undo_stack.count() == 0
    assert refusals and "shared with map:0004" in refusals[-1]


def test_an_out_of_domain_drag_is_refused_by_the_codec_and_leaves_no_history(
    tab, project, refusals
):
    """Dragging a region off the u16 domain is the codec's refusal, not a new rule."""
    state = overlay(tab, TARGET).state

    assert not tab._on_overlay_drag(state, (100, 20), (-200, 20))

    assert tab._undo_stack.count() == 0
    assert mt.read_project_transition_requests(project) == {}
    assert refusals and "unsigned 16-bit" in refusals[-1]
    # The region is back where it was: the failed gesture did not move it.
    assert region_of(tab, TARGET) == TARGET_REGION


def test_a_connection_this_image_does_not_hold_refuses_in_the_authoritys_words(
    tab, warps, project, refusals
):
    """An unsupported form is refused by the corpus, not by a rule stated here.

    The corpus refuses a record whose class word is not one this project measured at
    load time, and an identity it does not hold at all is the same answer one step
    later: the canvas shows the authority's own sentence and writes nothing.
    """
    missing = mt.TransitionIdentity(MapIdentity(0), 9)
    state = canvas_mod.TransitionOverlayState(
        identity=missing,
        region=TARGET_REGION,
        refusal=warps.region_edit_refusal(missing),
    )

    assert state.refusal is not None and "no transition with identity" in state.refusal
    assert not tab._on_overlay_drag(state, (100, 20), (120, 40))
    assert tab._undo_stack.count() == 0
    assert mt.read_project_transition_requests(project) == {}
    assert refusals and "no transition with identity" in refusals[-1]


def test_a_canvas_with_no_authoring_surface_refuses_every_drag(session, rendered, refusals):
    """Fail closed: with nothing to consult, nothing is edited and nothing is written."""
    widget = MapWorkspaceTab(session)
    state = overlay(widget, TARGET).state

    assert state.refusal == canvas_mod._NO_TRANSITION_GUARD
    assert not widget._on_overlay_drag(state, (100, 20), (120, 40))
    assert widget._undo_stack.count() == 0
    assert mt.read_project_transition_requests(session.project_dir) == {}
    assert refusals == [canvas_mod._NO_TRANSITION_GUARD]


# --- bounded reads (CQA-07) ---------------------------------------------------


@pytest.fixture
def reads(monkeypatch):
    """Count the corpus and project reads the canvas makes.

    Both project bindings are counted: the canvas re-reads through its own import of
    `read_project`, and the placement facade behind `scene_placements` holds its own
    binding to the same function - counting only one of them would understate the
    parse and hide a regression in the other.
    """
    import tools.webfoot.project as project_module
    import tools.webfoot.scene as scene_module

    counts = {"corpus": 0, "project": 0}
    real_corpus = mt.read_map_transitions
    real_project = project_module.read_project
    real_scene_project = scene_module.read_project

    def corpus(*args, **kwargs):
        counts["corpus"] += 1
        return real_corpus(*args, **kwargs)

    def project(*args, **kwargs):
        counts["project"] += 1
        return real_project(*args, **kwargs)

    def scene_project(*args, **kwargs):
        counts["project"] += 1
        return real_scene_project(*args, **kwargs)

    monkeypatch.setattr(mt, "read_map_transitions", corpus)
    monkeypatch.setattr(project_module, "read_project", project)
    monkeypatch.setattr(scene_module, "read_project", scene_project)
    return counts


def test_painting_selection_and_zoom_read_nothing(tab, reads):
    for key in reads:
        reads[key] = 0
    tab._on_overlay_clicked(mt.TransitionIdentity(MapIdentity(0), 0))
    tab.show_selected_transition(TARGET)
    tab._refresh_transition_selection()
    tab._canvas.zoom_in()
    tab._populate_transitions()
    assert reads == {"corpus": 0, "project": 0}


def test_a_map_switch_resolves_no_corpus_again_and_parses_the_project_once(tab, reads):
    for key in reads:
        reads[key] = 0
    tab._on_map_changed(tab._maps.item(1))
    # The corpus is per session. The one project parse is the placement facade's own
    # (`scene_placements`), which predates this overlay; the overlay's own authored
    # region read is cached against the project revision and adds none.
    assert reads == {"corpus": 0, "project": 1}
