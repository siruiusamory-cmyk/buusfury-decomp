"""MAP-NEW-AUTHORING-001: authoring a genuinely new map, against the real image.

Everything here reads the canonical Buu's Fury image and, where it builds, emits
a derivative under `tmp_path`. The canonical image is never written. The model
half of the capability is `tests/unit/test_map_authoring.py`'s.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot import map_authoring as ma
from tools.webfoot.allocation import AllocationError
from tools.webfoot.build import ProjectValidationError, build_project, validate_project
from tools.webfoot.map_transitions import read_map_transitions
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.model import (AuthoredMap, AuthoredMaps, ProjectMeta,
                                         read_project, write_authored_maps,
                                         write_project)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
TABLE_OFFSET = 0x8E2E0
TABLE_ADDRESS = 0x0808E2E0
STRIDE = 0x38
CANONICAL_ROWS = 452
EXPANSION_BASE = 0x800000
EXPANDED_SIZE = 0x01000000
NAME = "cave"
DONOR = 40
KEY = (0x99, 0x01)


def _rom_path() -> Path:
    return Path(os.environ.get(
        "MAP_NEW_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))


@pytest.fixture(scope="module")
def canonical() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture(scope="module")
def identified(canonical, catalog):
    from tools.webfoot.rom import identify_rom

    return identify_rom(_rom_path(), catalog)


@pytest.fixture(scope="module")
def profile(identified):
    return identified.profile_match.profile


@pytest.fixture(scope="module")
def extracted(tmp_path_factory, canonical, catalog) -> Path:
    """One extracted project, shared: extraction is the expensive half."""
    import shutil

    from tools.webfoot.build import extract_project

    root = tmp_path_factory.mktemp("map-new-project")
    destination = root / "project"
    extract_project(_rom_path(), destination, catalog, name="map-new",
                    graphics=False)
    return destination


@pytest.fixture()
def project(tmp_path, extracted) -> Path:
    import shutil

    destination = tmp_path / "project"
    shutil.copytree(extracted, destination)
    return destination


def _one(name: str = NAME, donor: int = DONOR, key: tuple[int, int] = KEY):
    return AuthoredMaps(maps={name: AuthoredMap(name, donor, key[0], key[1])})


def _named_offsets() -> set[int]:
    """Every canonical offset this domain is allowed to change."""
    named = set(range(ma.BASE_POOL_FILE_OFFSET, ma.BASE_POOL_FILE_OFFSET + 4))
    named.update(range(ma.COUNT_IMMEDIATE_FILE_OFFSET,
                       ma.COUNT_IMMEDIATE_FILE_OFFSET + 2))
    return named


def _materialize(canonical, identified, profile, document):
    return ma.materialize_authored_maps(
        canonical, identified, profile, tuple(document.ordered()))


# --- the storage contract ----------------------------------------------------


def test_the_table_is_452_rows_at_the_declared_extent(canonical, profile):
    records = ma.read_records(canonical, profile)

    assert len(records) == CANONICAL_ROWS
    assert ma.record_count(profile) == CANONICAL_ROWS
    assert ma.table_offset(profile, len(canonical)) == TABLE_OFFSET
    assert len(ma.canonical_table(canonical, profile)) == CANONICAL_ROWS * STRIDE


def test_the_engine_bound_is_the_one_halfword_the_census_measured(canonical, profile):
    """The count is code, and the two sites are checked before anything is written."""
    helper = canonical[ma.COUNT_IMMEDIATE_FILE_OFFSET:
                       ma.COUNT_IMMEDIATE_FILE_OFFSET + 2]
    assert helper == bytes([ma.COUNT_IMMEDIATE_CANONICAL, ma.COUNT_IMMEDIATE_OPCODE])
    assert (ma.COUNT_IMMEDIATE_BASE + ma.COUNT_IMMEDIATE_CANONICAL
            == CANONICAL_ROWS)


def test_the_base_word_is_the_one_pool_entry_the_lookup_loads(canonical, profile):
    import struct

    assert struct.unpack_from("<I", canonical, ma.BASE_POOL_FILE_OFFSET)[0] \
        == TABLE_ADDRESS
    assert ma.table_identity(profile).endswith("/map_entry_table:0000")


# --- the census, in the shape the roster incident taught ---------------------


def test_exactly_one_word_in_the_image_names_the_table_base(canonical):
    """Enumerated, not asserted: a second consumer has to fail this test.

    The roster census incident (`docs/research/APPEARANCE_ROSTER_EXPANSION.md`)
    is the reason this is a scan rather than a sentence: a published claim that
    the base has one inbound word is only load-bearing while a test re-derives
    it, and removing a consumer has to break the test rather than pass quietly.
    """
    import struct

    hits = [offset for offset in range(len(canonical) - 3)
            if struct.unpack_from("<I", canonical, offset)[0] == TABLE_ADDRESS]
    assert hits == [ma.BASE_POOL_FILE_OFFSET]


def test_the_count_helper_has_exactly_one_caller(canonical):
    """The helper is map-table specific, which is what makes one patch enough."""
    capstone = pytest.importorskip("capstone")
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    callers = []
    for address in range(0x08000000, 0x08040000, 2):
        offset = address - 0x08000000
        for insn in md.disasm(canonical[offset:offset + 4], address):
            if insn.mnemonic in ("bl", "blx") and insn.operands:
                if insn.operands[0].imm == 0x080125E0:
                    callers.append(address)
    assert callers == [0x08008A02]


# --- the plan ----------------------------------------------------------------


def test_one_authored_map_appends_exactly_one_row(canonical, identified, profile):
    result = _materialize(canonical, identified, profile, _one())

    assert result.canonical_rows == CANONICAL_ROWS
    assert result.row_count == CANONICAL_ROWS + 1
    assert result.placements[0].table_index == CANONICAL_ROWS
    assert result.placements[0].identity == f"map:{CANONICAL_ROWS:04d}"
    assert result.placements[0].key == KEY
    # The donor's root is inherited; the layer is this map's own copy.
    assert result.placements[0].layer_address != 0
    assert result.placements[0].root_address != result.placements[0].layer_address


def test_the_plan_repoints_the_base_and_raises_the_bound_by_one(
        canonical, identified, profile):
    import struct

    result = _materialize(canonical, identified, profile, _one())
    changes = {change.offset: change for change in result.changes}

    pool = changes[ma.BASE_POOL_FILE_OFFSET]
    assert pool.new == struct.pack("<I", result.table_address)
    assert pool.old == canonical[ma.BASE_POOL_FILE_OFFSET:
                                 ma.BASE_POOL_FILE_OFFSET + 4]

    bound = changes[ma.COUNT_IMMEDIATE_FILE_OFFSET]
    assert bound.new == bytes([ma.COUNT_IMMEDIATE_CANONICAL + 1,
                               ma.COUNT_IMMEDIATE_OPCODE])

    table = next(change for change in result.changes
                 if change.offset == result.table_range.start.value)
    assert table.new[:CANONICAL_ROWS * STRIDE] \
        == ma.canonical_table(canonical, profile)
    row = table.new[CANONICAL_ROWS * STRIDE:]
    assert row[:2] == bytes(KEY)
    assert struct.unpack_from("<I", row, 0x2C)[0] == result.placements[0].source_file_offset \
        + 0x08000000


def _donor_root(canonical, profile, donor: int) -> bytes:
    """The donor's own root bytes: `+0x2C` names a word that holds the root."""
    import struct

    record = ma.read_records(canonical, profile)[donor]
    source = record.variation_array_pointer_raw
    address = struct.unpack_from("<I", canonical, source - 0x08000000)[0]
    return canonical[address - 0x08000000:address - 0x08000000 + ma.ROOT_SIZE]


def test_the_new_root_names_its_own_layer_and_carries_the_donor_root(
        canonical, identified, profile):
    import struct

    result = _materialize(canonical, identified, profile, _one())
    placement = result.placements[0]
    changes = {change.offset: change for change in result.changes}

    block = changes[placement.source_file_offset].new
    assert struct.unpack_from("<I", block, 0)[0] == placement.root_address
    root = block[4:]
    slot = ma.mg.ROOT_LAYER_SLOTS[placement.layer_slot]
    assert struct.unpack_from("<I", root, slot)[0] == placement.layer_address
    # Every field this domain does not author is the donor's own byte.
    donor_root = _donor_root(canonical, profile, DONOR)
    for offset in range(0, ma.ROOT_SIZE, 4):
        if offset == slot:
            continue
        assert root[offset:offset + 4] == donor_root[offset:offset + 4]


def test_the_authored_layer_is_a_copy_of_the_donor_layer(
        canonical, identified, profile):
    import struct

    result = _materialize(canonical, identified, profile, _one())
    placement = result.placements[0]
    change = next(item for item in result.changes
                  if item.offset == placement.layer_file_offset)
    donor_root = _donor_root(canonical, profile, DONOR)
    donor_slot = ma.mg.ROOT_LAYER_SLOTS[placement.layer_slot]
    donor_layer = struct.unpack_from("<I", donor_root, donor_slot)[0]
    assert change.new == canonical[donor_layer - 0x08000000:
                                   donor_layer - 0x08000000 + len(change.new)]


# --- the ceiling and one above -----------------------------------------------


def test_the_supported_ceiling_is_accepted_and_one_above_is_refused(
        canonical, identified, profile):
    ceiling = ma.MAX_SUPPORTED_ROWS - CANONICAL_ROWS
    accepted = AuthoredMaps(maps={
        f"m{index:02d}": AuthoredMap(f"m{index:02d}", DONOR, KEY[0], index + 1)
        for index in range(ceiling)
    })
    result = _materialize(canonical, identified, profile, accepted)
    assert result.row_count == ma.MAX_SUPPORTED_ROWS

    with pytest.raises(Exception) as refused:
        AuthoredMaps(maps={
            **{f"m{index:02d}": AuthoredMap(f"m{index:02d}", DONOR, KEY[0],
                                            index + 1)
               for index in range(ceiling)},
            "one-too-many": AuthoredMap("one-too-many", DONOR, KEY[0], ceiling + 1),
        })
    assert "at most" in str(refused.value)


def test_a_donor_outside_the_table_is_refused(canonical, identified, profile):
    with pytest.raises(ma.MapAuthoringError) as refused:
        _materialize(canonical, identified, profile, _one(donor=CANONICAL_ROWS))
    assert "donor map index" in str(refused.value)


def test_a_key_a_canonical_record_already_uses_is_refused(
        canonical, identified, profile):
    taken = ma.canonical_key(ma.read_records(canonical, profile)[1])
    with pytest.raises(ma.MapAuthoringError) as refused:
        _materialize(canonical, identified, profile, _one(key=taken))
    assert "already used" in str(refused.value)


def test_a_tampered_base_pool_word_fails_closed(canonical, identified, profile):
    tampered = bytearray(canonical)
    tampered[ma.BASE_POOL_FILE_OFFSET] ^= 0xFF
    with pytest.raises(ma.MapAuthoringError) as refused:
        _materialize(bytes(tampered), identified, profile, _one())
    assert "literal pool word" in str(refused.value)


def test_a_tampered_count_immediate_fails_closed(canonical, profile):
    """The check is stated against the canonical immediate, not against a length.

    The image-level path refuses a tampered image even earlier, through the
    profile identity gate; this exercises the patch's own check directly, which is
    what a second image with the same table but a different bound would hit.
    """
    tampered = bytearray(canonical)
    tampered[ma.COUNT_IMMEDIATE_FILE_OFFSET] = 0xC4
    with pytest.raises(ma.MapAuthoringError) as refused:
        ma._row_count_change(bytes(tampered), profile, CANONICAL_ROWS + 1)
    assert "adds" in str(refused.value)


def test_a_tampered_image_is_refused_before_the_domain_plans_anything(
        identified, profile):
    """The domain never plans against bytes the profile did not authenticate."""
    from tools.webfoot.layout import LayoutError

    tampered = bytearray(_rom_path().read_bytes())
    tampered[ma.COUNT_IMMEDIATE_FILE_OFFSET] = 0xC4
    document = _one()
    with pytest.raises(LayoutError) as refused:
        ma.materialize_authored_maps(bytes(tampered), identified, profile,
                                     tuple(document.ordered()))
    assert "wrong ROM/profile" in str(refused.value)


# --- the build ---------------------------------------------------------------


def _build(project, rom, output, catalog):
    return build_project(project, rom, output, catalog)


@pytest.fixture(scope="module")
def built(tmp_path_factory, extracted, catalog):
    """One built derivative for the whole module, and its image."""
    import shutil

    root = tmp_path_factory.mktemp("map-new-build")
    project = root / "project"
    shutil.copytree(extracted, project)
    write_authored_maps(project, _one())
    output = root / "out.gba"
    result = _build(project, _rom_path(), output, catalog)
    return root, project, output, result, output.read_bytes()


def test_the_build_emits_an_expanded_image_and_a_manifest(built):
    _root, _project, output, result, image = built

    assert output.stat().st_size == EXPANDED_SIZE
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["base"]["sha256"] == CANONICAL_SHA256
    assert manifest["relocations"], "the moved table is not recorded"
    assert manifest["relocations"][0]["owner"] == ma.TABLE_OWNER


def test_the_built_image_grows_the_table_and_repaints_only_the_two_sites(
        built, canonical):
    import struct

    _root, _project, _output, _result, image = built
    table_address = struct.unpack_from("<I", image, ma.BASE_POOL_FILE_OFFSET)[0]
    table_at = table_address - 0x08000000
    assert table_at >= EXPANSION_BASE
    assert struct.unpack_from("<H", image, ma.COUNT_IMMEDIATE_FILE_OFFSET)[0] \
        == (ma.COUNT_IMMEDIATE_OPCODE << 8) | (ma.COUNT_IMMEDIATE_CANONICAL + 1)

    # The canonical rows survive byte-for-byte at the new address.
    assert image[table_at:table_at + CANONICAL_ROWS * STRIDE] \
        == canonical[TABLE_OFFSET:TABLE_OFFSET + CANONICAL_ROWS * STRIDE]

    named = _named_offsets()
    changed = [offset for offset in range(len(canonical))
               if offset not in named and image[offset] != canonical[offset]]
    assert changed == []


def test_the_built_image_carries_the_new_identity_the_plan_described(
        built, canonical, identified, profile):
    import struct

    _root, _project, _output, _result, image = built
    result = _materialize(canonical, identified, profile, _one())
    table_address = struct.unpack_from("<I", image, ma.BASE_POOL_FILE_OFFSET)[0]
    table_at = table_address - 0x08000000
    row = image[table_at + CANONICAL_ROWS * STRIDE:
                table_at + (CANONICAL_ROWS + 1) * STRIDE]

    assert row[:2] == bytes(KEY)
    source = struct.unpack_from("<I", row, 0x2C)[0]
    assert source >= 0x08800000, "the selector word is not in expanded storage"
    root = struct.unpack_from("<I", image, source - 0x08000000)[0]
    assert root >= 0x08800000, "the root is not in expanded storage"
    slot = struct.unpack_from("<I", image, root - 0x08000000 + 0x14)[0]
    assert slot >= 0x08800000, "the new root does not name an expanded layer"
    # The plan and the build place the same objects: the plan is not a fiction.
    assert root == result.placements[0].root_address


def test_rebuilding_the_same_project_is_byte_identical(
        built, tmp_path, catalog):
    root, project, _output, _result, image = built
    again = tmp_path / "again.gba"

    build_project(project, _rom_path(), again, catalog)

    assert again.read_bytes() == image


def test_the_project_round_trips_through_save_and_reopen(project):
    write_authored_maps(project, _one())

    reopened = read_project(project).authored_maps

    assert reopened.ordered()[0].name == NAME
    assert reopened.ordered()[0].donor == DONOR
    assert reopened.ordered()[0].key == KEY


def test_a_project_that_authors_nothing_reproduces_the_canonical_image(
        tmp_path, extracted, catalog):
    import shutil

    project = tmp_path / "plain"
    shutil.copytree(extracted, project)
    output = tmp_path / "plain.gba"

    build_project(project, _rom_path(), output, catalog)

    assert output.read_bytes() == _rom_path().read_bytes()


def test_validate_reports_a_bad_donor_rather_than_a_half_applied_build(
        project, identified, profile):
    write_authored_maps(project, _one(donor=CANONICAL_ROWS))

    report = validate_project(project, _rom_path(),
                              RomProfileCatalog.load("config/roms.yaml"))

    assert not report.passed
    assert any("authored map" in problem for problem in report.problems)


def test_a_build_refuses_a_bad_donor_with_the_project_validation_family(
        project, catalog):
    write_authored_maps(project, _one(donor=CANONICAL_ROWS))

    with pytest.raises(ProjectValidationError) as refused:
        build_project(project, _rom_path(), Path(project) / "out.gba", catalog)
    assert "authored map" in str(refused.value)


# --- the door into the authored map ------------------------------------------


SOURCE = 40
#: The donor the accepted runtime route used: the map the retargeted door already
#: led to, so the arrival the record carries describes the new map's geometry.
RETARGET_DONOR = 41


def _facts(canonical, profile, document=None):
    return ma.authored_map_facts(canonical, profile, document or _one())


def _door(corpus):
    """A created transition from the source map into the authored one."""
    from tools.webfoot.formats.map_transitions import TransitionArrival
    from tools.webfoot.map_transitions import (CreatedTransitionIdentity,
                                               MapIdentity, TransitionCreation,
                                               creation_templates)

    template = creation_templates(corpus, MapIdentity(SOURCE))[0]
    return CreatedTransitionIdentity(MapIdentity(SOURCE), "to-cave"), TransitionCreation(
        identity=CreatedTransitionIdentity(MapIdentity(SOURCE), "to-cave"),
        template=template.identity,
        destination=MapIdentity(CANONICAL_ROWS),
        region=template.record.region,
        arrival=TransitionArrival(0x40, 0x40),
        facing=None,
    )


def test_the_corpus_resolves_a_project_authored_destination(
        canonical, profile):
    """The row is not in the image yet, so its key and extent come from the facts."""
    from tools.webfoot.map_transitions import MapIdentity, read_map_transitions

    plain = read_map_transitions(canonical, profile)
    assert plain.map_count == CANONICAL_ROWS

    corpus = read_map_transitions(canonical, profile,
                                  authored=_facts(canonical, profile))

    assert corpus.map_count == CANONICAL_ROWS + 1
    assert corpus.key_for(MapIdentity(CANONICAL_ROWS)) == bytes(KEY)
    # The donor's own stored extents, plus the screen the engine adds.
    donor_root = _donor_root(canonical, profile, DONOR)
    assert corpus.destination_bounds(MapIdentity(CANONICAL_ROWS)) == (
        int.from_bytes(donor_root[0x08:0x0A], "little") + 1 + 240,
        int.from_bytes(donor_root[0x0A:0x0C], "little") + 1 + 160,
    )


def test_a_destination_the_project_does_not_author_is_still_refused(
        canonical, profile):
    """Without the facts the authored index is outside the declared range."""
    from tools.webfoot.map_transitions import (MapIdentity, MapTransitionsError,
                                               read_map_transitions)

    corpus = read_map_transitions(canonical, profile)
    with pytest.raises(MapTransitionsError) as refused:
        corpus.key_for(MapIdentity(CANONICAL_ROWS))
    assert "declared map-entry range" in str(refused.value)


def test_a_created_transition_may_name_the_authored_map(project, catalog,
                                                        identified, profile,
                                                        canonical):
    from tools.webfoot.map_transitions import (MapIdentity, read_map_transitions,
                                               set_transition_creations)

    write_authored_maps(project, _one())
    corpus = read_map_transitions(canonical, profile,
                                  authored=_facts(canonical, profile))
    identity, creation = _door(corpus)

    assert set_transition_creations(project, profile, canonical,
                                    {identity: creation}) is True

    stored = read_project(project).transition_creations.edits()
    assert stored[(SOURCE, "to-cave")].destination == f"map:{CANONICAL_ROWS:04d}"


@pytest.fixture(scope="module")
def doored(tmp_path_factory, extracted, catalog, canonical, identified, profile):
    """One project that authors a map AND a door into it, built once."""
    import shutil

    from tools.webfoot.map_transitions import read_map_transitions, set_transition_creations

    root = tmp_path_factory.mktemp("map-new-door")
    project = root / "project"
    shutil.copytree(extracted, project)
    document = _one()
    write_authored_maps(project, document)
    corpus = read_map_transitions(canonical, profile,
                                  authored=_facts(canonical, profile, document))
    identity, creation = _door(corpus)
    set_transition_creations(project, profile, canonical, {identity: creation})
    output = root / "out.gba"
    result = build_project(project, _rom_path(), output, catalog)
    return root, project, output, result, output.read_bytes()


def test_the_built_image_carries_a_door_into_the_authored_map(
        doored, canonical):
    """The source map's own root names an expanded array whose new element is
    a 566-class record addressed to the authored key."""
    import struct

    _root, _project, _output, _result, image = doored
    source_record = canonical[TABLE_OFFSET + SOURCE * STRIDE:
                              TABLE_OFFSET + (SOURCE + 1) * STRIDE]
    source_word = struct.unpack_from("<I", source_record, 0x2C)[0]
    source_root = struct.unpack_from("<I", image, source_word - 0x08000000)[0]
    count = struct.unpack_from("<I", image, source_root - 0x08000000 + 0x40)[0]
    array = struct.unpack_from("<I", image, source_root - 0x08000000 + 0x44)[0]
    canonical_root = struct.unpack_from("<I", canonical, source_word - 0x08000000)[0]
    canonical_count = struct.unpack_from(
        "<I", canonical, canonical_root - 0x08000000 + 0x40)[0]

    assert count == canonical_count + 1
    assert array >= 0x08800000, "the array did not move into expanded storage"

    element = struct.unpack_from("<I", image, array - 0x08000000 + 4 * (count - 1))[0]
    assert element >= 0x08800000, "the created record is not above canonical EOF"
    record_at = element - 0x08000000
    assert struct.unpack_from("<I", image, record_at)[0] == 0x08007675
    assert image[record_at + 0x11] == KEY[0]
    assert image[record_at + 0x12] == KEY[1]
    assert struct.unpack_from("<H", image, record_at + 0x14)[0] == 0x40


def test_the_door_and_the_row_resolve_to_one_identity(doored, canonical):
    """The record's destination key is the row the table gained, at its index.

    This is the whole chain in one place: a created record names a key, the
    relocated table holds a row with that key at an index past the canonical
    count, and the row's own root is above canonical EOF.
    """
    import struct

    _root, _project, _output, _result, image = doored
    table_address = struct.unpack_from("<I", image, ma.BASE_POOL_FILE_OFFSET)[0]
    assert table_address >= 0x08800000
    table_at = table_address - 0x08000000
    assert image[table_at:table_at + CANONICAL_ROWS * STRIDE] \
        == canonical[TABLE_OFFSET:TABLE_OFFSET + CANONICAL_ROWS * STRIDE]

    # Find the row by the key the record names, the way the engine's lookup does.
    wanted = bytes(KEY)
    rows = [
        index for index in range(CANONICAL_ROWS + 1)
        if image[table_at + index * STRIDE:table_at + index * STRIDE + 2] == wanted
    ]
    assert rows == [CANONICAL_ROWS]

    row = image[table_at + CANONICAL_ROWS * STRIDE:
                table_at + (CANONICAL_ROWS + 1) * STRIDE]
    source = struct.unpack_from("<I", row, 0x2C)[0]
    root = struct.unpack_from("<I", image, source - 0x08000000)[0]
    assert root >= 0x08800000
    assert struct.unpack_from("<I", image, root - 0x08000000 + 0x14)[0] >= 0x08800000


def test_the_doored_build_is_reproducible(doored, tmp_path, catalog):
    _root, project, _output, _result, image = doored
    again = tmp_path / "again.gba"

    build_project(project, _rom_path(), again, catalog)

    assert again.read_bytes() == image


# --- the accepted runtime route: retarget an existing door -------------------


DOOR = 1


@pytest.fixture(scope="module")
def retargeted(tmp_path_factory, extracted, catalog, canonical, identified, profile):
    """A project that points map 40's own evening door at the authored map.

    The donor is the map that door already led to, so the arrival the record
    carries was measured for the geometry the new map inherits. That bundle rule
    is the one the accepted runtime run followed.
    """
    import shutil

    from tools.webfoot.map_transitions import (MapIdentity, TransitionEdit,
                                               set_transition_edits)

    root = tmp_path_factory.mktemp("map-new-retarget")
    project = root / "project"
    shutil.copytree(extracted, project)
    document = AuthoredMaps(maps={
        NAME: AuthoredMap(NAME, RETARGET_DONOR, KEY[0], KEY[1])})
    write_authored_maps(project, document)
    corpus = read_map_transitions(canonical, profile,
                                  authored=_facts(canonical, profile, document))
    door = next(
        entry.identity for entry in corpus.for_map(MapIdentity(SOURCE))
        if corpus.destination(entry.identity).index == RETARGET_DONOR
    )
    set_transition_edits(project, profile, canonical,
                         {door: TransitionEdit(destination=MapIdentity(CANONICAL_ROWS))})
    output = root / "out.gba"
    result = build_project(project, _rom_path(), output, catalog)
    return root, project, output, result, output.read_bytes(), door


def test_the_retarget_keeps_the_door_and_moves_only_its_destination(
        retargeted, canonical):
    """The record is rewritten in place: no count, no array, no new record."""
    import struct

    _root, _project, _output, _result, image, door = retargeted
    before = canonical[TABLE_OFFSET + SOURCE * STRIDE:
                       TABLE_OFFSET + (SOURCE + 1) * STRIDE]
    source_word = struct.unpack_from("<I", before, 0x2C)[0]
    root = struct.unpack_from("<I", canonical, source_word - 0x08000000)[0]
    for offset in (0x40, 0x44):
        assert (image[root - 0x08000000 + offset:root - 0x08000000 + offset + 4]
                == canonical[root - 0x08000000 + offset:
                             root - 0x08000000 + offset + 4]), (
            "a retarget must not move the connection count or the array pointer")

    corpus = read_map_transitions(canonical,
                                  RomProfileCatalog.load("config/roms.yaml").profiles[0])
    entry = corpus.entry(door)
    record = image[entry.file_offset:entry.file_offset + 24]
    assert record[0x11] == KEY[0] and record[0x12] == KEY[1]
    # The arrival pair is untouched: it was authored for the geometry the new map
    # inherits from its donor.
    original = canonical[entry.file_offset:entry.file_offset + 24]
    assert record[0x14:0x18] == original[0x14:0x18]


def test_the_retargeted_build_carries_the_authored_row(
        retargeted, canonical):
    """The row the door now names is the authored one, above canonical EOF."""
    import struct

    _root, _project, _output, _result, image, _door = retargeted
    table_address = struct.unpack_from("<I", image, ma.BASE_POOL_FILE_OFFSET)[0]
    table_at = table_address - 0x08000000
    assert image[table_at:table_at + CANONICAL_ROWS * STRIDE] \
        == canonical[TABLE_OFFSET:TABLE_OFFSET + CANONICAL_ROWS * STRIDE]
    row = image[table_at + CANONICAL_ROWS * STRIDE:
                table_at + (CANONICAL_ROWS + 1) * STRIDE]
    assert row[:2] == bytes(KEY)
    source = struct.unpack_from("<I", row, 0x2C)[0]
    root = struct.unpack_from("<I", image, source - 0x08000000)[0]
    assert root >= 0x08800000
    assert struct.unpack_from("<I", image, root - 0x08000000 + 0x14)[0] >= 0x08800000


def test_the_retargeted_build_is_reproducible(retargeted, tmp_path, catalog):
    _root, project, _output, _result, image, _door = retargeted
    again = tmp_path / "again.gba"

    build_project(project, _rom_path(), again, catalog)

    assert again.read_bytes() == image
