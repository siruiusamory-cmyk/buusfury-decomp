"""The theme's hand-back, asserted where the application starts untouched.

The leak this pins was real: a module that installs the editor's theme leaves the whole
application styled, and another product's window measured afterwards in the same process reads
this theme's metrics. Measured, one ordinary button's size hint goes from 20 to 26 under the
stylesheet alone, and the enemy randomizer's control-height test reads 26 where it expects 24.
"""
from __future__ import annotations

import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QPushButton, QStyle  # noqa: E402

from tests import conftest  # noqa: E402
from tools.buufury_text import theme  # noqa: E402


@pytest.fixture(scope="module")
def application(untouched_application):
    return untouched_application


def test_taking_the_theme_back_restores_an_untouched_control(application) -> None:
    """Install the theme, take it back, and a plain control measures what it measured before."""
    def hint() -> int:
        return QPushButton("Browse...").sizeHint().height()

    before = hint()
    state = conftest.capture_application(application)
    theme.apply_theme(application, theme.MODE_DARK)
    assert hint() != before, "the theme has to move a control, or this asserts nothing"
    conftest.hand_back_application(application, state)
    assert hint() == before


def test_the_application_style_comes_back_as_a_new_live_proxy(application) -> None:
    """A hand-back by name frees the proxy, so the next install has to build another.

    Qt deletes the installed style inside the hand-back; the module has to notice, or it
    hands out a freed C++ object and the next install reuses one. Both halves are
    asserted: nothing is handed out while there is no proxy, and the reinstalled proxy's
    own metrics are the ones the application answers with.
    """
    state = conftest.capture_application(application)
    theme.apply_theme(application, theme.MODE_DARK)
    conftest.hand_back_application(application, state)
    assert theme.proxy_style() is None
    theme.apply_theme(application, theme.MODE_DARK)
    assert theme.proxy_style() is not None
    # The proxy's own gap, which the base style does not answer with.
    assert application.style().pixelMetric(
        QStyle.PixelMetric.PM_LayoutHorizontalSpacing) == theme.active_metrics().gap
