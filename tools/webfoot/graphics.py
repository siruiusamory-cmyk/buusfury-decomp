"""Semantic actor-sprite assets: stable identities, sharing, and safe edits.

TOOLKIT-010. The layer above `webfoot.formats.sprite_graphics`, and the one a
caller actually authors against. It answers three questions the raw codec
cannot: what is this asset called, who else uses it, and may I change it.

**Identity is never an address.** A ROM offset is provenance; it changes the
moment anything moves, and a project keyed on it would break on its own next
build. Assets are named by *what they are* within a verified profile:

    buus_fury_usa_rev0_01c1707f/graphic:0413
    buus_fury_usa_rev0_01c1707f/character:0007

The numeric part is a position in a deterministic enumeration of the corpus, so
the same ROM always yields the same names, and the name survives a rebuild.

**Sharing is represented, not flattened.** Of the 7,355 graphics in the
canonical corpus, 2,986 are reached by more than one frame record and 2,644 are
used by more than one character; one is used by eight. Extracting a private copy
per consumer would turn 7,355 real payloads into 10,959 fictional ones and make
"edit this character" quietly rewrite others. So a graphic is one asset carrying
its consumers, and :meth:`consumers_of` and :meth:`characters_using` are not
diagnostic conveniences: they are what a caller must read before editing.

**What is deliberately absent.** There is no `Sprite` class, no direction names,
no character names, and no animation labels. The ROM supplies none of those, and
`docs/research/GRAPHICS_FORMAT.md` records the reasoning. A frame's four
pointers are four numbered slots; whether slot 0 is "down" is a gameplay claim
this project has not established and will not assert for API convenience.

**Enemy linkage is not attempted here.** TOOLKIT-009 verified placement types
reaching enemy stat records, but no verified static path runs from an enemy
record to a graphics asset, so none is invented. Graphics assets are
independently addressable, which is why the pipeline is useful without it.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import capability
from .binary import GBA_ROM_BASE
from .formats import sprite_graphics as sg
from .formats import webfoot_lz
from .profile import RomProfile
from .rom import RomIdentification


class GraphicsError(capability.CapabilityError):
    """Unverified profile, malformed sprite record, or an unsafe edit."""


@dataclass(frozen=True, order=True)
class GraphicIdentity:
    """Stable name for one shared graphics payload."""

    profile_id: str
    index: int

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise GraphicsError("graphic identity requires a profile")
        if type(self.index) is not int or self.index < 0:
            raise GraphicsError("graphic index must be a non-negative integer")

    def __str__(self) -> str:
        return f"{self.profile_id}/graphic:{self.index:04d}"


@dataclass(frozen=True, order=True)
class CharacterIdentity:
    """Stable name for one entry of the character pointer table.

    The index is the table slot, which is the engine's own key - unlike a name,
    which the ROM does not supply. Slots whose structure carries no decodable
    animation still exist and keep their index; they are simply not listed as
    characters, so numbering never shifts because a neighbour failed to decode.
    """

    profile_id: str
    index: int

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise GraphicsError("character identity requires a profile")
        if type(self.index) is not int or self.index < 0:
            raise GraphicsError("character index must be a non-negative integer")

    def __str__(self) -> str:
        return f"{self.profile_id}/character:{self.index:04d}"


@dataclass(frozen=True, order=True)
class FrameRef:
    """One distinct frame record that reaches a graphic, and where it sits.

    A frame is identified by its file offset because - unlike a graphic - it is
    an interior structural node the project does not export as an asset. The
    offset is provenance for a consumer list, never a project-visible name.

    **A consumer is a distinct frame record, not a traversal path.** The same
    frame is reachable by several routes, because 333 animations are shared
    between characters: the canonical image has 10,959 distinct frames but
    20,760 routes to them. Counting routes would overstate sharing, so the
    consumer list is deduplicated by ``frame_offset`` and the remaining fields
    record the first route that reached it in deterministic order.
    :meth:`ActorSprites.characters_using` reports the affected characters, which
    is the question an editor actually needs answered.
    """

    frame_offset: int
    character_index: int
    animation_index: int
    frame_index: int
    direction: int


@dataclass(frozen=True)
class Graphic:
    """One shared graphics payload as a project asset."""

    identity: GraphicIdentity
    file_offset: int
    width: int
    height: int
    colour_256: bool
    pixels: bytes
    packed_size: int
    consumers: tuple[FrameRef, ...]
    characters: tuple[CharacterIdentity, ...]

    @property
    def shared(self) -> bool:
        """True when more than one distinct frame record reaches this payload."""
        return len(self.consumers) > 1

    def to_document(self) -> dict:
        """Deterministic, address-light description for project output.

        ``file_offset`` is included and labelled provenance rather than omitted:
        a mod author debugging a build needs to find the bytes, and hiding the
        offset does not make the project format address-independent - keying on
        it would. Nothing downstream resolves an asset *by* this number.
        """
        return {
            "id": str(self.identity),
            "width": self.width,
            "height": self.height,
            "bit_depth": 8 if self.colour_256 else 4,
            "transparent_index": sg.TRANSPARENT_INDEX,
            "packed_size": self.packed_size,
            "shared": self.shared,
            "consumer_count": len(self.consumers),
            "characters": [str(c) for c in self.characters],
            "provenance_file_offset": self.file_offset,
        }


@dataclass(frozen=True)
class Character:
    """One character-table entry and the animations reached from it."""

    identity: CharacterIdentity
    file_offset: int
    animation_offsets: tuple[int, ...]
    graphics: tuple[GraphicIdentity, ...]

    def to_document(self) -> dict:
        return {
            "id": str(self.identity),
            "animation_count": len(self.animation_offsets),
            "graphics": [str(g) for g in self.graphics],
            "provenance_file_offset": self.file_offset,
        }


class ActorSprites:
    """The decoded actor-sprite corpus for one exactly-verified ROM.

    Construction walks the whole corpus once. That is deliberate: sharing and
    consumer lists are only correct when every reference has been seen, so there
    is no lazy mode that could answer :meth:`consumers_of` from partial data.
    """

    def __init__(self, image: bytes, identification: RomIdentification) -> None:
        self.profile: RomProfile = capability.require(
            identification,
            capability.Capability.ACTOR_SPRITES,
            subsystem="actor sprites",
            error_type=GraphicsError,
        )
        layout = self.profile.actor_sprites
        assert layout is not None
        self.layout = layout
        self.base_bytes = bytes(image)
        size = len(self.base_bytes)

        self.table_offset = layout.character_table_address.to_file_offset(size)
        self.palette = sg.decode_palette(
            self.base_bytes, layout.object_palette_address.to_file_offset(size)
        )

        structures = self._read_structure_table()
        # Keyed by (graphic offset, frame offset) so a frame reached by several
        # routes contributes one consumer, keeping the first route seen.
        consumers: dict[int, dict[int, FrameRef]] = {}
        # Character membership is tracked separately and is NOT deduplicated by
        # frame: a shared animation means several characters legitimately reach
        # the same frame, and all of them are affected by an edit.
        users: dict[int, set[int]] = {}
        character_rows: list[tuple[int, int, tuple[int, ...], list[int]]] = []

        for slot, start in enumerate(structures):
            end = (
                structures[slot + 1]
                if slot + 1 < len(structures)
                else self.table_offset
            )
            animations = self._animations_in(start, end)
            if not animations:
                # A slot with no decodable animation is skipped rather than
                # reported as an empty character: 2 of 297 are like this, and
                # claiming them as characters with zero art would overstate what
                # was decoded.
                continue
            reached: list[int] = []
            for animation_index, animation_offset in enumerate(animations):
                animation = sg.decode_animation(self.base_bytes, animation_offset)
                for frame_index in range(animation.frame_count):
                    for direction in range(sg.DIRECTION_COUNT):
                        pointer = animation.pointer_for(frame_index, direction)
                        frame_offset = self._frame_offset(pointer)
                        if frame_offset is None:
                            continue
                        frame = sg.decode_frame(self.base_bytes, frame_offset)
                        for piece in frame.pieces:
                            graphic_offset = self._offset_of(piece.graphics_pointer)
                            if graphic_offset is None:
                                continue
                            consumers.setdefault(graphic_offset, {}).setdefault(
                                frame_offset,
                                FrameRef(
                                    frame_offset=frame_offset,
                                    character_index=slot,
                                    animation_index=animation_index,
                                    frame_index=frame_index,
                                    direction=direction,
                                ),
                            )
                            users.setdefault(graphic_offset, set()).add(slot)
                            reached.append(graphic_offset)
            character_rows.append((slot, start, tuple(animations), reached))

        # Enumeration order is ascending file offset, so the same ROM always
        # produces the same identities regardless of which character happened to
        # reach a shared payload first.
        self._graphics: dict[GraphicIdentity, Graphic] = {}
        self._by_offset: dict[int, GraphicIdentity] = {}
        for index, offset in enumerate(sorted(consumers)):
            identity = GraphicIdentity(self.profile.id, index)
            refs = tuple(sorted(consumers[offset].values()))
            first = refs[0]
            piece = self._piece_for(first.frame_offset, offset)
            width, height = piece.dimensions
            decoded = sg.decode_graphic(
                self.base_bytes, offset, width, height, colour_256=piece.colour_256
            )
            self._graphics[identity] = Graphic(
                identity=identity,
                file_offset=offset,
                width=width,
                height=height,
                colour_256=piece.colour_256,
                pixels=decoded.pixels,
                packed_size=decoded.packed_size,
                consumers=refs,
                characters=tuple(
                    sorted(
                        CharacterIdentity(self.profile.id, slot)
                        for slot in users.get(offset, ())
                    )
                ),
            )
            self._by_offset[offset] = identity

        self._characters: dict[CharacterIdentity, Character] = {}
        for slot, start, animations, reached in character_rows:
            identity = CharacterIdentity(self.profile.id, slot)
            self._characters[identity] = Character(
                identity=identity,
                file_offset=start,
                animation_offsets=animations,
                graphics=tuple(
                    sorted({self._by_offset[o] for o in reached if o in self._by_offset})
                ),
            )

    # --- enumeration ---------------------------------------------------------

    def graphics(self) -> tuple[Graphic, ...]:
        """Every distinct graphics payload, in stable identity order."""
        return tuple(self._graphics[k] for k in sorted(self._graphics))

    def characters(self) -> tuple[Character, ...]:
        """Every character-table slot that reached at least one graphic."""
        return tuple(self._characters[k] for k in sorted(self._characters))

    def graphic(self, identity: GraphicIdentity) -> Graphic:
        try:
            return self._graphics[identity]
        except KeyError:
            raise GraphicsError(f"unknown graphic: {identity}") from None

    def character(self, identity: CharacterIdentity) -> Character:
        try:
            return self._characters[identity]
        except KeyError:
            raise GraphicsError(f"unknown character: {identity}") from None

    def consumers_of(self, identity: GraphicIdentity) -> tuple[FrameRef, ...]:
        """Every frame that reaches this payload.

        Read this before editing. A caller that changes a graphic with several
        consumers changes all of them; that is a property of the ROM, not a
        limitation here, and the honest response is to make it visible rather
        than to fabricate a private copy.
        """
        return self.graphic(identity).consumers

    def characters_using(self, identity: GraphicIdentity) -> tuple[CharacterIdentity, ...]:
        """Every character affected by editing this payload.

        Derived from full traversal rather than from :attr:`Graphic.consumers`,
        which is deduplicated by frame: a shared animation lets several
        characters reach the very same frame record, and all of them change.
        """
        return self.graphic(identity).characters

    # --- the common reference graph ------------------------------------------

    def reference_document(self):
        """Publish the verified graphics pointers into the shared graph.

        Only pointers this project actually walked and decoded are published, and
        they are `CONFIRMED_REFERENCE` because each was checked twice over: the
        pointer resolved, and the payload it reached agreed with the OAM
        dimensions an unrelated record declared. Nothing is promoted from
        pointer *shape* - a scanner is not allowed to grow the graph, per the
        rule TOOLKIT-003 established.

        Frame pointers are deliberately left out. Publishing all 13,596 slots
        would triple the graph to restate what the animation records already say,
        and none of them is an edit target.
        """
        from .binary import FileOffset, GbaRomAddress
        from .document import RomDocument
        from .layout import (Anchor, AnchorId, Provenance, Reference,
                             ReferenceClass, ReferenceEncoding, RomRange)

        provenance = Provenance(
            self.profile.id, self.profile.sha256, self.layout.evidence
        )
        anchors: list[Anchor] = []
        references: list[Reference] = []

        def anchor(key: str, offset: int, size: int, kind: str, alignment: int = 1) -> None:
            anchors.append(
                Anchor(
                    AnchorId(key),
                    RomRange(FileOffset(offset), size),
                    kind,
                    key,
                    alignment,
                    False,
                    provenance,
                )
            )

        palette_id = f"{self.profile.id}/object_palette:0000"
        anchor(
            palette_id,
            self.layout.object_palette_address.to_file_offset(len(self.base_bytes)),
            sg.PALETTE_BYTES,
            "object_palette",
            alignment=2,
        )

        table_id = f"{self.profile.id}/character_table:0000"
        anchor(
            table_id,
            self.table_offset,
            self.layout.character_count * 4,
            "character_pointer_table",
            alignment=4,
        )

        for character in self.characters():
            anchor(str(character.identity), character.file_offset, 1,
                   "character_structure", alignment=4)
            references.append(
                Reference(
                    FileOffset(self.table_offset + character.identity.index * 4),
                    AnchorId(str(character.identity)),
                    0,
                    ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                    ReferenceClass.CONFIRMED_REFERENCE,
                    provenance,
                )
            )

        for graphic in self.graphics():
            key = str(graphic.identity)
            # The anchor spans the measured packed extent, which is the region an
            # edit is bounded by - not the decoded size, which is larger and
            # exists nowhere in the image.
            anchor(key, graphic.file_offset, graphic.packed_size,
                   "graphics_container", alignment=4)
            for reference in graphic.consumers:
                # The piece record's +0x0C word. One reference per distinct
                # frame, so a shared payload shows every route into it.
                references.append(
                    Reference(
                        FileOffset(reference.frame_offset + 4 + 0x0C),
                        AnchorId(key),
                        0,
                        ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                        ReferenceClass.CONFIRMED_REFERENCE,
                        provenance,
                    )
                )

        return RomDocument.from_bytes(
            self.base_bytes,
            self.profile,
            anchors=tuple(anchors),
            references=tuple(references),
        )

    # --- editing -------------------------------------------------------------

    def plan_palette_entry(self, index: int, colour: int) -> tuple[int, bytes]:
        """Recolour one palette entry, returning a ``(file_offset, bytes)`` change.

        This is the supported write path for a visible change, and the reason is
        capacity rather than preference: the object palette is uncompressed and
        fixed at 512 bytes, so a recolour is an exact two-byte in-place write
        with no re-encoding and no room to run out of. Pixel editing has to
        re-compress and usually cannot fit (see :meth:`plan_pixels`).

        ``colour`` is a raw GBA 15-bit word, not an RGB triple, because that is
        what the ROM stores: taking RGB here would mean quantising, and two
        different triples could silently land on one word.

        Every graphic using this index changes. The palette is global to the
        family, so this is a broad edit by nature - which is exactly why it is
        offered per entry rather than per asset, and why the caller decides
        which index is safe to touch.
        """
        if type(index) is not int or not 0 <= index < sg.PALETTE_ENTRIES:
            raise GraphicsError(
                f"palette index {index} is outside 0..{sg.PALETTE_ENTRIES - 1}"
            )
        if type(colour) is not int or not 0 <= colour <= 0x7FFF:
            raise GraphicsError(
                f"colour {colour} is not a 15-bit GBA word; bit 15 is unused on "
                "this hardware and must stay clear"
            )
        offset = self.layout.object_palette_address.to_file_offset(len(self.base_bytes))
        return offset + index * 2, colour.to_bytes(2, "little")

    def palette_users(self, index: int) -> tuple[GraphicIdentity, ...]:
        """Every graphic whose pixels reference this palette index.

        The honest answer to "what does recolouring entry N affect". Computed by
        scanning decoded pixels rather than assumed, because a palette entry that
        looks unused may still be reached by an asset this walk did decode.
        """
        if type(index) is not int or not 0 <= index < sg.PALETTE_ENTRIES:
            raise GraphicsError(
                f"palette index {index} is outside 0..{sg.PALETTE_ENTRIES - 1}"
            )
        needle = bytes((index,))
        return tuple(
            graphic.identity
            for graphic in self.graphics()
            if needle in graphic.pixels
        )

    def plan_pixels(self, identity: GraphicIdentity, pixels: bytes) -> sg.PayloadPlan:
        """Validate and re-encode new pixels for one graphic.

        Raises rather than truncating, padding, or relocating. The refusal path
        is the important one: the corpus is packed with no slack and this
        profile declares no free space, so a payload that will not fit has
        nowhere legitimate to go.
        """
        graphic = self.graphic(identity)
        decoded = sg.Graphic(
            offset=graphic.file_offset,
            width=graphic.width,
            height=graphic.height,
            colour_256=graphic.colour_256,
            pixels=graphic.pixels,
            packed_end=graphic.file_offset + graphic.packed_size,
        )
        return sg.plan_graphic_payload(self.base_bytes, decoded, pixels)

    def apply_plan(self, plan: sg.PayloadPlan) -> tuple[int, bytes]:
        """Turn a payload plan into one contiguous ``(offset, bytes)`` change.

        The replacement is padded to the original extent with the ORIGINAL
        trailing bytes, not with zeroes. Nothing establishes that a container's
        tail is disposable - the next container often begins immediately after -
        so bytes this edit does not need are re-emitted exactly as they were.
        That also keeps the change one clean region for the write planner rather
        than a hole the build has to reason about.
        """
        tail_start = plan.offset + len(plan.payload)
        tail_end = plan.offset + plan.original_size
        preserved = self.base_bytes[tail_start:tail_end]
        return plan.offset, plan.payload + preserved

    # --- internals -----------------------------------------------------------

    def _read_structure_table(self) -> tuple[int, ...]:
        size = len(self.base_bytes)
        offsets = []
        for slot in range(self.layout.character_count):
            entry = self.table_offset + slot * 4
            pointer = int.from_bytes(self.base_bytes[entry : entry + 4], "little")
            offset = self._offset_of(pointer)
            if offset is None:
                raise GraphicsError(
                    f"character table entry {slot} is not a ROM pointer: {pointer:#010x}"
                )
            offsets.append(offset)
        if offsets != sorted(offsets):
            raise GraphicsError("character structure pointers are not ascending")
        if offsets and offsets[-1] >= size:
            raise GraphicsError("character structure runs past the image")
        return tuple(offsets)

    def _animations_in(self, start: int, end: int) -> tuple[int, ...]:
        """Animation pointers between a structure's header and the next structure.

        The extent is resolved by walking to the next structure rather than by
        trusting a count, for the same reason `webfoot.formats.map_slots` walks:
        no field in this header has been shown to bound the list.
        """
        found: list[int] = []
        seen: set[int] = set()
        cursor = start + self.layout.animation_pointer_offset
        while cursor + 4 <= end:
            pointer = int.from_bytes(self.base_bytes[cursor : cursor + 4], "little")
            offset = self._offset_of(pointer)
            if offset is not None and offset not in seen and self._is_animation(offset):
                seen.add(offset)
                found.append(offset)
            cursor += 4
        return tuple(found)

    def _is_animation(self, offset: int) -> bool:
        try:
            animation = sg.decode_animation(self.base_bytes, offset)
        except sg.SpriteFormatError:
            return False
        # An animation is accepted only when at least one of its frame pointers
        # resolves to a well-formed frame whose pieces all point at plausible
        # containers. Requiring evidence from the layer below is what keeps a
        # coincidental pair of small words from being read as art.
        for pointer in animation.frame_pointers[:12]:
            if self._frame_offset(pointer) is not None:
                return True
        return False

    def _frame_offset(self, pointer: int) -> int | None:
        offset = self._offset_of(pointer)
        if offset is None:
            return None
        try:
            frame = sg.decode_frame(self.base_bytes, offset)
        except sg.SpriteFormatError:
            return None
        for piece in frame.pieces:
            if piece.shape >= len(sg.OBJECT_DIMENSIONS):
                return None
            graphic = self._offset_of(piece.graphics_pointer)
            if graphic is None:
                return None
            if not webfoot_lz.looks_like_container(
                self.base_bytes, graphic, minimum_size=32, maximum_size=64 * 1024
            ):
                return None
        return offset

    def _piece_for(self, frame_offset: int, graphic_offset: int) -> sg.Piece:
        frame = sg.decode_frame(self.base_bytes, frame_offset)
        for piece in frame.pieces:
            if self._offset_of(piece.graphics_pointer) == graphic_offset:
                return piece
        raise GraphicsError(
            f"frame at {frame_offset:#x} does not reference {graphic_offset:#x}"
        )

    def _offset_of(self, pointer: int) -> int | None:
        """ROM pointer -> file offset, or None when it is not one."""
        if not GBA_ROM_BASE <= pointer < GBA_ROM_BASE + len(self.base_bytes):
            return None
        return pointer - GBA_ROM_BASE


def load_actor_sprites(image: bytes, identification: RomIdentification) -> ActorSprites:
    return ActorSprites(image, identification)
