"""Narrow, fixed-width dominant-layer chunk-pointer writer for Buu rev0.

The immutable canonical image is the source for every build. A replacement must
already occur in the same layer, so this surface cannot allocate or relocate.

DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001 adds no capability here. It exposes the
four-byte field's file offset (so an edit session can record and display what one
change touches) and routes the replacement policy through
:func:`tools.export.map_browser.validate_cell_replacement`, which the preview path
uses too, so "what may be written" and "what may be previewed" cannot drift apart.
"""

from __future__ import annotations

import hashlib
import struct

from tools.export import canonical as canon
from tools.export import map_browser as mb
from tools.export.map_browser import SUPPORTED_ROM_SHA256


class MapLayoutWriteError(ValueError):
    """The requested fixed-size map-layout replacement is unsupported."""


def validate_chunk_replacement(layer_addresses: tuple[int, ...], replacement: object) -> int:
    """Apply the shared replacement policy, in this module's error family.

    The rule itself lives in :func:`tools.export.map_browser.validate_cell_replacement`
    because a reader's preview must enforce exactly the same thing; re-raising it
    here keeps this writer's public error type for its own callers.
    """
    try:
        return mb.validate_cell_replacement(layer_addresses, replacement)
    except mb.MapBrowserError as exc:
        raise MapLayoutWriteError(str(exc)) from exc


class MapLayoutWriter:
    def __init__(self, canonical_bytes: bytes) -> None:
        self._base = bytes(canonical_bytes)
        if hashlib.sha256(self._base).hexdigest() != SUPPORTED_ROM_SHA256:
            raise MapLayoutWriteError("expected the canonical Buu rev0 image")
        self._rom = canon.Rom(self._base)
        self._edits: dict[int, int] = {}

    def _layer(self, map_index: int, layer_slot: int) -> canon.LayerRecord:
        """The dominant layer record both the read and write paths address."""
        if type(map_index) is not int or not 0 <= map_index < canon.MAP_ENTRY_COUNT:
            raise MapLayoutWriteError("map index is out of range")
        if type(layer_slot) is not int or not 0 <= layer_slot < 4:
            raise MapLayoutWriteError("layer slot is out of range")
        entry = canon.read_map_entries(self._rom)[map_index]
        layer = canon.read_layer(self._rom, entry.root_address, layer_slot)
        if layer.handler != canon.DOMINANT_LAYER_HANDLER:
            raise MapLayoutWriteError("layer is not the dominant chunk form")
        return layer

    @staticmethod
    def _cell_index(layer: canon.LayerRecord, cell: object) -> int:
        if type(cell) is not int or not 0 <= cell < len(layer.chunk_addresses):
            raise MapLayoutWriteError("chunk cell is out of range")
        return cell

    def chunk_pointer(self, map_index: int, layer_slot: int, cell: int) -> int:
        """Read a dominant layer's row-major chunk pointer from source bytes."""
        layer = self._layer(map_index, layer_slot)
        return layer.chunk_addresses[self._cell_index(layer, cell)]

    def chunk_pointer_offset(self, map_index: int, layer_slot: int, cell: int) -> int:
        """The file offset of one layout cell's four-byte pointer field.

        Read-only: this is the field :meth:`set_chunk_pointer` would overwrite, and
        it is what an edit session records as the ROM offset of a pending change.
        It is the same arithmetic the write path uses, not a second copy of it.
        """
        layer = self._layer(map_index, layer_slot)
        self._cell_index(layer, cell)
        address = layer.address + canon.LAYER_CHUNK_WINDOW_OFFSET + 4 * cell
        return self._rom.span(address, 4)

    def set_chunk_pointer(
        self, map_index: int, layer_slot: int, cell: int, replacement: int
    ) -> None:
        """Replace one pointer, or restore the cell's own stored pointer.

        Restoring a cell's current value is how a revert works, so that case is
        accepted *before* the replacement policy runs: a cell that is currently
        null must be put back to null by the same call the editor uses to undo
        filling it, and the null pointer is never a legal *replacement*.
        """
        layer = self._layer(map_index, layer_slot)
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
        validate_chunk_replacement(layer.chunk_addresses, replacement)
        canon.read_chunk_entries(self._rom, replacement)
        self._edits[offset] = replacement

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
