"""Project-build materialization for measured compressed-dialogue resources.

DIALOGUE-VARIABLE-LENGTH-001 turned this module from a fixed-length overwrite
into a **deterministic container re-layout**, and the three things that follow
from that are worth stating before the code.

**A record's durable identity is a handle, and the handle is authored.** Retail
stores, in the record's ``+0x04``, a packed u32 naming a decoded span:
selector, decoded start and decoded length, all in :mod:`tools.webfoot.handles`'
one bit layout. A replacement that encodes to a different length therefore
cannot reuse the retail handle - it needs a *new* handle, built from semantic
fields, and every ROM word that named the old one must be repointed. This module
authors that handle; nothing here shifts bits by hand.

**Growing one record moves the records after it.** The decoded container is a
packed stream of records placed consecutively from offset 0: measured on the
canonical image, selector 1 holds 447 distinct records whose adjacent spans are
consecutive in 410 of 446 adjacent pairs, and the record at the edit boundary
``0x132..0x152`` is **the only record that intersects it**. So the Re-layout rule
is: splice the new text into the record's own span, and shift every record that
starts at or after its old end by the difference. A record's start is absolute,
so each shifted record's handle is re-authored with it, and each of those
handles has to be written back at every site that carries it.

**Only a proven reader counts as a reference.** A packed handle is read by the
engine in exactly one place that has been established: the bytecode dispatch
loop at ``0x08012552`` branches on **byte ``+0x02`` of the record word**, and
only kind ``0x05`` reaches the compressed-dialogue consumer at ``0x08012230``,
which loads ``[record + 0x04]`` as the handle (TEXT-HANDLE-001,
TEXT-HANDLE-002, both runtime-proven). The reference inventory is therefore
built from that structure and from nothing else. It is deliberately **not** "every
word that happens to unpack to a valid span": on the canonical image 46,298
distinct selector-1 words in that weak sense occur 59,491 times, of which only
143 are ever read as handles. Rewriting them would corrupt code and data.

The measured boundary this leaves
---------------------------------

The re-layout is defined for a record whose span no other record crosses, which
is what the canonical target is and which the module *checks* rather than
assumes: a container whose records straddle the edit boundary is refused with
that reason. Growth is additionally bounded by the toolkit's own container
decoder, whose safety limit is 64 KiB of decoded output and which a retail
dialogue container already fills to within 62 bytes - so the honest ceiling for
*this* target is a 94-byte replacement, well below the 4,094 bytes the handle's
length field can encode.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from .allocation import (Addressability, Allocation, AllocationKind, AllocationRequest,
                         allocate)
from .binary import FileOffset, GBA_ROM_BASE
from .formats.webfoot_lz import (DEFAULT_MAX_OUTPUT, ContainerError, pack, unpack,
                                 validate_retail_termination)
from .handles import DialogueHandle, HandleError, unpack_handle
from .layout import AnchorId, OwnedRegion, RomRange
from .profile import RomProfile
from .write import (ByteChange, DialogueEditProvenance, GeneratedAllocationProvenance,
                    GeneratedImage, WritePlan, plan_changes)


class CompressedDialogueError(ValueError):
    pass


# --- the proven handle-carrying structure ------------------------------------
#
# Measured, not assumed. The record word of the family the compressed-dialogue
# consumer is reached from is `idx, 0x00, 0x05, NN`: 0x68050001 is the retail
# target's own record word (TEXT-HANDLE-002), and the dispatch loop at
# 0x08012552 branches on byte +0x02 while the consumer reads +0x04. The three
# runtime-observed carriers of the target handle are all of this shape, so the
# inventory is a structure query and not a value-pattern guess.

#: The ``+0x02`` byte that selects the compressed-dialogue consumer.
TEXT_RECORD_KIND = 0x05
TEXT_RECORD_KIND_OFFSET = 2
#: The ``+0x01`` byte, zero in every measured member of the family. Requiring it
#: is what excludes Thumb code: the instruction bytes ``05 68`` put 0x05 at
#: ``+0x02`` of the word before them and otherwise match.
TEXT_RECORD_ZERO_OFFSET = 1
TEXT_RECORD_ZERO_VALUE = 0x00
#: Where the packed handle sits inside the record.
TEXT_RECORD_HANDLE_OFFSET = 4
#: One record word plus its handle word.
TEXT_RECORD_SIZE = 8

#: Selector slots the container-pointer table is probed for, one past the seven
#: measured containers so the eighth slot is seen to be *not* a container
#: pointer rather than silently truncated.
_CONTAINER_TABLE_PROBE = 8


@dataclass(frozen=True, slots=True)
class CompressedDialogueTarget:
    """Measured immutable identity of one record inside one container.

    ``decoded_start`` and ``decoded_length`` are the RETAIL record's fields, as
    measured. They stay the record's authoritative *position*: the authoring
    operation splices at the record's own end, so its start is invariant across
    every edit, and a replacement's length lives on the authored handle rather
    than here.
    """

    name: str
    selector: int
    table_offset: int
    packed_handle: int
    decoded_start: int
    decoded_length: int
    profile_id: str | None = None


@dataclass(frozen=True, slots=True)
class DialogueRecord:
    """One handle-defined decoded span and every ROM word that carries it.

    ``sites`` are FILE OFFSETS of the handle field (record ``+0x04``). One
    identity, a list of places - collapsing them would turn one message into
    several, and treating one place as the whole of the record's reach is how a
    patcher silently orphans the others.
    """

    handle: DialogueHandle
    sites: tuple[int, ...]

    @property
    def raw_handle(self) -> int:
        return self.handle.encode()

    def to_json(self) -> dict:
        return {**self.handle.to_json(),
                "reference_sites": [f"0x{site:06X}" for site in self.sites],
                "reference_site_count": len(self.sites)}


@dataclass(frozen=True, slots=True)
class DialogueLayout:
    """One decoded container, its decoded bytes, and its record inventory."""

    selector: int
    container_offset: int
    packed_end: int
    decoded: bytes
    records: tuple[DialogueRecord, ...]

    @property
    def packed_size(self) -> int:
        return self.packed_end - self.container_offset

    def records_starting_at(self, decoded_start: int) -> tuple[DialogueRecord, ...]:
        """Every record whose span begins exactly at ``decoded_start``.

        Plural on purpose: a container legitimately holds records that share a
        start and differ only in length - selector 1 holds three that begin at
        offset 0 - so a start alone does not name one record.
        """
        return tuple(record for record in self.records
                     if record.handle.decoded_start == decoded_start)

    def record_with_span(self, decoded_start: int, decoded_length: int
                         ) -> DialogueRecord | None:
        """The one record carrying exactly this measured span, if it exists."""
        for record in self.records:
            if (record.handle.decoded_start == decoded_start
                    and record.handle.decoded_length == decoded_length):
                return record
        return None

    def sole_record_starting_at(self, decoded_start: int) -> DialogueRecord | None:
        """The only record beginning at ``decoded_start``, or None if ambiguous.

        Ambiguity is reported as absence rather than resolved by a tie-break: a
        caller that meant one record and got another would repoint the wrong
        message, and which of two records sharing a start a searcher meant is
        not something the image answers.
        """
        matches = self.records_starting_at(decoded_start)
        return matches[0] if len(matches) == 1 else None

    def records_crossing(self, start: int, end: int) -> tuple[DialogueRecord, ...]:
        """Records whose span overlaps ``[start, end)`` without being equal to it.

        The re-layout rule is defined only when this is empty: a record that
        partly covers the edited span would have to change *content*, and no
        measured evidence says how the engine expects that to be expressed.
        """
        return tuple(
            record for record in self.records
            if record.handle.decoded_start < end and start < record.handle.decoded_end
            and not (record.handle.decoded_start == start
                     and record.handle.decoded_end == end)
        )

    def with_decoded(self, decoded: bytes,
                     records: tuple[DialogueRecord, ...]) -> "DialogueLayout":
        return replace(self, decoded=decoded, records=records)

    def to_json(self) -> dict:
        return {
            "selector": self.selector,
            "container_file_offset": self.container_offset,
            "decoded_size": len(self.decoded),
            "packed_size": self.packed_size,
            "record_count": len(self.records),
            "reference_site_count": sum(len(r.sites) for r in self.records),
            "records": [record.to_json() for record in self.records],
        }


@dataclass(frozen=True, slots=True)
class DialogueRelayout:
    """The deterministic result of changing one record's decoded length."""

    layout: DialogueLayout
    encoded: bytes
    decoded: bytes
    edited: DialogueRecord
    new_handle: DialogueHandle
    #: ``(old, new)`` for every displaced record, in ascending old start.
    moved: tuple[tuple[DialogueHandle, DialogueHandle], ...]
    reference_changes: tuple[ByteChange, ...]

    @property
    def decoded_delta(self) -> int:
        return len(self.encoded) - self.edited.handle.decoded_length

    @property
    def records(self) -> tuple[DialogueRecord, ...]:
        """The rebuilt container's inventory, with every handle re-authored.

        Keyed on the durable handle, which is unique per record, rather than on
        the decoded start, which is not.
        """
        renamed = {self.edited.raw_handle: self.new_handle}
        renamed.update({old.encode(): new for old, new in self.moved})
        return tuple(replace(record, handle=renamed[record.raw_handle])
                     if record.raw_handle in renamed else record
                     for record in self.layout.records)

    def to_json(self) -> dict:
        return {
            "old_handle": f"0x{self.edited.raw_handle:08X}",
            "new_handle": f"0x{self.new_handle.encode():08X}",
            "old_decoded_start": self.edited.handle.decoded_start,
            "new_decoded_start": self.new_handle.decoded_start,
            "old_decoded_length": self.edited.handle.decoded_length,
            "new_decoded_length": self.new_handle.decoded_length,
            "decoded_length_delta": self.decoded_delta,
            "displaced_record_count": len(self.moved),
            "reference_changes": len(self.reference_changes),
        }


@dataclass(frozen=True, slots=True)
class CompressedDialogueBuild:
    target: CompressedDialogueTarget
    old_container_offset: int
    old_allocation: int
    payload: bytes
    allocation: Allocation | None
    changes: tuple[ByteChange, ...]
    generated_allocation: GeneratedAllocationProvenance | None
    plan: WritePlan | None = None
    #: DIALOGUE-VARIABLE-LENGTH-001. The record-and-handle provenance for this
    #: edit, carried to the write manifest through the plan.
    dialogue_edit: DialogueEditProvenance | None = None
    #: The original and rebuilt inventories, for tests and for the report.
    layout: DialogueLayout | None = None
    relayout: DialogueRelayout | None = None


AUTHORED_DIALOGUE_TARGETS = {
    "goku-greeting": CompressedDialogueTarget(
        "goku-greeting", 1, 0x7B5B64, 0x02002641, 0x132, 0x20,
        "buus_fury_usa_rev0_01c1707f",
    ),
}


def target_named(name: str) -> CompressedDialogueTarget:
    try:
        return AUTHORED_DIALOGUE_TARGETS[name]
    except KeyError as exc:
        raise CompressedDialogueError(f"unsupported authored dialogue target: {name}") from exc


def _retail_container(canonical: bytes, profile: RomProfile,
                      target: CompressedDialogueTarget):
    if target.profile_id is not None and profile.id != target.profile_id:
        raise CompressedDialogueError(
            f"{target.name}: target is not supported by profile {profile.id!r}"
        )
    table_slot = target.table_offset + target.selector * 4
    if not 0 <= table_slot <= len(canonical) - 8:
        raise CompressedDialogueError("container-table slot lies outside canonical ROM")
    old_pointer = int.from_bytes(canonical[table_slot:table_slot + 4], "little")
    if old_pointer < GBA_ROM_BASE:
        raise CompressedDialogueError("container-table slot is not a ROM pointer")
    old_offset = FileOffset(old_pointer - GBA_ROM_BASE).value
    if old_offset >= len(canonical):
        raise CompressedDialogueError("container-table slot is not a canonical ROM pointer")
    return table_slot, old_offset, unpack(canonical, old_offset)


def container_selectors(canonical: bytes, table_offset: int) -> tuple[int, ...]:
    """Which selector slots of the container table actually name a container.

    Used by the container-wide invariant: a record may only be authored against
    a selector some table slot resolves. The probe runs one slot past the seven
    measured containers so an eighth entry is seen to be *not* a container
    pointer rather than silently ignored.
    """
    selectors = []
    for selector in range(_CONTAINER_TABLE_PROBE):
        slot = table_offset + selector * 4
        if slot + 4 > len(canonical):
            break
        word = int.from_bytes(canonical[slot:slot + 4], "little")
        if word < GBA_ROM_BASE or word - GBA_ROM_BASE >= len(canonical):
            continue
        try:
            container = unpack(canonical, word - GBA_ROM_BASE)
        except ContainerError:
            continue
        if not container.declared_size:
            continue
        selectors.append(selector)
    return tuple(selectors)


def dialogue_record_inventory(image: bytes, selector: int,
                              decoded_size: int) -> tuple[DialogueRecord, ...]:
    """Every ROM word that the engine's own dispatch reads as a handle.

    The query is structural: a 4-byte-aligned record word whose ``+0x01`` is
    zero and whose ``+0x02`` is :data:`TEXT_RECORD_KIND`, followed by a word that
    decodes to a legal span inside the container this selector names. Words that
    merely *unpack* plausibly are not references - see the module docstring for
    the measured size of that population - and a site outside this structure is
    left untouched.
    """
    found: dict[int, list[int]] = {}
    position = image.find(bytes([TEXT_RECORD_ZERO_VALUE, TEXT_RECORD_KIND]))
    while position != -1:
        record = position - TEXT_RECORD_ZERO_OFFSET
        if record >= 0 and record % 4 == 0 and record + TEXT_RECORD_SIZE <= len(image):
            handle = int.from_bytes(
                image[record + TEXT_RECORD_HANDLE_OFFSET:
                      record + TEXT_RECORD_HANDLE_OFFSET + 4], "little")
            record_selector, start, size = unpack_handle(handle)
            if (record_selector == selector and size and start % 2 == 0
                    and start + size <= decoded_size):
                found.setdefault(handle, []).append(
                    record + TEXT_RECORD_HANDLE_OFFSET)
        position = image.find(bytes([TEXT_RECORD_ZERO_VALUE, TEXT_RECORD_KIND]),
                              position + 1)
    return tuple(
        DialogueRecord(DialogueHandle.decode(handle), tuple(sorted(sites)))
        for handle, sites in sorted(found.items())
    )


def read_container_layout(canonical: bytes, profile: RomProfile,
                          target: CompressedDialogueTarget) -> DialogueLayout:
    """The target container's decoded bytes and its complete record inventory."""
    table_slot, old_offset, container = _retail_container(canonical, profile, target)
    records = dialogue_record_inventory(canonical, target.selector, len(container.data))
    return DialogueLayout(target.selector, old_offset, container.packed_end,
                          container.data, records)


def validate_container_layout(layout: DialogueLayout) -> None:
    """The container-wide invariant. Fails closed; never repairs.

    For every record: the handle's fields are legal and round-trip through the
    one encoder, its selector is the selector the layout was built for, its span
    is inside the decoded container, and its length is a positive whole number of
    halfwords. A container that fails this never reaches a pack, an allocation or
    a plan.
    """
    if not layout.records:
        raise CompressedDialogueError(
            f"selector {layout.selector}: no handle-carrying record was found in "
            "this image, so no record can be authored against it"
        )
    seen_handles: set[int] = set()
    for record in layout.records:
        handle = record.handle
        if handle.selector != layout.selector:
            raise CompressedDialogueError(
                f"record 0x{record.raw_handle:08X} names selector {handle.selector}, "
                f"not this container's {layout.selector}"
            )
        if not record.sites:
            raise CompressedDialogueError(
                f"record 0x{record.raw_handle:08X} has no reference site"
            )
        if handle.decoded_start < 0 or handle.decoded_end > len(layout.decoded):
            raise CompressedDialogueError(
                f"record 0x{record.raw_handle:08X} spans "
                f"[{handle.decoded_start}, {handle.decoded_end}) outside the "
                f"{len(layout.decoded)}-byte decoded container"
            )
        encoded = handle.encode()
        if encoded in seen_handles:
            raise CompressedDialogueError(
                f"two records share the durable handle 0x{encoded:08X}"
            )
        seen_handles.add(encoded)
        if DialogueHandle.decode(encoded) != handle:
            raise CompressedDialogueError(
                f"durable handle 0x{encoded:08X} does not round-trip"
            )


def relayout_for_length(layout: DialogueLayout, target: CompressedDialogueTarget,
                        encoded: bytes, owner: str, image: bytes) -> DialogueRelayout:
    """Splice ``encoded`` into the target record and re-author every handle.

    Deterministic, and checked at every step:

    * the target record is located by its measured span - the start the
      authoring operation never moves, plus the retail length, so an image that
      is not the measured base is refused rather than patched against the wrong
      layout;
    * no OTHER record may cross the edited span, because such a record would
      have to change content and no evidence defines how;
    * the rebuilt container must remain inside the toolkit's own decoder limit;
    * every displaced record's new handle is encoded through the one encoder, so
      a start that overflows the field is a refusal and not a truncated write.
    """
    if not encoded:
        raise CompressedDialogueError(
            f"{target.name}: replacement dialogue must not be empty"
        )
    validate_container_layout(layout)
    edited = layout.record_with_span(target.decoded_start, target.decoded_length)
    if edited is None:
        raise CompressedDialogueError(
            f"{target.name}: this image has no record spanning decoded "
            f"0x{target.decoded_start:X}..0x{target.decoded_start + target.decoded_length:X}"
        )

    start, end = edited.handle.decoded_start, edited.handle.decoded_end
    crossing = layout.records_crossing(start, end)
    if crossing:
        raise CompressedDialogueError(
            f"{target.name}: {len(crossing)} other record(s) cross the edited span "
            f"0x{start:X}..0x{end:X}, so growing this record has no defined "
            "re-layout in this container"
        )

    delta = len(encoded) - edited.handle.decoded_length
    decoded = layout.decoded[:start] + encoded + layout.decoded[end:]
    if len(decoded) > DEFAULT_MAX_OUTPUT:
        raise CompressedDialogueError(
            f"{target.name}: the rebuilt container would decode to {len(decoded)} "
            f"bytes, above this toolkit's {DEFAULT_MAX_OUTPUT}-byte container "
            "decoder limit; the limit is a host safety bound rather than a format "
            "fact, and lifting it is a separate decision"
        )

    try:
        new_handle = edited.handle.replace(decoded_length=len(encoded))
    except HandleError as exc:
        raise CompressedDialogueError(
            f"{target.name}: a {len(encoded)}-byte replacement cannot be encoded "
            f"in a durable handle: {exc}"
        ) from exc

    moved: list[tuple[DialogueHandle, DialogueHandle]] = []
    for record in layout.records:
        if delta == 0 or record is edited or record.handle.decoded_start < end:
            continue
        try:
            moved.append((record.handle,
                          record.handle.replace(
                              decoded_start=record.handle.decoded_start + delta)))
        except HandleError as exc:
            raise CompressedDialogueError(
                f"{target.name}: displacing the record at decoded offset "
                f"0x{record.handle.decoded_start:X} by {delta} bytes overflows the "
                f"durable handle's start field: {exc}"
            ) from exc
    moved.sort(key=lambda pair: pair[0].decoded_start)

    renamed = {edited.raw_handle: new_handle}
    renamed.update({old.encode(): new for old, new in moved})

    changes: list[ByteChange] = []
    for record in layout.records:
        new = renamed.get(record.raw_handle)
        if new is None or new == record.handle:
            continue
        for site in record.sites:
            old_word = image[site:site + 4]
            if len(old_word) != 4:
                raise CompressedDialogueError(
                    f"{target.name}: handle site 0x{site:06X} lies outside the image"
                )
            changes.append(ByteChange(
                offset=site,
                old=old_word,
                new=_word_bytes(new.encode()),
                owner=owner,
                reason=(
                    f"durable handle re-authored from 0x{record.raw_handle:08X} to "
                    f"0x{new.encode():08X} after the record's decoded layout changed"
                ),
            ))
    changes.sort(key=lambda change: change.offset)

    return DialogueRelayout(layout=layout, encoded=encoded, decoded=decoded,
                            edited=edited, new_handle=new_handle,
                            moved=tuple(moved),
                            reference_changes=tuple(changes))


def _word_bytes(value: int) -> bytes:
    return value.to_bytes(4, "little")


def validate_relayout(relayout: DialogueRelayout, image: bytes) -> None:
    """Neighbour and reference-consistency invariant. Fails closed.

    Two properties, both about what did NOT change:

    * **every unedited record still decodes to exactly the bytes it decoded to
      before.** This is the neighbour proof: a record that was truncated, that
      points into the middle of another, or whose start was not shifted when its
      bytes moved all fail it, and nothing else can;
    * **reference consistency**: every ROM word that carried a superseded handle
      is rewritten exactly once to that record's new handle, and no word outside
      the proven carrier structure is touched at all.

    And two about the edited record, which are what M1 ("keep the old length")
    has to fail: its span must still begin at the retail start - the record's
    anchor, which the authoring operation never moves - and must decode to
    exactly the replacement's bytes, not to a prefix of them.
    """
    rebuilt = relayout.decoded

    if relayout.new_handle.decoded_start != relayout.edited.handle.decoded_start:
        raise CompressedDialogueError(
            f"the authored record moved from decoded offset "
            f"0x{relayout.edited.handle.decoded_start:X} to "
            f"0x{relayout.new_handle.decoded_start:X}; this authoring operation "
            "replaces a record in place and must not move its anchor"
        )
    authored = rebuilt[relayout.new_handle.decoded_start:relayout.new_handle.decoded_end]
    if authored != relayout.encoded:
        raise CompressedDialogueError(
            f"the authored record's decoded span is {len(authored)} bytes and does "
            f"not carry the {len(relayout.encoded)}-byte replacement"
        )

    for record in relayout.layout.records:
        if record is relayout.edited:
            continue
        new = dict(relayout.moved).get(record.handle, record.handle)
        before = relayout.layout.decoded[record.handle.decoded_start:
                                        record.handle.decoded_end]
        after = rebuilt[new.decoded_start:new.decoded_end]
        if before != after:
            raise CompressedDialogueError(
                f"record 0x{record.raw_handle:08X} no longer decodes to its own "
                f"bytes after the re-layout (0x{record.handle.decoded_start:X} -> "
                f"0x{new.decoded_start:X})"
            )

    carriers = {site for record in relayout.layout.records for site in record.sites}
    expected: dict[int, int] = {}
    for record in relayout.layout.records:
        new = (relayout.new_handle if record is relayout.edited
               else dict(relayout.moved).get(record.handle))
        if new is None or new == record.handle:
            continue
        for site in record.sites:
            expected[site] = new.encode()
    written = {change.offset: int.from_bytes(change.new, "little")
               for change in relayout.reference_changes}
    if set(written) != set(expected):
        missing = sorted(set(expected) - set(written))
        extra = sorted(set(written) - set(expected))
        raise CompressedDialogueError(
            "reference update is incomplete: "
            f"{len(missing)} required site(s) not rewritten {missing[:4]}, "
            f"{len(extra)} unexpected site(s) rewritten {extra[:4]}"
        )
    for site, value in written.items():
        if site not in carriers:
            raise CompressedDialogueError(
                f"a word at 0x{site:06X} that no record reads as a handle was "
                "rewritten"
            )
        if value != expected[site]:
            raise CompressedDialogueError(
                f"the handle word at 0x{site:06X} was written as 0x{value:08X} "
                f"instead of 0x{expected[site]:08X}"
            )
    for change in relayout.reference_changes:
        if image[change.offset:change.offset + 4] != change.old:
            raise CompressedDialogueError(
                f"the handle word at 0x{change.offset:06X} is not the value this "
                "plan was computed from"
            )


def read_original_text(canonical: bytes, profile: RomProfile,
                       target: CompressedDialogueTarget) -> str:
    """Decode the span this record's CURRENT durable handle names in this image.

    Read through the record's own handle rather than through the registry's
    frozen retail length. The registry supplies the record's *position*, which
    the authoring operation never moves; the image supplies whatever length the
    handle currently carries. So this answers ``Good luck, Goku!`` for the
    canonical ROM and the authored line for a derivative this toolkit built -
    the same call, the same code path, which is what makes a derivative reopen
    resolve its record rather than fail on a stale handle.
    """
    layout = read_container_layout(canonical, profile, target)
    record = layout.sole_record_starting_at(target.decoded_start)
    if record is None:
        raise CompressedDialogueError(
            f"{target.name}: this image holds no single dialogue record starting "
            f"at decoded offset 0x{target.decoded_start:X}"
        )
    span = layout.decoded[record.handle.decoded_start:record.handle.decoded_end]
    try:
        return span.decode("utf-16le")
    except UnicodeDecodeError as exc:
        raise CompressedDialogueError(
            f"{target.name}: retail dialogue is not valid UTF-16LE"
        ) from exc


def _prepare_replacement(canonical: bytes, profile: RomProfile,
                         target: CompressedDialogueTarget, replacement: str,
                         reserved: Iterable[RomRange]) -> CompressedDialogueBuild:
    if profile.generated_expansion is None:
        raise CompressedDialogueError("profile declares no verified generated expansion")
    if not replacement:
        raise CompressedDialogueError("replacement dialogue must not be empty")
    table_slot, old_offset, container = _retail_container(canonical, profile, target)
    try:
        encoded = replacement.encode("utf-16le")
    except UnicodeEncodeError as exc:
        raise CompressedDialogueError(
            f"{target.name}: replacement dialogue cannot be encoded as UTF-16LE: {exc}"
        ) from exc
    if not encoded:
        raise CompressedDialogueError("replacement dialogue must not be empty")

    layout = DialogueLayout(
        target.selector, old_offset, container.packed_end, container.data,
        dialogue_record_inventory(canonical, target.selector, len(container.data)),
    )
    resolved = container_selectors(canonical, target.table_offset)
    if target.selector not in resolved:
        raise CompressedDialogueError(
            f"{target.name}: selector {target.selector} is not a container this "
            f"image's table resolves (it names {list(resolved)})"
        )
    owner = f"compressed-dialogue:{target.name}"
    relayout = relayout_for_length(layout, target, encoded, owner, canonical)
    validate_relayout(relayout, canonical)
    validate_container_layout(layout.with_decoded(relayout.decoded, relayout.records))

    payload = pack(relayout.decoded)
    # Fail closed before the payload can reach a size decision or a plan. The
    # engine terminates on the stream's own escape and on nothing else, so a
    # payload that merely happens to decode to the declared length is not
    # evidence that retail reads it correctly; it is refused here rather than
    # validated again in every caller.
    try:
        validate_retail_termination(payload)
    except ContainerError as exc:
        raise CompressedDialogueError(
            f"{target.name}: re-encoded dialogue payload does not satisfy the "
            f"retail termination contract: {exc}"
        ) from exc

    next_pointer = int.from_bytes(canonical[table_slot + 4:table_slot + 8], "little")
    if next_pointer < GBA_ROM_BASE:
        raise CompressedDialogueError("following container table entry is not a ROM pointer")
    next_offset = FileOffset(next_pointer - GBA_ROM_BASE).value
    old_allocation = next_offset - old_offset
    if next_offset <= old_offset or container.packed_end > next_offset:
        raise CompressedDialogueError("container table does not bound a valid retail allocation")

    reference_changes = relayout.reference_changes
    if len(payload) <= old_allocation:
        padded = payload + canonical[old_offset + len(payload):old_offset + old_allocation]
        changes = reference_changes + (
            ByteChange(old_offset, canonical[old_offset:old_offset + old_allocation],
                       padded, owner, "rebuild fits measured retail allocation"),
        )
        pointer_address = FileOffset(old_offset).to_gba_address(profile.size).raw
        edit = _dialogue_edit_provenance(
            target, layout, relayout, owner, payload, table_slot, pointer_address, False)
        return CompressedDialogueBuild(
            target, old_offset, old_allocation, payload, None, changes, None,
            dialogue_edit=edit, layout=layout, relayout=relayout,
        )

    expansion = profile.generated_expansion
    request = AllocationRequest(
        AnchorId(owner), owner, len(payload), 4,
        kind=AllocationKind.PACKED_STREAM,
        addressability=Addressability.EXPANDED_PERMITTED,
        evidence="compressed-dialogue selector pointers are engine-proven above "
                 "canonical EOF (ROM-EXPAND-001, LEVEL 4)",
    )
    allocation = allocate(
        profile, [request],
        occupied=tuple(OwnedRegion(span, "build reservation") for span in reserved),
    )[0]
    destination = allocation.range.start.value
    old = (canonical[destination:destination + len(payload)]
           if destination < len(canonical) else bytes([expansion.padding_byte]) * len(payload))
    image_size = expansion.output_size if destination >= profile.size else profile.size
    pointer = FileOffset(destination).to_gba_address(image_size).raw
    changes = reference_changes + (
        ByteChange(destination, old, payload, owner, "relocated compressed dialogue payload"),
        ByteChange(table_slot, canonical[table_slot:table_slot + 4], pointer.to_bytes(4, "little"),
                   owner, "selector container pointer to relocated resource"),
    )
    generated_allocation = None
    if destination >= profile.size:
        generated_allocation = GeneratedAllocationProvenance(
            domain="compressed_dialogue", resource=target.name, owner=owner,
            source_range=RomRange(FileOffset(old_offset), old_allocation),
            allocated_range=allocation.range, allocated_rom_address=pointer,
            pointer_offset=table_slot,
            expansion_evidence=allocation.free_region_evidence,
        )
    edit = _dialogue_edit_provenance(
        target, layout, relayout, owner, payload, table_slot, pointer, True)
    return CompressedDialogueBuild(target, old_offset, old_allocation, payload, allocation,
                                   changes, generated_allocation,
                                   dialogue_edit=edit, layout=layout, relayout=relayout)


def _dialogue_edit_provenance(
    target: CompressedDialogueTarget, layout: DialogueLayout,
    relayout: DialogueRelayout, owner: str, payload: bytes, table_slot: int,
    pointer_address: int, pointer_moved: bool,
) -> DialogueEditProvenance:
    return DialogueEditProvenance(
        resource=target.name,
        owner=owner,
        selector=target.selector,
        old_handle=relayout.edited.raw_handle,
        new_handle=relayout.new_handle.encode(),
        old_decoded_start=relayout.edited.handle.decoded_start,
        new_decoded_start=relayout.new_handle.decoded_start,
        old_decoded_length=relayout.edited.handle.decoded_length,
        new_decoded_length=relayout.new_handle.decoded_length,
        affected_record_count=len(relayout.moved),
        affected_handle_count=len({old.encode() for old, _new in relayout.moved}),
        reference_site_count=len(relayout.reference_changes),
        old_packed_size=layout.packed_size,
        new_packed_size=len(payload),
        container_pointer_offset=table_slot,
        container_pointer_address=pointer_address,
        pointer_moved=pointer_moved,
    )


def materialize_dialogues(canonical: bytes, profile: RomProfile,
                          replacements: dict[str, str], reserved: Iterable[RomRange] = ()) -> tuple[
                              tuple[CompressedDialogueBuild, ...], tuple[RomRange, ...],
                              GeneratedImage | None, tuple[GeneratedAllocationProvenance, ...]]:
    """Plan dialogue as one ordinary build domain against passed reservations."""
    before = tuple(reserved)
    occupied = before
    results = []
    for name, replacement in sorted(replacements.items()):
        result = _prepare_replacement(canonical, profile, target_named(name), replacement, occupied)
        results.append(result)
        if result.allocation is not None:
            occupied += (result.allocation.range,)
    generated = tuple(r.generated_allocation for r in results if r.generated_allocation is not None)
    image = None
    if generated:
        assert profile.generated_expansion is not None
        image = profile.generated_expansion.generated_image(
            profile.size, tuple(item.allocated_range for item in generated)
        )
    return tuple(results), occupied[len(before):], image, generated


def dialogue_edits_for(builds: Iterable[CompressedDialogueBuild]) -> tuple[DialogueEditProvenance, ...]:
    """The manifest provenance for a batch of dialogue edits."""
    return tuple(build.dialogue_edit for build in builds if build.dialogue_edit is not None)


def plan_replacement(canonical: bytes, profile: RomProfile,
                     target: CompressedDialogueTarget, replacement: str) -> CompressedDialogueBuild:
    """Compatibility planner built from the production dialogue domain."""
    results, _, image, generated = materialize_dialogues(canonical, profile, {target.name: replacement})
    result = results[0]
    plan = plan_changes(canonical, result.changes, profile_id=profile.id,
                        base_sha256=profile.sha256, generated_image=image,
                        generated_allocations=generated,
                        dialogue_edits=dialogue_edits_for(results))
    return replace(result, plan=plan)
