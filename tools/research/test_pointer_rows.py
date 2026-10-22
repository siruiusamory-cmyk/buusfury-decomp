import pytest

from tools import emitted
from tools.research import pointer_rows as P

RAM = "|unk_03003898|"


def names(**overrides):
    labels = {0x08000100: ("inc_0x100_0x110", "buu.s"), 0x08000204: ("sub_08000204", "buu.s")}
    labels.update(overrides.get("labels", {}))
    return (labels,
            overrides.get("exported", {"inc_0x100_0x110", "sub_08000204"}),
            {"buu.s": "buu.s", "fragment.s": "rest_of_the_game.s"},
            overrides.get("symbols", {0x08000300: {"lut_fx_green0"}}))


def test_the_reader_resolves_the_operand_forms_the_emitter_writes():
    assert emitted.operand_value("0x08070140") == 0x08070140
    assert emitted.operand_value("|unk_03003898|") == 0x03003898
    assert emitted.operand_value("|sub_0803E44C|+1") == 0x0803E44D
    assert emitted.operand_value("|inc_0x0701fa_0x071758|") is None


def test_a_slice_start_a_label_and_a_ram_address_each_name_a_word():
    known = names()
    assert P.spelling(0x08000100, "buu.s", known, 0x800000)[0] == "|inc_0x100_0x110|"
    assert P.spelling(0x08000205, "buu.s", known, 0x800000)[0] == "|sub_08000204|+1"
    assert P.spelling(0x03003898, "buu.s", known, 0x800000)[0] == RAM


def test_a_word_named_only_by_a_derived_name_is_not_resolved():
    known = names(symbols={0x08000300: {"map_record_run_190d24_root_record"}})
    operand, why = P.spelling(0x08000300, "buu.s", known, 0x800000)
    assert operand is None and "carries no address" in why


def test_a_label_another_unit_does_not_export_is_not_resolved():
    known = names(exported=set())
    operand, why = P.spelling(0x08000100, "rest_of_the_game.s", known, 0x800000)
    assert operand is None and "does not export" in why


def test_a_row_with_a_byte_outside_its_grid_words_is_not_converted():
    row = (0x100, 0x10E, "fragment.s", 1)
    words = [(0x100, 0x03003898, RAM, "ram"), (0x104, 0x03003898, RAM, "ram")]
    converted, reason = P.verdict(row, words, [])
    assert not converted and "outside the grid words" in reason


def test_a_row_inside_a_generated_fragment_is_listed_rather_than_converted():
    row = (0x100, 0x108, P.GENERATED[0], 1)
    words = [(0x100, 0x03003898, RAM, "ram"), (0x104, 0x03003898, RAM, "ram")]
    converted, reason = P.verdict(row, words, [])
    assert not converted and "citation_check" in reason


def test_the_dcd_block_reads_back_to_the_retail_row():
    row = bytes.fromhex("9838000398380003")
    text = "|unk_08000100|\n\tDCD\t|unk_03003898|\n\tDCD\t|unk_03003898|\n"
    assert dict(emitted.labeled_bytes(text)) == {0x100: row}
    assert b"".join(P.operand_bytes(operand) for operand in (RAM, RAM)) == row


def test_a_root_without_the_linker_symbols_is_refused_rather_than_read_as_unresolved(tmp_path):
    (tmp_path / "asm").mkdir()
    with pytest.raises(SystemExit):
        P.index(str(tmp_path))
    symbols = tmp_path / "build" / "output" / "symbols.json"
    symbols.parent.mkdir(parents=True)
    symbols.write_text('{"symbols": [{"address": "0x08000300", "name": "lut_fx_green0"}]}')
    assert P.index(str(tmp_path))[3] == {0x08000300: {"lut_fx_green0"}}


def test_apply_rewrites_the_token_and_a_second_run_reports_no_edit(tmp_path, monkeypatch):
    image = bytearray(0x800000)
    image[0x100:0x108] = bytes.fromhex("9838000398380003")
    carrier = tmp_path / "asm" / "fragment.s"
    carrier.parent.mkdir()
    carrier.write_text("|unk_08000100|\n\tINCBIN\tbaserom.gba_0x100_0x108.extracted\n")
    record = tmp_path / "rows.csv"
    record.write_text("row_start,row_end,row_file,row_line,word,value,operand,kind,row_verdict,"
                      "row_reason\n"
                      "0x000100,0x000108,fragment.s,2,0x000100,0x03003898,|unk_03003898|,ram,yes,ok\n"
                      "0x000100,0x000108,fragment.s,2,0x000104,0x03003898,|unk_03003898|,ram,yes,ok\n")
    monkeypatch.setattr(P, "RECORD", str(record))
    report = P.table(bytes(image), names())
    assert P.apply(str(tmp_path), bytes(image), report) == (1, 8)
    assert "DCD\t|unk_03003898|" in carrier.read_text()
    assert P.apply(str(tmp_path), bytes(image), report) == (0, 0)


def test_a_pool_row_with_a_zero_pad_carries_the_pad_and_an_unnamed_word(tmp_path, monkeypatch):
    image = bytearray(0x800000)
    image[0x10E:0x118] = bytes.fromhex("0000ffff0508" + "98380003")
    carrier = tmp_path / "asm" / "fragment.s"
    carrier.parent.mkdir()
    carrier.write_text("|unk_0800010E|\n\tINCBIN\tbaserom.gba_0x10e_0x118.extracted\n")
    record = tmp_path / "rows.csv"
    record.write_text("row_start,row_end,row_file,row_line,word,value,operand,kind,row_verdict,"
                      "row_reason\n"
                      "0x00010E,0x000118,fragment.s,2,0x000110,0x0805FFFF,,unresolved,no,off-grid\n"
                      "0x00010E,0x000118,fragment.s,2,0x000114,0x03003898,|unk_03003898|,ram,no,off-grid\n")
    monkeypatch.setattr(P, "RECORD", str(record))
    report = P.table(bytes(image), names())
    assert report[0]["row_verdict"] == "yes"
    assert "literal pool" in report[0]["row_reason"]
    assert P.apply(str(tmp_path), bytes(image), report) == (1, 10)
    text = carrier.read_text()
    assert "DCB\t0x00,0x00" in text and "DCD\t0x0805FFFF" in text
    assert dict(emitted.labeled_bytes(text)) == {0x10E: bytes(image[0x10E:0x118])}


def test_a_measured_pointer_array_with_unlabelled_targets_is_emitted_as_addresses(tmp_path,
                                                                                  monkeypatch):
    image = bytearray(0x800000)
    image[0x6B8028:0x6B8034] = bytes.fromhex("ac7f6b083c7f6b08d87e6b08")
    carrier = tmp_path / "asm" / "fragment.s"
    carrier.parent.mkdir()
    carrier.write_text("|unk_086B8028|\n\tINCBIN\tbaserom.gba_0x6b8028_0x6b8034.extracted\n")
    record = tmp_path / "rows.csv"
    record.write_text("row_start,row_end,row_file,row_line,word,value,operand,kind,row_verdict,"
                      "row_reason\n"
                      "0x6B8028,0x6B8034,fragment.s,2,0x6B8028,0x086B7FAC,,unresolved,no,x\n"
                      "0x6B8028,0x6B8034,fragment.s,2,0x6B802C,0x086B7F3C,,unresolved,no,x\n"
                      "0x6B8028,0x6B8034,fragment.s,2,0x6B8030,0x086B7ED8,,unresolved,no,x\n")
    monkeypatch.setattr(P, "RECORD", str(record))
    report = P.table(bytes(image), names())
    assert report[0]["row_verdict"] == "yes"
    assert report[0]["operand"] == "0x086B7FAC"
    assert "cmp r4,#3" in report[0]["row_reason"]
    assert P.apply(str(tmp_path), bytes(image), report) == (1, 12)
    assert dict(emitted.labeled_bytes(carrier.read_text())) == {
        0x6B8028: bytes(image[0x6B8028:0x6B8034])}


def test_a_word_defined_in_another_unit_is_imported_into_the_carrier_unit(tmp_path, monkeypatch):
    image = bytearray(0x800000)
    image[0x100:0x108] = bytes.fromhex("0402000804020008")
    asm = tmp_path / "asm"
    asm.mkdir()
    (asm / "buu.s").write_text("\tINCLUDE middle.s\n")
    (asm / "middle.s").write_text("\tINCLUDE fragment.s\n")
    (asm / "fragment.s").write_text("|unk_08000100|\n\tINCBIN\tbaserom.gba_0x100_0x108.extracted\n")
    (asm / "GBARam.s").write_text("|sub_08000204|\n")
    record = tmp_path / "rows.csv"
    record.write_text("row_start,row_end,row_file,row_line,word,value,operand,kind,row_verdict,"
                      "row_reason\n"
                      "0x000100,0x000108,fragment.s,2,0x000100,0x08000204,|sub_08000204|,label,"
                      "yes,ok\n"
                      "0x000100,0x000108,fragment.s,2,0x000104,0x08000204,|sub_08000204|,label,"
                      "yes,ok\n")
    monkeypatch.setattr(P, "RECORD", str(record))
    known = names(labels={0x08000100: ("inc_0x100_0x110", "GBARam.s")})
    report = P.table(bytes(image), known)
    assert P.declarations(str(tmp_path), report) == {"buu.s": (["        IMPORT |sub_08000204|"],
                                                              [])}
    assert P.apply(str(tmp_path), bytes(image), report) == (1, 8)
    assert "IMPORT |sub_08000204|" in (asm / "buu.s").read_text()
    assert P.declarations(str(tmp_path), report) == {}
