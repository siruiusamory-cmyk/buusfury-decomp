"""WORKBENCH-005 Layer 2 - the DragonByte Z Graphics workspace.

A visual game-content tab: SEE the game's real decoded sprites, select one,
inspect who uses it, step its animations, and recolour the shared object palette.
It is a THIN client - every pixel, dimension, backlink, animation and colour
comes from the `ActorSprites` SDK facade (`tools/webfoot/graphics.py`); this
widget computes no ROM-format value. Colour is never packed here (the SDK owns
RGB->GBA-word packing via `plan_palette_entry_rgb`, applied at build); a recolour
is recorded through the project + `session.project_mutated()`, exactly the way
the Inspector records a dialogue edit.

Desktop patterns adopted (the maintainer's DragonByte Z correction, not the old plain-UX
rule): a QSplitter between the thumbnail grid and the selected-asset inspector,
a contextual animation toolbar (prev/next + animation chooser), palette
Apply/Revert buttons, and a status line (selected asset, dimensions, shared
flag, validation/build currency). No IDE docking framework, no property-grid DSL.

The one rule that has bitten this project twice: every slot that calls the SDK
catches the exception family PARENTS - `GraphicsError`, `SpriteFormatError`,
`PngError` (three distinct families under `ValueError`) plus `ProjectError`/
`OSError` on project writes - so a failure becomes a QMessageBox, never a
dead-looking click or a terminal traceback (see references/error-handling.md).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QImage,
    QKeySequence,
    QPixmap,
    QUndoCommand,
    QUndoStack,
    qRgb,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .. import graphics as graphics_sdk
from ..formats.indexed_png import PngError
from ..formats.sprite_graphics import SpriteFormatError
from ..graphics import CharacterIdentity, GraphicIdentity, GraphicsError
from ..project import ProjectError
from .session import Session

#: The SDK exception families a Graphics slot must catch at its boundary. All
#: three are `ValueError` subclasses but sit in different families, so a lone
#: leaf leaves siblings uncaught (references/error-handling.md).
_SDK_ERRORS = (GraphicsError, SpriteFormatError, PngError)

_THUMB = 64  # icon-grid thumbnail edge, px
_PREVIEW_MIN = 320  # selected/animation preview min edge, px (was 160/120)
_SWATCH = 22  # palette swatch edge, px
_SWATCH_COLUMNS = 16  # 16x16 grid renders the 256-entry object palette
_IDENTITY_ROLE = Qt.ItemDataRole.UserRole
_PALETTE_CMD_ID = 0xB005  # shared id() so palette recolours can merge (WB-005 L3)


class PaletteRecolourCommand(QUndoCommand):
    """One undoable palette Apply: a batch of per-index recolours.

    Undo is SEMANTIC, never a byte write. For each index the command captures
    the NEW rgb and the PRIOR project state read from
    `graphics_sdk.get_palette_override` at construction time: either the prior
    override rgb, or None meaning "unauthored, so undo must REMOVE the override"
    (`remove_palette_override`). `redo()` runs on the first `stack.push()` too,
    so the SDK write and the tab refresh both live in `redo()`; `undo()` reverses
    each index to its captured prior state and refreshes the same way.

    Merging (see `mergeWith`): consecutive commands whose index-set is IDENTICAL
    collapse into one history entry, keeping the ORIGINAL prior-state and
    adopting the LATEST new rgb. Different index-sets do not merge.

    The first `redo()` that `QUndoStack.push()` fires is a no-op write: the apply
    is performed and validated in `_on_apply` BEFORE the push, because a Python
    exception raised inside `redo()` does not propagate cleanly through Qt's C++
    `push()` - PySide6 swallows it into a generic warning AND still records the
    failed command, corrupting the stack (verified). Applying before push and
    skipping the first redo keeps the failure path in `_on_apply`'s own guard,
    so a bad edit is surfaced and NOTHING is pushed. A later redo (after an undo)
    re-applies for real, since by then the edit is known-good.
    """

    def __init__(
        self,
        tab: "GraphicsTab",
        new_rgb: dict[int, tuple[int, int, int]],
        prior: dict[int, tuple[int, int, int] | None],
    ):
        indices = sorted(new_rgb)
        super().__init__(f"Recolour palette {', '.join(str(i) for i in indices)}")
        self._tab = tab
        self._new: dict[int, tuple[int, int, int]] = dict(new_rgb)
        # Prior state per index: rgb tuple, or None meaning "no override, undo
        # must remove". Captured in `_on_apply` before the pre-push write.
        self._prior: dict[int, tuple[int, int, int] | None] = dict(prior)
        # The apply already ran before push; the push-driven first redo skips it.
        self._applied = True

    def id(self) -> int:
        return _PALETTE_CMD_ID

    def redo(self) -> None:
        if self._applied:
            # First redo, fired by push(): the write already happened in
            # _on_apply, which also refreshed. Consume the flag, do nothing.
            self._applied = False
            return
        for index in sorted(self._new):
            r, g, b = self._new[index]
            self._tab._write_override(index, r, g, b)
        self._tab._after_undo_redo()

    def undo(self) -> None:
        for index in sorted(self._prior):
            prior = self._prior[index]
            if prior is None:
                self._tab._clear_override(index)
            else:
                self._tab._write_override(index, *prior)
        self._tab._after_undo_redo()

    def mergeWith(self, other: QUndoCommand) -> bool:
        if not isinstance(other, PaletteRecolourCommand):
            return False
        if set(self._new) != set(other._new):
            return False  # different index-set: keep as two entries
        # Same gesture on the same swatches: keep our original prior-state,
        # adopt the later new rgb, so a single undo restores the original.
        self._new.update(other._new)
        return True


def indexed_pixmap(pixels: bytes, width: int, height: int, rgb) -> QPixmap:
    """Build a QPixmap from linear 8-bit indexed pixels + an RGB colour table.

    `rgb` is the SDK's `palette.rgb` (256 (r,g,b) triples). Uses
    `QImage.Format_Indexed8` with `setColorTable`, the idiomatic Qt path for
    indexed art. The QImage does not own the buffer it is handed, so the result
    is `.copy()`d to a standalone image before making the pixmap - otherwise the
    pixels could be freed underneath it. No ROM-format math: this only maps an
    index to a display colour the SDK already computed.
    """
    colour_table = [qRgb(r, g, b) for (r, g, b) in rgb]
    # bytesPerLine == width: the SDK yields a tightly packed, unpadded buffer.
    image = QImage(bytes(pixels), width, height, width, QImage.Format.Format_Indexed8)
    image.setColorTable(colour_table)
    return QPixmap.fromImage(image.copy())


class GraphicsTab(QWidget):
    """Browse decoded sprites, inspect one, step animations, recolour palette."""

    projectChanged = Signal()  # emitted on a committed palette edit

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._session = session
        self._selected: GraphicIdentity | None = None
        self._pixmap_cache: dict[GraphicIdentity, QPixmap] = {}
        # Animation stepper state for the selected character.
        self._anim_character: CharacterIdentity | None = None
        self._animations: tuple = ()
        self._anim_index = 0
        self._frame_index = 0
        # Palette editor state: index -> pending (r,g,b) not yet applied.
        self._palette_pending: dict[int, tuple[int, int, int]] = {}
        # Swatches keyed by their TRUE global palette index, so the scoped view
        # (a subset of indices) and _pick_colour both address the real index.
        self._swatches: dict[int, QFrame] = {}
        # The distinct palette indices the selected sprite's pixels reference
        # (set(graphic.pixels)); None until a sprite is selected. NOT a palette
        # bank - just the colours this sprite's pixels actually address.
        self._used_indices: set[int] | None = None
        # WB-005 Layer 3: one undo history for the visual palette mutations this
        # tab commits. Established here; other editors migrate in later tickets.
        self._undo_stack = QUndoStack(self)

        # -- A. Asset browser (thumbnail grid) --------------------------------
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter by numeric identity (e.g. 413)")
        self._search.textChanged.connect(self._apply_filter)

        self._grid = QListWidget()
        self._grid.setViewMode(QListWidget.ViewMode.IconMode)
        self._grid.setIconSize(QSize(_THUMB, _THUMB))
        self._grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._grid.setMovement(QListWidget.Movement.Static)
        self._grid.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._grid.setSpacing(6)
        self._grid.currentItemChanged.connect(self._on_grid_selection)
        # WB-005 L4/L5: thumbnails decode lazily so opening a 7k-sprite ROM shows
        # the window at once instead of freezing on an eager full-corpus decode.
        # Scroll fills newly-visible rows early (valueChanged AND rangeChanged, so
        # a resize/relayout that shifts the range fires too); completeness does not
        # rely on that fragile viewport-visibility sampling, though - after populate
        # a chained-singleShot batch DRAIN icons every not-yet-decoded item a few at
        # a time, yielding to the event loop between batches (no thread, no freeze),
        # so no on-screen cell is ever left permanently blank (WB-005 missing-thumbs).
        self._grid.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._grid.verticalScrollBar().rangeChanged.connect(self._on_scroll)
        # Guards the chained drain so overlapping populate calls do not double-run it.
        self._drain_active = False

        browser = QWidget()
        browser_layout = QVBoxLayout(browser)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.addWidget(self._search)
        browser_layout.addWidget(self._grid, 1)

        # -- B. Selected-asset inspector --------------------------------------
        self._preview = QLabel("Select a sprite.")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setMinimumSize(_PREVIEW_MIN, _PREVIEW_MIN)
        self._preview.setFrameShape(QFrame.Shape.StyledPanel)
        self._dims = QLabel("—")
        self._shared = QLabel("—")
        self._consumers = QLabel("—")
        self._consumers.setWordWrap(True)
        self._characters = QLabel("—")
        self._characters.setWordWrap(True)
        info_box = QGroupBox("Selected asset")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(self._preview, 1)
        info_layout.addWidget(self._dims)
        info_layout.addWidget(self._shared)
        info_layout.addWidget(QLabel("Used by frames:"))
        info_layout.addWidget(self._consumers)
        info_layout.addWidget(QLabel("Characters:"))
        info_layout.addWidget(self._characters)
        # Export the selected sprite to an indexed PNG. Disabled until a sprite
        # is selected; the SDK façade (never a codec import here) does the encode.
        self._export = QPushButton("Export PNG…")
        self._export.setEnabled(False)
        self._export.clicked.connect(self._on_export)
        info_layout.addWidget(self._export)

        # -- C. Animation frame viewer ----------------------------------------
        self._anim_select = QListWidget()
        self._anim_select.setMaximumHeight(90)
        self._anim_select.currentRowChanged.connect(self._on_animation_chosen)
        self._anim_preview = QLabel("No character selected.")
        self._anim_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._anim_preview.setMinimumSize(_PREVIEW_MIN, _PREVIEW_MIN)
        self._anim_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self._frame_label = QLabel("—")
        self._prev_frame = QPushButton("◀ Prev")
        self._prev_frame.clicked.connect(lambda: self._step_frame(-1))
        self._next_frame = QPushButton("Next ▶")
        self._next_frame.clicked.connect(lambda: self._step_frame(1))
        # Timing is UNKNOWN per the SDK; a stepper only, never a playback speed.
        self._timing_note = QLabel("Frame timing is not recorded by the ROM; step manually.")
        self._timing_note.setWordWrap(True)
        anim_toolbar = QHBoxLayout()
        anim_toolbar.addWidget(self._prev_frame)
        anim_toolbar.addWidget(self._frame_label, 1)
        anim_toolbar.addWidget(self._next_frame)
        anim_box = QGroupBox("Animations")
        anim_layout = QVBoxLayout(anim_box)
        anim_layout.addWidget(self._anim_select)
        anim_layout.addWidget(self._anim_preview, 1)
        anim_layout.addLayout(anim_toolbar)
        anim_layout.addWidget(self._timing_note)

        inspector = QWidget()
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.setContentsMargins(0, 0, 0, 0)
        inspector_layout.addWidget(info_box, 1)
        inspector_layout.addWidget(anim_box, 1)

        # -- D. Palette editor -------------------------------------------------
        # Scope toggle: default-on so a selected sprite shows only the colours it
        # uses. Honest wording only - these are the indices the sprite's pixels
        # reference, NOT a proven per-sprite hardware palette bank.
        self._scope_used = QCheckBox("Show only colours used by this sprite")
        self._scope_used.setChecked(True)
        self._scope_used.toggled.connect(self._repaint_palette)
        self._scope_caption = QLabel(
            "The object palette is shared across sprites; per-sprite palette "
            "banks are not yet resolved (a later ticket)."
        )
        self._scope_caption.setWordWrap(True)
        self._scope_header = QLabel("Full palette.")
        self._scope_header.setWordWrap(True)
        self._palette_grid = QGridLayout()
        self._palette_grid.setSpacing(2)
        palette_holder = QWidget()
        palette_holder.setLayout(self._palette_grid)
        self._apply = QPushButton("Apply recolour")
        self._apply.setEnabled(False)
        self._apply.clicked.connect(self._on_apply)
        self._revert = QPushButton("Revert unapplied")
        self._revert.setEnabled(False)
        self._revert.clicked.connect(self._on_revert)
        # E. Pending change surfaced in game language, never as a raw write.
        self._pending_label = QLabel("No pending palette change.")
        self._pending_label.setWordWrap(True)
        # Undo/Redo actions from the stack: keyboard-enabled (Ctrl+Z/Ctrl+Y) and
        # surfaced as toolbar buttons. Each button uses setDefaultAction so its
        # enabled-state/text mirror the action automatically - no manual sync
        # lambda (one such lambda outlived the C++ stack and crashed teardown).
        # Scoped to this tab per WB-005 §8 (no app-wide menu retrofit this ticket).
        self._undo_action = self._undo_stack.createUndoAction(self, "Undo")
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._redo_action = self._undo_stack.createRedoAction(self, "Redo")
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._undo_button = QPushButton("Undo")
        self._undo_button.clicked.connect(self._undo_action.trigger)
        self._undo_button.setEnabled(self._undo_stack.canUndo())
        self._redo_button = QPushButton("Redo")
        self._redo_button.clicked.connect(self._redo_action.trigger)
        self._redo_button.setEnabled(self._undo_stack.canRedo())
        # Drive enabled-state from the stack's own signals into the button's C++
        # setEnabled slot directly (no Python closure over the stack, so nothing
        # dangles at teardown - the earlier lambda over the stack crashed there).
        self._undo_stack.canUndoChanged.connect(self._undo_button.setEnabled)
        self._undo_stack.canRedoChanged.connect(self._redo_button.setEnabled)
        self.addAction(self._undo_action)
        self.addAction(self._redo_action)

        palette_buttons = QHBoxLayout()
        palette_buttons.addWidget(self._apply)
        palette_buttons.addWidget(self._revert)
        palette_buttons.addWidget(self._undo_button)
        palette_buttons.addWidget(self._redo_button)
        palette_box = QGroupBox("Object palette (click a swatch to recolour)")
        palette_layout = QVBoxLayout(palette_box)
        palette_layout.addWidget(self._scope_used)
        palette_layout.addWidget(self._scope_header)
        palette_layout.addWidget(self._scope_caption)
        palette_layout.addWidget(palette_holder)
        palette_layout.addLayout(palette_buttons)
        palette_layout.addWidget(self._pending_label)

        # -- Layout: splitter (browser | inspector) over palette + status -----
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(browser)
        splitter.addWidget(inspector)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self._status = QLabel("Open a ROM to load its sprites.")

        root = QVBoxLayout(self)
        root.addWidget(splitter, 3)
        root.addWidget(palette_box, 2)
        root.addWidget(self._status)

    # -- session wiring -------------------------------------------------------

    def on_session_changed(self) -> None:
        """Re-populate from the session (ROM open, project change, edit)."""
        self._pixmap_cache.clear()
        self._populate_grid()
        self._populate_palette(clear_pending=True)
        self._update_status()

    def _sprites(self):
        """The corpus, catching the SDK family so a bad profile is not a crash."""
        try:
            return self._session.sprites
        except _SDK_ERRORS as exc:  # defensive: the accessor already swallows it
            QMessageBox.critical(self, "Graphics", str(exc))
            return None

    def _effective_rgb(self, sprites) -> list[tuple[int, int, int]]:
        """Canonical ROM palette with every COMMITTED override overlaid.

        Display must reflect what the built ROM would show: the canonical colour
        for an unauthored index, the authored colour where a recolour is
        committed. This is a pure tuple copy + dict overlay - no ROM-format math;
        the override map is loaded ONCE (not per index) via the SDK. A missing
        project (or an SDK read failure) just yields the canonical palette.
        """
        rgb = list(sprites.palette.rgb)
        profile = self._session.profile
        if self._session.project_dir is None or profile is None:
            return rgb
        try:
            overrides = graphics_sdk.get_palette_overrides(
                self._session.project_dir, profile
            )
        except (*_SDK_ERRORS, ProjectError, OSError):
            return rgb
        for index, colour in overrides.items():
            if 0 <= index < len(rgb):
                rgb[index] = colour
        return rgb

    # -- A. asset browser -----------------------------------------------------

    def _populate_grid(self) -> None:
        self._grid.blockSignals(True)
        self._grid.clear()
        self._selected = None
        sprites = self._sprites()
        if sprites is None:
            self._grid.blockSignals(False)
            return
        try:
            graphics = sprites.graphics()
        except _SDK_ERRORS as exc:
            self._grid.blockSignals(False)
            QMessageBox.critical(self, "Load sprites", str(exc))
            return
        # Cheap O(n) widget creation only - NO decode here. Each item carries its
        # identity + number; its icon is decoded lazily once the row is visible.
        for graphic in graphics:
            item = QListWidgetItem(str(graphic.identity.index))
            item.setData(_IDENTITY_ROLE, graphic.identity)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            self._grid.addItem(item)
        self._grid.blockSignals(False)
        self._apply_filter(self._search.text())
        # Paint the window first, then fill icons for the rows actually visible, and
        # start the background drain that eventually icons every remaining item.
        QTimer.singleShot(0, self._decode_visible_icons)
        self._start_icon_drain()

    def _on_scroll(self, *_args) -> None:
        """Scrollbar valueChanged/rangeChanged slot: fill now-visible rows early.

        The signals pass an int (scroll value / range bound); swallow it and run
        the None-driven visible pass. Completeness is guaranteed by the drain, so
        this is purely for snappier fill as the user scrolls or the grid relays out.
        """
        self._decode_visible_icons()

    def _start_icon_drain(self) -> None:
        """Chained-singleShot batch decode of every not-yet-iconed grid item.

        Decodes a small BATCH per event-loop tick, yielding between batches via
        QTimer.singleShot so the UI never freezes (no thread). Repeats until no
        icon-less item remains, so every cell fills regardless of viewport math or
        which rows scroll sampling happened to miss. `_pixmap_for`'s identity cache
        stops any re-decode; the guard stops a fresh populate from stacking drains.
        """
        if self._drain_active:
            return
        self._drain_active = True
        # Defer the first batch so populate itself stays O(n)-cheap (no icons set
        # synchronously); batches then run as the event loop turns.
        QTimer.singleShot(0, self._drain_batch)

    def _drain_batch(self, batch: int = 64) -> None:
        sprites = self._sprites()
        if sprites is None:
            self._drain_active = False
            return
        rgb = self._effective_rgb(sprites)
        done = 0
        for row in range(self._grid.count()):
            if done >= batch:
                break
            item = self._grid.item(row)
            if item is None or not item.icon().isNull():
                continue
            identity = item.data(_IDENTITY_ROLE)
            if not isinstance(identity, GraphicIdentity):
                continue
            try:
                graphic = sprites.graphic(identity)
                item.setIcon(self._pixmap_for(identity, graphic, rgb))
            except _SDK_ERRORS:
                # An undecodable item would loop forever; give it a transparent
                # 1x1 icon so it counts as "iconed" and the drain can finish.
                blank = QPixmap(1, 1)
                blank.fill(Qt.GlobalColor.transparent)
                item.setIcon(blank)
            done += 1
        if done >= batch:
            QTimer.singleShot(0, self._drain_batch)  # more remain; yield, continue
        else:
            self._drain_active = False  # nothing icon-less left

    def _decode_visible_icons(self, rows: list[int] | None = None) -> None:
        """Decode + set icons for grid rows visible in the viewport (lazy).

        Only visible, not-yet-iconed rows are decoded; `_pixmap_for`'s identity
        cache stops any re-decode. `rows` is an explicit row list used only by
        tests (offscreen Qt cannot report a real viewport rect); production leaves
        it None and the visible set is derived from `visualItemRect` intersecting
        the viewport (WB-005 L4 lazy-thumbnail fix).
        """
        sprites = self._sprites()
        if sprites is None:
            return
        rgb = self._effective_rgb(sprites)
        if rows is None:
            viewport = self._grid.viewport().rect()
            rows = [
                row
                for row in range(self._grid.count())
                if not self._grid.item(row).isHidden()
                and self._grid.visualItemRect(self._grid.item(row)).intersects(viewport)
            ]
        for row in rows:
            item = self._grid.item(row)
            if item is None or not item.icon().isNull():
                continue  # gone, or already decoded
            identity = item.data(_IDENTITY_ROLE)
            if not isinstance(identity, GraphicIdentity):
                continue
            try:
                graphic = sprites.graphic(identity)
                item.setIcon(self._pixmap_for(identity, graphic, rgb))
            except _SDK_ERRORS:
                # A single undecodable thumbnail must not blank the whole grid.
                pass

    def _pixmap_for(self, identity: GraphicIdentity, graphic, rgb) -> QPixmap:
        """Decode-once cache: keyed by identity so paint never re-decodes."""
        cached = self._pixmap_cache.get(identity)
        if cached is not None:
            return cached
        pixmap = indexed_pixmap(graphic.pixels, graphic.width, graphic.height, rgb)
        self._pixmap_cache[identity] = pixmap
        return pixmap

    @staticmethod
    def _scaled_for_preview(pixmap: QPixmap, box: int = _PREVIEW_MIN) -> QPixmap:
        """Scale a native-size sprite pixmap UP to fill a preview box, crisply.

        KeepAspectRatio (no distortion) + FastTransformation (nearest-neighbour, so
        pixel art scales up sharp, not blurred). Never scales DOWN: a sprite already
        larger than the box shows native rather than shrinking. Operates on a fresh
        pixmap, so the cached native thumbnail the grid uses is never mutated.
        """
        w, h = pixmap.width(), pixmap.height()
        if w <= 0 or h <= 0 or (w >= box and h >= box):
            return pixmap
        return pixmap.scaled(
            box,
            box,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )

    def _apply_filter(self, text: str) -> None:
        needle = text.strip()
        for row in range(self._grid.count()):
            item = self._grid.item(row)
            item.setHidden(bool(needle) and needle not in item.text())
        # Hiding/showing rows shifts what's on screen: fill any newly-visible ones.
        QTimer.singleShot(0, self._decode_visible_icons)

    def _on_grid_selection(self, current, _previous) -> None:
        if current is None:
            return
        identity = current.data(_IDENTITY_ROLE)
        if not isinstance(identity, GraphicIdentity):
            return
        self._selected = identity
        self._show_selected(identity)

    # -- B. selected-asset inspector ------------------------------------------

    def _show_selected(self, identity: GraphicIdentity) -> None:
        sprites = self._sprites()
        if sprites is None:
            return
        try:
            graphic = sprites.graphic(identity)
        except _SDK_ERRORS as exc:
            QMessageBox.critical(self, "Inspect sprite", str(exc))
            return
        # Keep selection state consistent no matter who calls us: _on_grid_selection
        # sets it, but _after_undo_redo calls us directly after _populate_grid has
        # nulled it, and the scoped palette header reads self._selected.index.
        self._selected = identity
        self._export.setEnabled(True)  # a sprite is selected: export is now valid
        rgb = self._effective_rgb(sprites)
        self._preview.setPixmap(
            self._scaled_for_preview(self._pixmap_for(identity, graphic, rgb))
        )
        self._dims.setText(f"Dimensions: {graphic.width} x {graphic.height}")
        self._shared.setText(
            f"Shared: {'yes' if graphic.shared else 'no'} "
            f"({len(graphic.consumers)} frame(s))"
        )
        self._consumers.setText(str(len(graphic.consumers)))
        self._characters.setText(
            ", ".join(str(c.index) for c in graphic.characters) or "none decoded"
        )
        # The palette indices this sprite's pixels actually reference. These are
        # SDK-provided linear indices, not a decoded ROM structure, so reading
        # them is not ROM-format math and claims no hardware palette bank.
        self._used_indices = set(graphic.pixels)
        self._populate_palette()
        # Load the first using character's animations, if any.
        self._load_character_animations(graphic.characters[0] if graphic.characters else None)
        self._update_status()

    def _on_export(self) -> None:
        """Export the selected sprite to an indexed PNG the user picks a path for.

        Encodes through the SDK façade with the EFFECTIVE palette so the file
        matches committed recolours; the widget never touches a codec. The SDK
        call AND the file write share one guard catching the SDK family + OSError,
        so a bad encode or an unwritable path becomes a QMessageBox, never a
        dead-looking click or a terminal traceback (the WB failure mode).
        """
        if self._selected is None:
            return
        sprites = self._sprites()
        if sprites is None:
            return
        suggested = f"sprite_{self._selected.index}.png"
        path, _filter = QFileDialog.getSaveFileName(
            self, "Export sprite PNG", suggested, "PNG image (*.png)"
        )
        if not path:  # user cancelled
            return
        try:
            blob = sprites.export_graphic_png(self._selected, self._effective_rgb(sprites))
            Path(path).write_bytes(blob)
        except (*_SDK_ERRORS, OSError) as exc:
            QMessageBox.critical(self, "Export PNG", str(exc))
            return
        self._status.setText(f"Exported sprite {self._selected.index} to {path}")

    # -- C. animation frame viewer --------------------------------------------

    def _load_character_animations(self, character: CharacterIdentity | None) -> None:
        self._anim_select.blockSignals(True)
        self._anim_select.clear()
        self._anim_character = character
        self._animations = ()
        self._anim_index = 0
        self._frame_index = 0
        if character is None:
            self._anim_select.blockSignals(False)
            self._anim_preview.setText("No character uses this sprite.")
            self._frame_label.setText("—")
            return
        sprites = self._sprites()
        if sprites is None:
            self._anim_select.blockSignals(False)
            return
        try:
            self._animations = sprites.get_actor_animations(character)
        except _SDK_ERRORS as exc:
            self._anim_select.blockSignals(False)
            QMessageBox.critical(self, "Animations", str(exc))
            return
        for animation in self._animations:
            self._anim_select.addItem(
                f"Animation {animation.index} ({len(animation.frames)} frames)"
            )
        self._anim_select.blockSignals(False)
        if self._animations:
            self._anim_select.setCurrentRow(0)
        else:
            self._anim_preview.setText("No decodable animations.")
            self._frame_label.setText("—")

    def _on_animation_chosen(self, row: int) -> None:
        if not (0 <= row < len(self._animations)):
            return
        self._anim_index = row
        self._frame_index = 0
        self._render_frame()

    def _step_frame(self, delta: int) -> None:
        if not self._animations:
            return
        frames = self._animations[self._anim_index].frames
        if not frames:
            return
        self._frame_index = (self._frame_index + delta) % len(frames)
        self._render_frame()

    def _render_frame(self) -> None:
        if not self._animations:
            return
        animation = self._animations[self._anim_index]
        frames = animation.frames
        if not frames:
            self._anim_preview.setText("Animation has no frames.")
            self._frame_label.setText("—")
            return
        frame = frames[self._frame_index]
        # timing_unknown is always True; the label carries no fabricated ms.
        self._frame_label.setText(f"Frame {frame.frame_index + 1} / {len(frames)}")
        sprites = self._sprites()
        if sprites is None:
            return
        rgb = self._effective_rgb(sprites)
        # First direction slot that decoded to a graphic is the shown frame.
        identity = next((g for g in frame.graphics if g is not None), None)
        if identity is None:
            self._anim_preview.setText("(no decodable art this frame)")
            return
        try:
            graphic = sprites.graphic(identity)
            self._anim_preview.setPixmap(
                self._scaled_for_preview(self._pixmap_for(identity, graphic, rgb))
            )
        except _SDK_ERRORS:
            self._anim_preview.setText("(frame art failed to decode)")

    # -- D/E. palette editor + pending change ---------------------------------

    def _repaint_palette(self, _checked=False) -> None:
        """Toggle/selection repaint: keep pending edits, just re-scope."""
        self._populate_palette()

    def _populate_palette(self, clear_pending: bool = False) -> None:
        """Render the palette, scoped to the selected sprite's used indices or full.

        Scoped mode (the default when a sprite is selected) shows only the
        swatches whose global index is in `self._used_indices` - the colours this
        sprite's pixels reference. Each swatch keeps its TRUE global index in the
        tooltip and a small caption label, so editing still targets the correct
        global palette entry. Full mode shows the whole 256-entry grid unchanged.
        No sprite selected -> full palette.

        `clear_pending` is set only by the session/undo reset paths; the toggle
        and selection repaints keep uncommitted edits so a re-scope never
        silently discards work.
        """
        for swatch in self._swatches.values():
            swatch.deleteLater()
        self._swatches = {}
        if clear_pending:
            self._palette_pending.clear()
        self._refresh_pending_ui()
        sprites = self._sprites()
        if sprites is None:
            self._scope_header.setText("Open a ROM to load its palette.")
            self._scope_caption.setVisible(False)
            return
        rgb = self._effective_rgb(sprites)

        scoped = self._scope_used.isChecked() and self._used_indices is not None
        if scoped:
            indices = sorted(i for i in self._used_indices if 0 <= i < len(rgb))
            self._scope_header.setText(
                f"Colours used by sprite #{self._selected.index} "
                f"({len(indices)} indices)"
                if self._selected is not None
                else f"Colours used by this sprite ({len(indices)} indices)"
            )
            self._scope_caption.setVisible(True)
        else:
            indices = list(range(len(rgb)))
            if self._used_indices is None:
                self._scope_header.setText("Full palette (select a sprite to scope).")
            else:
                self._scope_header.setText("Full palette.")
            self._scope_caption.setVisible(False)

        for column_pos, index in enumerate(indices):
            r, g, b = rgb[index]
            # Pending (uncommitted) edits preview on top of the effective colour.
            if index in self._palette_pending:
                r, g, b = self._palette_pending[index]
            swatch = QFrame()
            swatch.setFixedSize(_SWATCH, _SWATCH)
            swatch.setFrameShape(QFrame.Shape.Box)
            # Scoped swatches carry the true global index in the tooltip AND as a
            # small overlaid label, so an edit is never mistaken for a re-based one.
            swatch.setToolTip(f"Palette index {index}")
            if scoped:
                label = QLabel(str(index), swatch)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("color: rgba(255,255,255,160); font-size: 7px;")
                label.setFixedSize(_SWATCH, _SWATCH)
            self._paint_swatch(swatch, r, g, b)
            swatch.mousePressEvent = self._swatch_click(index)
            # Full mode keeps the canonical 16-wide grid at each index's home
            # cell; scoped mode packs the subset into a fresh 16-wide grid.
            row, col = (
                (column_pos // _SWATCH_COLUMNS, column_pos % _SWATCH_COLUMNS)
                if scoped
                else (index // _SWATCH_COLUMNS, index % _SWATCH_COLUMNS)
            )
            self._palette_grid.addWidget(swatch, row, col)
            self._swatches[index] = swatch

    @staticmethod
    def _paint_swatch(swatch: QFrame, r: int, g: int, b: int) -> None:
        swatch.setStyleSheet(f"background-color: rgb({r},{g},{b});")

    def _swatch_click(self, index: int):
        def handler(_event) -> None:
            self._pick_colour(index)
        return handler

    def _pick_colour(self, index: int) -> None:
        sprites = self._sprites()
        if sprites is None:
            return
        current = self._palette_pending.get(index) or self._effective_rgb(sprites)[index]
        chosen = QColorDialog.getColor(
            QColor(*current), self, f"Recolour palette index {index}"
        )
        if not chosen.isValid():
            return
        self._palette_pending[index] = (chosen.red(), chosen.green(), chosen.blue())
        swatch = self._swatches.get(index)
        if swatch is not None:
            self._paint_swatch(swatch, chosen.red(), chosen.green(), chosen.blue())
        self._refresh_pending_ui()

    def _refresh_pending_ui(self) -> None:
        pending = bool(self._palette_pending)
        self._revert.setEnabled(pending)
        self._apply.setEnabled(pending and self._session.project_dir is not None)
        if not pending:
            self._pending_label.setText("No pending palette change.")
            return
        sprites = self._sprites()
        effective = self._effective_rgb(sprites) if sprites is not None else None
        lines = []
        for index in sorted(self._palette_pending):
            r, g, b = self._palette_pending[index]
            # "from" colour is the EFFECTIVE colour before this pending edit
            # (committed override if any, else canonical) - not the raw ROM word.
            old = effective[index] if effective is not None else (0, 0, 0)
            # Disclose known shared consumers before Apply (SC4): count who
            # references this palette index, from the facade, never guessed. A
            # transient SDK error shows "unknown", never "0" - never understate
            # a shared edit's blast radius.
            try:
                consumers = (
                    len(sprites.palette_users(index)) if sprites is not None else "unknown"
                )
            except _SDK_ERRORS:
                consumers = "unknown"
            lines.append(
                f"Palette color {index}  "
                f"#{old[0]:02X}{old[1]:02X}{old[2]:02X} -> #{r:02X}{g:02X}{b:02X}"
                f"  ·  known consumers: {consumers}"
            )
        note = "" if self._session.project_dir is not None else "  (open a project to apply)"
        self._pending_label.setText("\n".join(lines) + note)

    def _on_apply(self) -> None:
        if not self._palette_pending or self._session.project_dir is None:
            return
        profile = self._session.profile
        sprites = self._sprites()
        if profile is None or sprites is None:
            return
        # Disclose the total known consumers across every pending index before
        # committing a shared edit; the count is the facade's, not invented.
        try:
            affected = sum(len(sprites.palette_users(i)) for i in self._palette_pending)
        except _SDK_ERRORS as exc:
            QMessageBox.critical(self, "Apply recolour", str(exc))
            return
        confirm = QMessageBox.question(
            self,
            "Apply palette recolour",
            f"This recolours {len(self._palette_pending)} palette entr(y/ies), "
            f"affecting {affected} known graphic consumer(s). Apply?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        # WB-005 Layer 3: capture prior state, perform + validate the apply, THEN
        # record it as a QUndoCommand. The write runs here (not in the command's
        # first redo) so an SDK failure is caught by this guard and the stack is
        # left untouched - a Python exception inside redo() would otherwise be
        # swallowed by Qt yet still leave the failed command on the stack.
        pending = dict(self._palette_pending)
        try:
            prior = {i: self._read_override(i) for i in pending}
            for index in sorted(pending):
                r, g, b = pending[index]
                self._write_override(index, r, g, b)
        except (*_SDK_ERRORS, ProjectError, OSError) as exc:
            QMessageBox.critical(self, "Apply recolour", str(exc))
            return
        # The edit is on disk and known-good; refresh currency + repaint (this
        # also clears _palette_pending), then record it. push() fires the
        # command's first redo, a no-op (see the command docstring), so no
        # double-write and merging still collapses consecutive same-index
        # gestures into one history entry.
        self._after_undo_redo()
        self._undo_stack.push(PaletteRecolourCommand(self, pending, prior))

    # -- WB-005 Layer 3: undo/redo support ------------------------------------

    def _read_override(self, index: int) -> tuple[int, int, int] | None:
        """The prior authored rgb for one index, or None if unauthored.

        Read in `_on_apply` before the write and handed to the command, so undo
        can reverse to it (None -> remove the override). Raises the SDK family /
        ProjectError / OSError on failure, caught by `_on_apply`'s guard before
        anything is pushed onto the stack.
        """
        profile = self._session.profile
        if self._session.project_dir is None or profile is None:
            return None
        return graphics_sdk.get_palette_override(
            self._session.project_dir, profile, index
        )

    def _write_override(self, index: int, r: int, g: int, b: int) -> None:
        """Persist one recolour through the SDK (redo, or undo-to-prior-rgb)."""
        profile = self._session.profile
        graphics_sdk.set_palette_override(
            self._session.project_dir, profile, index, r, g, b
        )

    def _clear_override(self, index: int) -> None:
        """Remove one authored recolour (undo of an index with no prior override)."""
        profile = self._session.profile
        graphics_sdk.remove_palette_override(
            self._session.project_dir, profile, index
        )

    def _after_undo_redo(self) -> None:
        """Post-command refresh: the exact currency + repaint the apply used.

        Every redo/undo is a project mutation, so it bumps the session revision
        and emits `projectChanged` (Build/Launch re-arm), then repaints the
        palette and status. Clean/dirty is deliberately NOT wired to
        `QUndoStack.setClean`: the Session tracks currency with a monotonic
        `project_revision` (validation/build compared against it), and an
        undo/redo is a fresh mutation there rather than a return to a clean
        point, so `setClean` would fight that model (qt-patterns.md).
        """
        # The effective palette changed, so every cached thumbnail using an
        # affected index is stale - drop the whole decode cache so grid/preview
        # repaint against the new effective colours.
        self._pixmap_cache.clear()
        self._session.project_mutated()
        self.projectChanged.emit()
        selected = self._selected
        self._populate_grid()  # clears _selected; repaints every thumbnail
        if selected is not None:
            self._show_selected(selected)  # repaint the inspector preview too
        self._populate_palette(clear_pending=True)
        self._update_status()

    def _on_revert(self) -> None:
        """Discard unapplied swatch edits and repaint from the ROM palette."""
        self._palette_pending.clear()
        self._populate_palette()

    # -- status line ----------------------------------------------------------

    def _update_status(self) -> None:
        sprites = self._sprites()
        if sprites is None:
            self._status.setText("No sprites available for the open ROM.")
            return
        parts = []
        if self._selected is not None:
            parts.append(f"asset {self._selected.index}")
        validation = "current" if self._session.validation_current else "stale"
        build = "current" if self._session.build_current else "stale"
        parts.append(f"validation {validation}")
        parts.append(f"build {build}")
        if self._session.project_dir is None:
            parts.append("no project open")
        self._status.setText("  ·  ".join(parts))
