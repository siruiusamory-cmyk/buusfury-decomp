import struct

from tools.research import consumer_search as search


def image_with(pointer_at, target, thumb_at=None, thumb_literal=None):
    image = bytearray(0x400)
    struct.pack_into("<I", image, pointer_at, search.ROM_BASE + target)
    if thumb_at is not None and thumb_literal is not None:
        immediate = (thumb_literal - ((thumb_at + 4) & ~3)) // 4
        struct.pack_into("<H", image, thumb_at, 0x4800 | immediate)
        struct.pack_into("<I", image, thumb_literal, search.ROM_BASE + target)
    return bytes(image)


def test_a_code_literal_and_a_data_word_are_both_sites_and_only_one_is_a_load():
    image = image_with(0x200, 0x300, thumb_at=0x100, thumb_literal=0x10C)
    code = [(0x100, 0x20, "thumb", "synthetic")]
    assert search.sites(image, [(0x300, 0x304)]) == [(0x10C, 0x300), (0x200, 0x300)]
    assert search.literal_loads(image, code, [(0x300, 0x304)]) == [(0x100, 0x10C, 0x300)]
    code_index = search._index([(0x100, 0x120)])
    assert search.classify(0x10C, code_index, search._index([])) == "code"
    assert search.classify(0x200, code_index, search._index([])) == "data"
    assert search.classify(0x10C, search._index([]), search._index([(0x100, 0x120)])) == "incbin"


def test_the_literal_address_is_never_tested_against_the_range():
    image = bytearray(image_with(0x200, 0x300, thumb_at=0x100, thumb_literal=0x10C))
    struct.pack_into("<I", image, 0x200, search.ROM_BASE + 0x10C)
    code = [(0x100, 0x20, "thumb", "synthetic")]
    assert search.sites(bytes(image), [(0x10C, 0x110)]) == [(0x200, 0x10C)]
    assert search.literal_loads(bytes(image), code, [(0x10C, 0x110)]) == []


def test_an_arm_literal_load_is_decoded_too():
    image = bytearray(0x400)
    struct.pack_into("<I", image, 0x100, 0xE59F1004)
    struct.pack_into("<I", image, 0x10C, search.ROM_BASE + 0x300)
    assert search.literal_loads(image, [(0x100, 0x40, "arm", "synthetic")],
                               [(0x300, 0x304)]) == [(0x100, 0x10C, 0x300)]


def test_ledger_rows_split_the_code_rows_from_the_data_rows(tmp_path):
    ledger = tmp_path / "ledger.csv"
    ledger.write_text("0x158,82586,thumb,code_158_143F2,asm/buu.s,transcription,byte-proven,1\n"
                      "0x71c90,3300,data,structured_run_71c90,asm/rest_of_the_game.s,generated,"
                      "byte-proven,0\n")
    rows, code = search.ledger_rows(str(ledger))
    assert len(rows) == 2
    assert code == [(0x158, 82586, "thumb", "code_158_143F2")]
