from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
for _path in (HERE, os.path.join(os.path.dirname(HERE), "gate")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import residual_index  # noqa: E402
import residual_verdicts  # noqa: E402


def test_the_verdict_tables_of_a_document_are_the_ones_that_state_a_verdict(tmp_path):
    path = tmp_path / "doc.md"
    path.write_text("| row | bytes | map evidence |\n|---|---|---|\n| `0010..0014` | 4 | read |\n"
                    "\n| start | end | null |\n|---|---|---|\n| `0x10` | `0x14` | no reader |\n",
                    encoding="utf-8")
    tables = residual_index.verdict_tables(str(path))
    assert len(tables) == 1
    assert tables[0][0][-1] == "null"
    assert residual_index.span_of(tables[0][1][0][1]) == (0x10, 0x14)


def test_a_span_is_read_from_two_cells_or_from_one_range():
    assert residual_index.span_of(["0x10", "0x14", "4"]) == (0x10, 0x14)
    assert residual_index.span_of(["0017a9ac..0017aaac", "256"]) == (0x17A9AC, 0x17AAAC)
    assert residual_index.span_of(["`0x005C3E..0x005C40`", "2"]) == (0x5C3E, 0x5C40)
    assert residual_index.span_of(["none", "4"]) is None


def test_the_census_gives_every_row_one_verdict_and_its_document():
    rows = residual_index.measure()
    assert residual_index.gaps(rows) == []
    assert residual_index.conflicts(rows) == []
    assert sum(row["bytes"] for row in rows) == residual_index.raw_bytes()


def test_the_index_states_the_gates_totals():
    rows = residual_index.measure()
    classes = residual_index.totals(rows)
    assert classes[residual_index.IDENTITY] == [0, 0]
    assert residual_index.identity_bytes() == sum(
        length for _start, length in residual_index.gate.union_ranges(
            residual_index.gate.identity_ranges()))
    assert sum(classes[name][1] for name in residual_index.CLASSES
               if name != residual_index.IDENTITY) == residual_index.raw_bytes()


def test_the_tracked_index_is_the_table_the_census_derives():
    rows = residual_index.measure()
    with open(residual_index.DOC_OUT, encoding="utf-8") as handle:
        assert handle.read() == residual_index.doc_text(rows)


def doctored(changes):
    rows = residual_index.measure()
    return [dict(rows[0], **changes)] + rows[1:]


def test_a_row_with_no_verdict_line_is_refused():
    with pytest.raises(SystemExit):
        residual_index.check(doctored({"carrier_lines": []}))


def test_a_row_carried_by_two_documents_is_refused():
    with pytest.raises(SystemExit):
        residual_index.check(doctored({"docs": ["R32_NULL_CENSUS.md", "R00_R22_NULL_CENSUS.md"]}))


def test_the_census_row_matches_the_document_its_generator_writes():
    rom = residual_verdicts.read_rom()
    comments = residual_verdicts.emitted.carrier_comments(residual_verdicts.ROOT)
    rows = [row for row in residual_verdicts.census("R02")
            if not residual_verdicts.inside_fence(row)]
    with open(residual_verdicts.DOC_R02, encoding="utf-8") as handle:
        assert handle.read() == residual_verdicts.r02_text(rows, comments)
    missing, _known = residual_verdicts.r19_rows()
    section = residual_verdicts.r19_section(missing, rom)
    with open(residual_verdicts.DOC_R19, encoding="utf-8") as handle:
        assert section in handle.read()
