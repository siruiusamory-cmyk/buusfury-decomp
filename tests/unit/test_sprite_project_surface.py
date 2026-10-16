"""SPRITE-PROJECT-SURFACE-001: the supported surface for an authored sprite.

The facade that turns a surface's collected values into `sprites/sprites.toml`
through the project model's own writer. Everything here runs portably: a
synthetic project directory for the document half, and two existing synthetic
worlds for the image half - the identity fixture's fabricated registry for the
engine id and the donor check, and the attachment fixture's fabricated map table
for the behaviour templates. The full draft dry run against a real profile lives
in `tests/integration/test_sprite_project_surface_rom.py`, because
`materialize_authored_sprites` resolves its profile through the packaged catalog.
"""

from __future__ import annotations

import pytest

from tests.unit import test_sprite_attachment_authoring as attachment_fixture
from tests.unit import test_sprite_identity_authoring as identity_fixture

from tools.webfoot import sprite_project as sp
from tools.webfoot.project.model import (AuthoredSpriteAnimation, AuthoredSprites,
                                         ProjectLoadError, ProjectMeta,
                                         ProjectValidationError, read_project,
                                         write_project)
from tools.webfoot.sprite_authoring import ActorTemplate

SPRITE_ID = 307
TEMPLATE = "map:0102/object:0007"


def _project(tmp_path, name: str = "surface-test"):
    """A project directory the model itself accepts, with no sprite document."""
    write_project(
        tmp_path,
        ProjectMeta(1, "synthetic_profile", "Synthetic Game", "0" * 64, 1024, name),
        enemies=[], characters=[])
    return tmp_path


def _template(**overrides) -> ActorTemplate:
    values = dict(
        identity=TEMPLATE, map="map:0102", map_index=102, slot_index=7,
        family=sp.ACTOR_FAMILY, position=(209, 580),
        wander_box=(192, 544, 272, 624), retained_raw=0,
        data_pointer_raw=0x08727000, behaviour_entry=b"\x00" * 16)
    values.update(overrides)
    return ActorTemplate(**values)


def _request(**overrides) -> sp.AuthoredSpriteRequest:
    values = dict(
        name="cui", donor_sprite_id=10,
        animations=(AuthoredSpriteAnimation(name="stand",
                                            sheet="sprites/cui/stand.png",
                                            frames=2),),
        free_palette_entries=(8, 9), behaviour_template=TEMPLATE,
        position=(209, 580), wander_box=(192, 544, 272, 624))
    values.update(overrides)
    return sp.AuthoredSpriteRequest(**values)


def _document(**overrides) -> AuthoredSprites:
    sprite = _request(**overrides).to_sprite(template=_template(), sprite_id=SPRITE_ID)
    return AuthoredSprites(sprites={sprite.name: sprite})


# --- the document half -------------------------------------------------------


def test_apply_writes_the_document_and_reopen_keeps_its_identity(tmp_path):
    project = _project(tmp_path)
    assert sp.authored_sprite(project) is None

    assert sp.apply_authored_sprite(project, _document()) is True

    path = project / "sprites" / "sprites.toml"
    assert path.is_file()
    reopened = sp.authored_sprite(project)
    assert reopened == read_project(project).sprites.only()
    assert reopened.name == "cui"
    assert reopened.sprite_id == SPRITE_ID
    assert reopened.donor_sprite_id == 10
    assert reopened.actor.behaviour_template == TEMPLATE


def test_an_unchanged_document_is_a_no_op(tmp_path):
    project = _project(tmp_path)
    sp.apply_authored_sprite(project, _document())
    first = (project / "sprites" / "sprites.toml").read_bytes()

    assert sp.apply_authored_sprite(project, _document()) is False
    assert (project / "sprites" / "sprites.toml").read_bytes() == first


def test_an_empty_document_removes_the_file(tmp_path):
    project = _project(tmp_path)
    sp.apply_authored_sprite(project, _document())

    assert sp.apply_authored_sprite(project, AuthoredSprites()) is True
    assert not (project / "sprites" / "sprites.toml").exists()
    assert sp.authored_sprite(project) is None
    assert sp.apply_authored_sprite(project, AuthoredSprites()) is False


def test_a_directory_that_is_not_a_project_is_refused(tmp_path):
    """A reopen with a missing dependency fails closed rather than creating one."""
    with pytest.raises(ProjectLoadError, match="project directory does not exist"):
        sp.apply_authored_sprite(tmp_path / "elsewhere", _document())
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ProjectLoadError, match="project file is missing"):
        sp.authored_sprite(empty)


def test_the_actor_block_carries_the_template_and_authors_the_position():
    sprite = _request(position=(11, 22), wander_box=(1, 2, 3, 4)).to_sprite(
        template=_template(retained_raw=0xDEADBEEF,
                           data_pointer_raw=0x0872ABCD,
                           identity="map:0003/object:0001", map="map:0003"),
        sprite_id=SPRITE_ID)

    assert sprite.actor.map == "map:0003"
    assert sprite.actor.family == sp.ACTOR_FAMILY
    assert sprite.actor.behaviour_template == "map:0003/object:0001"
    assert sprite.actor.retained_raw == 0xDEADBEEF
    assert sprite.actor.data_pointer_raw == 0x0872ABCD
    assert sprite.actor.position == (11, 22)
    assert sprite.actor.wander_box == (1, 2, 3, 4)


def test_the_model_still_refuses_a_malformed_request():
    """The facade adds no leniency: the document's own rules still fail closed."""
    with pytest.raises(ProjectValidationError, match="frames per facing"):
        AuthoredSpriteAnimation(name="stand", sheet="sprites/stand.png", frames=0)
    with pytest.raises(ProjectValidationError, match="must be lowercase"):
        AuthoredSpriteAnimation(name="Stand", sheet="sprites/stand.png", frames=1)
    with pytest.raises(ProjectValidationError, match="forward slashes"):
        AuthoredSpriteAnimation(name="stand", sheet="sprites\\stand.png", frames=1)
    with pytest.raises(ProjectValidationError, match="not a .png"):
        AuthoredSpriteAnimation(name="stand", sheet="sprites/stand.bmp", frames=1)


# --- the image half: the one addressable id and the donor --------------------


def test_probe_reports_the_appended_id_and_the_donors_envelope():
    world = identity_fixture._world()
    image = world[0]
    corpus = identity_fixture._sprites(world)

    probe = sp.probe_sprite_authoring(
        image, None, donor_sprite_id=identity_fixture.DONOR_SPRITE_ID,
        corpus=corpus)

    assert probe.sprite_id == identity_fixture.NEW_SPRITE_ID
    assert probe.character_count == identity_fixture.REGISTRY_ENTRIES
    assert probe.donor.width == identity_fixture.CELL_SIDE
    assert probe.donor.height == identity_fixture.CELL_SIDE
    assert probe.donor.piece_count == 1


def test_probe_reports_no_donor_when_none_was_asked_about():
    world = identity_fixture._world()
    probe = sp.probe_sprite_authoring(world[0], None,
                                      corpus=identity_fixture._sprites(world))
    assert probe.sprite_id == identity_fixture.NEW_SPRITE_ID
    assert probe.donor is None


def test_probe_refuses_a_donor_the_registry_does_not_hold():
    world = identity_fixture._world()
    with pytest.raises(sp.SpriteAuthoringError, match="is entry"):
        sp.probe_sprite_authoring(world[0], None, donor_sprite_id=0,
                                  corpus=identity_fixture._sprites(world))


def test_probe_refuses_a_donor_that_proves_no_single_piece():
    world = identity_fixture._world(donor_pieces=2)
    with pytest.raises(sp.SpriteAuthoringError, match="holds 2 pieces"):
        sp.probe_sprite_authoring(
            world[0], None, donor_sprite_id=identity_fixture.DONOR_SPRITE_ID,
            corpus=identity_fixture._sprites(world))


# --- the image half: the behaviour templates ---------------------------------


def test_only_slots_of_a_whole_supported_array_are_offered():
    image, profile, _entry = attachment_fixture._world()

    offered = {template.identity for template in sp.supported_actor_templates(image, profile)}

    assert offered == {
        "map:0000/object:0000",
        "map:0002/object:0000",
        "map:0002/object:0001",
        "map:0002/object:0002",
    }


def test_a_map_whose_array_holds_another_family_is_not_offered():
    image, profile, _entry = attachment_fixture._world()
    damaged = bytearray(image)
    damaged[attachment_fixture.TARGET_RECORD_BASE:
            attachment_fixture.TARGET_RECORD_BASE + 4] = (0x08000000).to_bytes(4, "little")

    offered = {template.identity
               for template in sp.supported_actor_templates(bytes(damaged), profile)}

    assert offered == {"map:0000/object:0000"}


def test_a_template_reports_the_words_and_position_it_carries():
    image, profile, _entry = attachment_fixture._world()

    template = sp.supported_template(image, profile, "map:0002/object:0001")

    assert template.map == "map:0002"
    assert template.map_index == attachment_fixture.TARGET_MAP
    assert template.slot_index == 1
    assert template.family == sp.ACTOR_FAMILY
    assert template.position == (101, 200)
    # The box its own behaviour entry carries, in the family's own value width.
    assert template.wander_box == attachment_fixture.RETAIL_BOX
    assert template.retained_raw == 0
    assert template.data_pointer_raw == attachment_fixture.NEW_DATA_POINTER
    assert len(template.behaviour_entry) == attachment_fixture.FAMILY.entry_size


def test_a_template_that_does_not_exist_is_refused():
    image, profile, _entry = attachment_fixture._world()
    with pytest.raises(sp.SpriteAuthoringError, match="does not exist"):
        sp.supported_template(image, profile, "map:0002/object:0009")
    with pytest.raises(ProjectValidationError,
                       match="not a 'map:NNNN/object:IIII'"):
        sp.supported_template(image, profile, "object:0001")
