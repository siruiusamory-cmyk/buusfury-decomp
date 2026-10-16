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

from dataclasses import dataclass, replace
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
    #: An edit changed how many lines this record has, so its rows no longer line up with
    #: it. They are read-only until that edit is reverted, and they say so.
    RESTRUCTURED = "record restructured"


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
        self._rows: dict[str, dict[str, Line]] = self._read_rows()
        #: target -> that target's pending WHOLE text. This is the only state an edit
        #: keeps per record, so every reader derives from one text and no two derivations
        #: can disagree. Measured, four review rounds each found a case where a second
        #: derivation by arithmetic disagreed with the export; there is only one now.
        self._text: dict[str, str] = {}
        #: row key -> the row's text as the image has it, for comparing against the derived
        #: text and for restoring one row.
        self._original_rows: dict[str, str] = {
            key: row.text for key, row in self._rows[LINES].items()}
        #: target -> its own row keys, in the partition's order.
        self._line_keys: dict[str, tuple[str, ...]] = self._index_lines()
        #: Targets whose row count the current edits changed, so their rows are marked.
        self._restructured: set[str] = set()
        #: The edit list the derived rows were computed for, so one edit derives once.
        self._derived_for: tuple = ()
        #: The row lookup, filled by `_resort`. Declared here because adopting a project
        #: refreshes the rows before the first sort has run.
        self._index: dict[str, Line] = {}
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

        A saved edit IS the record's whole text, which is the only thing this session
        stores per record, so adopting one is storing that text and nothing else. Measured
        before this model: a saved edit lived only in the edit list, so the next edit of
        that record composed from the original image text and silently discarded the saved
        change, and the undo after it erased the change outright.
        """
        edits: dict[str, object] = {}
        text: dict[str, str] = {}
        unmatched: list[str] = []
        for edit in project.edits:
            key = _key_of(edit)
            if self._rows[RECORDS].get(key) is None and self._rows[SLOT].get(key) is None:
                unmatched.append(key)
            edits[key] = edit
            text[key] = _new_of(edit)
        self.edits = edits
        self._text = text
        self.unmatched = tuple(unmatched)
        self._stale = True
        self._refresh()

    def _record_of(self, row: Line) -> textedit.Record | None:
        return self.model.record(*_parts(row.target)) if row.target else None

    def _index_lines(self) -> dict[str, tuple[str, ...]]:
        """Every row key, grouped by the record an edit of it would address, in order."""
        grouped: dict[str, list[str]] = {}
        for row in self._rows[LINES].values():
            grouped.setdefault(row.target or row.key, []).append(row.key)
        return {target: tuple(keys) for target, keys in grouped.items()}

    # --- what a record will say, and what its rows say ------------------------

    def _entries(self, target: str) -> tuple[str, ...]:
        """The row keys one target's own partition holds, in order."""
        return self._line_keys.get(target, ())

    def _text_of(self, target: str) -> str | None:
        """The target's own text before any edit, or None when nothing carries it."""
        holder = self._rows[RECORDS].get(target)
        if holder is not None:
            return holder.text
        slot = self._rows[SLOT].get(target)
        return None if slot is None else slot.text

    def _pending(self, target: str) -> str | None:
        """The record's pending whole text: the stored one, or its own."""
        if target in self._text:
            return self._text[target]
        return self._text_of(target)

    def _derived(self) -> dict[str, str]:
        """Every row's text as the EXPORT will write it, keyed the way this session keys.

        Rows are not derived by arithmetic on the record's text. They are read from the
        plan's own built output, through the engine's own line rule, so a row's text is
        what the exported image carries by construction rather than by a second opinion.
        Measured, four review rounds each found a case where arithmetic on the record's
        text disagreed with the export: edits to two rows of one record, a rename beside a
        line edit, a row inside a whole-record edit, and a saved edit read back from a
        project. None of those can drift here, because there is only one derivation.

        Rows are matched to the partition they came from by (target, ordinal). A target
        whose row COUNT changed has been restructured by an edit, and its rows are marked
        rather than guessed at.
        """
        if not self.edits:
            self._restructured = set()
            return dict(self._original_rows)
        plan = self.plan()
        if plan is None:
            self._restructured = set()
            return dict(self._original_rows)
        # The engine's OWN reader over the bytes the plan built, records included. Reusing
        # this model's record table against the edited streams was a real defect: a record
        # whose edit GREW it kept its old span, so the rows were cut at the old offsets and
        # disagreed with the exported image while the gate, which shared this route, agreed
        # with the session rather than with the export.
        model = textedit.load(plan.output, self.model.path, check_profile=False)
        grouped: dict[str, list[str]] = {}
        for row in textedit.lines(model, cutters_from_pool=self.cutters_from_pool):
            grouped.setdefault(row.target, []).append(row.text)
        moved = self._output_keys(plan, model)
        derived: dict[str, str] = {}
        self._restructured = set()
        for target, keys in self._line_keys.items():
            where = target if target not in self._text else moved.get(target)
            if where is None:
                # This record's edit moved it and the built image does not say where, so the
                # rows are marked rather than left reading text that is no longer true.
                self._restructured.add(target)
                for key in keys:
                    derived[key] = self._original_rows.get(key, "")
                continue
            texts = grouped.get(where, [])
            if len(texts) != len(keys):
                self._restructured.add(target)
                for key in keys:
                    derived[key] = self._original_rows.get(key, "")
                continue
            for key, text in zip(keys, texts):
                derived[key] = text
        return derived

    def _output_keys(self, plan, model) -> dict[str, str]:
        """Where each edited record lives in the plan's built image, keyed as it was here.

        A record that MOVES gets a new key, because a key is its container, offset and
        length. The plan says where each placement landed, and the record's own text
        identifies it among the built image's records, so the rows can be read from the
        image the export writes instead of from the offsets the original had.
        """
        by_span: dict[tuple[int, int], list] = {}
        for record in model.records:
            by_span.setdefault((record.start, record.length), []).append(record)
        mapping: dict[str, str] = {}
        for placement in plan.placements:
            exact = [record for record in by_span.get((placement.new_start,
                                                       placement.new_length), ())
                     if record.text == placement.text]
            if len(exact) == 1:
                mapping[placement.key] = exact[0].key
        for item in plan.in_place:
            # An in-place edit keeps its own span, so its key does not move.
            mapping[f"{item.selector}:{item.start}:{item.length}"] = \
                f"{item.selector}:{item.start}:{item.length}"
        return mapping

    def _refresh(self) -> None:
        """Bring every row's text up to what the export would write, once per edit list."""
        signature = tuple((key, _new_of(edit)) for key, edit in self.edits.items())
        if signature == self._derived_for:
            return
        self._derived_for = signature
        derived = self._derived()
        for key, text in derived.items():
            row = self._rows[LINES].get(key)
            if row is not None and row.text != text:
                refreshed = replace(row, text=text)
                self._rows[LINES][key] = refreshed
                # The lookup index holds the same rows, so leaving it behind made every
                # caller that asks for a row by key see the text from before the edit. The
                # clearing case caught it by finding no text left to clear.
                if self._index.get(key) is row:
                    self._index[key] = refreshed

    def set_edit(self, key: str, new: str) -> None:
        """Record what one row should say, as the record's own whole text.

        The only state this session keeps for a record is its text, so every way of
        editing a record writes that one thing and every reader derives from it.
        """
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        if not row.text and not new:
            return
        target = row.target or key
        current = self._pending(target)
        if current is None:
            raise textedit.TextEditError(
                f"{key} names a target this image does not carry")
        if self._is_whole_row(row, target):
            self._store(target, new, current)
            return
        if target in self._restructured:
            raise textedit.TextEditError(
                f"{target} was restructured by an earlier edit, so its rows no longer "
                "line up with it. Edit the record itself, or clear that edit first.")
        self._store(target, self._replace(row, new, current), current)

    def _is_whole_row(self, row: Line, target: str) -> bool:
        """Whether this row is the target's whole text, which a record or slot row is."""
        return row.key == target or row.view != LINES

    def _replace(self, row: Line, new: str, current: str) -> str:
        """The record's text with this row's own text replaced by `new`.

        The row's text is located inside the record's CURRENT text and must occur exactly
        once, so nothing is located by arithmetic on offsets that earlier edits moved. A
        row whose text appears twice in its record, or is empty, is refused rather than
        guessed at, and the message says which.
        """
        for candidate in (row.text, self._original_rows.get(row.key, "")):
            if not candidate:
                continue
            found = current.count(candidate)
            if found == 1:
                return current.replace(candidate, new, 1)
        raise textedit.TextEditError(
            f"this line's own text appears {current.count(row.text)} time(s) in its "
            "record, so which part of the record it replaces cannot be decided. Edit the "
            "record itself.")

    def _store(self, target: str, text: str, current: str) -> None:
        """Keep the record's text, or drop it when it is back to what the image says."""
        original = self._text_of(target)
        if text == original or not text:
            self._text.pop(target, None)
        else:
            self._text[target] = text
        edit = self._edit_for(target)
        if edit is None:
            self.edits.pop(target, None)
        else:
            self.edits[target] = edit
        self._stale = True
        self._refresh()

    def _edit_for(self, target: str) -> object | None:
        """The engine edit this session's stored text amounts to, if any."""
        text = self._text.get(target)
        original = self._text_of(target)
        holder = self._rows[RECORDS].get(target)
        if text is None or original is None or text == original:
            return None
        if holder is None:
            slot = self._rows[SLOT].get(target)
            if slot is None:
                return None
            return textedit.SlotEdit(slot=slot.position[1], old=original, new=text)
        record = self._record_of(holder)
        if record is None:
            return None
        return textedit.RecordEdit(record.selector, record.start, record.length,
                                   old=original, new=text)

    def set_rename(self, key: str, old: str, new: str, at: frozenset[int]) -> tuple[str, ...]:
        """Replace `old` with `new` at the chosen offsets of the record's OWN text.

        Offsets come from the same text the dialog showed, so a rename composes with an
        edit already made instead of replacing it, and two renames of one record compose
        because both are measured against that one text.
        """
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        target = row.target or key
        current = self._pending(target)
        if current is None:
            return (f"{key} names a target this image does not carry",)
        skipped: list[str] = []
        for offset in sorted(at):
            if offset < 0 or offset + len(old) > len(current):
                skipped.append(
                    f"offset {offset} of {key} is not inside the record's own text, so it "
                    "was left as it reads")
                continue
            if current[offset:offset + len(old)] != old:
                skipped.append(
                    f"offset {offset} of {key} no longer reads {old!r}, so it was left as "
                    "it reads")
                continue
            current = current[:offset] + new + current[offset + len(old):]
        if current != self._pending(target):
            self._store(target, current, self._pending(target) or current)
        return tuple(skipped)

    def snapshot(self, key: str) -> str | None:
        """The whole text one row's target holds, for an undo step to restore exactly."""
        row = self.line(key)
        return self._text.get((row.target or key) if row is not None else key)

    def restore(self, key: str, text: str | None) -> None:
        """Put one target back to a whole text this session was already in."""
        row = self.line(key)
        target = (row.target or key) if row is not None else key
        if text is None:
            self._text.pop(target, None)
        else:
            self._text[target] = text
        edit = self._edit_for(target)
        if edit is None:
            self.edits.pop(target, None)
        else:
            self.edits[target] = edit
        self._stale = True
        self._refresh()

    def clear_edit(self, key: str) -> None:
        """Clear one row's edit: the whole target for a record row, its own text for a line."""
        row = self.line(key)
        if row is None:
            self._text.pop(key, None)
            self.edits.pop(key, None)
            self._stale = True
            self._refresh()
            return
        target = row.target or key
        if self._is_whole_row(row, target):
            self._store(target, self._text_of(target) or "", self._pending(target) or "")
            return
        current = self._pending(target)
        if current is None or target in self._restructured:
            return
        original = self._original_rows.get(row.key)
        if original is None:
            raise textedit.TextEditError(
                f"{row.key} is not a row this image carries, so there is nothing to "
                "restore it to. Clear the whole record instead.")
        # A refusal here is REPORTED and not swallowed. Measured: swallowing it made Clear a
        # silent no-op on a row whose derived text no longer matched its record, while the
        # edit went on being exported, which is the worst of both.
        restored = self._replace(row, original, current)
        self._store(target, restored, current)

    def clear_all(self) -> None:
        if self.edits or self._text:
            self.edits = {}
            self._text = {}
            self._stale = True
            self._refresh()

    def ordered_edits(self) -> tuple[object, ...]:
        return tuple(self.edits[key] for key in self.edits)

    def pending_text(self, key: str) -> str:
        """What this row will say, which is what the export writes for it.

        A line row's text is the row's own, refreshed from the plan's built output. A
        record or slot row's text is the target's whole stored text. Neither is computed
        from offsets, so no edit can move one without the other following.
        """
        row = self.line(key)
        if row is None:
            raise KeyError(key)
        self._refresh()
        target = row.target or key
        if self._is_whole_row(row, target):
            return self._pending(target) if self._pending(target) is not None else row.text
        refreshed = self._rows[LINES].get(row.key)
        if refreshed is None:
            return row.text
        return refreshed.text
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
        """Whether an edit on this row's target actually changes this row.

        Compared against the row's text as the IMAGE has it, not as the session currently
        shows it, because the session's rows carry the derived text.
        """
        row = self.line(key)
        if row is None or (row.target or key) not in self.edits:
            return False
        original = self._original_rows.get(row.key, row.text)
        return self.pending_text(key) != original

    def state(self, key: str) -> State:
        self._prepare()
        row = self.line(key)
        if row is None:
            # An edit this image carries no row for: reported, never dropped.
            return State.BASE_CHANGED if key in self.edits else State.UNCHANGED
        target = row.target or key
        if target not in self.edits:
            return State.UNCHANGED
        if target in self._restructured and not self._is_whole_row(row, target):
            return State.RESTRUCTURED
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
        # The row's span in the IMAGE. Reading it from the row's current text made the limit
        # grow with the edit, so a line always reported itself exactly at its own limit and
        # the meter said nothing.
        original = self._original_rows.get(row.key, row.text)
        return len(original.encode("utf-16le")) or None

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
            limit = len(self._original_rows.get(row.key, row.text).encode("utf-16le"))
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
            # The record's OWN text, so the offsets the dialog shows are offsets in the text
            # a rename edits. Measuring them on the image's text instead would aim at
            # offsets that an edit already moved.
            text = self.pending_text(row.key)
            if old not in text or row.retail is None or len(text) != len(row.retail):
                continue
            try:
                occurrences = textedit.rename_occurrences(text, row.retail, old)
            except textedit.TextEditError:
                hits.append(Hit(key=row.key, snippet=text, retail="",
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
