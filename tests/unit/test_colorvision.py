"""The colour-vision simulator's own checks: the matrices, and what they prove."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6.QtGui")

from PySide6.QtGui import QColor, QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tools.qa import colorvision  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    """One offscreen application for the image cases."""
    return QApplication.instance() or QApplication([])


def test_every_matrix_row_sums_to_one() -> None:
    """The published property, and the one a mistyped matrix would break."""
    for kind, rows in colorvision.MATRICES.items():
        for index, row in enumerate(rows):
            assert abs(sum(row) - 1.0) < 1e-5, (kind, index, sum(row))


def test_the_three_dichromacies_are_offered() -> None:
    assert colorvision.KINDS == ("protanopia", "deuteranopia", "tritanopia")
    with pytest.raises(KeyError):
        colorvision.convert_color((1, 2, 3), "achromatopsia")


def test_a_neutral_grey_maps_to_itself_under_every_kind() -> None:
    """Why this application's neutral ladder is safe: no grey changes at all."""
    for kind in colorvision.KINDS:
        for level in (0, 32, 128, 200, 255):
            assert colorvision.convert_color((level, level, level), kind) == \
                (level, level, level), (kind, level)


def test_red_and_green_lose_their_hue_to_the_red_green_deficiencies() -> None:
    """The rule the owner's constraint rests on, measured rather than asserted.

    Red and green start 120 degrees apart in hue. Under both red-green
    deficiencies that gap collapses to a couple of degrees, so a state told apart
    by red against green would be unreadable, while their BRIGHTNESS stays about
    forty apart, which is why brightness is one of this application's channels.
    Tritanopia is a blue-yellow deficiency and is expected to keep them apart.
    """
    red, green = (220, 30, 30), (30, 200, 30)
    original_hue = abs(QColor(*red).hslHue() - QColor(*green).hslHue())

    def hue_gap(one, other) -> int:
        left, right = QColor(*one).hslHue(), QColor(*other).hslHue()
        if left < 0 or right < 0:
            return 0
        return min(abs(left - right), 360 - abs(left - right))

    def light_gap(one, other) -> int:
        return abs(QColor(*one).lightness() - QColor(*other).lightness())

    assert original_hue == 120
    for kind in ("protanopia", "deuteranopia"):
        seen_red = colorvision.convert_color(red, kind)
        seen_green = colorvision.convert_color(green, kind)
        assert hue_gap(seen_red, seen_green) <= 3, (kind, seen_red, seen_green)
        assert light_gap(seen_red, seen_green) >= 30, (kind, seen_red, seen_green)
    assert hue_gap(colorvision.convert_color(red, "tritanopia"),
                   colorvision.convert_color(green, "tritanopia")) > 90


def test_a_converted_image_keeps_its_size_and_alpha(qapp) -> None:
    image = QImage(4, 3, QImage.Format.Format_ARGB32)
    image.fill(QColor(220, 30, 30, 128))
    image.setPixel(0, 0, QColor(30, 200, 30, 255).rgba())
    out = colorvision.convert(image, "deuteranopia")
    assert out.size() == image.size()
    assert out.pixelColor(1, 1).alpha() == 128
    assert out.pixelColor(1, 1) != image.pixelColor(1, 1)
    assert out.pixelColor(0, 0).alpha() == 255
