"""Narrow, fixed-width dominant-layer chunk-pointer writer for Buu rev0.

The immutable canonical image is the source for every build. A replacement must
already occur in the same layer, so this surface cannot allocate or relocate.
"""

from __future__ import annotations

import hashlib
import struct

from tools.export import canonical as canon
from tools.export.map_browser import SUPPORTED_ROM_SHA256


class MapLayoutWriteError(ValueError):
    """The requested fixed-size map-layout replacement is unsupported."""


class MapLayoutWriter:
    def __init__(self, canonical_bytes: bytes) -> None:
        self._base = bytes(canonical_bytes)
        if hashlib.sha256(self._base).hexdigest() != SUPPORTED_ROM_SHA256:
            raise MapLayoutWriteError("expected the canonical Buu rev0 image")
        self._rom = canon.Rom(self._base)
        self._edits: dict[int, int] = {}

    def chunk_pointer(self, map_index: int, layer_slot: int, cell: int) -> int:
        """Read a dominant layer's row-major chunk pointer from source bytes."""
        if type(map_index) is not int or not 0 <= map_index < canon.MAP_ENTRY_COUNT:
            raise MapLayoutWriteError("map index is out of range")
        if type(layer_slot) is not int or not 0 <= layer_slot < 4:
            raise MapLayoutWriteError("layer slot is out of range")
        entry = canon.read_map_entries(self._rom)[map_index]
        layer = canon.read_layer(self._rom, entry.root_address, layer_slot)
        if layer.handler != canon.DOMINANT_LAYER_HANDLER:
            raise MapLayoutWriteError("layer is not the dominant chunk form")
        if type(cell) is not int or not 0 <= cell < len(layer.chunk_addresses):
            raise MapLayoutWriteError("chunk cell is out of range")
        return layer.chunk_addresses[cell]

    def set_chunk_pointer(
        self, map_index: int, layer_slot: int, cell: int, replacement: int
    ) -> None:
        """Replace one pointer with another existing non-null pointer in its layer."""
        original = self.chunk_pointer(map_index, layer_slot, cell)
        entry = canon.read_map_entries(self._rom)[map_index]
        layer = canon.read_layer(self._rom, entry.root_address, layer_slot)
        if type(replacement) is not int or replacement == 0 or replacement not in layer.chunk_addresses:
            raise MapLayoutWriteError("replacement must be an existing non-null chunk in this layer")
        canon.read_chunk_entries(self._rom, replacement)
        address = layer.address + canon.LAYER_CHUNK_WINDOW_OFFSET + 4 * cell
        offset = self._rom.span(address, 4)
        if replacement == original:
            self._edits.pop(offset, None)
        else:
            self._edits[offset] = replacement

    def build(self) -> bytes:
        """Build from the canonical source; an empty edit set is byte-identical."""
        result = bytearray(self._base)
        for offset, replacement in sorted(self._edits.items()):
            struct.pack_into("<I", result, offset, replacement)
        return bytes(result)
