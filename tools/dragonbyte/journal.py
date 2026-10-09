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
from typing import Callable, Mapping

from tools.webfoot.handles import HANDLE_LENGTH_MAX_BYTES
from tools.webfoot.project import StatProject, write_dialogue_replacements
from tools.webfoot.token_dictionary import authored_window_problem


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

    * the structure of the document - a non-empty mapping of string targets to
      string text, which is what ``_read_dialogues`` requires of the file;
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
    if not payload:
        raise JournalError("A dialogue replacement must name at least one record.")
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
}


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

    # -- binding --------------------------------------------------------------

    @property
    def authority(self) -> str | None:
        return self._authority

    def bind(self, authority: str) -> None:
        """Bind to one project, discarding every trace of another.

        A different project must never inherit this one's entries, checkpoints or
        revision counter, so binding is a full reset rather than a merge.
        """
        self._entries = []
        self._cursor = 0
        self._saved_revision = 0
        self._counter = 0
        self._authority = authority

    # -- editing --------------------------------------------------------------

    def apply(
        self,
        project: StatProject,
        *,
        kind: EditKind,
        target: str,
        after: object,
        resources: tuple[str, ...] = (),
        reason: str = "",
        coalesce_key: str = "",
    ) -> StatProject:
        """Validate one edit, commit it, and return the edited project.

        Everything that can fail runs before anything is written down: the target
        is resolved, the authority is checked, the payload is validated and the
        new project is computed. An exception therefore leaves the entries, the
        cursor and the revision counter exactly as they were.
        """
        adapter = DOCUMENT_ADAPTERS.get(target)
        if adapter is None:
            raise UnknownEditTargetError(
                f"No reversible document is registered for {target!r}, so this "
                "edit cannot be undone and was refused."
            )
        authority = project_authority(project)
        if self._authority is None:
            self._authority = authority
        elif self._authority != authority:
            raise JournalAuthorityError(
                f"This journal belongs to {self._authority}, not to {authority}."
            )
        before = adapter.read(project)
        adapter.validate(project, after)
        edited = adapter.install(project, after)
        # A fresh revision on a merge is the point: the merged entry's undo
        # returns to before the WHOLE gesture, and a reused revision would let a
        # merged journal look saved when it is not.
        operation = EditOperation(
            kind=kind,
            target=target,
            owner=authority,
            before=before,
            after=after,
            resources=tuple(resources),
            reason=reason,
            revision=self._counter + 1,
            coalesce_key=coalesce_key,
        )
        previous = self._pending()
        if self._merges_with(previous, operation):
            assert previous is not None
            merged = replace(
                previous,
                after=after,
                resources=tuple(dict.fromkeys(previous.resources + operation.resources)),
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
        return edited

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
        """
        adapter = DOCUMENT_ADAPTERS.get(operation.target)
        if adapter is None:
            raise UnknownEditTargetError(
                f"No reversible document is registered for {operation.target!r}."
            )
        moved = adapter.install(project, payload)
        self._cursor += delta
        return moved

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
        """
        for target in self._committed_targets():
            adapter = DOCUMENT_ADAPTERS[target]
            try:
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
