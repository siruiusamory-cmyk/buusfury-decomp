"""The chip atoms and the in-game preview.

The chip cases run off plain strings. The preview cases run over a SYNTHETIC image
built by `tests.unit.test_dialogue_render`, so the decode, the layout, the pane's
states and the pane's live repaint are all exercised without a ROM and without one
byte of game data committed. The one case that needs the real image is in
`test_dialogue_render.py`, which skips loudly without it.
"""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QMimeData, Qt  # noqa: E402
from PySide6.QtGui import QColor, QImage, QKeyEvent, QTextCursor  # noqa: E402
from PySide6.QtWidgets import QApplication, QTextEdit  # noqa: E402

from tests.text_fixture import appearances, open_image, simple, speaking_image  # noqa: E402
from tests.unit.test_dialogue_render import (  # noqa: E402
    BOX_FILLS,
    GLYPH_ADVANCE,
    synthetic_image,
)
from tools.buufury_text import chips, contextpane, preview, theme  # noqa: E402
from tools.buufury_text import session as app_session  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402

QAPP = QApplication.instance() or QApplication([])

#: Two prose runs around an interior 0x0A, then a 0x08 unit with an operand.
CURRENT = "AB\nCD\x08\x03EF"
ATOMS = ((2, 3), (5, 7))
#: The pane's own margin around the surface, which is where the box's first pixel is.
MARGIN = 8


def _key(widget, key: Qt.Key.Key) -> None:
    QAPP.sendEvent(widget, QKeyEvent(QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier))
    QAPP.processEvents()


def _type(widget, text: str) -> None:
    """One printable character through the widget's own key route."""
    QAPP.sendEvent(widget, QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_unknown,
                                     Qt.KeyboardModifier.NoModifier, text))
    QAPP.processEvents()


def _caret(widget: QTextEdit, position: int) -> None:
    cursor = widget.textCursor()
    cursor.setPosition(position)
    widget.setTextCursor(cursor)


# --- atom_ranges and control_label -------------------------------------------


def test_atom_ranges_names_every_control_unit() -> None:
    assert chips.atom_ranges(CURRENT) == ATOMS
    assert chips.atom_ranges("plain prose") == ()
    assert chips.atom_ranges("") == ()
    assert chips.atom_ranges("\n") == ((0, 1),)
    assert chips.atom_ranges("\x08\x03") == ((0, 2),)


def test_control_label_names_the_units_the_catalogue_will_replace() -> None:
    assert chips.control_label("\n") == "\u21b5"
    assert chips.control_label("\x08\x03") == "{08:03}"
    assert chips.control_label("\x0b") == "000B"
    assert chips.control_label("") == ""


# --- protected_edit refusals -------------------------------------------------


def test_protected_edit_refuses_typing_inside_an_atom() -> None:
    for atom in ATOMS:
        for at in range(*atom):
            assert chips.protected_edit(CURRENT, at, 0, "Q") == CURRENT


def test_protected_edit_refuses_backspace_at_each_edge_of_an_atom() -> None:
    for start, stop in ATOMS:
        assert chips.protected_edit(CURRENT, start, 1, "") == CURRENT
        assert chips.protected_edit(CURRENT, stop - 1, 1, "") == CURRENT
    assert chips.protected_edit(CURRENT, 6, 1, "") == CURRENT


def test_protected_edit_refuses_a_removal_that_contains_a_whole_atom() -> None:
    assert chips.protected_edit(CURRENT, 1, 4, "") == CURRENT
    assert chips.protected_edit(CURRENT, 0, len(CURRENT), "") == CURRENT


def test_protected_edit_refuses_an_insertion_that_carries_a_control_unit() -> None:
    assert chips.protected_edit(CURRENT, 0, 0, "\x08\x03") == CURRENT
    assert chips.protected_edit(CURRENT, 0, 0, "\n") == CURRENT


def test_protected_edit_refuses_a_lone_high_surrogate() -> None:
    assert chips.protected_edit(CURRENT, 0, 0, "\ud800") == CURRENT
    assert chips.protected_edit(CURRENT, 0, 0, "\ud800\udc00") != CURRENT


def test_protected_edit_allows_ordinary_typing_and_deletion() -> None:
    assert chips.protected_edit(CURRENT, 0, 0, "X") == "X" + CURRENT
    assert chips.protected_edit(CURRENT, 0, 1, "") == CURRENT[1:]
    assert chips.protected_edit(CURRENT, 3, 2, "") == "AB\n" + CURRENT[5:]
    # A deletion that reaches past the atom is still refused.
    assert chips.protected_edit(CURRENT, 3, 3, "") == CURRENT
    # A paste of plain prose at a boundary is allowed and lands whole.
    assert chips.protected_edit(CURRENT, 4, 0, "hello ") == "AB\nChello D\x08\x03EF"


# --- the widget ---------------------------------------------------------------


def test_chip_edit_round_trips_the_canonical_string() -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    assert editor.serialized() == CURRENT
    assert editor.atom_count() == len(ATOMS)
    editor.set_text("plain prose")
    assert editor.serialized() == "plain prose"
    assert editor.atom_count() == 0


def test_a_document_with_a_control_unit_lays_out_and_round_trips() -> None:
    """The atom's size and paint stubs must match the binding's own argument order.

    Measured, and this is why the case lays the document out: Qt calls
    `intrinsicSize(self, doc, posInDocument, format)` and `drawObject(self, painter,
    rect, doc, posInDocument, format)`, positionally. A stub declared without the
    position argument binds the format to an integer and raises inside the Qt
    override, but ONLY once the document actually lays out, which a widget that is
    never shown never does. The round-trip case beside this one passed while the
    editor could not open a line carrying a control unit at all, and a commit from
    that state wrote the previous row's text under the new row's key.
    """
    editor = chips.ChipTextEdit()
    editor.resize(280, 90)
    editor.show()
    editor.set_text(CURRENT)
    assert editor.serialized() == CURRENT
    assert editor.atom_count() == len(ATOMS)
    # Reading the laid-out size is what forces the two overrides to run.
    assert editor.document().size().width() > 0
    assert editor.document().size().height() > 0
    editor.close()


@pytest.mark.parametrize("text", [
    "Line one end",
    "Line one \x08\x0B end",
    "\x08\x0BLine one end",
    "\x08\x0Bmid\x08\x0Btail",
    "Line one end\x08\x0B",
])
def test_typing_at_the_end_of_a_line_with_a_control_unit_lands_at_the_end(text) -> None:
    """A document position is not a string position, and the difference is one each.

    A control unit is two characters in the canonical string and one character in the
    document, so handing a document position to a string function puts the edit one
    character early for every unit before the caret. Measured on the shipping widget
    before this case existed: typing at the end of `Line one <unit> end` produced
    `Line one <unit> enXYZd`, the two-unit line landed two characters early, and a line
    ENDING in a unit refused the keystroke and said nothing at all.
    """
    editor = chips.ChipTextEdit()
    editor.resize(300, 90)
    editor.show()
    editor.set_text(text)
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    editor.setTextCursor(cursor)
    said: list[str] = []
    editor.refused.connect(said.append)
    editor.insertPlainText("XYZ")
    assert editor.serialized() == text + "XYZ"
    assert said == []
    # The same line still refuses an insertion INTO an atom, and says why.
    if chips.atom_ranges(text):
        start, _end = chips.atom_ranges(text)[0]
        caret = editor.textCursor()
        caret.setPosition(chips.document_index(text + "XYZ", start + 1))
        editor.setTextCursor(caret)
        editor.insertPlainText("!")
        assert editor.serialized() == text + "XYZ"
        assert said == [chips.BREAKS_LOCK]
    editor.close()


def test_chip_edit_refuses_a_backspace_at_an_atom_edge() -> None:
    editor = chips.ChipTextEdit()
    editor.set_text(CURRENT)
    _caret(editor, 3)
    _key(editor, Qt.Key.Key_Backspace)
    assert editor.serialized() == CURRENT
    _caret(editor, 1)
    _key(editor, Qt.Key.Key_Backspace)
    assert editor.serialized() == "B\nCD\x08\x03EF"


def test_chip_edit_refuses_a_paste_that_carries_an_atom() -> None:
    editor = chips.ChipTextEdit()
    editor.set_text("hello")
    _caret(editor, 5)
    source = QMimeData()
    source.setText("world\x08\x03")
    assert editor.canInsertFromMimeData(source) is False
    source.setText("world")
    assert editor.canInsertFromMimeData(source) is True


def test_chip_edit_reports_every_accepted_edit() -> None:
    editor = chips.ChipTextEdit()
    editor.set_text("hello")
    seen: list[str] = []
    editor.edited.connect(seen.append)
    _caret(editor, 5)
    _type(editor, "X")
    assert editor.serialized() == "helloX"
    assert seen == ["helloX"]


# --- the in-game preview ------------------------------------------------------


def pane(image: bytes | None = None, name: str = "", text: str = "") -> preview.DialoguePreview:
    """A pane over one image, sized so its own paint path runs at scale 1."""
    widget = preview.DialoguePreview()
    widget.resize(preview.SURFACE_WIDTH + 2 * MARGIN, preview.SURFACE_HEIGHT + 2 * MARGIN)
    widget.set_image(image, name)
    widget.set_text(text)
    return widget


def shot(widget) -> QImage:
    """The pane's own canvas, painted through the widget's paintEvent."""
    image = QImage(widget.size(), QImage.Format.Format_ARGB32)
    image.fill(QColor("#000000"))
    widget.render(image)
    return image


def pixels(widget) -> bytes:
    """The pane's canvas as bytes, for an equality that does not depend on QImage."""
    return bytes(shot(widget).constBits())


def canvas_colours(widget) -> set[str]:
    image = shot(widget)
    return {image.pixelColor(x, y).name() for y in range(image.height())
            for x in range(image.width())}


def engine_colours() -> set[str]:
    """Every colour the engine's own render can put on the canvas in these cases."""
    palette = preview.decode_palette(bytes(synthetic_image()))
    return {QColor(*palette[index]).name()
            for index in (preview.DEFAULT_INK, *BOX_FILLS.values())}


def test_the_waiting_state_draws_no_box_and_no_glyph() -> None:
    widget = pane()
    assert widget.state() == "waiting"
    assert widget.missing() == ("an open image",)
    assert widget.ready() is False
    assert widget.source_name() == "waiting"
    # Room for the waiting line plus the wrapped list of what is absent.
    assert widget.sizeHint().width() == 260
    assert not (canvas_colours(widget) & engine_colours()), \
        "the waiting state drew part of the engine's own surface"


def test_an_image_whose_font_will_not_decode_is_waiting_and_names_the_font() -> None:
    widget = pane(b"not an image at all")
    assert widget.state() == "waiting"
    assert widget.missing() == ("the font at 0x6EE6C (the descriptor is outside the image)",)
    assert not (canvas_colours(widget) & engine_colours())


def test_an_image_whose_box_will_not_decode_is_waiting_and_names_the_box() -> None:
    image = synthetic_image()
    # A stored container of the wrong length where the 128 box's container lives.
    blob = webfoot_lz.build_stored(bytes(preview.SURFACE_BYTES // 10))
    offset = preview.BOX_ART[128]
    image[offset:offset + len(blob)] = blob
    widget = pane(bytes(image), "shot.gba", "A")
    assert widget.state() == "waiting"
    assert widget.missing()[0].startswith("the box art at 0x71A6C")
    assert not (canvas_colours(widget) & engine_colours()), \
        "a failed box decode drew something anyway"


def test_a_ready_pane_paints_the_engines_own_surface() -> None:
    image = bytes(synthetic_image())
    widget = pane(image, "shot.gba", "A")
    assert widget.state() == "ready", widget.missing()
    assert widget.missing() == ()
    assert widget.source_name() == "shot.gba"
    assert widget.sizeHint().width() == preview.SURFACE_WIDTH + 2 * MARGIN
    palette = preview.decode_palette(image)
    canvas = shot(widget)
    x, y = preview.TEXT_ORIGIN
    assert canvas.pixelColor(MARGIN + x, MARGIN + y).name() == \
        QColor(*palette[preview.DEFAULT_INK]).name()
    assert canvas.pixelColor(MARGIN + x + GLYPH_ADVANCE, MARGIN + y).name() == \
        QColor(*palette[BOX_FILLS[128]]).name()


def test_the_portrait_operand_selects_which_box_is_drawn() -> None:
    image = bytes(synthetic_image())
    widget = pane(image, "shot.gba", "A")
    palette = preview.decode_palette(image)
    assert shot(widget).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[128]]).name()
    widget.set_portrait(0x3F)
    assert shot(widget).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[144]]).name()


def test_a_record_the_box_cannot_hold_is_limited_and_draws_nothing() -> None:
    widget = pane(bytes(synthetic_image()), "shot.gba", "A" * 200)
    assert widget.state() == "limited"
    assert widget.missing() == (preview.SCROLL_RULE,)
    assert widget.ready() is False
    assert not (canvas_colours(widget) & engine_colours()), \
        "the limited state drew part of a window it refuses to guess"


def test_the_pane_scales_by_whole_pixels_and_never_in_between() -> None:
    image = bytes(synthetic_image())
    small = pane(image, "shot.gba", "A" * 120)
    large = preview.DialoguePreview()
    large.resize(2 * preview.SURFACE_WIDTH + 2 * MARGIN,
                 2 * preview.SURFACE_HEIGHT + 2 * MARGIN)
    large.set_image(image, "shot.gba")
    large.set_text("A" * 120)
    one, two = shot(small), shot(large)
    # Every 2x2 block is one pixel of the 1x render: a fractional stretch breaks this.
    for y in range(preview.SURFACE_HEIGHT):
        for x in range(preview.SURFACE_WIDTH):
            source = one.pixel(MARGIN + x, MARGIN + y)
            for dy in range(2):
                for dx in range(2):
                    assert two.pixel(MARGIN + 2 * x + dx, MARGIN + 2 * y + dy) == source


def test_the_pane_repaints_as_the_text_changes_and_only_then() -> None:
    widget = pane(bytes(synthetic_image()), "shot.gba", "A")
    first = pixels(widget)
    assert pixels(widget) == first
    widget.set_text("AA")
    assert pixels(widget) != first
    # A trailing space advances the cursor and draws nothing, which is the engine's
    # own rule for a space: the surface is the one for the text without it.
    widget.set_text("A ")
    assert pixels(widget) == first


# --- the pane the window actually builds --------------------------------------


def lined(model) -> app_session.Session:
    """A real session in the LINES view over one fixture's own records.

    Only the image BYTES are the preview's synthetic ones: a text fixture carries no
    font descriptor and no box art, so the pane would have nothing to decode.
    """
    return app_session.Session(replace(model, image=bytes(synthetic_image())),
                               cutters_from_pool=False)


def test_the_context_pane_hands_the_preview_the_image_it_opened(tmp_path: Path) -> None:
    """The wiring the preview cannot test on its own: the image in, the portrait in."""
    _bytes, model = simple(tmp_path)
    session = lined(model)
    panel = contextpane.ContextPane(theme.active_theme(), theme.metrics(QAPP))
    row = session.rows_of(app_session.LINES)[0]
    panel.set_line(session, row)
    panel.set_preview_state(row.text)
    assert panel.preview.state() == "ready", panel.preview.missing()
    assert panel.preview.source_name() == model.path.name
    palette = preview.decode_palette(session.model.image)
    # The box on screen is the one this record's own portrait selects, which is what
    # says the operand reached the preview rather than being dropped on the way.
    portrait = session.portraits.get(row.target or row.key)
    operand = None if portrait is None else portrait.operand
    assert shot(panel.preview).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[preview.box_for(operand)]]).name()


def test_the_context_pane_passes_the_records_portrait_operand_to_the_preview(
        tmp_path: Path) -> None:
    with appearances():
        model = open_image(speaking_image("A"), tmp_path)
    session = lined(model)
    panel = contextpane.ContextPane(theme.active_theme(), theme.metrics(QAPP))
    row = session.rows_of(app_session.LINES)[0]
    operand = session.portraits.get(row.target or row.key)
    assert operand is not None, "the fixture carries no portrait, so this proves nothing"
    panel.set_line(session, row)
    assert panel.preview.state() == "ready", panel.preview.missing()
    palette = preview.decode_palette(session.model.image)
    assert shot(panel.preview).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[144]]).name()


def test_the_context_pane_clears_the_preview_when_no_line_is_selected(tmp_path: Path) -> None:
    _bytes, model = simple(tmp_path)
    session = lined(model)
    panel = contextpane.ContextPane(theme.active_theme(), theme.metrics(QAPP))
    panel.set_line(session, session.rows_of(app_session.LINES)[0])
    assert panel.preview.ready()
    panel.set_line(None, None)
    assert panel.preview.state() == "waiting"
    assert panel.preview.missing() == ("an open image",)
