"""Editor destinations and the container the shell drives them through.

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`, human correction: the shell must read
like a ROM editor — **menu bar -> one compact strip -> active editor workspace ->
editor-local modes** — not like a tab strip listing every implementation panel.

Two consequences live here:

- :class:`EditorHost` wraps one editor surface so the shell has a single way to
  reach it (show it, ask for its undo stack, ask for its status line) without
  knowing which class it is.
- :class:`MapsEditor` is the **one** Maps destination. Browsing a map's layout,
  editing that layout's chunk cells, authoring a map's placements and retargeting
  the map's own connections are four modes of one editor, exactly as Porymap keeps
  Map / Events / Header / Connections inside one window with a tab bar rather than
  opening four windows. Every pre-existing map widget is mounted unchanged; only
  the mode switch that chooses between them is new.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from . import theme
from .map_browser_tab import MapBrowserTab
from .map_tab import MapWorkspaceTab
from .warp_tab import WarpTab
from .widgets import ToolStrip

#: Maps mode name -> one line saying what that mode is for. The wording uses the
#: product's own nouns; none of it is invented capability.
_MAP_MODES = (
    (
        "browse",
        "Browse",
        "Inspect any map's rendered layout, its layers and its record, without editing.",
    ),
    (
        "layout",
        "Layout",
        "Reassign one 256x256 chunk cell of a supported map to another chunk the "
        "same layer already uses, then Save As a new ROM.",
    ),
    (
        "objects",
        "Objects",
        "Inspect and author the placements a map contains: move them, clone one into "
        "a named authored NPC, and open its detailed editor.",
    ),
    (
        "warps",
        "Warps",
        "Retarget this map's existing connections: where each one leads, where the "
        "player arrives and which way they face, written to maps/transitions.toml.",
    ),
)


class EditorHost(QWidget):
    """One editor destination: a mode strip, then the editor that mode shows.

    Exists so the shell never has to know whether an editor is a plain widget or a
    composite, and so a tab's status line and undo stack are reachable the same
    way from every editor. An editor that owns internal modes *subclasses* this
    (:class:`MapsEditor`) or sets :meth:`set_content`, so the shell never wraps a
    host around a host - which is how the Maps editor's own status line ended up
    one level too deep for the shell to find.
    """

    def __init__(self, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._name = name
        self._content: QWidget | None = None
        self._status_label: QLabel | None = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def name(self) -> str:
        return self._name

    def set_content(self, widget: QWidget) -> None:
        """Adopt `widget` as this host's editor, keeping the host's status line.

        A composite editor built from another editor re-parents it here rather than
        creating a second host, and hands its own status label up via
        :meth:`set_status_label` so the shell always draws the right one.
        """
        self._content = widget
        self._layout.addWidget(widget, 1)

    def content(self) -> QWidget | None:
        return self._content

    def signal_source(self) -> QWidget:
        """The widget that owns this editor's own signals and mode controls.

        For a plain host that is the editor it wraps; for a composite editor that
        is itself - so a caller can reach "the thing with `romOpened`" or "the
        thing with `set_mode`" without knowing which kind it has.
        """
        return self._content if self._content is not None else self

    def add_surface(self, widget: QWidget) -> None:
        """Adopt `widget` as this host's editor.

        A surface that publishes status on demand is handed this host, so it can
        reach the one status holder without knowing how the shell is wired. The
        attribute is set only when the surface declares it, so a surface with no
        status of its own is unaffected.
        """
        if self._content is None:
            self._content = widget
        if hasattr(widget, "_host"):
            widget._host = self
        self._layout.addWidget(widget, 1)

    #: A host may publish its status line on demand, for an editor that keeps a
    #: status holder the shell mirrors rather than a label it renders itself.
    statusChanged = Signal(str)

    def set_status_label(self, label: QLabel | None) -> None:
        """Record the label this editor maintains as its own status line."""
        self._status_label = label

    def set_status_text(self, text: str) -> None:
        """Set this editor's status holder and publish it for the shell.

        An editor whose holder is not drawn (Atlas) must still reach the bar, or a
        message written while that editor is already on screen never arrives: the
        shell copies the holder at mount time and thereafter only on a signal.
        """
        if self._status_label is not None:
            self._status_label.setText(text)
        self.statusChanged.emit(text)

    def status_label(self) -> QLabel | None:
        return self._status_label

    def status_line(self) -> str:
        """This editor's current one-line status, or "" when it has none.

        The shell owns ONE status label and copies this text into it. Re-parenting
        each editor's own label into the bar instead looked tidier but made the
        bar's contents depend on mount order, which showed a hidden editor's line
        beside the visible one's.

        Read from the DECLARED label rather than from ``self._status_label`` alone,
        because a composite editor republishes on its own `statusChanged` while the
        label it declares is the one that actually holds the line.
        """
        label = self._status_label
        if label is None:
            label = getattr(self.signal_source(), "_status", None)
        return label.text() if label is not None else ""

    def undo_stack(self):
        """The active editor's undo stack, or None when it has none.

        The shell routes Edit-menu Undo/Redo here rather than inventing a second
        history. Two editors keep real stacks today (the placement workspace and
        the palette editor); the rest answer None.
        """
        return None


class MapsEditor(EditorHost):
    """The one Maps editor: Browse, Layout, Objects and Warps as internal modes."""

    #: Forwarded from the placement workspace when a user asks for the Scene editor.
    openSceneRequested = Signal(str, str)
    #: Forwarded from the placement workspace's Build & Run button.
    buildRunRequested = Signal()
    #: Any of the four modes changed the project.
    projectChanged = Signal()
    #: The active mode's own status line, republished for the shell. This is the
    #: base host's `statusChanged`, inherited rather than redeclared: shadowing it
    #: would create a second signal that callers connected to the base one would
    #: never receive.
    #: The pending layout-edit count changed; the shell shows it too.
    dirtyChanged = Signal()
    #: The mode changed, which changes whose undo stack the shell should route to.
    modeChanged = Signal(str)

    def unsaved_edit_count(self) -> int:
        """Pending layout edits no Save As has written yet, across every mode."""
        return self.browser.unsaved_edit_count()

    def __init__(self, session, parent: QWidget | None = None) -> None:
        super().__init__("Maps", parent)

        self.browser = MapBrowserTab(session)
        # The mode strip owns mode selection for this editor, so the browser stops
        # drawing its own Edit Layout toggle: one action, one control.
        self.browser.set_modes_owned_by_host(True)
        self.workspace = MapWorkspaceTab(session)
        self.warps = WarpTab(session)

        self._buttons: dict[str, QToolButton] = {}
        strip = ToolStrip()
        strip.add_label("Mode")
        for key, label, hint in _MAP_MODES:
            button = QToolButton()
            button.setText(label)
            button.setCheckable(True)
            button.setAutoRaise(True)
            button.setToolTip(hint)
            button.setAccessibleName(f"{label} mode")
            button.clicked.connect(lambda _checked=False, target=key: self.set_mode(target))
            self._buttons[key] = button
            strip.add(button)
        strip.add_separator()
        strip.add_stretch()
        self._mode_strip = strip

        self._stack = QStackedWidget()
        self._stack.addWidget(self.browser)
        self._stack.addWidget(self.workspace)
        self._stack.addWidget(self.warps)

        self._layout.addWidget(strip)
        self._layout.addWidget(self._stack, 1)

        self.browser.projectChanged.connect(self.projectChanged)
        self.browser.dirtyChanged.connect(self.dirtyChanged)
        self.workspace.projectChanged.connect(self.projectChanged)
        self.workspace.openSceneRequested.connect(self.openSceneRequested)
        self.workspace.buildRunRequested.connect(self.buildRunRequested)
        self.warps.projectChanged.connect(self.projectChanged)
        self.warps.dirtyChanged.connect(self._on_warps_dirty)

        self.set_status_label(self.browser._status)
        self.browser.statusChanged.connect(self._on_browser_status)
        self.workspace.statusChanged.connect(self._on_workspace_status)
        self.warps.statusChanged.connect(self._on_warps_status)
        #: Which surface publishes this editor's line right now. The three surfaces
        #: share one signal, so the label that counts is the active one's.
        self._status_source = "browser"

        self._mode = "browse"
        self.set_mode("browse")

    # -- modes ----------------------------------------------------------------

    def set_mode(self, key: str) -> None:
        """Show one map mode. Never changes what any mode can do."""
        if key not in self._buttons:
            return
        self._mode = key
        for name, button in self._buttons.items():
            button.setChecked(name == key)
        self._stack.setCurrentWidget(
            self.workspace
            if key == "objects"
            else self.warps
            if key == "warps"
            else self.browser
        )
        if key == "layout":
            self.browser.enter_edit_layout()
        elif key == "browse":
            self.browser.leave_edit_layout()
        elif key == "warps":
            self.warps.refresh()
        # The status line belongs to whichever mode is on screen.
        label = (
            self.workspace._status
            if key == "objects"
            else self.warps._status
            if key == "warps"
            else self.browser._status
        )
        self.set_status_label(label)
        self._status_source = (
            "workspace" if key == "objects" else "warps" if key == "warps" else "browser"
        )
        # Ask the mode that just became visible to restate itself. Without this the
        # label kept whatever it said the last time that same mode was active, so
        # switching Layout -> Objects -> Browse could show the placement editor's
        # readout while the map browser was on screen.
        if key == "objects":
            self.workspace.restate_status()
        elif key == "warps":
            self.warps.restate_status()
        else:
            self.browser._refresh_editor_state()
        self.statusChanged.emit(label.text())
        self.modeChanged.emit(key)

    def mode(self) -> str:
        return self._mode

    def mode_buttons(self) -> dict[str, QToolButton]:
        return self._buttons

    @staticmethod
    def _mode_hint(key: str) -> str:
        return {
            "browse": "Read-only: every map renders, nothing is edited.",
            "layout": "",
            "objects": "",
            "warps": "",
        }.get(key, "")

    # -- status forwarding ----------------------------------------------------

    def _on_browser_status(self, text: str) -> None:
        if self._status_source == "browser":
            self.statusChanged.emit(text)

    def _on_workspace_status(self, text: str) -> None:
        if self._status_source == "workspace":
            self.statusChanged.emit(text)

    def _on_warps_status(self, text: str) -> None:
        if self._status_source == "warps":
            self.statusChanged.emit(text)

    def _on_warps_dirty(self) -> None:
        self.dirtyChanged.emit()

    # -- capabilities the shell needs ----------------------------------------

    def on_session_changed(self) -> None:
        """A different image: reset every mode, then follow them to a true mode.

        The browser deliberately returns to view mode for an image it has not
        judged, the workspace drops a history that described the replaced map
        corpus, and the Warps surface drops its staged connection edits - they name
        records of the image that is gone. The strip is the one statement of which
        mode is active, so it cannot be left checked on Layout - a mode the editor
        is no longer in. Browse is the mode that matches what is on screen.
        Objects and Warps are kept: their corpora are re-read from the new image and
        the mode is still honoured.
        """
        self.browser.on_session_changed()
        self.workspace.on_session_changed()
        self.warps.on_session_changed()
        self.set_mode("browse" if self._mode == "layout" else self._mode)

    def on_project_mutated(self) -> None:
        """A project mutation: keep every mode's staged state, re-assert the mode.

        CQA-05. None of the staged surfaces is project-derived - the layout session
        is built from the open image's bytes, the placement history holds semantic
        positions the project still has, and the Warps drafts name transitions the
        project still has a place for - so this event must refresh what the project
        *can* change without discarding what the user staged.

        The mode is re-asserted afterwards so the strip and the editor it names
        cannot disagree. The strip is the one statement of which mode is active,
        so it is re-applied to the editor from ``self._mode`` rather than the
        editor being allowed to drift into a state the strip would misdescribe.
        """
        self.browser.on_project_mutated()
        self.workspace.on_project_mutated()
        self.warps.on_project_mutated()
        self.set_mode(self._mode)

    def build_run_requested(self) -> None:
        self.buildRunRequested.emit()

    def select_placement(self, map_id: str, placement_identity: str) -> None:
        self.set_mode("objects")
        self.workspace.select_placement(map_id, placement_identity)

    def undo_stack(self):
        """The ACTIVE mode's history, so Edit -> Undo answers what is on screen.

        Browse and Layout stage into the browser's own stack, Objects into the
        placement workspace's, and Warps into the new connection editor's; routing
        by mode is what keeps one Ctrl+Z from reaching a hidden surface's history.
        """
        if self._mode == "warps":
            return self.warps.undo_stack()
        if self._mode == "objects":
            return self.workspace._undo_stack
        return self.browser._undo_stack
