import pytest

from tools.runtime.rom006_gdb_probe import (
    MAP_ENTRY_BASE,
    MAP_ENTRY_SIZE,
    RspClient,
    decode_register_payload,
    effective_variation_source,
    level3_capture_is_valid,
    map_entry_address,
    rsp_packet,
    selector_from_scaled_r1,
)


def test_rsp_packet_encodes_ascii_payload_and_checksum():
    assert rsp_packet("g") == b"$g#67"
    assert rsp_packet("Z0,80089d4,2") == b"$Z0,80089d4,2#b5"


def test_register_payload_decodes_seventeen_little_endian_words():
    expected = tuple(range(17))
    payload = b"".join(value.to_bytes(4, "little") for value in expected).hex()

    assert decode_register_payload(payload) == expected


@pytest.mark.parametrize("payload", ["", "00" * 67, "zz" * 68])
def test_register_payload_rejects_wrong_width_or_non_hex(payload):
    with pytest.raises(ValueError, match="register payload"):
        decode_register_payload(payload)


@pytest.mark.parametrize(
    "command",
    ["?", "qSupported", "g", "s", "c", "Z0,80089d4,2", "z0,80089d4,2"],
)
def test_rsp_allowlist_accepts_only_probe_operations(command):
    assert RspClient.command_is_allowed(command)


@pytest.mark.parametrize(
    "command",
    ["M2000000,4:00000000", "X2000000,4:xxxx", "G00", "P0=00", "Z3,8000000,4"],
)
def test_rsp_allowlist_rejects_memory_and_register_writes(command):
    assert not RspClient.command_is_allowed(command)


def test_runtime_address_and_selector_helpers_reconstruct_capture():
    assert effective_variation_source(0x08072898) == 0x080728D4
    assert selector_from_scaled_r1(4) == 1
    assert map_entry_address(1) == MAP_ENTRY_BASE + MAP_ENTRY_SIZE


def test_level3_validator_requires_linked_thumb_entry_and_exact_post_step():
    entry = [0] * 17
    entry[0] = map_entry_address(1)
    entry[1] = 1
    entry[15] = 0x080089CC
    entry[16] = 0x20
    load = entry.copy()
    load[0] = 0x08072898
    load[1] = 4
    load[15] = 0x080089D4
    after = load.copy()
    after[0] = 0x082B5FA0
    after[15] = 0x080089D6

    assert level3_capture_is_valid(
        entry_registers=entry,
        load_registers=load,
        after_registers=after,
        expected_entry_address=0x0808E318,
        expected_source=0x080728D4,
        expected_first_word=0x082B5FA0,
    )

    after[15] = 0x080089D8
    assert not level3_capture_is_valid(
        entry_registers=entry,
        load_registers=load,
        after_registers=after,
        expected_entry_address=0x0808E318,
        expected_source=0x080728D4,
        expected_first_word=0x082B5FA0,
    )


@pytest.mark.parametrize("value", [-1, 0x1_0000_0000, True, "1"])
def test_map_entry_address_rejects_invalid_indices(value):
    with pytest.raises(ValueError, match="MapEntry index"):
        map_entry_address(value)


@pytest.mark.parametrize("value", [-1, 0x1_0000_0000])
def test_effective_source_rejects_non_u32(value):
    with pytest.raises(ValueError, match="unsigned 32-bit"):
        effective_variation_source(value)


@pytest.mark.parametrize("value", [-1, 3, 0x1_0000_0000])
def test_selector_helper_rejects_invalid_scaled_values(value):
    with pytest.raises(ValueError, match="selector|unsigned 32-bit"):
        selector_from_scaled_r1(value)
