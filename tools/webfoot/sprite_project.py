"""The supported product path for a project's authored actor sprite.

SPRITE-PROJECT-SURFACE-001. `sprites/sprites.toml` is created, replaced and
removed here and nowhere else: before this module the only caller of
`project.model.write_authored_sprites` anywhere in the tree was a unit test, so
the document was authorable only by hand.

This module owns no format and no plan of its own. It resolves the semantic
values a surface collects against the verified image, builds the document the
project model already defines, and writes it through the model's own writer. A
build then plans that document exactly as it did before this module existed.

The shape is the one the other authoring domains give their surfaces
(`dialogue.py`, `map_chunk.py`): validate, read the project once, merge, write one
file, and report whether anything changed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .project.model import (AuthoredSprite, AuthoredSpriteActor,
                            AuthoredSpriteAnimation, AuthoredSprites,
                            read_project, write_authored_sprites)
from .sprite_attachment import (FAMILY_MAP_SIBLING, SpriteAttachmentError,
                                supported_family)
from .sprite_authoring import (ActorTemplate, SpriteAuthoringError,
                               actor_template, actor_templates,
                               read_source_sheet)
from .sprite_identity import (AnimationSource, DonorEnvelope,
                              SpriteIdentityError, probe_new_sprite_identity,
                              require_cell_geometry)

#: The one object-record family this write path authors. The document states it
#: rather than assuming it because the statement is the check that keeps an
#: unmodelled family out (`sprite_attachment.SUPPORTED_FAMILIES`).
ACTOR_FAMILY = FAMILY_MAP_SIBLING


@dataclass(frozen=True, slots=True)
class SpriteAuthoringProbe:
    """What the open image can still offer, before anything is planned or written.

    ``sprite_id`` is the one engine id a grown registry can address, and ``donor``
    is the requested donor's measured envelope, or None when no donor was asked
    about. A donor this write path cannot copy raises the planner's own refusal
    rather than appearing here as a weaker value.
    """

    sprite_id: int
    character_count: int
    donor: DonorEnvelope | None = None


@dataclass(frozen=True, slots=True)
class AuthoredSpriteRequest:
    """One new identity, as a surface collects it.

    Only what an author actually decides. The engine id, the object family and the
    two carried header words are deliberately NOT here: the first is fixed by the
    image, the second has one supported value, and the third pair is read from the
    chosen template slot instead of being invented by a caller.
    """

    name: str
    donor_sprite_id: int
    animations: tuple[AuthoredSpriteAnimation, ...]
    free_palette_entries: tuple[int, ...]
    behaviour_template: str
    position: tuple[int, int]
    wander_box: tuple[int, int, int, int]

    def to_sprite(self, *, template: ActorTemplate, sprite_id: int) -> AuthoredSprite:
        """The document record, with every carried field taken from the template."""
        return AuthoredSprite(
            name=self.name,
            sprite_id=sprite_id,
            donor_sprite_id=self.donor_sprite_id,
            free_palette_entries=tuple(self.free_palette_entries),
            animations={animation.name: animation for animation in self.animations},
            actor=AuthoredSpriteActor(
                map=template.map,
                family=template.family,
                position=tuple(self.position),
                retained_raw=template.retained_raw,
                data_pointer_raw=template.data_pointer_raw,
                behaviour_template=template.identity,
                wander_box=tuple(self.wander_box),
            ),
        )


# --- reading ----------------------------------------------------------------


def authored_sprite(project_dir: str | Path) -> AuthoredSprite | None:
    """The project's authored identity, or None when it authors none."""
    sprites = read_project(project_dir).sprites
    return None if sprites.is_empty() else sprites.only()


def probe_sprite_authoring(
    image: bytes,
    identification,
    *,
    donor_sprite_id: int | None = None,
    profile=None,
    corpus=None,
) -> SpriteAuthoringProbe:
    """The id this image offers, and whether one donor is admissible.

    The engine id is fixed by the image and the donor check is the planner's own,
    so a surface that calls this cannot offer a value the build would refuse. The
    caller's already-resolved ``profile`` avoids re-deriving it, and no decoded
    corpus is needed unless the caller has none.
    """
    try:
        probe = probe_new_sprite_identity(image, identification,
                                          donor_sprite_id=donor_sprite_id,
                                          profile=profile, sprites=corpus)
    except (SpriteIdentityError, SpriteAttachmentError) as exc:
        raise SpriteAuthoringError(str(exc)) from exc
    return SpriteAuthoringProbe(sprite_id=probe.sprite_id,
                                character_count=probe.character_count,
                                donor=probe.donor)


def supported_actor_templates(image: bytes, profile) -> tuple[ActorTemplate, ...]:
    """Every object-array slot an authored actor can start from."""
    try:
        return actor_templates(image, profile, supported_family(ACTOR_FAMILY))
    except (SpriteIdentityError, SpriteAttachmentError) as exc:
        raise SpriteAuthoringError(str(exc)) from exc


def supported_template(image: bytes, profile, identity: str) -> ActorTemplate:
    """One template identity, resolved, or the refusal that names why not."""
    try:
        return actor_template(image, profile, supported_family(ACTOR_FAMILY), identity)
    except (SpriteIdentityError, SpriteAttachmentError) as exc:
        raise SpriteAuthoringError(str(exc)) from exc


# --- writing ----------------------------------------------------------------


def validate_authored_sprite(
    image: bytes,
    identification,
    profile,
    request: AuthoredSpriteRequest,
    *,
    project_dir: str | Path,
) -> AuthoredSprites:
    """The field-level half of the plan, and the document to write.

    Every refusal that precedes the registry runs here: the model's own validation,
    the donor probe, the planner's sheet reader and the planner's cell-geometry
    guard. A draft that returns from this has no field the planner refuses on
    sight, and the surface can answer between a click and its own repaint.

    The REST of the plan is the build's: the palette claim checked against the
    decoded actor-sprite graphics, the allocation and the relocation census.
    Measured on the canonical image a full plan takes about four minutes, which no
    dialog can spend, so `webfoot validate` is where that runs and it reports the
    same refusals with the same text.
    """
    try:
        probe = probe_new_sprite_identity(image, identification,
                                          donor_sprite_id=request.donor_sprite_id,
                                          profile=profile)
        template = actor_template(image, profile,
                                  supported_family(ACTOR_FAMILY),
                                  request.behaviour_template)
        sprite = request.to_sprite(template=template, sprite_id=probe.sprite_id)
        sprites = AuthoredSprites(sprites={sprite.name: sprite})
        envelope = probe.donor
        for animation in request.animations:
            sheet = read_source_sheet(project_dir, animation,
                                      where=f"sprite {sprite.name!r}")
            require_cell_geometry(AnimationSource(name=animation.name, sheet=sheet),
                                  envelope)
    except (SpriteIdentityError, SpriteAttachmentError) as exc:
        raise SpriteAuthoringError(str(exc)) from exc
    return sprites


def apply_authored_sprite(project_dir: str | Path,
                          sprites: AuthoredSprites) -> bool:
    """Write the authored-sprite document, or remove it when it is empty.

    The ONE write path for this document. Returns whether the project changed, so
    a surface can leave the project revision and the build state alone on a no-op.
    One file is written and nothing else in the project is touched.
    """
    committed = read_project(project_dir).sprites
    if committed == sprites:
        return False
    write_authored_sprites(project_dir, sprites)
    return True
