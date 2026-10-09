"""The Scripts & Text destination's model: scripts, events, dialogue and strings.

**This module exists to keep two text systems apart, and that is its first job.**

Two systems of text live in this image and they are not interchangeable: editing
one has exactly zero effect on the other.

1. *String tables.* Menu, quest, item, bio and map-name text: a 1,534-entry
   pointer table at file offset ``0x06BCE8`` whose slots point into an 82,874-byte
   pool of UTF-16LE at ``0x05792C``. A string's identity is its TABLE SLOT INDEX
   (``text:0000``..``text:1533``), never its address.
2. *Spoken dialogue.* Seven Webfoot-LZ containers reached through a 7-entry
   container table at file offset ``0x7B5B64``, holding about 390 KB of decoded
   UTF-16LE. A record's identity is the PACKED HANDLE (selector, decoded start,
   decoded length) that a kind-0x05 event-resource record stores at its ``+0x04``.

A full rename of system 1 once left every spoken line untouched, which is the
measured reason a row here names its system, its identity form and its own
storage, and why the two never share a column and never share an identity.

**Nothing here re-implements an SDK codec.** The string table, its entries and
its editing path come from `webfoot.text`; the dialogue containers, their record
inventory and the one authored target come from `webfoot.compressed_dialogue` and
`webfoot.dialogue`; the script families, the event corpus and every relation
between them come from `webfoot.scripts` and `webfoot.placement_events`. This
module adds a *view* of one open image plus the open project, and a *change list*
staged from the SDK's own `set_text`, exactly as `entitysurface` does for
placements.

**Every relation shown is proven, and every one refused is stated.**

* A dialogue record's sites are the ROM words `webfoot.compressed_dialogue`
  proves the engine reads as handles. Measured on the canonical image: 2,993 such
  sites, of which 2,735 lie inside the declared event-resource pool
  ``0x0877C5A4..0x0879B704`` and every one of those lies inside one of the 522
  records that pool's pointer table tiles. The 258 outside it are not event
  resources; they are excluded and counted, never linked.
* A script attachment appears only where the verified descriptor contract decoded
  one. A script corpus that does not round-trip raises rather than degrading,
  which is the SDK's own contract.
* A relation the evidence does not support appears nowhere: no item-to-text edge,
  no shop edge, no dialogue-record-to-string-table edge, and no name invented for
  a handler, a family or a record the evidence does not reach.

No Qt is imported: a test drives every answer with no window open.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.webfoot.binary import GBA_ROM_BASE, FileOffset
from tools.webfoot.compressed_dialogue import (
    AUTHORED_DIALOGUE_TARGETS,
    CompressedDialogueError,
    CompressedDialogueTarget,
    container_selectors,
    dialogue_record_inventory,
)
from tools.webfoot.dialogue import get_dialogue_original, validate_dialogue_replacement
from tools.webfoot.formats.webfoot_lz import ContainerError, unpack
from tools.webfoot.handles import DialogueHandle
from tools.webfoot.layout import RomRange
from tools.webfoot.maps import load_maps
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.profile import RomProfile, RomProfileCatalog
from tools.webfoot.rom import RomIdentification
from tools.webfoot.scripts import ScriptCorpus, load_scripts, script_families
from tools.webfoot.text import TextStrings, load_text_strings
from tools.webfoot.write import ByteChange

#: The four modes this destination carries, in mode order.
SCRIPTS = "scripts"
EVENTS = "events"
DIALOGUE = "dialogue"
STRINGS = "strings"
MODES: tuple[str, ...] = (SCRIPTS, EVENTS, DIALOGUE, STRINGS)

MODE_LABELS = {
    SCRIPTS: "Scripts",
    EVENTS: "Event resources",
    DIALOGUE: "Spoken dialogue",
    STRINGS: "String tables",
}

#: The two text systems' own names, and the one line each carries. A row states
#: which system it belongs to, and the page states it again above the table, so
#: neither can be read as the other even out of context.
STRING_SYSTEM = "string table"
SPOKEN_SYSTEM = "spoken dialogue"

#: Where each system's identity comes from, one sentence per system. The page
#: shows these two lines side by side on the two text modes, and they are the
#: sentence a reader keeps: different tables, different identity, different
#: storage, and an edit of one never reaches the other.
STRING_IDENTITY_LINE = (
    "Identity: pointer-table slot index (text:0000..text:1533), never an address. "
    "Storage: the UTF-16LE pool at 0x05792C through the 1,534-entry pointer table "
    "at 0x06BCE8."
)
SPOKEN_IDENTITY_LINE = (
    "Identity: packed handle (selector, decoded start, decoded length), never the "
    "displayed text. Storage: seven Webfoot-LZ containers reached through the "
    "table at 0x7B5B64."
)

SYSTEM_LINES = {
    STRINGS: (
        "String tables: menu, quest, item, bio and map-name text. A string's "
        "identity is its pointer-table slot, and its storage is the pool at file "
        "offset 0x05792C. This system does not reach spoken dialogue."
    ),
    DIALOGUE: (
        "Spoken dialogue: the seven Webfoot-LZ containers reached through the "
        "container table at file offset 0x7B5B64. A record's identity is the "
        "packed handle an event-resource record stores. This system does not "
        "reach the string tables."
    ),
    SCRIPTS: (
        "Script families and roots, read-only. This build has no event editor and "
        "no authoring verb, so assembly it cannot do is displayed and not offered."
    ),
    EVENTS: (
        "The event resource corpus, read-only: every record the pool's own pointer "
        "table tiles, with the text indices the verified call graph proves a "
        "record renders."
    ),
}

#: Dialog type words the contract's own decoder measured. A type outside this map
#: is shown as its raw byte, because the product does not know what it is.
DIALOG_TYPE_WORDS = {0x4: "dialog record", 0x0: "no dialog record"}


class TextSurfaceError(ValueError):
    """The open image's script, event, dialogue or text records could not be read."""


@dataclass(frozen=True, slots=True)
class ScriptFamilyRow:
    """One script family the profile declares, and the corpus it loads."""

    family: str
    entries: int
    instructions: int
    segments: int


@dataclass(frozen=True, slots=True)
class ScriptRootRow:
    """One script root: a semantic identity, its extent and its provenance.

    ``size`` is the root's span tiled to the next root in the pool's own order,
    which is how the profile's evidence describes that pool ("the roots tile the
    pool exhaustively"). A family the corpus gives explicit segments for carries
    the measured extent instead.
    """

    identity: str
    family: str
    owner: str
    owner_kind: str
    file_offset: int
    size: int
    address: int
    instructions: int
    measured_extent: bool


@dataclass(frozen=True, slots=True)
class EventResourceRow:
    """One record of the event-resource corpus, as the verified contract reads it."""

    identity: str
    index: int
    slot_file_offset: int
    file_offset: int
    size: int
    dialog_file_offset: int
    dialog_type_raw: int
    dialog_type: str
    supported: bool
    code_file_offset: int | None
    code_size: int
    instructions: int
    text_indices: tuple[int, ...]
    note: str


@dataclass(frozen=True, slots=True)
class DialogueRow:
    """One spoken-dialogue record, told apart from a string by every column.

    ``system`` and ``identity_form`` are the two fields that make the distinction
    legible on its own: the storage is a decoded container span, the identity is a
    packed handle, and neither exists in the string-table system.
    """

    system: str
    identity_form: str
    identity: str
    selector: int
    packed_handle: int
    decoded_start: int
    decoded_length: int
    text: str
    sites: tuple[int, ...]
    event_resources: tuple[int, ...]
    sites_outside: int
    editable: bool
    authoring_name: str
    note: str

    @property
    def provenance(self) -> str:
        """Where this row's every field comes from, in one sentence.

        The record's position and extent are the handle's own fields, its text is
        the decoded container span, and its reference sites are the event-resource
        records the SDK's structural query reached.
        """
        if not self.sites:
            return (
                "no event-resource record in this image carries this handle, so "
                "nothing in the image is shown to reference this record"
            )
        where = ", ".join(f"event_resource:{index:04d}" for index in self.event_resources)
        remainder = (
            f"; {self.sites_outside} site(s) outside the declared pool are not "
            "event resources and are not linked"
            if self.sites_outside
            else ""
        )
        return (
            f"{len(self.sites)} handle site(s) at "
            f"{', '.join(f'0x{site:06X}' for site in self.sites)}, reached from {where}"
            f"{remainder}"
        )


@dataclass(frozen=True, slots=True)
class StringRow:
    """One string-table slot, told apart from a dialogue record by every column."""

    system: str
    identity_form: str
    identity: str
    index: int
    text: str
    file_offset: int
    allocation: int
    address: int
    editable: bool
    note: str


@dataclass(frozen=True, slots=True)
class TextSurface:
    """One open image's scripts, event resources, dialogue records and strings."""

    identification: RomIdentification
    profile: RomProfile
    image: bytes
    #: The string table, loaded against this image. None with a stated reason.
    strings: TextStrings | None = None
    strings_problem: str = ""
    #: The event corpus, or None with a stated reason. It validates strictly, so a
    #: canonical descriptor it cannot reach is a refusal rather than an omission.
    events: PlacementEvents | None = None
    events_problem: str = ""
    #: Every script family this profile declares, with the corpus it loads.
    families: tuple[ScriptFamilyRow, ...] = ()
    family_problem: str = ""
    #: One corpus per family, by family name, for the root rows and the summary.
    corpora: dict[str, ScriptCorpus] | None = None
    #: Family name -> the file offset of the family's own declared pool. The
    #: corpus carries `source_offset` for one family only, so the rest take their
    #: extent from the profile's declaration exactly as `webfoot.scripts` does.
    pool_offsets: dict[str, int] = field(default_factory=dict)
    #: The container-table file offset and the selectors whose slots name a
    #: container, measured from this image rather than declared.
    container_table_offset: int = 0
    container_selectors: tuple[int, ...] = ()
    #: The declared event-resource pool, or None when the profile declares no
    #: event contract. A dialogue site outside it is counted and never linked.
    resource_pool: RomRange | None = None
    #: Per-image read caches. The image is immutable for the life of a surface, so
    #: these are computed once: the event corpus costs O(records^2) through
    #: `resource_show`, and a dialogue inventory costs one scan of the whole image
    #: per selector. A page render asks for both on every refresh. They are set
    #: through `object.__setattr__` because the record is frozen and they are
    #: derived state about an immutable image rather than part of its value.
    _event_cache: list | None = None
    _dialogue_cache: list | None = None
    _inventory_cache: dict | None = None
    #: Authored-target anchors, built once: the dialogue reader asks this question
    #: once per record, and 2,805 scans of a one-entry registry is wasted work.
    _target_cache: dict | None = None
    #: Why the dialogue mode holds what it holds: every declared selector whose
    #: container this image could not decode. Set by `dialogue_rows`.
    _dialogue_note: str = ""
    #: The event-resource records, tiled once. `resource_records()` re-tiles the
    #: whole pointer table on every call, and the dialogue reader asks for it once
    #: per record: measured at 2,639 calls and about 8 seconds per render.
    _records_cache: list | None = None

    # -- scripts ---------------------------------------------------------------

    def script_roots(self, family: str) -> tuple[ScriptRootRow, ...]:
        """Every root of one family, with the owner the contract proves for it."""
        corpus = self._corpus(family)
        if corpus is None:
            return ()
        owners: dict[str, tuple[str, str]] = {}
        for attachment in corpus.attachments:
            for event in corpus.ir.entries:
                if event.identity == attachment.event:
                    owners[event.identity] = (attachment.owner, attachment.owner_kind)
        segments = {
            segment.event: segment for segment in corpus.segments
        }
        pool = self.pool_offsets.get(family, corpus.source_offset)
        layout = next(
            (item for item in self.profile.scripts if item.family == family), None
        )
        tiles = _root_tiles(corpus, layout.pool_size if layout is not None else 0)
        # A root's own instructions are the blocks whose extent it begins: `Block`
        # is labelled by extent position (`block:%04d`), and an entry's offset IS
        # the extent position it roots.
        extent = tuple(sorted({entry.offset for entry in corpus.ir.entries}))
        labels = {position: f"block:{at:04d}" for at, position in enumerate(extent)}
        blocks = {block.identity: len(block.instructions) for block in corpus.ir.blocks}
        rows = []
        for entry in corpus.ir.entries:
            segment = segments.get(entry.identity)
            if segment is not None:
                file_offset, size = segment.file_offset, segment.size
                measured = True
            elif pool is not None and entry.identity in tiles:
                file_offset, size = pool + entry.offset, tiles[entry.identity]
                measured = False
            else:
                continue
            owner, kind = owners.get(entry.identity, ("", ""))
            rows.append(
                ScriptRootRow(
                    identity=entry.identity,
                    family=corpus.family,
                    owner=owner,
                    owner_kind=kind,
                    file_offset=file_offset,
                    size=size,
                    address=file_offset + GBA_ROM_BASE,
                    instructions=blocks.get(labels.get(entry.offset, ""), 0),
                    measured_extent=measured,
                )
            )
        return tuple(rows)

    def script_attachments(self, family: str) -> tuple[str, ...]:
        """The descriptors that attach a root of this family, in corpus order."""
        corpus = self._corpus(family)
        if corpus is None:
            return ()
        return tuple(attachment.owner for attachment in corpus.attachments)

    def _corpus(self, family: str) -> ScriptCorpus | None:
        if self.corpora is None:
            return None
        return self.corpora.get(family)

    # -- event resources -------------------------------------------------------

    def event_rows(self) -> tuple[EventResourceRow, ...]:
        """Every event-resource record, with the text indices it provenly renders.

        `dialog_text_references` is the one proven dialog-to-text edge: a slot
        whose call graph reaches the verified text pointer table. It is empty for
        a dialog whose index is computed at runtime, and that emptiness is the
        honest answer rather than a missing row.
        """
        if self.events is None:
            return ()
        if self._event_cache is not None:
            return tuple(self._event_cache)
        by_index: dict[int, list[int]] = {}
        for reference in self.events.dialog_text_references():
            by_index.setdefault(int(reference.dialog), []).append(int(reference.index))
        records = self.events.resource_records()
        rows = []
        for record in records:
            view = self.events.resource_show(record.index)
            indices = tuple(sorted(set(by_index.get(record.index, ()))))
            rows.append(
                EventResourceRow(
                    identity=view["identity"],
                    index=record.index,
                    slot_file_offset=view["slot_file_offset"],
                    file_offset=view["record_file_offset"],
                    size=view["record_size"],
                    dialog_file_offset=view["dialog_file_offset"],
                    dialog_type_raw=view["dialog_type"],
                    dialog_type=DIALOG_TYPE_WORDS.get(
                        view["dialog_type"], f"0x{view['dialog_type']:02X}"
                    ),
                    supported=bool(view["supported"]),
                    code_file_offset=view.get("code_file_offset"),
                    code_size=view.get("code_size", 0),
                    instructions=view.get("instructions", 0),
                    text_indices=indices,
                    note=(
                        "this record's call graph reaches the verified text table, so "
                        "these indices are the strings it renders"
                        if indices
                        else "no text index is proven for this record: its dialog "
                        "index is computed at runtime, or its slot does not reach the "
                        "text table"
                    ),
                )
            )
        object.__setattr__(self, "_event_cache", rows)
        return tuple(rows)

    # -- dialogue --------------------------------------------------------------

    def dialogue_rows(self) -> tuple[DialogueRow, ...]:
        """Every spoken-dialogue record this image's containers hold.

        One row per packed handle, ordered by selector then decoded start. A
        record is editable only when the SDK publishes it as an authored target,
        which is a registry of exactly one entry today; every other record states
        the SDK's own refusal sentence rather than a promise.

        A container the image cannot decode is STATED, not skipped: `dialogue_note`
        carries that reason, so a mode with no rows says why it has none rather
        than reading as a corpus that holds nothing.
        """
        rows: list[DialogueRow] = []
        if self._dialogue_cache is not None:
            return tuple(self._dialogue_cache)
        if self._inventory_cache is None:
            object.__setattr__(self, "_inventory_cache", {})
        problems: list[str] = []
        for selector in self.container_selectors:
            decoded, _record_count = self._container(selector)
            if decoded is None:
                problems.append(
                    f"selector {selector} names no container this build can decode"
                )
                continue
            inventory = self._inventory_cache.get(selector)
            if inventory is None:
                inventory = dialogue_record_inventory(
                    self.image, selector, len(decoded)
                )
                self._inventory_cache[selector] = inventory
            for record in inventory:
                handle = record.handle
                sites = tuple(record.sites)
                inside, outside = self._sites(sites)
                target = self._target_for(selector, handle)
                event_resources = self._resources_of(inside)
                span = decoded[handle.decoded_start:handle.decoded_end]
                try:
                    text = span.decode("utf-16le")
                    text_read = ""
                except UnicodeDecodeError:
                    text = ""
                    text_read = "this record is not valid UTF-16LE"
                editable = target is not None
                authoring_name = target.name if target is not None else ""
                if editable:
                    note = ""
                elif text_read:
                    note = text_read
                else:
                    note = "no authored target is registered for this record"
                rows.append(
                    DialogueRow(
                        system=SPOKEN_SYSTEM,
                        identity_form="packed handle",
                        identity=f"dialogue:0x{handle.encode():08X}",
                        selector=selector,
                        packed_handle=handle.encode(),
                        decoded_start=handle.decoded_start,
                        decoded_length=handle.decoded_length,
                        text=text,
                        sites=inside,
                        event_resources=event_resources,
                        sites_outside=outside,
                        editable=editable,
                        authoring_name=authoring_name,
                        note=note,
                    )
                )
        object.__setattr__(self, "_dialogue_cache", rows)
        object.__setattr__(
            self,
            "_dialogue_note",
            "; ".join(dict.fromkeys(problems)),
        )
        return tuple(rows)

    @property
    def dialogue_note(self) -> str:
        """Why this image's dialogue mode holds what it holds, or an empty string.

        Empty when every declared selector decoded. A container that did not is
        named here, because a mode with no rows and no reason reads as an image
        with no spoken dialogue.
        """
        return self._dialogue_note

    def authored_dialogue(self) -> tuple[CompressedDialogueTarget, ...]:
        """Every record this build can replace, from the SDK's own registry."""
        return tuple(
            target
            for target in AUTHORED_DIALOGUE_TARGETS.values()
            if target.profile_id is None or target.profile_id == self.profile.id
        )

    def dialogue_text(self, target: CompressedDialogueTarget) -> str:
        """The text one authored target's current handle names in this image."""
        return get_dialogue_original(self.image, self.profile, target)

    def dialogue_problem(self, target: CompressedDialogueTarget, text: str) -> str:
        """Why this replacement would be refused, or an empty string.

        The SDK's own validation, including the production re-layout planned and
        discarded, so a replacement this container cannot hold is refused here
        rather than at the build.
        """
        validation = validate_dialogue_replacement(
            target, text, self.profile, self.image
        )
        if validation.valid:
            return ""
        return "; ".join(problem.message for problem in validation.problems)

    # -- strings ---------------------------------------------------------------

    def string_rows(self) -> tuple[StringRow, ...]:
        """Every string-table slot, in table order, with its own system and identity."""
        if self.strings is None:
            return ()
        rows = []
        for entry in self.strings.entries():
            rows.append(
                StringRow(
                    system=STRING_SYSTEM,
                    identity_form="pointer-table slot",
                    identity=str(entry.identity),
                    index=entry.identity.index,
                    text=entry.text,
                    file_offset=entry.location.file_offset,
                    allocation=entry.location.allocation,
                    address=entry.location.file_offset + GBA_ROM_BASE,
                    editable=True,
                    note="",
                )
            )
        return tuple(rows)

    def plan(
        self, identity: Any, text: str
    ) -> tuple[str, tuple[ByteChange, ...], tuple[RomRange, ...]]:
        """One string edit staged through the SDK: refusal, changes, claimed spans.

        The three answers a single edit needs, from ONE staging, because they must
        agree. The SDK's own `set_text` runs against a clone of the loaded table,
        so the refusal is the production one - the exact deficit, or the reason
        this profile or this entry cannot relocate.

        The claimed spans are read off the changes themselves rather than computed
        from the record's canonical position, and that is the difference that
        matters when the edit RELOCATES: a longer replacement needs no space at
        its old address at all, it writes the body at the span the allocator chose
        and rewrites this entry's pointer-table slot to name it. Claiming the old
        address there would mark bytes in the ROM surface that this edit never
        touches, and would leave the bytes that really change outside the raw
        write's collision guard. Each change contributes the bytes it actually
        differs in, which is the whole of what one edit rewrites.
        """
        if self.strings is None:
            return (
                self.strings_problem or "no string table is loaded",
                (),
                (),
            )
        clone = _clone_strings(self.strings)
        try:
            clone.set_text(identity, text)
        except (ValueError, OSError) as exc:
            return (str(exc), (), ())
        owner = str(identity)
        changes = tuple(
            change
            for change in clone.changes()
            if change.owner == owner and change.old != change.new
        )
        claimed = tuple(
            RomRange(FileOffset(change.offset), len(change.new)) for change in changes
        )
        return ("", changes, claimed)

    # -- planning --------------------------------------------------------------

    def changes(self, project: Any | None) -> tuple[ByteChange, ...]:
        """Every pending string edit, as the SDK's own owner-bearing changes.

        Staged on a clone of the loaded table through the same `set_text` the
        build calls, and filtered to the slots that actually differ, so the owner
        is the SDK's own `text:NNNN` and nothing here mints an identity.
        """
        if project is None or self.strings is None or not project.strings:
            return ()
        clone = _clone_strings(self.strings)
        touched: set[str] = set()
        for identity, text in project.strings.items():
            if self.strings.entry(identity).text == text:
                continue
            try:
                clone.set_text(identity, text)
            except (ValueError, OSError):
                # The page states this refusal where a person made it; a change
                # list is not a second place to report it.
                continue
            touched.add(str(identity))
        if not touched:
            return ()
        return tuple(
            change
            for change in clone.changes()
            if change.owner in touched and change.old != change.new
        )

    def pending_bytes(self, project: Any | None) -> dict[int, bytes]:
        """The byte effect of every pending string edit, keyed by file offset."""
        return {change.offset: change.new for change in self.changes(project)}

    # -- the internals ---------------------------------------------------------

    def _container(self, selector: int) -> tuple[bytes | None, int]:
        slot = self.container_table_offset + selector * 4
        if slot + 4 > len(self.image):
            return None, 0
        word = int.from_bytes(self.image[slot:slot + 4], "little")
        if word < GBA_ROM_BASE or word - GBA_ROM_BASE >= len(self.image):
            return None, 0
        try:
            container = unpack(self.image, word - GBA_ROM_BASE)
        except ContainerError:
            return None, 0
        return container.data, len(container.data)

    def _sites(self, sites: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
        """Split a record's reference sites into the pool's and the rest.

        The pool is the profile's own declared event contract. A site outside it
        is not an event resource, so it is counted and never linked: the SDK's
        structural query finds it, and the evidence does not make it a
        reference. Measured on the canonical image: 2,735 of 2,993 sites are
        inside the pool, and every one of those lies inside a resource record.
        """
        if self.resource_pool is None:
            return sites, 0
        low = self.resource_pool.start.value
        high = self.resource_pool.end
        inside = tuple(site for site in sites if low <= site < high)
        return inside, len(sites) - len(inside)

    def _resources_of(self, sites: tuple[int, ...]) -> tuple[int, ...]:
        """Every event-resource record index one site lies inside.

        One bisect per site, not a scan of the 522-record table, because this runs
        for every one of the 2,805 dialogue records on every render.
        """
        if self.events is None or not sites:
            return ()
        if self._records_cache is None:
            records = list(self.events.resource_records())
            object.__setattr__(
                self,
                "_records_cache",
                ([record.start for record in records], records),
            )
        starts, records = self._records_cache
        found = set()
        for site in sites:
            at = bisect_right(starts, site) - 1
            if at >= 0 and records[at].start <= site < records[at].end:
                found.add(records[at].index)
        return tuple(sorted(found))

    def _target_for(self, selector: int, handle: DialogueHandle):
        """The authored target whose anchor is this record, or None.

        The anchor is ``(selector, decoded start)``, which the authoring
        operation never moves: the replacement is spliced at the record's own
        end, so the start survives an edit that re-authored its length.
        """
        if self._target_cache is None:
            object.__setattr__(
                self,
                "_target_cache",
                {
                    (target.selector, target.decoded_start): target
                    for target in self.authored_dialogue()
                },
            )
        return self._target_cache.get((selector, handle.decoded_start))

def _root_tiles(corpus: ScriptCorpus, pool_size: int) -> dict[str, int]:
    """Each root's span tiled to the next, for a family whose corpus has no segments."""
    entries = sorted(corpus.ir.entries, key=lambda entry: entry.offset)
    tiles: dict[str, int] = {}
    for position, entry in enumerate(entries):
        if position + 1 < len(entries):
            tiles[entry.identity] = entries[position + 1].offset - entry.offset
        else:
            tiles[entry.identity] = max(0, pool_size - entry.offset)
    return tiles


def _clone_strings(strings: TextStrings) -> TextStrings:
    """The same loaded table with its edit state copied, base bytes and all.

    The SDK exposes no public clone, and a second load would re-read and
    re-enumerate 1,534 entries per keystroke. The copy is the object's own
    documented state, so a staged edit cannot reach the surface's own table.
    """
    clone = TextStrings.__new__(TextStrings)
    clone.__dict__.update(strings.__dict__)
    clone._entries = dict(strings._entries)
    clone._edited = set(strings._edited)
    clone._relocating = dict(strings._relocating)
    return clone


def dialogue_span(row: DialogueRow) -> RomRange:
    """The byte extent one dialogue edit rewrites, as the ROM surface's own unit.

    A dialogue edit rewrites a decoded container, not a byte range of the file,
    so the honest extent is the record's CONTRIBUTING ROM WORDS: the handle field
    of every event-resource record that names it. Those are the bytes a manifest
    can name, and a row with no proven site has no extent to offer.
    """
    if not row.sites:
        raise TextSurfaceError(
            f"{row.identity} has no proven event-resource site, so no byte extent "
            "of this edit is established"
        )
    low = min(row.sites)
    high = max(row.sites) + 4
    return RomRange(FileOffset(low), high - low)


def load_text_surface(
    rom_path: str | Path,
    catalog: RomProfileCatalog,
    identification: RomIdentification,
    profile: RomProfile,
    image: bytes,
) -> TextSurface:
    """Read one already-identified image's scripts, events, dialogue and strings.

    Each family is loaded through the module that owns it, and a family that
    refuses states its reason on the surface rather than failing the destination:
    an image whose descriptor contract is absent still shows its strings.
    """
    from tools.webfoot.data.placement_contracts import CONTRACTS

    strings: TextStrings | None = None
    strings_problem = ""
    try:
        strings = load_text_strings(rom_path, catalog)
    except (ValueError, OSError) as exc:
        strings_problem = str(exc)

    events: PlacementEvents | None = None
    events_problem = ""
    try:
        events = PlacementEvents(load_maps(rom_path, catalog))
    except (ValueError, OSError) as exc:
        events_problem = str(exc)

    families: list[ScriptFamilyRow] = []
    corpora: dict[str, ScriptCorpus] = {}
    pool_offsets: dict[str, int] = {}
    family_problem = ""
    try:
        names = script_families(rom_path, catalog)
    except (ValueError, OSError) as exc:
        names = ()
        family_problem = str(exc)
    for layout in profile.scripts:
        pool_offsets[layout.family] = layout.pool_address.to_file_offset(len(image))
    for family in names:
        try:
            corpus = load_scripts(rom_path, catalog, family)
        except (ValueError, OSError) as exc:
            family_problem = family_problem or str(exc)
            continue
        corpora[family] = corpus
        families.append(
            ScriptFamilyRow(
                family=family,
                entries=len(corpus.ir.entries),
                instructions=corpus.instruction_count,
                segments=len(corpus.segments),
            )
        )

    table_offset = 0
    selectors: tuple[int, ...] = ()
    authored = tuple(AUTHORED_DIALOGUE_TARGETS.values())
    if authored:
        # The container table's address is the authored registry's own measured
        # fact, so it is read from there rather than restated as a literal.
        table_offset = authored[0].table_offset
        selectors = container_selectors(image, table_offset)
    pool: RomRange | None = None
    contract = CONTRACTS.get(profile.id)
    if contract is not None:
        resource = contract["event_resource"]
        # The pool is bounded by its own pointer table, which is the extent the
        # contract declares: `pool_start` and the table address.
        start = resource["pool_start"] - GBA_ROM_BASE
        pool = RomRange(FileOffset(start), resource["table"] - resource["pool_start"])

    return TextSurface(
        identification=identification,
        profile=profile,
        image=image,
        strings=strings,
        strings_problem=strings_problem,
        events=events,
        events_problem=events_problem,
        families=tuple(families),
        family_problem=family_problem,
        corpora=corpora,
        pool_offsets=pool_offsets,
        container_table_offset=table_offset,
        container_selectors=selectors,
        resource_pool=pool,
    )


def family_summary(rows: tuple[ScriptFamilyRow, ...]) -> str:
    """The one line the family list states about itself."""
    return (
        f"Script families: {len(rows)} declared, "
        f"{sum(row.entries for row in rows)} root(s)"
    )


def dialogue_summary(rows: tuple[DialogueRow, ...]) -> str:
    """The one line the dialogue list states about itself."""
    editable = sum(1 for row in rows if row.editable)
    return (
        f"Spoken dialogue records: {len(rows)}, {editable} with an authored "
        "target; no string-table row appears in this mode"
    )


def string_summary(rows: tuple[StringRow, ...]) -> str:
    """The one line the string list states about itself."""
    return (
        f"String-table slots: {len(rows)}; no spoken-dialogue record appears in "
        "this mode"
    )


def event_summary(rows: tuple[EventResourceRow, ...]) -> str:
    """The one line the event list states about itself."""
    return (
        f"Event resources: {len(rows)} record(s), "
        f"{sum(len(row.text_indices) for row in rows)} proven text reference(s)"
    )


__all__ = [
    "DIALOGUE",
    "EVENTS",
    "MODE_LABELS",
    "MODES",
    "SCRIPTS",
    "SPOKEN_SYSTEM",
    "STRINGS",
    "STRING_SYSTEM",
    "SYSTEM_LINES",
    "DialogueRow",
    "EventResourceRow",
    "ScriptFamilyRow",
    "ScriptRootRow",
    "StringRow",
    "TextSurface",
    "TextSurfaceError",
    "dialogue_span",
    "dialogue_summary",
    "event_summary",
    "family_summary",
    "load_text_surface",
    "string_summary",
]
