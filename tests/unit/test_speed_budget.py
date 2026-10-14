"""The rule-S speed guard in ``tests/conftest.py``: its budgets, its exceptions and
its failure path. Every node names the claim it makes.
"""

from __future__ import annotations

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
        5.0, "SPEED-GATE-001")
    assert conftest._speed_budget("tests/unit/test_nowhere.py::test_x", True) == (
        30.0, "SPEED-GATE-001")


def test_an_exception_allows_only_its_own_measurement_plus_the_slack(monkeypatch) -> None:
    monkeypatch.setitem(conftest._BUDGET_EXCEPTIONS, "tests/unit/test_nowhere.py::test_y",
                        (10.0, "a deliberately slow shape", "TICKET-1"))
    assert conftest._speed_budget("tests/unit/test_nowhere.py::test_y", False) == (
        15.0, "TICKET-1")


def test_every_exception_names_a_real_module_a_measurement_a_reason_and_a_ticket() -> None:
    assert conftest._BUDGET_EXCEPTIONS
    for nodeid, (seconds, why, ticket) in conftest._BUDGET_EXCEPTIONS.items():
        path = nodeid.split("::", 1)[0]
        assert (REPOSITORY_ROOT / path).is_file(), nodeid
        assert seconds > 0.0, nodeid
        if seconds <= conftest._SPEED_BUDGET_SECONDS:
            assert "headroom" in why, nodeid
        assert why.strip() and why != ticket, nodeid
        assert ticket.strip(), nodeid


def test_the_guard_names_a_slow_node_with_its_seconds_and_budget(monkeypatch, capsys) -> None:
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_slow": 9.5})
    assert conftest._report_speed_breaches(_Session()) is True
    printed = capsys.readouterr().out
    assert "tests/unit/test_nowhere.py::test_slow" in printed
    assert "9.50s" in printed
    assert "5.0s budget" in printed
    assert "SPEED-GATE-001" in printed


def test_a_node_inside_its_budget_is_not_a_breach(monkeypatch, capsys) -> None:
    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_quick": 1.25})
    assert conftest._report_speed_breaches(_Session()) is False
    assert capsys.readouterr().out == ""


def test_a_worker_stays_silent_because_the_controller_owns_the_report(monkeypatch) -> None:
    class _WorkerConfig(_Config):
        workerinput = {"workerid": "gw0"}

    class _WorkerSession(_Session):
        config = _WorkerConfig()

    monkeypatch.setattr(conftest, "_TEST_SECONDS",
                        {"tests/unit/test_nowhere.py::test_slow": 9.5})
    assert conftest._report_speed_breaches(_WorkerSession()) is False
