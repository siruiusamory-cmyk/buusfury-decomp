"""APPEARANCE-AUTHORING-GATE-001: the appearance table against the canonical image.

ROM-gated and read-only. The suite skips cleanly when the private canonical image
is not configured locally, and it never writes to it: every project it authors
into is a temporary directory and every image it builds is a temporary output.

What only this file can establish is that the census the plan rests on is true of
the image it is run against: the table's extent and record layout, the five
literal words that name it, the three compiled count bounds, that the canonical
records are copied rather than re-encoded, that the plan is deterministic, and
that a full build produces the image the plan describes.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
from dataclasses import replace
from pathlib import Path

import pytest

from tools.webfoot import appearance_authoring as aa
from tools.webfoot import appearances as ap
from tools.webfoot.build import ProjectValidationError, build_project, validate_project
from tools.webfoot.layout import AnchorId
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.model import (AuthoredAppearance, AuthoredAppearances,
                                         ProjectMeta, write_authored_appearances,
                                         write_project)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
CANONICAL_TABLE_SHA256 = \
    "0663af35a42c202df5411b2888b431f250c52830a5381dc3a073afdf7a1bfb8f"
CANONICAL_COUNT = 232
TABLE_OFFSET = 0x74D380
NEW_TABLE_OFFSET = 0x800000
NEW_TABLE_ADDRESS = 0x08800000
NAME = "new_face"
TEXT_INDEX = 1188
SPRITE_ID = 10
SPRITE_CEILING = 306


def _rom_path() -> Path:
    return Path(os.environ.get(
        "SPRITE_NEW_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba"))


@pytest.fixture(scope="module")
def canonical() -> bytes:
    path = _rom_path()
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def catalog():
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture(scope="module")
def identified(canonical, catalog):
    from tools.webfoot.rom import identify_rom

    return identify_rom(_rom_path(), catalog)


@pytest.fixture(scope="module")
def profile(identified):
    return identified.profile_match.profile


@pytest.fixture()
def project(tmp_path, identified, canonical) -> Path:
    write_project(
        tmp_path,
        ProjectMeta(1, identified.profile_match.profile.id,
                    identified.profile_match.profile.game, identified.hashes.sha256,
                    len(canonical), "appearance-rom-test"),
        enemies=[], characters=[])
    return tmp_path


@pytest.fixture(scope="module")
def extracted(tmp_path_factory, canonical, catalog) -> Path:
    """One extracted project, shared: extraction is the expensive half.

    A build refuses a project that does not carry the records the image has, so
    the build-level tests need the real extraction rather than a hand-written
    identity-only document. The plan-level tests above need no project at all.
    """
    from tools.webfoot.build import extract_project

    root = tmp_path_factory.mktemp("appearance-project")
    destination = root / "project"
    extract_project(_rom_path(), destination, catalog, name="appearance",
                    graphics=False)
    return destination


@pytest.fixture()
def authored(tmp_path, extracted) -> Path:
    """A private copy of the extracted project, so tests cannot see each other."""
    import shutil

    destination = tmp_path / "project"
    shutil.copytree(extracted, destination)
    return destination


def _document(*definitions: AuthoredAppearance) -> AuthoredAppearances:
    return AuthoredAppearances(appearances={item.name: item for item in definitions})


def _one(name: str = NAME, text: int = TEXT_INDEX, sprite: int = SPRITE_ID):
    return _document(AuthoredAppearance(name, text, sprite))


def _named_offsets() -> set[int]:
    """Every canonical offset this domain is allowed to change."""
    named = set()
    for offset in ap.APPEARANCE_TABLE_REFERENCE_OFFSETS:
        named.update(range(offset, offset + 4))
    named.update(ap.APPEARANCE_COUNT_OFFSETS)
    return named


# --- the storage contract ----------------------------------------------------


def test_the_table_is_232_records_at_the_declared_extent(canonical, profile):
    records = ap.read_records(canonical, profile)

    assert len(records) == CANONICAL_COUNT
    assert hashlib.sha256(ap.canonical_table(canonical, profile)).hexdigest() \
        == CANONICAL_TABLE_SHA256
    assert ap.table_offset(profile, len(canonical)) == TABLE_OFFSET
    assert len(ap.canonical_table(canonical, profile)) \
        == CANONICAL_COUNT * ap.APPEARANCE_RECORD_SIZE


def test_every_record_field_decodes_as_the_census_says(canonical, profile):
    records = ap.read_records(canonical, profile)

    assert {record.description_index - record.text_index for record in records} == {1}
    assert min(record.sprite_id for record in records) >= aa.SPRITE_ID_FLOOR
    assert max(record.sprite_id for record in records) == SPRITE_CEILING
    assert sum(1 for record in records if record.portrait_slot == 0) == 98
    assert sum(1 for record in records if record.stat_index < 0) == 88


def test_the_reference_graph_publishes_every_word_that_names_the_table(
        canonical, profile):
    """The relocation contract is measured, not asserted."""
    document = ap.reference_document(profile, canonical)
    anchor = document.anchor(AnchorId(ap.table_identity(profile)))

    assert anchor.kind == ap.APPEARANCE_TABLE_KIND
    assert anchor.relocatable is True
    references = document.inbound(anchor.identity)
    assert tuple(sorted(reference.source.value for reference in references)) \
        == tuple(sorted(ap.APPEARANCE_TABLE_REFERENCE_OFFSETS))
    expected = profile.appearances.address.raw.to_bytes(4, "little")
    for reference in references:
        assert canonical[reference.source.value:reference.source.value + 4] == expected


def test_a_word_that_no_longer_names_the_table_is_refused(canonical, profile):
    spoiled = bytearray(canonical)
    spoiled[ap.APPEARANCE_TABLE_REFERENCE_OFFSETS[0]] ^= 0x04

    with pytest.raises(ap.AppearanceError) as refused:
        ap.reference_document(profile, bytes(spoiled))

    assert "holds something else there" in str(refused.value)


# --- the plan ----------------------------------------------------------------


def test_the_plan_moves_the_whole_table_and_patches_only_what_it_names(
        canonical, identified, profile):
    materialization = aa.materialize_authored_appearances(
        canonical, identified, profile, _one())
    size = (CANONICAL_COUNT + 1) * ap.APPEARANCE_RECORD_SIZE

    assert materialization.record_count == CANONICAL_COUNT + 1
    assert materialization.table_range.start.value == NEW_TABLE_OFFSET
    assert materialization.table_range.size == size
    assert materialization.table_address == NEW_TABLE_ADDRESS
    assert materialization.records[0] == ap.read_records(canonical, profile)[0]
    assert materialization.records[CANONICAL_COUNT] == ap.AppearanceRecord(
        text_index=TEXT_INDEX, description_index=TEXT_INDEX + 1, sprite_id=SPRITE_ID,
        portrait_slot=ap.DEFAULT_PORTRAIT_SLOT, stat_index=ap.DEFAULT_STAT_INDEX)

    assert {change.offset for change in materialization.changes} \
        == set(ap.APPEARANCE_TABLE_REFERENCE_OFFSETS) \
        | set(ap.APPEARANCE_COUNT_OFFSETS) | {NEW_TABLE_OFFSET}
    block = next(change for change in materialization.changes
                 if change.offset == NEW_TABLE_OFFSET)
    assert block.new[:CANONICAL_COUNT * ap.APPEARANCE_RECORD_SIZE] \
        == ap.canonical_table(canonical, profile)
    for offset in ap.APPEARANCE_TABLE_REFERENCE_OFFSETS:
        change = next(item for item in materialization.changes if item.offset == offset)
        assert int.from_bytes(change.new, "little") == NEW_TABLE_ADDRESS
    for offset in ap.APPEARANCE_COUNT_OFFSETS:
        change = next(item for item in materialization.changes if item.offset == offset)
        assert change.old == bytes([ap.APPEARANCE_CANONICAL_COUNT])
        assert change.new == bytes([ap.APPEARANCE_CANONICAL_COUNT + 1])
    relocation = materialization.relocations[0]
    assert relocation.anchor == ap.table_identity(profile)
    assert len(relocation.references) == len(ap.APPEARANCE_TABLE_REFERENCE_OFFSETS)


def test_the_plan_is_deterministic(canonical, identified, profile):
    first = aa.materialize_authored_appearances(canonical, identified, profile, _one())
    second = aa.materialize_authored_appearances(canonical, identified, profile, _one())

    assert first.changes == second.changes
    assert first.relocations == second.relocations
    assert first.reserved == second.reserved
    assert first.table_address == second.table_address


def test_an_authored_sprite_identity_may_be_bound(canonical, identified, profile):
    """The one sprite id an authored record may name that no record names."""
    authored = aa.SPRITE_ID_FLOOR + profile.actor_sprites.character_count

    materialization = aa.materialize_authored_appearances(
        canonical, identified, profile, _one(sprite=authored),
        authored_sprite_id=authored)

    assert materialization.records[-1].sprite_id == authored
    with pytest.raises(aa.AppearanceAuthoringError):
        aa.materialize_authored_appearances(canonical, identified, profile,
                                            _one(sprite=authored))


# --- refusals ----------------------------------------------------------------


def test_a_sprite_id_the_accessor_cannot_resolve_is_refused(canonical, identified,
                                                            profile):
    for bad in (0, aa.SPRITE_ID_FLOOR - 1, SPRITE_CEILING + 1, 307):
        with pytest.raises(aa.AppearanceAuthoringError) as refused:
            aa.materialize_authored_appearances(canonical, identified, profile,
                                                _one(sprite=bad))
        assert "sprite id" in str(refused.value)


def test_a_text_index_outside_the_declared_table_is_refused(canonical, identified,
                                                            profile):
    count = profile.text_strings.count
    for bad in (count - 1, count, 2**16 - 1):
        with pytest.raises(aa.AppearanceAuthoringError) as refused:
            aa.materialize_authored_appearances(canonical, identified, profile,
                                                _one(text=bad))
        assert "text index" in str(refused.value)


def test_the_count_ceiling_is_refused_rather_than_widened(canonical, identified,
                                                          profile):
    """The bound is the seen-flag array's, and it is refused rather than widened.

    Eight appended records all set bits inside block+0xE2, the single byte after
    the engine's 232-bit array. The ninth would write block+0xE3, whose owner is
    not established, so the model states eight and the plan refuses the ninth."""
    ceiling = ap.APPEARANCE_COUNT_FLAG_CEILING - CANONICAL_COUNT
    assert ceiling == 8
    free = aa.authorable_sprite_ids(canonical, profile)
    assert len(free) >= ceiling + 1
    accepted = _document(*[AuthoredAppearance(f"a{index}", TEXT_INDEX, free[index])
                           for index in range(ceiling)])
    materialization = aa.materialize_authored_appearances(
        canonical, identified, profile, accepted)
    assert materialization.record_count == ap.APPEARANCE_COUNT_FLAG_CEILING

    with pytest.raises(ValueError):
        _document(*[AuthoredAppearance(f"a{index}", TEXT_INDEX, free[index])
                    for index in range(ceiling + 1)])


def test_a_profile_without_a_generated_expansion_fails_closed(canonical, identified,
                                                             profile):
    without = replace(profile, generated_expansion=None)

    with pytest.raises(ValueError) as refused:
        aa.materialize_authored_appearances(canonical, identified, without, _one())

    assert "generated expansion" in str(refused.value)


# --- the build ---------------------------------------------------------------


def _build(project_dir: Path, tmp_path: Path, name: str, catalog):
    output = tmp_path / f"{name}.gba"
    manifest = tmp_path / f"{name}.manifest.json"
    result = build_project(project_dir, _rom_path(), output, catalog,
                           manifest_path=manifest)
    return Path(result.output_path), Path(result.manifest_path)


def test_a_build_that_authors_nothing_reproduces_the_base_image(canonical, authored,
                                                                tmp_path, catalog):
    output, _manifest = _build(authored, tmp_path, "noop", catalog)

    assert output.read_bytes() == canonical


def test_the_build_writes_the_record_where_the_engine_looks_for_it(
        canonical, authored, tmp_path, catalog, profile):
    write_authored_appearances(authored, _one())
    output, manifest_path = _build(authored, tmp_path, "appearance", catalog)
    produced = output.read_bytes()
    size = (CANONICAL_COUNT + 1) * ap.APPEARANCE_RECORD_SIZE

    assert len(produced) == profile.generated_expansion.output_size
    table = produced[NEW_TABLE_OFFSET:NEW_TABLE_OFFSET + size]
    assert table[:CANONICAL_COUNT * ap.APPEARANCE_RECORD_SIZE] \
        == canonical[TABLE_OFFSET:TABLE_OFFSET
                     + CANONICAL_COUNT * ap.APPEARANCE_RECORD_SIZE]
    assert struct.unpack_from(
        "<HHIIi", table, CANONICAL_COUNT * ap.APPEARANCE_RECORD_SIZE) \
        == (TEXT_INDEX, TEXT_INDEX + 1, SPRITE_ID, 0, -1)
    for offset in ap.APPEARANCE_TABLE_REFERENCE_OFFSETS:
        assert struct.unpack_from("<I", produced, offset)[0] == NEW_TABLE_ADDRESS
    for offset in ap.APPEARANCE_COUNT_OFFSETS:
        assert produced[offset] == ap.APPEARANCE_CANONICAL_COUNT + 1

    # Nothing canonical moved except the fields this domain names.
    replaced = {index for index in range(len(canonical))
                if produced[index] != canonical[index]}
    assert replaced <= _named_offsets()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    relocations = [item for item in manifest["relocations"]
                   if item["anchor"] == ap.table_identity(profile)]
    assert len(relocations) == 1
    assert len(relocations[0]["references_rewritten"]) \
        == len(ap.APPEARANCE_TABLE_REFERENCE_OFFSETS)


def test_rebuilding_the_same_project_produces_the_same_image(authored, tmp_path,
                                                            catalog):
    write_authored_appearances(authored, _one())
    first, first_manifest = _build(authored, tmp_path, "first", catalog)
    second, second_manifest = _build(authored, tmp_path, "second", catalog)

    assert first.read_bytes() == second.read_bytes()
    assert first_manifest.read_bytes() == second_manifest.read_bytes()


def test_reopening_the_project_authors_the_same_definition(authored, tmp_path,
                                                          catalog, profile):
    """Create, save, reopen, rebuild: the identity survives both directions."""
    write_authored_appearances(authored, _one())
    first, _manifest = _build(authored, tmp_path, "roundtrip-a", catalog)

    from tools.webfoot.project.model import read_project

    reopened = read_project(authored).appearances.ordered()[0]
    assert reopened == AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)

    write_authored_appearances(authored, _document(reopened))
    second, _manifest = _build(authored, tmp_path, "roundtrip-b", catalog)

    assert first.read_bytes() == second.read_bytes()


def test_validate_reports_the_same_refusal_a_build_would_raise(authored, tmp_path,
                                                              catalog):
    """The cheap validation is the production rule, not a second one."""
    write_authored_appearances(authored, _one(sprite=SPRITE_CEILING + 1))

    report = validate_project(authored, _rom_path(), catalog)

    assert any("authored appearance definition" in problem
               for problem in report.problems)
    with pytest.raises(ProjectValidationError):
        _build(authored, tmp_path, "refused", catalog)

def test_a_sprite_id_a_canonical_record_selects_is_refused(canonical, identified,
                                                           profile):
    """The engine's search returns the earliest match, so an appended record that
    reuses a retail sprite id is either unreachable or a replacement."""
    used = ap.read_records(canonical, profile)[0].sprite_id
    with pytest.raises(ValueError) as refused:
        aa.new_records(profile, _one(sprite=used).ordered(),
                       canonical=ap.read_records(canonical, profile))
    assert "already" in str(refused.value)
    # and the full plan refuses it too, not only the field-level call
    with pytest.raises(ValueError) as planned:
        aa.materialize_authored_appearances(
            canonical, identified, profile,
            _document(AuthoredAppearance(NAME, TEXT_INDEX, used)))
    assert "already" in str(planned.value)


def test_the_sprite_id_the_engine_remaps_can_never_be_authored(canonical, identified,
                                                               profile):
    """At 0x0802794E the search swaps accessor(0x95) for accessor(0x92) before it
    compares anything, so a record bound to 149 can never be returned."""
    assert aa.UNMATCHABLE_SPRITE_ID == 149
    offered = aa.authorable_sprite_ids(canonical, profile)
    assert aa.UNMATCHABLE_SPRITE_ID not in offered

    with pytest.raises(ValueError):
        aa.new_records(profile, _one(sprite=aa.UNMATCHABLE_SPRITE_ID).ordered(),
                       canonical=ap.read_records(canonical, profile))


def test_the_authorable_sprite_ids_exclude_every_canonical_one(canonical, profile):
    used = {record.sprite_id for record in ap.read_records(canonical, profile)}
    offered = set(aa.authorable_sprite_ids(canonical, profile))
    assert len(offered) == 98
    assert not (offered & used)
    assert aa.UNMATCHABLE_SPRITE_ID not in offered

def test_the_roster_patch_sites_match_the_canonical_image(canonical):
    """Each stated site is checked against the image before anything is written.

    The roster object's layout lives in twenty-three compiled statements across
    five functions. Every one is pinned to the canonical bytes here, so a patch
    can only ever land on an image that is the one the census was taken from.
    """
    assert len(ap.ROSTER_PATCH_SITES) == 23
    for site in ap.ROSTER_PATCH_SITES:
        site.check(canonical)


def test_the_roster_replacements_state_the_supported_offsets(canonical):
    """The replacements decode to the offsets the grown layout needs."""
    by_role: dict[str, list] = {}
    for site in ap.ROSTER_PATCH_SITES:
        by_role.setdefault(site.role, []).append(site)

    size = by_role["object size"]
    assert len(size) == 1
    assert (size[0].replacement[0] << 5) == ap.ROSTER_OBJECT_SIZE == 0xB80

    counts = by_role["display-list count offset"]
    assert len(counts) == 4
    for site in counts:
        assert (site.replacement[0] << 2) == ap.ROSTER_SECOND_COUNT == 0x3D4

    bases = [site for site in by_role["tail base A"] if len(site.replacement) == 1]
    assert len(bases) == 4
    for site in bases:
        base = site.replacement[0] << 5
        assert base + 0x38 == ap.ROSTER_TAIL_A == 0xB58
        assert base + 0x3C == ap.ROSTER_TAIL_A + 4

    bases = [site for site in by_role["tail base B"] if len(site.replacement) == 1]
    assert len(bases) == 5
    for site in bases:
        assert (site.replacement[0] << 5) == ap.ROSTER_TAIL_B == 0xB60

    assert ap.ROSTER_SUPPORTED_COUNT == 240
    assert ap.ROSTER_CANONICAL_OBJECT_SIZE == 0xB20
    assert ap.ROSTER_CANONICAL_SECOND_COUNT == 0x3B4
    assert ap.ROSTER_CANONICAL_TAIL_A == 0xAF8


def test_the_roster_patch_sites_do_not_overlap(canonical):
    """No two statements share a byte, so the patch set is order-independent."""
    covered: set[int] = set()
    for site in ap.ROSTER_PATCH_SITES:
        span = range(site.offset, site.offset + len(site.expected))
        assert not (set(span) & covered), f"overlapping site at 0x{site.offset:06X}"
        covered.update(span)
