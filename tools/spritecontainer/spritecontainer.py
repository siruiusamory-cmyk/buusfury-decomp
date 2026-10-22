from __future__ import annotations

import struct

ROM_BASE = 0x08000000
CHARACTER_TABLE = 0x6B6BDC
CHARACTER_COUNT = 297


def references(rom: bytes) -> dict[int, int]:
    offsets: dict[int, int] = {}
    for index in range(CHARACTER_COUNT):
        address = struct.unpack_from("<I", rom, CHARACTER_TABLE + 4 * index)[0]
        if not ROM_BASE <= address < ROM_BASE + len(rom):
            raise ValueError("character %d holds %#010x" % (index, address))
        structure = address - ROM_BASE
        animations = rom[structure]
        for slot in range(animations):
            pointer = struct.unpack_from("<I", rom, structure + 0x54 + 4 * slot)[0]
            if pointer == 0:
                continue
            if not ROM_BASE <= pointer < ROM_BASE + len(rom):
                raise ValueError("character %d slot %d holds %#010x" % (index, slot, pointer))
            animation = pointer - ROM_BASE
            frames = struct.unpack_from("<I", rom, animation)[0]
            for frame_index in range(frames):
                for direction in range(4):
                    frame_pointer = struct.unpack_from(
                        "<I", rom, animation + 4 + 4 * (frame_index * 4 + direction))[0]
                    if frame_pointer == 0:
                        continue
                    if not ROM_BASE <= frame_pointer < ROM_BASE + len(rom):
                        raise ValueError("animation at %#x frame %d holds %#010x"
                                         % (animation, frame_index, frame_pointer))
                    frame = frame_pointer - ROM_BASE
                    pieces = struct.unpack_from("<I", rom, frame)[0]
                    for piece in range(pieces):
                        graphics = struct.unpack_from("<I", rom, frame + 8 + 12 * piece + 8)[0]
                        if not ROM_BASE <= graphics < ROM_BASE + len(rom):
                            raise ValueError("piece at %#x holds %#010x" % (frame, graphics))
                        offsets[graphics - ROM_BASE] = offsets.get(graphics - ROM_BASE, 0) + 1
    return offsets


def container_offsets(rom: bytes) -> list[int]:
    return sorted(references(rom))
