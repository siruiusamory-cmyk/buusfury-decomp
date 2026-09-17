"""Portable tests for the LOGX-FRAME-001 research probe.

Nothing here needs the private ROM: every case is synthetic bytes or pure
arithmetic, so the portable unit job exercises the parser's shape, its
fail-closed behaviour and its dependency boundary without a commercial image.
The ROM-gated evidence lives in ``tests/integration/test_logx_frame_rom.py``.
"""

from __future__ import annotations

import ast
import builtins
import importlib.util
import sys
from pathlib import Path

import pytest

from tools.research import logx_frame_probe as probe

ROM_BASE = probe.ROM_BASE
REPO_ROOT = Path(__file__).resolve().parents[2]


def synthetic_image(size: int = 0x2000) -> bytearray:
    """A zero-filled image of ROM length, not the canonical one."""
    return bytearray(size)


def write_u32(data: bytearray, address: int, value: int) -> None:
    data[address - ROM_BASE : address - ROM_BASE + 4] = value.to_bytes(4, "little")


# --- address arithmetic -------------------------------------------------------


def test_animation_table_arithmetic_is_the_engine_expression() -> None:
    """``base + 4 + 16*frame + 4*direction`` is what ``Animation`` computes."""
    animation = probe.Animation(
        address=0x0850C1DC,
        frame_count=4,
        cells=tuple(range(1, 17)),
        trailer_0_raw=1,
        trailer_1_raw=0x400,
    )
    assert animation.table_address == 0x0850C1DC + probe.ANIMATION_TABLE
    for frame in range(4):
        for direction in range(4):
            assert animation.cell_address(frame, direction) == (
                0x0850C1DC + 4 + 16 * frame + 4 * direction
            )
            assert animation.cell(frame, direction) == 4 * frame + direction + 1
    assert animation.table_end_address == 0x0850C1DC + 4 + 64
    assert animation.end_address == animation.table_end_address + 8
    assert animation.cell_count == 16
    assert animation.non_null_cells == 16


def test_cell_address_rejects_out_of_range_indices() -> None:
    animation = probe.Animation(
        address=0x0850C1DC,
        frame_count=2,
        cells=tuple(range(1, 9)),
        trailer_0_raw=1,
        trailer_1_raw=1,
    )
    with pytest.raises(probe.FrameProbeError, match="frame 2 outside"):
        animation.cell_address(2, 0)
    with pytest.raises(probe.FrameProbeError, match="direction 4 outside"):
        animation.cell_address(0, 4)


def test_frame_extent_is_the_header_plus_the_pieces() -> None:
    record = probe.FrameRecord(
        address=0x08423128,
        piece_count=2,
        header_min_x=0,
        header_min_y=0,
        header_width=0,
        header_height=0,
        pieces=(),
    )
    assert record.end_address == 0x08423128 + probe.FRAME_HEADER_SIZE + 2 * probe.PIECE_RECORD_SIZE
    assert probe.FRAME_HEADER_SIZE == 8
    assert probe.PIECE_RECORD_SIZE == 12
    assert probe.FRAME_HEADER_MIN_X == 4
    assert probe.FRAME_HEADER_MIN_Y == 5
    assert probe.FRAME_HEADER_WIDTH == 6
    assert probe.FRAME_HEADER_HEIGHT == 7


def test_table_bytes_helper() -> None:
    assert probe.table_bytes(1) == 16
    assert probe.table_bytes(4) == 64
    assert probe.table_bytes(16) == 256


# --- record parsing on synthetic bytes ---------------------------------------


def test_read_animation_parses_a_synthetic_record() -> None:
    data = synthetic_image()
    address = 0x08001000
    write_u32(data, address + 0x00, 2)
    for index in range(8):
        write_u32(data, address + 0x04 + 4 * index, 0x08002000 + 4 * index)
    write_u32(data, address + 0x04 + 32, 1)
    write_u32(data, address + 0x04 + 36, 0x400)

    animation = probe.read_animation(bytes(data), address)
    assert animation.frame_count == 2
    assert animation.cells == tuple(0x08002000 + 4 * i for i in range(8))
    assert animation.trailer_0_raw == 1
    assert animation.trailer_1_raw == 0x400
    assert animation.end_address == address + 0x04 + 32 + 8


def test_read_animation_rejects_a_zero_or_oversized_frame_count() -> None:
    for value, match in ((0, "out-of-range frame count 0"), (17, "out-of-range frame count 17")):
        data = synthetic_image()
        address = 0x08001000
        write_u32(data, address, value)
        with pytest.raises(probe.FrameProbeError, match=match):
            probe.read_animation(bytes(data), address)


def test_read_animation_rejects_a_nonzero_second_halfword() -> None:
    """The count's high half is checked, so a stray byte above it is caught."""
    data = synthetic_image()
    address = 0x08001000
    write_u32(data, address, 1)
    assert probe._u16(bytes(data), address + 2) == 0
    data[address - ROM_BASE + 2] = 0x01
    assert probe._u16(bytes(data), address + 2) == 1
    with pytest.raises(probe.FrameProbeError) as caught:
        probe.read_animation(bytes(data), address)
    message = str(caught.value)
    assert "second halfword" in message or "frame count" in message


def test_read_animation_rejects_an_address_outside_the_image() -> None:
    data = synthetic_image()
    with pytest.raises(probe.FrameProbeError, match="not in ROM"):
        probe.read_animation(bytes(data), 0x08000002)
    with pytest.raises(probe.FrameProbeError, match="not in ROM"):
        probe.read_animation(bytes(data), 0x09000000)


def test_read_frame_reads_pieces_at_the_engine_offsets() -> None:
    data = synthetic_image()
    address = 0x08001000
    write_u32(data, address + 0x00, 2)
    # The header's four bytes are the frame's bounding box over its pieces:
    # min_x -8, min_y -24, union width 32, union height 48.
    data[address - ROM_BASE + probe.FRAME_HEADER_MIN_X] = 0xF8  # -8
    data[address - ROM_BASE + probe.FRAME_HEADER_MIN_Y] = 0xE8  # -24
    data[address - ROM_BASE + probe.FRAME_HEADER_WIDTH] = 0x20
    data[address - ROM_BASE + probe.FRAME_HEADER_HEIGHT] = 0x30
    first = address + probe.FRAME_HEADER_SIZE
    second = first + probe.PIECE_RECORD_SIZE
    data[first - ROM_BASE + probe.PIECE_X] = 0xF8  # -8
    data[first - ROM_BASE + probe.PIECE_Y] = 0xE8  # -24
    data[first - ROM_BASE + probe.PIECE_DIM_0] = 0x20
    data[first - ROM_BASE + probe.PIECE_DIM_1] = 0x20
    # shape 0, size 2 (32x32), colour-256: (attr1 << 16) | attr0
    write_u32(data, first + probe.PIECE_ATTRIBUTES, 0x80002000)
    write_u32(data, first + probe.PIECE_GRAPHICS, 0x08001800)
    data[second - ROM_BASE + probe.PIECE_X] = 0x08
    data[second - ROM_BASE + probe.PIECE_Y] = 0xF8
    data[second - ROM_BASE + probe.PIECE_DIM_0] = 0x10
    data[second - ROM_BASE + probe.PIECE_DIM_1] = 0x20
    # shape 2, size 2 -> 16x32 (vertical), colour-256
    write_u32(data, second + probe.PIECE_ATTRIBUTES, 0x8000A000)
    write_u32(data, second + probe.PIECE_GRAPHICS, 0x08001840)

    record = probe.read_frame(bytes(data), address)
    assert record.piece_count == 2
    assert record.header_bounds == (-8, -24, 0x20, 0x30)
    assert record.header_bounds == record.piece_bounds
    assert record.end_address == address + 8 + 24
    assert [piece.address for piece in record.pieces] == [first, second]
    assert (record.pieces[0].x, record.pieces[0].y) == (-8, -24)
    assert (record.pieces[0].dim_0, record.pieces[0].dim_1) == (0x20, 0x20)
    assert record.pieces[0].attributes_raw == 0x80002000
    assert record.pieces[0].shape == 0
    assert record.pieces[0].size == 2
    assert record.pieces[0].colour_256 is True
    assert record.pieces[0].horizontal_flip is False
    assert record.pieces[0].dimensions == (32, 32)
    assert record.pieces[0].graphics_raw == 0x08001800
    assert record.pieces[1].x == 8
    assert record.pieces[1].y == -8
    assert record.pieces[1].dim_0 == 0x10
    assert record.pieces[1].dimensions == (16, 32)


def test_piece_attribute_decode_reports_a_reserved_shape() -> None:
    """Shape 3 is reserved on this hardware, so ``dimensions`` refuses it."""
    data = synthetic_image()
    address = 0x08001000
    write_u32(data, address + probe.PIECE_ATTRIBUTES, 0x8000C000)  # shape 3
    piece = probe.read_piece(bytes(data), address)
    assert piece.shape == 3
    assert piece.dimensions is None


def test_piece_flip_bits_come_from_attribute_1() -> None:
    data = synthetic_image()
    address = 0x08001000
    for word, expected in (
        (0x80002000, (False, False)),
        (0x90002000, (True, False)),
        (0xA0002000, (False, True)),
        (0xB0002000, (True, True)),
    ):
        write_u32(data, address + probe.PIECE_ATTRIBUTES, word)
        piece = probe.read_piece(bytes(data), address)
        assert (piece.horizontal_flip, piece.vertical_flip) == expected, hex(word)


def test_read_frame_rejects_a_zero_or_oversized_piece_count() -> None:
    for value, match in ((0, "declares 0 pieces"), (17, "declares 17 pieces")):
        data = synthetic_image()
        address = 0x08001000
        write_u32(data, address, value)
        with pytest.raises(probe.FrameProbeError, match=match):
            probe.read_frame(bytes(data), address)


def test_read_frame_rejects_a_record_that_runs_past_the_image() -> None:
    data = synthetic_image(0x1000)
    address = ROM_BASE + 0x0FF0
    write_u32(data, address, 4)
    with pytest.raises(probe.FrameProbeError, match="runs past the image"):
        probe.read_frame(bytes(data), address)


# --- graphics word resolution -------------------------------------------------


def test_to_file_offset_accepts_both_stored_forms() -> None:
    assert probe.to_file_offset(0x0850C200) == 0x0050C200
    assert probe.to_file_offset(0x0050C200) == 0x0050C200
    assert probe.to_file_offset(0) == 0
    assert probe.to_file_offset(probe.ROM_SIZE - 1) == probe.ROM_SIZE - 1
    assert probe.to_file_offset(probe.ROM_BASE + probe.ROM_SIZE) is None
    assert probe.to_file_offset(0xFFFFFFFF) is None
    assert probe.to_file_offset(-1) is None


def test_resolves_to_graphics_rejects_a_word_that_is_not_a_pointer() -> None:
    data = synthetic_image()
    address = 0x08001000
    piece = probe.read_piece(bytes(data), address)
    assert piece.graphics_raw == 0
    assert probe.resolves_to_graphics(bytes(data), piece) is None


def test_is_graphics_target_bounds_the_measured_region() -> None:
    assert probe.is_graphics_target(probe.GRAPHICS_REGION_MIN)
    assert probe.is_graphics_target(probe.GRAPHICS_REGION_MAX)
    assert not probe.is_graphics_target(probe.GRAPHICS_REGION_MIN - 1)
    assert not probe.is_graphics_target(probe.GRAPHICS_REGION_MAX + 1)
    assert not probe.is_graphics_target(0x00000002)
    assert probe.GRAPHICS_REGION_MIN < probe.GRAPHICS_REGION_MAX


def test_resolves_to_graphics_requires_the_container_and_the_dimensions_to_agree() -> None:
    # A real, tiny stored container placed inside the measured graphics region.
    data = synthetic_image(0x00700000)
    container = ROM_BASE + probe.GRAPHICS_REGION_MIN
    write_u32(data, container, 0)
    write_u32(data, container + 4, 64)
    piece_address = 0x08001000
    data[piece_address - ROM_BASE + probe.PIECE_DIM_0] = 8
    data[piece_address - ROM_BASE + probe.PIECE_DIM_1] = 8
    write_u32(data, piece_address + probe.PIECE_GRAPHICS, container)

    piece = probe.read_piece(bytes(data), piece_address)
    assert piece.graphics_offset == container - ROM_BASE
    assert probe.resolves_to_graphics(bytes(data), piece) == container - ROM_BASE

    data[piece_address - ROM_BASE + probe.PIECE_DIM_0] = 16
    mismatched = probe.read_piece(bytes(data), piece_address)
    assert probe.resolves_to_graphics(bytes(data), mismatched) is None

    write_u32(data, piece_address + probe.PIECE_GRAPHICS, 0x00000002)
    outside = probe.read_piece(bytes(data), piece_address)
    assert outside.graphics_offset == 2
    assert probe.resolves_to_graphics(bytes(data), outside) is None


# --- the canonical gate -------------------------------------------------------


def test_verify_canonical_fails_closed() -> None:
    with pytest.raises(probe.FrameProbeError, match="expected 8388608"):
        probe.verify_canonical(b"\x00" * 16)
    with pytest.raises(probe.FrameProbeError, match="non-canonical"):
        probe.verify_canonical(b"\x00" * probe.ROM_SIZE)


def test_canonical_hash_is_the_ticket_hash() -> None:
    assert probe.CANONICAL_SHA256 == (
        "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"
    )
    assert probe.CANONICAL_SHA256 == probe.CANONICAL_SHA256.upper()


# --- dependency boundary ------------------------------------------------------


def test_the_probe_imports_and_censuses_without_capstone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Behavioural check: with capstone blocked, import and the census still work.

    A source-text grep would pass on a comment, so this actually installs an
    import hook that refuses ``capstone`` and re-imports the probe from scratch in
    a fresh module namespace.  The census API must import and parse; only the
    instruction reader may refuse.
    """
    probe_path = REPO_ROOT / "tools" / "research" / "logx_frame_probe.py"
    for blocker in ("capstone", "tools.research.thumb_disasm"):
        for name in [name for name in sys.modules if name.startswith(blocker)]:
            monkeypatch.delitem(sys.modules, name, raising=False)

    real_import = builtins.__import__

    def refusing_import(name, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        if name == "capstone":
            raise ImportError("capstone is not installed in this test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", refusing_import)
    module_name = "logx_frame_probe_no_capstone"
    spec = importlib.util.spec_from_file_location(module_name, probe_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before executing: dataclasses resolves ``cls.__module__`` through
    # ``sys.modules`` while the class body is being processed.
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    # The census API and the record parser are usable without the disassembler.
    assert module.CANONICAL_SHA256 == probe.CANONICAL_SHA256
    assert callable(module.census)
    assert callable(module.piece_census)
    data = synthetic_image()
    address = 0x08001000
    write_u32(data, address, 1)
    write_u32(data, address + 4, 0x08002000)
    assert module.read_animation(bytes(data), address).frame_count == 1

    # Only instruction text needs capstone, and its absence is loud.
    with pytest.raises(SystemExit, match="capstone is required"):
        module.instruction_at(bytes(data), 0x08000000)


def test_the_probe_never_imports_capstone_at_module_level() -> None:
    """The module-level import list must not contain the optional dependency."""
    source = (REPO_ROOT / "tools" / "research" / "logx_frame_probe.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    module_level: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            module_level.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.col_offset == 0:
            module_level.append(node.module)
    assert "capstone" not in module_level
    assert "tools.research.thumb_disasm" not in module_level


def test_the_optional_dependency_module_fails_loudly_when_capstone_is_gone() -> None:
    """``thumb_disasm`` raises rather than degrading silently."""
    source = (REPO_ROOT / "tools" / "research" / "thumb_disasm.py").read_text(encoding="utf-8")
    assert "raise SystemExit" in source
    assert "import capstone" in source
    if "capstone" in sys.modules:
        pytest.skip("capstone is installed in this environment; absence is not reachable")
