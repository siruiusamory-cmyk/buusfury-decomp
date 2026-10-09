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

from tools.dragonbyte.journal import project_authority  # noqa: E402
from tools.dragonbyte.rawbytes import declared_extents  # noqa: E402
from tools.dragonbyte.romsurface import (  # noqa: E402
    BYTE_VIEW_ROWS,
    FILE_OFFSET,
    IMAGE_ADDRESS,
    ROM_ROW_BYTES,
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
    row_offset,
    search_bytes,
    surface_for,
    target_for_address,
    target_for_offset,
    with_manifest,
)
from tools.dragonbyte.session import Session, SessionError  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
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
        ),
    )


@pytest.fixture
def index(atlas) -> RangeIndex:
    return RangeIndex(atlas)


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


def test_the_jump_list_is_the_profiles_own_declared_table_list(profile, index):
    surface = surface_for(IMAGE, profile, _journal(), index=index)

    assert declared_tables(surface) == declared_extents(profile)
    assert declared_tables(surface), "the packaged profile declares a table"


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
