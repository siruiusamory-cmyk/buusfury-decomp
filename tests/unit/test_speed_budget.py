"""The rule-S speed guard in tests/conftest.py: its budgets, its exception table, the
single-node re-run it uses to tell a regression from runner variance, and its failure
path. Every node names the claim it makes.
"""

from __future__ import annotations

import ast

from tests import conftest
from tests.gates import REPOSITORY_ROOT


class _Hook:
    def __init__(self):
        self.reports = []

    def pytest_runtest_logreport(self, report):
        self.reports.append(report)


class _Plugins:
    def get_plugin(self, name):
        return None


class _Config:
    pluginmanager = _Plugins()

    def __init__(self):
        self.hook = _Hook()

    def getoption(self, name, default=None):
        return default


class _Session:
    def __init__(self):
        self.config = _Config()
        self.items: list = []


def test_the_unit_budget_is_five_seconds_and_the_rom_budget_is_thirty() -> None:
    assert conftest._SPEED_BUDGET_SECONDS == 5.0
    assert conftest._SPEED_ROM_BUDGET_SECONDS == 30.0


def test_an_unlisted_node_gets_the_rule_budget_and_the_rule_ticket() -> None:
    assert conftest._speed_budget("tests/unit/test_nowhere.py::test_x", False) == (
        5.0, 5.0, "SPEED-GATE-001")
    assert conftest._speed_budget("tests/unit/test_nowhere.py::test_x", True) == (
        30.0, 30.0, "SPEED-GATE-001")


def test_an_exception_below_the_budget_keeps_the_budget_as_its_allowance(monkeypatch) -> None:
    monkeypatch.setitem(conftest._BUDGET_EXCEPTIONS, "tests/unit/test_nowhere.py::test_y",
                        (3.100, "38600996718 f55e32d8", "a slow shape", "TICKET-1"))
    assert conftest._speed_budget("tests/unit/test_nowhere.py::test_y", False) == (
        5.0, 5.0, "TICKET-1")


def test_an_exception_over_the_budget_gets_proportional_slack(monkeypatch) -> None:
    monkeypatch.setitem(conftest._BUDGET_EXCEPTIONS, "tests/unit/test_nowhere.py::test_y",
                        (10.000, "38600996718 f55e32d8", "a slow shape", "TICKET-1"))
    assert conftest._speed_budget("tests/unit/test_nowhere.py::test_y", False) == (
        5.0, 15.0, "TICKET-1")


def test_every_exception_carries_a_measurement_a_source_a_reason_and_a_ticket() -> None:
    assert conftest._BUDGET_EXCEPTIONS
    for nodeid, (seconds, source, why, ticket) in conftest._BUDGET_EXCEPTIONS.items():
        path = nodeid.split("::", 1)[0]
        assert (REPOSITORY_ROOT / path).is_file(), nodeid
        assert seconds > 0.0, nodeid
        assert source.strip() and source != ticket, nodeid
        if seconds <= conftest._SPEED_BUDGET_SECONDS:
            assert "headroom" in why, nodeid
        assert why.strip() and why != ticket, nodeid
        assert ticket.strip(), nodeid


def test_the_exception_table_declares_each_key_once() -> None:
    source = (REPOSITORY_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    keys = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == (
                "_BUDGET_EXCEPTIONS"):
            keys = [key.value for key in node.value.keys]
    assert keys, "the exception table is not a dict literal with string keys"
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    assert not repeated, repeated


def test_the_re_run_of_a_node_the_session_never_collected_is_unmeasured() -> None:
    assert conftest._remeasure_item(_Session(), "tests/unit/test_nowhere.py::test_x") is None


def test_the_guard_names_a_slow_node_with_both_timings(monkeypatch, capsys) -> None:
    session = _Session()
    session.items = [_Item()]
    monkeypatch.setattr(conftest, "_TEST_SECONDS", {_Item.nodeid: 9.5})
    monkeypatch.setattr(conftest, "_remeasure_item", lambda session, nodeid: 9.8)
    assert conftest._report_speed_breaches(session) is True
    printed = capsys.readouterr().out
    assert _Item.nodeid in printed
    assert "took 9.50s" in printed and "re-run 9.80s" in printed
    assert "5.0s allowance" in printed and "budget 5.0s" in printed
    assert "SPEED-GATE-001" in printed


def test_a_breach_whose_re_run_is_inside_the_allowance_passes(monkeypatch, capsys) -> None:
    session = _Session()
    session.items = [_Item()]
    monkeypatch.setattr(conftest, "_TEST_SECONDS", {_Item.nodeid: 9.5})
    monkeypatch.setattr(conftest, "_remeasure_item", lambda session, nodeid: 1.0)
    assert conftest._report_speed_breaches(session) is False
    assert capsys.readouterr().out == ""


def test_a_node_inside_its_budget_is_not_a_breach(monkeypatch, capsys) -> None:
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_quick": 1.25})
    assert conftest._report_speed_breaches(_Session()) is False
    assert capsys.readouterr().out == ""


def test_an_integration_node_is_measured_against_the_rom_budget(monkeypatch, capsys) -> None:
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/integration/test_rom_reader_example.py::test_slow": 12.0})
    assert conftest._report_speed_breaches(_Session()) is False
    assert capsys.readouterr().out == ""
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/integration/test_rom_reader_example.py::test_slow": 31.0})
    monkeypatch.setattr(conftest, "_remeasure_item", lambda session, nodeid: 31.5)
    assert conftest._report_speed_breaches(_Session()) is True
    printed = capsys.readouterr().out
    assert "took 31.00s" in printed and "30.0s allowance" in printed


def test_an_xdist_controller_defers_to_its_workers(monkeypatch) -> None:
    class _ControllerConfig(_Config):
        def getoption(self, name, default=None):
            return 4 if name == "numprocesses" else default

    session = _Session()
    session.config = _ControllerConfig()
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_slow": 9.5})
    assert conftest._report_speed_breaches(session) is False


class _Item:
    nodeid = "tests/unit/test_nowhere.py::test_slow"
    location = ("tests/unit/test_nowhere.py", 1, "test_slow")


def test_a_confirmed_breach_is_reported_as_a_failed_test(monkeypatch) -> None:
    session = _Session()
    session.items = [_Item()]
    monkeypatch.setattr(conftest, "_TEST_SECONDS", {_Item.nodeid: 9.5})
    monkeypatch.setattr(conftest, "_remeasure_item", lambda session, nodeid: 9.8)
    assert conftest._report_speed_breaches(session) is True
    reports = session.config.hook.reports
    assert [report.outcome for report in reports] == ["failed"]
    assert reports[0].nodeid == _Item.nodeid
    assert "re-run 9.80s" in str(reports[0].longrepr)
