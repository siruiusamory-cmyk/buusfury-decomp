"""One open image, one edit list, one plan, and the state of every line.

No Qt is imported, so a test drives every answer with no window open. Every ROM
semantic comes from `tools.webfoot.textedit`; this module decides only which edits
are pending, what a line's state is, and what the meters show.

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


class State(Enum):
    """A line's primary state. The word and the glyph belong to the theme."""

    UNCHANGED = "unchanged"
    EDITED = "edited"
    WILL_MOVE = "will move"
    REFUSED = "refused"
    BASE_CHANGED = "base changed"


@dataclass(frozen=True, slots=True)
class Line:
    """One editable thing: a string slot or a dialogue record."""

    key: str
    kind: str
    text: str
    retail: str | None
    covering: tuple[str, ...] = ()
    sites: int = 0

    @property
    def shows_retail(self) -> bool:
        """Whether the canonical reference is loaded, so 'differs' can be answered."""
        return self.retail is not None


@dataclass(frozen=True, slots=True)
class Meter:
    """The NEW text against the span the engine will let it use, in both units."""

    chars: int
    chars_limit: int | None
    bytes: int
    bytes_limit: int | None


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
                 base_changed: bool = False) -> None:
        self.model = model
        self.edits: dict[str, object] = {}
        self.lines = self._read_lines()
        self._index = {line.key: line for line in self.lines}
        self.unmatched: tuple[str, ...] = ()
        self.base_changed = base_changed
        self._plan: textedit.Plan | None = None
        self._by_key: dict[str, textedit.Decision] = {}
        self._stale = True
        if project is not None:
            self.adopt(project)

    # --- reading the image ---------------------------------------------------

    def _read_lines(self) -> tuple[Line, ...]:
        lines = [Line(key=slot.key, kind=SLOT, text=slot.text, retail=slot.retail)
                 for slot in self.model.slots]
        lines += [Line(key=record.key, kind=RECORD, text=record.text,
                       retail=self._retail_text(record), covering=record.covering,
                       sites=len(record.sites))
                  for record in self.model.records]
        return tuple(lines)

    def _retail_text(self, record: textedit.Record) -> str | None:
        stream = self.model.retail_streams.get(record.selector)
        if stream is None or record.start + record.length > len(stream):
            return None
        return stream[record.start:record.start + record.length].decode("utf-16le", "replace")

    def line(self, key: str) -> Line | None:
        return self._index.get(key)

    def keys(self, kind: str) -> tuple[str, ...]:
        return tuple(line.key for line in self.lines if line.kind == kind)

    def total(self, kind: str) -> int:
        return sum(1 for line in self.lines if line.kind == kind)

    # --- the edit list -------------------------------------------------------

    def adopt(self, project: Project) -> None:
        """Take a saved edit list. An edit whose guard misses is kept, not rebased."""
        edits: dict[str, object] = {}
        unmatched: list[str] = []
        for edit in project.edits:
            key = _key_of(edit)
            if self.line(key) is None:
                unmatched.append(key)
            edits[key] = edit
        self.edits = edits
        self.unmatched = tuple(unmatched)
        self._stale = True

    def set_edit(self, key: str, new: str) -> None:
        """Record what one line should say, clearing the edit when it says that already."""
        line = self.line(key)
        if line is None:
            raise KeyError(key)
        if not line.text:
            raise textedit.TextEditError(
                f"{key} is empty, so there is nothing for an edit to name as the text it "
                "replaces")
        if new == line.text:
            self.clear_edit(key)
            return
        self.edits[key] = _edit_for(line, new)
        self._stale = True

    def clear_edit(self, key: str) -> None:
        if self.edits.pop(key, None) is not None:
            self._stale = True

    def clear_all(self) -> None:
        if self.edits:
            self.edits = {}
            self._stale = True

    def ordered_edits(self) -> tuple[object, ...]:
        return tuple(self.edits[key] for key in self.edits)

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
            self._plan, self._by_key = None, {}
            return
        order = tuple(self.edits)
        self._plan = textedit.plan(self.model, [self.edits[key] for key in order])
        self._by_key = {key: self._plan.decisions[index] for index, key in enumerate(order)}

    def plan(self) -> textedit.Plan | None:
        self._prepare()
        return self._plan

    def decision(self, key: str) -> textedit.Decision | None:
        self._prepare()
        return self._by_key.get(key)

    def refusals(self) -> tuple[textedit.Decision, ...]:
        plan = self.plan()
        return () if plan is None else plan.refusals

    # --- what a row shows ----------------------------------------------------

    def guard_holds(self, key: str) -> bool:
        """Whether the text this edit replaces still reads the way it did when made."""
        line, edit = self.line(key), self.edits.get(key)
        if line is None or edit is None:
            return False
        return line.text.count(_old_of(edit)) == 1

    def state(self, key: str) -> State:
        self._prepare()
        if key not in self.edits:
            return State.UNCHANGED
        if not self.guard_holds(key):
            return State.BASE_CHANGED
        decision = self._by_key.get(key)
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
        line = self.line(key)
        if line is None or line.retail is None:
            return None
        return line.text.rstrip(" ") != line.retail.rstrip(" ")

    def meter(self, key: str) -> Meter | None:
        """The NEW text, and the span the engine will let it use, when it said so."""
        self._prepare()
        edit = self.edits.get(key)
        decision = self._by_key.get(key)
        if edit is None or decision is None:
            return None
        limit = decision.bytes_before or None
        return Meter(chars=len(_new_of(edit)), chars_limit=None if limit is None else limit // 2,
                     bytes=len(_new_of(edit).encode("utf-16le")), bytes_limit=limit)

    def covering(self, key: str) -> tuple[str, ...]:
        line = self.line(key)
        return () if line is None else line.covering

    def sites(self, key: str) -> int:
        line = self.line(key)
        return 0 if line is None else line.sites

    # --- search and filters --------------------------------------------------

    def matching(self, term: str = "", kind: str | None = None,
                 states: frozenset[State] = frozenset(),
                 locked: bool | None = None) -> tuple[Line, ...]:
        """The rows a search box, a list toggle and the filter chips leave.

        The term is matched against what the image says, what the original game
        said, and what this line has been changed to say, so a search finds the
        wording the reader is looking at.
        """
        needle = term.casefold()
        found = []
        for line in self.lines:
            if kind is not None and line.kind != kind:
                continue
            if states and self.state(line.key) not in states:
                continue
            if locked is not None and bool(textedit.locked_tokens(line.text)) is not locked:
                continue
            if needle:
                edit = self.edits.get(line.key)
                typed = "" if edit is None else _new_of(edit)
                haystack = f"{line.text}\n{line.retail or ''}\n{typed}".casefold()
                if needle not in haystack:
                    continue
            found.append(line)
        return tuple(found)

    def counts(self, kind: str | None = None) -> dict[str, int]:
        """Progress counters: how much of each list has been touched."""
        tally = {state: 0 for state in State}
        for line in self.lines:
            if kind is not None and line.kind != kind:
                continue
            tally[self.state(line.key)] += 1
        return tally

    # --- per-occurrence rename ----------------------------------------------

    def rename_hits(self, old: str) -> tuple[Hit, ...]:
        """Every dialogue occurrence of `old`, with the retail test's own answer."""
        if not old:
            return ()
        hits: list[Hit] = []
        for line in self.lines:
            if line.kind != RECORD or old not in line.text or line.retail is None:
                continue
            try:
                occurrences = textedit.rename_occurrences(line.text, line.retail, old)
            except textedit.TextEditError:
                hits.append(Hit(key=line.key, snippet=line.text, retail="",
                                decision=textedit.UNCLEAR, at=-1))
                continue
            for occurrence in occurrences:
                hits.append(Hit(key=line.key, snippet=line.text, retail=occurrence.retail,
                                decision=occurrence.decision, at=occurrence.at))
        return tuple(hits)

    def rename_text(self, key: str, old: str, new: str, renamed_at: frozenset[int]) -> str:
        """The line's text with `new` at exactly the offsets the user chose."""
        line = self.line(key)
        if line is None:
            raise KeyError(key)
        pieces: list[str] = []
        cursor = 0
        for at in sorted(renamed_at):
            pieces.append(line.text[cursor:at])
            pieces.append(new)
            cursor = at + len(old)
        pieces.append(line.text[cursor:])
        return "".join(pieces)

    # --- export --------------------------------------------------------------

    def export(self, path: str | Path) -> dict:
        """Replay the edit list from the base image and write a new file."""
        plan = self.plan()
        if plan is None:
            raise textedit.TextEditError("REFUSED: the project holds no edits to export")
        return textedit.apply(plan, path)


def open_image(rom_path: str | Path, canonical: str | Path | None = None,
               project: Project | None = None) -> Session:
    """Open an image read-only and build the session over it."""
    model = textedit.open_rom(rom_path, canonical=canonical)
    changed = project is not None and project.rom_sha256 != model.sha256
    return Session(model, project=project, base_changed=changed)


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


def _edit_for(line: Line, new: str) -> object:
    if line.kind == SLOT:
        return textedit.SlotEdit(slot=int(line.key.split(":", 1)[1]), old=line.text, new=new)
    selector, start, length = (int(part) for part in line.key.split(":"))
    return textedit.RecordEdit(selector, start, length, line.text, new)
