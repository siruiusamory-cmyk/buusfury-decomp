"""Focused tests for the ONE authoritative shell project-status computation.

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`'s final correction: the human review
found captures disagreeing about project status - some showing `no project` and
others `not validated | not built` for what looked like the same ROM-only state.
The disagreement was in the *captures*, not in the product: the capture sequence
had a project open by then, so those states were genuinely "project open, never
validated" and the label was right.

What mattered was that there was no test pinning the computation itself, so the
two things could not be distinguished. These tests pin it:

- every state the state model defines produces exactly one string;
- that string is identical in every editor and at every window width, because the
  status is *project* state and has nothing to do with the active editor.

The presentation side is a pure function of the session, so most of this needs no
Qt at all. The parity test at the end does build the real window, because the
claim being made is about the real shell.
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QLabel, QStatusBar  # noqa: E402

from tools.webfoot.workbench.app import MainWindow  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402

_ROM = Path("C:/roms/canonical.gba")
_PROJECT = Path("C:/projects/demo")


def _state(*, rom=False, project=False, validated=None, built=None, revision=1):
    """A real `Session` with only the project state set.

    Deliberately a real Session rather than a bare stub: the shell reads
    `validation_current` / `build_current` off the session, and those are the
    session's own definitions of "current". Substituting a fake would test a second
    implementation of the very rule under test.
    """
    session = Session()
    session.rom_path = _ROM if rom else None
    session.project_dir = _PROJECT if project else None
    session.project_revision = revision
    session.validation_revision = validated
    session.build_revision = revision if built else None
    session.last_build = SimpleNamespace() if built else None
    return session


@pytest.fixture(scope="module")
def window():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    catalog = pytest.importorskip("tools.webfoot.profile").RomProfileCatalog.load(
        "config/roms.yaml"
    )
    return MainWindow(Session(), catalog)


def status_for(window, state) -> str:
    """The shell's own computation, with the session the status reads.

    The method reads currency off `self._session` (validation/build are *current*
    relative to the session's revision), while rom/project come from its arguments.
    The stub session is what makes those two agree, exactly as they do in the real
    application - this is not a second implementation, it is the real one with a
    controlled session behind it.
    """
    window._session = state
    return window._project_state_text(state.rom_path, state.project_dir, 0)


# -- the state model, one assertion per row of it ----------------------------


def test_no_rom_and_no_project(window) -> None:
    assert status_for(window, _state()) == "no ROM"


def test_rom_only_is_no_project(window) -> None:
    """An open ROM is NOT an open project.

    This is the exact confusion the correction was raised for: a ROM-only session
    must never report validation or build state, because there is no project to
    validate or build.
    """
    text = status_for(window, _state(rom=True))
    assert text == "no project"
    for forbidden in ("validated", "built", "stale"):
        assert forbidden not in text


def test_project_open_never_validated(window) -> None:
    text = status_for(window, _state(rom=True, project=True))
    assert "not validated" in text
    assert "not built" in text
    # "stale" would claim a result existed and was invalidated. None did.
    assert "stale" not in text


def test_project_validated_never_built(window) -> None:
    text = status_for(window, _state(rom=True, project=True, validated=1))
    assert "validation current" in text
    assert "not built" in text
    assert "stale" not in text


def test_project_validated_and_built(window) -> None:
    text = status_for(window, _state(rom=True, project=True, validated=1, built=True))
    assert "validation current" in text
    assert "build current" in text
    assert "stale" not in text


def test_stale_requires_an_invalidated_result(window) -> None:
    """`stale` only where a result existed: a revision was recorded and currency
    was then lost. A never-validated project cannot reach the word (asserted
    above), which is the distinction the correction turned on.
    """
    current = _state(rom=True, project=True, validated=1, built=True)
    assert "stale" not in status_for(window, current)  # control case

    # A real edit advances project_revision, which is exactly how the session
    # records "the recorded result no longer describes the project".
    invalidated = _state(rom=True, project=True, validated=1, built=True, revision=1)
    invalidated.project_revision = 2
    text = status_for(window, invalidated)
    assert "validation stale" in text
    assert "build stale" in text


# -- parity: one computation, whatever the editor or the width --------------


@pytest.mark.parametrize("width,height", [(1440, 900), (1100, 720)])
@pytest.mark.parametrize("editor", ["Atlas", "Inspector", "Maps", "Graphics"])
def test_status_is_identical_in_every_editor_and_width(
    window, editor, width, height, rom_only_session
) -> None:
    """The status is project state: neither the active editor nor the window width
    can change it. This is the parity the correction asked for.

    The session has a ROM and no project, which is the state the review found
    reported two different ways.
    """
    window._session = rom_only_session
    window.resize(width, height)
    window.show()
    window.show_editor(editor)
    window._refresh_identity()
    assert window._status_project.text() == "no project"


# -- there is ONE physical status row ---------------------------------------


def visible_status_texts(window) -> list[str]:
    """Every status sentence actually rendered anywhere in the window.

    A label counts only if it is genuinely on screen: a label with no parent, or one
    its parents have hidden, is not drawn and is not a second status row. That
    distinction is the whole point of this guard, because the way an editor keeps a
    status HOLDER without drawing it is precisely to leave it out of every layout.
    """
    texts: list[str] = []
    for label in window.findChildren(QLabel):
        if not label.isVisible() or label.parentWidget() is None:
            continue
        text = label.text().strip()
        if text:
            texts.append(text)
    return texts


@pytest.mark.parametrize("editor", ["Atlas", "Inspector", "Maps", "Graphics"])
def test_exactly_one_status_bar_and_no_editor_draws_its_own(window, editor) -> None:
    """The shell owns the status bar; an editor only publishes text into it.

    The independent review found the Atlas editor rendering its own copy of the
    sentence the bar was showing, and proved by mutation that nothing caught it.
    This catches it: BOTH halves of the bar - the active editor's line on the left
    and the project state on the right - must render exactly once each. Checking the
    bar's own text is what makes the guard independent of which sentence the shell
    happens to be showing.
    """
    window.show()
    window.show_editor(editor)
    window._refresh_identity()
    assert len(window.findChildren(QStatusBar)) == 1, "there is exactly one status bar"
    drawn = visible_status_texts(window)
    for part in (window._status_context.text().strip(), window._status_project.text().strip()):
        assert part, "both halves of the status bar carry text"
        assert drawn.count(part) == 1, (
            f"{editor}: {part!r} is rendered {drawn.count(part)} times"
        )


def test_no_editor_status_holder_is_drawn(window, rom_only_session) -> None:
    """Each editor's own status holder exists but is never rendered.

    One holder per editor is how the text reaches the bar; drawing one as well is
    the duplicate the review found on Atlas.
    """
    window._session = rom_only_session
    window.show()
    for editor in ("Atlas", "Inspector", "Maps", "Graphics"):
        window.show_editor(editor)
        window._refresh_identity()
        for host in window._hosts.values():
            label = host.status_label()
            if label is not None:
                assert label.isHidden() or label.parentWidget() is None, (
                    f"{editor}: an editor is drawing its own status row"
                )


@pytest.fixture(scope="module")
def rom_only_session():
    """The ROM-only state: a ROM open, no project."""
    return _state(rom=True)
