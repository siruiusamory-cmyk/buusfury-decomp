"""Read-only animation / frame / multipart-piece census for LOGX-FRAME-001.

The probe answers, deterministically and without writing to the image:

* what the 1,721 non-null animation references of the accepted sprite-definition
  census resolve to, and how those references share animation objects;
* the physical layout of an *animation object*: its leading count word, the
  4-byte-stride table of frame-cell pointers that follows it, and the two words
  after that table;
* the engine instructions that read each of those fields, and the exact
  ``16*frame + 4*direction + 4`` arithmetic LOGX-SPRITE-001 handed forward;
* the *frame record* a cell points at: its 8-byte header (the piece count and the
  frame's own bounding box) and its **12-byte** piece records, including the
  packed OBJ attribute pair and the graphics-container pointer each piece carries;
* the full census of every population the ticket must keep apart.

Names are positional except where an engine consumer justifies one.  The three
structural levels keep the accepted ROM-bible names - *definition*,
*animation*, *frame* - so this probe and ``docs/research/GRAPHICS_FORMAT.md``
cannot drift.  Inside a level, unresolved fields stay neutral
(``trailer_0_raw``, ``trailer_1_raw``).  The names this probe does promote are
each backed by a named instruction site, listed in :data:`EVIDENCE_INSTRUCTIONS`
and re-read by the ROM-gated suite:

* ``animation + 0x00`` is a 32-bit **frame count** - the engine compares it with
  the frame index it feeds to the cell arithmetic, and advances the animation
  modulo it (``0x0800DE78..0x0800DE90``, ``0x0800DEBA..0x0800DECC``);
* ``animation + 0x04`` begins a **4-byte-stride table of frame cells** addressed
  as ``base + 4 + 16*frame + 4*direction`` (``0x0800EF38``, ``0x0800EF68``,
  ``0x0800FFA4``, ``0x080100A4``, ``0x08010192``, ``0x080272AE``,
  ``0x080273D6``, ``0x0800F0A2``);
* a **frame record** is an **8-byte header** - ``u32 piece_count`` then ``s8
  min_x``, ``s8 min_y``, ``u8 width``, ``u8 height`` over the frame's pieces -
  followed by that many **12-byte** piece records.  The render loop computes
  ``frame + 8 + 12*index`` (``0x0800F3C0..0x0800F3CA``) and the header's four
  bytes reproduce the pieces' bounding box on all 10,980 canonical frames;
* inside a piece record the engine reads ``+0x00`` and ``+0x01`` as signed
  offsets, ``+0x02`` and ``+0x03`` as pixel extents, ``+0x04`` as a **packed OBJ
  attribute pair**, and ``+0x08`` as the graphics-container word
  (``0x0800F204``, ``0x0800F206``, ``0x0800F22A``, ``0x0800F22E``,
  ``0x0800F1C2``, ``0x0800F24C``, ``0x0800F3CE``).  The attribute decode's shape
  and size reproduce the stored extents on all 11,005 pieces.

Everything else - the animation's two trailing words, the meaning of the four
positions - is recorded raw and labelled ``UNRESOLVED`` or ``INFERRED`` in
``docs/research/LOGX_FRAME_PROVENANCE.md``; none of it is promoted here.

Evidence provenance labels follow ``docs/research-conventions.md``.  Addresses
are GBA addresses; a file offset is an address minus ``0x08000000``.

**Graphics-container pointer format.**  On the canonical image a piece's
``+0x08`` word is always the full GBA-address form (11,005 of 11,005); the bare
file-offset form is accepted because the same reader must serve a
differently-authored image.  Both name the same region,
``0x003C34D0..0x006A87A8``, which is the region ``GRAPHICS_FORMAT.md`` §9
records for the packed containers.  :func:`to_file_offset` resolves both and
rejects anything else.

**Dependency boundary.**  The census and the record arithmetic are pure: they
need only the standard library.  Capstone is needed *only* to read instruction
text, so that import is deferred to first use (``tools.research.thumb_disasm``
raises ``SystemExit`` when capstone is absent, and CI's portable unit job
installs only ``.[dev]``).  An environment without capstone can still import
this module, run the whole census API and use the ``--rows`` report; only
``--engine``, :func:`instruction_at` and :func:`format_instruction` require it.

The probe performs no I/O beyond reading the caller's bytes, writes no image or
graphics payload to disk, and never mutates the canonical image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Sequence

from tools.research import logx_sprite_probe as sprite
from tools.webfoot.formats import webfoot_lz

CANONICAL_SHA256 = "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"
ROM_SIZE = 8 * 1024 * 1024
ROM_BASE = 0x08000000

# --- the animation object ----------------------------------------------------

#: ``u32`` frame count.  The engine compares this with the frame index it feeds
#: to the cell arithmetic and advances the animation modulo it; it is read as a
#: whole word, never as a byte.
ANIMATION_FRAME_COUNT = 0x00

#: First cell of the frame/direction table.  Cell ``(frame, direction)`` lives at
#: ``address + 4 + 16*frame + 4*direction``, i.e. the table is a 4-byte-stride
#: array whose row stride is 16 bytes.
ANIMATION_TABLE = 0x04
ANIMATION_ROW_STRIDE = 16
ANIMATION_DIRECTIONS = 4

#: Bytes the two words after the ``4 * frame_count`` cell pointers occupy.  They
#: are recorded raw (``Animation.trailer_0_raw`` / ``trailer_1_raw``);
#: LOGX-SPRITE-001 left them unresolved and this ticket does not promote them.
ANIMATION_TRAILER_BYTES = 8


def table_bytes(frame_count: int) -> int:
    """Bytes one animation object's cell table occupies."""
    return ANIMATION_ROW_STRIDE * frame_count


#: Largest frame count the canonical corpus uses, and the largest the engine's
#: own state arithmetic can address (``obj+0x11`` doubled by ``lsls #4``).
FRAME_COUNT_MIN = 1
FRAME_COUNT_MAX = 16

# --- the frame record --------------------------------------------------------

#: ``u32`` piece count.
FRAME_PIECE_COUNT = 0x00

#: The frame record's header is 8 bytes: ``u32 piece_count`` then the frame's
#: own bounding box, ``s8 min_x``, ``s8 min_y``, ``u8 width``, ``u8 height``
#: over its pieces.  Two independent measurements fix the width:
#:
#: * the render loop at ``0x0800F3C0`` computes ``frame + 8 + 12*index`` from the
#:   record pointer, so the first piece starts 8 bytes in;
#: * under ``8 + 12*count`` the piece geometry is self-consistent on *every*
#:   piece of the canonical corpus: each piece's two dimension bytes multiply to
#:   the decoded size of the container its pointer names (11,005 of 11,005), and
#:   no record's counted extent crosses the next known frame start.
#:
#: The bounding box is not an interpretation: on all 10,980 canonical frames the
#: header's two signed bytes equal the minimum ``x`` and ``y`` over that frame's
#: pieces and its two unsigned bytes equal the width and height of their union.
FRAME_HEADER_SIZE = 0x08

#: One piece record: ``x``, ``y``, two dimension bytes, a packed OBJ attribute
#: pair, and the graphics-container word.
PIECE_RECORD_SIZE = 0x0C

#: Fields inside a frame record's 8-byte header.
FRAME_HEADER_MIN_X = 0x04   # s8, the minimum piece x
FRAME_HEADER_MIN_Y = 0x05   # s8, the minimum piece y
FRAME_HEADER_WIDTH = 0x06   # u8, the width of the pieces' union
FRAME_HEADER_HEIGHT = 0x07  # u8, the height of the pieces' union

#: Fields inside a piece record, relative to the piece's own start.  Every
#: offset below is an engine read site:
#:
#: * ``+0x00`` s8 ``x`` - ``ldrsb`` at ``0x0800F204`` (``r0`` is the piece the
#:   render loop addresses), ``0x0800FE3C``, ``0x080101E0``;
#: * ``+0x01`` s8 ``y`` - ``ldrb``/``ldrsb`` at ``0x0800F22A``, ``0x0800F25E``;
#: * ``+0x02`` u8 ``dim_0`` - ``ldrb`` at ``0x0800F206``; the engine halves it to
#:   centre an OBJ horizontally (``0x0800F20A lsrs``) and multiplies the pair to
#:   size the composite buffer (``0x0800F3DE muls``);
#: * ``+0x03`` u8 ``dim_1`` - ``ldrb`` at ``0x0800F22E``, ``0x080101FE``-region;
#: * ``+0x04`` u32 packed OBJ attribute pair ``(attr1 << 16) | attr0``, loaded at
#:   ``0x0800F1C2`` and ``0x0800F24C`` and merged into the outgoing OAM word
#:   under the mask literal ``0xFE00FFFF`` (pool ``0x0800F4B0``); decoded shape
#:   and size reproduce ``dim_0``/``dim_1`` on every canonical piece;
#: * ``+0x08`` u32 graphics-container word - the render loop's ``ldr r0,[r7,#8]``
#:   at ``0x0800F3CE``, where ``r7 = frame + 8 + 12*index``.  It is the only word
#:   in a piece that resolves to a container whose declared decoded length equals
#:   ``dim_0 * dim_1``.
PIECE_X = 0x00          # s8
PIECE_Y = 0x01          # s8
PIECE_DIM_0 = 0x02      # u8
PIECE_DIM_1 = 0x03      # u8
PIECE_ATTRIBUTES = 0x04  # u32 packed OBJ attribute pair
PIECE_GRAPHICS = 0x08    # u32 container pointer

#: The GBA OAM shape/size bit positions `GRAPHICS_FORMAT.md` §2 records.  No
#: canonical piece stores an attribute word, so these are **not** used by any
#: property here; they are kept only so the provenance document can name the bits
#: it reports as unconfirmed.
ATTRIBUTE_SHAPE_SHIFT = 14
ATTRIBUTE_SIZE_SHIFT = 14
ATTRIBUTE_H_FLIP = 0x1000        # attribute 1 bit 12
ATTRIBUTE_V_FLIP = 0x2000        # attribute 1 bit 13
ATTRIBUTE_COLOUR_256 = 0x2000    # attribute 0 bit 13

#: GBA OBJ shape/size -> pixel dimensions.  Shape is attribute-0 bits 14-15, size
#: is attribute-1 bits 14-15; shape 3 is reserved on this hardware and no
#: canonical piece takes it.  The table is the one GBATEK publishes and the one
#: ``tools/webfoot/formats/sprite_graphics.py`` already carries; it is duplicated
#: here so the research probe decodes independently of the reader under test.
OBJECT_DIMENSIONS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((8, 8), (16, 16), (32, 32), (64, 64)),
    ((16, 8), (32, 8), (32, 16), (64, 32)),
    ((8, 16), (8, 32), (16, 32), (32, 64)),
)

# --- ranges measured on the canonical image ----------------------------------

#: The region the packed graphics containers occupy, as file offsets.  Measured
#: in :func:`graphics_pointer_census`; not an engine declaration.  The lower bound
#: agrees with the value `GRAPHICS_FORMAT.md` §9 records, so the bounds are a
#: cross-check on the piece field rather than new information.
GRAPHICS_REGION_MIN = 0x003C34D0
GRAPHICS_REGION_MAX = 0x006A87A8

# --- engine instructions -----------------------------------------------------

#: ``name -> (address, expected text)``.  Reading them back needs capstone.
EVIDENCE_INSTRUCTIONS: dict[str, tuple[int, str]] = {
    # the frame/direction cell arithmetic, one entry per consuming function
    "cell_row_method": (0x0800EF38, "ldrb r2, [r0, #0x11]"),
    "cell_row_base": (0x0800EF3A, "ldr r1, [r0, #0x50]"),
    "cell_row_scale": (0x0800EF3C, "lsls r2, r2, #4"),
    "cell_row_add": (0x0800EF3E, "adds r1, r1, r2"),
    "cell_column_load": (0x0800EF40, "ldrb r2, [r0, #0x10]"),
    "cell_column_scale": (0x0800EF42, "lsls r2, r2, #2"),
    "cell_column_add": (0x0800EF44, "adds r1, r1, r2"),
    "cell_load": (0x0800EF46, "ldr r1, [r1, #4]"),
    "cell_store": (0x0800EF48, "str r1, [r0, #0x54]"),
    "cell_screen_row": (0x0800EF6E, "lsls r3, r3, #4"),
    "cell_screen_column": (0x0800EF76, "lsls r3, r3, #2"),
    "cell_render_row": (0x0800F0A6, "lsls r1, r1, #3"),
    "cell_render_column": (0x0800F0AC, "lsls r1, r1, #1"),
    "cell_render_base": (0x0800F0A4, "ldr r0, [r4, #0x4c]"),
    "cell_method2_row": (0x0800FFAA, "lsls r3, r3, #4"),
    "cell_method2_column": (0x0800FFB0, "lsls r3, r3, #2"),
    "constructor_row": (0x080273DC, "lsls r3, r3, #4"),
    "constructor_column": (0x080273DA, "lsls r1, r1, #2"),
    "constructor_cell": (0x080273E2, "ldr r1, [r1, #4]"),
    # the frame count as an advancing bound
    "advance_counter": (0x0800DE6E, "ldrh r2, [r1, #0x12]"),
    "advance_shift": (0x0800DE78, "ldrb r3, [r0, #4]"),
    "advance_count": (0x0800DE7E, "ldr r3, [r3]"),
    "advance_compare": (0x0800DE80, "cmp r3, r2"),
    "advance_branch": (0x0800DE82, "bgt #0x800de90"),
    "advance_store": (0x0800DE90, "strb r2, [r1, #0x11]"),
    "advance2_count": (0x0800DEC0, "ldr r0, [r0]"),
    "advance2_compare": (0x0800DEC2, "cmp r0, r2"),
    "advance2_reset": (0x0800DEC6, "movs r0, #0"),
    # the frame record and its pieces
    "frame_selected": (0x0800F188, "ldr r0, [r4, #0x54]"),
    "frame_piece_count": (0x0800F18A, "ldr r0, [r0]"),
    "frame_bbox_min_x": (0x0800F38E, "ldrb r2, [r0, #6]"),
    "frame_bbox_min_y": (0x0800F390, "ldrb r1, [r0, #7]"),
    "frame_bbox_area": (0x0800F392, "muls r2, r1, r2"),
    "piece_x_byte": (0x0800F204, "ldrsb r7, [r0, r3]"),
    "piece_dim_0_byte": (0x0800F206, "ldrb r3, [r0, #2]"),
    "piece_dim_0_halved": (0x0800F20A, "lsrs r3, r3, #1"),
    "piece_y_byte": (0x0800F22A, "ldrb r3, [r0, #1]"),
    "piece_dim_1_byte": (0x0800F22E, "ldrb r3, [r0, #3]"),
    # a piece's packed OBJ attribute pair, loaded and merged into the OAM word
    "piece_attribute_word": (0x0800F1C2, "ldr r3, [r0, #4]"),
    "piece_attribute_word2": (0x0800F24C, "ldr r6, [r0, #4]"),
    "piece_attribute_mask": (0x0800F216, "ldr r3, [pc, #0x298]"),
    "piece_count_check": (0x0800F39C, "ldr r1, [r0]"),
    "piece_count_single": (0x0800F39E, "cmp r1, #1"),
    "piece_container_kind": (0x0800F3A4, "ldr r2, [r1]"),
    "piece_container_kind_test": (0x0800F3A6, "cmp r2, #0"),
    "piece_loop_index": (0x0800F3C0, "lsls r1, r5, #1"),
    "piece_loop_base": (0x0800F3C8, "adds r7, r0, r1"),
    "piece_loop_stride": (0x0800F3CA, "adds r7, #8"),
    "piece_loop_attributes": (0x0800F3CC, "ldr r2, [r4, #0x34]"),
    "piece_loop_graphics": (0x0800F3CE, "ldr r0, [r7, #8]"),
    "piece_loop_dims": (0x0800F3D8, "ldrb r7, [r7, #2]"),
    "piece_loop_area": (0x0800F3DE, "muls r7, r0, r7"),
    # the character constructor reads the FRAME HEADER, not a piece
    "ctor_frame_min_x": (0x080273F0, "ldrsb r7, [r1, r3]"),
    "ctor_frame_min_y": (0x080273F4, "ldrsb r1, [r1, r3]"),
    "ctor_frame_bbox_w": (0x0802740C, "ldrb r2, [r3, #6]"),
    "ctor_frame_bbox_h": (0x08027410, "ldrb r3, [r3, #7]"),
    # the direction index is produced as one of exactly four compile-time values
    "facing_dx_branch": (0x0800A8BE, "cmp r2, #0"),
    "facing_right": (0x0800A8C2, "movs r2, #3"),
    "facing_left": (0x0800A8C8, "movs r2, #2"),
    "facing_dy_branch": (0x0800A8CE, "cmp r3, #0"),
    "facing_down": (0x0800A8D2, "movs r2, #0"),
    "facing_up": (0x0800A8D8, "movs r2, #1"),
    "facing_store": (0x0800A8C4, "strb r2, [r1, #0x10]"),
    "facing2_dy_branch": (0x080159E2, "cmp r2, #0"),
    "facing2_down": (0x080159E6, "movs r1, #0"),
    "facing2_up": (0x080159EC, "movs r1, #1"),
    "facing2_store": (0x080159D6, "strb r1, [r0, #0x10]"),
}


class FrameProbeError(RuntimeError):
    """Raised when the image or the requested report cannot be produced."""


# --- byte helpers ------------------------------------------------------------


def _u16(data: bytes, address: int) -> int:
    return struct.unpack_from("<H", data, address - ROM_BASE)[0]


def _u32(data: bytes, address: int) -> int:
    return struct.unpack_from("<I", data, address - ROM_BASE)[0]


def _u8(data: bytes, address: int) -> int:
    return data[address - ROM_BASE]


def _s8(value: int) -> int:
    return value - 0x100 if value & 0x80 else value


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def verify_canonical(data: bytes) -> None:
    """Fail closed unless ``data`` is the canonical Buu's Fury image."""
    if len(data) != ROM_SIZE:
        raise FrameProbeError(f"image is {len(data)} bytes, expected {ROM_SIZE}")
    actual = sha256_of(data)
    if actual != CANONICAL_SHA256:
        raise FrameProbeError(
            f"refusing non-canonical image: expected {CANONICAL_SHA256}, got {actual}"
        )


def load_rom(path: Path) -> bytes:
    data = Path(path).read_bytes()
    verify_canonical(data)
    return data


def in_rom(data: bytes, address: int) -> bool:
    """True when ``address`` is a word-aligned GBA address inside the image."""
    if address % 4:
        return False
    offset = address - ROM_BASE
    return 0 <= offset and offset + 4 <= len(data)


def to_file_offset(value: int) -> int | None:
    """Resolve a piece's graphics word in either of the two stored forms.

    On the canonical image **every** piece stores the full GBA address form
    (11,005 of 11,005); the bare file-offset form is accepted because the same
    reader has to serve a differently-authored image.  Anything outside both is
    rejected.

    Resolution is deliberately *not* gated on :data:`GRAPHICS_REGION_MIN`: a
    region test alone would classify a word by fiat.  The strong test is
    :func:`resolves_to_graphics`, which decodes the container and requires its
    declared size to equal the piece's own declared dimensions.
    """
    if ROM_BASE <= value < ROM_BASE + ROM_SIZE:
        return value - ROM_BASE
    if 0 <= value < ROM_SIZE:
        return value
    return None


def resolves_to_graphics(data: bytes, piece: "Piece") -> int | None:
    """The container offset ``piece`` names, or ``None`` when it does not.

    Three conditions must hold together, and the corpus supports all three on
    every piece:

    1. the word must resolve in one of the two stored forms
       (:func:`to_file_offset`);
    2. the resolved offset must land inside the region the containers occupy
       (:func:`is_graphics_target`), which rejects a word that resolves as a GBA
       address but points into the code area;
    3. the container must decode, and its declared decoded length must equal the
       piece's ``dim_0 * dim_1``.

    Across the canonical corpus 11,005 of 11,005 pieces pass all three.  The
    joint test is what makes the reading of ``+0x08`` as the graphics word
    evidence rather than a guess: no other word **inside the record** satisfies it
    (piece ``+0x00``, ``+0x04``, ``+0x0C`` and ``+0x10`` pass on zero pieces), and
    the *old* 16-byte layout's ``+0x0C`` reached only 10,980 of 11,005.  The test
    is not unique across the whole record's neighbourhood: on 7 of the 21
    multi-piece frames the frame header's own ``+0x04`` word coincidentally
    decodes to a container of the right size.  That is why the graphics word is
    fixed by the engine's own ``ldr r0,[r7,#8]`` at ``0x0800F3CE`` and by the
    11,005-piece agreement, not by the joint test alone.
    """
    offset = piece.graphics_offset
    if offset is None or not is_graphics_target(offset):
        return None
    size = container_size(data, offset)
    if size is None or size != piece.dim_0 * piece.dim_1:
        return None
    return offset


def is_graphics_target(offset: int) -> bool:
    """Whether an offset lands in the region the canonical containers occupy.

    The region is measured in :func:`graphics_pointer_census`; it is not an
    engine declaration, and a different image is expected to move it.
    """
    return GRAPHICS_REGION_MIN <= offset <= GRAPHICS_REGION_MAX


def container_size(data: bytes, offset: int) -> int | None:
    """The decoded length the container at ``offset`` declares, or ``None``.

    Memoised per image object, so the same container is not decompressed once per
    referencing piece.  The key is the object identity *together with* the object
    itself, which keeps the object alive and therefore prevents a collected
    object's address from being reused.  The table is bounded by
    :data:`_SIZE_CACHE_IMAGES`; past that the whole mapping is dropped.
    """
    sizes = _size_table(data)
    if offset in sizes:
        return sizes[offset]
    try:
        size: int | None = webfoot_lz.unpack(data, offset).declared_size
    except Exception:  # noqa: BLE001 - a malformed pointer is a finding, not a crash
        size = None
    sizes[offset] = size
    return size


def _size_table(data: bytes) -> dict[int, int | None]:
    """The per-image container-size table for ``data``, created on first use."""
    entry = _SIZE_CACHE.get(id(data))
    if entry is not None and entry[1] is data:
        return entry[0]
    if len(_SIZE_CACHE) >= _SIZE_CACHE_IMAGES:
        _SIZE_CACHE.clear()
    table: dict[int, int | None] = {}
    _SIZE_CACHE[id(data)] = (table, data)
    return table


#: ``{id(image): (sizes, image)}``.  The image is held alongside its table so its
#: address cannot be reused while the table is live.
_SIZE_CACHE: dict[int, tuple[dict[int, int | None], bytes]] = {}

#: How many distinct images the container-size table may hold before it is reset.
_SIZE_CACHE_IMAGES = 8


# --- record reading ----------------------------------------------------------


def _image_key(data: bytes) -> str:
    """A cheap content key for one image.

    The census caches below are keyed on content rather than object identity: a
    caller that re-reads the same image into a fresh ``bytes`` object - the
    ROM-gated suite reads it once per test - would otherwise miss the cache every
    time and pay for a full pass over the containers on each call.  The digest is
    only a cache key; the canonical gate in :func:`verify_canonical` is what
    establishes identity.
    """
    return hashlib.sha256(data).hexdigest()


@lru_cache(maxsize=8)
def _memoised_census(name: str, key: str, data: bytes) -> dict[str, Any]:
    """Run the named census once per (census, image content)."""
    registry: dict[str, Callable[[bytes], dict[str, Any]]] = _CENSUS_REGISTRY
    return registry[name](data)


#: The census functions register themselves here, so the memo wrapper never calls
#: itself recursively.
_CENSUS_REGISTRY: dict[str, Callable[[bytes], dict[str, Any]]] = {}


def _memoise(function: Callable[[bytes], dict[str, Any]]) -> Callable[[bytes], dict[str, Any]]:
    """Cache a census by image *content*.

    The reports are pure functions of their bytes and the suite asks for them
    repeatedly, so caching keeps a full-corpus run to one pass over the
    containers.  ``maxsize=8`` on the underlying cache bounds it, so a caller
    streaming different images cannot make it grow without bound.
    """
    _CENSUS_REGISTRY[function.__name__] = function

    @wraps(function)
    def wrapper(data: bytes) -> dict[str, Any]:
        return _memoised_census(function.__name__, _image_key(data), data)

    return wrapper


# --- animation objects -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Animation:
    """One animation object: a frame count, a cell table, and two raw words.

    ``cells`` holds ``4 * frame_count`` words in file order, so cell
    ``(frame, direction)`` is ``cells[4*frame + direction]`` - exactly what the
    engine's ``base + 4 + 16*frame + 4*direction`` reaches.
    """

    address: int
    frame_count: int
    cells: tuple[int, ...]
    trailer_0_raw: int
    trailer_1_raw: int

    @property
    def table_address(self) -> int:
        return self.address + ANIMATION_TABLE

    @property
    def table_end_address(self) -> int:
        return self.table_address + 4 * len(self.cells)

    @property
    def end_address(self) -> int:
        return self.table_end_address + ANIMATION_TRAILER_BYTES

    def cell_address(self, frame: int, direction: int) -> int:
        """The address ``base + 4 + 16*frame + 4*direction`` names."""
        if not 0 <= frame < self.frame_count:
            raise FrameProbeError(f"frame {frame} outside 0..{self.frame_count - 1}")
        if not 0 <= direction < ANIMATION_DIRECTIONS:
            raise FrameProbeError(
                f"direction {direction} outside 0..{ANIMATION_DIRECTIONS - 1}"
            )
        return self.table_address + ANIMATION_ROW_STRIDE * frame + 4 * direction

    def cell(self, frame: int, direction: int) -> int:
        return self.cells[ANIMATION_DIRECTIONS * frame + direction]

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    @property
    def non_null_cells(self) -> int:
        return sum(1 for value in self.cells if value)


def read_animation(data: bytes, address: int) -> Animation:
    """Read the animation object at ``address`` at the engine's own widths."""
    return _read_animation_cached(data, address)


@lru_cache(maxsize=512)
def _read_animation_cached(data: bytes, address: int) -> Animation:
    if not in_rom(data, address):
        raise FrameProbeError(f"animation address {address:#010x} is not in ROM")
    frame_count = _u32(data, address + ANIMATION_FRAME_COUNT)
    if not FRAME_COUNT_MIN <= frame_count <= FRAME_COUNT_MAX:
        raise FrameProbeError(
            f"animation at {address:#010x} has an out-of-range frame count {frame_count}"
        )
    high = _u16(data, address + 2)
    if high:
        raise FrameProbeError(
            f"animation at {address:#010x} has a nonzero second halfword {high:#06x}"
        )
    cells = tuple(
        _u32(data, address + ANIMATION_TABLE + 4 * i)
        for i in range(ANIMATION_DIRECTIONS * frame_count)
    )
    table_end = address + ANIMATION_TABLE + 4 * len(cells)
    return Animation(
        address=address,
        frame_count=frame_count,
        cells=cells,
        trailer_0_raw=_u32(data, table_end),
        trailer_1_raw=_u32(data, table_end + 4),
    )


# --- frame records and pieces ------------------------------------------------


@dataclass(frozen=True, slots=True)
class Piece:
    """One 12-byte piece record, read only at offsets the engine is seen to use.

    The record carries a **packed OBJ attribute pair** at ``+0x04`` in the layout
    ``GRAPHICS_FORMAT.md`` §2 describes - attribute 0 in the low half, attribute 1
    in the high half - and the engine loads it and merges it into the outgoing OAM
    word.  What that document places at ``+0x08`` is this record's
    graphics-container word.  The derived ``shape``/``size`` properties reproduce
    the stored ``dim_0``/``dim_1`` on every canonical piece, which is the check
    that makes the decode evidence rather than a guess.
    """

    address: int
    x: int
    y: int
    dim_0: int
    dim_1: int
    attributes_raw: int
    graphics_raw: int

    @property
    def graphics_offset(self) -> int | None:
        return to_file_offset(self.graphics_raw)

    @property
    def attribute_0(self) -> int:
        return self.attributes_raw & 0xFFFF

    @property
    def attribute_1(self) -> int:
        return (self.attributes_raw >> 16) & 0xFFFF

    @property
    def shape(self) -> int:
        return (self.attribute_0 >> ATTRIBUTE_SHAPE_SHIFT) & 3

    @property
    def size(self) -> int:
        return (self.attribute_1 >> ATTRIBUTE_SIZE_SHIFT) & 3

    @property
    def colour_256(self) -> bool:
        return bool(self.attribute_0 & ATTRIBUTE_COLOUR_256)

    @property
    def horizontal_flip(self) -> bool:
        return bool(self.attribute_1 & ATTRIBUTE_H_FLIP)

    @property
    def vertical_flip(self) -> bool:
        return bool(self.attribute_1 & ATTRIBUTE_V_FLIP)

    @property
    def dimensions(self) -> tuple[int, int] | None:
        """The pixel dimensions the attribute pair decodes to, or ``None``.

        ``None`` means the shape field is the reserved value 3, which this
        hardware does not use; no canonical piece takes that value.
        """
        if self.shape >= len(OBJECT_DIMENSIONS):
            return None
        return OBJECT_DIMENSIONS[self.shape][self.size]


@dataclass(frozen=True, slots=True)
class FrameRecord:
    """One frame record: an 8-byte header and ``piece_count`` 12-byte pieces.

    The header holds the piece count and the frame's own bounding box over those
    pieces: signed minimum x and y, then unsigned width and height.
    """

    address: int
    piece_count: int
    header_min_x: int
    header_min_y: int
    header_width: int
    header_height: int
    pieces: tuple[Piece, ...]

    @property
    def end_address(self) -> int:
        return self.address + FRAME_HEADER_SIZE + PIECE_RECORD_SIZE * self.piece_count

    @property
    def piece_bounds(self) -> tuple[int, int, int, int]:
        """``(min_x, min_y, width, height)`` computed from the pieces themselves."""
        min_x = min(piece.x for piece in self.pieces)
        min_y = min(piece.y for piece in self.pieces)
        max_x = max(piece.x + piece.dim_0 for piece in self.pieces)
        max_y = max(piece.y + piece.dim_1 for piece in self.pieces)
        return min_x, min_y, max_x - min_x, max_y - min_y

    @property
    def header_bounds(self) -> tuple[int, int, int, int]:
        return (
            self.header_min_x,
            self.header_min_y,
            self.header_width,
            self.header_height,
        )


def read_frame(data: bytes, address: int) -> FrameRecord:
    """Read the frame record at ``address``, bounded by its own piece count."""
    if not in_rom(data, address):
        raise FrameProbeError(f"frame address {address:#010x} is not in ROM")
    count = _u32(data, address + FRAME_PIECE_COUNT)
    if count == 0 or count > 16:
        raise FrameProbeError(
            f"frame at {address:#010x} declares {count} pieces, outside 1..16"
        )
    end = address + FRAME_HEADER_SIZE + PIECE_RECORD_SIZE * count
    if end > ROM_BASE + len(data):
        raise FrameProbeError(f"frame at {address:#010x} runs past the image")
    pieces = tuple(
        read_piece(data, address + FRAME_HEADER_SIZE + PIECE_RECORD_SIZE * i)
        for i in range(count)
    )
    return FrameRecord(
        address=address,
        piece_count=count,
        header_min_x=_s8(_u8(data, address + FRAME_HEADER_MIN_X)),
        header_min_y=_s8(_u8(data, address + FRAME_HEADER_MIN_Y)),
        header_width=_u8(data, address + FRAME_HEADER_WIDTH),
        header_height=_u8(data, address + FRAME_HEADER_HEIGHT),
        pieces=pieces,
    )


def read_piece(data: bytes, address: int) -> Piece:
    if address + PIECE_RECORD_SIZE > ROM_BASE + len(data):
        raise FrameProbeError(f"piece at {address:#010x} runs past the image")
    return Piece(
        address=address,
        x=_s8(_u8(data, address + PIECE_X)),
        y=_s8(_u8(data, address + PIECE_Y)),
        dim_0=_u8(data, address + PIECE_DIM_0),
        dim_1=_u8(data, address + PIECE_DIM_1),
        attributes_raw=_u32(data, address + PIECE_ATTRIBUTES),
        graphics_raw=_u32(data, address + PIECE_GRAPHICS),
    )


def frame_addresses(data: bytes) -> list[int]:
    """Every distinct non-null frame cell target, in ascending order."""
    found: set[int] = set()
    for address in animation_addresses(data):
        found.update(v for v in read_animation(data, address).cells if v)
    return sorted(found)


@dataclass(frozen=True, slots=True)
class AnimationWalk:
    """Every animation *reference*, walked through the cell table.

    ``cell_references`` counts cells over every reference, so a shared animation
    is walked once per definition that selects it - the population LOGX-SPRITE-001
    reported as 13,660.  ``unique_frame_targets`` is the distinct-target
    population and is a different number.
    """

    references: int
    cell_references: int
    unique_frame_targets: set[int]
    piece_references: int
    malformed_cell_references: int
    malformed_piece_references: int
    malformed_graphics_references: int
    malformed_animations: tuple[int, ...]
    frame_piece_counts: dict[int, int]

    @property
    def unique_frame_reference_count(self) -> int:
        return len(self.unique_frame_targets)


def walk_animations(data: bytes) -> AnimationWalk:
    """Walk every animation reference and validate each cell independently.

    A cell is *malformed* when it is not a ROM pointer, when the frame record it
    names declares an impossible piece count, or when the piece's graphics word
    is neither of the two stored forms.  Each animation that produces at least
    one malformed cell is listed, so a report never has to infer which records
    are unhealthy from a global count.
    """
    references = 0
    cell_references = 0
    unique_frames: set[int] = set()
    piece_references = 0
    malformed_cells = 0
    malformed_pieces = 0
    malformed_graphics = 0
    malformed_animations: list[int] = []
    piece_counts: dict[int, int] = {}

    for definition in sprite.iter_definitions(data):
        for value in definition.array:
            if not value:
                continue
            references += 1
            try:
                animation = read_animation(data, value)
            except FrameProbeError:
                malformed_animations.append(value)
                continue
            unhealthy = False
            for target in animation.cells:
                cell_references += 1
                if not in_rom(data, target):
                    malformed_cells += 1
                    unhealthy = True
                    continue
                unique_frames.add(target)
                try:
                    record = read_frame(data, target)
                except FrameProbeError:
                    malformed_pieces += 1
                    unhealthy = True
                    continue
                piece_counts[record.piece_count] = piece_counts.get(record.piece_count, 0) + 1
                piece_references += record.piece_count
                for piece in record.pieces:
                    if resolves_to_graphics(data, piece) is None:
                        malformed_graphics += 1
                        unhealthy = True
            if unhealthy:
                malformed_animations.append(value)

    return AnimationWalk(
        references=references,
        cell_references=cell_references,
        unique_frame_targets=unique_frames,
        piece_references=piece_references,
        malformed_cell_references=malformed_cells,
        malformed_piece_references=malformed_pieces,
        malformed_graphics_references=malformed_graphics,
        malformed_animations=tuple(sorted(set(malformed_animations))),
        frame_piece_counts=piece_counts,
    )


@_memoise
def animation_walk_census(data: bytes) -> dict[str, Any]:
    """The populations the ticket requires to stay apart, over animation references."""
    walk = walk_animations(data)
    return {
        "animation_references": walk.references,
        "cell_references": walk.cell_references,
        "unique_frame_targets": len(walk.unique_frame_targets),
        "piece_references": walk.piece_references,
        "malformed_cell_references": walk.malformed_cell_references,
        "malformed_piece_references": walk.malformed_piece_references,
        "malformed_graphics_references": walk.malformed_graphics_references,
        "malformed_animations": [f"{value:#010x}" for value in walk.malformed_animations],
        "healthy_animations": walk.references - len(walk.malformed_animations),
        "piece_count_references": dict(sorted(walk.frame_piece_counts.items())),
    }


def animation_addresses(data: bytes) -> list[int]:
    """Every distinct non-null animation target of the accepted definition run."""
    return sorted(
        {
            value
            for definition in sprite.iter_definitions(data)
            for value in definition.array
            if value
        }
    )


# --- censuses ----------------------------------------------------------------


@_memoise
def animation_reference_census(data: bytes) -> dict[str, Any]:
    """Section A: the 1,721 non-null references and their sharing.

    Reference count and unique-target count are separate populations and stay
    separate in the report.
    """
    definitions = sprite.iter_definitions(data)
    references: list[tuple[int, int, int]] = []
    for definition in definitions:
        for index, value in enumerate(definition.array):
            references.append((definition.identifier, index, value))

    non_null = [(d, i, v) for d, i, v in references if v]
    counts: dict[int, int] = {}
    for _, _, value in non_null:
        counts[value] = counts.get(value, 0) + 1
    resolvable = {value: in_rom(data, value) for value in counts}
    malformed = sorted(value for value, ok in resolvable.items() if not ok)
    return {
        "definitions": len(definitions),
        "array_slots": len(references),
        "non_null_references": len(non_null),
        "null_slots": len(references) - len(non_null),
        "unique_animation_targets": len(counts),
        "malformed_targets": [f"{value:#010x}" for value in malformed],
        "minimum_target": f"{min(counts):#010x}",
        "maximum_target": f"{max(counts):#010x}",
        "all_word_aligned": all(value % 4 == 0 for value in counts),
        "max_reuse": max(counts.values()),
        "shared_targets": sum(1 for value in counts.values() if value > 1),
        "reuse_histogram": _histogram(counts.values()),
    }


def _histogram(values: Sequence[int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


@_memoise
def cell_census(data: bytes) -> dict[str, Any]:
    """Section E/H: the frame/direction cell population and its sharing."""
    addresses = animation_addresses(data)
    animations = [read_animation(data, address) for address in addresses]
    cells = [value for animation in animations for value in animation.cells]
    non_null = [value for value in cells if value]
    by_direction: dict[int, dict[str, int]] = {
        direction: {"present": 0, "non_null": 0, "null": 0}
        for direction in range(ANIMATION_DIRECTIONS)
    }
    for animation in animations:
        for frame in range(animation.frame_count):
            for direction in range(ANIMATION_DIRECTIONS):
                bucket = by_direction[direction]
                bucket["present"] += 1
                if animation.cell(frame, direction):
                    bucket["non_null"] += 1
                else:
                    bucket["null"] += 1

    counts: dict[int, int] = {}
    for value in non_null:
        counts[value] = counts.get(value, 0) + 1

    # How many distinct *visual positions* one frame unit carries: the four
    # cells of a frame are independent poses, and this measures how often they
    # are literally the same.
    identical_rows = 0
    distinct_per_row: dict[int, int] = {}
    rows = 0
    for animation in animations:
        for frame in range(animation.frame_count):
            rows += 1
            row = [animation.cell(frame, direction) for direction in range(ANIMATION_DIRECTIONS)]
            distinct = len(set(row))
            distinct_per_row[distinct] = distinct_per_row.get(distinct, 0) + 1
            if distinct == 1:
                identical_rows += 1

    frame_counts: dict[int, int] = {}
    for animation in animations:
        frame_counts[animation.frame_count] = frame_counts.get(animation.frame_count, 0) + 1

    return {
        "unique_animations": len(animations),
        "frame_units": rows,
        "cells": len(cells),
        "non_null_cells": len(non_null),
        "null_cells": len(cells) - len(non_null),
        "cells_by_direction_index": {
            str(index): bucket for index, bucket in sorted(by_direction.items())
        },
        "unique_frame_targets": len(counts),
        "shared_frame_targets": sum(1 for value in counts.values() if value > 1),
        "max_frame_reuse": max(counts.values()) if counts else 0,
        "frame_reuse_histogram": _histogram(counts.values()),
        "frame_count_distribution": dict(sorted(frame_counts.items())),
        "distinct_cells_per_frame_unit": dict(sorted(distinct_per_row.items())),
        "frame_units_with_one_distinct_cell": identical_rows,
    }


@_memoise
def frame_census(data: bytes) -> dict[str, Any]:
    """Section F/I/J: frame records, piece counts and piece records."""
    addresses = frame_addresses(data)
    piece_counts: dict[int, int] = {}
    piece_records = 0
    piece_references = 0
    for address in addresses:
        record = read_frame(data, address)
        piece_counts[record.piece_count] = piece_counts.get(record.piece_count, 0) + 1
        piece_records += record.piece_count
        piece_references += record.piece_count
    return {
        "unique_frame_records": len(addresses),
        "piece_references": piece_references,
        "piece_count_distribution": dict(sorted(piece_counts.items())),
        "multi_piece_frames": sum(
            count for pieces, count in piece_counts.items() if pieces > 1
        ),
        "minimum_piece_count": min(piece_counts),
        "maximum_piece_count": max(piece_counts),
    }


@_memoise
def piece_census(data: bytes) -> dict[str, Any]:
    """Section J/K/L/M/N: the piece population, its fields and its graphics."""
    addresses = frame_addresses(data)
    x_values: dict[int, int] = {}
    y_values: dict[int, int] = {}
    dim_0: dict[int, int] = {}
    dim_1: dict[int, int] = {}
    attribute_words: dict[int, int] = {}
    shapes: dict[int, int] = {}
    sizes: dict[int, int] = {}
    flips: dict[str, int] = {}
    graphics_forms: dict[str, int] = {}
    graphics_targets: dict[int, int] = {}
    container_sizes: dict[int, int] = {}
    dim_match = 0
    attribute_dim_match = 0
    attribute_dim_mismatch = 0
    total = 0
    for address in addresses:
        for piece in read_frame(data, address).pieces:
            total += 1
            x_values[piece.x] = x_values.get(piece.x, 0) + 1
            y_values[piece.y] = y_values.get(piece.y, 0) + 1
            dim_0[piece.dim_0] = dim_0.get(piece.dim_0, 0) + 1
            dim_1[piece.dim_1] = dim_1.get(piece.dim_1, 0) + 1
            attribute_words[piece.attributes_raw] = (
                attribute_words.get(piece.attributes_raw, 0) + 1
            )
            shapes[piece.shape] = shapes.get(piece.shape, 0) + 1
            sizes[piece.size] = sizes.get(piece.size, 0) + 1
            key = f"H={int(piece.horizontal_flip)} V={int(piece.vertical_flip)}"
            flips[key] = flips.get(key, 0) + 1
            # The attribute pair's own decode must agree with the stored extents.
            if piece.dimensions == (piece.dim_0, piece.dim_1):
                attribute_dim_match += 1
            else:
                attribute_dim_mismatch += 1
            if piece.graphics_offset is None:
                graphics_forms["word_is_not_a_pointer"] = (
                    graphics_forms.get("word_is_not_a_pointer", 0) + 1
                )
                continue
            resolved = resolves_to_graphics(data, piece)
            if resolved is None:
                graphics_forms["container_does_not_resolve"] = (
                    graphics_forms.get("container_does_not_resolve", 0) + 1
                )
                continue
            form = "absolute" if piece.graphics_raw >= ROM_BASE else "relative"
            graphics_forms[form] = graphics_forms.get(form, 0) + 1
            graphics_targets[resolved] = graphics_targets.get(resolved, 0) + 1
            size = container_size(data, resolved)
            container_sizes[size] = container_sizes.get(size, 0) + 1
            dim_match += 1
    return {
        "piece_references": total,
        "unique_graphics_targets": len(graphics_targets),
        "graphics_pointer_forms": dict(sorted(graphics_forms.items())),
        "graphics_max_reuse": max(graphics_targets.values()) if graphics_targets else 0,
        "graphics_reuse_histogram": _histogram(graphics_targets.values()),
        "container_dimension_matches": dim_match,
        "attribute_dimension_matches": attribute_dim_match,
        "attribute_dimension_mismatches": attribute_dim_mismatch,
        "x_raw_distribution": dict(sorted(x_values.items())),
        "y_raw_distribution": dict(sorted(y_values.items())),
        "dimension_0_distribution": dict(sorted(dim_0.items())),
        "dimension_1_distribution": dict(sorted(dim_1.items())),
        "attribute_shape_distribution": dict(sorted(shapes.items())),
        "attribute_size_distribution": dict(sorted(sizes.items())),
        "flip_histogram": dict(sorted(flips.items())),
        "distinct_attribute_words": len(attribute_words),
        "container_declared_sizes": dict(sorted(container_sizes.items())),
    }


@_memoise
def frame_bbox_census(data: bytes) -> dict[str, Any]:
    """The frame header's bounding box, checked against the frame's own pieces.

    On every canonical frame the header's signed minimum x and y equal the minima
    over the frame's pieces, and its unsigned width and height equal the extent of
    their union.  That equality is what makes the four header bytes a bounding box
    rather than a raw word.
    """
    frames = 0
    xy_match = 0
    wh_match = 0
    both = 0
    mismatches: list[dict[str, Any]] = []
    for address in frame_addresses(data):
        record = read_frame(data, address)
        frames += 1
        bounds = record.piece_bounds
        header = record.header_bounds
        xy = (header[0], header[1]) == (bounds[0], bounds[1])
        wh = (header[2], header[3]) == (bounds[2], bounds[3])
        xy_match += int(xy)
        wh_match += int(wh)
        if xy and wh:
            both += 1
        elif len(mismatches) < 8:
            mismatches.append(
                {
                    "frame": f"{address:#010x}",
                    "header": list(header),
                    "pieces": list(bounds),
                }
            )
    return {
        "frames": frames,
        "header_minima_match_piece_minima": xy_match,
        "header_extents_match_piece_union": wh_match,
        "header_is_the_piece_bounding_box": both,
        "mismatches": mismatches,
    }


@_memoise
def graphics_pointer_census(data: bytes) -> dict[str, Any]:
    """Section N: the region and the resolution rate of the graphics words.

    The alignment and region checks are made over the **well-formed** population
    only; the malformed words are listed rather than allowed to drag a
    population-level claim to false.
    """
    offsets = []
    malformed: list[str] = []
    unresolved: list[str] = []
    for address in frame_addresses(data):
        for piece in read_frame(data, address).pieces:
            resolved = resolves_to_graphics(data, piece)
            if resolved is not None:
                offsets.append(resolved)
            elif piece.graphics_offset is None:
                malformed.append(f"{piece.graphics_raw:#010x}")
            else:
                unresolved.append(f"{piece.graphics_raw:#010x}")
    unique = sorted(set(offsets))
    decoding = 0
    failing = []
    for offset in unique:
        if container_size(data, offset) is None:
            failing.append(f"{offset:#08x}")
        else:
            decoding += 1
    return {
        "piece_references": len(offsets) + len(malformed) + len(unresolved),
        "resolvable": len(offsets),
        "words_that_are_not_pointers": len(malformed),
        "words_that_are_not_pointers_list": sorted(set(malformed)),
        "resolved_offset_whose_container_disagrees": len(unresolved),
        "resolved_offset_whose_container_disagrees_list": sorted(set(unresolved)),
        "unique_targets": len(unique),
        "unique_targets_that_decode": decoding,
        "unique_targets_that_fail": failing,
        "region_min": f"{min(unique):#08x}",
        "region_max": f"{max(unique):#08x}",
        "every_resolvable_target_word_aligned": all(offset % 4 == 0 for offset in unique),
        "every_resolvable_target_inside_the_measured_region": all(
            GRAPHICS_REGION_MIN <= offset <= GRAPHICS_REGION_MAX for offset in unique
        ),
    }


@_memoise
def trailer_census(data: bytes) -> dict[str, Any]:
    """The two words after the cell table, over the unique animation objects."""
    values_0: dict[int, int] = {}
    values_1: dict[int, int] = {}
    for address in animation_addresses(data):
        animation = read_animation(data, address)
        values_0[animation.trailer_0_raw] = values_0.get(animation.trailer_0_raw, 0) + 1
        values_1[animation.trailer_1_raw] = values_1.get(animation.trailer_1_raw, 0) + 1
    return {
        "animations": len(animation_addresses(data)),
        "trailer_0_histogram": dict(sorted(values_0.items())),
        "trailer_1_histogram": dict(sorted(values_1.items())),
        "trailer_1_distinct": len(values_1),
    }


@_memoise
def extent_census(data: bytes) -> dict[str, Any]:
    """Section S: how the animation and frame extents bound themselves.

    Two independent bounds are reported: the extent the leading count declares,
    and whether the record that follows starts exactly there.  Neither is
    inferred from pointer spacing alone.
    """
    addresses = animation_addresses(data)
    animations = [read_animation(data, address) for address in addresses]
    exact = 0
    overflow = 0
    aliased = 0
    frame_targets = set(frame_addresses(data))
    by_gap: dict[int, int] = {}
    for index, animation in enumerate(animations):
        if animation.table_end_address in frame_targets:
            aliased += 1
        if index + 1 == len(animations):
            continue
        gap = animations[index + 1].address - animation.end_address
        by_gap[gap] = by_gap.get(gap, 0) + 1
        if gap == 0:
            exact += 1
        elif gap < 0:
            overflow += 1

    frames = frame_addresses(data)
    frame_exact = 0
    frame_gap: dict[int, int] = {}
    frame_spans = sorted(
        (address, address + FRAME_HEADER_SIZE + PIECE_RECORD_SIZE * _u32(data, address))
        for address in frames
    )
    for index, (_, end) in enumerate(frame_spans[:-1]):
        gap = frame_spans[index + 1][0] - end
        frame_gap[gap] = frame_gap.get(gap, 0) + 1
        if gap == 0:
            frame_exact += 1

    return {
        "animations": len(animations),
        "consecutive_animation_pairs": max(0, len(animations) - 1),
        "animation_pairs_ending_exactly_where_the_next_begins": exact,
        "animation_pairs_where_the_count_overruns_the_next_record": overflow,
        # In some objects a frame record begins exactly where the table ends, so
        # the two words that follow the table are that record's header rather than
        # a trailer.  The count is reported because it bounds the trailer claim.
        "animations_whose_table_end_is_a_frame_record_start": aliased,
        # The animation objects are interleaved with the frame records and the
        # packed containers across one region, so the gap between two animation
        # objects is *other* data, never padding.  Only the summary is reported;
        # the full histogram is an inventory of other structures, not a finding.
        "animation_gap_minimum": min(by_gap) if by_gap else None,
        "animation_gap_maximum": max(by_gap) if by_gap else None,
        "animation_gap_distinct_values": len(by_gap),
        "animation_gaps_that_are_a_multiple_of_four": sum(
            1 for gap, count in by_gap.items() if gap % 4 == 0 for _ in range(count)
        ),
        "frame_records": len(frames),
        "consecutive_frame_pairs": max(0, len(frame_spans) - 1),
        "frame_pairs_ending_exactly_where_the_next_begins": frame_exact,
        "frame_gaps_that_are_a_multiple_of_four": sum(
            1 for gap, count in frame_gap.items() if gap % 4 == 0 for _ in range(count)
        ),
        "frame_gap_minimum": min(frame_gap) if frame_gap else None,
        "frame_gap_maximum": max(frame_gap) if frame_gap else None,
    }


@_memoise
def engine_census(data: bytes) -> dict[str, Any]:
    """Sections B/E/Q: the instruction sites that perform the cell arithmetic."""
    report: dict[str, Any] = {"instructions": {}}
    for name, (address, expected) in EVIDENCE_INSTRUCTIONS.items():
        mnemonic, operands, raw = instruction_at(data, address)
        text = f"{mnemonic} {operands}".rstrip()
        report["instructions"][name] = {
            "address": f"{address:#010x}",
            "text": text,
            "expected": expected,
            "matches": text == expected,
            "raw": raw.hex(),
        }
    report["all_match"] = all(entry["matches"] for entry in report["instructions"].values())
    return report


def state_table_direction_evidence(data: bytes) -> dict[str, Any]:
    """The direction index is produced as one of exactly four constants.

    The sites of :data:`DIRECTION_CONSTANT_SITES` write ``obj+0x10`` from a
    compare chain over two coordinate differences; the values written are
    0, 1, 2 and 3.  The report does not name which axis each value faces - that
    reading is recorded separately and marked INFERRED.
    """
    written: list[dict[str, Any]] = []
    for site, value in DIRECTION_CONSTANT_SITES:
        mnemonic, operands, _ = instruction_at(data, site)
        written.append(
            {
                "site": f"{site:#010x}",
                "value": value,
                "text": f"{mnemonic} {operands}".rstrip(),
            }
        )
    values = sorted({entry["value"] for entry in written})
    return {
        "constant_sites": written,
        "distinct_values": values,
        "writes_exactly_four_positions": values == [0, 1, 2, 3],
        "store_sites": {
            f"{site:#010x}": f"{instruction_at(data, site)[0]} {instruction_at(data, site)[1]}".rstrip()
            for site in DIRECTION_STORE_SITES
        },
    }


#: ``(site, constant)`` for each compile-time value written to the direction
#: index ``obj+0x10`` by the facing computers at ``0x0800A890`` and
#: ``0x080159B0``.  Each site is the ``movs`` whose very next instruction stores
#: that constant to ``obj+0x10``, so the value/position pairing is read out of
#: the code rather than assumed.
DIRECTION_CONSTANT_SITES: tuple[tuple[int, int], ...] = (
    (0x0800A8C2, 3),
    (0x0800A8C8, 2),
    (0x0800A8D2, 0),
    (0x0800A8D8, 1),
    (0x080159D4, 3),
    (0x080159DC, 2),
    (0x080159E6, 0),
    (0x080159EC, 1),
)

#: The stores that publish those constants to the object.  Each is the
#: instruction immediately after the matching :data:`DIRECTION_CONSTANT_SITES`
#: entry, so the pairing cannot drift.
DIRECTION_STORE_SITES: tuple[int, ...] = tuple(
    site + 2 for site, _ in DIRECTION_CONSTANT_SITES
)


@_memoise
def matrix_model_check(data: bytes) -> dict[str, Any]:
    """Independent check that the table is a 4-wide, 4-byte-stride matrix.

    Three structural facts are measured, each of which the alternative reading
    (``frame_count`` *direction* variants of four animation frames, or a
    16-byte frame record header) would falsify:

    1. every cell word is a ROM pointer, for every animation, with no exception;
    2. a frame target shared between two animations is always reached at the
       same *frame* index and different *direction* indices - i.e. the four
       cells of a frame index are alternative poses of one pose slot;
    3. no two animation objects overlap, so the counted extent is a real bound.
    """
    animations = [read_animation(data, address) for address in animation_addresses(data)]
    cell_targets = 0
    non_pointers = 0
    for animation in animations:
        for value in animation.cells:
            cell_targets += 1
            if not in_rom(data, value):
                non_pointers += 1

    sites: dict[int, list[tuple[int, int, int]]] = {}
    for animation in animations:
        for frame in range(animation.frame_count):
            for direction in range(ANIMATION_DIRECTIONS):
                value = animation.cell(frame, direction)
                if value:
                    sites.setdefault(value, []).append((animation.address, frame, direction))
    shared = {value: where for value, where in sites.items() if len(where) > 1}
    same_frame = 0
    cross_frame = 0
    for where in shared.values():
        if len({frame for _, frame, _ in where}) == 1:
            same_frame += 1
        else:
            cross_frame += 1

    spans = sorted((a.address, a.end_address) for a in animations)
    overlaps = sum(
        1 for index, (_, end) in enumerate(spans[:-1]) if spans[index + 1][0] < end
    )

    return {
        "cell_targets": cell_targets,
        "cell_targets_that_are_not_rom_pointers": non_pointers,
        "shared_frame_targets": len(shared),
        "shared_targets_confined_to_one_frame_index": same_frame,
        "shared_targets_spanning_frame_indices": cross_frame,
        "overlapping_animation_objects": overlaps,
    }


############################################
# engine instruction evidence
############################################


@lru_cache(maxsize=1)
def _decode_thumb_at() -> Callable[[bytes, int], Any]:
    """The Thumb decoder, imported on first use rather than at module import."""
    from tools.research.thumb_disasm import decode_thumb_at

    return decode_thumb_at


def instruction_at(data: bytes, address: int) -> tuple[str, str, bytes]:
    """``(mnemonic, operands, raw bytes)`` for the Thumb instruction at a site."""
    item = _decode_thumb_at()(data, address)
    if item is None:
        raise FrameProbeError(f"no Thumb instruction decodes at {address:#010x}")
    offset = address - ROM_BASE
    return item.mnemonic, item.operands, data[offset : offset + item.size]


def format_instruction(data: bytes, address: int) -> str:
    mnemonic, operands, _ = instruction_at(data, address)
    return f"{address:08x}  {mnemonic:<9} {operands}".rstrip()


def cell_arithmetic_trace(data: bytes, animation_address: int, frame: int, direction: int) -> dict[str, Any]:
    """Reproduce the engine's own cell address for one (frame, direction)."""
    animation = read_animation(data, animation_address)
    return {
        "animation": f"{animation.address:#010x}",
        "frame_count": animation.frame_count,
        "frame": frame,
        "direction": direction,
        "base": f"{animation.address:#010x}",
        "cell_address": f"{animation.cell_address(frame, direction):#010x}",
        "cell_address_by_stride": f"{animation.table_address + ANIMATION_ROW_STRIDE * frame + 4 * direction:#010x}",
        "flat_index": ANIMATION_DIRECTIONS * frame + direction,
        "target": f"{animation.cell(frame, direction):#010x}",
    }


def representative_report(data: bytes, animation_address: int) -> dict[str, Any]:
    """One animation object read end to end, for the report and the tests."""
    animation = read_animation(data, animation_address)
    rows = []
    for frame in range(animation.frame_count):
        row = []
        for direction in range(ANIMATION_DIRECTIONS):
            target = animation.cell(frame, direction)
            entry: dict[str, Any] = {
                "frame": frame,
                "direction": direction,
                "target": f"{target:#010x}",
                "cell_address": f"{animation.cell_address(frame, direction):#010x}",
            }
            if target and in_rom(data, target):
                record = read_frame(data, target)
                entry["piece_count"] = record.piece_count
                entry["header_bounds"] = list(record.header_bounds)
                entry["piece_bounds"] = list(record.piece_bounds)
                entry["pieces"] = [
                    {
                        "address": f"{piece.address:#010x}",
                        "x": piece.x,
                        "y": piece.y,
                        "dim_0": piece.dim_0,
                        "dim_1": piece.dim_1,
                        "attributes_raw": f"{piece.attributes_raw:#010x}",
                        "shape": piece.shape,
                        "size": piece.size,
                        "horizontal_flip": piece.horizontal_flip,
                        "vertical_flip": piece.vertical_flip,
                        "graphics_raw": f"{piece.graphics_raw:#010x}",
                        "graphics_offset": (
                            f"{piece.graphics_offset:#08x}"
                            if piece.graphics_offset is not None
                            else None
                        ),
                        "container_declared_size": (
                            container_size(data, resolved)
                            if (
                                resolved := resolves_to_graphics(data, piece)
                            )
                            is not None
                            else None
                        ),
                    }
                    for piece in record.pieces
                ]
            row.append(entry)
        rows.append(row)
    return {
        "address": f"{animation.address:#010x}",
        "frame_count": animation.frame_count,
        "cells": [f"{value:#010x}" for value in animation.cells],
        "trailer_0_raw": f"{animation.trailer_0_raw:#010x}",
        "trailer_1_raw": f"{animation.trailer_1_raw:#010x}",
        "end_address": f"{animation.end_address:#010x}",
        "rows": rows,
    }


def census(data: bytes, *, include_engine: bool = True) -> dict[str, Any]:
    """Every section the ticket's full-census mode reports."""
    report: dict[str, Any] = {
        "canonical_sha256": CANONICAL_SHA256,
        "image_sha256": sha256_of(data),
        "animation_references": animation_reference_census(data),
        "animation_walk": animation_walk_census(data),
        "cells": cell_census(data),
        "frames": frame_census(data),
        "pieces": piece_census(data),
        "graphics": graphics_pointer_census(data),
        "trailers": trailer_census(data),
        "extents": extent_census(data),
        "matrix_model": matrix_model_check(data),
        "frame_bbox": frame_bbox_census(data),
    }
    if include_engine:
        report["engine"] = engine_census(data)
        report["direction_constants"] = state_table_direction_evidence(data)
    return report


# --- rows -------------------------------------------------------------------


def animation_rows(data: bytes) -> list[dict[str, Any]]:
    """One row per animation *reference*; the census population, not the uniques."""
    rows = []
    for definition in sprite.iter_definitions(data):
        for slot, value in enumerate(definition.array):
            row: dict[str, Any] = {
                "definition_id": definition.identifier,
                "animation_slot": slot,
                "animation_address": f"{value:#010x}" if value else None,
                "frame_count": None,
                "cells": None,
                "non_null_cells": None,
                "trailer_0_raw": None,
                "trailer_1_raw": None,
                "anomaly": None,
            }
            if not value:
                row["anomaly"] = "null_animation_slot"
                rows.append(row)
                continue
            if not in_rom(data, value):
                row["anomaly"] = "animation_target_not_in_rom"
                rows.append(row)
                continue
            try:
                animation = read_animation(data, value)
            except FrameProbeError as exc:
                row["anomaly"] = str(exc)
                rows.append(row)
                continue
            row["frame_count"] = animation.frame_count
            row["cells"] = animation.cell_count
            row["non_null_cells"] = animation.non_null_cells
            row["trailer_0_raw"] = f"{animation.trailer_0_raw:#010x}"
            row["trailer_1_raw"] = f"{animation.trailer_1_raw:#010x}"
            if animation.non_null_cells != animation.cell_count:
                row["anomaly"] = "null_cell"
            rows.append(row)
    return rows


def frame_rows(data: bytes) -> list[dict[str, Any]]:
    """One row per distinct frame target."""
    rows = []
    for address in frame_addresses(data):
        try:
            record = read_frame(data, address)
        except FrameProbeError as exc:
            rows.append({"frame_address": f"{address:#010x}", "anomaly": str(exc)})
            continue
        rows.append(
            {
                "frame_address": f"{address:#010x}",
                "piece_count": record.piece_count,
                "end_address": f"{record.end_address:#010x}",
                "pieces": [
                    {
                        "x": piece.x,
                        "y": piece.y,
                        "dim_0": piece.dim_0,
                        "dim_1": piece.dim_1,
                        "attributes_raw": f"{piece.attributes_raw:#010x}",
                        "shape": piece.shape,
                        "size": piece.size,
                        "horizontal_flip": piece.horizontal_flip,
                        "vertical_flip": piece.vertical_flip,
                        "graphics_raw": f"{piece.graphics_raw:#010x}",
                        "graphics_offset": (
                            f"{piece.graphics_offset:#08x}"
                            if piece.graphics_offset is not None
                            else None
                        ),
                    }
                    for piece in record.pieces
                ],
                "anomaly": None,
            }
        )
    return rows


# --- CLI ---------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rom", type=Path, help="path to the canonical Buu's Fury image")
    parser.add_argument(
        "--census",
        action="store_true",
        help=(
            "print the full deterministic census (JSON). The engine-instruction "
            "section is included unless --no-engine is given, because it needs "
            "the optional capstone dependency"
        ),
    )
    parser.add_argument("--rows", action="store_true", help="print one row per animation reference")
    parser.add_argument("--frames", action="store_true", help="print one row per distinct frame")
    parser.add_argument(
        "--representative",
        type=lambda text: int(text, 0),
        default=None,
        metavar="ADDRESS",
        help="read one animation object end to end",
    )
    parser.add_argument(
        "--engine",
        action="store_true",
        help="print only the engine instruction evidence (requires capstone)",
    )
    parser.add_argument(
        "--no-engine",
        action="store_true",
        help="omit the engine section from --census, so the report needs no capstone",
    )
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    ran = False
    if args.census:
        print(
            json.dumps(
                census(data, include_engine=not args.no_engine), indent=2, sort_keys=True
            )
        )
        ran = True
    if args.engine:
        print(json.dumps(engine_census(data), indent=2, sort_keys=True))
        print(json.dumps(state_table_direction_evidence(data), indent=2, sort_keys=True))
        ran = True
    if args.representative is not None:
        print(
            json.dumps(
                representative_report(data, args.representative), indent=2, sort_keys=True
            )
        )
        ran = True
    if args.rows:
        for row in animation_rows(data):
            print(json.dumps(row, sort_keys=True))
        ran = True
    if args.frames:
        for row in frame_rows(data):
            print(json.dumps(row, sort_keys=True))
        ran = True
    if not ran:
        if args.no_engine:
            parser.error("--no-engine modifies --census; give --census as well")
        parser.print_help()
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
