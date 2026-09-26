"""ROM-gated proofs for CREATED map transitions. MAP-WARP-CREATE-PROJECT-001.

The claims here are the ones a synthetic image cannot settle, because they are about
a real 8 MiB image, its real roots and arrays, and the real project/build lifecycle:

* one supported selector-1 transition that the canonical image does **not** contain
  is created on map 40 through the production path, saved, closed, reopened and
  built by the normal build;
* the root's ``+0x40`` count grows by exactly one, ``+0x44`` is re-pointed at an
  expanded array that lives **above the original EOF**, and the new record lives
  above EOF too - which is the addressability this ticket exists to prove at build
  time (runtime proof belongs to a later emulator ticket);
* no other canonical byte changes: the count byte and the array-pointer bytes are the
  only ones, so every existing record, every existing ordering, every other map, the
  canonical array and the template record are byte-identical;
* the same saved project builds the same derivative and the same manifest twice;
* the canonical image is never written and is still refused as a write target;
* every refusal the ticket names is refused, on the real image, with a named reason.

The canonical ROM is opened read-only on every path and re-hashed afterwards. It is
never copied into the repository and no ROM-derived fixture is committed. The whole
file skips cleanly when the private image is absent.
"""

from __future__ import annotations

import glob
import hashlib
import os
import shutil
from pathlib import Path

import pytest

from tools.webfoot.allocation import InsufficientSpaceError
from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.build import (
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.formats.map_transitions import (
    FACING_EAST,
    FACING_PRESERVED_MASK,
    TRANSITION_CLASS_B_RAW,
    TRANSITION_SIZE,
    MapTransitionRegionError,
    TransitionArrival,
    TransitionRegion,
)
from tools.webfoot.map_transitions import (
    ARRAY_ELEMENT_WIDTH,
    ROOT_ARRAY_OFFSET,
    ROOT_COUNT_OFFSET,
    AuthoredTransitionCreation,
    CreatedTransitionIdentity,
    MapIdentity,
    TransitionCreation,
    TransitionEdit,
    TransitionFieldError,
    TransitionIdentity,
    materialize_transition_creations,
    read_map_transitions,
    read_project_transition_creations,
    remove_transition_creation,
    set_transition_creations,
    set_transition_edits,
)
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import (
    AuthoredTransitionCreation as StoredCreation,
    ProjectLoadError,
    ProjectValidationError,
    TransitionCreations,
    read_project,
    transition_creation_identity,
    write_transition_creations,
)
from tools.webfoot.write import OutputPathError

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)
CATALOG = "config/roms.yaml"

#: The map the created transition belongs to: Grand Kai, which MAP-WARP-* already
#: proved the transition format against, and whose canonical array is packed against
#: its OWN root - so a third element written in place would overwrite the root.
SOURCE = MapIdentity(40)
RETAIL_SOURCE_COUNT = 2
#: The template: map 40's first canonical record, a 566-class one. Same map by the
#: rule the format enforces, because the bytes a creation does not author are copied
#: from it.
TEMPLATE = TransitionIdentity(SOURCE, 0)
#: A destination map 40 does NOT already lead to (its canonical destinations are 39
#: and 41), so the created connection is genuinely new. Map 435's own walkable extent
#: is 402x402 px, from the engine's own camera-clamp word.
DESTINATION = MapIdentity(435)
RETAIL_DESTINATIONS = (MapIdentity(39), MapIdentity(41))
#: A new trigger region on map 40: distinct from both canonical door rectangles, and
#: shaped like the dominant canonical pattern (low = 8k, high = 8m + 1).
NEW_REGION = TransitionRegion(first=(120, 177), second=(240, 265))
#: Map 435 has no door back to map 40, so no arrival can be DERIVED - the ticket
#: requires it to be authored. This is the centre of map 435's own door rectangle,
#: a point that map already treats as walkable.
NEW_ARRIVAL = TransitionArrival(4, 368)
NEW_NAME = "volcano-gate"
NEW_DOOR = CreatedTransitionIdentity(SOURCE, NEW_NAME)
NEW_IDENTITY = transition_creation_identity(40, NEW_NAME)


def _rom_path() -> str:
    """The canonical image, or a skip. ``LOGX_CANONICAL_ROM`` overrides the path.

    Every ``roms/*Buu*.gba`` candidate is hashed rather than the first one taken:
    this checkout also holds a warp-randomized derivative whose name sorts ahead of
    the retail image, and a first-match helper silently skips the whole suite in
    that case. A skip is only honest when no candidate is the canonical image.
    """
    override = os.environ.get("LOGX_CANONICAL_ROM")
    if override:
        path = Path(override)
        if not path.is_file():
            pytest.skip(f"LOGX_CANONICAL_ROM is not a file: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != CANONICAL_SHA256:
            pytest.skip("LOGX_CANONICAL_ROM is not the canonical image")
        return str(path)
    matches = sorted(glob.glob(os.path.join("roms", "*Buu*.gba")))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    for candidate in matches:
        if hashlib.sha256(Path(candidate).read_bytes()).hexdigest() == CANONICAL_SHA256:
            return candidate
    pytest.skip("no local Buu's Fury image is the canonical profile these offsets target")


@pytest.fixture(scope="module")
def rom() -> str:
    return _rom_path()


@pytest.fixture(scope="module")
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load(CATALOG)


@pytest.fixture(scope="module")
def corpus(rom: str, catalog: RomProfileCatalog):
    from tools.webfoot.map_transitions import load_map_transitions

    return load_map_transitions(rom, catalog)


@pytest.fixture(scope="module")
def extracted(tmp_path_factory, rom: str, catalog: RomProfileCatalog) -> Path:
    directory = tmp_path_factory.mktemp("created-transitions") / "project"
    extract_project(rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture
def project(tmp_path: Path, extracted: Path) -> Path:
    directory = tmp_path / "project"
    shutil.copytree(extracted, directory)
    return directory


def create(project: Path, rom: str, *, name: str = NEW_NAME,
           destination: MapIdentity = DESTINATION, region: TransitionRegion = NEW_REGION,
           arrival: TransitionArrival = NEW_ARRIVAL, facing: int | None = FACING_EAST,
           template: TransitionIdentity = TEMPLATE,
           source: MapIdentity = SOURCE) -> bool:
    """Persist one created transition the way an authoring surface would."""
    identity = CreatedTransitionIdentity(source, name)
    return set_transition_creations(
        project,
        packaged_profile(),
        Path(rom).read_bytes(),
        {
            identity: TransitionCreation(
                identity=identity,
                template=template,
                destination=destination,
                region=region,
                arrival=arrival,
                facing=facing,
            )
        },
    )


def build(project: Path, rom: str, catalog, tmp_path: Path, name: str = "authored"):
    output = tmp_path / f"{name}.gba"
    result = build_project(project, rom, output, catalog)
    return result, output.read_bytes()


def read(image: bytes):
    return read_map_transitions(image, packaged_profile())


def offset_of(gba_address: int) -> int:
    expansion = packaged_profile().generated_expansion
    assert expansion is not None
    return GbaRomAddress(gba_address).to_file_offset(expansion.output_size)


def u32(image: bytes, gba_address: int) -> int:
    offset = GbaRomAddress(gba_address).to_file_offset(len(image))
    return int.from_bytes(image[offset : offset + 4], "little")


def differing(canonical: bytes, derivative: bytes) -> list[int]:
    return [i for i in range(len(canonical)) if canonical[i] != derivative[i]]


def authored_creation_of(image: bytes, creation: TransitionCreation) -> AuthoredTransitionCreation:
    """The request plus the template priors measured from the image, as the SDK does."""
    template = read(image).entry(creation.template).record
    return AuthoredTransitionCreation(
        creation=creation,
        prior_facing_raw=template.byte_0x10_raw,
        prior_unresolved_raw=template.byte_0x13_raw,
    )


def request(**overrides) -> TransitionCreation:
    fields = {
        "identity": NEW_DOOR,
        "template": TEMPLATE,
        "destination": DESTINATION,
        "region": NEW_REGION,
        "arrival": NEW_ARRIVAL,
        "facing": FACING_EAST,
    }
    fields.update(overrides)
    return TransitionCreation(**fields)


# --- the baseline -------------------------------------------------------------


def test_the_canonical_map_already_has_two_transitions_that_are_not_the_new_one(
    rom: str, corpus
):
    """The premise: the created transition is genuinely absent from the array."""
    entries = corpus.for_map(SOURCE)
    assert len(entries) == RETAIL_SOURCE_COUNT
    assert {corpus.destination(entry.identity) for entry in entries} == set(
        RETAIL_DESTINATIONS
    )
    assert corpus.root_for(SOURCE).count == RETAIL_SOURCE_COUNT
    assert all(
        corpus.destination(entry.identity) != DESTINATION for entry in entries
    )
    assert NEW_IDENTITY not in {str(entry.identity) for entry in entries}


def test_the_canonical_array_is_packed_against_its_own_root(corpus):
    """Why growth needs a new span: the element after the last one IS the root."""
    root = corpus.root_for(SOURCE)
    array_end = GbaRomAddress(root.array_address).to_file_offset(8388608) + (
        ARRAY_ELEMENT_WIDTH * root.count
    )
    root_offset = GbaRomAddress(root.root_address).to_file_offset(8388608)
    assert array_end == root_offset


# --- create, save, reopen -----------------------------------------------------


def test_a_created_transition_saves_reopens_and_builds(project: Path, rom: str, catalog, tmp_path: Path):
    assert create(project, rom) is True

    # Close and reopen: the durable identity and every authored field survive, and
    # nothing address-shaped was ever written into the document.
    reopened = read_project_transition_creations(project)
    assert set(reopened) == {NEW_DOOR}
    entry = reopened[NEW_DOOR]
    assert entry.creation.identity.key == NEW_IDENTITY
    assert str(entry.creation.template) == str(TEMPLATE)
    assert entry.creation.destination == DESTINATION
    assert entry.creation.region == NEW_REGION
    assert entry.creation.arrival == NEW_ARRIVAL
    assert entry.creation.facing == FACING_EAST
    text = (project / "maps" / "transition_creations.toml").read_text(encoding="utf-8")
    assert str(TEMPLATE) in text and str(DESTINATION) in text
    assert "0x" not in text.replace("prior_unresolved_raw", "")

    report = validate_project(project, rom, catalog)
    assert report.passed, report.problems

    result, derivative = build(project, rom, catalog, tmp_path)
    assert len(derivative) == packaged_profile().generated_expansion.output_size
    manifest = result.manifest.to_json()
    assert [item["identity"] for item in manifest["transition_creations"]] == [
        NEW_IDENTITY
    ]
    creation = manifest["transition_creations"][0]
    assert creation["template"] == str(TEMPLATE)
    assert creation["index"] == RETAIL_SOURCE_COUNT
    assert creation["prior_count"] == RETAIL_SOURCE_COUNT
    assert creation["count"] == RETAIL_SOURCE_COUNT + 1
    assert creation["destination"] == str(DESTINATION)
    assert creation["arrival"] == [NEW_ARRIVAL.x, NEW_ARRIVAL.y]
    assert creation["facing"] == FACING_EAST
    assert creation["prior_unresolved_raw"] == 0
    assert {field["source"] for field in creation["record_fields"]} == {
        "authored",
        "template",
        "authored+template",
    }


def test_the_canonical_region_gains_exactly_the_count_and_the_array_pointer(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    create(project, rom)
    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    root = corpus.root_for(SOURCE)
    count_offset = GbaRomAddress(root.count_offset).to_file_offset(len(canonical))
    pointer_offset = GbaRomAddress(root.array_pointer_offset).to_file_offset(
        len(canonical)
    )
    changed = differing(canonical, derivative)
    assert changed == [
        offset
        for offset in range(count_offset, count_offset + 4)
        if canonical[offset] != derivative[offset]
    ] + [
        offset
        for offset in range(pointer_offset, pointer_offset + 4)
        if canonical[offset] != derivative[offset]
    ]
    assert u32(derivative, root.count_offset) == RETAIL_SOURCE_COUNT + 1
    assert u32(canonical, root.count_offset) == RETAIL_SOURCE_COUNT
    assert u32(derivative, root.array_pointer_offset) != root.array_address
    # The pointer bytes are a full 32-bit little-endian GBA address, nothing else.
    new_array = u32(derivative, root.array_pointer_offset)
    assert derivative[
        GbaRomAddress(root.array_pointer_offset).to_file_offset(len(canonical)):
        GbaRomAddress(root.array_pointer_offset).to_file_offset(len(canonical)) + 4
    ] == new_array.to_bytes(4, "little")


def test_the_created_record_and_the_array_live_above_the_original_eof(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    create(project, rom)
    result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    root = corpus.root_for(SOURCE)
    new_array = u32(derivative, root.array_pointer_offset)
    assert new_array >= 0x08000000 + len(canonical), "array must be above canonical EOF"
    assert new_array < 0x0A000000, "and inside the Game Pak window"
    assert offset_of(new_array) >= len(canonical)
    assert offset_of(new_array) == GbaRomAddress(new_array).to_file_offset(
        len(derivative)
    )
    # The element that names the created record decodes the same way.
    element = offset_of(new_array) + ARRAY_ELEMENT_WIDTH * RETAIL_SOURCE_COUNT
    record_address = int.from_bytes(derivative[element : element + 4], "little")
    assert record_address >= 0x08000000 + len(canonical)
    assert offset_of(record_address) >= len(canonical)
    provenance = result.manifest.to_json()["transition_creations"][0]
    assert provenance["record_address"] == record_address
    assert provenance["array_address"] == new_array
    assert provenance["expanded"] is True
    for allocation in result.manifest.to_json()["generated_allocations"]:
        assert allocation["allocated_range"]["file_offset"] >= len(canonical)
        assert allocation["allocation_class"] == "generated_expansion"
        assert allocation["allocated_rom_address"] >= 0x08000000 + len(canonical)


def test_the_derivative_enumerates_the_new_transition_after_the_canonical_ones(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    create(project, rom)
    _result, derivative = build(project, rom, catalog, tmp_path)
    after = read(derivative)
    entries = after.for_map(SOURCE)
    assert [entry.identity.index for entry in entries] == [0, 1, 2]
    created = after.entry(TransitionIdentity(SOURCE, 2))
    assert created.record.destination_key == after.key_for(DESTINATION)
    assert after.destination(created.identity) == DESTINATION
    assert created.record.region == NEW_REGION
    assert created.record.arrival == NEW_ARRIVAL
    assert created.record.facing.arrival_direction == FACING_EAST
    assert created.record.facing.gate_direction == (
        corpus.entry(TEMPLATE).record.facing.gate_direction
    )
    assert created.record.class_raw == corpus.entry(TEMPLATE).record.class_raw
    assert created.record.byte_0x13_raw == corpus.entry(TEMPLATE).record.byte_0x13_raw
    assert {after.destination(entry.identity) for entry in entries} == set(
        RETAIL_DESTINATIONS
    ) | {DESTINATION}


def test_every_canonical_record_keeps_its_bytes_and_its_address(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    create(project, rom)
    _result, derivative = build(project, rom, catalog, tmp_path)
    after = read(derivative)
    for entry in corpus.entries():
        assert after.entry(entry.identity).record == entry.record
        assert after.entry(entry.identity).record_address == entry.record_address
    # The template is where it was, byte for byte, and unchanged.
    template_before = corpus.entry(TEMPLATE)
    template_after = after.entry(TEMPLATE)
    assert template_after.record_address == template_before.record_address
    assert template_after.record == template_before.record
    canonical = Path(rom).read_bytes()
    offset = GbaRomAddress(template_before.record_address).to_file_offset(len(canonical))
    assert derivative[offset : offset + TRANSITION_SIZE] == canonical[
        offset : offset + TRANSITION_SIZE
    ]


def test_an_unrelated_map_is_byte_identical(project: Path, rom: str, catalog, tmp_path: Path):
    """Map 39 is a neighbour Grand Kai links to; nothing about it may move."""
    create(project, rom)
    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    after = read(derivative)
    before_map_39 = read(canonical)
    for entry in before_map_39.for_map(MapIdentity(39)):
        other = after.entry(entry.identity)
        assert other.record == entry.record
        assert other.record_address == entry.record_address
    for identity in (MapIdentity(39), MapIdentity(41), MapIdentity(435)):
        assert after.root_for(identity) == before_map_39.root_for(identity)


def test_the_canonical_array_is_left_in_place_untouched(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    create(project, rom)
    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    root = corpus.root_for(SOURCE)
    offset = GbaRomAddress(root.array_address).to_file_offset(len(canonical))
    size = ARRAY_ELEMENT_WIDTH * RETAIL_SOURCE_COUNT
    assert derivative[offset : offset + size] == canonical[offset : offset + size]
    new_array = u32(derivative, root.array_pointer_offset)
    assert derivative[offset_of(new_array) : offset_of(new_array) + size] == canonical[
        offset : offset + size
    ]


# --- the root pointer encoding, measured over the whole corpus ----------------


def test_every_canonical_root_pointer_and_array_element_is_a_full_gba_address(corpus):
    """The encoding the expanded case reuses, censused rather than assumed."""
    seen = 0
    for index in range(corpus.map_count):
        root = corpus.root_for(MapIdentity(index))
        assert root.root_address & 0x08000000
        if root.count:
            assert root.array_address & 0x08000000
            assert root.array_address % 4 == 0
        for element in range(root.count):
            address = root.array_address + element * ARRAY_ELEMENT_WIDTH
            pointer = None
            for entry in corpus.for_map(MapIdentity(index)):
                if entry.element_address == address:
                    pointer = entry.record_address
                    break
            assert pointer is not None
            assert pointer & 0x08000000
            assert pointer % 4 == 0
            seen += 1
    assert seen == corpus.record_count


# --- determinism and safety ---------------------------------------------------


def test_two_builds_of_the_same_saved_project_are_identical(
    project: Path, rom: str, catalog, tmp_path: Path
):
    create(project, rom)
    first_result, first = build(project, rom, catalog, tmp_path, "one")
    second_result, second = build(project, rom, catalog, tmp_path, "two")
    assert first == second
    assert first_result.manifest.dumps() == second_result.manifest.dumps()
    assert first_result.output_path.read_bytes() == first


def test_the_canonical_input_is_never_written_and_is_still_refused(
    project: Path, rom: str, catalog, tmp_path: Path
):
    before = hashlib.sha256(Path(rom).read_bytes()).hexdigest()
    create(project, rom)
    build(project, rom, catalog, tmp_path)
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == before == CANONICAL_SHA256
    with pytest.raises(OutputPathError):
        build_project(project, rom, rom, catalog)
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == CANONICAL_SHA256


def test_removing_the_creation_restores_the_canonical_bytes(
    project: Path, rom: str, catalog, tmp_path: Path
):
    create(project, rom)
    assert remove_transition_creation(project, NEW_DOOR) is True
    _result, derivative = build(project, rom, catalog, tmp_path)
    assert hashlib.sha256(derivative).hexdigest() == CANONICAL_SHA256


# --- negative tests -----------------------------------------------------------


def test_an_identity_outside_the_map_table_is_refused(project: Path, rom: str):
    with pytest.raises(TransitionFieldError, match="declared map-entry range"):
        create(project, rom, source=MapIdentity(452))
    assert not (project / "maps" / "transition_creations.toml").exists()


def test_a_destination_the_table_does_not_declare_is_refused(project: Path, rom: str):
    with pytest.raises(TransitionFieldError):
        create(project, rom, destination=MapIdentity(452))
    assert not (project / "maps" / "transition_creations.toml").exists()


def test_a_169_class_template_is_refused(project: Path, rom: str):
    """Map 39's first record is the 169 class, whose pair is a scene delta."""
    with pytest.raises(TransitionFieldError, match="scene-relative delta"):
        create(
            project,
            rom,
            source=MapIdentity(39),
            template=TransitionIdentity(MapIdentity(39), 0),
        )
    assert not (project / "maps" / "transition_creations.toml").exists()


def test_a_template_from_another_map_is_refused(project: Path, rom: str):
    with pytest.raises(TransitionFieldError, match="same source map"):
        create(project, rom, template=TransitionIdentity(MapIdentity(39), 1))
    assert not (project / "maps" / "transition_creations.toml").exists()


def test_an_arrival_off_the_destination_map_is_refused(project: Path, rom: str):
    with pytest.raises(TransitionFieldError, match="off the map"):
        create(project, rom, arrival=TransitionArrival(9000, 9000))
    assert not (project / "maps" / "transition_creations.toml").exists()


@pytest.mark.parametrize("facing", [4, 9, 255, -1])
def test_an_invalid_facing_is_refused(facing, project: Path, rom: str):
    with pytest.raises(TransitionFieldError):
        create(project, rom, facing=facing)


def test_an_invalid_trigger_region_never_becomes_a_creation(project: Path, rom: str):
    with pytest.raises(MapTransitionRegionError):
        TransitionRegion(first=(700, 600), second=(136, 241))


def test_the_allocator_refuses_when_no_expansion_is_authorized(rom: str):
    """`EXPANDED_ONLY` fails closed rather than spending canonical space."""
    from dataclasses import replace as dataclasses_replace

    image = Path(rom).read_bytes()
    profile = dataclasses_replace(packaged_profile(), generated_expansion=None)
    with pytest.raises(InsufficientSpaceError):
        materialize_transition_creations(
            image, {NEW_DOOR: authored_creation_of(image, request())}, profile=profile
        )


def test_a_creation_that_would_alias_its_template_is_refused(project: Path, rom: str):
    image = Path(rom).read_bytes()
    template = read(image).entry(TEMPLATE)
    with pytest.raises(TransitionFieldError, match="byte-identical"):
        create(
            project,
            rom,
            region=template.record.region,
            destination=MapIdentity(39),
            arrival=TransitionArrival(599, 196),
            facing=None,
        )
    assert not (project / "maps" / "transition_creations.toml").exists()


def test_a_drifted_template_prior_is_refused(project: Path, rom: str, catalog):
    """A document authored against a different template byte cannot be applied."""
    write_transition_creations(
        project,
        TransitionCreations.from_edits({
            (40, NEW_NAME): StoredCreation(
                source=str(SOURCE),
                name=NEW_NAME,
                template=str(TEMPLATE),
                destination=str(DESTINATION),
                region=NEW_REGION,
                arrival=(NEW_ARRIVAL.x, NEW_ARRIVAL.y),
                prior_facing_raw=0x00,
                prior_unresolved_raw=0,
                facing=FACING_EAST,
            )
        }),
    )
    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any("+0x10" in problem for problem in report.problems), report.problems


def test_a_malformed_creation_document_is_refused_not_dropped(project: Path, rom: str):
    path = project / "maps" / "transition_creations.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '[creation."map:0040"."volcano-gate"]\n'
        'template = "map:0040/transition:0000"\n'
        'destination = "map:0435"\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError):
        read_project(project)
    output = project.parent / "refused.gba"
    with pytest.raises(ProjectLoadError):
        build_project(project, rom, output, catalog)
    assert not output.exists(), "a malformed creation must never be silently ignored"


def test_a_duplicate_authored_identity_is_refused():
    """One name, one creation: a table that yields it twice is refused.

    TOML itself refuses a repeated key, so this is the document model's own guard
    against a mapping that reached it some other way - and it is the branch that
    keeps "two creations, one identity" from becoming two records at two indices.
    """
    entry = StoredCreation(
        source=str(SOURCE),
        name=NEW_NAME,
        template=str(TEMPLATE),
        destination=str(DESTINATION),
        region=NEW_REGION,
        arrival=(NEW_ARRIVAL.x, NEW_ARRIVAL.y),
        prior_facing_raw=0x02,
        prior_unresolved_raw=0,
        facing=FACING_EAST,
    ).to_document()

    class _Duplicated(dict):
        def items(self):  # pragma: no cover - the point is the duplicate, not this
            return [(NEW_NAME, entry), (NEW_NAME, entry)]

    with pytest.raises(ProjectLoadError, match="twice"):
        TransitionCreations.from_document(
            {"creation": {"map:0040": _Duplicated()}}, "x"
        )


def test_a_repeated_key_in_the_creation_file_is_a_format_error(project: Path):
    path = project / "maps" / "transition_creations.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '[creation."map:0040".volcano-gate]\n'
        'template = "map:0040/transition:0000"\n'
        'destination = "map:0435"\n'
        'region = [[120, 177], [240, 265]]\n'
        'arrival = [4, 368]\n'
        'prior_facing_raw = 2\n'
        'prior_unresolved_raw = 0\n'
        "\n"
        '[creation."map:0040".volcano-gate]\n'
        'template = "map:0040/transition:0000"\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError):
        read_project(project)


def test_the_template_is_not_mutated_by_the_creation_and_vice_versa(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    """Independence in both directions, over one build that does both."""
    edited_region = TransitionRegion(first=(0, 17), second=(112, 169))
    assert set_transition_edits(
        project,
        packaged_profile(),
        Path(rom).read_bytes(),
        {TEMPLATE: TransitionEdit(region=edited_region)},
    )
    create(project, rom)
    _result, derivative = build(project, rom, catalog, tmp_path)
    after = read(derivative)
    # The template carries the authored edit...
    assert after.entry(TEMPLATE).record.region == edited_region
    # ...and the created record carries its own, composed from the canonical template.
    created = after.entry(TransitionIdentity(SOURCE, 2))
    assert created.record.region == NEW_REGION
    assert created.record.region != edited_region
    assert created.record_address != after.entry(TEMPLATE).record_address
    # The created record kept the CANONICAL template's unresolved bytes, not the
    # edited record's - an edit never touches them.
    assert created.record.byte_0x13_raw == corpus.entry(TEMPLATE).record.byte_0x13_raw
    assert created.record.facing.gate_direction == (
        corpus.entry(TEMPLATE).record.facing.gate_direction
    )
