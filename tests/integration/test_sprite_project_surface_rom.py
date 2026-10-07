"""SPRITE-PROJECT-SURFACE-001: the authoring surface against the canonical image.

ROM-gated and read-only. The suite skips cleanly when the private canonical image
is not configured locally, and it never writes to it: the project it authors into
is a temporary directory, and nothing here builds an image at all.

What only this file can establish is that the surface's cheap validation is the
PRODUCTION validation: the id it offers is the one the planner accepts, the donor
it admits is the donor whose envelope the composition guard measures, the template
it offers is a real object slot, and the document it writes is one `read_project`
reopens with its semantic identity intact. The full plan - the palette claim, the
allocation and the relocation census - is the build's, and the byte parity of the
document route is owned by `tests/integration/test_sprite_new_project_rom.py`.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from tests.helpers import write_truecolour_png
from tools.webfoot import sprite_project as sp
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project.model import (AuthoredSpriteAnimation, ProjectMeta,
                                         read_project, write_project)

CANONICAL_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
SPRITE_ID = 307
CHARACTER_COUNT = 297
DONOR_SPRITE_ID = 10
DONOR_CELL = 32
#: A donor whose own frames occupy more than one rect, so it proves no single
#: composition shape. Measured on the canonical image.
SPLIT_SHAPE_DONOR = 11
TEMPLATE = "map:0102/object:0007"
POSITION = (209, 580)
WANDER_BOX = (192, 544, 272, 624)
SHEET_COLOUR = (247, 8, 16)


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
def identified(canonical):
    from tools.webfoot.rom import identify_rom

    return identify_rom(_rom_path(), RomProfileCatalog.load("config/roms.yaml"))


@pytest.fixture(scope="module")
def profile(identified):
    return identified.profile_match.profile


@pytest.fixture()
def project(tmp_path, identified, canonical) -> Path:
    """A project the model reads, pinned to this image. No extraction needed."""
    write_project(
        tmp_path,
        ProjectMeta(1, identified.profile_match.profile.id,
                    identified.profile_match.profile.game, identified.hashes.sha256,
                    len(canonical), "surface-rom-test"),
        enemies=[], characters=[])
    return tmp_path


def _sheet(project: Path, *, frames: int = 2, side: int = DONOR_CELL,
           name: str = "sprites/cui/stand.png") -> str:
    path = project / name
    path.parent.mkdir(parents=True, exist_ok=True)
    write_truecolour_png(path, bytes(SHEET_COLOUR) * (side * side * frames * 4),
                         side * 4 * frames, side)
    return name


def _request(sheet: str, *, frames: int = 2,
             template: str = TEMPLATE) -> sp.AuthoredSpriteRequest:
    return sp.AuthoredSpriteRequest(
        name="cui", donor_sprite_id=DONOR_SPRITE_ID,
        animations=(AuthoredSpriteAnimation(name="stand", sheet=sheet,
                                            frames=frames),),
        free_palette_entries=(8, 9, 103), behaviour_template=template,
        position=POSITION, wander_box=WANDER_BOX)


# --- what the image offers ---------------------------------------------------


def test_the_image_offers_exactly_one_appended_identity(canonical, identified, profile):
    probe = sp.probe_sprite_authoring(canonical, identified, profile=profile)

    assert probe.sprite_id == SPRITE_ID
    assert probe.character_count == CHARACTER_COUNT
    assert probe.donor is None


def test_an_admissible_donor_reports_its_measured_envelope(canonical, identified,
                                                           profile):
    probe = sp.probe_sprite_authoring(canonical, identified, profile=profile,
                                      donor_sprite_id=DONOR_SPRITE_ID)

    assert probe.donor.width == DONOR_CELL
    assert probe.donor.height == DONOR_CELL
    assert probe.donor.piece_count == 1


def test_a_donor_that_proves_several_shapes_is_refused(canonical, identified, profile):
    with pytest.raises(sp.SpriteAuthoringError, match="several shapes"):
        sp.probe_sprite_authoring(canonical, identified, profile=profile,
                                  donor_sprite_id=SPLIT_SHAPE_DONOR)


def test_a_donor_outside_the_registry_is_refused(canonical, identified, profile):
    with pytest.raises(sp.SpriteAuthoringError, match="is entry"):
        sp.probe_sprite_authoring(canonical, identified, profile=profile,
                                  donor_sprite_id=CHARACTER_COUNT + 100)


def test_the_templates_are_real_slots_of_whole_arrays(canonical, profile):
    templates = sp.supported_actor_templates(canonical, profile)

    identities = {template.identity for template in templates}
    assert TEMPLATE in identities
    assert templates, "the canonical image offers at least one supported slot"
    for template in templates:
        assert template.family == sp.ACTOR_FAMILY
        assert template.map == f"map:{template.map_index:04d}"


def test_a_template_that_is_not_a_slot_is_refused(canonical, profile):
    with pytest.raises(sp.SpriteAuthoringError, match="does not exist"):
        sp.supported_template(canonical, profile, "map:0102/object:0099")


# --- what the surface writes -------------------------------------------------


def test_the_document_the_surface_writes_reopens_with_its_identity(
        canonical, identified, profile, project):
    sheet = _sheet(project)
    document = sp.validate_authored_sprite(canonical, identified, profile,
                                           _request(sheet), project_dir=project)

    assert sp.apply_authored_sprite(project, document) is True
    assert (project / "sprites" / "sprites.toml").is_file()

    reopened = sp.authored_sprite(project)
    assert reopened == read_project(project).sprites.only()
    assert reopened.name == "cui"
    assert reopened.sprite_id == SPRITE_ID
    assert reopened.donor_sprite_id == DONOR_SPRITE_ID
    assert reopened.actor.map == "map:0102"
    assert reopened.actor.behaviour_template == TEMPLATE
    assert reopened.actor.position == POSITION
    assert reopened.actor.wander_box == WANDER_BOX
    # The template's own carried words, taken from the image rather than invented.
    assert reopened.actor.retained_raw == 0
    assert reopened.actor.data_pointer_raw > 0


def test_writing_the_same_document_twice_is_a_no_op(canonical, identified, profile,
                                                    project):
    sheet = _sheet(project)
    document = sp.validate_authored_sprite(canonical, identified, profile,
                                           _request(sheet), project_dir=project)
    sp.apply_authored_sprite(project, document)
    first = (project / "sprites" / "sprites.toml").read_bytes()

    assert sp.apply_authored_sprite(project, document) is False
    assert (project / "sprites" / "sprites.toml").read_bytes() == first


def test_removing_the_document_leaves_the_project_loadable(canonical, identified,
                                                           profile, project):
    sheet = _sheet(project)
    document = sp.validate_authored_sprite(canonical, identified, profile,
                                           _request(sheet), project_dir=project)
    sp.apply_authored_sprite(project, document)

    assert sp.apply_authored_sprite(project, sp.AuthoredSprites()) is True
    assert sp.authored_sprite(project) is None
    assert read_project(project).sprites.is_empty()


# --- refusals the surface must not paper over --------------------------------


def test_a_cell_that_is_not_the_donors_rect_is_refused(canonical, identified,
                                                       profile, project):
    # The sheet's own width agrees with its declaration, so the file is a valid
    # sheet; its cell is simply not the shape the donor proves.
    sheet = _sheet(project, frames=2, side=16, name="sprites/cui/small.png")

    with pytest.raises(sp.SpriteAuthoringError, match="composition shape"):
        sp.validate_authored_sprite(canonical, identified, profile, _request(sheet),
                                    project_dir=project)


def test_a_sheet_that_is_not_there_is_refused(canonical, identified, profile,
                                              project):
    with pytest.raises(sp.SpriteAuthoringError, match="is not a file in this project"):
        sp.validate_authored_sprite(canonical, identified, profile,
                                    _request("sprites/cui/absent.png"),
                                    project_dir=project)


def test_a_sheet_whose_dimensions_disagree_with_its_frames_is_refused(
        canonical, identified, profile, project):
    sheet = _sheet(project)

    with pytest.raises(sp.SpriteAuthoringError, match="one row of square cells"):
        sp.validate_authored_sprite(canonical, identified, profile,
                                    _request(sheet, frames=1), project_dir=project)


def test_an_inverted_wander_box_is_refused_by_the_surface(canonical, identified,
                                                          profile, project):
    """The box is a field the surface authors, so the surface refuses it."""
    sheet = _sheet(project)
    request = _request(sheet)
    inverted = sp.AuthoredSpriteRequest(
        name=request.name, donor_sprite_id=request.donor_sprite_id,
        animations=request.animations,
        free_palette_entries=request.free_palette_entries,
        behaviour_template=request.behaviour_template, position=request.position,
        wander_box=(400, 500, 300, 600))

    with pytest.raises(sp.SpriteAuthoringError, match="inverted"):
        sp.validate_authored_sprite(canonical, identified, profile, inverted,
                                    project_dir=project)


# --- the surface's own output, built and compared to the runtime image -------


def test_the_surface_writes_the_document_the_runtime_record_ran(
        canonical, identified, profile, tmp_path):
    """The surface's own output, built and compared with the runtime document.

    The comparison is exact except for ONE field, and the exception is stated
    rather than assumed: the recorded runtime document states a
    ``data_pointer_raw`` taken from a NEIGHBOURING sibling slot of the same map,
    while the surface carries the chosen template slot's own word. The two differ
    by 16 bytes. That is why the capability is registered at `application` proof
    and the engine observation stays attached to the mechanism.

    What this proves is the application-level claim: the surface's document
    validates, builds to a valid image, authors the same identity and actor, and
    touches exactly the canonical fields and retail records the runtime case does.
    Skipped without the private sheets, exactly like the parity case itself.
    """
    import dataclasses

    from tests.integration import test_sprite_new_project_rom as parity
    from tools.webfoot.build import extract_project, validate_project
    from tools.webfoot.profile import RomProfileCatalog

    sources = parity.private_sheets()
    if sources is None:
        pytest.skip("private Cui sheets not configured locally")

    catalog = RomProfileCatalog.load("config/roms.yaml")
    rom = _rom_path()

    handwritten = tmp_path / "handwritten"
    through_surface = tmp_path / "through-surface"
    for destination in (handwritten, through_surface):
        extract_project(rom, destination, catalog, name="surface-parity",
                        graphics=False)

    parity.author_sprite(handwritten, sheets=parity.copy_sheets(handwritten, sources))
    expected = read_project(handwritten).sprites

    sheets = parity.copy_sheets(through_surface, sources)
    request = sp.AuthoredSpriteRequest(
        name="cui", donor_sprite_id=parity.DONOR_SPRITE_ID,
        animations=tuple(AuthoredSpriteAnimation(name=name,
                                                 sheet=f"sprites/cui/{name}.png",
                                                 frames=frames)
                         for name, frames in sorted(sheets.items())),
        free_palette_entries=parity.FREE_ENTRIES,
        behaviour_template=f"map:{parity.MAP_INDEX:04d}/object:{parity.DONOR_SLOT:04d}",
        position=parity.POSITION, wander_box=parity.WANDER_BOX)
    document = sp.validate_authored_sprite(canonical, identified, profile, request,
                                           project_dir=through_surface)
    sp.apply_authored_sprite(through_surface, document)

    # Everything except the one carried word, which is what the template itself
    # states rather than what the recorded document chose.
    written = document.only()
    recorded = expected.only()
    assert written.actor.data_pointer_raw == sp.supported_template(
        canonical, profile, request.behaviour_template).data_pointer_raw
    assert written.actor.data_pointer_raw != recorded.actor.data_pointer_raw
    assert dataclasses.replace(recorded, actor=dataclasses.replace(
        recorded.actor,
        data_pointer_raw=written.actor.data_pointer_raw)) == written

    report = validate_project(through_surface, rom, catalog)
    assert report.passed, report.problems
    output, manifest = parity.build(through_surface, tmp_path, "surface", catalog)
    produced = Path(output).read_bytes()
    assert len(produced) == 16 * 1024 * 1024

    entry = json.loads(Path(manifest).read_text(encoding="utf-8"))["sprite_authoring"][0]
    identity, actor = entry["identity"], entry["actor"]
    assert identity["sprite_id"] == parity.SPRITE_ID
    assert actor["map_index"] == parity.MAP_INDEX
    assert actor["array_slots"] == 11
    parity.assert_only_canonical_fields_changed(canonical, produced, profile, identity)
    parity.assert_retail_object_records_preserved(canonical, produced, profile, actor)
