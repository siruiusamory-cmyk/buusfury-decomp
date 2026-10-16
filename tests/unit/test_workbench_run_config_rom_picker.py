"""RUN-CONFIG-ROM-PICKER-001: a manually chosen ROM is launchable.

The Run surface carries its own ROM picker precisely so that a ROM can be named
independently of the last build. CORRECTNESS-AUDIT-001 confirmed that it could
not: the shell derived its Run action from ``session.last_build`` while the
Launch button derived from the ROM field, and ``_pick_rom`` recomputed neither,
so a chosen path was written into the field with both surfaces still disabled.

These tests drive the real widget path - the picker, the field, the visible
button and the shell's Ctrl+R action - instead of assigning the field and
calling ``_launch()``, which is the bypass that hid the defect. Both surfaces
are asserted together in every case, because the requirement is that the button
and the shell action agree rather than that either one works alone.
"""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtTest = pytest.importorskip("PySide6.QtTest")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QApplication = QtWidgets.QApplication
QTest = QtTest.QTest

from tools.webfoot.workbench import launcher as launcher_module  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    yield QApplication.instance() or QApplication([])


@pytest.fixture
def window(qapp, tmp_path, monkeypatch):
    """A real shell whose session has no successful build behind it."""
    from tools.webfoot.profile import RomProfileCatalog

    # A launch persists the mGBA path; keep that out of the real user config.
    monkeypatch.setenv("WEBFOOT_WORKBENCH_CONFIG_DIR", str(tmp_path / "config"))
    session = Session()
    assert session.last_build is None, "precondition: no build has happened"
    window = MainWindow(session, RomProfileCatalog.load("config/roms.yaml"))
    window.resize(1440, 900)
    window._launcher.on_session_changed()  # the session synchronization
    window._refresh_action_state()
    yield window
    window.close()


def pick(surface, monkeypatch, path) -> None:
    """Invoke the real picker slot with the file chooser answered."""
    monkeypatch.setattr(
        launcher_module.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )
    surface._pick_rom()


def armable(window) -> tuple[bool, bool]:
    """(the visible Launch button, the shell Ctrl+R action) enablement."""
    return (
        window._launcher._launch_button.isEnabled(),
        window._action_run.isEnabled(),
    )


def _rom(tmp_path, name: str = "picked.gba"):
    path = tmp_path / name
    path.write_bytes(b"\x00" * 32)
    return path


def _mgba(tmp_path):
    exe = tmp_path / "mgba.exe"
    exe.write_text("", encoding="utf-8")
    return exe


# -- the confirmed defect ---------------------------------------------------


def test_choosing_a_rom_arms_the_button_and_the_run_action(window, tmp_path, monkeypatch):
    """RED at the baseline: the picker wrote the field and armed nothing."""
    surface = window._launcher
    rom = _rom(tmp_path)

    assert armable(window) == (False, False), "precondition: nothing to launch"

    pick(surface, monkeypatch, rom)

    assert surface._rom_field.text() == str(rom), "the chosen path stays displayed"
    assert armable(window) == (True, True), "button and Ctrl+R action agree"


def test_the_run_action_launches_the_rom_the_picker_chose(window, tmp_path, monkeypatch):
    """The Ctrl+R / Tools -> Run path reaches the launcher with the picked ROM."""
    surface = window._launcher
    rom = _rom(tmp_path)
    exe = _mgba(tmp_path)
    launched: dict = {}
    monkeypatch.setattr(
        launcher_module.subprocess,
        "Popen",
        lambda args, *a, **k: launched.setdefault("args", args),
    )
    pick(surface, monkeypatch, rom)
    surface._mgba_field.setText(str(exe))

    window._action_run.trigger()

    assert launched["args"] == [str(exe), str(rom)]


def test_the_launch_button_launches_the_rom_the_picker_chose(window, tmp_path, monkeypatch):
    """The visible button reaches the same launcher with the same ROM."""
    surface = window._launcher
    rom = _rom(tmp_path)
    exe = _mgba(tmp_path)
    launched: dict = {}
    monkeypatch.setattr(
        launcher_module.subprocess,
        "Popen",
        lambda args, *a, **k: launched.setdefault("args", args),
    )
    pick(surface, monkeypatch, rom)
    surface._mgba_field.setText(str(exe))

    surface._launch_button.click()

    assert launched["args"] == [str(exe), str(rom)]


# -- negative controls ------------------------------------------------------


def test_cancelling_the_picker_arms_nothing(window, monkeypatch):
    surface = window._launcher
    assert armable(window) == (False, False)

    monkeypatch.setattr(
        launcher_module.QFileDialog, "getOpenFileName", lambda *a, **k: ("", "")
    )
    surface._pick_rom()

    assert surface._rom_field.text() == ""
    assert armable(window) == (False, False), "a cancelled pick arms nothing"


def test_clearing_the_chosen_rom_disarms_both(window, tmp_path, monkeypatch):
    surface = window._launcher
    pick(surface, monkeypatch, _rom(tmp_path))
    assert armable(window) == (True, True)

    surface._rom_field.setText("")

    assert armable(window) == (False, False), "an emptied field is not launchable"


def test_a_session_change_clears_the_manual_rom_and_disarms_both(
    window, tmp_path, monkeypatch
):
    """A project change keeps clearing a manual ROM; both surfaces follow it."""
    surface = window._launcher
    pick(surface, monkeypatch, _rom(tmp_path))
    assert armable(window) == (True, True)

    window._on_project_changed()

    assert surface._rom_field.text() == "", "the design clears a manual ROM here"
    assert armable(window) == (False, False)


# -- the launch debounce ----------------------------------------------------
#
# A successful launch disables the button for `_DEBOUNCE_MS` so a double click
# cannot spawn twice. That timer outlives the click, so it can fire after the
# ROM field has changed underneath it. Both cases run the real timer.


def test_the_debounce_does_not_re_arm_a_rom_cleared_inside_its_window(
    window, tmp_path, monkeypatch
):
    """RED at 61807558: the timer re-enabled the button unconditionally."""
    surface = window._launcher
    monkeypatch.setattr(launcher_module.subprocess, "Popen", lambda *a, **k: None)
    pick(surface, monkeypatch, _rom(tmp_path))
    surface._mgba_field.setText(str(_mgba(tmp_path)))

    window._action_run.trigger()  # the real launch; the button is debounced
    assert surface._launch_button.isEnabled() is False, "precondition: debounced"

    surface._rom_field.setText("")  # cleared inside the debounce window
    assert armable(window) == (False, False)

    QTest.qWait(launcher_module._DEBOUNCE_MS + 150)

    assert armable(window) == (False, False), "the debounce resurrected a cleared ROM"


def test_the_debounce_re_arms_a_rom_left_intact(window, tmp_path, monkeypatch):
    """Positive control in the same window: the timer still re-arms."""
    surface = window._launcher
    monkeypatch.setattr(launcher_module.subprocess, "Popen", lambda *a, **k: None)
    pick(surface, monkeypatch, _rom(tmp_path))
    surface._mgba_field.setText(str(_mgba(tmp_path)))

    window._action_run.trigger()
    assert surface._launch_button.isEnabled() is False, "precondition: debounced"

    QTest.qWait(launcher_module._DEBOUNCE_MS + 150)

    assert armable(window) == (True, True)


def test_a_build_still_arms_the_normal_run_path(window, tmp_path):
    surface = window._launcher
    built = _rom(tmp_path, "built.gba")
    assert armable(window) == (False, False)

    # The launcher reads only `output_path` from the session's last build.
    window._session.last_build = SimpleNamespace(output_path=built)
    window._on_build_finished()  # the real buildFinished handler

    assert surface._rom_field.text() == str(built)
    assert armable(window) == (True, True)
