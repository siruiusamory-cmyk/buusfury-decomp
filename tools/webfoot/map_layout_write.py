"""Narrow, fixed-width dominant-layer chunk-pointer writer for Buu rev0.

The immutable canonical image is the source for every build. A replacement must
already occur on the same map, so this surface cannot allocate or relocate.

DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001 adds no capability here. It exposes the
four-byte field's file offset (so an edit session can record and display what one
change touches) and routes the replacement policy through
:func:`validate_chunk_replacement`, which the preview path uses too, so "what may
be written" and "what may be previewed" cannot drift apart.

**CQA-04: this module no longer reads through ``tools.export``.** It used to take
its map-entry rows, its layer records and its replacement policy from
``tools.export.canonical`` and ``tools.export.map_browser`` - an export/research
reader standing underneath a shipped write path. Both are now the SDK's: the
records come from :mod:`tools.webfoot.formats.map_graphics`, the record shape
from :mod:`tools.webfoot.formats.map_entry`, and the profile from
:func:`tools.webfoot.packaged.packaged_profile`. The dependency now points
SDK authority -> export consumer, never the reverse, and
``tests/unit/test_map_decode_authority.py`` fails if it is turned back.
"""

from __future__ import annotations

import hashlib
import struct
from typing import Iterable

from .formats import map_entry as me
from .formats import map_graphics as mg
from .packaged import packaged_profile
from .profile import RomProfile


class MapLayoutWriteError(ValueError):
    """The requested fixed-size map-layout replacement is unsupported."""


def legal_chunk_pointers(*groups: Iterable[int]) -> tuple[int, ...]:
    """The distinct non-null pointers across pointer groups, in first-appearance order.

    The legal set for one map is the union of its dominant layers' windows - every
    pointer in it is a chunk the engine already dereferences for that map - and the
    caller that wants an edited layer's own chunks first passes that window first.
    Deterministic for a given image, so an ordinal resolves to the same chunk on
    every read.
    """
    seen: dict[int, None] = {}
    for group in groups:
        for pointer in group:
            if pointer:
                seen.setdefault(pointer, None)
    return tuple(seen)


def validate_chunk_replacement(
    allowed_addresses: tuple[int, ...], replacement: object
) -> int:
    """Whether a value may occupy a dominant-layer chunk-pointer cell.

    The whole policy, in one place: a cell of the accepted dominant form may only
    reference an existing, non-null chunk pointer **the same map already uses** in
    one of its dominant layers. The caller supplies that set, built by
    :func:`legal_chunk_pointers`. A layer that uses a single chunk may therefore
    still be painted with a sibling layer's chunk, which is what makes such a
    layer editable at all; the layer's own chunks and its siblings' are legal on
    the same terms, and neither is privileged.

    Nothing else is established - not the null pointer (which the engine's own
    occupancy test reads as unoccupied), not a chunk from another map (which would
    be a reference this map's records do not support), not a fresh address no
    dominant layer of this map contains (which would be allocation, not a
    fixed-size replacement), and not a boolean that merely equals an integer.

    This is the SDK-side owner of that rule. The export-side preview facade
    (``tools.export.map_browser.validate_cell_replacement``) and
    :func:`tools.webfoot.map_view.render_map`'s override check both call it, so
    the preview path and the write path cannot disagree about what is legal.

    Returns the accepted pointer so a caller can use the result directly.
    """
    if type(replacement) is not int:
        raise MapLayoutWriteError("a chunk pointer must be an integer address")
    if replacement == 0:
        raise MapLayoutWriteError("the null chunk pointer is not a replacement")
    if replacement not in allowed_addresses:
        raise MapLayoutWriteError(
            "a replacement chunk must already be used by a dominant layer of the same map"
        )
    return replacement


class MapLayoutWriter:
    def __init__(self, canonical_bytes: bytes, *, profile: RomProfile | None = None) -> None:
        """Bind the writer to one image and the profile that describes it.

        `profile` defaults to the packaged canonical profile, which is what every
        production caller means. It is injectable so the writer's profile-derived
        bounds can be exercised against a declaration that differs from the
        canonical one, rather than only asserted about the source.
        """
        self._base = bytes(canonical_bytes)
        # The one identity contract, not this module's own copy of the hash: the
        # readers this writer drives resolve the profile's declared table
        # addresses, so the bytes it accepts must be that same profile's image.
        resolved = profile if profile is not None else packaged_profile()
        expected = resolved.identity
        if hashlib.sha256(self._base).hexdigest() != expected.sha256:
            raise MapLayoutWriteError(
                f"expected the image described by profile {expected.profile_id!r}"
            )
        self._profile = resolved
        self._reader = mg.MapGraphicsReader(self._base, resolved)
        self._edits: dict[int, int] = {}

    @property
    def profile(self) -> RomProfile:
        """The profile this writer's addresses and bounds are resolved through."""
        return self._profile

    def _layer(
        self, map_index: int, layer_slot: int
    ) -> tuple[mg.LayerRecord, tuple[mg.LayerRecord, ...]]:
        """The dominant layer record both the read and write paths address.

        Returns the map's four layer records beside it: the legal replacement set
        is a property of the whole map, so a caller that only held one layer could
        not compute it.
        """
        count = self._reader.map_entry_count()
        if type(map_index) is not int or not 0 <= map_index < count:
            raise MapLayoutWriteError(
                f"map index is out of this profile's 0..{count - 1} declared range"
            )
        if type(layer_slot) is not int or not 0 <= layer_slot < len(mg.ROOT_LAYER_SLOTS):
            raise MapLayoutWriteError("layer slot is out of range")
        try:
            entry = mg.read_map_entries(self._reader)[map_index]
            records = mg.read_layers(self._reader, entry.root_address)
            layer = records[layer_slot]
        except mg.MapGraphicsError as exc:
            raise MapLayoutWriteError(str(exc)) from exc
        if layer.handler != mg.DOMINANT_LAYER_HANDLER:
            raise MapLayoutWriteError("layer is not the dominant chunk form")
        return layer, records


    @staticmethod
    def _cell_index(layer: mg.LayerRecord, cell: object) -> int:
        if type(cell) is not int or not 0 <= cell < len(layer.chunk_addresses):
            raise MapLayoutWriteError("chunk cell is out of range")
        return cell

    def chunk_pointer(self, map_index: int, layer_slot: int, cell: int) -> int:
        """Read a dominant layer's row-major chunk pointer from source bytes."""
        layer, _records = self._layer(map_index, layer_slot)
        return layer.chunk_addresses[self._cell_index(layer, cell)]

    def chunk_pointer_offset(self, map_index: int, layer_slot: int, cell: int) -> int:
        """The file offset of one layout cell's four-byte pointer field.

        Read-only: this is the field :meth:`set_chunk_pointer` would overwrite, and
        it is what an edit session records as the ROM offset of a pending change.
        It is the same arithmetic the write path uses, not a second copy of it.
        """
        layer, _records = self._layer(map_index, layer_slot)
        self._cell_index(layer, cell)
        address = layer.address + mg.LAYER_CHUNK_WINDOW_OFFSET + 4 * cell
        return self._reader.span(address, 4)

    def set_chunk_pointer(
        self, map_index: int, layer_slot: int, cell: int, replacement: int
    ) -> None:
        """Replace one pointer, or restore the cell's own stored pointer.

        Restoring a cell's current value is how a revert works, so that case is
        accepted *before* the replacement policy runs: a cell that is currently
        null must be put back to null by the same call the editor uses to undo
        filling it, and the null pointer is never a legal *replacement*.
        """
        layer, records = self._layer(map_index, layer_slot)
        cell = self._cell_index(layer, cell)
        original = layer.chunk_addresses[cell]
        offset = self.chunk_pointer_offset(map_index, layer_slot, cell)
        if type(replacement) is not int:
            # The policy states this too; it is repeated here so the early-out
            # below cannot mistake a boolean for a pointer that is already stored.
            raise MapLayoutWriteError("a chunk pointer must be an integer address")
        if replacement == original:
            self._edits.pop(offset, None)
            return
        validate_chunk_replacement(
            legal_chunk_pointers(*(record.chunk_addresses for record in records)),
            replacement,
        )
        try:
            mg.dominant_chunk_words(self._reader, replacement)
        except mg.MapGraphicsError as exc:
            raise MapLayoutWriteError(str(exc)) from exc
        self._edits[offset] = replacement

    def read_layer(self, map_index: int, layer_slot: int) -> mg.LayerRecord:
        """One map's dominant layer record, through this writer's reader."""
        return self._layer(map_index, layer_slot)[0]


    @property
    def pending_offsets(self) -> tuple[int, ...]:
        """File offsets of the pointer fields this writer would currently change."""
        return tuple(sorted(self._edits))

    def build(self) -> bytes:
        """Build from the canonical source; an empty edit set is byte-identical."""
        result = bytearray(self._base)
        for offset, replacement in sorted(self._edits.items()):
            struct.pack_into("<I", result, offset, replacement)
        return bytes(result)


#: The record shape this writer's reader must declare. Kept as a re-export so a
#: caller asking "what stride does this writer assume?" reads the format codec's
#: answer rather than a second number.
MAP_ENTRY_STRIDE = me.MAP_ENTRY_SIZE
