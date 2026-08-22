from __future__ import annotations

import struct

import pytest

from tools.mgba_probe.runtime import ReadEvent
from tools.runtime.rom008_object_trace import MANAGER
import tools.runtime.rom012_live_containment as rom012
from tools.runtime.rom012_live_containment import (
    CallbackTrace,
    FamilyObject,
    _action_outcome,
    _query_sample,
    _reconstruct_live_registry,
    _validate_native_event,
    _valid_descriptor_pointer,
    _valid_runtime_object_pointer,
    choose_nearest_target,
    direction_for_delta,
    movement_is_consistent,
    rectangle_delta,
)


class _MemoryClient:
    def __init__(self, chunks: dict[int, bytes]):
        self.memory: dict[int, int] = {}
        for address, data in chunks.items():
            self.memory.update(
                {address + offset: value for offset, value in enumerate(data)}
            )

    def allow_read(self, address: int, length: int) -> str:
        return f"m{address:x},{length:x}"

    def command(self, payload: str, timeout: float = 5.0) -> str:
        del timeout
        address_text, length_text = payload[1:].split(",")
        address = int(address_text, 16)
        length = int(length_text, 16)
        return bytes(self.memory[address + offset] for offset in range(length)).hex()


class _StepClient:
    def command(self, payload: str, timeout: float = 5.0) -> str:
        del timeout
        assert payload == "s"
        return "S05"


def _object(index: int, bounds: tuple[int, int, int, int]) -> FamilyObject:
    return FamilyObject(
        load_epoch=1,
        map_entry_address=0x0808EB68,
        map_entry_index=39,
        descriptor=0x08294948 + index * 0x20,
        object_pointer=0x0203DE7C + index * 0x18,
        registry_slot=MANAGER + 4 + index * 4,
        bounds=bounds,
    )


@pytest.mark.parametrize(
    ("point", "expected"),
    [
        ((172, 190), (420, 0)),
        ((592, 136), (0, 0)),
        ((600, 240), (0, 0)),
        ((601, 241), (-1, -1)),
        ((700, 100), (-100, 36)),
    ],
)
def test_rectangle_delta_uses_signed_half_open_bounds(point, expected):
    assert rectangle_delta(point, (592, 136, 601, 241)) == expected


def test_rectangle_delta_rejects_empty_rectangles():
    with pytest.raises(ValueError, match="non-empty"):
        rectangle_delta((0, 0), (1, 1, 1, 2))


def test_nearest_target_uses_distance_then_registry_order():
    farther = _object(1, (20, 0, 21, 1))
    nearest_later = _object(3, (10, 0, 11, 1))
    nearest_earlier = _object(2, (10, 0, 11, 1))

    target, delta = choose_nearest_target(
        (0, 0), [farther, nearest_later, nearest_earlier]
    )

    assert target == nearest_earlier
    assert delta == (10, 0)


def test_nearest_target_requires_a_factory_attributed_live_object():
    with pytest.raises(ValueError, match="no live"):
        choose_nearest_target((0, 0), [])


@pytest.mark.parametrize(
    ("direction", "delta", "expected"),
    [
        ("east", (4, 0), True),
        ("east", (-4, 0), False),
        ("west", (-4, 1), True),
        ("north", (1, -4), True),
        ("south", (0, 4), True),
        ("south", (5, 1), False),
    ],
)
def test_movement_correlation_requires_consistent_cardinal_motion(
    direction, delta, expected
):
    assert movement_is_consistent(direction, *delta) is expected


def test_movement_correlation_rejects_unknown_direction():
    with pytest.raises(ValueError, match="direction"):
        movement_is_consistent("sideways", 1, 0)


@pytest.mark.parametrize(
    ("delta", "expected"),
    [
        ((0, 0), "already inside"),
        ((5, 0), "east"),
        ((-5, -2), "north-west"),
        ((4, 3), "south-east"),
    ],
)
def test_direction_label(delta, expected):
    assert direction_for_delta(*delta) == expected


def test_family_object_preserves_factory_and_registry_identity():
    item = _object(7, (1, 2, 3, 4))

    data = item.to_dict()

    assert item.object_index == 7
    assert data["factory_raw"] == "0x08007675"
    assert data["object_index"] == 7
    assert data["bounds"] == [1, 2, 3, 4]


@pytest.mark.parametrize(
    ("pointer", "expected"),
    [
        (0x02000000, True),
        (0x02000002, False),
        (0x0203FFE8, True),
        (0x0203FFEC, False),
        (0x08000000, False),
    ],
)
def test_runtime_object_pointer_requires_aligned_complete_ewram_object(
    pointer, expected
):
    assert _valid_runtime_object_pointer(pointer) is expected


@pytest.mark.parametrize(
    ("pointer", "expected"),
    [
        (0x08000000, True),
        (0x08000002, False),
        (0x087FFFFC, True),
        (0x08800000, False),
        (0x02000000, False),
    ],
)
def test_descriptor_pointer_requires_aligned_word_inside_verified_rom(
    pointer, expected
):
    assert _valid_descriptor_pointer(pointer) is expected


def test_post_load_registry_reconstruction_uses_retained_descriptor_factory_chain():
    target_object = 0x02001000
    other_object = 0x02002000
    target_descriptor = 0x08200000
    other_descriptor = 0x08200020
    target_bytes = bytearray(0x18)
    struct.pack_into("<I", target_bytes, 0, 0x0804A09C)
    struct.pack_into("<hhhh", target_bytes, 4, 10, 20, 30, 40)
    struct.pack_into("<I", target_bytes, 0x0C, 0x02003000)
    struct.pack_into("<I", target_bytes, 0x14, target_descriptor)
    other_bytes = bytearray(0x18)
    struct.pack_into("<I", other_bytes, 0x14, other_descriptor)
    client = _MemoryClient(
        {
            MANAGER: struct.pack("<I", 3),
            MANAGER + 4: struct.pack(
                "<III", target_object, other_object, 0xDEADBEEF
            ),
            target_object: bytes(target_bytes),
            other_object: bytes(other_bytes),
            target_descriptor: struct.pack("<I", 0x08007675),
            other_descriptor: struct.pack("<I", 0x080072CD),
        }
    )

    entries, matches = _reconstruct_live_registry(
        client,
        map_entry_address=0x0808EB68,
        load_epoch=1,
    )

    assert len(entries) == 3
    assert entries[0]["factory_raw"] == "0x08007675"
    assert entries[1]["factory_matches_target"] is False
    assert entries[2]["object_pointer_valid"] is False
    assert len(matches) == 1
    assert matches[0].object_pointer == target_object
    assert matches[0].descriptor == target_descriptor
    assert matches[0].bounds == (10, 20, 30, 40)
    assert matches[0].callback_reference_raw == 0x02003000
    assert matches[0].object_dispatch_base_raw == 0x0804A09C


def test_query_sample_uses_callee_saved_entry_entity_from_r5():
    entity = 0x02010000
    client = _MemoryClient(
        {
            entity + 0x1A0: (172 << 8).to_bytes(4, "little", signed=True),
            entity + 0x1A4: (190 << 8).to_bytes(4, "little", signed=True),
        }
    )
    registers = [0] * 17
    registers[1] = 172
    registers[5] = entity

    sample = _query_sample(
        client,
        registers,
        load_epoch=1,
        object_pointer=0x02001000,
    )

    assert sample.entity == entity
    assert (sample.x, sample.y) == (172, 190)


def _native_event(target: FamilyObject, *, accepted: bool) -> ReadEvent:
    offset = 0x0C if accepted else 4
    width = 4 if accepted else 2
    address = target.object_pointer + offset
    return ReadEvent(
        event_id=1,
        control_sequence=3,
        target=target.object_pointer,
        load_epoch=target.load_epoch,
        descriptor=target.descriptor,
        factory_raw=0x08007675,
        factory_fetch=0x08007674,
        address=address,
        relative_offset=offset,
        access_width=width,
        overlap_start=address,
        overlap_end=address + width,
        instruction_pc=0x0801277A if accepted else 0x08012748,
        lr=0x080126F9,
        raw_r15=(0x0801277E if accepted else 0x0801274C),
        cpsr=0x3F,
        registers=tuple([0] * 16),
    )


@pytest.mark.parametrize("accepted", [False, True])
def test_native_event_validation_requires_exact_pc_address_width_and_identity(accepted):
    target = _object(0, (10, 20, 30, 40))
    event = _native_event(target, accepted=accepted)

    _validate_native_event(
        event,
        target=target,
        sequence=3,
        accepted=accepted,
    )

    wrong_width = ReadEvent(
        **{
            field: (1 if field == "access_width" else getattr(event, field))
            for field in ReadEvent.__dataclass_fields__
        }
    )
    with pytest.raises(RuntimeError, match="lost reconstructed"):
        _validate_native_event(
            wrong_width,
            target=target,
            sequence=3,
            accepted=accepted,
        )


def _registers_at(pc: int) -> list[int]:
    registers = [0] * 17
    registers[15] = pc
    registers[16] = 0x20
    return registers


def test_callback_trace_returns_completed_capture(monkeypatch):
    snapshots = iter([_registers_at(0x08020000), _registers_at(0x080127A0)])
    monkeypatch.setattr(rom012, "_registers", lambda client: next(snapshots))

    trace = rom012._trace_callback_without_breakpoint(
        _StepClient(),
        raw_target=0x08020001,
        return_pc=0x080127A0,
        max_steps=2,
    )

    assert trace.reached_target is True
    assert trace.returned_to_query is True
    assert trace.instruction_trace == ("0x08020000", "0x080127A0")


def test_callback_trace_retains_partial_capture_at_budget(monkeypatch):
    snapshots = iter([_registers_at(0x08020000), _registers_at(0x08020002)])
    monkeypatch.setattr(rom012, "_registers", lambda client: next(snapshots))

    trace = rom012._trace_callback_without_breakpoint(
        _StepClient(),
        raw_target=0x08020001,
        return_pc=0x080127A0,
        max_steps=2,
    )

    assert trace.reached_target is True
    assert trace.returned_to_query is False
    assert trace.instruction_trace == ("0x08020000", "0x08020002")


@pytest.mark.parametrize(
    ("reached_target", "returned_to_query", "expected"),
    [
        (False, False, "C"),
        (True, False, "B"),
        (True, True, "B"),
    ],
)
def test_action_outcome_depends_on_concrete_target_execution(
    reached_target, returned_to_query, expected
):
    trace = CallbackTrace((), tuple([0] * 17), reached_target, returned_to_query)

    result, _ = _action_outcome(trace)

    assert result == expected
