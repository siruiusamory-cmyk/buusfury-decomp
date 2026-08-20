import pytest

from tools.webfoot.binary import BinaryAddressError, GBA_ROM_BASE, GbaRomAddress


def test_gba_rom_address_converts_to_file_offset():
    address = GbaRomAddress(GBA_ROM_BASE + 0x1234)

    assert address.to_file_offset(0x2000) == 0x1234


def test_gba_rom_address_can_represent_null_without_converting_it():
    address = GbaRomAddress(0)

    assert address.is_null
    with pytest.raises(BinaryAddressError, match="not an address"):
        address.to_file_offset(0x100)


def test_gba_rom_address_rejects_end_by_default():
    address = GbaRomAddress(GBA_ROM_BASE + 0x100)

    with pytest.raises(BinaryAddressError, match="outside"):
        address.to_file_offset(0x100)
    assert address.to_file_offset(0x100, allow_end=True) == 0x100


@pytest.mark.parametrize("value", [-1, 0x1_0000_0000, True])
def test_gba_rom_address_rejects_non_u32_values(value):
    with pytest.raises(BinaryAddressError, match="32-bit unsigned"):
        GbaRomAddress(value)
