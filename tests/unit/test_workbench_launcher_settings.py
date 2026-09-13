"""WORKBENCH-003 - mGBA path persistence (settings helper + launcher wiring).

Helper tests round-trip a path and prove fail-safe behavior on
missing/corrupt/unwritable. Launcher tests (offscreen) prove field init
precedence and save-on-successful-launch. Both point the config dir at a tmp
dir via WEBFOOT_WORKBENCH_CONFIG_DIR so nothing touches the real user config.
"""

from __future__ import annotations

import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")  # settings imports QStandardPaths

from tools.webfoot.workbench import settings  # noqa: E402

_ENV = "WEBFOOT_WORKBENCH_CONFIG_DIR"


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    monkeypatch.setenv(_ENV, str(tmp_path))
    return tmp_path


# --- helper level (no widgets) ------------------------------------------------

def test_save_then_load_round_trips(config_dir):
    settings.save_mgba_path("/opt/mgba")
    assert settings.load_mgba_path() == "/opt/mgba"


def test_load_none_when_missing(config_dir):
    assert settings.load_mgba_path() is None


def test_load_none_on_corrupt_json(config_dir):
    (config_dir / "workbench-settings.json").write_text("{ not json", encoding="utf-8")
    assert settings.load_mgba_path() is None  # returns, does not raise


def test_save_tolerates_unwritable_dir(tmp_path, monkeypatch):
    # Point the config dir at a path whose parent is a FILE - mkdir will fail.
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(_ENV, str(blocker / "sub"))
    settings.save_mgba_path("/opt/mgba")  # must not raise
    assert settings.load_mgba_path() is None


# --- launcher level (offscreen widget) ----------------------------------------

@pytest.fixture(scope="module")
def qapp():
    from PySide6 import QtWidgets
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def session():
    from tools.webfoot.workbench.session import Session
    return Session()


def test_field_prefills_saved_valid_path(config_dir, qapp, session, tmp_path, monkeypatch):
    from tools.webfoot.workbench import launcher
    exe = tmp_path / "mgba.exe"
    exe.write_text("", encoding="utf-8")
    settings.save_mgba_path(str(exe))
    # Detection must NOT win when a valid saved path exists.
    monkeypatch.setattr(launcher, "_detect_mgba", lambda: "/on/path/mgba")
    tab = launcher.LauncherTab(session)
    assert tab._mgba_field.text() == str(exe)


def test_stale_saved_path_falls_back_to_detection(config_dir, qapp, session, monkeypatch):
    from tools.webfoot.workbench import launcher
    settings.save_mgba_path("/no/such/mgba")  # does not exist
    monkeypatch.setattr(launcher, "_detect_mgba", lambda: "/detected/mgba")
    tab = launcher.LauncherTab(session)
    assert tab._mgba_field.text() == "/detected/mgba"  # not the dead saved path


def test_picking_path_persists_without_launch(config_dir, qapp, session, tmp_path, monkeypatch):
    # The user's actual flow: Browse -> pick a path -> close (no launch) -> reopen.
    # _pick_mgba must persist immediately; a fresh tab must then pre-fill it.
    from tools.webfoot.workbench import launcher
    exe = tmp_path / "mgba.exe"
    exe.write_text("", encoding="utf-8")
    monkeypatch.setattr(launcher.QFileDialog, "getOpenFileName",
                        lambda *a, **k: (str(exe), ""))
    tab = launcher.LauncherTab(session)
    tab._pick_mgba()  # no _launch()/Popen anywhere
    saved = json.loads((config_dir / "workbench-settings.json").read_text(encoding="utf-8"))
    assert saved["mgba_path"] == str(exe)
    # Reopen: a fresh tab against the same config dir pre-fills the saved path.
    fresh = launcher.LauncherTab(session)
    assert fresh._mgba_field.text() == str(exe)


def test_successful_launch_persists_path(config_dir, qapp, session, tmp_path, monkeypatch):
    from tools.webfoot.workbench import launcher
    exe = tmp_path / "mgba.exe"
    exe.write_text("", encoding="utf-8")
    rom = tmp_path / "game.gba"
    rom.write_text("", encoding="utf-8")
    launched = {}
    monkeypatch.setattr(launcher.subprocess, "Popen",
                        lambda args, *a, **k: launched.setdefault("args", args))
    tab = launcher.LauncherTab(session)
    tab._mgba_field.setText(str(exe))
    tab._rom_field.setText(str(rom))
    tab._launch()
    assert launched["args"] == [str(exe), str(rom)]  # really "launched"
    saved = json.loads((config_dir / "workbench-settings.json").read_text(encoding="utf-8"))
    assert saved["mgba_path"] == str(exe)
