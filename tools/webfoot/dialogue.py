"""Public semantic authoring API for supported compressed dialogue.

Callers supply a recovered Atlas result, a verified profile, and project paths.
This module owns the mapping from storage identity to semantic identity and the
production replacement rules.  Callers never inspect handles, compression,
container offsets, or project TOML.

The contract DIALOGUE-VARIABLE-LENGTH-001 changed
-------------------------------------------------

The user-facing operation is now exactly **"replace this existing dialogue
record with this text"**. It used to be "...provided the text encodes to exactly
the record's retail length", because the durable handle - which carries the
decoded length as a field - was treated as immutable identity. It is not: the
handle is *authored*, and a replacement of any encodable length is spliced into
the record's own span, with every record the growth displaces re-authored and
repointed. Re-layout, handle authoring, repacking, relocation and reference
updating are implementation details the caller does not manage.

What survives from the old contract, deliberately:

* **The semantic key is the identity.** ``goku-greeting`` names the record; the
  raw handle value is one of its compiled properties. A record stays editable
  after its handle has changed, which is what a derivative reopen exercises.
* **Visible text is not identity.** Resolution still refuses to key on the
  displayed string, and a search result the SDK cannot map stays read-only.
* **Anchoring is by the record's own position.** A record's decoded start is
  invariant under this authoring operation - the splice happens at the record's
  end - so ``(selector, decoded_start)`` names the same record in the canonical
  ROM and in every derivative built from it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .compressed_dialogue import (
    AUTHORED_DIALOGUE_TARGETS,
    CompressedDialogueError,
    CompressedDialogueTarget,
    read_original_text,
    target_named,
)
from .handles import HANDLE_LENGTH_MAX_BYTES
from .profile import RomProfile
from .token_dictionary import authored_window_problem
from .project import (
    ProjectValidationError,
    read_project,
    write_dialogue_replacements,
)


class DialogueAuthoringError(ValueError):
    """Expected dialogue-authoring failure suitable for a product error."""


@dataclass(frozen=True, slots=True)
class DialogueProblem:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class DialogueValidation:
    problems: tuple[DialogueProblem, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.problems


def _supported_target(target: CompressedDialogueTarget, profile: RomProfile) -> bool:
    return target.profile_id is None or target.profile_id == profile.id


def _require_registered_target(
    target: CompressedDialogueTarget, profile: RomProfile | None = None
) -> CompressedDialogueTarget:
    """Return the canonical registry entry or fail closed on any identity drift."""
    try:
        registered = target_named(target.name)
    except CompressedDialogueError as exc:
        raise DialogueAuthoringError("Editing is not available for this record yet.") from exc
    if registered != target or (profile is not None and not _supported_target(registered, profile)):
        raise DialogueAuthoringError("Editing is not available for this record yet.")
    return registered


def _anchor(identity: Mapping[str, object]) -> tuple[int, int] | None:
    """``(selector, decoded start)`` from a recovered identity, or None.

    Both halves are required: a selector without a start names a container, not
    a record, and a start without a selector is not comparable to a target.
    """
    selector = identity.get("handle_selector")
    start = identity.get("handle_decoded_start")
    if type(selector) is not int or not isinstance(start, str):
        return None
    try:
        return selector, int(start, 16)
    except ValueError:
        return None


def resolve_dialogue_target(
    search_result: Mapping[str, object], profile: RomProfile
) -> CompressedDialogueTarget | None:
    """Resolve one decoded Atlas result to a supported semantic target.

    Two acceptances, and the second is the one that survives an authored edit:

    * the result's recovered packed handle is the registry's measured retail
      handle - the canonical case;
    * the result's recovered ``(selector, decoded start)`` is the registry
      record's own anchor. This is what lets a derivative built by this toolkit
      resolve ``goku-greeting`` after the edit re-authored its handle: the
      authoring operation splices at the record's END, so the record's start is
      invariant even though its length and handle are not.

    Only SDK-produced decoded-container results participate.  Visible text,
    addresses, decoded offsets of a phrase, and raw/address search results are
    never fallback identities.
    """
    if search_result.get("source") != "decoded-container-text":
        return None
    identity = search_result.get("identity")
    if not isinstance(identity, Mapping):
        return None
    packed = identity.get("packed_handle")
    anchor = _anchor(identity)
    for target in AUTHORED_DIALOGUE_TARGETS.values():
        if not _supported_target(target, profile):
            continue
        if packed == f"0x{target.packed_handle:08X}":
            return target
        if anchor == (target.selector, target.decoded_start):
            return target
    return None


def validate_dialogue_replacement(
    target: CompressedDialogueTarget, replacement: object,
    profile: RomProfile | None = None,
    canonical: bytes | None = None,
) -> DialogueValidation:
    """The production target's write-free candidate checks.

    Two layers, deliberately separated by what they can know:

    * **without an image** - the text is non-empty, encodes to UTF-16LE, and
      fits the durable handle's length field (4094 bytes). This is what an
      editor can answer per keystroke.
    * **with the base image** - the whole production re-layout is planned and
      discarded, so a replacement this container cannot hold is refused here
      rather than at the build. That includes the toolkit's own 64 KiB decoded
      container limit, which binds far earlier than the field's arithmetic
      maximum.
    """
    problems: list[DialogueProblem] = []
    try:
        _require_registered_target(target, profile)
    except DialogueAuthoringError:
        problems.append(DialogueProblem("unsupported_target", "Editing is not available for this record yet."))
        return DialogueValidation(tuple(problems))
    if not isinstance(replacement, str) or not replacement:
        problems.append(DialogueProblem("empty_replacement", "Replacement dialogue must not be empty."))
        return DialogueValidation(tuple(problems))
    # The expansion-token window is generated by the build, so it can never be
    # authored: without this a paste could produce a unit the decoder expands.
    window_problem = authored_window_problem(replacement, what="Replacement dialogue")
    if window_problem is not None:
        problems.append(DialogueProblem("reserved_token_window", window_problem + "."))
        return DialogueValidation(tuple(problems))
    try:
        encoded = replacement.encode("utf-16le")
    except UnicodeEncodeError:
        problems.append(DialogueProblem("unsupported_character", "Replacement contains an unsupported character."))
        return DialogueValidation(tuple(problems))
    if len(encoded) > HANDLE_LENGTH_MAX_BYTES:
        problems.append(DialogueProblem(
            "decoded_length",
            f"Replacement encodes to {len(encoded)} bytes; a durable dialogue "
            f"handle holds at most {HANDLE_LENGTH_MAX_BYTES}.",
        ))
        return DialogueValidation(tuple(problems))
    if canonical is not None:
        problem = _layout_problem(target, encoded, canonical, profile)
        if problem is not None:
            problems.append(problem)
    return DialogueValidation(tuple(problems))


def _layout_problem(
    target: CompressedDialogueTarget, encoded: bytes, canonical: bytes,
    profile: RomProfile | None,
) -> DialogueProblem | None:
    """Plan the real re-layout and report its refusal, or None. Writes nothing."""
    from .compressed_dialogue import read_container_layout, relayout_for_length, validate_relayout

    if profile is None:
        return None
    try:
        layout = read_container_layout(canonical, profile, target)
        relayout = relayout_for_length(
            layout, target, encoded, f"compressed-dialogue:{target.name}", canonical
        )
        validate_relayout(relayout, canonical)
    except CompressedDialogueError as exc:
        return DialogueProblem("replacement_layout", str(exc))
    return None


def get_dialogue_original(
    canonical: bytes, profile: RomProfile, target: CompressedDialogueTarget
) -> str:
    """Return the text this record's current durable handle names in this image.

    The registry supplies the record's position and the image supplies its
    current length, so the same call answers for the canonical ROM and for a
    derivative this toolkit already authored.
    """
    registered = _require_registered_target(target, profile)
    try:
        return read_original_text(canonical, profile, registered)
    except CompressedDialogueError as exc:
        raise DialogueAuthoringError(str(exc)) from exc


def get_dialogue_replacement(
    project_dir: str | Path,
    profile: RomProfile,
    target: CompressedDialogueTarget,
) -> str | None:
    """Return the current override after target and project compatibility checks."""
    registered = _require_registered_target(target, profile)
    return _load_compatible_project(project_dir, profile).dialogues.get(registered.name)


def _load_compatible_project(project_dir: str | Path, profile: RomProfile):
    project = read_project(project_dir)
    if project.meta.profile_id != profile.id:
        raise ProjectValidationError(
            f"project profile {project.meta.profile_id!r} does not match open ROM profile {profile.id!r}"
        )
    return project


def set_dialogue_replacement(
    project_dir: str | Path,
    profile: RomProfile,
    target: CompressedDialogueTarget,
    replacement: str,
    canonical: bytes | None = None,
) -> None:
    """Validate and persist one replacement in the normal project representation."""
    validation = validate_dialogue_replacement(target, replacement, profile, canonical)
    if not validation.valid:
        raise DialogueAuthoringError("; ".join(problem.message for problem in validation.problems))
    project = _load_compatible_project(project_dir, profile)
    dialogues = dict(project.dialogues)
    dialogues[target.name] = replacement
    write_dialogue_replacements(project_dir, dialogues)


def remove_dialogue_replacement(
    project_dir: str | Path, profile: RomProfile, target: CompressedDialogueTarget
) -> bool:
    """Remove one override; return whether project source changed."""
    registered = _require_registered_target(target, profile)
    project = _load_compatible_project(project_dir, profile)
    if registered.name not in project.dialogues:
        return False
    dialogues = dict(project.dialogues)
    del dialogues[registered.name]
    write_dialogue_replacements(project_dir, dialogues)
    return True
