"""Shared pieces of the text editor shell suite, split so ``--dist loadfile`` can spread it.

The shell module used to carry every case, so whenever it ran, one xdist worker was
busy for its whole own time and the job could not finish before that worker did.
The cases are unchanged; they are grouped into four modules under this one, and the
helpers and fixtures they share live here.

The application hand-back stays module-scoped: every shard imports ``qapp``, which
depends on ``untouched_application``, so each shard themes the application and
hands it back as that shard found it, exactly as the single file did.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

import tests.text_fixture as text_fixture  # noqa: E402
from tests.text_fixture import SPACES, build, lowered_record_floor  # noqa: E402
from tools.buufury_text import settings, theme  # noqa: E402
from tools.buufury_text import shell as shell_module  # noqa: E402
from tools.buufury_text import session as text_session  # noqa: E402
from tools.buufury_text.session import State  # noqa: E402


#: Bound at module level on purpose, so the application cannot be collected when the
#: fixture's scope ends and leave the rest of the session building widgets under Qt with
#: no application. See the same note in `test_text_tool_editor.py`.
QAPP = QApplication.instance() or QApplication([])

@pytest.fixture(scope="module")
def qapp(untouched_application):
    """The application this module themes, handed back untouched when it ends."""
    yield untouched_application

class _Dialogs:
    """A stand-in for QMessageBox that records instead of blocking.

    Every case that reaches a dialog installs this, so no test can hang on a
    modal question nobody answers.
    """

    StandardButton = QMessageBox.StandardButton

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.questions: list[str] = []
        self.answers = self.StandardButton.No

    def warning(self, _parent, _title, message) -> None:
        self.warnings.append(message)

    def critical(self, _parent, _title, message) -> None:
        self.warnings.append(message)

    def question(self, _parent, _title, message, *_args):
        self.questions.append(message)
        return self.answers

    def about(self, *_args) -> None:
        return None

class _Files:
    """A stand-in for the file dialogs, so no test opens a native chooser."""

    def __init__(self, chosen: str = "") -> None:
        self.chosen = chosen
        self.asked: list[str] = []

    def getOpenFileName(self, _parent, title, *_args):
        self.asked.append(title)
        return self.chosen, ""

    getSaveFileName = getOpenFileName

def covering_image() -> bytes:
    """Two records in one container: the outer span contains the inner one."""
    payload = bytearray(SPACES)
    payload[0x20:0x20 + 22] = "Outer line ".encode("utf-16le")
    payload[0x36:0x36 + 20] = "Inner".encode("utf-16le")
    return build(payloads={1: bytes(payload)}, records=[(1, 0x20, 0x40), (1, 0x36, 20)])

@pytest.fixture()
def working(tmp_path):
    """The synthetic image on disk, with a canonical copy beside it.

    `cutters_from_pool=False` because a fixture carries no handle site inside the
    profile's event pool, so the pool-limited cutters would leave the line list
    empty and the window would be tested over nothing.
    """
    folder = tmp_path / "image"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "retail.gba").write_bytes(covering_image())
    path = folder / "working.gba"
    path.write_bytes(covering_image())
    with lowered_record_floor():
        return text_session.open_image(path, canonical=folder / "retail.gba",
                                       cutters_from_pool=False)

@pytest.fixture()
def window(qapp, working, tmp_path, monkeypatch):
    """A shown window whose settings file is a temporary one, not the user's."""
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    shell = shell_module.Shell(working, applied, theme.MODE_DARK)
    shell.show()
    shell.activateWindow()
    QApplication.processEvents()
    yield shell
    shell.close()

def select_first(window) -> str:
    """Select and show the first row, so a case never leans on a default."""
    key = window.pane.rows()[0].key
    assert window.pane.select_key(key)
    window.show_line(key)
    return key

def prose_row(window) -> str:
    """Select and show the row the rename and the shortening both act on."""
    key = next((row.key for row in window.pane.rows() if "Inner" in row.text), "")
    assert key, [row.text for row in window.pane.rows()]
    assert window.pane.select_key(key)
    window.show_line(key)
    return key

def shrink(window) -> str:
    """One in-place edit: a shorter wording, which the engine can always keep."""
    key = prose_row(window)
    loaded = window.session.line(key).text
    changed = loaded.replace("Inner", "Innr")
    assert changed != loaded
    window.apply_edit(key, changed)
    assert window.session.state(key) is not State.REFUSED
    return key

def accent_share(button, applied) -> float:
    """The share of a button's own pixels the theme's accent fills.

    A property can be set and a stylesheet can still paint over it, so this reads
    the pixels the widget actually drew rather than the property it was given.
    """
    shot = button.grab().toImage()
    accent = theme.color(applied, "accent")
    total = shot.width() * shot.height()
    filled = sum(1 for y in range(shot.height()) for x in range(shot.width())
                 if shot.pixelColor(x, y) == accent)
    return filled / total if total else 0.0

def two_line_window(qapp, tmp_path, monkeypatch):
    """A shown window over one record whose text is two spoken lines."""
    monkeypatch.setattr(settings, "directory", lambda: tmp_path / "user-config")
    folder = tmp_path / "two-line"
    folder.mkdir()
    payload = bytearray(SPACES)
    payload[0x20:0x20 + 8] = "One\nTwo".encode("utf-16le")
    image = build(payloads={1: bytes(payload)}, records=[(1, 0x20, 14)])
    (folder / "retail.gba").write_bytes(image)
    path = folder / "working.gba"
    path.write_bytes(image)
    with lowered_record_floor():
        session = text_session.open_image(path, canonical=folder / "retail.gba",
                                          view=text_session.LINES, cutters_from_pool=False)
    applied = theme.apply_theme(qapp, theme.MODE_DARK)
    shell = shell_module.Shell(session, applied, theme.MODE_DARK)
    shell.show()
    QApplication.processEvents()
    target = session.model.records[0].key
    rows = sorted((row for row in session.lines if row.target == target),
                  key=lambda row: row.position[1])
    assert len(rows) == 2, [row.text for row in rows]
    return shell, session, target, rows

import tests.text_fixture as text_fixture  # noqa: E402


@pytest.fixture(autouse=True)
def fixture_handle_pool():
    """The fixture's record words are the proven carriers a write has to land on.

    A real image's proven carriers are the event-resource pool, which sits far above this
    fixture's payload. Without the patch the engine refuses every edit to a fixture record,
    which is the rule working: it writes only what it can prove a reader reaches. These tests
    are about the states above that rule.
    """
    with text_fixture.proven_handle_pool():
        yield
