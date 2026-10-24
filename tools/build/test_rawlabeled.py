import os
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))

import emitted  # noqa: E402
import gate  # noqa: E402
import rawlabeled  # noqa: E402


def require_rom():
    path = os.path.join(ROOT, "baserom.gba")
    if not os.path.exists(path):
        pytest.skip("%s is absent, so this ROM-gated test cannot run" % path)
    return open(path, "rb").read()


def test_named_slices_reads_one_token_per_slice_out_of_the_fragments(tmp_path):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "rawlabeled_0.s").write_text("\tINCBIN\tbaserom.gba_0x10_0x20.extracted\n")
    (asm / "rawlabeled_20.s").write_text("\tEXPORT\t|unk_08000020|\n|unk_08000020|\n"
                                         "\tINCBIN\tbaserom.gba_0x20_0x28.extracted\n")
    (asm / "loc_0.s").write_text("\tINCBIN\tbuild\\jcalg1\\gen_10.bin\n")
    (asm / "notes.txt").write_text("\tINCBIN\tbaserom.gba_0x30_0x38.extracted\n")
    assert rawlabeled.named_slices(str(tmp_path)) == {
        (0x10, 0x20): "baserom.gba_0x10_0x20.extracted",
        (0x20, 0x28): "baserom.gba_0x20_0x28.extracted"}


def test_extract_writes_every_slice_a_fragment_names_and_rewrites_none(tmp_path, capsys):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "rawlabeled_0.s").write_text("\tINCBIN\tbaserom.gba_0x0_0x4.extracted\n")
    rom = b"\x01\x02\x03\x04\x05\x06"
    assert rawlabeled.extract(rom, str(tmp_path)) == 0
    assert (tmp_path / "baserom.gba_0x0_0x4.extracted").read_bytes() == rom[0:4]
    assert capsys.readouterr().out.strip() == "slices named=1 written=1 bytes=4"
    (tmp_path / "baserom.gba_0x0_0x4.extracted").write_bytes(b"\x00" * 4)
    assert rawlabeled.extract(rom, str(tmp_path)) == 0
    assert (tmp_path / "baserom.gba_0x0_0x4.extracted").read_bytes() == rom[0:4]
    assert capsys.readouterr().out.strip() == "slices named=1 written=1 bytes=4"
    assert rawlabeled.extract(rom, str(tmp_path)) == 0
    assert capsys.readouterr().out.strip() == "slices named=1 written=0 bytes=4"


def test_a_slice_outside_the_image_is_refused(tmp_path):
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "rawlabeled_0.s").write_text("\tINCBIN\tbaserom.gba_0x0_0x10.extracted\n")
    with pytest.raises(SystemExit):
        rawlabeled.extract(b"\x00\x01", str(tmp_path))


def test_citation_rows_reports_both_raw_labeled_runs():
    rom = require_rom()
    assert rawlabeled.citation_rows(rom) == [
        ("0x74D248..0x74F058", 0x1E10, 22, 77),
        ("0x7B5B64..0x7B79A4", 0x1E40, 26, 91)]


def test_no_two_rows_of_the_tree_are_the_same_slice():
    require_rom()
    slices = gate.incbin_ranges()
    assert len(slices) == len(set(slices)), "a slice is named twice in asm/*.s"
    assert sum(length for _, length in slices) == gate.raw_classes()[0]


def test_fragment_symbols_reads_both_label_spellings_and_their_citations():
    bare = ("unk_0874d248\n"
            "        ; 4 ldr-literal site(s) load 0x0874D248 (0x080271EA): thumb\n"
            "\tINCBIN\tbaserom.gba_0x74d248_0x74d35c.extracted\n"
            "unk_0874d35c\n"
            "        ; no site names 0x0874D35C; the census's region boundary, not a cited address\n"
            "\tINCBIN\tbaserom.gba_0x74d35c_0x74d360.extracted\n")
    assert emitted.fragment_symbols(bare) == [
        (0x74D248, 0x74D35C, "baserom.gba_0x74d248_0x74d35c.extracted", True),
        (0x74D35C, 0x74D360, "baserom.gba_0x74d35c_0x74d360.extracted", False)]
    piped = ("\tEXPORT\t|unk_0874D248|\n"
             "|unk_0874D248|\n"
             "; no citation: a data-stated boundary (--boundaries)\n"
             "\tINCBIN\tbaserom.gba_0x74d248_0x74d35c.extracted\n")
    assert emitted.fragment_symbols(piped) == [
        (0x74D248, 0x74D35C, "baserom.gba_0x74d248_0x74d35c.extracted", False)]
    assert emitted.labeled_bytes(bare) == []


def test_the_reader_sees_both_raw_label_spellings():
    bare = "unk_0874d248\n        ; a comment between the data lines\n        DCB     0x4c,0x1c\n" \
           "unk_0874d24a\n        DCB     0x00,0x03\n"
    assert emitted.labeled_bytes(bare) == [(0x74D248, b"\x4c\x1c"),
                                           (0x74D24A, b"\x00\x03")]
    piped = "|unk_0874D248|\n\tDCB\t0x4c,0x1c\n"
    assert emitted.labeled_bytes(piped) == [(0x74D248, b"\x4c\x1c")]
    wide = "|unk_0874D248|\n\tDCD\t0x1c4c4b4a,0x0300001c\n"
    assert emitted.labeled_bytes(wide) == [
        (0x74D248, b"\x4a\x4b\x4c\x1c\x1c\x00\x00\x03")], emitted.labeled_bytes(wide)
    rows = emitted.labeled_rows(bare)
    assert rows == [(0x74D248, 0x74D24C, b"\x4c\x1c\x00\x03")], rows


def test_a_generated_run_with_one_address_takes_its_end_from_the_next_token():
    rom = bytes((index * 7) & 0xFF for index in range(0x80))
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "build", "jcalg1"))
    open(os.path.join(root, "build", "jcalg1", "gen_20.bin"), "wb").write(rom[0x20:0x40])
    open(os.path.join(root, "baserom.gba_0x40_0x60.extracted"), "wb").write(rom[0x40:0x60])
    text = ("        INCBIN  build\\jcalg1\\gen_20.bin\n"
            "        INCBIN  baserom.gba_0x40_0x60.extracted\n")
    rows, problems = emitted.source_rows(root, rom, text)
    assert problems == []
    assert [(low, high) for low, high, _, _ in rows] == [(0x20, 0x40), (0x40, 0x60)], rows
