from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import raw_remainder  # noqa: E402

CENSUS = [{"start": 0x10, "end": 0x14, "bytes": 4, "region": "R00", "route": "NONE"}]


def ledger_of(**changes):
    row = {"start": 0x10, "end": 0x14, "bytes": 4, "region": "R00", "route": "NONE",
           "references": "none", "consumer": "none", "attempts": "none", "status": "unmapped"}
    row.update(changes)
    return [row]


def test_the_ledger_passes_when_every_interval_carries_a_status_and_a_route():
    assert raw_remainder.ledger_check(ledger_of(), CENSUS, 4) == 4


def test_a_missing_interval_is_refused():
    with pytest.raises(SystemExit):
        raw_remainder.ledger_check([], CENSUS, 4)


def test_a_doubled_interval_is_refused():
    with pytest.raises(SystemExit):
        raw_remainder.ledger_check(ledger_of() + ledger_of(), CENSUS, 8)


def test_a_row_without_a_status_is_refused():
    with pytest.raises(SystemExit):
        raw_remainder.ledger_check(ledger_of(status=""), CENSUS, 4)


def test_a_status_outside_the_owner_vocabulary_is_refused():
    with pytest.raises(SystemExit):
        raw_remainder.ledger_check(ledger_of(status="residual"), CENSUS, 4)


def test_an_unrouted_row_is_refused():
    with pytest.raises(SystemExit):
        raw_remainder.ledger_check(ledger_of(route=""), CENSUS, 4)


def test_status_of_states_the_precedence_beside_a_row_that_matches_three_predicates():
    row = {"start": 0x100, "end": 0x110, "region_id": "R20"}
    assert raw_remainder.status_of(row, (0x100, 0x110), ("runtime-cited", 0x200)) == "in progress"
    assert raw_remainder.status_of(row, (0, 0), ("runtime-cited", 0x200)) == "runtime-pending"
    assert raw_remainder.status_of(row, (0, 0), None) == "identified binary"
    assert raw_remainder.status_of(row, (0, 0), ("cited", 0x200)) == "identified binary"


def test_the_ledger_headline_is_the_gates_source_total():
    with open(raw_remainder.LEDGER_DOC, encoding="utf-8") as handle:
        assert raw_remainder.doc_source(handle.read()) == raw_remainder.gate.source_bytes()


def test_a_stale_headline_is_not_the_gates_total():
    stale = "source=7780188 of 8388608 (92.7471 %)"
    assert raw_remainder.doc_source(stale) != raw_remainder.gate.source_bytes()


def test_the_ledger_doc_states_the_precedence_status_of_implements():
    with open(raw_remainder.LEDGER_DOC, encoding="utf-8") as handle:
        text = handle.read()
    assert "`in progress` > `runtime-pending` > `identified binary` > `unmapped`" in text


def test_the_route_doc_reports_the_class_it_holds_and_no_stale_count():
    import csv
    with open(raw_remainder.DOC_OUT, encoding="utf-8") as handle:
        text = handle.read()
    with open(raw_remainder.CSV_OUT, newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["class"] == "code-without-entry"]
    assert ("### `code-without-entry` - %d rows, %d B"
            % (len(rows), sum(int(row["bytes"]) for row in rows))) in text
    assert "The 9 rows left" not in text
    assert "0x042118..0x042188" in text
