from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
for _path in (HERE, os.path.join(os.path.dirname(HERE), "gate")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import others_found_triage  # noqa: E402
import residual_index  # noqa: E402


def test_the_triage_holds_exactly_the_index_class():
    rows = others_found_triage.others()
    assert rows == [row for row in residual_index.measure()
                    if row["verdict"] == residual_index.OTHERS]
    assert others_found_triage.check(rows) == (
        residual_index.totals(rows)[residual_index.OTHERS][0],
        residual_index.totals(rows)[residual_index.OTHERS][1])


def test_the_tracked_triage_is_the_table_the_groups_derive():
    assert others_found_triage.main(["--check"]) == 0


def doctored(reference, changes):
    specs = dict(others_found_triage.DISPOSITIONS)
    specs[reference] = dict(specs[reference], **changes)
    return specs


def test_a_group_of_4_kib_or_more_with_no_next_step_is_refused(monkeypatch):
    specs = dict(others_found_triage.DISPOSITIONS)
    del specs["code:0x08038B98"]
    monkeypatch.setattr(others_found_triage, "DISPOSITIONS", specs)
    with pytest.raises(SystemExit):
        others_found_triage.check()


def test_a_next_step_for_a_group_under_4_kib_is_refused(monkeypatch):
    specs = dict(others_found_triage.DISPOSITIONS)
    specs["code:0x08012848"] = dict(specs["code:0x08038B98"])
    monkeypatch.setattr(others_found_triage, "DISPOSITIONS", specs)
    with pytest.raises(SystemExit):
        others_found_triage.check()


def test_a_quote_its_document_no_longer_holds_is_refused(monkeypatch):
    specs = doctored("code:0x08038B98", {"sample": "a measurement no census states"})
    monkeypatch.setattr(others_found_triage, "DISPOSITIONS", specs)
    with pytest.raises(SystemExit):
        others_found_triage.check()
