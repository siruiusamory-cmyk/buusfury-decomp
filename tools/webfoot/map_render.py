"""Read-only ROM map renderer: ``render_map(rom, "map:0040")`` -> pixels.

MAP-VIS-002 closes the former VRAM oracle: the scene descriptor points to a
delta-coded tile-selector container, a tileset-container array, optional
animated-tile records, and four logical layer records.  The renderer reconstructs
those ROM objects directly and stitches every 32x32 layer chunk into the complete
logical map.  Runtime camera streaming into 32x32 hardware screenblocks is not a
map-format property and is intentionally not emulated.

The older VRAM-backed core remains as an independent regression oracle through
:func:`render_map_from_vram` and :func:`render_map_vram_reference`.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import struct

from .formats import bg_tilemap
from .formats import map_entry as me
from .formats import sprite_graphics
from .formats import webfoot_lz
from .profile import RomProfileCatalog
from .rom import identify_rom


class MapRenderError(ValueError):
    """Raised when a map cannot be resolved or rendered.

    One class: every caller either gets a render or is told, in the message, the
    exact link that failed.
    """


class UnsupportedMapAssemblyVariant(MapRenderError):
    """The descriptor uses a map assembly variant not yet proven."""


#: GBA ROM addresses map to file offsets by subtracting this base.
GBA_ROM_BASE = 0x08000000

#: MapEntry table: base address and record stride. CONFIRMED - the same values
#: `formats.map_entry` uses, restated as the arithmetic this module performs
#: directly (index -> record -> +0x2C) without loading the whole table.
MAP_ENTRY_TABLE_ADDRESS = 0x0808E2E0
MAP_ENTRY_STRIDE = me.MAP_ENTRY_SIZE  # 0x38
MAP_ENTRY_SCENE_POINTER_OFFSET = 0x2C  # variation_array_pointer_raw

#: Engine-global background palette: 256 RGB888 triples, uncompressed. A CONSTANT
#: for every map. Each channel byte is 8-bit but the hardware only keeps 5 bits,
#: so the display value is ``v>>3`` requantised then expanded - which reproduces
#: the live VRAM palette (an oracle's ``palette.bin``) verbatim at full brightness.
BG_PALETTE_ADDRESS = 0x080701B0
BG_PALETTE_ENTRIES = 256
BG_PALETTE_BYTES = BG_PALETTE_ENTRIES * 3

#: Regular-BG screen-size bits -> (width, height) in tiles (GBATEK).
SCREEN_SIZE_TILES = {0: (32, 32), 1: (64, 32), 2: (32, 64), 3: (64, 64)}

TILE_BYTES = bg_tilemap.TILE_BYTES_8BPP
SCREEN_CHUNK_BYTES = bg_tilemap.SCREEN_BLOCK_BYTES
SCREEN_CHUNK_SIDE = 32
SUPPORTED_LAYER_HANDLER = 0x08008087
MAX_TILE_INDEX = 0x3FF

#: Only the canonical Buu's Fury USA image is supported. The map-entry table
#: address and BG-palette address are specific to it; a different image would
#: resolve different bytes and must be refused.
SUPPORTED_ROM_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


@dataclass(frozen=True, slots=True)
class LayerSpec:
    """One BG layer's block wiring, as the hardware's BGxCNT would carry it."""

    bg: int
    char_base_block: int
    screen_base_block: int
    screen_size_bits: int
    priority: int
    color_256: bool


@dataclass(frozen=True, slots=True)
class RenderedLayer:
    """One composed BG layer: linear 8bpp indices plus its wiring."""

    bg: int
    priority: int
    char_base_block: int
    screen_base_block: int
    width: int
    height: int
    pixels: bytes

    @property
    def nonzero(self) -> int:
        return sum(1 for value in self.pixels if value)


@dataclass(frozen=True, slots=True)
class LogicalLayer:
    """One complete ROM-resident BG layer, before pixel rendering."""

    bg: int
    priority: int
    width_tiles: int
    height_tiles: int
    entries: tuple[bg_tilemap.ScreenEntry, ...]
    record_address: int
    chunk_addresses: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class MapAssembly:
    """ROM-derived character data and complete logical BG layers."""

    descriptor_address: int
    char_data: bytes
    selectors: tuple[int, ...]
    layers: tuple[LogicalLayer, ...]
    tileset_addresses: tuple[int, ...]
    animation_addresses: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class MapRenderResult:
    """The rendered map: per-layer indices, composite, palette, provenance."""

    semantic_map_id: str
    width: int
    height: int
    layers: tuple[RenderedLayer, ...]
    composite: bytes
    palette: tuple[tuple[int, int, int], ...]
    provenance: dict[str, object]
    warnings: tuple[str, ...] = field(default_factory=tuple)


#: Runtime effects intentionally excluded from the immutable-ROM render.
_ROM_RENDER_WARNINGS = (
    "complete logical map rendered; camera-relative circular screenblock storage not emulated",
    "BG palette from ROM 0x080701B0 at full brightness; runtime fade not applied",
    "ROM-resident animated tiles rendered at frame 0",
)

_VRAM_RENDER_WARNINGS = (
    "tile graphics and screenblocks sourced from a static VRAM reference capture",
    "BG palette from ROM 0x080701B0 at full brightness; runtime fade not applied",
    "animated tiles shown at the capture's runtime frame",
)


# --- resolution --------------------------------------------------------------

def _file_offset(address: int, rom_size: int) -> int:
    offset = address - GBA_ROM_BASE
    if not 0 <= offset < rom_size:
        raise MapRenderError(
            f"ROM pointer {address:#010x} (file {offset:#x}) is outside the "
            f"{rom_size:#x}-byte image"
        )
    return offset


def _u32(rom: bytes, address: int) -> int:
    offset = _file_offset(address, len(rom))
    if offset + 4 > len(rom):
        raise MapRenderError(f"u32 at {address:#010x} runs past the image")
    return struct.unpack_from("<I", rom, offset)[0]


def _verify_supported_rom(rom: bytes) -> None:
    """Refuse profile-specific rendering against any unverified byte image."""
    actual = hashlib.sha256(rom).hexdigest()
    if actual != SUPPORTED_ROM_SHA256:
        raise MapRenderError(
            "render_map requires canonical Buu's Fury USA rev0 ROM bytes; "
            f"got SHA-256 {actual}"
        )


def parse_map_id(map_id: str) -> int:
    """``"map:0040"`` -> ``40``. Decimal, matching this project's map identity.

    Fails closed on anything that is not the ``map:NNNN`` spelling, so a caller
    that hands a raw offset or a hex slug is refused rather than silently
    misresolved.
    """
    if not isinstance(map_id, str) or not map_id.startswith("map:"):
        raise MapRenderError(f"{map_id!r} is not a map identity (map:NNNN)")
    try:
        index = int(map_id[len("map:"):])
    except ValueError as exc:
        raise MapRenderError(f"{map_id!r} is not a map identity (map:NNNN)") from exc
    if index < 0:
        raise MapRenderError(f"{map_id!r} has a negative map index")
    return index


def resolve_descriptor(rom: bytes, map_index: int) -> tuple[int, int, int]:
    """``map_index`` -> ``(map_entry_address, scene_pointer, descriptor_address)``.

    Pure ROM arithmetic, general for every map: MapEntry[N] + 0x2C is a pointer
    into the content stream whose target is the scene descriptor. This is the
    ROM-proven identity chain.
    """
    map_entry_address = MAP_ENTRY_TABLE_ADDRESS + map_index * MAP_ENTRY_STRIDE
    scene_pointer = map_entry_address + MAP_ENTRY_SCENE_POINTER_OFFSET
    # Bounds the record itself before dereferencing.
    _file_offset(map_entry_address + MAP_ENTRY_STRIDE - 1, len(rom))
    indirect = _u32(rom, scene_pointer)
    descriptor = _u32(rom, indirect)
    _file_offset(descriptor, len(rom))
    return map_entry_address, indirect, descriptor


# --- palette (ROM-proven) ----------------------------------------------------

def decode_bg_palette(rom: bytes) -> tuple[tuple[int, int, int], ...]:
    """The 256-colour global BG palette from ROM 0x080701B0 as display RGB.

    Each RGB888 channel is requantised to the hardware's 5 bits and expanded
    back, so the result matches live VRAM (5-bit-per-channel) at full brightness
    rather than the raw 8-bit ROM bytes. This is the proven full-brightness
    palette; using it renders a mid-fade capture (e.g. map 39) at correct colour.
    """
    offset = _file_offset(BG_PALETTE_ADDRESS, len(rom))
    if offset + BG_PALETTE_BYTES > len(rom):
        raise MapRenderError(f"BG palette at {BG_PALETTE_ADDRESS:#010x} runs past the image")

    def display(byte: int) -> int:
        five = byte >> 3
        return (five << 3) | (five >> 2)

    return tuple(
        (display(rom[offset + i * 3]), display(rom[offset + i * 3 + 1]), display(rom[offset + i * 3 + 2]))
        for i in range(BG_PALETTE_ENTRIES)
    )


# --- ROM-resident assembly ---------------------------------------------------

def _unpack_at(rom: bytes, address: int, *, expected: int | None = None) -> bytes:
    try:
        container = webfoot_lz.unpack(rom, _file_offset(address, len(rom)))
    except webfoot_lz.ContainerError as exc:
        raise UnsupportedMapAssemblyVariant(
            f"container at {address:#010x} did not decode: {exc}"
        ) from exc
    if expected is not None and len(container.data) != expected:
        raise UnsupportedMapAssemblyVariant(
            f"container at {address:#010x} decoded {len(container.data):#x} "
            f"bytes, expected {expected:#x}"
        )
    return container.data


def decode_tile_selectors(rom: bytes, descriptor_address: int) -> tuple[int, ...]:
    """Decode descriptor ``+0x48`` into absolute ``bank:tile`` selectors.

    Entry zero is absolute.  Every later little-endian u16 is a delta from the
    preceding absolute selector, biased by one; arithmetic wraps to u16 exactly
    like the engine's ``ldrh/add/strh`` loop at ``0x08009C02..0x08009C12``.
    """
    remap_address = _u32(rom, descriptor_address + 0x48)
    raw = _unpack_at(rom, remap_address)
    if not raw or len(raw) % 2:
        raise UnsupportedMapAssemblyVariant(
            f"tile selector container at {remap_address:#010x} has "
            f"non-even decoded size {len(raw)}"
        )
    selectors = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    for index in range(1, len(selectors)):
        selectors[index] = (selectors[index] + selectors[index - 1] + 1) & 0xFFFF
    return tuple(selectors)


def _decode_layers(rom: bytes, descriptor_address: int) -> tuple[LogicalLayer, ...]:
    layers: list[LogicalLayer] = []
    for bg in range(4):
        record = _u32(rom, descriptor_address + 0x14 + bg * 4)
        if record == 0:
            continue
        record_offset = _file_offset(record, len(rom))
        _file_offset(record + 0x17, len(rom))
        width_blocks = rom[record_offset + 0x14]
        height_blocks = rom[record_offset + 0x15]
        if width_blocks == 0 and height_blocks == 0:
            continue
        if not width_blocks or not height_blocks:
            raise UnsupportedMapAssemblyVariant(
                f"BG{bg} layer at {record:#010x} has partial zero dimensions "
                f"{width_blocks}x{height_blocks}"
            )
        handler = _u32(rom, record)
        if handler != SUPPORTED_LAYER_HANDLER:
            raise UnsupportedMapAssemblyVariant(
                f"BG{bg} layer handler {handler:#010x} is not the proven "
                f"{SUPPORTED_LAYER_HANDLER:#010x} variant"
            )
        chunks: list[tuple[bg_tilemap.ScreenEntry, ...]] = []
        chunk_addresses: list[int] = []
        for chunk_index in range(width_blocks * height_blocks):
            address = _u32(rom, record + 0x18 + chunk_index * 4)
            raw = _unpack_at(rom, address, expected=SCREEN_CHUNK_BYTES)
            words = struct.unpack("<1024H", raw)
            chunks.append(tuple(bg_tilemap.ScreenEntry.decode(word) for word in words))
            chunk_addresses.append(address)

        width_tiles = width_blocks * SCREEN_CHUNK_SIDE
        height_tiles = height_blocks * SCREEN_CHUNK_SIDE
        entries: list[bg_tilemap.ScreenEntry] = []
        # The loader indexes chunks as y * width_blocks + x at
        # 0x08007C82..0x08007C90. Stitch each row of each 32x32 chunk into the
        # corresponding complete logical row.
        for block_y in range(height_blocks):
            for local_y in range(SCREEN_CHUNK_SIDE):
                for block_x in range(width_blocks):
                    chunk = chunks[block_y * width_blocks + block_x]
                    start = local_y * SCREEN_CHUNK_SIDE
                    entries.extend(chunk[start:start + SCREEN_CHUNK_SIDE])

        layers.append(
            LogicalLayer(
                bg=bg,
                priority=rom[_file_offset(descriptor_address + 4 + bg, len(rom))],
                width_tiles=width_tiles,
                height_tiles=height_tiles,
                entries=tuple(entries),
                record_address=record,
                chunk_addresses=tuple(chunk_addresses),
            )
        )
    if not layers:
        raise UnsupportedMapAssemblyVariant("scene descriptor has no supported BG layers")
    return tuple(layers)


def reconstruct_map_assembly(rom: bytes, descriptor_address: int) -> MapAssembly:
    """Reconstruct static-frame character bytes and complete logical layers."""
    selectors = decode_tile_selectors(rom, descriptor_address)
    atlas_array = _u32(rom, descriptor_address + 0x4C)
    atlas_cache: dict[int, bytes] = {}
    atlas_addresses: dict[int, int] = {}
    selected_tiles: list[bytes] = []
    for selector in selectors:
        bank, source_tile = selector >> 8, selector & 0xFF
        if bank not in atlas_cache:
            address = _u32(rom, atlas_array + bank * 4)
            atlas_cache[bank] = _unpack_at(rom, address, expected=0x4000)
            atlas_addresses[bank] = address
        atlas = atlas_cache[bank]
        start = source_tile * TILE_BYTES
        if start + TILE_BYTES > len(atlas):
            raise UnsupportedMapAssemblyVariant(
                f"selector {selector:#06x} reads tile {source_tile} past "
                f"atlas bank {bank} ({len(atlas):#x} bytes)"
            )
        selected_tiles.append(atlas[start:start + TILE_BYTES])

    layers = _decode_layers(rom, descriptor_address)
    referenced = {entry.tile_index for layer in layers for entry in layer.entries}
    animation_count = _u32(rom, descriptor_address + 0x0C)
    animation_array = _u32(rom, descriptor_address + 0x10)
    animations: list[tuple[int, int, bytes, int]] = []
    animation_addresses: list[int] = []
    for index in range(animation_count):
        animation = _u32(rom, animation_array + index * 4)
        offset = _file_offset(animation, len(rom))
        frame_count = rom[offset]
        tile_count = rom[offset + 1]
        destination_tile = struct.unpack_from("<H", rom, offset + 2)[0]
        if not frame_count or not tile_count:
            raise UnsupportedMapAssemblyVariant(
                f"animated-tile record at {animation:#010x} has zero extent"
            )
        first_frame = _u32(rom, animation + 4)
        _file_offset(first_frame + 4, len(rom))
        try:
            frame_data = webfoot_lz.unpack_raw_stream(
                rom,
                first_frame - GBA_ROM_BASE + 4,
                tile_count * TILE_BYTES,
                initial_literal_bits=8,
            )
        except webfoot_lz.ContainerError as exc:
            raise UnsupportedMapAssemblyVariant(
                f"animated-tile frame at {first_frame:#010x} did not decode: {exc}"
            ) from exc
        animations.append((destination_tile, tile_count, frame_data, animation))
        animation_addresses.append(animation)

    covered = set(range(len(selected_tiles)))
    for destination, count, _data, _address in animations:
        covered.update(range(destination, destination + count))
    missing = sorted(referenced - covered)
    if missing:
        sample = ", ".join(str(value) for value in missing[:8])
        raise UnsupportedMapAssemblyVariant(
            f"logical layers reference tiles not supplied by selectors or "
            f"animations: {sample}"
        )

    highest = max(covered | referenced)
    if highest > MAX_TILE_INDEX:
        raise UnsupportedMapAssemblyVariant(
            f"tile index {highest} exceeds the regular-BG 10-bit range"
        )
    char_data = bytearray((highest + 1) * TILE_BYTES)
    for destination, tile in enumerate(selected_tiles):
        start = destination * TILE_BYTES
        char_data[start:start + TILE_BYTES] = tile
    for destination, count, data, _address in animations:
        start = destination * TILE_BYTES
        char_data[start:start + count * TILE_BYTES] = data

    return MapAssembly(
        descriptor_address=descriptor_address,
        char_data=bytes(char_data),
        selectors=selectors,
        layers=layers,
        tileset_addresses=tuple(atlas_addresses[key] for key in sorted(atlas_addresses)),
        animation_addresses=tuple(animation_addresses),
    )


def reconstruct_charblock_from_rom(rom: bytes, descriptor_address: int) -> bytes:
    """Return the static-frame character bytes assembled by the descriptor."""
    return reconstruct_map_assembly(rom, descriptor_address).char_data


# --- VRAM-oracle dump loading (for scripts/tests) ----------------------------

def load_vram_dump(
    dump_dir: str | Path,
) -> tuple[bytes, tuple[LayerSpec, ...], tuple[tuple[int, int, int], ...]]:
    """Load a VRAM-oracle dump directory into render inputs.

    Reads ``vram.bin`` + ``dump_manifest.csv`` and returns
    ``(vram, layer_specs, capture_palette_rgb)``. Only the BG layers DISPCNT
    marks enabled are returned. ``capture_palette_rgb`` is decoded from the
    dump's own ``palette.bin`` (BGR555) - it may be dark if the capture was
    mid-fade; prefer the ROM palette (:func:`decode_bg_palette`) for colour.

    Kept out of the pure core so the renderer itself touches no filesystem.
    """
    dump = Path(dump_dir)
    manifest: dict[str, str] = {}
    with (dump / "dump_manifest.csv").open(newline="") as handle:
        for row in csv.reader(handle):
            if len(row) == 2 and row[0] != "field":
                manifest[row[0]] = row[1]

    vram = (dump / "vram.bin").read_bytes()
    capture_palette = sprite_graphics.decode_palette((dump / "palette.bin").read_bytes(), 0).rgb

    dispcnt = int(manifest["dispcnt"], 16)
    layers: list[LayerSpec] = []
    for bg in range(4):
        if not dispcnt & (1 << (8 + bg)):  # DISPCNT BG-enable bit
            continue
        layers.append(
            LayerSpec(
                bg=bg,
                char_base_block=int(manifest[f"bg{bg}_char_base_block"]),
                screen_base_block=int(manifest[f"bg{bg}_screen_base_block"]),
                screen_size_bits=int(manifest[f"bg{bg}_screen_size_bits"]),
                priority=int(manifest[f"bg{bg}_priority"]),
                color_256=manifest[f"bg{bg}_color_mode"] == "8bpp",
            )
        )
    if not layers:
        raise MapRenderError(f"{dump} manifest enables no BG layers")
    return vram, tuple(layers), capture_palette


# --- render core (pure, deterministic) ---------------------------------------

def render_map_from_vram(
    vram: bytes,
    layers_spec: tuple[LayerSpec, ...],
    palette_rgb: tuple[tuple[int, int, int], ...],
    *,
    semantic_map_id: str = "vram",
    provenance: dict[str, object] | None = None,
) -> MapRenderResult:
    """Render composited 8bpp indices from a VRAM capture and layer wiring.

    Pure and deterministic: no filesystem, no ROM, no Qt. ``vram`` supplies the
    charblocks and screenblocks; ``layers_spec`` is the per-BG block wiring;
    ``palette_rgb`` is the 256-colour table. Each enabled BG is rendered via
    ``bg_tilemap.render_layer`` and composed by priority (lower number on top;
    index-0 is transparent). Fails closed on any block/tile that runs past VRAM.
    """
    if not isinstance(vram, (bytes, bytearray)):
        raise MapRenderError("vram must be bytes")
    if not layers_spec:
        raise MapRenderError("no layers to render")
    vram = bytes(vram)

    rendered: list[RenderedLayer] = []
    for layer in layers_spec:
        map_w, map_h = SCREEN_SIZE_TILES[layer.screen_size_bits]
        try:
            pixels, width, height = bg_tilemap.render_layer(
                vram,
                char_base_block=layer.char_base_block,
                screen_base_block=layer.screen_base_block,
                map_width_tiles=map_w,
                map_height_tiles=map_h,
                color_256=layer.color_256,
            )
        except bg_tilemap.BgTilemapError as exc:
            raise MapRenderError(f"BG{layer.bg} did not render: {exc}") from exc
        rendered.append(
            RenderedLayer(
                bg=layer.bg,
                priority=layer.priority,
                char_base_block=layer.char_base_block,
                screen_base_block=layer.screen_base_block,
                width=width,
                height=height,
                pixels=pixels,
            )
        )

    width = rendered[0].width
    height = rendered[0].height
    if any(r.width != width or r.height != height for r in rendered):
        raise MapRenderError("layers differ in size; compositing needs one canvas")

    # Compose by priority: lower number draws on top; a higher (on-top) layer's
    # index-0 pixel is transparent and lets lower layers through. Draw bottom-up.
    composite = bytearray(width * height)
    for layer in sorted(rendered, key=lambda item: (item.priority, item.bg), reverse=True):
        for i, value in enumerate(layer.pixels):
            if value:
                composite[i] = value

    return MapRenderResult(
        semantic_map_id=semantic_map_id,
        width=width,
        height=height,
        layers=tuple(rendered),
        composite=bytes(composite),
        palette=palette_rgb,
        provenance=provenance or {"source": "vram capture"},
        warnings=_VRAM_RENDER_WARNINGS,
    )


def render_map(
    rom: bytes,
    map_id: str,
) -> MapRenderResult:
    """Render the complete static logical map from immutable ROM bytes only."""
    if not isinstance(rom, (bytes, bytearray)):
        raise MapRenderError("rom must be bytes")
    rom = bytes(rom)
    _verify_supported_rom(rom)

    map_index = parse_map_id(map_id)
    map_entry_address, scene_pointer, descriptor = resolve_descriptor(rom, map_index)
    assembly = reconstruct_map_assembly(rom, descriptor)
    palette = decode_bg_palette(rom)

    rendered: list[RenderedLayer] = []
    for layer in assembly.layers:
        try:
            pixels, width, height = bg_tilemap.render_entries(
                assembly.char_data,
                layer.entries,
                map_width_tiles=layer.width_tiles,
                map_height_tiles=layer.height_tiles,
                color_256=True,
            )
        except bg_tilemap.BgTilemapError as exc:
            raise MapRenderError(f"BG{layer.bg} did not render: {exc}") from exc
        rendered.append(
            RenderedLayer(
                bg=layer.bg,
                priority=layer.priority,
                char_base_block=0,
                screen_base_block=-1,
                width=width,
                height=height,
                pixels=pixels,
            )
        )

    width = max(layer.width for layer in rendered)
    height = max(layer.height for layer in rendered)
    composite = bytearray(width * height)
    for layer in sorted(rendered, key=lambda item: (item.priority, item.bg), reverse=True):
        for y in range(layer.height):
            source = y * layer.width
            destination = y * width
            for x, value in enumerate(layer.pixels[source:source + layer.width]):
                if value:
                    composite[destination + x] = value

    provenance = {
        "semantic_map_id": map_id,
        "map_index": map_index,
        "map_entry_address": f"{map_entry_address:#010x}",
        "scene_pointer": f"{scene_pointer:#010x}",
        "descriptor_address": f"{descriptor:#010x}",
        "bg_palette_address": f"{BG_PALETTE_ADDRESS:#010x}",
        "palette_source": f"ROM {BG_PALETTE_ADDRESS:#010x} (full brightness)",
        "tile_selector_address": f"{_u32(rom, descriptor + 0x48):#010x}",
        "tileset_addresses": [f"{address:#010x}" for address in assembly.tileset_addresses],
        "animation_addresses": [f"{address:#010x}" for address in assembly.animation_addresses],
        "layers": [
            {
                "bg": layer.bg,
                "record_address": f"{layer.record_address:#010x}",
                "priority": layer.priority,
                "width_tiles": layer.width_tiles,
                "height_tiles": layer.height_tiles,
                "chunk_addresses": [f"{address:#010x}" for address in layer.chunk_addresses],
            }
            for layer in assembly.layers
        ],
    }

    return MapRenderResult(
        semantic_map_id=map_id,
        width=width,
        height=height,
        layers=tuple(rendered),
        composite=bytes(composite),
        palette=palette,
        provenance=provenance,
        warnings=_ROM_RENDER_WARNINGS,
    )


def render_map_vram_reference(
    rom: bytes,
    map_id: str,
    vram: bytes,
    *,
    layers_spec: tuple[LayerSpec, ...],
    capture_palette_rgb: tuple[tuple[int, int, int], ...] | None = None,
    use_capture_palette: bool = False,
) -> MapRenderResult:
    """Render the historical 32x32 VRAM oracle for regression comparison."""
    if not isinstance(rom, (bytes, bytearray)):
        raise MapRenderError("rom must be bytes")
    if not isinstance(vram, (bytes, bytearray)):
        raise MapRenderError("vram must be bytes")
    if not layers_spec:
        raise MapRenderError("VRAM reference needs a layers_spec")
    rom = bytes(rom)
    map_index = parse_map_id(map_id)
    map_entry_address, scene_pointer, descriptor = resolve_descriptor(rom, map_index)
    if use_capture_palette:
        if capture_palette_rgb is None:
            raise MapRenderError("use_capture_palette set but no capture_palette_rgb given")
        palette = capture_palette_rgb
        palette_source = "VRAM capture palette.bin"
    else:
        palette = decode_bg_palette(rom)
        palette_source = f"ROM {BG_PALETTE_ADDRESS:#010x} (full brightness)"
    return render_map_from_vram(
        bytes(vram),
        layers_spec,
        palette,
        semantic_map_id=map_id,
        provenance={
            "semantic_map_id": map_id,
            "map_index": map_index,
            "map_entry_address": f"{map_entry_address:#010x}",
            "scene_pointer": f"{scene_pointer:#010x}",
            "descriptor_address": f"{descriptor:#010x}",
            "palette_source": palette_source,
            "tile_source": "VRAM reference capture",
        },
    )


def load_canonical_rom(path: str | Path, catalog: RomProfileCatalog) -> bytes:
    """Read and identity-check the canonical ROM, returning its bytes.

    A convenience for scripts and ROM-gated tests: it refuses any image whose
    SHA-256 is not the canonical one, because every address in this module is
    specific to that image.
    """
    identification = identify_rom(path, catalog)
    if identification.hashes.sha256.lower() != SUPPORTED_ROM_SHA256:
        raise MapRenderError(
            f"{path} is not the canonical Buu's Fury image this renderer supports"
        )
    return Path(path).read_bytes()
