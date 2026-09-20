"""Shared authored-image transaction and provenance verification.

DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001. Every editor domain in this SDK that
publishes a *DragonByte Z-authored derivative* of the canonical ROM performs the
same five steps:

    semantic edit
    -> domain legality validation
    -> bounded byte-edit plan
    -> shared authored-image transaction        <- this module
    -> verified derivative + provenance

**What this module owns, once, for every such domain:**

* the path conventions: where a derivative's provenance document lives
  (:func:`manifest_path_for`) and where a save stages its files before publishing
  them (:func:`staging_path`);
* refusal of a save whose source is any path it would write or delete - the
  requested output, the derived manifest, and both staging names;
* edit-plan normalization: duplicate physical writes collapse, conflicting
  writes to one field fail closed before anything is emitted, and the applied
  order is deterministic. The bounded-write and overlap checks are *not*
  reimplemented here; :func:`tools.webfoot.write.plan_changes` remains their one
  implementation;
* emission at temporary sibling paths, verification there, and only then
  publication - so a failed emit, a failed verification or a failed publish
  leaves whatever already existed at the destination byte-for-byte intact and no
  temporary file behind;
* the byte-level half of output verification: emitted size, emitted digest, and
  the requirement that no byte outside a declared field changed;
* the byte-level half of provenance: manifest schema and identity, the declared
  change list, the output digest and byte count, the requirement that each declared
  field holds its declared replacement, and reconstruction of the canonical image
  from the derivative alone.

**What stays in the domain, deliberately:**

* whether a particular semantic change is *legal* - "is this map-layout change
  allowed?". For reading, that question is answered by ``check_changes``, which
  also turns each declared owner into the domain's own typed target. For writing,
  the domain answers it before it builds its plan; nothing here adds a rule of
  its own;
* how a declared change is re-read out of an emitted image, which is the
  transaction's ``verify`` step.

Nothing here knows about maps, chunks, tiles or any other domain format, and no
new ROM capability is added by using it: an accepted derivative is still exactly
the canonical image plus the declared, domain-legal fields.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Generic, TypeVar

from . import write as write_sdk
from .write import ByteChange, WriteError, WriteManifest

#: The sibling document a DragonByte Z-authored image ships with, appended to the
#: image's own file name so one image maps to exactly one provenance document.
AUTHORED_MANIFEST_SUFFIX = ".dragonbyte.json"

#: Temporary sibling suffix. A destination is only ever replaced from a file
#: carrying this suffix in the same directory.
STAGING_SUFFIX = ".webfoot-partial"

#: The only provenance schema this build understands.
SUPPORTED_SCHEMA_VERSION = 1

#: What a verification hands back: the domain's typed record for one declared
#: change.
TARGET = TypeVar("TARGET")

#: What a save's own verification step hands back: the domain's typed re-read of
#: the emitted image.
VERIFIED = TypeVar("VERIFIED")


class AuthoredImageError(ValueError):
    """An authored-image save, or a declared derivative, was refused."""


# --- path conventions --------------------------------------------------------


def manifest_path_for(rom_path: str | Path) -> Path:
    """The provenance document path that belongs to one authored image file."""
    path = Path(rom_path)
    return path.with_name(path.name + AUTHORED_MANIFEST_SUFFIX)


def staging_path(destination: str | Path) -> Path:
    """A temporary sibling of a destination: same directory, same filesystem.

    A sibling keeps the final move atomic (one rename within one directory) and
    guarantees that nothing is ever written at the destination until the finished,
    verified artifact is ready to replace it.
    """
    destination = Path(destination)
    return destination.with_name(f".{destination.name}{STAGING_SUFFIX}")


def refuse_source_alias(source: str | Path, candidates: Iterable[tuple[str, Path]]) -> None:
    """Refuse a save whose every path - derived ones included - touches the source.

    The requested output is only the first of the paths a save writes or deletes:
    the provenance document is derived from it, and both are staged at siblings.
    A source file named after any of those would otherwise be replaced or removed
    by the save, since the underlying emitter's own alias guard only ever sees the
    staging paths it is handed. Every path is resolved, so a symlink or junction
    alias is caught too.
    """
    source_resolved = Path(source).resolve()
    for label, path in candidates:
        if Path(path).resolve() == source_resolved:
            raise AuthoredImageError(
                f"refusing to save: the {label} path is the source ROM ({path}); "
                "choose another name"
            )


# --- edit-plan normalization -------------------------------------------------


def normalize_changes(changes: Iterable[ByteChange]) -> tuple[ByteChange, ...]:
    """Collapse duplicate physical writes, refuse conflicting ones, order by offset.

    Two changes that would write the same bytes to the same field are one change:
    the survivor is the first in an order that does not depend on the caller's, so
    the emitted image and its manifest are identical whatever order the caller
    reported its edits in.

    Two changes that would write *different* bytes to one field are a
    contradiction and fail closed here, before anything is emitted: a half-applied
    plan would publish an image no caller asked for.

    Overlapping but not identical spans are not this function's business - they
    are refused by :func:`tools.webfoot.write.plan_changes`, the one
    implementation of that rule.
    """
    ordered = sorted(
        changes, key=lambda change: (change.offset, change.owner, change.old, change.new)
    )
    normalized: list[ByteChange] = []
    seen: dict[int, ByteChange] = {}
    for change in ordered:
        first = seen.get(change.offset)
        if first is None:
            seen[change.offset] = change
            normalized.append(change)
            continue
        if (first.old, first.new) != (change.old, change.new):
            raise AuthoredImageError(
                f"{first.owner} (0x{first.offset:08X}+{first.size}) and "
                f"{change.owner} (0x{change.offset:08X}+{change.size}) would write "
                "different bytes to the same field"
            )
    return tuple(normalized)


def verify_emitted_image(
    base: bytes,
    data: bytes,
    changes: tuple[ByteChange, ...],
    manifest: WriteManifest,
) -> tuple[int, ...]:
    """Prove an emitted image is the verified base plus exactly the declared fields.

    The three byte-level questions every authored output must answer, whatever the
    domain: it is the same length as the image it derives from, it hashes to what
    its own provenance declares, and every byte that differs lies inside a
    requested field. Returns the offsets that actually differ.
    """
    if len(data) != len(base):
        raise AuthoredImageError(f"the written ROM is {len(data)} bytes, not {len(base)}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != manifest.output_sha256:
        raise AuthoredImageError("the written ROM does not match its own digest")
    changed = tuple(
        index for index, (before, after) in enumerate(zip(base, data)) if before != after
    )
    allowed = {index for change in changes for index in range(change.offset, change.end)}
    unexpected = tuple(index for index in changed if index not in allowed)
    if unexpected:
        raise AuthoredImageError(
            "the written ROM changed bytes outside the requested fields: "
            + ", ".join(f"0x{index:08X}" for index in unexpected[:8])
        )
    if manifest.output_size != len(data):
        raise AuthoredImageError("the written ROM's recorded size is wrong")
    return changed


# --- the transaction ---------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AuthoredImageSave(Generic[VERIFIED]):
    """The verified result of writing a new image from a bounded byte-edit plan."""

    output_path: Path
    #: The provenance document published beside the image; it is what lets
    #: DragonByte Z reopen this derivative later.
    manifest_path: Path
    output_sha256: str
    output_size: int
    #: True when the normalized plan changes no byte; the output is then
    #: byte-identical to the base image.
    no_op: bool
    #: The normalized plan, ordered by offset.
    changes: tuple[ByteChange, ...]
    #: Every byte that differs from the base image, measured on the output.
    changed_offsets: tuple[int, ...]
    #: Whatever the caller's own verification step returned for the emitted bytes.
    verified: VERIFIED


def save_authored_image(
    base: bytes,
    *,
    source_path: str | Path,
    output_path: str | Path,
    profile_id: str,
    changes: Iterable[ByteChange],
    canonical_sha256: str,
    verify: Callable[[bytes, tuple[ByteChange, ...]], VERIFIED],
) -> AuthoredImageSave[VERIFIED]:
    """Write a NEW image from `changes` against `base`, then publish it.

    Never writes the source: the output path is refused when it resolves to the
    source, and the base is only ever read. With no effective change the output is
    byte-identical to the source, because every emitted byte comes from the
    verified base.

    `base` must be the canonical image named by `canonical_sha256`; both it and the
    file at `source_path` are re-proved by that hash before anything is written, so
    a plan computed against some other image cannot be emitted here.

    The transaction proves the output is `base` plus the spans this caller declared,
    of whatever width. Which widths and meanings a derivative may declare is the
    domain's contract, and :func:`verify_authored_image` is where that contract is
    enforced on the way back in.

    The image and its provenance document are built at temporary sibling paths,
    verified there, and only then moved onto the requested destinations, so a
    failed emit or a failed verification leaves whatever already existed at the
    destination byte-for-byte intact.

    `verify` is the domain's own re-read of the emitted bytes - it receives those
    bytes and the normalized plan, and returns the domain's typed result. It runs
    only after the byte-level checks above have passed, and whatever it raises
    propagates unchanged, with the staging paths cleaned up.

    The image is published first and its provenance second: the artifact the user
    asked for is the image. Two renames cannot be one atomic step, so a failure of
    the second is reported as what it is - an image written without its provenance,
    which therefore refuses to reopen until it is saved again.
    """
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise AuthoredImageError("an identified ROM profile is required to save")
    source = Path(source_path)
    output = Path(output_path)
    manifest_path = manifest_path_for(output)
    staging_output = staging_path(output)
    staging_manifest = staging_path(manifest_path)
    # The source is an input on every path and an output on none: refuse before
    # anything is deleted or emitted, including the derived and staging names.
    refuse_source_alias(
        source,
        (
            ("requested output", output),
            ("provenance manifest", manifest_path),
            ("temporary image", staging_output),
            ("temporary manifest", staging_manifest),
        ),
    )
    if not source.is_file():
        raise AuthoredImageError(f"the source ROM is not readable: {source}")
    if hashlib.sha256(source.read_bytes()).hexdigest() != canonical_sha256:
        raise AuthoredImageError(
            "the source ROM is not the canonical image this editor builds from"
        )
    # `base` is the image the plan is computed against and the image the emitted
    # bytes are diffed against, so its identity is re-proved here rather than
    # assumed from the caller: a plan built against some other image must not be
    # able to describe this one.
    if hashlib.sha256(base).hexdigest() != canonical_sha256:
        raise AuthoredImageError(
            "the base image is not the canonical image this editor builds from"
        )
    normalized = normalize_changes(changes)
    try:
        plan = write_sdk.plan_changes(
            base,
            normalized,
            profile_id=profile_id,
            base_sha256=canonical_sha256,
        )
    except WriteError as exc:
        raise AuthoredImageError(f"the edit set is not applicable: {exc}") from exc

    staging_output.unlink(missing_ok=True)
    staging_manifest.unlink(missing_ok=True)
    try:
        manifest = write_sdk.emit_image(
            source, staging_output, plan, manifest_path=staging_manifest
        )
        data = staging_output.read_bytes()
        changed_offsets = verify_emitted_image(base, data, normalized, manifest)
        verified = verify(data, normalized)
    except BaseException:
        # Nothing at the destination was touched, and a file this save just
        # created at a temporary path is not left behind.
        staging_output.unlink(missing_ok=True)
        staging_manifest.unlink(missing_ok=True)
        raise
    if hashlib.sha256(source.read_bytes()).hexdigest() != canonical_sha256:
        staging_output.unlink(missing_ok=True)
        staging_manifest.unlink(missing_ok=True)
        raise AuthoredImageError("the source ROM changed while it was being saved")
    try:
        os.replace(staging_output, output)
        try:
            os.replace(staging_manifest, manifest_path)
        except OSError as exc:
            raise AuthoredImageError(
                f"the new ROM was written to {output}, but its provenance could not "
                f"be published to {manifest_path}: {exc}. Save again to a writable "
                "destination to give it provenance."
            ) from exc
    finally:
        # The staging paths are cleaned on every outcome, including a failed publish.
        staging_output.unlink(missing_ok=True)
        staging_manifest.unlink(missing_ok=True)
    return AuthoredImageSave(
        output_path=output,
        manifest_path=manifest_path,
        output_sha256=manifest.output_sha256,
        output_size=manifest.output_size,
        no_op=plan.is_noop,
        changes=normalized,
        changed_offsets=changed_offsets,
        verified=verified,
    )


# --- provenance verification -------------------------------------------------


@dataclass(frozen=True, slots=True)
class DeclaredChange:
    """One declared fixed-width change, structurally checked and domain-neutral."""

    owner: str
    offset: int
    old: bytes
    new: bytes


@dataclass(frozen=True, slots=True)
class AuthoredChange(Generic[TARGET]):
    """A declared change plus the domain's own identity for it."""

    owner: str
    offset: int
    old: bytes
    new: bytes
    #: Whatever the domain's change checker made of this declaration.
    target: TARGET


@dataclass(frozen=True, slots=True)
class AuthoredImage(Generic[TARGET]):
    """A verified authored derivative: the canonical image plus declared changes."""

    path: Path
    manifest_path: Path
    profile_id: str
    #: The canonical image this derivative derives from, by SHA-256. The profile
    #: identity the manifest names must be the profile *of this image*.
    canonical_sha256: str
    output_sha256: str
    changes: tuple[AuthoredChange[TARGET], ...]
    #: The reconstructed canonical image, proven equal to the canonical image by
    #: SHA-256. Every accepted reader runs against these bytes.
    canonical_image: bytes


def _load_manifest(manifest_path: Path) -> dict:
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # A document that cannot be read or decoded is not a readable manifest,
        # and saying so here is what keeps a user-chosen file from reaching the
        # caller as an unhandled decoding error.
        raise AuthoredImageError(
            f"no readable DragonByte Z provenance manifest beside this ROM "
            f"({manifest_path.name}): {exc}"
        ) from exc
    try:
        document = json.loads(text)
    except (json.JSONDecodeError, RecursionError) as exc:
        # RecursionError covers a pathologically nested array or object, which is
        # a malformed document rather than a crash this layer should pass on.
        raise AuthoredImageError(f"malformed provenance manifest: {exc}") from exc
    if not isinstance(document, dict):
        raise AuthoredImageError("malformed provenance manifest: not a JSON object")
    return document


def _canonical_base(document: dict, canonical_sha256: str) -> tuple[str, str]:
    base = document.get("base")
    if not isinstance(base, dict):
        raise AuthoredImageError("malformed provenance manifest: no base identity")
    sha256 = base.get("sha256")
    profile_id = base.get("profile_id")
    if sha256 != canonical_sha256:
        raise AuthoredImageError(
            "the manifest's canonical base is not the expected canonical image"
        )
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise AuthoredImageError("the manifest names no base profile")
    return sha256, profile_id


def _output_identity(document: dict, data: bytes) -> str:
    output = document.get("output")
    if not isinstance(output, dict):
        raise AuthoredImageError("malformed provenance manifest: no output identity")
    declared = output.get("sha256")
    actual = hashlib.sha256(data).hexdigest()
    if declared != actual:
        raise AuthoredImageError(
            f"the image does not match its provenance: manifest says {declared}, "
            f"the file is {actual}"
        )
    if output.get("size") != len(data):
        raise AuthoredImageError(
            f"the image does not match its provenance: manifest says {output.get('size')} "
            f"bytes, the file is {len(data)}"
        )
    return actual


def _field(value: object, name: str, offset: int, field_bytes: int) -> bytes:
    if not isinstance(value, str) or len(value) != field_bytes * 2:
        raise AuthoredImageError(
            f"a declared change at 0x{offset:08X} has a bad {name} value: {value!r}"
        )
    try:
        field = bytes.fromhex(value)
    except ValueError as exc:
        raise AuthoredImageError(
            f"a declared change at 0x{offset:08X} has a bad {name} value: {value!r}"
        ) from exc
    if len(field) != field_bytes:
        raise AuthoredImageError(
            f"a declared change at 0x{offset:08X} has a bad {name} width"
        )
    return field


def _declared_changes(
    document: dict, field_bytes: int, expected_reason: str
) -> tuple[DeclaredChange, ...]:
    """Parse and structurally check the manifest's change list.

    Purely structural: an owner string is carried through opaque, because what it
    names is the domain's question, not this module's.
    """
    changes = document.get("changes")
    if not isinstance(changes, list) or not changes:
        raise AuthoredImageError("the manifest declares no changes")
    declared: list[DeclaredChange] = []
    seen: set[int] = set()
    changed_bytes = 0
    for change in changes:
        if not isinstance(change, dict):
            raise AuthoredImageError(
                "malformed provenance manifest: a change is not an object"
            )
        owner = change.get("owner")
        if not isinstance(owner, str) or not owner:
            raise AuthoredImageError("malformed provenance manifest: a change names no owner")
        if change.get("reason") != expected_reason:
            raise AuthoredImageError(
                f"the manifest declares an unsupported change reason: {change.get('reason')!r}"
            )
        if change.get("size") != field_bytes:
            raise AuthoredImageError(
                f"a declared change must be {field_bytes} bytes, not {change.get('size')!r}"
            )
        offset = change.get("offset")
        if type(offset) is not int or offset < 0 or offset % field_bytes:
            raise AuthoredImageError(f"a declared change has an unaligned offset: {offset!r}")
        if offset in seen:
            raise AuthoredImageError(
                f"two declared changes write the same field at 0x{offset:08X}"
            )
        seen.add(offset)
        old = _field(change.get("old"), "old", offset, field_bytes)
        new = _field(change.get("new"), "new", offset, field_bytes)
        if old == new:
            raise AuthoredImageError(
                f"a declared change at 0x{offset:08X} changes nothing"
            )
        changed_bytes += sum(1 for before, after in zip(old, new) if before != after)
        declared.append(DeclaredChange(owner=owner, offset=offset, old=old, new=new))
    declared_bytes = document.get("changed_byte_count")
    if declared_bytes != changed_bytes:
        raise AuthoredImageError(
            f"the manifest declares {declared_bytes!r} changed byte(s) but its own "
            f"changes account for {changed_bytes}"
        )
    return tuple(declared)


def _reconstruct_canonical(
    data: bytes, declared: tuple[DeclaredChange, ...], canonical_sha256: str
) -> bytes:
    """Undo the declared changes and require the result to be the canonical image.

    This is the decisive check for every domain: it bounds an accepted derivative
    to the canonical image plus exactly the declared fields, so an arbitrary
    modified image cannot pass, and it needs no copy of the canonical file - the
    canonical bytes are reconstructed from the derivative itself.
    """
    rebuilt = bytearray(data)
    for change in declared:
        end = change.offset + len(change.old)
        if end > len(rebuilt):
            raise AuthoredImageError(
                f"a declared change at 0x{change.offset:08X} lies outside the image"
            )
        rebuilt[change.offset : end] = change.old
    digest = hashlib.sha256(rebuilt).hexdigest()
    if digest != canonical_sha256:
        raise AuthoredImageError(
            "the image is not the canonical ROM plus the changes its manifest declares "
            f"(reconstructed SHA-256 {digest})"
        )
    return bytes(rebuilt)


def _check_declared_values(data: bytes, declared: tuple[DeclaredChange, ...]) -> None:
    """The image must actually carry each declared replacement.

    Reconstruction alone would accept a file that holds some *third* value in a
    declared field - restoring the declared ``old`` bytes would still reproduce
    the canonical image. A derivative is the canonical image plus its declared
    changes, so every declared field must hold the declared new bytes.
    """
    for change in declared:
        end = change.offset + len(change.new)
        if data[change.offset : end] != change.new:
            raise AuthoredImageError(
                f"the image does not carry the declared value at 0x{change.offset:08X}"
            )


def verify_authored_image(
    image_path: str | Path,
    *,
    canonical_sha256: str,
    field_bytes: int,
    expected_reason: str,
    check_changes: Callable[
        [tuple[DeclaredChange, ...], bytes, bytes], tuple[TARGET, ...]
    ],
    manifest_path: str | Path | None = None,
) -> AuthoredImage[TARGET]:
    """Prove that a non-canonical image is a derivative this tool authored.

    The canonical image itself is accepted by identity elsewhere, before any
    manifest is consulted; this function is the one path for an image that is
    *not* canonical.

    `check_changes` is the domain's half: it receives the structurally checked
    declarations, the reconstructed canonical image and the derivative's own
    bytes, and returns one typed target per declaration - or raises to refuse the
    whole document. It is called exactly once, so a domain that needs a reader or
    a writer over the canonical image builds it once per verification rather than
    once per declared change.

    Raises :class:`AuthoredImageError` for anything that is not: no manifest, a
    malformed or unsupported manifest, a base that is not the canonical image, a
    file that does not match its declared output, a change that is structurally
    unsupported, or a file that is not the canonical image plus exactly its
    declared changes.
    """
    path = Path(image_path)
    document_path = (
        Path(manifest_path) if manifest_path is not None else manifest_path_for(path)
    )
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise AuthoredImageError(f"cannot read {path}: {exc}") from exc

    document = _load_manifest(document_path)
    if (
        type(document.get("schema_version")) is not int
        or document["schema_version"] != SUPPORTED_SCHEMA_VERSION
    ):
        raise AuthoredImageError(
            f"unsupported provenance schema {document.get('schema_version')!r}; "
            f"this build understands {SUPPORTED_SCHEMA_VERSION}"
        )
    base_sha256, profile_id = _canonical_base(document, canonical_sha256)
    output_sha256 = _output_identity(document, data)
    declared = _declared_changes(document, field_bytes, expected_reason)
    canonical_image = _reconstruct_canonical(data, declared, canonical_sha256)
    _check_declared_values(data, declared)
    targets = check_changes(declared, canonical_image, data)
    if len(targets) != len(declared):
        raise AuthoredImageError(
            f"the change checker answered for {len(targets)} of {len(declared)} "
            "declared changes"
        )
    return AuthoredImage(
        path=path,
        manifest_path=document_path,
        profile_id=profile_id,
        canonical_sha256=base_sha256,
        output_sha256=output_sha256,
        changes=tuple(
            AuthoredChange(
                owner=change.owner,
                offset=change.offset,
                old=change.old,
                new=change.new,
                target=target,
            )
            for change, target in zip(declared, targets)
        ),
        canonical_image=canonical_image,
    )
