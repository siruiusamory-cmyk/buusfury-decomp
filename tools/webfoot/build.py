"""Extract, validate and build: the project lifecycle.

TOOLKIT-002. This module orchestrates and owns no format of its own. It reads a
ROM through `webfoot.stats`, writes text through `webfoot.project`, and emits an
image through `webfoot.write`. There is exactly one write path in this toolkit
and this module calls it rather than reimplementing it - a second writer is how
a project silently diverges from the ROM-first path it is supposed to replace.

The lifecycle:

    extract   verified ROM  -> project directory        (never copies the ROM)
    validate  project + ROM -> pass/fail, writing nothing
    build     project + ROM -> NEW image + manifest      (base untouched)

**Determinism is asserted, not assumed.** Nothing here consults the clock, the
filesystem's ordering, the machine's name, or a random source. Extraction sorts
by durable identity; the build applies changes in offset order because
`plan_changes` already sorts them. `reproducible-builds.org` lists timestamps,
build paths, and unstable input order as the standard sources of variance, and
each is excluded structurally here rather than scrubbed afterwards.

**A build validates before it writes.** Schema, profile, base identity and
every semantic value are checked while the output does not yet exist, so a
rejected build leaves nothing behind to clean up or mistake for a good one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import capability
from .profile import RomProfile, RomProfileCatalog, VerificationStatus
from .project import (
    PROJECT_FORMAT_VERSION,
    ProjectMeta,
    ProjectValidationError,
    StatProject,
    read_project,
    write_project,
)
from .rom import RomIdentification, identify_rom
from .stats import (
    CHARACTER_FIELDS,
    ENEMY_FIELDS,
    StatProfileError,
    StatTables,
    load_stat_tables,
)
from .text import (
    TextProfileError,
    TextStrings,
    TextTooLongError,
    load_text_strings,
)
from .write import (
    ByteChange,
    ProjectProvenance,
    WriteManifest,
    emit_image,
    plan_changes,
)


class BuildError(ValueError):
    """Base error for the extract/validate/build lifecycle."""


class ProjectRomMismatchError(BuildError):
    """Raised when a project is built against a ROM it was not authored for.

    This is the fail-closed rule the project format exists to enforce. A
    project pins one base image by SHA-256; applying it to a different image
    would produce a ROM whose provenance is a lie, because the manifest would
    claim edits that landed at offsets meaning something else entirely.
    """


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """What `validate` found. Empty `problems` means the project can build."""

    project_name: str
    profile_id: str
    base_sha256: str
    enemy_count: int
    character_count: int
    problems: tuple[str, ...]
    #: TOOLKIT-004. Zero when the project authors no text, which is legal.
    string_count: int = 0

    @property
    def passed(self) -> bool:
        return not self.problems


@dataclass(frozen=True, slots=True)
class BuildResult:
    """One completed build."""

    manifest: WriteManifest
    output_path: Path
    manifest_path: Path | None
    project_name: str


# --- extract -------------------------------------------------------------


#: Capabilities `extract` knows how to write into a project. A profile must
#: declare at least one; which ones it declares decides what the project holds.
_EXTRACTABLE = (
    capability.Capability.ENEMY_STATS,
    capability.Capability.CHARACTER_BASE_STATS,
    capability.Capability.TEXT_STRINGS,
)


def _require_extractable_profile(identification: RomIdentification) -> RomProfile:
    """The verified profile, if it declares anything this toolkit can extract.

    Verification is delegated to the subsystem gates that follow, which each
    re-check identity and the packaged contract for the capability they use.
    This function answers only the prior question - is there anything here to
    extract at all - so that a profile with no readable content is refused with
    that reason instead of with whichever subsystem happened to be tried first.
    """
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise BuildError("extraction requires an exactly verified ROM")
    profile = match.profile
    declared = [item for item in _EXTRACTABLE if capability.declared(profile, item)]
    if not declared:
        raise BuildError(
            f"profile {profile.id!r} declares no extractable content; this "
            "toolkit can read none of its stats, characters or text"
        )
    return profile


def extract_project(
    rom_path: str | Path,
    project_dir: str | Path,
    catalog: RomProfileCatalog,
    *,
    name: str | None = None,
) -> list[Path]:
    """Read a verified ROM and write a deterministic project. Never writes the ROM.

    The ROM is not copied into the project. A project is source; the base image
    is a separately-held input referenced by hash, which is what lets a mod be
    published without redistributing the game.

    `name` defaults to the profile id rather than to the directory name,
    because a directory name is a fact about where the project currently sits -
    exactly the kind of mutable filesystem detail `project.toml` must not pin.

    Every subsystem is extracted when the profile declares it and omitted when it
    does not, so one project layout serves games with different capabilities
    rather than forking per game. A profile declaring nothing this toolkit can
    read is refused outright: an empty project would be a misleading artifact
    rather than a useful one.
    """
    identification = identify_rom(rom_path, catalog)
    profile = _require_extractable_profile(identification)

    meta = ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id=profile.id,
        game=profile.game,
        base_rom_sha256=identification.hashes.sha256,
        base_rom_size=identification.size,
        name=name if name is not None else profile.id,
    )

    # Stats are extracted when the verified profile declares both stat tables.
    # `StatProfileError` here means "this ROM has no stats this toolkit can
    # read" - true of Legacy of Goku II, whose stat tables match none of this
    # toolkit's record shapes - which is a fact about the profile rather than a
    # failure of the extraction, so the rest of the project is still written.
    try:
        tables = load_stat_tables(rom_path, catalog)
    except StatProfileError:
        enemies: list = []
        characters: list = []
    else:
        enemies = [
            # Alias is None: this project has verified NAMES for the 9 characters
            # and for no enemy. Emitting an invented label would put a fabricated
            # fact into authored source, where it would then look extracted.
            (entry.identity, entry.record, entry.original_bytes, None)
            for entry in tables.enemies()
        ]
        characters = [
            (entry.identity, entry.record, entry.original_bytes, entry.alias)
            for entry in tables.characters()
        ]

    # Text is extracted when the verified profile declares a string table, and
    # omitted otherwise. `TextProfileError` here means "this ROM has no text
    # this toolkit can read", which is a fact about the profile rather than a
    # failure of the extraction - so the rest of the project is still written.
    try:
        strings = [
            (entry.identity, entry.text)
            for entry in load_text_strings(rom_path, catalog).entries()
        ]
    except TextProfileError:
        strings = []

    return write_project(
        project_dir,
        meta,
        enemies=enemies,
        characters=characters,
        strings=strings,
    )


# --- shared validation ---------------------------------------------------


def _check_identity(
    project: StatProject,
    identification: RomIdentification,
    profile: RomProfile,
) -> list[str]:
    """Confirm the project was authored against exactly this base image.

    Takes the identification directly rather than reaching through a loaded stat
    table, because identity must be checkable for a profile that declares no
    stats at all - and because reading it off whichever subsystem happened to
    load was always incidental.
    """
    problems: list[str] = []
    actual_sha256 = identification.hashes.sha256

    if project.meta.base_rom_sha256 != actual_sha256:
        problems.append(
            f"base ROM mismatch: project requires sha256 "
            f"{project.meta.base_rom_sha256}, supplied ROM is {actual_sha256}"
        )
    if project.meta.base_rom_size != identification.size:
        problems.append(
            f"base ROM size mismatch: project requires "
            f"{project.meta.base_rom_size} bytes, supplied ROM is "
            f"{identification.size}"
        )
    if project.meta.profile_id != profile.id:
        problems.append(
            f"profile mismatch: project targets {project.meta.profile_id!r}, "
            f"supplied ROM verified as {profile.id!r}"
        )
    return problems


def _check_records(project: StatProject, tables: StatTables | None) -> list[str]:
    """Check every authored record against the loaded tables.

    Three distinct failures, each reported against the offending entity:
    a record the ROM does not have, a record the project omitted, and a field
    whose value the semantic layer refuses.

    ``tables`` is None when the profile declares no stat tables. Mirrors
    `_check_strings`: only a project that *authors* records against such a ROM
    is a problem, and it is reported as one.
    """
    problems: list[str] = []
    if tables is None:
        if project.enemies or project.characters:
            return [
                "project authors stat records, but this ROM's profile declares "
                "no stat tables; a build would silently drop every authored record"
            ]
        return problems

    for label, authored, live, allowed in (
        ("enemy", project.enemies, {e.identity: e for e in tables.enemies()}, ENEMY_FIELDS),
        (
            "character",
            project.characters,
            {c.identity: c for c in tables.characters()},
            CHARACTER_FIELDS,
        ),
    ):
        for identity in sorted(set(authored) - set(live), key=lambda i: i.key):
            problems.append(
                f"{identity}: project declares a {label} record that this ROM "
                "does not contain"
            )
        for identity in sorted(set(live) - set(authored), key=lambda i: i.key):
            problems.append(
                f"{identity}: project is missing this {label} record; a build "
                "would silently leave it at its base value"
            )

        for identity in sorted(set(authored) & set(live), key=lambda i: i.key):
            values = authored[identity]
            entry = live[identity]

            if values["raw"] != entry.original_bytes:
                problems.append(
                    f"{identity}: authored raw bytes do not match this ROM; the "
                    "record's undecoded data was extracted from a different image"
                )

            for field, (minimum, maximum) in allowed.items():
                value = values[field]
                if value < minimum:
                    problems.append(
                        f"{identity}.{field}={value} is below the minimum {minimum}"
                    )
                elif maximum is not None and value > maximum:
                    problems.append(
                        f"{identity}.{field}={value} exceeds the maximum {maximum}"
                    )

    return problems


def _check_strings(project: StatProject, strings: TextStrings | None) -> list[str]:
    """Check every authored string against the loaded string table.

    Mirrors `_check_records`: a string the ROM does not have, a string the
    project omitted, and text the codec or the allocation refuses. The last of
    those is the one specific to variable-length content - a stat field fails on
    its value, a string fails on its *size*.

    Encodability is checked here rather than at project load, because whether a
    string can be encoded depends on the profile's encoding and a project is not
    paired with a profile until a build. `set_text` raises `TextCodecError` for
    text this ROM's codec cannot produce, which arrives below as a `ValueError`.
    """
    problems: list[str] = []
    if not project.strings:
        return problems
    if strings is None:
        return [
            "project authors text, but this ROM's profile declares no string "
            "table; a build would silently drop every authored string"
        ]

    live = {entry.identity: entry for entry in strings.entries()}

    for identity in sorted(set(project.strings) - set(live), key=_identity_order):
        problems.append(
            f"{identity}: project declares a string that this ROM does not contain"
        )
    for identity in sorted(set(live) - set(project.strings), key=_identity_order):
        problems.append(
            f"{identity}: project is missing this string; a build would silently "
            "leave it at its base value"
        )

    for identity in sorted(set(project.strings) & set(live), key=_identity_order):
        try:
            strings.set_text(identity, project.strings[identity])
        except (TextTooLongError, ValueError) as exc:
            problems.append(str(exc))

    return problems


def _identity_order(identity: object) -> int:
    """Sort key for reporting. Only table-indexed identities reach this."""
    return getattr(identity, "index", -1)


def _load_for_project(
    project_dir: str | Path,
    rom_path: str | Path,
    catalog: RomProfileCatalog,
) -> tuple[
    StatProject,
    RomIdentification,
    RomProfile,
    StatTables | None,
    TextStrings | None,
]:
    """Read the project and whichever subsystems this ROM's profile declares.

    A None subsystem means the profile does not declare it, which is a supported
    state rather than an error - only a project that *authors* content against a
    ROM lacking it is a problem, and the `_check_*` functions report that.
    """
    project = read_project(project_dir)
    identification = identify_rom(rom_path, catalog)
    profile = _require_extractable_profile(identification)
    try:
        tables: StatTables | None = load_stat_tables(rom_path, catalog)
    except StatProfileError:
        tables = None
    try:
        strings: TextStrings | None = load_text_strings(rom_path, catalog)
    except TextProfileError:
        strings = None
    return project, identification, profile, tables, strings


# --- validate ------------------------------------------------------------


def validate_project(
    project_dir: str | Path,
    rom_path: str | Path,
    catalog: RomProfileCatalog,
) -> ValidationReport:
    """Check a project against a base ROM. Writes nothing, ever."""
    project, identification, profile, tables, strings = _load_for_project(
        project_dir, rom_path, catalog
    )

    problems = _check_identity(project, identification, profile)
    # Record checks are meaningful only against the right image; running them
    # after an identity failure would bury the real cause under 150 mismatches.
    if not problems:
        problems = _check_records(project, tables) + _check_strings(project, strings)

    return ValidationReport(
        project_name=project.meta.name,
        profile_id=project.meta.profile_id,
        base_sha256=project.meta.base_rom_sha256,
        enemy_count=len(project.enemies),
        character_count=len(project.characters),
        string_count=len(project.strings),
        problems=tuple(problems),
    )


# --- build ---------------------------------------------------------------


def _apply_project_to_tables(project: StatProject, tables: StatTables) -> None:
    """Push authored semantic values into the loaded tables.

    Only fields that actually differ are set, so `plan()`'s reason strings name
    the real edits rather than reporting every record as touched.
    """
    for identity, values in project.enemies.items():
        entry = tables.enemy(identity)
        for field in ENEMY_FIELDS:
            if getattr(entry.record, field) != values[field]:
                tables.set_enemy_field(identity, field, values[field])

    for identity, values in project.characters.items():
        entry = tables.character(identity)
        for field in CHARACTER_FIELDS:
            if getattr(entry.record, field) != values[field]:
                tables.set_character_field(identity, field, values[field])


def build_project(
    project_dir: str | Path,
    rom_path: str | Path,
    output_path: str | Path,
    catalog: RomProfileCatalog,
    *,
    manifest_path: str | Path | None = None,
) -> BuildResult:
    """Build a project into a NEW ROM image. The base is never modified.

    Fails closed before writing: a project that does not validate produces an
    error and no output file. That ordering is the reason `validate_project`
    exists as its own step rather than as a flag - the check has to be usable
    without the build, and the build has to run it regardless.
    """
    project, identification, profile, tables, strings = _load_for_project(
        project_dir, rom_path, catalog
    )

    identity_problems = _check_identity(project, identification, profile)
    if identity_problems:
        raise ProjectRomMismatchError("; ".join(identity_problems))

    # `_check_strings` applies the authored text as it checks it, so it runs
    # before `_apply_project_to_tables` and its problems join the same gate.
    problems = _check_records(project, tables) + _check_strings(project, strings)
    if problems:
        raise ProjectValidationError(
            f"project failed validation with {len(problems)} problem(s): "
            + "; ".join(problems[:5])
            + ("; ..." if len(problems) > 5 else "")
        )

    # One plan for every subsystem, not one plan each. Overlap detection is
    # per-plan, so two plans could each validate while together writing the
    # same bytes; merging makes a stat record and a string that claimed the
    # same span a hard error instead of a silent last-writer-wins.
    #
    # Every declared subsystem contributes every record, edited or not - that is
    # what proves the round trip, since an unedited record must re-encode to its
    # original bytes and `plan_changes` then drops it as a no-op.
    changes: list[ByteChange] = []
    base_bytes: bytes | None = None
    if tables is not None:
        _apply_project_to_tables(project, tables)
        changes += tables.changes()
        base_bytes = tables.base_bytes
    if strings is not None:
        changes += strings.changes()
        base_bytes = strings.base_bytes if base_bytes is None else base_bytes

    if base_bytes is None:
        # Unreachable: `_require_extractable_profile` refuses a profile that
        # declares nothing, so at least one subsystem loaded. Kept because
        # silently emitting a copy of the base would look like a successful
        # build that applied the project.
        raise BuildError(
            f"profile {profile.id!r} declares no buildable content"
        )

    plan = plan_changes(
        base_bytes,
        changes,
        profile_id=profile.id,
        base_sha256=identification.hashes.sha256,
    )

    manifest = emit_image(
        rom_path,
        output_path,
        plan,
        manifest_path=manifest_path,
        project=ProjectProvenance(
            name=project.meta.name,
            format_version=project.meta.format_version,
        ),
    )

    return BuildResult(
        manifest=manifest,
        output_path=Path(output_path),
        manifest_path=Path(manifest_path) if manifest_path is not None else None,
        project_name=project.meta.name,
    )
