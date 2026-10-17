"""The session-end skip census, and the artefact dependency it declares.

A green ``fast`` run used to say only how many tests skipped. The census in
``tests/conftest.py`` now names each one with pytest's own reason and marks the
members declared in ``ARTEFACT_DEPENDENT_TESTS`` (``tests/gates.py``), so a
reader of a green local run can tell which assertions did not execute. These
tests hold both halves of that: the declaration names real tests that really
skip over a missing artefact, and the census reports skips without ever failing
a session over one.
"""

from __future__ import annotations

from pathlib import Path
import re
import types

import pytest

from tests import conftest
from tests.gates import ARTEFACT_DEPENDENT_TESTS, REPOSITORY_ROOT, TESTS_DIRECTORY


def _declared_member(entry: str) -> tuple[Path, str]:
    relative, _, test = entry.partition("::")
    return REPOSITORY_ROOT / TESTS_DIRECTORY / relative, test


def test_every_declared_artefact_member_names_a_real_skipping_test():
    """Prevents: the declaration decaying into node ids nobody checked.

    Each entry must be a portable test node id whose file exists and whose
    function is defined there, and the file must still carry the artefact skip
    the entry claims - a member that stopped skipping belongs out of the list,
    not in a report that never mentions it again.
    """
    assert ARTEFACT_DEPENDENT_TESTS, "the artefact dependency list cannot be empty"
    assert len(set(ARTEFACT_DEPENDENT_TESTS)) == len(ARTEFACT_DEPENDENT_TESTS)

    for entry in ARTEFACT_DEPENDENT_TESTS:
        path, test = _declared_member(entry)
        assert entry.startswith("unit/test_"), entry
        assert test.startswith("test_"), entry
        assert path.is_file(), f"{entry} is declared but {path} does not exist"
        source = path.read_text(encoding="utf-8")
        assert re.search(rf"^def {re.escape(test)}\(", source, re.M), (
            f"{entry} is declared but {path.name} defines no such test"
        )
        assert "not built" in source, (
            f"{entry} is declared as artefact-dependent but {path.name} carries "
            "no skip for a missing artefact"
        )


def _stub_session() -> types.SimpleNamespace:
    """The minimum a session hook needs: a config with no terminal plugin.

    No terminal reporter means the census prints through ``print``, which is what
    :func:`_observed_census` reads. The GUI guard is stubbed out of the way so
    this file tests the census rather than the guard.
    """
    config = types.SimpleNamespace(
        pluginmanager=types.SimpleNamespace(get_plugin=lambda name: None)
    )
    # The real session the hook is written for carries the items it collected, so the
    # stub mirrors that shape; `_report_speed_breaches` tolerates its absence, and this
    # keeps the stub honest rather than minimal.
    return types.SimpleNamespace(
        config=config, exitstatus=pytest.ExitCode.OK, items=[]
    )


def _run_session_end(monkeypatch, skips: dict[str, str]) -> types.SimpleNamespace:
    monkeypatch.setattr(conftest, "_SKIPPED_TEST_REASONS", dict(skips))
    # `_TEST_SECONDS` is the session's own recording, so a stub session handed to the
    # real hook would inherit whatever this worker has already timed and report those
    # nodes as rule-S breaches: the "silent when nothing skipped" case then prints,
    # and any breach makes the hook walk the session's items. Empty it for the stub.
    monkeypatch.setattr(conftest, "_TEST_SECONDS", {})
    monkeypatch.setattr(conftest, "_collapsed_required_modules", lambda: [])
    monkeypatch.setattr(conftest, "_collapsed_gui_modules", lambda: [])
    # This calls the real hook, which writes the module global the CI exit path carries, so
    # register the current value first: monkeypatch then hands it back at teardown rather
    # than leaving the status of this stub session behind for another file to read.
    monkeypatch.setattr(conftest, "_SESSION_EXIT_STATUS", conftest._SESSION_EXIT_STATUS)
    session = _stub_session()
    conftest.pytest_sessionfinish(session, pytest.ExitCode.OK)
    return session


def test_the_census_names_every_skip_and_marks_the_declared_member(
    monkeypatch, capsys
):
    """The census must name what skipped and why, not count it."""
    declared = (
        "tests/unit/test_site_consistency.py"
        "::test_the_built_site_passes_every_check"
    )
    _run_session_end(
        monkeypatch,
        {
            declared: "site not built; run `npm run build`",
            "tests/unit/test_map_render.py::test_map40_renders_from_vram_capture": (
                "canonical ROM or map40 VRAM dump not present"
            ),
        },
    )

    out = capsys.readouterr().out
    assert "unit/test_site_consistency.py::test_the_built_site_passes_every_check" in out
    assert "site not built; run `npm run build`" in out
    assert "declared artefact dependency" in out
    # An undeclared skip is still named and reasoned, and is not marked as one.
    assert "test_map40_renders_from_vram_capture" in out
    assert "canonical ROM or map40 VRAM dump not present" in out
    assert out.count("declared artefact dependency") == 1


def test_a_parametrised_member_is_covered_by_its_function(monkeypatch, capsys):
    """``::test_x[param]`` is the declared ``::test_x`` member."""
    parametrised = (
        "unit/test_questline_rail.py::test_built_page_carries_the_derived_stop"
        "[--rail-complete]"
    )
    _run_session_end(
        monkeypatch,
        {f"tests/{parametrised}": "site not built; run `npm run build`"},
    )

    out = capsys.readouterr().out
    assert f"skipped: {parametrised} - site not built" in out
    assert "declared artefact dependency" in out


def test_the_census_is_silent_when_nothing_skipped(monkeypatch, capsys):
    """A healthy run reports nothing, which is the other half of the contract."""
    _run_session_end(monkeypatch, {})

    assert capsys.readouterr().out == ""


def test_a_skipped_artefact_member_does_not_fail_the_session(monkeypatch, capsys):
    """The census reports; it does not enforce. No CI job builds the site for
    the fast gate, so a member skipping there is the designed arrangement."""
    monkeypatch.setenv("CI", "true")
    session = _run_session_end(
        monkeypatch,
        {
            "tests/unit/test_capability_registry.py"
            "::test_the_built_page_renders_the_registry_list": (
                "site not built; run `npm run build`"
            )
        },
    )

    assert "declared artefact dependency" in capsys.readouterr().out
    assert session.exitstatus == pytest.ExitCode.OK
