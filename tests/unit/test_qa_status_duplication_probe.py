"""The status-duplication probe refuses to call an unmeasured screen clean.

`tools/qa/status_duplication_probe.py` reads the shell's own status bar and reports
a screen as clean when it finds no duplicate sentence. A bar that renders nothing
yields no sentences at all, so the per-screen loop printed "clean" for every screen
and `main` exited 0 having measured nothing - a whole class of defect reported as
checked while nothing was read.

These tests pin the two pure helpers that guard it. The Qt-driven walk itself is
not driven here: the guard's logic is what must be covered, and keeping it pure is
what makes that possible without a window.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from tools.qa.status_duplication_probe import (  # noqa: E402
    SCREENS,
    status_vacuity,
    unreached_screens,
)


def test_the_named_screen_set_holds_the_nine_screens_the_probe_walks() -> None:
    assert len(SCREENS) == 9
    assert len(set(SCREENS)) == len(SCREENS)


def test_an_empty_sentence_list_is_refused_rather_than_called_clean() -> None:
    refusal = status_vacuity("Atlas", [])
    assert refusal is not None
    assert "Atlas" in refusal
    assert "not clean" in refusal
    assert status_vacuity("Atlas", ["No ROM loaded."]) is None


def test_a_screen_the_run_never_reached_is_reported() -> None:
    assert unreached_screens(list(SCREENS)) == []
    assert unreached_screens(list(SCREENS[:-1])) == [SCREENS[-1]]
    assert unreached_screens([]) == list(SCREENS)
