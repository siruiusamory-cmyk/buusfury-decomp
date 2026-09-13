"""T1.4 headless GUI smoke test for the workbench `MainWindow`.

Proves the window constructs and the tab-enable contract holds: four tabs in
order, only Atlas (0) enabled, Inspector/Build/Launch (1-3) disabled until a ROM
is open. Needs no ROM and no tmp dir - construction alone exercises the contract.

Offscreen Qt is set BEFORE PySide6 is imported; the whole module skips cleanly
if PySide6 (or the offscreen plugin) is unavailable, so CI without Qt does not
error.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Skip the module if PySide6 or the offscreen platform plugin can't init.
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
from tools.webfoot.profile import RomProfileCatalog  # noqa: E402
from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    # Singleton-safe: reuse the process-wide QApplication if one exists.
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


def test_mainwindow_tab_enable_contract(qapp) -> None:
    catalog = RomProfileCatalog.load("config/roms.yaml")
    window = MainWindow(Session(), catalog)

    tabs = window.findChild(QtWidgets.QTabWidget)
    assert tabs is not None
    assert tabs.count() == 4
    assert tabs.isTabEnabled(0)  # Atlas
    for index in (1, 2, 3):  # Inspector, Build, Launch
        assert not tabs.isTabEnabled(index)
