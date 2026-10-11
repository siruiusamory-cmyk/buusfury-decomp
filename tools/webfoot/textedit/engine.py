"""The reusable text-edit engine: one model, one plan, one writer.

WHAT THIS IS. The five friend-v3 release scripts each carry one route with the
release's own rows hard-coded in them: the World Tournament copy
(`build_friend_v3_world_tournament_split.py`), the registration rows and the
carry-forward prefix (`apply_friend_v3_registration_rows.py`), the in-place
wording repair (`apply_friend_v3_dialogue_text.py`), the per-occurrence rename
(`build_friend_v3_release31.py`) and the approved wording as tracked data
(`friend_v3_text_approvals.py`). This module is those routes with the rows taken
out: a project is an input image plus an ordered list of edits, and every export
replays the list from that input.

THREE SURFACES, ONE IDENTITY RULE. The 1,534-slot string table addresses text by
table index; the compressed dialogue containers address it by a packed handle
(selector, decoded start, decoded length, all in bytes). The two never share
identity and an edit is always addressed at exactly one of them.

HOW A STRUCTURE IS FOUND. A candidate address is a measurement - the image's
own literal names the container table, the table names the containers, the
handles name the records - and every one of them is then VALIDATED against the
bytes before anything is read through it: the header game code, all seven retail
container pointers, every one of the 1,534 table slots decoding to a terminated
string, and a dialogue corpus of at least `MINIMUM_DIALOGUE_RECORDS` records. An
image that fails any check is refused and the refusal names the check, so a
grown derivative is accepted and a foreign image is not.

WHAT AN EDIT DECIDES. For each edit the plan answers one of three ways:
`IN_PLACE` when the new text fits the record's own span and no other record's
boundary lies inside it (the difference is paid back as trailing spaces, so no
later record moves); `MOVE` when it does not, which copies the record into the
appended dialogue container with the previous payload carried forward as the
prefix and every handle word rewritten to name the new home; `REFUSED` with the
reason, which blocks the export.

WHAT IS NEVER SILENT. A moved record's bytes stay where they were, so every
longer live record that covers the same span keeps reading the old wording. Each
such record is reported on the decision and the plan carries a warning. Nothing
is changed behind the report and nothing is refused for it.

THE CANONICAL ROM IS THE ARBITER, NOT THE SPEAKER. A per-occurrence rename is
decided by comparing each occurrence with the canonical image at the SAME
character offset. This image displays one name on two different actors, so a
rename applied to every occurrence of the spelling renames the wrong character;
comparing at the offset is what tells them apart, and a length mismatch refuses
rather than aligning by guess.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .. import compressed_dialogue as cd
from ..binary import GBA_ROM_BASE as ROM_BASE
from ..destination import refuse_rom_destination
from ..dialogue_repack import chains_of, container_pointers, text_of
from ..formats import text_tables as tt
from ..formats import webfoot_lz
from ..handles import DialogueHandle, unpack_handle
from ..write import WriteError, ensure_new_destination, ensure_not_source_alias

#: One UTF-16LE code unit. A handle's start and length fields count these.
UNIT = 2
#: A Webfoot container's header: kind, then declared size.
CONTAINER_HEADER = 8
#: The appended container's ceiling. A handle's start field addresses 65,534
#: bytes into a decoded container (handles.HANDLE_START_MAX_BYTES).
PLACEMENT_CEILING = 65534
#: The most bytes a record's length field can encode (handles.HANDLE_LENGTH_MAX_BYTES).
RECORD_LENGTH_CEILING = 4094
#: A validated image must carry at least this many dialogue records. Measured on
#: the canonical image: 2,805. The floor is a sanity gate on the whole structure,
#: not a claim about any one record; a synthetic fixture in the tests lowers it.
MINIMUM_DIALOGUE_RECORDS = 100
#: The container table's own extent, in slots. The table is a 64-entry block and
#: the retail image's seven live selectors are its first seven entries.
SELECTOR_SLOTS = 64

#: The three answers a plan gives for one edit.
IN_PLACE = "in_place"
MOVE = "move"
REFUSED = "refused"


class TextEditError(ValueError):
    """An image, a plan or a destination that this engine refuses, with the reason."""


# --- detection ---------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MapTable:
    """One title's map table, and the placement route that reaches dialogue.

    Every address is a file offset, like the rest of `TitleProfile`.
    """

    table: int
    count: int
    stride: int
    name_slot_at: int
    array_at: int
    count_at: int
    placement_family: int
    descriptor_at: int
    resource_handler: int
    event_table: int
    event_count: int


@dataclass(frozen=True, slots=True)
class TitleProfile:
    """One Webfoot title's measured candidate addresses.

    Adding another title is appending one entry to `PROFILES`; no other line in
    this module names a game. Every address here is a candidate that the
    structure has to confirm - `validate` reads through each one and refuses the
    image when the bytes do not agree.
    """

    key: str
    game_code: bytes
    table_literal: int
    text_table: int
    text_slots: int
    live_selectors: int
    grown_selector: int
    #: The appearance table, whose records pair a name slot with a portrait slot.
    #: Zero means the title has none and no speaker can be resolved.
    appearance_table: int = 0
    appearance_count: int = 0
    #: The event-resource pool, as FILE offsets like every other address here.
    #: A handle site inside it has a proven consumer, so a record carrying one is
    #: a proven dialogue reference; a site outside it is counted and not linked.
    #: None means "not measured for this title".
    event_pool: tuple[int, int] | None = None
    #: The map table and the route from a map to the dialogue its placements
    #: reference. None means the title has none and no line can be placed.
    maps: MapTable | None = None


#: Game code bytes 0xAC..0xB0 of the GBA header, measured on the canonical image.
PROFILES: tuple[TitleProfile, ...] = (
    TitleProfile(
        key="buus-fury",
        game_code=b"BG3E",
        table_literal=0x123CC,
        text_table=0x6BCE8,
        text_slots=1534,
        live_selectors=7,
        grown_selector=7,
        appearance_table=0x74D380,
        appearance_count=232,
        # The event-resource pool the SDK's placement contracts declare at ROM
        # address 0x0877C5A4..0x0879B704, as file offsets.
        event_pool=(0x77C5A4, 0x79B704),
        maps=MapTable(
            table=0x8E2E0,
            count=452,
            stride=0x38,
            name_slot_at=0x0C,
            array_at=0x14,
            count_at=0x04,
            placement_family=0x0800FD55,
            descriptor_at=0x14,
            resource_handler=0x0800424F,
            event_table=0x79B704,
            event_count=522,
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class Layout:
    """One validated image's measured containers and table."""

    profile: TitleProfile
    table_offset: int
    streams: Mapping[int, bytes]
    offsets: Mapping[int, int]
    kinds: Mapping[int, int]
    room: Mapping[int, int]


def detect(image: bytes) -> Layout:
    """The validated layout of `image`, or a refusal naming the check it failed."""
    reasons = []
    for profile in PROFILES:
        try:
            return validate(image, profile)
        except TextEditError as error:
            reasons.append(str(error))
    raise TextEditError("REFUSED: no supported text image: " + "; ".join(reasons))


def validate(image: bytes, profile: TitleProfile) -> Layout:
    """Read every candidate `profile` names and refuse unless the bytes agree."""
    header_end = 0xB3
    table_end = profile.text_table + profile.text_slots * 4
    if len(image) < max(header_end, table_end):
        raise TextEditError(
            f"REFUSED: {profile.key}: the image is {len(image)} bytes, too short to hold the "
            f"text table at {profile.text_table:#x} with {profile.text_slots} slots")
    game_code = image[0xAC:0xB0]
    if game_code != profile.game_code:
        raise TextEditError(
            f"REFUSED: {profile.key}: the header game code is {game_code!r}, not "
            f"{profile.game_code!r}")
    literal = int.from_bytes(image[profile.table_literal:profile.table_literal + 4], "little")
    if not ROM_BASE <= literal < ROM_BASE + len(image):
        raise TextEditError(
            f"REFUSED: {profile.key}: the word at {profile.table_literal:#x} is "
            f"{literal:#010x}, which is not a ROM address inside this image")
    table_offset = literal - ROM_BASE

    streams: dict[int, bytes] = {}
    offsets: dict[int, int] = {}
    kinds: dict[int, int] = {}
    room: dict[int, int] = {}
    live_end = table_offset + profile.live_selectors * 4
    if live_end > len(image):
        raise TextEditError(
            f"REFUSED: {profile.key}: the container table at {table_offset:#x} does not hold "
            f"{profile.live_selectors} live selectors inside a {len(image)}-byte image")
    for selector in range(SELECTOR_SLOTS):
        slot = table_offset + selector * 4
        if slot + 4 > len(image):
            break
        pointer = int.from_bytes(image[slot:slot + 4], "little")
        if not ROM_BASE <= pointer < ROM_BASE + len(image):
            if selector < profile.live_selectors:
                raise TextEditError(
                    f"REFUSED: {profile.key}: live selector {selector} holds "
                    f"{pointer:#010x}, which is not a ROM address inside this image")
            continue
        try:
            container = webfoot_lz.unpack(image, pointer - ROM_BASE)
        except webfoot_lz.ContainerError as error:
            if selector < profile.live_selectors:
                raise TextEditError(
                    f"REFUSED: {profile.key}: live selector {selector} at {pointer:#010x} "
                    f"does not decode as a container: {error}") from error
            continue
        if container.declared_size == 0:
            if selector < profile.live_selectors:
                raise TextEditError(
                    f"REFUSED: {profile.key}: live selector {selector} declares no payload")
            continue
        streams[selector] = bytes(container.data)
        offsets[selector] = container.offset
        kinds[selector] = container.kind
        room[selector] = container.packed_end - container.offset

    for index in range(profile.text_slots):
        address = int.from_bytes(
            image[profile.text_table + index * 4:profile.text_table + index * 4 + 4], "little")
        if not ROM_BASE <= address < ROM_BASE + len(image):
            raise TextEditError(
                f"REFUSED: {profile.key}: text slot {index} holds {address:#010x}, which is not "
                "a ROM address inside this image")
        try:
            tt.decode_string(image, address - ROM_BASE)
        except tt.TextCodecError as error:
            raise TextEditError(
                f"REFUSED: {profile.key}: text slot {index} does not decode: {error}") from error

    return Layout(profile=profile, table_offset=table_offset, streams=streams,
                  offsets=offsets, kinds=kinds, room=room)


# --- the read-only model -----------------------------------------------------


@dataclass(frozen=True, slots=True)
class Slot:
    """One string-table slot: its index, the text it holds, and retail's text.

    `text` is the project codec's rendering, so a control unit reads as its
    `{08:XX}` token and a newline as `\\n`; that is what a writer must hand back
    to `formats.text_tables.encode_string`. `retail` is `None` unless the
    canonical image was supplied at open.
    """

    index: int
    text: str
    offset: int
    retail: str | None = None

    @property
    def key(self) -> str:
        return f"text:{self.index}"


@dataclass(frozen=True, slots=True)
class Record:
    """One dialogue record, as its handle defines it, with every carrying site."""

    selector: int
    start: int
    length: int
    text: str
    sites: tuple[int, ...]
    covering: tuple[str, ...]

    @property
    def key(self) -> str:
        return f"{self.selector}:{self.start}:{self.length}"

    @property
    def handle(self) -> DialogueHandle:
        """The packed handle this record's identity is made of."""
        return DialogueHandle(self.selector, self.start, self.length)

    @property
    def locked(self) -> tuple[str, ...]:
        """The control units inside this record, as locked tokens.

        Uninterpreted in v1: the engine knows a unit is a control unit and that
        an edit may not change it, not what it draws. A move or an in-place write
        that altered this sequence would be refused.
        """
        return locked_tokens(self.text)


@dataclass(frozen=True, slots=True)
class Model:
    """A read-only view of one image: its slots, its records and its containers."""

    path: Path
    sha256: str
    image: bytes
    layout: Layout
    slots: tuple[Slot, ...]
    records: tuple[Record, ...]
    by_key: Mapping[str, Record]
    retail_path: Path | None = None
    retail_sha256: str | None = None
    retail_streams: Mapping[int, bytes] = ()

    @property
    def profile(self) -> TitleProfile:
        return self.layout.profile

    def record(self, selector: int, start: int, length: int) -> Record | None:
        return self.by_key.get(f"{selector}:{start}:{length}")

    def selector_records(self, selector: int) -> tuple[Record, ...]:
        return tuple(record for record in self.records if record.selector == selector)


@dataclass(frozen=True, slots=True)
class Text:
    """A run of displayed characters with no control unit in it."""

    value: str


@dataclass(frozen=True, slots=True)
class Control:
    """One control unit, as the raw unit(s) it occupies.

    `operand` is the following halfword for a code that takes one (0x0008), else
    None. What the code DOES is not catalogued here: a caller that wants a name
    for it supplies the catalogue (the RE Lab's is pending).
    """

    raw: str
    code: int
    operand: str | None = None


def units(text: str) -> tuple[Text, Control]:
    """Split displayed text into alternating text runs and control units.

    `locked_tokens` answers which units a text carries; this answers where they
    sit, which is what an editor needs to draw each one as a single atom and to
    refuse an edit that splits one.
    """
    split: list[Text | Control] = []
    run: list[str] = []
    position = 0
    while position < len(text):
        codepoint = ord(text[position])
        if codepoint < 0x20:
            if run:
                split.append(Text("".join(run)))
                run = []
            if codepoint == 0x08 and position + 1 < len(text):
                split.append(Control(text[position:position + 2], codepoint,
                                     text[position + 1]))
                position += 2
                continue
            split.append(Control(text[position], codepoint))
        else:
            run.append(text[position])
        position += 1
    if run:
        split.append(Text("".join(run)))
    return tuple(split)


def locked_tokens(text: str) -> tuple[str, ...]:
    """Every control unit in `text`, in order, as the raw unit(s) it occupies.

    Measured on the seven compressed containers: a control unit is a halfword
    below 0x20 with a zero high byte, and 0x0008 consumes the following halfword
    as its operand. The three 0x00A0-range units the containers also carry are
    text, not control, and are not tokens.
    """
    return tuple(item.raw for item in units(text) if isinstance(item, Control))


# --- the record word, its portrait operand, and the spoken lines -------------


#: The dialogue record word, 8 bytes: a u16 id, the handler byte 0x05, the portrait
#: OPERAND, then the packed handle. Measured on the canonical image, re-read on
#: release 3.1, and stated the same way in FRIEND_V3_IDASA_UUB_DIALOGUE.md.
RECORD_WORD_BYTES = 8
#: Where the operand sits relative to the record's first handle site.
OPERAND_FROM_HANDLE = 1

#: One appearance record: a u16 name slot, a u16 description slot, a u32 sprite id,
#: a u32 PORTRAIT SLOT, then an i32 stat index. The join runs portrait slot -> the
#: appearance records that carry it -> their name slots. The reverse (array entry ->
#: appearance record) does not exist: the array at 0x6F393C holds art pointers only.
APPEARANCE_RECORD_BYTES = 0x10
APPEARANCE_NAME_SLOT_AT = 0x00
APPEARANCE_PORTRAIT_SLOT_AT = 0x08

#: The two units that END a displayed run. There is no page-break unit: the box
#: redraws per strip, and nothing measured shows 0x000B advancing a page, so
#: nothing here claims one.
LINE_BREAK = 0x000A
SOFT_END = 0x000B
BREAKS = (LINE_BREAK, SOFT_END)
#: Inline formatting consumes the unit after it, so a walk must step over that
#: operand instead of reading it as a break.
INLINE_FORMAT = 0x0008

#: The operand's three meanings, taken from the box constructor's own branches
#: (K-017): 0 and 7 take `r1 = 0` and the text object gets NO art, no default and
#: no fallback; 1..6 take the save/party path, so the character depends on the
#: player's save; 8 and above index the portrait array with no clamp and no null
#: test.
NO_ART_OPERANDS = (0, 7)
PARTY_OPERANDS = (1, 2, 3, 4, 5, 6)
FIRST_TABLE_OPERAND = 8

#: What a record's portrait operand says. The engine never maps an operand to a
#: character inside the game, so this is a tooling join by value, and it says only
#: which face is DRAWN.
NO_PORTRAIT = "no portrait"
PARTY_PORTRAIT = "party"
NAMED_PORTRAIT = "named"
UNKNOWN_PORTRAIT = "unknown"
AMBIGUOUS_PORTRAIT = "ambiguous"


def record_operand(model: Model, record: Record) -> int | None:
    """The portrait operand every one of this record's sites agrees on.

    None when the record carries no site or when its sites disagree. Measured on
    release 3.1, 21 record identities carry two distinct operands, every one of
    them with all sites inside the event pool, so a single portrait cannot be
    attributed to such a record.
    """
    seen = set()
    for site in record.sites:
        at = site - OPERAND_FROM_HANDLE
        if 0 <= at < len(model.image):
            seen.add(model.image[at])
    if len(seen) != 1:
        return None
    return seen.pop()


def _appearance_names(model: Model) -> dict[int, str]:
    """Portrait slot -> the displayed name, from the image's own appearance table.

    A slot that two appearance records disagree about is dropped rather than
    picked: over the table's 232 records exactly one slot is carried by more than
    one record, and those agree, so failing closed costs nothing.
    """
    profile = model.profile
    table, count = profile.appearance_table, profile.appearance_count
    if not table or not count or table + count * APPEARANCE_RECORD_BYTES > len(model.image):
        return {}
    seen: dict[int, set[str]] = {}
    for index in range(count):
        at = table + index * APPEARANCE_RECORD_BYTES
        slot = int.from_bytes(
            model.image[at + APPEARANCE_PORTRAIT_SLOT_AT:at + APPEARANCE_PORTRAIT_SLOT_AT + 4],
            "little")
        name_slot = int.from_bytes(
            model.image[at + APPEARANCE_NAME_SLOT_AT:at + APPEARANCE_NAME_SLOT_AT + 2], "little")
        if not slot or not 0 <= name_slot < len(model.slots):
            continue
        seen.setdefault(slot, set()).add(model.slots[name_slot].text)
    return {slot: next(iter(names)) for slot, names in seen.items() if len(names) == 1}


@dataclass(frozen=True, slots=True)
class Portrait:
    """Which face a record draws, as far as the data can say.

    `name` is set only for :data:`NAMED_PORTRAIT`. Every other kind is a stated
    gap rather than a guess: the game itself never maps an operand to a character.
    """

    operand: int | None
    kind: str
    name: str | None = None

    @property
    def resolved(self) -> str | None:
        """The character name, or None when the data does not attribute one."""
        return self.name if self.kind == NAMED_PORTRAIT else None


def portraits(model: Model) -> dict[str, Portrait]:
    """Record key -> which face that record's word draws.

    A key that is absent means the record carries no site at all. A key whose kind
    is :data:`AMBIGUOUS_PORTRAIT` means the record's own sites disagree on the
    operand byte, so no single face is attributable.

    MEASURED POPULATION, not a sample: the canonical image holds 2,221 handler-5
    records that are entries of a dialogue pointer array, of which 229 carry no
    portrait, 431 take the save-dependent party path and 1,561 index the array
    (K-017). Some operands have no owning appearance record, so those read as an
    unknown portrait rather than as a nearby name.
    """
    names = _appearance_names(model)
    found: dict[str, Portrait] = {}
    for record in model.records:
        operand = record_operand(model, record)
        if not record.sites:
            found[record.key] = Portrait(None, UNKNOWN_PORTRAIT)
        elif operand is None:
            found[record.key] = Portrait(None, AMBIGUOUS_PORTRAIT)
        elif operand in NO_ART_OPERANDS:
            found[record.key] = Portrait(operand, NO_PORTRAIT)
        elif operand in PARTY_OPERANDS:
            found[record.key] = Portrait(operand, PARTY_PORTRAIT)
        else:
            name = names.get(operand)
            found[record.key] = (Portrait(operand, NAMED_PORTRAIT, name) if name
                                 else Portrait(operand, UNKNOWN_PORTRAIT))
    return found


def speakers(model: Model) -> dict[str, str]:
    """Record key -> the one displayed name its portrait resolves to.

    The resolved subset of :func:`portraits`, for a caller that only wants the
    names. A key that is absent means the likeness is not attributable, and that
    is a measured minority report rather than an edge case: on release 3.1, 1,595
    of 2,818 records and 1,707 of 3,024 lines resolve.

    The name comes from the loaded image's own text table, so an image that renamed
    an actor reports the name that image shows.
    """
    return {key: portrait.name for key, portrait in portraits(model).items()
            if portrait.kind == NAMED_PORTRAIT and portrait.name}


@dataclass(frozen=True, slots=True)
class SpokenLine:
    """One spoken line: a stored run between explicit breaks, and its carriers."""

    selector: int
    start: int
    length: int
    text: str
    #: Every record whose span contains this line, narrowest first.
    records: tuple[str, ...]
    #: The subset of `records` whose own handle site lies in the event pool.
    proven: tuple[str, ...]
    #: Every handle site of those records, ascending.
    sites: tuple[int, ...]

    @property
    def key(self) -> str:
        return f"{self.selector}:{self.start}:{self.length}"

    @property
    def target(self) -> str:
        """The record an edit of this line should name.

        The narrowest PROVEN carrier, because that is a record whose sites this
        project has rewritten and verified; the narrowest carrier at all when none
        is proven, so that a line is never silently uneditable.
        """
        if self.proven:
            return self.proven[0]
        return self.records[0] if self.records else ""

    @property
    def target_is_proven(self) -> bool:
        return bool(self.proven)


def _split_runs(stream: bytes, start: int, end: int) -> tuple[tuple[int, int], ...]:
    """Cut `start`..`end` at the units that end a displayed run, terminators out."""
    runs: list[tuple[int, int]] = []
    run = start
    at = start
    while at + 2 <= end:
        unit = int.from_bytes(stream[at:at + 2], "little")
        if unit in BREAKS:
            runs.append((run, at))
            run = at + 2
            at += 2
            continue
        at += 4 if unit == INLINE_FORMAT else 2
    runs.append((run, end))
    return tuple(runs)


def shown_text(text: str) -> str:
    """Only the displayed characters of `text`, with every control unit dropped."""
    return "".join(item.value for item in units(text) if isinstance(item, Text))


@dataclass(frozen=True, slots=True)
class MapRow:
    """One row of the map table: where it sits, and what the table calls it."""

    index: int
    name: str

    @property
    def label(self) -> str:
        """The name, or the index alone when the table leaves the name slot empty."""
        return self.name.strip() or f"Map {self.index}"


def _event_extents(model: Model) -> dict[int, tuple[int, int]]:
    """Event resource start -> its extent, from the table's own sorted pointers."""
    table = model.profile.maps
    if table is None or table.event_table + table.event_count * 4 > len(model.image):
        return {}
    starts = sorted(
        int.from_bytes(model.image[table.event_table + 4 * index:
                                    table.event_table + 4 * index + 4], "little") - ROM_BASE
        for index in range(table.event_count))
    extents = {}
    for position, start in enumerate(starts):
        if start < 0:
            continue
        nxt = starts[position + 1] if position + 1 < len(starts) else table.event_table
        extents[start] = (start, nxt)
    return extents


def maps(model: Model) -> tuple[MapRow, ...]:
    """Every row of the map table, in map-table order.

    The name comes from the row's own name slot in the LOADED image's text table,
    so an image that renamed a map reports the name that image shows. 429 of the
    452 rows carry a name on the canonical image.
    """
    table = model.profile.maps
    if table is None or table.table + table.count * table.stride > len(model.image):
        return ()
    rows = []
    for index in range(table.count):
        at = table.table + index * table.stride
        slot = int.from_bytes(model.image[at + table.name_slot_at:
                                         at + table.name_slot_at + 4], "little")
        name = model.slots[slot].text if 0 <= slot < len(model.slots) else ""
        rows.append(MapRow(index=index, name=name))
    return tuple(rows)


def record_maps(model: Model) -> dict[str, int]:
    """Record key -> the map whose placements reach an event resource it sits in.

    THE CHAIN, every step measured on the canonical image: a map row's `+0x14`
    array holds placement pointers, a placement's `+0x14` names a descriptor, and a
    descriptor whose handler is `0x0800424F` carries a payload that is the start of
    an event resource. A record belongs to that map when one of its own handle sites
    falls inside that resource's extent. Measured: 28 maps reference 63 resources
    and reach 487 of the image's 2,805 records through 489 of its 2,993 sites, which
    reproduces the independent research probe exactly.

    THE LIMIT, stated rather than hidden: the payload's semantics are INFERRED. The
    handler is known to load and branch, and the payload is known to be a resource
    start, but no runtime observation yet shows that this handler is what reads that
    resource's dialogue. The route is therefore evidence-linked, not proven, and a
    caller that shows a map must say which map came from here.

    A record that two maps reach is given NO map, because a row shown under one of
    two owners would be a guess. Measured: one record of the 488 is shared.
    """
    table = model.profile.maps
    if table is None:
        return {}
    extents = _event_extents(model)
    if not extents:
        return {}
    ranges: list[tuple[int, int, int]] = []
    for index in range(table.count):
        at = table.table + index * table.stride
        if at + table.stride > len(model.image):
            break
        array = int.from_bytes(model.image[at + table.array_at:at + table.array_at + 4],
                               "little")
        count = model.image[at + table.count_at]
        if not ROM_BASE <= array < ROM_BASE + len(model.image):
            continue
        for position in range(count):
            word_at = array - ROM_BASE + 4 * position
            if word_at + 4 > len(model.image):
                break
            word = int.from_bytes(model.image[word_at:word_at + 4], "little")
            if not ROM_BASE <= word < ROM_BASE + len(model.image):
                continue
            placement = word - ROM_BASE
            if placement + 4 > len(model.image):
                continue
            if int.from_bytes(model.image[placement:placement + 4], "little") != \
                    table.placement_family:
                continue
            descriptor = int.from_bytes(
                model.image[placement + table.descriptor_at:
                            placement + table.descriptor_at + 4], "little") - ROM_BASE
            if not 0 <= descriptor <= len(model.image) - 8:
                continue
            handler = int.from_bytes(model.image[descriptor:descriptor + 4], "little")
            payload = int.from_bytes(model.image[descriptor + 4:descriptor + 8], "little")
            origin = payload - ROM_BASE
            if handler == table.resource_handler and origin in extents:
                low, high = extents[origin]
                ranges.append((low, high, index))
    reached: dict[str, set[int]] = {}
    for record in model.records:
        for site in record.sites:
            for low, high, index in ranges:
                if low <= site < high:
                    reached.setdefault(record.key, set()).add(index)
    return {key: next(iter(found)) for key, found in reached.items() if len(found) == 1}


def line_maps(model: Model, *, cutters_from_pool: bool = True) -> dict[str, int]:
    """Spoken-line key -> the map of the record an edit of that line would address."""
    owners = record_maps(model)
    if not owners:
        return {}
    return {row.key: owners[row.target]
            for row in lines(model, cutters_from_pool=cutters_from_pool)
            if row.target in owners}


def lines(model: Model, *, cutters_from_pool: bool = True) -> tuple[SpokenLine, ...]:
    """One row per spoken line, in the image's own storage order.

    A row is a maximal span of one container that no CUTTER's boundary cuts,
    further cut at the units that end a displayed run. With `cutters_from_pool`
    the cutters are the records with a handle site inside the profile's event
    pool; without it every record cuts. The pool filter matters because the
    structural query that finds records also fires on coincidence words and those
    chop real messages apart: on release 3.1, cutting at every record yields 3,317
    rows for 2,818 records where the pool-limited cutters yield 3,024.

    The pool filter reuses the proven-write test as a liveness test, which is an
    inference and is the rule's one free parameter. `SpokenLine.proven` names the
    rows and records that would move if it were dropped.
    """
    pool = model.profile.event_pool
    rows: list[SpokenLine] = []
    for selector in sorted(model.layout.streams):
        stream = model.layout.streams[selector]
        records = model.selector_records(selector)
        if cutters_from_pool and pool is not None:
            cutters = [row for row in records
                       if any(pool[0] <= site < pool[1] for site in row.sites)]
        else:
            cutters = list(records)
        if not cutters:
            continue
        ordered = sorted(records, key=lambda row: row.start)
        for chain_start, chain_end in chains_of(cutters):
            for start, end in _split_runs(bytes(stream), chain_start, chain_end):
                text = text_of(stream, start, end - start)
                if not shown_text(text).strip():
                    continue
                carriers = []
                for row in ordered:
                    if row.start > start:
                        break
                    if row.start + row.length >= end:
                        carriers.append(row)
                if not carriers:
                    continue
                carriers.sort(key=lambda row: (row.length, row.start))
                proven = [row for row in carriers
                          if pool is not None
                          and any(pool[0] <= site < pool[1] for site in row.sites)]
                rows.append(SpokenLine(
                    selector=selector, start=start, length=end - start, text=text,
                    records=tuple(row.key for row in carriers),
                    proven=tuple(row.key for row in proven),
                    sites=tuple(sorted({site for row in carriers for site in row.sites}))))
    return tuple(rows)


def open_rom(rom_path: str | Path, canonical: str | Path | None = None) -> Model:
    """Open an image read-only, with the canonical image as the retail reference."""
    path = Path(rom_path)
    return load(path.read_bytes(), path, canonical=canonical)


def load(image: bytes, path: str | Path, canonical: str | Path | None = None,
         *, check_profile: bool = True) -> Model:
    """A model over image bytes already in hand, which need not have been written down.

    `open_rom` reads a file and hands the bytes here. A caller holding an image it BUILT,
    which `plan` does, reads the result the same way without writing it out first, so a
    derived view of an edited image goes through the same reader as the original instead of
    reusing the original record table against edited bytes. Measured, that reuse was a real
    defect: a record whose edit GREW it kept its original span, so the lines read from the
    edited streams were cut at the old offsets and disagreed with the exported image.

    `check_profile` is off for that caller. The record floor guards against opening the
    WRONG image, and these bytes came from an image that already passed it.
    """
    path = Path(path)
    digest = hashlib.sha256(image).hexdigest()
    layout = detect(image)
    records = _read_records(image, layout)
    if check_profile and len(records) < MINIMUM_DIALOGUE_RECORDS:
        raise TextEditError(
            f"REFUSED: {path} carries {len(records)} dialogue record(s), under the "
            f"{MINIMUM_DIALOGUE_RECORDS}-record floor this profile validates against")
    slots = _read_slots(image, layout.profile)
    retail_file: Path | None = None
    retail_sha256 = None
    retail_streams: Mapping[int, bytes] = {}
    if canonical is not None:
        retail_path = Path(canonical)
        retail = retail_path.read_bytes()
        retail_layout = detect(retail)
        retail_file = retail_path
        retail_sha256 = hashlib.sha256(retail).hexdigest()
        retail_streams = dict(retail_layout.streams)
        retail_slots = _read_slots(retail, retail_layout.profile)
        if len(retail_slots) != len(slots):
            raise TextEditError(
                f"REFUSED: {retail_path} carries {len(retail_slots)} text slots and {path} "
                f"carries {len(slots)}; the retail reference must be the same table")
        slots = tuple(replace(slot, retail=other.text)
                      for slot, other in zip(slots, retail_slots))
    return Model(
        path=path,
        sha256=digest,
        image=image,
        layout=layout,
        slots=slots,
        records=records,
        by_key={record.key: record for record in records},
        retail_path=retail_file,
        retail_sha256=retail_sha256,
        retail_streams=retail_streams,
    )


def _read_slots(image: bytes, profile: TitleProfile) -> tuple[Slot, ...]:
    slots = []
    for index in range(profile.text_slots):
        at = profile.text_table + index * 4
        address = int.from_bytes(image[at:at + 4], "little")
        text, _end = tt.decode_string(image, address - ROM_BASE)
        slots.append(Slot(index=index, text=text, offset=address - ROM_BASE))
    return tuple(slots)


def _read_records(image: bytes, layout: Layout) -> tuple[Record, ...]:
    records: list[Record] = []
    for selector in sorted(layout.streams):
        stream = layout.streams[selector]
        rows = [(record.handle.decoded_start, record.handle.decoded_length, record)
                for record in cd.dialogue_record_inventory(image, selector, len(stream))]
        order = sorted(rows, key=lambda row: (row[0], -row[1]))
        covering: dict[str, tuple[str, ...]] = {}
        for position, (start, length, _record) in enumerate(order):
            end = start + length
            covering[f"{selector}:{start}:{length}"] = tuple(
                f"{selector}:{other_start}:{other_length}"
                for other_start, other_length, _ in order[:position]
                if other_start + other_length >= end)
        for start, length, record in rows:
            key = f"{selector}:{start}:{length}"
            records.append(Record(selector=selector, start=start, length=length,
                                  text=text_of(stream, start, length),
                                  sites=tuple(record.sites),
                                  covering=covering[key]))
    return tuple(records)


# --- edits -------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SlotEdit:
    """Replace a string-table slot's text. `old` is the guard the write checks."""

    slot: int
    old: str
    new: str


@dataclass(frozen=True, slots=True)
class RecordEdit:
    """Replace `old` with `new` inside one dialogue record.

    `old` must occur exactly once in the record; that count is the guard, and
    `old` may be the record's whole text when the whole line is being rewritten.
    """

    selector: int
    start: int
    length: int
    old: str
    new: str

    @property
    def key(self) -> str:
        return f"{self.selector}:{self.start}:{self.length}"


@dataclass(frozen=True, slots=True)
class RenameEdit:
    """Rename a character, deciding each occurrence against the canonical image.

    `relocated_slots` names the string-table slots whose text is the name itself.
    """

    old: str
    new: str
    retail_test: str
    relocated_slots: tuple[int, ...] = ()


#: What the retail test says about one occurrence of a name inside a record.
RENAME = "rename"    # retail names the same actor at this offset, so the swap happens
KEEP = "keep"        # retail names a different actor here, so this one stays
UNCLEAR = "unclear"  # retail names neither, so nothing can be decided here


@dataclass(frozen=True, slots=True)
class Occurrence:
    """One occurrence of a name in a record, and what retail says at that offset."""

    at: int
    retail: str
    decision: str


def rename_occurrences(current: str, counterpart: str, old: str) -> tuple[Occurrence, ...]:
    """Every occurrence of `old`, with the decision the retail offset implies.

    Split out of `rename_positions` so a per-occurrence dialog shows the decision
    the rename will actually make: one rule, one place.
    """
    if not old:
        raise TextEditError("REFUSED: a rename needs a name to replace")
    if len(current) != len(counterpart):
        raise TextEditError(
            f"REFUSED: the record is {len(current)} units and its retail counterpart is "
            f"{len(counterpart)}, so character offsets do not correspond and an occurrence "
            "cannot be attributed to an actor")
    found: list[Occurrence] = []
    cursor = 0
    while True:
        at = current.find(old, cursor)
        if at == -1:
            break
        retail_word = counterpart[at:at + len(old)]
        if retail_word == old:
            decision = RENAME
        elif any(character.isalpha() for character in retail_word):
            decision = KEEP
        else:
            decision = UNCLEAR
        found.append(Occurrence(at=at, retail=retail_word, decision=decision))
        cursor = at + len(old)
    return tuple(found)


def rename_positions(current: str, counterpart: str, *, old: str,
                     new: str) -> tuple[str, int, int, int]:
    """Rename each occurrence of `old` only where `counterpart` names the same actor.

    WHY POSITION BY POSITION AND NOT `str.replace`. The retail test is a decision
    about an OCCURRENCE, and a record can contain both actors: measured on this
    corpus, `3:2184:2112` and `3:1192:2690` hold lines whose retail text reads
    "I want to see Goten and Trunks compete" while the built text reads "I want
    to see Videl and Uub    compete" - that Videl IS the Goten-turned-Videl actor
    - beside occurrences that are retail Videl. A per-record decision applied
    with a per-occurrence replace renames the wrong one.

    WHY NO ALIGNMENT IS NEEDED. The earlier rename passes preserved every
    record's LENGTH: a shorter swap was paid for with spaces, so character offsets
    correspond one to one and the decision is a direct comparison at the SAME
    offset. A length mismatch means that correspondence is not established, so it
    refuses rather than aligning by guess.

    Returns the rebuilt text and the counts of occurrences renamed, kept because
    retail names the other actor there, and left because the retail word is
    neither.
    """
    pieces: list[str] = []
    cursor = 0
    counts = {RENAME: 0, KEEP: 0, UNCLEAR: 0}
    for item in rename_occurrences(current, counterpart, old):
        pieces.append(current[cursor:item.at])
        pieces.append(new if item.decision == RENAME else old)
        counts[item.decision] += 1
        cursor = item.at + len(old)
    pieces.append(current[cursor:])
    return "".join(pieces), counts[RENAME], counts[KEEP], counts[UNCLEAR]


# --- the plan ----------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Change:
    """One byte range the export will write."""

    start: int
    end: int
    what: str


@dataclass(frozen=True, slots=True)
class Decision:
    """What the plan decided for one edit target."""

    target: str
    method: str
    reason: str = ""
    covering: tuple[str, ...] = ()
    sites: int = 0
    bytes_before: int = 0
    bytes_after: int = 0


@dataclass(frozen=True, slots=True)
class _InPlace:
    decision: int
    selector: int
    start: int
    length: int
    old: str
    new: str


@dataclass(frozen=True, slots=True)
class _Placement:
    decision: int
    key: str
    text: str
    sites: tuple[int, ...]
    old_handle: int
    new_start: int = 0
    new_length: int = 0


@dataclass(frozen=True, slots=True)
class _SlotMove:
    decision: int
    slot: int
    old: str
    new: str
    method: str
    offset: int = 0
    allocation: int = 0
    at: int = 0


@dataclass(frozen=True, slots=True)
class Plan:
    """A deterministic, fully built export that has not been written anywhere."""

    model: Model
    decisions: tuple[Decision, ...]
    changes: tuple[Change, ...]
    warnings: tuple[str, ...]
    listed: tuple[str, ...]
    output: bytes
    output_sha256: str
    rewritten_selectors: tuple[int, ...]
    in_place: tuple[_InPlace, ...]
    placements: tuple[_Placement, ...]
    slot_moves: tuple[_SlotMove, ...]

    @property
    def refusals(self) -> tuple[Decision, ...]:
        return tuple(item for item in self.decisions if item.method == REFUSED)

    @property
    def summary(self) -> dict:
        counts = {IN_PLACE: 0, MOVE: 0, REFUSED: 0}
        for item in self.decisions:
            counts[item.method] = counts.get(item.method, 0) + 1
        return {
            "input": str(self.model.path),
            "input_sha256": self.model.sha256,
            "input_bytes": len(self.model.image),
            "output_sha256": self.output_sha256,
            "output_bytes": len(self.output),
            "in_place": counts[IN_PLACE],
            "moved": counts[MOVE],
            "refused": counts[REFUSED],
            "warnings": len(self.warnings),
        }


class _Builder:
    """The output image under construction, and the ranges it has written."""

    def __init__(self, image: bytes) -> None:
        self.out = bytearray(image)
        self.changes: list[Change] = []

    def write(self, at: int, payload: bytes, what: str) -> None:
        self.out[at:at + len(payload)] = payload
        self.changes.append(Change(at, at + len(payload), what))

    def append(self, payload: bytes, what: str) -> int:
        at = len(self.out)
        while at % 4:
            self.out.append(0x00)
            at += 1
        self.out += payload
        self.changes.append(Change(at, at + len(payload), what))
        return at


def plan(model: Model, edits: Iterable[object]) -> Plan:
    """Decide every edit, build the whole output in memory and report the changes."""
    edits = tuple(edits)
    decisions: list[Decision] = []
    in_place: list[_InPlace] = []
    placements: list[_Placement] = []
    slot_moves: list[_SlotMove] = []
    warnings: list[str] = []
    listed: list[str] = []

    for edit in edits:
        if isinstance(edit, SlotEdit):
            _decide_slot(model, edit, decisions, slot_moves)
        elif isinstance(edit, RecordEdit):
            _decide_record(model, edit, decisions, in_place, placements, warnings)
        elif isinstance(edit, RenameEdit):
            _decide_rename(model, edit, decisions, placements, slot_moves, warnings, listed)
        else:
            raise TextEditError(
                f"REFUSED: {edit!r} is not a SlotEdit, a RecordEdit or a RenameEdit")

    builder = _Builder(model.image)
    # The table moves before anything aims at one of its slots: an in-place
    # container relocation writes the slot of the table in force, and the image's
    # own table is live structure that must not be written (F1).
    table = _relocate_table(model, placements, decisions, builder, warnings)
    in_place, decisions, rewritten = _write_in_place(model, in_place, decisions, builder)
    placements, decisions = _write_moves(model, placements, decisions, builder, table)
    if placements:
        rewritten.add(model.profile.grown_selector)
    slot_moves, decisions = _write_slots(model, slot_moves, decisions, builder)

    output = bytes(builder.out)
    return Plan(
        model=model,
        decisions=tuple(decisions),
        changes=tuple(builder.changes),
        warnings=tuple(warnings),
        listed=tuple(listed),
        output=output,
        output_sha256=hashlib.sha256(output).hexdigest(),
        rewritten_selectors=tuple(sorted(rewritten)),
        in_place=tuple(in_place),
        placements=tuple(placements),
        slot_moves=tuple(slot_moves),
    )


# --- deciding one edit -------------------------------------------------------


def _refuse(decisions: list[Decision], target: str, reason: str, covering=(),
            sites: int = 0) -> int:
    decisions.append(Decision(target=target, method=REFUSED, reason=reason,
                              covering=tuple(covering), sites=sites))
    return len(decisions) - 1


def _note(decisions: list[Decision], target: str, method: str, covering=(), sites: int = 0,
          bytes_before: int = 0, bytes_after: int = 0) -> int:
    decisions.append(Decision(target=target, method=method, covering=tuple(covering),
                              sites=sites, bytes_before=bytes_before, bytes_after=bytes_after))
    return len(decisions) - 1


def _boundary_conflict(model: Model, selector: int, start: int, length: int) -> str:
    """Whether another live record's boundary lies strictly inside this span.

    An in-place replacement pays the difference back as trailing spaces, so
    everything between the edit and that pad moves. A record that merely CONTAINS
    the span reads the new wording, which is the intent; a record whose start or
    end lies strictly INSIDE the span is cut by the move.
    """
    end = start + length
    for other in model.selector_records(selector):
        if (other.start, other.length) == (start, length):
            continue
        other_end = other.start + other.length
        if start < other.start < end or start < other_end < end:
            return (f"record {other.start}:{other.length} has a boundary inside this span, "
                    "so an in-place edit would cut it")
    return ""


def _raw_slot(image: bytes, profile: TitleProfile, index: int) -> tuple[str, int, int]:
    """A slot's raw text, its file offset and its byte allocation including terminator."""
    at = profile.text_table + index * 4
    address = int.from_bytes(image[at:at + 4], "little")
    if not ROM_BASE <= address < ROM_BASE + len(image):
        raise TextEditError(f"text slot {index} holds {address:#010x}, not a ROM address")
    offset = address - ROM_BASE
    end = offset
    while end + 1 < len(image) and image[end:end + 2] != b"\x00\x00":
        end += 2
    if image[end:end + 2] != b"\x00\x00":
        raise TextEditError(f"text slot {index} has no terminator before the end of the image")
    return image[offset:end].decode("utf-16le", "replace"), offset, end - offset + UNIT


def _slot_tokens(text: str) -> tuple[str, ...]:
    """The control-unit operands in a slot's rendered text, in order.

    The token form is the project codec's own (`formats.text_tables._CONTROL_RE`),
    so a slot edit can never change which control units a string carries.
    """
    return tuple(match.group(1) for match in tt._CONTROL_RE.finditer(text))


def _references(image: bytes, pointer: int) -> int:
    """Word-aligned occurrences of `pointer`'s four bytes in the whole image."""
    if not ROM_BASE <= pointer < ROM_BASE + len(image):
        return 0
    needle = pointer.to_bytes(4, "little")
    count = 0
    position = image.find(needle)
    while position != -1:
        if position % 4 == 0 and position < len(image) - 4:
            count += 1
        position = image.find(needle, position + 1)
    return count


def _decide_slot(model: Model, edit: SlotEdit, decisions: list[Decision],
                 slot_moves: list[_SlotMove]) -> None:
    target = f"text:{edit.slot}"
    if not 0 <= edit.slot < len(model.slots):
        _refuse(decisions, target, f"slot {edit.slot} is outside the {len(model.slots)}-slot table")
        return
    try:
        raw, offset, allocation = _raw_slot(model.image, model.profile, edit.slot)
    except TextEditError as error:
        _refuse(decisions, target, str(error))
        return
    slot = model.slots[edit.slot]
    if slot.text != edit.old:
        _refuse(decisions, target,
                f"slot {edit.slot} reads {slot.text[:60]!r}, not the text this edit replaces")
        return
    if _slot_tokens(edit.new) != _slot_tokens(edit.old):
        _refuse(decisions, target,
                f"slot {edit.slot}: the edit changes the string's control units, which are "
                "locked")
        return
    try:
        encoded = tt.encode_string(edit.new)
    except tt.TextCodecError as error:
        _refuse(decisions, target, f"slot {edit.slot}: {error}")
        return
    method = IN_PLACE if len(encoded) <= allocation else MOVE
    index = _note(decisions, target, method, sites=1, bytes_before=len(raw.encode("utf-16le")) + UNIT,
                  bytes_after=len(encoded))
    slot_moves.append(_SlotMove(decision=index, slot=edit.slot, old=edit.old, new=edit.new,
                                method=method, offset=offset, allocation=allocation))


def _decide_record(model: Model, edit: RecordEdit, decisions: list[Decision],
                   in_place: list[_InPlace], placements: list[_Placement],
                   warnings: list[str]) -> None:
    target = edit.key
    record = model.record(edit.selector, edit.start, edit.length)
    if record is None:
        _refuse(decisions, target,
                "no live record carries this identity; its span lies outside the container's "
                "decoded payload or no record word names it")
        return
    if record.text.count(edit.old) != 1:
        _refuse(decisions, target,
                f"the record holds {edit.old!r} {record.text.count(edit.old)} time(s), expected "
                "exactly once")
        return
    replaced = record.text.replace(edit.old, edit.new)
    if locked_tokens(replaced) != locked_tokens(record.text):
        _refuse(decisions, target,
                "the edit changes the record's control units, which are locked")
        return
    encoded = replaced.encode("utf-16le")
    if len(encoded) > RECORD_LENGTH_CEILING:
        _refuse(decisions, target,
                f"the replacement is {len(encoded)} bytes, above the {RECORD_LENGTH_CEILING}-byte "
                "length field")
        return
    conflict = _boundary_conflict(model, edit.selector, edit.start, edit.length)
    method = IN_PLACE if not conflict and len(encoded) <= edit.length else MOVE
    index = _note(decisions, target, method, covering=record.covering, sites=len(record.sites),
                  bytes_before=edit.length, bytes_after=len(encoded))
    if method == IN_PLACE:
        in_place.append(_InPlace(decision=index, selector=edit.selector,
                                 start=edit.start, length=edit.length, old=edit.old, new=edit.new))
        return
    placements.append(_Placement(decision=index, key=target, text=replaced, sites=record.sites,
                                 old_handle=DialogueHandle(edit.selector, edit.start,
                                                           edit.length).encode()))
    if record.covering:
        warnings.append(
            f"{target} moves to the appended container; {len(record.covering)} longer record(s) "
            f"covering the same bytes keep the old wording: {', '.join(record.covering)}")
    elif conflict:
        warnings.append(f"{target}: {conflict}")


def _decide_rename(model: Model, edit: RenameEdit, decisions: list[Decision],
                   placements: list[_Placement], slot_moves: list[_SlotMove],
                   warnings: list[str], listed: list[str]) -> None:
    if not model.retail_streams:
        _refuse(decisions, f"rename:{edit.old}", "a per-occurrence rename needs the canonical "
                                                 "image, which was not supplied at open")
        return
    for selector in sorted(model.layout.streams):
        stream = model.layout.streams[selector]
        other = model.retail_streams.get(selector, b"")
        for record in cd.dialogue_record_inventory(model.image, selector, len(stream)):
            start = record.handle.decoded_start
            length = record.handle.decoded_length
            key = f"{selector}:{start}:{length}"
            current = text_of(stream, start, length)
            if edit.old not in current:
                continue
            counterpart = (other[start:start + length].decode("utf-16le", "replace")
                           if start + length <= len(other) else None)
            if counterpart is None or edit.old not in counterpart:
                listed.append(key)
                continue
            try:
                text, renamed, kept, unclear = rename_positions(
                    current, counterpart, old=edit.old, new=edit.new)
            except TextEditError as error:
                _refuse(decisions, key, str(error))
                continue
            if renamed == 0:
                listed.append(key)
                continue
            encoded = text.encode("utf-16le")
            if len(encoded) > RECORD_LENGTH_CEILING:
                _refuse(decisions, key,
                        f"the renamed record is {len(encoded)} bytes, above the "
                        f"{RECORD_LENGTH_CEILING}-byte length field")
                continue
            found = model.record(selector, start, length)
            covering = found.covering if found is not None else ()
            index = _note(decisions, key, MOVE, covering=covering, sites=len(record.sites),
                          bytes_before=length, bytes_after=len(encoded))
            placements.append(_Placement(
                decision=index, key=key, text=text, sites=tuple(record.sites),
                old_handle=DialogueHandle(selector, start, length).encode()))
            if covering:
                warnings.append(
                    f"{key} moves to the appended container; {len(covering)} longer record(s) "
                    f"covering the same bytes keep the old wording: {', '.join(covering)}")
            if unclear:
                warnings.append(
                    f"{key}: {unclear} occurrence(s) hold {edit.old!r} where retail names neither "
                    "it nor another actor, and were left alone")
    for slot in edit.relocated_slots:
        _decide_slot(model, SlotEdit(slot=slot, old=edit.old, new=edit.new), decisions, slot_moves)


# --- writing the plan --------------------------------------------------------


def _write_in_place(model: Model, in_place: list[_InPlace], decisions: list[Decision],
                    builder: _Builder) -> tuple[list[_InPlace], list[Decision], set[int]]:
    """Repack every edited container in place, preserving the kind it came in."""
    by_selector: dict[int, list[_InPlace]] = {}
    for row in in_place:
        by_selector.setdefault(row.selector, []).append(row)
    final: list[_InPlace] = []
    rewritten: set[int] = set()
    for selector in sorted(by_selector):
        stream = bytearray(model.layout.streams[selector])
        applied: list[_InPlace] = []
        for row in by_selector[selector]:
            text = text_of(bytes(stream), row.start, row.length)
            if text.count(row.old) != 1:
                decisions[row.decision] = replace(
                    decisions[row.decision], method=REFUSED,
                    reason=f"at write time the record holds {row.old!r} "
                           f"{text.count(row.old)} time(s)")
                continue
            replaced = text.replace(row.old, row.new)
            encoded = replaced.encode("utf-16le")
            pad = (row.length - len(encoded)) // UNIT
            if pad < 0:
                decisions[row.decision] = replace(
                    decisions[row.decision], method=REFUSED,
                    reason=f"the replacement needs {len(encoded)} bytes of a {row.length}-byte span")
                continue
            expected = replaced + " " * pad
            stream[row.start:row.start + row.length] = expected.encode("utf-16le")
            applied.append(row)
        if not applied:
            final.extend(by_selector[selector])
            continue
        kind = model.layout.kinds[selector]
        packed = (webfoot_lz.build_stored(bytes(stream)) if kind == webfoot_lz.STORED
                  else webfoot_lz.pack(bytes(stream), kind=kind))
        at = model.layout.offsets[selector]
        if len(packed) > model.layout.room[selector]:
            pointer = container_pointers(model.image)[selector]
            references = _references(model.image, pointer)
            if references != 1:
                for row in applied:
                    decisions[row.decision] = replace(
                        decisions[row.decision], method=REFUSED,
                        reason=f"selector {selector} needs {len(packed)} bytes of "
                               f"{model.layout.room[selector]}, and its old pointer has "
                               f"{references} word-aligned references, so it cannot be repointed")
                final.extend(by_selector[selector])
                continue
            at = builder.append(packed, f"container {selector} relocated")
            entry = _table_base(model.profile, builder.out) + selector * 4
            builder.write(entry, (ROM_BASE + at).to_bytes(4, "little"), f"table slot {selector}")
        else:
            builder.write(at, packed, f"container {selector}")
        rewritten.add(selector)
        final.extend(applied)
    return final, decisions, rewritten


def _refuse_all(decisions: list[Decision], rows: list[_Placement], reason: str) -> None:
    for row in rows:
        decisions[row.decision] = replace(decisions[row.decision], method=REFUSED, reason=reason)


def _relocate_table(model: Model, placements: list[_Placement], decisions: list[Decision],
                    builder: _Builder, warnings: list[str]) -> int | None:
    """Copy the container table aside when the grown slot does not name a container.

    THE RETAIL TABLE IS NEVER WRITTEN. A table whose grown slot does not already
    name a container is the image's own table, and its words are live structure:
    measured on the canonical image, the grown slot holds 0x03004A68 and three
    code loads reach that word through the literal at file 0x03D92C. The shipped
    releases never wrote it either: they ran on images whose table had already
    been moved into expansion space. This route does the same - copy the whole
    64-slot table into appended space and repoint the one literal that names it -
    and refuses when that literal is not named exactly once, rather than writing
    a word whose owner is unproven (P-027).

    This runs before any container relocation, never after it: an in-place
    container relocation writes the slot of the table in force, and run the other
    way round that write lands in the image's own table (F1).

    Returns the file offset of the table in force, or ``None`` when the table
    could not be moved aside, in which case every row has been refused.
    """
    table = model.layout.table_offset
    if not placements:
        return table
    selector = model.profile.grown_selector
    slot_at = table + selector * 4
    if slot_at + 4 > len(model.image):
        _refuse_all(decisions, placements,
                    "the grown selector's table slot lies outside the image")
        return None
    out = builder.out
    pointer = int.from_bytes(out[slot_at:slot_at + 4], "little")
    if ROM_BASE <= pointer < ROM_BASE + len(model.image):
        return table
    literal_at = model.profile.table_literal
    literal = int.from_bytes(model.image[literal_at:literal_at + 4], "little")
    references = _references(model.image, literal)
    if references != 1:
        _refuse_all(decisions, placements,
                    f"table slot {selector} holds {pointer:#010x}, not a container, so the "
                    f"table would have to be moved before that slot can be used; the table "
                    f"at {table:#x} is named by {references} word-aligned references and a "
                    "table with more than one owner cannot be moved aside, so the slot is "
                    "not proven free")
        return None
    block = bytes(out[table:table + SELECTOR_SLOTS * 4])
    moved = builder.append(block, "container table")
    builder.write(literal_at, (ROM_BASE + moved).to_bytes(4, "little"),
                  "container table literal")
    warnings.append(
        f"the container table is copied to {ROM_BASE + moved:#010x} and the literal at "
        f"{literal_at:#x} repointed, because table slot {selector} held {pointer:#010x}, "
        "not a container, and the image's own table words are live structure")
    return moved


def _write_moves(model: Model, placements: list[_Placement], decisions: list[Decision],
                 builder: _Builder, table: int | None) -> tuple[list[_Placement], list[Decision]]:
    """Copy every moved record into the appended container, prefix carried forward.

    ``table`` is the offset of the table in force, which `_relocate_table` has
    already moved aside when the grown slot did not name a container. A grown slot
    that names no container has nothing to carry forward, so the payload starts
    empty; the slot is written at the end either way.
    """
    if not placements or table is None:
        return [], decisions
    selector = model.profile.grown_selector
    out = builder.out
    slot_at = table + selector * 4
    pointer = int.from_bytes(out[slot_at:slot_at + 4], "little")
    prefix = b""
    if ROM_BASE <= pointer < ROM_BASE + len(model.image):
        try:
            prefix = bytes(webfoot_lz.unpack(bytes(out), pointer - ROM_BASE).data)
        except webfoot_lz.ContainerError as error:
            _refuse_all(decisions, placements,
                        f"the container that table slot {selector} names does not decode, so "
                        f"its payload cannot be carried forward: {error}")
            return [], decisions
    kept: list[_Placement] = []
    for row in placements:
        bad = next((site for site in row.sites
                    if int.from_bytes(model.image[site:site + 4], "little") != row.old_handle),
                   None)
        if bad is not None:
            decisions[row.decision] = replace(
                decisions[row.decision], method=REFUSED,
                reason=f"handle site {bad:#06x} carries "
                       f"{int.from_bytes(model.image[bad:bad + 4], 'little'):#010x}, not this "
                       f"record's {row.old_handle:#010x}")
            continue
        kept.append(row)
    if not kept:
        return [], decisions
    payload = bytearray(prefix)
    placed: list[_Placement] = []
    for row in kept:
        encoded = row.text.encode("utf-16le")
        placed.append(replace(row, new_start=len(payload), new_length=len(encoded)))
        payload += encoded
    if len(payload) % 2:
        payload += bytes([0x00, 0x00])
    if len(payload) > PLACEMENT_CEILING:
        _refuse_all(decisions, kept,
                    f"the carried payload would be {len(payload)} bytes, above the "
                    f"{PLACEMENT_CEILING}-byte ceiling the start field addresses")
        return [], decisions
    at = builder.append((0).to_bytes(4, "little") + len(payload).to_bytes(4, "little")
                        + bytes(payload), f"container {selector} appended")
    builder.write(slot_at, (ROM_BASE + at).to_bytes(4, "little"), f"table slot {selector}")
    for row in placed:
        word = DialogueHandle(selector, row.new_start, row.new_length).encode().to_bytes(4, "little")
        for site in row.sites:
            builder.write(site, word, f"handle for {row.key}")
    return placed, decisions


def _write_slots(model: Model, slot_moves: list[_SlotMove], decisions: list[Decision],
                 builder: _Builder) -> tuple[list[_SlotMove], list[Decision]]:
    """Write each edited string-table slot in place, or append it and repoint its one word."""
    final: list[_SlotMove] = []
    for row in slot_moves:
        if decisions[row.decision].method == REFUSED:
            final.append(row)
            continue
        encoded = tt.encode_string(row.new)
        if row.method == IN_PLACE:
            padding = bytes(row.allocation - len(encoded))
            builder.write(row.offset, encoded + padding, f"text slot {row.slot}")
            final.append(row)
            continue
        word_at = model.profile.text_table + row.slot * 4
        before = int.from_bytes(model.image[word_at:word_at + 4], "little")
        references = _references(model.image, before)
        if references != 1:
            decisions[row.decision] = replace(
                decisions[row.decision], method=REFUSED,
                reason=f"slot {row.slot}'s pointer {before:#010x} has {references} word-aligned "
                       "references, so it cannot be repointed")
            final.append(row)
            continue
        at = builder.append(encoded, f"text slot {row.slot}")
        builder.write(word_at, (ROM_BASE + at).to_bytes(4, "little"),
                      f"text slot {row.slot} pointer")
        final.append(replace(row, at=at))
    return final, decisions


# --- reading the result back -------------------------------------------------


def _container_stream(model: Model, image: bytes, selector: int, cache: dict) -> bytes:
    """The decoded payload of one selector in `image`, decoded once per call site.

    The table is found through the literal in the OUTPUT image, because a move
    gives a record a selector the input did not carry and may have moved the table
    itself.
    """
    if selector not in cache:
        entry = _table_base(model.profile, image) + selector * 4
        pointer = int.from_bytes(image[entry:entry + 4], "little")
        if not ROM_BASE <= pointer < ROM_BASE + len(image):
            raise webfoot_lz.ContainerError(
                f"selector {selector} holds {pointer:#010x}, which names no container")
        cache[selector] = bytes(webfoot_lz.unpack(bytes(image), pointer - ROM_BASE).data)
    return cache[selector]


def _table_base(profile: TitleProfile, image: bytes) -> int:
    """The container table's file offset, read from the image's own literal."""
    literal = int.from_bytes(image[profile.table_literal:profile.table_literal + 4], "little")
    return literal - ROM_BASE


def _text_at_site(model: Model, image: bytes, site: int, cache: dict) -> tuple[str, str]:
    """The text the handle word at `site` names, and why it could not be read."""
    word = int.from_bytes(image[site:site + 4], "little")
    selector, start, length = unpack_handle(word)
    try:
        stream = _container_stream(model, image, selector, cache)
    except webfoot_lz.ContainerError as error:
        return "", f"site {site:#06x} names selector {selector}: {error}"
    if start + length > len(stream):
        return "", (f"site {site:#06x} names {start}:{length} of selector {selector}, past its "
                    f"{len(stream)}-byte payload")
    return stream[start:start + length].decode("utf-16le"), ""


def readback(plan: Plan) -> tuple[str, ...]:
    """Read the built image back through the handles and report every disagreement.

    P-030: a moved record is checked at its HANDLE, never at the address it held
    before the move. P-007: an expected value comes from the plan, never from
    searching the payload for the wording. Every live SITE is checked, keyed by the
    site itself, so a record that moved out of a container that was also edited in
    place is checked once, against the text its own new handle names, and never
    against the row it left behind. Every record of the grown selector is checked
    too, which is the carry-forward proof: a record an earlier release placed there
    must still read its own text at its own offset.
    """
    model = plan.model
    image = plan.output
    cache: dict[int, bytes] = {}
    problems: list[str] = []
    expected: dict[int, tuple[str, bool]] = {}
    for row in model.records:
        want = row.text
        for item in plan.in_place:
            if (plan.decisions[item.decision].method == IN_PLACE
                    and item.selector == row.selector
                    and row.start <= item.start < row.start + row.length):
                want = want.replace(item.old, item.new)
        for site in row.sites:
            expected[site] = (want, False)
    for row in plan.placements:
        for site in row.sites:
            expected[site] = (row.text, True)
    for site in sorted(expected):
        want, exact = expected[site]
        got, why = _text_at_site(model, image, site, cache)
        if why:
            problems.append(why)
        elif exact and got != want:
            problems.append(f"site {site:#06x} reads {got[:50]!r}, expected {want[:50]!r}")
        elif not exact and got.replace(" ", "") != want.replace(" ", ""):
            problems.append(f"site {site:#06x} reads {got[:50]!r}, expected {want[:50]!r}")
    for row in plan.slot_moves:
        if plan.decisions[row.decision].method == REFUSED:
            continue
        try:
            got, _offset, _allocation = _raw_slot(image, model.profile, row.slot)
        except TextEditError as error:
            problems.append(f"text:{row.slot}: {error}")
            continue
        if got != row.new:
            problems.append(f"text:{row.slot}: reads {got[:50]!r}, expected {row.new[:50]!r}")
    return tuple(problems)


# --- the writer --------------------------------------------------------------


def apply(plan: Plan, out_path: str | Path) -> dict:
    """Write the plan to a new file, or refuse and write nothing.

    The order is the safety property: a refused edit or a failed readback raises
    before any byte is staged; the destination is checked against the protected
    ROM inputs, against the input file's own identity and against the canonical
    image opened as the retail reference (a hard link to either is the same file);
    an existing output is refused rather than overwritten; and the staged file is
    read back and compared with the verified bytes before it is renamed into
    place. The staged name is unpredictable and is created exclusively, so a
    leftover cannot be mistaken for an output and a stale name cannot be occupied.
    """
    refusals = plan.refusals
    if refusals:
        raise TextEditError("REFUSED: " + "; ".join(
            f"{item.target}: {item.reason}" for item in refusals))
    target = Path(out_path)
    try:
        for source in (plan.model.path, plan.model.retail_path):
            if source is None:
                continue
            refuse_rom_destination(source, target)
            ensure_not_source_alias(source, target)
        ensure_new_destination(target)
    except WriteError as error:
        raise TextEditError(f"REFUSED: {error}") from error
    problems = readback(plan)
    if problems:
        raise TextEditError("REFUSED: the built image does not read back: "
                            + "; ".join(problems))
    staged = None
    try:
        handle = tempfile.NamedTemporaryFile(dir=target.parent, prefix=target.name + ".",
                                             suffix=".staged", delete=False)
        staged = Path(handle.name)
        with handle:
            handle.write(plan.output)
            handle.flush()
            os.fsync(handle.fileno())
        if staged.read_bytes() != plan.output:
            raise TextEditError("REFUSED: the staged write does not match the verified bytes")
        os.replace(staged, target)
    except BaseException:
        if staged is not None:
            staged.unlink(missing_ok=True)
        raise
    return {**plan.summary, "output": str(target)}
