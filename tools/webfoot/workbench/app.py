"""WORKBENCH-001 GUI shell.

`MainWindow` is a thin QMainWindow holding a QTabWidget with the four tabs -
Atlas, Inspector, Build, Launch - in that order. It holds the shared `Session`
and the ROM profile catalog by constructor injection (no global state) and hands
them to whatever tab content is mounted; Wave 2 replaces the stub placeholders
with the real tab widgets.

The locked UX (the maintainer): no toolbar, no menu bar, no status bar, no docks. Only the
Atlas tab (0) is enabled at launch; Inspector/Build/Launch (1-3) are disabled
until a ROM is open. This shell holds no ROM-format knowledge - no offsets, masks
or record constants; that all lives behind the SDK the Session calls.
"""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from ..profile import RomProfileCatalog
from .atlas_browser import AtlasBrowserTab
from .build_panel import BuildPanelTab
from .inspector import InspectorTab
from .launcher import LauncherTab
from .session import Session

# Tab order is the contract; Wave 2 mounts real content at these indices.
_TAB_TITLES = ("Atlas", "Inspector", "Build", "Launch")
_POST_ROM_TABS = (1, 2, 3)  # enabled only once a ROM is open


class MainWindow(QMainWindow):
    def __init__(self, session: Session, catalog: RomProfileCatalog) -> None:
        super().__init__()
        self._session = session
        self._catalog = catalog

        self.setWindowTitle("Webfoot Workbench")

        self._tabs = QTabWidget()
        self._atlas = AtlasBrowserTab(session, catalog)
        self._inspector = InspectorTab()
        self._build = BuildPanelTab(session, catalog)
        self._launcher = LauncherTab(session)
        self._tabs.addTab(self._atlas, _TAB_TITLES[0])
        self._tabs.addTab(self._inspector, _TAB_TITLES[1])
        self._tabs.addTab(self._build, _TAB_TITLES[2])
        self._tabs.addTab(self._launcher, _TAB_TITLES[3])
        for index in _POST_ROM_TABS:
            self._tabs.setTabEnabled(index, False)

        self._atlas.romOpened.connect(self._enable_post_rom_tabs)
        self._atlas.romOpened.connect(self._build.on_session_changed)
        self._atlas.resultActivated.connect(self._on_result_activated)
        self._build.buildFinished.connect(self._launcher.on_session_changed)

        self.setCentralWidget(self._tabs)

    def _on_result_activated(self, result: dict) -> None:
        self._session.selected_result = result
        self._inspector.show_result(result)
        self._tabs.setCurrentIndex(1)

    def _enable_post_rom_tabs(self) -> None:
        """Enable Inspector/Build/Launch. Wave 2 calls this after `open_rom`."""
        for index in _POST_ROM_TABS:
            self._tabs.setTabEnabled(index, True)
