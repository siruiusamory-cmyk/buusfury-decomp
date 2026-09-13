"""Public semantic authoring API for supported compressed dialogue.

Callers supply a recovered Atlas result, a verified profile, and project paths.
This module owns the mapping from storage identity to semantic identity and the
production replacement rules.  Callers never inspect handles, compression,
container offsets, or project TOML.
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
from .profile import RomProfile
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


def resolve_dialogue_target(
    search_result: Mapping[str, object], profile: RomProfile
) -> CompressedDialogueTarget | None:
    """Resolve one decoded Atlas result to a supported semantic target.

    Only SDK-produced decoded-container results participate.  Visible text,
    addresses, decoded offsets, and raw/address search results are never fallback
    identities.
    """
    if search_result.get("source") != "decoded-container-text":
        return None
    identity = search_result.get("identity")
    if not isinstance(identity, Mapping):
        return None
    packed = identity.get("packed_handle")
    for target in AUTHORED_DIALOGUE_TARGETS.values():
        expected = f"0x{target.packed_handle:08X}"
        if packed == expected and _supported_target(target, profile):
            return target
    return None


def validate_dialogue_replacement(
    target: CompressedDialogueTarget, replacement: object,
    profile: RomProfile | None = None,
) -> DialogueValidation:
    """Perform the production target's lightweight, write-free candidate checks."""
    problems: list[DialogueProblem] = []
    try:
        _require_registered_target(target, profile)
    except DialogueAuthoringError:
        problems.append(DialogueProblem("unsupported_target", "Editing is not available for this record yet."))
        return DialogueValidation(tuple(problems))
    if not isinstance(replacement, str) or not replacement:
        problems.append(DialogueProblem("empty_replacement", "Replacement dialogue must not be empty."))
        return DialogueValidation(tuple(problems))
    try:
        encoded = replacement.encode("utf-16le")
    except UnicodeEncodeError:
        problems.append(DialogueProblem("unsupported_character", "Replacement contains an unsupported character."))
        return DialogueValidation(tuple(problems))
    if len(encoded) != target.decoded_length:
        problems.append(DialogueProblem(
            "decoded_length",
            f"Replacement encodes to {len(encoded)} bytes; this target requires exactly "
            f"{target.decoded_length} bytes.",
        ))
    return DialogueValidation(tuple(problems))


def get_dialogue_original(
    canonical: bytes, profile: RomProfile, target: CompressedDialogueTarget
) -> str:
    """Return the retail/original text for a supported target."""
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
) -> None:
    """Validate and persist one replacement in the normal project representation."""
    validation = validate_dialogue_replacement(target, replacement, profile)
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
