"""One additional actor-sprite identity, compiled into the one merged build plan.

SPRITE-NEW-AUTHORING-CORE-001.

**What this module owns.** Everything a retail image needs before its engine can
resolve an actor-sprite identity the image never contained: a grown
character-pointer registry in fresh space with every word that named the old
table repointed, one new character structure cloned from a donor the image
already draws, one animation record per authored sheet, one frame record per
engine direction slot, one graphics container per frame, and the object-palette
entries the artwork needs.

**What it deliberately does not own.** It does not place an actor. Attaching the
identity to a map object, a placement or the party table is a separate authoring
act, and no placement, map or party byte is written here. It authors no dialogue
and no script, and it offers no user interface.

**The composition guard.** The per-actor frame-composition buffer is sized by a
rule this write path has not solved, so an authored frame is admitted only inside
the donor's *proven* composition shape:
:func:`measure_donor_envelope` reads every frame of every animation the donor's
own structure decodes and reports the one frame rect the donor is seen to draw -
and refuses a donor whose frames disagree, which is the case no single proven
shape exists for. An authored frame must then be exactly that rect: a larger one
is a composition shape this path cannot prove, and a smaller one has no measured
placement, because the authored record copies the donor's own anchor. The guard
decides geometry only; it never authors one.

**The one mapping.** A source sheet is direction-major: four facings, each
holding all of its own frames. The animation record is frame-major - a frame
count, then that many groups of four direction pointers, which is the indexing
:meth:`sprite_graphics.Animation.pointer_for` states. So the sheet cell belonging
to engine slot ``f * 4 + d`` is cell ``d * frames_per_direction + f``, and
:meth:`SourceSheet.slot_cell_index` is the only place the two orders are
reconciled.

**Colour.** The artwork is RGB888 and the object palette holds 15-bit words, so
two source colours that pack to the same word are the same palette entry. Every
colour is reduced with the SDK's own
:func:`sprite_graphics.pack_gba_colour` and compared to the palette *as a word* -
the entry's low 15 bits, because bit 15 is not part of the colour and the SDK's
own decode already ignores it. A word the image already holds reuses that entry; a
word it does not hold takes one of the entries the caller explicitly requested,
and when none is left the plan is refused rather than approximated.

**What is reused.** :func:`allocation.allocate` places both spans above canonical
EOF under the addressability policy the retail evidence supports, and the write
layer authorizes them. The registry, structure, animations and frames are one
:data:`allocation.AllocationKind.SPRITE_IDENTITY_RECORD` placement because they
are one indivisible object; the containers are one
:data:`allocation.AllocationKind.GRAPHICS_CONTAINER` placement. Registry
relocation reuses the published contract rather than a private census: the anchor
must be published relocatable - the reference graph's own statement that its
inbound surface is fully expressed - and every inbound word the document
publishes is repointed and recorded as a
:class:`write.RelocationProvenance`.

**The corpus this reads.** ``sprites`` must supply exactly the four members
:func:`plan_new_sprite_identity` consumes: ``profile``, ``palette_users()``,
``registry_identity`` and ``reference_document()``. A caller holding a decoded
:class:`graphics.ActorSprites` passes nothing; a test can supply those four over
synthetic bytes, which is why the collaborator is a parameter and not a lookup.

The registry's inbound words are read through
:meth:`document.RomDocument.inbound` on the document that call already built,
rather than through :meth:`graphics.ActorSprites.registry_references`, which
would rebuild the same document a second time; the two return the same set, and
the document is where the check that each word still holds the table lives.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable

from .allocation import (Addressability, AllocationKind, AllocationRequest,
                         allocate)
from .binary import BinaryAddressError, FileOffset
from .formats import sprite_graphics as sg
from .layout import (AnchorId, OwnedRegion, ReferenceClass, ReferenceEncoding,
                     RomRange)
from .write import (ByteChange, GeneratedAllocationProvenance, ReferenceRewrite,
                    RelocationProvenance)


class SpriteIdentityError(ValueError):
    """An identity this write path will not author without guessing."""


#: The write owner of the identity's record block and of the registry rewrites.
RECORDS_OWNER = "sprite_identity:records"
#: The write owner of the object-palette entries the artwork needs.
PALETTE_OWNER = "sprite_identity:palette"
#: The write owner of the identity's packed graphics containers.
GRAPHICS_OWNER = "sprite_identity:graphics"

#: The one domain string this module's allocation provenance is recorded under.
DOMAIN = "sprite_identity"

#: Every record and payload this module authors is word aligned. The engine reads
#: animation, frame and container fields as little-endian words.
ALIGNMENT = 4

#: The engine's sprite-id floor. The registry accessor in the retail image
#: compares a requested id against 10 and indexes ``registry + 4 * (id - 10)``
#: with no bound check, so entry ``i`` of the table is sprite id ``i + 10``. The
#: table's *length* is the profile's: it is declared as
#: ``tables.actor_sprites.character_count``.
SPRITE_ID_FLOOR = 10

#: One frame of an animation is four direction slots, stored frame-major.
DIRECTION_COUNT = sg.DIRECTION_COUNT

#: The character structure: a ``0x54``-byte header whose first byte is the count
#: of animation pointers that follow it. The header's remaining bytes are copied
#: from the donor verbatim because their meaning is unresolved, and only the count
#: byte is rewritten to match the array actually written here.
STRUCTURE_COUNT_OFFSET = 0x00
STRUCTURE_HEADER_SIZE = 0x54
STRUCTURE_ANIMATION_TABLE_OFFSET = 0x54

#: The engine's animation accessors load the count with ``ldrb`` and compare it
#: against small immediates before indexing the array; the canonical corpus
#: carries counts from 1 through 23. That is a measured range, not a fixed
#: table: the array at ``+0x54`` is count-bounded and sparse.
MAX_ANIMATION_SLOTS = 23

#: An animation record: a frame count, then ``frame_count * 4`` frame pointers.
ANIMATION_HEADER_SIZE = 4

#: The largest frame count this write path will author. It is the bound the SDK's
#: own animation reader applies (:func:`sprite_graphics.decode_animation`), so
#: anything above it could not be read back by this project, let alone drawn.
MAX_FRAMES_PER_ANIMATION = 64

#: A frame record: a piece count, the frame's own bounding box, then pieces.
FRAME_HEADER_SIZE = sg.FRAME_HEADER_SIZE
FRAME_STRIDE = sg.FRAME_HEADER_SIZE + sg.PIECE_SIZE

#: A packed container is padded to a word boundary inside the generated block.
#: Containers are word aligned in the canonical corpus and the decompressor reads
#: them as little-endian words, so the padding is part of the layout rather than
#: slack.
CONTAINER_ALIGNMENT = 4

#: Index 0 of the object palette is the transparent entry, in both bit depths.
TRANSPARENT_INDEX = sg.TRANSPARENT_INDEX

#: The reference artwork keys transparency on this exact RGB triple.
DEFAULT_TRANSPARENT_COLOUR = (255, 0, 255)

#: The highest object-palette entry an 8bpp piece can address.
LAST_PALETTE_ENTRY = sg.PALETTE_ENTRIES - 1

#: A reference word is a full 32-bit little-endian GBA address. Read from the
#: encoding rather than restated, so a word this module writes is the width the
#: relocation contract reads.
REFERENCE_WIDTH = ReferenceEncoding.ABSOLUTE_ROM_U32_LE.width

#: The piece field that names a container, from the format codec.
PIECE_GRAPHICS_OFFSET = sg.PIECE_GRAPHICS


Colour = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class SourceSheet:
    """One direction-major source sheet: four facings of equal frame counts.

    ``pixels`` is RGB888, row-major, and describes one row of cells: cell
    ``d * frames_per_direction + f`` holds frame ``f`` of facing ``d``. Cell
    ``c`` therefore starts at pixel ``c * cell_width * cell_height``.

    ``transparent_colour`` is the source colour that becomes palette index 0.
    Index 0 is transparent on this hardware, so a sheet that used black for its
    background could not be authored at all; stating the key explicitly is what
    keeps "this pixel is a hole" distinct from "this pixel is black".
    """

    frames_per_direction: int
    cell_width: int
    cell_height: int
    pixels: bytes
    transparent_colour: Colour = DEFAULT_TRANSPARENT_COLOUR

    def __post_init__(self) -> None:
        for name, value in (("frames_per_direction", self.frames_per_direction),
                            ("cell_width", self.cell_width),
                            ("cell_height", self.cell_height)):
            if type(value) is not int or value <= 0:
                raise SpriteIdentityError(f"a source sheet needs a positive {name}")
        if self.frames_per_direction > MAX_FRAMES_PER_ANIMATION:
            raise SpriteIdentityError(
                f"a sheet of {self.frames_per_direction} frames per facing exceeds "
                f"the {MAX_FRAMES_PER_ANIMATION}-frame animation this project's own "
                "reader accepts, so the plan could not be read back")
        if type(self.pixels) is not bytes:
            raise SpriteIdentityError("a source sheet needs immutable pixel bytes")
        expected = self.width * self.height * 3
        if len(self.pixels) != expected:
            raise SpriteIdentityError(
                f"this sheet is {self.width}x{self.height}, {expected} RGB bytes, but "
                f"{len(self.pixels)} were supplied")
        _require_colour(self.transparent_colour, "a sheet's transparent colour")

    @property
    def frame_cells(self) -> int:
        """How many cells the whole sheet holds, across all four facings."""
        return self.frames_per_direction * DIRECTION_COUNT

    @property
    def width(self) -> int:
        return self.frame_cells * self.cell_width

    @property
    def height(self) -> int:
        return self.cell_height

    def slot_cell_index(self, frame_index: int, direction: int) -> int:
        """The sheet cell engine slot ``frame_index * 4 + direction`` is built from.

        This is the whole direction-major to frame-major mapping, and it is stated
        once so no caller can restate it differently.
        """
        if not 0 <= frame_index < self.frames_per_direction:
            raise SpriteIdentityError(
                f"frame {frame_index} is outside 0..{self.frames_per_direction - 1}")
        if not 0 <= direction < DIRECTION_COUNT:
            raise SpriteIdentityError(
                f"direction slot {direction} is outside 0..{DIRECTION_COUNT - 1}")
        return direction * self.frames_per_direction + frame_index

    def cell(self, index: int) -> bytes:
        """The RGB888 bytes of one cell, row-major."""
        if not 0 <= index < self.frame_cells:
            raise SpriteIdentityError(
                f"cell {index} is outside 0..{self.frame_cells - 1}")
        size = self.cell_width * self.cell_height * 3
        start = index * size
        return self.pixels[start:start + size]


@dataclass(frozen=True, slots=True)
class AnimationSource:
    """One animation slot of the identity, and the sheet whose frames fill it."""

    name: str
    sheet: SourceSheet

    def __post_init__(self) -> None:
        if type(self.name) is not str or not self.name.strip():
            raise SpriteIdentityError("an animation source needs a non-empty name")
        if not isinstance(self.sheet, SourceSheet):
            raise SpriteIdentityError(
                f"animation {self.name!r} needs a SourceSheet, not {self.sheet!r}")


@dataclass(frozen=True, slots=True)
class NewSpriteIdentity:
    """One actor-sprite identity to add, described but not yet placed.

    ``sprite_id`` is the engine id the identity will answer to. It is stated
    rather than derived so a caller cannot attach an actor to a number this build
    did not author; the planner accepts exactly the id an appended registry entry
    yields and refuses the rest.

    ``donor_sprite_id`` is an identity the image already contains. Its character
    structure header is cloned, and its first frame's single piece supplies the
    geometry - placement offsets, pixel extents and packed OAM attributes - that
    every authored frame copies verbatim. Choosing a donor is therefore how the
    author states the frame geometry this identity will keep.

    ``free_palette_entries`` is the caller's claim about which object-palette
    entries are free. The SDK cannot derive that claim completely: it decodes the
    actor-sprite graphics but not the portrait or user-interface payloads that
    share the same 256-entry palette. The planner therefore checks the claim
    against what it can prove - no decoded actor-sprite graphic draws a requested
    entry - and refuses an entry that fails, rather than silently recolouring
    another asset.
    """

    sprite_id: int
    donor_sprite_id: int
    animations: tuple[AnimationSource, ...]
    free_palette_entries: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (("sprite_id", self.sprite_id),
                            ("donor_sprite_id", self.donor_sprite_id)):
            if type(value) is not int or value < 0:
                raise SpriteIdentityError(f"{name} must be a non-negative integer")
        if not isinstance(self.animations, tuple) or not self.animations:
            raise SpriteIdentityError("an identity needs at least one animation slot")
        if len(self.animations) > MAX_ANIMATION_SLOTS:
            raise SpriteIdentityError(
                f"{len(self.animations)} animation slots exceeds the "
                f"{MAX_ANIMATION_SLOTS} the structure's count byte can state to the "
                "engine's accessors")
        for animation in self.animations:
            if not isinstance(animation, AnimationSource):
                raise SpriteIdentityError(
                    f"animation slots must be AnimationSource values, not {animation!r}")
        names = [animation.name for animation in self.animations]
        if len(set(names)) != len(names):
            raise SpriteIdentityError(
                f"animation names must be unique; got {sorted(names)}")
        if not isinstance(self.free_palette_entries, tuple):
            raise SpriteIdentityError("free palette entries must be a tuple")
        for index in self.free_palette_entries:
            if type(index) is not int or not TRANSPARENT_INDEX < index <= LAST_PALETTE_ENTRY:
                raise SpriteIdentityError(
                    f"free palette entry {index!r} is outside "
                    f"{TRANSPARENT_INDEX + 1}..{LAST_PALETTE_ENTRY}; entry "
                    f"{TRANSPARENT_INDEX} is the transparent entry")
        if len(set(self.free_palette_entries)) != len(self.free_palette_entries):
            raise SpriteIdentityError(
                f"free palette entries repeat: {sorted(self.free_palette_entries)}")


@dataclass(frozen=True, slots=True)
class AuthoredPaletteEntry:
    """One object-palette entry this identity needed written, and what it held."""

    index: int
    word: int
    colour: Colour
    previous_word: int
    file_offset: int

    def to_json(self) -> dict:
        return {"index": self.index, "word": self.word, "word_hex": f"0x{self.word:04X}",
                "colour": list(self.colour), "previous_word": self.previous_word,
                "file_offset": self.file_offset}


@dataclass(frozen=True, slots=True)
class AuthoredFrame:
    """One authored frame record, and the sheet cell its pixels came from."""

    slot: int
    frame_index: int
    direction: int
    sheet_cell: int
    record_range: RomRange
    container_range: RomRange
    sheet_name: str

    @property
    def rom_address(self) -> int:
        return self.record_range.start.to_gba_address(self.record_range.end).raw

    def to_json(self) -> dict:
        return {"sheet": self.sheet_name, "slot": self.slot,
                "frame_index": self.frame_index, "direction": self.direction,
                "sheet_cell": self.sheet_cell,
                "record_range": self.record_range.to_json(),
                "container_range": self.container_range.to_json()}


@dataclass(frozen=True, slots=True)
class AuthoredAnimation:
    """One animation slot: its own record, and every frame cell it names."""

    name: str
    slot: int
    animation_range: RomRange
    frames: tuple[AuthoredFrame, ...]

    @property
    def frames_per_direction(self) -> int:
        return len(self.frames) // DIRECTION_COUNT

    def to_json(self) -> dict:
        return {"name": self.name, "slot": self.slot,
                "frames_per_direction": self.frames_per_direction,
                "animation_range": self.animation_range.to_json(),
                "frames": [frame.to_json() for frame in self.frames]}


@dataclass(frozen=True, slots=True)
class AuthoredIdentity:
    """The identity as it was actually laid out, addresses included.

    Every record and every container lives above the canonical image, inside the
    profile's declared expansion. This record is what a later placement act reads
    to attach an actor to ``sprite_id``; it is descriptive and is never used to
    re-derive a plan.
    """

    sprite_id: int
    donor_sprite_id: int
    registry_entries: int
    registry_range: RomRange
    structure_range: RomRange
    animations: tuple[AuthoredAnimation, ...]
    containers_range: RomRange
    palette_entries: tuple[AuthoredPaletteEntry, ...]

    @property
    def registry_rom_address(self) -> int:
        return self.registry_range.start.to_gba_address(self.registry_range.end).raw

    @property
    def structure_rom_address(self) -> int:
        return self.structure_range.start.to_gba_address(
            self.structure_range.end).raw

    def to_json(self) -> dict:
        return {
            "sprite_id": self.sprite_id,
            "donor_sprite_id": self.donor_sprite_id,
            "registry_entries": self.registry_entries,
            "registry": {"range": self.registry_range.to_json(),
                         "rom_address": self.registry_rom_address,
                         "rom_address_hex": f"0x{self.registry_rom_address:08X}"},
            "structure": {"range": self.structure_range.to_json(),
                          "rom_address": self.structure_rom_address,
                          "rom_address_hex": f"0x{self.structure_rom_address:08X}",
                          "animation_slots": len(self.animations)},
            "animations": [animation.to_json() for animation in self.animations],
            "containers": self.containers_range.to_json(),
            "palette_entries": [entry.to_json() for entry in self.palette_entries],
        }


@dataclass(frozen=True, slots=True)
class SpriteIdentityMaterialization:
    """Everything this domain contributes to the one merged build plan.

    The four plan fields are the shape every authoring domain returns, so a
    caller threads them into :func:`write.plan_changes` unchanged. ``identity`` is
    this domain's own description of what it laid out.
    """

    identity: AuthoredIdentity
    changes: tuple[ByteChange, ...] = ()
    reserved: tuple[OwnedRegion, ...] = ()
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    relocations: tuple[RelocationProvenance, ...] = ()


@dataclass(frozen=True, slots=True)
class _Cell:
    """One authored frame cell: where it belongs, where it lives, and its pixels."""

    animation_index: int
    slot: int
    frame_index: int
    direction: int
    sheet_cell: int
    sheet_name: str
    pixels: bytes


@dataclass(frozen=True, slots=True)
class _Palette:
    """The palette assignment for one identity: its cells and the entries to write."""

    cells: tuple[_Cell, ...]
    entries: tuple[AuthoredPaletteEntry, ...]


def plan_new_sprite_identity(
    image: bytes,
    identification,
    identity: NewSpriteIdentity,
    *,
    reserved: tuple[OwnedRegion, ...] = (),
    sprites=None,
) -> SpriteIdentityMaterialization:
    """Compile one new actor-sprite identity into attributed changes. Pure.

    The identity is authored entirely above the canonical image and nothing
    canonical is retired: the only canonical bytes this plan changes are the words
    that named the character registry and the object-palette entries the artwork
    needs. Every existing structure, animation, frame and container keeps its own
    bytes, and the grown registry's first entries are the canonical entries
    verbatim.

    **Why a frame cannot grow.** The retail engine sizes a per-actor composition
    buffer from the frame it is drawing, and the rule that sizes it is not solved
    here. This planner therefore does not let an author choose frame geometry at
    all: it measures the donor's own proven frame rect
    (:func:`measure_donor_envelope`) and every authored frame copies the donor's
    own first frame - the same placement offsets, the same pixel extents, the same
    packed OAM attributes - with the sheet cell dimensions required to BE that
    rect. The result is that the authored frames are geometry the donor's
    animation already draws, so the budget is not merely unmodelled here, it is
    unchanged. What this does NOT establish: that the budget is adequate for
    whatever actor a later act points at these frames. Attaching this identity to
    an actor that draws smaller frames than the donor is the case that remains
    open.

    ``reserved`` is the build-scoped reservation set every allocating domain
    shares; the spans this domain places are returned for the domains after it.
    """
    if not isinstance(identity, NewSpriteIdentity):
        raise SpriteIdentityError(
            f"planning needs a NewSpriteIdentity, not {type(identity).__name__}")
    if sprites is None:
        from .graphics import load_actor_sprites

        sprites = load_actor_sprites(image, identification)
    authoring = _authoring(image, sprites, identity)
    container_payload, cell_offsets = _container_payloads(authoring)
    block_layout = _block_layout(authoring.layout.character_count,
                                 identity.animations,
                                 len(authoring.assignment.cells))
    allocations = _allocate(authoring, block_layout, len(container_payload), reserved)
    records = _encode_records(authoring, block_layout, cell_offsets, allocations)
    changes, rewrites = _changes(authoring, block_layout, records, cell_offsets,
                                 container_payload, allocations)
    generated, relocations = _provenance(authoring, allocations, block_layout, rewrites)
    return _materialize(authoring, block_layout, records, allocations, cell_offsets,
                        changes, generated, relocations)


@dataclass(frozen=True, slots=True)
class DonorEnvelope:
    """The one frame rect a donor's own animation records are seen to draw.

    ``width`` and ``height`` are pixel extents, not a tile count, and they are the
    frame record's own bounding box: the rect the donor's animation declares for
    its frames. ``anchor`` is that box's own signed minimum corner ``(min_x,
    min_y)``, which is what places the rect in the actor's space; a donor whose
    frames share the rect but not the anchor has no measured placement either.
    ``piece_count`` is how many pieces the frames carrying that rect hold,
    published so a caller can see that the proven shape was reached by more than
    one piece rather than assume it.

    The name is deliberately not "budget". What is proven here is the rectangle
    the donor already draws; *how* the engine sizes the per-actor composition
    buffer from that rect is unresolved, so this record states the shape and does
    not claim a budget.
    """

    width: int
    height: int
    anchor: tuple[int, int]
    piece_count: int

    @property
    def pixels(self) -> int:
        """The frame's ``w * h``; the extent a composed frame occupies."""
        return self.width * self.height

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


@dataclass(frozen=True, slots=True)
class _Authoring:
    """The inputs every stage below the planner's opening checks agrees on."""

    image: bytes
    identity: NewSpriteIdentity
    profile: object
    layout: object
    document: object
    anchor: object
    references: tuple
    entries: tuple
    donor_header: bytes
    piece: object
    palette: object
    palette_offset: int
    assignment: _Palette
    padding: int
    image_size: int


@dataclass(frozen=True, slots=True)
class _BlockLayout:
    """Where each part of the identity's record block starts, and how big it is.

    Everything is word aligned because the engine reads the animation, frame and
    container fields as little-endian words, and the frames follow the animations
    so that the words after an animation table are a frame header rather than an
    invented trailer.
    """

    registry_at: int
    structure_at: int
    animations_at: int
    frames_at: int
    size: int
    animation_sizes: tuple[int, ...]
    registry_size: int
    structure_size: int


@dataclass(frozen=True, slots=True)
class _Records:
    """The finished record block, with the addresses its own fields name."""

    block: bytes
    frame_addresses: tuple[int, ...]
    animation_addresses: tuple[int, ...]
    animation_ranges: tuple[RomRange, ...]


def _authoring(image: bytes, sprites, identity: NewSpriteIdentity) -> _Authoring:
    """Every check this write path makes before it is willing to plan anything."""
    profile = sprites.profile
    layout = profile.actor_sprites
    if layout is None:
        raise SpriteIdentityError(
            f"profile {profile.id!r} declares no actor_sprites; there is no registry "
            "to grow")
    expansion = profile.generated_expansion
    if expansion is None:
        raise SpriteIdentityError(
            "an additional sprite identity cannot be authored inside the canonical "
            "image - the grown registry and its frames outgrow the space a retail "
            "profile declares free - and this profile declares no generated "
            "expansion to place them in")
    document = sprites.reference_document()
    anchor, references, entries = _registry(image, sprites, document, layout)
    _require_appended_id(identity, layout)
    donor_header, piece, envelope = _donor(image, identity, entries, layout)
    for animation in identity.animations:
        _require_cell_geometry(animation, envelope)
    palette_offset = layout.object_palette_address.to_file_offset(len(image))
    palette = sg.decode_palette(image, palette_offset)
    return _Authoring(
        image=image, identity=identity, profile=profile, layout=layout,
        document=document, anchor=anchor, references=references,
        entries=tuple(entries), donor_header=donor_header, piece=piece,
        palette=palette, palette_offset=palette_offset,
        assignment=_assign_palette(palette, palette_offset, sprites, identity),
        padding=expansion.padding_byte, image_size=expansion.output_size)


def _container_payloads(authoring: _Authoring) -> tuple[bytes, tuple]:
    """One packed container per authored frame, word aligned inside the block."""
    graphic = sg.Graphic(offset=0, width=authoring.piece.dim_0,
                         height=authoring.piece.dim_1, colour_256=True, pixels=b"",
                         packed_end=0)
    parts: list[bytes] = []
    offsets: list[tuple[int, int]] = []
    running = 0
    for cell in authoring.assignment.cells:
        payload = sg.encode_graphic_payload(
            graphic, cell.pixels, kind=sg.GRAPHICS_CONTAINER_KIND)
        padded = payload + bytes([authoring.padding]) * (
            -len(payload) % CONTAINER_ALIGNMENT)
        offsets.append((running, len(payload)))
        parts.append(padded)
        running += len(padded)
    return b"".join(parts), tuple(offsets)


def _block_layout(canonical_entries: int, animations, cells: int) -> _BlockLayout:
    """The record block's extents, computed before any address is chosen."""
    registry_size = ALIGNMENT * (canonical_entries + 1)
    structure_size = STRUCTURE_HEADER_SIZE + ALIGNMENT * len(animations)
    animation_sizes = tuple(
        ANIMATION_HEADER_SIZE + ALIGNMENT * DIRECTION_COUNT
        * source.sheet.frames_per_direction
        for source in animations)
    structure_at = registry_size
    animations_at = structure_at + structure_size
    frames_at = animations_at + sum(animation_sizes)
    return _BlockLayout(
        registry_at=0, structure_at=structure_at, animations_at=animations_at,
        frames_at=frames_at, size=frames_at + FRAME_STRIDE * cells,
        animation_sizes=animation_sizes, registry_size=registry_size,
        structure_size=structure_size)


def _allocate(authoring: _Authoring, block_layout: _BlockLayout,
              container_size: int, reserved: tuple) -> dict:
    """Place the containers and the record block, both above canonical EOF.

    Both requests are `EXPANDED_ONLY` by policy rather than by first fit. The
    record block is the grown registry and its records, which is new content with
    no canonical extent to fit; the containers are new content too, and the shared
    canonical free window is small enough that spending it here would take a
    resource other domains draw on. Placing them above EOF is also exactly the
    addressability this capability has to prove.
    """
    requests = (
        AllocationRequest(
            AnchorId(GRAPHICS_OWNER), GRAPHICS_OWNER, container_size, ALIGNMENT,
            kind=AllocationKind.GRAPHICS_CONTAINER,
            addressability=Addressability.EXPANDED_ONLY,
            evidence="one packed container per authored frame of a new identity"),
        AllocationRequest(
            AnchorId(RECORDS_OWNER), RECORDS_OWNER, block_layout.size, ALIGNMENT,
            kind=AllocationKind.SPRITE_IDENTITY_RECORD,
            addressability=Addressability.EXPANDED_ONLY,
            evidence="the grown registry, its new structure, its animations and its "
                     "frames, as one indivisible placement"),
    )
    allocations = allocate(authoring.profile, requests,
                           occupied=_occupied(authoring.document, reserved))
    return {allocation.request.owner: allocation for allocation in allocations}


def _encode_records(authoring: _Authoring, block_layout: _BlockLayout,
                    cell_offsets: tuple, allocations: dict) -> _Records:
    """Fill the record block now that every address it names is known.

    The registry's last entry names the structure, the structure names each
    animation, each animation names its frames in engine slot order, and each frame
    names the container built from its own sheet cell.
    """
    image_size = authoring.image_size
    records_at = allocations[RECORDS_OWNER].range.start.value
    container_at = allocations[GRAPHICS_OWNER].rom_address
    block = bytearray([authoring.padding]) * block_layout.size
    block[:block_layout.registry_size] = struct.pack(
        f"<{authoring.layout.character_count + 1}I", *authoring.entries,
        FileOffset(records_at + block_layout.structure_at).to_gba_address(
            image_size).raw)
    block[block_layout.structure_at:
          block_layout.structure_at + STRUCTURE_HEADER_SIZE] = authoring.donor_header
    block[block_layout.structure_at + STRUCTURE_COUNT_OFFSET] = \
        len(authoring.identity.animations)

    frame_addresses = []
    for index, _cell in enumerate(authoring.assignment.cells):
        at = block_layout.frames_at + FRAME_STRIDE * index
        offset, _length = cell_offsets[index]
        block[at:at + FRAME_STRIDE] = _encode_frame(
            authoring.piece, container_at + offset)
        frame_addresses.append(
            FileOffset(records_at + at).to_gba_address(image_size).raw)

    cursor = block_layout.animations_at
    animation_addresses: list[int] = []
    animation_ranges: list[RomRange] = []
    slot = 0
    for source, size in zip(authoring.identity.animations, block_layout.animation_sizes):
        count = source.sheet.frame_cells
        block[cursor:cursor + size] = struct.pack(
            f"<I{count}I", source.sheet.frames_per_direction,
            *frame_addresses[slot:slot + count])
        animation_addresses.append(
            FileOffset(records_at + cursor).to_gba_address(image_size).raw)
        animation_ranges.append(RomRange(FileOffset(records_at + cursor), size))
        slot += count
        cursor += size
    struct.pack_into(f"<{len(animation_addresses)}I", block,
                     block_layout.structure_at + STRUCTURE_ANIMATION_TABLE_OFFSET,
                     *animation_addresses)
    return _Records(block=bytes(block), frame_addresses=tuple(frame_addresses),
                    animation_addresses=tuple(animation_addresses),
                    animation_ranges=tuple(animation_ranges))


def _changes(authoring: _Authoring, block_layout: _BlockLayout, records: _Records,
             cell_offsets: tuple, container_payload: bytes, allocations: dict):
    """The two new spans, the words that name the moved registry, the palette.

    The registry rewrites and the payload write are one transaction: a grown table
    no word reaches, or a word naming bytes that were never written, is a
    corruption rather than a partial authoring.
    """
    image = authoring.image
    sprite_id = authoring.identity.sprite_id
    records_at = allocations[RECORDS_OWNER].range.start.value
    container_at = allocations[GRAPHICS_OWNER].range.start.value
    changes = [
        ByteChange(
            records_at, bytes([authoring.padding]) * block_layout.size,
            records.block, RECORDS_OWNER,
            f"new sprite identity {sprite_id}: the "
            f"{authoring.layout.character_count + 1}-entry registry, its character "
            f"structure, {len(authoring.identity.animations)} animation record(s) and "
            f"{len(authoring.assignment.cells)} frame record(s), above canonical EOF"),
        ByteChange(
            container_at, bytes([authoring.padding]) * len(container_payload),
            container_payload, GRAPHICS_OWNER,
            f"new sprite identity {sprite_id}: "
            f"{len(authoring.assignment.cells)} packed {authoring.piece.dim_0}x"
            f"{authoring.piece.dim_1} graphics container(s), one per authored frame"),
    ]
    rewrites: list[ReferenceRewrite] = []
    registry_address = FileOffset(records_at).to_gba_address(authoring.image_size).raw
    for reference in authoring.references:
        source = reference.source.value
        changes.append(ByteChange(
            source, image[source:source + REFERENCE_WIDTH],
            registry_address.to_bytes(REFERENCE_WIDTH, "little"), RECORDS_OWNER,
            "registry relocation: this word named the canonical character table and "
            f"now names the {authoring.layout.character_count + 1}-entry table"))
        rewrites.append(ReferenceRewrite(
            reference=reference, new_source_file_offset=source,
            old_target_file_offset=authoring.document.target_offset(reference).value,
            new_target_file_offset=records_at))
    for entry in authoring.assignment.entries:
        changes.append(ByteChange(
            entry.file_offset, image[entry.file_offset:entry.file_offset + 2],
            entry.word.to_bytes(2, "little"), PALETTE_OWNER,
            f"object-palette entry {entry.index} now holds the colour this "
            f"identity's {entry.colour} artwork needs"))
    return tuple(changes), tuple(rewrites)


def _provenance(authoring: _Authoring, allocations: dict,
                block_layout: _BlockLayout, rewrites: tuple):
    """The write-layer authorization and the relocation record for both spans."""
    records_at = allocations[RECORDS_OWNER].range.start.value
    container_pointer_offset = (records_at + block_layout.frames_at
                                + FRAME_HEADER_SIZE + PIECE_GRAPHICS_OFFSET)
    generated = (
        allocations[RECORDS_OWNER].generated_allocation_provenance(
            domain=DOMAIN, resource=RECORDS_OWNER,
            pointer_offset=min(reference.source.value
                               for reference in authoring.references),
            source_range=authoring.anchor.range),
        allocations[GRAPHICS_OWNER].generated_allocation_provenance(
            domain=DOMAIN, resource=GRAPHICS_OWNER,
            pointer_offset=container_pointer_offset,
            source_range=RomRange(FileOffset(container_pointer_offset),
                                  REFERENCE_WIDTH)),
    )
    relocations = (RelocationProvenance(
        anchor=authoring.anchor.identity.value, owner=RECORDS_OWNER,
        old_range=authoring.anchor.range,
        new_range=RomRange(FileOffset(records_at), block_layout.registry_size),
        alignment=authoring.anchor.alignment,
        free_region_evidence=allocations[RECORDS_OWNER].free_region_evidence,
        references=rewrites),)
    return generated, relocations


def _materialize(authoring: _Authoring, block_layout: _BlockLayout, records: _Records,
                 allocations: dict, cell_offsets: tuple, changes: tuple,
                 generated: tuple, relocations: tuple) -> SpriteIdentityMaterialization:
    """The result record: what was laid out, and what the plan may write."""
    records_at = allocations[RECORDS_OWNER].range.start.value
    container_at = allocations[GRAPHICS_OWNER].range.start.value
    authored = AuthoredIdentity(
        sprite_id=authoring.identity.sprite_id,
        donor_sprite_id=authoring.identity.donor_sprite_id,
        registry_entries=authoring.layout.character_count + 1,
        registry_range=RomRange(FileOffset(records_at), block_layout.registry_size),
        structure_range=RomRange(
            FileOffset(records_at + block_layout.structure_at),
            block_layout.structure_size),
        animations=tuple(
            AuthoredAnimation(
                name=source.name, slot=index,
                animation_range=records.animation_ranges[index],
                frames=tuple(
                    AuthoredFrame(
                        slot=cell.slot, frame_index=cell.frame_index,
                        direction=cell.direction, sheet_cell=cell.sheet_cell,
                        sheet_name=cell.sheet_name,
                        record_range=RomRange(
                            FileOffset(records_at + block_layout.frames_at
                                       + FRAME_STRIDE * cell_index),
                            FRAME_STRIDE),
                        container_range=RomRange(
                            FileOffset(container_at + cell_offsets[cell_index][0]),
                            cell_offsets[cell_index][1]),
                    )
                    for cell_index, cell in enumerate(authoring.assignment.cells)
                    if cell.animation_index == index
                ),
            )
            for index, source in enumerate(authoring.identity.animations)
        ),
        containers_range=allocations[GRAPHICS_OWNER].range,
        palette_entries=authoring.assignment.entries,
    )
    return SpriteIdentityMaterialization(
        identity=authored, changes=changes,
        reserved=tuple(OwnedRegion(allocation.range, allocation.request.owner)
                       for allocation in allocations.values()),
        generated_allocations=generated, relocations=relocations)


# --- the registry ------------------------------------------------------------


def _require_appended_id(identity: NewSpriteIdentity, layout) -> None:
    """The only id a grown registry can offer is the entry appended after it.

    The accessor is ``registry + 4 * (id - floor)`` with no bound check, so an id
    below the new entry would name an existing identity and an id above it would
    read past the table. Stating the id in the request rather than deriving it
    silently is what makes "which identity did this build author" answerable.
    """
    expected = SPRITE_ID_FLOOR + layout.character_count
    if identity.sprite_id != expected:
        raise SpriteIdentityError(
            f"sprite id {identity.sprite_id} is not the identity this image can "
            f"offer: the registry is indexed as sprite id {SPRITE_ID_FLOOR} + entry, "
            f"so a {layout.character_count}-entry table grows to sprite id "
            f"{expected}, and no other id is addressable without overwriting an "
            "existing identity")


def _registry(image: bytes, sprites, document, layout):
    """The published registry anchor, its inbound words, and its entries.

    Every check here is a way the relocation contract could be false for this
    image, and each is a refusal rather than a workaround. A registry whose
    anchor is not published relocatable has an inbound surface the reference graph
    does not fully express, and growing it would strand whatever really reaches
    it.
    """
    anchor = document.anchor(AnchorId(sprites.registry_identity))
    table_offset = layout.character_table_address.to_file_offset(len(image))
    if anchor.kind != "character_pointer_table":
        raise SpriteIdentityError(
            f"{sprites.registry_identity} is published as kind {anchor.kind!r}, not a "
            "character_pointer_table")
    if (anchor.range.start.value != table_offset
            or anchor.range.size != layout.character_count * ALIGNMENT):
        raise SpriteIdentityError(
            f"{sprites.registry_identity} spans {anchor.range.to_json()}, but the "
            f"profile declares {layout.character_count} entries at file 0x"
            f"{table_offset:06X}")
    if not anchor.relocatable:
        raise SpriteIdentityError(
            f"{sprites.registry_identity} is not published relocatable, so its inbound "
            "surface is not fully expressed by the reference graph and moving it "
            "would strand whatever reaches it")
    references = document.inbound(anchor.identity)
    if not references:
        raise SpriteIdentityError(
            f"{sprites.registry_identity} has no published inbound word, so a moved "
            "table would have no owner to rewrite")
    expected = layout.character_table_address.raw.to_bytes(REFERENCE_WIDTH, "little")
    for reference in references:
        if (reference.target != anchor.identity
                or reference.classification is not ReferenceClass.CONFIRMED_REFERENCE
                or reference.encoding is not ReferenceEncoding.ABSOLUTE_ROM_U32_LE
                or reference.target_delta != 0):
            raise SpriteIdentityError(
                f"the registry's inbound word at 0x{reference.source.value:06X} is "
                f"{reference.classification.value} / {reference.encoding.value} with "
                f"delta {reference.target_delta}; only a confirmed, delta-free word "
                "addressing the table start can be repointed")
        source = reference.source.value
        if image[source:source + REFERENCE_WIDTH] != expected:
            raise SpriteIdentityError(
                f"the published registry reference at 0x{source:06X} does not hold the "
                "canonical table address, so this image is not the one the reference "
                "was published for")
    entries = list(struct.unpack_from(
        f"<{layout.character_count}I", image, table_offset))
    return anchor, references, entries


def _donor(image: bytes, identity: NewSpriteIdentity, entries, layout):
    """The donor's structure header, its first frame's single piece, and its envelope.

    The header is cloned verbatim - including the four 16-byte blocks at
    ``+0x10..+0x4F``, whose meaning is unresolved - and only its count byte is
    rewritten to match the animation array actually written. The first frame's
    piece fixes the authored geometry, so every property that could silently
    change the actor's drawing is read here instead of hardcoded: the placement
    offsets, the pixel extents and the packed OAM attribute word. Its frame rect
    is checked to be that same piece, and :func:`measure_donor_envelope` states
    the one rect the donor proves.
    """
    donor_offset = _donor_offset(identity, entries, layout, len(image))
    header = image[donor_offset:donor_offset + STRUCTURE_HEADER_SIZE]
    if len(header) != STRUCTURE_HEADER_SIZE:
        raise SpriteIdentityError(
            f"the donor structure at 0x{donor_offset:06X} is short of its "
            f"0x{STRUCTURE_HEADER_SIZE:X}-byte header")
    slots = header[STRUCTURE_COUNT_OFFSET]
    if not 1 <= slots <= MAX_ANIMATION_SLOTS:
        raise SpriteIdentityError(
            f"the donor structure at 0x{donor_offset:06X} declares {slots} animation "
            f"slots, outside 1..{MAX_ANIMATION_SLOTS}")
    table = donor_offset + STRUCTURE_ANIMATION_TABLE_OFFSET

    def frame_at(pointer: int, what: str):
        return sg.decode_frame(image, _file_offset(pointer, len(image), what))

    # This function states its own refusals in this module's terms; nothing to catch.
    envelope = measure_donor_envelope(image, donor_offset, frame_at)
    pointer = int.from_bytes(image[table:table + REFERENCE_WIDTH], "little")
    try:
        animation = sg.decode_animation(
            image, _file_offset(pointer, len(image), "the donor animation"))
        frame = frame_at(animation.pointer_for(0, 0), "the donor frame")
    except sg.SpriteFormatError as exc:
        raise SpriteIdentityError(
            f"the donor structure at 0x{donor_offset:06X} does not decode: {exc}"
        ) from exc
    if len(frame.pieces) != 1:
        raise SpriteIdentityError(
            f"the donor's first frame holds {len(frame.pieces)} pieces, but this write "
            "path authors one piece per frame and will not invent a multi-piece "
            "layout out of the donor's first piece")
    piece = frame.pieces[0]
    if ((piece.dim_0, piece.dim_1) != (frame.width, frame.height)
            or (piece.x, piece.y) != (frame.min_x, frame.min_y)):
        raise SpriteIdentityError(
            f"the donor's first frame declares a {frame.width}x{frame.height} frame "
            f"box at ({frame.min_x}, {frame.min_y}) but its own piece is "
            f"{piece.dim_0}x{piece.dim_1} at ({piece.x}, {piece.y}); this write path "
            "copies the frame record, so a donor whose record disagrees with itself "
            "would author geometry the donor does not draw")
    if not piece.colour_256:
        raise SpriteIdentityError(
            "the donor's first frame is a 4bpp piece, and the authored containers are "
            "8bpp; a 4bpp donor is refused rather than reinterpreted")
    if piece.horizontal_flip or piece.vertical_flip:
        # Bits 12-13 of attribute 1 are the flip bits for the OBJ forms this
        # project models. No affine form is modelled anywhere in the SDK and no
        # canonical piece is known to use one, so a donor that set them as an
        # affine parameter index would be refused here too, which is the safe
        # direction: its attribute word could not be copied meaningfully anyway.
        raise SpriteIdentityError(
            "the donor's first piece carries a flip bit, so every authored frame "
            "would mirror the sheet the author drew; choose a donor whose first piece "
            "is unflipped, or draw the mirrored facing in the sheet")
    return header, piece, envelope


def measure_donor_envelope(image: bytes, structure_offset: int,
                           frame_at: Callable[[int, str], object]) -> DonorEnvelope:
    """The one frame rect a donor's own animation records are seen to draw.

    Every animation the structure's count byte names is walked, and every frame
    each one repeats a pointer to is decoded, because a donor is a *population* of
    frames rather than its first one. The one rect - at one anchor - every decoded
    frame agrees on is that shape: what the donor's animation already composes,
    and therefore the only geometry this write path can call proven. The
    population measurement is evidence and lives in
    ``docs/research/SPRITE_NEW_COMPOSITION_GUARD.md``.

    A donor whose decoded frames disagree about their rect has no single proven
    shape, and a donor whose frames share a rect but place it at different anchors
    has no single proven placement; both are refused rather than resolved by
    preference, because the authored record copies one donor frame's geometry
    verbatim, so a shape or anchor chosen from one frame while another frame is
    what a later actor draws would be a guess.

    A slot whose animation pointer is null is skipped. That is stated as an
    observation rather than a rule of the engine's accessor: the canonical arrays
    carry such slots, each one's word is zero, and zero is not an address in this
    image, so it names no animation record to decode.

    ``frame_at`` decodes one frame by ROM pointer, so the one image-offset
    conversion lives in the caller.
    """
    table = structure_offset + STRUCTURE_ANIMATION_TABLE_OFFSET
    slots = image[structure_offset + STRUCTURE_COUNT_OFFSET]
    rects: dict[tuple[int, int], int] = {}
    anchors: dict[tuple[int, int], set[tuple[int, int]]] = {}
    for slot in range(slots):
        pointer = int.from_bytes(image[table + 4 * slot:table + 4 * slot + 4], "little")
        if pointer == 0:
            continue
        try:
            animation = sg.decode_animation(
                image, _file_offset(pointer, len(image), f"the donor animation {slot}"))
            frames = [frame_at(animation.pointer_for(index, direction),
                               f"the donor frame {slot}.{index}")
                      for index in range(animation.frame_count)
                      for direction in range(DIRECTION_COUNT)]
        except sg.SpriteFormatError as exc:
            raise SpriteIdentityError(
                f"the donor structure at 0x{structure_offset:06X} does not decode: {exc}"
            ) from exc
        for frame in frames:
            rect = (frame.width, frame.height)
            rects[rect] = max(rects.get(rect, 0), frame.piece_count)
            anchors.setdefault(rect, set()).add((frame.min_x, frame.min_y))
    if not rects:
        raise SpriteIdentityError(
            f"the donor structure at 0x{structure_offset:06X} names no decodable "
            "frame, so it proves no composition shape")
    if len(rects) > 1:
        shapes = ", ".join(f"{width}x{height}" for width, height in sorted(rects))
        raise SpriteIdentityError(
            f"the donor structure at 0x{structure_offset:06X} draws frames of "
            f"several shapes ({shapes}), so it proves no single composition shape; "
            "choose a donor whose own frames all occupy one rect")
    (width, height), piece_count = next(iter(rects.items()))
    placed = anchors[(width, height)]
    if len(placed) > 1:
        corners = ", ".join(f"({x}, {y})" for x, y in sorted(placed))
        raise SpriteIdentityError(
            f"the donor structure at 0x{structure_offset:06X} draws its {width}x"
            f"{height} frames at several anchors ({corners}), so it proves no single "
            "placement; choose a donor whose frames all sit at one anchor")
    return DonorEnvelope(width=width, height=height, anchor=next(iter(placed)),
                         piece_count=piece_count)


def _donor_offset(identity: NewSpriteIdentity, entries, layout, image_size: int) -> int:
    """The donor structure's file offset, or a refusal naming the id."""
    slot = identity.donor_sprite_id - SPRITE_ID_FLOOR
    if not 0 <= slot < layout.character_count:
        raise SpriteIdentityError(
            f"donor sprite id {identity.donor_sprite_id} is entry {slot}; the registry "
            f"holds entries 0..{layout.character_count - 1}, sprite ids "
            f"{SPRITE_ID_FLOOR}..{SPRITE_ID_FLOOR + layout.character_count - 1}")
    return _file_offset(entries[slot], image_size, "the donor structure")


def _require_cell_geometry(animation: AnimationSource, envelope: DonorEnvelope) -> None:
    """The sheet must be authored at exactly the donor's proven frame rect.

    Exact equality is the guard, not a convenience. A larger cell is a
    composition shape this write path cannot prove - the engine does size a
    per-actor buffer from the frame it composes, and the rule that sizes it is
    unresolved - and a smaller one has no measured placement, because the authored
    record copies the donor's own anchor instead of centring anything. A cell that
    is both tile-whole and equal to the proven rect is one the donor already draws.
    """
    sheet = animation.sheet
    if (sheet.cell_width, sheet.cell_height) != (envelope.width, envelope.height):
        raise SpriteIdentityError(
            f"animation {animation.name!r} is authored at "
            f"{sheet.cell_width}x{sheet.cell_height}, but the donor's own frames "
            f"prove exactly one composition shape, {envelope} at anchor "
            f"{envelope.anchor}, drawn as {envelope.piece_count} piece(s) "
            f"({envelope.pixels} bytes); this write "
            "path copies the donor's proven geometry verbatim, and neither a larger "
            "frame (an unproven composition shape) nor a smaller one (an unmeasured "
            "placement) is authored here")


# --- colour ------------------------------------------------------------------


def _colour_word(raw: int) -> int:
    """One palette entry's colour as the 15-bit word the write path can produce.

    Bit 15 of a GBA palette entry is not part of the colour, and the SDK's own
    :func:`sprite_graphics.expand_bgr555` already masks it away, so an entry whose
    stored word carries it holds the same colour as the 15-bit form.
    """
    return raw & 0x7FFF


def _assign_palette(palette, palette_offset: int, sprites,
                    identity: NewSpriteIdentity) -> _Palette:
    """Every authored pixel's palette index, and the entries that need writing.

    Reuse is decided on the palette WORD rather than on an expanded RGB triple, so
    two source colours that the hardware cannot tell apart are one entry here as
    well as on screen. The word compared is the entry's 15-bit colour
    (:func:`_colour_word`), because the SDK's own decode ignores bit 15 and the
    write path's :func:`sprite_graphics.pack_gba_colour` can only produce 15-bit
    words - a strict comparison would fail to see a colour the palette already
    displays and write a duplicate entry for it. Index 0 is never reused and never
    written: it is the transparent entry the chroma key maps to.

    An entry cannot be both reused for the colour it already holds and overwritten
    with a different one. Reusing one reserves it - it leaves the free list - and a
    written entry is no longer a candidate for the colour it used to hold, so a
    pixel the planner mapped to an entry always displays the colour it was authored
    with. Between two entries showing the same colour, one the caller offered as
    free and one it did not, the preserved entry wins: reusing the free one would
    reserve capacity the artwork may still need.
    """
    free = _requested_free_entries(sprites, identity)
    remaining = list(free)
    holders: dict[int, list[int]] = {}
    for index in range(TRANSPARENT_INDEX + 1, sg.PALETTE_ENTRIES):
        holders.setdefault(_colour_word(palette.raw[index]), []).append(index)
    held: dict[int, int] = {}
    written: dict[int, tuple[int, Colour]] = {}
    cells: list[_Cell] = []
    for animation_index, source in enumerate(identity.animations):
        sheet = source.sheet
        for slot in range(sheet.frame_cells):
            frame_index, direction = divmod(slot, DIRECTION_COUNT)
            cell_index = sheet.slot_cell_index(frame_index, direction)
            raw = sheet.cell(cell_index)
            out = bytearray()
            for start in range(0, len(raw), 3):
                pixel = (raw[start], raw[start + 1], raw[start + 2])
                if pixel == sheet.transparent_colour:
                    out.append(TRANSPARENT_INDEX)
                    continue
                word = sg.pack_gba_colour(*pixel)
                index = held.get(word)
                if index is None:
                    index = _reuse_entry(holders.get(word, ()), remaining, written)
                    if index is None:
                        index = _take_free_entry(remaining, palette, word, pixel)
                        written[index] = (word, sg.expand_bgr555(word))
                    held[word] = index
                out.append(index)
            cells.append(_Cell(
                animation_index=animation_index, slot=slot, frame_index=frame_index,
                direction=direction, sheet_cell=cell_index, sheet_name=source.name,
                pixels=bytes(out)))
    entries = tuple(
        AuthoredPaletteEntry(
            index=index, word=word, colour=colour,
            previous_word=palette.raw[index],
            file_offset=palette_offset + 2 * index)
        for index, (word, colour) in sorted(written.items())
    )
    return _Palette(cells=tuple(cells), entries=entries)


def _requested_free_entries(sprites, identity: NewSpriteIdentity) -> tuple[int, ...]:
    """The caller's free entries, checked against the graphics the corpus decoded."""
    for index in identity.free_palette_entries:
        users = sprites.palette_users(index)
        if users:
            raise SpriteIdentityError(
                f"object-palette entry {index} is requested as free, but "
                f"{len(users)} decoded actor-sprite graphic(s) draw it; writing this "
                "identity's colour there would recolour them")
    return identity.free_palette_entries


def _reuse_entry(candidates, remaining: list[int], written: dict) -> int | None:
    """An entry that already displays this colour, or None.

    ``candidates`` is every entry that held the colour before this plan ran, in
    ascending order. An entry the caller did not offer as free is preferred: it
    costs nothing to use, while reusing an entry that IS free must reserve it, and
    a later colour may have nowhere else to go. An entry this plan has already
    written is not a candidate for the colour it used to hold - it does not show
    that colour any more.
    """
    for index in candidates:
        if index not in written and index not in remaining:
            return index
    for index in candidates:
        if index not in written and index in remaining:
            remaining.remove(index)
            return index
    return None


def _take_free_entry(remaining: list[int], palette, word: int, pixel: Colour) -> int:
    """Consume one requested free entry, or refuse rather than approximate.

    The entry chosen is the one whose current colour is nearest the needed colour,
    and the lowest index on a tie. That ordering is determinism first: if an
    undecoded payload does draw the entry, the visible change is as small as this
    write path can make it, and the same input always takes the same entry.
    """
    if not remaining:
        raise SpriteIdentityError(
            f"the artwork needs the colour {pixel}, which packs to palette word "
            f"0x{word:04X}, and no entry holds it; every requested free entry is "
            "already taken, and this write path will not substitute a different "
            "colour for the one that was authored")
    display = sg.expand_bgr555(word)
    chosen = min(remaining, key=lambda i: (
        max(abs(palette.rgb[i][channel] - display[channel]) for channel in range(3)), i))
    remaining.remove(chosen)
    return chosen


# --- encoders ----------------------------------------------------------------


def _encode_frame(piece, container_address: int) -> bytes:
    """One frame record: a single piece, the donor's geometry, our container.

    The frame's bounding box and the piece's placement and extents are the
    donor's own values, so the authored record draws exactly what the donor draws
    and only the container pointer is new.
    """
    geometry = struct.pack("<bbBB", piece.x, piece.y, piece.dim_0, piece.dim_1)
    return (struct.pack("<I", 1) + geometry + geometry
            + struct.pack("<II", piece.attributes, container_address))


# --- shared helpers ----------------------------------------------------------


def _occupied(document, reserved: tuple[OwnedRegion, ...]) -> tuple[OwnedRegion, ...]:
    """Everything the allocator must place clear of, in the established form.

    The same set `webfoot.relocation.plan_relocation` uses: every anchor, plus
    every reference field that does not sit inside an anchor, plus the build's own
    reservations from earlier domains.
    """
    occupied = [OwnedRegion(anchor.range, anchor.owner) for anchor in document.anchors]
    for reference in document.references:
        if not any(anchor.range.contains(reference.source) for anchor in document.anchors):
            occupied.append(
                OwnedRegion(reference.source_range, f"reference:{reference.target.value}")
            )
    occupied.extend(reserved)
    return tuple(occupied)


def _file_offset(address: int, image_size: int, what: str) -> int:
    from .binary import GbaRomAddress

    try:
        return GbaRomAddress(address).to_file_offset(image_size)
    except BinaryAddressError as exc:
        raise SpriteIdentityError(
            f"{what} is named by 0x{address:08X}, which is not a file offset in this "
            f"{image_size}-byte image") from exc


def _require_colour(value, what: str) -> None:
    if (not isinstance(value, tuple) or len(value) != 3
            or any(type(channel) is not int or not 0 <= channel <= 255
                   for channel in value)):
        raise SpriteIdentityError(
            f"{what} must be three 0..255 channels, not {value!r}")
