"""DRAGONBYTE-Z-ROM-SURFACE-001: the ROM destination.

The headless lane drives the whole surface with no ``QApplication``: ``Go to
address`` in both spellings, the ownership strip over a range index, the
changed-bytes overlay, the canonical-versus-current columns, raw search and the
``Open bytes`` gate. It also proves in a fresh interpreter that the surface
module imports without leaking PySide6.

The ROM-gated lane is the acceptance proof for the overlay: a real build of a
real project, and the overlay asserted equal to the manifest's change set AND to
the bytes that actually differ between the canonical and built images, as sets
rather than as counts. It skips without the canonical image.

The windowed lane runs the real shell offscreen and drives the one thing a widget
is not allowed to decide: that the page renders the model's answers - the strip,
the caret, and a disabled ``Open bytes`` with its reason - rather than computing
its own.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import hashlib  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from tools.webfoot import atlas as atlas_module  # noqa: E402
from tools.webfoot.atlas import (  # noqa: E402
    UNKNOWN,
    UNKNOWN_HIGH_ENTROPY,
    VERIFIED_FREE,
    Atlas,
    AtlasObject,
    Confidence,
    CoverageMap,
    CoverageSpan,
    RangeIndex,
)
from tools.webfoot.binary import GBA_ROM_BASE, FileOffset  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.layout import Provenance, RomRange  # noqa: E402
from tools.webfoot.project import read_project  # noqa: E402
from tools.webfoot.write import ByteChange, apply_plan, plan_changes  # noqa: E402

from tools.dragonbyte.inspector import InspectorContext  # noqa: E402
from tools.dragonbyte.journal import project_authority  # noqa: E402
from tools.dragonbyte.rawbytes import declared_extents  # noqa: E402
from tools.dragonbyte.romsurface import (  # noqa: E402
    BYTE_VIEW_ROWS,
    DEFAULT_SEARCH_HITS,
    FILE_OFFSET,
    IMAGE_ADDRESS,
    ROM_ROW_BYTES,
    SEARCH_SCOPE,
    SurfaceError,
    byte_rows,
    changed_offsets,
    declared_tables,
    load_index,
    open_bytes,
    ownership,
    parse_pattern,
    parse_target,
    range_rows,
    range_selection_context,
    row_offset,
    search_bytes,
    selection_context,
    surface_for,
    target_for_address,
    target_for_offset,
    with_manifest,
    write_gate,
)
from tools.dragonbyte.session import Session, SessionError  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _close,
    _write_project,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The synthetic image every headless test reads: zero below 0x400, 0xFF above.
IMAGE_SIZE = 0x2000
IMAGE = b"\x00" * 0x400 + b"\xFF" * (IMAGE_SIZE - 0x400)
PROOF = Provenance("synthetic", "0" * 64, "rom-surface fixture")

#: A byte the fixture atlas object owns, and a byte nobody owns.
OWNED_OFFSET = 0x100
FREE_OFFSET = 0x400
#: A byte a below-floor (CANDIDATE) object covers, and one a declared extent does.
CANDIDATE_OFFSET = 0x180
DECLARED_OFFSET = 0x300

#: The reviewer's measured byte: inside an atlas object and outside every declared
#: table extent, so only the atlas can call it owned.
LEAK_OFFSET = 0x3BBBB0


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(None)


@pytest.fixture(scope="module")
def profile(catalog):
    return catalog.profiles[0]


@pytest.fixture
def atlas() -> Atlas:
    return Atlas(
        "synthetic",
        "0" * 64,
        IMAGE_SIZE,
        CoverageMap(
            (
                CoverageSpan(_span(0, 0x100), UNKNOWN, Confidence.UNKNOWN, PROOF),
                CoverageSpan(
                    _span(0x100, 0x100), UNKNOWN_HIGH_ENTROPY,
                    Confidence.OBSERVED, PROOF,
                ),
                CoverageSpan(
                    _span(0x200, IMAGE_SIZE - 0x200), VERIFIED_FREE,
                    Confidence.CONFIRMED, PROOF,
                ),
            ),
            IMAGE_SIZE,
        ),
        (
            AtlasObject(
                "fixture:table", _span(OWNED_OFFSET, 0x40), "pointer-table",
                Confidence.INFERRED, PROOF,
            ),
            AtlasObject(
                "fixture:candidate", _span(CANDIDATE_OFFSET, 0x40), "pointer-table",
                Confidence.CANDIDATE, PROOF,
            ),
        ),
    )


@pytest.fixture
def index(atlas) -> RangeIndex:
    """The production shape: an atlas plus the profile's declared layer.

    The windowed lane reads this index, and production's `load_index` always
    supplies declared extents, so the fixture that stands in for it does too.
    """
    return RangeIndex(atlas, ((_span(DECLARED_OFFSET, 0x40), "declared:test-table"),))


def _span(start: int, size: int) -> RomRange:
    return RomRange(FileOffset(start), size)


def _session(tmp_path: Path, profile, *, image: bytes = IMAGE) -> Session:
    """A session holding a real project and a synthetic verified image."""
    project_dir = _write_project(tmp_path / "proj")
    session = Session()
    session.project_dir = project_dir
    session.project = read_project(project_dir)
    session.base_image = image
    session.profile = profile
    session.journal.bind(project_authority(session.project))
    return session


# --- Go to address: one number, two spellings ---------------------------------


def test_go_to_address_reads_both_spellings_and_converts_between_them():
    """Acceptance clause 1: an image address and a file offset, both ways."""
    as_address = parse_target("0x08123456", 0x800000)
    as_offset = parse_target("0x123456", 0x800000)

    assert as_address.spelling == IMAGE_ADDRESS
    assert as_offset.spelling == FILE_OFFSET
    assert as_address.file_offset == as_offset.file_offset == 0x123456
    assert as_address.address == as_offset.address == 0x08123456
    assert "image address" in as_address.text()
    assert "file offset" in as_offset.text()

    offset = target_for_offset(0x123456, 0x800000)
    assert offset.address == 0x08123456
    assert target_for_address(offset.address, 0x800000).file_offset == 0x123456
    assert target_for_address(0x08123456, 0x800000).address == 0x08123456


def test_go_to_address_reads_the_rom_window_as_an_address_and_says_so():
    """A bare number in the GBA ROM window is an address, never a silent offset."""
    target = parse_target("0x08000000", 0x800000)

    assert target.spelling == IMAGE_ADDRESS
    assert target.file_offset == 0


@pytest.mark.parametrize(
    "text",
    ("0x09000000", "0x900000", "", "   ", "zz", "0x-4", "-1"),
)
def test_go_to_address_refuses_what_is_not_inside_the_image(text):
    with pytest.raises(SurfaceError):
        parse_target(text, 0x800000)


def test_go_to_address_refuses_the_last_byte_past_the_image():
    assert parse_target("0x7FFFFF", 0x800000).file_offset == 0x7FFFFF
    with pytest.raises(SurfaceError):
        parse_target("0x800000", 0x800000)


# --- the ownership strip ------------------------------------------------------


def test_the_strip_reports_the_index_owners_for_an_owned_byte(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    found = ownership(surface, OWNED_OFFSET)

    assert found.owners == ("fixture:table",)
    assert found.classification == UNKNOWN_HIGH_ENTROPY
    assert found.confidence is Confidence.OBSERVED
    assert found.address == GBA_ROM_BASE + OWNED_OFFSET
    assert "fixture:table" in found.text()


def test_the_strip_says_no_semantic_owner_known_rather_than_leaving_a_blank(
    index, profile
):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    found = ownership(surface, FREE_OFFSET)

    assert found.owners == ()
    assert found.owner_text == "no semantic owner known"
    assert "no semantic owner known" in found.text()


def test_the_strip_states_the_reason_when_no_index_is_loaded(profile):
    surface = surface_for(IMAGE, profile, _journal(), index_problem="no atlas here")
    found = ownership(surface, FREE_OFFSET)

    assert found.owners == ()
    assert "no atlas here" in found.text()
    assert not found.classification


def test_the_strip_never_answers_for_a_byte_the_image_does_not_have(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)

    with pytest.raises(SurfaceError):
        ownership(surface, IMAGE_SIZE)


# --- the overlay and the undo entry -------------------------------------------


def _journal():
    from tools.dragonbyte.journal import EditJournal

    return EditJournal()


def test_a_byte_edit_is_one_undo_entry_and_one_overlay_offset(
    tmp_path, profile
):
    """Acceptance clause 2, driven through the surface the user writes from."""
    session = _session(tmp_path, profile)
    surface = surface_for(session.base_image, profile, session.journal)

    assert surface.overlay == frozenset()
    session.apply_raw_edit(FREE_OFFSET, b"\x01\x02", confirmed=True)

    surface = surface_for(session.base_image, profile, session.journal)
    assert session.journal.depth == 1
    assert surface.overlay == frozenset({FREE_OFFSET, FREE_OFFSET + 1})
    assert surface.current_bytes(FREE_OFFSET, 2) == b"\x01\x02"
    assert surface.canonical_bytes(FREE_OFFSET, 2) == b"\xFF\xFF"

    session.undo_edit()
    after = surface_for(session.base_image, profile, session.journal)
    assert session.journal.depth == 0
    assert after.overlay == frozenset()
    assert after.current_bytes(FREE_OFFSET, 2) == b"\xFF\xFF"


def test_a_byte_edit_into_owned_bytes_is_refused_and_the_overlay_stays_empty(
    tmp_path, profile, index
):
    session = _session(tmp_path, profile)
    surface = surface_for(
        session.base_image, profile, session.journal, index=index
    )
    problem = session.raw_write_problem(
        OWNED_OFFSET, b"\x01", atlas=surface.index.atlas
    )

    assert "fixture:table" in problem
    with pytest.raises(SessionError):
        session.apply_raw_edit(
            OWNED_OFFSET, b"\x01", confirmed=True, atlas=surface.index.atlas
        )
    assert session.journal.depth == 0
    assert surface.overlay == frozenset()


def test_the_overlay_is_the_offsets_that_actually_differ(profile):
    """The synthetic half of clause 3: offsets, measured against real bytes."""
    changes = (
        ByteChange(offset=0x40, old=b"\x00\x00", new=b"\x00\x07", owner="enemy:434",
                   reason="test"),
        ByteChange(offset=0x100, old=b"\x00", new=b"\x00", owner="enemy:435",
                   reason="no-op"),
    )
    plan = plan_changes(
        IMAGE,
        changes,
        profile_id=profile.id,
        base_sha256=hashlib.sha256(IMAGE).hexdigest(),
    )
    built = apply_plan(IMAGE, plan)
    measured = frozenset(
        index for index, (before, after) in enumerate(zip(IMAGE, built))
        if before != after
    )
    surface = surface_for(IMAGE, profile, _journal())

    assert changed_offsets(changes) == measured == frozenset({0x41})
    assert with_manifest(surface, _Manifest(changes)).overlay == measured


class _Manifest:
    """The one field `with_manifest` reads, so this test builds no image."""

    def __init__(self, changes):
        self.changes = changes


# --- the views ----------------------------------------------------------------


def test_the_range_view_rows_tile_the_image_once_in_offset_order(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    rows = range_rows(surface)

    assert [row.span.start.value for row in rows] == [0, 0x100, 0x200]
    assert sum(row.span.size for row in rows) == IMAGE_SIZE
    assert rows[1].owners == ("fixture:table",)
    assert rows[0].owners == ()
    assert rows[0].owner_text == "no semantic owner known"
    assert rows[0].classification == UNKNOWN


def test_the_range_view_is_empty_and_states_why_without_an_index(profile):
    surface = surface_for(IMAGE, profile, _journal(), index_problem="missing atlas")

    assert range_rows(surface) == ()
    assert "missing atlas" in surface.index_problem


def test_the_byte_view_shows_the_canonical_and_the_current_bytes_side_by_side(
    profile,
):
    session = _session(_tmp(), profile)
    session.apply_raw_edit(FREE_OFFSET, b"\x01", confirmed=True)
    surface = surface_for(session.base_image, profile, session.journal)
    rows = byte_rows(surface, FREE_OFFSET, rows=1)

    assert len(rows) == 1
    row = rows[0]
    assert row.offset == row_offset(FREE_OFFSET)
    assert row.address == GBA_ROM_BASE + row.offset
    assert len(row.canonical) == ROM_ROW_BYTES
    assert row.canonical_hex() == "ff" * ROM_ROW_BYTES
    assert row.changed == (FREE_OFFSET - row.offset,)
    assert row.current_hex().startswith("01")


def test_the_byte_view_is_addressable_by_row_and_does_not_run_past_the_image(
    profile,
):
    surface = surface_for(IMAGE, profile, _journal())
    rows = byte_rows(surface, IMAGE_SIZE - 4, rows=BYTE_VIEW_ROWS)

    assert len(rows) == 1
    assert rows[0].offset == IMAGE_SIZE - ROM_ROW_BYTES
    assert rows[0].canonical == IMAGE[IMAGE_SIZE - ROM_ROW_BYTES:]
    with pytest.raises(SurfaceError):
        byte_rows(surface, IMAGE_SIZE, rows=1)


def test_the_ascii_gutter_prints_printable_bytes_and_dots_for_the_rest(profile):
    from tools.dragonbyte.romsurface import ascii_gutter

    assert ascii_gutter(b"A\x00\x7F z") == "A.." + " z"


def test_the_jump_list_is_the_open_indexs_own_declared_table_list(profile, index):
    surface = surface_for(IMAGE, profile, _journal(), index=index)

    # The index's declared layer is the authority once an index is loaded, and the
    # profile's own list is what production puts there: `load_index` builds the
    # index with `declared_extents(profile)`, so the jump list and the write
    # refusal read one list.
    assert declared_tables(surface) == index.declared
    assert declared_tables(surface)
    assert declared_tables(surface_for(IMAGE, profile, _journal())) == declared_extents(
        profile
    )
    assert declared_extents(profile), "the packaged profile declares a table"


# --- raw search ---------------------------------------------------------------


def test_raw_search_finds_every_offset_in_order_and_classifies_each_hit(
    index, profile
):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    hits = search_bytes(surface, "ffff", limit=4)

    assert [hit.offset for hit in hits] == [0x400, 0x401, 0x402, 0x403]
    assert hits[0].classification == VERIFIED_FREE
    assert hits[0].owner_text == "no semantic owner known"
    assert hits[0].address == GBA_ROM_BASE + hits[0].offset


def test_raw_search_reports_the_owner_where_the_index_has_one(index, profile):
    image = bytearray(IMAGE)
    image[OWNED_OFFSET + 4:OWNED_OFFSET + 6] = b"\xAB\xCD"
    surface = surface_for(bytes(image), profile, _journal(), index=index)
    hits = search_bytes(surface, "AB CD")

    assert [hit.offset for hit in hits] == [OWNED_OFFSET + 4]
    assert hits[0].owners == ("fixture:table",)


def test_raw_search_is_bounded_and_stops_at_the_limit(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    hits = search_bytes(surface, "ff", limit=3)

    assert len(hits) == 3
    assert [hit.offset for hit in hits] == [0x400, 0x401, 0x402]


@pytest.mark.parametrize("pattern", ("", "   ", "ABC", "zz", "0x"))
def test_raw_search_refuses_a_pattern_that_is_not_hex_bytes(pattern):
    with pytest.raises(SurfaceError):
        parse_pattern(pattern)


def test_a_search_hit_is_a_position_and_never_an_editable_owner(index, profile):
    """The specification's rule: a hit is not presented as an owner to edit."""
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    hit = search_bytes(surface, "ffffffff", limit=1)[0]

    assert hit.owners == ()
    assert not open_bytes(surface, hit.owner_text).available


# --- Open bytes ---------------------------------------------------------------


def test_open_bytes_opens_a_proven_extent(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    opened = open_bytes(surface, "the fixture table", owner="fixture:table")

    assert opened.available
    assert opened.extent == _span(OWNED_OFFSET, 0x40)
    assert opened.reason == ""
    assert "0x000100" in opened.status()


def test_open_bytes_is_disabled_with_a_stated_reason_when_no_extent_is_proven(
    index, profile
):
    """Acceptance clause 4."""
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    unknown = open_bytes(surface, "enemy:434", owner="enemy:434")
    nothing = open_bytes(surface, "the ROM surface")

    assert not unknown.available
    assert unknown.reason == (
        "Open bytes is disabled: no extent is proven for enemy:434, the range "
        "index knows no byte range for enemy:434."
    )
    assert not nothing.available
    assert "no extent is proven" in nothing.reason
    assert "nothing is selected" in nothing.reason


def test_open_bytes_refuses_an_extent_that_is_not_inside_the_image(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    opened = open_bytes(surface, "past the end", extent=_span(IMAGE_SIZE - 1, 8))

    assert not opened.available
    assert "runs past" in opened.reason


# --- the index is loaded from the SDK's artifact, or not at all ---------------


def test_load_index_states_that_a_missing_artifact_is_missing(profile, tmp_path):
    index, problem = load_index(profile, tmp_path)

    assert index is None
    assert "not assembled" in problem
    assert "atlas.jsonl" in problem


def test_load_index_refuses_an_atlas_for_another_image(profile, tmp_path):
    proof = Provenance("another-profile", "0" * 64, "another image")
    atlas = Atlas(
        "another-profile",
        "0" * 64,
        IMAGE_SIZE,
        CoverageMap(
            (CoverageSpan(_span(0, IMAGE_SIZE), UNKNOWN, Confidence.UNKNOWN, proof),),
            IMAGE_SIZE,
        ),
        (),
    )
    path = tmp_path / "atlas.jsonl"
    path.write_text("\n".join(atlas.to_jsonl_lines()) + "\n", encoding="utf-8")

    index, problem = load_index(profile, tmp_path)

    assert index is None
    assert "profile id" in problem


# --- the headless boundary ----------------------------------------------------


def test_the_surface_module_imports_with_no_pyside6_leak():
    """In a fresh interpreter, because this process has already built a window."""
    probe = (
        "import sys\n"
        "import tools.dragonbyte.romsurface\n"
        "leaked = sorted(n for n in sys.modules "
        "if n == 'PySide6' or n.startswith('PySide6.'))\n"
        "print('LEAKED', leaked)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "LEAKED []" in result.stdout, result.stdout


def test_the_whole_surface_is_answerable_with_no_window(profile):
    """No Qt symbol is needed to build, read or change the surface."""
    status = subprocess.run(
        [sys.executable, "-c", "import tools.dragonbyte.romsurface as m; print(m.ROM_ROW_BYTES)"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert status.returncode == 0, status.stderr
    assert status.stdout.strip() == str(ROM_ROW_BYTES)


# --- the accepted image: the overlay after a real build -----------------------


def _canonical_rom() -> Path:
    matches = sorted(SIBLING_CHECKOUT.glob("roms/*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    for match in matches:
        if hashlib.sha256(match.read_bytes()).hexdigest() == CANONICAL_SHA256:
            return match
    pytest.skip("local ROM is not the canonical profile these offsets target")


def _project_from_the_canonical_image(directory: Path, rom: Path, catalog) -> Path:
    """A valid project that authors exactly one changed enemy statistic.

    Every authored value is the canonical one except a single enemy's hp, so the
    only bytes a build can move are that field's own.
    """
    from dataclasses import replace

    from tools.webfoot.formats import stat_tables as st
    from tools.webfoot.project import PROJECT_FORMAT_VERSION, ProjectMeta, write_project
    from tools.webfoot.stats import load_stat_tables

    tables = load_stat_tables(rom, catalog)
    enemy_identity = st.StatIdentity(kind="enemy", key=434)
    entry = tables.enemy(enemy_identity)
    authored = replace(entry.record, hp=entry.record.hp + 1)
    # Every record is authored at its canonical value except that one field, and
    # the raw bytes authored are the ROM's own: the build applies the semantic
    # fields onto the canonical record, and it refuses a record whose raw bytes
    # came from another image. A project missing a record is refused too.
    enemies = []
    for enemy in tables.enemies():
        record = authored if enemy.identity == enemy_identity else enemy.record
        enemies.append((enemy.identity, record, enemy.original_bytes, None))
    characters = [
        (character.identity, character.record, character.original_bytes, character.alias)
        for character in tables.characters()
    ]
    meta = ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id=tables.profile.id,
        game="buus_fury",
        base_rom_sha256=CANONICAL_SHA256,
        base_rom_size=tables.profile.size,
        name="rom-surface-proof",
    )
    write_project(directory, meta, enemies=enemies, characters=characters)
    return directory


def test_the_overlay_is_exactly_the_manifest_change_set_after_a_build(
    tmp_path, catalog, profile
):
    """Acceptance clause 3, measured: build, then compare three sets."""
    from tools.webfoot.build import build_project

    rom = _canonical_rom()
    project_dir = _project_from_the_canonical_image(tmp_path / "proj", rom, catalog)
    output = tmp_path / "built.gba"
    result = build_project(project_dir, rom, output, catalog)

    canonical = rom.read_bytes()
    built = output.read_bytes()
    assert len(built) == len(canonical), "this project does not grow the image"
    actual = frozenset(
        offset
        for offset, (before, after) in enumerate(zip(canonical, built))
        if before != after
    )
    assert actual, "the authored edit moved at least one byte"

    surface = surface_for(canonical, profile, _journal())
    manifest = result.manifest
    assert changed_offsets(manifest.changes) == actual
    assert with_manifest(surface, manifest).overlay == actual
    assert manifest.changes, "the build reported its change set"


def test_the_canonical_image_is_unchanged_by_the_proof(tmp_path, catalog):
    rom = _canonical_rom()
    before = hashlib.sha256(rom.read_bytes()).hexdigest()
    _project_from_the_canonical_image(tmp_path / "proj", rom, catalog)

    assert hashlib.sha256(rom.read_bytes()).hexdigest() == before == CANONICAL_SHA256


def _tmp() -> Path:
    import tempfile

    return Path(tempfile.mkdtemp(prefix="dragonbyte-romsurface-"))


# --- the windowed lane: the page renders, it does not decide -------------------


@pytest.fixture(scope="module")
def qapp():
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def _settle(page) -> None:
    """Wait for the page's index worker, then drain its queued answer.

    The parse runs on a worker by design (docs/desktop-ui.md forbids blocking the
    UI thread for indexing), so a test that wants the loaded surface has to wait
    for the thread and then let the main thread deliver the signal.
    """
    from PySide6.QtWidgets import QApplication

    assert page._pool.waitForDone(30_000), "the range index worker did not finish"
    QApplication.processEvents()
    assert not page._index_loading, "the range index answer never reached the page"


@pytest.fixture
def rom_page(qapp, tmp_path, profile, index, monkeypatch):
    """The ROM destination inside the real shell, over the synthetic image.

    The index loader is replaced with the fixture index so this lane proves the
    page and nothing about the local atlas artifact; the artifact's own load is
    measured by `load_index` in the headless lane.
    """
    from tools.dragonbyte import rompage
    from tools.dragonbyte.shell import Shell

    monkeypatch.setattr(
        rompage, "load_index", lambda profile, directory=None: (index, "")
    )
    session = _session(tmp_path, profile)
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("rom")
    _settle(shell._rom_page)
    yield shell._rom_page, shell, session
    _close(shell, session)


def test_the_rom_destination_shows_the_surface_and_the_other_five_do_not(rom_page):
    from tools.dragonbyte.rompage import RomPage

    page, shell, _session_ = rom_page
    rows = range_rows(page._surface)

    assert isinstance(page, RomPage)
    assert shell._page_stack.currentWidget() is page
    assert page._model.rowCount() == len(rows)
    assert [
        page._model.data(page._model.index(0, column))
        for column in range(page._model.columnCount())
    ] == [
        f"0x{rows[0].address:08X}",
        f"0x{rows[0].span.start.value:06X}",
        f"0x{rows[0].span.size:06X}",
        rows[0].classification,
        rows[0].confidence.value,
        rows[0].owner_text,
        rows[0].preview.hex(),
    ]
    for candidate in ("maps", "entities", "scripts_text", "graphics", "data"):
        shell.show_destination(candidate)
        assert not isinstance(shell._pages[candidate], RomPage)
    shell.show_destination("rom")


def test_the_strip_is_the_model_ownership_answer_for_the_selection(rom_page):
    page, _shell, _session_ = rom_page

    assert page._strip.text() == ownership(page._surface, page._caret).text()
    assert "no semantic owner known" in page._strip.text()


def test_go_to_address_moves_one_selection_shared_by_both_views(rom_page):
    page, _shell, _session_ = rom_page

    page._goto.setText("0x08000400")
    page._goto_button.click()

    assert page._caret == 0x400
    assert "read as an image address" in page._message.text()
    assert page._model.data(page._model.index(0, 0)) == "0x08000000"
    page._views.setCurrentText("Bytes")
    assert page._caret == 0x400
    assert page._model.data(page._model.index(0, 0)) == "0x08000400"
    assert page._strip.text() == ownership(page._surface, 0x400).text()


def test_go_to_address_refuses_a_number_outside_the_image_with_its_reason(rom_page):
    page, _shell, _session_ = rom_page

    page._goto.setText("0x09999999")
    page._on_go()

    assert "outside" in page._message.text()
    assert page._caret == 0


def test_open_bytes_opens_the_proven_extent_and_is_disabled_without_one(rom_page):
    page, _shell, _session_ = rom_page

    assert page._open_button.isEnabled()
    assert "byte(s) at file offset" in page._open_button.toolTip()
    page._on_open_bytes()
    assert page._views.currentText() == "Bytes"
    assert page._caret == 0


def test_open_bytes_is_disabled_and_states_its_reason_with_no_rom(qapp, tmp_path):
    from tools.dragonbyte.shell import Shell

    session = Session()
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("rom")
    page = shell._rom_page

    assert not page._open_button.isEnabled()
    assert "Open a ROM first" in page._open_button.toolTip()
    assert "No ROM is open" in page._strip.text()
    assert page._model.rowCount() == 0
    _close(shell, session)


def test_a_write_from_the_page_is_one_journal_entry_and_one_undo(
    rom_page, monkeypatch
):
    from PySide6.QtWidgets import QMessageBox

    page, shell, session = rom_page
    monkeypatch.setattr(
        QMessageBox,
        "question",
        staticmethod(lambda *args, **kwargs: QMessageBox.StandardButton.Yes),
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        staticmethod(lambda *args, **kwargs: QMessageBox.StandardButton.Ok),
    )
    page._goto.setText("0x08000400")
    page._on_go()
    page._write_hex.setText("A1 B2")
    page._write_button.click()

    assert session.journal.depth == 1
    assert page._surface.overlay == frozenset({0x400, 0x401})
    assert page._surface.current_bytes(0x400, 2) == b"\xA1\xB2"
    page._views.setCurrentText("Bytes")
    changed = page._model.data(page._model.index(0, 4))
    assert "+00" in changed and "+01" in changed
    assert page._model.data(page._model.index(0, 2)).startswith("a1b2")

    shell.undo_edit()
    assert session.journal.depth == 0
    assert page._surface.overlay == frozenset()
    assert page._model.data(page._model.index(0, 2)).startswith("ffff")


def test_raw_search_lists_the_hits_with_the_index_classification(rom_page):
    page, _shell, _session_ = rom_page

    page._find.setText("ffff")
    page._find_button.click()

    assert page._views.currentText() == "Find results"
    assert page._model.rowCount() == len(page._hits)
    assert page._model.data(page._model.index(0, 0)) == "0x08000400"
    assert page._model.data(page._model.index(0, 2)) == VERIFIED_FREE
    assert "hit(s)" in page._message.text()


def test_a_search_pattern_that_is_not_hex_is_refused_with_its_reason(rom_page):
    page, _shell, _session_ = rom_page

    page._find.setText("not hex")
    page._on_find()

    assert "hex byte pattern" in page._message.text()
    assert page._views.currentText() == "Ranges"


def test_the_page_holds_no_rom_semantics_of_its_own():
    """`rompage` renders the model: it reads no SDK module and no address space."""
    import ast

    source = (REPOSITORY_ROOT / "tools/dragonbyte/rompage.py").read_text(
        encoding="utf-8"
    )
    imported = {
        node.module or ""
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert not [name for name in imported if name.startswith("tools.webfoot")], imported


# --- the review's fixes: one floor, one gate, no stall, no false claim --------


def test_the_write_gate_refuses_while_the_range_index_is_absent(profile):
    """The write fails closed when the surface cannot ask who owns the bytes."""
    surface = surface_for(
        IMAGE,
        profile,
        _journal(),
        index_problem="the range index is not assembled: atlas.jsonl is missing",
    )
    gate = write_gate(surface)

    assert not gate.available
    assert "not assembled" in gate.reason
    assert "cannot tell bytes a structure owns" in gate.reason


def test_the_write_gate_is_open_once_the_index_has_answered(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    gate = write_gate(surface)

    assert gate.available
    assert "saved with the project" in gate.reason
    # The build path applies a raw write now, so the gate must not claim otherwise.
    assert "applied to the image by the build path" in gate.reason


def test_the_raw_write_sentence_names_the_build_path_that_applies_it(rom_page):
    """The sentence where the user writes says what the build actually does."""
    from tools.dragonbyte.rompage import JOURNAL_LOCAL

    page, _shell, _session_ = rom_page

    assert page._write_note.text() == JOURNAL_LOCAL
    assert "build path" in JOURNAL_LOCAL
    assert "no build path" not in JOURNAL_LOCAL
    assert page._write_button.toolTip() == write_gate(page._surface).reason


def test_the_strip_and_the_write_path_use_one_ownership_floor(
    index, profile, tmp_path
):
    """A below-floor object is a known shape on screen and writable on disk."""
    session = _session(tmp_path, profile)
    surface = surface_for(session.base_image, profile, session.journal, index=index)

    known_shape = ownership(surface, CANDIDATE_OFFSET)
    assert known_shape.owners == ()
    assert known_shape.shapes == ("fixture:candidate",)
    assert "below the ownership floor" in known_shape.text()
    assert session.raw_write_problem(
        CANDIDATE_OFFSET, b"\x01", atlas=index.atlas
    ) == ""

    owner = ownership(surface, OWNED_OFFSET)
    assert owner.owners == ("fixture:table",)
    assert "fixture:table" in session.raw_write_problem(
        OWNED_OFFSET, b"\x01", atlas=index.atlas
    )

    declared = ownership(surface, DECLARED_OFFSET)
    assert declared.owners == ("declared:test-table",)
    # Production's declared layer IS the profile's own extent list, so the strip
    # and the write path agree there by construction. This fixture adds one
    # synthetic declared extent the write path cannot know, so only the strip
    # side of the declared rule is asserted here.


def test_the_range_view_reports_owners_under_the_same_floor(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    rows = range_rows(surface)

    def containing(offset: int):
        return next(
            row for row in rows if row.span.start.value <= offset < row.span.end
        )

    # A coverage row can carry an owner and a below-floor shape at once: the
    # split is per identity, not per row, and an owner is what the row shows.
    covered = containing(CANDIDATE_OFFSET)
    assert "fixture:table" in covered.owners
    assert "fixture:candidate" in covered.shapes
    assert covered.owner_text == "fixture:table"
    assert "declared:test-table" in containing(DECLARED_OFFSET).owners


def test_the_range_view_addresses_every_row_in_both_spellings(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    row = range_rows(surface)[0]

    assert row.address == GBA_ROM_BASE + row.span.start.value
    assert (row.address, row.span.start.value) == (0x08000000, 0)


def test_search_reads_the_current_bytes_and_says_so(index, profile, tmp_path):
    """A byte the project wrote is found; the canonical image does not hold it."""
    session = _session(tmp_path, profile)
    session.apply_raw_edit(FREE_OFFSET, b"\xDE\xAD\xBE\xEF", confirmed=True)
    surface = surface_for(session.base_image, profile, session.journal, index=index)

    assert surface.image.find(b"\xDE\xAD\xBE\xEF") == -1
    hits = search_bytes(surface, "DE AD BE EF")
    assert [hit.offset for hit in hits] == [FREE_OFFSET]
    assert "CURRENT bytes" in (search_bytes.__doc__ or "")
    assert "current bytes" in SEARCH_SCOPE


def test_a_search_can_tell_a_full_page_from_the_whole_answer(index, profile):
    surface = surface_for(IMAGE, profile, _journal(), index=index)

    assert len(search_bytes(surface, "ff", limit=3)) == 3
    probed = search_bytes(surface, "ff", limit=DEFAULT_SEARCH_HITS + 1)
    assert len(probed) == DEFAULT_SEARCH_HITS + 1


def test_the_index_parse_runs_off_the_ui_thread(
    qapp, tmp_path, profile, monkeypatch
):
    """The parse is a worker: the event loop is not held for it."""
    import threading
    import time

    from tools.dragonbyte import rompage
    from tools.dragonbyte.shell import Shell

    seen = []

    def slow(profile, directory=None):
        seen.append(threading.current_thread())
        time.sleep(1.0)
        return None, "the range index is not assembled for this test"

    monkeypatch.setattr(rompage, "load_index", slow)
    session = _session(tmp_path, profile)
    shell = Shell(session, tmp_path / "config")
    started = time.monotonic()
    shell.show_destination("rom")
    elapsed = time.monotonic() - started
    page = shell._rom_page

    assert elapsed < 0.6, elapsed
    assert page._index_loading
    assert "still loading" in page._surface.index_problem
    assert not page._write_button.isEnabled()
    _settle(page)
    assert seen and seen[0] is not threading.main_thread()
    assert "not assembled" in page._write_button.toolTip()
    _close(shell, session)


def test_the_write_controls_are_disabled_with_their_reason_without_an_index(
    qapp, tmp_path, profile, monkeypatch
):
    """Acceptance clause 4's shape, applied to the write the reviewer measured."""
    from tools.dragonbyte import rompage
    from tools.dragonbyte.shell import Shell

    monkeypatch.setattr(
        rompage,
        "load_index",
        lambda profile, directory=None: (
            None,
            "the range index is not assembled: atlas.jsonl is missing",
        ),
    )
    session = _session(tmp_path, profile)
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("rom")
    page = shell._rom_page
    _settle(page)

    assert not page._write_button.isEnabled()
    assert not page._write_hex.isEnabled()
    reason = page._write_button.toolTip()
    assert "not assembled" in reason
    assert "cannot tell bytes a structure owns" in reason
    assert reason in page._write_button.accessibleName()

    page._goto.setText("0x08000400")
    page._on_go()
    page._write_hex.setText("A1")
    page._on_write()

    assert session.journal.depth == 0, "no write may happen without the owner answer"
    _close(shell, session)


def test_the_page_says_the_build_applies_a_raw_write(rom_page):
    """The sentence where the user writes names the build path that applies it.

    It asserted the opposite until the build integration landed and made the old
    claim false: an authored raw write is now minted into the plan.
    """
    page, _shell, _session_ = rom_page

    note = page._write_note.text()

    assert "saved with the project" in note
    assert "shown in this surface" in note
    assert "build path applies it" in note.lower()
    assert "no build path" not in note.lower()
    assert "takes effect" not in note
    assert page._write_note.isVisibleTo(page)
    assert "applied to the image by the build path" in page._write_button.toolTip().lower()


def test_the_range_view_headers_name_both_spellings(rom_page):
    from PySide6.QtCore import Qt

    page, _shell, _session_ = rom_page

    assert page._model.headerData(0, Qt.Orientation.Horizontal) == "Address"
    assert page._model.headerData(1, Qt.Orientation.Horizontal) == "File offset"
    assert [
        page._model.data(page._model.index(0, column)) for column in (0, 1)
    ] == ["0x08000000", "0x000000"]


def test_a_capped_search_page_says_it_is_the_first_of_more(rom_page):
    page, _shell, _session_ = rom_page

    page._find.setText("ff")
    page._find_button.click()

    assert page._hits_truncated
    assert len(page._hits) == DEFAULT_SEARCH_HITS
    assert "the first of more" in page._message.text()
    assert SEARCH_SCOPE in page._message.text()


def test_a_search_for_a_byte_the_project_wrote_is_not_capped(rom_page):
    page, _shell, session = rom_page
    session.apply_raw_edit(FREE_OFFSET, b"\xDE\xAD\xBE\xEF", confirmed=True)
    page.refresh()

    page._find.setText("DE AD BE EF")
    page._find_button.click()

    assert [hit.offset for hit in page._hits] == [FREE_OFFSET]
    assert not page._hits_truncated
    assert "the first of more" not in page._message.text()


def test_the_canonical_rom_byte_the_gate_protects_is_refused_by_the_real_index(
    profile, tmp_path
):
    """The reviewer's measured leak, pinned against the assembled index.

    A byte inside an atlas object and outside every declared extent is refused by
    the atlas the range index holds, which is exactly why the write path is
    closed while no index is loaded.
    """
    index, problem = load_index(profile)
    if index is None:
        pytest.skip(problem)
    rom = _canonical_rom()
    image = rom.read_bytes()
    session = _session(tmp_path, profile, image=image)
    surface = surface_for(image, profile, session.journal, index=index)

    assert write_gate(surface).available
    owners = ownership(surface, LEAK_OFFSET).owners
    assert "seed:scripts.item_use.pool" in owners, owners
    assert "atlas:seed:scripts.item_use.pool" in session.raw_write_problem(
        LEAK_OFFSET, b"\x01", atlas=index.atlas
    )


# --- the delta review: identity, honesty, and the boundary --------------------


def _one_object_index(identity: str, offset: int) -> RangeIndex:
    """A tiny index whose only owner sits at one offset, for the race test."""
    proof = Provenance("synthetic", "0" * 64, "late-answer fixture")
    atlas = Atlas(
        "synthetic",
        "0" * 64,
        IMAGE_SIZE,
        CoverageMap(
            (
                CoverageSpan(
                    _span(0, IMAGE_SIZE), UNKNOWN, Confidence.UNKNOWN, proof
                ),
            ),
            IMAGE_SIZE,
        ),
        (
            AtlasObject(
                identity, _span(offset, 0x40), "pointer-table",
                Confidence.CONFIRMED, proof,
            ),
        ),
    )
    return RangeIndex(atlas)


def test_a_late_index_answer_for_another_image_is_ignored(
    qapp, tmp_path, profile, monkeypatch
):
    """The reviewer's race: A's answer must not be installed while B is open.

    A is slow and B is instant, so B's answer is delivered first and A's lands
    after it. The last-delivered answer must not be the one that wins.
    """
    import time

    from tools.dragonbyte import rompage
    from tools.dragonbyte.shell import Shell

    first = _one_object_index("image:a", 0x100)
    second = _one_object_index("image:b", 0x200)
    calls: list[int] = []

    def slow(profile, directory=None):
        call = len(calls)
        calls.append(call)
        if call == 0:
            time.sleep(1.0)
        return (first if call == 0 else second), ""

    monkeypatch.setattr(rompage, "load_index", slow)
    session = _session(tmp_path, profile)
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("rom")
    page = shell._rom_page

    session.rom_path = tmp_path / "second.gba"
    session.base_image = IMAGE
    page.refresh()
    deadline = time.monotonic() + 20
    while len(calls) < 2 and time.monotonic() < deadline:
        time.sleep(0.01)
    assert len(calls) == 2, "the second image started its own parse"

    _settle(page)
    assert calls == [0, 1]
    assert page._index is second, "the answer for the replaced image was installed"
    assert ownership(page._surface, 0x200).owners == ("image:b",)
    assert ownership(page._surface, 0x100).owners == ()
    assert write_gate(page._surface).available
    assert session.raw_write_problem(
        0x100, b"\x01", atlas=page._surface.index.atlas
    ) == "", "the gate must consult the current image's atlas"
    assert "image:a" in session.raw_write_problem(
        0x100, b"\x01", atlas=first.atlas
    )
    _close(shell, session)


def test_range_rows_skip_spans_the_open_image_does_not_have(index, profile):
    """An index for a larger image must not raise an address outside this one."""
    smaller = IMAGE[:0x180]
    surface = surface_for(smaller, profile, _journal(), index=index)

    rows = range_rows(surface)

    assert rows, "the spans inside the image are still rendered"
    assert all(row.span.start.value < len(smaller) for row in rows)
    assert [row.span.start.value for row in rows] == [0, 0x100]


# --- the index worker's own boundary ------------------------------------------


def _bare_page():
    """A ROM page over no image, so it starts no parse and a test can drive one."""
    from tools.dragonbyte.rompage import RomPage

    return RomPage(Session())


def test_a_failed_parse_becomes_the_stated_reason_when_the_page_is_alive(
    qapp, monkeypatch
):
    """The promise the worker exists for: a failure is a reason, not a dead thread."""
    from tools.dragonbyte import rompage

    def broken(profile, directory=None):
        raise RuntimeError("the atlas parser fell over")

    monkeypatch.setattr(rompage, "load_index", broken)
    page = _bare_page()
    answers: list = []
    page._index_signals.finished.connect(lambda *args: answers.append(args))
    task = rompage._IndexTask(None, None, 7, page._index_signals)

    task.run()  # on this thread, so the answer is delivered as a direct call

    assert len(answers) == 1
    token, index, problem = answers[0]
    assert token == 7
    assert index is None
    assert "could not be loaded" in problem
    assert "the atlas parser fell over" in problem


def test_a_parse_that_answers_after_its_page_is_gone_does_not_raise(qapp, monkeypatch):
    """The measured failure: "RuntimeError: Signal source has been deleted".

    A parse outlives the request that started it, so it can answer after the page
    that owns the signal source has been destroyed - which is what `Open bytes`
    from the Data destination makes ordinary. Before the emit was guarded that
    exception escaped on a pool thread, which is exactly what this boundary
    exists to prevent.

    `Shiboken.delete` deletes the C++ object while the Python wrapper the task
    holds stays alive, which is the shape of a page destroyed mid-parse. Qt's
    deferred deletion does not reproduce it here: `deleteLater` plus
    `processEvents` leaves the object usable, measured before this test was
    written.
    """
    shiboken = pytest.importorskip("shiboken6")
    from tools.dragonbyte import rompage

    monkeypatch.setattr(
        rompage, "load_index", lambda profile, directory=None: (None, "an answer")
    )
    page = _bare_page()
    signals = page._index_signals
    answers: list = []
    signals.finished.connect(lambda *args: answers.append(args))
    task = rompage._IndexTask(None, None, 8, signals)

    shiboken.Shiboken.delete(page)

    task.run()  # must not raise: nobody is left to report to

    assert answers == [], "a destroyed page can install nothing"


def test_the_page_drops_a_parse_when_its_own_token_answers(qapp):
    """One entry per outstanding parse, released by the answer that names it."""
    from tools.dragonbyte import rompage

    page = _bare_page()
    assert page._index_tasks == {}
    assert not hasattr(page, "_index_task"), "the dead attribute is gone"
    page._index_request = 3
    page._index_tasks[3] = rompage._IndexTask(None, None, 3, page._index_signals)

    page._index_ready(3, None, "the range index is unavailable")

    assert page._index_tasks == {}
    assert page._index_problem == "the range index is unavailable"
    assert page._index is None


def test_a_stale_index_answer_is_dropped_without_installing_or_leaking(qapp):
    from tools.dragonbyte import rompage

    page = _bare_page()
    page._index_request = 9
    page._index_tasks[4] = rompage._IndexTask(None, None, 4, page._index_signals)

    page._index_ready(4, "not an index", "stale")

    assert page._index_tasks == {}
    assert page._index is None
    assert page._index_problem == ""


# --- the visual-readiness pass: one selection, one inspector, one jump list ----


def _inspector(shell):
    """The shell's one inspector pane, found rather than reached for."""
    from tools.dragonbyte.inspector import InspectorPane

    panes = shell.findChildren(InspectorPane)
    assert len(panes) == 1
    return panes[0]


def _pane_text(pane) -> str:
    return " ".join(
        (
            pane._friendly.text(),
            pane._stable.text(),
            pane._support.text(),
            pane._detail.text(),
        )
    )


def test_the_selection_context_carries_the_identity_the_extent_and_the_restriction(
    atlas, index, profile
):
    """The headless half: what a range says about itself, in the pane's own tiers."""
    surface = surface_for(IMAGE, profile, _journal(), index=index)
    rows = range_rows(surface)

    def containing(offset: int):
        return next(row for row in rows if row.span.start.value <= offset < row.span.end)

    owned = range_selection_context(surface, containing(OWNED_OFFSET))
    assert owned.friendly == "fixture:table"
    assert owned.support == "Read-only"
    assert owned.stable.startswith(f"0x{GBA_ROM_BASE + OWNED_OFFSET:08X}")
    assert "0x000100 + 0x000100 byte(s)" in owned.stable
    assert owned.detail.startswith(UNKNOWN_HIGH_ENTROPY + " / OBSERVED")

    declared = range_selection_context(surface, containing(DECLARED_OFFSET))
    assert declared.friendly == "declared:test-table"
    assert declared.support == "Read-only"

    unmapped = range_selection_context(surface, containing(0x40))
    assert unmapped.friendly == "no semantic owner known"
    assert unmapped.support == "Not mapped"
    assert UNKNOWN in unmapped.detail

    # The declared layer owns the bytes it covers, so the free row is read with an
    # index that carries no declared extent, and its own rows.
    undeclared = surface_for(IMAGE, profile, _journal(), index=RangeIndex(atlas))
    free_row = next(
        row
        for row in range_rows(undeclared)
        if row.span.start.value <= FREE_OFFSET < row.span.end
    )
    assert free_row.owners == ()
    free = range_selection_context(undeclared, free_row)
    assert free.support == "Editable"
    assert free.friendly == "no semantic owner known"
    assert "a raw write is offered here" in free.detail

    single = selection_context(undeclared, FREE_OFFSET)
    assert "file offset 0x000400 | 1 byte(s)" in single.detail
    assert single.stable.endswith("+ 0x000001 byte(s)")


def test_the_selection_context_states_the_closed_write_gate_with_no_index(profile):
    surface = surface_for(IMAGE, profile, _journal(), index_problem="no atlas here")
    answer = selection_context(surface, FREE_OFFSET)

    assert answer.support == "Not mapped"
    assert answer.friendly == "no semantic owner known"
    assert "no atlas here" in answer.detail
    assert "A raw write is disabled" in answer.detail


def test_the_first_render_selects_a_real_row_and_the_inspector_publishes_it(rom_page):
    """The initial-row question, resolved: the first row IS the selection."""
    page, shell, _session_ = rom_page
    pane = _inspector(shell)

    current = page._table.selectionModel().currentIndex()
    assert current.isValid(), "a highlighted row must be an actual selection"
    row = page._range_rows[current.row()]
    assert page._caret == row.span.start.value, "the caret is the selected row's own start"

    answer = range_selection_context(page._surface, row)
    assert pane._friendly.text() == answer.friendly
    assert pane._stable.text() == answer.stable
    assert pane._support.text().endswith(answer.support)
    assert pane._detail.text() == answer.detail
    assert row.classification in pane._detail.text()
    assert "Nothing is selected" not in _pane_text(pane)


@pytest.mark.parametrize("path", ("programmatic", "keyboard", "mouse"))
def test_every_selection_path_publishes_the_same_context(rom_page, path):
    """Mouse, keyboard and programmatic selection are one path, not three."""
    from PySide6.QtCore import Qt as QtCore
    from PySide6.QtTest import QTest

    page, shell, _session_ = rom_page
    pane = _inspector(shell)
    target = 2
    row = page._range_rows[target]
    answer = range_selection_context(page._surface, row)

    shell.show()
    QTest.qWait(20)
    page._table.setCurrentIndex(page._model.index(0, 0))
    if path == "keyboard":
        page._table.setFocus()
        for _ in range(target):
            QTest.keyClick(page._table, QtCore.Key.Key_Down)
    elif path == "mouse":
        rectangle = page._table.visualRect(page._model.index(target, 0))
        assert not rectangle.isEmpty(), "the target row is not laid out to click"
        QTest.mouseClick(
            page._table.viewport(), QtCore.MouseButton.LeftButton, pos=rectangle.center()
        )
    else:
        page._table.setCurrentIndex(page._model.index(target, 0))

    assert page._caret == row.span.start.value, path
    assert pane._friendly.text() == answer.friendly, path
    assert pane._stable.text() == answer.stable, path
    assert pane._support.text().endswith(answer.support), path
    shell.hide()


def test_a_click_through_the_table_publishes_that_rows_own_identity(rom_page):
    """The measured defect: row 0x08719000 highlighted with an empty pane."""
    from PySide6.QtTest import QTest

    page, shell, _session_ = rom_page
    pane = _inspector(shell)
    target = len(page._range_rows) - 1
    row = page._range_rows[target]

    shell.show()
    QTest.qWait(20)
    page._table.selectRow(target)
    page._table.setCurrentIndex(page._model.index(target, 0))
    QTest.qWait(10)

    assert pane._friendly.text() == range_selection_context(page._surface, row).friendly
    assert f"0x{row.span.start.value:06X}" in pane._stable.text()
    assert "Nothing is selected" not in _pane_text(pane)
    shell.hide()


def test_another_pages_late_answer_cannot_republish_over_rom(rom_page):
    """One inspector, told only by the destination that is on screen."""
    page, shell, _session_ = rom_page
    pane = _inspector(shell)
    before = _pane_text(pane)

    shell._text_page._publish_selection(
        InspectorContext(friendly="a stale row", stable="stale:0001", support="Read-only")
    )

    assert _pane_text(pane) == before
    assert "a stale row" not in _pane_text(pane)


def test_no_rom_leaves_no_current_row_and_the_inspectors_empty_state(qapp, tmp_path):
    from tools.dragonbyte.shell import Shell

    session = Session()
    shell = Shell(session, tmp_path / "config")
    shell.show_destination("rom")
    page = shell._rom_page
    pane = _inspector(shell)

    assert not page._table.selectionModel().currentIndex().isValid()
    assert "Nothing is selected" in pane._friendly.text()
    assert "ROM is the active destination" in pane._detail.text()
    _close(shell, session)


def test_the_jump_list_is_the_open_indexs_own_declared_layer(rom_page):
    page, _shell, _session_ = rom_page

    expected = [
        f"{owner} (0x{span.start.value:06X})"
        for span, owner in declared_tables(page._surface)
        if span.start.value < page._surface.image_size
    ]
    assert expected, "the open index declares a table inside the image"
    assert [page._jump.itemText(at) for at in range(page._jump.count())] == expected
    assert page._jump.isEnabled()


def test_a_jump_selects_the_atlas_coverage_row_holding_the_declared_table(rom_page):
    """The jump lands on a coverage row the atlas already produced, not a new one."""
    page, _shell, _session_ = rom_page
    position = 0
    start = page._jump.itemData(position)
    assert start is not None

    page._jump.setCurrentIndex(position)
    page._on_jump(position)

    current = page._table.selectionModel().currentIndex()
    assert current.isValid(), "a jump must select a row"
    row = page._range_rows[current.row()]
    assert row.span.start.value <= start < row.span.end
    # The caret stays at the table's own first byte, not the row's start, so a
    # write after a jump lands where the jump named.
    assert page._caret == start
    assert page._message.text().startswith("Jump to ")


def test_a_jump_goes_through_the_one_selection_from_the_bytes_view(rom_page):
    page, _shell, _session_ = rom_page
    start = page._jump.itemData(0)

    page._views.setCurrentText("Bytes")
    assert page._views.currentText() == "Bytes"
    page._jump.setCurrentIndex(0)
    page._on_jump(0)

    assert page._views.currentText() == "Ranges"
    current = page._table.selectionModel().currentIndex()
    assert current.isValid()
    row = page._range_rows[current.row()]
    assert row.span.start.value <= start < row.span.end


def test_the_range_table_keeps_identity_columns_wide_and_elides_in_the_middle(rom_page):
    from PySide6.QtCore import Qt as QtCore

    page, _shell, _session_ = rom_page

    assert page._table.textElideMode() == QtCore.TextElideMode.ElideMiddle
    assert (
        page._model.headerData(6, QtCore.Orientation.Horizontal) == "Preview (bytes)"
    )
    assert page._table.columnWidth(3) >= 190, "Classification"
    assert page._table.columnWidth(5) >= 170, "Owner"
    assert page._table.horizontalHeader().stretchLastSection()
    assert page._goto.placeholderText() == "address or offset"
    assert "image address" in page._goto.toolTip()
