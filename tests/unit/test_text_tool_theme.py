"""The foundation: tokens, metrics, the type ladder, the painting helpers, icons.

Everything here runs offscreen and needs no ROM and no window. The palette is the
adopted Cartridge Workbench table, so the contrast cases below are measured from
the tokens rather than asserted from a doc.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QPoint, QRect, QSize, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QFontMetrics, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication, QStyleOptionViewItem, QStyle  # noqa: E402

from tools.buufury_text import status, theme  # noqa: E402
from tools.buufury_text.session import State  # noqa: E402

HEX = re.compile(r"#[0-9A-Fa-f]{6}")
#: The roles the type ladder names, and nothing else.
TYPE_ROLES = ("label", "caption", "body", "prose", "data", "strong")
#: The sizes the contract freezes. Whole pixels, not a ratio.
TYPE_SIZES = {"label": 11, "caption": 12, "body": 12, "prose": 13, "data": 12, "strong": 12}
#: The contrast floors this build can prove from its own tokens. The control border
#: is a recorded deviation: the adopted table calls it "intentionally subtle".
TEXT_FLOOR = 4.5
FOCUS_FLOOR = 3.0
DISABLED_FLOOR = 2.5

THEME_FIELDS = tuple(theme.TOKENS)

#: The stylesheet reads font metrics, so the application exists before any case
#: touches a theme. Offscreen, so no window is needed by any case here.
QAPP = QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _luminance(color: QColor) -> float:
    def linear(channel: float) -> float:
        channel /= 255
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    return (0.2126 * linear(color.red()) + 0.7152 * linear(color.green())
            + 0.0722 * linear(color.blue()))


def contrast(first: QColor, second: QColor) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# --- tokens -------------------------------------------------------------------


def test_the_token_table_carries_both_modes_for_every_field() -> None:
    for name, pair in theme.TOKENS.items():
        assert len(pair) == 2, name
        for value in pair:
            assert HEX.fullmatch(value), (name, value)


def test_every_theme_field_is_filled_from_the_token_table() -> None:
    assert len(THEME_FIELDS) == len(set(THEME_FIELDS))
    for mode, dark in ((theme.MODE_LIGHT, False), (theme.MODE_DARK, True)):
        resolved = theme.theme_for(mode, dark)
        for name, pair in theme.TOKENS.items():
            assert getattr(resolved, name) == pair[1 if dark else 0], (mode, name)


def test_theme_for_resolves_system_to_the_platform_scheme() -> None:
    assert theme.theme_for(theme.MODE_LIGHT, True).mode == theme.MODE_LIGHT
    assert theme.theme_for(theme.MODE_DARK, False).mode == theme.MODE_DARK
    assert theme.theme_for(theme.MODE_SYSTEM, True).mode == theme.MODE_DARK
    assert theme.theme_for(theme.MODE_SYSTEM, False).mode == theme.MODE_LIGHT
    assert theme.MODES == (theme.MODE_SYSTEM, theme.MODE_LIGHT, theme.MODE_DARK)


def test_the_three_new_roles_are_separate_names() -> None:
    light = theme.theme_for(theme.MODE_LIGHT, False)
    dark = theme.theme_for(theme.MODE_DARK, True)
    # A divider and a control border are different jobs with the same value today.
    assert light.divider == light.border
    assert dark.divider == dark.border
    # The ink on the accent fill is the surface token, in both modes.
    assert light.accent_ink == light.surface
    assert dark.accent_ink == dark.surface
    # Disabled text is its own step and is used for nothing else.
    assert light.text_disabled not in (light.text_primary, light.text_secondary)
    assert dark.text_disabled not in (dark.text_primary, dark.text_secondary)
    assert f"color: {light.text_disabled}" in theme.app_stylesheet(light)


def token_values() -> set[str]:
    return {value.lower() for pair in theme.TOKENS.values() for value in pair}


def hex_literals(sheet: str) -> set[str]:
    """Every hex literal in a stylesheet, ignoring any data URI it embeds."""
    without_uris = re.sub(r"url\(data:[^)]*\)", "url()", sheet)
    return {find.lower() for find in HEX.findall(without_uris)}


def test_app_stylesheet_uses_only_token_colours() -> None:
    for mode, dark in ((theme.MODE_LIGHT, False), (theme.MODE_DARK, True)):
        sheet = theme.app_stylesheet(theme.theme_for(mode, dark))
        assert hex_literals(sheet) <= token_values()
        assert "#" in sheet  # the tokens really reached it
        assert "background" in sheet


# --- metrics ------------------------------------------------------------------


def test_metrics_follow_the_contract_formulas_from_a_known_font_height() -> None:
    app = QApplication.instance()
    height = QFontMetrics(app.font()).height()
    shape = theme.metrics(app)
    assert shape.text_height == height
    assert shape.row_height == max(28, height + 12)
    assert shape.field_height == max(26, height + 10)
    assert shape.chip_height == max(24, height + 8)
    assert shape.header_height == max(24, height + 8)
    assert shape.status_height == max(24, height + 8)
    assert shape.tab_height == max(28, height + 12)
    assert shape.segment_height == 5
    assert (shape.pad_xs, shape.pad_sm, shape.pad_md, shape.pad_lg, shape.pad_xl) == (
        2, 4, 8, 12, 16)
    assert (shape.gap, shape.radius, shape.touch) == (8, 3, 40)


def test_the_spacing_ramp_never_spaces_six() -> None:
    shape = theme.metrics(QApplication.instance())
    gaps = (shape.pad_sm, shape.pad_md, shape.pad_lg, shape.pad_xl, shape.gap)
    assert 6 not in gaps
    assert shape.pad_xs == 2  # optical adjustment only


def test_the_shape_is_derived_from_a_font_height_and_is_stable() -> None:
    assert theme.metrics(None) == theme.metrics(None)
    shape = theme.metrics(None)
    assert shape.row_height == max(28, shape.text_height + 12)
    assert shape.chip_height == max(24, shape.text_height + 8)


# --- the type ladder ----------------------------------------------------------


def test_the_type_ladder_has_six_roles_at_the_frozen_sizes_and_two_weights() -> None:
    scale = theme.type_scale(QApplication.instance())
    weights = set()
    for role in TYPE_ROLES:
        font: QFont = getattr(scale, role)
        assert font.pixelSize() == TYPE_SIZES[role], role
        assert not font.italic(), role
        weights.add(int(font.weight()))
    assert weights == {400, 600}
    assert int(scale.label.weight()) == 600
    assert int(scale.strong.weight()) == 600
    assert int(scale.body.weight()) == 400


def test_the_caps_label_carries_the_documented_tracking() -> None:
    font = theme.type_scale(QApplication.instance()).label
    assert font.letterSpacingType() == QFont.SpacingType.AbsoluteSpacing
    assert font.letterSpacing() == pytest.approx(TYPE_SIZES["label"] * 0.08, abs=0.05)
    assert font.capitalization() == QFont.Capitalization.AllUppercase


def test_the_data_role_is_mono_with_tabular_figures() -> None:
    data = theme.type_scale(QApplication.instance()).data
    assert data.pixelSize() == TYPE_SIZES["data"]
    assert data.family() == theme.mono_font().family()
    assert data != theme.type_scale(QApplication.instance()).prose
    delta = theme.mono_font(delta=2)
    assert delta.pixelSize() == TYPE_SIZES["data"] + 2


def test_fonts_returns_the_installed_scale() -> None:
    assert theme.fonts().prose.pixelSize() == TYPE_SIZES["prose"]


# --- the painting helpers -----------------------------------------------------


def _canvas(width: int = 120, height: int = 24) -> QImage:
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor("#000000"))
    return image


def test_paint_segments_fills_the_right_number_of_blocks() -> None:
    image = _canvas()
    painter = QPainter(image)
    rect = QRect(0, 0, 100, 8)
    theme.paint_segments(painter, rect, 10, 4, theme.active_theme())
    painter.end()
    blocks = 0
    for index in range(10):
        left = rect.left() + int(index * rect.width() / 10) + 1
        if image.pixelColor(left, 4).name() != "#000000":
            blocks += 1
    assert blocks == 4


def test_paint_segments_stays_inside_its_rect() -> None:
    image = _canvas()
    painter = QPainter(image)
    rect = QRect(4, 3, 80, 9)
    theme.paint_segments(painter, rect, 8, 3, theme.active_theme())
    painter.end()
    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixelColor(x, y).name() == "#000000":
                continue
            assert rect.contains(x, y), (x, y)


def test_paint_segments_marks_overflow_by_shape_not_only_colour() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    ink = QColor(theme_.accent).name()
    inked = QColor(theme_.text_primary).name()
    over = _canvas(100, 12)
    painter = QPainter(over)
    theme.paint_segments(painter, QRect(0, 0, 90, 12), 8, 11, theme_, over=True)
    painter.end()
    # x=44 is inside the last block the limit covers; x=68 is past it. Same canvas.
    in_limit = [over.pixelColor(44, y).name() for y in range(12)]
    past_limit = [over.pixelColor(68, y).name() for y in range(12)]
    assert in_limit[0] == inked and in_limit[11] == inked
    # The overflow block sits lower, takes the accent, and still fills to the floor.
    assert past_limit[0] == QColor("#000000").name()
    assert past_limit[1] == ink
    assert past_limit[11] == ink


def test_paint_segments_overflow_is_a_geometry_change_not_only_a_colour() -> None:
    theme_ = theme.theme_for(theme.MODE_DARK, True)
    # One line under its limits and one past them, on identical canvases, so the
    # only difference the eye sees is what the overflow does to the block shape.
    limits = _canvas(200, 12)
    painter = QPainter(limits)
    theme.paint_segments(painter, QRect(0, 0, 120, 12), 6, 6, theme_)
    painter.end()
    past = _canvas(200, 12)
    painter = QPainter(past)
    theme.paint_segments(painter, QRect(0, 0, 120, 12), 6, 12, theme_, over=True)
    painter.end()
    assert _filled_rows(limits, 0, 60) == (0, 11)
    assert _filled_rows(past, 0, 60) == (0, 11)
    assert _filled_rows(past, 60, 120) == (1, 11)


def _filled_rows(image: QImage, left: int, right: int) -> tuple[int, int]:
    """The first and last row that carry any ink in a column band."""
    rows = [y for y in range(image.height())
            if any(image.pixelColor(x, y).name() != "#000000" for x in range(left, right))]
    return (rows[0], rows[-1])


def test_paint_segments_takes_the_accent_when_asked() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    image = _canvas(100, 8)
    painter = QPainter(image)
    theme.paint_segments(painter, QRect(0, 0, 90, 8), 4, 4, theme_, accent=True)
    painter.end()
    accent = QColor(theme_.accent).name()
    assert image.pixelColor(1, 4).name() == accent


def test_paint_row_background_fills_a_selection_and_adds_the_accent_indicator() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    option = QStyleOptionViewItem()
    option.rect = QRect(10, 5, 60, 20)
    option.state = QStyle.StateFlag.State_Selected
    image = _canvas()
    painter = QPainter(image)
    theme.paint_row_background(painter, option, theme_)
    painter.end()
    assert image.pixelColor(60, 15).name() == QColor(theme_.selection).name()
    assert image.pixelColor(10, 15).name() == QColor(theme_.accent).name()


def test_paint_row_background_leaves_an_unselected_row_alone() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    option = QStyleOptionViewItem()
    option.rect = QRect(0, 0, 40, 10)
    option.state = QStyle.StateFlag.State_Enabled
    image = _canvas(40, 10)
    painter = QPainter(image)
    theme.paint_row_background(painter, option, theme_)
    painter.end()
    assert image.pixelColor(20, 5).name() == "#000000"


def test_paint_divider_draws_one_line_at_the_bottom_of_the_rect() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    image = _canvas(40, 10)
    painter = QPainter(image)
    theme.paint_divider(painter, QRect(0, 0, 40, 10), theme_)
    painter.end()
    assert image.pixelColor(20, 9).name() == QColor(theme_.divider).name()
    assert image.pixelColor(20, 8).name() == "#000000"


def test_paint_focus_edge_draws_a_two_pixel_ring_that_is_not_a_fill() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    image = _canvas(40, 20)
    painter = QPainter(image)
    theme.paint_focus_edge(painter, QRect(0, 0, 40, 20), theme_)
    painter.end()
    focus = QColor(theme_.focus).name()
    # Read the ring rather than a fixed row: what matters is that every edge is two
    # pixels thick, that the ink is the focus token, and that the middle is hollow.
    rows = [y for y in range(image.height()) if image.pixelColor(20, y).name() == focus]
    columns = [x for x in range(image.width()) if image.pixelColor(x, 10).name() == focus]
    assert rows == [0, 1, 18, 19], rows
    assert columns == [0, 1, 38, 39], columns
    assert image.pixelColor(20, 10).name() != focus


def test_paint_marker_gives_every_state_its_own_shape() -> None:
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    drawn: dict[str, int] = {}
    for state in State:
        marker = status.presentation(state).marker
        image = _canvas(40, 30)
        painter = QPainter(image)
        theme.paint_marker(painter, QRect(0, 0, 40, 30), marker,
                           theme.state_marker(theme_, state))
        painter.end()
        drawn[marker] = sum(
            1 for y in range(30) for x in range(40)
            if image.pixelColor(x, y).name() != "#000000")
    assert drawn["none"] == 0
    # The count follows the table rather than being written down twice: a state added to
    # PRESENTATION must bring its own shape, and this catches one that reuses another's.
    shaped = {presentation.marker for presentation in status.PRESENTATION.values()
              if presentation.marker != "none"}
    assert len({count for marker, count in drawn.items() if marker in shaped}) == len(shaped)
    assert theme.state_marker(theme_, State.UNCHANGED).style() == Qt.PenStyle.NoPen
    assert theme.state_marker(theme_, State.REFUSED).width() == 4


def test_paint_badge_draws_a_fill_and_keeps_the_word() -> None:
    theme_ = theme.theme_for(theme.MODE_DARK, True)
    fill, ink = theme.state_colors(theme_, State.EDITED)
    image = _canvas(120, 24)
    painter = QPainter(image)
    theme.paint_badge(painter, QRect(0, 0, 110, 20), fill, ink, "pencil", "EDITED")
    painter.end()
    assert image.pixelColor(60, 10).name() != "#000000"


# --- style, palette, icons ----------------------------------------------------


def test_apply_theme_installs_the_proxy_style_and_returns_a_theme(qapp) -> None:
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    assert isinstance(applied, theme.Theme)
    assert isinstance(theme.proxy_style(), theme.EditorProxyStyle)
    # PySide6 hands Qt a QCommonStyle wrapper around the Python style, so the proof
    # that the overrides are live is the answer they give, not the wrapper's class.
    assert qapp.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth) == 1
    assert theme.active_theme() == applied
    assert qapp.palette().color(qapp.palette().ColorRole.Window) == theme.color(
        applied, "window")
    # The disabled group is the disabled token, and nothing else claims it.
    disabled = qapp.palette().color(
        qapp.palette().ColorGroup.Disabled, qapp.palette().ColorRole.Text)
    assert disabled.name() == QColor(applied.text_disabled).name()


def test_the_proxy_style_floors_an_input_at_the_field_height() -> None:
    shape = theme.metrics(QApplication.instance())
    style = theme.EditorProxyStyle(shape, QApplication.instance())
    option = QStyleOptionViewItem()
    for kind in (QStyle.ContentsType.CT_LineEdit, QStyle.ContentsType.CT_PushButton):
        size = style.sizeFromContents(kind, option, QSize(10, 4), None)
        assert size.height() >= shape.field_height, kind


def test_every_presentation_icon_exists_and_renders_in_its_ink() -> None:
    entries = [*status.PRESENTATION.values(), status.AUXILIARY]
    icons = Path(theme.__file__).resolve().parent / "icons"
    theme_ = theme.theme_for(theme.MODE_LIGHT, False)
    ink = QColor(theme_.text_primary)
    for entry in entries:
        assert (icons / f"{entry.icon}.svg").is_file(), entry.icon
        rendered = theme.icon(entry.icon, theme_.text_primary)
        assert not rendered.isNull(), entry.icon
        pixmap = rendered.pixmap(16, 16).toImage()
        painted = [pixmap.pixelColor(x, y) for y in range(pixmap.height())
                   for x in range(pixmap.width()) if pixmap.pixelColor(x, y).alpha() > 128]
        assert painted, entry.icon
        # The substitution worked: no visible pixel is the SVG's own black default,
        # and the strongest pixel is the ink that was asked for. Antialiased edges
        # blend toward the transparent background, so they are not exactly the ink.
        assert all(pixel.lightness() > 8 for pixel in painted), entry.icon
        strongest = max(pixel.lightness() for pixel in painted)
        assert abs(strongest - ink.lightness()) <= 3, (entry.icon, strongest,
                                                       ink.lightness())


def test_a_missing_icon_is_null_rather_than_wrong() -> None:
    assert theme.icon("no-such-icon").isNull()


def test_the_licence_notice_lists_exactly_the_icons_that_ship() -> None:
    """The notice is a licence claim, so its list and its count must match the tree.

    Measured drift: the notice said eighteen and listed eighteen while nineteen were
    tracked, `minus.svg` having been added for the meter's empty state without a line
    in the notice. A count nobody checks is a claim that can go quietly wrong.
    """
    from tests.gates import REPOSITORY_ROOT

    directory = REPOSITORY_ROOT / "tools" / "buufury_text" / "icons"
    shipped = sorted(path.stem for path in directory.glob("*.svg"))
    assert shipped, "the icon directory is part of the package"

    notice = (REPOSITORY_ROOT / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8")
    listed = re.findall(r"`([a-z0-9-]+)`", notice)
    named = sorted({name for name in listed if name in shipped})
    words = {18: "Eighteen", 19: "Nineteen", 20: "Twenty"}

    assert named == shipped, (
        f"the notice does not name {sorted(set(shipped) - set(named))}")
    assert words.get(len(shipped), str(len(shipped))) in notice, (
        f"the notice does not say its own count for {len(shipped)} icons")


def test_the_icon_cache_is_registered_for_removal_and_reused(monkeypatch, tmp_path) -> None:
    """The recoloured copies live in one directory that goes when the process does."""
    registered: list = []
    monkeypatch.setattr(theme, "atexit", SimpleNamespace(register=registered.append))
    monkeypatch.setattr(theme, "_ICON_FILES", None)
    first = theme._icon_cache()
    assert first.is_dir() and first.name.startswith("buufury-icons-")
    assert registered == [theme._drop_icon_cache]
    assert theme._icon_cache() == first, "a live directory must be reused, not leaked"
    assert len(registered) == 1, "a second call must not register a second removal"
    theme._drop_icon_cache()
    assert not first.is_dir()
    # A directory that is already gone must not break interpreter exit.
    monkeypatch.setattr(theme, "_ICON_FILES", tmp_path / "gone")
    theme._drop_icon_cache()


def test_color_refuses_a_name_that_is_not_a_token() -> None:
    with pytest.raises(KeyError):
        theme.color(theme.active_theme(), "not-a-token")


# --- contrast, measured from the tokens ---------------------------------------


@pytest.mark.parametrize("mode,dark", [(theme.MODE_LIGHT, False), (theme.MODE_DARK, True)])
def test_text_contrast_is_at_or_above_the_floor(mode: str, dark: bool) -> None:
    theme_ = theme.theme_for(mode, dark)
    for surface in (theme_.surface, theme_.surface_raised, theme_.window):
        for role in ("text_primary", "text_secondary"):
            ratio = contrast(QColor(getattr(theme_, role)), QColor(surface))
            assert ratio >= TEXT_FLOOR, (mode, role, surface, round(ratio, 2))


@pytest.mark.parametrize("mode,dark", [(theme.MODE_LIGHT, False), (theme.MODE_DARK, True)])
def test_focus_contrast_is_at_or_above_the_floor(mode: str, dark: bool) -> None:
    theme_ = theme.theme_for(mode, dark)
    for surface in (theme_.window, theme_.surface):
        assert contrast(QColor(theme_.focus), QColor(surface)) >= FOCUS_FLOOR, (mode, surface)


@pytest.mark.parametrize("mode,dark", [(theme.MODE_LIGHT, False), (theme.MODE_DARK, True)])
def test_the_accent_fill_and_its_ink_are_readable_together(mode: str, dark: bool) -> None:
    theme_ = theme.theme_for(mode, dark)
    assert contrast(QColor(theme_.accent_ink), QColor(theme_.accent)) >= TEXT_FLOOR
    assert contrast(QColor(theme_.accent), QColor(theme_.surface)) >= FOCUS_FLOOR
    assert contrast(QColor(theme_.text_primary), QColor(theme_.selection)) >= TEXT_FLOOR


@pytest.mark.parametrize("mode,dark", [(theme.MODE_LIGHT, False), (theme.MODE_DARK, True)])
def test_every_state_hue_is_readable_on_its_own_surface(mode: str, dark: bool) -> None:
    theme_ = theme.theme_for(mode, dark)
    for state in State:
        fill, ink = theme.state_colors(theme_, state)
        assert contrast(ink, fill) >= TEXT_FLOOR, (mode, state)
        assert contrast(
            theme.state_marker(theme_, state).color(), QColor(theme_.surface)
        ) >= FOCUS_FLOOR, (mode, state)


@pytest.mark.parametrize("mode,dark", [(theme.MODE_LIGHT, False), (theme.MODE_DARK, True)])
def test_disabled_text_stays_above_its_own_floor_and_below_the_text_floor(
        mode: str, dark: bool) -> None:
    theme_ = theme.theme_for(mode, dark)
    ratio = contrast(QColor(theme_.text_disabled), QColor(theme_.surface))
    assert ratio >= DISABLED_FLOOR, (mode, round(ratio, 2))
    assert ratio < TEXT_FLOOR, (mode, round(ratio, 2))


def test_the_control_border_is_a_recorded_deviation() -> None:
    """The adopted table calls the border "intentionally subtle"; measured, not assumed."""
    for mode, dark in ((theme.MODE_LIGHT, False), (theme.MODE_DARK, True)):
        theme_ = theme.theme_for(mode, dark)
        ratio = contrast(QColor(theme_.border), QColor(theme_.surface))
        assert ratio < FOCUS_FLOOR, (mode, round(ratio, 2))
        assert ratio > 1.2, (mode, round(ratio, 2))


#: The control classes Qt will draw itself if no rule names them, and the region of
#: each that carries its ink.
CONTROL_CLASSES = ("QMenuBar", "QComboBox", "QLineEdit", "QToolButton", "QPushButton")


def _flatten(image: QImage, backdrop: QColor) -> QImage:
    """A widget grab composited on the surface behind it.

    A transparent control, which is what an inline tool button is, grabs as a
    transparent image and would otherwise measure against black.
    """
    out = QImage(image.size(), QImage.Format.Format_ARGB32)
    out.fill(backdrop)
    painter = QPainter(out)
    painter.drawImage(0, 0, image)
    painter.end()
    return out


def _rendered_ink_and_background(image: QImage) -> tuple[QColor, QColor]:
    """The widget's own fill, and the pixel that contrasts with it the most."""
    counts: dict[int, int] = {}
    pixels = []
    for y in range(image.height()):
        for x in range(image.width()):
            value = image.pixel(x, y)
            counts[value] = counts.get(value, 0) + 1
            pixels.append(value)
    background = QColor(max(counts, key=lambda value: counts[value]))
    ink = max((QColor(value) for value in pixels),
              key=lambda colour: contrast(colour, background))
    return ink, background


def test_every_control_class_is_painted_in_the_theme_ink(qapp) -> None:
    """A control with no stylesheet rule is painted Qt's way, not the theme's.

    Measured, and this is the case that would have caught it: the light theme once
    rendered the menu bar, the four combo boxes and the address disclosure as white on
    a `#F3F4F6` window, about 1.1 to 1, while the dark theme painted all of them
    correctly, so no dark pass could see the defect and the source-level check found no
    literal to complain about. This renders each class instead of reading the source.
    """
    from PySide6.QtWidgets import (QComboBox, QLineEdit, QMenuBar, QPushButton,
                                   QToolButton, QVBoxLayout, QWidget)

    for mode in (theme.MODE_LIGHT, theme.MODE_DARK):
        applied = theme.apply_theme(qapp, mode)
        host = QWidget()
        host.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        column = QVBoxLayout(host)
        menu = QMenuBar()
        menu.addMenu("File")
        menu.addMenu("Edit")
        combo = QComboBox()
        combo.addItems(["Lines", "Records"])
        field = QLineEdit()
        field.setText("search")
        tool = QToolButton()
        tool.setText("Address, offset and size")
        button = QPushButton("Export")
        for widget in (menu, combo, field, tool, button):
            column.addWidget(widget)
        host.resize(320, 240)
        host.show()
        QApplication.processEvents()
        for name, widget in (("QMenuBar", menu), ("QComboBox", combo), ("QLineEdit", field),
                             ("QToolButton", tool), ("QPushButton", button)):
            assert name in CONTROL_CLASSES
            grabbed = _flatten(widget.grab().toImage(), QColor(applied.window))
            ink, background = _rendered_ink_and_background(grabbed)
            ratio = contrast(ink, background)
            assert ratio >= TEXT_FLOOR, (
                f"{mode} {name} draws ink {ink.name()} on {background.name()}, "
                f"{ratio:.2f}:1 against the {TEXT_FLOOR} floor: the stylesheet names no "
                f"rule for it, so Qt is choosing the ink"
            )
            assert background.name().lower() in (
                applied.surface.lower(), applied.surface_raised.lower(),
                applied.window.lower()), (mode, name, background.name())
        host.close()


#: The classes the case above does not reach, and how each one is rendered here:
#: the combo popup's own view, a menu, the tab strip, a header section, a table body
#: and the real tooltip window.
EXTRA_CONTROL_CLASSES = ("QComboBox view", "QMenu", "QTabBar", "QHeaderView",
                         "QTableView", "QToolTip")


def _theme_ink_present(image: QImage, applied) -> bool:
    """Whether any rendered pixel is exactly one of the theme's two text tokens.

    The tab strip also carries a 1 px base line that Qt draws itself, so on that row
    the most-contrasting pixel is not a label; requiring a token pixel keeps the row
    an honest measurement of the control's own ink.
    """
    tokens = {QColor(applied.text_primary).rgb(), QColor(applied.text_secondary).rgb()}
    return any(image.pixel(x, y) in tokens
               for y in range(image.height()) for x in range(image.width()))


def test_the_extra_control_classes_are_painted_in_the_theme_ink(qapp) -> None:
    """The same rendered-pixel rule, for the classes the first case does not reach.

    Every one of the six renders offscreen and no stand-in is used: the tooltip row
    is the QTipLabel Qt itself creates, not a QLabel wearing its name.
    """
    from PySide6.QtGui import QStandardItem, QStandardItemModel
    from PySide6.QtWidgets import (QComboBox, QMenu, QTabBar, QTableView, QToolTip,
                                   QVBoxLayout, QWidget)

    for mode in (theme.MODE_LIGHT, theme.MODE_DARK):
        applied = theme.apply_theme(qapp, mode)
        host = QWidget()
        host.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        column = QVBoxLayout(host)
        combo = QComboBox()
        combo.addItems(["Lines", "Records"])
        tabs = QTabBar()
        tabs.addTab("Lines")
        tabs.addTab("Records")
        table = QTableView()
        model = QStandardItemModel(3, 2)
        model.setHorizontalHeaderItem(0, QStandardItem("Line"))
        model.setHorizontalHeaderItem(1, QStandardItem("Record"))
        for row in range(3):
            model.setItem(row, 0, QStandardItem(f"Line {row}"))
            model.setItem(row, 1, QStandardItem("World Tournament Stadium"))
        table.setModel(model)
        for widget in (combo, tabs, table):
            column.addWidget(widget)
        host.resize(400, 260)
        host.show()
        QApplication.processEvents()
        # The popup list, the menu and the tooltip are their own windows, so each is
        # shown before anything in it is painted.
        combo.showPopup()
        QApplication.processEvents()
        menu = QMenu()
        menu.addAction("Rename")
        menu.addAction("Export")
        menu.popup(QPoint(12, 12))
        QApplication.processEvents()
        QToolTip.showText(QPoint(12, 12), "Line 1 of 3", table)
        QApplication.processEvents()
        tip = next((widget for widget in qapp.topLevelWidgets()
                    if widget.metaObject().className() == "QTipLabel"
                    and widget.isVisible()), None)
        for name, widget in (("QComboBox view", combo.view()), ("QMenu", menu),
                             ("QTabBar", tabs),
                             ("QHeaderView", table.horizontalHeader()),
                             ("QTableView", table), ("QToolTip", tip)):
            assert name in EXTRA_CONTROL_CLASSES
            assert widget is not None, name
            grabbed = _flatten(widget.grab().toImage(), QColor(applied.window))
            ink, background = _rendered_ink_and_background(grabbed)
            ratio = contrast(ink, background)
            assert ratio >= TEXT_FLOOR, (
                f"{mode} {name} draws ink {ink.name()} on {background.name()}, "
                f"{ratio:.2f}:1 against the {TEXT_FLOOR} floor: the stylesheet names no "
                f"rule for it, so Qt is choosing the ink"
            )
            assert background.name().lower() in (
                applied.surface.lower(), applied.surface_raised.lower(),
                applied.window.lower()), (mode, name, background.name())
            assert _theme_ink_present(grabbed, applied), (mode, name)
        QToolTip.hideText()
        menu.close()
        combo.hidePopup()
        host.close()
