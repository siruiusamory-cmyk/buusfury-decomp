"""Build the authored actor-sprite domain: identity first, then its actor.

SPRITE-NEW-PROJECT-SURFACE-001. This module is the ONE place a project's
``sprites/sprites.toml`` becomes a write plan. It owns no binary format of its
own: it resolves the document's semantic values against the verified image,
calls the two production planners this repository already ships, and threads the
result into the shape every other build domain returns.

The two planners run in a stated order, and the order is the point:

1. :func:`webfoot.sprite_identity.plan_new_sprite_identity` authors the identity
   - the grown character registry, the new structure, its animation and frame
   records, the packed containers and the object-palette entries the art needs -
   and places all of it above canonical EOF;
2. its reserved spans are handed to
   :func:`webfoot.sprite_attachment.plan_new_map_actor` as the build-scoped
   reservation set, so the appended object record and the re-emitted object array
   can only land clear of the identity;
3. both change lists merge into the ONE plan ``webfoot.build`` forms.

Nothing here re-implements either planner, and nothing here is a second build
path: ``read_project`` produced the document, and ``plan_changes`` and
``emit_image`` apply the result exactly as they do for stats, text or maps.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import capability
from .formats import map_entry as me
from .formats import map_placements as mp
from .formats import rgb_png
from .formats import sprite_graphics as sg
from .formats.indexed_png import PngError
from .project.model import (
    DEFAULT_SHEET_TRANSPARENT_COLOUR,
    AuthoredSprite,
    AuthoredSprites,
    parse_object_template_identity,
)
from .sprite_attachment import (
    AuthoredMapActor,
    NewMapActor,
    WanderBox,
    plan_new_map_actor,
    supported_family,
)
from .sprite_identity import (
    AnimationSource,
    AuthoredIdentity,
    NewSpriteIdentity,
    SourceSheet,
    plan_new_sprite_identity,
)
from .write import (ByteChange, GeneratedAllocationProvenance,
                    RelocationProvenance, SpriteAuthoringProvenance)


class SpriteAuthoringError(ValueError):
    """An authored sprite document this image cannot be built from."""


class SpriteAuthoringProfileError(SpriteAuthoringError,
                                  capability.CapabilityError):
    """The verified profile does not authorise this domain at all."""


@dataclass(frozen=True, slots=True)
class AuthoredSpriteMaterialization:
    """Everything the authored-sprite domain contributes to the merged plan.

    The four plan fields are the shape every authoring domain returns, so a
    caller threads them into :func:`webfoot.write.plan_changes` unchanged.
    ``identity`` and ``actor`` are this domain's own description of what it laid
    out, addresses included.
    """

    identity: AuthoredIdentity
    actor: AuthoredMapActor
    changes: tuple[ByteChange, ...] = ()
    reserved: tuple = ()
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    relocations: tuple[RelocationProvenance, ...] = ()

    def provenance(self) -> SpriteAuthoringProvenance:
        """The build manifest's record of what was authored, and where it landed."""
        return SpriteAuthoringProvenance(identity=self.identity.to_json(),
                                         actor=self.actor.to_json())


# --- reading what the project authored ---------------------------------------


def read_source_sheet(
    project_dir: str | Path,
    animation,
    *,
    where: object,
    transparent_colour: tuple[int, int, int] = DEFAULT_SHEET_TRANSPARENT_COLOUR,
) -> SourceSheet:
    """One project sheet PNG as the planner's own :class:`SourceSheet`.

    The sheet is a single row of square cells, four facing groups of equal frame
    counts, which is the layout the identity's own cell index describes. The
    declared frame count and the file's dimensions have to agree: the width
    states the same number, so a disagreement is refused rather than resolved by
    preferring one of them.

    An 8-bit RGBA sheet may state its holes in the alpha channel. A hole is a
    fully transparent pixel and becomes the sheet's transparent colour, which is
    what the planner maps to palette index 0; a partly transparent pixel is
    refused, because an indexed sprite pixel has no way to carry a fraction of a
    colour.
    """
    path = Path(project_dir) / animation.sheet
    if not path.is_file():
        raise SpriteAuthoringError(
            f"{where}: sheet {animation.sheet!r} is not a file in this project"
        )
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SpriteAuthoringError(f"{where}: cannot read {animation.sheet}: {exc}") from exc
    try:
        rgb, width, height, alpha = rgb_png.decode_truecolour(data)
    except PngError as exc:
        raise SpriteAuthoringError(f"{where}: {animation.sheet}: {exc}") from exc

    expected = animation.frames * sg.DIRECTION_COUNT * height
    if width != expected:
        raise SpriteAuthoringError(
            f"{where}: {animation.sheet} is {width}x{height}; {animation.frames} "
            f"frames per facing on four facings is one row of square cells "
            f"{expected} pixels wide"
        )
    if alpha is not None and any(value not in (0, 255) for value in alpha):
        raise SpriteAuthoringError(
            f"{where}: {animation.sheet} has a partly transparent pixel; a sprite "
            "pixel is one palette index, so a sheet states each pixel as opaque or "
            "as a hole"
        )
    # The planner reads cell ``c`` from pixel ``c * cell_width * cell_height``, so
    # the sheet's own cells are gathered here into that order. The file lays its
    # cells out in one row, so a cell is a column block of that row and the whole
    # image's row-major bytes are NOT the order a cell index describes.
    cells = animation.frames * sg.DIRECTION_COUNT
    pixels = bytearray()
    for index in range(cells):
        for y in range(height):
            row = y * width + index * height
            for x in range(height):
                at = 3 * (row + x)
                if alpha is not None and alpha[row + x] == 0:
                    pixels += bytes(transparent_colour)
                else:
                    pixels += rgb[at : at + 3]
    return SourceSheet(frames_per_direction=animation.frames, cell_width=height,
                       cell_height=height, pixels=bytes(pixels),
                       transparent_colour=transparent_colour)


def behaviour_template_entry(image: bytes, profile, family, template: str) -> bytes:
    """The inline behaviour entry of one existing object array slot.

    The template is named by map and slot rather than by address, and the slot is
    resolved against the canonical image here. Its record's own first word has to
    be the family this build writes and its entry has to lead with that family's
    class word: an entry lifted from a record the engine dispatches differently
    would install a behaviour this planner does not model. Nothing is inferred
    from the entry beyond that - the bytes are copied verbatim and the planner
    then writes the authored wander box into them.
    """
    map_index, slot_index = parse_object_template_identity(template, "behaviour template")
    table = profile.map_entries
    if table is None:
        raise SpriteAuthoringError(
            f"profile {profile.id!r} declares no map-entry table, so no object array "
            "slot can be named"
        )
    entry_at = table.address.to_file_offset(profile.size) + map_index * table.record_size
    if entry_at + me.MAP_ENTRY_SIZE > len(image):
        raise SpriteAuthoringError(
            f"behaviour template {template}: map {map_index}'s record runs past the image"
        )
    record = me.MapEntry.from_bytes(image[entry_at:entry_at + me.MAP_ENTRY_SIZE])
    count = record.trigger_count_raw
    if slot_index >= count:
        raise SpriteAuthoringError(
            f"behaviour template {template}: map {map_index} declares {count} object "
            f"slot(s), so slot {slot_index} does not exist"
        )
    try:
        array_at = _rom_address(record.scripts_pointer_raw, len(image))
        slots = mp.iter_object_slots(image, array_at, count)
    except mp.MapPlacementError as exc:
        raise SpriteAuthoringError(
            f"behaviour template {template}: map {map_index}'s object array: {exc}"
        ) from exc
    slot = slots[slot_index]
    if slot.target_offset is None:
        raise SpriteAuthoringError(
            f"behaviour template {template}: slot {slot_index} points outside the image"
        )
    if slot.family_raw != family.factory_raw:
        raise SpriteAuthoringError(
            f"behaviour template {template}: slot {slot_index} is family "
            f"0x{(slot.family_raw or 0):08X}, not the supported family "
            f"0x{family.factory_raw:08X}"
        )
    at = slot.target_offset + family.entry_inline_offset
    entry = image[at:at + family.entry_size]
    if len(entry) != family.entry_size:
        raise SpriteAuthoringError(
            f"behaviour template {template}: the behaviour entry runs past the image"
        )
    class_word = int.from_bytes(entry[family.entry_class_offset:
                                      family.entry_class_offset + 4], "little")
    if class_word != family.entry_class_raw:
        raise SpriteAuthoringError(
            f"behaviour template {template}: the entry leads with "
            f"0x{class_word:08X}, not the family's class word "
            f"0x{family.entry_class_raw:08X}"
        )
    return entry


def _rom_address(word: int, image_size: int) -> int:
    """A data word's file offset, refusing anything outside the image."""
    from .binary import GbaRomAddress, BinaryAddressError

    try:
        return GbaRomAddress(word).to_file_offset(image_size)
    except BinaryAddressError as exc:
        raise SpriteAuthoringError(f"0x{word:08X} is not an address in this image: "
                                   f"{exc}") from exc


def actor_request(image: bytes, profile, sprite: AuthoredSprite) -> NewMapActor:
    """The attachment planner's own request, resolved from the document."""
    actor = sprite.actor
    family = supported_family(actor.family)
    entry = behaviour_template_entry(image, profile, family, actor.behaviour_template)
    return NewMapActor(
        map_index=actor.map_index,
        family=family.name,
        sprite_id=sprite.sprite_id,
        position=actor.position,
        retained_04_raw=actor.retained_raw,
        data_pointer_raw=actor.data_pointer_raw,
        behaviour_entry=entry,
        wander_box=WanderBox(*actor.wander_box),
    )


def identity_request(
    project_dir: str | Path, sprite: AuthoredSprite
) -> NewSpriteIdentity:
    """The identity planner's own request, resolved from the document."""
    animations = tuple(
        AnimationSource(
            name=animation.name,
            sheet=read_source_sheet(project_dir, animation,
                                    where=f"sprite {sprite.name!r}"),
        )
        for animation in sprite.ordered_animations()
    )
    return NewSpriteIdentity(
        sprite_id=sprite.sprite_id,
        donor_sprite_id=sprite.donor_sprite_id,
        animations=animations,
        free_palette_entries=sprite.free_palette_entries,
    )


# --- the domain --------------------------------------------------------------


def materialize_authored_sprites(
    image: bytes,
    identification,
    profile,
    sprites: AuthoredSprites,
    project_dir: str | Path,
    *,
    reserved: tuple = (),
    corpus=None,
) -> AuthoredSpriteMaterialization:
    """Plan the project's new actor sprite and its actor, in that order.

    ``corpus`` is the decoded actor-sprite graphics when the caller already has
    it, so a build that also authors a palette or pixel override walks the corpus
    once rather than twice. ``reserved`` is the build-scoped reservation set every
    allocating domain shares; the spans this domain places are returned for the
    domains after it.
    """
    capability.require(
        identification,
        capability.Capability.ACTOR_SPRITES,
        subsystem="authored actor sprites",
        error_type=SpriteAuthoringProfileError,
        check_header=True,
    )
    capability.require(
        identification,
        capability.Capability.MAP_ENTRIES,
        subsystem="authored actor sprites",
        error_type=SpriteAuthoringProfileError,
        check_header=True,
    )
    sprite = sprites.only()

    identity_plan = plan_new_sprite_identity(
        image, identification, identity_request(project_dir, sprite),
        reserved=reserved, sprites=corpus,
    )
    attachment = plan_new_map_actor(
        image, identification, actor_request(image, profile, sprite),
        profile=profile, reserved=identity_plan.reserved,
    )
    return AuthoredSpriteMaterialization(
        identity=identity_plan.identity,
        actor=attachment.actor,
        changes=identity_plan.changes + attachment.changes,
        reserved=attachment.reserved,
        generated_allocations=(identity_plan.generated_allocations
                               + attachment.generated_allocations),
        relocations=identity_plan.relocations + attachment.relocations,
    )
