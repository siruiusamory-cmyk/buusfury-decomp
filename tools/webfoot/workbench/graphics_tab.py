"""WORKBENCH-005 Layer 2 - the DragonByte Z Graphics workspace.

A visual game-content tab: SEE the game's real decoded sprites, select one,
inspect who uses it, step its animations, and recolour the shared object palette.
It is a THIN client - every pixel, dimension, backlink, animation and colour
comes from the `ActorSprites` SDK facade (`tools/webfoot/graphics.py`); this
widget computes no ROM-format value. Colour is never packed here (the SDK owns
RGB->GBA-word packing via `plan_palette_entry_rgb`, applied at build); a recolour
is recorded through the project + `session.project_mutated()`, exactly the way
the Inspector records a dialogue edit.

Desktop patterns adopted (the DragonByte Z correction, not the old plain-UX
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
    QBrush,
    QColor,
    QImage,
    QKeySequence,
    QPainter,
    QPixmap,
    QUndoCommand,
    QUndoStack,
    qRgb,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .. import graphics as graphics_sdk
from .. import sprite_project as sprite_sdk
from ..formats.indexed_png import PngError
from ..formats.sprite_graphics import SpriteFormatError
from ..graphics import CharacterIdentity, GraphicIdentity, GraphicsError
from ..project import AuthoredSprites, ProjectError, read_project
from ..sprite_authoring import SpriteAuthoringError
from ..write import OutputPathError, ensure_not_source_alias
from . import theme
from .session import Session
from .sprite_dialog import SpriteAuthoringDialog
from .widgets import PanelHeader, StateChip, ToolStrip

#: The SDK exception families a Graphics slot must catch at its boundary. The
#: first three are `ValueError` subclasses in different families, so a lone leaf
#: leaves siblings uncaught (references/error-handling.md); `OutputPathError` is
#: the write module's own family, raised by the shared source-alias policy the
#: export slot applies before it lets a byte reach the destination.
_SDK_ERRORS = (GraphicsError, SpriteFormatError, PngError, OutputPathError)

_THUMB = 64  # icon-grid thumbnail edge, px
_PREVIEW_MIN = 320  # selected/animation preview min edge, px (was 160/120)
#: A swatch is a small dense square: big enough to tell two colours apart, hit with
#: a pointer and show a selection ring, and no bigger. Aseprite's palette entries
#: are 8-10px; this stays above that for pointer reliability on a wide display.
_SWATCH = 14
#: The object palette is sixteen 16-index rows by its own structure, so a bank is
#: 16 swatches and the bank label carries that row's true index range.
_SWATCH_COLUMNS = 16
#: How many bank blocks sit across before wrapping. Four 16-wide banks is 64
#: swatches wide, which fits the pane at a desktop width without a horizontal
#: scrollbar.
_PALETTE_BANK_COLUMNS = 4
#: One bank is the 16 indices of a palette row, drawn as a 4x4 block so a bank
#: costs four rows instead of one 16-wide strip. 16 = 4 x 4 by construction.
_BANK_EDGE = 4
#: Bound on the palette's own height, so the shared palette can never take half the
#: workspace: eight bank rows at 14px costs about 190px and then it scrolls.
_PALETTE_MAX_H = 210
#: Bound on the compact animation list beside the preview.
_ANIM_LIST_MAX_H = 64
#: Frame-control button width. Wide enough for the widest glyph it carries, so a
#: control is never elided; the overlap probe checks this.
_ANIM_BUTTON_W = 34
#: Preview playback cadence. Timing is NOT decoded from the image (the SDK says so),
#: so this is a fixed presentation rate and the note beside it says as much.
_PREVIEW_PLAY_MS = 240
_IDENTITY_ROLE = Qt.ItemDataRole.UserRole
_PALETTE_CMD_ID = 0xB005  # shared id() so palette recolours can merge (WB-005 L3)
_SPRITE_CMD_ID = 0xB006  # one authored-sprite commit is one history entry

#: The SDK families an authored-sprite slot must catch at its boundary. The
#: facade translates the planners' own families into `SpriteAuthoringError`, the
#: model raises `ProjectError`, and the write touches the filesystem.
_SPRITE_ERRORS = (SpriteAuthoringError, ProjectError, OSError)

#: Index -> alpha mask byte, applied to a whole scanline buffer in one C-level
#: `bytes.translate`. Entry 0 is 0 (transparent); every other index is 255
#: (opaque). This is what keeps the index-0 transparency from costing a Qt call per
#: pixel.
_OPAQUE_BY_INDEX = bytes([0] + [255] * 255)


class PaletteRecolourCommand(QUndoCommand):
    """One undoable palette Apply: a batch of per-index recolours.

    Undo is SEMANTIC, never a byte write. For each index the command captures
    the NEW rgb and the PRIOR project state read from
    `graphics_sdk.get_palette_overrides` at construction time: either the prior
    override rgb, or None meaning "unauthored, so undo must REMOVE the override".
    `redo()` runs on the first `stack.push()` too, so the SDK write and the tab
    refresh both live in `redo()`; `undo()` reverses each index to its captured
    prior state and refreshes the same way. Both commit their whole index set in
    ONE `set_palette_overrides` call - one index set is one project write, not
    one whole-project read+write per index (CQA-07).

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
        self._tab._write_overrides(dict(self._new))
        self._tab._after_undo_redo()

    def undo(self) -> None:
        # None means "remove": an index with no prior override must go back to
        # unauthored, and the batch write path expresses that as a removal.
        self._tab._write_overrides(dict(self._prior))
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


class AuthoredSpriteCommand(QUndoCommand):
    """One undoable commit to the project's authored-sprite document.

    The write ALREADY happened before the push, because a Python exception raised
    inside `redo()` does not propagate cleanly through Qt's C++ `push()` and the
    failed command would still be recorded on the stack. The first, push-driven
    redo is therefore a no-op. Undo writes the prior document - for a first commit
    an empty one, which is how undo removes the file - and both directions go
    through the tab's one write path, so an undo is a fresh project mutation
    rather than a silent return to a clean point.

    The project directory is captured here, at construction. The tab's history
    outlives an Open Project, and resolving the session's CURRENT directory when
    the command runs would write one project's document into another; a mismatch
    is refused and reported instead.
    """

    def __init__(self, tab: "GraphicsTab", project_dir, prior: AuthoredSprites,
                 current: AuthoredSprites, text: str):
        super().__init__(text)
        self._tab = tab
        self._project = Path(project_dir) if project_dir is not None else None
        self._prior = prior
        self._current = current
        self._applied = True

    def redo(self) -> None:
        if self._applied:
            self._applied = False
            return
        self._write(self._current)

    def undo(self) -> None:
        self._write(self._prior)

    def _write(self, document: AuthoredSprites) -> None:
        """Write this command's document into the project it was made in.

        A failed write leaves the file as it was, so the history and the disk can
        disagree; the strip re-reads the project on the next refresh, which is what
        shows the author that nothing moved. Qt gives a command no way to abort
        mid-stack, so the refusal is surfaced rather than swallowed.
        """
        current = self._tab._session.project_dir
        if (current is None or self._project is None
                or Path(current) != self._project):
            QMessageBox.information(
                self._tab, "Authored sprite",
                "This change belongs to a project that is no longer open, so it was "
                "not written. Open that project and use Undo there.")
            return
        try:
            self._tab._write_authored_document(document)
        except _SPRITE_ERRORS as exc:
            QMessageBox.critical(self._tab, "Authored sprite", str(exc))
            return
        self._tab._after_authored_change()


def indexed_pixmap(pixels: bytes, width: int, height: int, rgb) -> QPixmap:
    """Build a QPixmap from linear 8-bit indexed pixels + an RGB colour table.

    `rgb` is the SDK's `palette.rgb` (256 (r,g,b) triples). Uses
    `QImage.Format_Indexed8` with `setColorTable`, the idiomatic Qt path for
    indexed art. The QImage does not own the buffer it is handed, so the result
    is `.copy()`d to a standalone image before making the pixmap - otherwise the
    pixels could be freed underneath it. No ROM-format math: this only maps an
    index to a display colour the SDK already computed.

    Index 0 is treated as a TRANSPARENT index. That is not an assumption about the
    hardware: an unset pixel reads as index 0 in every one of these graphics, and
    painting it as opaque black is what put a black rectangle behind and around a
    sprite. Marking it transparent lets a preview show the art alone, so a
    transparent ground, a dark outline and a genuinely black pixel stay
    distinguishable.
    """
    colour_table = [qRgb(r, g, b) for (r, g, b) in rgb]
    # bytesPerLine == width: the SDK yields a tightly packed, unpadded buffer.
    image = QImage(bytes(pixels), width, height, width, QImage.Format.Format_Indexed8)
    image.setColorTable(colour_table)
    # Index 0 becomes alpha 0. `Format_Indexed8` carries no alpha of its own, so the
    # transparency is applied as a separate 8-bit MASK: 0 where the index is 0
    # (transparent) and 255 everywhere else (opaque).
    #
    # The mask is built in ONE bulk byte translation and handed to
    # `setAlphaChannel`, which is a native operation over the whole scanline buffer.
    # The obvious alternative - walking `pixelIndex(x, y)` in Python - costs a Qt
    # call per pixel and measured roughly 60x slower on a 9.2 Mpx composite (tens of
    # times slower at every size tried), which matters because it runs on the UI
    # thread: the Objects canvas shares this helper. See
    # `docs/research/UI_FUNCTIONAL_DIFF.md` for the recorded figures.
    mask_bytes = bytes(pixels).translate(_OPAQUE_BY_INDEX)
    mask = QImage(mask_bytes, width, height, width, QImage.Format.Format_Grayscale8)
    converted = image.convertToFormat(QImage.Format.Format_ARGB32)
    converted.setAlphaChannel(mask)
    return QPixmap.fromImage(converted)


class PreviewLabel(QLabel):
    """A sprite preview: a real 320px *preferred* box on a light technical ground.

    The viewer-size fix kept the preview at least 320px in each axis, and that is
    the right preferred size - a sprite shown smaller cannot be read. But as a hard
    *minimum* it made the Graphics pane taller than a 900px window once the palette
    was counted, which forced the whole shell's minimum above the screen it had to
    run on. So the preference is stated where a preference belongs:
    ``minimumSizeHint`` keeps asking for the square, and the layout is free to give
    the preview the height the window actually has.

    The ground is the palette's `preview` token, not black. On a light editor a
    black field read as a hole punched in the pane, and it was never needed to
    judge transparency: the sprite's own outline is what carries its edge.
    """

    def __init__(self, text: str = "", box: int = _PREVIEW_MIN) -> None:
        super().__init__(text)
        self._box = box
        self.setAutoFillBackground(True)
        fill = self.palette()
        fill.setColor(self.backgroundRole(), theme.color("preview"))
        self.setPalette(fill)
        # A transparency checkerboard, as Aseprite and Tiled use behind indexed art:
        # transparent pixels show it, so the art's own extent is visible instead of
        # being framed by an opaque field.
        self._checker = _preview_checker()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._checker)
        painter.end()
        super().paintEvent(event)

    def minimumSizeHint(self):  # noqa: N802 - Qt naming
        return QSize(self._box, self._box)


def _preview_checker(cell: int = 8) -> QBrush:
    """The preview's transparency checkerboard, from the palette's own greys."""
    pixmap = QPixmap(cell * 2, cell * 2)
    pixmap.fill(theme.color("preview"))
    painter = QPainter(pixmap)
    painter.fillRect(0, 0, cell, cell, theme.color("checker_dark"))
    painter.fillRect(cell, cell, cell, cell, theme.color("checker_dark"))
    painter.end()
    return QBrush(pixmap)


class GraphicsTab(QWidget):
    """Browse decoded sprites, inspect one, step animations, recolour palette."""

    projectChanged = Signal()  # emitted on a committed palette edit
    #: This editor's own status line, republished for the shell. The shell owns the
    #: one status bar and mirrors this editor's line into it, so the bar cannot show
    #: a stale selection state: a plain QLabel has no text-change signal of its own,
    #: which is exactly how "7390 sprites; none selected" stayed on screen after a
    #: sprite had been selected.
    statusChanged = Signal(str)

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
        #: The swatch whose detail line is currently shown. One selection, one
        #: detail line: individual swatches carry no permanent text.
        self._selected_palette_index: int | None = None
        # The distinct palette indices the selected sprite's pixels reference
        # (set(graphic.pixels)); None until a sprite is selected. NOT a palette
        # bank - just the colours this sprite's pixels actually address.
        self._used_indices: set[int] | None = None
        # WB-005 Layer 3: one undo history for the visual palette mutations this
        # tab commits. Established here; other editors migrate in later tickets.
        self._undo_stack = QUndoStack(self)
        #: True only while this tab is the EMITTER of `projectChanged`. The shell
        #: answers that signal by calling `on_project_mutated()` on every peer,
        #: this tab included (`app.py:166` + `app.py:249`), so without this guard
        #: one logical edit repaints twice: once from the emitting method's own
        #: refresh and once from the shell's re-entrant call back into it. The
        #: guard suppresses nothing on the wire - the signal still reaches every
        #: peer - it only stops this tab from answering its own emission, because
        #: the emitting method already repainted. CQA-07.
        self._emitting_project_change = False

        # -- A. Asset browser (thumbnail grid) --------------------------------
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by sprite ID\u2026")
        self._search.setClearButtonEnabled(True)
        self._search.setAccessibleName("Search sprites by ID")
        self._search.setToolTip(
            "The sprite index as the game image stores it. Only the ID is "
            "searchable here; sprite names are not recovered."
        )
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
        browser_layout.setSpacing(0)
        browser_header = PanelHeader("Sprites")
        browser_layout.addWidget(browser_header)
        browser_layout.addWidget(self._search)
        browser_layout.addWidget(self._grid, 1)

        # -- B. Contextual inspector -------------------------------------------
        #
        # Selection decides what appears here, the way GB Studio's Editor Sidebar
        # and Porymap's per-mode inspector page do. With nothing selected the pane
        # is ONE sentence and nothing else: no empty preview rectangle, no rows
        # reading "-", no disabled Export button, no empty animation pane. Every
        # one of those was implementation scaffolding showing through.
        self._preview = PreviewLabel("Select a sprite.")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # A sprite preview narrower than this cannot be read, and the tab's own
        # tests pin the width. The height floor is released so the pane fits a real
        # window; the box still asks for the full square.
        self._preview.setMinimumSize(_PREVIEW_MIN, 0)
        self._preview.setFrameShape(QFrame.Shape.NoFrame)
        self._preview.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        # -- C. Selection detail: one preview, one set of controls --------------
        #
        # There is exactly ONE preview in this editor. It shows the selected sprite
        # when a static asset is chosen and the selected animation's current frame
        # when an animated one is, because they are the same thing seen at two
        # levels of detail. A second preview pane showing the same sprite again was
        # pure duplication, and it cost a second 320px band of height.
        self._dims = QLabel("")
        self._dims.setProperty("dbzRole", "technical")
        self._shared = QLabel("")
        self._consumers = QLabel("")
        self._consumers.setWordWrap(True)
        self._characters = QLabel("")
        self._characters.setWordWrap(True)
        # Export the selected sprite to an indexed PNG. Only reachable while a
        # sprite is selected, because it is only meaningful then.
        self._export = QPushButton("Export PNG\u2026")
        self._export.setEnabled(False)
        self._export.clicked.connect(self._on_export)
        self._animations = ()
        self._anim_list_label = QLabel("Animations")
        self._anim_list_label.setProperty("dbzRole", "fieldLabel")
        self._anim_select = QListWidget()
        # Compact: a short scrolling list beside the controls, not a panel.
        self._anim_select.setMaximumHeight(_ANIM_LIST_MAX_H)
        self._anim_select.setMinimumWidth(0)
        self._anim_select.currentRowChanged.connect(self._on_animation_chosen)
        self._frame_label = QLabel("\u2014")
        # The frame readout must never be squeezed by the buttons beside it: it is
        # the only place the current frame is stated in words.
        self._frame_label.setMinimumWidth(84)
        self._frame_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._prev_frame = QPushButton("\u25c0")
        self._prev_frame.setToolTip("Previous frame")
        self._prev_frame.setFixedWidth(_ANIM_BUTTON_W)
        self._prev_frame.clicked.connect(lambda: self._step_frame(-1))
        # Play/pause is presentation only: it advances which frame is shown and
        # never touches ROM data, the decoded frame timing or the document.
        self._play = QPushButton("\u25b6")
        self._play.setToolTip(
            "Play or pause the preview at a fixed rate. Playback is presentation "
            "only; it never changes ROM data or frame timing."
        )
        self._play.setCheckable(True)
        self._play.setFixedWidth(_ANIM_BUTTON_W)
        self._play.toggled.connect(self._on_play_toggled)
        self._next_frame = QPushButton("\u25b6")
        self._next_frame.setToolTip("Next frame")
        self._next_frame.setFixedWidth(_ANIM_BUTTON_W)
        self._next_frame.clicked.connect(lambda: self._step_frame(1))
        # Timing is UNKNOWN per the SDK, so playback is a fixed preview cadence and
        # the note says so rather than implying a decoded frame duration.
        self._timing_note = QLabel(
            "Frame timing is not recorded by this image: the stepper and the "
            "preview play at a fixed rate, and neither is a decoded duration."
        )
        self._timing_note.setProperty("dbzRole", "hint")
        self._timing_note.setWordWrap(True)
        self._paint_timer = QTimer(self)
        self._paint_timer.setInterval(_PREVIEW_PLAY_MS)
        self._paint_timer.timeout.connect(lambda: self._step_frame(1))

        anim_strip = ToolStrip()
        anim_strip.add(self._prev_frame)
        anim_strip.add(self._play)
        anim_strip.add(self._next_frame)
        anim_strip.add(self._frame_label)
        anim_strip.add_stretch()
        self._anim_strip = anim_strip

        # The strip carries a stated minimum so the controls beside it cannot
        # squeeze the frame readout to nothing.
        anim_strip.setMinimumWidth(anim_strip.sizeHint().width())

        anim_row = QWidget()
        anim_row_layout = QVBoxLayout(anim_row)
        anim_row_layout.setContentsMargins(0, 0, 0, 0)
        anim_row_layout.setSpacing(theme.SPACE_SM)
        anim_row_layout.addWidget(anim_strip)
        anim_row_layout.addWidget(self._anim_list_label)
        anim_row_layout.addWidget(self._anim_select)

        self._asset_body = QWidget()
        asset_layout = QVBoxLayout(self._asset_body)
        asset_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        asset_layout.setSpacing(theme.SPACE_SM)
        asset_layout.addWidget(self._preview, 1)
        asset_layout.addWidget(anim_row)
        asset_layout.addWidget(self._timing_note)
        # An explicit two-column grid rather than a QFormLayout: the form stacked a
        # caption and its value on consecutive lines here, which read as five
        # unlabelled values. One column of captions, one of values, aligned once.
        details = QGridLayout()
        details.setContentsMargins(0, 0, 0, 0)
        details.setHorizontalSpacing(theme.SPACE_MD)
        details.setVerticalSpacing(theme.SPACE_XS)
        details.setColumnStretch(1, 1)
        for row, (caption, value) in enumerate(
            (
                ("Dimensions", self._dims),
                ("Frames", self._consumers),
                ("Characters", self._characters),
                ("Shared", self._shared),
            )
        ):
            label = QLabel(caption)
            label.setProperty("dbzRole", "fieldLabel")
            label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
            )
            details.addWidget(label, row, 0)
            details.addWidget(value, row, 1)
        asset_layout.addLayout(details)
        asset_layout.addWidget(self._export)
        self._asset_empty = QLabel(
            "Select a sprite to inspect it. Its preview, its animation, the frames "
            "that use it, the characters it belongs to and its export action appear "
            "here."
        )
        self._asset_empty.setProperty("dbzRole", "hint")
        self._asset_empty.setWordWrap(True)
        self._asset_empty.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self._asset_holder = QWidget()
        asset_holder_layout = QVBoxLayout(self._asset_holder)
        asset_holder_layout.setContentsMargins(0, 0, 0, 0)
        asset_holder_layout.setSpacing(0)
        self._asset_header = PanelHeader("Selected sprite")
        asset_holder_layout.addWidget(self._asset_header)
        asset_holder_layout.addWidget(self._asset_empty, 1)
        asset_holder_layout.addWidget(self._asset_body, 1)

        inspector = QWidget()
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.setContentsMargins(0, 0, 0, 0)
        inspector_layout.setSpacing(theme.SPACE_SM)
        inspector_layout.addWidget(self._asset_holder, 1)
        # Nothing selected yet, so the dependent surfaces do not exist yet.
        self._set_asset_body_visible(False)

        # -- D. Palette editor -------------------------------------------------
        # Scope toggle: default-on so a selected sprite shows only the colours it
        # uses. Honest wording only - these are the indices the sprite's pixels
        # reference, NOT a proven per-sprite hardware palette bank.
        self._scope_used = QCheckBox("Show only colours used by this sprite")
        self._scope_used.setChecked(True)
        self._scope_used.toggled.connect(self._repaint_palette)
        #: The selected-colour swatch is the only swatch with a border of its own,
        #: set in `_refresh_palette_detail`.
        self._scope_caption = QLabel(
            "The object palette is shared across sprites; per-sprite palette "
            "banks are not yet resolved (a later ticket)."
        )
        self._scope_caption.setWordWrap(True)
        self._scope_header = QLabel("Full palette.")
        self._scope_header.setWordWrap(True)
        #: One compact bank of swatches per 16 indices, laid out in a fixed number
        #: of columns. The object palette IS sixteen 16-index rows by its own
        #: structure, so the grid says 16 wide and the bank label carries the row's
        #: own index range; nothing here is re-based.
        self._palette_grid = QGridLayout()
        self._palette_grid.setSpacing(theme.SPACE_MD)
        self._palette_grid.setHorizontalSpacing(theme.SPACE_LG)
        self._palette_grid.setVerticalSpacing(theme.SPACE_MD)
        palette_holder = QWidget()
        palette_holder.setLayout(self._palette_grid)
        #: The palette is the one part of this editor that can be tall, so it lives
        #: in its own scroll area with a bounded height rather than stretching the
        #: workspace. It never occupies half the editor.
        palette_scroll = QScrollArea()
        palette_scroll.setWidget(palette_holder)
        palette_scroll.setWidgetResizable(True)
        palette_scroll.setFrameShape(QFrame.Shape.NoFrame)
        palette_scroll.setMaximumHeight(_PALETTE_MAX_H)
        palette_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        #: Selected-colour detail: the exact technical information for ONE swatch,
        #: shown once. Individual swatches carry no permanent text.
        self._palette_detail = QLabel("")
        self._palette_detail.setProperty("dbzRole", "technical")
        self._palette_detail.setWordWrap(True)
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
        palette_buttons.setContentsMargins(0, 0, 0, 0)
        palette_buttons.setSpacing(theme.SPACE_SM)
        palette_buttons.addWidget(self._apply)
        palette_buttons.addWidget(self._revert)
        palette_buttons.addWidget(self._undo_button)
        palette_buttons.addWidget(self._redo_button)
        palette_buttons.addStretch(1)
        palette_body = QWidget()
        palette_layout = QVBoxLayout(palette_body)
        palette_layout.setContentsMargins(
            theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM, theme.SPACE_SM
        )
        palette_layout.setSpacing(theme.SPACE_XS)
        palette_layout.addWidget(self._scope_used)
        palette_layout.addWidget(self._scope_header)
        palette_layout.addWidget(self._scope_caption)
        palette_layout.addWidget(palette_scroll, 1)
        palette_layout.addWidget(self._palette_detail)
        palette_layout.addLayout(palette_buttons)
        palette_layout.addWidget(self._pending_label)
        # The header says what the panel is; the caption inside says why the
        # scope is what it is. A titled QGroupBox could only do the first.
        palette_header = PanelHeader("Object palette", collapsible=True)
        palette_header.toggled.connect(palette_body.setVisible)
        palette_box = QWidget()
        palette_box_layout = QVBoxLayout(palette_box)
        palette_box_layout.setContentsMargins(0, 0, 0, 0)
        palette_box_layout.setSpacing(0)
        palette_box_layout.addWidget(palette_header)
        palette_box_layout.addWidget(palette_body, 1)

        # -- E. Authored sprite (project-scoped, not selection-scoped) ----------
        # The one surface that CREATES `sprites/sprites.toml`. A project documents
        # at most one new identity, so this is a strip that states the document and
        # offers create/edit/remove - not a collection and not a per-sprite panel.
        self._authored_chip = StateChip("No project open.", "readonly", plain=True)
        # The chip states the STATE in a few words and the summary line below
        # carries the sentence. A wrapping chip in a fixed-height ToolStrip grows
        # to two lines and pushes the strip's buttons outside the visible row,
        # which is what the first visual review of this surface caught.
        self._authored_chip.setWordWrap(False)
        self._authored_chip.setSizePolicy(QSizePolicy.Policy.Preferred,
                                          QSizePolicy.Policy.Fixed)
        self._authored_summary = QLabel("")
        self._authored_summary.setWordWrap(True)
        self._authored_summary.setProperty("dbzRole", "hint")
        self._authored_new = QPushButton("New authored sprite\u2026")
        self._authored_new.clicked.connect(self._on_new_authored_sprite)
        self._authored_edit = QPushButton("Edit\u2026")
        self._authored_edit.clicked.connect(self._on_edit_authored_sprite)
        self._authored_remove = QPushButton("Remove")
        self._authored_remove.clicked.connect(self._on_remove_authored_sprite)
        authored_tips = (
            (self._authored_new, "Create the project's one new actor-sprite identity"),
            (self._authored_edit, "Edit the authored sprite this project already has"),
            (self._authored_remove,
             "Remove the authored sprite from this project; Undo reverses it"),
        )
        for button, tip in authored_tips:
            button.setToolTip(tip)
        authored_strip = ToolStrip()
        authored_strip.add(self._authored_chip)
        authored_strip.add(self._authored_new)
        authored_strip.add(self._authored_edit)
        authored_strip.add(self._authored_remove)
        authored_strip.add_stretch()
        authored_box = QWidget()
        authored_box_layout = QVBoxLayout(authored_box)
        authored_box_layout.setContentsMargins(0, 0, 0, 0)
        authored_box_layout.setSpacing(0)
        authored_box_layout.addWidget(PanelHeader("Authored sprite"))
        authored_box_layout.addWidget(authored_strip)
        authored_box_layout.addWidget(self._authored_summary)
        #: The committed document and the (project, revision) key it was read at, so
        #: a repaint never re-parses the project for a fact that has not moved.
        self._authored = None
        self._authored_key: tuple[str | None, int] | None = None
        #: The project the current undo history belongs to.
        self._authored_project: str | None = None

        # -- Layout: splitter (browser | inspector) over palette + status -----
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(browser)
        splitter.addWidget(inspector)
        # Roughly 3:2 in the browser's favour, as Tiled gives its tile grid the
        # larger share of the pane; the inspector holds one preview and its
        # controls. The collection is the largest surface, which is the priority
        # order the human review set for this editor.
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([820, 600])

        # This label holds this editor's one status line, and it is NOT added to
        # this layout: the shell owns the single physical status bar and mirrors
        # this text into it. Drawing it here as well is what put the same sentence
        # on two rows at the foot of the window.
        self._status = QLabel("Open a ROM to load its sprites.")
        self._status.setProperty("dbzRole", "status")
        self._status.setWordWrap(True)
        self._status.setVisible(False)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(theme.SPACE_SM)
        root.addWidget(splitter, 3)
        root.addWidget(authored_box)
        root.addWidget(palette_box, 2)
        # No session change has happened yet, so the authored-sprite strip states
        # its opening condition here rather than leaving its buttons default-enabled
        # on a window that cannot author anything.
        self._refresh_authored_strip()

    # -- session wiring -------------------------------------------------------

    def on_session_changed(self) -> None:
        """Re-populate from the session (ROM open; a different image's palette)."""
        self._repaint_project_state(clear_pending=True, keep_selection=False)

    def on_project_mutated(self) -> None:
        """A project mutation elsewhere: repaint committed colours, keep pending.

        CQA-05. ``_palette_pending`` is authoring intent the user has chosen on
        the swatches but not applied; an unrelated project write must not
        discard it, so ``clear_pending`` is left False here. A session change
        clears it because a different image's palette is not the palette those
        indices describe, which is a genuinely different event.

        Committed overrides *are* project state and do change, so the decode
        cache is dropped and the grid, palette and selection are repainted from
        the new effective colours - the same refresh ``_after_undo_redo``
        performs, and no more work than the session-change path it replaces.
        """
        if self._emitting_project_change:
            # We are the emitter: this call is the shell answering our own
            # `projectChanged`, and the emitting method has already repainted
            # with this same state. See `_emitting_project_change`.
            return
        self._repaint_project_state(clear_pending=False, keep_selection=True)

    def _repaint_project_state(
        self, *, clear_pending: bool, keep_selection: bool
    ) -> None:
        """The ONE repaint path for every logical edit.

        An Apply, an Undo, a Redo, an unrelated project mutation and a session
        change all need the same thing: the decode cache is stale because the
        effective palette moved, so drop it, rebuild the grid, put the selection
        back, and repaint the palette from the new effective colours. Before
        CQA-07 each caller had its own near-copy of this sequence, and the
        emitters' copy plus the shell's re-entrant copy made every logical edit
        repaint twice. The two flags are the whole difference between the
        callers: a session change drops staged colours and cannot keep a
        selection (a different image's palette is not what those indices
        describe), while a project mutation keeps both.

        The effective palette is read ONCE for the whole repaint, here, and
        threaded to every surface that needs it: the preview render and the
        palette repaint through ``rgb``, and the staged-colour disclosure, which
        only computes its own when it is not handed one. It is computed after
        ``_populate_grid`` and before ``_show_selected`` because that is where
        it becomes available: the palette does not depend on the selection, and
        ``_show_selected`` is what restores the selection and the used-index set
        that the palette repaint then reads. ``None`` (no corpus) flows through
        unchanged, which every callee already handles.
        """
        self._pixmap_cache.clear()
        selected = self._selected
        self._populate_grid()  # clears _selected; repaints every thumbnail
        sprites = self._sprites()
        # ONE effective-palette read for this whole repaint: the grid rebuild
        # above nulled the selection but did not change the palette, so the map
        # is computed here and handed to the preview render and the palette
        # repaint rather than re-read by each of them. None when there is no
        # corpus, in which case every callee already handles it.
        rgb = self._effective_rgb(sprites) if sprites is not None else None
        if keep_selection and selected is not None:
            # refresh_palette=False: the palette is populated once, below, with
            # the effective colours this repaint computes once.
            self._show_selected(selected, refresh_palette=False, rgb=rgb)
        self._populate_palette(clear_pending=clear_pending, rgb=rgb)
        # Re-state the staged-change disclosure from the pending map as it NOW
        # stands, so the panel cannot keep a sentence about a staged colour that
        # has just been applied, undone, redone or dropped. Found in CQA-07's GUI
        # QA: without this the pending line and the enabled Apply/Revert buttons
        # outlived the staged edit they described (pre-existing, not a cost fix).
        # It costs no project read on that path: `_refresh_pending_ui` returns
        # before reading when nothing is staged, and it is handed this repaint's
        # one effective-palette map when something is.
        self._refresh_pending_ui(rgb)
        self._refresh_authored_strip()
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
        # Repopulating drops the selection, so the inspector returns to its empty
        # state rather than keeping detail for a sprite that may no longer exist.
        self._clear_selection()
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

    # -- B. contextual inspector ----------------------------------------------

    def _set_asset_body_visible(self, visible: bool) -> None:
        """Show the asset detail exactly when there is an asset to detail.

        Selection decides what the pane contains: the empty state is one sentence,
        and every dependent surface appears with a selection and disappears without
        one. Nothing renders as a "-" placeholder.
        """
        self._asset_body.setVisible(visible)
        self._asset_empty.setVisible(not visible)

    def _show_selected(
        self,
        identity: GraphicIdentity,
        refresh_palette: bool = True,
        rgb: list[tuple[int, int, int]] | None = None,
    ) -> None:
        """Show one sprite in the inspector.

        ``refresh_palette`` is False on the repaint path, which populates the
        palette itself and must not do it twice. ``rgb`` is the already-computed
        effective palette, threaded to the preview render and to that palette
        repaint so a selection costs ONE project read rather than one per
        surface - the caller has it in hand, so recomputing it here would be a
        whole-project parse spent to obtain a value this call was handed.
        """
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
        self._set_asset_body_visible(True)
        self._export.setEnabled(True)  # a sprite is selected: export is now valid
        if rgb is None:
            rgb = self._effective_rgb(sprites)
        self._preview.setPixmap(
            self._scaled_for_preview(self._pixmap_for(identity, graphic, rgb))
        )
        self._dims.setText(f"{graphic.width} \u00d7 {graphic.height} px")
        self._shared.setText(
            f"{'yes' if graphic.shared else 'no'} "
            f"({len(graphic.consumers)} frame(s))"
        )
        # A count with no caption is enough; the caption only earns its row when
        # there is a value under it, and "0" is a value.
        self._consumers.setText(str(len(graphic.consumers)))
        self._characters.setText(
            ", ".join(str(c.index) for c in graphic.characters) or "none decoded"
        )
        # The palette indices this sprite's pixels actually reference. These are
        # SDK-provided linear indices, not a decoded ROM structure, so reading
        # them is not ROM-format math and claims no hardware palette bank.
        self._used_indices = set(graphic.pixels)
        if refresh_palette:
            # Hand the palette the map we already hold: one effective-palette
            # read per selection, not one per selection-plus-repaint.
            self._populate_palette(rgb=rgb)
        # Load the first using character's animations, if any. The animation pane
        # only exists when the selection actually reaches a character: it is a
        # relation of the selected sprite, not a permanent empty rectangle.
        character = graphic.characters[0] if graphic.characters else None
        self._load_character_animations(character, rgb)
        self._update_status()

    def _clear_selection(self) -> None:
        """Return the inspector to its single-sentence empty state."""
        self._selected = None
        self._used_indices = None
        self._selected_palette_index = None
        self._stop_playback()
        self._set_asset_body_visible(False)
        self._preview.setPixmap(QPixmap())
        self._dims.clear()
        self._shared.clear()
        self._consumers.clear()
        self._characters.clear()
        self._export.setEnabled(False)
        self._update_status()

    def _on_export(self) -> None:
        """Export the selected sprite to an indexed PNG the user picks a path for.

        Encodes through the SDK façade with the EFFECTIVE palette so the file
        matches committed recolours; the widget never touches a codec. The SDK
        call AND the file write share one guard catching the SDK family + OSError,
        so a bad encode or an unwritable path becomes a QMessageBox, never a
        dead-looking click or a terminal traceback (the WB failure mode).

        The destination is checked against the open ROM through the write
        module's shared source-alias policy BEFORE any byte is written: a
        file dialog can be pointed at the ROM that is open, and a save dialog
        happily confirms overwriting it. The GUI owns only this wrapper - the
        rule itself is the SDK's, so it cannot drift from the CLI's.
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
            self._refuse_source_alias(path)
            blob = sprites.export_graphic_png(self._selected, self._effective_rgb(sprites))
            Path(path).write_bytes(blob)
        except (*_SDK_ERRORS, OSError) as exc:
            QMessageBox.critical(self, "Export PNG", str(exc))
            return
        self._status.setText(f"Exported sprite {self._selected.index} to {path}")

    def _refuse_source_alias(self, path) -> None:
        """Refuse an export destination that is the open ROM or an alias of it.

        A no-op when no ROM is open, which is the state the tab is mounted in
        before one is chosen. The rule is the SDK's ``ensure_not_source_alias``;
        this method only supplies the source the widget knows about, so the
        Workbench carries no filesystem-identity logic of its own.
        """
        if self._session.rom_path is None:
            return
        ensure_not_source_alias(self._session.rom_path, path)

    # -- C. animation frame viewer --------------------------------------------

    def _load_character_animations(
        self, character: CharacterIdentity | None, rgb=None
    ) -> None:
        """Load the selected character's animations into the stepper.

        ``rgb`` is the caller's already-computed effective palette, handed to the
        render below. Selecting row 0 is the initial state rather than a user
        choice, so it is done with the combo's signal blocked and the frame
        rendered once, explicitly - otherwise the row change would drive a
        second render that re-read the whole project for a palette this call
        already has.
        """
        self._stop_playback()
        self._anim_select.blockSignals(True)
        self._anim_select.clear()
        self._anim_character = character
        self._animations = ()
        self._anim_index = 0
        self._frame_index = 0
        # The animation controls only exist when the sprite actually reaches a
        # character; they are the animation *of this selection*, not a section.
        self._anim_row_visible = character is not None
        self._anim_list_label.setVisible(self._anim_row_visible)
        self._anim_select.setVisible(self._anim_row_visible)
        self._anim_strip.setVisible(self._anim_row_visible)
        self._timing_note.setVisible(self._anim_row_visible)
        if character is None:
            self._anim_select.blockSignals(False)
            self._frame_label.setText("\u2014")
            # No character: the one preview stays on the sprite itself.
            self._render_selected_sprite(rgb)
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
        if self._animations:
            self._anim_select.setCurrentRow(0)  # still blocked: see the docstring
            self._anim_select.blockSignals(False)
            self._render_frame(rgb)
        else:
            self._anim_select.blockSignals(False)
            self._frame_label.setText("\u2014")
            self._render_selected_sprite(rgb)

    def _render_selected_sprite(self, rgb=None) -> None:
        """Put the selected sprite itself in the one preview.

        ``rgb`` is the caller's already-computed effective palette; only a call
        that has none (a frame-step back to the sprite) computes it here.
        """
        if self._selected is None:
            return
        sprites = self._sprites()
        if sprites is None:
            return
        try:
            graphic = sprites.graphic(self._selected)
        except _SDK_ERRORS:
            return
        if rgb is None:
            rgb = self._effective_rgb(sprites)
        self._preview.setPixmap(
            self._scaled_for_preview(self._pixmap_for(self._selected, graphic, rgb))
        )

    def _on_play_toggled(self, playing: bool) -> None:
        """Start or stop the preview's fixed-cadence playback.

        Presentation only: it advances which frame is shown and never touches ROM
        data, the decoded frame timing (which the SDK reports as unknown) or the
        document. The button's own tooltip says so.
        """
        if playing and self._animations:
            self._paint_timer.start()
        else:
            self._paint_timer.stop()
            self._play.setChecked(False)

    def _stop_playback(self) -> None:
        self._paint_timer.stop()
        self._play.blockSignals(True)
        self._play.setChecked(False)
        self._play.blockSignals(False)

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

    def _render_frame(self, rgb=None) -> None:
        """Draw the current animation frame in the ONE preview.

        There is no second preview: when the selection reaches an animation, this
        is what the single preview shows, and stepping back to the sprite is what
        happens when the selection has no animation at all.

        ``rgb`` is the caller's already-computed effective palette when it has
        one (the selection path); a genuine user frame-step computes it here.
        """
        if not self._animations:
            self._render_selected_sprite(rgb)
            return
        animation = self._animations[self._anim_index]
        frames = animation.frames
        if not frames:
            self._frame_label.setText("\u2014")
            self._render_selected_sprite(rgb)
            return
        frame = frames[self._frame_index]
        # timing_unknown is always True; the label carries no fabricated ms.
        self._frame_label.setText(f"Frame {frame.frame_index + 1} / {len(frames)}")
        sprites = self._sprites()
        if sprites is None:
            return
        if rgb is None:
            rgb = self._effective_rgb(sprites)
        # First direction slot that decoded to a graphic is the shown frame.
        identity = next((g for g in frame.graphics if g is not None), None)
        if identity is None:
            # No art decoded for this frame: fall back to the sprite itself rather
            # than blanking the one preview.
            self._render_selected_sprite(rgb)
            return
        try:
            graphic = sprites.graphic(identity)
            self._preview.setPixmap(
                self._scaled_for_preview(self._pixmap_for(identity, graphic, rgb))
            )
        except _SDK_ERRORS:
            self._render_selected_sprite(rgb)

    # -- D/E. palette editor + pending change ---------------------------------

    def _repaint_palette(self, _checked=False) -> None:
        """Toggle/selection repaint: keep pending edits, just re-scope."""
        self._populate_palette()

    def _clear_palette_grid(self) -> None:
        """Empty the bank grid, and forget the swatches it held."""
        self._swatches = {}
        while self._palette_grid.count():
            item = self._palette_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _populate_palette(self, clear_pending: bool = False, rgb=None) -> None:
        """Lay the object palette out as compact 16-index banks.

        The palette is sixteen 16-index rows by its own structure, so it is drawn
        that way: one labelled bank per row, each a dense 4x4 block of small
        swatches, and the blocks wrap across the pane instead of stacking into a
        tower. A tall column-per-colour display read as a diagnostic chart and took
        half the workspace; this costs one bounded scroll area instead.

        Semantics are untouched: the index on every swatch is its true global
        index, the scope toggle still switches between the sprite's own colours and
        the whole shared palette, and a pending recolour still previews on top of
        the effective colour.

        ``rgb`` is an already-computed effective palette from a caller that has
        one (`_show_selected`). One repaint reads the committed override map ONCE
        and hands the result to every swatch and to the detail line; before
        CQA-07 each of the 256 swatches re-read and re-parsed the whole project to
        find the map this method had computed one line earlier.
        """
        if clear_pending:
            self._palette_pending.clear()
        self._clear_palette_grid()
        sprites = self._sprites()
        if sprites is None:
            self._scope_header.setText("Open a ROM to load its palette.")
            self._palette_detail.setText("")
            return
        if rgb is None:
            rgb = self._effective_rgb(sprites)

        scoped = self._scope_used.isChecked() and self._used_indices is not None
        if scoped:
            indices = sorted(i for i in self._used_indices if 0 <= i < len(rgb))
            self._scope_header.setText(
                f"Colours used by sprite #{self._selected.index} "
                f"({len(indices)} of {len(rgb)} indices)"
                if self._selected is not None
                else f"Colours used by this sprite ({len(indices)} indices)"
            )
            self._scope_caption.setVisible(True)
        else:
            indices = list(range(len(rgb)))
            if self._used_indices is None:
                self._scope_header.setText(
                    f"Shared object palette, {len(rgb)} indices "
                    "(select a sprite to scope it)"
                )
            else:
                self._scope_header.setText(
                    f"Shared object palette, {len(rgb)} indices"
                )
            self._scope_caption.setVisible(False)

        # Group the indices into banks. In scoped mode the banks are the contiguous
        # runs of the subset, which keeps a bank's label honest about its range.
        banks: list[tuple[int, list[int]]] = []
        for index in indices:
            bank_start = (index // _SWATCH_COLUMNS) * _SWATCH_COLUMNS
            if not banks or banks[-1][0] != bank_start:
                banks.append((bank_start, []))
            banks[-1][1].append(index)

        for position, (bank_start, members) in enumerate(banks):
            block_row, block_column = divmod(position, _PALETTE_BANK_COLUMNS)
            block = self._palette_bank(bank_start, members, scoped, rgb)
            # Aligned left and top in its cell, and the columns take no stretch, so
            # the banks pack together instead of spreading across the pane. A bank
            # is a dense block; spacing it out would make it read as a chart again.
            self._palette_grid.addWidget(
                block,
                block_row,
                block_column,
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            )
        for column in range(_PALETTE_BANK_COLUMNS):
            self._palette_grid.setColumnStretch(column, 0)
        self._palette_grid.setColumnStretch(_PALETTE_BANK_COLUMNS, 1)
        self._refresh_palette_detail(rgb)

    def _palette_bank(
        self, bank_start: int, members: list[int], scoped: bool, rgb
    ) -> QWidget:
        """One labelled bank: a 4x4 block of the 16 indices it holds."""
        bank = QWidget()
        layout = QVBoxLayout(bank)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        last = members[-1] if members else bank_start
        caption = QLabel(f"{bank_start:03d}\u2013{last:03d}")
        caption.setProperty("dbzRole", "technical")
        caption.setToolTip(
            f"Object palette indices {bank_start} to {bank_start + _SWATCH_COLUMNS - 1}"
        )
        layout.addWidget(caption)
        grid = QGridLayout()
        grid.setSpacing(1)
        layout.addLayout(grid)
        for position, index in enumerate(members):
            row, column = divmod(position, _BANK_EDGE)
            swatch = self._palette_swatch(index, scoped, rgb)
            # Keyed by the TRUE global index, so a pending recolour and the
            # repaint path address the real palette entry even in scoped view.
            self._swatches[index] = swatch
            grid.addWidget(swatch, row, column)
        return bank

    def _palette_swatch(self, index: int, scoped: bool, rgb) -> QFrame:
        # The effective palette comes from the caller's single read per repaint:
        # 256 swatches must not each re-read and re-parse the whole project.
        r, g, b = rgb[index]
        # Pending (uncommitted) edits preview on top of the effective colour.
        if index in self._palette_pending:
            r, g, b = self._palette_pending[index]
        swatch = QFrame()
        swatch.setFixedSize(_SWATCH, _SWATCH)
        swatch.setFrameShape(QFrame.Shape.Box)
        # The index is in the tooltip, and the selected colour's exact values are
        # in the one detail line below the grid. A swatch carries no permanent text:
        # 256 numbered labels read as a chart, not as a palette.
        swatch.setToolTip(
            f"Palette index {index}\n#{r:02X}{g:02X}{b:02X}"
            + ("\nclick to recolour" if scoped or self._used_indices is not None else "")
        )
        self._paint_swatch(swatch, r, g, b)
        swatch.mousePressEvent = self._swatch_click(index)
        return swatch

    def _refresh_palette_detail(self, rgb=None) -> None:
        """The one line of detail for the selected swatch, or nothing.

        ``rgb`` is the caller's already-computed effective palette when it has
        one, so the detail line costs no extra project read on the repaint path
        or on a colour pick; a caller with none (the direct QA seam) computes it.
        """
        index = self._selected_palette_index
        sprites = self._sprites()
        if index is None or sprites is None:
            self._palette_detail.setText("")
            return
        if rgb is None:
            rgb = self._effective_rgb(sprites)
        r, g, b = rgb[index]
        parts = [f"Selected index {index}", f"#{r:02X}{g:02X}{b:02X}"]
        if index in self._palette_pending:
            nr, ng, nb = self._palette_pending[index]
            parts.append(f"pending \u2192 #{nr:02X}{ng:02X}{nb:02X}")
        self._palette_detail.setText("  \u00b7  ".join(parts))
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
        self._selected_palette_index = index
        # ONE effective-palette read for the whole click: it seeds the dialog's
        # current colour, the detail line and the pending "from" colour. Reading
        # it once per surface was three whole-project parses inside one handler.
        rgb = self._effective_rgb(sprites)
        current = self._palette_pending.get(index) or rgb[index]
        chosen = QColorDialog.getColor(
            QColor(*current), self, f"Recolour palette index {index}"
        )
        if not chosen.isValid():
            self._refresh_palette_detail(rgb)
            return
        self._palette_pending[index] = (chosen.red(), chosen.green(), chosen.blue())
        swatch = self._swatches.get(index)
        if swatch is not None:
            self._paint_swatch(swatch, chosen.red(), chosen.green(), chosen.blue())
        self._refresh_pending_ui(rgb)

    def _refresh_pending_ui(self, rgb=None) -> None:
        """Re-state every staged recolour, and disclose its known consumers.

        ``rgb`` is the caller's already-computed effective palette when it has
        one; the "from" colour is the effective colour before this pending edit
        (committed override if any, else canonical), never the raw ROM word.
        """
        pending = bool(self._palette_pending)
        self._revert.setEnabled(pending)
        self._apply.setEnabled(pending and self._session.project_dir is not None)
        self._refresh_palette_detail(rgb)
        if not pending:
            self._pending_label.setText("No pending palette change.")
            return
        sprites = self._sprites()
        effective = rgb
        if effective is None and sprites is not None:
            effective = self._effective_rgb(sprites)
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
            prior = self._prior_overrides(pending)
            # ONE batch write for the whole gesture, not one whole-project
            # read+write per staged index.
            self._write_overrides(pending)
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

    def _prior_overrides(self, indices) -> dict[int, tuple[int, int, int] | None]:
        """The prior authored rgb for each index, or None where unauthored.

        Read in `_on_apply` before the write and handed to the command, so undo
        can reverse to it (None -> remove the override). ONE project load for the
        whole batch, because the SDK already returns the committed map in one
        read; a per-index read reloaded the project once per staged colour.
        Raises the SDK family / ProjectError / OSError on failure, caught by
        `_on_apply`'s guard before anything is pushed onto the stack.
        """
        profile = self._session.profile
        if self._session.project_dir is None or profile is None:
            return {index: None for index in indices}
        committed = graphics_sdk.get_palette_overrides(
            self._session.project_dir, profile
        )
        return {index: committed.get(index) for index in indices}

    def _write_overrides(
        self, colours: dict[int, tuple[int, int, int] | None]
    ) -> bool:
        """Persist a whole batch of recolours through the SDK.

        The one write path for an Apply, an Undo and a Redo: `None` in the batch
        means "remove this index", which is how an undo of a never-authored index
        reverses. Returns whether the project source changed.
        """
        profile = self._session.profile
        return graphics_sdk.set_palette_overrides(
            self._session.project_dir, profile, colours
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

        The pending map is cleared FIRST: the edit is durable now - `_on_apply`
        wrote it before the push, and a redo/undo wrote it just above - so any
        staged intent for those indices is superseded, and the repaint below must
        not paint it back on top of the durable colour.
        """
        self._palette_pending.clear()
        self._session.project_mutated()
        # The emitting method repaints itself at the end of this call, so the
        # shell's re-entrant `on_project_mutated()` on THIS tab is suppressed for
        # exactly the duration of the emission. The signal is not suppressed at
        # all: every other peer still receives it.
        self._emitting_project_change = True
        try:
            self.projectChanged.emit()
        finally:
            self._emitting_project_change = False
        self._repaint_project_state(clear_pending=True, keep_selection=True)

    def _on_revert(self) -> None:
        """Discard unapplied swatch edits and repaint from the ROM palette."""
        self._palette_pending.clear()
        self._populate_palette()
        # The staged set is now empty, so re-state the disclosure from it: the
        # same QA-found staleness the repaint path resets (the pending sentence
        # and the enabled Apply/Revert outliving the edit they described). Costs
        # no project read, because nothing is staged.
        self._refresh_pending_ui()

    # -- E. authored sprite ---------------------------------------------------

    def _refresh_authored_strip(self) -> None:
        """State the project's authored-sprite document, read once per revision.

        The document is project state and can move from anywhere - an undo here,
        another editor, a reopened project - so it is re-read whenever the project
        directory or the project revision moves, and never on a plain repaint.
        """
        project = self._session.project_dir
        project_key = str(project) if project is not None else None
        if project_key != self._authored_project:
            self._authored_project = project_key
            # A history entry names ONE project's document. Carrying the stack
            # across an Open Project would let Undo write the old project's
            # document into the new one, so the history goes with the project.
            if self._undo_stack.count():
                self._undo_stack.clear()
        key = (project_key, self._session.project_revision)
        if key == self._authored_key:
            return
        self._authored_key = key
        sprite = None
        problem = None
        if project is not None:
            try:
                sprite = sprite_sdk.authored_sprite(project)
            except (*_SDK_ERRORS, ProjectError, OSError) as exc:
                problem = str(exc)
        self._authored = sprite
        if problem is not None:
            self._authored_chip.set_state("Project unreadable.", "invalid")
            self._authored_summary.setText(problem)
            available = False
        elif not self._authoring_available():
            self._authored_chip.set_state("Authoring not available.", "readonly")
            self._authored_summary.setText(
                "Authoring a new sprite needs an open image whose profile declares "
                "actor sprites, and a project extracted from that image.")
            available = False
        elif sprite is None:
            self._authored_chip.set_state("No authored sprite.", "neutral")
            self._authored_summary.setText(
                "A new actor-sprite identity is content the image does not contain: "
                "its own animation slots and frames, drawn by one appended map actor. "
                "One image hosts one such identity per build.")
            available = True
        else:
            self._authored_chip.set_state(f"Authored: {sprite.name}", "saved")
            self._authored_summary.setText(
                f"{sprite.identity} - engine id {sprite.sprite_id}, donor sprite "
                f"{sprite.donor_sprite_id}, {len(sprite.animations)} animation slot(s), "
                f"actor on {sprite.actor.map} with behaviour template "
                f"{sprite.actor.behaviour_template}. A change here makes the current "
                "validation and build stale.")
            available = True
        self._authored_new.setEnabled(available)
        self._authored_edit.setEnabled(available and sprite is not None)
        self._authored_remove.setEnabled(available and sprite is not None)

    def _authoring_available(self) -> bool:
        session = self._session
        return (session.project_dir is not None
                and session.profile is not None
                and session.map_image is not None)

    def _open_authored_dialog(self, *, editing: bool) -> None:
        if self._session.project_dir is None:
            QMessageBox.information(
                self, "Authored sprite",
                "Open or extract a project first: a new sprite is written into the "
                "project, not into the ROM.")
            return
        dialog = SpriteAuthoringDialog(self, self._session, editing=editing)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        document = dialog.document()
        if document is None:
            return
        self._commit_authored_sprite(document, dialog.windowTitle())

    def _on_new_authored_sprite(self) -> None:
        self._open_authored_dialog(editing=False)

    def _on_edit_authored_sprite(self) -> None:
        self._open_authored_dialog(editing=True)

    def _on_remove_authored_sprite(self) -> None:
        if self._session.project_dir is None or self._authored is None:
            return
        confirm = QMessageBox.question(
            self, "Remove authored sprite",
            f"Remove {self._authored.identity} from this project? The sheets it "
            "draws from stay on disk; the project stops authoring the identity. "
            "Undo reverses this.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._commit_authored_sprite(AuthoredSprites(), "Remove authored sprite")

    def _commit_authored_sprite(self, document: AuthoredSprites, label: str) -> None:
        """Write the document, then record it as one undoable project mutation.

        The write runs HERE, before the push, so an SDK failure is caught by this
        guard and the history is left untouched (`AuthoredSpriteCommand`). A
        document identical to the committed one writes nothing, records no history
        entry and bumps no revision: an unchanged save must not make a good
        validation or a good build stale.
        """
        project = self._session.project_dir
        try:
            prior = read_project(project).sprites
            changed = self._write_authored_document(document)
        except _SPRITE_ERRORS as exc:
            QMessageBox.critical(self, "Authored sprite", str(exc))
            return
        if not changed:
            return
        self._after_authored_change()
        self._undo_stack.push(
            AuthoredSpriteCommand(self, project, prior, document, label))

    def _write_authored_document(self, document: AuthoredSprites) -> bool:
        """The one write path for the authored-sprite document."""
        return sprite_sdk.apply_authored_sprite(self._session.project_dir, document)

    def _after_authored_change(self) -> None:
        """Post-commit refresh: session currency, peers, and this tab's strip.

        Touching the project bumps the revision and re-arms Validate and Build, the
        contract every authoring surface follows. The palette is deliberately NOT
        repainted: the effective colours have not moved, so re-decoding the grid
        would be work for nothing.
        """
        self._session.project_mutated()
        self._emitting_project_change = True
        try:
            self.projectChanged.emit()
        finally:
            self._emitting_project_change = False
        self._refresh_authored_strip()
        self._update_status()

    # -- status line ----------------------------------------------------------

    def _update_status(self) -> None:
        """This editor's own line: what it is showing, and nothing the shell says.

        Validation, build and project state are *project* state and live in the
        shell's status bar, which is visible from every editor. Repeating them here
        printed the same fact twice on one line ("... no project open" beside the
        bar's own "no project"). What is left is what only this editor knows: which
        sprite is selected and what the palette scope is showing.

        One authoritative line: it is set here and published in the same call, so
        this editor's own label and the shell's bar can never disagree.
        """
        sprites = self._sprites()
        if sprites is None:
            text = "Open a ROM to load its sprites."
        else:
            parts = []
            if self._selected is not None:
                parts.append(f"sprite {self._selected.index} selected")
            else:
                parts.append(f"{self._grid.count()} sprites \u00b7 no selection")
            if self._used_indices is not None:
                parts.append(f"{len(self._used_indices)} palette colour(s) in use")
            text = "  \u00b7  ".join(parts)
        self._status.setText(text)
        self.statusChanged.emit(text)
