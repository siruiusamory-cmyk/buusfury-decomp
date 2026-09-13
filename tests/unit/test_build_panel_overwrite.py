"""WORKBENCH-001 live-QA fix: WriteError on a second build to the same output.

A second build raises `write.WriteError` ("refusing to overwrite"), which is NOT
a BuildError/ProjectError subclass and used to escape `_on_build` to the terminal.
The panel now catches it and, when the output file actually exists and is provably
not the source ROM, offers to overwrite (delete output + rebuild).

SC2 SAFETY: when the output path equals the source ROM the delete never happens.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.webfoot.workbench import build_panel as bp
from tools.webfoot.workbench.build_panel import BuildPanelTab, output_file_for
from tools.webfoot.workbench.session import Session
from tools.webfoot.write import WriteError

pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402


@pytest.fixture(scope="module")
def _app():
    return QApplication.instance() or QApplication([])


def _make_panel(tmp_path, _app):
    rom = tmp_path / "src" / "buus_fury.gba"
    rom.parent.mkdir()
    rom.write_bytes(b"\x00")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    session = Session(
        rom_path=rom,
        profile=SimpleNamespace(id="buus_fury_usa_rev0"),
        project_dir=tmp_path / "proj",
        output_dir=out_dir,
    )
    panel = BuildPanelTab(session, catalog=None)
    output_path = output_file_for(out_dir, session.profile.id)
    return panel, session, output_path


def test_overwrite_yes_deletes_output_and_rebuilds(tmp_path, monkeypatch, _app):
    panel, session, output_path = _make_panel(tmp_path, _app)
    output_path.write_bytes(b"OLD")  # simulate a prior build's output

    calls = {"n": 0, "finished": 0}

    def fake_build(project_dir, rom_path, out, catalog):
        calls["n"] += 1
        if Path(out).exists():
            raise WriteError("refusing to overwrite an existing output image")
        return SimpleNamespace(output_path=out)

    monkeypatch.setattr(bp.build_sdk, "build_project", fake_build)
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    panel.buildFinished.connect(lambda: calls.__setitem__("finished", calls["finished"] + 1))

    panel._on_build()  # must not raise

    assert not output_path.exists(), "prior output should have been unlinked"
    assert calls["n"] == 2, "build_project should be retried after unlink"
    assert calls["finished"] == 1, "buildFinished emitted on the retry"
    assert session.last_build is not None
    assert session.rom_path.exists(), "source ROM must never be touched"


def test_overwrite_no_keeps_output_no_crash(tmp_path, monkeypatch, _app):
    panel, session, output_path = _make_panel(tmp_path, _app)
    output_path.write_bytes(b"OLD")

    def fake_build(project_dir, rom_path, out, catalog):
        if Path(out).exists():
            raise WriteError("refusing to overwrite an existing output image")
        return SimpleNamespace(output_path=out)

    monkeypatch.setattr(bp.build_sdk, "build_project", fake_build)
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.No))

    panel._on_build()  # must not raise

    assert output_path.exists(), "output must be kept when the user declines"
    assert output_path.read_bytes() == b"OLD"
    assert session.last_build is None


def test_output_equals_rom_never_deletes(tmp_path, monkeypatch, _app):
    """SC2 SAFETY: if output_path resolves to the source ROM, no unlink, no build.

    The pre-build guard fires the refuse dialog; build_project is never called and
    the source ROM survives. Proven by making output_file_for return rom_path.
    """
    panel, session, _ = _make_panel(tmp_path, _app)
    rom = session.rom_path
    rom_before = rom.read_bytes()

    monkeypatch.setattr(bp, "output_file_for", lambda out_dir, pid: rom)
    build_called = {"n": 0}
    monkeypatch.setattr(
        bp.build_sdk, "build_project",
        lambda *a, **k: build_called.__setitem__("n", build_called["n"] + 1))
    # If code ever reached the delete branch this would flag it:
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))

    panel._on_build()

    assert build_called["n"] == 0, "build must not run when guard fails"
    assert rom.exists() and rom.read_bytes() == rom_before, "source ROM untouched"
