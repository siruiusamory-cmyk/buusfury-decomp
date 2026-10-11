"""Build a sprite definition that shows the donor's art in every animation the target's scripts use.

Why a copy and not a shared definition: a definition's animation array is what the engine indexes
when a script sets a state, and it does so with NO missing-animation check. Pointing a borrowed
definition at an actor therefore silently removes every animation the donor does not happen to have in
the same slot. Measured: the Heaven actor (map 451 slot 0) runs event resource 490, which sets state
12, and the borrowed definition's slot 12 is empty, so that actor gets no animation at all.

The copy keeps the donor's art everywhere it exists, and fills the slots the TARGET's own definition
occupied - plus every slot a script can select for that target - by building new animation records
from the donor's own frames:

* a slot the donor has and the target has, with the donor's frame count SHORTER than the target's, is
  padded by cycling the donor's frames up to the target's length, so an animation does not visibly
  end early;
* a slot the donor has and the target does not, or vice versa, keeps the donor's record;
* a slot the TARGET has and the donor does not is built from the donor animation whose frame count is
  closest, cycling to the target's count, because those frames are the donor's art standing in for a
  pose it does not draw.

Every choice that is a judgement call about MEANING (which donor animation stands in for a missing
pose) is recorded in the proof, so it can be questioned rather than buried.
"""

from __future__ import annotations

import struct

ROM_BASE = 0x08000000
CHARACTER_TABLE = 0x6B6BB4
ANIMATION_ARRAY = 0x54
HEADER_BYTES = 0x54


class DefinitionCopyError(Exception):
    """A refusal: the definition is not where or what this tool expects."""


def word(image: bytes, offset: int) -> int:
    return struct.unpack_from("<I", image, offset)[0]


def definition_offset(image: bytes, sprite_id: int) -> int:
    pointer = word(image, CHARACTER_TABLE + 4 * sprite_id)
    if pointer < ROM_BASE or pointer - ROM_BASE >= len(image):
        raise DefinitionCopyError(f"sprite {sprite_id} has no definition pointer")
    return pointer - ROM_BASE


def slots_of(image: bytes, sprite_id: int) -> list[int]:
    """The definition's animation records, one entry per slot, 0 for an empty slot."""
    at = definition_offset(image, sprite_id)
    count = image[at] & 0xFF
    return [word(image, at + ANIMATION_ARRAY + 4 * index) for index in range(count)]


def frame_count(image: bytes, record: int) -> int:
    return word(image, record - ROM_BASE) if record >= ROM_BASE else 0


def directions(image: bytes, record: int, frame: int) -> list[int]:
    at = record - ROM_BASE + 4 + 16 * frame
    return [word(image, at + 4 * direction) for direction in range(4)]


def _new_animation(out: bytearray, image: bytes, donor_record: int, wanted: int) -> int:
    """Append an animation record with `wanted` frames cycled from the donor's own frames."""
    donor_frames = frame_count(image, donor_record)
    if donor_frames <= 0:
        raise DefinitionCopyError("a donor animation with no frames cannot be cycled")
    while len(out) % 4:
        out.append(0x00)
    address = ROM_BASE + len(out)
    out += wanted.to_bytes(4, "little")
    for frame in range(wanted):
        for direction in directions(image, donor_record, frame % donor_frames):
            out += direction.to_bytes(4, "little")
    return address


def _closest_donor(donor_slots: list[int], image: bytes, wanted: int) -> tuple[int, int]:
    """The donor animation whose frame count is closest to `wanted`; ties go to the lowest slot."""
    choices = [(abs(frame_count(image, record) - wanted), index, record)
               for index, record in enumerate(donor_slots) if record >= ROM_BASE]
    if not choices:
        raise DefinitionCopyError("the donor definition has no animations to stand in with")
    _distance, index, record = min(choices)
    return index, record


def build_copy(image: bytes, target_id: int, donor_id: int,
               extra_slots: tuple[int, ...] = ()) -> tuple[bytes, dict]:
    """Append a definition for `target_id` that shows `donor_id` art in every needed slot."""
    donor_at = definition_offset(image, donor_id)
    donor_slots = slots_of(image, donor_id)
    target_slots = slots_of(image, target_id)
    count = max(len(donor_slots), len(target_slots), (max(extra_slots) + 1) if extra_slots else 0)

    out = bytearray(image)
    while len(out) % 4:
        out.append(0x00)
    copy_at = len(out)
    header = bytearray(image[donor_at:donor_at + HEADER_BYTES])
    header[0] = count & 0xFF
    out += header
    array_at = len(out)
    out += bytes(4 * count)

    filled: list[dict] = []
    for index in range(count):
        donor_record = donor_slots[index] if index < len(donor_slots) else 0
        target_record = target_slots[index] if index < len(target_slots) else 0
        target_frames = frame_count(image, target_record)
        donor_frames = frame_count(image, donor_record)
        chosen = donor_record
        reason = "donor slot kept"
        donor_source = index
        if donor_record >= ROM_BASE and target_frames > donor_frames:
            chosen = _new_animation(out, image, donor_record, target_frames)
            reason = f"padded from slot {index} ({donor_frames} frames) to the target's {target_frames}"
        elif donor_record < ROM_BASE and target_record >= ROM_BASE:
            donor_source, source_record = _closest_donor(donor_slots, image, target_frames)
            chosen = _new_animation(out, image, source_record, target_frames)
            reason = (f"donor slot {index} is empty; built {target_frames} frame(s) from donor slot "
                      f"{donor_source} as a stand-in pose")
        if chosen >= ROM_BASE:
            out[array_at + 4 * index:array_at + 4 * index + 4] = chosen.to_bytes(4, "little")
            filled.append({"slot": index, "record": f"0x{chosen:08X}",
                           "target_frames": target_frames, "donor_frames": donor_frames,
                           "donor_slot_used": donor_source, "reason": reason})
    for index in extra_slots:
        if index < count:
            continue
        raise DefinitionCopyError(f"extra slot {index} is outside the copy's {count} slots")

    entry = CHARACTER_TABLE + 4 * target_id
    previous = word(image, entry)
    out[entry:entry + 4] = (ROM_BASE + copy_at).to_bytes(4, "little")
    proof = {"target_id": target_id, "donor_id": donor_id,
             "copy_file": copy_at, "copy_bytes": len(out) - copy_at,
             "count": count, "entry_file": entry,
             "previous_definition": f"0x{previous:08X}",
             "new_definition": f"0x{ROM_BASE + copy_at:08X}",
             "target_occupied": [index for index, record in enumerate(target_slots)
                                 if record >= ROM_BASE],
             "filled": filled}
    # Every slot the target's own definition occupied must be non-empty in the copy, and no slot the
    # target used may be left null: that is the property the borrowed definition broke.
    copy_slots = [word(bytes(out), array_at + 4 * index) for index in range(count)]
    missing = [index for index, record in enumerate(target_slots)
               if record >= ROM_BASE and copy_slots[index] < ROM_BASE]
    if missing:
        raise DefinitionCopyError(f"the copy leaves slots {missing} empty that the target filled")
    proof["copy_occupied"] = [index for index, record in enumerate(copy_slots) if record >= ROM_BASE]
    return bytes(out), proof
