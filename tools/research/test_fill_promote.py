import pytest

from tools import emitted
from tools.research import fill_promote as F


def image_with_fill(value=0x00, length=326, before=8, after=5):
    return bytes(range(before)) + bytes([value]) * length + bytes(range(100, 100 + after))


def test_the_emitted_block_reads_back_to_the_retail_run():
    image = image_with_fill()
    run = {"start": 8, "length": 326, "value": 0x00}
    text = F.block(run)
    assert F.read_back(text) == image[8:8 + 326]


def test_a_nineteen_page_fill_reads_back_at_its_own_length():
    image = image_with_fill(value=0x00, length=1032)
    run = {"start": 8, "length": 1032, "value": 0x00}
    assert F.read_back(F.block(run)) == image[8:8 + 1032]


def test_the_source_reader_reads_the_same_run_the_assembler_fills():
    run = {"start": 0x75A0E9, "length": 326, "value": 0x00}
    assert dict(emitted.labeled_bytes(F.block(run))) == {0x75A0E9: bytes(326)}


def test_a_non_zero_run_is_refused_because_space_writes_zeroes():
    with pytest.raises(F.FillError):
        F.block({"start": 8, "length": 326, "value": 0xFF})
    with pytest.raises(F.FillError):
        F.verify(image_with_fill(value=0xFF), {"start": 8, "length": 326, "value": 0xFF})


def test_the_read_back_refuses_a_block_that_is_not_the_fill_shape():
    with pytest.raises(ValueError):
        F.read_back("\tDCB\t0x00\n")
    with pytest.raises(ValueError):
        F.read_back("|unk_0875A0E9|\n\t\tSPACE\t326\n\t\tSPACE\t326\n")


def test_a_perturbed_run_is_refused_by_verify():
    image = bytearray(image_with_fill())
    image[200] = 0x01
    with pytest.raises(F.FillError):
        F.verify(bytes(image), {"start": 8, "length": 326, "value": 0x00})


def test_plan_keeps_only_runs_of_the_minimum_length_and_splits_at_span_ends():
    image = bytes([0x00] * 300) + bytes([0x11]) + bytes([0x00] * 300)
    spans = [(0, 301), (301, 601)]
    runs = F.plan(image, spans, minimum=F.MIN_FILL)
    assert [(r["start"], r["length"], r["value"]) for r in runs] == [(0, 300, 0), (301, 300, 0)]


def test_plan_merges_spans_that_touch_so_a_run_across_two_slices_is_one_fill():
    image = bytes([0x00] * 400)
    runs = F.plan(image, [(0, 200), (200, 400)], minimum=F.MIN_FILL)
    assert [(r["start"], r["length"]) for r in runs] == [(0, 400)]


SOURCE = """\tCODE16
\tINCBIN\tbaserom.gba_0x1000_0x2000.extracted
\tINCBIN\tbaserom.gba_0x2000_0x3000.extracted
\tEND
"""


def splice_a_fill(monkeypatch=None):
    return F.splice(SOURCE, (0x1000, 0x2000), [{"start": 0x1800, "length": 0x100, "value": 0x00}])


def test_splice_puts_the_include_where_the_incbin_was():
    out = splice_a_fill()
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines[1] == "\tINCBIN  baserom.gba_0x1000_0x1800.extracted"
    assert lines[2] == "\tINCLUDE fill_1800.s"
    assert lines[3] == "\tINCBIN  baserom.gba_0x1900_0x2000.extracted"
    assert "baserom.gba_0x1000_0x2000.extracted" not in out


def test_splice_refuses_a_fill_that_is_not_inside_the_slice():
    with pytest.raises(F.FillError):
        F.splice(SOURCE, (0x1000, 0x2000), [{"start": 0x3000, "length": 0x100, "value": 0x00}])


def test_splice_refuses_when_the_token_is_not_found():
    with pytest.raises(F.FillError):
        F.splice("\tINCBIN\tother.bin\n", (0x1000, 0x2000), [])
