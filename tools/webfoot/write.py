"""Attributable, validated writes into a NEW ROM image.

TOOLKIT-001. This is the smallest primitive that later transaction, build and
patch systems can extend, and it exists to make one guarantee testable:

    every emitted byte change is attributable to a semantic owner.

Design notes, because each of these is load-bearing rather than incidental:

**The canonical ROM is an input on every path and an output on none.** The
input is read, identified and hash-checked; the output is a separate image.
`emit_image` never opens the source for writing, and the caller-facing API has
no in-place mode to reach for by mistake.

**Codecs stay pure.** All file access lives here. `webfoot.formats.stat_tables`
receives bytes and returns bytes, so the same codec will work unchanged when
the byte source is a decomp tree rather than a ROM - which is the abstraction
ARCH-TOOL-001 requires and the reason not to let I/O leak downward.

**Validation is a distinct step before emission.** `plan_changes` refuses a
change it cannot justify; nothing reaches an output image until every change
has been checked for bounds, size agreement and overlap. Kaitai Struct v0.11
reached the same conclusion from the other direction: its `_write()` throws
unless `_check()` ran after the last edit.

**A no-op emit is byte-identical.** Emitting with zero changes reproduces the
input exactly, verified by SHA-256. That is the first reproducible-build
invariant this project has, and every future build step inherits it.

Allocation and graph rewriting live above this module in TOOLKIT-003. They
compile into fixed-length overwrites of the original image; this layer still
owns no content format or allocation policy. Publication stages complete files
and rolls back links on caught failures; it is not a crash-recovery journal.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

from .rom import RomReadError
from .layout import Reference, RomRange


class WriteError(ValueError):
    """Base error for planning or emitting a ROM modification."""


class ChangeValidationError(WriteError):
    """Raised when a planned change cannot be justified against the base image."""


class OverlappingChangeError(ChangeValidationError):
    """Raised when two planned changes would write the same byte.

    Two owners writing one byte means at least one of them is wrong, and
    whichever landed last would silently win. Refusing is the only safe
    outcome, and it is cheap here because nothing has been written yet.
    """


@dataclass(frozen=True, slots=True)
class ByteChange:
    """One contiguous, fully attributed overwrite.

    `old` and `new` are both retained so the manifest is self-describing: a
    reader can verify the change applied to the base it claims, and can invert
    it, without consulting either image.

    `owner` is the semantic identity responsible - `"enemy:434"`, not an
    address. That is what makes the manifest answer "which edit changed these
    bytes" rather than merely "these bytes differ".
    """

    offset: int
    old: bytes
    new: bytes
    owner: str
    reason: str

    def __post_init__(self) -> None:
        if type(self.offset) is not int or self.offset < 0:
            raise ChangeValidationError("change offset must be a non-negative integer")
        if len(self.old) != len(self.new):
            raise ChangeValidationError(
                f"{self.owner}: change at 0x{self.offset:08X} would resize "
                f"{len(self.old)} -> {len(self.new)} bytes; TOOLKIT-001 supports "
                "only fixed-length overwrites; use an anchor relocation plan"
            )
        if not self.old:
            raise ChangeValidationError(f"{self.owner}: empty change at 0x{self.offset:08X}")
        if not self.owner:
            raise ChangeValidationError("every change must name a semantic owner")

    @property
    def size(self) -> int:
        return len(self.old)

    @property
    def end(self) -> int:
        """Exclusive end offset."""
        return self.offset + self.size

    @property
    def is_effective(self) -> bool:
        """False when this change would not alter any byte."""
        return self.old != self.new

    def to_json(self) -> dict:
        return {
            "offset": self.offset,
            "offset_hex": f"0x{self.offset:08X}",
            "size": self.size,
            "old": self.old.hex(),
            "new": self.new.hex(),
            "owner": self.owner,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class ReferenceRewrite:
    reference: Reference
    new_source_file_offset: int
    old_target_file_offset: int
    new_target_file_offset: int

    def to_json(self) -> dict:
        return {**self.reference.to_json(),
                "new_source_file_offset": self.new_source_file_offset,
                "old_target_file_offset": self.old_target_file_offset,
                "new_target_file_offset": self.new_target_file_offset}


@dataclass(frozen=True, slots=True)
class RelocationProvenance:
    anchor: str
    owner: str
    old_range: RomRange
    new_range: RomRange
    alignment: int
    free_region_evidence: str
    references: tuple[ReferenceRewrite, ...]

    def to_json(self) -> dict:
        return {"anchor": self.anchor, "owner": self.owner,
                "old_range": self.old_range.to_json(), "new_range": self.new_range.to_json(),
                "payload_size": self.new_range.size, "alignment": self.alignment,
                "free_region_evidence": self.free_region_evidence,
                "references_rewritten": [r.to_json() for r in self.references]}


@dataclass(frozen=True, slots=True)
class WritePlan:
    """A validated set of changes against one identified base image.

    Holding the base identity here is what lets `emit_image` refuse to apply a
    plan to the wrong ROM. A plan is only meaningful against the bytes it was
    computed from.
    """

    base_profile_id: str
    base_sha256: str
    base_size: int
    changes: tuple[ByteChange, ...]
    relocations: tuple[RelocationProvenance, ...] = ()

    @property
    def effective_changes(self) -> tuple[ByteChange, ...]:
        return tuple(c for c in self.changes if c.is_effective)

    @property
    def is_noop(self) -> bool:
        return not self.effective_changes

    @property
    def changed_byte_count(self) -> int:
        return sum(
            sum(1 for a, b in zip(c.old, c.new) if a != b)
            for c in self.effective_changes
        )


@dataclass(frozen=True, slots=True)
class ProjectProvenance:
    """Which authored project produced a build. TOOLKIT-002.

    Deliberately just a name and a format version. A path would make the
    manifest machine-specific and two identical builds would stop producing
    identical manifests; a timestamp would do the same. The base and output
    hashes already recorded alongside this are what actually identify the
    build, and they are reproducible.
    """

    name: str
    format_version: int

    def to_json(self) -> dict:
        return {"name": self.name, "format_version": self.format_version}


@dataclass(frozen=True, slots=True)
class WriteManifest:
    """Machine-readable provenance for one emitted image.

    Enough, on its own, to answer: which base, which profile, which output,
    which bytes changed, from what to what, and because of which semantic edit.
    """

    base_profile_id: str
    base_sha256: str
    output_sha256: str
    output_size: int
    changes: tuple[ByteChange, ...]
    #: Set by a project build; absent for a direct `stats set` edit, which has
    #: no project. TOOLKIT-002.
    project: ProjectProvenance | None = None
    relocations: tuple[RelocationProvenance, ...] = ()

    def to_json(self) -> dict:
        document = {
            "schema_version": 1,
            "base": {
                "profile_id": self.base_profile_id,
                "sha256": self.base_sha256,
            },
            "output": {
                "sha256": self.output_sha256,
                "size": self.output_size,
            },
            "changed_byte_count": sum(
                sum(1 for a, b in zip(c.old, c.new) if a != b) for c in self.changes
            ),
            "changes": [c.to_json() for c in self.changes],
        }
        if self.project is not None:
            document["project"] = self.project.to_json()
        if self.relocations:
            document["relocations"] = [r.to_json() for r in self.relocations]
        return document

    def dumps(self) -> str:
        """Deterministic JSON: stable key order, no incidental whitespace.

        Determinism matters because this file is an artefact of the build, and
        a manifest that differs run-to-run would undermine the very property it
        documents.
        """
        return json.dumps(self.to_json(), indent=2, sort_keys=True) + "\n"

    def changes_for(self, owner: str) -> tuple[ByteChange, ...]:
        return tuple(c for c in self.changes if c.owner == owner)


def plan_changes(
    base: bytes,
    changes: Iterable[ByteChange],
    *,
    profile_id: str,
    base_sha256: str,
    relocations: tuple[RelocationProvenance, ...] = (),
) -> WritePlan:
    """Validate `changes` against `base` and return an applicable plan.

    Every change must satisfy all three, and any failure aborts the whole plan
    rather than emitting a partially-applied image:

    1. it lies entirely inside the base image;
    2. its `old` bytes match what the base actually holds there, so a change
       computed against a different image cannot be applied to this one;
    3. it does not overlap another change.
    """
    ordered = sorted(changes, key=lambda c: c.offset)

    for change in ordered:
        if change.end > len(base):
            raise ChangeValidationError(
                f"{change.owner}: change at 0x{change.offset:08X} "
                f"(+{change.size}) extends past the {len(base)}-byte image"
            )
        actual = base[change.offset : change.end]
        if actual != change.old:
            raise ChangeValidationError(
                f"{change.owner}: base bytes at 0x{change.offset:08X} are "
                f"{actual.hex()}, but the change expected {change.old.hex()}; "
                "this plan was computed against a different image"
            )

    for previous, current in zip(ordered, ordered[1:]):
        if current.offset < previous.end:
            raise OverlappingChangeError(
                f"{previous.owner} (0x{previous.offset:08X}+{previous.size}) and "
                f"{current.owner} (0x{current.offset:08X}+{current.size}) "
                "would write the same bytes"
            )

    return WritePlan(
        base_profile_id=profile_id,
        base_sha256=base_sha256,
        base_size=len(base),
        changes=tuple(ordered),
        relocations=relocations,
    )


def apply_plan(base: bytes, plan: WritePlan) -> bytes:
    """Produce the output image. Pure: takes bytes, returns bytes.

    Refuses a plan whose recorded base identity does not match `base`, so a
    plan cannot be silently applied to the wrong image.
    """
    actual_sha256 = hashlib.sha256(base).hexdigest()
    if actual_sha256 != plan.base_sha256:
        raise ChangeValidationError(
            f"plan targets base {plan.base_sha256} but was given {actual_sha256}"
        )
    if len(base) != plan.base_size:
        raise ChangeValidationError(
            f"plan targets a {plan.base_size}-byte base but was given {len(base)}"
        )

    # Public dataclasses can be constructed directly; recheck even no-op plans.
    plan_changes(base, plan.changes, profile_id=plan.base_profile_id,
                 base_sha256=plan.base_sha256)

    if plan.is_noop:
        # Explicit, not incidental: a no-op must reproduce the input exactly.
        return bytes(base)

    out = bytearray(base)
    for change in plan.changes:
        out[change.offset : change.end] = change.new
    result = bytes(out)
    if len(result) != len(base):
        raise AssertionError("internal error: emitted image changed size")
    return result


def emit_image(
    base_path: str | Path,
    output_path: str | Path,
    plan: WritePlan,
    *,
    manifest_path: str | Path | None = None,
    project: ProjectProvenance | None = None,
) -> WriteManifest:
    """Read `base_path`, apply `plan`, write `output_path`, return provenance.

    The base is opened read-only and its identity is re-checked after the read,
    mirroring `webfoot.rom.identify_rom`, so a ROM that changes underneath us is
    an error rather than a silent corruption. Refusing to overwrite an existing
    output is deliberate: a build that clobbers its own previous artefact makes
    "did this run produce that file" unanswerable.
    """
    source = Path(base_path)
    destination = Path(output_path)

    # Order matters: the input path also exists, so the same-path check has to
    # run first or writing over the input would be reported as an ordinary
    # overwrite and would name the wrong rule to the caller.
    if source.resolve() == destination.resolve():
        raise WriteError(
            "refusing to write the output over the input image; the canonical "
            "ROM is read-only"
        )
    if destination.exists():
        raise WriteError(
            f"refusing to overwrite an existing output image: {destination}"
        )

    manifest_destination = Path(manifest_path) if manifest_path is not None else None
    if manifest_destination is not None:
        if manifest_destination.resolve() in (source.resolve(), destination.resolve()):
            raise WriteError("manifest must not alias the input or output image")
        if manifest_destination.exists():
            raise WriteError("refusing to overwrite an existing manifest")

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        base = stream.read()
        after = os.fstat(stream.fileno())
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise RomReadError(f"base ROM changed while it was being read: {source}")
    path_after = source.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        path_after.st_dev, path_after.st_ino, path_after.st_size, path_after.st_mtime_ns
    ):
        raise RomReadError(f"base ROM path changed while it was being read: {source}")

    output = apply_plan(base, plan)

    manifest = WriteManifest(
        base_profile_id=plan.base_profile_id,
        base_sha256=plan.base_sha256,
        output_sha256=hashlib.sha256(output).hexdigest(),
        output_size=len(output),
        changes=plan.effective_changes,
        project=project,
        relocations=plan.relocations,
    )
    # Stage complete files first. Publish using exclusive links: never replace
    # a raced destination. Publish image last; roll back our links on failure.
    artifacts = []
    if manifest_destination is not None:
        artifacts.append((manifest_destination, manifest.dumps().encode("utf-8")))
    artifacts.append((destination, output))
    staged = []
    published = []
    try:
        for path, data in artifacts:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".webfoot-", delete=False) as stream:
                temporary = Path(stream.name)
                staged.append((temporary, path))
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        for temporary, path in staged:
            os.link(temporary, path)
            published.append((temporary, path))
    except BaseException:
        for temporary, path in reversed(published):
            if path.exists() and os.path.samefile(temporary, path):
                path.unlink()
        raise
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    return manifest
