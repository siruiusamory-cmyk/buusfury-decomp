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

**This module owns output-path safety, and its policies stay separate.** The one
question every writer must answer - "may this path be written?" - is answered by
two explicit primitives rather than one predicate with hidden semantics:
:func:`ensure_not_source_alias` refuses a destination that *is* the verified
input (by filesystem identity, not string spelling) and
:func:`ensure_new_destination` refuses a destination that already exists. They
are deliberately not collapsed: a caller can be allowed to replace an existing
artefact while never being allowed to touch its own source. PNG and other
artefact exporters call the same primitives `emit_image` does, so no writer
re-derives filesystem logic or loses the invariant by asking nobody.

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
from typing import Iterable, Sequence

from .rom import RomReadError
from .layout import Reference, RomRange


class WriteError(ValueError):
    """Base error for planning or emitting a ROM modification."""


class OutputPathError(WriteError):
    """A destination path is refused by the shared output-path policies.

    Distinct from `ChangeValidationError` because nothing about the plan or the
    image content is wrong: the caller named a place to write that the toolkit
    will not write to. It still derives from `WriteError`, so a caller that
    already refuses a write with one `except WriteError` keeps refusing this one.
    """


# --- output-path safety ------------------------------------------------------
#
# One owner for "may this destination be written?". Before these lived here, the
# same question was answered independently - and differently - by `emit_image`
# (resolved-path comparison), `authored_image.refuse_source_alias` (resolved-path
# set) and, for the PNG export path, by nobody at all, which let
# `webfoot graphics export --out <the same file as the ROM>` replace the verified
# input with a PNG and report success. Every writer now asks this module.


def _same_existing_file(left: Path, right: Path) -> bool:
    """Whether two paths name one existing file, by filesystem identity.

    `os.path.samefile` compares the operating system's own identity for the file
    (device plus inode on POSIX, volume serial plus file index on Windows), which
    is the only comparison that catches a **hard link**: two directory entries
    with unrelated names that share one inode, where no amount of path
    normalisation can help because the names really are different names.

    Returns False when either path cannot be stat'd - most importantly when the
    destination does not exist yet, which is the ordinary case for an export.
    """
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def _same_path_spelling(left: Path, right: Path) -> bool:
    """Whether two path strings denote the same location once resolved.

    `resolve()` makes a relative spelling absolute, folds `.` and `..`, expands
    the 8.3 short form, and follows junctions and symlinks in every component
    that exists on disk - so `/tmp/./a.png`, `../tmp/a.png` and a path through a
    junction all compare equal. `normcase` then folds case and separators on
    Windows (`C:\\A\\B.PNG` equals `c:/a/b.png`), where the filesystem is
    case-insensitive, and is the identity on POSIX, where it is not.

    This is the half of the comparison that still works when the destination
    does not exist, since `samefile` then has no file to compare.
    """
    return os.path.normcase(str(left.resolve())) == os.path.normcase(
        str(right.resolve())
    )


def paths_are_the_same_file(left: str | Path, right: str | Path) -> bool:
    """Whether two paths denote the same file on this filesystem.

    True for the identical path, for two spellings of one path (relative or
    absolute, case- or separator-varied on Windows, through a junction or
    symlink), and for a **hard-link alias** - two names sharing one file - which
    requires the operating system's file identity rather than any comparison of
    the path strings.

    The public predicate behind the refusal policies below; exposed so a caller
    that needs the answer rather than the refusal (a GUI enabling a button, a
    report) reads the same rule instead of re-deriving it.
    """
    left, right = Path(left), Path(right)
    if _same_path_spelling(left, right):
        return True
    return _same_existing_file(left, right)


def ensure_not_source_alias(source: str | Path, destination: str | Path) -> None:
    """Refuse a `destination` that is the `source` file, or any filesystem alias of it.

    The invariant: **a source is an input on every path and an output on none.**
    The check is deliberately first and total - it runs before the caller creates
    a parent directory, opens the destination, or truncates anything - so a
    refused export leaves the source byte-identical and reports why.

    The message carries both halves deliberately: it names the rule ("refusing to
    write the output over the input image"), the reason ("the canonical ROM is
    read-only", which `docs/ROM_SAFETY.md` states as the permanent rule) and the
    consequence ("the source is an input on every path and can never be an output
    destination"). Callers keyed on the older wording keep matching rather than
    silently losing a regression assertion.

    Raises `OutputPathError`, which is a `WriteError` and therefore a
    `ValueError`: existing CLI call sites already turn it into a non-zero exit
    with the message on stderr, and a GUI boundary already catches the family.
    """
    if paths_are_the_same_file(source, destination):
        raise OutputPathError(
            f"refusing to write the output over the input image: {destination} is "
            f"the same file as the source {source}, and the canonical ROM is "
            "read-only; the source is an input on every path and can never be an "
            "output destination"
        )


def ensure_new_destination(destination: str | Path) -> None:
    """Refuse a destination that already exists.

    Separate from :func:`ensure_not_source_alias` on purpose: this is the
    overwrite policy, not the source-safety invariant. `emit_image` applies both,
    because a build that clobbers its own previous artefact makes "did this run
    produce that file" unanswerable. A caller with a legitimately different
    overwrite policy can take the source-alias invariant on its own.
    """
    if Path(destination).exists():
        raise OutputPathError(
            f"refusing to overwrite an existing output: {destination}"
        )


class ChangeValidationError(WriteError):
    """Raised when a planned change cannot be justified against the base image."""


class OverlappingChangeError(ChangeValidationError):
    """Raised when two planned changes would write the same byte.

    Two owners writing one byte means at least one of them is wrong, and
    whichever landed last would silently win. Refusing is the only safe
    outcome, and it is cheap here because nothing has been written yet.
    """


@dataclass(frozen=True, slots=True)
class GeneratedAllocationProvenance:
    """Why one generated-image span exists in this otherwise canonical ROM."""

    domain: str
    resource: str
    owner: str
    source_range: RomRange
    allocated_range: RomRange
    allocated_rom_address: int
    #: The field that references the allocated span, when there is one. A span
    #: referenced only from a structure the same build materializes - an authored
    #: layer record above canonical EOF, whose address the allocator chooses - has
    #: no field to name yet at the moment of allocation, and records ``None``
    #: rather than a fabricated offset. MAP-RESIZE-AND-LAYERS-001.
    pointer_offset: int | None
    expansion_evidence: str

    def owns(self, change: "ByteChange") -> bool:
        """Whether this allocator-issued span authorizes this appended write."""
        return (
            self.owner == change.owner
            and self.allocated_range.start.value <= change.offset
            and change.end <= self.allocated_range.end
        )

    def to_json(self) -> dict:
        return {
            "domain": self.domain,
            "resource": self.resource,
            "owner": self.owner,
            "source_range": self.source_range.to_json(),
            "allocated_range": self.allocated_range.to_json(),
            "allocated_rom_address": self.allocated_rom_address,
            "allocated_rom_address_hex": f"0x{self.allocated_rom_address:08X}",
            "allocation_class": "generated_expansion",
            "pointer_offset": self.pointer_offset,
            "pointer_offset_hex": (
                f"0x{self.pointer_offset:08X}"
                if self.pointer_offset is not None
                else None
            ),
            "expansion_evidence": self.expansion_evidence,
        }


@dataclass(frozen=True, slots=True)
class GeneratedImage:
    """A deterministic append-only image shape for a generated ROM.

    This is deliberately a write-time property, not a retail-ROM profile size.
    The source remains the exact canonical image named by ``WritePlan``; bytes
    after it are synthesized from one explicit padding value before any change
    is validated or written.
    """

    output_size: int
    padding_byte: int
    expansion_range: RomRange
    expansion_evidence: str
    allocated_spans: tuple[RomRange, ...] = ()

    def __post_init__(self) -> None:
        if type(self.output_size) is not int or self.output_size <= 0:
            raise ChangeValidationError("generated image size must be positive")
        if type(self.padding_byte) is not int or not 0 <= self.padding_byte <= 0xFF:
            raise ChangeValidationError("generated image padding must be one byte")
        if not self.expansion_evidence:
            raise ChangeValidationError("generated expansion requires evidence")

    def materialize(self, canonical: bytes) -> bytes:
        if len(canonical) > self.output_size:
            raise ChangeValidationError(
                f"generated image is {self.output_size} bytes but canonical input is "
                f"{len(canonical)} bytes"
            )
        if self.expansion_range.start.value != len(canonical):
            raise ChangeValidationError("generated expansion must begin at canonical EOF")
        if self.expansion_range.end != self.output_size:
            raise ChangeValidationError("generated expansion must end at generated image EOF")
        return canonical + bytes([self.padding_byte]) * (self.output_size - len(canonical))

    def contains_allocated(self, change: "ByteChange") -> bool:
        return any(
            span.start.value <= change.offset and change.end <= span.end
            for span in self.allocated_spans
        )

    def to_json(self) -> dict:
        return {
            "output_size": self.output_size,
            "padding_byte": self.padding_byte,
            "expansion_range": self.expansion_range.to_json(),
            "expansion_evidence": self.expansion_evidence,
            "allocated_spans": [span.to_json() for span in self.allocated_spans],
        }


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
class DialogueEditProvenance:
    """Why one durable dialogue handle changed, and everything that moved with it.

    DIALOGUE-VARIABLE-LENGTH-001. A compressed-dialogue replacement used to be a
    fixed-length overwrite, so the record's durable identity never moved and the
    bytes said everything there was to say. Once a replacement may change the
    record's decoded length, the *identity* changes too - the handle is
    re-authored and every record the growth displaces is re-authored with it -
    and that is a fact no byte diff can recover after the fact.

    This record is deliberately part of the existing manifest document rather
    than a third sidecar: `WriteManifest` already answers "which base, which
    output, which bytes, because of which semantic edit", and this answers the
    same question one level down, where the semantic edit is a dialogue record.
    """

    #: The project's semantic identity for the record (`goku-greeting`).
    resource: str
    #: The build-domain owner, as every other change attributes it.
    owner: str
    #: The container/selector the record lives in.
    selector: int
    old_handle: int
    new_handle: int
    old_decoded_start: int
    new_decoded_start: int
    old_decoded_length: int
    new_decoded_length: int
    #: How many OTHER records the growth displaced inside the container.
    affected_record_count: int
    #: How many distinct durable handles those displaced records carried.
    affected_handle_count: int
    #: How many ROM words were repointed to a re-authored handle.
    reference_site_count: int
    #: Packed bytes the container occupied before and after the rebuild.
    old_packed_size: int
    new_packed_size: int
    #: The container-table word the engine reads for this selector, and its value
    #: after the edit. `pointer_moved` says whether the payload was relocated.
    container_pointer_offset: int
    container_pointer_address: int
    pointer_moved: bool

    def to_json(self) -> dict:
        return {
            "resource": self.resource,
            "owner": self.owner,
            "selector": self.selector,
            "old_handle": f"0x{self.old_handle:08X}",
            "new_handle": f"0x{self.new_handle:08X}",
            "old_decoded_start": self.old_decoded_start,
            "new_decoded_start": self.new_decoded_start,
            "old_decoded_length": self.old_decoded_length,
            "new_decoded_length": self.new_decoded_length,
            "decoded_length_delta": self.new_decoded_length - self.old_decoded_length,
            "affected_record_count": self.affected_record_count,
            "affected_handle_count": self.affected_handle_count,
            "reference_site_count": self.reference_site_count,
            "old_packed_size": self.old_packed_size,
            "new_packed_size": self.new_packed_size,
            "packed_size_delta": self.new_packed_size - self.old_packed_size,
            "container_pointer_offset": self.container_pointer_offset,
            "container_pointer_offset_hex": f"0x{self.container_pointer_offset:06X}",
            "container_pointer_address": self.container_pointer_address,
            "container_pointer_address_hex": f"0x{self.container_pointer_address:08X}",
            "pointer_moved": self.pointer_moved,
        }


@dataclass(frozen=True, slots=True)
class ChunkEditProvenance:
    """MAP-CHUNK-AUTHORING-001. One authored chunk, and everything it moved.

    A chunk this project authored is a resource the canonical image does not
    contain, so no byte diff of the output can recover what it *was*: the
    identity the author gave it, the canonical chunk it started from, the
    screen-entry edits that made it differ, the span the allocator gave it, and
    the map cells that were repointed at it. This record is part of the existing
    manifest document rather than a second manifest family, for the same reason
    :class:`DialogueEditProvenance` is: `WriteManifest` already answers "which
    base, which output, which bytes, because of which semantic edit", and this
    answers it one level down, where the edit is a chunk.

    A build that authored no chunk writes no `chunk_edits` key at all.
    """

    #: The project's semantic identity for the chunk (`chunk:grass-sign`).
    resource: str
    #: The build-domain owner, as every other change attributes it.
    owner: str
    #: Where the body started: the canonical layer cell the template was read
    #: from, as ``map:NNNN/layer:N/chunk:N``.
    template: str
    #: The canonical container address the template resolved to.
    template_address: int
    #: SHA-256 of the 0x800 decoded screen-entry body that was materialized.
    body_sha256: str
    #: The encoded container's size, and the span the allocator reserved.
    container_size: int
    allocation_file_offset: int
    allocation_size: int
    #: The GBA address the map cells were repointed at.
    rom_address: int
    #: Whether that address lies above the canonical image, and the evidence the
    #: allocator used to authorize the expansion.
    expanded: bool
    expansion_evidence: str
    #: Every screen-entry cell the author changed, row-major.
    edits: tuple["ChunkEntryProvenance", ...]
    #: Every map cell repointed at this chunk, row-major by map then layer then
    #: cell, with the pointer each held before.
    placements: tuple["ChunkPlacementProvenance", ...]

    def to_json(self) -> dict:
        return {
            "resource": self.resource,
            "owner": self.owner,
            "template": self.template,
            "template_address": self.template_address,
            "template_address_hex": f"0x{self.template_address:08X}",
            "body_sha256": self.body_sha256,
            "container_size": self.container_size,
            "allocation_file_offset": self.allocation_file_offset,
            "allocation_file_offset_hex": f"0x{self.allocation_file_offset:08X}",
            "allocation_size": self.allocation_size,
            "rom_address": self.rom_address,
            "rom_address_hex": f"0x{self.rom_address:08X}",
            "expanded": self.expanded,
            "expansion_evidence": self.expansion_evidence,
            "edit_count": len(self.edits),
            "edits": [edit.to_json() for edit in self.edits],
            "placement_count": len(self.placements),
            "placements": [placement.to_json() for placement in self.placements],
        }


@dataclass(frozen=True, slots=True)
class ChunkEntryProvenance:
    """One screen-entry cell the author changed inside an authored chunk."""

    row: int
    column: int
    #: The entry the template held, and the entry the author put there.
    prior: int
    entry: int

    def to_json(self) -> dict:
        return {
            "row": self.row,
            "column": self.column,
            "prior": f"0x{self.prior:04X}",
            "entry": f"0x{self.entry:04X}",
        }


@dataclass(frozen=True, slots=True)
class ChunkPlacementProvenance:
    """One map cell repointed from a canonical chunk to an authored one."""

    map_index: int
    layer_slot: int
    cell: int
    #: The pointer the canonical image held at this cell.
    previous: int
    #: File offset of the four-byte pointer field that was rewritten.
    offset: int
    #: The authored chunk the cell now names.
    chunk: str

    def to_json(self) -> dict:
        return {
            "map_index": self.map_index,
            "layer_slot": self.layer_slot,
            "cell": self.cell,
            "owner": f"map:{self.map_index:04d} layer {self.layer_slot} cell {self.cell}",
            "previous": f"0x{self.previous:08X}",
            "offset": self.offset,
            "offset_hex": f"0x{self.offset:08X}",
            "chunk": self.chunk,
        }


@dataclass(frozen=True, slots=True)
class StructureExtentProvenance:
    """One map-root extent word a structural edit rewrote."""

    axis: str
    offset: int
    previous: int
    authored: int

    def to_json(self) -> dict:
        return {
            "axis": self.axis,
            "offset": self.offset,
            "offset_hex": f"0x{self.offset:08X}",
            "previous": self.previous,
            "authored": self.authored,
        }


@dataclass(frozen=True, slots=True)
class StructureFillProvenance:
    """The chunk a structural record's window initializes a region to.

    ``offsets`` names the window cells that hold the address. A cell offset is
    above canonical EOF - it lies inside the record this same build materializes -
    so it is stated as a field of the allocated span rather than as a canonical
    pointer holder.
    """

    chunk: str
    ordinal: int | None
    address: int
    offsets: tuple[int, ...]

    def to_json(self) -> dict:
        return {
            "chunk": self.chunk,
            "ordinal": self.ordinal,
            "address": self.address,
            "address_hex": f"0x{self.address:08X}",
            "cell_count": len(self.offsets),
            "offsets": list(self.offsets),
        }


@dataclass(frozen=True, slots=True)
class StructureEditProvenance:
    """One authored structural edit as the manifest records it.

    MAP-RESIZE-AND-LAYERS-001. Enough to answer, from the manifest alone, which
    map and layer slot changed, from which grid to which, where the record landed,
    what the map root's own slot field now holds, and which extent words moved. The
    ``authored_*`` fields are additive and answer whether the record is a
    project-authored layer's or a retail layer's, which a resize can be either of.
    """

    #: ``"resize"`` or ``"layer"``.
    kind: str
    #: The durable owner: ``map:NNNN/BGn`` for a resize, ``layer:name`` for an
    #: authored layer.
    owner: str
    map_index: int
    layer_slot: int
    #: The canonical record the header was copied from.
    template_address: int
    retail_columns: int
    retail_rows: int
    columns: int
    rows: int
    #: The root's own layer-slot pointer field and what it held before.
    slot_offset: int
    previous_record_address: int
    record_address: int
    record_size: int
    allocation_file_offset: int
    allocation_size: int
    expanded: bool
    expansion_evidence: str
    record_sha256: str
    fills: tuple[StructureFillProvenance, ...] = ()
    extents: tuple[StructureExtentProvenance, ...] = ()
    #: ``map:NNNN/BGn`` values whose cell content this record carries.
    cell_entries: int = 0
    #: MAP-RESIZE-AND-LAYERS-001. The ``layer:name`` identity when the record is a
    #: PROJECT-AUTHORED layer's - created by this project, or that layer grown by a
    #: resize - and "" when the record is a retail layer's own resize. This is what
    #: tells a reviewer which of the two a resize is, without reading the project.
    authored_layer: str = ""
    #: The grid the authored layer was CREATED at, which is the grid a resize of it
    #: grows from. 0/0 when the record is a retail layer's.
    authored_columns: int = 0
    authored_rows: int = 0

    @property
    def authored(self) -> bool:
        """Whether the record belongs to a project-authored layer."""
        return bool(self.authored_layer)

    def to_json(self) -> dict:
        return {
            "kind": self.kind,
            "owner": self.owner,
            "map_index": self.map_index,
            "layer_slot": self.layer_slot,
            "template_address": self.template_address,
            "template_address_hex": f"0x{self.template_address:08X}",
            "retail_columns": self.retail_columns,
            "retail_rows": self.retail_rows,
            "columns": self.columns,
            "rows": self.rows,
            "slot_offset": self.slot_offset,
            "slot_offset_hex": f"0x{self.slot_offset:08X}",
            "previous_record_address": self.previous_record_address,
            "previous_record_address_hex": f"0x{self.previous_record_address:08X}",
            "record_address": self.record_address,
            "record_address_hex": f"0x{self.record_address:08X}",
            "record_size": self.record_size,
            "allocation_file_offset": self.allocation_file_offset,
            "allocation_size": self.allocation_size,
            "expanded": self.expanded,
            "expansion_evidence": self.expansion_evidence,
            "record_sha256": self.record_sha256,
            "cell_entries": self.cell_entries,
            "authored": self.authored,
            "authored_layer": self.authored_layer,
            "authored_columns": self.authored_columns,
            "authored_rows": self.authored_rows,
            "fills": [fill.to_json() for fill in self.fills],
            "extents": [extent.to_json() for extent in self.extents],
        }


@dataclass(frozen=True, slots=True)
class TransitionEditProvenance:
    """One authored transition edit as the manifest records it.

    MAP-WARP-PROJECT-AUTHORING-001. Enough, from the manifest alone, to answer
    the three questions this capability's provenance owes: *which* semantic
    transition changed, which destination it carried and now carries, and which
    positional region it carried and now carries.

    The author-facing identity is ``identity`` - ``map:NNNN/transition:NNNN``,
    the source map plus the array index the engine's own walk assigns. The record's
    file offset is carried beside it as ``file_offset`` for the same reason
    :class:`ChunkEditProvenance` carries ``template_address``: it says which bytes
    moved, and it is deliberately not the identity.

    A field group the author did not edit is reported as ``None``/``""`` rather
    than restated, so the record names the real edit instead of the whole editable
    surface. Only a group that actually differs from the canonical record produces
    a provenance entry at all: a stored pair whose authored value equals its prior
    is a no-op and contributes nothing here.

    ``region`` is the two positional intervals, low/high each, in the record's own
    stored order - ``((first_low, first_high), (second_low, second_high))``. Which
    interval is horizontal, and what the endpoints' unit is, are UNRESOLVED, so no
    axis name is invented here either.
    """

    #: ``map:NNNN/transition:NNNN`` - the semantic identity, never an address.
    identity: str
    source_map: int
    index: int
    #: File offset of the 24-byte record this edit rewrote. Provenance, not identity.
    file_offset: int
    #: ``map:NNNN`` before and after, or "" when the destination was not edited.
    prior_destination: str = ""
    destination: str = ""
    #: The positional region before and after, or None when it was not edited.
    prior_region: tuple[tuple[int, int], tuple[int, int]] | None = None
    region: tuple[tuple[int, int], tuple[int, int]] | None = None
    #: MAP-WARP-RUNTIME-EDIT-001. The measured arrival point before and after, as
    #: ``(x, y)``, or None when that side has no authored arrival. Whether the
    #: group was touched at all is ``arrival_changed``, because "no authored
    #: arrival" is itself a value a project can set.
    prior_arrival: tuple[int, int] | None = None
    arrival: tuple[int, int] | None = None
    arrival_changed: bool = False
    #: MAP-WARP-ARRIVAL-SEMANTICS-001. The ``+0x10`` byte before and after, whole.
    #: The low two bits are the candidate facing decode; the high bits are
    #: UNRESOLVED and are carried verbatim, which is why this is the byte and not
    #: a direction.
    prior_facing_raw: int | None = None
    facing_raw: int | None = None
    facing_changed: bool = False

    @property
    def destination_changed(self) -> bool:
        return self.destination != ""

    @property
    def region_changed(self) -> bool:
        return self.region is not None

    def to_json(self) -> dict:
        return {
            "identity": self.identity,
            "source_map": self.source_map,
            "index": self.index,
            "file_offset": self.file_offset,
            "file_offset_hex": f"0x{self.file_offset:08X}",
            "destination_changed": self.destination_changed,
            "prior_destination": self.prior_destination,
            "destination": self.destination,
            "region_changed": self.region_changed,
            "prior_region": (
                [list(pair) for pair in self.prior_region]
                if self.prior_region is not None
                else None
            ),
            "region": (
                [list(pair) for pair in self.region]
                if self.region is not None
                else None
            ),
            "arrival_changed": self.arrival_changed,
            "prior_arrival": (
                list(self.prior_arrival) if self.prior_arrival is not None else None
            ),
            "arrival": list(self.arrival) if self.arrival is not None else None,
            "facing_changed": self.facing_changed,
            "prior_facing_raw": self.prior_facing_raw,
            "facing_raw": self.facing_raw,
            # The low two bits gate the door; the high nibble overrides the
            # arrival facing. None means "the record does not state one", which
            # leaves the actor walking the way it already was.
            "facing_gate_direction": (
                self.facing_raw & 0x03 if self.facing_raw is not None else None
            ),
            "facing_arrival_direction": (
                ((self.facing_raw >> 4) - 1)
                if self.facing_raw is not None and (self.facing_raw >> 4)
                else None
            ),
        }


@dataclass(frozen=True, slots=True)
class TransitionRecordFieldProvenance:
    """Where one physical field's bits of a CREATED transition record came from.

    MAP-WARP-CREATE-PROJECT-001. A created record has no canonical bytes, so its
    24 bytes are a composition of three kinds of material, and the ticket requires
    the build to say which is which rather than leaving it to be inferred:

    * **authored** - the project states the value (the region, the destination key,
      the arrival pair, and the high nibble of ``+0x10``);
    * **copied invariant/template** - ``+0x00``'s class/constructor word and
      ``+0x04``'s corpus-invariant word, carried from the template because their
      meanings are UNRESOLVED;
    * **preserved unresolved** - ``+0x13``, an engine-read field whose meaning is
      UNRESOLVED, copied from the template verbatim.

    ``authored_mask`` states the *bits* the project authored, because exactly one
    field is split: ``+0x10``'s high nibble is the authored arrival facing and its
    low nibble (the door gate and two untraced bits) is the template's. A mask of
    ``0`` means the field was copied whole; an all-ones mask means it was authored
    whole. ``source`` names which of the three kinds the entry is, for a reader that
    should not have to decode the mask to know.
    """

    offset: int
    width: int
    field: str
    source: str
    authored_mask: int

    @property
    def authored_bits(self) -> int:
        return bin(self.authored_mask).count("1")

    def to_json(self) -> dict:
        return {
            "offset": self.offset,
            "offset_hex": f"0x{self.offset:02X}",
            "width": self.width,
            "field": self.field,
            "source": self.source,
            "authored_mask": self.authored_mask,
            "authored_mask_hex": f"0x{self.authored_mask:X}",
        }


@dataclass(frozen=True, slots=True)
class TransitionCreationProvenance:
    """One CREATED transition as the manifest records it.

    MAP-WARP-CREATE-PROJECT-001. A created record is the one transition this build
    emits that has no canonical bytes, so its provenance owes more than an edit's:
    which semantic transition was created and where it landed, which canonical record
    it was initialized from, which field of the canonical enumeration it took, and
    what happened to the root and the pointer array that make it reachable.

    Every address here is provenance and never identity: ``identity`` is
    ``map:NNNN/transition:<name>``, the authored name, and it survives any rebuild
    that re-allocates the record somewhere else.
    """

    #: ``map:NNNN/transition:<name>`` - the durable authored identity.
    identity: str
    source_map: int
    #: The element index in the EXPANDED array the created record occupies. A
    #: build-time fact, deliberately not part of the identity.
    index: int
    #: ``map:NNNN/transition:IIII`` - the canonical record this one was composed over.
    template: str
    template_address: int
    destination: str
    region: tuple[tuple[int, int], tuple[int, int]]
    arrival: tuple[int, int]
    #: The created record's ``+0x10`` byte, whole: the authored high nibble over the
    #: template's own low nibble.
    facing_raw: int
    #: The arrival-facing direction the project stated, or None for "no override".
    facing: int | None
    record_address: int
    record_file_offset: int
    record_size: int
    array_address: int
    array_file_offset: int
    array_size: int
    #: ``root + 0x40``: where the count lives, and what it was and became.
    count_offset: int
    prior_count: int
    count: int
    #: ``root + 0x44``: where the array pointer lives, and what it was and became.
    #: Before the creation it named the CANONICAL array, which is left byte-identical
    #: in place; the expanded array is a new span that carries the same elements plus
    #: the created one.
    array_pointer_offset: int
    prior_array_address: int
    #: The engine-encoded bytes of the two pointer fields, so a manifest reader can
    #: answer "what encoding did this build use" without re-deriving it.
    count_bytes: str
    array_pointer_bytes: str
    record_pointer_bytes: str
    expanded: bool
    expansion_evidence: str
    #: The template's own preserved bytes as the project pinned them, and the live
    #: template's values they were checked against.
    prior_facing_raw: int
    prior_unresolved_raw: int
    #: Every physical field of the 24-byte record and where its bits came from.
    fields: tuple[TransitionRecordFieldProvenance, ...] = ()

    def to_json(self) -> dict:
        return {
            "identity": self.identity,
            "source_map": self.source_map,
            "index": self.index,
            "template": self.template,
            "template_address": self.template_address,
            "template_address_hex": f"0x{self.template_address:08X}",
            "destination": self.destination,
            "region": [list(pair) for pair in self.region],
            "arrival": list(self.arrival),
            "facing_raw": self.facing_raw,
            "facing": self.facing,
            "record_address": self.record_address,
            "record_address_hex": f"0x{self.record_address:08X}",
            "record_file_offset": self.record_file_offset,
            "record_file_offset_hex": f"0x{self.record_file_offset:08X}",
            "record_size": self.record_size,
            "array_address": self.array_address,
            "array_address_hex": f"0x{self.array_address:08X}",
            "array_file_offset": self.array_file_offset,
            "array_file_offset_hex": f"0x{self.array_file_offset:08X}",
            "array_size": self.array_size,
            "count_offset": self.count_offset,
            "count_offset_hex": f"0x{self.count_offset:08X}",
            "prior_count": self.prior_count,
            "count": self.count,
            "array_pointer_offset": self.array_pointer_offset,
            "array_pointer_offset_hex": f"0x{self.array_pointer_offset:08X}",
            "prior_array_address": self.prior_array_address,
            "prior_array_address_hex": f"0x{self.prior_array_address:08X}",
            "count_bytes": self.count_bytes,
            "array_pointer_bytes": self.array_pointer_bytes,
            "record_pointer_bytes": self.record_pointer_bytes,
            "expanded": self.expanded,
            "expansion_evidence": self.expansion_evidence,
            "prior_facing_raw": self.prior_facing_raw,
            "prior_unresolved_raw": self.prior_unresolved_raw,
            "record_fields": [field.to_json() for field in self.fields],
        }


@dataclass(frozen=True, slots=True)
class SpriteAuthoringProvenance:
    """One authored actor sprite as the manifest records it.

    SPRITE-NEW-PROJECT-SURFACE-001. An authored identity and its actor are the
    only structures this build emits that have no canonical bytes at all, so the
    manifest owes the addresses the planners actually chose: which registry the
    identity landed in, which structure and frames it answers through, which
    palette entries it wrote, which object array and record the actor occupies
    and which existing entry its behaviour started from.

    The two payloads are the planners' own ``to_json()`` documents rather than a
    restatement of their fields. They already are the published description of a
    planned identity and a planned actor - the runtime parity record reads the
    same two documents - and a second description here is exactly how two
    statements of one layout drift apart.
    """

    #: ``sprite_identity.AuthoredIdentity.to_json()``.
    identity: dict
    #: ``sprite_attachment.AuthoredMapActor.to_json()``.
    actor: dict

    def to_json(self) -> dict:
        return {"identity": self.identity, "actor": self.actor}


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
    generated_image: GeneratedImage | None = None
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    #: DIALOGUE-VARIABLE-LENGTH-001. Empty for a build that authored no
    #: dialogue record whose durable identity changed.
    dialogue_edits: tuple[DialogueEditProvenance, ...] = ()
    #: MAP-CHUNK-AUTHORING-001. Empty for a build that authored no chunk.
    chunk_edits: tuple[ChunkEditProvenance, ...] = ()
    #: MAP-RESIZE-AND-LAYERS-001. Empty for a build that authored no structure.
    structure_edits: tuple[StructureEditProvenance, ...] = ()
    #: MAP-WARP-PROJECT-AUTHORING-001. Empty for a build that authored no
    #: transition, and also for one whose authored transition values all equal the
    #: canonical record's own - a no-op edit is not an edit.
    transition_edits: tuple[TransitionEditProvenance, ...] = ()
    #: MAP-WARP-CREATE-PROJECT-001. Empty for a build that created no transition.
    transition_creations: tuple[TransitionCreationProvenance, ...] = ()
    #: SPRITE-NEW-PROJECT-SURFACE-001. Empty for a build that authored no new
    #: actor-sprite identity.
    sprite_authoring: tuple[SpriteAuthoringProvenance, ...] = ()

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
    generated_image: GeneratedImage | None = None
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    #: DIALOGUE-VARIABLE-LENGTH-001. Present only when a dialogue record's
    #: durable handle or decoded span changed in this build.
    dialogue_edits: tuple[DialogueEditProvenance, ...] = ()
    #: MAP-CHUNK-AUTHORING-001. Present only when a project-authored chunk was
    #: materialized in this build.
    chunk_edits: tuple[ChunkEditProvenance, ...] = ()
    #: MAP-RESIZE-AND-LAYERS-001. Present only when a project-authored resize or
    #: authored layer was materialized in this build.
    structure_edits: tuple[StructureEditProvenance, ...] = ()
    #: MAP-WARP-PROJECT-AUTHORING-001. Present only when a project's semantic
    #: transition edit actually changed a record's destination or region.
    transition_edits: tuple[TransitionEditProvenance, ...] = ()
    #: MAP-WARP-CREATE-PROJECT-001. Present only when a build materialized a
    #: project-created transition record and the expanded pointer array that
    #: reaches it.
    transition_creations: tuple[TransitionCreationProvenance, ...] = ()
    #: SPRITE-NEW-PROJECT-SURFACE-001. Present only when a build authored a new
    #: actor-sprite identity and attached it to a map actor.
    sprite_authoring: tuple[SpriteAuthoringProvenance, ...] = ()

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
        if self.generated_image is not None:
            document["generated_image"] = self.generated_image.to_json()
        if self.generated_allocations:
            document["generated_allocations"] = [
                allocation.to_json() for allocation in self.generated_allocations
            ]
        if self.dialogue_edits:
            document["dialogue_edits"] = [
                edit.to_json() for edit in self.dialogue_edits
            ]
        if self.chunk_edits:
            document["chunk_edits"] = [edit.to_json() for edit in self.chunk_edits]
        if self.structure_edits:
            document["structure_edits"] = [
                edit.to_json() for edit in self.structure_edits
            ]
        if self.transition_edits:
            document["transition_edits"] = [
                edit.to_json() for edit in self.transition_edits
            ]
        if self.transition_creations:
            document["transition_creations"] = [
                creation.to_json() for creation in self.transition_creations
            ]
        if self.sprite_authoring:
            document["sprite_authoring"] = [
                sprite.to_json() for sprite in self.sprite_authoring
            ]
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
    generated_image: GeneratedImage | None = None,
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = (),
    dialogue_edits: tuple[DialogueEditProvenance, ...] = (),
    chunk_edits: tuple[ChunkEditProvenance, ...] = (),
    structure_edits: tuple[StructureEditProvenance, ...] = (),
    transition_edits: tuple[TransitionEditProvenance, ...] = (),
    transition_creations: tuple[TransitionCreationProvenance, ...] = (),
    sprite_authoring: tuple[SpriteAuthoringProvenance, ...] = (),
) -> WritePlan:
    """Validate `changes` against `base` and return an applicable plan.

    Every change must satisfy all three, and any failure aborts the whole plan
    rather than emitting a partially-applied image:

    1. it lies entirely inside the base image;
    2. its `old` bytes match what the base actually holds there, so a change
       computed against a different image cannot be applied to this one;
    3. it does not overlap another change.

    A caller that can be handed one physical field twice may collapse exact
    duplicates before planning (see
    :func:`tools.webfoot.authored_image.normalize_changes`); a plan that still
    overlaps is refused here.
    """
    if generated_allocations and generated_image is None:
        raise ChangeValidationError(
            "generated allocation provenance requires a generated-image policy"
        )
    if generated_image is not None:
        allocation_spans = tuple(a.allocated_range for a in generated_allocations)
        if set(generated_image.allocated_spans) != set(allocation_spans):
            raise ChangeValidationError(
                "generated image allocation spans must exactly match allocation provenance"
            )
        for allocation in generated_allocations:
            span = allocation.allocated_range
            expansion = generated_image.expansion_range
            if not (expansion.start.value <= span.start.value and span.end <= expansion.end):
                raise ChangeValidationError(
                    f"{allocation.owner}: generated allocation lies outside the profile expansion range"
                )
    planning_image = (generated_image.materialize(base)
                       if generated_image is not None else base)
    ordered = sorted(changes, key=lambda c: c.offset)

    for change in ordered:
        if change.end > len(planning_image):
            raise ChangeValidationError(
                f"{change.owner}: change at 0x{change.offset:08X} "
                f"(+{change.size}) extends past the {len(planning_image)}-byte image"
            )
        actual = planning_image[change.offset : change.end]
        if actual != change.old:
            raise ChangeValidationError(
                f"{change.owner}: base bytes at 0x{change.offset:08X} are "
                f"{actual.hex()}, but the change expected {change.old.hex()}; "
                "this plan was computed against a different image"
            )
        if change.offset < len(base) < change.end:
            raise ChangeValidationError(
                f"{change.owner}: change at 0x{change.offset:08X} straddles canonical EOF"
            )
        if change.offset >= len(base):
            if generated_image is None or not any(
                allocation.owns(change) for allocation in generated_allocations
            ):
                raise ChangeValidationError(
                    f"{change.owner}: generated write at 0x{change.offset:08X} is not "
                    "authorized by its allocator-issued expansion provenance"
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
        generated_image=generated_image,
        generated_allocations=generated_allocations,
        dialogue_edits=tuple(dialogue_edits),
        chunk_edits=tuple(chunk_edits),
        structure_edits=tuple(structure_edits),
        transition_edits=tuple(transition_edits),
        transition_creations=tuple(transition_creations),
        sprite_authoring=tuple(sprite_authoring),
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
    planning_image = (plan.generated_image.materialize(base)
                      if plan.generated_image is not None else base)
    plan_changes(base, plan.changes, profile_id=plan.base_profile_id,
                 base_sha256=plan.base_sha256, generated_image=plan.generated_image,
                 generated_allocations=plan.generated_allocations)

    if plan.is_noop:
        # Explicit, not incidental: a no-op must reproduce the input exactly.
        return bytes(planning_image)

    out = bytearray(planning_image)
    for change in plan.changes:
        out[change.offset : change.end] = change.new
    result = bytes(out)
    if len(result) != len(planning_image):
        raise AssertionError("internal error: emitted image changed size")
    return result


def publish_new_files(artifacts: Sequence[tuple[Path, bytes]]) -> None:
    """Publish complete files that must not already exist, or publish none of them.

    The one owner of "put these bytes on disk as new files". Every file is staged
    beside its destination, flushed and synced, and only then published with an
    exclusive link, so an existing destination is never replaced and a raced
    writer loses rather than silently overwriting someone else's artefact. A
    failure unlinks only the links this call published.

    Files that legitimately replace an existing destination are a different policy
    and belong to `tools.webfoot.project.atomic.replace_document`, which replaces
    through `os.replace`; this function deliberately cannot do that.
    """
    staged: list[tuple[Path, Path]] = []
    published: list[tuple[Path, Path]] = []
    try:
        for path, data in artifacts:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=path.parent, prefix=".webfoot-", delete=False
            ) as stream:
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

    # Order matters: the input path also exists, so the alias check has to run
    # first or writing over the input would be reported as an ordinary overwrite
    # and would name the wrong rule to the caller. Both policies are this
    # module's, shared with every other writer - see `ensure_not_source_alias`.
    ensure_not_source_alias(source, destination)
    # OWNER R3. Identity, not digest: a hardlink or a junction-reached path to a
    # protected ROM is refused here even though its name and its content differ
    # from the source's, and a destination inside a protected input directory is
    # refused however it got there. Runs before `ensure_new_destination` so a
    # protected path is reported as protected rather than as occupied.
    from .destination import refuse_rom_destination

    refuse_rom_destination(source, destination)
    ensure_new_destination(destination)

    manifest_destination = Path(manifest_path) if manifest_path is not None else None
    if manifest_destination is not None:
        if paths_are_the_same_file(manifest_destination, source) or (
            paths_are_the_same_file(manifest_destination, destination)
        ):
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
        generated_image=plan.generated_image,
        generated_allocations=plan.generated_allocations,
        dialogue_edits=plan.dialogue_edits,
        chunk_edits=plan.chunk_edits,
        structure_edits=plan.structure_edits,
        transition_edits=plan.transition_edits,
        transition_creations=plan.transition_creations,
        sprite_authoring=plan.sprite_authoring,
    )
    # Stage complete files first. Publish using exclusive links: never replace
    # a raced destination. Publish image last; roll back our links on failure.
    artifacts = []
    if manifest_destination is not None:
        artifacts.append((manifest_destination, manifest.dumps().encode("utf-8")))
    artifacts.append((destination, output))
    publish_new_files(artifacts)
    return manifest
