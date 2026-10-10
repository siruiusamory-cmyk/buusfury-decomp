"""The Graphics destination's model: actor sprites, payloads, appearances and the palette.

Four systems, told apart on every surface, because two of them are the same
bytes to a careless reader:

1. *Actor sprite identity.* One character-table slot, ``profile/character:NNNN``.
   The engine's own key is the slot index; the ROM carries no name, so none is
   invented.
2. *Graphics payloads.* One shared container, ``profile/graphic:NNNN``.
   A payload is reached by frame records, several frames may reach one payload,
   and several characters may reach those frames.
3. *Appearance records.* One 16-byte row of the appearance-definition table,
   addressed by its table index.
4. *The object palette.* ONE table of 256 entries for the whole image.

**There is one global object palette and a palette index is shared.** A palette
index is not owned by a sprite: every graphic whose pixels reference it changes
when it is recoloured, and that is a property of the ROM rather than a limitation
of this code. So the surface discloses, for the entry it offers to edit, which
decoded actor-sprite graphics reference it and which characters they belong to.

**The consumer count has a corpus, and it is stated.** ``palette_users`` scans
the pixels of the decoded ACTOR-SPRITE graphics only. Map tilesets, portraits,
UI, HUD and font tiles are drawn through paths this project has not decoded, so
their use of an index is neither counted nor excluded. Where the corpus cannot be
read at all, a row says ``unknown`` and never ``0``.

**Which palette bank a sprite uses is not decoded anywhere in this project**, so
no per-sprite palette and no bank label appears here. The SDK's own sprite viewer
made the same refusal, and the field does not exist to label.

**The one editable relation, and why it is the only one.** The build already
emits an authored palette recolour as a `ByteChange` whose owner is
``palette_entry:NNN`` (`webfoot/build.py:1648-1657`), so a recolour is integrated,
attributable and reversible. The SDK names that two-byte in-place write the
supported path for a visible change, for a measured reason: a payload re-encode
has to re-compress and usually cannot fit its original container
(`webfoot/graphics.py:582-598`). An authored pixel import is a PNG file in the
project's asset tree rather than a project document, so it is not a payload this
destination can carry through the one journal, and it is not offered here.

Everything else on this page is read-only or inert, each stating its reason.

No Qt is imported: a test drives every answer with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.webfoot.appearances import AppearanceError, AppearanceRecord, read_records
from tools.webfoot.binary import GBA_ROM_BASE, FileOffset
from tools.webfoot.formats import sprite_graphics as sg
from tools.webfoot.graphics import (
    ActorSprites,
    Graphic,
    GraphicsError,
    load_actor_sprites,
)
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfile
from tools.webfoot.rom import RomIdentification
from tools.webfoot.write import ByteChange

#: The five views this destination carries, in view order.
SPRITES = "sprites"
PAYLOADS = "payloads"
APPEARANCES = "appearances"
PALETTE = "palette"
OTHER = "other"
MODES: tuple[str, ...] = (SPRITES, PAYLOADS, APPEARANCES, PALETTE, OTHER)

MODE_LABELS = {
    SPRITES: "Actor sprites",
    PAYLOADS: "Sprite payloads",
    APPEARANCES: "Appearance records",
    PALETTE: "Object palette",
    OTHER: "Other graphics systems",
}

#: The object palette's extent, from the SDK's own codec constant.
PALETTE_ENTRIES = sg.PALETTE_ENTRIES

#: The SDK's declared transparent entry. A recolour of it is inert rather than
#: forbidden: the codec draws nothing for it, so no actor sprite shows the colour.
TRANSPARENT_INDEX = sg.TRANSPARENT_INDEX

#: What each view is, in one sentence, stated above its table.
VIEW_LINES = {
    SPRITES: (
        "Actor sprite identity: one character-table slot per row. The ROM carries "
        "no name for a slot, so the slot index is the identity and no name is "
        "invented. Read-only: authoring a new identity is the SDK's sprite "
        "authoring path, not an edit of an existing slot."
    ),
    PAYLOADS: (
        "Sprite payloads: one shared graphics container per row, with the frame "
        "records that reach it. A payload reached by more than one frame is drawn "
        "in every one of them, and every character listed changes with it. "
        "Read-only: an authored payload is a PNG in the project's asset tree, not "
        "a document the one journal can carry."
    ),
    APPEARANCES: (
        "Appearance definitions: one 16-byte table record per row. Two fields are "
        "the ROM's own pointer-table indices, the sprite id is an engine id, and "
        "the portrait slot is the SDK's own field name for the record's +0x08. "
        "Read-only: the SDK grows this table by appending NEW definitions, and no "
        "path edits an existing canonical record."
    ),
    PALETTE: (
        "The one global object palette: 256 entries shared by every graphic whose "
        "pixels reference an index. A recolour is offered per entry and is disclosed "
        "with the consumers this project can count. Which palette bank a given "
        "sprite uses is not decoded anywhere in this project, so no per-sprite "
        "palette is shown and no bank is named."
    ),
    OTHER: (
        "Graphics systems outside the actor-sprite pipeline, as the repository's "
        "own coverage matrix measured them: which exist, which population is "
        "proven, and which have no editor here. Every row is inert, and none of "
        "them is named something the evidence does not name."
    ),
}

#: The palette view's own line. The build's owner identity is quoted because it is
#: what a person sees in the write manifest, and the shared-consumer sentence is
#: the one fact that makes this edit safe or unsafe.
PALETTE_IDENTITY_LINE = (
    "Identity: the object palette's entry index, 0..255, shared by every graphic "
    "whose pixels reference it. Storage: the {size}-byte object palette at file "
    "offset 0x{offset:06X} ({address}). A recolour is an exact two-byte write and "
    "the build records it under owner palette_entry:NNN."
)

PALETTE_DISCLOSURE = (
    "One global palette: recolouring entry 0x{index:02X} changes every graphic "
    "whose pixels reference it, and the same index reaches whichever sprite bank "
    "the engine selects. Which bank a given sprite uses is not decoded anywhere in "
    "this project, so no per-sprite palette is shown and no bank is named."
)

#: Graphics systems with no editor here, and the reason each is inert. Every
#: sentence is the coverage matrix's own verdict, with its line in
#: `docs/research/GRAPHICS_COVERAGE.md`; none of them invents a name or a
#: capability. The last field is that citation.
OTHER_SYSTEMS: tuple[tuple[str, str, str, str], ...] = (
    (
        "Portraits",
        "enumerable, reference coverage proven, no export",
        "155 Webfoot containers at the portrait pointer array, every one form 1 "
        "decoding to 4,096 bytes, reached through the appearance-definition "
        "table's +0x08 field. No portrait's palette or on-screen size is decoded "
        "anywhere, so no portrait is drawn, exported or edited here.",
        "docs/research/GRAPHICS_COVERAGE.md:51",
    ),
    (
        "UI, HUD and menus",
        "literal-named population enumerated, completeness not proven",
        "34 containers named by engine code literals and disjoint from the "
        "actor-sprite corpus, 7 of which render correctly. No pointer table bounds "
        "the family and the graphics identity of 27 is unknown, so this is a count "
        "for that rule rather than a list of all UI graphics.",
        "docs/research/GRAPHICS_COVERAGE.md:49",
    ),
    (
        "Fonts and glyphs",
        "system located, glyph population unknown",
        "A font descriptor and glyph source are located and glyphs are blitted "
        "per code unit, but the glyph-bank extent, glyph count and exact tile "
        "format were not bound. No font is rendered or edited here.",
        "docs/research/GRAPHICS_COVERAGE.md:52",
    ),
    (
        "Title, static and cutscene graphics",
        "unresolved",
        "One load-descriptor table names 7 containers outside the actor-sprite "
        "corpus, 6 of them about 65 KB, and no rendering consumer was traced. "
        "Whether they are graphics at all is not established, so no name and no "
        "preview is offered.",
        "docs/research/GRAPHICS_COVERAGE.md:53",
    ),
    (
        "Map tilesets and map graphics below the chunk level",
        "read-only today",
        "187 tileset banks are accepted as containers and their pixel identity is "
        "unresolved; chunk-level file authoring, tileset and screen-entry editing "
        "are deferred by the V1.0 scope. The Maps destination shows map graphics "
        "as they are read; this destination offers nothing here.",
        "docs/research/GRAPHICS_COVERAGE.md:54",
    ),
    (
        "Ki blasts and effects",
        "no separate system found",
        "The coverage matrix found no effects-only graphics table outside the "
        "actor-sprite pipeline in what was searched, and a ki blast is observed as "
        "an ordinary actor object. Where effects are sprites they are already the "
        "payloads above.",
        "docs/research/GRAPHICS_COVERAGE.md:50",
    ),
)


class GraphicsSurfaceError(ValueError):
    """The open image's actor-sprite, appearance or palette records were not read."""


@dataclass(frozen=True, slots=True)
class CharacterRow:
    """One character-table slot: the engine's own identity for one actor sprite."""

    identity: str
    index: int
    file_offset: int
    address: int
    animations: int
    payloads: int
    note: str


@dataclass(frozen=True, slots=True)
class PayloadRow:
    """One shared graphics container, with the frames and characters it reaches."""

    identity: str
    index: int
    file_offset: int
    address: int
    width: int
    height: int
    bit_depth: int
    packed_size: int
    frames: tuple[int, ...]
    characters: tuple[str, ...]
    editable: bool
    note: str

    @property
    def shared(self) -> bool:
        """True when more than one distinct frame record reaches this payload."""
        return len(self.frames) > 1

    @property
    def disclosure(self) -> str:
        """The consumers, counted by what the walk decoded rather than guessed."""
        if not self.frames:
            return (
                "no decoded frame record reaches this payload; the walk that "
                "decoded this corpus reached it from no animation"
            )
        characters = (
            ", ".join(self.characters) if self.characters else "no decoded character"
        )
        return (
            f"{len(self.frames)} distinct frame record(s) at "
            f"{', '.join(f'0x{offset:06X}' for offset in self.frames[:12])}"
            f"{' and more' if len(self.frames) > 12 else ''} reach this payload, "
            f"from {characters}"
        )


@dataclass(frozen=True, slots=True)
class AppearanceRow:
    """One appearance-definition record, in the SDK's own field names."""

    index: int
    file_offset: int
    address: int
    text_index: int
    description_index: int
    sprite_id: int
    portrait_slot: int
    stat_index: int
    note: str


@dataclass(frozen=True, slots=True)
class PaletteRow:
    """One object-palette entry and the consumers this project can actually count.

    The count has a corpus and the row says so rather than implying the whole
    image: a row reads ``0 of N decoded actor-sprite graphics`` and then names
    what was not counted. It never reads as "unused".
    """

    index: int
    rgb: tuple[int, int, int]
    raw: int
    users: tuple[str, ...]
    corpus: int
    editable: bool
    unsupported_reason: str

    @property
    def consumer_text(self) -> str:
        """What is known about this entry's consumers, corpus and all.

        The negative is deliberately not a bare zero: the count covers the decoded
        actor-sprite graphics only, so a row with no user in that corpus cannot
        claim to be unused anywhere.
        """
        outside = (
            "consumers outside the decoded actor-sprite corpus, such as portraits, "
            "UI, HUD and font tiles, are not counted and not excluded"
        )
        if not self.users:
            return f"0 of {self.corpus} decoded actor-sprite graphics; {outside}"
        shown = ", ".join(self.users[:12])
        more = f" and {len(self.users) - 12} more" if len(self.users) > 12 else ""
        return (
            f"{len(self.users)} of {self.corpus} decoded actor-sprite graphics: "
            f"{shown}{more}; {outside}"
        )


@dataclass(frozen=True, slots=True)
class OtherRow:
    """One graphics system outside the actor-sprite pipeline, and why it is inert."""

    name: str
    status: str
    reason: str
    evidence: str


@dataclass(frozen=True, slots=True)
class GraphicsSurface:
    """One open image's actor sprites, payloads, appearance records and palette."""

    identification: RomIdentification
    profile: RomProfile
    image: bytes
    sprites: ActorSprites | None
    sprites_problem: str
    appearances: tuple[AppearanceRecord, ...]
    appearances_problem: str
    palette_address: int
    palette_problem: str

    # -- the palette, the one editable relation ---------------------------------

    def palette_rows(self) -> tuple[PaletteRow, ...]:
        """Every entry of the one global object palette.

        The corpus size is stated on every row so the count's scope travels with
        the count. With no decoded corpus there is no count and no row: a palette
        reader of its own would be a second palette authority, so the page states
        the corpus's own refusal instead.
        """
        if self.sprites is None:
            return ()
        raw = self.sprites.palette.raw
        rgb = self.sprites.palette.rgb
        corpus = len(self.sprites.graphics())
        rows = []
        for index in range(PALETTE_ENTRIES):
            users = self.sprites.palette_users(index)
            rows.append(
                PaletteRow(
                    index=index,
                    rgb=rgb[index],
                    raw=raw[index],
                    users=tuple(str(identity) for identity in users),
                    corpus=corpus,
                    editable=index != TRANSPARENT_INDEX,
                    unsupported_reason=(
                        ""
                        if index != TRANSPARENT_INDEX
                        else "entry 0 is the SDK's declared transparent index"
                    ),
                )
            )
        return tuple(rows)

    def palette_row(self, index: int) -> PaletteRow:
        for row in self.palette_rows():
            if row.index == index:
                return row
        raise GraphicsSurfaceError(
            f"palette index {index} is outside 0..{PALETTE_ENTRIES - 1}"
        )

    def palette_identity_line(self) -> str:
        """Where this document's identity and storage come from, in one sentence."""
        return PALETTE_IDENTITY_LINE.format(
            size=PALETTE_ENTRIES * 2,
            offset=self.palette_address,
            address=f"0x{self.palette_address + GBA_ROM_BASE:08X}",
        )

    def palette_disclosure(self, index: int) -> str:
        """The shared-consumer disclosure for one entry, in the ROM's own terms."""
        return (
            PALETTE_DISCLOSURE.format(index=index)
            + " "
            + self.palette_row(index).consumer_text
        )

    def owners_of(self, index: int) -> tuple[str, ...]:
        """The characters affected by recolouring one entry, through its graphics.

        The graphics are the SDK's own ``palette_users`` answer; the characters
        come from the same corpus's own consumer traversal, so the sequence from
        an index to an actor is decoded rather than inferred.
        """
        if self.sprites is None:
            return ()
        seen: list[str] = []
        for identity in self.sprites.palette_users(index):
            for character in self.sprites.characters_using(identity):
                if str(character) not in seen:
                    seen.append(str(character))
        return tuple(seen)

    def plan(
        self, index: int, rgb: tuple[int, int, int]
    ) -> tuple[str, tuple[ByteChange, ...], tuple[RomRange, ...]]:
        """One palette edit staged through the SDK: refusal, changes, claimed spans.

        The three answers a single edit needs, from ONE staging, because they must
        agree. The SDK's own `plan_palette_entry_rgb` does the RGB-to-word packing
        and returns the exact two bytes the entry occupies, so this mints no
        address and no colour of its own. The owner is the build's own
        ``palette_entry:NNN``, so the journal entry and the write manifest name the
        same object.
        """
        if self.sprites is None:
            return (self.sprites_problem or "no actor-sprite corpus is loaded", (), ())
        if type(index) is not int or not 0 <= index < PALETTE_ENTRIES:
            return (f"palette index {index!r} is outside 0..{PALETTE_ENTRIES - 1}", (), ())
        red, green, blue = rgb
        try:
            offset, new = self.sprites.plan_palette_entry_rgb(index, red, green, blue)
        except (GraphicsError, ValueError) as exc:
            return (str(exc), (), ())
        old = self.image[offset : offset + len(new)]
        if old == new:
            return ("", (), ())
        change = ByteChange(
            offset=offset,
            old=old,
            new=new,
            owner=f"palette_entry:{index:03d}",
            reason=(
                f"object palette entry {index:03d} recoloured to "
                f"rgb({red}, {green}, {blue})"
            ),
        )
        claimed = (RomRange(FileOffset(offset), len(new)),)
        return ("", (change,), claimed)

    def changes(self, project: object | None) -> tuple[ByteChange, ...]:
        """Every pending palette edit the open project authors, owner-bearing.

        Staged through the same `plan` the page commits through, and filtered to
        the entries that actually differ, so the owner is always the build's own
        `palette_entry:NNN` and nothing here mints an identity.
        """
        if project is None or self.sprites is None:
            return ()
        palette = getattr(project, "graphics_overrides", None)
        if palette is None:
            return ()
        staged: list[ByteChange] = []
        for index in sorted(palette.palette):
            _problem, changes, _claimed = self.plan(index, palette.palette[index])
            staged.extend(change for change in changes if change.old != change.new)
        return tuple(staged)

    def pending_bytes(self, project: object | None) -> dict[int, bytes]:
        """The byte effect of every pending palette edit, keyed by file offset."""
        return {change.offset: change.new for change in self.changes(project)}

    # -- the read-only views ----------------------------------------------------

    def character_rows(self) -> tuple[CharacterRow, ...]:
        """Every character-table slot the walk decoded, in identity order."""
        if self.sprites is None:
            return ()
        return tuple(
            CharacterRow(
                identity=str(character.identity),
                index=character.identity.index,
                file_offset=character.file_offset,
                address=character.file_offset + GBA_ROM_BASE,
                animations=len(character.animation_offsets),
                payloads=len(character.graphics),
                note=(
                    "read-only: a new identity is authored through the SDK's sprite "
                    "authoring document, not by editing an existing slot"
                ),
            )
            for character in self.sprites.characters()
        )

    def payload_rows(self) -> tuple[PayloadRow, ...]:
        """Every distinct graphics payload, in identity order."""
        if self.sprites is None:
            return ()
        return tuple(
            _payload_row(graphic) for graphic in self.sprites.graphics()
        )

    def appearance_rows(self) -> tuple[AppearanceRow, ...]:
        """Every appearance-definition record the profile declares."""
        offset = _appearance_offset(self.profile, len(self.image))
        return tuple(
            AppearanceRow(
                index=index,
                file_offset=offset + index * 0x10,
                address=offset + index * 0x10 + GBA_ROM_BASE,
                text_index=record.text_index,
                description_index=record.description_index,
                sprite_id=record.sprite_id,
                portrait_slot=record.portrait_slot,
                stat_index=record.stat_index,
                note=(
                    "read-only: the portrait slot is the SDK's own name for the "
                    "record's +0x08, and the portrait's palette and on-screen size "
                    "are not decoded anywhere, so no portrait is drawn beside this row"
                ),
            )
            for index, record in enumerate(self.appearances)
        )

    def other_rows(self) -> tuple[OtherRow, ...]:
        """The graphics systems with no editor here, in the matrix's own words."""
        return tuple(OtherRow(*entry) for entry in OTHER_SYSTEMS)

    # -- the summaries the page states -----------------------------------------

    def sprite_summary(self) -> str:
        if self.sprites is None:
            return f"Actor sprites: not read. {self.sprites_problem}"
        return (
            f"Actor sprites: {len(self.sprites.characters())} character-table "
            f"slot(s) decoded, reaching {len(self.sprites.graphics())} distinct "
            "payload(s)"
        )

    def payload_summary(self) -> str:
        if self.sprites is None:
            return f"Payloads: not read. {self.sprites_problem}"
        rows = self.payload_rows()
        shared = sum(1 for row in rows if row.shared)
        return (
            f"Payloads: {len(rows)} container(s), {shared} reached by more than one "
            "frame record"
        )

    def appearance_summary(self) -> str:
        if self.appearances_problem:
            return f"Appearance definitions: not read. {self.appearances_problem}"
        return (
            f"Appearance definitions: {len(self.appearances)} record(s), every one "
            "read-only here"
        )

    def palette_summary(self, project: object | None) -> str:
        if self.sprites is None:
            return f"Object palette: not read. {self.sprites_problem}"
        authored = 0
        if project is not None:
            palette = getattr(project, "graphics_overrides", None)
            if palette is not None:
                authored = len(palette.palette)
        changes = len(self.changes(project))
        return (
            f"Object palette: {PALETTE_ENTRIES} entries, {authored} authored by the "
            f"open project, {changes} of them differing from the canonical image"
        )


def _payload_row(graphic: Graphic) -> PayloadRow:
    return PayloadRow(
        identity=str(graphic.identity),
        index=graphic.identity.index,
        file_offset=graphic.file_offset,
        address=graphic.file_offset + GBA_ROM_BASE,
        width=graphic.width,
        height=graphic.height,
        bit_depth=8 if graphic.colour_256 else 4,
        packed_size=graphic.packed_size,
        frames=tuple(consumer.frame_offset for consumer in graphic.consumers),
        characters=tuple(str(character) for character in graphic.characters),
        editable=False,
        note=(
            "read-only: pixels are authored by editing the project's extracted PNG, "
            "not by a project document the one journal writes, and the SDK's own "
            "write path for a visible change is the palette entry"
        ),
    )


def _appearance_offset(profile: RomProfile, image_size: int) -> int:
    layout = getattr(profile, "appearances", None)
    if layout is None:
        return 0
    return layout.address.to_file_offset(image_size)


def load_graphics_surface(
    identification: RomIdentification,
    profile: RomProfile,
    image: bytes,
) -> GraphicsSurface:
    """Read one already-identified image's graphics records.

    Each family is loaded through the module that owns it, and a family that
    refuses states its reason on the surface rather than failing the destination:
    an image whose profile declares no actor-sprite family still shows its
    appearance records and the coverage view. The palette rows are the one thing
    that cannot exist without the sprite corpus, because the palette and its
    users come from that same walk.
    """
    sprites: ActorSprites | None = None
    sprites_problem = ""
    palette_address = 0
    palette_problem = ""
    try:
        sprites = load_actor_sprites(image, identification)
        palette_address = profile.actor_sprites.object_palette_address.to_file_offset(
            len(image)
        )
    except (GraphicsError, ValueError, OSError) as exc:
        sprites_problem = str(exc)
        palette_problem = str(exc)

    appearances: tuple[AppearanceRecord, ...] = ()
    appearances_problem = ""
    try:
        appearances = read_records(image, profile)
    except (AppearanceError, ValueError, OSError) as exc:
        appearances_problem = str(exc)

    return GraphicsSurface(
        identification=identification,
        profile=profile,
        image=image,
        sprites=sprites,
        sprites_problem=sprites_problem,
        appearances=appearances,
        appearances_problem=appearances_problem,
        palette_address=palette_address,
        palette_problem=palette_problem,
    )


__all__ = [
    "APPEARANCES",
    "MODES",
    "MODE_LABELS",
    "OTHER",
    "OTHER_SYSTEMS",
    "PALETTE",
    "PALETTE_ENTRIES",
    "PAYLOADS",
    "SPRITES",
    "TRANSPARENT_INDEX",
    "AppearanceRow",
    "CharacterRow",
    "GraphicsSurface",
    "GraphicsSurfaceError",
    "OtherRow",
    "PaletteRow",
    "PayloadRow",
    "load_graphics_surface",
]
