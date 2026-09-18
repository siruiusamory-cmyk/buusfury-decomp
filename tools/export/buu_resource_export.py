"""ASSET-EXPORT-001: the canonical Buu's Fury resource exporter.

Builds a complete, deterministic, human-usable local resource library from the
canonical ROM using the accepted post-LOGX schemas, plus a separate sibling audit
directory for verification. The library holds PNG, JSON and CSV only, and no
generated prose.

Usage
-----

    python -m tools.export.buu_resource_export --rom <ROM> --output <EXPORT_ROOT>

``--all`` is the default. ``--maps``, ``--tiles`` and ``--sprites`` select
subsets; ``--audit-only`` analyses and writes the audit directory without
producing resource files; ``--force`` writes into a non-empty export root;
``--compare <earlier_root>`` diffs that tree against this run's artifacts.

Safety
------

* The ROM is opened read-only, hashed before and after, and never written,
  copied into the output, or named as a path inside the library.
* The output root must not be inside a git repository. The exporter resolves the
  path, looks for a ``.git`` entry in it or any ancestor, and refuses if it finds
  one, so a generated library cannot be staged by accident. That is a hard
  refusal rather than a ``.gitignore`` entry: an ignore rule protects one
  checkout, a refusal protects every one.
* The audit root must be a sibling of the export root, and neither root may
  contain the other.

Determinism
-----------

Every path is a pure function of numeric identity; every PNG uses a fixed filter
and compression level with no timestamp chunk; every JSON document is serialized
with sorted keys and LF endings. Two runs against the same ROM therefore produce
the same layout, filenames, pixel data, metadata values and hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
import shutil
import sys
import time
import zlib

from . import canonical as canon
from . import metadata as meta
from . import naming
from . import png
from . import render
from . import webfoot_strict as ws

#: The only image this exporter is authorized to read.
CANONICAL_ROM_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

TOOL_NAME = "buu_resource_export"
TOOL_VERSION = "1"

#: Bank sheets lay tiles out 16 to a row: 128 pixels wide at 8 pixels a tile.
BANK_SHEET_COLUMNS = naming.SHEET_TILE_COLUMNS

#: Frame sheets put the four direction indices of one frame on one row.
ANIMATION_SHEET_COLUMNS = naming.SHEET_DIRECTION_COLUMNS

#: The two palettes the accepted structures use, in canonical numeric order.
PALETTE_OBJECT_ID = 0
PALETTE_BACKGROUND_ID = 1

#: The accepted populations this export must account for exactly.
EXPECTED_POPULATIONS = {
    "map_entries": 452,
    "maps_exported": 452,
    "map_layers_classified": 1808,
    "sprite_definitions": 297,
    "animation_slots": 4070,
    "non_null_animations": 1721,
    "unique_frames": 10980,
    "sprite_pieces": 11005,
    "multipart_frames": 21,
    "structured_sprite_graphics": 7390,
    "chunks": 3745,
    "tile_banks": 187,
}


class ExportError(RuntimeError):
    """Raised when the export cannot proceed safely or faithfully."""


# --- ROM identity ------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_canonical_rom(path: Path) -> bytes:
    """Read the canonical ROM and refuse anything that is not exactly it."""
    if not path.exists():
        raise ExportError(f"ROM {path} does not exist")
    data = path.read_bytes()
    digest = sha256_bytes(data)
    if digest != CANONICAL_ROM_SHA256:
        raise ExportError(
            f"{path} is not the canonical Buu's Fury image: SHA-256 {digest} is "
            f"not {CANONICAL_ROM_SHA256}"
        )
    return data


# --- output-root safety ------------------------------------------------------

def is_repository_root(candidate: Path) -> bool:
    """Whether ``candidate`` is a usable git work-tree root.

    A bare ``.git`` directory is not enough: an interrupted clone, a stray
    ``mkdir .git`` or a half-deleted checkout leaves one behind, and treating
    that as a repository would refuse perfectly safe output paths. A real
    repository root either holds a ``.git`` directory containing ``HEAD``, or a
    ``.git`` *file* (a linked work tree or a submodule).
    """
    marker = candidate / ".git"
    if marker.is_dir():
        return (marker / "HEAD").exists()
    return marker.is_file()


def find_repository_root(path: Path) -> Path | None:
    """The nearest ancestor of ``path`` (inclusive) that is a work-tree root."""
    current = path.resolve()
    for candidate in (current, *current.parents):
        if is_repository_root(candidate):
            return candidate
    return None


def ensure_outside_repository(root: Path, label: str) -> None:
    """Refuse an output root that resolves inside a git work tree."""
    repository = find_repository_root(root)
    if repository is not None:
        raise ExportError(
            f"the {label} {root} resolves inside the git repository at "
            f"{repository}; generated resources must live outside version control"
        )


def audit_root_for(output_root: Path) -> Path:
    """``<EXPORT_ROOT>`` -> ``<EXPORT_ROOT>_Audit``, a sibling directory."""
    resolved = output_root.resolve()
    return resolved.parent / (resolved.name + "_Audit")


#: The directories the exporter owns beneath the resource root. ``--force``
#: removes exactly these before writing, so no artifact from an earlier revision
#: of the tool can survive into a published library, and nothing the exporter did
#: not create is ever touched.
GENERATED_DIRECTORIES = (
    naming.MAPS,
    naming.TILES,
    naming.SPRITES,
    naming.SPRITE_GRAPHICS,
    naming.PALETTES,
    naming.METADATA,
)


def clear_generated(output_root: Path) -> tuple[str, ...]:
    """Remove the exporter's own directories; return whatever else is left.

    A hard refusal to delete anything else is deliberate: the caller's directory
    may hold unrelated work, and a wide recursive delete driven by a flag is not
    an acceptable failure mode for a tool that is pointed at a user directory.
    """
    for name in GENERATED_DIRECTORIES:
        target = output_root / name
        if target.is_dir():
            shutil.rmtree(target)
    if not output_root.exists():
        return ()
    return tuple(sorted(entry.name for entry in output_root.iterdir()))


# --- writing -----------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Artifact:
    """One written file: its library-relative path, size and digest."""

    relative_path: str
    size: int
    sha256: str


class Writer:
    """Writes artifacts, digesting them on the way out.

    Digesting as it writes means the audit's hash table describes the bytes that
    actually reached disk rather than a second read of the tree, so the two can
    not disagree by construction.
    """

    def __init__(self, root: Path, *, enabled: bool = True) -> None:
        self.root = root
        self.enabled = enabled
        self.artifacts: list[Artifact] = []

    def write(self, relative_path: str, data: bytes) -> Artifact:
        artifact = Artifact(
            relative_path=relative_path,
            size=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
        )
        if self.enabled:
            target = self.root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.artifacts.append(artifact)
        return artifact

    @property
    def total_bytes(self) -> int:
        return sum(artifact.size for artifact in self.artifacts)


@dataclass(frozen=True, slots=True)
class Failure:
    """One structural failure, recorded rather than swallowed."""

    kind: str
    population: str
    identity: str
    detail: str

    def as_document(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "population": self.population,
            "identity": self.identity,
            "detail": self.detail,
        }


def write_rgba_png(
    writer: Writer,
    relative_path: str,
    width: int,
    height: int,
    pixels: bytes,
    table: bytes,
    *,
    already_rgba: bool = False,
) -> Artifact:
    """Expand an index image and write it as a lossless RGBA PNG."""
    rgba = pixels if already_rgba else render.to_rgba(pixels, table)
    return writer.write(relative_path, png.encode_rgba(width, height, rgba))


def entry_stats(entries: tuple[int, ...]) -> dict[str, int]:
    """Structural census over a run of tile entries.

    Only bits 0..9 are interpreted, and only as the tile ordinal the engine's own
    loaders populate. Bits 10 and 11 are counted because the renderer applies them
    as the platform's flip selectors; the 12..15 nibble is counted and recorded
    raw and is never interpreted.
    """
    ordinals = set()
    bit_10 = 0
    bit_11 = 0
    high_nibble = 0
    for word in entries:
        ordinals.add(word & canon.TILE_ENTRY_ORDINAL_MASK)
        if word & canon.TILE_ENTRY_BIT_10:
            bit_10 += 1
        if word & canon.TILE_ENTRY_BIT_11:
            bit_11 += 1
        if word & canon.TILE_ENTRY_HIGH_NIBBLE:
            high_nibble += 1
    return {
        "tile_ordinal_min": min(ordinals),
        "tile_ordinal_max": max(ordinals),
        "distinct_tile_ordinals": len(ordinals),
        "entry_bit_10_count": bit_10,
        "entry_bit_11_count": bit_11,
        "entry_high_nibble_nonzero_count": high_nibble,
    }


# --- the exporter ------------------------------------------------------------

class Exporter:
    """Produces the resource library and its audit directory."""

    def __init__(
        self, rom: canon.Rom, output_root: Path, audit_root: Path
    ) -> None:
        self.rom = rom
        self.output_root = output_root
        self.audit_root = audit_root
        self.failures: list[Failure] = []
        self.counters: dict[str, int] = {}
        self.references: dict[str, object] = {}
        self.started = time.monotonic()

        self.writer = Writer(output_root, enabled=True)
        self.subsystems: set[str] = set()
        self.object_palette = render.object_palette_rgb(rom)
        self.bg_palette = render.bg_palette_rgb(rom)
        self.object_table = render.rgba_table(self.object_palette)
        self.bg_table = render.rgba_table(self.bg_palette)

        self.map_entries = canon.read_map_entries(rom)
        self.layers: dict[int, tuple[canon.LayerRecord, ...]] = {}
        self.char_blocks: dict[int, canon.CharBlock] = {}
        self.selector_counts: dict[int, int] = {}
        self.animated_counts: dict[int, int] = {}
        self.chunk_entries: dict[int, tuple[int, ...]] = {}
        self.chunk_maps: dict[int, list[int]] = {}
        self.chunk_images: dict[tuple[int, int], bytes] = {}

        self.definitions: tuple[canon.SpriteDefinition, ...] = ()
        self.animations: dict[int, canon.AnimationRecord] = {}
        self.frames: dict[int, canon.FrameRecord] = {}
        self.graphic_indices: dict[int, bytes] = {}
        self.graphic_extents: dict[int, tuple[int, int]] = {}
        #: Piece count summed over every rendered cell of every animation
        #: reference. It reconciles with the accepted direction-cell total the
        #: same way `LOGX-SYNTHESIS.md` §8.2 states it: the extra pieces are
        #: exactly the 21 multipart frames, counted once per reference.
        self.piece_references_over_animation_references = 0

    # -- helpers --------------------------------------------------------------

    def count(self, key: str, value: int) -> None:
        self.counters[key] = value

    def fail(self, kind: str, population: str, identity: str, detail: str) -> None:
        self.failures.append(
            Failure(kind=kind, population=population, identity=identity, detail=detail)
        )

    # -- map graph ------------------------------------------------------------

    def collect_map_graph(self) -> None:
        """Read every map's roots, layers, character block and chunk containers.

        Collected once and shared, because the layer images, the composites and
        the chunk library all consume the same structures and because containers
        must not be decoded twice for one run.
        """
        for entry in self.map_entries:
            try:
                layers = canon.read_layers(self.rom, entry.root_address)
                self.layers[entry.index] = layers
                block, selectors, animated = canon.assemble_map_char_block(
                    self.rom, entry.root_address
                )
            except (canon.CanonicalError, ws.ContainerError, render.RenderError) as exc:
                self.fail(
                    "map_graph", "map_entries", f"map:{entry.index:04d}", str(exc)
                )
                continue
            self.char_blocks[entry.index] = block
            self.selector_counts[entry.index] = len(selectors)
            self.animated_counts[entry.index] = len(animated)
            for layer in layers:
                if layer.classification != "dominant":
                    continue
                for address in layer.chunk_addresses:
                    if address == 0:
                        continue
                    self.chunk_maps.setdefault(address, []).append(entry.index)
                    if address not in self.chunk_entries:
                        try:
                            self.chunk_entries[address] = canon.read_chunk_entries(
                                self.rom, address
                            )
                        except (canon.CanonicalError, ws.ContainerError) as exc:
                            self.fail(
                                "chunk", "chunks", f"{address:#010x}", str(exc)
                            )

    def layer_grid(self, layer: canon.LayerRecord) -> tuple[int, ...]:
        """Stitch a dominant layer's chunk grid into one entry array.

        The loader indexes chunks as ``y * chunk_x + x`` and each chunk is a
        32x32 block, so the stitched order is: for every chunk row, for every
        local row, for every chunk in that row, that local row's 32 entries.
        Concatenating whole chunks would scramble anything wider than one chunk.

        **A null chunk pointer contributes no entries.** The accepted record set
        carries an internal null in 117 of the 1,420 dominant layer records,
        across 86 maps and 156 of the 4,274 grid cells, and what such a cell
        displays is an open question: the constructor skips it while the
        streaming path substitutes the default container `0x08070808`. The
        substitution is measured to carry no data - that container is a stored
        container declaring zero bytes - so this renders the cell as no-data,
        which is the constructor's reading as well. Whether the *destination*
        would retain stale bytes is not something the ROM image can settle, so it
        is recorded here rather than resolved.
        """
        side = canon.CHUNK_SIDE_TILES
        blanks = (0,) * (side * side)
        chunks = [
            self.chunk_entries.get(address, blanks) if address else blanks
            for address in layer.chunk_addresses
        ]
        out: list[int] = []
        for block_y in range(layer.chunk_y):
            for local_y in range(side):
                for block_x in range(layer.chunk_x):
                    chunk = chunks[block_y * layer.chunk_x + block_x]
                    start = local_y * side
                    out.extend(chunk[start : start + side])
        return tuple(out)

    def render_layer(self, layer: canon.LayerRecord, map_index: int) -> bytes:
        """Assemble a layer image from its chunks' rendered images.

        A chunk image is cached per ``(container, map)`` and copied in 256 rows at
        a time, which keeps a layer of `chunk_x * chunk_y` cells proportional to
        the number of chunks rather than to the number of tiles. A null chunk
        pointer contributes no pixels, so its cell is left transparent.
        """
        side = canon.CHUNK_PIXELS
        width = layer.chunk_x * side
        height = layer.chunk_y * side
        canvas = bytearray(width * height)
        for cell, address in enumerate(layer.chunk_addresses):
            if address == 0:
                continue
            image = self.chunk_image(address, map_index)
            cell_x = (cell % layer.chunk_x) * side
            cell_y = (cell // layer.chunk_x) * side
            for row in range(side):
                target = (cell_y + row) * width + cell_x
                start = row * side
                canvas[target : target + side] = image[start : start + side]
        return bytes(canvas)

    def chunk_image(self, address: int, map_index: int) -> bytes:
        key = (address, map_index)
        cached = self.chunk_images.get(key)
        if cached is None:
            cached = render.render_chunk(
                self.chunk_entries[address], self.char_blocks[map_index].data
            )
            self.chunk_images[key] = cached
        return cached

    def chunk_render_signature(self, address: int, map_index: int) -> bytes:
        """A digest of exactly the pixels that decide a chunk's rendering.

        A chunk image depends on its entries and on the tile bytes of the
        ordinals those entries name - nothing else in the character block can
        reach it. Digesting just those tiles therefore tells whether two maps
        would render the same container identically, at a fraction of the cost of
        rendering it twice.
        """
        entries = self.chunk_entries[address]
        char_data = self.char_blocks[map_index].data
        digest = hashlib.sha256()
        for ordinal in sorted({word & canon.TILE_ENTRY_ORDINAL_MASK for word in entries}):
            start = ordinal * canon.BANK_TILE_BYTES
            digest.update(char_data[start : start + canon.BANK_TILE_BYTES])
        return digest.digest()

    # -- palettes -------------------------------------------------------------

    def export_palettes(self) -> None:
        documents = []
        for palette_id, role, palette, address, encoding, entries in (
            (
                PALETTE_OBJECT_ID,
                "object",
                self.object_palette,
                canon.OBJECT_PALETTE_ADDRESS,
                "bgr555_le_u16",
                canon.OBJECT_PALETTE_ENTRIES,
            ),
            (
                PALETTE_BACKGROUND_ID,
                "background",
                self.bg_palette,
                canon.BG_PALETTE_ADDRESS,
                "rgb888",
                canon.BG_PALETTE_ENTRIES,
            ),
        ):
            width, height, pixels = render.palette_strip(palette)
            relative = naming.palette_relative_path(palette_id)
            artifact = write_rgba_png(
                self.writer, relative, width, height, pixels, b"", already_rgba=True
            )
            document = {
                "palette_id": palette_id,
                "role": role,
                "source_address": f"{address:#010x}",
                "source_file_offset": f"{self.rom.offset(address):#08x}",
                "encoding": encoding,
                "entry_count": entries,
                "rgb": [list(colour) for colour in palette],
                "image": relative,
                "image_width": width,
                "image_height": height,
                "image_sha256": artifact.sha256,
            }
            self.writer.write(
                naming.palette_metadata_relative_path(palette_id),
                meta.dumps(document).encode("utf-8"),
            )
            documents.append(document)
        self.references["palettes"] = documents
        self.count("palettes", len(documents))

    # -- maps -----------------------------------------------------------------

    def export_maps(self) -> None:
        documents = []
        layers_rendered = 0
        layers_classified = 0
        composites = 0
        withheld = 0
        status_counts: dict[str, int] = {}

        for entry in self.map_entries:
            layers = self.layers.get(entry.index)
            block = self.char_blocks.get(entry.index)
            if layers is None or block is None:
                # The graph for this map could not be read; the failure is already
                # recorded, and the map still gets an identity and an explicit
                # status so no MapEntry can vanish from the inventory.
                documents.append(
                    {
                        "map_index": entry.index,
                        "map_entry_address": f"{entry.address:#010x}",
                        "map_entry_file_offset": (
                            f"{self.rom.offset(entry.address):#08x}"
                        ),
                        "key_high": entry.key_high,
                        "key_low": entry.key_low,
                        "source_address": f"{entry.source_address:#010x}",
                        "root_address": f"{entry.root_address:#010x}",
                        "text_index": entry.text_index,
                        "rom_text": self.rom.text(entry.text_index)
                        if entry.text_index is not None
                        else None,
                        "layer_count": 0,
                        "layers": [],
                        "composite_status": "withheld_map_graph_failure",
                    }
                )
                withheld += 1
                status_counts["map_graph_failure"] = (
                    status_counts.get("map_graph_failure", 0) + 1
                )
                continue
            layer_documents = []
            rendered: list[tuple[int, int, int, int, bytes]] = []
            all_accounted = True
            for layer in layers:
                layers_classified += 1
                document: dict[str, object] = {
                    "slot": layer.slot,
                    "record_address": f"{layer.address:#010x}",
                    "record_file_offset": f"{self.rom.offset(layer.address):#08x}",
                    "handler": f"{layer.handler:#010x}",
                    "classification": layer.classification,
                    "chunk_x": layer.chunk_x,
                    "chunk_y": layer.chunk_y,
                    "chunk_cells": layer.chunk_cells,
                    "null_chunk_cells": layer.null_chunk_count,
                }
                if layer.classification == "absent_placeholder":
                    status = "not_graphical_absent_layer"
                elif layer.classification != "dominant":
                    status = "not_rendered_unresolved_handler"
                    all_accounted = False
                else:
                    width = layer.chunk_x * canon.CHUNK_PIXELS
                    height = layer.chunk_y * canon.CHUNK_PIXELS
                    try:
                        grid = self.layer_grid(layer)
                        pixels = render.render_entries(
                            grid,
                            block.data,
                            layer.chunk_x * canon.CHUNK_SIDE_TILES,
                            layer.chunk_y * canon.CHUNK_SIDE_TILES,
                        )
                        addend = self.rom.u8(
                            entry.root_address + canon.ROOT_BG_ADDEND_OFFSET + layer.slot
                        )
                        relative = naming.map_layer_relative_path(entry.index, layer.slot)
                        artifact = write_rgba_png(
                            self.writer, relative, width, height, pixels, self.bg_table
                        )
                        rendered.append((addend, layer.slot, width, height, pixels))
                        layers_rendered += 1
                        status = "rendered"
                        document.update(
                            {
                                "width": width,
                                "height": height,
                                "bg_control_addend": addend,
                                "non_null_chunk_cells": layer.chunk_cells
                                - layer.null_chunk_count,
                                "image": relative,
                                "image_sha256": artifact.sha256,
                            }
                        )
                        document.update(entry_stats(grid))
                    except (
                        canon.CanonicalError,
                        ws.ContainerError,
                        render.RenderError,
                    ) as exc:
                        status = "render_failed"
                        all_accounted = False
                        document["error_kind"] = type(exc).__name__
                        self.fail(
                            "map_layer",
                            "map_entries",
                            f"map:{entry.index:04d}:slot:{layer.slot}",
                            str(exc),
                        )
                status_counts[status] = status_counts.get(status, 0) + 1
                document["status"] = status
                layer_documents.append(document)

            map_document: dict[str, object] = {
                "map_index": entry.index,
                "map_entry_address": f"{entry.address:#010x}",
                "map_entry_file_offset": f"{self.rom.offset(entry.address):#08x}",
                "key_high": entry.key_high,
                "key_low": entry.key_low,
                "source_address": f"{entry.source_address:#010x}",
                "root_address": f"{entry.root_address:#010x}",
                "text_index": entry.text_index,
                "rom_text": self.rom.text(entry.text_index)
                if entry.text_index is not None
                else None,
                "root_extent_x_raw": self.rom.u16(
                    entry.root_address + canon.ROOT_EXTENT_X_OFFSET
                ),
                "root_extent_y_raw": self.rom.u16(
                    entry.root_address + canon.ROOT_EXTENT_Y_OFFSET
                ),
                "bg_control_index": self.rom.u32(
                    entry.root_address + canon.ROOT_BG_CONTROL_OFFSET
                ),
                "connection_count": self.rom.u32(
                    entry.root_address + canon.ROOT_CONNECTION_COUNT_OFFSET
                ),
                "selector_count": self.selector_counts.get(entry.index, 0),
                "animated_tile_count": self.animated_counts.get(entry.index, 0),
                "char_block_tile_count": block.tile_count,
                "layer_count": len(layers),
                "layers": layer_documents,
            }

            if all_accounted and rendered:
                width = max(item[2] for item in rendered)
                height = max(item[3] for item in rendered)
                composed = render.compose_layers(rendered, width, height)
                relative = naming.map_composite_relative_path(entry.index)
                artifact = write_rgba_png(
                    self.writer, relative, width, height, composed, self.bg_table
                )
                composites += 1
                map_document.update(
                    {
                        "composite_status": "produced",
                        "composite_width": width,
                        "composite_height": height,
                        "composite_image": relative,
                        "composite_sha256": artifact.sha256,
                    }
                )
            else:
                withheld += 1
                map_document["composite_status"] = (
                    "withheld_unresolved_layer"
                    if not all_accounted
                    else "withheld_no_renderable_layer"
                )
            documents.append(map_document)

        self.writer.write(
            naming.metadata_relative_path(naming.MAPS_JSON),
            meta.dumps({"schema": 1, "maps": documents}).encode("utf-8"),
        )
        self.count("map_entries", len(self.map_entries))
        self.count("maps_exported", len(documents))
        self.count("maps_with_full_layer_classification", len(self.layers))
        self.count("map_layers_classified", layers_classified)
        self.count("map_layers_exported", layers_rendered)
        self.count("map_composites", composites)
        self.count("map_composites_withheld", withheld)
        for status, count in sorted(status_counts.items()):
            self.count(f"map_layer_status_{status}", count)
        self.references["map_layer_classification"] = dict(sorted(status_counts.items()))
        self.references["map_layer_handlers"] = {
            f"{handler:#010x}": count
            for handler, count in sorted(
                _handler_census(self.layers).items()
            )
        }
        null_cells = sum(
            layer.null_chunk_count
            for records in self.layers.values()
            for layer in records
        )
        null_records = sum(
            1
            for records in self.layers.values()
            for layer in records
            if layer.null_chunk_count
        )
        null_maps = sum(
            1
            for records in self.layers.values()
            if any(layer.null_chunk_count for layer in records)
        )
        self.count("map_layers_with_null_chunk_cell", null_records)
        self.count("map_null_chunk_cells", null_cells)
        self.count("maps_with_null_chunk_cell", null_maps)
        self.references["null_chunk_cells"] = {
            "records": null_records,
            "cells": null_cells,
            "maps": null_maps,
            "default_container_address": f"{canon.DEFAULT_CHUNK_CONTAINER:#010x}",
            "default_container_declared_size": self.rom.u32(
                canon.DEFAULT_CHUNK_CONTAINER + 4
            ),
            "rendered_as": "no_data",
        }

    # -- tiles ----------------------------------------------------------------

    def export_tiles(self) -> None:
        banks = canon.read_banks(self.rom)
        documents = []
        tiles_written = 0
        bank_maps: dict[int, set[int]] = {}
        for map_index, layers in self.layers.items():
            del layers
            root = self.map_entries[map_index].root_address
            try:
                selectors = canon.read_selector_stream(self.rom, root)
            except (canon.CanonicalError, ws.ContainerError):
                continue
            for selector in selectors:
                bank_maps.setdefault(selector >> 8, set()).add(map_index)

        for bank in banks:
            tiles = tuple(
                bank.payload[
                    index * canon.BANK_TILE_BYTES : (index + 1) * canon.BANK_TILE_BYTES
                ]
                for index in range(bank.tile_count)
            )
            width, height, sheet = render.tile_sheet(tiles, BANK_SHEET_COLUMNS)
            sheet_artifact = write_rgba_png(
                self.writer,
                naming.tile_sheet_relative_path(bank.index),
                width,
                height,
                sheet,
                self.bg_table,
            )
            for tile_id, tile in enumerate(tiles):
                write_rgba_png(
                    self.writer,
                    naming.tile_relative_path(bank.index, tile_id),
                    canon.TILE_PIXELS,
                    canon.TILE_PIXELS,
                    tile,
                    self.bg_table,
                )
                tiles_written += 1
            documents.append(
                {
                    "bank_id": bank.index,
                    "pointer_field_address": f"{bank.pointer_field_address:#010x}",
                    "container_address": f"{bank.container_address:#010x}",
                    "container_file_offset": (
                        f"{self.rom.offset(bank.container_address):#08x}"
                    ),
                    "declared_size": bank.declared_size,
                    "packed_bytes": bank.packed_bytes,
                    "tile_count": bank.tile_count,
                    "payload_sha256": sha256_bytes(bank.payload),
                    "tile_id_start": 0,
                    "tile_id_end": bank.tile_count - 1,
                    "decoded_tile_stride_bytes": canon.BANK_TILE_BYTES,
                    "tile_width": canon.TILE_PIXELS,
                    "tile_height": canon.TILE_PIXELS,
                    "palette_id": PALETTE_BACKGROUND_ID,
                    "sheet": naming.tile_sheet_relative_path(bank.index),
                    "sheet_width": width,
                    "sheet_height": height,
                    "sheet_sha256": sheet_artifact.sha256,
                    "referencing_map_count": len(bank_maps.get(bank.index, ())),
                    "referencing_map_indices": sorted(bank_maps.get(bank.index, ())),
                }
            )
        self.writer.write(
            naming.metadata_relative_path(naming.TILE_BANKS_JSON),
            meta.dumps({"schema": 1, "tile_banks": documents}).encode("utf-8"),
        )
        self.count("tile_banks", len(banks))
        self.count("individual_tiles", tiles_written)
        self.count("bank_sheets", len(documents))

    def export_chunks(self) -> None:
        """Export every unique dominant chunk target under one canonical image.

        The image is rendered against the lowest-index map that references the
        container. Where a chunk's pixels differ between referencing maps - the
        accepted corpus has exactly one such container - the variant count is
        recorded so the sharing is visible rather than assumed away.
        """
        render_map_of: dict[int, int] = {}
        for address, maps in self.chunk_maps.items():
            candidates = sorted(set(maps))
            for map_index in candidates:
                if map_index in self.char_blocks:
                    render_map_of[address] = map_index
                    break

        addresses = sorted(self.chunk_entries)
        documents = []
        rendered = 0
        variants = 0
        for chunk_id, address in enumerate(addresses):
            entries = self.chunk_entries[address]
            maps = sorted(set(self.chunk_maps.get(address, ())))
            document: dict[str, object] = {
                "chunk_id": chunk_id,
                "container_address": f"{address:#010x}",
                "container_file_offset": f"{self.rom.offset(address):#08x}",
                "declared_size": canon.CHUNK_DECODED_BYTES,
                "entry_count": canon.CHUNK_ENTRY_COUNT,
                "chunk_side_tiles": canon.CHUNK_SIDE_TILES,
                "width": canon.CHUNK_PIXELS,
                "height": canon.CHUNK_PIXELS,
                "referencing_map_count": len(maps),
                "referencing_map_indices": maps,
                "render_map_index": render_map_of.get(address),
            }
            document.update(entry_stats(entries))
            map_index = render_map_of.get(address)
            if map_index is None:
                document["status"] = "not_rendered_no_referencing_map"
                documents.append(document)
                continue
            try:
                pixels = render.render_chunk(entries, self.char_blocks[map_index].data)
                signatures = {
                    self.chunk_render_signature(address, other)
                    for other in maps
                    if other in self.char_blocks
                }
                if len(signatures) > 1:
                    variants += 1
                    document["distinct_render_variant_count"] = len(signatures)
                relative = naming.chunk_relative_path(chunk_id)
                artifact = write_rgba_png(
                    self.writer,
                    relative,
                    canon.CHUNK_PIXELS,
                    canon.CHUNK_PIXELS,
                    pixels,
                    self.bg_table,
                )
                document["status"] = "rendered"
                document["image"] = relative
                document["image_sha256"] = artifact.sha256
                rendered += 1
            except (
                canon.CanonicalError,
                ws.ContainerError,
                render.RenderError,
            ) as exc:
                document["status"] = "render_failed"
                document["error_kind"] = type(exc).__name__
                self.fail("chunk_render", "chunks", f"{address:#010x}", str(exc))
            documents.append(document)

        self.writer.write(
            naming.metadata_relative_path(naming.CHUNKS_JSON),
            meta.dumps({"schema": 1, "chunks": documents}).encode("utf-8"),
        )
        self.count("chunks", len(addresses))
        self.count("chunks_rendered", rendered)
        self.count("chunks_with_render_variants", variants)
        self.references["chunk_references"] = {
            f"{address:#010x}": sorted(set(self.chunk_maps.get(address, ())))
            for address in addresses
        }

    # -- sprites --------------------------------------------------------------

    def collect_sprite_graph(self) -> None:
        """Walk the accepted sprite graph and decode every graphics container.

        The walk is exactly: 297 definitions -> the count-bounded animation array
        -> `frame_count` rows of four cells -> each cell's frame record -> each
        piece's graphics word. Nothing else reaches a container, and a container
        that does not decode to exactly `dim_0 * dim_1` bytes is a failure rather
        than a silent omission.
        """
        self.definitions = canon.read_sprite_definitions(self.rom)
        for definition in self.definitions:
            for slot, pointer in enumerate(definition.animation_pointers):
                if pointer == 0:
                    continue
                animation = self.animation(pointer, definition.sprite_id, slot)
                if animation is None:
                    continue
                for frame_address in animation.cell_addresses:
                    frame = self.frame(frame_address)
                    if frame is None:
                        continue
                    for piece in frame.pieces:
                        try:
                            self.graphic_for(
                                piece.graphics_address,
                                piece.dim_0,
                                piece.dim_1,
                                piece.colour_256,
                            )
                        except (
                            canon.CanonicalError,
                            ws.ContainerError,
                            render.RenderError,
                        ) as exc:
                            self.fail(
                                "graphics",
                                "sprite_graphics",
                                f"{piece.graphics_address:#010x}",
                                str(exc),
                            )

    def animation(
        self, address: int, sprite_id: int, slot: int
    ) -> canon.AnimationRecord | None:
        cached = self.animations.get(address)
        if cached is not None:
            return cached
        try:
            record = canon.read_animation(self.rom, address)
        except (canon.CanonicalError, ws.ContainerError) as exc:
            self.fail(
                "animation",
                "animation_slots",
                f"sprite:{sprite_id}:slot:{slot}",
                str(exc),
            )
            return None
        self.animations[address] = record
        return record

    def frame(self, address: int) -> canon.FrameRecord | None:
        cached = self.frames.get(address)
        if cached is not None:
            return cached
        try:
            record = canon.read_frame(self.rom, address)
        except (canon.CanonicalError, ws.ContainerError) as exc:
            self.fail("frame", "frames", f"{address:#010x}", str(exc))
            return None
        self.frames[address] = record
        return record

    def graphic_for(
        self, address: int, width: int, height: int, colour_256: bool
    ) -> tuple[bytes, tuple[int, int]]:
        """Unswizzled indices and extents for a graphics container, cached.

        The cache is keyed by the container address and holds the *unflipped*
        image: the horizontal flip is a stored bit on the piece, so it is applied
        during frame assembly and never baked into the shared resource.
        """
        cached = self.graphic_indices.get(address)
        if cached is not None:
            extent = self.graphic_extents[address]
            if extent != (width, height):
                raise canon.CanonicalError(
                    f"graphics container {address:#010x} is referenced as both "
                    f"{extent[0]}x{extent[1]} and {width}x{height}"
                )
            return cached, extent
        graphic = canon.read_graphic(self.rom, address, width, height, colour_256)
        indices = render.unswizzle_tiles(
            graphic.payload, width, height, colour_256=colour_256
        )
        self.graphic_indices[address] = indices
        self.graphic_extents[address] = (width, height)
        return indices, (width, height)

    def export_sprite_graphics(self) -> None:
        """Export every structured sprite-graphics container a piece reaches."""
        documents = []
        for graphic_id, address in enumerate(sorted(self.graphic_indices)):
            width, height = self.graphic_extents[address]
            indices = self.graphic_indices[address]
            relative = naming.graphic_relative_path(graphic_id)
            artifact = write_rgba_png(
                self.writer, relative, width, height, indices, self.object_table
            )
            documents.append(
                {
                    "graphic_id": graphic_id,
                    "container_address": f"{address:#010x}",
                    "container_file_offset": f"{self.rom.offset(address):#08x}",
                    "declared_size": width * height,
                    "width": width,
                    "height": height,
                    "colour_256": True,
                    "palette_id": PALETTE_OBJECT_ID,
                    "image": relative,
                    "image_sha256": artifact.sha256,
                }
            )
        self.writer.write(
            naming.metadata_relative_path(naming.SPRITE_GRAPHICS_JSON),
            meta.dumps({"schema": 1, "sprite_graphics": documents}).encode("utf-8"),
        )
        self.count("structured_sprite_graphics", len(documents))

    def export_sprites(self) -> None:
        definition_documents = []
        animation_documents = []
        slots = 0
        non_null = 0
        directional_images = 0
        sheets = 0

        for definition in self.definitions:
            slot_documents = []
            for slot, pointer in enumerate(definition.animation_pointers):
                slots += 1
                if pointer == 0:
                    slot_documents.append({"slot": slot, "null": True})
                    continue
                non_null += 1
                animation = self.animation(pointer, definition.sprite_id, slot)
                if animation is None:
                    slot_documents.append(
                        {
                            "slot": slot,
                            "null": False,
                            "animation_address": f"{pointer:#010x}",
                            "status": "decode_failed",
                        }
                    )
                    continue
                slot_document = {
                    "slot": slot,
                    "null": False,
                    "animation_address": f"{pointer:#010x}",
                    "frame_count": animation.frame_count,
                    "direction_cells": animation.direction_cells,
                    "directory": naming.animation_relative_directory(
                        definition.sprite_id, slot
                    ),
                }
                try:
                    cells = self.render_animation(definition.sprite_id, slot, animation)
                except (
                    canon.CanonicalError,
                    ws.ContainerError,
                    render.RenderError,
                ) as exc:
                    slot_document["status"] = "render_failed"
                    self.fail(
                        "animation_render",
                        "animation_slots",
                        f"sprite:{definition.sprite_id}:slot:{slot}",
                        str(exc),
                    )
                    slot_documents.append(slot_document)
                    continue
                directional_images += cells
                sheets += 1
                slot_document["status"] = "rendered"
                slot_documents.append(slot_document)
                animation_documents.append(
                    {
                        "animation_address": f"{pointer:#010x}",
                        "frame_count": animation.frame_count,
                        "direction_cells": animation.direction_cells,
                        "cell_addresses": [
                            f"{address:#010x}" for address in animation.cell_addresses
                        ],
                        "sprite_id": definition.sprite_id,
                        "slot": slot,
                    }
                )
            definition_documents.append(
                {
                    "sprite_id": definition.sprite_id,
                    "run_index": definition.run_index,
                    "definition_address": f"{definition.address:#010x}",
                    "definition_file_offset": (
                        f"{self.rom.offset(definition.address):#08x}"
                    ),
                    "animation_array_offset": canon.SPRITE_ANIMATION_ARRAY_OFFSET,
                    "animation_slots": definition.slots,
                    "non_null_slots": definition.non_null_slots,
                    "null_slots": definition.slots - definition.non_null_slots,
                    "extent_end": f"{definition.extent_end:#010x}",
                    "slots": slot_documents,
                }
            )

        self.writer.write(
            naming.metadata_relative_path(naming.SPRITES_JSON),
            meta.dumps({"schema": 1, "sprites": definition_documents}).encode("utf-8"),
        )
        self.writer.write(
            naming.metadata_relative_path(naming.ANIMATIONS_JSON),
            meta.dumps(
                {
                    "schema": 1,
                    "unique_animation_count": len(self.animations),
                    "unique_animations": [
                        {
                            "animation_address": f"{address:#010x}",
                            "animation_file_offset": (
                                f"{self.rom.offset(address):#08x}"
                            ),
                            "frame_count": self.animations[address].frame_count,
                            "direction_cells": (
                                self.animations[address].direction_cells
                            ),
                            "cell_addresses": [
                                f"{cell:#010x}"
                                for cell in self.animations[address].cell_addresses
                            ],
                        }
                        for address in sorted(self.animations)
                    ],
                    "references": animation_documents,
                }
            ).encode("utf-8"),
        )
        self.write_frames_document()

        self.count("sprite_definitions", len(self.definitions))
        self.count("animation_slots", slots)
        self.count("non_null_animations", non_null)
        self.count("null_animation_slots", slots - non_null)
        self.count("unique_animations", len(self.animations))
        self.count("directional_frame_images", directional_images)
        self.count("animation_sheets", sheets)
        self.count("unique_frames", len(self.frames))
        self.count("sprite_pieces", sum(f.piece_count for f in self.frames.values()))
        self.count(
            "multipart_frames",
            sum(1 for frame in self.frames.values() if frame.piece_count > 1),
        )
        self.count(
            "piece_references_over_animation_references",
            self.piece_references_over_animation_references,
        )

    def render_animation(
        self, sprite_id: int, slot: int, animation: canon.AnimationRecord
    ) -> int:
        """Render every frame index x direction index of one animation."""
        cells: list[tuple[int, int, bytes]] = []
        written = 0
        for frame_index in range(animation.frame_count):
            for direction_index in range(canon.DIRECTION_COUNT):
                address = animation.cell_address(frame_index, direction_index)
                frame = self.frame(address)
                if frame is None:
                    raise canon.CanonicalError(
                        f"frame at {address:#010x} could not be read"
                    )
                pixels = self.assemble(frame)
                relative = naming.frame_direction_relative_path(
                    sprite_id, slot, frame_index, direction_index
                )
                write_rgba_png(
                    self.writer,
                    relative,
                    frame.width,
                    frame.height,
                    pixels,
                    self.object_table,
                )
                cells.append((frame.width, frame.height, pixels))
                self.piece_references_over_animation_references += frame.piece_count
                written += 1
        width, height, sheet = render.frame_sheet(cells, ANIMATION_SHEET_COLUMNS)
        write_rgba_png(
            self.writer,
            naming.animation_sheet_relative_path(sprite_id, slot),
            width,
            height,
            sheet,
            self.object_table,
        )
        return written

    def assemble(self, frame: canon.FrameRecord) -> bytes:
        return render.assemble_frame(frame, self.graphic_indices, self.graphic_extents)

    def write_frames_document(self) -> None:
        documents = []
        for address in sorted(self.frames):
            frame = self.frames[address]
            documents.append(
                {
                    "frame_address": f"{address:#010x}",
                    "frame_file_offset": f"{self.rom.offset(address):#08x}",
                    "piece_count": frame.piece_count,
                    "min_x": frame.min_x,
                    "min_y": frame.min_y,
                    "width": frame.width,
                    "height": frame.height,
                    "pieces": [
                        {
                            "piece_index": piece.index,
                            "piece_address": f"{piece.address:#010x}",
                            "x": piece.x,
                            "y": piece.y,
                            "dim_0": piece.dim_0,
                            "dim_1": piece.dim_1,
                            "attributes": f"{piece.attributes:#010x}",
                            "shape": piece.shape,
                            "size": piece.size,
                            "colour_256": piece.colour_256,
                            "horizontal_flip": piece.horizontal_flip,
                            "vertical_flip": piece.vertical_flip,
                            "graphics_address": f"{piece.graphics_address:#010x}",
                        }
                        for piece in frame.pieces
                    ],
                }
            )
        self.writer.write(
            naming.metadata_relative_path(naming.FRAMES_JSON),
            meta.dumps({"schema": 1, "frames": documents}).encode("utf-8"),
        )

    def export_aliases(self) -> None:
        """Record the party-slot alias mechanism structurally.

        Ids below the definition run's floor do not index the run. The engine
        branches at `cmp r0,#0xa`, resolves a party slot through a `0x68`-stride
        runtime record, indexes a 24-byte-record table at `0x086B82EC` and reads a
        `u16` sprite id from record `+0x0E`. The runtime party record is not
        ROM-resident, so no static alias-id-to-sprite-id mapping is claimed: the
        mechanism is recorded and each alias id stays unresolved.
        """
        self.writer.write(
            naming.metadata_relative_path(naming.ALIASES_JSON),
            meta.dumps(
                {
                    "schema": 1,
                    "party_slot_aliases": {
                        "ids": list(canon.SPRITE_PARTY_ALIAS_IDS),
                        "kind": "party_slot_alias",
                        "accessor_address": f"{canon.PARTY_ALIAS_ACCESSOR:#010x}",
                        "reentry_address": f"{canon.PARTY_ALIAS_REENTRY:#010x}",
                        "index_table_address": f"{canon.PARTY_ALIAS_INDEX_TABLE:#010x}",
                        "index_record_stride": canon.PARTY_ALIAS_INDEX_STRIDE,
                        "index_id_offset": canon.PARTY_ALIAS_INDEX_ID_OFFSET,
                        "runtime_party_record_in_rom": False,
                        "sprite_id_resolved": False,
                    },
                    "map_entry_text": [
                        {
                            "map_index": entry.index,
                            "text_index": entry.text_index,
                            "rom_text": self.rom.text(entry.text_index),
                        }
                        for entry in self.map_entries
                        if entry.text_index is not None
                    ],
                }
            ).encode("utf-8"),
        )

    # -- audit ----------------------------------------------------------------

    def count_document(self) -> dict[str, object]:
        """Measured populations beside the accepted expectations.

        Only the gates for the subsystems this run selected are reported, so a
        ``--maps``-only run is not judged against the sprite populations it was
        never asked to produce.
        """
        wanted = set()
        if "maps" in self.subsystems:
            wanted.update(
                {"map_entries", "maps_exported", "map_layers_classified"}
            )
        if "tiles" in self.subsystems:
            wanted.update({"chunks", "tile_banks"})
        if "sprites" in self.subsystems:
            wanted.update(
                {
                    "sprite_definitions",
                    "animation_slots",
                    "non_null_animations",
                    "unique_frames",
                    "sprite_pieces",
                    "multipart_frames",
                    "structured_sprite_graphics",
                }
            )
        entries = []
        for key, expected in sorted(EXPECTED_POPULATIONS.items()):
            if key not in wanted:
                continue
            actual = self.counters.get(key)
            entries.append(
                {
                    "key": key,
                    "expected": expected,
                    "measured": actual,
                    "accounted": actual == expected,
                }
            )
        return {
            "schema": 1,
            "subsystems": sorted(self.subsystems),
            "gates": entries,
            "measured": dict(sorted(self.counters.items())),
            "failure_count": len(self.failures),
        }

    def duplicate_document(self) -> dict[str, object]:
        groups: dict[str, list[str]] = {}
        for artifact in self.writer.artifacts:
            groups.setdefault(artifact.sha256, []).append(artifact.relative_path)
        duplicates = {
            digest: sorted(paths) for digest, paths in groups.items() if len(paths) > 1
        }
        return {
            "schema": 1,
            "artifact_count": len(self.writer.artifacts),
            "distinct_content_count": len(groups),
            "duplicate_group_count": len(duplicates),
            "duplicate_groups": duplicates,
        }

    def write_audit(
        self,
        *,
        options: dict[str, object],
        rom_sha256: str,
        foreign_entries: tuple[str, ...] = (),
    ) -> None:
        self.audit_root.mkdir(parents=True, exist_ok=True)
        meta.write(self.audit_root / "counts.json", self.count_document())
        meta.write(
            self.audit_root / "manifest.json",
            {
                "tool": TOOL_NAME,
                "tool_version": TOOL_VERSION,
                "python_version": sys.version.split()[0],
                "zlib_version": zlib.ZLIB_VERSION,
                "png_compression_level": png.COMPRESSION_LEVEL,
                "canonical_rom_sha256": rom_sha256,
                "rom_bytes": self.rom.size,
                "resource_output_root": str(self.output_root),
                "audit_output_root": str(self.audit_root),
                "options": options,
                "foreign_entries": list(foreign_entries),
                "artifact_count": len(self.writer.artifacts),
                "resource_bytes": self.writer.total_bytes,
                "elapsed_seconds": round(time.monotonic() - self.started, 3),
            },
        )
        meta.write(
            self.audit_root / "failures.json",
            {
                "failure_count": len(self.failures),
                "failures": [failure.as_document() for failure in self.failures],
            },
        )
        meta.write(self.audit_root / "references.json", self.references)
        meta.write(self.audit_root / "duplicate_groups.json", self.duplicate_document())
        meta.write_text(
            self.audit_root / "hashes.csv",
            meta.csv_rows(
                ("relative_path", "bytes", "sha256"),
                (
                    (artifact.relative_path, artifact.size, artifact.sha256)
                    for artifact in sorted(
                        self.writer.artifacts, key=lambda item: item.relative_path
                    )
                ),
            ),
        )

    # -- driver ---------------------------------------------------------------

    def run(
        self,
        *,
        maps: bool,
        tiles: bool,
        sprites: bool,
        audit_only: bool,
        options: dict[str, object],
        rom_sha256: str,
        foreign_entries: tuple[str, ...] = (),
    ) -> None:
        self.writer.enabled = not audit_only
        self.subsystems = set()
        if maps:
            self.subsystems.add("maps")
        if tiles:
            self.subsystems.add("tiles")
        if sprites:
            self.subsystems.add("sprites")
        if maps or tiles:
            self.collect_map_graph()
        if sprites:
            self.collect_sprite_graph()
        if maps:
            self.export_maps()
        if tiles:
            self.export_tiles()
            self.export_chunks()
        if sprites:
            self.export_sprites()
            self.export_sprite_graphics()
        self.export_palettes()
        self.export_aliases()
        self.write_audit(
            options=options, rom_sha256=rom_sha256, foreign_entries=foreign_entries
        )


def _handler_census(
    layers: dict[int, tuple[canon.LayerRecord, ...]]
) -> dict[int, int]:
    census: dict[int, int] = {}
    for records in layers.values():
        for layer in records:
            census[layer.handler] = census.get(layer.handler, 0) + 1
    return census


# --- comparison --------------------------------------------------------------

def compare_with(other_root: Path, expected_hashes: Path) -> tuple[bool, dict[str, object]]:
    """Diff an earlier export tree against this run's recorded artifact hashes."""
    if not expected_hashes.exists():
        raise ExportError(f"no audit hash table at {expected_hashes}")
    expected: dict[str, str] = {}
    for line in expected_hashes.read_text(encoding="utf-8").splitlines()[1:]:
        if not line:
            continue
        path, _size, digest = line.rsplit(",", 2)
        expected[path.strip('"')] = digest
    actual: dict[str, str] = {}
    for path in sorted(other_root.rglob("*")):
        if path.is_file():
            actual[path.relative_to(other_root).as_posix()] = sha256_bytes(
                path.read_bytes()
            )
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    differing = sorted(
        name for name in set(expected) & set(actual) if expected[name] != actual[name]
    )
    result = {
        "missing_count": len(missing),
        "extra_count": len(extra),
        "differing_count": len(differing),
        "missing": missing[:50],
        "extra": extra[:50],
        "differing": differing[:50],
    }
    return (not missing and not extra and not differing), result


# --- CLI ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.export.buu_resource_export",
        description=(
            "Export the canonical Buu's Fury resource library and its audit "
            "directory from the accepted post-LOGX schemas."
        ),
    )
    parser.add_argument("--rom", required=True, type=Path,
                        help="path to the canonical ROM (read-only)")
    parser.add_argument("--output", required=True, type=Path,
                        help="resource output root, outside the git repository")
    parser.add_argument("--audit", type=Path, default=None,
                        help="audit root (default: <OUTPUT>_Audit)")
    parser.add_argument("--maps", action="store_true", help="export the map side")
    parser.add_argument("--tiles", action="store_true", help="export tiles and chunks")
    parser.add_argument("--sprites", action="store_true", help="export the sprite side")
    parser.add_argument("--all", action="store_true", help="export everything (default)")
    parser.add_argument("--audit-only", action="store_true",
                        help="analyse and write the audit directory only")
    parser.add_argument("--force", action="store_true",
                        help="write into a non-empty output root")
    parser.add_argument("--compare", type=Path, default=None,
                        help="diff an earlier export root against this run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    output_root = args.output.resolve()
    audit_root = (args.audit or audit_root_for(output_root)).resolve()

    if audit_root == output_root:
        raise ExportError("the audit root must differ from the resource root")
    if output_root in audit_root.parents or audit_root in output_root.parents:
        raise ExportError("neither output root may contain the other")

    ensure_outside_repository(output_root, "resource output root")
    ensure_outside_repository(audit_root, "audit output root")

    if not args.audit_only and output_root.exists() and any(output_root.iterdir()):
        if not args.force:
            raise ExportError(
                f"{output_root} is not empty; pass --force to replace its contents"
            )
        foreign = clear_generated(output_root)
    else:
        foreign = ()

    rom_bytes = read_canonical_rom(args.rom)
    digest_before = sha256_bytes(rom_bytes)

    every = args.all or not (args.maps or args.tiles or args.sprites)
    exporter = Exporter(canon.Rom(rom_bytes), output_root, audit_root)
    exporter.run(
        maps=every or args.maps,
        tiles=every or args.tiles,
        sprites=every or args.sprites,
        audit_only=args.audit_only,
        options={
            "maps": every or args.maps,
            "tiles": every or args.tiles,
            "sprites": every or args.sprites,
            "audit_only": args.audit_only,
        },
        rom_sha256=digest_before,
        foreign_entries=foreign,
    )

    digest_after = sha256_bytes(args.rom.read_bytes())
    if digest_after != digest_before:
        raise ExportError(
            "the canonical ROM changed during the export; refusing the result"
        )

    counts = exporter.count_document()
    unaccounted = [gate["key"] for gate in counts["gates"] if not gate["accounted"]]
    status = "OK" if not exporter.failures and not unaccounted else "INCOMPLETE"
    print(
        json.dumps(
            {
                "status": status,
                "resource_output_root": str(output_root),
                "audit_output_root": str(audit_root),
                "artifact_count": len(exporter.writer.artifacts),
                "resource_bytes": exporter.writer.total_bytes,
                "failure_count": len(exporter.failures),
                "unaccounted_gates": unaccounted,
                "canonical_rom_sha256": digest_before,
            },
            sort_keys=True,
        )
    )

    if args.compare is not None:
        same, result = compare_with(
            args.compare.resolve(), audit_root / "hashes.csv"
        )
        print(
            json.dumps(
                {"determinism": "PASS" if same else "FAIL", **result}, sort_keys=True
            )
        )
        if not same:
            return 1

    if not args.audit_only:
        prose_files = meta.scan_for_prose_files(output_root)
        prose_keys = meta.scan_for_prose_keys(output_root)
        if prose_files or prose_keys:
            print(
                json.dumps(
                    {
                        "prose_files": [str(path) for path in prose_files],
                        "prose_metadata": [[str(p), d] for p, d in prose_keys],
                    },
                    sort_keys=True,
                )
            )
            return 1

    return 0 if status == "OK" else 2


if __name__ == "__main__":
    sys.exit(main())
