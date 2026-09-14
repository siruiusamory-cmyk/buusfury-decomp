"""Read-only map renderer: ``render_map(rom, "map:0040", vram)`` -> pixels.

MAP-VIS-001, finalized. The domain layer that turns a semantic map id into a
rendered background image. It is honest about where each byte comes from:

- **Identity, provenance, and palette are ROM-proven.** ``map:NNNN`` resolves to
  ``MapEntry[N] @ 0x0808E2E0 + N*0x38``, then ``+0x2C`` dereferences to a scene
  descriptor - pure ROM arithmetic, general for every map. The 256-colour global
  BG palette is read from ROM ``0x080701B0`` (RGB888, requantised to the
  hardware's 5 bits), a constant for every map and the correct full-brightness
  colours even when a capture was taken mid-fade.

- **Tile graphics and tilemaps come from a VRAM capture, NOT from ROM.** The one
  link that is *not* solved is reconstructing the exact VRAM charblock from the
  ROM tileset containers: the engine places tiles at a finer granularity than any
  clean container overlay, so a ROM-only charblock renders as garbage (verified:
  only ~40-65% of a container's 256 tiles land where a tile-start overlay would
  put them). That reconstruction is the documented open MAP-VIS-001 sub-problem
  (Outcome B). Until it is solved, the renderer takes the charblock and the four
  screenblocks from a per-map VRAM capture (``vram.bin`` + ``dump_manifest.csv``
  under ``build/toolkit031/mapvis001-*``) and hands them to the proven
  ``bg_tilemap.render_layer``, composing by BG priority.

So this is a VRAM-oracle renderer with ROM-resolved identity, provenance, and
palette - not a ROM-only renderer. :func:`reconstruct_charblock_from_rom` exists
only to fail closed with that explanation; there is no code path that silently
produces the garbage render.

**Full brightness, static frame.** The runtime fade/brightness registers are not
applied and animated tiles are captured at whatever frame the dump caught
(rendered as-is); both are recorded in the result's warnings.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
import struct

from .formats import bg_tilemap
from .formats import map_entry as me
from .formats import sprite_graphics
from .profile import RomProfileCatalog
from .rom import identify_rom


class MapRenderError(ValueError):
    """Raised when a map cannot be resolved or rendered.

    One class: every caller either gets a render or is told, in the message, the
    exact link that failed.
    """


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


#: The honest warnings every VRAM-oracle render carries.
_RENDER_WARNINGS = (
    "tile graphics and tilemaps sourced from a VRAM capture; exact "
    "ROM->charblock reconstruction is an open MAP-VIS-001 sub-problem",
    "BG palette from ROM 0x080701B0 at full brightness; runtime fade not applied",
    "animated tiles at static frame 0",
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


# --- QUARANTINED: ROM-container charblock reconstruction (Outcome B) ----------
#
# The one unsolved MAP-VIS-001 link. The engine loads tileset containers to
# per-tile destinations finer than any clean container overlay: only ~40-65% of
# a container's 256 tiles land where a tile-start overlay would place them
# (measured idx2 0x08096DA0 = 103/256, idx1 0x080959B4 = 67/256, idx0
# 0x080945C0 = 0/256). Both the old concatenation and the tile-start overlay
# produced visual garbage. Until the exact per-tile placement is recovered, the
# renderer takes the charblock (and screenblocks) from a VRAM capture instead.
#
# This function is kept ONLY so the failure is explicit and documented at the
# call site. It has no working body and never returns bytes.

def reconstruct_charblock_from_rom(rom: bytes, *args: object, **kwargs: object) -> bytes:
    """UNSOLVED. Raises: reconstructing VRAM tiles from ROM containers is open.

    See the module docstring and the block comment above. Supply a VRAM capture
    (``vram.bin`` + ``dump_manifest.csv``) to :func:`render_map` instead of
    attempting a ROM-only render.
    """
    raise MapRenderError(
        "ROM charblock reconstruction is an unsolved MAP-VIS-001 sub-problem "
        "(Outcome B): the engine's per-tile placement is finer than any container "
        "overlay, so a ROM-only charblock renders as garbage. Supply a VRAM "
        "capture instead - see render_map(rom, map_id, vram)."
    )


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
    for layer in sorted(rendered, key=lambda item: item.priority, reverse=True):
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
        warnings=_RENDER_WARNINGS,
    )


def render_map(
    rom: bytes,
    map_id: str,
    vram: bytes,
    *,
    layers_spec: tuple[LayerSpec, ...] | None = None,
    capture_palette_rgb: tuple[tuple[int, int, int], ...] | None = None,
    use_capture_palette: bool = False,
) -> MapRenderResult:
    """Render ``map_id`` from a VRAM capture, with ROM-resolved identity + palette.

    ``rom`` is the canonical Buu's Fury image (read-only); ``map_id`` is a
    semantic ``"map:NNNN"`` identity; ``vram`` is a per-map VRAM capture supplying
    the tile graphics and tilemaps (the open ROM->charblock link, see the module
    docstring). The map is resolved by its MapEntry index alone - no
    caller-supplied offsets - and provenance records the ROM offsets. The BG
    palette is read from ROM 0x080701B0 at full brightness by default (so a
    mid-fade capture still renders at correct colour); pass
    ``use_capture_palette=True`` with ``capture_palette_rgb`` to use the dump's
    own palette instead.

    ``layers_spec`` is the per-BG block wiring, normally from
    :func:`load_vram_dump`; it is required (there is no ROM-side derivation of it
    that is proven).
    """
    if not isinstance(rom, (bytes, bytearray)):
        raise MapRenderError("rom must be bytes")
    if not isinstance(vram, (bytes, bytearray)):
        raise MapRenderError("vram must be bytes")
    if not layers_spec:
        raise MapRenderError(
            "render_map needs a layers_spec (from load_vram_dump); the ROM-side "
            "BG wiring derivation is not proven"
        )
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

    provenance = {
        "semantic_map_id": map_id,
        "map_index": map_index,
        "map_entry_address": f"{map_entry_address:#010x}",
        "scene_pointer": f"{scene_pointer:#010x}",
        "descriptor_address": f"{descriptor:#010x}",
        "bg_palette_address": f"{BG_PALETTE_ADDRESS:#010x}",
        "palette_source": palette_source,
        "tile_source": "VRAM capture (ROM->charblock reconstruction unsolved, Outcome B)",
        "layer_wiring": [
            {
                "bg": layer.bg,
                "char_base_block": layer.char_base_block,
                "screen_base_block": layer.screen_base_block,
                "priority": layer.priority,
            }
            for layer in layers_spec
        ],
    }

    return render_map_from_vram(
        vram,
        layers_spec,
        palette,
        semantic_map_id=map_id,
        provenance=provenance,
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
