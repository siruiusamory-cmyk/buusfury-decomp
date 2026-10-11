"""One open image, one edit list, one plan, and the state of every row.

No Qt is imported, so a test drives every answer with no window open. Every ROM
semantic comes from `tools.webfoot.textedit`; this module decides only which rows
exist, which edits are pending, what a row's state is, and what the meters show.

THE DIALOGUE LIST HAS THREE SHAPES OVER ONE IMAGE.

- `LINES`, the default: one row per SPOKEN LINE, derived by the engine from the
  stored runs between explicit breaks, so a long covering record no longer shows
  up as one row containing half the script.
- `RECORDS`: one row per handle, which is what the engine actually reads and
  writes. Kept for power use.
- `SLOT`: one row per string-table slot, the second list, never merged with the
  first.

An edit is always a RECORD edit, because a record is what the engine reads and
writes. A row names the record it edits (`Line.target`) and the span inside it, so
editing one line of a record rewrites that line and leaves the record's other lines
alone.

The edit list is the project: `RecordEdit` and `SlotEdit` carry the LOADED text as
their guard, so an edit made against one image refuses against another.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from tools.webfoot import textedit

from .project import Project

#: The two lists the window shows. They never mix: a string slot and a dialogue
#: record are different identities in different tables.
SLOT = "slot"
RECORD = "record"

#: The shape of the dialogue list.
LINES = "lines"
RECORDS = "records"

#: The order the dialogue list is shown in. APPEARANCE is the owner's choice: the
#: first handle site, which is where the game's own script data names the line.
#: STORAGE is the image's own layout, which needs no assumption at all.
APPEARANCE = "appearance"
STORAGE = "storage"

#: What the dialogue list is grouped by. PLACE exists so the window can say that
#: no proven map or chapter link exists instead of inventing one.
UNGROUPED = "none"
BY_SPEAKER = "speaker"
BY_PLACE = "place"

#: What a row says when nothing attributes its speaker. The engine returns None
#: there; this word belongs to the surface, never to the engine.
UNKNOWN_SPEAKER = "Unknown speaker"

#: What a row says about the face the record DRAWS, one word per kind the engine
#: reports. The game never maps an operand to a character, so these are the four
#: honest gaps: no portrait at all, a face that depends on the player's save, a
#: portrait with no owning appearance record, and two sites that disagree.
PORTRAIT_WORDS: dict[str, str] = {
    textedit.NO_PORTRAIT: "No portrait",
    textedit.PARTY_PORTRAIT: "Party member (depends on save)",
    textedit.UNKNOWN_PORTRAIT: "Unknown portrait",
    textedit.AMBIGUOUS_PORTRAIT: UNKNOWN_SPEAKER,
}

#: The group a line falls in when no proven map or chapter link reaches it.
UNPLACED = "Unplaced"

#: What the place grouping rests on. It is an INFERENCE: the placement route links
#: a map to the event resources its placements name, and no runtime observation yet
#: shows that handler reading their dialogue. A surface that groups by place must
#: state the coverage, because most lines have no map.
PLACE_EVIDENCE = "the placement route, inferred rather than proven at runtime"


class State(Enum):
    """A row's primary state. The word and the glyph belong to the theme."""

    UNCHANGED = "unchanged"
    EDITED = "edited"
    WILL_MOVE = "will move"
    REFUSED = "refused"
    BASE_CHANGED = "base changed"


@dataclass(frozen=True, slots=True)
class Pending:
    """One replacement this session holds for part of a target's text.

    `offset` and `length` are positions in the ORIGINAL canonical text, never in the
    composed one, which is what lets two entries compose: the composed text is rebuilt
    from the original every time. `key` is the row an entry came from, and empty for the
    spans a rename batch contributes, which no row owns.
    """

    key: str
    offset: int
    length: int
    text: str

    @property
    def end(self) -> int:
        return self.offset + self.length

    @property
    def delta(self) -> int:
        """How much this entry changes the text's length."""
        return len(self.text) - self.length


@dataclass(frozen=True, slots=True)
class Line:
    """One row: a spoken line, a whole record, or a string slot."""

    key: str
    kind: str
    view: str
    text: str
    retail: str | None
    #: The record this row edits. Empty for a slot, which is its own target.
    target: str = ""
    #: Whether a proven handle site names the target, so an edit can rely on it.
    proven: bool = True
    speaker: str | None = None
    #: The kind word for a face that resolves to nobody: "No portrait", a
    #: save-dependent party face, an unknown portrait, or two sites that disagree.
    #: Empty when a name takes its place.
    portrait: str = ""
    #: The records that contain this row: the carriers of a spoken line, or the
    #: longer records covering a whole record.
    covering: tuple[str, ...] = ()
    sites: int = 0
    #: The map the placement route reaches, as a label, or empty when nothing
    #: places this row. `place_index` is the map table's own row, so a grouping can
    #: order by the table rather than by a name.
    place: str = ""
    place_index: int = -1
    position: tuple[int, int] = (0, 0)
    first_site: int = -1

    @property
    def shows_retail(self) -> bool:
        """Whether the canonical reference is loaded, so 'differs' can be answered."""
        return self.retail is not None

    @property
    def speaker_label(self) -> str:
        """The name when one resolves, else the kind of gap. Never a guess."""
        return self.speaker or self.portrait or UNKNOWN_SPEAKER


@dataclass(frozen=True, slots=True)
class Meter:
    """The NEW text against the span the engine will let it use, in both units."""

    chars: int
    chars_limit: int | None
    bytes: int
    bytes_limit: int | None


@dataclass(frozen=True, slots=True)
class Group:
    """One heading in the dialogue list, and the rows under it."""

    label: str
    rows: tuple[Line, ...]


@dataclass(frozen=True, slots=True)
class Hit:
    """One occurrence a rename would decide, for the per-occurrence dialog."""

    key: str
    snippet: str
    retail: str
    decision: str
    at: int


class Session:
    """The window's model. Everything it answers is derivable without a window."""

    def __init__(self, model: textedit.Model, project: Project | None = None,
                 base_changed: bool = False, view: str = LINES,
                 order: str = APPEARANCE, cutters_from_pool: bool = True) -> None:
        self.model = model
        self.view = view
        self.order = order
        self.cutters_from_pool = cutters_from_pool
        #: Edits are keyed by the RECORD they change, which is what the engine
        #: reads and writes, however many rows that record is shown as.
        self.edits: dict[str, object] = {}
        self.unmatched: tuple[str, ...] = ()
        self.base_changed = base_changed
        self._plan: textedit.Plan | None = None
        self._by_record: dict[str, textedit.Decision] = {}
        self._stale = True
        # The portrait join and the map join are read once, before the rows,
        # because every row's speaker and place come from them.
        self.portraits = textedit.portraits(model)
        self.speakers = textedit.speakers(model)
        self.map_labels = {row.index: row.label for row in textedit.maps(model)}
        self.record_places = textedit.record_maps(model)
        self.places = textedit.line_maps(model, cutters_from_pool=cutters_from_pool)
        self._edited_row: dict[str, str] = {}
        self._rows: dict[str, dict[str, Line]] = self._read_rows()
        #: target -> the spans this session holds for it, each a replacement of part of
        #: the ORIGINAL text. One entry per edited row, plus one per span a rename batch
        #: contributes. That is what lets two edits of one target compose instead of the
        #: second replacing the first, and what removes the need to locate any entry by
        #: searching for its text.
        self._pending: dict[str, tuple[Pending, ...]] = {}
        self._lines_by_target: dict[str, tuple[Line, ...]] = self._index_lines()
        if project is not None:
            self.adopt(project)
        self._resort()

    # --- reading the image ---------------------------------------------------

    def _record_retail(self, record: textedit.Record) -> str | None:
        stream = self.model.retail_streams.get(record.selector)
        if stream is None or record.start + record.length > len(stream):
            return None
        return stream[record.start:record.start + record.length].decode("utf-16le", "replace")

    def _read_rows(self) -> dict[str, dict[str, Line]]:
        slots = {slot.key: Line(key=slot.key, kind=SLOT, view=SLOT, text=slot.text,
                                retail=slot.retail, target="", sites=1,
                                position=(0, slot.index))
                 for slot in self.model.slots}
        records: dict[str, Line] = {}
        spoken: dict[str, Line] = {}
        for record in self.model.records:
            retail = self._record_retail(record)
            position = (record.selector, record.start)
            first = min(record.sites) if record.sites else -1
            portrait = self.portraits.get(record.key)
            place_index = self.record_places.get(record.key, -1)
            records[record.key] = Line(
                key=record.key, kind=RECORD, view=RECORDS, text=record.text, retail=retail,
                target=record.key, proven=True,
                speaker=None if portrait is None else portrait.resolved,
                portrait="" if portrait is None else PORTRAIT_WORDS.get(portrait.kind, ""),
                covering=record.covering, sites=len(record.sites),
                place=self.map_labels.get(place_index, ""), place_index=place_index,
                position=position, first_site=first)
        for row in textedit.lines(self.model, cutters_from_pool=self.cutters_from_pool):
            target = row.target
            holder = records.get(target)
            offset = (row.start - holder.position[1]) // 2 if holder is not None else 0
            length = row.length // 2
            speaker, portrait_word = self._line_evidence(row.records)
            place_index = self.places.get(row.key, -1)
            spoken[row.key] = Line(
                key=row.key, kind=RECORD, view=LINES, text=row.text,
                retail=None if holder is None or holder.retail is None
                else holder.retail[offset:offset + length],
                target=target, proven=row.target_is_proven,
                speaker=speaker, portrait=portrait_word,
                covering=row.records, sites=len(row.sites),
                place=self.map_labels.get(place_index, ""), place_index=place_index,
                position=(row.selector, row.start),
                first_site=min(row.sites) if row.sites else -1)
        return {SLOT: slots, RECORDS: records, LINES: spoken}

    def _line_evidence(self, carriers: tuple[str, ...]) -> tuple[str | None, str]:
        """The one name, or the one kind, that every carrier agrees on.

        A line carried by records that resolve to two names, or to a name and a
        party face, is genuinely drawn more than one way, so it is given no
        attribution rather than one of them.
        """
        held = [self.portraits[key] for key in carriers if key in self.portraits]
        names = {item.resolved for item in held if item.resolved}
        if len(names) == 1:
            return next(iter(names)), ""
        if len(names) > 1:
            return None, ""
        words = {PORTRAIT_WORDS.get(item.kind, "") for item in held}
        words.discard("")
        if len(words) == 1:
            return None, next(iter(words))
        return None, ""

    def _resort(self) -> None:
        """Order the current view. Ties break on the row's own length, never on
        dictionary order, so the list cannot depend on how the rows were built."""
        rows = self._rows.get(self.view, {})
        if self.order == STORAGE:
            ordered = sorted(rows.values(), key=lambda row: (row.kind != SLOT, row.position,
                                                             len(row.text)))
        else:
            # A row no site names sorts after every row a site does, rather than
            # being given a position the evidence does not support.
            ordered = sorted(rows.values(), key=lambda row: (row.kind != SLOT,
                                                             row.first_site if row.first_site >= 0
                                                             else 1 << 62,
                                                             row.position, len(row.text)))
        self.lines = tuple(ordered)
        self._index = {row.key: row for row in self.lines}

    def line(self, key: str) -> Line | None:
        """The row for `key`, whichever list or dialogue view holds it."""
        row = self._index.get(key)
        if row is not None:
            return row
        if key in self._rows[SLOT]:
            return self._rows[SLOT][key]
        other = RECORDS if self.view == LINES else LINES
        return self._rows[other].get(key)

    def rows_of(self, kind: str | None) -> tuple[Line, ...]:
        """The rows one system list shows: the slot table, or the dialogue view."""
        if kind == SLOT:
            return tuple(self._rows[SLOT].values())
        return self.lines

    def set_view(self, view: str) -> None:
        if view not in (LINES, RECORDS):
            raise ValueError(f"{view!r} is not a dialogue view")
        self.view = view
        self._resort()

    def set_order(self, order: str) -> None:
        if order not in (APPEARANCE, STORAGE):
            raise ValueError(f"{order!r} is not an order")
        self.order = order
        self._resort()

    def keys(self, kind: str) -> tuple[str, ...]:
        return tuple(row.key for row in self.rows_of(kind))

    def total(self, kind: str) -> int:
        return len(self.rows_of(kind))

    def view_size(self, view: str) -> int:
        return len(self._rows.get(view, {}))

    # --- the edit list -------------------------------------------------------

    def adopt(self, project: Project) -> None:
        """Take a saved edit list. An edit whose guard misses is kept, not rebased.

        Each edit is ALSO seeded into the span store, from the common prefix and suffix of
        the two texts it names, because the store is what the next edit composes onto and
        what an undo restores. Measured without it: a saved edit lived only in `edits`, so
        the next edit of that record in this session composed from the original text and
        silently discarded the saved change, and undoing that edit erased it outright.
        Rename and Clear on such a record did the same.
        """
        edits: dict[str, object] = {}
        seeded: dict[str, tuple[Pending, ...]] = {}
        unmatched: list[str] = []
        for edit in project.edits:
            key = _key_of(edit)
            if self._rows[RECORDS].get(key) is None and self._rows[SLOT].get(key) is None:
                unmatched.append(key)
            edits[key] = edit
            span = _span_between(_old_of(edit), _new_of(edit))
            if span is not None:
                seeded[key] = (Pending(key, *span),)
        self.edits = edits
        self._pending = seeded
        self.unmatched = tuple(unmatched)
        self._stale = True

    def _record_of(self, row: Line) -> textedit.Record | None:
        return self.model.record(*_parts(row.target)) if row.target else None

    def _index_lines(self) -> dict[str, tuple[Line, ...]]:
        """Every spoken line, grouped by the record an edit of it would address."""
        grouped: dict[str, list[Line]] = {}
        for row in self._rows[LINES].values():
            grouped.setdefault(row.target or row.key, []).append(row)
        return {target: tuple(rows) for target, rows in grouped.items()}

    def _rows_for(self, target: str) -> tuple[Line, ...]:
        """Every row of one record, in the record's own order."""
        return self._lines_by_target.get(target, ())

    def _span(self, row: Line) -> tuple[int, int]:
        """The row's character offset and length inside its target record."""
        holder = self._record_of(row)
        if holder is None or row.view != LINES:
            return 0, len(row.text)
        return (row.position[1] - holder.start) // 2, len(row.text)

    def _shift(self, target: str, offset: int) -> int:
        """How far an ORIGINAL offset moves once every entry before it applies."""
        return sum(entry.delta for entry in self._entries(target) if entry.end <= offset)

    def _entries(self, target: str) -> tuple[Pending, ...]:
        return self._pending.get(target, ())

    def _text_of(self, target: str) -> str | None:
        """The target's own text before any edit, or None when nothing carries it."""
        holder = self._rows[RECORDS].get(target)
        if holder is not None:
            return holder.text
        slot = self._rows[SLOT].get(target)
        return None if slot is None else slot.text

    def _compose_with(self, target: str, entries: tuple[Pending, ...]) -> str | None:
        """The target's text with `entries` applied, rebuilt from the original."""
        base = self._text_of(target)
        if base is None:
            return None
        if not entries:
            return base
        pieces: list[str] = []
        cursor = 0
        for entry in entries:
            pieces.append(base[cursor:entry.offset])
            pieces.append(entry.text)
            cursor = entry.end
        pieces.append(base[cursor:])
        return "".join(pieces)

    def _compose(self, target: str) -> str | None:
        """The target's pending text, from the entries this session holds for it.

        Every entry is a span of the ORIGINAL text, so the composed text is rebuilt from
        the original each time and two entries compose by construction: an entry that
        grows shifts every later one without any entry being rewritten, and no entry is
        ever found by searching for its text. Measured, two earlier shapes each failed
        here. The first built every edit from the original record and overwrote the
        stored one, so two lines of one record kept only the second. The second stored a
        renamed record as one whole new text and re-applied line entries by searching
        that text for the line's own old text, so a rename plus a line edit could not be
        combined at all, and two renames of one record kept only the second.
        """
        return self._compose_with(target, self._entries(target))

    @staticmethod
    def _place_in(entries: tuple[Pending, ...],
                  entry: Pending) -> tuple[Pending, ...] | None:
        """`entries` with `entry` placed, or None when it straddles one of them.

        An entry wholly inside the new one is superseded, because the new span's text IS
        the reader's own answer for that text, and an entry with the identical span is
        replaced. A PARTIAL overlap is the one case with no honest answer: two edits
        claim overlapping text and neither contains the other, so the caller refuses
        rather than guessing which text belongs where.
        """
        kept: list[Pending] = []
        for existing in entries:
            if entry.offset <= existing.offset and existing.end <= entry.end:
                continue
            if existing.offset < entry.end and entry.offset < existing.end:
                return None
            kept.append(existing)
        kept.append(entry)
        return tuple(sorted(kept, key=lambda item: item.offset))

    def _commit(self, target: str, entries: tuple[Pending, ...]) -> None:
        """Store the entries and rebuild the target's edit, once, after composing.

        The composed text is built BEFORE anything is written, so a combination that
        cannot be composed leaves the session exactly as it was.
        """
        text = self._compose_with(target, entries)
        base = self._text_of(target)
        holder = self._rows[RECORDS].get(target)
        slot = self._rows[SLOT].get(target)
        edit: object | None = None
        if text is not None and base is not None and text != base:
            # A set of entries that composes back to the original text is no edit at all,
            # which is what makes clearing the last entry clear the row's state with it.
            if holder is None and slot is not None:
                edit = textedit.SlotEdit(slot=slot.position[1], old=slot.text, new=text)
            elif holder is not None:
                record = self._record_of(holder)
                if record is not None:
                    edit = textedit.RecordEdit(record.selector, record.start, record.length,
                                               old=holder.text, new=text)
        if entries:
            self._pending[target] = entries
        else:
            self._pending.pop(target, None)
        if edit is None:
            self.edits.pop(target, None)
        else:
            self.edits[target] = edit
        self._stale = True

    def set_edit(self, key: str, new: str) -> None:
        """Record what one row should say, clearing that row's edit when it says it.

        Check then commit: the new entry list and the composed text are built before
        anything is written, so a combination with no honest answer leaves this session
        exactly as it was. That is what stops a refused edit from wedging a record.

        A row's span comes from the row, so an edit made in the Records shape is a span
        over the whole record and supersedes the line entries inside it, which is
        correct: the reader typed that text, and it already contains them.
        """
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        if not row.text:
            raise textedit.TextEditError(
                f"{key} is empty, so there is nothing for an edit to name as the text it "
                "replaces")
        target = row.target or key
        entries = self._entries(target)
        if new == row.text:
            if row.key == target:
                # The target's own row: what it now says is the whole of what it says.
                remaining: tuple[Pending, ...] = ()
            else:
                remaining = tuple(entry for entry in entries if entry.key != row.key)
            if remaining != entries:
                self._commit(target, remaining)
            return
        offset, length = self._span(row)
        placed = self._place_in(entries, Pending(row.key, offset, length, new))
        if placed is None:
            raise textedit.TextEditError(
                f"{key} covers text another edit of this record has already changed. "
                "Clear that edit first, or type the whole record.")
        self._commit(target, placed)

    def set_spans(self, key: str, old: str, new: str,
                  at: frozenset[int]) -> tuple[str, ...]:
        """Replace `old` with `new` at exactly the chosen offsets, as one target's edit.

        Returns a reason per span that could not be placed, so a rename batch applies
        what it can and says what it could not, rather than aborting whole or dropping
        part of its work quietly. Two batches touching a record compose, because every
        span is measured against the original text and never against a composed one.
        """
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        target = row.target or key
        base = self._text_of(target)
        entries = self._entries(target)
        skipped: list[str] = []
        for offset in sorted(at):
            if base is None or offset < 0 or offset + len(old) > len(base):
                # A span that does not lie inside the text cannot replace anything, and
                # splicing one would corrupt the record. Fail closed with the reason.
                skipped.append(
                    f"offset {offset} of {row.key} is not inside the record's own text, "
                    "so it was left as it reads")
                continue
            placed = self._place_in(entries, Pending("", offset, len(old), new))
            if placed is None:
                skipped.append(
                    f"offset {offset} of {row.key} lies inside an edit that is already "
                    "there, so it was left as it reads")
                continue
            entries = placed
        if entries != self._entries(target):
            self._commit(target, entries)
        return tuple(skipped)

    def snapshot(self, key: str) -> tuple[Pending, ...]:
        """The entries one row's target holds, for an undo step to restore exactly."""
        row = self.line(key)
        return self._entries((row.target or key) if row is not None else key)

    def restore(self, key: str, entries: tuple[Pending, ...]) -> None:
        """Put one target back to a snapshot this session was already in.

        No combination is attempted, because a snapshot was a state this session held,
        so this cannot fail. That is what makes undo of a rename, or of one row of a
        record, exact rather than a reconstruction that can be refused.
        """
        row = self.line(key)
        self._commit((row.target or key) if row is not None else key, tuple(entries))

    def _edit_for(self, row: Line, new: str) -> object:
        """One row's edit, on its own, with no other row of the record applied."""
        if row.kind == SLOT:
            return textedit.SlotEdit(slot=row.position[1], old=row.text, new=new)
        holder = self._record_of(row)
        if holder is None:
            raise textedit.TextEditError(
                f"{row.key} names record {row.target}, which this image does not carry")
        offset, length = self._span(row)
        replaced = holder.text[:offset] + new + holder.text[offset + length:]
        return textedit.RecordEdit(holder.selector, holder.start, holder.length,
                                   old=holder.text, new=replaced)

    def clear_edit(self, key: str) -> None:
        row = self.line(key)
        target = (row.target or key) if row is not None else key
        entries = self._entries(target)
        if row is None or row.key == target:
            # The target's own row: clearing it clears everything the target holds.
            remaining: tuple[Pending, ...] = ()
        else:
            remaining = tuple(entry for entry in entries if entry.key != row.key)
        if len(remaining) != len(entries):
            self._commit(target, remaining)

    def clear_all(self) -> None:
        if self.edits or self._pending:
            self.edits = {}
            self._pending = {}
            self._stale = True

    def ordered_edits(self) -> tuple[object, ...]:
        return tuple(self.edits[key] for key in self.edits)

    def pending_text(self, key: str) -> str:
        """What this row will say, whether or not its target record has an edit.

        A composed session edit knows where every row sits, including the rows nobody
        typed into, which moved when an edit before them grew, and a row whose own text a
        rename reached. A row with an entry of its own says exactly that entry's text. An
        edit adopted from a project file carries no spans, so its change is located by
        comparing the two texts instead.
        """
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        target = row.target or key
        entries = self._entries(target)
        composed = self._compose(target)
        if composed is None:
            return row.text
        if not entries:
            edit = self.edits.get(target)
            if edit is None:
                return row.text
            if row.view != LINES:
                return _new_of(edit)
            holder = self._record_of(row)
            if holder is None:
                return row.text
            return _span_in_new(_old_of(edit), _new_of(edit),
                                (row.position[1] - holder.start) // 2, len(row.text))
        offset, length = self._span(row)
        base = self._text_of(target)
        if base is not None and offset == 0 and length == len(base):
            # This row IS the target's whole text, which is what a record or slot row is,
            # so what it says is the composed text and not any single entry of it. Reading
            # an entry here showed 'U' for a record whose two entries composed to 'Une\nTvo'.
            return composed
        own = next((entry for entry in entries if entry.key == row.key), None)
        if own is not None:
            return own.text
        if any(offset < entry.end and entry.offset < offset + length for entry in entries):
            # An entry CONTAINS or STRADDLES this row, which is what a whole-record edit
            # and a rename across a line break both are. The row's span no longer locates
            # its text inside the composed one, so the text is located by comparing the
            # two instead of by arithmetic. Measured: slicing at the row's ORIGINAL offset
            # instead showed the wrong text for any whole-record edit that changed the
            # length, and reported those rows as UNCHANGED.
            base = self._text_of(target)
            if base is not None:
                return _span_in_new(base, composed, offset, length)
            return row.text
        start = offset + self._shift(target, offset)
        inside = sum(entry.delta for entry in entries
                     if offset <= entry.offset and entry.end <= offset + length)
        return composed[start:start + length + inside]

    def edited_keys(self) -> tuple[str, ...]:
        return tuple(self.edits)

    def project(self) -> Project:
        return Project(rom_sha256=self.model.sha256, rom_name=Path(self.model.path).name,
                       canonical_sha256=self.model.retail_sha256,
                       edits=self.ordered_edits())

    # --- the plan ------------------------------------------------------------

    def _prepare(self) -> None:
        if not self._stale:
            return
        self._stale = False
        if not self.edits:
            self._plan, self._by_record = None, {}
            return
        order = tuple(self.edits)
        self._plan = textedit.plan(self.model, [self.edits[key] for key in order])
        self._by_record = {key: self._plan.decisions[index]
                           for index, key in enumerate(order)}

    def plan(self) -> textedit.Plan | None:
        self._prepare()
        return self._plan

    def decision(self, key: str) -> textedit.Decision | None:
        self._prepare()
        row = self.line(key)
        return self._by_record.get((row.target or key) if row is not None else key)

    def refusal_reason(self, key: str) -> str:
        decision = self.decision(key)
        return "" if decision is None else decision.reason

    def refusals(self) -> tuple[textedit.Decision, ...]:
        plan = self.plan()
        return () if plan is None else plan.refusals

    # --- what a row shows ----------------------------------------------------

    def guard_holds(self, key: str) -> bool:
        """Whether the text this edit replaces still reads the way it did when made."""
        row = self.line(key)
        if row is None:
            return False
        edit = self.edits.get(row.target or key)
        holder = self._record_of(row) if row.kind == RECORD else None
        loaded = holder.text if holder is not None else row.text
        if edit is None:
            return False
        return loaded.count(_old_of(edit)) == 1

    def _changed(self, key: str) -> bool:
        """Whether an edit on this row's target actually changes this row."""
        row = self.line(key)
        if row is None or (row.target or key) not in self.edits:
            return False
        return self.pending_text(key) != row.text

    def state(self, key: str) -> State:
        self._prepare()
        row = self.line(key)
        if row is None:
            # An edit this image carries no row for: reported, never dropped.
            return State.BASE_CHANGED if key in self.edits else State.UNCHANGED
        if (row.target or key) not in self.edits:
            return State.UNCHANGED
        if not self._changed(key):
            # This row's own words are what they were, but its record changed around it, so
            # the row's bytes still move. Measured: a whole-record edit that grew the
            # record left every row whose own text it did not touch reading UNCHANGED, and
            # the counts line said nothing would move for a record that moves entirely.
            decision = self.decision(key)
            if decision is not None:
                if decision.method == textedit.REFUSED:
                    return State.REFUSED
                if decision.method == textedit.MOVE:
                    return State.WILL_MOVE
            return State.UNCHANGED
        if not self.guard_holds(key):
            return State.BASE_CHANGED
        decision = self.decision(key)
        if decision is None:
            return State.EDITED
        if decision.method == textedit.REFUSED:
            return State.REFUSED
        if decision.method == textedit.MOVE:
            return State.WILL_MOVE
        return State.EDITED

    def differs_from_retail(self, key: str) -> bool | None:
        """Whether this image already says something other than the original game.

        Trailing spaces are ignored: an in-place edit pays a shrink back with them,
        and a reader hears the same words either way.
        """
        row = self.line(key)
        if row is None or row.retail is None:
            return None
        return row.text.rstrip(" ") != row.retail.rstrip(" ")

    def headroom(self, key: str) -> Meter | None:
        """A row's own capacity with nothing used, or None when no limit is stated.

        The meter exists to tell a writer how much room a line has BEFORE they type, so
        an untouched row still has a number worth showing: zeros against the same limit
        the edit would be measured against. Measured, the empty state printed one
        placeholder twice with no number at all, so the headroom was invisible until
        after the fact. This is the row's own span rather than an invented budget: a row
        whose limit the engine does not state returns None and the surface says so.
        """
        row = self.line(key)
        if row is None:
            return None
        limit = self.limit_of(key)
        if limit is None:
            return None
        return Meter(chars=0, chars_limit=limit // 2, bytes=0, bytes_limit=limit)

    def limit_of(self, key: str) -> int | None:
        """The byte span a row's edit is measured against, or None when unstated.

        The engine's own statement wins when there is one, which is what a pending
        decision carries; otherwise the row's own span is the limit, because that is the
        room the text already occupies in place. Measured: without the fallback an
        untouched record-shaped row had no limit at all, so its budget could not be
        shown before the first keystroke.
        """
        row = self.line(key)
        if row is None:
            return None
        if row.view == RECORDS or row.kind == SLOT:
            decision = self.decision(key)
            if decision is not None and decision.bytes_before:
                return decision.bytes_before
        return len(row.text.encode("utf-16le")) or None

    def meter(self, key: str) -> Meter | None:
        """The NEW text against the span that decides its fate, in both units.

        A row with no pending change has no numbers to show, and a limit is absent
        when the engine did not state one: inventing either would be a ROM value
        this module is not allowed to compute. `headroom` is the same measurement with
        nothing used, which is what an untouched row shows.
        """
        row = self.line(key)
        if row is None or not self._changed(key):
            return None
        if row.view == RECORDS or row.kind == SLOT:
            decision = self.decision(key)
            edit = self.edits.get(row.target or key)
            if decision is None or edit is None:
                return None
            limit = decision.bytes_before or None
            text = _new_of(edit)
        else:
            limit = len(row.text.encode("utf-16le"))
            text = self.pending_text(key)
        return Meter(chars=len(text), chars_limit=None if limit is None else limit // 2,
                     bytes=len(text.encode("utf-16le")), bytes_limit=limit)

    def covering(self, key: str) -> tuple[str, ...]:
        row = self.line(key)
        return () if row is None else row.covering

    def sites(self, key: str) -> int:
        row = self.line(key)
        return 0 if row is None else row.sites

    # --- grouping, search and filters ---------------------------------------

    def grouped(self, by: str = UNGROUPED, rows: tuple[Line, ...] | None = None,
                term: str = "", states: frozenset[State] = frozenset(),
                locked: bool | None = None) -> tuple[Group, ...]:
        """The list as headings and rows, for the grouping the window asks for."""
        selected = self.matching(term=term, states=states, locked=locked) if rows is None \
            else rows
        if by == UNGROUPED:
            return (Group(label="", rows=selected),)
        if by == BY_PLACE:
            # Map-table order, then one honest group for everything the placement
            # route does not reach. No chapter is invented, because none exists.
            buckets: dict[int, list[Line]] = {}
            for row in selected:
                buckets.setdefault(row.place_index, []).append(row)
            groups = [Group(label=self.map_labels[index], rows=tuple(buckets[index]))
                      for index in sorted(index for index in buckets if index >= 0)]
            if -1 in buckets:
                groups.append(Group(label=UNPLACED, rows=tuple(buckets[-1])))
            return tuple(groups)
        if by != BY_SPEAKER:
            raise ValueError(f"{by!r} is not a grouping")
        buckets: dict[str, list[Line]] = {}
        for row in selected:
            buckets.setdefault(row.speaker_label, []).append(row)
        # A named speaker is more use than the unknown bucket, so it leads.
        return tuple(Group(label=name, rows=tuple(buckets[name]))
                     for name in sorted(buckets, key=lambda name: (name == UNKNOWN_SPEAKER,
                                                                    name.casefold())))

    def speaker_counts(self) -> dict[str, int]:
        """How many dialogue rows each speaker label covers, unknown included."""
        tally: dict[str, int] = {}
        for row in self._rows.get(LINES, {}).values():
            label = row.speaker_label
            tally[label] = tally.get(label, 0) + 1
        return tally

    def speaker_share(self) -> tuple[int, int]:
        """The resolved and total line counts, so a report can state the share."""
        rows = self._rows.get(LINES, {}).values()
        total = len(self._rows.get(LINES, {}))
        return sum(1 for row in rows if row.speaker), total

    def place_coverage(self) -> tuple[int, int]:
        """The placed and total rows of the current view, for the honest caption."""
        return (sum(1 for row in self.lines if row.place_index >= 0), len(self.lines))

    def map_order(self) -> tuple[str, ...]:
        """Every map label in map-table order, so a surface can show the order."""
        return tuple(self.map_labels[index] for index in sorted(self.map_labels))

    def matching(self, term: str = "", kind: str | None = None,
                 states: frozenset[State] = frozenset(),
                 locked: bool | None = None,
                 speaker: str | None = None) -> tuple[Line, ...]:
        """The rows a search box, the speaker filter and the filter chips leave.

        The term is matched against what the image says, what the original game
        said, and what this row has been changed to say, so a search finds the
        wording the reader is looking at.
        """
        needle = term.casefold()
        found = []
        for row in self.rows_of(kind):
            if speaker is not None and row.speaker_label != speaker:
                continue
            if states and self.state(row.key) not in states:
                continue
            if locked is not None and bool(textedit.locked_tokens(row.text)) is not locked:
                continue
            if needle:
                haystack = f"{row.text}\n{row.retail or ''}\n{self.pending_text(row.key)}"
                if needle not in haystack.casefold():
                    continue
            found.append(row)
        return tuple(found)

    def counts(self, kind: str | None = None) -> dict[str, int]:
        """Progress counters: how much of each list has been touched."""
        tally = {state: 0 for state in State}
        for row in self.rows_of(kind):
            tally[self.state(row.key)] += 1
        return tally

    # --- per-occurrence rename ----------------------------------------------

    def rename_hits(self, old: str, rows: tuple[Line, ...] | None = None) -> tuple[Hit, ...]:
        """Every dialogue occurrence of `old`, with the retail test's own answer."""
        if not old:
            return ()
        hits: list[Hit] = []
        for row in self._rows[RECORDS].values() if rows is None else rows:
            if old not in row.text or row.retail is None or len(row.text) != len(row.retail):
                continue
            try:
                occurrences = textedit.rename_occurrences(row.text, row.retail, old)
            except textedit.TextEditError:
                hits.append(Hit(key=row.key, snippet=row.text, retail="",
                                decision=textedit.UNCLEAR, at=-1))
                continue
            for occurrence in occurrences:
                hits.append(Hit(key=row.key, snippet=row.text, retail=occurrence.retail,
                                decision=occurrence.decision, at=occurrence.at))
        return tuple(hits)

    def rename_text(self, key: str, old: str, new: str, renamed_at: frozenset[int]) -> str:
        """The row's text with `new` at exactly the offsets the user chose."""
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        pieces: list[str] = []
        cursor = 0
        for at in sorted(renamed_at):
            pieces.append(row.text[cursor:at])
            pieces.append(new)
            cursor = at + len(old)
        pieces.append(row.text[cursor:])
        return "".join(pieces)

    # --- export --------------------------------------------------------------

    def export(self, path: str | Path) -> dict:
        """Replay the edit list from the base image and write a new file."""
        plan = self.plan()
        if plan is None:
            raise textedit.TextEditError("REFUSED: the project holds no edits to export")
        return textedit.apply(plan, path)


def open_image(rom_path: str | Path, canonical: str | Path | None = None,
               project: Project | None = None, view: str = LINES,
               order: str = APPEARANCE,
               cutters_from_pool: bool = True) -> Session:
    """Open an image read-only and build the session over it."""
    model = textedit.open_rom(rom_path, canonical=canonical)
    changed = project is not None and project.rom_sha256 != model.sha256
    return Session(model, project=project, base_changed=changed, view=view, order=order,
                   cutters_from_pool=cutters_from_pool)


def _span_between(old: str, new: str) -> tuple[int, int, str] | None:
    """The span of `old` that `new` replaces, or None when the two are identical.

    The inverse of `_span_in_new`, used to seed the span store from an edit that arrived
    as two texts: a project file's edit, or any edit this session did not record as a span.
    """
    if old == new:
        return None
    shortest = min(len(old), len(new))
    prefix = 0
    while prefix < shortest and old[prefix] == new[prefix]:
        prefix += 1
    suffix = 0
    while (suffix < shortest - prefix
           and old[len(old) - 1 - suffix] == new[len(new) - 1 - suffix]):
        suffix += 1
    return prefix, len(old) - prefix - suffix, new[prefix:len(new) - suffix]


def _span_in_new(old: str, new: str, offset: int, length: int) -> str:
    """The span of `new` that corresponds to `old[offset:offset + length]`.

    Used only for an edit this session did not type into a spoken line. The change
    is located by the common prefix and suffix of the two texts: a span before the
    change is unchanged, a span after it shifts by the change's length, and the
    span that contains the change is that span plus the difference. An insertion
    exactly at a span's end is attributed to the following span, which is the one
    case where this reading can be off by the inserted text.
    """
    shortest = min(len(old), len(new))
    prefix = 0
    while prefix < shortest and old[prefix] == new[prefix]:
        prefix += 1
    suffix = 0
    while (suffix < shortest - prefix
           and old[len(old) - 1 - suffix] == new[len(new) - 1 - suffix]):
        suffix += 1
    if offset + length <= prefix:
        return old[offset:offset + length]
    delta = len(new) - len(old)
    if offset >= len(old) - suffix:
        return new[offset + delta:offset + delta + length]
    return new[offset:offset + length + delta]


def _parts(key: str) -> tuple[int, int, int]:
    selector, start, length = (int(part) for part in key.split(":"))
    return selector, start, length


def _key_of(edit: object) -> str:
    if isinstance(edit, textedit.SlotEdit):
        return f"text:{edit.slot}"
    if isinstance(edit, textedit.RecordEdit):
        return edit.key
    raise textedit.TextEditError(
        f"{edit!r} is not a SlotEdit or a RecordEdit; this build stores the record "
        "decisions a rename produced")


def _old_of(edit: object) -> str:
    return getattr(edit, "old")


def _new_of(edit: object) -> str:
    return getattr(edit, "new")
