"""The rule-S speed guard in ``tests/conftest.py``: its budgets, its exceptions, its
re-run rule and its failure path. Every node names the claim it makes.
"""

from __future__ import annotations

import ast

from tests import conftest
from tests.gates import REPOSITORY_ROOT


class _Plugins:
    def get_plugin(self, name):
        return None


class _Config:
    pluginmanager = _Plugins()


class _Session:
    config = _Config()
    items: list = []


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


def test_the_guard_names_a_slow_node_with_its_seconds_and_allowance(monkeypatch, capsys) -> None:
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_slow": 9.5})
    assert conftest._report_speed_breaches(_Session()) is True
    printed = capsys.readouterr().out
    assert "tests/unit/test_nowhere.py::test_slow" in printed
    assert "took 9.50s" in printed
    assert "5.0s allowance" in printed and "budget 5.0s" in printed
    assert "SPEED-GATE-001" in printed


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
    assert conftest._report_speed_breaches(_Session()) is True
    printed = capsys.readouterr().out
    assert "took 31.00s" in printed and "30.0s allowance" in printed


def test_a_worker_stays_silent_because_the_controller_owns_the_report(monkeypatch) -> None:
    class _WorkerConfig(_Config):
        workerinput = {"workerid": "gw0"}

    class _WorkerSession(_Session):
        config = _WorkerConfig()

    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_slow": 9.5})
    assert conftest._report_speed_breaches(_WorkerSession()) is False
