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
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .. import compressed_dialogue as cd
from ..binary import GBA_ROM_BASE as ROM_BASE
from ..destination import refuse_rom_destination
from ..dialogue_repack import container_pointers, text_of
from ..formats import text_tables as tt
from ..formats import webfoot_lz
from ..handles import DialogueHandle, unpack_handle
from ..write import WriteError, ensure_not_source_alias

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

    @property
    def slot_at(self) -> int:
        """File offset of the table slot the appended container is written into."""
        return self.table_offset + self.profile.grown_selector * 4


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
    retail_sha256: str | None = None
    retail_streams: Mapping[int, bytes] = ()

    @property
    def profile(self) -> TitleProfile:
        return self.layout.profile

    def record(self, selector: int, start: int, length: int) -> Record | None:
        return self.by_key.get(f"{selector}:{start}:{length}")

    def selector_records(self, selector: int) -> tuple[Record, ...]:
        return tuple(record for record in self.records if record.selector == selector)


def locked_tokens(text: str) -> tuple[str, ...]:
    """Every control unit in `text`, in order, as the raw unit(s) it occupies.

    Measured on the seven compressed containers: a control unit is a halfword
    below 0x20 with a zero high byte, and 0x0008 consumes the following halfword
    as its operand. The three 0x00A0-range units the containers also carry are
    text, not control, and are not tokens.
    """
    tokens = []
    position = 0
    while position < len(text):
        codepoint = ord(text[position])
        if codepoint < 0x20:
            if codepoint == 0x08 and position + 1 < len(text):
                tokens.append(text[position:position + 2])
                position += 2
                continue
            tokens.append(text[position])
        position += 1
    return tuple(tokens)


def open_rom(rom_path: str | Path, canonical: str | Path | None = None) -> Model:
    """Open an image read-only, with the canonical image as the retail reference."""
    path = Path(rom_path)
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    layout = detect(image)
    records = _read_records(image, layout)
    if len(records) < MINIMUM_DIALOGUE_RECORDS:
        raise TextEditError(
            f"REFUSED: {path} carries {len(records)} dialogue record(s), under the "
            f"{MINIMUM_DIALOGUE_RECORDS}-record floor this profile validates against")
    slots = _read_slots(image, layout.profile)
    retail_sha256 = None
    retail_streams: Mapping[int, bytes] = {}
    if canonical is not None:
        retail_path = Path(canonical)
        retail = retail_path.read_bytes()
        retail_layout = detect(retail)
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
    if not old:
        raise TextEditError("REFUSED: a rename needs a name to replace")
    if len(current) != len(counterpart):
        raise TextEditError(
            f"REFUSED: the record is {len(current)} units and its retail counterpart is "
            f"{len(counterpart)}, so character offsets do not correspond and an occurrence "
            "cannot be attributed to an actor")
    pieces = []
    cursor = 0
    renamed = kept = unclear = 0
    while True:
        position = current.find(old, cursor)
        if position == -1:
            break
        retail_word = counterpart[position:position + len(old)]
        pieces.append(current[cursor:position])
        if retail_word == old:
            pieces.append(new)
            renamed += 1
        else:
            pieces.append(old)
            rival = counterpart[position:position + len(old)]
            if rival != old and any(character.isalpha() for character in rival):
                kept += 1
            else:
                unclear += 1
        cursor = position + len(old)
    pieces.append(current[cursor:])
    return "".join(pieces), renamed, kept, unclear


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
    in_place, decisions, rewritten = _write_in_place(model, in_place, decisions, builder)
    placements, decisions = _write_moves(model, placements, decisions, builder, warnings)
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
            entry = model.layout.table_offset + selector * 4
            builder.write(entry, (ROM_BASE + at).to_bytes(4, "little"), f"table slot {selector}")
        else:
            builder.write(at, packed, f"container {selector}")
        rewritten.add(selector)
        final.extend(applied)
    return final, decisions, rewritten


def _write_moves(model: Model, placements: list[_Placement], decisions: list[Decision],
                 builder: _Builder, warnings: list[str]) -> tuple[list[_Placement], list[Decision]]:
    """Copy every moved record into the appended container, prefix carried forward."""
    if not placements:
        return [], decisions
    selector = model.profile.grown_selector
    slot_at = model.layout.slot_at
    if slot_at + 4 > len(model.image):
        for row in placements:
            decisions[row.decision] = replace(decisions[row.decision], method=REFUSED,
                                              reason="the grown selector's table slot lies outside "
                                                     "the image")
        return [], decisions
    prefix = b""
    pointer = int.from_bytes(model.image[slot_at:slot_at + 4], "little")
    if not ROM_BASE <= pointer < ROM_BASE + len(model.image):
        warnings.append(
            f"table slot {selector} did not name a container and is being taken for this "
            f"image's appended container; it held {pointer:#010x} before this export")
    else:
        try:
            prefix = bytes(webfoot_lz.unpack(model.image, pointer - ROM_BASE).data)
        except webfoot_lz.ContainerError as error:
            for row in placements:
                decisions[row.decision] = replace(
                    decisions[row.decision], method=REFUSED,
                    reason=f"the container that table slot {selector} names does not decode, so "
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
        for row in kept:
            decisions[row.decision] = replace(
                decisions[row.decision], method=REFUSED,
                reason=f"the carried payload would be {len(payload)} bytes, above the "
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

    The selector is read from the OUTPUT image's own table, because a move gives
    a record a selector the input did not carry.
    """
    if selector not in cache:
        entry = model.layout.table_offset + selector * 4
        pointer = int.from_bytes(image[entry:entry + 4], "little")
        if not ROM_BASE <= pointer < ROM_BASE + len(image):
            raise webfoot_lz.ContainerError(
                f"selector {selector} holds {pointer:#010x}, which names no container")
        cache[selector] = bytes(webfoot_lz.unpack(image, pointer - ROM_BASE).data)
    return cache[selector]


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
    searching the payload for the wording. Every record of a rewritten container
    is checked, which is also the carry-forward proof: a record an earlier release
    placed in the grown selector must still read its own text at its own offset.
    """
    model = plan.model
    image = plan.output
    cache: dict[int, bytes] = {}
    problems: list[str] = []
    for row in model.records:
        if row.selector not in plan.rewritten_selectors:
            continue
        want = row.text
        for item in plan.in_place:
            if (plan.decisions[item.decision].method == IN_PLACE
                    and item.selector == row.selector
                    and row.start <= item.start < row.start + row.length):
                want = want.replace(item.old, item.new)
        got, why = _text_at_site(model, image, row.sites[0], cache)
        if why:
            problems.append(f"{row.key}: {why}")
        elif got.replace(" ", "") != want.replace(" ", ""):
            problems.append(f"{row.key}: reads {got[:50]!r}, expected {want[:50]!r}")
    for row in plan.placements:
        for site in row.sites:
            got, why = _text_at_site(model, image, site, cache)
            if why:
                problems.append(f"{row.key}: {why}")
            elif got != row.text:
                problems.append(f"{row.key}: site {site:#06x} reads {got[:50]!r}, expected "
                                f"{row.text[:50]!r}")
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
    before any byte is staged, the destination is checked against the protected
    ROM inputs and against the input file's own identity (a hard link to the
    input is the same file), and the staged file is read back and compared with
    the verified bytes before it is renamed into place.
    """
    refusals = plan.refusals
    if refusals:
        raise TextEditError("REFUSED: " + "; ".join(
            f"{item.target}: {item.reason}" for item in refusals))
    target = Path(out_path)
    source = plan.model.path
    try:
        refuse_rom_destination(source, target)
        ensure_not_source_alias(source, target)
    except WriteError as error:
        raise TextEditError(f"REFUSED: {error}") from error
    problems = readback(plan)
    if problems:
        raise TextEditError("REFUSED: the built image does not read back: "
                            + "; ".join(problems))
    staged = target.with_name(target.name + ".staged")
    staged.write_bytes(plan.output)
    if staged.read_bytes() != plan.output:
        raise TextEditError("REFUSED: the staged write does not match the verified bytes")
    staged.replace(target)
    return {**plan.summary, "output": str(target)}
