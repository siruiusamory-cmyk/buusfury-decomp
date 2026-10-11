"""The chip atoms and the in-game preview.

Everything here runs offscreen over plain strings and synthetic data: no ROM, no
window, and no game art committed. The renderer's own cases build a fake extraction
in `tmp_path` so the wrapping, the paging and the pixel comparison are exercised
without any real game data, and the capture harness is asserted to SKIP LOUDLY when
the real data or the real captures are absent.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QMimeData, Qt  # noqa: E402
from PySide6.QtGui import QColor, QImage, QKeyEvent, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication, QTextEdit  # noqa: E402

from tools.buufury_text import chips, preview, theme  # noqa: E402

QAPP = QApplication.instance() or QApplication([])

#: Two prose runs around an interior 0x0A, then a 0x08 unit with an operand.
CURRENT = "AB\nCD\x08\x03EF"
ATOMS = ((2, 3), (5, 7))
#: The game code, as the fixture builder and the engine both spell it.
GAME_CODE = "BG3E"


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


# --- layout, pure -------------------------------------------------------------


class Blank:
    """A stub source: one column per character, `page_lines` lines to a page."""

    def __init__(self, columns: int = 5, page_lines: int = 2) -> None:
        self.columns = columns
        self.page_lines = page_lines

    def advance(self, character: str) -> int:
        return 1


def test_layout_wraps_at_the_game_column_count() -> None:
    assert preview.layout("abcdefghij", Blank(columns=5)) == (("abcde", "fghij"),)


def test_layout_breaks_a_page_at_the_game_page_rule() -> None:
    pages = preview.layout("abcdefghijklmno", Blank(columns=5, page_lines=2))
    assert pages == (("abcde", "fghij"), ("klmno",))


def test_layout_honours_the_games_own_line_break() -> None:
    assert preview.layout("ab\ncd", Blank(columns=5, page_lines=3)) == (("ab", "cd"),)
    assert preview.layout("\x0a", Blank(columns=5)) == (("", ""),)


def test_layout_keeps_a_control_unit_as_one_column() -> None:
    pages = preview.layout("\x08\x03AB", Blank(columns=2))
    assert pages == ((f"{preview.CHARACTER}A", "B"),)


def test_layout_of_nothing_is_one_empty_line() -> None:
    assert preview.layout("", Blank()) == (("",),)


# --- a synthetic extraction, built in the test -------------------------------

#: Tile i of the fake font draws a solid block of INKS[i]; None means blank.
#: The tile index and the codepoint are deliberately different, so a loader that
#: confuses them fails here rather than in the preview.
INKS = (None, "#FF0000", "#00FF00", "#0000FF")
CODEPOINTS = (0x41, 0x42, 0x43, 0x44)  # A B C D
GLYPH = 8


def build_font(directory: Path, inks=INKS) -> None:
    sheet = QImage(GLYPH * len(inks), GLYPH, QImage.Format.Format_ARGB32)
    sheet.fill(Qt.GlobalColor.transparent)
    painter = QPainter(sheet)
    for index, ink in enumerate(inks):
        if ink is not None:
            painter.fillRect(index * GLYPH, 0, GLYPH, GLYPH, QColor(ink))
    painter.end()
    sheet.save(str(directory / "glyphs.png"))
    (directory / "glyph_widths.json").write_text(
        json.dumps({str(code): GLYPH for code in CODEPOINTS}), encoding="utf-8")
    (directory / "glyph_tiles.json").write_text(
        json.dumps({str(code): index for index, code in enumerate(CODEPOINTS)}),
        encoding="utf-8")


def build_metrics(directory: Path, origin=(0, 0), stride: int = 8, columns: int = 4,
                  pages: int = 2) -> None:
    (directory / "metrics.json").write_text(json.dumps({
        "origin": list(origin), "line_stride": stride, "box_rect": [0, 0, 32, 24],
        "columns": columns, "page_stride": stride, "page_count": pages,
        "glyph_width": GLYPH, "glyph_height": GLYPH, "box_width": 32,
    }), encoding="utf-8")


def build_extraction(root: Path, **kwargs) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "palette.json").write_text(json.dumps({"palette": [0, 0x7C00, 0x03E0, 0x001F]}),
                                       encoding="utf-8")
    build_font(root, **kwargs)
    box = QImage(32, 24, QImage.Format.Format_ARGB32)
    box.fill(QColor("#112233"))
    box.save(str(root / "box.png"))
    build_metrics(root)
    (root / "rules.md").write_text("Wrap at the column count; a page holds two lines.\n",
                                   encoding="utf-8")
    return root


def test_load_data_names_every_part_of_the_contract(tmp_path: Path) -> None:
    empty = tmp_path / "nothing"
    assert preview.load_data(empty).missing == preview.PARTS
    empty.mkdir()
    assert set(preview.load_data(empty).missing) == set(preview.PARTS)
    full = build_extraction(tmp_path / "dialogue")
    data = preview.load_data(full)
    assert data.missing == ()
    assert data.font is not None and data.metrics is not None and data.box is not None
    assert len(data.palette) == 4


def test_load_data_nominates_a_single_absent_part(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    (full / "rules.md").unlink()
    assert preview.load_data(full).missing == ("rules.md",)
    (full / "rules.md").write_text("rules\n", encoding="utf-8")
    (full / "glyphs.png").unlink()
    assert preview.load_data(full).missing == ("glyphs.png or glyphs.bin",)


def test_the_palette_is_read_as_rgb555(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    (full / "palette.json").write_text(json.dumps({"palette": [0x7C00, 0x03E0, 0x001F]}),
                                       encoding="utf-8")
    palette = preview.load_data(full).palette
    assert [color.name() for color in palette] == ["#ff0000", "#00ff00", "#0000ff"]


# --- the renderer -------------------------------------------------------------


def test_the_waiting_state_draws_the_line_and_nothing_else() -> None:
    widget = preview.DialoguePreview()
    widget.resize(240, 60)
    # An extraction under way: the named parts are absent, so the pane is not ready.
    widget.set_source(preview.DialogueData(missing=("metrics.json", "rules.md")))
    assert widget.state() == "incomplete"
    assert widget.missing() == ("metrics.json", "rules.md")
    assert widget.ready() is False
    widget.set_text("hello")
    image = QImage(widget.size(), QImage.Format.Format_ARGB32)
    image.fill(QColor("#000000"))
    widget.render(image)
    # Every colour on the canvas is the preview screen or the marker that writes
    # the line: no box fill, no box border, no glyph.
    seen = {image.pixelColor(x, y).name() for y in range(image.height())
            for x in range(image.width())}
    box = QColor(theme.active_theme().preview_box).name()
    ink = QColor(theme.active_theme().preview_ink).name()
    assert box not in seen, "the waiting state drew a box"
    assert ink not in seen, "the waiting state drew glyph ink"


def test_the_waiting_state_draws_nothing_when_nothing_is_extracted() -> None:
    widget = preview.DialoguePreview()
    widget.resize(240, 60)
    widget.set_source(preview.DialogueData(missing=preview.PARTS))
    assert widget.state() == "waiting"
    image = QImage(widget.size(), QImage.Format.Format_ARGB32)
    image.fill(QColor("#000000"))
    widget.render(image)
    seen = {image.pixelColor(x, y).name() for y in range(image.height())
            for x in range(image.width())}
    box = QColor(theme.active_theme().preview_box).name()
    ink = QColor(theme.active_theme().preview_ink).name()
    assert box not in seen, "the waiting state drew a box"
    assert ink not in seen, "the waiting state drew glyph ink"


def test_an_absent_directory_is_waiting(tmp_path: Path) -> None:
    # Nothing extracted at all: this is the state the pane ships in.
    widget = preview.DialoguePreview()
    widget.set_source(tmp_path / "no-extraction")
    assert widget.state() == "waiting"
    assert widget.missing() == preview.PARTS
    assert widget.source_name() == "waiting"
    assert widget.ready() is False


def test_a_widget_that_was_never_given_a_source_discovers_one(
        tmp_path: Path, monkeypatch) -> None:
    # Discovery points somewhere with nothing in it, so this does not depend on
    # what is (or is not) in this machine's build/gamedata/dialogue.
    monkeypatch.setattr(preview, "dialogue_directory", lambda: tmp_path / "absent")
    widget = preview.DialoguePreview()
    assert widget.state() == "waiting"
    assert widget.missing() == preview.PARTS


def test_an_empty_directory_is_waiting_too(tmp_path: Path) -> None:
    # A directory with nothing in it is nothing extracted, not a partial one.
    existing = tmp_path / "dialogue"
    existing.mkdir()
    widget = preview.DialoguePreview()
    widget.set_source(existing)
    assert widget.state() == "waiting"
    assert widget.missing() == preview.PARTS


def test_a_partly_filled_directory_is_incomplete_and_names_the_absent_parts(
        tmp_path: Path) -> None:
    partial = build_extraction(tmp_path / "dialogue")
    (partial / "rules.md").unlink()
    (partial / "box.png").unlink()
    widget = preview.DialoguePreview()
    widget.set_source(partial)
    assert widget.state() == "incomplete"
    assert set(widget.missing()) == {"rules.md", "box.png or box.bin"}
    assert widget.source_name() == "incomplete"


def test_a_ready_widget_names_its_source(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    widget = preview.DialoguePreview()
    widget.set_source(full)
    assert widget.state() == "ready"
    assert widget.missing() == ()
    assert widget.source_name() == preview.GAMEDATA.as_posix()


def test_the_renderer_draws_the_box_and_the_glyphs(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    data = preview.load_data(full)
    image = preview.render_line(data, "BC")
    assert (image.width(), image.height()) == (32, 24)
    # 'B' is codepoint 0x42 and tile 1 (red); 'C' is 0x43 and tile 2 (green). The
    # render resolves the codepoint through the width table, not the tile index.
    assert image.pixelColor(3, 3).name() == QColor("#FF0000").name()
    assert image.pixelColor(GLYPH + 3, 3).name() == QColor("#00FF00").name()
    # 'A' is codepoint 0x41 with width 8 and tile 0, which this sheet leaves blank:
    # a codepoint with a width and no art advances and paints nothing.
    blank = preview.render_line(data, "A")
    assert blank.pixelColor(3, 3).name() == QColor("#112233").name()
    # The box art is under everything the glyphs did not cover.
    assert image.pixelColor(31, 23).name() == QColor("#112233").name()


def test_the_second_line_follows_the_line_stride(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    build_metrics(full, origin=(2, 1), stride=10, columns=2)
    data = preview.load_data(full)
    image = preview.render_line(data, "BCD")
    # Two columns, so 'BCD' wraps to 'BC' and 'D'. 'D' is codepoint 0x44 and tile
    # 3 (blue), and it draws on the second line: one stride below the origin.
    assert image.pixelColor(2 + 3, 1 + 10 + 3).name() == QColor("#0000FF").name()


def test_scaling_is_integer_and_nearest_neighbour_only(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    data = preview.load_data(full)
    one = preview.render_line(data, "\x01", scale=1)
    two = preview.render_line(data, "\x01", scale=2)
    assert two.size() == one.size() * 2
    # Every 2x2 block of the scaled image is one pixel of the 1x image: that is
    # what nearest-neighbour means, and a fractional stretch would break it.
    for y in range(one.height()):
        for x in range(one.width()):
            source = one.pixelColor(x, y).name()
            for dy in range(2):
                for dx in range(2):
                    assert two.pixelColor(2 * x + dx, 2 * y + dy).name() == source


def test_render_refuses_without_the_data() -> None:
    with pytest.raises(ValueError):
        preview.render_line(preview.DialogueData(missing=preview.PARTS), "hello")


# --- the validation harness ---------------------------------------------------


def test_compare_reports_the_count_and_the_first_difference() -> None:
    left = QImage(4, 2, QImage.Format.Format_ARGB32)
    left.fill(QColor("#000000"))
    right = QImage(left)
    assert preview.compare(left, right) == (0, None)
    right.setPixelColor(2, 1, QColor("#FFFFFF"))
    assert preview.compare(left, right) == (1, (2, 1))
    smaller = QImage(2, 2, QImage.Format.Format_ARGB32)
    count, first = preview.compare(left, smaller)
    assert count == left.width() * left.height()
    assert first == (0, 0)


def test_the_harness_is_empty_and_says_so_when_the_data_is_absent(tmp_path: Path) -> None:
    absent = tmp_path / "no-gamedata"
    assert preview.harness(absent) == ()
    assert preview.references(absent) == ()


def test_the_harness_compares_every_declared_capture(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    captures = full / "captures"
    captures.mkdir()
    (captures / "line-1.json").write_text(json.dumps({"line": "\x01"}), encoding="utf-8")
    data = preview.load_data(full)
    preview.render_line(data, "\x01").save(str(captures / "line-1.png"))
    results = preview.harness(full)
    assert len(results) == 1
    assert results[0].name == "line-1"
    assert results[0].matches
    assert (results[0].differing, results[0].first) == (0, None)


def test_the_harness_reports_a_mismatch_rather_than_passing_it(tmp_path: Path) -> None:
    full = build_extraction(tmp_path / "dialogue")
    captures = full / "captures"
    captures.mkdir()
    (captures / "line-1.json").write_text(json.dumps({"line": "\x01"}), encoding="utf-8")
    wrong = QImage(32, 24, QImage.Format.Format_ARGB32)
    wrong.fill(QColor("#123456"))
    wrong.save(str(captures / "line-1.png"))
    results = preview.harness(full)
    assert len(results) == 1
    assert not results[0].matches
    assert results[0].differing > 0
    assert results[0].first is not None


@pytest.mark.skipif(preview.harness() == () and not preview.dialogue_directory().is_dir(),
                    reason=("no extracted dialogue data and no captures in "
                            f"{preview.GAMEDATA.as_posix()}; the harness needs both the "
                            "RE Lab's extraction and its reference mGBA captures, which "
                            "are ignored build/ paths and are never committed"))
def test_the_real_captures_match_the_real_render() -> None:
    results = preview.harness()
    assert results, "the data and the captures were both present, so nothing should be empty"
    for result in results:
        assert result.matches, (result.name, result.differing, result.first)
