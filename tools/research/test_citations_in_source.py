import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import citations_in_source as cis  # noqa: E402

ROW = (0x1000, 0x100)
RAW_ROW = (0x2000, 0x80)
CODE_PAIR = (0x1040, 0x1040 + 0x40)
GENERATED_PAIR = (0x3000, 0x3000 + 0x20)
ROWS = ((ROW[0], ROW[0] + ROW[1]), (RAW_ROW[0], RAW_ROW[0] + RAW_ROW[1]))
CODE = (CODE_PAIR,)
GENERATED = (GENERATED_PAIR,)


def classify(offset):
    return cis.site_class(cis.spans_index(CODE), cis.spans_index(GENERATED),
                          cis.spans_index(ROWS), offset)


def test_a_site_in_code_is_cited():
    got, routes, first, klass = cis.code_verdict({"A": [0x1050]}, False, classify)
    assert (got, routes, first, klass) == ("cited", ["A"], 0x1050, "code")
    got, routes, first, klass = cis.code_verdict({"P": [0x1060], "A": [0x1050]}, False, classify)
    assert (got, routes, first) == ("cited", ["P", "A"], 0x1050)


def test_a_site_only_in_a_raw_row_is_not_cited():
    assert classify(RAW_ROW[0] + 4) == "row"
    assert classify(GENERATED[0][0] + 4) == "generated"
    assert cis.code_verdict({"P": [RAW_ROW[0] + 4]}, False, classify)[0] == "unreferenced"
    assert cis.code_verdict({"A": [GENERATED[0][0] + 4]}, False, classify)[0] == "unreferenced"
    assert cis.code_verdict({"A": [0x9000]}, False, classify)[0] == "unreferenced"


def test_a_runtime_only_row_is_runtime_cited():
    got, routes, first, klass = cis.code_verdict({"P": [RAW_ROW[0] + 4]}, True, classify)
    assert (got, routes, first, klass) == ("runtime-cited", [], None, None)
    assert cis.code_verdict({}, False, classify) == ("unreferenced", [], None, None)


def test_a_site_at_a_rows_end_is_not_in_the_row():
    start, length = ROW
    assert cis.half_open(start, start + length, [start, start + length - 1]) == [start,
                                                                                start + length - 1]
    assert cis.half_open(start, start + length, [start + length]) == []
    assert classify(start + length) == "unledgered"
    got, routes, first, klass = cis.code_verdict({"A": [start + length, CODE_PAIR[0] + 0x10]},
                                                 False, classify)
    assert (got, first) == ("cited", CODE_PAIR[0] + 0x10)


def test_the_sum_invariant_raises_when_a_class_is_dropped():
    classes = {"cited": 10, "runtime-cited": 20, "unreferenced": 70}
    assert cis.check_totals(classes, 100, 100) == 100
    for dropped in ("cited", "runtime-cited", "unreferenced"):
        short = dict(classes)
        short[dropped] = 0
        try:
            cis.check_totals(short, 100, 100)
        except BaseException as error:
            assert isinstance(error, SystemExit), error
        else:
            raise AssertionError("a dropped %s did not raise" % dropped)
    try:
        cis.check_totals(classes, 100, 101)
    except BaseException as error:
        assert isinstance(error, SystemExit), error
    else:
        raise AssertionError("a raw total other than the INCBIN total did not raise")


def test_a_recorded_citation_site_is_not_a_channel():
    field = ("; cited by entry at file 0x08E580, field +0x30; 0x08008CEE ldr r1,[r0,#0x30] -> "
             "bl 0x08004038 (the opcode interpreter)")
    forms = cis.comment_forms([(15, field), (16, "; stride none proven")])
    assert forms == {"runtime": False, "recorded": True, "field_site": 0x8CEE}
    got, routes, first, klass = cis.code_verdict({}, forms["runtime"], classify)
    assert (got, routes, first, klass) == ("unreferenced", [], None, None)
    runtime = ("; cited by runtime read, session rt001, (pc, first_address_read): "
               "03000070=0819C78C, 03000084=0819C7EC")
    forms = cis.comment_forms([(13, runtime)])
    assert forms["runtime"] and not forms["recorded"]
    assert cis.code_verdict({}, forms["runtime"], classify)[0] == "runtime-cited"


def test_the_written_csv_parses_with_eight_fields_on_every_row():
    import csv as csv_module

    path = os.path.join(ROOT, "docs", "research", "RAW_CITATIONS.csv")
    assert os.path.exists(path), "run citations_in_source.py to write the table first"
    fields = ("row", "start", "end", "bytes", "class", "route", "first site", "site class")
    with open(path, newline="") as handle:
        reader = csv_module.DictReader(handle)
        assert tuple(reader.fieldnames) == fields, reader.fieldnames
        rows = list(reader)
    assert rows, "the table is empty"
    for listed in rows:
        assert None not in listed.values(), listed
        assert list(listed) == list(fields), listed
    pairs = [listed for listed in rows if listed["route"] == "P+A"]
    print("  RAW_CITATIONS.csv: %d row(s), all with the 8 named fields; P+A rows=%d"
          % (len(rows), len(pairs)))


if __name__ == "__main__":
    passed = 0
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            passed += 1
    print("citations_in_source: %d test(s) passed" % passed)
