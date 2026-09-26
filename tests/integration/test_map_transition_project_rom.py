"""ROM-gated proofs for authored map transitions. MAP-WARP-PROJECT-AUTHORING-001.

The claims here are the ones a synthetic image cannot settle, because they are
about a real 8 MiB image and the real project/build lifecycle:

* a semantic transition edit survives save, close and reopen, and the reopened
  project builds;
* the build rewrites exactly the bytes of the one record it names - the two
  destination-key bytes, the eight region bytes, or both - and nothing else in
  the image;
* the record's UNRESOLVED bytes, every unrelated transition record, and the roots
  and pointer arrays that reach them are byte-identical to the canonical image;
* two builds of the same saved project are byte-identical, derivative and manifest;
* a stored prior that does not match the image, an identity the image does not
  have, and a destination the profile's table does not declare are all refused;
* the canonical input is never written and is still refused as a write target.

The canonical ROM is opened read-only on every path and re-hashed afterwards. It
is never copied into the repository and no ROM-derived fixture is committed. The
whole file skips cleanly when the private image is absent.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from tools.webfoot.build import (
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.formats.map_transitions import TransitionRegion
from tools.webfoot.map_transitions import (
    MapIdentity,
    MapTransitionsError,
    TransitionEdit,
    TransitionIdentity,
    load_map_transitions,
    read_transition_edits,
    set_transition_edits,
)
from tools.webfoot.packaged import packaged_profile
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import (
    AuthoredTransition,
    ProjectValidationError,
    TransitionEdits,
    read_project,
    write_transition_edits,
)
from tools.webfoot.write import OutputPathError

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)
CATALOG = "config/roms.yaml"

#: Map 39's second record: the documented reciprocal link back to map 40, with a
#: deliberately non-square, asymmetric region - 9 wide by 105 tall, all four
#: endpoints distinct. The same record MAP-WARP-FORMAT-001 proved the format on.
MAP_39_SECOND = TransitionIdentity(MapIdentity(39), 1)
MAP_40 = MapIdentity(40)
RETAIL_REGION = TransitionRegion(first=(592, 601), second=(136, 241))
#: A second asymmetric region, chosen so that EVERY ONE of the eight encoded bytes
#: differs from the retail record's: `a` 0x0250 -> 0x0130, `b` 0x0088 -> 0x0110,
#: `c` 0x0259 -> 0x03C0, `d` 0x00F1 -> 0x0220. A region that reused a byte would
#: let a serializer that wrote only part of the positional field pass. The two
#: intervals still differ in width and no endpoint repeats, so a transposition of
#: either interval or of their ends lands a different value in at least one byte.
NEW_REGION = TransitionRegion(first=(0x0130, 0x03C0), second=(0x0110, 0x0220))
#: The record's engine-accessed extent, stated here independently of the codec.
RECORD_SIZE = 24
#: The record's UNRESOLVED bytes - class word, invariant word and the five
#: engine-read fields whose meaning this project has not measured.
UNRESOLVED_OFFSETS = (0x00, 0x04, 0x10, 0x13, 0x14, 0x16, 0x17)


def _rom_path() -> str:
    """The canonical image, or a skip. ``LOGX_CANONICAL_ROM`` overrides the path.

    A ticket worktree never carries the ignored image, so without the override
    this whole file skips there - which is how its locality, prior, determinism
    and safety claims went unexercised in a review worktree once already.
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
    if hashlib.sha256(Path(matches[0]).read_bytes()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return matches[0]


@pytest.fixture(scope="module")
def rom() -> str:
    return _rom_path()


@pytest.fixture(scope="module")
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load(CATALOG)


@pytest.fixture(scope="module")
def corpus(rom: str, catalog: RomProfileCatalog):
    return load_map_transitions(rom, catalog)


@pytest.fixture(scope="module")
def extracted(tmp_path_factory, rom: str, catalog: RomProfileCatalog) -> Path:
    """One extraction per module; each test copies it.

    Extracted without graphics, deliberately: nothing here asserts anything about
    sprite assets, and graphics extraction writes thousands of PNGs against this
    project's few dozen TOML files. Per-test copies keep a transition edit one test
    wrote from leaking into the next, which is the exact failure a shared directory
    would produce.
    """
    directory = tmp_path_factory.mktemp("extracted") / "project"
    extract_project(rom, directory, catalog, graphics=False)
    return directory


@pytest.fixture
def project(tmp_path: Path, extracted: Path) -> Path:
    directory = tmp_path / "project"
    shutil.copytree(extracted, directory)
    return directory


def offset_of(corpus, identity: TransitionIdentity = MAP_39_SECOND) -> int:
    return corpus.entry(identity).file_offset


def stage(project: Path, rom: str, edits) -> bool:
    """Persist a batch of edits the way an authoring surface would."""
    return set_transition_edits(
        project, packaged_profile(), Path(rom).read_bytes(), edits
    )


def build(project: Path, rom: str, catalog, tmp_path: Path, name: str = "out"):
    output = tmp_path / f"{name}.gba"
    result = build_project(project, rom, output, catalog)
    return result, output.read_bytes()


def differing(canonical: bytes, derivative: bytes) -> list[int]:
    return [i for i in range(len(canonical)) if canonical[i] != derivative[i]]


def a_target_whose_key_differs_in_both_bytes(corpus, identity=MAP_39_SECOND) -> MapIdentity:
    """A destination no test could satisfy by writing only one key byte."""
    current = corpus.key_for(corpus.destination(identity))
    return next(
        MapIdentity(index)
        for index in range(corpus.map_count)
        if all(
            written != original
            for written, original in zip(corpus.key_for(MapIdentity(index)), current)
        )
    )


# --- the baseline the locality claims are measured against -------------------


def test_an_unchanged_project_rebuilds_the_canonical_image(
    project: Path, rom: str, catalog, tmp_path: Path
):
    """The premise every diff below rests on: the build alone changes no byte."""
    _result, derivative = build(project, rom, catalog, tmp_path)
    assert hashlib.sha256(derivative).hexdigest() == CANONICAL_SHA256
    assert not (project / "maps" / "transitions.toml").exists()


# --- destination -------------------------------------------------------------


def test_a_destination_edit_saves_reopens_and_builds_only_the_key_bytes(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    target = a_target_whose_key_differs_in_both_bytes(corpus)
    assert stage(project, rom, {MAP_39_SECOND: TransitionEdit(destination=target)})

    # Close and reopen: the same semantic edit is there, as a prior/authored pair
    # against the map identities the engine resolves - no offset, no address.
    reopened = read_transition_edits(project).edits()[(39, 1)]
    assert reopened.prior_destination == str(MAP_40) == "map:0040"
    assert reopened.destination == target.key
    assert reopened.region is None and reopened.prior_region is None

    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    offset = offset_of(corpus)
    assert differing(canonical, derivative) == [offset + 0x11, offset + 0x12]

    assert corpus.destination(MAP_39_SECOND) == MAP_40, "the loaded corpus is unchanged"
    after = load_map_transitions_from_bytes(derivative)
    assert after.destination(MAP_39_SECOND) == target
    assert after.entry(MAP_39_SECOND).record.region == RETAIL_REGION


def test_a_region_edit_saves_reopens_and_builds_only_the_region_bytes(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    assert stage(project, rom, {MAP_39_SECOND: TransitionEdit(region=NEW_REGION)})

    reopened = read_transition_edits(project).edits()[(39, 1)]
    assert reopened.prior_region == RETAIL_REGION
    assert reopened.region == NEW_REGION
    assert reopened.destination is None and reopened.prior_destination is None

    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    offset = offset_of(corpus)
    assert differing(canonical, derivative) == list(range(offset + 0x08, offset + 0x10))

    after = load_map_transitions_from_bytes(derivative)
    record = after.entry(MAP_39_SECOND).record
    assert record.region == NEW_REGION
    assert record.to_bytes()[0x08:0x10] == NEW_REGION.to_bytes()
    # The destination pair is not authored, so it is the retail one.
    assert after.destination(MAP_39_SECOND) == MAP_40


def test_a_destination_and_a_region_together_build_only_those_ten_bytes(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    target = a_target_whose_key_differs_in_both_bytes(corpus)
    assert stage(
        project, rom,
        {MAP_39_SECOND: TransitionEdit(destination=target, region=NEW_REGION)},
    )
    reopened = read_transition_edits(project).edits()[(39, 1)]
    assert reopened.destination == target.key and reopened.prior_destination == "map:0040"
    assert reopened.region == NEW_REGION and reopened.prior_region == RETAIL_REGION

    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    offset = offset_of(corpus)
    assert differing(canonical, derivative) == sorted(
        [offset + 0x11, offset + 0x12] + list(range(offset + 0x08, offset + 0x10))
    )
    after = load_map_transitions_from_bytes(derivative)
    assert after.destination(MAP_39_SECOND) == target
    assert after.entry(MAP_39_SECOND).record.region == NEW_REGION


def load_map_transitions_from_bytes(image: bytes):
    """Read a derivative through the authority.

    A derivative is not the canonical image, so it is not *identified*; it is read
    through the authority's bytes seam under the same profile, which is exactly what
    the build itself does.
    """
    from tools.webfoot.map_transitions import read_map_transitions

    return read_map_transitions(image, packaged_profile())


# --- safety ------------------------------------------------------------------


def test_every_unrelated_transition_record_is_byte_identical_in_the_derivative(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    target = a_target_whose_key_differs_in_both_bytes(corpus)
    stage(project, rom, {MAP_39_SECOND: TransitionEdit(destination=target)})
    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()

    for entry in corpus.entries():
        if entry.identity == MAP_39_SECOND:
            continue
        span = slice(entry.file_offset, entry.file_offset + RECORD_SIZE)
        assert derivative[span] == entry.original_bytes, entry.identity
        assert canonical[span] == derivative[span], entry.identity
    # ...and nothing outside the one record moved at all.
    offset = offset_of(corpus)
    assert derivative[:offset] == canonical[:offset]
    assert derivative[offset + RECORD_SIZE :] == canonical[offset + RECORD_SIZE :]


def test_the_unresolved_bytes_of_the_edited_record_are_preserved(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    """The bytes this project has not measured are carried, never rewritten."""
    target = a_target_whose_key_differs_in_both_bytes(corpus)
    stage(
        project, rom,
        {MAP_39_SECOND: TransitionEdit(destination=target, region=NEW_REGION)},
    )
    _result, derivative = build(project, rom, catalog, tmp_path)
    canonical = Path(rom).read_bytes()
    offset = offset_of(corpus)
    for relative in UNRESOLVED_OFFSETS:
        assert derivative[offset + relative] == canonical[offset + relative], hex(relative)


def test_the_canonical_rom_is_unchanged_and_refused_as_a_write_target(
    project: Path, rom: str, catalog, tmp_path: Path
):
    before = hashlib.sha256(Path(rom).read_bytes()).hexdigest()
    stage(project, rom, {MAP_39_SECOND: TransitionEdit(region=NEW_REGION)})
    build(project, rom, catalog, tmp_path)
    after = hashlib.sha256(Path(rom).read_bytes()).hexdigest()
    assert after == before == CANONICAL_SHA256

    with pytest.raises(OutputPathError):
        build_project(project, rom, rom, catalog)


# --- no-op and determinism ---------------------------------------------------


def _no_op_project(project: Path) -> None:
    """A project that states both editable fields and their own prior values.

    Written through the project's own writer rather than the authoring API, because
    the API normalizes a pair that authors its prior away - it is not an edit. A
    hand-authored project can still state one, and the build must then emit
    nothing.
    """
    write_transition_edits(
        project,
        TransitionEdits.from_edits({
            (39, 1): AuthoredTransition(
                prior_destination="map:0040",
                destination="map:0040",
                prior_region=RETAIL_REGION,
                region=RETAIL_REGION,
            )
        }),
    )


def test_a_no_op_project_emits_no_effective_transition_change(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    _no_op_project(project)
    stored = read_project(project).transitions.edits()[(39, 1)]
    assert stored.is_noop()

    report = validate_project(project, rom, catalog)
    assert report.passed, report.problems

    result, derivative = build(project, rom, catalog, tmp_path)
    assert derivative == Path(rom).read_bytes()
    document = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert "transition_edits" not in document
    assert document["changed_byte_count"] == 0


def test_two_builds_of_the_same_project_are_byte_identical(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    target = a_target_whose_key_differs_in_both_bytes(corpus)
    stage(
        project, rom,
        {MAP_39_SECOND: TransitionEdit(destination=target, region=NEW_REGION)},
    )
    first_result, first = build(project, rom, catalog, tmp_path, name="first")
    second_result, second = build(project, rom, catalog, tmp_path, name="second")
    assert first == second
    assert hashlib.sha256(first).hexdigest() == first_result.manifest.output_sha256
    assert (
        first_result.manifest_path.read_bytes()
        == second_result.manifest_path.read_bytes()
    )


# --- provenance --------------------------------------------------------------


def test_the_manifest_records_the_semantic_identity_and_both_pairs(
    project: Path, rom: str, catalog, corpus, tmp_path: Path
):
    target = a_target_whose_key_differs_in_both_bytes(corpus)
    stage(
        project, rom,
        {MAP_39_SECOND: TransitionEdit(destination=target, region=NEW_REGION)},
    )
    result, _derivative = build(project, rom, catalog, tmp_path)
    document = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    (edit,) = document["transition_edits"]
    assert edit["identity"] == "map:0039/transition:0001"
    # The author-facing identity is the semantic one: no address anywhere in it.
    assert "0x" not in edit["identity"]
    assert edit["source_map"] == 39 and edit["index"] == 1
    assert edit["destination_changed"] and edit["region_changed"]
    assert edit["prior_destination"] == "map:0040"
    assert edit["destination"] == target.key
    assert edit["prior_region"] == [[592, 601], [136, 241]]
    assert edit["region"] == [[0x0130, 0x03C0], [0x0110, 0x0220]]

    owned = [
        change for change in document["changes"] if change["owner"] == edit["identity"]
    ]
    assert len(owned) == 1
    assert owned[0]["offset"] == edit["file_offset"]


# --- fail closed -------------------------------------------------------------


def test_a_prior_that_does_not_match_the_image_is_refused(
    project: Path, rom: str, catalog, tmp_path: Path
):
    """A project authored against a different image must not be reinterpreted."""
    write_transition_edits(
        project,
        TransitionEdits.from_edits({
            (39, 1): AuthoredTransition(
                prior_destination="map:0033", destination="map:0034"
            )
        }),
    )
    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any("authored against destination" in problem for problem in report.problems)

    output = tmp_path / "refused.gba"
    with pytest.raises(ProjectValidationError, match="authored against destination"):
        build_project(project, rom, output, catalog)
    assert not output.exists()


def test_an_identity_the_image_does_not_have_is_refused(
    project: Path, rom: str, catalog, tmp_path: Path
):
    """Map 39 has two records; naming a third must fail, not be dropped."""
    write_transition_edits(
        project,
        TransitionEdits.from_edits({
            (39, 2): AuthoredTransition(
                prior_destination="map:0040", destination="map:0038"
            )
        }),
    )
    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any(
        "map:0039/transition:0002" in problem for problem in report.problems
    ), report.problems

    output = tmp_path / "refused.gba"
    with pytest.raises(ProjectValidationError):
        build_project(project, rom, output, catalog)
    assert not output.exists()


def test_a_destination_the_table_does_not_declare_is_refused(
    project: Path, rom: str, catalog, tmp_path: Path
):
    write_transition_edits(
        project,
        TransitionEdits.from_edits({
            (39, 1): AuthoredTransition(
                prior_destination="map:0040", destination="map:0452"
            )
        }),
    )
    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any("declared map-entry range" in problem for problem in report.problems)


def test_an_invalid_region_is_refused_when_the_project_is_read(
    project: Path, rom: str, catalog, tmp_path: Path
):
    """An unordered interval never becomes an authored value in the first place."""
    path = project / "maps" / "transitions.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '[transition."map:0039".0001]\n'
        'prior_region = [[592, 601], [136, 241]]\n'
        "region = [[700, 600], [136, 241]]\n",
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectValidationError, match="low <= high"):
        read_project(project)


def test_staging_an_unknown_identity_is_refused_and_writes_nothing(
    project: Path, rom: str, catalog
):
    """The authoring API refuses an identity the image does not have."""
    image = Path(rom).read_bytes()
    with pytest.raises(MapTransitionsError) as caught:
        set_transition_edits(
            project, packaged_profile(), image,
            {TransitionIdentity(MapIdentity(39), 4): TransitionEdit(MapIdentity(40))},
        )
    assert "transition:0004" in str(caught.value)
    assert not (project / "maps" / "transitions.toml").exists()
