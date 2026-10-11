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

from PySide6.QtCore import QBuffer, QIODevice, QMimeData, Qt  # noqa: E402
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


def test_protected_edit_allows_typing_at_an_atoms_edges_and_refuses_inside_it() -> None:
    """FINDING 2: a caret at an atom's start is a legitimate place to type.

    Only an insertion STRICTLY inside a unit is refused. Measured before the fix:
    `protected_edit(CURRENT, 2, 0, "Q")` returned the text unchanged, so a caret just
    before a control unit could not be typed into at all.
    """
    for start, stop in ATOMS:
        assert chips.protected_edit(CURRENT, start, 0, "Q") == \
            CURRENT[:start] + "Q" + CURRENT[start:]
        assert chips.protected_edit(CURRENT, stop, 0, "Q") == \
            CURRENT[:stop] + "Q" + CURRENT[stop:]
    # Only the 0x08-plus-operand unit has an interior position, and only it refuses.
    assert chips.protected_edit(CURRENT, 6, 0, "Q") == CURRENT


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
    # FINDING 1: 0x0A, 0x0B and every other unit below 0x20 without an operand is ONE
    # canonical character, where 0x08 plus its operand is two.
    "Line one \x0b end",
    "\x0bLine one end",
    "Line one end\x0b",
    "\x0bmid\x0bLine one end",
    "\x0bmid\x08\x0Btail",
])
def test_typing_at_the_end_of_a_line_with_a_control_unit_lands_at_the_end(text) -> None:
    """A document position is not a string position, and the difference is per unit.

    A control unit is `len(unit.raw)` canonical characters - two for 0x08 plus its
    operand, one for every other unit - and one character in the document, so handing
    a document position to a string function puts the edit one character early for
    every two-character unit before the caret. Measured on the shipping widget before
    this case existed: typing at the end of `Line one <unit> end` produced
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
    # FINDING 1, mid-line: the caret just AFTER the unit is the position the mapping
    # read one character late, and clamping the end position hid that. Measured before
    # the fix: `ab<0x0B>cd` at document position 3 produced `ab<0x0B>cXd`, one
    # character late, and `Line one <0x0B> end` produced `Line one <0x0B>!end`.
    if chips.atom_ranges(text):
        _start, stop = chips.atom_ranges(text)[0]
        caret = editor.textCursor()
        caret.setPosition(chips.document_index(text + "XYZ", stop))
        editor.setTextCursor(caret)
        editor.insertPlainText("!")
        assert editor.serialized() == text[:stop] + "!" + text[stop:] + "XYZ"
        assert said == []
    editor.close()


def test_typing_at_a_control_unit_start_lands_before_it_and_is_not_refused() -> None:
    """FINDING 2, through the widget: the keystroke at a unit's start was dropped.

    Measured before the fix: a caret at the unit's own start followed by
    `insertPlainText("X")` left `ab<0x0B>cd` unchanged and emitted `BREAKS_LOCK`, so a
    legitimate caret in front of a control unit could not be typed into at all.
    """
    editor = chips.ChipTextEdit()
    editor.resize(300, 90)
    editor.show()
    editor.set_text("ab\x0bcd")
    said: list[str] = []
    editor.refused.connect(said.append)
    caret = editor.textCursor()
    caret.setPosition(chips.document_index("ab\x0bcd", 2))
    editor.setTextCursor(caret)
    editor.insertPlainText("X")
    assert editor.serialized() == "abX\x0bcd"
    assert said == []
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
    """The pane's canvas as bytes, for an equality that does not depend on QImage.

    The image is ENCODED rather than read through `constBits()`. Measured: the raw buffer
    view came back one byte off at its start on roughly three runs in four when this case
    was selected alone, so two grabs of an unchanged widget compared unequal and the case
    read as a repaint that never happened. The encoded form of one image is one byte
    string, so the comparison is about the pixels and not about how the buffer was read.
    """
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    shot(widget).save(buffer, "PNG")
    return bytes(buffer.data())


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
    # A stored container of the wrong length where the 128 box's container lives, with
    # the operand that selects that layout so the decode of it is what is attempted.
    blob = webfoot_lz.build_stored(bytes(preview.SURFACE_BYTES // 10))
    offset = preview.BOX_ART[128]
    image[offset:offset + len(blob)] = blob
    widget = pane(bytes(image), "shot.gba", "A")
    widget.set_portrait(preview.SECOND_LAYOUT_OPERAND)
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
    # A record with no portrait operand takes the FIRST layout, the 144 box.
    assert widget._render.limit == 144
    assert canvas.pixelColor(MARGIN + x + GLYPH_ADVANCE, MARGIN + y).name() == \
        QColor(*palette[BOX_FILLS[144]]).name()


def test_the_portrait_operand_selects_which_box_is_drawn() -> None:
    """The operand the record stores is what picks the layout, art and limit together."""
    image = bytes(synthetic_image())
    widget = pane(image, "shot.gba", "A")
    palette = preview.decode_palette(image)
    # Operand 0 is no portrait and takes the first layout, the 144 box.
    assert shot(widget).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[144]]).name()
    widget.set_portrait(7)
    assert shot(widget).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[128]]).name()
    widget.set_portrait(0)
    assert shot(widget).pixelColor(MARGIN, MARGIN).name() == \
        QColor(*palette[BOX_FILLS[144]]).name()
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


# --- the layout rule, and the two cases the pane states rather than draws -------


def test_the_operand_seven_rule_selects_the_layout_and_its_own_box_art() -> None:
    """F3: index 1 only for the operand that is exactly 7, and the art follows it.

    MEASURED from the box constructor `0x08012012`: index 0 unless the portrait operand
    is exactly 7 (`0x08012104` to `0x0801210A`), the layout being
    `0x08071720 + 0x10 + 0x14*index` (`0x0800B29E`), and the layout record carries BOTH
    the wrap limit and the art container. The rule this replaces was "portrait present"
    against "no portrait", which gave operand 0 - no portrait - the WRONG box: it took
    index 1 where the engine takes index 0. So operand 0 is a case here, not an aside.
    """
    image = bytes(synthetic_image())
    palette = preview.decode_palette(image)
    widget = pane(image, "shot.gba", "A")
    # Operand 0 means no portrait and takes the FIRST layout, limit 144, art 0x71758.
    assert preview.box_for(0) == 144
    # Only 7 takes the second layout, limit 128, art 0x71A6C.
    assert preview.box_for(7) == 128
    # An ordinary portrait operand, and a record with no operand at all, both take 0.
    for operand in (None, 1, 6, 8, 0x3F):
        assert preview.box_for(operand) == 144, operand
    for operand, limit in ((0, 144), (7, 128), (8, 144), (None, 144)):
        widget.set_portrait(operand)
        assert widget.state() == "ready", (operand, widget.missing())
        assert widget._render.limit == limit, operand
        assert shot(widget).pixelColor(MARGIN, MARGIN).name() == \
            QColor(*palette[BOX_FILLS[limit]]).name(), operand
    # The limit and the art are one choice, so what was decoded is the layout's own art.
    assert set(widget._arts) <= {144, 128}
    assert widget._arts[128] == preview.decode_box(image, 128)
    assert widget._arts[144] == preview.decode_box(image, 144)


def test_the_two_layout_records_and_their_limits_are_measured() -> None:
    assert preview.LAYOUT_LIMITS == (144, 128)
    assert tuple(preview.BOX_ART) == preview.LAYOUT_LIMITS
    assert preview.BOX_ART == {144: 0x71758, 128: 0x71A6C}
    assert preview.SECOND_LAYOUT_OPERAND == 7


def test_a_record_that_never_had_a_portrait_operand_keeps_the_first_layout() -> None:
    """The end of the wrong rule: operand 0 and an absent operand are NOT the 128 box.

    Measured before this case: the pane picked its box by portrait PRESENCE, so a record
    whose operand is 0 was drawn with the limit-128 art and wrapped at 128 instead of
    144, which changes where its lines break, not only its colours.
    """
    image = bytes(synthetic_image())
    widget = pane(image, "shot.gba", "A")
    widget.set_portrait(0)
    assert widget._render.limit == 144
    widget.set_portrait(7)
    assert widget._render.limit == 128
    widget.set_portrait(None)
    assert widget._render.limit == 144


def test_a_record_that_keeps_text_after_its_soft_end_is_limited_and_names_the_rule(
) -> None:
    """F6: 0x0B stops the fitter, and what follows it is not established.

    Measured: 307 of 5,610 (record, limit) pairs carry a 0x0B. The pane drew the first
    segment and still said ready, so an edit after the soft end never appeared in the
    render and nothing said so. The fitter sets the record's end flag at the soft end
    (0x0803DEB4) and leaves its cursor ON that unit; the rule that carries the reveal
    past it is not in the seam document and is not guessed here. The record is stated
    instead, so the pane is limited rather than falsely ready.
    """
    image = bytes(synthetic_image())
    font = preview.decode_font(image)
    art = preview.decode_box(image, 128)
    result = preview.render(font, art, "A\x0bB")
    assert result.drawn is False
    assert result.surface == b""
    assert result.missing == preview.SOFT_RULE
    assert preview.LIMITED + result.problem == \
        "In-game preview: this record keeps text after its own 0x0B soft end, and the " \
        "rule that draws what follows is not established"
    widget = pane(image, "shot.gba", "A")
    widget.set_text("A\x0bB")
    assert widget.state() == "limited"
    assert widget.missing() == (preview.SOFT_RULE,)
    assert not (canvas_colours(widget) & engine_colours()), \
        "the soft-end state drew part of a segment it refuses to guess"
    # A record that ENDS at its soft end is still the record, and still renders.
    assert preview.render(font, art, "A\x0b").drawn is True


def test_a_string_slot_row_is_reported_rather_than_drawn_as_an_empty_box(
        tmp_path: Path) -> None:
    """A slot is not drawn in a dialogue box at all, so an empty box is a lie.

    Measured before the fix: the shell handed the pane `""` for a slot row, the pane
    drew the art with no glyphs on it and reported ready, so a row the engine never
    draws in a box looked like a record that says nothing.
    """
    _bytes, model = simple(tmp_path)
    session = lined(model)
    slot = session.rows_of(app_session.SLOT)[0]
    panel = contextpane.ContextPane(theme.active_theme(), theme.metrics(QAPP))
    # A record first, so the slot is reached in the state a reader reaches it in.
    panel.set_line(session, session.rows_of(app_session.LINES)[0])
    panel.set_preview_state(session.rows_of(app_session.LINES)[0].text)
    assert panel.preview.ready()
    panel.set_line(session, slot)
    panel.set_preview_state("")
    assert slot.view == app_session.SLOT and slot.target == ""
    assert panel.preview.state() == "waiting"
    assert panel.preview.missing() == ("a dialogue record",)
    assert panel.preview.ready() is False
    assert not (canvas_colours(panel.preview) & engine_colours()), \
        "a slot row drew the game's box"
