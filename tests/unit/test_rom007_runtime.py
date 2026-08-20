import pytest

from tools.runtime.rom007_factory_probe import (
    ACTIVE_MAP_POINTER_PACKET,
    ADAPTER_PC,
    MANAGER_PC,
    ExecutionTarget,
    FactoryCapture,
    Rom007RspClient,
    adapter_entry_is_valid,
    adapter_steps_are_valid,
    decode_read_u32,
    execution_target,
    factory_capture_is_valid,
    map_entry_index_from_address,
    manager_entry_is_valid,
    population_is_complete,
    registry_slot,
    validate_registry_insertion,
)
from tools.runtime.rom006_gdb_probe import MAP_ENTRY_BASE, MAP_ENTRY_SIZE


def test_map_entry_address_converts_to_canonical_index():
    assert map_entry_index_from_address(MAP_ENTRY_BASE + 39 * MAP_ENTRY_SIZE) == 39


@pytest.mark.parametrize(
    "address",
    [MAP_ENTRY_BASE - 1, MAP_ENTRY_BASE + 1, MAP_ENTRY_BASE + 452 * MAP_ENTRY_SIZE],
)
def test_map_entry_address_rejects_outside_or_unaligned(address):
    with pytest.raises(ValueError, match="MapEntry address"):
        map_entry_index_from_address(address)


def test_execution_target_preserves_raw_thumb_bit():
    target = execution_target(0x08007675)
    assert target == ExecutionTarget(0x08007675, "Thumb", 0x08007674)
    assert execution_target(0x08007674) == ExecutionTarget(
        0x08007674, "ARM", 0x08007674
    )


@pytest.mark.parametrize("raw", [-1, 0x1_0000_0000, True, "0x08007675"])
def test_execution_target_rejects_non_u32(raw):
    with pytest.raises(ValueError, match="raw 32-bit"):
        execution_target(raw)


def test_active_map_memory_response_decodes_little_endian_u32():
    assert decode_read_u32("68eb0808") == 0x0808EB68


@pytest.mark.parametrize("payload", ["", "00", "0000000000", "gggggggg"])
def test_active_map_memory_response_rejects_malformed_payload(payload):
    with pytest.raises(ValueError, match="u32 memory response"):
        decode_read_u32(payload)


def test_rom007_rsp_allowlist_adds_only_exact_active_map_read():
    assert Rom007RspClient.command_is_allowed(ACTIVE_MAP_POINTER_PACKET)
    assert Rom007RspClient.command_is_allowed("g")
    assert not Rom007RspClient.command_is_allowed("m3001984,4")
    assert not Rom007RspClient.command_is_allowed("M3001980,4:00000000")


def test_registry_slot_uses_count_followed_by_pointer_array():
    assert registry_slot(0x03002A64, 0) == 0x03002A68
    assert registry_slot(0x03002A64, 1) == 0x03002A6C


def test_factory_capture_validator_fails_closed_on_target_or_slot_mismatch():
    valid = FactoryCapture(
        descriptor=0x08294948,
        target=execution_target(0x08007675),
        returned_object=0x0203DEBC,
        registry_slot=0x03002A68,
        old_count=0,
        new_count=1,
    )
    assert factory_capture_is_valid(
        valid,
        expected_descriptor=0x08294948,
        expected_raw_target=0x08007675,
        expected_object=0x0203DEBC,
        manager=0x03002A64,
        old_count=0,
    )
    assert not factory_capture_is_valid(
        valid,
        expected_descriptor=0x08294948,
        expected_raw_target=0x080072CD,
        expected_object=0x0203DEBC,
        manager=0x03002A64,
        old_count=0,
    )


def test_registry_insertion_validator_links_count_slot_object_and_manager():
    steps = []
    for pc in (0x0801267A, 0x0801267C, 0x0801267E, 0x08012680, 0x08012682, 0x08012684):
        registers = [0] * 17
        registers[0] = 0x0203DEBC
        registers[5] = 0x03002A64
        registers[15] = pc
        steps.append(registers)
    steps[0][1] = 0
    steps[1][2] = 1
    steps[3][1] = 0x03002A64

    assert validate_registry_insertion(
        steps, manager=0x03002A64, returned_object=0x0203DEBC
    ) == (0, 1, 0x03002A68)

    steps[1][2] = 2
    with pytest.raises(ValueError, match="increment"):
        validate_registry_insertion(
            steps, manager=0x03002A64, returned_object=0x0203DEBC
        )


def test_adapter_and_manager_provenance_checks_fail_closed():
    adapter = [0] * 17
    adapter[1] = 0x08294968
    adapter[14] = 0x08008AC7
    adapter[15] = ADAPTER_PC
    adapter[16] = 0x20
    assert adapter_entry_is_valid(adapter, 0x08294968)
    adapter[14] = 0x08008BC9
    assert not adapter_entry_is_valid(adapter, 0x08294968)

    adapter_steps = []
    for pc in (0x08009672, 0x08009674, 0x08009676, 0x08009678, 0x0800967A):
        step = [0] * 17
        step[15] = pc
        step[16] = 0x20
        adapter_steps.append(step)
    assert adapter_steps_are_valid(adapter_steps)
    adapter_steps[-1][15] = 0x0800967C
    assert not adapter_steps_are_valid(adapter_steps)

    manager = [0] * 17
    manager[0] = 0x03002A64
    manager[1] = 2
    manager[2] = 0x08294960
    manager[15] = MANAGER_PC
    manager[16] = 0x20
    assert manager_entry_is_valid(
        manager, manager=0x03002A64, count=2, array_base=0x08294960
    )
    manager[2] = 0x08294964
    assert not manager_entry_is_valid(
        manager, manager=0x03002A64, count=2, array_base=0x08294960
    )


def test_population_requires_every_adapter_declared_factory():
    capture = FactoryCapture(
        descriptor=0x08294948,
        target=execution_target(0x08007675),
        returned_object=0x0203DEBC,
        registry_slot=0x03002A68,
        old_count=0,
        new_count=1,
    )
    assert population_is_complete(1, [capture])
    assert not population_is_complete(2, [capture])
    assert not population_is_complete(None, [capture])
