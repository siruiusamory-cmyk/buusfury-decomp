"""Project-build materialization for measured compressed-dialogue resources."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from .allocation import Allocation, AllocationRequest, allocate
from .binary import FileOffset
from .formats.webfoot_lz import pack, unpack
from .layout import AnchorId, OwnedRegion, RomRange
from .profile import RomProfile
from .write import (ByteChange, GeneratedAllocationProvenance, GeneratedImage,
                    WritePlan, plan_changes)


class CompressedDialogueError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CompressedDialogueTarget:
    """Measured immutable identity of one record inside one container."""

    name: str
    selector: int
    table_offset: int
    packed_handle: int
    decoded_start: int
    decoded_length: int


@dataclass(frozen=True, slots=True)
class CompressedDialogueBuild:
    target: CompressedDialogueTarget
    old_container_offset: int
    old_allocation: int
    payload: bytes
    allocation: Allocation | None
    changes: tuple[ByteChange, ...]
    generated_allocation: GeneratedAllocationProvenance | None
    plan: WritePlan | None = None


AUTHORED_DIALOGUE_TARGETS = {
    "goku-greeting": CompressedDialogueTarget(
        "goku-greeting", 1, 0x7B5B64, 0x02002641, 0x132, 0x20
    ),
}


def target_named(name: str) -> CompressedDialogueTarget:
    try:
        return AUTHORED_DIALOGUE_TARGETS[name]
    except KeyError as exc:
        raise CompressedDialogueError(f"unsupported authored dialogue target: {name}") from exc


def _prepare_replacement(canonical: bytes, profile: RomProfile,
                         target: CompressedDialogueTarget, replacement: str,
                         reserved: Iterable[RomRange]) -> CompressedDialogueBuild:
    if profile.generated_expansion is None:
        raise CompressedDialogueError("profile declares no verified generated expansion")
    if not replacement:
        raise CompressedDialogueError("replacement dialogue must not be empty")
    table_slot = target.table_offset + target.selector * 4
    if not 0 <= table_slot <= len(canonical) - 8:
        raise CompressedDialogueError("container-table slot lies outside canonical ROM")
    old_pointer = int.from_bytes(canonical[table_slot:table_slot + 4], "little")
    if old_pointer < 0x08000000:
        raise CompressedDialogueError("container-table slot is not a ROM pointer")
    old_offset = FileOffset(old_pointer - 0x08000000).value
    if old_offset >= len(canonical):
        raise CompressedDialogueError("container-table slot is not a canonical ROM pointer")
    container = unpack(canonical, old_offset)
    encoded = replacement.encode("utf-16le")
    if len(encoded) != target.decoded_length:
        raise CompressedDialogueError(
            f"{target.name}: replacement encodes to {len(encoded)} bytes; durable "
            f"handle requires exactly {target.decoded_length}"
        )
    end = target.decoded_start + target.decoded_length
    if end > len(container.data):
        raise CompressedDialogueError("durable handle range lies outside decoded container")
    payload = pack(container.data[:target.decoded_start] + encoded + container.data[end:])
    next_pointer = int.from_bytes(canonical[table_slot + 4:table_slot + 8], "little")
    if next_pointer < 0x08000000:
        raise CompressedDialogueError("following container table entry is not a ROM pointer")
    next_offset = FileOffset(next_pointer - 0x08000000).value
    old_allocation = next_offset - old_offset
    if next_offset <= old_offset or container.packed_end > next_offset:
        raise CompressedDialogueError("container table does not bound a valid retail allocation")
    owner = f"compressed-dialogue:{target.name}"
    if len(payload) <= old_allocation:
        padded = payload + canonical[old_offset + len(payload):old_offset + old_allocation]
        return CompressedDialogueBuild(
            target, old_offset, old_allocation, payload, None,
            (ByteChange(old_offset, canonical[old_offset:old_offset + old_allocation], padded,
                        owner, "rebuild fits measured retail allocation"),), None,
        )

    expansion = profile.generated_expansion
    request = AllocationRequest(AnchorId(owner), owner, len(payload), 4)
    allocation = allocate(
        profile, [request],
        occupied=tuple(OwnedRegion(span, "build reservation") for span in reserved),
        capacity_regions=(expansion.free_region(profile.size),), image_size=expansion.output_size,
    )[0]
    destination = allocation.range.start.value
    old = (canonical[destination:destination + len(payload)]
           if destination < len(canonical) else bytes([expansion.padding_byte]) * len(payload))
    image_size = expansion.output_size if destination >= profile.size else profile.size
    pointer = FileOffset(destination).to_gba_address(image_size).raw
    changes = (
        ByteChange(destination, old, payload, owner, "relocated compressed dialogue payload"),
        ByteChange(table_slot, canonical[table_slot:table_slot + 4], pointer.to_bytes(4, "little"),
                   owner, "selector container pointer to relocated resource"),
    )
    generated_allocation = None
    if destination >= profile.size:
        generated_allocation = GeneratedAllocationProvenance(
            domain="compressed_dialogue", resource=target.name, owner=owner,
            source_range=RomRange(FileOffset(old_offset), old_allocation),
            allocated_range=allocation.range, allocated_rom_address=pointer,
            pointer_offset=table_slot,
            expansion_evidence=allocation.free_region_evidence,
        )
    return CompressedDialogueBuild(target, old_offset, old_allocation, payload, allocation,
                                   changes, generated_allocation)


def materialize_dialogues(canonical: bytes, profile: RomProfile,
                          replacements: dict[str, str], reserved: Iterable[RomRange] = ()) -> tuple[
                              tuple[CompressedDialogueBuild, ...], tuple[RomRange, ...],
                              GeneratedImage | None, tuple[GeneratedAllocationProvenance, ...]]:
    """Plan dialogue as one ordinary build domain against passed reservations."""
    before = tuple(reserved)
    occupied = before
    results = []
    for name, replacement in sorted(replacements.items()):
        result = _prepare_replacement(canonical, profile, target_named(name), replacement, occupied)
        results.append(result)
        if result.allocation is not None:
            occupied += (result.allocation.range,)
    generated = tuple(r.generated_allocation for r in results if r.generated_allocation is not None)
    image = None
    if generated:
        assert profile.generated_expansion is not None
        image = profile.generated_expansion.generated_image(
            profile.size, tuple(item.allocated_range for item in generated)
        )
    return tuple(results), occupied[len(before):], image, generated


def plan_replacement(canonical: bytes, profile: RomProfile,
                     target: CompressedDialogueTarget, replacement: str) -> CompressedDialogueBuild:
    """Compatibility planner built from the production dialogue domain."""
    results, _, image, generated = materialize_dialogues(canonical, profile, {target.name: replacement})
    result = results[0]
    plan = plan_changes(canonical, result.changes, profile_id=profile.id,
                        base_sha256=profile.sha256, generated_image=image,
                        generated_allocations=generated)
    return replace(result, plan=plan)
