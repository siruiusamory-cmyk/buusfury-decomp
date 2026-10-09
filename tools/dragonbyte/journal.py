"""The one edit journal for the active session.

An entry holds the document payload before an edit and the payload after it, and
nothing executable: undo and redo are readable from those two values alone, which
is why no callback is stored here and none is ever serialised. A document
participates by registering a reversible adapter - a reader, an installer, a
validator and a writer - so semantic, raw, asset and structural edits share one
timeline without this module knowing what any of them mean. Until an adapter is
registered for a target, an edit of that kind is refused with the reason, rather
than given an undo it cannot honour.

The journal is a third source of claimed-byte information, beside the range index
and the atlas objects, and it exposes the resource ranges its pending entries
claim so a later relocation can consult it. It does not implement the range index
and answers no byte-claim query itself.

No Qt is imported: a headless test drives the whole journal with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Callable, Mapping

from tools.webfoot.handles import HANDLE_LENGTH_MAX_BYTES
from tools.webfoot.layout import RomRange
from tools.webfoot.project import StatProject, write_dialogue_replacements
from tools.webfoot.token_dictionary import authored_window_problem

from .rawbytes import (
    RAW_TARGET,
    RawEdits,
    RawRefusal,
    RawWrite,
    claimed_by,
    write_raw_document,
)
from . import dataedits, mapedits, textedits


class JournalError(Exception):
    """An edit, an undo, a redo or a save was refused; the message says why."""


class UnknownEditTargetError(JournalError):
    """No reversible document is registered under this target name."""


class JournalAuthorityError(JournalError):
    """The operation does not belong to the project this journal is bound to."""


class EditKind(StrEnum):
    """The four edit kinds the product spec names."""

    SEMANTIC = "semantic"
    RAW = "raw"
    ASSET = "asset"
    STRUCTURAL = "structural"


@dataclass(frozen=True, slots=True)
class EditOperation:
    """One committed edit: the payload before it, the payload after it, and why.

    ``revision`` is assigned by the journal on commit and is monotonic; 0 means
    the operation was never committed. ``coalesce_key`` is the whole of the merge
    rule: an empty key never merges, and two consecutive operations with the same
    non-empty key over one target merge into one entry, so a continuous
    interaction is one undo rather than fifty.
    """

    kind: EditKind
    target: str
    owner: str
    before: object
    after: object
    resources: tuple[str, ...] = ()
    #: The byte ranges this operation claims, if it declares them. A raw write
    #: declares its own span; a semantic edit declares the extent it rewrites, so
    #: a later raw write into the same bytes is refused instead of racing it.
    claimed: tuple[RomRange, ...] = ()
    reason: str = ""
    revision: int = 0
    coalesce_key: str = ""


@dataclass(frozen=True, slots=True)
class _DocumentAdapter:
    """The four functions one reversible document registers."""

    read: Callable[[StatProject], object]
    install: Callable[[StatProject, object], StatProject]
    validate: Callable[[StatProject, object], None]
    write: Callable[[object, object], None]


def project_authority(project: StatProject) -> str:
    """The project's own identity, with no filesystem path in it.

    Two directories holding the same authored project are the same authority;
    the same directory opened twice is one authority, so an edit cannot be
    forged from a path that happens to point somewhere else.
    """
    meta = project.meta
    return f"{meta.name}/{meta.base_rom_sha256[:16]}/{meta.profile_id}"


def _read_dialogues(project: StatProject) -> object:
    return project.dialogues


def _install_dialogues(project: StatProject, payload: object) -> StatProject:
    return replace(project, dialogues=dict(payload))  # type: ignore[arg-type]


def _validate_dialogues(project: StatProject, payload: object) -> None:
    """The document-level checks, told through the SDK rather than restated.

    Two layers, by what can be known here:

    * the structure of the document - a mapping of string targets to string text.
      An EMPTY mapping is a legitimate authored state, not a refusal: the SDK's own
      writer removes the optional document for it, and ``read_project`` reads that
      absence back as "this project authors no dialogue";
    * the per-value checks ``validate_dialogue_replacement`` applies WITHOUT an
      image (it needs a registered target and a profile, so it cannot be called
      from a journal that holds neither): the reserved token window, through
      ``authored_window_problem``, and the durable handle's byte ceiling, through
      ``HANDLE_LENGTH_MAX_BYTES``.

    The layout layer - whether this image can hold the replacement, which needs
    the base bytes - arrives with the dialogue editing surfaces, which is where
    the target and the profile exist.
    """
    if not isinstance(payload, Mapping):
        raise JournalError(
            "A dialogue replacement document is a mapping of record names to text."
        )
    for target, text in payload.items():
        if not isinstance(target, str) or not target:
            raise JournalError("A dialogue record name must be a non-empty string.")
        if not isinstance(text, str) or not text:
            raise JournalError("Replacement dialogue must not be empty.")
        window = authored_window_problem(text, what="Replacement dialogue")
        if window is not None:
            raise JournalError(window + ".")
        try:
            encoded = text.encode("utf-16le")
        except UnicodeEncodeError as exc:
            raise JournalError(
                "Replacement dialogue contains a character that cannot be authored."
            ) from exc
        if len(encoded) > HANDLE_LENGTH_MAX_BYTES:
            raise JournalError(
                f"dialogue.{target} encodes to more than the "
                f"{HANDLE_LENGTH_MAX_BYTES}-byte maximum a durable dialogue handle "
                "holds."
            )


def _write_dialogues(directory: object, payload: object) -> None:
    write_dialogue_replacements(directory, payload)  # type: ignore[arg-type]


#: Target name -> the four functions that make that document reversible.
DOCUMENT_ADAPTERS: dict[str, _DocumentAdapter] = {
    "dialogues": _DocumentAdapter(
        read=_read_dialogues,
        install=_install_dialogues,
        validate=_validate_dialogues,
        write=_write_dialogues,
    ),
    # The Data destination's three authored tables. The four functions live in
    # their own module because they are the project's own documents rather than
    # anything this journal knows about; the registration is here because this
    # registry is the one list a target must appear in to be reversible at all.
    dataedits.DATA_TARGET: _DocumentAdapter(
        read=dataedits.read,
        install=dataedits.install,
        validate=dataedits.validate,
        write=dataedits.write,
    ),
    # The Maps destination's two authored documents, registered for the same
    # reason and in the same shape: this registry is the one list a target must
    # appear in to be reversible at all.
    mapedits.MAPS_TARGET: _DocumentAdapter(
        read=mapedits.read,
        install=mapedits.install,
        validate=mapedits.validate,
        write=mapedits.write,
    ),
    # The Scripts & Text destination's authored string table. A SEPARATE target
    # from "dialogues" on purpose: the two authored text documents reach two
    # independent systems in the image, and Save writes one payload per target, so
    # one shared target would let a string edit overwrite a dialogue replacement.
    textedits.TEXT_TARGET: _DocumentAdapter(
        read=textedits.read,
        install=textedits.install,
        validate=textedits.validate,
        write=textedits.write,
    ),
}


@dataclass(frozen=True, slots=True)
class RawContext:
    """Everything a raw write must be judged against, held by the caller.

    The product owns the image and the profile, so the journal is handed them
    rather than resolving a base ROM of its own. ``atlas`` is optional until S4
    builds the range index; the profile's declared extents stand in for it, which
    is the conservative direction.
    """

    base_image: bytes
    profile: object
    atlas: object | None = None


@dataclass(frozen=True, slots=True)
class RawRequest:
    """One requested raw write and the context it must be judged against."""

    write: object
    context: RawContext


def raw_request(after: object) -> RawWrite:
    """The write a raw request carries, or a refusal when it carries none."""
    if not isinstance(after, RawRequest) or not isinstance(after.write, RawWrite):
        raise RawRefusal("a raw byte edit carries a RawRequest holding a RawWrite.")
    return after.write


def write_raw(directory: object, payload: object) -> None:
    write_raw_document(Path(directory), payload)


class EditJournal:
    """One linear timeline of committed edits, one cursor, one revision counter.

    There is no boolean dirty flag and no settable counter: the cursor and the
    saved revision are the whole of the state, so undoing back to the saved point
    is clean by construction and cannot be made to look clean by hand.
    """

    def __init__(self) -> None:
        self._entries: list[EditOperation] = []
        self._cursor = 0
        self._saved_revision = 0
        self._counter = 0
        self._authority: str | None = None
        #: The raw byte document the project authors on disk, and the document at
        #: the cursor. The applied one is rebuilt from the base, never mutated in
        #: place, so a refusal cannot leave the two disagreeing.
        self._raw_base = RawEdits()
        self._raw_applied = RawEdits()

    # -- binding --------------------------------------------------------------

    @property
    def authority(self) -> str | None:
        return self._authority

    def bind(self, authority: str, *, raw: RawEdits | None = None) -> None:
        """Bind to one project, discarding every trace of another.

        A different project must never inherit this one's entries, checkpoints or
        revision counter, so binding is a full reset rather than a merge.

        `raw` is the raw byte document the project authors on disk. It is the
        immutable base the cursor replays onto, so a session that authors one new
        byte keeps every byte an earlier session authored instead of rebuilding
        the document from its own entries alone.
        """
        self._entries = []
        self._cursor = 0
        self._saved_revision = 0
        self._counter = 0
        self._authority = authority
        self._raw_base = raw if raw is not None else RawEdits()
        self._raw_applied = self._raw_base

    # -- editing --------------------------------------------------------------

    def apply(
        self,
        project: StatProject,
        *,
        kind: EditKind,
        target: str,
        after: object,
        resources: tuple[str, ...] = (),
        claimed: tuple[RomRange, ...] = (),
        reason: str = "",
        coalesce_key: str = "",
    ) -> StatProject:
        """Validate one edit, commit it, and return the edited project.

        Everything that can fail runs before anything is written down: the target
        is resolved, the authority is checked, the payload is validated and the
        new project is computed. An exception therefore leaves the entries, the
        cursor and the revision counter exactly as they were.

        A raw byte write is the one kind that does not change the project: it
        changes bytes the project's own documents do not describe. Its entry is
        owned by the `raw:` namespace of the address it writes, and the project
        handed back is the one handed in.
        """
        if target == RAW_TARGET:
            return self._apply_raw(project, after=after, reason=reason)
        adapter = DOCUMENT_ADAPTERS.get(target)
        if adapter is None:
            raise UnknownEditTargetError(
                f"No reversible document is registered for {target!r}, so this "
                "edit cannot be undone and was refused."
            )
        authority = self._authority_for(project)
        before = adapter.read(project)
        adapter.validate(project, after)
        edited = adapter.install(project, after)
        operation = self._operation(
            kind=kind,
            target=target,
            owner=authority,
            before=before,
            after=after,
            resources=resources,
            claimed=claimed,
            reason=reason,
            coalesce_key=coalesce_key,
        )
        self._commit(operation)
        return edited

    def raw_refusal(self, after: object) -> RawRefusal | None:
        """Why this raw write would be refused, or None. Commits nothing.

        The ONE judgment a raw write passes, called by the commit and by a caller
        that has to decide whether to ask a person at all. It is ordered by what
        the answer costs: the bytes' owner, then this session's own pending
        writes, then the confirmation last, so an owned range is refused without
        ever asking.
        """
        if not isinstance(after, RawRequest) or not isinstance(after.write, RawWrite):
            return RawRefusal("a raw byte edit carries a RawRequest holding a RawWrite.")
        write = after.write
        context = after.context
        if write.span.end > len(context.base_image):
            return RawRefusal(
                f"{write.owner}: 0x{write.offset:06X}+{write.span.size} extends past "
                f"the {len(context.base_image)}-byte image."
            )
        claim = claimed_by(context.profile, write.span, atlas=context.atlas)
        if claim is not None:
            owner, extent = claim
            return RawRefusal(
                f"These bytes back {owner}; edit that object instead.",
                owner=owner,
                claimed=extent,
            )
        # This session's own pending raw writes are the third source beside the
        # profile extents and the atlas, and the only one that can see a write
        # made here. A write at one offset and length replaces the write already
        # pending there, because one field has one owner; any other overlap is a
        # contradiction the plan would refuse, so it is refused here instead.
        for offset, pending in sorted(self._raw_applied.bytes_by_offset.items()):
            if not self._overlaps_pending(write, offset, pending):
                continue
            if offset == write.offset and len(pending) == len(write.new):
                continue
            return RawRefusal(
                f"{write.owner}: the pending write at 0x{offset:06X} covers "
                f"{len(pending)} byte(s), which this {len(write.new)}-byte write at "
                f"0x{write.offset:06X} overlaps without replacing; undo it first.",
                owner=write.owner,
            )
        # The applied semantic entries are the journal's own answer, and they are
        # consulted here because only the journal holds them. A raw entry's own
        # span is excluded: a raw write does not own bytes the way a structure
        # does. The redo tail above the cursor is not applied, so it claims
        # nothing and is not consulted.
        for entry in self._entries[: self._cursor]:
            if entry.target == RAW_TARGET:
                continue
            for declared in entry.claimed:
                if declared.overlaps(write.span):
                    return RawRefusal(
                        f"These bytes back {entry.owner}; edit it there, or undo that "
                        "edit first.",
                        owner=entry.owner,
                        claimed=declared,
                    )
        if not write.confirmed:
            return RawRefusal(
                "This write changes bytes no model explains, so it asks first: "
                f"0x{write.offset:06X} for {len(write.new)} byte(s), "
                f"{write.before.hex()} -> {write.new.hex()}, owned by {write.owner}."
            )
        return None

    def _apply_raw(
        self,
        project: StatProject,
        *,
        after: object,
        reason: str,
    ) -> StatProject:
        """Commit one raw byte write, or refuse it with the claiming owner."""
        refusal = self.raw_refusal(after)
        if refusal is not None:
            raise refusal
        write = raw_request(after)
        operation = self._operation(
            kind=EditKind.RAW,
            target=RAW_TARGET,
            owner=write.owner,
            before=write.before,
            after=write.new,
            resources=(),
            claimed=(write.span,),
            reason=reason or f"raw byte write at 0x{write.offset:06X}",
            coalesce_key="",
        )
        self._commit(operation)
        self._raw_applied = self._rebuild_raw()
        return project

    @staticmethod
    def _overlaps_pending(write: RawWrite, offset: int, pending: bytes) -> bool:
        return offset < write.span.end and write.offset < offset + len(pending)

    def _authority_for(self, project: StatProject) -> str:
        authority = project_authority(project)
        if self._authority is None:
            self._authority = authority
        elif self._authority != authority:
            raise JournalAuthorityError(
                f"This journal belongs to {self._authority}, not to {authority}."
            )
        return authority

    def _operation(
        self,
        *,
        kind: EditKind,
        target: str,
        owner: str,
        before: object,
        after: object,
        resources: tuple[str, ...],
        claimed: tuple[RomRange, ...],
        reason: str,
        coalesce_key: str,
    ) -> EditOperation:
        return EditOperation(
            kind=kind,
            target=target,
            owner=owner,
            before=before,
            after=after,
            resources=tuple(resources),
            claimed=tuple(claimed),
            reason=reason,
            revision=self._counter + 1,
            coalesce_key=coalesce_key,
        )

    def _commit(self, operation: EditOperation) -> None:
        """Append or merge `operation`, and move the revision counter with it.

        A fresh revision on a merge is the point: the merged entry's undo returns
        to before the WHOLE gesture, and a reused revision would let a merged
        journal look saved when it is not.
        """
        previous = self._pending()
        if self._merges_with(previous, operation):
            assert previous is not None
            merged = replace(
                previous,
                after=operation.after,
                resources=tuple(
                    dict.fromkeys(previous.resources + operation.resources)
                ),
                claimed=tuple(
                    dict.fromkeys(previous.claimed + operation.claimed)
                ),
                revision=operation.revision,
            )
            self._entries[self._cursor - 1] = merged
        else:
            # The user took a different branch from the cursor, so the abandoned
            # tail is dropped: a redo into a branch that no longer follows is a
            # lie about where the data came from.
            del self._entries[self._cursor :]
            self._entries.append(operation)
            self._cursor += 1
        self._counter = operation.revision

    @staticmethod
    def _merges_with(previous: EditOperation | None, operation: EditOperation) -> bool:
        """Whether ``operation`` continues ``previous`` or starts a new entry."""
        if previous is None or not operation.coalesce_key:
            return False
        return (
            previous.coalesce_key == operation.coalesce_key
            and previous.target == operation.target
            and previous.owner == operation.owner
            and previous.kind == operation.kind
        )

    # -- history --------------------------------------------------------------

    def undo(self, project: StatProject) -> StatProject:
        """Install the payload the entry above the cursor replaced."""
        pending = self._pending()
        if pending is None:
            raise JournalError("There is nothing to undo.")
        return self._move(project, pending, payload=pending.before, delta=-1)

    def redo(self, project: StatProject) -> StatProject:
        """Install the payload the entry below the cursor produced."""
        newer = self._at_cursor()
        if newer is None:
            raise JournalError("There is nothing to redo.")
        return self._move(project, newer, payload=newer.after, delta=1)

    def _move(
        self,
        project: StatProject,
        operation: EditOperation,
        *,
        payload: object,
        delta: int,
    ) -> StatProject:
        """Install one payload and move the cursor only once it has succeeded.

        Neither direction writes anything: an edit lives in memory until Save.
        A raw byte edit has nothing to install in the project - the bytes it
        changes are the image's, not a document's - so it moves the cursor and
        the raw document it keeps instead.
        """
        if operation.target == RAW_TARGET:
            if not isinstance(payload, bytes):
                raise RawRefusal("a raw byte entry holds before/after bytes.")
            self._cursor += delta
            self._raw_applied = self._rebuild_raw()
            return project
        adapter = DOCUMENT_ADAPTERS.get(operation.target)
        if adapter is None:
            raise UnknownEditTargetError(
                f"No reversible document is registered for {operation.target!r}."
            )
        moved = adapter.install(project, payload)
        self._cursor += delta
        return moved

    @staticmethod
    def _offset_of(operation: EditOperation) -> int:
        """The file offset a raw entry writes, from the span it claims."""
        if not operation.claimed:
            raise RawRefusal("a raw byte entry must claim the span it writes.")
        return operation.claimed[0].start.value

    @staticmethod
    def _raw_bytes(payload: object) -> bytes:
        if not isinstance(payload, bytes):
            raise RawRefusal("a raw byte entry holds before/after bytes.")
        return payload

    def _rebuild_raw(self) -> RawEdits:
        """The raw document at the cursor, replayed from the project's own base.

        The base is what the project authored on disk and each applied raw entry
        holds the bytes it wrote, so the state at any cursor is a function of the
        base and the history alone: no second field has to be kept in step, and a
        refusal cannot half-apply a write. This is O(depth) and runs once per raw
        apply, undo or redo.
        """
        document = self._raw_base
        for entry in self._entries[: self._cursor]:
            if entry.target != RAW_TARGET:
                continue
            document = replace(
                document,
                bytes_by_offset={
                    **document.bytes_by_offset,
                    self._offset_of(entry): self._raw_bytes(entry.after),
                },
            )
        return document

    # -- saving ---------------------------------------------------------------

    def save(self, project_dir: object, project: StatProject) -> None:
        """Persist every document the committed operations name, at the cursor.

        The payload written is the one at the cursor, not the newest ever seen: a
        Save after an undo must not resurrect the branch the user left.

        The write set is the whole history rather than the cursor's own entries,
        because a document an UNDONE operation touched still has to be made to
        agree with the project. Writing only what is applied would leave the base
        payload in memory and the edited one on disk, and the checkpoint below
        would then be a claim about a disk state that does not exist.

        The checkpoint moves only when every write has succeeded - a failure leaves
        the last real checkpoint in place and names the document it failed on,
        because claiming a save that did not happen is the defect this prevents.

        That guarantee holds only while the caller keeps its side of it: the
        project handed in must be the project this cursor's payloads produced. A
        document mutated outside `apply` would be written and then reported clean,
        so an edit that bypasses the journal is a defect no checkpoint can detect.

        Each document is replaced on its own, so a failure on the second leaves the
        first written while the checkpoint correctly stays put: multi-document
        atomicity is the ceiling here, and it is measured by
        `test_a_partial_multi_document_save_writes_what_it_can_and_holds_the_checkpoint`.
        When a second adapter lands, order the writes so the one most likely to
        fail goes first, or move the set into the SDK's single `write_project`.
        """
        for target in self._committed_targets():
            try:
                if target == RAW_TARGET:
                    write_raw(project_dir, self._raw_applied)
                    continue
                adapter = DOCUMENT_ADAPTERS[target]
                adapter.write(project_dir, adapter.read(project))
            except Exception as exc:
                raise JournalError(f"Could not save {target}: {exc}") from exc
        self._saved_revision = self.current_revision

    # -- reported state -------------------------------------------------------

    @property
    def can_undo(self) -> bool:
        return self._cursor > 0

    @property
    def can_redo(self) -> bool:
        return self._cursor < len(self._entries)

    @property
    def current_revision(self) -> int:
        """The revision at the cursor; 0 is the base state."""
        pending = self._pending()
        return pending.revision if pending is not None else 0

    @property
    def saved_revision(self) -> int:
        return self._saved_revision

    @property
    def is_dirty(self) -> bool:
        return self.current_revision != self._saved_revision

    @property
    def depth(self) -> int:
        """How many operations are applied - that is, lie at or below the cursor."""
        return self._cursor

    def edits(self) -> tuple[EditOperation, ...]:
        """The applied operations, oldest first."""
        return tuple(self._entries[: self._cursor])

    def pending_resources(self) -> frozenset[str]:
        """Every resource the applied operations claim, as a union.

        The union only: a redo tail that is not applied claims nothing, so a
        relocation asking this question is never told about work that is not in
        the project.
        """
        return frozenset(
            resource for entry in self._entries[: self._cursor] for resource in entry.resources
        )

    def pending_spans(self) -> tuple[RomRange, ...]:
        """Every byte range the applied operations declare they claim.

        The raw write's own answer to the question S4's range index will answer
        for the whole image; a caller that writes bytes consults this before it
        types. A redo tail claims nothing, as with `pending_resources`.
        """
        return tuple(
            span for entry in self._entries[: self._cursor] for span in entry.claimed
        )

    def raw_edits(self) -> RawEdits:
        """The raw byte document at the cursor."""
        return self._raw_applied

    def _committed_targets(self) -> list[str]:
        """The targets the committed history names, order-stable and de-duplicated.

        The whole history, not the applied prefix: an undone operation's document
        still has to be brought into agreement with the project by a Save.
        """
        return list(dict.fromkeys(entry.target for entry in self._entries))
    def _pending(self) -> EditOperation | None:
        """The entry the cursor sits above, or None at the base."""
        if self._cursor == 0:
            return None
        return self._entries[self._cursor - 1]

    def _at_cursor(self) -> EditOperation | None:
        """The entry the cursor sits on - the one a redo would apply, or None."""
        if self._cursor >= len(self._entries):
            return None
        return self._entries[self._cursor]

    def __len__(self) -> int:
        return self.depth
