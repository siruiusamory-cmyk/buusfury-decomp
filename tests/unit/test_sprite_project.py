"""SPRITE-NEW-PROJECT-SURFACE-001: the narrow authored-sprite document.

This is the text layer only: what a project may state, what it must refuse, and
that writing then reading it is the same document. The build's use of it - the
planning, the allocation and the emitted image - is proved against the canonical
image in `tests/integration/test_sprite_new_project_rom.py`, because a project is
only meaningful against the image it was authored for.
"""

from __future__ import annotations

import pytest

from tools.webfoot.project.format import dump_toml
from tools.webfoot.project.model import (
    AuthoredSprite,
    AuthoredSpriteActor,
    AuthoredSpriteAnimation,
    AuthoredSprites,
    ProjectLoadError,
    ProjectValidationError,
    parse_object_template_identity,
)


def animation(name: str, sheet: str | None = None, frames: int = 2):
    return AuthoredSpriteAnimation(name=name, sheet=sheet or f"sprites/cui/{name}.png",
                                   frames=frames)


def actor(**overrides):
    values = {
        "map": "map:0102",
        "family": "map-sibling-08017da3",
        "position": (209, 580),
        "retained_raw": 0,
        "data_pointer_raw": 142104172,
        "behaviour_template": "map:0102/object:0007",
        "wander_box": (192, 544, 272, 624),
    }
    values.update(overrides)
    return AuthoredSpriteActor(**values)


def sprite(name: str = "cui", **overrides):
    values = {
        "name": name,
        "sprite_id": 307,
        "donor_sprite_id": 10,
        "free_palette_entries": (8, 9, 103, 193, 236),
        "animations": {"walk": animation("walk", frames=4), "stand": animation("stand")},
        "actor": actor(),
    }
    values.update(overrides)
    return AuthoredSprite(**values)


def test_a_document_round_trips_and_is_deterministic():
    document = AuthoredSprites({"cui": sprite()}).to_document()
    first = dump_toml(document)
    assert first == dump_toml(AuthoredSprites({"cui": sprite()}).to_document())
    reloaded = AuthoredSprites.from_document(document, "project")
    assert reloaded.to_document() == document
    assert reloaded.only().animation_names() == ("stand", "walk")


def test_animation_slot_order_is_the_names_sorted():
    """A TOML table has no order, so the project states one instead of inheriting."""
    authored = sprite()
    assert list(authored.animations) == ["walk", "stand"]
    assert [item.name for item in authored.ordered_animations()] == ["stand", "walk"]


def test_the_document_shape_is_the_documented_one(tmp_path):
    text = dump_toml(AuthoredSprites({"cui": sprite()}).to_document())
    assert "[sprite.cui]" in text
    assert "[sprite.cui.animation.stand]" in text
    assert "[sprite.cui.actor]" in text
    assert 'behaviour_template = "map:0102/object:0007"' in text


def test_only_one_sprite_may_be_authored():
    with pytest.raises(ProjectValidationError, match="exactly"):
        AuthoredSprites({"cui": sprite("cui"), "vegeta": sprite("vegeta")})


def test_a_document_declaring_two_sprites_is_refused_at_load():
    document = {
        "sprite": {"cui": sprite("cui").to_document(),
                   "vegeta": sprite("vegeta").to_document()}
    }
    with pytest.raises(ProjectValidationError, match="exactly"):
        AuthoredSprites.from_document(document, "sprites/sprites.toml")


def test_an_absent_table_is_refused():
    with pytest.raises(ProjectLoadError, match=r"missing required \[sprite\] table"):
        AuthoredSprites.from_document({}, "sprites/sprites.toml")


@pytest.mark.parametrize("name", ["Cui", "2cui", "cui/other", "", "cui.x"])
def test_a_sprite_name_is_a_durable_identity(name):
    with pytest.raises(ProjectValidationError, match="lowercase"):
        sprite(name)


def test_an_unknown_key_is_refused():
    document = AuthoredSprites({"cui": sprite()}).to_document()
    document["sprite"]["cui"]["sprite"] = 1
    with pytest.raises(ProjectLoadError, match="unknown key"):
        AuthoredSprites.from_document(document, "sprites/sprites.toml")


def test_an_unknown_actor_key_is_refused():
    document = AuthoredSprites({"cui": sprite()}).to_document()
    document["sprite"]["cui"]["actor"]["retained_04_raw"] = 0
    with pytest.raises(ProjectLoadError, match="unknown key"):
        AuthoredSprites.from_document(document, "sprites/sprites.toml")


def test_a_missing_field_is_refused():
    document = AuthoredSprites({"cui": sprite()}).to_document()
    del document["sprite"]["cui"]["donor_sprite_id"]
    with pytest.raises(ProjectLoadError, match="donor_sprite_id"):
        AuthoredSprites.from_document(document, "sprites/sprites.toml")


@pytest.mark.parametrize("sheet", [
    "/absolute/sheet.png",
    "C:/elsewhere/sheet.png",
    "sprites\\windows\\sheet.png",
    "../outside/sheet.png",
    "sprites/cui/stand.bmp",
])
def test_a_sheet_path_must_stay_inside_the_project_and_be_a_png(sheet):
    with pytest.raises(ProjectValidationError, match="sheet"):
        animation("stand", sheet=sheet)


@pytest.mark.parametrize("frames", [0, 65])
def test_frames_per_facing_is_bounded(frames):
    with pytest.raises(ProjectValidationError, match="frames per facing"):
        animation("stand", frames=frames)


def test_an_animation_name_must_be_a_durable_identity():
    with pytest.raises(ProjectValidationError, match="lowercase"):
        animation("Stand")


def test_no_animations_is_refused():
    with pytest.raises(ProjectValidationError, match="at least one animation"):
        sprite(animations={})


def test_more_animations_than_the_structure_can_state_is_refused():
    many = {f"a{index:02d}": animation(f"a{index:02d}") for index in range(24)}
    with pytest.raises(ProjectValidationError, match="counts from 1 through"):
        sprite(animations=many)


def test_a_table_key_that_disagrees_with_the_animation_name_is_refused():
    with pytest.raises(ProjectValidationError, match="does not match"):
        sprite(animations={"stand": animation("walk")})


@pytest.mark.parametrize("index", [0, 256, -1])
def test_a_free_palette_entry_outside_the_object_palette_is_refused(index):
    with pytest.raises(ProjectValidationError, match="free palette entry"):
        sprite(free_palette_entries=(index,))


def test_a_repeated_free_palette_entry_is_refused():
    with pytest.raises(ProjectValidationError, match="repeat"):
        sprite(free_palette_entries=(8, 8))


@pytest.mark.parametrize("value", [-1, 0x1_0000_0000, "0"])
def test_a_retained_word_must_be_an_unsigned_32_bit_word(value):
    with pytest.raises(ProjectValidationError, match="32-bit"):
        actor(retained_raw=value)


def test_a_template_from_another_map_is_refused():
    """The entry an actor starts from is one that actor's own map already runs."""
    with pytest.raises(ProjectValidationError, match="same map"):
        actor(behaviour_template="map:0103/object:0007")


@pytest.mark.parametrize("template", ["map:0102", "object:0007", "map:0102/placement:0007",
                                      "map:102/object:7"])
def test_a_behaviour_template_must_be_a_map_object_identity(template):
    with pytest.raises(ProjectValidationError, match="template"):
        actor(behaviour_template=template)


@pytest.mark.parametrize("map_key", ["0102", "map:102", "map:0102/placement:0000"])
def test_an_actor_map_must_be_a_map_identity(map_key):
    with pytest.raises(ProjectValidationError, match="map:NNNN"):
        actor(map=map_key)


def test_position_and_box_must_be_pixel_pairs():
    with pytest.raises(ProjectValidationError, match=r"\[x, y\]"):
        actor(position=(1,))
    with pytest.raises(ProjectValidationError, match=r"\[x1, y1, x2, y2\]"):
        actor(wander_box=(1, 2, 3))


def test_an_actor_without_its_identity_is_refused():
    with pytest.raises(ProjectValidationError, match="actor"):
        sprite(actor=None)


def test_the_loaded_position_and_box_come_back_as_tuples():
    document = AuthoredSprites({"cui": sprite()}).to_document()
    loaded = AuthoredSprites.from_document(document, "project").only()
    assert loaded.actor.position == (209, 580)
    assert loaded.actor.wander_box == (192, 544, 272, 624)
    assert loaded.free_palette_entries == (8, 9, 103, 193, 236)


def test_an_object_template_identity_parses_to_map_and_slot():
    assert parse_object_template_identity("map:0102/object:0007", "test") == (102, 7)
    with pytest.raises(ProjectValidationError, match="map:NNNN/object:IIII"):
        parse_object_template_identity("map:0102/object:7", "test")


def _bare_project(tmp_path) -> None:
    (tmp_path / "project.toml").write_text(
        "[project]\n"
        "format_version = 1\n"
        'name = "bare"\n'
        "\n"
        "[base]\n"
        'profile_id = "buus_fury_usa_rev0_01c1707f"\n'
        'game = "buus_fury"\n'
        f'sha256 = "{"0" * 64}"\n'
        "size = 8388608\n",
        encoding="utf-8", newline="\n")


def test_the_writer_round_trips_through_read_project_and_is_deterministic(tmp_path):
    from tools.webfoot.project.model import read_project, write_authored_sprites

    _bare_project(tmp_path)
    authored = AuthoredSprites({"cui": sprite()})
    path = write_authored_sprites(tmp_path, authored)
    first = path.read_bytes()
    loaded = read_project(tmp_path)
    assert loaded.sprites.to_document() == authored.to_document()
    assert loaded.sprites.only().actor.map_index == 102

    write_authored_sprites(tmp_path, loaded.sprites)
    assert path.read_bytes() == first

    write_authored_sprites(tmp_path, AuthoredSprites())
    assert not path.exists()
