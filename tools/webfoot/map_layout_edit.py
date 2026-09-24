"""DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001 - the dominant-layer layout edit session.

This is the product-layer session the Map Browser's EDIT LAYOUT mode drives. It
answers three questions and owns no binary format of its own:

* which maps and layer slots the *proven* writer may touch (the accepted dominant
  chunk-grid form, and only where the layer already contains a second non-null
  chunk to substitute);
* which replacement chunks a selected layer offers - the layer's own existing
  non-null pointers, numbered for a human, never a raw address as the primary
  identity; and
* what a pending edit set would render as, in memory, without touching a byte.

Every write goes through :class:`tools.webfoot.map_layout_write.MapLayoutWriter`,
which accepts only an existing, non-null chunk pointer already used by the same
dominant layer. This module adds no capability beyond that: no new chunks, no
relocation, no resizing, no tile painting, no other layer form.

Saving follows the project's ROM-safety flow - verified base, generated output,
never the input - through the shared authored-image transaction in
:mod:`tools.webfoot.authored_image`, which owns the staging paths, the source-alias
refusals, the publication order and the byte-level verification. What this module
adds to it is the one domain question the shared layer cannot answer: whether the
emitted image carries the requested cell replacements, re-read from the output.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.export import canonical as canon
from tools.export import map_browser as mb
from tools.export import profile_authority
from tools.export import render as render_sdk
from tools.export import webfoot_strict as ws

from . import write as write_sdk
from .authored_image import AuthoredImageError, save_authored_image
from .map_layout_write import MapLayoutWriteError, MapLayoutWriter


class MapLayoutEditError(ValueError):
    """A layout target, replacement, preview or save could not be accepted."""


#: Every error family the accepted READERS raise. Each is an unrelated
#: ``ValueError`` subclass, so catching one leaf would let its siblings escape to
#: the terminal - where this session's only client has no console. The editor
#: translates all of them into its own single public failure type.
_READ_ERRORS = (
    canon.CanonicalError,
    ws.ContainerError,
    render_sdk.RenderError,
    mb.MapBrowserError,
)


#: The only layer form this ticket may edit, and the human names for the forms it
#: may not. Those stay read-only rather than forced into a grid they do not have.
#: Every phrase completes "BGn is ..." in :attr:`LayoutTarget.read_only_reason`.
_READ_ONLY_FORMS = {
    "absent_placeholder": "an empty slot holding no layer",
    "static_graphical_screenblock": "a screen-entry layer, not the dominant chunk grid",
    "static_graphical_terrain_field": (
        "a terrain-field layer, the special graphical form Map 19 uses"
    ),
    "dominant_zero_grid": "a dominant record whose chunk grid has a zero dimension",
    "dominant_partial_zero_grid": (
        "a dominant record whose chunk grid has a zero dimension"
    ),
    "unclassified_handler": "an unclassified layer handler",
}

_EDITABLE_CLASSIFICATION = "dominant"


@dataclass(frozen=True, slots=True)
class LayoutGrid:
    """Pure chunk-cell geometry of one dominant layer.

    A dominant layer's chunk grid is ``columns`` x ``rows`` cells of
    :data:`tools.export.canonical.CHUNK_PIXELS` square pixels each, laid out from
    the layer image's origin - the same origin-aligned placement the accepted
    renderer uses. Keys are row-major cell indices, exactly the order the layer's
    chunk-pointer window stores them in.
    """

    columns: int
    rows: int

    @property
    def cell_count(self) -> int:
        return self.columns * self.rows

    @property
    def width(self) -> int:
        return self.columns * canon.CHUNK_PIXELS

    @property
    def height(self) -> int:
        return self.rows * canon.CHUNK_PIXELS

    def contains(self, cell: object) -> bool:
        return type(cell) is int and 0 <= cell < self.cell_count

    def column_of(self, cell: int) -> int:
        if not self.contains(cell):
            raise MapLayoutEditError(f"chunk cell {cell!r} is outside this grid")
        return cell % self.columns

    def row_of(self, cell: int) -> int:
        if not self.contains(cell):
            raise MapLayoutEditError(f"chunk cell {cell!r} is outside this grid")
        return cell // self.columns

    def cell_at(self, x: int, y: int) -> int | None:
        """The cell covering one pixel of this layer, or None outside it."""
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return None
        return (y // canon.CHUNK_PIXELS) * self.columns + (x // canon.CHUNK_PIXELS)

    def cell_rect(self, cell: int) -> tuple[int, int, int, int]:
        """``(x, y, width, height)`` of one cell in this layer's own pixels."""
        column, row = self.column_of(cell), self.row_of(cell)
        return (
            column * canon.CHUNK_PIXELS,
            row * canon.CHUNK_PIXELS,
            canon.CHUNK_PIXELS,
            canon.CHUNK_PIXELS,
        )


@dataclass(frozen=True, slots=True)
class LayoutCell:
    """One row-major chunk cell of a dominant layer, as the source ROM holds it."""

    cell: int
    column: int
    row: int
    #: The four-byte pointer stored in the canonical image; 0 is the null pointer
    #: the engine's own occupancy test reads as unoccupied.
    pointer: int
    #: File offset of that four-byte field - the exact span one edit rewrites.
    offset: int


@dataclass(frozen=True, slots=True)
class LayoutSlot:
    """One of a root's four layer slots, classified for editing."""

    slot: int
    classification: str
    handler: int
    grid: LayoutGrid
    cells: tuple[LayoutCell, ...]
    #: The distinct non-null chunk pointers this layer already uses, in
    #: first-appearance order. This is exactly the set of legal replacements for
    #: any of its cells, and it is what a chooser offers.
    choices: tuple[int, ...]
    #: Non-empty when the slot cannot be edited, and why - a reason, not an error.
    read_only_reason: str

    @property
    def editable(self) -> bool:
        return not self.read_only_reason

    @property
    def label(self) -> str:
        """A short human label, e.g. ``BG1 · chunk grid 2x2``."""
        if self.classification == _EDITABLE_CLASSIFICATION:
            return f"BG{self.slot} · chunk grid {self.grid.columns}×{self.grid.rows}"
        return f"BG{self.slot} · {self.classification}"

    def ordinal_of(self, pointer: int) -> int | None:
        """The 1-based position of a chunk in this layer's own list, or None."""
        try:
            return self.choices.index(pointer) + 1
        except ValueError:
            return None

    def cells_using(self, pointer: int) -> tuple[int, ...]:
        """Every cell of this layer that currently references ``pointer``."""
        return tuple(cell.cell for cell in self.cells if cell.pointer == pointer)


@dataclass(frozen=True, slots=True)
class LayoutTarget:
    """Everything the editor may do with one map, and nothing it may not."""

    map_index: int
    #: The ROM-derived label, or None where the map publishes no text.
    name: str | None
    slots: tuple[LayoutSlot, ...]

    @property
    def editable_slots(self) -> tuple[LayoutSlot, ...]:
        return tuple(slot for slot in self.slots if slot.editable)

    @property
    def editable(self) -> bool:
        return bool(self.editable_slots)

    @property
    def read_only_reason(self) -> str:
        """Why no slot of this map can be edited, phrased as a state."""
        if self.editable:
            return ""
        details = "; ".join(
            f"BG{slot.slot} is {slot.read_only_reason}" for slot in self.slots
        )
        return f"no editable dominant layer ({details})"

    @property
    def read_only_kind(self) -> str:
        """The short form of the read-only state, for a one-line badge.

        ``unsupported`` when the map's slots are forms this ticket does not edit,
        ``no_alternative`` when they are dominant grids that use a single chunk and
        so have nothing to substitute, ``mixed`` when both apply, and ``""`` when
        the map is editable. A zero-dimension dominant grid is unsupported rather
        than alternative-less: it has no cells to speak of.
        """
        if self.editable:
            return ""
        kinds = {
            "no_alternative" if slot.classification == _EDITABLE_CLASSIFICATION else "unsupported"
            for slot in self.slots
        }
        if kinds == {"no_alternative"}:
            return "no_alternative"
        if kinds == {"unsupported"}:
            return "unsupported"
        return "mixed"


@dataclass(frozen=True, slots=True)
class LayoutEdit:
    """One pending cell change: what it was, what it becomes, where it lives."""

    map_index: int
    layer_slot: int
    cell: int
    original: int
    replacement: int
    #: File offset of the four-byte pointer field this change rewrites.
    offset: int


@dataclass(frozen=True, slots=True)
class LayoutSave:
    """The verified result of writing a new ROM from a pending edit set."""

    output_path: Path
    #: The provenance document published beside the image; it is what lets
    #: DragonByte Z reopen this derivative later.
    manifest_path: Path
    output_sha256: str
    output_size: int
    #: True when the edit set was empty; the output is then byte-identical.
    no_op: bool
    changes: tuple[LayoutEdit, ...]
    #: Every byte that differs from the canonical base, measured on the output.
    changed_offsets: tuple[int, ...]
    #: The changes re-read out of the reopened output image.
    verified: tuple[LayoutEdit, ...]


class MapLayoutEditor:
    """The edit session for one canonical image; holds pending edits in memory."""

    def __init__(self, canonical_bytes: bytes) -> None:
        self._base = bytes(canonical_bytes)
        try:
            # The hash gate and the only write primitive, in one place.
            self._writer = MapLayoutWriter(self._base)
            self._rom = canon.Rom(self._base)
            self._entries = canon.read_map_entries(self._rom)
        except (MapLayoutWriteError, *_READ_ERRORS) as exc:
            raise MapLayoutEditError(str(exc)) from exc
        self._targets: dict[int, LayoutTarget] = {}
        self._edits: dict[tuple[int, int, int], LayoutEdit] = {}
        #: Assembled character blocks, decoded once per map: re-decoding one is the
        #: dominant cost of a repeated preview render, and it is deterministic for
        #: one immutable image.
        self._char_data: dict[int, bytes] = {}

    @property
    def map_entry_count(self) -> int:
        """The profile's declared MapEntry count: the live index bound.

        Exposed rather than restated so a caller enumerating the corpus uses
        the same bound the editor itself refuses against.
        """
        return self._rom.map_entry_count()

    # -- what may be edited ------------------------------------------------

    def target(self, map_index: int) -> LayoutTarget:
        """Read (and cache) one map's layer slots, classified for editing."""
        count = self._rom.map_entry_count()
        if type(map_index) is not int or not 0 <= map_index < count:
            raise MapLayoutEditError(
                f"map index {map_index!r} is outside this profile's 0..{count - 1} "
                "declared map-entry range"
            )
        cached = self._targets.get(map_index)
        if cached is None:
            try:
                cached = self._build_target(map_index)
            except _READ_ERRORS as exc:
                raise MapLayoutEditError(
                    f"map:{map_index:04d} could not be read: {exc}"
                ) from exc
            self._targets[map_index] = cached
        return cached

    def _build_target(self, map_index: int) -> LayoutTarget:
        entry = self._entries[map_index]
        slots: list[LayoutSlot] = []
        for record in canon.read_layers(self._rom, entry.root_address):
            if record.classification == _EDITABLE_CLASSIFICATION:
                grid = LayoutGrid(record.chunk_x, record.chunk_y)
                cells = tuple(
                    LayoutCell(
                        cell=index,
                        column=grid.column_of(index),
                        row=grid.row_of(index),
                        pointer=pointer,
                        offset=self._writer.chunk_pointer_offset(
                            map_index, record.slot, index
                        ),
                    )
                    for index, pointer in enumerate(record.chunk_addresses)
                )
                choices = tuple(
                    dict.fromkeys(pointer for pointer in record.chunk_addresses if pointer)
                )
                reason = self._dominant_read_only_reason(grid, choices)
            else:
                grid = LayoutGrid(0, 0)
                cells = ()
                choices = ()
                reason = _READ_ONLY_FORMS.get(
                    record.classification, "an unclassified layer handler"
                )
            slots.append(
                LayoutSlot(
                    slot=record.slot,
                    classification=record.classification,
                    handler=record.handler,
                    grid=grid,
                    cells=cells,
                    choices=choices,
                    read_only_reason=reason,
                )
            )
        return LayoutTarget(
            map_index=map_index,
            name=mb.map_label(self._base, map_index),
            slots=tuple(slots),
        )

    @staticmethod
    def _dominant_read_only_reason(
        grid: LayoutGrid, choices: tuple[int, ...]
    ) -> str:
        """Why a dominant slot has nothing to substitute, or "" when it has.

        The proven write may only put a chunk the *same layer already uses* into a
        cell, so a layer that uses a single chunk - a 1x1 grid, or a larger grid
        repeating one chunk - has no legal replacement at all. That is a read-only
        state, not a failure.
        """
        if not grid.cell_count:
            return "a dominant record whose chunk grid has a zero dimension"
        if len(choices) < 2:
            return (
                f"a grid of {grid.cell_count} cell(s) using a single chunk, so it "
                "has no other chunk to substitute"
            )
        return ""

    def slot(self, map_index: int, layer_slot: int) -> LayoutSlot:
        target = self.target(map_index)
        if type(layer_slot) is not int or not 0 <= layer_slot < len(target.slots):
            raise MapLayoutEditError(f"layer slot {layer_slot!r} is out of range")
        return target.slots[layer_slot]

    def choices(self, map_index: int, layer_slot: int) -> tuple[int, ...]:
        """The legal replacement chunks for one layer: existing, non-null, its own."""
        return self.slot(map_index, layer_slot).choices

    def pointer(self, map_index: int, layer_slot: int, cell: int) -> int:
        """The chunk pointer the canonical image stores in one cell."""
        return self._writer.chunk_pointer(map_index, layer_slot, cell)

    def working_pointer(self, map_index: int, layer_slot: int, cell: int) -> int:
        """The pointer one cell holds once pending edits are applied."""
        edit = self._edits.get((map_index, layer_slot, cell))
        if edit is not None:
            return edit.replacement
        return self.pointer(map_index, layer_slot, cell)

    # -- pending edits ------------------------------------------------------

    def edit(self, map_index: int, layer_slot: int, cell: int) -> LayoutEdit | None:
        return self._edits.get((map_index, layer_slot, cell))

    def edits(self) -> tuple[LayoutEdit, ...]:
        """Every pending change, ordered by map, layer and cell."""
        return tuple(self._edits[key] for key in sorted(self._edits))

    def edits_for(self, map_index: int) -> tuple[LayoutEdit, ...]:
        return tuple(edit for edit in self.edits() if edit.map_index == map_index)

    @property
    def has_changes(self) -> bool:
        return bool(self._edits)

    @property
    def changed_cell_count(self) -> int:
        return len(self._edits)

    def set_cell(
        self, map_index: int, layer_slot: int, cell: int, replacement: int
    ) -> LayoutEdit | None:
        """Record one cell replacement; return None when it restores the original.

        Validation is the writer's, not a copy of it: an unsupported layer, an
        out-of-range cell, a null pointer, a chunk from another layer or a boolean
        all fail here, before anything is remembered.
        """
        slot = self.slot(map_index, layer_slot)
        if not slot.editable:
            raise MapLayoutEditError(
                f"BG{layer_slot} is not editable: {slot.read_only_reason}"
            )
        if not slot.grid.contains(cell):
            raise MapLayoutEditError(
                f"chunk cell {cell!r} is outside BG{layer_slot}'s "
                f"{slot.grid.columns}×{slot.grid.rows} grid"
            )
        try:
            self._writer.set_chunk_pointer(map_index, layer_slot, cell, replacement)
        except (MapLayoutWriteError, *_READ_ERRORS) as exc:
            raise MapLayoutEditError(str(exc)) from exc
        key = (map_index, layer_slot, cell)
        original = slot.cells[cell].pointer
        if replacement == original:
            self._edits.pop(key, None)
            return None
        edit = LayoutEdit(
            map_index=map_index,
            layer_slot=layer_slot,
            cell=cell,
            original=original,
            replacement=replacement,
            offset=slot.cells[cell].offset,
        )
        self._edits[key] = edit
        return edit

    def revert_cell(self, map_index: int, layer_slot: int, cell: int) -> bool:
        """Drop one cell's pending edit, restoring the canonical pointer."""
        key = (map_index, layer_slot, cell)
        edit = self._edits.get(key)
        if edit is None:
            return False
        try:
            self._writer.set_chunk_pointer(map_index, layer_slot, cell, edit.original)
        except (MapLayoutWriteError, *_READ_ERRORS) as exc:
            raise MapLayoutEditError(str(exc)) from exc
        del self._edits[key]
        return True

    def revert_map(self, map_index: int) -> int:
        """Drop every pending edit of one map; return how many were dropped."""
        keys = [key for key in self._edits if key[0] == map_index]
        for key in keys:
            edit = self._edits[key]
            try:
                self._writer.set_chunk_pointer(*key, edit.original)
            except (MapLayoutWriteError, *_READ_ERRORS) as exc:
                raise MapLayoutEditError(str(exc)) from exc
            del self._edits[key]
        return len(keys)

    def reset(self) -> int:
        """Drop every pending edit in the session, whichever map it belongs to."""
        dropped = len(self._edits)
        self._edits.clear()
        # Rebuild from the canonical image rather than trusting an unwind, so no
        # stale byte plan can survive a reset.
        self._writer = MapLayoutWriter(self._base)
        return dropped

    # -- preview ------------------------------------------------------------

    def overrides(
        self,
        map_index: int,
        draft: tuple[int, int, int] | None = None,
    ) -> dict[tuple[int, int], int]:
        """The cell substitutions a preview must apply, keyed ``(slot, cell)``.

        ``draft`` is one uncommitted ``(layer slot, cell, replacement)`` selection,
        so the map preview can answer a chooser click before the user applies it.
        Nothing is written: the result only drives an in-memory render.
        """
        overrides = {
            (edit.layer_slot, edit.cell): edit.replacement
            for edit in self.edits_for(map_index)
        }
        if draft is not None:
            layer_slot, cell, replacement = draft
            slot = self.slot(map_index, layer_slot)
            if not slot.editable:
                raise MapLayoutEditError(
                    f"BG{layer_slot} is not editable: {slot.read_only_reason}"
                )
            if not slot.grid.contains(cell):
                raise MapLayoutEditError(
                    f"chunk cell {cell!r} is outside BG{layer_slot}'s grid"
                )
            try:
                mb.validate_cell_replacement(slot.choices, replacement)
            except mb.MapBrowserError as exc:
                raise MapLayoutEditError(str(exc)) from exc
            overrides[(layer_slot, cell)] = replacement
        return overrides

    def preview(
        self,
        map_index: int,
        draft: tuple[int, int, int] | None = None,
    ) -> "mb.MapBrowserResult":
        """Render one map through the accepted pipeline with pending edits applied.

        The render reads the canonical image held by this session. No ROM file is
        opened and no byte is written merely to preview. The map's character block
        is decoded once per session, so answering a chooser click does not re-pay
        the exporter's container decoding.
        """
        overrides = self.overrides(map_index, draft)
        try:
            return mb.render_map(
                self._base,
                map_index,
                chunk_overrides=overrides or None,
                char_data=self.character_block(map_index),
            )
        except _READ_ERRORS as exc:
            raise MapLayoutEditError(str(exc)) from exc

    def character_block(self, map_index: int) -> bytes:
        """This map's assembled character block, decoded once per session.

        Public because the chunk chooser renders through the same block: re-decoding
        it per preview *and* per chooser refill is what makes a cold chunk pick slow.
        A block for a different map would render wrong pixels rather than raise, so
        callers must ask the session that owns the map.
        """
        cached = self._char_data.get(map_index)
        if cached is None:
            try:
                entry = self._entries[map_index]
                block, _selectors, _animated = canon.assemble_map_char_block(
                    self._rom, entry.root_address
                )
            except _READ_ERRORS as exc:
                raise MapLayoutEditError(
                    f"map:{map_index:04d} character block could not be decoded: {exc}"
                ) from exc
            cached = block.data
            self._char_data[map_index] = cached
        return cached

    # -- reading the pending changes in game language -----------------------

    def describe_edit(self, edit: LayoutEdit) -> str:
        """One pending change, phrased for a person rather than for a diff."""
        slot = self.slot(edit.map_index, edit.layer_slot)
        cell = slot.cells[edit.cell]
        before = slot.ordinal_of(edit.original)
        after = slot.ordinal_of(edit.replacement)
        return (
            f"BG{edit.layer_slot} · column {cell.column}, row {cell.row}: "
            f"{self._chunk_name(before)} → {self._chunk_name(after)}"
        )

    def describe_edits(self, map_index: int) -> tuple[str, ...]:
        return tuple(self.describe_edit(edit) for edit in self.edits_for(map_index))

    @staticmethod
    def _chunk_name(ordinal: int | None) -> str:
        return f"Chunk {ordinal}" if ordinal else "an empty cell"

    # -- building and saving ------------------------------------------------

    def build(self) -> bytes:
        """Build the edited image in memory; an empty edit set is byte-identical."""
        return self._writer.build()

    def save(
        self, output_path, *, source_path, profile_id: str
    ) -> LayoutSave:
        """Write a NEW ROM from the pending edit set, then publish it.

        Never writes the source: the output path is refused when it resolves to the
        source, and the canonical image is only ever read. With no pending edits the
        output is byte-identical to the source, because the edit plan is empty and
        every emitted byte comes from the verified base.

        The image and its provenance manifest are built at temporary sibling paths,
        verified there, and only then moved onto the requested destinations, so a
        failed emit or a failed verification leaves whatever already existed at the
        destination byte-for-byte intact. The shared transaction in
        :mod:`tools.webfoot.authored_image` owns all of that; this method supplies
        the bounded byte plan and the domain's own re-read of the emitted image.
        """
        # The session keeps a semantic record per change and the writer keeps the
        # byte plan; refuse to emit if the two ever disagree, rather than write a
        # plan that is not the edit set the user approved. Both sides are compared
        # as address sets - the records are ordered by map/cell, the plan by offset.
        # Physical-write conflicts *within* the plan are the shared layer's job
        # (write.plan_changes refuses any overlap).
        if sorted(edit.offset for edit in self.edits()) != list(self._writer.pending_offsets):
            raise MapLayoutEditError(
                "the pending layout changes and their byte plan disagree; nothing was written"
            )
        changes = tuple(
            write_sdk.ByteChange(
                offset=edit.offset,
                old=self._base[edit.offset : edit.offset + 4],
                new=edit.replacement.to_bytes(4, "little"),
                owner=f"map:{edit.map_index:04d} layer {edit.layer_slot} cell {edit.cell}",
                reason="existing same-layer chunk replacement",
            )
            for edit in self.edits()
        )
        try:
            saved = save_authored_image(
                self._base,
                source_path=source_path,
                output_path=output_path,
                profile_id=profile_id,
                changes=changes,
                canonical_sha256=profile_authority.canonical_export_identity().sha256,
                verify=self._verify_output,
            )
        except AuthoredImageError as exc:
            # One public failure type for this session, whatever refused the save.
            raise MapLayoutEditError(str(exc)) from exc
        return LayoutSave(
            output_path=saved.output_path,
            manifest_path=saved.manifest_path,
            output_sha256=saved.output_sha256,
            output_size=saved.output_size,
            no_op=saved.no_op,
            # The session's own record order (map, layer, cell), not the
            # transaction's offset order: the two carry the same set of changes
            # here, because the byte plan and the pending records are already
            # required to agree above, and this is the order the caller asked in.
            changes=changes,
            changed_offsets=saved.changed_offsets,
            verified=saved.verified,
        )

    def _verify_output(self, data: bytes, changes) -> tuple[LayoutEdit, ...]:
        """Re-prove one emitted image carries exactly the requested cell changes.

        The byte-level questions - length, digest, and that nothing outside a
        requested field changed - have already been answered by the shared
        transaction. What is left is the domain's own: every pending cell must read
        back its replacement through the accepted layer reader, and every requested
        change must be accounted for.
        """
        verified: list[LayoutEdit] = []
        try:
            rom = canon.Rom(data)
            entries = canon.read_map_entries(rom)
            for edit in self.edits():
                layer = canon.read_layer(
                    rom, entries[edit.map_index].root_address, edit.layer_slot
                )
                found = layer.chunk_addresses[edit.cell]
                if found != edit.replacement:
                    raise MapLayoutEditError(
                        f"map:{edit.map_index:04d} layer {edit.layer_slot} cell {edit.cell} "
                        f"reads back {found:#010x}, not {edit.replacement:#010x}"
                    )
                verified.append(edit)
        except _READ_ERRORS as exc:
            raise MapLayoutEditError(f"the written ROM could not be re-read: {exc}") from exc
        if len(verified) != len(changes):
            raise MapLayoutEditError("the written ROM does not carry every requested change")
        return tuple(verified)
